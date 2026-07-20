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
