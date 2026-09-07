from __future__ import annotations

import re
import unicodedata
import uuid
from collections.abc import Iterable
from datetime import datetime

from book_loop.domain.consistency import ConsistencyIssue
from book_loop.domain.models import Assertion, Evidence

_NAMESPACE = uuid.UUID("4f3a8f1e-7e2b-4f9b-9f5d-5c7d6b6a1d2e")
_RELATIVE_DATE_MARKERS = {
    "aujourd",
    "aujourd'hui",
    "demain",
    "hier",
    "today",
    "tomorrow",
    "yesterday",
    "next",
    "last",
    "prochain",
    "prochaine",
    "dernier",
    "derniere",
}


def normalize(value: str) -> str:
    """Normalize labels conservatively for deterministic rule matching."""
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return " ".join(text.lower().strip().split())


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", normalize(value)).strip("_")


def stable_issue_id(*, rule_id: str, book_id: str, left: Assertion, right: Assertion) -> str:
    pair = ":".join(sorted((left.id, right.id)))
    return str(uuid.uuid5(_NAMESPACE, f"{book_id}:{rule_id}:{pair}"))


def evidence_map(evidence: Iterable[Evidence]) -> dict[str, Evidence]:
    return {item.id: item for item in evidence}


def build_issue(
    *,
    rule_id: str,
    book_id: str,
    category: str,
    severity: str,
    message: str,
    left: Assertion,
    right: Assertion,
    evidence: dict[str, Evidence],
) -> ConsistencyIssue:
    left_evidence = evidence.get(left.evidence_id)
    right_evidence = evidence.get(right.evidence_id)
    return ConsistencyIssue(
        id=stable_issue_id(rule_id=rule_id, book_id=book_id, left=left, right=right),
        category=category,
        severity=severity,
        status="open",
        message=message,
        left_assertion_id=left.id,
        right_assertion_id=right.id,
        left_statement=left.statement,
        right_statement=right.statement,
        left_evidence=left_evidence.excerpt if left_evidence else "",
        right_evidence=right_evidence.excerpt if right_evidence else "",
        confidence=min(left.confidence, right.confidence),
        rule_id=rule_id,
        metadata={"detector": "narrative"},
    )


def active_assertions(assertions: Iterable[Assertion]) -> list[Assertion]:
    return [item for item in assertions if item.status.value != "rejected"]


def parse_year(value: str) -> int | None:
    """Extract an explicit year without interpreting relative narrative dates."""
    match = re.search(r"\b(\d{4})\b", normalize(value))
    if match:
        return int(match.group(1))

    normalized = normalize(value)
    if not normalized or any(marker in normalized.split() for marker in _RELATIVE_DATE_MARKERS):
        return None

    try:
        import dateparser
    except ImportError:
        return None

    parsed = dateparser.parse(
        value,
        settings={"RETURN_AS_TIMEZONE_AWARE": False, "PREFER_DAY_OF_MONTH": "first"},
    )
    return parsed.year if isinstance(parsed, datetime) else None


def affirmative(value: str) -> bool:
    return normalize(value) in {"true", "yes", "oui", "1", "alive", "vivant", "married", "marie"}
