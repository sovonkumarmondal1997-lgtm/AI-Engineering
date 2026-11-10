# Debuggers, Breakpoints, and Call Stacks — Complete Study Guide

**Stage 1 — Programming & Computational Thinking**  
**Module 07 — Testing and Systematic Debugging**  
**Lesson 05**

This guide follows the attached lesson `05-debuggers-breakpoints-and-call-stacks(1).md`. Part A teaches the concepts and examples in beginner-friendly language. Part B assesses the roadmap and current level. Part C solves all 20 coding exercises with explanations. Part D covers all 12 debugging labs, followed by interview, architecture, checklist, and knowledge-check material.

---

# Part A — Complete Lesson Summary and Teaching Notes

## 1. What debugging is and why it matters

A **bug** is behavior that is incorrect compared with the requirement or expected contract. **Debugging** is the systematic process of reproducing that behavior, observing program execution, finding the cause, fixing it, and verifying the correction.

Testing and debugging answer different questions:

| Activity | Main question |
|---|---|
| Testing | Does behavior match the expectation? |
| Debugging | Why does behavior differ? |
| Logging | What information did the program record? |
| Monitoring | Is the system healthy over time? |
| Tracing | How did a request travel across components? |

The normal engineering loop is:

```text
test failure → debugging → root cause → fix → regression test
```

A test can report `expected = 100, actual = 80`, but it may not tell you where 80 first appeared, which input caused it, which function changed the value, or which dependency supplied the wrong state. A debugger lets you inspect execution and state at selected moments.

Example:

```python
def calculate_total(price: int, quantity: int) -> int:
    return price * quantity

def main() -> None:
    print(calculate_total(10, 3))

if __name__ == "__main__":
    main()
```

If the output is unexpectedly 20, pause before the calculation and inspect `price` and `quantity`. Perhaps the multiplication is correct but the caller passed quantity 2. Do not change correct arithmetic to compensate for incorrect input.

A good debugging loop is:

```text
observe → reproduce → isolate → inspect → hypothesize
→ verify → fix → retest
```

Common mistakes are guessing before reproducing, changing several things simultaneously, fixing only the symptom, and assuming the exception line must be the origin of the bad state.

## 2. Why a debugger instead of only `print()`

`print()` debugging is useful and not inherently wrong:

```python
def calculate_total(price, quantity, discount):
    print("price =", price)
    print("quantity =", quantity)
    print("discount =", discount)
    subtotal = price * quantity
    return subtotal - discount
```

It is appropriate for a small, easy-to-reproduce issue, one quick observation, or an environment without an interactive debugger.

A debugger adds controlled pause-and-inspect capabilities. It can expose the current source line, function arguments, local variables, objects, call stack, execution position, and exception context. You can navigate between active frames and inspect state without predicting every value that should be printed.

Print debugging can become noisy, require repeated edits, be difficult across nested calls, and interleave confusingly in concurrent programs. A debugger is not automatically better in every situation; choose the instrument that answers the question with the least risk.

## 3. The debugger mental model

Think of a debugger as an execution observer:

```text
program executes → reaches pause point → pauses
→ debugger exposes state → inspect → step or continue
→ program executes again
```

At one moment, program state includes the current source location, function, arguments, local variables, accessible globals, object attributes, pending exception, and call stack.

A debugger is like pausing a movie: you can inspect the current frame, advance one step, inspect again, or resume. It does not identify the root cause automatically. It supplies evidence; the engineer compares **expected state** with **actual state** and reasons about the difference.

## 4. Breakpoints

A **breakpoint** tells a debugger to pause when execution reaches a particular location or satisfies a condition.

IDE example: click beside a source line. Python example:

```python
def calculate_total(price, quantity):
    subtotal = price * quantity
    breakpoint()
    return subtotal
```

Execution pauses after `subtotal` is calculated and before it is returned. It does not stop permanently; you can inspect and resume.

Place breakpoints strategically: identify the suspicious behavior, find the state transition, then pause immediately before or during it. Avoid placing breakpoints randomly everywhere, too late after bad state has propagated, or too early where they expose irrelevant work.

Do not casually attach an interactive debugger to production. Pausing can affect latency, locks, timeouts, throughput, and state.

## 5. Types of breakpoints and tool boundaries

Debugger features differ by IDE and environment. Distinguish Python language behavior, `pdb` commands, and IDE-specific UI.

- **Normal line breakpoint:** pause at a source line.
- **Conditional breakpoint:** pause only when a Boolean condition is true.
- **Logpoint:** record information without pausing, where supported.
- **Exception breakpoint:** pause when an exception is raised, where supported.
- **Function/method breakpoint:** pause when a function or method is reached.
- **Temporary breakpoint:** pause once, then remove itself; `pdb` has `tbreak`.
- **Hit/ignore count:** pause only after a number of hits; `pdb` has `ignore`.

A conditional breakpoint inside a loop can target one record:

```text
transaction["id"] == 5001
```

In `pdb`, a line breakpoint can be conditional, for example:

```text
(Pdb) b 12, transaction["id"] == 5001
```

Keep conditions simple, side-effect-free, and tied to the suspicious case. A condition that refers to a variable unavailable in the current frame or calls a mutating function can create confusion. Conditional breakpoints still have runtime impact.

## 6. Execution controls: Continue, Step Over, Step Into, Step Out

| Control | Meaning | Use it when |
|---|---|---|
| Continue | Resume until another breakpoint, exception, or program end | You have enough information about intervening lines |
| Step Over | Execute the current line without entering called functions | The called function is not the current investigation target |
| Step Into | Enter a called function | Its internal behavior is suspicious |
| Step Out | Finish the current function and return to its caller | You have learned enough inside the current function |
| Run to Cursor | Continue until a selected source line, where supported | You want to reach a later point without adding a permanent breakpoint |
| Restart | Start the debugged program again | You need a clean reproduction |
| Stop | End debugging/program execution | The session is no longer useful |

Example:

```python
def double(value):
    return value * 2

def main():
    result = double(10)
    print(result)
```

At `result = double(10)`, Step Over runs `double()` and returns to `main()`. Step Into enters `double()`. Step Out runs the rest of the current function and returns to the caller. Use stepping to answer a specific question; do not step every line just because the tool allows it.

## 7. Call stack and stack frames

The **call stack** is the chain of active function calls at the current execution point. If `main()` calls `service()`, which calls `repository()`, which calls `query()`, the conceptual stack is:

```text
main → service → repository → query
```

The currently active function is closest to the execution point. The call stack helps answer: who called this function, why is it running, and which caller supplied the current arguments?

A **stack frame** is the execution context for one active function call. It contains that call's arguments, local variables, current execution position, and links to its caller. Each function invocation has its own frame. Recursive calls therefore have separate local variables even when they use the same variable name.

A variable may be unavailable because it belongs to a different frame. Move to the caller's frame to inspect it. Do not assume there is one global local-variable namespace.

## 8. Reading a call stack and traceback

A **traceback** is a record of the call path associated with an exception. A **live call stack** is the active function-call chain while execution is paused.

A traceback answers, “How did execution reach the exception?” A live stack lets you inspect current frames and state before or during execution. They are related but not identical.

The line that raises an exception is not always where the incorrect state originated. A value may have been malformed much earlier and passed through several functions. Trace the value backward to the earliest point where it differs from the requirement.

## 9. Variables, watches, scope, and safe inspection

When paused, inspect rather than guess.

- **Arguments:** values passed into the current function.
- **Local variables:** names local to the current frame.
- **Globals:** names accessible from module/global scope.
- **Objects:** attributes and internal state.
- **Collections:** lengths, selected keys, selected elements, and nested fields.
- **Watch expressions:** expressions evaluated while paused, often repeatedly as execution stops.

Useful expressions include:

```python
type(value)
len(items)
items[:5]
payload.keys()
payload.get("status")
"abc" in ids
```

For objects:

```python
type(user)
vars(user)       # when the object has an instance __dict__
user.__dict__    # when available
repr(user)
```

`vars()` and `__dict__` are not guaranteed for every object; classes using `__slots__` and extension types may behave differently. A useful `__repr__` makes object state easier to understand.

Python scope matters: a local variable in `service()` may not be visible in the currently selected `query()` frame. Select the correct frame rather than assuming the variable disappeared.

A watch expression can execute code. In `pdb`, expressions can be evaluated in the current frame. Assignments and mutating calls can change program state. Prefer passive inspection first. Calling `order.total()` repeatedly may perform I/O or mutate state if the method is not pure. Do not use debugger commands to print credentials, dump secrets, issue payments, delete data, or otherwise exercise privileges accidentally.

First observe original state; then form a hypothesis; only then run a clearly controlled experiment that intentionally changes state. Record that the state was modified.

## 10. Debugging loops and conditional logic

Loops may run hundreds or millions of times. A conditional breakpoint can target the suspicious iteration rather than stopping on every item.

For a loop, inspect the current index, item, accumulator, and loop condition. For conditional logic, inspect the actual operands and evaluate the condition itself:

```python
def approve(balance, amount):
    if balance >= amount:
        return True
    return False
```

For `approve(99, 100)`, inspect `balance`, `amount`, and `balance >= amount`. The result is correctly `False`; do not change the comparison without checking the inputs and requirement.

## 11. Debugging exceptions and exception breakpoints

When an exception occurs, inspect:
- exception type and message;
- the input that triggered it;
- current and caller frames;
- local variables;
- whether the exception was caught, transformed, or swallowed;
- whether state changed before failure.

An exception breakpoint asks the debugger to pause when an exception is raised. It can stop closer to the original raise site, including exceptions later caught by application code, depending on debugger support and configuration.

Example:

```python
def parse(value):
    return int(value)

result = parse("10O")
```

Inspect `value`: the final character is letter `O`, not digit `0`. Confirm the input before changing the parser.

## 12. Debugging functions and nested calls

Follow the data through function boundaries. For a discount function, inspect subtotal before the call, arguments passed into it, intermediate discount, returned value, and final total. If a final result is wrong, find the earliest incorrect intermediate value rather than staring only at the final output.

A function may be correct while its caller passes the wrong argument. Always inspect both sides of a call.

## 13. Python `breakpoint()`

`breakpoint()` is Python's built-in request to enter the configured debugger. It was introduced in Python 3.7 and delegates through `sys.breakpointhook()`; with the default configuration it enters `pdb`.

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

When execution reaches the call, the debugger opens. The `PYTHONBREAKPOINT` environment variable and `sys.breakpointhook()` allow the behavior to be configured or disabled.

Before committing, search for temporary breakpoints:

```bash
grep -R "breakpoint()" .
```

Use `breakpoint()` for local investigation and small reproductions. Do not leave accidental interactive pauses in production paths.

## 14. Python `pdb` and `pdb.set_trace()`

`pdb` is Python's standard-library interactive source debugger. It supports breakpoints, stepping, stack-frame inspection, source listing, expression evaluation, post-mortem debugging, and programmatic debugging.

Two common entry points:

```python
breakpoint()
```

and:

```python
import pdb
pdb.set_trace()
```

`breakpoint()` uses the configured hook; `pdb.set_trace()` explicitly enters `pdb`. Understanding `pdb` is useful even when using an IDE because it works in terminals, SSH sessions, minimal containers, and remote Linux environments.

Core commands:

| Command | Meaning |
|---|---|
| `n` / `next` | Step over |
| `s` / `step` | Step into |
| `c` / `continue` | Continue |
| `p expression` | Print/evaluate an expression |
| `w` / `where` | Show stack |
| `l` / `list` | Show source |
| `q` / `quit` | Quit debugger |
| `b` | Set breakpoint |
| `tbreak` | Temporary breakpoint |
| `condition` | Set breakpoint condition |
| `ignore` | Ignore a number of breakpoint hits |
| `h` / `help` | Help |

A command is useful only when it supports a clear inspection question.

## 15. Command-line debugging

Start a script under `pdb`:

```bash
python -m pdb script.py
```

The source also covers module execution:

```bash
python -m pdb -m package.module
```

and process attachment in Python 3.14+ on supported systems:

```bash
python -m pdb -p 1234
```

Process attachment has operating-system and process-state constraints; it is not a universal or automatically safe production technique.

A simple `pdb` session might be:

```text
(Pdb) n
(Pdb) p a
(Pdb) p b
(Pdb) n
(Pdb) p result
(Pdb) c
```

## 16. Debugging pytest tests

A failing pytest test provides a reproducible entry point. First run only the failing test:

```bash
pytest tests/test_orders.py::test_total -q
```

Useful options:

```bash
pytest --pdb
pytest --trace
```

`--pdb` enters the debugger on errors or `KeyboardInterrupt`; `--trace` enters the debugger at the start of each test. `--full-trace` retains full tracebacks; `--pdbcls` selects a custom debugger class.

An inline breakpoint also works:

```python
def test_total(cart):
    result = cart.total()
    breakpoint()
    assert result == 100
```

Inspect Arrange state before changing application code. A fixture may be wrong. A parametrized case may contain an incorrect expected value. Focused execution reduces noise.

## 17. Debugging fixtures and parametrized tests

Fixtures are part of the execution path:

```text
test → fixture resolution → fixture setup → application code
```

If a test expects balance 500 but the fixture returns balance 0, the problem is in setup, not the business logic. At the start of the test inspect the fixture object and its attributes.

For parametrized tests, identify the exact failing parameter ID, rerun that case where practical, and inspect input, expected value, and actual result. Do not assume the largest value is the defect; test data can also be wrong.

## 18. Async Python debugging

`async def` defines a coroutine function; `await` suspends the current coroutine until an awaited operation completes; a coroutine represents resumable async computation; an event loop schedules and drives tasks.

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

Inspect `result`, the current coroutine/task, and call context. Async code may suspend and resume while other tasks make progress, so there may be multiple interleaved execution paths rather than one simple global timeline. IDE support differs. Python 3.14 adds `pdb.set_trace_async()` for use inside async functions; do not assume it exists in older versions.

## 19. Threads and processes

A **thread** is an execution path within a process. Threads share process memory and may race over shared state. A debugger may expose multiple thread stacks. Pausing one thread changes scheduling and can hide or alter a race.

A **process** has its own address space and operating-system resources. Multiple processes communicate through IPC or other mechanisms. Multiprocess debugging is harder because each process has independent state and lifecycle. Use logs, metrics, traces, safe diagnostics, and controlled reproductions before attempting live attachment.

Combine debugger, logs, deterministic reproduction, and tests for concurrency issues. Interactive pauses can significantly change timing.

## 20. Debugging state and side effects

First observe, do not mutate. Changing `balance` from 500 to 1000 inside a debugger changes the evidence and may change program behavior. If a controlled experiment requires mutation, record the original state and clearly distinguish the modified run from the original reproduction.

Side effects include database writes, API calls, file changes, cache mutations, object mutations, and event publication. A debugger expression is executable code, not necessarily a passive read. Avoid repeated calls to functions with unknown side effects. Protect credentials and sensitive information; a debugger operates with the program's authority.

## 21. Debugging objects and data structures

Useful object inspection:

```python
type(value)
vars(value)
value.__dict__
repr(value)
```

Use only when supported by the object's type. A good `__repr__` helps reveal state. For collections, inspect focused slices or keys rather than dumping enormous values:

```python
len(items)
items[:5]
payload.keys()
payload.get("status")
len(ids)
"abc" in ids
row[0]
payload["user"]["account"]["balance"]
```

This is controlled observation, not a requirement to print every object in full.

## 22. Debugging recursion

Each recursive call creates a new frame. For:

```python
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

`factorial(4)` creates frames for `n=4, 3, 2, 1`. Inspect successive `n` values and ask whether each call moves toward the base case.

Common defects: incorrect base case, recursive call that does not change the argument, or a step that moves away from termination.

## 23. Debugging decorators

A decorator often creates a wrapper:

```python
def log_call(func):
    def wrapper(*args, **kwargs):
        print("calling")
        return func(*args, **kwargs)
    return wrapper
```

The call path is `calculate() → wrapper() → original calculate()`. Inspect whether the wrapper changes arguments, catches exceptions, changes the return value, or fails to call the original function.

Use `functools.wraps` to preserve metadata and improve introspection:

```python
from functools import wraps

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

This does not remove wrapper execution; it improves metadata and debugging context.

## 24. Debugging context managers

A context manager's lifecycle is conceptually:

```text
__enter__() → body → __exit__()
```

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

Set breakpoints in `__enter__`, the body, and `__exit__` when setup, cleanup, or exception suppression is suspicious.

## 25. Debugging generators

A generator function uses `yield`. Calling it creates a generator object; its body executes as values are requested, not all at creation time. Debugging should inspect when iteration begins, each yield point, current local state, and when iteration completes. Do not assume all values are computed when the generator is created.

## 26. External dependencies, network/API, and database debugging

External dependencies include databases, HTTP APIs, filesystems, queues, and third-party services. Separate the application's request, dependency response, and mapping/handling logic.

For an API, inspect:

```text
URL → method → payload → status → response body
```

Check the outgoing request before blaming the server. Redact credentials and sensitive payloads.

For a database, inspect:

```text
repository → SQL query → parameters → database result → row mapping
```

Break before `execute()`, inspect query and parameters, step over, then inspect the returned row. A missing result alone does not prove whether the SQL, parameter, database state, or mapping is wrong.

## 27. Debugging data pipelines

A pipeline may look like:

```text
read → parse → validate → transform → aggregate → write
```

Find the bad record or partition, then inspect each stage boundary: raw, parsed, validated, transformed, and written. Use data-quality signals to identify the affected partition, isolate a small dataset, and use a conditional breakpoint. Do not step through millions of records.

## 28. Debugging ML pipelines

An ML pipeline may include data loading, preprocessing, feature construction, model inference, and postprocessing. Inspect shape, schema, feature ordering, nulls, transformations, model input, and output. Separate software defects (wrong feature, shape, preprocessing, or serving contract) from model quality decline, which needs evaluation against appropriate datasets and metrics.

## 29. Debugging AI/LLM applications

A useful application pipeline is:

```text
request → prompt construction → retrieval → model call
→ raw response → parsing/validation → tools → application state
```

Inspect prompt/template, retrieved context, model request metadata, structured response, parser input/error, tool arguments/results, configuration, and fallback handling. Redact sensitive information. Do not assume the model is wrong before checking the application parser and expected schema. Do not treat hidden chain-of-thought as debugger-visible state.

## 30. Debugging agentic AI systems

Represent observable workflow:

```text
user request → state → decision → tool call
→ tool result → state update → final response
```

Inspect state transitions, authorization, tool selection, arguments, results, retries, and termination. If approval is false, the transfer tool must not execute. Use controlled/fake tools for reproducibility. Inspect observable application decisions, not hidden reasoning.

## 31. Systematic debugging strategy

Use a repeatable sequence:

1. State the symptom precisely, e.g. “Expected 300, got 350 when quantity is 3.”
2. Reproduce it.
3. Minimize the reproduction: large application → small feature → one request → one input.
4. Identify the failing boundary: input/parser, parser/validator, validator/business logic, business/database, service/API, retrieval/LLM, or tool result/workflow state.
5. Place a strategic breakpoint near the transition.
6. Inspect inputs, outputs, objects, return values, and conditions.
7. Read the call stack: who called this function and why?
8. Step selectively (`next`, `step`, `continue`).
9. Form a specific hypothesis, such as “discount is applied twice.”
10. Verify by inspecting values before and after the relevant call.
11. Fix the root cause.
12. Run the focused test, then broader tests.
13. Add or retain regression protection.

## 32. Root cause vs symptom

A symptom is the visible failure, such as wrong total or `KeyError`. The root cause is the underlying reason, such as a wrong argument, incorrect transformation, stale schema, or missing authorization guard.

The earliest incorrect state is often more informative than the final symptom. Trace data backward through transformations and call boundaries until you find where it first diverged from the requirement.

## 33. Hypothesis-driven debugging

Randomly clicking and changing values is inefficient. Form one specific hypothesis, identify what evidence would support or reject it, inspect that evidence, then revise the hypothesis. Change one variable at a time. A debugger supplies evidence; the hypothesis guides what to inspect.

## 34. Minimal Reproducible Example (MRE)

An MRE is the smallest program and input that still reproduces the defect. Remove unrelated services, data, configuration, and steps while preserving the failure. It speeds investigation, makes communication clearer, and helps separate application defects from environment or dependency issues.

## 35. Common debugging mistakes

The source warns against: printing everywhere; stepping randomly; changing multiple things at once; assuming the first suspicious line is the root cause; ignoring input/fixture state; inspecting the wrong frame; mutating state casually; evaluating expressions with side effects; dumping huge collections; blaming an external dependency before inspecting requests/parameters; trying to debug millions of rows interactively; ignoring concurrency timing; inspecting sensitive information; and fixing a symptom without regression protection.

## 36. Debugger vs logging vs traceback

- **Debugger:** interactive local investigation of live state and execution.
- **Logging:** durable records of events and diagnostic context.
- **Traceback:** exception-associated call path.
- **Metrics:** quantitative health signals over time.
- **Distributed tracing:** request path across services.
- **Tests:** repeatable checks that detect and protect behavior.

A strong system uses these instruments together, not as substitutes.

## 37. Debugging and test-driven workflow

```text
test fails → reproduce one test → inspect Arrange/fixtures
→ breakpoint → inspect call stack and state → hypothesis
→ verify → fix → rerun focused test → run broader suite
→ add regression test
```

A good test gives a stable reproduction; the debugger explains why it fails. After a fix, keep a test that prevents recurrence.

## 38. Production debugging and safety

Local interactive debugging is usually safer. Production systems should primarily rely on structured logs, metrics, traces, correlation IDs, error tracking, sanitized reproducible inputs, and safe diagnostic endpoints.

Do not treat attaching a debugger to production as routine. Pausing can change timing and affect locks, throughput, and availability. Prefer read-only diagnostics, redaction, access controls, bounded payload capture, audited privileged access, and documented retention. Avoid arbitrary code execution or unrestricted interactive access. Minimize overhead with sampling, conditional diagnostics, asynchronous telemetry, bounded logging, feature flags, and targeted tracing.

## 39. Complete realistic bank-transfer example

Requirements:
1. Amount must be positive.
2. Sender has sufficient balance.
3. Transfer decreases sender balance.
4. Transfer increases receiver balance.
5. Rejected transaction does not mutate balances.

```python
class Account:
    def __init__(self, account_id: str, balance: int):
        self.account_id = account_id
        self.balance = balance

def validate_transfer(sender, receiver, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > sender.balance:
        raise ValueError("insufficient balance")
    if sender.account_id == receiver.account_id:
        raise ValueError("accounts must differ")

def execute_transfer(sender, receiver, amount):
    validate_transfer(sender, receiver, amount)
    sender.balance -= amount
    receiver.balance += amount

def transfer_service(sender, receiver, amount):
    execute_transfer(sender, receiver, amount)
    return {
        "status": "success",
        "sender_balance": sender.balance,
        "receiver_balance": receiver.balance,
    }
```

The source's first debugging scenario expects sender 700 and receiver 800 after transferring 300. But its test arranged receiver balance as 200, so the correct result is 500. The production implementation is correct; the test expectation is wrong. Inspect Arrange state before changing application code.

A second defect changes `amount <= 0` to `amount < 0`, allowing zero. A regression test should assert that a zero transfer raises `ValueError("amount must be positive")`. The test protects the business contract.

## 40. Complete order-processing mini-project

Flow:

```text
Order → calculate_subtotal → apply_discount
→ calculate_tax → final_total
```

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

Deliberate defect: calculate tax from `subtotal` instead of `discounted`. For items `(100, 2)` and `(50, 1)`, subtotal is 250. With 10% discount, discounted amount is 225. With 20% tax, tax is 45 and final total is 270. The buggy code calculates tax on 250, producing 50 and an incorrect total of 275.

Debug at `calculate_total`, inspect subtotal, Step Into `apply_discount`, inspect discounted, then inspect the argument passed to `calculate_tax`. Correct it to `calculate_tax(discounted, tax_percent)` and keep a regression test expecting 270. Add boundary tests for discount percentages 0 and 100.

## 41. Python / debugger command reference

- `breakpoint()` — enter the configured debugger.
- `pdb.set_trace()` — explicitly enter `pdb`.
- `python -m pdb script.py` — run a script under `pdb`.
- `python -m pdb -m package.module` — run a module under `pdb`.
- `python -m pdb -p PID` — process attach in Python 3.14+ on supported systems.
- `n` — next/Step Over.
- `s` — step/Step Into.
- `c` — continue.
- `p expression` — inspect expression.
- `w` — show stack.
- `l` — list source.
- `q` — quit.
- `b` — set breakpoint.
- `tbreak` — temporary breakpoint.
- `condition` — breakpoint condition.
- `ignore` — ignore breakpoint hits.
- `h` — help.
- `pytest --pdb` — enter debugger on test error.
- `pytest --trace` — enter debugger at test start.
- `pytest --full-trace` — show full traceback.
- `pytest --pdbcls` — choose custom debugger class.

Tool support and some commands vary by Python and debugger version; verify the environment before relying on version-specific capabilities.

## 42. Final mental model

```text
bug → reproduce → observe → minimize
→ identify suspicious boundary → breakpoint
→ inspect state → read call stack → inspect frame
→ step → hypothesis → verify with evidence
→ root cause → fix → run tests → regression protection
```

A debugger is an instrument for observing execution and state, not a magic bug-fixing tool. The engineer still has to answer: **What happened? Why did it happen? What evidence proves the cause?**

---

# Part B — Roadmap and Current-Level Assessment

## 1. Position in the project tree

The attached lesson belongs to:

`Stage 1 — Programming & Computational Thinking / 07-Testing-and-Systematic-Debugging / 05-debuggers-breakpoints-and-call-stacks.md`

Module 07 sequence:

1. Test Levels: Unit, Integration, and End-to-End — completed.
2. Pytest: Assertions, Fixtures, and Parametrization — completed.
3. Arrange–Act–Assert and Test Design — completed.
4. Boundary, Invalid, and Regression Tests — completed.
5. Debuggers, Breakpoints, and Call Stacks — current lesson.
6. Tracebacks, Logging, and Minimal Reproductions — not started.
7. Mocking and Test Doubles — not started.
8. Module README and practice questions.

The wider Stage 1 tree contains 24 modules, progressing from computational thinking and Python fundamentals through control flow/functions, collections and algorithms, files/structured data/CLI, modules/packages/dependencies/code quality, testing/debugging, OOP/data modelling, advanced Python, standard library, binary/text processing, modern Python, advanced testing, performance, packaging, internals, design patterns, visualization, security, code reading/refactoring/review, and gap lessons.

## 2. Relevant Stage 1 projects

The Stage 1 overview includes four cumulative projects:

1. Personal Expense Ledger CLI.
2. Log Investigation and Reliability CLI.
3. Data Quality and Transformation Pipeline — `orders.csv`, a `dqpipe` package (`cli.py`, `config.py`, `pipeline.py`, `rules.py`), tests, configuration, and data contract.
4. Rule-Based Risk Review Engine — `transactions.csv`, `rules.toml`, a `riskreview` package (`cli.py`, `engine.py`, `io.py`, `models.py`, `rules.py`), tests, and golden decision data.

These projects make debugging relevant: inspect CLI inputs, parsing, validation, transformations, file/database boundaries, configuration, and expected outputs. The data pipeline and risk engine especially benefit from stage-by-stage state inspection and regression tests.

## 3. Current learning level and scope

You have completed Python fundamentals, control flow and functions, collections and problem-solving, file handling, pathlib, CSV/JSON, encodings, CLI, streams/exit codes, logging, environment configuration, imports/packages, `pyproject.toml`/`uv`, dependency management, Ruff, type hints, documentation, and Module 07 Lessons 01–04.

Your current level is beginner progressing toward intermediate Python engineering. This lesson is appropriate because it uses concepts already learned: functions, arguments, return values, loops, conditionals, exceptions, classes/objects, pytest tests, fixtures, and parametrization.

The examples introduce debugging tools and the call-stack mental model, but do not require operating-system internals. Async, threads, processes, external dependencies, and production diagnostics are introduced conceptually; they are not prerequisites to master before completing the basic debugger exercises.

**Learning status:** Lesson 05 is the current lesson. Lesson 06 has not been started. This guide does not move you into the next lesson.

---

# Part C — All 20 Coding Exercises with Step-by-Step Explanations

## Level 1 — Basic

### Exercise 1 — First breakpoint

```python
def add(a, b):
    result = a + b
    breakpoint()
    return result
```

- `add` receives two arguments.
- `result` stores their sum.
- `breakpoint()` pauses after calculation.
- Inspect with `p result`.
- `return` sends the value back after continuing.

Place it before `return`; a line after `return` is unreachable.

### Exercise 2 — Step Over

```python
def main():
    breakpoint()
    result = double(10)
    print(result)
```

Pause before the call, then use Step Over or `n`. The debugger executes `double(10)` and returns to `main`; you do not enter the function body.

### Exercise 3 — Step Into

At the same breakpoint before `double(10)`, use Step Into or `s`. The debugger enters `double()` so you can inspect its argument and return calculation. Step Into differs from Step Over because it enters the called function.

### Exercise 4 — Inspect a local variable

```python
def calculate(price, quantity):
    subtotal = price * quantity
    breakpoint()
    return subtotal
```

At the pause, run `p price`, `p quantity`, and `p subtotal`. All three belong to the current `calculate` frame. They may no longer be available after stepping out of that frame.

### Exercise 5 — Read a call stack

```python
def a():
    b()

def b():
    c()

def c():
    breakpoint()
```

Inside `c`, use `w`. The active call chain is `a → b → c`; `c` is the current frame, with `b` and `a` as callers. A stack is a chain of active function calls, not merely source lines.

## Level 2 — Intermediate

### Exercise 6 — Conditional breakpoint

For the transaction list, pause only when:

```text
transaction["id"] == 5001
```

Set an IDE conditional breakpoint or a `pdb` breakpoint condition. The loop continues normally for other IDs and pauses for the target transaction. This is more efficient than stopping on every iteration.

### Exercise 7 — Identify the first bad state

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

For `"Alice"`, the requirement says preserve capitalization and replace lowercase `a` only.

- After `strip()`: `parsed == "Alice"` — correct.
- After `lower()`: `normalized == "alice"` — first incorrect state.
- After replacement: `"@lice"` — consequence of the earlier change.

The defect is the unrequired `.lower()`. Inspect each intermediate value; do not inspect only the final output.

### Exercise 8 — Debug a conditional

```python
def approve(balance, amount):
    breakpoint()
    if balance >= amount:
        return True
    return False
```

For `approve(99, 100)`, inspect `balance`, `amount`, and `balance >= amount`. They are `99`, `100`, and `False`. The function behaves consistently with its inputs. Do not change the comparison before checking the values and requirement.

### Exercise 9 — Debug an exception

```python
def parse(value):
    return int(value)

result = parse("10O")
```

Run `python -m pdb script.py`. At the exception inspect `value` using `p value`. The final character is letter `O`, not zero `0`; the input is malformed. Confirm input before modifying parser logic.

### Exercise 10 — Debug pytest

```python
def total(price, quantity):
    return price * quantity

def test_total():
    result = total(10, 3)
    breakpoint()
    assert result == 30
```

Run only the test:

```bash
pytest tests/test_total.py::test_total -q
```

At the pause, inspect `p result`. Focused test execution reduces unrelated setup and output.

## Level 3 — Advanced

### Exercise 11 — Debug a fixture

The fixture returns `{"balance": 100}`, but the test expects 500. At the breakpoint inspect:

```text
p account
p account["balance"]
```

The value is 100. The fixture's Arrange state is wrong; production code has not yet been involved. Correct the fixture or the expectation according to the requirement.

### Exercise 12 — Debug a parametrized case

```python
@pytest.mark.parametrize(
    "value,expected",
    [(1, 1), (2, 4), (3, 9)],
)
def test_square(value, expected):
    result = value * 2
    breakpoint()
    assert result == expected
```

Inspect each case:
- `value=2`: result 4, expected 4 — passes.
- `value=1`: result 2, expected 1 — fails.
- `value=3`: result 6, expected 9 — fails.

The implementation multiplies by 2 instead of squaring. A passing control case does not prove all parameters are correct.

### Exercise 13 — Recursive debugging

```python
def countdown(n):
    if n == 0:
        return
    breakpoint()
    countdown(n - 1)
```

Call `countdown(3)` and inspect successive frames: `n=3`, `2`, `1`, `0`. Each call moves toward the base case. The source's exercise asks you to inspect the stack and understand that each call has its own frame.

### Exercise 14 — Debug a generator

For a generator with several `yield` statements, place breakpoints before each yield and inspect when the body runs. Calling the generator creates a generator object; requesting the next value resumes execution until the next `yield`. Do not expect all values to be calculated at generator creation.

### Exercise 15 — Debug wrapper behavior

For a decorator that returns `wrapper`, follow:

```text
decorated function call → wrapper → original function
```

Set breakpoints inside the wrapper and original function. Inspect `args`, `kwargs`, whether the original function is called, and the returned value. A wrapper can change arguments, catch exceptions, or alter results.

## Level 4 — Production-oriented

### Exercise 16 — API boundary debugging

An API unexpectedly returns 400. Break before the client call and inspect URL, method, payload, and parameters. Step over the request, then inspect status and response body. Decide whether the outgoing request or response handling violates the contract. Do not blame the server before inspecting the request.

### Exercise 17 — Database debugging

For a user lookup, break before `execute()` and inspect SQL query and `account_id`. Step over and inspect the returned `row`. This separates a wrong parameter, query, database state, and row-mapping issue. Do not change SQL before inspecting the actual parameter.

### Exercise 18 — Data pipeline debugging

Use a conditional breakpoint:

```text
row["transaction_id"] == "TX-5001"
```

Inspect `raw`, `parsed`, `validated`, and `transformed`. This isolates one bad record without stepping through millions of rows.

### Exercise 19 — AI application debugging

Place breakpoints at prompt construction, model response handling, parser, and exception handler. Inspect prompt, retrieved context, raw model response, parser input, and parser error. Redact secrets and sensitive information. Distinguish output variability from an application parsing/schema defect.

### Exercise 20 — Agent workflow debugging

Break around state update, authorization check, tool selection, and transfer call. Inspect `current_state`, `approval_status`, `amount`, and `tool_args`. Use the call stack to identify which workflow function initiated the transfer. Verify observable safety rules; do not attempt to inspect hidden chain-of-thought.

---

# Part D — All 12 Debugging Labs

1. **Wrong variable value:** `calculate_total` adds price and quantity instead of multiplying. Inspect `price`, `quantity`, and `subtotal`; fix to `price * quantity`; retain a test expecting 30 for `(10, 3)`.
2. **Incorrect function argument:** `calculate_total` calls `apply_tax(0, 18)` instead of passing the subtotal. Inspect function arguments; correct to `apply_tax(subtotal, 18)` and ensure the tax function applies 18 percent according to its contract. Test `calculate_total(100) == 118`.
3. **Incorrect conditional:** `age > 18` rejects age 18. Inspect `age` and condition; fix to `age >= 18`; keep a regression test for 18.
4. **Off-by-one loop:** `range(len(items) - 1)` skips the final item. Inspect indexes 0 and 1 for a three-item list; fix to `range(len(items))`; test all three items are processed.
5. **Incorrect nested behavior:** discount is calculated correctly but added to total. Step Into `discount`, inspect `discount_value`, then fix `total + discount_value` to `total - discount_value`; test 100 becomes 90.
6. **Swallowed exception:** `except Exception` hides unrelated errors and returns `None`. Inspect exception in the handler; catch the expected `ValueError` if that is the contract; test invalid integer input.
7. **Wrong fixture value:** fixture creates `Account("A", 0)` while test expects 500. Inspect setup at test start; fix fixture balance to 500 or correct the expectation.
8. **Failing parametrized case:** inspect each `value` and `expected`; do not assume the empty string is broken if `lower()` handles it. Confirm which case and requirement actually fail.
9. **Recursive bug:** `countdown(n + 1)` moves away from base case. Inspect successive frames; change to `countdown(n - 1)`; retain a small termination test.
10. **Incorrect API response handling:** code expects `response.json()["data"]["name"]`, but actual contract is `{"user":{"name":"Alice"}}`. Inspect status and JSON; use `["user"]["name"]` if that is the stable API contract.
11. **Data transformation bug:** amount is already in major currency units, but code divides by 100. Inspect input and transformed row; remove unnecessary scaling; test 100 remains 100.
12. **Agent state-machine bug:** `transfer()` runs even when `approved` is false. Break before transfer and inspect approval/state; reject and return before tool execution when not approved; test that an unapproved transfer does not execute.

---

# Part E — Interview Questions and Architecture Review

## 24 interview questions — model answers

1. **What is debugging?** Reproduce incorrect behavior, inspect execution/state, identify root cause, fix, and verify.
2. **What is a breakpoint?** A pause point reached by execution or satisfied condition.
3. **Does it stop permanently?** No; execution pauses and can resume.
4. **Step Over?** Execute a call without entering its implementation.
5. **Step Into?** Enter the called function.
6. **Step Out?** Finish the current function and return to caller.
7. **Call stack?** Chain of active function calls.
8. **Stack frame?** Context for one active function call, including arguments, locals, and execution position.
9. **Traceback vs call stack?** Traceback describes exception call path; live stack is active execution while paused.
10. **Why is a variable unavailable?** It belongs to another scope/frame.
11. **Why conditional breakpoints?** Target one record/iteration in repeated execution.
12. **Why isn't exception location always root cause?** Bad state may have been created earlier and propagated.
13. **Debugger vs print?** Debugger allows interactive inspection of state and stack; print remains useful for simple/remote diagnostics.
14. **`breakpoint()`?** Built-in entry into configured debugger via `sys.breakpointhook()`.
15. **`pdb`?** Python standard-library interactive debugger.
16. **Debug failing pytest?** Run one test, inspect fixtures/inputs, break, inspect stack, hypothesize, verify, fix, rerun focused and broad tests.
17. **Debug parametrized test?** Identify and rerun exact case; inspect input/expected/actual.
18. **Why concurrency debugging is hard?** Interleaving and shared state; pausing changes timing.
19. **Debug recursion?** Inspect successive frames and confirm argument moves toward base case.
20. **Debug data pipeline?** Reduce dataset, isolate record, use conditional breakpoint, inspect stage boundaries.
21. **Debug LLM app?** Inspect deterministic application components, prompt/retrieval/parser/tool state; do not inspect hidden reasoning.
22. **Debug agent?** Inspect state transitions, tool calls/args/results, retries, authorization, termination.
23. **Hypothesis-driven debugging?** Form a testable explanation and seek evidence to confirm/reject it.
24. **Why MRE?** Reduces unrelated complexity and isolates cause.

## 10 architecture questions — core answers

1. **Large Python service:** combine structured logs, metrics, distributed traces, error tracking, local debugger, and reproducible test harness.
2. **Distributed backend:** use correlation/request ID; trace gateway → services → database; reproduce relevant interaction in controlled environment.
3. **Logs/metrics/traces/debugger/tests:** metrics show how often/how much; logs record what happened; traces show where request travelled; debugger shows local live state; tests reproduce/protect.
4. **Millions of pipeline records:** use quality signals, isolate partition/record, small dataset, conditional breakpoint, and local replay.
5. **AI/LLM app:** instrument deterministic envelope (request, prompt, retrieval, metadata, structured response, parser, tools, state) and redact sensitive data.
6. **Agent workflow:** represent state → decision → tool call → result → state update; use controlled tools.
7. **Cannot reproduce locally:** collect logs, traces, metrics, deployment metadata, sanitized request, configuration, and dependency versions.
8. **Safe production diagnostics:** read-only endpoints, structured/redacted logs, access controls, correlation IDs, bounded capture, audited privileged access; avoid arbitrary code execution.
9. **Sensitive data:** define what may be logged, what is redacted, who can access, and retention duration.
10. **Reduce production overhead:** sampling, conditional diagnostics, asynchronous telemetry, bounded logging, feature flags, and targeted tracing.

---

# Part F — Production Checklist

- [ ] Reproduce and state symptom precisely.
- [ ] Understand expected vs actual behavior.
- [ ] Minimize reproduction.
- [ ] Identify suspicious state transition.
- [ ] Place strategic breakpoint.
- [ ] Inspect variables, arguments, objects, and call stack.
- [ ] Select correct frame.
- [ ] Step Into only when useful; Step Over irrelevant/trusted code; Step Out when done.
- [ ] Use conditional breakpoints for repeated cases.
- [ ] Inspect exception type/context.
- [ ] Form and verify a hypothesis.
- [ ] Avoid casual state mutation and side-effecting expressions.
- [ ] Protect secrets and sensitive data.
- [ ] Fix root cause.
- [ ] Run focused and broader tests.
- [ ] Add/retain regression test.
- [ ] Check whether defect can recur elsewhere.
- [ ] Document important findings.

---

# Part G — Knowledge Check Answers

1. **Primary debugger purpose:** controlled observation of execution and state.
2. **Step Over vs Step Into:** Step Over does not enter called function; Step Into does.
3. **Step Out:** finish current function and return to caller.
4. **Conditional breakpoint:** pause only for relevant iteration.
5. **Current function in `main → service → repository → query`:** `query`.
6. **Why service variable unavailable in query frame:** it belongs to service's frame.
7. **For `f(10)` where `y=x+1` before breakpoint:** `x=10`, `y=11`.
8. **Call chain:** `a → b → c`.
9. **Expected 100, actual 120:** reproduce and inspect state before changing code.
10. **Better than “which line is broken?”:** where does state first become inconsistent with requirement?
11. **Debugger changes concurrency outcome:** pausing changes timing/scheduling/interleavings.
12. **Debugger as production observability?** No; use logs, metrics, traces, safe diagnostics, and reproducible evidence.
13. **Debug variable LLM wording:** inspect stable application contracts, schemas, tool calls, state, parser, and policy checks; use evaluation for model quality.
14. **Agent workflow:** inspect observable state transitions, tools, arguments, results, retries, authorization, termination, and outputs—not hidden chain-of-thought.

---

# Part H — Glossary and Completion Status

| Term | Meaning |
|---|---|
| Bug | Incorrect behavior against requirement |
| Debugging | Systematic investigation and correction |
| Debugger | Tool to pause and inspect execution |
| Breakpoint | Execution pause point |
| Conditional breakpoint | Pause only when condition is true |
| Logpoint | Record information without pausing, where supported |
| Step Over | Execute current line without entering called function |
| Step Into | Enter called function |
| Step Out | Finish current function and return to caller |
| Call stack | Active function-call chain |
| Stack frame | One function call's execution context |
| Traceback | Exception-associated call path |
| Watch expression | Expression evaluated while paused |
| `pdb` | Python standard-library debugger |
| `breakpoint()` | Built-in configured debugger entry point |
| MRE | Minimal Reproducible Example |
| Root cause | Underlying reason for incorrect behavior |
| Symptom | Visible manifestation of failure |
| Race condition | Outcome depends on concurrent timing/interleaving |
| Side effect | Operation that changes external or shared state |
| Regression test | Test that protects behavior from recurring defects |

**Completion status:** Module 07, Lesson 05 — Debuggers, Breakpoints, and Call Stacks is covered by this guide. Lesson 06 — Tracebacks, Logging, and Minimal Reproductions — remains unstarted until you request it.
