#!/bin/sh
# Instala el wheel de dist/ en <dir> y levanta ChambeaYa en 127.0.0.1:<puerto>.
# La BD (<dir>/chambeaya.db) persiste entre despliegues: solo se migra.
# Si la version nueva no responde en /health, vuelve a la anterior (codigo y BD).
# Uso: scripts/ci/deploy.sh <dir> <puerto>
set -eu

D=$1
PORT=$2
WHEEL=$(ls dist/*.whl)
DB="$D/chambeaya.db"
mkdir -p "$D"
[ -f "$D/secret_key" ] || python3 -c 'import secrets; print(secrets.token_hex())' > "$D/secret_key"

# modo demo: ProductionConfig exige cookies Secure y el login no funcionaria por http
export FLASK_APP=bootstrap.app:create_app FLASK_ENV=demo DEMO_PASSWORD=Demo1234
export DATABASE_URL="sqlite:///$DB" FLASK_PORT="$PORT"
SECRET_KEY=$(cat "$D/secret_key")
export SECRET_KEY

stop() {
    if [ -f "$D/app.pid" ]; then
        kill "$(cat "$D/app.pid")" 2>/dev/null || true
        rm -f "$D/app.pid"
        sleep 2
    fi
}

# dontKillMe: Jenkins no mata el proceso al terminar el build
start() {
    JENKINS_NODE_COOKIE=dontKillMe setsid nohup "$1/bin/chambeaya" > "$D/app.log" 2>&1 &
    echo $! > "$D/app.pid"
}

healthy() {
    for _ in $(seq 30); do
        # sin esto, otro proceso en el mismo puerto haria pasar el chequeo
        kill -0 "$(cat "$D/app.pid")" 2>/dev/null || return 1
        curl -sf "http://127.0.0.1:$PORT/health" > /dev/null && return 0
        sleep 1
    done
    return 1
}

# cada version en su carpeta (un venv no se puede mover); current apunta a la activa
NEW="$D/releases/$(date +%Y%m%d%H%M%S)"
PREV=$(readlink "$D/current" || true)
python3 -m venv "$NEW"
"$NEW/bin/pip" install -q "$WHEEL"

stop
if curl -s "http://127.0.0.1:$PORT/" > /dev/null; then
    echo "El puerto $PORT esta ocupado por otro proceso" >&2
    rm -rf "$NEW"
    exit 1
fi
rm -f "$DB.bak"
if [ -f "$DB" ]; then cp "$DB" "$DB.bak"; fi

if "$NEW/bin/flask" db upgrade && "$NEW/bin/flask" seed-demo && start "$NEW" && healthy; then
    ln -sfn "$NEW" "$D/current"
    # se conservan la version activa y la anterior para rollback
    ls -1d "$D"/releases/* | sort | head -n -2 | xargs -r rm -rf
    echo "ChambeaYa desplegado en http://127.0.0.1:$PORT ($(basename "$WHEEL"))"
    exit 0
fi

echo "Fallo el despliegue; log de la version nueva:" >&2
cat "$D/app.log" >&2 || true
stop
rm -rf "$NEW"
if [ -n "$PREV" ]; then
    echo "Rollback a $PREV" >&2
    if [ -f "$DB.bak" ]; then mv "$DB.bak" "$DB"; fi
    start "$PREV"
    healthy || echo "La version anterior tampoco responde" >&2
fi
exit 1
