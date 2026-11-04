# Summary: State and State Modelling

Main idea: State means information that a program remembers over time. State modelling helps us understand what information must be remembered, how it can change, and which changes should be allowed or rejected.

## 1. What is state?

State is information that:

- A program needs to remember.
- Can change over time.
- Can affect what the program does next.

Examples:

- Bank account balance.
- Current traffic light colour.
- Whether a user is logged in.

For example, a bank account balance changes whenever money is deposited or withdrawn. Future withdrawals depend on the current balance.

What is not necessarily state?

A value that can be calculated again from existing information does not always need to be stored.

Example: If you already have a list of numbers, you can calculate their average whenever required instead of storing the average separately.

## 2. Important concepts

| Concept | Simple meaning |
| --- | --- |
| State | Information a program remembers. |
| State transition | Changing from one state to another. |
| Valid transition | A change allowed by the system's rules. |
| Invalid transition | A change that violates the system's rules. |
| State machine | A model defining possible states and allowed changes between them. |
| Current state | The state the system is in right now. |

## 3. State transitions

A state transition happens when an event or action changes the current state.

Examples:

- Clicking the login button changes a user's login state.
- A traffic light timer changes the light colour.
- An elevator arriving at a floor changes its operating state.

Not every transition should be allowed.

For example, the simplified traffic light sequence is:

Red → Green → Yellow → Red

A direct transition from Red to Yellow is invalid because it skips Green.

## 4. State machine

A state machine defines all possible states and the transitions allowed from each state.

Example:

| Current state | Allowed next state |
| --- | --- |
| Red | Green |
| Green | Yellow |
| Yellow | Red |

Any transition not listed in this table should be rejected.

This is similar to checking a precondition before allowing an operation.

## 5. Python coding examples

### Example 1: A simple counter

```python
def increment(current_value):
    return current_value + 1

counter_value = 0
print(counter_value)  # 0
counter_value = increment(counter_value)
counter_value = increment(counter_value)
print(counter_value)  # 2
```

Explanation:

- counter_value stores the current state.
- increment() receives the current value and returns a new value.
- counter_value = increment(counter_value) saves the new state.
- Calling it twice changes the state from 0 → 1 → 2.

Notice that increment() does not directly modify the original variable. It returns a new value.

### Example 2: Traffic light state machine

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

Explanation:

- current_state remembers the current traffic light colour.
- advance() checks the current state using if and elif.
- It returns only the next allowed state.
- Reassigning current_state updates the state.

This function assumes the input is one of the three recognized states. An unknown state would return None, which is not a valid traffic light state.

### Example 3: Elevator state machine

This example checks whether a requested transition is allowed before changing the state.

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
print(current_state)  # still door_open
```

Explanation:

- is_transition_allowed() checks whether a requested change follows the rules.
- or allows multiple valid next states.
- It returns True if the transition is allowed and False otherwise.
- request_transition() calls the validation function and returns its result.
- The if statement changes current_state only when the request is valid.

The final request to move down is rejected because the elevator is in the door_open state. Its state remains unchanged.

Note: This is a simplified programming example, not a real or safety-certified elevator controller.

## 6. Common beginner mistakes

1. Not identifying state: Recalculating information that genuinely needs to be remembered, such as an account balance.
2. Allowing every transition: Directly assigning current_state = requested_state without checking the rules.
3. Changing state before validation: Always check whether a transition is valid before updating the state.
4. Confusing events and states: A button press is an event; logged_in or idle is a state.

## 7. Practice exercises

1. Login system: Identify the states logged_out, logging_in, and logged_in. Decide which transitions are allowed. Should a logged-out user jump directly to logged-in?
2. Implement is_transition_allowed(state, requested_state) for your login system.
3. Extend the traffic light example with a counter that increases after every complete Red → Green → Yellow → Red cycle. Call advance() ten times and print the completed cycles. Starting at Red does not count as a completed cycle.
4. Test invalid elevator transitions from every state. Print the current state before and after each rejected request to confirm it remains unchanged.

## 8. Connection to Applied AI and Agentic AI

AI agents also maintain state, such as:

- Which step of a task has been completed.
- Whether a tool call is pending.
- Whether a conversation is waiting for user confirmation.

An agent should not complete a task before performing its required steps or call a tool before receiving the necessary information.

State modelling helps developers build predictable and reliable AI workflows by defining valid states and rejecting invalid transitions.

## Final takeaway

State = What the program remembers. State transition = How that information changes. State machine = Rules that control which changes are allowed.

## Python Practice Exercises: State and State Modelling

We will solve all four exercises one by one, using beginner-friendly Python code.

For each exercise, I will explain:

1. What the problem asks.
2. The logic behind the solution.
3. The Python code.
4. The expected output.
5. How the code works step by step.

We will use the concepts from your State and State Modelling lesson: states, state transitions, functions, conditions, loops, counters, and validation.

### Exercise 1: Design a login system

Question: Identify the states logged_out, logging_in, and logged_in. Decide which transitions are allowed. Should a logged-out user jump directly to logged-in?

#### Step 1: Understand the problem

A login system has three possible states:

| State | Meaning |
| --- | --- |
| logged_out | User is not logged in. |
| logging_in | User is attempting to log in. |
| logged_in | User has successfully logged in. |

We need to decide how the user can move between these states.

#### Step 2: Define allowed transitions

I recommend the following rules:

| Current state | Requested next state | Allowed? |
| --- | --- | --- |
| logged_out | logging_in | Yes |
| logged_out | logged_in | No |
| logging_in | logged_in | Yes |
| logging_in | logged_out | Yes |
| logged_in | logged_out | Yes |
| logged_in | logging_in | No |

Why shouldn't a logged-out user jump directly to logged-in?

Because the user must first attempt authentication. The system should verify the credentials before granting access.

The normal successful flow is:

```text
logged_out
    ↓
logging_in
    ↓
logged_in
```

Other allowed transitions:

- logging_in → logged_out when authentication fails or is cancelled.
- logged_in → logged_out when the user logs out.

Exercise 1 answer: No, a logged-out user should not jump directly to logged-in.

### Exercise 2: Implement is_transition_allowed()

Question: Write a function that checks whether a requested login-state transition is allowed.

#### Step 1: Understand the logic

We already decided the rules in Exercise 1. Now we will convert those rules into Python.

The function will receive two inputs:

- state: The user's current state.
- requested_state: The state the user wants to move to.

It will return:

- True if the transition is allowed.
- False if the transition is not allowed.

#### Step 2: Python code

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

# Test the function
print(is_transition_allowed("logged_out", "logging_in"))
print(is_transition_allowed("logged_out", "logged_in"))
print(is_transition_allowed("logging_in", "logged_in"))
print(is_transition_allowed("logged_in", "logged_out"))
print(is_transition_allowed("logged_in", "logging_in"))
```

#### Step 3: Expected output

```text
True
False
True
True
False
```

#### Step 4: Understand how it works

For example:

```python
is_transition_allowed("logged_out", "logged_in")
```

Python checks:

1. Is the current state logged_out? Yes.
2. It checks whether the requested state is logging_in.
3. The requested state is logged_in, not logging_in.
4. Therefore, it returns False.

Important concepts used:

- def: Creates a function.
- Parameters: state and requested_state receive input values.
- if, elif, else: Check different conditions.
- ==: Compares two values.
- or: Allows either of two conditions to be true.
- return: Sends the result back.

Notice that this function only checks the transition. It does not change the actual current state.

### Exercise 3: Traffic light with a completed-cycle counter

Question: Extend the traffic light example with a counter that increases after every complete Red → Green → Yellow → Red cycle. Call advance() ten times and print the completed cycles.

Starting at Red does not count as a completed cycle.

#### Step 1: Understand the problem

Our traffic light follows this sequence:

Red → Green → Yellow → Red

One complete cycle means the light has moved through all three transitions and returned to Red.

We need two variables:

| Variable | Responsibility |
| --- | --- |
| current_state | Remembers the current traffic light colour. |
| cycle_count | Counts completed traffic light cycles. |

We will increase cycle_count only when the previous state was yellow and the new state becomes red.

#### Step 2: Python code

```python
def advance(state):
    if state == "red":
        return "green"
    elif state == "green":
        return "yellow"
    elif state == "yellow":
        return "red"

current_state = "red"
cycle_count = 0

for i in range(10):
    previous_state = current_state
    current_state = advance(current_state)
    if previous_state == "yellow" and current_state == "red":
        cycle_count = cycle_count + 1
    print("Current state:", current_state)
    print("Completed cycles:", cycle_count)

print("Total completed cycles:", cycle_count)
```

#### Step 3: Expected output

```text
Current state: green
Completed cycles: 0

Current state: yellow
Completed cycles: 0

Current state: red
Completed cycles: 1

Current state: green
Completed cycles: 1

Current state: yellow
Completed cycles: 1

Current state: red
Completed cycles: 2

Current state: green
Completed cycles: 2

Current state: yellow
Completed cycles: 2

Current state: red
Completed cycles: 3

Current state: green
Completed cycles: 3

Total completed cycles: 3
```

#### Step 4: Understand the important logic

Look at these lines:

```python
previous_state = current_state
current_state = advance(current_state)
```

First, we save the old state. Then we calculate and save the new state.

Next:

```python
if previous_state == "yellow" and current_state == "red":
    cycle_count = cycle_count + 1
```

This condition checks two things:

1. Was the previous state yellow?
2. Is the new state red?

Only when both conditions are true does the counter increase.

Why do we need previous_state?

Because we need to know whether the light has just completed the full cycle. Merely checking whether the current state is Red would incorrectly count the starting Red state.

#### Step 5: Understand the loop

```python
for i in range(10):
```

- range(10) produces ten iterations.
- The loop calls advance() ten times.
- Each iteration updates the traffic light state.
- The counter increases only after a complete cycle.

Final answer: 3 complete cycles.

### Exercise 4: Test invalid elevator transitions

Question: Test invalid transitions from every elevator state. Print the current state before and after each rejected request to confirm that it remains unchanged.

#### Step 1: Understand the elevator states

Our elevator has four possible states:

| Current state | Allowed next states |
| --- | --- |
| idle | moving_up, moving_down |
| moving_up | idle, door_open |
| moving_down | idle, door_open |
| door_open | idle |

We will deliberately request an invalid transition from each state.

#### Step 2: Python code

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

# Invalid transition test cases
test_cases = [
    ("idle", "door_open"),
    ("moving_up", "moving_down"),
    ("moving_down", "moving_up"),
    ("door_open", "moving_down")
]

for state, requested_state in test_cases:
```

#### Step 3: Expected output

```text
Before request: idle
Transition rejected
After request: idle
----------------------

Before request: moving_up
Transition rejected
After request: moving_up
----------------------

Before request: moving_down
Transition rejected
After request: moving_down
----------------------

Before request: door_open
Transition rejected
After request: door_open
----------------------
```

#### Step 4: Understand the important logic

##### 1. Test cases

```python
test_cases = [
    ("idle", "door_open"),
    ("moving_up", "moving_down"),
    ("moving_down", "moving_up"),
    ("door_open", "moving_down")
]
```

Each pair contains:

- First value: Current state.
- Second value: Requested state.

All four requests violate our transition rules.

##### 2. The loop

```python
for state, requested_state in test_cases:
```

The for loop takes one pair at a time and assigns its values to two variables.

##### 3. Reset the current state

```python
current_state = state
```

Each test starts with its own initial state. This ensures that one test does not affect another.

##### 4. Validate before updating

```python
if request_transition(current_state, requested_state):
    current_state = requested_state
```

The state changes only if the transition is allowed.

If the request is rejected, the else branch runs implicitly by skipping the if body. The original state remains unchanged.

This is the most important lesson: Never update the current state before checking whether the requested transition is valid.

## Final revision: What you learned from all four exercises

| Exercise | Python concepts practised | What you implemented |
| --- | --- | --- |
| 1 | State modelling, transition rules | Login state design |
| 2 | Functions, parameters, conditions, Boolean values | Transition validation |
| 3 | Functions, loops, variables, counters, conditions | Traffic light cycle counter |
| 4 | Functions, lists, tuples, loops, validation | Invalid elevator transition testing |
