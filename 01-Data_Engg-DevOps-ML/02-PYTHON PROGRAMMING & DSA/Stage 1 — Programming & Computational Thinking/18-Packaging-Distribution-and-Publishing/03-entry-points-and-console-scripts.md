# Entry Points and Console Scripts

> **Stage 1 — Programming & Computational Thinking · Module 18 — Packaging, Distribution and Publishing**  
> Baseline: Python 3.12+, a modern installer (`pip` or `uv`), and a PEP 517 build backend. Commands and tool options can evolve; check the documentation for the versions used by your team.

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Explain what an installed Python entry point is and how it differs from `if __name__ == "__main__"`.
- Declare console and GUI scripts in `pyproject.toml` and implement a predictable `main()` function.
- Explain how installers create launchers in virtual environments and how those launchers select an interpreter.
- Install a CLI in an isolated environment with `pipx` or `uv tool`, and run it with `uvx` or `uv run` where appropriate.
- Read the installed distribution version with `importlib.metadata`, manage exit codes, and access package resources portably.
- Test the built wheel and generated command in a clean environment rather than relying only on source-tree execution.
- Design CLI startup, compatibility, security, and distribution practices suitable for a team or public package.

### Prerequisites

Review Stage 1 Module 6: imports and `__main__`, project/package layout, `pyproject.toml`, dependency management, virtual environments, documentation, and semantic versioning. Module 1.5's command-line arguments, streams, and exit codes are useful prerequisites. Module 1.7 covers test design; Module 1.10 covers production habits and release basics; Module 1.16 covers testing installed artifacts. The previous Module 18 lessons cover build backends and wheel/sdist artifacts.

## 2. Mental model: from Python function to shell command

A Python function is not automatically a command available on a user's `PATH`. A package declares an **entry point** in distribution metadata. During installation, an installer reads that metadata and creates a platform-appropriate launcher for each console script.

```text
pyproject.toml
  [project.scripts]
  tinytools = "tinytools.cli:main"
          |
          v
build backend records entry-point metadata in the wheel
          |
          v
installer installs wheel and creates a launcher
  Unix-like:  <venv>/bin/tinytools
  Windows:    <venv>\Scripts\tinytools.exe (typically)
          |
          v
launcher imports tinytools.cli, calls main(), maps result to exit status
```

The names have distinct meanings:

- **Distribution name:** `tinytools`, used by installers and package metadata.
- **Import package:** `tinytools`, the Python package users import.
- **Command name:** `tinytools`, the executable users type. It can differ from both the distribution and import name.
- **Entry-point target:** `tinytools.cli:main`, identifying a callable in an importable module.

This separation lets users run a command without knowing where its source file lives or manually invoking `python path/to/script.py`.

## 3. Beginner concepts

### 3.1 What is an entry point?

An entry point is standardized metadata that names an object provided by an installed distribution. Python packaging uses entry points for several purposes, including console scripts and plugin discovery. This lesson focuses on command-line launchers; the next lesson covers plugin entry-point groups.

Entry points are valuable because they:

- expose a stable command independent of the repository's working directory;
- let an installer create the right launcher for the current environment and operating system;
- connect packaging metadata to Python code without requiring users to locate source files;
- make a CLI installable through ordinary package tools.

Entry-point metadata is declarative. The installer does not need to run your CLI just to generate the launcher, though installation and later command execution have their own trust and execution considerations.

### 3.2 `[project.scripts]`

PEP 621 standardizes project metadata in `pyproject.toml`. The `[project.scripts]` table maps command names to import targets.

```toml
[project.scripts]
tinytools = "tinytools.cli:main"
```

Interpret the target as:

- `tinytools.cli`: import this module;
- `main`: retrieve the callable named `main` from that module;
- `tinytools`: install a command with this name.

The command name should be a sensible executable name. Avoid names likely to collide with common system commands or commands owned by another package. If the project provides multiple commands, each command name maps to its own target.

#### What should `main()` accept and return?

The generated console-script wrapper calls the target with **no required positional arguments**. A well-designed CLI can accept an optional `argv` parameter for testability, but the installed launcher invokes it without passing command-line arguments directly; the function normally reads arguments through `argparse` or another CLI framework.

The return value is interpreted like `sys.exit()`:

- `None` means successful completion (status 0);
- an integer becomes the process exit status (conventionally 0 means success, nonzero means failure);
- returning a string or another non-integer is not a way to print a message: `sys.exit()` treats a non-`None` non-integer argument as an error message, writes it to stderr, and exits with status 1.

For predictable CLIs, return an integer status code and print user-facing output explicitly. Do not call `sys.exit()` deep inside ordinary business logic; return a result or raise a well-defined exception and let the CLI boundary decide the process status.

### 3.3 A minimal, complete `tinytools` project

Use this layout throughout the lesson:

```text
tinytools-project/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── tinytools/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       └── data.json
└── tests/
    └── test_cli.py
```

The `src/` layout helps ensure tests do not accidentally import the package merely because the repository root is on `sys.path`. It encourages testing what is installed. See the preceding lessons for the broader layout and build-backend discussion.

#### `pyproject.toml`

```toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "tinytools"
version = "0.1.0"
description = "A small example command-line utility"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
license-files = ["LICENSE"]
authors = [{ name = "Example Maintainer" }]
classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.12",
  "Environment :: Console",
]
dependencies = []

[project.scripts]
tinytools = "tinytools.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/tinytools"]

[tool.hatch.build.targets.wheel.force-include]
"src/tinytools/data.json" = "tinytools/data.json"
```

The `build-system` table selects Hatchling as the backend. The minimum version is `1.27` because this example uses PEP 639’s SPDX `license` string and `license-files` array; older Hatchling releases may expect the deprecated table form instead. `[project]` contains distribution metadata, and `[project.scripts]` declares the executable mapping. `license = "MIT"` is an SPDX expression, not a substitute for including the license text. `license-files = ["LICENSE"]` declares the file to include in the distributions. The Hatchling target configuration selects the import package and explicitly includes the example resource; consult the installed Hatchling documentation for its current file-selection rules.

#### `README.md`

```markdown
# tinytools

A small example command-line utility for learning Python packaging.

Install the package, then run `tinytools --help` or `tinytools --version`.
```

#### `LICENSE`

For this teaching example, use the standard MIT license text and replace the copyright holder and year with the project’s actual details. Do not copy this license declaration into a real project unless MIT is the license the project has chosen.

```text
MIT License

Copyright (c) 2026 Example Maintainer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

#### `src/tinytools/__init__.py`

```python
"""Small command-line utility used in packaging lessons."""
```

#### `src/tinytools/data.json`

```json
{
  "greeting": "hello from packaged data"
}
```

#### `src/tinytools/cli.py`

```python
from __future__ import annotations

import argparse
import json
from importlib.metadata import PackageNotFoundError, version
from importlib.resources import files


def installed_version() -> str:
    """Return the installed distribution version, with a source-tree fallback."""
    try:
        return version("tinytools")
    except PackageNotFoundError:
        # Useful when running directly from an uninstalled checkout.
        # A release smoke test should not silently accept this fallback.
        return "0+unknown"


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit status."""
    parser = argparse.ArgumentParser(prog="tinytools")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {installed_version()}",
    )
    parser.add_argument(
        "--show-data",
        action="store_true",
        help="print the bundled example data",
    )
    args = parser.parse_args(argv)

    if args.show_data:
        resource = files("tinytools").joinpath("data.json")
        data = json.loads(resource.read_text(encoding="utf-8"))
        print(data["greeting"])
    else:
        print("hello from tinytools")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Important details:

- `argv` is optional. `main()` called by the generated launcher receives no arguments, so `argparse` reads `sys.argv` by default. Tests can call `main(["--show-data"])` without modifying global process arguments.
- `argparse` handles `--help` automatically and exits with status 0. Invalid arguments normally produce a nonzero status (usually 2).
- `action="version"` prints the version and exits successfully. The value comes from installed distribution metadata instead of duplicating `0.1.0` in the implementation.
- `importlib.resources.files("tinytools")` locates a resource associated with the package, independent of the caller's working directory. Resource access is not the same as opening `Path.cwd() / "data.json"`.
- The `PackageNotFoundError` fallback is for source-tree convenience. In an installed-wheel test, assert the version is the expected release version so a missing installation cannot pass unnoticed.
- The `if __name__ == "__main__"` block supports direct module execution; it does **not** declare an installed shell command. The `[project.scripts]` table does that.

#### `src/tinytools/__main__.py`

```python
from .cli import main

raise SystemExit(main())
```

This makes `python -m tinytools` work. When Python executes a package with `-m`, it runs the package's `__main__.py`. The module should remain a thin dispatch layer. Keep the canonical CLI implementation in `cli.py` so the installed command and module invocation share behavior.

### 3.4 `[project.gui-scripts]`

```toml
[project.gui-scripts]
tinytools-gui = "tinytools.gui:main"
```

A GUI script is similar to a console script, but on platforms that distinguish console and GUI processes—especially Windows—the launcher is created without attaching a console. This matters for GUI applications that should not open a terminal window. It is not a universal GUI framework and does not change how your application builds its interface. Do not declare a GUI script for an ordinary terminal CLI.

## 4. Intermediate: installation and runtime behavior

### 4.1 How launchers are generated

When a wheel is installed, the installer reads its entry-point metadata (commonly stored as `entry_points.txt` in the distribution's `.dist-info` directory). It creates a platform-appropriate executable or wrapper for each `console_scripts` entry.

Typical locations:

- Unix-like virtual environment: `.venv/bin/tinytools`;
- Windows virtual environment: `.venv\Scripts\tinytools.exe` and associated launcher support, depending on installer implementation.

The exact generated files are implementation-specific. Treat the command name and behavior as the public interface, not the launcher's byte-for-byte contents.

On Unix-like systems, a script wrapper commonly has a shebang pointing to the environment's Python interpreter. Windows uses executable launchers rather than relying on a Unix shebang. The key property is that the installed command should run using the interpreter/environment where it was installed, not an arbitrary global Python. Activating a virtual environment adjusts `PATH` so its `bin/` or `Scripts/` directory is searched first.

Diagnose command selection with:

```bash
# Unix-like
command -v tinytools
python -c "import sys; print(sys.executable)"

# Windows PowerShell
Get-Command tinytools
python -c "import sys; print(sys.executable)"
```

A command-not-found error commonly indicates the environment is not activated, the scripts directory is not on `PATH`, or the package was installed into a different environment.

### 4.2 `pipx`, `uv tool`, `uvx`, and `uv run`

These tools serve related but distinct workflows:

| Command/tool | Typical use | Environment behavior | Important caveat |
|---|---|---|---|
| `pipx install PACKAGE` | Install a user-facing CLI as a tool. | Creates a dedicated virtual environment per application and exposes its commands. | The pipx binary directory must be on `PATH`; `pipx ensurepath` can help configure it. |
| `uv tool install PACKAGE` | Install a CLI tool managed by uv. | Uses an isolated tool environment and exposes its executables through uv's tool bin directory. | Ensure the tool bin directory is on `PATH`; behavior/options depend on uv version. |
| `uvx PACKAGE` | Run a tool without a persistent manual installation workflow. | uv provisions an isolated environment as needed and runs the command. | It is an alias for `uv tool run`; pin a version when repeatability matters. |
| `uv run ...` | Run a command in the current uv project environment. | Resolves/synchronizes the project's environment according to the project configuration. | It is not the same as installing a globally exposed standalone CLI. |

Examples (replace `tinytools` with a published package name for remote installation):

```bash
pipx install tinytools
pipx run tinytools --help

uv tool install tinytools
uvx tinytools --help

# From the tinytools project directory:
uv run tinytools --help
```

For local development, install the current checkout into a disposable environment or use the project's configured environment. Do not confuse a command found in a developer environment with a verified release artifact.

### 4.3 Installed version without duplicated version strings

The distribution version is available through `importlib.metadata.version("tinytools")`. This reads installed metadata; it does not import `tinytools.__init__` to discover a variable.

```python
from importlib.metadata import PackageNotFoundError, version

try:
    current_version = version("tinytools")
except PackageNotFoundError:
    current_version = "0+unknown"
```

Use this approach when the CLI is expected to be installed. The fallback can help contributors running from a checkout, but it can also mask a packaging mistake if used in release tests without an assertion. If a project needs a source-tree version before installation, use a deliberate versioning strategy rather than maintaining several manually edited version strings.

### 4.4 Exit status: `return` versus `SystemExit`

A `return 0` inside `main()` returns to its caller. It does not terminate the Python process by itself. The generated console-script wrapper effectively invokes the callable and passes its result to `sys.exit()`. For `python -m tinytools`, the explicit `raise SystemExit(main())` provides the same command-line boundary.

```python
def main(argv: list[str] | None = None) -> int:
    # Parse arguments and run the operation.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Prefer stable exit-code conventions and document them for automation. Do not rely on exact human-readable stderr text as a machine interface. Tests can check the returned status directly for unit-level behavior and use a subprocess to verify the real process exit code.

### 4.5 CLI framework choices

| Framework | Strengths | Trade-offs / good fit |
|---|---|---|
| `argparse` (standard library) | No third-party runtime dependency; robust parser; supports help and subcommands. | More manual work for complex validation, rich output, or shell completion. Good default for small and dependency-light tools. |
| Click | Composable commands, parameter types, prompts, testing utilities, broad ecosystem. | Adds a runtime dependency and a framework-specific programming model. Good for multi-command CLIs. |
| Typer | Type-hint-driven interface built on Click; concise command declarations. | Adds dependencies and some behavior is mediated by Click and annotations. Good when typed declarations improve readability. |
| Cyclopts | Modern annotation-oriented command interfaces and generated help. | Smaller ecosystem than `argparse`/Click in some environments; verify feature and compatibility needs. Good when its API fits the team. |

Choose based on command complexity, support policy, dependency budget, testing facilities, help/completion requirements, and team familiarity. A framework is not a substitute for a well-defined CLI contract.

### 4.6 Package resources safely

Do not assume the current working directory is the package directory. This is fragile:

```python
# Fragile: succeeds only when the working directory matches expectations.
from pathlib import Path
text = (Path("data.json")).read_text()
```

Use `importlib.resources` for data shipped as package resources:

```python
from importlib.resources import files

resource = files("tinytools").joinpath("data.json")
text = resource.read_text(encoding="utf-8")
```

This works with normal installed packages and is designed to support package resources that may not correspond to a persistent filesystem path. If an API requires an actual filesystem path, use `importlib.resources.as_file()` as a context manager and keep the path usage within its context. Ensure the build backend includes the resource in the wheel; correct code cannot load a file that was omitted from the artifact.

## 5. Test the installed artifact, not only the source tree

### 5.1 Unit tests for CLI behavior

`tests/test_cli.py`:

```python
from tinytools.cli import main


def test_default_command(capsys):
    assert main([]) == 0
    assert capsys.readouterr().out.strip() == "hello from tinytools"


def test_show_data(capsys):
    assert main(["--show-data"]) == 0
    assert capsys.readouterr().out.strip() == "hello from packaged data"
```

These tests validate callable behavior, but they are not enough to prove the wheel includes the resource or that the generated launcher works. They may also fail to import the package if the test environment has not installed it or configured the source tree appropriately.

### 5.2 Build the wheel

From the project root, using current versions of uv and Hatchling:

```bash
uv build
```

The command should create both an sdist and a wheel in `dist/` by default. The declared `hatchling>=1.27` floor is intentional: the example uses PEP 639 license metadata, which older Hatchling releases may not support. For this project, filenames should follow the package/version convention, such as `tinytools-0.1.0.tar.gz` and `tinytools-0.1.0-py3-none-any.whl`; the precise wheel tags depend on the artifact and backend. Do not treat these example names as proof that a build was executed.

Inspect the wheel archive with an available archive tool:

```bash
python -m zipfile -l dist/tinytools-0.1.0-py3-none-any.whl
```

Look for `tinytools/cli.py`, `tinytools/__main__.py`, `tinytools/data.json`, and a `tinytools-0.1.0.dist-info/` directory. Its metadata commonly includes `METADATA`, `WHEEL`, `RECORD`, and `entry_points.txt`. `entry_points.txt` may be absent if the distribution declares no entry points; in this example it should describe the console script. `RECORD` lists installed archive paths and hashes/sizes where applicable.

### 5.3 Install the wheel into a clean environment

Use a fresh environment that is not the project's development environment. On Unix-like systems:

```bash
python3.12 -m venv /tmp/tinytools-wheel-test
/tmp/tinytools-wheel-test/bin/python -m pip install --upgrade pip
/tmp/tinytools-wheel-test/bin/python -m pip install dist/tinytools-0.1.0-py3-none-any.whl
/tmp/tinytools-wheel-test/bin/tinytools --help
/tmp/tinytools-wheel-test/bin/tinytools --version
/tmp/tinytools-wheel-test/bin/tinytools --show-data
/tmp/tinytools-wheel-test/bin/python -m tinytools
```

On Windows PowerShell, create a venv and invoke its interpreter and scripts explicitly:

```powershell
py -3.12 -m venv .venv-wheel-test
.\.venv-wheel-test\Scripts\python.exe -m pip install --upgrade pip
.\.venv-wheel-test\Scripts\python.exe -m pip install .\dist\tinytools-0.1.0-py3-none-any.whl
.\.venv-wheel-test\Scripts\tinytools.exe --help
.\.venv-wheel-test\Scripts\tinytools.exe --version
.\.venv-wheel-test\Scripts\tinytools.exe --show-data
.\.venv-wheel-test\Scripts\python.exe -m tinytools
```

Expected behavior, not claimed execution output:

- `--help` prints usage and exits successfully;
- `--version` prints `tinytools 0.1.0` for the example wheel and exits successfully;
- `--show-data` prints `hello from packaged data`;
- `python -m tinytools` prints the default greeting.

To verify exit codes explicitly in a shell, run a command and inspect `$?` (POSIX shells) or `$LASTEXITCODE` (PowerShell). For invalid arguments, `argparse` normally exits nonzero. Do not run a command through a shell wrapper that masks the underlying status.

**Important:** this wheel is pure Python, so its example tag is generally `py3-none-any`. A real build can differ if project configuration or backend behavior changes. Always use the actual filename produced by the build instead of hard-coding an assumed tag in automation.

## 6. Advanced: performance, distribution, and compatibility

### 6.1 Keep `--help` fast with lazy imports

The console-script launcher imports the target module before calling `main()`. Any expensive imports at the top level of `cli.py` therefore happen even for `tinytools --help` or `tinytools --version`.

Avoid importing heavy optional libraries at module import time when only one command needs them:

```python
# Better for startup when this feature is rarely used.
def convert_file(path: str) -> int:
    import pandas as pd  # Import only when conversion is requested.

    # Conversion implementation goes here.
    return 0
```

Keep parser construction and lightweight metadata access cheap. Measure before optimizing:

```bash
python -X importtime -m tinytools --help
```

`-X importtime` reports import timing information to stderr; output can be noisy and varies by Python version and environment. Use it to identify expensive imports, not as a benchmark of total CLI latency. A production CLI may need a dedicated cold-start measurement on representative systems.

### 6.2 Zipapps, `shiv`, `pex`, PyInstaller, and Nuitka

These tools solve different deployment problems; none is a direct replacement for the standard entry-point mechanism in every situation.

| Tool/format | Model | When it can fit | Trade-offs |
|---|---|---|---|
| `zipapp` | Packages Python application code into a ZIP-based executable archive, commonly run with Python. | Small Python applications where a compatible interpreter is available. | Dependencies and native extensions need deliberate handling; not a universal self-contained binary. |
| `shiv` | Builds runnable Python zipapps with dependencies. | Deploying Python CLI applications in environments with Python installed. | Runtime still depends on Python and platform compatibility; caches and dependency layout need consideration. |
| `pex` | Builds executable Python environments/archives with dependency resolution and runtime support. | Reproducible application bundles and controlled deployments. | More packaging concepts and artifact-size/runtime trade-offs; native dependencies remain platform-sensitive. |
| PyInstaller | Bundles a Python application and much of its runtime/dependencies. | Distributing an application to users who should not need to install Python separately. | Builds are generally platform-specific; bundles can be large and require platform testing. |
| Nuitka | Compiles Python modules to C/C++-based binaries or extensions and can package applications. | Performance-sensitive or standalone deployment cases where compilation/package behavior is suitable. | Build toolchain and platform complexity; not automatically faster or smaller for every workload. |

Choose based on whether users have Python, native dependency needs, target OS/architecture, update mechanism, signing, startup time, artifact size, and operational support. A normal wheel remains a strong default for Python libraries and many team CLIs.

### 6.3 Windows, PATH, shebangs, and PEP 668

- **Windows launchers:** installers typically create `.exe` launchers for console scripts in a virtual environment's `Scripts` directory. Do not assume Unix shell wrapper details apply on Windows.
- **PATH:** if a command is installed but not found, inspect the active environment and the installer/tool's binary directory. `pipx ensurepath` helps configure the pipx path; restart the shell if required by the platform.
- **Shebang limits:** Unix-like systems and kernels impose practical limits on shebang handling and path lengths. Virtual environments in unusually long paths can expose launcher problems. Prefer manageable environment paths and let installers generate launchers instead of hand-writing them.
- **User versus system installs:** prefer project virtual environments or isolated tool environments. Avoid installing packages into an operating-system-managed Python with elevated privileges.
- **PEP 668:** distributions can mark their Python installation as externally managed. Installers may refuse global modifications and direct users toward virtual environments. Do not advise bypassing that protection as a routine fix; use a venv, `pipx`, or `uv tool` according to the task.

### 6.4 CLI security and privilege boundaries

A CLI executes with the permissions of the invoking user. Packaging a command does not sandbox it. Treat package names, dependencies, update sources, and command inputs as security-sensitive.

- Verify the distribution name and publisher before installing. Typosquatting can exploit one-character misspellings or misleading names.
- Do not recommend `sudo pip install` as a routine installation method. Use a virtual environment or isolated tool environment.
- Avoid `shell=True` for subprocess calls with untrusted or externally supplied input. Prefer argument lists and `subprocess.run([...], check=True, ...)` when practical.
- Validate paths and input values, handle errors without leaking secrets, and avoid logging tokens or credentials.
- For internal tools, use a trusted private index and explicit package/version policy; avoid ambiguous index configuration that can enable dependency confusion.
- Pin or constrain versions according to the deployment policy. For operational runbooks, document the exact tool version or package version when repeatability is important.

Example of safer subprocess invocation:

```python
import subprocess


def run_converter(input_path: str, output_path: str) -> None:
    subprocess.run(
        ["converter", "--input", input_path, "--output", output_path],
        check=True,
        text=True,
        capture_output=True,
    )
```

Argument lists avoid shell parsing, but they do not remove the need to validate arguments, manage timeouts, handle errors, or trust the executable being invoked.

### 6.5 Treat the CLI as a public API

Once users or scripts depend on a command, its interface is part of the package's compatibility contract. Version and review changes to:

- command names and aliases;
- flags, positional arguments, defaults, and environment variables;
- subcommand names and configuration-file formats;
- stdout/stderr behavior where automation relies on it;
- exit codes and error semantics;
- minimum supported Python and dependency versions.

Prefer adding new options compatibly. Deprecate old flags with clear warnings and a documented removal window. A breaking rename or changed exit-code meaning may require a major release under the project's versioning policy. Do not treat help text as the entire contract: scripts may parse output, so machine-readable output should be explicit and stable.

### 6.6 Multiple commands, aliases, subcommands, and module dispatch

Multiple entry points can share implementation functions:

```toml
[project.scripts]
tinytools = "tinytools.cli:main"
tinytools-check = "tinytools.commands.check:main"
tinytools-convert = "tinytools.commands.convert:main"
```

Each target must be importable and callable with no required arguments from the generated wrapper. Aliases can map two command names to the same function, but aliases increase the long-term compatibility burden. Use a single command with subcommands when commands form one coherent product and shared options/configuration are useful. Separate executables can be convenient when users need a focused command or different invocation name.

For subcommands, `argparse` supports subparsers; Click, Typer, and Cyclopts provide their own command-group patterns. Keep `__main__.py` as a thin module dispatch entry point. Avoid duplicating command logic in both `__main__.py` and installed script targets.

### 6.7 Internal CLI distribution

For a team CLI, distribute through a controlled private package index or an approved internal artifact store. Establish:

1. who may publish packages and how releases are reviewed;
2. a version-pinning or controlled-upgrade policy;
3. a rollback process and support window;
4. dependency/index configuration that avoids dependency confusion;
5. a way to verify the installed command's version (`tinytools --version`);
6. a self-update policy—automatic upgrades are not always appropriate for production runbooks.

Example installation from a private index depends on the organization's index configuration and authentication. Avoid placing credentials directly in command-line arguments or source control. For uv, a team may use `uv tool install --from <package-spec> <command-name>` when the package distribution name and exposed command name differ; consult the installed uv version's documentation for exact option syntax.

## 7. Common mistakes and systematic troubleshooting

### Mistake 1: only using `if __name__ == "__main__"`

**Symptom:** `python -m tinytools` works but `tinytools` is not found after installation.  
**Cause:** module execution is not an installed command declaration.  
**Fix:** declare `[project.scripts]`, rebuild the wheel, reinstall it, and check the environment's scripts directory.

### Mistake 2: data access depends on the working directory

**Symptom:** command works from the repository root but fails when run elsewhere.  
**Cause:** code opens `data.json` relative to `Path.cwd()`.  
**Fix:** use `importlib.resources.files("tinytools")` and confirm the file is included in the wheel.

### Mistake 3: `--help` is slow

**Symptom:** help takes seconds or initializes unrelated subsystems.  
**Cause:** expensive imports and side effects happen before argument parsing.  
**Fix:** move optional imports into command handlers, avoid network/database initialization at import time, and measure with `-X importtime`.

### Mistake 4: command points to the wrong target

**Symptom:** launcher fails with import or attribute errors.  
**Cause:** misspelled module path, missing function, package omitted from wheel, or stale installation.  
**Fix:** inspect `entry_points.txt`, install the freshly built wheel in a new venv, and test `python -c "from tinytools.cli import main; print(callable(main))"` using that venv's interpreter.

### Mistake 5: the wrong version appears

**Symptom:** `--version` prints `0+unknown` or an unexpected release.  
**Cause:** package isn't installed in the active interpreter, another distribution/version is selected, or the command belongs to a different environment.  
**Fix:** invoke the venv's Python explicitly; inspect `python -m pip show tinytools`, `python -c "import sys; print(sys.executable)"`, and `command -v tinytools` (or `Get-Command tinytools`).

### Mistake 6: tests pass but the installed command fails

**Symptom:** unit tests pass from the checkout but launcher/resource behavior breaks after installation.  
**Cause:** tests exercise source imports rather than the wheel, or files were excluded from the distribution.  
**Fix:** build the wheel, install it into a clean environment, invoke the generated command and `python -m tinytools`, and test from a directory outside the repository.

### Mistake 7: nonzero exit status is lost

**Symptom:** automation reports success despite a command failure.  
**Cause:** caller ignores the returned status, a wrapper doesn't propagate it, or a shell pipeline masks it.  
**Fix:** return an integer from `main()`, use `raise SystemExit(main())` for module execution, and test the actual subprocess exit code.

## 8. Hands-on exercises

Complete these in order. Do not move on until you can explain the result rather than merely copying commands.

### Exercise A — Add the installed command

1. Create the `tinytools-project` layout in Section 3.3.
2. Add `[project.scripts]` with `tinytools = "tinytools.cli:main"`.
3. Build a wheel and inspect its `entry_points.txt`.
4. Install the wheel in a fresh virtual environment and run `tinytools --help`.

**Success criteria:** the command is created by installation, help is shown, and the command works outside the repository directory.

### Exercise B — Diagnose a missing resource

1. Temporarily remove the Hatchling configuration that includes `data.json`, or change the resource path to a nonexistent filename.
2. Build a new wheel and list its contents.
3. Install that wheel in a fresh environment and run `tinytools --show-data`.
4. Identify whether the failure is a Python path bug or an artifact-inclusion bug; fix the correct layer.

**Success criteria:** `data.json` appears in the wheel and `--show-data` succeeds after installation.

### Exercise C — Verify exit codes

1. Add an argument that triggers a deliberate error and return a documented nonzero status.
2. Test `main([...])` directly.
3. Invoke the installed executable as a subprocess and assert its return code.
4. Confirm `--help` and `--version` exit successfully.

**Success criteria:** the tests distinguish function-level results from process-level exit behavior.

### Exercise D — Improve startup time

1. Add a deliberately expensive optional import to a command handler.
2. Compare `python -X importtime -m tinytools --help` before and after moving the import inside the handler.
3. Explain why the import is or is not required for help/version output.

**Success criteria:** you can identify import-time costs and avoid unrelated work before parsing arguments.

### Exercise E — Define a compatibility policy

Write a short policy that defines supported command names, flag deprecation windows, exit-code meanings, version reporting, and internal installation/update procedures. Include a test for each interface behavior that users or automation depend on.

## 9. Production-oriented packaging lab

The objective is to prove that the distribution, not merely the source checkout, exposes a usable CLI.

### Lab checklist

1. **Review metadata:** confirm project name, version, `requires-python`, runtime dependencies, and script mappings in `pyproject.toml`.
2. **Run tests:** execute unit tests in the development environment.
3. **Build artifacts:** run `uv build` and record the actual wheel filename.
4. **Inspect wheel:** verify modules, `__main__.py`, package resources, `.dist-info/METADATA`, `WHEEL`, `RECORD`, and `entry_points.txt` where applicable.
5. **Create a clean environment:** use a fresh venv and install the exact wheel path.
6. **Run command checks:** verify `--help`, `--version`, default behavior, resource access, and error cases.
7. **Verify module invocation:** run `python -m tinytools` with the venv's interpreter.
8. **Verify working-directory independence:** run the command while the current directory is outside the source checkout.
9. **Check exit codes:** assert the status of success and failure cases.
10. **Repeat across supported platforms:** at minimum test the operating systems and Python versions the project claims to support; do not infer Windows correctness from Linux-only tests.
11. **Record evidence:** capture the Python version, tool versions, wheel filename, test results, and any platform-specific limitations in the release record.

### Example subprocess smoke test

The following test assumes the `tinytools` wheel has already been installed into the environment running pytest. For release-grade isolation, run pytest from outside the repository or use a dedicated test project so the source tree cannot shadow the installed package.

```python
import subprocess
import sys


def test_installed_module_runs():
    result = subprocess.run(
        [sys.executable, "-m", "tinytools"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "hello from tinytools"
```

To test the generated `tinytools` executable itself, locate it in the active venv's scripts directory (`bin` on Unix-like systems, `Scripts` on Windows) and invoke that path with `subprocess.run`. This specifically tests launcher generation and target resolution, whereas `python -m tinytools` tests `__main__.py` dispatch.

## 10. Self-check questions with answers

### 1. What does `tinytools = "tinytools.cli:main"` generate at installation time?

The build backend records a `console_scripts` entry-point mapping in the distribution metadata. When an installer installs the wheel, it reads that metadata and generates a platform-appropriate launcher named `tinytools` in the environment's scripts directory. The launcher imports `tinytools.cli`, retrieves `main`, calls it without required arguments, and converts its result into process exit behavior. The exact launcher implementation differs by platform and installer.

### 2. How can a CLI report its installed version without hard-coding it twice?

Use `importlib.metadata.version("tinytools")`, which reads the installed distribution metadata. Catch `PackageNotFoundError` only if a source-tree fallback is useful, and make release tests assert the expected installed version so the fallback cannot conceal a failed installation. This keeps the package's declared distribution version as the version source of truth.

### 3. How do you package the CLI, install it with `pipx` or `uv tool`, and verify `--help` and exit codes?

Build with `uv build`, inspect the wheel, and install the wheel into a clean venv to validate the artifact directly. For a published distribution, use `pipx install tinytools` or `uv tool install tinytools`; ensure the relevant tool bin directory is on `PATH`. Run `tinytools --help` and `tinytools --version`, check successful exit statuses, invoke an invalid-argument or deliberate-error path, and verify its nonzero status. For a local unpublished wheel, use a clean venv and the exact wheel path rather than assuming a package index already contains it. Record the tool/Python versions and repeat on each supported platform.

## 11. Final competency checklist

- [ ] I can explain the difference between an entry point, `__main__.py`, and a Python script file.
- [ ] I can declare `[project.scripts]` and explain `module:function` resolution.
- [ ] I understand the purpose and platform caveat of `[project.gui-scripts]`.
- [ ] I can explain how launchers are generated and why the active environment and `PATH` matter.
- [ ] I can choose between `pipx`, `uv tool install`, `uvx`, and `uv run` for a specific workflow.
- [ ] I can read the installed version with `importlib.metadata` and avoid hiding packaging failures with a fallback.
- [ ] I can design `main()` with predictable arguments, output, and exit codes.
- [ ] I can access packaged resources with `importlib.resources` and ensure the backend includes them.
- [ ] I can test a wheel and generated command in a clean environment, outside the source tree.
- [ ] I can diagnose slow startup with `-X importtime` and defer optional imports.
- [ ] I can explain the trade-offs among zipapps, `shiv`, `pex`, PyInstaller, and Nuitka.
- [ ] I understand PATH, Windows launcher, shebang, and PEP 668 considerations.
- [ ] I can apply safe subprocess practices and reason about package-name and dependency trust.
- [ ] I treat CLI names, flags, configuration, output contracts, and exit codes as public interfaces.
- [ ] I can define an internal distribution and version-pinning policy for a team CLI.

## 12. References

Prefer the standards and official project documentation for normative behavior and version-specific options.

- **PEP 621 — Storing project metadata in `pyproject.toml`:** https://peps.python.org/pep-0621/
- **PEP 639 — Improving License Clarity with Better Package Metadata:** https://peps.python.org/pep-0639/
- **PyPA entry points specification:** https://packaging.python.org/en/latest/specifications/entry-points/
- **PyPA `pyproject.toml` specification and project metadata:** https://packaging.python.org/en/latest/specifications/pyproject-toml/
- **PyPA guide to writing `pyproject.toml` (including backend version support for PEP 639):** https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- **Python `importlib.metadata`:** https://docs.python.org/3/library/importlib.metadata.html
- **Python `importlib.resources`:** https://docs.python.org/3/library/importlib.resources.html
- **Python `argparse`:** https://docs.python.org/3/library/argparse.html
- **Python `sys.exit`:** https://docs.python.org/3/library/sys.html#sys.exit
- **Python `zipapp`:** https://docs.python.org/3/library/zipapp.html
- **Python command-line interface and `-X importtime`:** https://docs.python.org/3/using/cmdline.html
- **PEP 668 — Externally managed environments:** https://peps.python.org/pep-0668/
- **pipx documentation:** https://pipx.pypa.io/stable/
- **uv documentation:** https://docs.astral.sh/uv/
- **Click documentation:** https://click.palletsprojects.com/
- **Typer documentation:** https://typer.tiangolo.com/
- **Cyclopts documentation:** https://cyclopts.readthedocs.io/
- **shiv documentation:** https://shiv.readthedocs.io/
- **PEX documentation:** https://docs.pex-tool.org/
- **PyInstaller documentation:** https://pyinstaller.org/en/stable/
- **Nuitka documentation:** https://nuitka.net/doc/user-manual.html
- **Python Packaging User Guide — packaging projects:** https://packaging.python.org/en/latest/tutorials/packaging-projects/

---

**Lesson boundary:** this lesson explains how installed Python packages expose commands. Building wheels and sdists is covered in Lessons 01–02; plugin discovery through non-console entry-point groups is covered in Lesson 04; publication and release automation are covered later in Module 18.
