#!/bin/bash
# update.sh - Script de mise à jour

echo "🔄 Mise à jour du projet..."

# Sauvegarder les modifications locales
echo "📦 Sauvegarde des modifications locales..."
git stash push -m "Auto-save before update"

# Récupérer les dernières modifications
echo "⬇️  Récupération des dernières modifications..."
git fetch --all --prune

# Mettre à jour la branche courante
echo "🔧 Mise à jour de la branche..."
git pull --rebase

# Restaurer les modifications
echo "♻️  Restauration des modifications..."
git stash pop

echo "✅ Mise à jour terminée !"