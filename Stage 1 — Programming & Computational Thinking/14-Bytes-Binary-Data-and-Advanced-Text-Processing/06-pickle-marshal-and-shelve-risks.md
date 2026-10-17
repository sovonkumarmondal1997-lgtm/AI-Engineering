# Pickle, Marshal, and Shelve Risks

> **Baseline:** Python 3.12+. Version-specific and third-party notes are labelled. This lesson focuses on serialization trust boundaries, not merely saving and restoring objects.

## Learning outcomes

By the end, you can:

- Explain `pickle.dumps/loads`, `dump/load`, protocol compatibility, `marshal`, and `shelve`.
- Explain why unpickling may invoke code and why untrusted or unauthenticated pickle data must never be loaded.
- Inspect pickle opcodes with `pickletools` without unpickling.
- Describe the limits of restricted unpicklers, HMAC, scanners, and sandboxing.
- Choose appropriate formats for API messages, tables, configuration, arrays, and ML models.
- Identify compatibility, persistence, concurrency, and multiprocessing costs.
- Apply a serialization threat-model checklist.

## Prerequisites and scope

Know Python functions/classes, imports, exceptions, file I/O, bytes, and basic authentication terminology. Earlier lessons cover byte representations and binary files; this lesson uses those ideas without re-teaching them.

The parent tree places this at **Stage 1 — Programming & Computational Thinking / 14-Bytes-Binary-Data-and-Advanced-Text-Processing/06-pickle-marshal-and-shelve-risks.md**, after diffs/string utilities and before compression and memory-mapped files. Stay focused on serialization risks and format selection.

---

## 1. Serialization is not trust

**Serialization** converts an in-memory value to a representation that can be stored or transmitted. **Deserialization** reconstructs a value from that representation. A format does not automatically establish who created the data, whether it was modified, whether the producer is authorized, whether parsing can execute code, or whether the representation will remain compatible over time.

> Treat every serialized artifact as untrusted until its origin, integrity, and parsing behavior are established. For pickle specifically, never load data from an untrusted or unauthenticated source.

“It's on our server,” “it's in a cache,” and “it came from a model hub” are not sufficient trust arguments. Shared directories, poisoned caches, compromised build pipelines, registries, and network inputs can cross trust boundaries.

## 2. Pickle fundamentals

The standard-library `pickle` module serializes many Python objects.

- `pickle.dumps(obj)` returns serialized `bytes`.
- `pickle.loads(data)` reconstructs an object from bytes.
- `pickle.dump(obj, file)` writes to a binary file-like object.
- `pickle.load(file)` reads and reconstructs from a binary file-like object.

### 2.1 A trusted-data round trip

This example creates and consumes the bytes locally. It demonstrates the API; it is **not** a recommendation to load arbitrary files.

```python
import pickle

record = {"job_id": 17, "status": "complete", "items": [3, 5, 8]}
blob = pickle.dumps(record, protocol=pickle.HIGHEST_PROTOCOL)
restored = pickle.loads(blob)
assert restored == record
print(restored)
print(type(blob).__name__)
```

Expected output:

```text
{'job_id': 17, 'status': 'complete', 'items': [3, 5, 8]}
bytes
```

`pickle.HIGHEST_PROTOCOL` selects the highest protocol supported by the running interpreter. It is useful for controlled same-environment transfers, but may not be readable by older interpreters. If compatibility matters, choose a protocol supported by every required reader and test it.

### 2.2 Protocols and compatibility

Pickle has protocols 0 through 5. Protocol 0 is a legacy text representation; later protocols add support and efficiency features. Protocol 5 adds out-of-band buffer support.

**Python 3.12 note:** the default protocol is 4 and `pickle.HIGHEST_PROTOCOL` is 5. Defaults can change across Python versions; pin a protocol when compatibility is part of the contract. Protocol compatibility alone does not guarantee application compatibility: referenced modules/classes must remain importable and semantically compatible.

### 2.3 What can be pickled?

Built-in scalars and containers and many user-defined instances are commonly picklable. Functions and classes are generally referenced by qualified name rather than having their source code embedded, so the defining module and object must be importable at load time.

Common failure cases include lambdas and local/nested functions, open file handles, sockets, locks, generators, and objects whose state contains unpicklable members. Custom `__reduce__`, `__reduce_ex__`, or state methods can also fail. Exact behavior depends on the object and implementation: test the actual objects and deployment environment.

### 2.4 File APIs and explicit binary mode

```python
import pickle
from pathlib import Path
from tempfile import TemporaryDirectory

record = {"version": 1, "values": [10, 20]}
with TemporaryDirectory() as directory:
    path = Path(directory) / "trusted-local-cache.pkl"
    with path.open("wb") as stream:
        pickle.dump(record, stream, protocol=4)
    # Safe in this example because this code just created the file in a
    # controlled temporary directory; the extension itself proves nothing.
    with path.open("rb") as stream:
        restored = pickle.load(stream)
    print(restored == record)
```

Expected output: `True`.

The safety argument is controlled provenance, not the `.pkl` suffix.

## 3. Why unpickling can execute code

Pickle reconstructs Python objects, including objects requiring callable reconstruction logic. Opcodes such as `GLOBAL`, `STACK_GLOBAL`, `REDUCE`, and `BUILD` participate in resolving globals, calling reconstruction functions, and restoring state. A malicious stream can abuse these capabilities. Custom `__reduce__` or `__reduce_ex__` methods can return a callable and arguments used during reconstruction; the callable need not be harmless.

### 3.1 Harmless, isolated demonstration

The callable below only prints a message and returns a dictionary. The pickle is created locally and immediately loaded; there is no external artifact or destructive payload.

```python
import pickle

def announce(message):
    print(f"Reconstruction called: {message}")
    return {"message": message}

class HarmlessNotice:
    def __reduce__(self):
        return (announce, ("hello from a local demonstration",))

local_blob = pickle.dumps(HarmlessNotice())
result = pickle.loads(local_blob)
print(result)
```

Expected output:

```text
Reconstruction called: hello from a local demonstration
{'message': 'hello from a local demonstration'}
```

This illustrates the mechanism, not an exploit payload. **Never load a suspicious pickle to “see what it does.”**

### 3.2 Non-negotiable rule

Never call `pickle.load`, `pickle.loads`, or a library API that implicitly unpickles data when the source is untrusted or unauthenticated. This includes downloads, email attachments, public model hubs, network messages, uploads, shared caches, shared directories, and artifacts from another tenant or pipeline without an established trust boundary.

Authentication alone does not prove that a producer is benign. An authorized producer or signing pipeline may be compromised or malicious.

## 4. Inspecting pickle without loading it

`pickletools` is a standard-library module for inspecting pickle opcodes. `pickletools.dis()` disassembles a byte stream; it does not reconstruct the object through normal unpickling behavior.

```python
import pickle
import pickletools

sample = pickle.dumps({"x": 1}, protocol=4)
pickletools.dis(sample)
```

The exact opcodes and offsets vary by protocol/version. A typical protocol-4 stream for this dictionary includes instructions such as `PROTO`, `FRAME`, `EMPTY_DICT`, `SHORT_BINUNICODE`, `BININT1`, `SETITEM`, and `STOP`.

Ask whether the stream references globals/reconstruction callables, includes `REDUCE` or `BUILD` operations needing scrutiny, matches the claimed artifact type, or appears truncated. **Disassembly is not proof of safety.** Static inspection can miss contextual behavior; do not turn “I inspected it” into “it is safe to unpickle.”

## 5. Mitigations and their limits

### 5.1 Restricted `Unpickler.find_class`

A custom `pickle.Unpickler` can override `find_class(module, name)` to reject or allow particular global references. This may reduce exposure for a narrowly specified and tested data shape, but is not a general safe-pickle switch.

```python
import io
import pickle

ALLOWED_GLOBALS = {("builtins", "complex")}

class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) not in ALLOWED_GLOBALS:
            raise pickle.UnpicklingError(f"global is not allowed: {module}.{name}")
        return super().find_class(module, name)

def load_restricted(blob: bytes):
    return RestrictedUnpickler(io.BytesIO(blob)).load()

# Protocol 4 encodes this value through the allow-listed builtins.complex global.
blob = pickle.dumps(complex(1, 2), protocol=4)  # locally generated test data
assert load_restricted(blob) == complex(1, 2)
```

This demonstrates a narrow policy. A real policy must consider the complete opcode set, allowed types/callables, and resource exhaustion. A permitted class/callable may have risky behavior; an allow-list is not a universal proof of safety. Prefer non-executable formats for untrusted boundaries.

### 5.2 HMAC authentication

A message authentication code such as HMAC can detect modification if verification happens before parsing and the secret remains secret. It can help establish that a blob was produced by a party possessing the key. It does **not** establish benign intent: a malicious or compromised authorized producer can create a valid MAC.

Conceptual order:

1. Obtain bytes without unpickling them.
2. Verify the MAC over the exact bytes using a trusted secret.
3. Reject on verification failure.
4. Only consider loading if the producer and artifact are within an explicitly trusted boundary.

Key storage, rotation, authorization, replay policy, and verification order matter. This is not permission to accept arbitrary authenticated pickles.

### 5.3 Scanners and sandboxing

- **Fickling** is a third-party pickle analysis tool for investigating suspicious artifacts. It is an aid to review, not a safety guarantee.
- **Sandboxing** can reduce impact when risky parsers must be analyzed: use an isolated, unprivileged process/container, no secrets, minimal read-only filesystem, no unnecessary network, and strict CPU/memory/time limits. Sandboxes can be misconfigured or escaped; they do not justify loading untrusted pickle in an ordinary application process.
- Static analysis and code review help identify load sites and provenance assumptions but cannot prove all inputs safe.

### 5.4 Static-analysis policy

The roadmap names Bandit rules **B301/B403**. In commonly used Bandit versions, B301 flags unsafe pickle-related calls and B403 flags importing `pickle`. Rule behavior can vary by tool version; pin the scanner and consult its current rule documentation. An import may be legitimate for trusted writing or `pickletools`, but every load site needs careful trust analysis. Document suppression rationale.

The same policy should review `yaml.load` and dynamic execution such as `eval`, using the scanner's current rule mapping rather than assuming IDs are universal.

## 6. Safer format selection

“Safer” here means avoiding pickle's arbitrary-object reconstruction risk for an appropriate data shape. No format removes the need for size limits, schema validation, dependency hygiene, and resource controls.

| Use case | Consider | Caveat |
|---|---|---|
| API payload / interoperable records | JSON | Validate schema/types, limit size/depth, reject unexpected fields as appropriate |
| Flat tabular interchange | CSV | Define dialect, quoting, null representation, and types |
| Large analytical tables | Parquet or Arrow | Third-party libraries; govern schemas, versions, and metadata |
| Compact typed messages | MessagePack or Protocol Buffers | Library/schema versions matter; validate semantic constraints |
| Configuration | TOML or safe YAML loading | Validate values; parsing safety is not authorization |
| NumPy arrays | `numpy.save(..., allow_pickle=False)` for supported non-object arrays | Validate dimensions, dtype, and file size; avoid object arrays |
| Tensor weights | Safetensors where supported | Check framework support, provenance, and expected shapes |
| Portable inference | ONNX where supported | Inspect provenance and runtime/operator policy; complex parsers still need controls |
| Trusted Python-only local state | Pickle may be convenient | Only across a clearly trusted boundary; compatibility is fragile |

### 6.1 TOML and YAML

Python 3.11+ includes `tomllib` for reading TOML. It parses data rather than arbitrary Python object graphs, but applications must validate values and authorization decisions. For YAML, use the safe-loading API of the chosen library (for PyYAML, `yaml.safe_load`) rather than unsafe object constructors. Safe loading reduces object-construction risk but does not validate application semantics or eliminate resource-exhaustion risks.

### 6.2 NumPy arrays (third-party)

```python
# Requires third-party NumPy.
import numpy as np
from pathlib import Path
from tempfile import TemporaryDirectory

array = np.array([1.5, 2.5, 3.5], dtype=np.float64)
with TemporaryDirectory() as directory:
    path = Path(directory) / "values.npy"
    np.save(path, array, allow_pickle=False)
    restored = np.load(path, allow_pickle=False)
    assert np.array_equal(restored, array)
    print(restored.dtype, restored.tolist())
```

Expected output: `float64 [1.5, 2.5, 3.5]`.

`allow_pickle=False` prevents object arrays from being loaded through pickle; it is not a universal guarantee against malformed-file, resource, or parser risks. For ML models, prefer supported safer weight/interchange formats when practical, but still verify provenance, pin dependencies, review the artifact, and constrain loading/inference.

## 7. `marshal`: internal and version-dependent

`marshal` is primarily used by Python internals, including `.pyc` bytecode-cache machinery. Its format may change incompatibly between Python versions. It is not a general interchange or long-term archival format, and it is not designed as a security boundary for hostile input.

```python
import marshal

blob = marshal.dumps((1, "hello", [2, 3]))
restored = marshal.loads(blob)
print(restored)
```

Expected output: `(1, 'hello', [2, 3])`.

This simple round trip does not establish that arbitrary marshal inputs are safe. Avoid using it for data exchange or untrusted bytes.

## 8. `shelve`: persistent dictionary, not a database

`shelve` provides a dictionary-like interface backed by a `dbm` storage implementation and pickle. Values are pickled; reading an entry can trigger reconstruction behavior.

```python
import shelve
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    path = str(Path(directory) / "job-cache")
    with shelve.open(path) as db:
        db["job-17"] = {"status": "done", "attempts": 2}
    with shelve.open(path) as db:
        print(db["job-17"])
```

Expected output: `{'status': 'done', 'attempts': 2}`. This is safe only in the example's controlled temporary directory because the code created the data itself.

Operational limitations:

- **Concurrency:** `shelve` does not provide a general multi-process transactional database contract. Concurrent read/write access is not coordinated by the interface; use a database and locking strategy appropriate to the workload.
- **Backend differences:** `dbm` selects among platform-dependent backends. File layout, size limits, and behavior differ; do not assume backend files are portable.
- **Mutable values:** retrieving a list/dict and mutating it in place may not persist automatically. Reassign the value (`db[key] = value`) after mutation.
- **`writeback=True`:** caches accessed entries and writes them back on sync/close. This can consume substantial memory and write more data than expected. It does not make concurrent access safe.
- **Read risk and evolution:** shelve inherits pickle risks and class/module compatibility problems.

Treat `shelve` as a narrow local trusted cache, not a replacement for SQLite, PostgreSQL, or a concurrent transactional database.

## 9. Protocol 5 and out-of-band buffers

Pickle protocol 5 (Python 3.8+, PEP 574) supports out-of-band buffers. This was motivated by reducing copies when transferring large buffers, such as numerical arrays, alongside the pickle control stream. The producer and consumer must coordinate buffer order, lifetime, ownership, and transport. It is an optimization, not a security feature: protocol 5 does not make pickle safe for untrusted input and does not guarantee every path is zero-copy.

Use it only when both ends are controlled, compatible, and designed for the buffer protocol. For external model/data interchange, prefer a documented format and schema where practical.

## 10. Custom object state: `copyreg`, `__reduce_ex__`, `__getstate__`

These advanced hooks help explain object compatibility and risk; they do not make arbitrary objects portable automatically.

- `__reduce_ex__(protocol)` can supply reconstruction instructions and receives a protocol number. It generally takes precedence over `__reduce__` when present.
- `__getstate__` supplies state to serialize; restoration may use `__setstate__` or default mechanisms.
- `copyreg` registers reduction functions for types.

Custom reduction/state code can depend on import paths, callable behavior, and external resources. Treat it as executable serialization logic. Review changes, test supported protocols, and never use these hooks to accept untrusted producers.

## 11. ML model supply-chain risk

A model artifact may encode executable reconstruction behavior, not just numerical weights. Public hubs, mirrors, shared caches, and build pipelines are supply-chain boundaries. Risks include load-time code execution, resource exhaustion, dependency compromise, and tampered artifacts.

Controls:

1. Prefer Safetensors for weights when supported.
2. For PyTorch, understand the exact deployed API/version and prefer `torch.load(..., weights_only=True)` where appropriate and supported.
3. Pin dependencies, verify provenance/integrity, and record model source/revision.
4. Load in a least-privilege environment without secrets or unnecessary network access.
5. Validate expected tensor names, shapes, dtypes, and architecture; successful parsing does not prove trustworthiness.
6. Review custom classes/allow-list requirements rather than automatically permitting them.

**PyTorch version/context note:** `torch.load(weights_only=True)` behavior and defaults have changed across releases. Pass it explicitly where available, consult documentation for the deployed version, and test the exact artifact. It reduces a class of risks but is not an absolute guarantee for every file, dependency, or resource-exhaustion scenario. “PyTorch file” does not mean “safe weights.”

## 12. Multiprocessing and serialization costs

Process pools often serialize arguments/results, especially under spawn-based process creation. This adds CPU/memory/copy overhead, can fail for lambdas/local functions/open handles/locks, and creates compatibility constraints. It is also a risk if workers deserialize data from a less-trusted process or shared channel.

Prefer importable module-level worker functions, small explicit messages, and schema-validated values. For large arrays, evaluate shared memory or supported buffer mechanisms with explicit ownership/lifetime rules.

```python
def square(value: int) -> int:
    return value * value

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor() as pool:
        print(list(pool.map(square, [1, 2, 3])))
```

Expected output: `[1, 4, 9]`. Run as a script; interactive notebooks and different process-start methods may behave differently. Use the main guard where required by the platform/start method.

## 13. Schema-validated inter-process messaging

For services, queues, and process boundaries, prefer explicit schemas over arbitrary Python object graphs. A robust pipeline should:

1. Set a maximum message size before parsing.
2. Parse a non-executable representation (e.g., JSON, Protobuf, MessagePack).
3. Validate required fields, types, ranges, enumerations, and version.
4. Reject inconsistent values under a documented compatibility policy.
5. Apply authorization separately from validation.
6. Log failures without leaking secrets.
7. Version schemas and test old/new producer-consumer combinations.

A schema establishes shape, not sender authorization. Keep authentication, authorization, validation, and business rules distinct.

## 14. Compatibility and long-term storage

Pickle can depend on protocol/Python versions, importable module paths, class names, custom reduction/state code, third-party dependencies, and changing class semantics. It is usually a poor archival/interchange contract. If an internal pickle cache is justified, document owner, provenance, lifetime, version constraints, and invalidation strategy; regenerate it when incompatible versions change. Long-term records should use a documented schema and migration tests.

## 15. Tests that do not execute malicious payloads

Test local round trips and inspection behavior. For suspicious artifacts, test the decision/inspection workflow—never “what happens if I unpickle it.” These examples require `pytest` only for the test functions.

```python
import io
import pickle
import pickletools
import pytest

def test_local_round_trip():
    value = {"name": "job", "count": 3}
    blob = pickle.dumps(value, protocol=4)
    assert pickle.loads(blob) == value  # Only locally generated test data.

def test_pickle_disassembly_is_available():
    blob = pickle.dumps({"x": 1}, protocol=4)
    operations = list(pickletools.genops(blob))
    assert operations
    assert operations[-1][0].name == "STOP"

def test_restricted_loader_rejects_unlisted_global():
    class OnlySetUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            if (module, name) == ("builtins", "set"):
                return super().find_class(module, name)
            raise pickle.UnpicklingError("global rejected")

    # Protocol 0 encodes complex through a global/reduction reference.
    # The test rejects it by policy; it does not use a malicious payload.
    blob = pickle.dumps(complex(1, 2), protocol=0)
    with pytest.raises(pickle.UnpicklingError):
        OnlySetUnpickler(io.BytesIO(blob)).load()
```

These tests do not prove a restricted unpickler universally safe. Keep tests deterministic and never add destructive payloads to a test suite.

## 16. Threat-model checklist

- [ ] Which component creates the artifact, and can an attacker influence its bytes or object graph?
- [ ] Is it read from a shared cache, network, upload, model registry, or another tenant?
- [ ] Can a non-executable schema-based format represent the data instead?
- [ ] Is provenance authenticated before parsing? Who controls the key and signing process?
- [ ] Are byte size, nesting, array dimensions, CPU, and memory bounded?
- [ ] Are class/module references stable and reviewed?
- [ ] Does the loader run with least privilege and without unnecessary secrets/network?
- [ ] Are protocol, Python, dependency, and schema versions pinned/tested?
- [ ] Are static-analysis findings reviewed and suppressions documented?
- [ ] Is there a retention, invalidation, and migration plan?
- [ ] Can the artifact be inspected with `pickletools` without loading it?

If trust cannot be established, do not unpickle it.

## 17. Common mistakes

| Mistake | Correction |
|---|---|
| “Pickle is safe because it's binary.” | Binary encoding is not a security property; reconstruction can invoke callables. |
| “The file is signed, so it is safe.” | A MAC/signature establishes provenance/integrity under assumptions, not benign behavior. |
| “`find_class` makes pickle safe.” | It restricts global lookup but is not a universal sandbox or proof. |
| “`pickletools.dis` says it looks fine, so load it.” | Disassembly aids analysis; it is not a safety certification. |
| “`shelve` is just a database.” | It uses `dbm` plus pickle and inherits the risks and backend limits. |
| “`marshal` is stable interchange.” | It is Python-internal and version-dependent. |
| “Highest protocol is always best.” | It may break older readers; choose against compatibility requirements. |
| “A model file only contains tensors.” | Some formats can encode executable reconstruction or complex parser behavior. |
| “`weights_only=True` guarantees complete safety.” | It reduces some risks; behavior depends on PyTorch version and context. |
| “Multiprocessing serialization is free.” | Large object graphs cost CPU/memory and can fail for runtime objects. |

## 18. Exercises and answers

### Exercise 1 — Choose a format

Pick a format for (a) a public REST response, (b) a large analytical table, (c) model weights shared between teams, (d) a trusted local Python-only cache, and (e) configuration.

**Answer:** (a) JSON or a schema-backed API format with validation and limits; (b) Parquet/Arrow depending on storage and processing needs; (c) Safetensors where supported, or ONNX for portable inference, with provenance checks; (d) Pickle only for a private trusted short-lived cache with invalidation/version policy, otherwise a simpler schema format; (e) TOML or safe YAML loading followed by validation.

### Exercise 2 — Inspect, don't load

A colleague sends `model.pkl` from an unknown source. Give three actions that do not execute it and a decision before loading.

**Answer:** Verify provenance/checksum claims through a trusted channel; inspect bytes using `pickletools` and/or Fickling without `load`/`loads`; review expected artifact type and dependencies in an isolated analysis workflow. Do not load in a normal process unless trust is established; obtain non-pickle weights if possible.

### Exercise 3 — Fix a mitigation claim

Rewrite: “We HMAC-sign our pickles, so unpickling is safe.”

**Answer:** “HMAC can detect unauthorized modification when key handling and verification are trustworthy, but it cannot make a malicious authorized producer safe. Restrict artifact producers, verify before parsing, isolate where appropriate, and prefer non-executable formats across untrusted boundaries.”

### Exercise 4 — Find the hidden cost

A process pool sends a 2 GB object graph to each worker. Name two likely costs and one alternative.

**Answer:** Serialization CPU time and extra memory/copy overhead. Evaluate compact identifiers, shared data storage, or supported shared-memory/out-of-band buffers with explicit ownership/lifetime.

### Exercise 5 — Explain `find_class`

What does overriding it do, and why is it not a universal defense?

**Answer:** It can reject global references not on an allow-list. It does not eliminate resource exhaustion or prove every permitted callable/type harmless; the policy depends on the complete allowed set and pickle semantics. Prefer non-executable formats for untrusted data.

## 19. Roadmap self-checks

### 1. Why can `pickle.loads(untrusted)` run arbitrary code?

Pickle reconstructs objects from opcodes. Global lookups and reduction operations can invoke callables during reconstruction, and custom `__reduce__`/`__reduce_ex__` methods can specify reconstruction behavior. Loading is therefore not passive data parsing.

### 2. What does the restricted `Unpickler` protect against, and what does it not?

A `find_class` allow-list blocks global references not explicitly allowed and can provide defense in depth for a narrow, tested case. It does not make arbitrary pickle safe, eliminate resource-exhaustion risk, or prove every allowed reconstruction behavior harmless.

### 3. Choose a format for a trained scikit-learn model, a job-result cache, and an API payload.

- **Trained scikit-learn model:** Prefer a supported safer/non-executable model format if available. If the required workflow relies on pickle/joblib/cloudpickle, load only artifacts from a tightly controlled, authenticated, reviewed pipeline in an isolated environment—never arbitrary model downloads.
- **Job-result cache:** JSON, MessagePack, SQLite, or another schema-backed store is preferable for simple data. Pickle is only a candidate for a private, trusted, short-lived Python-only cache with invalidation and version policy.
- **API payload:** JSON or a schema-backed format such as Protobuf; validate fields, types, sizes, and version. Never use pickle as public API interchange.

No format is universally best: choose based on interoperability, schema needs, data types, trust boundary, performance, and longevity.

## 20. Glossary

- **Serialization:** Convert an in-memory value to a storable/transmittable representation.
- **Deserialization:** Reconstruct a value from a serialized representation.
- **Pickle protocol:** Versioned opcode/encoding rules for pickle.
- **Opcode:** An instruction in a pickle stream.
- **`__reduce__` / `__reduce_ex__`:** Hooks that describe object reconstruction.
- **`find_class`:** Unpickler hook for resolving global names.
- **HMAC:** Keyed message authentication code used to detect modification under a secret-key assumption.
- **`marshal`:** Python-internal serialization machinery, notably used around bytecode caches; not stable interchange.
- **`shelve`:** Dictionary-like persistence built on `dbm` and pickle.
- **Out-of-band buffer:** Buffer data transported separately from the main pickle stream, supported by protocol 5.
- **Schema validation:** Check parsed data against expected structure and semantic constraints.
- **Supply chain:** Artifacts, dependencies, build processes, registries, and publishers that deliver software/models.

## 21. Completion checklist

- [ ] I can explain `dumps`/`loads` and `dump`/`load` and their bytes/file distinction.
- [ ] I know protocol defaults are version-dependent and can choose for compatibility.
- [ ] I can explain how pickle reconstruction may invoke callables.
- [ ] I never unpickle untrusted or unauthenticated data.
- [ ] I can inspect a stream with `pickletools` without executing it.
- [ ] I understand limits of restricted unpicklers, HMAC, scanners, and sandboxing.
- [ ] I know `marshal` is not a stable interchange format.
- [ ] I understand `shelve`'s pickle, backend, concurrency, and writeback implications.
- [ ] I can choose safer data, configuration, array, and model formats.
- [ ] I understand protocol 5's buffer motivation and security limits.
- [ ] I can identify multiprocessing serialization costs and schema-validated IPC alternatives.
- [ ] I can justify the trust boundary of any serialization path I design.

## Final principle

**A serialization format is a data contract, not a trust guarantee.** Prefer explicit schemas for interchange, bound and validate inputs, verify provenance before parsing, and never unpickle untrusted or unauthenticated data.
