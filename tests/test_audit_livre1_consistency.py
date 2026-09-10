from types import SimpleNamespace

from scripts.audit_livre1_consistency import (
    AuditRepository,
    AuditResult,
    InMemoryTemporalStore,
    render_candidate_snapshot,
)
from book_loop.application.use_cases.consistency_coverage import measure_coverage
from book_loop.domain.models import Assertion
from book_loop.domain.temporal import TemporalScope, TemporalScopeKind


def _assertion(identifier: str, source_id: str, statement: str, object_: str) -> Assertion:
    return Assertion(
        id=identifier,
        book_id="livre-1",
        source_document_id=source_id,
        chunk_id=f"chunk-{identifier}",
        evidence_id=f"evidence-{identifier}",
        statement=statement,
        subject="Kael",
        predicate="located_in",
        object=object_,
        confidence=0.9,
    )


def test_candidate_snapshot_uses_conflict_id_and_preserves_evidence_fields() -> None:
    repository = AuditRepository([], [], [], [], [])
    repository.sources.extend(
        [
            SimpleNamespace(id="source-1", metadata={"chapter_number": "1"}),
            SimpleNamespace(id="source-2", metadata={"chapter_number": "2"}),
        ]
    )
    repository.assertions.extend(
        [
            _assertion("assertion-1", "source-1", "Kael est dans 403.", "Unité de Recherche 403"),
            _assertion("assertion-2", "source-2", "Kael rejoint les Bas-Fonds.", "Bas-Fonds"),
        ]
    )
    conflict = SimpleNamespace(
        id="stable-candidate-id",
        left_assertion_id="assertion-1",
        right_assertion_id="assertion-2",
    )
    temporal_store = InMemoryTemporalStore()
    temporal_store.save_temporal_scope(
        assertion_id="assertion-1",
        scope=TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=1),
    )
    temporal_store.save_temporal_scope(
        assertion_id="assertion-2",
        scope=TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
    )
    coverage = measure_coverage(repository.assertions, temporal_context_store=temporal_store)
    result = AuditResult(((1, 1, 1), (2, 1, 1)), repository, temporal_store, coverage, (conflict,))

    snapshot = render_candidate_snapshot(result)

    assert '"candidate_id": "stable-candidate-id"' in snapshot
    assert '"assertion_id": "assertion-1"' in snapshot
    assert '"statement": "Kael est dans 403."' in snapshot
    assert '"chapter": "2"' in snapshot
    assert '"story_point": 2' in snapshot
