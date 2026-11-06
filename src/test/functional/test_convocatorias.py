"""Pruebas funcionales de convocatorias asignadas a I5."""

from uuid import uuid4

if __package__:
    from .pages.convocatoria_page import ConvocatoriaPage
    from .pages.login_page import LoginPage
else:
    from pages.convocatoria_page import ConvocatoriaPage
    from pages.login_page import LoginPage


def test_con_01_crea_convocatoria_valida_como_borrador(driver, base_url):
    """Una empresa puede crear una convocatoria válida en estado borrador."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    page = ConvocatoriaPage(driver, base_url)
    page.open_convocatorias()

    titulo = f"Practicante QA funcional {uuid4().hex[:8]}"
    page.create_draft(
        titulo=titulo,
        descripcion="Apoyo en pruebas funcionales y documentación.",
        habilidades="Python, Selenium, pytest",
        beneficios="Mentoría, horario flexible",
    )

    assert page.convocatoria_is_borrador(titulo)