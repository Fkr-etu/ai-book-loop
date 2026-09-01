from book_loop.agents.writer import WriterAgent


class FakeLLM:
    def __init__(self) -> None:
        self.user_prompt = None

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.user_prompt = user_prompt
        return "draft"


def test_writer_passes_canonical_context_to_llm() -> None:
    llm = FakeLLM()
    context = "AUTHOR IDEA:\nA hidden heir.\n\nPREVIOUS CHAPTER SUMMARIES:\nChapter 1: The heir learns the truth."

    result = WriterAgent(llm).write(context=context)

    assert result == "draft"
    assert llm.user_prompt == context
