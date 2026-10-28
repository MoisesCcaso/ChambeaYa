# Tablero Kanban e issues

Relacionado: [reparto/horas](04-reparto-equipo.md), [convenciones](02-convenciones.md), [entrega](11-reportes-y-entrega.md).

## Creación

Responsable: el coordinador, que confirmó tener permiso de administrar Projects en la cuenta propietaria **MoisesCcaso**. Crea un GitHub Project, elige plantilla **KANBAN**, lo vincula al repo y deja estas columnas exactas y en orden: `TO-DO`, `CURRENT ITERATION`, `IN PROGRESS`, `FIX VALIDATION`, `DONE`. Antes de crear issues, confirma que los seis integrantes pueden ver el Project y colaborar en él.

Etiquetas que se crearán: `unit test` para los issues I-01–I-22 de pruebas R7–R9 y `enhancement` para I-23 de reportes R10–R11. Si una prueba revela un defecto que requiere cambiar código, crear un issue de corrección aparte con `enhancement` y dependencia al test que lo detectó.

## Plantilla de issue

**Título:** `[R#] verbo + módulo`. En la descripción de cada issue incluye el alcance y la ruta de prueba indicados en su bloque, además de estos criterios comunes para I-01–I-22: seguir los casos de la guía del integrante, aplicar TDD, crear solo el archivo asignado, pasar las pruebas y anotar cobertura. Si se descubre un defecto de código, abrir un issue de corrección separado antes de modificar `src/main/`. Enlazar el PR hacia `development` con el issue. I-23 tiene criterios propios en su bloque.

## Issues propuestos

Los IDs son provisionales; anota el número real de cada issue en la guía del integrante para usarlo en los footers `fix #n`. La separación de carpetas y la fixture compartida de R3 se completaron en Fase 0, por eso no aparecen como issues pendientes. Los issues I-01–I-22 cubren las pruebas R7–R9. I-23 integra y versiona los reportes R10–R11 después de que se integren las pruebas. Inicio: `TO-DO`.

### I-01 — Pruebas de dominio auth

**Título:** `[R7] Probar dominio auth`

**Descripción:** Probar reglas de usuario, autenticación y tokens. Crear `src/test/domain/test_auth_domain.py` siguiendo la guía del Integrante 1.

**Criterios de aceptación:**
- Cubrir los casos de dominio propuestos en la guía.
- Pasar pytest y registrar la cobertura del archivo.
- Crear o modificar solo el archivo de prueba asignado.

**Responsable:** Integrante 1  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO
### I-02 — Repositorio de usuario

**Título:** `[R8] Probar repositorio de usuario`

**Descripción:** Probar guardado y consultas del repositorio de usuario con SQLite en memoria, sin dobles. Crear `src/test/infrastructure/test_usuario_repository.py`.

**Criterios de aceptación:**
- Usar los modelos ORM reales y SQLite en memoria, sin mocks.
- Verificar guardado y consultas.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 1  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO
### I-03 — Servicio de usuario

**Título:** `[R9] Probar servicio de usuario con dobles`

**Descripción:** Probar el servicio de usuario aislado con dobles de sus interfaces y verificar resultados e interacciones. Crear `src/test/application/test_usuario_service.py`.

**Criterios de aceptación:**
- Probar sin repositorios reales.
- Verificar resultados, métodos y argumentos de los dobles.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 1  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO
### I-04 — Pruebas de dominio perfil

**Título:** `[R7] Probar dominio perfil`

**Descripción:** Probar reglas de perfil, RUC y los objetos de valor asignados, incluido `NombreCompleto`. Crear `src/test/domain/test_perfil_domain.py` según la guía del Integrante 2.

**Criterios de aceptación:**
- Cubrir los casos de perfil, RUC y objetos de valor de la guía.
- Pasar pytest y registrar la cobertura.
- Modificar solo el archivo de prueba asignado.

**Responsable:** Integrante 2  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-05 — Repositorio de perfil

**Título:** `[R8] Probar repositorio perfil`

**Descripción:** Probar guardado, lectura y conversión del repositorio de perfil con SQLite en memoria, sin dobles. Crear `src/test/infrastructure/test_perfil_repository.py`.

**Criterios de aceptación:**
- Usar los modelos ORM reales y SQLite en memoria, sin mocks.
- Verificar persistencia, lectura y conversión.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 2  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-06 — Servicio de perfil

**Título:** `[R9] Probar servicio perfil con doble`

**Descripción:** Probar el servicio de perfil aislado con dobles de sus interfaces y verificar resultados e interacciones. Crear `src/test/application/test_perfil_service.py`.

**Criterios de aceptación:**
- Probar con dobles de repositorio.
- Verificar resultados, llamadas y argumentos.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 2  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-07 — Pruebas de dominio convocatorias

**Título:** `[R7] Probar dominio convocatorias`

**Descripción:** Probar reglas, transiciones y fábrica de convocatorias y postulaciones. Crear `src/test/domain/test_convocatorias_domain.py` según la guía del Integrante 3.

**Criterios de aceptación:**
- Cubrir reglas, estados y fábricas de la guía.
- Pasar pytest y registrar la cobertura.
- Modificar solo el archivo de prueba asignado.

**Responsable:** Integrante 3  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-08 — Repositorio de convocatorias

**Título:** `[R8] Probar repositorio convocatoria`

**Descripción:** Probar persistencia, búsquedas y eliminación de convocatorias con SQLite en memoria, sin dobles. Crear `src/test/infrastructure/test_convocatoria_repository.py`.

**Criterios de aceptación:**
- Usar los modelos ORM reales y SQLite en memoria, sin mocks.
- Verificar guardado, búsquedas y eliminación.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 3  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-09 — Repositorio de postulaciones

**Título:** `[R8] Probar repositorio postulación`

**Descripción:** Probar persistencia y consultas de postulaciones con SQLite en memoria, sin dobles. Crear `src/test/infrastructure/test_postulacion_repository.py`.

**Criterios de aceptación:**
- Usar los modelos ORM reales y SQLite en memoria, sin mocks.
- Verificar persistencia y consultas.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 3  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-10 — Servicio de convocatorias

**Título:** `[R9] Probar servicio convocatoria con dobles`

**Descripción:** Probar el servicio de convocatorias aislado con dobles de repositorio; verificar reglas, llamadas y argumentos. Crear `src/test/application/test_convocatoria_service.py`.

**Criterios de aceptación:**
- Probar sin repositorios reales.
- Verificar reglas, llamadas y argumentos de los dobles.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 3  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-11 — Pruebas de dominio matching

**Título:** `[R7] Probar dominio matching`

**Descripción:** Probar cálculo, normalización y resultados de matching según las reglas del dominio. Crear `src/test/domain/test_matching_domain.py` según la guía del Integrante 4.

**Criterios de aceptación:**
- Cubrir cálculo, normalización y resultados de la guía.
- Pasar pytest y registrar la cobertura.
- Modificar solo el archivo de prueba asignado.

**Responsable:** Integrante 4  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-12 — Repositorio matching

**Título:** `[R8] Probar repositorio matching`

**Descripción:** Probar guardado, lectura y actualización de sugerencias con SQLite en memoria, sin dobles. Crear `src/test/infrastructure/test_matching_repository.py`.

**Criterios de aceptación:**
- Usar los modelos ORM reales y SQLite en memoria, sin mocks.
- Verificar guardado, lectura y actualización.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 4  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-13 — Servicio matching

**Título:** `[R9] Probar servicio matching con dobles`

**Descripción:** Probar el servicio de matching aislado con dobles de perfil, convocatorias y sugerencias; verificar resultados e interacciones. Crear `src/test/application/test_matching_service.py`.

**Criterios de aceptación:**
- Probar con dobles de las tres interfaces.
- Verificar resultados y llamadas.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 4  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-14 — Pruebas de dominio práctica y evaluación

**Título:** `[R7] Probar dominio práctica/evaluación`

**Descripción:** Probar reglas y transiciones de prácticas, entregables y evaluaciones. Crear `src/test/domain/test_practica_evaluacion_domain.py` según la guía del Integrante 5.

**Criterios de aceptación:**
- Cubrir reglas y transiciones de la guía.
- Pasar pytest y registrar la cobertura.
- Modificar solo el archivo de prueba asignado.

**Responsable:** Integrante 5  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-15 — Repositorio de prácticas

**Título:** `[R8] Probar repositorio práctica`

**Descripción:** Probar persistencia y consultas de prácticas, entregables y evaluaciones con SQLite en memoria, sin dobles. Crear `src/test/infrastructure/test_practica_repository.py`.

**Criterios de aceptación:**
- Usar los modelos ORM reales y SQLite en memoria, sin mocks.
- Verificar persistencia y consultas.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 5  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-16 — Repositorio de certificados

**Título:** `[R8] Probar repositorio certificado`

**Descripción:** Probar guardado y consultas del repositorio de certificados con SQLite en memoria, sin dobles. Crear `src/test/infrastructure/test_certificado_repository.py`.

**Criterios de aceptación:**
- Usar los modelos ORM reales y SQLite en memoria, sin mocks.
- Verificar guardado y consultas.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 5  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-17 — Servicio de prácticas

**Título:** `[R9] Probar servicio práctica con dobles`

**Descripción:** Probar el servicio de prácticas aislado con dobles de sus interfaces; verificar reglas, llamadas y argumentos. Crear `src/test/application/test_practica_service.py`.

**Criterios de aceptación:**
- Probar con dobles de sus interfaces.
- Verificar reglas, llamadas y argumentos.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 5  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-18 — Pruebas de dominio certificación

**Título:** `[R7] Probar dominio certificación`

**Descripción:** Probar creación y reglas de certificados, PDF y QR, controlando el tiempo o UUID cuando corresponda. Crear `src/test/domain/test_certificacion_domain.py` según la guía del Integrante 6.

**Criterios de aceptación:**
- Cubrir los casos de certificados, PDF y QR de la guía.
- Hacer deterministas fechas y UUID cuando corresponda.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 6  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-19 — Repositorio de notificaciones

**Título:** `[R8] Probar repositorio notificación`

**Descripción:** Probar escritura y lectura de notificaciones con SQLite en memoria, sin dobles. Crear `src/test/infrastructure/test_notificacion_repository.py`.

**Criterios de aceptación:**
- Usar los modelos ORM reales y SQLite en memoria, sin mocks.
- Verificar escritura y lectura.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 6  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-20 — Servicio de certificación

**Título:** `[R9] Probar servicio certificación con doble`

**Descripción:** Probar el servicio de certificación aislado con dobles de certificado y práctica; verificar interacciones y resultados. Crear `src/test/application/test_certificacion_service.py`.

**Criterios de aceptación:**
- Probar con dobles de certificado y práctica.
- Verificar interacciones y resultados.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 6  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-21 — Servicio de postulación

**Título:** `[R9] Probar servicio postulación con dobles`

**Descripción:** Probar el servicio de postulación aislado con dobles de sus repositorios; cubrir selección y guardas según la guía del Integrante 3. Crear `src/test/application/test_postulacion_service.py`.

**Criterios de aceptación:**
- Probar sin repositorios reales.
- Cubrir selección y guardas de la guía.
- Verificar llamadas y argumentos; pasar pytest y registrar la cobertura.

**Responsable:** Integrante 3  
**Etiqueta:** `unit test`  
**Duración:** 1 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-22 — Servicio de notificaciones

**Título:** `[R9] Probar servicio notificación con dobles`

**Descripción:** Probar el servicio de notificaciones aislado con dobles reader/writer; verificar llamadas, argumentos y resultados. Crear `src/test/application/test_notificacion_service.py`.

**Criterios de aceptación:**
- Probar con dobles reader/writer.
- Verificar llamadas, argumentos y resultados.
- Pasar pytest y registrar la cobertura.

**Responsable:** Integrante 6  
**Etiqueta:** `unit test`  
**Duración:** 0.5 h  
**Dependencia:** Ninguna  
**Columna inicial:** TO-DO

### I-23 — Reportes finales

**Título:** `[R10–R11] Consolidar reportes globales y unitarios en reports/`

**Descripción:** Tras integrar I-01–I-22, ejecutar las suites global y unitaria; generar JUnit y cobertura XML/HTML, revisar los resultados y versionar los artefactos finales en `reports/`.

**Criterios de aceptación:**
- Las suites global y unitaria pasan.
- Los reportes JUnit y de cobertura XML/HTML se generan y revisan en `reports/`.
- Si la cobertura global es menor al 80 %, explicar la diferencia frente al baseline.
- Los reportes finales quedan versionados y el commit enlazado al issue.

**Responsable:** Integrante 1  
**Etiqueta:** `enhancement`  
**Duración:** 1 h  
**Dependencia:** I-01–I-22 integrados  
**Columna inicial:** TO-DO

Carga de pruebas R7–R9: Integrante 1 = 1.5 h; Integrante 2 = 1.5 h; Integrante 3 = 3 h; Integrante 4 = 1.5 h; Integrante 5 = 2 h; Integrante 6 = 2 h. I-23 añade 1 h de reportes a Integrante 1 en Fase 2. Totales de issues Fase 1–2: Integrante 1 = 2.5 h; Integrante 2 = 1.5 h; Integrante 3 = 3 h; Integrante 4 = 1.5 h; Integrante 5 = 2 h; Integrante 6 = 2 h. Suma 12.5 h entre seis personas; máximo individual 3 h, diferencia máxima 1.5 h. Todas las cargas caben en las 4 h del laboratorio. Son estimaciones iniciales.

## Descripciones de columnas para el README del Project

Estas descripciones se pueden copiar al README del GitHub Project. Mover cada tarjeta cuando cumpla la condición indicada.

### TO-DO

Tareas pendientes.

### CURRENT ITERATION

Tareas elegidas para trabajarse durante la iteración actual.

### IN PROGRESS

Tareas en las que se está trabajando en una rama `lab5/<capa>-<modulo>`.

### FIX VALIDATION

Correcciones que esperan una nueva revisión o verificación.

### DONE

Tarea completada: PR integrado en `development`, criterios cumplidos e issue cerrado.

## Etiquetas

- `unit test`: issues de pruebas de dominio, repositorios y servicios de aplicación (R7–R9).
- `enhancement`: consolidación de reportes finales (R10–R11) o una corrección de código aprobada si las pruebas revelan un defecto.
