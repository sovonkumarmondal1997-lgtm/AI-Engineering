# Fuzzing Basics: Finding Parser Bugs Before Attackers Do

> **Level:** Beginner → intermediate → advanced  
> **Baseline:** Python 3.12+, pytest 8+, Hypothesis; Atheris for coverage-guided fuzzing  
> **Focus:** input-handling reliability, parser contracts, failure triage, and safe security testing

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain fuzzing, test oracles, and how fuzzing complements example-based tests.
- Fuzz byte and text parsers with a deterministic hand-rolled loop and Hypothesis.
- Distinguish documented rejection of malformed input from unexpected implementation failures.
- Build a small Atheris harness with a seed corpus and understand dictionaries and instrumentation.
- Find and fix a length-prefixed binary parser defect, then preserve the discovery as an exact regression test.
- Choose between byte-level mutation and structure-aware generation; triage crashes and resource exhaustion safely.
- Apply fuzzing to native extensions, stateful APIs, OpenAPI services, and data/ML transformations.
- Design a bounded fuzzing policy that is repeatable, isolated, and useful in CI.

## 1. What fuzzing is—and is not

**Fuzzing** repeatedly supplies generated, mutated, or structure-aware inputs to a target and checks whether the target violates an observable property. Inputs may be random bytes, Unicode strings, valid documents with mutations, sequences of API calls, or protocol messages.

Example-based tests ask, “Does this known input produce the expected result?” Fuzzing asks, “Across many unfamiliar inputs, can this code violate its contract?” Both are needed.

| Technique | Main strength | Main limitation |
|---|---|---|
| Example-based unit tests | Precise expectations for known cases | Only cover cases someone selected |
| Property-based testing (Hypothesis) | Generates cases and shrinks failures to small examples | Strategy and test budget bound what it explores |
| Coverage-guided fuzzing (Atheris/libFuzzer) | Uses execution coverage to steer mutations toward new code paths | Coverage is not correctness; harness/oracle quality matters |
| Structure-aware fuzzing | Reaches deep states by producing mostly-valid inputs | Requires a useful grammar or model |
| Differential testing | Finds disagreement between independent implementations | Both implementations can share the same defect or differ by design |
| Metamorphic testing | Checks relations when exact expected output is hard to compute | The relation itself must be valid for the domain |

Fuzzing is especially valuable for parsers, deserializers, tokenizers, protocol handlers, archive readers, image/document readers, configuration loaders, binary file formats, and validation boundaries exposed to untrusted data. A parser can be correct for every hand-picked example and still crash on an empty buffer, a truncated length field, deeply nested input, or an integer that claims an impossible payload size.

### A useful mental model

A fuzz test has three parts:

1. **Target:** the function or operation under test, such as `parse(data)`.
2. **Input generator:** random, mutated, grammar-based, or stateful inputs.
3. **Oracle:** the rule that determines whether a result is acceptable.

A fuzzer without a meaningful oracle may generate millions of inputs while silently accepting bugs.

## 2. Define the oracle before generating inputs

An **oracle** describes what must be true for every generated input or operation. For a parser, the baseline oracle may be:

> Given bounded input, the parser either returns a valid result or raises its documented input-rejection exception. It must not leak unrelated exceptions, hang, or consume unbounded resources.

Common oracle families:

- **Crash-resistance:** malformed data must not trigger an unexpected exception or interpreter/native crash.
- **Rejection contract:** invalid input raises a documented exception such as `ParseError` or `ValueError`.
- **Round-trip:** `parse(serialize(value)) == value` for supported values. This does not imply every arbitrary byte string is valid.
- **Canonicalization/idempotence:** `normalize(normalize(x)) == normalize(x)` when normalization is defined that way.
- **Differential agreement:** two implementations agree on the shared supported input domain.
- **Metamorphic relation:** a known transformation of input must produce a predictable relation in output.
- **Resource budget:** work and memory remain within stated limits for the input-size range being tested.

A “must not crash” oracle is not the same as “must return the right answer.” A parser that returns `{}` for every input never crashes, but is likely broken. Pair crash-resistance with format invariants, boundary examples, round-trip properties, and differential checks where possible.

**Important limit:** an in-process assertion does not reliably enforce a hard timeout or memory ceiling. For potentially hostile loops, decompression, recursion, or native code, run the target in a child process with an external timeout and operating-system/container limits. Python-level `tracemalloc` does not measure every native allocation.

## 3. Build a small parser with an explicit contract

We will use a tiny binary record format:

- First two bytes: unsigned big-endian payload length (`0` through `65535`).
- Remaining bytes: exactly that many payload bytes.
- No trailing bytes are allowed.
- Input length is capped at `MAX_INPUT` bytes.
- Malformed input raises `ParseError`.

The parser should not allocate based on an untrusted length field before confirming the data is present. Python integers do not overflow like fixed-width C integers, but length arithmetic, resource limits, and assumptions at native boundaries can still be wrong.

```python
# parser.py
class ParseError(ValueError):
    """The input does not match the record format."""


MAX_INPUT = 4096


def parse_record(data: bytes) -> bytes:
    """Parse one [2-byte length][payload] record, with no trailing bytes."""
    if len(data) > MAX_INPUT:
        raise ParseError("input too large")
    if len(data) < 2:
        raise ParseError("missing length field")

    declared = int.from_bytes(data[:2], "big")
    payload = data[2:]
    if declared != len(payload):
        raise ParseError("declared length does not match payload")
    return payload


def serialize_record(payload: bytes) -> bytes:
    """Encode a payload accepted by parse_record."""
    if len(payload) > MAX_INPUT - 2:
        raise ValueError("payload too large")
    if len(payload) > 0xFFFF:
        raise ValueError("payload cannot fit in the two-byte length field")
    return len(payload).to_bytes(2, "big") + payload
```

The `MAX_INPUT` cap is deliberately lower than the representable two-byte length. It makes the exercise bounded and demonstrates that format limits and operational limits are separate. `serialize_record` permits at most `MAX_INPUT - 2` payload bytes, so its output never exceeds the parser's cap.

## 4. A deliberately flawed length-prefixed parser

Here is a bug that looks plausible in a first implementation. It trusts the length field when slicing but does not verify that the full payload exists.

```python
# flawed_parser.py — intentionally incorrect
class ParseError(ValueError):
    pass


def parse_record_flawed(data: bytes) -> bytes:
    if len(data) < 2:
        raise ParseError("missing length field")

    declared = int.from_bytes(data[:2], "big")
    # BUG: slicing silently returns fewer bytes when the input is truncated.
    return data[2 : 2 + declared]
```

For example, `b"\x00\x05ab"` declares five payload bytes but contains only two. The flawed parser returns `b"ab"` as if the record were valid. This is a semantic integrity defect, even though it does not crash. Downstream code may treat a truncated record as complete.

A fuzzer can expose the defect when the oracle says: **if parsing returns successfully, the declared length must equal the returned payload length and the entire record must be consumed**.

```python
# test_flawed_parser.py
from hypothesis import given, strategies as st
from flawed_parser import parse_record_flawed, ParseError


@given(st.binary(min_size=2, max_size=32))
def test_successful_parse_consumes_declared_length(data: bytes) -> None:
    declared = int.from_bytes(data[:2], "big")
    try:
        result = parse_record_flawed(data)
    except ParseError:
        return  # documented rejection is acceptable

    assert len(result) == declared, (
        f"declared {declared} bytes, parser returned {len(result)}"
    )
    assert len(data) == declared + 2, "parser accepted trailing bytes"
```

Hypothesis generates a two-byte prefix and a short suffix. It can shrink a failing case to a tiny example such as `b"\x00\x01"`: the header declares one byte, but the payload is empty. The exact minimized example may vary by Hypothesis version, strategy, and run; the invariant is what matters. This test intentionally fails against the flawed implementation and should pass after the fix.

### Corrected implementation and regression tests

```python
# parser.py
class ParseError(ValueError):
    """The input does not match the record format."""


MAX_INPUT = 4096


def parse_record(data: bytes) -> bytes:
    if len(data) > MAX_INPUT:
        raise ParseError("input too large")
    if len(data) < 2:
        raise ParseError("missing length field")

    declared = int.from_bytes(data[:2], "big")
    actual = len(data) - 2
    if declared != actual:
        raise ParseError("declared length does not match payload")
    return data[2:]


def serialize_record(payload: bytes) -> bytes:
    if len(payload) > MAX_INPUT - 2:
        raise ValueError("payload too large")
    return len(payload).to_bytes(2, "big") + payload
```

```python
# test_parser.py
import pytest
from hypothesis import given, strategies as st

from parser import MAX_INPUT, ParseError, parse_record, serialize_record


def test_empty_payload_is_valid() -> None:
    assert parse_record(b"\x00\x00") == b""


def test_regular_payload() -> None:
    assert parse_record(b"\x00\x03abc") == b"abc"


@pytest.mark.parametrize("data", [b"", b"\x00", b"\x00\x01", b"\x00\x01ab"])
def test_malformed_or_trailing_data_is_rejected(data: bytes) -> None:
    with pytest.raises(ParseError):
        parse_record(data)


def test_input_limit_is_enforced() -> None:
    with pytest.raises(ParseError, match="too large"):
        parse_record(b"\x00\x00" + b"x" * (MAX_INPUT - 1))


@given(st.binary(max_size=MAX_INPUT - 2))
def test_round_trip(payload: bytes) -> None:
    assert parse_record(serialize_record(payload)) == payload


@given(st.binary(min_size=2, max_size=MAX_INPUT))
def test_successful_parse_matches_declared_length(data: bytes) -> None:
    try:
        result = parse_record(data)
    except ParseError:
        return
    assert len(result) == int.from_bytes(data[:2], "big")
```

The regression case should preserve the exact bytes that revealed the defect. Once Hypothesis has minimized a failure, copy that input into a deterministic test such as:

```python
def test_regression_rejects_truncated_payload() -> None:
    with pytest.raises(ParseError):
        parse_record(b"\x00\x01")
```

A permanent regression test protects against reintroducing the same bug even if future fuzzing does not rediscover it. The generated property test stays too; one is not a replacement for the other.

## 5. Expected rejection versus unexpected failure

Fuzzing intentionally explores malformed inputs. A parser should often reject them, and that is normal behavior—not a bug. The harness must know which exception types represent documented rejection.

```python
try:
    parse_record(data)
except ParseError:
    pass  # documented invalid input; acceptable
```

Do **not** write this:

```python
try:
    parse_record(data)
except Exception:
    pass  # BAD: hides bugs
```

A broad `except Exception` can conceal `IndexError`, `TypeError`, `AssertionError`, accidental `KeyError`, logic failures surfaced as `RuntimeError`, and bugs introduced by refactoring. The fuzzer then reports the input as “handled” and stops treating the failure as a finding. It also makes the harness's behavior less useful as a correctness oracle.

Catch only exceptions that the parser contract explicitly documents for invalid input. If the target uses multiple documented rejection types, catch that narrow tuple. Do not catch `BaseException`: it includes process-control exceptions such as `KeyboardInterrupt` and `SystemExit`.

There is one nuance: a parser may legitimately document a broader exception type, such as `ValueError`. Catch it only if the contract genuinely treats every relevant `ValueError` from that boundary as invalid input. Prefer a dedicated exception such as `ParseError` when designing a parser API, because it separates input rejection from programming mistakes.

## 6. Hand-rolled random fuzzing

Before using a dedicated fuzzer, a small deterministic loop is useful for learning and smoke testing. Use a local random generator with a fixed seed so a failure can be reproduced. Bound both input size and iteration count.

```python
# random_fuzz.py
import random

from parser import ParseError, parse_record


def run_smoke_fuzz(iterations: int = 5_000, seed: int = 20261018) -> None:
    rng = random.Random(seed)
    for index in range(iterations):
        size = rng.randrange(0, 129)
        data = rng.randbytes(size)
        try:
            parse_record(data)
        except ParseError:
            continue  # documented rejection
        # A successful parse is allowed, but its contract must still hold.
        assert len(data) >= 2
        assert len(parse_record(data)) == int.from_bytes(data[:2], "big")


if __name__ == "__main__":
    run_smoke_fuzz()
    print("bounded smoke fuzz completed")
```

The fixed seed makes this exact sequence repeatable with the same Python behavior. Random fuzzing is not a substitute for boundary-oriented test cases; it may not hit the interesting header values for a long time. For targeted cases, generate values around boundaries: `0`, `1`, `MAX_INPUT`, one below, one above, `0xFFFF`, truncated headers, and payload lengths that disagree with the header.

A hand-rolled loop has no coverage feedback and little automatic minimization. When it finds a failure, print or persist the seed, iteration number, and exact input in hexadecimal or base64. Do not log unbounded binary blobs into shared logs if they may contain secrets.

## 7. Hypothesis: property-based fuzzing in everyday tests

Install the development dependency in the project environment, for example:

```bash
uv add --dev hypothesis pytest
uv run pytest
```

Hypothesis generates many inputs and shrinks a failing input toward a simpler counterexample. Shrinking is one of its most valuable features: a 900-byte failing input may reduce to a two-byte prefix that demonstrates the actual boundary error.

### Binary and text strategies

```python
from hypothesis import given, settings, strategies as st


@given(st.binary(max_size=2_000))
def test_binary_parser_rejects_or_returns(parser, data: bytes) -> None:
    # Replace `parser` with a project-specific fixture or call.
    ...


@given(st.text(max_size=2_000))
def test_text_parser_rejects_or_returns(data: str) -> None:
    # Exercise Unicode, NULs, combining marks, and unusual code points.
    ...
```

The first snippet illustrates the strategy shape; it is not a complete test because `parser` is project-specific. A complete test for our parser appears below.

```python
from hypothesis import given, strategies as st
from parser import ParseError, parse_record


@given(st.binary(max_size=2_000))
def test_parser_has_no_unexpected_exception(data: bytes) -> None:
    try:
        parse_record(data)
    except ParseError:
        pass
```

This is a useful baseline oracle, but it checks only unexpected exceptions. It does not prove semantic correctness, and it does not impose a hard time or memory limit. Add invariants, boundary tests, and an external process limit for potentially dangerous targets.

For text parsers, use `st.text(max_size=...)` and assert the text parser’s documented rejection type (for example, `TextParseError`) rather than catching every exception. If using a hand-rolled string loop, seed a local `random.Random`, cap both string length and iteration count, and include Unicode edge cases such as NUL, combining marks, and non-ASCII characters. For structured values use `st.dictionaries`, `st.lists`, `st.tuples`, `st.one_of`, and `st.builds` as appropriate. For binary formats, `st.binary()` explores arbitrary bytes, while composite strategies can generate valid headers and then mutate one property at a time. `max_size` limits generated input length; it does not guarantee bounded CPU time for a pathological regular expression or decompressor.

### Control cost and reproduce failures

- Keep per-example input sizes modest initially; increase only when resource budgets justify it.
- Use `@settings(max_examples=...)` for a deliberately bounded local experiment. Defaults may change across Hypothesis versions; make the budget explicit for a teaching exercise or CI lane.
- Let Hypothesis manage its example database in normal test workflows; avoid deleting its state as part of each run.
- Use the reported falsifying example to reproduce the issue, then add an exact regression test.
- Avoid `deadline=None` as a universal “fix” for slow tests. A deadline is a useful signal, but it is not a security-grade timeout and machine load can affect it.

```python
from hypothesis import given, settings, strategies as st


@settings(max_examples=300, deadline=100)  # milliseconds per example; tune for your environment
@given(st.binary(max_size=512))
def test_small_inputs(data: bytes) -> None:
    # Call the real target and assert its documented contract.
    ...
```

This is a template: replace `...` with the target's contract. `deadline` measures example execution in Hypothesis; use process isolation and OS-level limits for hard containment.

## 8. Coverage-guided fuzzing with Atheris

Atheris is a coverage-guided Python fuzzer built on libFuzzer. It mutates inputs and uses instrumentation/coverage feedback to favor inputs that reach new execution paths. It is particularly useful for parsers and libraries where the input can be represented as bytes.

Install Atheris in a supported environment according to its current package/platform instructions. Native toolchains and supported Python/platform combinations matter; do not assume every operating system or Python build works identically.

### Minimal harness

```python
# fuzz_parser.py
import sys

import atheris

with atheris.instrument_imports():
    import parser as target


def TestOneInput(data: bytes) -> None:
    # Keep the harness fast and side-effect free. Input is capped at 4096 bytes.
    if len(data) > target.MAX_INPUT:
        return
    try:
        result = target.parse_record(data)
    except target.ParseError:
        return  # only documented invalid-input rejection is ignored

    # A successful result must obey the format's declared-length invariant.
    if len(data) < 2:
        raise AssertionError("parser accepted input without a complete header")
    declared = int.from_bytes(data[:2], "big")
    if len(result) != declared or len(data) != declared + 2:
        raise AssertionError("parser accepted an inconsistent record")


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
```

The module is named `parser.py` here for clarity; in a real project, import the package under test. Instrument imports before importing the target so Atheris can instrument eligible Python code. The harness intentionally skips oversized inputs rather than testing the size guard; exercise the `MAX_INPUT + 1` boundary in ordinary unit tests, or raise the cap and let the parser reject it. Do not confuse harness input caps with target validation tests.

Run with a corpus directory containing seed files, for example (from the directory containing `fuzz_parser.py`; the example uses POSIX shell syntax):

```bash
mkdir -p corpus/parser
printf '\000\000' > corpus/parser/empty.bin
printf '\000\003abc' > corpus/parser/abc.bin
printf '\000\005ab' > corpus/parser/truncated.bin
uv run python fuzz_parser.py corpus/parser -max_len=4096 -max_total_time=60
```

Atheris passes libFuzzer arguments supplied to `atheris.Setup(sys.argv, ...)` through to the engine. Options can vary by Atheris/libFuzzer build, so confirm the flags supported by the installed tool (`-help`) and run only in a controlled environment. The command above is an example, not evidence that this fuzz campaign has been executed. Seed files help the fuzzer start near meaningful format states; they are not proof that those states are fully tested.

### Corpus and dictionary

A **corpus** is a directory of inputs used as starting examples and accumulated discoveries. Start with:

- Minimal valid inputs: empty payload, one-byte payload, typical record.
- Boundary values: largest supported payload, zero length, maximum representable length.
- Invalid inputs: truncated prefix, truncated payload, extra trailing bytes, inconsistent length.
- Real-world samples that are safe to share and stripped of secrets/PII.

A **dictionary** gives the mutator useful tokens or byte sequences, such as magic constants, separators, field names, or protocol markers. For a binary length-prefix parser, the two-byte length values are often more useful as corpus seeds than a dictionary. For structured text, a dictionary may contain `"{`, `":"`, `null`, `true`, and format-specific tokens. Dictionaries are hints, not grammars.

Keep corpus files small, review additions, remove duplicates/redundant inputs with the fuzzer's corpus tooling where available, and preserve minimized regression cases separately in the normal test suite. Do not commit proprietary/customer payloads or secrets to a public corpus.

### python-afl awareness

`python-afl` is an alternative AFL-based approach. AFL-family tools typically use a different execution/instrumentation workflow from Atheris/libFuzzer; setup depends on the Python build, instrumentation mode, and environment. Learn the concepts—input file or stdin, persistent versus process-per-input execution, coverage feedback, corpus, dictionary, timeout—but choose one supported toolchain for a project rather than mixing instructions blindly.

## 9. Harness engineering: fast, deterministic, isolated

A harness is part of the test system and can be defective too. Good harnesses are:

- **Small:** one entry point, one target, one or two clear invariants.
- **Fast:** no remote calls, large setup, repeated disk writes, or expensive global initialization per input.
- **Bounded:** cap input size, recursion/decompression limits where available, run budget, timeout, and memory.
- **Deterministic where possible:** fixed configuration, no current-time dependence, no uncontrolled randomness, no dependence on previous inputs.
- **Isolated:** no production database, network, destructive filesystem actions, credentials, or shared mutable state.
- **Observable:** preserve exact failing bytes and a reproducible command/seed.

If the target writes files, wrap the logic so the fuzz target calls a pure parse/transform function, or use a temporary directory in an isolated child process. Never fuzz code that can delete or overwrite arbitrary files. Do not direct fuzz traffic at production services. For a service/API, use a local test instance, explicit authorization, low request budgets, and a dedicated disposable environment.

### Resource bounds are layered

1. Input-size cap before parsing.
2. Format-specific bounds: maximum nesting depth, field count, declared decompressed size, archive entry count, and total output size.
3. Fuzzer iteration/time budget.
4. Per-input timeout in a child process for hang-prone targets.
5. Process/container memory and CPU limits.
6. Restricted filesystem/network permissions and a disposable working directory.

On Unix-like systems, `resource.setrlimit` can set some process resource limits, but availability and exact semantics vary by OS and resource. It is not portable containment, and it cannot safely interrupt every hang. Prefer process/container isolation and supervisor-enforced timeouts for hard limits. Resource limits can also interfere with the fuzzer itself, so test them deliberately.

## 10. Useful properties beyond “does not crash?”

### Round-trip

For supported values, test `parse(serialize(value)) == value`. Also test malformed serialized data independently; round-trip tests only explore values the serializer can represent.

```python
@given(st.binary(max_size=MAX_INPUT - 2))
def test_record_round_trip(payload: bytes) -> None:
    assert parse_record(serialize_record(payload)) == payload
```

### Differential testing

Compare independent implementations only on their common, documented domain. For JSON, for example, compare `json.loads` and `orjson.loads` for valid JSON and agreed error categories; implementations may intentionally differ in accepted extensions, numeric handling, duplicate keys, or error types. A disagreement is a lead to investigate, not automatic proof that one side is wrong.

```python
import json
import orjson
from hypothesis import given, strategies as st


# Generate a deliberately shared subset of JSON values: bounded integers,
# strings, booleans, null, lists, and string-to-integer objects.
small_int = st.integers(min_value=-(2**53), max_value=2**53)
json_value = st.recursive(
    st.one_of(st.none(), st.booleans(), small_int, st.text(max_size=32)),
    lambda children: st.one_of(
        st.lists(children, max_size=5),
        st.dictionaries(st.text(max_size=16), small_int, max_size=5),
    ),
    max_leaves=10,
)


@given(json_value)
def test_json_implementations_agree_on_shared_values(value: object) -> None:
    data = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
    assert orjson.loads(data) == json.loads(data)
```

This test deliberately generates a small shared subset instead of feeding arbitrary UTF-8 bytes to both libraries. Exact compatibility still requires a clearly defined domain and explicit handling of differences such as duplicate object keys, numeric precision, extensions, and error behavior. In production, include `orjson` as a test dependency and expand the strategy only where the two libraries are intended to agree.

### Metamorphic properties for data and ML code

Sometimes no easy “golden answer” exists, but relations should hold:

- Permuting rows should not change a commutative aggregate such as a sum or count, assuming duplicate rows and null semantics are unchanged.
- Splitting a dataset into chunks and combining partial counts should equal counting the full dataset.
- Normalization performed twice should equal normalization once, if it is specified as idempotent.
- Serializing and reloading a dataset should preserve schema and documented values.
- Reordering independent records should not alter a model evaluation metric when the metric is order-independent and the evaluation pipeline has no order-sensitive sampling.

For ML systems, account for randomness, floating-point reduction order, batching, GPU nondeterminism, and model-version differences. Use tolerances and controlled seeds where appropriate; do not assert bitwise equality unless the contract promises it.

## 11. Structure-aware versus byte-level fuzzing

**Byte-level (mutation) fuzzing** flips bits, changes bytes, truncates data, duplicates chunks, and splices inputs. It is excellent for malformed headers and low-level parser robustness. However, if a format has checksums, magic bytes, or deep structure, random mutation may fail at the first validation check and never reach complex code.

**Structure-aware fuzzing** generates inputs from a grammar, schema, strategy, or model. It can make valid JSON objects, nested protocol messages, or binary records with consistent lengths, then mutate one invariant at a time. It reaches deeper states but may miss malformed encodings if it only generates valid structures.

A practical campaign combines both:

1. Seed corpus of small valid and invalid samples.
2. Byte mutation to stress parsing boundaries.
3. Structure-aware generation for deep semantic paths.
4. Targeted mutations: corrupt length/checksum, truncate nested object, duplicate a field, exceed nesting or count limits.
5. Regression tests for each meaningful defect.

## 12. Bug classes fuzzing can expose

### Unhandled exceptions and malformed boundaries

Empty input, one-byte headers, invalid UTF-8, truncated structures, duplicate fields, unexpected types, and missing delimiters often expose unchecked assumptions. Expected rejection is fine; unrelated exceptions are findings.

### Infinite loops and algorithmic complexity

Malformed termination markers, cyclic references, pathological state machines, or repeated rescanning can hang. A fuzzer needs an external timeout to classify hangs reliably. Be careful with concurrency: a thread timeout does not necessarily stop the runaway thread.

### Excessive recursion and memory exhaustion

Deeply nested JSON-like data, recursive grammar productions, cyclic object graphs, huge list counts, and large allocation requests may cause `RecursionError`, high memory use, or process termination. Define maximum depth/counts and fuzz just below and above those limits. Avoid running memory-exhaustion cases in a developer's main process.

### ReDoS (regular-expression denial of service)

Certain regex patterns can take superlinear or exponential time on carefully shaped strings. Fuzzing may find slow inputs, but ordinary Hypothesis deadlines are not a hard containment boundary. Test suspicious patterns in a child process with an external timeout and a strict maximum input length. Review regex design and complexity rather than merely increasing the timeout.

### Binary length handling defects

Common errors include trusting declared lengths, off-by-one slices, integer conversion assumptions, multiplication overflow in native code, confusing bytes and element counts, accepting trailing bytes, and allocating before validating a length. Test zero, maximum, maximum-plus-one, truncated, overlong, and inconsistent fields.

### Decompression bombs and archive expansion

A small compressed input may expand to huge output or contain many entries. Cap compressed size, decompressed bytes, entry count, nesting, and CPU time. If the library supports bounded streaming decompression, stop once the output cap is reached. Do not test a real decompression bomb in an unbounded process. Use small controlled fixtures to verify that the cap triggers.

## 13. Native extensions and sanitizers

Pure-Python fuzzing is excellent for Python-level logic, validation, state transitions, and exception paths. If the parser calls C/C++/Rust/native code, Python-level fuzzing alone may not expose memory corruption, use-after-free, out-of-bounds access, or undefined behavior in the native layer.

- **ASan (AddressSanitizer):** detects many native memory errors, including out-of-bounds access and use-after-free.
- **UBSan (UndefinedBehaviorSanitizer):** detects many forms of undefined behavior in C/C++.
- Other platform/toolchain sanitizers may help with leaks, thread races, or other native failures.

Run the extension and fuzzer with a compatible instrumented native build and compiler/runtime setup. A Python exception is not a substitute for sanitizer instrumentation. Treat sanitizer findings as serious; capture the reproducer, native stack trace, build flags, platform, and version. Rebuild and rerun the exact minimized input after a fix.

## 14. Continuous fuzzing and corpus operations

Fuzzing works best as a recurring activity, not a one-time heroic run.

- **Pull request:** quick bounded smoke fuzz or regression suite; no unbounded campaigns.
- **Nightly:** longer budget, selected high-risk targets, coverage/corpus review, and failure triage.
- **Release:** longer run on release candidates and supported platforms/toolchains.
- **Continuous infrastructure:** OSS-Fuzz and ClusterFuzzLite are examples of systems that help run fuzzers continuously; onboarding requirements and supported languages/build systems differ.

Assign an owner to each harness. Track the target, contract/oracle, input cap, time/memory budget, corpus location, toolchain version, failure notification route, and regression-test location. Minimize corpus inputs, keep valuable seeds, remove secrets, and avoid allowing corpus growth to become unreviewed storage of customer data. Preserve the exact failing bytes for regressions even when the broader fuzz corpus is later minimized.

Do not treat “no crash found in 60 seconds” as proof of safety. Record the budget, version, corpus, platform, and known limitations so results can be interpreted honestly.

## 15. Stateful and API fuzzing

Some bugs require a sequence of operations, not a single byte string: cache insertion followed by eviction, writer then reader, transaction open/rollback, or parser reset followed by another parse. Hypothesis stateful testing can generate operation sequences using `RuleBasedStateMachine` and check invariants after each step.

A small conceptual example:

```python
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant


class CacheModel(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.model: dict[str, int] = {}
        self.cache = {}

    @rule(key=st.text(max_size=8), value=st.integers())
    def put(self, key: str, value: int) -> None:
        self.model[key] = value
        self.cache[key] = value

    @rule(key=st.text(max_size=8))
    def delete(self, key: str) -> None:
        self.model.pop(key, None)
        self.cache.pop(key, None)

    @invariant()
    def contents_match_model(self) -> None:
        assert self.cache == self.model


TestCache = CacheModel.TestCase
```

In real stateful tests, use the actual public API rather than mutating internal dictionaries, and ensure operations have bounded side effects. The model above is intentionally simple; it illustrates sequence generation and an invariant, not a production cache implementation.

For HTTP APIs, schema-aware fuzzing can use OpenAPI descriptions. **Schemathesis** is one tool that generates API cases from an OpenAPI schema and checks response behavior. Run it only against a local/test environment, with a restricted operation set, authentication appropriate to that environment, and rate limits. For example, after starting an explicitly disposable local test service, a current CLI form is `uvx schemathesis run http://127.0.0.1:8080/openapi.json --max-time 30`; verify the installed version’s `--help` before relying on flags in CI. Never substitute a production URL just to make the example run. Schema-driven tools can find invalid responses, contract mismatches, and edge cases, but they do not prove business semantics or authorize testing a third-party service.

## 16. Security-sensitive input surfaces

Prioritize surfaces where untrusted input crosses a trust boundary:

- Archive, image, document, media, and compressed-file readers.
- JSON/YAML/XML/protobuf and other deserializers; avoid unsafe general-purpose object deserialization for untrusted input.
- CSV, Parquet, Avro, database wire protocols, and streaming/event payload decoders.
- URL, path, header, cookie, and query parsing.
- Template engines, expression languages, regular expressions, and query builders.
- Authentication/token formats, signed-message parsers, and cryptographic protocol framing.
- Prompt, tool-call, and structured-output parsers in LLM agents—especially where parsed fields can trigger actions.

Fuzz pure parsing/validation layers separately from effects. For agent tool-call parsing, use mocked tools and assert that malformed data cannot cause real file deletion, network requests, privilege changes, or unintended tool invocation. Fuzzing checks robustness, not authorization policy by itself; add explicit security invariants and permission tests.

## 17. Triage and minimize findings

When a fuzzer finds a problem:

1. **Preserve the artifact:** save exact bytes, corpus file, seed, tool versions, platform, and command.
2. **Classify the failure:** unexpected exception, assertion/oracle violation, timeout, memory limit, native sanitizer finding, or environment/tool failure.
3. **Reproduce:** run the minimized input outside the long-running campaign using the same target version.
4. **Minimize:** let Hypothesis shrink naturally; use Atheris/libFuzzer minimization or corpus tools for coverage-guided crashes; simplify further only if behavior remains.
5. **Understand the contract:** is the input invalid, and if so should it raise `ParseError`? Or did valid input produce a wrong result? Distinguish product bugs from harness bugs and expected behavior.
6. **Fix root cause:** validate lengths before slicing/allocation, bound recursion/output, correct state transitions, or fix the native code.
7. **Add regression test:** retain exact minimized bytes and assert the required behavior.
8. **Rerun:** focused test, full regression suite, sanitizer run if relevant, then the fuzz campaign.
9. **Document:** record severity, impact, supported versions, and any corpus/privacy decision.

Never suppress a finding merely to make a fuzz run green. If an exception is legitimate, update the documented parser contract and test it explicitly rather than catching every exception in the harness.

## 18. Common mistakes

- **Catching `Exception` broadly:** hides programming errors and makes the oracle meaningless. Catch only documented rejection exceptions.
- **No semantic oracle:** “did not crash” does not guarantee correct output. Add length, schema, round-trip, differential, or metamorphic properties.
- **Unbounded input:** huge inputs can make the harness slow or exhaust memory. Start with strict caps and escalate in an isolated process.
- **No timeout isolation:** a fuzzer may hang forever in the target. Use supervisor-enforced timeouts for dangerous code.
- **Side effects in the target:** fuzzing can invoke the target thousands of times. Remove network/database/filesystem effects or isolate them safely.
- **Only random bytes:** deep parser logic may never be reached. Combine mutation with valid seeds and structure-aware generation.
- **Only valid structured data:** malformed boundaries remain untested. Include truncation, invalid lengths, duplicate fields, and trailing data.
- **Treating a fuzzer timeout as a definitive vulnerability without reproduction:** investigate environment noise, then reproduce in a bounded child process.
- **Not preserving exact bytes:** a prose description is not a reproducible regression case.
- **Not adding regression tests:** the same bug may return after the corpus changes.
- **Treating a clean fuzz run as proof:** fuzzing is evidence under a particular budget, corpus, build, and oracle—not proof of correctness.
- **Ignoring corpus privacy:** real-world samples can contain credentials, personal data, or proprietary content.

## 19. Exercises

### Exercise A — discover the length bug

1. Run the Hypothesis property against `parse_record_flawed`.
2. Record the smallest failing bytes in hexadecimal.
3. Explain why `data[2:2 + declared]` does not guarantee that `declared` bytes existed.
4. Implement the corrected parser and preserve the exact failure as a regression test.
5. Add tests for a missing prefix, truncated payload, trailing bytes, zero-length payload, maximum permitted input, and oversized input.

### Exercise B — improve the oracle

Start with a no-unexpected-exception test. Add a successful-parse invariant and a round-trip property. Describe what each property can and cannot detect.

### Exercise C — structure-aware inputs

Build a Hypothesis strategy that creates valid length-prefixed records. Then mutate one property: declared length plus one, payload truncation, or trailing byte. Compare how quickly it reaches the parser's deeper checks versus arbitrary bytes.

### Exercise D — resource-safe decompression

Use a tiny, bounded compressed fixture and a wrapper that refuses to emit more than a configured output limit. Test the exact boundary and boundary-plus-one. Do not create or run a giant expansion payload.

### Exercise E — design a fuzzing policy

For three components in a project, document input trust boundary, oracle, max input, resource limits, seed corpus, schedule, owner, and how findings become regression tests.

## 20. Fuzzing policy checklist

Before merging a fuzz harness, answer:

- [ ] Is the target a clear public boundary with a documented input contract?
- [ ] Does the harness catch only documented invalid-input exceptions?
- [ ] Does it assert meaningful invariants beyond “no crash” where possible?
- [ ] Are input size, CPU time, memory, nesting, decompressed output, and iteration budgets considered?
- [ ] Are hang-prone or native targets isolated in a child process/container?
- [ ] Are filesystem, network, database, and tool side effects disabled or safely mocked?
- [ ] Is the run reproducible from exact bytes, seed, versions, and command?
- [ ] Does the corpus contain small valid, invalid, and boundary examples without secrets?
- [ ] Are byte mutation and structure-aware inputs both considered?
- [ ] Are findings minimized, triaged, fixed, and added as permanent regression tests?
- [ ] Is the harness owned, scheduled, and monitored in CI/nightly/release workflows?
- [ ] Are limitations recorded so a short clean run is not mistaken for proof?

## 21. Self-check with model answers

### 1. What is the oracle in “the parser must not crash”? How does it differ from a round-trip oracle?

The crash-resistance oracle says the parser must not terminate unexpectedly for bounded inputs; invalid input may raise a documented rejection exception. A round-trip oracle says supported values survive serialization and parsing: `parse(serialize(x)) == x`. The first tests robustness, while the second tests a semantic relation for values the serializer can represent. Neither alone proves the whole parser correct.

### 2. Write a Hypothesis test that finds a bug in a deliberately flawed length-prefixed parser, then add the regression test.

Generate bytes with at least a two-byte prefix and bounded size. If parsing succeeds, assert that returned payload length equals the declared length and that no trailing bytes remain. The flawed parser accepts a truncated payload because slicing silently returns fewer bytes. After fixing the parser to compare declared and actual lengths, add a deterministic `pytest.raises(ParseError)` test using the minimized exact bytes, for example `b"\x00\x01"`.

### 3. List three input-handling components in your own projects that deserve fuzz harnesses and why.

Answers depend on the project. Good examples include a compressed archive reader (expansion and path-handling limits), a binary event decoder (length/truncation defects), and an API/tool-call JSON parser (unexpected structures must not trigger unintended actions). Choose components exposed to untrusted or high-volume input and define an explicit oracle for each.

## Execution and version note

The code and commands in this lesson are teaching examples, not a claim that a fuzzing campaign has been run. Run them in a project environment with the target package and the listed tools installed; verify platform-specific Atheris/native-sanitizer prerequisites and CLI flags against the installed versions. A successful syntax check is not equivalent to executing the tests, and a bounded fuzz run is not proof of correctness.

## Completion criteria

You are ready to apply this lesson when you can explain the target/generator/oracle split; run a bounded Hypothesis test; identify why broad exception swallowing is unsafe; fix and regress the length-prefix defect; create a minimal Atheris harness and seed corpus; and specify safe limits, triage steps, and an owner for a real fuzz target.
