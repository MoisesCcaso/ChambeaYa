# Integrante 2 — Perfil

Relacionado: [reparto](04-reparto-equipo.md), [convenciones](02-convenciones.md), [reportes](11-reportes-y-entrega.md).

## Alcance

Código: `domain/perfil/{practicante,empresa,ruc,nombre_completo}.py`; `infrastructure/sqlalchemy_perfil_repository.py`; `application/perfil_application_service.py`. Crear solo `tests/domain/test_perfil_domain.py`, `tests/infrastructure/test_perfil_repository.py`, `tests/application/test_perfil_service.py`. No tomar auth ajeno, conftest/config ni otros archivos.

Rama(s): `lab5/domain-perfil`, `lab5/infrastructure-perfil`, `lab5/application-perfil`. Commits sugeridos `test(domain-perfil): cubrir identidad y score` + `fix #n`; `test(infrastructure-perfil): verificar mapeo de perfiles` + `fix #n`; `test(application-perfil): cubrir actualización de perfil` + `fix #n`.

TDD rojo-verde-refactor.

| Capa / regla | Dado / Cuando / Entonces; entrada y expectativa | Técnica / doble |
|---|---|---|
| Dominio `Practicante.verificar_identidad` | DNI `12345678` válido; 7/9 caracteres o no dígitos lanza ValueError; carnet con trim de longitud >=4 es aceptado | límites/equivalencia; sin doble |
| Dominio `Practicante.calcular_score` | 10 habilidades + 5 formaciones + identidad verificada = 100; exceso queda topado en 100 | valor límite; sin doble |
| Dominio `RUC.es_valido` y `Empresa.verificar_ruc` | probar RUC válido `20100070970`, prefijo no permitido y dígito final incorrecto; empresa refleja bool | equivalencia; sin doble |
| Dominio `NombreCompleto.validar` | recorta nombres/apellidos; falta uno produce ValueError; es módulo local aislado | equivalencia; sin doble |
| Repositorio `save_practicante/find...` | persistir perfil con listas, recargar y comprobar listas/flags; desconocido None | SQLite memoria; sin dobles |
| Repositorio `save_empresa` | guardar Empresa con `RUC("20100070970")`, recargar y comprobar número encapsulado; buscar usuario desconocido None | SQLite memoria; sin dobles |
| Servicio `update_practicante` | usuario activo tipo practicante; data con nombres, DNI, habilidades; repositorio retorna Practicante con estado actualizado y save recibe objeto | autospec `IPerfilRepository`, `IUsuarioRepository`; verificar argumentos |
| Servicio guardas | usuario empresa/inactivo o usuario inexistente al llamar `update_practicante` → ValueError antes de guardar | mismos autospec, verificar `save_practicante.assert_not_called()` |

En R9 importar interfaces reales `IPerfilRepository` y `IUsuarioRepository` desde sus módulos `i_*.py`; el usuario para setup es un `Usuario` de dominio simple. No importar `UsuarioApplicationService` ni prueba de Integrante 1. Sin control directo de tiempo/UUID en estas reglas; no introducir patch. En R8 ORM real; app fixture usa `TestingConfig` SQLite memoria.

Meta: objetivo de 80 % por archivo tras medir líneas ejecutables; incluir sus validaciones locales sin asumir que se usan en otros flujos. Priorizar `Practicante`, `RUC` y el VO aislado.

Riesgo: el módulo `NombreCompleto` no se usa en flujos (análisis: 0 %); probar aislado sin afirmar que el servicio lo consume. Dependencia con Integrante 1 solo conceptual; autospec propio.

DoD: pruebas de dominio/ORM/aplicación en rutas exclusivas; R8 sin doubles; R9 doubles con métodos reales; TDD y evidencia de cobertura; PR integrado.


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

- `domain/perfil/practicante.py:29-99` (DNI 8, carnet longitud mínima 4, score 5 por habilidad hasta 10, formación hasta 5, identidad 25, tope 100); `empresa.py:19-24`; `ruc.py:8-35` (11 dígitos, prefijos 10/15/17/20 y módulo 11); `nombre_completo.py:9-19`.
- `infrastructure/sqlalchemy_perfil_repository.py:15-115` (save, mapeo y JSON).
- `application/perfil_application_service.py:181-327` (constructores, update y guardas).
- `config.py:48-52`; `frameworks/flask_mvc/app.py:14-48`.
