# generate_secret_key.py
"""
Script pour générer une clé secrète sécurisée pour les sessions
Exécutez : python generate_secret_key.py
"""

import secrets
import base64

def generate_secret_key():
    """Génère une clé secrète aléatoire pour les sessions"""
    # Génère 32 bytes aléatoires (256 bits)
    key = secrets.token_bytes(32)
    # Encode en base64 pour stockage facile
    encoded_key = base64.urlsafe_b64encode(key).decode()
    return encoded_key

if __name__ == "__main__":
    key = generate_secret_key()
    print("\n" + "="*60)
    print("🔑 VOTRE CLÉ SECRÈTE POUR LES SESSIONS")
    print("="*60)
    print(f"\n{key}\n")
    print("Ajoutez cette ligne à votre fichier .env :")
    print(f"SESSION_SECRET_KEY={key}")
    print("="*60)