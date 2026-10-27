# Roadmap

The full project tree of this repository, from Stage 0 to Stage 5D, generated from the folders and files on disk.

## Stage summary

| Stage | Folder | Modules | Folders | Files |
|---|---|---|---|---|
| Stage 0 | `Stage 0 — Computer & Digital Foundation` | 5 | 10 | 79 |
| Stage 1 | `Stage 1 — Programming & Computational Thinking` | 25 | 38 | 311 |
| Stage 2 | `Stage 2 — Python for Data Engineering_1` | 23 | 24 | 287 |
| Stage 2B | `Stage 2B — Python for Data Engineering_2` | 6 | 7 | 92 |
| Stage 2C | `Stage 2C — Data Engineering_3` | 10 | 51 | 191 |
| Stage 2D | `Stage 2D — Data Architecture` | 17 | 34 | 207 |
| Stage 2E | `Stage 2E — Production DevOps & Platform Engineering` | 18 | 36 | 266 |
| Stage 3 | `Stage 3 — Data Structures & Algorithms` | 22 | 44 | 374 |
| Stage 4A | `Stage 4A — Basic Mathematics Prerequisite` | 16 | 32 | 208 |
| Stage 4B | `Stage 4B — Mathematics for Machine Learning` | 15 | 30 | 164 |
| Stage 4C | `Stage 4C — Advanced Mathematics for Machine Learning — Deep Learning` | 11 | 22 | 147 |
| Stage 5A | `Stage 5A — Machine Learning Foundation` | 14 | 27 | 164 |
| Stage 5B | `Stage 5B — Advanced Machine Learning` | 16 | 30 | 167 |
| Stage 5C | `Stage 5C — Deep Learning & Transformers` | 16 | 32 | 145 |
| Stage 5D | `Stage 5D — MLOps` | 17 | 33 | 165 |

Module counts include each stage's overview folder.

## Stage 0 — Computer & Digital Foundation

```text
Stage 0 — Computer & Digital Foundation/
├── 00-Stage-0-Overview/
│   ├── Projects/
│   │   ├── 01-stage-0-incident-simulation.md
│   │   └── README.md
│   ├── README.md
│   └── learning-plan.md
├── 01-How-Computers-Work/
│   ├── Projects/
│   │   ├── 01-program-execution-and-gpu-audit.md
│   │   └── README.md
│   ├── 01-motherboard-and-buses.md
│   ├── 02-cpu.md
│   ├── 03-cores.md
│   ├── 04-binary-bits-and-bytes.md
│   ├── 05-hexadecimal.md
│   ├── 06-registers.md
│   ├── 07-instructions-and-machine-code.md
│   ├── 08-compilation-and-interpretation.md
│   ├── 09-cache.md
│   ├── 10-ram.md
│   ├── 11-storage.md
│   ├── 12-hdd-vs-ssd.md
│   ├── 13-gpu.md
│   ├── 14-files.md
│   ├── 15-input-output.md
│   ├── 16-processes.md
│   ├── 17-what-happens-when-a-program-starts.md
│   ├── 18-what-happens-when-a-function-executes.md
│   ├── 19-why-ram-and-storage-are-different.md
│   ├── 20-why-gpus-matter-for-ai.md
│   └── README.md
├── 02-Operating-System-Fundamentals/
│   ├── Projects/
│   │   ├── 01-process-resource-and-port-diagnosis.md
│   │   └── README.md
│   ├── 01-kernel-and-user-space.md
│   ├── 02-system-calls.md
│   ├── 03-processes.md
│   ├── 04-threads.md
│   ├── 05-scheduling.md
│   ├── 06-virtual-memory.md
│   ├── 07-filesystems.md
│   ├── 08-permissions.md
│   ├── 09-environment-variables.md
│   ├── 10-signals.md
│   ├── 11-standard-input-output.md
│   ├── 12-pipes.md
│   ├── 13-shell.md
│   ├── 14-process-lifecycle.md
│   ├── 15-os-tools-overview.md
│   ├── 16-local-networking-for-development.md
│   └── README.md
├── 03-Command-Line/
│   ├── Projects/
│   │   ├── 01-shell-file-and-stream-investigation.md
│   │   └── README.md
│   ├── 01-navigation.md
│   ├── 02-file-operations.md
│   ├── 03-viewing-files.md
│   ├── 04-searching.md
│   ├── 05-text-processing.md
│   ├── 06-pipes-and-redirection.md
│   ├── 07-environment-variables.md
│   ├── 08-shell-scripts.md
│   ├── 09-permissions.md
│   ├── 10-command-line-tools-overview.md
│   ├── 11-safe-terminal-and-filesystem-literacy.md
│   ├── 12-shell-quoting-and-standard-streams.md
│   └── README.md
├── 04-Developer-Environment/
│   ├── Projects/
│   │   ├── 01-developer-environment-health-check.md
│   │   ├── 02-python-workspace-bootstrap.md
│   │   └── README.md
│   ├── 01-vscode-and-terminal.md
│   ├── 02-ide-concepts.md
│   ├── 03-extensions.md
│   ├── 04-formatters-and-linters.md
│   ├── 05-debugger.md
│   ├── 06-virtual-environments.md
│   ├── 07-package-managers.md
│   ├── 08-project-structure.md
│   ├── 09-python-tooling.md
│   ├── 10-git-github-and-ssh-basics.md
│   ├── 11-reproducible-python-workspaces-with-uv.md
│   ├── 12-secrets-and-local-security-hygiene.md
│   ├── 13-evidence-based-debugging-and-notes.md
│   └── README.md
└── README.md
```

## Stage 1 — Programming & Computational Thinking

```text
Stage 1 — Programming & Computational Thinking/
├── 00-Stage-1-Overview/
│   ├── Projects/
│   │   ├── 03-data-quality-and-transformation-pipeline/
│   │   │   ├── data/
│   │   │   │   └── orders.csv
│   │   │   ├── src/
│   │   │   │   └── dqpipe/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── cli.py
│   │   │   │       ├── config.py
│   │   │   │       ├── pipeline.py
│   │   │   │       └── rules.py
│   │   │   ├── tests/
│   │   │   │   ├── test_cli.py
│   │   │   │   ├── test_pipeline.py
│   │   │   │   └── test_rules.py
│   │   │   ├── .gitignore
│   │   │   ├── README.md
│   │   │   ├── config.toml
│   │   │   ├── data-contract.md
│   │   │   ├── learning-notes.md
│   │   │   └── pyproject.toml
│   │   ├── 04-rule-based-risk-review-engine/
│   │   │   ├── config/
│   │   │   │   └── rules.toml
│   │   │   ├── data/
│   │   │   │   └── transactions.csv
│   │   │   ├── src/
│   │   │   │   └── riskreview/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── cli.py
│   │   │   │       ├── engine.py
│   │   │   │       ├── io.py
│   │   │   │       ├── models.py
│   │   │   │       └── rules.py
│   │   │   ├── tests/
│   │   │   │   ├── golden/
│   │   │   │   │   └── decisions.jsonl
│   │   │   │   ├── test_engine.py
│   │   │   │   └── test_io_cli.py
│   │   │   ├── .gitignore
│   │   │   ├── README.md
│   │   │   └── pyproject.toml
│   │   ├── 01-personal-expense-ledger-cli.md
│   │   ├── 02-log-investigation-and-reliability-cli.md
│   │   ├── 03-data-quality-and-transformation-pipeline.md
│   │   ├── 04-rule-based-risk-review-engine.md
│   │   └── README.md
│   ├── README.md
│   └── learning-plan.md
├── 01-Computational-Thinking-and-Program-Design/
│   ├── 01-algorithms-programs-and-data.md
│   ├── 02-values-expressions-statements-and-variables.md
│   ├── 03-input-process-output.md
│   ├── 04-sequence-selection-iteration-and-abstraction.md
│   ├── 05-problem-decomposition.md
│   ├── 06-preconditions-postconditions-and-edge-cases.md
│   ├── 07-pseudocode-flowcharts-and-dry-runs.md
│   ├── 08-state-and-state-modelling.md
│   ├── README.md
│   └── practice-questions.md
├── 02-Python-Core-Language-and-Data-Types/
│   ├── 01-python-files-interpreter-repl-and-indentation.md
│   ├── 02-variables-basic-types-and-none.md
│   ├── 03-operators-and-precedence.md
│   ├── 04-strings-indexing-slicing-and-formatting.md
│   ├── 05-lists-mutation-copying-and-aliasing.md
│   ├── 06-tuples-and-unpacking.md
│   ├── 07-dictionaries-and-lookups.md
│   ├── 08-sets-and-unique-values.md
│   ├── 09-type-conversion-and-truthiness.md
│   ├── 10-mutability-and-immutability.md
│   ├── README.md
│   └── practice-questions.md
├── 03-Control-Flow-Functions-Scope-and-Errors/
│   ├── 01-conditionals-guards-and-boolean-logic.md
│   ├── 02-for-while-loops-and-loop-control.md
│   ├── 03-functions-parameters-and-return-values.md
│   ├── 04-function-arguments-defaults-and-docstrings.md
│   ├── 05-scope-lifetime-and-global-state.md
│   ├── 06-pure-functions-and-side-effects.md
│   ├── 07-exceptions-validation-and-useful-errors.md
│   ├── README.md
│   └── practice-questions.md
├── 04-Problem-Solving-Collections-and-Algorithmic-Habits/
│   ├── 01-search-count-filter-map-and-aggregate.md
│   ├── 02-grouping-deduplication-and-sorting.md
│   ├── 03-big-o-time-and-space-complexity.md
│   ├── 04-choosing-lists-dictionaries-sets-stacks-and-queues.md
│   ├── 05-comprehensions-and-readable-code.md
│   ├── 06-recursion-basics.md
│   ├── 07-basic-parsing-and-regular-expressions.md
│   ├── README.md
│   └── practice-questions.md
├── 05-Text-Files-Structured-Data-and-CLI-Programs/
│   ├── 01-reading-and-writing-text-files.md
│   ├── 02-pathlib-and-portable-paths.md
│   ├── 03-csv-files.md
│   ├── 04-json-and-serialization.md
│   ├── 05-encodings-and-newlines.md
│   ├── 06-command-line-arguments-with-argparse.md
│   ├── 07-standard-streams-and-exit-codes.md
│   ├── 08-logging-versus-print.md
│   ├── 09-environment-configuration-and-input-validation.md
│   ├── README.md
│   └── practice-questions.md
├── 06-Modules-Packages-Dependencies-and-Code-Quality/
│   ├── 01-imports-modules-and-main.md
│   ├── 02-project-layout-and-package-structure.md
│   ├── 03-pyproject-lock-files-and-uv.md
│   ├── 04-dependency-management-and-semantic-versioning.md
│   ├── 05-ruff-formatting-and-linting.md
│   ├── 06-type-hints-and-type-checking.md
│   ├── 07-docstrings-readmes-and-user-documentation.md
│   ├── README.md
│   └── practice-questions.md
├── 07-Testing-and-Systematic-Debugging/
│   ├── 01-test-levels-unit-integration-and-end-to-end.md
│   ├── 02-pytest-assertions-fixtures-and-parametrization.md
│   ├── 03-arrange-act-assert-and-test-design.md
│   ├── 04-boundary-invalid-and-regression-tests.md
│   ├── 05-debuggers-breakpoints-and-call-stacks.md
│   ├── 06-tracebacks-logging-and-minimal-reproductions.md
│   ├── 07-mocking-and-test-doubles.md
│   ├── README.md
│   └── practice-questions.md
├── 08-Object-Oriented-Design-Data-Modelling-and-Functional-Style/
│   ├── 01-encapsulation-abstraction-and-composition.md
│   ├── 02-inheritance-and-polymorphism.md
│   ├── 03-dataclasses-and-data-models.md
│   ├── 04-class-and-instance-attributes.md
│   ├── 05-protocols-interfaces-and-dependency-inversion.md
│   ├── 06-pure-functions-immutability-and-higher-order-functions.md
│   ├── 07-separating-side-effects-from-domain-logic.md
│   ├── 08-dependency-boundaries-and-layered-design.md
│   ├── README.md
│   └── practice-questions.md
├── 09-Advanced-Production-Oriented-Python-Foundations/
│   ├── 01-iterables-iterators-and-generators.md
│   ├── 02-decorators.md
│   ├── 03-context-managers.md
│   ├── 04-generator-expressions-and-memory-tradeoffs.md
│   ├── 05-advanced-typing-essentials.md
│   ├── 06-enums-and-state-machines.md
│   ├── 07-datetime-timezones-and-timestamps.md
│   ├── 08-counter-defaultdict-and-deque.md
│   ├── 09-functools-cache-and-partial.md
│   ├── 10-python-object-model-and-garbage-collection.md
│   ├── 11-concurrency-vocabulary.md
│   ├── README.md
│   └── practice-questions.md
├── 10-Production-Habits-for-Python-Programs/
│   ├── 01-configuration-and-env-files.md
│   ├── 02-safe-and-useful-logging.md
│   ├── 03-validation-errors-and-exit-codes.md
│   ├── 04-idempotency-and-repeatable-jobs.md
│   ├── 05-safe-file-writes.md
│   ├── 06-profiling-and-measuring-before-optimizing.md
│   ├── 07-dependency-upgrades-and-supply-chain-awareness.md
│   ├── 08-readmes-runbooks-and-release-basics.md
│   ├── README.md
│   └── practice-questions.md
├── 11-Advanced-Python-Data-Model-and-Object-Design/
│   ├── 01-dunder-methods-repr-str-eq-and-hash.md
│   ├── 02-rich-comparison-and-total-ordering.md
│   ├── 03-container-protocols-getitem-len-iter-and-contains.md
│   ├── 04-operator-overloading-and-numeric-protocols.md
│   ├── 05-properties-and-computed-attributes.md
│   ├── 06-descriptors-and-attribute-lookup-order.md
│   ├── 07-slots-and-memory-layout.md
│   ├── 08-mro-super-and-cooperative-inheritance.md
│   ├── 09-mixins-and-multiple-inheritance-pitfalls.md
│   ├── 10-abstract-base-classes-and-collections-abc.md
│   ├── 11-copying-pickling-and-object-lifecycle-hooks.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Advanced-Python-Data-Model-and-Object-Design.md
├── 12-Metaprogramming-and-Dynamic-Python/
│   ├── 01-introspection-with-inspect-and-dir.md
│   ├── 02-getattr-setattr-and-dynamic-attribute-access.md
│   ├── 03-parametrized-and-class-based-decorators.md
│   ├── 04-class-decorators-and-class-factories.md
│   ├── 05-init-subclass-and-subclass-registries.md
│   ├── 06-type-and-dynamic-class-creation.md
│   ├── 07-metaclasses.md
│   ├── 08-ast-and-code-generation-basics.md
│   ├── 09-eval-exec-and-their-risks.md
│   ├── 10-designing-declarative-apis-and-mini-dsls.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Metaprogramming-and-Dynamic-Python.md
├── 13-Standard-Library-Toolkit/
│   ├── 01-itertools-and-iteration-recipes.md
│   ├── 02-operator-and-functional-composition.md
│   ├── 03-shutil-tempfile-zipfile-and-tarfile.md
│   ├── 04-subprocess-and-running-external-commands-safely.md
│   ├── 05-sqlite3-embedded-database.md
│   ├── 06-hashlib-hmac-secrets-and-uuid.md
│   ├── 07-random-and-statistics.md
│   ├── 08-tomllib-and-configparser.md
│   ├── 09-urllib-sockets-and-http-server-basics.md
│   ├── 10-weakref-contextvars-and-copy.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Standard-Library-Toolkit.md
├── 14-Bytes-Binary-Data-and-Advanced-Text-Processing/
│   ├── 01-bytes-bytearray-and-memoryview.md
│   ├── 02-struct-and-binary-file-formats.md
│   ├── 03-unicode-normalization-and-text-pitfalls.md
│   ├── 04-advanced-regular-expressions.md
│   ├── 05-difflib-textwrap-and-string-utilities.md
│   ├── 06-pickle-marshal-and-shelve-risks.md
│   ├── 07-base64-zlib-gzip-and-stream-compression.md
│   ├── 08-mmap-and-large-binary-files.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Bytes-Binary-Data-and-Advanced-Text-Processing.md
├── 15-Modern-Python-Language-Features/
│   ├── 01-structural-pattern-matching.md
│   ├── 02-assignment-expressions-and-walrus-operator.md
│   ├── 03-positional-only-keyword-only-and-star-argument-design.md
│   ├── 04-exception-chaining-notes-and-custom-hierarchies.md
│   ├── 05-exception-groups-and-except-star.md
│   ├── 06-modern-generics-typeddict-and-type-parameter-syntax.md
│   ├── 07-advanced-dataclasses-and-attrs.md
│   ├── 08-f-string-internals-and-template-strings.md
│   ├── 09-the-warnings-module-and-deprecations.md
│   ├── 10-python-version-differences-3-10-to-3-14.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Modern-Python-Language-Features.md
├── 16-Advanced-Testing-and-Test-Architecture/
│   ├── 01-coverage-line-branch-and-what-it-really-means.md
│   ├── 02-mutation-testing.md
│   ├── 03-pytest-plugins-hooks-and-conftest-architecture.md
│   ├── 04-snapshot-and-golden-file-testing.md
│   ├── 05-flaky-tests-and-test-isolation.md
│   ├── 06-testing-cli-and-subprocess-programs.md
│   ├── 07-testing-time-randomness-and-concurrency.md
│   ├── 08-test-matrices-with-tox-and-nox.md
│   ├── 09-fuzzing-basics.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Advanced-Testing-and-Test-Architecture.md
├── 17-Profiling-Memory-and-Runtime-Performance/
│   ├── 01-cprofile-pstats-and-flame-graphs.md
│   ├── 02-sampling-profilers-with-py-spy.md
│   ├── 03-timeit-and-microbenchmark-pitfalls.md
│   ├── 04-tracemalloc-and-memory-leak-hunting.md
│   ├── 05-memray-and-allocation-analysis.md
│   ├── 06-garbage-collector-tuning-and-reference-cycles.md
│   ├── 07-cpython-performance-idioms.md
│   ├── 08-ctypes-and-cffi-for-native-code.md
│   ├── 09-c-and-rust-extensions-awareness-pyo3-and-pybind11.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Profiling-Memory-and-Runtime-Performance.md
├── 18-Packaging-Distribution-and-Publishing/
│   ├── 01-build-backends-and-pep-517.md
│   ├── 02-wheels-sdists-and-binary-compatibility.md
│   ├── 03-entry-points-and-console-scripts.md
│   ├── 04-plugin-architectures-with-entry-points.md
│   ├── 05-publishing-to-testpypi-and-pypi.md
│   ├── 06-trusted-publishing-and-signed-releases.md
│   ├── 07-versioning-changelogs-and-release-automation.md
│   ├── 08-namespace-packages-and-monorepos.md
│   ├── 09-private-indexes-and-internal-packages.md
│   ├── 10-sbom-and-license-compliance.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Packaging-Distribution-and-Publishing.md
├── 19-CPython-Internals-and-Runtime-Behaviour/
│   ├── 01-source-to-bytecode-pipeline.md
│   ├── 02-reading-bytecode-with-dis.md
│   ├── 03-frames-call-stack-and-the-evaluation-loop.md
│   ├── 04-import-system-finders-loaders-and-sys-modules.md
│   ├── 05-memory-allocator-and-small-object-optimizations.md
│   ├── 06-gil-internals-and-subinterpreters.md
│   ├── 07-specializing-interpreter-and-jit.md
│   ├── 08-sys-os-and-runtime-introspection.md
│   ├── 09-post-mortem-and-remote-attach-debugging.md
│   ├── 10-sys-monitoring-and-tracing-hooks.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-CPython-Internals-and-Runtime-Behaviour.md
├── 20-Design-Patterns-and-Library-API-Design/
│   ├── 01-pythonic-design-patterns-overview.md
│   ├── 02-creational-patterns-factory-builder-and-singleton-alternatives.md
│   ├── 03-structural-patterns-adapter-facade-and-proxy.md
│   ├── 04-behavioural-patterns-strategy-observer-and-command.md
│   ├── 05-plugin-and-registry-patterns.md
│   ├── 06-designing-public-apis.md
│   ├── 07-backward-compatibility-and-deprecation-policy.md
│   ├── 08-error-hierarchies-for-libraries.md
│   ├── 09-sans-io-and-testable-library-design.md
│   ├── 10-anti-patterns-and-refactoring-to-patterns.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Design-Patterns-and-Library-API-Design.md
├── 21-Data-Visualization-and-Notebook-Workflows/
│   ├── 01-matplotlib-figure-and-axes-model.md
│   ├── 02-choosing-the-right-chart.md
│   ├── 03-seaborn-and-plotly.md
│   ├── 04-jupyter-notebook-workflows.md
│   ├── 05-reproducible-notebooks-with-papermill-and-nbstripout.md
│   ├── 06-figures-for-reports-and-dashboards.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Data-Visualization-and-Notebook-Workflows.md
├── 22-Secure-Python-Coding/
│   ├── 01-untrusted-input-and-injection-risks.md
│   ├── 02-unsafe-deserialization.md
│   ├── 03-path-traversal-and-safe-file-handling.md
│   ├── 04-shell-and-subprocess-injection.md
│   ├── 05-secrets-tokens-and-cryptography-basics.md
│   ├── 06-ssrf-and-safe-http-clients.md
│   ├── 07-static-analysis-with-bandit-and-pip-audit.md
│   ├── 08-threat-modelling-small-python-services.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Secure-Python-Coding.md
├── 23-Code-Reading-Refactoring-and-Code-Review/
│   ├── 01-reading-unfamiliar-codebases.md
│   ├── 02-characterization-tests-for-legacy-code.md
│   ├── 03-refactoring-catalogue.md
│   ├── 04-code-smells-and-technical-debt.md
│   ├── 05-writing-and-receiving-code-review.md
│   ├── 06-git-blame-bisect-and-history-archaeology.md
│   ├── 07-contributing-to-open-source-python-projects.md
│   ├── 08-reading-cpython-and-library-source.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Code-Reading-Refactoring-and-Code-Review.md
├── 24-Functions-and-OOP-Gap-Lessons/
│   ├── 01-first-class-functions-and-callables.md
│   ├── 02-lambda-expressions-and-when-not-to-use-them.md
│   ├── 03-closures-and-captured-variables.md
│   ├── 04-nonlocal-and-late-binding-pitfalls.md
│   ├── 05-map-filter-reduce-and-sorting-with-key-functions.md
│   ├── 06-callable-objects-with-call.md
│   ├── 07-function-design-review-and-refactoring-checklist.md
│   ├── 08-classes-and-objects-from-first-principles.md
│   ├── 09-init-new-and-object-construction.md
│   ├── 10-inheritance-and-super-constructor-chaining.md
│   ├── 11-class-design-review-and-refactoring-checklist.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Functions-and-OOP-Gap-Lessons.md
└── README.md
```

## Stage 2 — Python for Data Engineering_1

```text
Stage 2 — Python for Data Engineering_1/
├── 00-Stage-2-Overview/
│   ├── Projects/
│   │   ├── 01-api-to-warehouse-incremental-ingestion.md
│   │   ├── 02-cdc-replication-postgres-to-lakehouse.md
│   │   ├── 03-orchestrated-elt-with-airflow-and-dbt.md
│   │   ├── 04-lakehouse-medallion-pipeline-with-pyspark-and-delta.md
│   │   ├── 05-real-time-kafka-streaming-pipeline.md
│   │   ├── 06-data-quality-and-observability-platform.md
│   │   ├── 07-capstone-end-to-end-data-platform.md
│   │   └── README.md
│   └── README.md
├── 01-Data-Engineering-Foundations-and-Pipeline-Thinking/
│   ├── 01-what-data-engineers-build.md
│   ├── 02-data-lifecycle-from-sources-to-consumers.md
│   ├── 03-batch-micro-batch-and-streaming.md
│   ├── 04-etl-elt-and-reverse-etl.md
│   ├── 05-oltp-vs-olap-workloads.md
│   ├── 06-warehouse-lake-and-lakehouse-architectures.md
│   ├── 07-medallion-bronze-silver-gold-layers.md
│   ├── 08-slas-freshness-latency-and-data-consumers.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Data-Engineering-Foundations-and-Pipeline-Thinking.md
├── 02-Numerical-Computing-with-NumPy/
│   ├── 01-ndarray-dtypes-and-memory-layout.md
│   ├── 02-vectorization-and-broadcasting.md
│   ├── 03-indexing-boolean-masks-and-fancy-indexing.md
│   ├── 04-aggregations-and-axis-semantics.md
│   ├── 05-nan-missing-values-and-sentinels.md
│   ├── 06-views-copies-and-memory-efficiency.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Numerical-Computing-with-NumPy.md
├── 03-DataFrames-with-pandas/
│   ├── 01-series-dataframe-and-index.md
│   ├── 02-reading-and-writing-data-sources.md
│   ├── 03-selection-with-loc-iloc-and-query.md
│   ├── 04-dtypes-nullable-types-and-categoricals.md
│   ├── 05-cleaning-missing-duplicates-and-outliers.md
│   ├── 06-groupby-aggregate-transform-and-apply.md
│   ├── 07-merge-join-concat-and-join-cardinality.md
│   ├── 08-reshaping-pivot-melt-stack-and-unstack.md
│   ├── 09-time-series-resampling-and-rolling-windows.md
│   ├── 10-string-and-datetime-accessors.md
│   ├── 11-method-chaining-and-pipe.md
│   ├── 12-copy-on-write-and-chained-assignment-pitfalls.md
│   ├── 13-chunked-processing-and-memory-reduction.md
│   ├── README.md
│   ├── interview-practice.md
│   ├── practice-questions.md
│   └── roadmap-DataFrames-with-pandas.md
├── 04-Columnar-Engines-Arrow-Polars-and-DuckDB/
│   ├── 01-apache-arrow-columnar-memory-model.md
│   ├── 02-polars-expressions-and-contexts.md
│   ├── 03-polars-lazy-api-and-query-optimization.md
│   ├── 04-polars-streaming-for-larger-than-memory-data.md
│   ├── 05-duckdb-in-process-analytics.md
│   ├── 06-querying-files-and-object-storage-with-duckdb.md
│   ├── 07-zero-copy-interop-between-pandas-polars-duckdb-and-arrow.md
│   ├── 08-choosing-a-dataframe-engine.md
│   ├── 09-mini-project.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Columnar-Engines-Arrow-Polars-and-DuckDB.md
├── 05-Data-Formats-Compression-and-File-Layout/
│   ├── 01-row-oriented-vs-columnar-storage.md
│   ├── 02-parquet-internals-row-groups-pages-and-statistics.md
│   ├── 03-reading-and-writing-parquet-with-pyarrow.md
│   ├── 04-avro-files-and-row-oriented-formats.md
│   ├── 05-orc-and-format-selection-tradeoffs.md
│   ├── 06-nested-semi-structured-data-flatten-and-explode.md
│   ├── 07-compression-codecs-snappy-gzip-zstd-lz4.md
│   ├── 08-partitioning-and-hive-style-directory-layouts.md
│   ├── 09-small-files-problem-and-target-file-sizing.md
│   ├── 10-excel-xml-and-fixed-width-legacy-formats.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Data-Formats-Compression-and-File-Layout.md
├── 06-SQL-for-Data-Engineers/
│   ├── 01-select-filter-sort-and-null-semantics.md
│   ├── 02-joins-and-join-explosion.md
│   ├── 03-aggregation-group-by-and-having.md
│   ├── 04-subqueries-and-ctes.md
│   ├── 05-window-functions-ranking-running-totals-and-lag-lead.md
│   ├── 06-set-operations-and-deduplication-patterns.md
│   ├── 07-ddl-constraints-and-column-data-types.md
│   ├── 08-indexes-and-reading-explain-plans.md
│   ├── 09-transactions-isolation-levels-and-locking.md
│   ├── 10-merge-upsert-and-scd-implementation-in-sql.md
│   ├── README.md
│   ├── interview-practice.md
│   ├── practice-questions.md
│   └── roadmap-SQL-for-Data-Engineers.md
├── 07-Python-Database-Connectivity/
│   ├── 01-db-api-pep-249-connections-and-cursors.md
│   ├── 02-postgresql-from-python-with-psycopg.md
│   ├── 03-parameterized-queries-and-sql-injection.md
│   ├── 04-transaction-control-from-python.md
│   ├── 05-connection-pooling.md
│   ├── 06-sqlalchemy-core-engine-and-metadata.md
│   ├── 07-sqlalchemy-orm-when-to-use-and-avoid.md
│   ├── 08-schema-migrations-with-alembic.md
│   ├── 09-bulk-loading-with-copy-and-executemany.md
│   ├── 10-server-side-cursors-and-streaming-large-results.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Python-Database-Connectivity.md
├── 08-Data-Modelling-for-Analytics/
│   ├── 01-normalization-and-denormalization.md
│   ├── 02-dimensional-modelling-facts-and-dimensions.md
│   ├── 03-star-and-snowflake-schemas.md
│   ├── 04-grain-natural-keys-and-surrogate-keys.md
│   ├── 05-slowly-changing-dimension-types.md
│   ├── 06-data-vault-hubs-links-and-satellites.md
│   ├── 07-one-big-table-and-wide-denormalized-models.md
│   ├── 08-modelling-event-and-clickstream-data.md
│   ├── README.md
│   ├── interview-practice.md
│   ├── practice-questions.md
│   └── roadmap-Data-Modelling-for-Analytics.md
├── 09-Data-Ingestion-and-Extraction-Patterns/
│   ├── 01-http-fundamentals-for-data-extraction.md
│   ├── 02-httpx-and-requests-sessions-and-timeouts.md
│   ├── 03-api-authentication-keys-oauth2-and-token-refresh.md
│   ├── 04-pagination-offset-cursor-and-keyset.md
│   ├── 05-rate-limits-http-429-and-retry-after.md
│   ├── 06-full-vs-incremental-extraction-and-watermarks.md
│   ├── 07-change-data-capture-concepts.md
│   ├── 08-webhooks-and-push-based-ingestion.md
│   ├── 09-html-parsing-and-responsible-scraping.md
│   ├── 10-sftp-and-file-drop-ingestion.md
│   ├── 11-ingestion-frameworks-dlt-and-managed-connectors.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Data-Ingestion-and-Extraction-Patterns.md
├── 10-Concurrency-and-Parallelism-in-Practice/
│   ├── 01-threading-and-threadpoolexecutor.md
│   ├── 02-multiprocessing-and-processpoolexecutor.md
│   ├── 03-asyncio-event-loop-coroutines-and-tasks.md
│   ├── 04-taskgroups-cancellation-and-timeouts.md
│   ├── 05-async-http-extraction-with-httpx.md
│   ├── 06-semaphores-and-bounded-concurrency.md
│   ├── 07-queues-and-producer-consumer-pipelines.md
│   ├── 08-race-conditions-locks-and-thread-safety.md
│   ├── 09-gil-free-threaded-python-and-choosing-a-model.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Concurrency-and-Parallelism-in-Practice.md
├── 11-Data-Validation-Contracts-and-Quality/
│   ├── 01-data-quality-dimensions.md
│   ├── 02-pydantic-models-validators-and-serialization.md
│   ├── 03-dataframe-schema-validation-with-pandera.md
│   ├── 04-declarative-checks-with-great-expectations-and-soda.md
│   ├── 05-data-contracts-and-producer-ownership.md
│   ├── 06-schema-evolution-and-compatibility-rules.md
│   ├── 07-quarantine-dead-letter-and-bad-record-handling.md
│   ├── 08-volume-freshness-and-distribution-anomaly-checks.md
│   ├── 09-reconciliation-and-row-count-audits.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Data-Validation-Contracts-and-Quality.md
├── 12-Transformation-Patterns-and-Pipeline-Design/
│   ├── 01-structuring-extract-transform-load-code.md
│   ├── 02-deduplication-and-merge-based-loads.md
│   ├── 03-incremental-processing-and-backfills.md
│   ├── 04-late-arriving-data-and-reprocessing-windows.md
│   ├── 05-hashing-for-surrogate-keys-and-change-detection.md
│   ├── 06-lookups-enrichment-and-reference-data.md
│   ├── 07-metadata-and-config-driven-pipelines.md
│   ├── 08-checkpoints-pipeline-state-and-resumability.md
│   ├── 09-dbt-fundamentals-models-tests-and-python-models.md
│   ├── README.md
│   ├── interview-practice.md
│   ├── practice-questions.md
│   └── roadmap-Transformation-Patterns-and-Pipeline-Design.md
├── 13-Orchestration-and-Workflow-Management/
│   ├── 01-dags-dependencies-and-scheduling-concepts.md
│   ├── 02-limits-of-cron-and-why-orchestrators-exist.md
│   ├── 03-apache-airflow-architecture.md
│   ├── 04-airflow-dags-operators-and-taskflow-api.md
│   ├── 05-airflow-connections-variables-hooks-and-xcoms.md
│   ├── 06-sensors-deferrable-operators-and-data-aware-scheduling.md
│   ├── 07-task-retries-slas-and-failure-callbacks.md
│   ├── 08-backfills-catchup-and-partitioned-runs.md
│   ├── 09-dagster-software-defined-assets.md
│   ├── 10-prefect-flows-and-tasks.md
│   ├── 11-testing-and-validating-dags.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Orchestration-and-Workflow-Management.md
├── 14-Distributed-Processing-with-PySpark/
│   ├── 01-distributed-computing-driver-executors-and-cluster-managers.md
│   ├── 02-sparksession-configuration-and-deploy-modes.md
│   ├── 03-rdds-vs-dataframes.md
│   ├── 04-transformations-actions-and-lazy-evaluation.md
│   ├── 05-dataframe-api-select-filter-and-withcolumn.md
│   ├── 06-spark-sql-and-temporary-views.md
│   ├── 07-joins-shuffle-and-broadcast-joins.md
│   ├── 08-partitioning-repartition-and-coalesce.md
│   ├── 09-data-skew-and-salting.md
│   ├── 10-caching-and-persistence-levels.md
│   ├── 11-python-udfs-vs-pandas-udfs-vs-built-ins.md
│   ├── 12-catalyst-optimizer-and-explain-plans.md
│   ├── 13-adaptive-query-execution.md
│   ├── 14-data-sources-save-modes-and-bucketing.md
│   ├── 15-spark-ui-and-debugging-slow-jobs.md
│   ├── 16-testing-pyspark-code.md
│   ├── README.md
│   ├── interview-practice.md
│   ├── practice-questions.md
│   └── roadmap-Distributed-Processing-with-PySpark.md
├── 15-Lakehouse-Table-Formats/
│   ├── 01-why-open-table-formats-exist.md
│   ├── 02-delta-lake-transaction-log.md
│   ├── 03-apache-iceberg-snapshots-and-manifests.md
│   ├── 04-apache-hudi-overview.md
│   ├── 05-acid-merge-update-and-delete-on-data-lakes.md
│   ├── 06-time-travel-and-table-versioning.md
│   ├── 07-compaction-z-ordering-and-liquid-clustering.md
│   ├── 08-vacuum-retention-and-table-maintenance.md
│   ├── 09-catalogs-hive-metastore-glue-unity-and-polaris.md
│   ├── README.md
│   ├── interview-practice.md
│   └── roadmap-Lakehouse-Table-Formats.md
├── 16-Streaming-and-Event-Driven-Data/
│   ├── 01-event-streams-vs-message-queues.md
│   ├── 02-kafka-topics-partitions-offsets-and-replication.md
│   ├── 03-kafka-producers-in-python.md
│   ├── 04-kafka-consumers-and-consumer-groups.md
│   ├── 05-delivery-semantics-at-most-at-least-and-exactly-once.md
│   ├── 06-protobuf-and-schema-registry.md
│   ├── 07-event-time-processing-time-and-watermarks.md
│   ├── 08-tumbling-sliding-and-session-windows.md
│   ├── 09-stateful-stream-processing.md
│   ├── 10-spark-structured-streaming.md
│   ├── 11-apache-flink-and-pyflink-overview.md
│   ├── 12-debezium-cdc-streams-into-kafka.md
│   ├── 13-backpressure-and-consumer-lag.md
│   ├── README.md
│   ├── interview-practice.md
│   ├── practice-questions.md
│   └── roadmap-Streaming-and-Event-Driven-Data.md
├── 17-Cloud-Storage-and-Cloud-Data-Platforms/
│   ├── 01-object-storage-s3-gcs-and-adls.md
│   ├── 02-boto3-and-s3-operations.md
│   ├── 03-fsspec-and-cloud-agnostic-file-access.md
│   ├── 04-iam-roles-and-least-privilege-for-pipelines.md
│   ├── 05-cloud-warehouses-snowflake-bigquery-and-redshift.md
│   ├── 06-python-warehouse-connectors-and-bulk-loads.md
│   ├── 07-serverless-data-processing.md
│   ├── 08-managed-spark-databricks-emr-and-dataproc.md
│   ├── 09-storage-classes-and-lifecycle-policies.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Cloud-Storage-and-Cloud-Data-Platforms.md
├── 18-Containers-Infrastructure-and-CI-CD-for-Data/
│   ├── 01-docker-images-for-python-pipelines.md
│   ├── 02-docker-compose-for-local-data-stacks.md
│   ├── 03-kubernetes-concepts-for-data-workloads.md
│   ├── 04-terraform-basics-for-data-infrastructure.md
│   ├── 05-ci-pipelines-for-data-projects.md
│   ├── 06-environment-promotion-dev-staging-and-prod.md
│   ├── 07-cloud-secrets-managers.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Containers-Infrastructure-and-CI-CD-for-Data.md
├── 19-Testing-Data-Pipelines/
│   ├── 01-testing-transformations-with-fixture-dataframes.md
│   ├── 02-dataframe-equality-and-tolerance-assertions.md
│   ├── 03-integration-tests-with-testcontainers.md
│   ├── 04-property-based-testing-with-hypothesis.md
│   ├── 05-synthetic-and-sampled-test-data.md
│   ├── 06-schema-and-contract-regression-tests.md
│   ├── 07-end-to-end-pipeline-smoke-tests.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Testing-Data-Pipelines.md
├── 20-Observability-Lineage-Governance-and-Security/
│   ├── 01-pipeline-metrics-and-run-metadata.md
│   ├── 02-opentelemetry-tracing-for-pipelines.md
│   ├── 03-alerting-and-on-call-for-data.md
│   ├── 04-data-lineage-with-openlineage.md
│   ├── 05-data-catalogs-and-metadata-management.md
│   ├── 06-pii-detection-masking-and-tokenization.md
│   ├── 07-encryption-at-rest-and-in-transit.md
│   ├── 08-row-and-column-level-access-control.md
│   ├── 09-retention-deletion-and-gdpr-compliance.md
│   ├── 10-data-incident-response-and-postmortems.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Observability-Lineage-Governance-and-Security.md
├── 21-Performance-Scaling-and-Cost-Optimization/
│   ├── 01-estimating-data-size-and-memory-footprint.md
│   ├── 02-predicate-pushdown-and-projection-pruning.md
│   ├── 03-parallel-dataframes-with-dask.md
│   ├── 04-ray-data-overview.md
│   ├── 05-numba-and-cython-for-hot-loops.md
│   ├── 06-benchmarking-pipelines.md
│   ├── 07-compute-cost-optimization.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Performance-Scaling-and-Cost-Optimization.md
└── 22-Serving-Data-for-Analytics-ML-and-AI/
    ├── 01-fastapi-data-services.md
    ├── 02-serving-aggregates-and-caching-layers.md
    ├── 03-semantic-layers-and-metric-definitions.md
    ├── 04-feature-stores-and-ml-handoff.md
    ├── 05-embedding-and-vector-data-pipelines.md
    ├── README.md
    ├── practice-questions.md
    └── roadmap-Serving-Data-for-Analytics-ML-and-AI.md
```

## Stage 2B — Python for Data Engineering_2

```text
Stage 2B — Python for Data Engineering_2/
├── 00-Gap-Modules-Overview/
│   ├── Projects/
│   │   ├── 01-dockerized-local-data-lab.md
│   │   ├── 02-remote-server-pipeline-operations.md
│   │   ├── 03-aws-serverless-lakehouse.md
│   │   ├── 04-databricks-lakehouse-platform.md
│   │   ├── 05-system-design-interview-portfolio.md
│   │   └── README.md
│   └── README.md
├── 01-Docker-Essentials-for-Data-Labs/
│   ├── 01-containers-images-and-registries-for-users.md
│   ├── 02-running-databases-and-services-in-containers.md
│   ├── 03-ports-networks-and-service-discovery.md
│   ├── 04-volumes-bind-mounts-and-data-persistence.md
│   ├── 05-environment-variables-and-configuration-for-containers.md
│   ├── 06-logs-exec-and-troubleshooting-containers.md
│   ├── 07-using-docker-compose-stacks.md
│   ├── 08-resource-limits-and-laptop-capacity.md
│   ├── 09-cleanup-disk-usage-and-housekeeping.md
│   ├── 10-docker-desktop-wsl2-and-platform-differences.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Docker-Essentials-for-Data-Labs.md
├── 02-Linux-and-Shell-for-Data-Servers/
│   ├── 01-remote-servers-ssh-config-keys-and-jump-hosts.md
│   ├── 02-ssh-tunnels-and-port-forwarding-for-data-tools.md
│   ├── 03-tmux-and-long-running-sessions.md
│   ├── 04-file-transfer-at-scale-scp-rsync-and-rclone.md
│   ├── 05-systemd-services-timers-and-journalctl.md
│   ├── 06-server-resource-monitoring-cpu-memory-disk-and-io.md
│   ├── 07-disk-space-inodes-and-large-file-management.md
│   ├── 08-command-line-data-tools-jq-csvkit-miller-and-duckdb-cli.md
│   ├── 09-log-investigation-on-servers.md
│   ├── 10-users-sudo-packages-and-server-hygiene.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Linux-and-Shell-for-Data-Servers.md
├── 03-AWS-Data-Engineering-Deep-Dive/
│   ├── 01-aws-data-services-landscape-and-reference-architectures.md
│   ├── 02-s3-tables-access-points-and-batch-operations.md
│   ├── 03-glue-data-catalog-crawlers-and-schema-management.md
│   ├── 04-glue-etl-jobs-and-glue-data-quality.md
│   ├── 05-athena-advanced-partition-projection-ctas-and-iceberg.md
│   ├── 06-lake-formation-permissions-and-governance.md
│   ├── 07-redshift-deep-dive-serverless-spectrum-and-data-sharing.md
│   ├── 08-kinesis-data-streams-firehose-and-msk.md
│   ├── 09-emr-on-ec2-eks-and-serverless.md
│   ├── 10-step-functions-eventbridge-and-mwaa-orchestration.md
│   ├── 11-dms-and-zero-etl-integrations.md
│   ├── 12-cloudwatch-cloudtrail-and-cost-explorer-for-data.md
│   ├── 13-kms-vpc-endpoints-and-private-networking-for-data.md
│   ├── 14-sagemaker-unified-studio-and-datazone-overview.md
│   ├── README.md
│   ├── interview-practice.md
│   ├── practice-questions.md
│   └── roadmap-AWS-Data-Engineering-Deep-Dive.md
├── 04-Databricks-Lakehouse-Platform-Deep-Dive/
│   ├── 01-databricks-architecture-workspaces-and-planes.md
│   ├── 02-compute-clusters-serverless-and-sql-warehouses.md
│   ├── 03-notebooks-git-folders-and-project-structure.md
│   ├── 04-unity-catalog-deep-dive-volumes-locations-and-permissions.md
│   ├── 05-auto-loader-and-incremental-file-ingestion.md
│   ├── 06-lakeflow-connect-managed-ingestion.md
│   ├── 07-lakeflow-declarative-pipelines-and-expectations.md
│   ├── 08-lakeflow-jobs-orchestration.md
│   ├── 09-photon-performance-and-predictive-optimization.md
│   ├── 10-databricks-sql-ai-bi-dashboards-and-genie.md
│   ├── 11-delta-sharing-and-marketplace.md
│   ├── 12-databricks-asset-bundles-and-ci-cd.md
│   ├── 13-cost-management-and-system-tables.md
│   ├── 14-mlflow-and-feature-engineering-handoff.md
│   ├── README.md
│   ├── interview-practice.md
│   ├── practice-questions.md
│   └── roadmap-Databricks-Lakehouse-Platform-Deep-Dive.md
├── 05-Data-Engineering-System-Design-Interviews/
│   ├── 01-system-design-interview-format-and-evaluation-rubric.md
│   ├── 02-requirements-clarification-and-scoping.md
│   ├── 03-back-of-the-envelope-estimation-for-data-systems.md
│   ├── 04-a-reusable-design-framework-for-data-platforms.md
│   ├── 05-trade-off-catalogue-batch-streaming-storage-and-engines.md
│   ├── 06-diagramming-and-communicating-designs.md
│   ├── 07-design-case-batch-analytics-platform.md
│   ├── 08-design-case-real-time-clickstream-analytics.md
│   ├── 09-design-case-cdc-replication-to-lakehouse.md
│   ├── 10-design-case-ml-feature-platform.md
│   ├── 11-design-case-log-and-metrics-analytics-at-scale.md
│   ├── 12-design-case-ad-attribution-and-deduplication.md
│   ├── 13-design-case-iot-telemetry-ingestion.md
│   ├── 14-design-case-gdpr-deletion-across-a-platform.md
│   ├── 15-design-case-rag-and-vector-data-platform.md
│   ├── 16-failure-scenarios-and-deep-dive-follow-up-questions.md
│   ├── 17-behavioural-interviews-for-data-engineers.md
│   ├── 18-take-home-assignments-and-live-pipeline-coding.md
│   ├── 19-mock-interview-plans-and-self-review.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Data-Engineering-System-Design-Interviews.md
└── README.md
```

## Stage 2C — Data Engineering_3

```text
Stage 2C — Data Engineering_3/
├── 01-NoSQL-and-Distributed-Databases/
│   ├── 01-nosql-families-and-when-to-use-them.md
│   ├── 02-cap-theorem-and-consistency-models.md
│   ├── 03-mongodb-document-modelling-and-aggregation.md
│   ├── 04-cassandra-wide-column-partitioning-and-tombstones.md
│   ├── 05-dynamodb-single-table-design-and-streams.md
│   ├── 06-redis-caching-and-data-structures.md
│   ├── 07-elasticsearch-and-opensearch-for-search-and-logs.md
│   ├── 08-graph-databases-neo4j-and-cypher.md
│   ├── 09-change-streams-and-nosql-to-lakehouse-ingestion.md
│   └── roadmap-NoSQL-and-Distributed-Databases.md
├── 02-Hadoop-Ecosystem-and-Legacy-Big-Data/
│   ├── 01-hdfs-architecture-namenode-datanodes-and-replication.md
│   ├── 02-yarn-resource-management.md
│   ├── 03-mapreduce-model-and-why-spark-replaced-it.md
│   ├── 04-hive-metastore-and-hiveql.md
│   ├── 05-hbase-and-wide-column-on-hdfs.md
│   ├── 06-sqoop-flume-and-oozie-legacy-tooling.md
│   ├── 07-migrating-hadoop-workloads-to-cloud-lakehouse.md
│   └── roadmap-Hadoop-Ecosystem-and-Legacy-Big-Data.md
├── 03-Snowflake-Deep-Dive/
│   ├── 01-snowflake-architecture-storage-compute-and-services.md
│   ├── 02-virtual-warehouses-sizing-and-scaling.md
│   ├── 03-micro-partitions-clustering-and-pruning.md
│   ├── 04-stages-copy-into-and-snowpipe.md
│   ├── 05-streams-tasks-and-dynamic-tables.md
│   ├── 06-snowpark-python-and-udfs.md
│   ├── 07-time-travel-cloning-and-zero-copy.md
│   ├── 08-rbac-masking-policies-and-row-access.md
│   ├── 09-data-sharing-and-marketplace.md
│   ├── 10-cost-monitoring-and-resource-monitors.md
│   └── roadmap-Snowflake-Deep-Dive.md
├── 04-Google-Cloud-BigQuery-and-GCP-Data-Engineering/
│   ├── 01-gcp-data-services-landscape.md
│   ├── 02-bigquery-architecture-slots-and-storage.md
│   ├── 03-partitioning-clustering-and-query-cost-control.md
│   ├── 04-bigquery-loading-streaming-and-external-tables.md
│   ├── 05-bigquery-ml-and-scheduled-queries.md
│   ├── 06-pubsub-and-dataflow-apache-beam.md
│   ├── 07-dataproc-and-dataproc-serverless.md
│   ├── 08-cloud-composer-and-workflows.md
│   ├── 09-dataplex-iam-and-governance.md
│   └── roadmap-Google-Cloud-BigQuery-and-GCP-Data-Engineering.md
├── 05-Azure-Data-Engineering-and-Microsoft-Fabric/
│   ├── 01-azure-data-services-landscape.md
│   ├── 02-adls-gen2-and-blob-storage.md
│   ├── 03-azure-data-factory-pipelines-and-mapping-data-flows.md
│   ├── 04-synapse-analytics-dedicated-and-serverless-pools.md
│   ├── 05-event-hubs-and-stream-analytics.md
│   ├── 06-microsoft-fabric-lakehouse-and-onelake.md
│   ├── 07-azure-databricks-integration.md
│   ├── 08-entra-id-rbac-and-key-vault.md
│   ├── 09-purview-governance-and-lineage.md
│   └── roadmap-Azure-Data-Engineering-and-Microsoft-Fabric.md
├── 06-dbt-and-Analytics-Engineering/
│   ├── 01-dbt-project-structure-and-materializations.md
│   ├── 02-sources-seeds-snapshots-and-incremental-models.md
│   ├── 03-jinja-macros-and-packages.md
│   ├── 04-tests-contracts-and-model-governance.md
│   ├── 05-documentation-lineage-and-exposures.md
│   ├── 06-dbt-performance-and-slim-ci.md
│   ├── 07-semantic-layer-and-metricflow.md
│   ├── 08-deploying-dbt-with-airflow-and-dbt-cloud.md
│   └── roadmap-dbt-and-Analytics-Engineering.md
├── 07-Real-Time-OLAP-and-Query-Engines/
│   ├── 01-clickhouse-architecture-and-mergetree.md
│   ├── 02-apache-druid-and-apache-pinot-overview.md
│   ├── 03-trino-and-presto-federated-queries.md
│   ├── 04-starrocks-and-doris-overview.md
│   ├── 05-materialized-views-and-pre-aggregation.md
│   ├── 06-choosing-an-olap-engine-for-low-latency-dashboards.md
│   └── roadmap-Real-Time-OLAP-and-Query-Engines.md
├── 08-Data-Platform-Architecture-and-Data-Products/
│   ├── 03_data_products_and_slas/
│   │   ├── data/
│   │   │   ├── consumer_list.json
│   │   │   ├── orders_snapshot.json
│   │   │   ├── schema_v1.json
│   │   │   ├── schema_v2_breaking.json
│   │   │   └── slo_history.json
│   │   ├── reports/
│   │   │   ├── notification_outbox.json
│   │   │   └── slo_report.json
│   │   ├── specs/
│   │   │   ├── customer_360.yaml
│   │   │   └── orders.yaml
│   │   ├── tests/
│   │   │   └── test_product_lab.py
│   │   ├── CONSUMER_ONBOARDING.md
│   │   ├── README.md
│   │   ├── product_lab.py
│   │   └── pyproject.toml
│   ├── 04-master-data-management-and-entity-resolution/
│   │   ├── data/
│   │   │   ├── incremental_records.json
│   │   │   └── source_records.json
│   │   ├── reports/
│   │   │   └── run_report.json
│   │   ├── tests/
│   │   │   └── test_resolver.py
│   │   ├── README.md
│   │   ├── pyproject.toml
│   │   ├── resolver.py
│   │   ├── run_lab.py
│   │   └── splink_runner.py
│   ├── 05-metadata-driven-platform-design/
│   │   ├── 05_metadata_platform/
│   │   │   ├── configs/
│   │   │   │   ├── customers.yaml
│   │   │   │   ├── orders.yaml
│   │   │   │   └── product_catalog.yaml
│   │   │   ├── data/
│   │   │   │   ├── data_customers.csv
│   │   │   │   ├── data_orders.csv
│   │   │   │   └── data_products.csv
│   │   │   ├── fixtures/
│   │   │   │   ├── expected_crm_plan_contract.json
│   │   │   │   └── legacy_customers_v1.yaml
│   │   │   ├── generated/
│   │   │   │   ├── commerce_orders.plan.json
│   │   │   │   ├── crm_customers.plan.json
│   │   │   │   ├── erp_product_catalog.plan.json
│   │   │   │   ├── governance_policies.json
│   │   │   │   ├── stg_commerce_orders.sql
│   │   │   │   ├── stg_crm_customers.sql
│   │   │   │   └── stg_erp_product_catalog.sql
│   │   │   ├── reports/
│   │   │   │   ├── commerce_orders.openlineage.json
│   │   │   │   ├── crm_customers.openlineage.json
│   │   │   │   ├── erp_product_catalog.openlineage.json
│   │   │   │   └── run_history.jsonl
│   │   │   ├── schema/
│   │   │   │   ├── generate_json_schema.py
│   │   │   │   └── metadata-v2.schema.json
│   │   │   ├── templates/
│   │   │   │   └── staging_model.sql.j2
│   │   │   ├── tests/
│   │   │   │   └── test_platform.py
│   │   │   ├── README.md
│   │   │   ├── metadata_platform.py
│   │   │   ├── pyproject.toml
│   │   │   └── run_lab.py
│   │   ├── configs/
│   │   │   ├── customers.yaml
│   │   │   ├── orders.yaml
│   │   │   └── product_catalog.yaml
│   │   ├── data/
│   │   │   ├── data_customers.csv
│   │   │   ├── data_orders.csv
│   │   │   └── data_products.csv
│   │   ├── fixtures/
│   │   │   ├── expected_crm_plan_contract.json
│   │   │   └── legacy_customers_v1.yaml
│   │   ├── generated/
│   │   │   ├── commerce_orders.plan.json
│   │   │   ├── crm_customers.plan.json
│   │   │   ├── erp_product_catalog.plan.json
│   │   │   ├── generated_manifest.json
│   │   │   ├── governance_policies.json
│   │   │   ├── sources.yml
│   │   │   ├── stg_commerce_orders.sql
│   │   │   ├── stg_crm_customers.sql
│   │   │   └── stg_erp_product_catalog.sql
│   │   ├── reports/
│   │   │   ├── commerce_orders.openlineage.json
│   │   │   ├── crm_customers.openlineage.json
│   │   │   ├── erp_product_catalog.openlineage.json
│   │   │   └── run_history.jsonl
│   │   ├── schema/
│   │   │   ├── generate_json_schema.py
│   │   │   └── metadata-v3.schema.json
│   │   ├── templates/
│   │   │   └── staging_model.sql.j2
│   │   ├── tests/
│   │   │   └── test_platform.py
│   │   ├── README.md
│   │   ├── metadata_platform.py
│   │   ├── pyproject.toml
│   │   └── run_lab.py
│   ├── 06-multi-tenant-and-multi-region-data-platforms/
│   │   └── experiments/
│   │       └── 06_multi_tenant/
│   │           ├── docs/
│   │           │   ├── architecture.md
│   │           │   └── offboarding.md
│   │           ├── outputs/
│   │           │   ├── 11111111-1111-1111-1111-111111111111-export-manifest.json
│   │           │   └── audit.jsonl
│   │           ├── postgres/
│   │           │   ├── bootstrap.sql
│   │           │   └── silo_variant.sql
│   │           ├── tests/
│   │           │   ├── test_postgres_rls.py
│   │           │   └── test_simulation.py
│   │           ├── README.md
│   │           ├── docker-compose.yml
│   │           ├── pyproject.toml
│   │           ├── run_lab.py
│   │           └── tenancy_lab.py
│   ├── 07-build-vs-buy-and-vendor-selection/
│   │   └── experiments/
│   │       └── 07_build_vs_buy/
│   │           ├── docs/
│   │           │   └── adr/
│   │           │       └── ADR-007.md
│   │           ├── outputs/
│   │           │   ├── scorecard_results.csv
│   │           │   └── tco_results.csv
│   │           ├── tests/
│   │           │   └── test_model.py
│   │           ├── README.md
│   │           ├── assumptions.json
│   │           ├── model.py
│   │           ├── poc_plan.md
│   │           └── scorecard.json
│   ├── 01-lambda-vs-kappa-architecture.md
│   ├── 02-data-mesh-principles-and-domain-ownership.md
│   ├── 03-data-products-and-slas.md
│   ├── 04-master-data-management-and-entity-resolution.md
│   ├── 05-metadata-driven-platform-design.md
│   ├── 06-multi-tenant-and-multi-region-data-platforms.md
│   ├── 07-build-vs-buy-and-vendor-selection.md
│   └── roadmap-Data-Platform-Architecture-and-Data-Products.md
├── 09-Analytics-Foundations-for-Data-Engineers/
│   ├── 01-descriptive-statistics-and-distributions-at-scale.md
│   ├── 02-sampling-and-approximate-algorithms-hyperloglog-and-sketches.md
│   ├── 03-hypothesis-testing-and-confidence-intervals.md
│   ├── 04-ab-testing-and-experiment-data-pipelines.md
│   ├── 05-cohort-funnel-and-retention-analysis.md
│   ├── 06-time-series-analysis-and-forecasting-basics.md
│   ├── 07-bi-tools-and-dashboard-design-metabase-superset-tableau.md
│   ├── 08-data-visualization-with-matplotlib-plotly-and-altair.md
│   ├── 09-data-storytelling-and-stakeholder-communication.md
│   └── roadmap-Analytics-Foundations-for-Data-Engineers.md
├── 10-Big-Data-ML-and-MLOps-Handoff/
│   ├── 01-distributed-ml-with-spark-mllib.md
│   ├── 02-feature-engineering-at-scale.md
│   ├── 03-training-data-pipelines-and-dataset-versioning.md
│   ├── 04-model-registry-and-batch-vs-online-inference.md
│   ├── 05-data-drift-monitoring-for-ml-pipelines.md
│   └── roadmap-Big-Data-ML-and-MLOps-Handoff.md
└── README.md
```

## Stage 2D — Data Architecture

```text
Stage 2D — Data Architecture/
├── 00-Stage-2D-Overview/
│   ├── Projects/
│   │   ├── 01-enterprise-data-architecture-capstone.md
│   │   └── README.md
│   └── README.md
├── 01-Data-Architecture-Foundations-and-Principles/
│   ├── Projects/
│   │   ├── 01-current-state-data-architecture-inventory.md
│   │   └── README.md
│   ├── 01-what-data-architecture-is-and-what-data-architects-do.md
│   ├── 02-data-architecture-vs-data-engineering-and-solution-architecture.md
│   ├── 03-business-capabilities-domains-and-data-ownership.md
│   ├── 04-architecture-principles-and-quality-attributes.md
│   ├── 05-data-architecture-lifecycle-and-governance.md
│   ├── 06-enterprise-data-architecture-frameworks-and-reference-models.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Data-Architecture-Foundations-and-Principles.md
├── 02-Requirements-Constraints-and-Architecture-Decisions/
│   ├── Projects/
│   │   ├── 02-requirements-and-architecture-decision-pack.md
│   │   └── README.md
│   ├── 01-stakeholder-discovery-and-business-requirements.md
│   ├── 02-functional-and-non-functional-requirements.md
│   ├── 03-data-volume-velocity-variety-and-growth-estimation.md
│   ├── 04-latency-throughput-freshness-and-availability-targets.md
│   ├── 05-constraints-assumptions-dependencies-and-risks.md
│   ├── 06-architecture-trade-offs-and-decision-criteria.md
│   ├── 07-architecture-decision-records-adrs.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Requirements-Constraints-and-Architecture-Decisions.md
├── 03-Data-Architecture-Patterns-and-Reference-Architectures/
│   ├── Projects/
│   │   ├── 03-reference-architecture-pattern-comparison.md
│   │   └── README.md
│   ├── 01-centralized-federated-and-domain-oriented-architectures.md
│   ├── 02-data-warehouse-data-lake-and-lakehouse-patterns.md
│   ├── 03-lambda-and-kappa-architectures.md
│   ├── 04-data-mesh-principles-and-domain-data-products.md
│   ├── 05-data-fabric-and-metadata-driven-architecture.md
│   ├── 06-event-driven-and-data-sharing-patterns.md
│   ├── 07-selecting-and-combining-architecture-patterns.md
│   ├── README.md
│   └── roadmap-Data-Architecture-Patterns-and-Reference-Architectures.md
├── 04-Conceptual-Logical-and-Physical-Data-Modeling/
│   ├── Projects/
│   │   ├── 04-enterprise-conceptual-and-logical-data-model.md
│   │   └── README.md
│   ├── 01-conceptual-logical-and-physical-models.md
│   ├── 02-entities-relationships-cardinality-and-constraints.md
│   ├── 03-normalization-and-relational-modeling.md
│   ├── 04-dimensional-modeling-facts-dimensions-and-grain.md
│   ├── 05-data-vault-and-historical-modeling.md
│   ├── 06-event-modeling-and-domain-driven-design.md
│   ├── 07-schema-evolution-and-backward-compatibility.md
│   ├── 08-model-review-naming-standards-and-data-dictionaries.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Conceptual-Logical-and-Physical-Data-Modeling.md
├── 05-Database-and-Storage-Architecture/
│   ├── Projects/
│   │   ├── 05-storage-technology-selection-and-logical-layout.md
│   │   └── README.md
│   ├── 01-oltp-olap-and-operational-analytical-separation.md
│   ├── 02-relational-nosql-and-specialized-database-selection.md
│   ├── 03-object-storage-and-file-format-selection.md
│   ├── 04-warehouse-lakehouse-and-table-format-design.md
│   ├── 05-partitioning-indexing-clustering-and-data-layout.md
│   ├── 06-replication-consistency-and-transaction-boundaries.md
│   ├── 07-retention-archival-and-data-lifecycle-storage-tiers.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Database-and-Storage-Architecture.md
├── 06-Data-Integration-and-Interoperability/
│   ├── Projects/
│   │   ├── 06-cross-system-data-integration-design.md
│   │   └── README.md
│   ├── 01-batch-etl-elt-and-incremental-ingestion.md
│   ├── 02-change-data-capture-and-database-replication.md
│   ├── 03-apis-files-and-managed-connectors.md
│   ├── 04-streaming-events-and-message-contracts.md
│   ├── 05-data-contracts-schema-registry-and-compatibility.md
│   ├── 06-data-virtualization-federation-and-data-sharing.md
│   ├── 07-idempotency-deduplication-and-reconciliation.md
│   ├── 08-integration-pattern-selection-and-failure-handling.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Data-Integration-and-Interoperability.md
├── 07-Enterprise-Data-Platform-and-Lakehouse-Architecture/
│   ├── Projects/
│   │   ├── 07-enterprise-lakehouse-reference-architecture.md
│   │   └── README.md
│   ├── 01-platform-capabilities-and-logical-reference-architecture.md
│   ├── 02-ingestion-storage-processing-and-consumption-zones.md
│   ├── 03-bronze-silver-gold-and-data-product-boundaries.md
│   ├── 04-compute-storage-and-control-plane-separation.md
│   ├── 05-catalogs-metastores-and-platform-metadata.md
│   ├── 06-self-service-platforms-and-developer-experience.md
│   ├── 07-multi-team-isolation-and-tenant-boundaries.md
│   ├── 08-platform-service-levels-and-product-thinking.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Enterprise-Data-Platform-and-Lakehouse-Architecture.md
├── 08-Cloud-Hybrid-and-Multi-Cloud-Data-Architecture/
│   ├── Projects/
│   │   ├── 08-cloud-platform-architecture-comparison.md
│   │   └── README.md
│   ├── 01-cloud-data-architecture-principles.md
│   ├── 02-aws-data-architecture-reference-patterns.md
│   ├── 03-azure-data-architecture-reference-patterns.md
│   ├── 04-gcp-data-architecture-reference-patterns.md
│   ├── 05-networking-identity-and-private-connectivity.md
│   ├── 06-hybrid-connectivity-and-on-premises-integration.md
│   ├── 07-portability-lock-in-and-multi-cloud-trade-offs.md
│   ├── 08-infrastructure-as-code-and-environment-strategy.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Cloud-Hybrid-and-Multi-Cloud-Data-Architecture.md
├── 09-Streaming-and-Real-Time-Data-Architecture/
│   ├── Projects/
│   │   ├── 09-real-time-risk-monitoring-architecture.md
│   │   └── README.md
│   ├── 01-real-time-use-cases-and-latency-budgets.md
│   ├── 02-event-brokers-topics-partitions-and-retention.md
│   ├── 03-event-time-processing-ordering-and-watermarks.md
│   ├── 04-stream-processing-state-and-delivery-semantics.md
│   ├── 05-cdc-event-backbones-and-replay.md
│   ├── 06-real-time-serving-stores-and-materialized-views.md
│   ├── 07-late-events-backpressure-and-stream-failure-modes.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Streaming-and-Real-Time-Data-Architecture.md
├── 10-Data-Governance-Security-Privacy-and-Compliance/
│   ├── Projects/
│   │   ├── 10-sensitive-data-governance-and-access-design.md
│   │   └── README.md
│   ├── 01-governance-operating-model-and-accountability.md
│   ├── 02-data-classification-sensitivity-and-criticality.md
│   ├── 03-identity-access-control-and-least-privilege.md
│   ├── 04-encryption-key-management-and-secrets.md
│   ├── 05-pii-masking-tokenization-and-de-identification.md
│   ├── 06-consent-purpose-limitation-and-data-residency.md
│   ├── 07-retention-deletion-legal-holds-and-auditability.md
│   ├── 08-regulatory-controls-and-evidence-design.md
│   ├── 09-governance-by-design-and-policy-enforcement.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Data-Governance-Security-Privacy-and-Compliance.md
├── 11-Metadata-Lineage-Quality-and-Master-Data/
│   ├── Projects/
│   │   ├── 11-enterprise-metadata-and-lineage-design.md
│   │   └── README.md
│   ├── 01-business-technical-and-operational-metadata.md
│   ├── 02-data-catalogs-discovery-and-classification.md
│   ├── 03-end-to-end-lineage-and-impact-analysis.md
│   ├── 04-data-quality-dimensions-and-critical-data-elements.md
│   ├── 05-data-observability-and-quality-service-levels.md
│   ├── 06-master-data-management-and-golden-records.md
│   ├── 07-reference-data-entity-resolution-and-identifiers.md
│   ├── 08-metadata-standards-and-interoperability.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Metadata-Lineage-Quality-and-Master-Data.md
├── 12-Reliability-Resilience-and-Disaster-Recovery/
│   ├── Projects/
│   │   ├── 12-disaster-recovery-and-resilience-plan.md
│   │   └── README.md
│   ├── 01-reliability-objectives-sli-slo-and-sla.md
│   ├── 02-failure-domains-and-blast-radius.md
│   ├── 03-high-availability-and-redundancy-patterns.md
│   ├── 04-backup-restore-and-recovery-validation.md
│   ├── 05-rpo-rto-and-disaster-recovery-strategies.md
│   ├── 06-replay-reprocessing-and-backfill-architecture.md
│   ├── 07-incident-response-runbooks-and-postmortems.md
│   ├── 08-business-continuity-and-resilience-testing.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Reliability-Resilience-and-Disaster-Recovery.md
├── 13-Performance-Scalability-and-Cost-Architecture/
│   ├── Projects/
│   │   ├── 13-capacity-cost-and-performance-review.md
│   │   └── README.md
│   ├── 01-capacity-planning-and-growth-forecasting.md
│   ├── 02-throughput-latency-concurrency-and-queueing.md
│   ├── 03-query-performance-and-data-locality.md
│   ├── 04-scaling-partitioning-sharding-and-hotspots.md
│   ├── 05-caching-materialization-and-serving-trade-offs.md
│   ├── 06-cost-modeling-unit-economics-and-finops.md
│   ├── 07-performance-testing-and-capacity-validation.md
│   ├── 08-architecture-optimization-with-measured-evidence.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Performance-Scalability-and-Cost-Architecture.md
├── 14-Data-Access-Serving-Semantic-and-AI-Data-Architecture/
│   ├── Projects/
│   │   ├── 14-analytics-and-ai-data-serving-architecture.md
│   │   └── README.md
│   ├── 01-analytical-serving-patterns-and-consumer-needs.md
│   ├── 02-warehouse-marts-and-semantic-layers.md
│   ├── 03-operational-data-serving-and-low-latency-access.md
│   ├── 04-feature-platforms-and-training-serving-consistency.md
│   ├── 05-document-data-embedding-and-vector-pipelines.md
│   ├── 06-rag-knowledge-data-and-permission-aware-retrieval.md
│   ├── 07-data-products-apis-and-consumer-contracts.md
│   ├── 08-access-patterns-cache-strategy-and-freshness.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Data-Access-Serving-Semantic-and-AI-Data-Architecture.md
├── 15-Architecture-Documentation-Reviews-and-Operating-Model/
│   ├── Projects/
│   │   ├── 15-current-state-to-target-state-architecture-review.md
│   │   └── README.md
│   ├── 01-context-container-component-and-deployment-diagrams.md
│   ├── 02-data-flow-and-trust-boundary-diagrams.md
│   ├── 03-architecture-description-and-viewpoints.md
│   ├── 04-architecture-decision-records-and-decision-log.md
│   ├── 05-design-reviews-threat-models-and-risk-registers.md
│   ├── 06-reference-architectures-standards-and-reusable-patterns.md
│   ├── 07-team-boundaries-ownership-and-platform-operating-model.md
│   ├── 08-migration-roadmaps-and-architecture-modernization.md
│   ├── 09-communicating-trade-offs-to-technical-and-business-stakeholders.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Architecture-Documentation-Reviews-and-Operating-Model.md
├── 16-Enterprise-Data-Architecture-Case-Studies-and-Capstone/
│   ├── Projects/
│   │   ├── 16-enterprise-data-architecture-capstone.md
│   │   └── README.md
│   ├── 01-case-study-banking-data-platform.md
│   ├── 02-case-study-customer-360-and-master-data.md
│   ├── 03-case-study-real-time-fraud-and-risk-platform.md
│   ├── 04-case-study-enterprise-lakehouse-modernization.md
│   ├── 05-case-study-multi-cloud-data-platform.md
│   ├── 06-case-study-governed-rag-and-enterprise-knowledge.md
│   ├── 07-capstone-requirements-and-architecture-deliverables.md
│   ├── 08-capstone-validation-defense-and-review-rubric.md
│   ├── README.md
│   ├── practice-questions.md
│   └── roadmap-Enterprise-Data-Architecture-Case-Studies-and-Capstone.md
└── README.md
```

## Stage 2E — Production DevOps & Platform Engineering

```text
Stage 2E — Production DevOps & Platform Engineering/
├── 00-Stage-2E-Overview/
│   ├── Projects/
│   │   ├── 01-production-readiness-baseline.md
│   │   └── README.md
│   ├── free-tier-cloud-account-and-cost-safety.md
│   ├── lab-environment-setup.md
│   ├── local-lab-kind-minikube-and-localstack.md
│   ├── prerequisites-and-exit-criteria.md
│   └── production-devops-tooling-map.md
├── 01-Container-Image-Engineering-and-Registry-Hygiene/
│   ├── Projects/
│   │   ├── 01-hardened-optimized-image-pipeline-for-data-services.md
│   │   └── README.md
│   ├── 01-multi-stage-builds-and-layer-optimization.md
│   ├── 02-minimal-and-distroless-base-images.md
│   ├── 03-reproducible-and-deterministic-image-builds.md
│   ├── 04-build-caching-buildkit-and-build-performance.md
│   ├── 05-image-tagging-versioning-and-immutability.md
│   ├── 06-container-registries-mirrors-and-pull-through-caches.md
│   ├── 07-registry-retention-garbage-collection-and-access-control.md
│   ├── 08-non-root-containers-and-runtime-defaults.md
│   ├── PROMPT-Container-Image-Engineering-and-Registry-Hygiene.md
│   ├── README.md
│   └── practice-questions.md
├── 02-CI-CD-Pipeline-Engineering/
│   ├── Projects/
│   │   ├── 01-multi-stage-ci-cd-pipeline-for-data-and-ml-service.md
│   │   └── README.md
│   ├── 01-ci-cd-architecture-and-pipeline-design-principles.md
│   ├── 02-github-actions-workflows-runners-and-reusable-workflows.md
│   ├── 03-gitlab-ci-stages-jobs-and-templates.md
│   ├── 04-build-caching-parallelism-and-pipeline-speed.md
│   ├── 05-monorepo-and-path-based-pipelines.md
│   ├── 06-test-stages-quality-gates-and-flaky-test-management.md
│   ├── 07-artifact-repositories-and-package-publishing.md
│   ├── 08-semantic-versioning-changelogs-and-release-automation.md
│   ├── 09-environment-promotion-approvals-and-protected-branches.md
│   ├── 10-self-hosted-runners-scaling-and-security.md
│   ├── 11-pipeline-observability-and-dora-delivery-metrics.md
│   ├── PROMPT-CI-CD-Pipeline-Engineering.md
│   ├── README.md
│   └── practice-questions.md
├── 03-Production-Kubernetes-Operations/
│   ├── Projects/
│   │   ├── 01-resilient-data-pipeline-on-kubernetes.md
│   │   └── README.md
│   ├── 01-production-cluster-architecture-and-control-plane.md
│   ├── 02-namespaces-resource-quotas-and-limit-ranges.md
│   ├── 03-probes-health-checks-and-workload-recovery.md
│   ├── 04-deployments-statefulsets-jobs-and-cronjobs-in-production.md
│   ├── 05-pod-disruption-budgets-and-graceful-shutdown.md
│   ├── 06-horizontal-and-vertical-autoscaling.md
│   ├── 07-node-pools-taints-affinity-and-workload-placement.md
│   ├── 08-cluster-upgrades-and-version-compatibility.md
│   ├── 09-kubernetes-rbac-and-pod-security-standards.md
│   ├── 10-etcd-health-backup-and-control-plane-troubleshooting.md
│   ├── 11-production-cluster-troubleshooting.md
│   ├── PROMPT-Production-Kubernetes-Operations.md
│   ├── README.md
│   └── practice-questions.md
├── 04-Kubernetes-Networking-Ingress-and-Service-Mesh/
│   ├── Projects/
│   │   ├── 01-secure-ingress-and-mtls-for-data-and-ml-apis.md
│   │   └── README.md
│   ├── 01-kubernetes-networking-model-cni-and-pod-networking.md
│   ├── 02-services-kube-proxy-and-cluster-dns.md
│   ├── 03-ingress-controllers-and-gateway-api.md
│   ├── 04-load-balancers-and-external-traffic-management.md
│   ├── 05-network-policies-and-zero-trust-segmentation.md
│   ├── 06-tls-termination-and-certificate-lifecycle-with-cert-manager.md
│   ├── 07-service-mesh-fundamentals-istio-and-linkerd.md
│   ├── 08-mtls-traffic-shifting-retries-and-circuit-breaking.md
│   ├── 09-ebpf-networking-and-cilium-overview.md
│   ├── 10-network-troubleshooting-dns-latency-and-packet-loss.md
│   ├── PROMPT-Kubernetes-Networking-Ingress-and-Service-Mesh.md
│   ├── README.md
│   └── practice-questions.md
├── 05-Kubernetes-Storage-and-Stateful-Data-Workloads/
│   ├── Projects/
│   │   ├── 01-stateful-data-platform-with-snapshots-and-recovery.md
│   │   └── README.md
│   ├── 01-volumes-persistentvolumes-and-persistentvolumeclaims.md
│   ├── 02-storageclasses-dynamic-provisioning-and-csi-drivers.md
│   ├── 03-volume-snapshots-cloning-and-expansion.md
│   ├── 04-statefulset-storage-patterns-and-stable-identity.md
│   ├── 05-running-databases-and-brokers-with-operators.md
│   ├── 06-storage-performance-iops-throughput-and-latency.md
│   ├── 07-data-locality-zonal-failure-and-volume-affinity.md
│   ├── 08-storage-troubleshooting-and-orphaned-volumes.md
│   ├── PROMPT-Kubernetes-Storage-and-Stateful-Data-Workloads.md
│   ├── README.md
│   └── practice-questions.md
├── 06-Helm-Kustomize-and-Kubernetes-Packaging/
│   ├── Projects/
│   │   ├── 01-reusable-chart-and-overlays-for-multi-environment-delivery.md
│   │   └── README.md
│   ├── 01-kubernetes-manifest-management-and-the-templating-problem.md
│   ├── 02-helm-charts-values-and-templates.md
│   ├── 03-helm-hooks-dependencies-and-subcharts.md
│   ├── 04-helm-chart-testing-linting-and-versioning.md
│   ├── 05-kustomize-bases-overlays-and-patches.md
│   ├── 06-choosing-helm-vs-kustomize-and-combining-them.md
│   ├── 07-chart-repositories-oci-registries-and-signing.md
│   ├── 08-operators-crds-and-custom-controllers-overview.md
│   ├── PROMPT-Helm-Kustomize-and-Kubernetes-Packaging.md
│   ├── README.md
│   └── practice-questions.md
├── 07-Advanced-Infrastructure-as-Code-and-Cloud-Operations/
│   ├── Projects/
│   │   ├── 01-governed-multi-environment-data-platform-infrastructure.md
│   │   └── README.md
│   ├── 01-terraform-state-backends-locking-and-recovery.md
│   ├── 02-terraform-modules-and-environment-reuse.md
│   ├── 03-state-migration-import-and-drift-detection.md
│   ├── 04-safe-infrastructure-plans-and-change-approval.md
│   ├── 05-cloud-account-and-environment-boundaries.md
│   ├── 06-policy-as-code-for-infrastructure-guardrails.md
│   ├── 07-cloud-quotas-service-limits-and-resource-governance.md
│   ├── 08-infrastructure-decommissioning-and-orphan-cleanup.md
│   ├── 09-terragrunt-opentofu-and-pulumi-alternatives.md
│   ├── 10-configuration-management-with-ansible.md
│   ├── 11-infrastructure-testing-terratest-and-plan-validation.md
│   ├── 12-crossplane-and-kubernetes-native-infrastructure.md
│   ├── PROMPT-Advanced-Infrastructure-as-Code-and-Cloud-Operations.md
│   ├── README.md
│   └── practice-questions.md
├── 08-GitOps-and-Progressive-Delivery/
│   ├── Projects/
│   │   ├── 01-gitops-controlled-data-service-release.md
│   │   └── README.md
│   ├── 01-gitops-principles-and-desired-state-reconciliation.md
│   ├── 02-argo-cd-applications-projects-and-sync-policies.md
│   ├── 03-flux-controllers-and-kustomize-helm-reconciliation.md
│   ├── 04-repository-layout-and-multi-environment-promotion.md
│   ├── 05-configuration-and-secret-reference-management.md
│   ├── 06-deployment-drift-detection-and-reconciliation.md
│   ├── 07-progressive-delivery-with-canary-and-blue-green-releases.md
│   ├── 08-argo-rollouts-flagger-and-traffic-based-analysis.md
│   ├── 09-release-health-analysis-and-automated-abort.md
│   ├── 10-feature-flags-and-dark-launches.md
│   ├── 11-database-and-data-platform-migration-safety.md
│   ├── 12-backward-compatible-pipeline-and-api-releases.md
│   ├── 13-release-evidence-and-audit-trails.md
│   ├── PROMPT-GitOps-and-Progressive-Delivery.md
│   ├── README.md
│   └── practice-questions.md
├── 09-Secrets-and-Identity-Management/
│   ├── Projects/
│   │   ├── 01-zero-static-credential-secrets-platform.md
│   │   └── README.md
│   ├── 01-secrets-threat-model-and-lifecycle.md
│   ├── 02-hashicorp-vault-architecture-and-auth-methods.md
│   ├── 03-dynamic-secrets-leases-and-rotation.md
│   ├── 04-external-secrets-operator-and-cloud-secret-managers.md
│   ├── 05-sops-sealed-secrets-and-encrypted-secrets-in-git.md
│   ├── 06-kubernetes-secret-encryption-and-csi-secret-store.md
│   ├── 07-workload-identity-irsa-and-federated-credentials.md
│   ├── 08-secret-leak-detection-and-incident-response.md
│   ├── PROMPT-Secrets-and-Identity-Management.md
│   ├── README.md
│   └── practice-questions.md
├── 10-Site-Reliability-Engineering-and-Incident-Management/
│   ├── Projects/
│   │   ├── 01-production-incident-simulation-and-postmortem.md
│   │   └── README.md
│   ├── 01-service-level-indicators-objectives-and-error-budgets.md
│   ├── 02-reliability-targets-for-batch-streaming-and-inference.md
│   ├── 03-alert-quality-noise-reduction-and-escalation-policies.md
│   ├── 04-incident-severity-roles-and-command-structure.md
│   ├── 05-production-triage-and-blameless-postmortems.md
│   ├── 06-capacity-related-failures-and-cascading-outages.md
│   ├── 07-toil-reduction-and-operational-automation.md
│   ├── 08-runbook-design-and-operational-readiness-reviews.md
│   ├── 09-error-budget-policies-and-release-freezes.md
│   ├── 10-on-call-rotations-handoffs-and-sustainable-paging.md
│   ├── 11-dora-metrics-and-engineering-performance-measurement.md
│   ├── PROMPT-Site-Reliability-Engineering-and-Incident-Management.md
│   ├── README.md
│   └── practice-questions.md
├── 11-Production-Observability-Stack-and-Performance-Operations/
│   ├── Projects/
│   │   ├── 01-platform-health-and-bottleneck-investigation.md
│   │   ├── 02-end-to-end-observability-stack-build.md
│   │   └── README.md
│   ├── 01-production-telemetry-architecture-and-retention.md
│   ├── 02-prometheus-metrics-scraping-and-promql.md
│   ├── 03-grafana-dashboards-and-dashboard-as-code.md
│   ├── 04-loki-and-centralized-log-pipelines.md
│   ├── 05-opentelemetry-collector-and-trace-pipelines.md
│   ├── 06-alertmanager-routing-silencing-and-on-call-integration.md
│   ├── 07-service-dependencies-and-end-to-end-failure-correlation.md
│   ├── 08-actionable-alerts-and-symptom-based-monitoring.md
│   ├── 09-saturation-queue-depth-and-resource-exhaustion.md
│   ├── 10-distributed-trace-analysis-and-bottleneck-isolation.md
│   ├── 11-scheduled-job-freshness-and-deadline-monitoring.md
│   ├── 12-observability-cost-cardinality-and-data-retention.md
│   ├── 13-production-load-stress-and-soak-testing.md
│   ├── PROMPT-Production-Observability-Stack-and-Performance-Operations.md
│   ├── README.md
│   └── practice-questions.md
├── 12-Production-Security-and-Software-Supply-Chain/
│   ├── Projects/
│   │   ├── 01-secure-and-verified-container-release.md
│   │   └── README.md
│   ├── 01-threat-modelling-for-data-and-ml-platforms.md
│   ├── 02-container-image-scanning-and-vulnerability-triage.md
│   ├── 03-software-bills-of-materials-and-dependency-provenance.md
│   ├── 04-image-signing-and-deployment-verification.md
│   ├── 05-build-isolation-and-short-lived-ci-identities.md
│   ├── 06-workload-identity-and-credential-rotation.md
│   ├── 07-runtime-security-and-container-hardening.md
│   ├── 08-admission-controls-and-deployment-policy-enforcement.md
│   ├── 09-security-auditing-and-vulnerability-remediation-workflows.md
│   ├── 10-slsa-framework-and-build-provenance-levels.md
│   ├── 11-kyverno-and-opa-gatekeeper-policy-authoring.md
│   ├── 12-runtime-threat-detection-with-falco.md
│   ├── PROMPT-Production-Security-and-Software-Supply-Chain.md
│   ├── README.md
│   └── practice-questions.md
├── 13-Backup-Disaster-Recovery-and-Resilience-Testing/
│   ├── Projects/
│   │   ├── 01-tested-disaster-recovery-for-data-and-ml.md
│   │   └── README.md
│   ├── 01-recovery-time-and-recovery-point-objectives.md
│   ├── 02-backup-scope-retention-and-immutability.md
│   ├── 03-restoring-platform-metadata-and-configuration.md
│   ├── 04-recovering-data-pipeline-state-and-checkpoints.md
│   ├── 05-recovering-model-artifacts-and-registry-metadata.md
│   ├── 06-regional-failure-and-dependency-outage-strategies.md
│   ├── 07-restore-drills-and-recovery-evidence.md
│   ├── 08-failure-injection-and-resilience-exercises.md
│   ├── 09-kubernetes-backup-and-restore-with-velero.md
│   ├── 10-chaos-engineering-with-litmus-and-chaos-mesh.md
│   ├── PROMPT-Backup-Disaster-Recovery-and-Resilience-Testing.md
│   ├── README.md
│   └── practice-questions.md
├── 14-Multi-Cluster-and-Multi-Region-Operations/
│   ├── Projects/
│   │   ├── 01-two-region-failover-for-a-data-platform.md
│   │   └── README.md
│   ├── 01-multi-cluster-topologies-and-when-to-split-clusters.md
│   ├── 02-fleet-management-and-cluster-lifecycle-with-cluster-api.md
│   ├── 03-multi-cluster-gitops-and-config-propagation.md
│   ├── 04-cross-cluster-service-discovery-and-traffic-routing.md
│   ├── 05-global-load-balancing-and-dns-failover.md
│   ├── 06-active-active-vs-active-passive-regional-designs.md
│   ├── 07-data-replication-and-consistency-across-regions.md
│   ├── 08-multi-cluster-observability-and-policy-governance.md
│   ├── PROMPT-Multi-Cluster-and-Multi-Region-Operations.md
│   ├── README.md
│   └── practice-questions.md
├── 15-Platform-Capacity-Compute-Economics-and-FinOps/
│   ├── Projects/
│   │   ├── 01-capacity-and-cost-governance-for-data-ml-platforms.md
│   │   └── README.md
│   ├── 01-platform-capacity-forecasting-and-headroom.md
│   ├── 02-workload-priorities-quotas-and-resource-contention.md
│   ├── 03-cloud-budget-alerts-and-spending-guardrails.md
│   ├── 04-cost-allocation-by-team-project-and-workload.md
│   ├── 05-idle-resource-detection-and-automated-cleanup.md
│   ├── 06-cost-reliability-and-performance-tradeoffs.md
│   ├── 07-capacity-and-cost-review-for-production-releases.md
│   ├── 08-spot-and-preemptible-instances-for-data-workloads.md
│   ├── 09-karpenter-and-cluster-autoscaler-node-provisioning.md
│   ├── 10-event-driven-autoscaling-with-keda.md
│   ├── 11-kubernetes-cost-visibility-with-opencost.md
│   ├── 12-gpu-scheduling-sharing-and-ml-workload-economics.md
│   ├── PROMPT-Platform-Capacity-Compute-Economics-and-FinOps.md
│   ├── README.md
│   └── practice-questions.md
├── 16-Platform-Engineering-and-Internal-Developer-Platforms/
│   ├── Projects/
│   │   ├── 01-self-service-data-and-ml-platform-portal.md
│   │   └── README.md
│   ├── 01-platform-engineering-principles-and-platform-as-a-product.md
│   ├── 02-golden-paths-templates-and-paved-roads.md
│   ├── 03-self-service-infrastructure-and-environment-provisioning.md
│   ├── 04-developer-portals-and-backstage-service-catalog.md
│   ├── 05-scaffolding-and-software-templates.md
│   ├── 06-platform-apis-with-crossplane-compositions.md
│   ├── 07-multi-tenancy-isolation-and-tenant-onboarding.md
│   ├── 08-platform-slos-adoption-metrics-and-developer-experience.md
│   ├── 09-platform-governance-deprecation-and-versioning.md
│   ├── PROMPT-Platform-Engineering-and-Internal-Developer-Platforms.md
│   ├── README.md
│   └── practice-questions.md
├── 17-Production-DevOps-Integrated-Capstone/
│   ├── Projects/
│   │   ├── 01-production-data-platform-deployment.md
│   │   ├── 02-reliable-scheduled-pipeline-operations.md
│   │   ├── 03-production-ml-service-operations.md
│   │   ├── 04-end-to-end-production-devops-capstone.md
│   │   └── README.md
│   ├── PROMPT-Production-DevOps-Integrated-Capstone.md
│   ├── README.md
│   ├── capstone-requirements.md
│   ├── cost-and-reliability-rubric.md
│   ├── incident-and-recovery-rubric.md
│   ├── platform-and-delivery-rubric.md
│   ├── production-readiness-checklist.md
│   └── security-and-release-rubric.md
└── README.md
```

## Stage 3 — Data Structures & Algorithms

```text
Stage 3 — Data Structures & Algorithms/
├── 00-Stage-3-Overview/
│   ├── Projects/
│   │   ├── 01-algorithm-toolkit-and-benchmark.md
│   │   └── README.md
│   ├── PROMPT-Stage-3-Overview.md
│   ├── README.md
│   ├── dsa-topic-map-and-interview-coverage.md
│   ├── learning-plan.md
│   ├── progress-tracker-and-readiness-checklist.md
│   ├── role-wise-dsa-relevance-map.md
│   └── stage-prerequisites-and-learning-objectives.md
├── 01-Complexity-and-Big-O/
│   ├── Projects/
│   │   ├── 01-benchmark-python-collections.md
│   │   └── README.md
│   ├── 01-what-an-algorithm-is.md
│   ├── 02-counting-steps-and-growth.md
│   ├── 03-big-o-notation.md
│   ├── 04-time-vs-space-complexity.md
│   ├── 05-amortized-analysis.md
│   ├── 06-measuring-real-performance-in-python.md
│   ├── 07-best-average-and-worst-case-analysis.md
│   ├── 08-complexity-analysis-of-loops-and-recursion.md
│   ├── 09-comparing-algorithmic-complexities.md
│   ├── PROMPT-Complexity-and-Big-O.md
│   ├── README.md
│   └── practice-questions.md
├── 02-Arrays-Strings-and-Hashing/
│   ├── Projects/
│   │   ├── 01-build-a-hash-map-from-scratch.md
│   │   ├── 02-array-and-string-problem-toolkit.md
│   │   └── README.md
│   ├── 01-arrays-and-dynamic-arrays.md
│   ├── 02-strings-and-immutability.md
│   ├── 03-hash-tables-internals.md
│   ├── 04-hash-map-and-set-patterns.md
│   ├── 05-prefix-sums.md
│   ├── 06-frequency-counting-patterns.md
│   ├── 07-multidimensional-arrays-and-matrices.md
│   ├── 08-string-manipulation-and-patterns.md
│   ├── 09-subarrays-substrings-and-subsequences.md
│   ├── 10-hashing-collisions-and-performance-tradeoffs.md
│   ├── 11-kadane-and-maximum-subarray-patterns.md
│   ├── 12-boyer-moore-voting-and-majority-element.md
│   ├── 13-dutch-national-flag-and-in-place-partitioning.md
│   ├── 14-rolling-hash-and-rabin-karp.md
│   ├── PROMPT-Arrays-Strings-and-Hashing.md
│   ├── README.md
│   └── practice-questions.md
├── 03-Two-Pointers-Sliding-Window-and-Binary-Search/
│   ├── Projects/
│   │   ├── 01-log-window-analyzer.md
│   │   ├── 02-search-and-window-pattern-library.md
│   │   └── README.md
│   ├── 01-two-pointers.md
│   ├── 02-sliding-window.md
│   ├── 03-binary-search.md
│   ├── 04-binary-search-on-the-answer.md
│   ├── 05-pattern-recognition-drills.md
│   ├── 06-fast-and-slow-pointers.md
│   ├── 07-interval-based-problem-patterns.md
│   ├── 08-sorting-and-searching-combinations.md
│   ├── 09-invariants-and-search-space-reduction.md
│   ├── PROMPT-Two-Pointers-Sliding-Window-and-Binary-Search.md
│   ├── README.md
│   └── practice-questions.md
├── 04-Stacks-Queues-and-Linked-Lists/
│   ├── Projects/
│   │   ├── 01-implement-an-lru-cache.md
│   │   ├── 02-build-a-stack-queue-and-deque-toolkit.md
│   │   ├── 03-implement-an-lfu-cache.md
│   │   └── README.md
│   ├── 01-stacks.md
│   ├── 02-queues-and-deques.md
│   ├── 03-monotonic-stack.md
│   ├── 04-singly-and-doubly-linked-lists.md
│   ├── 05-lru-cache-design.md
│   ├── 06-monotonic-queues.md
│   ├── 07-fast-and-slow-pointer-linked-list-problems.md
│   ├── 08-expression-parsing-and-balanced-delimiters.md
│   ├── 09-designing-data-structures-with-combined-components.md
│   ├── 10-lfu-cache-design.md
│   ├── 11-time-based-key-value-store-and-design-problems.md
│   ├── PROMPT-Stacks-Queues-and-Linked-Lists.md
│   ├── README.md
│   └── practice-questions.md
├── 05-Recursion-Backtracking-and-Sorting/
│   ├── Projects/
│   │   ├── 01-sorting-benchmark.md
│   │   ├── 02-backtracking-puzzle-solver.md
│   │   └── README.md
│   ├── 01-recursion-and-the-call-stack.md
│   ├── 02-backtracking.md
│   ├── 03-sorting-algorithms.md
│   ├── 04-merge-sort-and-quick-sort.md
│   ├── 05-divide-and-conquer.md
│   ├── 06-recursion-trees-and-recursive-complexity.md
│   ├── 07-permutations-combinations-and-subsets.md
│   ├── 08-constraint-satisfaction-and-pruning.md
│   ├── 09-stable-in-place-and-adaptive-sorting.md
│   ├── 10-selection-algorithms-and-quickselect.md
│   ├── 11-counting-radix-and-bucket-sort.md
│   ├── 12-non-comparison-sorting-and-top-k-frequent-patterns.md
│   ├── 13-sorting-in-python-timsort-and-custom-comparators.md
│   ├── PROMPT-Recursion-Backtracking-and-Sorting.md
│   ├── README.md
│   └── practice-questions.md
├── 06-Trees-and-Tries/
│   ├── Projects/
│   │   ├── 01-autocomplete-with-a-trie.md
│   │   ├── 02-binary-tree-algorithm-toolkit.md
│   │   └── README.md
│   ├── 01-tree-terminology.md
│   ├── 02-tree-traversals.md
│   ├── 03-binary-search-trees.md
│   ├── 04-balanced-trees-intuition.md
│   ├── 05-tries-and-prefix-search.md
│   ├── 06-recursive-and-iterative-tree-problems.md
│   ├── 07-lowest-common-ancestor.md
│   ├── 08-binary-tree-views-and-tree-properties.md
│   ├── 09-binary-search-tree-validation-and-operations.md
│   ├── 10-serialization-and-deserialization-of-trees.md
│   ├── 11-avl-trees-and-rotations.md
│   ├── 12-red-black-trees-and-balancing-invariants.md
│   ├── 13-morris-traversal-and-constant-space-traversal.md
│   ├── 14-euler-tour-and-subtree-queries.md
│   ├── 15-binary-lifting-and-fast-lca.md
│   ├── 16-trie-variants-wildcard-and-xor-tries.md
│   ├── PROMPT-Trees-and-Tries.md
│   ├── README.md
│   └── practice-questions.md
├── 07-Heaps-and-Priority-Queues/
│   ├── Projects/
│   │   ├── 01-top-k-streaming-tracker.md
│   │   ├── 02-running-median-service.md
│   │   └── README.md
│   ├── 01-heap-structure.md
│   ├── 02-heapq-in-python.md
│   ├── 03-top-k-problems.md
│   ├── 04-merging-sorted-streams.md
│   ├── 05-scheduling-with-priority-queues.md
│   ├── 06-two-heaps-and-running-medians.md
│   ├── 07-heap-based-search-and-selection.md
│   ├── 08-priority-queue-design-tradeoffs.md
│   ├── 09-tournament-trees-and-k-way-selection.md
│   ├── 10-indexed-priority-queues-and-decrease-key.md
│   ├── PROMPT-Heaps-and-Priority-Queues.md
│   ├── README.md
│   └── practice-questions.md
├── 08-Graphs-BFS-DFS-and-Shortest-Paths/
│   ├── Projects/
│   │   ├── 01-dependency-resolver.md
│   │   └── README.md
│   ├── 01-graph-representations.md
│   ├── 02-breadth-first-search.md
│   ├── 03-depth-first-search.md
│   ├── 04-topological-sort.md
│   ├── 05-union-find.md
│   ├── 06-dijkstra-shortest-paths.md
│   ├── 07-connected-components-and-cycle-detection.md
│   ├── 08-bipartite-graphs-and-two-coloring.md
│   ├── 09-grid-and-matrix-graph-problems.md
│   ├── 10-directed-vs-undirected-and-weighted-vs-unweighted-graphs.md
│   ├── PROMPT-Graphs-BFS-DFS-and-Shortest-Paths.md
│   ├── README.md
│   └── practice-questions.md
├── 09-Dynamic-Programming/
│   ├── Projects/
│   │   ├── 01-fuzzy-text-matcher.md
│   │   ├── 02-dynamic-programming-pattern-library.md
│   │   └── README.md
│   ├── 01-what-dynamic-programming-is.md
│   ├── 02-memoization-vs-tabulation.md
│   ├── 03-one-dimensional-dp-patterns.md
│   ├── 04-two-dimensional-dp-patterns.md
│   ├── 05-edit-distance-and-sequence-alignment.md
│   ├── 06-state-transition-and-base-case-design.md
│   ├── 07-knapsack-and-subset-sum.md
│   ├── 08-grid-path-and-matrix-dp.md
│   ├── 09-longest-increasing-subsequence.md
│   ├── 10-interval-and-partition-dp.md
│   ├── 11-tree-dynamic-programming.md
│   ├── 12-bitmask-dynamic-programming-introduction.md
│   ├── 13-space-optimization-in-dynamic-programming.md
│   ├── PROMPT-Dynamic-Programming.md
│   ├── README.md
│   └── practice-questions.md
├── 10-Bit-Manipulation-and-Bitwise-Algorithms/
│   ├── Projects/
│   │   ├── 01-bitwise-utility-library.md
│   │   ├── 02-subset-enumeration-toolkit.md
│   │   └── README.md
│   ├── 01-binary-representation-and-bitwise-operators.md
│   ├── 02-bit-masks-and-bit-flags.md
│   ├── 03-setting-clearing-toggling-and-checking-bits.md
│   ├── 04-shifts-and-integer-bit-properties.md
│   ├── 05-counting-set-bits-and-hamming-weight.md
│   ├── 06-xor-patterns-and-single-number-problems.md
│   ├── 07-subsets-using-bitmasks.md
│   ├── 08-bit-tricks-and-common-interview-patterns.md
│   ├── 09-bitmask-dynamic-programming.md
│   ├── 10-bit-manipulation-correctness-and-edge-cases.md
│   ├── PROMPT-Bit-Manipulation-and-Bitwise-Algorithms.md
│   ├── README.md
│   └── practice-questions.md
├── 11-Greedy-Algorithms/
│   ├── Projects/
│   │   ├── 01-interval-scheduling-optimizer.md
│   │   ├── 02-resource-allocation-planner.md
│   │   └── README.md
│   ├── 01-greedy-algorithm-fundamentals.md
│   ├── 02-greedy-choice-property-and-correctness.md
│   ├── 03-interval-scheduling-and-activity-selection.md
│   ├── 04-merge-intervals-and-interval-optimization.md
│   ├── 05-meeting-room-and-resource-allocation-problems.md
│   ├── 06-jump-game-and-reachability-patterns.md
│   ├── 07-gas-station-and-circular-optimization-problems.md
│   ├── 08-greedy-vs-dynamic-programming.md
│   ├── 09-huffman-coding-and-greedy-construction.md
│   ├── 10-proving-or-disproving-a-greedy-strategy.md
│   ├── PROMPT-Greedy-Algorithms.md
│   ├── README.md
│   └── practice-questions.md
├── 12-Advanced-Graph-Algorithms/
│   ├── Projects/
│   │   ├── 01-graph-routing-and-algorithm-comparison.md
│   │   ├── 02-dependency-analysis-and-critical-path-tool.md
│   │   └── README.md
│   ├── 01-graph-algorithm-selection-guide.md
│   ├── 02-bellman-ford-shortest-paths.md
│   ├── 03-floyd-warshall-all-pairs-shortest-paths.md
│   ├── 04-minimum-spanning-trees-kruskal-and-prim.md
│   ├── 05-strongly-connected-components.md
│   ├── 06-bridges-and-articulation-points.md
│   ├── 07-advanced-union-find-patterns.md
│   ├── 08-shortest-paths-with-special-constraints.md
│   ├── 09-network-flow-and-max-flow-min-cut-introduction.md
│   ├── 10-bipartite-matching-introduction.md
│   ├── 11-advanced-topological-ordering-and-dependency-analysis.md
│   ├── 12-graph-algorithm-complexity-and-tradeoffs.md
│   ├── 13-a-star-search-and-heuristics.md
│   ├── 14-bidirectional-search-and-0-1-bfs.md
│   ├── 15-eulerian-and-hamiltonian-paths-introduction.md
│   ├── PROMPT-Advanced-Graph-Algorithms.md
│   ├── README.md
│   └── practice-questions.md
├── 13-Range-Query-Data-Structures/
│   ├── Projects/
│   │   ├── 01-range-query-engine.md
│   │   ├── 02-dynamic-range-statistics-tool.md
│   │   └── README.md
│   ├── 01-range-query-problem-fundamentals.md
│   ├── 02-prefix-sums-for-range-queries.md
│   ├── 03-difference-arrays-and-range-updates.md
│   ├── 04-fenwick-tree-binary-indexed-tree.md
│   ├── 05-fenwick-tree-point-updates-and-prefix-queries.md
│   ├── 06-segment-tree-fundamentals.md
│   ├── 07-segment-tree-range-queries-and-point-updates.md
│   ├── 08-lazy-propagation-for-range-updates.md
│   ├── 09-iterative-segment-trees.md
│   ├── 10-sparse-table-for-static-range-queries.md
│   ├── 11-choosing-between-prefix-sums-fenwick-and-segment-trees.md
│   ├── 12-range-query-complexity-and-correctness.md
│   ├── 13-sqrt-decomposition-and-mos-algorithm.md
│   ├── 14-interval-trees-and-merge-sort-trees.md
│   ├── PROMPT-Range-Query-Data-Structures.md
│   ├── README.md
│   └── practice-questions.md
├── 14-Advanced-Problem-Solving-Patterns/
│   ├── Projects/
│   │   ├── 01-pattern-recognition-practice-engine.md
│   │   ├── 02-mixed-pattern-challenge-set.md
│   │   └── README.md
│   ├── 01-pattern-recognition-and-problem-classification.md
│   ├── 02-prefix-suffix-and-cumulative-patterns.md
│   ├── 03-intervals-and-sweep-line-algorithms.md
│   ├── 04-coordinate-compression.md
│   ├── 05-invariants-and-proof-driven-problem-solving.md
│   ├── 06-meet-in-the-middle.md
│   ├── 07-monotonicity-and-binary-search-on-the-answer.md
│   ├── 08-advanced-two-pointers-and-sliding-window.md
│   ├── 09-combinatorial-counting-and-search-space-pruning.md
│   ├── 10-randomized-algorithms-and-hashing-tradeoffs.md
│   ├── 11-choosing-between-greedy-dp-and-backtracking.md
│   ├── 12-reducing-one-problem-to-a-known-pattern.md
│   ├── 13-approximating-and-bounding-complexity.md
│   ├── 14-game-theory-minimax-and-game-dp.md
│   ├── 15-reservoir-sampling-and-fisher-yates-shuffle.md
│   ├── PROMPT-Advanced-Problem-Solving-Patterns.md
│   ├── README.md
│   └── practice-questions.md
├── 15-String-Algorithms/
│   ├── Projects/
│   │   ├── 01-substring-search-engine-benchmark.md
│   │   ├── 02-log-pattern-scanner-with-aho-corasick.md
│   │   └── README.md
│   ├── 01-string-matching-fundamentals.md
│   ├── 02-kmp-and-prefix-function.md
│   ├── 03-z-algorithm.md
│   ├── 04-rabin-karp-and-multi-pattern-hashing.md
│   ├── 05-manacher-and-palindromic-substrings.md
│   ├── 06-aho-corasick-multi-pattern-search.md
│   ├── 07-suffix-arrays-and-suffix-trees-introduction.md
│   ├── 08-longest-common-prefix-and-string-dp-links.md
│   ├── 09-text-processing-for-logs-and-tokenization.md
│   ├── PROMPT-String-Algorithms.md
│   ├── README.md
│   └── practice-questions.md
├── 16-Math-Number-Theory-and-Geometry/
│   ├── Projects/
│   │   ├── 01-number-theory-toolkit.md
│   │   ├── 02-geometry-problem-set.md
│   │   └── README.md
│   ├── 01-gcd-lcm-and-euclidean-algorithm.md
│   ├── 02-primes-and-sieve-of-eratosthenes.md
│   ├── 03-modular-arithmetic-and-fast-exponentiation.md
│   ├── 04-combinatorics-nCr-and-counting-with-modulo.md
│   ├── 05-probability-and-expected-value-for-interviews.md
│   ├── 06-basic-computational-geometry-and-line-sweep.md
│   ├── 07-convex-hull-and-closest-pair-introduction.md
│   ├── PROMPT-Math-Number-Theory-and-Geometry.md
│   ├── README.md
│   └── practice-questions.md
├── 17-Probabilistic-and-Advanced-Data-Structures/
│   ├── Projects/
│   │   ├── 01-bloom-filter-deduplicator.md
│   │   ├── 02-streaming-analytics-sketch-library.md
│   │   ├── 03-consistent-hash-ring-simulator.md
│   │   └── README.md
│   ├── 01-why-approximate-data-structures-exist.md
│   ├── 02-bloom-filter-and-counting-bloom-filter.md
│   ├── 03-count-min-sketch-and-frequency-estimation.md
│   ├── 04-hyperloglog-and-cardinality-estimation.md
│   ├── 05-skip-lists.md
│   ├── 06-consistent-hashing-and-hash-rings.md
│   ├── 07-cuckoo-and-open-addressing-hash-tables.md
│   ├── 08-heavy-hitters-and-streaming-algorithms.md
│   ├── 09-sliding-window-statistics-over-streams.md
│   ├── PROMPT-Probabilistic-and-Advanced-Data-Structures.md
│   ├── README.md
│   └── practice-questions.md
├── 18-Storage-Engine-and-Large-Scale-Data-Algorithms/
│   ├── Projects/
│   │   ├── 01-mini-lsm-key-value-store.md
│   │   ├── 02-external-sort-for-large-files.md
│   │   ├── 03-join-algorithm-comparison.md
│   │   └── README.md
│   ├── 01-memory-hierarchy-and-io-cost-model.md
│   ├── 02-b-trees-and-b-plus-trees.md
│   ├── 03-lsm-trees-memtables-and-compaction.md
│   ├── 04-external-merge-sort.md
│   ├── 05-hash-joins-sort-merge-joins-and-nested-loops.md
│   ├── 06-partitioning-sharding-and-skew-handling.md
│   ├── 07-columnar-encoding-run-length-and-dictionary.md
│   ├── 08-mapreduce-style-algorithm-design.md
│   ├── PROMPT-Storage-Engine-and-Large-Scale-Data-Algorithms.md
│   ├── README.md
│   └── practice-questions.md
├── 19-Similarity-Search-and-AI-Algorithms/
│   ├── Projects/
│   │   ├── 01-mini-vector-search-engine.md
│   │   ├── 02-agent-task-dag-scheduler.md
│   │   ├── 03-rate-limiter-and-llm-request-queue.md
│   │   └── README.md
│   ├── 01-nearest-neighbor-search-fundamentals.md
│   ├── 02-kd-trees-and-ball-trees.md
│   ├── 03-minhash-and-jaccard-similarity.md
│   ├── 04-locality-sensitive-hashing.md
│   ├── 05-hnsw-and-graph-based-ann-search.md
│   ├── 06-top-k-retrieval-and-reranking-with-heaps.md
│   ├── 07-beam-search-and-constrained-decoding.md
│   ├── 08-dag-scheduling-and-task-planning-search.md
│   ├── 09-rate-limiting-token-bucket-and-leaky-bucket.md
│   ├── 10-agent-workflow-graphs-and-state-machines.md
│   ├── 11-caching-and-memoization-for-llm-applications.md
│   ├── PROMPT-Similarity-Search-and-AI-Algorithms.md
│   ├── README.md
│   └── practice-questions.md
├── 20-Coding-Interview-Method/
│   ├── Projects/
│   │   ├── 01-practice-log-first-50-problems.md
│   │   ├── 02-timed-mock-interview-scorecard.md
│   │   └── README.md
│   ├── 01-structured-problem-solving-framework.md
│   ├── 02-communicating-while-coding.md
│   ├── 03-testing-and-edge-cases.md
│   ├── 04-spaced-repetition-practice-system.md
│   ├── 05-mock-interview-routine.md
│   ├── 06-clarifying-requirements-and-constraints.md
│   ├── 07-brute-force-to-optimized-solution.md
│   ├── 08-explaining-time-and-space-complexity.md
│   ├── 09-debugging-under-interview-conditions.md
│   ├── 10-timed-coding-practice-strategy.md
│   ├── 11-reviewing-failed-solutions-and-error-patterns.md
│   ├── 12-interview-readiness-rubric.md
│   ├── PROMPT-Coding-Interview-Method.md
│   ├── README.md
│   └── practice-questions.md
├── 21-Advanced-DSA-Capstone-and-Interview-Readiness/
│   ├── Projects/
│   │   ├── 01-dsa-algorithm-toolkit-capstone.md
│   │   ├── 02-advanced-problem-solving-portfolio.md
│   │   ├── 03-final-timed-interview-simulation.md
│   │   └── README.md
│   ├── 01-capstone-requirements-and-success-criteria.md
│   ├── 02-building-a-reusable-dsa-algorithm-toolkit.md
│   ├── 03-benchmarking-and-complexity-validation.md
│   ├── 04-solving-mixed-topic-problems-under-time-limits.md
│   ├── 05-advanced-interview-question-bank.md
│   ├── 06-weekly-mock-interview-and-review-cycle.md
│   ├── 07-final-readiness-assessment.md
│   ├── 08-gaps-remediation-and-revision-plan.md
│   ├── 09-final-project-documentation-and-demonstration.md
│   ├── 10-system-design-bridge-from-dsa-to-architecture.md
│   ├── PROMPT-Advanced-DSA-Capstone-and-Interview-Readiness.md
│   ├── README.md
│   └── practice-questions.md
└── README.md
```

## Stage 4A — Basic Mathematics Prerequisite

```text
Stage 4A — Basic Mathematics Prerequisite/
├── 00-Prerequisite-Overview/
│   ├── Projects/
│   │   ├── 01-prerequisite-math-workbook-and-readiness-check.md
│   │   └── README.md
│   ├── PROMPT-Prerequisite-Overview.md
│   ├── README.md
│   ├── how-4a-connects-to-4b-and-4c.md
│   ├── learning-plan.md
│   └── readiness-checklist-and-self-assessment.md
├── 01-Number-Systems-and-Arithmetic-Essentials/
│   ├── Projects/
│   │   ├── 01-number-system-explorer-in-python.md
│   │   └── README.md
│   ├── 01-number-types-and-the-number-line.md
│   ├── 02-sets-set-notation-and-venn-diagrams.md
│   ├── 03-negative-numbers-and-absolute-value.md
│   ├── 04-place-value-decimals-and-rounding.md
│   ├── 05-order-of-operations.md
│   ├── 06-factors-multiples-primes-and-gcd-lcm-essentials.md
│   ├── 07-estimation-mental-math-and-sanity-checks.md
│   ├── 08-units-conversions-and-dimensional-consistency.md
│   ├── PROMPT-Number-Systems-and-Arithmetic-Essentials.md
│   ├── README.md
│   └── practice-questions.md
├── 02-Fractions-Ratios-and-Percentages/
│   ├── Projects/
│   │   ├── 01-percentage-and-ratio-calculator.md
│   │   └── README.md
│   ├── 01-fractions-meaning-equivalence-and-simplifying.md
│   ├── 02-comparing-and-ordering-fractions.md
│   ├── 03-fraction-arithmetic.md
│   ├── 04-converting-between-fractions-decimals-and-percentages.md
│   ├── 05-ratios-simplifying-and-equivalent-ratios.md
│   ├── 06-rates-and-unit-rates.md
│   ├── 07-direct-and-inverse-proportion.md
│   ├── 08-percentages-of-quantities-increase-decrease-and-reverse.md
│   ├── 09-percentage-points-versus-percentage-change.md
│   ├── 10-weighted-averages.md
│   ├── PROMPT-Fractions-Ratios-and-Percentages.md
│   ├── README.md
│   └── practice-questions.md
├── 03-Algebra-Foundations/
│   ├── Projects/
│   │   ├── 01-symbolic-algebra-checker-with-sympy.md
│   │   └── README.md
│   ├── 01-variables-constants-coefficients-terms-and-expressions.md
│   ├── 02-translating-words-into-expressions.md
│   ├── 03-like-terms-simplifying-and-the-distributive-property.md
│   ├── 04-expanding-brackets-and-algebraic-identities.md
│   ├── 05-factorization-fundamentals.md
│   ├── 06-substitution-and-evaluating-formulas.md
│   ├── 07-rearranging-formulas.md
│   ├── 08-algebraic-fractions.md
│   ├── 09-polynomials-and-basic-terminology.md
│   ├── 10-common-algebra-mistakes.md
│   ├── PROMPT-Algebra-Foundations.md
│   ├── README.md
│   └── practice-questions.md
├── 04-Equations-Inequalities-and-Systems/
│   ├── Projects/
│   │   ├── 01-equation-and-system-solver-toolkit.md
│   │   └── README.md
│   ├── 01-equations-and-the-balance-principle.md
│   ├── 02-solving-linear-equations.md
│   ├── 03-linear-equations-with-brackets-fractions-and-variables-on-both-sides.md
│   ├── 04-translating-word-problems-into-equations.md
│   ├── 05-factoring-trinomials-and-solving-quadratics-by-factoring.md
│   ├── 06-completing-the-square.md
│   ├── 07-the-quadratic-formula-and-the-discriminant.md
│   ├── 08-solving-linear-inequalities.md
│   ├── 09-compound-inequalities-solution-sets-and-interval-notation.md
│   ├── 10-absolute-value-equations-and-inequalities.md
│   ├── 11-systems-of-linear-equations-by-substitution.md
│   ├── 12-systems-of-linear-equations-by-elimination.md
│   ├── 13-special-cases-no-solution-and-infinitely-many-solutions.md
│   ├── 14-three-variable-systems-and-the-bridge-to-matrices.md
│   ├── 15-checking-solutions-and-extraneous-results.md
│   ├── PROMPT-Equations-Inequalities-and-Systems.md
│   ├── README.md
│   └── practice-questions.md
├── 05-Exponents-Roots-and-Growth/
│   ├── Projects/
│   │   ├── 01-exponential-growth-and-scale-visualizer.md
│   │   └── README.md
│   ├── 01-powers-bases-exponents-squares-and-cubes.md
│   ├── 02-exponent-laws.md
│   ├── 03-zero-and-negative-exponents.md
│   ├── 04-fractional-exponents-roots-and-radicals.md
│   ├── 05-scientific-notation-and-orders-of-magnitude.md
│   ├── 06-compound-growth-and-decay-linear-versus-exponential.md
│   ├── 07-the-constant-e-and-continuous-growth.md
│   ├── 08-powers-of-two-and-binary-scale.md
│   ├── PROMPT-Exponents-Roots-and-Growth.md
│   ├── README.md
│   └── practice-questions.md
├── 06-Logarithms/
│   ├── Projects/
│   │   ├── 01-logarithm-scale-and-log-likelihood-demo.md
│   │   └── README.md
│   ├── 01-what-logarithms-mean-and-the-exponent-log-relationship.md
│   ├── 02-common-and-natural-logarithms-and-evaluating-them.md
│   ├── 03-logarithm-rules.md
│   ├── 04-change-of-base.md
│   ├── 05-solving-exponential-equations.md
│   ├── 06-solving-logarithmic-equations.md
│   ├── 07-logarithmic-scales.md
│   ├── 08-why-logarithms-matter-in-machine-learning.md
│   ├── PROMPT-Logarithms.md
│   ├── README.md
│   └── practice-questions.md
├── 07-Functions-and-Graphs/
│   ├── Projects/
│   │   ├── 01-function-plotter-and-activation-gallery.md
│   │   └── README.md
│   ├── 01-cartesian-plane-plotting-and-reading-coordinates.md
│   ├── 02-what-a-function-is-and-function-notation.md
│   ├── 03-domain-and-range.md
│   ├── 04-variables-parameters-and-independent-versus-dependent.md
│   ├── 05-evaluating-and-piecewise-functions.md
│   ├── 06-linear-functions-slope-intercepts-and-line-equations.md
│   ├── 07-intersection-of-lines-and-the-geometry-of-linear-systems.md
│   ├── 08-quadratic-functions-and-parabolas.md
│   ├── 09-polynomial-functions-and-end-behavior.md
│   ├── 10-exponential-and-logarithmic-functions-and-graphs.md
│   ├── 11-function-composition.md
│   ├── 12-inverse-functions.md
│   ├── 13-increasing-decreasing-extrema-and-curvature-intuition.md
│   ├── 14-activation-shapes-sigmoid-tanh-and-relu.md
│   ├── 15-transformations-and-how-parameters-change-graphs.md
│   ├── 16-reading-graph-scales-and-avoiding-misleading-charts.md
│   ├── PROMPT-Functions-and-Graphs.md
│   ├── README.md
│   └── practice-questions.md
├── 08-Geometry-and-Trigonometry/
│   ├── Projects/
│   │   ├── 01-trigonometry-and-unit-circle-visualizer.md
│   │   └── README.md
│   ├── 01-points-lines-angles-parallel-and-perpendicular.md
│   ├── 02-triangles-and-the-pythagorean-theorem.md
│   ├── 03-distance-midpoint-and-circles-in-the-plane.md
│   ├── 04-degrees-and-radians.md
│   ├── 05-right-triangle-trigonometry.md
│   ├── 06-unit-circle-and-basic-trigonometric-identities.md
│   ├── 07-periodic-functions-and-sine-cosine-graphs.md
│   ├── PROMPT-Geometry-and-Trigonometry.md
│   ├── README.md
│   └── practice-questions.md
├── 09-Vectors-as-Arrows-and-Data-Points/
│   ├── Projects/
│   │   ├── 01-vector-arrows-and-angle-explorer.md
│   │   └── README.md
│   ├── 01-scalars-vectors-and-points-versus-vectors.md
│   ├── 02-vector-addition-subtraction-and-scaling-in-2d-and-3d.md
│   ├── 03-vector-length-and-unit-vectors.md
│   ├── 04-direction-angle-and-perpendicularity-intuition.md
│   ├── 05-data-points-as-lists-of-numbers.md
│   ├── PROMPT-Vectors-as-Arrows-and-Data-Points.md
│   ├── README.md
│   └── practice-questions.md
├── 10-Sequences-Series-and-Summation/
│   ├── Projects/
│   │   ├── 01-sequence-and-series-explorer.md
│   │   └── README.md
│   ├── 01-sequences-terms-indices-and-explicit-formulas.md
│   ├── 02-arithmetic-sequences.md
│   ├── 03-geometric-sequences.md
│   ├── 04-recursive-definitions-and-recurrence-relations.md
│   ├── 05-summation-and-product-notation.md
│   ├── 06-finite-sums-and-series-formulas.md
│   ├── 07-infinite-sequences-and-the-idea-of-convergence.md
│   ├── 08-infinite-geometric-series.md
│   ├── PROMPT-Sequences-Series-and-Summation.md
│   ├── README.md
│   └── practice-questions.md
├── 11-Counting-and-Combinatorics/
│   ├── Projects/
│   │   ├── 01-counting-and-combinatorics-calculator.md
│   │   └── README.md
│   ├── 01-the-counting-principle.md
│   ├── 02-factorials-and-permutations.md
│   ├── 03-combinations-and-binomial-coefficients.md
│   ├── 04-pascals-triangle-and-the-binomial-theorem.md
│   ├── 05-inclusion-exclusion.md
│   ├── 06-counting-with-restrictions-and-combinatorial-explosion.md
│   ├── PROMPT-Counting-and-Combinatorics.md
│   ├── README.md
│   └── practice-questions.md
├── 12-Descriptive-Statistics-Basics/
│   ├── Projects/
│   │   ├── 01-descriptive-statistics-from-scratch.md
│   │   └── README.md
│   ├── 01-types-of-data.md
│   ├── 02-mean-median-and-mode.md
│   ├── 03-range-variance-and-standard-deviation-of-data.md
│   ├── 04-quartiles-percentiles-iqr-and-outliers.md
│   ├── 05-histograms-box-plots-and-scatter-plots.md
│   ├── 06-z-scores-and-standardization.md
│   ├── 07-population-sample-and-common-data-pitfalls.md
│   ├── PROMPT-Descriptive-Statistics-Basics.md
│   ├── README.md
│   └── practice-questions.md
├── 13-Limits-and-Rates-of-Change-Bridge/
│   ├── Projects/
│   │   ├── 01-secant-to-tangent-limit-visualizer.md
│   │   └── README.md
│   ├── 01-average-rate-of-change-and-secant-lines.md
│   ├── 02-instantaneous-rate-of-change-and-tangent-slope-intuition.md
│   ├── 03-limits-of-functions-numerically-and-graphically.md
│   ├── 04-limit-laws-and-continuity-intuition.md
│   ├── 05-limits-at-infinity-and-asymptotes.md
│   ├── 06-accumulation-and-area-under-a-curve-intuition.md
│   ├── PROMPT-Limits-and-Rates-of-Change-Bridge.md
│   ├── README.md
│   └── practice-questions.md
├── 14-Complex-Numbers-Optional/
│   ├── Projects/
│   │   ├── 01-complex-plane-visualizer.md
│   │   └── README.md
│   ├── 01-imaginary-unit-and-complex-arithmetic.md
│   ├── 02-complex-plane-modulus-and-conjugate.md
│   ├── 03-polar-form-and-eulers-formula-introduction.md
│   ├── PROMPT-Complex-Numbers-Optional.md
│   ├── README.md
│   └── practice-questions.md
├── 15-Mathematical-Notation-Reasoning-and-Math-in-Code/
│   ├── Projects/
│   │   ├── 01-formula-to-python-translation-workbook.md
│   │   └── README.md
│   ├── 01-symbols-for-equality-approximation-and-inequality.md
│   ├── 02-greek-letters-in-mathematics.md
│   ├── 03-subscripts-superscripts-and-indices.md
│   ├── 04-reading-formulas-left-to-right-assumptions-and-conditions.md
│   ├── 05-basic-logic-if-then-counterexamples-and-necessary-vs-sufficient.md
│   ├── 06-problem-solving-strategy-and-verifying-answers.md
│   ├── 07-reading-research-style-mathematics.md
│   ├── 08-translating-formulas-into-python-and-numpy.md
│   ├── PROMPT-Mathematical-Notation-Reasoning-and-Math-in-Code.md
│   ├── README.md
│   └── practice-questions.md
└── README.md
```

## Stage 4B — Mathematics for Machine Learning

```text
Stage 4B — Mathematics for Machine Learning/
├── 00-Stage-4-Overview/
│   ├── Projects/
│   │   ├── 01-math-for-ml-notebook-library.md
│   │   └── README.md
│   ├── README.md
│   ├── SYLLABUS-00-Stage-4-Overview.md
│   ├── how-4b-connects-to-4a-and-4c.md
│   └── learning-plan.md
├── 01-Vectors-Dot-Product-and-Norms/
│   ├── Projects/
│   │   ├── 01-vector-operations-library-in-numpy.md
│   │   ├── 02-geometry-of-dot-product-explorer.md
│   │   └── README.md
│   ├── 01-vectors-in-n-dimensions-and-numpy-arrays.md
│   ├── 02-dot-product-and-its-geometric-meaning.md
│   ├── 03-projection-onto-a-vector.md
│   ├── 04-norms-l1-l2-and-infinity-and-distance.md
│   ├── 05-linear-combinations-span-and-linear-independence.md
│   ├── README.md
│   ├── SYLLABUS-01-Vectors-Dot-Product-and-Norms.md
│   └── practice-questions.md
├── 02-Matrices-and-Linear-Transformations/
│   ├── Projects/
│   │   ├── 01-matrix-operations-from-scratch.md
│   │   ├── 02-gaussian-elimination-solver.md
│   │   ├── 03-linear-transformation-visualizer.md
│   │   └── README.md
│   ├── 01-matrices-as-data-tables-and-linear-maps.md
│   ├── 02-matrix-vector-and-matrix-matrix-multiplication.md
│   ├── 03-transpose-identity-and-special-matrices.md
│   ├── 04-matrix-shapes-broadcasting-and-batching.md
│   ├── 05-linear-transformations-rotation-scaling-and-shear.md
│   ├── 06-solving-ax-equals-b-and-gaussian-elimination.md
│   ├── 07-determinants-and-invertibility.md
│   ├── 08-matrix-inverse-and-when-it-fails.md
│   ├── 09-rank-and-column-space-intuition.md
│   ├── README.md
│   ├── SYLLABUS-02-Matrices-and-Linear-Transformations.md
│   └── practice-questions.md
├── 03-Eigenvalues-SVD-and-Low-Rank-Structure/
│   ├── Projects/
│   │   ├── 01-eigenvalue-power-iteration.md
│   │   ├── 02-image-compression-with-svd.md
│   │   └── README.md
│   ├── 01-eigenvalues-and-eigenvectors.md
│   ├── 02-eigendecomposition-and-matrix-powers.md
│   ├── 03-singular-value-decomposition-intuition-and-computation.md
│   ├── 04-low-rank-approximation.md
│   ├── 05-matrix-norms-frobenius-and-spectral.md
│   ├── README.md
│   ├── SYLLABUS-03-Eigenvalues-SVD-and-Low-Rank-Structure.md
│   └── practice-questions.md
├── 04-Similarity-Distance-and-Embedding-Geometry/
│   ├── Projects/
│   │   ├── 01-word-vector-similarity-explorer.md
│   │   ├── 02-curse-of-dimensionality-experiments.md
│   │   └── README.md
│   ├── 01-cosine-similarity.md
│   ├── 02-euclidean-versus-cosine-versus-dot-product-similarity.md
│   ├── 03-high-dimensional-geometry-and-the-curse-of-dimensionality.md
│   ├── README.md
│   ├── SYLLABUS-04-Similarity-Distance-and-Embedding-Geometry.md
│   └── practice-questions.md
├── 05-Derivatives-and-Single-Variable-Optimization/
│   ├── Projects/
│   │   ├── 01-symbolic-and-numerical-derivative-comparison.md
│   │   ├── 02-numerical-gradient-checker.md
│   │   └── README.md
│   ├── 01-the-derivative-from-limits-slope-of-a-curve.md
│   ├── 02-derivative-rules.md
│   ├── 03-derivatives-of-exponential-logarithmic-and-trigonometric-functions.md
│   ├── 04-the-chain-rule.md
│   ├── 05-derivatives-of-sigmoid-tanh-and-relu.md
│   ├── 06-second-derivatives-and-curvature.md
│   ├── 07-finding-minima-and-maxima.md
│   ├── 08-numerical-versus-analytical-derivatives-and-gradient-checking.md
│   ├── README.md
│   └── practice-questions.md
├── 06-Integral-Calculus/
│   ├── Projects/
│   │   ├── 01-numerical-integration-toolkit.md
│   │   ├── 02-area-under-a-density-curve-lab.md
│   │   └── README.md
│   ├── 01-antiderivatives-and-the-indefinite-integral.md
│   ├── 02-definite-integrals-and-the-fundamental-theorem-of-calculus.md
│   ├── 03-integration-by-substitution-and-by-parts.md
│   ├── 04-improper-integrals.md
│   ├── 05-numerical-integration-riemann-sums-and-the-trapezoid-rule.md
│   ├── 06-double-integrals-introduction.md
│   ├── README.md
│   └── practice-questions.md
├── 07-Multivariable-Calculus-and-Gradients/
│   ├── Projects/
│   │   ├── 01-gradient-field-and-contour-plotter.md
│   │   ├── 02-backpropagation-by-hand-on-a-tiny-network.md
│   │   └── README.md
│   ├── 01-functions-of-several-variables-and-level-sets.md
│   ├── 02-partial-derivatives.md
│   ├── 03-gradients-and-the-direction-of-steepest-ascent.md
│   ├── 04-computational-graphs-and-backpropagation-by-hand.md
│   ├── README.md
│   └── practice-questions.md
├── 08-Optimization-Fundamentals/
│   ├── Projects/
│   │   ├── 01-gradient-descent-visualizer.md
│   │   ├── 02-optimizer-comparison-sgd-momentum-adam.md
│   │   └── README.md
│   ├── 01-loss-functions-mse-mae-and-huber.md
│   ├── 02-gradient-descent.md
│   ├── 03-learning-rate-and-convergence.md
│   ├── 04-stochastic-and-mini-batch-gradient-descent.md
│   ├── 05-momentum-rmsprop-and-adam-intuition.md
│   ├── README.md
│   └── practice-questions.md
├── 09-Probability-Fundamentals/
│   ├── Projects/
│   │   ├── 01-probability-simulations.md
│   │   ├── 02-bayes-spam-filter-by-hand.md
│   │   └── README.md
│   ├── 01-sample-spaces-events-and-probability-axioms.md
│   ├── 02-conditional-probability-and-the-multiplication-rule.md
│   ├── 03-law-of-total-probability-and-bayes-theorem.md
│   ├── 04-independence.md
│   ├── 05-random-variables-discrete-and-continuous.md
│   ├── 06-pmf-pdf-and-cdf.md
│   ├── 07-expectation-and-variance.md
│   ├── 08-covariance-and-correlation.md
│   ├── README.md
│   └── practice-questions.md
├── 10-Common-Distributions/
│   ├── Projects/
│   │   ├── 01-distribution-gallery-and-fitting.md
│   │   ├── 02-poisson-event-rate-simulator.md
│   │   └── README.md
│   ├── 01-bernoulli-and-binomial.md
│   ├── 02-categorical-multinomial-and-softmax.md
│   ├── 03-poisson-distribution.md
│   ├── 04-uniform-and-exponential-distributions.md
│   ├── 05-normal-distribution.md
│   ├── 06-beta-and-dirichlet-distributions-in-outline.md
│   ├── README.md
│   └── practice-questions.md
├── 11-Sampling-and-Limit-Theorems/
│   ├── Projects/
│   │   ├── 01-sampling-from-a-next-token-distribution.md
│   │   ├── 02-clt-and-lln-simulation-lab.md
│   │   └── README.md
│   ├── 01-random-sampling-and-inverse-transform-sampling.md
│   ├── 02-law-of-large-numbers.md
│   ├── 03-central-limit-theorem.md
│   ├── 04-sampling-distributions-and-standard-error.md
│   ├── README.md
│   └── practice-questions.md
├── 12-Inferential-Statistics-for-Experiments-and-Evals/
│   ├── Projects/
│   │   ├── 01-is-prompt-b-really-better.md
│   │   ├── 02-bootstrap-confidence-interval-lab.md
│   │   ├── 03-ab-test-analysis-report.md
│   │   └── README.md
│   ├── 01-confidence-intervals.md
│   ├── 02-bootstrap-resampling.md
│   ├── 03-hypothesis-testing-and-p-values.md
│   ├── 04-t-tests-and-paired-tests-for-model-comparison.md
│   ├── 05-tests-for-proportions-and-ab-testing.md
│   ├── 06-effect-size-sample-size-and-statistical-power.md
│   ├── 07-correlation-versus-causation-confounding-and-sampling-bias.md
│   ├── README.md
│   └── practice-questions.md
├── 13-Information-Theory-for-ML/
│   ├── Projects/
│   │   ├── 01-compute-perplexity-of-text.md
│   │   ├── 02-entropy-and-kl-explorer.md
│   │   └── README.md
│   ├── 01-information-and-surprise.md
│   ├── 02-entropy.md
│   ├── 03-cross-entropy-as-a-loss.md
│   ├── 04-kl-divergence.md
│   ├── 05-perplexity.md
│   ├── README.md
│   └── practice-questions.md
├── 14-Linear-Models-Mathematics/
│   ├── Projects/
│   │   ├── 01-linear-regression-from-scratch-in-numpy.md
│   │   ├── 02-logistic-regression-from-scratch.md
│   │   ├── 03-ridge-versus-lasso-comparison.md
│   │   └── README.md
│   ├── 01-linear-regression-design-matrix-and-residuals.md
│   ├── 02-the-normal-equation-and-closed-form-solution.md
│   ├── 03-gradient-descent-versus-closed-form-for-linear-regression.md
│   ├── 04-logistic-regression-sigmoid-and-log-loss-gradient.md
│   ├── 05-ridge-and-lasso-regularization-mathematics.md
│   ├── README.md
│   └── practice-questions.md
└── README.md
```

## Stage 4C — Advanced Mathematics for Machine Learning — Deep Learning

```text
Stage 4C — Advanced Mathematics for Machine Learning — Deep Learning/
├── 00-Stage-4C-Overview/
│   ├── Projects/
│   │   ├── 01-deep-learning-math-derivation-notebook.md
│   │   └── README.md
│   ├── README.md
│   ├── how-4c-connects-to-4b-and-the-ml-stages.md
│   └── learning-plan.md
├── 01-Advanced-Linear-Algebra/
│   ├── Projects/
│   │   ├── 01-gram-schmidt-qr-and-cholesky-from-scratch.md
│   │   ├── 02-pca-from-scratch-with-svd.md
│   │   ├── 03-einsum-workout-for-transformer-operations.md
│   │   └── README.md
│   ├── 01-vector-spaces-subspaces-basis-and-change-of-basis.md
│   ├── 02-four-fundamental-subspaces-and-the-rank-nullity-theorem.md
│   ├── 03-orthogonality-orthonormal-bases-and-gram-schmidt.md
│   ├── 04-orthogonal-projections-onto-subspaces-and-the-geometry-of-least-squares.md
│   ├── 05-lu-qr-and-cholesky-decompositions.md
│   ├── 06-the-spectral-theorem-for-symmetric-matrices.md
│   ├── 07-positive-definite-and-positive-semidefinite-matrices.md
│   ├── 08-svd-derivation-pseudoinverse-and-the-eckart-young-theorem.md
│   ├── 09-pca-mathematical-derivation.md
│   ├── 10-tensors-index-notation-and-einsum.md
│   ├── README.md
│   └── practice-questions.md
├── 02-Multivariable-and-Matrix-Calculus/
│   ├── Projects/
│   │   ├── 01-jacobian-and-hessian-numerical-lab.md
│   │   ├── 02-taylor-approximation-visualizer.md
│   │   └── README.md
│   ├── 01-the-multivariable-chain-rule.md
│   ├── 02-directional-derivatives-and-gradient-geometry.md
│   ├── 03-jacobian-matrices.md
│   ├── 04-hessian-matrices-and-second-order-derivatives.md
│   ├── 05-taylor-series-and-multivariate-taylor-approximation.md
│   ├── 06-matrix-calculus-identities.md
│   ├── 07-vectorization-and-kronecker-products-optional.md
│   ├── README.md
│   └── practice-questions.md
├── 03-Optimization-Theory-and-Training-Algorithms/
│   ├── Projects/
│   │   ├── 01-convex-versus-non-convex-landscape-explorer.md
│   │   ├── 02-optimizer-from-scratch-adamw-and-schedules.md
│   │   ├── 03-newton-and-lbfgs-comparison.md
│   │   └── README.md
│   ├── 01-convex-sets-and-convex-functions.md
│   ├── 02-first-and-second-order-optimality-conditions.md
│   ├── 03-constrained-optimization-and-lagrange-multipliers.md
│   ├── 04-kkt-conditions-and-duality-introduction.md
│   ├── 05-convergence-rates-of-gradient-descent.md
│   ├── 06-conditioning-and-ill-conditioned-problems.md
│   ├── 07-newtons-method-and-quasi-newton-lbfgs.md
│   ├── 08-proximal-methods-and-coordinate-descent.md
│   ├── 09-saddle-points-and-non-convex-landscapes.md
│   ├── 10-stochastic-optimization-theory-and-gradient-noise.md
│   ├── 11-optimizers-in-full-nesterov-rmsprop-adam-and-adamw.md
│   ├── 12-learning-rate-schedules-warmup-and-decay.md
│   ├── README.md
│   └── practice-questions.md
├── 04-Advanced-Probability/
│   ├── Projects/
│   │   ├── 01-multivariate-gaussian-explorer.md
│   │   ├── 02-monte-carlo-and-importance-sampling-lab.md
│   │   ├── 03-metropolis-hastings-sampler.md
│   │   └── README.md
│   ├── 01-joint-distributions-and-marginalization.md
│   ├── 02-conditional-distributions-and-conditional-independence.md
│   ├── 03-covariance-matrices.md
│   ├── 04-the-multivariate-gaussian-distribution.md
│   ├── 05-conditional-expectation.md
│   ├── 06-law-of-total-expectation-and-law-of-total-variance.md
│   ├── 07-change-of-variables-for-random-variables.md
│   ├── 08-concentration-inequalities-markov-chebyshev-and-hoeffding.md
│   ├── 09-markov-chains-and-stationary-distributions.md
│   ├── 10-monte-carlo-estimation-and-importance-sampling.md
│   ├── 11-mcmc-metropolis-hastings-and-gibbs-sampling.md
│   ├── README.md
│   └── practice-questions.md
├── 05-Statistical-Estimation-and-Bayesian-Inference/
│   ├── Projects/
│   │   ├── 01-mle-and-map-estimation-lab.md
│   │   ├── 02-bayesian-coin-and-conjugate-update-demo.md
│   │   ├── 03-gaussian-mixture-em-from-scratch.md
│   │   └── README.md
│   ├── 01-likelihood-and-log-likelihood.md
│   ├── 02-maximum-likelihood-estimation.md
│   ├── 03-properties-of-estimators-bias-variance-and-consistency.md
│   ├── 04-fisher-information-and-the-cramer-rao-bound.md
│   ├── 05-maximum-a-posteriori-estimation-and-priors-as-regularization.md
│   ├── 06-bayesian-inference-posteriors-and-conjugate-priors.md
│   ├── 07-empirical-risk-expected-risk-and-generalization.md
│   ├── 08-uncertainty-quantification-aleatoric-epistemic-and-calibration.md
│   ├── 09-the-exponential-family-and-generalized-linear-models.md
│   ├── 10-expectation-maximization-and-gaussian-mixture-models.md
│   ├── README.md
│   └── practice-questions.md
├── 06-Advanced-Information-Theory/
│   ├── Projects/
│   │   ├── 01-mutual-information-and-divergence-calculator.md
│   │   └── README.md
│   ├── 01-joint-and-conditional-entropy.md
│   ├── 02-mutual-information.md
│   ├── 03-properties-of-cross-entropy-and-kl-divergence.md
│   ├── 04-jensen-shannon-divergence-and-other-divergences.md
│   ├── 05-differential-entropy-and-the-maximum-entropy-principle-optional.md
│   ├── README.md
│   └── practice-questions.md
├── 07-Mathematics-of-Deep-Learning-Training/
│   ├── Projects/
│   │   ├── 01-mini-autograd-engine.md
│   │   ├── 02-initialization-and-gradient-flow-experiments.md
│   │   ├── 03-normalization-layers-from-scratch.md
│   │   └── README.md
│   ├── 01-vector-jacobian-and-jacobian-vector-products.md
│   ├── 02-reverse-mode-automatic-differentiation.md
│   ├── 03-forward-mode-automatic-differentiation.md
│   ├── 04-backpropagation-through-layers-in-matrix-form.md
│   ├── 05-softmax-and-cross-entropy-gradients.md
│   ├── 06-modern-activations-gelu-silu-and-gradient-flow.md
│   ├── 07-vanishing-and-exploding-gradients.md
│   ├── 08-weight-initialization-xavier-and-he.md
│   ├── 09-normalization-mathematics-batchnorm-layernorm-and-rmsnorm.md
│   ├── 10-regularization-mathematics-dropout-and-label-smoothing.md
│   ├── 11-floating-point-arithmetic-and-numerical-error.md
│   ├── 12-numerical-stability-logsumexp-and-stable-softmax.md
│   ├── README.md
│   └── practice-questions.md
├── 08-Mathematics-of-Convolutional-and-Recurrent-Models/
│   ├── Projects/
│   │   ├── 01-convolution-from-scratch-and-fft-check.md
│   │   ├── 02-bptt-gradient-flow-in-a-simple-rnn.md
│   │   └── README.md
│   ├── 01-convolution-versus-cross-correlation-and-output-shapes.md
│   ├── 02-fourier-transform-and-the-convolution-theorem.md
│   ├── 03-pooling-receptive-fields-and-backpropagation-through-convolution.md
│   ├── 04-recurrent-networks-and-backpropagation-through-time.md
│   ├── 05-lstm-and-gru-gating-mathematics.md
│   ├── README.md
│   └── practice-questions.md
├── 09-Mathematics-of-Transformers-and-Representations/
│   ├── Projects/
│   │   ├── 01-attention-from-scratch-in-numpy.md
│   │   ├── 02-rope-and-positional-encoding-visualizer.md
│   │   ├── 03-lora-low-rank-update-demo.md
│   │   └── README.md
│   ├── 01-scaled-dot-product-attention-as-matrix-operations.md
│   ├── 02-multi-head-attention-and-masking.md
│   ├── 03-positional-encodings-sinusoidal-and-rotary-rope.md
│   ├── 04-softmax-temperature-and-sampling-distributions.md
│   ├── 05-geometry-of-learned-representations-and-anisotropy.md
│   ├── 06-lora-and-low-rank-weight-updates.md
│   ├── 07-random-projections-and-the-johnson-lindenstrauss-lemma.md
│   ├── 08-singular-value-spectra-of-weight-matrices.md
│   ├── README.md
│   └── practice-questions.md
├── 10-Mathematics-of-Generative-and-Latent-Variable-Models/
│   ├── Projects/
│   │   ├── 01-vae-elbo-on-a-toy-dataset.md
│   │   ├── 02-diffusion-forward-process-visualizer.md
│   │   └── README.md
│   ├── 01-latent-variable-models-and-marginal-likelihood.md
│   ├── 02-variational-inference-and-the-elbo.md
│   ├── 03-the-reparameterization-trick-and-the-vae-objective.md
│   ├── 04-gans-and-adversarial-objectives.md
│   ├── 05-diffusion-models-forward-process-and-noise-prediction.md
│   ├── 06-autoregressive-factorization-and-sequence-likelihood.md
│   ├── README.md
│   └── practice-questions.md
└── README.md
```

## Stage 5A — Machine Learning Foundation

```text
Stage 5A — Machine Learning Foundation/
├── 00-Stage-Overview/
│   ├── Projects/
│   │   ├── 01-learning-environment-smoke-test.md
│   │   └── README.md
│   ├── README.md
│   ├── learning-plan.md
│   ├── prerequisites-and-success-criteria.md
│   └── tools-and-environment-setup.md
├── 01-Machine-Learning-Fundamentals-and-Problem-Framing/
│   ├── Projects/
│   │   ├── 01-ml-problem-framing-and-baseline.md
│   │   └── README.md
│   ├── 01-rules-vs-machine-learning-and-ai-ml-dl.md
│   ├── 02-learning-paradigms-and-task-types.md
│   ├── 03-features-labels-parameters-and-hyperparameters.md
│   ├── 04-training-inference-and-generalization.md
│   ├── 05-batch-online-and-incremental-learning.md
│   ├── 06-parametric-vs-nonparametric-and-generative-vs-discriminative-models.md
│   ├── 07-business-problem-framing-baselines-and-success-metrics.md
│   ├── 08-ml-lifecycle-and-when-not-to-use-ml.md
│   ├── README.md
│   └── practice-questions.md
├── 02-Data-Understanding-EDA-and-Data-Quality/
│   ├── Projects/
│   │   ├── 01-eda-and-data-quality-report.md
│   │   └── README.md
│   ├── 01-dataset-structure-and-variable-types.md
│   ├── 02-univariate-eda.md
│   ├── 03-bivariate-and-multivariate-eda.md
│   ├── 04-missing-data-duplicates-and-invalid-values.md
│   ├── 05-outlier-investigation.md
│   ├── 06-target-distribution-and-class-imbalance-diagnosis.md
│   ├── 07-sampling-bias-representativeness-and-correlation-pitfalls.md
│   ├── 08-dataset-shift-and-data-quality-validation.md
│   ├── 09-data-dictionaries-and-dataset-documentation.md
│   ├── README.md
│   └── practice-questions.md
├── 03-Data-Preprocessing-and-Feature-Engineering/
│   ├── Projects/
│   │   ├── 01-reusable-preprocessing-pipeline.md
│   │   ├── 02-data-leakage-hunt.md
│   │   └── README.md
│   ├── 01-train-validation-test-and-splitting-strategies.md
│   ├── 02-missing-value-imputation.md
│   ├── 03-outlier-treatment-and-robust-transformations.md
│   ├── 04-categorical-encoding-one-hot-ordinal-and-target.md
│   ├── 05-high-cardinality-features-hashing-and-frequency-encoding.md
│   ├── 06-standardization-normalization-and-power-transformations.md
│   ├── 07-datetime-and-cyclical-features.md
│   ├── 08-grouped-and-time-window-aggregate-features.md
│   ├── 09-interactions-polynomial-features-and-binning.md
│   ├── 10-text-feature-extraction-introduction.md
│   ├── 11-scikit-learn-pipelines-and-column-transformers.md
│   ├── 12-data-leakage-and-training-serving-skew.md
│   ├── 13-custom-transformers-and-feature-validation.md
│   ├── README.md
│   └── practice-questions.md
├── 04-Regression-Algorithms/
│   ├── Projects/
│   │   ├── 01-regression-model-benchmark.md
│   │   └── README.md
│   ├── 01-regression-baselines.md
│   ├── 02-linear-regression-and-assumptions.md
│   ├── 03-coefficients-intercepts-and-residual-analysis.md
│   ├── 04-polynomial-regression-and-nonlinearity.md
│   ├── 05-ridge-lasso-and-elastic-net.md
│   ├── 06-robust-regression-and-outlier-sensitivity.md
│   ├── 07-categorical-and-interaction-terms.md
│   ├── 08-generalized-linear-models-for-count-and-skewed-targets.md
│   ├── 09-log-ordinal-and-bounded-target-handling.md
│   ├── 10-quantile-regression-and-prediction-intervals.md
│   ├── README.md
│   └── practice-questions.md
├── 05-Classification-Algorithms/
│   ├── Projects/
│   │   ├── 01-classification-algorithm-comparison.md
│   │   └── README.md
│   ├── 01-binary-multiclass-and-multilabel-classification.md
│   ├── 02-logistic-regression-and-decision-boundaries.md
│   ├── 03-multiclass-strategies-and-softmax.md
│   ├── 04-probability-scores-and-default-thresholds.md
│   ├── 05-knn-distance-metrics-and-feature-scaling.md
│   ├── 06-naive-bayes-and-conditional-independence.md
│   ├── 07-support-vector-machines-margins-and-kernels.md
│   ├── 08-discriminant-analysis-lda-and-qda.md
│   ├── 09-computational-cost-and-failure-modes-of-classical-algorithms.md
│   ├── README.md
│   └── practice-questions.md
├── 06-Model-Evaluation-and-Metrics/
│   ├── Projects/
│   │   ├── 01-metric-selection-and-evaluation-report.md
│   │   └── README.md
│   ├── 01-training-validation-and-test-performance.md
│   ├── 02-confusion-matrix-and-the-limits-of-accuracy.md
│   ├── 03-precision-recall-f1-and-averaging.md
│   ├── 04-specificity-sensitivity-and-balanced-accuracy.md
│   ├── 05-roc-auc-and-precision-recall-curves.md
│   ├── 06-log-loss-and-probabilistic-scoring.md
│   ├── 07-regression-metrics-and-mape-limitations.md
│   ├── 08-subgroup-metrics-and-confidence-intervals.md
│   ├── 09-metric-selection-for-business-outcomes.md
│   ├── README.md
│   └── practice-questions.md
├── 07-Generalization-and-Model-Selection/
│   ├── Projects/
│   │   ├── 01-diagnose-an-overfit-model.md
│   │   └── README.md
│   ├── 01-underfitting-overfitting-and-generalization-error.md
│   ├── 02-bias-variance-tradeoff-in-practice.md
│   ├── 03-cross-validation-fundamentals.md
│   ├── 04-stratified-group-and-time-aware-validation.md
│   ├── 05-grid-search-and-randomized-search.md
│   ├── 06-learning-and-validation-curves.md
│   ├── 07-pipelines-in-cross-validation-and-leakage-safe-tuning.md
│   ├── README.md
│   └── practice-questions.md
├── 08-Trees-Ensembles-and-Gradient-Boosting/
│   ├── Projects/
│   │   ├── 01-tabular-model-benchmark.md
│   │   └── README.md
│   ├── 01-decision-tree-structure-and-splitting.md
│   ├── 02-gini-entropy-information-gain-and-variance-reduction.md
│   ├── 03-tree-depth-pruning-and-leaf-constraints.md
│   ├── 04-random-forests-and-bagging.md
│   ├── 05-extra-trees-and-ensemble-diversity.md
│   ├── 06-voting-stacking-and-blending.md
│   ├── 07-boosting-vs-bagging.md
│   ├── 08-gradient-boosting-fundamentals.md
│   ├── 09-xgboost-lightgbm-and-catboost.md
│   ├── 10-monotonic-constraints-and-categorical-handling-in-boosting.md
│   ├── 11-hyperparameter-tuning-and-missing-value-handling.md
│   ├── 12-feature-importance-introduction.md
│   ├── README.md
│   └── practice-questions.md
├── 09-Unsupervised-Learning-and-Clustering/
│   ├── Projects/
│   │   ├── 01-customer-segmentation.md
│   │   └── README.md
│   ├── 01-what-unsupervised-learning-can-establish.md
│   ├── 02-k-means-initialization-and-cluster-count.md
│   ├── 03-hierarchical-clustering-and-dendrograms.md
│   ├── 04-dbscan-and-hdbscan.md
│   ├── 05-gaussian-mixture-models-and-em-intuition.md
│   ├── 06-clustering-metrics-and-stability.md
│   ├── 07-cluster-interpretation-and-profiling.md
│   ├── README.md
│   └── practice-questions.md
├── 10-Classical-NLP-and-Text-Classification/
│   ├── Projects/
│   │   ├── 01-support-ticket-classifier-baseline.md
│   │   └── README.md
│   ├── 01-text-normalization-and-cleaning.md
│   ├── 02-tokenization-vocabulary-and-n-grams.md
│   ├── 03-stop-words-stemming-and-lemmatization.md
│   ├── 04-bag-of-words-and-tf-idf.md
│   ├── 05-sparse-feature-matrices.md
│   ├── 06-naive-bayes-logistic-regression-and-linear-svm-for-text.md
│   ├── 07-text-evaluation-and-error-analysis.md
│   ├── 08-rare-terms-vocabulary-drift-and-pipeline.md
│   ├── README.md
│   └── practice-questions.md
├── 11-Experiment-Tracking-and-Reproducibility-Basics/
│   ├── Projects/
│   │   ├── 01-tracked-experiment-suite.md
│   │   └── README.md
│   ├── 01-why-experiments-fail-to-reproduce-and-random-seeds.md
│   ├── 02-dataset-snapshots-and-code-config-versioning-basics.md
│   ├── 03-tracking-runs-with-a-simple-logger-and-experiment-reports.md
│   ├── 04-systematic-run-comparison-and-avoiding-cherry-picking.md
│   ├── README.md
│   └── practice-questions.md
├── 12-Error-Analysis-Debugging-and-Model-Improvement/
│   ├── Projects/
│   │   ├── 01-error-analysis-and-improvement-report.md
│   │   └── README.md
│   ├── 01-confusion-matrix-driven-error-analysis.md
│   ├── 02-false-positive-and-false-negative-inspection.md
│   ├── 03-performance-slices-and-subgroups.md
│   ├── 04-failure-taxonomies-and-edge-cases.md
│   ├── 05-label-noise-and-data-errors.md
│   ├── 06-data-centric-vs-model-centric-improvement.md
│   ├── 07-ablation-studies-and-impact-prioritization.md
│   ├── README.md
│   └── practice-questions.md
├── 13-Stage-5A-Capstone/
│   ├── 01-end-to-end-classification-with-error-analysis.md
│   ├── 02-foundation-capstone-and-reproducible-report.md
│   ├── 03-stage-5a-readiness-assessment.md
│   ├── README.md
│   └── project-standards-and-rubric.md
└── README.md
```

## Stage 5B — Advanced Machine Learning

```text
Stage 5B — Advanced Machine Learning/
├── 00-Stage-Overview/
│   ├── Projects/
│   │   ├── 01-advanced-experiment-design.md
│   │   └── README.md
│   ├── README.md
│   ├── learning-plan.md
│   └── prerequisites-and-exit-criteria.md
├── 01-Advanced-Validation-and-Model-Selection/
│   ├── Projects/
│   │   ├── 01-compute-aware-model-selection.md
│   │   └── README.md
│   ├── 01-nested-validation-and-selection-bias.md
│   ├── 02-distribution-aware-validation-and-adversarial-validation.md
│   ├── 03-bayesian-hyperparameter-optimization.md
│   ├── 04-compute-aware-search-and-multi-fidelity-tuning.md
│   ├── 05-robustness-and-sensitivity-analysis.md
│   ├── 06-comparing-models-across-folds-and-datasets.md
│   ├── README.md
│   └── practice-questions.md
├── 02-Probabilistic-Prediction-and-Uncertainty-in-Practice/
│   ├── Projects/
│   │   ├── 01-probabilistic-prediction-report.md
│   │   ├── 02-conformal-prediction-lab.md
│   │   └── README.md
│   ├── 01-probabilistic-classifiers-and-predictive-distributions.md
│   ├── 02-bayesian-linear-and-logistic-regression-in-practice.md
│   ├── 03-ensembles-and-bootstrap-for-prediction-uncertainty.md
│   ├── 04-gaussian-processes-and-small-data-uncertainty.md
│   ├── 05-split-conformal-prediction.md
│   ├── 06-conformalized-quantile-regression-and-adaptive-intervals.md
│   ├── 07-uncertainty-aware-abstention-and-human-review.md
│   ├── README.md
│   └── practice-questions.md
├── 03-Imbalanced-Learning-and-Decision-Thresholds/
│   ├── Projects/
│   │   ├── 01-rare-event-classification.md
│   │   └── README.md
│   ├── 01-rare-event-problem-framing.md
│   ├── 02-class-weights-and-cost-sensitive-learning.md
│   ├── 03-under-and-oversampling-and-smote-limitations.md
│   ├── 04-resampling-inside-training-folds.md
│   ├── 05-expected-cost-and-threshold-optimization.md
│   ├── 06-alert-capacity-and-review-limits.md
│   ├── README.md
│   └── practice-questions.md
├── 04-Probability-Calibration-and-Reliability/
│   ├── Projects/
│   │   ├── 01-calibrated-risk-scoring-model.md
│   │   └── README.md
│   ├── 01-calibration-vs-discrimination.md
│   ├── 02-reliability-diagrams-and-brier-score.md
│   ├── 03-platt-scaling-and-temperature-scaling.md
│   ├── 04-isotonic-regression-and-multiclass-calibration.md
│   ├── 05-calibration-data-and-leakage-prevention.md
│   ├── README.md
│   └── practice-questions.md
├── 05-Dimensionality-Reduction-and-Representation/
│   ├── Projects/
│   │   ├── 01-dimensionality-reduction-comparison.md
│   │   └── README.md
│   ├── 01-pca-in-practice-and-explained-variance.md
│   ├── 02-random-projection-and-ica-overview.md
│   ├── 03-tsne-and-umap.md
│   ├── 04-reconstruction-error-and-information-loss.md
│   ├── 05-leakage-and-visualization-limitations.md
│   ├── README.md
│   └── practice-questions.md
├── 06-Anomaly-and-Novelty-Detection/
│   ├── Projects/
│   │   ├── 01-fraud-or-system-anomaly-detection.md
│   │   └── README.md
│   ├── 01-anomalies-outliers-and-novelty.md
│   ├── 02-statistical-and-distance-based-methods.md
│   ├── 03-isolation-forest.md
│   ├── 04-local-outlier-factor.md
│   ├── 05-one-class-svm.md
│   ├── 06-density-and-reconstruction-based-methods.md
│   ├── 07-thresholding-with-scarce-labels.md
│   ├── 08-anomaly-drift-and-alert-quality.md
│   ├── README.md
│   └── practice-questions.md
├── 07-Feature-Selection-Interpretability-and-Explainability/
│   ├── Projects/
│   │   ├── 01-explainability-and-model-risk-audit.md
│   │   └── README.md
│   ├── 01-feature-selection-filter-wrapper-and-embedded-methods.md
│   ├── 02-variance-correlation-and-mutual-information.md
│   ├── 03-recursive-feature-elimination-and-lasso-selection.md
│   ├── 04-multicollinearity-and-unstable-coefficients.md
│   ├── 05-model-specific-vs-model-agnostic-explanations.md
│   ├── 06-permutation-importance.md
│   ├── 07-shap-and-feature-attribution.md
│   ├── 08-partial-dependence-and-ice.md
│   ├── 09-explanation-stability-and-causal-limitations.md
│   ├── 10-counterfactual-explanations-and-recourse.md
│   ├── README.md
│   └── practice-questions.md
├── 08-Time-Series-Analysis-and-Forecasting/
│   ├── Projects/
│   │   ├── 01-demand-or-traffic-forecasting.md
│   │   └── README.md
│   ├── 01-trend-seasonality-and-residuals.md
│   ├── 02-naive-and-seasonal-naive-baselines.md
│   ├── 03-lag-features-and-rolling-statistics.md
│   ├── 04-forecast-horizons-recursive-vs-direct.md
│   ├── 05-autoregression-and-moving-average-intuition.md
│   ├── 06-arima-and-sarima-concepts.md
│   ├── 07-exponential-smoothing-and-prophet-style-models.md
│   ├── 08-regression-and-gradient-boosting-for-forecasting.md
│   ├── 09-global-models-and-hierarchical-forecasting.md
│   ├── 10-probabilistic-forecasting-and-forecast-intervals.md
│   ├── 11-rolling-origin-backtesting-and-forecast-metrics.md
│   ├── 12-missing-timestamps-intermittent-demand-and-drift.md
│   ├── README.md
│   └── practice-questions.md
├── 09-Recommender-Systems-and-Learning-to-Rank/
│   ├── Projects/
│   │   ├── 01-recommender-and-ranking-evaluation.md
│   │   └── README.md
│   ├── 01-recommendation-problems-and-baselines.md
│   ├── 02-user-item-matrices-and-feedback-types.md
│   ├── 03-collaborative-filtering.md
│   ├── 04-matrix-factorization.md
│   ├── 05-content-based-and-hybrid-recommendation.md
│   ├── 06-two-tower-retrieval-and-candidate-generation.md
│   ├── 07-cold-start-and-sparse-interactions.md
│   ├── 08-pointwise-pairwise-and-listwise-ranking.md
│   ├── 09-precision-recall-at-k-map-and-ndcg.md
│   ├── 10-offline-vs-online-evaluation.md
│   ├── 11-popularity-bias-diversity-and-feedback-loops.md
│   ├── README.md
│   └── practice-questions.md
├── 10-Causal-Inference-and-Product-Experimentation/
│   ├── Projects/
│   │   ├── 01-causal-effect-estimation-study.md
│   │   ├── 02-uplift-modeling-lab.md
│   │   └── README.md
│   ├── 01-prediction-vs-causal-inference.md
│   ├── 02-confounding-and-causal-diagrams.md
│   ├── 03-treatment-effects-and-selection-bias.md
│   ├── 04-propensity-scores-matching-and-weighting.md
│   ├── 05-difference-in-differences-and-synthetic-control.md
│   ├── 06-uplift-modeling-and-heterogeneous-treatment-effects.md
│   ├── 07-instrumental-variables-and-regression-discontinuity-introduction.md
│   ├── 08-variance-reduction-cuped-and-sequential-testing.md
│   ├── 09-bandits-and-off-policy-evaluation.md
│   ├── README.md
│   └── practice-questions.md
├── 11-Semi-Supervised-Active-and-Weak-Supervision/
│   ├── Projects/
│   │   ├── 01-label-efficiency-study.md
│   │   └── README.md
│   ├── 01-labeled-vs-unlabeled-data.md
│   ├── 02-pseudo-labeling-and-self-training.md
│   ├── 03-active-learning-and-query-strategies.md
│   ├── 04-weak-supervision-and-noisy-labels.md
│   ├── README.md
│   └── practice-questions.md
├── 12-Graph-Machine-Learning/
│   ├── Projects/
│   │   ├── 01-graph-based-fraud-detection.md
│   │   └── README.md
│   ├── 01-graph-data-and-graph-features.md
│   ├── 02-node-embeddings-deepwalk-and-node2vec.md
│   ├── 03-link-prediction-and-graph-based-fraud-detection.md
│   ├── 04-graph-laplacian-and-message-passing-gnn-basics.md
│   ├── 05-graph-ml-evaluation-and-scaling.md
│   ├── README.md
│   └── practice-questions.md
├── 13-Reinforcement-Learning-Foundations/
│   ├── Projects/
│   │   ├── 01-tabular-q-learning-agent.md
│   │   ├── 02-policy-gradient-agent.md
│   │   └── README.md
│   ├── 01-mdps-and-bellman-equations.md
│   ├── 02-value-and-policy-iteration.md
│   ├── 03-monte-carlo-and-temporal-difference-learning.md
│   ├── 04-q-learning-and-function-approximation.md
│   ├── 05-policy-gradients-and-reinforce.md
│   ├── 06-actor-critic-and-ppo-intuition.md
│   ├── 07-reward-design-exploration-and-rl-in-practice.md
│   ├── README.md
│   └── practice-questions.md
├── 14-Specialist-ML-Electives/
│   ├── 01-survival-analysis-concepts.md
│   ├── 02-hidden-markov-models-and-kalman-filters-introduction.md
│   ├── 03-selecting-specialist-methods.md
│   ├── README.md
│   └── practice-questions.md
├── 15-Stage-5B-Capstones/
│   ├── 01-rare-event-model-with-calibration-and-conformal-uncertainty.md
│   ├── 02-time-series-forecasting-and-backtesting.md
│   ├── 03-recommender-system-with-ranking-metrics.md
│   ├── 04-advanced-ml-capstone.md
│   ├── README.md
│   └── project-standards-and-rubric.md
└── README.md
```

## Stage 5C — Deep Learning & Transformers

```text
Stage 5C — Deep Learning & Transformers/
├── 00-Stage-Overview/
│   ├── Projects/
│   │   ├── 01-train-a-small-gpt-and-write-the-report.md
│   │   └── README.md
│   ├── README.md
│   └── learning-plan.md
├── 01-Neural-Networks-and-Backpropagation/
│   ├── Projects/
│   │   ├── 01-mlp-from-scratch-in-numpy.md
│   │   └── README.md
│   ├── 01-the-neuron-and-perceptron.md
│   ├── 02-layers-and-activations.md
│   ├── 03-forward-pass-and-loss-computation.md
│   ├── 04-backpropagation-in-practice.md
│   ├── README.md
│   └── practice-questions.md
├── 02-PyTorch-Fundamentals/
│   ├── Projects/
│   │   ├── 01-mnist-mlp-in-pytorch.md
│   │   └── README.md
│   ├── 01-tensors.md
│   ├── 02-autograd-in-practice.md
│   ├── 03-nn-module.md
│   ├── 04-datasets-and-dataloaders.md
│   ├── 05-gpu-and-device-management.md
│   ├── 06-saving-and-loading-models-in-pytorch.md
│   ├── README.md
│   └── practice-questions.md
├── 03-Training-Deep-Networks/
│   ├── Projects/
│   │   ├── 01-training-diagnostics-dashboard.md
│   │   └── README.md
│   ├── 01-the-training-loop.md
│   ├── 02-optimizers-and-learning-rate-schedules-in-practice.md
│   ├── 03-initialization-and-normalization-in-practice.md
│   ├── 04-dropout-regularization-and-data-augmentation.md
│   ├── 05-mixed-precision-training.md
│   ├── 06-gradient-clipping-and-gradient-accumulation.md
│   ├── 07-deep-learning-tuning-playbook-learning-rate-batch-size-and-budget.md
│   ├── 08-debugging-training-runs.md
│   ├── README.md
│   └── practice-questions.md
├── 04-Computer-Vision-Essentials/
│   ├── Projects/
│   │   ├── 01-transfer-learning-image-classifier.md
│   │   ├── 02-object-detection-mini-project.md
│   │   └── README.md
│   ├── 01-convolutions-in-practice-and-feature-maps.md
│   ├── 02-cnn-architectures-and-residual-connections.md
│   ├── 03-transfer-learning-and-fine-tuning.md
│   ├── 04-object-detection.md
│   ├── 05-image-segmentation.md
│   ├── 06-detection-and-segmentation-metrics.md
│   ├── README.md
│   └── practice-questions.md
├── 05-Sequence-Models-and-Tabular-Deep-Learning/
│   ├── Projects/
│   │   ├── 01-tabular-deep-learning-vs-gradient-boosting.md
│   │   └── README.md
│   ├── 01-recurrent-networks-in-practice.md
│   ├── 02-why-rnns-struggle-and-gated-units.md
│   ├── 03-deep-learning-for-time-series-and-tabular-data.md
│   ├── README.md
│   └── practice-questions.md
├── 06-Embeddings-and-Representation-Learning/
│   ├── Projects/
│   │   ├── 01-train-small-word-embeddings.md
│   │   └── README.md
│   ├── 01-one-hot-vs-dense-embeddings.md
│   ├── 02-word2vec-intuition.md
│   ├── 03-contrastive-learning.md
│   ├── 04-sentence-embeddings.md
│   ├── 05-autoencoders-and-representation-learning.md
│   ├── README.md
│   └── practice-questions.md
├── 07-Attention-and-the-Transformer/
│   ├── Projects/
│   │   ├── 01-transformer-block-in-pytorch.md
│   │   └── README.md
│   ├── 01-the-attention-idea.md
│   ├── 02-queries-keys-values-and-scaled-dot-product-attention.md
│   ├── 03-multi-head-attention-and-masking.md
│   ├── 04-positional-encoding-in-practice.md
│   ├── 05-the-transformer-block.md
│   ├── 06-encoder-decoder-and-decoder-only-architectures.md
│   ├── 07-efficient-attention-and-flashattention.md
│   ├── 08-architecture-variants-mixture-of-experts-and-state-space-models.md
│   ├── README.md
│   └── practice-questions.md
├── 08-Tokenization/
│   ├── Projects/
│   │   ├── 01-build-a-bpe-tokenizer.md
│   │   └── README.md
│   ├── 01-why-tokenization-matters.md
│   ├── 02-characters-words-and-subwords.md
│   ├── 03-byte-pair-encoding.md
│   ├── 04-tokenizer-quirks-and-costs.md
│   ├── README.md
│   └── practice-questions.md
├── 09-Build-a-GPT-From-Scratch/
│   ├── Projects/
│   │   ├── 01-nano-gpt-on-custom-corpus.md
│   │   └── README.md
│   ├── 01-bigram-language-model.md
│   ├── 02-self-attention-head.md
│   ├── 03-full-gpt-model.md
│   ├── 04-training-on-a-text-corpus.md
│   ├── 05-scaling-it-up.md
│   ├── README.md
│   └── practice-questions.md
├── 10-Pretraining-Scaling-Laws-and-Compute/
│   ├── Projects/
│   │   ├── 01-scaling-mini-experiment.md
│   │   └── README.md
│   ├── 01-pretraining-objectives.md
│   ├── 02-pretraining-data.md
│   ├── 03-scaling-laws.md
│   ├── 04-compute-flops-and-memory.md
│   ├── 05-distributed-training-ddp-fsdp-and-activation-checkpointing.md
│   ├── 06-long-context-and-training-stability.md
│   ├── README.md
│   └── practice-questions.md
├── 11-Post-Training-SFT-RLHF-DPO-and-Constitutional-AI/
│   ├── Projects/
│   │   ├── 01-compare-base-vs-instruct-models.md
│   │   └── README.md
│   ├── 01-from-base-model-to-assistant.md
│   ├── 02-supervised-fine-tuning.md
│   ├── 03-reward-models-and-rlhf.md
│   ├── 04-dpo-and-preference-optimization.md
│   ├── 05-constitutional-ai-and-rlaif.md
│   ├── 06-reinforcement-learning-for-reasoning.md
│   ├── README.md
│   └── practice-questions.md
├── 12-Decoding-and-Sampling/
│   ├── Projects/
│   │   ├── 01-sampling-parameters-experiment.md
│   │   └── README.md
│   ├── 01-greedy-and-sampling-based-decoding.md
│   ├── 02-temperature.md
│   ├── 03-top-k-top-p-and-min-p.md
│   ├── 04-kv-cache-intuition.md
│   ├── 05-speculative-decoding-intuition.md
│   ├── README.md
│   └── practice-questions.md
├── 13-Reasoning-Models-and-Test-Time-Compute/
│   ├── Projects/
│   │   ├── 01-reasoning-budget-vs-accuracy.md
│   │   └── README.md
│   ├── 01-chain-of-thought.md
│   ├── 02-test-time-compute-and-inference-scaling.md
│   ├── 03-when-reasoning-helps-and-hurts.md
│   ├── 04-reasoning-budgets-and-cost.md
│   ├── README.md
│   └── practice-questions.md
├── 14-Multimodal-Models/
│   ├── Projects/
│   │   ├── 01-zero-shot-image-classification-with-clip.md
│   │   └── README.md
│   ├── 01-vision-transformers.md
│   ├── 02-clip-and-image-text-alignment.md
│   ├── 03-vision-language-models.md
│   ├── 04-audio-and-speech-models.md
│   ├── 05-diffusion-models-in-practice.md
│   ├── README.md
│   └── practice-questions.md
├── 15-Reading-and-Reproducing-ML-Papers/
│   ├── Projects/
│   │   ├── 01-reproduce-a-small-paper-result.md
│   │   └── README.md
│   ├── 01-how-to-read-a-paper.md
│   ├── 02-the-essential-paper-list.md
│   ├── 03-reproducing-results.md
│   ├── 04-writing-paper-summaries.md
│   ├── README.md
│   └── practice-questions.md
└── README.md
```

## Stage 5D — MLOps

```text
Stage 5D — MLOps/
├── 00-Stage-Overview/
│   ├── Projects/
│   │   ├── 01-local-mlops-environment.md
│   │   └── README.md
│   ├── README.md
│   ├── architecture-and-tooling-map.md
│   ├── learning-plan.md
│   └── prerequisites-and-exit-criteria.md
├── 01-Production-ML-Lifecycle-and-System-Design/
│   ├── Projects/
│   │   ├── 01-production-ml-system-design.md
│   │   └── README.md
│   ├── 01-notebook-to-production.md
│   ├── 02-ml-system-requirements-and-batch-vs-online-decision.md
│   ├── 03-production-ml-system-components.md
│   ├── 04-non-functional-requirements-latency-throughput-and-cost-budgets.md
│   ├── 05-failure-modes-and-risk-assessment-for-ml-systems.md
│   ├── README.md
│   └── practice-questions.md
├── 02-Code-Quality-Testing-and-Project-Structure/
│   ├── Projects/
│   │   ├── 01-tested-ml-training-package.md
│   │   └── README.md
│   ├── 01-package-structure-and-configuration.md
│   ├── 02-type-hints-linting-and-formatting.md
│   ├── 03-unit-tests-for-features-and-transformations.md
│   ├── 04-integration-and-contract-tests.md
│   ├── 05-data-and-model-behavior-tests.md
│   ├── 06-logging-exceptions-and-error-handling.md
│   ├── README.md
│   └── practice-questions.md
├── 03-Data-and-Feature-Pipeline-Engineering/
│   ├── Projects/
│   │   ├── 01-reliable-feature-pipeline.md
│   │   └── README.md
│   ├── 01-data-contracts-and-schema-validation.md
│   ├── 02-data-quality-gates-and-failure-policies.md
│   ├── 03-idempotency-retries-and-backfills.md
│   ├── 04-point-in-time-correctness.md
│   ├── 05-feature-pipeline-reproducibility-and-data-versioning.md
│   ├── 06-batch-and-online-feature-computation.md
│   ├── 07-feature-stores-in-practice.md
│   ├── README.md
│   └── practice-questions.md
├── 04-Workflow-Orchestration-and-Scheduling/
│   ├── Projects/
│   │   ├── 01-orchestrated-training-and-batch-scoring.md
│   │   └── README.md
│   ├── 01-dags-tasks-dependencies-and-scheduling.md
│   ├── 02-airflow-orchestration-fundamentals.md
│   ├── 03-task-timeouts-alerts-and-failure-handling-in-dags.md
│   ├── 04-parameterized-and-reusable-pipelines.md
│   ├── 05-workflow-testing-and-local-development.md
│   ├── README.md
│   └── practice-questions.md
├── 05-Experiment-Tracking-Model-Registry-and-Lineage/
│   ├── Projects/
│   │   ├── 01-registered-model-with-lineage.md
│   │   └── README.md
│   ├── 01-mlflow-tracking-and-experiment-runs.md
│   ├── 02-parameters-metrics-and-artifacts.md
│   ├── 03-model-packaging-and-serialization.md
│   ├── 04-model-registry-and-versioning.md
│   ├── 05-model-lineage-and-provenance.md
│   ├── 06-approval-and-promotion-workflows.md
│   ├── README.md
│   └── practice-questions.md
├── 06-Reproducible-Training-and-Resource-Management/
│   ├── Projects/
│   │   ├── 01-resource-aware-training.md
│   │   └── README.md
│   ├── 01-reproducible-training-runs-and-lockfiles.md
│   ├── 02-cpu-memory-gpu-and-storage-profiling.md
│   ├── 03-parallelism-and-resource-limits.md
│   ├── 04-checkpointing-and-resuming-training.md
│   ├── README.md
│   └── practice-questions.md
├── 07-Containers-for-ML/
│   ├── Projects/
│   │   ├── 01-containerized-training-and-inference.md
│   │   └── README.md
│   ├── 01-docker-images-for-ml-gpu-and-cuda.md
│   ├── 02-dependency-and-layer-caching-for-ml-images.md
│   ├── 03-docker-compose-for-local-ml-services.md
│   ├── README.md
│   └── practice-questions.md
├── 08-CI-CD-and-Release-Automation-for-ML/
│   ├── Projects/
│   │   ├── 01-ci-cd-for-an-ml-model.md
│   │   └── README.md
│   ├── 01-ci-cd-for-machine-learning-what-is-different.md
│   ├── 02-model-quality-gates-and-regression-checks-in-ci.md
│   ├── 03-release-strategies-canary-blue-green-and-shadow.md
│   ├── 04-rollback-and-release-recovery.md
│   ├── README.md
│   └── practice-questions.md
├── 09-Model-Serving-and-Inference-APIs/
│   ├── Projects/
│   │   ├── 01-batch-inference-pipeline.md
│   │   ├── 02-online-prediction-api.md
│   │   ├── 03-model-server-framework-comparison.md
│   │   └── README.md
│   ├── 01-batch-scoring-jobs.md
│   ├── 02-online-inference-service-design.md
│   ├── 03-fastapi-request-response-and-validation.md
│   ├── 04-model-loading-warmup-and-process-lifecycle.md
│   ├── 05-input-output-schemas-and-compatibility.md
│   ├── 06-concurrency-timeouts-and-resource-limits.md
│   ├── 07-authentication-and-rate-limiting.md
│   ├── 08-model-serving-frameworks-bentoml-torchserve-and-triton.md
│   ├── 09-serving-on-kubernetes-with-kserve.md
│   ├── 10-load-testing-latency-and-throughput.md
│   ├── README.md
│   └── practice-questions.md
├── 10-Inference-Optimization-and-Model-Compression/
│   ├── Projects/
│   │   ├── 01-inference-performance-benchmark.md
│   │   ├── 02-onnx-and-quantization-lab.md
│   │   └── README.md
│   ├── 01-profiling-inference-bottlenecks.md
│   ├── 02-model-export-and-onnx.md
│   ├── 03-onnx-runtime-tensorrt-and-torch-compile.md
│   ├── 04-quantization-and-pruning-for-non-llm-models.md
│   ├── 05-gpu-inference-and-dynamic-batching.md
│   ├── 06-prediction-and-feature-caching-for-inference.md
│   ├── 07-edge-and-on-device-deployment-basics.md
│   ├── 08-cost-per-prediction-and-optimization-tradeoffs.md
│   ├── 09-autoscaling-and-capacity-planning.md
│   ├── README.md
│   └── practice-questions.md
├── 11-Cloud-Deployment-for-ML/
│   ├── Projects/
│   │   ├── 01-cloud-deployed-ml-workflow.md
│   │   └── README.md
│   ├── 01-cloud-ml-deployment-architecture.md
│   ├── 02-object-storage-and-model-artifacts.md
│   ├── 03-managed-training-and-inference-options.md
│   ├── 04-environment-separation-and-configuration-for-ml.md
│   ├── 05-cost-controls-and-resource-cleanup.md
│   ├── README.md
│   └── practice-questions.md
├── 12-Data-Model-and-Service-Monitoring/
│   ├── Projects/
│   │   ├── 01-model-and-service-monitoring-dashboard.md
│   │   └── README.md
│   ├── 01-logs-metrics-and-traces-for-ml-services.md
│   ├── 02-data-quality-and-schema-drift-monitoring.md
│   ├── 03-feature-and-prediction-distribution-monitoring.md
│   ├── 04-data-drift-vs-concept-drift.md
│   ├── 05-delayed-labels-and-real-world-performance.md
│   ├── 06-monitoring-tools-evidently-prometheus-and-grafana.md
│   ├── 07-service-latency-errors-and-saturation.md
│   ├── 08-alerts-runbooks-and-operational-reports.md
│   ├── README.md
│   └── practice-questions.md
├── 13-Retraining-Continuous-Training-and-Feedback-Loops/
│   ├── Projects/
│   │   ├── 01-automated-retraining-pipeline.md
│   │   └── README.md
│   ├── 01-retraining-triggers-and-policy.md
│   ├── 02-scheduled-vs-event-driven-retraining.md
│   ├── 03-training-windows-and-label-maturity.md
│   ├── 04-retraining-validation-against-the-champion-model.md
│   ├── 05-labeling-and-feedback-loops-in-production.md
│   ├── README.md
│   └── practice-questions.md
├── 14-Production-Reliability-Security-and-Governance/
│   ├── Projects/
│   │   ├── 01-production-readiness-and-risk-review.md
│   │   └── README.md
│   ├── 01-slis-slos-and-error-budgets-for-ml-services.md
│   ├── 02-circuit-breakers-fallbacks-and-graceful-degradation.md
│   ├── 03-sensitive-data-privacy-and-retention.md
│   ├── 04-model-cards-dataset-cards-and-audit-trails.md
│   ├── 05-fairness-monitoring-and-responsible-deployment.md
│   ├── 06-disaster-recovery-and-incident-response-for-ml.md
│   ├── 07-ml-specific-security-model-extraction-adversarial-inputs-and-data-poisoning.md
│   ├── README.md
│   └── practice-questions.md
├── 15-Production-ML-Architecture-Patterns/
│   ├── Projects/
│   │   ├── 01-production-architecture-comparison.md
│   │   └── README.md
│   ├── 01-reference-architectures-batch-and-real-time-scoring.md
│   ├── 02-streaming-prediction-patterns.md
│   ├── 03-human-in-the-loop-review-pattern.md
│   ├── 04-champion-challenger-and-multi-model-routing.md
│   ├── 05-architecture-case-studies-and-trade-off-reviews.md
│   ├── README.md
│   └── practice-questions.md
├── 16-Stage-5D-Production-Projects-and-Capstone/
│   ├── 01-reproducible-training-and-registry-pipeline.md
│   ├── 02-containerized-online-and-batch-serving.md
│   ├── 03-monitoring-retraining-and-rollback-loop.md
│   ├── 04-final-production-mlops-capstone.md
│   ├── README.md
│   └── production-project-rubric.md
└── README.md
```
