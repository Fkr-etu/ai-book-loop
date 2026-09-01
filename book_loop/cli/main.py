from __future__ import annotations

import argparse

from book_loop.application.use_cases.add_chapter import AddChapter
from book_loop.application.use_cases.approve_outline import ApproveOutline
from book_loop.application.use_cases.create_book import CreateBook
from book_loop.application.use_cases.generate_chapter import GenerateChapter
from book_loop.application.use_cases.generate_outline import GenerateOutline
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="book-loop")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a book")
    create.add_argument("--title", required=True)
    create.add_argument("--theme", required=True)
    create.add_argument("--idea", required=True)
    create.add_argument("--lore", default="")
    create.add_argument("--constraint", action="append", default=[])

    outline = subparsers.add_parser("outline", help="Generate an outline")
    outline.add_argument("book_id")
    approve = subparsers.add_parser("approve-outline", help="Approve the outline")
    approve.add_argument("book_id")

    chapter = subparsers.add_parser("chapter-add", help="Add a chapter")
    chapter.add_argument("book_id")
    chapter.add_argument("--title", required=True)
    chapter.add_argument("--objective", required=True)

    generate = subparsers.add_parser("chapter-generate", help="Generate a chapter")
    generate.add_argument("book_id")
    generate.add_argument("chapter_number", type=int)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    container = Container(Settings())

    if args.command == "create":
        book = container.create_book().execute(
            title=args.title, theme=args.theme, author_idea=args.idea,
            lore=args.lore, constraints=args.constraint,
        )
        print(f"Book created: {book.id}")
        return

    book = container.repository.get(args.book_id)
    if args.command == "outline":
        book = container.generate_outline().execute(book)
        print(book.outline)
    elif args.command == "approve-outline":
        container.approve_outline().execute(book)
        print("Outline approved")
    elif args.command == "chapter-add":
        book = container.add_chapter().execute(book, title=args.title, objective=args.objective)
        print(f"Chapter added: {book.chapters[-1].number}")
    elif args.command == "chapter-generate":
        result = container.generate_chapter().execute(book, chapter_number=args.chapter_number)
        print(result.draft)
        if result.summary:
            print(f"\nCanonical summary:\n{result.summary}")
        if result.decision:
            print(f"\nDecision: {result.decision}")


if __name__ == "__main__":
    main()
