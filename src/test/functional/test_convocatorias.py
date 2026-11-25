"""Pruebas funcionales de convocatorias asignadas a I5."""

from uuid import uuid4

from selenium.webdriver.common.by import By

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

    title = f"Practicante QA funcional {uuid4().hex[:8]}"
    page.create_draft(
        title=title,
        description="Apoyo en pruebas funcionales y documentación.",
        skills="Python, Selenium, pytest",
        benefits="Mentoría, horario flexible",
    )

    assert page.convocatoria_is_borrador(title)


def test_con_02_rechaza_convocatoria_sin_titulo(driver, base_url):
    """El formulario impide guardar una convocatoria sin título."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    page = ConvocatoriaPage(driver, base_url)
    page.open_convocatorias()
    page.start_new_convocatoria()
    page.fill_convocatoria(
        title="",
        description="Convocatoria de prueba sin título.",
        skills="Python",
    )
    filas_antes = len(
        driver.find_element(*page.TABLE).find_elements(By.TAG_NAME, "tr")
    )
    page.save_draft()

    title = driver.find_element(*page.TITLE)
    assert not driver.execute_script("return arguments[0].validity.valid;", title)
    assert driver.execute_script("return arguments[0].validationMessage;", title)
    assert (
        len(driver.find_element(*page.TABLE).find_elements(By.TAG_NAME, "tr"))
        == filas_antes
    )


def test_con_03_publica_convocatoria_en_borrador(driver, base_url):
    """Una empresa puede publicar una convocatoria que está en borrador."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    page = ConvocatoriaPage(driver, base_url)
    page.open_convocatorias()
    title = f"Practicante QA publicación {uuid4().hex[:8]}"
    page.create_draft(
        title=title,
        description="Convocatoria creada para probar su publicación.",
        skills="Python, Selenium",
    )

    assert page.convocatoria_is_borrador(title)
    page.publish_job_posting(title)

    assert page.convocatoria_is_publicada(title)


def test_con_04_no_ofrece_publicar_convocatoria_ya_publicada(driver, base_url):
    """Una convocatoria publicada deja de ofrecer la acción Publicar."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    page = ConvocatoriaPage(driver, base_url)
    page.open_convocatorias()
    title = f"Practicante QA publicación única {uuid4().hex[:8]}"
    page.create_draft(
        title=title,
        description="Convocatoria para verificar que publicar no se repita.",
        skills="Python, Selenium",
    )

    assert page.convocatoria_is_borrador(title)
    page.publish_job_posting(title)

    assert page.convocatoria_is_publicada(title)
    assert not page.can_publish_convocatoria(title)


def test_con_05_cierra_convocatoria_publicada(driver, base_url):
    """Una empresa puede cerrar una convocatoria publicada."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    page = ConvocatoriaPage(driver, base_url)
    page.open_convocatorias()
    title = f"Practicante QA cierre {uuid4().hex[:8]}"
    page.create_draft(
        title=title,
        description="Convocatoria creada para probar el cierre.",
        skills="Python, Selenium",
    )

    assert page.convocatoria_is_borrador(title)
    page.publish_job_posting(title)
    assert page.convocatoria_is_publicada(title)

    page.close_job_posting(title)

    assert page.convocatoria_is_cerrada(title)


def test_con_06_muestra_candidatos_de_convocatoria(driver, base_url):
    """La empresa puede ver al practicante postulado a una convocatoria demo."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    page = ConvocatoriaPage(driver, base_url)
    page.open_convocatorias()
    page.open_candidates("Practicante de aseguramiento de calidad")

    assert page.candidate_is_listed("Andrea Quispe")
