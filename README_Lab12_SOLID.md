# 🔧 Laboratorio 12 – SOLID

**ChambeaYa - Principios SOLID Aplicados**

---

## 📋 Objetivo

Aplicar los principios SOLID para que el software sea más fácil de escalar y mantener.

---

## 📂 Archivos Modificados en este Laboratorio

| Archivo | Principios Aplicados | Cambio Principal |
|---------|----------------------|-------------------|
| `application/matching_application_service.py` | S, D | Separar responsabilidades, depender de interfaces |
| `application/postulacion_application_service.py` | S, D | Separar responsabilidades, depender de interfaces |
| `presentation/matching_controller.py` | S | Solo manejo de HTTP |
| `domain/practica_evaluacion/evaluacion.py` | O | Clase base abstracta, herencia para nuevos tipos |
| `domain/perfil/practicante.py` | L | Sustitución correcta de clase padre |
| `domain/perfil/empresa.py` | L | Sustitución correcta de clase padre |
| `domain/convocatorias/i_convocatoria_repository.py` | I | Interfaces segregadas (Lectura/Escritura) |
| `domain/auth/i_usuario_repository.py` | I | Interfaces segregadas (Lectura/Escritura) |
| `frameworks/flask_mvc/app.py` | D | Inyección de dependencias con interfaces |

---

## 📌 Principios Aplicados

### 1. Single Responsibility (Responsabilidad Única) + Dependency Inversion (Inversión de Dependencias)

**Archivo:** `application/matching_application_service.py`

```python
# application/matching_application_service.py
# LAB 12 - SOLID: S (Responsabilidad Única) y D (Inversión de Dependencias)

from typing import List, Dict, Optional
from domain.matching.sugerencia import Sugerencia
from domain.matching.i_sugerencia_repository import ISugerenciaRepository
from domain.perfil.i_perfil_repository import IPerfilRepository
from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository
from domain.matching.matching_dominio_servicio import MatchingDominioServicio


class MatchingApplicationService:
    """
    LAB 12 - SRP: Esta clase tiene la ÚNICA responsabilidad de orquestar el proceso de matching.
    No se encarga de persistencia (lo hace SugerenciaRepository) ni de notificaciones.

    LAB 12 - DIP: Depende de ABSTRACCIONES (interfaces), no de implementaciones concretas.
    """

    def __init__(
        self,
        sugerencia_repo: ISugerenciaRepository,  # DIP: Dependencia de interfaz
        perfil_repo: IPerfilRepository,          # DIP: Dependencia de interfaz
        convocatoria_repo: IConvocatoriaRepository  # DIP: Dependencia de interfaz
    ):
        self.sugerencia_repo = sugerencia_repo
        self.perfil_repo = perfil_repo
        self.convocatoria_repo = convocatoria_repo
        self.matching_servicio = MatchingDominioServicio()

    def recomendar_convocatorias(self, practicante_id: int, limit: int = 10) -> List[Dict]:
        """
        Orquesta el proceso de recomendación.
        """
        # 1. Obtener perfil
        perfil = self.perfil_repo.obtener_por_usuario_id(practicante_id)
        if not perfil or not perfil.habilidades:
            return []

        # 2. Obtener convocatorias activas
        convocatorias = self.convocatoria_repo.listar_activas()
        if not convocatorias:
            return []

        # 3. Generar sugerencias (delegado al servicio de dominio)
        sugerencias = self.matching_servicio.generar_sugerencias(
            practicante_id=practicante_id,
            habilidades_practicante=perfil.habilidades,
            convocatorias=convocatorias
        )

        # 4. Guardar sugerencias (responsabilidad del repositorio)
        self.sugerencia_repo.eliminar_por_practicante(practicante_id)
        sugerencias_guardadas = self.sugerencia_repo.guardar_multiples(sugerencias[:limit])

        # 5. Formatear respuesta
        return self._formatear_resultado(sugerencias_guardadas, convocatorias)

    def _formatear_resultado(self, sugerencias: List[Sugerencia], convocatorias: List) -> List[Dict]:
        """Formatea las sugerencias para la respuesta API."""
        resultado = []
        for sug in sugerencias:
            conv = next((c for c in convocatorias if c.id == sug.convocatoria_id), None)
            if conv:
                resultado.append({
                    "convocatoria": conv.to_dict(),
                    "score_match": sug.score_match,
                    "habilidades_match": sug.habilidades_match
                })
        return resultado
```

**Archivo:** `application/postulacion_application_service.py`

```python
# application/postulacion_application_service.py
# LAB 12 - SOLID: S (Responsabilidad Única) y D (Inversión de Dependencias)

from typing import List, Dict, Optional
from datetime import datetime
from domain.convocatorias.postulacion import Postulacion
from domain.convocatorias.i_postulacion_repository import IPostulacionRepository
from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository
from domain.perfil.i_perfil_repository import IPerfilRepository


class PostulacionApplicationService:
    """
    LAB 12 - SRP: Esta clase tiene la ÚNICA responsabilidad de gestionar postulaciones.
    No contiene lógica de validación compleja (delegada al dominio) ni de persistencia directa.

    LAB 12 - DIP: Depende de ABSTRACCIONES (interfaces), no de implementaciones concretas.
    """

    def __init__(
        self,
        postulacion_repo: IPostulacionRepository,  # DIP: Dependencia de interfaz
        convocatoria_repo: IConvocatoriaRepository,  # DIP: Dependencia de interfaz
        perfil_repo: IPerfilRepository  # DIP: Dependencia de interfaz
    ):
        self.postulacion_repo = postulacion_repo
        self.convocatoria_repo = convocatoria_repo
        self.perfil_repo = perfil_repo

    def postularse(
        self,
        practicante_id: int,
        convocatoria_id: int,
        mensaje: str = "",
        archivos: List[str] = None
    ) -> Dict:
        """
        Crea una nueva postulación.
        """
        # 1. Validar que exista el perfil
        perfil = self.perfil_repo.obtener_por_usuario_id(practicante_id)
        if not perfil:
            raise ValueError("El practicante no tiene un perfil completo")

        # 2. Validar convocatoria (delegado al dominio)
        convocatoria = self.convocatoria_repo.obtener_por_id(convocatoria_id)
        if not convocatoria:
            raise ValueError("Convocatoria no encontrada")
        if not convocatoria.esta_activa():
            raise ValueError("La convocatoria no está activa")

        # 3. Validar postulación duplicada
        existente = self.postulacion_repo.obtener_por_practicante_y_convocatoria(
            practicante_id, convocatoria_id
        )
        if existente:
            raise ValueError("Ya existe una postulación para esta convocatoria")

        # 4. Crear postulación (entidad de dominio)
        postulacion = Postulacion(
            id=None,
            convocatoria_id=convocatoria_id,
            practicante_id=practicante_id,
            fecha_postulacion=datetime.utcnow(),
            estado='pendiente',
            mensaje_postulacion=mensaje,
            archivos_adjuntos=archivos or []
        )

        # 5. Guardar (responsabilidad del repositorio)
        guardada = self.postulacion_repo.guardar(postulacion)
        return guardada.to_dict()

    def obtener_postulaciones_practicante(self, practicante_id: int) -> List[Dict]:
        """Obtiene todas las postulaciones de un practicante."""
        postulaciones = self.postulacion_repo.obtener_por_practicante(practicante_id)
        return [p.to_dict() for p in postulaciones]

    def actualizar_estado(self, postulacion_id: int, nuevo_estado: str, usuario_rol: str = "empresa") -> Dict:
        """Actualiza el estado de una postulación."""
        if usuario_rol != "empresa":
            raise PermissionError("Solo las empresas pueden cambiar el estado de postulaciones")

        estados_validos = ['pendiente', 'aceptada', 'rechazada', 'completada']
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado inválido. Debe ser uno de: {estados_validos}")

        postulacion = self.postulacion_repo.obtener_por_id(postulacion_id)
        if not postulacion:
            raise ValueError("Postulación no encontrada")

        # La lógica de cambio de estado está en la entidad (dominio)
        if nuevo_estado == 'aceptada':
            postulacion.aceptar()
        elif nuevo_estado == 'rechazada':
            postulacion.rechazar()
        elif nuevo_estado == 'completada':
            postulacion.completar()

        actualizada = self.postulacion_repo.actualizar_estado(postulacion_id, nuevo_estado)
        return actualizada.to_dict()
```

### 2. Single Responsibility (Responsabilidad Única) en la capa de presentación

**Archivo:** `presentation/matching_controller.py`

```python
# presentation/matching_controller.py
# LAB 12 - SOLID: S (Responsabilidad Única)
# El controlador SOLO maneja peticiones HTTP. No contiene lógica de negocio.

from flask import Blueprint, request, jsonify, session
from application.matching_application_service import MatchingApplicationService
from infrastructure.sqlalchemy_sugerencia_repository import SQLAlchemySugerenciaRepository
from infrastructure.sqlalchemy_perfil_repository import SQLAlchemyPerfilRepository
from infrastructure.sqlalchemy_convocatoria_repository import SQLAlchemyConvocatoriaRepository
from frameworks.sqlalchemy_orm.database import db

matching_blueprint = Blueprint('matching', __name__, url_prefix='/matching')

# Inyección de dependencias (DIP aplicado en el servicio)
sugerencia_repo = SQLAlchemySugerenciaRepository(db.session)
perfil_repo = SQLAlchemyPerfilRepository(db.session)
convocatoria_repo = SQLAlchemyConvocatoriaRepository(db.session)

matching_service = MatchingApplicationService(
    sugerencia_repo=sugerencia_repo,
    perfil_repo=perfil_repo,
    convocatoria_repo=convocatoria_repo
)


@matching_blueprint.route('/recomendaciones', methods=['GET'])
def recomendar_convocatorias():
    """
    SRP: Este controlador SOLO maneja la petición HTTP.
    Obtiene el usuario, llama al servicio y devuelve la respuesta.
    """
    try:
        # 1. Obtener usuario autenticado
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "No autenticado"}), 401

        # 2. Obtener parámetros
        limit = request.args.get('limit', 10, type=int)
        if limit > 50:
            limit = 50

        # 3. Llamar al servicio (toda la lógica está ahí)
        recomendaciones = matching_service.recomendar_convocatorias(usuario_id, limit)

        # 4. Devolver respuesta
        return jsonify({
            "data": recomendaciones,
            "total": len(recomendaciones)
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
```

### 3. Open/Closed (Abierto/Cerrado)

**Archivo:** `domain/practica_evaluacion/evaluacion.py`

```python
# domain/practica_evaluacion/evaluacion.py
# LAB 12 - SOLID: O (Abierto/Cerrado)
# La clase base está abierta para extensión (herencia) pero cerrada para modificación.

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


@dataclass
class Evaluacion(ABC):
    """
    Clase base abstracta para evaluaciones.
    Está ABIERTA para extensión (puedes crear nuevas subclases) pero
    CERRADA para modificación (no debes cambiar esta clase base).
    """
    id: Optional[int]
    entregable_id: int
    puntaje: float
    comentario: str
    fecha_evaluacion: Optional[datetime] = None

    def __post_init__(self):
        if self.fecha_evaluacion is None:
            self.fecha_evaluacion = datetime.utcnow()

    @abstractmethod
    def es_aprobatoria(self) -> bool:
        """
        Método abstracto que las subclases deben implementar.
        Permite diferentes criterios de aprobación según el tipo de evaluación.
        """
        pass

    @abstractmethod
    def obtener_puntaje_normalizado(self) -> float:
        """
        Método abstracto para normalizar puntajes según diferentes escalas.
        """
        pass

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "entregable_id": self.entregable_id,
            "puntaje": self.puntaje,
            "comentario": self.comentario,
            "fecha_evaluacion": self.fecha_evaluacion.isoformat() if self.fecha_evaluacion else None
        }


# Ejemplo de extensión (nueva subclase)
@dataclass
class EvaluacionTecnica(Evaluacion):
    """
    Subclase que extiende Evaluacion para evaluaciones técnicas.
    No modifica la clase base, solo la extiende.
    """
    criterios_tecnicos: List[str] = None

    def es_aprobatoria(self) -> bool:
        # Criterio de aprobación: puntaje >= 4.0
        return self.puntaje >= 4.0

    def obtener_puntaje_normalizado(self) -> float:
        # Normaliza a escala 0-1
        return self.puntaje / 5.0


@dataclass
class EvaluacionFinal(Evaluacion):
    """
    Subclase que extiende Evaluacion para evaluaciones finales de práctica.
    """
    def es_aprobatoria(self) -> bool:
        # Criterio de aprobación: puntaje >= 3.5
        return self.puntaje >= 3.5

    def obtener_puntaje_normalizado(self) -> float:
        # Normaliza a escala 0-100
        return self.puntaje * 20
```

### 4. Liskov Substitution (Sustitución de Liskov)

**Archivo:** `domain/perfil/practicante.py`

```python
# domain/perfil/practicante.py
# LAB 12 - SOLID: L (Sustitución de Liskov)
# Esta subclase puede sustituir a la clase padre sin alterar el comportamiento esperado.

from dataclasses import dataclass
from typing import Optional, List
from domain.perfil.usuario_base import UsuarioBase  # Suponiendo una clase padre


@dataclass
class Practicante(UsuarioBase):
    """
    Subclase que cumple con LSP: puede sustituir a UsuarioBase sin problemas.
    """
    habilidades: List[str]
    formacion_educativa: List[str]
    carnet_universitario: str
    dni: str

    def obtener_rol(self) -> str:
        """Sobrescribe el método de la clase padre."""
        return "practicante"

    def esta_verificado(self) -> bool:
        """Implementa un comportamiento específico pero consistente con la interfaz."""
        return bool(self.dni) and bool(self.carnet_universitario)

    def obtener_identificador(self) -> str:
        """Retorna el identificador del usuario (dni)."""
        return self.dni
```

**Archivo:** `domain/perfil/empresa.py`

```python
# domain/perfil/empresa.py
# LAB 12 - SOLID: L (Sustitución de Liskov)
# Esta subclase puede sustituir a la clase padre sin alterar el comportamiento esperado.

from dataclasses import dataclass
from typing import Optional
from domain.perfil.usuario_base import UsuarioBase  # Suponiendo una clase padre


@dataclass
class Empresa(UsuarioBase):
    """
    Subclase que cumple con LSP: puede sustituir a UsuarioBase sin problemas.
    """
    razon_social: str
    ruc: str
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None

    def obtener_rol(self) -> str:
        """Sobrescribe el método de la clase padre."""
        return "empresa"

    def esta_verificado(self) -> bool:
        """Implementa un comportamiento específico pero consistente con la interfaz."""
        return bool(self.ruc) and len(self.ruc) == 11

    def obtener_identificador(self) -> str:
        """Retorna el identificador de la empresa (ruc)."""
        return self.ruc
```

### 5. Interface Segregation (Segregación de Interfaces)

**Archivo:** `domain/convocatorias/i_convocatoria_repository.py`

```python
# domain/convocatorias/i_convocatoria_repository.py
# LAB 12 - SOLID: I (Segregación de Interfaces)
# La interfaz grande se divide en interfaces más pequeñas y específicas.

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.convocatorias.convocatoria import Convocatoria


class IConvocatoriaRepositoryLectura(ABC):
    """Interfaz específica para operaciones de lectura."""

    @abstractmethod
    def obtener_por_id(self, convocatoria_id: int) -> Optional[Convocatoria]:
        pass

    @abstractmethod
    def listar_activas(self) -> List[Convocatoria]:
        pass

    @abstractmethod
    def listar_por_empresa(self, empresa_id: int) -> List[Convocatoria]:
        pass


class IConvocatoriaRepositoryEscritura(ABC):
    """Interfaz específica para operaciones de escritura."""

    @abstractmethod
    def guardar(self, convocatoria: Convocatoria) -> Convocatoria:
        pass

    @abstractmethod
    def actualizar(self, convocatoria: Convocatoria) -> Convocatoria:
        pass

    @abstractmethod
    def eliminar(self, convocatoria_id: int) -> bool:
        pass


# La interfaz principal extiende las dos interfaces específicas
class IConvocatoriaRepository(IConvocatoriaRepositoryLectura, IConvocatoriaRepositoryEscritura):
    """
    Interfaz completa que hereda de las interfaces segregadas.
    Las clases que implementen esta interfaz deben cumplir con todos los métodos.
    """
    pass
```

**Archivo:** `domain/auth/i_usuario_repository.py`

```python
# domain/auth/i_usuario_repository.py
# LAB 12 - SOLID: I (Segregación de Interfaces)

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.auth.usuario import Usuario


class IUsuarioRepositoryLectura(ABC):
    """Interfaz específica para operaciones de lectura de usuarios."""

    @abstractmethod
    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def obtener_por_rol(self, rol: str) -> List[Usuario]:
        pass


class IUsuarioRepositoryEscritura(ABC):
    """Interfaz específica para operaciones de escritura de usuarios."""

    @abstractmethod
    def guardar(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def actualizar(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def activar(self, usuario_id: int) -> Usuario:
        pass

    @abstractmethod
    def desactivar(self, usuario_id: int) -> Usuario:
        pass


class IUsuarioRepository(IUsuarioRepositoryLectura, IUsuarioRepositoryEscritura):
    """
    Interfaz completa que hereda de las interfaces segregadas.
    """
    pass
```

### 6. Dependency Inversion (Inversión de Dependencias)

**Archivo:** `frameworks/flask_mvc/app.py`

```python
# frameworks/flask_mvc/app.py
# LAB 12 - SOLID: D (Inversión de Dependencias)
# Los módulos de alto nivel dependen de abstracciones, no de implementaciones concretas.

from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from frameworks.sqlalchemy_orm.database import db
from infrastructure.sqlalchemy_usuario_repository import SQLAlchemyUsuarioRepository
from infrastructure.sqlalchemy_perfil_repository import SQLAlchemyPerfilRepository
from infrastructure.sqlalchemy_convocatoria_repository import SQLAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_postulacion_repository import SQLAlchemyPostulacionRepository
from application.usuario_application_service import UsuarioApplicationService
from application.matching_application_service import MatchingApplicationService
from presentation.matching_controller import matching_blueprint
from presentation.postulacion_controller import postulacion_blueprint
# ... otros imports


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chambeaya.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'

    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    # ============================================
    # LAB 12 - DIP: Inyección de Dependencias
    # Los servicios reciben interfaces (abstracciones),
    # no implementaciones concretas.
    # ============================================

    # Repositorios concretos (implementaciones)
    usuario_repo = SQLAlchemyUsuarioRepository(db.session)
    perfil_repo = SQLAlchemyPerfilRepository(db.session)
    convocatoria_repo = SQLAlchemyConvocatoriaRepository(db.session)
    postulacion_repo = SQLAlchemyPostulacionRepository(db.session)

    # Servicios de aplicación (dependen de interfaces)
    usuario_service = UsuarioApplicationService(usuario_repo)
    matching_service = MatchingApplicationService(
        sugerencia_repo=SugerenciaRepository(db.session),  # Inyección
        perfil_repo=perfil_repo,
        convocatoria_repo=convocatoria_repo
    )

    # Controladores (reciben servicios)
    app.register_blueprint(matching_blueprint)
    app.register_blueprint(postulacion_blueprint)
    # ... otros blueprints

    return app
```

---

## 📊 Resumen de Principios Aplicados

| Principio | Descripción | Ejemplo |
|-----------|-------------|---------|
| SRP | Una clase, una responsabilidad | `MatchingApplicationService`, `PostulacionApplicationService`, `matching_controller.py` |
| OCP | Abierto para extensión, cerrado para modificación | `Evaluacion` (base) → `EvaluacionTecnica`, `EvaluacionFinal` |
| LSP | Sustitución de clases base | `Practicante` y `Empresa` heredan de `UsuarioBase` |
| ISP | Interfaces específicas | `IConvocatoriaRepositoryLectura/Escritura`, `IUsuarioRepositoryLectura/Escritura` |
| DIP | Depender de abstracciones | Servicios de aplicación reciben interfaces inyectadas desde `frameworks/flask_mvc/app.py` |

📅 Fecha: Julio 2026
