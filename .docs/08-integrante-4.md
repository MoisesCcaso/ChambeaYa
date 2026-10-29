# Integrante 4 — Matching

Relacionado: [reparto](04-reparto-equipo.md), [convenciones](02-convenciones.md), [reportes](11-reportes-y-entrega.md).

## Alcance

Código: `src/main/domain/matching/{sugerencia,resultado_matching,matching_dominio_servicio}.py`; `src/main/infrastructure/sqlalchemy_matching_repository.py`; `src/main/application/matching_application_service.py`. Tests exclusivos: `src/test/domain/test_matching_domain.py`, `src/test/infrastructure/test_matching_repository.py`, `src/test/application/test_matching_service.py`. No agregar el servicio/Repositorio de notificaciones, asignado a Integrante 6.

Ramas: `lab5/domain-matching`, `lab5/infrastructure-matching`, `lab5/application-matching`. Commits `test(domain-matching): cubrir compatibilidad` + `fix #n`; `test(infrastructure-matching): persistir sugerencias` + `fix #n`; `test(application-matching): aislar cálculo de sugerencias` + `fix #n`.

| Capa / regla | Dado / Cuando / Entonces | Técnica / doble |
|---|---|---|
| Dominio `Sugerencia.calcular_compatibilidad` | intersección casefold: 1 de 2 requisitos da 50; requisitos vacíos o que normalizan a conjunto vacío da 0 | equivalencia; sin doble |
| Dominio `ResultadoMatching.es_compatible` | 50 con umbral 50 devuelve True; 49.99 devuelve False | valor límite; sin doble |
| Dominio `MatchingDominioServicio.calcular_match/filtrar_convocatorias` | None retorna None; filtrar omite no publicadas, exige score >= umbral 50 y ordena descendente | partición/límite; sin doble |
| Repositorio `save/find_by_practicante_id` | guardar sugerencia y recargar campos/JSON; sin filas devuelve `[]`; guardar dos veces misma pareja verifica upsert | SQLite memoria; sin mocks |
| Servicio `calculate_for_practicante` | repositorios devuelven practicante y convocatorias; el servicio de dominio calcula resultados y se guardan sus sugerencias | Crear tres dobles independientes con `create_autospec(IPerfilRepository, instance=True, spec_set=True)`, `create_autospec(IConvocatoriaRepository, instance=True, spec_set=True)` y `create_autospec(ISugerenciaRepository, instance=True, spec_set=True)`. Configurar `find_practicante_by_user_id`, `find_all` y `save`; verificar argumentos y resultados |
| Servicio `suggest_convocatorias` | perfil y convocatorias devueltos por repositorios se pasan al servicio de dominio; retorna sus resultados | Reutilizar dobles separados de las tres interfaces anteriores; verificar ID de usuario y umbral delegado. El servicio de dominio real se usa por defecto |

El código puntúa coincidencias sobre requisitos y usa umbral inclusivo 50.0 por defecto; verificar también la lista requerida vacía. Las tres interfaces existen bajo `src/main/domain/perfil/i_perfil_repository.py`, `src/main/domain/convocatorias/i_convocatoria_repository.py` y `src/main/domain/matching/i_sugerencia_repository.py`. R8 importa ORM real y usa TestingConfig. Sin fechas ni UUID relevantes, no usar patch.

Meta: al menos 80 % de líneas ejecutables por archivo. Priorizar los dos métodos del repositorio y los casos de listas vacías del dominio; anotar numerador y denominador medidos.

Riesgo: el servicio usa varios contextos y puede tentar a probar rutas externas; construir entidades simples localmente. Integrante 2 no debe ser dependencia de ejecución: usar autospec de la interfaz.

DoD: fórmula comprobada línea por línea, seis rutas propias sin colisiones, repository sin doubles, service con doubles y reporte de cobertura.

## Reportes durante Fase 1

Puedes conservar localmente los reportes de tus ejecuciones para informar resultados en el issue o PR. Los artefactos dentro de `reports/` están en `.gitignore`: no los incluyas en tus commits de I-11–I-13. Se regenerarán y versionarán como reportes finales en I-23, después de integrar I-01–I-22; consulta [11-reportes-y-entrega.md](11-reportes-y-entrega.md).

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

- `src/main/domain/matching/sugerencia.py:1-33` (casefold, score es intersección/requeridos), `resultado_matching.py:1-11` (default umbral 50 inclusivo), `matching_dominio_servicio.py:6-37`.
- `src/main/infrastructure/sqlalchemy_matching_repository.py:9-65` (save/upsert, find, conversión JSON); interface `src/main/domain/matching/i_sugerencia_repository.py:7-17`.
- `src/main/application/matching_application_service.py:4-43` (constructor y dos operaciones); interfaces: `src/main/domain/perfil/i_perfil_repository.py:7-26`, `src/main/domain/convocatorias/i_convocatoria_repository.py:7-30`, `src/main/domain/matching/i_sugerencia_repository.py:7-17`.
- `src/main/config.py:48-52`; `src/main/frameworks/flask_mvc/app.py:14-48`.
