from __future__ import annotations

import argparse
import json
from pathlib import Path

from book_loop.application.services.linguistic_evaluation import EvaluationCase, evaluate_checker
from book_loop.domain.models import DiagnosticCategory
from book_loop.infrastructure.linguistic.spacy import SpacyFrenchChecker


def load_cases(path: Path) -> list[EvaluationCase]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [
        EvaluationCase(
            id=row["id"],
            text=row["text"],
            expected_categories=frozenset(DiagnosticCategory(value) for value in row["expected_categories"]),
            literary=bool(row.get("literary", False)),
        )
        for row in rows
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the French linguistic checker against the controlled corpus.")
    parser.add_argument("--corpus", type=Path, default=Path("tests/fixtures/linguistic_corpus.json"))
    parser.add_argument("--model", default="fr_core_news_sm")
    args = parser.parse_args()

    cases = load_cases(args.corpus)
    metrics = evaluate_checker(SpacyFrenchChecker(model_name=args.model), cases)
    print(json.dumps({
        "cases": metrics.cases,
        "expected_findings": metrics.expected_findings,
        "detected_findings": metrics.detected_findings,
        "true_positives": metrics.true_positives,
        "false_positives": metrics.false_positives,
        "false_negatives": metrics.false_negatives,
        "precision": metrics.precision,
        "recall": metrics.recall,
        "literary_false_positives": metrics.literary_false_positives,
        "literary_false_positive_rate": metrics.literary_false_positive_rate,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
