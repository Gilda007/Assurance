#!/bin/bash
# backup.sh - Script shell pour backup LOMETA

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="${SCRIPT_DIR}/backup_manager.py"
LOG_FILE="/var/log/lometa_backup.log"
PID_FILE="/var/run/lometa_backup.pid"

# Fonction de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Vérifier si le script tourne déjà
check_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log "⚠️ Un backup est déjà en cours (PID: $pid)"
            exit 1
        else
            rm -f "$PID_FILE"
        fi
    fi
}

# Créer le dossier de logs si nécessaire
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

# Vérifier que le script Python existe
if [ ! -f "$BACKUP_SCRIPT" ]; then
    log "❌ Script Python non trouvé: $BACKUP_SCRIPT"
    exit 1
fi

# Vérifier que pg_dump est disponible
if ! command -v pg_dump &> /dev/null; then
    log "❌ pg_dump non trouvé. PostgreSQL n'est pas installé."
    exit 1
fi

# Vérifier que Python est disponible
if ! command -v python3 &> /dev/null; then
    log "❌ Python3 non trouvé"
    exit 1
fi

# Exécuter le backup
check_running
echo $$ > "$PID_FILE"

log "🚀 Démarrage du backup"

# Exécuter le script Python
python3 "$BACKUP_SCRIPT"
BACKUP_EXIT_CODE=$?

# Nettoyer
rm -f "$PID_FILE"

if [ $BACKUP_EXIT_CODE -eq 0 ]; then
    log "✅ Backup terminé avec succès"
else
    log "❌ Backup échoué (code: $BACKUP_EXIT_CODE)"
fi

exit $BACKUP_EXIT_CODE