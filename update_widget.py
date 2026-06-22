import os
import zipfile
import shutil
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QProgressBar, QScrollArea,
    QFrame, QMessageBox, QWidget, QGraphicsDropShadowEffect, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QThread, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QFont, QColor, QPalette
from update_client import UpdateClient


class DownloadInstallThread(QThread):
    """Thread pour télécharger et installer un module"""
    progress = Signal(int, int)
    status = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, client, module, install_paths):
        super().__init__()
        self.client = client
        self.module = module
        self.install_paths = install_paths
        self.temp_dir = Path("_internal/addons")

        try:
            # Correction : parents=True force la création de '_internal' s'il n'existe pas en mode dev
            self.temp_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Repli de sécurité universel si l'arborescence locale refuse d'écrire (ex: permissions sous Linux)
            import tempfile
            self.temp_dir = Path(tempfile.gettempdir()) / "lometa_updates"
            self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self):
        zip_path = self.temp_dir / self.module['filename']
        
        self.status.emit(f"📥 Téléchargement de {self.module['name']}...")
        
        def progress_callback(current, total):
            percent = int(current * 100 / total)
            self.progress.emit(percent, 100)
        
        success = self.client.download_module(self.module, str(zip_path), progress_callback)
        
        if not success:
            self.finished.emit(False, self.module['name'])
            return
        
        self.status.emit(f"📦 Installation de {self.module['name']}...")
        self.progress.emit(0, 0)
        
        try:
            extract_dir = self.temp_dir / f"{self.module['id']}"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)
            
            items = list(extract_dir.iterdir())
            source_dir = items[0] if len(items) == 1 and items[0].is_dir() else extract_dir
            
            for install_path in self.install_paths:
                target_dir = Path(install_path) / self.module['id']
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(source_dir, target_dir)
                self.status.emit(f"📁 Installé dans {target_dir}")
            
            shutil.rmtree(extract_dir)
            os.remove(zip_path)
            
            self.finished.emit(True, self.module['name'])
            
        except Exception as e:
            self.status.emit(f"❌ Erreur: {str(e)}")
            self.finished.emit(False, self.module['name'])


class ModuleCard(QFrame):
    """Carte individuelle pour un module avec design moderne"""
    
    selection_changed = Signal(bool, object)
    
    def __init__(self, module, parent=None):
        super().__init__(parent)
        self.module = module
        self.is_selected = True
        self.setup_ui()
        self.apply_shadow()
    
    def setup_ui(self):
        self.setFixedHeight(100)
        self.setStyleSheet("""
            ModuleCard {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
            ModuleCard:hover {
                border-color: #6366f1;
                background: #faf5ff;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(16)
        
        # Checkbox stylisée
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid #cbd5e1;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #6366f1;
                border-color: #6366f1;
            }
            QCheckBox::indicator:checked::after {
                width: 10px;
                height: 10px;
            }
        """)
        self.checkbox.toggled.connect(self.on_checkbox_toggled)
        layout.addWidget(self.checkbox)
        
        # Zone d'icône
        icon_frame = QFrame()
        icon_frame.setFixedSize(50, 50)
        icon_frame.setStyleSheet("""
            QFrame {
                background: #eef2ff;
                border-radius: 14px;
            }
        """)
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel("📦")
        icon_label.setStyleSheet("font-size: 24px;")
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_frame)
        
        # Informations du module
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        
        # Nom et version
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        name_label = QLabel(self.module['name'])
        name_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 700;
            color: #1e293b;
        """)
        header_layout.addWidget(name_label)
        
        version_label = QLabel(f"v{self.module.get('version', '1.0.0')}")
        version_label.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            color: #6366f1;
            background: #eef2ff;
            padding: 2px 8px;
            border-radius: 12px;
        """)
        header_layout.addWidget(version_label)
        header_layout.addStretch()
        
        info_layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(self.module.get('description', f"Module {self.module['name']} pour LOMETA"))
        desc_label.setStyleSheet("""
            font-size: 12px;
            color: #64748b;
        """)
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        # Métadonnées
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(16)
        
        size_label = QLabel(f"💾 {self.module['size_mb']} MB")
        size_label.setStyleSheet("font-size: 11px; color: #94a3b8;")
        meta_layout.addWidget(size_label)
        
        filename_label = QLabel(f"📄 {self.module['filename']}")
        filename_label.setStyleSheet("font-size: 11px; color: #94a3b8;")
        meta_layout.addWidget(filename_label)
        
        if self.module.get('modified_str'):
        #    date_label = QLabel(f"📅 {self.module['modified_str']}")
        #    date_label.setStyleSheet("font-size: 11px; color: #94a3b8;")
        #    meta_layout.addWidget(date_label)
            pass
        
        meta_layout.addStretch()
        info_layout.addLayout(meta_layout)
        
        layout.addLayout(info_layout, 1)
        
        # Badge de statut (optionnel)
        status_frame = QFrame()
        status_frame.setFixedSize(8, 8)
        status_frame.setStyleSheet("""
            QFrame {
                background: #10b981;
                border-radius: 4px;
            }
        """)
        layout.addWidget(status_frame)
    
    def apply_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def on_checkbox_toggled(self, checked):
        self.is_selected = checked
        if checked:
            self.setStyleSheet("""
                ModuleCard {
                    background: white;
                    border-radius: 16px;
                    border: 1px solid #6366f1;
                }
            """)
        else:
            self.setStyleSheet("""
                ModuleCard {
                    background: white;
                    border-radius: 16px;
                    border: 1px solid #e2e8f0;
                }
            """)
        self.selection_changed.emit(checked, self.module)
    
    def is_checked(self):
        return self.checkbox.isChecked()


class UpdateWidget(QDialog):
    """Widget de mise à jour avec design professionnel"""
    
    def __init__(self, modules, parent=None):
        super().__init__(parent)
        self.modules = modules
        self.client = UpdateClient()
        self.threads = []
        self.module_cards = []
        
        # Configuration de la fenêtre
        self.setWindowTitle("Mise à jour des modules - LOMETA")
        self.setMinimumSize(700, 550)
        self.resize(800, 600)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background: #f1f5f9;
            }
        """)
        
        # Effet d'ombre sur la fenêtre
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Chemins d'installation
        self.install_paths = [
            "addons",
            "_internal/addons",
            "dist/LOMETA/addons",
            "dist/LOMETA/_internal/addons"
        ]
        self.install_paths = [p for p in self.install_paths if os.path.exists(p) or os.path.exists(os.path.dirname(p))]
        if not self.install_paths:
            self.install_paths = ["addons"]
            os.makedirs("addons", exist_ok=True)
        
        self.setup_ui()
        self.load_modules()
    
    def setup_ui(self):
        """Configure l'interface principale - Design sobre et professionnel"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(0)
        
        # Conteneur principal
        container = QFrame()
        container.setObjectName("mainContainer")
        container.setStyleSheet("""
            QFrame#mainContainer {
                background: #ffffff;
                border-radius: 20px;
            }
        """)
        
        # Ombre légère
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 4)
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # ========== EN-TÊTE ==========
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(88)
        header.setStyleSheet("""
            QFrame#header {
                background: #1e293b;
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(28, 0, 28, 0)
        
        # Titre
        title_container = QWidget()
        title_container_layout = QVBoxLayout(title_container)
        title_container_layout.setSpacing(6)
        
        title_label = QLabel("Mises à jour disponibles")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
            letter-spacing: -0.2px;
        """)
        title_container_layout.addWidget(title_label)
        
        subtitle_label = QLabel(f"{len(self.modules)} module(s) prêt(s) à être installé(s)")
        subtitle_label.setStyleSheet("""
            font-size: 12px;
            color: #94a3b8;
        """)
        title_container_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        
        # Bouton fermer
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                border: none;
                border-radius: 15px;
                color: #94a3b8;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
                color: #ffffff;
            }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        container_layout.addWidget(header)
        
        # ========== CORPS ==========
        body = QFrame()
        body.setObjectName("body")
        body.setStyleSheet("""
            QFrame#body {
                background: #ffffff;
            }
        """)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 24, 28, 24)
        body_layout.setSpacing(20)
        
        # Statistiques en ligne
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        total_size = sum(m.get('size_mb', 0) for m in self.modules)
        
        stats_items = [
            ("📦", str(len(self.modules)), "disponibles"),
            ("💾", f"{total_size:.1f}" if total_size > 0 else "?", "Mo"),
            ("⚡", "Auto", "installation"),
        ]
        
        for icon, value, label in stats_items:
            stat_frame = QFrame()
            stat_frame.setStyleSheet("""
                QFrame {
                    background: #f8fafc;
                    border-radius: 12px;
                }
            """)
            stat_frame.setFixedHeight(64)
            stat_layout_h = QHBoxLayout(stat_frame)
            stat_layout_h.setContentsMargins(16, 0, 16, 0)
            
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 20px;")
            stat_layout_h.addWidget(icon_lbl)
            
            stat_info = QVBoxLayout()
            stat_info.setSpacing(2)
            value_lbl = QLabel(value)
            value_lbl.setStyleSheet("""
                font-size: 16px;
                font-weight: 700;
                color: #0f172a;
            """)
            stat_info.addWidget(value_lbl)
            label_lbl = QLabel(label)
            label_lbl.setStyleSheet("""
                font-size: 11px;
                color: #64748b;
            """)
            stat_info.addWidget(label_lbl)
            
            stat_layout_h.addLayout(stat_info)
            stat_layout_h.addStretch()
            stats_layout.addWidget(stat_frame)
        
        stats_layout.addStretch()
        body_layout.addWidget(stats_widget)
        
        # Séparateur
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #e2e8f0;")
        body_layout.addWidget(sep)
        
        # Titre de section
        section_label = QLabel("Modules disponibles")
        section_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 600;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        body_layout.addWidget(section_label)
        
        # Zone de scroll pour les modules
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 5px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        self.modules_container = QWidget()
        self.modules_container.setStyleSheet("background: transparent;")
        self.modules_layout = QVBoxLayout(self.modules_container)
        self.modules_layout.setSpacing(10)
        self.modules_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.modules_container)
        body_layout.addWidget(scroll_area, 1)
        
        # ========== ZONE DE PROGRESSION ==========
        self.progress_frame = QFrame()
        self.progress_frame.setVisible(False)
        self.progress_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 12px;
            }
        """)
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setSpacing(8)
        progress_layout.setContentsMargins(16, 14, 16, 14)
        
        self.progress_label = QLabel("Préparation...")
        self.progress_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 500;
            color: #0f172a;
        """)
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #e2e8f0;
                border-radius: 4px;
                height: 4px;
            }
            QProgressBar::chunk {
                background: #3b82f6;
                border-radius: 4px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            font-size: 11px;
            color: #64748b;
        """)
        progress_layout.addWidget(self.status_label)
        
        body_layout.addWidget(self.progress_frame)
        
        # ========== BOUTONS ==========
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(12)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.download_btn = QPushButton("Installer la sélection")
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.setFixedHeight(40)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0 24px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QPushButton:disabled {
                background: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self.download_btn.clicked.connect(self.download_selected)
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 0 20px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #f8fafc;
                border-color: #cbd5e1;
            }
        """)
        self.cancel_btn.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.cancel_btn)
        body_layout.addWidget(btn_container)
        
        container_layout.addWidget(body)
        main_layout.addWidget(container)
        
        self.download_btn.setEnabled(False)
    
    def load_modules(self):
        """Charge la liste des modules disponibles"""
        for module in self.modules:
            card = ModuleCard(module)
            card.selection_changed.connect(self.on_selection_changed)
            self.modules_layout.addWidget(card)
            self.module_cards.append(card)
        
        self.modules_layout.addStretch()
        self.update_button_state()
    
    def on_selection_changed(self, checked, module):
        """Gère le changement de sélection"""
        self.update_button_state()
    
    def update_button_state(self):
        """Met à jour l'état du bouton de téléchargement"""
        has_selection = any(card.is_checked() for card in self.module_cards)
        self.download_btn.setEnabled(has_selection)
    
    # def download_selected(self):
    #     """Lance le processus de téléchargement/installation des modules cochés"""
    #     self.selected_modules = []
    #     for card, checkbox, module in self.module_cards:
    #         if checkbox.isChecked():
    #             self.selected_modules.append((card, module))
                
    #     if not self.selected_modules:
    #         QMessageBox.warning(self, "Attention", "Veuillez sélectionner au moins un module.")
    #         return
            
    #     # --- NOUVEAU : SELECTION DU DOSSIER CIBLE ---
    #     from PySide6.QtWidgets import QFileDialog
    #     dir_path = QFileDialog.getExistingDirectory(
    #         self, 
    #         "Sélectionner le dossier dans lequel faire l'installation de la sélection",
    #         "", 
    #         QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
    #     )
        
    #     if not dir_path:
    #         return  # L'utilisateur a annulé l'explorateur, on arrête proprement sans crash
            
    #     self.install_paths = dir_path  # On applique le dossier choisi à l'installation
    #     # --------------------------------------------
        
    #     # Préparation de l'UI pour la progression
    #     self.current_index = 0
    #     self.progress_bar.setValue(0)
    #     self.progress_bar.setVisible(True)
    #     self.cancel_btn.setEnabled(False)
        
    #     self.install_next()

    def download_selected(self):
        """Lance le processus de téléchargement/installation des modules cochés"""
        self.selected_modules = []
        
        # CORRECTION ICI : On boucle sur l'objet 'card' unique, 
        # et on accède à sa checkbox et à son module directement.
        for card in self.module_cards:
            if card.checkbox.isChecked():
                self.selected_modules.append((card, card.module))
                
        if not self.selected_modules:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner au moins un module.")
            return
            
        # --- SÉLECTION DU DOSSIER CIBLE ---
        from PySide6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(
            self, 
            "Sélectionner le dossier dans lequel faire l'installation de la sélection",
            "", 
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not dir_path:
            return  # L'utilisateur a annulé l'explorateur, on arrête proprement sans crash
            
        self.install_paths = dir_path  # On applique le dossier choisi à l'installation
        # ----------------------------------
        
        # Préparation de l'UI pour la progression
        self.current_index = 0
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.cancel_btn.setEnabled(False)
        
        self.install_next()
    
    def install_next(self):
        """Installe le module suivant"""
        if self.current_index >= len(self.selected_modules):
            self.on_all_complete()
            return
        
        card, module = self.selected_modules[self.current_index]
        self.current_module = module
        
        thread = DownloadInstallThread(self.client, module, self.install_paths)
        thread.progress.connect(self.on_progress)
        thread.status.connect(self.on_status_message)
        thread.finished.connect(self.on_module_finished)
        thread.start()
        self.threads.append(thread)
    
    def on_progress(self, current, total):
        """Met à jour la progression"""
        if total > 0:
            self.progress_bar.setValue(current)
            self.progress_bar.setRange(0, 100)
        else:
            self.progress_bar.setRange(0, 0)
    
    def on_status_message(self, message):
        """Met à jour le message de statut"""
        self.progress_label.setText(message)
    
    def on_module_finished(self, success, module_name):
        """Fin de l'installation d'un module"""
        if success:
            self.status_label.setText(f"✅ Module {module_name} installé avec succès")
            
            # Marquer la carte comme installée
            for card, module in self.selected_modules:
                if module['name'] == module_name:
                    card.setStyleSheet("""
                        ModuleCard {
                            background: #f0fdf4;
                            border-radius: 16px;
                            border: 1px solid #10b981;
                        }
                    """)
                    break
        else:
            self.status_label.setText(f"❌ Échec de l'installation de {module_name}")
        
        self.current_index += 1
        self.install_next()
    
    def on_all_complete(self):
        """Tous les modules sont installés"""
        self.progress_bar.setVisible(False)
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setText("Fermer")
        
        QMessageBox.information(
            self,
            "Installation terminée",
            "✅ Tous les modules sélectionnés ont été installés avec succès !\n\n"
            "🔄 Veuillez redémarrer l'application pour appliquer les changements.",
            QMessageBox.Ok
        )
        
        self.close()