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
        req = request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
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


def create_opening(base_url: str, titulo: str, publicar: bool = True,
                   cerrar: bool = False) -> int:
    """Crea una convocatoria de la empresa demo y devuelve su identificador."""
    empresa = login(base_url, EMPRESA_EMAIL, EMPRESA_PASSWORD)
    opening = empresa.expect(
        "POST",
        "/convocatorias",
        {
            "titulo": titulo,
            "descripcion": "Convocatoria creada por las pruebas funcionales.",
            "habilidades_requeridas": ["Python"],
            "beneficios": ["Mentoría"],
        },
        status=201,
    )
    opening_id = opening["id"]
    if publicar or cerrar:
        empresa.expect("POST", f"/convocatorias/{opening_id}/publicar")
    if cerrar:
        empresa.expect("POST", f"/convocatorias/{opening_id}/cerrar")
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
    empresa = login(base_url, EMPRESA_EMAIL, EMPRESA_PASSWORD)

    postulacion = student.expect(
        "POST", f"/postulaciones/convocatorias/{opening_id}", status=201
    )
    postulacion_id = postulacion["id"]
    empresa.expect("POST", f"/postulaciones/{postulacion_id}/seleccionar")
    practica = empresa.expect(
        "POST", "/practicas", {"postulacion_id": postulacion_id}, status=201
    )
    practica_id = practica["id"]
    student.expect(
        "POST", f"/practicas/{practica_id}/entregables",
        {"archivo": "informe-final.pdf"}, status=201,
    )
    empresa.expect(
        "POST", f"/practicas/{practica_id}/evaluar", {"puntaje": 90}, status=201
    )
    empresa.expect("POST", f"/practicas/{practica_id}/finalizar")
    certificado = empresa.expect(
        "POST", f"/certificados/{practica_id}/emitir", status=201
    )
    return certificado["codigo_qr"]["valor"]
