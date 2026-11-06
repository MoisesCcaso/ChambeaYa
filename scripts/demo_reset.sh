#!/usr/bin/env bash
# Equivalente Linux/macOS de demo.ps1: reinicia la BD demo y levanta la app.
# Uso: scripts/demo_reset.sh [--no-reset]
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python="$root/.venv/bin/python"
[ -x "$python" ] || { echo "No se encontró .venv. Ejecuta poetry install." >&2; exit 1; }

cd "$root"
export FLASK_ENV=demo
export SECRET_KEY=chambeaya-demo-local
export DATABASE_URL=sqlite:///chambeaya-demo.db
export PYTHONPATH="$root/src/main"
app=(-m flask --app frameworks.flask_mvc.app:create_app)

if [ "${1:-}" != "--no-reset" ]; then
    rm -f "$root/instance/chambeaya-demo.db"
    echo "Base de demostración reiniciada."
fi

"$python" "${app[@]}" db upgrade
"$python" "${app[@]}" seed-demo
echo "ChambeaYa en http://127.0.0.1:5000 (Ctrl+C para detener)"
exec "$python" "${app[@]}" run --no-reload
