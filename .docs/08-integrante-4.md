# Integrante 4 — Matching

Relacionado: [reparto](04-reparto-equipo.md), [convenciones](02-convenciones.md), [reportes](11-reportes-y-entrega.md).

## Alcance

Código: `domain/matching/{sugerencia,resultado_matching,matching_dominio_servicio}.py`; `infrastructure/sqlalchemy_matching_repository.py`; `application/matching_application_service.py`. Tests exclusivos: `tests/domain/test_matching_domain.py`, `tests/infrastructure/test_matching_repository.py`, `tests/application/test_matching_service.py`. No agregar el servicio/Repositorio de notificaciones, asignado a Integrante 6.

Ramas: `lab5/domain-matching`, `lab5/infrastructure-matching`, `lab5/application-matching`. Commits `test(domain-matching): cubrir compatibilidad` + `fix #n`; `test(infrastructure-matching): persistir sugerencias` + `fix #n`; `test(application-matching): aislar cálculo de sugerencias` + `fix #n`.

TDD rojo-verde-refactor.

| Capa / regla | Dado / Cuando / Entonces | Técnica / doble |
|---|---|---|
| Dominio `Sugerencia.calcular_compatibilidad` | intersección casefold: 1 de 2 requisitos da 50; requisitos vacíos o que normalizan a conjunto vacío da 0 | equivalencia; sin doble |
| Dominio `ResultadoMatching.es_compatible` | 50 con umbral 50 devuelve True; 49.99 devuelve False | valor límite; sin doble |
| Dominio `MatchingDominioServicio.calcular_match/filtrar_convocatorias` | None retorna None; filtrar omite no publicadas, exige score >= umbral 50 y ordena descendente | partición/límite; sin doble |
| Repositorio `save/find_by_practicante_id` | guardar sugerencia y recargar campos/JSON; sin filas devuelve `[]`; guardar dos veces misma pareja verifica upsert | SQLite memoria; sin mocks |
| Servicio `calculate_for_practicante` | perfiles/convocatorias fake de dominio y repositorios autospec; devuelve cálculo y guarda sugerencias según flujo | `create_autospec(IPerfilRepository/IConvocatoriaRepository/ISugerenciaRepository, instance=True, spec_set=True)`; verificar llamadas y filtros |
| Servicio `suggest_convocatorias` | configuración de repositorios devuelve sugerencias del practicante | mismos autospec; verificar ID pasado |

El código puntúa coincidencias sobre requisitos y usa umbral inclusivo 50.0 por defecto; verificar también la lista requerida vacía. Las tres interfaces existen bajo `domain/perfil/i_perfil_repository.py`, `domain/convocatorias/i_convocatoria_repository.py` y `domain/matching/i_sugerencia_repository.py`. R8 importa ORM real y usa TestingConfig. Sin fechas ni UUID relevantes, no usar patch.

Meta: al menos 80 % de líneas ejecutables por archivo. Priorizar los dos métodos del repositorio y los casos de listas vacías del dominio; anotar numerador y denominador medidos.

Riesgo: el servicio usa varios contextos y puede tentar a probar rutas externas; construir entidades simples localmente. Integrante 2 no debe ser dependencia de ejecución: usar autospec de la interfaz.

DoD: fórmula comprobada línea por línea, seis rutas propias sin colisiones, repository sin doubles, service con doubles y reporte de cobertura.

## Checklist para retomar el trabajo

- [ ] Leer el estado de la tarjeta/issue asignado y confirmar la rama de `development` con la Fase 0 integrada.
- [ ] Crear/actualizar la rama propia según [02-convenciones.md](02-convenciones.md); anotar el issue y el siguiente caso pendiente.
- [ ] Completar primero los casos de dominio con TDD: rojo, verde, refactor.
- [ ] Probar el repositorio contra SQLite en memoria, sin dobles.
- [ ] Probar el servicio asignado con autospec/dobles y comprobar retornos, llamadas y argumentos.
- [ ] Ejecutar los archivos propios y la suite unitaria; registrar el siguiente paso pendiente en el issue.
- [ ] Medir y anotar cobertura de los archivos asignados; no copiar porcentajes de reportes anteriores sin reproducirlos.
- [ ] Confirmar el DoD de esta guía, crear commits con `fix #<n>`, abrir PR a `development` y mover la tarjeta en el Project.

## Verificado

- `domain/matching/sugerencia.py:1-33` (casefold, score es intersección/requeridos), `resultado_matching.py:1-11` (default umbral 50 inclusivo), `matching_dominio_servicio.py:6-37`.
- `infrastructure/sqlalchemy_matching_repository.py:9-65` (save/upsert, find, conversión JSON); interface `domain/matching/i_sugerencia_repository.py:7-17`.
- `application/matching_application_service.py:4-43` (constructor y dos operaciones); interfaces: `domain/perfil/i_perfil_repository.py:7-26`, `domain/convocatorias/i_convocatoria_repository.py:7-30`, `domain/matching/i_sugerencia_repository.py:7-17`.
- `config.py:48-52`; `frameworks/flask_mvc/app.py:14-48`.
