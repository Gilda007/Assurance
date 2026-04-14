# update_manager.py
import os
import sys
import json
import shutil
import tempfile
import urllib.request
import urllib.error
import zipfile
from datetime import datetime
from PySide6.QtCore import QThread, Signal, QObject, QTimer
from PySide6.QtWidgets import QMessageBox

# Import du dialogue de mise à jour
from update_dialog import UpdateDialog

# Import des modules existants
try:
    from config import Config
except ImportError:
    class Config:
        UPDATE_SERVER = "http://192.168.100.17:5000/api"
        
        @staticmethod
        def get_app_dir():
            if getattr(sys, 'frozen', False):
                return os.path.dirname(sys.executable)
            return os.path.dirname(os.path.abspath(__file__))
        
        @staticmethod
        def get_modules_dir():
            return os.path.join(Config.get_app_dir(), 'addons')

# Import du VersionManager existant
from version_manager import VersionManager


class UpdateChecker(QThread):
    """Thread de vérification des mises à jour"""
    
    update_found = Signal(dict)
    no_update = Signal()
    error_occurred = Signal(str)
    progress = Signal(int, int)
    
    def __init__(self, server_url, addons_dir):
        super().__init__()
        self.server_url = server_url
        self.addons_dir = addons_dir
        self.version_manager = VersionManager(addons_dir)
        self.current_version = self.version_manager.get_app_version()
        
    def run(self):
        """Vérifie les mises à jour"""
        try:
            url = f"{self.server_url}/check_updates"
            req = urllib.request.Request(url)
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                updates = self.check_available_updates(data)
                
                # Mettre à jour la date du dernier check
                self.version_manager.update_last_check()
                
                if updates:
                    self.update_found.emit(updates)
                else:
                    self.no_update.emit()
                    
        except urllib.error.URLError as e:
            self.error_occurred.emit(f"Impossible de contacter le serveur: {e.reason}")
        except Exception as e:
            self.error_occurred.emit(f"Erreur: {str(e)}")
    
    def check_available_updates(self, server_data):
        """Compare les versions locales avec le serveur"""
        updates = {}
        
        # Vérifier la version de l'application
        if self.is_newer_version(server_data.get('app_version', '0'), self.current_version):
            updates['app'] = {
                'type': 'app',
                'name': 'Application principale',
                'current_version': self.current_version,
                'new_version': server_data['app_version'],
                'download_url': server_data.get('app_download_url'),
                'changelog': server_data.get('app_changelog', ''),
                'size': server_data.get('app_size', 0)
            }
        
        # Vérifier les modules
        local_versions = self.version_manager.get_all_modules()
        
        for module_name, server_info in server_data.get('modules', {}).items():
            local_version = local_versions.get(module_name, {}).get('version', '0.0.0')
            
            if self.is_newer_version(server_info.get('version', '0'), local_version):
                updates[module_name] = {
                    'type': 'module',
                    'name': module_name,
                    'current_version': local_version,
                    'new_version': server_info['version'],
                    'download_url': server_info['download_url'],
                    'changelog': server_info.get('changelog', ''),
                    'size': server_info.get('size', 0)
                }
        
        return updates
    
    def is_newer_version(self, server_version, local_version):
        """Compare deux versions"""
        try:
            server_parts = [int(x) for x in server_version.split('.')]
            local_parts = [int(x) for x in local_version.split('.')]
            
            while len(server_parts) < 3:
                server_parts.append(0)
            while len(local_parts) < 3:
                local_parts.append(0)
            
            return server_parts > local_parts
        except:
            return False


class UpdateInstaller(QThread):
    """Thread d'installation des mises à jour"""
    
    progress = Signal(int, int)
    status = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, addons_dir, temp_dir=None):
        super().__init__()
        self.addons_dir = addons_dir
        self.temp_dir = temp_dir or tempfile.mkdtemp()
        self.updates_queue = []
        self.version_manager = VersionManager(addons_dir)
        
    def add_update(self, update_info):
        """Ajoute une mise à jour à installer"""
        self.updates_queue.append(update_info)
    
    def run(self):
        """Installe toutes les mises à jour en file d'attente"""
        success_count = 0
        error_count = 0
        
        for i, update in enumerate(self.updates_queue):
            self.current_update = update
            self.status.emit(f"Téléchargement de {update['name']}...")
            
            download_path = self.download_update(update)
            if not download_path:
                error_count += 1
                continue
            
            self.progress.emit(i + 1, len(self.updates_queue))
            
            self.status.emit(f"Installation de {update['name']}...")
            success = self.install_update(update, download_path)
            
            if success:
                success_count += 1
            else:
                error_count += 1
        
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        if error_count == 0:
            self.finished.emit(True, f"{success_count} mise(s) à jour installée(s) avec succès")
        else:
            self.finished.emit(False, f"{success_count} réussie(s), {error_count} erreur(s)")
    
    def download_update(self, update):
        """Télécharge une mise à jour"""
        try:
            file_ext = '.zip'
            temp_file = os.path.join(self.temp_dir, f"{update['name']}{file_ext}")
            
            urllib.request.urlretrieve(
                update['download_url'],
                temp_file,
                self.report_progress
            )
            
            return temp_file
            
        except Exception as e:
            self.status.emit(f"Erreur téléchargement: {str(e)}")
            return None
    
    def report_progress(self, block, block_size, total_size):
        """Rapporte la progression du téléchargement"""
        if total_size > 0:
            downloaded = block * block_size
            percent = int((downloaded / total_size) * 100)
            self.progress.emit(percent, 100)
    
    def install_update(self, update, download_path):
        """Installe une mise à jour téléchargée"""
        try:
            if update['type'] == 'module':
                return self.install_module_update(update, download_path)
            elif update['type'] == 'app':
                return self.install_app_update(update, download_path)
            return False
        except Exception as e:
            self.status.emit(f"Erreur installation: {str(e)}")
            return False
    
    def install_module_update(self, update, download_path):
        """Installe une mise à jour de module"""
        module_path = os.path.join(self.addons_dir, update['name'])
        backup_path = os.path.join(self.addons_dir, f"{update['name']}_backup")
        
        try:
            # Sauvegarder l'ancienne version
            if os.path.exists(module_path):
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                shutil.move(module_path, backup_path)
            
            # Extraire la nouvelle version
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(self.addons_dir)
            
            # Vérifier que le module a bien été extrait
            if not os.path.exists(module_path):
                if os.path.exists(backup_path):
                    shutil.move(backup_path, module_path)
                raise Exception("Extraction échouée")
            
            # Supprimer la sauvegarde
            shutil.rmtree(backup_path, ignore_errors=True)
            
            # Mettre à jour les versions dans VersionManager
            self.version_manager.update_module(
                update['name'],
                update['new_version'],
                update.get('changelog', ''),
                update.get('size', 0)
            )
            
            return True
            
        except Exception as e:
            # Restaurer la sauvegarde en cas d'erreur
            if os.path.exists(backup_path):
                if os.path.exists(module_path):
                    shutil.rmtree(module_path)
                shutil.move(backup_path, module_path)
            self.version_manager.add_to_history(
                "update_failed",
                update['name'],
                update['current_version'],
                update['new_version'],
                str(e)
            )
            return False
    
    def install_app_update(self, update, download_path):
        """Installe une mise à jour de l'application"""
        app_dir = os.path.dirname(self.addons_dir)
        
        # Script de mise à jour pour Windows
        updater_script = os.path.join(self.temp_dir, 'update_app.bat')
        
        with open(updater_script, 'w') as f:
            f.write(f"""@echo off
timeout /t 2 /nobreak > nul
echo Mise à jour de l'application...
move /Y "{download_path}" "{app_dir}\\update.zip"
echo Mise à jour terminée. Veuillez redémarrer l'application.
timeout /t 3 /nobreak > nul
""")
        
        # Lancer le script
        import subprocess
        subprocess.Popen([updater_script], shell=True)
        
        # Mettre à jour la version dans VersionManager
        self.version_manager.set_app_version(update['new_version'])
        
        # Quitter l'application
        QTimer.singleShot(1000, lambda: sys.exit(0))
        
        return True


class UpdateManager(QObject):
    """Gestionnaire principal des mises à jour"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.addons_dir = Config.get_addons_dir()
        self.updates_available = {}
        self.version_manager = VersionManager(self.addons_dir)
        
        # Créer le dossier addons s'il n'existe pas
        os.makedirs(self.addons_dir, exist_ok=True)
        
    def check_updates_manual(self):
        """Vérifie manuellement les mises à jour"""
        self.checker = UpdateChecker(Config.UPDATE_SERVER, self.addons_dir)
        self.checker.update_found.connect(self.on_updates_found)
        self.checker.no_update.connect(self.on_no_update)
        self.checker.error_occurred.connect(self.on_update_error)
        self.checker.start()
    
    def check_updates_auto(self):
        """Vérifie automatiquement les mises à jour (silencieux)"""
        checker = UpdateChecker(Config.UPDATE_SERVER, self.addons_dir)
        checker.update_found.connect(self.on_auto_updates_found)
        checker.start()
    
    def on_updates_found(self, updates):
        """Affiche le dialogue de mise à jour"""
        self.updates_available = updates
        dialog = UpdateDialog(self.parent, updates)
        if dialog.exec():
            self.install_updates(dialog.get_selected_updates())
    
    def on_auto_updates_found(self, updates):
        """Notification silencieuse de mise à jour"""
        self.updates_available = updates
        if self.parent:
            count = len(updates)
            if hasattr(self.parent, 'show_status_message'):
                self.parent.show_status_message(f"{count} mise(s) à jour disponible(s)")
    
    def on_no_update(self):
        """Aucune mise à jour trouvée"""
        if self.parent:
            QMessageBox.information(self.parent, "Mise à jour", "Votre application est à jour")
    
    def on_update_error(self, error):
        """Erreur lors de la vérification"""
        if self.parent:
            QMessageBox.warning(self.parent, "Erreur", f"Impossible de vérifier les mises à jour:\n{error}")
    
    def install_updates(self, selected_updates):
        """Installe les mises à jour sélectionnées"""
        self.installer = UpdateInstaller(self.addons_dir)
        self.installer.finished.connect(self.on_install_finished)
        
        for update_name in selected_updates:
            if update_name in self.updates_available:
                self.installer.add_update(self.updates_available[update_name])
        
        self.installer.start()
    
    def on_install_finished(self, success, message):
        """Installation terminée"""
        if success:
            QMessageBox.information(self.parent, "Mise à jour", message + "\n\nRedémarrez l'application pour appliquer les changements.")
        else:
            QMessageBox.warning(self.parent, "Erreur", message)