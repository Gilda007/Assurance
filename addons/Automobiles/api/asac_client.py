# addons/Automobiles/api/asac_client.py
"""
Client HTTP pour l'API ASAC
"""

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class AsacAPIError(Exception):
    """Exception pour les erreurs de l'API ASAC"""
    def __init__(self, message: str, status_code: int = None, errors: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.errors = errors


class AsacCredentials:
    """Identifiants de connexion ASAC"""
    def __init__(self, app_key: str, username: str, api_url: str = "http://localhost:8001"):
        self.app_key = app_key
        self.username = username
        self.api_url = api_url


class AsacClient:
    """Client pour l'API ASAC"""
    
    def __init__(self, credentials: AsacCredentials):
        self.credentials = credentials
        self.token = None
        self.session = requests.Session()
    
    def authenticate(self) -> str:
        """
        Authentification pour obtenir un token
        """
        url = f"{self.credentials.api_url}/api/v1/auth/tokens/app-key"
        
        params = {
            "app_key": self.credentials.app_key,
            "username": self.credentials.username
        }
        
        try:
            response = self.session.post(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get("token")
            
            # Ajouter le token aux headers
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            
            logger.info(f"Authentifié avec succès")
            return self.token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur d'authentification: {e}")
            raise AsacAPIError(f"Erreur d'authentification: {str(e)}")
        
    # addons/Automobiles/api/asac_client.py - Version avec logs détaillés

    def create_production(self, production_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée une production d'attestation
        """
        if not self.token:
            self.authenticate()
        
        url = f"{self.credentials.api_url}/api/v1/productions"
        
        # Afficher la requête complète pour debug
        import json
        print("\n" + "="*60)
        print("📤 REQUÊTE ENVOYÉE À L'API ASAC:")
        print("="*60)
        # Nettoyer les dates pour l'affichage
        request_copy = json.loads(json.dumps(production_request, default=str))
        print(json.dumps(request_copy, indent=2, default=str))
        print("="*60 + "\n")
        
        try:
            response = self.session.post(url, json=production_request)
            
            if response.status_code == 401:
                # Token expiré, réauthentifier et réessayer
                self.authenticate()
                response = self.session.post(url, json=production_request)
            
            # Afficher la réponse
            print("\n" + "="*60)
            print("📥 RÉPONSE DE L'API ASAC:")
            print("="*60)
            print(f"Status: {response.status_code}")
            print(f"Body: {response.text}")
            print("="*60 + "\n")
            
            if response.status_code != 201:
                logger.error(f"❌ Erreur API: {response.status_code}")
                logger.error(f"   Réponse: {response.text}")
            
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la production: {e}")
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    message = error_data.get("message", str(e))
                    errors = error_data.get("errors", {})
                    
                    # Afficher les erreurs de validation
                    print("\n" + "="*60)
                    print("❌ ERREURS DE VALIDATION ASAC:")
                    print("="*60)
                    for field, err_list in errors.items():
                        for err in err_list:
                            print(f"   {field}: {err}")
                    print("="*60 + "\n")
                    
                    raise AsacAPIError(message, e.response.status_code, errors)
                except:
                    pass
            
            raise AsacAPIError(f"Erreur lors de la production: {str(e)}")