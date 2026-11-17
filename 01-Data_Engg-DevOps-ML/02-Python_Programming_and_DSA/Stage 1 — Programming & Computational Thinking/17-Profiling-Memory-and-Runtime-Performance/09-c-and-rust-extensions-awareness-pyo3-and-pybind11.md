# C and Rust Extensions Awareness: PyO3, pybind11, and the Native Boundary

> **Module:** Stage 1 — Programming & Computational Thinking  
> **Folder:** `17-Profiling-Memory-and-Runtime-Performance/`  
> **Lesson:** `09-c-and-rust-extensions-awareness-pyo3-and-pybind11.md`  
> **Audience:** Python/data engineers progressing from profiling to production performance engineering  
> **Baseline:** Python 3.12+ concepts; the PyO3 walkthrough pins PyO3 0.29.0 and uses a compatible current Rust toolchain. Check the compatibility matrix before changing versions.

## Why this lesson exists

A native extension is compiled code that Python can import as a module. It may be written in C, C++, or Rust and exposes a Python-facing API. Native code can reduce interpreter overhead, use specialized instructions, reuse an established native library, control memory layout, or run suitable work without holding the Global Interpreter Lock (GIL). None of these advantages is automatic: conversion costs, poor algorithms, contention, and packaging overhead can erase the gain.

This lesson follows:

1. CPU profiling and sampling (Lessons 01–02) to identify the actual hot path.
2. Benchmark design (Lesson 03) to measure realistic end-to-end costs.
3. Memory analysis and allocation work (Lessons 04–05) and GC/reference cycles (Lesson 06) to understand the memory consequences.
4. CPython performance idioms (Lesson 07) to fix simpler problems first.
5. `ctypes` and CFFI (Lesson 08) to call existing native functions.
6. This lesson: understand compiled extension modules, their build and runtime boundary, and the operational cost of adopting one.

The module roadmap's shared exercise is **`slowlog`**, a deliberately inefficient log/CSV analytics workload. The aim is not to write a native library for its own sake. The aim is to make a defensible engineering decision using correctness tests, profiles, benchmarks, memory measurements, and a maintenance plan.

## Prerequisites

You should be able to:

- Read Python functions, iterables, exceptions, tests, and `pyproject.toml`.
- Explain Big-O complexity and choose dictionaries, sets, lists, and streaming algorithms appropriately.
- Profile with `cProfile`/`pstats` and a sampling profiler; write repeatable benchmarks.
- Reason about Python objects, reference counting, cyclic GC, generators, buffers, and copies.
- Use a virtual environment, `pip` or `uv`, Git, a shell, and `pytest`.
- Understand the C ABI at a conceptual level from Lesson 08: pointers, lengths, integer widths, calling conventions, and library loading.

You do **not** need to be an expert in Rust, C++, compiler construction, or the CPython C API before starting.

## Learning objectives

By the end, you should be able to:

- Explain why a library might put a loop or data structure in native code.
- Choose among algorithmic changes, vectorization, Numba, Cython, pybind11/nanobind, PyO3, CFFI, a separate service, and no change.
- Build and test a small PyO3 extension and understand minimal pybind11/Cython project layouts.
- Identify conversions, allocations, GIL behavior, exception translation, and threading assumptions at the Python/native boundary.
- Read native build metadata and recognize the wheel/ABI/platform matrix required for distribution.
- Investigate native crashes and assess safety, supply-chain, reproducibility, and maintenance risks.
- Write an evidence-based architecture decision record (ADR) for a `slowlog` hot spot.

---

# Part 1 — Beginner: reason about native code before writing it

## 1. What does “native” mean?

Ordinary CPython executes Python bytecode in the interpreter. For a simple loop such as:

```python
def sum_squares_python(values: list[float]) -> float:
    total = 0.0
    for value in values:
        total += value * value
    return total
```

each iteration involves Python-level operations and object semantics: retrieving an element, performing numeric operations, and updating an object reference. CPython has optimized these operations over time, but a loop over millions of Python objects can still incur significant interpreter and object overhead.

A native implementation may execute a tight loop in compiled machine code. If the function accepts a large buffer and performs substantial work per call, it may reduce per-element interpreter overhead. The speed-up depends on the workload, compiler, CPU, data representation, and wrapper design.

### Common sources of performance

- **Native loops:** move repeated per-element work from Python bytecode into compiled code.
- **SIMD/vector instructions:** process multiple numeric values per instruction when the compiler or library can safely vectorize the operation. Data alignment, aliasing, CPU features, and compiler flags matter.
- **Memory layout:** contiguous typed arrays can improve cache locality and avoid one Python object per scalar.
- **Existing native libraries:** reuse optimized parsers, compression, cryptography, regular-expression engines, database clients, or numerical kernels rather than reimplementing them.
- **GIL release:** a binding may release the GIL while it performs work that does not access Python objects. This can allow other Python threads to run and, with appropriate native parallelism, may permit CPU parallelism. It does not make every extension parallel.
- **Lower allocation pressure:** native code can process a buffer without constructing millions of temporary Python objects, provided the API is designed to avoid conversions and copies.

Native code is not inherently faster. A poor native algorithm can lose to Python; a NumPy or Polars operation may already use highly optimized native kernels; and conversion at the boundary can cost more than the loop saves.

## 2. The decision order

Use this order when investigating a slow `slowlog` stage:

1. **Validate the workload and correctness.** Is the input representative? Are results checked?
2. **Fix algorithmic complexity.** Replace repeated scans or nested loops with an index, dictionary, set, or streaming pass where appropriate.
3. **Reduce unnecessary work and I/O.** Parse once, avoid duplicate decoding, batch reads, and remove repeated conversions.
4. **Change the data representation.** Use contiguous arrays, columnar data, or buffers if that fits the workload.
5. **Use an existing vectorized/native library.** NumPy, Polars, Arrow, a database engine, or an established parser may already solve the problem.
6. **Consider JIT compilation** such as Numba for supported numerical loops.
7. **Consider a native extension** only when a measurable hot spot remains and the boundary/API can be kept narrow.
8. **Consider a separate worker/service** when isolation, independent scaling, or fault containment matters more than in-process latency.

Do not translate a slow \(O(n^2)\) algorithm into Rust and call the job done if an \(O(n)\) algorithm solves the same problem.

## 3. Native-extension ecosystem

| Tool or approach | Language/model | Typical fit | Important trade-off |
|---|---|---|---|
| CPython C API | C; direct interpreter API | Fine-grained control, existing C libraries, mature low-level integration | High complexity; reference counting, object layout, and API-version obligations |
| Cython | Python-like syntax compiled to C/C++ | Incrementally type hot loops, typed memoryviews, bind C libraries | Generated C/C++ and build complexity; type declarations need care |
| pybind11 | C++ templates and Python bindings | Existing C++ libraries, STL and class-heavy APIs | C++ compiler/toolchain and ABI concerns; conversion policies matter |
| nanobind | C++ binding framework | Similar use cases to pybind11 with a different design/performance footprint | Ecosystem, compatibility, and migration considerations |
| PyO3 | Rust bindings for Python | Rust algorithms/libraries, strong default memory safety, explicit ownership | Rust toolchain, crate graph, conversion and GIL/threading design |
| maturin | Python packaging/build frontend for Rust extensions | Build/install/package PyO3 projects | Does not remove platform, ABI, or release-engineering work |
| CFFI | C ABI interface | Call C libraries, declare C signatures, optional compiled API mode | ABI correctness and buffer/pointer lifetime remain your responsibility |
| `ctypes` | Standard-library C ABI interface | Small wrappers around existing shared libraries | Runtime signature declarations and pointer safety; not a replacement for all bindings |
| Numba | JIT compilation of supported Python/NumPy code | Numerical loops with supported types and operations | Compilation warm-up, supported-subset constraints, specialization behavior |
| Mojo (awareness only) | Emerging language/toolchain for high-performance systems and numerical code | Evaluate only when its Python integration and deployment model fit the project | Do not treat it as a drop-in CPython extension framework; verify maturity, interoperability, and supported distribution targets for the exact version |
| NumPy / Polars / Arrow | Existing native-backed data libraries | Array or columnar workloads | API/data model may need to change; conversion can be expensive |
| Separate process/service | IPC or network boundary | Isolation, independent scaling, language/runtime choice | Serialization, IPC/network latency, deployment and operational cost |

These tools are not interchangeable. PyO3 is a binding framework; maturin is a build/package tool commonly used with it. Cython compiles typed Python-like source. Numba is a JIT approach rather than a traditional extension-binding framework.

## 4. The cost model: the boundary is part of the algorithm

An end-to-end native call can be modeled as:

\[
T_{\mathrm{total}} =
T_{\mathrm{convert,in}} +
T_{\mathrm{boundary}} +
T_{\mathrm{kernel}} +
T_{\mathrm{convert,out}} +
T_{\mathrm{allocation}}
\]

For tiny inputs, boundary and conversion costs may dominate. For large inputs, the kernel may dominate. If a Python list of millions of boxed floats is converted into a Rust `Vec<f64>`, that conversion costs time and allocates memory. If every call converts the same data again, the extension may be slower overall.

Useful API design principles:

- Prefer a **coarse-grained call** that processes a batch over one native call per item.
- Choose one clear data contract: Python sequences, NumPy arrays, a buffer-protocol object, or Arrow-compatible buffers.
- If using a buffer directly, specify dtype, shape, stride, byte order, mutability, ownership, and lifetime requirements.
- Do not claim “zero-copy” unless the implementation actually avoids copies on the supported paths. A buffer view can still trigger a conversion elsewhere.
- Keep Python objects out of a detached/GIL-free native region.
- Keep the Python-facing API small, stable, and easy to test against a pure-Python reference.

## 5. Memory safety and failure modes

A native extension executes in the Python process. A segmentation fault, invalid memory access, data race, or native abort can terminate the entire interpreter; Python exceptions cannot catch every native failure.

- **C:** manual pointer and lifetime discipline; buffer overruns and use-after-free can corrupt memory.
- **C++:** RAII and smart pointers help, but undefined behavior, data races, dangling references, and ABI mismatch remain possible.
- **Rust:** safe Rust prevents many memory errors, but `unsafe` blocks, FFI boundaries, incorrect aliasing assumptions, and unsafe dependencies can reintroduce them. Rust does not guarantee that the extension is logically correct or panic-free.
- **All languages:** input validation, dependency review, compiler/toolchain provenance, crash diagnostics, and platform testing remain necessary.

Treat native code as a high-trust component with an explicit contract and release process.

---

# Part 2 — Intermediate: build a minimal PyO3 extension

## 6. Project layout and pinned toolchain

The example exports `sum_squares(values)` as the `fastmath` extension module. It accepts a Python sequence that PyO3 can convert to `Vec<f64>`, computes the sum of squares in Rust, and returns a Python float.

This example intentionally prioritizes clarity over zero-copy performance. The sequence-to-`Vec<f64>` conversion is part of the call. Later sections show how to benchmark and reason about that cost.

Create this layout:

```text
fastmath-demo/
├── Cargo.toml
├── pyproject.toml
├── src/
│   └── lib.rs
└── tests/
    └── test_fastmath.py
```

Use a current stable Rust toolchain, Python 3.12+, and a virtual environment. The Rust crate version is pinned to PyO3 **0.29.0** for reproducibility of this lesson; when upgrading, read PyO3's migration guide and test the full Python/platform matrix.

### `Cargo.toml`

```toml
[package]
name = "fastmath"
version = "0.1.0"
edition = "2021"

[lib]
name = "fastmath"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "=0.29.0", features = ["extension-module"] }
```

`cdylib` asks Cargo to produce a dynamic library suitable for loading by a foreign runtime. The library name `fastmath` must match the Python extension module name. `extension-module` configures PyO3 for the extension-module linking model on supported platforms.

### `pyproject.toml`

```toml
[build-system]
requires = ["maturin>=1.9,<2"]
build-backend = "maturin"

[project]
name = "fastmath-demo"
version = "0.1.0"
requires-python = ">=3.12"
description = "Small PyO3 learning extension"
```

The distribution/project name (`fastmath-demo`) may differ from the import name (`fastmath`). The `[build-system]` table tells Python build frontends how to build the package. Maturin discovers the Rust crate and builds the extension. This minimal learning project has no runtime Python dependencies.

### `src/lib.rs`

```rust
use pyo3::prelude::*;

#[pymodule]
mod fastmath {
    use pyo3::prelude::*;

    /// Return the sum of x*x for every value in the input sequence.
    #[pyfunction]
    fn sum_squares(values: Vec<f64>) -> f64 {
        values.iter().map(|value| value * value).sum()
    }
}
```

#### Read the Rust code

- `Vec<f64>` is an owned, contiguous Rust vector of 64-bit floating-point values. PyO3 extracts compatible Python sequences into this vector. Extraction can fail; PyO3 reports that as a Python exception rather than calling the function with an invalid vector.
- `.iter()` borrows each vector element; `.map(...)` computes its square; `.sum()` accumulates the results.
- `#[pyfunction]` tells PyO3 to expose the Rust function as a Python-callable function.
- `#[pymodule]` declares a Python module. In this module-style form, the module identifier `fastmath` must match the library/import name. The macro generates the initialization machinery.
- The function's return type `f64` maps to a Python `float`.
- There is no explicit `Result` because this tiny kernel has no domain-specific error condition after successful argument extraction. Real APIs should model invalid values and operational failures deliberately.

### Build and invoke

Install Rust using the official Rust installation instructions for your operating system. Install Python 3.12+ and create a virtual environment.

Linux/macOS:

```bash
cd fastmath-demo
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "maturin>=1.9,<2" pytest
maturin develop --release
python -c "import fastmath; print(fastmath.sum_squares([1.0, 2.0, 3.0]))"
pytest -q
```

Windows PowerShell:

```powershell
cd fastmath-demo
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "maturin>=1.9,<2" pytest
maturin develop --release
python -c "import fastmath; print(fastmath.sum_squares([1.0, 2.0, 3.0]))"
pytest -q
```

Expected numeric result: `14.0`. The command `maturin develop --release` compiles an optimized Rust build and installs the extension into the active virtual environment. It requires a suitable Rust toolchain and a supported Python environment. If the build fails, inspect the compiler error before changing versions at random.

### `tests/test_fastmath.py`

```python
import math

import pytest

import fastmath


def test_sum_squares_basic() -> None:
    assert fastmath.sum_squares([1.0, 2.0, 3.0]) == 14.0


def test_empty_sequence() -> None:
    assert fastmath.sum_squares([]) == 0.0


def test_tuple_input() -> None:
    assert fastmath.sum_squares((2.0, -3.0)) == 13.0


def test_result_is_float() -> None:
    assert isinstance(fastmath.sum_squares([2]), float)


def test_bad_element_is_python_exception() -> None:
    with pytest.raises((TypeError, ValueError, OverflowError)):
        fastmath.sum_squares([1.0, "not a number"])


def test_finite_values() -> None:
    result = fastmath.sum_squares([0.5, 1.5])
    assert math.isclose(result, 2.5, rel_tol=0.0, abs_tol=1e-12)
```

Run tests from the project root after `maturin develop --release`. These tests exercise conversion and the visible API, not every possible floating-point edge case. Add tests for very large values, infinities, NaNs, and your chosen overflow/validation policy if the production contract requires them.

## 7. `Result`, exceptions, and panic behavior in Rust

PyO3 converts many Rust return types into Python objects and maps `PyResult<T>` errors into Python exceptions. A function that can fail should generally return `PyResult<T>`:

```rust
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[pyfunction]
fn positive_square_root(value: f64) -> PyResult<f64> {
    if !value.is_finite() || value < 0.0 {
        return Err(PyValueError::new_err(
            "value must be finite and non-negative",
        ));
    }
    Ok(value.sqrt())
}
```

`PyResult<T>` is an alias for a result whose error is a Python exception type. Returning `Err(...)` raises that exception on the Python side. This is better than silently returning a sentinel that callers might mistake for a valid result.

A Rust **panic** is not the same as a Python exception. PyO3 can catch unwinding panics at supported boundaries and turn them into a Python `PanicException` in common configurations, but this is not a universal recovery guarantee. If a build uses `panic = "abort"`, the process aborts; aborts cannot be converted into Python exceptions. A panic must not be used for ordinary input validation. Avoid `unwrap()` and `expect()` on input-dependent or operationally fallible paths in production extension code. Define whether failures are returned, translated, logged, or treated as fatal.

## 8. The GIL: what the binding must promise

On conventional GIL-enabled CPython, only one thread at a time executes Python bytecode while holding the GIL. Native extensions can release the GIL during work that does not access Python objects. This can let other Python threads progress; native code can also use its own threads. It does not follow that simply writing Rust or C++ makes Python threads parallel.

PyO3's API for detaching Python access has evolved; do not copy old examples that use deprecated names without checking the version-specific guide. With current PyO3, use the version's supported `Python::detach` API when the function has a `Python` token and the native operation is independent of Python state. The simple `sum_squares(Vec<f64>)` example does not explicitly detach: it is small and intended to teach the boundary first. For a long-running native kernel, design a detached section only after establishing that it will not touch Python objects, invoke Python callbacks, or use APIs that require an attached Python thread.

For pybind11, the analogous pattern is a scoped GIL release such as `py::gil_scoped_release` around a native-only region. For every language, ask:

- Is any Python object accessed in this region?
- Could the operation call a Python callback or raise a Python exception?
- Are the buffers alive and immutable or exclusively owned for the full native operation?
- Can two calls mutate shared native state concurrently?
- Does the library itself use threads, and could nested thread pools oversubscribe the machine?

Do not release the GIL merely because a function is “written in C++/Rust.” An extension that calls back into Python or manipulates Python objects must obey the runtime's attachment and locking rules.

## 9. Minimal pybind11 C++ example

Use pybind11 when the underlying library is already C++ or when its types, templates, and RAII-based design are a natural fit. It provides C++ wrappers for exposing functions and classes to Python.

Project layout:

```text
cppmath-demo/
├── pyproject.toml
├── CMakeLists.txt
└── src/
    └── cppmath.cpp
```

### `pyproject.toml`

```toml
[build-system]
requires = ["scikit-build-core>=0.10", "pybind11>=2.13"]
build-backend = "scikit_build_core.build"

[project]
name = "cppmath-demo"
version = "0.1.0"
requires-python = ">=3.12"
description = "Minimal pybind11 learning extension"

[tool.scikit-build]
wheel.packages = []
```

This example installs a top-level native module named `_cppmath`; the underscore is a conventional cue that it is an implementation detail. The package is intentionally minimal. For a user-facing package, provide a Python package wrapper and public API instead of requiring callers to depend directly on a private implementation module.

### `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.15...4.4)
project(cppmath_demo LANGUAGES CXX)

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_cppmath MODULE src/cppmath.cpp)
install(TARGETS _cppmath LIBRARY DESTINATION . RUNTIME DESTINATION .)
```

### `src/cppmath.cpp`

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>  // enables std::vector conversions

#include <vector>

namespace py = pybind11;

double sum_squares(double const *values, py::ssize_t size) {
    double total = 0.0;
    for (py::ssize_t i = 0; i < size; ++i) {
        total += values[i] * values[i];
    }
    return total;
}

PYBIND11_MODULE(_cppmath, module) {
    module.doc() = "Small pybind11 demonstration";
    module.def("sum_squares", [](std::vector<double> values) {
        return sum_squares(values.data(),
                           static_cast<py::ssize_t>(values.size()));
    });
}
```

The binding includes `<pybind11/stl.h>` so pybind11 can convert compatible Python sequences to and from standard-library containers such as `std::vector<double>`. The vector is an owned copy in this example. It is intentionally a simple demonstration, not a zero-copy NumPy binding. `PYBIND11_MODULE(_cppmath, module)` must match the compiled module name.

### Build and smoke test

With CMake and a C++ compiler installed:

```bash
python -m venv .venv
# Activate the environment using the command for your shell.
python -m pip install --upgrade pip
python -m pip install "scikit-build-core>=0.10" "pybind11>=2.13"
python -m pip install .
python -c "import _cppmath; print(_cppmath.sum_squares([1.0, 2.0, 3.0]))"
```

Expected result: `14.0`. If building from a source checkout fails, verify that CMake can find the pybind11 package installed into the isolated build environment. The backend normally arranges build requirements; do not assume a globally installed pybind11 package is required. This is a minimal architecture example; production packages usually install the module inside a named Python package and expose a stable Python wrapper.

C++ exceptions are translated by pybind11's registered exception translators for common standard exceptions. Define a deliberate exception contract; do not leak pointers or C++ references whose lifetime is shorter than the Python object using them. RAII helps manage resources but does not eliminate undefined behavior.

## 10. Cython and typed memoryviews

Cython lets you write Python-like `.pyx` code and compile it to C/C++ extensions. It can be a good incremental path when a Python loop can be typed without redesigning the entire application.

Example `kernels.pyx`:

```cython
# cython: language_level=3
def sum_squares(const double[::1] values):
    cdef Py_ssize_t i
    cdef Py_ssize_t n = values.shape[0]
    cdef double total = 0.0
    for i in range(n):
        total += values[i] * values[i]
    return total
```

`const double[::1]` is a read-only typed memoryview describing a one-dimensional contiguous buffer of C doubles. `const` allows compatible read-only as well as writable exporters; `::1` requests a contiguous layout. The function does not promise to accept every Python sequence: the caller must supply a compatible buffer, such as a suitable NumPy array with a compatible dtype and layout. An incompatible dtype/layout is normally rejected rather than silently converted by the memoryview declaration itself; any explicit conversion or contiguity repair must be counted as part of the caller’s cost. A typed memoryview can access a compatible buffer without converting each value to a Python object.

A typical Cython build uses `Cython` plus a setuptools or other supported build backend to translate `.pyx` into C/C++ and then compile a platform extension. The exact `pyproject.toml`, generated C source, and compiler configuration should be pinned and tested for the project's chosen Cython version and build backend. Do not treat `.pyx` as an interpreted Python file or assume the compiler is optional in a source build.

Cython can optionally disable bounds checks or wraparound checks for performance, but only do so when the index invariants are proven and tested; disabling checks can turn a Python exception into memory corruption.

## 11. Data exchange: list, NumPy, buffers, and Arrow

### Python lists

A list holds references to Python objects. For numeric data, that usually means object indirection and conversion into a typed native container. This is convenient and safe at the API boundary, but it can allocate and copy.

### NumPy arrays

A NumPy array stores typed values in a data buffer with shape, strides, dtype, and flags. Many numerical operations already run in compiled loops. A native binding can accept arrays through the buffer protocol or a library-specific integration, but must validate dtype, dimensionality, contiguity, alignment, and mutability. `numpy.asarray` may return a view or make a copy depending on the input and requested dtype/layout.

### Python buffer protocol

The buffer protocol allows an exporter to expose a memory region plus metadata. A native consumer must not assume every buffer is contiguous, writable, native-endian, or alive forever. Hold the appropriate view/exporter reference for the entire operation, and never retain a raw pointer beyond its valid lifetime.

### Arrow-compatible exchange

Apache Arrow's C Data Interface and related interchange mechanisms can share columnar array metadata and buffers between compatible implementations. This can avoid row-by-row Python-object conversion, but “zero-copy” is conditional: format conversions, casts, rechunking, ownership rules, and incompatible layouts can still copy. Arrow interchange is not the same as passing an arbitrary NumPy pointer. Follow the producer/consumer lifetime and release-callback contract.

A useful design question is: **where is the first Python object created for each scalar?** A columnar pipeline that remains in typed buffers across multiple operations may gain more than a native function that repeatedly converts a list at every call.

---

# Part 3 — Advanced: production engineering consequences

## 12. Fair benchmarking: Python, Rust, and NumPy

Never benchmark one implementation on pre-converted data and another on the original input without saying so. Separate at least these cases:

1. **Kernel-focused comparison:** data is already in the representation each implementation consumes.
2. **End-to-end comparison:** include conversion, allocation, and result construction the real caller pays.
3. **Throughput and latency:** measure realistic batch sizes, not only one large array.
4. **Cold and warm behavior:** include JIT/build/import warm-up when it matters; do not include compilation in steady-state kernel timing unless production recompiles per run.
5. **Memory and concurrency:** track peak memory, allocation volume, GIL contention, thread-pool oversubscription, and tail latency.

### Reference implementations

Save this as `bench_sum_squares.py` in the PyO3 project after building the extension:

```python
from __future__ import annotations

import statistics
import time

import fastmath
import numpy as np


def pure_python(values: list[float]) -> float:
    total = 0.0
    for value in values:
        total += value * value
    return total


def median_seconds(function, repeat: int = 7) -> float:
    samples = []
    for _ in range(repeat):
        start = time.perf_counter()
        function()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def main() -> None:
    # Construct input outside the timed region: this benchmark measures repeated
    # calls on existing data. A separate end-to-end benchmark should time setup.
    values = [float(i % 1000) / 1000.0 for i in range(500_000)]
    array = np.asarray(values, dtype=np.float64)

    expected = pure_python(values)
    assert np.isclose(fastmath.sum_squares(values), expected, rtol=1e-12)
    assert np.isclose(np.dot(array, array), expected, rtol=1e-12)

    def numpy_list_to_array_and_dot() -> float:
        # One conversion, then reuse that array for both operands.
        converted = np.asarray(values, dtype=np.float64)
        return float(np.dot(converted, converted))

    cases = {
        "pure Python list loop": lambda: pure_python(values),
        "PyO3 Vec extraction + Rust loop": lambda: fastmath.sum_squares(values),
        "NumPy dot on prebuilt ndarray": lambda: np.dot(array, array),
        "NumPy one conversion + dot": numpy_list_to_array_and_dot,
    }

    for name, function in cases.items():
        seconds = median_seconds(function)
        print(f"{name:36s} {seconds:.6f} s")



if __name__ == "__main__":
    main()
```

Install NumPy separately for this benchmark:

```bash
python -m pip install numpy
python bench_sum_squares.py
```

For the roadmap-required `pyperf` experiment, save this optional runner as `bench_sum_squares_pyperf.py` after building `fastmath` and installing NumPy and pyperf:

```python
from __future__ import annotations

import numpy as np
import pyperf

import fastmath


def pure_python(values: list[float]) -> float:
    total = 0.0
    for value in values:
        total += value * value
    return total


def numpy_list_to_array_and_dot(values: list[float]) -> float:
    converted = np.asarray(values, dtype=np.float64)
    return float(np.dot(converted, converted))


def main() -> None:
    values = [float(i % 1000) / 1000.0 for i in range(500_000)]
    array = np.asarray(values, dtype=np.float64)
    expected = pure_python(values)
    assert np.isclose(fastmath.sum_squares(values), expected, rtol=1e-12)
    assert np.isclose(np.dot(array, array), expected, rtol=1e-12)
    assert np.isclose(numpy_list_to_array_and_dot(values), expected, rtol=1e-12)

    runner = pyperf.Runner()
    runner.bench_func("python/list loop", pure_python, values)
    runner.bench_func("pyo3/list conversion + kernel", fastmath.sum_squares, values)
    runner.bench_func("numpy/prebuilt array kernel", np.dot, array, array)
    runner.bench_func("numpy/list conversion + kernel", numpy_list_to_array_and_dot, values)


if __name__ == "__main__":
    main()
```

Run it with `python -m pip install pyperf` followed by `python bench_sum_squares_pyperf.py --rigorous`. `pyperf` launches worker processes and reports measured results; record the command, environment, and output with the performance report. The correctness assertions run before the timed cases. The prebuilt-array kernel case excludes list-to-array conversion by design; the other list-input cases include their respective conversion paths. Do not compare those categories as if they had identical boundary costs.

**No fixed speed-up is promised.** Results depend on the CPU, compiler, Python/Rust versions, memory allocator, list conversion, NumPy build, and BLAS implementation. The `Vec<f64>` extraction is part of the PyO3 call; the NumPy prebuilt-array case has already paid array construction. The prebuilt-array and one-conversion NumPy cases intentionally answer different questions. The helper converts once per invocation, matching the fact that the PyO3 wrapper converts the input sequence once. Use `pyperf` for more rigorous process isolation and repeated measurement; the hand-written timer here is an exploratory demonstration, not a release-grade benchmark.

Floating-point addition order can change results slightly. Use tolerances when appropriate, and define NaN, infinity, overflow, and reproducibility expectations before replacing an implementation.

## 13. Boundary overhead and batch size

For a function doing one multiplication and addition, the native kernel is tiny. Conversion, argument checking, and the call itself may cost more than the work. A native function that processes a million values per call amortizes the boundary overhead across many elements.

Benchmark a size curve, for example \(n \in \{0, 1, 8, 128, 4096, 10^6\}\). Record latency and throughput separately. If a proposed extension only wins at an unrealistic batch size, it may not improve the production workload. Also measure the number of calls per record: moving the loop into native code usually matters more than translating a single scalar operation.

## 14. Threads, async code, and native parallelism

`asyncio` is a concurrency framework, not a way to make CPU-bound Python code run in parallel. A long synchronous native call inside an event-loop callback can still block the event loop even if the extension releases the GIL: the thread executing the callback remains busy until the call returns. Use a worker thread/process or asynchronous native API where appropriate, and define cancellation behavior.

Native extensions may launch their own thread pools (for example, numerical libraries). Combining these with application worker pools can oversubscribe CPUs and degrade p95/p99 latency. Benchmark with production-like concurrency and limit nested parallelism where necessary.

For free-threaded CPython, “the GIL is absent” does not mean “shared mutable state is automatically safe.” Extensions must explicitly declare and satisfy their thread-safety requirements, protect native shared state, avoid races, and test their supported interpreter build. A module that assumes global interpreter serialization may need substantial changes.

## 15. `pyproject.toml`, build isolation, and wheel production

A `pyproject.toml` separates project metadata, build-system requirements, and backend-specific settings. Build isolation installs the declared build requirements into a temporary environment; a developer's global packages should not be a hidden build dependency.

Read these sections carefully:

- `[build-system]`: the build backend and its own dependencies (`maturin`, `scikit-build-core`, `setuptools`, etc.).
- `[project]`: distribution name/version, supported Python versions, runtime dependencies, license and metadata.
- `[tool.maturin]` or `[tool.scikit-build]`: backend-specific configuration such as module name, source layout, CMake settings, or wheel packages.
- Cargo metadata (`Cargo.toml`): Rust crate type, dependencies, features, and compiler settings.
- CMake configuration: C++ standard, target name, linked libraries, include paths, and install destination.
- CI configuration: which Python versions, platforms, architectures, and ABI variants are actually built and tested.

### Wheels are platform-specific artifacts

A wheel is not simply a zipped Python source package. A native wheel includes compiled binaries and must be compatible with the interpreter ABI, operating system, CPU architecture, and shared-library environment it targets.

- **Linux `manylinux`:** compatibility policy for wheels targeting glibc-based Linux systems. Build and inspect according to the selected manylinux policy.
- **Linux `musllinux`:** for musl-based systems such as Alpine; not interchangeable with manylinux.
- **macOS `universal2`:** a single wheel can include both x86_64 and arm64 slices if all native components and build settings support that architecture combination. It is not automatic.
- **Windows:** compiler/runtime compatibility and architecture matter; ensure required DLLs are bundled or available through supported mechanisms.
- **`cibuildwheel`:** automates building and testing wheels across configured Python/platform combinations on CI. It does not guarantee every dependency is portable or every wheel is correct.
- **maturin:** can build PyO3 wheels and supports cross-platform workflows; each target still requires an appropriate toolchain/runner and dependency strategy.
- **`abi3` / stable ABI:** can reduce the number of CPython-version-specific wheels for extensions that stay within the Limited API and satisfy the binding framework's constraints. It is not a universal switch and may limit available APIs or features. Verify the chosen PyO3/C API support and minimum Python version before claiming stable-ABI compatibility.

A wheel is not “portable” merely because compilation succeeded on the author's laptop. Test the built wheel in a clean environment on the target platform. Native wheels can also be large; check current PyPI upload-size policy and artifact-size budgets before release rather than hard-coding a limit that may change. For the detailed wheel, source-distribution, and release workflow, continue with Stage 1 Module 18, especially its wheel/build and publishing lessons.

### Free-threaded Python

Free-threaded CPython uses distinct interpreter builds and wheel tags; support is version- and framework-specific. Do not assume a regular `cp3xx` wheel supports a `cp3xxt` interpreter. Do not copy a historical tag matrix as timeless truth: consult the current PyO3, CPython, and `cibuildwheel` documentation, enable the relevant build selectors where required, and test the actual artifact. A module must declare GIL usage/thread-safety correctly and audit every shared mutable structure and dependency.

The right release statement is “we build and test these exact interpreter/platform combinations,” not “we support Python everywhere.”

## 16. Example CI shape with `cibuildwheel`

A minimal GitHub Actions concept is to run a matrix of native wheel builds and then install/test the produced wheels. This example explicitly targets CPython 3.12 on each listed OS; it is not a full multi-version or architecture matrix. Expand `CIBW_BUILD`, add architecture/build-policy configuration, and install/test the produced wheels to match the project's actual support promise. The following is a starting point, not a complete release pipeline:

```yaml
name: native-wheels
on:
  workflow_dispatch:
  push:
    tags: ["v*"]

jobs:
  build-wheels:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: actions-rust-lang/setup-rust-toolchain@v1
      - run: python -m pip install --upgrade pip cibuildwheel
        env:
          CIBW_BUILD: "cp312-*"
      - run: python -m cibuildwheel --output-dir wheelhouse
        env:
          CIBW_BUILD: "cp312-*"
      - uses: actions/upload-artifact@v4
        with:
          name: wheels-${{ matrix.os }}
          path: wheelhouse/*.whl
```

Pin actions to reviewed immutable commit SHAs in a production workflow, use a lock or constraint strategy for build tools, and run tests against the built wheels in clean environments. Linux manylinux/musllinux policies and architecture selection need explicit configuration for the target support matrix. A workflow file alone does not prove the matrix has succeeded.

## 17. CPython C API evolution and thread-safety obligations

The CPython C API evolves. Extensions using private implementation details or the full C API can require rebuilds or code changes across Python versions. CPython 3.12 introduced support for per-interpreter GIL configurations in subinterpreters, which makes correct per-module state and interpreter isolation important. CPython 3.13 introduced free-threaded builds experimentally; CPython 3.14 declared support for the free-threaded build, but support remains dependent on the exact binding framework and its dependencies. CPython 3.12 also introduced immortal objects for selected objects; this is an implementation-level runtime detail, not a stable application-level optimization contract and not a reason to rely on object identity or refcount values. The Limited API and stable ABI can reduce some version-specific rebuilding, but only if the extension stays within the supported subset and the binding framework's constraints. Do not use private CPython structs or undocumented internals as a shortcut for performance.

Subinterpreters and free-threaded builds introduce additional requirements. Extension state should be per-module where appropriate rather than stored in unsafe process-global Python-object pointers. Native global state needs explicit synchronization. A dependency may not support subinterpreters or free-threaded execution even if your own code looks thread-safe.

Before claiming compatibility, check:
- The exact CPython versions and builds tested.
- Whether the extension uses the Limited API/stable ABI.
- Whether all third-party native libraries support the same targets.
- Whether the module declares GIL usage correctly and handles concurrent access.
- Whether subinterpreter support is claimed, tested, and documented.

## 18. Security, dependencies, and reproducible builds

Native dependencies expand the trusted computing base. Review both source and build-time dependencies.

- Pin and review Rust crates, C/C++ dependencies, build backends, and compiler/toolchain versions.
- Commit appropriate lock files for the repository's workflow; use `Cargo.lock` for application/workspace reproducibility and decide intentionally how library crates manage it.
- Record compiler flags and environment variables; avoid unreviewed `-march=native` in distributable wheels because it can produce binaries that fail on other CPUs.
- Generate an SBOM when required by the organization's release policy, and scan dependencies for known vulnerabilities and license obligations.
- Verify source archives and wheels are built from the intended commit and that build provenance is retained.
- Keep secrets out of build logs and use least-privilege publishing credentials or trusted publishing.
- Fuzz or property-test parsing and buffer-boundary code. Reject invalid sizes and malformed input before passing it to unsafe code.
- Avoid downloading or loading arbitrary native binaries at runtime. Shared-library search paths can create DLL/shared-library hijacking risks.
- Define an upgrade policy for security fixes, including how quickly native dependencies are rebuilt and republished.

Rust's type system is a valuable defense, not a supply-chain policy. A vulnerable dependency or unsafe block can still compromise a process.

## 19. Diagnose crashes and performance regressions

Python traceback tools cannot always explain a native segmentation fault. Use a layered approach.

1. **Reduce the reproducer.** Keep the smallest input and exact command that reproduces the failure.
2. **Enable Python fault diagnostics.** Run `python -X faulthandler your_script.py` or enable `faulthandler` early in the program. This can print Python stack traces on fatal signals, but it may not identify the faulty native instruction.
3. **Use a native debugger.** On Linux use `gdb`; on macOS use `lldb`; on Windows use the supported Visual Studio debugger or WinDbg. Capture a native backtrace and inspect loaded libraries.
4. **Use symbols and a debug build.** Preserve debug symbols and use a non-optimized or lightly optimized build when debugging; reproduce again in release mode after fixing.
5. **Use sanitizers when supported.** AddressSanitizer can help find out-of-bounds access and use-after-free; UndefinedBehaviorSanitizer can find some classes of undefined behavior. They require compatible compiler/linker settings and may need special runtime setup. Sanitizer success does not prove absence of defects.
6. **Profile the native region.** `py-spy --native`, platform profilers such as `perf`, Instruments, or Visual Studio Profiler can help when symbols and native-stack support are available. Confirm the profiler's platform and permission limitations.
7. **Check lifetime and concurrency.** Investigate dangling buffers, references retained past their lifetime, callbacks, shared state, and races. A crash that appears intermittent may be a race rather than an input parsing bug.

Do not suppress a crash by catching a Python exception around a native call; a segmentation fault or abort is not an ordinary Python exception.

## 20. Fair case studies: what the ecosystem examples teach

These examples are design patterns, not proof that every native implementation beats every Python implementation. Their architecture and performance profile can evolve; check the projects' current documentation when making implementation-specific claims.

- **Polars:** a Rust-based DataFrame engine with columnar execution and Apache Arrow-related data representations. The broader lesson is that query planning, columnar layout, expression execution, and reduced Python-level row iteration can matter more than simply translating a loop.
- **`pydantic-core`:** the validation engine behind Pydantic's Python-facing models is implemented in Rust. The lesson is to keep a friendly Python API while moving repeated parsing/validation work into a compiled core.
- **`tokenizers`:** Hugging Face's tokenizers library uses Rust for high-throughput tokenization and exposes Python bindings. Text processing has substantial work per call and can benefit from compiled algorithms and carefully designed APIs.
- **`orjson`:** a Rust-based JSON library exposes a compact Python API around native parsing/serialization. Serialization is a boundary-heavy workload where allocation, Unicode handling, correctness, and the chosen API contract all matter.
- **`ruff`:** a Rust-based linter/formatter shows how a compiled implementation can make repeated static analysis practical in editor and CI workflows. It also illustrates the importance of stable CLI/API contracts and distribution.
- **`uv`:** a Rust-based Python package/project tool demonstrates performance-sensitive orchestration where filesystem work, dependency resolution, caching, and packaging behavior interact. Native implementation is one part of a larger system design.

Common pattern: preserve an ergonomic Python-facing API, move substantial repeated work into a compiled core, avoid unnecessary per-element Python transitions, and invest in build/distribution automation. Also note the cost: native dependency graphs, platform wheels, crash debugging, compatibility policy, and release engineering.

---

# Part 4 — Decision matrix and ADR

## 21. Decision matrix

Use this as a starting point; the rating is workload- and team-dependent.

| Option | Performance potential | Implementation effort | Packaging burden | Memory safety | Debugging complexity | Maintainability |
|---|---|---:|---:|---|---|---|
| Keep existing Python | Low–high depending on algorithm and workload | Low | Low | Strong runtime guardrails for ordinary Python operations | Low | High when code is clear and tested |
| Improve algorithm/data structure | Often highest ROI | Low–medium | Low | Python-level safety | Low–medium | Usually high |
| Vectorize with NumPy/Polars/Arrow | High for suitable array/columnar work | Low–medium; may require data-model change | Medium if native dependencies are introduced | Mature libraries manage most native internals | Medium | High when APIs fit the domain |
| Numba | High for supported numerical loops | Medium | Medium; JIT/runtime and supported-subset constraints | More guarded than manual pointers, but type/operation constraints remain | Medium | Medium; specialization and warm-up must be understood |
| Cython | High for typed hot loops | Medium–high | High | C-level bounds/lifetime risks depend on options and code | High | Medium |
| PyO3/Rust extension | High for coarse-grained kernels and Rust libraries | High | High | Strong default safety in safe Rust; FFI/unsafe risks remain | High | Medium–high with good API and Rust skills |
| pybind11/C++ extension | High for existing C++ or optimized kernels | High | High | Manual/RAII discipline; undefined behavior possible | High | Medium; C++ expertise and ABI policy required |
| C API / low-level FFI | Potentially high, use-case-specific | Very high | High | Highest burden for manual pointer/lifetime code | Very high | Low–medium without specialist ownership |
| Separate process/service | Depends on compute and batching; adds IPC/network cost | High | High operational burden | Process boundary improves fault isolation, not input correctness | High across distributed boundaries | Medium; deployment/observability ownership needed |

A native implementation should pass a higher bar than a Python refactor because its long-term costs include toolchains, binary artifacts, supported ABI/platform matrices, native crash debugging, and specialist maintenance.

## 22. Architecture Decision Record (ADR) template

Use this template for the final `slowlog` exercise. Do not fill in invented benchmark results.

```markdown
# ADR-NNN: How should we optimize <slowlog hot spot>?

- Status: Proposed | Accepted | Rejected | Superseded
- Date:
- Owners:
- Python/runtime/platform scope:

## Context
- Workload and representative input size:
- Current behavior and correctness contract:
- Profile evidence (function/line/native stack):
- Baseline p50/p95 or throughput:
- Peak memory/allocation evidence:
- Operational constraints:

## Options considered
1. Retain current implementation
2. Improve algorithm/data structure
3. Vectorize or use NumPy/Polars/Arrow
4. Use Numba
5. Add a PyO3 or pybind11/Cython extension
6. Move the work to a separate worker/service

## Evidence and comparison
- Commands and environment:
- Input preparation/conversion included?:
- Warm-up and repetitions:
- Correctness/property tests:
- Latency/throughput and peak-memory results:
- Platform and concurrency coverage:

## Decision
- Chosen option:
- Why it is the smallest sufficient change:
- Why other options were rejected:

## Consequences
- Performance and memory:
- Build/wheel/platform matrix:
- Debugging and observability:
- Security/SBOM/dependency impact:
- Compatibility and upgrade policy:
- Rollback plan and owner:

## Acceptance criteria
- Correctness:
- Performance target:
- Memory target:
- CI and packaging:
- Revisit trigger:
```

### Worked decision framing: `slowlog` repeated text parsing

Suppose profiling shows a function repeatedly splitting and normalizing the same log field, and a dictionary index could eliminate repeated scans. The first candidate should be an algorithmic/data-flow change, not Rust. If the revised code still spends most time in a CPU-heavy parsing kernel and input can be processed in batches, compare a suitable existing parser, vectorized approach, Numba, and a native extension. If the job is dominated by disk reads or decompression, changing the parsing language may have little effect. The example deliberately supplies no benchmark numbers: collect them from your workload.

---

# Part 5 — Common mistakes and troubleshooting

## 23. Common mistakes

- Writing native code before profiling the actual workload.
- Translating an inefficient algorithm instead of improving complexity.
- Benchmarking only the native kernel while ignoring input conversion and allocation.
- Calling a native function once per row or scalar rather than processing a batch.
- Assuming a Python list is a contiguous typed array.
- Calling a buffer “zero-copy” without verifying ownership, dtype, strides, and lifetime.
- Releasing the GIL while accessing Python objects or allowing callbacks to re-enter Python incorrectly.
- Treating Rust panics as ordinary input errors, or using `panic = "abort"` while expecting Python exceptions.
- Assuming `unsafe` Rust is safe because the rest of the project is Rust.
- Returning a reference/pointer to temporary C++/Rust storage.
- Disabling Cython bounds checks without proven invariants.
- Shipping a wheel built only on the developer's machine and calling it cross-platform.
- Assuming `abi3`, `manylinux`, `universal2`, or free-threaded compatibility without testing the actual wheel and dependencies.
- Benchmarking a JIT implementation before warm-up, or omitting cold-start costs when cold starts matter in production.
- Ignoring thread-pool oversubscription when native libraries create their own worker threads.
- Failing to define exception, NaN/infinity, integer-overflow, cancellation, and concurrency behavior at the public API boundary.

## 24. Troubleshooting table

| Symptom | Likely causes | First checks |
|---|---|---|
| `ImportError: dynamic module does not define module export function` | Module name mismatch between Cargo/CMake, `#[pymodule]`/`PYBIND11_MODULE`, and import name | Match exact names; clean build artifacts and rebuild |
| `ModuleNotFoundError` after a successful build | Extension installed in another interpreter/venv or wrong working directory | Check `python -c "import sys; print(sys.executable)"`, `python -m pip show`, and `maturin develop` environment |
| Rust compile error in PyO3 macro | PyO3 API/version mismatch, wrong module declaration, unsupported Rust version | Confirm pinned crate version, toolchain, and current version-specific guide |
| C++ CMake cannot find pybind11 | Build dependency not installed in isolated build environment or config path issue | Inspect backend build logs; verify `build-system.requires` and `find_package` |
| Native call is slower than Python | Small kernel, conversion/copy overhead, poor algorithm, benchmark artifact | Measure end-to-end and kernel-only paths; batch calls; compare to vectorized libraries |
| Crash or intermittent corruption | Invalid pointer, lifetime error, race, ABI mismatch, native dependency bug | Minimize reproducer; enable faulthandler; run under debugger/sanitizer |
| Works on Linux but fails on Alpine | glibc vs musl wheel/dependency mismatch | Build/test a musllinux-compatible artifact or use a supported base image |
| Wheel fails on another Python version | CPython ABI-specific extension or unsupported API | Inspect wheel tags and stable-ABI claims; build for supported versions |
| Free-threaded interpreter rejects or crashes in extension | Missing thread-safety support/declaration or incompatible dependency | Check exact framework support, GIL usage declaration, and concurrent shared state |
| Performance regresses under load | Nested thread pools, lock contention, allocation spikes, cache pressure | Benchmark realistic concurrency; cap parallelism; profile CPU and memory |

---

# Part 6 — Exercises and self-check

## 25. Exercises

### Exercise 1 — prove the hot spot

Profile `slowlog` with representative data. Write down the top three cumulative-time functions and top three self-time functions. State which result would justify a native extension and which result would not.

**Deliverable:** profile excerpt, hypothesis, and one falsifiable performance prediction.

### Exercise 2 — compare representations

Use the `sum_squares` example to compare Python lists, a prebuilt NumPy array, and the PyO3 call. Separate conversion and kernel time. Test at least five input sizes.

**Deliverable:** benchmark script, environment, correctness assertions, repeated timings, and a paragraph explaining where the crossover occurs (if any).

### Exercise 3 — API design

Redesign `sum_squares` for a real data pipeline. Specify input type, dtype, shape, ownership, lifetime, mutability, error behavior, and whether a copy is allowed. Explain why you selected a Python sequence, NumPy buffer, or Arrow-compatible input.

### Exercise 4 — choose a binding framework

For each scenario, justify a tool:
- Existing C library with a stable C ABI.
- Existing C++ class-heavy library.
- Numerical Python loop over contiguous arrays.
- Rust implementation with complex ownership.
- Pure Python code whose bottleneck is a repeated dictionary scan.
- Work that must be isolated from the main process for reliability.

Include at least one reason **not** to choose your selected tool.

### Exercise 5 — packaging review

Review a native project's `pyproject.toml`, Cargo/CMake configuration, and CI workflow. Identify every supported Python/platform/ABI combination and distinguish “configured,” “built,” and “tested.” Propose the smallest release matrix that meets the project's actual support promise.

### Exercise 6 — crash investigation tabletop

A production process exits with a segmentation fault only under concurrent load. Write a first-hour incident plan: reproduction, faulthandler, native debugger, sanitizer/debug build, race/lifetime hypotheses, containment, and evidence to preserve.

### Exercise 7 — final ADR

Complete the ADR for one measured `slowlog` hot spot. Compare retaining the implementation, algorithmic refactoring, vectorization, Numba, a PyO3/pybind11/Cython extension, and a separate service. Include correctness evidence, end-to-end benchmark results, conversion costs, packaging burden, ownership, rollback, and a revisit trigger.

## 26. Self-check questions

1. Why can translating a Python loop into Rust fail to improve end-to-end runtime?
2. What does PyO3's `#[pyfunction]` do? What does `#[pymodule]` do?
3. Why must the extension module's name agree across the Rust/C++ build and Python import?
4. What does `Vec<f64>` conversion cost, and when would a buffer-oriented API be preferable?
5. Why is a NumPy operation often a better first choice than a hand-written extension?
6. What does releasing the GIL allow, and what does it not guarantee?
7. How should a Rust `Result` failure reach Python? Why is a panic not an input-validation strategy?
8. What is the difference between manylinux and musllinux? What does `universal2` mean?
9. Why does a successful local build not prove wheel portability?
10. When can `abi3` reduce wheel count, and why must support be verified rather than assumed?
11. What new obligations appear for free-threaded Python extensions?
12. Which tools can help diagnose a native crash, and what are their limitations?
13. Why can Arrow-compatible data exchange reduce Python overhead, and under what conditions can it still copy?
14. What evidence should be required before accepting a native extension into `slowlog`?

## 27. Review checklist

Before approving a native extension, verify:

- [ ] The hot spot is supported by profiling and representative benchmarks.
- [ ] Algorithmic and existing-library alternatives were evaluated.
- [ ] Correctness tests compare the native implementation with a trusted reference.
- [ ] The Python/native data contract documents dtype, shape, lifetime, ownership, and errors.
- [ ] Conversion and allocation costs are included in end-to-end measurements.
- [ ] GIL release and native thread safety are explicit and tested.
- [ ] Panic, exception, cancellation, and invalid-input behavior are defined.
- [ ] The build backend, compiler, dependencies, and versions are declared.
- [ ] CI builds and tests the exact promised platform/Python/ABI matrix.
- [ ] Wheels are tested in clean target environments.
- [ ] Crash diagnostics and a rollback plan exist.
- [ ] Dependency, license, SBOM, and provenance requirements are addressed.
- [ ] The performance gain justifies the additional long-term ownership cost.

## 28. Further reading

Prefer the documentation for the exact versions selected by your project:

- PyO3 User Guide: <https://pyo3.rs/>
- PyO3 releases and migration notes: <https://github.com/PyO3/pyo3/releases>
- Maturin User Guide: <https://www.maturin.rs/>
- pybind11 documentation: <https://pybind11.readthedocs.io/>
- scikit-build-core documentation: <https://scikit-build-core.readthedocs.io/>
- Cython documentation: <https://cython.readthedocs.io/>
- Numba documentation: <https://numba.readthedocs.io/>
- Python buffer protocol: <https://docs.python.org/3/c-api/buffer.html>
- Python C API / Limited API: <https://docs.python.org/3/c-api/stable.html>
- cibuildwheel documentation: <https://cibuildwheel.pypa.io/>
- Apache Arrow C Data Interface: <https://arrow.apache.org/docs/format/CDataInterface.html>
- Python `faulthandler`: <https://docs.python.org/3/library/faulthandler.html>

---

## Final principle

A native extension is an architectural choice, not a badge of performance engineering. Profile first, fix the algorithm and data representation, compare existing native-backed libraries, then prototype a narrow native boundary if the evidence warrants it. Measure the full path, test correctness and concurrency, and budget for wheels, crash diagnosis, dependency security, and long-term ownership.
