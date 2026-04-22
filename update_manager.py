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
from PySide6.QtWidgets import QFrame, QHBoxLayout, QMessageBox, QLabel, QPushButton

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
        
    # Dans UpdateChecker.run()
    def run(self):
        """Vérifie les mises à jour"""
        try:
            print("🚀 UpdateChecker.run() démarré")  # ← Debug
            url = f"{self.server_url}/check_updates"
            print(f"   URL: {url}")  # ← Debug
            
            req = urllib.request.Request(url)
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                print(f"   Réponse serveur reçue")  # ← Debug
                
                updates = self.check_available_updates(data)
                print(f"   Mises à jour trouvées: {len(updates)}")  # ← Debug
                
                if updates:
                    print(f"   ✅ Émission du signal update_found")  # ← Debug
                    self.update_found.emit(updates)
                else:
                    print(f"   ❌ Aucune mise à jour, émission de no_update")  # ← Debug
                    self.no_update.emit()
        except Exception as e:
            print(f"   ❌ Erreur: {e}")  # ← Debug
            self.error_occurred.emit(str(e))

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
        self.version_manager = VersionManager(self.addons_dir)
        
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

        print(f"📁 UpdateManager - addons_dir : {self.addons_dir}")
        
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
        print("🔄 Vérification AUTO des mises à jour...")  # ← Debug
        print(f"   Serveur: {Config.UPDATE_SERVER}")
        print(f"   Dossier addons: {self.addons_dir}")
        
        checker = UpdateChecker(Config.UPDATE_SERVER, self.addons_dir)
        checker.update_found.connect(self.on_auto_updates_found)
        checker.no_update.connect(self.on_no_update)
        checker.error_occurred.connect(self.on_update_error)
        checker.start()
    
    def on_updates_found(self, updates):
        """Affiche le dialogue de mise à jour"""
        self.updates_available = updates
        dialog = UpdateDialog(self.parent, updates)
        if dialog.exec():
            self.install_updates(dialog.get_selected_updates())
    
    def on_auto_updates_found(self, updates):
        """Notification silencieuse de mise à jour"""
        print(f"📢 Mises à jour trouvées (auto): {list(updates.keys())}")  # ← Debug
        
        self.updates_available = updates
        if self.parent:
            count = len(updates)
            message = f"🔔 {count} mise(s) à jour disponible(s)"
            
            # Afficher une notification dans la barre d'état
            if hasattr(self.parent, 'show_status_message'):
                self.parent.show_status_message(message)
            else:
                print(message)
            
            # ⚠️ OPTIONNEL : Afficher une boîte de dialogue non intrusive
            self.show_notification_bubble(count)
    
    def on_no_update(self):
        """Aucune mise à jour trouvée"""
        if self.parent:
            QMessageBox.information(self.parent, "Mise à jour", "Votre application est à jour")
    
    def show_notification_bubble(self, count):
        """Affiche une bulle de notification"""
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtCore import QTimer
        
        # Notification qui disparaît automatiquement
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("📢 Mises à jour disponibles")
        msg.setText(f"{count} module(s) peuvent être mis à jour")
        msg.setInformativeText("Cliquez sur 'Aide' → 'Vérifier les mises à jour' pour les installer")
        msg.setStandardButtons(QMessageBox.Ok)
        
        # Fermeture automatique après 5 secondes
        QTimer.singleShot(5000, msg.close)
        msg.open()

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
        """Installation terminée (pour les mises à jour)"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        if success:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("✅ Mise à jour réussie")
            msg_box.setText(f"{message}\n\nLes modifications prendront effet après le redémarrage.")
            msg_box.setInformativeText("Voulez-vous redémarrer l'application maintenant ?")
            
            restart_btn = msg_box.addButton("🔄 Redémarrer maintenant", QMessageBox.AcceptRole)
            later_btn = msg_box.addButton("⏰ Redémarrer plus tard", QMessageBox.RejectRole)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    border-radius: 16px;
                }
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            
            result = msg_box.exec()
            
            if msg_box.clickedButton() == restart_btn:
                self.restart_application()
            else:
                self.refresh_data()
                self.show_restart_notification()
        else:
            QMessageBox.warning(self, "❌ Erreur", message)

    def show_restart_notification(self):
        """Affiche une notification toast"""
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        from PySide6.QtCore import QPropertyAnimation
        
        # Créer une notification flottante
        notification = QFrame(self)
        notification.setStyleSheet("""
            QFrame {
                background: #1e293b;
                border-radius: 12px;
                color: white;
            }
        """)
        notification.setFixedHeight(50)
        
        layout = QHBoxLayout(notification)
        layout.setContentsMargins(15, 0, 15, 0)
        
        icon = QLabel("🔄")
        icon.setStyleSheet("font-size: 16px;")
        
        text = QLabel("Module installé. Redémarrez l'application pour appliquer les changements.")
        text.setStyleSheet("color: white; font-size: 12px;")
        
        restart_btn = QPushButton("Redémarrer")
        restart_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        restart_btn.clicked.connect(self.restart_application)
        
        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #94a3b8;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                color: white;
            }
        """)
        close_btn.clicked.connect(notification.deleteLater)
        
        layout.addWidget(icon)
        layout.addWidget(text, 1)
        layout.addWidget(restart_btn)
        layout.addWidget(close_btn)
        
        # Positionner en bas à droite
        notification.adjustSize()
        notification.move(
            self.width() - notification.width() - 20,
            self.height() - notification.height() - 20
        )
        
        # Effet d'apparition/disparition
        opacity_effect = QGraphicsOpacityEffect()
        notification.setGraphicsEffect(opacity_effect)
        
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()
        
        notification.show()
        
        # Auto-disparition après 8 secondes
        QTimer.singleShot(8000, notification.deleteLater)

    def restart_application(self):
        """Redémarre l'application"""
        import sys
        import subprocess
        import os
        from PySide6.QtWidgets import QApplication
        
        try:
            # Obtenir le chemin de l'application
            if getattr(sys, 'frozen', False):
                # Mode compilé (exécutable)
                app_path = sys.executable
                args = []
            else:
                # Mode développement (script Python)
                # Chercher main.py dans différents emplacements
                possible_paths = [
                    sys.argv[0],  # Chemin actuel
                    os.path.join(os.getcwd(), "main.py"),
                    os.path.join(os.path.dirname(__file__), "..", "main.py"),
                    os.path.join(os.path.dirname(sys.argv[0]), "main.py"),
                ]
                
                app_path = None
                for path in possible_paths:
                    if os.path.exists(path) and path.endswith('.py'):
                        app_path = path
                        break
                
                if not app_path:
                    # Dernier recours : utiliser python avec le script actuel
                    app_path = sys.executable
                    args = [sys.argv[0]]
                else:
                    args = []
            
            # Construire la commande
            cmd = [app_path] + args + sys.argv[1:]
            
            print(f"🔄 Redémarrage avec : {cmd}")  # Debug
            
            # Lancer la nouvelle instance
            if sys.platform == "win32":
                # Windows
                subprocess.Popen(cmd, shell=True)
            else:
                # Linux/Mac
                subprocess.Popen(cmd)
            
            # Fermer l'instance actuelle
            QApplication.quit()
            
        except Exception as e:
            print(f"Erreur redémarrage: {e}")
            QMessageBox.warning(
                self, 
                "Erreur", 
                f"Impossible de redémarrer automatiquement : {str(e)}\n\n"
                "Veuillez redémarrer l'application manuellement."
            )