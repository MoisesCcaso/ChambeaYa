"""Job posting functional tests assigned to I5."""

from uuid import uuid4

from selenium.webdriver.common.by import By

if __package__:
    from .pages.job_posting_page import JobPostingPage
    from .pages.login_page import LoginPage
else:
    from pages.job_posting_page import JobPostingPage
    from pages.login_page import LoginPage


def test_con_01_creates_valid_job_posting_as_draft(driver, base_url):
    """A company can create a valid job posting as a draft."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    page = JobPostingPage(driver, base_url)
    page.open_job_postings()

    title = f"Practicante QA funcional {uuid4().hex[:8]}"
    page.create_draft(
        title=title,
        description="Apoyo en pruebas funcionales y documentación.",
        skills="Python, Selenium, pytest",
        benefits="Mentoría, horario flexible",
    )

    assert page.job_posting_is_draft(title)


def test_con_02_rejects_job_posting_without_title(driver, base_url):
    """The form prevents saving a job posting without a title."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    page = JobPostingPage(driver, base_url)
    page.open_job_postings()
    page.start_new_job_posting()
    page.fill_job_posting(
        title="",
        description="Convocatoria de prueba sin título.",
        skills="Python",
    )
    rows_before = len(
        driver.find_element(*page.TABLE).find_elements(By.TAG_NAME, "tr")
    )
    page.save_draft()

    title = driver.find_element(*page.TITLE)
    assert not driver.execute_script("return arguments[0].validity.valid;", title)
    assert driver.execute_script("return arguments[0].validationMessage;", title)
    assert (
        len(driver.find_element(*page.TABLE).find_elements(By.TAG_NAME, "tr"))
        == rows_before
    )


def test_con_03_publishes_draft_job_posting(driver, base_url):
    """A company can publish a draft job posting."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    page = JobPostingPage(driver, base_url)
    page.open_job_postings()
    title = f"Practicante QA publicación {uuid4().hex[:8]}"
    page.create_draft(
        title=title,
        description="Convocatoria creada para probar su publicación.",
        skills="Python, Selenium",
    )

    assert page.job_posting_is_draft(title)
    page.publish_job_posting(title)

    assert page.job_posting_is_published(title)


def test_con_04_does_not_offer_publishing_an_already_published_job_posting(driver, base_url):
    """A published job posting no longer offers the Publish action."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    page = JobPostingPage(driver, base_url)
    page.open_job_postings()
    title = f"Practicante QA publicación única {uuid4().hex[:8]}"
    page.create_draft(
        title=title,
        description="Convocatoria para verificar que publicar no se repita.",
        skills="Python, Selenium",
    )

    assert page.job_posting_is_draft(title)
    page.publish_job_posting(title)

    assert page.job_posting_is_published(title)
    assert not page.can_publish_job_posting(title)


def test_con_05_closes_published_job_posting(driver, base_url):
    """A company can close a published job posting."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    page = JobPostingPage(driver, base_url)
    page.open_job_postings()
    title = f"Practicante QA cierre {uuid4().hex[:8]}"
    page.create_draft(
        title=title,
        description="Convocatoria creada para probar el cierre.",
        skills="Python, Selenium",
    )

    assert page.job_posting_is_draft(title)
    page.publish_job_posting(title)
    assert page.job_posting_is_published(title)

    page.close_job_posting(title)

    assert page.job_posting_is_closed(title)


def test_con_06_shows_job_posting_candidates(driver, base_url):
    """The company can see the intern who applied to a demo job posting."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login("empresa@demo.local", "Demo1234")
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Empresa"

    page = JobPostingPage(driver, base_url)
    page.open_job_postings()
    page.open_candidates("Practicante de aseguramiento de calidad")

    assert page.candidate_is_listed("Andrea Quispe")
