from book_loop.cli.main import build_parser


def test_create_parser_accepts_author_inputs() -> None:
    args = build_parser().parse_args([
        "create",
        "--title", "My Book",
        "--theme", "Fantasy",
        "--idea", "A hidden city",
        "--lore", "Ancient magic",
        "--constraint", "First person",
    ])
    assert args.command == "create"
    assert args.title == "My Book"
    assert args.constraint == ["First person"]
