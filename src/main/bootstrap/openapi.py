"""OpenAPI route inventory generated from the Flask REST route map.

Deriving paths from the registered API blueprints keeps ZAP's scan targets
aligned with the routes that the server actually exposes.
"""

import re

from flask import jsonify, request


API_BLUEPRINTS = {
    "auth",
    "certificado",
    "convocatoria",
    "health",
    "matching",
    "notificacion",
    "perfil",
    "postulacion",
    "practica",
}
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
PATH_PARAMETER = re.compile(r"<(?:(\w+):)?(\w+)(?:\([^<>]*\))?>")


def _openapi_path(rule):
    return PATH_PARAMETER.sub(r"{\2}", rule)


def _parameter_type(converter):
    converter_name = type(converter).__name__.lower()
    if "integer" in converter_name:
        return {"type": "integer"}
    if "float" in converter_name:
        return {"type": "number", "format": "float"}
    if "uuid" in converter_name:
        return {"type": "string", "format": "uuid"}
    return {"type": "string"}


def build_openapi_document(app, server_url):
    """Return an OpenAPI 3.0 document for the application's REST blueprints."""
    paths = {}
    for rule in app.url_map.iter_rules():
        blueprint_name = rule.endpoint.split(".", 1)[0]
        if blueprint_name not in API_BLUEPRINTS:
            continue

        path = _openapi_path(rule.rule)
        path_item = paths.setdefault(path, {})
        parameters = [
            {
                "name": argument,
                "in": "path",
                "required": True,
                "schema": _parameter_type(rule._converters[argument]),
            }
            for argument in sorted(rule.arguments)
        ]
        methods = {method.lower() for method in (rule.methods or ())}
        for method in sorted(HTTP_METHODS.intersection(methods)):
            operation = {
                "operationId": f"{blueprint_name}_{rule.endpoint.split('.', 1)[1]}_{method}",
                "summary": rule.endpoint.split(".", 1)[1].replace("_", " ").capitalize(),
                "responses": {
                    "200": {"description": "Solicitud procesada"},
                    "201": {"description": "Recurso creado"},
                    "400": {"description": "Solicitud inválida"},
                    "401": {"description": "Autenticación requerida"},
                    "403": {"description": "Operación no permitida"},
                    "404": {"description": "Recurso no encontrado"},
                },
            }
            if parameters:
                operation["parameters"] = parameters
            if rule.endpoint == "convocatoria.list_job_postings" and method == "get":
                operation["parameters"] = [
                    {
                        "name": "q",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"},
                        "description": "Texto para buscar convocatorias publicadas.",
                    }
                ]

            if method in {"post", "put", "patch"}:
                if rule.endpoint == "practica.upload_deliverable":
                    content = {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {"archivo": {"type": "string", "format": "binary"}},
                            }
                        }
                    }
                else:
                    content = {
                        "application/json": {
                            "schema": {"type": "object", "additionalProperties": True}
                        }
                    }
                operation["requestBody"] = {
                    "required": False,
                    "content": content,
                }
            path_item[method] = operation

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "ChambeaYa REST API",
            "version": "1.0.0",
            "description": (
                "Operaciones REST registradas en Flask. Las rutas se generan "
                "desde los blueprints del servidor. Las sesiones autenticadas "
                "usan la cookie de sesión de Flask."
            ),
        },
        # Build this from the request serving the document so the same spec works
        # on local, staging, and deployed ports without hardcoding an environment.
        "servers": [{"url": server_url}],
        "paths": paths,
    }


def openapi_json():
    from flask import current_app

    return jsonify(build_openapi_document(current_app, request.host_url.rstrip("/")))
