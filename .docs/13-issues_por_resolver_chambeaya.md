# Issues por resolver — ChambeaYa

Lista consolidada de los issues que el equipo va a solucionar. Reúne tres fuentes:

1. **Auditoría manual** — 35 hallazgos que SonarQube no detecta, con IDs `S` (seguridad), `B` (bugs), `R` (rendimiento) y `D` (diseño).
2. **Catálogo de 24 code smells de diseño y arquitectura** — sección *Catálogo de los 24 Code Smells*, con su estrategia de refactoring.
3. **Catálogo de 12 incidencias de SonarQube** — sección *Catálogo de las 12 Incidencias*, priorizadas a partir de `sonar-reporte.md` (34 incidencias en 9 reglas, IDs `SQ1`–`SQ9`).

## Resumen de la auditoría manual

- **35 hallazgos**: 2 de gravedad crítica, 5 de gravedad alta, 9 de gravedad media, 19 de gravedad baja
- **3 verificados ejecutando la app** en una base de datos en memoria (marcados con *Sí*).
- **Prioridad:** Atender primero S1 y S2: son los únicos con los que alguien de fuera puede sacar datos o tomar una cuenta sin ninguna credencial.

| ID | Error | Dónde | Gravedad | Verificado |
|---|---|---|---|---|
| S1 | Certificados descargables sin iniciar sesión | `routes/certificado_routes.py:113-141` | Crítica | Sí |
| S2 | Configuración por defecto insegura | `config.py:83, frameworks/flask_mvc/app.py:24` | Crítica | - |
| S3 | Tokens de autenticación escritos en los logs | `infrastructure/smtp_auth_email_sender.py:133` | Alta | - |
| S4 | El login revela qué cuentas existen | `domain/auth/autenticacion_dominio_servicio.py:33-34` | Alta | Sí |
| S8 | La verificación de certificados no verifica nada | `domain/certificacion/codigo_qr.py:18-22, application/certificacion_application_service.py:52-58` | Alta | - |
| S9 | flask seed-demo funciona en producción | `frameworks/flask_mvc/app.py:44, frameworks/flask_mvc/demo.py:236` | Alta | - |
| B1 | Operaciones de varios pasos sin transacción | `application/postulacion_application_service.py:103-113` | Alta | - |
| S5 | Tokens guardados en texto plano | `models/usuario_model.py, infrastructure/sqlalchemy_usuario_repository.py:40-46` | Media | - |
| S6 | Las sesiones no se pueden revocar | `routes/auth_routes.py (sesión Flask)` | Media | - |
| S7 | Sin límite de intentos ni de correos | `/auth/login, /auth/recover-password, /auth/resend-activation` | Media | - |
| S10 | SMTP sin TLS manda la contraseña sin cifrar | `infrastructure/smtp_auth_email_sender.py:174-182` | Media | - |
| B2 | El servicio se salta las reglas del dominio | `application/postulacion_application_service.py:112` | Media | - |
| B3 | Nombres en blanco permiten postular y certificar | `application/perfil_application_service.py:27-30` | Media | Sí |
| B4 | Rechazar una postulación puede dar 500 después de guardarla | `routes/postulacion_routes.py:159-170` | Media | - |
| B5 | Notificaciones de nuevas sugerencias repetidas sin fin | `routes/matching_routes.py:58-66` | Media | - |
| R1 | Consultas N+1 (una consulta extra por cada fila) | `servicios de postulación y práctica` | Media | - |
| B6 | La tabla sugerencias se escribe pero nunca se lee | `application/matching_application_service.py:32-33` | Baja | - |
| B7 | Un RUC enviado como número se rechaza | `application/perfil_application_service.py:82, domain/perfil/ruc.py:17` | Baja | - |
| B8 | Fechas con y sin zona horaria mezcladas (latente) | `models/entregable_model.py, models/evaluacion_model.py` | Baja | - |
| B9 | Longitudes de texto sin validar (latente) | `modelos: título 180, nombres 120, carnet 40, archivo 255` | Baja | - |
| R2 | El matching carga todas las convocatorias | `application/matching_application_service.py:19` | Baja | - |
| D1 | El dominio depende del framework | `domain/auth/autenticacion_dominio_servicio.py:8` | Baja | - |
| D2 | Lógica de negocio en las rutas | `frameworks/flask_mvc/routes/` | Baja | - |
| D3 | La misma regla en dos capas | `routes/postulacion_routes.py:95-105 y su servicio` | Baja | - |
| D4 | Control de dueño copiado a mano | `select_candidate:84, evaluate:65, publish:24` | Baja | - |
| D5 | Validación duplicada entre fábrica y entidad | `domain/convocatorias/convocatoria_fabrica.py y convocatoria.py` | Baja | - |
| D6 | Serializadores JSON copiados | `repositorios de perfil, convocatoria y matching` | Baja | - |
| D7 | Código muerto | `notificacion.py:5-8, nombre_completo.py, postulacion.py:16, auth_routes.py:65` | Baja | - |
| D8 | Nombres que engañan | `varios` | Baja | - |
| D9 | Bloques duplicados en las rutas | `frameworks/flask_mvc/routes/ (8 módulos)` | Baja | - |
| D10 | Códigos HTTP equivocados | `rutas` | Baja | - |
| D11 | Estados y tipos como texto suelto | `rutas de convocatoria, postulación y perfil` | Baja | - |
| D12 | Métodos y constructores demasiado grandes | `demo.py:58, domain/auth/usuario.py:10` | Baja | - |
| D13 | Generalidad especulativa | `domain/, application/, presentation/` | Baja | - |
| D14 | Detalles sueltos | `varios` | Baja | - |

## Seguridad

### S1 - Certificados descargables sin iniciar sesión (verificado)

- **Dónde:** `routes/certificado_routes.py:113-141`
- **Gravedad:** Crítica

GET /certificados/practica/<id>/pdf no comprueba sesión ni dueño. Probado: sin login responde 200 con el PDF, mientras la ruta hermana /certificados/practica/<id> responde 401. Los IDs son secuenciales, así que se pueden descargar todos y obtener el nombre de cada practicante y su código de verificación.

### S2 - Configuración por defecto insegura

- **Dónde:** `config.py:83, frameworks/flask_mvc/app.py:24`
- **Gravedad:** Crítica

Si FLASK_ENV falta o está mal escrito ("produccion", "prod"), se carga DevelopmentConfig en silencio: DEBUG=True y EXPOSE_AUTH_TOKENS=True. Con eso, POST /auth/recover-password con el email de otra persona devuelve su token de reseteo en la respuesta, lo que permite tomar cualquier cuenta.

### S3 - Tokens de autenticación escritos en los logs

- **Dónde:** `infrastructure/smtp_auth_email_sender.py:133`
- **Gravedad:** Alta

El modo console, que es el valor por defecto, hace logger.info con el enlace completo de activación o reseteo. Cualquiera con acceso a los logs puede usarlos.

### S4 - El login revela qué cuentas existen (verificado)

- **Dónde:** `domain/auth/autenticacion_dominio_servicio.py:33-34`
- **Gravedad:** Alta

usuario.login() se ejecuta antes de comprobar la contraseña. Probado con una contraseña al azar: un email inexistente responde "Credenciales inválidas" y una cuenta pendiente responde "La cuenta no está activa". El registro también lo revela ("El correo ya está registrado").

### S5 - Tokens guardados en texto plano

- **Dónde:** `models/usuario_model.py, infrastructure/sqlalchemy_usuario_repository.py:40-46`
- **Gravedad:** Media

Los tokens de activación y reseteo se guardan y buscan tal cual. Si se filtra la base de datos, todos los tokens vigentes sirven directamente.

### S6 - Las sesiones no se pueden revocar

- **Dónde:** `routes/auth_routes.py (sesión Flask)`
- **Gravedad:** Media

La sesión es una cookie firmada que solo contiene usuario_id. Cambiar la contraseña no cierra las sesiones abiertas en otros dispositivos, y ninguna ruta vuelve a comprobar si la cuenta sigue activa.

### S7 - Sin límite de intentos ni de correos

- **Dónde:** `/auth/login, /auth/recover-password, /auth/resend-activation`
- **Gravedad:** Media

Permite fuerza bruta de contraseñas y mandar correos sin límite a la bandeja de cualquiera: cada resend-activation envía uno nuevo.

### S8 - La verificación de certificados no verifica nada

- **Dónde:** `domain/certificacion/codigo_qr.py:18-22, application/certificacion_application_service.py:52-58`
- **Gravedad:** Alta

El certificado se busca por su código y después se compara valor == código, que siempre es cierto. El hash es sha256(dato) sin secreto (no es un HMAC): quien edite la base de datos recalcula el hash y el certificado sigue pasando como válido. El documento se compara contra su propia copia guardada, así que el error 409 "perdió su integridad" nunca se puede producir.

### S9 - flask seed-demo funciona en producción

- **Dónde:** `frameworks/flask_mvc/app.py:44, frameworks/flask_mvc/demo.py:236`
- **Gravedad:** Alta

El comando se registra siempre, sin mirar DEMO_MODE. En producción crea cuentas activas con contraseña conocida. Sonar marcó la contraseña escrita en el código (S6437), pero no que falte esta protección.

### S10 - SMTP sin TLS manda la contraseña sin cifrar

- **Dónde:** `infrastructure/smtp_auth_email_sender.py:174-182`
- **Gravedad:** Media

Con MAIL_USE_TLS=false, el login() al servidor de correo viaja en texto plano y nada lo avisa.


## Bugs e integridad de datos

### B1 - Operaciones de varios pasos sin transacción

- **Dónde:** `application/postulacion_application_service.py:103-113`
- **Gravedad:** Alta

Todos los save() de los repositorios hacen commit(). select_candidate guarda la postulación seleccionada y luego cada una de las otras por separado; si algo falla a mitad, una convocatoria puede quedar con dos candidatos seleccionados. Pasa lo mismo en calculate_for_practicante.

### B2 - El servicio se salta las reglas del dominio

- **Dónde:** `application/postulacion_application_service.py:112`
- **Gravedad:** Media

otra.estado = ESTADO_RECHAZADA asigna el estado a mano, cuando Postulacion.rechazar() lo prohíbe explícitamente ("Solo una postulación pendiente puede rechazarse").

### B3 - Nombres en blanco permiten postular y certificar (verificado)

- **Dónde:** `application/perfil_application_service.py:27-30`
- **Gravedad:** Media

"   " se guarda tal cual y pasa el filtro de apply(), porque un string con espacios cuenta como verdadero. Probado. El certificado sale como "Se certifica que      completó...". La clase NombreCompleto, que sí quita los espacios, existe pero no se usa en ningún sitio.

### B4 - Rechazar una postulación puede dar 500 después de guardarla

- **Dónde:** `routes/postulacion_routes.py:159-170`
- **Gravedad:** Media

Es la única de las 8 rutas que crea la notificación sin try/except. Si falla la notificación, el rechazo ya quedó guardado, pero el cliente recibe un 500.

### B5 - Notificaciones de nuevas sugerencias repetidas sin fin

- **Dónde:** `routes/matching_routes.py:58-66`
- **Gravedad:** Media

Cada llamada a /matching/calcular crea una notificación nueva sin leer, aunque las sugerencias sean las mismas de antes.

### B6 - La tabla sugerencias se escribe pero nunca se lee

- **Dónde:** `application/matching_application_service.py:32-33`
- **Gravedad:** Baja

Nada consulta las sugerencias guardadas, y tampoco se borran cuando dejan de ser válidas.

### B7 - Un RUC enviado como número se rechaza

- **Dónde:** `application/perfil_application_service.py:82, domain/perfil/ruc.py:17`
- **Gravedad:** Baja

{"ruc": 20100070970} en JSON llega como int y no pasa isinstance(numero, str). Responde "El RUC no es válido" aunque el RUC sea correcto.

### B8 - Fechas con y sin zona horaria mezcladas (latente)

- **Dónde:** `models/entregable_model.py, models/evaluacion_model.py`
- **Gravedad:** Baja

Estos modelos usan DateTime sin timezone=True, mientras el dominio crea fechas con zona y el resto de modelos la guarda. Ordenar un historial que mezcle ambos tipos lanza TypeError.

### B9 - Longitudes de texto sin validar (latente)

- **Dónde:** `modelos: título 180, nombres 120, carnet 40, archivo 255`
- **Gravedad:** Baja

SQLite guarda el texto aunque exceda el límite. En PostgreSQL saltaría un DataError que nadie captura (solo se maneja IntegrityError) y el usuario vería un 500.


## Rendimiento

### R1 - Consultas N+1 (una consulta extra por cada fila)

- **Dónde:** `servicios de postulación y práctica`
- **Gravedad:** Media

list_for_convocatoria hace 2 por postulación; list_for_practicante, 1 por postulación; practica.list_for_user de empresa tiene tres bucles anidados; select_postulacion consulta dentro de un bucle; download_deliverable carga todos los entregables para quedarse con uno.

### R2 - El matching carga todas las convocatorias

- **Dónde:** `application/matching_application_service.py:19`
- **Gravedad:** Baja

find_all() trae también borradores y cerradas, y las filtra en Python en lugar de hacerlo en la consulta SQL.


## Diseño y code smells

### D1 - El dominio depende del framework

- **Dónde:** `domain/auth/autenticacion_dominio_servicio.py:8`
- **Gravedad:** Baja

La capa de dominio importa werkzeug, rompiendo la arquitectura hexagonal.

### D2 - Lógica de negocio en las rutas

- **Dónde:** `frameworks/flask_mvc/routes/`
- **Gravedad:** Baja

8 bloques de notificación, el cálculo de otras_pendientes, la escritura de archivos en disco y la generación del PDF del certificado viven en la capa web.

### D3 - La misma regla en dos capas

- **Dónde:** `routes/postulacion_routes.py:95-105 y su servicio`
- **Gravedad:** Baja

"Seleccionar a uno rechaza al resto" está en el servicio y se recalcula en la ruta para poder notificar.

### D4 - Control de dueño copiado a mano

- **Dónde:** `select_candidate:84, evaluate:65, publish:24`
- **Gravedad:** Baja

Ya existen _require_owned_convocatoria, _require_empresa_owner y _find_owned, pero no se usan ahí; cada copia tiene además un mensaje de error distinto.

### D5 - Validación duplicada entre fábrica y entidad

- **Dónde:** `domain/convocatorias/convocatoria_fabrica.py y convocatoria.py`
- **Gravedad:** Baja

ConvocatoriaFabrica y Convocatoria.actualizar hacen la misma validación con los mismos mensajes.

### D6 - Serializadores JSON copiados

- **Dónde:** `repositorios de perfil, convocatoria y matching`
- **Gravedad:** Baja

_dump_list y _load_list están copiados en 3 repositorios.

### D7 - Código muerto

- **Dónde:** `notificacion.py:5-8, nombre_completo.py, postulacion.py:16, auth_routes.py:65`
- **Gravedad:** Baja

Constantes TIPO_* de notificación (0 usos), NombreCompleto (0 usos), Postulacion.aceptar() (solo la usa un test) y data.pop("password_reset_token") sobre una respuesta que nunca tiene esa clave.

### D8 - Nombres que engañan

- **Dónde:** `varios`
- **Gravedad:** Baja

ArchivoPDF guarda texto, no un PDF; autenticar() parece devolver un booleano pero lanza excepción; calcular_score() modifica el estado; find_by_practicante_id y find_practicante_by_id hacen cosas distintas.

### D9 - Bloques duplicados en las rutas

- **Dónde:** `frameworks/flask_mvc/routes/ (8 módulos)`
- **Gravedad:** Baja

El bloque de autenticación está copiado 44 veces y el except ValueError 50 veces. Sonar solo vio el texto "No autenticado" repetido (S1192), no la estructura duplicada.

### D10 - Códigos HTTP equivocados

- **Dónde:** `rutas`
- **Gravedad:** Baja

"No encontrado" y "no autorizado" responden 400 en lugar de 404 o 403.

### D11 - Estados y tipos como texto suelto

- **Dónde:** `rutas de convocatoria, postulación y perfil`
- **Gravedad:** Baja

"publicada", "pendiente" y "empresa" escritos a mano en vez de usar las constantes del dominio; el tipo de notificación no se valida.

### D12 - Métodos y constructores demasiado grandes

- **Dónde:** `demo.py:58, domain/auth/usuario.py:10`
- **Gravedad:** Baja

seed_demo_data tiene 179 líneas y escribe directo en el ORM saltándose el dominio. Usuario.__init__ recibe 10 parámetros.

### D13 - Generalidad especulativa

- **Dónde:** `domain/, application/, presentation/`
- **Gravedad:** Baja

10 interfaces con una sola implementación, Reader y Writer recibiendo el mismo objeto, PracticaFabrica con un único método, y constructores con =None que obligan a poner guardas en 16 clases.

### D14 - Detalles sueltos

- **Dónde:** `varios`
- **Gravedad:** Baja

Errata "# -*- coding: utf-8 -*-}" en practica_application_service.py:2; 52 archivos con shebang inútil; indentación inconsistente en postulacion.py:11-14 y sqlalchemy_perfil_repository.py:89-98; el correo de prueba dice "Gmail" fijo aunque el servidor sea otro.

## Lo que está bien

El frontend escapa todo el HTML (escapeHTML en 37 sitios, textContent en los diálogos): no se encontró XSS. Las subidas de archivos tienen lista blanca de extensiones, secure_filename y límite de 10 MB. La cookie de sesión lleva HttpOnly y SameSite=Lax.

## Nota sobre el reporte de SonarQube

La incidencia de Sonar S4830 en smtp_auth_email_sender.py:176 parece un falso positivo: starttls() usa ssl.create_default_context(), que sí valida el certificado. El riesgo real en esa zona es S10.


## Catálogo de los 24 Code Smells de Diseño y Arquitectura más Críticos (lab_Issues.md)

Esta sección consolida y formaliza los 24 code smells de diseño orientado a objetos y arquitectura que SonarQube no detecta en el proyecto, combinando las reinterpretaciones técnicas de hallazgos previos con los nuevos descubrimientos de diseño.

### Tabla Comparativa de los 24 Code Smells

| N° | Smell / Incidencia | Clasificación (Tipo-Subtipo) | Dónde | Gravedad | Coincide con | Verificado |
|---|---|---|---|---|---|---|
| 1 | Instanciación directa de persistencia concreta en la capa web | SOLID-DIP | `frameworks/flask_mvc/routes/*.py` | Alta | Inédito | Sí |
| 2 | Feature Envy y orquestación en emisión de certificados | Coupler-Feature Envy | `routes/certificado_routes.py:58-77` | Alta | D2 | Sí |
| 3 | Feature Envy y orquestación en selección de candidatos | Coupler-Feature Envy | `routes/postulacion_routes.py:93-130` | Alta | D2, D3 | Sí |
| 4 | Feature Envy y orquestación en evaluación de prácticas | Coupler-Feature Envy | `routes/practica_routes.py:112-129` | Alta | D2 | Sí |
| 5 | Interfaz gruesa que mezcla agregados de dominio distintos | SOLID-ISP | `domain/perfil/i_perfil_repository.py:7-26` | Alta | Inédito | Sí |
| 6 | Múltiples motivos de cambio en servicio de perfiles | Change Preventer-Divergent Change | `application/perfil_application_service.py` | Alta | Inédito | Sí |
| 7 | Travesía en cadena a través de agregados ajenos | Coupler-Message Chains | `application/practica_application_service.py:114-121` | Alta | R1 | Sí |
| 8 | Descomposición de Value Object en datos primitivos | Bloater-Data Clumps | `domain/auth/usuario.py:27-30, 54-62` | Media | D12 | Sí |
| 9 | Obsesión primitiva en nombres y Value Object huérfano | Bloater-Primitive Obsession | `domain/perfil/practicante.py:20, nombre_completo.py` | Media | D7, B3 | Sí |
| 10 | Intermediario innecesario en verificación de código QR | Coupler-Middle Man | `domain/certificacion/certificacion_dominio_servicio.py:20-23` | Media | Inédito | Sí |
| 11 | Fábrica perezosa sin justificación arquitectónica | Dispensable-Lazy Class | `domain/practica_evaluacion/practica_fabrica.py:7-16` | Media | D13 | Sí |
| 12 | Controladores de presentación como intermediarios anémicos | Coupler-Middle Man | `presentation/*_controller.py` | Media | Inédito | Sí |
| 13 | Contenedor de datos anémico y redundante | Dispensable-Data Class | `domain/matching/resultado_matching.py:1-11` | Media | Inédito | Sí |
| 14 | Bolsas de datos genéricas no tipadas en servicios de aplicación | Bloater-Primitive Obsession | `application/convocatoria_application_service.py:10` | Media | Inédito | Sí |
| 15 | Duplicación algorítmica en sincronización de modelos ORM | Dispensable-Duplicate Code | `infrastructure/sqlalchemy_practica_repository.py:29-64` | Media | Inédito | Sí |
| 16 | Acoplamiento de entidades de dominio a rutas HTTP | SOLID-DIP | `domain/certificacion/archivo_pdf.py:16, codigo_qr.py:14` | Media | Inédito | Sí |
| 17 | Violación de encapsulamiento y Feature Envy en cálculo de score | Coupler-Feature Envy | `application/perfil_application_service.py:50, 57` | Media | Inédito | Sí |
| 18 | Algoritmo de matching rígido sin extensibilidad | SOLID-OCP | `domain/matching/sugerencia.py:10-33` | Media | Inédito | Sí |
| 19 | Ruptura de invariantes mediante mutación directa de estado | SOLID-LSP | `application/postulacion_application_service.py:112` | Media | B2 | Sí |
| 20 | Validación de atributos duplicada entre fábrica y entidad | Dispensable-Duplicate Code | `domain/convocatorias/convocatoria_fabrica.py:8-18` | Baja | D5 | Sí |
| 21 | Capa de dominio acoplada a biblioteca externa de la web | SOLID-DIP | `domain/auth/autenticacion_dominio_servicio.py:8` | Baja | D1 | Sí |
| 22 | Retorno de tuplas posicionales anónimas en casos de uso | Bloater-Primitive Obsession | `application/postulacion_application_service.py:53, 66` | Baja | Inédito | Sí |
| 23 | Operaciones de múltiples pasos sin abstracción transaccional | SOLID-SRP | `application/postulacion_application_service.py:103-114` | Baja | B1 | Sí |
| 24 | Estado temporal dependiente del ciclo de vida en entidad | Object-Orientation Abuser-Temporary Field | `domain/convocatorias/convocatoria.py:32, 47, 55` | Baja | Inédito | Sí |

### Detalle de los 24 Hallazgos

**1. Instanciación directa de persistencia concreta en la capa web (SOLID-DIP)**: Las funciones de rutas de Flask instancian directamente con constructores concretos adaptadores de infraestructura (`SqlAlchemyPracticaRepository`, `SqlAlchemyPerfilRepository`, etc.) en cada petición entrante en lugar de recibir abstracciones inyectadas. Esto acopla la capa de presentación a SQLAlchemy e impide sustituir la persistencia por dobles de prueba o almacenes alternativos. SonarQube no detecta violaciones de inversión de dependencias ni acoplamiento entre capas arquitectónicas.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/routes/*.py` (especialmente `practica_routes.py:28-36`, `convocatoria_routes.py:25-30`, `postulacion_routes.py:33-38`), funciones constructoras `build_*_controller()`
**Estrategia de Refactoring**: Introduce Parameter Object: agrupar las dependencias de persistencia en un contenedor de inyección y pasarlas a la capa de rutas mediante una fábrica o inyector centralizado.

**2. Feature Envy y orquestación en emisión de certificados (Coupler-Feature Envy)**: Tras ejecutar la emisión del certificado, la función de ruta HTTP consulta múltiples repositorios (`SqlAlchemyPracticaRepository`, `SqlAlchemyPerfilRepository`), navega para obtener el `usuario_id` del practicante, instancia el servicio de notificaciones y despacha el mensaje `CERTIFICADO_EMITIDO`. La ruta depende más de los métodos y datos de `Practica`, `Perfil` y `Notificacion` que de sus propias responsabilidades HTTP. SonarQube no analiza la afinidad de datos ni la fuga de lógica de negocio hacia controladores web.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/routes/certificado_routes.py`, función `issue_certificado` (líneas 58-77)
**Estrategia de Refactoring**: Move Method: mover la lógica de orquestación y envío de notificación al caso de uso `CertificacionApplicationService.issue_certificate`, delegando a un método privado `_notificar_emision`.

**3. Feature Envy y orquestación en selección de candidatos (Coupler-Feature Envy)**: En el endpoint `select_postulacion`, la ruta web consulta `SqlAlchemyPostulacionRepository`, filtra manualmente las postulaciones que quedarán rechazadas (`otras_pendientes`), y orquesta el envío de notificaciones tanto al postulante seleccionado como a los descartados. La ruta asume responsabilidades del caso de uso. SonarQube no detecta responsabilidades mal asignadas entre capas.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/routes/postulacion_routes.py`, función `select_postulacion` (líneas 93-130)
**Estrategia de Refactoring**: Move Method: mover la consulta de postulaciones afectadas y el envío de notificaciones hacia `PostulacionApplicationService.select_candidate`.

**4. Feature Envy y orquestación en evaluación de prácticas (Coupler-Feature Envy)**: Al registrar una evaluación con éxito, la ruta HTTP recupera el identificador del practicante, consulta `SqlAlchemyPerfilRepository` para resolver su `usuario_id`, instancia `NotificacionApplicationService` y construye la notificación `EVALUACION_DISPONIBLE`. La ruta coordina efectos colaterales de negocio en lugar de limitarse al protocolo HTTP. SonarQube no distingue entre orquestación de aplicación y enrutamiento web.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/routes/practica_routes.py`, función `register_evaluation` (líneas 112-129)
**Estrategia de Refactoring**: Move Method: trasladar el flujo de notificación hacia `PracticaApplicationService.evaluate`.

**5. Interfaz gruesa que mezcla agregados de dominio distintos (SOLID-ISP)**: La interfaz `IPerfilRepository` reúne operaciones pertenecientes a dos raíces de agregado conceptualmente distintas: `Practicante` (`save_practicante`, `find_practicante_by_user_id`, `find_practicante_by_id`) y `Empresa` (`save_empresa`, `find_empresa_by_user_id`). Servicios como `PostulacionApplicationService` o `MatchingApplicationService`, que únicamente requieren información del practicante, quedan forzados a depender de un contrato que incluye operaciones de empresa. SonarQube no evalúa la cohesión de métodos dentro de interfaces abstractas.
**Módulo o Componente**: `src/main/domain/perfil/i_perfil_repository.py`, interfaz `IPerfilRepository` (líneas 7-26)
**Estrategia de Refactoring**: Extract Interface: dividir `IPerfilRepository` en dos interfaces segregadas: `IPracticanteRepository` e `IEmpresaRepository`.

**6. Múltiples motivos de cambio en servicio de perfiles (Change Preventer-Divergent Change)**: `PerfilApplicationService` gestiona conjuntamente los flujos y reglas de negocio de practicantes (gestión de habilidades, cálculo de score, verificación de identidad con DNI/carnet) y de empresas (validación de RUC SUNAT y razón social). Si cambian las políticas de verificación empresarial o las de reputación académica, la misma clase debe ser modificada. SonarQube no identifica clases con responsabilidades divergentes orientadas a distintos actores.
**Módulo o Componente**: `src/main/application/perfil_application_service.py`, clase `PerfilApplicationService`
**Estrategia de Refactoring**: Extract Class: extraer las responsabilidades en dos servicios independientes: `PracticanteApplicationService` y `EmpresaApplicationService`.

**7. Travesía en cadena a través de agregados ajenos (Coupler-Message Chains)**: En `list_for_user`, el servicio navega manualmente a través de convocatorias, luego por cada postulación y finalmente por cada práctica para resolver las prácticas pertenecientes a una empresa mediante tres bucles anidados. Igualmente, `_require_empresa_owner` navega de práctica a postulación y de postulación a convocatoria. El servicio acopla su lógica a la estructura de relaciones interna de otros agregados violando la Ley de Demeter. SonarQube no analiza travesías de relaciones entre modelos de dominio.
**Módulo o Componente**: `src/main/application/practica_application_service.py`, métodos `list_for_user` (líneas 114-121) y `_require_empresa_owner` (líneas 157-166)
**Estrategia de Refactoring**: Hide Delegate: encapsular la relación proveyendo un método de consulta directo en el repositorio (`find_by_empresa_id`) que resuelva las prácticas asociadas a la empresa mediante una única consulta sin travesías manuales.

**8. Descomposición de Value Object en datos primitivos (Bloater-Data Clumps)**: La entidad `Usuario` descompone los tokens de activación y recuperación en pares de campos primitivos individuales (`activation_token`, `activation_token_expires_at`, `password_reset_token`, `password_reset_expires_at`) que siempre aparecen y mutan juntos, en lugar de mantener la referencia al objeto `TokenRecuperacion`. Además, `UsuarioApplicationService` extrae ambos datos y los pasa a `autenticar_dominio_servicio.validar_token(valor, expiracion)`, recreando innecesariamente el objeto para verificar vigencia. SonarQube no detecta grupos de campos primitivos concurrentes.
**Módulo o Componente**: `src/main/domain/auth/usuario.py` (líneas 27-30, 54-62) y `src/main/application/usuario_application_service.py` (líneas 124-128, 143-147)
**Estrategia de Refactoring**: Preserve Whole Object: asociar las instancias de `TokenRecuperacion` (o `TokenSeguridad`) directamente como atributos de `Usuario`, evitando la dispersión de primitivos.

**9. Obsesión primitiva en nombres y Value Object huérfano (Bloater-Primitive Obsession)**: La entidad `Practicante` maneja `nombres` y `apellidos` como cadenas de texto primitivas sin encapsular su validación ni normalización, permitiendo inconsistencias. En contraste, existe el Value Object `NombreCompleto` en `domain.perfil.nombre_completo` que valida no vacuidad y formatea el nombre, pero se encuentra completamente desvinculado del modelo de producción (código muerto). SonarQube no detecta el desaprovechamiento de Value Objects frente a tipos primitivos.
**Módulo o Componente**: `src/main/domain/perfil/practicante.py` (líneas 20-21, 29-39) y `src/main/domain/perfil/nombre_completo.py`
**Estrategia de Refactoring**: Replace Data Value with Object: sustituir los atributos primitivos `nombres` y `apellidos` en `Practicante` por la composición del Value Object `NombreCompleto`.

**10. Intermediario innecesario en verificación de código QR (Coupler-Middle Man)**: El método `verificar_codigo_qr` de `CertificacionDominioServicio` se limita exclusivamente a delegar la llamada a `certificado.codigo_qr.verificar(valor)` sin aportar validaciones adicionales ni coordinación de negocio. Actúa como un intermediario que añade una capa de indirección superflua. SonarQube no distingue entre servicios con lógica genuina y métodos delegadores pasivos.
**Módulo o Componente**: `src/main/domain/certificacion/certificacion_dominio_servicio.py`, método `verificar_codigo_qr` (líneas 20-23)
**Estrategia de Refactoring**: Remove Middle Man: eliminar el método delegador del servicio de dominio e invocar directamente la verificación a través del agregado `Certificado` o su Value Object `CodigoQR`.

**11. Fábrica perezosa sin justificación arquitectónica (Dispensable-Lazy Class)**: La clase `PracticaFabrica` contiene únicamente un método de 3 líneas útiles que valida que los identificadores no sean nulos y llama al constructor de `Practica`. No gestiona jerarquías polimórficas ni lógica compleja de inicialización, exigiendo instanciaciones innecesarias (`PracticaFabrica().iniciar_practica(...)`). SonarQube no mide el valor arquitectónico ni el costo de mantenimiento de clases anémicas.
**Módulo o Componente**: `src/main/domain/practica_evaluacion/practica_fabrica.py`, clase `PracticaFabrica` (líneas 7-16)
**Estrategia de Refactoring**: Inline Class: fusionar la responsabilidad eliminando la fábrica e incorporando un método de fábrica estático dentro de la propia clase `Practica` (*Replace Constructor with Factory Method*).

**12. Controladores de presentación como intermediarios anémicos (Coupler-Middle Man)**: Las clases de la capa `src/main/presentation/` (`PracticaController`, `ConvocatoriaController`, `CertificadoController`, etc.) no procesan peticiones HTTP ni conocen el framework web (Flask maneja los requests en `flask_mvc/routes/`). Cada método de estos controladores se limita a validar la presencia del servicio, delegar la llamada a `ApplicationService` y serializar a diccionario con una tupla de código de estado, constituyendo una capa redundante de intermediarios. SonarQube no evalúa la redundancia entre capas de controladores.
**Módulo o Componente**: `src/main/presentation/*_controller.py` (8 clases de controladores)
**Estrategia de Refactoring**: Remove Middle Man: integrar las responsabilidades de serialización en las rutas HTTP de Flask o en presentadores dedicados, eliminando los controladores intermedios duplicados.

**13. Contenedor de datos anémico y redundante (Dispensable-Data Class)**: La clase `ResultadoMatching` actúa como un simple contenedor de atributos (`score_compatibilidad`, `practicante_id`, `convocatoria_id`, `sugerencia`, `convocatoria`) que duplica los datos ya contenidos en `Sugerencia` y `Convocatoria`, contando con un único método de una línea (`es_compatible`). Carece de comportamiento sustancial. SonarQube no marca clases de datos con atributos y un método básico como código problemático.
**Módulo o Componente**: `src/main/domain/matching/resultado_matching.py`, clase `ResultadoMatching` (líneas 1-11)
**Estrategia de Refactoring**: Move Method: mover el método `es_compatible` a la entidad `Sugerencia` y simplificar la estructura eliminando el contenedor redundante (*Inline Class*).

**14. Bolsas de datos genéricas no tipadas en servicios de aplicación (Bloater-Primitive Obsession)**: Métodos clave de casos de uso como `ConvocatoriaApplicationService.create_convocatoria`, `update` y `PerfilApplicationService.update_practicante` reciben un argumento genérico `data: dict` sin estructura formal. Esto oscurece el contrato de entrada, exige extracciones manuales `.get("...")` dispersas y traslada el riesgo de errores tipográficos o valores faltantes al interior del servicio. SonarQube no detecta el uso de primitivos dinámicos en fronteras de casos de uso.
**Módulo o Componente**: `src/main/application/convocatoria_application_service.py` (líneas 10, 33) y `perfil_application_service.py` (líneas 19, 75)
**Estrategia de Refactoring**: Introduce Parameter Object: sustituir el diccionario sin tipar por objetos de transferencia de datos (DTO / Command Objects) explícitos como `CrearConvocatoriaCommand` o `ActualizarPerfilDTO`.

**15. Duplicación algorítmica en sincronización de modelos ORM (Dispensable-Duplicate Code)**: En `SqlAlchemyPracticaRepository.save`, el algoritmo para sincronizar colecciones hijas con la base de datos (obtener IDs actuales, eliminar huérfanos de la relación y agregar nuevos registros no existentes) está implementado de manera idéntica y consecutiva para `entregables` y para `evaluaciones`. Aunque operan sobre tipos distintos, la lógica y estructura algorítmica son idénticas. SonarQube solo detecta duplicación literal exacta de tokens de código, no duplicación conceptual o algorítmica.
**Módulo o Componente**: `src/main/infrastructure/sqlalchemy_practica_repository.py`, método `save` (líneas 29-46 vs 47-64)
**Estrategia de Refactoring**: Extract Method: parametrizar la lógica de sincronización de colecciones en una función auxiliar genérica `_sync_collection(model_collection, domain_collection, model_class, mapper_func)`.

**16. Acoplamiento de entidades de dominio a rutas HTTP de infraestructura (SOLID-DIP)**: Las entidades `ArchivoPDF` y `CodigoQR` generan dentro de su propia lógica de dominio cadenas de texto que corresponden a rutas de endpoints web de presentación (`url = f"/certificados/practica/{practica_id}/pdf"` y `url_verificacion = f"/certificados/verificar/{valor}"`). Esto invierte el flujo de dependencias de Clean Architecture, acoplando el núcleo del dominio a convenciones de ruteo HTTP. SonarQube no detecta semántica de URLs dentro de atributos de dominio.
**Módulo o Componente**: `src/main/domain/certificacion/archivo_pdf.py` (línea 16) y `codigo_qr.py` (línea 14)
**Estrategia de Refactoring**: Move Method: extraer la construcción de URLs hacia la capa de presentación o servicios de infraestructura dedicados a generar enlaces web.

**17. Violación de encapsulamiento y Feature Envy en cálculo de score (Coupler-Feature Envy)**: En `PerfilApplicationService`, cada método que modifica el perfil de un practicante (`update_practicante`, `add_habilidad`, `add_formacion`, `register_identity`) se ve obligado a invocar manualmente `practicante.calcular_score()`. El servicio tiene que controlar el estado interno y las invariantes del objeto; si se omite dicha llamada en un nuevo método, el estado queda inconsistente. SonarQube no analiza la cohesión de invariantes de negocio dentro de agregados.
**Módulo o Componente**: `src/main/application/perfil_application_service.py`, métodos modificadores (líneas 50, 57, 64, 72)
**Estrategia de Refactoring**: Move Method: encapsular el recálculo automático del score internamente dentro de los métodos de mutación de `Practicante` (`agregar_habilidad`, `agregar_formacion`, etc.), protegiendo la invariante.

**18. Algoritmo de matching rígido sin extensibilidad (SOLID-OCP)**: El cálculo de compatibilidad en `Sugerencia.calcular_compatibilidad` está codificado de forma estricta mediante intersección simple de conjuntos de cadenas normalizadas dividida por el total de requerimientos. No existe abstracción para incorporar ponderaciones por nivel de experiencia, sinónimos de tecnologías o filtros de exclusión sin modificar directamente el código del método. SonarQube no identifica rigidez arquitectónica frente a futuros requerimientos de extensión.
**Módulo o Componente**: `src/main/domain/matching/sugerencia.py`, método `calcular_compatibilidad` (líneas 10-33)
**Estrategia de Refactoring**: Replace Type Code with State/Strategy: extraer el cálculo de compatibilidad a una interfaz de estrategia `MatchingStrategy` permitiendo inyectar algoritmos alternativos sin alterar `Sugerencia`.

**19. Ruptura de invariantes de dominio mediante mutación directa de estado (SOLID-LSP)**: En `PostulacionApplicationService.select_candidate`, la asignación `otra.estado = Postulacion.ESTADO_RECHAZADA` muta directamente el campo de la entidad omitiendo el método `otra.rechazar()`, que implementa la regla de transición de estados ("Solo una postulación pendiente puede rechazarse"). Esto viola el encapsulamiento del agregado y evade las precondiciones del dominio. SonarQube no detecta evasión de reglas de métodos mediante asignaciones de atributos.
**Módulo o Componente**: `src/main/application/postulacion_application_service.py`, método `select_candidate` (línea 112)
**Estrategia de Refactoring**: Encapsulate Field: restringir la mutación directa de atributos de estado y forzar todas las transiciones a través de métodos de negocio explícitos en `Postulacion`.

**20. Validación de atributos duplicada entre fábrica y entidad (Dispensable-Duplicate Code)**: La fábrica `ConvocatoriaFabrica.crear_convocatoria` y el método `Convocatoria.actualizar` replican las mismas validaciones sobre el título obligatorio, la obligatoriedad de que las habilidades requeridas sean una lista y que los beneficios sean una lista. Esta duplicación conceptual de reglas causa divergencia si las restricciones de validación se modifican en un punto y no en el otro. SonarQube no detecta duplicación semántica distribuida entre clases distintas.
**Módulo o Componente**: `src/main/domain/convocatorias/convocatoria_fabrica.py` (líneas 8-18) y `convocatoria.py` (líneas 72-90)
**Estrategia de Refactoring**: Move Method: centralizar las reglas de validación en la entidad `Convocatoria` o en Value Objects asociados, y delegar la validación desde la fábrica hacia la entidad.

**21. Capa de dominio acoplada a biblioteca externa del framework web (SOLID-DIP)**: La clase de servicio de dominio `AutenticacionDominioServicio` importa y utiliza directamente funciones criptográficas de `werkzeug.security` (`generate_password_hash`, `check_password_hash`). El núcleo de dominio queda acoplado a una biblioteca de infraestructura/web en lugar de depender de una abstracción de hashing inyectada. SonarQube no evalúa la pureza del dominio frente a dependencias de terceros.
**Módulo o Componente**: `src/main/domain/auth/autenticacion_dominio_servicio.py` (líneas 8-9, 27, 34)
**Estrategia de Refactoring**: Extract Interface: definir una interfaz en el dominio (ej. `IPasswordHasher`) e inyectar su implementación concreta desde la capa de infraestructura.

**22. Retorno de tuplas posicionales anónimas en casos de uso (Bloater-Primitive Obsession)**: Los métodos `PostulacionApplicationService.list_for_practicante` y `list_for_convocatoria` devuelven colecciones de tuplas anónimas `(postulacion, convocatoria)` y `(postulacion, practicante, practica)`. Los consumidores dependen del orden posicional de los elementos (`t[0]`, `t[1]`, `t[2]`) en lugar de atributos con nombres explícitos, volviendo frágil el código ante cualquier cambio de firma. SonarQube no detecta estructuras de datos anónimas no tipadas.
**Módulo o Componente**: `src/main/application/postulacion_application_service.py`, métodos `list_for_practicante` (líneas 53-61) y `list_for_convocatoria` (líneas 66-77)
**Estrategia de Refactoring**: Replace Array with Object: introducir objetos de resultado explícitos (ej. `PostulacionDetalleDTO` y `CandidatoConvocatoriaDTO`) que empaqueten los datos con atributos nombrados.

**23. Operaciones de múltiples pasos sin abstracción transaccional (SOLID-SRP)**: En `PostulacionApplicationService.select_candidate`, se modifica y persiste el candidato seleccionado y luego se iteran y persisten las demás postulaciones una por una mediante `self.postulacion_repository.save()`, ejecutando un commit en cada iteración. La orquestación del caso de uso queda acoplada a persistencias parciales sin una abstracción de Unidad de Trabajo que garantice atomicidad. SonarQube no detecta ausencia de límites transaccionales ni fallas en la atomicidad de múltiples llamadas a repositorio.
**Módulo o Componente**: `src/main/application/postulacion_application_service.py`, método `select_candidate` (líneas 103-114)
**Estrategia de Refactoring**: Extract Class: introducir el patrón Unit of Work o aislar la operación multi-entidad en un método transaccional de repositorio que asegure un único commit atómico.

**24. Estado temporal dependiente del ciclo de vida en entidad (Object-Orientation Abuser-Temporary Field)**: En la entidad `Convocatoria`, el campo `fecha_cierre` solo tiene sentido y contiene datos válidos cuando `estado == ESTADO_CERRADA`. Durante los estados de borrador y publicada, el campo permanece en `None`, y al reabrir una convocatoria se fuerza artificialmente a `None`. En lugar de modelar los estados y sus datos asociados con clases de estado, se usan campos temporales en una clase monolítica. SonarQube no analiza el ciclo de vida de los atributos en relación con los estados del objeto.
**Módulo o Componente**: `src/main/domain/convocatorias/convocatoria.py`, campo `fecha_cierre` (líneas 32, 47, 55)
**Estrategia de Refactoring**: Replace Type Code with State/Strategy: modelar los estados de `Convocatoria` (`BorradorState`, `PublicadaState`, `CerradaState`) mediante el patrón State, donde la fecha de cierre pertenezca exclusivamente al estado cerrado.

Resumen: 24 hallazgos (Bloater: 4, Object-Orientation Abuser: 1, Change Preventer: 1, Dispensable: 4, Coupler: 6, SOLID: 8). Smells del catálogo no detectados: Alternative Classes with Different Interfaces, Refused Bequest, Switch Statements, Parallel Inheritance Hierarchies, Incomplete Library Class, Long Parameter List.



## Catálogo de las 12 Incidencias más Críticas de SonarQube (sonar-reporte.md)

Esta sección consolida y prioriza las 12 incidencias automáticas más relevantes detectadas por SonarQube en el análisis estático, organizadas por impacto en seguridad, mantenibilidad y accesibilidad, con su respectiva estrategia de refactorización o mitigación.

### Tabla Comparativa de las 12 Incidencias de SonarQube

| N° | Incidencia / Regla | Clasificación (Dimensión - Regla) | Dónde | Gravedad | Dimensión | Verificado |
|---|---|---|---|---|---|---|
| 1 | Literal duplicado "Perfil de practicante no encontrado" | Mantenibilidad - python:S1192 | `application/postulacion_application_service.py:22` | Alta | Maintainability | Sí |
| 2 | Validación de certificado SSL/TLS en conexión SMTP | Seguridad - python:S4830 | `infrastructure/smtp_auth_email_sender.py:176` | Alta | Security | Sí |
| 3 | Complejidad cognitiva alta en autenticación frontend | Mantenibilidad - javascript:S3776 | `frameworks/flask_mvc/static/js/auth.js:87` | Alta | Maintainability | Sí |
| 4 | Complejidad cognitiva alta en renderizado de vistas | Mantenibilidad - javascript:S3776 | `frameworks/flask_mvc/static/js/app.js:299` | Alta | Maintainability | Sí |
| 5 | Operaciones ternarias anidadas en JavaScript | Mantenibilidad - javascript:S3358 | `frameworks/flask_mvc/static/js/app.js:357-374` | Media | Maintainability | Sí |
| 6 | Ausencia de encabezados th en tabla HTML | Accesibilidad - Web:S5256 | `frameworks/flask_mvc/templates/app.html:124` | Media | Accessibility | Sí |
| 7 | Etiqueta label sin control de formulario asociado | Accesibilidad - Web:S6853 | `frameworks/flask_mvc/templates/app.html:185` | Media | Accessibility | Sí |
| 8 | Falta de atributos aria-label en controles y diálogos | Accesibilidad - Web:S5255 | `frameworks/flask_mvc/templates/app.html:13, 115, 138, 189` | Media | Accessibility | Sí |
| 9 | Literal duplicado "No autenticado" en capa de rutas | Mantenibilidad - python:S1192 | `frameworks/flask_mvc/routes/convocatoria_routes.py:36` | Alta | Maintainability | Sí |
| 10 | Literal duplicado "Empresa no encontrada..." en rutas | Mantenibilidad - python:S1192 | `frameworks/flask_mvc/routes/convocatoria_routes.py:39` | Alta | Maintainability | Sí |
| 11 | Literal duplicado "Convocatoria no encontrada" en aplicación | Mantenibilidad - python:S1192 | `application/convocatoria_application_service.py:26` | Alta | Maintainability | Sí |
| 12 | Literal duplicado "Postulación no encontrada" en aplicación | Mantenibilidad - python:S1192 | `application/postulacion_application_service.py:83` | Alta | Maintainability | Sí |

### Detalle de las 12 Incidencias

**1. Literal duplicado "Perfil de practicante no encontrado" en aplicación (Mantenibilidad-python:S1192)**: El mensaje de error literal `"Perfil de practicante no encontrado"` se encuentra duplicado 3 veces en `postulacion_application_service.py` (líneas 22, 52 y 129) dentro de las validaciones de postulación, listado y cancelación, aumentando el riesgo de inconsistencias tipográficas en validaciones y mensajes propagados hacia la capa de presentación.
**Módulo o Componente**: `src/main/application/postulacion_application_service.py`, métodos `apply`, `list_for_practicante` y `cancel` (líneas 22, 52, 129)
**Estrategia de Refactoring**: Replace Magic Number with Symbolic Constant / Replace Error Code with Exception: definir una constante a nivel de módulo `NOT_FOUND_PRACTICANTE = "Perfil de practicante no encontrado"` o implementar una excepción especializada de dominio (`PerfilPracticanteNoEncontradoError`).

**2. Validación de certificado SSL/TLS en conexión SMTP (Seguridad-python:S4830)**: Al inicializar el transporte seguro SMTP mediante `smtp.starttls(context=ssl.create_default_context())`, SonarQube alerta sobre la configuración de contexto para garantizar que la verificación de nombres de host y la cadena de confianza de certificados del servidor no sean omitidas. Si bien `create_default_context()` aplica validación por defecto, la falta de parámetros explícitos de validación en configuraciones personalizadas puede provocar conexiones vulnerables a ataques Man-in-the-Middle (MitM).
**Módulo o Componente**: `src/main/infrastructure/smtp_auth_email_sender.py`, método `_send` (líneas 175-177)
**Estrategia de Refactoring**: Parameterize Method: configurar explícitamente el contexto SSL asegurando `context.check_hostname = True` y `context.verify_mode = ssl.CERT_REQUIRED`, manejando excepciones específicas de verificación de certificados.

**3. Complejidad cognitiva alta en autenticación frontend (Mantenibilidad-javascript:S3776)**: La función de manejo de autenticación en `auth.js` acumula una complejidad cognitiva de 23 puntos (superando el límite de 15 fijado por SonarQube). Concentra en un solo bloque el procesamiento del submit, la validación de campos, la gestión de estados de interfaz, el consumo de la API REST mediante fetch y el enrutamiento posterior.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/static/js/auth.js`, función de gestión de formulario de autenticación (línea 87)
**Estrategia de Refactoring**: Extract Method: descomponer la función en subfunciones especializadas (`validateAuthForm`, `submitAuthRequest`, `handleAuthResponse`, `displayAuthErrors`) reduciendo las estructuras de control anidadas.

**4. Complejidad cognitiva alta en renderizado de vistas (Mantenibilidad-javascript:S3776)**: La función encargada de actualizar y conmutar vistas dinámicas en `app.js` alcanza una complejidad cognitiva de 20 puntos. Contiene múltiples bifurcaciones condicionales anidadas (`if/else`, `switch`) para evaluar roles de usuario, permisos y secciones activas, dificultando el mantenimiento y las pruebas.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/static/js/app.js`, función de renderizado de vistas principales (línea 299)
**Estrategia de Refactoring**: Replace Nested Conditional with Guard Clauses / Replace Conditional with Polymorphism (Strategy de vistas en JS): emplear un mapa de controladores de vista por sección o cláusulas de guarda tempranas que eliminen el anidamiento.

**5. Operaciones ternarias anidadas en JavaScript (Mantenibilidad-javascript:S3358)**: Se identifican 9 instancias de expresiones ternarias anidadas (ej. `a ? b : (c ? d : e)`) para calcular badges de estado, clases CSS condicionales y textos de estado en `app.js` (líneas 357, 358, 361, 374, 473, 830, 831, 834, 975). Esta práctica degrada severamente la legibilidad del código.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/static/js/app.js`, funciones de renderizado de listas de convocatorias y postulaciones (líneas 357-374, 830-834)
**Estrategia de Refactoring**: Decompose Conditional: extraer las ternarias anidadas en sentencias `if/else` convencionales o crear funciones de consulta puras (`getStatusBadge(estado)`) con retornos tempranos.

**6. Ausencia de encabezados th en tabla HTML (Accesibilidad-Web:S5256)**: La tabla de datos de postulaciones y entregables en la plantilla principal carece de celdas de encabezado `<th>` en su cabecera `<thead>`, empleando únicamente celdas genéricas `<td>` o filas desestructuradas. Esto impide que los lectores de pantalla asociados a tecnologías asistivas puedan asociar los datos de las filas con sus títulos de columna.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/templates/app.html`, estructura `<table>` (línea 124)
**Estrategia de Refactoring**: Reemplazar las etiquetas `<td>` de la cabecera por elementos semánticos `<th>` incluyendo el atributo de alcance `scope="col"`.

**7. Etiqueta label sin control de formulario asociado (Accesibilidad-Web:S6853)**: En el formulario modal de subida o edición, existe un elemento `<label>` que no cuenta con el atributo `for` vinculado a un identificador `id` de control, ni contiene el `<input>` anidado en su interior. Esto imposibilita enfocar el campo al pulsar sobre la etiqueta.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/templates/app.html`, formulario modal (línea 185)
**Estrategia de Refactoring**: Añadir el atributo `for="<input-id>"` a la etiqueta `<label>` haciendo coincidir el identificador único del elemento de entrada correspondiente.

**8. Falta de atributos aria-label en controles y diálogos (Accesibilidad-Web:S5255)**: Múltiples botones de acción basados exclusivamente en íconos, botones de cierre de diálogos modales y contenedores interactivos carecen de texto visible o de atributos de accesibilidad `aria-label` o `aria-labelledby`, resultando invisibles para usuarios de lectores de pantalla.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/templates/app.html`, elementos interactivos y modales (líneas 13, 115, 138, 189)
**Estrategia de Refactoring**: Incorporar atributos `aria-label="..."` descriptivos en cada botón de icono y vincular los diálogos modales con su título mediante `aria-labelledby="modal-title-id"`.

**9. Literal duplicado "No autenticado" en capa de rutas (Mantenibilidad-python:S1192)**: La cadena literal de respuesta de error de sesión `"No autenticado"` se repite literalmente 8 veces en `convocatoria_routes.py`, y múltiples veces adicionales en `notificacion_routes.py`, `perfil_routes.py` y `postulacion_routes.py`, incrementando el riesgo de inconsistencias tipográficas en la API.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/routes/convocatoria_routes.py` (línea 36) y módulos hermanos de rutas
**Estrategia de Refactoring**: Replace Magic Number with Symbolic Constant: centralizar el mensaje en una constante compartida `NO_AUTENTICADO_ERROR = "No autenticado"` en `routes/__init__.py` o encapsular la comprobación en un decorador `@login_required`.

**10. Literal duplicado "Empresa no encontrada..." en rutas (Mantenibilidad-python:S1192)**: El literal `"Empresa no encontrada para este usuario"` se encuentra duplicado 8 veces en `convocatoria_routes.py:39`, 4 veces en `postulacion_routes.py:72` y 4 veces en `practica_routes.py:57`.
**Módulo o Componente**: `src/main/frameworks/flask_mvc/routes/convocatoria_routes.py` (línea 39), `postulacion_routes.py:72`, `practica_routes.py:57`
**Estrategia de Refactoring**: Replace Magic Number with Symbolic Constant / Extract Method: definir una constante simbólica compartida y abstraer la validación de pertenencia de empresa en un helper o decorador `@empresa_required`.

**11. Literal duplicado "Convocatoria no encontrada" en aplicación (Mantenibilidad-python:S1192)**: El mensaje de excepción `"Convocatoria no encontrada"` se repite 4 veces en `convocatoria_application_service.py`, 3 veces en `postulacion_application_service.py` y 3 veces en `practica_application_service.py`.
**Módulo o Componente**: `src/main/application/convocatoria_application_service.py` (línea 26) y servicios de aplicación dependientes
**Estrategia de Refactoring**: Replace Magic Number with Symbolic Constant / Replace Error Code with Exception: definir excepciones de dominio específicas (ej. `ConvocatoriaNoEncontradaError`) con mensaje predeterminado.

**12. Literal duplicado "Postulación no encontrada" en aplicación (Mantenibilidad-python:S1192)**: El mensaje literal `"Postulación no encontrada"` se duplica 4 veces en `postulacion_application_service.py:83` y 3 veces en `practica_application_service.py:23`.
**Módulo o Componente**: `src/main/application/postulacion_application_service.py` (línea 83) y `practica_application_service.py` (línea 23)
**Estrategia de Refactoring**: Replace Magic Number with Symbolic Constant / Replace Error Code with Exception: unificar el mensaje en una constante o crear la excepción especializada `PostulacionNoEncontradaError`.

Resumen: 12 incidencias (Seguridad: 1, Mantenibilidad: 8, Accesibilidad: 3). Cobertura de las reglas más frecuentes de SonarQube en el proyecto: S4830, S3776, S3358, S5256, S6853, S5255 y S1192.
