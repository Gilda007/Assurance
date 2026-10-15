#!/bin/bash
# ============================================================================
# SCRIPT INTERACTIF DE CRÉATION DE BASE DE DONNÉES POSTGRESQL POUR LOMETA
# Version Linux / macOS
# ============================================================================

# ============================================================================
# COULEURS
# ============================================================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

# ============================================================================
# FONCTIONS
# ============================================================================

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}============================================================${RESET}"
    echo -e "${BOLD}${BLUE}      CRÉATION DE LA BASE DE DONNÉES LOMETA${RESET}"
    echo -e "${BOLD}${BLUE}============================================================${RESET}"
    echo ""
}

print_success() {
    echo -e "${GREEN}[OK]${RESET} $1"
}

print_error() {
    echo -e "${RED}[ERREUR]${RESET} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${RESET} $1"
}

print_warning() {
    echo -e "${YELLOW}[ATTENTION]${RESET} $1"
}

print_separator() {
    echo ""
    echo -e "${BOLD}----------------------------------------------------------------${RESET}"
    echo ""
}

# ============================================================================
# SAISIE DES INFORMATIONS
# ============================================================================

get_config() {
    print_header
    
    echo -e "${BOLD}📋 Configuration de la connexion PostgreSQL${RESET}"
    echo ""
    echo "Veuillez renseigner les informations suivantes :"
    echo ""
    
    # Hôte PostgreSQL
    read -p "Hôte PostgreSQL [localhost] : " PG_HOST
    PG_HOST=${PG_HOST:-localhost}
    
    # Port PostgreSQL
    read -p "Port PostgreSQL [5432] : " PG_PORT
    PG_PORT=${PG_PORT:-5432}
    
    # Utilisateur administrateur
    read -p "Utilisateur administrateur PostgreSQL [postgres] : " PG_ADMIN
    PG_ADMIN=${PG_ADMIN:-postgres}
    
    # Mot de passe administrateur (masqué)
    echo ""
    echo -e "${YELLOW}⚠️  Entrez le mot de passe de l'administrateur PostgreSQL${RESET}"
    read -s -p "Mot de passe : " PG_PASSWORD
    echo ""
    
    # Vérifier que le mot de passe n'est pas vide
    if [ -z "$PG_PASSWORD" ]; then
        print_error "Le mot de passe est requis."
        exit 1
    fi
    
    echo ""
    print_separator
    
    # ========================================================================
    # SAISIE DES INFORMATIONS DE LA BASE
    # ========================================================================
    
    echo -e "${BOLD}📋 Configuration de la base de données${RESET}"
    echo ""
    
    # Nom de la base de données
    read -p "Nom de la base de données [lometa_db] : " DB_NAME
    DB_NAME=${DB_NAME:-lometa_db}
    
    # Nom de l'utilisateur
    read -p "Nom d'utilisateur [lometa_user] : " DB_USER
    DB_USER=${DB_USER:-lometa_user}
    
    # Mot de passe de l'utilisateur
    echo ""
    read -s -p "Mot de passe de l'utilisateur (masqué) : " DB_PASSWORD
    echo ""
    DB_PASSWORD=${DB_PASSWORD:-Lom3t@2024#Secure!}
    
    echo ""
    print_separator
    
    # ========================================================================
    # CONFIRMATION
    # ========================================================================
    
    echo -e "${BOLD}📋 RÉCAPITULATIF DE LA CONFIGURATION${RESET}"
    echo ""
    echo -e "   ${BOLD}Connexion PostgreSQL :${RESET}"
    echo -e "      Hôte     : $PG_HOST"
    echo -e "      Port     : $PG_PORT"
    echo -e "      Admin    : $PG_ADMIN"
    echo ""
    echo -e "   ${BOLD}Base de données :${RESET}"
    echo -e "      Nom       : $DB_NAME"
    echo -e "      Utilisateur : $DB_USER"
    echo ""
    echo -e "${YELLOW}⚠️  ATTENTION : Ce script va créer :${RESET}"
    echo -e "   - Base de données '$DB_NAME'"
    echo -e "   - Utilisateur '$DB_USER' avec le mot de passe défini"
    echo -e "   - Droits complets sur la base"
    echo ""
    read -p "Continuer ? (o/N) : " CONFIRM
    
    if [[ ! "$CONFIRM" =~ ^[OoYy]$ ]]; then
        echo "Annulé."
        exit 0
    fi
    
    echo ""
    print_separator
}

# ============================================================================
# VÉRIFICATION DE POSTGRESQL
# ============================================================================

check_postgres() {
    print_info "Vérification de PostgreSQL..."
    
    # Vérifier si psql est disponible
    if ! command -v psql &> /dev/null; then
        print_error "PostgreSQL n'est pas installé ou psql n'est pas dans le PATH."
        echo ""
        echo "Veuillez installer PostgreSQL :"
        echo "   Ubuntu/Debian : sudo apt install postgresql postgresql-contrib"
        echo "   Fedora/RHEL   : sudo dnf install postgresql-server postgresql-contrib"
        echo "   Arch Linux    : sudo pacman -S postgresql"
        echo "   macOS         : brew install postgresql"
        echo ""
        exit 1
    fi
    
    # Récupérer la version
    PG_VERSION=$(psql --version 2>&1)
    print_success "PostgreSQL trouvé : $PG_VERSION"
    echo ""
}

# ============================================================================
# TEST DE CONNEXION
# ============================================================================

test_connection() {
    print_info "Test de connexion à PostgreSQL..."
    
    # Tester la connexion
    export PGPASSWORD="$PG_PASSWORD"
    if ! psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN" -d postgres -c "SELECT 1" &> /dev/null; then
        unset PGPASSWORD
        print_error "Échec de la connexion à PostgreSQL."
        echo ""
        echo "Vérifiez :"
        echo "   - PostgreSQL est en cours d'exécution"
        echo "   - Le mot de passe est correct"
        echo "   - L'utilisateur '$PG_ADMIN' existe"
        echo "   - Le port $PG_PORT est ouvert"
        echo ""
        exit 1
    fi
    
    unset PGPASSWORD
    print_success "Connexion établie avec succès."
    echo ""
}

# ============================================================================
# CRÉATION DE LA BASE DE DONNÉES ET DE L'UTILISATEUR
# ============================================================================

create_database() {
    print_info "Création de la base de données et de l'utilisateur..."
    
    export PGPASSWORD="$PG_PASSWORD"
    
    # 1. Créer l'utilisateur
    print_info "Création de l'utilisateur '$DB_USER'..."
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN" -d postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" &> /dev/null; then
        print_success "Utilisateur '$DB_USER' créé."
    else
        print_warning "L'utilisateur '$DB_USER' existe peut-être déjà."
    fi
    
    # 2. Créer la base de données
    print_info "Création de la base de données '$DB_NAME'..."
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" &> /dev/null; then
        print_success "Base de données '$DB_NAME' créée."
    else
        print_warning "La base de données '$DB_NAME' existe peut-être déjà."
    fi
    
    # 3. Donner les droits sur la base
    print_info "Attribution des droits..."
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN" -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" &> /dev/null; then
        print_success "Droits sur la base '$DB_NAME' attribués."
    else
        print_error "Erreur lors de l'attribution des droits sur la base."
    fi
    
    # 4. Donner les droits sur le schéma public
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN" -d "$DB_NAME" -c "GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;" &> /dev/null; then
        print_success "Droits sur le schéma public attribués."
    else
        print_warning "Erreur lors de l'attribution des droits sur le schéma public."
    fi
    
    # 5. Donner les droits par défaut sur les tables
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN" -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO $DB_USER;" &> /dev/null; then
        print_success "Droits par défaut sur les tables attribués."
    else
        print_warning "Erreur lors de l'attribution des droits par défaut (non bloquante)."
    fi
    
    # 6. Donner les droits sur les séquences
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN" -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO $DB_USER;" &> /dev/null; then
        print_success "Droits par défaut sur les séquences attribués."
    else
        print_warning "Erreur lors de l'attribution des droits sur les séquences."
    fi
    
    # 7. Donner les droits sur les fonctions
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN" -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON FUNCTIONS TO $DB_USER;" &> /dev/null; then
        print_success "Droits par défaut sur les fonctions attribués."
    else
        print_warning "Erreur lors de l'attribution des droits sur les fonctions."
    fi
    
    unset PGPASSWORD
    echo ""
}

# ============================================================================
# INSTALLATION DES EXTENSIONS
# ============================================================================

create_extensions() {
    print_info "Installation des extensions PostgreSQL..."
    
    export PGPASSWORD="$PG_PASSWORD"
    
    # Extension UUID
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" &> /dev/null; then
        print_success "Extension 'uuid-ossp' installée."
    else
        print_warning "Extension 'uuid-ossp' : échec (non bloquant)."
    fi
    
    # Extension pgcrypto
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;" &> /dev/null; then
        print_success "Extension 'pgcrypto' installée."
    else
        print_warning "Extension 'pgcrypto' : échec (non bloquant)."
    fi
    
    # Extension pg_trgm (recherche textuelle)
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;" &> /dev/null; then
        print_success "Extension 'pg_trgm' installée."
    else
        print_warning "Extension 'pg_trgm' : échec (non bloquant)."
    fi
    
    # Extension btree_gist (index avancés)
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_ADMIN" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS btree_gist;" &> /dev/null; then
        print_success "Extension 'btree_gist' installée."
    else
        print_warning "Extension 'btree_gist' : échec (non bloquant)."
    fi
    
    unset PGPASSWORD
    echo ""
}

# ============================================================================
# AFFICHAGE DES INFORMATIONS FINALES
# ============================================================================

show_info() {
    echo ""
    echo -e "${BOLD}${GREEN}============================================================${RESET}"
    echo -e "${BOLD}${GREEN}      INSTALLATION TERMINÉE AVEC SUCCÈS !${RESET}"
    echo -e "${BOLD}${GREEN}============================================================${RESET}"
    echo ""
    echo -e "${BOLD}📋 Informations de connexion :${RESET}"
    echo ""
    echo -e "   ${BOLD}Connexion PostgreSQL :${RESET}"
    echo -e "      Hôte     : $PG_HOST"
    echo -e "      Port     : $PG_PORT"
    echo ""
    echo -e "   ${BOLD}Base de données :${RESET}"
    echo -e "      Nom       : $DB_NAME"
    echo -e "      Utilisateur : $DB_USER"
    echo -e "      Mot de passe : ********"
    echo ""
    echo -e "${BOLD}🔗 Chaîne de connexion (DSN) :${RESET}"
    echo -e "    postgresql://$DB_USER:$DB_PASSWORD@$PG_HOST:$PG_PORT/$DB_NAME"
    echo ""
    echo -e "${BOLD}📝 Fichier config.ini :${RESET}"
    echo ""
    echo "[DATABASE]"
    echo "host = $PG_HOST"
    echo "port = $PG_PORT"
    echo "database = $DB_NAME"
    echo "user = $DB_USER"
    echo "password = $DB_PASSWORD"
    echo ""
    echo -e "${BOLD}🔄 Pour tester la connexion :${RESET}"
    echo -e "    psql -h $PG_HOST -p $PG_PORT -U $DB_USER -d $DB_NAME"
    echo ""
    echo -e "${YELLOW}⚠️  Conservez ces informations en lieu sûr !${RESET}"
    echo ""
    read -p "Appuyez sur Entrée pour continuer..."
}

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

main() {
    # Récupérer les informations
    get_config
    
    # Vérifier PostgreSQL
    check_postgres
    
    # Tester la connexion
    test_connection
    
    # Créer la base de données
    create_database
    
    # Créer les extensions
    create_extensions
    
    # Afficher les informations
    show_info
}

# ============================================================================
# LANCEMENT
# ============================================================================

main