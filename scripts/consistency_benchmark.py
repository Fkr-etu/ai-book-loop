from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable


class GoldLabel(StrEnum):
    CONTRADICTION = "contradiction"
    EVOLUTION = "evolution"
    COMPATIBLE = "compatible"
    NOISE = "noise"


@dataclass(frozen=True, slots=True)
class BenchmarkMetrics:
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    fpr: float


def evaluate(
    *,
    gold: dict[str, GoldLabel],
    predicted_ids: Iterable[str],
) -> BenchmarkMetrics:
    """Evaluate detector candidates against a manually annotated candidate set.

    The gold set is the baseline candidate universe, so non-contradiction labels
    provide the denominator for false-positive rate. Candidates introduced by a
    later detector version are counted as false positives unless explicitly added
    to the gold set.
    """
    predicted = set(predicted_ids)
    contradiction_ids = {
        candidate_id
        for candidate_id, label in gold.items()
        if label is GoldLabel.CONTRADICTION
    }
    non_contradiction_ids = set(gold) - contradiction_ids

    true_positives = len(predicted & contradiction_ids)
    false_negatives = len(contradiction_ids - predicted)
    false_positives = len(predicted - contradiction_ids)

    precision_denominator = true_positives + false_positives
    negative_denominator = len(non_contradiction_ids)

    return BenchmarkMetrics(
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        precision=(true_positives / precision_denominator if precision_denominator else 0.0),
        recall=(true_positives / len(contradiction_ids) if contradiction_ids else 0.0),
        fpr=(false_positives / negative_denominator if negative_denominator else 0.0),
    )
