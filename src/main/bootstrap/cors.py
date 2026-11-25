"""Minimal CORS for the client app: only the exact origins in CLIENT_ORIGINS, with credentials (session cookie)."""

from flask import request


def register_cors(app):
    allowed_origins = {
        origin.strip().rstrip("/")
        for origin in app.config.get("CLIENT_ORIGINS", "").split(",")
        if origin.strip()
    }

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.vary.add("Origin")
        return response
