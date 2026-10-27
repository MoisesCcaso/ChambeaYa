# Reportes y entrega

Relacionado: [reparto](04-reparto-equipo.md).

## Preparar y ejecutar Poetry + pytest

Desde la raíz del repositorio, usar Python 3.12 (el proyecto exige `>=3.12`) y Poetry 2.4.3, la versión registrada en `poetry.lock`. Comprueba ambas versiones antes de instalar dependencias. `poetry.toml` configura el entorno virtual del proyecto como `.venv`; el archivo `.env` es solo para la configuración local de Flask.

Bash en Ubuntu/Linux (si la versión del sistema no es 2.4.3, instala Poetry aislado con pipx):

```bash
python3 --version
# El sudo se usa solo para instalar pipx desde los paquetes de Ubuntu.
sudo apt install pipx
pipx ensurepath
pipx install "poetry==2.4.3"
~/.local/bin/poetry --version
~/.local/bin/poetry env use python3.12
~/.local/bin/poetry install
~/.local/bin/poetry run python --version
~/.local/bin/poetry run pytest -v
```

En macOS, instala Poetry 2.4.3 mediante la [guía oficial](https://python-poetry.org/docs/#installation). En PowerShell, el instalador oficial permite fijar la versión requerida:

```powershell
py -3.12 --version
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py - --version 2.4.3
poetry --version
poetry env use (py -3.12 -c "import sys; print(sys.executable)")
poetry install
poetry run python --version
poetry run pytest -v
```

`poetry install` lee `poetry.lock` y el grupo no opcional `dev`, que contiene pytest y pytest-cov. `poetry run` ejecuta herramientas dentro de `.venv`. El resultado de `poetry --version` debe ser 2.4.3 y `poetry run python --version` debe ser 3.12 o posterior. En Ubuntu, usa la ruta `~/.local/bin/poetry` en todos los comandos si `/usr/bin/poetry` apunta a una versión anterior. La suite existente usa `unittest.TestCase`, que pytest descubre; después de Fase 0, las rutas unitarias por capa se pueden ejecutar con el segundo comando de reportes de abajo.

Desde la raíz, con Poetry instalado y dependencias del grupo dev (`poetry install`). Bash/macOS:

```bash
mkdir -p reports
poetry run pytest -v --junitxml=reports/junit.xml --cov --cov-report=term-missing --cov-report=html:reports/htmlcov --cov-report=xml:reports/coverage.xml
poetry run pytest -v src/test/domain src/test/infrastructure src/test/application --junitxml=reports/junit-unit.xml --cov --cov-report=term-missing --cov-report=html:reports/unit-htmlcov --cov-report=xml:reports/unit-coverage.xml
```

PowerShell:

```powershell
New-Item -ItemType Directory -Force reports | Out-Null
poetry run pytest -v --junitxml=reports/junit.xml --cov --cov-report=term-missing --cov-report=html:reports/htmlcov --cov-report=xml:reports/coverage.xml
poetry run pytest -v src/test/domain src/test/infrastructure src/test/application --junitxml=reports/junit-unit.xml --cov --cov-report=term-missing --cov-report=html:reports/unit-htmlcov --cov-report=xml:reports/unit-coverage.xml
```

La primera ejecución incluye integración + unitarias: `reports/junit.xml`, `reports/coverage.xml`, `reports/htmlcov/`. La segunda limita tests unitarios por ruta: `reports/junit-unit.xml`, `reports/unit-coverage.xml`, `reports/unit-htmlcov/`. Coverage.py crea un `reports/htmlcov/.gitignore` que oculta su HTML; al versionar los reportes finales, fuerza la inclusión de esas carpetas:

```bash
git add reports/junit.xml reports/coverage.xml reports/junit-unit.xml reports/unit-coverage.xml
git add -f reports/htmlcov reports/unit-htmlcov
```

En PowerShell se usan los mismos comandos Git. Versionar los reportes después de la ejecución final; `.coverage` y cachés no. Los informes de cobertura calculan cobertura de código de producción; el filtro selecciona qué pruebas la ejercitan. No publicar como “cobertura unitaria” un informe obtenido con la suite global.

Cada integrante entrega en su PR: nombre/ruta de los tests, salida de pytest, líneas ejecutables/cubiertas de los archivos asignados, observaciones de fallos y enlace al issue. Tras integrar los seis PR, la persona integradora ejecuta ambos comandos desde `development`, revisa los reportes XML/HTML y versiona los artefactos finales en `reports/`.

## Checklist R1–R11

- [ ] R1 `main` + `development`; ramas de laboratorio desde `development` actualizado. Responsable: Integrante 1.
- [ ] R2 Poetry declara pytest y pytest-cov; `unittest.mock` estándar. Responsable: Integrante 1.
- [x] R3 implementación en `src/main/` y pruebas en `src/test/`, con pruebas organizadas por domain/infrastructure/application/integration. La suite de partida pasa (12/12) tras el cambio de rutas. Responsable: Integrante 1.
- [ ] R4 Project KANBAN con cinco columnas exactas. Responsable: coordinador autorizado.
- [ ] R5 Issues con descripción, responsable, etiqueta, duración y criterios. Responsable: coordinador + equipo.
- [ ] R6 commits a `development` vía PR con Conventional Commits y footer `fix #n`. Responsable: cada integrante.
- [ ] R7 seis módulos de dominio con TDD y casos BDD. Responsable: Integrantes 1–6.
- [ ] R8 seis repositorios SQLite en memoria sin dobles. Responsable: Integrantes 1–6.
- [ ] R9 servicios de aplicación aislados con dobles de repositorios. Responsable: Integrantes 1–6.
- [ ] R10 JUnit XML refleja ejecución global y unitaria. Responsable: Integrante 1 al integrar.
- [ ] R11 cobertura global y unitaria en XML/HTML; cobertura global al menos 80 % o variación explicada frente a baseline reproducible. Responsable: Integrante 1 al integrar.
