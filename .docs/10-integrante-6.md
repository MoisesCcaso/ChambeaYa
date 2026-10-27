# Integrante 6 — Certificación, postulaciones y notificaciones

Relacionado: [reparto](04-reparto-equipo.md), [convenciones](02-convenciones.md), [reportes](11-reportes-y-entrega.md).

## Alcance

Dominio `domain/certificacion/{certificado,archivo_pdf,codigo_qr,certificacion_dominio_servicio}.py`; repo `infrastructure/sqlalchemy_notificacion_repository.py`; servicios `application/certificacion_application_service.py`, `application/notificacion_application_service.py`. Tests: `tests/domain/test_certificacion_domain.py`, `tests/infrastructure/test_notificacion_repository.py`, `tests/application/test_certificacion_service.py`, `tests/application/test_notificacion_service.py`. Postulación se asigna a Integrante 3. Carga estimada: 1.5 h.

Ramas: `lab5/domain-certificacion`, `lab5/infrastructure-notificacion`, `lab5/application-certificacion`, `lab5/application-notificacion`. Commits `test(domain-certificacion): validar contenido y QR` + `fix #n`; `test(infrastructure-notificacion): consultar y marcar lecturas` + `fix #n`; `test(application-certificacion): cubrir emisión` + `fix #n`; `test(application-notificacion): validar guardas de lectura` + `fix #n`.

TDD rojo-verde-refactor.

| Capa / regla | Dado / Cuando / Entonces | Técnica / doble |
|---|---|---|
| Dominio `CertificacionDominioServicio.generar_certificado` | práctica no finalizada o sin evaluación aprobada → ValueError; finalizada/aprobada → certificado PDF/QR | partición; fake simple de objetos dominio; patch `domain.certificacion.codigo_qr.uuid4` para UUID determinista |
| Dominio `ArchivoPDF.verificar_integridad` | contenido idéntico verifica, cambiado/None o hash vacío falla | equivalencia; sin doble |
| Dominio `CodigoQR.generar/verificar` | valor generado verifica solo valor correcto; valor alterado falla | equivalencia; patch `domain.certificacion.codigo_qr.uuid4` con objeto `.hex` controlado |
| Repo notificaciones | guardar, listar por usuario, unread y count; `mark_as_read` de otro usuario lanza ValueError; mark-all cambia solo pendientes del usuario | SQLite memoria; sin mocks |
| Servicio certificación | práctica finalizada+aprobada devuelve existente o guarda nuevo certificado según camino; verificar ID | `create_autospec(ICertificadoRepository, instance=True, spec_set=True)` y `IPracticaRepository`; verificar llamadas y argumentos |
| Servicio notificación | `list_notifications`, `mark_as_read`, `mark_all_as_read`, unread count; delega IDs y verifica guardas | autospec `INotificacionReader` y `INotificacionWriter`; interfaces segregadas |

El UUID es parcheable en domain.certificacion.codigo_qr.uuid4. Para servicios R9 no usar SQLite. Probar las llamadas directas de los servicios; los efectos disparados por las rutas corresponden a integración.

Meta: al menos 80 % de líneas ejecutables por archivo. Registrar las métricas observadas en el reporte de cobertura del PR.

Riesgo: Certificación usa cinco repositorios por inyección y Notificación separa writer/reader. Usar autospec locales; Postulación quedó con Integrante 3 por afinidad de módulo.

DoD: casos del dominio con UUID controlado, repo SQLite sin doubles, dos servicios autospec, no dependencias sobre tests ajenos, tiempo y cobertura informados, PR integrado.

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

- `domain/certificacion/certificacion_dominio_servicio.py:7-29`; `certificado.py:5-19`; `archivo_pdf.py:4-28`; `codigo_qr.py:4-22` (importa `uuid4`, usa SHA-256).
- `infrastructure/sqlalchemy_notificacion_repository.py:12-99`; interfaces `domain/notificaciones/i_notificacion_reader.py:6-18`, `i_notificacion_writer.py:6-18`.
- Servicios: `application/certificacion_application_service.py:5-78` (constructor, emisión/verificación) y `application/notificacion_application_service.py:6-43` (writer/reader y 5 métodos). Postulación se verifica en la guía de Integrante 3.
- Interfaces asignadas: certificado `domain/certificacion/i_certificado_repository.py:4-20`; práctica `domain/practica_evaluacion/i_practica_repository.py:7-22`; notificación `domain/notificaciones/i_notificacion_reader.py:6-18` e `i_notificacion_writer.py:6-18`.
- `config.py:48-52`; `frameworks/flask_mvc/app.py:14-48`.
