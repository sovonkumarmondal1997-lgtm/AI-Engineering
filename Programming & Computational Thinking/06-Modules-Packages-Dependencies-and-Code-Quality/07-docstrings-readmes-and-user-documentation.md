# Docstrings, READMEs, and User Documentation

## Learning Objectives

By the end of this chapter you will be able to:

- Explain what documentation is, why code alone is never sufficient, and
  which audience (user, developer, maintainer, reviewer, operator, API
  consumer) each kind of documentation serves.
- Write correct, useful docstrings for functions, methods, classes,
  modules, and packages, and explain precisely how Python stores and
  exposes them through `__doc__`.
- Distinguish comments from docstrings by purpose, location, tooling
  support, and runtime accessibility — and know when each is
  appropriate.
- Write docstrings in Google, NumPy, and Sphinx/reStructuredText style,
  explain their structural differences, and justify picking one style
  per project.
- Combine type hints with docstrings correctly: know what each layer
  communicates, and avoid redundant, rot-prone prose that merely
  repeats a type annotation.
- Write a complete, professional `README.md` — overview, prerequisites,
  installation, configuration, usage, testing, troubleshooting,
  development, and contribution sections — for a real Python project.
- Document CLI programs, environment variables, and configuration
  values with required/optional/default/security-sensitivity
  information, without ever committing real secrets.
- Explain documentation drift and documentation debt, why they happen,
  and how Documentation as Code, code review, and CI reduce them.
- Explain `pydoc`, `doctest`, Sphinx, and MkDocs as distinct
  mechanisms/tools, and know which solves which problem — without
  conflating a Python language feature with a third-party tool.
- Write architecture documentation, an Architecture Decision Record
  (ADR), a runbook, and a troubleshooting guide, and explain how each
  differs from a README.
- Distinguish tutorials, how-to guides, reference documentation, and
  explanation documentation (the Diátaxis framework), and user
  documentation from developer documentation.
- Document data pipelines, ML systems, and agentic AI systems at a
  production level of rigor, explaining why AI systems typically need
  *more* documentation than deterministic code.
- Apply a documentation-quality framework (correctness, completeness,
  clarity, consistency, discoverability, maintainability, audience
  awareness, actionability) to review and improve existing
  documentation.

## 1. Why Documentation Matters

**What is documentation?** Documentation is any written material,
separate from the code's execution logic, that explains what a system
does, how to use it, why it was built a certain way, or how to operate
it. A docstring, a `README.md`, a comment, an architecture diagram, and
an incident runbook are all documentation — they differ in audience and
form, not in fundamental purpose.

**Why do software projects need documentation at all, if the code
already says what happens?** Because *"what happens"* and *"what you
need to know to use this safely"* are different questions. Code is
unambiguous about mechanism — line by line, it is a precise, executable
description of behavior. But code is silent about **intent**: why a
choice was made, what a caller is allowed to assume, what will break if
a rule is violated, and what to do when something goes wrong. Reading
every line of a codebase to discover these things does not scale past a
handful of files, and it is exactly the kind of question documentation
exists to answer directly.

**Why isn't "readable code" enough by itself?** Consider a function
whose code is completely clean, with a good name and clear logic:

```python
def charge_customer(customer_id: str, amount_cents: int) -> str:
    if amount_cents <= 0:
        raise ValueError("amount_cents must be positive")
    payment = payment_gateway.create_charge(customer_id, amount_cents)
    return payment.id
```

Reading this, you can tell *what the code does*, statement by
statement: validate, call the gateway, return an ID. What you **cannot**
tell from the code alone: Is this safe to call twice with the same
arguments (is it idempotent), or will retrying after a timeout double-
charge the customer? Does `create_charge` block, and for how long, under
gateway outages? Is `amount_cents` in the customer's local currency or
always USD? What exceptions can `payment_gateway.create_charge` raise,
and which of those should the caller catch? None of this is visible by
reading the function body — it depends on behavior of a collaborator
(`payment_gateway`), on operational assumptions, and on business rules
that live outside this one function's syntax. This is precisely the gap
documentation — starting with a docstring, in §5 — exists to close: not
by restating what the code does, but by making its non-obvious
assumptions and contracts explicit.

**Why do different people need different documentation?** A single
project is read by several distinct audiences, and each one needs a
different *kind* of answer:

- **Beginner user** — "How do I install and run this?" (README, §23)
- **Developer / integrator** — "What does this function do, what does
  it return, what can go wrong?" (docstrings, API docs, §5, §41)
- **Maintainer** — "How is this system organized, and why was it built
  this way?" (architecture docs, ADRs, §58–59)
- **Reviewer** — "Does this change do what it claims, and is the public
  contract still honored?" (docstrings + PR description, §37)
- **Operator / on-call engineer** — "The service is down — what do I
  do?" (runbooks, §78)
- **API consumer** — "What are the inputs, outputs, errors, and
  guarantees of this interface?" (API contracts, §22, §41)
- **DevOps engineer** — "How is this deployed, configured, and rolled
  back?" (operational documentation, §77)
- **Data engineer** — "What schema does this pipeline expect and
  produce, and how does it fail?" (§60)
- **ML engineer** — "What are the model's input/output contracts and
  known limitations?" (§61)
- **AI engineer** — "What tools can this agent call, what happens on
  failure, and what are its safety boundaries?" (§62–63)

A README written for a beginner user and an ADR written for a future
maintainer are both "documentation," but they answer completely
different questions, at different depths, for different readers. Much
of this chapter is about matching the *right kind* of documentation to
the *right* audience and question — writing an architecture document
where a one-line docstring would do is as much a mistake as omitting a
docstring where one is needed.

## 2. Documentation Types

Rather than treating "documentation" as one undifferentiated thing,
professional projects separate it into categories, each with its own
purpose, audience, and typical location.

| Type | Purpose | Primary audience | Typical example |
|---|---|---|---|
| **Code documentation** | Explain what a specific function/class/module does and how to call it correctly | Developers reading or calling the code | A docstring on `charge_customer()` |
| **API documentation** | Define the contract of a public interface (inputs, outputs, errors, guarantees) | API consumers, integrators | Generated reference for a Python package or HTTP endpoint |
| **User documentation** | Explain how to install, configure, and use the software | End users, beginner developers | `README.md`, a "Getting Started" guide |
| **Developer documentation** | Explain how to set up a dev environment, run tests, and contribute | Contributors, new team members | `CONTRIBUTING.md`, dev setup guide |
| **Project documentation** | Explain what the project is, its scope, status, and history | Anyone evaluating or joining the project | `README.md` overview, `CHANGELOG.md` |
| **Operational documentation** | Explain how to deploy, monitor, and recover the running system | Operators, on-call engineers, SRE | Runbooks, deployment guides |
| **Architecture documentation** | Explain how the system is structured and why | Maintainers, new engineers, architects | Architecture overview, ADRs |

These categories overlap in practice — a README often contains a slice
of user documentation *and* a slice of developer documentation — but
keeping the categories distinct in your head is what prevents a README
from either ballooning into an unusable wall of text, or omitting
information a reader genuinely needs because "it's somewhere else." The
rest of this chapter builds out each of these categories in order,
starting from the smallest unit — the docstring — and ending at
production-scale operational and AI-system documentation.

## 3. What Is a Docstring?

**What is a docstring?** A **docstring** (documentation string) is a
string literal written as the very first statement inside a function,
method, class, or module. Python treats it specially: it is stored on
the object's `__doc__` attribute, retrievable at runtime, and read by
tools like `help()`, IDEs, and documentation generators.

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price."""
    return price * quantity
```

**Where does the docstring go, and why does placement matter?** It must
be the *first statement* in the function body — before any other code,
including other strings or comments. Python's compiler looks
specifically at the first statement of a function/class/module body: if
it's a plain string literal, that string becomes `__doc__`; if anything
else comes first, there is no docstring, regardless of what strings
appear later.

```python
def bad_example():
    x = 1
    """This is NOT a docstring — it's just an unused string literal."""
    return x

print(bad_example.__doc__)  # None
```

**How does Python store a docstring, and how do you read it back?**
Every function, class, and module has a `__doc__` attribute, set
automatically to the docstring string (or `None` if there isn't one):

```python
>>> def calculate_total(price: float, quantity: int) -> float:
...     """Calculate the total price."""
...     return price * quantity
...
>>> print(calculate_total.__doc__)
Calculate the total price.
>>> help(calculate_total)
Help on function calculate_total in module __main__:

calculate_total(price: float, quantity: int) -> float
    Calculate the total price.
```

`help()` is a built-in function that reads `__doc__` (along with the
signature) and prints a formatted summary — this is the same mechanism
IDEs use to show a tooltip when you hover over a function call, and the
same mechanism documentation generators (§42–46) use to build reference
pages, entirely from your source code.

**Triple-quoted strings**, as a Python syntax feature, are not
exclusive to docstrings — `"""..."""` and `'''...'''` are simply string
literals that can span multiple lines. Docstrings conventionally use
triple double-quotes (`"""`) even for one-line docstrings, both because
multi-line docstrings need triple quotes anyway and because it signals
"this is a docstring" to both humans and tools at a glance. `PEP 257`
(Python's docstring convention) and tools like Ruff (§67) enforce or
encourage this convention.

Docstrings apply at four levels, covered in depth in §5, §15, §17, and
§18 respectively:

```python
def function_docstring():
    """A function docstring."""

class ExampleClass:
    """A class docstring."""

    def method_docstring(self):
        """A method docstring."""

"""A module docstring — written at the very top of a .py file,
before any imports."""
```

## 4. Comments vs Docstrings

This distinction is one of the most important in this chapter, and it
is frequently blurred by beginners, so it is worth stating precisely.

| Aspect | `# comment` | `"""docstring"""` |
|---|---|---|
| **Syntax** | Line starting with `#` | String literal as the first statement in a function/class/module |
| **Location** | Anywhere in the code | Only as the first statement of a function, class, or module |
| **Purpose** | Explain *why* a specific line/block of code does something non-obvious | Explain *what* a function/class/module does, its contract, and how to use it |
| **Runtime accessibility** | **Discarded** by the interpreter — not stored anywhere, not inspectable at runtime | **Stored** as `__doc__` — inspectable at runtime via `obj.__doc__` or `help(obj)` |
| **Tooling support** | Not read by `help()`, IDE tooltips, or documentation generators | Read by `help()`, IDE tooltips, `pydoc`, Sphinx, MkDocs, and type checkers' hover info |
| **Intended audience** | Someone reading *this specific line* of source code | Someone *calling* the function/class, possibly without ever opening the source file |

```python
def calculate_discount(price: float, is_loyalty_member: bool) -> float:
    """Calculate the discounted price for a customer.

    Loyalty members receive an additional 5% off on top of any
    standing sale discount already applied to `price`.
    """
    # Loyalty discount is applied multiplicatively, not additively,
    # per finance's 2024 pricing policy — do not change to price - 0.05.
    if is_loyalty_member:
        price *= 0.95
    return price
```

The docstring tells a *caller* — who may never read this function's
body — what the function does and what "loyalty member" pricing means.
The comment tells a *maintainer* editing this exact line why the
multiplication (`*=`), rather than the seemingly-equivalent subtraction
a future editor might reach for, is deliberate — information that is
irrelevant to a caller and would be noise in the docstring.

**When is a comment appropriate?** When something about a specific line
or block is non-obvious *from the code itself* — a workaround for a bug
in a dependency, a reason a "simpler" alternative was rejected, a
reference to a ticket or spec that constrains this exact
implementation. **When is a docstring appropriate?** Whenever a
function, class, or module has a public contract another person (or
your future self) needs to understand without reading its
implementation. A common mistake is writing a comment that merely
restates the next line (`# add one to x` above `x += 1`) — this is
noise, not documentation, in either form; see §71 for what should *not*
be documented at all.

## 5. Function Docstrings

A function docstring's job is to describe the function's **contract**:
what it needs, what it returns, and what can go wrong — everything a
caller must know *without reading the implementation*.

```python
def divide(a: float, b: float) -> float:
    """Divide a by b.

    Raises:
        ZeroDivisionError: If b is zero.
    """
    return a / b
```

Even for a function this small, the docstring adds something the
signature alone (even a fully typed one) does not: it tells the caller
*explicitly* that `b == 0` is a documented failure mode, not an
oversight — information a caller needs to decide whether to validate
`b` beforehand or wrap the call in a `try`/`except`.

A more realistic example, showing the range of things worth
documenting — parameters, return value, side effects, exceptions, and
an important assumption:

```python
def charge_customer(customer_id: str, amount_cents: int) -> str:
    """Charge a customer through the payment gateway.

    This call is NOT idempotent: calling it twice with the same
    arguments creates two separate charges. Callers that may retry
    on timeout must implement their own deduplication (e.g. an
    idempotency key) before invoking this function again.

    Args:
        customer_id: The gateway's customer identifier, not the
            internal database ID.
        amount_cents: Amount to charge, in cents, in the customer's
            billing currency. Must be positive.

    Returns:
        The gateway's charge ID, used to look up or refund the
        charge later.

    Raises:
        ValueError: If amount_cents is not positive.
        GatewayTimeoutError: If the gateway does not respond within
            the configured timeout. The charge may or may not have
            succeeded on the gateway's side — see the idempotency
            note above before retrying.
    """
    if amount_cents <= 0:
        raise ValueError("amount_cents must be positive")
    payment = payment_gateway.create_charge(customer_id, amount_cents)
    return payment.id
```

**What should be documented here, and why?** The non-idempotency
warning, because it changes how a caller must handle retries — this is
exactly the kind of assumption that was invisible from the code alone
in §1. The distinction between `customer_id` (gateway ID) and "the
internal database ID," because a caller could easily pass the wrong ID
and get a confusing runtime error instead of a documented mismatch. The
exceptions, because `except Exception` around this call would silently
swallow the ambiguous-charge-state case the docstring is warning about.

**What should *not* be documented?** That the function "calls
`payment_gateway.create_charge`" — that's visible from reading the one-
line body, and restating it adds nothing (§71 develops this principle
further). A docstring documents the *contract*, not a narration of the
implementation.

## 6. Docstring Content

Not every docstring needs every possible section — a one-line function
with an obvious contract needs a one-line docstring, and padding it out
with empty `Args:`/`Returns:` sections is noise, not rigor. The common
components, used *as needed*, are:

- **Summary** — one line, present tense, stating what the function
  does. Always present, even in a one-line docstring.
- **Detailed description** — additional paragraphs, only when the
  summary alone leaves out something important (a warning, a subtlety,
  a business rule).
- **Parameters** — what each parameter means, when its meaning isn't
  fully obvious from its name and type (§8, §12).
- **Return value** — what is returned and what it represents,
  especially when the return type alone doesn't convey meaning (e.g. an
  `int` that's actually a specific kind of ID).
- **Exceptions** — which exceptions the caller should expect and
  potentially handle (only the ones that are part of the *documented*
  contract, not every exception Python could theoretically raise).
- **Examples** — a short, runnable usage snippet, when usage isn't
  obvious from the signature alone (§31, §50).
- **Side effects** — anything the function does besides computing and
  returning a value: writing a file, sending a network request,
  mutating a shared object, logging.
- **Notes / Warnings** — caveats that don't fit cleanly elsewhere
  (performance characteristics, thread-safety, deprecation).

The governing principle, worth committing to memory because it recurs
throughout this chapter (§70–71):

> **Document what is useful and non-obvious.** If a fact is already
> obvious from the function's name, type hints, or a one-line
> implementation, restating it in prose adds maintenance cost without
> adding information.

```python
def get_user_count() -> int:
    """Return the number of registered users."""
    return len(_users)
```

This one-line docstring is complete. Adding an `Args:` section (there
are no parameters), a `Returns:` section restating "Returns an int"
(the return type already says that; the summary already says what it
represents), or a `Raises:` section for exceptions this function cannot
raise would all violate the principle above.

## 7. Docstring Styles

A **docstring style** is a convention for how the structured parts of a
docstring (parameters, returns, raises, examples) are formatted as
text. Python does not enforce or define a style — `__doc__` is just a
string; everything past that is convention, chosen by a project or
team so that every docstring in the codebase reads consistently and so
that automated tools (documentation generators, IDEs) can parse the
structure. Three styles are common in the Python ecosystem: **Google
style**, **NumPy style**, and **Sphinx/reStructuredText style**. Here
is the *same* function documented in all three, so the structural
differences are visible side by side:

**Google style** (§8):

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    Args:
        price: Unit price.
        quantity: Number of items.

    Returns:
        The total price.
    """
    return price * quantity
```

**NumPy style** (§9):

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    Parameters
    ----------
    price : float
        Unit price.
    quantity : int
        Number of items.

    Returns
    -------
    float
        The total price.
    """
    return price * quantity
```

**Sphinx / reStructuredText style** (§10):

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    :param price: Unit price.
    :param quantity: Number of items.
    :return: The total price.
    """
    return price * quantity
```

Do not try to memorize all three as equally important — you will
mostly write in whichever style your project or team has already
chosen (§11). What matters is recognizing all three on sight, since
you'll encounter each of them reading other people's code, and knowing
that the *choice* is a team convention, not a Python language rule.

## 8. Google-Style Docstrings

**Google-style docstrings** use plain-English section headers
(`Args:`, `Returns:`, `Raises:`, etc.) followed by indented lines. It's
the most widely used style in modern application code because it reads
naturally even in a plain-text editor with no rendering.

```python
def calculate_total(
    price: float,
    quantity: int,
) -> float:
    """Calculate the total price.

    Args:
        price: Unit price.
        quantity: Number of items.

    Returns:
        The total price.
    """
    return price * quantity
```

The sections you'll use most, each included **only when it applies**:

- **`Args:`** — one line per parameter: `name: description.` (no type
  in parentheses when a type hint is already present — see §14).
- **`Returns:`** — describes what the return value *means*, not merely
  its type.
- **`Raises:`** — one line per documented exception: `ExceptionType: In
  what condition it's raised.`
- **`Examples:`** — a short usage snippet, often written as a `doctest`
  block (§50) so it can be executed and verified.
- **`Notes:`** — caveats that don't belong under the other headers.
- **`Yields:`** — used instead of `Returns:` for a generator function,
  describing what each yielded value represents.
- **`Attributes:`** — used in class docstrings (§15) to document
  instance attributes, not function parameters.

```python
def stream_lines(path: str):
    """Yield each non-empty line from a text file.

    Args:
        path: Path to the file to read.

    Yields:
        Each non-empty line, with trailing whitespace stripped.
    """
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                yield stripped
```

## 9. NumPy-Style Docstrings

**NumPy-style docstrings** use section headers underlined with dashes,
and put each parameter's type on its own header-like line, with the
description indented below it:

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    Parameters
    ----------
    price : float
        Unit price.
    quantity : int
        Number of items.

    Returns
    -------
    float
        The total price.

    Raises
    ------
    ValueError
        If quantity is negative.

    Examples
    --------
    >>> calculate_total(2.5, 4)
    10.0
    """
    if quantity < 0:
        raise ValueError("quantity must be non-negative")
    return price * quantity
```

**Why is NumPy-style common specifically in scientific Python, data
science, and machine learning?** Because it originated in — and is used
throughout — NumPy, SciPy, pandas, and scikit-learn, and it handles a
case those libraries hit constantly better than Google style does:
documenting functions with many parameters, each carrying array
shapes, dtypes, and units, where the two-line "type on its own line,
description below" layout stays readable even for a function with a
dozen parameters. If you work with these libraries, you will read (and
likely write) far more NumPy-style docstrings than Google-style ones.

## 10. Sphinx-Style Docstrings

**Sphinx-style** (also called **reStructuredText style**, after the
markup language it's written in) uses inline field markers rather than
section headers:

```python
def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    :param price: Unit price.
    :param quantity: Number of items.
    :return: The total price.
    :raises ValueError: If quantity is negative.
    """
    if quantity < 0:
        raise ValueError("quantity must be non-negative")
    return price * quantity
```

`:param name:`, `:return:`, and `:raises ExceptionType:` are
reStructuredText field lists — the same markup Sphinx (§44) uses
throughout its documentation source files, which is why this style
integrates most directly with Sphinx-generated documentation. **Where
does this style still appear in practice?** Mostly in older or
long-established Python projects (many predating Google-style's
popularity), and in projects that build their documentation site
directly with Sphinx and want docstrings to match the surrounding
`.rst` files' syntax. You are unlikely to *choose* this style for a new
project today, but you will encounter it reading mature libraries'
source.

## 11. Choosing a Docstring Style

No style is universally "best" — each trades off differently:

| Consideration | Google | NumPy | Sphinx/RST |
|---|---|---|---|
| **Readability as plain text** | High — reads like prose | Medium — dash-underlines add visual noise in a plain editor | Low — field markers (`:param:`) read awkwardly unrendered |
| **Verbosity** | Compact | More vertical space (type + description on separate lines) | Compact |
| **Best fit** | General application/backend code | Scientific/numerical code with many typed parameters | Projects already built around Sphinx/`.rst` |
| **Tooling** | Supported by Sphinx (via `napoleon` extension), MkDocs plugins, most IDEs | Supported by Sphinx (via `napoleon`), MkDocs plugins | Native Sphinx support, no extension needed |
| **Ecosystem convention** | Common in Google's own style guide, FastAPI, many backend frameworks | NumPy, SciPy, pandas, scikit-learn, most of scientific Python | Older libraries, Sphinx-first projects |

**The practical decision**: pick one style for a project (or adopt
whatever your team/employer already uses) and apply it consistently.
The cost of *inconsistency* — some functions in Google style, others
in NumPy style, in the same codebase — is higher than the cost of
picking either "acceptable" style: readers build a mental parser for
one format, and switching formats mid-codebase breaks that parser on
every function. For general backend/application/AI-engineering work —
the kind this course is building toward — **Google style is a
reasonable default**: it's compact, reads well unrendered, and is
widely understood.

## 12. Function Docstring Best Practices

- **Write concise, imperative summaries.** `"""Calculate the total
  price."""`, not `"""This function will calculate the total
  price."""` — the imperative mood ("Calculate," "Return," "Raise") is
  shorter and is the convention `PEP 257` and most style guides
  recommend.
- **Write meaningful parameter descriptions**, not restatements of the
  name. `quantity: Number of items.` adds little over the name alone;
  `quantity: Number of items, before any bulk discount is applied.`
  adds real information.
- **Document non-obvious behavior explicitly** — idempotency,
  ordering guarantees, caching, mutation of arguments.
- **Document exceptions that are part of the contract**, not every
  exception Python could theoretically raise (a `TypeError` from
  passing the wrong type is usually not worth documenting when type
  hints already communicate the expected type — see §14).
- **Avoid redundant type information when type hints already provide
  it** (§13–14) — this is one of the most common docstring mistakes and
  gets its own section below.
- **Document side effects** — network calls, file writes, global-state
  mutation, logging with side effects (e.g. emitting a metric).
- **Document important constraints** — value ranges, required
  ordering of calls, thread-safety assumptions.

**Poor vs. good, side by side:**

```python
# Poor — vague, restates the name, no exception info
def send_email(to: str, subject: str, body: str) -> bool:
    """Send an email."""
    ...

# Good — states the contract precisely
def send_email(to: str, subject: str, body: str) -> bool:
    """Send a transactional email via the configured SMTP relay.

    This call blocks until the relay accepts or rejects the message;
    it does not guarantee final delivery to the recipient's inbox.

    Returns:
        True if the relay accepted the message, False if it was
        rejected (e.g. invalid address). Network failures raise
        SMTPConnectionError rather than returning False.

    Raises:
        SMTPConnectionError: If the relay cannot be reached.
    """
    ...
```

## 13. Type Hints + Docstrings

This section connects directly to the previous chapter,
[`06-type-hints-and-type-checking.md`](./06-type-hints-and-type-checking.md).
Type hints and docstrings are **complementary layers**, not competing
ways of documenting the same thing — each communicates something the
other cannot.

```python
def create_user(user_id: int, email: str) -> User:
    """Create and persist a new user account.

    A duplicate email raises DuplicateEmailError rather than
    returning an existing user — callers must not assume this
    function is safe to call twice with the same email.

    Args:
        user_id: Caller-supplied identifier; must be unique and is
            NOT generated by this function.
        email: Must already be validated as a well-formed address —
            this function does not validate email format itself.

    Raises:
        DuplicateEmailError: If a user with this email already exists.
    """
    ...
```

| Layer | Communicates | Checked by |
|---|---|---|
| **Type hints** (`user_id: int`, `-> User`) | The *shape* of data: what type each parameter and the return value is | A static type checker (mypy/Pyright), at development time, without running the code |
| **Docstring** (the prose above) | The *behavior*, *meaning*, *constraints*, *side effects*, and *business rules* around that data | Nothing automatically — it's read by humans, `help()`, and documentation generators |

The type hint `user_id: int` tells a caller and a type checker "pass an
`int` here" — but it says nothing about *whose* `int` this should be
(caller-supplied vs. auto-generated), which is exactly the kind of
fact that changes how correctly a caller can use the function and that
only the docstring communicates. Neither layer replaces the other:
removing the type hints would leave a type checker unable to catch
`create_user("abc", "x@example.com")`; removing the docstring would
leave a caller unable to discover the duplicate-email behavior without
reading the implementation.

## 14. When Not to Document Types

**The principle**: if a type hint already communicates a value's type
unambiguously, repeating that exact type in the docstring's prose is
redundant — it adds words without adding information, and it is a
second place that can drift out of sync with the code the next time
the signature changes.

```python
# Bad — repeats the type hint in prose; now two things can go stale
def create_user(name: str, age: int) -> None:
    """Create a user.

    Args:
        name (str): A string containing the name.
        age (int): An integer representing the age.
    """

# Better — the type hint already says str/int; the docstring adds
# what the type hint cannot: meaning and constraints
def create_user(name: str, age: int) -> None:
    """Create a user.

    Args:
        name: User's display name, shown publicly on their profile.
        age: User's age in years; must be 13 or older (COPPA).
    """
```

Note this is a *style choice for typed codebases specifically* — it's
why Google-style docstrings written alongside type hints normally drop
the `(str)`/`(int)` parenthetical that the plain Google-style spec
otherwise allows, and why NumPy-style docstrings (which put the type on
its own line unconditionally, §9) are more redundant with type hints
by construction. When a codebase has no type hints at all (rare in new
code, common in legacy code — see §81 of the previous chapter),
documenting the type in prose is not redundant, because there is no
other source of truth for it.

## 15. Class Docstrings

A class docstring describes what the class **represents** and what its
**instances** guarantee — its purpose, important state, and usage
assumptions — not a restatement of its method list (which is already
visible via `dir()` or an IDE).

```python
class BankAccount:
    """Represent a customer's bank account.

    A BankAccount enforces a non-negative balance invariant: no
    operation on this class can leave `balance` below zero. Deposits
    and withdrawals are not thread-safe — concurrent calls on the
    same instance from multiple threads can violate the invariant
    above.

    Attributes:
        account_id: Unique identifier assigned at creation.
        balance: Current balance in the account's currency, in cents.
    """

    def __init__(self, account_id: str, balance: int = 0) -> None:
        self.account_id = account_id
        self.balance = balance

    def withdraw(self, amount: int) -> None:
        """Withdraw amount cents from the account.

        Raises:
            InsufficientFundsError: If amount exceeds the balance.
        """
        if amount > self.balance:
            raise InsufficientFundsError(self.account_id)
        self.balance -= amount
```

**What to document on a class**: its **purpose** (what real-world or
domain concept it represents), any **invariants** it maintains (the
non-negative balance above), important **state** it holds, **lifecycle**
concerns (must `connect()` be called before other methods?), **side
effects** of construction or common methods, exceptions its methods can
raise as part of their contract, and **usage assumptions** (thread-
safety, whether instances are meant to be reused or are single-use).

## 16. Class Attribute Documentation

Attributes are documented in two places, depending on what they are:

**Instance attributes**, set in `__init__`, are documented in the class
docstring's `Attributes:` section, as shown in §15 above — Python
itself has no dedicated syntax for "attribute docstrings," so the
class docstring is the conventional place.

**`ClassVar`** attributes (shared across all instances, not per-
instance state) benefit from an inline comment or a brief docstring-
style note, since their "shared, not per-instance" nature is easy to
miss:

```python
from typing import ClassVar

class RateLimiter:
    """Enforce a shared request-rate limit across all instances."""

    # Shared across every RateLimiter instance — intentional, since
    # the limit applies process-wide, not per limiter.
    _global_request_count: ClassVar[int] = 0
```

**Dataclass fields** are self-documenting to a degree via their type
hints and defaults, but non-obvious fields still benefit from the class
docstring's `Attributes:` section:

```python
from dataclasses import dataclass

@dataclass
class RetryPolicy:
    """Configuration for how a failed operation should be retried.

    Attributes:
        max_attempts: Total attempts including the first, not the
            number of *retries* — max_attempts=1 means no retry.
        backoff_seconds: Base delay before the first retry; doubles
            after each subsequent failure (exponential backoff).
    """

    max_attempts: int = 3
    backoff_seconds: float = 1.0
```

The `max_attempts` note above is a good example of *why* attribute
documentation is useful even with type hints present: `int` says
nothing about the off-by-one ambiguity ("attempts" vs. "retries") that
a caller could easily get wrong without the docstring.

## 17. Method Docstrings

**When should a method have a docstring?**

- **Public methods** — almost always, following the same rules as
  function docstrings (§5), since they're part of the class's public
  contract.
- **Internal / private methods** (conventionally prefixed with a single
  underscore, `_helper`) — only when their behavior is genuinely non-
  obvious; a short, clear implementation with a good name often needs
  no docstring at all (§71).
- **"Private" methods** (double-underscore-prefixed, triggering name
  mangling) — same standard as single-underscore methods; the
  mangling is about attribute access, not documentation policy.
- **Property methods** (`@property`) — document them like an attribute
  (what the value represents), not like a method with parameters, since
  callers use them as `obj.value`, not `obj.value()`.
- **Special methods** (`__init__`, `__eq__`, `__repr__`, etc.) —
  document them when their behavior isn't the obvious default; `__eq__`
  comparing by `id` alone vs. by field values is exactly the kind of
  thing worth one line.

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self._celsius = celsius

    @property
    def fahrenheit(self) -> float:
        """Temperature in degrees Fahrenheit, derived from Celsius."""
        return self._celsius * 9 / 5 + 32

    def _clamp(self, value: float) -> float:
        # Trivial, obvious from the name and one-line body — no
        # docstring needed.
        return max(-273.15, value)
```

**Why not every trivial method needs a large docstring**: a one-line
`_clamp` helper with an obvious name and body gains nothing from a
`Args:`/`Returns:` block — the maintenance cost (another place to keep
in sync) outweighs the near-zero information the docstring would add.
This is the same "document what is useful and non-obvious" principle
from §6, applied at the method level.

## 18. Module Docstrings

A **module docstring** is a docstring placed as the very first
statement in a `.py` file — before any imports — describing the
module's overall purpose, scope, and public API at a glance.

```python
"""Utilities for processing customer transaction data.

This module provides pure functions for validating, normalizing,
and aggregating transaction records read from the billing pipeline.
It performs no I/O itself — callers are responsible for reading
input and writing output.
"""

from __future__ import annotations

import datetime


def normalize_amount(raw: str) -> int:
    """Convert a raw currency string like '$12.50' to integer cents."""
    ...
```

```python
>>> import transactions
>>> print(transactions.__doc__)
Utilities for processing customer transaction data.

This module provides pure functions for validating, normalizing,
and aggregating transaction records read from the billing pipeline.
It performs no I/O itself — callers are responsible for reading
input and writing output.
```

**What belongs in a module docstring**: the module's **purpose** (why
this file exists, as opposed to any other), its **scope** (what it does
and, often more usefully, what it deliberately does *not* do — "no I/O
itself" above), important **behavior** that applies to the whole module
rather than one function, its intended **public API** (which names
callers should import), and **module-level assumptions** (e.g. "assumes
naive datetimes are UTC"). A module docstring is the first thing a
reader — or a documentation generator (§42) — sees when opening the
file, so it earns its keep by orienting a reader before they scroll
into implementation details.

## 19. Package Documentation

A **package** — a directory of modules with an `__init__.py` — needs
documentation at a *higher* level than any single module: what the
package as a whole is for, which of its modules/classes/functions form
its supported public interface, how to install it, and how to use it
at a glance.

**What belongs in package-level documentation** (typically split
between the package's `__init__.py` docstring and its `README.md`,
§20):

- **Package purpose** — the problem this whole package solves.
- **Public modules** — which submodules are meant to be imported
  directly by users, versus internal implementation detail.
- **Public classes/functions** — the small set of names most users need,
  highlighted rather than making a reader discover them by browsing
  every module.
- **Usage examples** — a minimal end-to-end example using the package
  as a whole, not any single function in isolation.
- **Dependencies** — what this package requires (delegated to
  `pyproject.toml`, §66, for the authoritative machine-readable list,
  but often summarized in prose).
- **Installation** — how to add this package as a dependency.

**How package documentation differs from individual module
documentation**: a module docstring (§18) answers "what does *this
file* do"; package documentation answers "what does this *entire
library* do, and where do I start?" A user evaluating whether to adopt
a package reads package-level documentation first (often the README) —
they only descend to individual module docstrings once they've decided
to use it and need details on a specific function.

## 20. `__init__.py` Documentation

Package-level documentation relates to `__init__.py` in two related
but distinct ways, worth keeping separate:

**1. The package docstring.** `__init__.py`'s own docstring (its first
statement) becomes the package's `__doc__`, exactly like a module
docstring:

```python
# my_package/__init__.py
"""my_package: utilities for validating and normalizing billing data.

See the project README for installation and full usage examples.
"""

from my_package.validation import validate_amount
from my_package.normalization import normalize_currency

__all__ = ["validate_amount", "normalize_currency"]
```

**2. Public exports via `__all__`.** `__all__` is a list of names that
defines what `from my_package import *` imports, and is read by some
documentation generators and IDEs as a signal of the package's intended
public API.

**Why these are related but different concerns**: the package
docstring is prose — it *describes* the package for a human reader.
`__all__` is executable — it *controls* import behavior and signals
(but does not enforce) which names are public. Setting `__all__`
without a package docstring leaves a reader knowing *which* names are
public but not *why the package exists*; writing a great docstring
without `__all__` leaves the *supported* interface ambiguous, since
nothing distinguishes `validate_amount` (meant for external use) from
an internal helper that happens to also be importable. Use both
together: the docstring orients a reader, `__all__` disambiguates the
supported surface for tools and `import *`.

## 21. Public vs Private APIs

**Public API**: the functions, classes, and methods a project commits
to keeping stable — external code is expected and safe to depend on
them. **Private / internal implementation**: everything else — helpers
that exist to support the public API internally, and that the project
reserves the right to change or remove without notice.

Python signals this by convention, not enforcement: a single leading
underscore (`_helper`) means "internal — not part of the public
contract," even though nothing stops external code from importing and
calling it anyway.

```python
def process_order(order: Order) -> Receipt:
    """Process a customer order and return a receipt.

    This is the package's public entry point for order processing.
    """
    _validate_order(order)
    return _build_receipt(order)


def _validate_order(order: Order) -> None:
    # Internal helper — not part of the public contract. May change
    # signature or be removed without a deprecation notice.
    ...
```

**How documentation communicates supported usage**: `process_order`
gets a full docstring, because callers are meant to rely on its
contract staying stable. `_validate_order` may get a one-line note (or
none at all, per §17) precisely *because* it isn't a promise to
anyone — documenting it as thoroughly as a public function would
misleadingly suggest it's equally safe to depend on. **Why documenting
every private helper as heavily as public functions creates
maintenance overhead**: every fully-documented function is a
*commitment* readers reasonably interpret as "this interface won't
change casually." Over-documenting internals either creates a false
sense of stability, or creates busywork updating detailed docs for
code that's expected to churn freely.

## 22. API Contracts

Documentation, taken together, functions as an **API contract**: an
explicit statement of what a caller can rely on, and what remains the
implementation's discretion to change.

A realistic Python service function, with its contract made explicit:

```python
def get_user_profile(user_id: int) -> UserProfile:
    """Fetch a user's public profile.

    Input expectations:
        user_id must refer to an existing, non-deleted user. Deleted
        users are NOT distinguished from nonexistent ones — both
        raise UserNotFoundError, by design, to avoid leaking deletion
        status to callers without appropriate permission.

    Output behavior:
        Returns a UserProfile containing only publicly-visible
        fields. Email and other private fields are never included,
        regardless of caller permissions — use get_user_private() for
        those, which requires an authenticated admin context.

    Errors:
        UserNotFoundError: user_id does not resolve to a visible user.

    Side effects:
        Increments the user's `profile_view_count` — this function
        is NOT read-only despite its name.

    Compatibility:
        The returned UserProfile's field set is considered a stable
        public contract; new fields may be added, but existing
        fields will not be removed or repurposed without a major
        version bump (see CHANGELOG.md).
    """
    ...
```

Every clause above is a promise (or an explicit *non*-promise) a caller
can build on: the not-read-only side effect prevents a caller from
assuming it's safe to call speculatively; the compatibility note tells
a caller which changes would count as breaking (§75) versus additive.
This is the fullest expression of what a function docstring is *for* —
everything §5–§17 built up to.

## 23. README Files

**What is `README.md`?** The single file, conventionally at a
repository's root, that a reader (or a hosting platform like GitHub)
sees first when they open the project. **Why does almost every serious
repository need one?** Because it is the answer to the very first
questions any new reader has — "what is this, and how do I use it" —
before they've read a single line of actual code.

**Who reads it?** Everyone, at some point: a beginner deciding whether
to try the project, a developer integrating it as a dependency, a
teammate setting up a local dev environment, a reviewer orienting
themselves on an unfamiliar PR, even the project's own author six
months later.

**What should the first 30 seconds tell the reader?** What the project
*is* (one or two sentences), and roughly how to get it running. A
README that opens with a wall of badges, a long philosophical
introduction, or buries the installation instructions on page three of
scrolling has failed at its primary job.

**README as the project's front door**: it is not comprehensive
documentation (that's what architecture docs, API references, and
runbooks are for, elsewhere in this chapter) — it is the entry point
that orients a reader and routes them to whatever deeper documentation
they actually need next.

## 24. README Structure

A practical, commonly-used structure, built up section by section:

- **Project name** — the repository's name, as a top-level heading.
- **Overview** — one to three sentences: what problem this solves.
- **Problem solved** — one paragraph of context, if the overview alone
  isn't enough (often merged into Overview for small projects).
- **Features** — a short bullet list of what the project actually does.
- **Architecture overview** — only when useful; a one-paragraph or
  one-diagram summary, with a link to full architecture docs (§58) for
  anything larger than a paragraph.
- **Prerequisites** — required Python version, OS, external services.
- **Installation** — exact commands to get dependencies installed.
- **Setup** — anything beyond `pip`/`uv install`: database migrations,
  seed data, generated files.
- **Configuration** — environment variables and config files (§27).
- **Usage** — how to actually run the thing, with example commands.
- **Examples** — runnable snippets beyond basic usage.
- **CLI commands** — for CLI projects, the commands and flags available.
- **Testing** — how to run the test suite.
- **Development** — dev-specific setup (linting, type checking).
- **Project structure** — a short directory tree with one-line
  descriptions, for larger projects.
- **Troubleshooting** — common problems and fixes (§30, §79).
- **Contribution** — link to `CONTRIBUTING.md` (§56), or inline basics.
- **License** — the project's license.
- **Security / contact information** — where relevant, how to report a
  security issue, or who to contact.

**Not every project needs every section.** A small personal script
needs Overview, Installation, and Usage — nothing more. A production
service intended for a team needs most of the list. Padding a small
project's README with empty "Contribution" and "License" sections
because a checklist demands them is exactly the kind of unnecessary
documentation §71 warns against.

## 25. README for Beginners

A README should let a new developer go from **clone → install →
configure → run → test**, without needing to ask the author a single
basic question. Concretely, that means every step in the chain has an
*exact, copy-pasteable command* — not a description of a command.

```markdown
## Installation

1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/example/billing-service.git
   cd billing-service
   \`\`\`

2. Install dependencies (requires Python 3.12+ and `uv`):
   \`\`\`bash
   uv sync
   \`\`\`

3. Copy the example environment file and fill in your values:
   \`\`\`bash
   cp .env.example .env
   \`\`\`

4. Run the service:
   \`\`\`bash
   uv run python -m billing_service
   \`\`\`

5. Run the test suite to confirm everything works:
   \`\`\`bash
   uv run pytest
   \`\`\`
```

Every one of these five steps is a command the reader can copy
verbatim, in the *order* they must run them, with any prerequisite
(Python 3.12+, `uv`) stated *before* it's needed rather than discovered
via an error message. A README that instead says "install the
dependencies and configure your environment" forces the reader to
guess the exact commands — precisely the kind of basic question a good
README exists to make unnecessary.

## 26. README Installation Documentation

Connecting directly to the earlier chapters in this module
([`03-pyproject-lock-files-and-uv.md`](./03-pyproject-lock-files-and-uv.md),
[`04-dependency-management-and-semantic-versioning.md`](./04-dependency-management-and-semantic-versioning.md)),
installation documentation should state, precisely and in order:

- **Python version** — the minimum (and, if relevant, maximum)
  supported version, matching `requires-python` in `pyproject.toml`.
- **`uv`** — that the project uses `uv` for dependency management, and
  the one command (`uv sync`) that installs everything from the lock
  file.
- **Dependencies** — that they're declared in `pyproject.toml` and
  pinned in `uv.lock` — README doesn't need to *list* them (that would
  immediately drift, §34); it links to the authoritative files instead.
- **Virtual environment** — that `uv` manages this automatically (no
  manual `python -m venv` step needed), or, if the project doesn't use
  `uv`, the exact `venv` creation and activation commands.
- **Installation commands** — the literal, runnable command sequence.

```markdown
## Prerequisites

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/) for dependency management

## Installation

\`\`\`bash
git clone https://github.com/example/billing-service.git
cd billing-service
uv sync
\`\`\`

This creates a `.venv/` and installs the exact dependency versions
pinned in `uv.lock`. To run any command inside that environment,
prefix it with `uv run`, e.g. `uv run python -m billing_service`.
```

Note what's deliberately **not** here: a hand-maintained list of
package names and versions. That information already lives, as the
single source of truth, in `pyproject.toml`/`uv.lock` (§66) — repeating
it in prose creates a second copy that will inevitably drift the first
time a dependency is bumped.

## 27. README Configuration

Configuration documentation must clearly distinguish **required** vs.
**optional**, state each value's **type** and **default**, and flag
anything **secret** — while never containing a real secret itself.

```markdown
## Configuration

Copy `.env.example` to `.env` and fill in the values below.

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string. |
| `API_KEY` | Yes | — | **Secret.** Payment gateway API key — never commit a real value. |
| `LOG_LEVEL` | No | `INFO` | One of `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
| `REQUEST_TIMEOUT_SECONDS` | No | `30` | HTTP client timeout for outbound gateway calls. |
```

**`.env.example`**, conceptually, is a template file committed to the
repository that lists every configuration variable's *name* with a
placeholder or safe default — never a real value:

```bash
# .env.example — copy to .env and fill in real values. Never commit .env.
DATABASE_URL=postgresql://user:password@localhost:5432/billing
API_KEY=your-api-key-here
LOG_LEVEL=INFO
REQUEST_TIMEOUT_SECONDS=30
```

**Why never include real secrets in documentation**: a README (and its
full git history — deleting a secret in a later commit does not remove
it from history) is often public, or at minimum readable by everyone
with repository access, which is almost always a broader audience than
everyone who should hold a production credential. §76 develops this
into a full documentation-security discussion.

## 28. README Usage

Usage documentation shows the reader **command → expected input →
expected output**, concretely, not abstractly.

```markdown
## Usage

Run the CLI with a customer ID to fetch their current balance:

\`\`\`bash
uv run python -m billing_service balance --customer-id 12345
\`\`\`

Expected output:

\`\`\`text
Customer 12345: $128.50
\`\`\`

Flags:

- `--customer-id INT` (required) — the customer to look up.
- `--currency TEXT` (optional, default `USD`) — display currency.

Example with the currency flag:

\`\`\`bash
uv run python -m billing_service balance --customer-id 12345 --currency EUR
\`\`\`
```

This connects directly to the CLI/`argparse` material from earlier in
your Programming & Computational Thinking track: a `python -m app ...`
invocation, its arguments, its flags, and — critically — what the
reader should actually *see* when it works, so they can confirm success
without guessing.

## 29. CLI Documentation

CLI documentation covers everything a user of a command-line program
needs, beyond a single usage example: the command's **purpose**, its
full **syntax**, every **argument** and **option**, worked **examples**,
its **exit codes**, its **errors**, and any **environment
variables**/**configuration** it reads.

```markdown
### `billing-service balance`

Fetch a customer's current balance.

**Syntax:**
\`\`\`text
billing-service balance --customer-id ID [--currency CODE]
\`\`\`

**Arguments:**

| Argument | Required | Description |
|---|---|---|
| `--customer-id` | Yes | Integer customer ID to look up. |
| `--currency` | No | ISO 4217 currency code (default: `USD`). |

**Exit codes:**

| Code | Meaning |
|---|---|
| `0` | Success. |
| `1` | Customer not found. |
| `2` | Invalid arguments (e.g. non-integer `--customer-id`). |

**Example:**
\`\`\`bash
billing-service balance --customer-id 12345
# Customer 12345: $128.50
\`\`\`
```

**`--help` as documentation**: a well-written CLI, built with `argparse`
(or a similar library), generates a `--help` output automatically from
its argument definitions — and that generated help text *is* a form of
user documentation, arguably the most important one, because it is
always available, always in sync with the actual code (unlike prose
documentation, which can drift — §34), and reachable without leaving
the terminal. Good CLI documentation in a README or docs site is
usually a curated, example-rich *complement* to `--help`, not a
replacement for keeping `--help` itself accurate and well-worded.

## 30. Documentation for Errors

Error documentation follows a consistent, scannable shape: **symptom →
cause → solution → verification.**

```markdown
### Problem: `API_KEY is missing`

**Symptom:** The service fails to start with:
\`\`\`text
ConfigError: API_KEY is missing
\`\`\`

**Cause:** The `API_KEY` environment variable is not set — either
`.env` doesn't exist, or it exists but doesn't define `API_KEY`.

**Solution:**
1. Confirm `.env` exists: `ls .env`
2. If missing, copy the template: `cp .env.example .env`
3. Add your API key to the `API_KEY=` line in `.env`.

**Verification:** Re-run the service; the error should not reappear.
\`\`\`bash
uv run python -m billing_service
\`\`\`
```

This is the atomic unit of **troubleshooting documentation** (built out
fully in §79): every documented error follows the same four-part
shape, so a reader scanning a troubleshooting page always knows exactly
where to look for the piece they need.

## 31. Examples as Documentation

**Why are examples often more useful than long explanations?** Because
a working example lets a reader *pattern-match* their own use case
against something they can run and see succeed, which is usually
faster than parsing prose and mentally simulating what it implies.
Examples should progress in complexity:

**Minimal example** — the smallest possible correct usage:

```python
from billing_service import calculate_total

calculate_total(price=9.99, quantity=3)  # 29.97
```

**Realistic example** — closer to how the function is actually called
in application code:

```python
order_items = [("widget", 9.99, 3), ("gadget", 19.99, 1)]
total = sum(
    calculate_total(price=price, quantity=qty)
    for _, price, qty in order_items
)
print(f"Order total: ${total:.2f}")
```

**Complete example** — a runnable end-to-end script including imports,
setup, and error handling, suitable for copy-pasting into a new file:

```python
"""Example: compute and print an order total, handling bad input."""

from billing_service import calculate_total
from billing_service.errors import InvalidQuantityError

order_items = [("widget", 9.99, 3), ("gadget", 19.99, -1)]

total = 0.0
for name, price, qty in order_items:
    try:
        total += calculate_total(price=price, quantity=qty)
    except InvalidQuantityError:
        print(f"Skipping {name}: invalid quantity {qty}")

print(f"Order total: ${total:.2f}")
```

Presenting all three — not just the complete one — matters: a reader
skimming for "does this function even exist and what does it return"
wants the minimal example; a reader about to integrate it wants the
realistic or complete one. Providing only the complete example forces
every reader to parse the whole thing just to answer the simple
question.

## 32. Good vs Bad Examples

**Bad documentation examples**, and what's wrong with each:

```markdown
<!-- Vague instructions -->
Set up your environment and run the app.

<!-- Missing prerequisites -->
Run: uv run python -m billing_service
(never mentions Python 3.12+ or uv are required first)

<!-- Incomplete command -->
Run pytest to test.
(actual required command is `uv run pytest`, not bare `pytest`,
because dependencies live in a uv-managed venv)

<!-- Outdated example, from before a rename -->
from billing import calc_total   # function was renamed to calculate_total

<!-- Unexplained configuration -->
Set FEATURE_FLAG_7 in your environment.
(no description of what it does or what values it accepts)

<!-- Fake / invented output -->
$ billing-service balance --customer-id 12345
Success!
(the real output format is "Customer 12345: $128.50" — this was
never actually run)

<!-- Missing expected result entirely -->
Run the balance command to check a customer's balance.
(no example command, no example output at all)
```

**Improved versions**, fixing each specific problem:

```markdown
## Prerequisites
Python 3.12+ and uv (https://docs.astral.sh/uv/).

## Installation
\`\`\`bash
uv sync
\`\`\`

## Testing
\`\`\`bash
uv run pytest
\`\`\`

## Usage
\`\`\`python
from billing_service import calculate_total
calculate_total(price=9.99, quantity=3)  # 29.97
\`\`\`

## Configuration
`FEATURE_FLAG_7` (optional, default `false`) — enables the new tax
calculation engine. Set to `true` to opt in early.

## Checking a balance
\`\`\`bash
billing-service balance --customer-id 12345
# Customer 12345: $128.50
\`\`\`
```

Each fix maps directly to a specific named failure above: prerequisites
now stated up front, the exact runnable command used, the current
function name, the flag explained, and the *actual* output shown
instead of an invented one — which leads directly into §33.

## 33. Documentation Accuracy

**Why is incorrect documentation actually dangerous** — worse, in a
real sense, than no documentation at all? Because a reader trusts
documentation by default; wrong documentation doesn't just fail to
help, it actively sends the reader down a wrong path with false
confidence, often costing more time than if they'd had to figure
things out from the code from scratch.

Common sources of inaccurate documentation:

- **Stale commands** — a command that worked at write-time but no
  longer matches the current CLI/API.
- **Wrong package names** — referencing a package that was renamed or
  replaced.
- **Incorrect configuration** — a documented environment variable that
  no longer exists, or whose meaning changed.
- **Outdated screenshots** — a UI walkthrough showing a version of the
  interface that no longer exists.
- **Changed APIs** — a documented function signature that no longer
  matches the actual one.
- **Changed file paths** — instructions referencing a file that has
  since moved.
- **Obsolete behavior** — a documented default or edge case that was
  since changed in code without a corresponding documentation update.

**Why documentation should be tested**: every category above is a
*silent* failure — nothing breaks visibly when documentation goes
stale; it simply sits there, plausible-looking and wrong, until a
reader tries to follow it and it fails. §49–51 (documentation testing,
doctest, executable examples) exist specifically to convert some of
these silent failures into loud, CI-caught ones.

## 34. Documentation Drift

**Documentation drift** is the gradual, usually unintentional process
by which documentation and the code it describes fall out of sync over
time — the specific *mechanism* that produces the stale-documentation
symptoms listed in §33.

**Why it happens** — the causes are almost always changes to the code
that aren't mirrored by a corresponding documentation update:

- **API changes** — a parameter renamed, added, or removed.
- **Refactoring** — internal restructuring that happens to change a
  documented file path or module boundary.
- **Dependency changes** — a library upgrade that changes required
  configuration or minimum versions.
- **Configuration changes** — an environment variable renamed or
  removed.
- **Deployment changes** — a changed hostname, port, or deployment
  command.

**Mitigation** — no single technique eliminates drift, but each reduces
it:

- **Documentation review** — treating documentation updates as a
  required part of code review (§37), not an afterthought.
- **Examples that are actually run** — a doctest (§50) or a tested
  example script fails CI the moment it goes stale, rather than
  silently rotting.
- **Automated checks** — link checkers, CI steps that run documented
  commands.
- **CI integration** — making documentation checks part of the same
  pipeline that gates merges, so drift is caught before it ships.
- **Generated documentation** — API reference generated directly from
  docstrings and type hints (§42, §47) cannot drift from the function
  signature, because it *is* the function signature, rendered.

## 35. Documentation as Code

**Documentation as Code** is the practice of treating documentation
with the same engineering rigor as source code: written in a
plain-text, diffable format (Markdown), stored in the same **Git**
repository as the code it describes, changed via the same **pull
request** workflow, subject to the same **code review**, and validated
by the same **CI** pipeline.

**Why documentation should live close to code when appropriate**:
proximity is what makes the rest of this practice possible. A README
or docstring living *in the same repository and the same commit* as
the code change it describes can be reviewed alongside that change
(§37), and a reviewer can directly compare "does this new parameter
match what the docstring now claims" in a single diff view. Documentation
kept in a completely separate wiki or external tool, with no
connection to the commit that changed the underlying behavior,
structurally cannot be reviewed this way — it becomes an entirely
separate, easily-forgotten task, and is one of the biggest practical
drivers of documentation drift (§34).

This does not mean *all* documentation must live in the repository —
a company-wide onboarding wiki, for instance, reasonably lives
elsewhere — but documentation that describes *this specific codebase's
behavior* (docstrings, README, architecture docs, ADRs) should live
with the code, versioned identically.

## 36. Documentation in Git

A professional workflow treats a documentation update as a normal part
of shipping a change, not a separate follow-up task:

```
code change
    ↓
documentation update
    ↓
tests
    ↓
documentation review
    ↓
commit
    ↓
pull request
```

**Why documentation should be updated with the feature/change that
requires it, in the same commit or PR**: because that is the only
point at which the person with full context on *what changed and why*
is actively working on it. Deferring the documentation update to "a
follow-up PR" is, in practice, one of the most common ways documentation
drift (§34) begins — the follow-up PR frequently never happens, because
by the time it would, the context has moved on to the next task.

```bash
git add billing_service/pricing.py README.md
git commit -m "feat: add bulk-discount tier to calculate_total

Also updates README usage example and the calculate_total docstring
to reflect the new `bulk_discount` parameter."
```

Committing the code and documentation change together — as shown
above — is a small habit with an outsized effect on keeping a
repository's documentation trustworthy over its lifetime.

## 37. Documentation in Code Review

A thorough reviewer asks documentation-specific questions alongside the
usual correctness/style review, because documentation quality is part
of what a PR ships:

- **Is the public API documented?** New public functions/classes/CLI
  flags should have docstrings or README updates, not just working
  code.
- **Are examples correct?** If the PR touches a function used in a
  README or docstring example, does that example still run and produce
  the stated output?
- **Are configuration changes documented?** A new required environment
  variable with no corresponding README/`.env.example` update should
  block the PR — it will break every other developer's setup silently.
- **Are new CLI flags documented?** In `--help` text (usually free, via
  `argparse`) and in any README CLI section that duplicates it.
- **Are breaking changes documented?** Per §75 — a changed function
  signature or removed field needs a migration note, not just updated
  code.

A reviewer who approves a PR that adds a required config value with no
documentation update is, in effect, approving documentation drift on
day one — before the code has even shipped.

## 38. Changelogs

**`CHANGELOG.md`** is a file, conventionally at the repository root,
that lists user-facing changes **per release**, in reverse-chronological
order.

```markdown
# Changelog

## [1.4.0] - 2026-08-12
### Added
- Bulk-discount tier support in `calculate_total`.

### Fixed
- `charge_customer` no longer raises on zero-cent charges (was
  incorrectly rejecting valid $0 promotional charges).

### Deprecated
- `calc_total` is deprecated; use `calculate_total` instead. Will be
  removed in 2.0.0.

## [1.3.1] - 2026-07-30
### Fixed
- Fixed currency rounding error in EUR conversions.
```

**Why changelogs exist**: a user or integrator upgrading this
dependency needs to know, at a glance, what changed *for them* —
new features, fixed bugs, breaking changes, deprecations — without
reading every commit or PR that went into the release.

**README vs. changelog vs. commit message** — three different
granularities, easy to conflate:

| | Scope | Audience | Changes over time? |
|---|---|---|---|
| **README** | Current state of the project | Anyone starting fresh today | Yes — always describes *now* |
| **CHANGELOG** | History of what changed, release by release | Existing users upgrading | No — old entries are never rewritten |
| **Commit message** | One specific code change | Developers reading git history/blame | No — permanent record of that one change |

A commit message explains *one diff*; a changelog entry summarizes
*what that diff (and others like it) means for a user upgrading*; a
README describes only the *current* state, with no history at all.

## 39. Release Notes

**Release notes** cover the same underlying events as a changelog —
**new features**, **fixes**, **breaking changes**, **migration
instructions**, **deprecations** — but differ in form and purpose.

**How release notes differ from a changelog**: a changelog is a
terse, cumulative, append-only *log*, meant to be scanned or diffed
release-to-release. Release notes are a more narrative, standalone
*announcement* for a single release — often including *why* a change
was made, not just *what* changed, and commonly including explicit
**migration instructions** a changelog entry would only summarize in
one line.

```markdown
# Release Notes — v2.0.0

This release removes the deprecated `calc_total` function (announced
in v1.4.0's changelog) in favor of `calculate_total`.

## Breaking Changes

`calc_total` has been removed. Migrate as follows:

\`\`\`python
# Before (v1.x)
from billing_service import calc_total
total = calc_total(9.99, 3)

# After (v2.0+)
from billing_service import calculate_total
total = calculate_total(price=9.99, quantity=3)
\`\`\`

Note the parameters are now keyword-only and named `price`/`quantity`
rather than positional.
```

In practice, many small-to-medium projects use *only* a `CHANGELOG.md`
and skip separate release notes — release notes tend to appear for
larger, more public releases where a narrative explanation genuinely
adds value beyond the changelog's terse entries.

## 40. Deprecation Documentation

Documenting a deprecated API needs five specific pieces of information:
**what** is deprecated, **why**, the **replacement**, a **timeline** if
one is known, and a **migration example**.

```python
import warnings


def calc_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    .. deprecated:: 1.4.0
        Use :func:`calculate_total` instead — this name will be
        removed in 2.0.0. `calc_total` used positional-only
        arguments, which made call sites ambiguous
        (``calc_total(3, 9.99)`` vs. ``calc_total(9.99, 3)``);
        `calculate_total` requires keyword arguments to prevent that
        class of bug.

    Migration:
        >>> # Before
        >>> calc_total(9.99, 3)
        >>> # After
        >>> calculate_total(price=9.99, quantity=3)
    """
    warnings.warn(
        "calc_total is deprecated since 1.4.0 and will be removed in "
        "2.0.0; use calculate_total instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return calculate_total(price=price, quantity=quantity)
```

Two channels are working together here: the **docstring**, read by
anyone looking the function up in documentation or an IDE, and a
runtime **`DeprecationWarning`** (Python's built-in warning category
for exactly this purpose), which surfaces to anyone who actually
*calls* the function, even if they never open its documentation.
Neither alone is sufficient — the warning reaches active callers, the
docstring reaches anyone evaluating whether to start using it.

## 41. API Documentation

**API documentation**, at a conceptual level, applies to any interface
a separate piece of code (or person) calls into: a **Python API** (a
package's public functions/classes), an **HTTP API** (REST/GraphQL
endpoints), or a **CLI API** (a command-line program's commands and
flags, §29). Despite the different transport, consumers of any of these
need the same categories of information:

- **Inputs** — what parameters/arguments/fields are accepted, and their
  constraints.
- **Outputs** — what is returned, and its shape.
- **Errors** — what can go wrong, and how it's signaled (exception,
  HTTP status code, exit code).
- **Authentication** — how a caller proves who they are, if relevant.
- **Examples** — a worked call showing real inputs and real outputs.
- **Limits** — rate limits, size limits, pagination.
- **Compatibility** — what's guaranteed to stay stable across versions
  (§22, §75).

A Python function's docstring (§5, §22), a CLI's `--help` and README
section (§29), and an HTTP endpoint's OpenAPI/Swagger spec are all
answering this same checklist, in a format suited to their transport.

## 42. Python API Documentation

Python docstrings are not just read by humans directly — they are the
**source material** documentation generators consume to build a
browsable API reference site, without the author writing that site's
content by hand.

```
docstrings + type hints  →  documentation generator  →  HTML reference site
```

Three tools that do this, introduced here at the level this section
promises and developed individually in §43–46:

- **`pydoc`** — Python's own built-in module for inspecting and
  rendering docstrings, with zero setup (§43).
- **Sphinx** — a mature, highly configurable documentation generator,
  traditionally reStructuredText-based (§44).
- **MkDocs** — a Markdown-first documentation-site generator, popular
  for combining hand-written guides with generated API reference (§45).

(A fourth tool sometimes mentioned in this space, **`pdoc`** — distinct
from the built-in `pydoc` — is a lightweight, near-zero-configuration
API-doc generator; it's mentioned here for completeness but not
covered in depth, since Sphinx and MkDocs cover the concepts you need
at this stage.)

None of this replaces writing good docstrings in the first place
(§5–§17) — generated documentation is only as good as the docstrings
and type hints it's built from.

## 43. `pydoc`

**`pydoc`** is a module in Python's standard library — not a
third-party tool — that reads an object's `__doc__` (and its
signature) and renders a formatted summary, exactly like `help()`
does, because `help()` is itself built on `pydoc`.

```bash
python -m pydoc billing_service.calculate_total
```

```text
Help on function calculate_total in billing_service:

billing_service.calculate_total = calculate_total(price: float, quantity: int) -> float
    Calculate the total price.

    Args:
        price: Unit price.
        quantity: Number of items.

    Returns:
        The total price.
```

`pydoc` can also start a local HTTP server that renders browsable
documentation for every installed module:

```bash
python -m pydoc -b
```

**Why this matters**: `pydoc` requires no setup, no configuration file,
and no third-party dependency — it's available the instant you have a
Python interpreter, which makes it the fastest way to check what a
docstring will actually look like to a reader, and a reasonable
fallback for small projects that don't need a full Sphinx/MkDocs site.

## 44. Sphinx

**Sphinx** is a mature, widely-used, third-party Python documentation
generator — **not** part of the Python standard library — originally
built to document Python itself and still used for CPython's own
documentation today.

**What it does**: reads your **docstrings** (via its `autodoc`
extension) and hand-written `.rst` (reStructuredText) files, resolves
**cross-references** between them (a `:func:`calculate_total`` link
that becomes a real hyperlink in the output), and produces
**generated documentation** as a full HTML site (or PDF, or other
formats).

```rst
.. automodule:: billing_service
   :members:
```

This one directive in a `.rst` file tells Sphinx to pull in every
public member of the `billing_service` module, along with its
docstrings, and render a full reference page — the docstrings you
already wrote in §5–§18 become the content, with no duplication.

**Why mature Python projects often use it**: it's powerful and highly
configurable (custom themes, versioned docs, PDF output, deep
cross-referencing), it's the tool most Sphinx-style docstrings (§10)
are written for, and it has decades of ecosystem support — it is,
however, also the tool with the steepest configuration learning curve
of the three covered here.

## 45. MkDocs

**MkDocs** is a third-party static-site generator built specifically
around **Markdown** — you write `.md` files, configure a simple
`mkdocs.yml` for **navigation**, and MkDocs builds a searchable
**documentation site** with a chosen **theme** (Material for MkDocs
being the most popular).

```yaml
# mkdocs.yml
site_name: Billing Service Docs
nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - API Reference: api.md
theme:
  name: material
```

For API reference generated from docstrings specifically, MkDocs is
typically paired with a plugin (such as `mkdocstrings`) that reads
your docstrings the same way Sphinx's `autodoc` does, and renders them
as part of the MkDocs site.

**When Markdown-first documentation is attractive**: when your
project's documentation is primarily hand-written **guides** (a
"Getting Started," a set of how-to pages) with a smaller amount of
generated API reference, and your team is already comfortable writing
Markdown (as opposed to learning reStructuredText for Sphinx). It has a
noticeably gentler learning curve than Sphinx for straightforward
documentation sites.

## 46. `pydoc` vs Sphinx vs MkDocs

| | `pydoc` | Sphinx | MkDocs |
|---|---|---|---|
| **Purpose** | Inspect docstrings ad hoc, zero setup | Full-featured documentation-site generator | Markdown-first documentation-site generator |
| **Source format** | Reads docstrings directly, no separate files | reStructuredText (`.rst`), plus docstrings via `autodoc` | Markdown (`.md`), plus docstrings via a plugin (e.g. `mkdocstrings`) |
| **API documentation** | Yes — its core purpose | Yes — via `autodoc` | Yes — via a plugin |
| **User guides / tutorials** | No — not its purpose | Yes — hand-written `.rst` pages | Yes — hand-written `.md` pages, its core strength |
| **Customization** | Minimal | Extensive (themes, extensions, custom builders) | Moderate (themes, plugins) |
| **Learning curve** | Essentially none | Steep | Gentle |
| **Typical usage** | Quick local lookup, small projects | Large/mature libraries, projects already using `.rst` | Guide-heavy documentation sites, teams preferring Markdown |

None of these three is universally best — `pydoc` answers "what does
this function's docstring say, right now, with zero setup"; Sphinx and
MkDocs both answer "build me a full documentation website," differing
mainly in source format and configuration depth. The right choice
depends on your project's scale and your team's existing comfort with
Markdown vs. reStructuredText.

## 47. Automatic API Documentation

The concept unifying §42–46, stated as a pipeline:

```
source code
    ↓
docstrings / type hints
    ↓
documentation generator (Sphinx / MkDocs / pydoc)
    ↓
documentation site
```

**Benefits**: the generated reference **cannot drift from the function
signature** (§34), because it's built directly from that signature at
generation time — rename a parameter in code, and the next generated
build reflects the rename automatically, with no separate file to
remember to update. It also guarantees *completeness* in a mechanical
sense: every public function that has a docstring appears in the
generated reference, with no risk of a human simply forgetting to add
one to a hand-maintained page.

**Limitations**: a documentation generator can only render what's
*in* your docstrings — it cannot invent an explanation you never
wrote, cannot generate a "Getting Started" narrative, cannot explain
*why* an architectural decision was made, and cannot substitute for a
worked, realistic example if your docstring only has a one-line
summary. Generated API reference is necessary but not sufficient — see
§48.

## 48. Documentation Generation

Generated documentation (API reference, §47) and hand-written
documentation (guides, tutorials, architecture explanations) serve
different, complementary roles within the same documentation site:

- **Generated API reference** — the exhaustive, mechanically accurate
  "what exists and what's its signature" layer.
- **Hand-written guides** — the "how do I actually accomplish X"
  narrative layer a generator cannot produce on its own.
- **Examples** — often hand-written even when embedded inside a
  docstring that gets pulled into generated output (§31, §50).
- **Navigation** — how a reader moves between guides and reference,
  configured by the documentation-site tool (Sphinx's `toctree`,
  MkDocs's `nav`, §53).

**Why generated API docs should complement, not replace, human-written
explanation**: a generated reference page for `calculate_total`
faithfully shows its signature and docstring — but a reader who has
never used the package at all needs a "Getting Started" guide to even
know that `calculate_total` is the function they should be looking at
in the first place. Projects that ship *only* generated reference, with
no hand-written guide layer, are notoriously hard to get started with,
even when every individual function is perfectly documented.

## 49. Documentation Testing

**How documentation can be tested**, concretely — turning the "silent
failure" problem from §33 into something CI catches:

- **Code examples** — run as part of the test suite (via `doctest`,
  §50, or a dedicated "examples" test file).
- **CLI commands** — a documented command literally executed in CI,
  asserting it exits successfully and/or matches expected output.
- **Links** — a link checker that fetches every internal/external link
  in the documentation and flags 404s (§52).
- **Imports** — a check that every `import` statement shown in a
  documentation example actually resolves against the current
  codebase (catches a renamed/removed function, §34).
- **Doctests** — Python's built-in mechanism for embedding *and
  running* examples directly inside a docstring — covered in full in
  §50.

None of these need to cover *every* piece of documentation to be
worthwhile — even testing the handful of examples in a README's
"Usage" section catches the single most damaging kind of drift: a
reader's very first command failing.

## 50. `doctest`

**`doctest`** is a module in Python's standard library that scans
docstrings for text formatted like an interactive interpreter session
(`>>>` prompts followed by expected output) and **executes** each one,
comparing the actual output to what's written.

```python
def add(a: int, b: int) -> int:
    """Add two numbers.

    >>> add(2, 3)
    5
    """
    return a + b
```

- **Prompt**: `>>>` marks a line as code to execute, exactly as it
  would appear typed at a live interpreter.
- **Expected output**: the line(s) immediately following the `>>>`
  line(s), with no prompt, are the output `doctest` expects that code
  to produce.
- **Execution**: running `python -m doctest yourmodule.py -v` (or
  integrating doctests into a `pytest` run) actually executes
  `add(2, 3)` and fails loudly if the real result isn't exactly `5`.

```bash
python -m doctest billing_service/pricing.py -v
```

**Benefits**: an example that's wrong (stale, typo'd, or simply never
correct in the first place) fails a test run immediately — this is the
single most direct fix to documentation drift (§34) available for
docstring examples specifically, since the example *cannot* silently
rot without a test failing to flag it.

**Limitations**: doctests are best suited to short, deterministic,
pure-function examples — an example involving network calls, random
data, timestamps, or complex setup is awkward or impossible to express
as a doctest, and forcing it usually produces a brittle, hard-to-read
test rather than useful documentation. Use doctests where they fit
naturally; use a regular test file (or just a non-executed illustrative
example) where they don't.

## 51. Executable Documentation Examples

**Why executable examples reduce documentation drift**: as established
in §34 and §50, an example that is actually run by CI cannot silently
go stale the way a plain prose example can — a code change that breaks
the example breaks the build, forcing someone to either fix the code's
compatibility or update the example, in either case keeping the two in
sync by construction rather than by discipline alone.

**Trade-offs**, honestly stated, since this is not a free win:

- **Maintenance** — an executable example is still code: it needs to
  keep compiling and passing as the codebase evolves, which is real,
  ongoing work, just work that's now *visible* (as a CI failure)
  instead of invisible (as silent drift).
- **Readability** — a doctest's strict output-matching format
  (exact whitespace, exact repr formatting) can make an example harder
  to read than equivalent prose-plus-code that isn't required to match
  output character-for-character.
- **Execution time** — examples that hit a real database, network
  service, or slow computation add real time to every CI run that
  executes them; this often argues for *mocking* such dependencies in
  doctests, or excluding slow examples from the executed set.
- **Complexity** — not every concept a docstring needs to illustrate
  reduces cleanly to a short, deterministic, executable snippet (a
  concurrency subtlety, a distributed-system behavior); forcing these
  into doctest form often produces a worse explanation than plain
  prose would.

The practical takeaway: use executable examples where they fit
naturally (pure functions, deterministic logic) and accept plain,
non-executed illustrative examples elsewhere — don't chase 100%
"testable documentation" as a goal in itself (this connects to §69's
caution against chasing 100% documentation *coverage* as a metric).

## 52. Documentation Links

Documentation commonly links to three kinds of destinations:

- **Internal links** — to another page/section within the same
  documentation (e.g. a README linking to `CONTRIBUTING.md`, or a
  docstring's `See Also:` note pointing to a related function).
- **External links** — to something outside the project (a library's
  own documentation, a spec, an RFC).
- **Anchors** — a link to a specific heading within a page (e.g.
  `README.md#configuration`), generated automatically by most Markdown
  renderers from heading text.
- **Relative links** — a link expressed relative to the current file's
  location (`./06-type-hints-and-type-checking.md`), rather than an
  absolute URL — the correct choice for links *within* a repository, so
  they keep working regardless of where the repository is hosted or
  cloned.

**Link rot** is the phenomenon of a link that worked when written
gradually becoming broken — a page moved, a heading renamed (breaking
its anchor), an external site restructured or taken down. **Why
documentation links should be periodically checked**: an unchecked
broken link degrades silently, exactly like the documentation-drift
failure mode in §33–34 — nothing alerts anyone until a reader actually
clicks it and hits a dead end. A link checker, run periodically or in
CI (§49), converts this into a build failure instead of a silent,
slowly-accumulating rot.

## 53. Documentation Navigation

**Documentation information architecture** is the practice of
organizing a documentation *set* — not any single page — so a reader
can find the right page for their current need. A widely-used
conceptual framework for this is **Diátaxis**, which sorts
documentation into four purposes:

- **Getting started** — the fastest path from zero to a working setup
  (closely related to a README's installation/usage sections, §25).
- **Tutorials** — learning-oriented, step-by-step walkthroughs for a
  newcomer, prioritizing a successful first experience over
  completeness.
- **How-to guides** — task-oriented instructions for a specific,
  already-understood goal ("how do I configure X for Y").
- **Reference** — comprehensive, structured lookup material (generated
  API docs, §47, are almost always reference material).
- **Explanation** — understanding-oriented discussion of *why*
  (architecture docs, ADRs, §58–59).

You do not need to memorize Diátaxis's exact terminology — the useful
takeaway is simply that **these are different jobs**, and a single page
trying to do all four at once (a "Getting Started" tutorial that also
tries to be exhaustive reference material) typically serves every
reader worse than four focused pages would.

## 54. Tutorial vs How-to vs Reference vs Explanation

The same four categories from §53, made concrete for a Python project:

| Type | Question it answers | Example for a Python billing package |
|---|---|---|
| **Tutorial** | "Teach me, step by step, from nothing." | "Your First Invoice: a 10-minute walkthrough from `uv sync` to a printed receipt." |
| **How-to guide** | "I know roughly what I want — show me how." | "How to add a custom discount rule." |
| **Reference** | "What exactly does this function/parameter/flag do?" | The generated API reference for `calculate_total` (§47). |
| **Explanation** | "Why is it built this way?" | "Why charges are idempotency-keyed" (an ADR, §59). |

A tutorial and a how-to guide can look superficially similar (both are
step-by-step), but they differ in *intent*: a tutorial optimizes for a
beginner's successful *first* experience, even if that means glossing
over edge cases; a how-to guide assumes the reader already understands
the basics and wants the complete, correct procedure for one specific
task, edge cases included.

## 55. User Documentation vs Developer Documentation

These two categories answer fundamentally different questions and are
worth separating explicitly, even when they end up in the same README:

**User documentation** — for someone who wants to *use* the software
as-is:

- Installation
- Usage
- CLI commands
- Troubleshooting

**Developer documentation** — for someone who wants to *change or
extend* the software:

- Architecture (§58)
- Module structure
- Testing (how to run and write tests)
- Contribution guidelines (§56)
- Design decisions (§59)

A user of a CLI tool needs to know how to invoke it; they have no need
to know how its internal modules are structured. A contributor needs
both — the user-level documentation to understand what the tool *does*,
plus developer documentation to understand how to safely change it.
Mixing these into one undifferentiated README section makes both
audiences scroll past information irrelevant to them; a common,
effective structure is a lean top-level README (mostly user
documentation, with a link to `CONTRIBUTING.md`) and a separate
developer-documentation section or file for the rest.

## 56. `CONTRIBUTING.md`

**`CONTRIBUTING.md`** is the conventional file explaining how someone
becomes a contributor — the developer-documentation counterpart to a
user-facing README. It typically contains:

- **Setup** — dev-specific environment setup, often more involved than
  a user's install (e.g. pre-commit hooks, dev-only dependencies).
- **Coding standards** — style conventions the project expects.
- **Testing** — how to run tests, and any coverage expectations.
- **Linting** — the exact command to run (connecting to
  [`05-ruff-formatting-and-linting.md`](./05-ruff-formatting-and-linting.md)).
- **Formatting** — likewise, how formatting is enforced.
- **Branch workflow** — expected branch naming, whether to rebase or
  merge, etc.
- **Pull requests** — what a PR description should contain, review
  expectations.
- **Commit expectations** — message format, whether commits should be
  squashed.

```markdown
## Development Setup

\`\`\`bash
uv sync --group dev
\`\`\`

## Before Submitting a PR

\`\`\`bash
uv run ruff format .
uv run ruff check .
uv run mypy .
uv run pytest
\`\`\`

All four commands must pass. See [Ruff](./05-ruff-formatting-and-linting.md)
and [Type Checking](./06-type-hints-and-type-checking.md) for what
each check enforces.
```

Connecting explicitly to Ruff, type checking, and `pytest` — as shown
above — turns `CONTRIBUTING.md` into the single place a new contributor
learns the exact, current quality gates their change must pass, rather
than discovering them one CI failure at a time.

## 57. Development Documentation

Distinct from `CONTRIBUTING.md`'s contribution-process focus,
**development documentation** covers the practical mechanics of
working on the codebase day to day:

- **Local development** — how to run the project locally, hot-reload,
  and iterate.
- **Environment setup** — dev-only configuration beyond what a user
  needs (test database credentials, mock service endpoints).
- **Test commands** — how to run the full suite, a single test file,
  or tests matching a keyword.
- **Lint commands** — the exact Ruff invocation(s).
- **Type checking** — the exact type-checker invocation.
- **Build commands** — for projects that have a build step (packaging,
  bundling).
- **Debugging** — how to attach a debugger, enable verbose logging, or
  reproduce a failure locally.
- **Common failures** — the developer-facing equivalent of §30's
  user-facing error documentation ("`ModuleNotFoundError` after
  pulling latest — you likely need to re-run `uv sync`").

```markdown
## Running a Single Test

\`\`\`bash
uv run pytest tests/test_pricing.py::test_bulk_discount -v
\`\`\`

## Common Issue: ModuleNotFoundError after pulling

A new dependency was likely added. Re-sync your environment:

\`\`\`bash
uv sync
\`\`\`
```

## 58. Architecture Documentation

**Why production systems need architecture documentation**: as a
system grows past a handful of files, "read all the code" stops being
a viable way to understand how it's structured — a new engineer (or the
original author, months later) needs a document that answers "what are
the pieces, and how do they fit together" *before* diving into any
single file.

Architecture documentation typically covers:

- **System overview** — a one-paragraph summary of what the system
  does end to end.
- **Components** — the major pieces (services, modules, databases) and
  each one's responsibility.
- **Data flow** — how a request or a unit of data moves through the
  system.
- **Dependencies** — what each component depends on, internally and
  externally.
- **External services** — third-party APIs, databases, message queues.
- **Failure points** — where the system is most likely to fail, and
  what happens when it does.
- **Deployment** — how and where the system actually runs.

A simple architecture diagram, expressed in Markdown text (no diagram
tool required for something this size):

```text
Client
  │
  ▼
API Gateway  ──────►  Auth Service
  │
  ▼
Billing Service  ──────►  PostgreSQL (billing DB)
  │
  ▼
Payment Gateway (external, third-party)
```

Even this simple a diagram, paired with one sentence per arrow ("API
Gateway calls Auth Service synchronously to validate the request
token before forwarding to Billing Service"), gives a new reader a
mental map that would otherwise take hours of code-reading to build.

## 59. Architecture Decision Records

An **Architecture Decision Record (ADR)** is a short, standalone
document capturing **one** significant architectural decision, written
at the time it's made, and never rewritten afterward (a later decision
that supersedes it gets its *own* new ADR, referencing the old one).

Typical structure:

```markdown
# ADR 0007: Use idempotency keys for payment charges

## Context

`charge_customer` is called from a client that may retry on network
timeout. Without deduplication, a retried request after a timeout can
create a duplicate charge if the original request actually succeeded
on the gateway's side but the response was lost.

## Decision

Require callers to pass a client-generated idempotency key. The
payment gateway deduplicates charges by this key for 24 hours,
guaranteeing a retried request with the same key never double-charges.

## Alternatives Considered

- **Server-generated idempotency keys**: rejected — doesn't help,
  since the client can't attach the key to a retry it doesn't yet
  have (the key would only exist after the first successful call).
- **Optimistic duplicate detection** (compare amount + customer +
  timestamp window): rejected — too fragile; two legitimately
  identical charges within the window would be incorrectly merged.

## Consequences

- Every caller of `charge_customer` must now generate and pass a
  unique key per logical charge attempt (see updated docstring, §5).
- The payment gateway's 24-hour deduplication window means a retry
  after 24+ hours is treated as a new charge — this is documented in
  `charge_customer`'s docstring as a known limitation.
```

**Why ADRs are useful**: an ADR captures the *reasoning*, including
rejected alternatives, at the moment the decision was fresh — exactly
the information that's lost forever if a future engineer only has the
resulting code and has to guess *why* it was built this way, or worse,
"fixes" it by reverting to an alternative that was already tried and
rejected for a documented reason.

## 60. Documentation for Data Pipelines

A realistic data-engineering example, documenting the pieces that
matter most for a pipeline specifically:

```markdown
## Pipeline: `daily_transaction_load`

**Input:** Raw CSV files landing in `s3://raw-bucket/transactions/{date}/`,
one file per source system, matching schema `transactions_v2.avsc`.

**Transformation:** Deduplicates by `(transaction_id, source_system)`,
converts all amounts to cents (integer), and normalizes timestamps to
UTC.

**Output:** Parquet files in `s3://processed-bucket/transactions/{date}/`,
partitioned by `date`, matching schema `transactions_processed_v1.avsc`.

**Schema:** See `schemas/transactions_processed_v1.avsc` for the
authoritative, machine-checked schema — this document summarizes it,
but the schema file is the source of truth.

**Failure handling:** A malformed row is written to a `_rejects/`
sidecar path rather than failing the whole batch. The pipeline fails
only if rejected rows exceed 1% of the batch.

**Retries:** The pipeline is idempotent per `date` partition — safe to
re-run for a given date; it overwrites that partition's output
entirely rather than appending.

**Dependencies:** Requires the `source_system` upstream export to have
completed (checked via its `_SUCCESS` marker file) before running.
```

Every field here maps to a real operational question a data engineer
debugging a failed run needs answered fast: what came in, what
happened to it, what came out, how failures are handled, whether a
re-run is safe, and what upstream dependency might be the actual root
cause.

## 61. Documentation for ML Systems

Documentation for an ML system needs to cover the model as a black box
with a contract, not just the surrounding code:

```markdown
## Model: `churn_predictor_v3`

**Model inputs:** A feature vector of 42 features, defined in
`features/churn_v3_schema.json`. All features must be pre-scaled
using `StandardScaler` fitted on the v3 training set (see
`artifacts/churn_v3_scaler.pkl`) — passing unscaled features silently
produces plausible-looking but wrong predictions.

**Model outputs:** A float in `[0, 1]`, the predicted probability of
churn within 30 days. NOT a binary classification — callers apply
their own threshold (production currently uses 0.7).

**Preprocessing:** See `pipelines/churn_preprocessing.py`; must be
applied identically at inference time as at training time.

**Feature expectations:** `days_since_last_login` assumes UTC
timestamps; a naive (timezone-unaware) datetime is treated as UTC,
which has caused incorrect predictions when fed local-time data in
the past.

**Model version:** v3, trained 2026-06-01 on data through 2026-05-31.
See `MODEL_CARD.md` for training data details and known limitations.

**Dependencies:** scikit-learn==1.5.2 (exact version — the pickled
model is not guaranteed compatible with other versions).

**Evaluation:** AUC 0.87, precision@0.7-threshold 0.81 on the 2026-05
holdout set. See `evaluation/churn_v3_report.ipynb` for full metrics.

**Deployment:** Served via the `ml-inference` service; see its
runbook (§78) for rollback procedure if a bad model version ships.
```

The exact-version pin on `scikit-learn` and the scaling requirement are
the kind of ML-specific "silent wrongness" traps (§1's "understandable
from code but still has important behavioral assumptions" pattern,
applied to models): nothing crashes if you feed unscaled features or
use a slightly different library version — the model just produces
confidently wrong predictions, which is exactly why this needs to be
documented explicitly rather than left to be discovered.

## 62. Documentation for AI Systems

AI systems — those built around a call to an LLM or other external
model provider — need documentation covering pieces that don't exist
in ordinary deterministic code:

- **Model providers** — which provider/model is being called, and any
  fallback provider.
- **Prompts** — the actual prompt templates used, and what variables
  they're populated with.
- **Tools** — what tools/functions the model can invoke (developed
  fully for agentic systems in §63).
- **Configuration** — temperature, max tokens, and other
  generation parameters that affect output.
- **Agent workflow** — the sequence of steps a request goes through.
- **State** — what's remembered across turns/calls, and for how long.
- **Retries** — how transient provider failures are retried.
- **Fallbacks** — what happens if the primary provider/model is
  unavailable.
- **Observability** — what's logged/traced for debugging a bad
  response after the fact.
- **Limitations** — known failure modes (hallucination risk, prompt
  injection surface, context-length limits).

**Why AI systems often need *more* documentation than deterministic
code**: a traditional function's behavior is fully determined by its
code — read the code, and you know exactly what it will do for any
input. An LLM call's behavior additionally depends on a **model
provider's changing weights** (a provider can update a model version
under a fixed name), **non-determinism** (the same prompt can produce
different outputs), and a **prompt template's exact wording** (subtle
rewording can change behavior in ways no diff of the surrounding
Python code would show). None of that is visible from reading the
calling code the way a normal function's logic is — which is exactly
why explicit documentation of the prompt, the model/version, and the
known failure modes matters more here than for equivalent deterministic
code.

## 63. Documentation for Agentic AI Systems

A realistic agentic pipeline, as a flow:

```text
User
  │
  ▼
Agent
  │
  ▼
Planner
  │
  ▼
Tool Selection
  │
  ▼
Tool Execution
  │
  ▼
Result
  │
  ▼
Final Response
```

For each stage, documentation should cover:

```markdown
## Agent: `support_ticket_agent`

**Tools available:**

| Tool | Purpose | Permissions |
|---|---|---|
| `search_knowledge_base` | Read-only search over help articles | None required |
| `create_refund` | Issues a refund up to $50 | Requires `agent:refund` scope; amounts over $50 are rejected, not escalated silently |
| `escalate_to_human` | Hands off the conversation | None required |

**Inputs:** User message + conversation history (last 10 turns).

**Outputs:** A response string, plus a structured `action_taken` field
logged for every tool call made.

**Failure behavior:** If a tool call raises, the agent calls
`escalate_to_human` rather than retrying silently or fabricating a
result — this is a hard rule enforced in code, not just a prompt
instruction.

**Retry behavior:** Provider timeouts are retried up to 2 times with
exponential backoff; a third failure escalates to a human.

**Model configuration:** `gpt-...`-class model, temperature 0.2 (kept
low deliberately — this agent takes real actions, e.g. `create_refund`,
so we favor consistency over creative variation).

**Safety boundaries:** `create_refund` is hard-capped at $50 in code
(not just prompted) — the model cannot be prompted into exceeding
this limit, since the cap is enforced by the tool implementation, not
by instructing the model to "please stay under $50."

**Observability:** Every tool call, its arguments, and its result are
logged with a `conversation_id` for replay/debugging.
```

**Why this level of detail matters specifically for agentic systems**:
an agent that can *take actions* (issue a refund, send an email) turns
a documentation gap into an operational risk, not just a confusion —
"what happens on tool failure" and "what are the hard safety
boundaries" are questions that, left undocumented, are also left
*unverified*, which is a materially different risk than an undocumented
pure function.

## 64. Configuration Documentation

For every configuration value, document, where applicable: **name**,
**purpose**, **required/optional**, **type**, **default**, an
**example**, and its **security sensitivity**.

```text
API_TIMEOUT_SECONDS=30
```

- **Name:** `API_TIMEOUT_SECONDS`
- **Purpose:** Maximum time to wait for the payment gateway to respond
  before raising `GatewayTimeoutError`.
- **Required/optional:** Optional.
- **Type:** Integer, seconds.
- **Default:** `30`.
- **Example:** `API_TIMEOUT_SECONDS=15` for a stricter timeout in a
  latency-sensitive deployment.
- **Security sensitivity:** Not sensitive — safe to log or display.

Compare to a genuinely sensitive value:

- **Name:** `API_KEY`
- **Security sensitivity:** **Secret.** Never log, never display in
  error messages, never commit a real value (§76).

Documenting *type* and *default* explicitly (not just "an integer,
probably") lets a reader configure the value correctly the first time,
without needing to read the source to find where the default is
actually applied.

## 65. Environment Variable Documentation

A table is the standard, scannable format for a full set of
environment variables:

| Variable | Required | Type | Default | Description |
|----------|----------|------|---------|-------------|
| `DATABASE_URL` | Yes | string | — | PostgreSQL connection string. |
| `API_KEY` | Yes | string (secret) | — | Payment gateway API key. Never commit a real value. |
| `API_TIMEOUT_SECONDS` | No | int | `30` | Gateway request timeout, in seconds. |
| `LOG_LEVEL` | No | string | `INFO` | One of `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
| `FEATURE_FLAG_TAX_V2` | No | bool | `false` | Enables the new tax calculation engine. |

**Why this format is useful**: every column answers exactly one
question a reader has when configuring the system — "do I have to set
this," "what kind of value goes here," "what happens if I don't set
it," "what does it actually do" — scannable in one pass, without
prose. As stated in §27 and repeated here deliberately: **never
include actual credentials** in this table or anywhere in
documentation, even as a "just for this example" placeholder that
looks close to a real value.

## 66. Documentation for Dependencies

Documentation should communicate, in prose, what the project depends
on — while delegating the *authoritative, exact* version information
to machine-readable files, per the pattern already established in
§26:

- **Python version** — stated in prose (README prerequisites) and
  enforced by `requires-python` in `pyproject.toml`.
- **Required packages** — declared in `pyproject.toml`, pinned in
  `uv.lock` (per
  [`03-pyproject-lock-files-and-uv.md`](./03-pyproject-lock-files-and-uv.md)
  and
  [`04-dependency-management-and-semantic-versioning.md`](./04-dependency-management-and-semantic-versioning.md)).
- **System dependencies** — anything not installable via `uv`/`pip`
  (a system-level PostgreSQL client library, `ffmpeg`, etc.) — these
  *must* be documented in prose, since no Python dependency file
  captures them.
- **External services** — a database, a message queue, a third-party
  API — documented in prose (often in the README's Prerequisites or
  Architecture section) since they're not "dependencies" in the
  packaging sense at all.

**Why dependency files provide machine-readable information while
README provides human-readable setup guidance**: `pyproject.toml` and
`uv.lock` are the *source of truth* a tool (`uv sync`) reads
mechanically — they're precise but not narrative. The README is where
a human learns *that* a PostgreSQL instance needs to exist and roughly
how to get one running locally — information no dependency file
expresses at all, since "you need a running database" isn't a Python
package dependency.

## 67. Documentation and Code Quality

Documentation connects to the quality tools covered earlier in this
module — Ruff
([`05-ruff-formatting-and-linting.md`](./05-ruff-formatting-and-linting.md)),
type checking
([`06-type-hints-and-type-checking.md`](./06-type-hints-and-type-checking.md)),
and testing — in a few concrete ways:

- **Docstring style enforcement** — Ruff includes lint rules (in its
  `pydocstyle`-derived `D` rule set) that can check things like
  "every public function has a docstring" or "the docstring's first
  line ends with a period," when those rules are explicitly enabled in
  a project's Ruff configuration.
- **Documentation linting** — checking Markdown files themselves for
  structural issues (§68).
- **Broken links** — caught by a link checker, not Ruff (§52).
- **Examples** — kept honest by doctest/executable examples (§49–51),
  not by Ruff.
- **API consistency** — a type checker (mypy/Pyright) catches a
  docstring's implicit type claims being *contradicted* by the actual
  signature only indirectly, by catching real type errors at call
  sites — it does not read docstring prose at all.

**Being precise about what's real here**: Ruff's `D`-rule docstring
checks verify *presence and basic formatting* of docstrings (is one
present, does it start with a capital letter, etc.) — they do not, and
cannot, verify that a docstring's *content* is accurate. A docstring
that confidently describes the wrong behavior passes every Ruff check
just as cleanly as a correct one. Do not treat "Ruff's docstring rules
pass" as equivalent to "the documentation is correct" — it only
confirms the documentation *exists and is formatted consistently*.

## 68. Documentation Linting

**Documentation linting**, distinct from code linting, checks the
Markdown/documentation files themselves for structural problems:

- **Malformed Markdown** — a broken table, an unclosed code fence, a
  heading missing its `#`.
- **Broken links** — covered in §52; often checked by a dedicated link
  checker rather than a general Markdown linter.
- **Missing headings** — a document that's supposed to follow a
  template (e.g. every ADR needs a `## Decision` section) but is
  missing one.
- **Invalid references** — a Markdown link like `[see here](#usage)`
  whose target heading doesn't actually exist in the document.
- **Inconsistent formatting** — mixed heading styles, inconsistent
  code-fence languages, inconsistent list markers.

Appropriate tooling exists for this (general-purpose Markdown linters,
and link checkers run as a separate CI step) — this chapter does not
walk through configuring a specific one, since the *concept* (treat
documentation source files as lintable, just like code) is the
transferable idea, and the exact tool is a project-level choice similar
to picking a docstring style in §11.

## 69. Documentation Coverage

**Documentation coverage** is a measurable statistic: the proportion of
public APIs, modules, classes, or functions that have a docstring
present.

For example, a coverage tool might report "87% of public functions in
this package have a docstring" by mechanically checking `__doc__ is
not None` across every public symbol.

**Why 100% documentation coverage is not automatically a meaningful
quality metric**: coverage measures *presence*, not *correctness* or
*usefulness* — exactly the same limitation Ruff's docstring rules have
(§67). A trivially satisfied docstring like

```python
def get_id(self) -> int:
    """Get id."""
    return self._id
```

counts as "covered" by any coverage tool, while contributing almost no
real information over the function's name and return type — and this
kind of function might reasonably need *no* docstring at all, per the
"document what is useful and non-obvious" principle from §6. Chasing
100% coverage as a target can actively produce *worse* documentation,
by incentivizing exactly this kind of empty, box-checking docstring
across every trivial method. Coverage is a useful *signal* (a package
at 10% coverage almost certainly has real gaps) but not a *quality*
metric on its own.

## 70. What Should Be Documented?

A decision framework, restating and consolidating the "document what
is useful and non-obvious" principle (§6) as a concrete checklist.
Document, especially:

- **Public APIs** — anything another piece of code or another person is
  expected to call/depend on (§21–22).
- **Non-obvious behavior** — anything a reader could not correctly
  infer just from the name, signature, and a quick read of the body.
- **Important assumptions** — what the function/class assumes about its
  inputs, its caller, or its environment.
- **Side effects** — anything beyond "compute and return a value."
- **Errors** — what can go wrong and how it's signaled.
- **Configuration** — every value a deployer needs to set correctly.
- **Operational procedures** — how to run, deploy, and recover the
  system (§77–79).
- **Architecture decisions** — why the system is shaped the way it is
  (§58–59).
- **User workflows** — how a real user accomplishes a real task end to
  end (§28, §54).

## 71. What Should Not Be Documented?

The complementary list — documentation that adds maintenance cost
without adding real information:

```python
# Redundant comment — restates the next line exactly
# Increment the counter by one
counter += 1

# Obvious code needing no explanation at all
def get_name(self) -> str:
    """Get the name."""  # adds nothing over the function's own name
    return self._name

# Documenting an implementation detail likely to change soon
def process(self):
    """Uses a for loop internally to iterate over items."""
    # Whether it's a for-loop, a comprehension, or vectorized code is
    # an implementation detail with no bearing on the public contract
    # — and will make this docstring wrong the next time someone
    # refactors the loop into something else.

# Duplicating type information the hint already states (§14)
def set_age(self, age: int) -> None:
    """Args:
        age (int): An integer for the age.
    """
```

**Why documentation has a maintenance cost**: every sentence written is
a sentence that must be kept accurate as the code evolves (§34, §73).
Documenting something trivial, obvious, or purely internal doesn't just
waste the writer's time once — it creates an ongoing obligation (and an
ongoing opportunity to silently go stale) for zero corresponding
benefit to any reader.

## 72. Documentation Debt

**Documentation debt** is the accumulated backlog of documentation
problems a project carries — the documentation-specific analogue of
technical debt. It manifests as:

- **Stale documentation** — accurate when written, now describing
  behavior that has since changed (the accumulated result of
  unaddressed documentation drift, §34).
- **Missing documentation** — public APIs, configuration values, or
  procedures that were never documented in the first place.
- **Contradictory documentation** — two documents (or a docstring and a
  README) that disagree with each other about the same behavior,
  leaving a reader unable to tell which one to trust.

**Impact on engineering teams**: every one of these costs real time,
repeatedly — a new engineer who hits stale setup instructions loses an
afternoon and then asks a teammate (costing the teammate's time too);
an on-call engineer with a contradictory runbook during an incident
loses time that, during an outage, is directly costly. Unlike
untested code (whose risk is somewhat contained until that code path
actually runs), documentation debt's cost is paid by *every reader* who
encounters the stale or missing page, compounding over the life of the
project.

## 73. Maintaining Documentation

A maintenance strategy, as concrete practices rather than aspiration:

- **Update with code changes** — the §36 workflow: documentation
  changes land in the same commit/PR as the code change that requires
  them.
- **Review during PRs** — the §37 checklist, applied on every review,
  not just "big" ones.
- **Automate checks** — link checking, doctest execution, and
  documented-command execution in CI (§49).
- **Periodically audit** — a scheduled (e.g. quarterly) pass reading
  through the README and key docs end to end, as if new, looking for
  anything that's drifted.
- **Remove obsolete content** — deleting a stale section is often
  better than leaving it wrong; an absent answer prompts a reader to
  ask, a wrong answer actively misleads them.
- **Preserve useful historical decisions** — obsolete *current-state*
  documentation should be deleted, but the *reasoning* behind a past
  decision (an ADR, §59) should be kept, precisely because ADRs are
  never rewritten — they're a historical record, not current-state
  documentation.

## 74. Versioned Documentation

**Why documentation may need versions**: when a project ships multiple
supported versions simultaneously (a library with a v1 still in use by
some consumers and a v2 with a different API), a single, unversioned
documentation set cannot correctly describe both at once — a v1 user
following "current" docs that actually describe v2 will hit errors
immediately.

Common patterns:

- **`v1` / `v2`** — separate documentation trees or site versions, one
  per major version, each internally consistent.
- **`current` / `legacy`** — a simpler two-way split, when only the
  latest and one prior version are actively supported.

**Discussion — API/library versioning**: this connects directly to
semantic versioning
([`04-dependency-management-and-semantic-versioning.md`](./04-dependency-management-and-semantic-versioning.md)):
a **major** version bump is exactly the signal that documentation
likely needs its own new version too, since a major bump is, by
definition, where breaking changes (§75) are allowed to occur. A
project that never makes breaking changes (or ships only one supported
version at a time) may reasonably need no documentation versioning at
all — this is a scale-dependent practice, not a universal requirement.

## 75. Breaking Changes

A breaking change needs documentation covering five specific things:
**what** changed, **who** is affected, **migration steps**, the **old
behavior**, and the **new behavior** — with a concrete example, as
shown fully in §39's release-notes example. Restated as its own
checklist, since this is one of the highest-stakes categories of
documentation (getting it wrong directly breaks other people's code):

```markdown
## Breaking Change: `calculate_total` now requires keyword arguments

**What changed:** `calculate_total(price, quantity)` no longer accepts
positional arguments; both must now be passed as keywords.

**Who is affected:** Any caller using positional arguments, e.g.
`calculate_total(9.99, 3)`.

**Old behavior:**
\`\`\`python
calculate_total(9.99, 3)  # worked
\`\`\`

**New behavior:**
\`\`\`python
calculate_total(9.99, 3)  # TypeError: takes 0 positional arguments
calculate_total(price=9.99, quantity=3)  # required now
\`\`\`

**Migration:** Update all call sites to use keyword arguments. A
regex-based find (`calculate_total\([\d.]+,\s*\d+\)`) can help locate
positional call sites across a codebase.
```

Every one of these five pieces answers a question an affected caller
will have, in the order they'll have it: did this affect me, what
exactly broke, and precisely how do I fix it.

## 76. Documentation Security

**What should never appear in documentation**: real passwords, real
API keys, private credentials of any kind, or sensitive production
information (internal hostnames that reveal infrastructure, real
customer data used "just as an example").

**Why this matters even for private repositories**: documentation
persists in git history indefinitely — a secret committed and then
"removed" in a later commit is still recoverable from history unless
that history is explicitly rewritten (a destructive, disruptive
operation) and the credential is rotated regardless. Treat any secret
that ever touched a commit as compromised and rotate it, rather than
relying on deletion.

**Safe documentation patterns**:

```bash
# Placeholder — obviously not a real value
API_KEY=sk-your-api-key-here

# .env.example — real filename pattern, template values only
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

```text
# Redacted example output — shows the shape without a real value
$ echo $API_KEY
sk-***************************abcd
```

The pattern across all three: show the reader exactly what *shape* of
value is expected (so they recognize a correctly-configured value when
they see one) without ever showing a value that would work if copied
verbatim into a real deployment.

## 77. Documentation for Operations

**Operational documentation** covers running and maintaining a *live*
system — a different concern from user documentation (how to use the
software) or developer documentation (how to change its code):

- **Deployment** — how a new version actually gets deployed.
- **Rollback** — how to revert to a previous version if a deployment
  is bad.
- **Health checks** — what endpoint/command confirms the system is
  healthy.
- **Logs** — where they live and how to search them.
- **Alerts** — what alerts exist and what each one means.
- **Common incidents** — recurring problems and their known fixes.
- **Recovery procedures** — how to restore service after a failure.

This category is aimed squarely at the **operator** audience
introduced in §1 — someone who needs the system running correctly
*right now*, often under time pressure, and has neither the time nor
the need to read source code to figure out what to do. §78–79 develop
this into the two most important concrete artifacts: runbooks and
troubleshooting guides.

## 78. Runbooks

A **runbook** is a specific, procedural document for responding to a
specific operational scenario — written so that someone under
incident-response pressure (possibly not the original author, possibly
at 3 a.m.) can follow it mechanically.

```markdown
## Runbook: Service Returning HTTP 500

**Symptom:** `billing-service` health check fails; clients receive
HTTP 500 on all requests.

**Diagnosis:**
1. Check service logs for the most recent error:
   \`\`\`bash
   kubectl logs -l app=billing-service --tail=50
   \`\`\`
2. Check database connectivity:
   \`\`\`bash
   kubectl exec -it billing-service-0 -- python -m billing_service.healthcheck
   \`\`\`

**Likely causes:**
- Database connection pool exhausted (look for `TooManyConnections` in
  logs).
- Payment gateway outage (look for repeated `GatewayTimeoutError`).

**Remediation:**
- Pool exhaustion: restart the service to reset the pool:
  \`\`\`bash
  kubectl rollout restart deployment/billing-service
  \`\`\`
- Gateway outage: confirm via the gateway's status page; no service-
  side fix exists — wait for gateway recovery, and consider enabling
  the maintenance-mode flag to return a clearer error to clients.

**Escalation:** If neither cause matches, or remediation doesn't
resolve within 15 minutes, page the on-call lead via PagerDuty.
```

**Why runbooks matter in production**: during an actual incident,
figuring out the right response *from first principles* is exactly
what a runbook exists to make unnecessary — it converts "think through
the whole system under pressure" into "follow these known steps,"
which is both faster and less error-prone for anyone, including the
system's own author.

## 79. Documentation for Troubleshooting

A general-purpose troubleshooting template, applicable to any
documented problem — the more general form of §30's error-
documentation shape and §78's runbook shape:

```markdown
**Problem:** One-line statement of what's going wrong.

**Symptoms:** What the user/operator actually observes (error message,
exit code, behavior).

**Likely Cause:** The most probable underlying reason, ranked if
there's more than one.

**Diagnosis:** Concrete steps/commands to confirm which cause applies.

**Solution:** The exact fix, as copy-pasteable commands where possible.

**Verification:** How to confirm the fix actually worked.

**Prevention:** How to avoid hitting this again, if applicable (a
config change, a documented gotcha to remember).
```

**Runbook vs. troubleshooting guide — the distinction worth
preserving**: a runbook (§78) is usually written for a specific,
already-known operational scenario ("what to do when the service
returns 500s"), often incident-response-oriented and urgent. A
troubleshooting guide (this section, and §30) is broader and more
reference-like — a collection of many smaller, individually-documented
problems a user or developer might hit, organized for scanning rather
than for following start-to-finish during an active incident.

## 80. Documentation for Onboarding

**How documentation helps a new engineer become productive** — by
converting what would otherwise be a series of individual questions
asked to teammates into a single, followable path:

```text
prerequisites
    ↓
clone repository
    ↓
install dependencies
    ↓
configure environment
    ↓
run application
    ↓
run tests
    ↓
run lint/type checks
    ↓
understand architecture
    ↓
make first change
```

This flow deliberately mirrors and extends §25's clone → install →
configure → run → test chain, adding the two steps that turn a working
local setup into an actually *productive* new contributor: reading
enough architecture documentation (§58) to understand where a change
belongs, and then making one small, real change — often literally
labeled a "good first issue" — to exercise the entire above chain
(including a PR and code review, §37) before tackling anything
consequential. A repository whose onboarding flow requires asking a
teammate at any of these nine steps has a documentation gap at exactly
that step.

## 81. Documentation Quality Principles

Eight properties worth evaluating any piece of documentation against:

- **Correctness** — does it accurately describe current behavior
  (§33–34)?
- **Completeness** — does it cover what a reader actually needs,
  without requiring them to guess or ask (§25)?
- **Clarity** — is it understandable on a single read, without
  requiring the reader to already know the answer?
- **Consistency** — does it use the same terms, style, and structure
  as the rest of the project's documentation (§11)?
- **Discoverability** — can a reader actually *find* this document
  when they need it (§53)?
- **Maintainability** — is it structured so that future updates are
  easy and low-risk, rather than requiring a rewrite (§73)?
- **Audience awareness** — does it match the depth and vocabulary of
  who's actually going to read it (§1, §55)?
- **Actionability** — does it tell the reader what to *do*, not just
  describe a state of affairs (§30, §78–79)?

Each of these is a separate failure mode — documentation can be
perfectly *correct* but fail on *discoverability* (an accurate answer
buried in the wrong file nobody thinks to open), or perfectly *clear*
but fail on *correctness* (a beautifully written, confidently wrong
explanation). A useful habit when reviewing documentation (your own or
someone else's) is running through this list explicitly, rather than
just asking "does this look okay."

## 82. Good vs Bad Documentation

Before/after pairs across several of the categories this chapter has
covered, each with the specific reason the improved version is better.

**Function docstring:**

```python
# Bad — vague, no contract information
def process(data):
    """Processes the data."""
    ...

# Good — states the actual contract
def process_transaction(raw: dict[str, str]) -> Transaction:
    """Parse and validate a raw transaction dict into a Transaction.

    Raises:
        ValidationError: If required fields are missing or malformed.
    """
    ...
```
*Why better:* names, types, and the exception contract replace a
restatement of the function's own name.

**README installation:**

```markdown
<!-- Bad -->
Install the requirements and run the app.

<!-- Good -->
\`\`\`bash
uv sync
uv run python -m billing_service
\`\`\`
```
*Why better:* exact, copy-pasteable commands replace a description of
commands (§25).

**CLI usage:**

```markdown
<!-- Bad -->
Use the balance command to check a balance.

<!-- Good -->
\`\`\`bash
billing-service balance --customer-id 12345
# Customer 12345: $128.50
\`\`\`
```
*Why better:* shows the real command and real output, not a
description of what the command does (§29).

**Configuration:**

```markdown
<!-- Bad -->
Set your API key.

<!-- Good -->
`API_KEY` (required, secret) — payment gateway key. Copy
`.env.example` to `.env` and fill in your own value; never commit
`.env`.
```
*Why better:* states required-vs-optional and secrecy explicitly, and
gives the exact safe mechanism (§27, §76).

**Troubleshooting:**

```markdown
<!-- Bad -->
If it doesn't work, check your config.

<!-- Good -->
**Symptom:** `ConfigError: API_KEY is missing`. **Solution:** `cp
.env.example .env` and set `API_KEY`. (§30)
```
*Why better:* names the exact symptom and exact fix, not a generic
suggestion to "check."

**Architecture description:**

```markdown
<!-- Bad -->
The service talks to the database and the payment gateway.

<!-- Good -->
Billing Service reads/writes PostgreSQL synchronously for order state,
and calls the Payment Gateway (external, third-party) synchronously
during checkout — a gateway outage therefore blocks checkout entirely
rather than degrading gracefully; see ADR 0007 for the planned
async-queue mitigation. (§58)
```
*Why better:* states the *nature* of each dependency (sync vs. async,
internal vs. external) and its *failure implication*, not just that a
connection exists.

## 83. Complete README Example

A realistic, complete `README.md` for a small Python project, showing
every section from §24 working together:

```markdown
# Billing Service

A small Python service for calculating order totals and processing
customer charges through a third-party payment gateway.

## Features

- Order-total calculation with bulk-discount support
- Idempotent charge processing via the payment gateway
- CLI for looking up a customer's current balance

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- A running PostgreSQL instance (see Configuration below)

## Installation

\`\`\`bash
git clone https://github.com/example/billing-service.git
cd billing-service
uv sync
\`\`\`

## Configuration

Copy `.env.example` to `.env` and fill in the values:

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string. |
| `API_KEY` | Yes | — | **Secret.** Payment gateway API key. |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, or `ERROR`. |

## Usage

\`\`\`bash
uv run python -m billing_service balance --customer-id 12345
# Customer 12345: $128.50
\`\`\`

## Testing

\`\`\`bash
uv run pytest
\`\`\`

## Linting and Type Checking

\`\`\`bash
uv run ruff check .
uv run mypy .
\`\`\`

## Project Structure

\`\`\`text
billing_service/
├── __init__.py
├── pricing.py       # calculate_total and related pricing logic
├── payments.py       # charge_customer and gateway integration
└── cli.py             # command-line entry point
\`\`\`

## Troubleshooting

**`ConfigError: API_KEY is missing`** — copy `.env.example` to `.env`
and set `API_KEY`.

## Development

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full contribution
workflow, coding standards, and PR process.

## License

MIT
```

## 84. Complete Docstring Example

A realistic module, fully documented at every level covered in this
chapter, with each part explained:

```python
"""Utilities for calculating order totals and applying discounts.

This module contains pure functions only — no I/O, no network calls.
Callers in billing_service.payments are responsible for persisting
any computed totals.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OrderItem:
    """A single line item within a customer order.

    Attributes:
        name: Display name of the item.
        unit_price: Price per unit, in the order's currency.
        quantity: Number of units ordered; must be non-negative.
    """

    name: str
    unit_price: float
    quantity: int


def calculate_total(
    price: float,
    quantity: int,
    *,
    bulk_discount_threshold: int = 10,
    bulk_discount_rate: float = 0.1,
) -> float:
    """Calculate the total price for a single line item.

    Applies a bulk discount when quantity meets or exceeds
    bulk_discount_threshold.

    Args:
        price: Unit price.
        quantity: Number of items; must be non-negative.
        bulk_discount_threshold: Minimum quantity to qualify for the
            bulk discount.
        bulk_discount_rate: Fractional discount applied when the
            threshold is met (0.1 == 10% off).

    Returns:
        The total price, after any bulk discount.

    Raises:
        ValueError: If quantity is negative.

    Examples:
        >>> calculate_total(10.0, 5)
        50.0
        >>> calculate_total(10.0, 10)
        90.0
    """
    if quantity < 0:
        raise ValueError("quantity must be non-negative")
    total = price * quantity
    if quantity >= bulk_discount_threshold:
        total *= 1 - bulk_discount_rate
    return total


class Order:
    """Represent a customer order composed of one or more line items.

    An Order is immutable once created — add_item is the only
    supported way to modify its contents, and it returns a NEW Order
    rather than mutating the existing one, to keep Order instances
    safe to share across threads.
    """

    def __init__(self, items: list[OrderItem]) -> None:
        self._items = list(items)

    def total(self) -> float:
        """Return the order's total price across all line items."""
        return sum(
            calculate_total(item.unit_price, item.quantity)
            for item in self._items
        )

    def add_item(self, item: OrderItem) -> Order:
        """Return a new Order with item appended.

        Does not modify this Order in place — see the class docstring.
        """
        return Order([*self._items, item])
```

**Walking through every part**: the **module docstring** states scope
(pure functions, no I/O) up front, so a reader immediately knows not
to look here for persistence logic. `OrderItem`'s **class docstring**
documents its **attributes**, since a dataclass's field types alone
don't convey `quantity`'s non-negativity constraint. `calculate_total`'s
**function docstring** documents its keyword-only discount parameters
and includes a **doctest example** (§50) that's actually executable.
`Order`'s **class docstring** documents its most important, non-obvious
property — immutability — right where a caller will see it before
calling `add_item` and being surprised the original wasn't modified;
its **method docstrings** stay short because `total()`'s summary line
alone is sufficient (§6), while `add_item` repeats the immutability
note briefly at the exact point a caller would otherwise get it wrong.

## 85. Complete Documentation Workflow

An end-to-end workflow, integrating everything from §35–37, §49, and
the earlier chapters of this module:

```text
write code
    ↓
add type hints
    ↓
write docstrings
    ↓
update README
    ↓
add tests/examples
    ↓
run Ruff
    ↓
run type checker
    ↓
run tests
    ↓
review documentation
    ↓
commit
    ↓
CI
    ↓
release documentation
```

- **Write code** — implement the change.
- **Add type hints** — communicate shape (§13,
  [`06-type-hints-and-type-checking.md`](./06-type-hints-and-type-checking.md)).
- **Write docstrings** — communicate behavior, contract, and
  constraints (§5–§18).
- **Update README** — if the change affects installation, usage,
  configuration, or CLI behavior (§24–29).
- **Add tests/examples** — including doctests where they fit naturally
  (§49–51).
- **Run Ruff** — format and lint, including docstring presence/style
  checks if configured (§67,
  [`05-ruff-formatting-and-linting.md`](./05-ruff-formatting-and-linting.md)).
- **Run type checker** — verify signatures match actual usage.
- **Run tests** — including any doctests, as part of the same run.
- **Review documentation** — self-review against §81's quality
  principles before opening the PR.
- **Commit** — code and documentation together, per §36.
- **CI** — automated checks (lint, types, tests, link checks) gate the
  merge.
- **Release documentation** — update `CHANGELOG.md`/release notes
  (§38–39) when the change ships in a release.

This is not a rigid, one-way pipeline that must be followed in strict
top-to-bottom order every single time — in practice, docstrings are
often written *while* coding, not strictly after — but it is the
*complete set of stages* a production-quality change passes through,
and skipping any one of them is exactly where the documentation debt
described in §72 begins to accumulate.

## 86. Documentation Debugging Lab

The module below has eight deliberate documentation problems, one per
category covered in this chapter. Read it carefully and try to find
all eight before checking the answer key.

```python
"""billing_service.pricing — pricing utilities."""

from __future__ import annotations


def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price.

    Args:
        price: Unit price.

    Returns:
        None.
    """
    if quantity < 0:
        raise ValueError("quantity must be non-negative")
    return price * quantity


def apply_discount(total: float, code: str) -> float:
    """Apply a discount code.

    Args:
        total: The total (float): a floating point number.
        code: A discount code, e.g. "SUMMER10".
    """
    if code == "SUMMER10":
        return total * 0.9
    return total
```

```markdown
## Installation

\`\`\`bash
pip install billing-service-old-name
\`\`\`

## Usage

\`\`\`python
from billing_service import calc_total
calc_total(9.99, 3)
\`\`\`

## Configuration

Set your discount codes in the environment.
```

**Answer key** — the eight issues, and the fix for each:

1. **Missing return documentation.** `calculate_total`'s `Returns:`
   section says `None`, but the function returns `price * quantity`
   (a `float`). *Fix:* `Returns: The total price.`
2. **Missing parameter documentation.** `calculate_total`'s `Args:`
   section documents `price` but omits `quantity` entirely. *Fix:*
   add `quantity: Number of items; must be non-negative.`
3. **Missing exception documentation.** `calculate_total` raises
   `ValueError` for negative quantity, but this isn't documented at
   all. *Fix:* add a `Raises: ValueError: If quantity is negative.`
   section.
4. **Wrong/redundant parameter description.** `apply_discount`'s
   `total` description ("The total (float): a floating point number")
   both repeats the type hint redundantly (§14) and tells the reader
   nothing useful. *Fix:* `total: The pre-discount amount.`
5. **Missing return documentation (second instance).**
   `apply_discount` has no `Returns:` section at all, despite having
   meaningful return behavior (discounted vs. unchanged total). *Fix:*
   add `Returns: The discounted total, or the original total
   unchanged if code is not recognized.`
6. **Outdated README installation command.** The install command
   references `billing-service-old-name`, an apparent former package
   name — this is a stale command (§33). *Fix:* update to the current
   package name.
7. **Broken/stale example.** The usage example imports `calc_total`,
   but the actual function (per the module above) is named
   `calculate_total` — this is exactly the renamed-function drift
   scenario from §32/§34. *Fix:* update the import and call to
   `calculate_total`.
8. **Unexplained configuration.** "Set your discount codes in the
   environment" names no actual variable, no format, no example — it's
   the "unexplained configuration" bad-example pattern from §32. *Fix:*
   name the actual variable, e.g. `DISCOUNT_CODES` (comma-separated
   list, optional, default empty) — with a concrete example value.

## 87. Coding + Documentation Exercises

### Level 1 — Basic

**1. Write a function docstring.**
*Task:* Write a Google-style docstring for:
```python
def square(n: int) -> int:
    return n * n
```
*Hints:* This is a simple, one-line-summary case — no `Args:`/`Returns:`
needed if the summary already covers it, per §6.
*Answer:*
```python
def square(n: int) -> int:
    """Return n squared."""
    return n * n
```
*Explanation:* A trivial, fully self-explanatory function needs only a
summary line — padding it with sections would violate §6's "document
what is useful and non-obvious" principle.

**2. Identify comment vs. docstring.**
*Task:* Is `# validate input before processing` a comment or a
docstring? Is `"""Validate input before processing."""` as a function's
first statement a comment or a docstring?
*Answer:* The first is a comment (starts with `#`, discarded at
runtime). The second is a docstring (a string literal, first statement,
stored as `__doc__`). See §4's comparison table.

**3. Document parameters.**
*Task:* Add an `Args:` section to:
```python
def greet(name: str, formal: bool) -> str:
    return f"Good day, {name}." if formal else f"Hi {name}!"
```
*Answer:*
```python
def greet(name: str, formal: bool) -> str:
    """Build a greeting string.

    Args:
        name: Person to greet.
        formal: If True, use formal phrasing.
    """
    return f"Good day, {name}." if formal else f"Hi {name}!"
```

**4. Document return values.**
*Task:* Add a `Returns:` section describing what `greet` above
actually returns.
*Answer:* `Returns: The greeting string, formal or informal per
'formal'.` *Explanation:* Describes *meaning*, not just repeats "a
str" (already known from the type hint, §14).

### Level 2 — Intermediate

**5. Document a class.**
*Task:* Write a class docstring for:
```python
class ShoppingCart:
    def __init__(self):
        self._items = []
```
*Answer:*
```python
class ShoppingCart:
    """A mutable collection of items a customer intends to purchase.

    Not thread-safe — concurrent add/remove calls on the same
    instance from multiple threads are not supported.
    """
```

**6. Document a module.**
*Task:* Write a module docstring for a file containing only
`ShoppingCart` and its supporting functions, with no I/O.
*Answer:* `"""Shopping cart data structures and pricing logic. No I/O
performed — callers handle persistence."""`

**7. Write a README.**
*Task:* Write a minimal README (Overview, Installation, Usage) for a
one-function CLI tool `wordcount` that counts words in a file.
*Answer:* (sketch)
```markdown
# wordcount

Counts words in a text file.

## Installation
\`\`\`bash
uv sync
\`\`\`

## Usage
\`\`\`bash
uv run python -m wordcount myfile.txt
# 452 words
\`\`\`
```

**8. Document CLI usage.**
*Task:* Add an exit-code table to the `wordcount` README above,
covering success and "file not found."
*Answer:*
```markdown
| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | File not found |
```

**9. Document configuration.**
*Task:* Document an optional `WORDCOUNT_ENCODING` variable (default
`utf-8`).
*Answer:* `WORDCOUNT_ENCODING` (optional, default `utf-8`) — text
encoding used to read the input file.

### Level 3 — Advanced

**10. Document package APIs.**
*Task:* For a package `textutils` with public functions
`count_words` and `count_lines`, and an internal helper
`_split_tokens`, write the `__init__.py` docstring and `__all__`.
*Answer:*
```python
"""textutils: word and line counting utilities for plain-text files."""

from textutils.counting import count_words, count_lines

__all__ = ["count_words", "count_lines"]
```
*Explanation:* `_split_tokens` is deliberately excluded from `__all__`
— it's internal (§21) and stays undocumented at the package level.

**11. Write architecture documentation.**
*Task:* Write a one-paragraph architecture overview for a two-
component system: a CLI that reads files and an internal counting
library it calls.
*Answer:* "The `wordcount` CLI (`wordcount/cli.py`) parses arguments
and reads the target file, then calls the `textutils` library
(`textutils/counting.py`) to perform the actual counting. `textutils`
has no knowledge of the CLI and performs no I/O itself, so it can be
reused by other callers independently of the CLI."

**12. Write an ADR.**
*Task:* Write a short ADR for the decision "use UTF-8 as the default
file encoding, with an override via `WORDCOUNT_ENCODING`."
*Answer:* (sketch, per §59's structure)
```markdown
# ADR 0001: Default to UTF-8 file encoding

## Context
Users' input files vary in encoding; guessing wrong produces
mojibake or a crash.

## Decision
Default to UTF-8 (the modern, near-universal default), with an
explicit WORDCOUNT_ENCODING override for legacy files.

## Alternatives Considered
- Auto-detect encoding: rejected — adds a dependency and can guess
  wrong silently, which is worse than a clear, documented default.

## Consequences
Users with non-UTF-8 files must set WORDCOUNT_ENCODING explicitly;
this is documented in the README configuration section.
```

**13. Create troubleshooting documentation.**
*Task:* Document `UnicodeDecodeError` using the §79 template.
*Answer:*
```markdown
**Problem:** UnicodeDecodeError when running wordcount.
**Symptoms:** Crash with `UnicodeDecodeError: 'utf-8' codec can't
decode byte...`
**Likely Cause:** Input file is not UTF-8 encoded.
**Diagnosis:** Check the file's actual encoding, e.g. via `file
-i myfile.txt`.
**Solution:** Set `WORDCOUNT_ENCODING` to the file's actual encoding.
**Verification:** Re-run; the crash should not recur.
```

**14. Create developer onboarding documentation.**
*Task:* Write the onboarding flow (§80) for the `wordcount` project.
*Answer:* clone → `uv sync` → (no configuration needed for default
UTF-8 case) → `uv run python -m wordcount README.md` → `uv run
pytest` → `uv run ruff check .` → read the architecture paragraph
above → pick a "good first issue."

### Level 4 — Production

**15. Document a backend service.**
*Task:* Sketch the API-contract-style docstring (§22) for an endpoint
handler `get_order(order_id: int) -> Order`.
*Answer:* (sketch) Document input expectations (must be an existing
order), output (full `Order` including private fields only for the
order's owner), errors (`OrderNotFoundError`, `PermissionDeniedError`),
side effects (none — read-only), compatibility (field set is stable
across minor versions).

**16. Document a data pipeline.**
*Task:* Using §60's template, document a pipeline that loads daily
`wordcount` results into a warehouse table.
*Answer:* (sketch) Input: per-file JSON results in
`s3://.../wordcount/{date}/`. Transformation: aggregate per-directory
totals. Output: `warehouse.wordcount_daily`, partitioned by `date`.
Failure handling: missing files for a date are logged, not fatal.
Retries: idempotent per `date`, safe to re-run.

**17. Document an ML pipeline.**
*Task:* Using §61's template, document a hypothetical
`word_frequency_anomaly` model.
*Answer:* (sketch) Inputs: daily word-frequency vector; outputs:
anomaly score in `[0, 1]`; preprocessing: must match training-time
normalization exactly; model version and dependency pin stated
explicitly; evaluation metrics linked; deployment/rollback pointed to
its runbook.

**18. Document an AI agent system.**
*Task:* Using §63's template, document a hypothetical
`summarize_wordcount_report` agent that can call a `send_email` tool.
*Answer:* (sketch) Tools table including `send_email`'s permissions;
explicit statement that the agent cannot send email to addresses
outside an allow-list, enforced in the tool implementation, not just
prompted; failure behavior on tool error; observability (logged tool
calls per request).

**19. Create a production runbook.**
*Task:* Using §78's template, write a runbook for "wordcount CLI
reports 0 words for a non-empty file."
*Answer:* (sketch) Symptom: 0 count on known non-empty file.
Diagnosis: check encoding (link to exercise 13's troubleshooting
entry) and check the file isn't binary. Likely cause: wrong encoding
silently producing zero tokens rather than crashing. Remediation: set
`WORDCOUNT_ENCODING` correctly. Escalation: file an issue if the
correct encoding still produces 0.

## 88. Mini Project — Production-Ready Python Project Documentation

**Project**: document a small, realistic Python project — an
`invoicing` package with a `generate_invoice(order, customer)`
function, a `Customer` dataclass, and a CLI — entirely *within this
lesson*, demonstrating every required piece end to end. (No files are
created outside this lesson document — everything below is the
demonstrated deliverable.)

**`README.md`** (per §83's template):

```markdown
# Invoicing

Generates PDF invoices from order and customer data.

## Prerequisites
Python 3.12+, uv.

## Installation
\`\`\`bash
uv sync
\`\`\`

## Configuration
| Variable | Required | Default | Description |
|---|---|---|---|
| `INVOICE_OUTPUT_DIR` | No | `./invoices` | Directory PDFs are written to. |

## Usage
\`\`\`bash
uv run python -m invoicing generate --order-id 501
# Wrote invoices/INV-501.pdf
\`\`\`

## Testing
\`\`\`bash
uv run pytest
\`\`\`

## Linting / Type Checking
\`\`\`bash
uv run ruff check .
uv run mypy .
\`\`\`

## Architecture Overview
The CLI (`invoicing/cli.py`) loads an Order and Customer from the
database, then calls `invoicing.pdf.generate_invoice`, a pure
function with no I/O, to build the PDF bytes, which the CLI then
writes to disk.

## Troubleshooting
**`CustomerNotFoundError`** — the `--order-id` references an order
whose customer record was deleted. Re-run against a valid order.

## Development
See CONTRIBUTING.md.
```

**Function docstrings:**

```python
def generate_invoice(order: Order, customer: Customer) -> bytes:
    """Render an invoice as PDF bytes.

    Pure function — performs no file I/O; callers write the returned
    bytes to disk or send them over the network as needed.

    Args:
        order: Must have at least one line item; a zero-item order
            raises ValueError.
        customer: Billing details shown on the invoice header.

    Returns:
        The rendered PDF, as bytes.

    Raises:
        ValueError: If order has no line items.
    """
```

**Class docstring:**

```python
class Customer:
    """A billing customer.

    Attributes:
        name: Full legal name, shown on invoices.
        billing_address: Shown on invoices; not validated by this
            class — validate at intake, before construction.
    """
```

**Module docstring:**

```python
"""invoicing.pdf — pure PDF-rendering logic for customer invoices.

No I/O in this module. See invoicing.cli for the file-writing entry
point.
"""
```

**CLI documentation** (per §29): `generate` command, `--order-id`
(required, int), exit codes `0` success / `1` order not found / `2`
customer not found.

**Configuration documentation** (per §64–65): the `INVOICE_OUTPUT_DIR`
table row shown in the README above.

**Troubleshooting section**: shown in the README above, following the
§30/§79 symptom → cause → solution shape.

**Developer setup**: `uv sync --group dev`, then the same
Ruff/mypy/pytest triad from §56.

**Testing instructions**: `uv run pytest`, shown above.

**Ruff instructions**: `uv run ruff check .` / `uv run ruff format .`.

**Type-checking instructions**: `uv run mypy .`.

**Architecture overview**: shown in the README above — CLI as I/O
boundary, `pdf` module as pure logic, matching the pattern established
in §58 and exercise 11.

**Changelog/release-notes concept** (per §38–39): a `CHANGELOG.md`
would record, e.g., `## [1.1.0] - Added INVOICE_OUTPUT_DIR
configuration (previously hardcoded to ./invoices).`

**Runbook concept** (per §78): a runbook for "PDF generation hangs"
would diagnose whether the hang is in font loading (a known slow
first-call cost) vs. a genuine deadlock, with the specific log lines
to check for each.

This mini-project demonstrates the full documentation stack — code-
level, project-level, operational — applied consistently to one small,
coherent system, exactly as a real project would need it.

## 89. Interview Questions

**Beginner**

- *What is a docstring?* A string literal as the first statement of a
  function/class/module, stored as `__doc__` and readable at runtime
  via `help()` or `obj.__doc__` (§3).
- *Comment vs. docstring?* A comment (`#`) is discarded at runtime and
  explains a specific line's *why*; a docstring is stored as `__doc__`
  and explains a function/class/module's overall *contract* (§4).
- *Why use `README.md`?* It's the first thing a new reader sees,
  answering "what is this and how do I run it" before they read any
  code (§23).
- *What is `__doc__`?* The attribute Python automatically sets to a
  function/class/module's docstring, or `None` if there isn't one
  (§3).

**Intermediate**

- *What should a function docstring contain?* A summary, plus whatever
  of parameters, return value, exceptions, side effects, and examples
  is actually useful and non-obvious for that specific function (§6).
- *Why combine type hints and docstrings?* Type hints communicate
  *shape* (checked statically); docstrings communicate *behavior,
  meaning, constraints* (checked by no tool, read by humans) (§13).
- *Google vs. NumPy docstrings?* Google style uses plain section
  headers and reads compactly; NumPy style puts each parameter's type
  on its own line and is the convention in scientific Python (§8–9,
  §11).
- *What belongs in a README?* Enough for a new reader to go from
  clone to a working, tested setup without asking the author a basic
  question — not exhaustive reference documentation (§24–25).
- *What is documentation drift?* Code and documentation gradually
  falling out of sync as code changes without a corresponding
  documentation update (§34).

**Advanced**

- *How would you document a Python package?* A package docstring plus
  `__all__` in `__init__.py` for the supported surface, individual
  module/function/class docstrings for detail, and a README/generated
  reference site for the package as a whole (§19–20, §47).
- *How would you keep documentation synchronized with code?* Update
  documentation in the same commit/PR as the code change (§36), review
  it in code review (§37), and use executable examples/doctests where
  practical so drift fails CI rather than rotting silently (§49–51).
- *How would you document a public API?* State input expectations,
  output behavior, errors, side effects, and compatibility guarantees
  explicitly — the API-contract shape from §22.
- *What should be generated versus manually written?* Exhaustive,
  mechanically-derivable reference (signatures, parameter lists) should
  be generated from docstrings/type hints (§47); narrative guides,
  tutorials, and "why" explanations must be hand-written, since a
  generator has no access to intent (§48).

**Production**

- *Design documentation for a large Python service.* Layer it:
  docstrings for code-level contracts, generated API reference for
  the package surface, a README for getting started, architecture
  docs + ADRs for structural decisions, runbooks for operational
  response, and a changelog for release-to-release tracking — matching
  each artifact to the audience question it answers (§1, §93).
- *How would you document an ML pipeline?* Model inputs/outputs
  (including exact preprocessing requirements), model version, exact
  dependency pins, evaluation metrics, and deployment/rollback
  procedure — because a model's silent-wrongness failure mode makes
  these especially high-stakes to leave undocumented (§61).
- *How would you document an agentic AI system?* Every tool's purpose
  and permissions, failure/retry behavior, model configuration, and
  hard-coded (not merely prompted) safety boundaries — because an
  agent that takes real actions turns a documentation gap into an
  operational risk (§62–63).
- *How would you prevent documentation from becoming stale?*
  Documentation-as-code practices (§35–37), executable examples where
  feasible (§49–51), periodic audits, and treating documentation debt
  (§72) as a tracked, prioritized backlog item rather than an
  afterthought.
- *How would you integrate documentation checks into CI?* Run
  doctests alongside the regular test suite, run a link checker, and
  (optionally) execute the literal commands shown in the README as a
  smoke test — turning silent drift into a build failure (§49).

## 90. Architecture Questions

- **Where should developer documentation live?** In the repository
  itself — `CONTRIBUTING.md`, developer-setup docs, architecture docs —
  so it's versioned identically to the code it describes and reviewed
  through the same PR process (§35, §56–57).
- **What belongs in README vs. architecture documentation?** README
  covers "how do I get this running" (installation, usage,
  configuration); architecture documentation covers "how is this
  built and why" (components, data flow, decisions) — a README that
  balloons into a full architecture explanation has outgrown its job
  (§24 vs. §58).
- **What belongs in API reference vs. tutorials?** API reference
  (generated, §47) is exhaustive and structured for lookup; a tutorial
  (§54) is a curated, ordered path for a beginner's first successful
  experience — mixing them serves neither reader well.
- **How should documentation be versioned?** Matched to how the
  project itself is versioned — a project with multiple supported
  major versions needs versioned docs trees; a project with one
  supported version at a time can keep a single, always-current set
  (§74).
- **How should a monorepo organize documentation?** Each package/service
  keeps its own README, docstrings, and (if it has one) its own ADR
  log for decisions local to it; cross-cutting architecture decisions
  that affect multiple packages get a top-level architecture doc/ADR
  log, so a reader knows where to look based on whether their question
  is package-local or system-wide.
- **How should production runbooks be maintained?** Reviewed and
  updated after every incident that reveals a gap (a runbook that
  didn't cover what actually happened is itself a finding), and
  periodically audited like any other operational documentation (§73,
  §78).
- **How should AI-agent tool contracts be documented?** As explicit,
  per-tool contracts — purpose, inputs, permissions, and hard
  (code-enforced) limits — reviewed with the same rigor as a public
  API contract, since a tool an agent can invoke is functionally a
  public API the model itself is the caller of (§22, §63).

## 91. Knowledge Check

1. What is the difference between a comment and a docstring?
2. Where must a docstring be placed for Python to recognize it as one?
3. What attribute stores a function's docstring?
4. Name the three common docstring styles covered in this chapter.
5. Why might a Google-style docstring omit the type in `Args:` when
   type hints are present?
6. What is the difference between a module docstring and package
   documentation?
7. What does `__all__` control, and how does it relate to
   documentation?
8. What is the difference between a public API and a private
   implementation detail, documentation-wise?
9. Name three sections a professional README typically includes.
10. What should a CLI's `--help` output be considered, documentation-
    wise?
11. What is documentation drift, and name one cause?
12. What is documentation debt, and how does it differ from
    documentation drift?
13. What is the difference between a changelog and release notes?
14. What does `doctest` do, and what module provides it?
15. What is the difference between Sphinx and MkDocs?
16. Is `pydoc` a third-party tool or part of the Python standard
    library?
17. What four categories does the Diátaxis framework use to organize
    documentation?
18. What is the difference between user documentation and developer
    documentation?
19. What does `CONTRIBUTING.md` typically contain?
20. What is an ADR, and what four sections does it typically have?
21. What is a runbook, and how does it differ from a troubleshooting
    guide?
22. Why do ML systems need explicit documentation of preprocessing
    steps?
23. Why do agentic AI systems typically need more documentation than
    ordinary deterministic code?
24. What should never appear in documentation, regardless of context?
25. Why is 100% documentation coverage not automatically a meaningful
    quality goal?

**Answers**

1. A comment (`#`) is discarded at runtime and explains a specific
   line; a docstring is a stored, runtime-accessible string explaining
   a function/class/module's contract (§4).
2. As the very first statement of the function/class/module body,
   before any other code (§3).
3. `__doc__` (§3).
4. Google, NumPy, Sphinx/reStructuredText (§7).
5. Because the type hint already states the type unambiguously;
   repeating it in prose is redundant and can drift out of sync with
   the signature (§14).
6. A module docstring describes one `.py` file; package documentation
   describes the whole library/directory, including which modules
   form its public surface (§18–19).
7. `__all__` controls what `from package import *` imports and signals
   (but does not enforce) the public API; it's related to but distinct
   from the package docstring, which explains *why* the package exists
   (§20).
8. A public API is a stable contract external code can depend on; a
   private implementation detail (conventionally underscore-prefixed)
   can change without notice and is documented more lightly, if at all
   (§21).
9. Any three of: overview, prerequisites, installation, configuration,
   usage, testing, troubleshooting, project structure, contribution
   (§24).
10. A form of user documentation — generated from the CLI's own
    argument definitions and always available without leaving the
    terminal (§29).
11. Code and documentation falling out of sync over time; caused by,
    e.g., API changes, refactoring, or configuration changes without a
    corresponding documentation update (§34).
12. Documentation drift is the *process* by which documentation goes
    stale; documentation debt is the *accumulated backlog* of stale,
    missing, and contradictory documentation that results (§72, and
    §34 distinguishes them explicitly).
13. A changelog is a terse, cumulative, per-release log; release notes
    are a more narrative, standalone announcement for one release,
    often including migration instructions (§38–39).
14. `doctest` scans docstrings for `>>>`-prefixed interactive-session
    examples and executes them, comparing actual to expected output;
    it's part of Python's standard library (§50).
15. Sphinx is reStructuredText-based with extensive customization and
    a steeper learning curve; MkDocs is Markdown-first with a gentler
    learning curve, commonly paired with a plugin for generated API
    reference (§44–46).
16. Part of the Python standard library — not a third-party tool
    (§43).
17. Tutorials, how-to guides, reference, and explanation (§53–54).
18. User documentation serves someone using the software as-is
    (installation, usage); developer documentation serves someone
    changing/extending it (architecture, testing, contribution) (§55).
19. Dev setup, coding standards, testing/linting/type-checking
    commands, branch workflow, PR and commit expectations (§56).
20. A short document capturing one architectural decision; typically
    Context, Decision, Alternatives Considered, Consequences (§59).
21. A runbook is a procedural response to one specific operational
    scenario, often incident-response-oriented; a troubleshooting
    guide is a broader, scannable collection of many smaller
    documented problems (§78–79).
22. Because mismatched preprocessing (e.g. unscaled features) produces
    confidently wrong predictions with no crash or visible error —
    exactly the "silent wrongness" failure mode documentation exists
    to prevent (§61).
23. Because their behavior additionally depends on a model provider's
    changing weights, non-determinism, and exact prompt wording — none
    of which is visible from reading the surrounding Python code the
    way ordinary logic is (§62).
24. Real passwords, API keys, private credentials, or sensitive
    production information — even in an example, even in a private
    repository, since git history persists it (§76).
25. Because coverage measures *presence* of a docstring, not its
    *correctness* or *usefulness* — a trivial, low-value docstring on
    every function achieves 100% coverage while adding little real
    information (§69).

## 92. Glossary

- **Docstring** — A string literal as the first statement of a
  function, method, class, or module, stored as `__doc__`.
- **Comment** — A `#`-prefixed line explaining a specific piece of
  code; discarded at runtime, not stored or introspectable.
- **README** — The conventional entry-point file (`README.md`)
  orienting a new reader to a project.
- **API documentation** — Documentation defining a public interface's
  contract: inputs, outputs, errors, and guarantees.
- **User documentation** — Documentation for someone using the
  software as-is (installation, usage, troubleshooting).
- **Developer documentation** — Documentation for someone
  changing/extending the software (architecture, testing,
  contribution).
- **Reference documentation** — Comprehensive, structured lookup
  material, often generated from docstrings.
- **Tutorial** — Learning-oriented, step-by-step documentation for a
  newcomer's first successful experience.
- **How-to guide** — Task-oriented instructions for a specific,
  already-understood goal.
- **Architecture documentation** — Documentation explaining a system's
  components, data flow, and structure.
- **ADR (Architecture Decision Record)** — A standalone document
  capturing one significant architectural decision and its reasoning,
  never rewritten after the fact.
- **Runbook** — A procedural document for responding to a specific
  operational scenario, written for use under incident pressure.
- **Changelog** — A terse, cumulative, per-release log of user-facing
  changes.
- **Release notes** — A narrative, standalone announcement for one
  release, often including migration instructions.
- **Documentation drift** — The gradual process of documentation
  falling out of sync with the code it describes.
- **Documentation debt** — The accumulated backlog of stale, missing,
  or contradictory documentation.
- **Doctest** — A standard-library mechanism that executes `>>>`-style
  examples embedded in docstrings and checks their output.
- **Sphinx** — A third-party, reStructuredText-based documentation
  generator.
- **MkDocs** — A third-party, Markdown-first documentation-site
  generator.
- **`pydoc`** — A standard-library module/tool for inspecting and
  rendering docstrings, underlying `help()`.
- **Public API** — The functions/classes/methods a project commits to
  keeping stable for external use.
- **Private API** — Internal implementation detail not part of the
  stable, supported contract.
- **Configuration documentation** — Documentation stating each
  configuration value's name, purpose, requiredness, type, default,
  and sensitivity.
- **Troubleshooting** — A documented problem's symptom, cause,
  solution, and verification.
- **Onboarding documentation** — Documentation guiding a new
  contributor from clone to their first productive change.

## 93. Final Mental Model

```text
CODE
  ↓
TYPE HINTS
  ↓
DOCSTRINGS
  ↓
README
  ↓
API / USER DOCUMENTATION
  ↓
EXAMPLES
  ↓
TESTED DOCUMENTATION
  ↓
ARCHITECTURE / OPERATIONS DOCUMENTATION
  ↓
MAINTAINED PRODUCTION DOCUMENTATION
```

Each layer communicates something the layer below it cannot:

- **Code** explains **HOW** the system works, precisely and
  executably — but says nothing about intent.
- **Types** explain **WHAT** shapes of data are expected — checked
  statically, but silent on meaning and behavior (§13).
- **Docstrings** explain **WHAT** individual code elements do —
  their contract, constraints, and side effects (§5–§18).
- **README** explains **HOW to get started** — installation,
  configuration, first run (§23–29).
- **User documentation** explains **HOW to use the system** —
  workflows, CLI usage, troubleshooting (§28–30, §55).
- **Examples** make abstract explanation concrete — the fastest path
  to a reader's own working code (§31–32).
- **Tested documentation** keeps the layers above honest — an
  executable example that fails loudly the moment it goes stale,
  instead of silently rotting (§49–51).
- **Architecture / operations documentation** explains **HOW the
  system is organized** and **HOW to run and recover it** — the layer
  a maintainer and an operator each need, for different reasons
  (§58–59, §77–79).
- **Maintained production documentation** is not a separate layer so
  much as a discipline applied to all the layers above, continuously —
  documentation as code, reviewed and updated with every change,
  rather than written once and left to drift (§35–37, §73).

## Final Takeaways

- Documentation is not an afterthought bolted onto finished code — it
  is how intent, contracts, and operational knowledge that code alone
  cannot express get communicated to every audience who needs them:
  users, developers, reviewers, operators, and API consumers (§1).
- A docstring documents a function/class/module's **contract** — what
  it needs, what it returns, what can go wrong, and what's non-obvious
  — not a restatement of what its code already makes visible (§5–§6,
  §70–71).
- Type hints and docstrings are complementary, not redundant: types
  communicate shape, statically checked; docstrings communicate
  behavior, meaning, and constraints, read by humans and tools (§13).
- A README is a project's front door — it should take a new reader
  from clone to a working, tested setup without requiring them to ask
  a single basic question (§23, §25).
- Documentation drift and documentation debt are the default outcome
  of treating documentation as separate from code; Documentation as
  Code — same repository, same commit, same review, same CI — is the
  practice that resists that default (§34–37, §72–73).
- Different documentation artifacts answer different questions for
  different audiences: a docstring, a README, an ADR, and a runbook
  are not interchangeable, and using the wrong one for a given
  question serves the reader poorly even when the content itself is
  accurate (§53–55, §58–59, §77–79).
- AI and ML systems typically need *more* explicit documentation than
  deterministic code, precisely because their behavior depends on
  things — model versions, prompts, non-determinism — that are
  invisible from reading the surrounding Python source (§61–63).
- Production-quality documentation is a continuous discipline, not a
  one-time deliverable: written alongside code, reviewed in every PR,
  validated where possible by execution (doctests, tested examples),
  and periodically audited — exactly like the code it describes (§73,
  §85).
