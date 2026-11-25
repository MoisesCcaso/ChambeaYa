"""Login/logout functional tests assigned to I2."""

if __package__:
    from .pages.login_page import LoginPage
else:
    from pages.login_page import LoginPage


def test_log_01_valid_intern_login(driver, base_url):
    """An intern with demo credentials reaches their dashboard."""
    page = LoginPage(driver, base_url)
    page.open_login()
    page.login("practicante@demo.local", "Demo1234")
    page.wait_for_path("/app")

    assert page.current_path == "/app"
    assert page.role_label == "Practicante"


def test_log_02_valid_company_login(driver, base_url):
    """A company with demo credentials reaches its dashboard and menu."""
    page = LoginPage(driver, base_url)
    page.open_login()
    page.login("empresa@demo.local", "Demo1234")
    page.wait_for_path("/app")

    assert page.current_path == "/app"
    assert page.role_label == "Empresa"
    assert page.company_menu_is_visible()


def test_log_03_rejects_wrong_password(driver, base_url):
    """A wrong password shows an error and keeps the form."""
    page = LoginPage(driver, base_url)
    page.open_login()
    page.login("practicante@demo.local", "Incorrecta1")

    assert page.current_path == "/ingresar"
    assert page.error_message


def test_log_04_rejects_unknown_email(driver, base_url):
    """An email without an account shows an error and keeps the form."""
    page = LoginPage(driver, base_url)
    page.open_login()
    page.login("nadie@demo.local", "Demo1234")

    assert page.current_path == "/ingresar"
    assert page.error_message


def test_log_05_redirects_app_without_session(driver, base_url):
    """Visiting /app without a session redirects to the login form."""
    page = LoginPage(driver, base_url)
    page.open("/app")

    assert page.current_path == "/ingresar"


def test_log_06_logout_invalida_acceso_a_app(driver, base_url):
    """After logging out, a new visit to /app goes back to /ingresar."""
    page = LoginPage(driver, base_url)
    page.open_login()
    page.login("practicante@demo.local", "Demo1234")
    page.wait_for_path("/app")
    assert page.role_label == "Practicante"

    page.logout()
    assert page.current_path == "/ingresar"

    page.open("/app")
    assert page.current_path == "/ingresar"
