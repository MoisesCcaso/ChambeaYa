# ChambeaYa

Plataforma web para la gestión de prácticas preprofesionales, conectando estudiantes y empresas mediante postulaciones, seguimiento de procesos, recomendaciones basadas en habilidades y certificación digital de prácticas.

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
  - [7.3 Distribución de responsabilidades](#73-distribución-de-responsabilidades)
- [8. Tecnologías](#8-tecnologías)
- [9. Ejecución local](#9-ejecución-local)
- [10. Pruebas](#10-pruebas)
- [11. Migraciones](#11-migraciones)
- [12. Endpoints iniciales](#12-endpoints-iniciales)
- [13. Documentación complementaria](#13-documentación-complementaria)

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
| `Postulacion` | convocatorias | estado (pendiente/seleccionada/rechazada/cancelada) | aceptar(), rechazar(), cancelar(), reactivar(), reconsiderar() |
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
# domain/perfil/ruc.py
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
# domain/matching/matching_dominio_servicio.py
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
| `PracticaFabrica` | `Practica` en estado `EN_CURSO` | postulacion_id y practicante_id obligatorios |

**Fragmento — ConvocatoriaFabrica:**

```python
# domain/convocatorias/convocatoria_fabrica.py
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
# domain/practica_evaluacion/i_practica_repository.py — Interfaz (dominio)
class IPracticaRepository(ABC):
    @abstractmethod
    def save(self, practica): ...
    @abstractmethod
    def find_by_id(self, practica_id): ...
    @abstractmethod
    def find_by_practicante_id(self, practicante_id): ...

# infrastructure/sqlalchemy_practica_repository.py — Implementación
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

El proyecto sigue una arquitectura en 5 capas con la regla de dependencia hacia adentro:

```
┌──────────────────────────────────────────────────────┐
│  frameworks/  (Flask, SQLAlchemy, Alembic)            │
│  ┌──────────────────────────────────────────────────┐ │
│  │  presentation/  (Controllers — adaptadores HTTP) │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │  application/  (Servicios de caso de uso)    │ │ │
│  │  │  ┌──────────────────────────────────────────┐ │ │ │
│  │  │  │  domain/  (Entidades, Value Objects,     │ │ │ │
│  │  │  │            Interfaces de repositorio,    │ │ │ │
│  │  │  │            Servicios de dominio)          │ │ │ │
│  │  │  └──────────────────────────────────────────┘ │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────┘ │
│  infrastructure/  (Repositorios SQLAlchemy, Email)     │
└──────────────────────────────────────────────────────┘
```

**Regla de dependencia:** Las capas externas dependen de las internas, nunca al revés. `frameworks` → `presentation` → `application` → `domain`. `infrastructure` implementa interfaces de `domain`.

---

# 5. Visión General de Arquitectura

## 5.1 Diagrama de Paquetes

<img width="1714" height="932" alt="ChambeaYa - Arquitectura en Capas Flask UML" src="https://github.com/user-attachments/assets/c948c189-1b8a-4f14-9987-f434a5120d74" />

## 5.2 Estructura del Proyecto

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

## 5.3 Clean Architecture / DDD

| Capa | Responsabilidad | Depende de |
|------|----------------|------------|
| **Domain** | Entidades, Value Objects, interfaces de repositorio, servicios de dominio | Nada (capa más interna) |
| **Application** | Casos de uso, orquestación, DTOs | Domain |
| **Infrastructure** | Repositorios concretos, email sender, persistencia | Domain (implementa interfaces) |
| **Presentation** | Controladores HTTP, serialización JSON | Application |
| **Frameworks** | Flask routes, SQLAlchemy ORM, Alembic, config | Presentation + Infrastructure |

La inyección de dependencias ocurre en las **rutas** (frameworks), que construyen los objetos concretos y los pasan como abstracciones a las capas internas.

---

# 6. Prácticas de Desarrollo Aplicadas

## 6.1 Estilos de Programación

### 6.1.1 Things (Cosas / OOP)

Las entidades de dominio encapsulan estado y comportamiento juntos. No son DTOs anémicos — contienen las reglas de negocio que protegen sus invariantes. `Practica` gestiona su ciclo de vida (`EN_CURSO` → `FINALIZADA`) y solo permite transiciones válidas.

```python
# domain/practica_evaluacion/practica.py
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
# application/email_delivery_error.py
class EmailDeliveryError(RuntimeError):
    """Error controlado al entregar un correo transaccional."""

# frameworks/flask_mvc/routes/auth_routes.py
@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    controller = build_usuario_controller()
    try:
        data, status_code = controller.register(payload)
    except EmailDeliveryError as exc:
        return jsonify({"error": str(exc)}), 503
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

# frameworks/flask_mvc/app.py — error global
@app.errorhandler(IntegrityError)
def handle_integrity_error(_error):
    db.session.rollback()
    return jsonify({"error": "El registro ya existe o contiene datos en conflicto"}), 409
```

### 6.1.3 Persistent-Tables (Tablas Persistentes)

Cada modelo ORM hereda de `db.Model` y mapea directamente a una tabla SQL. Las columnas usan tipos explícitos, claves foráneas, unicidad y defaults. Los campos no escalares (listas) se serializan como JSON text.

```python
# frameworks/sqlalchemy_orm/models/practicante_model.py
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

Cada petición cruza tres capas estrictas. **Route** (framework) construye dependencias y recibe HTTP. **Controller** (presentation) serializa/deserializa. **Application Service** orquesta usando servicios de dominio e interfaces de repositorio. Cada capa solo conoce a la inmediata inferior.

```python
# frameworks/flask_mvc/routes/matching_routes.py — Route
@matching_bp.get("/sugerencias")
def suggest_convocatorias():
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        return jsonify({"error": "No autenticado"}), 401
    controller = build_matching_controller()
    data, status_code = controller.suggest_convocatorias(usuario_id)
    return jsonify(data), status_code

def build_matching_controller():
    app_service = MatchingApplicationService(
        SqlAlchemyMatchingRepository(),
        SqlAlchemyPerfilRepository(),
        SqlAlchemyConvocatoriaRepository(),
        MatchingDominioServicio(),
    )
    return MatchingController(app_service)

# presentation/matching_controller.py — Controller
class MatchingController:
    def suggest_convocatorias(self, usuario_id):
        self._require_service()
        resultados = self.matching_application_service.suggest_convocatorias(usuario_id)
        return [self._serialize_resultado(r) for r in resultados], 200

# application/matching_application_service.py — Application Service
class MatchingApplicationService:
    def suggest_convocatorias(self, usuario_id, umbral=50.0):
        self._require_repositories()
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Practicante no encontrado")
        convocatorias = self.convocatoria_repository.find_all()
        return self.matching_servicio.filtrar_convocatorias(practicante, convocatorias, umbral)

# domain/matching/matching_dominio_servicio.py — Domain Service
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
# frameworks/flask_mvc/routes/practica_routes.py
@practica_bp.post("")
def start_practica():
    """POST /practicas — 201: Iniciar práctica"""
    data, status_code = build_practica_controller().start(empresa.id, postulacion_id)
    return jsonify(data), 201

@practica_bp.get("/<int:practica_id>")
def get_practica(practica_id):
    """GET /practicas/<id> — 200: Consultar práctica"""
    data, status_code = build_practica_controller().get_for_user(usuario_id, practica_id)
    return jsonify(data), 200

@practica_bp.post("/<int:practica_id>/evaluar")
def register_evaluation(practica_id):
    """POST /practicas/<id>/evaluar — 201: Registrar evaluación"""
    data, status_code = controller.register_evaluation(empresa.id, practica_id, payload)
    return jsonify(data), 201

@practica_bp.post("/<int:practica_id>/finalizar")
def finish_practica(practica_id):
    """POST /practicas/<id>/finalizar — 200: Finalizar práctica"""
    data, status_code = build_practica_controller().finish(empresa.id, practica_id)
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
# domain/perfil/practicante.py
def agregar_habilidad(self, habilidad):
    habilidad_normalizada = self._normalizar_texto(habilidad)
    if habilidad_normalizada and habilidad_normalizada not in self.habilidades:
        self.habilidades.append(habilidad_normalizada)
    return self
```

### PascalCase para clases

```python
# domain/practica_evaluacion/practica.py
class Practica: ...

# domain/practica_evaluacion/evaluacion.py
class Evaluacion: ...
```

### UPPER_CASE para constantes de dominio

```python
# domain/practica_evaluacion/evaluacion.py
PUNTAJE_APROBACION = 60.0

# domain/notificaciones/notificacion.py
class Notificacion:
    TIPO_POSTULACION_SELECCIONADA = "POSTULACION_SELECCIONADA"
    TIPO_EVALUACION_DISPONIBLE = "EVALUACION_DISPONIBLE"
    TIPO_CERTIFICADO_EMITIDO = "CERTIFICADO_EMITIDO"
    TIPO_NUEVAS_SUGERENCIAS = "NUEVAS_SUGERENCIAS"
```

### Prefijo `_` para métodos privados

```python
# infrastructure/sqlalchemy_convocatoria_repository.py
def _to_convocatoria_domain(self, model): ...
def _dump_list(self, values): ...
def _load_list(self, value): ...
```

### Imports ordenados por capa arquitectónica

```python
# frameworks/flask_mvc/routes/certificado_routes.py
from flask import Blueprint, jsonify, session         # framework

from application.certificacion_application_service import ...  # application
from infrastructure.sqlalchemy_certificado_repository import ...  # infrastructure
from presentation.certificado_controller import ...     # presentation
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
# domain/matching/sugerencia.py
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

Cada función hace una sola cosa. `issue()` del controller solo orquesta; `_serialize()` solo transforma a dict.

```python
# presentation/certificado_controller.py
def issue(self, empresa_id, practica_id):
    self._require_service()
    certificado, creado = self.certificacion_application_service.issue_certificate(
        empresa_id, practica_id
    )
    return self._serialize_certificado(certificado), 201 if creado else 200

def _serialize_certificado(self, certificado):
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
# frameworks/flask_mvc/routes/matching_routes.py
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

Los imports se organizan según la dependencia entre capas: framework → domain → application → infrastructure → presentation.

```python
# frameworks/flask_mvc/routes/postulacion_routes.py
from flask import Blueprint, jsonify, session              # framework

from application.notificacion_application_service import ...  # application
from infrastructure.sqlalchemy_notificacion_repository import ...  # infrastructure
from presentation.postulacion_controller import ...          # presentation
```

### 6.3.5 Objetos con comportamiento (no anémicos)

Las entidades no son simples contenedores de datos; encapsulan validación y lógica de negocio.

```python
# domain/certificacion/archivo_pdf.py
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
# domain/practica_evaluacion/practica.py
def finalizar(self):
    if self.estado != self.ESTADO_EN_CURSO:
        raise ValueError("La práctica ya está finalizada")
    if not self.entregables:
        raise ValueError("No se puede finalizar una práctica sin entregables registrados")
    self.estado = self.ESTADO_FINALIZADA
    return self

# domain/convocatorias/postulacion.py
def cancelar(self):
    if self.estado != self.ESTADO_PENDIENTE:
        raise ValueError("Solo una postulación pendiente puede retirarse")
    self.estado = self.ESTADO_CANCELADA
    return self
```

### 6.3.7 Interfaces segregadas

Interfaces pequeñas y específicas; cada cliente depende solo de los métodos que realmente usa.

```python
# domain/notificaciones/i_notificacion_writer.py
class INotificacionWriter(ABC):
    @abstractmethod
    def save(self, notificacion): ...
    @abstractmethod
    def mark_as_read(self, usuario_id, notificacion_id): ...
    @abstractmethod
    def mark_all_as_read(self, usuario_id): ...

# domain/notificaciones/i_notificacion_reader.py
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

Cada clase tiene una única razón de cambiar. `Notificacion` solo conoce su estado de dominio; `NotificacionController` solo serializa HTTP; `SqlAlchemyNotificacionRepository` solo persiste.

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
        self.leida = True

# presentation/notificacion_controller.py — Solo HTTP
class NotificacionController:
    def list_notifications(self, usuario_id):
        self._require_service()
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

### 6.4.2 OCP — Open/Closed Principle

Para agregar un nuevo tipo de notificación solo se crea una constante en `Notificacion` y se invoca `create_notification()` desde un hook. No se modifica el ApplicationService, Controller ni Repository del módulo de notificaciones.

```python
# domain/notificaciones/notificacion.py — Abierto a extensión
class Notificacion:
    TIPO_POSTULACION_SELECCIONADA = "POSTULACION_SELECCIONADA"
    TIPO_EVALUACION_DISPONIBLE = "EVALUACION_DISPONIBLE"
    TIPO_CERTIFICADO_EMITIDO = "CERTIFICADO_EMITIDO"
    TIPO_NUEVAS_SUGERENCIAS = "NUEVAS_SUGERENCIAS"

# application/notificacion_application_service.py — Cerrado a modificación
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

`SqlAlchemyNotificacionRepository` implementa tanto `INotificacionWriter` como `INotificacionReader`. La misma instancia puede inyectarse en ambos roles sin alterar el comportamiento esperado. Si se creara un `PostgresNotificacionRepository` con las mismas interfaces, podría sustituir al actual sin cambiar el ApplicationService ni el Controller.

```python
# infrastructure/sqlalchemy_notificacion_repository.py
class SqlAlchemyNotificacionRepository(INotificacionWriter, INotificacionReader):
    def save(self, notificacion): ...              # INotificacionWriter
    def mark_as_read(self, usuario_id, notificacion_id): ...  # INotificacionWriter
    def find_by_usuario_id(self, usuario_id): ...  # INotificacionReader
    def count_unread(self, usuario_id): ...         # INotificacionReader

# frameworks/flask_mvc/routes/notificacion_routes.py
def build_notificacion_controller():
    repo = SqlAlchemyNotificacionRepository()
    service = NotificacionApplicationService(writer=repo, reader=repo)
    return NotificacionController(service)
```

### 6.4.4 ISP — Interface Segregation Principle

En lugar de un `INotificacionRepository` con 6 métodos, se segregaron dos interfaces especializadas. El ApplicationService las recibe como dependencias separadas; `create_notification` solo usa `writer`, `list_notifications` solo usa `reader`.

```python
# domain/notificaciones/i_notificacion_writer.py — Solo escritura
class INotificacionWriter(ABC):
    @abstractmethod
    def save(self, notificacion): ...
    @abstractmethod
    def mark_as_read(self, usuario_id, notificacion_id): ...
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
        return self.writer.save(notificacion)   # solo usa writer

    def list_notifications(self, usuario_id):
        self._require_reader()
        return self.reader.find_by_usuario_id(usuario_id)  # solo usa reader
```

### 6.4.5 DIP — Dependency Inversion Principle

`NotificacionApplicationService` (alta capa) depende de las abstracciones `INotificacionWriter`/`INotificacionReader` definidas en la capa de dominio. `SqlAlchemyNotificacionRepository` (baja capa) también depende de esas mismas abstracciones al implementarlas. La inyección ocurre en las rutas.

```python
# domain/notificaciones/i_notificacion_writer.py — Abstracción en dominio
class INotificacionWriter(ABC):
    @abstractmethod
    def save(self, notificacion): ...

# application/notificacion_application_service.py — Alta capa
class NotificacionApplicationService:
    def __init__(self, writer=None, reader=None):
        self.writer = writer  # depende de abstracción, no de concreción
        self.reader = reader

    def create_notification(self, ...):
        self._require_writer()
        return self.writer.save(notificacion)

# infrastructure/sqlalchemy_notificacion_repository.py — Baja capa
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

# frameworks/flask_mvc/routes/notificacion_routes.py — Inyección
def build_notificacion_controller():
    repo = SqlAlchemyNotificacionRepository()                     # concreción
    service = NotificacionApplicationService(writer=repo, reader=repo)  # como abstracción
    return NotificacionController(service)
```

## 6.5 Domain-Driven Design (DDD)

### 6.5.1 Entidades

Objetos con identidad propia (`id`) y ciclo de vida. Son mutables y encapsulan reglas de negocio.

```python
# domain/practica_evaluacion/practica.py
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
# domain/perfil/nombre_completo.py
class NombreCompleto:
    def __init__(self, nombres=None, apellidos=None):
        self.nombres = nombres
        self.apellidos = apellidos

    def validar(self):
        if not self.nombres or not self.apellidos:
            raise ValueError("Nombres y apellidos son obligatorios")

    def __str__(self):
        return f"{self.nombres} {self.apellidos}".strip()

# domain/perfil/ruc.py
class RUC:
    def __init__(self, numero=None):
        self.numero = numero

    def es_valido(self):
        # Algoritmo de módulo 11 de SUNAT
        ...
```

### 6.5.3 Servicios de Dominio

Operaciones que no pertenecen naturalmente a una sola entidad. Son stateless y coordinant varias entidades o value objects.

```python
# domain/auth/autenticacion_dominio_servicio.py
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
# domain/practica_evaluacion/practica.py
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
domain/                  ← Módulos por contexto
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
# domain/convocatorias/convocatoria_fabrica.py
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

# domain/practica_evaluacion/entregable.py — fábrica estática
@staticmethod
def crear(practica_id, archivo):
    if not archivo or not str(archivo).strip():
        raise ValueError("Debe adjuntarse un archivo")
    return Entregable(practica_id=practica_id, archivo=str(archivo).strip())
```

### 6.5.6 Repositorios

Interfaces en el dominio que definen el contrato de persistencia; implementaciones concretas en infraestructura.

```python
# domain/auth/i_usuario_repository.py
class IUsuarioRepository(ABC):
    @abstractmethod
    def save(self, usuario): ...

    @abstractmethod
    def find_by_email(self, email): ...

    @abstractmethod
    def find_by_id(self, usuario_id): ...

# infrastructure/sqlalchemy_usuario_repository.py
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

Cinco capas con dependencias hacia adentro: el dominio no conoce infraestructura ni frameworks.

```
frameworks/    ← Flask, SQLAlchemy, Alembic (configuración, rutas)
presentation/  ← Controllers (serialización HTTP)
application/   ← Application Services (orquestación de casos de uso)
infrastructure/← Repositorios concretos, email sender
domain/        ← Entidades, VO, servicios de dominio, interfaces de repositorio
```

Flujo de ejemplo para registrar un usuario:

```
UsuarioController.register(payload)
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


## 7.3 Distribución de responsabilidades

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

- Python 3.10 o superior
- Flask 3
- SQLAlchemy y Flask-SQLAlchemy
- Alembic y Flask-Migrate
- SQLite
- ReportLab y QRCode

---

# 9. Ejecución local

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

```bash
curl http://127.0.0.1:5000/health
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

```bash
python -m flask --app frameworks.flask_mvc.app:create_app test-email --to tu_correo@gmail.com
```

No utilices la contraseña normal de Gmail ni subas el archivo `.env` al
repositorio.

---

# 10. Pruebas

Ejecutar todas las pruebas desde PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

En Linux o macOS:

```bash
python -m unittest discover -s tests -v
```

El conjunto de pruebas incluye 8 casos de integración que cubren el flujo
completo de negocio: registro, activación, perfiles, convocatorias, matching,
postulaciones, prácticas, entregables, evaluaciones, certificados y
notificaciones.

---

# 11. Migraciones

El entorno de migraciones ya está inicializado en `frameworks/migrations`.

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

---

# 12. Endpoints iniciales

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

---

# 13. Documentación complementaria

- [`BACKEND.md`](BACKEND.md) — Referencia completa de endpoints, flujos de la API y ejemplos
- [`VISTAS.md`](VISTAS.md) — Guía de vistas web, rutas públicas y estructura de la interfaz
- [`DEMO.md`](DEMO.md) — Guía de presentación local con datos precargados y recorrido recomendado
