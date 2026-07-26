# Principios SOLID — UC-13: Notificar Eventos

## 1. SRP — Single Responsibility Principle

**Idea:** Cada clase debe tener una única razón para cambiar.

**Aplicación en UC-13:**

| Clase | Responsabilidad única | Razón de cambio |
|---|---|---|
| `Notificacion` | Estado y comportamiento de dominio | Cambia la regla de negocio de "qué es una notificación" |
| `NotificacionApplicationService` | Orquestar casos de uso | Cambia la secuencia de pasos de un caso de uso |
| `SqlAlchemyNotificacionRepository` | Persistencia en base de datos | Cambia el motor de BD o el ORM |
| `NotificacionController` | Serialización HTTP | Cambia el formato de respuesta JSON |
| `notificacion_routes.py` | Enrutamiento + autenticación | Cambia la URL o el método HTTP |

**Fragmento de código:**

```python
# domain/notificaciones/notificacion.py — Solo dominio
class Notificacion:
    def __init__(self, id=None, usuario_destino_id=None, tipo=None, mensaje=None,
                 metadata=None, leida=False, created_at=None):
        self.id = id
        self.usuario_destino_id = usuario_destino_id
        self.tipo = tipo
        self.mensaje = mensaje
        self.metadata = metadata or {}
        self.leida = leida
        self.created_at = created_at

    def marcar_como_leida(self):
        self.leida = True  # única operación de dominio

# presentation/notificacion_controller.py — Solo HTTP
class NotificacionController:
    def list_notifications(self, usuario_id):
        notificaciones = self.notificacion_application_service.list_notifications(usuario_id)
        return [self._serialize(n) for n in notificaciones], 200

    def _serialize(self, notificacion):
        return {
            "id": notificacion.id,
            "usuario_destino_id": notificacion.usuario_destino_id,
            "tipo": notificacion.tipo,
            "mensaje": notificacion.mensaje,
            "metadata": notificacion.metadata,
            "leida": notificacion.leida,
            "created_at": notificacion.created_at.isoformat() if notificacion.created_at else None,
        }
```

`Notificacion` solo conoce su estado y comportamiento de dominio. `NotificacionController` solo sabe serializar para HTTP. Ninguna mezcla de responsabilidades.

---

## 2. OCP — Open/Closed Principle

**Idea:** Las entidades deben estar abiertas para extensión pero cerradas para modificación.

**Aplicación en UC-13:** Para agregar un nuevo tipo de notificación solo se crea una constante en `Notificacion` y se invoca `create_notification()` desde el hook correspondiente. No es necesario modificar el `ApplicationService`, el `Controller`, el `Repository` ni las `Routes` del módulo de notificaciones.

**Fragmento de código:**

```python
# domain/notificaciones/notificacion.py
class Notificacion:
    TIPO_POSTULACION_SELECCIONADA = "POSTULACION_SELECCIONADA"
    TIPO_EVALUACION_DISPONIBLE = "EVALUACION_DISPONIBLE"
    TIPO_CERTIFICADO_EMITIDO = "CERTIFICADO_EMITIDO"
    TIPO_NUEVAS_SUGERENCIAS = "NUEVAS_SUGERENCIAS"

# application/notificacion_application_service.py
class NotificacionApplicationService:
    def create_notification(self, usuario_destino_id, tipo, mensaje, metadata=None):
        notificacion = Notificacion(
            usuario_destino_id=usuario_destino_id,
            tipo=tipo,              # cualquier string es aceptado — no hay switch/case
            mensaje=mensaje,
            metadata=metadata,
        )
        return self.writer.save(notificacion)
    # Este método nunca cambia al agregar nuevos tipos de notificación.
```

Para extender con un nuevo tipo (ej. `"POSTULACION_RECHAZADA"`), solo se añade el hook:

```python
# en la ruta correspondiente — sin modificar nada del módulo notificaciones
notif_service.create_notification(
    usuario_destino_id=practicante.usuario_id,
    tipo="POSTULACION_RECHAZADA",
    mensaje="Tu postulación ha sido rechazada",
)
```

---

## 3. LSP — Liskov Substitution Principle

**Idea:** Las subclases deben poder sustituir a sus clases base sin alterar el comportamiento del programa.

**Aplicación en UC-13:** `SqlAlchemyNotificacionRepository` implementa tanto `INotificacionWriter` como `INotificacionReader`. El `NotificacionApplicationService` recibe ambas interfaces por separado. El mismo objeto repositorio puede ser usado como writer y como reader sin problemas, demostrando que `SqlAlchemyNotificacionRepository` puede sustituir a cualquiera de las dos interfaces.

**Fragmento de código:**

```python
# infrastructure/sqlalchemy_notificacion_repository.py
class SqlAlchemyNotificacionRepository(INotificacionWriter, INotificacionReader):
    def save(self, notificacion): ...      # implementa INotificacionWriter
    def mark_as_read(self, notificacion_id): ...  # implementa INotificacionWriter
    def find_by_usuario_id(self, usuario_id): ...  # implementa INotificacionReader
    def count_unread(self, usuario_id): ...  # implementa INotificacionReader

# frameworks/flask_mvc/routes/notificacion_routes.py — Sustitución en acción
def build_notificacion_controller():
    repo = SqlAlchemyNotificacionRepository()
    # Misma instancia cumple ambos roles — LSP garantizado
    service = NotificacionApplicationService(writer=repo, reader=repo)
    return NotificacionController(service)
```

Si se creara un `PostgresNotificacionRepository` que también implemente ambas interfaces, podría sustituir a `SqlAlchemyNotificacionRepository` sin cambiar el `ApplicationService` ni el `Controller`.

---

## 4. ISP — Interface Segregation Principle

**Idea:** Los clientes no deben ser forzados a depender de interfaces que no usan.

**Aplicación en UC-13:** En lugar de una interfaz única `INotificacionRepository` con 6 métodos, se separaron dos interfaces especializadas:

- `INotificacionWriter`: solo operaciones de escritura (3 métodos)
- `INotificacionReader`: solo operaciones de lectura (3 métodos)

El `NotificacionApplicationService` recibe ambas por separado. `create_notification()` solo usa `writer`. `list_notifications()` solo usa `reader`. Ningún cliente depende de métodos que no necesita.

**Fragmento de código:**

```python
# domain/notificaciones/i_notificacion_writer.py — Solo escritura
class INotificacionWriter(ABC):
    @abstractmethod
    def save(self, notificacion): ...
    @abstractmethod
    def mark_as_read(self, notificacion_id): ...
    @abstractmethod
    def mark_all_as_read(self, usuario_id): ...

# domain/notificaciones/i_notificacion_reader.py — Solo lectura
class INotificacionReader(ABC):
    @abstractmethod
    def find_by_usuario_id(self, usuario_id): ...
    @abstractmethod
    def find_unread_by_usuario_id(self, usuario_id): ...
    @abstractmethod
    def count_unread(self, usuario_id): ...

# application/notificacion_application_service.py
class NotificacionApplicationService:
    def __init__(self, writer=None, reader=None):
        self.writer = writer    # solo INotificacionWriter
        self.reader = reader    # solo INotificacionReader

    def create_notification(self, ...):
        self._require_writer()
        return self.writer.save(notificacion)  # solo usa writer

    def list_notifications(self, usuario_id):
        self._require_reader()
        return self.reader.find_by_usuario_id(usuario_id)  # solo usa reader
```

---

## 5. DIP — Dependency Inversion Principle

**Idea:** Los módulos de alto nivel no deben depender de módulos de bajo nivel. Ambos deben depender de abstracciones.

**Aplicación en UC-13:** `NotificacionApplicationService` (alto nivel) depende de `INotificacionWriter` e `INotificacionReader` (abstracciones en la capa de dominio). `SqlAlchemyNotificacionRepository` (bajo nivel) también depende de esas mismas abstracciones al implementarlas. La inyección de dependencias ocurre en las rutas, que construyen el repositorio concreto y lo pasan como abstracción.

**Fragmento de código:**

```python
# domain/notificaciones/i_notificacion_writer.py — Abstracción (capa de dominio)
class INotificacionWriter(ABC):
    @abstractmethod
    def save(self, notificacion): ...

# application/notificacion_application_service.py — Alto nivel
class NotificacionApplicationService:
    def __init__(self, writer=None, reader=None):
        self.writer = writer  # Depende de abstracción, no de concreción
        self.reader = reader

    def create_notification(self, usuario_destino_id, tipo, mensaje, metadata=None):
        self._require_writer()
        notificacion = Notificacion(...)
        return self.writer.save(notificacion)  # No sabe si es SQLAlchemy, Postgres, etc.

# infrastructure/sqlalchemy_notificacion_repository.py — Bajo nivel
class SqlAlchemyNotificacionRepository(INotificacionWriter, INotificacionReader):
    def save(self, notificacion):
        # Implementación concreta con SQLAlchemy
        model = NotificacionModel(...)
        db.session.add(model)
        db.session.commit()
        return self._to_domain(model)

# frameworks/flask_mvc/routes/notificacion_routes.py — Punto de inyección
def build_notificacion_controller():
    repo = SqlAlchemyNotificacionRepository()                     # concreción
    service = NotificacionApplicationService(writer=repo, reader=repo)  # inyectada como abstracción
    return NotificacionController(service)
```

La flecha de dependencia apunta hacia adentro (hacia el dominio) tanto desde la aplicación como desde la infraestructura. Invertir la dependencia permite cambiar de SQLite a PostgreSQL sin tocar el `ApplicationService`.
