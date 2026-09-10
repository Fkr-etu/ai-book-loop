from __future__ import annotations

import json
from pathlib import Path


GOLD_PATH = Path("tests/fixtures/livre1-consistency-gold.json")
EXPECTED_CANDIDATE_IDS = {
    "d0c5346f-77be-5de7-af87-f37ea4f50b20",
    "8713171d-d8f6-5ec3-8980-14130a288b36",
    "fb9f6160-34e1-53fb-99b1-65a1f9be7346",
    "52a46538-5391-5b91-bea0-105d980c2778",
    "aa30cdc2-d158-5bc2-b381-c2ea2d7ca996",
    "fd977281-c359-5659-9390-e2dd100dda75",
}


def load_gold() -> dict:
    return json.loads(GOLD_PATH.read_text(encoding="utf-8"))


def test_livre1_gold_freezes_real_audit_candidate_universe() -> None:
    payload = load_gold()
    annotations = payload["annotations"]
    candidate_ids = {item["candidate_id"] for item in annotations}

    assert payload["corpus"] == "Livre I"
    assert payload["candidate_count"] == 6
    assert candidate_ids == EXPECTED_CANDIDATE_IDS
    assert len(annotations) == len(candidate_ids) == 6


def test_livre1_gold_has_only_supported_labels() -> None:
    payload = load_gold()
    labels = {item["label"] for item in payload["annotations"]}

    assert labels <= {"contradiction", "evolution", "compatible", "noise"}
    assert all(item["rationale"] for item in payload["annotations"])
    assert all(len(item["evidence"]) == 2 for item in payload["annotations"])
