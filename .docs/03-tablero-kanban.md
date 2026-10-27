# Tablero Kanban e issues

Relacionado: [reparto/horas](04-reparto-equipo.md), [convenciones](02-convenciones.md), [entrega](11-reportes-y-entrega.md).

## Creación

Responsable: persona con permiso de escritura en el repositorio y permiso de administrar Projects en la organización/cuenta propietaria. El repositorio pertenece a **MoisesCcaso**: pedir a su propietario que cree el Project o habilite el permiso si los demás no ven la opción. La persona coordinadora crea un GitHub Project, elige plantilla **KANBAN**, lo vincula al repo y deja estas columnas exactas y en orden: `TO-DO`, `CURRENT ITERATION`, `IN PROGRESS`, `FIX VALIDATION`, `DONE`. Confirmar permisos de lectura/escritura para seis integrantes antes de crear issues.

Etiquetas: `unit test` (tareas de pruebas R7–R9), `enhancement` (infraestructura, tablero, reportes o cambios habilitadores). Añadir `documentation` para documentación del laboratorio y `integration` para integración/reporte si la plantilla requiere filtrar por tipo; son complementarias, nunca sustituyen las dos etiquetas exigidas.

## Plantilla de issue

**Título:** `[R#] verbo + módulo`. Campos: descripción y alcance; responsable (Integrante N); etiqueta; estimación en horas; criterios verificables; dependencia (ID o ninguna); ruta de prueba asignada; definición de terminado: pruebas pasan, cobertura anotada, PR a development enlazado.

## Issues propuestos

Los IDs son provisionales; crear primero issues de infraestructura y luego sustituir `#` en commits. Inicio: tareas habilitadoras `TO-DO`; trabajo de pruebas `TO-DO` hasta concluir preparación.

| ID prov. | Título / descripción | Responsable | Etiqueta | h | Inicial |
|---|---|---:|---|---:|---|
| I-01 | [R3] Mover integración y compartir fixture SQLite en memoria | Integrante 1 | enhancement | 1.5 | TO-DO |
| I-02 | [R7] Probar dominio auth | Integrante 1 | unit test | 0.5 | TO-DO |
| I-03 | [R8] Probar repositorio de usuario | Integrante 1 | unit test | 0.5 | TO-DO |
| I-04 | [R9] Probar servicio de usuario con dobles | Integrante 1 | unit test | 0.5 | TO-DO |
| I-05 | [R7] Probar dominio perfil | Integrante 2 | unit test | 0.5 | TO-DO |
| I-06 | [R8] Probar repositorio perfil | Integrante 2 | unit test | 0.5 | TO-DO |
| I-07 | [R9] Probar servicio perfil con doble | Integrante 2 | unit test | 0.5 | TO-DO |
| I-08 | [R7] Probar dominio convocatorias | Integrante 3 | unit test | 0.5 | TO-DO |
| I-09 | [R8] Probar repositorio convocatoria | Integrante 3 | unit test | 0.5 | TO-DO |
| I-10 | [R8] Probar repositorio postulación | Integrante 3 | unit test | 0.5 | TO-DO |
| I-11 | [R9] Probar servicio convocatoria con dobles | Integrante 3 | unit test | 0.5 | TO-DO |
| I-12 | [R7] Probar dominio matching | Integrante 4 | unit test | 0.5 | TO-DO |
| I-13 | [R8] Probar repositorio matching | Integrante 4 | unit test | 0.5 | TO-DO |
| I-14 | [R9] Probar servicio matching con dobles | Integrante 4 | unit test | 0.5 | TO-DO |
| I-15 | [R7] Probar dominio práctica/evaluación | Integrante 5 | unit test | 0.5 | TO-DO |
| I-16 | [R8] Probar repositorio práctica | Integrante 5 | unit test | 0.5 | TO-DO |
| I-17 | [R8] Probar repositorio certificado | Integrante 5 | unit test | 0.5 | TO-DO |
| I-18 | [R9] Probar servicio práctica con dobles | Integrante 5 | unit test | 0.5 | TO-DO |
| I-19 | [R7] Probar dominio certificación | Integrante 6 | unit test | 0.5 | TO-DO |
| I-20 | [R8] Probar repositorio notificación | Integrante 6 | unit test | 0.5 | TO-DO |
| I-21 | [R9] Probar servicio certificación con doble | Integrante 6 | unit test | 0.5 | TO-DO |
| I-22 | [R9] Probar servicio postulación con dobles | Integrante 3 | unit test | 1.0 | TO-DO |
| I-23 | [R9] Probar servicio notificación con dobles | Integrante 6 | unit test | 0.5 | TO-DO |

Estimación total por persona: I1 3 h; I2 1.5 h; I3 3 h; I4 1.5 h; I5 2 h; I6 1.5 h. Máximo 3 h, dentro de las 4 h; el resto queda para coordinación, revisión, integración y reportes. Estimaciones son planificación inicial, ajustar el tablero si la guía docente define otra distribución.

## Flujo

`TO-DO` = sin iniciar; `CURRENT ITERATION` = comprometido para esta sesión; `IN PROGRESS` = rama/código en curso; `FIX VALIDATION` = el PR tuvo observaciones o falló CI y su autor aplica/valida la corrección; `DONE` = criterios completos, PR integrado y evidencia enlazada. Mover tarjeta al comenzar trabajo, al pedir revisión, y solo a DONE al integrar.
