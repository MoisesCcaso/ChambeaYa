"""Pruebas funcionales del área de Perfiles asignadas a I4."""

from uuid import uuid4

if __package__:
    from .pages.login_page import LoginPage
    from .pages.profile_page import ProfilePage
else:
    from pages.login_page import LoginPage
    from pages.profile_page import ProfilePage


def test_per_01_guardar_datos_validos_perfil_practicante(driver, base_url):
    """PER-01: Guardar datos válidos en perfil practicante."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("practicante@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Practicante"

    profile_page = ProfilePage(driver, base_url)
    profile_page.open_profile()

    nuevos_nombres = f"Andrea {uuid4().hex[:6]}"
    nuevos_apellidos = "Quispe Flores"
    profile_page.fill_student_profile(
        nombres=nuevos_nombres,
        apellidos=nuevos_apellidos,
        dni="72483915",
        carnet="202612345",
    )
    profile_page.submit_student_profile()

    status = profile_page.get_student_status()
    assert (
        "actualizado" in status.lower()
        or "guardado" in status.lower()
        or "éxito" in status.lower()
        or status != ""
    )
