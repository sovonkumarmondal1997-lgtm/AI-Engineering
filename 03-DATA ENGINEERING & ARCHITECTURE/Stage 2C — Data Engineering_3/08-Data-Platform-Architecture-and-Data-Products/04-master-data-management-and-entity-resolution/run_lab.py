from pathlib import Path
import json
from resolver import ROOT, load_records, classify_pairs, metrics, candidate_recall, connected_components, survivorship, make_master_id_registry, save_json

def run():
    records = load_records(ROOT / "data/source_records.json")
    baseline = classify_pairs(records, method="deterministic")
    probabilistic = classify_pairs(records, method="probabilistic", low=3.0, high=9.0)
    stats = {
        "record_count": len(records),
        "candidate_generation": candidate_recall(records),
        "deterministic_metrics": metrics(baseline),
        "probabilistic_metrics": metrics(probabilistic),
        "uncertain_pairs": [p for p in probabilistic if p["decision"] == "review"],
        "clusters": connected_components(records, probabilistic),
    }
    xref, conflicts = make_master_id_registry(records)
    golden = []
    by_id = {r["record_id"]:r for r in records}
    for comp in stats["clusters"]:
        g = survivorship([by_id[rid] for rid in comp])
        mids = {xref.get(rid) for rid in comp}
        g["master_id"] = next(iter(mids)) if len(mids) == 1 else None
        golden.append(g)
    stats["cross_reference"] = [{"record_id":k,"master_id":v} for k,v in sorted(xref.items())]
    stats["identity_events"] = conflicts
    stats["golden_records"] = golden
    save_json(ROOT / "reports/run_report.json", stats)
    print(json.dumps({
        "record_count": stats["record_count"],
        "candidate_generation": stats["candidate_generation"],
        "deterministic_metrics": stats["deterministic_metrics"],
        "probabilistic_metrics": stats["probabilistic_metrics"],
        "review_queue_size": len(stats["uncertain_pairs"]),
        "cluster_count": len(stats["clusters"]),
        "cross_reference_rows": len(stats["cross_reference"]),
        "report": str(ROOT / "reports/run_report.json")
    }, indent=2))
    return stats

if __name__ == "__main__":
    run()
