from book_loop.cli.main import build_parser


def test_create_parser_accepts_author_inputs() -> None:
    args = build_parser().parse_args([
        "create", "--title", "My Book", "--theme", "Fantasy", "--idea", "A hidden city",
        "--lore", "Ancient magic", "--constraint", "First person",
    ])
    assert args.command == "create"
    assert args.title == "My Book"
    assert args.constraint == ["First person"]


def test_outline_commands_accept_book_id() -> None:
    assert build_parser().parse_args(["outline", "b1"]).book_id == "b1"
    assert build_parser().parse_args(["approve-outline", "b1"]).command == "approve-outline"


def test_chapter_add_accepts_title_and_objective() -> None:
    args = build_parser().parse_args([
        "chapter-add", "b1", "--title", "Beginning", "--objective", "Start conflict"
    ])
    assert args.command == "chapter-add"
    assert args.book_id == "b1"
    assert args.objective == "Start conflict"


def test_cli_main_execution(monkeypatch, capsys):
    import sys
    from book_loop.cli.main import main

    monkeypatch.setattr(sys, "argv", [
        "book-loop", "create", "--title", "CLI Book", "--theme", "Theme", "--idea", "Idea"
    ])
    main()
    captured = capsys.readouterr()
    assert "Book created:" in captured.out
