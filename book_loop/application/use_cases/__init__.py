"""Application use cases orchestrating domain ports."""
from __future__ import annotations

from book_loop.application.use_cases.add_chapter import AddChapter
from book_loop.application.use_cases.approve_chapter import ApproveChapter
from book_loop.application.use_cases.approve_outline import ApproveOutline
from book_loop.application.use_cases.create_book import CreateBook
from book_loop.application.use_cases.create_character import CreateCharacter
from book_loop.application.use_cases.create_character_relation import CreateCharacterRelation
from book_loop.application.use_cases.delete_character import DeleteCharacter
from book_loop.application.use_cases.delete_character_relation import DeleteCharacterRelation
from book_loop.application.use_cases.generate_chapter import GenerateChapter
from book_loop.application.use_cases.generate_outline import GenerateOutline
from book_loop.application.use_cases.reject_chapter import RejectChapter
from book_loop.application.use_cases.review_chapter import ReviewChapter
from book_loop.application.use_cases.set_creative_brief import SetCreativeBrief
from book_loop.application.use_cases.update_book import UpdateBook
from book_loop.application.use_cases.update_character import UpdateCharacter
from book_loop.application.use_cases.update_outline import UpdateOutline

__all__ = [
    "AddChapter",
    "ApproveChapter",
    "ApproveOutline",
    "CreateBook",
    "CreateCharacter",
    "CreateCharacterRelation",
    "DeleteCharacter",
    "DeleteCharacterRelation",
    "GenerateChapter",
    "GenerateOutline",
    "RejectChapter",
    "ReviewChapter",
    "SetCreativeBrief",
    "UpdateBook",
    "UpdateCharacter",
    "UpdateOutline",
]
