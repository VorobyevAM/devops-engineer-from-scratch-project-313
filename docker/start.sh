#!/bin/sh
set -eu

envsubst '${PORT} ${APP_PORT}' \
    < /etc/nginx/templates/default.conf.template \
    > /etc/nginx/conf.d/default.conf

.venv/bin/uvicorn main:app --host 127.0.0.1 --port "${APP_PORT}" &
app_pid=$!

cleanup() {
    kill "${app_pid}" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

nginx -g 'daemon off;'
