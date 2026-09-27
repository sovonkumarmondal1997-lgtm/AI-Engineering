# `functools`, Caching, and Partial Application

> **Roadmap:** Stage 1 — Programming & Computational Thinking → `09-Advanced-Production-Oriented-Python-Foundations`  
> **File:** `09-functools-cache-and-partial.md`

This chapter teaches Python's `functools` module from beginner level to production-oriented usage, with special focus on:

- higher-order functions and function reuse;
- memoization and caching;
- `functools.cache`;
- `functools.lru_cache`;
- cache keys, hashability, lifetime, invalidation, memory, and correctness;
- `functools.partial`;
- `functools.partialmethod`;
- related callable utilities such as `wraps`, `update_wrapper`, `reduce`, and `singledispatch`;
- testing, debugging, performance measurement;
- Applied AI Engineering use cases.

The goal is not API memorization. The goal is to understand **why** each tool exists and when its semantics match the problem.

## Learning objectives

By the end of this chapter you should be able to answer:

1. What problem does `functools` solve?
2. What are memoization, cache hits, and cache misses?
3. How does a manual cache work?
4. When is `@cache` appropriate?
5. When is `@lru_cache` more appropriate?
6. Why must cached arguments be hashable?
7. How do cache-key semantics affect correctness and hit rate?
8. What problems can mutable cached return values create?
9. What is cache invalidation?
10. What does `partial` do?
11. How is `partialmethod` different from `partial`?
12. When is a wrapper function or configuration object clearer?
13. What are the memory and lifecycle implications of process-local caching?
14. How do these ideas connect to AI inference, RAG, data pipelines, and agent systems?

## Version baseline

Examples target modern Python and explicitly call out Python 3.14-specific behavior where relevant.

| Feature | Version |
|---|---:|
| `lru_cache` | 3.2+ |
| `typed` option | 3.3+ |
| direct `lru_cache` decorator form | 3.8+ |
| `cache` | 3.9+ |
| `cache_parameters()` | 3.9+ |
| `Placeholder` for partial positional slots | 3.14+ |
| `partial` as a method descriptor | 3.14+ |

Always verify the interpreter version used by your production environment.

# 1. Why `functools` Exists

Python functions are objects. They can be passed around, returned, wrapped, configured, and reused.

```python
def add(a, b):
    return a + b

operation = add
print(operation(2, 3))
```

A second function can accept a function as an argument:

```python
def apply_twice(function, value):
    return function(function(value))

print(apply_twice(lambda x: x + 1, 10))
```

The `functools` module supplies standard-library utilities for this style of function-oriented programming.

A useful mental map is:

```text
functools
   |
   +-- adapt callables
   |      +-- partial
   |      +-- partialmethod
   |
   +-- reuse results
   |      +-- cache
   |      +-- lru_cache
   |
   +-- preserve/inspect wrappers
   |      +-- wraps
   |      +-- update_wrapper
   |
   +-- other function composition
          +-- reduce
          +-- singledispatch
```

The important engineering idea is:

> A standard abstraction communicates intent to another engineer.

`@lru_cache(maxsize=128)` says much more than an arbitrary global dictionary whose purpose must be reverse-engineered.

# 2. The Problem: Repeated Computation

Suppose a function performs expensive deterministic work:

```python
def expensive_computation(x):
    total = 0
    for number in range(1, 500_000):
        total += (number * x) % 97
    return total
```

Now:

```python
expensive_computation(10)
expensive_computation(10)
expensive_computation(10)
```

may repeat exactly the same computation.

The repeated work has consequences:

- CPU is used repeatedly.
- latency is paid repeatedly.
- throughput is reduced.
- power and infrastructure resources are consumed.

But repeated input alone does not justify caching.

Compare:

```python
from datetime import datetime

def current_time():
    return datetime.now()
```

with:

```python
def normalize(text):
    return " ".join(text.lower().split())
```

The first intentionally changes over time. The second can often be treated as a stable value transformation.

The engineering question is:

> **Would returning the previous result for the same logical input still be correct?**

# 3. Memoization

**Memoization** means storing a function's result so the result can be reused when the same key is requested again.

Conceptual flow:

```text
arguments
   |
   v
cache lookup
   |
   +---- hit ----> return stored result
   |
   +---- miss ---> compute
                    |
                    v
                 store result
                    |
                    v
                 return
```

A manual implementation makes the concept concrete:

```python
memo = {}

def square(x):
    if x in memo:
        return memo[x]

    result = x * x
    memo[x] = result
    return result
```

Calls:

```python
print(square(5))  # computes
print(square(5))  # reuses
print(square(7))  # computes
```

The cache is conceptually:

```text
5 -> 25
7 -> 49
```

Memoization is a special case of caching where function arguments determine reusable results.

# 4. Cache Hit and Cache Miss

A **cache hit** means the requested key is already stored.

A **cache miss** means it is not.

```python
store = {}

def get_value(key):
    if key in store:
        print("HIT")
        return store[key]

    print("MISS")
    value = key * 10
    store[key] = value
    return value

get_value(4)
get_value(4)
```

Expected:

```text
MISS
HIT
```

The hit/miss distinction matters because caching creates two different execution paths.

### Hit

```text
key creation
→ lookup
→ return stored value
```

### Miss

```text
key creation
→ lookup
→ execute function
→ store
→ return
```

A cache is valuable when the work avoided on hits is worth the cost of keying, storing, and retaining results.

# 5. Manual Memoization and Its Limitations

A closure can keep a private cache:

```python
def make_cached_square():
    cache = {}

    def square(x):
        if x in cache:
            return cache[x]

        result = x * x
        cache[x] = result
        return result

    return square

square = make_cached_square()
print(square(5))
print(square(5))
```

This teaches an important concept: the cache has a lifetime.

The dictionary lives as long as the returned closure keeps the closed-over state alive.

However, manual caching leaves many responsibilities with you:

- key construction;
- hashability;
- cache growth;
- invalidation;
- introspection;
- testing;
- concurrency behavior;
- documentation.

The standard library provides reusable abstractions for common memoization behavior.

# 6. `functools.cache`

Import it:

```python
from functools import cache
```

Use it as a decorator:

```python
@cache
def square(x):
    print("computing")
    return x * x

print(square(5))
print(square(5))
```

Conceptually, the second call uses the first call's stored result.

Python documents `cache()` as a simple lightweight **unbounded** function cache and explains that it is equivalent in effect to `lru_cache(maxsize=None)`. Because it does not manage eviction, its implementation can be simpler than a bounded LRU cache. citeturn147567search1

### Unbounded is the critical word

An unbounded cache can continue accumulating distinct keys:

```text
new key
→ new cache entry
→ more retained memory
```

Therefore `@cache` is especially attractive when the set of useful keys is naturally bounded or otherwise known to be small enough for the application's lifetime.

# 7. `cache` Argument Requirements

Cached arguments must be hashable.

Simple examples:

```python
hash(10)
hash("hello")
hash(("model-a", "v1"))
```

Common unhashable containers include:

```python
[]
{}
set()
```

Therefore this is invalid for the cache boundary:

```python
from functools import cache

@cache
def total(items):
    return sum(items)

# total([1, 2, 3])
```

The call raises `TypeError` because a list cannot be used as part of the hash-based cache key.

An immutable representation may be appropriate:

```python
print(total((1, 2, 3)))
```

But conversion is not automatically correct.

Ask whether the computation depends on:

- order,
- duplicates,
- element identity,
- original types.

For unordered unique data, a representation such as `frozenset` can sometimes be appropriate:

```python
frozenset({"a", "b", "a"})
```

The representation must match business semantics.

# 8. Hashability, Equality, and Cache Keys

Hashability matters because dictionary-like cache structures need keys.

The simplified model is:

```text
function arguments
       ↓
cache key semantics
       ↓
hash + equality
       ↓
cached entry
```

This connects:

- `hash()`,
- dictionary keys,
- set membership,
- memoization.

Do not confuse value equality with identity.

```python
a = "hello"
b = "".join(["he", "llo"])

print(a == b)
```

The values can compare equal even if they are distinct objects.

For caching, the key is about argument semantics rather than simply whether two references point to the same object.

When debugging unexpected misses, inspect:

1. the exact values;
2. the exact types;
3. equality behavior;
4. whether normalization is consistent;
5. whether different keyword-call patterns are being used.

# 9. Mutable Arguments and Canonicalization

Mutable objects are problematic as direct cache arguments because their state can change and common mutable built-ins are unhashable.

A better design can move canonicalization outside the cached boundary:

```python
from functools import cache

def normalize_items(items):
    return tuple(items)

@cache
def process_items(items):
    return sum(items)

print(process_items(normalize_items([1, 2, 3])))
```

Now the cached function sees an immutable tuple.

However, canonicalization must preserve the intended semantics.

Suppose order does not matter:

```text
["a", "b"]
["b", "a"]
```

A tuple distinguishes them. A `frozenset` does not.

Suppose duplicates matter:

```text
["a", "a", "b"]
```

A set-like representation would lose multiplicity.

Therefore:

> **Canonicalize according to the function's semantic contract, not merely according to what is hashable.**

# 10. Mutable Cached Return Values

A cached result can itself be mutable.

```python
from functools import cache

@cache
def get_items():
    return []

items = get_items()
items.append("event")

print(get_items())
```

The later call can return the same list object.

That creates shared state:

```text
cache
 └── key → list object ← caller A
                      ← caller B
```

Safer designs include immutable return values:

```python
@cache
def get_items():
    return ("a", "b", "c")
```

or caching immutable internal data and creating a fresh mutable object for each caller:

```python
@cache
def _get_items():
    return ("a", "b", "c")

def get_items():
    return list(_get_items())
```

This distinction matters in production systems because a cache can otherwise become an unexpected shared mutable state mechanism.

# 11. Cache Lifetime

A `functools` cache is in-memory state attached to the wrapped callable.

Conceptually:

```text
process starts
    ↓
function created
    ↓
cache grows
    ↓
process exits
    ↓
cache disappears
```

Therefore a process-local `functools` cache is not automatically:

- durable storage;
- a database;
- a shared cache across processes;
- a distributed cache.

### Lifetime questions

Ask:

- How long does the function object remain alive?
- How long should the result remain valid?
- What happens on process restart?
- Can the key space grow indefinitely?
- Does the cached result retain large objects?

The cache lifetime and the business-data lifetime are not the same concept.

# 12. `cache_clear()`

Cached wrappers expose `cache_clear()`.

```python
from functools import cache

@cache
def compute(x):
    print("computing")
    return x * 2

compute(5)
compute(5)

compute.cache_clear()

compute(5)
```

Conceptually:

```text
call 1 → miss
call 2 → hit
clear
call 3 → miss
```

Common uses include:

- invalidation;
- tests;
- configuration changes;
- development/debugging;
- memory management;
- semantic/version changes.

`cache_clear()` clears the cache as a whole. It is not arbitrary key deletion and does not provide TTL semantics.

# 13. `lru_cache` Fundamentals

Import it:

```python
from functools import lru_cache
```

Use a bounded cache:

```python
@lru_cache(maxsize=128)
def square(x):
    print("computing")
    return x * x
```

`LRU` means **Least Recently Used**.

Python documents `lru_cache` as a memoizing decorator that retains up to `maxsize` recent calls, with `cache_info()`, `cache_clear()`, `cache_parameters()`, and `__wrapped__` available on the wrapper. citeturn147567search2turn147567search4

The key difference from `cache()` is that an LRU cache can intentionally discard entries.

# 14. Why LRU Exists

Imagine a long-running service with millions of distinct inputs.

An unbounded cache can grow continuously:

```text
request A → store
request B → store
request C → store
...
request 1,000,000 → store
```

A bounded cache changes the policy:

```text
keep only the useful recent working set
```

LRU is based on recency.

The reasoning is:

> The entries used recently may be more likely to be used again soon.

This pattern can fit workloads such as:

- recently used metadata;
- repeated parsing of hot documents;
- recent configuration reads;
- stable application lookups.

It is not a guarantee. If almost every input is unique, an LRU policy cannot manufacture reuse.

# 15. `maxsize`

Example:

```python
from functools import lru_cache

@lru_cache(maxsize=3)
def lookup(x):
    return x * 10
```

The cache is bounded by entry count.

A conceptual sequence:

```text
lookup(A)
lookup(B)
lookup(C)
```

Now three entries are retained.

If `A` is requested again, it becomes recently used.

If `D` arrives, the least recently used entry is a candidate for eviction.

### Important distinction

`maxsize` is an **entry limit**, not:

- a byte limit;
- a megabyte limit;
- a time-to-live;
- a CPU limit.

Actual memory depends on the objects referenced by keys and values.

# 16. LRU Eviction Step by Step

Suppose:

```text
maxsize = 3
```

Conceptual state:

```text
A
A, B
A, B, C
```

Access `A`:

```text
B, C, A
```

Then access `D`:

```text
C, A, D
```

`B` is the least recently used entry in this teaching model.

Do not interpret this as "delete the oldest insertion." LRU means least recently **used**, which can differ from insertion order.

### Good fit

LRU is attractive when recent calls are useful predictors of near-future calls.

### Poor fit

If calls are mostly one-time unique values, the cache may incur memory and lookup overhead without creating many hits.

# 17. `lru_cache(maxsize=None)` vs `cache`

You can write:

```python
@lru_cache(maxsize=None)
def compute(x):
    return x * x
```

`maxsize=None` means the LRU size limit is disabled; the cache can grow without bound. Python documents this behavior explicitly. citeturn147567search6

For a simple unbounded memoization use case:

```python
@cache
def compute(x):
    return x * x
```

usually communicates intent more directly.

The two should not be distinguished by imaginary universal speed claims. The important difference is API and semantics:

```text
cache
→ simple unbounded cache

lru_cache
→ configurable cache with LRU behavior
```

# 18. `typed=True`

`lru_cache` supports:

```text
@lru_cache(maxsize=128, typed=True)
```

This can separate calls whose immediate arguments differ by type.

Example:

```python
from functools import lru_cache

@lru_cache(maxsize=None, typed=True)
def describe(value):
    print("computing")
    return type(value).__name__

print(describe(1))
print(describe(1.0))
```

With `typed=True`, the argument types can contribute to distinct cached calls.

With `typed=False`, equal arguments are generally treated as the same logical call, but Python documents subtleties for particular types and nested values. citeturn147567search2turn147567search6

Use `typed=True` when type distinctions are part of the function's semantics.

Do not enable it automatically.

# 19. Cache Key Semantics with Positional and Keyword Arguments

Consider:

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def combine(a, b):
    return f"{a}:{b}"
```

Repeated positional calls are easy:

```python
combine(1, 2)
combine(1, 2)
```

Keyword forms require more care:

```python
combine(a=1, b=2)
combine(b=2, a=1)
```

Python's documentation states that distinct argument patterns can be treated as distinct calls and specifically notes that differing keyword-argument order can produce separate cache entries. citeturn147567search2turn147567search4

Therefore, do not assume:

```text
semantic equivalence
=
identical cache entry
```

### Production technique

Normalize at a stable internal boundary:

```python
def get_config(model_id, *, region):
    return _get_config_cached(model_id, region)

@lru_cache(maxsize=256)
def _get_config_cached(model_id, region):
    return {"model_id": model_id, "region": region}
```

This gives the cache a predictable calling convention.

# 20. `cache_info()`

`lru_cache` exposes:

```python
cache_info()
```

Example:

```python
from functools import lru_cache

@lru_cache(maxsize=4)
def square(x):
    return x * x

square(2)
square(2)
square(3)

print(square.cache_info())
```

A representative result looks like:

```text
CacheInfo(hits=1, misses=2, maxsize=4, currsize=2)
```

The fields mean:

- `hits`: calls served from cached entries;
- `misses`: calls requiring the wrapped function;
- `maxsize`: configured capacity;
- `currsize`: entries currently stored.

A basic hit ratio is:

```python
info = square.cache_info()
total = info.hits + info.misses

hit_ratio = info.hits / total if total else 0.0
print(hit_ratio)
```

This is a diagnostic metric, not proof that caching is beneficial.

# 21. `cache_parameters()`

Modern `lru_cache` wrappers expose:

```python
cache_parameters()
```

Example:

```python
from functools import lru_cache

@lru_cache(maxsize=256, typed=True)
def f(x):
    return x

print(f.cache_parameters())
```

Conceptually:

```python
{"maxsize": 256, "typed": True}
```

Python documents the returned dictionary as informational. Mutating it does not alter the cache configuration. citeturn147567search2turn147567search4

It is useful during debugging:

```text
configuration
→ inspect parameters
→ compare with workload
```

For example, a cache with a large intended working set but `maxsize=8` may evict so aggressively that the hit rate is poor.

# 22. `__wrapped__`

The original function remains accessible through:

```python
__wrapped__
```

Example:

```python
from functools import lru_cache

@lru_cache(maxsize=16)
def compute(x):
    return x * 2

print(compute(5))
print(compute.__wrapped__(5))
```

The second call bypasses the caching wrapper.

Python documents `__wrapped__` as useful for introspection, bypassing the cache, and re-wrapping the underlying callable. citeturn147567search2turn147567search4

A testing or debugging use is comparing:

```text
cached path
vs
uncached underlying function
```

Do not expose this as the primary business API unless there is a clear reason.

# 23. Decorator Stacking and Cache Placement

Caching is a decorator, so decorator order can change behavior.

These are not automatically equivalent:

```python
@cache
@other_decorator
def f(x):
    ...
```

and:

```python
@other_decorator
@cache
def g(x):
    ...
```

The inner transformation occurs first.

A simple logging decorator illustrates the idea:

```python
from functools import cache, wraps

def log_calls(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print("called", args, kwargs)
        return function(*args, **kwargs)
    return wrapper

@cache
@log_calls
def f(x):
    return x * 2

@log_calls
@cache
def g(x):
    return x * 2
```

In the first arrangement, the logging layer participates differently in what gets cached than in the second arrangement.

The engineering lesson is:

> **When debugging decorators, expand the nesting mentally from the inside out.**

# 24. Cache Purity and Determinism

Caching is safest when:

```text
same relevant inputs
→ same valid result
```

Examples often well suited to memoization:

```python
def normalize(text):
    return " ".join(text.lower().split())
```

```python
def square(x):
    return x * x
```

Potentially unsafe to cache blindly:

```python
from datetime import datetime

def current_time():
    return datetime.now()
```

```python
import random

def random_value():
    return random.random()
```

```python
def send_email(user_id):
    ...
```

The first two depend on changing or intentionally variable state.

The last has a side effect.

The cache must not change the meaning of the function merely because the decorator is syntactically easy to add.

# 25. Caching Side Effects

This is a common production mistake:

```python
from functools import cache

@cache
def send_email(user_id):
    send_email_to_network(user_id)
    return True
```

Call:

```python
send_email(123)
send_email(123)
```

The second call can reuse the stored result without repeating the function body.

Therefore the email side effect may occur only once.

### Separate concepts

**Computation**

```text
input → reusable value
```

**Command**

```text
input → external side effect
```

Memoization naturally fits computation.

For commands, use explicit patterns for:

- idempotency;
- job deduplication;
- exactly-once requirements;
- transaction semantics.

Do not use `functools.cache` as a replacement for those systems.



# 26. Cache and External State

A cached result can become stale whenever the function reads state that can change outside its explicit arguments.

Examples include:

- current time;
- random-number generators;
- environment variables;
- feature flags;
- files;
- databases;
- remote APIs;
- authorization context;
- tenant context;
- model configuration.

Consider:

```python
from functools import lru_cache

settings = {"mode": "production"}

@lru_cache(maxsize=16)
def get_mode():
    return settings["mode"]

print(get_mode())

settings["mode"] = "debug"

print(get_mode())
```

The second call can still return `"production"`.

The cache did exactly what it was asked to do: reuse the prior result.

The mistake is in the semantic contract.

### A useful question

Ask:

> "What state can change the function's output even though the function's argument list stays the same?"

That hidden state is part of the real dependency graph.

Either make it explicit, keep it stable for the cache lifetime, invalidate when it changes, or avoid caching.

# 27. Cache and Current Time

Do not blindly cache functions whose meaning is "what time is it now?"

```python
from functools import cache
from datetime import datetime, timezone

@cache
def current_time():
    return datetime.now(timezone.utc)
```

The first result can be reused indefinitely.

So the function no longer means:

```text
current time
```

It effectively means:

```text
time when the first uncached call occurred
```

A better design is not to cache the time source.

If a larger computation depends on time, consider passing a time value explicitly:

```python
from datetime import datetime, timezone

def status_at(now):
    ...
```

Then a computation can be cached by `now` if that actually matches the desired semantics.

# 28. Cache and Randomness

Random values have intentionally variable semantics.

```python
import random

def random_value():
    return random.random()
```

Caching this function would transform:

```text
new random value
```

into:

```text
reuse the first random value
```

That may be correct in a deterministic simulation, but then determinism should be explicit in the design.

For example, a deterministic transformation of an explicit seed:

```python
def deterministic_value(seed):
    rng = random.Random(seed)
    return rng.random()
```

has a much clearer cache contract than a function reading global randomness.

The point is not "never cache random-derived computation."

The point is:

> Cache only when the caller's meaning of "same input" matches the function's actual dependencies.

# 29. Cache and Environment Variables

Suppose:

```python
import os
from functools import cache

@cache
def feature_enabled():
    return os.getenv("FEATURE_X") == "1"
```

If the environment can change during the process lifetime, the cached function holds a stale snapshot.

One option is to load configuration once intentionally at startup:

```text
startup configuration
→ immutable application state
→ stable reads
```

In that case caching may be unnecessary.

Another is to make the configuration version explicit:

```python
def feature_enabled(config_version):
    ...
```

The correct design depends on the configuration lifecycle.

# 30. Cache and Files

Consider:

```python
from functools import lru_cache

@lru_cache(maxsize=64)
def parse_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return parse(file.read())
```

If the file changes, the cached result may become stale.

Possible semantic keys include:

```text
(path, file_version)
```

or:

```text
(path, content_digest)
```

The choice depends on the application.

Do not blindly rely on modification timestamps without considering filesystem behavior, concurrent updates, and deployment conventions.

The key lesson is:

```text
file identity
is not necessarily
file content identity
```

# 31. Cache and Databases

Suppose:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user(user_id):
    return database.fetch_user(user_id)
```

This may reduce repeated reads.

But database state can change:

```text
DB
→ user 123 is ACTIVE

cache
→ user 123 is PENDING
```

Questions to answer:

- Are reads allowed to be stale?
- How frequently does data change?
- Can another process update the record?
- Should writes invalidate the cache?
- Is the record tenant-specific?
- Is authorization part of the result?
- Is process-local scope acceptable?

### Broad invalidation

```python
get_user.cache_clear()
```

is simple but may destroy all useful entries.

### Better architecture

A dedicated application cache may support:

- key-level invalidation;
- TTL;
- shared workers;
- explicit namespaces;
- serialization.

Do not force a process-local decorator to solve a system-level cache lifecycle problem.

# 32. Cache and API Responses

Remote APIs may be expensive or rate-limited, which makes caching attractive.

Example:

```python
def fetch_metadata(model_id):
    return api_client.get_metadata(model_id)
```

Before caching, establish:

```text
How often does the response change?
Who is allowed to see it?
Does the result depend on credentials?
Does the API return version information?
```

For public, stable metadata, caching may be straightforward.

For user-specific data:

```text
(user_id, resource_id)
```

may be necessary.

For authorization-sensitive data:

```text
(tenant_id, user_id, resource_id, authorization_scope)
```

may be part of the semantic key.

For real-time information, a TTL/freshness-aware cache may be more appropriate than `functools`.

# 33. Cache Invalidation

A cache becomes stale when the underlying truth changes but the stored result does not.

Conceptually:

```text
source of truth
     |
     | update
     v
new state

cache
     |
     +---- old state
```

The application must determine when the old cache entry is no longer valid.

Common strategies:

### Explicit invalidation

```python
function.cache_clear()
```

Useful for broad resets.

### Versioned keys

```text
(model_version, input)
```

The new version naturally uses a different key.

### TTL

```text
value valid for N seconds
```

Not provided by `cache`/`lru_cache` themselves.

### Bypass

Do not cache a highly dynamic function.

### Important distinction

LRU eviction is not the same as freshness.

An entry can be recently used and still be stale.

# 34. `functools` Cache vs External Cache

| Characteristic | `cache` / `lru_cache` | External cache |
|---|---|---|
| Scope | one process | often shared |
| Persistence | process lifetime | depends on system |
| TTL | not built in | commonly available |
| Shared between workers | no | often yes |
| Network cost | none | usually present |
| Serialization | normal Python objects | usually serialized |
| Operational complexity | low | higher |
| Best fit | local memoization | shared application caching |

An external system may be appropriate when results need to be shared between:

- web workers;
- containers;
- replicas;
- processes;
- services.

The important boundary is:

> **A process-local memoization cache is not a distributed cache.**

# 35. Cache Memory Trade-Offs

Caching trades repeated computation for retained state.

```text
less CPU work
     ↓
more memory retention
```

A cached wrapper can retain references to argument objects and returned values while entries remain cached. Python documents this explicitly for `lru_cache`. citeturn147567search2turn147567search4

The memory question is therefore:

```text
number of entries
×
size of referenced object graph
```

This is only a reasoning model.

Actual memory depends on:

- Python object overhead;
- shared references;
- nested object graphs;
- allocator behavior;
- key representation;
- result representation.

### Practical warning

This can be dangerous:

```python
@cache
def load_huge_document(document_id):
    return huge_object()
```

If millions of IDs can arrive, the process may retain a large amount of memory.

Bounded caching may help:

```python
@lru_cache(maxsize=256)
def load_huge_document(document_id):
    return huge_object()
```

But `maxsize=256` still says nothing about bytes.

# 36. `maxsize` Is an Entry Limit

`maxsize` means:

```text
maximum retained cache entries
```

It does not mean:

```text
maximum RAM
```

For example:

```text
10 entries × 20 MB each
≈ potentially hundreds of MB
```

whereas:

```text
10,000 entries × tiny integers
```

can be relatively small.

This is why cache sizing needs representative measurements.

### Production decision

Estimate:

```text
working-set size
+
average key/value footprint
+
acceptable memory budget
```

Then validate empirically.

# 37. Cache Performance and Break-Even Thinking

A miss includes the underlying computation.

A hit avoids it.

Conceptually:

```text
MISS
→ lookup + compute + store

HIT
→ lookup + return
```

Caching is useful when the avoided computation is meaningful relative to:

- key creation;
- lookup;
- memory retention;
- cache management.

### Strong candidates

- expensive deterministic parsing;
- repeated normalization;
- repeated stable metadata computation;
- recursive subproblem reuse.

### Weak candidates

- trivial arithmetic;
- mostly unique inputs;
- highly volatile data;
- results whose validity changes faster than the cache lifecycle.

Do not assume "expensive" automatically means "cacheable."

# 38. Cache Break-Even Example

Suppose:

```text
computation = 50 ms
cache lookup = small local cost
```

If the same input repeats frequently, the cache can save substantial work.

Now suppose:

```text
computation = extremely cheap
unique inputs = nearly 100%
```

The cache may add state without providing meaningful benefit.

The decision can be framed as:

```text
Expected savings
=
hit frequency × cost avoided
```

versus:

```text
cache costs
=
lookup + memory + lifecycle + correctness complexity
```

This is a conceptual model, not a universal numerical formula.

# 39. Measuring Cache Effectiveness

For `lru_cache`:

```python
info = function.cache_info()

total = info.hits + info.misses
hit_ratio = info.hits / total if total else 0.0

print(info)
print(hit_ratio)
```

Observe:

```text
hits
misses
currsize
maxsize
```

If the hit ratio is very low, investigate:

- mostly unique inputs;
- inconsistent call patterns;
- cache too small;
- incorrect key normalization;
- caching the wrong operation.

If the hit ratio is high but memory is too large, reduce capacity or reconsider the result being cached.

If the hit ratio is high but correctness is poor, the cache key/lifecycle is wrong.

# 40. Cache Observability

A production cache needs more than "the decorator is present."

A useful diagnostic chain is:

```text
cache configuration
      ↓
workload
      ↓
hits / misses
      ↓
memory
      ↓
correctness / freshness
```

A cache dashboard might monitor:

- call volume;
- hit ratio;
- current entry count;
- latency on hits;
- latency on misses;
- memory pressure;
- invalidation events.

`cache_info()` provides only a small subset of these signals.

Use it as a local diagnostic primitive, not a complete monitoring platform.



# 41. Cache Testing Basics

Caching adds state to a function that looks stateless.

A test suite must control that state.

```python
from functools import lru_cache

@lru_cache(maxsize=8)
def square(x):
    return x * x

def test_square():
    square.cache_clear()

    assert square(4) == 16
    assert square(4) == 16

    info = square.cache_info()
    assert info.misses == 1
    assert info.hits == 1
```

### Why clear first?

An earlier test can already have inserted:

```text
4 → 16
```

Then the test expecting the first call to be a miss is actually performing a hit.

### Testing rule

If the assertion depends on cache state, establish the cache state first.

# 42. Testing Cache Correctness

A useful cache test matrix includes:

| Test | What it proves |
|---|---|
| first call | underlying computation works |
| repeated call | cache reuse works |
| new key | distinct inputs remain distinct |
| `cache_clear()` | invalidation is effective |
| changed version | semantic versions do not collide |
| mutable result | sharing behavior is understood |
| external state | freshness assumptions are explicit |

Example:

```python
from functools import lru_cache

calls = 0

@lru_cache(maxsize=8)
def compute(x):
    global calls
    calls += 1
    return x * 2

compute.cache_clear()
calls = 0

compute(10)
compute(10)

assert calls == 1
```

A test like this verifies the memoization effect without relying on timing.

# 43. Testing `partial`

Test from the callable contract:

```python
from functools import partial

def multiply(a, b):
    return a * b

def test_double():
    double = partial(multiply, 2)

    assert double(5) == 10
    assert double(9) == 18
```

Test keyword configuration too:

```python
def format_value(value, *, prefix):
    return f"{prefix}{value}"

formatted = partial(format_value, prefix="ID-")

assert formatted(42) == "ID-42"
```

And inspect the stored configuration when useful:

```python
assert formatted.func is format_value
assert formatted.args == ()
assert formatted.keywords == {"prefix": "ID-"}
```

Test only what your code actually depends on.

# 44. Debugging Cache Problems: A Repeatable Workflow

When cache behavior looks wrong:

## Step 1 — Identify the wrapper

Find:

```text
@cache
```

or:

```text
@lru_cache(...)
```

## Step 2 — Identify the exact key inputs

Write down every argument reaching the function.

## Step 3 — Check hashability

```python
hash(argument)
```

## Step 4 — Check equality

Are two intended-equivalent values actually equal?

## Step 5 — Check keyword call styles

Compare:

```python
f(a=1, b=2)
```

and:

```python
f(b=2, a=1)
```

## Step 6 — Inspect metrics

```python
f.cache_info()
```

## Step 7 — Check lifecycle

Was the cache supposed to be cleared?

## Step 8 — Check hidden state

Does output depend on:

- time,
- database state,
- file contents,
- environment,
- permissions,
- model version?

## Step 9 — Check memory

Is the cache retaining large objects?

## Step 10 — Check concurrency assumptions

Could multiple concurrent misses be expected?

This workflow is much more effective than randomly changing `maxsize`.

# 45. Debugging `partial`

When a partial callable behaves unexpectedly, inspect:

```python
operation.func
operation.args
operation.keywords
```

Example:

```python
from functools import partial

def connect(host, port, timeout):
    return host, port, timeout

connect_local = partial(
    connect,
    host="localhost",
    port=5432,
)

print(connect_local.func)
print(connect_local.args)
print(connect_local.keywords)
```

Then manually expand:

```python
connect_local(timeout=5)
```

to:

```python
connect(
    host="localhost",
    port=5432,
    timeout=5,
)
```

### If behavior is still confusing

Compare it with an explicit wrapper:

```python
def connect_local(timeout):
    return connect(
        host="localhost",
        port=5432,
        timeout=timeout,
    )
```

If the wrapper is clearer, use the wrapper.

# 46. Performance Measurement with `timeit`

Use `timeit` for focused experiments.

```python
from functools import cache
from timeit import timeit

def expensive(x):
    total = 0
    for i in range(100_000):
        total += (i * x) % 97
    return total

@cache
def cached_expensive(x):
    total = 0
    for i in range(100_000):
        total += (i * x) % 97
    return total

cached_expensive.cache_clear()

uncached_time = timeit(
    "expensive(10)",
    globals=globals(),
    number=10,
)

first_time = timeit(
    "cached_expensive(10)",
    globals=globals(),
    number=1,
)

warm_time = timeit(
    "cached_expensive(10)",
    globals=globals(),
    number=10,
)

print(uncached_time, first_time, warm_time)
```

This separates:

- uncached computation;
- first cached call;
- warm cached calls.

### Do not invent benchmark conclusions

A benchmark result belongs to:

```text
specific code
+
specific hardware
+
specific Python version
+
specific workload
```

Measure before making performance claims.

# 47. Cold Cache vs Warm Cache

Caching produces different runtime behavior depending on cache state.

### Cold

```text
cache empty
→ miss
→ compute
```

### Warm

```text
entry present
→ hit
→ reuse
```

A benchmark that measures only warm calls answers:

> "How fast is a cache hit?"

It does not answer:

> "How fast is the application end-to-end?"

Production workloads usually contain a mixture of:

- misses;
- hits;
- evictions;
- invalidations;
- cold starts.

# 48. Cache Benchmarking Pitfalls

Avoid these mistakes:

### Only one key

A workload of:

```text
A A A A A A
```

can overstate the benefit.

### Only unique keys

```text
A B C D E F ...
```

can understate a cache that is designed for a hot working set.

### Ignoring memory

A speed improvement that causes unacceptable memory use may be a bad trade.

### Ignoring correctness

A stale answer is not a successful optimization.

### Ignoring startup

Process-local caches are initially empty after a restart.

### Ignoring deployment changes

A new model/configuration version can change the meaning of old results.

Use representative workload distributions.

# 49. Cache and `self`

Caching methods has a special lifetime issue.

```python
from functools import lru_cache

class Calculator:
    @lru_cache(maxsize=128)
    def square(self, x):
        return x * x
```

The effective cache key includes the instance and the explicit arguments.

Python's documentation explains that cached methods include `self` in the cache and can therefore keep instances alive until entries are evicted or the cache is cleared. citeturn147567search0turn147567search4

This matters when instances are:

- short-lived;
- numerous;
- large;
- expected to be garbage-collected.

A standalone pure function can sometimes provide a clearer caching boundary:

```python
@lru_cache(maxsize=128)
def square_for_configuration(configuration_id, x):
    return x * x
```

Choose based on ownership and lifecycle, not only code brevity.

# 50. Concurrent Cache Misses

`lru_cache` is threadsafe at the cache-structure level, but the underlying function may be invoked more than once when multiple threads encounter the same missing key before the first computation finishes. Python explicitly documents this possibility. citeturn147567search2turn147567search4

Conceptual scenario:

```text
Thread A → lookup K → MISS → compute
Thread B → lookup K → MISS → compute
```

The cache remains coherent, but both computations may happen.

### Do not infer an exactly-once guarantee

`lru_cache` is not:

- a distributed lock;
- a single-flight executor;
- a task queue;
- an idempotency layer.

When exactly-once execution matters, use an explicit coordination design.

# 51. Process Boundaries

With multiple processes:

```text
worker A → cache A
worker B → cache B
worker C → cache C
```

Each process owns its own in-memory cache.

A hit in worker A does not populate worker B.

This matters in:

- web servers;
- containers;
- inference replicas;
- multiprocessing;
- horizontally scaled services.

### Consequence

If a result must be globally shared, use a shared data system rather than assuming `functools` will coordinate processes.

# 52. Process Restart

A local cache disappears when the process exits.

```text
process 1
  cache contains:
    A → result
    B → result

restart

process 2
  cache:
    empty
```

This may be exactly what you want for:

- temporary computation reuse;
- worker-local hot data;
- safe ephemeral state.

It is not enough for data that must survive failure.

If results must be durable:

```text
cache
+
persistent store
```

or a different architecture may be appropriate.

# 53. Production Boundary: Memory vs Durability

An in-memory memoization cache is not the source of truth unless the application explicitly treats it that way.

A common architecture is:

```text
database / object store / model registry
            ↓
        process cache
            ↓
        fast repeated reads
```

The cache is an acceleration layer.

When the process dies:

```text
cached acceleration disappears
```

but:

```text
source of truth remains
```

This is a healthy separation for many systems.

# 54. Cache and Security Context

Authorization-sensitive functions need careful keys.

Suppose:

```python
def get_document(document_id, user_id):
    ...
```

If the result depends on both:

```text
document_id
+
user_id
```

then a cache keyed only by `document_id` does not represent the full result semantics.

Likewise, multi-tenant systems may require:

```text
tenant_id
+
document_id
```

and possibly other access context.

The defensive principle is:

> **A cached result may only be reused when the caller's relevant security context matches the context under which the result was produced.**

Do not treat cache keys as performance-only details. They can be security boundaries.

# 55. Model Versioning and AI Cache Keys

A model-dependent result may be a function of:

```text
model_id
model_version
preprocessing_version
input
```

Example conceptual key:

```python
key = (
    "embedding-model",
    "v3",
    "prep-v5",
    text,
)
```

If the model changes:

```text
v3 → v4
```

the new key naturally points to a different result namespace.

Similarly:

```text
prompt-template v2
→ prompt-template v3
```

may need separation.

### Why this helps

Versioned keys make semantic changes explicit.

The cache does not need to know *why* the model changed; the key expresses that the computation's meaning changed.

# 56. Applied AI — Deterministic Preprocessing

Suppose an ingestion pipeline repeatedly performs:

```text
raw text
→ normalization
→ segmentation
→ metadata extraction
```

If these steps are deterministic and expensive, memoization can reduce repeated work.

Example:

```python
from functools import lru_cache

@lru_cache(maxsize=1024)
def normalize_for_indexing(text):
    return " ".join(text.lower().split())
```

The cache key is the text.

If the normalization algorithm changes, the key may need a version:

```python
@lru_cache(maxsize=1024)
def normalize_for_indexing(version, text):
    ...
```

This illustrates a general AI engineering pattern:

```text
stable transformation
→ explicit semantic key
→ bounded local cache
```

# 57. Applied AI — Embeddings

Embeddings are a classic candidate for caching because repeated text can be expensive to process.

But a robust conceptual key may require:

```text
provider
+
model
+
model version
+
preprocessing version
+
input
```

Example:

```python
from functools import lru_cache

@lru_cache(maxsize=2048)
def embedding_key(
    provider,
    model_version,
    preprocessing_version,
    text,
):
    return (
        provider,
        model_version,
        preprocessing_version,
        text,
    )
```

This function merely constructs a key in the example; a real embedding cache would need a separate design.

### Important point

Do not make:

```text
text
```

the only key dimension if the result can differ under another model or preprocessing configuration.

# 58. Applied AI — RAG

A RAG pipeline has multiple stages with different cache suitability.

| Stage | Potential cache candidate | Main question |
|---|---|---|
| parsing | yes | deterministic? |
| chunking | yes | versioned rules? |
| embedding | often | model/version stable? |
| retrieval | sometimes | index freshness? |
| generation | sometimes | same context/model/semantics? |

Do not cache the entire pipeline by default.

Instead identify stable reusable subcomputations.

### Example

```text
document
   ↓
deterministic parsing
   ↓
cache candidate
   ↓
embedding
   ↓
cache candidate with model/version
   ↓
retrieval
   ↓
freshness-aware decision
   ↓
generation
```

Caching should follow semantic boundaries.

# 59. Applied AI — Agent Systems

Agent architectures can contain:

- deterministic parsing;
- tool metadata lookup;
- configuration lookup;
- current state;
- external reads;
- side-effecting actions.

Potentially cacheable:

```text
static tool schema
stable model metadata
deterministic text transformation
```

Potentially unsafe without additional policy:

```text
current balance
current inventory
authorization-sensitive resource
send email
create ticket
execute purchase
```

### Agent mental model

Classify each callable:

```text
pure-ish computation
read-only external state
side-effecting command
```

Caching is easiest for the first category.

The other categories require explicit freshness, authorization, idempotency, or execution semantics.

# 60. Applied AI — Evaluation

Evaluation systems often repeat expensive deterministic preprocessing.

For example:

```python
from functools import lru_cache

@lru_cache(maxsize=5000)
def normalize_model_output(raw_output):
    return raw_output.strip().lower()
```

Potential benefits include:

- repeated benchmark records;
- repeated parsing;
- large evaluation suites with repeated outputs.

But if the evaluator's normalization rules change, old cached results may be semantically invalid.

A versioned key can make that dependency visible:

```python
@lru_cache(maxsize=5000)
def normalize_model_output(parser_version, raw_output):
    ...
```

Reproducibility matters as much as speed in evaluation systems.



# 61. `partial` Fundamentals

Now switch from reusing **results** to reusing **configuration**.

Suppose:

```python
def multiply(a, b):
    return a * b
```

If the application repeatedly wants:

```python
multiply(2, value)
```

you could create a wrapper:

```python
def double(value):
    return multiply(2, value)
```

Or use:

```python
from functools import partial

double = partial(multiply, 2)
```

Then:

```python
print(double(5))
print(double(8))
```

Expected:

```text
10
16
```

### Mental model

```text
existing callable
      ↓
pre-fill some arguments
      ↓
new callable
      ↓
supply remaining arguments later
```

`partial` is therefore a callable-adaptation tool.

# 62. `partial()` Syntax

The core signature is:

```text
partial(func, /, *args, **keywords)
```

Example:

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, 2)

print(square(5))
```

Conceptually:

```python
power(2, 5)
```

### Keyword example

```python
def connect(host, port, timeout):
    return host, port, timeout

connect_local = partial(
    connect,
    host="localhost",
    port=5432,
)

print(connect_local(timeout=5))
```

Conceptually:

```python
connect(
    host="localhost",
    port=5432,
    timeout=5,
)
```

The value of `partial` is not magic. It simply removes repeated argument specification.

# 63. Positional Arguments with `partial`

Example:

```python
from functools import partial

def multiply(a, b, c):
    return a * b * c

times_two = partial(multiply, 2)

print(times_two(3, 4))
```

Conceptually:

```python
multiply(2, 3, 4)
```

Multiple fixed arguments work too:

```python
special = partial(
    multiply,
    2,
    3,
)

print(special(4))
```

The remaining argument is:

```text
c
```

### When positional pre-filling is clear

Use it when:

- the function has few parameters;
- parameter positions are obvious;
- the fixed values are stable.

When there are many parameters, keywords often communicate intent better.

# 64. Keyword Arguments with `partial`

Suppose:

```python
def format_value(value, *, prefix, suffix):
    return f"{prefix}{value}{suffix}"
```

Create:

```python
from functools import partial

format_id = partial(
    format_value,
    prefix="ID-",
    suffix="",
)

print(format_id(42))
```

Expected:

```text
ID-42
```

Keywords can make configuration explicit.

This is especially useful for:

- backend settings;
- parser modes;
- model identifiers;
- regions;
- feature flags;
- retry options.

# 65. Partial Keyword Overrides

Pre-filled keyword arguments can be extended or overridden by later keyword arguments.

```python
from functools import partial

def request(url, *, timeout):
    return url, timeout

fast_request = partial(
    request,
    timeout=2,
)

print(fast_request("https://example.test"))
print(fast_request("https://example.test", timeout=5))
```

The second call can override the pre-filled keyword.

Python documents this extend-and-override behavior for `partial`. citeturn147567search1turn147567search4

### Positional conflicts are different

```python
def greet(name, greeting):
    return f"{greeting}, {name}"

hello_alice = partial(greet, "Alice")

# hello_alice(name="Bob", greeting="Hello")
```

`name` has already been filled positionally. Providing it again by keyword creates the usual Python multiple-values conflict.

# 66. Python 3.14 `Placeholder`

Python 3.14 adds:

```python
from functools import Placeholder
```

as a sentinel for reserving a positional slot in `partial` and `partialmethod`. citeturn147567search2turn147567search4

Example:

```python
from functools import Placeholder, partial

_ = Placeholder

def divide(a, b):
    return a / b

divide_by_two = partial(
    divide,
    _,
    2,
)

print(divide_by_two(10))
```

The conceptual mapping is:

```text
a → supplied later
b → fixed as 2
```

Without `Placeholder`, ordinary `partial` naturally fixes leading positional arguments.

### Version compatibility

This example requires Python 3.14+.

For older supported runtimes, a named wrapper is often clearer:

```python
def divide_by_two(value):
    return divide(value, 2)
```

Do not make a deployment depend on a new feature without checking the production interpreter version.

# 67. `partial` Object Attributes

A partial object exposes useful attributes:

```python
from functools import partial

def multiply(a, b):
    return a * b

double = partial(multiply, 2)

print(double.func)
print(double.args)
print(double.keywords)
```

Conceptually:

```text
.func
→ original callable

.args
→ fixed positional arguments

.keywords
→ fixed keyword arguments
```

Example:

```python
assert double.func is multiply
assert double.args == (2,)
assert double.keywords == {}
```

These attributes are useful for debugging and introspection.

Do not build business logic around deep assumptions about the internal implementation of partial objects.

# 68. Partial Is Callable

A partial is a callable object.

```python
from functools import partial

def multiply(a, b):
    return a * b

double = partial(multiply, 2)

print(callable(double))
```

Expected:

```text
True
```

That means a generic API can accept it:

```python
def run(callback, value):
    return callback(value)

print(run(double, 6))
```

Expected:

```text
12
```

This is where higher-order functions become practical.

# 69. `partial` vs Lambda

These can express similar behavior.

```python
from functools import partial

double_partial = partial(multiply, 2)
```

versus:

```python
double_lambda = lambda x: multiply(2, x)
```

### Prefer `partial` when

The meaning is literally:

```text
take this function
+
fix this argument
```

### Prefer a lambda when

You need a small transformation that is not merely argument pre-filling.

Example:

```python
to_label = lambda item: f"ID:{item['id']}"
```

### Production point

The shortest expression is not automatically the clearest expression.

Use the construct that tells another engineer what the code means.

# 70. `partial` vs Wrapper Function

A wrapper is:

```python
def production_processor(document):
    return process_document(
        document,
        mode="production",
        strict=True,
    )
```

A partial is:

```python
production_processor = partial(
    process_document,
    mode="production",
    strict=True,
)
```

Partial is attractive because it directly communicates:

```text
same function
+
fixed configuration
```

A wrapper is better when you need additional behavior:

```python
def production_processor(document):
    validate_document(document)

    result = process_document(
        document,
        mode="production",
        strict=True,
    )

    record_metric("processed")
    return result
```

### Decision

```text
only fix arguments → partial
add business logic → wrapper
```

# 71. `partialmethod`

`partialmethod` is the class-oriented form.

```python
from functools import partialmethod

class Greeter:
    def greet(self, greeting, name):
        return f"{greeting}, {name}"

    say_hello = partialmethod(greet, "Hello")
```

Then:

```python
greeter = Greeter()
print(greeter.say_hello("Alice"))
```

Expected:

```text
Hello, Alice
```

Python documents `partialmethod` as a descriptor designed for method definitions rather than direct invocation. citeturn147567search2turn147567search5

# 72. Why `partialmethod` Exists

Ordinary instance methods participate in method binding.

Conceptually:

```text
obj.method(...)
```

causes `self` to be associated with the underlying function.

`partialmethod` is designed to combine that method behavior with fixed arguments.

Example:

```python
class Cell:
    def set_state(self, state):
        self.state = state

    set_alive = partialmethod(set_state, True)
    set_dead = partialmethod(set_state, False)
```

Then:

```python
cell = Cell()

cell.set_alive()
print(cell.state)

cell.set_dead()
print(cell.state)
```

Expected:

```text
True
False
```

Mental model:

```text
self
+
fixed state argument
+
future call arguments
```

# 73. `partial` vs `partialmethod`

| Tool | Meaning |
|---|---|
| `partial` | general partially configured callable |
| `partialmethod` | partially configured method definition |

Use:

```python
process_prod = partial(process, mode="production")
```

outside class method definitions.

Use:

```python
run_prod = partialmethod(run, mode="production")
```

inside a class when method binding matters.

### Maintainability warning

Five clearly named specialized methods can be useful.

Fifty partial methods can make a class API difficult to understand.

Use the abstraction selectively.

# 74. `partial` with Callbacks

Many frameworks need a callable with a known shape.

Suppose:

```python
def process_record(record, *, mode, strict):
    return {
        "record": record,
        "mode": mode,
        "strict": strict,
    }
```

Create:

```python
from functools import partial

production_processor = partial(
    process_record,
    mode="production",
    strict=True,
)
```

Now:

```python
for record in ["a", "b"]:
    print(production_processor(record))
```

The callback consumer only needs:

```text
record → result
```

This pattern appears in:

- event callbacks;
- job functions;
- data transforms;
- task runners;
- test helpers;
- plugin interfaces.

# 75. `partial` in Data Processing

A transformation can be specialized:

```python
def transform_row(row, *, mode, normalize):
    if normalize:
        row = row.strip()
    return f"{mode}:{row}"
```

Create:

```python
from functools import partial

production_transform = partial(
    transform_row,
    mode="production",
    normalize=True,
)
```

Then:

```python
rows = [" a ", " b "]

processed = [
    production_transform(row)
    for row in rows
]

print(processed)
```

Expected:

```text
['production:a', 'production:b']
```

The configuration is fixed once.

The row changes each call.

# 76. `partial` in Applied AI Engineering

Consider a generic embedding function:

```python
def embed_text(
    text,
    *,
    provider,
    model,
    normalize,
):
    ...
```

A deployment can create:

```python
from functools import partial

production_embed = partial(
    embed_text,
    provider="provider-a",
    model="embedding-v3",
    normalize=True,
)
```

The rest of the pipeline can use:

```text
text → embedding
```

without repeatedly specifying deployment configuration.

This can be useful for:

- embedding pipelines;
- inference adapters;
- preprocessing;
- model provider configuration;
- region-specific services;
- evaluation transforms.

But a partial is not a replacement for dependency injection, lifecycle management, configuration validation, or resource management.

# 77. Partial for Model Inference Configuration

A generic inference function might be:

```python
def infer(
    prompt,
    *,
    model,
    temperature,
    retry_limit,
):
    ...
```

A service may define:

```python
production_infer = partial(
    infer,
    model="model-v3",
    temperature=0.1,
    retry_limit=3,
)
```

This is useful when the application intentionally wants one stable callable.

For complex inference configuration, consider a dedicated configuration object:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class InferenceConfig:
    model: str
    temperature: float
    retry_limit: int
```

The rule is:

```text
lightweight adaptation
→ partial

domain configuration
→ configuration object
```

# 78. Configuration Objects vs `partial`

A partial is concise:

```python
production_processor = partial(
    process,
    mode="production",
    strict=True,
)
```

A configuration object is more explicit:

```python
config = ProcessingConfig(
    mode="production",
    strict=True,
)
```

Configuration objects are often better when settings need:

- validation;
- serialization;
- logging;
- documentation;
- equality semantics;
- lifecycle;
- dependency injection.

Do not force a simple case into a class.

Do not force a complex configuration domain into a chain of partials.

# 79. Related Utility: `wraps`

A brief connection to decorators:

```python
from functools import wraps

def log_calls(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print("calling", function.__name__)
        return function(*args, **kwargs)

    return wrapper
```

`wraps` helps preserve metadata from the original function.

Relevant metadata includes:

- `__name__`;
- `__doc__`;
- `__wrapped__`.

This matters for:

- debugging;
- introspection;
- testing;
- tooling.

The decorator itself is not the focus here. The relationship is simply:

```text
functools
→ function adaptation + callable metadata utilities
```

# 80. Related Utility: `update_wrapper`

The explicit metadata helper is:

```python
from functools import update_wrapper
```

Example:

```python
def original():
    """Original documentation."""
    return 42

def wrapper():
    return original()

update_wrapper(wrapper, original)

print(wrapper.__name__)
print(wrapper.__doc__)
print(wrapper.__wrapped__ is original)
```

Use `wraps` inside common decorator definitions.

Use `update_wrapper` when explicit wrapper metadata control is needed.

This supporting concept becomes useful when inspecting decorator stacks around cached functions.

# 81. Related Utility: `reduce`

`reduce` folds an iterable into one result.

```python
from functools import reduce

values = [1, 2, 3, 4]

result = reduce(
    lambda left, right: left + right,
    values,
)

print(result)
```

Expected:

```text
10
```

Conceptually:

```text
(((1 + 2) + 3) + 4)
```

An initializer can be supplied:

```python
result = reduce(
    lambda left, right: left + right,
    values,
    100,
)
```

Expected:

```text
110
```

Often a built-in is clearer:

```python
sum(values)
```

The important lesson is not to use `reduce` simply because it exists.

# 82. Related Utility: `singledispatch`

`singledispatch` creates a generic function whose implementation can depend on the first argument's type.

```python
from functools import singledispatch

@singledispatch
def describe(value):
    return f"generic: {value!r}"

@describe.register
def _(value: int):
    return f"integer: {value}"

print(describe(10))
print(describe("hello"))
```

The integer call uses the registered implementation.

The string call uses the generic implementation.

This is an advanced related tool, not a central chapter topic.

Use it when type-based extensibility improves the design, not merely because it is sophisticated.

# 83. `functools` API Decision Table

| Problem | Tool |
|---|---|
| Simple unbounded memoization | `cache` |
| Bounded memoization | `lru_cache` |
| Inspect cache statistics | `cache_info()` |
| Inspect LRU configuration | `cache_parameters()` |
| Clear cached results | `cache_clear()` |
| Preserve wrapper metadata | `wraps` |
| Explicit metadata copying | `update_wrapper` |
| Pre-fill callable arguments | `partial` |
| Pre-fill method arguments | `partialmethod` |
| Fold iterable into one value | `reduce` |
| First-argument type dispatch | `singledispatch` |

Do not use every tool in one project.

The abstraction should match the problem.

# 84. Production Example — AI Document Processing Optimization Layer

We now combine:

```text
lru_cache
+
cache metrics
+
cache invalidation
+
partial
```

## Problem

An AI document service repeatedly performs deterministic processing:

```text
document
  ↓
normalize
  ↓
extract metadata
  ↓
calculate statistics
```

The same document version may be processed repeatedly.

## Requirements

- avoid repeated deterministic work;
- bound local cache size;
- expose cache metrics;
- allow explicit invalidation;
- create a specialized production callable;
- make the key explicit;
- test cache behavior.

# 85. Production Example — Implementation

```python
from functools import lru_cache, partial
from typing import NamedTuple


class ProcessingResult(NamedTuple):
    document_id: str
    document_version: str
    normalized_text: str
    word_count: int


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


@lru_cache(maxsize=256)
def preprocess_document(
    document_id: str,
    document_version: str,
    preprocessing_version: str,
    text: str,
) -> ProcessingResult:
    normalized = normalize_text(text)

    return ProcessingResult(
        document_id=document_id,
        document_version=document_version,
        normalized_text=normalized,
        word_count=len(normalized.split()),
    )


def process_document(
    document_id: str,
    document_version: str,
    text: str,
    *,
    preprocessing_version: str,
    strict: bool,
) -> ProcessingResult:
    if strict and not text.strip():
        raise ValueError("document text is empty")

    return preprocess_document(
        document_id,
        document_version,
        preprocessing_version,
        text,
    )


production_processor = partial(
    process_document,
    preprocessing_version="prep-v3",
    strict=True,
)
```

### Why this structure?

`preprocess_document` is the cached deterministic boundary.

The key includes:

```text
document_id
document_version
preprocessing_version
text
```

The production partial fixes:

```text
preprocessing_version
strictness
```

while leaving the request-specific document data to the caller.

# 86. Production Example — Event Flow

First call:

```python
result = production_processor(
    "doc-100",
    "version-7",
    " Hello   World ",
)
```

Conceptually:

```text
request
→ cache lookup
→ MISS
→ normalization
→ result
→ store result
```

Repeated call:

```python
same_result = production_processor(
    "doc-100",
    "version-7",
    " Hello   World ",
)
```

Conceptually:

```text
request
→ cache lookup
→ HIT
→ return stored result
```

Different version:

```python
new_result = production_processor(
    "doc-100",
    "version-8",
    " Hello   World ",
)
```

This produces a different cache-key state because the document version changed.

# 87. Production Example — Why the Key Is Explicit

Suppose the cache key used only:

```text
document_id
```

Then:

```text
version-7
version-8
```

could collide.

That would be incorrect if the content changed.

Likewise, if preprocessing changes:

```text
prep-v3
prep-v4
```

the results may differ.

Versioned keys make the semantic dependency explicit:

```text
(document identity,
 document version,
 preprocessing version,
 content)
```

### A possible optimization

If `document_version` is guaranteed to uniquely identify content, storing both version and full text in the cache key might be unnecessary.

But removing text is safe only if that contract is real.

Optimization should follow correctness, not precede it.

# 88. Production Example — Metrics

After several calls:

```python
info = preprocess_document.cache_info()

print("hits:", info.hits)
print("misses:", info.misses)
print("currsize:", info.currsize)
print("maxsize:", info.maxsize)
print("parameters:", preprocess_document.cache_parameters())
```

This allows an engineer to ask:

```text
Is the local cache producing reuse?
Is the capacity reasonable?
Is the working set larger than expected?
```

Do not infer production-wide hit rates from one local process.

# 89. Production Example — Invalidation

Suppose preprocessing rules change:

```text
prep-v3 → prep-v4
```

The versioned key lets the new configuration use different entries.

A broad emergency reset is also available:

```python
preprocess_document.cache_clear()
```

The application should document why and when this happens.

### Why clearing is not enough

If there are many replicas:

```text
worker A → cleared
worker B → old cache
worker C → old cache
```

A process-local clear does not automatically coordinate those workers.

This is why distributed invalidation is a separate architecture problem.

# 90. Production Example — Testing

```python
def test_repeated_document_reuses_cache():
    preprocess_document.cache_clear()

    first = production_processor(
        "doc-100",
        "version-7",
        "Hello   World",
    )

    second = production_processor(
        "doc-100",
        "version-7",
        "Hello   World",
    )

    assert first == second

    info = preprocess_document.cache_info()

    assert info.misses == 1
    assert info.hits == 1
```

Different version:

```python
def test_document_version_changes_key():
    preprocess_document.cache_clear()

    first = production_processor(
        "doc-100",
        "version-7",
        "Hello",
    )

    second = production_processor(
        "doc-100",
        "version-8",
        "Hello",
    )

    assert first == second

    info = preprocess_document.cache_info()
    assert info.misses == 2
```

The result values can happen to be equal while cache entries remain distinct.

That distinction is important:

```text
equal result
≠
same cache key
```

# 91. Production Example — Mutable Results

The example returns a `NamedTuple`, which is immutable.

That is intentional.

A mutable result such as:

```python
def example():
    return {
        "tokens": [...],
    }
```

could be changed by callers and thereby alter future calls that reuse the cached object.

Immutable result representations can reduce that class of bug.

If a mutable result is required by an API, consider:

- returning a fresh copy;
- caching an immutable internal form;
- defining explicit ownership rules.

# 92. Production Example — Limitations

This example is **not** a complete production cache platform.

It does not include:

- distributed sharing;
- TTL;
- persistent cache;
- distributed invalidation;
- memory-budget enforcement in bytes;
- rate limiting;
- cross-worker coordination;
- exactly-once computation;
- observability beyond local cache metrics.

Its purpose is to show where standard-library memoization and partial application fit inside a larger system.

# 93. Applied AI — LLM Metadata

Stable model metadata can be a reasonable local cache candidate:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_model_metadata(model_id, model_version):
    return {
        "model_id": model_id,
        "model_version": model_version,
        "supports_tool_use": True,
    }
```

The key contains:

```text
model_id
+
model_version
```

because metadata can change across versions.

This is easier to reason about than caching a generic user-specific LLM response.

# 94. Applied AI — Tool Results

Classify tools before caching them.

### Deterministic read

```text
input → stable value
```

Potential cache candidate.

### Dynamic read

```text
input → current external state
```

Needs a freshness policy.

### Side-effecting command

```text
input → external change
```

Do not substitute result memoization for idempotency.

Examples:

```text
read schema
→ potentially cache

get current inventory
→ freshness required

create ticket
→ explicit command semantics
```

# 95. Applied AI — RAG Cache Layers

A useful mental model:

```text
document parsing
    → often deterministic

chunking
    → often deterministic but version-sensitive

embedding
    → model/version-sensitive

retrieval
    → index/freshness-sensitive

generation
    → model/context/tool/state-sensitive
```

The correct question is:

> Which stage has a stable reusable result?

Do not cache an entire RAG pipeline just because some substeps are deterministic.

# 96. Applied AI — Agent Tool Cache

A read-only tool can sometimes be cached:

```python
@lru_cache(maxsize=128)
def get_static_tool_schema(tool_id, version):
    ...
```

But:

```python
def create_ticket(data):
    ...
```

is a command.

Caching the command's result can suppress repeated execution.

Likewise:

```python
def get_current_account_balance(user_id):
    ...
```

may need current external state and authorization.

Agent caching must therefore be designed around semantics, not just token/latency cost.

# 97. Applied AI — Backend and Data Engineering

Useful local memoization targets include:

- repeated schema parsing;
- deterministic transformation;
- configuration lookup;
- stable model metadata;
- expensive serialization preparation;
- repeated evaluation transformations.

Useful partial-application targets include:

- fixed provider;
- fixed model;
- fixed preprocessing configuration;
- fixed deployment mode;
- fixed retry parameters.

This makes `functools` a small but useful building block across the engineering stack.

# 98. Security and Correctness Checklist

For any cached AI/backend function, ask:

```text
[ ] Does the result depend on user identity?
[ ] Does the result depend on tenant identity?
[ ] Does authorization scope matter?
[ ] Does model version matter?
[ ] Does prompt/template version matter?
[ ] Does preprocessing version matter?
[ ] Does external state matter?
[ ] Is stale data acceptable?
[ ] Can the result be safely shared?
[ ] Can the returned object be mutated?
```

If the answer reveals a dependency that is not represented in the cache contract, stop and redesign before optimizing.

# 99. Production Anti-Patterns

## Anti-pattern 1 — Cache every expensive function

Why wrong:

```text
expensive
≠
safe to reuse
```

## Anti-pattern 2 — Use `@cache` for arbitrary user input

Why risky:

```text
unbounded key growth
```

## Anti-pattern 3 — Cache commands

Why risky:

```text
cache hit
→ side effect skipped
```

## Anti-pattern 4 — Cache without a version

Why risky:

```text
model/config changed
→ old semantics remain reachable
```

## Anti-pattern 5 — Ignore tenant/authorization context

Why risky:

```text
same resource ID
≠
same permitted result
```

## Anti-pattern 6 — Assume `maxsize` is a memory budget

Why wrong:

```text
maxsize = entries
```

not bytes.

# 100. API Coverage Reference — `cache`

`cache`:

```python
@cache
def f(x):
    ...
```

Relevant behavior:

- unbounded memoization;
- hashable arguments;
- cached return values;
- process-local lifetime;
- `cache_clear()`;
- underlying callable via `__wrapped__`.

Python added `cache` in version 3.9. citeturn147567search1

Use it when its unbounded semantics are intentional.

# 101. API Coverage Reference — `lru_cache`

Main forms:

```python
@lru_cache
def f(x):
    ...
```

and:

```python
@lru_cache(maxsize=128, typed=False)
def f(x):
    ...
```

Relevant capabilities:

```python
f.cache_info()
f.cache_clear()
f.cache_parameters()
f.__wrapped__
```

Python documents bounded LRU behavior, cache statistics, configuration inspection, and clearing. citeturn147567search2turn147567search4

# 102. API Coverage Reference — `partial`

Main form:

```text
partial(func, /, *args, **keywords)
```

Relevant attributes:

```python
partial_object.func
partial_object.args
partial_object.keywords
```

Later keyword arguments can extend and override stored keyword arguments. citeturn147567search1turn147567search4

# 103. API Coverage Reference — `partialmethod`

Main form:

```text
partialmethod(func, /, *args, **keywords)
```

Use inside classes to define methods with pre-filled arguments.

It participates in descriptor-based method binding. citeturn147567search2turn147567search5

# 104. API Coverage Reference — Related Utilities

```python
from functools import wraps
from functools import update_wrapper
from functools import reduce
from functools import singledispatch
```

These are related callable utilities.

They should not be included in designs merely because they are available.

The central tools in this chapter remain:

```text
cache
lru_cache
partial
partialmethod
```



# 105. Progressive Exercises

Work through these in order. Do not immediately look for a complete solution.

## Level 1 — Manual Memoization

Implement:

```python
def square(x):
    ...
```

with a dictionary.

Requirements:

- compute a value on a miss;
- reuse it on a hit;
- make hit/miss behavior observable.

Hint:

```python
cache = {}
```

## Level 2 — `@cache`

Replace the manual dictionary with:

```python
from functools import cache
```

and `@cache`.

Requirements:

- preserve the function's behavior;
- identify the cache lifetime.

## Level 3 — Hashability

Test a cached function with:

```text
int
str
tuple
list
dict
set
```

Goal:

- identify which values can participate directly in the cache key;
- explain why.

Hint:

```python
hash(value)
```

## Level 4 — Fibonacci Memoization

Implement Fibonacci twice:

1. naive recursive version;
2. memoized version.

Record the conceptual difference in repeated work.

## Level 5 — `lru_cache`

Use:

```text
@lru_cache(maxsize=3)
```

and call a sequence of unique and repeated values.

Inspect:

```python
function.cache_info()
```

## Level 6 — LRU Reasoning

Given:

```text
maxsize = 3

A
B
C
A
D
```

Predict which entry is evicted.

Then verify experimentally.

## Level 7 — Cache Clearing

Write a test that:

1. produces a cache hit;
2. calls `cache_clear()`;
3. verifies that a subsequent call becomes a miss.

## Level 8 — Keyword Cache Keys

Experiment with:

```python
f(a=1, b=2)
f(b=2, a=1)
```

Inspect cache metrics and explain what you observe.

## Level 9 — `typed=True`

Build a function that behaves differently for:

```text
int
float
```

and compare:

```python
typed=False
```

with:

```python
typed=True
```

Do not merely memorize the output. Explain the cache-key semantics.

# 106. Progressive Exercises — Partial Application

## Level 10 — `partial`

Create:

```text
double
triple
```

from:

```python
def multiply(a, b):
    ...
```

using `partial`.

## Level 11 — Keyword Partial

Given:

```python
def connect(host, port, timeout):
    ...
```

create:

```text
connect_local
```

with fixed host and port.

## Level 12 — Override

Create a partial with a default timeout, then override the timeout at call time.

Explain why the keyword override works.

## Level 13 — Partial Inspection

Inspect:

```python
partial_object.func
partial_object.args
partial_object.keywords
```

Explain what each represents.

## Level 14 — `partial` vs Lambda

Implement the same behavior with:

```text
partial
lambda
```

Compare readability.

## Level 15 — `partial` vs Wrapper

Write a wrapper that validates input before calling the underlying function.

Explain why the wrapper is now more expressive than a plain partial.

## Level 16 — `partialmethod`

Create:

```text
start()
stop()
```

specialized from one underlying method using `partialmethod`.

# 107. Progressive Exercises — Production Reasoning

## Level 17 — Cache Key Design

Design a cache key for:

```text
document embedding
```

where output depends on:

- provider;
- model;
- model version;
- preprocessing version;
- text.

Explain why each field exists.

## Level 18 — Stale Data

Design a cache around:

```text
feature flags
```

Then define an invalidation strategy.

## Level 19 — Multi-Tenant Data

Design a cache key for:

```text
get_document(document_id, tenant_id)
```

and explain why:

```text
document_id
```

alone may be insufficient.

## Level 20 — Model Upgrade

A model changes from:

```text
v3 → v4
```

Design a key/invalidation strategy that prevents old results from silently being reused under v4 semantics.

## Level 21 — Memory

A cache retains 5,000 objects, each potentially large.

Explain why:

```python
maxsize=5000
```

is not a memory limit.

## Level 22 — Benchmark

Design a benchmark with:

```text
cold cache
warm cache
repeated keys
unique keys
```

Use `timeit`.

Explain which results would be meaningful to production.

# 108. Applied AI Mini-Exercises

## Exercise A — Embedding Cache

Implement a deterministic toy embedding function:

```python
def embedding(text, model_version):
    ...
```

Use `lru_cache`.

Requirements:

- model version must be part of the semantic key;
- repeated same-version calls should reuse results;
- changed model version should create a distinct cache entry.

## Exercise B — Agent Metadata

Cache a stable tool-schema lookup.

Then list reasons why caching:

```text
create_ticket(...)
```

would be a different problem.

## Exercise C — RAG Preprocessing

Cache:

```text
normalize
→ chunk
```

but include a preprocessing version.

Explain what should happen after the preprocessing algorithm changes.

# 109. Knowledge Checks

Answer these in your own words:

1. What problem does `functools` solve?
2. What is memoization?
3. What is a cache hit?
4. What is a cache miss?
5. Why can repeated deterministic work be cached?
6. What does `@cache` do?
7. Why is `@cache` unbounded?
8. Why must cached arguments be hashable?
9. How are cache keys related to dictionary keys?
10. Why can a cached mutable return value be dangerous?
11. What does `cache_clear()` do?
12. What does LRU stand for?
13. What does `maxsize` control?
14. What does `cache_info()` show?
15. What does `cache_parameters()` show?
16. What does `typed=True` change?
17. Why can different keyword call patterns matter?
18. Why can caching an instance method retain the instance?
19. Why is process-local caching not distributed caching?
20. What is invalidation?
21. Why is LRU eviction not the same as freshness?
22. What is `partial`?
23. What is `partialmethod`?
24. How is partial application different from caching?
25. When is a wrapper function better than a partial?
26. When is a configuration object better?
27. What does `__wrapped__` mean?
28. Why can model version belong in an AI cache key?
29. Why can tenant context belong in an AI cache key?
30. What is the first question to ask before adding a cache?

# 110. Knowledge Check — Guidance

### What does `@cache` mean?

It provides a process-local unbounded memoization cache for a function.

### What does `lru_cache` add?

It provides configurable cache retention, including LRU eviction when bounded.

### Why hashable arguments?

The cache must be able to use the arguments as part of a hash-based key.

### Why is a mutable result dangerous?

A cache can return the same object to later callers, allowing one caller's mutation to affect another caller.

### Why is cache invalidation necessary?

The stored result can outlive the validity of the state from which it was computed.

### Why is a model version relevant?

A new model can produce a different result for the same raw input.

### Why is tenant context relevant?

The same resource identifier can have different permitted or contextual results for different tenants.

### What is partial?

It creates a new callable with some arguments already supplied.

### What is the core difference?

```text
cache
→ reuse result

partial
→ reuse configuration
```

# 111. Interview Questions

## Beginner

1. What is `functools`?
2. What is memoization?
3. What is caching?
4. What is a cache hit?
5. What is a cache miss?
6. What is `lru_cache`?
7. What is `partial`?
8. What is `partialmethod`?

## Intermediate

9. `cache` vs `lru_cache`?
10. What does `maxsize` do?
11. What is LRU eviction?
12. Why must arguments be hashable?
13. What does `cache_info()` do?
14. What does `cache_clear()` do?
15. What does `cache_parameters()` do?
16. `partial` vs lambda?
17. `partial` vs wrapper?
18. `partial` vs `partialmethod`?

## Advanced

19. Explain cache-key semantics.
20. Explain `typed=True`.
21. Why can keyword ordering affect cache entries?
22. Why can cached methods retain `self`?
23. Why can concurrent cache misses run the underlying function more than once?
24. Why are side-effect functions poor cache candidates?
25. Why can mutable return values be dangerous?
26. Why does `maxsize` not equal a memory limit?
27. Why isn't LRU the same as TTL?
28. Explain `__wrapped__`.

## Production

29. How do you decide whether a function is cacheable?
30. How would you design a cache key for embeddings?
31. How would you handle model version changes?
32. How would you prevent cross-tenant cache collisions?
33. When would you use a process-local cache?
34. When would you use an external cache?
35. How would you measure cache effectiveness?
36. When would you decide not to cache?
37. How would you test cache invalidation?
38. How would you document a cache's correctness contract?

# 112. Interview Model-Answer Guidance

## `cache` vs `lru_cache`

A strong answer says:

```text
cache → simple unbounded memoization
lru_cache → memoization with configurable retention and LRU eviction
```

Then discusses memory, reuse, workload, and lifecycle.

## Hashability

Explain dictionary-style key semantics rather than simply saying "Python requires it."

## Invalidation

Explain that eviction is not invalidation.

```text
LRU → memory/working-set policy
invalidation → correctness/freshness policy
```

## Mutable return values

Explain that the cache can retain and return object references.

## Process-local

Explain that each process has its own memory and therefore its own decorator cache.

## AI key design

List every input dimension that changes the result, including model/configuration version and security context when relevant.

# 113. Architecture Scenarios

Use this framework for each scenario:

```text
1. Is the operation deterministic?
2. What exactly is the cache key?
3. How long is the result valid?
4. How is invalidation handled?
5. What is the memory policy?
6. Is tenant/user context relevant?
7. Is authorization relevant?
8. Is cross-process sharing required?
9. What happens after restart?
10. How will success be measured?
```

## Scenario 1 — LLM Metadata Cache

A service repeatedly requests model metadata.

Consider:

```text
model_id
+
model_version
```

A local LRU cache may be suitable.

## Scenario 2 — Embedding Cache

Identical document chunks are embedded repeatedly.

Consider:

```text
provider
+
model
+
model_version
+
preprocessing_version
+
text
```

Discuss memory and persistence.

## Scenario 3 — Document Processing

Deterministic parsing happens repeatedly in one worker.

Discuss:

```text
document_version
+
parser_version
```

## Scenario 4 — RAG Retrieval

The index changes continuously.

Ask whether retrieval results can remain valid long enough for a process-local memoization strategy.

## Scenario 5 — Public API Metadata

A service retrieves stable public information.

Discuss whether `lru_cache` is enough or whether an external shared cache would be more appropriate.

## Scenario 6 — Authorization-Sensitive Read

The result differs by access scope.

Discuss which identity/context dimensions belong in the key.

## Scenario 7 — Agent Tool

A tool performs an external action.

Discuss why memoization can suppress side effects and why idempotency is a separate design.

## Scenario 8 — Multi-Worker Inference

Ten workers share traffic.

Explain why local caches diverge and when shared caching may become necessary.

# 114. Debugging Challenges

These are intentionally broken or misleading examples. Diagnose first.

## Challenge 1 — Unhashable Input

```python
from functools import cache

@cache
def total(items):
    return sum(items)

total([1, 2, 3])
```

Questions:

- What happens?
- Why?
- What immutable representation could be appropriate?

## Challenge 2 — Stale Configuration

```python
from functools import cache

settings = {"debug": False}

@cache
def debug_enabled():
    return settings["debug"]
```

Then:

```python
debug_enabled()
settings["debug"] = True
debug_enabled()
```

Questions:

- Why can the second call still be `False`?
- What invalidation design would be appropriate?

## Challenge 3 — Mutable Return

```python
from functools import cache

@cache
def get_items():
    return []

items = get_items()
items.append("x")

print(get_items())
```

Explain the shared-state behavior.

## Challenge 4 — Wrong AI Key

```python
@cache
def embed(text):
    return embed_with_current_model(text)
```

What breaks after a model upgrade?

## Challenge 5 — Cache Too Small

```python
@lru_cache(maxsize=2)
def compute(x):
    return x * 2
```

Workload:

```text
A B C A B C A B C
```

Why might the hit rate be poor?

# 115. Debugging Challenges — Partial

## Challenge 6 — Positional Conflict

```python
from functools import partial

def greet(name, greeting):
    return f"{greeting}, {name}"

hello_alice = partial(greet, "Alice")

hello_alice(name="Bob", greeting="Hello")
```

Explain the argument conflict.

## Challenge 7 — Hidden Logic

```python
processor = partial(
    process,
    mode="production",
    strict=True,
    transform="normalize",
)
```

At what point would a named wrapper or configuration object improve readability?

## Challenge 8 — Partial Method

```python
class Worker:
    def run(self, mode):
        return mode

    run_prod = partial(run, "production")
```

Why should the method-oriented tool be considered?

The lesson is to understand method binding and use `partialmethod` when it expresses the intended class behavior.

# 116. More Debugging Challenges — Production

## Challenge 9 — Test Pollution

```python
@lru_cache(maxsize=32)
def compute(x):
    return x * 2
```

Test A calls:

```python
compute(10)
```

Test B expects its first `compute(10)` call to be a miss.

Why can Test B fail?

## Challenge 10 — Unbounded User Input

```python
@cache
def parse_user_text(text):
    return expensive_parse(text)
```

What memory risk appears when every request contains unique text?

## Challenge 11 — Missing Tenant

```python
@cache
def get_document(document_id):
    return fetch_document_for_current_tenant(document_id)
```

What hidden dependency is missing from the key?

## Challenge 12 — Model Configuration

```python
@lru_cache(maxsize=1024)
def predict(prompt):
    return call_model(prompt)
```

List at least five pieces of state that could change the result.

# 117. Comparison Tables

## `cache` vs `lru_cache`

| Feature | `cache` | `lru_cache` |
|---|---|---|
| Core purpose | unbounded memoization | memoization with configurable retention |
| Default retention | unbounded | 128 calls when using its default |
| Eviction policy | none | LRU when bounded |
| `maxsize` | not used as its main API | configurable |
| `cache_info()` | use `lru_cache` when cache statistics are needed | available |
| `cache_clear()` | available | available |
| `cache_parameters()` | not the central distinction | available |
| Typical use | naturally bounded key domains | potentially larger working sets |

## `partial` vs Lambda vs Wrapper

| Approach | Best for | Strength | Trade-off |
|---|---|---|---|
| `partial` | argument pre-filling | explicit adaptation | limited custom logic |
| lambda | tiny custom transformation | flexible and concise | can obscure meaning |
| wrapper | custom behavior | explicit and extensible | more code |

## `partial` vs `partialmethod`

| Feature | `partial` | `partialmethod` |
|---|---|---|
| Produces | callable object | method descriptor |
| Typical location | normal application code | class method definition |
| Pre-fills arguments | yes | yes |
| Handles method binding | general callable semantics | designed for method binding |

## Process-Local vs External Cache

| Characteristic | `functools` cache | External cache |
|---|---|---|
| Memory location | process | separate system |
| Cross-worker sharing | no | often yes |
| Restart persistence | no | depends on system |
| TTL | no built-in TTL | commonly available |
| Network cost | no | usually yes |
| Serialization | normal Python object references | typically required |
| Operational complexity | low | higher |

# 118. API Matrix

## Cache APIs

| API | Purpose | Main input | Result/behavior |
|---|---|---|---|
| `cache` | unbounded memoization | callable | cached callable |
| `lru_cache` | bounded/unbounded memoization | callable + options | cached callable |
| `cache_info()` | inspect metrics | none | statistics object |
| `cache_parameters()` | inspect configuration | none | information dictionary |
| `cache_clear()` | clear entries | none | cache reset |
| `__wrapped__` | access underlying function | attribute | original callable |

## Partial APIs

| API/attribute | Purpose |
|---|---|
| `partial()` | create configured callable |
| `.func` | original callable |
| `.args` | stored positional arguments |
| `.keywords` | stored keyword arguments |
| `partialmethod()` | method-oriented partial application |
| `Placeholder` | reserve a positional slot in Python 3.14+ |

# 119. Performance and Memory Model

Think of a cached call as:

```text
arguments
   ↓
key handling
   ↓
cache lookup
   |
   +---- hit ----> return
   |
   +---- miss ---> underlying computation
                    ↓
                 store result
```

A useful conceptual cost model is:

```text
cache value
=
lookup cost
+
memory cost
+
lifecycle complexity
```

versus:

```text
recompute value
=
computation cost
```

Caching is attractive when the expected saved computation is larger than the costs and risks introduced by the cache.

### Time complexity language

For hash-based cache operations, think in terms of typical expected constant-time lookup behavior rather than an absolute guarantee under every possible hashing workload.

For `lru_cache`, additional bookkeeping is needed to manage recency and eviction.

Do not make unsupported micro-performance claims about one form always beating another.

Measure the workload.

# 120. Cache Decision Framework

Before adding `@cache` or `@lru_cache`, ask:

```text
[ ] Is the function deterministic enough?
[ ] Are the relevant arguments hashable?
[ ] Are repeated inputs common?
[ ] Is the computation expensive enough?
[ ] Is the result safe to reuse?
[ ] Is the result's validity period understood?
[ ] Is the cache key complete?
[ ] Is the key normalized consistently?
[ ] Could time affect the result?
[ ] Could randomness affect the result?
[ ] Could database/file/API state affect the result?
[ ] Does user/tenant context matter?
[ ] Does authorization matter?
[ ] Does model/version/configuration matter?
[ ] Is unbounded growth acceptable?
[ ] If not, what maxsize is appropriate?
[ ] Is memory impact understood?
[ ] Is cache behavior observable?
[ ] Is invalidation defined?
[ ] Is process-local scope sufficient?
[ ] What happens after restart?
```

If several answers are unclear, caching is not ready to be added.

# 121. Partial Decision Framework

Use `partial` when:

```text
an existing callable already has the right behavior
+
some arguments should be fixed
+
remaining callers need a simpler interface
```

Use a wrapper when:

```text
validation
logging
branching
metrics
error translation
additional business logic
```

is required.

Use a configuration object when:

```text
many options
+
domain meaning
+
validation
+
lifecycle
+
serialization
```

make the configuration a meaningful piece of application state.

# 122. Production Checklist

## Caching

```text
[ ] Primary use case is explicit.
[ ] Function semantics are understood.
[ ] Function is deterministic enough for reuse.
[ ] All result-determining inputs are represented.
[ ] Arguments are hashable.
[ ] Keyword-call conventions are controlled.
[ ] Mutable arguments are handled safely.
[ ] Mutable return values are handled safely.
[ ] Cache size is intentional.
[ ] Memory implications are understood.
[ ] Freshness requirements are documented.
[ ] Invalidation is documented.
[ ] Model/configuration versions are considered.
[ ] Tenant context is considered.
[ ] Authorization context is considered.
[ ] Process-local limitations are understood.
[ ] Cross-worker sharing requirements are understood.
[ ] Hit/miss behavior can be measured.
[ ] Tests reset cache state.
[ ] Restart behavior is understood.
```

## Partial application

```text
[ ] Only argument adaptation is needed.
[ ] Fixed arguments are obvious.
[ ] Keyword conflicts are understood.
[ ] The resulting callable is readable.
[ ] A wrapper would not be clearer.
[ ] A configuration object would not be better.
[ ] Large captured objects are not unintentionally retained.
[ ] `partialmethod` is used when method binding is the real requirement.
```

# 123. Final Mental Model

## `functools`

```text
Reusable tools for working with functions and callable objects.
```

## Memoization

```text
Store a function result so a repeated logical call can reuse it.
```

## `@cache`

```text
Simple unbounded memoization.
```

## `@lru_cache`

```text
Memoization with configurable retention and LRU eviction.
```

## Cache hit

```text
The reusable result is already stored.
```

## Cache miss

```text
The result is not stored, so the computation runs.
```

## Cache key

```text
The semantic input identity used to decide whether reuse is valid.
```

## Cache invalidation

```text
The mechanism that prevents stale results from remaining authoritative.
```

## `partial`

```text
Pre-fill callable arguments.
```

## `partialmethod`

```text
Pre-fill method arguments while preserving method-oriented binding semantics.
```

## Final engineering rule

Choose these tools from:

```text
semantic intent
+
access pattern
+
correctness
+
lifetime
+
memory
+
deployment topology
```

not merely from API availability.

The two core ideas are:

```text
Caching
→ "Have I already computed this valid result?"

Partial application
→ "Can I reuse this callable with some stable configuration already fixed?"
```

When you can answer those questions clearly, `functools` stops being a collection of decorators and becomes a practical engineering toolbox.

# 124. Final Self-Review Checklist

```text
[ ] functools is introduced.
[ ] Function reuse is explained.
[ ] Higher-order functions are connected appropriately.
[ ] Memoization is explained.
[ ] Cache hit/miss is explained.
[ ] Manual caching is explained.
[ ] cache is explained.
[ ] cache is identified as unbounded.
[ ] Hashability is explained.
[ ] Mutable arguments are discussed.
[ ] Canonicalization is discussed.
[ ] Mutable return values are discussed.
[ ] Cache lifetime is discussed.
[ ] cache_clear() is explained.
[ ] lru_cache is explained.
[ ] LRU is explained.
[ ] maxsize is explained.
[ ] LRU eviction is explained.
[ ] typed=True is explained.
[ ] Cache-key semantics are explained.
[ ] Positional arguments are discussed.
[ ] Keyword arguments are discussed.
[ ] Keyword ordering is discussed.
[ ] cache_info() is explained.
[ ] cache_parameters() is explained.
[ ] __wrapped__ is explained.
[ ] Decorator stacking is addressed.
[ ] Purity/determinism is discussed.
[ ] Side effects are discussed.
[ ] External state is discussed.
[ ] Databases are discussed.
[ ] APIs are discussed.
[ ] Files are discussed.
[ ] Time/randomness/environment are discussed.
[ ] Cache invalidation is explained.
[ ] Process-local scope is explained.
[ ] Distributed-cache distinction is explained.
[ ] Method/self retention is discussed.
[ ] Concurrency boundary is discussed.
[ ] partial is explained.
[ ] Positional partial arguments are explained.
[ ] Keyword partial arguments are explained.
[ ] Keyword overriding is explained.
[ ] Positional conflicts are explained.
[ ] Python 3.14 Placeholder is explained.
[ ] partial attributes are explained.
[ ] Partial objects are callable.
[ ] partial vs lambda is explained.
[ ] partial vs wrapper is explained.
[ ] partialmethod is explained.
[ ] partial vs partialmethod is explained.
[ ] Callbacks are discussed.
[ ] Data-processing examples are included.
[ ] Backend/API examples are included.
[ ] ML preprocessing is included.
[ ] Embedding cache is included.
[ ] RAG cache is included.
[ ] Agent cache is included.
[ ] Evaluation cache is included.
[ ] Model-version concerns are included.
[ ] Multi-tenancy is included.
[ ] Authorization is included.
[ ] Performance measurement is included.
[ ] Memory trade-offs are included.
[ ] Production example is included.
[ ] Testing is included.
[ ] Debugging is included.
[ ] Exercises are included.
[ ] Knowledge checks are included.
[ ] Interview questions are included.
[ ] Architecture scenarios are included.
[ ] Debugging challenges are included.
[ ] Comparison tables are included.
[ ] API coverage is included.
[ ] Python-version considerations are included.
[ ] Mini-project is included.
[ ] Production limitations are included.
[ ] Decision framework is included.
[ ] Production checklist is included.
[ ] Final mental model is included.
```

# 125. Scope Verification Note

The source specification requires this chapter to change only:

```text
09-Advanced-Production-Oriented-Python-Foundations/09-functools-cache-and-partial.md
```

The artifact produced for this task is only the requested Markdown file in the working directory.

No Python source files, exercise files, answer-key files, configuration files, project files, or additional Markdown chapter files are required by this deliverable.

