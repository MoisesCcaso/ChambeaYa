# Casos de prueba – Oportunidades, postulaciones y certificado público (I6)

Técnica de caja negra: **casos de uso y estados**. Automatizados en
[`test_postulaciones.py`](../test_postulaciones.py) (1 método por caso).

| ID | Objeto de prueba | Escenario / Acciones | Valores de prueba | Resultado esperado | Resultado obtenido |
|----|------------------|----------------------|-------------------|--------------------|--------------------|
| POS-01 | Oportunidades | Iniciar sesión como practicante y abrir Oportunidades | Una convocatoria publicada y otra en borrador (creadas por API) | La lista muestra la publicada y no muestra el borrador | Aprobado |
| POS-02 | Postulación | Practicante con perfil completo abre una convocatoria publicada y pulsa "Postular ahora" | Convocatoria publicada; practicante nuevo con nombres y apellidos | Aviso "Postulación registrada correctamente" y la postulación aparece como Pendiente en Mis postulaciones | Aprobado |
| POS-03 | Postulación | Postular y revisar de nuevo la misma convocatoria; reintentar por API | Misma convocatoria, mismo practicante | El botón de postular desaparece y se muestra la etiqueta Pendiente; solo hay una fila en Mis postulaciones; el servidor responde 400 "Ya existe una postulación para esta convocatoria" | Aprobado |
| POS-04 | Postulación | Abrir Oportunidades con una convocatoria cerrada; intentar postular por API | Convocatoria publicada y luego cerrada | La convocatoria no aparece en la lista; el servidor responde 400 "Solo se puede postular a convocatorias publicadas" | Aprobado |
| POS-05 | Certificado | Abrir `/verificar-certificado` (sin sesión), escribir el código y verificar | Código real de un certificado emitido por API (`CERT-<práctica>-<8 hex>`) | Resultado con estilo válido y título "Certificado válido" | Aprobado |
| POS-06 | Certificado | Abrir `/verificar-certificado` y verificar un código inexistente | `XXXX-0000` | Resultado con estilo inválido y título "Certificado no encontrado" | Aprobado |

Notas:

- Cada caso crea sus propios datos por API (`postulacion_data.py`), así que no
  depende de otros casos ni modifica a `practicante@demo.local`; POS-01 usa esa
  cuenta solo para leer.
- POS-05 recorre el flujo completo por API: convocatoria publicada,
  postulación, selección, práctica, entregable, evaluación aprobada,
  finalización y emisión del certificado.
- La columna "Resultado obtenido" se completa tras ejecutar la suite en el
  equipo del integrante.

## Datos de prueba y ejecución

```bash
.\demo.ps1 -Reset                      # Windows: reinicia la BD demo y deja la app en :5000
poetry run pytest src/test/functional/test_postulaciones.py
```

`FLASK_ENV=demo` activa `EXPOSE_AUTH_TOKENS`, necesario para activar las
cuentas nuevas por API.
