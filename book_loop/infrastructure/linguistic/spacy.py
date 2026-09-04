from __future__ import annotations

from collections.abc import Callable
from typing import Any

from book_loop.domain.models import (
    Diagnostic,
    DiagnosticCategory,
    DiagnosticSeverity,
    DiagnosticSource,
    LinguisticCheckResult,
    LinguisticCheckStatus,
)


class SpacyFrenchChecker:
    """French spaCy adapter focused on conservative structural signals.

    The pipeline is injected or loaded lazily so importing the application does
    not require a French spaCy model. Only high-confidence subject/verb number
    mismatches are emitted as errors; sentence fragments remain warnings because
    literary prose and dialogue intentionally contain fragments.
    """

    def __init__(
        self,
        *,
        model_name: str = "fr_core_news_sm",
        nlp: Any | None = None,
        loader: Callable[[str], Any] | None = None,
    ) -> None:
        if not model_name.strip() and nlp is None:
            raise ValueError("spaCy model name is required")
        self.model_name = model_name
        self._nlp = nlp
        self._loader = loader

    @property
    def nlp(self) -> Any:
        if self._nlp is None:
            loader = self._loader
            if loader is None:
                try:
                    import spacy
                except ImportError as exc:  # pragma: no cover - environment dependent
                    raise RuntimeError("spaCy is not installed") from exc
                loader = spacy.load
            try:
                self._nlp = loader(self.model_name)
            except Exception as exc:
                raise RuntimeError(
                    f"Unable to load spaCy model {self.model_name!r}: {exc}"
                ) from exc
        return self._nlp

    def check(self, text: str, *, language: str = "fr") -> LinguisticCheckResult:
        if language != "fr":
            raise ValueError("SpacyFrenchChecker currently supports only French")
        if not text.strip():
            return LinguisticCheckResult(
                status=LinguisticCheckStatus.NO_ISSUES_FOUND,
                checker="spacy-fr",
            )

        doc = self.nlp(text)
        diagnostics = self._diagnostics(doc, text)
        return LinguisticCheckResult(
            status=(
                LinguisticCheckStatus.ISSUES_FOUND
                if diagnostics
                else LinguisticCheckStatus.NO_ISSUES_FOUND
            ),
            diagnostics=diagnostics,
            checker="spacy-fr",
        )

    @classmethod
    def _diagnostics(cls, doc: Any, text: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for sentence in doc.sents:
            tokens = [token for token in sentence if not token.is_space and not token.is_punct]
            verbs = [token for token in tokens if token.pos_ in {"VERB", "AUX"}]
            if len(tokens) >= 4 and not verbs:
                diagnostics.append(
                    Diagnostic(
                        category=DiagnosticCategory.SYNTAX,
                        severity=DiagnosticSeverity.WARNING,
                        source=DiagnosticSource.NLP,
                        message="Sentence contains no detected verb; verify whether it is an intentional fragment.",
                        start_offset=sentence.start_char,
                        end_offset=sentence.end_char,
                        original_text=text[sentence.start_char : sentence.end_char],
                        confidence=0.75,
                        rule_id="SPACY_FR_NO_VERB",
                        metadata={"signal": "missing_verb"},
                    )
                )

            for token in verbs:
                for child in token.children:
                    if child.dep_ not in {"nsubj", "nsubj:pass"}:
                        continue
                    subject_number = child.morph.get("Number")
                    verb_number = token.morph.get("Number")
                    if not subject_number or not verb_number:
                        continue
                    if subject_number[0] == verb_number[0]:
                        continue
                    start = child.idx
                    end = token.idx + len(token.text)
                    diagnostics.append(
                        Diagnostic(
                            category=DiagnosticCategory.AGREEMENT,
                            severity=DiagnosticSeverity.ERROR,
                            source=DiagnosticSource.NLP,
                            message=(
                                f"Possible subject-verb number disagreement: "
                                f"{child.text!r} / {token.text!r}."
                            ),
                            start_offset=start,
                            end_offset=end,
                            original_text=text[start:end],
                            confidence=0.93,
                            rule_id="SPACY_FR_SUBJECT_VERB_NUMBER",
                            suggestions=[],
                            metadata={
                                "subject": child.text,
                                "verb": token.text,
                                "subject_number": subject_number[0],
                                "verb_number": verb_number[0],
                            },
                        )
                    )
        return diagnostics
