# Lesson 04 — Operator Overloading and Numeric Protocols

**Stage:** 1 — Programming & Computational Thinking  
**Module:** 11 — Advanced Python Data Model and Object Design  
**Target:** Python 3.12+  
**Audience:** Learners moving from Python fundamentals toward production Data Engineering and AI Engineering

> **Roadmap alignment:** This lesson follows `roadmap-Advanced-Python-Data-Model-and-Object-Design.md`, Lesson 04. It covers operator-to-dunder mappings, unary operators, non-mutating arithmetic, reflected and in-place operations, `NotImplemented`, conversion methods, bitwise operators and flags, matrix multiplication, numeric interoperability, `__divmod__`, modular `__pow__`, operator-based DSLs, NumPy interoperability awareness, immutable value objects, and performance trade-offs.

---

## 1. Learning outcomes

By the end of this lesson, you should be able to:

1. Explain how expressions such as `left + right`, `-value`, and `value @ matrix` dispatch to special methods.
2. Implement readable arithmetic for a small value object without unexpectedly mutating operands.
3. Distinguish direct methods (`__add__`), reflected methods (`__radd__`), and in-place methods (`__iadd__`).
4. Return `NotImplemented` for unsupported operand types and explain how Python resolves the operation.
5. Implement scalar multiplication and support useful mixed operand orders.
6. Explain why `sum()` commonly requires a suitable `__radd__` or an explicit `start` value.
7. Use conversion methods such as `__int__`, `__float__`, `__complex__`, `__round__`, `__index__`, and `__bool__` appropriately.
8. Use bitwise operations and `enum.Flag` for flags rather than inventing unclear meanings for operators.
9. Recognize the numeric tower and the practical differences among `int`, `float`, `Fraction`, and `Decimal`.
10. Explain why `Decimal + float` raises `TypeError`, and choose a deliberate numeric policy.
11. Implement `__divmod__` and understand the three-argument form of `pow()`.
12. Decide when an operator-based API is clear, and when a named method is safer.
13. Recognize NumPy's `__array__` and `__array_ufunc__` as advanced interoperability hooks.
14. Identify temporary-object and per-element Python overhead, and know when to measure or vectorize.

## 2. Prerequisites and setup

You should already understand classes, instance attributes, type annotations, exceptions, and the basics of special methods from the previous lessons. The earlier lessons on `__repr__`, equality, hashing, and comparisons are useful context, but you do not need to have memorized every special method.

Use Python 3.12 or newer. Examples that use `pytest` require it to be installed in your development environment:

```bash
python --version
python -m pip install pytest
```

Save the examples in a `.py` file or run each self-contained code block in a Python interpreter. The code blocks in this lesson are designed to be runnable independently unless explicitly labelled as a shell command.

## 3. The central idea: make objects work naturally with Python syntax

Operator overloading lets a class define what familiar syntax means for its instances. For example:

- `Vector(1, 2) + Vector(3, 4)` can mean component-wise vector addition.
- `Money(10) * 3` can mean scaling a monetary amount by a count.
- `Path("data") / "events.csv"` means path composition.
- `matrix_a @ matrix_b` means matrix multiplication.
- `permission_a | permission_b` can combine permission flags.

Python does not infer these meanings. It uses special methods implemented by the operand types. The important design rule is **semantic restraint**: use an operator only when its meaning will be obvious to another Python developer.

A custom `+` should act like addition in the domain. Do not use `+` to send an email, execute a database query, or trigger an unrelated side effect. Named methods are usually clearer for operations that are not naturally arithmetic or algebraic.

## 4. Operator-to-method reference

### 4.1 Common binary operators

| Expression | Primary special method | Reflected counterpart | Typical meaning |
|---|---|---|---|
| `a + b` | `a.__add__(b)` | `b.__radd__(a)` | Addition / combination |
| `a - b` | `a.__sub__(b)` | `b.__rsub__(a)` | Subtraction |
| `a * b` | `a.__mul__(b)` | `b.__rmul__(a)` | Multiplication / scaling |
| `a / b` | `a.__truediv__(b)` | `b.__rtruediv__(a)` | True division |
| `a // b` | `a.__floordiv__(b)` | `b.__rfloordiv__(a)` | Floor division |
| `a % b` | `a.__mod__(b)` | `b.__rmod__(a)` | Remainder |
| `a ** b` | `a.__pow__(b)` | `b.__rpow__(a)` | Exponentiation |
| `a @ b` | `a.__matmul__(b)` | `b.__rmatmul__(a)` | Matrix multiplication |
| `a divmod b` | `a.__divmod__(b)` | `b.__rdivmod__(a)` | Quotient and remainder |
| `a & b` | `a.__and__(b)` | `b.__rand__(a)` | Bitwise AND / set-like operation |
| `a \| b` | `a.__or__(b)` | `b.__ror__(a)` | Bitwise OR / set-like operation |
| `a ^ b` | `a.__xor__(b)` | `b.__rxor__(a)` | Bitwise XOR |
| `a << b` | `a.__lshift__(b)` | `b.__rlshift__(a)` | Left shift |
| `a >> b` | `a.__rshift__(b)` | `b.__rrshift__(a)` | Right shift |

The expression `a + b` is not literally implemented as a simple Python-level call to `a.__add__(b)` in every situation. Python follows the binary operator dispatch rules, including subtype priority and reflected methods. The table is a useful mental model, not the complete dispatch algorithm.

### 4.2 In-place operators

| Expression | In-place method |
|---|---|
| `a += b` | `a.__iadd__(b)` |
| `a -= b` | `a.__isub__(b)` |
| `a *= b` | `a.__imul__(b)` |
| `a /= b` | `a.__itruediv__(b)` |
| `a //= b` | `a.__ifloordiv__(b)` |
| `a %= b` | `a.__imod__(b)` |
| `a **= b` | `a.__ipow__(b)` |
| `a @= b` | `a.__imatmul__(b)` |
| `a &= b`, `a \|= b`, `a ^= b` | `__iand__`, `__ior__`, `__ixor__` |
| `a <<= b`, `a >>= b` | `__ilshift__`, `__irshift__` |

If an in-place method is absent or returns `NotImplemented`, Python can fall back to the ordinary binary operation and rebind the left-hand variable to the result. Therefore, `x += y` does **not** universally mean “mutate the existing object.”

### 4.3 Unary operators

| Expression | Method | Typical meaning |
|---|---|---|
| `-x` | `__neg__` | Negation |
| `+x` | `__pos__` | Unary plus / normalized positive value |
| `abs(x)` | `__abs__` | Magnitude |
| `~x` | `__invert__` | Bitwise inversion |

Unary operators generally operate on one object and return a result. Their return types depend on the domain: `abs(Vector(...))` may return a scalar, while `-Vector(...)` should return another vector.

## 5. Start with a small immutable `Vector`

A vector is a useful first example because its operations have familiar mathematical meanings. This version is intentionally small and supports addition, scalar multiplication, magnitude, and a useful representation.

```python
from __future__ import annotations

from math import hypot


class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: object) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: object) -> Vector:
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector(self.x * scalar, self.y * scalar)

    def __abs__(self) -> float:
        return hypot(self.x, self.y)

    def __neg__(self) -> Vector:
        return Vector(-self.x, -self.y)

    def __repr__(self) -> str:
        return f"Vector({self.x!r}, {self.y!r})"


left = Vector(1, 2)
right = Vector(3, 4)
print(left + right)  # Vector(4.0, 6.0)
print(left * 3)      # Vector(3.0, 6.0)
print(abs(right))    # 5.0
print(-left)         # Vector(-1.0, -2.0)
print(left)          # Vector(1.0, 2.0): unchanged by addition
```

### What this example teaches

- `__add__` defines the class's meaning for `+`.
- Returning a new `Vector` keeps the original operands unchanged.
- Unsupported operands return `NotImplemented` rather than pretending to add unrelated types.
- `__abs__` can return a scalar even though the original object is a vector.
- The `__repr__` method makes examples and debugging output understandable.

**Design note:** The example is pedagogical, not a complete industrial vector implementation. It accepts `bool` because `bool` is a subclass of `int`, and it converts coordinates to `float`; a stricter production API may choose to reject booleans and define a more explicit numeric policy.

## 6. `NotImplemented` is part of operator negotiation

`NotImplemented` is a special singleton used by binary special methods to say, “This operand combination is not supported by this implementation; let Python try the other dispatch path.” It is not the same as `NotImplementedError`.

- Return `NotImplemented` when the type combination is unsupported.
- Raise a specific exception when the operand types are supported but the supplied value violates a domain rule (for example, a negative quantity that the domain forbids).
- Do not return `None` to signal unsupported arithmetic. `None` is an ordinary return value and usually leads to confusing behavior.

```python
class Identifier:
    def __init__(self, value: str) -> None:
        self.value = value

    def __add__(self, other: object) -> object:
        if not isinstance(other, Identifier):
            return NotImplemented
        return Identifier(self.value + other.value)

    def __repr__(self) -> str:
        return f"Identifier({self.value!r})"


print(Identifier("job-") + Identifier("42"))

try:
    Identifier("job-") + 42
except TypeError as exc:
    print(type(exc).__name__)
```

The final `TypeError` is produced because neither applicable operand implementation accepted the operation. Returning `NotImplemented` gives Python a chance to resolve the operation consistently rather than forcing a premature error inside one operand's method.

## 7. Reflected operators: support the other operand order

A direct method is associated with the left operand; a reflected method gives the right operand a chance to handle the expression. Reflected methods are especially useful when a custom value should interact with built-in numeric types.

For example, implementing only `Vector.__mul__` may support `vector * 3` but not `3 * vector`. `__rmul__` provides the reflected behavior.

```python
from __future__ import annotations

from math import hypot


class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)

    def __mul__(self, scalar: object) -> Vector:
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: object) -> Vector:
        return self * scalar

    def __repr__(self) -> str:
        return f"Vector({self.x!r}, {self.y!r})"


vector = Vector(2, 5)
print(vector * 3)  # Vector(6.0, 15.0)
print(3 * vector)  # Vector(6.0, 15.0)
```

For scalar multiplication, the meaning is symmetric, so forwarding `__rmul__` to `__mul__` is appropriate. This pattern is not universally valid: subtraction and division are order-sensitive, so their reflected implementations must preserve the correct operand order.

### 7.1 Operand dispatch order and subclass priority

At a high level, Python tries the left operand's implementation and may try the right operand's reflected implementation. There is an important refinement: if the right operand's type is a strict subclass of the left operand's type and supplies a distinct reflected implementation, that reflected implementation can be given priority. This lets a more specialized subtype control operations involving its instances.

Do not build application logic around a simplistic “left always wins” rule. Return `NotImplemented` for unsupported combinations, and test operations with both operand orders and relevant subclasses.

```python
class BaseValue:
    def __add__(self, other: object) -> str | object:
        if not isinstance(other, BaseValue):
            return NotImplemented
        return "BaseValue.__add__"


class SpecialValue(BaseValue):
    def __radd__(self, other: object) -> str | object:
        if isinstance(other, BaseValue):
            return "SpecialValue.__radd__"
        return NotImplemented


print(BaseValue() + SpecialValue())
```

The result demonstrates the subclass's reflected method taking priority. The exact dispatch rules are documented by Python's data model; the practical lesson is to implement and test both sides intentionally.

## 8. Implementing `__radd__` correctly: `sum()`

The built-in `sum()` starts with `0` by default. For a list of custom values, it effectively needs to combine the initial value with the first element, then accumulate the remaining elements. A custom class that supports adding only another instance may therefore fail at the initial `0 + first_value` step.

```python
from __future__ import annotations


class Vector:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: object) -> Vector:
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __radd__(self, other: object) -> Vector:
        if other == 0:
            return self
        return self.__add__(other)

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"


vectors = [Vector(1, 1), Vector(2, 2), Vector(3, 3)]
print(sum(vectors))  # Vector(6, 6)
```

Returning `self` for the additive identity `0` is safe in this example because `Vector` does not mutate itself during addition. A more explicit alternative is to pass a `Vector` start value to `sum()`:

```python
class Vector:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: object) -> "Vector":
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __radd__(self, other: object) -> "Vector":
        if other == 0:
            return self
        return self.__add__(other)

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"


vectors = [Vector(1, 1), Vector(2, 2)]
total = sum(vectors, start=Vector(0, 0))
print(total)  # Vector(3, 3)
```

**Production guidance:** Prefer an explicit `start` value when it communicates the domain clearly. If you want `sum(values)` to work naturally, define the zero/additive-identity behavior deliberately and test it. Do not accept every integer as a valid identity merely to make `sum()` work.

## 9. In-place operations: `__iadd__` and friends

In-place operators can be efficient for mutable objects, but mutation affects aliases. If an object is immutable, it is usually more appropriate for `+=` to create a new value or to rely on the fallback to `__add__`.

### 9.1 A mutable vector with `__iadd__`

```python
from __future__ import annotations


class MutableVector:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: object) -> MutableVector:
        if not isinstance(other, MutableVector):
            return NotImplemented
        return MutableVector(self.x + other.x, self.y + other.y)

    def __iadd__(self, other: object) -> MutableVector:
        if not isinstance(other, MutableVector):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        return self

    def __repr__(self) -> str:
        return f"MutableVector({self.x}, {self.y})"


first = MutableVector(1, 2)
alias = first
first += MutableVector(10, 20)
print(first)       # MutableVector(11, 22)
print(alias)       # MutableVector(11, 22): same object was mutated
print(first is alias)  # True
```

### 9.2 `list +=` versus `tuple +=`

```python
values = [1, 2]
alias = values
values += [3]
print(values)        # [1, 2, 3]
print(alias)         # [1, 2, 3]
print(values is alias)  # True

items = (1, 2)
alias_tuple = items
items += (3,)
print(items)             # (1, 2, 3)
print(alias_tuple)       # (1, 2)
print(items is alias_tuple)  # False
```

Lists are mutable and their in-place addition extends the existing list. Tuples are immutable, so `+=` creates a new tuple and rebinds the variable. This difference matters when data structures are shared across pipeline stages or passed into helper functions.

### 9.3 If `__iadd__` is absent

When an object has no applicable `__iadd__`, Python falls back to the ordinary addition protocol and reassigns the result to the left-hand target. For immutable value objects, this often produces the expected behavior without writing an in-place method.

Do not implement `__iadd__` merely because the operator exists. First decide whether the type is mutable, what aliasing means, and whether mutation is an expected part of the API.

## 10. Conversion and interpretation protocols

These methods connect custom objects to built-in conversion and truth-testing operations.

| Built-in / expression | Special method | Intended contract |
|---|---|---|
| `int(x)` | `__int__` | Explicit integer conversion |
| `float(x)` | `__float__` | Explicit floating-point conversion |
| `complex(x)` | `__complex__` | Explicit complex conversion |
| `round(x)` / `round(x, n)` | `__round__` | Rounding semantics |
| `list[index]` / `range(index)` | `__index__` | Exact integer-like value for indexing |
| `bool(x)` / `if x:` | `__bool__` | Truth value |

`__index__` is not a general “convert anything to an integer” method. It represents an exact integer-like value used by operations that require an integer index. For example, `int(3.7)` truncates to `3`, but a float is not accepted as a list index. If your object represents an index, `__index__` should return an `int` and should not silently round or truncate a non-integral value.

```python
class BatchIndex:
    def __init__(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("value must be an integer, not bool")
        self.value = value

    def __index__(self) -> int:
        return self.value


records = ["batch-A", "batch-B", "batch-C"]
index = BatchIndex(1)
print(records[index])  # batch-B
print(range(index))   # range(0, 1)
```

### 10.1 Conversion methods should be unsurprising

A conversion should preserve the meaning of the domain. Converting a `Money` object to `float` may lose precision; converting a `Duration` to `int` might need a documented unit such as seconds. Do not implement conversions simply because they are possible. If a conversion is ambiguous, prefer a named method such as `to_minor_units()` or `to_seconds()`.

```python
class DurationSeconds:
    def __init__(self, seconds: int) -> None:
        if isinstance(seconds, bool) or not isinstance(seconds, int):
            raise TypeError("seconds must be an integer")
        self.seconds = seconds

    def __int__(self) -> int:
        return self.seconds

    def __bool__(self) -> bool:
        return self.seconds != 0


print(int(DurationSeconds(12)))   # 12
print(bool(DurationSeconds(0)))   # False
print(bool(DurationSeconds(12)))  # True
```

An object's truthiness should be defined consistently. If you implement `__bool__`, it must return `True` or `False`. If `__bool__` is absent, Python may use `__len__` to determine truthiness for container-like objects; otherwise instances are generally truthy by default.

## 11. Bitwise operators and `enum.Flag`

Bitwise operators (`&`, `|`, `^`, `~`, `<<`, `>>`) are appropriate for integer bit patterns, masks, and flag combinations. They are also used by some libraries for set-like or vectorized operations. The meaning should remain intuitive in the domain.

Python's `enum.Flag` is a safer way to model a finite set of combinable options than manually assigning unexplained integers.

```python
from enum import Flag, auto


class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


allowed = Permission.READ | Permission.WRITE
print(Permission.READ in allowed)       # True
print(Permission.EXECUTE in allowed)    # False
print(allowed & Permission.WRITE)       # Permission.WRITE
```

The exact numeric values generated by `auto()` are an implementation detail of the enum's value generation; use the symbolic members in application code. In an `IntFlag`, members are also integer-compatible, which can be useful for bitmasks that cross an external interface, but it is still important to validate values at system boundaries.

Avoid overloading `&` or `|` for a meaning that readers would not associate with intersection, union, or combination. The same caution applies to `>>` for function composition: it can be elegant in a deliberately designed DSL, but may surprise maintainers in ordinary business code.

## 12. Matrix multiplication and `@`

The `@` operator was added to support matrix multiplication without confusing it with element-wise multiplication (`*`). A custom type can implement `__matmul__` and, if useful, `__rmatmul__` and `__imatmul__`.

The following minimal example shows the protocol shape for a two-dimensional matrix. It is illustrative, not a replacement for NumPy: it omits many validations, numerical considerations, and performance optimizations.

```python
from __future__ import annotations


class Matrix2x2:
    def __init__(self, rows: tuple[tuple[float, float], tuple[float, float]]) -> None:
        self.rows = rows

    def __matmul__(self, other: object) -> Matrix2x2:
        if not isinstance(other, Matrix2x2):
            return NotImplemented
        a, b = self.rows
        c, d = other.rows
        return Matrix2x2((
            (a[0] * c[0] + a[1] * d[0], a[0] * c[1] + a[1] * d[1]),
            (b[0] * c[0] + b[1] * d[0], b[0] * c[1] + b[1] * d[1]),
        ))

    def __repr__(self) -> str:
        return f"Matrix2x2({self.rows!r})"


left = Matrix2x2(((1, 2), (3, 4)))
right = Matrix2x2(((5, 6), (7, 8)))
print(left @ right)
```

In scientific computing, `@` commonly means matrix multiplication, whereas `*` may mean element-wise multiplication for array-like objects. Follow the conventions of the ecosystem your type integrates with.

## 13. The numeric tower and interoperability

Python has several built-in and standard-library numeric types, each with different semantics:

- `int`: arbitrary-precision integers, subject to memory and performance limits.
- `float`: usually IEEE 754 binary floating-point; many decimal fractions are approximations.
- `fractions.Fraction`: rational values represented exactly as a numerator and denominator.
- `decimal.Decimal`: decimal arithmetic with configurable precision and rounding behavior.
- `complex`: complex numbers with real and imaginary components.

The `numbers` module defines abstract base classes such as `Number`, `Complex`, `Real`, `Rational`, and `Integral`. These classes help express broad numeric categories, but registering with or subclassing an ABC does not automatically guarantee that every operator combination will work correctly. Your methods still need clear contracts.

```python
from fractions import Fraction
from numbers import Number, Real
from decimal import Decimal


values = [10, 2.5, Fraction(1, 3), Decimal("1.25"), 2 + 3j]
for value in values:
    print(type(value).__name__, isinstance(value, Number))

print(isinstance(10, Real))
print(isinstance(2.5, Real))
print(isinstance(2 + 3j, Real))
```

The `numbers` ABCs are classification tools, not a promise that arbitrary mixed arithmetic is safe. In particular, `Decimal` deliberately does not freely mix with `float` for arithmetic.

### 13.1 Why `Decimal + float` raises

```python
from decimal import Decimal


amount = Decimal("0.10")
rate = 0.2

try:
    print(amount + rate)
except TypeError as exc:
    print(type(exc).__name__)
```

`Decimal` is designed for decimal arithmetic with explicit precision and rounding. Silently combining it with a binary floating-point approximation would make the numeric policy ambiguous, so Python raises `TypeError`. Convert at the boundary from a deliberate representation rather than trying to hide the mismatch inside a generic operator.

```python
from decimal import Decimal


# Prefer constructing Decimal from text when the source is a decimal amount.
amount = Decimal("0.10")
rate = Decimal("0.20")
print(amount + rate)  # 0.30

# If a float already exists, Decimal(str(value)) uses its readable decimal
# representation. This is a policy choice, not recovery of the original input.
rate_from_float = Decimal(str(0.2))
print(rate_from_float)  # 0.2
```

### 13.2 Do not use binary floats for exact monetary arithmetic

```python
from decimal import Decimal
from fractions import Fraction


print(0.1 + 0.2)                       # 0.30000000000000004
print(Decimal("0.1") + Decimal("0.2"))  # 0.3
print(Fraction(1, 10) + Fraction(2, 10))  # 3/10
```

Use `Decimal` or integer minor units when business requirements demand decimal monetary semantics. Use `Fraction` when exact rational arithmetic is needed. Use `float` for numerical workloads where binary floating-point behavior is expected and acceptable. Avoid designing custom operators that silently convert among these types without a clearly documented policy.

## 14. `__divmod__` and modular exponentiation

`divmod(a, b)` asks for quotient and remainder together. A custom numeric type can implement `__divmod__` (and, when appropriate, `__rdivmod__`) to preserve its domain semantics.

```python
class Minutes:
    def __init__(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("value must be an integer")
        self.value = value

    def __divmod__(self, other: object) -> tuple[int, int]:
        if not isinstance(other, Minutes):
            return NotImplemented
        if other.value == 0:
            raise ZeroDivisionError("cannot divide by zero minutes")
        return divmod(self.value, other.value)


quotient, remainder = divmod(Minutes(17), Minutes(5))
print(quotient, remainder)  # 3 2
```

This example returns plain integers because its stated operation is a quotient/remainder pair. A production type should document the result types and units; if returning a tuple of custom quantities would be more meaningful, implement that contract instead.

The built-in `pow(base, exponent, modulus)` supports modular exponentiation for integer-compatible values. For custom numeric types, `__pow__` may receive a third `modulo` argument. If the type does not support the three-argument form, it should reject it clearly rather than accidentally ignore the modulus.

```python
print(pow(2, 10, 17))  # 4
```

A custom class can receive the optional modulus as the third argument to `__pow__`. This small example supports integer exponents and the integer modular form; a production numeric type should document its supported combinations explicitly.

```python
class ModularInt:
    def __init__(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("value must be an integer")
        self.value = value

    def __pow__(self, exponent: object, modulo: object = None) -> object:
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            return NotImplemented
        if modulo is None:
            return ModularInt(self.value ** exponent)
        if isinstance(modulo, bool) or not isinstance(modulo, int):
            return NotImplemented
        return pow(self.value, exponent, modulo)

    def __repr__(self) -> str:
        return f"ModularInt({self.value})"


print(pow(ModularInt(2), 10))      # ModularInt(1024)
print(pow(ModularInt(2), 10, 17))  # 4
```

The three-argument form computes modular exponentiation efficiently and is not equivalent to computing `2 ** 10` first and then taking `% 17` for all possible large inputs in terms of resource use. For security-sensitive cryptographic operations, use vetted cryptographic libraries rather than implementing cryptography with a custom numeric class.

## 15. Immutable value objects and frozen dataclasses

Arithmetic is often easiest to reason about when a value object is immutable: an operation returns a new value rather than changing an existing one. This reduces aliasing surprises and makes values safer to share across functions, tasks, and pipeline stages.

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pixel:
    x: int
    y: int

    def __add__(self, other: object) -> Pixel:
        if not isinstance(other, Pixel):
            return NotImplemented
        return Pixel(self.x + other.x, self.y + other.y)


first = Pixel(2, 3)
second = first + Pixel(4, 5)
print(first)   # Pixel(x=2, y=3)
print(second)  # Pixel(x=6, y=8)
```

`frozen=True` prevents ordinary attribute assignment after initialization; it does not make every nested object deeply immutable. If a frozen dataclass contains a mutable list, that list can still be mutated. For a truly value-like type, prefer immutable fields or defensively copy/normalize inputs.

For data engineering, immutable configuration values, partition identifiers, schema coordinates, and domain measurements can reduce accidental cross-stage mutation. Immutability does not replace validation or transaction boundaries, but it helps make local behavior predictable.

## 16. Operator-based DSLs: useful, but use restraint

Some libraries use operators to build domain-specific languages (DSLs):

- `Path("data") / "events.csv"` composes a path.
- `tensor_a @ tensor_b` performs matrix multiplication.
- `Permission.READ | Permission.WRITE` combines flags.
- A query library may use comparison and bitwise operators to build expressions.

A pipeline DSL might choose `|` or `>>` for composition. That can be appropriate if the library defines the grammar consistently, documents precedence, and gives operators one obvious meaning. In a general-purpose application, `compose()`, `pipe()`, or `join_path()` may be clearer.

Before overloading an operator, ask:

1. Is this meaning familiar to Python developers?
2. Does it preserve expected operand order and result type?
3. Will the operation be surprising when used with built-in types?
4. Is operator precedence intuitive for expressions users will write?
5. Can the behavior be explained in one sentence and tested for both operand orders?
6. Would a named method communicate the intention better?

Avoid operator overloading that causes hidden I/O, mutates unexpectedly, or changes meaning based on subtle ambient state.

## 17. NumPy interoperability awareness: `__array__` and `__array_ufunc__`

NumPy supports advanced integration hooks for custom array-like objects:

- `__array__` lets an object participate in conversion to a NumPy array, with behavior that depends on the method signature and NumPy version.
- `__array_ufunc__` allows a custom object to control how NumPy universal functions (ufuncs) interact with it.

These hooks are beyond a first implementation of arithmetic dunder methods. Their purpose is to coordinate behavior with NumPy operations such as `numpy.add`, not simply to provide an alias for `__add__`. Interoperability involves dtype, shape, broadcasting, ownership, coercion, and dispatch rules. Check the supported NumPy version's documentation before implementing these hooks in a library.

Do not implement a speculative `__array__` method that eagerly materializes a large or lazy data source without documenting the memory cost. In data engineering and machine learning, implicit conversion can accidentally turn a distributed or lazy computation into a large in-memory operation.

## 18. Performance: temporary objects and vectorization

Operator overloads can make code elegant, but each operation may create a new object. A chain such as `a + b + c + d` can allocate intermediate values. In numeric workloads, looping over Python objects one element at a time can be far slower than using vectorized operations in a library designed for contiguous arrays or tensors.

The right approach depends on the workload:

- Prefer clarity and correctness first.
- Measure with representative data before optimizing.
- For large numerical arrays, consider NumPy, pandas, or the relevant tensor framework's vectorized operations.
- Use in-place operations only when mutation semantics are safe and the library's API supports them correctly.
- Consider allocation pressure, peak memory, and object lifetime as well as CPU time.
- Do not assume that implementing `__iadd__` makes a type faster; profile the actual code path.

```python
from timeit import timeit


values = list(range(1000))

list_comprehension_time = timeit("[value * 2 for value in values]", globals=globals(), number=1000)
map_time = timeit("list(map(lambda value: value * 2, values))", globals=globals(), number=1000)
print(round(list_comprehension_time, 4), round(map_time, 4))
```

The timings depend on the Python build, machine, and workload. This snippet is a demonstration of measurement, not a claim that one form is always faster. For meaningful comparisons, run repeated measurements under controlled conditions and benchmark the actual production workload.

## 19. Common mistakes and how to avoid them

| Mistake | Why it is a problem | Better approach |
|---|---|---|
| Mutating `self` inside `__add__` | Violates normal expectations and surprises aliases | Return a new value for ordinary arithmetic |
| Forgetting reflected methods | `3 * vector` or `sum(values)` may fail | Implement `__rmul__`/`__radd__` where semantics justify them |
| Raising `TypeError` immediately for every unknown operand | Prevents Python from trying reflected dispatch | Return `NotImplemented` for unsupported type combinations |
| Returning `None` for unsupported operations | `None` is treated as a result, not a dispatch signal | Return `NotImplemented` |
| Treating `NotImplemented` as `NotImplementedError` | They have different meanings | Use the singleton in operator methods; reserve exceptions for actual failures |
| Implementing `__iadd__` without considering aliases | Other references may observe mutation | Document mutability and test alias behavior |
| Mixing `Decimal` and `float` casually | Precision and conversion policies become unclear | Normalize inputs to a deliberate numeric representation |
| Accepting arbitrary types via silent coercion | Can hide domain bugs | Define explicit supported operand types and conversion rules |
| Overloading `+` for an unrelated action | Code becomes difficult to read | Use a named method for non-arithmetic actions |
| Using `__index__` for truncating conversion | Index protocols require exact integer semantics | Use `__int__` for explicit conversion and `__index__` only for index-like values |
| Assuming `__array__` is harmless | May materialize a large dataset or lose laziness | Document conversion behavior and memory costs |
| Optimizing before measuring | Adds complexity without proven benefit | Benchmark representative workloads first |

## 20. Production case study: a small `Money` value object

Money is a useful example because it demonstrates why operator design must include domain rules, not just method names. The implementation below stores integer minor units (for example, cents) and a currency code. It supports addition only between matching currencies and integer multiplication. It deliberately rejects floating-point multiplication to avoid silent rounding policy.

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    minor_units: int
    currency: str = "USD"

    def __post_init__(self) -> None:
        if isinstance(self.minor_units, bool) or not isinstance(self.minor_units, int):
            raise TypeError("minor_units must be an integer")
        if not self.currency or self.currency.strip() != self.currency:
            raise ValueError("currency must be a non-empty, trimmed code")

    def __add__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("cannot add different currencies")
        return Money(self.minor_units + other.minor_units, self.currency)

    def __mul__(self, factor: object) -> Money:
        if isinstance(factor, bool) or not isinstance(factor, int):
            return NotImplemented
        return Money(self.minor_units * factor, self.currency)

    def __rmul__(self, factor: object) -> Money:
        return self * factor

    def __repr__(self) -> str:
        return f"Money({self.minor_units}, {self.currency!r})"


subtotal = Money(1250, "USD") + Money(375, "USD")
print(subtotal)       # Money(1625, 'USD')
print(3 * subtotal)   # Money(4875, 'USD')
```

Important choices:

- The representation stores minor units, avoiding binary floating-point for the amount itself.
- Adding a different currency is a domain error, so it raises `ValueError` rather than returning `NotImplemented`. Both operands are valid `Money` objects, but the requested operation violates the domain rule.
- Unsupported operand types return `NotImplemented` so Python can try reflected dispatch.
- Multiplication accepts integers only. A production financial system may need decimal quantities, tax rules, explicit rounding modes, exchange rates, currency metadata, and auditability; this simple class does not claim to implement those policies.
- Currency conversion should be a named operation with an explicit exchange-rate source and timestamp, not an implicit side effect of `+`.

## 21. Testing operator contracts with `pytest`

Operator tests should cover correct results, unsupported types, both operand orders where supported, immutability, invalid domain combinations, and edge cases. The following tests are self-contained and can be saved as `test_operator_lesson.py`.

```python
from dataclasses import dataclass
import pytest


@dataclass(frozen=True)
class Money:
    minor_units: int
    currency: str = "USD"

    def __add__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("currency mismatch")
        return Money(self.minor_units + other.minor_units, self.currency)

    def __mul__(self, factor: object) -> "Money":
        if isinstance(factor, bool) or not isinstance(factor, int):
            return NotImplemented
        return Money(self.minor_units * factor, self.currency)

    def __rmul__(self, factor: object) -> "Money":
        return self * factor


def test_addition_returns_new_value_and_preserves_inputs() -> None:
    first = Money(100)
    second = Money(250)
    result = first + second
    assert result == Money(350)
    assert first == Money(100)
    assert second == Money(250)
    assert result is not first


def test_reflected_multiplication() -> None:
    assert 3 * Money(125) == Money(375)


def test_unsupported_type_raises_type_error_after_dispatch() -> None:
    with pytest.raises(TypeError):
        Money(100) + 5


def test_currency_mismatch_is_domain_error() -> None:
    with pytest.raises(ValueError, match="currency mismatch"):
        Money(100, "USD") + Money(100, "EUR")


def test_float_multiplication_is_not_silently_accepted() -> None:
    with pytest.raises(TypeError):
        Money(100) * 1.5
```

Run the tests with:

```bash
python -m pytest -q test_operator_lesson.py
```

Expected result: five tests pass. Tests should validate externally observable behavior, not merely assert that a special method exists.

## 22. Additional test ideas for a production class

Extend the suite based on your domain:

- Test zero, negative values, and very large integers.
- Test `sum()` with and without an explicit start value if accumulation is supported.
- Test both `a + b` and `b + a` when addition is intended to be commutative.
- Test that subtraction and division preserve operand order.
- Test that unsupported operations produce a useful `TypeError` at the expression boundary.
- Test in-place operations with aliases if the class is mutable.
- Test conversions such as `int(value)` and `float(value)` only if those conversions are part of the public API.
- Test the exact rounding policy for decimal quantities.
- Test interoperability with `Decimal`, `Fraction`, or third-party numeric types only if you explicitly support them.
- Test NumPy interoperability against the supported NumPy versions if you implement array hooks.

Do not assert that every conceivable type combination must work. A safe, documented rejection is often better than ambiguous coercion.

## 23. Exercises

Try these before reading the solutions. Use Python 3.12+ and write tests for each implementation.

### Exercise 1 — Complete scalar multiplication

Implement `__mul__` and `__rmul__` for a two-dimensional `Vector`. It should support `vector * 3` and `3 * vector`, return a new vector, and reject unsupported operands through `NotImplemented`.

### Exercise 2 — Explain `sum()` failure

Create a `Vector` class that adds only another `Vector`. Explain why `sum([Vector(1, 1), Vector(2, 2)])` fails, then fix it using either a suitable `__radd__` or an explicit `start` value.

### Exercise 3 — Mutation and aliasing

Create a mutable vector with `__iadd__`. Bind two names to the same instance, apply `+=`, and show what both names observe. Then explain how an immutable implementation should behave.

### Exercise 4 — Design a unit-aware duration

Create a `Duration` value object stored in integer milliseconds. Implement addition for durations and reject other operand types. Should multiplying a duration by a float be allowed? Document and test your chosen policy.

### Exercise 5 — Decimal policy

Write a small function that accepts decimal amounts from text and uses `Decimal`. Demonstrate why constructing `Decimal` from a string is preferable to passing a float directly when the original intent is decimal text.

### Exercise 6 — Flags

Define `Access` using `enum.Flag` with `READ`, `WRITE`, and `ADMIN`. Combine two flags and test membership. Explain why `|` is more readable than manually adding integer constants.

### Exercise 7 — Matrix multiplication

Implement `__matmul__` for a small fixed-size matrix type. Validate dimensions and return `NotImplemented` for an unsupported operand type. Write tests for a valid product and an invalid shape.

### Exercise 8 — Operator restraint review

Consider a class where `a + b` sends `a`'s contents to `b` over a network. Explain why a named method is likely a better API. Identify at least three design or debugging risks of hidden I/O inside an arithmetic operator.

## 24. Exercise solutions and guidance

### Solution 1 — Scalar multiplication

```python
from __future__ import annotations


class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)

    def __mul__(self, scalar: object) -> "Vector":
        if isinstance(scalar, bool) or not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: object) -> "Vector":
        return self * scalar

    def __repr__(self) -> str:
        return f"Vector({self.x!r}, {self.y!r})"


v = Vector(2, 4)
assert (v * 3).x == 6 and (v * 3).y == 12
assert (3 * v).x == 6 and (3 * v).y == 12
assert (v.x, v.y) == (2.0, 4.0)  # Original value is unchanged.
```

The last assertion only checks that the object is equal to itself; it does not prove two separately created vectors compare by value. For a production value object, implement equality deliberately (or use an appropriate dataclass) and test it. The important operator lessons are the reflected method and returning a new instance.

### Solution 2 — `sum()`

`sum()` starts from integer zero by default, so the first operation is effectively `0 + first_vector`. If `Vector.__radd__` does not accept zero and `Vector.__add__` only accepts another vector, the operation fails. A deliberate `__radd__` can recognize zero as the additive identity, or the caller can write `sum(vectors, start=Vector(0, 0))`.

### Solution 3 — Aliasing

If `__iadd__` mutates the current instance, all references to that instance observe the change. For an immutable vector, `+=` should instead produce a new vector and rebind the variable; any alias to the original should continue to point at the original value.

### Solution 4 — Duration

A sound baseline is to add only other `Duration` values and store integer milliseconds. If fractional multiplication is needed, decide whether to return a decimal duration, round to an integer millisecond, or reject fractional results. Document the rounding mode and test boundary cases. Do not silently truncate.

### Solution 5 — Decimal

```python
from decimal import Decimal


amount = Decimal("0.10")
assert amount + Decimal("0.20") == Decimal("0.30")
assert Decimal(str(0.1)) == Decimal("0.1")
```

`Decimal("0.10")` directly represents the intended decimal literal. `Decimal(0.1)` instead captures the exact decimal value of the binary float approximation, which is usually not what a money input intended as decimal text means.

### Solution 6 — Flags

```python
from enum import Flag, auto


class Access(Flag):
    READ = auto()
    WRITE = auto()
    ADMIN = auto()


access = Access.READ | Access.WRITE
assert Access.READ in access
assert Access.WRITE in access
assert Access.ADMIN not in access
```

The enum names document intent, and bitwise combination expresses a set of flags directly.

### Solution 7 — Matrix multiplication

The exact implementation depends on the matrix representation and shape policy. A correct solution should check that the left matrix's column count equals the right matrix's row count, return `NotImplemented` for unsupported types, and test dimension mismatch explicitly. Avoid silently truncating rows or filling missing values.

### Solution 8 — Operator restraint

Network I/O inside `+` would be surprising, could block, fail due to connectivity, retry, or produce external side effects when callers expect a pure value calculation. It also makes logging and debugging expressions harder and can hide latency. A named operation such as `send_to(destination)` communicates the effect and gives a place to express timeout, retry, authentication, and error-handling policy.

## 25. Self-check

Answer each question without looking back. Suggested answers follow.

1. Which method normally implements `a + b` on the left operand?
2. Why should an unsupported operand type usually cause a special method to return `NotImplemented` rather than raise `TypeError` immediately?
3. Why might `3 * vector` fail when `vector * 3` works?
4. What is the difference between `__add__` and `__iadd__`?
5. If `__iadd__` is absent, what can Python do for `x += y`?
6. Why does `sum([Vector(1, 1), Vector(2, 2)])` often need `__radd__` or an explicit `start`?
7. When should `__index__` be used rather than `__int__`?
8. Why does `Decimal("0.1") + 0.2` raise `TypeError`?
9. What does `@` conventionally mean in scientific Python?
10. Name two risks of operator overloads that have surprising meanings.
11. Why is `enum.Flag` useful for permission sets?
12. What are `__array__` and `__array_ufunc__` used for at a high level?

### Answer key

1. `__add__`.
2. `NotImplemented` permits Python to try the reflected implementation on the other operand before raising a final `TypeError`.
3. The left operand's `__mul__` may not support the vector; `Vector.__rmul__` is needed for scalar-left multiplication.
4. `__add__` implements ordinary addition, normally returning a result without mutating the original operand; `__iadd__` defines the in-place operator behavior and may mutate.
5. It can fall back to the ordinary binary operation and rebind `x` to the result.
6. The default start value is integer zero, so `0 + first_vector` must be supported or the caller must provide a compatible `start` value.
7. Use `__index__` for exact integer-like values in indexing contexts; `__int__` is for explicit integer conversion and may have different conversion semantics.
8. Python avoids silently mixing decimal arithmetic with binary floating-point arithmetic, which would make precision policy unclear.
9. Matrix multiplication.
10. They can make code unreadable, hide side effects, create surprising coercions, complicate debugging, or introduce aliasing and performance problems.
11. It represents named, combinable flags with readable bitwise operations and membership checks.
12. They provide hooks for conversion to NumPy arrays and for custom handling of NumPy ufunc operations, respectively.

## 26. Readiness checklist

You are ready to move on when you can check each item honestly:

- [ ] I can map common binary and unary operators to their special methods.
- [ ] I can implement `__add__` so it returns a new value and preserves operands.
- [ ] I can explain and use reflected methods such as `__rmul__` and `__radd__`.
- [ ] I know when to return `NotImplemented` and when to raise a domain exception.
- [ ] I understand why subclass reflected-method priority means dispatch is not simply “left side always wins.”
- [ ] I can explain the difference between `+=` on mutable and immutable objects.
- [ ] I can design `sum()` support deliberately rather than accepting arbitrary operands.
- [ ] I can distinguish `__int__` from `__index__`.
- [ ] I can use `enum.Flag` for combinable flags.
- [ ] I understand why `Decimal`, `float`, and `Fraction` should not be mixed without an explicit policy.
- [ ] I can explain `__divmod__`, three-argument `pow()`, and `@` at a conceptual level.
- [ ] I know when a named method is clearer than an overloaded operator.
- [ ] I can test result values, unsupported operands, reflected dispatch, immutability, and aliasing.
- [ ] I understand that custom numeric operators may allocate temporary objects and that performance claims should be benchmarked.

## 27. Key takeaways

1. Operator overloading connects custom classes to familiar Python syntax through special methods.
2. Keep operator meaning unsurprising and consistent with the domain.
3. Ordinary arithmetic should generally return a new value rather than mutate operands.
4. Reflected methods support the other operand order; `NotImplemented` lets Python continue dispatch.
5. In-place operators may mutate, but are not guaranteed to do so.
6. Numeric interoperability requires explicit policies for type support, precision, conversion, and rounding.
7. Use `Decimal` or integer minor units for exact money semantics rather than binary floats.
8. Use bitwise operators for flags/masks and `@` for matrix multiplication when those meanings are natural.
9. NumPy integration hooks are advanced protocols and should be implemented only with a clear interoperability and memory model.
10. Optimize only after measuring representative workloads.

---

**Next lesson:** `05-properties-and-computed-attributes.md` — using properties and computed attributes to maintain a stable public API while adding validation, caching, and controlled access to object state.
