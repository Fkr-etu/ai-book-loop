from __future__ import annotations

import argparse

from book_loop.application.services.book import BookService
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.database.repository import SQLiteBookRepository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="book-loop")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a book")
    create.add_argument("--title", required=True)
    create.add_argument("--theme", required=True)
    create.add_argument("--idea", required=True)
    create.add_argument("--lore", default="")
    create.add_argument("--constraint", action="append", default=[])
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings()
    repository = SQLiteBookRepository(settings.database_url)

    if args.command == "create":
        book = BookService(repository).create(
            title=args.title,
            theme=args.theme,
            author_idea=args.idea,
            lore=args.lore,
            constraints=args.constraint,
        )
        print(f"Book created: {book.id}")


if __name__ == "__main__":
    main()
