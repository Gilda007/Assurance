# module_detector.py
import os
import json
from pathlib import Path
from typing import Dict, List, Optional


class ModuleDetector:
    """Détecte les modules installés localement et leurs versions"""
    
    def __init__(self, addons_dir: str = None):
        self.addons_dir = addons_dir or self._get_default_addons_dir()
        self.installed_modules = {}
        self._scan_modules()
    
    def _get_default_addons_dir(self) -> str:
        """Détermine le dossier des addons"""
        # Priorité : variable d'environnement
        if 'LOMETA_ADDONS_DIR' in os.environ:
            return os.environ['LOMETA_ADDONS_DIR']
        
        # Mode développeur
        if os.path.exists('addons'):
            return 'addons'
        
        # Mode compilé
        import sys
        if getattr(sys, 'frozen', False):
            # Exécutable PyInstaller
            base_dir = os.path.dirname(sys.executable)
            internal_dir = os.path.join(base_dir, '_internal', 'addons')
            if os.path.exists(internal_dir):
                return internal_dir
            return os.path.join(base_dir, 'addons')
        
        # Fallback
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'addons')
    
    def _scan_modules(self):
        """Scanne le dossier des addons pour détecter les modules installés"""
        self.installed_modules = {}
        
        if not os.path.exists(self.addons_dir):
            print(f"⚠️ Dossier addons non trouvé : {self.addons_dir}")
            return
        
        for item in os.listdir(self.addons_dir):
            module_path = os.path.join(self.addons_dir, item)
            
            if not os.path.isdir(module_path):
                continue
            
            # Ignorer les dossiers cachés et les backups
            if item.startswith('_') or item.startswith('.'):
                continue
            
            # Chercher le manifest
            manifest_path = os.path.join(module_path, 'manifest.json')
            version = self._get_module_version(manifest_path)
            
            # Si pas de manifest, chercher dans __init__.py
            if version is None:
                version = self._get_version_from_init(module_path)
            
            # Si toujours pas de version, utiliser "0.0.0"
            if version is None:
                version = "0.0.0"
            
            self.installed_modules[item] = {
                'id': item,
                'name': self._get_module_name(module_path, item),
                'version': version,
                'path': module_path,
                'has_manifest': manifest_path and os.path.exists(manifest_path)
            }
            
            print(f"📦 Module détecté : {item} v{version}")
    
    def _get_module_version(self, manifest_path: str) -> Optional[str]:
        """Lit la version depuis le fichier manifest.json"""
        if not os.path.exists(manifest_path):
            return None
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', data.get('version', None))
        except (json.JSONDecodeError, IOError):
            return None
    
    def _get_version_from_init(self, module_path: str) -> Optional[str]:
        """Extrait la version depuis __init__.py"""
        init_path = os.path.join(module_path, '__init__.py')
        if not os.path.exists(init_path):
            return None
        
        try:
            with open(init_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Chercher __version__ = "x.y.z"
                import re
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
        except (IOError, UnicodeDecodeError):
            pass
        
        return None
    
    def _get_module_name(self, module_path: str, default: str) -> str:
        """Récupère le nom du module depuis le manifest ou le dossier"""
        manifest = os.path.join(module_path, 'manifest.json')
        if os.path.exists(manifest):
            try:
                with open(manifest, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('name', default)
            except:
                pass
        
        # Formater le nom : "automobiles" → "Automobiles"
        return default.replace('_', ' ').title()
    
    def get_installed_modules(self) -> Dict[str, Dict]:
        """Retourne la liste des modules installés"""
        return self.installed_modules
    
    def is_module_installed(self, module_id: str) -> bool:
        """Vérifie si un module est installé"""
        return module_id in self.installed_modules
    
    def get_module_version(self, module_id: str) -> Optional[str]:
        """Récupère la version d'un module installé"""
        if module_id in self.installed_modules:
            return self.installed_modules[module_id]['version']
        return None
    
    def filter_updates(self, server_modules: List[Dict]) -> List[Dict]:
        """
        Filtre les modules du serveur pour ne garder que ceux qui sont installés
        et qui ont une version plus récente
        """
        updates = []
        
        for server_module in server_modules:
            module_id = server_module.get('id')
            
            # Vérifier si le module est installé
            if not self.is_module_installed(module_id):
                print(f"⏭️ Module ignoré (non installé) : {module_id}")
                continue
            
            # Récupérer la version installée
            installed_version = self.get_module_version(module_id)
            server_version = server_module.get('version', '0.0.0')
            
            # Comparer les versions
            if self._is_newer_version(server_version, installed_version):
                # Ajouter la version actuelle pour l'affichage
                server_module['current_version'] = installed_version
                updates.append(server_module)
                print(f"📌 Mise à jour disponible : {module_id} ({installed_version} → {server_version})")
            else:
                print(f"✅ Module déjà à jour : {module_id} ({installed_version})")
        
        return updates
    
    def _is_newer_version(self, server_version: str, local_version: str) -> bool:
        """Compare deux versions sémantiques"""
        try:
            server_parts = [int(x) for x in server_version.split('.')]
            local_parts = [int(x) for x in local_version.split('.')]
            
            # Pad with zeros
            while len(server_parts) < 3:
                server_parts.append(0)
            while len(local_parts) < 3:
                local_parts.append(0)
            
            return server_parts > local_parts
        except (ValueError, AttributeError):
            # En cas d'erreur, considérer que c'est plus récent
            return server_version != local_version