# Pruebas funcionales (Lab06)

Pruebas de caja negra de la interfaz web de ChambeaYa, automatizadas con
**Selenium WebDriver** y **pytest**. Cada vista tiene su Page Object en
`pages/` y su archivo `test_<área>.py`.

## Requisitos

- Python 3.12 o superior y [Poetry](https://python-poetry.org/).
- Google Chrome. Si no está instalado, Selenium Manager descarga una versión
  de prueba automáticamente la primera vez; no hace falta instalar el driver.

Instalar dependencias (incluye `selenium` y `pytest-html`):

```bash
poetry install
```

## 1. Levantar la aplicación demo

Las pruebas necesitan la app corriendo en `http://127.0.0.1:5000` con los datos
demo. Dejarla abierta en una terminal aparte.

**Windows (PowerShell):**

```powershell
.\demo.ps1 -Reset
```

**Linux / macOS** (equivalente a `demo.ps1`):

```bash
export FLASK_ENV=demo SECRET_KEY=chambeaya-demo-local DATABASE_URL=sqlite:///chambeaya-demo.db
rm -f instance/chambeaya-demo.db          # equivalente a -Reset (opcional)
poetry run flask --app frameworks.flask_mvc.app:create_app db upgrade
poetry run flask --app frameworks.flask_mvc.app:create_app seed-demo
poetry run flask --app frameworks.flask_mvc.app:create_app run --no-reload
```

En modo demo la app expone los tokens de activación y recuperación
(`EXPOSE_AUTH_TOKENS=True`), que usan las pruebas de activación y recuperación.

Credenciales demo:

| Rol | Correo | Contraseña |
|-----|--------|------------|
| Practicante | `practicante@demo.local` | `Demo1234` |
| Empresa | `empresa@demo.local` | `Demo1234` |

## 2. Ejecutar las pruebas

Desde la raíz del proyecto, en otra terminal:

```bash
# Suite funcional completa con reporte xUnit y HTML
poetry run pytest src/test/functional \
  --junitxml=reports/functional.xml \
  --html=reports/functional.html --self-contained-html

# Un solo archivo
poetry run pytest src/test/functional/test_registro.py

# Un solo caso
poetry run pytest "src/test/functional/test_registro.py::test_reg_05_confirmacion_distinta_de_la_contrasena"
```

Chrome se ejecuta en modo headless (sin ventana), según `conftest.py`.

Los reportes `reports/functional.xml` y `reports/functional.html` están en
`.gitignore`.

### Usar otra URL o puerto

```bash
CHAMBEAYA_BASE_URL=http://127.0.0.1:5055 poetry run pytest src/test/functional
```

### Solo pruebas unitarias (sin navegador ni app)

`poetry run pytest` sin argumentos también incluye las pruebas funcionales.
Para ejecutar solo las unitarias:

```bash
poetry run pytest src/test --ignore=src/test/functional
```

## Estructura

```text
src/test/functional/
├── conftest.py          # fixtures driver (Chrome headless) y base_url
├── auth_data.py         # creación de cuentas únicas por API
├── pages/               # Page Objects (base_page.py y uno por vista)
└── test_<área>.py       # un archivo por área, un método por caso
```

## Problemas frecuentes

| Síntoma | Causa probable |
|---------|----------------|
| `ERR_CONNECTION_REFUSED` o tiempo de espera agotado en todas las pruebas | La app no está corriendo o está en otro puerto (`CHAMBEAYA_BASE_URL`) |
| Falla el token de activación | La app no se levantó en modo demo (`FLASK_ENV=demo`) |
| Fallan casos que dependen de datos demo | Reiniciar la base: `.\demo.ps1 -Reset` o borrar `instance/chambeaya-demo.db` |
