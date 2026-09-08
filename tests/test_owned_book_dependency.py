from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from book_loop.api import dependencies
from book_loop.domain.models import UserPublic


def test_get_owned_book_returns_book_for_current_owner(monkeypatch):
    book = SimpleNamespace(id="book-1", owner_id="user-1")
    user = UserPublic(id="user-1", email="owner@example.com")
    request = SimpleNamespace()
    container = SimpleNamespace()

    monkeypatch.setattr(dependencies, "get_current_user", lambda _request: user)
    monkeypatch.setattr(dependencies, "get_book", lambda _book_id, _container: book)

    assert dependencies.get_owned_book("book-1", request, container) is book


def test_get_owned_book_hides_book_owned_by_another_user(monkeypatch):
    book = SimpleNamespace(id="book-1", owner_id="user-1")
    user = UserPublic(id="user-2", email="other@example.com")
    request = SimpleNamespace()
    container = SimpleNamespace()

    monkeypatch.setattr(dependencies, "get_current_user", lambda _request: user)
    monkeypatch.setattr(dependencies, "get_book", lambda _book_id, _container: book)

    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_owned_book("book-1", request, container)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Livre introuvable."
