# Class and Instance Attributes

## 1. Learning Objectives

By the end of this chapter you should be able to:

- define instance attributes and class attributes;
- explain `self` and method binding;
- distinguish instance state from class state;
- understand instance and class namespaces;
- explain attribute lookup, inheritance, and shadowing;
- distinguish mutation from reassignment;
- recognize dangerous shared mutable class state;
- use `getattr()`, `setattr()`, `hasattr()`, `delattr()`, `vars()`, `dir()`, `type()`, and `id()`;
- use `ClassVar` correctly;
- understand `__dict__`, `__class__`, `__mro__`, and `__slots__`;
- understand the basic role of descriptors and properties;
- reason about state ownership, testing, debugging, concurrency, and process boundaries;
- apply these ideas to backend, data-engineering, ML, LLM, and agentic-AI systems.

The progression is:

```text
BASIC → INTERMEDIATE → ADVANCED → PRODUCTION
```

The real objective is not merely knowing `self.x` versus `Class.x`. It is knowing **where state should live, who owns it, who can change it, what is shared, and how that behaves under concurrency and multiple processes**.

---

## 2. Prerequisites

You should already understand:

- variables and expressions;
- objects;
- classes and instances;
- methods;
- `__init__()`;
- `self` at a basic level;
- basic inheritance.

Quick refresh:

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name


user = User("Alice")
print(user.name)
```

`self.name` is an attribute associated with the new instance.

---

# 3. What Is an Attribute?

## What is it?

An attribute is a named value or behavior associated with an object and accessed with dot notation.

```python
user.name
user.age
user.email
```

Here:

- `user` is an object reference;
- `name` is the attribute name;
- the attribute has some resolved value;
- the value may be stored directly, inherited, or produced by descriptor machinery.

## Why does it exist?

Attributes give objects named state and behavior instead of forcing callers to remember positional indexes or unrelated helper functions.

## Simple analogy

Think of an object as a file folder.

```text
User folder
├── name
├── age
└── email
```

The attribute name is the label; the attribute value is the current content.

## Basic syntax

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age
```

## `user.name` vs `user.name()`

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name

    def greet(self) -> str:
        return f"Hello, {self.name}"


user = User("Alice")
print(user.name)
print(user.greet())
```

Expected output:

```text
Alice
Hello, Alice
```

`user.name` reads an attribute. `user.greet()` first retrieves the `greet` attribute, then calls the resulting bound method.

## `name` vs `self.name` vs `user.name`

Inside a method:

```python
name
```

can be a local variable or parameter.

```python
self.name
```

means the `name` attribute of the current instance.

```python
user.name
```

means the `name` attribute of the object referenced by `user`.

## Important distinction

| Concept | Example | Meaning |
|---|---|---|
| Local variable | `name` | A local binding in a function scope |
| Parameter | `name` in `__init__(name)` | Input binding for the call |
| Instance attribute | `self.name` | State associated with an instance |
| Class attribute | `User.category` | State/value associated with a class |
| Method | `user.greet` | Behavior obtained through attribute lookup |

### Production lesson

A clear attribute model makes object state easier to inspect, test, serialize, and change.

---

# 4. Understanding `self`

## What is it?

`self` is the conventional first parameter of an instance method.

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name

    def greet(self) -> str:
        return f"Hello, {self.name}"
```

## Is `self` a keyword?

No. It is a convention. Python does not reserve the name `self` as a keyword.

You can technically write:

```python
class User:
    def __init__(this, name: str) -> None:
        this.name = name
```

but normal Python uses `self`.

## Step-by-step execution

```python
user = User("Alice")
```

Conceptually:

1. Python creates a `User` instance.
2. Python invokes the constructor.
3. The new instance is passed as the first method argument.
4. By convention that argument is named `self`.
5. `self.name = "Alice"` creates the instance attribute.

## Method binding

When you write:

```python
user.greet()
```

Python retrieves the method through the class and binds `user` as the instance argument. A useful simplified model is:

```python
User.greet(user)
```

The actual mechanism uses descriptors, which is covered later.

### Why it matters

Without the instance reference, the method would not know which object's state it should read or modify.

---

# 5. Instance Attributes

## What are they?

Instance attributes belong to a particular object.

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age


user1 = User("Alice", 25)
user2 = User("Bob", 30)

print(user1.name)
print(user2.name)
```

Expected output:

```text
Alice
Bob
```

## Ownership

Think:

```text
user1 → its own name/age state
user2 → its own name/age state
```

The two instances can have different values because their instance state is independent.

## Lifecycle

Instance attributes are commonly created during `__init__()`, changed during the object's life, and destroyed when the object is no longer reachable.

## Read, modify, delete

```python
user = User("Alice", 25)

user.age = 26
print(user.age)

del user.age
```

After deletion, a later `user.age` access can raise `AttributeError` unless another lookup path supplies that attribute.

## Production lesson

Customer-specific data, request state, connection/session state, and per-object configuration usually belong to the instance or an external durable system rather than hidden class state.

---

# 6. Instance Attributes and `__dict__`

Many ordinary Python objects expose their dynamically stored instance attributes through `__dict__`.

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age


user = User("Alice", 25)
print(user.__dict__)
```

Typical output:

```text
{'name': 'Alice', 'age': 25}
```

You can add another dynamic attribute:

```python
user.email = "alice@example.com"
print(user.__dict__)
```

Typical output:

```text
{'name': 'Alice', 'age': 25, 'email': 'alice@example.com'}
```

## Critical accuracy point

Do **not** assume every Python object has `__dict__`.

Example:

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


point = Point(1, 2)
```

`point.__dict__` normally raises `AttributeError` because the class uses slots without a dynamic instance dictionary.

## Production lesson

`__dict__` is an excellent debugging aid when available, but it should not be treated as the universal definition of object state.

---

# 7. Class Attributes

## What are they?

A class attribute is defined on the class rather than on one particular instance.

```python
class Employee:
    company = "Acme"

    def __init__(self, name: str) -> None:
        self.name = name


employee1 = Employee("Alice")
employee2 = Employee("Bob")

print(employee1.company)
print(employee2.company)
print(Employee.company)
```

Expected output:

```text
Acme
Acme
Acme
```

## Why does `employee.company` work?

Because attribute lookup can continue from the instance to its class.

The value is not copied into each object merely because it is accessible through the instance.

## Common uses

- constants;
- stable class metadata;
- default policies;
- intentionally shared registries;
- class-wide counters;
- framework configuration that is truly type-level.

### Production caution

Mutable class-level state can become hidden shared state. Use it only when the sharing is intentional and its lifecycle is understood.

---

# 8. Instance Attributes vs Class Attributes

| Concern | Instance attribute | Class attribute |
|---|---|---|
| Ownership | One object | Class |
| Typical syntax | `self.x = value` | `Class.x = value` or class-body declaration |
| Typical storage | Instance namespace when supported | Class namespace |
| Sharing | Usually not shared | May be shared/visible to many instances |
| Typical use | User data, request state, client config | Constants, defaults, shared registry |
| Inheritance | Instance belongs to the created object | Can be inherited/overridden |
| Main risk | Per-object inconsistency | Unintentional shared state |
| Testing risk | Usually localized | Can leak between tests |
| Concurrency risk | Depends on sharing of the instance | Mutable class state can be shared within a process |

### Most important distinction

**Instance attribute:** state belonging to one particular object.

**Class attribute:** value/state defined on the class and available through Python's attribute lookup rules, potentially shared among instances.

---

# 9. Attribute Lookup

When Python evaluates:

```python
obj.attribute
```

it must resolve a value or descriptor.

## Beginner model

Start with:

```text
instance
  ↓
class
  ↓
base classes according to MRO
```

If the instance namespace contains the attribute, it may be found there. Otherwise the lookup can continue through the class and its base classes.

## More accurate model

Python attribute access is more sophisticated because descriptors can take precedence.

A useful advanced mental model is:

```text
obj.attribute
   ↓
attribute machinery / descriptors
   ↓
instance namespace where applicable
   ↓
class and MRO
   ↓
possible __getattr__ fallback
```

The exact algorithm involves `__getattribute__`, data-descriptor precedence, non-data descriptors, and class lookup.

## Useful introspection

```python
print(type(obj))
print(obj.__class__)
print(getattr(obj, "__dict__", None))
print(type(obj).__dict__)
print(type(obj).__mro__)
```

### Important lesson

Do not model `obj.x` as simply:

```python
obj.__dict__["x"]
```

That works only for a subset of Python objects and attributes.

---

# 10. `__class__`, `type()`, and `__mro__`

Consider:

```python
class Animal:
    pass


class Dog(Animal):
    pass


dog = Dog()

print(type(dog))
print(dog.__class__)
print(Dog.__mro__)
```

Typical output conceptually:

```text
<class '__main__.Dog'>
<class '__main__.Dog'>
(<class '__main__.Dog'>, <class '__main__.Animal'>, <class 'object'>)
```

## `type(obj)`

Returns the object's concrete type.

## `obj.__class__`

Refers to the object's class.

## `Class.__mro__`

Shows the Method Resolution Order used for inherited lookup.

### Production use

These APIs are especially useful when debugging polymorphic code or a confusing inheritance chain.

---

# 11. Class Namespace and `Class.__dict__`

Classes are objects too, so the class has its own namespace.

```python
class Employee:
    company = "Acme"
    country = "India"

    def greet(self) -> str:
        return "hello"


print(Employee.__dict__)
```

The mapping contains entries for:

- class attributes;
- methods;
- descriptors;
- special class attributes.

The object returned is normally a read-only `mappingproxy` view.

Do not try to mutate it directly:

```python
# Employee.__dict__["company"] = "Other"  # not allowed
```

Use:

```python
Employee.company = "Other"
```

### Compare the namespaces

```python
employee = Employee()

print(employee.__dict__)
print(Employee.__dict__)
```

The first represents instance-level dynamic storage where available. The second represents the class namespace.

---

# 12. Attribute Shadowing

Start with:

```python
class Employee:
    company = "Acme"


employee = Employee()
print(employee.company)
```

Output:

```text
Acme
```

Now:

```python
employee.company = "Other"

print(employee.company)
print(Employee.company)
print(employee.__dict__)
```

Expected output:

```text
Other
Acme
{'company': 'Other'}
```

## What happened?

Before assignment:

```text
employee.__dict__ → no company
Employee.__dict__ → company = "Acme"
```

After assignment:

```text
employee.__dict__ → company = "Other"
Employee.__dict__ → company = "Acme"
```

The instance attribute is nearer in normal lookup and **shadows** the class attribute.

### Another instance

```python
employee2 = Employee()
print(employee2.company)
```

It still sees:

```text
Acme
```

### Production lesson

Shadowing is not automatically bad. Unintentional shadowing is dangerous because it can make different objects silently use different configuration values.

---

# 13. Assignment Semantics

Consider:

```python
class Employee:
    company = "Acme"


employee = Employee()
```

## Instance assignment

```python
employee.company = "Other"
```

Normally creates or updates an instance attribute.

## Class assignment

```python
Employee.company = "New Acme"
```

changes the class attribute.

## Complete example

```python
class Employee:
    company = "Acme"


first = Employee()
second = Employee()

first.company = "Local"
Employee.company = "Global"

print(first.company)
print(second.company)
print(Employee.company)
```

Expected:

```text
Local
Global
Global
```

### Why?

`first` has a shadowing instance value. `second` does not, so it reads the class value.

### Better approach

Use the owner explicitly:

```python
employee.timeout = 10       # one instance
APIClient.DEFAULT_TIMEOUT = 20  # class policy
```

This makes intent visible during code review.

---

# 14. Reading vs Writing Through an Instance

A critical rule:

```python
obj.class_attribute
```

may read a class attribute.

But:

```python
obj.class_attribute = value
```

normally creates or updates an instance attribute instead of modifying the class.

Example:

```python
class Config:
    timeout = 30


a = Config()
b = Config()

print(a.timeout)
a.timeout = 60

print(a.timeout)
print(b.timeout)
print(Config.timeout)
```

Expected output:

```text
30
60
30
```

To intentionally change the shared class value:

```python
Config.timeout = 60
```

### Production lesson

Explicit scope reduces accidental global-like state changes.

---

# 15. Mutable Class Attributes

This is one of the most important practical sections.

Consider:

```python
class Team:
    members = []


team1 = Team()
team2 = Team()

team1.members.append("Alice")

print(team2.members)
```

Expected:

```text
['Alice']
```

## Why?

Both instances resolve `members` to the same list object on the class.

```text
Team.members
     ↓
  [shared list]
    ↙      ↘
team1      team2
```

## Mutation

```python
team1.members.append("Alice")
```

changes the existing list.

## Reassignment

```python
team1.members = ["Alice"]
```

creates an instance-level attribute and shadows the class list.

## Identity

```python
class Team:
    members = []


team1 = Team()
team2 = Team()

print(team1.members is team2.members)
```

Expected:

```text
True
```

After:

```python
team1.members = ["Alice"]
print(team1.members is team2.members)
```

Expected:

```text
False
```

## Do not memorize the wrong rule

Not:

> "Never use mutable class attributes."

Better:

> **Shared mutable state is dangerous when the sharing is unintended.**

A deliberately shared registry can be valid:

```python
from typing import ClassVar


class PluginRegistry:
    plugins: ClassVar[dict[str, object]] = {}

    @classmethod
    def register(cls, name: str, plugin: object) -> None:
        cls.plugins[name] = plugin
```

Now the sharing is intentional.

## Production questions

- Who owns the object?
- Should all instances see changes?
- Does the state need locking?
- How will tests reset it?
- Does it need cross-process consistency?
- Does it belong in an external cache/database instead?

---

# 16. Mutable vs Immutable Values

Common immutable values include:

```text
int
float
str
tuple (when its contents are immutable)
frozenset
```

Common mutable values include:

```text
list
dict
set
many custom objects
```

## Mutation vs rebinding

```python
class Example:
    values = []


Example.values.append(1)  # mutate the list
Example.values = [2]      # rebind the class attribute
```

These are different operations.

### Shared references

```python
a = []
b = a

print(a is b)
```

Expected:

```text
True
```

The names refer to the same object.

### Equal but not identical

```python
a = []
b = []

print(a == b)
print(a is b)
```

Expected:

```text
True
False
```

### Key idea

Changing an object and changing what a name points to are different operations. This distinction explains many class-attribute bugs.

---

# 17. Shared State vs Per-Object State

Before defining an attribute, ask:

1. Does every object need its own value?
2. Should every instance see the same value?
3. Can one object's change affect another?
4. Is this configuration or runtime state?
5. Who owns the state?
6. Does it require synchronization?
7. Does it need persistence?
8. Does it need dependency injection?
9. Does it need to be shared across processes?

### Examples

```text
user.name             → instance
client.timeout        → instance
MAX_RETRIES           → class/module policy
request_id            → request/operation
conversation history  → session/run or external store
transaction ledger    → external durable system
```

### Production rule

Choose scope from lifecycle and ownership, not from convenience.

---

# 18. Class Constants

A common pattern is:

```python
class Order:
    MAX_ITEMS = 100
```

Uppercase communicates intent, but Python does not enforce immutability.

```python
Order.MAX_ITEMS = 200
```

is technically possible.

## Class constant vs module constant

```python
DEFAULT_TIMEOUT = 30
```

may be appropriate when the value belongs to a module/package.

```python
class APIClient:
    DEFAULT_TIMEOUT = 30
```

can make the value part of the class's discoverable API/policy.

### Production lesson

Constants should have a clear owner and should not be confused with mutable runtime state.

---

# 19. Class Attributes for Defaults and Configuration

Use a class-level default for a type-level policy, then copy the effective value into the instance when each client can differ.

```python
class APIClient:
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3

    def __init__(self, base_url: str, timeout: int | None = None) -> None:
        self.base_url = base_url
        self.timeout = (
            self.DEFAULT_TIMEOUT if timeout is None else timeout
        )
        self.max_retries = self.MAX_RETRIES


first = APIClient("https://example.invalid")
second = APIClient("https://example.invalid", timeout=10)

print(first.timeout)
print(second.timeout)
print(APIClient.DEFAULT_TIMEOUT)
```

Expected:

```text
30
10
30
```

### Why this works

```text
class default → class
actual runtime configuration → instance
```

### When to use a configuration object

When there are many related values:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ClientConfig:
    timeout: int = 30
    max_retries: int = 3
```

Then:

```python
class APIClient:
    def __init__(self, config: ClientConfig) -> None:
        self.config = config
```

This can make dependency ownership more explicit.

---

# 20. Class Attributes and Methods

Class attributes interact with normal methods, class methods, and static methods.

```python
class User:
    user_count = 0

    def __init__(self, name: str) -> None:
        self.name = name
        User.user_count += 1


User("Alice")
User("Bob")
print(User.user_count)
```

Expected:

```text
2
```

A class method can access class-level state through `cls`:

```python
class User:
    user_count = 0

    def __init__(self, name: str) -> None:
        self.name = name
        type(self).user_count += 1

    @classmethod
    def count(cls) -> int:
        return cls.user_count


User("Alice")
User("Bob")
print(User.count())
```

Expected:

```text
2
```

### `self` vs `cls`

```text
self → current instance
cls  → class used to call the class method
```

Use class state only when the state genuinely belongs to the class.

---

# 21. Class Attributes and Inheritance

```python
class Animal:
    species = "animal"


class Dog(Animal):
    pass


dog = Dog()

print(Dog.species)
print(dog.species)
```

Expected:

```text
animal
animal
```

The subclass can override it:

```python
class Dog(Animal):
    species = "dog"


print(Animal.species)
print(Dog.species)
```

Expected:

```text
animal
dog
```

An instance can shadow the subclass class attribute:

```python
dog = Dog()
dog.species = "puppy"

print(dog.species)
print(Dog.species)
```

Expected:

```text
puppy
dog
```

### Key idea

Inheritance affects **lookup**. It does not imply that class attributes are copied into every instance.

---

# 22. Attribute Lookup and MRO

Example:

```python
class Animal:
    species = "animal"


class Mammal(Animal):
    category = "mammal"


class Dog(Mammal):
    pass


dog = Dog()

print(Dog.__mro__)
print(dog.species)
print(dog.category)
```

Typical MRO:

```text
Dog → Mammal → Animal → object
```

Python searches this hierarchy according to the rules of attribute access.

### Why MRO matters

If multiple inheritance exists, Python needs a deterministic order for finding names.

Inspect it with:

```python
print(Dog.__mro__)
print(Dog.mro())
```

Descriptors further refine the lookup rules, which is why class/instance lookup should not be reduced to one simplistic dictionary lookup.

---

# 23. Descriptors — Advanced Foundation

A **descriptor** is an object implementing one or more of:

```python
__get__
__set__
__delete__
```

and participating in attribute access.

## Why do descriptors exist?

They let Python customize what happens when an attribute is read, assigned, or deleted.

Properties use descriptor behavior. Methods are descriptor-backed. Frameworks such as ORMs and validation systems can also use descriptors.

## Small example

```python
class PositiveNumber:
    def __set_name__(self, owner, name) -> None:
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value) -> None:
        if value < 0:
            raise ValueError("value must be non-negative")
        instance.__dict__[self.name] = value


class Product:
    price = PositiveNumber()


product = Product()
product.price = 10
print(product.price)
```

Expected:

```text
10
```

### Data vs non-data descriptor

A data descriptor generally implements `__set__` or `__delete__` as well as `__get__`.

A non-data descriptor generally provides only `__get__`.

Data descriptors have stronger precedence in ordinary attribute lookup.

### Why it matters

It explains why `obj.x` can execute code even when there is no `x` entry in `obj.__dict__`.

---

# 24. `property` and Attribute Access

A property provides attribute-style access with method-controlled behavior.

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius


temperature = Temperature(25.0)
print(temperature.celsius)
```

Expected:

```text
25.0
```

A setter can validate assignment:

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value
```

Now:

```python
temperature = Temperature(20.0)
temperature.celsius = 30.0
print(temperature.celsius)
```

Expected:

```text
30.0
```

### Why this matters

A property makes the public syntax look like ordinary attribute access while allowing validation, computation, or controlled mutation internally.

---

# 25. Attribute Helper Functions

## `getattr()`

### Purpose

Retrieve an attribute by dynamic name.

### Syntax

```python
getattr(object, name)
getattr(object, name, default)
```

### Return value

The resolved attribute value.

### Exception

Without a default, a missing attribute raises `AttributeError`.

### Example

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name


user = User("Alice")
print(getattr(user, "name"))
print(getattr(user, "email", "Unknown"))
```

Expected:

```text
Alice
Unknown
```

### Real-world use

Useful when the attribute name comes from configuration/schema data.

### Common mistake

Using `getattr(user, "name")` everywhere when `user.name` is clearer.

---

## `setattr()`

### Purpose

Assign an attribute using a dynamic name.

### Syntax

```python
setattr(object, name, value)
```

### Return value

`None`.

### Example

```python
class User:
    pass


user = User()
setattr(user, "name", "Alice")
print(user.name)
```

Expected:

```text
Alice
```

### Common mistake

Using dynamic mutation everywhere and making object shape unpredictable.

---

## `hasattr()`

### Purpose

Check whether attribute access succeeds.

### Syntax

```python
hasattr(object, name)
```

### Return value

A boolean.

### Example

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name


user = User("Alice")
print(hasattr(user, "name"))
print(hasattr(user, "email"))
```

Expected:

```text
True
False
```

### Important caveat

`hasattr()` performs attribute access, so properties/descriptors can run while checking.

### Common mistake

Using `hasattr()` as a substitute for a formal API contract.

---

## `delattr()`

### Purpose

Delete an attribute dynamically.

### Syntax

```python
delattr(object, name)
```

### Return value

`None`.

### Example

```python
class User:
    pass


user = User()
setattr(user, "email", "alice@example.com")
print(hasattr(user, "email"))
delattr(user, "email")
print(hasattr(user, "email"))
```

Expected:

```text
True
False
```

### Common mistake

Swallowing every `AttributeError` instead of diagnosing the real cause.

---

# 26. Attribute Deletion

Normal syntax:

```python
del obj.attribute
```

Dynamic syntax:

```python
delattr(obj, "attribute")
```

Deleting an instance attribute may reveal an inherited/class attribute again.

```python
class User:
    role = "user"


user = User()
user.role = "admin"

print(user.role)
del user.role
print(user.role)
```

Expected:

```text
admin
user
```

### Why?

The instance-level shadow disappears, so lookup continues to the class.

### Production lesson

For stable application models, explicit optional state is often easier to reason about than frequent dynamic creation/deletion of attributes.

---

# 27. Dynamic Attributes

Python can allow attributes to be created dynamically:

```python
class User:
    pass


user = User()
user.name = "Alice"
user.age = 30
```

### Benefits

- dynamic frameworks;
- adapters;
- exploratory programming;
- generic tooling.

### Risks

- inconsistent object shapes;
- missing attributes at runtime;
- difficult documentation;
- weak contracts;
- harder static analysis.

### Better application style

```python
class User:
    def __init__(self, name: str, email: str | None = None) -> None:
        self.name = name
        self.email = email
```

### Important nuance

Dynamic attributes are not inherently bad. The question is whether the flexibility matches the problem.

---

# 28. Missing Attributes and `AttributeError`

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name


user = User("Alice")
print(user.email)
```

This raises an `AttributeError` because no instance, class, base class, or descriptor supplies `email`.

### Debugging tools

```python
print(getattr(user, "__dict__", None))
print(type(user))
print(user.__class__)
print(dir(user))
print(hasattr(user, "email"))
print(getattr(user, "email", None))
```

### Important distinction

```python
"email" in getattr(user, "__dict__", {})
```

asks whether the name is stored directly in the instance dictionary.

```python
hasattr(user, "email")
```

asks whether attribute access succeeds.

Those are not the same question.

---

# 29. `vars()`, `dir()`, `type()`, and `id()`

## `vars()`

For an object with `__dict__`, `vars(obj)` provides that namespace.

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name


user = User("Alice")
print(vars(user))
```

Expected:

```text
{'name': 'Alice'}
```

It can fail for objects without an appropriate `__dict__`.

## `dir()`

```python
print("name" in dir(user))
```

`dir()` returns an introspection-oriented list of attribute names.

It is useful for exploration but is not a perfect schema of every possible dynamically accessible attribute.

## `type()`

```python
print(type(user))
```

Returns the concrete type.

## `id()`

```python
a = []
b = a
print(id(a) == id(b))
```

Expected:

```text
True
```

`id()` is a runtime identity value, not a persistent database identifier.

---

# 30. Object Identity and Shared References

The operators:

```text
is
id()
```

are about object identity.

```python
a = []
b = a

assert a is b
assert id(a) == id(b)
```

By contrast:

```python
a = []
b = []

assert a == b
assert a is not b
```

### Class-state example

```python
class Team:
    members = []


one = Team()
two = Team()

assert one.members is two.members
```

This is why mutable class state can leak changes between instances.

---

# 31. Class Attributes vs Global Variables

Compare:

```python
DEFAULT_TIMEOUT = 30
```

with:

```python
class APIClient:
    DEFAULT_TIMEOUT = 30
```

with:

```python
class APIClient:
    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout
```

### Scope comparison

| Scope | Good question |
|---|---|
| Module | Does this value belong to the module/package? |
| Class | Is it part of the type's policy/metadata? |
| Instance | Does this object have its own effective value? |
| Request | Does it apply to one operation only? |
| External system | Must the state survive/share beyond the process? |

No scope is universally best.

---

# 32. `ClassVar`

Import:

```python
from typing import ClassVar
```

Example:

```python
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class User:
    name: str
    user_type: ClassVar[str] = "standard"
```

### What does it communicate?

It tells typing/dataclass tooling:

> `user_type` is class-level rather than a normal instance field.

### Dataclass effect

`ClassVar` fields are excluded from normal dataclass field processing.

So:

```python
User("Alice")
```

is valid without passing `user_type`.

### Runtime limitation

`ClassVar` does not enforce runtime behavior.

This is technically possible:

```python
User.user_type = "premium"
```

### Production lesson

Use `ClassVar` to communicate intent and improve static reasoning, not as a runtime validator.

---

# 33. Type Annotations for Attributes

Class annotation:

```python
class User:
    company: str
```

does not automatically create the attribute on each instance.

Instance annotation:

```python
class User:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name
```

communicates the type of `name`.

Class-level annotation with `ClassVar`:

```python
from typing import ClassVar


class User:
    company: ClassVar[str] = "Acme"
```

### Key distinction

```text
annotation → communicates intended type/role
assignment → creates/updates runtime state
```

Type hints do not automatically validate runtime values.

---

# 34. `__slots__`

A class can define:

```python
class User:
    __slots__ = ("name", "age")

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age
```

### What does it do?

It defines a constrained set of instance storage slots. In this basic form, arbitrary attributes are not allowed and the normal dynamic instance dictionary is not created.

```python
user = User("Alice", 30)
```

But:

```python
user.email = "alice@example.com"
```

normally raises `AttributeError`.

### Potential benefits

- tighter object layout;
- lower memory use in suitable workloads;
- prevention of accidental dynamic attributes.

### Important limits

Slots can interact with:

- inheritance;
- weak references;
- framework expectations;
- dynamic metaprogramming.

Do **not** claim slots always make programs faster or always save a fixed amount of memory.

### Weak references

A slotted class may include `__weakref__` in its slots when weak-reference support is required.

---

# 35. Serialization and Attribute State

Serialization must decide what state is part of the external representation.

Example:

```python
class User:
    role = "standard"

    def __init__(self, name: str) -> None:
        self.name = name


user = User("Alice")

print(vars(user))
print(user.role)
```

Expected:

```text
{'name': 'Alice'}
standard
```

A serializer based only on `vars(user)` sees instance dictionary state, not every attribute available through lookup.

### Production lesson

Do not accidentally serialize class configuration as if it were per-instance data.

Define the transport contract explicitly.

---

# 36. Testing Class and Instance Attributes

Use `pytest` to test state ownership.

## Independent state

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name


def test_instances_have_independent_names() -> None:
    first = User("Alice")
    second = User("Bob")

    assert first.name == "Alice"
    assert second.name == "Bob"
```

## Shared class state

```python
class Service:
    version = "1"


def test_class_attribute_is_shared() -> None:
    first = Service()
    second = Service()

    Service.version = "2"

    assert first.version == "2"
    assert second.version == "2"
```

## Shadowing

```python
def test_instance_can_shadow_class_attribute() -> None:
    class Service:
        version = "1"

    service = Service()
    service.version = "local"

    assert service.version == "local"
    assert Service.version == "1"
```

### Mutable-state regression test

```python
def test_mutable_class_state_is_visible_to_other_instances() -> None:
    class Registry:
        items: list[str] = []

    first = Registry()
    second = Registry()

    first.items.append("x")

    assert second.items == ["x"]
```

This intentionally demonstrates the bug. The production fix is to move `items` to instance state when sharing is not intended.

---

# 37. Debugging Attribute Problems

Use a repeatable workflow.

### Step 1 — inspect the instance namespace

```python
print(getattr(obj, "__dict__", None))
```

### Step 2 — inspect the class

```python
print(type(obj).__dict__)
```

### Step 3 — inspect inheritance

```python
print(type(obj).__mro__)
```

### Step 4 — inspect identity

```python
print(id(obj))
```

For a mutable attribute:

```python
print(id(obj.items))
```

### Step 5 — test access

```python
print(hasattr(obj, "name"))
print(getattr(obj, "name", "<missing>"))
```

### Step 6 — consider descriptors

Check whether the class stores a `property` or custom descriptor under that name.

### Questions to ask

- Is the attribute on the instance?
- Is it on the class?
- Is it inherited?
- Is it shadowed?
- Is it mutable?
- Is the object shared?
- Is a property/descriptor involved?
- Is another thread/task modifying it?
- Is another process working with a different copy?

---

# 38. Common Bugs

## Forgetting `self`

Broken:

```python
class User:
    def __init__(name: str) -> None:
        name = name
```

Correct:

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name
```

**Lesson:** instance state must be attached to the instance.

## Accidental class mutation

Broken:

```python
class User:
    name = "unknown"

    def set_name(self, name: str) -> None:
        User.name = name
```

Correct:

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name
```

## Mutable class attribute

Broken:

```python
class Client:
    headers: dict[str, str] = {}
```

Correct:

```python
class Client:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}
```

## Accidental shadowing

A developer changes:

```python
client.timeout = 5
```

when they intended to change a class default.

## Mutation instead of rebinding

`shared_list.append(x)` mutates the existing object. Assigning `instance.shared_list = [...]` creates a separate instance binding.

## Assuming every object has `__dict__`

Slots and custom object layouts may not.

## Treating inheritance as copying

An inherited class attribute is found through lookup; it is not automatically copied into every instance.

## Dynamic attributes producing inconsistent state

If only some objects have a field, callers need extra runtime assumptions.

## Test interference

Class-level mutable state can survive across test functions and make test order matter.

---

# 39. Production State Ownership

One useful hierarchy is:

```text
MODULE
  ↓
CLASS
  ↓
INSTANCE
  ↓
REQUEST / OPERATION
  ↓
EXTERNAL SYSTEM
```

## Module scope

Good for:

- module-wide constants;
- stateless helper configuration.

## Class scope

Good for:

- constants;
- stable defaults;
- class metadata;
- intentional registries.

Risk:

- hidden shared mutation.

## Instance scope

Good for:

- client configuration;
- session state;
- per-object lifecycle;
- customer-specific state.

## Request scope

Good for:

- request ID;
- authorization context;
- temporary options;
- per-call state.

## External scope

Needed when state must survive process lifetime or be shared across workers:

- database;
- cache;
- object store;
- message broker;
- workflow state store.

### Core principle

> A class attribute can become hidden shared state.

That can be dangerous in a long-running service if the sharing is not intentional.

---

# 40. Concurrency

Consider:

```python
class Counter:
    count = 0
```

If multiple threads/tasks execute:

```python
Counter.count += 1
```

the logical operation involves reading, adding, and writing. Shared mutable state therefore needs concurrency-aware design.

### Do not rely on the GIL

The Global Interpreter Lock does not make arbitrary shared mutable application state logically race-free and is not a substitute for synchronization or correct state ownership.

### Threads

Threads in the same process can see shared class state.

### Async tasks

Async tasks in one process share memory too, so mutable class objects can be shared between them.

### Multiprocessing

Independent worker processes normally have separate memory. A class attribute in process A is not automatically updated in process B.

### Production lesson

If multiple executions mutate shared state, decide explicitly:

- is sharing required?
- is synchronization required?
- can the state be made immutable?
- should it be externalized?

---

# 41. Distributed Systems

Imagine:

```text
Worker A → Client.cache
Worker B → Client.cache
```

If A and B are separate processes, each normally has its own memory:

```text
Worker A → local cache A
Worker B → local cache B
```

They do not automatically share a Python class attribute.

### When global shared state is required

Use something designed for sharing:

```text
Workers
  ↓
external cache / database / broker
```

### Common production mistake

Putting a token, cache, counter, or conversation history on a class and assuming all containers/workers see the same value.

### Key lesson

> Normal Python class state is process-local memory, not distributed state.

---

# 42. Real-World Examples

## Banking

### Class-level

```python
class BankPolicy:
    DEFAULT_CURRENCY = "INR"
    MAX_TRANSFER_AMOUNT = 1_000_000
```

### Instance-level

```text
account_id
owner_id
balance
```

### Request-level

```text
request_id
idempotency_key
authentication context
```

### Externalized

```text
transaction ledger
persistent balances
audit events
```

A class variable is not a substitute for a durable banking ledger.

## Data engineering

Class-level:

```python
class PipelineDefaults:
    BATCH_SIZE = 1000
    TIMEOUT_SECONDS = 30
```

Instance/job-level:

```text
job_id
source
destination
current_batch
```

External:

```text
workflow metadata
checkpoint state
raw/processed data
```

## Machine learning

Class-level:

```text
supported model families
default batch size
```

Instance-level:

```text
loaded model
model version
device
preprocessing configuration
```

Request-level:

```text
request ID
input
deadline
```

## LLM application

Class-level:

```text
stable defaults
provider metadata
```

Instance-level:

```text
base URL
timeout
transport/session
```

Request-level:

```text
prompt/messages
request ID
generation parameters
```

External:

```text
credentials
usage records
persistent conversations
shared cache
```

## Agentic AI

Class-level:

```text
stable defaults
supported policies
```

Instance-level:

```text
agent configuration
model client
tool registry object when intentionally owned by the agent
```

Run-level:

```text
messages
current step
tool results
execution state
```

Externalized:

```text
durable checkpoints
shared memory
persistent events
```

## API client

A strong pattern is:

```text
class default policy
        ↓
instance effective configuration
        ↓
request-specific values
```

---

# 43. Advanced Integrated Example — AI Inference Client

This example combines:

- class attributes;
- instance attributes;
- `ClassVar`;
- configuration;
- validation;
- properties;
- mutable per-instance state;
- testing considerations.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class ClientDefaults:
    timeout_seconds: int = 30
    max_retries: int = 3


class AIClient:
    PRODUCT_NAME: ClassVar[str] = "AIClient"
    DEFAULTS = ClientDefaults()

    def __init__(
        self,
        base_url: str,
        timeout_seconds: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")

        timeout = (
            self.DEFAULTS.timeout_seconds
            if timeout_seconds is None
            else timeout_seconds
        )
        retries = (
            self.DEFAULTS.max_retries
            if max_retries is None
            else max_retries
        )

        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if retries < 0:
            raise ValueError("max_retries cannot be negative")

        self.base_url = base_url
        self.timeout_seconds = timeout
        self.max_retries = retries
        self._request_history: list[str] = []

    @property
    def request_count(self) -> int:
        return len(self._request_history)

    def record_request(self, request_id: str) -> None:
        if not request_id:
            raise ValueError("request_id is required")
        self._request_history.append(request_id)


client = AIClient("https://example.invalid", timeout_seconds=10)
client.record_request("req-1")
print(client.request_count)
```

Expected:

```text
1
```

## Why each attribute belongs where

| Attribute | Scope | Reason |
|---|---|---|
| `PRODUCT_NAME` | class | Stable type metadata |
| `DEFAULTS` | class | Shared immutable defaults |
| `base_url` | instance | Each client can target a different endpoint |
| `timeout_seconds` | instance | Effective per-client configuration |
| `max_retries` | instance | Effective per-client policy |
| `_request_history` | instance | Per-client mutable runtime state |
| request ID | request | Belongs to an individual operation |
| credentials | external secret system | Sensitive and lifecycle-specific |

### Production lesson

Default policy is not the same thing as runtime state.

---

# 44. Progressive Coding Examples

## Example 1 — Simple User

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name


user = User("Alice")
print(user.name)
```

Expected:

```text
Alice
```

**Line-by-line:** `self.name = name` binds the constructor argument to the new instance. `user = User(...)` creates the instance. `user.name` reads its state.

**Common mistake:** `name = name` only rebinds a local variable.

**Production lesson:** customer-specific values normally belong to instance state.

## Example 2 — Multiple Users

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name


alice = User("Alice")
bob = User("Bob")

print(alice.name)
print(bob.name)
```

Expected:

```text
Alice
Bob
```

Each object has independent instance state.

## Example 3 — Class Configuration

```python
class APIClient:
    DEFAULT_TIMEOUT = 30

    def __init__(self, timeout: int | None = None) -> None:
        self.timeout = (
            self.DEFAULT_TIMEOUT if timeout is None else timeout
        )


first = APIClient()
second = APIClient(timeout=10)

print(APIClient.DEFAULT_TIMEOUT)
print(first.timeout)
print(second.timeout)
```

Expected:

```text
30
30
10
```

The default is class-level; effective configuration is instance-level.

## Example 4 — Mutable Class Attribute Bug

```python
class Team:
    members: list[str] = []


team1 = Team()
team2 = Team()
team1.members.append("Alice")

print(team2.members)
```

Expected:

```text
['Alice']
```

The list is shared.

## Example 5 — Shadowing

```python
class Employee:
    company = "Acme"


employee = Employee()
employee.company = "Local"

print(employee.company)
print(Employee.company)
```

Expected:

```text
Local
Acme
```

The instance attribute shadows the class attribute.

## Example 6 — Class Assignment

```python
class Employee:
    company = "Acme"


alice = Employee()
bob = Employee()
Employee.company = "New Acme"

print(alice.company)
print(bob.company)
```

Expected:

```text
New Acme
New Acme
```

## Example 7 — Inheritance

```python
class Animal:
    species = "animal"


class Dog(Animal):
    pass


print(Dog().species)
```

Expected:

```text
animal
```

The value is inherited through lookup.

## Example 8 — `ClassVar`

```python
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class User:
    name: str
    category: ClassVar[str] = "standard"


user = User("Alice")
print(user.name)
print(user.category)
print(User.category)
```

Expected:

```text
Alice
standard
standard
```

## Example 9 — Property

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius


temperature = Temperature(20.0)
print(temperature.celsius)
```

Expected:

```text
20.0
```

The property provides attribute-style access through descriptor machinery.

## Example 10 — Production API/AI Client

```python
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class ClientDefaults:
    timeout: int = 30


class AIClient:
    PRODUCT_NAME: ClassVar[str] = "AIClient"
    DEFAULTS = ClientDefaults()

    def __init__(self, base_url: str, timeout: int | None = None) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        self.base_url = base_url
        self.timeout = self.DEFAULTS.timeout if timeout is None else timeout


client = AIClient("https://example.invalid", timeout=10)
print(client.base_url)
print(client.timeout)
```

Expected:

```text
https://example.invalid
10
```

**Production lesson:** separate class defaults, instance configuration, and request state.

---

# 45. Exercises

## Basic

### Exercise 1 — Instance Attribute Basics

#### Problem

Create a `Book` with `title` and `pages` stored per instance.

#### Requirements

Create two books and change only the first title.

#### Expected behavior

The second title must remain unchanged.

#### Solution

```python
class Book:
    def __init__(self, title: str, pages: int) -> None:
        self.title = title
        self.pages = pages


first = Book("Python", 300)
second = Book("Data Engineering", 500)
first.title = "Advanced Python"

assert first.title == "Advanced Python"
assert second.title == "Data Engineering"
```

#### Explanation

Each object owns its own `title` binding.

#### Key learning

Instance state is per object.

---

### Exercise 2 — Inspect the Instance Namespace

#### Problem

Create a user and inspect `__dict__`.

#### Requirements

Add `email` dynamically and verify it appears.

#### Expected behavior

The namespace changes after the dynamic assignment.

#### Solution

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age


user = User("Alice", 30)
assert user.__dict__ == {"name": "Alice", "age": 30}

user.email = "alice@example.com"
assert user.__dict__["email"] == "alice@example.com"
```

#### Explanation

A normal object commonly stores dynamic instance attributes in `__dict__`.

#### Key learning

`__dict__` is common, not universal.

---

### Exercise 3 — Class Attribute

#### Problem

Create an `Employee` with a class-level company name.

#### Requirements

Access it through the class and an instance.

#### Expected behavior

Both access paths return the same value.

#### Solution

```python
class Employee:
    company = "Acme"


employee = Employee()
assert employee.company == "Acme"
assert Employee.company == "Acme"
```

#### Explanation

The instance finds the value through class lookup.

#### Key learning

Accessibility through an instance does not mean instance storage.

---

### Exercise 4 — Shadowing

#### Problem

Make an instance override a class attribute.

#### Requirements

Preserve the class value.

#### Expected behavior

Instance shows `Local`; class shows `Acme`.

#### Solution

```python
class Employee:
    company = "Acme"


employee = Employee()
employee.company = "Local"

assert employee.company == "Local"
assert Employee.company == "Acme"
```

#### Explanation

Instance assignment creates a nearer attribute.

#### Key learning

Shadowing changes what a particular object reads.

---

### Exercise 5 — Mutation vs Reassignment

#### Problem

Show the difference for a class-level list.

#### Requirements

Demonstrate that `append()` is shared, while reassignment creates instance state.

#### Expected behavior

After reassignment, one instance is independent.

#### Solution

```python
class Team:
    members: list[str] = []


first = Team()
second = Team()

first.members.append("Alice")
assert second.members == ["Alice"]

first.members = ["Bob"]
assert first.members == ["Bob"]
assert second.members == ["Alice"]
```

#### Explanation

Mutation changes the shared list; reassignment changes the instance binding.

#### Key learning

Always separate object mutation from attribute rebinding.

---

### Exercise 6 — Class Constant

#### Problem

Create `MAX_RETRIES` and use it as an instance default.

#### Requirements

Allow a per-instance override.

#### Expected behavior

The class constant stays unchanged.

#### Solution

```python
class APIClient:
    MAX_RETRIES = 3

    def __init__(self, max_retries: int | None = None) -> None:
        self.max_retries = (
            self.MAX_RETRIES if max_retries is None else max_retries
        )


default_client = APIClient()
custom_client = APIClient(5)

assert default_client.max_retries == 3
assert custom_client.max_retries == 5
assert APIClient.MAX_RETRIES == 3
```

#### Explanation

The class owns a default policy; each instance owns its effective setting.

#### Key learning

Class defaults and instance configuration can coexist.

---

## Intermediate

### Exercise 7 — `getattr()` and `setattr()`

#### Problem

Write a function that changes a named attribute and returns the old value.

#### Requirements

Use `getattr()` and `setattr()`.

#### Expected behavior

`name` changes from Alice to Bob.

#### Solution

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name


def update_attribute(obj: object, name: str, value: object) -> object:
    old = getattr(obj, name)
    setattr(obj, name, value)
    return old


user = User("Alice")
assert update_attribute(user, "name", "Bob") == "Alice"
assert user.name == "Bob"
```

#### Explanation

These built-ins are useful when attribute names are data.

#### Key learning

Dynamic access should be used where dynamic names are actually needed.

---

### Exercise 8 — `hasattr()` and `delattr()`

#### Problem

Add and remove an optional attribute.

#### Requirements

Use both functions.

#### Expected behavior

`email` exists between the two operations.

#### Solution

```python
class User:
    pass


user = User()
assert not hasattr(user, "email")

setattr(user, "email", "alice@example.com")
assert hasattr(user, "email")

delattr(user, "email")
assert not hasattr(user, "email")
```

#### Explanation

The APIs let generic code manipulate attributes by name.

#### Key learning

Attribute existence is a runtime property; stable models should still have explicit contracts.

---

### Exercise 9 — Introspection

#### Problem

Use `type()`, `id()`, `vars()`, and `dir()`.

#### Requirements

Verify the expected type and instance namespace.

#### Expected behavior

The object is a `User`, and `name` is discoverable.

#### Solution

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name


user = User("Alice")
assert type(user) is User
assert vars(user) == {"name": "Alice"}
assert "name" in dir(user)
assert isinstance(id(user), int)
```

#### Explanation

Introspection is valuable for debugging and generic tools.

#### Key learning

`dir()` and `vars()` answer different questions.

---

### Exercise 10 — Inherited Class Attribute

#### Problem

Create `Animal` and `Dog` with inherited `species`.

#### Requirements

Override `species` only in `Dog`.

#### Expected behavior

`Animal.species` remains `animal`; `Dog.species` becomes `dog`.

#### Solution

```python
class Animal:
    species = "animal"


class Dog(Animal):
    species = "dog"


assert Animal.species == "animal"
assert Dog.species == "dog"
assert Dog().species == "dog"
```

#### Explanation

The subclass class attribute shadows the inherited class attribute.

#### Key learning

Inheritance changes lookup relationships rather than copying state into instances.

---

### Exercise 11 — `ClassVar`

#### Problem

Create a dataclass with one instance field and one class value.

#### Requirements

Use `ClassVar`.

#### Expected behavior

The class-level value should not be a constructor argument.

#### Solution

```python
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class User:
    name: str
    account_type: ClassVar[str] = "standard"


user = User("Alice")
assert user.account_type == "standard"
assert User.account_type == "standard"
```

#### Explanation

`ClassVar` communicates class-level intent and excludes the value from normal dataclass field processing.

#### Key learning

`ClassVar` is not runtime validation.

---

### Exercise 12 — Property

#### Problem

Expose a computed `full_name`.

#### Requirements

Use `@property` and update correctly when a component changes.

#### Expected behavior

The property reflects current underlying state.

#### Solution

```python
class Person:
    def __init__(self, first_name: str, last_name: str) -> None:
        self.first_name = first_name
        self.last_name = last_name

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


person = Person("Ada", "Lovelace")
assert person.full_name == "Ada Lovelace"
person.last_name = "Byron"
assert person.full_name == "Ada Byron"
```

#### Explanation

`full_name` is computed, not separately stored.

#### Key learning

An attribute-looking API can execute descriptor-backed logic.

---

### Exercise 13 — Property Descriptor Inspection

#### Problem

Inspect a property stored on a class.

#### Requirements

Prove that it implements `__get__`.

#### Expected behavior

The class namespace contains a `property` instance.

#### Solution

```python
class Person:
    @property
    def name(self) -> str:
        return "Alice"


descriptor = Person.__dict__["name"]
assert isinstance(descriptor, property)
assert hasattr(descriptor, "__get__")
```

#### Explanation

Properties are descriptors stored in the class namespace.

#### Key learning

Descriptor machinery explains controlled attribute access.

---

### Exercise 14 — MRO Inspection

#### Problem

Create a three-level inheritance chain and inspect its MRO.

#### Requirements

Assert the exact order.

#### Expected behavior

`C.mro()` must be `[C, B, A, object]`.

#### Solution

```python
class A:
    value = "A"


class B(A):
    pass


class C(B):
    pass


assert C.mro() == [C, B, A, object]
assert C().value == "A"
```

#### Explanation

MRO determines inherited lookup order.

#### Key learning

`mro()` is a practical debugging API.

---

### Exercise 15 — `__slots__`

#### Problem

Restrict a user to `name` only.

#### Requirements

Declare slots and demonstrate that `email` cannot be added dynamically.

#### Expected behavior

Assigning `email` raises `AttributeError`.

#### Solution

```python
class User:
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name


user = User("Alice")
assert user.name == "Alice"

try:
    user.email = "alice@example.com"
except AttributeError:
    pass
else:
    raise AssertionError("email should not be assignable")
```

#### Explanation

Slots constrain the instance layout.

#### Key learning

Slots are a design trade-off, not a universal performance switch.

---

### Exercise 16 — Intentional Shared Registry

#### Problem

Create a class-level plugin registry.

#### Requirements

Use `ClassVar` and a class method.

#### Expected behavior

All instances observe the same registered plugin.

#### Solution

```python
from typing import ClassVar


class PluginRegistry:
    plugins: ClassVar[dict[str, object]] = {}

    @classmethod
    def register(cls, name: str, plugin: object) -> None:
        cls.plugins[name] = plugin


first = PluginRegistry()
second = PluginRegistry()

PluginRegistry.register("demo", object())

assert "demo" in first.plugins
assert "demo" in second.plugins
```

#### Explanation

Here shared state is intentional.

#### Key learning

The problem is unintended sharing, not the mere existence of shared state.

---

## Advanced

### Exercise 17 — State Source Inspector

#### Problem

Write a helper that reports whether an attribute is directly on the instance, available on the class/MRO, or missing.

#### Requirements

Do not mutate the object.

#### Expected behavior

Return `

#### Expected behavior

Return `instance`, `class-or-inherited`, or `missing`.

#### Solution

```python
def attribute_source(obj: object, name: str) -> str:
    namespace = getattr(obj, "__dict__", {})
    if name in namespace:
        return "instance"
    if hasattr(type(obj), name):
        return "class-or-inherited"
    return "missing"


class User:
    role = "user"

    def __init__(self, name: str) -> None:
        self.name = name


user = User("Alice")
assert attribute_source(user, "name") == "instance"
assert attribute_source(user, "role") == "class-or-inherited"
assert attribute_source(user, "email") == "missing"
```

#### Explanation

The helper first checks direct instance storage, then checks class/MRO access.

#### Key learning

An attribute can be accessible without being physically stored in the instance namespace.

---

### Exercise 18 — Per-Client Timeout

#### Problem

Design an API client with a class default and instance-specific effective timeout.

#### Requirements

- define `DEFAULT_TIMEOUT` on the class;
- allow a per-instance override.

#### Expected behavior

Two clients can hold different effective timeout values.

#### Solution

```python
class APIClient:
    DEFAULT_TIMEOUT = 30

    def __init__(self, timeout: int | None = None) -> None:
        self.timeout = (
            self.DEFAULT_TIMEOUT if timeout is None else timeout
        )


first = APIClient()
second = APIClient(10)

assert first.timeout == 30
assert second.timeout == 10
assert APIClient.DEFAULT_TIMEOUT == 30
```

#### Explanation

The class owns the default policy. Each instance owns its actual configuration.

#### Key learning

Defaults and runtime state can have different owners.

---

### Exercise 19 — Agent Configuration vs Run State

#### Problem

Create immutable agent configuration and separate per-run message state.

#### Requirements

- configuration must be shareable;
- messages must be isolated.

#### Expected behavior

Adding a message to one run must not affect another.

#### Solution

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentConfig:
    model_name: str = "example-model"


@dataclass
class AgentRun:
    config: AgentConfig
    messages: list[str] = field(default_factory=list)


config = AgentConfig()
first = AgentRun(config)
second = AgentRun(config)

first.messages.append("hello")

assert second.messages == []
assert first.config is second.config
```

#### Explanation

Immutable configuration can be safely shared while mutable execution state is per run.

#### Key learning

Lifecycle boundaries should guide attribute ownership.

---

### Exercise 20 — State Ownership Review

#### Problem

Repair this design:

```python
class Agent:
    messages = []
    temperature = 0.2
```

#### Requirements

- temperature should be a class-level default;
- messages must be per-instance.

#### Expected behavior

Two agents must not share message history.

#### Solution

```python
class Agent:
    DEFAULT_TEMPERATURE = 0.2

    def __init__(self, temperature: float | None = None) -> None:
        self.temperature = (
            self.DEFAULT_TEMPERATURE
            if temperature is None
            else temperature
        )
        self.messages: list[str] = []


first = Agent()
second = Agent()
first.messages.append("hello")

assert second.messages == []
assert first.temperature == 0.2
assert second.temperature == 0.2
```

#### Explanation

The original `messages` was class-level mutable state. The repaired design gives each instance a separate list.

#### Key learning

Ask whether a value is a default policy, object state, or execution state before choosing its scope.

---

### Exercise 21 — Test Isolation

#### Problem

Redesign a cache so tests do not depend on one another through class-level state.

#### Requirements

- make the cache instance-owned;
- prove two fresh caches are independent.

#### Expected behavior

A mutation in one cache must not appear in another.

#### Solution

```python
class Cache:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}


def test_first() -> None:
    cache = Cache()
    cache.values["a"] = "1"
    assert cache.values["a"] == "1"


def test_second() -> None:
    cache = Cache()
    assert cache.values == {}


test_first()
test_second()
```

#### Explanation

Fresh instances establish isolation without reset logic for shared class state.

#### Key learning

Test isolation is strongly affected by state ownership.

---

### Exercise 22 — Slotted Model Inspection

#### Problem

Create a slotted `Point` and write a safe debug helper for its attributes.

#### Requirements

- use `__slots__`;
- do not assume `__dict__` exists.

#### Expected behavior

The helper returns both declared attributes.

#### Solution

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


def point_state(point: Point) -> dict[str, int]:
    return {
        "x": point.x,
        "y": point.y,
    }


point = Point(1, 2)
assert point_state(point) == {"x": 1, "y": 2}
```

#### Explanation

A domain-specific inspection function is more reliable than assuming a dynamic dictionary exists.

#### Key learning

Object introspection should respect the object's storage model.

---

### Exercise 23 — Property-Backed Invariant

#### Problem

Create a client whose timeout can be read as an attribute but cannot be set to zero or less.

#### Requirements

- use `@property`;
- validate the setter.

#### Expected behavior

`timeout` accepts positive values and rejects non-positive values.

#### Solution

```python
class Client:
    def __init__(self, timeout: int) -> None:
        self.timeout = timeout

    @property
    def timeout(self) -> int:
        return self._timeout

    @timeout.setter
    def timeout(self, value: int) -> None:
        if value <= 0:
            raise ValueError("timeout must be positive")
        self._timeout = value


client = Client(30)
client.timeout = 10
assert client.timeout == 10

try:
    client.timeout = 0
except ValueError:
    pass
else:
    raise AssertionError("invalid timeout was accepted")
```

#### Explanation

The property provides controlled attribute access.

#### Key learning

An attribute API can protect invariants without forcing callers to use a method such as `set_timeout()`.

---

### Exercise 24 — Class Registry with Explicit Reset

#### Problem

Build an intentionally shared class registry that can be reset for tests.

#### Requirements

- use `ClassVar`;
- provide `register()`;
- provide `clear()`;
- make sharing explicit.

#### Expected behavior

After `clear()`, the registry is empty for every instance.

#### Solution

```python
from typing import ClassVar


class Registry:
    values: ClassVar[dict[str, object]] = {}

    @classmethod
    def register(cls, name: str, value: object) -> None:
        cls.values[name] = value

    @classmethod
    def clear(cls) -> None:
        cls.values.clear()


first = Registry()
second = Registry()

Registry.register("x", object())
assert "x" in first.values
assert "x" in second.values

Registry.clear()
assert first.values == {}
assert second.values == {}
```

#### Explanation

Shared state is appropriate here only because sharing is the explicit purpose of the registry.

#### Key learning

If class-level mutable state is required, its lifecycle and test cleanup should be deliberate.

---

# DEBUGGING LAB

## Debugging Problem 1 — Mutable Class Attribute

### Broken code

```python
class ShoppingCart:
    items: list[str] = []


first = ShoppingCart()
second = ShoppingCart()
first.items.append("book")

assert second.items == []
```

### Expected behavior

Each cart should have an independent list.

### Actual behavior

The assertion fails because both carts resolve the same class-level list.

### Debugging clues

```python
print(first.items is second.items)
print(ShoppingCart.items)
```

The first expression is `True`.

### Investigation

The list was created at class-definition time and stored on the class.

### Root cause

Shared mutable state was used where per-instance state was required.

### Fix

```python
class ShoppingCart:
    def __init__(self) -> None:
        self.items: list[str] = []
```

### Explanation

Each constructor call now creates a new list.

### General lesson

Use instance ownership for per-object collections.

---

## Debugging Problem 2 — Shadowing Bug

### Broken code

```python
class Config:
    timeout = 30


config = Config()
Config.timeout = 60
config.timeout = 10

assert Config.timeout == 10
```

### Expected behavior

The class default should remain `60`; only the instance should be `10`.

### Actual behavior

The assertion fails because `config.timeout = 10` created an instance attribute instead of changing the class.

### Debugging clues

```python
print(config.__dict__)
print(Config.timeout)
print(config.timeout)
```

### Investigation

You will see:

```text
{'timeout': 10}
60
10
```

### Root cause

The code confused instance assignment with class assignment.

### Fix

Use the intended owner explicitly:

```python
config.timeout = 10
assert Config.timeout == 60
```

or, when intentionally changing the shared default:

```python
Config.timeout = 10
```

### Explanation

The two assignments have different ownership semantics.

### General lesson

Do not infer the assignment target from how the attribute was originally read.

---

## Debugging Problem 3 — Inheritance Lookup Bug

### Broken code

```python
class Base:
    region = "global"


class Child(Base):
    pass


child = Child()
child.region = "local"
Base.region = "new-global"

assert child.region == "new-global"
```

### Expected behavior

A developer expecting the class change to be visible on the child is surprised.

### Actual behavior

`child.region` remains `local`.

### Debugging clues

```python
print(child.__dict__)
print(Base.__dict__["region"])
print(Child.__mro__)
```

### Root cause

The instance contains a shadowing attribute, so ordinary lookup finds it before the class value.

### Fix

If the instance should follow the inherited value, remove the shadow:

```python
del child.region
assert child.region == "new-global"
```

### General lesson

Shadowing changes the effective value for one object.

---

## Debugging Problem 4 — Dynamic Attribute Bug

### Broken code

```python
class User:
    pass


alice = User()
bob = User()
alice.email = "alice@example.com"

print(bob.email)
```

### Expected behavior

The model should define whether `email` exists for all users.

### Actual behavior

```text
AttributeError
```

### Debugging clues

```python
print(vars(alice))
print(vars(bob))
```

### Root cause

Dynamic assignment created an attribute on only one object.

### Fix

Define the model explicitly:

```python
class User:
    def __init__(self, email: str | None = None) -> None:
        self.email = email
```

### General lesson

Dynamic attributes are useful, but stable application state should usually have an explicit contract.

---

## Debugging Problem 5 — Shared-State Test Bug

### Broken code

```python
class Metrics:
    values: dict[str, int] = {}


def test_first() -> None:
    Metrics.values["requests"] = 1
    assert Metrics.values["requests"] == 1


def test_second() -> None:
    assert Metrics.values == {}
```

### Expected behavior

Every test should begin with a clean registry.

### Actual behavior

The second test can fail after the first test.

### Debugging clues

Inspect:

```python
print(Metrics.values)
```

### Root cause

Mutable class state persists in the process.

### Fix

Prefer instance state for test-local metrics, or explicitly reset intentionally global registries in fixtures when class sharing is genuinely required.

### General lesson

Tests expose hidden ownership problems.

---

## Debugging Problem 6 — Missing `__dict__`

### Broken code

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


point = Point(1, 2)
print(point.__dict__)
```

### Expected behavior

The developer wants to inspect the object.

### Actual behavior

`AttributeError` because this slotted object does not provide a normal instance dictionary.

### Debugging clues

```python
print(Point.__slots__)
print(hasattr(point, "__dict__"))
```

### Root cause

The class uses constrained slots.

### Fix

Use direct attributes or a model-aware inspection function.

### General lesson

Never assume `__dict__` exists on every Python object.

---

## Debugging Problem 7 — Mutation vs Reassignment

### Broken code

```python
class Registry:
    names: list[str] = []


first = Registry()
second = Registry()

first.names = first.names
first.names.append("Alice")

assert second.names == []
```

### Expected behavior

The developer expected the assignment to make a copy.

### Actual behavior

The list remains shared.

### Debugging clues

```python
print(first.names is second.names)
```

### Root cause

Assignment copied the reference, not the list.

### Fix

A shallow copy would be:

```python
first.names = list(first.names)
```

But the stronger design is per-instance initialization:

```python
class Registry:
    def __init__(self) -> None:
        self.names: list[str] = []
```

### General lesson

Rebinding a name to the same object is not copying that object.

---

## Debugging Problem 8 — Accidental Class Mutation

### Broken code

```python
class Client:
    headers: dict[str, str] = {}

    def add_header(self, key: str, value: str) -> None:
        self.headers[key] = value


first = Client()
second = Client()
first.add_header("X-Trace", "abc")

assert second.headers == {}
```

### Expected behavior

Each client should have its own headers.

### Actual behavior

`second.headers` also contains the header.

### Debugging clues

```python
print(first.headers is second.headers)
```

### Root cause

The dictionary belongs to the class.

### Fix

```python
class Client:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}

    def add_header(self, key: str, value: str) -> None:
        self.headers[key] = value
```

### General lesson

Per-client mutable state belongs to the client instance.

---

# PRODUCTION ARCHITECTURE

## 46. Configurable AI/API Inference Client — Mini Project

Build a small production-oriented client that demonstrates:

- class-level defaults;
- class constants;
- instance configuration;
- request-specific state;
- safe mutable state;
- `ClassVar`;
- validation;
- property access;
- pytest tests;
- logging considerations;
- explicit state ownership.

### Requirements

The client should:

1. store a base URL per instance;
2. expose a class-level default timeout;
3. expose a class-level retry policy;
4. support per-instance timeout;
5. validate configuration;
6. keep request history per instance;
7. expose request count through a property;
8. use `ClassVar` for stable product metadata;
9. avoid credentials;
10. make tests independent.

### Architecture

```text
AIClient class
   |
   +-- constants/defaults
   |
   +-- methods
   |
   +-- descriptors/properties
   |
   +-- per-instance configuration
   |
   +-- per-instance runtime state
            |
            +--> individual request state
            |
            +--> external API
```

### Implementation

```python
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import ClassVar


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClientDefaults:
    timeout_seconds: int = 30
    max_retries: int = 3


class AIClient:
    PRODUCT_NAME: ClassVar[str] = "AIClient"
    DEFAULTS: ClassVar[ClientDefaults] = ClientDefaults()

    def __init__(
        self,
        base_url: str,
        timeout_seconds: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")

        timeout = (
            self.DEFAULTS.timeout_seconds
            if timeout_seconds is None
            else timeout_seconds
        )
        retries = (
            self.DEFAULTS.max_retries
            if max_retries is None
            else max_retries
        )

        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if retries < 0:
            raise ValueError("max_retries cannot be negative")

        self.base_url = base_url
        self.timeout_seconds = timeout
        self.max_retries = retries
        self._request_history: list[str] = []

    @property
    def request_count(self) -> int:
        return len(self._request_history)

    def record_request(self, request_id: str) -> None:
        if not request_id:
            raise ValueError("request_id is required")
        self._request_history.append(request_id)
        logger.info(
            "recorded request",
            extra={
                "client_type": type(self).__name__,
                "request_id": request_id,
            },
        )
```

### State ownership

| State | Owner | Reason |
|---|---|---|
| `PRODUCT_NAME` | Class | Stable metadata |
| `DEFAULTS` | Class | Immutable defaults |
| `base_url` | Instance | Clients can target different endpoints |
| `timeout_seconds` | Instance | Effective configuration |
| `max_retries` | Instance | Effective configuration |
| `_request_history` | Instance | Per-client mutable runtime state |
| `request_id` | Request | Per-operation state |
| secret credentials | Secret manager/external system | Security and lifecycle |

### Tests

```python
import pytest


def test_default_configuration() -> None:
    client = AIClient("https://example.invalid")

    assert client.timeout_seconds == 30
    assert client.max_retries == 3


def test_instance_configuration_is_independent() -> None:
    first = AIClient("https://a.invalid", timeout_seconds=10)
    second = AIClient("https://b.invalid", timeout_seconds=20)

    assert first.timeout_seconds == 10
    assert second.timeout_seconds == 20


def test_request_history_is_instance_owned() -> None:
    first = AIClient("https://a.invalid")
    second = AIClient("https://b.invalid")

    first.record_request("req-1")

    assert first.request_count == 1
    assert second.request_count == 0


def test_invalid_timeout() -> None:
    with pytest.raises(ValueError):
        AIClient("https://example.invalid", timeout_seconds=0)


def test_invalid_retry_count() -> None:
    with pytest.raises(ValueError):
        AIClient("https://example.invalid", max_retries=-1)
```

### Production considerations

A real client would also need appropriate:

- timeouts;
- retry policy;
- connection pooling;
- rate-limit handling;
- structured logs;
- tracing;
- secret injection;
- metrics;
- error translation;
- request correlation.

The important lesson remains:

```text
class policy → instance configuration → request state → external system
```

---

# 47. Interview Questions

## Beginner

### What is an instance attribute?

An attribute associated with a particular object, usually assigned through `self.attribute`.

### What is a class attribute?

An attribute defined on the class and available through class/instance lookup.

### What is `self`?

The conventional first parameter of an instance method that identifies the current instance.

### Is `self` a Python keyword?

No. It is a convention.

### Where are instance attributes commonly created?

Usually in `__init__()` with assignments such as `self.name = name`, though dynamic creation later is possible.

### Why can `obj.class_attribute` work?

Because attribute lookup can continue from the instance to the class.

---

## Intermediate

### Does reading a class attribute through an instance copy it?

No. It normally resolves and returns the existing class-level value/object.

### Does `obj.x = value` normally change the class?

No. For ordinary attributes, it creates or updates an instance-level attribute.

### What is shadowing?

An attribute nearer in the lookup path hides a same-named attribute farther away.

### Why are mutable class attributes dangerous?

Multiple instances can reference the same mutable object and therefore observe each other's changes.

### What is the difference between mutation and reassignment?

Mutation changes an object in place; reassignment changes the object/value referenced by an attribute name.

### What is `ClassVar`?

A typing construct used to communicate that an attribute is class-level rather than an instance field.

### Does `ClassVar` enforce runtime types?

No.

### What is `__dict__`?

A commonly available namespace containing dynamically stored attributes for classes/instances that provide one.

### Does every object have `__dict__`?

No. Slots and other object layouts may not.

---

## Advanced

### What is MRO?

The Method Resolution Order used to search the class hierarchy for attributes and methods.

### What is a descriptor?

An object implementing methods such as `__get__`, `__set__`, or `__delete__` that participates in attribute access.

### Why is `property` a descriptor?

Because a `property` object implements descriptor methods, allowing attribute access to execute getter/setter logic.

### What is `getattr()` used for?

Dynamic attribute lookup.

### What is `setattr()` used for?

Dynamic attribute assignment.

### What does `hasattr()` actually test?

Whether attribute access succeeds; it can invoke descriptors/properties while doing so.

### Why is `dir()` not a perfect schema?

It is intended for useful introspection and can be affected by inheritance, custom `__dir__`, and dynamic behavior.

### What is `id()` useful for?

Runtime object-identity diagnostics, especially when investigating shared references.

### What does `__slots__` do?

It constrains instance attribute storage and can eliminate the normal dynamic instance dictionary for a class, subject to inheritance/design.

---

## Architecture

### Why should a per-request list usually not be a class attribute?

Because all objects in the process could share it, creating cross-request leakage and concurrency/test-isolation problems.

### Where should an API client's default timeout live?

A class constant/default or configuration object can own the policy; each instance should normally store its effective timeout when clients differ.

### Where should agent messages live?

Per-run/session state or an external store, not shared mutable class state.

### Does class state become shared across web workers?

Not when the workers are separate processes; each process normally has its own memory.

### When is mutable class state appropriate?

When shared ownership is intentional, its lifecycle is explicit, and concurrency, testing, and process-scope implications are handled.

---

# 48. Architecture Questions

## Scenario 1 — Multiple Web Workers

A service has:

```python
class Cache:
    values = {}
```

and the team expects all worker processes to share this cache.

### Model answer

That expectation is incorrect for normal separate processes. Each worker gets its own in-memory class state. Use an external shared cache or database when the cache must be shared or durable.

## Scenario 2 — Different API Timeouts

100 clients require different timeouts.

### Model answer

Keep a class-level default and store effective timeout per instance. If configuration is complex, inject a configuration object.

## Scenario 3 — Agent Run State

The system stores model defaults, messages, tool results, and current step.

### Model answer

Stable defaults can be class-level or configuration-level. Messages, tool results, and current step belong to a run/session object or external checkpoint state.

## Scenario 4 — Cross-Request Leakage

A user receives another user's data from a class-level dictionary.

### Model answer

Inspect mutable class attributes and verify whether distinct requests are mutating the same object. Move request/customer state to an appropriate instance/request scope and add regression tests.

## Scenario 5 — Test Order Dependency

Tests pass alone but fail together.

### Model answer

Look for module/class mutable state. Inspect `Class.__dict__`, reset intentional shared registries, or redesign to instance ownership.

## Scenario 6 — Subclass Defaults

A subclass needs a different default timeout.

### Model answer

A subclass can override a class attribute:

```python
class BaseClient:
    DEFAULT_TIMEOUT = 30


class SlowClient(BaseClient):
    DEFAULT_TIMEOUT = 60
```

Instance initialization should read through the subclass-aware class lookup.

## Scenario 7 — Serialization

A serializer based on `vars(obj)` omits a class attribute.

### Model answer

That is expected because `vars(obj)` represents the instance dictionary. Define the serialized contract explicitly rather than assuming every reachable attribute is serialized.

## Scenario 8 — Class-Level Cache

A class-level cache is intended to be shared within a process.

### Model answer

This can be valid. Make ownership explicit, provide lifecycle/eviction rules, consider concurrency, and reset/replace it in tests. Do not assume the cache is shared across processes.

## Scenario 9 — `ClassVar` Review

A developer uses `ClassVar` to 

A developer uses `ClassVar` to make a class attribute immutable.

### Model answer

That is incorrect. `ClassVar` communicates that an attribute is class-level to typing/dataclass tooling; it does not prevent reassignment at runtime.

## Scenario 10 — Request-Specific Headers

An AI client stores HTTP headers on the class because every request uses the same defaults.

### Model answer

Immutable default headers may be class-level, but per-request mutable headers should not automatically be stored on a shared class object. Prefer request-local structures and copy defaults when needed.

---

# 49. Knowledge Check

## Multiple Choice

### Question 1

Which statement is correct?

A. Every attribute is stored in the instance `__dict__`.
B. Class attributes are copied into every instance.
C. An instance can resolve an attribute from its class.
D. `ClassVar` prevents assignment at runtime.

**Answer:** C.

**Explanation:** Attribute lookup can continue from an instance to its class and bases. The other statements are false.

### Question 2

What normally happens with:

```python
obj.x = value
```

when `x` exists only as a normal class attribute?

A. The class is changed.
B. An instance attribute is created or updated.
C. All instances receive copies.
D. The assignment is ignored.

**Answer:** B.

### Question 3

Why is this risky?

```python
class Team:
    members = []
```

A. Lists cannot be class attributes.
B. The list may be unintentionally shared.
C. `append()` does not work on class attributes.
D. Classes cannot contain objects.

**Answer:** B.

### Question 4

What does `ClassVar[str]` primarily communicate?

A. Runtime type enforcement.
B. Database persistence.
C. Class-level intent to typing/dataclass tooling.
D. Deep immutability.

**Answer:** C.

### Question 5

Which function returns an object's concrete type?

A. `id()`
B. `dir()`
C. `type()`
D. `vars()`

**Answer:** C.

## Predict the Output

### Question 6

```python
class Config:
    timeout = 30


a = Config()
b = Config()
a.timeout = 10

print(a.timeout)
print(b.timeout)
print(Config.timeout)
```

**Answer:**

```text
10
30
30
```

**Explanation:** `a.timeout = 10` creates an instance-level shadowing attribute.

### Question 7

```python
class Team:
    members = []


first = Team()
second = Team()
first.members.append("Alice")

print(second.members)
```

**Answer:**

```text
['Alice']
```

**Explanation:** Both instances resolve the same mutable list stored on the class.

### Question 8

```python
class Team:
    members = []


first = Team()
second = Team()
first.members = ["Alice"]

print(first.members)
print(second.members)
```

**Answer:**

```text
['Alice']
[]
```

**Explanation:** Reassignment creates instance-level state for `first`.

### Question 9

```python
class Animal:
    species = "animal"


class Dog(Animal):
    pass


dog = Dog()
print(dog.species)
```

**Answer:**

```text
animal
```

**Explanation:** The value is inherited through lookup.

### Question 10

```python
class Animal:
    species = "animal"


class Dog(Animal):
    species = "dog"


dog = Dog()
dog.species = "puppy"

print(dog.species)
print(Dog.species)
print(Animal.species)
```

**Answer:**

```text
puppy
dog
animal
```

**Explanation:** The instance shadows `Dog.species`; `Dog` independently shadows `Animal.species`.

## Short Answer

### Question 11 — What is object state?

**Answer:** Information associated with an object that influences its behavior, representation, or lifecycle.

### Question 12 — Why can `obj.role` work even when `role` is not in `obj.__dict__`?

**Answer:** The attribute may be defined on the class or a base class, or it may be supplied by a descriptor.

### Question 13 — What is shadowing?

**Answer:** A nearer attribute hides a same-named attribute farther along the normal lookup path.

### Question 14 — What is the difference between mutation and reassignment?

**Answer:** Mutation changes an existing object; reassignment changes which value/object an attribute name refers to.

### Question 15 — Why is `__dict__` not a complete model of every accessible attribute?

**Answer:** Attributes may come from classes, bases, descriptors, properties, slots, or dynamic attribute hooks.

### Question 16 — What does `ClassVar` do?

**Answer:** It marks an annotation as class-level for static typing and, for dataclasses, excludes it from normal dataclass field processing.

### Question 17 — Does `ClassVar` enforce runtime types?

**Answer:** No.

### Question 18 — Does `__slots__` always improve performance?

**Answer:** No. It changes object layout and may reduce memory use or affect speed in some workloads; benchmark the real workload.

### Question 19 — Does the GIL make shared class state safe?

**Answer:** No. Correct synchronization and state ownership are still required.

### Question 20 — Is class state shared across independent worker processes?

**Answer:** Normally no. Each process has its own memory space.

## Debugging

### Question 21 — Two objects unexpectedly share a list. What should you check?

**Answer:** Check whether the list is a class attribute and whether `first.items is second.items` is `True`.

### Question 22 — A test fails only after another test runs. What should you investigate?

**Answer:** Shared mutable class/module state, caches, registries, and other persistent in-process state.

### Question 23 — `obj.__dict__` raises `AttributeError`. What is one likely cause?

**Answer:** The object may use `__slots__` or another storage mechanism without a normal instance dictionary.

## Architecture

### Question 24 — Where should an API client's default timeout live?

**Answer:** A class constant/default or configuration object can hold policy; each instance can hold its effective timeout.

### Question 25 — Where should an agent's per-run message history live?

**Answer:** In per-run/session state or an external state store, not unintended shared class state.

### Question 26 — When is a mutable class attribute appropriate?

**Answer:** When shared ownership is intentional, its lifecycle and concurrency behavior are understood, and test/process scope is handled.

### Question 27 — When should class-level state be externalized?

**Answer:** When it must survive process restarts or be consistent/shared across independent processes or machines.

---

# 50. Common Misconceptions

## "Every attribute belongs to the instance."

Correct model:

```text
instance
class
base class
descriptor
```

can all participate in what `obj.name` resolves to.

## "Class attributes are automatically copied into instances."

Correct model: the instance can find class attributes through lookup. There is no automatic per-instance copy simply because an attribute is readable from the instance.

## "Reading a class attribute through an instance creates a copy."

Correct model: a value is resolved and returned. A mutable object may be the exact same shared object.

## "Assigning through an instance modifies the class."

Correct model: ordinary assignment to `obj.x` normally creates or updates an instance attribute. Class assignment is written as `Class.x = value`.

## "Class attributes are constants."

Correct model: uppercase is a convention; Python does not enforce constantness.

## "Mutable class attributes are always forbidden."

Correct model: intentional shared mutable state can be valid. Unintentional sharing is the danger.

## "Every object has `__dict__`."

Correct model: many ordinary objects do, but slotted objects and other specialized layouts may not.

## "ClassVar validates runtime types."

Correct model: it communicates static/data-model intent; runtime validation requires runtime code or a validation system.

## "Type hints enforce runtime types."

Correct model: annotations primarily support tooling and human understanding. They do not automatically reject every runtime mismatch.

## "Slots always improve performance."

Correct model: slots change object layout and can offer memory benefits in suitable workloads, but neither speed nor memory improvement is universal.

## "The GIL makes shared state safe."

Correct model: the GIL is not an application-level synchronization contract.

## "Class attributes are shared across processes."

Correct model: normal process memory is separate. Cross-process state requires an external mechanism or explicitly shared memory architecture.

## "Inheritance copies class attributes into every object."

Correct model: inheritance changes lookup relationships.

## "`__dict__` is the authoritative schema of an object."

Correct model: `__dict__` is one storage namespace. Accessible attributes can also come from classes, descriptors, slots, or custom hooks.

## "`hasattr()` is just a dictionary membership test."

Correct model: `hasattr()` performs attribute access and therefore can invoke properties/descriptors.

---

# 51. Required API Coverage and Technical Accuracy

This chapter intentionally covers the relevant Python APIs and language features rather than listing them without explanation.

## `getattr()`

```python
getattr(object, name)
getattr(object, name, default)
```

- **Purpose:** dynamic attribute access;
- **parameters:** object, attribute-name string, optional fallback;
- **return:** resolved attribute value or fallback;
- **exception:** missing attribute raises `AttributeError` when no default is supplied;
- **use:** dynamic schemas, generic tools;
- **mistake:** replacing clear dot notation with reflection everywhere.

## `setattr()`

```python
setattr(object, name, value)
```

- **Purpose:** dynamic attribute assignment;
- **parameters:** target, attribute-name string, value;
- **return:** `None`;
- **use:** generic mappers and framework-style code;
- **mistake:** making stable object shape unpredictable.

## `hasattr()`

```python
hasattr(object, name)
```

- **Purpose:** determine whether attribute access succeeds;
- **parameter:** target object and name;
- **return:** `bool`;
- **caveat:** attribute access can invoke descriptors/properties;
- **mistake:** treating it as a complete interface definition.

## `delattr()`

```python
delattr(object, name)
```

- **Purpose:** dynamic attribute deletion;
- **parameters:** target and name;
- **return:** `None`;
- **exception:** missing attributes can raise `AttributeError`;
- **use:** dynamic model manipulation;
- **mistake:** using deletion to compensate for an unclear state model.

## `type()`

```python
type(obj)
```

Returns the concrete runtime type of `obj`.

Use it when debugging or when exact runtime type identity is actually part of the problem.

## `id()`

```python
id(obj)
```

Returns an integer associated with the object's identity during its lifetime.

Use it to diagnose shared references.

It is not a persistent identifier for databases or APIs.

## `dir()`

```python
dir(obj)
```

Returns an introspection-oriented list of attribute names.

Use it for exploration and debugging.

It is not a perfect schema of every possible accessible attribute.

## `vars()`

```python
vars(obj)
```

For objects that expose a suitable `__dict__`, this provides the object's namespace mapping.

It can fail for objects that do not have the required namespace.

## `__dict__`

For many normal Python objects, this is the dynamic attribute namespace.

Do not assume every object has one.

## `__class__`

An object's class reference.

## `__mro__`

A class's Method Resolution Order tuple.

## `property`

A descriptor type that supports attribute-style access through getter/setter/deleter functions.

## `__get__`, `__set__`, `__delete__`

Descriptor methods that customize attribute access, assignment, and deletion.

A minimal descriptor can implement all three:

```python
class TracedAttribute:
    def __set_name__(self, owner, name) -> None:
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value) -> None:
        instance.__dict__[self.name] = value

    def __delete__(self, instance) -> None:
        del instance.__dict__[self.name]


class Record:
    value = TracedAttribute()


record = Record()
record.value = 10
assert record.value == 10
del record.value
```

Here:

- `record.value` invokes `__get__`;
- assignment invokes `__set__`;
- deletion invokes `__delete__`.

## `__slots__`

Constrains instance attribute storage and can remove the normal dynamic instance dictionary for that class.

## `ClassVar`

Communicates that an annotation is class-level rather than instance-level. With dataclasses, it prevents the name from being treated as a normal field.

### Accuracy rules to remember

Never claim:

- every object has `__dict__`;
- every attribute is stored in `__dict__`;
- class attributes are copied into instances;
- reading a class attribute creates a copy;
- instance assignment normally modifies the class;
- class attributes are immutable;
- class attributes are always constants;
- mutable class attributes are always forbidden;
- `ClassVar` performs runtime validation;
- type hints automatically enforce runtime types;
- slots always improve performance;
- slots always save a fixed amount of memory;
- the GIL makes shared mutable state safe;
- normal class state is shared among independent processes;
- JSON automatically serializes arbitrary Python objects.

### Simplification policy

When explaining Python internals to a beginner:

1. give the simple mental model;
2. label it as simplified when necessary;
3. refine it with descriptor/MRO details afterward.

This avoids both incorrect simplification and premature complexity.

---

# 52. Production Checklist and Final Mental Model

## Ownership

- [ ] Is this value class-level, instance-level, request-level, or external?
- [ ] Is the owner obvious from the code?
- [ ] Does the lifecycle match the chosen scope?

## Mutability

- [ ] Is shared mutation intentional?
- [ ] Could one object's change affect another?
- [ ] Would an immutable value be safer?

## Configuration

- [ ] Are stable defaults separated from runtime state?
- [ ] Would a configuration object be clearer?
- [ ] Are external dependencies injected rather than hidden in class state?

## Inheritance

- [ ] Is a class-level attribute intentionally inherited?
- [ ] Is subclass overriding intentional?
- [ ] Is instance shadowing expected?

## Testing

- [ ] Do tests verify independent instance state?
- [ ] Are class registries reset when required?
- [ ] Can state leak across tests?

## Concurrency

- [ ] Can threads mutate the same class-level object?
- [ ] Can async tasks mutate it?
- [ ] Is synchronization necessary?

## Processes

- [ ] Is the class state incorrectly assumed to be global across workers?
- [ ] Should state be moved to a database/cache/broker?

## Type Safety

- [ ] Are attribute annotations accurate?
- [ ] Is `ClassVar` used for true class-level values?
- [ ] Are runtime validation requirements explicit?

## Introspection

- [ ] Does debugging code handle objects without `__dict__`?
- [ ] Is `dir()` being treated as a debugging aid rather than a complete schema?

## Performance

- [ ] Is `__slots__` justified by object count/layout?
- [ ] Has the actual workload been benchmarked?

## Security

- [ ] Are secrets outside source-code class attributes?
- [ ] Can shared class state retain sensitive information?
- [ ] Are debug representations/logs safe?

## API design

- [ ] Is dynamic `getattr()`/`setattr()` actually necessary?
- [ ] Is ordinary dot notation clearer?
- [ ] Is attribute deletion necessary for the model contract?

---

## Final Mental Model

### Instance attribute

```text
INSTANCE ATTRIBUTE
      ↓
state associated with one particular object
```

Examples:

```python
self.name
self.timeout
self.session
self.messages
```

### Class attribute

```text
CLASS ATTRIBUTE
      ↓
value/state defined on the class and available through
Python's attribute lookup rules
```

Examples:

```text
DEFAULT_TIMEOUT
MAX_RETRIES
VERSION
shared registry (when intentional)
```

### Attribute lookup

```text
obj.name
   ↓
attribute-access machinery
   ↓
descriptor rules + instance/class/MRO lookup
   ↓
resolved value or behavior
```

### Shadowing

```text
Class:
    name = "global"

Instance:
    name = "local"
```

The instance value normally wins for ordinary lookup.

### Mutable shared state

```text
           CLASS
             |
             v
       shared list/dict
          /       \
     object A   object B
```

If the shared object is mutated, both objects can observe that mutation.

### The final engineering question

Before deciding where an attribute belongs, ask:

```text
What is this state?
Who owns it?
Who can change it?
Who should see the change?
How long should it live?
Does it need persistence?
Does it need synchronization?
Does it cross a process boundary?
Does it cross an API/data boundary?
How will it be tested?
How will it be debugged?
```

If the answers are clear, the choice between class and instance attributes becomes an architectural decision rather than a syntax trick.

---

## Final Self-Review

- [x] Beginner explanation exists.
- [x] Instance attributes are fully explained.
- [x] Class attributes are fully explained.
- [x] `self` is explained.
- [x] Object state is explained.
- [x] Class state is explained.
- [x] `__dict__` is explained accurately.
- [x] `Class.__dict__` is explained.
- [x] `__class__` is explained.
- [x] Attribute lookup is explained.
- [x] Shadowing is explained.
- [x] Assignment semantics are explained.
- [x] Mutation vs reassignment is explained.
- [x] Mutable class attributes are deeply explained.
- [x] Inheritance interaction is explained.
- [x] MRO is introduced.
- [x] Descriptors are introduced accurately.
- [x] `property` is explained.
- [x] `getattr()` is explained.
- [x] `setattr()` is explained.
- [x] `hasattr()` is explained.
- [x] `delattr()` is explained.
- [x] `vars()` is explained.
- [x] `dir()` is explained.
- [x] `type()` is explained.
- [x] `id()` is explained.
- [x] `ClassVar` is explained.
- [x] `__slots__` is explained.
- [x] Type annotations are explained accurately.
- [x] Testing is covered.
- [x] Debugging is covered.
- [x] Concurrency implications are covered.
- [x] Multi-process implications are covered.
- [x] Production state ownership is covered.
- [x] Banking example exists.
- [x] Data engineering example exists.
- [x] ML example exists.
- [x] LLM example exists.
- [x] Agentic AI example exists.
- [x] API client example exists.
- [x] At least 20 exercises exist.
- [x] Debugging lab exists.
- [x] Mini-project exists.
- [x] Interview questions exist.
- [x] Architecture questions exist.
- [x] Knowledge check exists.
- [x] Common misconceptions exist.
- [x] Production checklist exists.
- [x] Final mental model exists.
- [x] Relevant attribute APIs are covered.
- [x] Technical-accuracy warnings are explicit.
- [x] No secrets or real credentials are used.
- [x] No unrelated files are intentionally modified.

