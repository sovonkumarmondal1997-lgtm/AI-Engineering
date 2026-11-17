# Calling Native Libraries from Python with `ctypes` and `cffi`

> **Stage 1 --- Programming & Computational Thinking · Module 1.17 ·
> Lesson 08**\
> **Target:** Python 3.12+; examples are designed for mainstream 64-bit
> Linux, macOS, and Windows unless a section says otherwise.\
> **Scope:** Call existing native libraries safely. Building full Python
> extension modules with the CPython API, Cython, pybind11, or PyO3
> belongs to Lesson 09.

## Why this lesson exists

Python code can call compiled code without turning the compiled code
into a purpose-built Python extension module. A foreign-function
interface (FFI) describes the boundary between a Python process and a
function implemented in another language or in a system/vendor library.

This is useful when integrating a compression or cryptography library, a
vendor SDK, a system API, or a small C routine that profiling has shown
to be a genuine bottleneck. It is not a default optimization. A native
call can be slower than Python when calls are tiny, conversions copy
data, or the work is dominated by I/O or allocation.

The central rule is:

> **An FFI declaration is an executable claim about a C ABI.** If the
> declaration, ownership, or lifetime is wrong, Python cannot reliably
> protect you from memory corruption, crashes, or undefined behavior.

## Learning objectives

By the end, you should be able to:

1.  Explain when `ctypes` or `cffi` is appropriate and distinguish an
    FFI from a Python extension module.
2.  Load a shared library deliberately and declare exact native argument
    and return types.
3.  Safely pass byte buffers, pointers, structures, arrays, callbacks,
    and output parameters.
4.  Explain `ctypes` ABI details and the difference between CFFI ABI and
    API modes.
5.  Build and test a small C checksum routine with both wrappers and a
    pure-Python reference.
6.  Recognize the limits of pointer validation, GIL assumptions,
    zero-copy claims, and benchmark conclusions.
7.  Review library loading, packaging, debugging, and security risks
    before production deployment.

## Prerequisites

You should already understand:

-   Python functions, exceptions, bytes, `bytearray`, `memoryview`, and
    object lifetimes.
-   Basic C declarations: pointers, arrays, structs, `size_t`, integer
    types, and header files.
-   Processes, virtual memory, shared libraries, and the difference
    between a source file and a compiled binary.
-   Unit tests and the principle from earlier performance lessons:
    measure before optimizing.
-   Profiling and memory analysis from Lessons 01--07. Those lessons
    identify whether a native boundary is justified; this lesson does
    not repeat their profiling-tool tutorials.

A C compiler is required for the complete helper-library lab and CFFI
API-mode build. The `ctypes` module is part of Python's standard
library. Install CFFI in your virtual environment:

``` bash
python -m pip install cffi
```

With `uv`:

``` bash
uv add cffi
```

Use a supported Python environment and compiler toolchain. On Linux,
install GCC or Clang and the standard C development headers; on macOS,
install Xcode Command Line Tools (`xcode-select --install`); on Windows,
use the Visual Studio Build Tools C/C++ workload or another compiler
supported by your Python/CFFI toolchain. Commands below are examples,
not a guarantee that every compiler is installed.

------------------------------------------------------------------------

## 1. What an FFI does

An FFI lets one language call functions exposed through another
language's binary calling convention. For `ctypes` and CFFI, the common
case is a C ABI: function names, argument layout, return layout, calling
convention, and data layout must agree with the compiled library.

Use an FFI when:

-   a maintained native library already provides the required operation;
-   a system or vendor API is only exposed as a C ABI;
-   a measured, bounded kernel benefits from operating on a whole buffer
    in native code;
-   integrating a library is less costly than maintaining a bespoke
    extension module.

Do **not** reach for an FFI just because C is "faster." First rule out
algorithmic problems, repeated I/O, unnecessary allocations, inefficient
data structures, and Python-level overhead. For numerical/data
workloads, vectorized NumPy or a suitable library may already move work
into native code with a safer interface.

### FFI versus extension module

  -----------------------------------------------------------------------
  Approach                Typical use             Build requirement
  ----------------------- ----------------------- -----------------------
  `ctypes`                Call an existing C ABI  No Python extension
                          directly                build; a native shared
                                                  library must exist

  CFFI ABI mode           Declare and load an     No wrapper compilation;
                          existing library at     still needs a
                          runtime                 compatible native
                                                  library

  CFFI API mode           Compile C declarations  C compiler and build
                          against headers into a  step
                          generated extension     

  CPython C API, Cython,  Implement a             Extension build and
  pybind11, PyO3          Python-facing extension packaging workflow
                          module or expose richer 
                          types                   
  -----------------------------------------------------------------------

Lesson 09 covers full extension-module development. Here, CFFI API mode
is used only to demonstrate compiling a thin CFFI binding against a C
header; it is not a full survey of extension development.

------------------------------------------------------------------------

## 2. Shared libraries and loading

A native library is compiled for a particular operating system,
architecture, ABI, and often runtime environment. Common suffixes are:

-   Linux/ELF: `.so` (sometimes versioned, such as `libexample.so.1`);
-   macOS/Mach-O: `.dylib` (frameworks and `.so` names also exist);
-   Windows/PE: `.dll`.

Names and search conventions differ. A library's filename alone does not
establish that it is compatible with your Python process.

### Loading an existing library

``` python
import ctypes
import ctypes.util

name = ctypes.util.find_library("c")
if name is None:
    raise RuntimeError("Could not locate the platform C runtime")

libc = ctypes.CDLL(name)
```

`find_library()` asks the platform for a plausible library name. It is
not a security validator, not a universal package manager, and not a
guarantee that the returned library has the exact API you expect. Some
platforms or minimal containers may not resolve names reliably. For a
bundled application, use a known, trusted library path resolved relative
to the installed package and validate packaging on every target
platform.

`ctypes.CDLL` is the usual loader for C calling conventions. On Windows,
`ctypes.WinDLL` is intended for the `stdcall` convention; use it only
when the API documentation specifies that convention. Do not guess. On
Windows, `ctypes.CDLL` is generally associated with `cdecl`.
Calling-convention mismatches can corrupt the stack or crash.

Avoid hard-coding `libc.so.6` as a cross-platform solution. It is a
glibc-specific name and will not work as written on macOS or Windows.

### A small standard-library call

``` python
import ctypes
import ctypes.util

library_name = ctypes.util.find_library("c")
if library_name is None:
    raise RuntimeError("C runtime was not found")

libc = ctypes.CDLL(library_name)
libc.strlen.argtypes = [ctypes.c_char_p]
libc.strlen.restype = ctypes.c_size_t

result = libc.strlen(b"hello")
assert result == 5
print(result)  # 5
```

Why the declarations matter:

-   `argtypes` tells `ctypes` how to convert Python arguments before the
    call.
-   `restype` tells it how to interpret the return value.
-   `strlen` returns `size_t`, not `int`. The platform's `size_t` is the
    correct unsigned type for an object size.
-   `c_char_p` represents a pointer to a NUL-terminated C string. It is
    not a general binary-buffer abstraction when embedded NUL bytes are
    meaningful.

**Never rely on defaults.** `ctypes` assumes an `int` return type if
`restype` is not set. On a 64-bit process, returning a pointer and
interpreting only an `int` can truncate the address. Wrong argument
declarations can cause invalid conversions or native memory corruption.
A successful smoke test does not prove a signature is correct.

------------------------------------------------------------------------

## 3. C types and ABI contracts

The declaration in Python must match the declaration in the library's
public header, including signedness, width, pointer indirection, and
calling convention.

  ------------------------------------------------------------------------------
  C declaration          Common `ctypes` type               Important caveat
  ---------------------- ---------------------------------- --------------------
  `int`                  `ctypes.c_int`                     C `int` is not
                                                            guaranteed to be
                                                            64-bit

  `double`               `ctypes.c_double`                  Must match
                                                            floating-point type

  `char *` used as       `ctypes.c_char_p`                  Does not express
  NUL-terminated string                                     arbitrary binary
                                                            data plus length

  `unsigned char *`      `ctypes.POINTER(ctypes.c_ubyte)`   Pointer validity and
                         or a buffer argument               length remain your
                                                            responsibility

  `size_t`               `ctypes.c_size_t`                  Platform-dependent
                                                            width; do not
                                                            replace with `c_int`

  `void *`               `ctypes.c_void_p`                  Opaque pointer; does
                                                            not make
                                                            dereferencing safe

  `unsigned long long`   `ctypes.c_ulonglong`               Match the exact
                                                            header type

  `int *`                `ctypes.POINTER(ctypes.c_int)`     An output pointer
                                                            needs valid writable
                                                            storage
  ------------------------------------------------------------------------------

Use fixed-width integer types in public APIs when the contract requires
fixed widths (`uint32_t`, `uint64_t` from `<stdint.h>`), but mirror them
exactly in each binding. Never assume that C `long` has the same width
on Windows and Unix-like systems: 64-bit Windows commonly uses LLP64
(`long` is 32-bit, pointers are 64-bit), while 64-bit Linux/macOS
commonly use LP64 (`long` and pointers are 64-bit).

### Bytes, strings, and lifetimes

-   Python `str` is Unicode. Encode explicitly before passing text:
    `text.encode("utf-8")`.
-   `bytes` is immutable and can contain NUL bytes. For a function
    accepting `(pointer, length)`, the length is the authoritative
    boundary.
-   A C string normally ends at the first NUL byte. Passing arbitrary
    binary data through a `c_char_p`-only API may silently truncate its
    logical content.
-   A Python-created temporary object is not a substitute for a
    documented ownership contract. If C retains a pointer after the
    call, the Python owner must keep the storage alive for the entire
    retention period.
-   `ctypes` can keep some converted arguments alive for the duration of
    the call, but that does **not** make it safe for C to retain those
    pointers afterward.

Do not pass a Python string directly to a function expecting a C
`char *`. Encode it and understand whether the function expects a
NUL-terminated string or pointer-plus-length.

------------------------------------------------------------------------

## 4. Lab: a bounded C checksum function

This lab implements a simple 64-bit FNV-1a-style checksum over a byte
sequence. It is for learning FFI mechanics, not for cryptography,
authentication, tamper-proof integrity, or collision-resistant
identifiers. It is intentionally small, allocation-free, and bounded.

The public C function:

``` c
int checksum_bytes(
    const unsigned char *data,
    size_t length,
    unsigned long long *out
);
```

Contract:

-   Return `0` on success, `1` for invalid arguments, and `2` if
    `length` exceeds the library's 64 MiB limit.
-   `out` must be a valid writable pointer for one `unsigned long long`.
-   If `length > 0`, `data` must point to at least `length` readable
    bytes.
-   Empty input (`length == 0`) is valid; `data` may be `NULL` in that
    case.
-   The function never retains either pointer after returning.
-   The output value is written only on success.
-   The wrapper separately validates input type and length before
    calling native code.

These checks detect some invalid inputs. They cannot prove that an
arbitrary non-NULL pointer points to valid memory or that it has the
claimed extent. Only pass pointers and buffers whose ownership and
bounds are already known.

### Public header: `checksum.h` (create this first)

Save this file as `checksum.h` in the same directory as `checksum.c`:

``` c
#ifndef CHECKSUM_H
#define CHECKSUM_H

#include <stddef.h>

/* Export the public entry point from a Windows DLL. On ELF/Mach-O,
   ordinary external visibility is sufficient for this example. */
#if defined(_WIN32)
#  define CHECKSUM_API __declspec(dllexport)
#else
#  define CHECKSUM_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

CHECKSUM_API int checksum_bytes(
    const unsigned char *data,
    size_t length,
    unsigned long long *out
);

#ifdef __cplusplus
}
#endif

#endif
```

The implementation includes this header so the compiler checks the
function definition against the public declaration. Keep the header and
implementation in sync.

### 4.1 Complete C source: `checksum.c`

Save this exact source as `checksum.c`:

``` c
#include <stddef.h>
#include <limits.h>

#define CHECKSUM_MAX_BYTES ((size_t)64 * 1024 * 1024)

#if ULLONG_MAX != 18446744073709551615ULL
#error "This example requires a 64-bit unsigned long long"
#endif

/* Return codes: 0 = success, 1 = invalid arguments, 2 = too large. */
int checksum_bytes(
    const unsigned char *data,
    size_t length,
    unsigned long long *out
) {
    size_t i;
    unsigned long long hash = 14695981039346656037ULL;

    if (out == NULL) {
        return 1;
    }
    if (length > CHECKSUM_MAX_BYTES) {
        return 2;
    }
    if (length > 0 && data == NULL) {
        return 1;
    }

    for (i = 0; i < length; ++i) {
        hash ^= (unsigned long long)data[i];
        hash *= 1099511628211ULL;
    }

    *out = hash;
    return 0;
}
```

This code requires a C compiler with support for `unsigned long long`
and the standard `<stddef.h>` / `<limits.h>` headers. The compile-time
check makes the intended 64-bit arithmetic requirement explicit.
Unsigned overflow is defined modulo (2\^{64}) for this required type
width.

The empty-input checksum is the FNV offset basis, because the loop
executes zero times. The checksum is not a security primitive.

### 4.2 Compile the shared library

Run commands from the directory containing `checksum.c`. Use the
compiler appropriate for your platform.

**Linux (GCC or Clang):**

``` bash
cc -std=c11 -O2 -Wall -Wextra -Wpedantic -fPIC -shared checksum.c -o libchecksum.so
```

**macOS (Apple Clang):**

``` bash
cc -std=c11 -O2 -Wall -Wextra -Wpedantic -fPIC -dynamiclib checksum.c -o libchecksum.dylib
```

**Windows (Developer Command Prompt for Visual Studio):**

``` bat
cl /nologo /O2 /W4 /LD checksum.c /link /OUT:checksum.dll
```

The Windows command creates an import library and object file as build
by-products in addition to `checksum.dll`; the runtime wrapper needs the
DLL. The `CHECKSUM_API` declaration in `checksum.h` uses
`__declspec(dllexport)` on Windows so `checksum_bytes` is present in the
DLL export table and discoverable by `ctypes`/CFFI ABI mode. If your
toolchain uses a different compiler, follow its documented shared-library
flags. The library must match Python's process
architecture (for example, 64-bit Python needs a compatible 64-bit DLL).

Do not download an unknown prebuilt DLL/SO and load it merely because
its filename matches. Build from reviewed source or obtain the library
from a trusted vendor distribution and verify its provenance.

### 4.3 Pure-Python reference implementation

Save as `checksum_reference.py`:

``` python
MAX_INPUT_BYTES = 64 * 1024 * 1024
MASK64 = (1 << 64) - 1
OFFSET_BASIS = 14695981039346656037
FNV_PRIME = 1099511628211


def checksum_python(data: bytes) -> int:
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    if len(data) > MAX_INPUT_BYTES:
        raise ValueError("input exceeds 64 MiB limit")

    value = OFFSET_BASIS
    for byte in data:
        value ^= byte
        value = (value * FNV_PRIME) & MASK64
    return value
```

This reference is the correctness oracle for the lab. Its explicit mask
reproduces 64-bit unsigned wraparound in Python's arbitrary-precision
integers.

### 4.4 `ctypes` wrapper

Save as `checksum_ctypes.py` next to the compiled library and reference
module:

``` python
from __future__ import annotations

import ctypes
import os
from pathlib import Path

from checksum_reference import MAX_INPUT_BYTES, checksum_python

MAX_NATIVE_BYTES = MAX_INPUT_BYTES


def _library_path() -> Path:
    """Resolve only the library built beside this wrapper."""
    base = Path(__file__).resolve().parent
    if os.name == "nt":
        name = "checksum.dll"
    elif os.sys.platform == "darwin":
        name = "libchecksum.dylib"
    else:
        name = "libchecksum.so"
    path = base / name
    if not path.is_file():
        raise FileNotFoundError(
            f"Native library not found: {path}. Build it using the instructions."
        )
    return path


_lib = ctypes.CDLL(str(_library_path()))
_checksum = _lib.checksum_bytes
_checksum.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte),  # const unsigned char *data
    ctypes.c_size_t,                 # size_t length
    ctypes.POINTER(ctypes.c_ulonglong),  # unsigned long long *out
]
_checksum.restype = ctypes.c_int  # status code


def checksum_native(data: bytes) -> int:
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    length = len(data)
    if length > MAX_NATIVE_BYTES:
        raise ValueError("input exceeds 64 MiB limit")

    output = ctypes.c_ulonglong()

    if length == 0:
        # C contract explicitly permits NULL for empty input.
        data_pointer = ctypes.POINTER(ctypes.c_ubyte)()
        status = _checksum(data_pointer, 0, ctypes.byref(output))
    else:
        # from_buffer_copy owns a stable copy for the duration of this call.
        # The local variable keeps that allocation alive until C returns.
        buffer = (ctypes.c_ubyte * length).from_buffer_copy(data)
        status = _checksum(buffer, length, ctypes.byref(output))

    if status == 1:
        raise ValueError("native checksum rejected its arguments")
    if status == 2:
        raise ValueError("native checksum input is too large")
    if status != 0:
        raise RuntimeError(f"unexpected native status code: {status}")

    return int(output.value)


if __name__ == "__main__":
    sample = b"hello native world"
    assert checksum_native(sample) == checksum_python(sample)
    print(checksum_native(sample))
```

Why this wrapper is conservative:

-   It declares all three argument types and the return type.
-   It uses `c_size_t` for `size_t`, not `c_int`.
-   It uses a pointer type for `unsigned char *`, not a truncated
    integer.
-   It allocates output storage and passes it with `byref`.
-   For nonempty input, `from_buffer_copy` creates an owned copy whose
    lifetime spans the call. This avoids accidentally passing a pointer
    into a temporary conversion.
-   For empty input, it passes a typed NULL pointer, which the C
    contract explicitly permits.
-   It validates the maximum size in Python and C. The native check
    remains important because other callers could bypass this Python
    wrapper.

The wrapper cannot protect against a corrupted library, an ABI mismatch,
or a malicious native function. Native code executes in the Python
process and can corrupt it.

### 4.5 `cffi` ABI-mode wrapper

Save as `checksum_cffi_abi.py`:

``` python
from __future__ import annotations

import os
from pathlib import Path

from cffi import FFI
from checksum_reference import MAX_INPUT_BYTES, checksum_python

ffi = FFI()
ffi.cdef("""
    int checksum_bytes(
        const unsigned char *data,
        size_t length,
        unsigned long long *out
    );
""")

base = Path(__file__).resolve().parent
if os.name == "nt":
    library_path = base / "checksum.dll"
elif os.sys.platform == "darwin":
    library_path = base / "libchecksum.dylib"
else:
    library_path = base / "libchecksum.so"

if not library_path.is_file():
    raise FileNotFoundError(
        f"Native library not found: {library_path}. Build it using the instructions."
    )

lib = ffi.dlopen(str(library_path))


def checksum_native(data: bytes) -> int:
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    length = len(data)
    if length > MAX_INPUT_BYTES:
        raise ValueError("input exceeds 64 MiB limit")

    out = ffi.new("unsigned long long *")
    if length == 0:
        data_pointer = ffi.NULL
    else:
        # CFFI owns this copied array; its Python cdata reference stays alive
        # until the native call has returned.
        data_pointer = ffi.new("unsigned char[]", data)

    status = lib.checksum_bytes(data_pointer, length, out)
    if status == 1:
        raise ValueError("native checksum rejected its arguments")
    if status == 2:
        raise ValueError("native checksum input is too large")
    if status != 0:
        raise RuntimeError(f"unexpected native status code: {status}")
    return int(out[0])


if __name__ == "__main__":
    sample = b"hello native world"
    assert checksum_native(sample) == checksum_python(sample)
    print(checksum_native(sample))
```

ABI mode loads a binary library and trusts your declarations. It does
not compile your declarations against the C header, so a mismatch may
not be caught until runtime. This example deliberately uses a local,
explicitly resolved library path instead of a generic search path.

### 4.6 CFFI API mode: compile against the header

API mode lets a C compiler check the binding against declarations
included from a header. Use the `checksum.h` created before the C source
in Section 4.1. The `checksum.c` implementation includes that header, so
the implementation and generated binding compile against the same public
declaration. Save the following as `build_ffi.py`:

``` python
from cffi import FFI

ffibuilder = FFI()
ffibuilder.cdef("""
    int checksum_bytes(
        const unsigned char *data,
        size_t length,
        unsigned long long *out
    );
""")
ffibuilder.set_source(
    "_checksum_cffi",
    '#include "checksum.h"',
    sources=["checksum.c"],
    depends=["checksum.h"],
)
if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
```

Run:

``` bash
python build_ffi.py
```

Then save `checksum_cffi_api.py`:

``` python
from _checksum_cffi import ffi, lib
from checksum_reference import MAX_INPUT_BYTES, checksum_python


def checksum_native(data: bytes) -> int:
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    length = len(data)
    if length > MAX_INPUT_BYTES:
        raise ValueError("input exceeds 64 MiB limit")

    out = ffi.new("unsigned long long *")
    data_pointer = ffi.NULL if length == 0 else ffi.new("unsigned char[]", data)
    status = lib.checksum_bytes(data_pointer, length, out)
    if status == 1:
        raise ValueError("native checksum rejected its arguments")
    if status == 2:
        raise ValueError("native checksum input is too large")
    if status != 0:
        raise RuntimeError(f"unexpected native status code: {status}")
    return int(out[0])


if __name__ == "__main__":
    sample = b"hello native world"
    assert checksum_native(sample) == checksum_python(sample)
    print(checksum_native(sample))
```

**Build notes:**

-   API mode needs a C compiler and development headers. Run the build
    command in the project directory so `checksum.h` and `checksum.c`
    are found.
-   The generated extension's filename and ABI tag are chosen by
    CFFI/Python; do not rename it manually.
-   The example compiles `checksum.c` into the generated extension, so
    it does not need to load `libchecksum.so` at runtime.
-   In a real package, declare CFFI as a build/runtime dependency as
    appropriate, include headers and source in the source distribution,
    and test wheel builds on each supported OS/Python/architecture. Do
    not claim a wheel is portable until it has been tested on the
    intended platform matrix.

### 4.7 Run and compare

Build the shared library for the current OS, install CFFI, and run:

``` bash
python checksum_ctypes.py
python checksum_cffi_abi.py
python build_ffi.py
python checksum_cffi_api.py
```

Each wrapper prints the same integer for the same sample. The exact
value is deterministic for this algorithm, but treat the pure-Python
comparison as the primary correctness check rather than copying a number
from a different implementation.

------------------------------------------------------------------------

## 5. Testing the contract and edge cases

Save the following as `test_checksum.py` after creating the reference
and at least one native wrapper. The tests below use `ctypes`; switch
the import to `checksum_cffi_abi` or `checksum_cffi_api` to run the same
public contract against another binding.

``` python
import pytest

from checksum_reference import MAX_INPUT_BYTES, checksum_python
from checksum_ctypes import checksum_native


@pytest.mark.parametrize("data", [
    b"",
    b"a",
    b"hello",
    b"\x00",
    b"\x00inside\x00binary",
    bytes(range(256)),
])
def test_native_matches_reference(data):
    assert checksum_native(data) == checksum_python(data)


def test_large_but_bounded_input():
    data = b"x" * (1024 * 1024)
    assert checksum_native(data) == checksum_python(data)


def test_maximum_supported_input():
    data = b"x" * MAX_INPUT_BYTES
    assert checksum_native(data) == checksum_python(data)


def test_rejects_input_above_limit_before_native_call():
    # This allocates only a 64 MiB + 1 byte Python object. Use a lower
    # configurable limit in a test-specific wrapper if that is too costly
    # for your CI environment.
    data = b"x" * (MAX_INPUT_BYTES + 1)
    with pytest.raises(ValueError, match="64 MiB"):
        checksum_native(data)


@pytest.mark.parametrize("bad", ["text", bytearray(b"x"), memoryview(b"x"), None])
def test_requires_bytes(bad):
    with pytest.raises(TypeError, match="bytes"):
        checksum_native(bad)


def test_deterministic_and_does_not_mutate_input():
    data = b"unchanged"
    before = data[:]
    first = checksum_native(data)
    second = checksum_native(data)
    assert first == second == checksum_python(data)
    assert data == before
```

Install and run:

``` bash
python -m pip install pytest
python -m pytest -q
```

The 64 MiB boundary tests intentionally allocate a sizeable object. In
memory-constrained CI, refactor the wrapper to accept an injected
maximum for unit tests, or use a smaller test-only build limit. Do not
silently remove the production boundary test from the release validation
plan.

### Testing invalid lengths and invalid pointers

The Python wrapper's public API accepts `bytes`, so callers cannot
supply an arbitrary pointer or lie about the length. It tests invalid
lengths by rejecting oversized input before the FFI call. The C function
also checks `length > CHECKSUM_MAX_BYTES` and rejects `data == NULL` for
a nonzero length.

Do **not** test invalid raw pointers by fabricating addresses such as
`ctypes.cast(1, ...)`. Dereferencing a bogus pointer can crash the
interpreter, corrupt memory, or behave differently across operating
systems. A wrapper cannot safely validate arbitrary pointer provenance.
Test the C contract in a separate native test executable under
sanitizers, and test Python-facing validation without constructing
invalid addresses.

For a native-only test of the function's explicit checks, pass a NULL
pointer with nonzero length and a valid output pointer:

``` c
#include <assert.h>
#include <stddef.h>

int checksum_bytes(const unsigned char *, size_t, unsigned long long *);

int main(void) {
    unsigned long long out = 123;
    assert(checksum_bytes(NULL, 1, &out) == 1);
    assert(out == 123); /* failure must not overwrite output */
    assert(checksum_bytes(NULL, 0, &out) == 0);
    return 0;
}
```

Compile the test with `checksum.c` into a separate executable. It tests
only the function's explicit NULL checks; it does not prove that
arbitrary non-NULL pointers are valid.

------------------------------------------------------------------------

## 6. `ctypes` structures, unions, arrays, and output parameters

When the native header exposes a structure, mirror its fields in order
and with exact types. Never infer layout from a diagram or from one
platform's result.

``` python
import ctypes


class Point(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
    ]


class Bounds(ctypes.Structure):
    _fields_ = [
        ("minimum", Point),
        ("maximum", Point),
        ("flags", ctypes.c_uint32),
    ]


class ValueUnion(ctypes.Union):
    _fields_ = [
        ("as_int", ctypes.c_int),
        ("as_double", ctypes.c_double),
    ]


Int10 = ctypes.c_int * 10
values = Int10(*range(10))
point = Point(1.5, -2.0)
bounds = Bounds(Point(0.0, 0.0), Point(10.0, 20.0), 0)
```

The Python declarations above demonstrate the mechanism; they are not a
declaration for an external library. Before using real structures,
verify the header's packing/alignment rules, compiler ABI, field widths,
nested types, and any conditional compilation. `ctypes.sizeof(Point)`,
`ctypes.alignment(Point)`, and field offsets can help diagnose layout,
but do not replace a comparison with authoritative C-side
`sizeof`/`offsetof` values.

### Pointer arguments and `byref`

``` python
import ctypes

lib = ctypes.CDLL("path-to-a-trusted-library")
# Example contract only: int get_value(int *out_value)
lib.get_value.argtypes = [ctypes.POINTER(ctypes.c_int)]
lib.get_value.restype = ctypes.c_int

value = ctypes.c_int()
status = lib.get_value(ctypes.byref(value))
if status != 0:
    raise RuntimeError(f"get_value failed with status {status}")
print(value.value)
```

The library name and `get_value` symbol are placeholders. Do not run
this snippet without replacing them with a real API and matching header.
`byref(value)` provides a pointer to existing storage; it does not
allocate storage owned by the C library.

### Native return codes and output parameters

Many C APIs return a status code and fill output parameters. Treat the
status code as authoritative. Do not read output memory after a failed
call unless the API explicitly documents it as valid. Initialize output
values where helpful for diagnosis, but initialization does not make an
invalid pointer safe.

Some APIs signal errors with a NULL pointer. For a function returning an
opaque pointer, set `restype = ctypes.c_void_p` (or a specific pointer
type) and check for `None`. If the API returns a handle that must be
released, encode that ownership in a `try/finally` or context manager;
never assume Python garbage collection will release native resources.

### `errno` and `use_errno=True`

For a C function documented to set `errno`, load the library with
`use_errno=True`, declare its signature, check the documented failure
sentinel, then call `ctypes.get_errno()` immediately after the failed
call:

``` python
import ctypes
import ctypes.util

name = ctypes.util.find_library("c")
if name is None:
    raise RuntimeError("C runtime not found")
libc = ctypes.CDLL(name, use_errno=True)

# Example: POSIX open() returns -1 on failure and sets errno.
# open() is POSIX-specific; this example is not a Windows API.
libc.open.argtypes = [ctypes.c_char_p, ctypes.c_int]
libc.open.restype = ctypes.c_int

fd = libc.open(b"/path/that/should/not/exist", 0)
if fd == -1:
    error_number = ctypes.get_errno()
    raise OSError(error_number, "open failed")
```

For production POSIX code, use the documented flags and close a
successful file descriptor with `os.close(fd)` or the appropriate native
API. The sample uses a deliberately missing path to demonstrate the
error convention. Do not assume every C library uses `errno`; many
return their own error codes or use an error-output parameter.
`use_errno=True` does not create an `errno` contract where the native
API has none.

------------------------------------------------------------------------

## 7. Callbacks with `CFUNCTYPE`

A callback reverses the direction of the boundary: native code calls a
Python callable through a C-compatible function pointer.

``` python
import ctypes

CALLBACK = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)


def double_value(value: int) -> int:
    return value * 2


callback = CALLBACK(double_value)  # Keep this object alive while C may call it.
```

This creates a callback object, but it does not call anything by itself.
To use it, the native API must document a matching callback signature
and when callbacks may occur.

Critical lifetime rule: retain a strong Python reference to the callback
object for as long as native code can call it. If C stores the callback
beyond the registration call, keep it in a long-lived owner object and
unregister it before releasing the reference or unloading the library.
Otherwise, a later callback can jump through an invalid function
pointer.

Additional cautions:

-   The callback's return and argument types must match exactly.
-   Catch Python exceptions inside the callback and translate them into
    a documented native error result; do not allow exceptions to escape
    through arbitrary C frames.
-   Native callbacks may occur on foreign-created threads. Understand
    the runtime and CFFI/ctypes behavior for the exact call path; do not
    assume thread-local state or context variables behave as they would
    on the initiating Python thread.
-   Keep callback work short and avoid re-entering APIs that can
    deadlock.
-   The GIL and callback behavior differ by runtime/build and by how the
    callback is entered. Test the supported Python versions and thread
    model.

------------------------------------------------------------------------

## 8. Buffers, `memoryview`, and NumPy

Zero-copy is an ownership and lifetime property, not a magic keyword.
Ask four questions for every buffer:

1.  Who allocated it?
2.  Who may mutate it?
3.  How long is it valid?
4.  Can native code retain it after the call?

### `create_string_buffer`

``` python
import ctypes

buffer = ctypes.create_string_buffer(128)  # 128 bytes of writable storage
```

This allocates a writable C character array. If the API writes text,
reserve enough space for any terminating NUL and validate the reported
output length before decoding. A buffer size is not automatically a
guarantee that the C function will respect it; the native API must
accept a capacity or otherwise document a strict bound.

### `from_buffer` versus `from_buffer_copy`

``` python
import ctypes

source = bytearray(b"abc")
Array3 = ctypes.c_ubyte * len(source)

view = Array3.from_buffer(source)       # Shares writable buffer storage
copy = Array3.from_buffer_copy(source)  # Copies bytes into ctypes-owned storage

view[0] = ord("z")
assert source == bytearray(b"zbc")
assert bytes(copy) == b"abc"
```

`from_buffer` requires a writable, compatible buffer and keeps the
exporter alive while the ctypes view exists. The exporter cannot be
resized while an exported buffer view is active. `from_buffer_copy` is
simpler when a stable independent snapshot is more important than
avoiding a copy.

### `memoryview`

A `memoryview` exposes a buffer without necessarily copying it. It does
not make every buffer contiguous, writable, or compatible with every C
function. Before passing a view, check the API's expectations for
contiguity, element format, item size, alignment, and mutability. For an
API that requires contiguous bytes, normalize deliberately (for example,
`view = memoryview(data).cast("B")` only when the source supports the
cast and layout requirements are satisfied) or copy into a controlled
buffer.

### NumPy interoperability

NumPy exposes arrays through the buffer protocol and `numpy.ctypeslib`.
A typical pattern for a C function that expects a contiguous `double *`
is:

``` python
import ctypes
import numpy as np
import numpy.ctypeslib

values = np.ascontiguousarray([1.0, 2.0, 3.0], dtype=np.float64)
pointer = values.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
# Keep `values` alive for the entire native call.
```

This is a pointer to the array's memory, not an owned copy. The pointer
becomes invalid if the array is freed or its storage changes. Validate
dtype, dimensionality, contiguity, alignment, and length before passing
it to C. Do not pass an arbitrary NumPy array to a function expecting
`double *` and hope its representation matches. `data_as` keeps a
reference to the array through the pointer object in common NumPy
implementations, but retaining the array explicitly makes the lifetime
contract clear.

------------------------------------------------------------------------

## 9. CFFI: ABI mode versus API mode

CFFI provides a C-like declaration interface and often feels more
natural for APIs with many pointers and structures.

### ABI mode

Typical steps:

1.  Create an `FFI()` instance.
2.  Declare function/type signatures using `ffi.cdef(...)`.
3.  Load an existing library with `ffi.dlopen(...)`.
4.  Allocate data with `ffi.new(...)`, pass pointers, and read outputs.
5.  Release references only after native code no longer uses them.

ABI mode does not compile the declaration against the real header. It
relies on the caller's declaration being correct and the runtime ABI
matching the library. It is convenient for calling a system/vendor
library but retains ABI mismatch risks.

### API mode

API mode uses `ffi.set_source(...)` and a compiler to build a generated
extension that includes the real header. The C compiler checks
declarations and can expose compiler-checked bindings. It requires a
compiler and proper build configuration. API mode is not automatically
"safe": the native function can still write beyond a buffer, dereference
invalid pointers, or have a defective contract.

### `ffi.new`, `ffi.buffer`, and lifetimes

-   `ffi.new("int *", 42)` allocates C-compatible storage owned by the
    CFFI object.
-   `ffi.new("unsigned char[]", bytes_value)` creates a C array
    initialized from the bytes; keep the returned cdata object alive
    while C uses it.
-   `ffi.buffer(pointer, size)` exposes memory through Python's buffer
    protocol; the programmer must ensure the underlying pointer remains
    valid for the buffer's full lifetime.
-   `ffi.NULL` is a null pointer, not a valid address to dereference.
-   Never pass a pointer to a local buffer to an asynchronous native
    operation unless the buffer is kept alive until completion.

CFFI declarations use C types, not `ctypes` type objects. Read CFFI's
documentation for the exact release and compiler mode you deploy; do not
infer support for a feature from a different mode.

------------------------------------------------------------------------

## 10. ABI correctness: alignment, packing, endianness, and sizes

### Structure layout and packing

C compilers insert padding to satisfy alignment rules. The field order,
alignment, and padding of a structure are part of the ABI. Do not set
`ctypes.Structure._pack_` just to make `sizeof()` match a guessed
number. Use packing only when the C header and compiler contract
explicitly specify packed layout. Packed structures can also cause
unaligned accesses and performance or portability problems.

For API mode, including the real header lets the compiler see its actual
declarations. For ABI mode and `ctypes`, compare against a small C
helper that reports `sizeof(struct T)`, `_Alignof(struct T)`, and
`offsetof(struct T, field)` for the supported build. Repeat this check
for every supported compiler/architecture.

### Endianness

Endianness affects interpretation of multi-byte data stored in memory or
serialized to bytes. A native integer passed by value follows the
platform ABI; a byte protocol has its own endianness contract. Do not
reinterpret network/file bytes as native integers without an explicit
byte order. Use `int.from_bytes(..., "little"|"big")` or an established
serialization API for wire formats.

### Integer widths and overflow

Use `size_t`/`c_size_t` for C object sizes, not `int`. Use `ptrdiff_t`
for C pointer differences where that is the declared API type. Match
signedness. Validate Python integers before converting to a narrower C
integer; otherwise values may be rejected, wrapped, or converted
according to binding-specific rules. Check multiplication and addition
for overflow before allocating `count * element_size` bytes in C. A
length check in Python does not protect a second native entry point or
another caller.

### Calling conventions and symbols

The correct function symbol, calling convention, and signature must
match the compiled library. `CDLL` and `WinDLL` are not interchangeable
guesses. C++ name mangling is not a stable C ABI; use a library's
documented `extern "C"` shim or its official binding rather than
searching for mangled names. Variadic C functions are especially
difficult to declare safely; prefer a non-variadic wrapper when you
control the native code.

------------------------------------------------------------------------

## 11. Performance: batching beats per-element calls

Every FFI call has a fixed cost: argument conversion, transition into
native code, possible GIL handling, and return conversion. For a tiny
operation, this overhead can exceed the work itself. Converting Python
objects to C arrays can also cost more than the native computation.

Prefer an API like `checksum_bytes(pointer, length, out)` over calling
`checksum_one_byte()` once per byte. Batch records, pass contiguous
buffers, and keep conversion work proportional to the useful work. For
numerical data, compare a native loop against NumPy/vectorized
operations that already batch work.

### A fair benchmark plan

Do not paste invented timing numbers into documentation. Measure on your
own machine:

1.  Validate equivalent output first with unit tests.
2.  Compare pure Python, `ctypes`, CFFI ABI mode, and CFFI API mode on
    identical immutable byte inputs.
3.  Include wrapper validation and any conversion/copy in the end-to-end
    measurement; optionally report a separate kernel-only measurement
    with its limitations.
4.  Test several sizes: empty, tiny (for example 16 bytes), medium (64
    KiB), and large (1 MiB or more, within the 64 MiB cap).
5.  Repeat runs, warm imports separately from steady-state timing, avoid
    printing in the timed function, and report Python/compiler/OS/CPU
    and library build flags.
6.  Measure peak memory or copy costs if input conversion is relevant.
7.  Confirm any microbenchmark win in the actual application profile and
    end-to-end workload.

For a quick exploratory comparison, use `time.perf_counter()` around
many repeated calls or `timeit`; for a robust benchmark suite, use the
`pyperf` methodology taught in Lesson 03. Keep benchmark theory in
Lesson 03. Never claim that native code is faster based on a single run
or a kernel-only comparison that omits wrapper costs.

### GIL and concurrency

Do not assume all native calls improve concurrency. The GIL behavior
depends on the binding and call path:

-   `ctypes.CDLL` calls generally release the GIL around the foreign
    function call; `ctypes.PyDLL` is designed for Python C API calls and
    does not release it in the same way.
-   CFFI's behavior differs between ABI/API mode and how the function is
    invoked; consult the documentation for the deployed CFFI version and
    test the exact call path.
-   Releasing the GIL permits other Python threads to run, but does not
    make a single native call faster by itself.
-   Two threads calling a non-thread-safe library can race. Native
    global state, callback re-entry, locks, and I/O semantics still
    matter.
-   On free-threaded Python builds, runtime behavior and extension
    compatibility differ; test the specific interpreter and
    dependencies.
-   A long-running native call may block the calling thread, and
    callbacks into Python can reintroduce GIL/runtime constraints.

Treat thread safety and GIL behavior as API-specific properties to
verify, not as a performance guarantee.

------------------------------------------------------------------------

## 12. Packaging, wheels, compatibility, and licensing

### Runtime-loaded library

For `ctypes` or CFFI ABI mode, the shared library must be present and
discoverable at runtime. Decide whether it is:

-   a documented system dependency installed by the operating
    system/package manager;
-   a vendor-provided library installed in a known location;
-   a library bundled inside your package and loaded through a carefully
    resolved package-relative path.

Do not assume a wheel can bundle any arbitrary native dependency and
remain portable. Linux wheels may require manylinux-compatible builds
and tools such as `auditwheel`; macOS wheels may require correct
deployment targets and `delocate`; Windows wheels need compatible DLL
dependencies and a safe loading strategy. Validate the actual artifacts
on the target platform matrix. Platform tags, libc baseline,
architecture, Python ABI, and transitive dependencies all matter.

CFFI API-mode builds produce platform-specific extension binaries.
Include the source/header needed for source distributions, declare
build-system requirements, and test isolated wheel builds. A local
editable install is not proof that an sdist or wheel is complete.

### Licensing and supply chain

Review the native library's license, notices, redistribution terms,
patent clauses where relevant, and obligations for static versus dynamic
linking. LGPL and other copyleft licenses can impose conditions that
need legal review; do not summarize a license as "safe" without
examining the exact version and distribution model. Record the upstream
version, checksum/provenance, build options, and security update
process.

### Dynamic library loading risks

A library load executes native code with the privileges of the Python
process. A path controlled by an untrusted user can enable arbitrary
code execution. Search-path hijacking can also load an unintended
library.

Production controls:

-   Prefer absolute paths resolved from a trusted installation location.
-   Avoid current-working-directory and user-writable-directory search
    when resolving privileged components.
-   Do not trust environment variables such as `LD_LIBRARY_PATH` or
    `PATH` in a privileged/service deployment without a threat
    assessment.
-   On Windows, use documented safe DLL-loading mechanisms and trusted
    directories; avoid ambiguous bare DLL names.
-   Verify the expected library/version/symbols where feasible;
    signatures alone do not establish provenance.
-   Run with least privilege, keep dependencies patched, and inventory
    transitive native dependencies.
-   Treat plugins, native libraries, and callback registration as
    executable code, not passive data.

------------------------------------------------------------------------

## 13. Debugging native failures

### Python-side diagnostics

Enable fault handling early in a diagnostic run:

``` python
import faulthandler
faulthandler.enable()
```

`faulthandler` can print Python tracebacks for certain fatal signals and
faults, but it does not make memory corruption recoverable. The process
may terminate without a useful traceback, especially if native code
corrupts state.

### Native debuggers and core dumps

-   **Linux:** `gdb --args python your_script.py`, then `run`, `bt`, and
    `thread apply all bt` after a crash. Core dumps may require
    OS/container configuration (`ulimit -c`, system core-pattern
    policy).
-   **macOS:** use LLDB/Xcode tools and the platform's crash reports;
    exact core-dump workflows differ by system configuration.
-   **Windows:** use Visual Studio's native debugger or WinDbg; inspect
    the native stack and module list.
-   **Valgrind:** useful on supported Unix-like systems for invalid
    reads/writes and leaks, though it can be slow and may require a
    compatible build/runtime.
-   **AddressSanitizer (ASan) / UndefinedBehaviorSanitizer (UBSan):**
    compile native code with sanitizer flags, for example
    `-fsanitize=address,undefined -fno-omit-frame-pointer -g` on
    supported GCC/Clang toolchains. Runtime preload/configuration can be
    needed when instrumented code is loaded into Python. A standalone
    native test executable is often the simplest first step.
-   **Windows sanitizers:** use the compiler's supported diagnostics and
    sanitizer capabilities; flags and runtime support differ from
    GCC/Clang.

Example Linux debugging build:

``` bash
cc -std=c11 -O1 -g -Wall -Wextra -Wpedantic \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  checksum.c native_contract_test.c -o native_contract_test
./native_contract_test
```

This command assumes `native_contract_test.c` is the standalone test
shown earlier. Sanitizers can find defects in instrumented code and
execution paths; they do not prove the absence of bugs and may not
instrument prebuilt dependencies.

### Failure triage

  -----------------------------------------------------------------------
  Symptom               Likely causes             First checks
  --------------------- ------------------------- -----------------------
  Process crashes at    Wrong signature, bad      Verify header,
  call                  pointer, calling          `argtypes`/`restype`,
                        convention, ABI mismatch  architecture, debugger
                                                  backtrace

  Returned pointer      Missing/wrong `restype`,  Declare pointer return
  looks truncated       wrong pointer type        explicitly; never route
                                                  pointers through
                                                  `c_int`

  Garbled structure     Packing/alignment/field   Compare `sizeof`,
  fields                type mismatch             alignment, offsets with
                                                  C helper

  Works once, crashes   Retained pointer outlives Document ownership and
  later                 buffer, callback          unregister lifecycle
                        collected, native race    

  `OSError` loading     Wrong path, missing       Inspect file format and
  library               transitive dependency,    loader diagnostics
                        wrong architecture        

  Incorrect output only NUL termination, length,  Use pointer-plus-length
  for binary data       signedness, encoding,     API and binary test
                        byte order                cases

  Deadlock or poor      Native lock, callback,    Minimize reproducer;
  concurrency           GIL, non-thread-safe      inspect all thread
                        library                   stacks
  -----------------------------------------------------------------------

Do not keep rerunning a crashing process with production data. Reproduce
with bounded test input in an isolated environment and capture native
diagnostics.

------------------------------------------------------------------------

## 14. Common mistakes

1.  **Omitting `argtypes` or `restype`.** Default `int` returns can
    truncate pointer values and misinterpret 64-bit results.
2.  **Using `c_int` for `size_t`.** Large lengths can be truncated or
    converted incorrectly.
3.  **Passing `str` where C expects bytes.** Encode deliberately and
    specify the encoding.
4.  **Using `c_char_p` for arbitrary binary data.** Embedded NUL bytes
    have string semantics; prefer pointer plus length.
5.  **Assuming a pointer is valid because it is non-NULL.** FFI wrappers
    cannot validate arbitrary memory provenance or bounds.
6.  **Allowing native code to retain temporary buffers.** Keep owners
    alive until native use is complete; design explicit
    registration/unregistration for asynchronous APIs.
7.  **Dropping a callback reference.** Keep `CFUNCTYPE` objects alive as
    long as native code may invoke them.
8.  **Guessing struct packing or calling convention.** Verify the actual
    header and platform ABI.
9.  **Assuming zero-copy is automatically faster.** Copies can be safer
    and faster for small payloads.
10. **Assuming native means concurrent or faster.** GIL, locks,
    conversion, and call overhead matter.
11. **Loading a bare library name from an untrusted search path.**
    Library loading is code execution.
12. **Benchmarking only the C kernel.** Include validation and
    conversion costs for end-to-end claims.
13. **Testing invalid pointers by fabricating addresses.** Such tests
    can crash the interpreter and do not create a useful safety proof.
14. **Claiming compatibility from one machine.** Build and test every
    supported OS, architecture, Python version, and compiler
    combination.

------------------------------------------------------------------------

## 15. Security review checklist for an FFI

Before production approval, answer each item with evidence:

-   [ ] Is the library from a trusted source, pinned to an expected
    version, and covered by a patch/update process?
-   [ ] Is the resolved path absolute or otherwise constrained to a
    trusted installation directory?
-   [ ] Can current directory, `PATH`, `LD_LIBRARY_PATH`, plugin
    directories, or user-writable paths alter which binary is loaded?
-   [ ] Are all native signatures copied from the authoritative header
    and checked for calling convention, pointer level, signedness, and
    return type?
-   [ ] Are lengths, counts, multiplication, and output capacities
    bounded before the call and checked again in C where relevant?
-   [ ] Are NULL pointers and error codes handled according to the
    documented contract?
-   [ ] Is every pointer's owner and lifetime documented, including
    asynchronous use and callbacks?
-   [ ] Are output buffers writable and large enough according to a
    native API that accepts capacity?
-   [ ] Are text encoding and NUL-termination rules explicit?
-   [ ] Are structure layout, packing, and platform-dependent integer
    sizes verified?
-   [ ] Are native errors translated into predictable Python exceptions
    without reading invalid outputs?
-   [ ] Is the library thread-safe for the actual call pattern, and is
    GIL behavior verified for supported runtimes?
-   [ ] Are native tests run with sanitizers or other memory diagnostics
    where practical?
-   [ ] Are wheels and transitive dependencies tested on the supported
    platform matrix?
-   [ ] Are licensing and redistribution obligations reviewed?
-   [ ] Are crash diagnostics available without exposing sensitive
    production data?

A checked box means a review artifact, test, or documented contract
exists. It does not mean "the sample ran once."

------------------------------------------------------------------------

## 16. Troubleshooting the lab

**`FileNotFoundError` for the library**\
Build the shared library from the correct directory. Check the expected
OS-specific filename and ensure the wrapper and library are in the same
directory. Do not "fix" the problem by loading an arbitrary library from
the system path.

**`OSError: ... cannot open shared object file` or Windows DLL load
failure**\
The file may exist while a transitive dependency is missing, the
architecture may not match, or the runtime loader may not search the
expected directory. Inspect the dependency list with platform tools
(`ldd`/`readelf` on Linux, `otool -L` on macOS, Dependencies or dumpbin
on Windows). Do not run `ldd` on untrusted binaries in
security-sensitive workflows.

**CFFI cannot find a compiler or header**\
Install the appropriate build tools, run `build_ffi.py` from the
directory containing `checksum.c` and `checksum.h`, and verify the
compiler is available in the shell used to run Python. API mode requires
compilation; ABI mode does not compile the binding.

**CFFI `VerificationError`, compile error, or missing symbol**\
Compare `cdef` with `checksum.h` and the compiled source. Ensure the
function is exported with the expected symbol name and no C++ name
mangling. Do not "fix" a declaration mismatch by casting pointers.

**Different checksum results**\
Check that both implementations use the same offset basis, prime, byte
sequence, unsigned 64-bit wraparound, and exact length. Run the
edge-case tests before benchmarking.

**Crash after a call returns**\
Look for retained pointers, callback lifetime, incorrect `restype`,
structure layout, and writes beyond a native output buffer. Reproduce
under a native debugger or sanitizer; a Python traceback may not be
available.

------------------------------------------------------------------------

## 17. Relationship to profiling and memory analysis

Use the earlier lessons to justify and validate this boundary:

1.  **Profile first** (Lessons 01--02): establish whether Python code or
    a native library is actually hot.
2.  **Benchmark carefully** (Lesson 03): define equivalent work and
    include conversion and call overhead.
3.  **Measure memory** (Lessons 04--06): understand whether buffers are
    copied, retained, or allocated natively. `tracemalloc` does not
    account for every allocation made by arbitrary native libraries.
4.  **Apply Python-level improvements** (Lesson 07): remove algorithmic
    waste before adding FFI complexity.
5.  **Use this lesson** to call an existing C ABI with explicit
    contracts and bounded inputs.
6.  **Move to Lesson 09** only if the requirement needs a purpose-built
    extension, richer Python object integration, or a more controlled
    native build architecture.

For the shared `slowlog` log-analysis/ETL project, do not invent a
native kernel merely to use this lesson. Identify a bounded, measurable
text/byte-scanning or checksum operation, compare outputs against a
Python reference, and record whether the FFI boundary improves the
end-to-end workload. If the workload is I/O-bound or parsing dominates
elsewhere, the correct conclusion may be not to retain the native
implementation.

------------------------------------------------------------------------

## 18. Exercises

### Exercise A --- signatures and return types

Given a C header declaring
`size_t count_bytes(const unsigned char *data, size_t length);`, write a
`ctypes` declaration. Explain why `c_int` is wrong for the return type
and why a NULL pointer with a nonzero length is only valid if the API
contract says so.

### Exercise B --- struct layout

Define a C structure with `char tag; double value; unsigned int flags;`.
Write a matching `ctypes.Structure`. Write a C helper reporting
`sizeof`, `_Alignof`, and each `offsetof`; compare the results on two
supported platforms. Do not add `_pack_` unless the header explicitly
requires it.

### Exercise C --- callbacks

Find a native API that accepts a callback. Document its signature,
registration lifetime, unregister sequence, callback thread model,
exception translation, and behavior during shutdown. Demonstrate that
the Python callback object remains strongly referenced until after
unregistration.

### Exercise D --- buffers

Extend a native function to fill a caller-provided output buffer with a
capacity parameter. Define its behavior when the capacity is too small
and test it under ASan/UBSan. The function must never write more than
the supplied capacity.

### Exercise E --- benchmark and decide

Compare the reference checksum and both FFI wrappers on empty, tiny,
medium, and large inputs. Report distributions and environment metadata,
include copies and wrapper validation, and verify identical output.
Explain at which input size (if any) native execution repays the
boundary cost. Do not fabricate a speed-up if results are noisy or
negative.

------------------------------------------------------------------------

## 19. Self-check questions

1.  Why is leaving `restype` at its default dangerous for a function
    that returns a pointer?
2.  Why should `size_t` map to `ctypes.c_size_t` rather than `c_int`?
3.  When is `c_char_p` unsuitable for a buffer containing embedded NUL
    bytes?
4.  What can `ctypes` or CFFI validate, and what can they not prove
    about an arbitrary pointer?
5.  What is the practical difference between CFFI ABI mode and API mode?
6.  Why must a `CFUNCTYPE` callback object remain alive while C may call
    it?
7.  Why is a successful one-time run not evidence that a structure
    declaration is correct?
8.  How can copying a buffer be a safer and even faster choice than a
    zero-copy path?
9.  Under what conditions can an FFI call release the GIL, and why does
    that not guarantee thread safety?
10. Why is loading a native library from a user-controlled directory a
    code-execution risk?
11. Which measurements distinguish a faster native kernel from a slower
    end-to-end wrapper?
12. When should you stop optimizing Python and consider Lesson 09's
    extension-module options?

------------------------------------------------------------------------

## 20. Final FFI implementation task

Deliver a small, reviewable repository with:

``` text
ffi-checksum-lab/
├── checksum.c
├── checksum.h
├── checksum_reference.py
├── checksum_ctypes.py
├── checksum_cffi_abi.py
├── build_ffi.py
├── checksum_cffi_api.py
├── test_checksum.py
├── benchmark_checksum.py
└── README.md
```

Requirements:

1.  Implement the C function with a bounded length, explicit return-code
    contract, and no retained pointers.
2.  Implement the pure-Python reference and both `ctypes` and CFFI
    wrappers.
3.  Add tests for empty, ordinary, embedded-NUL, large, maximum,
    over-limit, and invalid Python input cases. Do not fabricate invalid
    memory addresses.
4.  Run the tests against every wrapper and record
    Python/compiler/OS/architecture details.
5.  Run native contract tests under sanitizers when available; record
    toolchain limitations honestly.
6.  Benchmark multiple sizes with equivalent outputs and end-to-end
    conversion costs. Do not report unmeasured results.
7.  Document library provenance, build commands, runtime dependency
    strategy, license, supported platforms, and failure behavior.
8.  Complete the security checklist and identify any unverified
    assumptions.
9.  Include a decision memo: keep the FFI only if correctness,
    maintenance cost, deployment complexity, and measured end-to-end
    performance justify it.
10. State clearly that the checksum is not cryptographic.

### Acceptance criteria

-   [ ] Exact native signatures are declared and reviewed against the
    header.
-   [ ] All wrappers match the pure-Python reference on the tested
    cases.
-   [ ] Empty input is handled without dereferencing NULL.
-   [ ] Lengths are bounded in both the Python wrapper and native
    function.
-   [ ] Buffer and callback lifetimes are documented.
-   [ ] No test fabricates or dereferences an invalid address.
-   [ ] Native failures are translated into explicit Python errors.
-   [ ] Build and loading behavior is verified on every claimed
    platform.
-   [ ] Benchmark methodology includes wrapper/conversion cost and no
    invented measurements.
-   [ ] The final decision follows evidence, not the assumption that
    native code is always faster.

## Further reading

Prefer primary documentation for the exact Python/CFFI version and
target OS:

-   Python `ctypes`: <https://docs.python.org/3/library/ctypes.html>
-   Python `ctypes.util`:
    <https://docs.python.org/3/library/ctypes.html#finding-shared-libraries>
-   CFFI documentation: <https://cffi.readthedocs.io/>
-   C standard integer and size types:
    <https://en.cppreference.com/w/c/types/integer.html> and
    <https://en.cppreference.com/w/c/types/size_t.html>
-   Python packaging binary distribution guidance:
    <https://packaging.python.org/en/latest/guides/packaging-binary-extensions/>
-   manylinux policy and tooling: <https://github.com/pypa/manylinux>
-   AddressSanitizer:
    <https://clang.llvm.org/docs/AddressSanitizer.html>
-   Valgrind: <https://valgrind.org/docs/manual/manual.html>

API details and platform loader behavior can change. Confirm the docs
for the Python, CFFI, compiler, and operating-system versions you
actually deploy.
