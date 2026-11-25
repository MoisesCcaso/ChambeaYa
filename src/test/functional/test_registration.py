"""Functional tests for account registration (I1).

Black-box techniques: equivalence classes and boundary values on the
/registro view. Cases that create accounts use a unique email, so they
can be repeated without resetting the demo database.
"""

import uuid

import pytest

from .pages.register_page import RegisterPage

VALID_PASSWORD = "Abcd1234"
DEMO_EMAIL = "practicante@demo.local"
PASSWORD_REQUIREMENTS_ERROR = "La contraseña todavía no cumple todos los requisitos."


def unique_email() -> str:
    """Generates an email that does not exist in the database."""
    return f"reg-{uuid.uuid4().hex[:12]}@test.local"


@pytest.fixture
def page(driver, base_url) -> RegisterPage:
    """Opens the registration view before each test."""
    return RegisterPage(driver, base_url).open()


def test_reg_01_valid_intern_registration(page):
    """Valid data creates the account and leads to activation."""
    page.register(unique_email(), VALID_PASSWORD, role="practicante")

    assert page.feedback_text() == "Cuenta creada. Te llevaremos a la activación."
    assert page.feedback_kind() == "success"
    page.wait_for_path("/activar")
    assert "token=" in page.driver.current_url


def test_reg_02_7_character_password_fails_length(page):
    """Lower bound: 7 characters fail the rule and the browser blocks submitting."""
    page.fill(unique_email(), "Abcd123")

    assert page.rule_is_valid("length") is False
    assert page.field_validation_message("password") != ""

    page.submit()

    assert page.current_path() == "/registro"
    assert not page.is_feedback_visible()


def test_reg_03_8_character_password_meets_all_rules(page):
    """Exact bound: 8 characters with upper, lower case and a digit meet every rule."""
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
def test_reg_04_password_missing_a_required_character_class(page, password, missing_rule):
    """Invalid classes: missing an uppercase letter, a lowercase letter or a digit."""
    page.fill(unique_email(), password)

    status = page.rules_status()
    assert status[missing_rule] is False
    assert all(fulfilled for rule, fulfilled in status.items() if rule != missing_rule)

    page.submit()

    assert page.feedback_text() == PASSWORD_REQUIREMENTS_ERROR
    assert page.feedback_kind() == "error"
    assert page.current_path() == "/registro"


def test_reg_05_confirmation_differs_from_password(page):
    """If the confirmation does not match, the account is not created."""
    page.fill(unique_email(), VALID_PASSWORD, "Abcd1235")
    page.submit()

    assert page.feedback_text() == "Las contraseñas no coinciden."
    assert page.feedback_kind() == "error"
    assert page.current_path() == "/registro"


def test_reg_06_email_ya_registrado(page):
    """An email that already has an account is rejected by the server."""
    page.register(DEMO_EMAIL, VALID_PASSWORD)

    assert page.feedback_text() == (
        "El correo ya está registrado. Si la cuenta está pendiente, "
        "solicita un nuevo enlace de activación."
    )
    assert page.feedback_kind() == "error"
    assert page.current_path() == "/registro"


def test_reg_06_email_with_invalid_format(page):
    """An email without @ is blocked by the browser validation."""
    page.fill("sin-arroba", VALID_PASSWORD)

    assert page.field_validation_message("email") != ""

    page.submit()

    assert page.current_path() == "/registro"
    assert not page.is_feedback_visible()
