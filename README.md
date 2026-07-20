# ChambeaYa

Plataforma web para la gestión de prácticas preprofesionales, conectando estudiantes y empresas mediante postulaciones, seguimiento de procesos, recomendaciones basadas en habilidades y certificación digital de prácticas.

## Estructura del proyecto

```bash
ChambeaYa/
├── config.py
├── requirements.txt
├── run.py
├── application/
│   ├── __init__.py
│   ├── certificacion_application_service.py
│   ├── convocatoria_application_service.py
│   ├── matching_application_service.py
│   ├── perfil_application_service.py
│   ├── postulacion_application_service.py
│   ├── practica_application_service.py
│   └── usuario_application_service.py
├── domain/
│   ├── __init__.py
│   ├── auth/
│   ├── certificacion/
│   ├── convocatorias/
│   ├── matching/
│   ├── perfil/
│   └── practica_evaluacion/
├── frameworks/
│   ├── __init__.py
│   ├── flask_mvc/
│   │   ├── app.py
│   │   ├── routes/
│   │   ├── static/
│   │   └── templates/
│   ├── migrations/
│   ├── schemas/
│   └── sqlalchemy_orm/
│       ├── database.py
│       └── models/
├── infrastructure/
│   ├── __init__.py
│   ├── sqlalchemy_certificado_repository.py
│   ├── sqlalchemy_convocatoria_repository.py
│   ├── sqlalchemy_perfil_repository.py
│   ├── sqlalchemy_postulacion_repository.py
│   ├── sqlalchemy_practica_repository.py
│   ├── sqlalchemy_sugerencia_repository.py
│   └── sqlalchemy_usuario_repository.py
└── presentation/
    ├── __init__.py
    ├── certificado_controller.py
    ├── convocatoria_controller.py
    ├── matching_controller.py
    ├── perfil_controller.py
    ├── postulacion_controller.py
    ├── practica_controller.py
    └── usuario_controller.py
```

## Capas del sistema


- **domain**: entidades y reglas del negocio.
- **application**: servicios de aplicación.
- **infrastructure**: repositorios e integración con persistencia.
- **presentation**: controladores de la capa de exposición.
- **frameworks**: componentes técnicos como Flask, SQLAlchemy y migraciones.

<img width="3333" height="1812" alt="ChambeaYa - Arquitectura en Capas Flask UML" src="https://github.com/user-attachments/assets/8378e75e-f5ca-4be1-8506-cad06f7e2aed" />


## Tecnologías

- Python
- Flask
- SQLAlchemy
- Flask-Migrate

## Ejecución local

Crear y activar entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Configurar variables de entorno:

```bash
cp .env.example .env
```

Levantar la aplicación:

```bash
flask --app frameworks.flask_mvc.app:create_app run --debug
```

Verificar que la app responde:

```bash
curl http://127.0.0.1:5000/health
```

## Migraciones

El entorno de migraciones ya está inicializado en `frameworks/migrations`.

Crear una nueva migración después de modificar modelos:

```bash
flask --app frameworks.flask_mvc.app:create_app db migrate -m "descripcion del cambio"
```

Aplicar migraciones:

```bash
flask --app frameworks.flask_mvc.app:create_app db upgrade
```

Revertir la última migración:

```bash
flask --app frameworks.flask_mvc.app:create_app db downgrade
```

## Endpoints iniciales

Salud de la aplicación:

```bash
curl http://127.0.0.1:5000/health
```

Registro de usuario:

```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"practicante@example.com","password":"secret123","tipo":"practicante"}'
```

La respuesta incluye `activation_token` para pruebas locales. En producción ese token debe enviarse por correo.

Activación de cuenta:

```bash
curl -X POST http://127.0.0.1:5000/auth/activate \
  -H "Content-Type: application/json" \
  -d '{"token":"TOKEN_DE_ACTIVACION"}'
```

Inicio de sesión:

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -c cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"email":"practicante@example.com","password":"secret123"}'
```

Usuario autenticado:

```bash
curl -b cookies.txt http://127.0.0.1:5000/auth/me
```

Cierre de sesión:

```bash
curl -X POST -b cookies.txt http://127.0.0.1:5000/auth/logout
```

Solicitud de recuperación de contraseña:

```bash
curl -X POST http://127.0.0.1:5000/auth/recover-password \
  -H "Content-Type: application/json" \
  -d '{"email":"practicante@example.com"}'
```

La respuesta incluye `password_reset_token` para pruebas locales. En producción ese token debe enviarse por correo.

Restablecimiento de contraseña:

```bash
curl -X POST http://127.0.0.1:5000/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token":"TOKEN_DE_RECUPERACION","new_password":"nuevaClave123"}'
```

Perfil del practicante autenticado:

```bash
curl -b cookies.txt http://127.0.0.1:5000/perfil/me
```

Crear o actualizar perfil de practicante:

```bash
curl -X PUT http://127.0.0.1:5000/perfil/me \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"nombres":"Diego","apellidos":"Perez","habilidades":["Python"],"formacion_educativa":["Ingenieria de Sistemas"]}'
```

Agregar habilidad:

```bash
curl -X POST http://127.0.0.1:5000/perfil/me/habilidades \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"habilidad":"Flask"}'
```

Agregar formación educativa:

```bash
curl -X POST http://127.0.0.1:5000/perfil/me/formacion \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"formacion":"UNSA"}'
```

Registrar y verificar identidad:

```bash
curl -X POST http://127.0.0.1:5000/perfil/me/identidad \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"dni":"12345678","carnet_universitario":"20260001"}'
```

Consultar score de reputación:

```bash
curl -b cookies.txt http://127.0.0.1:5000/perfil/me/reputacion
```

## Laboratorio 9: Convenciones RF.1 y RF.2

Esta sección documenta las convenciones de codificación aplicadas sobre los archivos bajo responsabilidad de RF.1 y RF.2.

### RF.1 - Registro y autenticación

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

### RF.2 - Gestión del perfil del joven

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

### Revisión de calidad

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
