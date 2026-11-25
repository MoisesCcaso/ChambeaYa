"""Client app (views): serves HTML/CSS/JS only and talks to the API by HTTP (import rule: architecture tests)."""

from pathlib import Path

import pytest

from client.app import create_app

CLIENT_DIR = Path(__file__).resolve().parents[2] / "main" / "client"


@pytest.fixture
def client():
    return create_app({"TESTING": True, "API_URL": "http://api.test:5000"}).test_client()


@pytest.mark.parametrize("path", [
    "/", "/ingresar", "/registro", "/activar", "/recuperar", "/restablecer",
    "/verificar-certificado", "/app",
])
def test_views_answer_200_without_session(client, path):
    response = client.get(path)

    assert response.status_code == 200
    assert response.mimetype == "text/html"


def test_base_template_exposes_the_api_url_to_the_js(client):
    html = client.get("/ingresar").get_data(as_text=True)

    assert 'window.CHAMBEAYA_API_URL = "http://api.test:5000";' in html
    assert "csrf-token" not in html


def test_auth_and_app_views_keep_their_key_elements(client):
    register_view = client.get("/registro").data
    assert b'name="password_confirmation"' in register_view
    assert b'id="password-requirements"' in register_view
    assert b'id="activation-email-field"' in client.get("/activar").data

    app_view = client.get("/app").data
    assert b'id="app-shell"' in app_view
    assert b'id="confirmation-dialog"' in app_view
    assert b'data-filter="cancelada"' in app_view


def test_demo_buttons_only_in_demo_mode():
    demo = create_app({"TESTING": True, "DEMO_MODE": True, "DEMO_PASSWORD": "Demo1234"}).test_client()
    plain = create_app({"TESTING": True, "DEMO_MODE": False}).test_client()

    assert b"data-demo-login" in demo.get("/ingresar").data
    assert b"data-demo-login" not in plain.get("/ingresar").data


@pytest.mark.parametrize("asset", [
    "/static/css/app.css", "/static/js/common.js", "/static/js/auth.js", "/static/js/verify.js",
    "/static/js/app.js", "/static/icons.svg", "/static/img/chambeaYa_icon.ico",
    "/static/img/chambeaya-logo-horizontal.png", "/static/img/chambeaya-logo-square.png",
])
def test_static_assets_are_served(client, asset):
    response = client.get(asset)

    assert response.status_code == 200
    assert len(response.data) > 0
    response.close()


def test_app_script_keeps_its_actions_and_uses_api_links(client):
    script = client.get("/static/js/app.js").data
    for action in (
        b"data-delete-opening", b"data-duplicate-opening", b"data-reopen-opening",
        b"data-cancel-application", b"data-reconsider-candidate",
        b"data-delete-deliverable", b"data-delete-evaluation",
    ):
        assert action in script
    assert script.count(b"C.apiUrl(") == 5


def test_common_script_calls_the_api_with_credentials_and_csrf_from_the_api():
    common = (CLIENT_DIR / "static" / "js" / "common.js").read_text(encoding="utf-8")

    assert 'credentials: "include"' in common
    assert 'apiUrl("/auth/csrf-token")' in common
    assert "window.CHAMBEAYA_API_URL" in common

