# update_widget.py
"""
Widget pour afficher et télécharger les modules disponibles
"""

import os
import zipfile
import shutil
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QProgressBar, QScrollArea,
    QFrame, QMessageBox, QWidget
)
from PySide6.QtCore import Qt, Signal, QThread
from update_client import UpdateClient


class DownloadInstallThread(QThread):
    """Thread pour télécharger et installer un module"""
    progress = Signal(int, int)  # current, total
    status = Signal(str)          # message
    finished = Signal(bool, str)  # success, module_name
    
    def __init__(self, client, module, install_paths):
        super().__init__()
        self.client = client
        self.module = module
        self.install_paths = install_paths
        self.temp_dir = Path("temp_downloads")
        self.temp_dir.mkdir(exist_ok=True)
    
    def run(self):
        zip_path = self.temp_dir / self.module['filename']
        
        # Téléchargement
        self.status.emit(f"📥 Téléchargement de {self.module['name']}...")
        
        def progress_callback(current, total):
            percent = int(current * 100 / total)
            self.progress.emit(percent, 100)
        
        success = self.client.download_module(self.module, str(zip_path), progress_callback)
        
        if not success:
            self.finished.emit(False, self.module['name'])
            return
        
        # Installation
        self.status.emit(f"📦 Installation de {self.module['name']}...")
        self.progress.emit(0, 0)  # Mode indéterminé
        
        try:
            # Extraire le zip
            extract_dir = self.temp_dir / f"extract_{self.module['id']}"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)
            
            # Trouver le contenu (si un seul dossier, l'utiliser)
            items = list(extract_dir.iterdir())
            if len(items) == 1 and items[0].is_dir():
                source_dir = items[0]
            else:
                source_dir = extract_dir
            
            # Installer dans chaque chemin
            for install_path in self.install_paths:
                target_dir = Path(install_path) / self.module['id']
                
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                
                shutil.copytree(source_dir, target_dir)
                self.status.emit(f"📁 Installé dans {target_dir}")
            
            # Nettoyer
            shutil.rmtree(extract_dir)
            os.remove(zip_path)
            
            self.finished.emit(True, self.module['name'])
            
        except Exception as e:
            self.status.emit(f"❌ Erreur: {str(e)}")
            self.finished.emit(False, self.module['name'])


class UpdateWidget(QDialog):
    """Widget de mise à jour"""
    
    def __init__(self, modules, parent=None):
        super().__init__(parent)
        self.modules = modules
        self.client = UpdateClient()
        self.threads = []
        
        # Chemins d'installation
        self.install_paths = [
            "addons",
            "_internal/addons",
            "dist/LOMETA/addons",
            "dist/LOMETA/_internal/addons"
        ]
        # Garder seulement les chemins valides
        self.install_paths = [p for p in self.install_paths if os.path.exists(p) or os.path.exists(os.path.dirname(p))]
        if not self.install_paths:
            self.install_paths = ["addons"]
            os.makedirs("addons", exist_ok=True)
        
        self.setWindowTitle("Mise à jour des modules - LOMETA")
        self.setMinimumSize(550, 450)
        self.setModal(True)
        
        self.setup_ui()
        self.load_modules()
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Message principal
        msg = QLabel("🎉 Des mises à jour sont disponibles !\nTéléchargez les modules que vous souhaitez installer :")
        msg.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 12px;
        """)
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        layout.addWidget(msg)
        
        # Zone de scroll pour les modules
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 10px;")
        
        self.modules_widget = QWidget()
        self.modules_layout = QVBoxLayout(self.modules_widget)
        self.modules_layout.setSpacing(10)
        
        scroll.setWidget(self.modules_widget)
        layout.addWidget(scroll)
        
        # Zone de progression
        self.progress_frame = QFrame()
        self.progress_frame.setVisible(False)
        self.progress_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        prog_layout = QVBoxLayout(self.progress_frame)
        
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #64748b; font-size: 12px;")
        prog_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 5px;
            }
        """)
        prog_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.progress_frame)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.download_btn = QPushButton("📥 Télécharger la sélection")
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 25px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #059669; }
            QPushButton:disabled { background-color: #94a3b8; }
        """)
        self.download_btn.clicked.connect(self.download_selected)
        
        self.close_btn = QPushButton("Fermer")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 25px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #dc2626; }
        """)
        self.close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)
        
        self.checkboxes = []
        self.download_btn.setEnabled(False)
    
    def load_modules(self):
        """Charge la liste des modules disponibles"""
        for module in self.modules:
            # Checkbox
            cb = QCheckBox()
            cb.setChecked(True)
            cb.stateChanged.connect(self.update_button_state)
            self.checkboxes.append((cb, module))
            
            # Widget du module
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background: #f8fafc;
                    border-radius: 10px;
                    padding: 12px;
                }
                QFrame:hover { background: #f1f5f9; }
            """)
            
            frame_layout = QHBoxLayout(frame)
            frame_layout.setSpacing(12)
            frame_layout.addWidget(cb)
            
            info = QVBoxLayout()
            name = QLabel(f"<b>{module['name']}</b>")
            name.setStyleSheet("color: #1e293b;")
            info.addWidget(name)
            
            details = QLabel(f"📄 {module['filename']}  •  💾 {module['size_mb']} MB")
            details.setStyleSheet("color: #64748b; font-size: 11px;")
            info.addWidget(details)
            
            frame_layout.addLayout(info)
            frame_layout.addStretch()
            
            self.modules_layout.addWidget(frame)
        
        self.modules_layout.addStretch()
        self.update_button_state()
    
    def update_button_state(self):
        """Met à jour l'état du bouton"""
        has_selection = any(cb.isChecked() for cb, _ in self.checkboxes)
        self.download_btn.setEnabled(has_selection)
    
    def download_selected(self):
        """Télécharge et installe les modules sélectionnés"""
        selected = [(cb, m) for cb, m in self.checkboxes if cb.isChecked()]
        
        if not selected:
            return
        
        # Désactiver l'interface
        self.download_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        self.progress_frame.setVisible(True)
        
        # Démarrer l'installation séquentielle
        self.selected_modules = selected
        self.current_index = 0
        self.install_next()
    
    def install_next(self):
        """Installe le module suivant"""
        if self.current_index >= len(self.selected_modules):
            self.on_all_complete()
            return
        
        cb, module = self.selected_modules[self.current_index]
        self.current_module = module
        
        thread = DownloadInstallThread(self.client, module, self.install_paths)
        thread.progress.connect(self.on_progress)
        thread.status.connect(self.on_status)
        thread.finished.connect(self.on_module_finished)
        thread.start()
        self.threads.append(thread)
    
    def on_progress(self, current, total):
        """Met à jour la progression"""
        if total > 0:
            self.progress_bar.setValue(current)
            self.progress_bar.setRange(0, 100)
        else:
            self.progress_bar.setRange(0, 0)  # Mode indéterminé
    
    def on_status(self, message):
        """Met à jour le message de statut"""
        self.progress_label.setText(message)
    
    def on_module_finished(self, success, module_name):
        """Fin de l'installation d'un module"""
        if success:
            self.progress_label.setText(f"✅ {module_name} installé avec succès!")
        else:
            self.progress_label.setText(f"❌ Échec de l'installation de {module_name}")
        
        self.current_index += 1
        self.install_next()
    
    def on_all_complete(self):
        """Tous les modules sont installés"""
        self.progress_bar.setVisible(False)
        self.close_btn.setEnabled(True)
        
        QMessageBox.information(
            self,
            "Installation terminée",
            "Tous les modules ont été installés avec succès !\n\n"
            "Redémarrez l'application pour appliquer les changements."
        )
        
        self.close()