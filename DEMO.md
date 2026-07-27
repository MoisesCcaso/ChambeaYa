# Guía de presentación local

La demostración utiliza una base SQLite independiente. No modifica
`chambeaya.db` ni requiere servicios externos.

## Iniciar

Desde PowerShell, en la raíz del proyecto:

```powershell
.\demo.ps1
```

La aplicación quedará disponible en `http://127.0.0.1:5000`.

En el login aparecerán accesos rápidos para completar automáticamente las
credenciales:

| Rol | Correo | Contraseña |
| --- | --- | --- |
| Practicante | `practicante@demo.local` | `Demo1234` |
| Empresa | `empresa@demo.local` | `Demo1234` |

## Reiniciar antes de presentar

Si se finalizaron prácticas, se emitieron certificados o se modificaron los
datos durante un ensayo:

```powershell
.\demo.ps1 -Reset
```

La opción `-Reset` elimina únicamente `instance/chambeaya-demo.db`, vuelve a
aplicar las migraciones y restaura el escenario inicial.

## Recorrido recomendado

### 1. Vista pública

1. Mostrar la landing.
2. Abrir la validación pública de certificados.
3. Explicar el registro separado para practicantes y empresas.

### 2. Practicante

1. En el login, pulsar **Practicante** e ingresar.
2. Mostrar el resumen y el perfil verificado de Andrea Quispe.
3. Explorar las convocatorias publicadas.
4. Abrir **Para ti** para mostrar el matching por habilidades.
5. Mostrar las postulaciones seleccionada y pendiente.
6. Abrir la práctica para enseñar el entregable y la evaluación de 85 puntos.
7. Revisar las notificaciones.
8. Cerrar sesión.

### 3. Empresa

1. En el login, pulsar **Empresa** e ingresar.
2. Mostrar las convocatorias publicadas y el borrador editable.
3. Abrir los candidatos de la convocatoria de calidad.
4. Seleccionar al candidato e iniciar una nueva práctica si se desea.
5. Abrir la práctica backend existente.
6. Finalizarla: ya cuenta con entregable y evaluación aprobada.
7. Emitir el certificado y abrir el PDF y el QR.
8. Cerrar sesión.

### 4. Certificado público

1. Copiar el código emitido.
2. Cerrar sesión.
3. Abrir `/verificar-certificado`.
4. Validar el código para demostrar la consulta pública de integridad.

## Recuperación rápida

- Si el puerto 5000 está ocupado, detener la otra aplicación con `Ctrl+C`.
- Si cambió el esquema, ejecutar nuevamente `.\demo.ps1 -Reset`.
- Los tokens de activación y recuperación se muestran únicamente en el modo
  local de demostración, por lo que no se necesita configurar correo.
