# test_auth.py - Test de l'authentification
import requests
import json

BASE_URL = "http://127.0.0.1:8001/api/v1"

def test_generate_token():
    """Test de génération de token"""
    print("\n" + "="*50)
    print("TEST: GÉNÉRATION DE TOKEN")
    print("="*50)
    
    # Récupérer la clé applicative depuis la base
    # Pour ce test, utiliser la clé par défaut
    app_key = "TEST_APP_KEY_2024"
    username = "asac_admin"
    
    url = f"{BASE_URL}/auth/tokens/app-key"
    params = {
        "app_key": app_key,
        "username": username
    }
    
    try:
        response = requests.post(url, params=params)
        print(f"Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token généré avec succès!")
            print(f"   Token: {data['token'][:50]}...")
            print(f"   Nom: {data['token_name']}")
            print(f"   Expire le: {data['expires_at']}")
            return data['token']
        else:
            print(f"❌ Erreur: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def test_verify_token(token):
    """Test de vérification de token"""
    print("\n" + "="*50)
    print("TEST: VÉRIFICATION DE TOKEN")
    print("="*50)
    
    url = f"{BASE_URL}/auth/verify"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token valide!")
            print(f"   Utilisateur: {data['user']['username']}")
            print(f"   Email: {data['user']['email']}")
            return True
        else:
            print(f"❌ Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


if __name__ == "__main__":
    # 1. Générer un token
    token = test_generate_token()
    
    # 2. Vérifier le token
    if token:
        test_verify_token(token)