"""Test data for the activation and recovery flows (I3).

Creates unique accounts through the authentication API so every test is
independent of the others and does not alter the demo accounts. Requires the
app to expose the tokens (``EXPOSE_AUTH_TOKENS=true``, on in the ``demo``
configuration, in ``development`` without SMTP and in ``testing``).
"""

import json
import uuid
from http.cookiejar import CookieJar
from urllib import request
from urllib.error import HTTPError

VALID_PASSWORD = "Abcd1234"


def unique_email() -> str:
    """Generates an email that does not exist in the database."""
    return f"func-{uuid.uuid4().hex[:12]}@test.local"


def csrf_token(opener, api_url: str) -> str:
    """Asks the API for a CSRF token bound to the ``opener`` session."""
    with opener.open(f"{api_url.rstrip('/')}/auth/csrf-token", timeout=10) as response:
        token = json.load(response).get("csrf_token")
    assert token, "La API no devolvió el token CSRF"
    return token


def _post(api_url: str, path: str, payload: dict) -> dict:
    """Sends a JSON POST to the API and returns the decoded body."""
    opener = request.build_opener(request.HTTPCookieProcessor(CookieJar()))
    req = request.Request(
        f"{api_url.rstrip('/')}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token(opener, api_url),
        },
        method="POST",
    )
    try:
        with opener.open(req, timeout=10) as response:
            return json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise AssertionError(
            f"{path} respondió {error.code}: {detail}"
        ) from error


def register_pending_user(
    api_url: str, password: str = VALID_PASSWORD
) -> dict:
    """Registers an inactive intern and returns email, password and token."""
    email = unique_email()
    data = _post(
        api_url,
        "/auth/register",
        {
            "email": email,
            "password": password,
            "password_confirmation": password,
            "tipo": "practicante",
        },
    )
    token = data.get("activation_token")
    assert token, (
        "La aplicación no expone el token de activación; "
        "ejecútela con EXPOSE_AUTH_TOKENS=true (por ejemplo, FLASK_ENV=demo)."
    )
    return {"email": email, "password": password, "activation_token": token}


def register_active_user(
    api_url: str, password: str = VALID_PASSWORD
) -> dict:
    """Registers and activates an intern; returns email and password."""
    user = register_pending_user(api_url, password)
    _post(api_url, "/auth/activate", {"token": user["activation_token"]})
    return user
