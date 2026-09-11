from book_loop.application.use_cases.grill import MAX_HISTORY_MESSAGES, Grill, GrillMessage, GrillResponse
from book_loop.domain.models import BookState, CreativeBrief, GrillPersonality


class RecordingLLM:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate_structured(self, **kwargs):
        self.calls.append(kwargs)
        return GrillResponse(reply="Je vois une faiblesse dans cette motivation.", question="Qu'est-ce qui empêche réellement ton personnage de partir ?", done=False)


def make_book(personality: GrillPersonality = GrillPersonality.CHALLENGER) -> BookState:
    return BookState(id="book-1", owner_id="user-1", title="Le dernier hiver", theme="Roman · Policier", author_idea="Une inspectrice reprend une vieille affaire.", creative_brief=CreativeBrief(premise="Une inspectrice reprend une vieille affaire."), lore="Paris en hiver.", constraints=["Rester réaliste"], grill_personality=personality)


def test_grill_returns_minimal_structured_contract_and_uses_personality() -> None:
    llm = RecordingLLM()
    result = Grill(llm).execute(book=make_book(GrillPersonality.DEVILS_ADVOCATE), messages=[GrillMessage(role="user", content="Elle poursuit l'enquête par devoir.")], turn=1)
    assert result.question
    assert result.done is False
    assert "contre-exemple" in str(llm.calls[0]["system_prompt"])
    assert llm.calls[0]["schema"] is GrillResponse


def test_grill_bounds_history_before_sending_it_to_the_model() -> None:
    llm = RecordingLLM()
    messages = [GrillMessage(role="user", content=f"message {i}") for i in range(MAX_HISTORY_MESSAGES + 5)]
    Grill(llm).execute(book=make_book(), messages=messages, turn=1)
    prompt = str(llm.calls[0]["user_prompt"])
    assert "message 0" not in prompt
    assert f"message {MAX_HISTORY_MESSAGES + 4}" in prompt


def test_grill_stops_after_the_session_turn_limit_without_calling_llm() -> None:
    llm = RecordingLLM()
    result = Grill(llm).execute(book=make_book(), messages=[], turn=9)
    assert result.done is True
    assert result.question is None
    assert llm.calls == []


def test_grill_message_rejects_empty_content() -> None:
    try:
        GrillMessage(role="user", content="")
    except ValueError:
        return
    raise AssertionError("Empty Grill messages must be rejected")
