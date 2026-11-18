# Auditoría manual de código - ChambeaYa

Generado el 2026-11-18 11:09. Hallazgos que **no** aparecen en el reporte de SonarQube (34 incidencias, ver `sonar-reporte.md`).

## Resumen

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
