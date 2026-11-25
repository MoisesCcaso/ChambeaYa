"""Functional tests for opportunities, job applications and the public certificate (I6)."""

from uuid import uuid4

if __package__:
    from . import job_application_data
    from .pages.login_page import LoginPage
    from .pages.job_application_page import JobApplicationPage, VerifyCertificatePage
else:
    import job_application_data
    from pages.login_page import LoginPage
    from pages.job_application_page import JobApplicationPage, VerifyCertificatePage

DEMO_INTERN = ("practicante@demo.local", "Demo1234")


def _title(prefijo: str) -> str:
    """Unique title so each test only finds its own data."""
    return f"{prefijo} {uuid4().hex[:8]}"


def _login_intern(driver, base_url, email: str, password: str) -> None:
    """Logs in through the UI and checks it enters as an intern."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login(email, password)
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Practicante"


def test_pos_01_lista_solo_convocatorias_publicadas(driver, base_url):
    """Opportunities shows published job postings and hides drafts."""
    published = _title("Practicante publicada")
    draft = _title("Practicante borrador")
    job_application_data.create_opening(base_url, published)
    job_application_data.create_opening(base_url, draft, publish=False)

    _login_intern(driver, base_url, *DEMO_INTERN)
    page = JobApplicationPage(driver, base_url).open_opportunities()

    assert page.opportunity_is_listed(published)
    assert not page.opportunity_is_listed(draft)


def test_pos_02_applies_to_published_job_posting(driver, base_url):
    """An intern with a complete profile applies and sees the pending application."""
    title = _title("Practicante postulacion")
    opening_id = job_application_data.create_opening(base_url, title)
    user = job_application_data.create_student_with_profile(base_url)

    _login_intern(driver, base_url, user["email"], user["password"])
    page = JobApplicationPage(driver, base_url).open_opportunities()
    page.select_opportunity(opening_id)
    aviso = page.apply(opening_id)

    assert "Postulación registrada correctamente" in aviso
    page.open_applications()
    assert page.application_has_status(title, "pendiente")


def test_pos_03_does_not_allow_applying_twice(driver, base_url):
    """After applying, the UI removes the button and the server rejects the duplicate."""
    title = _title("Practicante duplicada")
    opening_id = job_application_data.create_opening(base_url, title)
    user = job_application_data.create_student_with_profile(base_url)

    _login_intern(driver, base_url, user["email"], user["password"])
    page = JobApplicationPage(driver, base_url).open_opportunities()
    page.select_opportunity(opening_id)
    page.apply(opening_id)

    assert "status-pendiente" in page.detail_status_class()
    assert not page.apply_button_is_present(opening_id)
    page.open_applications()
    assert page.application_count(title) == 1

    api = job_application_data.login(base_url, user["email"], user["password"])
    code, cuerpo = api.call("POST", f"/postulaciones/convocatorias/{opening_id}")
    assert code == 409
    assert "Ya existe una postulación" in cuerpo["error"]


def test_pos_04_does_not_allow_applying_to_closed_job_posting(driver, base_url):
    """A closed job posting is not offered and the server rejects applying."""
    title = _title("Practicante cerrada")
    opening_id = job_application_data.create_opening(base_url, title, close=True)
    user = job_application_data.create_student_with_profile(base_url)

    _login_intern(driver, base_url, user["email"], user["password"])
    page = JobApplicationPage(driver, base_url).open_opportunities()
    assert not page.opportunity_is_listed(title)

    api = job_application_data.login(base_url, user["email"], user["password"])
    code, cuerpo = api.call("POST", f"/postulaciones/convocatorias/{opening_id}")
    assert code == 409
    assert "Solo se puede postular a convocatorias publicadas" in cuerpo["error"]


def test_pos_05_verifies_certificate_with_valid_code(driver, base_url):
    """The public page recognizes an issued certificate by its real code."""
    code = job_application_data.create_issued_certificate(base_url)

    page = VerifyCertificatePage(driver, base_url).open_verification()
    page.verify(code)

    assert page.result_is_valid
    assert "Certificado válido" in page.result_text


def test_pos_06_rejects_unknown_certificate_code(driver, base_url):
    """An unknown code shows the certificate-not-found message."""
    page = VerifyCertificatePage(driver, base_url).open_verification()
    page.verify("XXXX-0000")

    assert not page.result_is_valid
    assert "Certificado no encontrado" in page.result_text
