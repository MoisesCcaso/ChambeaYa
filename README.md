# ChambeaYa

Plataforma web para la gestión de prácticas preprofesionales, conectando estudiantes y empresas mediante postulaciones, seguimiento de procesos, recomendaciones basadas en habilidades y certificación digital de prácticas.

## Estructura del proyecto

```bash
ChambeaYa/
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
│   ├── migrations/
│   ├── schemas/
│   └── sqlalchemy_orm/
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
