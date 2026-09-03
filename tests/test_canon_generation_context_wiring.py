from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container


def test_container_wires_knowledge_repository_into_generation_context(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'book.db'}",
        llm_provider="fake",
    )
    container = Container(settings)

    assert container.context_builder.knowledge_repository is container.repository
    assert container.chapter_workflow.context_builder is container.context_builder
