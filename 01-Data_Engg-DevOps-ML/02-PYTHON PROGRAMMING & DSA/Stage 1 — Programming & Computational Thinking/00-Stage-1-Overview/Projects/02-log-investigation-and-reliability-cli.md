# Project 02 — Log Investigation & Reliability CLI

**Stage:** Stage 1 — Programming & Computational Thinking  
**Project folder in the learning roadmap:** `Stage 1 — Programming & Computational Thinking/00-Stage-1-Overview/Projects/02-log-investigation-and-reliability-cli.md`  
**Implementation repository:** `stage-1-projects/02-logscope/`  
**Expected effort:** 15–25 focused hours  
**Prerequisites:** Stage 1 modules 01–07 and Module 09 (iterators/generators, datetime, `Counter`, `deque`)  
**Status:** Implementation guide and audit specification

> This guide follows the supplied `learning-plan.md` Project 2 scope and engineering standard. It is a project brief plus a build plan: implement one milestone at a time, run the tests and quality gates, and record mistakes in `learning-notes.md`. Do not skip to the final code without understanding each module.

---

## 1. Project outcome

Build `logscope`, a reliable command-line tool that investigates application logs. It must stream large files, tolerate malformed lines and undecodable bytes, summarize severity and service failures, detect bursts of errors, trace request IDs, filter by time, and emit human-readable or JSON reports.

This is a learning project that models common on-call and data-platform investigations. It is not a production log aggregation service.

### Success criteria

By completion, you can explain and demonstrate:

- Why a generator is appropriate for line-by-line input and where memory still grows.
- How a named-group regular expression defines a small log grammar.
- How to parse timestamps into timezone-aware UTC datetimes.
- How `Counter` and `deque` simplify frequency analysis and sliding windows.
- How malformed data differs from setup failures and how exit codes communicate outcomes.
- Why multi-file ordering is a design choice rather than an assumption.
- How deterministic synthetic data creates a reproducible incident for regression tests.
- How to test pure analysis separately from filesystem and CLI behaviour.

## 2. Scope and explicit non-goals

### In scope

1. Read one or more UTF-8 log files as streams.
2. Parse a documented log-line format using one anchored regular expression with named groups.
3. Ignore blank lines; count malformed nonblank lines; replace invalid UTF-8 bytes and count affected lines.
4. Count levels, report top repeated error messages, and calculate per-service error counts/rates.
5. Detect error bursts with a configurable time window and threshold.
6. Trace a request ID and return matching events in timestamp order.
7. Apply inclusive `--since` and `--until` time filters.
8. Provide `summary`, `bursts`, and `trace` commands with text and JSON output.
9. Fail clearly for missing/unreadable files and enforce `--max-malformed-rate` (default 5%).
10. Generate seeded synthetic logs containing a planted `payments` incident and malformed rows.
11. Package as a `uv` project with tests, Ruff, and strict mypy.

### Out of scope

Real-time tailing, distributed search, log shipping, dashboards, cloud storage, authentication, alert delivery, and concurrent log ingestion. Those are later-stage concerns.

### Data and privacy

Use synthetic logs only. Do not commit real production logs, credentials, tokens, IP addresses, personal data, or customer identifiers.

---

## 3. Contract before code

### 3.1 Accepted log grammar

A nonblank valid line follows this shape:

```text
2026-03-01T08:00:01Z INFO api req=r000001 request ok
2026-03-01T08:00:02Z ERROR payments req=r000002 db timeout
2026-03-01T08:00:03Z WARN worker started
```

Grammar:

- Timestamp: UTC RFC-3339-like subset `YYYY-MM-DDTHH:MM:SSZ` (no fractional seconds or offsets in this first version).
- Level: `DEBUG`, `INFO`, `WARN`, `ERROR`, or `CRITICAL`.
- Service: one or more letters, digits, underscores, dots, or hyphens.
- Request ID: optional `req=<identifier>` field immediately after service.
- Message: the remaining text; it may be empty.
- Blank/whitespace-only lines are ignored and do not affect the malformed rate.
- A nonblank line that fails the grammar or has an impossible calendar timestamp is malformed.
- Input is decoded as UTF-8 with `errors="replace"`. A line containing U+FFFD replacement characters is counted as an undecodable line and is also malformed rather than being silently accepted.

The grammar is deliberately narrower than every possible logging format. State this limitation in the README.

### 3.2 Time-filter semantics

- Parse `--since` and `--until` as ISO-8601 timestamps.
- Require timezone-aware values; normalize them to UTC.
- Both bounds are inclusive.
- If `since > until`, treat it as invalid command input (exit 2).
- Parse and account for all nonblank input lines before applying event-time filters, so the malformed-rate gate describes the input files, not only the selected time window.

### 3.3 Exit-code contract

| Code | Meaning |
|---:|---|
| `0` | Command succeeded and malformed rate is within the configured limit |
| `1` | Expected operational/data failure: missing/unreadable input, malformed-rate threshold exceeded, or no trace matches |
| `2` | Invalid arguments or invalid option values (`argparse` convention) |

Unexpected programming errors must not be swallowed. Reports go to `stdout`; warnings and diagnostics go to `stderr`. JSON on stdout must remain valid JSON even when a warning is emitted.

### 3.4 Important scalability decision

A generator keeps ingestion memory proportional to the current line/event and the analysis state, not the full input file. However, `trace` must retain matching events and deterministic top-N/reporting keeps bounded summary state. `bursts` keeps a sliding deque and returns detected burst summaries. This implementation processes files sequentially; it does **not** globally merge interleaved timestamps across files. For burst analysis, input must be timestamp-ordered within each file and files must be supplied in chronological order. If that assumption cannot be guaranteed, use the stretch-goal `heapq.merge` design or explicitly sort events (with higher memory cost).

---

## 4. Architecture and project tree

Create this independent project inside the practice repository described in `learning-plan.md`.

```text
stage-1-projects/
├── README.md
├── .gitignore
└── 02-logscope/
    ├── pyproject.toml
    ├── uv.lock
    ├── README.md
    ├── design-notes.md
    ├── learning-notes.md
    ├── data/
    │   └── .gitkeep
    ├── tools/
    │   └── make_logs.py
    ├── src/
    │   └── logscope/
    │       ├── __init__.py
    │       ├── parser.py
    │       ├── analysis.py
    │       ├── report.py
    │       └── cli.py
    └── tests/
        ├── test_parser.py
        ├── test_analysis.py
        ├── test_reports.py
        └── test_cli.py
```

### Module responsibilities

| File | Responsibility | Must not do |
|---|---|---|
| `parser.py` | Grammar, event model, streaming input, parse statistics, time parsing | Print reports or choose exit codes |
| `analysis.py` | Pure counts, top-N, service rates, burst detection, trace filtering | Open files or print |
| `report.py` | Convert a report dictionary to deterministic text/JSON | Read files or inspect CLI arguments |
| `cli.py` | `argparse`, orchestration, stdout/stderr, exit codes | Contain core parsing/analysis algorithms |
| `tools/make_logs.py` | Seeded synthetic log generation | Generate or access real logs |
| `tests/` | Unit, integration, boundary, regression, and CLI tests | Depend on the current working directory or wall-clock time |

---

## 5. Milestone 1 — Decompose the problem

Before implementation, create `design-notes.md`. Start with this checklist and add your own examples.

### Inputs

- One or more log paths.
- Command (`summary`, `bursts`, or `trace`).
- Optional inclusive UTC time bounds.
- `--format text|json`.
- For `summary`: top-N count.
- For `bursts`: positive window in seconds and positive error threshold.
- For `trace`: request ID.
- Maximum malformed-line rate in the inclusive range 0–1.

### Outputs

- Summary counts by level.
- Top repeated error messages.
- Per-service total events, error count, and error rate.
- Burst windows (start, end, number of errors).
- Matching request trace in timestamp order.
- Input/parse statistics: nonblank lines, valid events, malformed lines, undecodable lines, malformed rate.
- Operational warnings on stderr and documented exit code.

### Pseudocode

```text
parse CLI arguments
validate time bounds and numeric thresholds
initialize ParseStats
for each input path:
    stream nonblank lines
    count every nonblank line
    decode with replacement and flag replacement characters
    parse line into an event or count malformed
    keep event state needed by selected command
apply inclusive time filter to valid events
build the selected report
write deterministic text or JSON to stdout
write diagnostics to stderr
return exit 1 if an operational/data gate failed; otherwise 0
```

### Edge-case table to complete

| Case | Expected behaviour |
|---|---|
| Empty file | Valid zero-event report, exit 0 |
| Whitespace-only file | Zero nonblank lines, malformed rate 0 |
| Only malformed nonblank lines | Report still produced; threshold normally fails |
| Invalid calendar timestamp such as month 13 | Count malformed; do not crash |
| Invalid UTF-8 bytes | Replacement decoding; affected line counted malformed |
| Missing file | Clear stderr diagnostic, exit 1 |
| Same timestamp on several events | Stable order preserved by input order |
| Exactly at `--since` or `--until` | Included |
| `since > until` | Invalid usage, exit 2 |
| Exactly threshold errors within exactly window duration | Burst detected (inclusive window) |
| Threshold 1 | Each isolated error qualifies; bursts are grouped according to the documented state rule |
| Request ID not found | Clear stderr diagnostic, exit 1 |
| Multi-file timestamps overlap | Behaviour follows documented input-order assumption; add merge support as stretch goal |
| Very long single line | Parser should remain linear/simple; test a 200 KB line |
| Unicode in message | Preserved in UTF-8 output |

---

## 6. Milestone 2 — Create the package and tooling

From the `stage-1-projects` root:

```bash
uv init --package logscope
cd logscope
uv add --dev pytest ruff mypy
```

Adjust the generated project metadata so the import package is `logscope` and the console command is `logscope`. Keep the generated `[build-system]` table from `uv` unless you know why it must change.

Use this `pyproject.toml` shape (retain a compatible build-system table generated by `uv`):

```toml
[project]
name = "logscope"
version = "0.1.0"
description = "Streaming log investigation and reliability CLI"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
logscope = "logscope.cli:main"

[dependency-groups]
dev = ["pytest", "ruff", "mypy"]

[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "C4", "RUF"]

[tool.mypy]
python_version = "3.12"
strict = true
mypy_path = "src"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"
```

After configuring the project, run:

```bash
uv sync
uv run python --version
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src
```

Commit `uv.lock`. Do not commit `.venv`, caches, generated logs, or real log files.

---

## 7. Milestone 3 — Implement the parser and streaming reader

### `src/logscope/__init__.py`

```python
"""Logscope: a small, streaming log investigation CLI."""

__version__ = "0.1.0"
```

### `src/logscope/parser.py`

```python
"""Log grammar, event model, streaming reader, and parse statistics."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

LINE_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+"
    r"(?P<level>DEBUG|INFO|WARN|ERROR|CRITICAL)\s+"
    r"(?P<service>[\w.-]+)"
    r"(?:\s+req=(?P<request_id>[\w.-]+))?"
    r"(?:\s+(?P<message>.*))?$"
)
REPLACEMENT_CHARACTER = "\ufffd"


@dataclass(frozen=True, slots=True)
class LogEvent:
    """One valid log event; timestamps are always timezone-aware UTC."""

    timestamp: datetime
    level: str
    service: str
    request_id: str | None
    message: str


@dataclass(slots=True)
class ParseStats:
    """Counts used to calculate input quality and enforce the malformed-rate gate."""

    total_nonblank: int = 0
    valid_events: int = 0
    malformed: int = 0
    undecodable_lines: int = 0

    @property
    def malformed_rate(self) -> float:
        """Return malformed / nonblank lines; an empty input has rate zero."""
        if self.total_nonblank == 0:
            return 0.0
        return self.malformed / self.total_nonblank


def parse_line(line: str) -> LogEvent | None:
    """Parse a single line, returning None for malformed syntax or impossible dates."""
    match = LINE_RE.fullmatch(line.rstrip("\r\n"))
    if match is None:
        return None

    try:
        timestamp = datetime.strptime(match["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError:
        return None

    return LogEvent(
        timestamp=timestamp,
        level=match["level"],
        service=match["service"],
        request_id=match["request_id"],
        message=match["message"] or "",
    )


def read_events(paths: Iterable[Path], stats: ParseStats) -> Iterator[LogEvent]:
    """Yield valid events line by line; malformed nonblank lines are counted, not raised.

    File-open errors intentionally propagate to the CLI, which can report an operational
    failure with the path. Input paths are processed in the order supplied.
    """
    for path in paths:
        with path.open("r", encoding="utf-8", errors="replace", newline=None) as handle:
            for raw_line in handle:
                if not raw_line.strip():
                    continue

                stats.total_nonblank += 1
                has_decode_replacement = REPLACEMENT_CHARACTER in raw_line
                event = None if has_decode_replacement else parse_line(raw_line)

                if event is None:
                    stats.malformed += 1
                    if has_decode_replacement:
                        stats.undecodable_lines += 1
                    continue

                stats.valid_events += 1
                yield event


def parse_time(value: str) -> datetime:
    """Parse an ISO-8601 timestamp and require an explicit timezone offset."""
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"invalid ISO-8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a timezone, for example 2026-03-01T08:00:00Z")
    return parsed.astimezone(UTC)
```

### Parser tests — `tests/test_parser.py`

```python
from datetime import UTC, timedelta
from pathlib import Path

import pytest

from logscope.parser import ParseStats, parse_line, parse_time, read_events


def test_parse_line_with_request_id() -> None:
    event = parse_line("2026-03-01T10:00:00Z ERROR api req=abc-1 db timeout")
    assert event is not None
    assert event.request_id == "abc-1"
    assert event.message == "db timeout"
    assert event.timestamp.tzinfo is UTC


def test_parse_line_without_request_id_and_empty_message() -> None:
    event = parse_line("2026-03-01T10:00:01Z INFO worker")
    assert event is not None
    assert event.request_id is None
    assert event.message == ""


@pytest.mark.parametrize(
    "line",
    [
        "garbage",
        "2026-13-45T10:00:00Z ERROR api broken",
        "2026-03-01T10:00:00Z error api lower-case-level",
        "2026-03-01T10:00:00 ERROR api missing-z",
    ],
)
def test_malformed_lines_return_none(line: str) -> None:
    assert parse_line(line) is None


def test_reader_counts_malformed_blank_and_valid_lines(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text(
        "garbage\n2026-03-01T10:00:00Z INFO api request ok\n \n",
        encoding="utf-8",
    )
    stats = ParseStats()
    events = list(read_events([path], stats))
    assert len(events) == 1
    assert (stats.total_nonblank, stats.valid_events, stats.malformed) == (2, 1, 1)


def test_invalid_utf8_line_is_counted_as_malformed(tmp_path: Path) -> None:
    path = tmp_path / "bad.log"
    path.write_bytes(b"2026-03-01T10:00:00Z INFO api good\n\xffbad bytes\n")
    stats = ParseStats()
    events = list(read_events([path], stats))
    assert len(events) == 1
    assert stats.undecodable_lines == 1
    assert stats.malformed == 1


def test_parse_time_requires_timezone_and_normalizes_to_utc() -> None:
    parsed = parse_time("2026-03-01T11:00:00+01:00")
    assert parsed.utcoffset() == timedelta(0)
    assert parsed.hour == 10
    with pytest.raises(ValueError, match="timezone"):
        parse_time("2026-03-01T10:00:00")
```

**Learning checkpoint:** Explain why `parse_line()` returns `None` for malformed data instead of printing or raising an exception. Explain why file-open errors are different from malformed lines.

---

## 8. Milestone 4 — Implement pure analysis functions

### `src/logscope/analysis.py`

```python
"""Pure analysis functions over parsed events."""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Iterable
from datetime import datetime, timedelta

from .parser import LogEvent

ERROR_LEVELS = frozenset({"ERROR", "CRITICAL"})


def filter_events(
    events: Iterable[LogEvent],
    since: datetime | None = None,
    until: datetime | None = None,
) -> list[LogEvent]:
    """Return events within inclusive timezone-aware bounds, preserving input order."""
    result: list[LogEvent] = []
    for event in events:
        if since is not None and event.timestamp < since:
            continue
        if until is not None and event.timestamp > until:
            continue
        result.append(event)
    return result


def level_counts(events: Iterable[LogEvent]) -> dict[str, int]:
    """Count events by level with deterministic key order."""
    counts = Counter(event.level for event in events)
    return {level: counts[level] for level in sorted(counts)}


def top_error_messages(
    events: Iterable[LogEvent], limit: int = 5
) -> list[dict[str, str | int]]:
    """Return the most frequent ERROR/CRITICAL messages with deterministic tie-breaks."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    counts = Counter(
        event.message for event in events if event.level in ERROR_LEVELS
    )
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    return [{"message": message, "count": count} for message, count in ranked]


def service_stats(events: Iterable[LogEvent]) -> list[dict[str, str | int | float]]:
    """Calculate per-service totals, errors, and error rate; zero events are absent."""
    counts: dict[str, Counter[str]] = {}
    for event in events:
        counts.setdefault(event.service, Counter())["total"] += 1
        if event.level in ERROR_LEVELS:
            counts[event.service]["errors"] += 1

    rows: list[dict[str, str | int | float]] = []
    for service in sorted(counts):
        total = counts[service]["total"]
        errors = counts[service]["errors"]
        rows.append(
            {
                "service": service,
                "total": total,
                "errors": errors,
                "error_rate": errors / total,
            }
        )
    return rows


def find_error_bursts(
    events: Iterable[LogEvent],
    window: timedelta,
    threshold: int,
) -> list[dict[str, str | int]]:
    """Find error bursts using a sliding deque; events must be timestamp ordered.

    The window is inclusive: an error exactly `window` seconds before the current error
    remains in the window. Each qualifying run emits one burst when it crosses threshold;
    it will not emit again until the count drops below threshold.
    """
    if window < timedelta(0):
        raise ValueError("window must be non-negative")
    if threshold < 1:
        raise ValueError("threshold must be at least 1")

    recent: deque[datetime] = deque()
    bursts: list[dict[str, str | int]] = []
    in_burst = False

    for event in events:
        if event.level not in ERROR_LEVELS:
            continue
        recent.append(event.timestamp)
        while recent and event.timestamp - recent[0] > window:
            recent.popleft()

        if len(recent) >= threshold and not in_burst:
            bursts.append(
                {
                    "start": recent[0].isoformat().replace("+00:00", "Z"),
                    "end": event.timestamp.isoformat().replace("+00:00", "Z"),
                    "count": len(recent),
                }
            )
            in_burst = True
        elif len(recent) < threshold:
            in_burst = False

    return bursts


def trace_request(events: Iterable[LogEvent], request_id: str) -> list[LogEvent]:
    """Return matching request events sorted by timestamp, stably for ties."""
    matches = [event for event in events if event.request_id == request_id]
    return sorted(matches, key=lambda event: event.timestamp)
```

### `tests/test_analysis.py`

```python
from datetime import UTC, datetime, timedelta

import pytest

from logscope.analysis import (
    ERROR_LEVELS,
    find_error_bursts,
    filter_events,
    level_counts,
    service_stats,
    top_error_messages,
    trace_request,
)
from logscope.parser import LogEvent


def event(second: int, level: str = "ERROR", service: str = "api",
          message: str = "boom", request_id: str | None = None) -> LogEvent:
    return LogEvent(
        timestamp=datetime(2026, 3, 1, 10, 0, second, tzinfo=UTC),
        level=level,
        service=service,
        request_id=request_id,
        message=message,
    )


def test_level_counts_and_top_errors_are_deterministic() -> None:
    events = [event(0, message="z"), event(1, message="a"), event(2, message="z")]
    assert level_counts(events) == {"ERROR": 3}
    assert top_error_messages(events, 2) == [
        {"message": "z", "count": 2},
        {"message": "a", "count": 1},
    ]


def test_service_error_rate() -> None:
    events = [event(0), event(1, level="INFO"), event(2, service="worker", level="CRITICAL")]
    rows = service_stats(events)
    assert rows[0] == {"service": "api", "total": 2, "errors": 1, "error_rate": 0.5}
    assert rows[1]["service"] == "worker"


def test_filter_bounds_are_inclusive() -> None:
    events = [event(0), event(1), event(2)]
    start = datetime(2026, 3, 1, 10, 0, 1, tzinfo=UTC)
    end = datetime(2026, 3, 1, 10, 0, 2, tzinfo=UTC)
    assert [item.timestamp.second for item in filter_events(events, start, end)] == [1, 2]


def test_burst_detected_at_inclusive_window_boundary() -> None:
    events = [event(0), event(5), event(10), event(40)]
    bursts = find_error_bursts(events, timedelta(seconds=10), 3)
    assert len(bursts) == 1
    assert bursts[0]["count"] == 3


@pytest.mark.parametrize("threshold", [0, -1])
def test_burst_rejects_non_positive_threshold(threshold: int) -> None:
    with pytest.raises(ValueError, match="threshold"):
        find_error_bursts([], timedelta(seconds=5), threshold)


def test_trace_matches_id_and_sorts_by_time() -> None:
    events = [event(2, request_id="r1"), event(1, request_id="r2"), event(0, request_id="r1")]
    result = trace_request(events, "r1")
    assert [item.timestamp.second for item in result] == [0, 2]
    assert ERROR_LEVELS == frozenset({"ERROR", "CRITICAL"})
```

**Important design note:** `filter_events()` and `trace_request()` return lists. They are appropriate for the initial learning project and bounded traces, but they are not strict constant-memory operations. `summary` can be implemented as a one-pass aggregation in a future optimization; document current memory costs honestly.

---

## 9. Milestone 5 — Build deterministic reports

### `src/logscope/report.py`

```python
"""Pure deterministic report formatting."""

from __future__ import annotations

import json
from typing import Any


def format_json(report: dict[str, Any]) -> str:
    """Serialize a report deterministically; no timestamps are generated here."""
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)


def format_text(report: dict[str, Any]) -> str:
    """Render a readable report for terminal use."""
    lines = [f"Command: {report['command']}"]

    stats = report["input"]
    lines.extend(
        [
            "",
            "Input quality:",
            f"  nonblank lines: {stats['total_nonblank']}",
            f"  valid events:   {stats['valid_events']}",
            f"  malformed:      {stats['malformed']}",
            f"  undecodable:    {stats['undecodable_lines']}",
            f"  malformed rate: {stats['malformed_rate']:.2%}",
        ]
    )

    if report["command"] == "summary":
        lines.extend(["", "Levels:"])
        for level, count in report["levels"].items():
            lines.append(f"  {level:<8} {count}")
        lines.extend(["", "Top error messages:"])
        for row in report["top_errors"]:
            lines.append(f"  {row['count']:>6}  {row['message']}")
        lines.extend(["", "Service error rates:"])
        for row in report["services"]:
            lines.append(
                f"  {row['service']:<16} errors={row['errors']:<6} "
                f"total={row['total']:<6} rate={row['error_rate']:.2%}"
            )

    elif report["command"] == "bursts":
        lines.extend(["", "Error bursts:"])
        if not report["bursts"]:
            lines.append("  none")
        for burst in report["bursts"]:
            lines.append(
                f"  {burst['start']} .. {burst['end']}  errors={burst['count']}"
            )

    elif report["command"] == "trace":
        lines.extend(["", f"Request trace: {report['request_id']}"])
        if not report["events"]:
            lines.append("  no matching events")
        for event in report["events"]:
            lines.append(
                f"  {event['timestamp']} {event['level']:<8} "
                f"{event['service']:<12} {event['message']}"
            )

    return "\n".join(lines) + "\n"
```

### `tests/test_reports.py`

```python
import json

from logscope.report import format_json, format_text


def sample_report() -> dict:
    return {
        "command": "summary",
        "input": {
            "total_nonblank": 2,
            "valid_events": 2,
            "malformed": 0,
            "undecodable_lines": 0,
            "malformed_rate": 0.0,
        },
        "levels": {"ERROR": 1, "INFO": 1},
        "top_errors": [{"message": "db timeout", "count": 1}],
        "services": [
            {"service": "api", "total": 2, "errors": 1, "error_rate": 0.5}
        ],
    }


def test_json_is_parseable_and_deterministic() -> None:
    report = sample_report()
    first = format_json(report)
    assert json.loads(first) == report
    assert format_json(report) == first


def test_text_contains_input_quality_and_error_rate() -> None:
    rendered = format_text(sample_report())
    assert "malformed rate: 0.00%" in rendered
    assert "rate=50.00%" in rendered
```

---

## 10. Milestone 6 — CLI and operational behaviour

### `src/logscope/cli.py`

```python
"""Argument parsing, orchestration, output streams, and process exit codes."""

from __future__ import annotations

import argparse
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

from .analysis import (
    filter_events,
    find_error_bursts,
    level_counts,
    service_stats,
    top_error_messages,
    trace_request,
)
from .parser import LogEvent, ParseStats, parse_time, read_events
from .report import format_json, format_text

EXIT_OK = 0
EXIT_OPERATIONAL = 1


def positive_int(value: str) -> int:
    """Argparse type for positive integers."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def non_negative_float(value: str) -> float:
    """Argparse type for finite non-negative numbers."""
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    if parsed < 0 or parsed != parsed or parsed == float("inf"):
        raise argparse.ArgumentTypeError("must be finite and non-negative")
    return parsed


def rate_limit(value: str) -> float:
    """Argparse type for malformed rate in [0, 1]."""
    parsed = non_negative_float(value)
    if parsed > 1:
        raise argparse.ArgumentTypeError("must be between 0 and 1")
    return parsed


def cli_time(value: str):
    """Argparse adapter that turns timestamp validation errors into usage errors."""
    try:
        return parse_time(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logscope",
        description="Investigate synthetic or authorized application logs.",
    )
    parser.add_argument("files", nargs="+", type=Path, help="input log files in processing order")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--since", type=cli_time, help="inclusive timezone-aware ISO timestamp")
    parser.add_argument("--until", type=cli_time, help="inclusive timezone-aware ISO timestamp")
    parser.add_argument(
        "--max-malformed-rate",
        type=rate_limit,
        default=0.05,
        help="fail with exit 1 if malformed nonblank line rate exceeds this value (default 0.05)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    summary = sub.add_parser("summary", help="summarize levels, messages, and services")
    summary.add_argument("--top", type=positive_int, default=5, help="number of error messages")

    bursts = sub.add_parser("bursts", help="detect error bursts")
    bursts.add_argument("--window-seconds", type=non_negative_float, default=60.0)
    bursts.add_argument("--threshold", type=positive_int, default=5)

    trace = sub.add_parser("trace", help="show events for one request ID")
    trace.add_argument("request_id")

    return parser


def event_to_dict(event: LogEvent) -> dict[str, str | None]:
    return {
        "timestamp": event.timestamp.isoformat().replace("+00:00", "Z"),
        "level": event.level,
        "service": event.service,
        "request_id": event.request_id,
        "message": event.message,
    }


def build_report(
    command: str,
    events: list[LogEvent],
    stats: ParseStats,
    args: argparse.Namespace,
) -> dict[str, Any]:
    """Build a report from already-read events; this function does not perform I/O."""
    input_report = {
        "total_nonblank": stats.total_nonblank,
        "valid_events": stats.valid_events,
        "malformed": stats.malformed,
        "undecodable_lines": stats.undecodable_lines,
        "malformed_rate": stats.malformed_rate,
    }
    report: dict[str, Any] = {"command": command, "input": input_report}

    if command == "summary":
        selected = filter_events(events, args.since, args.until)
        report.update(
            {
                "levels": level_counts(selected),
                "top_errors": top_error_messages(selected, args.top),
                "services": service_stats(selected),
            }
        )
    elif command == "bursts":
        selected = filter_events(events, args.since, args.until)
        report["bursts"] = find_error_bursts(
            selected,
            timedelta(seconds=args.window_seconds),
            args.threshold,
        )
    elif command == "trace":
        selected = filter_events(events, args.since, args.until)
        matches = trace_request(selected, args.request_id)
        report["request_id"] = args.request_id
        report["events"] = [event_to_dict(event) for event in matches]
    else:
        raise ValueError(f"unsupported command: {command}")

    return report


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.since is not None and args.until is not None and args.since > args.until:
        parser.error("--since must be earlier than or equal to --until")

    stats = ParseStats()
    events: list[LogEvent] = []

    try:
        # This first version stores valid events to support time filters and trace.
        # Input is still streamed line-by-line; see README for retained-memory limits.
        events.extend(read_events(args.files, stats))
    except OSError as exc:
        print(f"error: cannot read input file: {exc}", file=sys.stderr)
        return EXIT_OPERATIONAL

    report = build_report(args.command, events, stats, args)
    rendered = format_json(report) if args.format == "json" else format_text(report)
    print(rendered, end="")

    if stats.malformed_rate > args.max_malformed_rate:
        print(
            "warning: malformed-line rate "
            f"{stats.malformed_rate:.2%} exceeds limit {args.max_malformed_rate:.2%}",
            file=sys.stderr,
        )
        return EXIT_OPERATIONAL

    if args.command == "trace" and not report["events"]:
        print(f"error: no events found for request ID {args.request_id!r}", file=sys.stderr)
        return EXIT_OPERATIONAL

    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
```

### `tests/test_cli.py`

```python
import json
from pathlib import Path

from logscope.cli import main


def write_log(path: Path, *lines: str) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_summary_json_and_malformed_gate(tmp_path: Path, capsys) -> None:
    log = tmp_path / "app.log"
    write_log(
        log,
        "2026-03-01T10:00:00Z ERROR api req=r1 db timeout",
        "bad line",
    )
    code = main(["--format", "json", "--max-malformed-rate", "0.5", str(log), "summary"])
    captured = capsys.readouterr()
    assert code == 0
    payload = json.loads(captured.out)
    assert payload["input"]["malformed"] == 1
    assert "warning:" not in captured.out


def test_malformed_rate_exceeded_returns_one(tmp_path: Path, capsys) -> None:
    log = tmp_path / "app.log"
    write_log(log, "bad line", "also bad")
    code = main(["--max-malformed-rate", "0.05", str(log), "summary"])
    captured = capsys.readouterr()
    assert code == 1
    assert "warning:" in captured.err
    assert "Input quality:" in captured.out


def test_missing_file_returns_one_without_traceback(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing.log"
    code = main([str(missing), "summary"])
    captured = capsys.readouterr()
    assert code == 1
    assert "error: cannot read input file:" in captured.err
    assert "Traceback" not in captured.err


def test_trace_request_id(tmp_path: Path, capsys) -> None:
    log = tmp_path / "app.log"
    write_log(
        log,
        "2026-03-01T10:00:02Z INFO api req=r1 second",
        "2026-03-01T10:00:01Z ERROR payments req=r1 first",
    )
    code = main([str(log), "trace", "r1"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.index("first") < captured.out.index("second")


def test_invalid_time_range_uses_argparse_exit_two(tmp_path: Path) -> None:
    log = tmp_path / "app.log"
    log.write_text("", encoding="utf-8")
    try:
        main([
            "--since", "2026-03-02T00:00:00Z",
            "--until", "2026-03-01T00:00:00Z",
            str(log), "summary",
        ])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("argparse should exit with code 2 for an invalid time range")
```

**Review note:** The reference implementation uses `cli_time()` to wrap `parse_time()` and raise `argparse.ArgumentTypeError`. Keep this adapter in place and retain the regression test that invalid timestamps produce exit 2 rather than a traceback.

### Required M6 CLI fix: timezone parser adapter

**Applied in the reference `cli.py` above.** `cli_time()` converts timestamp validation failures into `argparse.ArgumentTypeError`, so invalid timestamps produce the documented usage exit code 2 instead of a traceback. Add the explicit return annotation `-> datetime` and import `datetime` from `datetime` when implementing the module; this is included in the type-checking checklist.

### Synthetic generator — `tools/make_logs.py`

```python
"""Generate deterministic synthetic logs: python tools/make_logs.py data/app.log 5000."""

from __future__ import annotations

import argparse
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

SERVICES = ("api", "auth", "worker", "payments")
ERRORS = ("db timeout", "upstream 503", "invalid token", "disk quota exceeded")
INFOS = ("request ok", "cache hit", "job started", "job finished")


def generate_lines(count: int, seed: int = 42) -> list[str]:
    """Return deterministic synthetic lines with a planted payments incident."""
    if count < 1:
        raise ValueError("count must be at least 1")
    rng = random.Random(seed)
    timestamp = datetime(2026, 3, 1, 8, 0, 0, tzinfo=UTC)
    lines: list[str] = []

    for index in range(count):
        timestamp += timedelta(seconds=rng.randint(0, 3))
        if 2000 <= index < 2040:
            level, service = "ERROR", "payments"
        else:
            level = rng.choices(("INFO", "WARN", "ERROR"), weights=(85, 10, 5))[0]
            service = rng.choice(SERVICES)

        message = rng.choice(ERRORS if level == "ERROR" else INFOS)
        lines.append(
            f"{timestamp:%Y-%m-%dT%H:%M:%S}Z {level} {service} "
            f"req=r{index:06d} {message}"
        )
        if index % 997 == 0:
            lines.append("### intentionally malformed synthetic row ###")

    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("count", type=int)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    lines = generate_lines(args.count, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
```

Add a generator regression test that calls `generate_lines(5000, seed=42)` twice and asserts identical lists. When 5,000 lines are generated, assert that the known incident segment has at least 40 consecutive `payments` `ERROR` events and that the burst command detects it with `--window-seconds 120 --threshold 10`.

---

## 11. Milestone 7 — README, commands, and investigation walkthrough

### Recommended README contents

Include purpose, prerequisites, install steps, the grammar, commands, exit codes, module design, tests, limitations, and the incident walkthrough. The following commands are the intended interface:

```bash
# Generate a reproducible synthetic dataset
uv run python tools/make_logs.py data/app.log 5000 --seed 42

# Overall level/message/service report
uv run logscope data/app.log summary

# Machine-readable summary
uv run logscope --format json data/app.log summary

# Detect a burst: at least 10 errors within 120 seconds
uv run logscope data/app.log bursts --window-seconds 120 --threshold 10

# Trace a synthetic request
uv run logscope data/app.log trace r002001

# Inclusive UTC time filter
uv run logscope --since 2026-03-01T08:30:00Z --until 2026-03-01T09:00:00Z data/app.log summary

# Permit up to 10% malformed nonblank lines
uv run logscope --max-malformed-rate 0.10 data/app.log summary
```

**Argument placement:** global options (`--format`, `--since`, `--until`, `--max-malformed-rate`) are placed before the file list and subcommand in these examples. Subcommand-specific options follow the subcommand.

Do not claim actual sample output until you have run these commands against generated data. Capture the real output and include it in the README. For a small hand-written example, show the exact lines used and the exact resulting report.

### `learning-notes.md`

Record at least three mistakes using this template:

```markdown
## Mistake: <short title>
- Expected:
- Actual:
- Evidence (test/command):
- Root cause:
- Fix:
- Regression test:
- What I will do differently next time:
```

---

## 12. Testing plan and coverage matrix

| Concern | Minimum evidence |
|---|---|
| Grammar | Valid line with request ID, without request ID, empty message, malformed shape, invalid date |
| Encoding | Invalid UTF-8 line is replaced and counted |
| Streaming | Reader yields incrementally; no `read_text()` or `readlines()` in parser |
| Stats | Empty file, whitespace-only file, malformed-only file, valid + malformed |
| Time | Explicit timezone required; normalize offset to UTC; inclusive bounds; invalid range |
| Counts | Empty events; every supported level; deterministic ordering |
| Top errors | Only ERROR/CRITICAL count; tie-break by message; invalid top-N rejected |
| Service rate | No division by zero; deterministic service ordering |
| Burst | Below threshold, exactly threshold, exact window boundary, threshold 1, negative window rejected |
| Trace | Existing ID, absent ID, multiple services, stable chronological ordering |
| CLI | JSON parses; diagnostics only stderr; missing path exit 1; malformed threshold exit 1; bad args exit 2 |
| Generator | Same seed produces identical bytes; planted incident is detectable |
| Regression | Every bug discovered during implementation gets a failing test before its fix |
| Large input | Generate at least 1 million lines and record wall time / peak RSS; do not assert machine-specific timings |

Run the tests using `tmp_path` and `capsys`. Tests should not depend on the repository current directory or today's date.

---

## 13. Quality gate and Git workflow

Run before every commit:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy --strict src
uv run pytest -q
```

Then verify formatting without changing files:

```bash
uv run ruff format --check .
git status --short
```

Suggested small commits:

```text
docs(logscope): define log grammar and investigation contract
feat(logscope): parse events and count malformed lines
feat(logscope): add deterministic summary analysis
feat(logscope): detect error bursts with a sliding window
feat(logscope): add request tracing and time filters
feat(logscope): add JSON and text reports
test(logscope): cover malformed bytes and boundary timestamps
docs(logscope): document incident walkthrough and limitations
```

Once acceptance is complete:

```bash
git tag project-2-done
```

---

## 14. Senior-engineer audit report

This audit distinguishes **design requirements** from **verified execution**. A code sample in a Markdown guide is not proof that the entire project passes the toolchain. Run the full quality gate locally before marking the project complete.

### Findings and required remediation

| ID | Severity | Finding | Required fix / acceptance evidence |
|---|---|---|---|
| L01 | High | A regex match alone does not validate calendar dates | `parse_line()` catches `ValueError` from `strptime`; tests include month 13 and impossible dates |
| L02 | High | `argparse` must not show a traceback for malformed time values | Use the `cli_time()` adapter shown in M6; test exit code 2 |
| L03 | High | Malformed data must be visible without corrupting JSON output | Report goes to stdout; warning/diagnostic to stderr; parse stdout with `json.loads()` |
| L04 | High | Burst detection requires ordered timestamps | Document per-file and cross-file order assumptions; test boundary; implement `heapq.merge` if global order is required |
| L05 | High | A generator alone does not guarantee constant memory if callers materialize it | Current CLI collects events for filters/trace. State this honestly; summary streaming optimization is a stretch goal |
| L06 | Medium | Repeated error tie ordering must be deterministic | Sort by descending count then ascending message; regression test ties |
| L07 | Medium | Service error rate denominator must be defined | Use error events / all valid filtered events for each service; test service with no errors |
| L08 | Medium | Invalid UTF-8 can otherwise disappear silently | Decode with replacement, count replacement-character lines as malformed, report both counts |
| L09 | Medium | Empty input can divide by zero | Define malformed rate as 0 for zero nonblank lines |
| L10 | Medium | Inclusive/exclusive window ambiguity creates off-by-one bugs | Window is inclusive; test an error exactly at the duration boundary |
| L11 | Medium | Trace results can be emitted in file order rather than time order | Sort trace matches by timestamp; preserve stable ordering for equal timestamps |
| L12 | Medium | Sample logs must never contain real personal or production data | Generator produces synthetic logs only; no real logs committed |
| L13 | Medium | Large-line and million-line behaviour needs evidence | Add a 200 KB line test and a documented 1M-line smoke test; record measured results rather than promising fixed timing |
| L14 | Medium | The generator must be reproducible | Use a local `random.Random(seed)` and test same-seed output equality |
| L15 | Low | `trace_request()` and `filter_events()` materialize results | Accept for this beginner project but document memory complexity and future streaming options |
| L16 | Low | Exact supported log grammar is intentionally narrow | Document unsupported timestamp variants, multiline stack traces, and other log formats |

### Additional code-review checks

- [ ] All Python modules use type hints and focused docstrings.
- [ ] No broad `except Exception`, bare `except`, `eval`, or `exec`.
- [ ] File encoding is explicit.
- [ ] No `print()` in parser or analysis modules.
- [ ] CLI errors use stderr and meaningful exit codes.
- [ ] JSON serialization is deterministic (`sort_keys=True`).
- [ ] No current-time dependency exists in analysis logic.
- [ ] Time comparisons are timezone-aware UTC.
- [ ] CLI argument validation rejects negative thresholds and invalid malformed-rate values.
- [ ] Every bug found during audit has a regression test.
- [ ] README output is captured from a real run, not invented.
- [ ] `uv.lock` is committed and clean-clone setup succeeds.

### Audit verdict

The architecture and scope are appropriate for Stage 1: standard-library-only parsing and analysis, a `src/` package, a thin CLI shell, deterministic synthetic data, focused tests, and explicit operational behaviour. The main risk is overstating scalability: the input reader streams, but the current CLI materializes valid events for filtering, trace, and burst analysis. This is a deliberate first implementation trade-off, not a claim of O(1) total memory.

**Do not mark the project done until** the `cli_time()` adapter is applied, generator regression tests are added, all code is formatted, and Ruff, strict mypy, pytest, README commands, and a clean-clone install have passed in the target environment.

---

## 15. Universal acceptance checklist

- [ ] Prerequisite modules 01–07 and 09 reviewed; design notes completed before implementation.
- [ ] `uv sync` succeeds from a clean clone.
- [ ] `uv.lock` committed.
- [ ] Parser handles valid, malformed, blank, impossible-date, Unicode, and invalid-UTF-8 cases.
- [ ] Input is read line by line; no eager file read in `parser.py`.
- [ ] Summary, burst, trace, time filters, text output, and JSON output work.
- [ ] Missing files produce a clear stderr message and exit 1, without traceback.
- [ ] Invalid arguments/time bounds produce exit 2.
- [ ] Malformed-rate threshold is enforced after a report is produced.
- [ ] Burst window and threshold boundary tests pass.
- [ ] Seeded generator produces reproducible synthetic logs and a detectable planted incident.
- [ ] JSON output remains parseable when warnings are emitted on stderr.
- [ ] `uv run ruff format .`, `uv run ruff check .`, `uv run mypy --strict src`, and `uv run pytest -q` pass without unexplained suppressions.
- [ ] README contains 3–5 real command examples with actual captured output.
- [ ] README documents memory behaviour and timestamp-order assumptions honestly.
- [ ] `learning-notes.md` contains at least three mistakes, root causes, fixes, and regression tests.
- [ ] `git tag project-2-done` created only after all checks pass.

## 16. Interview talking points

Be ready to answer these without reading the code:

1. Why is a generator useful here, and why does the current CLI still use memory proportional to the number of valid events?
2. What is the difference between malformed input and an operational error?
3. Why are timestamps normalized to aware UTC at the parser boundary?
4. Why is `deque` a good fit for a sliding time window?
5. What is the time complexity of the burst detector, assuming sorted input?
6. Why is deterministic tie-breaking important for tests and incident reports?
7. What assumptions does the multi-file implementation make about event order?
8. How would you add global ordering without loading every event into memory?
9. How do you keep JSON stdout valid when the malformed-rate threshold fails?
10. What tests prove the incident detector finds a known planted incident?

---

## 17. Source alignment

This guide is based on the supplied Stage 1 `learning-plan.md` Project 2 section and shared engineering standard, together with the supplied `Roadmap_ptree.md` Stage 1 tree. The roadmap identifies the project brief at:

`Stage 1 — Programming & Computational Thinking/00-Stage-1-Overview/Projects/02-log-investigation-and-reliability-cli.md`

The learning plan defines Project 2 as a 15–25 hour project requiring regex, generators, `Counter`, `deque`, datetime handling, streaming, exit codes, text/JSON reports, malformed-line accounting, error bursts, request tracing, time filters, seeded synthetic logs, and the universal acceptance checklist. The design above preserves those requirements and adds explicit testable contracts where implementation details need to be unambiguous.
