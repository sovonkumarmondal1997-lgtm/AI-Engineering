import pytest
from resolver import (
    ROOT, load_records, candidate_pairs, candidate_recall, classify_pairs, metrics,
    deterministic_decision, standardise, survivorship, make_master_id_registry,
    norm_email, norm_phone, norm_date, pair_count, decision_from_score,
)


def test_dataset_is_reproducible_and_has_ground_truth():
    records = load_records(ROOT / "data/source_records.json")
    assert len(records) == 21
    assert len({r["entity_id"] for r in records}) == 11
    assert len({r["record_id"] for r in records}) == len(records)


def test_candidate_generation_reduces_pairs_and_keeps_all_synthetic_true_pairs():
    records = load_records(ROOT / "data/source_records.json")
    result = candidate_recall(records)
    assert result["all_possible_pairs"] == 210
    assert result["candidate_pairs"] == 13
    assert result["all_ground_truth_match_pairs"] == 11
    assert result["candidate_true_pairs"] == 11
    assert result["blocking_recall"] == 1.0
    assert 0 < result["reduction_ratio"] < 1


def test_deterministic_pair_uses_explicit_rule_and_canonical_phone():
    a = standardise({"record_id":"a","name":"A B","email":"x@y.com","phone":"9876543210","dob":"2000-01-01","postcode":"700001"})
    b = standardise({"record_id":"b","name":"A B","email":"X@Y.COM","phone":"+91 98765 43210","dob":"2000-01-01T00:00:00Z","postcode":"700001"})
    decision, _ = deterministic_decision(a, b)
    assert decision == "match"
    assert a["phone_norm"] == b["phone_norm"]
    assert a["dob_norm"] == b["dob_norm"]


def test_email_normalisation_preserves_significant_punctuation():
    assert norm_email(" Jane.Doe+sales@Example.com ") == "jane.doe+sales@example.com"
    assert norm_email("jane.doe@example.com") != norm_email("janedoe@example.com")


def test_phone_normalisation_does_not_truncate_foreign_country_codes():
    assert norm_phone("9876543210") == norm_phone("+91 98765 43210")
    assert norm_phone("+1 9876543210") != norm_phone("+91 9876543210")


def test_date_normalisation_handles_iso_datetime_and_rejects_ambiguous_dates():
    assert norm_date("2000-01-01T23:30:00Z") == "2000-01-01"
    assert norm_date("2000-01-01") == "2000-01-01"
    assert norm_date("03/04/2001") == ""
    assert norm_date("not-a-date") == ""


def test_threshold_boundaries_are_consistent():
    assert decision_from_score(2.999, 3.0, 9.0) == "non_match"
    assert decision_from_score(3.0, 3.0, 9.0) == "review"
    assert decision_from_score(8.999, 3.0, 9.0) == "review"
    assert decision_from_score(9.0, 3.0, 9.0) == "match"


def test_pair_metrics_are_bounded_and_report_denominator_edge_cases():
    records = load_records(ROOT / "data/source_records.json")
    for method in ["deterministic", "probabilistic"]:
        result = metrics(classify_pairs(records, method=method))
        assert 0 <= result["precision"] <= 1
        assert 0 <= result["recall_within_candidates"] <= 1
        assert 0 <= result["f1_within_candidates"] <= 1
        assert result["unlabelled_candidate_pairs"] == 0

    no_predictions = metrics([{"ground_truth_match": True, "decision": "review"}])
    assert no_predictions["precision"] is None
    assert no_predictions["recall_within_candidates"] == 0.0
    assert no_predictions["f1_within_candidates"] == 0.0
    assert no_predictions["precision_defined"] is False

    no_positive_truth = metrics([{"ground_truth_match": False, "decision": "non_match"}])
    assert no_positive_truth["precision"] is None
    assert no_positive_truth["recall_within_candidates"] is None
    assert no_positive_truth["f1_within_candidates"] is None


def test_unlabelled_pairs_do_not_become_ground_truth_matches():
    records = [
        standardise({"record_id": "a", "email": "same@example.com"}),
        standardise({"record_id": "b", "email": "same@example.com"}),
    ]
    pairs = classify_pairs(records)
    assert len(pairs) == 1
    assert pairs[0]["ground_truth_match"] is None
    result = metrics(pairs)
    assert result["unlabelled_candidate_pairs"] == 1
    assert result["precision"] is None


def test_uncertain_pairs_are_not_auto_merged():
    records = load_records(ROOT / "data/source_records.json")
    decisions = classify_pairs(records, method="probabilistic")
    review = [p for p in decisions if p["decision"] == "review"]
    assert review
    from resolver import connected_components
    clusters = [set(c) for c in connected_components(records, decisions)]
    assert not any("CRM-012" in c and ("CRM-002" in c or "WEB-102" in c) for c in clusters)


def test_survivorship_is_deterministic_and_auditable():
    records = load_records(ROOT / "data/source_records.json")
    cluster = [r for r in records if r["entity_id"] == "E1"]
    g = survivorship(cluster)
    assert g["name"]["source_record_id"] == "CRM-001"
    assert g["email"]["source_record_id"] == "WEB-101"
    assert g["source_record_ids"] == ["BILL-201", "CRM-001", "WEB-101"]
    assert g["dob"]["rule"] == "complete"


def test_incremental_registry_preserves_existing_ids_without_merge_or_split():
    records = load_records(ROOT / "data/source_records.json")
    old_xref, old_events = make_master_id_registry(records)
    assert old_events == []
    incremental = load_records(ROOT / "data/incremental_records.json")
    all_records = records + incremental
    new_xref, events = make_master_id_registry(all_records, old_xref)
    for rid, mid in old_xref.items():
        assert new_xref[rid] == mid
    assert new_xref["WEB-110"] == old_xref["CRM-010"]
    assert new_xref["CRM-011"] not in set(old_xref.values())
    assert events == []


def test_split_gets_distinct_id_and_stewardship_event():
    records = load_records(ROOT / "data/source_records.json")
    # CRM-001 and WEB-101 form one component; unrelated CRM-003 is a separate component.
    subset = [r for r in records if r["record_id"] in {"CRM-001", "WEB-101", "CRM-003"}]
    previous = {"CRM-001": "M-000001", "WEB-101": "M-000001", "CRM-003": "M-000001"}
    registry, events = make_master_id_registry(subset, previous)
    assert registry["CRM-001"] == registry["WEB-101"] == "M-000001"
    assert registry["CRM-003"] != "M-000001"
    assert len({registry[r["record_id"]] for r in subset}) == 2
    assert any("split_detected" in event["action"] for event in events)


def test_merge_of_two_existing_master_ids_is_not_silent():
    records = load_records(ROOT / "data/source_records.json")
    subset = [r for r in records if r["record_id"] in {"CRM-001", "WEB-101"}]
    previous = {"CRM-001": "M-000001", "WEB-101": "M-000002"}
    registry, events = make_master_id_registry(subset, previous)
    assert registry["CRM-001"] == "M-000001"
    assert registry["WEB-101"] == "M-000002"
    assert any(event["action"] == "merge_conflict_steward_review_required" for event in events)


def test_invalid_method_thresholds_and_duplicate_ids_fail_explicitly():
    records = load_records(ROOT / "data/source_records.json")
    with pytest.raises(ValueError):
        classify_pairs(records, method="typo")
    with pytest.raises(ValueError):
        classify_pairs(records, low=10, high=3)
    duplicate = [standardise({"record_id": "x"}), standardise({"record_id": "x"})]
    with pytest.raises(ValueError, match="duplicate record_id"):
        candidate_pairs(duplicate)


def test_blocking_recall_is_undefined_without_labelled_true_pairs():
    records = [
        standardise({"record_id": "a", "entity_id": "E1", "email": "a@example.com"}),
        standardise({"record_id": "b", "entity_id": "E2", "email": "b@example.com"}),
    ]
    result = candidate_recall(records)
    assert result["all_ground_truth_match_pairs"] == 0
    assert result["blocking_recall"] is None
    assert result["blocking_recall_defined"] is False


def test_ten_million_pair_formula_and_invalid_sizes():
    assert pair_count(10_000_000) == 49_999_995_000_000
    assert pair_count(0) == 0
    assert pair_count(1) == 0
    with pytest.raises(ValueError):
        pair_count(-1)
    with pytest.raises(ValueError):
        pair_count(1.5)
