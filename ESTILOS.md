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

**Descripción:** API REST con endpoints que usan métodos HTTP semánticos (POST para crear
recursos, GET para consultarlos) y códigos de respuesta apropiados (201, 400, 401).

**Fragmento de código:**
```python
# frameworks/flask_mvc/routes/certificado_routes.py
@certificado_bp.post("/emitir")
def issue_certificate():
    """POST /certificados/emitir — Crear un certificado digital."""
    ...

@certificado_bp.get("/verificar/<codigo>")
def verify_certificate(codigo):
    """GET /certificados/verificar/<codigo> — Verificar integridad de un certificado."""
    ...
```

---

**Resumen:** Se aplicaron 5 estilos de programación en la implementación de UC-22.
