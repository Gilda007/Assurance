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
from PySide6.QtWidgets import QFrame, QHBoxLayout, QMessageBox, QLabel, QPushButton, QProgressDialog

from typing import Dict, List

from update_dialog import UpdateDialog
from module_detector import ModuleDetector

try:
    from server.config import Config
except ImportError:
    class Config:
        UPDATE_SERVER = "http://localhost:8000/"
        
        @staticmethod
        def get_app_dir():
            if getattr(sys, 'frozen', False):
                return os.path.dirname(sys.executable)
            return os.path.dirname(os.path.abspath(__file__))
        
        @staticmethod
        def get_addons_dir():
            return os.path.join(Config.get_app_dir(), 'addons')


class UpdateChecker(QThread):
    """Thread de vérification des mises à jour - Version filtrée"""
    
    update_found = Signal(dict)  # Dictionnaire des mises à jour disponibles
    no_update = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, server_url: str, session_token: str = None):
        super().__init__()
        self.server_url = server_url.rstrip('/')
        self.session_token = session_token
        self.module_detector = ModuleDetector(Config.get_addons_dir())
    
    def run(self):
        """Vérifie les mises à jour via l'API"""
        try:
            from update_client import UpdateClient
            
            client = UpdateClient(session_token=self.session_token, server_url=self.server_url)
            status_code, modules = client.get_available_modules()
            
            if status_code != 200 or not modules:
                if status_code == 200:
                    self.no_update.emit()
                elif status_code == 401:
                    self.error_occurred.emit("Session expirée. Veuillez vous reconnecter.")
                elif status_code == 404:
                    self.error_occurred.emit("Serveur de mise à jour non accessible")
                else:
                    self.error_occurred.emit(f"Erreur: code {status_code}")
                return
            
            # ✅ FILTRAGE : Ne garder que les modules installés avec mise à jour
            updates = self.module_detector.filter_updates(modules)
            
            if updates:
                # Structurer en dictionnaire pour compatibilité
                updates_dict = {}
                for module in updates:
                    updates_dict[module['id']] = {
                        'type': 'module',
                        'id': module['id'],
                        'name': module['name'],
                        'current_version': module.get('current_version', '0.0.0'),
                        'new_version': module.get('version', '1.0.0'),
                        'download_url': module.get('download_url', ''),
                        'changelog': module.get('description', ''),
                        'size': module.get('size', 0),
                        'size_mb': module.get('size_mb', 0)
                    }
                self.update_found.emit(updates_dict)
            else:
                self.no_update.emit()
                
        except Exception as e:
            self.error_occurred.emit(str(e))


class UpdateManager(QObject):
    """Gestionnaire principal des mises à jour - Version corrigée"""
    
    def __init__(self, parent=None, session_token: str = None):
        super().__init__(parent)
        self.parent = parent
        self.session_token = session_token
        self.addons_dir = Config.get_addons_dir()
        self.updates_available = {}
        self.module_detector = ModuleDetector(self.addons_dir)
        
        os.makedirs(self.addons_dir, exist_ok=True)
    
    def check_updates_manual(self):
        """Vérifie manuellement les mises à jour"""
        self.checker = UpdateChecker(Config.UPDATE_SERVER, self.session_token)
        self.checker.update_found.connect(self.on_updates_found)
        self.checker.no_update.connect(self.on_no_update)
        self.checker.error_occurred.connect(self.on_update_error)
        self.checker.start()
    
    def check_updates_auto(self):
        """Vérifie automatiquement les mises à jour (silencieux)"""
        self.checker = UpdateChecker(Config.UPDATE_SERVER, self.session_token)
        self.checker.update_found.connect(self.on_auto_updates_found)
        self.checker.no_update.connect(lambda: None)
        self.checker.error_occurred.connect(self.on_update_error)
        self.checker.start()
    
    def on_updates_found(self, updates_dict):
        """Affiche le dialogue de mise à jour avec les modules filtrés"""
        self.updates_available = updates_dict
        
        if updates_dict:
            dialog = UpdateDialog(self.parent, updates_dict)
            if dialog.exec():
                self.install_updates(dialog.get_selected_updates())
        else:
            self.on_no_update()
    
    def on_auto_updates_found(self, updates_dict):
        """Notification silencieuse de mise à jour"""
        self.updates_available = updates_dict
        
        if updates_dict and self.parent:
            count = len(updates_dict)
            if hasattr(self.parent, 'show_status_message'):
                self.parent.show_status_message(f"🔔 {count} mise(s) à jour disponible(s)")
            self.show_notification_bubble(count)
    
    def on_no_update(self):
        """Aucune mise à jour trouvée pour les modules installés"""
        if self.parent:
            QMessageBox.information(
                self.parent, 
                "Mise à jour", 
                "✅ Tous vos modules sont à jour.\n\n"
                f"📦 {len(self.module_detector.get_installed_modules())} module(s) installé(s) - Aucune mise à jour disponible."
            )
    
    def on_update_error(self, error):
        """Erreur lors de la vérification"""
        if self.parent:
            QMessageBox.warning(
                self.parent, 
                "Erreur", 
                f"Impossible de vérifier les mises à jour:\n{error}\n\n"
                "Vérifiez votre connexion réseau."
            )
    
    def show_notification_bubble(self, count):
        """Affiche une bulle de notification"""
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("📢 Mises à jour disponibles")
        msg.setText(f"🔔 {count} module(s) peuvent être mis à jour")
        msg.setInformativeText("Cliquez sur 'Aide' → 'Vérifier les mises à jour' pour les installer")
        msg.setStandardButtons(QMessageBox.Ok)
        QTimer.singleShot(5000, msg.close)
        msg.open()
    
    def install_updates(self, selected_updates):
        """Installe les mises à jour sélectionnées"""
        from update_manager import UpdateInstaller
        
        self.installer = UpdateInstaller(self.addons_dir, self.session_token)
        self.installer.finished.connect(self.on_install_finished)
        
        # Boîte de progression
        self.progress_dialog = QProgressDialog("Préparation...", "Annuler", 0, 100, self.parent)
        self.progress_dialog.setWindowTitle("Mise à jour")
        self.progress_dialog.setMinimumWidth(400)
        self.progress_dialog.setStyleSheet("""
            QProgressDialog {
                background: white;
                border-radius: 12px;
            }
            QProgressBar {
                border: none;
                background: #e2e8f0;
                border-radius: 6px;
                height: 8px;
            }
            QProgressBar::chunk {
                background: #3b82f6;
                border-radius: 6px;
            }
        """)
        
        self.installer.progress.connect(self.progress_dialog.setValue)
        self.installer.status.connect(self.progress_dialog.setLabelText)
        self.progress_dialog.canceled.connect(self.installer.terminate)
        
        for update_name in selected_updates:
            if update_name in self.updates_available:
                self.installer.add_update(self.updates_available[update_name])
        
        self.installer.start()
        self.progress_dialog.show()
    
    def on_install_finished(self, success, message):
        """Installation terminée"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        if success:
            QMessageBox.information(
                self.parent,
                "✅ Mise à jour réussie",
                f"{message}\n\nLes modifications prendront effet après le redémarrage."
            )
        else:
            QMessageBox.warning(self.parent, "❌ Erreur", message)
    
    def get_installed_modules_info(self) -> Dict:
        """Retourne les informations des modules installés"""
        return self.module_detector.get_installed_modules()

class UpdateInstaller(QThread):
    """Thread d'installation des mises à jour - Compatible update_server.py"""
    
    progress = Signal(int, int)
    status = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, addons_dir, session_token: str = None, temp_dir=None):
        super().__init__()
        self.addons_dir = addons_dir
        self.session_token = session_token
        self.temp_dir = temp_dir or tempfile.mkdtemp()
        self.updates_queue = []
    
    def add_update(self, update_info):
        """Ajoute une mise à jour à installer"""
        self.updates_queue.append(update_info)
    
    def run(self):
        """Installe toutes les mises à jour en file d'attente"""
        from update_client import UpdateClient
        
        client = UpdateClient(session_token=self.session_token, server_url=Config.UPDATE_SERVER)
        success_count = 0
        error_count = 0
        
        for i, update in enumerate(self.updates_queue):
            self.current_update = update
            self.status.emit(f"Téléchargement de {update['name']}...")
            
            download_path = self.download_update(client, update)
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
    
    def download_update(self, client, update):
        """Télécharge une mise à jour via UpdateClient"""
        try:
            import requests
            
            download_url = f"{Config.UPDATE_SERVER}{update['download_url']}"
            if self.session_token:
                separator = '&' if '?' in download_url else '?'
                download_url += f"{separator}auth={self.session_token}"
            
            file_ext = '.zip'
            temp_file = os.path.join(self.temp_dir, f"{update['name']}{file_ext}")
            
            response = requests.get(download_url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            self.progress.emit(percent, 100)
            
            return temp_file
            
        except Exception as e:
            self.status.emit(f"Erreur téléchargement: {str(e)}")
            return None
    
    def install_update(self, update, download_path):
        """Installe une mise à jour téléchargée"""
        module_path = os.path.join(self.addons_dir, update['id'] if 'id' in update else update['name'])
        backup_path = os.path.join(self.addons_dir, f"_{update['name']}_backup")
        
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
                # Chercher si le dossier a un nom différent
                extracted_items = os.listdir(self.addons_dir)
                for item in extracted_items:
                    if item.endswith(update['name']) or update['name'].startswith(item):
                        module_path = os.path.join(self.addons_dir, item)
                        break
            
            # Supprimer la sauvegarde
            shutil.rmtree(backup_path, ignore_errors=True)
            
            return True
            
        except Exception as e:
            # Restaurer la sauvegarde en cas d'erreur
            if os.path.exists(backup_path):
                if os.path.exists(module_path):
                    shutil.rmtree(module_path)
                shutil.move(backup_path, module_path)
            return False   


    def report_progress(self, block, block_size, total_size):
        """Rapporte la progression du téléchargement"""
        if total_size > 0:
            downloaded = block * block_size
            percent = int((downloaded / total_size) * 100)
            self.progress.emit(percent, 100)
    
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
    