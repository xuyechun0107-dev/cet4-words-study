#!/bin/sh
set -eu

ENV_FILE=/opt/enplay/shared/api.env

if [ ! -r "$ENV_FILE" ]; then
    echo "Cannot read $ENV_FILE" >&2
    exit 1
fi

# api.env is an administrator-owned POSIX shell environment file. Export every
# assignment while loading it, without echoing any values into the journal.
set -a
# shellcheck disable=SC1090
. "$ENV_FILE"

: "${ADMIN_TOKEN:?api.env must set ADMIN_TOKEN}"

if [ -z "${DATABASE_URL:-}" ]; then
    : "${MYSQL_PASSWORD:?api.env must set DATABASE_URL or MYSQL_PASSWORD}"
    DATABASE_URL="mysql+pymysql://cet4:${MYSQL_PASSWORD}@127.0.0.1:3306/cet4?charset=utf8mb4"
fi

REDIS_URL=${REDIS_URL:-redis://127.0.0.1:6379/0}
PRESENCE_SECRET=${PRESENCE_SECRET:-$ADMIN_TOKEN}
AUDIO_ROOT=${AUDIO_ROOT:-/opt/enplay/shared/audio}
ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-https://enplay.aoke.ltd,https://enplay.ningboaoke.com,https://cet4-words-study.pages.dev}
ALLOWED_HOSTS=${ALLOWED_HOSTS:-api-enplay.aoke.ltd,api-enplay.ningboaoke.com,localhost,127.0.0.1}
set +a

cd /opt/enplay/current/api
exec /opt/enplay/venv/bin/uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 28100 \
    --workers 1 \
    --proxy-headers \
    --forwarded-allow-ips 127.0.0.1 \
    --no-server-header
