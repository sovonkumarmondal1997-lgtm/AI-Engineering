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

Always validate a requested transition before updating the current state.

## Practice Exercises – State Management and State Transitions

We will solve all four exercises one by one, following the instructions in each exercise.

For every exercise, I will explain:

1. What the problem is asking.
2. The logic behind the solution.
3. The Python code.
4. The expected output.
5. How the code works.

Important concept: A state represents the current condition of a system. A state transition means changing the system from one state to another according to predefined rules.

### Exercise 1 – Login System: Identify States and Allowed Transitions

#### Step 1. Understand the problem

We have a login system with three states:

| State | Meaning |
| --- | --- |
| logged_out | User is not logged in. |
| logging_in | User is attempting to log in. |
| logged_in | User has successfully logged in. |

Our job is to decide which state transitions are allowed.

#### Step 2. Identify allowed transitions

Let's define the login workflow:

1. A user starts in logged_out.
2. When the user submits login credentials, the system moves to logging_in.
3. If authentication succeeds, the system moves to logged_in.
4. If authentication fails, the system returns to logged_out.
5. A logged-in user can log out and return to logged_out.

| Current state | Requested state | Allowed? | Reason |
| --- | --- | --- | --- |
| logged_out | logging_in | Yes | User starts authentication. |
| logged_out | logged_in | No | Authentication has not happened. |
| logging_in | logged_in | Yes | Authentication succeeds. |
| logging_in | logged_out | Yes | Authentication fails or is cancelled. |
| logged_in | logged_out | Yes | User logs out. |
| logged_in | logging_in | No | User is already logged in. |
| logged_in | logged_in | No | No state change is needed. |

#### Step 3. Visualize the login workflow

```text
LOGGED_OUT
User is not authenticated
        ↓
LOGGING_IN
Authentication is in progress
        ↓                     ↓
     Success            Failure / Cancel
        ↓                     ↓
   LOGGED_IN             LOGGED_OUT
   Authenticated         Not authenticated
```

Logging out from LOGGED_IN also returns the user to LOGGED_OUT.

Answer to the important question: Should a logged-out user jump directly to logged-in?

No. The user must pass through logging_in so that authentication can be performed before access is granted.

This is the state-transition design we will implement in Exercise 2.

### Exercise 2 – Implement is_transition_allowed()

#### Step 1. Understand the requirement

We need to create a Python function:

```python
is_transition_allowed(state, requested_state)
```

It receives two arguments:

- state: The user's current state.
- requested_state: The state the user wants to move into.

The function should return:

- True if the transition is allowed.
- False if the transition is not allowed.

#### Step 2. Implement the Python code

```python
# Function to check whether a transition is allowed
def is_transition_allowed(state, requested_state):
    if state == "logged_out":
        return requested_state == "logging_in"
    elif state == "logging_in":
        return requested_state in ["logged_in", "logged_out"]
    elif state == "logged_in":
        return requested_state == "logged_out"
    else:
        return False

# Test different transitions
print(is_transition_allowed("logged_out", "logging_in"))
print(is_transition_allowed("logged_out", "logged_in"))
print(is_transition_allowed("logging_in", "logged_in"))
print(is_transition_allowed("logging_in", "logged_out"))
print(is_transition_allowed("logged_in", "logged_out"))
print(is_transition_allowed("logged_in", "logging_in"))
```

#### Step 3. Expected output

```text
True
False
True
True
True
False
```

#### Step 4. Understand the important Python concepts

| Python concept | Purpose |
| --- | --- |
| def | Defines a function. |
| Parameters | Receive the current and requested states. |
| if | Checks the current state. |
| elif | Checks alternative conditions. |
| in | Checks whether a value exists in a list. |
| == | Compares two values. |
| return | Sends True or False back to the caller. |

How does this work?

For example:

```python
is_transition_allowed("logged_out", "logged_in")
```

Python checks:

1. Is the current state logged_out? Yes.
2. Is the requested state logging_in? No.
3. Therefore, it returns False.

Important: This function only checks whether a transition is allowed. It does not actually change the current state.

### Exercise 3 – Traffic Light with a Completed Cycle Counter

#### Step 1. Understand the problem

We have three traffic light states:

1. Red
2. Green
3. Yellow

The traffic light follows this sequence:

```text
RED
 ↓
GREEN
 ↓
YELLOW
 ↓
RED

One complete Red → Green → Yellow → Red cycle.
```

Our requirements:

- Start with Red.
- Every call to advance() changes the traffic light state.
- Increase the cycle counter after completing Yellow → Red.
- Call advance() ten times.
- Starting at Red does not count as a completed cycle.

#### Step 2. Plan the logic

We need two variables:

```python
state = "Red"
completed_cycles = 0
```

Allowed transitions:

| Current state | Next state |
| --- | --- |
| Red | Green |
| Green | Yellow |
| Yellow | Red |

The cycle counter increases only when the current state is Yellow and the next state becomes Red.

#### Step 3. Implement the Python code

```python
# Initial state
state = "Red"

# Initial cycle counter
completed_cycles = 0

# Function to advance the traffic light
def advance():
    global state, completed_cycles
    if state == "Red":
        state = "Green"
    elif state == "Green":
        state = "Yellow"
    elif state == "Yellow":
        state = "Red"
        # One complete cycle has finished
        completed_cycles = completed_cycles + 1

# Call advance() ten times
for i in range(10):
    advance()
    print("Step:", i + 1)
    print("Traffic Light:", state)
    print("Completed Cycles:", completed_cycles)
    print("--------------------")

# Display final result
```

#### Step 4. Expected output

```text
Step: 1
Traffic Light: Green
Completed Cycles: 0
--------------------
Step: 2
Traffic Light: Yellow
Completed Cycles: 0
--------------------
Step: 3
Traffic Light: Red
Completed Cycles: 1
--------------------
Step: 4
Traffic Light: Green
Completed Cycles: 1
--------------------
Step: 5
Traffic Light: Yellow
Completed Cycles: 1
--------------------
Step: 6
Traffic Light: Red
Completed Cycles: 2
--------------------
Step: 7
Traffic Light: Green
Completed Cycles: 2
--------------------
Step: 8
Traffic Light: Yellow
Completed Cycles: 2
--------------------
Step: 9
Traffic Light: Red
Completed Cycles: 3
--------------------
Step: 10
Traffic Light: Green
Completed Cycles: 3
--------------------
Final State: Green
Total Completed Cycles: 3
```

Expected result: 3 completed cycles

#### Step 5. Understand the important Python concepts

##### 1. global keyword

```python
global state, completed_cycles
```

This tells Python that the function should modify the variables defined outside the function, rather than creating new local variables with those names.

##### 2. Conditional statements

```python
if state == "Red":
    state = "Green"
```

This checks the current state and changes it to the next state.

##### 3. Reassignment

```python
completed_cycles = completed_cycles + 1
```

This increases the counter by one.

##### 4. For loop

```python
for i in range(10):
    advance()
```

This calls the function ten times.

##### 5. State transition

Every call changes the current traffic light state according to the predefined sequence.

#### Step 6. Why are there only three completed cycles?

Let's count:

| Calls | Transition | Completed cycles |
| --- | --- | --- |
| 1 | Red → Green | 0 |
| 2 | Green → Yellow | 0 |
| 3 | Yellow → Red | 1 |
| 4 | Red → Green | 1 |
| 5 | Green → Yellow | 1 |
| 6 | Yellow → Red | 2 |
| 7 | Red → Green | 2 |
| 8 | Green → Yellow | 2 |
| 9 | Yellow → Red | 3 |
| 10 | Red → Green | 3 |

We get three completed cycles because each complete cycle requires three transitions.

The tenth call starts the fourth cycle but does not complete it.

### Exercise 4 – Test Invalid Elevator Transitions from Every State

#### Step 1. Understand the problem

We need to test an elevator system to make sure it does not move into an invalid state.

The exercise does not specify the elevator's exact states and transition rules. Therefore, we will use a simple two-floor elevator model for this solution.

Let's define four states:

| State | Meaning |
| --- | --- |
| at_ground | Elevator is at the ground floor. |
| moving_up | Elevator is moving towards the first floor. |
| at_first_floor | Elevator is at the first floor. |
| moving_down | Elevator is moving towards the ground floor. |

#### Step 2. Identify allowed transitions

Our elevator follows this sequence:

```text
AT_GROUND
 ↓
MOVING_UP
 ↓
AT_FIRST_FLOOR
 ↓
MOVING_DOWN

Returns to AT_GROUND to complete the cycle.
```

Allowed transitions:

| Current state | Allowed next state |
| --- | --- |
| at_ground | moving_up |
| moving_up | at_first_floor |
| at_first_floor | moving_down |
| moving_down | at_ground |

Any other transition is rejected.

#### Step 3. Implement the Python code

We will create a function called advance_elevator().

Its responsibilities are:

1. Receive the current state.
2. Receive the requested state.
3. Check whether the transition is allowed.
4. Return the new state if allowed.
5. Return the original state if rejected.

```python
# Define allowed elevator transitions
allowed_transitions = {
    "at_ground": ["moving_up"],
    "moving_up": ["at_first_floor"],
    "at_first_floor": ["moving_down"],
    "moving_down": ["at_ground"]
}

# Function to handle elevator transitions
def advance_elevator(state, requested_state):
    if requested_state in allowed_transitions.get(state, []):
        print("Transition Allowed")
        return requested_state
    else:
        print("Transition Rejected")
        return state

# Define invalid transition tests
test_cases = [
    ("at_ground", "moving_down"),
    ("moving_up", "moving_down"),
    ("at_first_floor", "moving_up"),
    ("moving_down", "moving_up")
]

# Test invalid transitions
for current_state, requested_state in test_cases:
    print("\nCurrent State Before:", current_state)
    new_state = advance_elevator(
```

#### Step 4. Expected output

```text
Current State Before: at_ground
Transition Rejected
Current State After: at_ground

Current State Before: moving_up
Transition Rejected
Current State After: moving_up

Current State Before: at_first_floor
Transition Rejected
Current State After: at_first_floor

Current State Before: moving_down
Transition Rejected
Current State After: moving_down

All 4 invalid transitions rejected
```

#### Step 5. Understand the important Python concepts

##### 1. Dictionary

```python
allowed_transitions = {
    "at_ground": ["moving_up"],
    "moving_up": ["at_first_floor"]
}
```

A dictionary stores information in key-value pairs.

Here:

- Key = Current elevator state.
- Value = List of allowed next states.

##### 2. .get() method

```python
allowed_transitions.get(state, [])
```

This retrieves the allowed transitions for the current state.

If the state does not exist in the dictionary, it returns an empty list instead of raising a KeyError.

##### 3. in operator

```python
requested_state in allowed_transitions.get(state, [])
```

Checks whether the requested state exists in the list of allowed states.

##### 4. Returning the original state

```python
return state
```

If a transition is rejected, the function returns the original state.

This is important because an invalid request must not change the elevator's state.

##### 5. Tuple unpacking

```python
for current_state, requested_state in test_cases:
```

Each test case contains two values. Python assigns them to the two variables automatically.

#### Step 6. Verify the state remains unchanged

The most important requirement is:

If a transition is rejected, the current state must remain unchanged.

For example:

```python
current_state = "at_ground"
new_state = advance_elevator(
    current_state,
    "moving_down"
)
print(current_state == new_state)
```

Output:

```text
Transition Rejected
True
```

True confirms that the original state and returned state are identical.

## Final Revision – All Four Exercises

Let's review what you learned.

| Exercise | Main concept | Python concepts |
| --- | --- | --- |
| 1. Login system | Identifying states and transitions | State modelling, transition rules |
| 2. Login implementation | Validating transitions | Functions, parameters, conditions, return |
| 3. Traffic light | Tracking completed cycles | State changes, counters, loops, global |
| 4. Elevator | Rejecting invalid transitions | Dictionaries, lists, .get(), in, return |

### Important engineering concepts to remember

1. State: Describes the current condition of a system.
2. State transition: Changes a system from one state to another.
3. Allowed transition: A change permitted by predefined rules.
4. Invalid transition: A change that violates those rules.
5. State preservation: When a transition is rejected, the original state remains unchanged.
6. Counter: Tracks how many times a particular event occurs.

## Your understanding checkpoint

Try answering these four questions before moving forward:

1. Why should a logged-out user not transition directly to logged_in?
2. Why does the traffic light counter increase only during Yellow → Red?
3. What does allowed_transitions.get(state, []) do?
4. Why should an elevator's current state remain unchanged after an invalid transition?
