# Integrante 3 — Convocatorias y postulaciones

Relacionado: [reparto](04-reparto-equipo.md), [convenciones](02-convenciones.md), [reportes](11-reportes-y-entrega.md).

## Alcance

Código dominio `src/main/domain/convocatorias/{convocatoria,convocatoria_fabrica,postulacion}.py`; repos `src/main/infrastructure/sqlalchemy_convocatoria_repository.py`, `sqlalchemy_postulacion_repository.py`; servicios `src/main/application/convocatoria_application_service.py` y `src/main/application/postulacion_application_service.py`. Pruebas: `src/test/domain/test_convocatorias_domain.py`, `src/test/infrastructure/test_convocatoria_repository.py`, `src/test/infrastructure/test_postulacion_repository.py`, `src/test/application/test_convocatoria_service.py`, `src/test/application/test_postulacion_service.py`. Postulación se asigna aquí por afinidad de contexto y repositorio.

Ramas: `lab5/domain-convocatorias`, `lab5/infrastructure-convocatorias`, `lab5/application-convocatoria`, `lab5/application-postulacion`. Commits `test(domain-convocatorias): cubrir cambios de estado` + `fix #n`; `test(infrastructure-convocatorias): persistir convocatorias y postulaciones` + `fix #n`; `test(application-convocatoria): aislar ciclo de publicación` + `fix #n`; `test(application-postulacion): probar selección de candidato` + `fix #n`.

| Capa / regla | Dado / Cuando / Entonces | Técnica / doble |
|---|---|---|
| Dominio `Convocatoria.publicar/cerrar/reabrir` | borrador→publicada→cerrada→publicada; publicar desde estado distinto lanza ValueError | transición; patch `domain.convocatorias.convocatoria.datetime` para fecha fija |
| Dominio `Convocatoria.actualizar/validar_eliminacion` | actualizar en borrador aplica campos; no borrador rechaza; solo borrador eliminable | partición; sin doble |
| Dominio `Postulacion` | pendiente selecciona/rechaza/cancela; cancelada reactiva; seleccionada/rechazada reconsidera; estado no permitido lanza error | transición de estados; sin doble |
| Repo convocatoria | guardar y buscar por id/empresa; search filtra estado/texto; borrar id inexistente False y existente True | SQLite memoria, sin mocks |
| Repo postulación | guardar; buscar por convocatoria+practicante; lista por cada FK; desconocido devuelve None/lista vacía | SQLite memoria, sin mocks |
| Servicio convocatoria `publish` | repo devuelve Convocatoria borrador; servicio publica, guarda una vez y devuelve guardada | autospec `IConvocatoriaRepository`, verificar id y argumento a save |
| Servicio `search`/`find_by_id` | `search("Python", "publicada")` delega ambos argumentos y retorna la lista del repo; `find_by_id(99)` retorna el None que entrega el repo | autospec de `IConvocatoriaRepository`; verificar llamadas/argumentos |
| Servicio Postulación `select_candidate` | candidato pendiente de convocatoria propia queda seleccionado; otras postulaciones pendientes quedan rechazadas y guardadas | autospec `IPostulacionRepository`, `IConvocatoriaRepository`, `IPerfilRepository`, `IPracticaRepository`; verificar saves e IDs |

Las interfaces concretas son `src/main/domain/convocatorias/i_convocatoria_repository.py` e `i_postulacion_repository.py`. No confundir `aceptar()` alias con `seleccionar()`: ambos existen, y servicio opera sus propias reglas. `Convocatoria.datetime` está importado directamente como `datetime`; patch exacto `domain.convocatorias.convocatoria.datetime`. No hay UUID en asignación.

Meta de cobertura: al menos 80 % de líneas ejecutables por archivo. Registrar numerador y denominador medidos al inicio y al cierre del PR.

Riesgo: selección coordina varios repositorios y rechaza postulaciones pendientes de la misma convocatoria. La dependencia queda aislada con autospec de las interfaces; no requiere pruebas de otros integrantes.

DoD: dominio determinista, dos repos con SQLite, servicio aislado con autospec, archivos únicos y cobertura anotada.

## Reportes durante Fase 1

Puedes conservar localmente los reportes de tus ejecuciones para informar resultados en el issue o PR. Los artefactos dentro de `reports/` están en `.gitignore`: no los incluyas en tus commits de I-07–I-10 ni I-21. Se regenerarán y versionarán como reportes finales en I-23, después de integrar I-01–I-22; consulta [11-reportes-y-entrega.md](11-reportes-y-entrega.md).

## Pasos para completar los issues

- [ ] Leer el estado de la tarjeta/issue asignado y confirmar que `development` está actualizado, con implementación en `src/main/` y pruebas en `src/test/`.
- [ ] Crear/actualizar la rama propia según [02-convenciones.md](02-convenciones.md); anotar el issue y el siguiente caso pendiente.
- [ ] Completar los casos de prueba asignados en esta guía.
- [ ] Probar el repositorio contra SQLite en memoria, sin dobles.
- [ ] Probar el servicio asignado con autospec/dobles y comprobar retornos, llamadas y argumentos.
- [ ] Ejecutar los archivos propios y la suite unitaria; registrar el siguiente paso pendiente en el issue.
- [ ] Medir y anotar cobertura de los archivos asignados; no copiar porcentajes de reportes anteriores sin reproducirlos.
- [ ] Confirmar el DoD de esta guía, crear commits con `fix #<n>`, abrir PR a `development` y mover la tarjeta en el Project.

## Verificado

- `src/main/domain/convocatorias/convocatoria.py:34-108` (estados y fecha UTC); `convocatoria_fabrica.py:5-30`; `postulacion.py:4-54` (estados y métodos, incluye `aceptar`).
- `src/main/infrastructure/sqlalchemy_convocatoria_repository.py:12-101` (save/search/delete); `sqlalchemy_postulacion_repository.py:9-56` (save y búsquedas); interfaces en `src/main/domain/convocatorias/i_convocatoria_repository.py:7-30` e `i_postulacion_repository.py:7-26`.
- `src/main/application/convocatoria_application_service.py:5-103` (constructor, publish/update/delete/search y guardas); `src/main/application/postulacion_application_service.py:5-166` (constructor, `select_candidate` 79-114 y guardas).
- `src/main/config.py:48-52`; `src/main/frameworks/flask_mvc/app.py:14-48`.
