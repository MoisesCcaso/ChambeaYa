# Casos de prueba – Activación y recuperación de contraseña (I3)

Técnica de caja negra: **casos de uso**. Automatizados en
[`test_recuperacion.py`](../test_recuperacion.py) (1 método por caso).

| ID | Objeto de prueba | Escenario / Acciones | Valores de prueba | Resultado esperado | Resultado obtenido |
|----|------------------|----------------------|-------------------|--------------------|--------------------|
| REC-01 | Activación | Abrir enlace `/activar?token=...` y confirmar | Token válido (obtenido por API con `EXPOSE_AUTH_TOKENS=true`) | Mensaje "Tu cuenta está activa", redirige a `/ingresar` y el login lleva a `/app` | Aprobado |
| REC-02 | Activación | Abrir enlace con token inválido y confirmar | `token=invalido` | Mensaje "Token de activación inválido"; permanece en `/activar` | Aprobado |
| REC-03 | Login | Iniciar sesión con cuenta sin activar | Usuario recién registrado, `Abcd1234` | Mensaje "La cuenta no está activa"; permanece en `/ingresar` | Aprobado |
| REC-04 | Recuperar | Solicitar recuperación en `/recuperar` | `practicante@demo.local` | "Solicitud procesada…" y redirección a `/restablecer?token=...` | Aprobado |
| REC-05 | Restablecer | Cambiar contraseña con valor válido | `Nueva1234` | "Contraseña actualizada", redirige a `/ingresar`; el login con la nueva contraseña entra a `/app` | Aprobado |
| REC-06 | Restablecer | Cambiar contraseña con valor inválido (límite: < 8 caracteres) | `corta` | `minlength` del navegador la marca inválida; el servidor responde "La contraseña debe tener al menos 8 caracteres" y la contraseña anterior sigue vigente | Aprobado |

Notas:

- REC-05 y REC-06 usan cuentas creadas por API en cada ejecución, para no
  alterar `practicante@demo.local` ni depender de otros casos.
- REC-06 desactiva `noValidate` solo para ejercitar la validación del servidor;
  la validación del navegador se comprueba con `validity.tooShort`.

## Datos de prueba y ejecución

```bash
scripts/demo_reset.sh            # reinicia la BD demo y deja la app en :5000
poetry run pytest src/test/functional/test_recuperacion.py
```

`FLASK_ENV=demo` activa `EXPOSE_AUTH_TOKENS`, necesario para obtener los
tokens de activación y recuperación sin correo.
