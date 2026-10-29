# Reparto del equipo

R7 pide seis módulos de dominio; R8 seis repositorios; R9 seis servicios. El código contiene siete módulos de dominio, ocho repositorios y ocho servicios. Se asignan seis contextos verticales. Se deja el dominio de notificaciones fuera de R7: `Notificacion.marcar_como_leida` es un comportamiento mínimo y no justifica otra asignación de dominio en un equipo de seis; su repositorio y servicio sí se cubren como extensiones. Para repartir los módulos restantes sin un séptimo integrante, el repositorio de Postulación y su servicio van con Convocatorias (Integrante 3), mientras que el repositorio de Certificado va con Práctica (Integrante 5). Así se cubren los ocho repositorios y los ocho servicios; nadie recibe más de dos servicios.

## Métrica de carga reproducible

La métrica es la suma de horas estimadas en la tabla de issues de [03-tablero-kanban.md](03-tablero-kanban.md). Las pruebas R7–R9 de Fase 1 suman: Integrante 1 = 1.5 h, Integrante 2 = 1.5 h, Integrante 3 = 3 h, Integrante 4 = 1.5 h, Integrante 5 = 2 h e Integrante 6 = 2 h. En Fase 2, el issue de reportes añade 1 h a Integrante 1, para un total de 2.5 h en sus issues. Totales Fase 1–2: I1=2.5 h, I2=1.5 h, I3=3 h, I4=1.5 h, I5=2 h, I6=2 h. Suma total: 12.5 h; diferencia máxima aceptable: 2 h; diferencia observada: 1.5 h. Todas las cargas individuales quedan por debajo de las 4 h. Recalcular sumando duraciones si se edita el tablero.

## Matriz exclusiva de archivos de prueba

| Persona | Dominio — archivo nuevo | Repositorio — archivo nuevo | Servicio(s) aplicación — archivo nuevo(s) |
|---|---|---|---|
| Integrante 1 | `src/test/domain/test_auth_domain.py` | `src/test/infrastructure/test_usuario_repository.py` | `src/test/application/test_usuario_service.py` |
| Integrante 2 | `src/test/domain/test_perfil_domain.py` | `src/test/infrastructure/test_perfil_repository.py` | `src/test/application/test_perfil_service.py` |
| Integrante 3 | `src/test/domain/test_convocatorias_domain.py` | `src/test/infrastructure/test_convocatoria_repository.py`, `src/test/infrastructure/test_postulacion_repository.py` | `src/test/application/test_convocatoria_service.py`, `src/test/application/test_postulacion_service.py` |
| Integrante 4 | `src/test/domain/test_matching_domain.py` | `src/test/infrastructure/test_matching_repository.py` | `src/test/application/test_matching_service.py` |
| Integrante 5 | `src/test/domain/test_practica_evaluacion_domain.py` | `src/test/infrastructure/test_practica_repository.py`, `src/test/infrastructure/test_certificado_repository.py` | `src/test/application/test_practica_service.py` |
| Integrante 6 | `src/test/domain/test_certificacion_domain.py` | `src/test/infrastructure/test_notificacion_repository.py` | `src/test/application/test_certificacion_service.py`, `src/test/application/test_notificacion_service.py` |

Cada ruta aparece una sola vez. `src/test/integration/test_backend_integration.py` y `src/test/conftest.py` son archivos compartidos ya preparados; ningún integrante los edita.

## Módulos de código (rutas exactas)

| Persona | Dominio | Repositorio | Servicios de aplicación |
|---|---|---|---|
| 1 | `src/main/domain/auth/{usuario,token_recuperacion,autenticacion_dominio_servicio}.py` | `src/main/infrastructure/sqlalchemy_usuario_repository.py` | `src/main/application/usuario_application_service.py` |
| 2 | `src/main/domain/perfil/{practicante,empresa,ruc,nombre_completo}.py` | `src/main/infrastructure/sqlalchemy_perfil_repository.py` | `src/main/application/perfil_application_service.py` |
| 3 | `src/main/domain/convocatorias/{convocatoria,convocatoria_fabrica,postulacion}.py` | `src/main/infrastructure/sqlalchemy_convocatoria_repository.py`; `src/main/infrastructure/sqlalchemy_postulacion_repository.py` | `src/main/application/convocatoria_application_service.py`; `src/main/application/postulacion_application_service.py` |
| 4 | `src/main/domain/matching/{sugerencia,resultado_matching,matching_dominio_servicio}.py` | `src/main/infrastructure/sqlalchemy_matching_repository.py` | `src/main/application/matching_application_service.py` |
| 5 | `src/main/domain/practica_evaluacion/{practica,practica_fabrica,entregable,evaluacion}.py` | `src/main/infrastructure/sqlalchemy_practica_repository.py`; `src/main/infrastructure/sqlalchemy_certificado_repository.py` | `src/main/application/practica_application_service.py` |
| 6 | `src/main/domain/certificacion/{certificado,archivo_pdf,codigo_qr,certificacion_dominio_servicio}.py` | `src/main/infrastructure/sqlalchemy_notificacion_repository.py` | `src/main/application/certificacion_application_service.py`, `src/main/application/notificacion_application_service.py` |

## Dependencias y cómo no bloquearse

- Auth (`IUsuarioRepository`) es consumido por perfil, postulación y certificación; esos servicios usan autospec local de la interfaz, nunca importan pruebas/clases de Integrante 1.
- Perfil es consumido por convocatorias, postulación y matching (`IPerfilRepository`); sus pruebas de aplicación construyen doubles locales.
- Convocatoria/Postulación se conectan en los servicios de postulación y práctica. Integrante 3 cubre el servicio de Postulación junto con Convocatorias; Integrante 5 lo aísla dentro de Práctica y usa autospec de la interfaz, sin depender de tests ajenos.
- Práctica es consumida por certificación; Integrante 6 usa fake/autospec `IPracticaRepository` para su servicio. `IPracticaRepository` está en `src/main/domain/practica_evaluacion/`.
- Matching usa perfil, convocatoria y sugerencia; simular cada interfaz.
- `SqlAlchemyNotificacionRepository` implementa `INotificacionWriter` y `INotificacionReader`; Integrante 6 cubre escritura/lectura sin mocks.

R8 siempre usa SQLite en memoria y ORM/modelos existentes; sin mocks. R9 siempre usa doubles de repositorio (`create_autospec(Interfaz, instance=True, spec_set=True)`); verificar método, argumentos y retorno. Para correo usar autospec `IAuthEmailSender`. No mockear modelos SQLAlchemy en R8.

### Criterio para meta de cobertura

Meta por archivo: al menos 80 % de líneas ejecutables. Medir el baseline antes de escribir pruebas y registrar numerador/denominador al inicio y al cierre del PR. Cada guía individual enumera las reglas que deben cubrirse.
