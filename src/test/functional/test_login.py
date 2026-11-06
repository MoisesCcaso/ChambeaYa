"""Pruebas funcionales de login/logout asignadas a I2."""

from .pages.login_page import LoginPage


def test_log_01_login_valido_practicante(driver, base_url):
    """Un practicante con credenciales demo accede a su panel."""
    page = LoginPage(driver, base_url)
    page.open_login()
    page.login("practicante@demo.local", "Demo1234")

    assert page.current_path == "/app"
    assert page.role_label == "Practicante"


def test_log_02_login_valido_empresa(driver, base_url):
    """Una empresa con credenciales demo accede a su panel y menú."""
    page = LoginPage(driver, base_url)
    page.open_login()
    page.login("empresa@demo.local", "Demo1234")

    assert page.current_path == "/app"
    assert page.role_label == "Empresa"
    assert page.company_menu_is_visible()


def test_log_03_rechaza_contrasena_incorrecta(driver, base_url):
    """Una contraseña incorrecta muestra un error y conserva el formulario."""
    page = LoginPage(driver, base_url)
    page.open_login()
    page.login("practicante@demo.local", "Incorrecta1")

    assert page.current_path == "/ingresar"
    assert page.error_message


def test_log_04_rechaza_correo_inexistente(driver, base_url):
    """Un correo sin cuenta muestra un error y conserva el formulario."""
    page = LoginPage(driver, base_url)
    page.open_login()
    page.login("nadie@demo.local", "Demo1234")

    assert page.current_path == "/ingresar"
    assert page.error_message
