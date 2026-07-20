# Laboratorio 9: Convenciones RF.1 y RF.2

Este documento describe las convenciones de codificación aplicadas sobre los archivos bajo responsabilidad de RF.1 y RF.2.

## RF.1 - Registro y autenticación

Archivos revisados:

```text
application/usuario_application_service.py
domain/auth/autenticacion_dominio_servicio.py
domain/auth/i_usuario_repository.py
domain/auth/token_recuperacion.py
domain/auth/usuario.py
frameworks/flask_mvc/routes/auth_routes.py
frameworks/migrations/versions/734d8ba24491_add_user_activation_and_password_reset_.py
frameworks/sqlalchemy_orm/models/usuario_model.py
infrastructure/sqlalchemy_usuario_repository.py
presentation/usuario_controller.py
```

Práctica: nombres de módulos, clases y métodos siguiendo convenciones Python.

Fragmento:

```python
class UsuarioApplicationService:
    def register_user(self, email, password, tipo):
        self._require_repository()
        normalized_email = self._normalize_email(email)
```

Práctica: separación por capas. La ruta Flask no contiene reglas de negocio; delega en controller, application service y repository.

Fragmento:

```python
def build_usuario_controller():
    repository = SqlAlchemyUsuarioRepository()
    service = UsuarioApplicationService(repository)
    return UsuarioController(service)
```

Práctica: manejo seguro de contraseñas. No se guarda la contraseña en texto plano; se usa hash con Werkzeug.

Fragmento:

```python
def generar_password_hash(self, password):
    if not password:
        raise ValueError("La contraseña es obligatoria")

    return generate_password_hash(password)
```

Práctica: validación temprana de entradas obligatorias.

Fragmento:

```python
def _normalize_email(self, email):
    if not email:
        raise ValueError("El email es obligatorio")

    return email.strip().lower()
```

Práctica: uso de tokens con expiración para activación y recuperación.

Fragmento:

```python
def generar_token(self, horas_vigencia=24):
    expiracion = datetime.now(timezone.utc) + timedelta(hours=horas_vigencia)
    return TokenRecuperacion(token_urlsafe(32), expiracion)
```

Práctica: corrección de code smells detectables por revisión estática/SonarLint. Se eliminaron constructores vacíos que solo contenían `pass`.

Antes:

```python
class SqlAlchemyUsuarioRepository(IUsuarioRepository):
    def __init__(self):
        pass
```

Después:

```python
class SqlAlchemyUsuarioRepository(IUsuarioRepository):
    def save(self, usuario):
        ...
```

## RF.2 - Gestión del perfil del joven

Archivos revisados:

```text
application/perfil_application_service.py
domain/perfil/i_perfil_repository.py
domain/perfil/practicante.py
frameworks/flask_mvc/routes/perfil_routes.py
infrastructure/sqlalchemy_perfil_repository.py
presentation/perfil_controller.py
```

Práctica: entidades de dominio con comportamiento propio. `Practicante` administra sus habilidades, formación, identidad y reputación.

Fragmento:

```python
def agregar_habilidad(self, habilidad):
    habilidad_normalizada = self._normalizar_texto(habilidad)
    if habilidad_normalizada and habilidad_normalizada not in self.habilidades:
        self.habilidades.append(habilidad_normalizada)

    return self
```

Práctica: métodos privados para reutilizar validaciones internas.

Fragmento:

```python
def _require_practicante_user(self, usuario_id):
    usuario = self.usuario_repository.find_by_id(usuario_id)
    if usuario is None:
        raise ValueError("Usuario no encontrado")
```

Práctica: endpoints pequeños y con responsabilidades claras. La ruta valida sesión, lee JSON y delega la operación.

Fragmento:

```python
@perfil_bp.put("/me")
def update_my_profile():
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
```

Práctica: serialización explícita de respuestas para no exponer objetos internos directamente.

Fragmento:

```python
def _serialize_practicante(self, practicante):
    return {
        "id": practicante.id,
        "usuario_id": practicante.usuario_id,
        "nombres": practicante.nombres,
        "apellidos": practicante.apellidos,
        "habilidades": practicante.habilidades,
    }
```

Práctica: corrección de code smells en métodos fuera del alcance de RF.2. En lugar de dejar `pass`, se declara explícitamente que la funcionalidad pertenece a otro RF.

Antes:

```python
def update_empresa(self):
    pass
```

Después:

```python
def update_empresa(self):
    raise NotImplementedError("El perfil de empresa no pertenece a RF.2")
```

## Revisión de calidad

Sobre RF.1 y RF.2 se aplicaron estas acciones:

- Uso de `snake_case` para archivos, funciones y variables.
- Uso de clases en `PascalCase`.
- Separación de responsabilidades por capas.
- Validación temprana de datos obligatorios.
- Uso de hashing para contraseñas.
- Uso de tokens aleatorios con expiración para activación y recuperación.
- Eliminación de constructores vacíos innecesarios.
- Reemplazo de `pass` ambiguos por `NotImplementedError` cuando el método no pertenece al alcance del RF.
- Documentación de endpoints y prácticas aplicadas.
