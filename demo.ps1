param(
    [switch]$Reset
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
$demoDatabase = Join-Path $projectRoot "instance\chambeaya-demo.db"

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "No se encontró .venv. Crea el entorno e instala requirements.txt primero."
}

Set-Location -LiteralPath $projectRoot
$env:FLASK_ENV = "demo"
$env:SECRET_KEY = "chambeaya-demo-local"
$env:DATABASE_URL = "sqlite:///chambeaya-demo.db"

if ($Reset -and (Test-Path -LiteralPath $demoDatabase)) {
    Remove-Item -LiteralPath $demoDatabase -Force
    Write-Host "Base de demostración reiniciada." -ForegroundColor Yellow
}

& $pythonPath -m flask --app frameworks.flask_mvc.app:create_app db upgrade
if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron aplicar las migraciones."
}

& $pythonPath -m flask --app frameworks.flask_mvc.app:create_app seed-demo
if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron crear los datos de demostración."
}

Write-Host ""
Write-Host "ChambeaYa está listo para la presentación:" -ForegroundColor Cyan
Write-Host "  URL:          http://127.0.0.1:5000"
Write-Host "  Practicante: practicante@demo.local / Demo1234"
Write-Host "  Empresa:      empresa@demo.local / Demo1234"
Write-Host ""
Write-Host "Presiona Ctrl+C para detener la aplicación."

& $pythonPath -m flask --app frameworks.flask_mvc.app:create_app run --no-reload
