import json
from pathlib import Path
from metadata_platform import load_all_specs, write_generated, execute_simulation, make_openlineage_event, ROOT

def main():
    specs = load_all_specs()
    plans = write_generated()
    run_rows = []
    for i, spec in enumerate(specs, 1):
        row = execute_simulation(spec, f"demo-run-{i}")
        run_rows.append(row)
        event = make_openlineage_event(spec, row["run_id"], row["status"], row["started_at"], row["ended_at"])
        (ROOT / "reports" / f"{spec.pipeline_id}.openlineage.json").write_text(json.dumps(event, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({
        "pipelines_loaded": len(specs),
        "plans_generated": len(plans),
        "dbt_models_generated": len(list((ROOT/"generated").glob("stg_*.sql"))),
        "governance_policies": len(plans),
        "simulated_runs": len(run_rows),
        "statuses": {r["pipeline_id"]: r["status"] for r in run_rows},
        "output_dir": str(ROOT/"generated"),
        "run_history": str(ROOT/"reports/run_history.jsonl"),
        "note": "local orchestration simulation; no Airflow, Dagster, source, warehouse, or OpenLineage backend invoked"
    }, indent=2))

if __name__ == "__main__":
    main()
