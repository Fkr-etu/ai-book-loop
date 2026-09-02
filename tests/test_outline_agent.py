import pytest

from book_loop.agents.outline import OutlineAgent


class FakeLLM:
    def __init__(self, response: str):
        self.response = response

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        return self.response


def test_outline_agent_parses_structured_json() -> None:
    agent = OutlineAgent(FakeLLM(
        '{"chapters":[{"number":1,"title":"Opening","objective":"Introduce the hero"}]}'
    ))

    outline = agent.generate(theme="Fantasy", author_idea="Idea", lore="", constraints=[])

    assert outline.chapters[0].number == 1
    assert outline.chapters[0].title == "Opening"


def test_outline_agent_accepts_fenced_json() -> None:
    agent = OutlineAgent(FakeLLM(
        '```json\n{"chapters":[{"number":1,"title":"Opening","objective":"Introduce the hero"}]}\n```'
    ))

    outline = agent.generate(theme="Fantasy", author_idea="Idea", lore="", constraints=[])
    assert outline.chapters[0].title == "Opening"


def test_outline_agent_rejects_invalid_provider_output() -> None:
    agent = OutlineAgent(FakeLLM("not json"))

    with pytest.raises(ValueError, match="invalid structured JSON"):
        agent.generate(theme="Fantasy", author_idea="Idea", lore="", constraints=[])
