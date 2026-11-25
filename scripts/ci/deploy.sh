#!/bin/sh
# Instala el wheel de dist/ en <dir> y levanta la API REST en 127.0.0.1:<api_port>
# y el cliente (vistas) en 127.0.0.1:<client_port>.
# La BD (<dir>/chambeaya.db) persiste entre despliegues: solo se migra.
# Si la version nueva no responde (API en /health y cliente en /), vuelve a la anterior (codigo y BD).
# Uso: scripts/ci/deploy.sh <dir> <api_port> <client_port>
set -eu

D=$1
PORT=$2
CLIENT_PORT=$3
WHEEL=$(ls dist/*.whl)
DB="$D/chambeaya.db"
mkdir -p "$D"
[ -f "$D/secret_key" ] || python3 -c 'import secrets; print(secrets.token_hex())' > "$D/secret_key"

# modo demo: ProductionConfig exige cookies Secure y el login no funcionaria por http
export FLASK_APP=bootstrap.app:create_app FLASK_ENV=demo DEMO_PASSWORD=Demo1234
export DATABASE_URL="sqlite:///$DB" FLASK_PORT="$PORT" CLIENT_PORT="$CLIENT_PORT"
# mismo host para los dos: la cookie de sesion de la API viaja entre puertos (same-site)
export API_URL="http://127.0.0.1:$PORT" APP_URL="http://127.0.0.1:$CLIENT_PORT"
export CLIENT_ORIGINS="$APP_URL"
SECRET_KEY=$(cat "$D/secret_key")
export SECRET_KEY

stop() {
    for name in app client; do
        if [ -f "$D/$name.pid" ]; then
            kill "$(cat "$D/$name.pid")" 2>/dev/null || true
            rm -f "$D/$name.pid"
        fi
    done
    sleep 2
}

# dontKillMe: Jenkins no mata los procesos al terminar el build
start() {
    JENKINS_NODE_COOKIE=dontKillMe setsid nohup "$1/bin/chambeaya" > "$D/app.log" 2>&1 &
    echo $! > "$D/app.pid"
    JENKINS_NODE_COOKIE=dontKillMe setsid nohup "$1/bin/chambeaya-client" > "$D/client.log" 2>&1 &
    echo $! > "$D/client.pid"
}

healthy() {
    for _ in $(seq 30); do
        # sin esto, otro proceso en el mismo puerto haria pasar el chequeo
        kill -0 "$(cat "$D/app.pid")" 2>/dev/null || return 1
        kill -0 "$(cat "$D/client.pid")" 2>/dev/null || return 1
        curl -sf "http://127.0.0.1:$PORT/health" > /dev/null \
            && curl -sf "http://127.0.0.1:$CLIENT_PORT/" > /dev/null && return 0
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
for p in "$PORT" "$CLIENT_PORT"; do
    if curl -s "http://127.0.0.1:$p/" > /dev/null; then
        echo "El puerto $p esta ocupado por otro proceso" >&2
        rm -rf "$NEW"
        exit 1
    fi
done
rm -f "$DB.bak"
if [ -f "$DB" ]; then cp "$DB" "$DB.bak"; fi

if "$NEW/bin/flask" db upgrade && "$NEW/bin/flask" seed-demo && start "$NEW" && healthy; then
    ln -sfn "$NEW" "$D/current"
    # se conservan la version activa y la anterior para rollback
    ls -1d "$D"/releases/* | sort | head -n -2 | xargs -r rm -rf
    echo "ChambeaYa desplegado: cliente http://127.0.0.1:$CLIENT_PORT, API http://127.0.0.1:$PORT ($(basename "$WHEEL"))"
    exit 0
fi

echo "Fallo el despliegue; logs de la version nueva:" >&2
cat "$D/app.log" "$D/client.log" >&2 || true
stop
rm -rf "$NEW"
if [ -n "$PREV" ]; then
    echo "Rollback a $PREV" >&2
    if [ -f "$DB.bak" ]; then mv "$DB.bak" "$DB"; fi
    # una version previa a la separacion no tiene chambeaya-client: solo se levanta la API
    if [ -x "$PREV/bin/chambeaya-client" ]; then
        start "$PREV"
        healthy || echo "La version anterior tampoco responde" >&2
    else
        JENKINS_NODE_COOKIE=dontKillMe setsid nohup "$PREV/bin/chambeaya" > "$D/app.log" 2>&1 &
        echo $! > "$D/app.pid"
    fi
fi
exit 1
