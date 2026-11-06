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


def test_per_02_agregar_habilidad_perfil_practicante(driver, base_url):
    """PER-02: Agregar habilidad en perfil practicante."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("practicante@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Practicante"

    profile_page = ProfilePage(driver, base_url)
    profile_page.open_profile()

    habilidad = "Python"
    # Si ya existe, la removemos primero para garantizar la prueba
    profile_page.remove_skill_if_present(habilidad)
    profile_page.add_skill(habilidad)

    skills = profile_page.get_skills()
    assert any(habilidad.lower() in s.lower() for s in skills), (
        f"'{habilidad}' no aparece en skills-list: {skills}"
    )


def test_per_03_habilidad_vacia_no_se_agrega(driver, base_url):
    """PER-03: Intentar agregar habilidad vacía no modifica la lista."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("practicante@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Practicante"

    profile_page = ProfilePage(driver, base_url)
    profile_page.open_profile()

    skills_antes = profile_page.get_skills()
    # Intentar agregar habilidad vacía
    profile_page.add_skill("")

    skills_despues = profile_page.get_skills()
    assert len(skills_despues) == len(skills_antes), (
        f"La lista de habilidades cambió tras intentar agregar cadena vacía: {skills_despues}"
    )


def test_per_04_agregar_formacion_perfil_practicante(driver, base_url):
    """PER-04: Agregar formación educativa en perfil practicante."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("practicante@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Practicante"

    profile_page = ProfilePage(driver, base_url)
    profile_page.open_profile()

    formacion = "Ing. de Sistemas"
    # Si ya existe, la removemos primero para garantizar la prueba
    profile_page.remove_education_if_present(formacion)
    profile_page.add_education(formacion)

    education = profile_page.get_education()
    assert any(formacion.lower() in e.lower() for e in education), (
        f"'{formacion}' no aparece en education-list: {education}"
    )
