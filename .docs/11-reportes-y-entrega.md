# Reportes y entrega

Relacionado: [reparto](04-reparto-equipo.md).

## Preparar y ejecutar Poetry + pytest

Desde la raíz del repositorio, usar Python 3.12 (el proyecto exige `>=3.12`). Poetry necesita que ese intérprete ya esté instalado; verifica la versión antes de instalar dependencias. Si ya tienes Poetry, salta el paso de instalación.

Bash en Ubuntu/Linux y macOS (instalador oficial de Poetry, solo si `poetry --version` no responde):

```bash
python3 --version
curl -sSL https://install.python-poetry.org | python3 -
poetry --version
poetry env use python3.12
poetry install
poetry run python --version
poetry run pytest -v
```

PowerShell (si `poetry --version` no responde):

```powershell
py -3.12 --version
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
poetry --version
poetry env use (py -3.12 -c "import sys; print(sys.executable)")
poetry install
poetry run python --version
poetry run pytest -v
```

`poetry install` lee `poetry.lock` y el grupo no opcional `dev`, que contiene pytest y pytest-cov. `poetry run` ejecuta herramientas dentro del entorno del proyecto. El resultado de `poetry run python --version` debe ser 3.12 o posterior; pytest debe terminar con código 0 y mostrar los tests descubiertos. Para ver cobertura en terminal: `poetry run pytest --cov --cov-report=term-missing`. La suite existente usa `unittest.TestCase`, que pytest descubre; después de Fase 0, las rutas unitarias por capa se pueden ejecutar con el segundo comando de reportes de abajo. Si `poetry` no se reconoce tras instalar, abre una terminal nueva y revisa PATH según las instrucciones oficiales de Poetry.

Desde la raíz, con Poetry instalado y dependencias del grupo dev (`poetry install`). Bash/macOS:

```bash
mkdir -p reports
poetry run pytest -v --junitxml=reports/junit.xml --cov --cov-report=term-missing --cov-report=html:reports/htmlcov --cov-report=xml:reports/coverage.xml
poetry run pytest -v tests/domain tests/infrastructure tests/application --junitxml=reports/junit-unit.xml --cov --cov-report=term-missing --cov-report=html:reports/unit-htmlcov --cov-report=xml:reports/unit-coverage.xml
```

PowerShell:

```powershell
New-Item -ItemType Directory -Force reports | Out-Null
poetry run pytest -v --junitxml=reports/junit.xml --cov --cov-report=term-missing --cov-report=html:reports/htmlcov --cov-report=xml:reports/coverage.xml
poetry run pytest -v tests/domain tests/infrastructure tests/application --junitxml=reports/junit-unit.xml --cov --cov-report=term-missing --cov-report=html:reports/unit-htmlcov --cov-report=xml:reports/unit-coverage.xml
```

La primera ejecución incluye integración + unitarias: `reports/junit.xml`, `reports/coverage.xml`, `reports/htmlcov/`. La segunda limita tests unitarios por ruta: `reports/junit-unit.xml`, `reports/unit-coverage.xml`, `reports/unit-htmlcov/`. Ambos grupos de artefactos se versionan en Git después de la ejecución final; `.coverage` y cachés no. Los informes de cobertura calculan cobertura de código de producción; el filtro selecciona qué pruebas la ejercitan. No publicar como “cobertura unitaria” un informe obtenido con la suite global.

Cada integrante entrega en su PR: nombre/ruta de los tests, salida de pytest, líneas ejecutables/cubiertas de los archivos asignados, observaciones de fallos y enlace al issue. Tras integrar los seis PR, la persona integradora ejecuta ambos comandos desde `development`, revisa los reportes XML/HTML y versiona los artefactos finales en `reports/`.

## Checklist R1–R11

- [ ] R1 `main` + `development`; ramas de laboratorio desde `development` actualizado. Responsable: Integrante 1.
- [ ] R2 Poetry declara pytest y pytest-cov; `unittest.mock` estándar. Responsable: Integrante 1.
- [ ] R3 pruebas separadas por domain/infrastructure/application/integration. Responsable: Integrante 1.
- [ ] R4 Project KANBAN con cinco columnas exactas. Responsable: coordinador autorizado.
- [ ] R5 Issues con descripción, responsable, etiqueta, duración y criterios. Responsable: coordinador + equipo.
- [ ] R6 commits a `development` vía PR con Conventional Commits y footer `fix #n`. Responsable: cada integrante.
- [ ] R7 seis módulos de dominio con TDD y casos BDD. Responsable: Integrantes 1–6.
- [ ] R8 seis repositorios SQLite en memoria sin dobles. Responsable: Integrantes 1–6.
- [ ] R9 servicios de aplicación aislados con dobles de repositorios. Responsable: Integrantes 1–6.
- [ ] R10 JUnit XML refleja ejecución global y unitaria. Responsable: Integrante 1 al integrar.
- [ ] R11 cobertura global y unitaria en XML/HTML; cobertura global al menos 80 % o variación explicada frente a baseline reproducible. Responsable: Integrante 1 al integrar.
