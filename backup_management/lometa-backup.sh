#!/bin/bash
# lometa-backup.sh - Point d'entrée du service systemd pour les backups LOMETA

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="${SCRIPT_DIR}/backup_manager.py"
LOG_FILE="/var/log/lometa_backup.log"
PID_FILE="/var/run/lometa_backup.pid"

if [ -f /etc/default/lometa-backup ]; then
    . /etc/default/lometa-backup
fi

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-ams_db}"
DB_USER="${DB_USER:-ams_admin}"
DB_PASSWORD="${DB_PASSWORD:-}"
SCP_TARGET="${SCP_TARGET:-}"
SCP_USER="${SCP_USER:-}"
SCP_PORT="${SCP_PORT:-22}"
SCP_REMOTE_PATH="${SCP_REMOTE_PATH:-~/backups_lometa}"
SCP_PRIVATE_KEY="${SCP_PRIVATE_KEY:-}"

export DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD SCP_TARGET SCP_USER SCP_PORT SCP_REMOTE_PATH SCP_PRIVATE_KEY

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$(dirname "$PID_FILE")"
touch "$LOG_FILE"

if [ -f "$PID_FILE" ]; then
    existing_pid=$(cat "$PID_FILE" 2>/dev/null || true)
    if [ -n "$existing_pid" ] && kill -0 "$existing_pid" 2>/dev/null; then
        log "Un backup est déjà en cours (PID: $existing_pid)"
        exit 1
    fi
fi

echo $$ > "$PID_FILE"
trap 'rm -f "$PID_FILE"' EXIT

log "Démarrage du backup LOMETA"
log "Connexion PostgreSQL: $DB_HOST:$DB_PORT/$DB_NAME ($DB_USER)"

if [ ! -f "$BACKUP_SCRIPT" ]; then
    log "Script Python introuvable: $BACKUP_SCRIPT"
    exit 1
fi

python3 "$BACKUP_SCRIPT"
