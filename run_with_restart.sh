#!/bin/bash
# run_with_restart.sh - Lanceur avec redémarrage automatique

echo "========================================"
echo "   LOMETA - Lanceur avec redémarrage"
echo "========================================"
echo ""

LOG_DIR="$HOME/Documents/LOMETA/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/launcher_$(date +%Y%m%d_%H%M%S).log"

while true; do
    echo "[$(date)] Démarrage de l'application..." | tee -a "$LOG_FILE"
    
    # Lancer l'application
    python3 main.py
    
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[$(date)] Application fermée normalement" | tee -a "$LOG_FILE"
        exit 0
    else
        echo "[$(date)] ATTENTION: Application crashée (code: $EXIT_CODE)" | tee -a "$LOG_FILE"
        echo "Redémarrage dans 5 secondes..."
        sleep 5
    fi
done