import pytest

from book_loop.domain.models import DiagnosticCategory, DiagnosticSeverity, LinguisticCheckStatus
from book_loop.infrastructure.linguistic.spacy import SpacyFrenchChecker


class FakeToken:
    def __init__(self, text, idx, pos_, morph, dep_, children=()):
        self.text = text
        self.idx = idx
        self.pos_ = pos_
        self.morph = morph
        self.dep_ = dep_
        self.children = list(children)
        self.is_space = False
        self.is_punct = text in {".", ",", "!", "?"}


class FakeMorph:
    def __init__(self, number):
        self.number = number

    def get(self, name):
        return [self.number] if name == "Number" else []


class FakeSentence:
    def __init__(self, tokens):
        self.tokens = tokens
        self.start_char = tokens[0].idx
        self.end_char = tokens[-1].idx + len(tokens[-1].text)

    def __iter__(self):
        return iter(self.tokens)


class FakeDoc:
    def __init__(self, sentences):
        self.sents = sentences


def test_detects_subject_verb_number_disagreement() -> None:
    subject = FakeToken("Les veilleurs", 0, "NOUN", FakeMorph("Plur"), "nsubj")
    verb = FakeToken("veille", 14, "VERB", FakeMorph("Sing"), "ROOT", [subject])
    doc = FakeDoc([FakeSentence([subject, verb])])

    checker = SpacyFrenchChecker(nlp=lambda _: doc)
    result = checker.check("Les veilleurs veille")

    assert result.status == LinguisticCheckStatus.ISSUES_FOUND
    assert len(result.diagnostics) == 1
    diagnostic = result.diagnostics[0]
    assert diagnostic.category == DiagnosticCategory.AGREEMENT
    assert diagnostic.severity == DiagnosticSeverity.ERROR
    assert diagnostic.rule_id == "SPACY_FR_SUBJECT_VERB_NUMBER"
    assert diagnostic.start_offset == 0
    assert diagnostic.end_offset == len("Les veilleurs veille")


def test_sentence_fragment_is_warning_not_error() -> None:
    tokens = [
        FakeToken("Une", 0, "DET", FakeMorph("Sing"), "det"),
        FakeToken("nuit", 4, "NOUN", FakeMorph("Sing"), "ROOT"),
        FakeToken("très", 9, "ADV", FakeMorph("Sing"), "advmod"),
        FakeToken("silencieuse", 14, "ADJ", FakeMorph("Sing"), "amod"),
        FakeToken(".", 25, "PUNCT", FakeMorph("Sing"), "punct"),
    ]
    doc = FakeDoc([FakeSentence(tokens)])
    result = SpacyFrenchChecker(nlp=lambda _: doc).check("Une nuit très silencieuse.")

    assert result.status == LinguisticCheckStatus.ISSUES_FOUND
    assert result.diagnostics[0].category == DiagnosticCategory.SYNTAX
    assert result.diagnostics[0].severity == DiagnosticSeverity.WARNING


def test_loads_model_lazily() -> None:
    calls = []

    def loader(name):
        calls.append(name)
        return lambda _: FakeDoc([])

    checker = SpacyFrenchChecker(loader=loader)
    assert calls == []
    checker.check("Marseille.")
    assert calls == ["fr_core_news_sm"]


def test_non_french_language_is_rejected() -> None:
    checker = SpacyFrenchChecker(nlp=lambda _: FakeDoc([]))
    with pytest.raises(ValueError, match="only French"):
        checker.check("Hello.", language="en")
