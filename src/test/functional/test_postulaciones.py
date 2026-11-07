"""Pruebas funcionales de oportunidades, postulaciones y certificado público (I6)."""

from uuid import uuid4

if __package__:
    from . import postulacion_data
    from .pages.login_page import LoginPage
    from .pages.postulacion_page import PostulacionPage, VerificarCertificadoPage
else:
    import postulacion_data
    from pages.login_page import LoginPage
    from pages.postulacion_page import PostulacionPage, VerificarCertificadoPage

DEMO_PRACTICANTE = ("practicante@demo.local", "Demo1234")


def _titulo(prefijo: str) -> str:
    """Título único para que cada prueba encuentre solo sus propios datos."""
    return f"{prefijo} {uuid4().hex[:8]}"


def _login_practicante(driver, base_url, email: str, password: str) -> None:
    """Inicia sesión por la interfaz y comprueba que entra como practicante."""
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    login_page.login(email, password)
    login_page.wait_for_path("/app")
    assert login_page.role_label == "Practicante"


def test_pos_01_lista_solo_convocatorias_publicadas(driver, base_url):
    """Oportunidades muestra las convocatorias publicadas y oculta los borradores."""
    publicada = _titulo("Practicante publicada")
    borrador = _titulo("Practicante borrador")
    postulacion_data.create_opening(base_url, publicada)
    postulacion_data.create_opening(base_url, borrador, publicar=False)

    _login_practicante(driver, base_url, *DEMO_PRACTICANTE)
    page = PostulacionPage(driver, base_url).open_oportunidades()

    assert page.opportunity_is_listed(publicada)
    assert not page.opportunity_is_listed(borrador)


def test_pos_02_postula_a_convocatoria_publicada(driver, base_url):
    """Un practicante con perfil completo postula y ve su postulación pendiente."""
    titulo = _titulo("Practicante postulacion")
    opening_id = postulacion_data.create_opening(base_url, titulo)
    user = postulacion_data.create_student_with_profile(base_url)

    _login_practicante(driver, base_url, user["email"], user["password"])
    page = PostulacionPage(driver, base_url).open_oportunidades()
    page.select_opportunity(opening_id)
    aviso = page.apply(opening_id)

    assert "Postulación registrada correctamente" in aviso
    page.open_postulaciones()
    assert page.application_has_status(titulo, "pendiente")


def test_pos_03_no_permite_postular_dos_veces(driver, base_url):
    """Tras postular, la interfaz retira el botón y el servidor rechaza el duplicado."""
    titulo = _titulo("Practicante duplicada")
    opening_id = postulacion_data.create_opening(base_url, titulo)
    user = postulacion_data.create_student_with_profile(base_url)

    _login_practicante(driver, base_url, user["email"], user["password"])
    page = PostulacionPage(driver, base_url).open_oportunidades()
    page.select_opportunity(opening_id)
    page.apply(opening_id)

    assert "status-pendiente" in page.detail_status_class()
    assert not page.apply_button_is_present(opening_id)
    page.open_postulaciones()
    assert page.application_count(titulo) == 1

    api = postulacion_data.login(base_url, user["email"], user["password"])
    codigo, cuerpo = api.call("POST", f"/postulaciones/convocatorias/{opening_id}")
    assert codigo == 400
    assert "Ya existe una postulación" in cuerpo["error"]


def test_pos_04_no_permite_postular_a_convocatoria_cerrada(driver, base_url):
    """Una convocatoria cerrada no se ofrece y el servidor rechaza postular."""
    titulo = _titulo("Practicante cerrada")
    opening_id = postulacion_data.create_opening(base_url, titulo, cerrar=True)
    user = postulacion_data.create_student_with_profile(base_url)

    _login_practicante(driver, base_url, user["email"], user["password"])
    page = PostulacionPage(driver, base_url).open_oportunidades()
    assert not page.opportunity_is_listed(titulo)

    api = postulacion_data.login(base_url, user["email"], user["password"])
    codigo, cuerpo = api.call("POST", f"/postulaciones/convocatorias/{opening_id}")
    assert codigo == 400
    assert "Solo se puede postular a convocatorias publicadas" in cuerpo["error"]


def test_pos_05_verifica_certificado_con_codigo_valido(driver, base_url):
    """La página pública reconoce un certificado emitido con su código real."""
    codigo = postulacion_data.create_issued_certificate(base_url)

    page = VerificarCertificadoPage(driver, base_url).open_verificacion()
    page.verify(codigo)

    assert page.result_is_valid
    assert "Certificado válido" in page.result_text


def test_pos_06_rechaza_codigo_de_certificado_inexistente(driver, base_url):
    """Un código que no existe muestra el mensaje de certificado no encontrado."""
    page = VerificarCertificadoPage(driver, base_url).open_verificacion()
    page.verify("XXXX-0000")

    assert not page.result_is_valid
    assert "Certificado no encontrado" in page.result_text
