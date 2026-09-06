from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from book_loop.api.dependencies import get_current_user
from book_loop.api.routes import auth, books, canon, chapters, documents, outline
from book_loop.infrastructure.auth import COOKIE_NAME
from book_loop.infrastructure.container import Container


def _origin_is_allowed(request: Request, container: Container) -> bool:
    origin = request.headers.get("origin")
    if not origin:
        return False
    return origin in container.settings.cors_allowed_origins


def create_app(container: Container | None = None) -> FastAPI:
    if container is None:
        container = Container()

    app = FastAPI(title="AI Book Loop API", version="0.1.0")
    app.state.container = container

    app.add_middleware(
        CORSMiddleware,
        allow_origins=container.settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        """Lightweight liveness endpoint for Cloud Run and load balancers."""
        return {"status": "ok"}

    @app.middleware("http")
    async def protect_cookie_authenticated_mutations(request: Request, call_next):
        """Reject cross-origin state changes when secure browser auth uses a session cookie.

        Local HTTP clients intentionally use ``auth_cookie_secure=False`` and may not send
        browser Origin headers. Production uses a secure cookie, so browser mutations must
        carry an Origin from the configured CORS allowlist.
        """
        unsafe_method = request.method not in {"GET", "HEAD", "OPTIONS"}
        has_session_cookie = bool(request.cookies.get(COOKIE_NAME))
        csrf_protection_enabled = container.settings.auth_cookie_secure
        if (
            unsafe_method
            and has_session_cookie
            and csrf_protection_enabled
            and not _origin_is_allowed(request, container)
        ):
            return JSONResponse(
                status_code=403,
                content={"detail": "Requête d'origine non autorisée."},
            )
        return await call_next(request)

    @app.middleware("http")
    async def protect_book_routes(request: Request, call_next):
        if not request.url.path.startswith("/api/books"):
            return await call_next(request)
        if request.method == "OPTIONS":
            return await call_next(request)

        try:
            current_user = get_current_user(request)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

        request.state.user = current_user
        parts = [part for part in request.url.path.split("/") if part]
        if len(parts) >= 3:
            book_id = parts[2]
            try:
                book = container.repository.get(book_id)
            except KeyError:
                return await call_next(request)
            if book.owner_id != current_user.id:
                return JSONResponse(status_code=404, content={"detail": "Livre introuvable."})
        return await call_next(request)

    app.include_router(auth.router)
    app.include_router(books.router)
    app.include_router(outline.router)
    app.include_router(chapters.router)
    app.include_router(canon.router)
    app.include_router(documents.router)

    return app


app = create_app()
