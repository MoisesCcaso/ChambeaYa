# Integrante 5 — Práctica/evaluación

Relacionado: [reparto](04-reparto-equipo.md), [convenciones](02-convenciones.md), [reportes](11-reportes-y-entrega.md).

## Alcance

Dominio `src/main/domain/practica_evaluacion/{practica,practica_fabrica,entregable,evaluacion}.py`; repos `src/main/infrastructure/sqlalchemy_practica_repository.py`, `sqlalchemy_certificado_repository.py`; servicio `src/main/application/practica_application_service.py`. Tests: `src/test/domain/test_practica_evaluacion_domain.py`, `src/test/infrastructure/test_practica_repository.py`, `src/test/infrastructure/test_certificado_repository.py`, `src/test/application/test_practica_service.py`. No editar dominio certificación ni servicio certificación.

Ramas: `lab5/domain-practica`, `lab5/infrastructure-practica`, `lab5/application-practica`. Commits `test(domain-practica): cubrir finalización y evaluación` + `fix #n`; `test(infrastructure-practica): persistir agregado e hijos` + `fix #n`; `test(application-practica): aislar ciclo de práctica` + `fix #n`.

| Capa / regla | Dado / Cuando / Entonces | Técnica / doble |
|---|---|---|
| Dominio `Evaluacion.crear/esta_aprobada` | puntajes 0 y 100 aceptados, -0.01/100.01 rechazados; 59.99 falla aprobación, 60 aprueba | límite; patch `domain.practica_evaluacion.evaluacion.datetime` |
| Dominio `Practica.finalizar` | sin entregable falla; con entregable y evaluación 59 falla; evaluación >=60 finaliza | partición y transición; sin doble |
| Dominio `Practica` mutaciones | finalizada no admite subir/evaluar/eliminar; ID de entregable no presente lanza ValueError | transición; patch de fecha opcional en `domain.practica_evaluacion.entregable.datetime` |
| Repo práctica | guardar agregado con hijos; recargar entrega/evaluación; quitar hijo y guardar sincroniza colección | SQLite memoria; sin mocks |
| Repo certificado | guardar Certificado con QR/PDF, búsquedas id/código/práctica, no encontrado None | SQLite memoria; sin mocks |
| Servicio `finish` | práctica en curso con entregable+aprobación; repositorios autospec devuelven agregado; servicio guarda estado final y devuelve resultado | autospec `IPracticaRepository` y las interfaces requeridas por constructor; verificar llamadas/argumentos |
| Servicio `upload_deliverable/evaluate` | usuario habilitado/permiso según firma real; verificar persistencia de agregado | autospec de interfaces; usar dominio real para sus reglas |

Reglas confirmadas: `PUNTAJE_APROBACION=60.0`, rango inclusivo 0–100. El patch de tiempo en Evaluacion es exactamente `domain.practica_evaluacion.evaluacion.datetime`. `Entregable.crear` tiene su propio módulo de fecha; validar el import y patch local antes de añadir. No parchear datetime global. `SqlAlchemyPracticaRepository.save` persiste y sincroniza hijos en SQLite en memoria.

Meta: al menos 80 % de líneas ejecutables por archivo; cubrir guardado, lectura y mapeo de hijos.

Riesgo: servicio depende de varios repositorios; sus interfaces están en dominio. Integrante 6 puede probar certificación con autospec de `IPracticaRepository`, sin depender de este test ni sus fixtures.

DoD: casos de límites correctos, fecha determinista con patch módulo-local, R8 SQLite sin dobles, R9 autospec, PR integrado y reportes.

## Reportes durante Fase 1

Puedes conservar localmente los reportes de tus ejecuciones para informar resultados en el issue o PR. Los artefactos dentro de `reports/` están en `.gitignore`: no los incluyas en tus commits de I-14–I-17. Se regenerarán y versionarán como reportes finales en I-23, después de integrar I-01–I-22; consulta [11-reportes-y-entrega.md](11-reportes-y-entrega.md).

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

- `src/main/domain/practica_evaluacion/evaluacion.py:6-36` (60.0, 0–100 inclusivo); `practica.py:8-78` (finalización requiere entregable/evaluación aprobada); `entregable.py:7-23`; `practica_fabrica.py:7-16`.
- `src/main/infrastructure/sqlalchemy_practica_repository.py:14-100`; `sqlalchemy_certificado_repository.py:12-72` (persistencia/lookup); interfaces `src/main/domain/practica_evaluacion/i_practica_repository.py:7-22` y `src/main/domain/certificacion/i_certificado_repository.py:4-20`.
- `src/main/application/practica_application_service.py:12-178` (constructor y métodos públicos); interfaces de dependencias en `src/main/domain/perfil/i_perfil_repository.py`, `src/main/domain/convocatorias/i_postulacion_repository.py`, `i_convocatoria_repository.py`.
- Patch fecha: `domain.practica_evaluacion.evaluacion.datetime`; `Entregable.crear` tiene misma dependencia local en `domain.practica_evaluacion.entregable.datetime`.
- `src/main/config.py:48-52`; `src/main/frameworks/flask_mvc/app.py:14-48`.
