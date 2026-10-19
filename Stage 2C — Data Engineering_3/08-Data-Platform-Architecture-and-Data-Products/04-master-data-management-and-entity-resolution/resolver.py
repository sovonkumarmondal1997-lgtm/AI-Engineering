from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import defaultdict
from datetime import date, datetime
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_PRIORITY = {"crm": 3, "web": 2, "billing": 1}
DEFAULT_PHONE_COUNTRY_CODE = "91"  # This synthetic fixture is India-centric.


def norm_text(value):
    """Conservative Latin-script normalisation for this teaching fixture."""
    if value is None:
        return ""
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", value.casefold())).strip()


def norm_email(value):
    """Case-fold and remove whitespace, but preserve email-significant punctuation."""
    if value is None:
        return ""
    return re.sub(r"\s+", "", str(value).strip()).casefold()


def norm_phone(value, default_country_code=DEFAULT_PHONE_COUNTRY_CODE):
    """Canonicalise common Indian national/international forms without truncating country codes.

    This is deliberately not a global phone-number parser. Production code should use a
    country-aware library such as libphonenumber and retain the source country context.
    """
    digits = re.sub(r"\D", "", str(value or ""))
    if not digits:
        return ""
    if digits.startswith("00"):
        digits = digits[2:]
    if len(digits) == 10:
        return default_country_code + digits
    if len(digits) == 11 and digits.startswith("0"):
        return default_country_code + digits[1:]
    if len(digits) == 12 and digits.startswith(default_country_code):
        return digits
    return digits


def norm_postcode(value):
    return re.sub(r"\W", "", str(value or "").upper())


def norm_date(value):
    """Return ISO date for supported ISO date/datetime strings; invalid values become missing.

    Ambiguous locale formats (for example 03/04/2001) are intentionally not guessed.
    """
    if value is None or not str(value).strip():
        return ""
    raw = str(value).strip()
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError:
        pass
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return parsed.date().isoformat()
    except ValueError:
        return ""


def _validate_records(records):
    seen = set()
    for index, record in enumerate(records):
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError(f"record at index {index} has no non-empty record_id")
        if record_id in seen:
            raise ValueError(f"duplicate record_id: {record_id}")
        seen.add(record_id)


def name_similarity(a, b):
    a, b = norm_text(a), norm_text(b)
    if not a or not b:
        return 0.0
    try:
        from rapidfuzz.fuzz import WRatio
        return WRatio(a, b) / 100.0
    except ImportError:
        return SequenceMatcher(None, a, b).ratio()


def token_similarity(a, b):
    aa, bb = set(norm_text(a).split()), set(norm_text(b).split())
    return len(aa & bb) / len(aa | bb) if aa or bb else 0.0


def standardise(record):
    out = dict(record)
    out.update({
        "name_norm": norm_text(record.get("name", "")),
        "email_norm": norm_email(record.get("email", "")),
        "phone_norm": norm_phone(record.get("phone", "")),
        "address_norm": norm_text(record.get("address", "")),
        "postcode_norm": norm_postcode(record.get("postcode", "")),
        "dob_norm": norm_date(record.get("dob", "")),
    })
    return out


def load_records(path):
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError("records file must contain a JSON array of objects")
    _validate_records(records)
    return [standardise(r) for r in records]


def pair_key(a, b):
    return tuple(sorted((a["record_id"], b["record_id"])))


def pair_count(n):
    """Number of unique unordered pairs among n records."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("n must be a non-negative integer")
    return n * (n - 1) // 2


def candidate_pairs(records):
    """Union of exact-email, canonical-phone, and postcode-plus-surname blocks."""
    _validate_records(records)
    buckets = defaultdict(list)
    for r in records:
        if r.get("email_norm"):
            buckets[("email", r["email_norm"])].append(r)
        if r.get("phone_norm") and len(r["phone_norm"]) >= 8:
            buckets[("phone", r["phone_norm"])].append(r)
        name_tokens = r.get("name_norm", "").split()
        surname = name_tokens[-1] if name_tokens else ""
        if r.get("postcode_norm") and surname:
            buckets[("post_surname", r["postcode_norm"], surname)].append(r)
    pairs = {}
    for bucket in buckets.values():
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                pairs[pair_key(bucket[i], bucket[j])] = (bucket[i], bucket[j])
    return [pairs[k] for k in sorted(pairs)]


def pair_features(a, b):
    email_a, email_b = a.get("email_norm", ""), b.get("email_norm", "")
    phone_a, phone_b = a.get("phone_norm", ""), b.get("phone_norm", "")
    dob_a, dob_b = a.get("dob_norm", ""), b.get("dob_norm", "")
    postcode_a, postcode_b = a.get("postcode_norm", ""), b.get("postcode_norm", "")
    email_exact = bool(email_a and email_a == email_b)
    phone_exact = bool(phone_a and len(phone_a) >= 8 and phone_a == phone_b)
    dob_exact = bool(dob_a and dob_a == dob_b)
    postcode_exact = bool(postcode_a and postcode_a == postcode_b)
    ns = name_similarity(a.get("name", ""), b.get("name", ""))
    ts = token_similarity(a.get("name", ""), b.get("name", ""))
    address = name_similarity(a.get("address", ""), b.get("address", ""))
    return {
        "email_exact": email_exact, "phone_exact": phone_exact, "dob_exact": dob_exact,
        "postcode_exact": postcode_exact, "name_similarity": round(ns, 4),
        "name_token_similarity": round(ts, 4), "address_similarity": round(address, 4),
    }


def deterministic_decision(a, b):
    f = pair_features(a, b)
    # Illustrative rule only: one strong identifier plus corroborating evidence.
    strong = (
        (f["email_exact"] and (f["dob_exact"] or f["name_similarity"] >= 0.86))
        or (f["phone_exact"] and f["dob_exact"] and f["postcode_exact"])
        or (f["email_exact"] and f["phone_exact"])
    )
    return ("match" if strong else "non_match"), f


def fs_inspired_score(a, b):
    """Hand-configured Fellegi–Sunter-inspired score, not a trained probability.

    Actual Fellegi–Sunter weights use comparison-outcome probabilities, e.g. log2(m/u).
    These fixed constants are only a transparent teaching heuristic.
    """
    f = pair_features(a, b)
    score = 0.0
    score += 4.0 if f["email_exact"] else (-1.5 if a.get("email_norm") and b.get("email_norm") else 0.0)
    score += 3.5 if f["phone_exact"] else (-1.0 if a.get("phone_norm") and b.get("phone_norm") else 0.0)
    score += 2.0 if f["dob_exact"] else (-1.0 if a.get("dob_norm") and b.get("dob_norm") else 0.0)
    score += 1.5 if f["postcode_exact"] else (-0.4 if a.get("postcode_norm") and b.get("postcode_norm") else 0.0)
    score += 3.0 if f["name_similarity"] >= 0.96 else (1.5 if f["name_similarity"] >= 0.86 else (-1.0 if f["name_similarity"] < 0.55 else 0.0))
    score += 1.0 if f["address_similarity"] >= 0.88 else 0.0
    return round(score, 3), f


def decision_from_score(score, low, high):
    """Apply inclusive high threshold and exclusive low threshold consistently."""
    return "match" if score >= high else ("non_match" if score < low else "review")


def classify_pairs(records, low=3.0, high=9.0, method="probabilistic"):
    if method not in {"deterministic", "probabilistic"}:
        raise ValueError("method must be 'deterministic' or 'probabilistic'")
    try:
        low, high = float(low), float(high)
    except (TypeError, ValueError) as exc:
        raise ValueError("thresholds must be numeric") from exc
    if not math.isfinite(low) or not math.isfinite(high) or low < 0 or high < low:
        raise ValueError("thresholds must be finite, non-negative, and low <= high")
    out = []
    for a, b in candidate_pairs(records):
        if method == "deterministic":
            decision, feats = deterministic_decision(a, b)
            score = None
        else:
            score, feats = fs_inspired_score(a, b)
            decision = decision_from_score(score, low, high)
        left_entity, right_entity = a.get("entity_id"), b.get("entity_id")
        labelled = left_entity not in (None, "") and right_entity not in (None, "")
        out.append({
            "left_id": a["record_id"], "right_id": b["record_id"],
            "left_entity": left_entity, "right_entity": right_entity,
            "ground_truth_match": (left_entity == right_entity) if labelled else None,
            "score": score, "decision": decision, "features": feats,
        })
    return out


def metrics(pair_results):
    """Pair metrics on labelled candidates; undefined denominators are reported as null."""
    labelled = [r for r in pair_results if isinstance(r.get("ground_truth_match"), bool)]
    tp = sum(r["decision"] == "match" and r["ground_truth_match"] is True for r in labelled)
    fp = sum(r["decision"] == "match" and r["ground_truth_match"] is False for r in labelled)
    fn = sum(r["decision"] != "match" and r["ground_truth_match"] is True for r in labelled)
    truth_pairs = sum(r["ground_truth_match"] is True for r in labelled)
    predicted_pairs = sum(r["decision"] == "match" for r in labelled)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1_denominator = 2 * tp + fp + fn
    f1 = (2 * tp / f1_denominator) if f1_denominator else None
    return {
        "candidate_pairs": len(pair_results),
        "labelled_candidate_pairs": len(labelled),
        "unlabelled_candidate_pairs": len(pair_results) - len(labelled),
        "candidate_ground_truth_match_pairs": truth_pairs,
        "predicted_matches": predicted_pairs,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives_within_candidates": fn,
        "precision": round(precision, 4) if precision is not None else None,
        "recall_within_candidates": round(recall, 4) if recall is not None else None,
        "f1_within_candidates": round(f1, 4) if f1 is not None else None,
        "precision_defined": precision is not None,
        "recall_defined": recall is not None,
        "f1_defined": f1 is not None,
    }


def all_true_pairs(records):
    labelled = [r for r in records if r.get("entity_id") not in (None, "")]
    return sum(1 for i in range(len(labelled)) for j in range(i + 1, len(labelled))
               if labelled[i].get("entity_id") == labelled[j].get("entity_id"))


def candidate_recall(records):
    _validate_records(records)
    labelled = [r for r in records if r.get("entity_id") not in (None, "")]
    cands = candidate_pairs(records)
    found = {pair_key(a, b) for a, b in cands}
    truth = {pair_key(labelled[i], labelled[j]) for i in range(len(labelled))
             for j in range(i + 1, len(labelled))
             if labelled[i].get("entity_id") == labelled[j].get("entity_id")}
    return {
        "record_count": len(records),
        "labelled_record_count": len(labelled),
        "unlabelled_record_count": len(records) - len(labelled),
        "all_possible_pairs": pair_count(len(records)),
        "all_possible_labelled_pairs": pair_count(len(labelled)),
        "all_ground_truth_match_pairs": len(truth),
        "candidate_true_pairs": len(found & truth),
        "blocking_recall": round(len(found & truth) / len(truth), 4) if truth else None,
        "blocking_recall_defined": bool(truth),
        "candidate_pairs": len(found),
        "reduction_ratio": round(1 - len(found) / pair_count(len(records)), 4) if len(records) > 1 else None,
    }


def connected_components(records, decisions):
    """Build components from auto-match edges. Review edges never merge clusters.

    Connected components are a simple demonstration: transitive chains can still cause
    false merges, so production systems need cluster-level constraints and review policies.
    """
    _validate_records(records)
    ids = [r["record_id"] for r in records]
    parent = {x: x for x in ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    known = set(ids)
    for p in decisions:
        if p["decision"] == "match":
            if p["left_id"] not in known or p["right_id"] not in known:
                raise ValueError("decision references a record absent from the supplied record set")
            union(p["left_id"], p["right_id"])
    groups = defaultdict(list)
    for record_id in ids:
        groups[find(record_id)].append(record_id)
    return sorted([sorted(v) for v in groups.values()], key=lambda x: x[0])


def make_master_id_registry(records, previous_xref=None):
    """Assign stable IDs; surface merge conflicts and detect split components.

    Previous mappings for records outside this batch are retained as historical xrefs. For a
    split, the component containing the most previously mapped records keeps the old ID (ties
    break deterministically); other components receive new IDs and an explicit stewardship event.
    A component touching multiple old IDs is not silently merged: its existing mappings remain,
    new records are left unmapped, and a conflict event is emitted.
    """
    _validate_records(records)
    previous_xref = dict(previous_xref or {})
    comps = connected_components(records, classify_pairs(records, method="probabilistic"))
    old_mids_by_comp = [sorted({previous_xref[rid] for rid in comp if rid in previous_xref}) for comp in comps]
    component_indexes_by_mid = defaultdict(list)
    for index, mids in enumerate(old_mids_by_comp):
        for mid in mids:
            component_indexes_by_mid[mid].append(index)

    next_num = 1
    used_ids = set(previous_xref.values())
    for mid in used_ids:
        try:
            next_num = max(next_num, int(str(mid).split("-")[-1]) + 1)
        except ValueError:
            continue

    def allocate_id():
        nonlocal next_num
        while True:
            candidate = f"M-{next_num:06d}"
            next_num += 1
            if candidate not in used_ids:
                used_ids.add(candidate)
                return candidate

    # Choose one deterministic anchor component for every prior ID split across components.
    split_anchor = {}
    events = []
    for mid, indexes in sorted(component_indexes_by_mid.items()):
        if len(indexes) > 1:
            # If an old ID participates in a multi-master conflict component, keep its
            # historical mapping there and allocate new IDs to any other components.
            conflict_indexes = [i for i in indexes if len(old_mids_by_comp[i]) > 1]
            eligible_indexes = [i for i in indexes if old_mids_by_comp[i] == [mid]]
            if conflict_indexes:
                anchor = min(conflict_indexes, key=lambda i: (-sum(previous_xref.get(rid) == mid for rid in comps[i]), comps[i][0]))
            elif eligible_indexes:
                anchor = min(eligible_indexes, key=lambda i: (-sum(previous_xref.get(rid) == mid for rid in comps[i]), comps[i][0]))
            else:
                anchor = min(indexes, key=lambda i: comps[i][0])
            split_anchor[mid] = anchor

    registry = dict(previous_xref)  # Preserve historical xrefs outside this current batch.
    for i, comp in enumerate(comps):
        mids = old_mids_by_comp[i]
        if len(mids) > 1:
            events.append({
                "action": "merge_conflict_steward_review_required",
                "records": comp,
                "existing_master_ids": mids,
                "reason": "automatic component touches multiple previously distinct master IDs",
            })
            # Existing record mappings remain untouched; new records in this component stay unmapped.
            continue
        if len(mids) == 1:
            old_mid = mids[0]
            if old_mid in split_anchor and split_anchor[old_mid] != i:
                new_mid = allocate_id()
                for rid in comp:
                    registry[rid] = new_mid
                events.append({
                    "action": "split_detected_new_id_assigned_steward_review_required",
                    "old_master_id": old_mid,
                    "proposed_master_id": new_mid,
                    "records": comp,
                    "reason": "non-anchor split component receives a new ID; steward must confirm the split",
                })
            else:
                for rid in comp:
                    registry[rid] = old_mid
        else:
            new_mid = allocate_id()
            for rid in comp:
                registry[rid] = new_mid

    # Any current records without mappings belong to an unresolved merge conflict.
    return registry, events


def survivorship(records):
    """Field-specific, deterministic survivorship with field-level provenance.

    Name/postcode use source priority; contact/address use recency; DOB uses record-level
    completeness (count of populated core attributes), then recency and source priority.
    Consent is never inferred from recency or source priority.
    """
    if not records:
        raise ValueError("cannot build golden record from empty cluster")
    entity_records = sorted(records, key=lambda r: r["record_id"])

    def source_priority(record):
        return SOURCE_PRIORITY.get(str(record.get("source", "unknown")).casefold(), 0)

    def completeness(record):
        fields = ("name", "email", "phone", "address", "postcode", "dob")
        return sum(bool(record.get(field)) for field in fields)

    def best(field, mode):
        candidates = [r for r in entity_records if r.get(field) not in (None, "")]
        if not candidates:
            return None
        if mode == "source":
            winner = max(candidates, key=lambda r: (source_priority(r), r.get("updated_at", ""), r["record_id"]))
        elif mode == "recent":
            winner = max(candidates, key=lambda r: (r.get("updated_at", ""), source_priority(r), r["record_id"]))
        elif mode == "complete":
            winner = max(candidates, key=lambda r: (completeness(r), r.get("updated_at", ""), source_priority(r), r["record_id"]))
        else:
            raise ValueError(f"unknown survivorship mode: {mode}")
        return {"value": winner[field], "source_record_id": winner["record_id"], "rule": mode}

    return {
        "master_id": None,
        "name": best("name", "source"),
        "email": best("email", "recent"),
        "phone": best("phone", "recent"),
        "address": best("address", "recent"),
        "postcode": best("postcode", "source"),
        "dob": best("dob", "complete"),
        "source_record_ids": sorted(r["record_id"] for r in entity_records),
        "consent_values": sorted({r.get("consent", "unknown") for r in entity_records}),
        "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship",
    }


def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
