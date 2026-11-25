"""CORS: only the client origin gets credentialed access to the API."""

import pytest

from bootstrap.app import create_app

CLIENT = "http://127.0.0.1:5001"


@pytest.fixture
def client():
    app = create_app("testing")
    app.config["SECRET_KEY"] = "testing-secret"
    return app.test_client()


def test_allowed_origin_gets_credentialed_cors_headers(client):
    response = client.get("/health", headers={"Origin": CLIENT})

    assert response.headers["Access-Control-Allow-Origin"] == CLIENT
    assert response.headers["Access-Control-Allow-Credentials"] == "true"
    assert "X-CSRFToken" in response.headers["Access-Control-Allow-Headers"]
    assert "Origin" in response.headers["Vary"]


def test_foreign_origin_gets_no_cors_headers(client):
    response = client.get("/health", headers={"Origin": "http://evil.example"})

    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers
    assert "Access-Control-Allow-Credentials" not in response.headers


def test_preflight_for_a_write_is_answered_with_200(client):
    response = client.options(
        "/auth/login",
        headers={
            "Origin": CLIENT,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, X-CSRFToken",
        },
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == CLIENT
    assert "POST" in response.headers["Access-Control-Allow-Methods"]


def test_api_serves_no_views_or_static_assets(client):
    for path in ("/", "/ingresar", "/app", "/static/js/app.js"):
        response = client.get(path)
        assert response.status_code == 404
        assert response.is_json
