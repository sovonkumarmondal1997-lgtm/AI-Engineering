# Unsafe Deserialization

**Stage 1 — Programming & Computational Thinking**  
**Module 22 — Secure Python Coding**  
**Lesson 02 of 08** · Trust boundaries, safe formats, artifact provenance and controlled loading

> **Safety rule:** Never deserialize pickle or another object-capable format from an untrusted or unauthenticated source. Examples in this lesson are for defensive learning and local, self-owned labs. No unknown artifact should be loaded to “see what it does.”

## 1. Learning outcomes

By the end of this lesson, you should be able to:

1. Explain serialization and deserialization, and why some formats can invoke behavior during loading.
2. Identify risky Python loaders and choose an appropriate data format for the task.
3. Treat uploaded files, downloaded models, shared storage, caches, registries and inter-process/network messages as trust boundaries.
4. Explain the roles and limitations of `__reduce__`, restricted unpicklers, hashes, signatures, scanners and file permissions.
5. Validate data structure and resource usage after parsing—even when the format is designed not to execute code.
6. Design a model-artifact pipeline that verifies provenance before loading, validates metadata and runs with least privilege.
7. Inspect pickle opcodes with `pickletools.dis` without executing the pickle, while understanding why opcode policy checks are not a general safety proof.
8. Write a `safe_load_model(path)` policy that rejects pickle by default, verifies an approved artifact, loads a safer tensor format and validates metadata.
9. Test that untrusted or disallowed artifacts are rejected without invoking a deserializer.

## 2. Prerequisites and terminology

### Prerequisites from the roadmap

This lesson builds on:

- **Module 1.12:** `eval`/`exec` and AST allow-lists.
- **Module 1.13:** temporary files, hashing, `secrets`, subprocesses and archives.
- **Module 1.14:** pickle, Unicode, decompression and resource-exhaustion risks.
- **Modules 1.3 and 1.10:** exceptions, validation and configuration/logging.
- **Modules 1.7 and 1.16:** tests, regression tests and fuzzing.
- **Modules 1.10 and 1.18:** dependency/supply-chain awareness and artifact publishing.
- **Stage 0:** OS permissions, processes, network boundaries and isolation.

If you are not yet comfortable with file paths, exceptions, byte strings, hashes or unit tests, review those foundations before attempting the lab.

### Terms

- **Serialization:** converting an in-memory value into bytes or text that can be stored or transmitted.
- **Deserialization:** parsing that representation back into an in-memory value.
- **Object-capable format:** a format/loader combination that can reconstruct arbitrary classes, resolve global names or invoke callables while loading.
- **Gadget:** a class or function whose normal behavior can be chained by an attacker to cause an unintended effect during object reconstruction.
- **Artifact:** a stored output such as a model, dataset, package, checkpoint or feature cache.
- **Provenance:** evidence of where an artifact came from, how it was built and which identity approved it.
- **Integrity:** evidence that bytes match an expected value.
- **Authenticity:** evidence that an artifact came from a holder of a trusted identity/key.
- **Schema:** a contract describing the expected fields, types, shapes and constraints of data.
- **Sandbox:** an isolation boundary intended to limit a process's access to files, network, credentials and resources.
- **Blast radius:** the damage possible if a control fails.

## 3. Serialization versus deserialization

### 3.1 The mental model

A serializer is like a packing process: it encodes a value into a representation. A deserializer unpacks that representation. The security question is not simply “does this file look like data?” It is:

**What operations can the chosen loader perform while interpreting these bytes?**

JSON generally describes basic data values such as objects, arrays, strings, numbers, booleans and null. A pickle stream can describe Python object reconstruction steps, including references to callables and arguments. The difference is fundamental: a loader for an object-capable format may invoke behavior before your application has a chance to validate the resulting object.

### 3.2 Data-flow diagram

```text
Producer / source
      |
      v
Serialized bytes (file, HTTP response, cache, queue, model registry)
      |
      v
Trust boundary: authenticate provenance and enforce byte-size limits
      |
      v
Choose an allowed format and a constrained parser/loader
      |
      v
Reconstructed values / tensors / object graph
      |
      v
Validate schema, types, shapes, ranges, counts and business invariants
      |
      v
Application use under least privilege
```

For object-capable formats, the dangerous operation can happen **inside the loader**, before the validation step. Therefore, “load it and then check whether it looks suspicious” is too late for formats that can execute behavior during reconstruction.

### 3.3 Threat model

Consider the assets, entry points, trust assumptions and impact:

| Item | Examples |
|---|---|
| Assets | Cloud credentials, database access, source code, training data, model weights, feature data, customer records |
| Entry points | Uploaded model/config, public model hub, shared bucket, notebook artifact, cache directory, RPC message, worker queue |
| Threat actors | Malicious uploader, compromised developer machine, compromised build dependency, untrusted tenant, attacker with write access to shared storage |
| Security boundaries | Registry-to-runtime, user-to-service, producer-to-consumer, parent-to-worker process, one tenant's cache to another tenant |
| Potential impact | Code execution, credential theft, data exfiltration, altered predictions, corrupted training data, denial of service, persistent cache poisoning |

“Internal” is not a trust level. A shared bucket can be writable by several teams; an internal cache can be poisoned by another local account; a public model can be popular and still be malicious. Trust must be established through provenance, permissions and controlled production—not by location or filename.

## 4. Beginner foundation: why deserialization can execute behavior

### 4.1 Why pickle is different

Pickle is designed to reconstruct Python objects, not merely represent primitive data. During unpickling, the protocol may resolve global objects and invoke reconstruction callables. A class can define special methods such as `__reduce__` or `__setstate__` that influence reconstruction.

Conceptually, `__reduce__` can tell pickle that reconstruction should call a particular callable with particular arguments. If the stream names a dangerous callable, or a callable with dangerous side effects, loading can trigger those effects. The loader may perform the call as part of reconstructing the object.

This is why the rule is categorical: **do not unpickle data that is untrusted or unauthenticated**. Do not treat an artifact as safe because it was downloaded from a model hub, emailed by a colleague, stored in a private bucket, or produced by a familiar tool.

### 4.2 The safe demonstration boundary

This lesson does not provide a destructive pickle payload. The later regression test constructs a local fixture whose reconstruction hook would only print a marker, then proves that the policy rejects the `.pkl` file without unpickling it. To learn the mechanism safely:

1. Read about `__reduce__` in Module 1.14's pickle lesson.
2. Inspect a known, inert pickle fixture with `pickletools.dis`; this disassembles opcodes and does not unpickle the stream.
3. Study a harmless class's reduction tuple as ordinary Python data without serializing it into a payload or invoking a loader on unknown bytes.
4. In a controlled, disposable training environment, use a pre-reviewed instructor-provided fixture and a marker-file proof only if your course specifically requires it. Never execute an artifact from an unknown source.

The fixture is never passed to a pickle API; the key regression property is that a disallowed `.pkl` file is rejected before any deserializer is called.

### 4.3 The validation timing problem

For a simple data format, parsing typically creates primitive containers. Those values still require schema validation and resource controls. For object-capable formats, reconstruction can invoke code before you receive the result. This yields two separate controls:

- **Before loading:** establish provenance, restrict formats, bound file size, and choose a safe loader. Hash the exact bytes that will be parsed; checking a path and reopening it later creates a time-of-check/time-of-use (TOCTOU) gap.
- **After parsing/loading:** validate the resulting structure, tensor shapes, metadata, counts, numeric ranges and business invariants.

Post-load validation does not undo code execution that already happened. Conversely, a format that does not execute code can still carry hostile values, oversized structures or malformed tensor metadata.

## 5. Format comparison: capabilities, risks and appropriate use

“Safer” means safer for a particular purpose and loader configuration—not risk-free.

| Format / API | Capabilities and risk | Safer use | Appropriate scenarios / limits |
|---|---|---|---|
| `pickle` | Reconstructs Python objects and can invoke callables during loading | Do not load untrusted/unauthenticated data; prefer data-only formats | Trusted, controlled Python-only persistence where provenance and permissions are strong; avoid for interchange |
| `marshal` | Python-internal, version-sensitive representation that can encode code objects; loading a code object is not itself execution | Do not treat untrusted marshalled data/code as safe; never execute untrusted code objects | Interpreter internals; not a durable cross-version interchange format |
| `shelve` | Persistent mapping backed by pickle for values | Treat its database as pickle; protect its directory and never open attacker-writable shelves | Trusted local cache with strict permissions only |
| PyYAML unsafe loader (`yaml.load` with unsafe loader) | Can construct Python objects and invoke constructors | `yaml.safe_load` plus schema and resource limits | Human-authored configuration; safe loader supports a more limited set of types |
| `jsonpickle` | Encodes/reconstructs Python object graphs | Avoid for untrusted input; use plain JSON schema instead | Controlled legacy/internal interchange only with strong provenance |
| `dill`, `cloudpickle` | Can serialize functions/classes and richer Python state | Never load from untrusted sources; keep producer/consumer versions aligned | Controlled distributed computing or ephemeral trusted workflows |
| `joblib.load` | Commonly uses pickle-based mechanisms | Treat input as executable-trust material; verify provenance and permissions | Trusted scikit-learn artifacts from controlled builds only |
| `torch.load` | Historically uses pickle-based loading; behavior and defaults vary by PyTorch version and options | Prefer tensor-only formats such as `safetensors` when suitable; where applicable use `weights_only=True` and validate | Do not infer safety from a filename or a recent default; pin and review the installed version's documentation |
| `numpy.load(..., allow_pickle=True)` | Object arrays may require pickle | Use `allow_pickle=False` unless a trusted legacy artifact makes pickle unavoidable | Numeric arrays should normally be stored without object arrays |
| JSON | Represents primitive data structures; parser does not normally reconstruct arbitrary Python objects | Bound bytes/depth/counts, reject ambiguity and validate schema | API payloads and config; large/deep documents still create resource risks |
| CSV | Tabular text | Validate headers, row/column counts and types; treat spreadsheet formula interpretation separately | Flat data interchange; weak typing and dialect ambiguity |
| TOML | Typed configuration values | Strict schema and size limits after parsing | Human-readable config; parser safety does not validate meaning |
| Parquet / Arrow | Columnar typed data and metadata | Use trusted, patched parsers; validate schema, row counts, nested depth and sizes | Analytics and data lakes; native parser vulnerabilities/resource exhaustion remain possible |
| MessagePack | Compact data encoding; extensions may add application-specific semantics | Disable or constrain extension types; schema-validate decoded values | Compact service messages; configuration and extension handling matter |
| Protocol Buffers | Schema-defined wire format | Validate semantics, bounds and authorization after decoding | Typed RPC/event messages; schema does not prove trust or business validity |
| `yaml.safe_load` | Avoids arbitrary Python-object construction in normal use | Use safe loader, validate schema and bound aliases/depth/size | Configuration; safe does not mean resource-unbounded |
| `numpy.load(..., allow_pickle=False)` | Numeric arrays without object-pickle reconstruction | Keep `allow_pickle=False`; validate dimensions, dtype, file size | Numeric NumPy arrays; still parse untrusted binary data carefully |
| `safetensors` | Tensor-focused format designed not to embed arbitrary Python object reconstruction | Verify provenance, cap size, validate tensor names/shapes/dtypes and metadata | Model weights; does not prove model behavior, provenance or license |
| ONNX | Model graph interchange format | Validate model/opset and provenance; use runtime isolation and resource limits | Model deployment/interchange; graph/runtime operators and parser/runtime bugs remain relevant |
| GGUF | Model-weight/container format used by some inference ecosystems | Verify provenance and compatibility; validate metadata and load in a constrained runtime | Model distribution; format alone does not guarantee benign model behavior |

### Choosing formats by task

- **Tensor weights:** prefer `safetensors` when the model architecture/runtime supports it; ONNX can fit interoperable graph deployment after validation.
- **Feature cache:** prefer Parquet/Arrow or another data-only typed representation rather than pickled DataFrames. Protect the cache directory and validate schema.
- **User-uploaded config:** use JSON or TOML, or `yaml.safe_load`, followed by strict schema and resource validation.
- **RPC payload:** use a schema-defined protocol such as Protocol Buffers or a constrained JSON/MessagePack contract; authenticate peers and validate semantics.
- **Trusted Python-only ephemeral state:** object serialization may be convenient, but convenience is not a reason to accept artifacts from outside the trust domain.

No format eliminates all risk. Even a data-only parser can have implementation vulnerabilities; decoded data can violate business rules; numeric tensors can be enormous; and model weights can encode harmful or biased behavior without executing code during loading.

## 6. Vulnerable patterns and safe alternatives

Every unsafe loader example is marked **VULNERABLE / LAB ONLY** and paired with a defensive alternative. The lesson does not include a destructive payload; the regression lab later creates only a harmless marker-printing fixture and never deserializes it.

### 6.1 Pickle and `joblib`

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — never load untrusted or unauthenticated files.
import pickle

with open("downloaded_model.pkl", "rb") as file:
    model = pickle.load(file)
```

**Safe direction:** reject pickle at an untrusted boundary. If an old trusted workflow requires it, isolate it, authenticate the exact artifact against a trusted manifest, restrict the loader where practical, and run it with minimal privileges. These controls reduce risk; they do not turn arbitrary pickle into a safe interchange format.

```python
from pathlib import Path

ALLOWED_SUFFIXES = {".safetensors"}

def reject_object_serialization(path: Path) -> None:
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError("unsupported artifact format")
```

The extension check is only an early policy gate, not proof of file format. Verify the actual artifact structure with the format-specific library and compare its digest against a trusted allow-list.

`joblib.load()` should be treated as unsafe for untrusted inputs because its persistence mechanism is pickle-based. Do not replace `pickle.load()` with `joblib.load()` and assume the risk has disappeared.

### 6.2 `marshal`

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — do not accept untrusted marshal data; never execute a loaded code object.
import marshal
value = marshal.loads(untrusted_bytes)  # Loading a code object is not itself execution.
```

**Safe direction:** use JSON, a schema-defined protocol or a suitable data format. `marshal` is an interpreter-internal, version-sensitive representation that can encode code objects. Loading a marshalled code object does not itself execute it, but later executing an untrusted code object is unsafe. It is not a security boundary or general-purpose interchange protocol.

### 6.3 PyYAML

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — unsafe loader behavior depends on loader/version.
import yaml
value = yaml.load(untrusted_text, Loader=yaml.UnsafeLoader)
```

**Safer alternative:**

```python
import yaml

value = yaml.safe_load(untrusted_text)
```

Then validate `value` against an explicit schema and bound input bytes, nesting depth, aliases and collection sizes. Use a supported PyYAML version and confirm the API/default behavior for that version. Do not rely on an implicit default: loader defaults have changed across PyYAML releases, and explicit safe-loader selection is clearer.

### 6.4 NumPy object arrays

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — object arrays can require pickle.
import numpy as np
array = np.load("untrusted.npy", allow_pickle=True)
```

**Safe alternative for numeric arrays:**

```python
import numpy as np

array = np.load("numeric-array.npy", allow_pickle=False)
if array.ndim > 4:
    raise ValueError("unexpected array rank")
if array.size > 10_000_000:
    raise ValueError("array too large")
```

The size check shown is an application example, not a universal limit. For untrusted inputs, enforce file-size and allocation limits before or during loading too; a post-load `array.size` check may be too late to prevent a large allocation.

### 6.5 PyTorch checkpoints

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — legacy pickle-capable loading of untrusted files.
import torch
checkpoint = torch.load("untrusted-checkpoint.pt", map_location="cpu")
```

**Safer direction:** prefer a tensor-only format such as `safetensors` when available. If a supported PyTorch version and artifact shape permit it, `torch.load(..., weights_only=True)` restricts the set of objects that may be reconstructed compared with unrestricted pickle loading. It is not a universal proof of safety, and behavior/defaults are version-sensitive. Pin PyTorch, consult the documentation for the exact installed version, avoid unreviewed allow-list additions, validate the state dictionary, and load in a constrained process.

Do not assume `map_location="cpu"` makes a checkpoint safe; it controls device placement, not provenance or arbitrary loader behavior.

### 6.6 JSON and other data-only formats

A data-only format reduces code-execution risk but does not make the resulting data trusted.

```python
import json

value = json.loads(untrusted_text)
if type(value) is not dict:
    raise ValueError("expected a JSON object")
if len(value) > 100:
    raise ValueError("too many fields")
```

In production, enforce a byte limit before reading the full document, reject duplicate keys if ambiguity matters, limit nesting and collection counts, validate exact types and fields, and apply business rules. Some JSON libraries accept non-standard values such as NaN/Infinity or have parser-specific behavior; configure and test the chosen parser deliberately.

## 7. Intermediate controls

### 7.1 Provenance and trust boundaries

Before loading an artifact, establish:

- **Origin:** Which build or producer created it?
- **Identity:** Which signing identity or trusted registry account approved it?
- **Integrity:** Do the current bytes match the expected digest?
- **Authorization:** Is this producer permitted to publish this artifact for this environment?
- **Version:** Is the exact model revision or commit pinned?
- **Permissions:** Can an untrusted user replace the file, manifest, or cache entry?
- **Compatibility:** Is the artifact intended for this runtime/library version?
- **License:** Is the model or dataset license acceptable for the intended use?

A private registry is useful only if publishing permissions, review and identity controls are trustworthy. “Downloaded from an official hub” is not sufficient by itself; pin the revision and verify provenance.

### 7.2 Hashes, signatures and HMACs

A cryptographic hash such as SHA-256 maps bytes to a digest. Comparing the computed digest with a **trusted expected digest** detects accidental or malicious byte changes relative to that expectation.

A hash stored beside the artifact in the same attacker-writable location is not an authenticity guarantee: an attacker can replace both. A hash alone proves consistency only relative to a trusted expected hash.

A digital signature can authenticate an artifact or manifest if the signing key, identity verification, key protection and trust policy are secure. It does not prove that the signed artifact is benign. A compromised or malicious trusted producer can sign a malicious artifact.

An HMAC uses a shared secret key to authenticate bytes to parties that possess that key. It is not a defence against a malicious trusted producer that knows the key and intentionally signs unsafe content. HMAC also requires secure key distribution and rotation. Never hard-code signing keys into artifacts or expose them to untrusted build steps.

The roadmap names SHA-256, Sigstore, minisign and Ed25519 via `cryptography` as relevant mechanisms. Choose one supported, operationally managed approach; do not invent a signature protocol.

### 7.3 Restricted unpicklers: useful but not a general safety proof

A custom `pickle.Unpickler` can override `find_class()` to reject global names or permit only a small set of known classes. This can block some common reconstruction paths, but it is difficult to define a complete safe policy for arbitrary Python object graphs. Allowed classes may have dangerous behavior; opcodes and reconstruction semantics are subtle; and resource exhaustion remains possible.

**VULNERABLE / LAB ONLY:**

```python
# VULNERABLE / LAB ONLY — a restricted loader is not a general safe loader.
import pickle

class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name: str):
        if module == "builtins" and name in {"dict", "list", "str", "int"}:
            return super().find_class(module, name)
        raise pickle.UnpicklingError("global is not allowed")
```

This snippet illustrates the policy hook, not a recommendation to accept arbitrary pickle. Even if the allow-list is carefully chosen, do not use it to justify loading untrusted pickles in a production service. The robust default is to reject pickle outside the trusted artifact domain and use a data-only format. If legacy loading is unavoidable, isolate it and document the residual risk.

### 7.4 Inspecting pickle opcodes without loading

`pickletools.dis()` disassembles pickle opcodes; it does not execute the pickle stream. It is useful for offline analysis of a known artifact, but disassembly is not a complete proof that a stream is safe.

```python
import pickletools
from pathlib import Path

def inspect_pickle(path: Path, *, max_bytes: int = 1_000_000) -> None:
    # Read a bounded amount from one opened file; a prior stat() would race.
    with path.open("rb") as file:
        data = file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("pickle exceeds inspection size limit")
    pickletools.dis(data)
```

Run this only on a local analysis copy, under resource limits if the source is untrusted. `pickletools.dis` avoids unpickling but still parses attacker-controlled bytes; apply size/time controls and keep Python patched. Do not copy a disassembled artifact into a loader as a “safe” result.

The roadmap suggests policy checks for `GLOBAL`/`STACK_GLOBAL` references such as `os.system`, `subprocess`, `builtins.eval/exec/__import__`, `posix` and `socket`. Such checks can be useful as a scanner signal or admission heuristic, but deny-listing names misses alternate paths, permitted classes with dangerous behavior and resource attacks. A static policy checker is not a general-purpose safety guarantee.

### 7.5 Scanner tools

Tools named in the roadmap include `fickling`, ModelScan and `picklescan`. They can help identify suspicious pickle structures or known patterns. Use them as defence-in-depth:

- Pin and update scanner versions.
- Preserve scan results and artifact digests for audit.
- Fail closed for policy-defined high-risk artifacts.
- Do not treat a clean scan as permission to load an untrusted pickle.
- Keep the actual format policy and sandbox in place.

Scanners have false negatives, may not model every runtime behavior, and cannot prove that a model is trustworthy or licensed.

### 7.6 Validate after safe parsing

Even JSON, safe YAML, Parquet, Arrow, MessagePack, Protocol Buffers and safetensors can yield untrusted structure. Validate:

- Exact types and allowed fields; reject unexpected fields where appropriate.
- Maximum document bytes, nesting depth, key count, list length and string length.
- Tensor names, rank, shape, dtype and total element/byte counts.
- Numeric finiteness and permitted ranges.
- Model architecture/config compatibility and expected tensor names.
- Data version, schema version and business invariants.

For example, a tensor with an unexpected shape may cause a failure, memory pressure or an unsafe downstream assumption even though no Python code was executed during parsing.

### 7.7 XML, YAML, JSON and archive resource risks

- **XML:** external entities can cause file/network access, and entity expansion can exhaust resources. Use a hardened parser such as `defusedxml`, keep it updated, and limit input size/depth.
- **YAML:** aliases, deeply nested structures and very large collections can consume CPU/memory. `safe_load` addresses arbitrary Python-object construction, not all resource-exhaustion risks.
- **JSON:** deeply nested or huge objects, huge integers, duplicate keys and parser differences can cause expensive processing or ambiguity. Bound and validate.
- **ZIP/tar:** archives can contain traversal paths, links, huge expansion ratios or excessive member counts. Archive extraction and path containment are covered in Lesson 03 and Module 1.14's compression lesson. Do not duplicate those chapters here; reject suspicious members and enforce size/count/ratio limits before extraction.

## 8. Advanced artifact pipeline: build → verify → controlled load → validate → isolate

### 8.1 Pipeline stages

```text
Build in controlled CI
   |
   v
Record source revision, dependencies, config and model license
   |
   v
Produce artifact + schema/versioned metadata
   |
   v
Compute digest; sign manifest using protected build identity
   |
   v
Publish to registry with restricted write access / immutable versions
   |
   v
At load: verify expected digest/signature and pinned revision
   |
   v
Enforce format policy; reject pickle outside trusted domain
   |
   v
Load in constrained worker with no unnecessary credentials/network
   |
   v
Validate metadata, tensor schema, shapes, sizes and invariants
   |
   v
Promote result only after checks; record audit evidence
```

**Build:** use reviewed source and pinned dependencies; separate untrusted pull-request jobs from signing credentials.

**Hash/sign:** generate a manifest that binds the digest to model identity, revision, format, metadata schema and build identity. Protect the signing key in a dedicated service or trusted workflow.

**Publish:** use a registry with access controls, immutable versioning where possible, audit logs and a documented promotion path. Do not let an arbitrary training job overwrite production artifacts.

**Verify:** compare against a trusted allow-list or verify a signature under a known trust policy before parsing the model file. Validate the manifest itself and prevent rollback to a disallowed revision.

**Controlled load:** select an allowed format, impose byte/resource limits, and use a low-privilege process.

**Validate:** verify expected tensor names/shapes/dtypes and metadata schema. A successful load is not the same as a valid or authorized model.

**Audit:** record artifact digest, pinned revision, validation result, loader/runtime versions and approver/build identity. Avoid logging credentials or sensitive training data.

### 8.2 Safe metadata validation

A metadata schema should be versioned and deliberately small. Example fields include `model_id`, `revision`, `format`, `architecture`, `tensor_count` and a schema version. Reject missing or unexpected fields, wrong exact types, unrecognized architectures and unreasonable counts. Do not dynamically import a class named by untrusted metadata.

```python
def validate_metadata(metadata: object) -> dict[str, object]:
    if type(metadata) is not dict:
        raise ValueError("metadata must be an object")

    required = {"model_id", "revision", "format", "tensor_count"}
    if set(metadata) != required:
        raise ValueError("unexpected metadata fields")

    if type(metadata["model_id"]) is not str or not 1 <= len(metadata["model_id"]) <= 128:
        raise ValueError("invalid model_id")
    if type(metadata["revision"]) is not str or not 1 <= len(metadata["revision"]) <= 128:
        raise ValueError("invalid revision")
    if metadata["format"] != "safetensors":
        raise ValueError("unsupported format")
    count = metadata["tensor_count"]
    if type(count) is not int or not 0 <= count <= 100_000:
        raise ValueError("invalid tensor_count")
    return metadata
```

This is an illustrative application contract, not a universal metadata schema. In a real system, bind metadata to the same signed manifest as the artifact; otherwise an attacker might swap metadata independently.

### 8.3 The `safe_load_model(path)` exercise

The roadmap asks for a function that:

1. Checks a signature/hash allow-list.
2. Refuses pickle formats unless an explicit trust flag is present **and** a sandbox flag is active.
3. Loads `safetensors`.
4. Validates metadata with a schema.
5. Includes tests proving a malicious pickle fixture is rejected, never executed.

For production, the recommended policy is stronger than the exercise's legacy escape hatch: **do not provide an in-process override that loads arbitrary pickle merely because two flags are set**. An explicit flag does not establish trust, and a boolean cannot prove the process is sandboxed. If a legacy exception is unavoidable, route it to a separately deployed, reviewed, low-privilege worker with externally enforced isolation and an approval workflow. Keep the default application loader limited to approved data-only formats.

## 9. Sandboxing and distributed execution

### 9.1 Layers and what they do

| Control | Helps prevent/limit | Does not guarantee |
|---|---|---|
| Separate OS user | Access to other users' files/processes | Safety if that user has broad credentials or permissions |
| No network / egress policy | Exfiltration and access to internal services | No local damage or covert channels through allowed outputs |
| Read-only filesystem | Persistence and modification of mounted files | No memory/CPU exhaustion or reads of permitted files |
| Container | Namespaces and resource/environment separation | Strong isolation against every kernel/runtime vulnerability |
| seccomp / AppArmor / SELinux | Restrict selected syscalls or access patterns | Correct policy or complete containment |
| CPU/memory/PID/disk quotas and timeouts | Bound many denial-of-service effects | All native-library bugs or every uninterruptible operation |
| Ephemeral VM / stronger micro-VM boundary | Stronger separation for risky processing | Absolute security; configuration and hypervisor remain relevant |
| Restricted unpickler | Blocks some disallowed global lookups | Arbitrary pickle safety or resource safety |
| Hash/signature verification | Integrity/provenance under a trusted policy | Benign behavior of a correctly signed artifact |
| Scanner | Detects known suspicious patterns | Proof that a clean artifact is safe |

Sandboxing is defence-in-depth, not permission to load an untrusted pickle in the main application process. If risky legacy loading is unavoidable, use a separate worker with dropped privileges, no network, read-only mounts, tight resource limits and an ephemeral environment. Return results over a typed, data-only channel such as JSON or Arrow rather than pickle.

### 9.2 `multiprocessing`, `concurrent.futures` and distributed systems

Python's multiprocessing mechanisms commonly use pickle to transfer objects between processes. A parent and child under one operator's control may form a trusted channel, but that assumption fails if network listeners, sockets, worker queues or job submission interfaces are exposed to untrusted clients.

- Do not expose internal multiprocessing listeners or worker ports to untrusted networks.
- Authenticate peers and use TLS where communication crosses trust boundaries.
- `multiprocessing.connection` supports an `authkey` mechanism; configure it securely and understand its trust model. It is not a replacement for network isolation or a complete modern transport-security design.
- Dask, Ray and Spark deployments need their own authentication, TLS, network isolation and code-execution security model. Pickle on the wire is a significant boundary; consult the platform's security guidance and keep worker interfaces private.
- Prefer typed messages and data-only formats at trust boundaries.
- Do not send secrets or privileged live objects to workers that do not need them.

### 9.3 Caches are attack surfaces

Examples from the roadmap include `joblib.Memory`, `diskcache`, on-disk `functools`-related caches, `__pycache__`, `shelve` and `dbm`.

Controls:

- Use per-user or per-service cache directories with restrictive permissions.
- Do not use world-writable cache paths for serialized objects.
- Prevent lower-trust users/jobs from replacing cache entries consumed by higher-privilege processes.
- Include trusted keys/versions in cache identity; verify integrity where appropriate.
- Use atomic writes and avoid partially written artifacts being consumed.
- Treat cache contents as untrusted if the producer or storage permissions are uncertain.
- Prefer data-only cache representations for values that cross trust boundaries.
- Remember that bytecode caches and cache metadata also need appropriate ownership and update controls.

A digest stored inside the same writable cache does not defend against an attacker who can replace both data and digest.

### 9.4 Incident scenarios and response

**Scenario A — downloaded fine-tuned model:** A data scientist downloads a pickle checkpoint from a public hub and loads it on a laptop with cloud credentials. The artifact's popularity does not establish trust.

**Scenario B — shared bucket:** A training job writes to a shared bucket; another principal can replace an artifact later consumed by a production worker.

**Scenario C — poisoned feature cache:** A compromised development machine writes a serialized cache object that a privileged batch job later loads.

**Immediate response if compromise is suspected:**

1. Stop loading the affected artifact and isolate the worker/host as appropriate.
2. Preserve the artifact, digest, source URL/revision, registry audit logs, process logs and relevant timestamps.
3. Revoke/rotate credentials that may have been exposed; do not assume deleting the artifact reverses a leak.
4. Identify all consumers, caches and derived artifacts that may have been affected.
5. Rebuild from a known-good source in a clean environment; verify the build identity and provenance.
6. Restore from immutable or trusted versions, invalidate poisoned caches and restrict the write path.
7. Add a regression test and update the artifact admission policy.
8. Record the timeline, impact, root cause and preventive actions.

The roadmap also calls for awareness of analogous ecosystem risks: Java serialization, PHP `unserialize`, and the obsolete .NET `BinaryFormatter` all illustrate the broader principle that object reconstruction can cross into behavior.

## 10. Hands-on lab: safe model-loading policy

### 10.1 Lab scope and dependencies

Use only local test files and a self-owned workspace. Do not download unknown checkpoints and do not attempt to inspect them by loading. This lab intentionally does **not** create or execute a malicious pickle.

Target Python: **3.11+**. The policy tests use only the standard library and pytest. The optional real tensor-loading adapter uses `safetensors` and NumPy.

```bash
python -m venv .venv
# Activate .venv for your operating system.
python -m pip install --upgrade pip
python -m pip install pytest
# Optional for the tensor adapter:
python -m pip install safetensors numpy
```

### 10.2 Design requirements

Implement `safe_load_model(path)` so that it:

- Rejects all formats except `.safetensors` before invoking a deserializer.
- Requires a digest from a trusted allow-list/manifest and checks SHA-256 before loading.
- Enforces a maximum artifact byte size.
- Validates a separate metadata document against a strict schema and verifies that it is bound to the trusted manifest in production.
- Loads tensors with a safetensors reader only after the checks pass.
- Validates tensor count, names, shapes and dtypes after loading.
- Never silently falls back to pickle, `joblib`, `torch.load` or NumPy object loading.
- Runs in a low-privilege, resource-limited worker in production.

A digest argument supplied by the same untrusted request as the artifact is not trusted provenance. In production, the expected digest and metadata binding must come from a protected registry or verified signature.

### 10.3 Runnable policy layer and regression tests

Save the following as `safe_model_policy.py`. This teaching policy reads bounded bytes once, verifies the digest of the exact artifact bytes passed to the parser, and verifies the metadata digest as well. The expected digests must come from a protected, verified manifest—not from the same untrusted request as the files. This avoids hashing a path and later reopening it for deserialization.

```python
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

MAX_ARTIFACT_BYTES = 512 * 1024 * 1024
MAX_METADATA_BYTES = 64 * 1024
MAX_TENSORS = 100_000
MAX_RANK = 8
MAX_ELEMENTS = 64_000_000
ALLOWED_DTYPES = {"bool", "uint8", "int8", "int16", "int32", "int64", "float16", "float32", "float64"}

def read_bounded(path: Path, *, max_bytes: int) -> bytes:
    with path.open("rb") as file:
        data = file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("file exceeds size limit")
    return data

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate metadata key")
        result[key] = value
    return result

def parse_metadata(raw: bytes) -> dict[str, object]:
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("invalid metadata JSON") from exc
    if type(value) is not dict:
        raise ValueError("metadata must be an object")
    required = {"model_id", "revision", "format", "tensor_count", "tensor_schema"}
    if set(value) != required:
        raise ValueError("unexpected metadata fields")
    for field in ("model_id", "revision"):
        item = value[field]
        if type(item) is not str or not 1 <= len(item) <= 128:
            raise ValueError(f"invalid {field}")
    if value["format"] != "safetensors":
        raise ValueError("unsupported metadata format")
    count, schema = value["tensor_count"], value["tensor_schema"]
    if type(count) is not int or not 1 <= count <= MAX_TENSORS:
        raise ValueError("invalid tensor_count")
    if type(schema) is not dict or len(schema) != count:
        raise ValueError("tensor schema/count mismatch")
    for name, spec in schema.items():
        if type(name) is not str or not 1 <= len(name) <= 256:
            raise ValueError("invalid tensor name")
        if type(spec) is not dict or set(spec) != {"dtype", "shape"}:
            raise ValueError("invalid tensor schema entry")
        if type(spec["dtype"]) is not str or spec["dtype"] not in ALLOWED_DTYPES:
            raise ValueError("unsupported tensor dtype")
        shape = spec["shape"]
        if type(shape) is not list or not 1 <= len(shape) <= MAX_RANK:
            raise ValueError("invalid tensor rank")
        elements = 1
        for dim in shape:
            if type(dim) is not int or not 1 <= dim <= MAX_ELEMENTS:
                raise ValueError("invalid tensor dimension")
            elements *= dim
            if elements > MAX_ELEMENTS:
                raise ValueError("tensor element limit exceeded")
    return value

def validate_tensors(tensors: object, metadata: dict[str, object]) -> dict[str, Any]:
    if type(tensors) is not dict:
        raise ValueError("tensor loader returned an unexpected object")
    schema = metadata["tensor_schema"]
    assert type(schema) is dict  # Internal invariant after metadata validation.
    if set(tensors) != set(schema):
        raise ValueError("tensor names do not match metadata")
    total_bytes = 0
    for name, tensor in tensors.items():
        spec = schema[name]
        if not hasattr(tensor, "shape") or not hasattr(tensor, "dtype") or not hasattr(tensor, "nbytes"):
            raise ValueError("tensor is missing shape/dtype/size metadata")
        if tuple(tensor.shape) != tuple(spec["shape"]):
            raise ValueError("tensor shape mismatch")
        if str(tensor.dtype) != spec["dtype"]:
            raise ValueError("tensor dtype mismatch")
        if type(tensor.nbytes) is not int or not 0 < tensor.nbytes <= MAX_ARTIFACT_BYTES:
            raise ValueError("tensor byte-size limit exceeded")
        total_bytes += tensor.nbytes
        if total_bytes > MAX_ARTIFACT_BYTES:
            raise ValueError("total tensor byte-size limit exceeded")
    return tensors

def safe_load_model(
    path: Path,
    metadata_path: Path,
    *,
    trusted_sha256: str,
    trusted_metadata_sha256: str,
    load_safetensors: Callable[[bytes], Any],
) -> dict[str, Any]:
    """Load allow-listed safetensors bytes; expected digests come from a trusted manifest."""
    if path.suffix.lower() != ".safetensors":
        raise ValueError("only safetensors artifacts are allowed")
    for digest in (trusted_sha256, trusted_metadata_sha256):
        if type(digest) is not str or len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
            raise ValueError("invalid trusted SHA-256 digest")

    artifact_bytes = read_bounded(path, max_bytes=MAX_ARTIFACT_BYTES)
    if sha256_bytes(artifact_bytes).lower() != trusted_sha256.lower():
        raise ValueError("artifact digest mismatch")
    metadata_bytes = read_bounded(metadata_path, max_bytes=MAX_METADATA_BYTES)
    if sha256_bytes(metadata_bytes).lower() != trusted_metadata_sha256.lower():
        raise ValueError("metadata digest mismatch")
    metadata = parse_metadata(metadata_bytes)
    # The parser receives the exact bytes whose digest was checked above.
    return validate_tensors(load_safetensors(artifact_bytes), metadata)
```

The policy code is a teaching skeleton, not a production-complete verifier. It still needs a reviewed signature/manifest verifier, rollback policy, OS-level isolation and concurrency-aware memory limits. The callback must use only the approved safetensors parser. Tensor shape/size checks run after parsing, so external memory limits and a reviewed preflight strategy remain necessary for high-risk or large artifacts.

Save the following as `test_safe_model_policy.py`:

```python
import hashlib
import json
import pickle
import pytest
import safe_model_policy as policy
from safe_model_policy import safe_load_model

def digest(data):
    return hashlib.sha256(data).hexdigest()

def write_metadata(path, *, count=1):
    value = {
        "model_id": "demo-model", "revision": "rev-001", "format": "safetensors",
        "tensor_count": count,
        "tensor_schema": {"weight": {"dtype": "float32", "shape": [2, 2]}},
    }
    path.write_text(json.dumps(value), encoding="utf-8")

class FakeTensor:
    shape = (2, 2)
    dtype = "float32"
    nbytes = 16

def setup_files(tmp_path):
    artifact = tmp_path / "model.safetensors"
    raw = b"placeholder bytes; not a real safetensors file"
    artifact.write_bytes(raw)
    metadata = tmp_path / "metadata.json"
    write_metadata(metadata)
    return artifact, metadata, raw

def call_policy(artifact, metadata, loader):
    return safe_load_model(
        artifact, metadata,
        trusted_sha256=digest(artifact.read_bytes()),
        trusted_metadata_sha256=digest(metadata.read_bytes()),
        load_safetensors=loader,
    )

# VULNERABLE / LAB ONLY fixture builder: this creates bytes only. Never unpickle them.
class HarmlessMarkerOnLoad:
    def __reduce__(self):
        # If unpickled, this would only print a marker; this test never unpickles it.
        return (print, ("PICKLE_FIXTURE_WAS_EXECUTED",))

def test_rejects_pickle_before_loader(tmp_path, capsys):
    artifact = tmp_path / "untrusted.pkl"
    artifact.write_bytes(pickle.dumps(HarmlessMarkerOnLoad()))
    metadata = tmp_path / "metadata.json"
    write_metadata(metadata)
    calls = []
    with pytest.raises(ValueError, match="only safetensors"):
        call_policy(artifact, metadata, lambda data: calls.append(data))
    assert calls == []
    assert capsys.readouterr().out == ""  # The fixture was never deserialized.

def test_rejects_artifact_digest_mismatch_before_loader(tmp_path):
    artifact, metadata, _ = setup_files(tmp_path)
    with pytest.raises(ValueError, match="artifact digest mismatch"):
        safe_load_model(artifact, metadata, trusted_sha256="0" * 64,
            trusted_metadata_sha256=digest(metadata.read_bytes()),
            load_safetensors=lambda data: pytest.fail("loader must not run"))

def test_rejects_metadata_digest_mismatch_before_loader(tmp_path):
    artifact, metadata, _ = setup_files(tmp_path)
    with pytest.raises(ValueError, match="metadata digest mismatch"):
        safe_load_model(artifact, metadata, trusted_sha256=digest(artifact.read_bytes()),
            trusted_metadata_sha256="0" * 64,
            load_safetensors=lambda data: pytest.fail("loader must not run"))

def test_rejects_oversized_artifact_before_loader(tmp_path, monkeypatch):
    artifact, metadata, _ = setup_files(tmp_path)
    monkeypatch.setattr(policy, "MAX_ARTIFACT_BYTES", 8)
    with pytest.raises(ValueError, match="file exceeds size limit"):
        call_policy(artifact, metadata, lambda data: pytest.fail("loader must not run"))

def test_loader_receives_exact_verified_bytes(tmp_path):
    artifact, metadata, raw = setup_files(tmp_path)
    seen = []
    result = call_policy(artifact, metadata, lambda data: seen.append(data) or {"weight": FakeTensor()})
    assert seen == [raw]
    assert set(result) == {"weight"}

def test_rejects_tensor_schema_count_mismatch_before_loader(tmp_path):
    artifact, metadata, _ = setup_files(tmp_path)
    write_metadata(metadata, count=2)
    with pytest.raises(ValueError, match="tensor schema/count mismatch"):
        call_policy(artifact, metadata, lambda data: pytest.fail("loader must not run"))

def test_rejects_duplicate_metadata_keys(tmp_path):
    artifact, metadata, _ = setup_files(tmp_path)
    metadata.write_text('{"model_id":"a","model_id":"b","revision":"r",'
        '"format":"safetensors","tensor_count":1,'
        '"tensor_schema":{"weight":{"dtype":"float32","shape":[2,2]}}}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate metadata key"):
        call_policy(artifact, metadata, lambda data: pytest.fail("loader must not run"))

def test_rejects_tensor_shape_mismatch(tmp_path):
    artifact, metadata, _ = setup_files(tmp_path)
    class WrongShape(FakeTensor):
        shape = (4,)
    with pytest.raises(ValueError, match="tensor shape mismatch"):
        call_policy(artifact, metadata, lambda data: {"weight": WrongShape()})
```

Run the tests in the isolated environment:

```bash
python -m pytest -q
```

**Expected observations (not a claim of execution):** a `.pkl` file, digest mismatch, duplicate metadata key or schema/count mismatch is rejected before the tensor callback; the callback receives the exact verified artifact bytes; tensor shape mismatch is rejected after parsing. These tests use placeholder bytes and a fake tensor, so they test policy ordering/schema logic, not actual safetensors parsing.

For an integration test, create a small benign tensor file using the pinned safetensors library, create a trusted test manifest, pass the verified bytes to its bytes-based loader, and verify names, shapes and dtypes. Never substitute an unknown pickle fixture or call a pickle-capable loader.

### 10.4 Optional safetensors adapter sketch

The exact API depends on the selected framework. For a NumPy-based adapter, the following illustrates the boundary; keep the artifact policy above and pin/test the library version:

```python
from safetensors.numpy import load

def load_tensor_bytes(data: bytes):
    # Receives the exact bytes whose digest safe_load_model verified.
    return load(data)
```

Pass `load_tensor_bytes` as the `load_safetensors` callback. Confirm that the pinned `safetensors` version exposes this bytes-based `load` API; if your chosen binding differs, preserve the key property that the parser consumes the exact verified bytes rather than reopening an attacker-mutable path. Post-load schema checks do not replace external memory limits or preflight checks for tensor allocation sizes.

### 10.5 Exercise extension: signed manifests

Extend the lab with a manifest containing artifact SHA-256, metadata SHA-256, model ID, pinned revision, format, build identity and schema version. Verify the signature using a vetted library and a public key pinned through a trusted deployment configuration. Add tests for:

- Modified artifact bytes.
- Modified metadata bytes.
- Invalid signature.
- Unknown signing key.
- Disallowed or rolled-back revision.
- Unsupported format such as `.pkl`.
- Oversized artifact and metadata.
- Wrong tensor count, shape or dtype.
- Missing or extra metadata fields.

Do not put the private signing key in the repository or in the same writable bucket as the artifact. A test using a fake digest proves code paths, not cryptographic authenticity; use a vetted signature library for signature tests.

## 11. Testing strategy and security review

### 11.1 Test properties

Test the properties of the loading boundary, not just that a helper was called:

- Unsupported formats are rejected before deserializer invocation.
- Digest/signature failures stop the pipeline before parsing.
- Metadata is strict and bound to the same trusted manifest.
- The allowed loader is the only deserializer used.
- Oversized input is rejected before reading or allocating excessively.
- Tensor metadata matches the expected schema and application contract.
- Errors are generic to callers and diagnostic details are access-controlled.
- Tests do not need to execute malicious code to prove a disallowed artifact is rejected.

### 11.2 Malicious fixture policy

The roadmap requests a malicious pickle fixture that must be rejected, never executed. The lab constructs a deliberately small fixture whose reconstruction hook would only print a marker, then proves the policy rejects the `.pkl` path before any deserializer callback; the fixture is never unpickled. Do not replace this with a destructive payload or pass it to `pickle.load`, `joblib.load`, unrestricted `torch.load` or another pickle-capable loader.

### 11.3 Fuzzing and malformed data

Fuzz the parsers and validators with bounded input sizes. Include malformed headers, unknown metadata keys, duplicate JSON keys, deep nesting, huge arrays, invalid UTF-8, invalid tensor shapes and incorrect lengths. Fuzzing can find parser crashes and invariant violations but cannot prove safety. Run fuzzers under time and memory limits; do not fuzz an unrestricted pickle loader with attacker-controlled artifacts.

### 11.4 Static and dependency checks

The roadmap names Bandit, Ruff security rules, `pip-audit`, secret scanners and optional Semgrep. These tools can detect risky loader calls, known vulnerable dependencies and accidentally committed secrets. Use them in CI with reviewed findings and an exception process. A clean scanner result does not prove an artifact is safe.

### 11.5 Review checklist

1. Is the source trusted by identity and policy, or merely “internal”?
2. Can an untrusted principal replace the artifact, metadata, hash or cache entry?
3. Does any code path call `pickle`, `joblib.load`, unsafe YAML, `marshal`, `dill`, `cloudpickle`, object-array loading or a pickle-capable framework loader?
4. Is the exact format allow-listed and checked before deserialization?
5. Is the expected digest/signature anchored in a trusted manifest or key policy?
6. Are signing credentials separated from untrusted build/test steps?
7. Are library versions, model revisions and licenses recorded and pinned?
8. Are file size, nesting, tensor shape, element count, CPU, memory and time bounded?
9. Is the worker isolated with no unnecessary network, secrets or write access?
10. Is the resulting structure validated against a schema and business invariants?
11. Are the artifact and metadata linked by a trusted manifest?
12. Do tests prove rejection occurs before the loader is called?

## 12. Common mistakes

1. **Calling `pickle.load()` because the file came from a colleague or model hub.** Provenance and trust must be established; location and popularity are not security controls.
2. **Using `yaml.load()` without an explicit safe loader.** Defaults are version-sensitive. Use `yaml.safe_load` and validate the result.
3. **Treating a private bucket or internal cache as trusted.** Permissions and producer identities may be broader than expected; protect and audit write access.
4. **Believing a hash proves authenticity by itself.** A hash must be compared with a trusted expected digest; an attacker who can replace both data and hash defeats that check.
5. **Believing a signature makes the artifact benign.** A malicious or compromised trusted signer can sign a malicious artifact. Signatures establish provenance under a trust policy, not harmlessness.
6. **Relying solely on scanners.** Scanners miss patterns and cannot prove all runtime behavior safe. Enforce a format policy and isolate risky processing.
7. **Assuming a restricted unpickler makes arbitrary pickle safe.** Class behavior, reconstruction semantics and resource exhaustion remain difficult to bound. Prefer data-only formats.
8. **Assuming `torch.load(..., map_location="cpu")` is a security control.** Device placement is not a provenance check or a guarantee against unsafe deserialization.
9. **Validating only after loading.** A dangerous reconstruction may already have executed. Authenticate and enforce format policy before loading.
10. **Assuming safe formats require no validation.** Safe parsing does not establish schema correctness, authorization, bounded resource usage or benign model behavior.
11. **Treating a model's weights as the whole model.** Architecture code, custom operators, preprocessing and runtime dependencies can introduce separate risks.
12. **Ignoring caches and inter-process communication.** They often hide serialization boundaries that are not obvious from the public API.
13. **Assuming a container alone guarantees containment.** Kernel, runtime, mounted secrets, network and resource configuration still matter.
14. **Treating a boolean `--i-trust-this` flag as a sandbox.** A flag is an assertion, not an isolation boundary. Enforce isolation outside the process and keep unsafe loading exceptional.

## 13. Self-check questions and answer key

Answer these before reviewing the explanations.

### Questions

1. Why can deserializing a pickle execute behavior before the application validates the returned object?
2. Choose formats for (a) tensor weights, (b) a feature cache, (c) a user-uploaded configuration and (d) an RPC payload. Justify each choice.
3. Why is HMAC-signing a pickle not a defence against a malicious trusted producer?
4. What does `pickletools.dis()` do, and why is disassembly not proof of safety?
5. What can a restricted `Unpickler.find_class()` block? What does it fail to guarantee?
6. Explain the difference between a hash, a signature and provenance.
7. Why are internal shared storage and caches part of the threat model?
8. Why does `numpy.load(..., allow_pickle=False)` still need size and schema controls?
9. What is the purpose of `torch.load(..., weights_only=True)`, and why must its behavior be checked against the installed PyTorch version?
10. Name four sandbox controls and one residual risk for each.
11. Design the stages of a safe model-artifact pipeline from build to runtime.
12. How can a regression test prove a disallowed pickle is rejected without executing it?
13. What are the main risks in `multiprocessing` or a distributed worker that uses pickle?
14. Why should model license, pinned revision and metadata schema be part of the artifact review?

### Answer key

1. Pickle can encode object reconstruction steps and callable references; the loader may invoke them while rebuilding the object graph. Post-load validation happens after those operations.
2. (a) Prefer `safetensors` where supported or validated ONNX for a model graph; (b) Parquet/Arrow for typed feature data; (c) JSON/TOML or `yaml.safe_load` with schema and limits; (d) Protocol Buffers or a constrained JSON/MessagePack schema. In every case, validate semantics and authenticate the communication/artifact as required.
3. A producer that knows the shared HMAC key can generate a valid MAC for malicious bytes. HMAC authenticates possession of the key, not the benevolence of the signer.
4. `pickletools.dis()` parses and displays opcodes without unpickling. It is still a parser of untrusted bytes, and manual review/pattern checks cannot cover all semantics, class behavior or resource attacks.
5. It can reject selected global lookups and allow only a narrow set. It does not establish general pickle safety, eliminate dangerous behavior in allowed classes, or prevent resource exhaustion.
6. A hash fingerprints bytes; a signature authenticates a message under a trusted key/identity policy; provenance records the origin/build/approval chain. A hash is only meaningful against a trusted expected value.
7. A lower-trust user/job may poison a cache or replace an artifact consumed by a higher-privilege process. “Internal” describes location, not who can write it or whether it is authentic.
8. Parsing can still allocate large arrays or produce unexpected rank, dtype, shape or values. Bound input and validate the resulting structure; pre-load limits matter when allocation itself is risky.
9. `weights_only=True` narrows the kinds of objects that can be reconstructed in supported PyTorch versions. It is not a universal guarantee; defaults and supported behavior are version-sensitive, so pin versions, consult exact documentation and validate outputs.
10. Examples: no network limits exfiltration but may not prevent local damage; read-only filesystem limits persistence but not CPU exhaustion; low-privilege user limits file access but may still hold useful credentials; resource quotas limit some denial-of-service behavior but do not remove parser vulnerabilities.
11. Build from reviewed source and pinned dependencies; create artifact/metadata; hash and sign a manifest with protected identity; publish to restricted immutable registry; verify signature/digests/revision; enforce format allow-list; load in a constrained worker; validate schema/tensors; record audit evidence.
12. Give the policy function a `.pkl` path and inject a loader callback that records calls or fails if invoked. Assert the policy raises before the callback runs. The test does not need to unpickle any bytes.
13. Pickle can be used to transfer objects across process/network boundaries. Exposed worker listeners, unauthenticated clients or weak network isolation can let an attacker supply serialized data; use authentication, TLS where appropriate, network controls and typed data-only messages.
14. Pinned revision and provenance help establish which artifact was reviewed; schema validation ensures expected structure; licensing determines whether use/distribution is permitted. None alone proves the model is safe, but omitting them weakens operational control.

## 14. Completion checklist and next lesson

- [ ] I can explain serialization versus deserialization and identify the loader as a trust boundary.
- [ ] I know why `pickle`, `marshal`, `shelve`, unsafe YAML, `jsonpickle`, `dill`, `cloudpickle`, `joblib`, pickle-capable PyTorch loading and NumPy object arrays are unsafe for untrusted input.
- [ ] I can choose a data-only format appropriate to tensors, configs, analytics data and RPC messages.
- [ ] I understand the difference between hashes, HMACs, signatures, provenance and benign behavior.
- [ ] I can explain the limits of restricted unpicklers, opcode policy checks and scanners.
- [ ] I validate schema, types, shapes, counts, resource limits and business invariants after safe parsing.
- [ ] I can describe the build → sign → publish → verify → controlled load → validate → isolate pipeline.
- [ ] I understand cache permissions, worker/network boundaries and sandbox residual risks.
- [ ] I can test that disallowed formats are rejected before a deserializer is called.
- [ ] I have considered model revision, license, metadata schema and incident response in the artifact workflow.

### What to learn next

Continue in roadmap order with **Lesson 03 — `03-path-traversal-and-safe-file-handling.md`**. It expands the file-handling and archive-extraction risks mentioned here, including traversal, symlinks, safe temporary files, upload handling and archive member validation. This lesson intentionally does not duplicate that chapter.

---

## Version and source notes

- The uploaded `roadmap-Secure-Python-Coding.md` is the authoritative source for the required lesson topics, format list, tools, artifact pipeline, sandboxing, cache risks, incident scenarios, exercise and self-check. The project tree confirms this file belongs under `Stage 1 — Programming & Computational Thinking/22-Secure-Python-Coding/`.
- Version-sensitive APIs—especially PyYAML loader defaults and PyTorch checkpoint loading—must be verified against the exact pinned dependency version. This lesson explicitly recommends safe modes rather than relying on defaults.
- The policy code is a teaching skeleton. It does not claim to be a complete production artifact verifier; signature verification, manifest binding, tensor validation and OS-level isolation must be implemented for the target environment.
- No unknown artifact is loaded. The lab constructs a harmless marker-printing pickle fixture solely to test pre-deserialization rejection; it is never unpickled. Test observations are described as expectations in the lesson, not claims of execution.
