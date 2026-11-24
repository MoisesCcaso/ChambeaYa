# ChambeaYa

Plataforma web para la gestión de prácticas preprofesionales, conectando estudiantes y empresas mediante postulaciones, seguimiento de procesos, recomendaciones basadas en habilidades y certificación digital de prácticas.

**Stack:** Python 3.12+ · Flask 3 · SQLAlchemy · Alembic · SQLite · Poetry · pytest · Selenium · SonarQube · Jenkins

## Inicio rápido

```bash
poetry install
cp .env.example .env            # Windows: Copy-Item .env.example .env
poetry run flask --app frameworks.flask_mvc.app:create_app db upgrade
poetry run flask --app frameworks.flask_mvc.app:create_app run --debug
```

Abre `http://127.0.0.1:5000`. Para una demo con datos precargados, consulta el [modo demo](#92-modo-demo).

---

## Índice

- [1. Equipo de Trabajo](#1-equipo-de-trabajo)
- [2. Propósito del Proyecto](#2-propósito-del-proyecto)
- [3. Funcionalidades](#3-funcionalidades)
  - [3.1 Diagrama de Casos de Uso UML](#31-diagrama-de-casos-de-uso-uml)
  - [3.2 Prototipo (GUI)](#32-prototipo-gui)
  - [3.3 Funcionalidades principales](#33-funcionalidades-principales)
- [4. Modelo de Dominio](#4-modelo-de-dominio)
  - [4.1 Diagrama de Clases](#41-diagrama-de-clases)
  - [4.2 Módulos del Dominio](#42-módulos-del-dominio)
  - [4.3 Entidades](#43-entidades)
  - [4.4 Value Objects](#44-value-objects)
  - [4.5 Servicios de Dominio](#45-servicios-de-dominio)
  - [4.6 Agregados](#46-agregados)
  - [4.7 Fábricas](#47-fábricas)
  - [4.8 Repositorios](#48-repositorios)
  - [4.9 Arquitectura en Capas](#49-arquitectura-en-capas)
- [5. Visión General de Arquitectura](#5-visión-general-de-arquitectura)
  - [5.1 Diagrama de Paquetes](#51-diagrama-de-paquetes)
  - [5.2 Estructura del Proyecto](#52-estructura-del-proyecto)
  - [5.3 Clean Architecture / DDD](#53-clean-architecture--ddd)
- [6. Prácticas de Desarrollo Aplicadas](#6-prácticas-de-desarrollo-aplicadas)
  - [6.1 Estilos de Programación](#61-estilos-de-programación)
    - [6.1.1 Things](#611-things-cosas--oop)
    - [6.1.2 Error/Exception Handling](#612-errorexception-handling)
    - [6.1.3 Persistent-Tables](#613-persistent-tables-tablas-persistentes)
    - [6.1.4 Trinity](#614-trinity-tres-capas)
    - [6.1.5 Restful](#615-restful)
  - [6.2 Convenciones de Codificación](#62-convenciones-de-codificación)
  - [6.3 Codificación Limpia (Clean Code)](#63-codificación-limpia-clean-code)
  - [6.4 Principios SOLID](#64-principios-solid)
  - [6.5 Domain-Driven Design (DDD)](#65-domain-driven-design-ddd)
    - [6.5.1 Entidades](#651-entidades)
    - [6.5.2 Objetos de Valor](#652-objetos-de-valor)
    - [6.5.3 Servicios de Dominio](#653-servicios-de-dominio)
    - [6.5.4 Agregados y Módulos](#654-agregados-y-módulos)
    - [6.5.5 Fábricas](#655-fábricas)
    - [6.5.6 Repositorios](#656-repositorios)
    - [6.5.7 Arquitectura en Capas](#657-arquitectura-en-capas)
- [7. Gestión del Proyecto](#7-gestión-del-proyecto)
  - [7.1 Tablero Trello](#71-tablero-trello)
  - [7.2 Distribución de responsabilidades](#72-distribución-de-responsabilidades)
- [8. Tecnologías](#8-tecnologías)
- [9. Ejecución local](#9-ejecución-local)
  - [9.1 Instalación y arranque](#91-instalación-y-arranque)
  - [9.2 Modo demo](#92-modo-demo)
  - [9.3 Verificación de correo (SMTP)](#93-verificación-de-correo-smtp)
- [10. Interfaz web](#10-interfaz-web)
- [11. API REST](#11-api-rest)
- [12. Persistencia y migraciones](#12-persistencia-y-migraciones)
- [13. Pruebas](#13-pruebas)
- [14. Integración y despliegue continuo (Jenkins)](#14-integración-y-despliegue-continuo-jenkins)

---

# 1. Equipo de Trabajo

| Integrante | Rango asignado | Módulo / Responsabilidad |
|------------|----------------|--------------------------|
| Omar Rivera Olivera | 1–5 | Perfil A (Joven) — UCs 1–5 |
| Edú Sucari Ccansaya | 6–10 | Perfil A (Joven) — UCs 6–10 |
| Moisés Ccaso Idme | 1–5 | Perfil B (Empresa) — UCs 1–5 |
| Jhair Torres Chávez | 1–6 | Sistema — UCs 1–6 |
| Lorenzo Quispe Torrez | 6–7 | Perfil B (Empresa) — UCs 6–7 |
| Roid Huaylla Guzman | 4–8 | Product Backlog — UCs 4–8 |

**URL del repositorio:** `https://github.com/MoisesCcaso/ChambeaYa`

---

# 2. Propósito del Proyecto

ChambeaYa tiene como propósito facilitar la gestión integral de prácticas preprofesionales mediante una plataforma web que conecte estudiantes y empresas. El sistema centraliza la publicación de convocatorias, el proceso de postulación, el seguimiento de las prácticas y la emisión de certificados digitales, optimizando la comunicación entre todos los actores involucrados.

---

# 3. Funcionalidades

## 3.1 Diagrama de Casos de Uso UML

<img width="653" height="350" alt="Diagrama_casos_uso_Usuario1" src="https://github.com/user-attachments/assets/8cc71cd1-e318-4a91-a9f2-13b458c95fff" />
<img width="641" height="402" alt="Diagrama_casos_uso_Interfaz" src="https://github.com/user-attachments/assets/e0c4a67f-6437-4308-b2ad-3c3ba6a44b68" />

## 3.2 Prototipo (GUI)

<img width="2560" height="2274" alt="image" src="https://github.com/user-attachments/assets/34553da9-6040-4355-9546-bb309ab573e5" />

<img width="2560" height="1417" alt="image" src="https://github.com/user-attachments/assets/58c69ccc-fbf3-4980-baee-fed182929df0" />

<img width="2560" height="1504" alt="image" src="https://github.com/user-attachments/assets/8116b851-98e2-4e3a-b504-7fe8d963b0c7" />

<img width="2560" height="1417" alt="image" src="https://github.com/user-attachments/assets/5afbc9f5-3ddd-4e85-910c-a44d63f42d72" />

<img width="2560" height="1417" alt="image" src="https://github.com/user-attachments/assets/10dcebf7-a0a0-4412-83a4-a9753bc3156c" />

<img width="2560" height="1417" alt="image" src="https://github.com/user-attachments/assets/969b9e9f-82d1-4c22-920b-f17beeb7d525" />

## 3.3 Funcionalidades principales

- Gestión de usuarios (registro, activación de cuenta, inicio de sesión, recuperación de contraseña)
- Gestión de perfiles de estudiantes y empresas (datos personales, habilidades, formación, RUC)
- Publicación y administración de convocatorias (CRUD, publicar, cerrar, reabrir, duplicar)
- Postulación a convocatorias (aplicar, cancelar, reconsiderar)
- Matching basado en habilidades (sugerencias con puntaje de compatibilidad)
- Seguimiento de prácticas (iniciar, subir entregables, registrar evaluaciones, finalizar)
- Notificaciones automáticas de eventos (selección, evaluación, certificado, sugerencias)
- Gestión y emisión de certificados digitales (PDF + QR con verificación pública)
- Validación de identidad (DNI/carnet para practicante, RUC para empresa)
- Score de reputación para practicantes
- Vista web con interfaz adaptativa para ambos roles

---

# 4. Modelo de Dominio

## 4.1 Diagrama de Clases

<img width="1754" height="932" alt="ChambeaYa - Domain Model (DDD)" src="https://github.com/user-attachments/assets/6fcab8ba-61e0-482c-aad8-2ad69dfcb3ea" />

## 4.2 Módulos del Dominio

El dominio del sistema se organiza en 7 módulos:

| Módulo | Propósito | Entidades |
|--------|-----------|-----------|
| `auth` | Autenticación, registro, activación, recuperación de contraseña | `Usuario`, `TokenRecuperacion` |
| `perfil` | Gestión de perfiles de practicante y empresa | `Practicante`, `Empresa`, `NombreCompleto`, `RUC` |
| `convocatorias` | Publicación y administración de convocatorias y postulaciones | `Convocatoria`, `Postulacion` |
| `matching` | Algoritmo de compatibilidad entre habilidades del practicante y requisitos de la convocatoria | `Sugerencia`, `ResultadoMatching` |
| `practica_evaluacion` | Ciclo de vida de la práctica, entregables y evaluaciones | `Practica`, `Entregable`, `Evaluacion` |
| `notificaciones` | Notificaciones automáticas de eventos del sistema | `Notificacion` |
| `certificacion` | Emisión y verificación de certificados digitales | `Certificado`, `ArchivoPDF`, `CodigoQR` |

## 4.3 Entidades

Las entidades tienen identidad propia (id) y encapsulan comportamiento de negocio.

| Entidad | Módulo | Atributos clave | Comportamiento |
|---------|--------|-----------------|----------------|
| `Usuario` | auth | email, password_hash, tipo, estado, activation_token | registrar(), login(), activar(), asignar_token_activacion(), actualizar_password() |
| `Practicante` | perfil | nombres, apellidos, dni, habilidades, score_reputacion | actualizar_datos(), agregar_habilidad(), verificar_identidad(), calcular_score() |
| `Empresa` | perfil | razon_social, ruc, verificada | verificar_ruc() |
| `Convocatoria` | convocatorias | titulo, descripcion, estado, habilidades_requeridas, beneficios | publicar(), cerrar(), reabrir(), actualizar(), validar_eliminacion() |
| `Postulacion` | convocatorias | estado (pendiente/seleccionada/rechazada/cancelada) | seleccionar(), rechazar(), cancelar(), reactivar(), reconsiderar() |
| `Sugerencia` | matching | puntaje_match, habilidades_coincidentes | calcular_compatibilidad() |
| `Practica` | practica_evaluacion | estado (EN_CURSO/FINALIZADA), entregables, evaluaciones | subir_entregable(), registrar_evaluacion(), finalizar() |
| `Entregable` | practica_evaluacion | archivo, fecha_subida | (creado por factory estática) |
| `Evaluacion` | practica_evaluacion | puntaje (0-100), fecha_evaluacion | esta_aprobada() (umbral ≥ 60) |
| `Notificacion` | notificaciones | tipo, mensaje, metadata, leida | marcar_como_leida() |
| `Certificado` | certificacion | codigo_qr, documento | generar_pdf(), verificar_integridad() |

## 4.4 Value Objects

Son objetos inmutables con validación encapsulada, sin identidad propia.

| Value Object | Módulo | Validación |
|-------------|--------|------------|
| `TokenRecuperacion` | auth | Esta_vigente() — verifica expiración contra UTC |
| `NombreCompleto` | perfil | Validar() — nombres y apellidos obligatorios |
| `RUC` | perfil | Es_valido() — algoritmo módulo 11 SUNAT con prefijos 10, 15, 17, 20 |
| `ArchivoPDF` | certificacion | Verificar_integridad() — SHA-256 del contenido |
| `CodigoQR` | certificacion | Generar() + verificar() con hash SHA-256 |
| `ResultadoMatching` | matching | Es_compatible(umbral) — score ≥ umbral |

**Fragmento — RUC con validación SUNAT:**

```python
# src/main/domain/perfil/ruc.py
class RUC:
    def __init__(self, numero=None):
        self.numero = numero

    def es_valido(self):
        prefijos_validos = ("10", "15", "17", "20")
        factores = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)
        numero = self.numero
        if not numero or not isinstance(numero, str) or not numero.isdigit() or len(numero) != 11:
            return False
        if numero[:2] not in prefijos_validos:
            return False
        digitos = [int(d) for d in numero[:10]]
        suma = sum(d * f for d, f in zip(digitos, factores))
        digito_verificador = 11 - (suma % 11)
        if digito_verificador == 10: digito_verificador = 0
        elif digito_verificador == 11: digito_verificador = 1
        return digito_verificador == int(numero[10])
```

## 4.5 Servicios de Dominio

Son clases sin estado que implementan lógica de negocio que no pertenece a una sola entidad.

| Servicio | Módulo | Métodos clave |
|----------|--------|---------------|
| `AutenticacionDominioServicio` | auth | generar_password_hash(), autenticar(), generar_token(), validar_token() |
| `MatchingDominioServicio` | matching | calcular_match(), filtrar_convocatorias() |
| `CertificacionDominioServicio` | certificacion | generar_certificado(), verificar_codigo_qr() |

**Fragmento — MatchingDominioServicio:**

```python
# src/main/domain/matching/matching_dominio_servicio.py
class MatchingDominioServicio:
    def calcular_match(self, practicante, convocatoria):
        sugerencia = Sugerencia(
            practicante_id=practicante.id,
            convocatoria_id=convocatoria.id,
        )
        score = sugerencia.calcular_compatibilidad(
            practicante.habilidades,
            convocatoria.habilidades_requeridas,
        )
        return ResultadoMatching(
            score_compatibilidad=score,
            practicante_id=practicante.id,
            convocatoria_id=convocatoria.id,
            sugerencia=sugerencia,
        )

    def filtrar_convocatorias(self, practicante, convocatorias, umbral=50.0):
        resultados = []
        for convocatoria in convocatorias:
            if convocatoria.estado != Convocatoria.ESTADO_PUBLICADA:
                continue
            resultado = self.calcular_match(practicante, convocatoria)
            if resultado is not None and resultado.es_compatible(umbral):
                resultados.append(resultado)
        return sorted(resultados, key=lambda r: r.score_compatibilidad, reverse=True)
```

## 4.6 Agregados

Un agregado es un conjunto de entidades relacionadas donde una raíz garantiza la consistencia de las invariantes.

**Agregado `Practica`** (raíz: `Practica`, hijos: `Entregable`, `Evaluacion`):

```
Practica (raíz)
  ├── id, postulacion_id, practicante_id, estado
  ├── Entregable[]  — solo se acceden/modifican a través de Practica
  └── Evaluacion[]  — solo se acceden/modifican a través de Practica
```

La raíz `Practica` controla todas las operaciones: no se pueden subir entregables si está finalizada, no se puede finalizar sin entregables ni sin una evaluación aprobada. Los hijos no existen independientemente de la raíz.

## 4.7 Fábricas

Son objetos que encapsulan la creación de entidades complejas, asegurando que nazcan en un estado válido.

| Fábrica | Crea | Validaciones |
|---------|------|-------------|
| `ConvocatoriaFabrica` | `Convocatoria` en estado `BORRADOR` | empresa_id obligatorio, título obligatorio, habilidades y beneficios como lista |
| `Practica.iniciar` (factory method) | `Practica` en estado `EN_CURSO` | postulacion_id y practicante_id obligatorios |

**Fragmento — ConvocatoriaFabrica:**

```python
# src/main/domain/convocatorias/convocatoria_fabrica.py
class ConvocatoriaFabrica:
    def crear_convocatoria(self, empresa_id, titulo, habilidades_requeridas=None,
                           descripcion=None, beneficios=None):
        if not empresa_id:
            raise ValueError("La empresa es obligatoria")
        if not titulo or not str(titulo).strip():
            raise ValueError("El título es obligatorio")
        convocatoria = Convocatoria()
        convocatoria.empresa_id = empresa_id
        convocatoria.titulo = str(titulo).strip()
        convocatoria.descripcion = str(descripcion).strip() if descripcion else None
        convocatoria.estado = Convocatoria.ESTADO_BORRADOR
        for habilidad in (habilidades_requeridas or []):
            convocatoria.agregar_habilidad_requerida(habilidad)
        for beneficio in (beneficios or []):
            convocatoria.agregar_beneficio(beneficio)
        return convocatoria
```

## 4.8 Repositorios

Cada repositorio tiene una interfaz en la capa de dominio (contrato abstracto) y una implementación concreta en infraestructura (SQLAlchemy). El `ApplicationService` depende solo de la abstracción.

### Interfaces (capa domain)

| Interfaz | Métodos |
|----------|---------|
| `IUsuarioRepository` | save(), find_by_email(), find_by_id(), find_by_activation_token(), find_by_password_reset_token() |
| `IPerfilRepository` | save_practicante(), save_empresa(), find_practicante_by_user_id(), find_practicante_by_id(), find_empresa_by_user_id() |
| `IConvocatoriaRepository` | save(), find_by_id(), find_all(), search(), find_by_empresa_id(), delete() |
| `IPostulacionRepository` | save(), find_by_id(), find_by_practicante_id(), find_by_convocatoria_id(), find_by_convocatoria_and_practicante() |
| `ISugerenciaRepository` | save(), find_by_practicante_id() |
| `IPracticaRepository` | save(), find_by_id(), find_by_practicante_id(), find_by_postulacion_id() |
| `INotificacionWriter` | save(), mark_as_read(), mark_all_as_read() |
| `INotificacionReader` | find_by_usuario_id(), find_unread_by_usuario_id(), count_unread() |
| `ICertificadoRepository` | save(), find_by_id(), find_by_codigo(), find_by_practica_id() |

### Implementaciones (capa infrastructure)

| Implementación | Interfaz(es) | Tecnología |
|----------------|-------------|------------|
| `SqlAlchemyUsuarioRepository` | IUsuarioRepository | SQLAlchemy + SQLite |
| `SqlAlchemyPerfilRepository` | IPerfilRepository | SQLAlchemy + SQLite |
| `SqlAlchemyConvocatoriaRepository` | IConvocatoriaRepository | SQLAlchemy + SQLite |
| `SqlAlchemyPostulacionRepository` | IPostulacionRepository | SQLAlchemy + SQLite |
| `SqlAlchemyMatchingRepository` | ISugerenciaRepository | SQLAlchemy + SQLite |
| `SqlAlchemyPracticaRepository` | IPracticaRepository | SQLAlchemy + SQLite |
| `SqlAlchemyNotificacionRepository` | INotificacionWriter + INotificacionReader | SQLAlchemy + SQLite |
| `SqlAlchemyCertificadoRepository` | ICertificadoRepository | SQLAlchemy + SQLite |

**Fragmento — Contrato + implementación:**

```python
# src/main/domain/practica_evaluacion/i_practica_repository.py — Interfaz (dominio)
class IPracticaRepository(ABC):
    @abstractmethod
    def save(self, practica): ...
    @abstractmethod
    def find_by_id(self, practica_id): ...
    @abstractmethod
    def find_by_practicante_id(self, practicante_id): ...

# src/main/infrastructure/sqlalchemy_practica_repository.py — Implementación
class SqlAlchemyPracticaRepository(IPracticaRepository):
    def save(self, practica):
        model = None
        if practica.id is not None:
            model = db.session.get(PracticaModel, practica.id)
        if model is None:
            model = PracticaModel(postulacion_id=practica.postulacion_id,
                                  practicante_id=practica.practicante_id)
            db.session.add(model)
        model.estado = practica.estado
        # Sincroniza colecciones hijas (Entregable, Evaluacion)...
        db.session.commit()
        return self._to_practica_domain(model)

    def find_by_id(self, practica_id):
        model = db.session.get(PracticaModel, practica_id)
        return self._to_practica_domain(model)

    def _to_practica_domain(self, model):
        if model is None:
            return None
        entregables = [Entregable(id=e.id, archivo=e.archivo, ...) for e in model.entregables]
        evaluaciones = [Evaluacion(id=e.id, puntaje=e.puntaje, ...) for e in model.evaluaciones]
        return Practica(id=model.id, ..., entregables=entregables, evaluaciones=evaluaciones)
```

## 4.9 Arquitectura en Capas

El proyecto sigue una arquitectura en 4 capas con la regla de dependencia hacia adentro:

```
┌──────────────────────────────────────────────────────┐
│  frameworks  (Flask routes + serialización JSON,      │
│               SQLAlchemy, Alembic)                    │
│  ┌──────────────────────────────────────────────────┐ │
│  │  application  (Servicios de caso de uso)         │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │  domain  (Entidades, Value Objects,          │ │ │
│  │  │           Interfaces de repositorio,         │ │ │
│  │  │           Servicios de dominio)              │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────┘ │
│  infrastructure  (Repositorios SQLAlchemy, Email)      │
└──────────────────────────────────────────────────────┘
```

**Regla de dependencia:** Las capas externas dependen de las internas, nunca al revés. `frameworks` → `application` → `domain`. `infrastructure` implementa interfaces de `domain`.

---

# 5. Visión General de Arquitectura

## 5.1 Diagrama de Paquetes

<img width="1714" height="932" alt="ChambeaYa - Arquitectura en Capas Flask UML" src="https://github.com/user-attachments/assets/c948c189-1b8a-4f14-9987-f434a5120d74" />

## 5.2 Estructura del Proyecto

El código de implementación está en `src/main/` y las pruebas en `src/test/`,
separados según la estructura solicitada para el laboratorio. La suite se divide
por dominio, infraestructura, aplicación, integración y funcionales.

```text
ChambeaYa/
├── pyproject.toml / poetry.lock   ← dependencias y build (Poetry)
├── sonar-project.properties       ← configuración de SonarQube
├── Jenkinsfile                    ← pipeline de CI/CD
├── demo.ps1                       ← demo en Windows
├── scripts/
│   ├── demo_reset.sh              ← demo en Linux/macOS
│   └── ci/deploy.sh               ← despliegue usado por Jenkins
└── src/
    ├── main/
    │   ├── config.py
    │   ├── run.py
    │   ├── application/
    │   ├── domain/
    │   ├── frameworks/
    │   │   ├── flask_mvc/
    │   │   │   ├── routes/
    │   │   │   ├── static/
    │   │   │   └── templates/
    │   │   ├── migrations/
    │   │   └── sqlalchemy_orm/
    │   └── infrastructure/
    └── test/
        ├── conftest.py
        ├── application/
        ├── domain/
        ├── frameworks/            ← plantillas HTML y accesibilidad
        ├── infrastructure/
        ├── integration/
        └── functional/            ← Selenium (Page Objects)
```

## 5.3 Clean Architecture / DDD

| Capa | Responsabilidad | Depende de |
|------|----------------|------------|
| **Domain** | Entidades, Value Objects, interfaces de repositorio, servicios de dominio | Nada (capa más interna) |
| **Application** | Casos de uso, orquestación, DTOs | Domain |
| **Infrastructure** | Repositorios concretos, email sender, persistencia | Domain (implementa interfaces) |
| **Frameworks** | Flask routes (HTTP + serialización JSON), SQLAlchemy ORM, Alembic, config | Application + Infrastructure |

La inyección de dependencias ocurre en las **rutas** (frameworks), que construyen los objetos concretos y los pasan como abstracciones a las capas internas.

---

# 6. Prácticas de Desarrollo Aplicadas

## 6.1 Estilos de Programación

### 6.1.1 Things (Cosas / OOP)

Las entidades de dominio encapsulan estado y comportamiento juntos. No son DTOs anémicos — contienen las reglas de negocio que protegen sus invariantes. `Practica` gestiona su ciclo de vida (`EN_CURSO` → `FINALIZADA`) y solo permite transiciones válidas.

```python
# src/main/domain/practica_evaluacion/practica.py
class Practica:
    ESTADO_EN_CURSO = "EN_CURSO"
    ESTADO_FINALIZADA = "FINALIZADA"

    def __init__(self, id=None, postulacion_id=None, practicante_id=None,
                 estado=None, entregables=None, evaluaciones=None):
        self.id = id
        self.postulacion_id = postulacion_id
        self.practicante_id = practicante_id
        self.estado = estado or self.ESTADO_EN_CURSO
        self.entregables = entregables or []
        self.evaluaciones = evaluaciones or []

    def subir_entregable(self, archivo):
        if self.estado == self.ESTADO_FINALIZADA:
            raise ValueError("No se pueden subir entregables a una práctica finalizada")
        entregable = Entregable.crear(practica_id=self.id, archivo=archivo)
        self.entregables.append(entregable)
        return entregable

    def finalizar(self):
        if self.estado != self.ESTADO_EN_CURSO:
            raise ValueError("La práctica ya está finalizada")
        if not self.entregables:
            raise ValueError("No se puede finalizar una práctica sin entregables registrados")
        self.estado = self.ESTADO_FINALIZADA
        return self
```

### 6.1.2 Error/Exception Handling

Cada capa lanza excepciones específicas. La capa de routes captura y mapea a códigos HTTP semánticos: `ValueError` → 400, `EmailDeliveryError` → 503, `IntegrityError` → 409. En el dominio se usan guard clauses con `raise ValueError` para fallar rápido ante estados inválidos.

```python
# src/main/application/email_delivery_error.py
class EmailDeliveryError(RuntimeError):
    """Error controlado al entregar un correo transaccional."""

# src/main/frameworks/flask_mvc/routes/auth_routes.py
@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    try:
        usuario = build_usuario_service().register_user(
            email=payload.get("email"),
            password=payload.get("password"),
            password_confirmation=payload.get("password_confirmation"),
            tipo=payload.get("tipo"),
        )
    except EmailDeliveryError as exc:
        return jsonify({"error": str(exc)}), 503
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

# src/main/frameworks/flask_mvc/app.py — error global
@app.errorhandler(IntegrityError)
def handle_integrity_error(_error):
    db.session.rollback()
    return jsonify({"error": "El registro ya existe o contiene datos en conflicto"}), 409
```

### 6.1.3 Persistent-Tables (Tablas Persistentes)

Cada modelo ORM hereda de `db.Model` y mapea directamente a una tabla SQL. Las columnas usan tipos explícitos, claves foráneas, unicidad y defaults. Los campos no escalares (listas) se serializan como JSON text.

```python
# src/main/frameworks/sqlalchemy_orm/models/practicante_model.py
from frameworks.sqlalchemy_orm.database import db

class PracticanteModel(db.Model):
    __tablename__ = "practicantes"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(8), unique=True, nullable=True)
    carnet_universitario = db.Column(db.String(20), nullable=True)
    habilidades = db.Column(db.Text, nullable=False, default="[]")
    formacion_educativa = db.Column(db.Text, nullable=False, default="[]")
    score_reputacion = db.Column(db.Float, nullable=False, default=0.0)
    identidad_verificada = db.Column(db.Boolean, nullable=False, default=False)
```

### 6.1.4 Trinity (Tres Capas)

Cada petición cruza tres capas estrictas. **Route** (framework) construye dependencias, recibe HTTP y serializa la respuesta JSON. **Application Service** orquesta usando servicios de dominio e interfaces de repositorio. **Domain Service** aplica las reglas de negocio. Cada capa solo conoce a la inmediata inferior.

```python
# src/main/frameworks/flask_mvc/routes/matching_routes.py — Route
@matching_bp.get("/sugerencias")
def suggest_convocatorias():
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    try:
        resultados = build_matching_service().suggest_convocatorias(usuario_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify([serialize_resultado(r) for r in resultados]), 200

def build_matching_service():
    return MatchingApplicationService(
        SqlAlchemyMatchingRepository(),
        SqlAlchemyPerfilRepository(),
        SqlAlchemyConvocatoriaRepository(),
        MatchingDominioServicio(),
    )

# src/main/application/matching_application_service.py — Application Service
class MatchingApplicationService:
    def suggest_convocatorias(self, usuario_id, umbral=50.0):
        self._require_repositories()
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Practicante no encontrado")
        convocatorias = self.convocatoria_repository.find_all()
        return self.matching_servicio.filtrar_convocatorias(practicante, convocatorias, umbral)

# src/main/domain/matching/matching_dominio_servicio.py — Domain Service
class MatchingDominioServicio:
    def filtrar_convocatorias(self, practicante, convocatorias, umbral=50.0):
        resultados = []
        for convocatoria in convocatorias:
            if convocatoria.estado != Convocatoria.ESTADO_PUBLICADA:
                continue
            resultado = self.calcular_match(practicante, convocatoria)
            if resultado and resultado.es_compatible(umbral):
                resultados.append(resultado)
        return sorted(resultados, key=lambda r: r.score_compatibilidad, reverse=True)
```

### 6.1.5 Restful

La API usa URLs semánticas con sustantivos en plural, verbos HTTP según su propósito (POST=crear 201, GET=consultar 200, PUT=actualizar 200) y códigos de estado para cada resultado. Los errores de validación retornan 400, no autenticado 401, no encontrado 404, conflicto 409.

```python
# src/main/frameworks/flask_mvc/routes/practica_routes.py
@practica_bp.post("")
def start_practica():
    """POST /practicas — 201: Iniciar práctica"""
    practica = build_practica_service().start_practica(empresa.id, postulacion_id)
    return jsonify(serialize_practica(practica)), 201

@practica_bp.get("/<int:practica_id>")
def get_practica(practica_id):
    """GET /practicas/<id> — 200: Consultar práctica"""
    practica = build_practica_service().get_for_user(usuario_id, practica_id)
    return jsonify(serialize_practica(practica)), 200

@practica_bp.post("/<int:practica_id>/evaluar")
def register_evaluation(practica_id):
    """POST /practicas/<id>/evaluar — 201: Registrar evaluación"""
    practica = build_practica_service().evaluate(empresa.id, practica_id, payload.get("puntaje"))
    return jsonify(serialize_practica(practica)), 201

@practica_bp.post("/<int:practica_id>/finalizar")
def finish_practica(practica_id):
    """POST /practicas/<id>/finalizar — 200: Finalizar práctica"""
    data = serialize_practica(build_practica_service().finish(empresa.id, practica_id))
    return jsonify(data), 200

# Códigos de error en toda la API:
return jsonify({"error": "..."}), 400   # validación
return jsonify({"error": "No autenticado"}), 401  # sin sesión
return jsonify({"error": "..."}), 404   # no encontrado
return jsonify({"error": "..."}), 409   # conflicto (registro duplicado)
return jsonify({"error": "..."}), 503   # error de infraestructura (email)
```

## 6.2 Convenciones de Codificación

### snake_case para funciones, métodos y variables

```python
# src/main/domain/perfil/practicante.py
def agregar_habilidad(self, habilidad):
    habilidad_normalizada = self._normalizar_texto(habilidad)
    if habilidad_normalizada and habilidad_normalizada not in self.habilidades:
        self.habilidades.append(habilidad_normalizada)
    return self
```

### PascalCase para clases

```python
# src/main/domain/practica_evaluacion/practica.py
class Practica: ...

# src/main/domain/practica_evaluacion/evaluacion.py
class Evaluacion: ...
```

### UPPER_CASE para constantes de dominio

```python
# src/main/domain/practica_evaluacion/evaluacion.py
PUNTAJE_APROBACION = 60.0

# src/main/domain/notificaciones/notificacion.py
class Notificacion:
    TIPO_POSTULACION_SELECCIONADA = "POSTULACION_SELECCIONADA"
    TIPO_EVALUACION_DISPONIBLE = "EVALUACION_DISPONIBLE"
    TIPO_CERTIFICADO_EMITIDO = "CERTIFICADO_EMITIDO"
    TIPO_NUEVAS_SUGERENCIAS = "NUEVAS_SUGERENCIAS"
```

### Prefijo `_` para métodos privados

```python
# src/main/infrastructure/sqlalchemy_convocatoria_repository.py
def _to_convocatoria_domain(self, model): ...
def _dump_list(self, values): ...
def _load_list(self, value): ...
```

### Imports ordenados por capa arquitectónica

```python
# src/main/frameworks/flask_mvc/routes/certificado_routes.py
from flask import Blueprint, jsonify, session         # framework

from application.certificacion_application_service import ...  # application
from infrastructure.sqlalchemy_certificado_repository import ...  # infrastructure
```

## 6.3 Codificación Limpia (Clean Code)

- [6.3.1 Nombres descriptivos](#631-nombres-descriptivos)
- [6.3.2 Funciones pequeñas](#632-funciones-pequeñas-una-responsabilidad)
- [6.3.3 Docstrings en endpoints](#633-docstrings-en-endpoints)
- [6.3.4 Imports por capa](#634-imports-por-capa-arquitectónica)
- [6.3.5 Objetos con comportamiento](#635-objetos-con-comportamiento-no-anémicos)
- [6.3.6 Guard clauses + excepciones](#636-guard-clauses--excepciones)
- [6.3.7 Interfaces segregadas](#637-interfaces-segregadas)

### 6.3.1 Nombres descriptivos

Los nombres comunican intención sin requerir comentarios adicionales. El método `calcular_compatibilidad` describe exactamente qué hace: recibe dos listas de habilidades y calcula un score.

```python
# src/main/domain/matching/sugerencia.py
def calcular_compatibilidad(self, habilidades_practicante, habilidades_requeridas):
    if not habilidades_requeridas:
        self.puntaje_match = 0.0
        return self.puntaje_match
    set_practicante = {str(h).strip().casefold() for h in (habilidades_practicante or []) if str(h).strip()}
    set_requeridas = {str(h).strip().casefold() for h in (habilidades_requeridas or []) if str(h).strip()}
    coincidentes = set_practicante & set_requeridas
    self.habilidades_coincidentes = list(coincidentes)
    self.puntaje_match = len(coincidentes) / len(set_requeridas) * 100
    return self.puntaje_match
```

### 6.3.2 Funciones pequeñas (una responsabilidad)

Cada función hace una sola cosa. `issue_certificado()` de la ruta solo atiende HTTP y delega; `serialize_certificado()` solo transforma a dict.

```python
# src/main/frameworks/flask_mvc/routes/certificado_routes.py
def issue_certificado(practica_id):
    ...
    try:
        certificado, creado = build_certificacion_service().issue_certificate(
            empresa.id, practica_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(serialize_certificado(certificado)), 201 if creado else 200

def serialize_certificado(certificado):
    return {
        "id": certificado.id,
        "practica_id": certificado.practica_id,
        "codigo_qr": {"valor": certificado.codigo_qr.valor} if certificado.codigo_qr else None,
        "documento": {"url": certificado.documento.url} if certificado.documento else None,
    }
```

### 6.3.3 Docstrings en endpoints

Los endpoints REST llevan docstring describiendo el método HTTP y la operación que realizan.

```python
# src/main/frameworks/flask_mvc/routes/matching_routes.py
@matching_bp.get("/sugerencias")
def suggest_convocatorias():
    """GET /matching/sugerencias — Obtener convocatorias sugeridas para el practicante."""
    ...

@matching_bp.post("/calcular")
def calculate_match():
    """POST /matching/calcular — Calcular y guardar matching para el practicante."""
    ...
```

### 6.3.4 Imports por capa arquitectónica

Los imports se organizan según la dependencia entre capas: framework → domain → application → infrastructure.

```python
# src/main/frameworks/flask_mvc/routes/postulacion_routes.py
from flask import Blueprint, jsonify, session              # framework

from application.notificacion_application_service import ...  # application
from infrastructure.sqlalchemy_notificacion_repository import ...  # infrastructure
```

### 6.3.5 Objetos con comportamiento (no anémicos)

Las entidades no son simples contenedores de datos; encapsulan validación y lógica de negocio.

```python
# src/main/domain/certificacion/archivo_pdf.py
class ArchivoPDF:
    @staticmethod
    def crear(practica_id, contenido):
        if not contenido:
            raise ValueError("Debe proveerse el contenido del PDF")
        contenido_bytes = contenido.encode() if isinstance(contenido, str) else contenido
        url = f"/certificados/practica/{practica_id}/pdf"
        hash_integridad = hashlib.sha256(contenido_bytes).hexdigest()
        return ArchivoPDF(url=url, hash_integridad=hash_integridad, contenido=contenido)

    def verificar_integridad(self, contenido):
        if contenido is None or not self.hash_integridad:
            return False
        contenido_bytes = contenido.encode() if isinstance(contenido, str) else contenido
        return hashlib.sha256(contenido_bytes).hexdigest() == self.hash_integridad
```

### 6.3.6 Guard clauses + excepciones

Validar primero, ejecutar después. Las precondiciones se verifican al inicio del método con guard clauses cortas.

```python
# src/main/domain/practica_evaluacion/practica.py
def finalizar(self):
    if self.estado != self.ESTADO_EN_CURSO:
        raise ValueError("La práctica ya está finalizada")
    if not self.entregables:
        raise ValueError("No se puede finalizar una práctica sin entregables registrados")
    self.estado = self.ESTADO_FINALIZADA
    return self

# src/main/domain/convocatorias/postulacion.py
def cancelar(self):
    if self.estado != self.ESTADO_PENDIENTE:
        raise ValueError("Solo una postulación pendiente puede retirarse")
    self.estado = self.ESTADO_CANCELADA
    return self
```

### 6.3.7 Interfaces segregadas

Interfaces pequeñas y específicas; cada cliente depende solo de los métodos que realmente usa.

```python
# src/main/domain/notificaciones/i_notificacion_writer.py
class INotificacionWriter(ABC):
    @abstractmethod
    def save(self, notificacion): ...
    @abstractmethod
    def mark_as_read(self, usuario_id, notificacion_id): ...
    @abstractmethod
    def mark_all_as_read(self, usuario_id): ...

# src/main/domain/notificaciones/i_notificacion_reader.py
class INotificacionReader(ABC):
    @abstractmethod
    def find_by_usuario_id(self, usuario_id): ...
    @abstractmethod
    def find_unread_by_usuario_id(self, usuario_id): ...
    @abstractmethod
    def count_unread(self, usuario_id): ...
```

## 6.4 Principios SOLID

- [6.4.1 SRP — Single Responsibility Principle](#641-srp--single-responsibility-principle)
- [6.4.2 OCP — Open/Closed Principle](#642-ocp--openclosed-principle)
- [6.4.3 LSP — Liskov Substitution Principle](#643-lsp--liskov-substitution-principle)
- [6.4.4 ISP — Interface Segregation Principle](#644-isp--interface-segregation-principle)
- [6.4.5 DIP — Dependency Inversion Principle](#645-dip--dependency-inversion-principle)

### 6.4.1 SRP — Single Responsibility Principle

Cada clase tiene una única razón de cambiar. `Notificacion` solo conoce su estado de dominio; las rutas de `notificacion_routes.py` solo atienden HTTP y serializan; `SqlAlchemyNotificacionRepository` solo persiste.

```python
# src/main/domain/notificaciones/notificacion.py — Solo dominio
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
        self.leida = True

# src/main/frameworks/flask_mvc/routes/notificacion_routes.py — Solo HTTP
@notificacion_bp.get("")
def list_notificaciones():
    ...
    notificaciones = build_notificacion_service().list_notifications(usuario_id)
    return jsonify([serialize_notificacion(n) for n in notificaciones]), 200

def serialize_notificacion(notificacion):
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

### 6.4.2 OCP — Open/Closed Principle

Para agregar un nuevo tipo de notificación solo se crea una constante en `Notificacion` y se invoca `create_notification()` desde un hook. No se modifica el ApplicationService, las rutas ni el Repository del módulo de notificaciones.

```python
# src/main/domain/notificaciones/notificacion.py — Abierto a extensión
class Notificacion:
    TIPO_POSTULACION_SELECCIONADA = "POSTULACION_SELECCIONADA"
    TIPO_EVALUACION_DISPONIBLE = "EVALUACION_DISPONIBLE"
    TIPO_CERTIFICADO_EMITIDO = "CERTIFICADO_EMITIDO"
    TIPO_NUEVAS_SUGERENCIAS = "NUEVAS_SUGERENCIAS"

# src/main/application/notificacion_application_service.py — Cerrado a modificación
class NotificacionApplicationService:
    def create_notification(self, usuario_destino_id, tipo, mensaje, metadata=None):
        notificacion = Notificacion(
            usuario_destino_id=usuario_destino_id,
            tipo=tipo,              # cualquier string funciona — no hay switch/case
            mensaje=mensaje,
            metadata=metadata,
        )
        return self.writer.save(notificacion)

# Hook en postulacion_routes.py — extensión sin modificar el módulo notificaciones
notif_service.create_notification(
    usuario_destino_id=practicante.usuario_id,
    tipo="POSTULACION_RECHAZADA",
    mensaje="Tu postulación no fue seleccionada",
)
```

### 6.4.3 LSP — Liskov Substitution Principle

`SqlAlchemyNotificacionRepository` implementa tanto `INotificacionWriter` como `INotificacionReader`. La misma instancia puede inyectarse en ambos roles sin alterar el comportamiento esperado. Si se creara un `PostgresNotificacionRepository` con las mismas interfaces, podría sustituir al actual sin cambiar el ApplicationService ni las rutas.

```python
# src/main/infrastructure/sqlalchemy_notificacion_repository.py
class SqlAlchemyNotificacionRepository(INotificacionWriter, INotificacionReader):
    def save(self, notificacion): ...              # INotificacionWriter
    def mark_as_read(self, usuario_id, notificacion_id): ...  # INotificacionWriter
    def find_by_usuario_id(self, usuario_id): ...  # INotificacionReader
    def count_unread(self, usuario_id): ...         # INotificacionReader

# src/main/frameworks/flask_mvc/routes/notificacion_routes.py
def build_notificacion_service():
    repo = SqlAlchemyNotificacionRepository()
    return NotificacionApplicationService(writer=repo, reader=repo)
```

### 6.4.4 ISP — Interface Segregation Principle

En lugar de un `INotificacionRepository` con 6 métodos, se segregaron dos interfaces especializadas. El ApplicationService las recibe como dependencias separadas; `create_notification` solo usa `writer`, `list_notifications` solo usa `reader`.

```python
# src/main/domain/notificaciones/i_notificacion_writer.py — Solo escritura
class INotificacionWriter(ABC):
    @abstractmethod
    def save(self, notificacion): ...
    @abstractmethod
    def mark_as_read(self, usuario_id, notificacion_id): ...
    @abstractmethod
    def mark_all_as_read(self, usuario_id): ...

# src/main/domain/notificaciones/i_notificacion_reader.py — Solo lectura
class INotificacionReader(ABC):
    @abstractmethod
    def find_by_usuario_id(self, usuario_id): ...
    @abstractmethod
    def find_unread_by_usuario_id(self, usuario_id): ...
    @abstractmethod
    def count_unread(self, usuario_id): ...

# src/main/application/notificacion_application_service.py
class NotificacionApplicationService:
    def __init__(self, writer=None, reader=None):
        self.writer = writer    # solo INotificacionWriter
        self.reader = reader    # solo INotificacionReader

    def create_notification(self, ...):
        self._require_writer()
        return self.writer.save(notificacion)   # solo usa writer

    def list_notifications(self, usuario_id):
        self._require_reader()
        return self.reader.find_by_usuario_id(usuario_id)  # solo usa reader
```

### 6.4.5 DIP — Dependency Inversion Principle

`NotificacionApplicationService` (alta capa) depende de las abstracciones `INotificacionWriter`/`INotificacionReader` definidas en la capa de dominio. `SqlAlchemyNotificacionRepository` (baja capa) también depende de esas mismas abstracciones al implementarlas. La inyección ocurre en las rutas.

```python
# src/main/domain/notificaciones/i_notificacion_writer.py — Abstracción en dominio
class INotificacionWriter(ABC):
    @abstractmethod
    def save(self, notificacion): ...

# src/main/application/notificacion_application_service.py — Alta capa
class NotificacionApplicationService:
    def __init__(self, writer=None, reader=None):
        self.writer = writer  # depende de abstracción, no de concreción
        self.reader = reader

    def create_notification(self, ...):
        self._require_writer()
        return self.writer.save(notificacion)

# src/main/infrastructure/sqlalchemy_notificacion_repository.py — Baja capa
class SqlAlchemyNotificacionRepository(INotificacionWriter, INotificacionReader):
    def save(self, notificacion):
        model = NotificacionModel(
            usuario_destino_id=notificacion.usuario_destino_id,
            tipo=notificacion.tipo,
            mensaje=notificacion.mensaje,
        )
        db.session.add(model)
        db.session.commit()
        return self._to_domain(model)

# src/main/frameworks/flask_mvc/routes/notificacion_routes.py — Inyección
def build_notificacion_service():
    repo = SqlAlchemyNotificacionRepository()                     # concreción
    return NotificacionApplicationService(writer=repo, reader=repo)  # como abstracción
```

## 6.5 Domain-Driven Design (DDD)

### 6.5.1 Entidades

Objetos con identidad propia (`id`) y ciclo de vida. Son mutables y encapsulan reglas de negocio.

```python
# src/main/domain/practica_evaluacion/practica.py
class Practica:
    ESTADO_EN_CURSO = "en_curso"
    ESTADO_FINALIZADA = "finalizada"

    def __init__(self, id=None, postulacion_id=None, practicante_id=None):
        self.id = id
        self.postulacion_id = postulacion_id
        self.practicante_id = practicante_id
        self.estado = self.ESTADO_EN_CURSO
        self.entregables = []
        self.evaluaciones = []

    def finalizar(self):
        if self.estado != self.ESTADO_EN_CURSO:
            raise ValueError("La práctica ya está finalizada")
        self.estado = self.ESTADO_FINALIZADA
```

### 6.5.2 Objetos de Valor

Inmutables, sin identidad, se comparan por su contenido. Encapsulan conceptos pequeños del dominio.

```python
# src/main/domain/perfil/nombre_completo.py
class NombreCompleto:
    def __init__(self, nombres=None, apellidos=None):
        self.nombres = nombres
        self.apellidos = apellidos

    def validar(self):
        if not self.nombres or not self.apellidos:
            raise ValueError("Nombres y apellidos son obligatorios")

    def __str__(self):
        return f"{self.nombres} {self.apellidos}".strip()

# src/main/domain/perfil/ruc.py
class RUC:
    def __init__(self, numero=None):
        self.numero = numero

    def es_valido(self):
        # Algoritmo de módulo 11 de SUNAT
        ...
```

### 6.5.3 Servicios de Dominio

Operaciones que no pertenecen naturalmente a una sola entidad. Son stateless y coordinan varias entidades o value objects.

```python
# src/main/domain/auth/autenticacion_dominio_servicio.py
class AutenticacionDominioServicio:
    def autenticar(self, usuario, password):
        if not usuario or not usuario.esta_activo():
            return False
        return usuario.login(password)

    def generar_token(self, horas_vigencia=24):
        expiracion = datetime.now(timezone.utc) + timedelta(hours=horas_vigencia)
        valor = secrets.token_urlsafe(48)
        return TokenRecuperacion(valor=valor, expiracion=expiracion)
```

### 6.5.4 Agregados y Módulos

El agregado raíz `Practica` encapsula `Entregable` y `Evaluacion` como hijos, garantizando invariantes. Los módulos agrupan conceptos por contexto acotado.

```python
# src/main/domain/practica_evaluacion/practica.py
def subir_entregable(self, archivo):
    entregable = Entregable.crear(practica_id=self.id, archivo=archivo)
    self.entregables.append(entregable)
    return entregable

def registrar_evaluacion(self, puntaje):
    evaluacion = Evaluacion.crear(practica_id=self.id, puntaje=puntaje)
    self.evaluaciones.append(evaluacion)
    return evaluacion
```

```
src/main/domain/          ← Módulos por contexto
├── auth/                ← Autenticación y usuarios
├── convocatorias/       ← Convocatorias y postulaciones
├── perfil/              ← Perfiles de practicante y empresa
├── certificacion/       ← Certificados, QR, PDF
├── practica_evaluacion/ ← Prácticas, entregables, evaluaciones
├── matching/            ← Sugerencias y compatibilidad
└── notificaciones/      ← Notificaciones
```

### 6.5.5 Fábricas

Encapsulan la creación de objetos complejos. Pueden ser clases dedicadas o métodos estáticos.

```python
# src/main/domain/convocatorias/convocatoria_fabrica.py
class ConvocatoriaFabrica:
    def crear_convocatoria(self, empresa_id, titulo, descripcion=None):
        if not empresa_id:
            raise ValueError("La empresa es obligatoria")
        if not titulo or not str(titulo).strip():
            raise ValueError("El título es obligatorio")
        convocatoria = Convocatoria()
        convocatoria.empresa_id = empresa_id
        convocatoria.titulo = str(titulo).strip()
        convocatoria.descripcion = descripcion
        convocatoria.estado = Convocatoria.ESTADO_BORRADOR
        return convocatoria

# src/main/domain/practica_evaluacion/entregable.py — fábrica estática
@staticmethod
def crear(practica_id, archivo):
    if not archivo or not str(archivo).strip():
        raise ValueError("Debe adjuntarse un archivo")
    return Entregable(practica_id=practica_id, archivo=str(archivo).strip())
```

### 6.5.6 Repositorios

Interfaces en el dominio que definen el contrato de persistencia; implementaciones concretas en infraestructura.

```python
# src/main/domain/auth/i_usuario_repository.py
class IUsuarioRepository(ABC):
    @abstractmethod
    def save(self, usuario): ...

    @abstractmethod
    def find_by_email(self, email): ...

    @abstractmethod
    def find_by_id(self, usuario_id): ...

# src/main/infrastructure/sqlalchemy_usuario_repository.py
class SqlAlchemyUsuarioRepository(IUsuarioRepository):
    def save(self, usuario):
        model = UsuarioModel.query.get(usuario.id) if usuario.id else None
        if model is None:
            model = UsuarioModel()
            db.session.add(model)
        model.email = usuario.email
        model.password_hash = usuario.password_hash
        db.session.commit()
        return self._to_domain(model)
```

### 6.5.7 Arquitectura en Capas

Cuatro capas con dependencias hacia adentro: el dominio no conoce infraestructura ni frameworks.

```
src/main/frameworks/    ← Flask, SQLAlchemy, Alembic (configuración, rutas + serialización HTTP)
src/main/application/   ← Application Services (orquestación de casos de uso)
src/main/infrastructure/← Repositorios concretos, email sender
src/main/domain/        ← Entidades, VO, servicios de dominio, interfaces de repositorio
```

Flujo de ejemplo para registrar un usuario:

```
POST /auth/register  (auth_routes.register)
  → UsuarioApplicationService.register_user(...)
    → AutenticacionDominioServicio.generar_password_hash(password)
    → Usuario.registrar()
    → IUsuarioRepository.save(usuario)         ← interfaz
      → SqlAlchemyUsuarioRepository.save(...)  ← implementación
        → db.session (SQLAlchemy)
```

---

# 7. Gestión del Proyecto

## 7.1 Tablero Trello

El seguimiento del proyecto se realizó mediante un tablero basado en la metodología **User Story Mapping**, organizado en Trello.

**URL del tablero:** `https://trello.com/b/OvZDZjiX/sistema-de-practicas-pre-profesionales-verificadas-unsa-2026`

<img width="1856" height="818" alt="TableroTrello-ChambeaYa" src="https://github.com/user-attachments/assets/0502f27f-b8a4-43d3-8807-3707745d04c8" />

## 7.2 Distribución de responsabilidades

| Integrante | Rango asignado | Módulo |
|------------|----------------|--------|
| Omar | 1–5 | Perfil A (Joven) |
| Edú | 6–10 | Perfil A (Joven) |
| Moisés | 1–5 | Perfil B (Empresa) |
| Jhair | 1–6 | Sistema |
| Lorenzo | 6–7 | Perfil B (Empresa) |
| Lorenzo | 1–3 | Product Backlog |
| Roid | 4–8 | Product Backlog |

---

# 8. Tecnologías

| Área | Herramientas |
|------|--------------|
| Lenguaje | Python 3.12 o superior |
| Web | Flask 3, Flask-WTF (CSRF), plantillas Jinja, CSS y JavaScript nativo |
| Persistencia | SQLAlchemy, Flask-SQLAlchemy, Alembic, Flask-Migrate, SQLite |
| Documentos | ReportLab (PDF) y QRCode |
| Dependencias y build | Poetry 2.4.3 |
| Pruebas | pytest, pytest-cov, pytest-html, Selenium WebDriver |
| Calidad | Ruff, SonarQube |
| CI/CD | Jenkins |

---

# 9. Ejecución local

El proyecto requiere **Python 3.12 o superior** y **Poetry 2.4.3**, la versión registrada en `poetry.lock`.

- `.venv` es el entorno de Python del proyecto. Poetry lo crea dentro del repositorio porque `poetry.toml` configura `virtualenvs.in-project = true`.
- `.env` es un archivo distinto: contiene la configuración local de Flask, como la clave secreta y los datos SMTP. No se sube al repositorio.
- Las dependencias se declaran solo en `pyproject.toml`. Si algún entorno exige un `requirements.txt`, se genera en el momento con `poetry export -f requirements.txt -o requirements.txt` (requiere el plugin `poetry-plugin-export`) y no se versiona.

## 9.1 Instalación y arranque

**Windows (PowerShell):**

```powershell
poetry install
Copy-Item .env.example .env
poetry run flask --app frameworks.flask_mvc.app:create_app db upgrade
poetry run flask --app frameworks.flask_mvc.app:create_app run --debug
```

**Linux o macOS:**

```bash
poetry install
cp .env.example .env
poetry run flask --app frameworks.flask_mvc.app:create_app db upgrade
poetry run flask --app frameworks.flask_mvc.app:create_app run --debug
```

La aplicación queda disponible en `http://127.0.0.1:5000`. Para comprobarla:

```bash
curl http://127.0.0.1:5000/health
# {"service":"ChambeaYa","status":"ok"}
```

**Instalar la versión correcta de Poetry.** Comprueba que `poetry --version` muestre exactamente `2.4.3` antes de instalar las dependencias. En Ubuntu, si la versión del sistema es antigua, instala la requerida con pipx y usa su ruta explícita para no seleccionar la de `/usr/bin/poetry`:

```bash
# El sudo se usa solo para instalar pipx desde los paquetes de Ubuntu.
sudo apt install pipx
pipx ensurepath
pipx install "poetry==2.4.3"
~/.local/bin/poetry --version
~/.local/bin/poetry install
```

En Windows y macOS, instala Poetry 2.4.3 siguiendo la [guía oficial de instalación](https://python-poetry.org/docs/#installation).

## 9.2 Modo demo

La demo usa una base SQLite independiente (`instance/chambeaya-demo.db`) con datos precargados. No modifica `chambeaya.db` ni requiere servicios externos.

| Sistema | Iniciar | Reiniciar los datos e iniciar |
|---------|---------|-------------------------------|
| Windows (PowerShell) | `.\demo.ps1` | `.\demo.ps1 -Reset` |
| Linux / macOS | `scripts/demo_reset.sh --no-reset` | `scripts/demo_reset.sh` |

El reinicio elimina únicamente `instance/chambeaya-demo.db`, vuelve a aplicar las migraciones y restaura el escenario inicial. Úsalo antes de presentar si en un ensayo se finalizaron prácticas, se emitieron certificados o se modificaron datos.

En el login aparecen accesos rápidos que completan las credenciales:

| Rol | Correo | Contraseña |
|-----|--------|------------|
| Practicante | `practicante@demo.local` | `Demo1234` |
| Empresa | `empresa@demo.local` | `Demo1234` |

La contraseña sale de la variable `DEMO_PASSWORD`. Los scripts la definen como `Demo1234` si no existe. Si ejecutas `flask seed-demo` a mano, agrega `DEMO_PASSWORD=Demo1234` a tu `.env` (ver `.env.example`).

En modo demo los tokens de activación y recuperación se muestran en pantalla, así que no hace falta configurar correo.

### Recorrido recomendado

**1. Vista pública**

1. Mostrar la landing.
2. Abrir la validación pública de certificados.
3. Explicar el registro separado para practicantes y empresas.

**2. Practicante**

1. En el login, pulsar **Practicante** e ingresar.
2. Mostrar el resumen y el perfil verificado de Andrea Quispe.
3. Explorar las convocatorias publicadas.
4. Abrir **Para ti** para mostrar el matching por habilidades.
5. Mostrar las postulaciones seleccionada y pendiente.
6. Abrir la práctica para enseñar el entregable y la evaluación de 85 puntos.
7. Revisar las notificaciones.
8. Cerrar sesión.

**3. Empresa**

1. En el login, pulsar **Empresa** e ingresar.
2. Mostrar las convocatorias publicadas y el borrador editable.
3. Abrir los candidatos de la convocatoria de calidad.
4. Seleccionar al candidato e iniciar una nueva práctica si se desea.
5. Abrir la práctica backend existente.
6. Finalizarla: ya cuenta con entregable y evaluación aprobada.
7. Emitir el certificado y abrir el PDF y el QR.
8. Cerrar sesión.

**4. Certificado público**

1. Copiar el código emitido.
2. Cerrar sesión.
3. Abrir `/verificar-certificado`.
4. Validar el código para demostrar la consulta pública de integridad.

### Problemas frecuentes

- **El puerto 5000 está ocupado:** detén la otra aplicación con `Ctrl+C`.
- **Cambió el esquema de la base:** vuelve a iniciar la demo con reinicio (`.\demo.ps1 -Reset` o `scripts/demo_reset.sh`).

## 9.3 Verificación de correo (SMTP)

Las cuentas nuevas permanecen en estado `pendiente` hasta que el usuario abre el enlace de activación enviado a su correo. Para usar un servidor SMTP real, configura en `.env`:

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

`APP_URL` debe ser la dirección desde la que el usuario puede abrir la aplicación. Si el correo se abre en otro dispositivo, usa una dirección de red o una URL pública en lugar de `127.0.0.1`.

En los modos `console` y `demo` los tokens pueden exponerse para facilitar las pruebas locales. Ese comportamiento debe permanecer desactivado cuando se envían correos reales.

Para comprobar la conexión después de configurar SMTP:

```bash
poetry run flask --app frameworks.flask_mvc.app:create_app test-email --to tu_correo@gmail.com
```

No uses la contraseña normal de Gmail ni subas el archivo `.env` al repositorio.

---

# 10. Interfaz web

La interfaz está implementada directamente sobre Flask con plantillas Jinja, CSS y JavaScript nativo. No requiere un proceso de compilación adicional.

| Ruta | Vista |
|------|-------|
| `/` | Página de presentación |
| `/ingresar` | Inicio de sesión |
| `/registro` | Registro con confirmación y requisitos de contraseña |
| `/activar` | Activación mediante el enlace enviado al correo, y reenvío |
| `/recuperar` | Solicitud de recuperación de contraseña |
| `/restablecer` | Restablecimiento de contraseña |
| `/verificar-certificado` | Validación pública de certificados |
| `/app` | Aplicación autenticada según el rol |

La ruta `/app` detecta el rol de la sesión y presenta únicamente sus funciones:

- **Practicante:** perfil, oportunidades, sugerencias, postulaciones, prácticas, entregables, evaluaciones, certificados y notificaciones.
- **Empresa:** perfil, convocatorias, candidatos, selección, prácticas, evaluaciones, emisión de certificados y notificaciones.

Las vistas consumen los endpoints de la [API REST](#11-api-rest) con la sesión de Flask. Los errores de validación y de autorización se muestran en contexto, y las acciones incluyen estados de carga, confirmaciones y estados vacíos.

**Diseño.** Paleta sobria de azul profundo y grises fríos, con `#0062fc` como color primario, tomado de la identidad gráfica de ChambeaYa. No usa degradados. Las pantallas priorizan tablas, listas y secciones amplias sobre grupos repetitivos de tarjetas, con navegación adaptable para escritorio, tableta y móvil.

| Archivo | Contenido |
|---------|-----------|
| `src/main/frameworks/flask_mvc/templates/` | Estructura de las vistas |
| `src/main/frameworks/flask_mvc/static/css/app.css` | Sistema visual y responsive |
| `src/main/frameworks/flask_mvc/static/icons.svg` | Iconografía SVG reutilizable |
| `src/main/frameworks/flask_mvc/static/img/` | Logos horizontal y cuadrado |
| `src/main/frameworks/flask_mvc/static/js/common.js` | Utilidades y cliente HTTP |
| `src/main/frameworks/flask_mvc/static/js/app.js` | Interacción de la aplicación |
| `src/main/frameworks/flask_mvc/static/js/auth.js` | Flujos de autenticación |
| `src/main/frameworks/flask_mvc/static/js/verify.js` | Validación de certificados |

---

# 11. API REST

El backend usa Flask, SQLAlchemy y sesiones HTTP. La autenticación usa la cookie de sesión de Flask: las rutas protegidas requieren haber iniciado sesión con `POST /auth/login`. En los ejemplos con `curl`, la cookie se guarda con `-c cookies.txt` y se envía con `-b cookies.txt`.

Las respuestas siguen los códigos descritos en [6.1.5 Restful](#615-restful): 400 validación, 401 sin sesión, 404 no encontrado, 409 conflicto y 503 error de correo.

### Salud

| Método | Ruta | Uso |
|---|---|---|
| GET | `/health` | Comprobar que la aplicación responde |

### Autenticación

| Método | Ruta | Uso |
|---|---|---|
| POST | `/auth/register` | Registrar empresa o practicante |
| POST | `/auth/activate` | Activar la cuenta |
| POST | `/auth/resend-activation` | Reenviar el enlace de activación |
| POST | `/auth/login` | Iniciar sesión |
| GET | `/auth/me` | Consultar el usuario autenticado |
| POST | `/auth/logout` | Cerrar sesión |
| POST | `/auth/recover-password` | Solicitar recuperación de contraseña |
| POST | `/auth/reset-password` | Cambiar la contraseña con un token |

Los tokens (`activation_token`, `password_reset_token`) se incluyen en la respuesta solo cuando `EXPOSE_AUTH_TOKENS=true` (desarrollo, demo y pruebas). Con SMTP, el token llega dentro del enlace enviado al correo.

```bash
# Registro
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"practicante@example.com","password":"Secret123","password_confirmation":"Secret123","tipo":"practicante"}'

# Activación
curl -X POST http://127.0.0.1:5000/auth/activate \
  -H "Content-Type: application/json" \
  -d '{"token":"TOKEN_DE_ACTIVACION"}'

# Reenviar el enlace de activación
curl -X POST http://127.0.0.1:5000/auth/resend-activation \
  -H "Content-Type: application/json" \
  -d '{"email":"practicante@example.com"}'

# Inicio de sesión (guarda la cookie)
curl -X POST http://127.0.0.1:5000/auth/login \
  -c cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"email":"practicante@example.com","password":"Secret123"}'

# Usuario autenticado
curl -b cookies.txt http://127.0.0.1:5000/auth/me

# Cierre de sesión
curl -X POST -b cookies.txt http://127.0.0.1:5000/auth/logout

# Solicitud de recuperación de contraseña
curl -X POST http://127.0.0.1:5000/auth/recover-password \
  -H "Content-Type: application/json" \
  -d '{"email":"practicante@example.com"}'

# Restablecimiento de contraseña
curl -X POST http://127.0.0.1:5000/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token":"TOKEN_DE_RECUPERACION","new_password":"nuevaClave123"}'
```

### Perfiles

| Método | Ruta | Uso |
|---|---|---|
| GET | `/perfil/me` | Obtener el perfil según el tipo de usuario |
| PUT | `/perfil/me` | Crear o actualizar el perfil de practicante |
| PUT | `/perfil/me/empresa` | Crear o actualizar la empresa y validar el RUC |
| POST | `/perfil/me/habilidades` | Añadir una habilidad |
| POST | `/perfil/me/formacion` | Añadir formación educativa |
| POST | `/perfil/me/identidad` | Registrar y verificar DNI o carnet |
| GET | `/perfil/me/reputacion` | Consultar el score de reputación |

```bash
# Perfil del usuario autenticado
curl -b cookies.txt http://127.0.0.1:5000/perfil/me

# Crear o actualizar perfil de practicante
curl -X PUT http://127.0.0.1:5000/perfil/me \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"nombres":"Diego","apellidos":"Perez","habilidades":["Python"],"formacion_educativa":["Ingenieria de Sistemas"]}'

# Agregar habilidad
curl -X POST http://127.0.0.1:5000/perfil/me/habilidades \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"habilidad":"Flask"}'

# Agregar formación educativa
curl -X POST http://127.0.0.1:5000/perfil/me/formacion \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"formacion":"UNSA"}'

# Registrar y verificar identidad
curl -X POST http://127.0.0.1:5000/perfil/me/identidad \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"dni":"12345678","carnet_universitario":"20260001"}'

# Consultar score de reputación
curl -b cookies.txt http://127.0.0.1:5000/perfil/me/reputacion
```

### Convocatorias y matching

| Método | Ruta | Uso |
|---|---|---|
| GET | `/convocatorias?q=python` | Buscar convocatorias publicadas |
| GET | `/convocatorias/<id>` | Ver una convocatoria publicada |
| GET | `/convocatorias/mis` | Listar las convocatorias de la empresa |
| POST | `/convocatorias` | Crear un borrador |
| PUT | `/convocatorias/<id>` | Editar un borrador propio |
| DELETE | `/convocatorias/<id>` | Eliminar un borrador propio |
| POST | `/convocatorias/<id>/publicar` | Publicar un borrador |
| POST | `/convocatorias/<id>/cerrar` | Cerrar una convocatoria |
| POST | `/convocatorias/<id>/reabrir` | Reabrir una convocatoria cerrada (vuelve a publicada) |
| POST | `/convocatorias/<id>/duplicar` | Duplicar como nuevo borrador ("Copia de …") |
| GET | `/matching/sugerencias` | Calcular sugerencias sin persistir |
| POST | `/matching/calcular` | Calcular y guardar sugerencias |

El matching compara habilidades sin distinguir mayúsculas y solo considera convocatorias publicadas.

### Postulaciones

| Método | Ruta | Uso |
|---|---|---|
| POST | `/postulaciones/convocatorias/<id>` | Postular a una convocatoria |
| GET | `/postulaciones/me` | Listar las postulaciones del practicante |
| POST | `/postulaciones/<id>/cancelar` | Retirar una postulación pendiente (practicante) |
| GET | `/postulaciones/convocatorias/<id>` | Listar los candidatos de la empresa |
| POST | `/postulaciones/<id>/seleccionar` | Seleccionar a un candidato |
| POST | `/postulaciones/<id>/rechazar` | Rechazar a un candidato |
| POST | `/postulaciones/<id>/reconsiderar` | Devolver a pendiente una postulación seleccionada o rechazada, si aún no se inició la práctica |

No se permiten postulaciones duplicadas. Al seleccionar a un candidato, las demás postulaciones pendientes de la convocatoria se rechazan.

### Prácticas, entregables y evaluaciones

| Método | Ruta | Uso |
|---|---|---|
| POST | `/practicas` | Iniciar una práctica desde una postulación seleccionada |
| GET | `/practicas` | Listar las prácticas visibles para el usuario |
| GET | `/practicas/<id>` | Consultar una práctica autorizada |
| POST | `/practicas/<id>/entregables` | Subir PDF, DOC, DOCX o ZIP (máx. 10 MB) |
| GET | `/practicas/<id>/entregables` | Historial de entregables |
| GET | `/practicas/<id>/entregables/<id>/archivo` | Descargar un entregable |
| DELETE | `/practicas/<id>/entregables/<id>` | Eliminar un entregable |
| POST | `/practicas/<id>/evaluar` | Registrar una evaluación de 0 a 100 |
| GET | `/practicas/<id>/evaluaciones` | Historial de evaluaciones |
| DELETE | `/practicas/<id>/evaluaciones/<id>` | Eliminar una evaluación (empresa) |
| POST | `/practicas/<id>/finalizar` | Finalizar la práctica |

Para finalizar se exige al menos un entregable y una evaluación aprobada (puntaje mínimo: 60).

```bash
# Subir un entregable (en PowerShell usa curl.exe y ` para continuar la línea)
curl -X POST http://127.0.0.1:5000/practicas/1/entregables \
  -b cookies.txt \
  -F "archivo=@informe.pdf"
```

### Notificaciones y certificados

| Método | Ruta | Uso |
|---|---|---|
| GET | `/notificaciones` | Listar las notificaciones propias |
| GET | `/notificaciones/no-leidas` | Contar las no leídas |
| PUT | `/notificaciones/<id>/leer` | Marcar una notificación propia como leída |
| PUT | `/notificaciones/leer-todas` | Marcar todas como leídas |
| POST | `/certificados/<practica_id>/emitir` | Emitir el certificado |
| GET | `/certificados/practica/<practica_id>` | Consultar un certificado autorizado |
| GET | `/certificados/verificar/<codigo>` | Verificación pública |
| GET | `/certificados/practica/<practica_id>/pdf` | Descargar el PDF |
| GET | `/certificados/<codigo>/qr` | Descargar el QR |

La emisión es idempotente: una práctica tiene como máximo un certificado. La verificación comprueba tanto el QR como la integridad del contenido persistido.

---

# 12. Persistencia y migraciones

- La base SQLite de desarrollo vive en `instance/chambeaya.db`, y la de la demo en `instance/chambeaya-demo.db`.
- Los entregables subidos se guardan en `instance/uploads/entregables`.
- Las claves foráneas de SQLite se habilitan en cada conexión.
- La revisión `9f12c0a8d4e1` completa el esquema de todas las funcionalidades.
- `instance/` está ignorado por Git y no debe versionarse.

El entorno de migraciones está en `src/main/frameworks/migrations`. Ejecuta los comandos desde el entorno Poetry del proyecto:

```bash
# Crear una migración después de modificar modelos
poetry run flask --app frameworks.flask_mvc.app:create_app db migrate -m "descripcion del cambio"

# Aplicar migraciones
poetry run flask --app frameworks.flask_mvc.app:create_app db upgrade

# Revertir la última migración
poetry run flask --app frameworks.flask_mvc.app:create_app db downgrade
```

Para reiniciar la base de desarrollo, detén la aplicación, elimina únicamente `instance/chambeaya.db` y vuelve a ejecutar `db upgrade`.

---

# 13. Pruebas

La suite está en `src/test/` y se divide por capa:

| Carpeta | Tipo | Necesita la app levantada |
|---------|------|---------------------------|
| `domain/`, `application/`, `infrastructure/`, `frameworks/` | Unitarias | No |
| `integration/` | Integración (flujos de negocio con Flask y SQLite en memoria) | No |
| `functional/` | Funcionales de caja negra con Selenium | Sí, en modo demo |

pytest descubre tanto las clases `unittest.TestCase` como las pruebas pytest. Los comandos funcionan igual en PowerShell, Linux y macOS.

**Unitarias e integración** (no requieren navegador ni app):

```sh
poetry run pytest --ignore=src/test/functional
```

**Con cobertura.** El XML lo usa SonarQube; el HTML es para revisarla en el navegador:

```sh
poetry run pytest --ignore=src/test/functional --cov --cov-report=xml --cov-report=html
# reports/coverage.xml y reports/htmlcov/index.html
```

**Funcionales (Selenium).** Primero levanta la [demo](#92-modo-demo) en otra terminal y luego ejecuta:

```sh
poetry run pytest src/test/functional
```

La guía completa de las funcionales (Page Objects, reportes HTML, casos de prueba y cómo usar otra URL) está en [`src/test/functional/README.md`](src/test/functional/README.md).

`poetry run pytest` sin argumentos ejecuta **toda** la suite, funcionales incluidas, así que necesita la demo levantada.

---

# 14. Integración y despliegue continuo (Jenkins)

El `Jenkinsfile` de la raíz define el pipeline. Jenkins lo ejecuta automáticamente cuando detecta cambios en la rama configurada (*Poll SCM*):

| # | Etapa | Qué hace | Si falla |
|---|-------|----------|----------|
| 1 | Build (Poetry) | `poetry install` y `poetry build`. Archiva el wheel | Se detiene |
| 2 | Pruebas unitarias | pytest sin funcionales, con cobertura y reporte JUnit | Se detiene |
| 3 | Análisis SonarQube | `sonar-scanner` con `sonar-project.properties` | Se detiene |
| 4 | Quality Gate | Espera el veredicto de SonarQube (máx. 5 min) | Se detiene |
| 5 | Staging efímero | Instala el wheel en el workspace con BD nueva, en `127.0.0.1:5001` | Se detiene |
| 6 | Pruebas funcionales | Selenium contra staging; luego se apaga staging | Se detiene |
| 7 | Despliegue | Instala el mismo wheel en `$JENKINS_HOME/chambeaya`, en `127.0.0.1:5000` | Rollback automático |

**Despliegue (`scripts/ci/deploy.sh`).** Lo usan staging y el despliegue final:

- Cada versión se instala en `releases/<timestamp>`, y el symlink `current` apunta a la activa. Se conservan la versión activa y la anterior.
- La base de datos persiste entre despliegues: solo se aplican `db upgrade` y `seed-demo` (que es idempotente). Antes de migrar se respalda.
- Si la versión nueva no responde en `/health`, se restauran la versión anterior y su base de datos.
- El servidor corre en modo demo y solo en localhost, porque `ProductionConfig` exige cookies `Secure` (HTTPS).

**Configuración necesaria en Jenkins:**

- Plugins: SonarQube Scanner, JUnit, Pipeline, Workspace Cleanup y Timestamper.
- **Manage Jenkins → System → SonarQube servers:** un servidor llamado `SonarQube`, con la URL de SonarQube y una credencial *Secret text* `sonar-token`.
- **Manage Jenkins → Tools:** un *SonarQube Scanner* llamado `sonar-scanner`.
- **En SonarQube:** un webhook hacia `http://<jenkins>/sonarqube-webhook/`. Si Jenkins y SonarQube corren en la misma máquina, agrega `sonar.validateWebhooks=false` a `conf/sonar.properties`.
- **El job:** *Pipeline script from SCM*, apuntando a este repositorio y a la rama `*/main`, con Script Path `Jenkinsfile`.
