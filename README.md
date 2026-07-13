# ChambeaYa

Plataforma web para la gestión de prácticas preprofesionales, conectando estudiantes y empresas mediante postulaciones, seguimiento de procesos, recomendaciones basadas en habilidades y certificación digital de prácticas.

---

# Propósito

ChambeaYa tiene como propósito facilitar la gestión integral de prácticas preprofesionales mediante una plataforma web que conecte estudiantes y empresas. El sistema centraliza la publicación de convocatorias, el proceso de postulación, el seguimiento de las prácticas y la emisión de certificados digitales, optimizando la comunicación entre todos los actores involucrados.

---

# Funcionalidades

## Funcionalidades de Alto Nivel

> **Agregar aquí el Diagrama de Casos de Uso UML**

<img width="653" height="350" alt="Diagrama_casos_uso_Usuario1" src="https://github.com/user-attachments/assets/8cc71cd1-e318-4a91-a9f2-13b458c95fff" />
<img width="641" height="402" alt="Diagrama_casos_uso_Interfaz" src="https://github.com/user-attachments/assets/e0c4a67f-6437-4308-b2ad-3c3ba6a44b68" />


### Funcionalidades principales

- Gestión de usuarios.
- Gestión de perfiles de estudiantes y empresas.
- Publicación y administración de convocatorias.
- Postulación a convocatorias.
- Seguimiento del proceso de prácticas.
- Recomendación de oportunidades basada en habilidades.
- Gestión y emisión de certificados digitales.

## Prototipo (GUI)

> **Agregar aquí las capturas o prototipos de la interfaz gráfica del sistema.**

<img width="653" height="1600" alt="screen" src="https://github.com/user-attachments/assets/4b9551bf-5712-44be-8374-ccdae991e3a6" />

---

# Modelo de Dominio

## Diagrama de Clases

> **Agregar aquí el Diagrama de Clases del Dominio.**

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


> **Agregar aquí el Diagrama de Arquitectura (Paquetes + Clases).**

<img width="1714" height="932" alt="ChambeaYa - Arquitectura en Capas Flask UML" src="https://github.com/user-attachments/assets/c948c189-1b8a-4f14-9987-f434a5120d74" />

## Estructura del Proyecto

```text
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

- Python
- Flask
- SQLAlchemy
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
