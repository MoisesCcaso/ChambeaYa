"""Functional tests for account activation and password recovery (I3).

Black-box technique: use cases. Each case creates its own accounts through
the API (see ``auth_data``), so they do not depend on other tests nor change
the demo accounts.
"""

from . import auth_data
from .pages.login_page import LoginPage
from .pages.recovery_page import RecoveryPage

NEW_PASSWORD = "Nueva1234"


def test_rec_01_activation_with_valid_token(driver, base_url):
    """The link with a valid token activates the account and allows logging in."""
    user = auth_data.register_pending_user(base_url)
    page = RecoveryPage(driver, base_url)
    page.open_activation(user["activation_token"])
    page.submit_activation()

    assert "Tu cuenta está activa" in page.feedback
    page.wait_for_path("/ingresar")

    login = LoginPage(driver, base_url)
    login.login(user["email"], user["password"])
    page.wait_for_path("/app")


def test_rec_02_activation_with_invalid_token(driver, base_url):
    """An invalid token is rejected with an error message."""
    page = RecoveryPage(driver, base_url)
    page.open_activation("invalido")
    page.submit_activation()

    assert page.feedback == "Token de activación inválido"
    assert page.current_path == "/activar"


def test_rec_03_login_with_inactive_account(driver, base_url):
    """A freshly registered account cannot log in."""
    user = auth_data.register_pending_user(base_url)
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login(user["email"], user["password"])

    assert login.error_message == "La cuenta no está activa"
    assert login.current_path == "/ingresar"


def test_rec_04_recovery_request_with_existing_email(driver, base_url):
    """A request with an existing email leads to the reset."""
    page = RecoveryPage(driver, base_url)
    page.open_recovery()
    page.request_recovery("practicante@demo.local")

    assert "Solicitud procesada" in page.feedback
    page.wait_for_path("/restablecer")
    assert page.current_token != ""


def test_rec_05_reset_with_valid_password(driver, base_url):
    """The new password replaces the old one and allows logging in."""
    user = auth_data.register_active_user(base_url)
    page = RecoveryPage(driver, base_url)
    page.open_recovery()
    page.request_recovery(user["email"])
    page.wait_for_path("/restablecer")
    page.reset_password(NEW_PASSWORD)

    assert "Contraseña actualizada" in page.feedback
    page.wait_for_path("/ingresar")

    login = LoginPage(driver, base_url)
    login.login(user["email"], NEW_PASSWORD)
    page.wait_for_path("/app")
    assert login.role_label == "Practicante"


def test_rec_06_reset_with_invalid_password(driver, base_url):
    """A password shorter than 8 characters is rejected."""
    user = auth_data.register_active_user(base_url)
    page = RecoveryPage(driver, base_url)
    page.open_recovery()
    page.request_recovery(user["email"])
    page.wait_for_path("/restablecer")
    page.reset_password_skipping_browser_validation("corta")

    assert page.password_field_is_too_short()
    assert page.feedback == "La contraseña debe tener al menos 8 caracteres"
    assert page.current_path == "/restablecer"

    login = LoginPage(driver, base_url)
    login.open_login()
    login.login(user["email"], user["password"])
    page.wait_for_path("/app")
