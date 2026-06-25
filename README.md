# ChambeaYa

Plataforma web para la gestión de prácticas preprofesionales, conectando estudiantes y empresas mediante postulaciones, seguimiento de procesos, recomendaciones basadas en habilidades y certificación digital de prácticas.

## Estructura del proyecto

```bash
ChambeaYa/
├── application/
│   ├── __init__.py
│   ├── certificacionApplicationService.py
│   ├── convocatoriaApplicationService.py
│   ├── matchingApplicationService.py
│   ├── perfilApplicationService.py
│   ├── postulacionApplicationService.py
│   ├── practicaApplicationService.py
│   └── usuarioApplicationService.py
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
│   ├── sqlAlchemyCertificadoRepository.py
│   ├── sqlAlchemyConvocatoriaRepository.py
│   ├── sqlAlchemyPerfilRepository.py
│   ├── sqlAlchemyPostulacionRepository.py
│   ├── sqlAlchemyPracticaRepository.py
│   ├── sqlAlchemySugerenciaRepository.py
│   └── sqlAlchemyUsuarioRepository.py
└── presentation/
    ├── __init__.py
    ├── certificadoController.py
    ├── convocatoriaController.py
    ├── matchingController.py
    ├── perfilController.py
    ├── postulacionController.py
    ├── practicaController.py
    └── usuarioController.py
```

## Capas del sistema


- **domain**: entidades y reglas del negocio.
- **application**: servicios de aplicación.
- **infrastructure**: repositorios e ինտégración con persistencia.
- **presentation**: controladores de la capa de exposición.
- **frameworks**: componentes técnicos como Flask, SQLAlchemy y migraciones.

<img width="3333" height="1812" alt="ChambeaYa - Arquitectura en Capas Flask UML" src="https://github.com/user-attachments/assets/8378e75e-f5ca-4be1-8506-cad06f7e2aed" />


## Tecnologías

- Python
- Flask
- SQLAlchemy

