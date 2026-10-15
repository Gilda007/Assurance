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
