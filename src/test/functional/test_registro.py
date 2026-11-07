"""Pruebas funcionales del registro de cuentas (I1).

Técnicas de caja negra: clases de equivalencia y valores límite sobre la
vista /registro. Los casos que crean cuentas usan un correo único, así que
se pueden repetir sin reiniciar la base demo.
"""

import uuid

import pytest

from .pages.register_page import RegisterPage

VALID_PASSWORD = "Abcd1234"
DEMO_EMAIL = "practicante@demo.local"
PASSWORD_REQUIREMENTS_ERROR = "La contraseña todavía no cumple todos los requisitos."


def unique_email() -> str:
    """Genera un correo que no existe en la base de datos."""
    return f"reg-{uuid.uuid4().hex[:12]}@test.local"


@pytest.fixture
def page(driver, base_url) -> RegisterPage:
    """Abre la vista de registro antes de cada prueba."""
    return RegisterPage(driver, base_url).open()


def test_reg_01_registro_valido_de_practicante(page):
    """Datos válidos crean la cuenta y llevan a la activación."""
    page.register(unique_email(), VALID_PASSWORD, tipo="practicante")

    assert page.feedback_text() == "Cuenta creada. Te llevaremos a la activación."
    assert page.feedback_kind() == "success"
    page.wait_for_path("/activar")
    assert "token=" in page.driver.current_url


def test_reg_02_contrasena_de_7_caracteres_no_cumple_longitud(page):
    """Límite inferior: 7 caracteres no cumplen la regla y el navegador bloquea el envío."""
    page.fill(unique_email(), "Abcd123")

    assert page.rule_is_valid("length") is False
    assert page.field_validation_message("password") != ""

    page.submit()

    assert page.current_path() == "/registro"
    assert not page.is_feedback_visible()


def test_reg_03_contrasena_de_8_caracteres_cumple_todas_las_reglas(page):
    """Límite exacto: 8 caracteres con mayúscula, minúscula y número cumplen todo."""
    page.fill(unique_email(), "Abcd1234")

    assert page.rules_status() == {rule: True for rule in RegisterPage.PASSWORD_RULES}
    assert page.field_validation_message("password") == ""


@pytest.mark.parametrize(
    ("password", "missing_rule"),
    [
        ("abcd1234", "uppercase"),
        ("ABCD1234", "lowercase"),
        ("Abcdefgh", "number"),
    ],
    ids=["sin-mayuscula", "sin-minuscula", "sin-numero"],
)
def test_reg_04_contrasena_sin_clase_de_caracter_requerida(page, password, missing_rule):
    """Clases inválidas: falta una mayúscula, una minúscula o un número."""
    page.fill(unique_email(), password)

    status = page.rules_status()
    assert status[missing_rule] is False
    assert all(fulfilled for rule, fulfilled in status.items() if rule != missing_rule)

    page.submit()

    assert page.feedback_text() == PASSWORD_REQUIREMENTS_ERROR
    assert page.feedback_kind() == "error"
    assert page.current_path() == "/registro"


def test_reg_05_confirmacion_distinta_de_la_contrasena(page):
    """Si la confirmación no coincide, no se crea la cuenta."""
    page.fill(unique_email(), VALID_PASSWORD, "Abcd1235")
    page.submit()

    assert page.feedback_text() == "Las contraseñas no coinciden."
    assert page.feedback_kind() == "error"
    assert page.current_path() == "/registro"


def test_reg_06_email_ya_registrado(page):
    """Un correo que ya tiene cuenta es rechazado por el servidor."""
    page.register(DEMO_EMAIL, VALID_PASSWORD)

    assert page.feedback_text() == (
        "El correo ya está registrado. Si la cuenta está pendiente, "
        "solicita un nuevo enlace de activación."
    )
    assert page.feedback_kind() == "error"
    assert page.current_path() == "/registro"


def test_reg_06_email_con_formato_invalido(page):
    """Un correo sin @ es bloqueado por la validación del navegador."""
    page.fill("sin-arroba", VALID_PASSWORD)

    assert page.field_validation_message("email") != ""

    page.submit()

    assert page.current_path() == "/registro"
    assert not page.is_feedback_visible()
