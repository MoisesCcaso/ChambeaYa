# Reporte de SonarQube — ChambeaYa

| Dato | Valor |
|---|---|
| Proyecto | `chambeaya` |
| Herramienta | SonarQube Community 25.1 |
| Incidencias abiertas | **34** |
| Reglas incumplidas | 9 |
| Archivos afectados | 14 |
| Deuda técnica estimada | 4 h 59 min |

Las rutas de archivo son relativas a `src/main/`. Los hallazgos que SonarQube no detecta están en `13-issues_por_resolver_chambeaya.md`.

## Resumen

| Severidad | Incidencias |
|---|---:|
| Alta | 18 |
| Media | 15 |
| Baja | 1 |

| Dimensión de calidad | Incidencias |
|---|---:|
| Mantenibilidad | 30 |
| Seguridad | 2 |
| Fiabilidad | 2 |

## Incidencias por regla

| ID | Regla | Qué indica | Severidad | Dimensión | Casos | Esfuerzo |
|---|---|---|---|---|---:|---:|
| SQ1 | `python:S1192` | Literales de texto duplicados: definir una constante | Alta | Mantenibilidad | 14 | 2 h 14 min |
| SQ2 | `javascript:S3776` | Complejidad cognitiva por encima del límite (15) | Alta | Mantenibilidad | 2 | 23 min |
| SQ3 | `python:S4830` | Validación del certificado TLS deshabilitada | Alta | Seguridad | 1 | 5 min |
| SQ4 | `python:S6437` | Contraseña escrita en el código fuente | Alta | Seguridad | 1 | 1 h |
| SQ5 | `javascript:S3358` | Operadores ternarios anidados | Media | Mantenibilidad | 9 | 45 min |
| SQ6 | `Web:S5255` | Elemento interactivo sin `aria-label` ni `aria-labelledby` | Media | Mantenibilidad | 4 | 20 min |
| SQ7 | `Web:S5256` | Tabla sin celdas de encabezado `<th>` | Media | Fiabilidad | 1 | 2 min |
| SQ8 | `Web:S6853` | `<label>` sin control de formulario asociado | Media | Fiabilidad | 1 | 5 min |
| SQ9 | `python:S1481` | Variable local declarada y sin usar | Baja | Mantenibilidad | 1 | 5 min |

## Detalle

### SQ1 · Literales de texto duplicados: definir una constante

`python:S1192` · Severidad **Alta** · Mantenibilidad · 14 casos

| Archivo | Línea | Mensaje de SonarQube |
|---|---:|---|
| `application/convocatoria_application_service.py` | 26 | Define a constant instead of duplicating this literal "Convocatoria no encontrada" 4 times. |
| `application/postulacion_application_service.py` | 22 | Define a constant instead of duplicating this literal "Perfil de practicante no encontrado" 3 times. |
| `application/postulacion_application_service.py` | 28 | Define a constant instead of duplicating this literal "Convocatoria no encontrada" 3 times. |
| `application/postulacion_application_service.py` | 83 | Define a constant instead of duplicating this literal "Postulación no encontrada" 4 times. |
| `application/practica_application_service.py` | 23 | Define a constant instead of duplicating this literal "Postulación no encontrada" 3 times. |
| `application/practica_application_service.py` | 29 | Define a constant instead of duplicating this literal "Convocatoria no encontrada" 3 times. |
| `frameworks/flask_mvc/routes/convocatoria_routes.py` | 36 | Define a constant instead of duplicating this literal "No autenticado" 8 times. |
| `frameworks/flask_mvc/routes/convocatoria_routes.py` | 39 | Define a constant instead of duplicating this literal "Empresa no encontrada para este usuario" 8 times. |
| `frameworks/flask_mvc/routes/notificacion_routes.py` | 25 | Define a constant instead of duplicating this literal "No autenticado" 4 times. |
| `frameworks/flask_mvc/routes/perfil_routes.py` | 27 | Define a constant instead of duplicating this literal "No autenticado" 7 times. |
| `frameworks/flask_mvc/routes/postulacion_routes.py` | 44 | Define a constant instead of duplicating this literal "No autenticado" 7 times. |
| `frameworks/flask_mvc/routes/postulacion_routes.py` | 72 | Define a constant instead of duplicating this literal "Empresa no encontrada para este usuario" 4 times. |
| `frameworks/flask_mvc/routes/practica_routes.py` | 57 | Define a constant instead of duplicating this literal "Empresa no encontrada para este usuario" 4 times. |
| `frameworks/flask_mvc/routes/web_routes.py` | 16 | Define a constant instead of duplicating this literal "auth.html" 5 times. |

### SQ2 · Complejidad cognitiva por encima del límite (15)

`javascript:S3776` · Severidad **Alta** · Mantenibilidad · 2 casos

| Archivo | Línea | Mensaje de SonarQube |
|---|---:|---|
| `frameworks/flask_mvc/static/js/app.js` | 299 | Refactor this function to reduce its Cognitive Complexity from 20 to the 15 allowed. |
| `frameworks/flask_mvc/static/js/auth.js` | 87 | Refactor this function to reduce its Cognitive Complexity from 23 to the 15 allowed. |

### SQ3 · Validación del certificado TLS deshabilitada

`python:S4830` · Severidad **Alta** · Seguridad · 1 caso

> **Nota:** Probable falso positivo: `starttls()` usa `ssl.create_default_context()`, que sí valida el certificado. El riesgo real de esa conexión es otro (ver S10 en `13-issues_por_resolver_chambeaya.md`).

| Archivo | Línea | Mensaje de SonarQube |
|---|---:|---|
| `infrastructure/smtp_auth_email_sender.py` | 176 | Enable server certificate validation on this SSL/TLS connection. |

### SQ4 · Contraseña escrita en el código fuente

`python:S6437` · Severidad **Alta** · Seguridad · 1 caso

| Archivo | Línea | Mensaje de SonarQube |
|---|---:|---|
| `frameworks/flask_mvc/demo.py` | 69 | Revoke and change this password, as it is compromised. |

### SQ5 · Operadores ternarios anidados

`javascript:S3358` · Severidad **Media** · Mantenibilidad · 9 casos

| Archivo | Línea | Mensaje de SonarQube |
|---|---:|---|
| `frameworks/flask_mvc/static/js/app.js` | 357 | Extract this nested ternary operation into an independent statement. |
| `frameworks/flask_mvc/static/js/app.js` | 358 | Extract this nested ternary operation into an independent statement. |
| `frameworks/flask_mvc/static/js/app.js` | 361 | Extract this nested ternary operation into an independent statement. |
| `frameworks/flask_mvc/static/js/app.js` | 374 | Extract this nested ternary operation into an independent statement. |
| `frameworks/flask_mvc/static/js/app.js` | 473 | Extract this nested ternary operation into an independent statement. |
| `frameworks/flask_mvc/static/js/app.js` | 830 | Extract this nested ternary operation into an independent statement. |
| `frameworks/flask_mvc/static/js/app.js` | 831 | Extract this nested ternary operation into an independent statement. |
| `frameworks/flask_mvc/static/js/app.js` | 834 | Extract this nested ternary operation into an independent statement. |
| `frameworks/flask_mvc/static/js/app.js` | 975 | Extract this nested ternary operation into an independent statement. |

### SQ6 · Elemento interactivo sin `aria-label` ni `aria-labelledby`

`Web:S5255` · Severidad **Media** · Mantenibilidad · 4 casos

| Archivo | Línea | Mensaje de SonarQube |
|---|---:|---|
| `frameworks/flask_mvc/templates/app.html` | 13 | Add an "aria-label" or "aria-labbelledby" attribute to this element. |
| `frameworks/flask_mvc/templates/app.html` | 115 | Add an "aria-label" or "aria-labbelledby" attribute to this element. |
| `frameworks/flask_mvc/templates/app.html` | 138 | Add an "aria-label" or "aria-labbelledby" attribute to this element. |
| `frameworks/flask_mvc/templates/app.html` | 189 | Add an "aria-label" or "aria-labbelledby" attribute to this element. |

### SQ7 · Tabla sin celdas de encabezado `<th>`

`Web:S5256` · Severidad **Media** · Fiabilidad · 1 caso

| Archivo | Línea | Mensaje de SonarQube |
|---|---:|---|
| `frameworks/flask_mvc/templates/app.html` | 124 | Add "&lt;th&gt;" headers to this "&lt;table&gt;". |

### SQ8 · `<label>` sin control de formulario asociado

`Web:S6853` · Severidad **Media** · Fiabilidad · 1 caso

| Archivo | Línea | Mensaje de SonarQube |
|---|---:|---|
| `frameworks/flask_mvc/templates/app.html` | 185 | A form label must be associated with a control. |

### SQ9 · Variable local declarada y sin usar

`python:S1481` · Severidad **Baja** · Mantenibilidad · 1 caso

| Archivo | Línea | Mensaje de SonarQube |
|---|---:|---|
| `frameworks/flask_mvc/demo.py` | 42 | Replace the unused local variable "width" with "_". |

---

Exportado de SonarQube el 2026-07-27 mediante su API (`/api/issues/search`). Las métricas globales del proyecto (cobertura, rating de mantenibilidad) no se incluyeron: el token usado era de análisis y no tiene permiso para leerlas.
