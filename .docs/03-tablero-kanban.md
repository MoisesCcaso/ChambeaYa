# Tablero Kanban e issues

Relacionado: [reparto/horas](04-reparto-equipo.md), [convenciones](02-convenciones.md), [entrega](11-reportes-y-entrega.md).

## Creación

Responsable: el coordinador, que confirmó tener permiso de administrar Projects en la cuenta propietaria **MoisesCcaso**. Crea un GitHub Project, elige plantilla **KANBAN**, lo vincula al repo y deja estas columnas exactas y en orden: `TO-DO`, `CURRENT ITERATION`, `IN PROGRESS`, `FIX VALIDATION`, `DONE`. Antes de crear issues, confirma que los seis integrantes pueden ver el Project y colaborar en él.

Etiquetas que se crearán: `unit test` para los issues I-01–I-22 de pruebas R7–R9 y `enhancement` para I-23 de reportes R10–R11. Si una prueba revela un defecto que requiere cambiar código, crear un issue de corrección aparte con `enhancement` y dependencia al test que lo detectó.

## Plantilla de issue

**Título:** `[R#] verbo + módulo`. Campos: descripción y alcance; responsable (Integrante N); etiqueta; estimación en horas; criterios verificables; dependencia (ID o ninguna); ruta de prueba asignada; definición de terminado: pruebas pasan, cobertura anotada, PR a development enlazado.

## Issues propuestos

Los IDs son provisionales; anota el número real de cada issue en la guía del integrante para usarlo en los footers `fix #n`. La separación de carpetas y la fixture compartida de R3 se completaron en Fase 0, por eso no aparecen como issues pendientes. Los issues I-01–I-22 cubren las pruebas R7–R9. I-23 integra y versiona los reportes R10–R11 después de que se integren las pruebas. Inicio: `TO-DO`.

| ID prov. | Título / descripción | Responsable | Etiqueta | h | Dependencia | Inicial |
|---|---|---:|---|---:|---|---|
| I-01 | [R7] Probar dominio auth | Integrante 1 | unit test | 0.5 | Ninguna | TO-DO |
| I-02 | [R8] Probar repositorio de usuario | Integrante 1 | unit test | 0.5 | Ninguna | TO-DO |
| I-03 | [R9] Probar servicio de usuario con dobles | Integrante 1 | unit test | 0.5 | Ninguna | TO-DO |
| I-04 | [R7] Probar dominio perfil | Integrante 2 | unit test | 0.5 | Ninguna | TO-DO |
| I-05 | [R8] Probar repositorio perfil | Integrante 2 | unit test | 0.5 | Ninguna | TO-DO |
| I-06 | [R9] Probar servicio perfil con doble | Integrante 2 | unit test | 0.5 | Ninguna | TO-DO |
| I-07 | [R7] Probar dominio convocatorias | Integrante 3 | unit test | 0.5 | Ninguna | TO-DO |
| I-08 | [R8] Probar repositorio convocatoria | Integrante 3 | unit test | 0.5 | Ninguna | TO-DO |
| I-09 | [R8] Probar repositorio postulación | Integrante 3 | unit test | 0.5 | Ninguna | TO-DO |
| I-10 | [R9] Probar servicio convocatoria con dobles | Integrante 3 | unit test | 0.5 | Ninguna | TO-DO |
| I-11 | [R7] Probar dominio matching | Integrante 4 | unit test | 0.5 | Ninguna | TO-DO |
| I-12 | [R8] Probar repositorio matching | Integrante 4 | unit test | 0.5 | Ninguna | TO-DO |
| I-13 | [R9] Probar servicio matching con dobles | Integrante 4 | unit test | 0.5 | Ninguna | TO-DO |
| I-14 | [R7] Probar dominio práctica/evaluación | Integrante 5 | unit test | 0.5 | Ninguna | TO-DO |
| I-15 | [R8] Probar repositorio práctica | Integrante 5 | unit test | 0.5 | Ninguna | TO-DO |
| I-16 | [R8] Probar repositorio certificado | Integrante 5 | unit test | 0.5 | Ninguna | TO-DO |
| I-17 | [R9] Probar servicio práctica con dobles | Integrante 5 | unit test | 0.5 | Ninguna | TO-DO |
| I-18 | [R7] Probar dominio certificación | Integrante 6 | unit test | 0.5 | Ninguna | TO-DO |
| I-19 | [R8] Probar repositorio notificación | Integrante 6 | unit test | 0.5 | Ninguna | TO-DO |
| I-20 | [R9] Probar servicio certificación con doble | Integrante 6 | unit test | 0.5 | Ninguna | TO-DO |
| I-21 | [R9] Probar servicio postulación con dobles | Integrante 3 | unit test | 1.0 | Ninguna | TO-DO |
| I-22 | [R9] Probar servicio notificación con dobles | Integrante 6 | unit test | 0.5 | Ninguna | TO-DO |
| I-23 | [R10–R11] Consolidar reportes globales y unitarios en `reports/` | Integrante 1 | enhancement | 1.0 | I-01–I-22 integrados | TO-DO |

**Criterios de aceptación de I-23:** después de integrar los issues I-01–I-22, ejecutar las variantes global y unitaria de [11-reportes-y-entrega.md](11-reportes-y-entrega.md); confirmar que todas las pruebas pasan; generar JUnit XML y cobertura XML/HTML global y unitaria; guardar todo en `reports/`; explicar cualquier resultado global menor a 80 % frente al baseline; versionar los reportes finales y enlazar el commit al issue.

Carga de pruebas R7–R9: Integrante 1 = 1.5 h; Integrante 2 = 1.5 h; Integrante 3 = 3 h; Integrante 4 = 1.5 h; Integrante 5 = 2 h; Integrante 6 = 2 h. I-23 añade 1 h de reportes a Integrante 1 en Fase 2. Totales de issues Fase 1–2: Integrante 1 = 2.5 h; Integrante 2 = 1.5 h; Integrante 3 = 3 h; Integrante 4 = 1.5 h; Integrante 5 = 2 h; Integrante 6 = 2 h. Suma 12.5 h entre seis personas; máximo individual 3 h, diferencia máxima 1.5 h. Todas las cargas caben en las 4 h del laboratorio. Son estimaciones iniciales.

## Flujo

`TO-DO` = sin iniciar; `CURRENT ITERATION` = comprometido para esta sesión; `IN PROGRESS` = rama/código en curso; `FIX VALIDATION` = el PR tuvo observaciones o falló CI y su autor aplica/valida la corrección; `DONE` = criterios completos, PR integrado y evidencia enlazada. Mover tarjeta al comenzar trabajo, al pedir revisión, y solo a DONE al integrar.
