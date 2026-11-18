# Reporte SonarQube - chambeaya

Generado el 2026-11-18 10:43 desde http://localhost:9000

## Metricas del proyecto

_No disponibles: el token usado no tiene permiso de lectura de metricas._


## Incidencias: 34 exportadas de 34

### Por severidad

| Severidad | Cantidad |
|---|---|
| HIGH | 18 |
| MEDIUM | 15 |
| LOW | 1 |

### Por dimension de calidad

| Dimension | Cantidad |
|---|---|
| MAINTAINABILITY | 30 |
| SECURITY | 2 |
| RELIABILITY | 2 |

### Top 15 reglas mas incumplidas

| Cantidad | Regla |
|---|---|
| 9 | javascript:S3358: Extract this nested ternary operation into an independent st |
| 4 | python:S1192: Define a constant instead of duplicating this literal "No au |
| 4 | Web:S5255: Add an "aria-label" or "aria-labbelledby" attribute to this  |
| 3 | python:S1192: Define a constant instead of duplicating this literal "Convo |
| 3 | python:S1192: Define a constant instead of duplicating this literal "Empre |
| 2 | python:S1192: Define a constant instead of duplicating this literal "Postu |
| 2 | javascript:S3776: Refactor this function to reduce its Cognitive Complexity fr |
| 1 | python:S1192: Define a constant instead of duplicating this literal "Perfi |
| 1 | python:S1481: Replace the unused local variable "width" with "_". |
| 1 | python:S6437: Revoke and change this password, as it is compromised. |
| 1 | python:S1192: Define a constant instead of duplicating this literal "auth. |
| 1 | Web:S5256: Add "<th>" headers to this "<table>". |
| 1 | Web:S6853: A form label must be associated with a control. |
| 1 | python:S4830: Enable server certificate validation on this SSL/TLS connect |

### Top 15 archivos con mas incidencias

| Cantidad | Archivo |
|---|---|
| 10 | `src/main/frameworks/flask_mvc/static/js/app.js` |
| 6 | `src/main/frameworks/flask_mvc/templates/app.html` |
| 3 | `src/main/application/postulacion_application_service.py` |
| 2 | `src/main/application/practica_application_service.py` |
| 2 | `src/main/frameworks/flask_mvc/demo.py` |
| 2 | `src/main/frameworks/flask_mvc/routes/convocatoria_routes.py` |
| 2 | `src/main/frameworks/flask_mvc/routes/postulacion_routes.py` |
| 1 | `src/main/application/convocatoria_application_service.py` |
| 1 | `src/main/frameworks/flask_mvc/routes/notificacion_routes.py` |
| 1 | `src/main/frameworks/flask_mvc/routes/perfil_routes.py` |
| 1 | `src/main/frameworks/flask_mvc/routes/practica_routes.py` |
| 1 | `src/main/frameworks/flask_mvc/routes/web_routes.py` |
| 1 | `src/main/frameworks/flask_mvc/static/js/auth.js` |
| 1 | `src/main/infrastructure/smtp_auth_email_sender.py` |

## Detalle completo

| Archivo | Linea | Severidad | Regla | Mensaje |
|---|---|---|---|---|
| `src/main/application/convocatoria_application_service.py` | 26 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "Convocatoria no encontrada" 4 times. |
| `src/main/application/postulacion_application_service.py` | 22 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "Perfil de practicante no encontrado" 3 times. |
| `src/main/application/postulacion_application_service.py` | 28 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "Convocatoria no encontrada" 3 times. |
| `src/main/application/postulacion_application_service.py` | 83 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "Postulación no encontrada" 4 times. |
| `src/main/application/practica_application_service.py` | 23 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "Postulación no encontrada" 3 times. |
| `src/main/application/practica_application_service.py` | 29 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "Convocatoria no encontrada" 3 times. |
| `src/main/frameworks/flask_mvc/demo.py` | 42 | LOW | python:S1481 | Replace the unused local variable "width" with "_". |
| `src/main/frameworks/flask_mvc/demo.py` | 69 | HIGH | python:S6437 | Revoke and change this password, as it is compromised. |
| `src/main/frameworks/flask_mvc/routes/convocatoria_routes.py` | 36 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "No autenticado" 8 times. |
| `src/main/frameworks/flask_mvc/routes/convocatoria_routes.py` | 39 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "Empresa no encontrada para este usuario" 8 times. |
| `src/main/frameworks/flask_mvc/routes/notificacion_routes.py` | 25 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "No autenticado" 4 times. |
| `src/main/frameworks/flask_mvc/routes/perfil_routes.py` | 27 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "No autenticado" 7 times. |
| `src/main/frameworks/flask_mvc/routes/postulacion_routes.py` | 44 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "No autenticado" 7 times. |
| `src/main/frameworks/flask_mvc/routes/postulacion_routes.py` | 72 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "Empresa no encontrada para este usuario" 4 times. |
| `src/main/frameworks/flask_mvc/routes/practica_routes.py` | 57 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "Empresa no encontrada para este usuario" 4 times. |
| `src/main/frameworks/flask_mvc/routes/web_routes.py` | 16 | HIGH | python:S1192 | Define a constant instead of duplicating this literal "auth.html" 5 times. |
| `src/main/frameworks/flask_mvc/static/js/app.js` | 299 | HIGH | javascript:S3776 | Refactor this function to reduce its Cognitive Complexity from 20 to the 15 allowed. |
| `src/main/frameworks/flask_mvc/static/js/app.js` | 357 | MEDIUM | javascript:S3358 | Extract this nested ternary operation into an independent statement. |
| `src/main/frameworks/flask_mvc/static/js/app.js` | 358 | MEDIUM | javascript:S3358 | Extract this nested ternary operation into an independent statement. |
| `src/main/frameworks/flask_mvc/static/js/app.js` | 361 | MEDIUM | javascript:S3358 | Extract this nested ternary operation into an independent statement. |
| `src/main/frameworks/flask_mvc/static/js/app.js` | 374 | MEDIUM | javascript:S3358 | Extract this nested ternary operation into an independent statement. |
| `src/main/frameworks/flask_mvc/static/js/app.js` | 473 | MEDIUM | javascript:S3358 | Extract this nested ternary operation into an independent statement. |
| `src/main/frameworks/flask_mvc/static/js/app.js` | 830 | MEDIUM | javascript:S3358 | Extract this nested ternary operation into an independent statement. |
| `src/main/frameworks/flask_mvc/static/js/app.js` | 831 | MEDIUM | javascript:S3358 | Extract this nested ternary operation into an independent statement. |
| `src/main/frameworks/flask_mvc/static/js/app.js` | 834 | MEDIUM | javascript:S3358 | Extract this nested ternary operation into an independent statement. |
| `src/main/frameworks/flask_mvc/static/js/app.js` | 975 | MEDIUM | javascript:S3358 | Extract this nested ternary operation into an independent statement. |
| `src/main/frameworks/flask_mvc/static/js/auth.js` | 87 | HIGH | javascript:S3776 | Refactor this function to reduce its Cognitive Complexity from 23 to the 15 allowed. |
| `src/main/frameworks/flask_mvc/templates/app.html` | 13 | MEDIUM | Web:S5255 | Add an "aria-label" or "aria-labbelledby" attribute to this element. |
| `src/main/frameworks/flask_mvc/templates/app.html` | 115 | MEDIUM | Web:S5255 | Add an "aria-label" or "aria-labbelledby" attribute to this element. |
| `src/main/frameworks/flask_mvc/templates/app.html` | 124 | MEDIUM | Web:S5256 | Add "<th>" headers to this "<table>". |
| `src/main/frameworks/flask_mvc/templates/app.html` | 138 | MEDIUM | Web:S5255 | Add an "aria-label" or "aria-labbelledby" attribute to this element. |
| `src/main/frameworks/flask_mvc/templates/app.html` | 185 | MEDIUM | Web:S6853 | A form label must be associated with a control. |
| `src/main/frameworks/flask_mvc/templates/app.html` | 189 | MEDIUM | Web:S5255 | Add an "aria-label" or "aria-labbelledby" attribute to this element. |
| `src/main/infrastructure/smtp_auth_email_sender.py` | 176 | HIGH | python:S4830 | Enable server certificate validation on this SSL/TLS connection. |
