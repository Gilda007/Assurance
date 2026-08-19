#!/bin/bash
# ============================================================================
# Générateur de Certificat Développeur LOMETA
# ============================================================================
# Utilisation: ./generate_dev_certificate.sh [--help] [--validity DAYS]
# ============================================================================

set -e  # Arrêt en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ============================================================================
# FONCTIONS
# ============================================================================

print_header() {
    echo ""
    echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║              🔐 GÉNÉRATEUR DE CERTIFICAT DÉVELOPPEUR              ║${NC}"
    echo -e "${CYAN}${BOLD}║                          LOMETA v1.0                                ║${NC}"
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

# ============================================================================
# AFFICHAGE DE L'AIDE
# ============================================================================

show_help() {
    cat << EOF
📖 UTILISATION

    ./generate_dev_certificate.sh [OPTIONS]

📌 OPTIONS

    --validity DAYS    Durée de validité en jours (défaut: 365)
    --output DIR       Dossier de sortie (défaut: ./certificates)
    --help             Affiche cette aide

📝 EXEMPLES

    # Certificat standard (365 jours)
    ./generate_dev_certificate.sh

    # Certificat de test (30 jours)
    ./generate_dev_certificate.sh --validity 30

    # Certificat avec dossier personnalisé
    ./generate_dev_certificate.sh --output ./mes_certificats --validity 180

📁 FICHIERS GÉNÉRÉS

    developer_private_key.pem   🔑 Clé privée (À GARDER SECRÈTE !)
    developer_public_key.pem    🔓 Clé publique (À DISTRIBUER)
    lometa_ca.crt               📜 Certificat CA
    lometa_ca.pem               📜 Certificat CA (format PEM)
    certificate_chain.pem       🔗 Chaîne de certificats
    README.md                   📖 Instructions

🔐 SÉCURITÉ

    ⚠️  NE JAMAIS partager la clé privée (developer_private_key.pem)
    ✅  Partager uniquement la clé publique (developer_public_key.pem)
    ✅  Le certificat CA est à distribuer avec LOMETA

EOF
    exit 0
}

# ============================================================================
# PARAMÈTRES PAR DÉFAUT
# ============================================================================

VALIDITY_DAYS=365
OUTPUT_DIR="./certificates"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================================================
# TRAITEMENT DES ARGUMENTS
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_help
            ;;
        --validity)
            VALIDITY_DAYS="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
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

print_step "Vérification des prérequis..."

# Vérifier OpenSSL
if ! command -v openssl &> /dev/null; then
    print_error "OpenSSL n'est pas installé."
    echo "Installez-le avec: sudo apt-get install openssl (Ubuntu/Debian)"
    echo "ou: brew install openssl (macOS)"
    exit 1
fi
print_success "OpenSSL trouvé: $(openssl version)"

# Vérifier que le dossier de sortie existe
mkdir -p "$OUTPUT_DIR"
print_success "Dossier de sortie: $OUTPUT_DIR"

# ============================================================================
# GÉNÉRATION DES CERTIFICATS
# ============================================================================

print_separator
print_step "🔑 Génération des certificats"
print_separator

cd "$OUTPUT_DIR"

# ----------------------------------------------------------------------------
# 1. Générer la clé privée du développeur
# ----------------------------------------------------------------------------
print_step "1/5 Génération de la clé privée du développeur..."
if [ -f "developer_private_key.pem" ]; then
    print_warning "La clé privée existe déjà. Utilisation de la clé existante."
else
    openssl genrsa -out developer_private_key.pem 2048 2>/dev/null
    chmod 600 developer_private_key.pem
    print_success "Clé privée générée: developer_private_key.pem"
fi

# ----------------------------------------------------------------------------
# 2. Extraire la clé publique
# ----------------------------------------------------------------------------
print_step "2/5 Extraction de la clé publique..."
if [ -f "developer_public_key.pem" ]; then
    print_warning "La clé publique existe déjà."
else
    openssl rsa -in developer_private_key.pem -pubout -out developer_public_key.pem 2>/dev/null
    print_success "Clé publique extraite: developer_public_key.pem"
fi

# ----------------------------------------------------------------------------
# 3. Générer le certificat auto-signé (CA)
# ----------------------------------------------------------------------------
print_step "3/5 Génération du certificat CA (auto-signé)..."

# Créer un fichier de configuration OpenSSL
cat > openssl_ca.cnf << EOF
[req]
default_bits = 2048
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
CN = LOMETA Developer CA
O = LOMETA Technologies
OU = Developer Tools
C = CM
ST = Cameroon
L = Yaoundé

[v3_ca]
basicConstraints = critical, CA:TRUE
keyUsage = critical, digitalSignature, keyCertSign, cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
EOF

if [ ! -f "lometa_ca.crt" ]; then
    openssl req -x509 -new -nodes \
        -key developer_private_key.pem \
        -sha256 \
        -days "$VALIDITY_DAYS" \
        -out lometa_ca.crt \
        -config openssl_ca.cnf 2>/dev/null
    
    # Créer une version PEM du certificat
    cp lometa_ca.crt lometa_ca.pem
    
    print_success "Certificat CA généré: lometa_ca.crt (valide $VALIDITY_DAYS jours)"
else
    print_warning "Le certificat CA existe déjà."
fi

# ----------------------------------------------------------------------------
# 4. Créer la chaîne de certificats
# ----------------------------------------------------------------------------
print_step "4/5 Création de la chaîne de certificats..."
if [ ! -f "certificate_chain.pem" ]; then
    cat lometa_ca.crt developer_public_key.pem > certificate_chain.pem
    print_success "Chaîne de certificats: certificate_chain.pem"
fi

# ----------------------------------------------------------------------------
# 5. Générer un certificat exemple pour un module
# ----------------------------------------------------------------------------
print_step "5/5 Génération du certificat exemple pour un module..."

# Créer un CSR exemple
cat > openssl_module.cnf << EOF
[req]
default_bits = 2048
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = lometa.automobiles.v1
O = LOMETA Technologies
OU = Modules
C = CM

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth, serverAuth
EOF

# Générer la clé du module exemple
if [ ! -f "example_module_key.pem" ]; then
    openssl genrsa -out example_module_key.pem 2048 2>/dev/null
fi

# Générer le CSR du module exemple
if [ ! -f "example_module.csr" ]; then
    openssl req -new \
        -key example_module_key.pem \
        -out example_module.csr \
        -config openssl_module.cnf 2>/dev/null
fi

# Signer le CSR avec le certificat CA
if [ ! -f "example_module_cert.pem" ]; then
    openssl x509 -req \
        -in example_module.csr \
        -CA lometa_ca.crt \
        -CAkey developer_private_key.pem \
        -CAcreateserial \
        -out example_module_cert.pem \
        -days "$VALIDITY_DAYS" \
        -sha256 \
        -extfile openssl_module.cnf \
        -extensions v3_req 2>/dev/null
    
    print_success "Certificat exemple: example_module_cert.pem"
fi

# Vérifier le certificat exemple
if openssl verify -CAfile lometa_ca.crt example_module_cert.pem &>/dev/null; then
    print_success "✅ Certificat exemple vérifié avec succès"
else
    print_warning "⚠️ La vérification du certificat exemple a échoué"
fi

# ----------------------------------------------------------------------------
# 6. Nettoyage des fichiers temporaires
# ----------------------------------------------------------------------------
rm -f openssl_ca.cnf openssl_module.cnf

# ============================================================================
# AFFICHAGE DES RÉSULTATS
# ============================================================================

cd - > /dev/null

print_separator
print_step "📋 RÉSUMÉ DES FICHIERS GÉNÉRÉS"
print_separator

echo ""
echo -e "${BOLD}Fichier${NC}                          | ${BOLD}Description${NC}                          | ${BOLD}À partager${NC}"
echo -e "${CYAN}──────────────────────────────────────────┼──────────────────────────────────────────┼────────────────${NC}"
echo -e "developer_private_key.pem           | 🔑 Clé privée du développeur              | ${RED}NON${NC} ⚠️"
echo -e "developer_public_key.pem            | 🔓 Clé publique du développeur             | ${GREEN}OUI${NC}"
echo -e "lometa_ca.crt / lometa_ca.pem       | 📜 Certificat CA                          | ${GREEN}OUI${NC}"
echo -e "certificate_chain.pem               | 🔗 Chaîne de certificats                  | ${GREEN}OUI${NC}"
echo -e "example_module_cert.pem             | 📄 Certificat exemple                     | ${GREEN}OUI${NC}"
echo -e "example_module_key.pem              | 🔑 Clé privée exemple                     | ${RED}NON${NC} ⚠️"
echo -e "example_module.csr                  | 📝 Demande de signature                   | ${YELLOW}NON${NC}"
echo ""

print_separator
print_step "🔐 INSTRUCTIONS D'UTILISATION"
print_separator

echo ""
echo -e "${BOLD}1. Pour certifier un module:${NC}"
echo "   Utilisez le certificat CA (lometa_ca.crt) et la clé privée (developer_private_key.pem)"
echo ""
echo -e "${BOLD}2. Pour vérifier un certificat:${NC}"
echo "   openssl verify -CAfile lometa_ca.crt module_certificate.pem"
echo ""
echo -e "${BOLD}3. Distribuer la clé publique:${NC}"
echo "   Copiez developer_public_key.pem et lometa_ca.crt dans LOMETA/certificates/"
echo ""
echo -e "${BOLD}4. Intégration dans LOMETA:${NC}"
echo "   - Copier lometa_ca.crt → ~/.lometa/certificates/ca.crt"
echo "   - Copier developer_public_key.pem → ~/.lometa/certificates/developer.pub"
echo ""

print_separator
print_step "📁 EMPLACEMENT DES FICHIERS"
print_separator
echo ""
echo "   📂 $(realpath "$OUTPUT_DIR")"
ls -la "$OUTPUT_DIR" | grep -E "\.(pem|crt|csr)$" | while read line; do
    echo "      $line"
done
echo ""

print_separator
print_success "✅ Génération du certificat développeur terminée !"
print_separator
echo ""

# ============================================================================
# GÉNÉRATION DU README
# ============================================================================

cat > "$OUTPUT_DIR/README.md" << 'EOF'
# 🔐 Certificats Développeur LOMETA

## Fichiers Générés

| Fichier | Description | Sécurité |
|---------|-------------|----------|
| `developer_private_key.pem` | Clé privée du développeur | 🔒 SECRET - À ne jamais partager |
| `developer_public_key.pem` | Clé publique | 📤 À distribuer |
| `lometa_ca.crt` | Certificat CA | 📤 À distribuer |
| `certificate_chain.pem` | Chaîne de certificats | 📤 À distribuer |

## Sécurité

⚠️ **IMPORTANT** :
- La clé privée (`developer_private_key.pem`) doit rester SECRÈTE
- Ne jamais la commiter dans Git
- Ne jamais la partager

## Utilisation

### Certifier un module

```bash
# 1. Générer la clé du module
openssl genrsa -out module_key.pem 2048

# 2. Créer le CSR
openssl req -new -key module_key.pem -out module.csr

# 3. Signer avec le CA
openssl x509 -req -in module.csr \
    -CA lometa_ca.crt \
    -CAkey developer_private_key.pem \
    -CAcreateserial \
    -out module_cert.pem \
    -days 365 \
    -sha256

# 4. Vérifier
openssl verify -CAfile lometa_ca.crt module_cert.pem