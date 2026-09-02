from __future__ import annotations

import argparse
from pathlib import Path

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

    edit_outline = subparsers.add_parser("outline-edit", help="Replace the editable outline")
    edit_outline.add_argument("book_id")
    source = edit_outline.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="New outline text")
    source.add_argument("--file", type=Path, help="Read the new outline from a UTF-8 file")

    approve = subparsers.add_parser("approve-outline", help="Approve the outline")
    approve.add_argument("book_id")

    chapter = subparsers.add_parser("chapter-add", help="Add a chapter")
    chapter.add_argument("book_id")
    chapter.add_argument("--title", required=True)
    chapter.add_argument("--objective", required=True)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    container = Container(Settings())

    if args.command == "create":
        book = container.create_book().execute(
            title=args.title,
            theme=args.theme,
            author_idea=args.idea,
            lore=args.lore,
            constraints=args.constraint,
        )
        print(f"Book created: {book.id}")
        return

    book = container.repository.get(args.book_id)
    if args.command == "outline":
        book = container.generate_outline().execute(book)
        print(book.outline)
    elif args.command == "outline-edit":
        outline = args.text if args.text is not None else args.file.read_text(encoding="utf-8")
        book = container.update_outline().execute(book, outline=outline)
        print("Outline updated; approval reset")
    elif args.command == "approve-outline":
        container.approve_outline().execute(book)
        print("Outline approved")
    elif args.command == "chapter-add":
        book = container.add_chapter().execute(book, title=args.title, objective=args.objective)
        print(f"Chapter added: {book.chapters[-1].number}")


if __name__ == "__main__":
    main()
