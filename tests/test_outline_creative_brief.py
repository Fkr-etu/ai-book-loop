from book_loop.agents.outline import OutlineAgent
from book_loop.domain.models import CreativeBrief


class RecordingLLM:
    def __init__(self) -> None:
        self.user_prompt = ""

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.user_prompt = user_prompt
        return '{"chapters":[{"number":1,"title":"Opening","objective":"Introduce the hero"}]}'


def test_outline_agent_includes_creative_brief() -> None:
    llm = RecordingLLM()
    brief = CreativeBrief(
        premise="A cartographer discovers a hidden city.",
        audience="Adult readers",
        tone="Wonder and tension",
        themes=["identity", "discovery"],
        must_include=["a living map"],
        must_avoid=["gratuitous violence"],
    )

    OutlineAgent(llm).generate(
        theme="Fantasy",
        author_idea="Idea",
        lore="",
        constraints=[],
        creative_brief=brief,
    )

    assert "CREATIVE BRIEF:" in llm.user_prompt
    assert "Premise: A cartographer discovers a hidden city." in llm.user_prompt
    assert "Audience: Adult readers" in llm.user_prompt
    assert "Themes: identity, discovery" in llm.user_prompt
    assert "Must include: a living map" in llm.user_prompt
    assert "Must avoid: gratuitous violence" in llm.user_prompt
