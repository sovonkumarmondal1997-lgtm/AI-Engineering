# Import System: Finders, Loaders, and `sys.modules`

> **Target:** CPython 3.12–3.14. Examples use documented public APIs unless marked otherwise. Check `python --version` before comparing output. Private CPython internals and startup behavior can vary by patch release, build, platform, and launch mode.
>
> **Version note on explicit lazy imports:** PEP 810 was accepted for Python 3.15. Its `lazy import` syntax is **not valid in Python 3.12–3.14**. This lesson uses lazy-import mechanisms available in the target versions and describes PEP 810 separately as a forward-looking version boundary.

## Learning outcomes

After this lesson, you should be able to:

1. Trace a normal import from `sys.modules` lookup through spec discovery, module creation, execution, and name binding.
2. Explain module specs and common module attributes, and distinguish an import package from a distribution package.
3. Diagnose `sys.path`, environment, `site`, virtual-environment, package, namespace-package, and circular-import problems.
4. Explain the roles of `sys.meta_path`, `sys.path_hooks`, path-entry finders, loaders, and the standard import machinery.
5. Use `importlib`, `importlib.metadata`, and `importlib.resources` for their intended purposes.
6. Measure import costs, reason about lazy loading, and understand the current version status of PEP 810.
7. Recognise shadowing and import-path risks; use isolated/safe-path modes and reproducible deployment practices appropriately.
8. Build a small custom finder/loader or runtime plugin loader, with an explicit allow-list and per-plugin error isolation.
9. Explain extension-module ABI compatibility, multi-phase initialisation, import locking, bytecode caches, zip imports, and frozen-app considerations at the appropriate level.
10. Diagnose imports using `-v`, `find_spec`, `module.__file__`, distribution metadata, and audit hooks, while understanding that import hooks are not a security sandbox.

## Prerequisites

Know how to write functions, use modules and packages, handle exceptions, create a virtual environment, and run Python from a shell. Basic familiarity with `sys`, `pip`, and the difference between a source file and an installed package is helpful. You do not need to know CPython's C source to complete the experiments.

## 1. Mental model: import is a protocol, not just file loading

The `import` statement asks Python to find a module, initialise it if needed, and bind names in the importing scope. The import system can load code from ordinary source files, extension modules, frozen modules, zip archives, namespace packages, or custom sources supplied by import hooks.

For a typical first import of a module name, the simplified sequence is:

```text
import name
   │
   ├─ Is name already in sys.modules?
   │      └─ yes: reuse the cached module object
   │
   └─ no: ask finders for a ModuleSpec
          ├─ determine loader and origin/package search locations
          ├─ create a module object
          ├─ place it in sys.modules before executing its code
          ├─ execute module code (which may itself import modules)
          └─ bind the requested name(s) in the importing namespace
```

This diagram is deliberately simplified. Imports can involve parent packages, relative-name resolution, multiple finders, namespace-package composition, and custom loaders. In particular, the module is normally placed in `sys.modules` **before** its body is executed. This prevents infinite recursive loading and explains why a circular import can see a partially initialised module.

### Why it matters in production

Import mechanics explain many common incidents: a local `json.py` shadows the standard library; a service imports a different package version than expected; a plugin is missing; startup is slow; a circular import observes a name before it exists; or a dependency works on a developer laptop but fails in a hermetic container.

### First observation

```python
import importlib
import json
import sys

print(json.__name__)
print(json.__spec__.origin)
print("json cached:", sys.modules.get("json") is json)

# Re-executes the module code in the existing module object; use cautiously.
importlib.reload(json)
```

Representative output includes `json`, a path or other origin description for the loaded `json` implementation, and `json cached: True`. The origin and path vary by installation and implementation.

`reload()` is not a production hot-swap mechanism. It generally re-executes code in the existing module namespace; it does not update references imported elsewhere with `from module import name`, and it cannot reliably undo side effects or migrate existing objects to new class/function definitions.

## 2. `sys.modules`: the module cache and its edge cases

`sys.modules` is a mapping from fully qualified module names to module objects. It is the first place the import machinery checks. Repeated imports usually reuse the cached module rather than searching the filesystem and executing the module body again. A key mapped to `None` deliberately makes the corresponding import fail with `ModuleNotFoundError`; deleting a key causes a later import to search again, but does not destroy module objects still referenced elsewhere.

```python
import sys
import json

first = sys.modules["json"]
import json as json_again
second = sys.modules["json"]

print(first is second)
print(json is json_again)
```

Output:

```text
True
True
```

The import statement still performs name-binding semantics in the importing scope, but module initialisation is normally not repeated. Importing a submodule also involves parent packages, e.g. `import package.submodule` generally makes `package` available and binds the top-level package name in the current scope.

### Why the cache is updated before module execution

Suppose `alpha` imports `beta`, and `beta` imports `alpha`. Before `alpha` finishes running, the import system has already inserted its module object into `sys.modules`. When `beta` asks for `alpha`, it can get that object before `alpha` has defined every name. This is intentional and necessary to break recursive import loops, but it means a circular import can observe incomplete state.

If module execution fails, the import machinery removes the newly failing module entry it inserted, while modules already present before that load are left alone. Do not depend on manually mutating `sys.modules` as a normal dependency-management strategy: deleting or replacing entries can create duplicate module identities, inconsistent classes, and hard-to-debug state.

### Second-import self-check preview

On the second `import json` in one interpreter, Python normally finds `json` in `sys.modules`, reuses that module object, and binds the local name. It does not normally rerun `json`'s top-level code. The cache is per interpreter (usually one interpreter per process in a simple program), not a persistent disk cache; subinterpreters have separate import state.

## 3. `ModuleSpec`, module creation, and module attributes

A `ModuleSpec` describes how a module should be loaded. It typically includes the fully qualified name, loader, origin, whether the module is a package, and package search locations. Finders produce specs; loaders create/execute modules according to the import protocol.

Useful attributes to inspect:

| Attribute | Meaning and caveat |
|---|---|
| `__name__` | Module's import name; can be `__main__` when executed as a script. |
| `__file__` | Location string for file-backed modules; may be absent for built-in, namespace, or other modules. |
| `__spec__` | Import-system spec, often the best starting point for loader/origin details. |
| `__package__` | Legacy package-context attribute. Prefer `__spec__.parent`; fallback use was deprecated in 3.12, and the attribute was deprecated in 3.13 with removal from import-system handling in 3.15. |
| `__path__` | Present on packages; iterable of locations used to search for submodules. Prefer `__spec__.submodule_search_locations` for import-system introspection. Namespace packages can have multiple locations. |
| `__loader__` | Loader associated with the module. Prefer `__spec__.loader`; setting `__loader__` without setting `__spec__.loader` was deprecated in 3.12, with that legacy handling scheduled for removal in 3.16. |
| `__cached__` | Optional cached-bytecode path. Prefer `__spec__.cached`; setting `__cached__` without setting `__spec__.cached` was deprecated in 3.13, with that legacy handling scheduled for removal in 3.15. |

```python
import json

for attr in ("__name__", "__file__", "__spec__", "__package__",
             "__path__", "__loader__", "__cached__"):
    print(f"{attr}: {getattr(json, attr, '<not present>')}")
```

Output is installation-specific. For an ordinary non-package module, `__path__` is typically absent. A package's `__path__` controls where its submodules are searched.

### Import protocol and failure cleanup

For custom loading, the key operations are typically:

1. Find a spec.
2. Create a module from the spec (often with `importlib.util.module_from_spec`).
3. Insert it into `sys.modules` under the correct name before execution.
4. Execute with `spec.loader.exec_module(module)`.
5. If execution fails, remove the new cache entry and propagate the error.

Use `importlib.import_module()` for ordinary programmatic imports. Avoid calling the lower-level `__import__()` directly unless you specifically need its different return-value behavior.

## 4. How `sys.path` is built; `site`, environment, and virtual environments

`sys.path` is the search path used by the standard path-based finder. Its initial contents depend on how Python was launched and configured. Typical contributors include:

- The script's directory (or an empty-string entry representing the current directory in some launch modes).
- `PYTHONPATH`, unless ignored by the selected mode.
- Standard-library and platform-specific library locations.
- Site-package directories, usually added/processed by `site`.
- `.pth` files in site directories, which may add paths; lines beginning with `import` followed by whitespace can execute code during site initialisation.
- Customisations by an embedding application, launcher, or framework.

Inspect the actual environment rather than assuming a universal order:

```bash
python --version
python -c "import sys; print(sys.executable); print(*sys.path, sep='\n')"
python -m site
```

`sys.path` is a list, not a cryptographic trust policy. Earlier entries can take precedence and shadow later entries. `PYTHONPATH` can unintentionally expose unexpected modules across projects if it is globally configured.

### Virtual environments

A virtual environment usually isolates installed distributions from the base interpreter while still using the base interpreter's standard library. Inspect:

```python
import sys
print("executable:", sys.executable)
print("prefix:", sys.prefix)
print("base_prefix:", sys.base_prefix)
```

In a typical active virtual environment, `sys.prefix` differs from `sys.base_prefix`; exact details depend on platform and configuration. `pyvenv.cfg` and the `site` module affect how environment paths are established. The virtual environment does not automatically make arbitrary imports hermetic: the current directory, environment variables, editable installs, `.pth` files, and application-added paths can still matter.

### Safer launch modes

- `python -I` enables isolated mode: ignores `PYTHON*` environment variables and excludes the current/script directory and user site-packages from the usual import path setup. It is useful for controlled execution, but it does not make arbitrary code safe.
- `python -P` (or `PYTHONSAFEPATH`) avoids prepending a potentially unsafe path such as the script directory/current directory. Available since Python 3.11.
- `-S` disables automatic import of `site` during startup; this changes site-package and `.pth` processing and is not a drop-in security switch for every application.

Try `python -c "import sys; print(sys.flags); print(sys.path)"`, then compare with `python -I -c ...` and `python -P -c ...`. The exact path list depends on installation and launch context.

### Editable installs (PEP 660)

An editable install makes imports resolve to a development source tree while package metadata is installed into the environment. Backends may implement this using `.pth` files, generated import hooks, or other mechanisms allowed by the packaging backend. Editable mode is convenient for development, but it can make import resolution differ from a built wheel. Always test release artifacts in a clean environment as well as the editable checkout.

## 5. Packages, absolute and relative imports, namespace packages

A package is a module that can contain submodules. A regular package usually has an `__init__.py`; its `__path__` identifies locations for submodule search. Absolute imports name a module from the import root, while explicit relative imports use leading dots relative to the current package:

```python
# In package/service/handlers.py
from package.service import models   # absolute
from . import validators             # relative to package.service
from ..settings import API_TIMEOUT   # relative to parent package
```

Relative imports need package context; executing a file directly as `python package/service/handlers.py` often loses the package context expected by these imports. Prefer `python -m package.service.handlers` when appropriate, or structure the project as an installable package.

### Namespace packages (PEP 420)

A namespace package can combine portions from multiple directories without a single `__init__.py`. It is useful when separate distributions contribute subpackages under one shared namespace. The path-based finder can discover multiple portions and expose them through the package's search path.

Trade-off: namespace packages can make the effective package location less obvious, and a regular package with `__init__.py` may take precedence over namespace portions depending on search conditions. Diagnose using `package.__spec__`, `package.__path__`, and `package.__file__` (which may be absent).

### Experiment: see the resolved origin

```python
import importlib.util

for name in ("json", "email", "this_name_should_not_exist_42"):
    spec = importlib.util.find_spec(name)
    print(name, "->", None if spec is None else spec.origin)
```

Expected: installed modules usually have a spec; a deliberately nonexistent name usually returns `None`. The origin can be `built-in`, `frozen`, a file path, or another loader-defined value. `find_spec("pkg.submodule")` may import the parent package to resolve the submodule; it is not always a side-effect-free filesystem query.

## 6. Circular imports and partially initialised modules

Consider two modules where `alpha.py` imports `value` from `beta.py`, while `beta.py` imports `value` from `alpha.py`. When `alpha` starts, it is inserted into `sys.modules`, then begins executing. It imports `beta`; `beta` finds `alpha` in the cache, but `alpha.value` may not have been assigned yet. A `from alpha import value` can therefore fail with an error mentioning a partially initialised module.

### Minimal reproduction

Create a temporary directory with these two files.

`alpha.py`:

```python
from beta import beta_value
alpha_value = "alpha ready"
```

`beta.py`:

```python
from alpha import alpha_value
beta_value = "beta ready"
```

Run `python -c "import alpha"` from that directory. Expected: an `ImportError` because `alpha_value` is requested before `alpha.py` reaches its assignment. Exact wording varies by version.

### Fixes, ranked by design quality

1. **Restructure shared concepts:** move common constants/types/interfaces into a third module that both can import.
2. **Import a module rather than a specific name:** `import alpha` can postpone attribute lookup until use, but it is only a fix if the attribute is available by then; it does not eliminate all cycles.
3. **Move an import inside a function:** useful when the dependency is needed only at runtime and the call happens after initialisation. This can hide architectural coupling, so use intentionally.
4. **Use dependency injection or a registration phase:** especially for plugins and framework components.

Do not use `importlib.reload()` as a general circular-import repair. The underlying dependency cycle remains.

## 7. Finders, loaders, and the standard machinery

### The layers

- **Meta-path finders** are consulted through `sys.meta_path`. Standard entries commonly include `BuiltinImporter`, `FrozenImporter`, and `PathFinder`. A custom meta-path finder can intercept a name before path-based lookup.
- **Path-entry finders** are selected for entries in `sys.path` or a package's `__path__`. `sys.path_hooks` contains callables that can produce finders for path entries; `sys.path_importer_cache` caches the result for a path entry.
- **Loaders** create/execute module code. Common loader classes include `SourceFileLoader`, `SourcelessFileLoader`, and `ExtensionFileLoader`. Built-in/frozen modules use their corresponding machinery.
- **ModuleSpec** joins finder and loader decisions: it records the name, loader, origin and package search locations.

```python
import sys
import importlib.machinery

print("meta path:")
for finder in sys.meta_path:
    print(" ", finder)

print("path hooks:")
for hook in sys.path_hooks:
    print(" ", hook)
```

Output is interpreter-specific. Tools such as test runners, coverage systems, editable-install backends, and application packagers may add hooks or alter import behavior. Do not assume `sys.meta_path` contains exactly the same entries in every process.

### `find_spec`, `module_from_spec`, and direct-path imports

Use `importlib.util.find_spec(name)` to ask the active import system for a spec. Use `importlib.util.spec_from_file_location(name, path)` when a file really must be loaded under a chosen module name. Use `module_from_spec(spec)` to create a module and `exec_module(module)` to execute it.

```python
import importlib.util
import sys
from pathlib import Path

def import_from_path(module_name: str, file_path: str):
    """Load one trusted Python source file under an unused module name."""
    if module_name in sys.modules:
        raise ImportError(f"module name already exists: {module_name!r}")

    path = Path(file_path).resolve()
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {module_name!r} from {path}")
    module = importlib.util.module_from_spec(spec)
    # Insert before execution so recursive imports see the same module object.
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        # Remove only the object this helper inserted; preserve any replacement.
        if sys.modules.get(module_name) is module:
            del sys.modules[module_name]
        raise
    return module
```

This resembles the standard import protocol but is not a full replacement for `import`. In particular, package-relative imports require correct package names/spec details, parent package handling, and appropriate search locations. Never load untrusted paths simply because you can load them. This helper rejects a name already present in `sys.modules`; production code should also use deliberate naming and package-context rules rather than treating direct-path loading as a general import replacement.

Use `importlib.import_module("package.module")` for normal dynamic imports. After creating a module file at runtime, call `importlib.invalidate_caches()` if the path finder might have cached directory contents.

## 8. `importlib.metadata` versus `importlib.resources`

These APIs solve different problems:

- `importlib.metadata` reads **distribution metadata**: installed distribution version, files, requirements, and entry points. A distribution name is not necessarily the same as an import package name. One distribution may provide multiple import packages, and a namespace package may be supplied by several distributions.
- `importlib.resources` accesses **data files belonging to a package** without assuming the package is a normal directory on disk. This matters for zip imports and other non-filesystem loaders.

```python
from importlib import metadata, resources

# Distribution metadata: this may raise PackageNotFoundError if not installed.
try:
    print("pip distribution version:", metadata.version("pip"))
except metadata.PackageNotFoundError:
    print("pip distribution metadata is not installed here")

# Package data: create your own package and data file to test this reliably.
# Example: resources.files("my_package").joinpath("data/schema.json").read_text()
```

The `pip` output depends on the environment. `resources.files()` expects an importable package, and not every resource needs to be a permanent real filesystem path. Prefer `Traversable` operations (for example `read_text` or `open`) rather than assuming `Path(__file__).parent` works for every loader.

### Entry points and plugin discovery

`metadata.entry_points()` discovers declared plugin entry points from installed distributions. It does not make the plugin trusted, and discovery does not mean the code has already been safely executed. Loading an entry point imports and executes third-party code. Apply an explicit policy: which distribution/plugin names are allowed, which versions are accepted, and which capabilities are available to the plugin.

## 9. Import-time costs and lazy import patterns

### Measure first

Use the interpreter's import-time reporting rather than guessing:

```bash
python -X importtime -c "import json; import pathlib"
```

The output reports import timing information, usually with cumulative and self-time columns and a tree-like nesting structure. Exact formatting and timing vary by version and platform. Use the same command, interpreter, environment, and workload when comparing revisions. Timing includes filesystem/cache state and import side effects; it is not a pure benchmark of the import machinery.

For verbose import tracing, use `python -v -c "import json"`. It can produce extensive output.

### Practical ways to reduce startup time

- Remove unused top-level dependencies.
- Split optional features into modules and import them only when the feature is invoked.
- Avoid expensive network, filesystem, or registry work at import time; make it explicit in a function or application startup phase.
- Keep plugin discovery and plugin activation separate.
- Measure CLI subcommands separately, including `--help` paths.

### Available lazy patterns in Python 3.12–3.14

1. **Function-local import:** simple and explicit; the import statement is reached only when the function runs. Once imported, the module is cached, but the statement still has some lookup overhead on subsequent calls.
2. **Module-level `__getattr__` (PEP 562):** can defer loading a named attribute until it is requested. Useful for compatibility facades, but can surprise introspection and type-checking tools unless carefully documented.
3. **`importlib.util.LazyLoader`:** defers a module loader's execution until a module attribute is accessed. It has loader/spec constraints and delayed errors occur at attribute access, which can be far from the import statement. It is not a general replacement for all `from ... import ...` behavior.

Example of a simple function-local import:

```python
def render_report(rows):
    # json is imported only if this feature is invoked.
    import json
    return json.dumps(rows)
```

This often improves startup only if the function is not called on the startup path. It does not make importing `json` itself faster and should not be applied mechanically; local imports can obscure dependencies.

### PEP 810 status — do not use unsupported syntax on target versions

PEP 810, **Explicit lazy imports**, is final for Python 3.15. The syntax `lazy import json` and `lazy from package import name` is not available in CPython 3.12–3.14 and will produce a syntax error there. Do not put it into code intended to run on the target versions. When adopting Python 3.15+, check that release's documentation and feature behavior rather than treating the PEP text as a substitute for a release-specific test.

## 10. Shadowing, path hijacking, and import security

A module name is resolved according to the active import path and finders, not according to what a developer intended. If a project directory contains `random.py`, `json.py`, `email.py`, `types.py`, or `test.py`, it can shadow a standard-library module or break tools that import it. Shadowing can also arise from a compromised `PYTHONPATH`, malicious `.pth` code, an unexpected editable install, or a typosquatted distribution.

### Diagnostic steps

```bash
python -c "import json; print(json.__file__); print(json.__spec__.origin)"
python -v -c "import json"
python -m pip show -f PACKAGE_NAME
```

And in Python:

```python
import importlib.util
print(importlib.util.find_spec("json"))
```

Use `find_spec` and `__file__`/`__spec__.origin` to establish what was selected. `pip show -f` describes a distribution, which may not map one-to-one to an import name. If `json` was already imported from a wrong location, inspecting the current module object is more informative than searching in a fresh process alone.

### Hardening checklist

- Launch with `-I` or `-P` when compatible with the application's needs.
- Avoid global `PYTHONPATH` settings and unnecessary writable import directories.
- Keep `.pth` files and editable-install hooks under change control; `.pth` files may execute code.
- Pin dependencies and verify distributions/wheels through your organisation's supply-chain process.
- Do not automatically load every module found in a directory or every entry point discovered on the machine.
- Treat imported code as code execution with the process's privileges.

**Critical limitation:** import hooks, allow-lists, and audit hooks are not a complete sandbox. A module that has been imported can execute arbitrary Python and native code with the process's permissions. Security isolation requires process/container/OS boundaries, least privilege, and dependency provenance—not just a custom finder.

## 11. Mini experiment: allow-listed plugin loader with error isolation

This experiment loads only named plugins from a controlled directory and continues if one plugin fails. It demonstrates explicit policy and operational isolation; it is **not** a sandbox and must only be run with trusted local code.

Create a directory named `plugin_demo` with these files:

`plugin_demo/hello.py`:

```python
def run():
    return "hello from plugin"
```

`plugin_demo/broken.py`:

```python
raise RuntimeError("plugin failed during import")
```

`plugin_demo/denied.py`:

```python
def run():
    return "this should not be imported by the allow-list demo"
```

Save the following as `run_plugins.py` in the parent directory:

```python
from importlib import import_module

# Explicit allow-list: never import arbitrary names supplied by user input.
ALLOWED = {"hello", "broken"}


def load_plugins(package_name, requested_names):
    results = {}
    for name in requested_names:
        if name not in ALLOWED:
            results[name] = {"status": "rejected", "error": "not allow-listed"}
            continue
        qualified_name = f"{package_name}.{name}"
        try:
            module = import_module(qualified_name)
            entry = getattr(module, "run", None)
            if not callable(entry):
                raise TypeError("plugin must expose callable run()")
            results[name] = {"status": "loaded", "result": entry()}
        except Exception as exc:
            # One plugin failure must not prevent later plugins from being checked.
            results[name] = {
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
            }
    return results


if __name__ == "__main__":
    for name, outcome in load_plugins(
        "plugin_demo", ["hello", "broken", "denied"]
    ).items():
        print(name, outcome)
```

Add `plugin_demo/__init__.py` (it may be empty) and run `python run_plugins.py` from the parent directory. Representative output, with insertion order preserved on supported modern Python versions:

```text
hello {'status': 'loaded', 'result': 'hello from plugin'}
broken {'status': 'failed', 'error': 'RuntimeError: plugin failed during import'}
denied {'status': 'rejected', 'error': 'not allow-listed'}
```

The import error for `broken` occurs when the module executes, and the exception is caught so `denied` can still be processed. The `except Exception` block deliberately does not catch `BaseException` subclasses such as `KeyboardInterrupt` and `SystemExit`.

### Experiment procedure

1. Run the script and confirm that `hello` succeeds, `broken` is isolated, and `denied` is rejected without import.
2. Add a new `unexpected.py` and request it; confirm that it is rejected until added to the allow-list.
3. Remove `run()` from `hello.py`; observe the contract-validation error.
4. Add a print statement to a plugin's top level; observe that import itself executes the statement before `run()` is called.
5. Inspect `sys.modules` after the run to see which modules were imported. The failed module's cache state may be removed after import failure; do not depend on private cache mutation details.

**Interpretation:** allow-lists reduce accidental plugin loading, and per-plugin exception handling prevents one ordinary plugin exception from aborting the whole discovery run.

**What this does not prove:** the allow-list does not make an approved plugin safe, isolate memory/state, limit filesystem/network access, prevent malicious native code, or protect against dependency compromise. For untrusted plugins, use a separate process with a restricted OS-level security boundary and a narrow IPC protocol.

## 12. Writing a minimal meta-path finder/loader

A meta-path finder can observe or provide imports before the standard `PathFinder`. This illustrative finder handles only names beginning with `json`, delegates their path-based spec lookup to `PathFinder`, and logs both elapsed lookup time and the returned origin. It returns the delegated spec (or `None` if the path finder cannot find the name); the import machinery then uses the spec's loader. The finder does not execute the module body itself.

```python
import importlib.abc
import importlib.machinery
import sys
import time

class LoggingFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if not fullname.startswith("json"):
            return None
        started = time.perf_counter()
        spec = None
        try:
            # Delegate to the standard path-based finder, not to this finder.
            spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
            return spec
        finally:
            elapsed_ms = (time.perf_counter() - started) * 1000
            origin = spec.origin if spec is not None else "<not found by PathFinder>"
            print(f"import lookup {fullname}: {elapsed_ms:.3f} ms; origin={origin}")

# Retain the exact hook object so cleanup removes only this registration.
finder = LoggingFinder()
sys.meta_path.insert(0, finder)
try:
    import json
finally:
    sys.meta_path.remove(finder)
```

If `json` is already in `sys.modules`, the finder normally will not be called. In environments where startup customisation may preload `json`, save the snippet as `finder_demo.py` and run `python -S finder_demo.py` to make the experiment more reproducible; `-S` skips automatic `site` initialisation and is not representative of every production launch. The hook logs **lookup time and the spec origin**, not module execution time, and it only watches names with the selected prefix that reach path-based lookup; it does not literally log every import (for example, cache hits bypass finders). A finder that delegates incorrectly to `importlib.util.find_spec(fullname)` can recurse into itself; direct delegation to the intended later finder avoids that problem. `PathFinder.find_spec()` is a public API, but this logging hook is still instrumentation that can affect import behavior and timing.

For a real loader, implement `find_spec()` to return a valid `ModuleSpec` with a loader, and implement the appropriate `create_module()`/`exec_module()` methods. Follow the import protocol carefully, handle failure cleanup, and test circular imports. For source transformation, use a controlled loader that obtains source, parses/transforms the AST, compiles it, and executes the code in the module namespace. Keep transformations deterministic, explainable, and limited to trusted inputs. Test runners such as pytest use import hooks for features such as assertion rewriting; this is powerful tooling behavior, not a general recommendation to rewrite arbitrary application code.

### Example: load a module from an in-memory source mapping

A finder is not required to search the filesystem. This minimal example serves a module from a dictionary, illustrating the same finder → spec → loader → execution protocol. It is deliberately a **single, non-package module** and executes the configured source as code.

```python
import importlib.abc
import importlib.util
import sys

SOURCES = {
    "virtual_greeting": "MESSAGE = 'hello from memory'\n",
}

class DictLoader(importlib.abc.Loader):
    def __init__(self, source):
        self.source = source

    def exec_module(self, module):
        code = compile(self.source, f"<memory:{module.__name__}>", "exec")
        exec(code, module.__dict__)

class DictFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        source = SOURCES.get(fullname)
        if source is None:
            return None
        loader = DictLoader(source)
        return importlib.util.spec_from_loader(
            fullname, loader, origin=f"memory:{fullname}"
        )

finder = DictFinder()
sys.meta_path.insert(0, finder)
try:
    import virtual_greeting
    print(virtual_greeting.MESSAGE, virtual_greeting.__spec__.origin)
finally:
    # Hooks and synthetic modules are process-global state; clean up the demo.
    sys.meta_path.remove(finder)
    sys.modules.pop("virtual_greeting", None)
```

Expected output:

```text
hello from memory memory:virtual_greeting
```

This pattern can be adapted to trusted source stored in a database or archive. A package-capable loader must additionally define package search locations and support submodule resolution/resources as required. Never feed untrusted source to `compile`/`exec`; an import hook does not confine the code it runs.

### Example: a narrow import-denial policy (not a sandbox)

A finder can reject a name by raising an import exception rather than returning `None`. This can be useful for a controlled test or policy diagnostic, but it is not a security boundary. Save the snippet as `deny_import_demo.py` and run `python -S deny_import_demo.py` so normal `site` startup does not pre-import the demonstration target:

```python
import importlib.abc
import sys

class DenyJsonFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "json" or fullname.startswith("json."):
            raise ModuleNotFoundError("blocked by demonstration policy", name=fullname)
        return None

finder = DenyJsonFinder()
sys.meta_path.insert(0, finder)
try:
    try:
        import json
    except ModuleNotFoundError as exc:
        print(type(exc).__name__, exc.name)
finally:
    sys.meta_path.remove(finder)
```

Representative output in a fresh CPython process:

```text
ModuleNotFoundError json
```

If `json` was already in `sys.modules`, the finder would not be consulted. Code can also access existing objects or use other mechanisms, and native code can bypass Python-level assumptions. Treat this as an import-policy demonstration only; use OS process isolation for untrusted code.

### AST rewriting inside a controlled loader

A loader can transform source before compilation. For example, an `ast.NodeTransformer` can replace a selected literal, then `ast.fix_missing_locations()` and `compile()` produce an executable code object. The transformation must preserve intended semantics and source locations; the result may differ from the original source and may complicate debugging, tracebacks, signatures, and tooling. The following small demonstration is **not** a general-purpose security filter:

```python
import ast

source = "answer = 40 + 2\n"
tree = ast.parse(source, filename="<input>")

class RewriteForty(ast.NodeTransformer):
    def visit_Constant(self, node):
        if type(node.value) is int and node.value == 40:
            return ast.copy_location(ast.Constant(value=41), node)
        return node

tree = RewriteForty().visit(tree)
ast.fix_missing_locations(tree)
namespace = {}
exec(compile(tree, "<rewritten>", "exec"), namespace)
print(namespace["answer"])
```

Expected output is `43`. In a real import loader, obtain source using that loader's supported API, transform the AST, compile with an appropriate filename, and execute in the module namespace. Avoid broad rewrites of third-party code unless the behavior and maintenance costs are explicit.

### Import audit hooks

`sys.addaudithook()` can observe documented audit events, including `import` events. A hook may log useful event arguments, but event details vary by operation/version and an audit hook cannot be treated as a complete record of all behavior. Hooks run in-process and can affect performance. They are not a security sandbox and cannot safely contain malicious code that already has process privileges. A Python-level hook is permanent for that interpreter; use a short-lived diagnostic process when experimenting.

```python
import sys

def log_import_event(event, args):
    if event == "import":
        # Log only the module-name field; full arguments may contain paths.
        name = args[0] if args else "<no-name>"
        print("audit import:", name)

sys.addaudithook(log_import_event)
import json
```

Save as `audit_import.py` and run `python -S audit_import.py` if normal site initialisation has already loaded `json`; otherwise choose a target module that is not yet present in `sys.modules`. The exact event sequence and arguments depend on the import path and interpreter version. Existing hooks can prevent a new Python-level hook from being added, so do not assume registration succeeded in a process you do not control.

Use audit hooks for diagnosis and policy telemetry, not as your only control against untrusted imports. Do not assume every import maps to exactly one event with a stable argument shape; verify against the deployed Python documentation.

## 13. Extension modules, ABI tags, and multi-phase initialisation

Pure Python modules are commonly loaded from `.py` source and may use `.pyc` bytecode caches. Extension modules are native shared libraries—typically `.so` on many Unix-like systems and `.pyd` on Windows—that must be compatible with the interpreter, platform, architecture, and ABI.

### Key terms

- **`PyInit_modulename`:** the conventional exported initialisation function for an extension named `modulename`. It is used by both older single-phase and PEP 489 multi-phase designs: a single-phase initializer returns a module object, while a multi-phase initializer returns a `PyModuleDef` that describes creation/execution phases and slots.
- **ABI tag:** packaging tag indicating interpreter/ABI/platform compatibility. A wheel tag helps pip decide whether a wheel is compatible; it is not a guarantee that every dependency or external library is compatible.
- **`abi3`:** the stable ABI mechanism that allows certain extensions built against the limited API to work across supported CPython versions. The extension must actually obey the Limited API/stable ABI constraints; simply renaming a wheel does not make it `abi3` compatible.
- **Multi-phase initialisation (PEP 489):** separates module creation from execution and supports module-specific state. Since CPython 3.12, extension modules must use multi-phase initialisation to be imported in subinterpreters; this does not by itself guarantee full subinterpreter safety.
- **Per-interpreter state:** extension state should be associated with the interpreter/module rather than stored carelessly in process-global mutable C variables when supporting subinterpreters or free-threaded configurations.

A C extension may fail to import due to a missing shared library, wrong architecture, unsupported Python ABI, unresolved symbol, or incorrect initialisation function. Inspect the complete exception and wheel tags; test the exact platform and Python build used in deployment. Native extensions can crash the process, and import-path controls do not isolate them.

For extension authors, consult the current C API documentation and PEP 489. Support for subinterpreters and free-threaded builds must be declared and implemented according to the relevant current APIs; it cannot be inferred from successful import in a conventional GIL-enabled build.

## 14. Import locks and concurrency

Importing a module can execute arbitrary top-level code, and multiple threads may request the same module concurrently. CPython's import machinery uses locks, including per-module import locks, to coordinate module initialisation and reduce duplicate execution. The precise implementation is CPython-specific and has evolved; do not build application synchronization assumptions on private lock internals.

Circular imports that cross threads can produce complicated wait relationships. Keep module top-level code simple and avoid acquiring application locks or starting complex background work during import. Prefer explicit initialisation functions after imports complete. In free-threaded CPython builds, re-check current documentation for concurrency guarantees and extension compatibility; do not assume behavior based solely on a GIL-enabled build.

**Practical rule:** imports should ideally define objects and register predictable metadata, not perform network calls, wait for application locks, start workers, or mutate global state in ways that depend on import order.

## 15. Hermetic and reproducible imports: zip, frozen apps, and bytecode

### Hermetic imports

A hermetic application controls its interpreter, dependencies, search paths, and startup configuration so the same deployment resolves the same modules. Useful practices include locked dependencies, reproducible builds, clean virtual environments, avoiding ambient `PYTHONPATH`, testing built wheels, and inspecting module origins in diagnostics. `-I` can reduce environmental influence but is not a complete hermetic-build strategy.

### Zip imports and `zipapp`

`zipimport` can load Python modules from zip archives. `zipapp` packages a Python application into a runnable archive (often `.pyz`). This can simplify distribution, but native extension modules generally cannot be imported directly from a zip archive in the same way as pure Python source; deployment may need to extract native components. Resource access should use `importlib.resources` rather than assume a normal source-tree path.

### Frozen applications

Tools such as PyInstaller bundle an interpreter/application dependencies and may use bootstrapping and custom import machinery. A module may have an origin like `frozen` or a tool-specific path rather than a conventional `.py` file. Diagnose the packaged executable itself; behavior from a source checkout does not prove the frozen artifact includes all dynamic imports/resources.

### `.pyc` files, PEP 552, and performance

CPython compiles source to bytecode and can cache it in `.pyc` files under `__pycache__`. Bytecode caches can avoid recompiling source, but do not skip module execution: top-level statements still run when the module is imported in a new process. The `.pyc` format and bytecode are CPython/version-specific implementation details, not a portable interchange format.

- **Timestamp-based invalidation:** the cache header records source metadata (including timestamp and source size). On a normal source import, CPython checks whether that metadata matches the source; coarse timestamp resolution or same-size edits within a timestamp window can matter in unusual build/deployment workflows.
- **Hash-based invalidation (PEP 552):** the header stores a hash of source bytes. A **checked-hash** cache is validated against the source when configured to do so; an **unchecked-hash** cache relies on the distributor/build workflow to keep the cache consistent. The interpreter option `--check-hash-based-pycs` can override the default policy (`default`, `always`, or `never`).
- `compileall` can select a cache invalidation mode explicitly. For example, `python -m compileall --invalidation-mode checked-hash -q your_package` requests checked-hash caches on supported target versions. Validate the command with the exact interpreter used for the build.

A `.pyc` file is a cache, not a security boundary. It does not prove the source or distribution is trusted, and importing a cached module still executes its module code.

Useful commands and controls:

```bash
python -m compileall -q your_package
python -X importtime -c "import your_package"
```

- `sys.dont_write_bytecode = True` or `-B` prevents writing bytecode cache files, but does not mean Python stops compiling source as needed.
- `PYTHONPYCACHEPREFIX` can redirect bytecode cache files to a separate tree.
- Hash-based `.pyc` files support deterministic validation modes; do not assume every deployment uses checked-hash caches.
- On CPython 3.12–3.14, `-X frozen_modules=off` (or `PYTHON_FROZEN_MODULES=off` where supported) tells the import machinery to ignore most frozen modules; the essential `importlib_bootstrap` and `importlib_bootstrap_external` frozen modules remain in use. The default is generally on for installed non-debug builds and off for source/development or debug builds. Verify the exact interpreter's command-line docs and test the packaged application.

For deployment, bytecode caches are a performance/packaging detail, not a security boundary. Never execute `.pyc` files from untrusted sources. Measure startup on the target artifact and include import-time budgets for latency-sensitive CLIs.

## 16. Practical experiments and diagnostics

### Experiment A — prove the second import uses the cache

**Question:** Does a second import in one process reuse the same module object?

**Setup:** Run a fresh `python -c` process with the Section 2 example.

**Procedure:** Print object identity and `sys.modules` identity before/after a second import. Optionally create a temporary module whose top level prints a marker, then import it twice.

**Expected observation:** the module object identity remains the same and the top-level marker normally appears only on the first successful import in that process.

**Interpretation:** `sys.modules` prevents normal repeated initialisation.

**Does not prove:** imports are free of all lookup/name-binding overhead, that a module can never be reloaded, or that another process shares the same cache.

### Experiment B — diagnose shadowing

**Question:** Which `json` module is this process actually loading?

**Setup:** In a disposable directory, create a file named `json.py` that prints a marker; run `python -c "import json; print(json.__file__)"` from that directory.

**Procedure:** Compare normal launch, `python -P`, and `python -I` from the same location. Remove the test file after the experiment.

**Expected observation:** normal launch may select the local file if it precedes the standard library; safe-path/isolated mode changes the initial path behavior and should prevent that current/script-directory shadowing path from being added in the normal way.

**Interpretation:** import origin depends on startup path configuration.

**Does not prove:** `-I` makes all imports safe, or that a module can never be shadowed through other configured finders/paths.

### Experiment C — measure import time

**Question:** Which imports dominate startup cost for a CLI command?

**Setup/command:** `python -X importtime -c "import json; import pathlib"` and then run the real CLI's fastest path (such as `--help`).

**Procedure:** Capture output for the same interpreter/environment, compare before and after one targeted change, and measure multiple cold/warm trials if filesystem caching matters.

**Expected observation:** nested imports show cumulative/self time; an optional heavy dependency may account for a meaningful share of startup.

**Interpretation:** import-time output identifies candidates for targeted optimisation.

**Does not prove:** all displayed time is CPU time, that one run is statistically stable, or that deferring an import improves end-to-end latency for the common path.

### Experiment D — reproduce a circular import

**Question:** Why can `from alpha import value` fail while `alpha` is only partially initialised?

**Setup:** Use the two files from Section 6 in an empty temporary directory.

**Procedure:** Run `python -c "import alpha"`; then move shared data into a third module and retry.

**Expected observation:** the first version fails before the target name is defined; the refactored version imports successfully.

**Interpretation:** import order and module initialisation order matter.

**Does not prove:** all circular imports fail or that every cycle can be fixed by moving imports into functions.

### Experiment E — plugin allow-list and error isolation

**Question:** Can one plugin fail without preventing the rest of a batch from being processed?

**Setup/command:** Create the `plugin_demo` package from Section 11 and run `python run_plugins.py`.

**Procedure:** Verify success, failure, and rejection statuses; add an unapproved module and request it; then remove `run()` from an approved plugin.

**Expected observation:** approved healthy plugin loads; the import-time exception is recorded as a failure; unapproved plugin is rejected without being imported.

**Interpretation:** explicit policy and exception isolation improve plugin orchestration reliability.

**Does not prove:** plugins are sandboxed or trustworthy. All approved code executes with the host process's privileges.

## 17. Common mistakes and troubleshooting

| Symptom | Likely cause | Diagnostic/action |
|---|---|---|
| `ModuleNotFoundError` | Wrong interpreter/environment, missing distribution, wrong path, typo | Check `sys.executable`, `sys.path`, `python -m pip show`, `find_spec`. |
| `ImportError` mentioning partially initialised module | Circular import asks for a name before it is defined | Refactor shared definitions, inspect import order, avoid `reload` as a bandage. |
| Unexpected stdlib module behavior | Local file/package shadows stdlib | Print `module.__file__` and `module.__spec__.origin`; rename local file and clear stale cache files if relevant. |
| Works in editable checkout, fails after packaging | Dynamic import/resource omitted or different resolution | Test built wheel/frozen artifact in a clean environment; use metadata/resources APIs. |
| CLI startup is slow | Eager optional imports or import-time side effects | Measure with `-X importtime`; defer only measured optional dependencies. |
| Plugin batch stops at one plugin failure | Exception not isolated around each plugin import/entry call | Catch ordinary per-plugin exceptions, log safe context, continue. |
| Module has no `__file__` | Built-in/frozen/namespace/custom loader | Inspect `__spec__` (including `origin`, `loader`, and `submodule_search_locations`); do not assume every module is a file. |
| Extension import fails | ABI/platform mismatch or missing shared dependency | Inspect wheel tags, interpreter version, architecture, and full loader error. |
| Import works locally but not in container | Ambient environment/path or undeclared dependency | Use a clean locked environment, remove global `PYTHONPATH`, inspect origin in deployed process. |

### The syllabus's common mistakes, explicitly

- Do not name application files `email.py`, `json.py`, `test.py`, `random.py`, or other standard-library/common tool names.
- Check how `sys.path[0]` is set by the actual launch command; running a file directly and running a package with `-m` can produce different import contexts.
- Do not use `reload()` for production hot-swap unless you have a carefully designed lifecycle that handles old references, state migration, concurrency, and side effects.

## 18. Self-check questions with answers

### 1. Trace what happens, step by step, on the second `import json` in the same process.

**Answer:** Python checks `sys.modules` for `json`. If the entry is present and valid, the cached module object is reused; normal module body execution and file searching are not repeated. The import statement still applies its name-binding semantics in the current namespace. The cache belongs to that interpreter, not the filesystem; a second process and a separate subinterpreter have separate import state.

### 2. Why does a circular import often yield `ImportError: cannot import name`?

**Answer:** To prevent infinite recursive imports, a newly loading module is inserted into `sys.modules` before its body finishes. A second module in the cycle can therefore obtain the first module while it is only partially initialised. If it executes `from first import some_name` before that name has been assigned, the requested attribute is not available and import fails. Refactoring shared definitions or changing dependency direction is usually better than hiding the import inside a function.

### 3. Implement a meta-path finder that logs every import with the file location and time taken.

**Answer:** A robust logger must distinguish **spec lookup time** from **module execution time**. A `MetaPathFinder.find_spec()` can time discovery and log `spec.origin` for specs it returns, but it cannot accurately measure full execution time just by timing `find_spec()`. To time execution, wrap/decorate the loader (or instrument module execution separately), preserve `create_module()` and `exec_module()` semantics, and account for modules already in `sys.modules` (the finder is not consulted on ordinary cache hits). Do not recursively call `importlib.util.find_spec()` from your own finder for the same name, because it can invoke the finder again. The minimal logging finder in Section 12 demonstrates lookup timing; extending it to loader wrapping is the next exercise.

## 19. Extension exercise: log lookup and execution separately

Starting from Section 12, create a `MetaPathFinder` that delegates to the next appropriate finder and, when it receives a spec, wraps the spec's loader with a small proxy that times `exec_module(module)`. Preserve the original loader methods and metadata, and do not wrap a loader that lacks `exec_module()` without a deliberate compatibility strategy. Run in a fresh process with a module that is not already imported.

Record two measurements:

- **Lookup time:** time spent finding a spec.
- **Execution time:** time spent running the module loader.

Expected: the values are separate and may differ significantly. The result does not measure all process startup costs, nor does it prove the import hook is safe for arbitrary third-party loaders. Be careful not to double-wrap loaders or leave global hooks installed after the experiment.

## 20. Concept map and summary

```text
import statement
   │
   ├─ sys.modules cache hit ──> reuse module object
   │
   └─ cache miss
        ├─ sys.meta_path finders
        │     └─ PathFinder → sys.path_hooks/path-entry finder
        ├─ ModuleSpec (name, loader, origin, package locations)
        ├─ create module → insert in sys.modules
        ├─ execute module body
        └─ bind requested name(s)

module/package ──> metadata (importlib.metadata)
               └─ package data (importlib.resources)

runtime risks: circular initialisation · shadowing · import-time side effects
               · plugin supply chain · extension ABI · retained sys.path hooks
```

Remember these principles:

- `sys.modules` is the per-interpreter module cache; successful normal imports usually execute a module body once per interpreter/module name, unless it is explicitly reloaded or import state is deliberately changed.
- Finders discover; specs describe; loaders create/execute. The standard import system is extensible, but custom hooks must preserve protocol and cleanup behavior.
- `sys.path`, `site`, `.pth` files, virtual environments, editable installs, and launch flags influence what code is imported.
- Distribution metadata and import modules are different namespaces; package resources should not be assumed to be ordinary files.
- Circular imports expose partially initialised modules. Refactor dependency direction rather than relying on reload.
- Measure import cost. Lazy loading shifts work and errors; it does not automatically improve end-to-end performance.
- PEP 810 is final for Python 3.15, not available syntax for the 3.12–3.14 target of this lesson.
- Import hooks and audit hooks are useful mechanisms, not complete security boundaries. Treat imported plugins as executable code.
- `.pyc` files avoid some compilation work, not module execution. Verify imports in the exact deployment artifact and runtime.

## References

Prefer documentation for the exact Python minor version used in deployment.

1. Python import system reference: https://docs.python.org/3/reference/import.html
2. `importlib` documentation (finders, loaders, specs, `LazyLoader`, direct-path recipe): https://docs.python.org/3/library/importlib.html
3. `sys` documentation (`sys.path`, `sys.modules`, `sys.meta_path`, audit hooks, flags): https://docs.python.org/3/library/sys.html
4. `site` documentation and `.pth` processing: https://docs.python.org/3/library/site.html
5. `importlib.metadata`: https://docs.python.org/3/library/importlib.metadata.html
6. `importlib.resources`: https://docs.python.org/3/library/importlib.resources.html
7. `zipimport`: https://docs.python.org/3/library/zipimport.html
8. `compileall`: https://docs.python.org/3/library/compileall.html
9. PEP 420 — Implicit Namespace Packages: https://peps.python.org/pep-0420/
10. PEP 451 — A ModuleSpec Type for the Import System: https://peps.python.org/pep-0451/
11. PEP 489 — Multi-phase Extension Module Initialization: https://peps.python.org/pep-0489/
12. PEP 552 — Deterministic pycs: https://peps.python.org/pep-0552/
13. PEP 660 — Editable Installs for pyproject.toml based builds: https://peps.python.org/pep-0660/
14. PEP 810 — Explicit lazy imports (accepted for Python 3.15; not syntax for 3.12–3.14): https://peps.python.org/pep-0810/
15. Python 3.11 “What’s New” (safe-path flags): https://docs.python.org/3/whatsnew/3.11.html
16. CPython source: `Lib/importlib/_bootstrap.py`, `Lib/importlib/_bootstrap_external.py`, `Lib/importlib/abc.py`, `Python/import.c`, and `Python/importdl.c` (paths/functions can move across releases): https://github.com/python/cpython
