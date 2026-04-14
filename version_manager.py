# version_manager.py
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Optional
from config import Config

class VersionManager:
    """Gestionnaire du fichier versions.json"""
    
    def __init__(self, addons_dir=None):
        # Si addons_dir n'est pas fourni, utiliser Config
        if addons_dir is None:
            addons_dir = Config.get_addons_dir()
        
        self.addons_dir = addons_dir
        self.version_file = os.path.join(addons_dir, 'versions.json')
        self.data = self.load()
        
        print(f"📁 VersionManager - addons_dir : {self.addons_dir}")
    
    def load(self) -> dict:
        """Charge le fichier versions.json"""
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur chargement versions.json: {e}")
                return self.get_default_structure()
        return self.get_default_structure()
    
    def save(self):
        """Sauvegarde le fichier versions.json"""
        try:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Erreur sauvegarde versions.json: {e}")
            return False
    
    def get_module_manifest(self, module_name):
        """Lit le manifest.json d'un module installé localement"""
        manifest_path = os.path.join(self.addons_dir, module_name, 'manifest.json')
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def update_module_manifest(self, module_name, new_version, changelog=""):
        """Met à jour le manifest.json d'un module après mise à jour"""
        manifest_path = os.path.join(self.addons_dir, module_name, 'manifest.json')
        
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        else:
            manifest = {
                "name": module_name,
                "version": "1.0.0",
                "author": "Unknown",
                "category": "General"
            }
        
        # Mettre à jour la version
        manifest['version'] = new_version
        if changelog:
            manifest['changelog'] = changelog
        manifest['last_updated'] = datetime.now().isoformat()
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        # Mettre à jour le versions.json global
        self.update_module(module_name, new_version, changelog)

    def get_local_modules_versions(self):
        """Retourne un dictionnaire des versions locales de tous les modules"""
        versions = {}
        for module_name in os.listdir(self.addons_dir):
            module_path = os.path.join(self.addons_dir, module_name)
            manifest_path = os.path.join(module_path, 'manifest.json')
            
            if os.path.isdir(module_path) and os.path.exists(manifest_path):
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                    versions[module_name] = manifest.get('version', '0.0.0')
        
        return versions

    def get_default_structure(self) -> dict:
        """Retourne la structure par défaut"""
        return {
            "app_version": "1.0.0",
            "last_check": None,
            "modules": {},
            "settings": {
                "auto_update": True,
                "check_interval": 3600,
                "notify_before_update": True,
                "backup_before_update": True
            },
            "history": []
        }
    
    def get_app_version(self) -> str:
        """Retourne la version de l'application"""
        return self.data.get('app_version', '1.0.0')
    
    def set_app_version(self, version: str):
        """Met à jour la version de l'application"""
        self.data['app_version'] = version
        self.save()
    
    def get_module_version(self, module_name: str) -> Optional[str]:
        """Retourne la version d'un module"""
        module = self.data['modules'].get(module_name)
        return module.get('version') if module else None
    
    def get_all_modules(self) -> dict:
        """Retourne tous les modules avec leurs infos"""
        return self.data.get('modules', {})
    
    def update_module(self, module_name: str, version: str, changelog: str = "", size: int = 0):
        """Met à jour les informations d'un module"""
        now = datetime.now().isoformat()
        
        if module_name not in self.data['modules']:
            # Nouvelle installation
            self.data['modules'][module_name] = {
                "version": version,
                "installed_date": now,
                "last_update": now,
                "size": size,
                "checksum": "",
                "enabled": True,
                "changelog": changelog
            }
            self.add_to_history("install", module_name, "0.0.0", version, "success")
        else:
            # Mise à jour
            old_version = self.data['modules'][module_name]['version']
            self.data['modules'][module_name]['version'] = version
            self.data['modules'][module_name]['last_update'] = now
            self.data['modules'][module_name]['changelog'] = changelog
            if size > 0:
                self.data['modules'][module_name]['size'] = size
            self.add_to_history("update", module_name, old_version, version, "success")
        
        self.save()
    
    def set_module_checksum(self, module_name: str, checksum: str):
        """Définit le checksum d'un module"""
        if module_name in self.data['modules']:
            self.data['modules'][module_name]['checksum'] = checksum
            self.save()
    
    def enable_module(self, module_name: str, enabled: bool):
        """Active ou désactive un module"""
        if module_name in self.data['modules']:
            self.data['modules'][module_name]['enabled'] = enabled
            self.save()
    
    def add_to_history(self, action: str, module: str, old_version: str, new_version: str, status: str):
        """Ajoute une entrée dans l'historique"""
        self.data['history'].insert(0, {  # Insert au début
            "date": datetime.now().isoformat(),
            "action": action,
            "module": module,
            "old_version": old_version,
            "new_version": new_version,
            "status": status
        })
        
        # Garder seulement les 50 derniers événements
        if len(self.data['history']) > 50:
            self.data['history'] = self.data['history'][:50]
        
        self.save()
    
    def update_last_check(self):
        """Met à jour la date du dernier check"""
        self.data['last_check'] = datetime.now().isoformat()
        self.save()
    
    def get_setting(self, key: str, default=None):
        """Récupère un paramètre"""
        return self.data.get('settings', {}).get(key, default)
    
    def set_setting(self, key: str, value):
        """Définit un paramètre"""
        if 'settings' not in self.data:
            self.data['settings'] = {}
        self.data['settings'][key] = value
        self.save()
    
    def calculate_checksum(self, file_path: str) -> str:
        """Calcule le checksum SHA256 d'un fichier"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def verify_module_integrity(self, module_name: str, file_path: str) -> bool:
        """Vérifie l'intégrité d'un module"""
        if module_name not in self.data['modules']:
            return False
        
        expected_checksum = self.data['modules'][module_name].get('checksum')
        if not expected_checksum:
            return True  # Pas de checksum à vérifier
        
        actual_checksum = self.calculate_checksum(file_path)
        return actual_checksum == expected_checksum
    
    def get_update_history(self, limit: int = 10) -> list:
        """Retourne l'historique des mises à jour"""
        return self.data.get('history', [])[:limit]
    
    def is_module_installed(self, module_name: str) -> bool:
        """Vérifie si un module est installé"""
        return module_name in self.data['modules']
    
    def get_module_info(self, module_name: str) -> Optional[dict]:
        """Retourne les informations d'un module"""
        return self.data['modules'].get(module_name)
    
    def get_enabled_modules(self) -> list:
        """Retourne la liste des modules activés"""
        return [
            name for name, info in self.data['modules'].items()
            if info.get('enabled', True)
        ]
    
    def needs_update(self, module_name: str, server_version: str) -> bool:
        """Vérifie si une mise à jour est nécessaire"""
        current_version = self.get_module_version(module_name)
        if not current_version:
            return True
        
        # Comparer les versions
        current_parts = [int(x) for x in current_version.split('.')]
        server_parts = [int(x) for x in server_version.split('.')]
        
        # Compléter avec des zéros
        while len(current_parts) < 3:
            current_parts.append(0)
        while len(server_parts) < 3:
            server_parts.append(0)
        
        return server_parts > current_parts
    
    def set_module_dependencies(self, module_name, dependencies):
        """Sauvegarde les dépendances d'un module"""
        if module_name in self.data['modules']:
            self.data['modules'][module_name]['dependencies_installed'] = dependencies
            self.data['modules'][module_name]['dependencies_date'] = datetime.now().isoformat()
            self.save()
    
    def get_module_dependencies(self, module_name):
        """Récupère les dépendances d'un module"""
        module = self.data['modules'].get(module_name, {})
        return module.get('dependencies_installed', [])
    
    def check_module_dependencies(self, module_name):
        """Vérifie si les dépendances d'un module sont toujours installées"""
        import subprocess
        import sys
        
        module = self.data['modules'].get(module_name, {})
        deps = module.get('dependencies_installed', [])
        
        if not deps:
            return True, "Aucune dépendance enregistrée"
        
        # Vérifier les packages installés
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=json'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            installed = {pkg['name'].lower() for pkg in json.loads(result.stdout)}
            missing = []
            
            for dep in deps:
                dep_name = dep.get('name', '').lower()
                if dep_name and dep_name not in installed:
                    missing.append(dep_name)
            
            if missing:
                return False, f"Dépendances manquantes: {', '.join(missing)}"
            return True, "Toutes les dépendances sont installées"
        
        return False, "Impossible de vérifier les dépendances"
