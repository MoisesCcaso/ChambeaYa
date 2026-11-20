# Informe de Práctica 7: Auditoría Manual de Code Smells y Análisis Estático SonarQube

**Proyecto:** ChambeaYa - Plataforma de Prácticas Profesionales (Flask / Python)  
**Autor:** Jhair  
**Fecha:** 18 de Noviembre de 2026  
**Documento base de referencia:** [.docs/auditoria-manual.md](file:///home/shiarowo/UNSA/IS2/ChambeaYa/.docs/auditoria-manual.md) y [.docs/sonar-reporte.md](file:///home/shiarowo/UNSA/IS2/ChambeaYa/.docs/sonar-reporte.md)

---

## 1. Resumen Ejecutivo y Tabla Comparativa

Este informe consolida los **4 hallazgos manuales más representativos** de diseño orientado a objetos (que SonarQube no detecta) y las **2 incidencias automáticas más críticas** reportadas por SonarQube. El objetivo es evidenciar el contraste entre la detección léxico-mecánica de herramientas automatizadas y el análisis de arquitectura limpia, cohesión y acoplamiento que requiere juicio de diseño de ingeniería de software.

### Tabla Comparativa de los 6 Hallazgos Seleccionados

| N° | Categoría / Origen | N° en Auditoría | Incidencia / Smell | Clasificación (Tipo-Subtipo / Regla) | Módulo / Ubicación | Gravedad | Estrategia de Refactoring / Solución |
|---|---|---|---|---|---|---|---|
| **1** | Manual (Diseño OO) | **N° 2** (D2) | Feature Envy y orquestación en emisión de certificados | Coupler - Feature Envy (SOLID-SRP) | `src/main/frameworks/flask_mvc/routes/certificado_routes.py:58-77` | Alta | *Move Method*: Mover la consulta y notificación a `CertificacionApplicationService.issue_certificate`. |
| **2** | Manual (Diseño OO) | **N° 5** | Interfaz gruesa que mezcla agregados de dominio distintos | SOLID - ISP (Interface Segregation Principle) | `src/main/domain/perfil/i_perfil_repository.py:7-26` | Alta | *Extract Interface*: Dividir en `IPracticanteRepository` e `IEmpresaRepository`. |
| **3** | Manual (Diseño OO) | **N° 6** | Múltiples motivos de cambio en servicio de perfiles | Change Preventer - Divergent Change (SOLID-SRP) | `src/main/application/perfil_application_service.py` | Alta | *Extract Class*: Separar en `PracticanteApplicationService` y `EmpresaApplicationService`. |
| **4** | Manual (Diseño OO) | **N° 7** (R1) | Travesía en cadena a través de agregados ajenos | Coupler - Message Chains (Ley de Demeter) | `src/main/application/practica_application_service.py:114-121` | Alta | *Hide Delegate* / *Move Method*: Crear consulta directa `find_by_empresa_id` en repositorio. |
| **5** | SonarQube (Automático) | **N° 1** | Literal duplicado "Perfil de practicante no encontrado" | Mantenibilidad - python:S1192 | `src/main/application/postulacion_application_service.py:22` | Alta | *Replace Magic Number with Symbolic Constant* / *Replace Error Code with Exception*: Unificar en constante o excepción de dominio. |
| **6** | SonarQube (Automático) | **N° 3** | Complejidad cognitiva alta en autenticación frontend | Mantenibilidad - javascript:S3776 | `src/main/frameworks/flask_mvc/static/js/auth.js:87` | Alta | *Extract Method* / *Decompose Conditional*: Modularizar validación, consumo fetch y renderizado DOM. |

---

## 2. Detalle Exhaustivo de los 4 Code Smells Manuales (Diseño y Arquitectura OO)

---

### **Hallazgo 1 (N° 2 en Auditoría Manual)**

**2. Feature Envy y orquestación en emisión de certificados (Coupler-Feature Envy)**: Tras ejecutar la emisión del certificado, la función de ruta HTTP de Flask consulta múltiples repositorios (`SqlAlchemyPracticaRepository`, `SqlAlchemyPerfilRepository`), navega para obtener el `usuario_id` del practicante, instancia el servicio de notificaciones y despacha el mensaje `CERTIFICADO_EMITIDO`. La ruta depende más de los métodos y datos de `Practica`, `Perfil` y `Notificacion` que de sus propias responsabilidades HTTP. SonarQube no analiza la afinidad de datos ni la fuga de lógica de negocio hacia controladores web.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/routes/certificado_routes.py`, función `issue_certificado` (líneas 58-77)
**Estrategia de Refactoring**: Move Method: mover la lógica de orquestación y envío de notificación al caso de uso `CertificacionApplicationService.issue_certificate`, delegando a un método privado `_notificar_emision`.

#### Diagnóstico del Problema e Impacto
En una arquitectura limpia (Clean Architecture / Hexagonal), la capa de presentación (rutas Flask) debe tener como única responsabilidad recibir la petición HTTP, validar el formato de entrada, llamar a un caso de uso de aplicación y retornar la respuesta JSON correspondiente. 
En `issue_certificado`, la ruta web se convierte en un orquestador que conoce la estructura interna de tres agregados distintos (`Práctica`, `Practicante` y `Notificación`), instanciando infraestructura directamente y gestionando flujos alternativos con `try/except`.

```python
# CÓDIGO ACTUAL (Problemático en certificado_routes.py:58-77)
@certificado_bp.post("/<int:practica_id>/emitir")
def issue_certificado(practica_id):
    # ... validación de sesión y empresa ...
    controller = build_certificado_controller()
    data, status_code = controller.issue(empresa.id, practica_id)

    if status_code == 201:
        try:
            # SMELL: La ruta web coordina 3 repositorios y un servicio ajeno
            practica_repo = SqlAlchemyPracticaRepository()
            practica = practica_repo.find_by_id(practica_id)
            if practica and practica.practicante_id:
                perfil_repo = SqlAlchemyPerfilRepository()
                practicante = perfil_repo.find_practicante_by_id(practica.practicante_id)
                if practicante:
                    repo = SqlAlchemyNotificacionRepository()
                    notif_service = NotificacionApplicationService(writer=repo, reader=repo)
                    notif_service.create_notification(
                        usuario_destino_id=practicante.usuario_id,
                        tipo="CERTIFICADO_EMITIDO",
                        mensaje="Tu certificado digital ha sido emitido",
                        metadata={"practica_id": practica_id},
                    )
        except Exception:
            current_app.logger.exception("No se pudo crear la notificación de certificado emitido")

    return jsonify(data), status_code
```

#### Solución Refactorizada (Antes vs Después)
Aplicando **Move Method**, la coordinación del efecto secundario pasa al servicio de aplicación `CertificacionApplicationService`:

```python
# CÓDIGO REFACTORIZADO: En CertificacionApplicationService
class CertificacionApplicationService:
    def __init__(self, certificado_repository, practica_repository,
                 postulacion_repository, convocatoria_repository,
                 perfil_repository, notificacion_service=None):
        # Inyección de dependencias
        self.notificacion_service = notificacion_service
        # ... demás repositorios ...

    def issue_certificate(self, empresa_id, practica_id):
        # ... validaciones de práctica, convocatoria y practicante ...
        certificado = CertificacionDominioServicio().generar_certificado(
            practica, practicante, convocatoria
        )
        guardado = self.certificado_repository.save(certificado)
        self._notificar_emision(practicante.usuario_id, practica_id)
        return guardado, True

    def _notificar_emision(self, usuario_id, practica_id):
        if self.notificacion_service:
            self.notificacion_service.create_notification(
                usuario_destino_id=usuario_id,
                tipo="CERTIFICADO_EMITIDO",
                mensaje="Tu certificado digital ha sido emitido",
                metadata={"practica_id": practica_id},
            )

# CÓDIGO REFACTORIZADO: En certificado_routes.py (Limpio y cohesivo)
@certificado_bp.post("/<int:practica_id>/emitir")
def issue_certificado(practica_id):
    usuario_id = get_authenticated_user_id()
    if usuario_id is None:
        return jsonify({"error": NO_AUTENTICADO_ERROR}), 401
    empresa = get_authenticated_empresa()
    if empresa is None:
        return jsonify({"error": "Empresa no encontrada para este usuario"}), 400

    data, status_code = build_certificado_controller().issue(empresa.id, practica_id)
    return jsonify(data), status_code
```

---

### **Hallazgo 2 (N° 5 en Auditoría Manual)**

**5. Interfaz gruesa que mezcla agregados de dominio distintos (SOLID-ISP)**: La interfaz `IPerfilRepository` reúne operaciones pertenecientes a dos raíces de agregado conceptualmente distintas: `Practicante` (`save_practicante`, `find_practicante_by_user_id`, `find_practicante_by_id`) y `Empresa` (`save_empresa`, `find_empresa_by_user_id`). Servicios como `PostulacionApplicationService` o `MatchingApplicationService`, que únicamente requieren información del practicante, quedan forzados a depender de un contrato que incluye operaciones de empresa. SonarQube no evalúa la cohesión de métodos dentro de interfaces abstractas.
**Módulo o Componente**: `src/main/domain/perfil/i_perfil_repository.py`, interfaz `IPerfilRepository` (líneas 7-26)
**Estrategia de Refactoring**: Extract Interface: dividir `IPerfilRepository` en dos interfaces segregadas: `IPracticanteRepository` e `IEmpresaRepository`.

#### Diagnóstico del Problema e Impacto
El Principio de Segregación de Interfaces (ISP) establece que ningún cliente debe ser forzado a depender de métodos que no utiliza. En Domain-Driven Design (DDD), `Practicante` y `Empresa` son dos agregados con identidades y tablas independientes (`practicantes` y `empresas`).
Al fusionarlos en `IPerfilRepository`, cualquier cambio en la persistencia de empresas (por ejemplo, añadir campos tributarios de validación SUNAT) fuerza la recompilación y modificación de clases y pruebas que solo gestionan alumnos practicantes.

```python
# CÓDIGO ACTUAL (Violación ISP en i_perfil_repository.py:7-26)
class IPerfilRepository(ABC):
    # Métodos de Practicante
    @abstractmethod
    def save_practicante(self, practicante): pass
    @abstractmethod
    def find_practicante_by_user_id(self, usuario_id): pass
    @abstractmethod
    def find_practicante_by_id(self, practicante_id): pass

    # Métodos de Empresa (Completamente disjuntos)
    @abstractmethod
    def save_empresa(self, empresa): pass
    @abstractmethod
    def find_empresa_by_user_id(self, usuario_id): pass
```

#### Solución Refactorizada (Antes vs Después)
Aplicando **Extract Interface**, se crean dos contratos especializados:

```python
# CÓDIGO REFACTORIZADO: Separación en dos interfaces segregadas
class IPracticanteRepository(ABC):
    @abstractmethod
    def save_practicante(self, practicante): pass
    @abstractmethod
    def find_practicante_by_user_id(self, usuario_id): pass
    @abstractmethod
    def find_practicante_by_id(self, practicante_id): pass

class IEmpresaRepository(ABC):
    @abstractmethod
    def save_empresa(self, empresa): pass
    @abstractmethod
    def find_empresa_by_user_id(self, usuario_id): pass

# En infraestructura, el adaptador SQLAlchemy puede implementar ambas interfaces:
class SqlAlchemyPerfilRepository(IPracticanteRepository, IEmpresaRepository):
    # Implementa los métodos de cada interfaz sin acoplar a los clientes
```

---

### **Hallazgo 3 (N° 6 en Auditoría Manual)**

**6. Múltiples motivos de cambio en servicio de perfiles (Change Preventer-Divergent Change)**: `PerfilApplicationService` gestiona conjuntamente los flujos y reglas de negocio de practicantes (gestión de habilidades, cálculo de score, verificación de identidad con DNI/carnet) y de empresas (validación de RUC SUNAT y razón social). Si cambian las políticas de verificación empresarial o las de reputación académica, la misma clase debe ser modificada. SonarQube no identifica clases con responsabilidades divergentes orientadas a distintos actores.
**Módulo o Componente**: `src/main/application/perfil_application_service.py`, clase `PerfilApplicationService`
**Estrategia de Refactoring**: Extract Class: extraer las responsabilidades en dos servicios independientes: `PracticanteApplicationService` y `EmpresaApplicationService`.

#### Diagnóstico del Problema e Impacto
El smell *Divergent Change* ocurre cuando una clase sufre modificaciones recurrentes debido a razones conceptuales no relacionadas entre sí. 
En `PerfilApplicationService`, convergen dos actores del sistema:
1. El **estudiante/practicante**, cuyo ciclo de vida gira en torno a su reputación, habilidades y validación de matrícula universitaria.
2. La **empresa reclutadora**, cuyo ciclo de vida se rige por razón social, validación de algoritmo de RUC (módulo 11) y estados de verificación jurídica.

```python
# CÓDIGO ACTUAL (Divergent Change en perfil_application_service.py)
class PerfilApplicationService:
    def get_practicante_profile(self, usuario_id): ...
    def update_practicante(self, usuario_id, data): ...
    def add_habilidad(self, usuario_id, habilidad): ...
    def add_formacion(self, usuario_id, formacion): ...
    def register_identity(self, usuario_id, dni=None, carnet_universitario=None): ...
    def verify_profile(self, usuario_id): ...
    def get_reputation_score(self, usuario_id): ...

    # Responsabilidad totalmente distinta:
    def update_empresa(self, usuario_id, data): ...
    def get_empresa_profile(self, usuario_id): ...
```

#### Solución Refactorizada (Antes vs Después)
Aplicando **Extract Class**, se divide la clase en dos servicios de aplicación cohesivos, cada uno con una única responsabilidad (SRP):

```python
# CÓDIGO REFACTORIZADO: Separación por actor de negocio
class PracticanteApplicationService:
    def __init__(self, practicante_repository, usuario_repository):
        self.practicante_repository = practicante_repository
        self.usuario_repository = usuario_repository

    def get_profile(self, usuario_id): ...
    def update_profile(self, usuario_id, data): ...
    def add_habilidad(self, usuario_id, habilidad): ...
    def add_formacion(self, usuario_id, formacion): ...
    def verify_identity(self, usuario_id, dni, carnet): ...
    def get_reputation_score(self, usuario_id): ...

class EmpresaApplicationService:
    def __init__(self, empresa_repository, usuario_repository):
        self.empresa_repository = empresa_repository
        self.usuario_repository = usuario_repository

    def get_profile(self, usuario_id): ...
    def update_profile(self, usuario_id, data): ...
```

---

### **Hallazgo 4 (N° 7 en Auditoría Manual)**

**7. Travesía en cadena a través de agregados ajenos (Coupler-Message Chains)**: En `list_for_user`, el servicio navega manualmente a través de convocatorias, luego por cada postulación y finalmente por cada práctica para resolver las prácticas pertenecientes a una empresa mediante tres bucles anidados. Igualmente, `_require_empresa_owner` navega de práctica a postulación y de postulación a convocatoria. El servicio acopla su lógica a la estructura de relaciones interna de otros agregados violando la Ley de Demeter. SonarQube no analiza travesías de relaciones entre modelos de dominio.
**Módulo o Componente**: `src/main/application/practica_application_service.py`, métodos `list_for_user` (líneas 114-121) y `_require_empresa_owner` (líneas 157-166)
**Estrategia de Refactoring**: Hide Delegate: encapsular la relación proveyendo un método de consulta directo en el repositorio (`find_by_empresa_id`) que resuelva las prácticas asociadas a la empresa mediante una única consulta sin travesías manuales.

#### Diagnóstico del Problema e Impacto
*Message Chains* se produce cuando un cliente navega por una secuencia de objetos intermediarios para obtener los datos deseados (`A -> B -> C -> D`). 
En `practica_application_service.py:114-121`:
```python
# CÓDIGO ACTUAL (Tres bucles anidados navegando agregados ajenos)
practicas = []
for convocatoria in self.convocatoria_repository.find_by_empresa_id(empresa.id):
    for postulacion in self.postulacion_repository.find_by_convocatoria_id(convocatoria.id):
        practica = self.practica_repository.find_by_postulacion_id(postulacion.id)
        if practica is not None:
            practicas.append(practica)
return practicas
```
Este diseño genera dos consecuencias graves:
1. **Acoplamiento estructural:** Si la relación entre postulaciones y convocatorias cambia, el servicio de prácticas se rompe.
2. **Problema de rendimiento N+1:** Si una empresa tiene 10 convocatorias con 15 postulaciones cada una, el método realiza $1 + 10 + 150 = 161$ consultas SQL individuales.

#### Solución Refactorizada (Antes vs Después)
Aplicando **Hide Delegate** y **Move Method**, se delega la consulta al repositorio de infraestructura:

```python
# CÓDIGO REFACTORIZADO: En SqlAlchemyPracticaRepository
class SqlAlchemyPracticaRepository(IPracticaRepository):
    def find_by_empresa_id(self, empresa_id):
        # Una única consulta SQL con JOIN relacional
        return (
            PracticaModel.query
            .join(PostulacionModel, PracticaModel.postulacion_id == PostulacionModel.id)
            .join(ConvocatoriaModel, PostulacionModel.convocatoria_id == ConvocatoriaModel.id)
            .filter(ConvocatoriaModel.empresa_id == empresa_id)
            .all()
        )

# CÓDIGO REFACTORIZADO: En PracticaApplicationService (Sin cadenas de llamadas)
def list_for_user(self, usuario_id):
    self._require_repositories()
    practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
    if practicante is not None:
        return self.practica_repository.find_by_practicante_id(practicante.id)

    empresa = self.perfil_repository.find_empresa_by_user_id(usuario_id)
    if empresa is None:
        raise ValueError("Perfil no encontrado")

    # Delegación directa y limpia
    return self.practica_repository.find_by_empresa_id(empresa.id)
```

---

## 3. Detalle Exhaustivo de las 2 Incidencias SonarQube Más Críticas

---

### **Incidencia SonarQube 1 (N° 1 en Tabla SonarQube)**

**1. Literal duplicado "Perfil de practicante no encontrado" en aplicación (Mantenibilidad-python:S1192)**: El mensaje de error literal `"Perfil de practicante no encontrado"` se encuentra duplicado 3 veces en `postulacion_application_service.py` (líneas 22, 52 y 129) dentro de las validaciones de postulación, listado y cancelación, aumentando el riesgo de inconsistencias tipográficas en validaciones y mensajes propagados hacia la capa de presentación.
**Módulo o Componente**: `src/main/application/postulacion_application_service.py`, métodos `apply`, `list_for_practicante` y `cancel` (líneas 22, 52, 129)
**Estrategia de Refactoring**: Replace Magic Number with Symbolic Constant / Replace Error Code with Exception: definir una constante a nivel de módulo `NOT_FOUND_PRACTICANTE = "Perfil de practicante no encontrado"` o implementar una excepción especializada de dominio (`PerfilPracticanteNoEncontradoError`).

#### Riesgo Técnico e Impacto (python:S1192: String literals should not be duplicated)
SonarQube cataloga esta regla como severidad **HIGH** bajo la dimensión de **MAINTAINABILITY**. La duplicación de literales de cadena ("Magic Strings") para el control de flujo o excepciones genera una dispersión de contratos de error. Si en el futuro se decide modificar la redacción del mensaje para internacionalización (i18n), alineamiento con la UI o personalización por rol, cualquier omisión manual provocará que métodos como `apply`, `list_for_practicante` o `cancel` respondan con mensajes discordantes ante el mismo error semántico de dominio.

```python
# CÓDIGO ACTUAL (postulacion_application_service.py)
def apply(self, usuario_id, convocatoria_id):
    practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
    if practicante is None:
        raise ValueError("Perfil de practicante no encontrado")  # <-- Línea 22

def list_for_practicante(self, usuario_id):
    practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
    if practicante is None:
        raise ValueError("Perfil de practicante no encontrado")  # <-- Línea 52

def cancel(self, usuario_id, postulacion_id):
    practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
    if practicante is None:
        raise ValueError("Perfil de practicante no encontrado")  # <-- Línea 129
```

#### Solución y Refactorización
```python
# CÓDIGO REFACTORIZADO (Extracción de constante simbólica o excepción de dominio)
NOT_FOUND_PRACTICANTE = "Perfil de practicante no encontrado"

# O alternativamente definiendo una excepción especializada de dominio:
class PerfilPracticanteNoEncontradoError(ValueError):
    def __init__(self, message=NOT_FOUND_PRACTICANTE):
        super().__init__(message)
```

---

### **Incidencia SonarQube 2 (N° 3 en Tabla SonarQube)**

**3. Complejidad cognitiva alta en autenticación frontend (Mantenibilidad-javascript:S3776)**: La función de manejo de autenticación en `auth.js` acumula una complejidad cognitiva de 23 puntos (superando el límite de 15 fijado por SonarQube). Concentra en un solo bloque el procesamiento del submit, la validación de campos, la gestión de estados de interfaz, el consumo de la API REST mediante fetch y el enrutamiento posterior.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/static/js/auth.js`, función de gestión de formulario de autenticación (línea 87)
**Estrategia de Refactoring**: Extract Method: descomponer la función en subfunciones especializadas (`validateAuthForm`, `submitAuthRequest`, `handleAuthResponse`, `displayAuthErrors`) reduciendo las estructuras de control anidadas.

#### Diagnóstico del Problema de Mantenibilidad
La complejidad cognitiva mide qué tan difícil es para un desarrollador humano comprender el flujo de control mental de una unidad de código. A diferencia de la complejidad ciclomática (que solo cuenta bifurcaciones matemáticas), la complejidad cognitiva penaliza fuertemente el **anidamiento** (`callbacks`, promesas anidadas dentro de condicionales dentro de escuchadores de eventos).
En `auth.js:87`, la función centraliza:
- Captura del evento submit y preventDefault.
- Múltiples condiciones `if (!email) ... if (!password)`.
- Bloques `try/catch` encadenados con peticiones `fetch`.
- Desempaquetado manual de respuestas JSON con ternarios para status codes 200, 400 y 401.
- Manipulación directa del DOM para inyectar textos de error.

#### Solución Refactorizada (Antes vs Después)
Aplicando **Extract Method** y **Decompose Conditional**, la función principal se reduce a un coordinador lineal con complejidad cognitiva menor a 5:

```javascript
// CÓDIGO REFACTORIZADO EN auth.js
async function handleAuthSubmit(event) {
    event.preventDefault();
    const credentials = getFormCredentials();

    const validationError = validateCredentials(credentials);
    if (validationError) {
        showErrorMessage(validationError);
        return;
    }

    try {
        setLoadingState(true);
        const user = await authenticateApi(credentials);
        redirectUserByRole(user.tipo);
    } catch (error) {
        showErrorMessage(error.message);
    } finally {
        setLoadingState(false);
    }
}
```

---

## 4. Conclusiones y Comparativa Metodológica

1. **Complementariedad Indispensable**:
   SonarQube es sumamente efectivo detectando vulnerabilidades puntuales (`python:S6437`, contraseñas en código), errores de configuración (`python:S4830`, TLS) y métricas de complejidad cognitiva (`javascript:S3776`). Sin embargo, **es completamente ciego ante violaciones de diseño arquitectónico**, como ubicar orquestación de negocio dentro de una ruta HTTP (*Feature Envy*), agrupar agregados distintos en un repositorio (*violación de ISP*), o navegar estructuras ajenas (*Message Chains*).

2. **Impacto en el Ciclo de Vida del Software**:
   Los defectos señalados por SonarQube suelen ser fáciles de corregir de forma aislada (cambiar una variable, extraer un método en un archivo JS). Por el contrario, los *code smells* de diseño manual identificados (N° 2, N° 5, N° 6 y N° 7) afectan la modularidad global, la capacidad de realizar pruebas unitarias con dobles de prueba y el costo a largo plazo de añadir nuevas funcionalidades al sistema ChambeaYa.

3. **Recomendación para el Equipo de Desarrollo**:
   Se recomienda adoptar linters y SonarQube como primera barrera de control de calidad sintáctico y de seguridad básica en la integración continua (CI), complementándolo mandatoriamente con revisiones de código por pares (*Peer Code Reviews*) enfocadas en principios SOLID, límites de agregados DDD y desacoplamiento entre capas.


---

## 5. Tarjetas de Trello para Backlog de Refactorización y Deuda Técnica

A continuación se presenta el contenido estructurado de las **6 tarjetas de Trello** listas para integrarse en el tablero Kanban/Scrum del proyecto (columnas sugeridas: *Product Backlog* → *Sprint Backlog* → *In Progress* → *Peer Review / Testing* → *Done*).

---

### Tarjeta 1: [REFACTOR-OO] Mover orquestación de notificaciones fuera de la ruta de certificados
- **Etiquetas**: `Refactoring`, `Backend`, `Clean Architecture`, `Coupler`, `SOLID-SRP`
- **Prioridad**: Alta
- **Story Points (Estimación)**: 3 SP
- **Descripción**:
  La función de ruta HTTP `issue_certificado` en `src/main/frameworks/flask_mvc/routes/certificado_routes.py:58-77` incurre en *Feature Envy* y viola el principio de responsabilidad única (SRP). Tras emitir el certificado, la ruta consulta manualmente `SqlAlchemyPracticaRepository`, `SqlAlchemyPerfilRepository`, extrae el `usuario_id` del practicante, instancia `SqlAlchemyNotificacionRepository` y `NotificacionApplicationService`, y envía la notificación `CERTIFICADO_EMITIDO`.
  La capa web debe limitarse a recibir HTTP y delegar a la capa de aplicación.
- **Estrategia de Refactoring**:
  *Move Method* (refactoring.guru): Trasladar la coordinación de la notificación hacia `CertificacionApplicationService.issue_certificate`, llamando a un método privado `_notificar_emision`.
- **Criterios de Aceptación (Checklist)**:
  - [x] Inyectar `notificacion_service` opcional en `CertificacionApplicationService.__init__`.
  - [x] Mover la consulta de practicante y la creación de notificación a `_notificar_emision` dentro de `CertificacionApplicationService`.
  - [x] Simplificar `issue_certificado` en `certificado_routes.py` para que solo invoque al controlador/servicio y retorne `jsonify(data), status_code`.
  - [x] Eliminar la instanciación directa de repositorios y servicios de notificación dentro de `certificado_routes.py`.
  - [x] Ejecutar pruebas unitarias de emisión de certificados (`pytest src/test/domain/` y `src/test/application/`) asegurando que pasen sin regresión.

---

### Tarjeta 2: [SOLID-ISP] Segregar interfaz IPerfilRepository en Practicante y Empresa
- **Etiquetas**: `SOLID`, `Refactoring`, `Domain`, `Architecture`, `ISP`
- **Prioridad**: Alta
- **Story Points (Estimación)**: 5 SP
- **Descripción**:
  La interfaz `IPerfilRepository` en `src/main/domain/perfil/i_perfil_repository.py:7-26` agrupa en un solo contrato operaciones pertenecientes a dos raíces de agregados DDD disjuntas: `Practicante` (`save_practicante`, `find_practicante_by_user_id`, `find_practicante_by_id`) y `Empresa` (`save_empresa`, `find_empresa_by_user_id`).
  Esto viola el Principio de Segregación de Interfaces (ISP), forzando a servicios que solo interactúan con practicantes (como `PostulacionApplicationService` y `MatchingApplicationService`) a depender de operaciones de empresas.
- **Estrategia de Refactoring**:
  *Extract Interface* (refactoring.guru): Dividir `IPerfilRepository` en dos interfaces cohesivas e independientes: `IPracticanteRepository` e `IEmpresaRepository`.
- **Criterios de Aceptación (Checklist)**:
  - [ ] Crear la interfaz abstracta `IPracticanteRepository` en `domain/perfil/` con las operaciones exclusivas de practicantes.
  - [ ] Crear la interfaz abstracta `IEmpresaRepository` en `domain/perfil/` con las operaciones exclusivas de empresas.
  - [ ] Actualizar el adaptador `SqlAlchemyPerfilRepository` en `infrastructure/` para que implemente ambas interfaces explícitamente (`class SqlAlchemyPerfilRepository(IPracticanteRepository, IEmpresaRepository)`).
  - [ ] Actualizar firmas y dependencias de `PostulacionApplicationService`, `MatchingApplicationService` y `PracticaApplicationService` para que dependan únicamente de `IPracticanteRepository`.
  - [ ] Validar que todos los tests de perfiles y servicios dependientes sigan pasando exitosamente.

---

### Tarjeta 3: [SOLID-SRP] Extraer PerfilApplicationService en servicios especializados por actor
- **Etiquetas**: `Refactoring`, `Application`, `Change Preventer`, `SOLID-SRP`
- **Prioridad**: Alta
- **Story Points (Estimación)**: 5 SP
- **Descripción**:
  La clase `PerfilApplicationService` en `src/main/application/perfil_application_service.py` sufre del code smell *Divergent Change* y viola el principio de responsabilidad única (SRP). Administra reglas de negocio para dos actores con ciclos de vida y requerimientos totalmente independientes: estudiantes practicantes (habilidades, cálculo de reputación académica, validación de matrícula) y empresas (validación de RUC con algoritmo módulo 11 de SUNAT y razón social). Cualquier cambio en las políticas de un actor obliga a editar la clase compartida.
- **Estrategia de Refactoring**:
  *Extract Class* (refactoring.guru): Separar la clase monolítica en dos servicios de aplicación dedicados: `PracticanteApplicationService` y `EmpresaApplicationService`.
- **Criterios de Aceptación (Checklist)**:
  - [ ] Crear la clase `PracticanteApplicationService` con métodos de perfil, habilidades, educación, identidad y score de reputación.
  - [ ] Crear la clase `EmpresaApplicationService` con métodos de perfil empresarial y validación de RUC.
  - [ ] Ajustar la inyección de repositorios segregados (`IPracticanteRepository` e `IEmpresaRepository`) en cada nuevo servicio.
  - [ ] Actualizar `perfil_routes.py` y `perfil_controller.py` para instanciar y delegar al servicio correspondiente según la ruta.
  - [ ] Ejecutar la suite de pruebas unitarias de aplicación para verificar que no haya regresiones.

---

### Tarjeta 4: [REFACTOR-PERF] Eliminar Message Chains en consulta de prácticas de empresa
- **Etiquetas**: `Refactoring`, `Performance`, `Backend`, `Coupler`, `Database`
- **Prioridad**: Alta
- **Story Points (Estimación)**: 3 SP
- **Descripción**:
  En `src/main/application/practica_application_service.py:114-121`, el método `list_for_user` implementa 3 bucles anidados navegando manualmente a través de convocatorias, postulaciones y prácticas:
  `for convocatoria in convocatorias: for postulacion in postulaciones: practica = find_by_postulacion_id(...)`.
  Esto viola la Ley de Demeter (*Message Chains*), acopla el servicio a la jerarquía relacional de agregados ajenos y genera un grave problema de rendimiento con $N+1$ consultas SQL.
- **Estrategia de Refactoring**:
  *Hide Delegate* / *Move Method* (refactoring.guru): Crear un método de consulta directo `find_by_empresa_id` en `IPracticaRepository` implementado mediante una única consulta con `JOIN` en `SqlAlchemyPracticaRepository`.
- **Criterios de Aceptación (Checklist)**:
  - [ ] Definir el método `find_by_empresa_id(empresa_id)` en la interfaz `IPracticaRepository`.
  - [ ] Implementar la consulta optimizada con `JOIN` relacional entre `PracticaModel`, `PostulacionModel` y `ConvocatoriaModel` en `SqlAlchemyPracticaRepository`.
  - [ ] Reemplazar los 3 bucles anidados en `PracticaApplicationService.list_for_user` por una única llamada a `self.practica_repository.find_by_empresa_id(empresa.id)`.
  - [ ] Refactorizar de manera idéntica la comprobación de pertenencia en `_require_empresa_owner` (líneas 157-166).
  - [ ] Verificar mediante pruebas unitarias de persistencia que la lista de prácticas devuelta sea idéntica y eficiente.

---

### Tarjeta 5: [MAINTAINABILITY] Eliminar literal duplicado "Perfil de practicante no encontrado"
- **Etiquetas**: `Mantenibilidad`, `SonarQube`, `Code Smell`, `python:S1192`, `Backend`, `Application`
- **Prioridad**: Alta
- **Story Points (Estimación)**: 2 SP
- **Descripción**:
  SonarQube reporta la incidencia `python:S1192` (Maintainability - High) en `src/main/application/postulacion_application_service.py:22` debido a la duplicación de la cadena literal `"Perfil de practicante no encontrado"` en 3 métodos del servicio (`apply`, `list_for_practicante` y `cancel`). El uso repetido de cadenas mágicas dispersa los contratos de error de dominio e incrementa el riesgo de desincronización tipográfica.
- **Estrategia de Mitigación / Refactoring**:
  *Replace Magic Number with Symbolic Constant* / *Replace Error Code with Exception*: Unificar el mensaje en una constante simbólica compartida a nivel de módulo (`NOT_FOUND_PRACTICANTE = "Perfil de practicante no encontrado"`) o reemplazar la excepción genérica `ValueError` por una excepción especializada del modelo de dominio (`PerfilPracticanteNoEncontradoError`).
- **Criterios de Aceptación (Checklist)**:
  - [ ] Definir la constante simbólica `NOT_FOUND_PRACTICANTE` o la clase de excepción `PerfilPracticanteNoEncontradoError`.
  - [ ] Reemplazar las 3 apariciones literales de `"Perfil de practicante no encontrado"` en `apply` (línea 22), `list_for_practicante` (línea 52) y `cancel` (línea 129).
  - [ ] Verificar que los controladores y rutas que capturan o exponen el mensaje sigan recibiendo el texto esperado.
  - [ ] Ejecutar las pruebas unitarias de postulación (`pytest src/test/application/test_postulacion_service.py`) y verificar que pasen al 100%.
  - [ ] Comprobar que SonarQube no marque advertencias `python:S1192` en este servicio.

---

### Tarjeta 6: [FRONTEND] Reducir complejidad cognitiva y modularizar auth.js
- **Etiquetas**: `Frontend`, `JavaScript`, `SonarQube`, `Mantenibilidad`, `javascript:S3776`
- **Prioridad**: Media
- **Story Points (Estimación)**: 3 SP
- **Descripción**:
  SonarQube reporta la incidencia `javascript:S3776` (Maintainability - High) en `src/main/frameworks/flask_mvc/static/js/auth.js:87`, con una complejidad cognitiva de 23 puntos frente al umbral máximo permitido de 15.
  La función de autenticación maneja en un único bloque monolítico la captura del evento, validación de inputs, promesas `fetch` asíncronas, ramas condicionales anidadas por código HTTP y renderizado de errores en el DOM.
- **Estrategia de Refactoring**:
  *Extract Method* / *Decompose Conditional* (refactoring.guru): Modularizar la función principal extrayendo la lectura de datos, la validación de credenciales, la llamada a la API y el manejo de respuestas en funciones puras y reutilizables.
- **Criterios de Aceptación (Checklist)**:
  - [ ] Extraer la función `getFormCredentials(form)` para lectura de campos del DOM.
  - [ ] Extraer la función pura `validateCredentials(credentials)` para validación de formato y obligatoriedad.
  - [ ] Extraer la función asíncrona `authenticateApi(credentials)` para aislamiento de la llamada `fetch`.
  - [ ] Extraer la función `showErrorMessage(message)` para actualización visual del DOM.
  - [ ] Reestructurar la función principal como un orquestador lineal con retornos tempranos (*Guard Clauses*), reduciendo la complejidad cognitiva por debajo de 10 puntos.
  - [ ] Verificar manualmente el flujo de inicio de sesión y registro en el navegador para comprobar que la interfaz responda idénticamente.


  ===================================================


    ChambeaYa es una plataforma web desarrollada en Python (Flask) diseñada para la gestión integral  
  del ciclo de vida de prácticas preprofesionales y profesionales, conectando a
  estudiantes/egresados universitarios con empresas reclutadoras.
  
  ### 1. Propósito
  
  Centralizar y agilizar el encuentro laboral entre practicantes y empresas, cubriendo desde la     
  publicación de ofertas hasta la acreditación formal de la práctica mediante certificados digitales
  verificables.
  ──────
  ### 2. Roles Principales
  
  • Practicante (Estudiante / Egresado): Gestiona su perfil académico, habilidades y formación,     
  recibe recomendaciones de convocatorias por compatibilidad (matching), postula a ofertas, sube    
  entregables periódicos y consulta/descarga sus certificados con código QR.
  • Empresa: Valida su identidad jurídica (RUC/SUNAT), publica y administra convocatorias, evalúa y 
  selecciona postulantes, califica entregables y emite certificados digitales al finalizar la       
  práctica.
  ──────
  ### 3. Módulos y Funcionalidades Clave
  
  1. Autenticación y Seguridad (auth): Registro, login, activación de cuenta vía email y            
  recuperación de contraseñas.
  2. Perfiles e Identidad (perfil): Validación de identidad (DNI/Carnet universitario para alumnos, 
  RUC para empresas) y cálculo de score de reputación.
  3. Convocatorias y Postulaciones (convocatorias): Ciclo de vida de convocatorias (borrador,      
  publicada, cerrada) y flujo de selección/rechazo de postulantes.
  4. Sistema de Matching (matching): Algoritmo que calcula el porcentaje de compatibilidad entre las
  habilidades del postulante y los requisitos de las vacantes.
  5. Seguimiento y Evaluación (practica_evaluacion): Gestión de entregables (archivos PDF/ZIP), 
  registro de evaluaciones y finalización formal de la práctica.
  6. Certificación Digital (certificacion): Generación de certificados en PDF y códigos QR para
  verificación pública de autenticidad e integridad.
  7. Notificaciones (notificaciones): Avisos automáticos ante eventos (postulación seleccionada,    
  evaluación disponible, emisión de certificado).
  ──────
  ### 4. Arquitectura y Tecnologías 
  
  • Backend: Python 3, Flask, SQLAlchemy ORM, SQLite. 
  • Arquitectura: Inspirada en Clean Architecture / Domain-Driven Design (DDD) por capas: 
      • Dominio: Entidades, Value Objects y Servicios de dominio puros.
      • Aplicación: Casos de uso y orquestación.
      • Presentación: Blueprints y rutas Flask.
      • Infraestructura: Repositorios SQLAlchemy y envío de correos SMTP.

