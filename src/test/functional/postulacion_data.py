"""Datos de prueba para postulaciones y certificados (I6).

Crea por la API las convocatorias, cuentas y certificados que necesitan los
casos POS, de modo que cada prueba sea independiente de las demás y no altere
las cuentas demo. Requiere la aplicación en modo demo
(``FLASK_ENV=demo``) para obtener los tokens de activación.
"""

import json
from http.cookiejar import CookieJar
from urllib import request
from urllib.error import HTTPError

try:
    from . import auth_data
except ImportError:  # ejecución directa sin paquete
    import auth_data

EMPRESA_EMAIL = "empresa@demo.local"
EMPRESA_PASSWORD = "Demo1234"


class ApiSession:
    """Cliente HTTP con cookies de sesión para llamar a la API de ChambeaYa."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._opener = request.build_opener(
            request.HTTPCookieProcessor(CookieJar())
        )

    def call(self, method: str, path: str, payload: dict | None = None):
        """Envía la petición y devuelve ``(código_http, cuerpo_json)``."""
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"}
        if method != "GET":
            headers["X-CSRFToken"] = auth_data.csrf_token(self._opener, self.base_url)
        req = request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with self._opener.open(req, timeout=10) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            try:
                return error.code, json.loads(body)
            except ValueError:
                return error.code, {"error": body}

    def expect(self, method: str, path: str, payload: dict | None = None,
               status: int = 200) -> dict:
        """Llama a la API y exige el código HTTP esperado."""
        code, body = self.call(method, path, payload)
        assert code == status, f"{method} {path} respondió {code}: {body}"
        return body


def login(base_url: str, email: str, password: str) -> ApiSession:
    """Inicia sesión por API y devuelve la sesión autenticada."""
    session = ApiSession(base_url)
    session.expect("POST", "/auth/login", {"email": email, "password": password})
    return session


def create_opening(base_url: str, title: str, publish: bool = True,
                   close: bool = False) -> int:
    """Crea una convocatoria de la empresa demo y devuelve su identificador."""
    company = login(base_url, EMPRESA_EMAIL, EMPRESA_PASSWORD)
    opening = company.expect(
        "POST",
        "/convocatorias",
        {
            "titulo": title,
            "descripcion": "Convocatoria creada por las pruebas funcionales.",
            "habilidades_requeridas": ["Python"],
            "beneficios": ["Mentoría"],
        },
        status=201,
    )
    opening_id = opening["id"]
    if publish or close:
        company.expect("POST", f"/convocatorias/{opening_id}/publicar")
    if close:
        company.expect("POST", f"/convocatorias/{opening_id}/cerrar")
    return opening_id


def create_student_with_profile(base_url: str) -> dict:
    """Crea y activa un practicante con nombres y apellidos (requisito para postular)."""
    user = auth_data.register_active_user(base_url)
    student = login(base_url, user["email"], user["password"])
    student.expect(
        "PUT", "/perfil/me", {"nombres": "Ana", "apellidos": "Prueba"}
    )
    return user


def create_issued_certificate(base_url: str) -> str:
    """Recorre el flujo completo y devuelve el código de un certificado emitido.

    Convocatoria publicada -> postulación -> selección -> práctica ->
    entregable -> evaluación aprobada -> finalización -> emisión.
    """
    opening_id = create_opening(base_url, "Convocatoria para certificado")
    user = create_student_with_profile(base_url)
    student = login(base_url, user["email"], user["password"])
    company = login(base_url, EMPRESA_EMAIL, EMPRESA_PASSWORD)

    job_application = student.expect(
        "POST", f"/postulaciones/convocatorias/{opening_id}", status=201
    )
    job_application_id = job_application["id"]
    company.expect("POST", f"/postulaciones/{job_application_id}/seleccionar")
    internship = company.expect(
        "POST", "/practicas", {"postulacion_id": job_application_id}, status=201
    )
    internship_id = internship["id"]
    student.expect(
        "POST", f"/practicas/{internship_id}/entregables",
        {"archivo": "informe-final.pdf"}, status=201,
    )
    company.expect(
        "POST", f"/practicas/{internship_id}/evaluar", {"puntaje": 90}, status=201
    )
    company.expect("POST", f"/practicas/{internship_id}/finalizar")
    certificado = company.expect(
        "POST", f"/certificados/{internship_id}/emitir", status=201
    )
    return certificado["codigo_qr"]["valor"]
