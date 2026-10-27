# Convenciones de trabajo

Relacionado: [tablero](03-tablero-kanban.md), [reparto](04-reparto-equipo.md).

## Commits

Formato: `tipo(scope): verbo y objeto` en imperativo, breve. Tipos permitidos: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `build`, `ci`, `style`. Scope identifica capa/módulo: `domain-auth`, `infrastructure-matching`, `application-perfil`, `tests-config`.

Usar cuerpo para motivación/decisiones y footer `fix #<n>` con el issue asignado (la guía exige esta referencia). Para cerrar el issue automáticamente, usar `Closes #<n>` si el equipo confirma que acepta el formato GitHub; no sustituir el footer obligatorio.

Ejemplos:

- `test(domain-auth): cubrir límites de contraseña` + footer `fix #12`
- `test(infrastructure-perfil): probar persistencia en SQLite` + footer `fix #13`
- `test(application-convocatorias): aislar repositorios` + footer `fix #14`
- `docs(lab5): aclarar casos de expiración` + footer `fix #15`
- `refactor(tests-config): centralizar fixture de base temporal` + footer `fix #16`
- `chore(reports): guardar XML de JUnit y cobertura` + footer `fix #17`

No usar: `update`, `cambios`, `final`, `test: cosas`, `feat(all): ...`, ni número de PR como sustituto de `fix #<n>`. No afirmar `fix` si el commit solo agrega pruebas; preferir `test` y conservar el footer exigido.

## Gitflow

Crear `lab5/<capa>-<modulo>` desde `development` actualizado, siguiendo `lab9/` y `lab10/`. Un PR por rama hacia `development`; no abrir PR a `main`. Actualizar con `git fetch origin` y `git rebase origin/development` antes del PR (o resolver merge si el equipo/PR ya lo requiere). No reescribir una rama publicada sin coordinarlo.

Antes del primer commit, configurar identidad propia con `git config user.name "Nombre elegido"` y `git config user.email "correo verificado"`; comprobar `git config user.name` y `git config user.email`. No se imponen nombres personales en estos documentos.

## Prevención de conflictos

Después de Fase 0, cada integrante crea/modifica solo sus seis archivos de prueba asignados. No editar `conftest.py`, `pyproject.toml`, README, archivo monolítico integrado ni archivos de otras personas. Si surge una necesidad común, abrir/solicitar issue al responsable de integración; acordar el cambio antes de implementarlo.

Convención: `src/test/domain/test_<contexto>_domain.py`, `src/test/infrastructure/test_<contexto>_repository.py`, `src/test/application/test_<contexto>_service.py`; clases `TestNombreDeClase`, métodos `test_<regla>_<escenario>`. Mantener `unittest.TestCase`; ejecutar pytest.
