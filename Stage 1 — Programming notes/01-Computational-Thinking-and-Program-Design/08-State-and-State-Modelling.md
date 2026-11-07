# Stage 1 — Topic 08: State and State Modelling
## Complete Study Guide, Level Assessment, and Solved Exercises

---

## Part 1 — Lesson summary (under 750 words)

### 1. What is state?
**State** is information a program must remember because it can change over time and affects what the program should do next. Examples include a bank balance, a traffic light's current colour, and whether a user is logged in. State persists across relevant steps and is updated by events.

A value does not always need to be stored as state. If it can be recalculated from information already available—for example, an average calculated from a stored list—you may calculate it when needed instead of maintaining a separate value.

### 2. State transitions
A **state transition** is a change from one state to another, usually caused by an event or action: a login click, a timer finishing, or an elevator reaching a floor.

A transition is **valid** when it follows the system's rules. It is **invalid** when it breaks those rules. In this lesson's simplified traffic-light model, the only permitted sequence is:

`red → green → yellow → red`

Therefore, `red → yellow` and `green → red` are invalid. A program should check a transition before changing the state. This is a precondition check, connecting to Topic 06.

### 3. State machines
A **state machine** lists the possible states and the permitted next state(s) from each current state. The lesson's traffic-light transition table is:

| Current state | Allowed next state |
|---|---|
| `red` | `green` |
| `green` | `yellow` |
| `yellow` | `red` |

A transition absent from the table must be rejected. The program can return `False`, raise an error, or otherwise refuse the change while keeping the current state unchanged. **Current state** means the one state the system occupies now.

### 4. Representing state in Python

**Example 1 — Counter**

```python
def increment(current_value):
    return current_value + 1

counter_value = 0
print(counter_value)  # 0
counter_value = increment(counter_value)
counter_value = increment(counter_value)
print(counter_value)  # 2
```

`counter_value` stores the state. `increment()` does not remember or modify it; it returns a new value. Assigning that result back (`counter_value = increment(counter_value)`) performs the transition. The state changes `0 → 1 → 2`.

**Example 2 — Traffic light**

```python
def advance(state):
    if state == "red":
        return "green"
    elif state == "green":
        return "yellow"
    elif state == "yellow":
        return "red"

current_state = "red"
print(current_state)  # red
current_state = advance(current_state)
print(current_state)  # green
current_state = advance(current_state)
print(current_state)  # yellow
current_state = advance(current_state)
print(current_state)  # red
```

`advance()` implements the transition table and returns only the permitted next state. Reassigning the result updates the current state. This simplified function assumes its input is one of the three recognised states; an unknown string falls through and returns `None`, which is not a valid light state.

**Example 3 — Elevator transition validation**

This is a simplified teaching model, not a complete or safety-certified elevator controller. It does not model floors, movement completion, stopping conditions, or door-safety interlocks.

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
print(current_state)  # idle
if request_transition(current_state, "moving_up"):
    current_state = "moving_up"
print(current_state)  # moving_up
if request_transition(current_state, "door_open"):
    current_state = "door_open"
print(current_state)  # door_open
if request_transition(current_state, "moving_down"):
    current_state = "moving_down"
print(current_state)  # still door_open (rejected)
```

`is_transition_allowed()` checks the transition rules and returns a Boolean. `or` permits either of two destinations. `request_transition()` passes that result back to the caller; it does not change the state. The caller updates `current_state` only inside an `if` whose condition is `True`. From `door_open`, only `idle` is allowed, so the `moving_down` request is rejected and the state stays `door_open`.

### 5. Common mistakes and why this matters
Do not forget to identify information that must persist, allow arbitrary state changes without validation, or modify state before checking whether a transition is valid. A rejected transition must leave the state unchanged. Also keep **events** (such as a button press) distinct from **states** (such as `idle`).

These ideas apply to data workflows and AI agents: a task may be `waiting_for_input`, `running`, or `completed`; it must not become completed before required steps have run. Define states and permitted transitions, then reject invalid changes before they happen.

---

## Part 2 — Current learning-level assessment

The previously shared Stage 1 roadmap progresses from computational thinking and program design through Python fundamentals, control flow, collections, functions, files/CLI, testing, OOP, and production practices. Its practical projects include an expense-ledger CLI, log-investigation CLI, data-quality pipeline, and rule-based risk-review engine.

Your demonstrated progress through Topics 03–07 covers input/process/output, sequence/selection/iteration/functions, decomposition, preconditions and edge cases, pseudocode, flowcharts, and dry runs. **Your current demonstrated level is foundational/beginner, progressing toward structured program design.** Topic 08 builds on your understanding of variables, functions, conditionals, Boolean results, and precondition checks.

The roadmap shows intended coverage, not proof of mastery. For this topic, mastery means you can identify what must be remembered, list all states, define allowed transitions, implement validation, and demonstrate that rejected transitions do not mutate state.

---

## Part 3 — Solved exercises (under 1,500 words)

### Exercise 1 — Model a simple login system

**Chosen rules**

| Current state | Allowed next state | Reason |
|---|---|---|
| `logged_out` | `logging_in` | User starts authentication |
| `logging_in` | `logged_in` | Authentication succeeds |
| `logging_in` | `logged_out` | Authentication fails or is cancelled |
| `logged_in` | `logged_out` | User logs out |

A direct `logged_out → logged_in` transition is **disallowed**. The user must pass through `logging_in`, where authentication is performed. These are the rules for this simple model; a real login system would also need additional security and error states.

### Exercise 2 — Implement `is_transition_allowed()`

```python
def is_transition_allowed(state, requested_state):
    if state == "logged_out":
        return requested_state == "logging_in"
    elif state == "logging_in":
        return requested_state == "logged_in" or requested_state == "logged_out"
    elif state == "logged_in":
        return requested_state == "logged_out"
    else:
        return False

print(is_transition_allowed("logged_out", "logging_in"))  # True
print(is_transition_allowed("logged_out", "logged_in"))   # False
print(is_transition_allowed("logging_in", "logged_in"))   # True
print(is_transition_allowed("logged_in", "logged_out"))   # True
print(is_transition_allowed("logged_in", "logging_in"))   # False
```

**Line by line**
1. The function receives the current state and the requested destination.
2. If the current state is `logged_out`, only `logging_in` is accepted.
3. If it is `logging_in`, either successful login (`logged_in`) or cancellation/failure (`logged_out`) is accepted.
4. If it is `logged_in`, only logout (`logged_out`) is accepted.
5. Any unknown current state returns `False`.
6. The print calls check valid and invalid examples, including the prohibited direct login.

### Exercise 3 — Count completed traffic-light cycles over ten advances

A cycle counts only when the light moves back to `red` after leaving it. Starting at red is not a completed cycle.

```python
def advance(state):
    if state == "red":
        return "green"
    elif state == "green":
        return "yellow"
    elif state == "yellow":
        return "red"

current_state = "red"
completed_cycles = 0

for step in range(10):
    current_state = advance(current_state)
    if current_state == "red":
        completed_cycles = completed_cycles + 1

print(completed_cycles)  # 3
print(current_state)     # green
```

**Line by line**
1. `advance()` applies the same three permitted traffic-light transitions as the lesson.
2. `current_state = "red"` sets the starting state.
3. `completed_cycles = 0` starts the cycle counter at zero; the initial red does not count.
4. `range(10)` repeats the body ten times.
5. `current_state = advance(current_state)` performs and stores one transition.
6. `if current_state == "red":` detects the completion of a full red → green → yellow → red cycle.
7. The counter increases only when that condition is true.
8. The final print statements show three completed cycles and the state after ten transitions.

**Trace of states:** Start `red`; after calls 1–3: `green, yellow, red` (cycle 1); calls 4–6: `green, yellow, red` (cycle 2); calls 7–9: `green, yellow, red` (cycle 3); call 10: `green`. Therefore output is `3` cycles and final state `green`.

### Exercise 4 — Test invalid requests from every elevator state

Use the lesson's `is_transition_allowed()` and `request_transition()` functions. For each state, choose a destination that is not allowed. The test updates the state only if the request is accepted.

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

test_cases = [
    ("idle", "door_open"),
    ("moving_up", "moving_down"),
    ("moving_down", "moving_up"),
    ("door_open", "moving_up")
]

for initial_state, requested_state in test_cases:
    current_state = initial_state
    before = current_state
    allowed = is_transition_allowed(current_state, requested_state)
    accepted = request_transition(current_state, requested_state)

    if accepted:
        current_state = requested_state

    print("Request:", before, "->", requested_state)
    print("Allowed:", allowed, "| Accepted:", accepted)
    print("Before:", before, "| After:", current_state)
    print("Unchanged:", before == current_state)
```

**Line by line**
1. The two functions reproduce the lesson's transition rules and validation behavior.
2. `test_cases` contains one invalid destination for each defined state.
3. The loop takes one test case at a time and sets `current_state` to its starting state.
4. `before` records the state before the request.
5. The next two lines check the request through both required functions.
6. The `if accepted` block is the only place that could update the state. Since every test is invalid, this block is skipped each time.
7. The print statements show the requested transition, both validation results, the before/after values, and whether the state stayed unchanged.

**Expected result:** Each test prints `Allowed: False`, `Accepted: False`, and `Unchanged: True`. The four rejected transitions are `idle → door_open`, `moving_up → moving_down`, `moving_down → moving_up`, and `door_open → moving_up`.

---

## Completion checklist

- [ ] I can explain state using an example of my own.
- [ ] I can distinguish states from events.
- [ ] I can list valid and invalid transitions.
- [ ] I can implement a state machine that rejects invalid transitions.
- [ ] I can prove that a rejected transition leaves state unchanged.
- [ ] I have completed all four exercises.

**Stay on this topic until you can explain the transition rules and write the exercises without copying.**
