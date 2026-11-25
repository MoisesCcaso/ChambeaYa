param(
    [switch]$Reset
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
$demoDatabase = Join-Path $projectRoot "instance\chambeaya-demo.db"

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "No se encontró .venv. Ejecuta poetry install para crear el entorno e instalar el proyecto."
}

Set-Location -LiteralPath $projectRoot
$env:FLASK_ENV = "demo"
$env:SECRET_KEY = "chambeaya-demo-local"
$env:DATABASE_URL = "sqlite:///chambeaya-demo.db"
# Mismo host para los dos: la cookie de sesión de la API viaja entre puertos (same-site).
$env:API_URL = "http://127.0.0.1:5000"
$env:APP_URL = "http://127.0.0.1:5001"
$env:CLIENT_ORIGINS = "http://127.0.0.1:5001"
if (-not $env:DEMO_PASSWORD) {
    $env:DEMO_PASSWORD = "Demo1234"
}

if ($Reset -and (Test-Path -LiteralPath $demoDatabase)) {
    Remove-Item -LiteralPath $demoDatabase -Force
    Write-Host "Base de demostración reiniciada." -ForegroundColor Yellow
}

& $pythonPath -m flask --app bootstrap.app:create_app db upgrade
if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron aplicar las migraciones."
}

& $pythonPath -m flask --app bootstrap.app:create_app seed-demo
if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron crear los datos de demostración."
}

Write-Host ""
Write-Host "ChambeaYa está listo para la presentación:" -ForegroundColor Cyan
Write-Host "  Cliente:      http://127.0.0.1:5001"
Write-Host "  API REST:     http://127.0.0.1:5000"
Write-Host "  Practicante: practicante@demo.local / $env:DEMO_PASSWORD"
Write-Host "  Empresa:      empresa@demo.local / $env:DEMO_PASSWORD"
Write-Host ""
Write-Host "Presiona Ctrl+C para detener la aplicación."

$api = Start-Process -FilePath $pythonPath -NoNewWindow -PassThru -ArgumentList @(
    "-m", "flask", "--app", "bootstrap.app:create_app", "run", "--no-reload", "--port", "5000"
)
try {
    & $pythonPath -m flask --app client.app:create_app run --no-reload --port 5001
}
finally {
    Stop-Process -Id $api.Id -ErrorAction SilentlyContinue
}
