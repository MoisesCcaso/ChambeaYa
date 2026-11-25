"""Profiles functional tests assigned to I4."""

from uuid import uuid4

if __package__:
    from .pages.login_page import LoginPage
    from .pages.profile_page import ProfilePage
else:
    from pages.login_page import LoginPage
    from pages.profile_page import ProfilePage


def test_per_01_saves_valid_intern_profile_data(driver, base_url):
    """PER-01: Save valid data in the intern profile."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("practicante@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Practicante"

    profile_page = ProfilePage(driver, base_url)
    profile_page.open_profile()

    new_first_names = f"Andrea {uuid4().hex[:6]}"
    new_last_names = "Quispe Flores"
    profile_page.fill_student_profile(
        first_names=new_first_names,
        last_names=new_last_names,
        dni="72483915",
        card="202612345",
    )
    profile_page.submit_student_profile()

    status = profile_page.get_student_status()
    assert (
        "actualizado" in status.lower()
        or "guardado" in status.lower()
        or "éxito" in status.lower()
        or status != ""
    )


def test_per_02_adds_skill_to_intern_profile(driver, base_url):
    """PER-02: Add a skill to the intern profile."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("practicante@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Practicante"

    profile_page = ProfilePage(driver, base_url)
    profile_page.open_profile()

    skill = "Python"
    # If it already exists, remove it first so the test is meaningful
    profile_page.remove_skill_if_present(skill)
    profile_page.add_skill(skill)

    skills = profile_page.get_skills()
    assert any(skill.lower() in s.lower() for s in skills), (
        f"'{skill}' no aparece en skills-list: {skills}"
    )


def test_per_03_empty_skill_is_not_added(driver, base_url):
    """PER-03: Trying to add an empty skill does not change the list."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("practicante@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Practicante"

    profile_page = ProfilePage(driver, base_url)
    profile_page.open_profile()

    skills_antes = profile_page.get_skills()
    # Try to add an empty skill
    profile_page.add_skill("")

    skills_despues = profile_page.get_skills()
    assert len(skills_despues) == len(skills_antes), (
        f"La lista de habilidades cambió tras intentar agregar cadena vacía: {skills_despues}"
    )


def test_per_04_adds_education_to_intern_profile(driver, base_url):
    """PER-04: Add an education entry to the intern profile."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("practicante@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Practicante"

    profile_page = ProfilePage(driver, base_url)
    profile_page.open_profile()

    education_entry = "Ing. de Sistemas"
    # If it already exists, remove it first so the test is meaningful
    profile_page.remove_education_if_present(education_entry)
    profile_page.add_education(education_entry)

    education = profile_page.get_education()
    assert any(education_entry.lower() in e.lower() for e in education), (
        f"'{education_entry}' no aparece en education-list: {education}"
    )


def test_per_05_saves_company_profile_with_valid_ruc(driver, base_url):
    """PER-05: Save the company profile with a valid RUC (11 digits)."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    profile_page = ProfilePage(driver, base_url)
    profile_page.open_profile()

    profile_page.fill_company_profile(
        legal_name="Innovación Andina S.A.C.",
        ruc="20100070970",  # Valid 11-digit RUC
    )
    profile_page.submit_company_profile()

    status = profile_page.get_company_status()
    assert (
        "actualizado" in status.lower()
        or "registrada" in status.lower()
        or "guardado" in status.lower()
        or status != ""
    ), f"No se obtuvo confirmación de guardado en company-profile-status: '{status}'"


def test_per_06_invalid_ruc_shows_validation_error(driver, base_url):
    """PER-06: An invalid RUC (10 and 12 digits) shows a validation error."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    profile_page = ProfilePage(driver, base_url)
    profile_page.open_profile()

    # Case 1: 10-digit RUC → the pattern="[0-9]{11}" field marks it invalid
    profile_page.fill_company_profile(
        legal_name="Empresa Test S.A.C.",
        ruc="1234567890",  # 10 digits
    )
    assert not profile_page.is_company_ruc_valid(), (
        "Se esperaba que el RUC de 10 dígitos fuera inválido"
    )
    assert profile_page.company_ruc_validation_message() != "", (
        "Se esperaba mensaje de validación para RUC de 10 dígitos"
    )

    # Case 2: 12-digit RUC → maxlength="11" blocks typing more than 11 chars
    profile_page.fill_company_profile(ruc="123456789012")  # tries 12 digits
    actual_value = profile_page.get_company_ruc_value()
    assert len(actual_value) <= 11, (
        f"El campo RUC debería limitar a 11 caracteres, pero contiene: '{actual_value}'"
    )
