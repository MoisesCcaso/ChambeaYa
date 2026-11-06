"""Datos de prueba para los flujos de activación y recuperación (I3).

Crea cuentas únicas por la API de autenticación para que cada prueba sea
independiente de las demás y no altere las cuentas demo. Requiere que la
aplicación exponga los tokens (``EXPOSE_AUTH_TOKENS=true``, activo en la
configuración ``demo``, ``development`` sin SMTP y ``testing``).
"""

import json
import uuid
from urllib import request
from urllib.error import HTTPError

VALID_PASSWORD = "Abcd1234"


def unique_email() -> str:
    """Genera un correo que no existe en la base de datos."""
    return f"func-{uuid.uuid4().hex[:12]}@test.local"


def _post(base_url: str, path: str, payload: dict) -> dict:
    """Envía un POST JSON a la API y devuelve el cuerpo decodificado."""
    req = request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=10) as response:
            return json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise AssertionError(
            f"{path} respondió {error.code}: {detail}"
        ) from error


def register_pending_user(
    base_url: str, password: str = VALID_PASSWORD
) -> dict:
    """Registra un practicante sin activar y devuelve email, password y token."""
    email = unique_email()
    data = _post(
        base_url,
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
    base_url: str, password: str = VALID_PASSWORD
) -> dict:
    """Registra y activa un practicante; devuelve email y password."""
    user = register_pending_user(base_url, password)
    _post(base_url, "/auth/activate", {"token": user["activation_token"]})
    return user
