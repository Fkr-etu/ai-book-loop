from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ResendEmailSender:
    """Infrastructure adapter for Resend's transactional email API."""

    def __init__(self, *, api_key: str, from_address: str) -> None:
        if not api_key:
            raise ValueError("RESEND_API_KEY must be configured")
        self.api_key = api_key
        self.from_address = from_address

    def send_verification_email(self, *, recipient: str, verification_url: str) -> None:
        payload = json.dumps(
            {
                "from": self.from_address,
                "to": [recipient],
                "subject": "Vérifiez votre adresse e-mail — Book Loop",
                "html": (
                    "<p>Bienvenue sur Book Loop.</p>"
                    "<p>Confirmez votre adresse e-mail pour activer votre compte :</p>"
                    f'<p><a href="{verification_url}">Vérifier mon adresse e-mail</a></p>'
                    "<p>Ce lien expire dans 24 heures.</p>"
                ),
            }
        ).encode("utf-8")
        request = Request(
            "https://api.resend.com/emails",
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=10) as response:
                if response.status >= 300:
                    raise RuntimeError(f"Resend returned HTTP {response.status}")
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError("Unable to send verification email") from exc
