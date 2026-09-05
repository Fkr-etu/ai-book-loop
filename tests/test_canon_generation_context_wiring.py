import os

from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")


def test_container_wires_knowledge_repository_into_generation_context():
    settings = Settings(database_url=DATABASE_URL, llm_provider="fake")
    container = Container(settings)

    assert container.context_builder.knowledge_repository is container.repository
    assert container.chapter_workflow.context_builder is container.context_builder
