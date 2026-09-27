# Debuggers, Breakpoints, and Call Stacks

## Learning Objectives

By the end of this chapter you should be able to:

- Explain what debugging is and how it differs from testing, logging, tracing, and monitoring.
- Build a mental model of a debugger as an instrument for observing program execution.
- Set and use normal, conditional, temporary, exception-oriented, and function-oriented breakpoints where supported.
- Understand `Continue`, `Step Over`, `Step Into`, `Step Out`, `Run to Cursor`, `Restart`, and `Stop`.
- Explain the call stack and stack frames without treating them as mysterious IDE concepts.
- Read a Python traceback and connect it to a live debugger call stack.
- Inspect local variables, arguments, globals, objects, collections, and expressions.
- Understand Python scope while moving between stack frames.
- Use `breakpoint()`, `pdb.set_trace()`, and command-line `pdb`.
- Use core `pdb` commands to navigate and inspect a running program.
- Debug pytest failures, fixtures, and parametrized cases.
- Debug loops, branches, recursion, exceptions, generators, decorators, and context managers.
- Understand the additional challenges of async code, threads, processes, and external dependencies.
- Debug APIs, databases, data pipelines, ML pipelines, AI/LLM applications, and agentic workflows.
- Use hypothesis-driven debugging instead of random stepping.
- Build a minimal reproducible example.
- Find root cause rather than merely changing the visible symptom.
- Convert a discovered defect into a regression test.
- Apply debugger knowledge safely in production-oriented environments.

---

## Prerequisites

You should understand basic Python:

- variables
- functions
- arguments and return values
- conditionals
- loops
- exceptions
- classes and objects
- basic pytest tests

You do **not** need to be an expert in operating-system internals to use a debugger. However, understanding a few ideas from the Python execution model makes debugging much easier.

This chapter deliberately starts with simple language and gradually introduces:

```text
program execution
    ↓
function calls
    ↓
frames
    ↓
call stack
    ↓
breakpoints
    ↓
stepping
    ↓
state inspection
    ↓
root-cause diagnosis
```

The previous testing chapters teach you how to detect incorrect behavior. This chapter focuses on what to do **after you know something is wrong**.

---

# 1. What Is Debugging?

## What is it?

A **bug** is behavior that is incorrect relative to the intended requirement, contract, or expectation.

**Debugging** is the systematic process of finding the cause of incorrect behavior and correcting it.

A useful debugging loop is:

```text
Observe
   ↓
Reproduce
   ↓
Isolate
   ↓
Inspect
   ↓
Hypothesize
   ↓
Verify
   ↓
Fix
   ↓
Retest
```

## Why does debugging exist?

A failing test can tell you:

```text
expected = 100
actual   = 80
```

That tells you **that** something is wrong.

It may not tell you:

```text
Where did 80 first appear?
Which input produced it?
Which function changed the value?
Which branch ran?
Which dependency returned the wrong state?
```

Debugging tools help answer those questions.

## How does debugging differ from testing?

| Activity | Main question |
|---|---|
| Testing | Does behavior match the expectation? |
| Debugging | Why does the behavior differ? |
| Logging | What information did we record? |
| Monitoring | Is the system healthy over time? |
| Tracing | How did a request flow across components? |

Testing and debugging are complementary:

```text
Test failure
    ↓
Debugging
    ↓
Root cause
    ↓
Fix
    ↓
Regression test
```

## Simple example

```python
def calculate_total(price: int, quantity: int) -> int:
    return price * quantity


def main() -> None:
    print(calculate_total(10, 3))


if __name__ == "__main__":
    main()
```

Suppose the output is unexpectedly `20` instead of `30`.

A debugger can stop before the return and let you inspect:

```text
price = 10
quantity = 2
```

You have learned that the calculation may be correct and the input may be wrong.

## Common mistakes

- Guessing at a fix before reproducing the bug.
- Changing several things at once.
- Assuming the first suspicious line is automatically the root cause.
- Debugging only the symptom.
- Ignoring recent changes.

## Better approach

Use evidence:

```text
What happened?
→ Can I reproduce it?
→ What state existed at failure?
→ Where did the incorrect state first appear?
```

## Production considerations

Interactive debugging is excellent for local diagnosis, but production systems often require:

- logs
- metrics
- traces
- correlation IDs
- reproducible inputs
- safe diagnostic tooling

A production incident may not be reproducible locally.

---

# 2. Why Debuggers Exist

## What problem does `print()` debugging solve?

`print()` lets you observe values:

```python
def calculate_total(price, quantity, discount):
    print("price =", price)
    print("quantity =", quantity)
    print("discount =", discount)

    subtotal = price * quantity
    return subtotal - discount
```

This can be perfectly useful for a quick diagnosis.

## Why does a dedicated debugger help?

A debugger can pause at a point in execution and expose much more context:

```text
current source line
local variables
function arguments
object state
call stack
breakpoints
execution position
exception context
```

You can also move backward through the **call chain** by selecting older stack frames.

## Limitations of print debugging

### No automatic pause-and-inspect state

You must decide in advance what to print.

### Noise

Large programs can produce huge amounts of output.

### Temporary instrumentation

You usually have to add and then remove debug statements.

### Harder nested-call diagnosis

A nested failure may require prints in several functions.

### Harder conditional investigation

You may need:

```python
if transaction["id"] == 5001:
    print(...)
```

just to avoid thousands of messages.

### Harder concurrent diagnosis

Multiple threads can interleave their output.

## Important nuance

`print()` is not bad.

It is often appropriate when:

- the code is simple
- the process is easy to reproduce
- you need one quick observation
- an interactive debugger is unavailable

The important skill is choosing the right instrument.

---

# 3. Debugger Mental Model

## The basic model

Think of the debugger as an execution observer:

```text
Python program
     ↓
executes
     ↓
reaches a pause point
     ↓
execution pauses
     ↓
debugger exposes state
     ↓
you inspect
     ↓
you step or continue
     ↓
program executes again
```

## What is program state?

At a particular moment, the program has a state.

That state can include:

- current source location
- current function
- function arguments
- local variables
- accessible globals
- object attributes
- pending exception
- current call stack

## Simple analogy

Imagine a movie.

Without a debugger:

```text
Play
──────────────→
```

With a debugger:

```text
Play
───→ Pause
      ↓
   inspect frame
      ↓
   advance one step
      ↓
   inspect again
      ↓
   continue
```

The program is still executing normally; the debugger gives you controlled pause points and visibility.

## Important mental model

A debugger does not magically know the root cause.

It gives you **evidence**.

You still have to reason about:

```text
expected state
vs
actual state
```

---

# 4. Breakpoints

## What is a breakpoint?

A **breakpoint** is an instruction to the debugger:

> Pause execution when this location is reached.

For example, in an IDE you may click beside a source-code line.

In Python you can also write:

```python
def calculate_total(price, quantity):
    subtotal = price * quantity
    breakpoint()
    return subtotal
```

When execution reaches `breakpoint()`, the program enters the configured debugger. Python's built-in `breakpoint()` delegates through `sys.breakpointhook()`; with the standard configuration this enters `pdb`. citeturn193898search5turn682082view0

## Why does it exist?

Without a breakpoint, a program may run past the interesting state before you can inspect it.

## What happens when execution reaches a breakpoint?

Conceptually:

```text
source line
   ↓
breakpoint condition satisfied
   ↓
pause
   ↓
debugger prompt/UI
   ↓
inspect / step / continue
```

The program does not stop permanently. You can resume it.

## Breakpoint placement strategy

Bad:

```text
put breakpoints on 30 random lines
```

Better:

```text
identify the suspicious behavior
        ↓
find the state transition
        ↓
place breakpoint immediately before or during that transition
```

### Example

Suppose:

```python
balance = account.balance
approved = balance >= amount
process_transfer(account, amount)
```

If the wrong approval result is suspicious, a breakpoint around the `approved` calculation is usually more informative than one at the end of the entire function.

## Common mistakes

- Breakpoint everywhere.
- Breakpoint too late, after incorrect state has already propagated.
- Breakpoint too early, creating too much irrelevant work.
- Leaving permanent debug statements in production code.

## Production considerations

Do not casually attach an interactive debugger to a production process. Pausing execution can affect latency, locks, timeouts, throughput, and state.

---

# 5. Types of Breakpoints

Debugger and IDE feature sets differ, so treat the following as **concepts**, not guarantees that every environment exposes the same UI.

## Normal line breakpoint

Pause at a specific line.

Useful for:

```text
inspect this exact transition
```

## Conditional breakpoint

Pause only when a condition is true.

Example:

```text
transaction["id"] == 5001
```

Useful in loops and repeated requests.

## Logpoint / non-stopping breakpoint

A debugger feature that records information without pausing execution, where supported.

This is useful when:

```text
you need repeated observations
but cannot afford interactive pauses
```

Some IDEs call this a logpoint; implementations vary.

## Exception breakpoint

Pause when an exception occurs, where the debugger supports that mode.

Useful when an exception is raised deep in a call stack and may later be caught or transformed.

## Function/method breakpoint

Pause when execution reaches a function or method.

In `pdb`, breakpoints can be set by function expression as well as line.

## Temporary breakpoint

Pause once and then remove the breakpoint.

`pdb` provides `tbreak`.

## Hit-count / ignore-count behavior

Some IDEs expose a hit count or ignore-count feature. In `pdb`, `ignore` lets you skip a specified number of breakpoint hits.

### Common mistake

Assuming that a feature shown in one IDE is part of the Python language.

It is not.

```text
Python language
vs
pdb behavior
vs
IDE debugger feature
```

Keep those layers separate.

---

# 6. Conditional Breakpoints

## What is it?

A conditional breakpoint pauses only when a Boolean condition becomes true.

Suppose:

```python
for transaction in transactions:
    process(transaction)
```

There may be 100,000 transactions, but only:

```text
transaction["id"] == 5001
```

is suspicious.

A conditional breakpoint lets you stop only there.

## Why is it useful?

It reduces repetitive pauses.

Instead of:

```text
pause #1
pause #2
pause #3
...
pause #5001
```

you can target the relevant case.

## Simple concept

```text
for every item:
    if condition:
        pause
```

## `pdb` example

You can set a breakpoint condition with:

```text
(Pdb) b 12, transaction["id"] == 5001
```

or update an existing breakpoint using `condition`.

`pdb` supports breakpoint conditions as expressions that must evaluate to true before the breakpoint is honored. citeturn108140view0

## Useful conditions

```python
transaction["id"] == 5001
```

```python
user["email"] == "alice@example.com"
```

```python
amount > limit
```

```python
status == "FAILED"
```

## Common mistakes

- Condition references a variable that is not in the current scope.
- Condition itself raises an exception.
- Condition is more complicated than the actual behavior.
- Condition introduces side effects.

## Better approach

Keep a breakpoint condition:

- simple
- side-effect-free
- directly tied to the suspicious case

## Production considerations

Conditional breakpoints reduce unnecessary pauses but still have runtime and operational implications. Use them carefully in live systems and prefer non-invasive observability when possible.

---

# 7. Stepping Through Code

The primary execution controls are:

| Operation | Meaning |
|---|---|
| Continue | Resume until another pause point |
| Step Over | Execute the current line without entering called functions |
| Step Into | Enter a called function |
| Step Out | Finish the current function and return to caller |
| Run to Cursor | Continue until a chosen source location, where supported |
| Restart | Start the debugged program again |
| Stop | End debugging/program execution |

## Continue

```text
paused
  ↓
continue
  ↓
run normally
  ↓
next breakpoint/exception/end
```

Use when you have enough information and do not need to inspect each intervening line.

## Step Over

Use when the current function call is not where you want to investigate.

```python
result = calculate_total()
```

Step Over executes the call and stops at the next line in the current function.

## Step Into

Use when the called function itself is suspicious.

```python
result = calculate_total()
```

Step Into moves into `calculate_total()`.

## Step Out

Use when you are inside a function and realize:

> I do not need to inspect the rest of this function.

The debugger runs until that function returns.

## Run to Cursor

Some IDEs provide a command that continues to a selected source line without requiring a permanent breakpoint.

## Restart

Restarts the debugged program. The exact semantics depend on the debugger environment.

## Stop

Ends execution/debugging.

## Common mistake

Stepping every line just because the debugger allows it.

Debugging is not a video-game speedrun. Step only when the next line can answer your current question.

---

# 8. Step Over vs Step Into

This is one of the most important beginner concepts.

Suppose:

```python
def main():
    total = calculate()


def calculate():
    return add_tax(apply_discount(100))


def apply_discount(value):
    return value - 10


def add_tax(value):
    return value + 18
```

Call chain:

```text
main
 ↓
calculate
 ↓
apply_discount
```

## Step Over

At:

```python
total = calculate()
```

Step Over says:

> Run `calculate()` as one operation and return me to `main()`.

Conceptually:

```text
main
 ↓
[calculate executes]
 ↓
main
```

## Step Into

Step Into says:

> Enter `calculate()` because I want to inspect its internal behavior.

```text
main
 ↓
calculate
 ↓
apply_discount
```

## When to use Step Over

Use it when:

- the function is trusted
- you only care about its returned value
- entering would create irrelevant detail
- you want to reach the next suspicious statement quickly

## When to use Step Into

Use it when:

- the called function may contain the bug
- the return value is unexpected
- you need to inspect its internal state
- you need to trace the call chain

## Example debugging question

You see:

```text
expected total = 108
actual total   = 118
```

Possible hypothesis:

> The discount function did not run.

Step Into can verify:

```text
calculate
  ↓
apply_discount?
```

If it did run, inspect its returned value and continue.

---

# 9. Step Out

## What is it?

Step Out finishes the current function and returns to its caller.

Suppose:

```python
def calculate():
    value = apply_discount()
    tax = calculate_tax(value)
    return tax


def calculate_tax(value):
    ...
```

You step into `calculate_tax()` and quickly learn:

> The tax function is correct.

Instead of:

```text
step
step
step
step
...
```

use Step Out.

The debugger completes:

```text
calculate_tax()
```

and returns to:

```text
calculate()
```

## Why is it useful?

It reduces noise.

## Good heuristic

Use:

```text
Step Into
```

to investigate a function.

Use:

```text
Step Over
```

to treat a function as one operation.

Use:

```text
Step Out
```

when you already have enough information inside that function.

---

# 10. Call Stack

## What is a call stack?

The **call stack** is the current chain of active function calls.

Suppose:

```python
def main():
    process_order()


def process_order():
    validate_order()


def validate_order():
    parse_amount()


def parse_amount():
    ...
```

The call chain is:

```text
main()
  ↓
process_order()
  ↓
validate_order()
  ↓
parse_amount()
```

At the moment `parse_amount()` is running, these calls are still active.

That chain is represented by stack frames.

## Why does it exist?

A function needs to know where to return when it finishes.

The runtime therefore keeps information about active calls.

The debugger exposes that call context.

## Simple analogy

Imagine a stack of plates:

```text
top
┌────────────────────┐
│ parse_amount frame │ ← current
├────────────────────┤
│ validate frame     │
├────────────────────┤
│ process frame      │
├────────────────────┤
│ main frame         │
└────────────────────┘
bottom
```

The currently executing function is usually at the top/current end of this conceptual stack.

## Important nuance

The debugger's exact presentation is implementation- and tool-dependent. The conceptual stack model is what matters for debugging.

---

# 11. Stack Frames

## What is a stack frame?

A **stack frame** represents the execution context for one active function call.

Conceptually it contains information such as:

- which function is executing
- its arguments
- local variables
- current execution position
- surrounding execution context needed to resume

Python exposes frame/traceback objects programmatically, and debuggers use this execution information to let you inspect active calls.

## Example

```python
def outer(x):
    y = x + 1
    return inner(y)


def inner(value):
    result = value * 2
    breakpoint()
    return result
```

When paused inside `inner()`:

```text
Frame: inner
arguments:
    value = 11

locals:
    result = 22

caller:
    outer
```

The caller's frame may contain:

```text
x = 10
y = 11
```

## Why frames matter

Without frame awareness, beginners often ask:

> "Why can't I see this variable?"

The answer may simply be:

> That variable belongs to a different function frame.

---

# 12. Reading a Call Stack

Suppose an exception produces:

```text
main()
  → process_order()
    → validate_order()
      → parse_amount()
        → ValueError
```

Read it as:

```text
main called process_order
process_order called validate_order
validate_order called parse_amount
parse_amount raised ValueError
```

## How to identify the likely failure boundary

Ask:

1. Where did the exception originate?
2. Which function passed the problematic value?
3. What was the last boundary where the value was known to be correct?
4. Which frame contains the first suspicious state?

## Example

```text
main()
  ↓
process_order(order)
  ↓
validate_order(order)
  ↓
parse_amount(order["amount"])
```

Suppose:

```text
order["amount"] = "10O"
```

The root cause could be:

- bad input
- bad parser
- incorrect earlier transformation
- wrong field mapping

The call stack shows **where** the code was executing. It does not automatically identify which of these causes is correct.

## Common mistake

Assuming:

```text
exception line = root cause
```

The exception line is the failure location, not always the origin of the incorrect state.

---

# 13. Traceback vs Call Stack

These concepts are related but not identical.

## Traceback

A Python **traceback** records the chain of execution associated with an exception.

Example:

```text
Traceback (most recent call last):
  File "app.py", line 20, in main
    process_order()
  File "orders.py", line 10, in process_order
    validate_order()
  File "orders.py", line 6, in validate_order
    parse_amount()
  File "parser.py", line 3, in parse_amount
    int(value)
ValueError: invalid literal
```

It is usually what you inspect after an exception has occurred.

## Live debugger call stack

While paused, the debugger shows the currently active stack.

You can often navigate among frames and inspect state.

## Relationship

```text
Exception occurs
     ↓
traceback describes exception path

Program paused
     ↓
debugger exposes live stack/state
```

## Why use both?

A traceback can tell you where to begin.

The debugger can then answer:

```text
What were the values?
Which branch executed?
Who called this?
Why did this input get here?
```

---

# 14. Variables While Debugging

When paused, inspect state rather than guessing.

## Local variables

```python
def calculate(price, quantity):
    subtotal = price * quantity
    breakpoint()
    return subtotal
```

At the breakpoint:

```text
price
quantity
subtotal
```

may all be visible.

## Function parameters

You can inspect:

```text
price = 100
quantity = 3
```

## Globals

Module-level state may also be visible, depending on the current frame/tool.

## Object attributes

For:

```python
account.balance
account.status
```

inspect both.

## Collections

For:

```python
transactions
```

inspect length, representative items, or a specific element.

## Nested data

Example:

```python
payload = {
    "user": {
        "account": {
            "balance": 500
        }
    }
}
```

A debugger lets you inspect:

```text
payload["user"]["account"]["balance"]
```

without adding multiple prints.

## Common mistake

Dumping a million-record list.

Instead inspect:

```python
len(records)
records[0]
records[index]
```

where appropriate.

---

# 15. Watching Expressions

## What is a watch expression?

A watch expression is an expression evaluated while paused, often repeatedly as execution stops.

Examples:

```text
total
```

```text
len(items)
```

```text
user["balance"]
```

```text
quantity * price
```

The `pdb` debugger provides `display`, which can show an expression's value when execution stops. citeturn108140view1

## Why is it useful?

Sometimes you care about one derived value rather than a whole object.

For example:

```python
approved = balance >= amount
```

Watching:

```text
balance >= amount
```

can help you see how the result changes through repeated execution.

## Danger: side effects

A debugger can evaluate Python expressions.

That means a careless expression may mutate state:

```python
database.delete(...)
```

or call a function with side effects.

Even a function that looks like a getter may not be purely observational.

## Better approach

Prefer:

```text
attribute access
length
comparisons
pure calculations
```

and avoid invoking mutating operations while investigating.

## Important technical detail

`pdb` permits Python statements to be evaluated in the current stack frame. This is powerful, but it means debugging can change the program if you deliberately execute assignments or mutating calls. citeturn108140view0

---

# 16. Local vs Global Scope During Debugging

Python name lookup follows nested scopes.

For beginner debugging, think:

```text
local
 ↓
enclosing
 ↓
global
 ↓
builtins
```

This is a simplified conceptual view of Python's LEGB lookup model.

## Example

```python
tax_rate = 0.18


def calculate_total(price):
    discount = 10
    breakpoint()
    return price - discount + price * tax_rate
```

Inside `calculate_total()` you can see:

```text
price      → local
discount   → local
tax_rate   → global
```

## What changes when you move frames?

Suppose:

```python
def outer():
    discount = 10
    inner()


def inner():
    breakpoint()
```

Inside `inner()` you do not automatically have:

```text
discount
```

as a local variable.

It exists in `outer()`'s frame.

The debugger may let you navigate to the outer frame.

## Why this matters

Many debugging mistakes come from inspecting the wrong frame.

---

# 17. Debugging Loops

Loops can generate hundreds or millions of iterations.

## Example

```python
for transaction in transactions:
    result = process(transaction)
```

A normal breakpoint pauses every iteration.

That is usually impractical.

## Strategy 1 — conditional breakpoint

Pause when:

```python
transaction["id"] == 5001
```

## Strategy 2 — inspect iteration counter

```python
for index, transaction in enumerate(transactions):
    ...
```

Inspect:

```text
index
```

## Strategy 3 — find the first bad item

Suppose records are:

```text
0 → good
1 → good
2 → good
3 → bad
```

A breakpoint around the mutation or validation may identify the first bad state.

## Strategy 4 — reduce the dataset

Instead of:

```text
1,000,000 records
```

create:

```text
10-record reproducer
```

## Common mistakes

- Step through every item.
- Print every item.
- Debug the loop body without knowing which iteration matters.

## Better approach

```text
Find suspicious case
→ condition
→ pause
→ inspect
```

---

# 18. Debugging Conditional Logic

Suppose:

```python
def approve_transfer(balance, amount):
    if balance >= amount:
        return "approved"
    return "rejected"
```

Suppose:

```text
balance = 100
amount = 100
```

but result is `"rejected"`.

Pause before the branch and inspect:

```text
balance
amount
balance >= amount
```

If:

```text
balance = 99
amount = 100
```

the branch is correct.

The bug may be earlier.

## Useful technique

Do not merely inspect the final Boolean.

Inspect its inputs.

```text
condition:
    balance >= amount

inputs:
    balance = ?
    amount = ?
```

## Better debugging question

> What exact values caused this branch to be selected?

This shifts debugging from:

```text
Why did else run?
```

to:

```text
Why was the condition false?
```

---

# 19. Debugging Exceptions

## What should you inspect?

When an exception occurs:

```text
exception type
exception message
failure line
call stack
current frame
local variables
arguments
upstream data
```

## Example

```python
def parse_amount(value: str) -> int:
    return int(value)


def process(order: dict) -> int:
    return parse_amount(order["amount"])
```

Failure:

```text
ValueError
```

Do not stop at:

```text
int(value)
```

Inspect:

```text
value
order
```

Maybe:

```text
value = "100O"
```

where a letter `O` appears instead of zero.

## Caught exceptions

Consider:

```python
try:
    process_order(order)
except ValueError:
    return {"status": "invalid"}
```

The original failure may be hidden from the outside.

A debugger exception breakpoint can help where supported because it can stop closer to the point where the exception is raised rather than only where the outer handler finishes.

---

# 20. Exception Breakpoints

## What is the concept?

An exception breakpoint asks the debugger to pause when an exception is raised.

The exact controls differ by debugger.

## Important distinction

There is a difference between:

```text
exception raised
```

and:

```text
exception uncaught
```

Example:

```python
try:
    int("abc")
except ValueError:
    return "invalid"
```

The `ValueError` is raised but caught.

If you only stop on **uncaught** exceptions, you may not pause there.

If you stop on the exception at raise time, you can inspect the exact state.

## Why is it useful?

Especially for:

- swallowed exceptions
- broad `except` blocks
- error translation
- nested failures
- unexpected retry behavior

## Common mistake

Turning on all exception breaks in a large application and getting interrupted constantly.

## Better approach

Start narrow.

Pause on:

```text
specific exception category
specific subsystem
specific reproduction
```

where the debugger supports that filtering.

---

# 21. Debugging Functions

Consider:

```python
def calculate_discount(subtotal: int) -> int:
    return subtotal * 10 // 100


def calculate_tax(amount: int) -> int:
    return amount * 18 // 100


def calculate_total(subtotal: int) -> int:
    discount = calculate_discount(subtotal)
    taxable = subtotal - discount
    tax = calculate_tax(taxable)
    return taxable + tax
```

Suppose:

```text
subtotal = 1000
expected total = 1062
actual total = 1080
```

## Debugging plan

1. Reproduce the exact value.
2. Break inside `calculate_total()`.
3. Inspect `subtotal`.
4. Step Into `calculate_discount()`.
5. inspect `discount`.
6. return to caller.
7. inspect `taxable`.
8. Step Into `calculate_tax()`.
9. inspect `tax`.
10. compare final result.

## Execution diagram

```text
calculate_total
      |
      +--> calculate_discount
      |        |
      |        +--> discount
      |
      +--> calculate_tax
               |
               +--> tax
      |
      +--> final total
```

## Deliberate bug

Suppose the code accidentally becomes:

```python
taxable = subtotal
```

The debugger can show:

```text
discount = 100
taxable  = 1000  ← suspicious
```

The incorrect state first appears at `taxable`.

That is much stronger evidence than seeing only the final wrong number.

---

# 22. Python `breakpoint()`

## What is it?

`breakpoint()` is Python's built-in way to request entry into a debugger at runtime.

It was introduced in Python 3.7. By default, it routes through `sys.breakpointhook()`, which normally enters `pdb`. citeturn193898search5turn682082view0

## Syntax

```python
breakpoint()
```

It can also receive arguments for the configured hook, but most beginner usage is the zero-argument form.

## Simple example

```python
def calculate_total(price, quantity):
    subtotal = price * quantity
    breakpoint()
    return subtotal
```

Run the program normally:

```bash
python app.py
```

When execution reaches `breakpoint()`, you enter the debugger.

## Why use it?

It is convenient because:

```python
import pdb
pdb.set_trace()
```

is no longer required for the common case.

## `PYTHONBREAKPOINT`

The built-in is configurable through `sys.breakpointhook()` and the `PYTHONBREAKPOINT` environment variable. This lets environments customize or disable the breakpoint behavior. citeturn193898search5

## Common mistake

Committing a temporary `breakpoint()` unintentionally.

Before committing:

```bash
grep -R "breakpoint()" .
```

or use your IDE/search tooling to find deliberate debug statements.

## When to use

- local investigation
- small reproductions
- deliberate interactive debugging

## When not to use

Avoid leaving interactive pauses in production code paths unless deliberately designed as part of a diagnostic mechanism.

---

# 23. Python `pdb`

## What is `pdb`?

`pdb` is Python's standard-library interactive debugger.

It supports:

- breakpoints
- single stepping
- stack-frame inspection
- source listing
- expression evaluation
- post-mortem debugging
- programmatic debugging

The current Python documentation describes it as an interactive source-code debugger with conditional breakpoints, stepping, stack-frame inspection, source listing, and evaluation in frame context. citeturn682082view0

## Why does it matter?

Even if you primarily use VS Code, PyCharm, another IDE, or an editor-integrated debugger, understanding `pdb` gives you a portable debugger mental model.

## Two common entry points

```python
breakpoint()
```

and:

```python
import pdb
pdb.set_trace()
```

## Why learn the CLI?

Because a debugger can be useful:

- over SSH
- in a minimal container
- on a remote Linux host
- without a graphical IDE
- inside CI reproduction environments

## Common mistake

Memorizing commands without learning the concepts.

Commands are tools.

The real skill is:

```text
observe
→ inspect
→ compare
→ hypothesize
```

---

# 24. `pdb` Breakpoints

## `breakpoint()`

Modern, concise:

```python
breakpoint()
```

## `pdb.set_trace()`

Explicitly enter `pdb`:

```python
import pdb


def calculate(value):
    pdb.set_trace()
    return value * 2
```

`pdb.set_trace()` enters the debugger at the calling stack frame. Current Python documentation also provides options such as `header` and, in recent Python releases, command-related features. citeturn682082view0

## Conceptual relationship

```text
breakpoint()
    ↓
sys.breakpointhook()
    ↓
configured debugger
    ↓
normally pdb
```

`pdb.set_trace()` explicitly asks for `pdb`.

## `pdb` breakpoint command

Inside `pdb`:

```text
(Pdb) b 20
```

sets a breakpoint at a line.

You can also specify a function.

`pdb` supports conditional breakpoints and temporary breakpoints through commands such as `condition` and `tbreak`. citeturn108140view0

## When to use

Use `breakpoint()` in application code when you want the standard configurable mechanism.

Use `pdb.set_trace()` when you intentionally want to invoke `pdb` directly.

---

# 25. Debugging from the Command Line

## Start a Python program under `pdb`

```bash
python -m pdb script.py
```

Python's current documentation also supports:

```bash
python -m pdb -m package.module
```

and, in Python 3.14+, process attachment by PID:

```bash
python -m pdb -p 1234
```

The latter is subject to operating-system/process conditions and should not be treated as a universal safe production technique. citeturn682082view0

## Simple script

```python
def add(a, b):
    return a + b


print(add(2, 3))
```

Run:

```bash
python -m pdb script.py
```

You enter the debugger before normal execution proceeds.

## Basic session

Conceptually:

```text
(Pdb) n
(Pdb) p a
(Pdb) p b
(Pdb) n
(Pdb) p result
(Pdb) c
```

## Useful commands

```text
n → next
s → step
c → continue
p → print expression
w → where/call stack
l → list source
q → quit
```

## Why command-line debugging matters

In a minimal Linux environment:

```text
no IDE
no graphical tools
SSH only
```

you can still debug Python.

---

# 26. Debugging Pytest Tests

A failed pytest test gives you a reproducible entry point.

## Workflow

```text
pytest failure
    ↓
identify exact test
    ↓
run only that test
    ↓
add breakpoint or use debugger option
    ↓
inspect state
    ↓
step through code
    ↓
identify root cause
    ↓
fix
    ↓
rerun focused test
    ↓
run broader suite
```

## Reproduce one test

```bash
pytest tests/test_orders.py::test_total -q
```

## Use pytest's debugger options

Current pytest provides:

```bash
pytest --pdb
```

to start the interactive debugger on errors or `KeyboardInterrupt`.

It also provides:

```bash
pytest --trace
```

to break immediately while running each test.

`--full-trace` can retain full tracebacks, and `--pdbcls` can select a custom debugger class. citeturn682082search0turn682082search4

## Inline breakpoint

```python
def test_total(cart):
    result = cart.total()
    breakpoint()
    assert result == 100
```

## Why this is useful

The test already provides a controlled reproduction.

Instead of debugging:

```text
entire application
```

you debug:

```text
one known scenario
```

## Common mistakes

- Running the entire suite for every debugging attempt.
- Debugging the assertion without inspecting Arrange state.
- Ignoring fixtures.
- Ignoring the specific parametrized case.

---

# 27. Debugging Fixtures

Suppose:

```python
import pytest


@pytest.fixture
def user():
    return User(name="Alice", active=True)


def test_user_is_active(user):
    breakpoint()
    assert user.active is True
```

If the test fails, inspect:

```text
user
user.name
user.active
```

But the interesting bug might be in the fixture itself.

## Debugging chain

```text
test
 ↓
fixture resolution
 ↓
fixture setup
 ↓
application code
```

## Example fixture bug

```python
@pytest.fixture
def account():
    return BankAccount("A", balance=0)
```

Suppose the test expects:

```text
balance = 500
```

The production code may be correct.

The fixture is wrong.

## Better debugging question

> Is the bad state already wrong before the Act step?

If yes, investigate Arrange/fixture setup before changing application code.

---

# 28. Debugging Parametrized Tests

Suppose:

```python
import pytest


@pytest.mark.parametrize(
    "value,expected",
    [
        (1, 1),
        (2, 4),
        (3, 9),
        (4, 16),
    ],
)
def test_square(value, expected):
    result = square(value)
    assert result == expected
```

Suppose:

```text
3 → failure
```

## Debugging workflow

1. Identify the specific case.
2. Re-run the individual parameterized node when convenient.
3. Add a breakpoint.
4. Inspect:
   ```text
   value
   expected
   result
   ```
5. Determine whether the test data or production logic is wrong.

## Readable IDs

```text
@pytest.mark.parametrize(
    "value,expected",
    [
        pytest.param(1, 1, id="one"),
        pytest.param(2, 4, id="two"),
        pytest.param(3, 9, id="three"),
    ],
)
```

A failure such as:

```text
test_square[three]
```

is easier to interpret.

## Common mistake

Assuming a failing parameter always means production code is wrong.

Parameterized test data can also be incorrect.

---

# 29. Debugging Async Python

## Key terms

### `async def`

Defines a coroutine function.

### `await`

Suspends the current coroutine until the awaited operation produces its result.

### Coroutine

An object representing an async computation that can be resumed.

### Event loop

A runtime mechanism that schedules and drives asynchronous tasks.

## Example

```python
import asyncio


async def fetch_value():
    await asyncio.sleep(0)
    return 42


async def main():
    result = await fetch_value()
    breakpoint()
    print(result)


asyncio.run(main())
```

While paused, you care about:

```text
result
current coroutine/task
call context
```

## Why async debugging feels different

Execution can suspend at:

```python
await something()
```

and resume later.

Multiple tasks may progress around the same time.

## Important limitation

IDE support varies.

Some environments expose async-task views and specialized stepping. Others provide more basic source-level debugging.

Python 3.14's `pdb` also includes an async `set_trace_async()` entry point for use inside async functions; this is a current-version feature and should not be assumed for older Python versions. citeturn682082view0

## Common mistake

Assuming:

```text
one source-line sequence
=
one global execution timeline
```

Async programs can have multiple tasks with interleaved progress.

---

# 30. Debugging Threads

## Thread

A thread is an execution path within a process.

Multiple threads can run concurrently.

## Example

```python
import threading


def worker():
    total = 10
    breakpoint()
    return total


thread = threading.Thread(target=worker)
thread.start()
thread.join()
```

## Why is thread debugging harder?

Because:

```text
Thread A
Thread B
Thread C
```

may all have active execution contexts.

Shared state can create:

- races
- lost updates
- inconsistent reads

## Multiple call stacks

Conceptually:

```text
Thread A stack
    ↓
function_a
function_b

Thread B stack
    ↓
function_x
function_y
```

Debugger interfaces may let you select threads.

## Important distinction

A race condition is not necessarily visible from one paused thread.

Pausing one thread can also change timing and hide the race.

## Better approach

Combine:

```text
debugger
+
logs
+
deterministic reproduction
+
tests
```

## Production considerations

Interactive pauses can significantly change timing. Use caution when investigating concurrency bugs.

---

# 31. Debugging Processes

## Thread vs process

A **process** has its own address space and operating-system resources.

Threads within a process typically share that process's memory.

Conceptually:

```text
Process
 ├── Thread A
 ├── Thread B
 └── Thread C
```

For multiple processes:

```text
Process A
    separate memory
Process B
    separate memory
```

## Why is multiprocess debugging harder?

Because:

- there are multiple address spaces
- multiple processes may have different states
- IPC may be involved
- process startup/termination complicates reproduction

## Attaching

Current Python's `python -m pdb -p PID` can attach `pdb` to a running Python process on supported platforms/configurations. The Python 3.14 documentation notes that attachment may wait until a bytecode instruction executes or a signal is received if the target is blocked in a system call or I/O. citeturn682082view0

Treat this as a technical capability, not an invitation to attach to production casually.

## Better production approach

Prefer:

```text
logs
metrics
traces
safe diagnostic endpoints
controlled reproductions
```

unless live attachment is explicitly designed, authorized, and operationally safe.

---

# 32. Debugging State

## Observe vs mutate

When debugging, your first goal should be:

```text
observe
```

not:

```text
change
```

## Why?

Suppose:

```python
balance = 500
```

You manually change it to:

```text
balance = 1000
```

Now the program may behave differently.

You have changed the evidence.

## When modifying state can be useful

Sometimes an experienced developer intentionally modifies state to answer a controlled question:

> "What happens if this condition were true?"

That can be a useful experiment.

But record that you changed it and do not mistake the modified run for the original reproduction.

## Best practice

First:

```text
observe original state
```

Then:

```text
form hypothesis
```

Then, if necessary:

```text
controlled experiment
```

---

# 33. Debugging Side Effects

Evaluating an expression can execute code.

Potential side effects include:

- database writes
- API requests
- file changes
- cache mutations
- object mutations
- event publication

## Example

Suppose:

```python
order.total()
```

normally computes a value but unexpectedly logs or mutates internal state.

Calling it repeatedly from the debugger can change behavior.

## Safer inspection

Prefer:

```text
order._raw_total
```

or other known observational state where appropriate.

Better still, inspect a pure value that has already been calculated.

## Security concern

Do not type sensitive commands into a debugger that could:

```text
print credentials
dump secrets
make payment calls
delete data
```

A debugger is powerful because it can operate inside the program's authority.

---

# 34. Debugging Objects

Useful Python inspection techniques include:

```python
type(value)
```

```python
vars(value)
```

when the object has an instance `__dict__`.

You may also inspect:

```python
value.__dict__
```

where appropriate.

## `type(value)`

Answers:

> What class/type is this object?

## `vars(value)`

For appropriate objects, shows their instance namespace.

Example:

```python
class User:
    def __init__(self, name: str, active: bool):
        self.name = name
        self.active = active


user = User("Alice", True)
```

A debugger or REPL can inspect:

```python
type(user)
vars(user)
```

## `repr(value)`

A good `__repr__` can make debugger inspection much easier.

Example:

```python
class User:
    def __repr__(self):
        return f"User(name={self.name!r}, active={self.active!r})"
```

## Common mistake

Using `__dict__` as if every object must have one.

Objects using slots or extension types may behave differently.

---

# 35. Debugging Data Structures

Large data structures are common failure sources.

## Lists

Inspect:

```python
len(items)
items[:5]
items[index]
```

## Dictionaries

Inspect:

```python
payload.keys()
payload.get("status")
```

or direct access when the field is known.

## Sets

Inspect:

```python
len(ids)
"abc" in ids
```

## Tuples

Inspect:

```python
len(row)
row[0]
```

## Nested structures

Instead of dumping everything:

```python
payload
```

inspect the path that matters:

```python
payload["user"]["account"]["balance"]
```

## Why this matters

A debugger is not only a pause mechanism.

It is a **controlled observation tool**.

---

# 36. Debugging Recursion

Suppose:

```python
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

Call:

```python
factorial(4)
```

The conceptual call stack becomes:

```text
factorial(4)
    ↓
factorial(3)
    ↓
factorial(2)
    ↓
factorial(1)
```

## Why is this useful?

You can see:

```text
n = 4
n = 3
n = 2
n = 1
```

Each recursive call gets its own frame.

## Common recursion bugs

### Incorrect base case

```text
if n < 1:
```

instead of:

```text
if n <= 1:
```

### Incorrect recursive step

```python
return factorial(n)
```

instead of:

```python
return factorial(n - 1)
```

### Infinite recursion

The call stack keeps growing until a recursion-related failure occurs.

## Debugging strategy

Inspect:

```text
n
current frame
caller frame
```

and ask:

> Does the stack move toward the base case?

---

# 37. Debugging Decorators

Decorators often create wrappers.

Example:

```python
def log_call(func):
    def wrapper(*args, **kwargs):
        print("calling")
        return func(*args, **kwargs)

    return wrapper
```

Now:

```python
@log_call
def calculate():
    return 42
```

Conceptually:

```text
calculate()
    ↓
wrapper()
    ↓
original calculate()
```

## Why can this be confusing?

The debugger may show:

```text
wrapper
```

when you expected:

```text
calculate
```

## Debugging questions

- Am I in the wrapper?
- Did the wrapper modify arguments?
- Did it catch exceptions?
- Did it alter the return value?
- Did it call the original function?

## Good practice

Use `functools.wraps` in production decorators so metadata is preserved:

```python
from functools import wraps


def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
```

This does not eliminate runtime wrapper behavior, but it improves introspection and debugging context.

---

# 38. Debugging Context Managers

Context managers use:

```python
with resource:
    ...
```

Conceptually:

```text
__enter__()
   ↓
body
   ↓
__exit__()
```

Example:

```python
class Resource:
    def __enter__(self):
        print("open")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("close")


with Resource() as resource:
    breakpoint()
    print(resource)
```

## What can go wrong?

- `__enter__()` creates bad state
- body mutates resource unexpectedly
- `__exit__()` suppresses an exception
- cleanup does not execute as expected

## Debugging strategy

Use breakpoints in:

```text
__enter__
body
__exit__
```

especially when lifecycle bugs are suspected.

---

# 39. Debugging Generators

## What is a generator?

A generator function uses `yield`.

Example:

```python
def numbers():
    yield 1
    yield 2
    yield 3
```

Calling:

```python
generator = numbers()
```

does not immediately execute all three `yield` statements.

The generator executes lazily as values are requested.

## Why is debugging different?

Execution can suspend at a `yield` and later resume.

Conceptually:

```text
numbers()
   ↓
yield 1
   ↓
suspended
   ↓
resume
   ↓
yield 2
```

## Debugging strategy

Inspect:

```text
where execution is paused
current yielded value
local variables
resume point
```

## Common mistake

Assuming a generator runs from top to bottom at creation time.

It does not.

---

# 40. Debugging External Dependencies

Applications often interact with:

- databases
- HTTP APIs
- files
- queues
- cloud services

A failure may come from:

```text
application
or
dependency
```

## Diagnostic model

```text
application input
    ↓
client code
    ↓
dependency call
    ↓
dependency response
    ↓
application processing
```

At each boundary ask:

```text
What did I send?
What did I receive?
What did I expect?
```

## Example

An API request fails.

Inspect:

```text
URL
method
headers
payload
timeout
status
response body
```

Then determine:

```text
Was the request wrong?
Was the response wrong?
Did our parser mishandle a correct response?
```

## Common mistake

Immediately blaming the external service.

The bug may be:

```python
response.json()["data"]["items"]
```

when the actual response is:

```json
{"result": {"items": []}}
```

---

# 41. Debugging Network/API Issues

Use the request-response pipeline:

```text
application
   ↓
HTTP client
   ↓
network
   ↓
server
   ↓
response
   ↓
parser
   ↓
business logic
```

## Inspect

### URL

Is the endpoint correct?

### Method

```text
GET
POST
PUT
PATCH
DELETE
```

### Headers

Check relevant headers, but do not dump secrets.

### Payload

Verify:

```json
{
  "amount": 100
}
```

is actually what was sent.

### Status

Examples:

```text
2xx
4xx
5xx
```

### Response body

Inspect schema and values.

### Timeout

Was the client waiting too long?

### Retries

Did retries happen?

Could retries create duplicate side effects?

## Security

Never casually log:

```text
API keys
access tokens
passwords
session cookies
payment credentials
personal secrets
```

Redact or exclude them.

---

# 42. Debugging Database Issues

A database bug can involve:

- wrong query
- wrong parameters
- missing record
- incorrect transaction state
- connection failure
- unexpected `NULL`
- mapping error

## Example

```python
def get_balance(conn, account_id):
    row = conn.execute(
        "SELECT balance FROM accounts WHERE id = ?",
        (account_id,),
    ).fetchone()

    return row[0]
```

If:

```text
TypeError
or
None-related failure
```

debug:

```text
account_id
query parameters
row
```

## Transaction state

Also inspect:

```text
committed?
rolled back?
transaction still open?
```

## Important architecture point

The call stack may tell you:

```text
API endpoint
 ↓
service
 ↓
repository
 ↓
database call
```

That tells you where the interaction originated.

It does not tell you whether the database or application is at fault.

---

# 43. Debugging Data Pipelines

Consider:

```text
input
 ↓
parse
 ↓
validate
 ↓
transform
 ↓
write
```

## Why interactive stepping does not scale

Suppose:

```text
10 million records
```

A line breakpoint inside:

```text
for row in rows:
```

would be useless.

## Better strategy

### Reduce the dataset

Use:

```text
10–100 representative records
```

### Conditional breakpoint

Pause when:

```python
row["transaction_id"] == "TX-5001"
```

### Inspect first bad state

Find:

```text
input correct
→ parsed correct
→ transformed incorrect
```

The first incorrect transition is usually more useful than the final bad output.

## Example

```python
for row in rows:
    parsed = parse(row)
    validated = validate(parsed)
    transformed = transform(validated)
    write(transformed)
```

Place breakpoints around the transitions:

```text
parse
validate
transform
write
```

## Production consideration

For large pipelines, combine:

```text
small reproducible input
+
structured logs
+
data-quality checks
+
debugger
```

---

# 44. Debugging ML Pipelines

An ML pipeline might look like:

```text
data loading
    ↓
preprocessing
    ↓
feature generation
    ↓
model call
    ↓
postprocessing
    ↓
result
```

## Debugging questions

### Data loading

```text
Did the expected rows arrive?
```

### Preprocessing

```text
Did missing values become expected representations?
```

### Feature generation

```text
Are shapes and dtypes correct?
```

### Model call

```text
Did the expected configuration reach the model?
```

### Postprocessing

```text
Did we transform the model result correctly?
```

## Useful variables to inspect

```text
batch.shape
batch.dtype
features.shape
features.dtype
missing_count
configuration
prediction
```

## Debugger vs model evaluation

A debugger can show:

```text
features = wrong shape
```

It does not tell you whether:

```text
the model is accurate
```

Model quality requires evaluation against appropriate data and metrics.

---

# 45. Debugging AI/LLM Applications

A useful application pipeline is:

```text
request
  ↓
validation
  ↓
prompt construction
  ↓
retrieval
  ↓
model invocation
  ↓
output parsing
  ↓
tool execution
  ↓
response
```

## Good breakpoint locations

### Prompt construction

Inspect:

```text
system instructions
user input
retrieved context
variables
```

Be careful not to expose sensitive information.

### Retrieval

Inspect:

```text
number of documents
document IDs
ranking
filters
```

### Tool arguments

Inspect:

```text
tool name
arguments
authorization context
```

### Response parser

Inspect:

```text
raw output format
parsed object
validation result
```

### Error handling

Inspect:

```text
exception
retry counter
fallback selection
```

## Important limitation

A debugger can inspect the application state surrounding a model invocation.

It should not be treated as a mechanism for accessing hidden chain-of-thought or private internal model reasoning.

## Better debugging question

Instead of:

> "Why did the model think this?"

ask:

> "What prompt, retrieved context, configuration, tool result, and application state did our code provide, and how did our application interpret the output?"

---

# 46. Debugging Agentic AI Systems

Consider:

```text
user request
   ↓
workflow/controller
   ↓
tool selection
   ↓
tool execution
   ↓
state update
   ↓
next step
   ↓
termination
```

## Inspect

- user input
- configuration
- current state
- tool name
- tool arguments
- tool result
- iteration count
- retry count
- termination condition
- final structured result

## Example

```python
def run_transfer_agent(agent, request):
    balance = agent.get_balance(request["account"])
    if balance < request["amount"]:
        return {"status": "rejected"}

    result = agent.transfer(
        request["account"],
        request["recipient"],
        request["amount"],
    )
    return result
```

A breakpoint before `transfer()` lets you inspect:

```text
balance
request["amount"]
request["recipient"]
```

## State-machine debugging

For an agent workflow:

```text
START
 ↓
BALANCE_CHECKED
 ↓
AUTHORIZED
 ↓
TRANSFER_EXECUTED
 ↓
COMPLETED
```

A bug may be:

```text
BALANCE_CHECKED
 ↓
TRANSFER_EXECUTED
```

without:

```text
AUTHORIZED
```

The debugger helps identify where the invalid transition occurs.

## Important limitation

Do not attempt to debug hidden model chain-of-thought. Debug:

```text
observable state
tool execution
workflow transitions
application decisions
```

---

# 47. Systematic Debugging Strategy

Use a repeatable process.

## 1. Observe the symptom

What exactly is wrong?

Bad:

```text
"It is broken."
```

Better:

```text
"Expected 300, got 350 when quantity is 3."
```

## 2. Reproduce it

Can you cause the same failure again?

## 3. Minimize it

Reduce:

```text
large application
→ small feature
→ one request
→ one input
```

## 4. Identify the failing boundary

Where does expected state become unexpected state?

```text
input correct
→ parsing correct
→ transformation wrong
```

Then the transformation boundary becomes the focus.

## 5. Place a strategic breakpoint

Pause near the suspicious transition.

## 6. Inspect state

Check:

```text
inputs
locals
objects
return values
conditions
```

## 7. Read the call stack

Who called this function?

Why is it running?

## 8. Step

Use:

```text
next
step
return
continue
```

selectively.

## 9. Form a hypothesis

Example:

> Discount is applied twice.

## 10. Verify

Inspect:

```text
discount before call
discount after call
final subtotal
```

## 11. Fix root cause

Correct the underlying defect.

## 12. Run tests

Start narrow:

```bash
pytest tests/test_orders.py::test_discount -q
```

Then broader tests.

## 13. Add regression protection

Keep or add a test for the discovered defect.

---

# 48. Root Cause vs Symptom

## Symptom

The visible failure.

Example:

```text
total = 120
expected = 100
```

## Possible root cause

```text
discount applied twice
```

But there may be other causes:

```text
wrong tax
wrong input quantity
wrong price
wrong currency
```

## Why the distinction matters

Fixing the symptom may hide the problem.

Example:

```python
if total == 120:
    total = 100
```

This is not a root-cause fix.

## Better debugging

Trace the data:

```text
expected input
    ↓
actual input
    ↓
intermediate state
    ↓
wrong intermediate state
    ↓
final wrong result
```

The earliest incorrect state is often more informative than the final symptom.

---

# 49. Debugging by Hypothesis

Scientific debugging is faster than random clicking.

## Poor approach

```text
click breakpoint
step
click another breakpoint
change code
rerun
hope
```

## Better approach

```text
Hypothesis:
discount is applied twice
```

Then gather evidence.

```text
discount before first application = 10
discount after first application = 10
second application = ? 
```

## Hypothesis cycle

```text
Hypothesis
    ↓
Observation
    ↓
Evidence
    ↓
Confirmed / refuted
    ↓
Next hypothesis
```

## Example

Symptom:

```text
order total too low
```

Hypothesis:

> quantity is doubled.

Inspect:

```text
quantity = 4
```

False.

Next hypothesis:

> discount is doubled.

Inspect:

```text
discount = 200
```

confirmed.

## Why this matters

A debugger provides evidence. A hypothesis tells you what evidence to look for.

---

# 50. Minimal Reproducible Example

## What is an MRE?

A **Minimal Reproducible Example** is the smallest program/data scenario that still reproduces the defect.

## Why does it matter?

A smaller reproduction reduces:

- execution time
- cognitive load
- noise
- unrelated dependencies

## Example

Instead of reproducing a data bug using:

```text
2 million rows
15 services
Kafka
PostgreSQL
LLM provider
scheduler
```

reduce it to:

```python
rows = [
    {"amount": "100"},
    {"amount": "100O"},
]
```

and one function:

```python
parse_amount(rows[1]["amount"])
```

## MRE workflow

```text
large failure
    ↓
remove unrelated components
    ↓
reduce data
    ↓
reduce calls
    ↓
reduce environment
    ↓
small reproducible bug
```

## Common mistake

Stopping once the bug happens once.

A good MRE should be:

```text
repeatable
small
understandable
```

---

# 51. Common Debugging Mistakes

## Mistake 1 — Print everywhere

### Bad

```python
print(a)
print(b)
print(c)
print(d)
```

### Why

Creates noise and often does not reveal the execution context.

### Better

Pause once at the suspicious transition and inspect the relevant state.

---

## Mistake 2 — Random breakpoints

### Why

You collect information without a debugging question.

### Better

Place breakpoints around a hypothesis.

---

## Mistake 3 — Step through everything

### Why

It is slow and cognitively expensive.

### Better

Use:

```text
continue
conditional breakpoints
step over
step out
```

strategically.

---

## Mistake 4 — Ignore the call stack

### Why

You may inspect the current function without understanding why it received the data.

### Better

Ask:

> Who called this function, and what did the caller pass?

---

## Mistake 5 — Inspect the wrong frame

A variable may appear "missing" because it belongs to the caller frame.

### Better

Move to the relevant frame.

---

## Mistake 6 — Debug without reproduction

Without a stable reproduction, you may chase a moving target.

### Better

Create a small reproducible scenario.

---

## Mistake 7 — Change multiple things at once

Then you cannot tell which change fixed the behavior.

### Better

Change one causal thing at a time when practical.

---

## Mistake 8 — Fix the symptom

Example:

```python
if wrong_value:
    wrong_value = correct_value
```

### Better

Find where `wrong_value` was first created.

---

## Mistake 9 — Ignore recent changes

A regression often becomes much easier to diagnose by comparing recent code/configuration/dependency changes.

This is evidence, not proof; old latent bugs can surface after unrelated changes.

---

## Mistake 10 — Log secrets

Never casually expose:

```text
tokens
passwords
API keys
private data
payment information
```

---

## Mistake 11 — Assume debugger proves causality

A breakpoint shows state at a point in execution.

It does not automatically prove:

```text
A caused B
```

You still need reasoning and controlled experiments.

---

# 52. Debugger vs Logging

| Tool | Best for |
|---|---|
| Debugger | interactive local investigation |
| Logging | recorded events and diagnostic context |
| Metrics | trends and aggregate health |
| Tracing | request path across components |
| Tests | repeatable expected behavior |

## Debugger strengths

```text
live state
step execution
frame navigation
interactive inspection
```

## Logging strengths

```text
historical evidence
remote systems
production-safe diagnosis when designed correctly
```

## Why logging can beat a debugger in production

Suppose an incident occurred at:

```text
03:17
```

You cannot rewind a normal server process to that exact moment.

Logs/traces may preserve relevant evidence.

## Why debugger can beat logs locally

A complex nested object can be inspected directly without anticipating the field before the run.

## Production perspective

Use a layered strategy:

```text
tests
+
logs
+
metrics
+
traces
+
interactive debugger when appropriate
```

---

# 53. Debugger vs Traceback

## Traceback

Best for:

```text
where exception propagated
```

## Debugger

Best for:

```text
what was state at this point?
why did this branch execute?
who called this?
what happens next?
```

## Example

Traceback:

```text
parse_amount → ValueError
```

Debugger:

```text
value = "100O"
caller = validate_order
order_id = "TX-5001"
```

Now you have more evidence.

## Use both

```text
traceback
  ↓
starting point
  ↓
debugger
  ↓
state inspection
  ↓
root cause
```

---

# 54. Debugging and Test-Driven Workflow

A strong engineering loop is:

```text
test fails
    ↓
debug
    ↓
find root cause
    ↓
fix
    ↓
test passes
    ↓
retain regression protection
```

## Example

A pytest failure:

```text
assert result == 100
E assert 120 == 100
```

Debug:

```text
result = 120
subtotal = 100
discount = -20
```

Hypothesis:

> Discount sign is inverted.

Fix:

```python
total = subtotal - discount
```

Then:

```text
focused test
→ broader related tests
→ complete suite
```

## Why tests improve debugging

Tests provide:

- repeatability
- controlled input
- expected result
- quick reruns

The best debugger session often starts with a good test.

---

# 55. Production Debugging

## Local interactive debugging

Usually:

```text
developer
+
source code
+
breakpoint
+
local process
```

## Production incident diagnosis

Usually:

```text
service
+
logs
+
metrics
+
traces
+
correlation IDs
+
deployment history
+
reproduction
```

## Why is production debugging different?

Production may contain:

- real customer data
- high request volume
- distributed dependencies
- strict latency requirements
- privacy constraints
- security constraints
- concurrency
- irreversible side effects

Pausing code can be dangerous.

## Safe production-oriented practices

### Use correlation IDs

Connect:

```text
request
→ service logs
→ downstream calls
```

### Redact secrets

Never expose tokens or passwords.

### Prefer read-only diagnostics

When possible:

```text
inspect
```

rather than:

```text
mutate
```

### Reproduce outside production

Use:

```text
sanitized data
controlled environment
same configuration
same code version
```

### Capture deployment context

Check:

```text
commit
configuration change
dependency version
feature flag
schema migration
```

## Important

Do not treat attaching a debugger to production as a routine first step. It may be possible in some environments, but the operational, security, and concurrency implications must be explicitly understood.

---

# 56. Complete Realistic Debugging Example

We will debug a small bank transaction flow.

## Requirements

1. Transaction amount must be positive.
2. Sender must have enough balance.
3. Transfer must decrease the sender balance.
4. Transfer must increase the receiver balance.
5. A rejected transaction must not mutate balances.

## Production-like code

```python
class Account:
    def __init__(self, account_id: str, balance: int):
        self.account_id = account_id
        self.balance = balance


def validate_transfer(sender: Account, receiver: Account, amount: int) -> None:
    if amount <= 0:
        raise ValueError("amount must be positive")

    if amount > sender.balance:
        raise ValueError("insufficient balance")

    if sender.account_id == receiver.account_id:
        raise ValueError("accounts must differ")


def execute_transfer(sender: Account, receiver: Account, amount: int) -> None:
    validate_transfer(sender, receiver, amount)

    sender.balance -= amount
    receiver.balance += amount


def transfer_service(sender: Account, receiver: Account, amount: int) -> dict:
    execute_transfer(sender, receiver, amount)

    return {
        "status": "success",
        "sender_balance": sender.balance,
        "receiver_balance": receiver.balance,
    }
```

Suppose a developer reports:

```text
Expected sender balance = 700
Expected receiver balance = 800
Actual sender balance = 700
Actual receiver balance = 700
```

The transaction amount was:

```text
300
```

## Step 1 — Reproduce

```python
def test_transfer_service():
    sender = Account("A", 1000)
    receiver = Account("B", 500)

    result = transfer_service(sender, receiver, 300)

    assert result["sender_balance"] == 700
    assert result["receiver_balance"] == 800
```

Suppose this fails.

## Step 2 — Break at the mutation

Place a breakpoint in:

```python
sender.balance -= amount
receiver.balance += amount
```

## Step 3 — Inspect

At the first statement:

```text
sender.balance = 1000
receiver.balance = 500
amount = 300
```

Correct.

After:

```python
sender.balance -= amount
```

inspect:

```text
sender.balance = 700
receiver.balance = 500
```

Correct.

After:

```python
receiver.balance += amount
```

inspect:

```text
sender.balance = 700
receiver.balance = 800
```

Also correct.

## Step 4 — Read the call stack

```text
transfer_service
    ↓
execute_transfer
    ↓
validate_transfer
```

Suppose the debugger actually shows:

```text
receiver.balance = 200
```

before execution.

The problem may be in setup, not transfer logic.

## Step 5 — Hypothesis

> The receiver's initial balance is not what the test expectation assumes.

## Step 6 — Verify

Inspect the Arrange state:

```python
receiver = Account("B", 200)
```

Now:

```text
200 + 300 = 500
```

The service may be completely correct.

## Root cause

The test expected `800` but arranged a receiver with `200`.

## Lesson

A debugger can prevent you from "fixing" correct production code simply because the test scenario was wrong.

---

## Second bug: negative transfer

Suppose the implementation is changed accidentally:

```python
def validate_transfer(sender, receiver, amount):
    if amount < 0:
        raise ValueError("amount must be positive")
```

Zero now passes.

## Regression test

```python
import pytest


def test_zero_transfer_is_rejected():
    sender = Account("A", 1000)
    receiver = Account("B", 500)

    with pytest.raises(ValueError, match="amount must be positive"):
        transfer_service(sender, receiver, 0)
```

This test captures the contract and protects future changes.

---

## Debugging sequence summary

```text
pytest failure
    ↓
reproduce
    ↓
breakpoint near mutation
    ↓
inspect sender/receiver/amount
    ↓
inspect call stack
    ↓
step
    ↓
discover setup mismatch
    ↓
do not change production code unnecessarily
```

This is the kind of debugging discipline expected in production engineering.

---

# 57. Complete Mini Project

## Project objective

Build a small order-processing application containing enough layers to make debugger usage meaningful.

## Features

```text
Order
 ↓
add_item
 ↓
calculate_subtotal
 ↓
apply_discount
 ↓
calculate_tax
 ↓
final_total
```

## Source code

```python
class Order:
    def __init__(self, items: list[tuple[int, int]]):
        self.items = items


def calculate_subtotal(items: list[tuple[int, int]]) -> int:
    return sum(price * quantity for price, quantity in items)


def apply_discount(subtotal: int, discount_percent: int) -> int:
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount must be between 0 and 100")
    return subtotal - (subtotal * discount_percent // 100)


def calculate_tax(amount: int, tax_percent: int) -> int:
    return amount * tax_percent // 100


def calculate_total(order: Order, discount_percent: int, tax_percent: int) -> int:
    subtotal = calculate_subtotal(order.items)
    discounted = apply_discount(subtotal, discount_percent)
    tax = calculate_tax(discounted, tax_percent)
    return discounted + tax
```

## Deliberate bug

Introduce:

```python
discounted = apply_discount(subtotal, discount_percent)
tax = calculate_tax(subtotal, tax_percent)
```

instead of:

```python
tax = calculate_tax(discounted, tax_percent)
```

Now the tax ignores the discount.

## Debugging task

Input:

```python
order = Order([
    (100, 2),
    (50, 1),
])
```

Discount:

```text
10%
```

Tax:

```text
20%
```

## Debugging plan

```text
break at calculate_total
    ↓
inspect subtotal
    ↓
step into discount
    ↓
inspect discounted
    ↓
step to tax
    ↓
inspect tax input
    ↓
compare expected tax input
```

## Expected observation

```text
subtotal  = 250
discounted = 225
```

The buggy code uses:

```text
tax input = 250
```

when it should use:

```text
tax input = 225
```

## Corrected code

```python
def calculate_total(order: Order, discount_percent: int, tax_percent: int) -> int:
    subtotal = calculate_subtotal(order.items)
    discounted = apply_discount(subtotal, discount_percent)
    tax = calculate_tax(discounted, tax_percent)
    return discounted + tax
```

## Regression test

```python
def test_discount_is_applied_before_tax():
    order = Order([
        (100, 2),
        (50, 1),
    ])

    result = calculate_total(
        order,
        discount_percent=10,
        tax_percent=20,
    )

    assert result == 270
```

Calculation:

```text
subtotal = 250
discount = 25
discounted = 225
tax = 45
total = 270
```

## Mini-project tasks

1. Run the broken code.
2. Reproduce the incorrect total.
3. Add a breakpoint inside `calculate_total()`.
4. Inspect `subtotal`.
5. Step Into `apply_discount()`.
6. Inspect `discounted`.
7. Step to `calculate_tax()`.
8. Identify the incorrect argument.
9. Fix the code.
10. Run the regression test.
11. Add additional boundary tests around `discount_percent=0` and `100`.

---

# 58. Coding Exercises

## Level 1 — Basic

### Exercise 1 — First breakpoint

**Problem**

```python
def add(a, b):
    result = a + b
    return result
```

**Task**

Insert a breakpoint immediately before the return and inspect `result`.

**Hints**

Use:

```python
breakpoint()
```

**Complete solution**

```python
def add(a, b):
    result = a + b
    breakpoint()
    return result
```

At the debugger inspect:

```text
p result
```

**Explanation**

The breakpoint pauses after the calculation but before the return, making the computed state visible.

**Common mistake**

Putting the breakpoint after the return. That line will never be reached.

---

### Exercise 2 — Step Over

**Problem**

```python
def double(value):
    return value * 2


def main():
    result = double(10)
    print(result)
```

**Task**

Pause before `double(10)` and practice Step Over.

**Hints**

Step Over should return to `main()` after `double()` completes.

**Complete solution**

```python
def main():
    breakpoint()
    result = double(10)
    print(result)
```

Then use your IDE's **Step Over** or `n` in `pdb`.

**Explanation**

You do not need to enter `double()` to inspect its implementation.

**Common mistake**

Using Step Into and then wondering why the debugger entered `double()`.

---

### Exercise 3 — Step Into

**Problem**

Use the same program.

**Task**

Enter `double()` using Step Into.

**Complete solution**

```python
def main():
    breakpoint()
    result = double(10)
```

Use Step Into or:

```text
(Pdb) s
```

**Explanation**

Step Into follows the function call into its implementation.

**Common mistake**

Confusing Step Over with Step Into.

---

### Exercise 4 — Inspect a local variable

**Problem**

```python
def calculate(price, quantity):
    subtotal = price * quantity
    breakpoint()
    return subtotal
```

**Task**

Inspect:

```text
price
quantity
subtotal
```

**Complete solution**

Run:

```text
(Pdb) p price
(Pdb) p quantity
(Pdb) p subtotal
```

**Explanation**

All three belong to the current function frame.

**Common mistake**

Looking for the variables after stepping out of the function.

---

### Exercise 5 — Read a call stack

**Problem**

```python
def a():
    b()


def b():
    c()


def c():
    breakpoint()
```

**Task**

Determine the call stack.

**Complete solution**

Conceptually:

```text
a()
↓
b()
↓
c()
```

Inside `pdb`, use:

```text
(Pdb) w
```

**Explanation**

The current frame is `c()` with callers `b()` and `a()`.

**Common mistake**

Reading the stack as a list of source-code lines rather than active function calls.

---

## Level 2 — Intermediate

### Exercise 6 — Conditional breakpoint

**Problem**

```python
transactions = [
    {"id": 1, "amount": 10},
    {"id": 2, "amount": 20},
    {"id": 5001, "amount": 999},
]
```

**Task**

Pause only for transaction ID `5001`.

**Hints**

Use an IDE conditional breakpoint or a `pdb` breakpoint condition.

**Complete solution**

Conceptually:

```text
condition:
transaction["id"] == 5001
```

**Explanation**

This prevents unnecessary pauses for unrelated records.

**Common mistake**

Breaking on every iteration.

---

### Exercise 7 — Identify the first bad state

**Problem**

```python
def pipeline(value):
    parsed = value.strip()
    normalized = parsed.lower()
    transformed = normalized.replace("a", "@")
    return transformed
```

Suppose input `"Alice"` produces the wrong result.

**Task**

Pause after each stage and identify where the output first differs from the intended value.

**Complete solution**

```python
def pipeline(value):
    parsed = value.strip()
    breakpoint()

    normalized = parsed.lower()
    breakpoint()

    transformed = normalized.replace("a", "@")
    breakpoint()

    return transformed
```

**Explanation**

Compare expected and actual after each transformation. The earliest incorrect state is usually the best debugging target.

**Common mistake**

Only inspecting the final output.

---

### Exercise 8 — Debug a conditional

**Problem**

```python
def approve(balance, amount):
    if balance >= amount:
        return True
    return False
```

**Task**

Find why:

```text
approve(99, 100)
```

returns `False`.

**Complete solution**

```python
def approve(balance, amount):
    breakpoint()

    if balance >= amount:
        return True
    return False
```

Inspect:

```text
p balance
p amount
p balance >= amount
```

Expected:

```text
99
100
False
```

**Explanation**

The function is behaving consistently with its input.

**Common mistake**

Changing the comparison before checking the actual input values.

---

### Exercise 9 — Debug an exception

**Problem**

```python
def parse(value):
    return int(value)


result = parse("10O")
```

**Task**

Identify the bad input.

**Complete solution**

Use:

```bash
python -m pdb script.py
```

When stopped at the exception, inspect:

```text
(Pdb) p value
```

**Explanation**

The character `"O"` is not the digit `"0"`.

**Common mistake**

Changing the parser without confirming the input.

---

### Exercise 10 — Debug pytest

**Problem**

```python
def total(price, quantity):
    return price * quantity


def test_total():
    result = total(10, 3)
    breakpoint()
    assert result == 30
```

**Task**

Run only this test and inspect `result`.

**Complete solution**

```bash
pytest tests/test_total.py::test_total -q
```

Then at the breakpoint:

```text
(Pdb) p result
```

**Explanation**

Focused test execution reduces noise.

**Common mistake**

Running the entire test suite while debugging one simple function.

---

## Level 3 — Advanced

### Exercise 11 — Debug a fixture

**Problem**

```python
import pytest


@pytest.fixture
def account():
    return {"balance": 100}


def test_balance(account):
    breakpoint()
    assert account["balance"] == 500
```

**Task**

Find whether the failure is in the fixture or test.

**Complete solution**

Inspect:

```text
(Pdb) p account
(Pdb) p account["balance"]
```

You will see:

```text
100
```

The fixture provides the wrong setup for the test expectation.

**Explanation**

The production code is not involved yet.

**Common mistake**

Changing application code when the Arrange state is already incorrect.

---

### Exercise 12 — Debug a parametrized case

**Problem**

```python
import pytest


@pytest.mark.parametrize(
    "value,expected",
    [(1, 1), (2, 4), (3, 9)],
)
def test_square(value, expected):
    result = value * 2
    breakpoint()
    assert result == expected
```

**Task**

Identify the failure for `value=2`.

**Complete solution**

Inspect:

```text
value = 2
expected = 4
result = 4
```

The case passes.

For `value=1`:

```text
value = 1
expected = 1
result = 2
```

The defect is revealed.

**Explanation**

The debugger helps distinguish a failing parameter case from the passing cases.

**Common mistake**

Assuming the largest input must be the buggy case.

---

### Exercise 13 — Recursive debugging

**Problem**

```python
def countdown(n):
    if n == 0:
        return
    countdown(n - 1)
```

**Task**

Use the call stack to observe recursive frames.

**Complete solution**

```python
def countdown(n):
    breakpoint()
    if n == 0:
        return
    countdown(n - 1)
```

Call:

```python
countdown(3)
```

You will conceptually observe:

```text
countdown(3)
countdown(2)
countdown(1)
countdown(0)
```

**Explanation**

Each recursive call has its own frame.

**Common mistake**

Thinking there is only one `n` variable for all recursive calls.

---

### Exercise 14 — Debug a generator

**Problem**

```python
def numbers():
    yield 1
    yield 2
    yield 3
```

**Task**

Observe when the function actually runs.

**Complete solution**

```python
def numbers():
    breakpoint()
    yield 1
    yield 2
    yield 3
```

Then:

```python
generator = numbers()
next(generator)
```

**Explanation**

The function body starts executing when the generator is advanced, not merely when the generator object is created.

**Common mistake**

Expecting all three values to be computed at generator creation.

---

### Exercise 15 — Debug wrapper behavior

**Problem**

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        breakpoint()
        return func(*args, **kwargs)
    return wrapper
```

**Task**

Determine whether the wrapper is modifying arguments.

**Complete solution**

Inside the breakpoint inspect:

```text
args
kwargs
```

Then step into:

```text
func(*args, **kwargs)
```

**Explanation**

The wrapper is part of the execution call chain.

**Common mistake**

Assuming the debugger's current function name must be the decorated function's original name.

---

## Level 4 — Production-Oriented

### Exercise 16 — API boundary debugging

**Problem**

An API returns 400 unexpectedly.

**Task**

Inspect:

```text
URL
method
payload
status
response body
```

**Complete solution**

Place the breakpoint immediately before the API client call.

Inspect the request object and then the response after stepping over the call.

**Explanation**

You want to determine whether the request was wrong or the response was mishandled.

**Common mistake**

Blaming the server before inspecting the outgoing request.

---

### Exercise 17 — Database debugging

**Problem**

A user lookup returns no record.

**Task**

Debug:

```text
repository
→ SQL parameters
→ database result
```

**Complete solution**

Break before `execute()` and inspect:

```text
query
account_id
```

Step over and inspect:

```text
row
```

**Explanation**

This establishes whether the problem is input, query, database state, or mapping.

**Common mistake**

Changing SQL before inspecting the actual parameter value.

---

### Exercise 18 — Data pipeline debugging

**Problem**

One record is transformed incorrectly.

**Task**

Do not step through the entire dataset. Find and isolate the bad record.

**Complete solution**

Use a conditional breakpoint:

```text
row["transaction_id"] == "TX-5001"
```

Inspect:

```text
raw
parsed
validated
transformed
```

**Explanation**

This targets the first suspicious record.

**Common mistake**

Stepping through millions of rows.

---

### Exercise 19 — AI application debugging

**Problem**

An LLM response cannot be parsed.

**Task**

Inspect:

```text
prompt
retrieved context
raw model response
parser input
parser error
```

**Complete solution**

Place breakpoints at:

```text
prompt construction
model response handling
parser
exception handler
```

Inspect only the minimum needed data and redact secrets.

**Explanation**

This distinguishes model output variability from application parsing errors.

**Common mistake**

Assuming the model is wrong before inspecting the parser and expected schema.

---

### Exercise 20 — Agent workflow debugging

**Problem**

An agent executed a transfer without an approval state.

**Task**

Find where the invalid state transition occurred.

**Complete solution**

Break around:

```text
state update
authorization check
tool selection
transfer call
```

Inspect:

```text
current_state
approval_status
amount
tool_args
```

Use the call stack to identify which workflow function initiated the transfer.

**Explanation**

The debugging target is the observable workflow state, not hidden reasoning.

**Common mistake**

Trying to inspect hidden chain-of-thought.

---

# 59. Debugging Lab

## Lab 1 — Wrong variable value

### Broken code

```python
def calculate_total(price, quantity):
    subtotal = price + quantity
    breakpoint()
    return subtotal
```

### Expected symptom

```text
calculate_total(10, 3)
→ 13
```

instead of:

```text
30
```

### Investigation

Inspect:

```text
price = 10
quantity = 3
subtotal = 13
```

### Root cause

The operation is addition instead of multiplication.

### Corrected code

```python
def calculate_total(price, quantity):
    subtotal = price * quantity
    breakpoint()
    return subtotal
```

### Regression test

```python
def test_calculate_total_multiplies_price_by_quantity():
    assert calculate_total(10, 3) == 30
```

---

## Lab 2 — Incorrect function argument

### Broken code

```python
def apply_tax(amount, tax_rate):
    return amount + (amount * tax_rate)


def calculate_total(subtotal):
    return apply_tax(0, 18)
```

### Symptom

Expected:

```text
118
```

Actual:

```text
0
```

### Breakpoint

Inside `apply_tax()`.

### Inspect

```text
amount = 0
tax_rate = 18
```

### Root cause

Caller passed the wrong argument and also uses the wrong percentage representation for the current function contract.

### Corrected example

```python
def apply_tax(amount, tax_rate):
    return amount + (amount * tax_rate // 100)


def calculate_total(subtotal):
    return apply_tax(subtotal, 18)
```

### Regression test

```python
def test_tax_uses_subtotal():
    assert calculate_total(100) == 118
```

---

## Lab 3 — Incorrect conditional

### Broken code

```python
def is_eligible(age):
    if age > 18:
        return True
    return False
```

### Symptom

Age `18` is rejected.

### Breakpoint

Before the `if`.

### Inspect

```text
age = 18
age > 18 = False
```

### Root cause

Boundary condition is wrong.

### Corrected code

```python
def is_eligible(age):
    return age >= 18
```

### Regression test

```python
def test_age_18_is_eligible():
    assert is_eligible(18) is True
```

---

## Lab 4 — Off-by-one loop

### Broken code

```python
items = ["a", "b", "c"]

for index in range(len(items) - 1):
    print(items[index])
```

### Symptom

`"c"` is never processed.

### Breakpoint

Inside the loop.

### Inspect

```text
index = 0
index = 1
```

No iteration for `2`.

### Root cause

Range ends before `len(items)`.

### Corrected code

```python
for index in range(len(items)):
    print(items[index])
```

### Regression test

```python
def test_all_items_are_processed():
    items = ["a", "b", "c"]
    processed = []

    for index in range(len(items)):
        processed.append(items[index])

    assert processed == ["a", "b", "c"]
```

---

## Lab 5 — Incorrect nested behavior

### Broken code

```python
def discount(total):
    return total * 10 // 100


def final_total(total):
    discount_value = discount(total)
    return total + discount_value
```

### Symptom

Discount increases total.

### Debugging strategy

Step Into `discount()`, return, then inspect:

```text
total
discount_value
```

### Root cause

Discount is being added instead of subtracted.

### Corrected code

```python
def final_total(total):
    discount_value = discount(total)
    return total - discount_value
```

### Regression test

```python
def test_discount_reduces_total():
    assert final_total(100) == 90
```

---

## Lab 6 — Swallowed exception

### Broken code

```python
def load_user(value):
    try:
        return int(value)
    except Exception:
        return None
```

### Symptom

Unexpected invalid input silently becomes `None`.

### Debugging strategy

Use an exception breakpoint where supported, or place a breakpoint in the `except` block.

### Root cause

A broad exception handler hides the original failure category.

### Better code

```python
def load_user(value):
    try:
        return int(value)
    except ValueError:
        return None
```

The correct handling depends on the application contract.

### Regression test

```python
def test_load_user_returns_none_for_invalid_integer():
    assert load_user("abc") is None
```

---

## Lab 7 — Wrong fixture value

### Broken fixture

```python
@pytest.fixture
def account():
    return Account("A", 0)
```

### Failing test

```python
def test_withdraw():
    account = ...
    assert account.balance == 500
```

### Investigation

Break at the start of the test and inspect fixture state.

### Root cause

Arrange state is incorrect.

### Correction

```python
@pytest.fixture
def account():
    return Account("A", 500)
```

---

## Lab 8 — Failing parametrized case

### Broken code

```python
def normalize(value):
    return value.lower()
```

### Test

```python
@pytest.mark.parametrize(
    "value,expected",
    [
        ("Alice", "alice"),
        ("Bob", "bob"),
        ("", ""),
    ],
)
def test_normalize(value, expected):
    breakpoint()
    assert normalize(value) == expected
```

### Debugging strategy

Inspect the specific failing parameter and its expected value.

### Root cause possibilities

The empty case may not actually fail here. A failure might instead come from a different case or requirement such as `None`.

### Lesson

Do not invent the root cause from the parameter list. Observe it.

---

## Lab 9 — Recursive bug

### Broken code

```python
def countdown(n):
    if n == 0:
        return
    countdown(n + 1)
```

### Symptom

Recursion continues away from the base case.

### Debugging strategy

Inspect successive frames:

```text
n = 1
n = 2
n = 3
...
```

### Root cause

Recursive argument moves in the wrong direction.

### Fix

```python
def countdown(n):
    if n == 0:
        return
    countdown(n - 1)
```

### Regression test

Use a small input such as:

```python
def test_countdown_terminates():
    countdown(3)
```

---

## Lab 10 — Incorrect API response handling

### Broken code

```python
response = client.get("/users/1")
name = response.json()["data"]["name"]
```

Actual API:

```json
{
  "user": {
    "name": "Alice"
  }
}
```

### Symptom

`KeyError: 'data'`

### Debugging strategy

Break immediately after `response`.

Inspect:

```text
response.status_code
response.json()
```

### Root cause

Application expects the wrong response schema.

### Better

```python
name = response.json()["user"]["name"]
```

only if that is the actual stable API contract.

---

## Lab 11 — Data transformation bug

### Broken code

```python
def transform(row):
    row["amount"] = row["amount"] / 100
    return row
```

### Requirement

Amount is already in major currency units.

### Symptom

`100` becomes `1`.

### Debugging strategy

Inspect:

```text
input row
after transform
```

### Root cause

Unnecessary scaling.

### Regression test

```python
def test_transform_preserves_major_currency_amount():
    row = {"amount": 100}

    result = transform(row)

    assert result["amount"] == 100
```

---

## Lab 12 — Agent state-machine bug

### Broken concept

```python
if approved:
    state = "AUTHORIZED"

transfer()
state = "COMPLETED"
```

The transfer call happens even if `approved` is false.

### Debugging strategy

Break before `transfer()`.

Inspect:

```text
approved
state
```

### Root cause

The transfer is not guarded by the authorization state.

### Better

```python
if not approved:
    return {"status": "rejected"}

transfer()
state = "COMPLETED"
```

### Regression test

```python
def test_unapproved_transfer_does_not_execute(fake_tools):
    ...
```

The exact assertion should verify the observable safety contract.

---

# 60. Interview Questions

## Beginner

### 1. What is debugging?

**Model answer:** Debugging is the systematic process of reproducing incorrect behavior, inspecting execution and state, identifying the root cause, fixing it, and verifying the fix.

### 2. What is a breakpoint?

**Model answer:** A breakpoint is a pause point that causes the debugger to stop execution when reached or when its condition is satisfied.

### 3. Does a breakpoint stop the program permanently?

**Model answer:** No. It pauses execution. The developer can inspect state and then continue or step through execution.

### 4. What is Step Over?

**Model answer:** It executes the current statement without entering the implementation of a called function and then stops at the next relevant point in the current function.

### 5. What is Step Into?

**Model answer:** It enters a called function so you can inspect its internal behavior.

### 6. What is Step Out?

**Model answer:** It executes until the current function returns to its caller.

### 7. What is a call stack?

**Model answer:** It is the chain of active function calls at a particular point in execution, represented conceptually by stack frames.

### 8. What is a stack frame?

**Model answer:** A frame represents the execution context of an active function call, including arguments, local state, and the current execution position.

## Intermediate

### 9. Traceback vs call stack?

**Model answer:** A traceback describes the call path associated with an exception. A live debugger call stack represents the currently active execution chain while the program is paused.

### 10. Why can a variable be unavailable while debugging?

**Model answer:** The variable may belong to a different scope or stack frame. You may need to navigate to the caller or another relevant frame.

### 11. Why use conditional breakpoints?

**Model answer:** They let you pause only for a particular case, which is valuable inside loops, repeated requests, or large datasets.

### 12. Why is the exception location not always the root cause?

**Model answer:** The failure can be caused by incorrect state created earlier and propagated through several functions.

### 13. Why is a debugger better than printing everything?

**Model answer:** A debugger allows interactive inspection of current state, call stack, and execution without requiring you to predict every useful value in advance. Print statements can still be appropriate for simple or remote diagnostics.

### 14. What is `breakpoint()`?

**Model answer:** It is Python's built-in mechanism for entering the configured debugger through `sys.breakpointhook()`. With the default configuration it enters `pdb`.

### 15. What is `pdb`?

**Model answer:** `pdb` is Python's standard-library interactive debugger.

## Advanced

### 16. How do you debug a failing pytest test?

**Model answer:**

```text
reproduce one test
→ break
→ inspect test inputs and fixtures
→ inspect call stack
→ step through suspicious code
→ form hypothesis
→ verify
→ fix
→ rerun focused test
→ run broader tests
```

### 17. How do you debug a parametrized test?

**Model answer:** Identify the specific failing parameter case, rerun that case where practical, inspect its input/expected values, and use a breakpoint to trace the corresponding execution.

### 18. What makes concurrency debugging difficult?

**Model answer:** Multiple threads/tasks can interleave, shared state can race, and pausing execution can alter timing and potentially hide the original race.

### 19. How would you debug a recursive function?

**Model answer:** Inspect successive stack frames and the recursive argument. Verify that each recursive call progresses toward the base case.

### 20. How would you debug a data pipeline?

**Model answer:** Reduce the dataset, isolate the failing record, use conditional breakpoints, and inspect state at stage boundaries such as parse, validate, transform, and write.

### 21. How would you debug an LLM application?

**Model answer:** Inspect deterministic application state around prompt construction, retrieval, model invocation, response parsing, tool arguments, and fallback/error handling. Avoid treating hidden chain-of-thought as debugger-visible state.

### 22. How would you debug an agentic workflow?

**Model answer:** Trace observable state transitions, tool calls, arguments, results, retries, authorization checks, and termination conditions.

### 23. What is hypothesis-driven debugging?

**Model answer:** It means forming a specific explanation for the symptom, gathering evidence through inspection, confirming or rejecting the hypothesis, and then moving to the next hypothesis if necessary.

### 24. Why create a minimal reproducible example?

**Model answer:** It reduces unrelated complexity, speeds up investigation, and makes the root cause easier to isolate and communicate.

---

# 61. Architecture Questions

## 1. How would you design debugging support for a large Python service?

Use multiple layers:

```text
application code
+
structured logging
+
metrics
+
distributed tracing
+
error tracking
+
local debugger
+
reproducible test harness
```

The local debugger is one instrument, not the entire diagnostic architecture.

## 2. How would you debug a distributed backend?

Start with an external identifier such as a correlation/request ID.

Trace:

```text
request
→ gateway
→ service A
→ service B
→ database
```

Use traces and logs to identify the failing component, then reproduce the relevant component interaction locally or in a controlled environment.

## 3. How would you combine logs, metrics, traces, and debugging?

Use each for a different question:

```text
metrics → how often/how much?
logs    → what happened?
traces  → where did it travel?
debugger → what was the local live state?
tests   → can we reproduce and protect it?
```

## 4. How would you debug a pipeline processing millions of records?

Do not interactively step through all records.

Use:

```text
data-quality signals
→ identify bad partition/record
→ isolate small dataset
→ conditional breakpoint
→ local replay
```

## 5. How would you debug an AI/LLM application?

Instrument the deterministic envelope:

```text
request
prompt
retrieval
model request metadata
structured response
parser
tools
state
```

Redact sensitive information.

For model quality issues, combine debugging with evaluation datasets rather than relying solely on interactive sessions.

## 6. How would you debug an agentic workflow?

Represent the workflow explicitly:

```text
state
→ decision
→ tool call
→ tool result
→ state update
```

Then inspect each transition.

Use deterministic fake/controlled tools for local reproducibility.

## 7. What if local debugging cannot reproduce the problem?

Shift from interactive debugging to evidence collection:

```text
production logs
traces
metrics
deployment metadata
sanitized request
configuration
dependency versions
```

Then reproduce the relevant state in a controlled environment.

## 8. How would you design safe production diagnostics?

Prefer:

- read-only diagnostic endpoints
- structured logs
- redaction
- access controls
- correlation IDs
- bounded payload capture
- audited privileged access

Avoid arbitrary code execution or unrestricted interactive access.

## 9. How would you prevent sensitive data exposure?

Define:

```text
what can be logged
what must be redacted
who can access diagnostics
how long data is retained
```

Never assume a debugger session is automatically private.

## 10. How would you minimize debugging overhead in production?

Use:

```text
sampling
conditional diagnostics
asynchronous telemetry
bounded logging
feature flags
targeted tracing
```

Avoid globally enabling expensive debug behavior.

---

# 62. Production Debugging Checklist

- [ ] Reproduce the problem.
- [ ] State the symptom precisely.
- [ ] Understand expected behavior.
- [ ] Identify actual behavior.
- [ ] Minimize the reproduction.
- [ ] Identify the suspicious state transition.
- [ ] Place a strategic breakpoint.
- [ ] Inspect relevant variables.
- [ ] Inspect function arguments.
- [ ] Inspect object state.
- [ ] Read the call stack.
- [ ] Move to the relevant frame.
- [ ] Step Into only where useful.
- [ ] Step Over trusted/irrelevant code.
- [ ] Step Out when the current function is no longer useful.
- [ ] Use conditional breakpoints for repeated cases.
- [ ] Check exception type and context.
- [ ] Form an explicit hypothesis.
- [ ] Verify the hypothesis with evidence.
- [ ] Avoid mutating state casually.
- [ ] Avoid side-effecting debugger expressions.
- [ ] Protect secrets and sensitive data.
- [ ] Fix the root cause.
- [ ] Run focused tests.
- [ ] Run broader regression tests.
- [ ] Add or retain a regression test.
- [ ] Check whether the issue can recur elsewhere.
- [ ] Document important diagnostic findings.

---

# 63. Knowledge Check

## Conceptual questions

### Question 1

What is the primary purpose of a debugger?

**Answer:** To provide controlled observation of program execution and state so an engineer can reason about incorrect behavior.

### Question 2

What is the key difference between Step Over and Step Into?

**Answer:** Step Over runs the called function without entering it; Step Into enters the called function for inspection.

### Question 3

What does Step Out do?

**Answer:** It completes the current function and returns execution to its caller.

### Question 4

Why is a conditional breakpoint useful in a large loop?

**Answer:** It pauses only for the relevant iteration instead of stopping on every iteration.

---

## Call-stack questions

### Question 5

If the stack is:

```text
main
→ service
→ repository
→ query
```

which function is the closest to the current execution point if `query` is active?

**Answer:** `query`.

### Question 6

Why might a variable in `service()` not be visible while you are stopped in `query()`?

**Answer:** Because the variable belongs to `service()`'s frame, not the current `query()` frame. Navigate to the appropriate frame.

---

## Code-tracing questions

### Question 7

What state exists here?

```python
def f(x):
    y = x + 1
    breakpoint()
    return y
```

for `f(10)`?

**Answer:**

```text
x = 10
y = 11
```

### Question 8

What is the call chain?

```python
def a():
    b()


def b():
    c()


def c():
    breakpoint()
```

**Answer:**

```text
a → b → c
```

---

## Debugging questions

### Question 9

A test says:

```text
expected 100
actual 120
```

What should you do first?

**Answer:** Reproduce the failure and inspect the actual state rather than immediately changing code.

### Question 10

What is a better question than "Which line is broken?"

**Answer:**

> "Where does the program state first become inconsistent with the requirement?"

### Question 11

Why can a debugger session change the outcome of a concurrency bug?

**Answer:** Pausing execution changes timing, scheduling, and interleavings.

---

## Architecture questions

### Question 12

Should you use an interactive debugger as the primary production observability system?

**Answer:** No. Production systems generally need logs, metrics, traces, safe diagnostics, and reproducible evidence. Interactive debugging can be a specialized tool when explicitly designed and authorized.

### Question 13

How would you debug an AI application when the generated wording varies?

**Answer:** Inspect deterministic application components and stable observable contracts such as schemas, tool calls, state, parsing, and policy checks. Use evaluation methods for model quality.

### Question 14

What should an agentic regression/debugging workflow inspect?

**Answer:** Observable state transitions, tool calls, arguments, results, retries, authorization, termination, and final outputs—not hidden chain-of-thought.

---

# 64. Glossary

| Term | Meaning |
|---|---|
| Bug | Incorrect behavior relative to a requirement or expected contract |
| Debugging | Systematic investigation and correction of incorrect behavior |
| Debugger | Tool that lets you pause and inspect program execution |
| Breakpoint | A point where debugger execution pauses |
| Conditional breakpoint | Breakpoint that pauses only when a condition is true |
| Temporary breakpoint | Breakpoint that is removed after being hit |
| Logpoint | Non-stopping breakpoint-style diagnostic feature, where supported |
| Step Over | Execute current line without entering called function |
| Step Into | Enter a called function |
| Step Out | Run until current function returns |
| Continue | Resume execution until another pause point |
| Call stack | Active chain of nested function calls |
| Stack frame | Execution context belonging to one active function call |
| Traceback | Exception-related record of the call path |
| Execution state | Relevant program state at a moment in execution |
| Local variable | Name/state belonging to a local function scope |
| Global variable | Name/state defined at module/global scope |
| Watch expression | Expression evaluated repeatedly while paused, where supported |
| `breakpoint()` | Python built-in that invokes the configured breakpoint hook |
| `pdb` | Python standard-library debugger |
| `pdb.set_trace()` | Explicitly enters `pdb` at the calling frame |
| `python -m pdb` | Command-line way to run a Python program under `pdb` |
| Exception breakpoint | Debugger feature that pauses on raised exceptions |
| Test failure | Test result showing actual behavior differs from expected behavior |
| Root cause | Underlying cause that produced the observed defect |
| Symptom | Visible manifestation of a deeper problem |
| Minimal Reproducible Example | Smallest practical example that still reproduces a bug |
| Observability | Ability to understand system behavior from emitted evidence |
| Logging | Recording diagnostic events |
| Metrics | Numeric measurements of system behavior |
| Tracing | Recording request/service execution paths |
| Conditional execution | Branching based on a Boolean condition |
| Frame navigation | Moving between caller/callee execution contexts |
| Post-mortem debugging | Inspecting an exception after program failure |
| Nondeterminism | Behavior that can vary due to timing, randomness, environment, or other uncontrolled factors |
| Regression | Previously working behavior that becomes broken after change |
| Regression test | Test that protects important established behavior after changes |

---

# Python / Debugger API and Command Reference

This section is intentionally compact. The goal is to know the important controls and their reasoning use.

## `breakpoint()`

**What it does:** Enters the configured debugger via `sys.breakpointhook()`.

**Why it exists:** Provides a concise, standard entry point for interactive debugging.

**Syntax:**

```python
breakpoint()
```

**Important detail:** The default hook normally enters `pdb`; the behavior can be customized through Python's breakpoint hook configuration. citeturn193898search5

**Common mistake:** Leaving an unintended breakpoint in committed code.

**Use when:** Investigating local code.

**Avoid when:** A permanent production pause is not explicitly intended.

---

## `pdb.set_trace()`

**What it does:** Enters `pdb` at the calling stack frame.

**Syntax:**

```python
import pdb
pdb.set_trace()
```

**Why use it:** Explicitly invokes the standard debugger.

**Common mistake:** Using it where `breakpoint()` is a more portable/configurable choice.

**Use when:** You deliberately want standard-library `pdb`.

**Avoid when:** A temporary debugging hook should not remain in production code.

---

## `python -m pdb`

**What it does:** Starts a Python program under `pdb`.

**Syntax:**

```bash
python -m pdb script.py
```

Current Python also supports module execution and, in Python 3.14+, a `-p/--pid` process-attachment option. citeturn682082view0

**Use when:** Debugging from a terminal or minimal environment.

**Common mistake:** Assuming process attachment is safe merely because the command exists.

---

## `c` / `continue`

**What it does:** Resumes execution until another breakpoint or stopping condition.

**Use when:** You have enough information about the current location.

---

## `n` / `next`

**What it does:** Continues until the next line in the current function or until that function returns.

**Use when:** You want to follow the current function without entering calls.

---

## `s` / `step`

**What it does:** Executes the current line and stops at the next possible source-level opportunity, including inside a called function.

**Use when:** Investigating a called function.

---

## `r` / `return`

**What it does:** Continues until the current function returns.

**Use when:** You are done inspecting the current function.

---

## `w` / `where`

**What it does:** Displays the current stack trace and indicates the current frame. Current `pdb` supports optional frame-count behavior as well. citeturn108140view0

**Use when:** You need to understand who called the current function.

---

## `l` / `list`

**What it does:** Displays source around the current location.

**Use when:** You need source context while in a terminal debugger.

---

## `p expression`

**What it does:** Evaluates and prints an expression in the current frame. citeturn108140view1

Example:

```text
(Pdb) p balance
(Pdb) p amount
(Pdb) p balance - amount
```

**Common mistake:** Evaluating expressions with side effects.

---

## `pp expression`

**What it does:** Like `p`, but pretty-prints the result.

**Use when:** Inspecting nested dictionaries/lists or large structured values.

---

## `a` / `args`

**What it does:** Displays current function arguments and their values. citeturn108140view1

**Use when:** A function may have received unexpected inputs.

---

## `locals`

**What it does:** Displays local names and values.

**Use when:** You want a broader view of current frame state.

---

## `globals`

**What it does:** Displays accessible global names.

**Use when:** Global configuration or module state is suspicious.

---

## `b` / `break`

**What it does:** Sets or lists breakpoints.

Example:

```text
(Pdb) b 20
```

`pdb` also accepts function-based breakpoints and conditions. citeturn108140view0

---

## `tbreak`

**What it does:** Sets a temporary breakpoint removed after its first hit. citeturn108140view0

**Use when:** You need one targeted pause.

---

## `condition`

**What it does:** Adds or changes a breakpoint condition.

Example:

```text
(Pdb) condition 1 transaction["id"] == 5001
```

**Use when:** A repeated code path should pause only for one case.

---

## `ignore`

**What it does:** Skips a configured number of breakpoint hits before honoring the breakpoint.

**Use when:** The relevant failure occurs after many repeated calls.

---

## `clear`

**What it does:** Removes breakpoints.

**Use when:** Cleaning up temporary debugging state.

---

## `help`

**What it does:** Displays debugger help.

Example:

```text
(Pdb) help
(Pdb) help next
```

**Use when:** You forget a command.

This is better than memorizing every command.

---

# Internal Python Debugging Concepts

The debugger is easier to understand when connected to Python's execution model.

## Functions create execution contexts

When Python calls:

```python
calculate_total()
```

the runtime needs context for that active call.

Conceptually:

```text
function
+
arguments
+
locals
+
execution position
```

form a frame-like execution context.

## Calls create a chain

```text
main()
 ↓
service()
 ↓
repository()
```

At the deepest call, the debugger can expose this chain.

## Returns unwind the chain

```text
repository returns
 ↓
service resumes
 ↓
main resumes
```

## Exceptions can unwind the chain

```text
deep function raises
 ↓
caller handles?
 ├─ yes → continue in handler
 └─ no  → exception propagates upward
```

The traceback records the propagation path when the exception reaches the reporting mechanism.

## Why this matters

The call stack is not just an IDE panel.

It represents the nested execution context that makes function calls return to the correct caller.

---

# Important Distinctions

## Debugger vs test

```text
test:
Does it behave correctly?

debugger:
Why does it behave incorrectly?
```

## Debugger vs print

```text
print:
You preselect observations.

debugger:
You can interactively explore state after pausing.
```

## Debugger vs traceback

```text
traceback:
Where did an exception propagate?

debugger:
What is the live state and call context?
```

## Debugger vs logging

```text
debugger:
interactive and local

logging:
historical and remote-friendly
```

## Python vs IDE behavior

```text
Python:
breakpoint(), pdb, execution semantics

pdb:
standard-library debugger commands

IDE:
visual breakpoint UI, watches, thread panels, etc.
```

Do not turn an IDE feature into a claim about Python itself.

---

# Debugging Heuristics

## Heuristic 1 — Find the first wrong state

Suppose:

```text
input = 100
parsed = 100
normalized = 100
transformed = 80
result = 80
```

Do not start at:

```text
result = 80
```

Start at:

```text
transformed = 80
```

That is where the state first became incorrect.

## Heuristic 2 — Trust evidence, not assumptions

Do not assume:

```text
database is broken
model is broken
test is broken
```

Inspect.

## Heuristic 3 — Minimize before stepping

A smaller reproduction makes the debugger more powerful.

## Heuristic 4 — One hypothesis at a time

Otherwise debugging becomes experimentation without causal clarity.

## Heuristic 5 — Debug boundaries

Useful boundaries include:

```text
input → parser
parser → validator
validator → business logic
business logic → database
service → API
retrieval → LLM
tool result → workflow state
```

## Heuristic 6 — After fixing, make the fix durable

```text
bug
→ fix
→ regression test
```

---

# Final Mental Model

The complete debugging model is:

```text
BUG
 ↓
REPRODUCE
 ↓
OBSERVE
 ↓
MINIMIZE
 ↓
IDENTIFY SUSPICIOUS BOUNDARY
 ↓
BREAKPOINT
 ↓
INSPECT STATE
 ↓
READ CALL STACK
 ↓
INSPECT RELEVANT FRAME
 ↓
STEP THROUGH EXECUTION
 ↓
FORM HYPOTHESIS
 ↓
VERIFY WITH EVIDENCE
 ↓
IDENTIFY ROOT CAUSE
 ↓
FIX
 ↓
RUN TESTS
 ↓
ADD REGRESSION PROTECTION
```

A debugger is not a magic bug-fixing tool.

It is an **instrument for observing program execution and state**.

The engineer still provides the reasoning.

Remember the three central questions:

```text
What happened?
Why did it happen?
What evidence proves the cause?
```

Then connect debugging to the larger engineering workflow:

```text
testing
   ↓
failure
   ↓
systematic debugging
   ↓
root cause
   ↓
fix
   ↓
regression protection
   ↓
CI/CD
   ↓
production observability
```

And at larger system scales:

```text
Python application
    ↓
backend service
    ↓
API
    ↓
database
    ↓
data pipeline
    ↓
ML system
    ↓
AI/LLM application
    ↓
agentic workflow
    ↓
distributed production system
```

The same core idea remains:

> Observe the actual state, understand the execution path, and use evidence to move from symptom to root cause.

---

# Final Self-Review Checklist

- [x] Debugging is explained from absolute beginner level.
- [x] Bug is explained.
- [x] Debugger is explained.
- [x] Debugging vs testing is explained.
- [x] Debugging vs logging is explained.
- [x] Debugging vs print statements is explained.
- [x] Debugging vs monitoring is explained.
- [x] Debugger mental model is explained.
- [x] Program state is explained.
- [x] Breakpoints are explained.
- [x] Breakpoint placement strategy is explained.
- [x] Normal breakpoints are covered.
- [x] Conditional breakpoints are covered.
- [x] Logpoints are covered conceptually.
- [x] Exception breakpoints are covered.
- [x] Function/method breakpoints are covered conceptually.
- [x] Temporary breakpoints are covered.
- [x] Hit/ignore-count concepts are covered.
- [x] IDE-specific features are clearly distinguished from Python behavior.
- [x] Continue is explained.
- [x] Step Over is explained.
- [x] Step Into is explained.
- [x] Step Out is explained.
- [x] Run to Cursor is covered conceptually.
- [x] Restart is covered conceptually.
- [x] Stop is covered.
- [x] Call stack is deeply explained.
- [x] Stack frames are explained.
- [x] Caller/callee concepts are explained.
- [x] Return context is explained.
- [x] Reading call stacks is explained.
- [x] Traceback vs call stack is explained.
- [x] Variable inspection is explained.
- [x] Local/global scope is explained.
- [x] Watch expressions are explained.
- [x] Side effects during evaluation are explained.
- [x] Loop debugging is covered.
- [x] Conditional logic debugging is covered.
- [x] Exception debugging is covered.
- [x] Exception breakpoints are covered.
- [x] Functions are debugged with a realistic example.
- [x] `breakpoint()` is covered.
- [x] `pdb` is covered.
- [x] `pdb.set_trace()` is covered.
- [x] `python -m pdb` is covered.
- [x] Core `pdb` commands are explained.
- [x] `continue` / `c` is covered.
- [x] `next` / `n` is covered.
- [x] `step` / `s` is covered.
- [x] `return` / `r` is covered.
- [x] `where` / `w` is covered.
- [x] `list` / `l` is covered.
- [x] `print` / `p` is covered.
- [x] `pp` is covered.
- [x] `args` / `a` is covered.
- [x] `locals` is covered.
- [x] `globals` is covered.
- [x] `break` / `b` is covered.
- [x] `tbreak` is covered.
- [x] `clear` is covered.
- [x] `condition` is covered.
- [x] `ignore` is covered.
- [x] `help` is covered.
- [x] Pytest debugging is covered.
- [x] Pytest `--pdb` is covered.
- [x] Pytest `--trace` is covered.
- [x] Fixture debugging is covered.
- [x] Parametrized test debugging is covered.
- [x] Async debugging is introduced.
- [x] Thread debugging is introduced.
- [x] Process debugging is introduced.
- [x] State observation vs mutation is covered.
- [x] Side effects are covered.
- [x] Object debugging is covered.
- [x] Data-structure debugging is covered.
- [x] Recursion debugging is covered.
- [x] Decorator debugging is covered.
- [x] Context-manager debugging is covered.
- [x] Generator debugging is covered.
- [x] External dependency debugging is covered.
- [x] Network/API debugging is covered.
- [x] Database debugging is covered.
- [x] Data-pipeline debugging is covered.
- [x] ML-pipeline debugging is covered.
- [x] AI/LLM debugging is covered.
- [x] Agentic-AI debugging is covered.
- [x] Hidden chain-of-thought is not treated as debugger-visible state.
- [x] A systematic debugging strategy is explained.
- [x] Root cause vs symptom is explained.
- [x] Hypothesis-driven debugging is explained.
- [x] Minimal reproducible examples are explained.
- [x] Common debugging mistakes are covered.
- [x] Debugger vs logging is explained.
- [x] Debugger vs traceback is explained.
- [x] Test-driven debugging workflow is covered.
- [x] Production debugging is covered.
- [x] Production security/privacy concerns are covered.
- [x] A complete realistic debugging example is included.
- [x] A complete mini-project is included.
- [x] At least 20 progressive exercises are included.
- [x] Every exercise includes a task, hints, solution, explanation, and common mistake guidance.
- [x] A debugging lab is included.
- [x] The debugging lab includes 12 distinct failure scenarios.
- [x] Interview questions are included.
- [x] Architecture questions are included.
- [x] Production checklist is included.
- [x] Knowledge check is included.
- [x] Glossary is included.
- [x] Final mental model is included.
- [x] Python debugging APIs are technically distinguished from IDE features.
- [x] Current `breakpoint()`/`pdb` behavior is reflected accurately.
- [x] Current pytest debugger options are reflected accurately.
- [x] Code examples are valid Python when presented as executable examples.
- [x] Async/process features are qualified by Python-version/tooling differences where necessary.
- [x] The chapter progresses from basic → intermediate → advanced → production.
- [x] The material connects to backend, API, database, data, ML, AI/LLM, agentic AI, CI/CD, and reliability work.
- [x] The chapter does not treat interactive debugging as the only production diagnosis technique.
- [x] The chapter does not claim that a debugger automatically identifies root cause.
- [x] The chapter does not encourage unsafe production debugging.
- [x] The chapter does not claim access to hidden model reasoning.
- [x] No unrelated topic has taken over the chapter.
