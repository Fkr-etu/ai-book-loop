from __future__ import annotations

from starlette.requests import Request

from book_loop.api.routes.auth import _client_ip


def _request(headers: list[tuple[bytes, bytes]], client: tuple[str, int] = ("127.0.0.1", 1234)) -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/auth/login",
            "headers": headers,
            "client": client,
        }
    )


def test_client_ip_uses_rightmost_forwarded_address() -> None:
    request = _request(
        [(b"x-forwarded-for", b"203.0.113.10, 198.51.100.20")]
    )

    assert _client_ip(request) == "198.51.100.20"


def test_client_ip_falls_back_to_asgi_client() -> None:
    request = _request([])

    assert _client_ip(request) == "127.0.0.1"
