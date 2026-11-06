"""Pruebas funcionales de activación y recuperación de contraseña (I3).

Técnica de caja negra: casos de uso. Cada caso crea sus propias cuentas por
API (ver ``auth_data``), de modo que no dependen de otros tests ni modifican
las cuentas demo.
"""

from . import auth_data
from .pages.login_page import LoginPage
from .pages.recovery_page import RecoveryPage

NEW_PASSWORD = "Nueva1234"


def test_rec_01_activacion_con_token_valido(driver, base_url):
    """El enlace con token válido activa la cuenta y permite iniciar sesión."""
    user = auth_data.register_pending_user(base_url)
    page = RecoveryPage(driver, base_url)
    page.open_activation(user["activation_token"])
    page.submit_activation()

    assert "Tu cuenta está activa" in page.feedback
    page.wait_for_path("/ingresar")

    login = LoginPage(driver, base_url)
    login.login(user["email"], user["password"])
    page.wait_for_path("/app")


def test_rec_02_activacion_con_token_invalido(driver, base_url):
    """Un token inválido es rechazado con un mensaje de error."""
    page = RecoveryPage(driver, base_url)
    page.open_activation("invalido")
    page.submit_activation()

    assert page.feedback == "Token de activación inválido"
    assert page.current_path == "/activar"


def test_rec_03_login_con_cuenta_sin_activar(driver, base_url):
    """Una cuenta recién registrada no puede iniciar sesión."""
    user = auth_data.register_pending_user(base_url)
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login(user["email"], user["password"])

    assert login.error_message == "La cuenta no está activa"
    assert login.current_path == "/ingresar"
