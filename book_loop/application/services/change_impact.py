from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from collections.abc import Iterable

from book_loop.domain.models import CanonicalFact


@dataclass(frozen=True)
class ChangeImpact:
    """Evidence-backed impact of changing one canonical fact.

    Dependencies are deliberately conservative: a fact is considered dependent
    only when it explicitly references the changed fact's subject as its object.
    No semantic inference is performed.
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

        dependents: dict[str, list[str]] = defaultdict(list)
        for fact in active_facts:
            if fact.id == changed.id:
                continue
            if fact.object.strip().casefold() == changed.subject.strip().casefold():
                dependents[changed.id].append(fact.id)

        queue = deque([changed.id])
        visited: set[str] = {changed.id}
        affected: list[str] = []

        while queue:
            current = queue.popleft()
            for dependent_id in sorted(dependents.get(current, [])):
                if dependent_id in visited:
                    continue
                visited.add(dependent_id)
                affected.append(dependent_id)
                queue.append(dependent_id)

        return ChangeImpact(
            changed_fact_id=changed.id,
            affected_fact_ids=tuple(affected),
        )
