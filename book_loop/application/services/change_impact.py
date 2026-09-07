from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable
from dataclasses import dataclass

from book_loop.domain.models import CanonicalFact


@dataclass(frozen=True)
class ChangeImpact:
    """Evidence-backed impact of changing one canonical fact.

    Dependencies are deliberately conservative: a fact is considered dependent
    when its subject explicitly matches the object referenced by an upstream
    fact. No semantic inference is performed.
    """

    changed_fact_id: str
    affected_fact_ids: tuple[str, ...]


class ChangeImpactAnalyzer:
    """Build a lightweight dependency graph from explicit canonical references."""

    def analyze(
        self,
        facts: Iterable[CanonicalFact],
        *,
        changed_fact_id: str,
    ) -> ChangeImpact:
        active_facts = [fact for fact in facts if fact.active]
        by_id = {fact.id: fact for fact in active_facts}
        changed = by_id.get(changed_fact_id)
        if changed is None:
            raise KeyError(f"Unknown active canonical fact: {changed_fact_id}")

        by_subject: dict[str, list[str]] = defaultdict(list)
        for fact in active_facts:
            if fact.id != changed.id:
                by_subject[fact.subject.strip().casefold()].append(fact.id)

        queue = deque([changed.id])
        visited: set[str] = {changed.id}
        affected: list[str] = []

        while queue:
            current = by_id[queue.popleft()]
            reference = current.object.strip().casefold()
            for dependent_id in sorted(by_subject.get(reference, [])):
                if dependent_id in visited:
                    continue
                visited.add(dependent_id)
                affected.append(dependent_id)
                queue.append(dependent_id)

        return ChangeImpact(
            changed_fact_id=changed.id,
            affected_fact_ids=tuple(affected),
        )
