# update_client.py
"""
Client pour vérifier et télécharger les modules depuis le serveur
"""

import requests
from typing import List, Dict
from pathlib import Path


class UpdateClient:
    """Client simple pour interagir avec le serveur de modules"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url.rstrip('/')
        self.timeout = 10
    
    def get_available_modules(self) -> tuple:
        """
        Récupère la liste des modules disponibles
        
        Returns:
            (status_code, modules_list)
            200: Succès, modules_list contient la liste
            404: Serveur non trouvé
             autre: Erreur
        """
        try:
            response = requests.get(
                f"{self.server_url}/api/modules",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return 200, response.json()
            else:
                return response.status_code, []
                
        except requests.exceptions.ConnectionError:
            return 404, []  # Serveur non accessible
        except requests.exceptions.Timeout:
            return -1, []   # Timeout
        except Exception as e:
            print(f"Erreur: {e}")
            return -2, []
    
    def download_module(self, module: Dict, target_path: str, callback=None) -> bool:
        """
        Télécharge un module
        
        Args:
            module: Informations du module
            target_path: Chemin de destination
            callback: Fonction de progression(current, total)
        
        Returns:
            True si succès, False sinon
        """
        try:
            download_url = f"{self.server_url}{module['download_url']}"
            
            response = requests.get(download_url, stream=True, timeout=self.timeout)
            
            if response.status_code != 200:
                return False
            
            total = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            Path(target_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if callback and total > 0:
                            callback(downloaded, total)
            
            return True
            
        except Exception as e:
            print(f"Erreur téléchargement: {e}")
            return False