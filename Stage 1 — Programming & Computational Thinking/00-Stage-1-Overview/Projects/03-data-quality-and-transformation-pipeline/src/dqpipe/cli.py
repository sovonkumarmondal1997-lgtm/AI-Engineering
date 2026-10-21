"""Command-line interface for dqpipe."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .config import load_config
from .pipeline import run_pipeline, write_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dqpipe",
        description="Validate, normalise, deduplicate, and audit an orders CSV.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="run the batch quality pipeline")
    run.add_argument("--input", required=True, type=Path)
    run.add_argument("--out-dir", type=Path, default=Path("out"))
    run.add_argument("--config", type=Path, default=None)
    run.add_argument("--max-reject-rate", type=float, default=None)
    run.add_argument("--dry-run", action="store_true", help="validate and report without writing outputs")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "run":
        parser.error("unsupported command")

    input_path: Path = args.input
    out_dir: Path = args.out_dir
    try:
        if not input_path.is_file():
            raise ValueError(f"input file does not exist or is not a file: {input_path}")
        threshold_from_config, countries = load_config(args.config)
        threshold = threshold_from_config if args.max_reject_rate is None else args.max_reject_rate
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("--max-reject-rate must be between 0 and 1")
        if not __import__("math").isfinite(threshold):
            raise ValueError("--max-reject-rate must be finite")
        report, outcomes, clean_rows = run_pipeline(input_path, out_dir, countries)
        if not args.dry_run:
            output_paths = {
                (out_dir / "clean_orders.csv").resolve(),
                (out_dir / "rejects.csv").resolve(),
                (out_dir / "quality_report.json").resolve(),
            }
            if input_path.resolve() in output_paths:
                raise ValueError("input file must not be one of the pipeline output files")
            write_outputs(out_dir, report, outcomes, clean_rows)
        print(json.dumps(report, indent=2, sort_keys=True))
        if report["reject_rate"] > threshold:
            print(
                f"dqpipe: reject rate {report['reject_rate']:.2%} exceeds threshold "
                f"{threshold:.2%}",
                file=sys.stderr,
            )
            return 1
        return 0
    except (OSError, ValueError, csv.Error) as exc:
        print(f"dqpipe: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
