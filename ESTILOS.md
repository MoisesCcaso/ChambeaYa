# Estilos de Programación — ChambeaYa (UC-22)

## 1. Things (Entidades de Dominio Ricas)

**Descripción:** Objetos de dominio que encapsulan datos **y** comportamiento (reglas de
negocio, invariantes, transiciones de estado), en lugar de ser contenedores pasivos de datos.

**Fragmento de código:**
```python
# domain/certificacion/certificado.py
class Certificado:
    def generar_hash(self):
        datos = f"{self.practica_id}{self.fecha_emision}"
        self.hash_integridad = hashlib.sha256(datos.encode()).hexdigest()
        return self.hash_integridad

    def verificar_integridad(self):
        if not self.hash_integridad:
            raise ValueError("Hash de integridad no generado")
        datos = f"{self.practica_id}{self.fecha_emision}"
        return hashlib.sha256(datos.encode()).hexdigest() == self.hash_integridad
```

---

## 2. Error/Exception Handling

**Descripción:** Excepciones como mecanismo principal para comunicar violaciones de reglas
de negocio, fallos de validación y errores de autorización, desde la capa de dominio hasta
los manejadores de rutas que traducen excepciones a códigos HTTP.

**Fragmento de código:**
```python
# application/certificacion_application_service.py
def issue_certificate(self, practica_id):
    practica = self.practica_repository.find_by_id(practica_id)
    if practica is None:
        raise ValueError("Práctica no encontrada")

    practicante = self.perfil_repository.find_practicante_by_user_id(
        practica.practicante_id
    )
    if practicante is None:
        raise ValueError("Practicante no encontrado")

# frameworks/flask_mvc/routes/certificado_routes.py
try:
    data, status_code = controller.issue(payload)
except ValueError as exc:
    return jsonify({"error": str(exc)}), 400
```

---

## 3. Persistent-Tables

**Descripción:** Modelos ORM que mapean entidades de dominio a tablas en base de datos,
usando SQLAlchemy como capa de persistencia con columnas, tipos, claves foráneas y
restricciones de unicidad.

**Fragmento de código:**
```python
# frameworks/sqlalchemy_orm/models/certificado_model.py
class CertificadoModel(db.Model):
    __tablename__ = "certificados"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    practica_id = db.Column(db.Integer, db.ForeignKey("practicas.id"), nullable=False)
    qr_valor = db.Column(db.String(64), unique=True, nullable=False)
    qr_url = db.Column(db.String(256), nullable=False)
    hash_integridad = db.Column(db.String(128), nullable=False)
    fecha_emision = db.Column(db.DateTime(timezone=True), nullable=False)
```

---

## 4. Trinity

**Descripción:** Arquitectura de 3 capas donde cada capa tiene una responsabilidad
claramente definida:

- **Controller** (presentación): recibe la solicitud HTTP y serializa la respuesta.
- **ApplicationService** (aplicación): orquesta la lógica de negocio y la persistencia.
- **Repository** (infraestructura): implementa el acceso a datos concretos (SQLAlchemy).

**Fragmento de código:**
```python
# presentation/certificado_controller.py  ─── Capa de presentación
class CertificadoController:
    def issue(self, payload):
        practica_id = payload.get("practica_id")
        certificado = self.certificacion_application_service.issue_certificate(practica_id)
        return self._serialize(certificado), 201
```

```python
# application/certificacion_application_service.py  ─── Capa de aplicación
class CertificacionApplicationService:
    def issue_certificate(self, practica_id):
        practica = self.practica_repository.find_by_id(practica_id)
        practicante = self.perfil_repository.find_practicante_by_user_id(
            practica.practicante_id
        )
        certificado = self.certificacion_servicio.generar_certificado(...)
        return self.certificado_repository.save(certificado)
```

```python
# infrastructure/sqlalchemy_certificado_repository.py  ─── Capa de infraestructura
class SqlAlchemyCertificadoRepository(ICertificadoRepository):
    def save(self, certificado):
        model = CertificadoModel(practica_id=certificado.practica_id)
        db.session.add(model)
        db.session.commit()
        return self._to_domain(model)
```

---

## 5. Restful

**Descripción:** La capa de rutas sigue el estilo arquitectónico REST, aplicando
convenciones HTTP semánticas: cada endpoint representa un recurso identificado por URI,
usa el método HTTP adecuado y devuelve códigos de estado que reflejan el resultado
de la operación.

**Principios aplicados:**

- **Recursos con URI claros:** `/certificados/emitir` y `/certificados/verificar/<codigo>`
  identifican de forma unívoca las operaciones sobre certificados.
- **Métodos HTTP semánticos:** POST para crear un certificado, GET para consultar/verificar.
- **Códigos de respuesta correctos:**
  - `201 Created` — emisión exitosa de certificado
  - `200 OK` — verificación de certificado realizada
  - `400 Bad Request` — parámetros faltantes o inválidos
  - `401 Unauthorized` — usuario no autenticado (sesión expirada o ausente)
- **Serialización JSON:** todas las respuestas se retornan como `jsonify(...)`.
- **Dependencias inyectadas en la ruta:** cada endpoint construye su controller con los
  repositorios concretos necesarios, manteniendo la separación de capas.

**Fragmento de código:**
```python
# frameworks/flask_mvc/routes/certificado_routes.py

@certificado_bp.post("/emitir")
def issue_certificate():
    """POST /certificados/emitir — Crear un certificado digital."""
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401

    payload = request.get_json(silent=True) or {}
    controller = build_certificado_controller()

    try:
        data, status_code = controller.issue(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code


@certificado_bp.get("/verificar/<codigo>")
def verify_certificate(codigo):
    """GET /certificados/verificar/<codigo> — Verificar integridad de un certificado."""
    controller = build_certificado_controller()

    try:
        data, status_code = controller.verify(codigo)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(data), status_code
```

**Tabla de endpoints:**

| Método | Ruta | Descripción | Respuesta exitosa | Errores posibles |
|---|---|---|---|---|
| POST | `/certificados/emitir` | Emitir un certificado digital para una práctica | 201 + JSON con id, qr_url | 400 (falta practica_id), 401 (no autenticado) |
| GET | `/certificados/verificar/<codigo>` | Verificar la integridad de un certificado por código QR | 200 + JSON con estado de validez | 400 (certificado no encontrado) |

---

**Resumen:** Se aplicaron 5 estilos de programación en la implementación de UC-22.

---

## Componentes DDD utilizados

A través de la aplicación de los principios del Diseño Guiado por el Dominio (DDD) y el
estándar PEP 8, se define la estructura de componentes, servicios y repositorios necesarios
para la emisión y verificación de certificados digitales automáticos.

- **Entidad Certificado** (`domain/certificacion/certificado.py`) – encapsula `practica_id`,
  `fecha_emision`, `hash_integridad` e implementa `generar_hash()` y `verificar_integridad()`

- **Servicio de dominio CertificacionDominioServicio**
  (`domain/certificacion/certificacion_dominio_servicio.py`) – orquesta la creación de
  certificado + código QR

- **Interfaz ICertificadoRepository** (`domain/certificacion/i_certificado_repository.py`) –
  define `save()`, `find_by_id()`, `find_by_codigo()`, `find_by_practica_id()`

- **Servicio de aplicación CertificacionApplicationService**
  (`application/certificacion_application_service.py`) – `issue_certificate()` orquesta
  práctica → practicante → certificado con inyección de repositorios

- **Controller + Blueprint** (`presentation/certificado_controller.py` +
  `frameworks/flask_mvc/routes/certificado_routes.py`) – serializa el certificado y expone
  `POST /certificados/emitir` y `GET /certificados/verificar/<codigo>`
