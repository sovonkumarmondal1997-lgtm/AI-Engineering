"""Optional Splink 4 / DuckDB demonstration.

Install with: python -m pip install -e '.[splink]'
This is separate from the standard-library core lab. It was not executed in the
validation environment because Splink and DuckDB were not installed.
"""
import json
from pathlib import Path

import pandas as pd
import splink.comparison_library as cl
from splink import DuckDBAPI, Linker, SettingsCreator, block_on

from resolver import ROOT, standardise

records = json.loads((ROOT / "data/source_records.json").read_text(encoding="utf-8"))
# Ground-truth labels are evaluation-only and must never enter matching features.
normalised = [standardise(record) for record in records]
df = pd.DataFrame(normalised).drop(columns=["entity_id"], errors="ignore")

settings = SettingsCreator(
    link_type="dedupe_only",
    unique_id_column_name="record_id",
    blocking_rules_to_generate_predictions=[
        block_on("email_norm"),
        block_on("phone_norm"),
        block_on("postcode_norm", "name_norm"),
    ],
    comparisons=[
        cl.ExactMatch("email_norm").configure(term_frequency_adjustments=True),
        cl.ExactMatch("phone_norm"),
        cl.ExactMatch("dob_norm"),
        cl.JaroWinklerAtThresholds("name_norm", [0.9, 0.7]),
        cl.JaroWinklerAtThresholds("address_norm", [0.9, 0.7]),
    ],
    retain_matching_columns=True,
    retain_intermediate_calculation_columns=True,
)

db_api = DuckDBAPI()
df_sdf = db_api.register(df, dataset_display_name="entity_resolution_source_records")
linker = Linker(df_sdf, settings)

# These are model-training operations. They need diagnostics and representative data;
# running them does not guarantee calibrated or unbiased match probabilities.
linker.training.estimate_u_using_random_sampling(max_pairs=1_000_000)
linker.training.estimate_parameters_using_expectation_maximisation(block_on("phone_norm"))

# This threshold is a starting point for inspection, not a production decision threshold.
predictions = linker.inference.predict(threshold_match_weight=3.0)
out = predictions.as_pandas_dataframe()
report_dir = ROOT / "reports"
report_dir.mkdir(parents=True, exist_ok=True)
out.to_csv(report_dir / "splink_predictions.csv", index=False)
print(f"Splink wrote {len(out)} scored candidate predictions to {report_dir / 'splink_predictions.csv'}")
