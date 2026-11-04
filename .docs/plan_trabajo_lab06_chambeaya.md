# Plan de Trabajo – Laboratorio 06: Pruebas Funcionales sobre ChambeaYa

**Curso:** Ingeniería de Software II (UNSA) – DSc. Edgar Sarmiento Calisaya
**Duración:** 2 horas · **Equipo:** 6 integrantes
**Proyecto bajo prueba:** `https://github.com/MoisesCcaso/ChambeaYa` (Flask + Jinja + JS)
**Stack de pruebas:** Python 3.12 + Selenium WebDriver + pytest (xUnit: `setup`/`teardown`, `assert`, suites). El lab permite Python.

> Supuesto: el sistema bajo prueba es ChambeaYa en lugar de `springbootwebapp`. Si el docente exige este último, el reparto por áreas cambia, pero las tareas transversales y el flujo Git se mantienen.

---

## 1. Principio de reparto equitativo

Cada integrante recibe exactamente:

| Carga | Cantidad |
|-------|----------|
| Área funcional propia (diseñar + automatizar) | **6 casos de prueba** (36 en total) |
| Tarea transversal propia | **1** |
| Revisión cruzada de PR | **1 PR** del compañero siguiente (I1→I2→…→I6→I1) |
| Ramas / PRs | 1 rama, 1 PR a `development` |

## 2. Asignación

| Integrante | Área funcional (vista) | Tarea transversal | Rama |
|-----------|------------------------|-------------------|------|
| **I1** | Registro (`/registro`) | Crear `development`, estructura de carpetas, README de ejecución, merges finales | `lab6/functional-registro` |
| **I2** | Login / logout (`/ingresar`, `/app`) | Dependencias (`selenium`, `pytest`) en `pyproject.toml`, `conftest.py` (driver, URL base) y `BasePage` | `lab6/functional-login` |
| **I3** | Activación y recuperación de contraseña (`/activar`, `/recuperar`, `/restablecer`) | Datos de prueba: reinicio de BD demo, usuarios, `EXPOSE_AUTH_TOKENS` | `lab6/functional-recuperacion` |
| **I4** | Perfil practicante y perfil empresa (`/app` → Perfil) | Tabla consolidada de casos de prueba (E1) | `lab6/functional-perfiles` |
| **I5** | Convocatorias de empresa (crear, publicar, cerrar) | Reporte de ejecución (E3): `--junitxml` + HTML | `lab6/functional-convocatorias` |
| **I6** | Oportunidades y postulaciones (practicante) + verificación pública de certificado | Test Suite (marcadores pytest), ejecución completa y verificación final | `lab6/functional-postulaciones` |

## 3. Casos de prueba por integrante (caja negra)

Credenciales demo: `practicante@demo.local` / `empresa@demo.local`, contraseña `Demo1234`.
Regla de contraseña (verificada en `auth.js`): mínimo 8 caracteres, 1 minúscula, 1 mayúscula, 1 número.
Los resultados marcados con (*) deben confirmarse en la app antes de fijar el `assert`.

### I1 – Registro (clases de equivalencia + valores límite)

| ID | Objeto de prueba | Escenario / Acciones | Valores de prueba | Resultado esperado |
|----|------------------|----------------------|-------------------|--------------------|
| REG-01 | Registro | Datos válidos, tipo practicante | `nuevo@test.com`, `Abcd1234`, igual en confirmación | Registro aceptado; indica activar cuenta (*) |
| REG-02 | Contraseña | Límite inferior de longitud (7 caracteres) | `Abcd123` | Regla de longitud sin cumplir; "La contraseña todavía no cumple todos los requisitos." |
| REG-03 | Contraseña | Límite exacto (8 caracteres) | `Abcd1234` | Todas las reglas marcadas como cumplidas |
| REG-04 | Contraseña | Falta mayúscula / minúscula / número (3 clases inválidas) | `abcd1234`, `ABCD1234`, `Abcdefgh` | Regla correspondiente sin cumplir; no envía |
| REG-05 | Confirmación | Contraseñas distintas | `Abcd1234` vs `Abcd1235` | "Las contraseñas no coinciden." |
| REG-06 | Email | Correo ya registrado / formato inválido | `practicante@demo.local`; `sin-arroba` | Error en contexto; no crea cuenta (*) |

### I2 – Login / logout (tabla de decisión: email × contraseña × estado)

| ID | Objeto de prueba | Escenario / Acciones | Valores de prueba | Resultado esperado |
|----|------------------|----------------------|-------------------|--------------------|
| LOG-01 | Login | Credenciales válidas practicante | `practicante@demo.local` / `Demo1234` | Redirige a `/app` con vista de practicante |
| LOG-02 | Login | Credenciales válidas empresa | `empresa@demo.local` / `Demo1234` | Redirige a `/app` con menú de empresa |
| LOG-03 | Login | Contraseña incorrecta | `practicante@demo.local` / `Incorrecta1` | Mensaje de error; permanece en `/ingresar` |
| LOG-04 | Login | Email inexistente | `nadie@demo.local` / `Demo1234` | Mensaje de error; permanece en `/ingresar` |
| LOG-05 | Acceso | `/app` sin sesión | URL directa | Redirige a `/ingresar` |
| LOG-06 | Logout | Cerrar sesión y volver atrás | Botón `logout-button` | Sesión terminada; `/app` redirige a `/ingresar` |

### I3 – Activación y recuperación de contraseña (casos de uso)

| ID | Objeto de prueba | Escenario / Acciones | Valores de prueba | Resultado esperado |
|----|------------------|----------------------|-------------------|--------------------|
| REC-01 | Activación | Enlace con token válido | Token obtenido por API (`EXPOSE_AUTH_TOKENS=true`) | Cuenta activada; permite iniciar sesión |
| REC-02 | Activación | Token inválido | `token=invalido` | Mensaje de error (*) |
| REC-03 | Login | Cuenta sin activar | Usuario recién registrado | Error "La cuenta no está activa" (*) |
| REC-04 | Recuperar | Solicitud con email existente | `practicante@demo.local` | "Solicitud procesada…" y paso a `/restablecer` |
| REC-05 | Restablecer | Nueva contraseña válida | `Nueva1234` | Contraseña cambiada; login con la nueva funciona |
| REC-06 | Restablecer | Nueva contraseña inválida | `corta` | Rechazada con mensaje de error (*) |

### I4 – Perfiles (clases de equivalencia)

| ID | Objeto de prueba | Escenario / Acciones | Valores de prueba | Resultado esperado |
|----|------------------|----------------------|-------------------|--------------------|
| PER-01 | Perfil practicante | Guardar datos válidos | Nombre y datos completos | Estado de guardado exitoso en `student-profile-status` |
| PER-02 | Perfil practicante | Agregar habilidad | `Python` | Aparece en `skills-list` |
| PER-03 | Perfil practicante | Habilidad vacía | `` | No se agrega (*) |
| PER-04 | Perfil practicante | Agregar formación | `Ing. de Sistemas` | Aparece en `education-list` |
| PER-05 | Perfil empresa | Guardar con RUC válido | RUC de 11 dígitos | Guardado exitoso en `company-profile-status` |
| PER-06 | Perfil empresa | RUC inválido (límite 10 y 12 dígitos) | `1234567890`, `123456789012` | Error de validación (*) |

### I5 – Convocatorias (casos de uso + estados)

| ID | Objeto de prueba | Escenario / Acciones | Valores de prueba | Resultado esperado |
|----|------------------|----------------------|-------------------|--------------------|
| CON-01 | Convocatoria | Crear con datos válidos | Título, descripción, habilidades | Aparece en estado `borrador` |
| CON-02 | Convocatoria | Título vacío | `` | Error de validación (*) |
| CON-03 | Convocatoria | Publicar desde borrador | Acción "Publicar" | Estado `publicada` |
| CON-04 | Convocatoria | Publicar una ya publicada | Reintento | Error "Solo una convocatoria en borrador puede publicarse" |
| CON-05 | Convocatoria | Cerrar convocatoria publicada | Acción "Cerrar" | Estado `cerrada` |
| CON-06 | Convocatoria | Ver candidatos de una convocatoria | Convocatoria con postulación | Lista de candidatos visible |

### I6 – Oportunidades, postulaciones y certificado público

| ID | Objeto de prueba | Escenario / Acciones | Valores de prueba | Resultado esperado |
|----|------------------|----------------------|-------------------|--------------------|
| POS-01 | Oportunidades | Listar convocatorias publicadas | Login practicante | Se muestran convocatorias publicadas |
| POS-02 | Postulación | Postular a una convocatoria | Convocatoria publicada | Aparece en "Postulaciones" |
| POS-03 | Postulación | Postular dos veces a la misma | Reintento | Error o botón deshabilitado (*) |
| POS-04 | Postulación | Postular a convocatoria cerrada | Convocatoria `cerrada` | No permitido (*) |
| POS-05 | Certificado | Verificar código válido | Código demo | Certificado reconocido en `/verificar-certificado` |
| POS-06 | Certificado | Verificar código inexistente | `XXXX-0000` | Mensaje de no encontrado (*) |

## 4. Estructura del proyecto de pruebas

```
src/test/functional/
├── conftest.py                  # driver, base_url, fixtures (I2, I3)
├── pages/
│   ├── base_page.py             # I2
│   ├── register_page.py         # I1
│   ├── login_page.py            # I2
│   ├── recovery_page.py         # I3
│   ├── profile_page.py          # I4
│   ├── convocatoria_page.py     # I5
│   └── postulacion_page.py      # I6
├── test_registro.py             # I1
├── test_login.py                # I2
├── test_recuperacion.py         # I3
├── test_perfiles.py             # I4
├── test_convocatorias.py        # I5
├── test_postulaciones.py        # I6
└── docs/casos_de_prueba.md      # E1 consolidado (I4)
```

Un método por caso de prueba. Cada archivo y su Page Object pertenecen a un solo integrante, así no hay conflictos de merge. `conftest.py` y `base_page.py` los entrega I2 primero y los demás los consumen.

**Ejecución:**

```bash
poetry install
.\demo.ps1 -Reset                       # app en http://127.0.0.1:5000 con datos demo
poetry run pytest src/test/functional --junitxml=reports/functional.xml --html=reports/functional.html
```

## 5. Entregables del laboratorio

| Entregable | Responsable |
|-----------|-------------|
| E1 Casos de prueba en formato tabular (consolidado) | I4 |
| E2 Proyecto de automatización de pruebas funcionales | I1–I6 (cada uno su parte) |
| E3 Reporte de ejecución xUnit | I5 |

## 6. Cronograma (2 horas)

| Tiempo | Actividad | Responsables |
|--------|-----------|--------------|
| 0:00–0:15 | Crear `development`, estructura de carpetas, README | I1 |
| 0:00–0:20 | Dependencias, `conftest.py`, `BasePage` (se mergea primero) | I2 |
| 0:00–0:20 | Datos demo, reinicio de BD, tokens de activación | I3 |
| 0:20–0:50 | Diseño final de casos de prueba de cada área | I1–I6 |
| 0:50–1:30 | Automatización: 1 método por caso, en su rama | I1–I6 |
| 1:30–1:45 | PRs a `development` y revisión cruzada | I1–I6 |
| 1:45–1:55 | Ejecución completa, reporte y tabla consolidada | I4, I5, I6 |
| 1:55–2:00 | Merge final y entrega | I1 |

## 7. Flujo Git (convenciones del repositorio)

Se siguen las reglas de `.docs/02-convenciones.md` del repo.

### 7.1 Ramas

- `main`: estable. `development`: integración; **no existe aún en el remoto**, la crea I1 desde `main`.
- Ramas de trabajo: `lab6/functional-<area>` (ver tabla de asignación), creadas desde `development` actualizado.
- Un PR por rama hacia `development`. Nunca PR a `main` ni commit directo a `main` o `development`.
- Antes del PR: `git fetch origin && git rebase origin/development`.
- No reescribir una rama ya publicada sin avisar al equipo.

### 7.2 Comandos

```bash
# I1: una sola vez
git checkout main && git pull origin main
git checkout -b development && git push -u origin development

# Cada integrante
git checkout development && git pull origin development
git checkout -b lab6/functional-login
git config user.name "Tu Nombre" && git config user.email "tu-correo@unsa.edu.pe"

# trabajo y commits...

git fetch origin && git rebase origin/development
git push -u origin lab6/functional-login
# Abrir PR hacia development; reviewer = compañero siguiente

# Cierre (I1, con todas las ramas ya integradas y pruebas en verde)
git checkout main && git merge --no-ff development && git push origin main
```

### 7.3 Commits

Formato: `tipo(scope): verbo y objeto` en imperativo, breve. Tipos: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `build`, `ci`, `style`.
Scopes sugeridos: `tests-functional-registro`, `tests-functional-login`, `tests-functional-recuperacion`, `tests-functional-perfiles`, `tests-functional-convocatorias`, `tests-functional-postulaciones`, `tests-config`, `reports`.
Footer: `fix #<n>` con el número real del issue asignado, como exige el repo.

```
build(tests-config): agregar selenium y pytest al grupo dev
test(tests-functional-login): cubrir contraseña incorrecta
test(tests-functional-registro): validar límite de 8 caracteres
feat(tests-functional-login): crear page object de inicio de sesión
docs(tests-functional-perfiles): consolidar tabla de casos de prueba
chore(reports): guardar reporte de ejecución funcional
```

No usar: `update`, `cambios`, `final`, `test: cosas`. Un cambio lógico por commit.

## 8. Definition of Done

- [ ] App corriendo localmente con datos demo.
- [ ] 36 casos diseñados (6 por integrante) y consolidados en E1.
- [ ] Un método de prueba por caso, con `assert`.
- [ ] Los resultados marcados con (*) confirmados contra la app real.
- [ ] 6 PRs integrados en `development` con revisión cruzada.
- [ ] Reporte de ejecución (`reports/functional.xml` y `.html`) generado.
- [ ] Fallos reales documentados como defectos, no ocultos.
- [ ] `development` integrado en `main` al final.

## 9. Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| Pruebas dependientes entre áreas (p. ej. postular requiere convocatoria publicada) | Usar datos demo y reiniciar con `demo.ps1 -Reset`; no depender del resultado de otro test |
| Activación requiere token por correo | `EXPOSE_AUTH_TOKENS=true` en entorno de prueba |
| Conflictos en `pyproject.toml` | Solo I2 lo modifica |
| Selectores frágiles | Page Objects y selectores por `id`/`name` (`auth-form`, `skill-input`, `logout-button`) |
| Tiempo (2 h) | Priorizar casos válidos y de límite; los (*) se cierran al final |
