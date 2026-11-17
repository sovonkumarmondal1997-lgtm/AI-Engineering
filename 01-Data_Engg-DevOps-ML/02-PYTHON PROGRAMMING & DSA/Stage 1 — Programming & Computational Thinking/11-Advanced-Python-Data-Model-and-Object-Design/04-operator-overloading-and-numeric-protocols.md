# Operator Overloading and Numeric Protocols

> **Stage 1 — Programming & Computational Thinking**  
> **Module 11 — Advanced Python Data Model and Object Design**  
> **Lesson 04** · Python 3.12+

## 1. Purpose and position in the roadmap

This lesson follows container protocols in Module 11 and develops the Python data model further: custom objects can participate in arithmetic, unary operations, comparisons, bitwise operations, and numeric conversion by implementing the relevant special methods.

The project tree places this material under `Stage 1 — Programming & Computational Thinking/11-Advanced-Python-Data-Model-and-Object-Design/`. The module roadmap's Lesson 04 is the specification for the scope below. The examples use small, explicit value objects so that dispatch and type contracts remain visible.

## 2. Prerequisites

You should understand:

- classes, methods, and immutable versus mutable state;
- Python's special methods and `NotImplemented`;
- equality and container protocols;
- basic arithmetic, integer division, modulo, powers, and bitwise operations;
- type annotations and `pytest`.

## 3. Learning objectives

After this lesson, you should be able to:

1. Map operators to the corresponding special methods.
2. Explain binary dispatch, reflected methods, subclass priority, and `NotImplemented`.
3. Implement arithmetic and unary methods for a small immutable value object.
4. Distinguish normal binary operations from in-place operations and their fallback.
5. Implement conversion and numeric protocol methods with clear contracts.
6. Explain how built-in numeric types interoperate—and where they deliberately do not.
7. Use bitwise operators for bit masks and `enum.Flag`.
8. Recognize when operator overloading improves a domain model and when it creates an opaque DSL.
9. Test supported operations, unsupported operands, aliases, edge cases, and immutability.
10. Reason about allocation, vectorization, and NumPy interoperability at a high level.

---

## 4. Conceptual model: operators are protocol dispatch

An expression such as `left + right` is not simply “call `left.__add__(right)` no matter what.” Python's binary operator machinery considers the operand types and their implementations, including a reflected method on the right operand. A method can return a value, return `NotImplemented` to decline the operation, or raise an exception for a genuine error.

Three rules are central:

1. **Implement only meaningful operations.** A `Money` object may add compatible money values but should not silently add a string.
2. **Return `NotImplemented` for an unsupported operand type.** It lets Python try the other operand's reflected method where applicable, and ultimately produce a normal `TypeError` if no implementation accepts the operation.
3. **Keep operator semantics intuitive.** `a + b` should mean a recognizable combination, not trigger unrelated I/O or hidden mutation.

`NotImplemented` is a special singleton used as a return value from a special method. It is not the same as raising `NotImplementedError`, which is an exception and normally signals that code has intentionally not been implemented.

```python
class Left:
    def __add__(self, other):
        print("Left.__add__")
        return NotImplemented


class Right:
    def __radd__(self, other):
        print("Right.__radd__")
        return "handled by right"


print(Left() + Right())
```

Expected output:

```text
Left.__add__
Right.__radd__
handled by right
```

If both sides decline, Python raises `TypeError`:

```python
class NoArithmetic:
    def __add__(self, other):
        return NotImplemented

    def __radd__(self, other):
        return NotImplemented


try:
    NoArithmetic() + object()
except TypeError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
TypeError
```

### 4.1 Binary dispatch and reflected-method priority

For a binary operation such as `a + b`, Python first considers the operation on the left operand and the reflected operation on the right operand. If the right operand's type is a strict subclass of the left operand's type and supplies a different reflected implementation, Python gives that reflected implementation priority. This allows a specialized subtype to handle an operation before a more general base-class implementation.

The exact dispatch details depend on type relationships and whether the relevant methods are implemented/overridden; do not model the process as a simple unconditional left-call followed by right-call for every possible case.

```python
class Base:
    def __add__(self, other):
        print("Base.__add__")
        return "base add"


class Special(Base):
    def __radd__(self, other):
        print("Special.__radd__")
        return "special reflected add"


print(Base() + Special())
```

Expected output:

```text
Special.__radd__
special reflected add
```

`Special` is a strict subclass of `Base`, and it provides its own reflected method, so that reflected implementation gets priority for this expression.

### 4.2 Arithmetic operators and their methods

| Expression | Left-side method | Reflected method |
|---|---|---|
| `a + b` | `a.__add__(b)` | `b.__radd__(a)` |
| `a - b` | `a.__sub__(b)` | `b.__rsub__(a)` |
| `a * b` | `a.__mul__(b)` | `b.__rmul__(a)` |
| `a / b` | `a.__truediv__(b)` | `b.__rtruediv__(a)` |
| `a // b` | `a.__floordiv__(b)` | `b.__rfloordiv__(a)` |
| `a % b` | `a.__mod__(b)` | `b.__rmod__(a)` |
| `a ** b` | `a.__pow__(b)` | `b.__rpow__(a)` |
| `a @ b` | `a.__matmul__(b)` | `b.__rmatmul__(a)` |
| `divmod(a, b)` | `a.__divmod__(b)` | `b.__rdivmod__(a)` |

The reflected family is not a second, unrelated set of operators: it is the protocol that lets the right operand participate when the left implementation declines or when subclass priority applies.

### 4.3 Unary and bitwise operator map

| Expression | Special method |
|---|---|
| `-x` | `x.__neg__()` |
| `+x` | `x.__pos__()` |
| `abs(x)` | `x.__abs__()` |
| `~x` | `x.__invert__()` |
| `a & b` | `a.__and__(b)` / reflected `__rand__` |
| `a \| b` | `a.__or__(b)` / reflected `__ror__` |
| `a ^ b` | `a.__xor__(b)` / reflected `__rxor__` |
| `a << b` | `a.__lshift__(b)` / reflected `__rlshift__` |
| `a >> b` | `a.__rshift__(b)` / reflected `__rrshift__` |

Comparison operators use the rich-comparison methods (`__lt__`, `__le__`, `__eq__`, `__ne__`, `__gt__`, `__ge__`) rather than arithmetic methods. See the preceding roadmap lesson for their detailed ordering contracts.

---

## 5. The evolving example: immutable `Vector2`

A two-dimensional vector is a useful domain for arithmetic because addition, subtraction, negation, scalar multiplication, and magnitude have intuitive meanings. The class below is immutable by public-API convention: its public coordinates are read-only properties, and its arithmetic returns new vectors rather than mutating coordinates. Python code can still deliberately reassign the underscore-prefixed storage attributes, so this class is not a hard immutability boundary. Section 15 shows a frozen dataclass when ordinary attribute reassignment must be prevented.

We deliberately support only:
- vector + vector;
- vector - vector;
- vector * a real scalar and scalar * vector;
- unary `+`, unary `-`, and `abs(vector)`.

We do **not** claim that vector division, matrix multiplication, or every numeric conversion is meaningful for this type.

```python
from __future__ import annotations

from math import hypot, isfinite
from numbers import Real
from typing import Self
from types import NotImplementedType


class Vector2:
    __slots__ = ("_x", "_y")

    def __init__(self, x: Real, y: Real) -> None:
        if isinstance(x, bool) or isinstance(y, bool):
            raise TypeError("boolean coordinates are not accepted")
        if not isinstance(x, Real) or not isinstance(y, Real):
            raise TypeError("coordinates must be real numbers")
        if not isfinite(float(x)) or not isfinite(float(y)):
            raise ValueError("coordinates must be finite")
        self._x = x
        self._y = y

    @property
    def x(self) -> Real:
        return self._x

    @property
    def y(self) -> Real:
        return self._y

    def __repr__(self) -> str:
        return f"Vector2({self._x!r}, {self._y!r})"

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Vector2):
            return NotImplemented
        return self._x == other._x and self._y == other._y

    def __add__(self, other: object) -> Self | NotImplementedType:
        if not isinstance(other, Vector2):
            return NotImplemented
        return type(self)(self._x + other._x, self._y + other._y)

    def __sub__(self, other: object) -> Self | NotImplementedType:
        if not isinstance(other, Vector2):
            return NotImplemented
        return type(self)(self._x - other._x, self._y - other._y)

    def __mul__(self, scalar: object) -> Self | NotImplementedType:
        if isinstance(scalar, bool) or not isinstance(scalar, Real):
            return NotImplemented
        return type(self)(self._x * scalar, self._y * scalar)

    def __rmul__(self, scalar: object) -> Self | NotImplementedType:
        return self * scalar

    def __neg__(self) -> Self:
        return type(self)(-self._x, -self._y)

    def __pos__(self) -> Self:
        return type(self)(+self._x, +self._y)

    def __abs__(self) -> float:
        return hypot(float(self._x), float(self._y))

    def __bool__(self) -> bool:
        return self._x != 0 or self._y != 0


v = Vector2(3, 4)
print(v + Vector2(1, 2))
print(v - Vector2(1, 2))
print(v * 2)
print(2 * v)
print(-v, +v, abs(v), bool(Vector2(0, 0)))
print(v)
```

Expected output:

```text
Vector2(4, 6)
Vector2(2, 2)
Vector2(6, 8)
Vector2(6, 8)
Vector2(-3, -4) Vector2(3, 4) 5.0 False
Vector2(3, 4)
```

### 5.1 Why return `NotImplemented`?

If `Vector2.__add__` receives a string, it declines rather than trying to guess a conversion. This leaves Python free to try the string's reflected method, if any, and then raise `TypeError` if no side supports the operation.

```python
v = Vector2(1, 2)
try:
    v + "north"
except TypeError as exc:
    print(type(exc).__name__, str(exc))
```

The exact wording of a `TypeError` message can vary by Python version and operand combination. The stable expectation is that the expression raises `TypeError`, not a particular message.

### 5.2 Immutability and aliasing

`a + b` returns a new value object. It does not modify either operand.

```python
a = Vector2(1, 2)
alias = a
result = a + Vector2(10, 20)
print(alias is a, alias, result)
```

Expected output:

```text
True Vector2(1, 2) Vector2(11, 22)
```

This is different from mutating an object in place. The name `result` is bound to a newly returned object; the original `a` remains unchanged. The same distinction appears with built-ins: `list += iterable` mutates the existing list (so aliases observe the extension), while `tuple += iterable` creates a new tuple and rebinds the target name.

The example accepts `numbers.Real` implementations such as ordinary integers and floats, while explicitly rejecting `bool`. It does not promise interoperability with `Decimal`, which is not registered as a `numbers.Real` in the standard numeric tower. `Fraction` is a `Real` and is accepted; the resulting coordinate arithmetic follows the underlying operand types. The constructor's finiteness check converts to `float` for validation, which is suitable for this small educational vector but is not a universal exactness strategy for arbitrary-precision numerics.

---

## 6. Reflected methods: `__radd__`, `__rmul__`, and friends

A reflected method lets the right operand define what an operation means when the left operand cannot handle it. A canonical example is `2 * vector`: the integer's multiplication does not know how to scale a custom vector, so `Vector2.__rmul__` can handle the scalar.

For a custom numeric type, implement reflected methods only when the operation is meaningful. Common pairs include:

- `__add__` / `__radd__`
- `__sub__` / `__rsub__`
- `__mul__` / `__rmul__`
- `__truediv__` / `__rtruediv__`
- `__floordiv__` / `__rfloordiv__`
- `__mod__` / `__rmod__`
- `__pow__` / `__rpow__`
- `__matmul__` / `__rmatmul__`

The operation is not automatically commutative. For subtraction, `a - b` and `b - a` are different. A reflected subtraction implementation must preserve operand order.

```python
from __future__ import annotations
from types import NotImplementedType


class Quantity:
    def __init__(self, value: int) -> None:
        self.value = value

    def __sub__(self, other: object) -> Quantity | NotImplementedType:
        if not isinstance(other, Quantity):
            return NotImplemented
        return Quantity(self.value - other.value)

    def __rsub__(self, other: object) -> Quantity | NotImplementedType:
        if isinstance(other, int) and not isinstance(other, bool):
            return Quantity(other - self.value)
        return NotImplemented

    def __repr__(self) -> str:
        return f"Quantity({self.value})"


print(Quantity(3) - Quantity(10))
print(10 - Quantity(3))
```

Expected output:

```text
Quantity(-7)
Quantity(7)
```

In this design `10 - Quantity(3)` is explicitly supported, while other left operands are declined. This is a deliberate interoperability policy, not something Python invents automatically.

---

## 7. In-place operations: `__iadd__` and fallback

The augmented assignment statement `x += y` first tries the in-place operation `x.__iadd__(y)` when available. If that operation is absent or returns `NotImplemented`, Python falls back to the normal addition protocol and assigns the result back to the target. For a mutable object, `__iadd__` may mutate the existing object and return it; for an immutable value object, it commonly returns a new object.

Do not assume `+=` always mutates. The visible variable is assigned the operation's result, so object identity depends on the type's implementation.

```python
from __future__ import annotations
from types import NotImplementedType


class ImmutableCounter:
    def __init__(self, value: int) -> None:
        self.value = value

    def __add__(self, other: object) -> ImmutableCounter | NotImplementedType:
        if not isinstance(other, int) or isinstance(other, bool):
            return NotImplemented
        return type(self)(self.value + other)

    def __repr__(self) -> str:
        return f"ImmutableCounter({self.value})"


counter = ImmutableCounter(2)
before = counter
counter += 3  # no __iadd__: uses __add__ then rebinds counter
print(counter, before, counter is before)
```

Expected output:

```text
ImmutableCounter(5) ImmutableCounter(2) False
```

For a mutable implementation, `__iadd__` could update internal state and return `self`. That can preserve aliases, which may be correct for a mutable collection but surprising for a value object. Write tests that explicitly check identity and mutation semantics when aliases matter.

---

## 8. Full arithmetic method reference

This table maps the core numeric operations. Each special method normally receives the other operand as its argument; unary methods receive only `self`.

| Operation | Primary method | Reflected method | Notes |
|---|---|---|---|
| `a + b` | `__add__` | `__radd__` | Addition / domain-specific combination |
| `a - b` | `__sub__` | `__rsub__` | Order matters |
| `a * b` | `__mul__` | `__rmul__` | Often scalar multiplication for vectors |
| `a / b` | `__truediv__` | `__rtruediv__` | True division |
| `a // b` | `__floordiv__` | `__rfloordiv__` | Floor division, not truncation toward zero |
| `a % b` | `__mod__` | `__rmod__` | Remainder follows Python's modulo convention |
| `a ** b` | `__pow__` | `__rpow__` | May also receive a modulus in three-argument `pow` |
| `a @ b` | `__matmul__` | `__rmatmul__` | Matrix multiplication; not ordinary multiplication |
| `divmod(a, b)` | `__divmod__` | `__rdivmod__` | Returns quotient/remainder pair |
| `-a` | `__neg__` | — | Unary negation |
| `+a` | `__pos__` | — | Unary plus |
| `abs(a)` | `__abs__` | — | Absolute value / magnitude |
| `~a` | `__invert__` | — | Bitwise inversion for integer-like values |
| `a & b` | `__and__` | `__rand__` | Bitwise AND |
| `a \| b` | `__or__` | `__ror__` | Bitwise OR |
| `a ^ b` | `__xor__` | `__rxor__` | Bitwise XOR |
| `a << b` | `__lshift__` | `__rlshift__` | Left shift |
| `a >> b` | `__rshift__` | `__rrshift__` | Right shift |

Comparison methods belong to the rich comparison protocol. They should not be implemented by reusing arithmetic methods unless the domain semantics explicitly require it.

---

## 9. `__divmod__` and three-argument `pow`

`divmod(a, b)` combines floor division and modulo semantics. A custom numeric type can define `__divmod__` to return a pair appropriate to its domain.

`pow(base, exponent, modulus)` has a special three-argument form, chiefly for modular exponentiation with integers. A custom `__pow__` may be called with a third argument in supported cases; if you implement it, account for the optional modulus deliberately. Do not claim that a custom `__pow__` supports three-argument `pow` unless its signature and behavior demonstrate it.

```python
from __future__ import annotations
from types import NotImplementedType


class IntLike:
    def __init__(self, value: int) -> None:
        self.value = value

    def __divmod__(self, other: object) -> tuple[int, int] | NotImplementedType:
        if not isinstance(other, IntLike):
            return NotImplemented
        return divmod(self.value, other.value)

    def __pow__(self, exponent: object, modulo: object | None = None) -> IntLike | NotImplementedType:
        if not isinstance(exponent, int) or isinstance(exponent, bool):
            return NotImplemented
        if modulo is None:
            if exponent < 0:
                raise ValueError("IntLike supports only non-negative exponents without a modulus")
            return type(self)(self.value ** exponent)
        if not isinstance(modulo, int) or isinstance(modulo, bool):
            return NotImplemented
        return type(self)(pow(self.value, exponent, modulo))

    def __repr__(self) -> str:
        return f"IntLike({self.value})"


print(divmod(IntLike(17), IntLike(5)))
print(pow(IntLike(2), 5))
print(pow(IntLike(2), 5, 7))
```

Expected output:

```text
(3, 2)
IntLike(32)
IntLike(4)
```

This is an educational wrapper around integer semantics, not a complete implementation of Python's integer protocol. It supports non-negative exponents without a modulus and integer exponents with a valid modulus; a negative exponent without a modulus raises `ValueError` rather than returning a floating-point result wrapped in an integer-like object. It does not define every arithmetic operation, conversion method, or reflected method.

---

## 10. Numeric conversions and truth protocol

Conversion methods have different contracts and should not be treated as interchangeable.

| Operation | Method | Meaning |
|---|---|---|
| `int(x)` | `__int__` | Integer conversion; may be lossy for non-integral values |
| `float(x)` | `__float__` | Float conversion |
| `complex(x)` | `__complex__` | Complex conversion |
| `round(x)` / `round(x, ndigits)` | `__round__` | Rounding policy |
| `operator.index(x)` and index contexts | `__index__` | Exact integer representation |
| `bool(x)` | `__bool__` or fallback `__len__` | Truth value |

### 10.1 `__int__` is not `__index__`

`__index__` is for exact integer contexts such as list indices and bit positions. `__int__` can represent a conversion and may discard fractional information. Implement `__index__` only when the object truly represents an exact integer.

```python
import operator


class PageNumber:
    def __init__(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("page number must be an int")
        self.value = value

    def __index__(self) -> int:
        return self.value

    def __int__(self) -> int:
        return self.value


pages = ["intro", "methods", "tests"]
print(pages[PageNumber(1)])
print(operator.index(PageNumber(2)))
```

Expected output:

```text
methods
2
```

### 10.2 A conversion example

```python
class Measurement:
    def __init__(self, value: float) -> None:
        self.value = float(value)

    def __float__(self) -> float:
        return self.value

    def __int__(self) -> int:
        return int(self.value)

    def __complex__(self) -> complex:
        return complex(self.value)

    def __round__(self, ndigits: int | None = None) -> int | float:
        if ndigits is None:
            return round(self.value)
        return round(self.value, ndigits)

    def __bool__(self) -> bool:
        return self.value != 0.0


m = Measurement(3.14159)
print(int(m), float(m), complex(m), round(m, 2), bool(m))
print(bool(Measurement(0.0)))
```

Expected output:

```text
3 3.14159 (3.14159+0j) 3.14 True
False
```

`__bool__` should return an actual `bool`. If it is absent, Python falls back to `__len__` where available; it does not use `__int__` or `__float__` to determine truthiness.

---

## 11. Numeric tower and interoperability

The `numbers` module describes an abstract numeric tower, including `Number`, `Complex`, `Real`, `Rational`, and `Integral`. These ABCs help describe mathematical capabilities, but runtime registration and arithmetic interoperability are not identical things. An object being an instance of an ABC does not guarantee that every mixed operation works.

- `int` is an integral real number.
- `float` is a real floating-point type.
- `fractions.Fraction` represents rational numbers and participates in the standard numeric tower.
- `decimal.Decimal` is designed for decimal arithmetic, including many financial use cases, but is not a `numbers.Real` implementation in the same way as `float` and `Fraction`.

### 11.1 Why `Decimal + float` raises `TypeError`

Mixing `Decimal` and `float` in arithmetic is rejected to prevent silent mixing of decimal arithmetic with binary floating-point approximation.

```python
from decimal import Decimal
from fractions import Fraction


print(Fraction(1, 3) + Fraction(1, 6))
print(Fraction(1, 2) + 0.25)

try:
    Decimal("0.1") + 0.2
except TypeError as exc:
    print(type(exc).__name__)
```

Expected output:

```text
1/2
0.75
TypeError
```

The `Fraction`/`float` operation produces a `float`, while `Fraction` with `Fraction` stays exact as a rational. For precision-sensitive code, choose one numeric model and convert deliberately at a well-defined boundary.

### 11.2 Interoperability policy for custom types

Before supporting mixed operations, answer:

1. Which operand types are supported?
2. What type is returned?
3. Does the result preserve exactness, precision, units, or currency?
4. Should unsupported operands yield `NotImplemented` or a domain-specific exception?
5. Does reflected dispatch preserve operand order?

Avoid broad coercion such as `float(other)` inside every method. It may silently lose precision or accept semantically incompatible values.

### 11.3 `numbers.Number` and `numbers.Real`

```python
from numbers import Number, Real
from decimal import Decimal
from fractions import Fraction

for value in (3, 2.5, Fraction(1, 3), Decimal("1.2")):
    print(type(value).__name__, isinstance(value, Number), isinstance(value, Real))
```

Expected output on standard Python 3.12+:

```text
int True True
float True True
Fraction True True
Decimal True False
```

This is an example of ABC membership, not a complete predictor of mixed arithmetic support.

---

## 12. Bitwise operators and `enum.Flag`

Bitwise operators are useful for masks, capabilities, permissions, and sets of flags. `enum.Flag` gives named members a readable representation while supporting combinations with bitwise operations.

```python
from enum import Flag, auto


class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


granted = Permission.READ | Permission.WRITE
print(granted)
print(bool(granted & Permission.READ))
print(bool(granted & Permission.EXECUTE))
```

Expected output:

```text
Permission.READ|WRITE
True
False
```

Use `Flag` when combinations are meaningful. `IntFlag` is available when integer interoperability is specifically required. Avoid using arithmetic `+` for flag combination: bitwise OR expresses the set-union-like meaning.

For custom bitmask types, define `__and__`, `__or__`, `__xor__`, reflected variants if meaningful, and `__invert__` with a clear policy for unknown bits.

---

## 13. `__matmul__` and array interoperability

The `@` operator maps to `__matmul__` and `__rmatmul__`. It is intended for matrix multiplication and related linear-algebra operations, not ordinary scalar multiplication. A custom matrix/vector class should define the shape rules and result type explicitly.

NumPy adds a separate layer of interoperability:

- `__array__` lets an object expose or convert to a NumPy array representation.
- `__array_ufunc__` lets an object participate in NumPy universal-function dispatch, such as operations implemented by ufuncs.
- `__array_priority__` has historically influenced precedence in some mixed NumPy operations, but the exact interaction depends on NumPy version and the operation. Prefer current NumPy interoperability protocols rather than relying on old precedence tricks.

These hooks are NumPy-specific conventions, not Python's core numeric tower. They require NumPy to be installed and should be implemented only when the object has a well-defined array interpretation. This lesson does not claim that `Vector2` is a NumPy array or that it interoperates with NumPy automatically.

Illustrative interface sketch (requires NumPy to implement fully; not a runnable implementation):

```python
# Sketch only — NumPy is an optional dependency.
#
# class MyArrayLike:
#     def __array__(self, dtype=None, copy=None):
#         ...
#
#     def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
#         ...
```

Do not implement `__array__` merely to make an object “work with NumPy.” Define ownership, copy behavior, dtype conversion, and ufunc result semantics first.

---

## 14. Fluent operator DSLs: powerful but risky

Operator overloading can make domain code readable. For example, `pathlib.Path / "file.txt"` composes a path, `Permission.READ | Permission.WRITE` combines flags, and a pipeline library might use `stage_a | stage_b` or `source >> transform` to compose operations. The latter two are custom DSL conventions, not built-in meanings for arbitrary objects.

```python
from pathlib import Path

path = Path("data") / "records.csv"
print(path.as_posix())
```

Expected output:

```text
data/records.csv
```

It can also create an opaque DSL where ordinary operators trigger hidden network calls, mutate global state, or mean unrelated things depending on context. A fluent DSL is appropriate when:

- the operator meaning is familiar to the target audience;
- operand types and result types are predictable;
- errors are explicit;
- precedence and associativity do not surprise users;
- debugging is still straightforward.

Prefer named methods when the operation is not naturally represented by a Python operator, e.g. `dataset.join(other, on="customer_id")` is often clearer than inventing arithmetic-like syntax.

---

## 15. Performance and value-object design

A frozen dataclass makes the immutability contract enforceable for ordinary attribute assignment, rather than relying only on a private-attribute convention. Operator methods should return a new instance and decline unsupported operands.

```python
from dataclasses import dataclass
from types import NotImplementedType


@dataclass(frozen=True, slots=True)
class FrozenPoint:
    x: float
    y: float

    def __add__(self, other: object) -> "FrozenPoint | NotImplementedType":
        if not isinstance(other, FrozenPoint):
            return NotImplemented
        return FrozenPoint(self.x + other.x, self.y + other.y)


left = FrozenPoint(1, 2)
right = left + FrozenPoint(3, 4)
print(left, right, left is right)
```

Expected output:

```text
FrozenPoint(x=1, y=2) FrozenPoint(x=4, y=6) False
```

A frozen dataclass is not a security boundary against deliberate low-level mutation, but it prevents ordinary reassignment and is a clearer default for value objects.

### 15.1 Temporary allocations

Immutable arithmetic usually creates a new object per operation. For a small `Vector2`, this is a reasonable trade-off for clarity and alias safety. In tight numeric loops, repeated temporary allocations may be expensive.

### 15.2 Vectorization

Vectorized array operations can perform work in optimized native code and reduce Python-level loop overhead. Do not assume a custom class is vectorized just because it implements `__add__`. NumPy array interoperability must be designed explicitly, and benchmarks should use realistic data sizes.

### 15.3 In-place methods

An in-place method can avoid some allocations, but it changes aliasing semantics and may be impossible or inappropriate for immutable objects. Measure before adding complexity.

### 15.4 Numeric correctness beats clever coercion

A numeric API should document exactness, units, overflow, rounding, accepted operand types, and result types. Avoid silently converting `Decimal` to `float`, `Fraction` to `float`, or a dimensioned quantity to an untyped number.

---

## 16. Common mistakes and debugging

1. **Raising `NotImplementedError` instead of returning `NotImplemented`.** The former is an exception; the latter declines an operation and permits dispatch.
2. **Returning `None` for unsupported operand types.** Python treats it as a result, not a request to try the reflected method.
3. **Forgetting `__radd__` when supporting `sum()`.** `sum()` starts with integer `0` by default, so the first operation is `0 + first_value`. A custom value type can support this intentionally in `__radd__`, or callers can supply a compatible `start` value to `sum()`.
4. **Assuming reflected methods always run only after the left method.** A strict subclass's reflected implementation can get priority.
5. **Implementing only the left method and expecting `scalar * custom_value` to work.** Add a reflected method when that operand order is meaningful.
6. **Treating non-commutative operations as commutative.** Reflected subtraction/division must preserve operand order.
7. **Assuming `+=` necessarily mutates.** It can return a new object and rebind the target.
8. **Implementing `__iadd__` on an immutable type by mutating shared state.** That breaks value semantics and can surprise aliases.
9. **Claiming all numeric types interoperate.** ABC membership is not a guarantee of mixed arithmetic support.
10. **Silently coercing `Decimal` and `float`.** Their arithmetic models differ; Python rejects direct mixed addition.
11. **Confusing `__int__` and `__index__`.** `__index__` must represent an exact integer for indexing contexts.
12. **Returning a non-`bool` from `__bool__`.** The method must return `True` or `False`.
13. **Claiming `__matmul__` is ordinary multiplication.** It has distinct linear-algebra semantics.
14. **Overloading operators with surprising side effects.** Keep operator meanings intuitive and document result types.
15. **Assuming custom operators are vectorized.** Python special methods alone do not remove Python-level loop overhead.
16. **Implementing NumPy hooks without a coherent ownership or result policy.** `__array__` and `__array_ufunc__` are explicit interoperability contracts.
17. **Ignoring aliases in tests.** A result can be numerically correct while mutating an operand unexpectedly.
18. **Overpromising three-argument `pow`.** Test and document the optional modulus explicitly.
19. **Implementing only a partial numeric API but presenting it as a complete number type.** State supported operations and conversions precisely.

For debugging, inspect the actual operand types, the exact special method called, whether it returned `NotImplemented`, and whether the final exception came from dispatch or from inside a method. Avoid tests that assert exact `TypeError` wording unless the message itself is part of your public API.

---

## 17. Pytest tests

Save the example classes in `operator_protocols_examples.py`, then save these tests as `test_operator_protocols.py`. They cover supported arithmetic, reflected operations, unsupported types, conversion, immutability/aliasing, dispatch priority, in-place fallback, `Decimal` interoperability, and bitwise flags.

```python
from decimal import Decimal
from enum import Flag, auto
from fractions import Fraction

import pytest

# Import these from your example module when using separate files:
# from operator_protocols_examples import (Vector2, Quantity, ImmutableCounter, PageNumber, IntLike, FrozenPoint, SumVector)


def test_vector_arithmetic_and_alias_safety():
    vector = Vector2(3, 4)
    alias = vector
    result = vector + Vector2(1, 2)

    assert result == Vector2(4, 6)
    assert alias is vector
    assert vector == Vector2(3, 4)
    assert result is not vector


def test_vector_reflected_scalar_multiplication():
    assert 2 * Vector2(3, 4) == Vector2(6, 8)
    assert Vector2(3, 4) * 2 == Vector2(6, 8)


def test_vector_unary_and_bool():
    assert -Vector2(1, 2) == Vector2(-1, -2)
    assert +Vector2(1, 2) == Vector2(1, 2)
    assert abs(Vector2(3, 4)) == 5.0
    assert not Vector2(0, 0)


def test_vector_unsupported_operand_raises_type_error():
    with pytest.raises(TypeError):
        _ = Vector2(1, 2) + "north"


def test_subclass_reflected_method_priority(capsys):
    class Base:
        def __add__(self, other):
            print("Base.__add__")
            return "base"

    class Special(Base):
        def __radd__(self, other):
            print("Special.__radd__")
            return "special"

    assert Base() + Special() == "special"
    assert capsys.readouterr().out == "Special.__radd__\n"


def test_inplace_fallback_rebinds_immutable_counter():
    counter = ImmutableCounter(2)
    before = counter
    counter += 3
    assert counter.value == 5
    assert before.value == 2
    assert counter is not before


def test_iadd_notimplemented_falls_back_to_add():
    class DecliningInplaceCounter:
        def __init__(self, value: int) -> None:
            self.value = value

        def __iadd__(self, amount: int):
            return NotImplemented

        def __add__(self, amount: int):
            return type(self)(self.value + amount)

    counter = DecliningInplaceCounter(2)
    before = counter
    counter += 3
    assert counter.value == 5
    assert before.value == 2
    assert counter is not before


def test_mutable_inplace_add_preserves_alias():
    class MutableCounter:
        def __init__(self, value: int) -> None:
            self.value = value

        def __iadd__(self, amount: int) -> "MutableCounter":
            self.value += amount
            return self

    counter = MutableCounter(2)
    alias = counter
    counter += 1
    assert counter is alias
    assert alias.value == 3


def test_intlike_pow_rejects_negative_non_modular_exponent():
    with pytest.raises(ValueError, match="non-negative exponents"):
        pow(IntLike(2), -1)


def test_frozen_point_addition_and_immutability():
    from dataclasses import FrozenInstanceError

    point = FrozenPoint(1, 2)
    result = point + FrozenPoint(3, 4)
    assert result == FrozenPoint(4, 6)
    assert result is not point
    with pytest.raises(FrozenInstanceError):
        point.x = 10


def test_sumvector_accepts_integer_zero_identity_only():
    result = sum([SumVector(1, 1), SumVector(2, 2)])
    assert (result.x, result.y) == (3, 3)
    with pytest.raises(TypeError):
        False + SumVector(1, 1)


def test_page_number_index_protocol():
    values = ["intro", "methods", "tests"]
    assert values[PageNumber(1)] == "methods"


def test_fraction_and_decimal_float_policy():
    assert Fraction(1, 3) + Fraction(1, 6) == Fraction(1, 2)
    with pytest.raises(TypeError):
        _ = Decimal("0.1") + 0.2


def test_flag_combination():
    class Permission(Flag):
        READ = auto()
        WRITE = auto()
        EXECUTE = auto()

    granted = Permission.READ | Permission.WRITE
    assert bool(granted & Permission.READ)
    assert not bool(granted & Permission.EXECUTE)
```

The tests assume the corresponding classes in the lesson are copied into the importable example module. In a production repository, keep examples and tests in separate files and run `pytest -q`. Do not report a passing test run unless you have actually executed it.

---

## 18. Graduated exercises

### Exercise 1 — Beginner: map operators

For each expression below, name the primary special method and reflected method where one exists:

- `a + b`
- `a // b`
- `-a`
- `a @ b`
- `a & b`
- `divmod(a, b)`

### Exercise 2 — Beginner: unsupported operands

Implement a `Temperature` value object that adds only another `Temperature`. For other types, return `NotImplemented`. Demonstrate that adding a string raises `TypeError`.

### Exercise 3 — Intermediate: reflected arithmetic

Extend `Temperature` so that `5 + temperature` is meaningful only if the design clearly defines what the integer means. Implement `__radd__` without assuming the operation is automatically commutative.

### Exercise 4 — Intermediate: in-place semantics

Implement both an immutable counter without `__iadd__` and a mutable counter with `__iadd__`. Test the object identity and alias behavior of `counter += 1`.

### Exercise 5 — Intermediate: conversion methods

Implement a page-index type with `__index__`. Explain why an approximate measurement should not automatically implement `__index__`.

### Exercise 6 — Advanced: `divmod` and modular power

Implement a small integer wrapper supporting `__divmod__` and `__pow__(exponent, modulo=None)`. Test both `pow(value, exponent)` and `pow(value, exponent, modulus)`.

### Exercise 7 — Advanced: numeric interoperability policy

Write a short policy for how a domain numeric type should interact with `int`, `float`, `Fraction`, and `Decimal`. State which combinations are supported, what the result type is, and how unsupported combinations fail.

### Exercise 8 — Production design: benchmark allocations

Compare a pure-Python immutable vector loop with a vectorized array implementation for realistic sizes. Measure execution time and peak memory; explain why the benchmark is workload-dependent and why operator overloading alone does not imply vectorization.

---

## 19. Worked solutions

### Solution 1

| Expression | Primary method | Reflected method |
|---|---|---|
| `a + b` | `__add__` | `__radd__` |
| `a // b` | `__floordiv__` | `__rfloordiv__` |
| `-a` | `__neg__` | None |
| `a @ b` | `__matmul__` | `__rmatmul__` |
| `a & b` | `__and__` | `__rand__` |
| `divmod(a, b)` | `__divmod__` | `__rdivmod__` |

### Solution 2

```python
from __future__ import annotations
from types import NotImplementedType


class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = float(celsius)

    def __add__(self, other: object) -> Temperature | NotImplementedType:
        if not isinstance(other, Temperature):
            return NotImplemented
        return Temperature(self.celsius + other.celsius)

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius == other.celsius

    def __repr__(self) -> str:
        return f"Temperature({self.celsius!r})"


assert Temperature(10) + Temperature(5) == Temperature(15)
try:
    Temperature(10) + "5"
except TypeError:
    pass
else:
    raise AssertionError("unsupported addition should fail")
```

For a fully testable value object, implement `__eq__` and consider whether the temperature scale and absolute-zero constraints need validation. The unsupported-type behavior should be expressed by `NotImplemented`, not `NotImplementedError`.

### Solution 3

A valid design could treat an integer as a temperature delta only if the API explicitly defines that convention. Otherwise, do not implement `__radd__`; requiring a `Temperature` operand is safer. If the integer represents a delta, use a distinct `TemperatureDelta` type to prevent confusion between an absolute temperature and a difference.

### Solution 4

Immutable fallback is demonstrated by `ImmutableCounter` in Section 7. A mutable implementation could be:

```python
class MutableCounter:
    def __init__(self, value: int) -> None:
        self.value = value

    def __iadd__(self, amount: int) -> "MutableCounter":
        self.value += amount
        return self


counter = MutableCounter(2)
alias = counter
counter += 1
assert counter is alias
assert alias.value == 3
```

Because `__iadd__` mutates and returns `self`, aliases observe the change. This is appropriate only when mutation is part of the object's contract.

### Solution 5

The `PageNumber` class in Section 10 provides `__index__`, so list indexing accepts it. An approximate measurement should not implement `__index__` because index contexts require an exact integer interpretation; silently rounding or truncating would make indexing surprising.

### Solution 6

The `IntLike` class in Section 9 demonstrates both methods. Extend its tests to cover exponent zero, invalid exponents, modulus zero (which should raise `ValueError` under integer `pow` semantics), and negative exponents. If the wrapper does not intend to support those cases, state that limitation and test the expected failure.

### Solution 7

A conservative policy is to support exact rational operations with `int` and `Fraction`, explicitly decide whether float mixing is permitted, and reject `Decimal`/`float` mixing unless the caller converts at a deliberate boundary. The result type should be documented for every supported pair. ABC inheritance alone is insufficient evidence that an operation works.

### Solution 8

Use `timeit` and `tracemalloc` (or a benchmark framework) with repeatable inputs and enough repetitions. Record Python and NumPy versions, array sizes, warm-up policy, and whether allocations are included. Do not generalize from a tiny input: interpreter overhead, memory layout, native kernels, and conversion costs can reverse a result.

---

## 20. Roadmap self-check answers

### 1. Why does `sum([Vector(1,1), Vector(2,2)])` fail by default and how do you fix it?

`sum()` starts with integer `0`, so it begins by evaluating `0 + Vector(1, 1)`. A vector that implements only `Vector.__add__` for another vector cannot handle that first operation, and without a compatible `__radd__`, the expression raises `TypeError`. One fix is to implement `__radd__` for the intentional zero-start case; another is to provide a compatible `start` value such as `sum(vectors, Vector(0, 0))`. The latter requires the vector addition method to support the vector start value.

```python
from __future__ import annotations
from types import NotImplementedType


class SumVector:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    def __add__(self, other: object) -> SumVector | NotImplementedType:
        if not isinstance(other, SumVector):
            return NotImplemented
        return type(self)(self.x + other.x, self.y + other.y)

    def __radd__(self, other: object) -> SumVector | NotImplementedType:
        if type(other) is int and other == 0:
            return type(self)(self.x, self.y)
        return NotImplemented

    def __repr__(self) -> str:
        return f"SumVector({self.x}, {self.y})"

print(sum([SumVector(1, 1), SumVector(2, 2)]))
```

Expected output:

```text
SumVector(3, 3)
```

The integer-zero case returns a copy rather than aliasing the first input, because this demonstration stores mutable attributes. For an actually immutable value object, returning `self` can be safe. For more complex numeric types, validate the exact zero type and preserve the domain's identity semantics.

### 2. What happens if `__add__` returns `NotImplemented`?

Python treats it as a refusal to handle that operand pair and tries an eligible reflected implementation on the right operand. If no implementation supports the operation, Python raises `TypeError`. `NotImplemented` is not the same as `NotImplementedError`.

### 3. Which method does `v += w` call when `__iadd__` is absent?

Python falls back to the normal addition protocol (`__add__` and, if needed, reflected dispatch), then rebinds the target name to the result. That may create a new object rather than mutate the existing one. Lists illustrate in-place mutation; tuples illustrate rebinding to a new tuple.

---

## 21. Final engineering checklist

- [ ] Every supported operator has a documented meaning and result type.
- [ ] Unsupported operand types return `NotImplemented` where appropriate.
- [ ] Reflected methods preserve operand order and support only intentional combinations.
- [ ] Subclass reflected-method priority is understood and tested.
- [ ] In-place methods have explicit mutation and aliasing semantics.
- [ ] `NotImplemented` is not confused with `NotImplementedError`.
- [ ] Unary, arithmetic, bitwise, comparison, and conversion protocols are not conflated.
- [ ] `__int__`, `__float__`, `__complex__`, `__round__`, `__index__`, and `__bool__` follow their contracts.
- [ ] Three-argument `pow` and `divmod` are tested if claimed to be supported.
- [ ] `int`, `float`, `Fraction`, and `Decimal` interoperability is explicit.
- [ ] `Decimal`/`float` mixing is not silently coerced.
- [ ] `enum.Flag` is used for flag combinations where appropriate.
- [ ] `@` is reserved for a clear matrix-multiplication-like meaning.
- [ ] NumPy interoperability hooks are treated as explicit, optional contracts.
- [ ] Performance claims are benchmarked on representative workloads.
- [ ] Tests cover aliases, unsupported operands, dispatch, numeric edge cases, and expected exceptions.
- [ ] Operator overloading improves readability rather than hiding surprising side effects.

**Lesson complete when:** you can trace an operator expression through Python's dispatch, implement a small coherent numeric value object, define its interoperability boundaries, and test both successful and rejected operations.
