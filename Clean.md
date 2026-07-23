# Prácticas de Codificación Legible — ChambeaYa (UC-12 / UC-22)

## 1. Nombres

**Práctica:** Usar nombres descriptivos que comuniquen la intención del código sin
requerir comentarios adicionales.

**Fragmento de código (UC-22):**

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

**Fragmento de código (UC-12):**

```python
# domain/matching/sugerencia.py
class Sugerencia:
    def __init__(self, id=None, practicante_id=None, convocatoria_id=None,
                 puntaje_match=None, habilidades_coincidentes=None):
        self.id = id
        self.practicante_id = practicante_id
        self.convocatoria_id = convocatoria_id
        self.puntaje_match = puntaje_match or 0.0
        self.habilidades_coincidentes = habilidades_coincidentes or []

    def calcular_compatibilidad(self, habilidades_practicante, habilidades_requeridas):
        if not habilidades_requeridas:
            self.puntaje_match = 0.0
            return self.puntaje_match

        set_practicante = set(h for h in habilidades_practicante if h)
        set_requeridas = set(h for h in habilidades_requeridas if h)
        coincidentes = set_practicante & set_requeridas

        self.habilidades_coincidentes = list(coincidentes)
        self.puntaje_match = len(coincidentes) / len(set_requeridas) * 100
        return self.puntaje_match
```

---

## 2. Funciones

**Práctica:** Funciones pequeñas con una sola responsabilidad, extraídas para
reutilización y legibilidad.

**Fragmento de código (UC-22):**

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

**Fragmento de código (UC-12):**

```python
# presentation/matching_controller.py
class MatchingController:
    def suggest_convocatorias(self, usuario_id):
        self._require_service()
        resultados = self.matching_application_service.suggest_convocatorias(usuario_id)
        return [self._serialize_resultado(r) for r in resultados], 200

    def _serialize_resultado(self, resultado):
        return {
            "practicante_id": resultado.practicante_id,
            "convocatoria_id": resultado.convocatoria_id,
            "score_compatibilidad": round(resultado.score_compatibilidad, 2),
            "es_compatible": resultado.es_compatible(),
        }
```

---

## 3. Comentarios

**Práctica:** Docstrings en endpoints REST que describen el método HTTP y la
operación que realiza.

**Fragmento de código (UC-22):**

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

**Fragmento de código (UC-12):**

```python
# frameworks/flask_mvc/routes/matching_routes.py
@matching_bp.get("/sugerencias")
def suggest_convocatorias():
    """GET /matching/sugerencias — Obtener convocatorias sugeridas para el practicante."""
    ...

@matching_bp.post("/calcular")
def calculate_match():
    """POST /matching/calcular — Calcular y guardar matching para el practicante."""
    ...
```

---

## 4. Estructura de Código Fuente

**Práctica:** Imports organizados por capa arquitectónica en orden de dependencia:
domain → application → infrastructure → presentation → routes.

**Fragmento de código (UC-22):**

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

**Fragmento de código (UC-12):**

```python
# frameworks/flask_mvc/routes/matching_routes.py
from flask import Blueprint, jsonify, session

from application.matching_application_service import MatchingApplicationService
from domain.matching.matching_dominio_servicio import MatchingDominioServicio
from infrastructure.sqlalchemy_matching_repository import SqlAlchemyMatchingRepository
from infrastructure.sqlalchemy_perfil_repository import SqlAlchemyPerfilRepository
from infrastructure.sqlalchemy_convocatoria_repository import SqlAlchemyConvocatoriaRepository
from presentation.matching_controller import MatchingController
```

---

## 5. Objetos/Estructura de Datos

**Práctica:** Entidades con comportamiento propio (no solo contenedores de datos).

**Fragmento de código (UC-22):**

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

**Fragmento de código (UC-12):**

```python
# domain/matching/resultado_matching.py
class ResultadoMatching:
    def __init__(self, score_compatibilidad=0.0, practicante_id=None,
                 convocatoria_id=None, sugerencia=None):
        self.score_compatibilidad = score_compatibilidad
        self.practicante_id = practicante_id
        self.convocatoria_id = convocatoria_id
        self.sugerencia = sugerencia

    def es_compatible(self, umbral=50.0):
        return self.score_compatibilidad >= umbral
```

---

## 6. Tratamiento de Errores

**Práctica:** Excepciones de dominio + guard clauses + mapeo a códigos HTTP.

**Fragmento de código (UC-22):**

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

**Fragmento de código (UC-12):**

```python
# application/matching_application_service.py
def suggest_convocatorias(self, usuario_id, umbral=50.0):
    self._require_repositories()

    practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
    if practicante is None:
        raise ValueError("Practicante no encontrado")

    convocatorias = self.convocatoria_repository.find_all()
    return self.matching_servicio.filtrar_convocatorias(practicante, convocatorias, umbral)

def _require_repositories(self):
    if self.sugerencia_repository is None:
        raise RuntimeError("MatchingApplicationService requiere un repositorio de sugerencias")
    if self.perfil_repository is None:
        raise RuntimeError("MatchingApplicationService requiere un repositorio de perfil")
    if self.convocatoria_repository is None:
        raise RuntimeError("MatchingApplicationService requiere un repositorio de convocatorias")
```

---

## 7. Clases

**Práctica:** Interface Segregation (ISP) — interfaces pequeñas y específicas para
cada repositorio.

**Fragmento de código (UC-22):**

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

**Fragmento de código (UC-12):**

```python
# domain/matching/i_sugerencia_repository.py
class ISugerenciaRepository(ABC):
    @abstractmethod
    def save(self, sugerencia):
        pass

    @abstractmethod
    def find_by_practicante_id(self, practicante_id):
        pass
```

---

**Resumen:** Se aplicaron 7 categorías de Clean Code en las implementaciones de UC-22 y UC-12.

---

## Componentes DDD utilizados (UC-12)

- `domain/matching/sugerencia.py` — Entidad Sugerencia con `calcular_compatibilidad()`
- `domain/matching/resultado_matching.py` — Value Object ResultadoMatching con `es_compatible()`
- `domain/matching/matching_dominio_servicio.py` — Servicio de dominio con `calcular_match()` y `filtrar_convocatorias()`
- `domain/matching/i_sugerencia_repository.py` — Interfaz ISugerenciaRepository (`save`, `find_by_practicante_id`)
- `application/matching_application_service.py` — Servicio de aplicación con `suggest_convocatorias()` y `calculate_for_practicante()`
- `presentation/matching_controller.py` — Controller con serialización de resultados
- `frameworks/flask_mvc/routes/matching_routes.py` — Blueprint `GET /matching/sugerencias` y `POST /matching/calcular`
- `infrastructure/sqlalchemy_matching_repository.py` — Repositorio concreto (mapeo SugerenciaModel ↔ Sugerencia)
- `frameworks/sqlalchemy_orm/models/sugerencia_model.py` — Modelo ORM tabla `sugerencias`
