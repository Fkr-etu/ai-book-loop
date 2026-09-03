from __future__ import annotations

import argparse
import json
from pathlib import Path

from book_loop.domain.models import CreativeBrief, Outline
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
    create.add_argument("--owner-id", default="cli-user", help="Owner id for the local CLI book")

    brief = subparsers.add_parser("brief", help="Set the structured creative brief")
    brief.add_argument("book_id")
    brief.add_argument("--premise", required=True)
    brief.add_argument("--audience", default="")
    brief.add_argument("--tone", default="")
    brief.add_argument("--theme", dest="brief_themes", action="append", default=[])
    brief.add_argument("--must-include", action="append", default=[])
    brief.add_argument("--must-avoid", action="append", default=[])

    outline = subparsers.add_parser("outline", help="Generate an outline")
    outline.add_argument("book_id")

    edit_outline = subparsers.add_parser("outline-edit", help="Replace the editable outline")
    edit_outline.add_argument("book_id")
    source = edit_outline.add_mutually_exclusive_group(required=True)
    source.add_argument("--json", dest="outline_json", help="Structured outline as JSON")
    source.add_argument("--file", type=Path, help="Read structured outline JSON from a UTF-8 file")

    approve = subparsers.add_parser("approve-outline", help="Approve the outline")
    approve.add_argument("book_id")

    chapter = subparsers.add_parser("chapter-add", help="Add a chapter from the approved outline")
    chapter.add_argument("book_id")
    chapter.add_argument("chapter_number", type=int)

    real_run = subparsers.add_parser("real-run", help="Run a two-chapter live LLM smoke test")
    real_run.add_argument("--title", default="Les Veilleurs de Marseille")
    real_run.add_argument("--theme", default="thriller futuriste")
    real_run.add_argument(
        "--idea",
        default="Une archiviste découvre que certains souvenirs de Marseille ont été volontairement effacés.",
    )
    real_run.add_argument("--premise", default="Une archiviste enquête sur des souvenirs effacés de Marseille.")
    real_run.add_argument("--audience", default="adultes")
    real_run.add_argument("--tone", default="mystérieux et tendu")
    real_run.add_argument("--brief-theme", action="append", default=["mémoire", "identité", "transmission"])
    real_run.add_argument("--must-include", action="append", default=["Marseille", "une archiviste", "un secret familial"])
    real_run.add_argument("--must-avoid", action="append", default=["science-fiction trop technique"])
    real_run.add_argument("--owner-id", default="real-run")

    return parser


def _require_live_llm(settings: Settings) -> None:
    if settings.llm_provider == "fake" or not settings.gemini_api_key:
        raise RuntimeError(
            "Live run requires LLM_PROVIDER=gemini and GEMINI_API_KEY; refusing to run with the fake provider."
        )


def _run_real_test(args: argparse.Namespace, container: Container) -> None:
    _require_live_llm(container.settings)
    book = container.create_book().execute(
        owner_id=args.owner_id,
        title=args.title,
        theme=args.theme,
        author_idea=args.idea,
    )
    print(f"[1/7] Book created: {book.id}")

    brief = CreativeBrief(
        premise=args.premise,
        audience=args.audience,
        tone=args.tone,
        themes=args.brief_theme,
        must_include=args.must_include,
        must_avoid=args.must_avoid,
    )
    book = container.set_creative_brief().execute(book, brief)
    print("[2/7] Creative brief persisted")

    book = container.generate_outline().execute(book)
    print(f"[3/7] Outline generated: {len(book.outline.chapters)} chapters")
    container.approve_outline().execute(book)
    print("[4/7] Outline approved")

    chapter_count = min(2, len(book.outline.chapters))
    if chapter_count < 2:
        raise RuntimeError("The live outline must contain at least two chapters for the smoke test")

    for chapter_number in range(1, chapter_count + 1):
        book = container.repository.get(book.id)
        book = container.add_chapter().execute(book, chapter_number=chapter_number)
        result = container.generate_chapter().execute(book, chapter_number)
        print(
            f"[5/7] Chapter {chapter_number}: approved after {result.attempt} version(s), "
            f"review score={result.review_score}"
        )

    reloaded = container.repository.get(book.id)
    if len(reloaded.chapters) != 2 or any(chapter.status.value != "approved" for chapter in reloaded.chapters):
        raise RuntimeError("E2E persistence check failed")
    if not all(chapter.summary for chapter in reloaded.chapters):
        raise RuntimeError("E2E summary check failed")
    print("[6/7] SQLite state reloaded with two approved chapters and summaries")
    print("[7/7] REAL E2E TEST: PASS")


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings()
    container = Container(settings)

    if args.command == "real-run":
        _run_real_test(args, container)
        return

    if args.command == "create":
        book = container.create_book().execute(
            owner_id=args.owner_id,
            title=args.title,
            theme=args.theme,
            author_idea=args.idea,
            lore=args.lore,
            constraints=args.constraint,
        )
        print(f"Book created: {book.id}")
        return

    book = container.repository.get(args.book_id)
    if args.command == "brief":
        brief = CreativeBrief(
            premise=args.premise,
            audience=args.audience,
            tone=args.tone,
            themes=args.brief_themes,
            must_include=args.must_include,
            must_avoid=args.must_avoid,
        )
        container.set_creative_brief().execute(book, brief)
        print("Creative brief saved")
    elif args.command == "outline":
        book = container.generate_outline().execute(book)
        print(json.dumps(book.outline.model_dump(mode="json"), indent=2, ensure_ascii=False))
    elif args.command == "outline-edit":
        raw = args.outline_json if args.outline_json is not None else args.file.read_text(encoding="utf-8")
        outline = Outline.model_validate(json.loads(raw))
        container.update_outline().execute(book, outline=outline)
        print("Outline updated; approval reset")
    elif args.command == "approve-outline":
        container.approve_outline().execute(book)
        print("Outline approved")
    elif args.command == "chapter-add":
        book = container.add_chapter().execute(book, chapter_number=args.chapter_number)
        print(f"Chapter added: {book.chapters[-1].number}")


if __name__ == "__main__":
    main()
