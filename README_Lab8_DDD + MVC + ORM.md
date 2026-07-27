# 🏗️ Laboratorio 8 – DDD + MVC + ORM

**ChambeaYa - Estructura del Proyecto**

---

## 📋 Objetivo

Organizar la estructura de directorios/archivos del proyecto de una aplicación web implementando **DDD (Domain-Driven Design)** con frameworks **MVC** y **ORM**.

---

## 🧱 Estructura del Proyecto (DDD + MVC + ORM)

```bash
ChambeaYa/
├── config.py                    # Configuración de la aplicación
├── requirements.txt             # Dependencias
├── run.py                       # Punto de entrada
├── domain/                      # 🟢 CAPA DE DOMINIO
│   ├── auth/                    # Entidades y reglas de autenticación
│   ├── perfil/                  # Entidades y reglas de perfil
│   ├── convocatorias/           # Entidades y reglas de convocatorias
│   ├── matching/                # Entidades y reglas de matching
│   ├── practica_evaluacion/     # Entidades y reglas de prácticas
│   └── certificacion/           # Entidades y reglas de certificación
├── application/                 # 🟡 CAPA DE APLICACIÓN
│   ├── usuario_application_service.py
│   ├── perfil_application_service.py
│   ├── convocatoria_application_service.py
│   ├── matching_application_service.py
│   ├── postulacion_application_service.py
│   ├── practica_application_service.py
│   └── certificacion_application_service.py
├── infrastructure/              # 🔵 CAPA DE INFRAESTRUCTURA
│   ├── sqlalchemy_usuario_repository.py
│   ├── sqlalchemy_perfil_repository.py
│   ├── sqlalchemy_convocatoria_repository.py
│   ├── sqlalchemy_postulacion_repository.py
│   └── sqlalchemy_practica_repository.py
├── presentation/                # 🟣 CAPA DE PRESENTACIÓN
│   ├── usuario_controller.py
│   ├── perfil_controller.py
│   ├── convocatoria_controller.py
│   ├── matching_controller.py
│   ├── postulacion_controller.py
│   ├── practica_controller.py
│   └── certificado_controller.py
└── frameworks/                  # ⚙️ FRAMEWORKS
    ├── flask_mvc/               # Configuración de Flask
    │   ├── app.py               # Fábrica de la aplicación
    │   ├── routes/              # Registro de rutas
    │   ├── templates/           # Plantillas HTML
    │   └── static/              # Archivos estáticos
    ├── sqlalchemy_orm/          # Configuración de SQLAlchemy
    │   ├── database.py          # Conexión a BD
    │   └── models/              # Modelos ORM (mapeo)
    └── migrations/              # Migraciones de base de datos
```

## 📊 Diagrama de Clases del Dominio

`images/diagrama_clases_dominio.png`

## 🧩 Módulos del Dominio

| Módulo | Descripción |
|--------|-------------|
| auth | Autenticación y usuarios |
| perfil | Perfiles de practicantes y empresas |
| convocatorias | Gestión de convocatorias de prácticas |
| matching | Recomendaciones y postulaciones |
| practica_evaluacion | Prácticas, entregables y evaluaciones |
| certificacion | Certificados digitales y reputación |

## 🔄 Flujo de Datos (Arquitectura Hexagonal)

```text
[Cliente] → [Controller] → [Application Service] → [Domain Entity]
                              ↓
                         [Repository Interface] ← [Domain]
                              ↑
                    [Repository Implementation] ← [Infrastructure]
                              ↓
                         [SQLAlchemy Model] → [Database]
```

## 🛠 Tecnologías Utilizadas

| Tecnología | Descripción |
|------------|-------------|
| Python 3.14+ | Lenguaje de programación |
| Flask | Framework web (MVC) |
| SQLAlchemy | ORM para persistencia |
| Flask-Migrate | Migraciones de base de datos |
| SQLite | Base de datos (desarrollo) |

## 🚀 Ejecución Local

```bash
# 1. Clonar repositorio
git clone https://github.com/MoisesCcaso/ChambeaYa.git
cd ChambeaYa

# 2. Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env

# 5. Crear migraciones y base de datos
flask --app frameworks.flask_mvc.app:create_app db init
flask --app frameworks.flask_mvc.app:create_app db migrate -m "Initial migration"
flask --app frameworks.flask_mvc.app:create_app db upgrade

# 6. Ejecutar la aplicación
flask --app frameworks.flask_mvc.app:create_app run --debug

# 7. Verificar
curl http://127.0.0.1:5000/health
```

📅 Fecha: Julio 2026
