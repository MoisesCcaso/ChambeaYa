# Integrante 6 — Certificación, postulaciones y notificaciones

Relacionado: [reparto](04-reparto-equipo.md), [convenciones](02-convenciones.md), [reportes](11-reportes-y-entrega.md).

## Alcance

Dominio `src/main/domain/certificacion/{certificado,archivo_pdf,codigo_qr,certificacion_dominio_servicio}.py`; repo `src/main/infrastructure/sqlalchemy_notificacion_repository.py`; servicios `src/main/application/certificacion_application_service.py`, `src/main/application/notificacion_application_service.py`. Tests: `src/test/domain/test_certificacion_domain.py`, `src/test/infrastructure/test_notificacion_repository.py`, `src/test/application/test_certificacion_service.py`, `src/test/application/test_notificacion_service.py`. Postulación se asigna a Integrante 3. Carga estimada de sus cuatro issues: 2 h (0.5 h cada uno).

Ramas: `lab5/domain-certificacion`, `lab5/infrastructure-notificacion`, `lab5/application-certificacion`, `lab5/application-notificacion`. Commits `test(domain-certificacion): validar contenido y QR` + `fix #n`; `test(infrastructure-notificacion): consultar y marcar lecturas` + `fix #n`; `test(application-certificacion): cubrir emisión` + `fix #n`; `test(application-notificacion): validar guardas de lectura` + `fix #n`.

TDD rojo-verde-refactor.

| Capa / regla | Dado / Cuando / Entonces | Técnica / doble |
|---|---|---|
| Dominio `CertificacionDominioServicio.generar_certificado` | práctica no finalizada o sin evaluación aprobada → ValueError; finalizada/aprobada → certificado PDF/QR | partición; fake simple de objetos dominio; patch `domain.certificacion.codigo_qr.uuid4` para UUID determinista |
| Dominio `ArchivoPDF.verificar_integridad` | contenido idéntico verifica, cambiado/None o hash vacío falla | equivalencia; sin doble |
| Dominio `CodigoQR.generar/verificar` | valor generado verifica solo valor correcto; valor alterado falla | equivalencia; patch `domain.certificacion.codigo_qr.uuid4` con objeto `.hex` controlado |
| Repo notificaciones | guardar, listar por usuario, unread y count; `mark_as_read` de otro usuario lanza ValueError; mark-all cambia solo pendientes del usuario | SQLite memoria; sin mocks |
| Servicio certificación `issue_certificate` | con dependencias válidas, devuelve `(certificado_existente, False)` si ya existe; si no, genera y guarda uno nuevo y devuelve `(certificado_guardado, True)` | Crear autospecs separados para los cinco contratos requeridos por el constructor: `ICertificadoRepository`, `IPracticaRepository`, `IPostulacionRepository`, `IConvocatoriaRepository` e `IPerfilRepository`. Configurar las búsquedas y `save`; verificar llamadas, argumentos y la tupla devuelta. Para el camino nuevo, usar dominio real y parchear `domain.certificacion.codigo_qr.uuid4` si se necesita un QR determinista |
| Servicio notificación | `list_notifications`, `mark_as_read`, `mark_all_as_read`, unread count; delega IDs y verifica guardas | autospec `INotificacionReader` y `INotificacionWriter`; interfaces segregadas |

El UUID es parcheable en `domain.certificacion.codigo_qr.uuid4`. `CertificacionApplicationService` requiere los cinco repositorios indicados en la tabla, aunque una ruta use solo algunos. Para servicios R9 no usar SQLite. Probar las llamadas directas de los servicios; los efectos disparados por las rutas corresponden a integración.

Meta: al menos 80 % de líneas ejecutables por archivo. Registrar las métricas observadas en el reporte de cobertura del PR.

Riesgo: Certificación usa cinco repositorios por inyección y Notificación separa writer/reader. Usar autospec locales; Postulación quedó con Integrante 3 por afinidad de módulo.

DoD: casos del dominio con UUID controlado, repo SQLite sin doubles, dos servicios autospec, no dependencias sobre tests ajenos, tiempo y cobertura informados, PR integrado.

## Reportes durante Fase 1

Puedes conservar localmente los reportes de tus ejecuciones para informar resultados en el issue o PR. Los artefactos dentro de `reports/` están en `.gitignore`: no los incluyas en tus commits de I-18–I-20 ni I-22. Se regenerarán y versionarán como reportes finales en I-23, después de integrar I-01–I-22; consulta [11-reportes-y-entrega.md](11-reportes-y-entrega.md).

## Checklist para retomar el trabajo

- [ ] Leer el estado de la tarjeta/issue asignado y confirmar que `development` está actualizado, con implementación en `src/main/` y pruebas en `src/test/`.
- [ ] Crear/actualizar la rama propia según [02-convenciones.md](02-convenciones.md); anotar el issue y el siguiente caso pendiente.
- [ ] Completar primero los casos de dominio con TDD: rojo, verde, refactor.
- [ ] Probar el repositorio contra SQLite en memoria, sin dobles.
- [ ] Probar el servicio asignado con autospec/dobles y comprobar retornos, llamadas y argumentos.
- [ ] Ejecutar los archivos propios y la suite unitaria; registrar el siguiente paso pendiente en el issue.
- [ ] Medir y anotar cobertura de los archivos asignados; no copiar porcentajes de reportes anteriores sin reproducirlos.
- [ ] Confirmar el DoD de esta guía, crear commits con `fix #<n>`, abrir PR a `development` y mover la tarjeta en el Project.

## Verificado

- `src/main/domain/certificacion/certificacion_dominio_servicio.py:7-29`; `certificado.py:5-19`; `archivo_pdf.py:4-28`; `codigo_qr.py:4-22` (importa `uuid4`, usa SHA-256).
- `src/main/infrastructure/sqlalchemy_notificacion_repository.py:12-99`; interfaces `src/main/domain/notificaciones/i_notificacion_reader.py:6-18`, `i_notificacion_writer.py:6-18`.
- Servicios: `src/main/application/certificacion_application_service.py:5-78` (constructor, emisión/verificación) y `src/main/application/notificacion_application_service.py:6-43` (writer/reader y 5 métodos). Postulación se verifica en la guía de Integrante 3.
- Interfaces asignadas: certificado `src/main/domain/certificacion/i_certificado_repository.py:4-20`; práctica `src/main/domain/practica_evaluacion/i_practica_repository.py:7-22`; notificación `src/main/domain/notificaciones/i_notificacion_reader.py:6-18` e `i_notificacion_writer.py:6-18`.
- `src/main/config.py:48-52`; `src/main/frameworks/flask_mvc/app.py:14-48`.
