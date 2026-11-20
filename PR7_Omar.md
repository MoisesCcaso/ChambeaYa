# Informe de Práctica 7: Auditoría Manual de Code Smells y Análisis Estático SonarQube

**Proyecto:** ChambeaYa - Plataforma de Prácticas Profesionales (Flask / Python)  
**Autor:** Omar Joaquín Rivera Olivera  
**Fecha:** 20 de Noviembre de 2026  
**Documento base de referencia:** [.docs/13-issues_por_resolver_chambeaya.md](.docs/13-issues_por_resolver_chambeaya.md) y [.docs/sonar-reporte.md](.docs/sonar-reporte.md)

---

## 1. Resumen Ejecutivo y Tablas para el Informe Grupal

Este informe consolida los **4 hallazgos manuales de diseño orientado a objetos** (N° 13, 14, 15 y 16 del catálogo de 24 code smells) y las **2 incidencias de accesibilidad detectadas por SonarQube** (N° 7 y 8 del catálogo de 12 incidencias). Mientras SonarQube identifica fallos sintácticos y semánticos en plantillas HTML (`Web:S6853`, `Web:S5255`), la revisión manual permite localizar violaciones estructurales de Clean Architecture, inversión de dependencias (DIP), obsesión primitiva, clases de datos anémicas y duplicación algorítmica en persistencia.

### Tabla Comparativa de los 6 Hallazgos Seleccionados

| N° | Categoría / Origen | N° en Auditoría | Incidencia / Smell | Clasificación (Tipo-Subtipo / Regla) | Módulo / Ubicación | Gravedad | Estrategia de Refactoring / Solución |
|---|---|---|---|---|---|---|---|
| **1** | Manual (Diseño OO) | **N° 13** | Contenedor de datos anémico y redundante (`ResultadoMatching`) | Dispensable - Data Class | `src/main/domain/matching/resultado_matching.py:1-11` | Media | *Move Method* / *Inline Class*: Mover `es_compatible` a `Sugerencia` y simplificar `MatchingDominioServicio`. |
| **2** | Manual (Diseño OO) | **N° 14** | Bolsas de datos genéricas no tipadas en servicios de aplicación | Bloater - Primitive Obsession | `src/main/application/convocatoria_application_service.py:10, 33` y servicios de perfil (`practicante_application_service.py`, `empresa_application_service.py`) | Media | *Introduce Parameter Object*: Sustituir `data: dict` por DTOs / Command Objects explícitos. |
| **3** | Manual (Diseño OO) | **N° 15** | Duplicación algorítmica en sincronización de modelos ORM | Dispensable - Duplicate Code | `src/main/infrastructure/sqlalchemy_practica_repository.py:29-64` | Media | *Extract Method*: Parametrizar la sincronización de colecciones hijas en `_sync_collection`. |
| **4** | Manual (Diseño OO) | **N° 16** | Acoplamiento de entidades de dominio a rutas HTTP de infraestructura | SOLID - DIP | `src/main/domain/certificacion/archivo_pdf.py:16`, `src/main/domain/certificacion/codigo_qr.py:14` | Media | *Move Method*: Extraer la construcción de URLs HTTP hacia la capa de presentación/aplicación. |
| **5** | SonarQube (Automático) | **N° 7** | Etiqueta `<label>` sin control de formulario asociado | Accesibilidad - `Web:S6853` | `src/main/frameworks/flask_mvc/templates/app.html:185` | Media | Asociación explícita `for="opportunity-search"` vinculando `<label>` con `<input id="opportunity-search">`. |
| **6** | SonarQube (Automático) | **N° 8** | Falta de atributos `aria-label` en controles y paneles `<aside>` | Accesibilidad - `Web:S5255` | `src/main/frameworks/flask_mvc/templates/app.html:13, 115, 138, 189` | Media | Incorporar atributos `aria-label` descriptivos en los 4 contenedores `<aside>`. |

---

### Filas Listas para el Informe Grupal (`Pr07_Refactoring_TDD.pdf`)

#### Para la Sección 3.3 — Reporte consolidado de Issues SonarQube

| N° | Categoría | Descripción | Módulo o Componente | Responsable | Prioridad | Estrategia de Refactoring |
|---|---|---|---|---|---|---|
| 7 | Accesibilidad - `Web:S6853` | Etiqueta `<label>` sin control de formulario asociado explícitamente | `src/main/frameworks/flask_mvc/templates/app.html:185` | Omar Joaquín Rivera Olivera | Media | Añadir el atributo `for="opportunity-search"` a la etiqueta `<label class="search-field">` para asociarla explícitamente al elemento `<input id="opportunity-search">`. |
| 8 | Accesibilidad - `Web:S5255` | Contenedores `<aside>` sin atributos `aria-label` o `aria-labelledby` | `src/main/frameworks/flask_mvc/templates/app.html:13, 115, 138, 189` | Omar Joaquín Rivera Olivera | Media | Incorporar atributos `aria-label` descriptivos en los cuatro paneles `<aside>` (`#sidebar`, `#dashboard-progress`, `#profile-summary`, `#opportunity-detail`). |

#### Para la Sección 3.4 — Reporte consolidado de Issues Manuales

| N° | Categoría | Descripción | Módulo o Componente | Responsable | Prioridad | Estrategia de Refactoring |
|---|---|---|---|---|---|---|
| 13 | Dispensable - Data Class | Contenedor de datos anémico y redundante (`ResultadoMatching`) | `src/main/domain/matching/resultado_matching.py:1-11` | Omar Joaquín Rivera Olivera | Media | *Move Method* / *Inline Class*: mover el método `es_compatible` a la entidad `Sugerencia` y simplificar `MatchingDominioServicio` evitando la redundancia del contenedor anémico. |
| 14 | Bloater - Primitive Obsession | Bolsas de datos genéricas no tipadas (`data: dict`) en servicios de aplicación | `src/main/application/convocatoria_application_service.py`, `practicante_application_service.py`, `empresa_application_service.py` | Omar Joaquín Rivera Olivera | Media | *Introduce Parameter Object*: encapsular los diccionarios dinámicos en objetos de transferencia de datos (DTO / Command Objects) explícitos (`CrearConvocatoriaCommand`, `ActualizarConvocatoriaCommand`, `ActualizarPracticanteDTO`, `ActualizarEmpresaDTO`). |
| 15 | Dispensable - Duplicate Code | Duplicación algorítmica en sincronización de modelos ORM (`entregables` y `evaluaciones`) | `src/main/infrastructure/sqlalchemy_practica_repository.py:29-64` | Omar Joaquín Rivera Olivera | Media | *Extract Method*: parametrizar la lógica repetida de eliminación de huérfanos e inserción de nuevos elementos en un método auxiliar `_sync_collection`. |
| 16 | SOLID - DIP | Acoplamiento de entidades de dominio a rutas HTTP de infraestructura | `src/main/domain/certificacion/archivo_pdf.py:16`, `src/main/domain/certificacion/codigo_qr.py:14` | Omar Joaquín Rivera Olivera | Media | *Move Method*: extraer la construcción de rutas web (`/certificados/practica/.../pdf` y `/certificados/verificar/...`) fuera del dominio hacia la capa de presentación/presentadores. |

---

## 2. Detalle Exhaustivo de los 4 Code Smells Manuales (Diseño y Arquitectura OO)

---

### **Hallazgo 1 (N° 13 en Auditoría Manual)**

**13. Contenedor de datos anémico y redundante (Dispensable-Data Class)**: La clase `ResultadoMatching` actúa como un simple contenedor de atributos (`score_compatibilidad`, `practicante_id`, `convocatoria_id`, `sugerencia`, `convocatoria`) que duplica los datos ya contenidos en `Sugerencia` y `Convocatoria`, contando con un único método de una línea (`es_compatible`). Carece de comportamiento sustancial. SonarQube no marca clases de datos con atributos y un método básico como código problemático.  
**Módulo o Componente**: `src/main/domain/matching/resultado_matching.py`, clase `ResultadoMatching` (líneas 1-11)  
**Estrategia de Refactoring**: *Move Method* / *Inline Class*: mover el método `es_compatible` a la entidad `Sugerencia` y simplificar la estructura eliminando el contenedor redundante.

#### Diagnóstico del Problema e Impacto
`ResultadoMatching` repite tres valores ya presentes en `Sugerencia` (`puntaje_match`, `practicante_id`, `convocatoria_id`) y envuelve una referencia a `Sugerencia` y `Convocatoria` solo para exponer `es_compatible(umbral=50.0)`. En `MatchingDominioServicio.filtrar_convocatorias`, `MatchingApplicationService.calculate_for_practicante` y `matching_routes.serialize_resultado`, los consumidores navegan por `resultado.sugerencia.habilidades_coincidentes` y `resultado.convocatoria.titulo`, lo que demuestra que `Sugerencia` (enlazando o recibiendo `convocatoria`) es la entidad que debe poseer la regla `es_compatible`.

```python
# CÓDIGO ACTUAL (ANTES — src/main/domain/matching/resultado_matching.py:1-11)
class ResultadoMatching:
    def __init__(self, score_compatibilidad=0.0, practicante_id=None,
                 convocatoria_id=None, sugerencia=None, convocatoria=None):
        self.score_compatibilidad = score_compatibilidad
        self.practicante_id = practicante_id
        self.convocatoria_id = convocatoria_id
        self.sugerencia = sugerencia
        self.convocatoria = convocatoria

    def es_compatible(self, umbral=50.0):
        return self.score_compatibilidad >= umbral
```

#### Solución Refactorizada (Antes vs Después)
Aplicando **Move Method** e **Inline Class**, se traslada `es_compatible(umbral=50.0)` a `Sugerencia` y se elimina la redundancia de `ResultadoMatching` en `MatchingDominioServicio`, `MatchingApplicationService` y `matching_routes` (manteniendo compatibilidad controlada si alguna prueba existente requiere transición gradual):

```python
# CÓDIGO REFACTORIZADO (DESPUÉS — src/main/domain/matching/sugerencia.py)
class Sugerencia:
    def __init__(self, id=None, practicante_id=None, convocatoria_id=None,
                 puntaje_match=None, habilidades_coincidentes=None, convocatoria=None):
        self.id = id
        self.practicante_id = practicante_id
        self.convocatoria_id = convocatoria_id
        self.puntaje_match = puntaje_match or 0.0
        self.habilidades_coincidentes = habilidades_coincidentes or []
        self.convocatoria = convocatoria

    def es_compatible(self, umbral=50.0):
        return self.puntaje_match >= umbral
```

---

### **Hallazgo 2 (N° 14 en Auditoría Manual)**

**14. Bolsas de datos genéricas no tipadas en servicios de aplicación (Bloater-Primitive Obsession)**: Métodos clave de casos de uso como `ConvocatoriaApplicationService.create_convocatoria`, `update` y `PracticanteApplicationService.update_practicante` / `EmpresaApplicationService.update_empresa` (antes reunidos en `PerfilApplicationService`) reciben un argumento genérico `data: dict` sin estructura formal. Esto oscurece el contrato de entrada, exige extracciones manuales `.get("...")` dispersas y traslada el riesgo de errores tipográficos o valores faltantes al interior del servicio. SonarQube no detecta el uso de primitivos dinámicos en fronteras de casos de uso.  
**Módulo o Componente**: `src/main/application/convocatoria_application_service.py` (líneas 10, 33), `src/main/application/practicante_application_service.py` (línea 22) y `src/main/application/empresa_application_service.py` (línea 16)  
**Estrategia de Refactoring**: *Introduce Parameter Object*: sustituir el diccionario sin tipar por objetos de transferencia de datos (DTO / Command Objects) explícitos como `ConvocatoriaCommand`, `ActualizarPracticanteDTO` y `ActualizarEmpresaDTO`.

#### Diagnóstico del Problema e Impacto
Al recibir `data` como un `dict` arbitrario, la firma del método no documenta qué campos son obligatorios u opcionales, obliga a repetir `data.get("...")` y mezcla la validación de presencia de claves (`"dni" in data`) dentro del caso de uso.

```python
# CÓDIGO ACTUAL (ANTES — src/main/application/convocatoria_application_service.py:10-42)
    def create_convocatoria(self, empresa_id, data):
        self._require_repository()
        titulo = data.get("titulo")
        descripcion = data.get("descripcion")
        habilidades_requeridas = data.get("habilidades_requeridas")
        beneficios = data.get("beneficios")
        convocatoria = self.convocatoria_fabrica.crear_convocatoria(
            empresa_id, titulo, descripcion=descripcion,
            habilidades_requeridas=habilidades_requeridas, beneficios=beneficios
        )
        return self.convocatoria_repository.save(convocatoria)

    def update(self, empresa_id, convocatoria_id, data):
        self._require_repository()
        convocatoria = self._find_owned(empresa_id, convocatoria_id)
        convocatoria.actualizar(
            titulo=data.get("titulo"),
            descripcion=data.get("descripcion"),
            habilidades_requeridas=data.get("habilidades_requeridas"),
            beneficios=data.get("beneficios"),
        )
        return self.convocatoria_repository.save(convocatoria)
```

#### Solución Refactorizada (Antes vs Después)
Aplicando **Introduce Parameter Object**, se introducen `@dataclass` explícitos con conversión controlada `from_dict` en la frontera del controlador/servicio:

```python
# CÓDIGO REFACTORIZADO (DESPUÉS — DTOs / Command Objects tipados)
from dataclasses import dataclass
from typing import Optional

_UNSET = object()

@dataclass(frozen=True)
class ConvocatoriaCommand:
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    habilidades_requeridas: Optional[list] = None
    beneficios: Optional[list] = None

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, cls):
            return data
        payload = data or {}
        return cls(
            titulo=payload.get("titulo"),
            descripcion=payload.get("descripcion"),
            habilidades_requeridas=payload.get("habilidades_requeridas"),
            beneficios=payload.get("beneficios"),
        )

@dataclass(frozen=True)
class ActualizarPracticanteDTO:
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    dni: object = _UNSET
    carnet_universitario: object = _UNSET
    habilidades: object = _UNSET
    formacion_educativa: object = _UNSET
```

---

### **Hallazgo 3 (N° 15 en Auditoría Manual)**

**15. Duplicación algorítmica en sincronización de modelos ORM (Dispensable-Duplicate Code)**: En `SqlAlchemyPracticaRepository.save`, el algoritmo para sincronizar colecciones hijas con la base de datos (obtener IDs actuales, eliminar huérfanos de la relación y agregar nuevos registros no existentes) está implementado de manera idéntica y consecutiva para `entregables` y para `evaluaciones`. Aunque operan sobre tipos distintos, la lógica y estructura algorítmica son idénticas. SonarQube solo detecta duplicación literal exacta de tokens de código, no duplicación conceptual o algorítmica.  
**Módulo o Componente**: `src/main/infrastructure/sqlalchemy_practica_repository.py`, método `save` (líneas 29-64)  
**Estrategia de Refactoring**: *Extract Method*: parametrizar la lógica de sincronización de colecciones en una función auxiliar genérica `_sync_collection(model_collection, domain_collection, mapper_func)`.

#### Diagnóstico del Problema e Impacto
Cualquier cambio en la estrategia de sincronización de hijos ORM (por ejemplo, actualización de campos existentes o reglas de borrado lógico) exige modificar dos bloques paralelos manualmente, arriesgando divergencias entre `entregables` y `evaluaciones`.

```python
# CÓDIGO ACTUAL (ANTES — src/main/infrastructure/sqlalchemy_practica_repository.py:29-64)
        ids_entregables_actuales = {
            entregable.id
            for entregable in practica.entregables
            if entregable.id is not None
        }
        for entregable_model in list(model.entregables):
            if entregable_model.id not in ids_entregables_actuales:
                model.entregables.remove(entregable_model)

        ids_existentes = {e.id for e in model.entregables}
        for entregable in practica.entregables:
            if entregable.id in ids_existentes:
                continue
            model.entregables.append(EntregableModel(
                archivo=entregable.archivo,
                fecha_subida=entregable.fecha_subida,
            ))

        ids_evaluaciones_actuales = {
            evaluacion.id
            for evaluacion in practica.evaluaciones
            if evaluacion.id is not None
        }
        for evaluacion_model in list(model.evaluaciones):
            if evaluacion_model.id not in ids_evaluaciones_actuales:
                model.evaluaciones.remove(evaluacion_model)

        ids_evaluaciones_existentes = {e.id for e in model.evaluaciones}
        for evaluacion in practica.evaluaciones:
            if evaluacion.id in ids_evaluaciones_existentes:
                continue
            model.evaluaciones.append(EvaluacionModel(
                puntaje=evaluacion.puntaje,
                fecha_evaluacion=evaluacion.fecha_evaluacion,
            ))
```

#### Solución Refactorizada (Antes vs Después)
Aplicando **Extract Method**, se unifica la sincronización en `_sync_collection`:

```python
# CÓDIGO REFACTORIZADO (DESPUÉS — src/main/infrastructure/sqlalchemy_practica_repository.py)
        self._sync_collection(
            model.entregables,
            practica.entregables,
            lambda item: EntregableModel(
                archivo=item.archivo,
                fecha_subida=item.fecha_subida,
            ),
        )
        self._sync_collection(
            model.evaluaciones,
            practica.evaluaciones,
            lambda item: EvaluacionModel(
                puntaje=item.puntaje,
                fecha_evaluacion=item.fecha_evaluacion,
            ),
        )

    def _sync_collection(self, model_collection, domain_collection, mapper_func):
        ids_actuales = {
            item.id for item in domain_collection if item.id is not None
        }
        for item_model in list(model_collection):
            if item_model.id not in ids_actuales:
                model_collection.remove(item_model)

        ids_existentes = {item_model.id for item_model in model_collection}
        for item in domain_collection:
            if item.id in ids_existentes:
                continue
            model_collection.append(mapper_func(item))
```

---

### **Hallazgo 4 (N° 16 en Auditoría Manual)**

**16. Acoplamiento de entidades de dominio a rutas HTTP de infraestructura (SOLID-DIP)**: Las entidades `ArchivoPDF` y `CodigoQR` generan dentro de su propia lógica de dominio cadenas de texto que corresponden a rutas de endpoints web de presentación (`url = f"/certificados/practica/{practica_id}/pdf"` y `url_verificacion = f"/certificados/verificar/{valor}"`). Esto invierte el flujo de dependencias de Clean Architecture, acoplando el núcleo del dominio a convenciones de ruteo HTTP. SonarQube no detecta semántica de URLs dentro de atributos de dominio.  
**Módulo o Componente**: `src/main/domain/certificacion/archivo_pdf.py` (línea 16) y `src/main/domain/certificacion/codigo_qr.py` (línea 14)  
**Estrategia de Refactoring**: *Move Method*: extraer la construcción de URLs hacia la capa de presentación o servicios de infraestructura dedicados a generar enlaces web.

#### Diagnóstico del Problema e Impacto
Si los endpoints del blueprint `certificado_bp` cambian de prefijo o se exponen mediante otro adaptador (por ejemplo, API v2 o CLI), las entidades puras de dominio quedarían obsoletas o requerirían cambios por motivos ajenos a las reglas de negocio de certificación. Además, `certificado_routes.serialize_certificado` ya construye la ruta `"imagen_url": f"/certificados/{certificado.codigo_qr.valor}/qr"` en la capa web, evidenciando que todas las URLs HTTP pertenecen a la capa de infraestructura/presentación.

```python
# CÓDIGO ACTUAL (ANTES — archivo_pdf.py:16 y codigo_qr.py:14)
class ArchivoPDF:
    @staticmethod
    def crear(practica_id, contenido):
        if not contenido:
            raise ValueError("Debe proveerse el contenido del PDF para generar el archivo")
        contenido_bytes = contenido.encode() if isinstance(contenido, str) else contenido
        url = f"/certificados/practica/{practica_id}/pdf"
        hash_integridad = hashlib.sha256(contenido_bytes).hexdigest()
        return ArchivoPDF(
            url=url,
            hash_integridad=hash_integridad,
            contenido=contenido_bytes.decode("utf-8"),
        )

class CodigoQR:
    @staticmethod
    def generar(practica_id):
        valor = f"CERT-{practica_id}-{uuid4().hex[:8]}"
        url_verificacion = f"/certificados/verificar/{valor}"
        hash_integridad = hashlib.sha256(valor.encode()).hexdigest()
        return CodigoQR(valor=valor, url_verificacion=url_verificacion, hash_integridad=hash_integridad)
```

#### Solución Refactorizada (Antes vs Después)
Aplicando **Move Method**, las entidades de dominio generan únicamente identidad/integridad pura sin rutas HTTP codificadas, y `certificado_routes.serialize_certificado` / `SqlAlchemyCertificadoRepository` resuelven las URLs de acceso HTTP:

```python
# CÓDIGO REFACTORIZADO (DESPUÉS — dominio desacoplado de URLs + construcción en rutas/infraestructura)
class ArchivoPDF:
    @staticmethod
    def crear(practica_id, contenido, url=None):
        if not contenido:
            raise ValueError("Debe proveerse el contenido del PDF para generar el archivo")
        contenido_bytes = contenido.encode() if isinstance(contenido, str) else contenido
        hash_integridad = hashlib.sha256(contenido_bytes).hexdigest()
        return ArchivoPDF(
            url=url,
            hash_integridad=hash_integridad,
            contenido=contenido_bytes.decode("utf-8"),
        )

class CodigoQR:
    @staticmethod
    def generar(practica_id, url_verificacion=None):
        valor = f"CERT-{practica_id}-{uuid4().hex[:8]}"
        hash_integridad = hashlib.sha256(valor.encode()).hexdigest()
        return CodigoQR(valor=valor, url_verificacion=url_verificacion, hash_integridad=hash_integridad)

# En certificado_routes.serialize_certificado y SqlAlchemyCertificadoRepository.save:
# "url_verificacion": certificado.codigo_qr.url_verificacion or f"/certificados/verificar/{certificado.codigo_qr.valor}"
# "url": certificado.documento.url or f"/certificados/practica/{certificado.practica_id}/pdf"
```

---

## 3. Detalle Exhaustivo de las 2 Incidencias SonarQube (Accesibilidad Web)

---

### **Incidencia SonarQube 1 (N° 7 en Catálogo SonarQube — `Web:S6853`)**

**7. Etiqueta `<label>` sin control de formulario asociado (`Accesibilidad - Web:S6853`)**: En la barra de búsqueda de la vista de oportunidades en `app.html:185`, el elemento `<label class="search-field">` contiene un `<svg>` decorativo seguido del `<input id="opportunity-search">`, pero carece de atributo `for` explícito vinculado al identificador del control de entrada.  
**Módulo o Componente**: `src/main/frameworks/flask_mvc/templates/app.html`, línea 185  
**Estrategia de Refactoring**: Añadir explícitamente `for="opportunity-search"` a la etiqueta `<label class="search-field">` y mantener un vínculo unívoco con `<input id="opportunity-search">`.

```html
<!-- CÓDIGO ACTUAL (ANTES — app.html:185) -->
<label class="search-field"><svg class="icon" aria-hidden="true"><use href="{{ url_for('static', filename='icons.svg') }}#icon-search"></use></svg><input id="opportunity-search" type="search" placeholder="Buscar por puesto o habilidad"></label>
```

```html
<!-- CÓDIGO REFACTORIZADO (DESPUÉS — app.html:185) -->
<label class="search-field" for="opportunity-search"><svg class="icon" aria-hidden="true"><use href="{{ url_for('static', filename='icons.svg') }}#icon-search"></use></svg><input id="opportunity-search" type="search" placeholder="Buscar por puesto o habilidad"></label>
```

---

### **Incidencia SonarQube 2 (N° 8 en Catálogo SonarQube — `Web:S5255`)**

**8. Falta de atributos `aria-label` en contenedores y paneles `<aside>` (`Accesibilidad - Web:S5255`)**: La plantilla `app.html` define cuatro elementos landmark `<aside>` (líneas 13, 115, 138 y 189) sin `aria-label` ni `aria-labelledby`. Para usuarios de tecnologías asistivas y lectores de pantalla, tener múltiples regiones complementarias (`complementary` / `<aside>`) sin etiqueta diferenciadora impide identificar cada panel.  
**Módulo o Componente**: `src/main/frameworks/flask_mvc/templates/app.html`, líneas 13, 115, 138 y 189  
**Estrategia de Refactoring**: Incorporar atributos `aria-label` descriptivos en cada uno de los cuatro `<aside>`.

```html
<!-- CÓDIGO ACTUAL (ANTES — app.html:13, 115, 138, 189) -->
<aside class="sidebar" id="sidebar">
...
<aside class="progress-panel" id="dashboard-progress"></aside>
...
<aside class="profile-summary" id="profile-summary"></aside>
...
<aside class="detail-panel" id="opportunity-detail">
```

```html
<!-- CÓDIGO REFACTORIZADO (DESPUÉS — app.html:13, 115, 138, 189) -->
<aside class="sidebar" id="sidebar" aria-label="Menú lateral">
...
<aside class="progress-panel" id="dashboard-progress" aria-label="Progreso del perfil"></aside>
...
<aside class="profile-summary" id="profile-summary" aria-label="Resumen de perfil"></aside>
...
<aside class="detail-panel" id="opportunity-detail" aria-label="Detalle de convocatoria">
```

---

## 4. Conclusiones y Comparativa Metodológica

1. **Detección semántica vs. análisis estructural**: SonarQube localiza con precisión reglas concretas de accesibilidad HTML (`Web:S6853`, `Web:S5255`), pero no detecta cuando una clase de dominio está vacía de comportamiento (`ResultadoMatching`), cuando un parámetro `dict` oculta contratos (`Primitive Obsession`), cuando dos algoritmos ORM replican la misma sincronización (`Duplicate Code`) ni cuando el dominio construye rutas HTTP (`SOLID-DIP`).
2. **Beneficio directo en mantenibilidad y pruebas**: Al eliminar `Data Class`, introducir DTOs explícitos, extraer `_sync_collection` y desacoplar URLs del dominio, los casos de uso se vuelven más predecibles, fáciles de probar con dobles unitarios y respetuosos de la dirección de dependencias de Clean Architecture.

---

## 5. Tarjetas para GitHub Issues y Tablero Kanban (`PRACT07-Refactoring (IS2)`)

A continuación se detalla el contenido estructurado de las **6 tarjetas** siguiendo exactamente la convención de títulos, descripción, estrategia de refactoring, checklist y ramas del tablero `PRACT07-Refactoring (IS2)`:

---

### Tarjeta 1 (Manual 13 — Issue [#179](https://github.com/MoisesCcaso/ChambeaYa/issues/179))
- **Issue**: `#179` (https://github.com/MoisesCcaso/ChambeaYa/issues/179)
- **Título**: `[DATA-CLASS] Eliminar contenedor de datos anémico ResultadoMatching moviendo comportamiento a Sugerencia`
- **Rama**: `refactor(pract7)/issue-179-data-class-resultado-matching`
- **Etiquetas**: `Refactoring`, `Domain`, `Dispensable`, `Data Class`
- **Prioridad**: Media
- **Descripción**:
  La clase `ResultadoMatching` en `src/main/domain/matching/resultado_matching.py:1-11` actúa como una *Data Class* anémica que duplica campos ya existentes en `Sugerencia` y `Convocatoria`, aportando únicamente el método `es_compatible(umbral=50.0)`.
- **Estrategia de Refactoring**:
  *Move Method* / *Inline Class* (refactoring.guru): Mover `es_compatible` hacia `Sugerencia` y simplificar `MatchingDominioServicio` y sus consumidores eliminando la redundancia del contenedor intermedio.
- **Criterios de Aceptación (Checklist)**:
  - [x] Mover el método `es_compatible(umbral=50.0)` y la referencia opcional de `convocatoria` a `Sugerencia` (`src/main/domain/matching/sugerencia.py`).
  - [x] Actualizar `MatchingDominioServicio` para trabajar directamente con `Sugerencia` y eliminar la dependencia innecesaria a `ResultadoMatching`.
  - [x] Actualizar `matching_routes` y `MatchingApplicationService` para consumir `Sugerencia` de forma cohesiva.
  - [x] Actualizar/ampliar pruebas unitarias en `src/test/domain/test_matching_domain.py` y `src/test/application/test_matching_service.py` y validar que pasen al 100%.

---

### Tarjeta 2 (Manual 14 — Issue [#180](https://github.com/MoisesCcaso/ChambeaYa/issues/180))
- **Issue**: `#180` (https://github.com/MoisesCcaso/ChambeaYa/issues/180)
- **Título**: `[PRIMITIVE-OBSESSION] Reemplazar diccionarios genéricos por Parameter Objects (DTOs) en servicios de aplicación`
- **Rama**: `refactor(pract7)/issue-180-parameter-object-dtos`
- **Etiquetas**: `Refactoring`, `Application`, `Bloater`, `Primitive Obsession`
- **Prioridad**: Media
- **Descripción**:
  Los casos de uso `ConvocatoriaApplicationService.create_convocatoria`, `ConvocatoriaApplicationService.update`, `PracticanteApplicationService.update_practicante` y `EmpresaApplicationService.update_empresa` reciben bolsas genéricas `data: dict` sin tipado formal, dispersando `.get(...)` y ocultando el contrato de entrada.
- **Estrategia de Refactoring**:
  *Introduce Parameter Object* (refactoring.guru): Definir DTOs / Command Objects explícitos (`ConvocatoriaCommand`, `ActualizarPracticanteDTO`, `ActualizarEmpresaDTO`) y adaptarlos en los servicios de aplicación.
- **Criterios de Aceptación (Checklist)**:
  - [x] Definir DTOs / Command Objects tipados (`ConvocatoriaCommand`, `ActualizarPracticanteDTO`, `ActualizarEmpresaDTO`) con conversión segura desde `dict`.
  - [x] Refactorizar `ConvocatoriaApplicationService`, `PracticanteApplicationService` y `EmpresaApplicationService` para operar sobre dichos objetos tipados (conservando compatibilidad si reciben `dict` en fronteras HTTP).
  - [x] Garantizar compatibilidad transparente con las rutas de `convocatoria_routes.py` y `perfil_routes.py`.
  - [x] Agregar pruebas unitarias para validar los DTOs y confirmar que las suites de convocatoria y perfil pasen sin regresiones.

---

### Tarjeta 3 (Manual 15 — Issue [#181](https://github.com/MoisesCcaso/ChambeaYa/issues/181))
- **Issue**: `#181` (https://github.com/MoisesCcaso/ChambeaYa/issues/181)
- **Título**: `[DUPLICATE-CODE] Extraer método genérico _sync_collection en SqlAlchemyPracticaRepository`
- **Rama**: `refactor(pract7)/issue-181-extract-sync-collection-practica`
- **Etiquetas**: `Refactoring`, `Infrastructure`, `Dispensable`, `Duplicate Code`
- **Prioridad**: Media
- **Descripción**:
  En `src/main/infrastructure/sqlalchemy_practica_repository.py:29-64`, `SqlAlchemyPracticaRepository.save` repite exactamente el mismo algoritmo de sincronización de colecciones hijas (eliminación de huérfanos e inserción de nuevos registros) para `entregables` y `evaluaciones`.
- **Estrategia de Refactoring**:
  *Extract Method* (refactoring.guru): Extraer un método auxiliar privado `_sync_collection(model_collection, domain_collection, mapper_func)` que unifique la lógica de sincronización.
- **Criterios de Aceptación (Checklist)**:
  - [x] Implementar `_sync_collection(self, model_collection, domain_collection, mapper_func)` en `SqlAlchemyPracticaRepository`.
  - [x] Reemplazar los dos bloques repetidos en `SqlAlchemyPracticaRepository.save` por llamadas a `_sync_collection`.
  - [x] Verificar mediante `src/test/infrastructure/test_practica_repository.py` (y pruebas unitarias específicas) que la adición y eliminación de entregables y evaluaciones se comporta de forma idéntica.

---

### Tarjeta 4 (Manual 16 — Issue [#182](https://github.com/MoisesCcaso/ChambeaYa/issues/182))
- **Issue**: `#182` (https://github.com/MoisesCcaso/ChambeaYa/issues/182)
- **Título**: `[SOLID-DIP] Desacoplar rutas HTTP de las entidades de dominio ArchivoPDF y CodigoQR`
- **Rama**: `refactor(pract7)/issue-182-dip-certificacion-urls`
- **Etiquetas**: `SOLID`, `DIP`, `Domain`, `Refactoring`, `Clean Architecture`
- **Prioridad**: Media
- **Descripción**:
  En `src/main/domain/certificacion/archivo_pdf.py:16` y `src/main/domain/certificacion/codigo_qr.py:14`, las entidades de dominio construyen URLs de rutas HTTP de Flask (`/certificados/practica/{id}/pdf` y `/certificados/verificar/{valor}`), violando el Principio de Inversión de Dependencias (DIP) y acoplando el dominio a la capa web.
- **Estrategia de Refactoring**:
  *Move Method* (refactoring.guru): Retirar la generación hardcodeada de rutas HTTP fuera de `ArchivoPDF.crear` y `CodigoQR.generar`, trasladando la construcción de rutas web a `certificado_routes.serialize_certificado` y `SqlAlchemyCertificadoRepository`.
- **Criterios de Aceptación (Checklist)**:
  - [x] Modificar `ArchivoPDF.crear` y `CodigoQR.generar` para que no construyan rutas HTTP acopladas al router web (aceptando `url` / `url_verificacion` opcionales desde fuera o dejándolas en `None` en el dominio puro).
  - [x] Mover la construcción de las URLs HTTP hacia `certificado_routes.serialize_certificado` y `SqlAlchemyCertificadoRepository.save`.
  - [x] Ajustar `SqlAlchemyCertificadoRepository` si es necesario cuando persiste/reconstruye documentos sin URL hardcodeada.
  - [x] Actualizar y ejecutar las pruebas unitarias en `src/test/domain/test_certificacion_domain.py`, `src/test/application/test_certificacion_service.py` y `src/test/infrastructure/test_certificado_repository.py`.

---

### Tarjeta 5 (SonarQube 7 — Issue [#183](https://github.com/MoisesCcaso/ChambeaYa/issues/183))
- **Issue**: `#183` (https://github.com/MoisesCcaso/ChambeaYa/issues/183)
- **Título**: `[ACCESSIBILITY] Asociar etiqueta label con control de formulario en app.html (Web:S6853)`
- **Rama**: `fix(pract7)/issue-183-label-for-app-html`
- **Etiquetas**: `Accesibilidad`, `SonarQube`, `Frontend`, `Web:S6853`
- **Prioridad**: Media
- **Descripción**:
  SonarQube reporta la regla `Web:S6853` en `src/main/frameworks/flask_mvc/templates/app.html:185`, donde la etiqueta `<label class="search-field">` carece de atributo `for` asociado explícitamente al control `<input id="opportunity-search">`.
- **Estrategia de Refactoring**:
  Añadir el atributo `for="opportunity-search"` a la etiqueta `<label>` vinculándola explícitamente al identificador del campo de búsqueda.
- **Criterios de Aceptación (Checklist)**:
  - [x] Agregar `for="opportunity-search"` al elemento `<label class="search-field">` en `src/main/frameworks/flask_mvc/templates/app.html:185`.
  - [x] Verificar con pruebas unitarias/validación HTML que el atributo `for` coincide exactamente con el `id` del `<input>` correspondiente.
  - [x] Confirmar que no se introducen regresiones en la interfaz ni en las pruebas existentes.

---

### Tarjeta 6 (SonarQube 8 — Issue [#184](https://github.com/MoisesCcaso/ChambeaYa/issues/184))
- **Issue**: `#184` (https://github.com/MoisesCcaso/ChambeaYa/issues/184)
- **Título**: `[ACCESSIBILITY] Agregar atributos aria-label a contenedores y paneles en app.html (Web:S5255)`
- **Rama**: `fix(pract7)/issue-184-aria-label-app-html`
- **Etiquetas**: `Accesibilidad`, `SonarQube`, `Frontend`, `Web:S5255`
- **Prioridad**: Media
- **Descripción**:
  SonarQube reporta la regla `Web:S5255` en `src/main/frameworks/flask_mvc/templates/app.html` (líneas 13, 115, 138 y 189), debido a que los cuatro contenedores `<aside>` carecen de `aria-label` o `aria-labelledby`, dificultando la navegación mediante lectores de pantalla.
- **Estrategia de Refactoring**:
  Incorporar atributos `aria-label` descriptivos en cada elemento `<aside>` de `app.html`.
- **Criterios de Aceptación (Checklist)**:
  - [x] Añadir `aria-label` descriptivo a `<aside class="sidebar" id="sidebar">` (línea 13).
  - [x] Añadir `aria-label` descriptivo a `<aside class="progress-panel" id="dashboard-progress">` (línea 115).
  - [x] Añadir `aria-label` descriptivo a `<aside class="profile-summary" id="profile-summary">` (línea 138).
  - [x] Añadir `aria-label` descriptivo a `<aside class="detail-panel" id="opportunity-detail">` (línea 189).
  - [x] Validar con pruebas automatizadas sobre la plantilla HTML que todos los `<aside>` cuentan con etiqueta accesible.
