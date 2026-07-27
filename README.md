# ChambeaYa

Plataforma web para la gestión de prácticas preprofesionales, conectando estudiantes y empresas mediante postulaciones, seguimiento de procesos, recomendaciones basadas en habilidades y certificación digital de prácticas.

---

# Propósito

ChambeaYa tiene como propósito facilitar la gestión integral de prácticas preprofesionales mediante una plataforma web que conecte estudiantes y empresas. El sistema centraliza la publicación de convocatorias, el proceso de postulación, el seguimiento de las prácticas y la emisión de certificados digitales, optimizando la comunicación entre todos los actores involucrados.

---

# Funcionalidades

## Funcionalidades de Alto Nivel

<img width="653" height="350" alt="Diagrama_casos_uso_Usuario1" src="https://github.com/user-attachments/assets/8cc71cd1-e318-4a91-a9f2-13b458c95fff" />
<img width="641" height="402" alt="Diagrama_casos_uso_Interfaz" src="https://github.com/user-attachments/assets/e0c4a67f-6437-4308-b2ad-3c3ba6a44b68" />


### Funcionalidades principales

- Gestión de usuarios.
- Registro, activación de cuenta y recuperación de contraseña por correo.
- Gestión de perfiles de estudiantes y empresas.
- Publicación y administración de convocatorias.
- Postulación a convocatorias.
- Seguimiento de prácticas, entregables y evaluaciones.
- Recomendación de oportunidades basada en habilidades.
- Gestión de notificaciones.
- Gestión y emisión de certificados digitales.

## Prototipo (GUI)

<img width="653" height="1600" alt="screen" src="https://github.com/user-attachments/assets/4b9551bf-5712-44be-8374-ccdae991e3a6" />

---

# Modelo de Dominio

## Diagrama de Clases

<img width="1754" height="932" alt="ChambeaYa - Domain Model (DDD)" src="https://github.com/user-attachments/assets/6fcab8ba-61e0-482c-aad8-2ad69dfcb3ea" />

## Módulos del Dominio

El dominio del sistema se encuentra organizado en los siguientes módulos:

- **Auth**
- **Perfil**
- **Convocatorias**
- **Matching**
- **Práctica y Evaluación**
- **Certificación**

---

# Vista General de Arquitectura

## Arquitectura del Sistema

El proyecto sigue una arquitectura por capas inspirada en los principios de **Domain-Driven Design (DDD)**, separando claramente la lógica del negocio, los casos de uso, la infraestructura y la presentación.

<img width="1714" height="932" alt="ChambeaYa - Arquitectura en Capas Flask UML" src="https://github.com/user-attachments/assets/c948c189-1b8a-4f14-9987-f434a5120d74" />

## Estructura del Proyecto

```text
ChambeaYa/
├── config.py
├── requirements.txt
├── run.py
├── application/
│   ├── __init__.py
│   ├── certificacion_application_service.py
│   ├── convocatoria_application_service.py
│   ├── email_delivery_error.py
│   ├── matching_application_service.py
│   ├── notificacion_application_service.py
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
│   ├── notificaciones/
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
│   ├── smtp_auth_email_sender.py
│   ├── sqlalchemy_certificado_repository.py
│   ├── sqlalchemy_convocatoria_repository.py
│   ├── sqlalchemy_matching_repository.py
│   ├── sqlalchemy_notificacion_repository.py
│   ├── sqlalchemy_perfil_repository.py
│   ├── sqlalchemy_postulacion_repository.py
│   ├── sqlalchemy_practica_repository.py
│   └── sqlalchemy_usuario_repository.py
└── presentation/
    ├── __init__.py
    ├── certificado_controller.py
    ├── convocatoria_controller.py
    ├── matching_controller.py
    ├── notificacion_controller.py
    ├── perfil_controller.py
    ├── postulacion_controller.py
    ├── practica_controller.py
    └── usuario_controller.py
```

## Organización de Capas

| Capa | Responsabilidad |
|------|-----------------|
| **Domain** | Contiene las entidades, objetos de valor, reglas del negocio y servicios de dominio. |
| **Application** | Implementa los casos de uso y coordina la interacción entre el dominio y la infraestructura. |
| **Infrastructure** | Implementa repositorios, persistencia e integración con tecnologías externas. |
| **Presentation** | Expone la funcionalidad del sistema mediante controladores y endpoints. |
| **Frameworks** | Contiene la configuración e integración con Flask, SQLAlchemy, migraciones y componentes técnicos. |

---

# Tecnologías

- Python 3.10 o superior
- Flask 3
- SQLAlchemy y Flask-SQLAlchemy
- Alembic y Flask-Migrate
- SQLite
- ReportLab y QRCode

## Ejecución local

### Windows (PowerShell)

Crear el entorno, instalar las dependencias y copiar la configuración local:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Crear o actualizar la base de datos:

```powershell
.\.venv\Scripts\python.exe -m flask `
  --app frameworks.flask_mvc.app:create_app `
  db upgrade
```

Iniciar la aplicación:

```powershell
.\.venv\Scripts\python.exe -m flask `
  --app frameworks.flask_mvc.app:create_app `
  run --debug
```

### Linux o macOS

Crear y activar el entorno:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m flask --app frameworks.flask_mvc.app:create_app db upgrade
python -m flask --app frameworks.flask_mvc.app:create_app run --debug
```

La aplicación estará disponible en `http://127.0.0.1:5000`. Para comprobarla:

```powershell
curl.exe http://127.0.0.1:5000/health
```

La respuesta esperada es:

```json
{"service":"ChambeaYa","status":"ok"}
```

### Verificación de correo

Las cuentas nuevas permanecen en estado `pendiente` hasta que el usuario abre
el enlace de activación enviado a su correo. Para utilizar un servidor SMTP
real, configura en `.env`:

```env
APP_URL=http://127.0.0.1:5000
MAIL_DELIVERY_MODE=smtp
MAIL_SERVER=smtp.tu-proveedor.com
MAIL_PORT=587
MAIL_USERNAME=tu_usuario_smtp
MAIL_PASSWORD=tu_clave_smtp
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_SENDER=ChambeaYa <no-reply@tu-dominio.com>
EXPOSE_AUTH_TOKENS=false
```

`APP_URL` debe ser la dirección desde la que el usuario puede abrir la
aplicación. Si el correo se abre en otro dispositivo, utiliza una dirección de
red o URL pública accesible en lugar de `127.0.0.1`.

En los modos `console` y `demo` los tokens pueden exponerse para facilitar las
pruebas locales. Este comportamiento debe permanecer desactivado cuando se
envían correos reales.

Para comprobar la conexión después de configurar SMTP:

```powershell
.\.venv\Scripts\python.exe -m flask `
  --app frameworks.flask_mvc.app:create_app `
  test-email --to tu_correo@gmail.com
```

Levantar la aplicación:

No utilices la contraseña normal de Gmail ni subas el archivo `.env` al
repositorio.

`APP_URL` debe ser la dirección desde la que el usuario puede abrir la
aplicación. Si el correo se abre en otro dispositivo, utiliza una dirección de
red o URL pública accesible en lugar de `127.0.0.1`.

Para comprobar la conexión después de configurar SMTP:

```powershell
.\.venv\Scripts\python.exe -m flask `
  --app frameworks.flask_mvc.app:create_app `
  test-email --to tu_correo@gmail.com
```

La referencia completa del backend, sus endpoints y el flujo integrado se
encuentra en [`BACKEND.md`](BACKEND.md).

La guía de las vistas, rutas y estructura de la interfaz se encuentra en
[`VISTAS.md`](VISTAS.md).

Para una presentación local con cuentas y datos preparados, utiliza
[`DEMO.md`](DEMO.md) y ejecuta:

```powershell
.\demo.ps1 -Reset
```

Esto usa `instance/chambeaya-demo.db`, una base independiente de la base de
desarrollo, y carga dos cuentas listas para la exposición.

## Pruebas

Ejecutar todas las pruebas desde PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

En Linux o macOS:

```bash
python -m unittest discover -s tests -v
```

La referencia completa del backend, sus endpoints y el flujo integrado se
encuentra en [`BACKEND.md`](BACKEND.md).

La guía de las vistas, rutas y estructura de la interfaz se encuentra en
[`VISTAS.md`](VISTAS.md).

Para una presentación local con cuentas y datos preparados, utiliza
[`DEMO.md`](DEMO.md) y ejecuta:

```powershell
.\demo.ps1
```

Ejecutar las pruebas integrales:

```bash
python -m unittest discover -s tests -v
```

## Migraciones

El entorno de migraciones ya está inicializado en `frameworks/migrations`.
En Windows, usa `.\.venv\Scripts\python.exe` donde los siguientes comandos
indican `python`.

Crear una nueva migración después de modificar modelos:

```bash
python -m flask --app frameworks.flask_mvc.app:create_app db migrate -m "descripcion del cambio"
```

Aplicar migraciones:

```bash
python -m flask --app frameworks.flask_mvc.app:create_app db upgrade
```

Revertir la última migración:

```bash
python -m flask --app frameworks.flask_mvc.app:create_app db downgrade
```

La base SQLite de desarrollo se guarda en `instance/chambeaya.db`. Para
reiniciarla, detén la aplicación, elimina únicamente ese archivo y vuelve a
ejecutar `db upgrade`. Los archivos subidos se almacenan por separado en
`instance/uploads/entregables`.

## Endpoints iniciales

Salud de la aplicación:

```bash
curl http://127.0.0.1:5000/health
```

Registro de usuario:

```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"practicante@example.com","password":"Secret123","password_confirmation":"Secret123","tipo":"practicante"}'
```

La respuesta incluye `activation_token` únicamente en los modos locales que
tienen `EXPOSE_AUTH_TOKENS=true`. Con SMTP, el token se entrega dentro del
enlace enviado al correo.

Activación de cuenta:

```bash
curl -X POST http://127.0.0.1:5000/auth/activate \
  -H "Content-Type: application/json" \
  -d '{"token":"TOKEN_DE_ACTIVACION"}'
```

Reenviar el enlace de activación:

```bash
curl -X POST http://127.0.0.1:5000/auth/resend-activation \
  -H "Content-Type: application/json" \
  -d '{"email":"practicante@example.com"}'
```

Inicio de sesión:

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -c cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"email":"practicante@example.com","password":"Secret123"}'
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

La respuesta incluye `password_reset_token` solamente cuando
`EXPOSE_AUTH_TOKENS=true`. En el flujo SMTP se envía un enlace de recuperación
al correo registrado.

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
## Convenciones de Codificación

**Lenguaje:** Python 3, siguiendo [PEP 8](https://peps.python.org/pep-0008/).
**Herramienta de análisis estático:** SonarLint (extensión VS Code).

### Prácticas aplicadas
- **Nomenclatura:** `snake_case` para funciones/variables (`subir_entregable`,
  `obtener_historial_entregables`), `PascalCase` para clases (`Practica`,
  `Entregable`, `Evaluacion`), `UPPER_CASE` para constantes de dominio
  (`PUNTAJE_APROBACION`).
- **Encapsulamiento:** métodos internos prefijados con `_` para distinguirlos
  de la API pública de cada clase (`_to_practica_domain`, `_serialize_practica`).
- **Validación explícita:** excepciones específicas (`ValueError`) con mensajes
  descriptivos en español, en vez de fallos silenciosos.
- **Type hints y docstrings:** agregados en los métodos de dominio para mejorar
  legibilidad y mantenimiento.
- **Separación de responsabilidades (DDD):** las reglas de negocio (ej. "no se
  puede finalizar una práctica sin entregables") viven en la entidad de dominio
  `Practica`, no en el controlador ni en el repositorio.
- Alembic
- Flask-Migrate

---

# Gestión del Proyecto

## Tablero Kanban / Scrum

El seguimiento del proyecto se realizó mediante un tablero basado en la metodología **User Story Mapping**, organizado en Trello.

<img width="1856" height="818" alt="TableroTrello-ChambeaYa" src="https://github.com/user-attachments/assets/0502f27f-b8a4-43d3-8807-3707745d04c8" />

### Distribución de responsabilidades

| Integrante | Rango asignado | Módulo |
|------------|----------------|--------|
| Omar | 1–5 | Perfil A (Joven) |
| Edú | 6–10 | Perfil A (Joven) |
| Moisés | 1–5 | Perfil B (Empresa) |
| Jhair | 1–6 | Sistema |
| Lorenzo | 6–7 | Perfil B (Empresa) |
| Lorenzo | 1–3 | Product Backlog |
| Roid | 4–8 | Product Backlog |
