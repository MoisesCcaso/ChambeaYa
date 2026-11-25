"""Centralized error handling: business errors and HTTP errors are answered as JSON."""

import pytest

from shared.errors import (
    AuthenticationError,
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
)


@pytest.mark.parametrize(
    ("error_class", "status_code"),
    [
        (DomainError, 400),
        (AuthenticationError, 401),
        (ForbiddenError, 403),
        (NotFoundError, 404),
        (ConflictError, 409),
    ],
)
def test_domain_errors_map_to_their_http_status(app, error_class, status_code):
    @app.get("/_test/domain-error")
    def raise_domain_error():
        raise error_class("Mensaje de negocio")

    response = app.test_client().get("/_test/domain-error")

    assert response.status_code == status_code
    assert response.get_json() == {"error": "Mensaje de negocio"}


def test_domain_errors_are_still_value_errors():
    # Existing callers catch ValueError; the hierarchy must keep that contract.
    assert issubclass(DomainError, ValueError)
    assert all(issubclass(cls, DomainError) for cls in
               (AuthenticationError, ForbiddenError, NotFoundError, ConflictError))


def test_unexpected_error_returns_generic_500_without_leaking_details(app):
    @app.get("/_test/crash")
    def crash():
        raise RuntimeError("detalle interno con datos sensibles")

    response = app.test_client().get("/_test/crash")

    assert response.status_code == 500
    assert response.get_json() == {"error": "Error interno del servidor"}


def test_plain_value_error_is_treated_as_internal_error(app):
    @app.get("/_test/bug")
    def bug():
        int("no-es-numero")

    response = app.test_client().get("/_test/bug")

    assert response.status_code == 500
    assert response.get_json() == {"error": "Error interno del servidor"}


def test_unknown_api_route_returns_json_404(client):
    response = client.get("/convocatorias/no-existe/recurso")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Recurso no encontrado"}


def test_wrong_http_method_returns_json_405(client):
    response = client.delete("/auth/login")

    assert response.status_code == 405
    assert response.get_json() == {"error": "Método no permitido para este recurso"}


def test_browser_navigation_also_gets_json_because_the_api_has_no_views(client):
    response = client.get("/pagina-inexistente", headers={"Accept": "text/html"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Recurso no encontrado"}


def test_certificate_pdf_requires_authentication(client):
    response = client.get("/certificados/practica/1/pdf")

    assert response.status_code == 401
    assert response.get_json() == {"error": "No autenticado"}
