# Development Setup

## Prerequisites

- Python version required by the project's packaging configuration.
- Git.
- A Gemini API key only when exercising the real provider.

## Install

Use the project's declared Python packaging/development workflow from `pyproject.toml`.

The normal test suite should not require a Gemini key.

## Run tests

Run the test suite with the project's configured pytest command. CI executes the same test suite as the merge gate.

## CLI

The CLI is the primary MVP entry point. Use `python -m book_loop.cli.main --help` to inspect the commands supported by the current implementation.

## Configuration

Runtime configuration is handled by `book_loop.infrastructure.config.Settings` and assembled by the composition root. Do not add provider or database configuration directly to CLI/use-case code.
