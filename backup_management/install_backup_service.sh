#!/bin/bash
# install_backup_service.sh - Version corrigée

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCÈS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[AVERTISSEMENT]${NC} $1"; }
print_error() { echo -e "${RED}[ERREUR]${NC} $1"; }
print_separator() { echo "============================================================"; }

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Ce script doit être exécuté en tant que root (sudo)"
        exit 1
    fi
}

check_files() {
    local missing_files=()
    for file in "backup_manager.py" "lometa-backup.sh" "lometa-backup.service" "lometa-backup.timer"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_error "Fichiers manquants:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi
}

create_directories() {
    print_info "Création des dossiers..."
    mkdir -p /var/backups/lometa
    mkdir -p /var/log
    mkdir -p /etc/default
    chmod 755 /var/backups/lometa
    print_success "Dossiers créés"
}

copy_files() {
    print_info "Copie des fichiers..."
    cp backup_manager.py /usr/local/bin/
    cp lometa-backup.sh /usr/local/bin/
    cp lometa-backup.service /etc/systemd/system/
    cp lometa-backup.timer /etc/systemd/system/
    chmod +x /usr/local/bin/backup_manager.py
    chmod +x /usr/local/bin/lometa-backup.sh
    print_success "Fichiers copiés"
}

# Nouvelle fonction pour configurer la base de données
configure_database() {
    print_info "Configuration de la base de données..."
    
    # Demander les paramètres de connexion
    read -p "Hôte PostgreSQL [$DB_HOST]: " input_host
    DB_HOST=${input_host:-"localhost"}
    
    read -p "Port PostgreSQL [$DB_PORT]: " input_port
    DB_PORT=${input_port:-"5432"}
    
    read -p "Nom de la base de données [$DB_NAME]: " input_db
    DB_NAME=${input_db:-"ams_db"}
    
    read -p "Utilisateur PostgreSQL [$DB_USER]: " input_user
    DB_USER=${input_user:-"ams_admin"}
    
    read -sp "Mot de passe PostgreSQL: " DB_PASSWORD
    echo ""
    
    # Tester la connexion
    print_info "Test de connexion à PostgreSQL..."
    
    export PGPASSWORD="$DB_PASSWORD"
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1; then
        print_success "Connexion réussie"
        
        # Mettre à jour le fichier backup_manager.py
        sed -i "s/DB_HOST = \".*\"/DB_HOST = \"$DB_HOST\"/" /usr/local/bin/backup_manager.py
        sed -i "s/DB_PORT = \".*\"/DB_PORT = \"$DB_PORT\"/" /usr/local/bin/backup_manager.py
        sed -i "s/DB_NAME = \".*\"/DB_NAME = \"$DB_NAME\"/" /usr/local/bin/backup_manager.py
        sed -i "s/DB_USER = \".*\"/DB_USER = \"$DB_USER\"/" /usr/local/bin/backup_manager.py
        sed -i "s/DB_PASSWORD = \".*\"/DB_PASSWORD = \"$DB_PASSWORD\"/" /usr/local/bin/backup_manager.py
        
        # Mettre à jour le script shell
        sed -i "s/DB_HOST=\".*\"/DB_HOST=\"$DB_HOST\"/" /usr/local/bin/lometa-backup.sh
        sed -i "s/DB_PORT=\".*\"/DB_PORT=\"$DB_PORT\"/" /usr/local/bin/lometa-backup.sh
        sed -i "s/DB_NAME=\".*\"/DB_NAME=\"$DB_NAME\"/" /usr/local/bin/lometa-backup.sh
        sed -i "s/DB_USER=\".*\"/DB_USER=\"$DB_USER\"/" /usr/local/bin/lometa-backup.sh
        
        unset PGPASSWORD
        return 0
    else
        print_error "Impossible de se connecter à PostgreSQL"
        print_warning "Vérifiez:"
        echo "  - Le serveur PostgreSQL est accessible: ping $DB_HOST"
        echo "  - Le port $DB_PORT est ouvert: nc -zv $DB_HOST $DB_PORT"
        echo "  - Les identifiants sont corrects"
        unset PGPASSWORD
        return 1
    fi
}

# Vérifier les prérequis
check_prerequisites() {
    print_info "Vérification des prérequis..."
    
    # Vérifier psql
    if ! command -v psql &> /dev/null; then
        print_error "PostgreSQL client non installé (psql)"
        print_info "Installez-le avec: apt install postgresql-client -y"
        exit 1
    fi
    
    # Vérifier python3
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 non installé"
        exit 1
    fi
    
    print_success "Prérequis vérifiés"
}

reload_systemd() {
    print_info "Rechargement de systemd..."
    systemctl daemon-reload
    print_success "Systemd rechargé"
}

enable_timer() {
    print_info "Activation du timer..."
    systemctl enable lometa-backup.timer
    systemctl start lometa-backup.timer
    print_success "Timer activé"
}

check_status() {
    echo ""
    print_separator
    echo "STATUT:"
    systemctl status lometa-backup.timer --no-pager | head -10
    print_separator
    echo ""
    systemctl list-timers --no-pager | grep -E "NEXT|lometa" || echo "Timer en attente"
    print_separator
}

test_backup() {
    print_info "Test du backup..."
    if /usr/local/bin/lometa-backup.sh; then
        print_success "Test réussi"
    else
        print_error "Test échoué"
        tail -20 /var/log/lometa_backup.log 2>/dev/null || true
    fi
}

uninstall_service() {
    print_warning "Désinstallation..."
    systemctl stop lometa-backup.timer 2>/dev/null || true
    systemctl disable lometa-backup.timer 2>/dev/null || true
    rm -f /etc/systemd/system/lometa-backup.service
    rm -f /etc/systemd/system/lometa-backup.timer
    rm -f /usr/local/bin/backup_manager.py
    rm -f /usr/local/bin/lometa-backup.sh
    systemctl daemon-reload
    print_success "Désinstallé"
}

main_menu() {
    print_separator
    echo -e "${GREEN}INSTALLATION SERVICE BACKUP LOMETA${NC}"
    print_separator
    
    if [ "$1" == "--uninstall" ] || [ "$1" == "-u" ]; then
        uninstall_service
        exit 0
    fi
    
    check_root
    check_prerequisites
    check_files
    create_directories
    copy_files
    
    if configure_database; then
        reload_systemd
        enable_timer
        check_status
        
        echo ""
        read -p "Tester le backup immédiatement ? (o/N): " test_now
        if [[ $test_now =~ ^[OoYy]$ ]]; then
            test_backup
        fi
        
        print_separator
        print_success "✅ Installation terminée!"
        echo ""
        print_info "Commandes:"
        echo "  systemctl status lometa-backup.timer"
        echo "  tail -f /var/log/lometa_backup.log"
        echo "  sudo $0 --uninstall"
    else
        print_error "❌ Installation échouée"
        exit 1
    fi
}

# Variables par défaut
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="ams_db"
DB_USER="ams_admin"

main_menu "$@"