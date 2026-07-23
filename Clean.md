# Prácticas de Codificación Legible — ChambeaYa (UC-22)

## 1. Nombres

**Práctica:** Usar nombres descriptivos que comuniquen la intención del código sin
requerir comentarios adicionales.

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

## 2. Funciones

**Práctica:** Funciones pequeñas con una sola responsabilidad, extraídas para
reutilización y legibilidad.

**Fragmento de código:**

```python
# presentation/certificado_controller.py
class CertificadoController:
    def issue(self, payload):
        self._require_service()
        practica_id = payload.get("practica_id")

        if not practica_id:
            return {"error": "practica_id es requerido"}, 400

        certificado = self.certificacion_application_service.issue_certificate(practica_id)
        return self._serialize(certificado), 201

    def _serialize(self, certificado):
        return {
            "id": certificado.id,
            "practica_id": certificado.practica_id,
            "fecha_emision": certificado.fecha_emision.isoformat(),
            "qr_valor": certificado.codigo_qr.valor,
            "qr_url": certificado.codigo_qr.url_verificacion,
        }
```

---

## 3. Comentarios

**Práctica:** Docstrings en endpoints REST que describen el método HTTP y la
operación que realiza.

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

---

## 4. Estructura de Código Fuente

**Práctica:** Imports organizados por capa arquitectónica en orden de dependencia:
domain → application → infrastructure → presentation → routes.

**Fragmento de código:**

```python
# frameworks/flask_mvc/routes/certificado_routes.py
from flask import Blueprint, jsonify, request, session

from application.certificacion_application_service import CertificacionApplicationService
from domain.certificacion.certificacion_dominio_servicio import CertificacionDominioServicio
from infrastructure.sqlalchemy_certificado_repository import SqlAlchemyCertificadoRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from infrastructure.sqlalchemy_practica_repository import SqlAlchemyPracticaRepository
from presentation.certificado_controller import CertificadoController
```

---

## 5. Objetos/Estructura de Datos

**Práctica:** Value Objects con comportamiento propio (no solo contenedores de datos).

**Fragmento de código:**

```python
# domain/certificacion/codigo_qr.py
class CodigoQR:
    def __init__(self, valor=None, url_verificacion=None, hash_integridad=None):
        self.valor = valor
        self.url_verificacion = url_verificacion
        self.hash_integridad = hash_integridad

    def generar(self, _certificado_id, base_url="http://localhost:5000"):
        self.valor = secrets.token_urlsafe(16)
        self.url_verificacion = f"{base_url}/certificados/verificar/{self.valor}"
        self.hash_integridad = hashlib.sha256(self.valor.encode()).hexdigest()
        return self

    def verificar(self):
        if not self.valor or not self.hash_integridad:
            return False

        return hashlib.sha256(self.valor.encode()).hexdigest() == self.hash_integridad
```

---

## 6. Tratamiento de Errores

**Práctica:** Excepciones de dominio + guard clauses + mapeo a códigos HTTP.

**Fragmento de código:**

```python
# application/certificacion_application_service.py
def issue_certificate(self, practica_id, base_url="http://localhost:5000"):
    self._require_repositories()

    practica = self.practica_repository.find_by_id(practica_id)
    if practica is None:
        raise ValueError("Práctica no encontrada")

    practicante = self.perfil_repository.find_practicante_by_user_id(
        practica.practicante_id
    )
    if practicante is None:
        raise ValueError("Practicante no encontrado")
```

```python
# frameworks/flask_mvc/routes/certificado_routes.py
try:
    data, status_code = controller.issue(payload)
except ValueError as exc:
    return jsonify({"error": str(exc)}), 400
```

---

## 7. Clases

**Práctica:** Interface Segregation (ISP) — interfaces pequeñas y específicas para
cada repositorio.

**Fragmento de código:**

```python
# domain/certificacion/i_certificado_repository.py
class ICertificadoRepository(ABC):
    @abstractmethod
    def save(self, certificado):
        pass

    @abstractmethod
    def find_by_id(self, certificado_id):
        pass

    @abstractmethod
    def find_by_codigo(self, codigo):
        pass

    @abstractmethod
    def find_by_practica_id(self, practica_id):
        pass
```

---

**Resumen:** Se aplicaron 7 categorías de Clean Code en la implementación de UC-22.
