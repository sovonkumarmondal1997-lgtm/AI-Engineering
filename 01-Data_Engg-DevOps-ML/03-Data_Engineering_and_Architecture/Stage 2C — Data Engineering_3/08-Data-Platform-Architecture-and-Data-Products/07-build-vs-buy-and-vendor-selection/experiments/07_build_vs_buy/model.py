from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
ASSUMPTIONS = json.loads((ROOT / "assumptions.json").read_text(encoding="utf-8"))
SCORECARD = json.loads((ROOT / "scorecard.json").read_text(encoding="utf-8"))
OUTPUTS = ROOT / "outputs"


def validate_inputs() -> None:
    rate = ASSUMPTIONS["fully_loaded_engineering_hourly_rate"]
    if not isinstance(rate, (int, float)) or rate <= 0:
        raise ValueError("Fully loaded hourly rate must be positive")
    if not ASSUMPTIONS["horizons_years"] or any(not isinstance(h, int) or h <= 0 for h in ASSUMPTIONS["horizons_years"]):
        raise ValueError("Horizons must be positive integer years")
    if not ASSUMPTIONS["usage_multipliers"] or any(not isinstance(m, (int, float)) or m <= 0 for m in ASSUMPTIONS["usage_multipliers"]):
        raise ValueError("Usage multipliers must be positive")
    required = {
        "annual_vendor_base", "annual_vendor_variable_at_1x",
        "annual_ingestion_infrastructure_at_1x",
        "annual_common_destination_storage_observability_at_1x",
        "annual_data_movement_egress_at_1x",
        "initial_implementation_hours", "annual_maintenance_operations_hours",
        "annual_on_call_hours", "annual_upgrade_hours", "annual_training_refresh_hours",
        "one_time_training_hours", "one_time_migration_hours", "terminal_exit_hours",
    }
    for name, candidate in ASSUMPTIONS["candidates"].items():
        missing = required - candidate.keys()
        if missing:
            raise ValueError(f"Candidate {name} missing assumptions: {sorted(missing)}")
        for field in required:
            if candidate[field] < 0:
                raise ValueError(f"Candidate {name} has negative {field}")
    weights = SCORECARD["weights"]
    if sum(weights.values()) != 100:
        raise ValueError("Scorecard weights must sum to exactly 100")
    if set(SCORECARD["candidate_scores"]) != set(SCORECARD["candidate_labels"]):
        raise ValueError("Each scored candidate must have exactly one display label")
    if set(SCORECARD["candidate_scores"]) != set(SCORECARD["hard_gate_status"]):
        raise ValueError("Every scored candidate must have a hard-gate status")
    if set(SCORECARD["candidate_scores"]) != set(SCORECARD["candidate_rationale"]):
        raise ValueError("Every scored candidate must have a rationale")
    if any(not isinstance(reason, str) or not reason.strip() for reason in SCORECARD["candidate_rationale"].values()):
        raise ValueError("Candidate rationale must be non-empty")
    for name, scores in SCORECARD["candidate_scores"].items():
        if set(scores) != set(weights):
            raise ValueError(f"Candidate {name} must score every criterion exactly once")
        if any(type(score) is not int or not 1 <= score <= 5 for score in scores.values()):
            raise ValueError(f"Candidate {name} scores must be integers in [1, 5]")


def annual_recurring(candidate: dict[str, Any], multiplier: float, rate: float) -> dict[str, float]:
    if multiplier <= 0 or rate <= 0:
        raise ValueError("Usage multiplier and hourly rate must be positive")
    vendor = candidate["annual_vendor_base"] + candidate["annual_vendor_variable_at_1x"] * multiplier
    infrastructure = (
        candidate["annual_ingestion_infrastructure_at_1x"]
        + candidate["annual_common_destination_storage_observability_at_1x"]
    ) * multiplier
    egress = candidate["annual_data_movement_egress_at_1x"] * multiplier
    labour_hours = sum(candidate[field] for field in (
        "annual_maintenance_operations_hours", "annual_on_call_hours",
        "annual_upgrade_hours", "annual_training_refresh_hours",
    ))
    labour = labour_hours * rate
    return {
        "vendor": vendor,
        "infrastructure": infrastructure,
        "egress": egress,
        "labour": labour,
        "total": vendor + infrastructure + egress + labour,
    }


def tco(candidate: dict[str, Any], horizon: int, multiplier: float, rate: float) -> dict[str, float]:
    if not isinstance(horizon, int) or horizon <= 0:
        raise ValueError("Horizon must be a positive integer number of years")
    recurring = annual_recurring(candidate, multiplier, rate)
    initial = candidate["initial_implementation_hours"] * rate
    migration = candidate["one_time_migration_hours"] * rate
    training = candidate["one_time_training_hours"] * rate
    exit_cost = candidate["terminal_exit_hours"] * rate
    one_time = initial + migration + training
    total = one_time + horizon * recurring["total"] + exit_cost
    return {
        "horizon_years": horizon,
        "usage_multiplier": multiplier,
        "initial_implementation": initial,
        "migration": migration,
        "one_time_training": training,
        "vendor_recurring_total": horizon * recurring["vendor"],
        "infrastructure_recurring_total": horizon * recurring["infrastructure"],
        "egress_recurring_total": horizon * recurring["egress"],
        "labour_recurring_total": horizon * recurring["labour"],
        "terminal_exit": exit_cost,
        "tco_including_exit": total,
        "operating_tco_excluding_exit": total - exit_cost,
        "annual_recurring_total": recurring["total"],
    }


def weighted_score(weights: dict[str, int], scores: dict[str, int]) -> float:
    if set(weights) != set(scores):
        raise ValueError("Every weighted criterion must have exactly one score")
    if any(type(w) is not int or w < 0 for w in weights.values()) or sum(weights.values()) != 100:
        raise ValueError("Weights must be non-negative integers summing to exactly 100")
    if any(type(score) is not int or not 1 <= score <= 5 for score in scores.values()):
        raise ValueError("Scores must be integers in [1, 5]")
    return sum(weights[k] * scores[k] for k in weights) / 100


def generate_tco_rows() -> list[dict[str, Any]]:
    validate_inputs()
    rate = ASSUMPTIONS["fully_loaded_engineering_hourly_rate"]
    rows = []
    for key, candidate in ASSUMPTIONS["candidates"].items():
        for horizon in ASSUMPTIONS["horizons_years"]:
            for multiplier in ASSUMPTIONS["usage_multipliers"]:
                rows.append({"candidate": key, "label": candidate["label"], **tco(candidate, horizon, multiplier, rate)})
    return rows


def generate_score_rows() -> list[dict[str, Any]]:
    validate_inputs()
    weights = SCORECARD["weights"]
    rows = []
    for candidate, scores in SCORECARD["candidate_scores"].items():
        rows.append({
            "candidate": candidate,
            "label": SCORECARD["candidate_labels"][candidate],
            "weighted_score_1_to_5": round(weighted_score(weights, scores), 3),
            "evidence_status": "ILLUSTRATIVE_HYPOTHESIS_NOT_MEASURED",
            "hard_gate_status": SCORECARD["hard_gate_status"][candidate],
            "decision_eligible": "NO—HARD GATES NOT ASSESSED",
        })
    return sorted(rows, key=lambda row: row["weighted_score_1_to_5"], reverse=True)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("Cannot write empty CSV")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUTPUTS.mkdir(exist_ok=True)
    tco_rows = generate_tco_rows()
    score_rows = generate_score_rows()
    write_csv(OUTPUTS / "tco_results.csv", tco_rows)
    write_csv(OUTPUTS / "scorecard_results.csv", score_rows)
    print("TCO model: illustrative USD; not vendor quotes")
    print("candidate | horizon | usage | TCO incl. terminal exit")
    for row in tco_rows:
        print(f'{row["candidate"]} | {row["horizon_years"]}y | {row["usage_multiplier"]}x | ${row["tco_including_exit"]:,.0f}')
    print("\nWeighted score hypotheses (not evidence-based final rankings)")
    for row in score_rows:
        print(f'{row["label"]}: {row["weighted_score_1_to_5"]:.3f}/5; gates={row["hard_gate_status"]}; eligible={row["decision_eligible"]}')
    print(f"CSV outputs written under {OUTPUTS}")


if __name__ == "__main__":
    main()
