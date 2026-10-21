"""Configuration loading and validation."""

from __future__ import annotations

import math
import tomllib
from pathlib import Path
from typing import Any


DEFAULT_COUNTRIES = {
    "usa": "US",
    "united states": "US",
    "us": "US",
    "uk": "GB",
    "gb": "GB",
    "india": "IN",
    "in": "IN",
}
DEFAULT_MAX_REJECT_RATE = 0.20


def load_config(path: Path | None) -> tuple[float, dict[str, str]]:
    """Load TOML configuration, or return documented defaults when no file is given."""
    if path is None:
        return DEFAULT_MAX_REJECT_RATE, dict(DEFAULT_COUNTRIES)

    try:
        with path.open("rb") as handle:
            raw: dict[str, Any] = tomllib.load(handle)
    except OSError as exc:
        raise ValueError(f"cannot read config {path}: {exc}") from None
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"invalid TOML config {path}: {exc}") from None

    pipeline = raw.get("pipeline", {})
    if not isinstance(pipeline, dict):
        raise ValueError("config [pipeline] must be a TOML table")
    threshold = pipeline.get("max_reject_rate", DEFAULT_MAX_REJECT_RATE)
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise ValueError("pipeline.max_reject_rate must be a number between 0 and 1")
    threshold = float(threshold)
    if not math.isfinite(threshold) or not 0.0 <= threshold <= 1.0:
        raise ValueError("pipeline.max_reject_rate must be a finite number between 0 and 1")

    raw_countries = raw.get("countries", DEFAULT_COUNTRIES)
    if not isinstance(raw_countries, dict) or not raw_countries:
        raise ValueError("config [countries] must be a non-empty TOML table")
    countries: dict[str, str] = {}
    for key, code in raw_countries.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("country mapping keys must be non-empty strings")
        if not isinstance(code, str) or len(code) != 2 or not code.isalpha():
            raise ValueError(f"country mapping for {key!r} must be a two-letter code")
        countries[key.strip().casefold()] = code.upper()
    return threshold, countries
