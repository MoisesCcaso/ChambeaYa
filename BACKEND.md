# Backend de ChambeaYa

El backend usa Flask, SQLAlchemy, migraciones Alembic y sesiones HTTP. La API
integra autenticación, perfiles, convocatorias, postulaciones, matching,
prácticas, entregables, evaluaciones, notificaciones y certificados.

## Preparación en Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m flask --app frameworks.flask_mvc.app:create_app db upgrade
```

Para ejecutar:

```powershell
.\.venv\Scripts\python.exe -m flask --app frameworks.flask_mvc.app:create_app run --debug
```

Para ejecutar las pruebas integrales:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Autenticación

La autenticación usa la cookie de sesión de Flask. Las rutas protegidas
requieren haber iniciado sesión con `POST /auth/login`.

| Método | Ruta | Uso |
|---|---|---|
| POST | `/auth/register` | Registrar empresa o practicante |
| POST | `/auth/activate` | Activar la cuenta |
| POST | `/auth/login` | Iniciar sesión |
| GET | `/auth/me` | Consultar usuario autenticado |
| POST | `/auth/logout` | Cerrar sesión |
| POST | `/auth/recover-password` | Solicitar recuperación |
| POST | `/auth/reset-password` | Cambiar contraseña con token |

Los tokens se incluyen en la respuesta solo en desarrollo y pruebas. En
producción deben enviarse mediante un proveedor de correo.

## Perfiles

| Método | Ruta | Uso |
|---|---|---|
| GET | `/perfil/me` | Obtener el perfil según el tipo de usuario |
| PUT | `/perfil/me` | Crear o actualizar perfil de practicante |
| PUT | `/perfil/me/empresa` | Crear o actualizar empresa y validar RUC |
| POST | `/perfil/me/habilidades` | Añadir habilidad |
| POST | `/perfil/me/formacion` | Añadir formación |
| POST | `/perfil/me/identidad` | Verificar DNI o carnet |
| GET | `/perfil/me/reputacion` | Consultar reputación |

## Convocatorias y matching

| Método | Ruta | Uso |
|---|---|---|
| GET | `/convocatorias?q=python` | Buscar convocatorias publicadas |
| GET | `/convocatorias/<id>` | Ver convocatoria publicada |
| GET | `/convocatorias/mis` | Listar convocatorias de la empresa |
| POST | `/convocatorias` | Crear borrador |
| PUT | `/convocatorias/<id>` | Editar borrador propio |
| POST | `/convocatorias/<id>/publicar` | Publicar borrador |
| POST | `/convocatorias/<id>/cerrar` | Cerrar convocatoria |
| GET | `/matching/sugerencias` | Calcular sugerencias sin persistir |
| POST | `/matching/calcular` | Calcular y guardar sugerencias |

El matching compara habilidades sin distinguir mayúsculas y solo considera
convocatorias publicadas.

## Postulaciones

| Método | Ruta | Uso |
|---|---|---|
| POST | `/postulaciones/convocatorias/<id>` | Postular a una convocatoria |
| GET | `/postulaciones/me` | Listar postulaciones del practicante |
| GET | `/postulaciones/convocatorias/<id>` | Listar candidatos de la empresa |
| POST | `/postulaciones/<id>/seleccionar` | Seleccionar candidato |
| POST | `/postulaciones/<id>/rechazar` | Rechazar candidato |

No se permiten postulaciones duplicadas. Al seleccionar a un candidato, las
otras postulaciones pendientes de la convocatoria se rechazan.

## Prácticas, entregables y evaluaciones

| Método | Ruta | Uso |
|---|---|---|
| POST | `/practicas` | Iniciar práctica desde una postulación seleccionada |
| GET | `/practicas` | Listar prácticas visibles para el usuario |
| GET | `/practicas/<id>` | Consultar práctica autorizada |
| POST | `/practicas/<id>/entregables` | Subir PDF, DOC, DOCX o ZIP (máx. 10 MB) |
| GET | `/practicas/<id>/entregables` | Historial de entregables |
| GET | `/practicas/<id>/entregables/<id>/archivo` | Descargar entregable |
| POST | `/practicas/<id>/evaluar` | Registrar evaluación de 0 a 100 |
| GET | `/practicas/<id>/evaluaciones` | Historial de evaluaciones |
| POST | `/practicas/<id>/finalizar` | Finalizar práctica |

Para finalizar se exige al menos un entregable y una evaluación aprobada
(puntaje mínimo: 60).

Ejemplo de subida:

```powershell
curl.exe -X POST http://127.0.0.1:5000/practicas/1/entregables `
  -b cookies.txt `
  -F "archivo=@informe.pdf"
```

## Notificaciones y certificados

| Método | Ruta | Uso |
|---|---|---|
| GET | `/notificaciones` | Listar notificaciones propias |
| GET | `/notificaciones/no-leidas` | Contar no leídas |
| PUT | `/notificaciones/<id>/leer` | Marcar una notificación propia |
| PUT | `/notificaciones/leer-todas` | Marcar todas como leídas |
| POST | `/certificados/<practica_id>/emitir` | Emitir certificado |
| GET | `/certificados/practica/<practica_id>` | Consultar certificado autorizado |
| GET | `/certificados/verificar/<codigo>` | Verificación pública |
| GET | `/certificados/practica/<practica_id>/pdf` | Descargar PDF |
| GET | `/certificados/<codigo>/qr` | Descargar QR |

La emisión es idempotente: una práctica tiene como máximo un certificado. La
verificación comprueba tanto el QR como la integridad del contenido persistido.

## Persistencia y archivos

- La base SQLite predeterminada vive en `instance/chambeaya.db`.
- Los entregables viven en `instance/uploads/entregables`.
- Las claves foráneas de SQLite se habilitan en cada conexión.
- La revisión `9f12c0a8d4e1` completa el esquema de todas las funcionalidades.
- `instance/` está ignorado por Git y no debe versionarse.

