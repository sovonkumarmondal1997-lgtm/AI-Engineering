# State and State Modelling

## Why this topic matters

Almost every interesting program needs to remember something between one
step and the next: how much money is in an account, what color a traffic
light currently is, whether a user is logged in. This "remembered
information" is called **state**. Many confusing bugs come from state
changing in a way the programmer did not expect, or from a program
allowing a change that should never have been allowed (like a traffic
light jumping straight from red to green). This lesson teaches you to
think about state deliberately: what values need to be remembered, which
changes are valid, and which are not.

## Learning outcomes

By the end of this lesson, you will be able to:

- Explain what "state" means in a program, with your own example.
- Identify what information must be remembered (state) for a given
  problem, versus what can be recalculated each time.
- Distinguish between a valid and an invalid state transition.
- Build a simple state machine in Python, such as a traffic light or an
  elevator, that rejects invalid transitions.

## Prerequisites

- [Sequence, Selection, Iteration, and Abstraction](04-sequence-selection-iteration-and-abstraction.md)
- [Preconditions, Postconditions, and Edge Cases](06-preconditions-postconditions-and-edge-cases.md)

## Key terms

| Term | Plain-English definition |
|---|---|
| **State** | Information a program remembers between one action and the next, which can change over time. |
| **State transition** | A change from one state to another, usually triggered by some event or action. |
| **Valid transition** | A state change that is allowed by the rules of the system, such as a traffic light going from red to green. |
| **Invalid transition** | A state change that should never be allowed, such as a traffic light going straight from red to green without passing through the correct sequence. |
| **State machine** | A system with a fixed, known set of possible states and a fixed set of rules describing which transitions between states are allowed. |
| **Current state** | The one state a system is in right now, out of all its possible states. |

## Step-by-step explanation

### 1. What is "state"?

**State** is any information a program needs to remember, that can change
over time, and that affects future behavior. A bank account's balance is
state: it changes with every deposit and withdrawal, and future
withdrawals depend on its current value. The color a traffic light is
currently showing is state. Whether a user is currently logged in is
state. Notice the common thread: state is not recalculated fresh every
time from nothing — it persists, and it is updated by specific events.

Contrast this with something that is **not** state: if you can always
recompute a value freshly from other information you already have (for
example, an average, computed from a list of numbers you already store),
you don't necessarily need to separately remember it as state — you can
just recalculate it whenever it's needed. Deciding what genuinely needs to
be remembered, versus what can be recalculated on demand, is itself part
of state modelling.

### 2. State transitions: how state changes

A **state transition** is a change from one state to another, usually
triggered by an event: a user clicking "log in," a light's timer running
out, an elevator arriving at a floor. Thinking about state means thinking
not just about the possible states, but about **which events cause which
transitions**.

### 3. Valid versus invalid transitions

Not every imaginable state change should be allowed. A traffic light
should go red → green → yellow → red, in that specific order — it should
never jump directly from red to yellow, or from green to red, skipping
yellow. A **valid transition** follows the real-world (or business) rules
of the system; an **invalid transition** violates them. A well-designed
program actively **prevents** invalid transitions, rather than merely
hoping they never happen. This connects directly to the precondition idea
from [topic 6](06-preconditions-postconditions-and-edge-cases.md): before
allowing a transition, you check a precondition ("is this transition
allowed from the current state?").

### 4. A state machine: states plus allowed transitions

A **state machine** formalizes this thinking: you list every possible
state a system can be in, and for each state, exactly which other states
it is allowed to move to. This can be written as a simple table:

```text
Current state  | Allowed next states
---------------|--------------------
red            | green
green          | yellow
yellow         | red
```

Any transition not listed in this table (for example, `red -> yellow`) is
invalid and should be rejected by the program, typically by raising an
error or refusing the change and leaving the state unchanged.

### 5. Representing state and transitions in Python

At this stage, the simplest way to represent state is with a variable
holding the current state's name (as a string), and a small function that
uses `if` / `elif` / `else` (from
[topic 4](04-sequence-selection-iteration-and-abstraction.md)) to decide
what the next state should be, or whether a requested change is even
allowed. The function checks the current state's value before allowing any
change, exactly like a precondition check.

## Examples

### Example 1 — A single piece of state: a simple counter

```python
def increment(current_value):
    return current_value + 1


counter_value = 0
print(counter_value)                       # 0

counter_value = increment(counter_value)
counter_value = increment(counter_value)
print(counter_value)                       # 2
```

**Plain-English explanation:**

- `counter_value` is a variable that holds the **state**: a single number
  that persists between lines, in contrast to a value that gets
  recalculated fresh every time.
- `increment(current_value)` is a small function (from
  [topic 4](04-sequence-selection-iteration-and-abstraction.md)): it takes
  whatever value it is given and simply `return`s one more than it. The
  function itself does not remember anything and does not change
  `counter_value` directly — it only hands back a new value.
- `counter_value = increment(counter_value)` is the **state transition**:
  it calls `increment` with the current state, and immediately stores the
  returned result back into `counter_value`, overwriting the old value.
- Calling this line twice moves the state from `0` to `1` to `2`.
  `print(counter_value)` after both calls confirms the state correctly
  remembers both increments, not just the most recent one — because the
  new value was saved back into the same variable each time.
- This is the simplest possible example of state: a variable that persists
  and changes over time, updated by reassigning it to the result of a
  small function.

### Example 2 — A traffic light with valid transitions only

```python
def advance(state):
    if state == "red":
        return "green"
    elif state == "green":
        return "yellow"
    elif state == "yellow":
        return "red"


current_state = "red"
print(current_state)                       # red

current_state = advance(current_state)
print(current_state)                       # green

current_state = advance(current_state)
print(current_state)                       # yellow

current_state = advance(current_state)
print(current_state)                       # red
```

**Plain-English explanation:**

- `current_state` is a variable holding the current state as a plain
  string. It starts at `"red"` and is reassigned every time the light
  moves, which is how the state persists and changes across the program.
- `advance(state)` is a small function that directly represents the
  transition table from step 4 above: given the current state, its
  `if` / `elif` / `else` chooses the one state that is allowed to come
  next, and `return`s it. There is exactly one branch per real state, and
  no branch lets you jump straight from `"red"` to `"yellow"`.
- `current_state = advance(current_state)` is one state transition: it
  calls `advance` with the current state and immediately stores the
  returned value back into `current_state`, overwriting the old value.
- Tracing through the four `print` statements confirms the light correctly
  cycles red → green → yellow → red, matching the rules from step 4.
- This example shows a state machine where invalid transitions are not
  just "checked against" — they are **impossible to express at all**,
  because `advance()` never asks "what state do you want to go to?" It
  always decides the one valid next state itself, based only on the
  current state.

### Example 3 — An elevator that rejects invalid requested transitions

This example is harder: instead of always moving to one fixed next state,
it must check whether a **requested** transition is valid, and reject it
if not — closer to how many real systems work, where an external request
might ask for something disallowed.

```python
def is_transition_allowed(state, requested_state):
    if state == "idle":
        return requested_state == "moving_up" or requested_state == "moving_down"
    elif state == "moving_up":
        return requested_state == "idle" or requested_state == "door_open"
    elif state == "moving_down":
        return requested_state == "idle" or requested_state == "door_open"
    elif state == "door_open":
        return requested_state == "idle"
    else:
        return False


def request_transition(state, requested_state):
    if is_transition_allowed(state, requested_state):
        return True
    else:
        return False


current_state = "idle"
print(current_state)                                         # idle

if request_transition(current_state, "moving_up"):
    current_state = "moving_up"
print(current_state)                                          # moving_up

if request_transition(current_state, "door_open"):
    current_state = "door_open"
print(current_state)                                          # door_open

if request_transition(current_state, "moving_down"):
    current_state = "moving_down"
print(current_state)                                          # still door_open (rejected)
```

**Plain-English explanation:**

- `is_transition_allowed(state, requested_state)` is a small function that
  represents the transition rules: for each possible `state`, its
  `if` / `elif` / `else` checks whether `requested_state` is one of the
  states allowed from there, using `or` to allow more than one valid next
  state (for example, `"idle"` can move to either `"moving_up"` or
  `"moving_down"`). It returns `True` or `False`.
- `request_transition(state, requested_state)` calls
  `is_transition_allowed` and simply returns whatever it decides — `True`
  if the move is allowed, `False` if it is not. Notice it never touches
  `current_state` itself; it only reports whether the move *would* be
  valid.
- The calling code decides what to do with that answer: `if
  request_transition(current_state, "moving_up"): current_state =
  "moving_up"` only reassigns `current_state` when the function returns
  `True`. When the function returns `False`, the `if` body never runs, so
  `current_state` is left **completely unchanged**.
- Tracing through the example: the elevator starts `"idle"`. Moving to
  `"moving_up"` is allowed from `"idle"`, so `current_state` updates. From
  `"moving_up"`, moving to `"door_open"` is allowed, so it updates again.
  But from `"door_open"`, the only allowed next state is `"idle"` — so
  requesting `"moving_down"` returns `False`, the `if` body is skipped,
  and `current_state` stays `"door_open"`.
- This is the key lesson of the example: a well-built state machine does
  not just perform whatever transition is asked for — it **checks first**,
  exactly like a precondition check from
  [topic 6](06-preconditions-postconditions-and-edge-cases.md), and the
  state is only ever changed after the check succeeds. This prevents the
  elevator from ever entering an impossible or unsafe sequence of states,
  no matter what asks it to.

## Common beginner mistakes

- **Not identifying state at all**, and instead recalculating everything
  from scratch every time, even information that genuinely needs to
  persist and change (like a balance or a current traffic light color).
- **Allowing any transition without checking the rules**, for example
  directly writing `current_state = requested_state` with no check first —
  this makes invalid transitions possible and is exactly the bug this
  topic is meant to prevent.
- **Forgetting that rejecting an invalid transition should leave the state
  unchanged.** A common mistake is to partially update state, or to update
  it and then try to "undo" it, instead of checking validity *before*
  making any change at all, as Example 3 does.
- **Confusing "what happened" (an event, like a button press) with "the
  state itself" (idle, moving, and so on).** Keeping event names and state
  names cleanly separate, especially with clear naming, avoids a lot of
  confusion as a state machine grows.

## Try it yourself

1. List, in plain English, the states and the valid transitions for a
   simple login system: `logged_out`, `logging_in`, `logged_in`. Decide
   what should happen if a `logged_out` user tries to jump directly to
   `logged_in`.
2. Implement your login system from exercise 1 as a small function
   `is_transition_allowed(state, requested_state)`, following the pattern
   of Example 3 (returning `True` or `False`).
3. Extend the `advance` function from Example 2: add a separate counter
   variable that increases by one every time the light returns to `"red"`
   after having left it. Call `advance` ten times in a row (reassigning
   `current_state` and updating the counter each time) and print how many
   full cycles have happened.
4. Using the functions from Example 3, write a small test that calls
   `request_transition` with an invalid request from every state, and
   confirms (using `print` for now) that `current_state` truly never
   changes when a request is rejected.

## Summary

- **State** is information a program remembers over time, which changes in
  response to events and affects future behavior.
- A **state transition** is a change from one state to another; some
  transitions are **valid** and some are **invalid**, according to the
  rules of the system being modeled.
- A **state machine** formally lists every possible state and, for each
  one, exactly which transitions are allowed.
- Well-designed code checks whether a requested transition is valid
  *before* changing any state, and leaves the state completely unchanged
  if the request is rejected.
- Deciding what genuinely needs to be remembered as state, versus what can
  be recalculated on demand, is itself an important design decision.

## Completion checklist

- [ ] I can explain, with my own example, what "state" means in a program.
- [ ] I can distinguish a valid transition from an invalid one for a
      system I choose.
- [ ] I have built a small state machine in Python (such as a traffic
      light or an elevator) that rejects invalid transitions.
- [ ] I can explain why a rejected transition should leave the state
      unchanged.
- [ ] I have completed the "try it yourself" exercises above.

## Connection to later Applied AI and Agentic AI engineering work

Agent systems are full of state: what step of a multi-step task has been
completed, whether a tool call is pending, whether a conversation is
waiting for user confirmation. Just like the traffic light and elevator in
this lesson, an agent must only allow certain transitions — for example, it
usually should not be allowed to "complete" a task before required steps
have actually run, or to call a tool that requires information it does not
yet have. The exact discipline you practiced here — list the possible
states, define which transitions are valid, and reject anything else
before it happens — is the same discipline used to design safe, predictable
agent workflows and tool-use policies later in this curriculum.
