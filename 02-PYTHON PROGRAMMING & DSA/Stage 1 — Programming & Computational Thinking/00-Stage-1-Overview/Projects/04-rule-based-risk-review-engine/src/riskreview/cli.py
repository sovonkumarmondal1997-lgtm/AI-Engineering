"""CLI for deterministic risk assessment."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from .engine import ConfigError, build_engine
from .io import InputError, read_transactions, write_decisions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="riskreview")
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess", help="assess transactions against configured rules")
    assess.add_argument("--transactions", type=Path, required=True)
    assess.add_argument("--rules", type=Path, required=True, dest="rules_path")
    assess.add_argument("--out", type=Path, required=True)
    assess.add_argument("--fail-on-reject", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "assess":
        parser.error("unsupported command")
    try:
        input_path: Path = args.transactions
        output_path: Path = args.out
        config_path: Path = args.rules_path
        if not input_path.is_file():
            raise InputError(f"transactions file does not exist: {input_path}")
        if not config_path.is_file():
            raise ConfigError(f"rules file does not exist: {config_path}")
        if input_path.resolve() == output_path.resolve():
            raise ValueError("output path must not overwrite the input CSV")
        bundle = build_engine(config_path)
        transactions = read_transactions(input_path)
        assessments = bundle.engine.assess_all(transactions)
        write_decisions(output_path, assessments, bundle.config_sha256)
        counts = Counter(item.decision.value for item in assessments)
        rule_counts = Counter(hit.rule_id for item in assessments for hit in item.hits)
        summary = {
            "transactions_assessed": len(assessments),
            "decisions": {key: counts.get(key, 0) for key in ("approve", "review", "reject")},
            "top_rules_fired": [
                {"rule_id": rule_id, "count": count}
                for rule_id, count in sorted(rule_counts.items(), key=lambda pair: (-pair[1], pair[0]))[:5]
            ],
            "config_sha256": bundle.config_sha256,
            "output": str(output_path),
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        if args.fail_on_reject and counts["reject"]:
            print("riskreview: one or more transactions were rejected", file=sys.stderr)
            return 1
        return 0
    except (OSError, ValueError, ConfigError, InputError) as exc:
        print(f"riskreview: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
