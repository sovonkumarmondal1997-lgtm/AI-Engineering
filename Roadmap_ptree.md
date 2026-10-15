# Project Tree — Senior Applied AI Engineer Roadmap

This is the folder and file plan that follows [`Roadmap.md`](./Roadmap.md) stage by stage.
Every stage and module here matches a stage and module in the roadmap, in the same order.

## How to read this tree

- **Stages 0–2C already exist** in this repository. Their module folders are listed from disk, with file counts.
- **Stages 3–18 are new.** Create each folder only when you start that stage, the same rule the repo already uses.
- Naming follows the existing repo conventions:
  - Stage folder: a readable title, e.g. `Mathematics for Machine Learning/`
  - Stage overview: `00-Stage-N-Overview/` with `README.md`, `learning-plan.md` and the stage project in `Projects/`
  - Module folder: `NN-Title-In-Kebab-Case/`
  - Lesson file: `NN-lesson-name.md`
  - Every module has `README.md`, its lessons, `practice-questions.md` and a hands-on lab in `Projects/`
- **Stage 16 (Flagship Portfolio Projects)** is laid out as real GitHub-style repositories, because those are what hiring managers open.

## 1. Top-level layout

```text
AI Engineering/
├── README.md
├── Roadmap.md
├── Roadmap_ptree.md
├── Stage 0 — Computer & Digital Foundation/           # Stage 0 (exists)
├── Stage 1 — Programming & Computational Thinking/    # Stage 1 (exists)
├── Stage 2 — Python for Data Engineering_1/           # Stage 2 (exists)
├── Stage 2B — Python for Data Engineering_2/           # Stage 2B (exists)
├── Stage 2C — Data Engineering_3/           # Stage 2C (exists)
├── Stage 2D — Data Architecture/           # Stage 2D (exists)
├── Stage 3 — Data Structures & Algorithms/            # Stage 3
├── Mathematics for Machine Learning/        # Stage 4
├── Machine Learning Foundations/            # Stage 5
├── Deep Learning & Transformers/            # Stage 6
├── Backend Engineering for AI Systems/      # Stage 7
├── LLM Application Engineering/             # Stage 8
├── Retrieval & RAG Systems/                 # Stage 9
├── Evaluation & Experimentation/            # Stage 10
├── AI Agents & Tool Use/                    # Stage 11
├── AI Safety, Security & Responsible AI/    # Stage 12
├── Model Customization & Inference/         # Stage 13
├── LLMOps & AI System Design/               # Stage 14
├── Applied AI in the Field/                 # Stage 15
├── Flagship Portfolio Projects/             # Stage 16
├── Interview Preparation & Getting Hired/   # Stage 17
└── Career Growth to Senior/                 # Stage 18
```

## 2. Existing stages (0–2) — already in this repository

These folders already exist, and their lesson files are written. Only the module level is shown here, to keep the tree readable.

### Stage 0 — Computer & Digital Foundation

```text
Stage 0 — Computer & Digital Foundation/
├── 00-Stage-0-Overview/
│   ├── Projects/
│   │   ├── 01-stage-0-incident-simulation.md
│   │   └── README.md
│   ├── README.md
│   └── learning-plan.md
├── 01-How-Computers-Work/
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
│   ├── Projects/
│   │   ├── 01-program-execution-and-gpu-audit.md
│   │   └── README.md
│   └── README.md
├── 02-Operating-System-Fundamentals/
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
│   ├── Projects/
│   │   ├── 01-process-resource-and-port-diagnosis.md
│   │   └── README.md
│   └── README.md
├── 03-Command-Line/
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
│   ├── Projects/
│   │   ├── 01-shell-file-and-stream-investigation.md
│   │   └── README.md
│   └── README.md
├── 04-Developer-Environment/
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
│   ├── Projects/
│   │   ├── 01-developer-environment-health-check.md
│   │   ├── 02-python-workspace-bootstrap.md
│   │   └── README.md
│   └── README.md
└── README.md
```

### Stage 1 — Programming & Computational Thinking

```text
Stage 1 — Programming & Computational Thinking/
├── 00-Stage-1-Overview/
│   ├── Projects/
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

### Stage 2 — Python for Data Engineering_1

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
│   │   ├── README.md
│   │   ├── api-to-warehouse-incremental-ingestion.md
│   │   ├── capstone-end-to-end-data-platform.md
│   │   ├── cdc-replication-postgres-to-lakehouse.md
│   │   ├── data-quality-and-observability-platform.md
│   │   ├── lakehouse-medallion-pipeline-with-pyspark-and-delta.md
│   │   ├── orchestrated-elt-with-airflow-and-dbt.md
│   │   └── real-time-kafka-streaming-pipeline.md
│   ├── README.md
│   └── learning-plan.md
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

### Stage 2B — Python for Data Engineering_2

```text
Stage 2B — Python for Data Engineering_2/
├── 00-Gap-Modules-Overview/
│   ├── Projects/
│   │   ├── 01-dockerized-local-data-lab.md
│   │   ├── 02-remote-server-pipeline-operations.md
│   │   ├── 03-aws-serverless-lakehouse.md
│   │   ├── 04-databricks-lakehouse-platform.md
│   │   ├── 05-system-design-interview-portfolio.md
│   │   ├── README.md
│   │   ├── aws-serverless-lakehouse.md
│   │   ├── databricks-lakehouse-platform.md
│   │   ├── dockerized-local-data-lab.md
│   │   ├── remote-server-pipeline-operations.md
│   │   └── system-design-interview-portfolio.md
│   ├── README.md
│   └── learning-plan.md
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

### Stage 2C — Data Engineering_3

```text
Stage 2C — Data Engineering_3/
├── README.md
├── 01-NoSQL-and-Distributed-Databases/
│   ├── 01-nosql-families-and-when-to-use-them.md
│   ├── 02-cap-theorem-and-consistency-models.md
│   ├── 03-mongodb-document-modelling-and-aggregation.md
│   ├── 04-cassandra-wide-column-partitioning-and-tombstones.md
│   ├── 05-dynamodb-single-table-design-and-streams.md
│   ├── 06-redis-caching-and-data-structures.md
│   ├── 07-elasticsearch-and-opensearch-for-search-and-logs.md
│   ├── 08-graph-databases-neo4j-and-cypher.md
│   └── 09-change-streams-and-nosql-to-lakehouse-ingestion.md
├── 02-Hadoop-Ecosystem-and-Legacy-Big-Data/
│   ├── 01-hdfs-architecture-namenode-datanodes-and-replication.md
│   ├── 02-yarn-resource-management.md
│   ├── 03-mapreduce-model-and-why-spark-replaced-it.md
│   ├── 04-hive-metastore-and-hiveql.md
│   ├── 05-hbase-and-wide-column-on-hdfs.md
│   ├── 06-sqoop-flume-and-oozie-legacy-tooling.md
│   └── 07-migrating-hadoop-workloads-to-cloud-lakehouse.md
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
│   └── 10-cost-monitoring-and-resource-monitors.md
├── 04-Google-Cloud-BigQuery-and-GCP-Data-Engineering/
│   ├── 01-gcp-data-services-landscape.md
│   ├── 02-bigquery-architecture-slots-and-storage.md
│   ├── 03-partitioning-clustering-and-query-cost-control.md
│   ├── 04-bigquery-loading-streaming-and-external-tables.md
│   ├── 05-bigquery-ml-and-scheduled-queries.md
│   ├── 06-pubsub-and-dataflow-apache-beam.md
│   ├── 07-dataproc-and-dataproc-serverless.md
│   ├── 08-cloud-composer-and-workflows.md
│   └── 09-dataplex-iam-and-governance.md
├── 05-Azure-Data-Engineering-and-Microsoft-Fabric/
│   ├── 01-azure-data-services-landscape.md
│   ├── 02-adls-gen2-and-blob-storage.md
│   ├── 03-azure-data-factory-pipelines-and-mapping-data-flows.md
│   ├── 04-synapse-analytics-dedicated-and-serverless-pools.md
│   ├── 05-event-hubs-and-stream-analytics.md
│   ├── 06-microsoft-fabric-lakehouse-and-onelake.md
│   ├── 07-azure-databricks-integration.md
│   ├── 08-entra-id-rbac-and-key-vault.md
│   └── 09-purview-governance-and-lineage.md
├── 06-dbt-and-Analytics-Engineering/
│   ├── 01-dbt-project-structure-and-materializations.md
│   ├── 02-sources-seeds-snapshots-and-incremental-models.md
│   ├── 03-jinja-macros-and-packages.md
│   ├── 04-tests-contracts-and-model-governance.md
│   ├── 05-documentation-lineage-and-exposures.md
│   ├── 06-dbt-performance-and-slim-ci.md
│   ├── 07-semantic-layer-and-metricflow.md
│   └── 08-deploying-dbt-with-airflow-and-dbt-cloud.md
├── 07-Real-Time-OLAP-and-Query-Engines/
│   ├── 01-clickhouse-architecture-and-mergetree.md
│   ├── 02-apache-druid-and-apache-pinot-overview.md
│   ├── 03-trino-and-presto-federated-queries.md
│   ├── 04-starrocks-and-doris-overview.md
│   ├── 05-materialized-views-and-pre-aggregation.md
│   └── 06-choosing-an-olap-engine-for-low-latency-dashboards.md
├── 08-Data-Platform-Architecture-and-Data-Products/
│   ├── 01-lambda-vs-kappa-architecture.md
│   ├── 02-data-mesh-principles-and-domain-ownership.md
│   ├── 03-data-products-and-slas.md
│   ├── 04-master-data-management-and-entity-resolution.md
│   ├── 05-metadata-driven-platform-design.md
│   ├── 06-multi-tenant-and-multi-region-data-platforms.md
│   └── 07-build-vs-buy-and-vendor-selection.md
├── 09-Analytics-Foundations-for-Data-Engineers/
│   ├── 01-descriptive-statistics-and-distributions-at-scale.md
│   ├── 02-sampling-and-approximate-algorithms-hyperloglog-and-sketches.md
│   ├── 03-hypothesis-testing-and-confidence-intervals.md
│   ├── 04-ab-testing-and-experiment-data-pipelines.md
│   ├── 05-cohort-funnel-and-retention-analysis.md
│   ├── 06-time-series-analysis-and-forecasting-basics.md
│   ├── 07-bi-tools-and-dashboard-design-metabase-superset-tableau.md
│   ├── 08-data-visualization-with-matplotlib-plotly-and-altair.md
│   └── 09-data-storytelling-and-stakeholder-communication.md
└── 10-Big-Data-ML-and-MLOps-Handoff/
    ├── 01-distributed-ml-with-spark-mllib.md
    ├── 02-feature-engineering-at-scale.md
    ├── 03-training-data-pipelines-and-dataset-versioning.md
    ├── 04-model-registry-and-batch-vs-online-inference.md
    └── 05-data-drift-monitoring-for-ml-pipelines.md
```

## 3. New stages (3–18) — full file plan

### Stage 2D — Data Architecture

```text
Stage 2D — Data Architecture/
├── 00-Stage-2D-Overview/
│   ├── Projects/
│   │   ├── 01-enterprise-data-architecture-capstone.md
│   │   └── README.md
│   ├── learning-plan.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
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
│   ├── practice-questions.md
│   ├── README.md
│   └── roadmap-Enterprise-Data-Architecture-Case-Studies-and-Capstone.md
└── README.md
```

### Stage 3 — Data Structures & Algorithms

```text
Stage 3 — Data Structures & Algorithms/
├── README.md
│
├── 00-Stage-3-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   ├── stage-prerequisites-and-learning-objectives.md
│   ├── dsa-topic-map-and-interview-coverage.md
│   ├── progress-tracker-and-readiness-checklist.md
│   └── Projects/
│       ├── README.md
│       └── 01-algorithm-toolkit-and-benchmark.md
│
├── 01-Complexity-and-Big-O/
│   ├── README.md
│   ├── 01-what-an-algorithm-is.md
│   ├── 02-counting-steps-and-growth.md
│   ├── 03-big-o-notation.md
│   ├── 04-time-vs-space-complexity.md
│   ├── 05-amortized-analysis.md
│   ├── 06-measuring-real-performance-in-python.md
│   ├── 07-best-average-and-worst-case-analysis.md
│   ├── 08-complexity-analysis-of-loops-and-recursion.md
│   ├── 09-comparing-algorithmic-complexities.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-benchmark-python-collections.md
│
├── 02-Arrays-Strings-and-Hashing/
│   ├── README.md
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
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-build-a-hash-map-from-scratch.md
│       └── 02-array-and-string-problem-toolkit.md
│
├── 03-Two-Pointers-Sliding-Window-and-Binary-Search/
│   ├── README.md
│   ├── 01-two-pointers.md
│   ├── 02-sliding-window.md
│   ├── 03-binary-search.md
│   ├── 04-binary-search-on-the-answer.md
│   ├── 05-pattern-recognition-drills.md
│   ├── 06-fast-and-slow-pointers.md
│   ├── 07-interval-based-problem-patterns.md
│   ├── 08-sorting-and-searching-combinations.md
│   ├── 09-invariants-and-search-space-reduction.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-log-window-analyzer.md
│       └── 02-search-and-window-pattern-library.md
│
├── 04-Stacks-Queues-and-Linked-Lists/
│   ├── README.md
│   ├── 01-stacks.md
│   ├── 02-queues-and-deques.md
│   ├── 03-monotonic-stack.md
│   ├── 04-singly-and-doubly-linked-lists.md
│   ├── 05-lru-cache-design.md
│   ├── 06-monotonic-queues.md
│   ├── 07-fast-and-slow-pointer-linked-list-problems.md
│   ├── 08-expression-parsing-and-balanced-delimiters.md
│   ├── 09-designing-data-structures-with-combined-components.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-implement-an-lru-cache.md
│       └── 02-build-a-stack-queue-and-deque-toolkit.md
│
├── 05-Recursion-Backtracking-and-Sorting/
│   ├── README.md
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
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-sorting-benchmark.md
│       └── 02-backtracking-puzzle-solver.md
│
├── 06-Trees-and-Tries/
│   ├── README.md
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
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-autocomplete-with-a-trie.md
│       └── 02-binary-tree-algorithm-toolkit.md
│
├── 07-Heaps-and-Priority-Queues/
│   ├── README.md
│   ├── 01-heap-structure.md
│   ├── 02-heapq-in-python.md
│   ├── 03-top-k-problems.md
│   ├── 04-merging-sorted-streams.md
│   ├── 05-scheduling-with-priority-queues.md
│   ├── 06-two-heaps-and-running-medians.md
│   ├── 07-heap-based-search-and-selection.md
│   ├── 08-priority-queue-design-tradeoffs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-top-k-streaming-tracker.md
│       └── 02-running-median-service.md
│
├── 08-Graphs-BFS-DFS-and-Shortest-Paths/
│   ├── README.md
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
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-dependency-resolver.md
│
├── 09-Dynamic-Programming/
│   ├── README.md
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
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-fuzzy-text-matcher.md
│       └── 02-dynamic-programming-pattern-library.md
│
├── 10-Bit-Manipulation-and-Bitwise-Algorithms/
│   ├── README.md
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
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-bitwise-utility-library.md
│       └── 02-subset-enumeration-toolkit.md
│
├── 11-Greedy-Algorithms/
│   ├── README.md
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
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-interval-scheduling-optimizer.md
│       └── 02-resource-allocation-planner.md
│
├── 12-Advanced-Graph-Algorithms/
│   ├── README.md
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
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-graph-routing-and-algorithm-comparison.md
│       └── 02-dependency-analysis-and-critical-path-tool.md
│
├── 13-Range-Query-Data-Structures/
│   ├── README.md
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
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-range-query-engine.md
│       └── 02-dynamic-range-statistics-tool.md
│
├── 14-Advanced-Problem-Solving-Patterns/
│   ├── README.md
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
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-pattern-recognition-practice-engine.md
│       └── 02-mixed-pattern-challenge-set.md
│
├── 15-Coding-Interview-Method/
│   ├── README.md
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
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       ├── 01-practice-log-first-50-problems.md
│       └── 02-timed-mock-interview-scorecard.md
│
└── 16-Advanced-DSA-Capstone-and-Interview-Readiness/
    ├── README.md
    ├── 01-capstone-requirements-and-success-criteria.md
    ├── 02-building-a-reusable-dsa-algorithm-toolkit.md
    ├── 03-benchmarking-and-complexity-validation.md
    ├── 04-solving-mixed-topic-problems-under-time-limits.md
    ├── 05-advanced-interview-question-bank.md
    ├── 06-weekly-mock-interview-and-review-cycle.md
    ├── 07-final-readiness-assessment.md
    ├── 08-gaps-remediation-and-revision-plan.md
    ├── 09-final-project-documentation-and-demonstration.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        ├── 01-dsa-algorithm-toolkit-capstone.md
        ├── 02-advanced-problem-solving-portfolio.md
        └── 03-final-timed-interview-simulation.md
```

### Stage 4 — Mathematics for Machine Learning — `Mathematics for Machine Learning/`

```text
Mathematics for Machine Learning/
├── README.md
├── 00-Stage-4-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-math-for-ml-notebook-library.md
├── 01-Math-Refresher-and-Notation/
│   ├── README.md
│   ├── 01-numbers-and-algebra-refresher.md
│   ├── 02-functions-and-graphs.md
│   ├── 03-exponents-and-logarithms.md
│   ├── 04-summation-and-product-notation.md
│   ├── 05-reading-math-in-papers.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-plot-common-functions.md
├── 02-Vectors-and-Vector-Spaces/
│   ├── README.md
│   ├── 01-what-a-vector-is.md
│   ├── 02-vector-operations.md
│   ├── 03-dot-product-and-projection.md
│   ├── 04-norms-and-distance.md
│   ├── 05-linear-independence-and-span.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-vectors-in-numpy.md
├── 03-Matrices-and-Linear-Transformations/
│   ├── README.md
│   ├── 01-matrices-as-data-and-functions.md
│   ├── 02-matrix-multiplication.md
│   ├── 03-transpose-inverse-and-identity.md
│   ├── 04-matrix-shapes-and-broadcasting.md
│   ├── 05-eigenvalues-and-eigenvectors.md
│   ├── 06-svd-and-low-rank-approximation.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-image-compression-with-svd.md
├── 04-Similarity-Distance-and-Embedding-Math/
│   ├── README.md
│   ├── 01-cosine-similarity.md
│   ├── 02-euclidean-vs-cosine.md
│   ├── 03-high-dimensional-geometry.md
│   ├── 04-nearest-neighbors-intuition.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-word-vector-similarity-explorer.md
├── 05-Derivatives-and-Gradients/
│   ├── README.md
│   ├── 01-rates-of-change.md
│   ├── 02-derivative-rules.md
│   ├── 03-partial-derivatives.md
│   ├── 04-gradients.md
│   ├── 05-numerical-vs-analytical-derivatives.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-numerical-gradient-checker.md
├── 06-Chain-Rule-and-Optimization/
│   ├── README.md
│   ├── 01-the-chain-rule.md
│   ├── 02-computational-graphs.md
│   ├── 03-gradient-descent.md
│   ├── 04-learning-rate-and-convergence.md
│   ├── 05-sgd-momentum-and-adam-intuition.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-gradient-descent-visualizer.md
├── 07-Probability-Fundamentals/
│   ├── README.md
│   ├── 01-events-and-probability.md
│   ├── 02-conditional-probability.md
│   ├── 03-bayes-theorem.md
│   ├── 04-random-variables.md
│   ├── 05-expectation-and-variance.md
│   ├── 06-independence-and-correlation.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-probability-simulations.md
├── 08-Distributions-and-Sampling/
│   ├── README.md
│   ├── 01-bernoulli-and-binomial.md
│   ├── 02-normal-distribution.md
│   ├── 03-categorical-distribution-and-softmax.md
│   ├── 04-law-of-large-numbers.md
│   ├── 05-central-limit-theorem.md
│   ├── 06-sampling-methods.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-sampling-from-a-next-token-distribution.md
├── 09-Statistics-for-Experiments-and-Evals/
│   ├── README.md
│   ├── 01-descriptive-statistics.md
│   ├── 02-confidence-intervals.md
│   ├── 03-bootstrap-resampling.md
│   ├── 04-hypothesis-testing-and-p-values.md
│   ├── 05-paired-tests-for-model-comparison.md
│   ├── 06-sample-size-and-statistical-power.md
│   ├── 07-multiple-comparisons.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-is-prompt-b-really-better.md
└── 10-Information-Theory-for-ML/
    ├── README.md
    ├── 01-information-and-surprise.md
    ├── 02-entropy.md
    ├── 03-cross-entropy-loss.md
    ├── 04-kl-divergence.md
    ├── 05-perplexity.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-compute-perplexity-of-text.md
```

### Stage 5 — Machine Learning Foundations — `Machine Learning Foundations/`

```text
Machine Learning Foundations/
├── README.md
├── 00-Stage-5-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-end-to-end-classifier-with-error-analysis.md
├── 01-What-Machine-Learning-Is/
│   ├── README.md
│   ├── 01-rules-vs-learning.md
│   ├── 02-supervised-unsupervised-and-self-supervised.md
│   ├── 03-training-validation-and-test-sets.md
│   ├── 04-the-ml-project-lifecycle.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-first-model-with-scikit-learn.md
├── 02-Data-Preparation-and-Feature-Engineering/
│   ├── README.md
│   ├── 01-exploratory-data-analysis.md
│   ├── 02-missing-values-and-outliers.md
│   ├── 03-encoding-categorical-features.md
│   ├── 04-scaling-and-normalization.md
│   ├── 05-data-leakage.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-leakage-hunt.md
├── 03-Linear-and-Logistic-Regression/
│   ├── README.md
│   ├── 01-linear-regression.md
│   ├── 02-loss-functions.md
│   ├── 03-logistic-regression.md
│   ├── 04-softmax-regression.md
│   ├── 05-implementing-from-scratch-in-numpy.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-regression-from-scratch.md
├── 04-Model-Evaluation-and-Metrics/
│   ├── README.md
│   ├── 01-accuracy-and-its-traps.md
│   ├── 02-precision-recall-and-f1.md
│   ├── 03-roc-and-pr-curves.md
│   ├── 04-regression-metrics.md
│   ├── 05-calibration.md
│   ├── 06-choosing-metrics-for-business-goals.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-metric-selection-report.md
├── 05-Overfitting-Regularization-and-Validation/
│   ├── README.md
│   ├── 01-bias-variance-trade-off.md
│   ├── 02-regularization.md
│   ├── 03-cross-validation.md
│   ├── 04-hyperparameter-tuning.md
│   ├── 05-learning-curves.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-diagnose-an-overfit-model.md
├── 06-Trees-Ensembles-and-Gradient-Boosting/
│   ├── README.md
│   ├── 01-decision-trees.md
│   ├── 02-random-forests.md
│   ├── 03-gradient-boosting.md
│   ├── 04-xgboost-and-lightgbm.md
│   ├── 05-feature-importance.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-tabular-benchmark.md
├── 07-Unsupervised-Learning/
│   ├── README.md
│   ├── 01-k-means-clustering.md
│   ├── 02-hierarchical-and-density-clustering.md
│   ├── 03-pca.md
│   ├── 04-t-sne-and-umap.md
│   ├── 05-anomaly-detection.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-cluster-support-tickets.md
├── 08-Classic-NLP-and-Text-Classification/
│   ├── README.md
│   ├── 01-text-preprocessing.md
│   ├── 02-bag-of-words-and-tf-idf.md
│   ├── 03-naive-bayes-and-linear-text-models.md
│   ├── 04-limits-of-classic-nlp.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-ticket-classifier-baseline.md
├── 09-Experiment-Tracking-and-Reproducibility/
│   ├── README.md
│   ├── 01-why-experiments-go-wrong.md
│   ├── 02-seeds-and-determinism.md
│   ├── 03-mlflow-experiment-tracking.md
│   ├── 04-data-and-model-versioning.md
│   ├── 05-writing-experiment-reports.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-tracked-experiment-suite.md
└── 10-Error-Analysis-and-Model-Debugging/
    ├── README.md
    ├── 01-slicing-performance.md
    ├── 02-confusion-driven-analysis.md
    ├── 03-label-noise.md
    ├── 04-building-a-failure-taxonomy.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-error-analysis-report.md
```

### Stage 6 — Deep Learning & Transformers — `Deep Learning & Transformers/`

```text
Deep Learning & Transformers/
├── README.md
├── 00-Stage-6-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-train-a-small-gpt-and-write-the-report.md
├── 01-Neural-Networks-and-Backpropagation/
│   ├── README.md
│   ├── 01-the-neuron.md
│   ├── 02-layers-and-activations.md
│   ├── 03-forward-pass.md
│   ├── 04-backpropagation.md
│   ├── 05-build-micrograd.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-autograd-engine-from-scratch.md
├── 02-PyTorch-Fundamentals/
│   ├── README.md
│   ├── 01-tensors.md
│   ├── 02-autograd.md
│   ├── 03-nn-module.md
│   ├── 04-datasets-and-dataloaders.md
│   ├── 05-gpu-and-device-management.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-mnist-mlp-in-pytorch.md
├── 03-Training-Deep-Networks/
│   ├── README.md
│   ├── 01-the-training-loop.md
│   ├── 02-optimizers.md
│   ├── 03-initialization-and-normalization.md
│   ├── 04-dropout-and-regularization.md
│   ├── 05-learning-rate-schedules.md
│   ├── 06-debugging-training-runs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-training-diagnostics-dashboard.md
├── 04-CNNs-and-RNNs-Essentials/
│   ├── README.md
│   ├── 01-convolutions.md
│   ├── 02-cnn-architectures.md
│   ├── 03-recurrent-networks.md
│   ├── 04-why-rnns-struggle.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-transfer-learning-image-classifier.md
├── 05-Embeddings-and-Representation-Learning/
│   ├── README.md
│   ├── 01-one-hot-vs-dense-embeddings.md
│   ├── 02-word2vec-intuition.md
│   ├── 03-contrastive-learning.md
│   ├── 04-sentence-embeddings.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-train-small-word-embeddings.md
├── 06-Attention-and-the-Transformer/
│   ├── README.md
│   ├── 01-the-attention-idea.md
│   ├── 02-queries-keys-and-values.md
│   ├── 03-scaled-dot-product-attention.md
│   ├── 04-multi-head-attention.md
│   ├── 05-positional-encoding.md
│   ├── 06-the-transformer-block.md
│   ├── 07-encoder-decoder-and-decoder-only.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-attention-from-scratch.md
├── 07-Tokenization/
│   ├── README.md
│   ├── 01-why-tokenization-matters.md
│   ├── 02-characters-words-and-subwords.md
│   ├── 03-byte-pair-encoding.md
│   ├── 04-tokenizer-quirks-and-costs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-build-a-bpe-tokenizer.md
├── 08-Build-a-GPT-From-Scratch/
│   ├── README.md
│   ├── 01-bigram-language-model.md
│   ├── 02-self-attention-head.md
│   ├── 03-full-gpt-model.md
│   ├── 04-training-on-a-text-corpus.md
│   ├── 05-sampling-from-your-model.md
│   ├── 06-scaling-it-up.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-nano-gpt-on-custom-corpus.md
├── 09-Pretraining-Scaling-Laws-and-Compute/
│   ├── README.md
│   ├── 01-pretraining-objectives.md
│   ├── 02-pretraining-data.md
│   ├── 03-scaling-laws.md
│   ├── 04-compute-flops-and-memory.md
│   ├── 05-distributed-training-overview.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-scaling-mini-experiment.md
├── 10-Post-Training-SFT-RLHF-DPO-and-Constitutional-AI/
│   ├── README.md
│   ├── 01-from-base-model-to-assistant.md
│   ├── 02-supervised-fine-tuning.md
│   ├── 03-reward-models-and-rlhf.md
│   ├── 04-dpo.md
│   ├── 05-constitutional-ai-and-rlaif.md
│   ├── 06-reinforcement-learning-for-reasoning.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-compare-base-vs-instruct-models.md
├── 11-Decoding-and-Sampling/
│   ├── README.md
│   ├── 01-greedy-and-beam-search.md
│   ├── 02-temperature.md
│   ├── 03-top-k-and-top-p.md
│   ├── 04-kv-cache-intuition.md
│   ├── 05-speculative-decoding-intuition.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-sampling-parameters-experiment.md
├── 12-Reasoning-Models-and-Test-Time-Compute/
│   ├── README.md
│   ├── 01-chain-of-thought.md
│   ├── 02-test-time-compute.md
│   ├── 03-how-reasoning-models-are-trained.md
│   ├── 04-when-reasoning-helps-and-hurts.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-reasoning-budget-vs-accuracy.md
├── 13-Multimodal-Models/
│   ├── README.md
│   ├── 01-vision-transformers.md
│   ├── 02-clip-and-contrastive-image-text.md
│   ├── 03-vision-language-models.md
│   ├── 04-audio-and-speech-models.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-zero-shot-image-classification-with-clip.md
└── 14-Reading-and-Reproducing-ML-Papers/
    ├── README.md
    ├── 01-how-to-read-a-paper.md
    ├── 02-the-essential-paper-list.md
    ├── 03-reproducing-results.md
    ├── 04-writing-paper-summaries.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-reproduce-a-small-paper-result.md
```

### Stage 7 — Backend Engineering for AI Systems — `Backend Engineering for AI Systems/`

```text
Backend Engineering for AI Systems/
├── README.md
├── 00-Stage-7-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-production-ready-ai-api-service.md
├── 01-HTTP-REST-and-API-Design/
│   ├── README.md
│   ├── 01-how-the-web-works.md
│   ├── 02-http-methods-status-codes-and-headers.md
│   ├── 03-rest-api-design.md
│   ├── 04-json-and-api-contracts.md
│   ├── 05-api-versioning.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-design-an-api-spec.md
├── 02-FastAPI-and-Pydantic/
│   ├── README.md
│   ├── 01-first-fastapi-service.md
│   ├── 02-request-validation-with-pydantic.md
│   ├── 03-dependency-injection.md
│   ├── 04-error-handling.md
│   ├── 05-openapi-docs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-crud-service.md
├── 03-Async-Python-and-Concurrent-API-Calls/
│   ├── README.md
│   ├── 01-sync-vs-async.md
│   ├── 02-asyncio-event-loop.md
│   ├── 03-async-http-clients.md
│   ├── 04-concurrency-limits-and-semaphores.md
│   ├── 05-async-pitfalls.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-parallel-llm-call-runner.md
├── 04-Databases-for-AI-Applications/
│   ├── README.md
│   ├── 01-postgresql-for-applications.md
│   ├── 02-orm-and-migrations.md
│   ├── 03-redis-fundamentals.md
│   ├── 04-storing-conversations-and-traces.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-conversation-store.md
├── 05-Caching-Queues-and-Background-Jobs/
│   ├── README.md
│   ├── 01-caching-strategies.md
│   ├── 02-message-queues.md
│   ├── 03-background-workers.md
│   ├── 04-idempotency.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-job-queue-for-batch-inference.md
├── 06-Streaming-Responses/
│   ├── README.md
│   ├── 01-server-sent-events.md
│   ├── 02-websockets.md
│   ├── 03-streaming-llm-tokens-to-clients.md
│   ├── 04-backpressure-and-cancellation.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-streaming-chat-endpoint.md
├── 07-Auth-Rate-Limiting-and-API-Security/
│   ├── README.md
│   ├── 01-authentication-and-api-keys.md
│   ├── 02-authorization.md
│   ├── 03-rate-limiting-algorithms.md
│   ├── 04-owasp-api-security-basics.md
│   ├── 05-secrets-management.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-secure-the-api.md
├── 08-Resilience-and-Failure-Handling/
│   ├── README.md
│   ├── 01-timeouts.md
│   ├── 02-retries-with-backoff-and-jitter.md
│   ├── 03-circuit-breakers.md
│   ├── 04-graceful-degradation.md
│   ├── 05-handling-provider-outages.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-chaos-test-an-llm-service.md
├── 09-Testing-AI-Backends/
│   ├── README.md
│   ├── 01-unit-and-integration-tests.md
│   ├── 02-mocking-llm-calls.md
│   ├── 03-contract-tests.md
│   ├── 04-load-testing.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-test-suite-and-load-test.md
├── 10-Deployment-and-CI-CD/
│   ├── README.md
│   ├── 01-containerizing-ai-services.md
│   ├── 02-ci-cd-pipelines.md
│   ├── 03-cloud-deployment-options.md
│   ├── 04-configuration-and-environments.md
│   ├── 05-logging-and-metrics-basics.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-deploy-to-the-cloud.md
└── 11-Minimal-Frontends-for-AI-Demos/
    ├── README.md
    ├── 01-streamlit-and-gradio.md
    ├── 02-basic-react-and-nextjs.md
    ├── 03-chat-ui-patterns.md
    ├── 04-demo-polish.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-demo-ui.md
```

### Stage 8 — LLM Application Engineering — `LLM Application Engineering/`

```text
LLM Application Engineering/
├── README.md
├── 00-Stage-8-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-structured-document-extraction-service.md
├── 01-How-LLM-APIs-Work/
│   ├── README.md
│   ├── 01-messages-and-roles.md
│   ├── 02-tokens-and-context-windows.md
│   ├── 03-sampling-parameters-in-apis.md
│   ├── 04-pricing-and-usage.md
│   ├── 05-sdks-for-major-providers.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-first-llm-api-calls.md
├── 02-Model-Selection-Cost-and-Latency/
│   ├── README.md
│   ├── 01-model-families-and-tiers.md
│   ├── 02-capability-vs-cost-vs-latency.md
│   ├── 03-benchmarking-models-on-your-task.md
│   ├── 04-open-weight-vs-api-models.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-model-selection-matrix.md
├── 03-Prompt-Engineering-Fundamentals/
│   ├── README.md
│   ├── 01-clear-and-direct-instructions.md
│   ├── 02-system-prompts-and-roles.md
│   ├── 03-few-shot-examples.md
│   ├── 04-xml-tags-and-structure.md
│   ├── 05-letting-the-model-think.md
│   ├── 06-prompt-iteration-workflow.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-prompt-iteration-log.md
├── 04-Context-Engineering/
│   ├── README.md
│   ├── 01-what-goes-in-the-context-window.md
│   ├── 02-long-context-strategies.md
│   ├── 03-lost-in-the-middle.md
│   ├── 04-context-compression-and-summarization.md
│   ├── 05-prompt-templates.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-long-document-qa.md
├── 05-Structured-Outputs-and-Validation/
│   ├── README.md
│   ├── 01-json-outputs.md
│   ├── 02-schemas-and-pydantic-validation.md
│   ├── 03-retry-and-repair-strategies.md
│   ├── 04-extraction-patterns.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-invoice-extractor.md
├── 06-Tool-Use-and-Function-Calling/
│   ├── README.md
│   ├── 01-how-tool-calling-works.md
│   ├── 02-defining-tool-schemas.md
│   ├── 03-handling-tool-results.md
│   ├── 04-parallel-tool-calls.md
│   ├── 05-tool-errors.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-multi-tool-assistant.md
├── 07-Streaming-and-Conversation-Management/
│   ├── README.md
│   ├── 01-streaming-responses.md
│   ├── 02-multi-turn-conversations.md
│   ├── 03-conversation-memory.md
│   ├── 04-ux-for-latency.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-streaming-assistant.md
├── 08-Prompt-Caching-Batching-and-Cost-Control/
│   ├── README.md
│   ├── 01-prompt-caching.md
│   ├── 02-batch-apis.md
│   ├── 03-token-budgeting.md
│   ├── 04-cost-estimation-and-tracking.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-cost-reduction-experiment.md
├── 09-Extended-Thinking-and-Reasoning-Controls/
│   ├── README.md
│   ├── 01-reasoning-modes-in-apis.md
│   ├── 02-thinking-budgets.md
│   ├── 03-when-to-use-reasoning.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-reasoning-vs-standard-comparison.md
├── 10-Vision-PDFs-and-Multimodal-Inputs/
│   ├── README.md
│   ├── 01-image-inputs.md
│   ├── 02-pdf-and-document-inputs.md
│   ├── 03-charts-and-tables.md
│   ├── 04-multimodal-limits.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-receipt-and-chart-reader.md
├── 11-Model-Context-Protocol/
│   ├── README.md
│   ├── 01-what-mcp-is.md
│   ├── 02-hosts-clients-and-servers.md
│   ├── 03-tools-resources-and-prompts.md
│   ├── 04-using-mcp-servers.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-connect-an-app-to-mcp-servers.md
├── 12-Prompt-Management-and-Versioning/
│   ├── README.md
│   ├── 01-prompts-as-code.md
│   ├── 02-prompt-versioning.md
│   ├── 03-configuration-driven-prompts.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-prompt-registry.md
└── 13-LLM-Failure-Modes-and-Mitigations/
    ├── README.md
    ├── 01-hallucination.md
    ├── 02-instruction-drift.md
    ├── 03-sycophancy.md
    ├── 04-inconsistency-and-non-determinism.md
    ├── 05-mitigation-playbook.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-failure-mode-catalog.md
```

### Stage 9 — Retrieval & RAG Systems — `Retrieval & RAG Systems/`

```text
Retrieval & RAG Systems/
├── README.md
├── 00-Stage-9-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-rag-v1-foundation-for-flagship-1.md
├── 01-Why-RAG-and-When-Not-To/
│   ├── README.md
│   ├── 01-the-knowledge-problem.md
│   ├── 02-rag-vs-long-context-vs-fine-tuning.md
│   ├── 03-rag-architecture-overview.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-naive-rag-baseline.md
├── 02-Document-Parsing-and-Ingestion/
│   ├── README.md
│   ├── 01-parsing-pdfs-html-and-office-files.md
│   ├── 02-tables-and-images-in-documents.md
│   ├── 03-metadata-extraction.md
│   ├── 04-ingestion-pipelines.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-ingestion-pipeline.md
├── 03-Chunking-Strategies/
│   ├── README.md
│   ├── 01-fixed-size-chunking.md
│   ├── 02-structure-aware-chunking.md
│   ├── 03-semantic-chunking.md
│   ├── 04-chunk-size-and-overlap-experiments.md
│   ├── 05-contextual-chunk-enrichment.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-chunking-experiment.md
├── 04-Embedding-Models/
│   ├── README.md
│   ├── 01-how-embedding-models-work.md
│   ├── 02-choosing-embedding-models.md
│   ├── 03-embedding-benchmarks.md
│   ├── 04-domain-adaptation-of-embeddings.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-embedding-model-comparison.md
├── 05-Vector-Search-and-ANN-Indexes/
│   ├── README.md
│   ├── 01-exact-vs-approximate-search.md
│   ├── 02-hnsw.md
│   ├── 03-ivf-and-product-quantization.md
│   ├── 04-vector-databases-and-pgvector.md
│   ├── 05-filtering-and-metadata.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-ann-recall-vs-latency.md
├── 06-Lexical-and-Hybrid-Retrieval/
│   ├── README.md
│   ├── 01-bm25.md
│   ├── 02-when-keyword-search-wins.md
│   ├── 03-hybrid-retrieval-and-score-fusion.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-hybrid-vs-dense.md
├── 07-Reranking/
│   ├── README.md
│   ├── 01-bi-encoders-vs-cross-encoders.md
│   ├── 02-reranking-models.md
│   ├── 03-llm-based-reranking.md
│   ├── 04-reranking-cost-trade-offs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-reranker-impact-study.md
├── 08-Query-Understanding-and-Rewriting/
│   ├── README.md
│   ├── 01-query-rewriting.md
│   ├── 02-query-decomposition.md
│   ├── 03-hyde.md
│   ├── 04-routing-queries.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-query-rewrite-experiment.md
├── 09-Context-Construction-and-Citations/
│   ├── README.md
│   ├── 01-context-assembly.md
│   ├── 02-citation-generation.md
│   ├── 03-citation-verification.md
│   ├── 04-handling-conflicting-sources.md
│   ├── 05-saying-i-dont-know.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-verified-citations.md
├── 10-Retrieval-Evaluation/
│   ├── README.md
│   ├── 01-building-a-retrieval-test-set.md
│   ├── 02-recall-and-precision-at-k.md
│   ├── 03-mrr-and-ndcg.md
│   ├── 04-synthetic-query-generation.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-retrieval-eval-harness.md
├── 11-Generation-Evaluation-for-RAG/
│   ├── README.md
│   ├── 01-faithfulness-and-groundedness.md
│   ├── 02-answer-relevance-and-correctness.md
│   ├── 03-end-to-end-rag-evaluation.md
│   ├── 04-component-vs-system-metrics.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-rag-eval-report.md
├── 12-Production-RAG-Freshness-Scale-and-Access-Control/
│   ├── README.md
│   ├── 01-incremental-indexing.md
│   ├── 02-document-updates-and-deletes.md
│   ├── 03-permission-aware-retrieval.md
│   ├── 04-scaling-to-millions-of-documents.md
│   ├── 05-rag-latency-and-cost.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-incremental-reindexing.md
└── 13-Advanced-RAG-Patterns/
    ├── README.md
    ├── 01-agentic-rag.md
    ├── 02-multi-hop-retrieval.md
    ├── 03-graph-rag.md
    ├── 04-multimodal-rag.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-agentic-rag-prototype.md
```

### Stage 10 — Evaluation & Experimentation — `Evaluation & Experimentation/`

```text
Evaluation & Experimentation/
├── README.md
├── 00-Stage-10-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-evalforge-v1-foundation-for-flagship-2.md
├── 01-Why-Evals-Are-the-Core-Skill/
│   ├── README.md
│   ├── 01-evals-as-the-product-spec.md
│   ├── 02-vibe-checks-vs-measurement.md
│   ├── 03-eval-driven-development.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-write-your-first-eval.md
├── 02-Defining-Success-Criteria/
│   ├── README.md
│   ├── 01-specific-measurable-success-criteria.md
│   ├── 02-quality-dimensions.md
│   ├── 03-guardrail-metrics-latency-cost-safety.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-success-criteria-doc.md
├── 03-Building-Eval-Datasets/
│   ├── README.md
│   ├── 01-golden-datasets.md
│   ├── 02-sampling-from-production-data.md
│   ├── 03-synthetic-data-generation.md
│   ├── 04-edge-cases-and-adversarial-examples.md
│   ├── 05-dataset-versioning.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-build-a-300-example-eval-set.md
├── 04-Code-Based-Graders/
│   ├── README.md
│   ├── 01-exact-match-and-regex.md
│   ├── 02-schema-and-format-checks.md
│   ├── 03-execution-based-grading.md
│   ├── 04-string-similarity-metrics.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-grader-library.md
├── 05-LLM-as-Judge/
│   ├── README.md
│   ├── 01-judge-prompt-design.md
│   ├── 02-rubrics-and-scoring-scales.md
│   ├── 03-pairwise-comparison.md
│   ├── 04-judge-biases.md
│   ├── 05-calibrating-judges-against-humans.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-judge-agreement-study.md
├── 06-Human-Evaluation-and-Labeling/
│   ├── README.md
│   ├── 01-labeling-guidelines.md
│   ├── 02-inter-annotator-agreement.md
│   ├── 03-labeling-tools-and-workflows.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-label-and-measure-agreement.md
├── 07-Statistical-Rigor-in-Evals/
│   ├── README.md
│   ├── 01-variance-and-non-determinism.md
│   ├── 02-confidence-intervals-for-evals.md
│   ├── 03-significance-testing-for-model-comparison.md
│   ├── 04-how-many-examples-you-need.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-significance-report.md
├── 08-Regression-Testing-and-CI-for-AI/
│   ├── README.md
│   ├── 01-eval-suites-as-tests.md
│   ├── 02-ci-gates-for-prompt-and-model-changes.md
│   ├── 03-tracking-results-over-time.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-github-actions-eval-gate.md
├── 09-Online-Evaluation-and-User-Feedback/
│   ├── README.md
│   ├── 01-implicit-and-explicit-feedback.md
│   ├── 02-ab-testing-ai-features.md
│   ├── 03-shadow-and-canary-evaluation.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-ab-test-simulation.md
├── 10-Benchmarks-and-Their-Limits/
│   ├── README.md
│   ├── 01-public-benchmarks-overview.md
│   ├── 02-contamination.md
│   ├── 03-benchmark-vs-task-specific-evals.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-benchmark-critique.md
└── 11-Error-Analysis-and-Failure-Taxonomies/
    ├── README.md
    ├── 01-reading-model-outputs.md
    ├── 02-open-and-axial-coding.md
    ├── 03-prioritizing-failures.md
    ├── 04-closing-the-loop.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-failure-taxonomy.md
```

### Stage 11 — AI Agents & Tool Use — `AI Agents & Tool Use/`

```text
AI Agents & Tool Use/
├── README.md
├── 00-Stage-11-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-analyst-agent-v1-foundation-for-flagship-3.md
├── 01-Workflows-vs-Agents/
│   ├── README.md
│   ├── 01-what-an-agent-is.md
│   ├── 02-workflows-vs-autonomous-agents.md
│   ├── 03-when-not-to-build-an-agent.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-workflow-vs-agent-comparison.md
├── 02-The-Agent-Loop/
│   ├── README.md
│   ├── 01-observe-think-act.md
│   ├── 02-building-an-agent-loop-from-scratch.md
│   ├── 03-stop-conditions.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-agent-in-100-lines.md
├── 03-Designing-Tools-for-Agents/
│   ├── README.md
│   ├── 01-tool-interface-design.md
│   ├── 02-tool-descriptions-and-examples.md
│   ├── 03-error-messages-for-models.md
│   ├── 04-tool-output-formatting.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-tool-design-ab-test.md
├── 04-Workflow-Patterns/
│   ├── README.md
│   ├── 01-prompt-chaining.md
│   ├── 02-routing.md
│   ├── 03-parallelization.md
│   ├── 04-orchestrator-workers.md
│   ├── 05-evaluator-optimizer.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-pattern-implementations.md
├── 05-Planning-Reflection-and-Self-Correction/
│   ├── README.md
│   ├── 01-planning.md
│   ├── 02-react-pattern.md
│   ├── 03-reflection-and-critique.md
│   ├── 04-verification-steps.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-self-correcting-agent.md
├── 06-State-Memory-and-Context-Management/
│   ├── README.md
│   ├── 01-short-term-state.md
│   ├── 02-long-term-memory.md
│   ├── 03-context-management-for-agents.md
│   ├── 04-compaction-and-summarization.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-long-running-agent-memory.md
├── 07-Sandboxed-Code-Execution/
│   ├── README.md
│   ├── 01-why-sandboxing.md
│   ├── 02-containers-and-isolation.md
│   ├── 03-resource-limits.md
│   ├── 04-safe-file-and-network-access.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-python-execution-sandbox.md
├── 08-Building-MCP-Servers/
│   ├── README.md
│   ├── 01-mcp-server-anatomy.md
│   ├── 02-exposing-tools-and-resources.md
│   ├── 03-authentication-and-security.md
│   ├── 04-testing-mcp-servers.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-database-mcp-server.md
├── 09-Multi-Agent-Systems/
│   ├── README.md
│   ├── 01-when-multiple-agents-help.md
│   ├── 02-orchestrator-and-subagents.md
│   ├── 03-communication-and-handoffs.md
│   ├── 04-cost-and-failure-amplification.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-research-multi-agent-system.md
├── 10-Reliability-Budgets-and-Termination/
│   ├── README.md
│   ├── 01-infinite-loops-and-runaway-costs.md
│   ├── 02-step-and-token-budgets.md
│   ├── 03-retries-and-recovery.md
│   ├── 04-human-in-the-loop.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-agent-reliability-harness.md
├── 11-Evaluating-Agents/
│   ├── README.md
│   ├── 01-outcome-vs-trajectory-evaluation.md
│   ├── 02-task-success-metrics.md
│   ├── 03-tool-call-accuracy.md
│   ├── 04-agent-benchmarks.md
│   ├── 05-simulated-environments.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-agent-eval-suite.md
├── 12-Coding-Agents-and-Computer-Use/
│   ├── README.md
│   ├── 01-how-coding-agents-work.md
│   ├── 02-repository-understanding.md
│   ├── 03-edit-test-loops.md
│   ├── 04-computer-use-agents.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-mini-coding-agent.md
└── 13-Agent-Frameworks-and-SDKs/
    ├── README.md
    ├── 01-framework-landscape.md
    ├── 02-agent-sdks-from-model-providers.md
    ├── 03-framework-vs-from-scratch-trade-offs.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-rebuild-your-agent-with-an-sdk.md
```

### Stage 12 — AI Safety, Security & Responsible AI — `AI Safety, Security & Responsible AI/`

```text
AI Safety, Security & Responsible AI/
├── README.md
├── 00-Stage-12-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-red-team-report-foundation-for-flagship-4.md
├── 01-Why-Safety-Matters-at-Frontier-Labs/
│   ├── README.md
│   ├── 01-the-mission-of-frontier-labs.md
│   ├── 02-types-of-ai-risk.md
│   ├── 03-safety-as-an-engineering-discipline.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-summarize-lab-safety-policies.md
├── 02-Alignment-Fundamentals/
│   ├── README.md
│   ├── 01-what-alignment-means.md
│   ├── 02-rlhf-recap.md
│   ├── 03-constitutional-ai.md
│   ├── 04-interpretability-overview.md
│   ├── 05-model-specs-and-behavior-policies.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-alignment-paper-summaries.md
├── 03-Frontier-Safety-Frameworks/
│   ├── README.md
│   ├── 01-responsible-scaling-policies.md
│   ├── 02-dangerous-capability-evaluations.md
│   ├── 03-system-cards.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-compare-safety-frameworks.md
├── 04-Prompt-Injection/
│   ├── README.md
│   ├── 01-direct-prompt-injection.md
│   ├── 02-indirect-prompt-injection.md
│   ├── 03-data-exfiltration-attacks.md
│   ├── 04-defenses-and-their-limits.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-injection-attack-suite.md
├── 05-Jailbreaks-and-Misuse/
│   ├── README.md
│   ├── 01-jailbreak-techniques-overview.md
│   ├── 02-misuse-categories.md
│   ├── 03-abuse-monitoring.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-misuse-risk-assessment.md
├── 06-Red-Teaming/
│   ├── README.md
│   ├── 01-red-teaming-methodology.md
│   ├── 02-automated-red-teaming.md
│   ├── 03-attack-success-rate-metrics.md
│   ├── 04-reporting-findings.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-red-team-your-rag-system.md
├── 07-Guardrails/
│   ├── README.md
│   ├── 01-input-classification.md
│   ├── 02-output-filtering.md
│   ├── 03-policy-enforcement-layers.md
│   ├── 04-guardrail-latency-and-cost.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-guardrail-layer.md
├── 08-Agent-Security/
│   ├── README.md
│   ├── 01-least-privilege-for-tools.md
│   ├── 02-confirmation-for-risky-actions.md
│   ├── 03-sandbox-escapes-and-supply-chain.md
│   ├── 04-audit-logging.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-agent-permission-system.md
├── 09-Privacy-and-Data-Governance/
│   ├── README.md
│   ├── 01-pii-detection-and-redaction.md
│   ├── 02-data-retention.md
│   ├── 03-regulations-overview.md
│   ├── 04-training-data-and-consent.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-pii-redaction-pipeline.md
├── 10-Fairness-Bias-and-Harm-Evaluation/
│   ├── README.md
│   ├── 01-sources-of-bias.md
│   ├── 02-measuring-bias-in-llm-outputs.md
│   ├── 03-mitigation-strategies.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-bias-probe-eval.md
├── 11-Helpfulness-vs-Harmlessness/
│   ├── README.md
│   ├── 01-over-refusal.md
│   ├── 02-measuring-false-refusal-rate.md
│   ├── 03-balancing-safety-and-usefulness.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-refusal-calibration-study.md
└── 12-Documentation-and-Transparency/
    ├── README.md
    ├── 01-model-cards.md
    ├── 02-system-documentation-for-ai-features.md
    ├── 03-communicating-limitations.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-write-a-system-card.md
```

### Stage 13 — Model Customization & Inference — `Model Customization & Inference/`

```text
Model Customization & Inference/
├── README.md
├── 00-Stage-13-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-specialized-small-model-foundation-for-flagship-7.md
├── 01-Prompting-vs-RAG-vs-Fine-Tuning/
│   ├── README.md
│   ├── 01-decision-framework.md
│   ├── 02-what-fine-tuning-can-and-cannot-do.md
│   ├── 03-cost-and-maintenance-trade-offs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-decision-memo.md
├── 02-Open-Weight-Models-and-Hugging-Face/
│   ├── README.md
│   ├── 01-hugging-face-hub-and-transformers.md
│   ├── 02-model-licenses.md
│   ├── 03-running-models-locally.md
│   ├── 04-chat-templates.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-run-an-open-model-locally.md
├── 03-Supervised-Fine-Tuning/
│   ├── README.md
│   ├── 01-preparing-sft-data.md
│   ├── 02-training-configuration.md
│   ├── 03-running-sft.md
│   ├── 04-overfitting-and-catastrophic-forgetting.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-sft-a-small-model.md
├── 04-Parameter-Efficient-Fine-Tuning/
│   ├── README.md
│   ├── 01-lora.md
│   ├── 02-qlora.md
│   ├── 03-adapter-merging-and-serving.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-lora-vs-full-fine-tune.md
├── 05-Preference-Tuning/
│   ├── README.md
│   ├── 01-preference-data.md
│   ├── 02-dpo-in-practice.md
│   ├── 03-evaluating-preference-tuned-models.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-dpo-experiment.md
├── 06-Distillation-and-Synthetic-Data/
│   ├── README.md
│   ├── 01-distillation-from-larger-models.md
│   ├── 02-synthetic-data-quality-control.md
│   ├── 03-terms-of-service-and-licensing.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-distill-a-classifier.md
├── 07-Evaluating-Customized-Models/
│   ├── README.md
│   ├── 01-before-and-after-evaluation.md
│   ├── 02-regression-on-general-capabilities.md
│   ├── 03-cost-quality-latency-frontier.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-fine-tune-evaluation-report.md
├── 08-Inference-Fundamentals/
│   ├── README.md
│   ├── 01-prefill-and-decode.md
│   ├── 02-ttft-tpot-and-throughput.md
│   ├── 03-memory-bandwidth-bottlenecks.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-measure-inference-metrics.md
├── 09-KV-Cache-and-Batching/
│   ├── README.md
│   ├── 01-kv-cache.md
│   ├── 02-static-and-continuous-batching.md
│   ├── 03-pagedattention.md
│   ├── 04-prefix-caching.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-batching-experiment.md
├── 10-Quantization/
│   ├── README.md
│   ├── 01-number-formats.md
│   ├── 02-post-training-quantization.md
│   ├── 03-quality-impact-of-quantization.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-quantization-trade-off-study.md
├── 11-Serving-Open-Models-with-vLLM/
│   ├── README.md
│   ├── 01-vllm-architecture.md
│   ├── 02-deploying-vllm.md
│   ├── 03-load-testing-inference-servers.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-throughput-latency-characterization.md
└── 12-GPUs-and-Cost-Modeling/
    ├── README.md
    ├── 01-gpu-architecture-for-inference.md
    ├── 02-gpu-memory-math.md
    ├── 03-cloud-gpu-cost-modeling.md
    ├── 04-build-vs-buy-inference.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-inference-cost-model.md
```

### Stage 14 — LLMOps & AI System Design — `LLMOps & AI System Design/`

```text
LLMOps & AI System Design/
├── README.md
├── 00-Stage-14-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-observability-layer-for-your-portfolio.md
├── 01-LLM-Observability-and-Tracing/
│   ├── README.md
│   ├── 01-logs-metrics-and-traces.md
│   ├── 02-opentelemetry-for-llm-apps.md
│   ├── 03-tracing-agents-and-tool-calls.md
│   ├── 04-observability-tools-landscape.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-instrument-your-rag-system.md
├── 02-Production-Metrics/
│   ├── README.md
│   ├── 01-quality-metrics-in-production.md
│   ├── 02-reliability-metrics-and-slos.md
│   ├── 03-cost-per-request-and-per-user.md
│   ├── 04-dashboards-that-matter.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-ai-system-dashboard.md
├── 03-Routing-Fallbacks-and-Multi-Provider/
│   ├── README.md
│   ├── 01-model-routing.md
│   ├── 02-fallback-chains.md
│   ├── 03-provider-abstraction.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-router-with-fallbacks.md
├── 04-Caching-and-Cost-Optimization/
│   ├── README.md
│   ├── 01-exact-and-semantic-caching.md
│   ├── 02-cost-optimization-playbook.md
│   ├── 03-quality-cost-trade-offs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-cost-optimization-case-study.md
├── 05-Rate-Limits-and-Capacity-Planning/
│   ├── README.md
│   ├── 01-provider-rate-limits.md
│   ├── 02-queueing-and-load-shedding.md
│   ├── 03-capacity-planning.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-load-test-and-capacity-plan.md
├── 06-Release-Management-for-AI/
│   ├── README.md
│   ├── 01-versioning-prompts-models-and-indexes.md
│   ├── 02-staged-rollouts-and-feature-flags.md
│   ├── 03-rollback-strategies.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-canary-release.md
├── 07-Monitoring-Drift-and-Regressions/
│   ├── README.md
│   ├── 01-input-drift.md
│   ├── 02-quality-drift.md
│   ├── 03-model-version-changes.md
│   ├── 04-alerting.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-drift-monitor.md
├── 08-Incident-Response-for-AI-Systems/
│   ├── README.md
│   ├── 01-ai-incident-types.md
│   ├── 02-runbooks.md
│   ├── 03-postmortems.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-write-a-postmortem.md
├── 09-Data-Flywheels-and-Continuous-Improvement/
│   ├── README.md
│   ├── 01-capturing-feedback.md
│   ├── 02-turning-failures-into-eval-cases.md
│   ├── 03-improvement-loops.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-feedback-to-eval-pipeline.md
├── 10-AI-System-Design-Framework/
│   ├── README.md
│   ├── 01-requirements-and-constraints.md
│   ├── 02-architecture-building-blocks.md
│   ├── 03-back-of-envelope-estimation.md
│   ├── 04-trade-off-discussion.md
│   ├── 05-design-doc-template.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-system-design-doc.md
└── 11-AI-System-Design-Case-Studies/
    ├── README.md
    ├── 01-customer-support-assistant.md
    ├── 02-enterprise-search.md
    ├── 03-coding-assistant.md
    ├── 04-document-processing-pipeline.md
    ├── 05-voice-agent.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-five-mock-designs.md
```

### Stage 15 — Applied AI in the Field — `Applied AI in the Field/`

```text
Applied AI in the Field/
├── README.md
├── 00-Stage-15-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-mock-customer-engagement.md
├── 01-The-Applied-AI-Role-at-Frontier-Labs/
│   ├── README.md
│   ├── 01-role-variants.md
│   ├── 02-a-week-in-the-life.md
│   ├── 03-skills-that-differentiate.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-role-research-notes.md
├── 02-Customer-Discovery-and-Problem-Framing/
│   ├── README.md
│   ├── 01-asking-the-right-questions.md
│   ├── 02-finding-the-real-problem.md
│   ├── 03-feasibility-assessment.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-discovery-interview-script.md
├── 03-Scoping-Prototypes-and-Success-Metrics/
│   ├── README.md
│   ├── 01-scoping-a-proof-of-concept.md
│   ├── 02-defining-success-with-customers.md
│   ├── 03-prototype-to-production-plan.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-poc-scope-document.md
├── 04-Design-Docs-and-Architecture-Decision-Records/
│   ├── README.md
│   ├── 01-design-doc-structure.md
│   ├── 02-writing-adrs.md
│   ├── 03-reviewing-others-docs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-write-a-design-doc.md
├── 05-Technical-Demos-and-Presentations/
│   ├── README.md
│   ├── 01-demo-storytelling.md
│   ├── 02-live-demo-risk-management.md
│   ├── 03-recording-demo-videos.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-ten-minute-demo.md
├── 06-Explaining-AI-to-Non-Technical-Stakeholders/
│   ├── README.md
│   ├── 01-translating-technical-trade-offs.md
│   ├── 02-setting-expectations-about-ai-limits.md
│   ├── 03-handling-objections.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-executive-summary.md
├── 07-Business-Case-and-ROI/
│   ├── README.md
│   ├── 01-estimating-value.md
│   ├── 02-total-cost-of-ownership.md
│   ├── 03-roi-reporting.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-roi-model.md
├── 08-Technical-Writing-and-Building-in-Public/
│   ├── README.md
│   ├── 01-writing-technical-blog-posts.md
│   ├── 02-sharing-experiments.md
│   ├── 03-open-source-contribution.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-publish-first-post.md
└── 09-Senior-Behaviors-Ownership-Leadership-and-Mentoring/
    ├── README.md
    ├── 01-ownership-and-ambiguity.md
    ├── 02-leading-without-authority.md
    ├── 03-mentoring.md
    ├── 04-cross-team-collaboration.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-leadership-reflection-log.md
```

### Stage 16 — Flagship Portfolio Projects — `Flagship Portfolio Projects/`

Every project folder is meant to become **its own public GitHub repository**. The layout below is what a hiring manager should see when they open it.

```text
Flagship Portfolio Projects/
├── README.md
├── 00-Portfolio-Overview/
│   ├── README.md
│   ├── portfolio-strategy.md
│   ├── how-the-projects-connect.md
│   ├── repo-standards.md
│   ├── readme-template.md
│   ├── adr-template.md
│   ├── experiment-report-template.md
│   ├── resume-bullets-guide.md
│   └── interview-question-bank.md
├── 01-Grounded-RAG-Platform/
│   ├── README.md
│   ├── pyproject.toml
│   ├── Makefile
│   ├── docker-compose.yml
│   ├── .github/
│   │   └── workflows/
│   │       ├── ci.yml
│   │       └── eval-gate.yml
│   ├── docs/
│   │   ├── architecture.md
│   │   ├── evaluation.md
│   │   ├── experiments.md
│   │   ├── failure-analysis.md
│   │   ├── cost-and-latency.md
│   │   ├── lessons-learned.md
│   │   └── decisions/
│   │       ├── ADR-001-document-parsing.md
│   │       ├── ADR-002-chunking-strategy.md
│   │       ├── ADR-003-hybrid-retrieval.md
│   │       ├── ADR-004-reranker-choice.md
│   │       └── ADR-005-citation-verification.md
│   ├── src/
│   │   └── grounded/
│   │       ├── ingestion/
│   │       ├── parsing/
│   │       ├── chunking/
│   │       ├── indexing/
│   │       ├── retrieval/
│   │       ├── reranking/
│   │       ├── generation/
│   │       ├── citations/
│   │       ├── api/
│   │       └── observability/
│   ├── evals/
│   │   ├── datasets/
│   │   │   ├── retrieval-testset.jsonl
│   │   │   ├── answer-testset.jsonl
│   │   │   └── unanswerable-testset.jsonl
│   │   ├── graders/
│   │   └── run_evals.py
│   ├── experiments/
│   │   ├── exp-001-chunk-size-and-overlap.md
│   │   ├── exp-002-dense-vs-bm25-vs-hybrid.md
│   │   ├── exp-003-reranker-impact.md
│   │   ├── exp-004-query-rewriting.md
│   │   └── exp-005-latency-optimization.md
│   ├── benchmarks/
│   │   ├── latency_benchmark.py
│   │   ├── load_test.py
│   │   └── results/
│   ├── configs/
│   │   ├── base.yaml
│   │   └── experiments/
│   ├── scripts/
│   │   ├── download_corpus.py
│   │   └── build_index.py
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   └── demo/
│       ├── app.py
│       └── demo-script.md
├── 02-EvalForge-Evaluation-Platform/
│   ├── README.md
│   ├── pyproject.toml
│   ├── docker-compose.yml
│   ├── .github/
│   │   └── workflows/
│   │       └── ci.yml
│   ├── docs/
│   │   ├── architecture.md
│   │   ├── grader-design.md
│   │   ├── judge-calibration.md
│   │   ├── statistics.md
│   │   ├── lessons-learned.md
│   │   └── decisions/
│   │       ├── ADR-001-experiment-storage.md
│   │       ├── ADR-002-judge-model-choice.md
│   │       └── ADR-003-significance-testing-method.md
│   ├── src/
│   │   └── evalforge/
│   │       ├── datasets/
│   │       ├── runners/
│   │       ├── graders/
│   │       │   ├── code_graders/
│   │       │   └── llm_judges/
│   │       ├── stats/
│   │       ├── storage/
│   │       ├── reports/
│   │       ├── ci/
│   │       └── dashboard/
│   ├── human-labels/
│   │   ├── labeling-guidelines.md
│   │   └── judge-vs-human-agreement.md
│   ├── examples/
│   │   ├── evaluate-grounded-rag/
│   │   └── evaluate-analyst-agent/
│   ├── experiments/
│   │   ├── exp-001-judge-bias-study.md
│   │   ├── exp-002-prompt-v1-vs-v2-significance.md
│   │   └── exp-003-model-a-vs-model-b.md
│   └── tests/
├── 03-Data-Analyst-Agent/
│   ├── README.md
│   ├── pyproject.toml
│   ├── docker-compose.yml
│   ├── docs/
│   │   ├── architecture.md
│   │   ├── tool-design.md
│   │   ├── sandbox-security.md
│   │   ├── agent-evaluation.md
│   │   ├── failure-analysis.md
│   │   ├── lessons-learned.md
│   │   └── decisions/
│   │       ├── ADR-001-workflow-vs-agent.md
│   │       ├── ADR-002-sandbox-technology.md
│   │       ├── ADR-003-memory-strategy.md
│   │       └── ADR-004-mcp-server-design.md
│   ├── src/
│   │   └── analyst_agent/
│   │       ├── agent_loop/
│   │       ├── tools/
│   │       │   ├── sql_tool.py
│   │       │   ├── python_tool.py
│   │       │   ├── schema_tool.py
│   │       │   └── chart_tool.py
│   │       ├── sandbox/
│   │       ├── memory/
│   │       ├── budgets/
│   │       ├── mcp_server/
│   │       ├── api/
│   │       └── observability/
│   ├── evals/
│   │   ├── tasks/
│   │   │   ├── analytics-questions.jsonl
│   │   │   └── ground-truth-answers.jsonl
│   │   ├── trajectory_graders/
│   │   └── run_agent_evals.py
│   ├── experiments/
│   │   ├── exp-001-tool-description-variants.md
│   │   ├── exp-002-planning-vs-no-planning.md
│   │   └── exp-003-model-comparison-cost-vs-success.md
│   ├── data/
│   │   └── README.md
│   ├── tests/
│   └── demo/
├── 04-Red-Team-and-Guardrails-Harness/
│   ├── README.md
│   ├── pyproject.toml
│   ├── docs/
│   │   ├── threat-model.md
│   │   ├── attack-taxonomy.md
│   │   ├── defense-design.md
│   │   ├── results.md
│   │   ├── responsible-disclosure-note.md
│   │   ├── lessons-learned.md
│   │   └── decisions/
│   │       ├── ADR-001-guardrail-placement.md
│   │       └── ADR-002-classifier-vs-llm-guard.md
│   ├── src/
│   │   └── redteam/
│   │       ├── attacks/
│   │       │   ├── direct_injection/
│   │       │   ├── indirect_injection/
│   │       │   ├── data_exfiltration/
│   │       │   └── tool_misuse/
│   │       ├── attack_generators/
│   │       ├── guardrails/
│   │       │   ├── input_filters/
│   │       │   ├── output_filters/
│   │       │   └── tool_permissions/
│   │       └── scoring/
│   ├── evals/
│   │   ├── attack-suite.jsonl
│   │   ├── benign-suite.jsonl
│   │   └── run_redteam.py
│   ├── reports/
│   │   ├── baseline-attack-success-rate.md
│   │   ├── after-defenses.md
│   │   └── system-card.md
│   └── tests/
├── 05-Customer-Deployment-Case-Study/
│   ├── README.md
│   ├── discovery/
│   │   ├── customer-brief.md
│   │   ├── discovery-interview-notes.md
│   │   └── problem-statement.md
│   ├── design/
│   │   ├── design-doc.md
│   │   ├── success-criteria.md
│   │   └── decisions/
│   │       └── ADR-001-build-approach.md
│   ├── prototype/
│   │   ├── src/
│   │   ├── evals/
│   │   └── tests/
│   ├── pilot/
│   │   ├── pilot-plan.md
│   │   ├── pilot-results.md
│   │   └── rollout-plan.md
│   ├── business/
│   │   ├── roi-model.md
│   │   ├── total-cost-of-ownership.md
│   │   └── executive-summary.md
│   └── demo/
│       ├── demo-script.md
│       └── demo-video-link.md
├── 06-Capstone-Autonomous-Coding-Agent/
│   ├── README.md
│   ├── pyproject.toml
│   ├── docker-compose.yml
│   ├── .github/
│   │   └── workflows/
│   │       ├── ci.yml
│   │       └── nightly-benchmark.yml
│   ├── docs/
│   │   ├── architecture.md
│   │   ├── benchmark-design.md
│   │   ├── scaffold-experiments.md
│   │   ├── safety-and-permissions.md
│   │   ├── cost-and-latency.md
│   │   ├── failure-analysis.md
│   │   ├── lessons-learned.md
│   │   └── decisions/
│   │       ├── ADR-001-repository-indexing.md
│   │       ├── ADR-002-edit-format.md
│   │       ├── ADR-003-test-execution-sandbox.md
│   │       ├── ADR-004-context-management.md
│   │       └── ADR-005-stopping-criteria.md
│   ├── src/
│   │   └── coding_agent/
│   │       ├── indexer/
│   │       ├── retrieval/
│   │       ├── tools/
│   │       │   ├── search_code.py
│   │       │   ├── read_file.py
│   │       │   ├── edit_file.py
│   │       │   ├── run_tests.py
│   │       │   └── run_shell.py
│   │       ├── sandbox/
│   │       ├── context/
│   │       ├── planner/
│   │       ├── guardrails/
│   │       ├── observability/
│   │       └── cli/
│   ├── benchmark/
│   │   ├── tasks/
│   │   ├── task-selection-criteria.md
│   │   ├── harness/
│   │   └── results/
│   ├── experiments/
│   │   ├── exp-001-baseline-scaffold.md
│   │   ├── exp-002-repo-map-vs-no-repo-map.md
│   │   ├── exp-003-model-comparison.md
│   │   └── exp-004-budget-vs-success-rate.md
│   ├── tests/
│   └── demo/
└── 07-Optional-Specialized-Model-Study/
    ├── README.md
    ├── pyproject.toml
    ├── docs/
    │   ├── study-design.md
    │   ├── data-generation.md
    │   ├── training-runs.md
    │   ├── inference-benchmarks.md
    │   ├── results-and-recommendation.md
    │   └── decisions/
    │       ├── ADR-001-base-model-choice.md
    │       └── ADR-002-lora-vs-full-fine-tune.md
    ├── src/
    │   ├── data/
    │   ├── training/
    │   ├── evaluation/
    │   └── serving/
    ├── configs/
    │   ├── lora.yaml
    │   ├── qlora.yaml
    │   └── vllm.yaml
    ├── benchmarks/
    │   ├── throughput_latency.py
    │   └── results/
    ├── model-card.md
    └── tests/
```

### Stage 17 — Interview Preparation & Getting Hired — `Interview Preparation & Getting Hired/`

```text
Interview Preparation & Getting Hired/
├── README.md
├── 00-Stage-17-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-job-search-campaign-tracker.md
├── 01-How-Frontier-Labs-Hire/
│   ├── README.md
│   ├── 01-the-hiring-pipeline.md
│   ├── 02-what-each-round-tests.md
│   ├── 03-common-rejection-reasons.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-target-company-research.md
├── 02-Resume-and-Portfolio-Presentation/
│   ├── README.md
│   ├── 01-resume-structure.md
│   ├── 02-writing-impact-bullets.md
│   ├── 03-github-and-portfolio-site.md
│   ├── 04-telling-a-career-change-story.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-resume-v1-and-review.md
├── 03-Coding-Interviews/
│   ├── README.md
│   ├── 01-practice-plan.md
│   ├── 02-practical-coding-rounds.md
│   ├── 03-debugging-rounds.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-timed-mock-coding-sessions.md
├── 04-AI-System-Design-Interviews/
│   ├── README.md
│   ├── 01-interview-framework.md
│   ├── 02-common-prompts.md
│   ├── 03-going-deep-on-trade-offs.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-mock-system-design-sessions.md
├── 05-Project-Deep-Dive-Interviews/
│   ├── README.md
│   ├── 01-preparing-each-project-story.md
│   ├── 02-surviving-the-why-chain.md
│   ├── 03-admitting-limitations.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-project-deep-dive-drills.md
├── 06-ML-and-LLM-Concepts-Interviews/
│   ├── README.md
│   ├── 01-core-ml-questions.md
│   ├── 02-llm-and-transformer-questions.md
│   ├── 03-rag-agents-and-evals-questions.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-concept-flashcards.md
├── 07-Behavioral-and-Mission-Interviews/
│   ├── README.md
│   ├── 01-star-stories.md
│   ├── 02-mission-and-safety-alignment.md
│   ├── 03-values-and-culture-questions.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-story-bank.md
├── 08-Take-Home-Assignments/
│   ├── README.md
│   ├── 01-scoping-a-take-home.md
│   ├── 02-delivering-a-strong-submission.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-practice-take-home.md
├── 09-Networking-and-Referrals/
│   ├── README.md
│   ├── 01-building-a-network-from-zero.md
│   ├── 02-reaching-out-well.md
│   ├── 03-community-and-events.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-outreach-plan.md
└── 10-Offers-and-First-90-Days/
    ├── README.md
    ├── 01-evaluating-offers.md
    ├── 02-negotiation-basics.md
    ├── 03-first-90-days-plan.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-ninety-day-plan.md
```

### Stage 18 — Career Growth to Senior — `Career Growth to Senior/`

```text
Career Growth to Senior/
├── README.md
├── 00-Stage-18-Overview/
│   ├── README.md
│   ├── learning-plan.md
│   └── Projects/
│       ├── README.md
│       └── 01-senior-readiness-evidence-portfolio.md
├── 01-Choosing-Your-First-AI-Role/
│   ├── README.md
│   ├── 01-role-types-that-build-toward-applied-ai.md
│   ├── 02-startup-vs-big-company.md
│   ├── 03-evaluating-learning-potential.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-role-selection-scorecard.md
├── 02-Growing-From-Junior-to-Mid-Level/
│   ├── README.md
│   ├── 01-delivering-reliably.md
│   ├── 02-owning-features-end-to-end.md
│   ├── 03-getting-feedback.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-quarterly-growth-plan.md
├── 03-What-Senior-Really-Means/
│   ├── README.md
│   ├── 01-scope-and-impact.md
│   ├── 02-technical-judgment.md
│   ├── 03-ambiguity-and-prioritization.md
│   ├── 04-multiplying-others.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-senior-gap-analysis.md
├── 04-Building-Senior-Evidence/
│   ├── README.md
│   ├── 01-brag-document.md
│   ├── 02-measurable-impact-stories.md
│   ├── 03-design-docs-and-launches.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-brag-document.md
├── 05-Staying-Current-With-the-Frontier/
│   ├── README.md
│   ├── 01-reading-routine.md
│   ├── 02-evaluating-new-models-quickly.md
│   ├── 03-separating-hype-from-signal.md
│   ├── practice-questions.md
│   └── Projects/
│       ├── README.md
│       └── 01-new-model-evaluation-memo.md
└── 06-Applying-as-a-Senior-Candidate/
    ├── README.md
    ├── 01-senior-interview-differences.md
    ├── 02-positioning-your-experience.md
    ├── 03-leveling-and-negotiation.md
    ├── practice-questions.md
    └── Projects/
        ├── README.md
        └── 01-senior-application-packet.md
```

## 4. Summary of stages (Stage 1 to Stage 18)

Modules exclude the `00-` overview folder. Lessons are the numbered `NN-*.md` files inside modules. Files is the total file count of the stage tree.

| Stage | Name | Folder | Modules | Lessons | Files | Stage project |
|---|---|---|---|---|---|---|
| 1 | Programming & Computational Thinking | `Stage 1 — Programming & Computational Thinking/` | 24 | 212 | 282 | 4 stage projects: `personal-expense-ledger-cli`, `log-investigation-and-reliability-cli`, `data-quality-and-transformation-pipeline`, `rule-based-risk-review-engine` |
| 2 | Python for Data Engineering_1 | `Stage 2 — Python for Data Engineering_1/` | 22 | 206 | 295 | 7 stage projects, ending in `capstone-end-to-end-data-platform` |
| 2B | Python for Data Engineering_2 | `Stage 2B — Python for Data Engineering_2/` | 5 | 67 | 98 | 5 stage projects, ending in `system-design-interview-portfolio` |
| 2C | Data Engineering_3 | `Stage 2C — Data Engineering_3/` | 10 | 79 | 80 | none (module lessons only, no stage project) |
| 2D | Data Architecture | `Stage 2D — Data Architecture/` | 16 | 124 | 209 | `enterprise-data-architecture-capstone` |
| 3 | Data Structures & Algorithms | `Stage 3 — Data Structures & Algorithms/` | 16 | 166 | 253 | `algorithm-toolkit-and-benchmark` |
| 4 | Mathematics for Machine Learning | `Mathematics for Machine Learning/` | 10 | 54 | 99 | `math-for-ml-notebook-library` |
| 5 | Machine Learning Foundations | `Machine Learning Foundations/` | 10 | 48 | 93 | `end-to-end-classifier-with-error-analysis` |
| 6 | Deep Learning & Transformers | `Deep Learning & Transformers/` | 14 | 69 | 130 | `train-a-small-gpt-and-write-the-report` |
| 7 | Backend Engineering for AI Systems | `Backend Engineering for AI Systems/` | 11 | 50 | 99 | `production-ready-ai-api-service` |
| 8 | LLM Application Engineering | `LLM Application Engineering/` | 13 | 56 | 113 | `structured-document-extraction-service` |
| 9 | Retrieval & RAG Systems | `Retrieval & RAG Systems/` | 13 | 54 | 111 | `rag-v1-foundation-for-flagship-1` |
| 10 | Evaluation & Experimentation | `Evaluation & Experimentation/` | 11 | 40 | 89 | `evalforge-v1-foundation-for-flagship-2` |
| 11 | AI Agents & Tool Use | `AI Agents & Tool Use/` | 13 | 51 | 108 | `analyst-agent-v1-foundation-for-flagship-3` |
| 12 | AI Safety, Security & Responsible AI | `AI Safety, Security & Responsible AI/` | 12 | 43 | 96 | `red-team-report-foundation-for-flagship-4` |
| 13 | Model Customization & Inference | `Model Customization & Inference/` | 12 | 40 | 93 | `specialized-small-model-foundation-for-flagship-7` |
| 14 | LLMOps & AI System Design | `LLMOps & AI System Design/` | 11 | 40 | 89 | `observability-layer-for-your-portfolio` |
| 15 | Applied AI in the Field | `Applied AI in the Field/` | 9 | 28 | 69 | `mock-customer-engagement` |
| 16 | Flagship Portfolio Projects | `Flagship Portfolio Projects/` | 7 | — | 156 | 7 flagship repos (1 optional) |
| 17 | Interview Preparation & Getting Hired | `Interview Preparation & Getting Hired/` | 10 | 30 | 75 | `job-search-campaign-tracker` |
| 18 | Career Growth to Senior | `Career Growth to Senior/` | 6 | 19 | 48 | `senior-readiness-evidence-portfolio` |
| **Total** | | | **255** | **1476** | **2685** | |

## 5. Build order

```text
Stage 0 (exists) → 1 (exists) → 2 (exists, wrap up) → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11
                                                                                    │
                                  Milestone M4: start applying for first AI job ◄───┘

→ 12 → 13 → 14 → 16 → 17 → 18 (years, on the job)
  Stage 15 runs in parallel from Stage 8 onward (1–2 hours per week).

Flagship projects begin inside the stages and are finished in Stage 16:
  Stage 9  → Flagship 01 (Grounded RAG)       Stage 12 → Flagship 04 (Red Team & Guardrails)
  Stage 10 → Flagship 02 (EvalForge)          Stage 13 → Flagship 07 (Optional model study)
  Stage 11 → Flagship 03 (Analyst Agent)      Stage 15 → Flagship 05 (Customer case study)
  Stage 11 (Module 12) → Flagship 06 (Capstone coding agent), finished in Stage 16
```
