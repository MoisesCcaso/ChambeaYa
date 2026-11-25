"""Centralized error handling: every API error is answered as JSON {"error": "<mensaje>"}."""

from flask import jsonify, request
from flask_wtf.csrf import CSRFError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from application.email_delivery_error import EmailDeliveryError
from shared.database import db
from shared.errors import DomainError

# User-facing texts stay in Spanish (the site targets Peru).
HTTP_ERROR_MESSAGES = {
    400: "Solicitud inválida",
    401: "No autenticado",
    403: "No tienes permiso para realizar esta acción",
    404: "Recurso no encontrado",
    405: "Método no permitido para este recurso",
    413: "El archivo excede el límite de 10 MB",
    415: "Tipo de contenido no soportado",
    500: "Error interno del servidor",
}


def _error(message, status_code):
    return jsonify({"error": message}), status_code


def _wants_html():
    # A browser navigating to a page gets the HTML error page; API clients (fetch, Postman) get JSON.
    return request.accept_mimetypes.best == "text/html"


def register_error_handlers(app):
    @app.errorhandler(DomainError)
    def handle_domain_error(error):
        return _error(str(error), error.status_code)

    @app.errorhandler(EmailDeliveryError)
    def handle_email_delivery_error(error):
        return _error(str(error), 503)

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(_error):
        db.session.rollback()
        return _error("El registro ya existe o contiene datos en conflicto", 409)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        return _error(f"Solicitud rechazada: {error.description}", 400)

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        if _wants_html():
            return error
        return _error(HTTP_ERROR_MESSAGES.get(error.code, error.name), error.code)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        db.session.rollback()
        app.logger.exception("Unhandled error on %s %s", request.method, request.path)
        return _error(HTTP_ERROR_MESSAGES[500], 500)
