#!/bin/bash
# ============================================================================
# Certificateur de Module LOMETA
# ============================================================================
# Utilisation: ./certify_module.sh --module CHEMIN --validity JOURS [--certifier NOM]
# ============================================================================

set -e  # Arrêt en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ============================================================================
# FONCTIONS
# ============================================================================

print_header() {
    echo ""
    echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║              🔐 CERTIFICATEUR DE MODULE LOMETA                   ║${NC}"
    echo -e "${CYAN}${BOLD}║                          v1.0                                     ║${NC}"
    echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_step() {
    echo -e "${CYAN}📌 $1${NC}"
}

print_separator() {
    echo -e "${CYAN}────────────────────────────────────────────────────────────────────────${NC}"
}

print_key_value() {
    printf "   ${BOLD}%-20s${NC} : ${GREEN}%s${NC}\n" "$1" "$2"
}

# ============================================================================
# AFFICHAGE DE L'AIDE
# ============================================================================

show_help() {
    cat << EOF
📖 UTILISATION

    ./certify_module.sh --module CHEMIN --validity JOURS [OPTIONS]

📌 OPTIONS OBLIGATOIRES

    --module, -m CHEMIN      Chemin du dossier du module à certifier
    --validity, -v JOURS     Durée de validité en jours (OBLIGATOIRE)

📌 OPTIONS OPTIONNELLES

    --certifier, -c NOM      Nom du certifieur (défaut: LOMETA Authority)
    --output, -o CHEMIN      Dossier de sortie (défaut: ./certificates)
    --force, -f              Force la regénération du certificat
    --help, -h               Affiche cette aide

📝 EXEMPLES

    # Certifier un module pour 30 jours
    ./certify_module.sh --module ./addons/Automobiles --validity 30

    # Certifier avec un nom de certifieur personnalisé
    ./certify_module.sh --module ./addons/Automobiles --validity 365 --certifier "Fearless Cybertech"

    # Certifier pour une courte durée (test)
    ./certify_module.sh --module ./addons/Automobiles --validity 4 --certifier "Fearless Cybertech"

🔐 PRÉREQUIS

    Le script recherche la clé privée du développeur dans:
    1. ./certificates/developer_private_key.pem
    2. ~/.lometa/certificates/developer_private_key.pem
    3. /etc/lometa/certificates/developer_private_key.pem

📁 FICHIERS GÉNÉRÉS DANS LE MODULE

    certificate.json    📜 Certificat du module (format JSON)
    certificate.pem     📜 Certificat du module (format PEM)

EOF
    exit 0
}

# ============================================================================
# DÉTECTION DE LA CLÉ PRIVÉE
# ============================================================================

find_private_key() {
    local search_paths=(
        "./certificates/developer_private_key.pem"
        "$HOME/.lometa/certificates/developer_private_key.pem"
        "/etc/lometa/certificates/developer_private_key.pem"
        "./developer_private_key.pem"
        "../certificates/developer_private_key.pem"
    )
    
    for path in "${search_paths[@]}"; do
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    
    return 1
}

# ============================================================================
# VÉRIFICATION DU MANIFEST
# ============================================================================

validate_manifest() {
    local manifest_file="$1/manifest.json"
    
    if [ ! -f "$manifest_file" ]; then
        print_error "manifest.json non trouvé dans le module"
        print_info "Assurez-vous que le module contient un fichier manifest.json"
        return 1
    fi
    
    # Vérifier que le manifest est valide
    if ! python3 -c "import json; json.load(open('$manifest_file'))" 2>/dev/null; then
        print_error "manifest.json invalide (JSON mal formé)"
        return 1
    fi
    
    return 0
}

# ============================================================================
# PARAMÈTRES PAR DÉFAUT
# ============================================================================

VALIDITY_DAYS="4"          # ✅ Plus de valeur par défaut
CERTIFIER="LOMETA Authority"
OUTPUT_DIR="./certificates"
MODULE_PATH=""
FORCE=false

# ============================================================================
# TRAITEMENT DES ARGUMENTS
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            ;;
        --module|-m)
            MODULE_PATH="$2"
            shift 2
            ;;
        --validity|-v)
            VALIDITY_DAYS="$2"
            shift 2
            ;;
        --certifier|-c)
            CERTIFIER="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --force|-f)
            FORCE=true
            shift
            ;;
        *)
            print_error "Option inconnue: $1"
            echo "Utilisez --help pour l'aide"
            exit 1
            ;;
    esac
done

# ============================================================================
# VÉRIFICATION DES PRÉREQUIS
# ============================================================================

print_header

# ✅ Vérifier que le module est spécifié
if [ -z "$MODULE_PATH" ]; then
    print_error "Chemin du module non spécifié"
    echo "Utilisez --module pour spécifier le chemin"
    exit 1
fi

# ✅ Vérifier que la validité est spécifiée
if [ -z "$VALIDITY_DAYS" ]; then
    print_error "Durée de validité non spécifiée"
    echo "Utilisez --validity pour spécifier le nombre de jours"
    echo ""
    echo -e "${YELLOW}Exemple:${NC}"
    echo "   ./certify_module.sh --module ./addons/Automobiles --validity 30"
    exit 1
fi

# ✅ Vérifier que la validité est un nombre positif
if ! [[ "$VALIDITY_DAYS" =~ ^[0-9]+$ ]] || [ "$VALIDITY_DAYS" -lt 1 ]; then
    print_error "La validité doit être un nombre entier positif"
    echo "Valeur actuelle: '$VALIDITY_DAYS'"
    exit 1
fi

# Vérifier que le module existe
if [ ! -d "$MODULE_PATH" ]; then
    print_error "Le module n'existe pas: $MODULE_PATH"
    exit 1
fi

# Convertir en chemin absolu
MODULE_PATH=$(cd "$MODULE_PATH" && pwd)

print_step "Module à certifier: $MODULE_PATH"
print_step "Durée de validité: $VALIDITY_DAYS jours"

# Vérifier OpenSSL
if ! command -v openssl &> /dev/null; then
    print_error "OpenSSL n'est pas installé."
    echo "Installez-le avec: sudo apt-get install openssl (Ubuntu/Debian)"
    echo "ou: brew install openssl (macOS)"
    exit 1
fi

# Vérifier Python (pour le JSON)
if ! command -v python3 &> /dev/null; then
    print_error "Python3 n'est pas installé"
    exit 1
fi

# ============================================================================
# DÉTECTION DE LA CLÉ PRIVÉE
# ============================================================================

print_separator
print_step "🔑 Recherche de la clé privée du développeur"
print_separator

PRIVATE_KEY=$(find_private_key)

if [ -z "$PRIVATE_KEY" ]; then
    print_error "Clé privée du développeur non trouvée !"
    echo ""
    print_info "Recherche effectuée dans:"
    echo "   ./certificates/developer_private_key.pem"
    echo "   ~/.lometa/certificates/developer_private_key.pem"
    echo "   /etc/lometa/certificates/developer_private_key.pem"
    echo "   ./developer_private_key.pem"
    echo ""
    echo -e "${YELLOW}Pour générer une clé:${NC}"
    echo "   ./generate_dev_certificate.sh"
    exit 1
fi

print_success "Clé privée trouvée: $PRIVATE_KEY"

# Vérifier les permissions de la clé privée
if [ "$(stat -c %a "$PRIVATE_KEY" 2>/dev/null || stat -f %Lp "$PRIVATE_KEY" 2>/dev/null)" != "600" ]; then
    print_warning "Permissions de la clé privée non sécurisées"
    print_info "Correction des permissions..."
    chmod 600 "$PRIVATE_KEY"
    print_success "Permissions corrigées: 600"
fi

# ============================================================================
# CHARGEMENT DU MANIFEST
# ============================================================================

print_separator
print_step "📋 Lecture du manifest.json"
print_separator

if ! validate_manifest "$MODULE_PATH"; then
    exit 1
fi

# Extraire les informations du manifest
MANIFEST_FILE="$MODULE_PATH/manifest.json"
MODULE_NAME=$(python3 -c "import json; print(json.load(open('$MANIFEST_FILE')).get('name', 'unknown'))")
MODULE_VERSION=$(python3 -c "import json; print(json.load(open('$MANIFEST_FILE')).get('version', '1.0.0'))")

print_key_value "Nom du module" "$MODULE_NAME"
print_key_value "Version" "$MODULE_VERSION"
print_key_value "Validité" "$VALIDITY_DAYS jours"
print_key_value "Certifié par" "$CERTIFIER"

# ============================================================================
# VÉRIFICATION SI LE CERTIFICAT EXISTE DÉJÀ
# ============================================================================

CERT_FILE="$MODULE_PATH/certificate.json"
CERT_PEM="$MODULE_PATH/certificate.pem"

if [ -f "$CERT_FILE" ] && [ "$FORCE" = false ]; then
    print_warning "Un certificat existe déjà dans le module"
    echo ""
    read -p "Voulez-vous le remplacer ? (o/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[OoYy]$ ]]; then
        print_info "Opération annulée"
        exit 0
    fi
fi

# ============================================================================
# GÉNÉRATION DU CERTIFICAT
# ============================================================================

print_separator
print_step "🔐 Génération du certificat RSA"
print_separator

# Créer le dossier de sortie
mkdir -p "$OUTPUT_DIR"

# 1. Générer la clé privée du module
print_step "1/6 Génération de la clé privée du module..."
MODULE_KEY="$OUTPUT_DIR/${MODULE_NAME}_private_key.pem"
openssl genrsa -out "$MODULE_KEY" 2048 2>/dev/null
chmod 600 "$MODULE_KEY"
print_success "Clé privée du module: $MODULE_KEY"

# 2. Créer le fichier de configuration OpenSSL
print_step "2/6 Création de la configuration OpenSSL..."
cat > "$OUTPUT_DIR/openssl.cnf" << EOF
[req]
default_bits = 2048
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = $MODULE_NAME
O = $CERTIFIER
OU = LOMETA Modules
C = CM
ST = Cameroon
L = Yaoundé
emailAddress = admin@lometa.com

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = DNS:$MODULE_NAME.lometa.com
EOF
print_success "Configuration créée"

# 3. Générer le CSR
print_step "3/6 Génération du Certificate Signing Request (CSR)..."
CSR_FILE="$OUTPUT_DIR/${MODULE_NAME}.csr"
openssl req -new \
    -key "$MODULE_KEY" \
    -out "$CSR_FILE" \
    -config "$OUTPUT_DIR/openssl.cnf" 2>/dev/null
print_success "CSR généré: $CSR_FILE"

# 4. Trouver le certificat CA
print_step "4/6 Recherche du certificat CA..."
CA_CERT=$(find "$(dirname "$PRIVATE_KEY")" -name "lometa_ca.crt" 2>/dev/null | head -1)

if [ -z "$CA_CERT" ]; then
    # Chercher dans les dossiers courants
    for path in "./certificates/lometa_ca.crt" "$HOME/.lometa/certificates/lometa_ca.crt" "./lometa_ca.crt"; do
        if [ -f "$path" ]; then
            CA_CERT="$path"
            break
        fi
    done
fi

if [ -z "$CA_CERT" ]; then
    print_error "Certificat CA (lometa_ca.crt) non trouvé !"
    print_info "Générez-le d'abord avec: ./generate_dev_certificate.sh"
    exit 1
fi
print_success "Certificat CA trouvé: $CA_CERT"

# 5. Signer le certificat
print_step "5/6 Signature du certificat avec la clé privée du développeur..."
CERT_PEM_FINAL="$OUTPUT_DIR/${MODULE_NAME}_certificate.pem"

# Extraire la clé publique du développeur
PUBLIC_KEY=$(find "$(dirname "$PRIVATE_KEY")" -name "developer_public_key.pem" 2>/dev/null | head -1)
if [ -z "$PUBLIC_KEY" ]; then
    # Générer la clé publique si elle n'existe pas
    PUBLIC_KEY="$OUTPUT_DIR/developer_public_key.pem"
    openssl rsa -in "$PRIVATE_KEY" -pubout -out "$PUBLIC_KEY" 2>/dev/null
fi

openssl x509 -req \
    -in "$CSR_FILE" \
    -CA "$CA_CERT" \
    -CAkey "$PRIVATE_KEY" \
    -CAcreateserial \
    -out "$CERT_PEM_FINAL" \
    -days "$VALIDITY_DAYS" \
    -sha256 \
    -extfile "$OUTPUT_DIR/openssl.cnf" \
    -extensions v3_req 2>/dev/null

print_success "Certificat signé: $CERT_PEM_FINAL"

# 6. Vérifier le certificat
print_step "6/6 Vérification du certificat..."
if openssl verify -CAfile "$CA_CERT" "$CERT_PEM_FINAL" &>/dev/null; then
    print_success "✅ Certificat valide"
else
    print_warning "⚠️ La vérification du certificat a échoué"
fi

# ============================================================================
# CRÉATION DU CERTIFICAT JSON
# ============================================================================

print_separator
print_step "📄 Création du certificat JSON"
print_separator

# Calculer les checksums des fichiers
print_info "Calcul des checksums des fichiers..."

# Générer la liste des fichiers (exclure les fichiers de certificat)
FILES=$(find "$MODULE_PATH" -type f \
    ! -name "certificate.json" \
    ! -name "certificate.pem" \
    ! -name "*.pyc" \
    ! -path "*/__pycache__/*" \
    ! -path "*/.git/*" \
    ! -name ".DS_Store" \
    ! -name "*.pyc" \
    | sort)

# Créer le dictionnaire des checksums
CHECKSUMS="{"
COUNT=0
for file in $FILES; do
    rel_path="${file#$MODULE_PATH/}"
    # Échapper les guillemets dans le chemin
    rel_path_escaped=$(echo "$rel_path" | sed 's/"/\\"/g')
    checksum=$(sha256sum "$file" | cut -d' ' -f1)
    if [ $COUNT -gt 0 ]; then
        CHECKSUMS="$CHECKSUMS, "
    fi
    CHECKSUMS="$CHECKSUMS\"$rel_path_escaped\": \"$checksum\""
    COUNT=$((COUNT + 1))
done
CHECKSUMS="$CHECKSUMS }"

# Extraire les informations du certificat PEM
CERT_INFO=$(openssl x509 -in "$CERT_PEM_FINAL" -text -noout 2>/dev/null)
CERT_SERIAL=$(echo "$CERT_INFO" | grep "Serial Number:" | head -1 | sed 's/Serial Number: //' | tr -d ' ' | head -c 16)
CERT_SUBJECT=$(echo "$CERT_INFO" | grep "Subject:" | head -1 | sed 's/Subject: //')
CERT_ISSUER=$(echo "$CERT_INFO" | grep "Issuer:" | head -1 | sed 's/Issuer: //')

# ✅ Utiliser la date calculée plutôt que l'extraction
EXPIRY_DATE_ISO=$(date -u -Iseconds -d "+$VALIDITY_DAYS days" | sed 's/+00:00/Z/')
CERTIFIED_DATE_ISO=$(date -u -Iseconds | sed 's/+00:00/Z/')

# ✅ Pour not_before et not_after, utiliser les dates ISO
NOT_BEFORE_ISO=$(date -Iseconds)
NOT_AFTER_ISO=$(date -Iseconds -d "+$VALIDITY_DAYS days")

# Créer le fichier JSON
CERT_JSON=$(cat << EOF
{
  "version": "3.0.0",
  "certificate_type": "MODULE",
  "module_name": "$MODULE_NAME",
  "module_version": "$MODULE_VERSION",
  "certified_by": "$CERTIFIER",
  "certified_date": "$CERTIFIED_DATE_ISO",
  "expiry_date": "$EXPIRY_DATE_ISO",
  "certificate_id": "$CERT_SERIAL",
  "serial_number": "$CERT_SERIAL",
  "subject": "$CERT_SUBJECT",
  "issuer": "$CERT_ISSUER",
  "validity": {
    "not_before": "$NOT_BEFORE_ISO",
    "not_after": "$NOT_AFTER_ISO",
    "days": $VALIDITY_DAYS
  },
  "checksum_algorithm": "SHA-256",
  "checksums": $CHECKSUMS,
  "metadata": {
    "certified_by": "$CERTIFIER",
    "certification_date": "$CERTIFIED_DATE_ISO"
  },
  "signature_algorithm": "RSA-PSS-SHA256",
  "certificate_chain": []
}
EOF
)

# Sauvegarder le JSON
echo "$CERT_JSON" | python3 -m json.tool > "$CERT_FILE"
print_success "Certificat JSON: $CERT_FILE"

# Copier le certificat PEM dans le module
cp "$CERT_PEM_FINAL" "$CERT_PEM"
print_success "Certificat PEM: $CERT_PEM"

# ============================================================================
# NETTOYAGE
# ============================================================================

rm -f "$OUTPUT_DIR/openssl.cnf"

# ============================================================================
# RÉSULTATS
# ============================================================================

print_separator
print_step "📋 CERTIFICAT GÉNÉRÉ AVEC SUCCÈS"
print_separator
echo ""

print_key_value "Module" "$MODULE_NAME"
print_key_value "Version" "$MODULE_VERSION"
print_key_value "Certifié par" "$CERTIFIER"
print_key_value "Validité" "$VALIDITY_DAYS jours"
print_key_value "ID" "$CERT_SERIAL"
print_key_value "Date d'expiration" "$EXPIRY_DATE_ISO"
print_key_value "Fichiers vérifiés" "$(echo "$FILES" | wc -l)"

echo ""
print_separator
print_step "📁 FICHIERS GÉNÉRÉS"
print_separator
echo ""

echo -e "   ${BOLD}Dans le module:${NC}"
echo -e "   📜 $CERT_FILE"
echo -e "   📜 $CERT_PEM"
echo ""
echo -e "   ${BOLD}Dans le dossier de sortie:${NC}"
echo -e "   🔑 $MODULE_KEY"
echo -e "   📝 $CSR_FILE"
echo -e "   📜 $CERT_PEM_FINAL"

echo ""
print_separator
print_success "✅ Module certifié avec succès !"
print_separator
echo ""

# ============================================================================
# VÉRIFICATION FINALE
# ============================================================================

print_step "🔍 Vérification du certificat installé..."
if python3 -c "
import json
import hashlib
from pathlib import Path

cert_file = Path('$CERT_FILE')
if not cert_file.exists():
    print('❌ Certificat non trouvé')
    exit(1)

cert = json.loads(cert_file.read_text())
print(f'   ✅ Certificat chargé: {cert.get(\"certificate_id\", \"N/A\")}')
print(f'   ✅ Module: {cert.get(\"module_name\", \"N/A\")}')
print(f'   ✅ Version: {cert.get(\"module_version\", \"N/A\")}')
print(f'   ✅ Expiration: {cert.get(\"expiry_date\", \"N/A\")}')
" 2>/dev/null; then
    print_success "✅ Certificat installé et valide"
else
    print_warning "⚠️ Vérification du certificat échouée"
fi

echo ""
print_success "🎉 Opération terminée !"
echo ""
echo -e "${YELLOW}📌 Pour vérifier le certificat:${NC}"
echo "   openssl verify -CAfile $(dirname "$CA_CERT")/lometa_ca.crt $CERT_PEM"
echo ""