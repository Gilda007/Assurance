# test_bcrypt.py
import bcrypt

# Le hash stocké en BD
stored_hash = "$2b$12$BbwusPQjzfe8kSBe6GrMQOE4Fqw7HMX6XI1NcrLoYHiamjGujjB/2"

# Le mot de passe en clair (à remplacer par celui que vous utilisez)
password = "Admin123"

# Vérifier
if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
    print("✅ Mot de passe correct !")
else:
    print("❌ Mot de passe incorrect")