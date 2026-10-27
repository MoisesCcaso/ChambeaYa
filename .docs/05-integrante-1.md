# Integrante 1 — Auth

Relacionado: [reparto](04-reparto-equipo.md), [convenciones](02-convenciones.md), [reportes](11-reportes-y-entrega.md). Sin nombres propios: elijan su identidad Git.

## Alcance

Dominio: `domain/auth/usuario.py`, `token_recuperacion.py`, `autenticacion_dominio_servicio.py`. Repositorio: `infrastructure/sqlalchemy_usuario_repository.py`. Servicio: `application/usuario_application_service.py`. Pruebas propias: `tests/domain/test_auth_domain.py`, `tests/infrastructure/test_usuario_repository.py`, `tests/application/test_usuario_service.py`. No tomar ownership de interfaces, fixture, integración, configuración, correo SMTP concreto ni pruebas de otro integrante.

Rama: `lab5/domain-auth`, `lab5/infrastructure-usuario`, `lab5/application-usuario` (puede usar una sola rama si respeta el scope). Commits: prueba roja `test(domain-auth): cubrir login pendiente` + `fix #n`; verde/repositorio `test(infrastructure-usuario): persistir tokens` + `fix #n`; aplicación `test(application-usuario): verificar activación aislada` + `fix #n`.

Aplicar TDD rojo-verde-refactor. Casos recomendados (casos unitarios construibles sin módulos ajenos):

| Capa / caso | Dado / Cuando / Entonces; entrada y expectativa | Técnica / doble |
|---|---|---|
| Dominio `Usuario.registrar` | email, hash y tipo `practicante` → retorna mismo objeto; tipo inválido → `ValueError` | partición de equivalencia; sin doble |
| Dominio `AutenticacionDominioServicio.generar_password_hash` | `Aa123456` pasa; 7 caracteres, 129, o sin mayúscula/minúscula/dígito falla | valores límite: 8/128; sin doble |
| Dominio `TokenRecuperacion.esta_vigente` | expiración futura verdadera; expirada, valor vacío o expiración None falsa | transición/límite; `patch("domain.auth.token_recuperacion.datetime")` con `datetime.now.return_value` y timezone UTC |
| Repositorio `save/find_by_email` | instancia app TestingConfig, crear/guardar `Usuario`; buscar email devuelve campos y tipo; desconocido devuelve `None` | integración SQLite memoria; sin dobles |
| Repositorio tokens | persistir activation/reset token y consultar por cada valor; token ausente devuelve `None` | equivalencia; sin dobles |
| Servicio `register_user` | email con espacios/mayúsculas, contraseñas coincidentes; guarda usuario normalizado pendiente y llama `send_activation(email, token)` una vez | `create_autospec(IUsuarioRepository, instance=True, spec_set=True)`; autospec `IAuthEmailSender`; dominio auth real o autospec con hash/token deterministas; verificar argumentos |
| Servicio `recover_password` | usuario inexistente → `None`, sin guardar ni enviar; usuario existente → token de 2 horas, guarda y envía | mismos autospec; verificar `find_by_email`, `save`, `send_password_reset` |

Las interfaces existen en `domain/auth/i_usuario_repository.py` (`save`, búsquedas por email/id/tokens) y `domain/auth/i_auth_email_sender.py` (send_activation/send_password_reset); verificar nombres completos antes de crear autospec. Para `generate_token`, no afirmar token fijo; comprobar expiración y forma. Parche de tiempo exacto: el token consulta `datetime` en `domain.auth.token_recuperacion.datetime`; servicio auth usa `domain.auth.autenticacion_dominio_servicio.datetime`. No hay `uuid4` asignado a este contexto.

Meta por archivo: 80 % de líneas ejecutables; anotar covered/total medido en el baseline de Fase 0 y al cerrar el PR.

Riesgo: envío de correo puede lanzar `EmailDeliveryError`; aislar sender y cubrir traducción de error si cabe. Dependencia: ningún bloqueo, Perfil usa su propio autospec de `IUsuarioRepository`.

DoD: tres archivos exclusivos, reglas/casos descritos, SQLite para repositorio sin mocks, dobles con `spec_set`, suite pasa, reporte con líneas por archivo, PR integrado a development. Ver [11](11-reportes-y-entrega.md).

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

- `domain/auth/usuario.py:32-71`; `token_recuperacion.py:7-20`; `autenticacion_dominio_servicio.py:11-41`.
- `application/usuario_application_service.py:18-172` (inyección, registro, recuperación y activación).
- `infrastructure/sqlalchemy_usuario_repository.py:10-62`; interfaces `domain/auth/i_usuario_repository.py`, `domain/auth/i_auth_email_sender.py`.
- `config.py:48-52`; `frameworks/flask_mvc/app.py:14-48` (`create_app`, selección config, modelos importados); la suite actual gestiona `db.create_all/drop_all` en `tests/test_backend_integration.py:21-28`.
