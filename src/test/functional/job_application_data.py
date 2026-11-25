"""Test data for job applications and certificates (I6).

Creates through the API the job postings, accounts and certificates the POS
cases need, so every test is independent of the others and does not alter
the demo accounts. Requires the app in demo mode
(``FLASK_ENV=demo``) to get the activation tokens.
"""

import json
from http.cookiejar import CookieJar
from urllib import request
from urllib.error import HTTPError

try:
    from . import auth_data
except ImportError:  # direct run without a package
    import auth_data

COMPANY_EMAIL = "empresa@demo.local"
COMPANY_PASSWORD = "Demo1234"


class ApiSession:
    """HTTP client with session cookies to call the ChambeaYa API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._opener = request.build_opener(
            request.HTTPCookieProcessor(CookieJar())
        )

    def call(self, method: str, path: str, payload: dict | None = None):
        """Sends the request and returns ``(http_status, json_body)``."""
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
        """Calls the API and requires the expected HTTP status."""
        code, body = self.call(method, path, payload)
        assert code == status, f"{method} {path} respondió {code}: {body}"
        return body


def login(base_url: str, email: str, password: str) -> ApiSession:
    """Logs in through the API and returns the authenticated session."""
    session = ApiSession(base_url)
    session.expect("POST", "/auth/login", {"email": email, "password": password})
    return session


def create_opening(base_url: str, title: str, publish: bool = True,
                   close: bool = False) -> int:
    """Creates a job posting for the demo company and returns its id."""
    company = login(base_url, COMPANY_EMAIL, COMPANY_PASSWORD)
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
    """Creates and activates an intern with first and last names (required to apply)."""
    user = auth_data.register_active_user(base_url)
    student = login(base_url, user["email"], user["password"])
    student.expect(
        "PUT", "/perfil/me", {"nombres": "Ana", "apellidos": "Prueba"}
    )
    return user


def create_issued_certificate(base_url: str) -> str:
    """Walks the full flow and returns the code of an issued certificate.

    Published job posting -> application -> selection -> internship ->
    deliverable -> passed evaluation -> finish -> issuance.
    """
    opening_id = create_opening(base_url, "Convocatoria para certificado")
    user = create_student_with_profile(base_url)
    student = login(base_url, user["email"], user["password"])
    company = login(base_url, COMPANY_EMAIL, COMPANY_PASSWORD)

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
    certificate = company.expect(
        "POST", f"/certificados/{internship_id}/emitir", status=201
    )
    return certificate["codigo_qr"]["valor"]
