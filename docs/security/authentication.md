# Authentication and authorization

- JWT signing uses `auth_secret_key` from environment/settings. Do not commit production secrets.
- Browser sessions use an HttpOnly cookie. `auth_cookie_secure` must be enabled behind HTTPS in production.
- CORS origins are explicit and credentialed requests are supported only from configured origins.
- Every `/api/books/...` request requires an authenticated user.
- A book is owned by the `owner_id` stored in `BookState`; users receive `404` for books they do not own to avoid resource enumeration.
- Bearer tokens remain accepted for API clients, while browser clients should use the HttpOnly session cookie.

For production, configure at least:

```env
AUTH_SECRET_KEY=<long-random-secret>
AUTH_COOKIE_SECURE=true
CORS_ALLOWED_ORIGINS=["https://app.example.com"]
```
