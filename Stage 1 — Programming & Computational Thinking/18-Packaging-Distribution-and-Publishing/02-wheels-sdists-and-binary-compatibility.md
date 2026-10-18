# Wheels, Source Distributions, and Binary Compatibility

> **Stage 1 — Programming & Computational Thinking · Module 18 — Packaging, Distribution and Publishing**  
> Baseline: Python 3.12+; examples use `tinytools` version `0.1.0`. Native-wheel examples refer to the stated interpreter, ABI, operating-system, libc, and architecture tags; a filename alone is not proof that a binary actually satisfies its declared compatibility.

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Explain the purpose and installation behavior of source distributions (sdists) and wheels.
- Decode wheel filenames and distinguish Python, ABI, and platform compatibility tags.
- Inspect archives, metadata, package data, and `.dist-info` records.
- Understand how installers select compatible wheels and what platform overrides do—and do not—guarantee.
- Configure package inclusion rules and diagnose missing runtime files.
- Explain native wheel production, Linux compatibility policies, stable ABI trade-offs, and platform repair tools.
- Investigate common resolver/build failures and test built artifacts rather than only the source checkout or an editable install.

### Prerequisites

You should know Python imports and packages, virtual environments, `pyproject.toml`, runtime versus development dependencies, version specifiers, source (`src/`) layouts, and basic tests. The preceding lesson, **Build Backends and PEP 517**, explains how a frontend calls a backend to create artifacts. Module 1.6 covers project layout, dependency management, and `uv`; Module 1.16 covers testing installed artifacts.

This lesson uses `uv`, `pip`, Python's `zipfile` and `tarfile` modules, and common archive utilities. Exact command options may vary by tool version; consult the linked current documentation when upgrading toolchains.

## 2. Mental model: two artifacts, different jobs

A source repository is designed for contributors. A distribution artifact is designed for another machine to install. The repository may contain tests, CI configuration, documentation sources, benchmarks, and development scripts that should not be shipped. Conversely, the artifact must contain every module and runtime resource needed by an installed user.

### 2.1 Source distribution (sdist)

An **sdist** is a source archive, conventionally named `name-version.tar.gz`. A modern standardized sdist contains the source files and a `PKG-INFO` metadata file, plus the required sdist structure. A frontend can unpack it and ask a backend to build a wheel from it.

An sdist is valuable because it makes source available for review and allows a wheel to be built for an environment that does not have a prebuilt compatible wheel. It may need a compiler, headers, system libraries, build dependencies, and executable build code. An sdist is not necessarily a complete copy of the Git repository.

### 2.2 Wheel

A **wheel** is a built distribution with the `.whl` extension. It is a ZIP-format archive with a defined layout and metadata. A compatible wheel can usually be installed by unpacking files into the environment's installation scheme; it does not normally require rebuilding the package from source.

A pure-Python wheel often contains `.py` modules and package data. A native wheel can also contain compiled extension modules and bundled shared libraries. The wheel format itself does not guarantee that a native library is portable, safe, or compatible merely because the filename says it is.

### 2.3 Comparison

| Property | Source distribution (`.tar.gz`) | Wheel (`.whl`) |
|---|---|---|
| Primary purpose | Provide source and build metadata | Provide a built, installable distribution |
| Common contents | Source files, `PKG-INFO`, build inputs | Installed package files, `.dist-info`, sometimes native binaries/resources |
| Installation | Usually requires a build step to create a wheel | Compatible wheel is generally unpacked and recorded |
| Compiler required? | Possibly, depending on the project/backend | Usually not for the already-built artifact, though runtime system libraries may still be needed |
| Build code executed on consumer machine? | Often, while building from source | Normally not as part of wheel installation; installed application code still runs when imported or invoked |
| Portability | Source can be rebuilt for a target environment if all inputs and toolchains are available | Limited by the wheel's Python, ABI, platform, architecture, and external-library compatibility |
| Best practice for public release | Publish it so users can inspect source and build where needed | Publish one or more wheels for supported environments, alongside the sdist |

**Production rule:** for a library intended for broad distribution, publish the sdist and all wheels you claim to support. An sdist alone may leave native-package users compiling from source; a wheel-only release removes the canonical source archive and can reduce fallback options.

### 2.4 Why wheels often install faster

With an sdist, an installer generally has to unpack the archive, prepare a build environment, install build requirements, invoke the backend, and install the resulting wheel. A compatible wheel skips that package build. The installer still resolves dependencies, downloads files, validates metadata, and installs files.

A wheel can reduce exposure to build-time code execution because a normal wheel installation does not need to run the source project's build backend. It is not inherently risk-free: the wheel's code executes when used, its contents may be malicious, a native extension can have vulnerabilities, and the package may depend on unsafe runtime components. Prefer trusted sources, verify provenance where available, and test artifacts.

## 3. Build the running example: `tinytools`

Start with this minimal pure-Python package. It gives us concrete artifacts to inspect before discussing platform-specific wheels.

```text
tinytools-project/
├── pyproject.toml
├── README.md
├── LICENSE
└── src/
    └── tinytools/
        ├── __init__.py
        ├── core.py
        ├── data/
        │   └── defaults.json
        └── py.typed
```

### 3.1 `pyproject.toml`

```toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "tinytools"
version = "0.1.0"
description = "Small utilities for data engineering examples"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
license-files = ["LICENSE"]
authors = [{ name = "Tinytools Maintainers" }]
classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.12",
  "Operating System :: OS Independent",
]
dependencies = []

[tool.hatch.build.targets.wheel]
packages = ["src/tinytools"]

[tool.hatch.build.targets.sdist]
include = [
  "/pyproject.toml",
  "/README.md",
  "/LICENSE",
  "/src/tinytools",
]
```

`license = "MIT"` is the SPDX license expression style standardized by PEP 639; `license-files` names the license text to include. Use a valid SPDX expression and confirm the license file matches it. The minimum `hatchling>=1.27` is intentional: Hatchling 1.27.0 introduced support for PEP 639 metadata; an older backend may reject or mishandle this configuration. Backend options under `[tool.hatch.*]` are Hatchling-specific, not universal `pyproject.toml` keys.

### 3.2 Python package and resource

`src/tinytools/__init__.py`:

```python
from .core import normalize_name

__all__ = ["normalize_name"]
```

`src/tinytools/core.py`:

```python
from importlib.resources import files
import json


def normalize_name(value: str) -> str:
    """Return a normalized name suitable for simple examples."""
    return " ".join(value.strip().lower().split())


def load_defaults() -> dict[str, object]:
    """Load defaults shipped inside the installed package."""
    resource = files("tinytools").joinpath("data", "defaults.json")
    return json.loads(resource.read_text(encoding="utf-8"))
```

`src/tinytools/data/defaults.json`:

```json
{
  "timeout_seconds": 10,
  "strict": true
}
```

`src/tinytools/py.typed` is an empty marker file indicating that the package provides inline type information, as described by PEP 561. Its presence in the source tree is not enough: it must be included in the built wheel.

`README.md` should explain the package and installation. `LICENSE` should contain the actual license text; do not copy a license identifier into a file and assume that is the complete license.

### 3.3 Build both artifacts

From `tinytools-project/`, with a current `uv` installation:

```bash
uv build
```

Expected artifact names for this static version and a pure-Python project are typically:

```text
dist/tinytools-0.1.0.tar.gz
dist/tinytools-0.1.0-py3-none-any.whl
```

These are expected names, not a claim that this command was executed here. Build-tool versions and configuration can affect output details. `uv build` normally builds both an sdist and wheel; check the actual files created in `dist/`.

You can also use the PyPA `build` frontend:

```bash
python -m pip install build
python -m build
```

If the project uses a build backend with requirements that are not installed in the invoking environment, `build` normally creates an isolated environment for those requirements. Do not confuse installing the frontend (`build`) with installing the backend (`hatchling`).

## 4. Decode wheel filenames

The general wheel filename structure is:

```text
{distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl
```

The optional build tag is uncommon and, when present, must begin with a digit. Filename components are normalized according to the wheel specification. The three compatibility tags answer separate questions:

1. **Python tag:** Which Python implementation/version family is supported?
2. **ABI tag:** Which application binary interface is required?
3. **Platform tag:** Which operating system, architecture, and platform policy are targeted?

### 4.1 Pure Python example

```text
tinytools-0.1.0-py3-none-any.whl
```

- `tinytools`: normalized distribution name.
- `0.1.0`: package version.
- `py3`: Python 3 implementation family, not a promise about every possible Python 3 feature level. `Requires-Python` and actual code compatibility still matter.
- `none`: no specific Python ABI is required.
- `any`: no platform-specific binary restriction is declared.

A pure-Python wheel is often compatible across many Python 3 implementations and platforms, but only if the code and dependencies truly support them. In the example project, `requires-python = ">=3.12"` narrows the supported interpreter versions even though the wheel tag says `py3`.

### 4.2 Native example

```text
numpy-2.1.0-cp313-cp313-manylinux_2_17_x86_64.whl
```

| Component | Interpretation |
|---|---|
| `numpy` | Distribution name |
| `2.1.0` | Distribution version |
| `cp313` (Python tag) | CPython 3.13 |
| `cp313` (ABI tag) | CPython 3.13's version-specific ABI; this is not the stable `abi3` ABI |
| `manylinux_2_17_x86_64` (platform tag) | x86-64 Linux wheel built for the manylinux policy associated with glibc 2.17 compatibility, subject to that policy's other constraints |

This is a filename interpretation exercise. It does not assert that this exact artifact is currently published or appropriate for every Linux distribution. Actual compatibility also depends on architecture, CPU instruction requirements, shared libraries, and the package's implementation.

### 4.3 Tags can be compressed in filenames

A wheel can express multiple compatible tags using dot-separated components, such as `py2.py3-none-any`. In the `WHEEL` metadata file, the corresponding tags are represented as separate `Tag:` fields. A filename's tag triple is shorthand for compatibility claims; it is not a complete software bill of materials.

## 5. Inspecting wheel and sdist contents

### 5.1 List archive contents

On Linux/macOS, with `unzip` available:

```bash
unzip -l dist/tinytools-0.1.0-py3-none-any.whl
tar -tzf dist/tinytools-0.1.0.tar.gz
```

On Windows PowerShell, `tar -tf dist/tinytools-0.1.0.tar.gz` is commonly available, and Python's standard library is portable across platforms.

To inspect a wheel without an external archive program:

```bash
python -m zipfile -l dist/tinytools-0.1.0-py3-none-any.whl
```

To inspect an sdist:

```bash
python -m tarfile -l dist/tinytools-0.1.0.tar.gz
```

These commands list files; they do not prove that the package imports or that every resource works.

### 5.2 Required and common `.dist-info` files

A wheel contains a directory similar to:

```text
tinytools-0.1.0.dist-info/
├── METADATA
├── WHEEL
├── RECORD
├── entry_points.txt       # only when entry points are defined
└── licenses/              # when license files are recorded under PEP 639 metadata
    └── LICENSE
```

The exact file set varies. `entry_points.txt` is present when the distribution declares entry points; it is not required for every wheel. The wheel specification requires at minimum `METADATA`, `WHEEL`, and `RECORD` in `.dist-info`.

- **`METADATA`:** Core Metadata for the distribution. It can include `Name`, `Version`, `Requires-Python`, `Requires-Dist`, `Provides-Extra`, classifiers, project URLs, and license metadata, depending on what the project declares and what metadata version is used.
- **`WHEEL`:** Metadata about the wheel format and build, including `Wheel-Version`, `Generator`, `Root-Is-Purelib`, and one or more `Tag` entries.
- **`RECORD`:** A list of files in the wheel and their hashes/sizes as specified by the wheel format. `RECORD` itself cannot contain its own hash. It helps installers detect archive-integrity mismatches; it is not a publisher signature or proof of trustworthy origin.
- **`entry_points.txt`:** The legacy-compatible serialized entry-point declarations used by installers and `importlib.metadata`; present only if applicable.
- **`licenses/`:** License files recorded through modern PEP 639/Core Metadata handling may be installed under `.dist-info/licenses/`.

For example, `METADATA` may include:

```text
Metadata-Version: 2.4
Name: tinytools
Version: 0.1.0
Summary: Small utilities for data engineering examples
Requires-Python: >=3.12
License-Expression: MIT
License-File: LICENSE
```

This is illustrative: the precise metadata version and formatting depend on the backend and the standards it supports. Do not hand-edit built metadata; fix the source metadata/configuration and rebuild.

### 5.3 Inspect selected metadata

Use Python to inspect files without extracting the archive:

```python
from pathlib import Path
from zipfile import ZipFile

wheel = next(Path("dist").glob("tinytools-*.whl"))
with ZipFile(wheel) as archive:
    names = archive.namelist()
    print("Package files:")
    for name in names:
        if name.startswith("tinytools/"):
            print(name)

    metadata_name = next(
        name for name in names if name.endswith(".dist-info/METADATA")
    )
    print("\nMETADATA:\n")
    print(archive.read(metadata_name).decode("utf-8"))
```

This example assumes exactly one matching wheel and a valid `.dist-info/METADATA`; handle `StopIteration` and malformed archives in production tooling. Never extract an untrusted archive into a sensitive directory without considering path traversal and other archive risks.

### 5.4 What to check in each artifact

For the wheel, verify that it contains:

- `tinytools/__init__.py` and `tinytools/core.py` in the expected package path;
- `tinytools/data/defaults.json`;
- `tinytools/py.typed`;
- expected `.dist-info` metadata and license files.

For the sdist, verify it contains the build configuration, source package, README, license, and every file needed to rebuild the wheel. The sdist need not include every test or CI file, but a backend must be able to build from the contents of the sdist itself, not from files that only exist in the author's checkout.

## 6. How installers select wheels

### 6.1 Compatibility is a set, not a single Python version

An installer computes an ordered list of tags supported by its target interpreter and platform. A wheel is eligible when one of the wheel's tags intersects that supported set and its metadata constraints are satisfied. When multiple wheels match, installers prefer the best-ranked compatible candidate according to their compatibility ordering and resolver behavior.

For example, a CPython 3.12 environment might support a range of tags including version-specific CPython tags, `abi3` tags where applicable, and pure-Python tags. Exact results depend on the Python build, operating system, architecture, libc, and versions of the `packaging`/installer tooling.

Inspect the current environment:

```bash
python -m pip debug --verbose
```

Read the “Compatible tags” section. It is environment-specific; do not paste a tag list from one computer into a release policy for all users.

### 6.2 Common Python and ABI tags

| Tag | Meaning and caveats |
|---|---|
| `cp312` | CPython 3.12 when used as the interpreter tag. As an ABI tag it identifies the CPython 3.12 ABI. The same text in two positions has different meanings. |
| `abi3` | Uses CPython's stable ABI/limited API mechanism, allowing a compatible extension to support multiple CPython versions. The extension must actually be built and tested for that contract. |
| `py3-none-any` | Pure-Python-style tag with no specific ABI/platform requirement, subject to `Requires-Python` and real code compatibility. |
| `cp313-cp313t` | A common free-threaded CPython 3.13 wheel tag: `cp313` is the interpreter tag and `cp313t` is the free-threaded ABI tag. Do not interpret `cp313t` as the interpreter tag in this filename. |
| `none` | No Python ABI requirement is declared for that tag. It does not mean the package has no dependencies. |

The tag ecosystem evolves with Python implementations and ABI changes. Use current `packaging.tags` documentation rather than maintaining your own parser or inferring support from a version number alone.

### 6.3 Platform tags: Linux, macOS, Windows, and architecture

| Example | Meaning |
|---|---|
| `manylinux_2_28_x86_64` | Linux x86-64 wheel built to a manylinux policy associated with glibc 2.28 compatibility, with additional policy constraints. |
| `manylinux_2_17_aarch64` | Linux ARM64/AArch64 wheel using the manylinux glibc 2.17 baseline, subject to policy constraints. |
| `musllinux_1_2_x86_64` | Linux x86-64 wheel targeting musl libc 1.2 policy, relevant to musl-based systems such as Alpine Linux. It is not interchangeable with manylinux. |
| `macosx_11_0_arm64` | macOS ARM64 wheel with a stated deployment target. Compatibility depends on macOS deployment target and architecture rules. |
| `win_amd64` | Windows x86-64 platform tag; it does not mean ARM64 Windows. |
| `win_arm64` | Windows ARM64 platform tag when supported by the toolchain and installer. |
| `linux_aarch64` | A Linux ARM64 tag, but unlike a compliant manylinux tag it does not itself promise broad glibc compatibility. |

A wheel can still fail on a machine that appears to match its tag if it requires an unavailable external shared library, unsupported CPU instructions, or a system feature not captured by the tag. Tags are necessary compatibility metadata, not a substitute for testing.

### 6.4 `uv pip install --python-platform`

`uv pip install` supports platform selection options for resolution/installation workflows, for example:

```bash
uv pip install --python-platform x86_64-unknown-linux-gnu some-package
```

The accepted target triple/values and behavior depend on the `uv` version and command. Consult `uv pip install --help` and current `uv` documentation for exact supported targets. A platform override helps select distributions for a target environment; it does **not** emulate that operating system, compile a native extension, guarantee all external libraries exist, or prove that the resulting environment can run on the target. Cross-platform resolution is not cross-platform testing.

### 6.5 `--only-binary` and `--no-binary`

```bash
python -m pip install --only-binary :all: some-package
python -m pip install --no-binary :all: some-package
```

- `--only-binary :all:` tells pip not to use source distributions for the selected requirement set. It can avoid local compiler/build steps and reduce build-time code execution, but installation fails if no acceptable wheel exists for a required package.
- `--no-binary :all:` tells pip to prefer/use source distributions instead of wheels for the selected requirement set. This can be useful for controlled source builds or debugging, but can greatly increase installation time and expose the environment to build scripts and native toolchain complexity.

These are pip options. Equivalent behavior and syntax in other installers may differ. They affect distribution selection; they do not prove the chosen artifact is safe or reproducible.

## 7. Package inclusion rules: source tree, sdist, and wheel

A common packaging defect is a file that exists in the repository but not in the published wheel. Another is a file that appears in the wheel but is absent from the sdist, so downstream users cannot rebuild it.

### 7.1 Different artifacts can have different file sets

- **Source tree:** all tracked and untracked local project files.
- **Sdist:** the files selected for source distribution and needed to rebuild.
- **Wheel:** the installable files selected for the target package distribution.

Do not assume that a Git-tracked file is automatically included by every backend, or that every file in an sdist belongs in the wheel. Build from the sdist in a clean environment to test that source archive's completeness.

### 7.2 Setuptools and `MANIFEST.in`

For a setuptools project, `MANIFEST.in` is a source-distribution file-selection mechanism. For example:

```text
# MANIFEST.in (setuptools-specific)
include README.md
include LICENSE
recursive-include src/tinytools *.py *.json py.typed
```

This controls sdist file inclusion under setuptools' rules. It does not by itself guarantee that every file is installed into a wheel; package discovery and package-data configuration still matter. Setuptools projects may use configuration such as:

```toml
[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
tinytools = ["py.typed", "data/*.json"]
```

These keys are setuptools-specific. Do not copy them into a Hatchling project expecting them to take effect.

### 7.3 Hatchling and other backends

Hatchling has its own build-target configuration and include/exclude rules. The `tinytools` example uses:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/tinytools"]

[tool.hatch.build.targets.sdist]
include = ["/pyproject.toml", "/README.md", "/LICENSE", "/src/tinytools"]
```

That configuration is a compact illustration of explicit package selection. For real projects, confirm the backend's default exclusions and pattern semantics. `flit-core`, `pdm-backend`, `setuptools`, `maturin`, and `scikit-build-core` each have distinct project-layout and inclusion conventions.

### 7.4 `py.typed` and runtime data

PEP 561's `py.typed` marker tells type checkers that inline typing information is provided. It must ship with the package if consumers need that signal. Likewise, templates, SQL files, JSON schemas, model configuration, and other runtime resources must be included intentionally.

Prefer `importlib.resources` for reading package resources rather than relying on a current-working-directory path. A source-tree test can accidentally pass because the file is present locally. An installed-wheel smoke test is what catches a missing package resource.

## 8. Core metadata that affects installation

The following metadata is often visible in a wheel's `METADATA` file:

- **`Requires-Python`:** the supported Python version range. Installers can use it to reject incompatible releases.
- **`Requires-Dist`:** runtime dependency requirements, possibly with environment markers and extras conditions.
- **`Provides-Extra`:** declares an extra such as `test` or `postgres`; corresponding conditional `Requires-Dist` entries define what it installs.
- **Classifiers:** descriptive standardized labels, including Python versions, operating systems, and development status. They help users and indexes but do not override `Requires-Python` or validate code compatibility.
- **Dynamic metadata:** source configuration can declare metadata fields as dynamic when the backend supplies them at build time, subject to the relevant metadata rules. A consumer sees the resolved metadata in the artifact, not the author's intention.

A metadata example:

```text
Requires-Python: >=3.12
Requires-Dist: httpx>=0.27
Provides-Extra: test
Requires-Dist: pytest>=8; extra == "test"
Classifier: Programming Language :: Python :: 3
```

This is illustrative, not a promise that `tinytools` has those dependencies. Core metadata fields and the permitted dynamic fields are standardized separately from each backend's configuration. A project must not mark a field dynamic and also provide a static value where the applicable specification forbids it.

### PEP 639 license metadata

PEP 639 standardizes SPDX license expressions and license-file inclusion. In modern Core Metadata, this can appear as `License-Expression` and one or more `License-File` fields. License files need to be included in the distribution at the specified paths. Older metadata may use legacy `License` fields or license classifiers; do not assume an older package's metadata follows the new representation. For current projects, use the syntax supported by the selected backend and validate the produced artifacts.

### PEP 658: metadata available from an index

PEP 658 defines how a package index using the Simple Repository API can expose a distribution's Core Metadata separately (commonly via a `.metadata` URL associated with the distribution link). A resolver can inspect metadata without downloading the complete wheel first, improving dependency-resolution efficiency when the index and installer support it. This is an index protocol capability—not a new file that every wheel must contain, and not a guarantee that every index serves separate metadata.

## 9. Native wheels: build, repair, and validate

Pure Python packaging is mostly file selection and metadata. Native extensions add compilers, linkers, headers, ABI compatibility, system libraries, and platform-specific artifacts. Examples include NumPy-like numerical packages, Rust extensions, and C/C++ bindings.

### 9.1 `cibuildwheel`

[`cibuildwheel`](https://cibuildwheel.pypa.io/) automates building and testing wheels across supported Python versions and operating systems. It is commonly integrated with CI runners and containerized Linux build environments. It is not a compiler or a universal cross-compilation solution: the project still needs valid build configuration, native dependencies, and appropriate CI infrastructure.

A minimal configuration sketch for a project whose backend can build native extensions might look like:

```toml
[tool.cibuildwheel]
# Example only: narrow this to the versions/platforms the project supports.
build = "cp312-* cp313-*"
test-command = "python -c \"import tinytools\""
```

This is illustrative configuration; actual build selectors and supported interpreter variants depend on the installed `cibuildwheel` version. Do not copy it blindly for a pure-Python package or a project that does not yet support CPython 3.13. In production, test meaningful functionality and resources, not only that an import succeeds.

### 9.2 Linux and `manylinux`

Linux distributions differ in libc versions and system-library availability. The modern `manylinux_{major}_{minor}_{arch}` tag expresses a glibc baseline as part of a defined policy. A wheel built against a newer glibc than its claimed baseline may fail on older systems even if it is tagged optimistically.

To distribute broadly, build in a compatible manylinux environment (commonly via the images and workflows used by `cibuildwheel`) and check/repair the wheel. Do not build on a recent host and simply rename the wheel to a lower `manylinux` tag. A tag is a compatibility claim that must be backed by the build environment and policy checks.

### 9.3 `musllinux` and Alpine

Alpine Linux commonly uses musl libc rather than glibc. `manylinux` and `musllinux` target different libc families and are not interchangeable. If supporting Alpine is important, build and test a musllinux wheel or provide another supported installation path. A generic `linux_x86_64` wheel does not automatically offer broad Linux compatibility.

### 9.4 Repair tools

| Tool | Main use | Important limitation |
|---|---|---|
| `auditwheel` | Inspect Linux wheels and repair eligible wheels by bundling external shared libraries and applying appropriate manylinux policy/tagging | Cannot make arbitrary incompatible binaries portable; licensing and system-library policy still matter |
| `delocate` | Inspect/repair macOS wheels, copying eligible non-system shared libraries and updating references | Must be built/tested for supported macOS deployment targets and architectures |
| `delvewheel` | Repair Windows wheels by bundling eligible DLL dependencies and adjusting references | Does not eliminate all Windows runtime prerequisites or validate the whole application |

Repairing a wheel can increase its size and may require careful license review for bundled libraries. Re-inspect and test the repaired wheel; do not assume the repair command's exit code is the only quality gate.

### 9.5 ARM64 distribution strategies

ARM64 (AArch64) is a distinct architecture from x86-64. Publish the appropriate platform-tagged wheel for Linux ARM64, macOS ARM64, or Windows ARM64 as applicable; do not use one platform tag to stand in for all of them. Options include native ARM64 CI runners, supported cross-compilation, and platform-specific build environments. Native runners are often easier to reason about, while cross-compilation can be faster or necessary in constrained infrastructure but adds toolchain and test complexity.

A successful cross-build is not proof of runtime compatibility. Run tests on the target architecture or a credible target environment. Be alert to optional CPU instruction sets, architecture-specific dependencies, and external shared libraries.

### 9.6 Stable ABI (`abi3`) and the limited API

CPython's Stable ABI and Limited API allow some extension modules to target a stable subset of CPython's C API. A correctly configured extension may then support multiple CPython versions with fewer wheel variants, often using an `abi3` ABI tag.

Trade-offs:

- The extension must restrict itself to the supported API and build correctly for the intended minimum Python version.
- Not every C API or extension pattern is available through the limited API.
- Dependencies may have their own ABI constraints, so `abi3` does not automatically make the entire package portable.
- Testing across the declared Python versions remains necessary.
- Free-threaded CPython builds have distinct ABI considerations; do not assume a conventional `cp313`/`abi3` extension is compatible with free-threaded builds. Newer CPython versions may define a separate free-threaded stable ABI (for example, `abi3t` in CPython 3.15); use the current CPython and packaging documentation and verify the actual tags emitted by the toolchain rather than extrapolating across versions.

Use `abi3` only when the extension and its dependency stack support it and the reduced wheel matrix is worth the constraints.

## 10. Wheel size, license compliance, and metadata efficiency

### 10.1 Optimize size without breaking users

Large wheels increase download time, storage, cache cost, and mirror overhead. Review wheel contents before trying to optimize them.

Practical steps:

1. Exclude tests, benchmarks, build outputs, caches, and documentation sources when they are not runtime resources.
2. Include only required data; do not remove files that runtime behavior depends on.
3. Avoid bundling duplicate shared libraries across package components where safe and feasible.
4. Strip native debug symbols only when doing so fits debugging, crash-reporting, and licensing needs.
5. Inspect compressed and uncompressed sizes and test all supported installation paths after changes.

Do not apply aggressive exclusions to `data/`, `py.typed`, templates, SQL, or schemas without tests that prove they are unnecessary. Package size reduction is a correctness change if it alters runtime contents.

### 10.2 PyPI file-size limits

PyPI enforces per-file upload limits, and the limit may change over time or differ through approved exceptions. Do not hard-code a limit into a long-lived policy document. Before release, check the current [PyPI help/documentation](https://pypi.org/help/) and project upload response. If a legitimate artifact exceeds the current default, follow PyPI's current process for requesting an increase rather than splitting or renaming the artifact in an unsupported way.

### 10.3 PEP 639 license files

A distribution should carry the relevant license text and notices, not merely metadata claiming a license. PEP 639 defines SPDX license expressions and standardized license-file handling. Validate both the expression and the actual files in the sdist and wheel. Bundling native libraries also introduces third-party license obligations; consult their licenses and include notices where required.

### 10.4 PEP 658 and dependency resolution

When supported by an index, separate metadata lets a resolver inspect dependencies and `Requires-Python` without downloading full artifacts that it may later reject. This can reduce network transfer during resolution. It does not alter wheel compatibility rules and does not replace integrity checks on the final distribution.

## 11. Direct references and installation sources

Python installers can install from multiple sources:

- **Package index:** `python -m pip install tinytools` resolves a named project through configured indexes.
- **Local path:** `python -m pip install .` builds/installs the project at the current path; `python -m pip install dist/tinytools-0.1.0-py3-none-any.whl` installs a specific local wheel.
- **URL:** `python -m pip install https://example.invalid/packages/tinytools-0.1.0-py3-none-any.whl` illustrates a direct artifact URL. The URL must actually be reachable and trustworthy; `.invalid` is reserved and will not work.
- **VCS:** `python -m pip install "tinytools @ git+https://example.org/team/tinytools.git@v0.1.0"` illustrates a VCS direct reference pinned to a tag. Use a commit hash for stronger immutability where supported and ensure credentials are handled securely.
- **Editable local install:** `python -m pip install -e .` is a development workflow, not a substitute for testing a built wheel.

Direct references in a requirements file can be useful for controlled deployments, but published package metadata has stricter rules. The dependency-specifier/Core Metadata specifications prohibit or restrict direct URL references in uploaded distribution metadata; in particular, PyPI does not accept uploaded metadata whose `Requires-Dist` dependencies use direct URL references. Do not put a private VCS URL or arbitrary artifact URL in a library's published runtime dependencies as a way to bypass normal dependency publication. Consult the current dependency specifier and Core Metadata specs for the exact restrictions and use a package index or documented deployment-specific requirements where appropriate.

Security considerations: install only from trusted sources, pin revisions when reproducibility matters, protect credentials, and understand that installing a VCS project usually involves building it from source and therefore executing build-time code.

## 12. Troubleshooting: systematic diagnosis

Start with evidence: exact command, full error, Python version, OS/architecture/libc, installer version, configured indexes, selected artifact URL/name, and whether the failure occurs during resolution, build, installation, import, or runtime use.

### 12.1 `No matching distribution found`

This usually means the resolver could not find a candidate satisfying the requirement and the target environment. Possible causes include:

1. The package/version is not available on the configured index.
2. `Requires-Python` excludes the active Python version.
3. No wheel tag matches the interpreter/ABI/platform, and no usable sdist is available or permitted.
4. `--only-binary` excludes the available sdist.
5. An index configuration or network/authentication issue hides the release.
6. The package's version constraint conflicts with other requirements.

Diagnosis:

```bash
python --version
python -m pip --version
python -m pip debug --verbose
python -m pip index versions some-package
```

`pip index versions` is an inspection aid and may be affected by index configuration and network access. Check the configured index and package page, read `Requires-Python`, inspect the candidate wheel tags, and compare against the environment's supported tags. For `uv`, use its verbose output and current help/docs to inspect resolver and platform settings.

Fix the root cause: select a supported Python version, allow an sdist if appropriate, build/publish a compatible wheel, correct metadata, update an installer only when needed, or resolve index/network configuration. Do not solve it by renaming an incompatible wheel.

### 12.2 `Failed building wheel`

This message is often a summary, not the root cause. Read earlier log lines. Common causes:

- missing compiler, linker, or SDK;
- missing Python development headers or system-library headers;
- build backend or build dependency incompatibility;
- missing source files in the sdist;
- unsupported Python version or ABI;
- incorrect environment variables or toolchain configuration;
- dependency constraints that cannot be satisfied in the build environment.

Diagnosis workflow:

1. Re-run with verbose output (`python -m pip -v ...` or the relevant frontend's verbose option).
2. Identify whether failure occurs while installing build dependencies, calling a backend hook, compiling, linking, or packaging files.
3. Try building the sdist's wheel in a clean environment, not only from the Git checkout.
4. Confirm compiler and system dependencies from the project's build documentation.
5. Check whether a compatible wheel exists; if the project is third-party, report the missing wheel/unsupported environment to maintainers rather than guessing at compiler flags.

Avoid immediately using `--no-build-isolation` as a fix. It can hide missing build requirements by accidentally using packages installed in your environment, making the build non-reproducible. Use it only when you intentionally manage the build environment and install the exact declared build requirements yourself.

### 12.3 Missing `py.typed` or data files

Symptoms include a type checker treating the package as untyped or runtime code raising `FileNotFoundError` only after installation.

1. List wheel and sdist contents.
2. Check backend-specific inclusion configuration.
3. Rebuild both artifacts.
4. Install the wheel in a clean virtual environment outside the source directory.
5. Run a smoke test that reads the resource and, where relevant, run a type-checking fixture.

Do not infer correct packaging from an editable installation; editable installs can expose files directly from the checkout that were never included in the wheel.

### 12.4 Native wheel fails on Linux

Check the architecture and tag first, then inspect linked shared libraries and glibc baseline. A `manylinux_2_28` wheel is not generally compatible with a glibc 2.17 system. A manylinux wheel is not automatically appropriate for musl/Alpine. Use `auditwheel show` where available, build against the intended policy, repair eligible dependencies, and test in representative containers/hosts.

## 13. Hands-on artifact validation lab

This lab turns the `tinytools` example into a release-quality artifact check. It deliberately validates the wheel and sdist separately.

### Step 1 — Build from a clean checkout

Ensure generated files are not accidentally committed or relied on. From the project root:

```bash
rm -rf dist build *.egg-info
uv build
```

`rm -rf` is a destructive shell command: run it only from the intended project directory after checking the paths. On Windows, remove the `dist`, `build`, and `*.egg-info` outputs using PowerShell or delete only those known generated directories. The `*.egg-info` pattern may match nothing; that is fine.

Record the actual artifact filenames and sizes. For the example's static metadata, expect one `.tar.gz` and one `.whl`.

### Step 2 — Inspect wheel and sdist

```bash
python -m zipfile -l dist/tinytools-0.1.0-py3-none-any.whl
python -m tarfile -l dist/tinytools-0.1.0.tar.gz
```

If the actual wheel name differs, substitute the exact path printed by your shell. Confirm the resource and typing marker appear in the wheel. Confirm the sdist includes the source files and metadata needed to rebuild it.

### Step 3 — Build a wheel from the sdist

Use a temporary directory and a clean environment so the build does not accidentally use files from the checkout:

```bash
python -m venv .venv-sdist-check
# Linux/macOS:
. .venv-sdist-check/bin/activate
python -m pip install --upgrade pip build
python -m build --wheel --outdir wheel-from-sdist dist/tinytools-0.1.0.tar.gz
```

On Windows PowerShell, activate with `.\.venv-sdist-check\Scripts\Activate.ps1`. This command asks the `build` frontend to unpack the sdist and build a wheel from that archive, rather than from the working checkout. The `build` frontend and the backend requirements must be available according to the sdist's `pyproject.toml`; build isolation is enabled by default. A successful build proves the sdist contains the inputs needed to complete the build, but it does not prove every runtime resource made it into the wheel—inspect and smoke-test the rebuilt wheel too. If the build fails because a required build input was omitted, fix sdist inclusion and rebuild the original artifacts.

### Step 4 — Install the wheel in a clean environment

Create a separate environment outside the source tree:

```bash
python -m venv .venv-wheel-check
# Linux/macOS:
. .venv-wheel-check/bin/activate
python -m pip install --upgrade pip
python -m pip install --no-deps dist/tinytools-0.1.0-py3-none-any.whl
python -c "import tinytools; print(tinytools.normalize_name('  Hello   WORLD  '))"
python -c "from tinytools.core import load_defaults; print(load_defaults())"
```

Expected observations: the first command prints `hello world`; the second prints the JSON object from `defaults.json`. These are expected results derived from the example code, not a claim that the commands were executed here. If the installed wheel lacks the JSON resource, the second command fails—exactly the defect this test is designed to catch.

`--no-deps` is suitable here because `tinytools` declares no runtime dependencies. Do not use it in a general production installation unless dependencies are installed by another controlled mechanism.

### Step 5 — Check metadata and wheel structure

```bash
python -m pip install check-wheel-contents twine
check-wheel-contents dist/tinytools-0.1.0-py3-none-any.whl
python -m twine check dist/*
```

These tools validate different properties: `check-wheel-contents` checks wheel layout/content issues, while `twine check` checks distribution metadata/README rendering issues. Neither replaces an installed-wheel test. Exact command entry points can vary by tool release; consult `--help` if necessary.

For metadata schema validation, a tool such as `validate-pyproject` can validate project configuration against the applicable schema. It does not prove that the produced wheel contains all required files or imports correctly.

### Step 6 — Test the sdist's installability

In another clean environment or a clean container, install the sdist directly:

```bash
python -m pip install dist/tinytools-0.1.0.tar.gz
```

This exercises the frontend/backend build path. Installation success alone does not prove that every expected runtime resource is present, so also inspect the installed files and run resource-specific smoke tests. Build a wheel explicitly from the sdist as in Step 3 to separate sdist completeness from wheel file-selection behavior. For production, run this lab across supported operating systems and Python versions, including any native platform matrix.

### Step 7 — CI release gate

A sensible packaging CI job should:

- run unit tests and type checks;
- build sdist and wheel from a clean checkout;
- inspect archive contents for required resources and license files;
- build a wheel from the sdist;
- validate metadata and wheel layout;
- install the wheel in a fresh environment and run smoke/integration tests;
- run the native wheel matrix and platform repair checks where applicable;
- retain artifact hashes and build logs for release review.

## 14. Exercises

Complete these in order. Keep notes of the observed artifacts and errors; do not assume an exercise passed until you have run it.

### Exercise A — Explain artifact differences

For `tinytools`, list five files expected in the wheel and identify which metadata directory contains the build metadata. Then explain why a sdist may include build inputs that are not installed as runtime files.

### Exercise B — Find a missing resource

Temporarily remove `data/defaults.json` from the Hatchling wheel selection (or use a throwaway branch with an exclusion rule), rebuild, and install the wheel into a fresh environment. Run `load_defaults()`.

- What exception occurs?
- Why might tests from the repository still pass?
- Which inclusion configuration fixes the problem?

Restore the correct configuration and verify the wheel again.

### Exercise C — Tag triage

For each filename, identify the likely supported interpreter, ABI, platform, and one important caveat:

1. `tinytools-0.1.0-py3-none-any.whl`
2. `numpy-2.1.0-cp313-cp313-manylinux_2_17_x86_64.whl`
3. `exampleext-1.0.0-cp312-abi3-win_amd64.whl`
4. `exampleext-1.0.0-cp313-cp313t-manylinux_2_28_aarch64.whl`
5. `exampleext-1.0.0-cp312-cp312-musllinux_1_2_x86_64.whl`

Treat these as tag-decoding examples; do not infer that a particular project actually publishes these files. For item 3, explain why `abi3` is not the same as `cp312` as an ABI tag. For item 4, explain why free-threaded compatibility needs explicit attention.

### Exercise D — Reproduce a missing-wheel error

In a controlled environment, use `--only-binary :all:` with a package/version/platform combination that has no compatible wheel. Record the exact error and explain whether the cause is index availability, `Requires-Python`, tags, or binary-only policy. Do not use a critical production dependency for this experiment.

### Exercise E — Native-build failure investigation

Choose a small native extension project or a disposable environment. Inspect the verbose log from a build failure (or use a documented example log from a project's issue tracker). Classify the failure as dependency resolution, missing compiler/header, linker/shared-library, unsupported ABI, or package file selection. Propose a fix tied to the evidence rather than disabling build isolation by default.

### Exercise F — CI matrix plan

Design a release matrix for a hypothetical package supporting CPython 3.12 and 3.13 on Linux x86-64, Linux ARM64, macOS ARM64, and Windows x86-64. Specify which runners/build environments you would use, which wheel tags you expect, where native libraries are repaired, and how you will test each artifact. Include free-threaded Python only if the project and dependencies support it.

## 15. Self-check questions with answers

### 1. How do you decode `numpy-2.1.0-cp313-cp313-manylinux_2_17_x86_64.whl`?

- `numpy`: distribution name.
- `2.1.0`: version.
- First `cp313`: CPython 3.13 interpreter tag.
- Second `cp313`: CPython 3.13 ABI tag.
- `manylinux_2_17_x86_64`: Linux x86-64 wheel targeting the manylinux policy associated with glibc 2.17 compatibility, subject to the policy's additional constraints.

It is not an `abi3` wheel. Compatibility also depends on the artifact's actual shared-library dependencies and the target system; filename decoding alone is not a runtime test.

### 2. Why can wheels improve installation security compared with sdists?

A compatible wheel generally installs by unpacking and recording files rather than running the package's build backend on the consumer's machine. An sdist commonly invokes build code and may compile native code, so the build step creates an additional execution surface. However, wheels are not automatically trustworthy: malicious code can be shipped in a wheel and run when imported or invoked, and native binaries can contain vulnerabilities. Trustworthy source, provenance, integrity verification, dependency review, and artifact testing still matter.

### 3. How do you build a wheel, inspect its contents, and explain the files in `.dist-info`?

1. Build with `uv build` (or `python -m build`) from the project root.
2. List the wheel with `python -m zipfile -l dist/<actual-wheel-name>.whl` or `unzip -l`.
3. Read `.dist-info/METADATA` for package metadata and runtime dependencies; `WHEEL` for wheel format and tags; `RECORD` for the archive file inventory and hashes; `entry_points.txt` when entry points are declared; and `licenses/` when license files are recorded under modern metadata rules.
4. Confirm required package files such as `py.typed` and data resources are present.
5. Install the built wheel into a clean virtual environment outside the checkout and run smoke tests. Also inspect the sdist and verify that a wheel can be rebuilt from it.

## 16. Final competency checklist

- [ ] I can explain the distinct roles of an sdist and a wheel.
- [ ] I can decode distribution name, version, Python tag, ABI tag, and platform tag without conflating them.
- [ ] I can explain `py3-none-any`, `cp312`, `abi3`, `cp313t`, `manylinux`, and `musllinux` at a useful level.
- [ ] I can inspect `.whl` and `.tar.gz` contents using portable tools.
- [ ] I can interpret `METADATA`, `WHEEL`, `RECORD`, and conditional `entry_points.txt`.
- [ ] I know that metadata tags are compatibility claims, not proof of runtime success.
- [ ] I can configure and test package data and `py.typed` inclusion for the selected backend.
- [ ] I can explain the difference between setuptools `MANIFEST.in` and backend-specific wheel inclusion settings.
- [ ] I can explain why `--only-binary :all:` can fail when a compatible wheel is unavailable.
- [ ] I can diagnose missing-wheel and native-build failures from verbose evidence.
- [ ] I understand the role and limits of `cibuildwheel`, `auditwheel`, `delocate`, and `delvewheel`.
- [ ] I can explain glibc baseline and musl compatibility considerations.
- [ ] I understand the benefits and restrictions of `abi3` and the special case of free-threaded Python.
- [ ] I verify current PyPI file-size rules rather than relying on a remembered limit.
- [ ] I can validate both artifacts, build from the sdist, and install/test the built wheel in a clean environment.

## 17. Authoritative references

Use specifications for normative requirements and tool documentation for implementation-specific behavior. Tool defaults and accepted target values change; check the current version when applying these instructions to a release pipeline.

- [Python Packaging User Guide — Package Formats](https://packaging.python.org/en/latest/discussions/package-formats/) — high-level explanation of sdists and wheels.
- [PyPA Binary Distribution Format (wheel specification)](https://packaging.python.org/en/latest/specifications/binary-distribution-format/) — wheel filename and archive layout, `.dist-info`, and installation model.
- [PyPA Source Distribution Format](https://packaging.python.org/en/latest/specifications/source-distribution-format/) — standardized sdist structure.
- [PyPA Platform Compatibility Tags](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/) — interpreter, ABI, and platform tags; Linux compatibility policy.
- [Writing `pyproject.toml` — license metadata and backend support](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) — current PEP 639 syntax and minimum backend versions.
- [CPython documentation — Stable ABI for free-threaded builds](https://docs.python.org/3/howto/abi3t-migration.html) — version-specific guidance for `abi3t`; check availability for the interpreter versions you support.
- [PEP 425 — Compatibility Tags for Built Distributions](https://peps.python.org/pep-0425/) — background on wheel compatibility tags.
- [PEP 600 — Future `manylinux` Platform Tags](https://peps.python.org/pep-0600/) — manylinux policy model.
- [PEP 656 — `musllinux` Platform Tags](https://peps.python.org/pep-0656/) — musl-based Linux compatibility tags.
- [PEP 384 — Defining a Stable ABI](https://peps.python.org/pep-0384/) — CPython Stable ABI background.
- [PEP 639 — Improving License Clarity with Better Package Metadata](https://peps.python.org/pep-0639/) — SPDX expressions and license files.
- [PEP 658 — Serve Distribution Metadata in the Simple Repository API](https://peps.python.org/pep-0658/) — separate metadata availability at indexes.
- [Core Metadata Specification](https://packaging.python.org/en/latest/specifications/core-metadata/) — `Requires-Python`, `Requires-Dist`, classifiers, and other metadata fields.
- [`cibuildwheel` documentation](https://cibuildwheel.pypa.io/) — multi-platform wheel building and testing.
- [`auditwheel` project](https://github.com/pypa/auditwheel), [`delocate` project](https://github.com/matthew-brett/delocate), and [`delvewheel` project](https://github.com/adang1345/delvewheel) — platform-specific wheel inspection/repair.
- [`uv` documentation](https://docs.astral.sh/uv/) and [`pip` documentation](https://pip.pypa.io/en/stable/) — current frontend and installer options.
- [PyPI Help](https://pypi.org/help/) — current upload policies and file-size limits.

---

**Release principle:** build artifacts from a clean source state, inspect what is actually inside them, and test the built wheel in the environments you claim to support. A successful build is only the start of artifact validation.
