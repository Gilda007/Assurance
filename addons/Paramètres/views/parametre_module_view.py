import os
import json
import zipfile
import shutil
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QFileDialog, 
                             QMessageBox, QFrame, QScrollArea, QGraphicsDropShadowEffect,
                             QProgressBar, QProgressDialog, QGridLayout)
from PySide6.QtCore import Qt, QSize, QUrl, QThread, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QDesktopServices, QColor, QFont, QPalette, QLinearGradient, QBrush

# Import du gestionnaire de mise à jour
from update_manager import UpdateManager, UpdateChecker, UpdateInstaller
from version_manager import VersionManager


class ModuleInstaller(QThread):
    """Thread pour l'installation d'un module depuis un fichier zip"""
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, zip_path, addons_dir):
        super().__init__()
        self.zip_path = zip_path
        self.addons_dir = addons_dir
        
    def run(self):
        try:
            self.status.emit("Extraction du module...")
            
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                if 'manifest.json' not in [f for f in zip_ref.namelist() if f.endswith('manifest.json')]:
                    self.finished.emit(False, "Le module ne contient pas de manifest.json")
                    return
                
                zip_ref.extractall(self.addons_dir)
            
            extracted_folders = [f for f in os.listdir(self.addons_dir) 
                                if os.path.isdir(os.path.join(self.addons_dir, f))]
            
            if extracted_folders:
                module_name = extracted_folders[-1]
                manifest_path = os.path.join(self.addons_dir, module_name, 'manifest.json')
                if os.path.exists(manifest_path):
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    
                    version_manager = VersionManager(self.addons_dir)
                    version_manager.update_module(
                        module_name,
                        manifest.get('version', '1.0.0'),
                        manifest.get('changelog', 'Installation initiale'),
                        0
                    )
                    
                    self.status.emit("Module installé avec succès")
                    self.finished.emit(True, f"Module {module_name} installé")
                else:
                    self.finished.emit(False, "Manifest.json non trouvé après extraction")
            else:
                self.finished.emit(False, "Aucun dossier extrait")
                
        except Exception as e:
            self.finished.emit(False, f"Erreur: {str(e)}")


class ModernCard(QFrame):
    """Carte moderne avec effet de survol"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
        
    def setup_style(self):
        self.setStyleSheet("""
            ModernCard {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
            ModernCard:hover {
                border-color: #cbd5e1;
                background-color: #fafcff;
            }
        """)
        self._add_shadow()
    
    def _add_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)


class ParametreModuleWidget(QWidget):
    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.addons_dir = os.path.join(os.getcwd(), "addons")
        self.version_manager = VersionManager(self.addons_dir)
        self.update_manager = UpdateManager(self)
        
        self.setup_ui()
        self.refresh_data()
        self.check_modules_updates()
    
    def setup_ui(self):
        # Style global
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f8;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #e2e8f0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #94a3b8;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #64748b;
            }
        """)
        
        # Scroll principal
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.NoFrame)
        main_scroll.setStyleSheet("border: none; background: transparent;")
        
        # Widget principal
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(40, 30, 40, 40)
        self.main_layout.setSpacing(30)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        
        # Titre et sous-titre
        title_container = QVBoxLayout()
        title = QLabel("Extensions & Modules")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: 800;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1e293b, stop:1 #3b82f6);
            background-clip: text;
            color: transparent;
        """)
        
        subtitle = QLabel("Personnalisez et enrichissez votre application avec des modules additionnels")
        subtitle.setStyleSheet("color: #64748b; font-size: 14px; margin-top: 8px;")
        
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        
        # Boutons d'action
        btn_container = QHBoxLayout()
        btn_container.setSpacing(15)
        
        self.btn_import = self._create_gradient_button(
            "📥 Importer un module", 
            "#3b82f6", "#2563eb",
            "bg-gradient-to-r from-blue-500 to-blue-600"
        )
        self.btn_import.clicked.connect(self.import_zip_module)
        
        self.btn_check_updates = self._create_gradient_button(
            "🔄 Vérifier les mises à jour", 
            "#10b981", "#059669",
            "bg-gradient-to-r from-emerald-500 to-emerald-600"
        )
        self.btn_check_updates.clicked.connect(self.check_modules_updates)
        
        btn_container.addWidget(self.btn_import)
        btn_container.addWidget(self.btn_check_updates)
        
        header_layout.addLayout(title_container, 1)
        header_layout.addLayout(btn_container)
        self.main_layout.addLayout(header_layout)

        # --- STATS CARDS ---
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(25)
        
        self.card_total = self._create_modern_stat_card("Modules Disponibles", "0", "#3b82f6", "📦")
        self.card_active = self._create_modern_stat_card("Modules Installés", "0", "#10b981", "✅")
        self.card_updates = self._create_modern_stat_card("Mises à jour", "0", "#f59e0b", "🔄")
        
        self.stats_layout.addWidget(self.card_total)
        self.stats_layout.addWidget(self.card_active)
        self.stats_layout.addWidget(self.card_updates)
        self.stats_layout.addStretch()
        self.main_layout.addLayout(self.stats_layout)

        # --- MAIN CONTENT ---
        content_split = QHBoxLayout()
        content_split.setSpacing(30)

        # Sidebar - Liste des modules
        sidebar_container = QFrame()
        sidebar_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 24px;
                border: 1px solid #e2e8f0;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(15)
        
        # Sidebar header
        sidebar_header = QLabel("📋 Modules disponibles")
        sidebar_header.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #1e293b;
            padding: 0 10px 10px 10px;
            border-bottom: 2px solid #e2e8f0;
        """)
        sidebar_layout.addWidget(sidebar_header)
        
        self.module_list = QListWidget()
        self.module_list.setStyleSheet("""
            QListWidget {
                border: none;
                outline: none;
                background: transparent;
            }
            QListWidget::item {
                padding: 14px 16px;
                border-radius: 14px;
                margin-bottom: 6px;
                color: #475569;
                font-weight: 500;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #eff6ff, stop:1 #dbeafe);
                color: #2563eb;
                font-weight: 600;
            }
            QListWidget::item:hover:!selected {
                background: #f8fafc;
            }
        """)
        self.module_list.currentRowChanged.connect(self.display_module_details)
        sidebar_layout.addWidget(self.module_list)
        
        # Détails du module
        self.detail_frame = ModernCard()
        self.detail_layout = QVBoxLayout(self.detail_frame)
        self.detail_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll pour le contenu des détails
        self.detail_scroll = QScrollArea()
        self.detail_scroll.setWidgetResizable(True)
        self.detail_scroll.setFrameShape(QFrame.NoFrame)
        self.detail_scroll.setStyleSheet("border: none; background: transparent;")
        
        self.dynamic_widget = QWidget()
        self.dynamic_layout = QVBoxLayout(self.dynamic_widget)
        self.dynamic_layout.setContentsMargins(30, 30, 30, 30)
        self.dynamic_layout.setSpacing(20)
        
        self.placeholder = QFrame()
        placeholder_layout = QVBoxLayout(self.placeholder)
        placeholder_layout.setAlignment(Qt.AlignCenter)
        
        placeholder_icon = QLabel("🔌")
        placeholder_icon.setStyleSheet("font-size: 64px; background: transparent;")
        placeholder_icon.setAlignment(Qt.AlignCenter)
        
        placeholder_text = QLabel("Sélectionnez un module")
        placeholder_text.setStyleSheet("font-size: 18px; font-weight: 600; color: #94a3b8;")
        placeholder_text.setAlignment(Qt.AlignCenter)
        
        placeholder_sub = QLabel("pour voir les détails et options")
        placeholder_sub.setStyleSheet("font-size: 13px; color: #cbd5e1;")
        placeholder_sub.setAlignment(Qt.AlignCenter)
        
        placeholder_layout.addWidget(placeholder_icon)
        placeholder_layout.addWidget(placeholder_text)
        placeholder_layout.addWidget(placeholder_sub)
        
        self.dynamic_layout.addWidget(self.placeholder)
        self.detail_scroll.setWidget(self.dynamic_widget)
        self.detail_layout.addWidget(self.detail_scroll)
        
        content_split.addWidget(sidebar_container, 35)
        content_split.addWidget(self.detail_frame, 65)
        self.main_layout.addLayout(content_split)
        
        main_scroll.setWidget(main_widget)
        
        # Layout principal
        main_container = QVBoxLayout(self)
        main_container.setContentsMargins(0, 0, 0, 0)
        main_container.addWidget(main_scroll)
    
    def _create_gradient_button(self, text, color1, color2, gradient_class):
        """Crée un bouton avec dégradé"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color1}, stop:1 {color2});
                color: white;
                font-weight: bold;
                border-radius: 14px;
                padding: 12px 24px;
                font-size: 13px;
                border: none;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color2}, stop:1 {color1});
            }}
            QPushButton:pressed {{
                padding-top: 13px;
                padding-bottom: 11px;
            }}
        """)
        return btn
    
    def _create_modern_stat_card(self, title, value, color, icon):
        """Crée une carte statistique moderne"""
        card = QFrame()
        card.setFixedSize(220, 130)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }}
        """)
        
        # Ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Partie gauche - Icône
        icon_container = QFrame()
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {color}15;
                border-radius: 15px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 24px; background: transparent;")
        icon_layout.addWidget(icon_lbl)
        
        # Partie droite - Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet("""
            color: #64748b;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1px;
        """)
        
        value_lbl = QLabel(value)
        value_lbl.setObjectName("stat_value")
        value_lbl.setStyleSheet(f"""
            color: {color};
            font-size: 32px;
            font-weight: 800;
        """)
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(value_lbl)
        
        layout.addWidget(icon_container)
        layout.addSpacing(15)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return card
    
    def _update_stat_value(self, card, value):
        """Met à jour la valeur d'une carte statistique"""
        for child in card.findChildren(QLabel):
            if child.objectName() == "stat_value":
                child.setText(value)
                break

    def get_all_modules(self):
        """Récupère tous les modules avec leurs informations"""
        modules = []
        if not os.path.exists(self.addons_dir): 
            return modules
        
        for folder in os.listdir(self.addons_dir):
            folder_path = os.path.join(self.addons_dir, folder)
            manifest = os.path.join(folder_path, "manifest.json")
            
            if os.path.isdir(folder_path) and not folder.startswith(".") and not folder.endswith("_backup"):
                m_data = {
                    "name": folder, 
                    "version": "1.0.0", 
                    "author": "Inconnu", 
                    "description": "", 
                    "installable": True, 
                    "folder_name": folder,
                    "has_update": False,
                    "new_version": None,
                    "icon": "📦"
                }
                
                if os.path.exists(manifest):
                    try:
                        with open(manifest, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data.get("description"), list): 
                                data["description"] = " ".join(data["description"])
                            m_data.update(data)
                            # Définir une icône basée sur la catégorie
                            category = data.get('category', '').lower()
                            if 'automobile' in category:
                                m_data['icon'] = '🚗'
                            elif 'finance' in category:
                                m_data['icon'] = '💰'
                            elif 'param' in category:
                                m_data['icon'] = '⚙️'
                    except: 
                        pass
                
                local_version = self.version_manager.get_module_version(folder)
                if local_version:
                    m_data['version'] = local_version
                
                modules.append(m_data)
        
        return modules

    def refresh_data(self):
        """Rafraîchit l'affichage des modules"""
        self.module_list.clear()
        mods = self.get_all_modules()
        active = 0
        updates_available = 0
        
        for m in mods:
            if m.get('installable'): 
                active += 1
            
            if m.get('has_update'):
                updates_available += 1
                item_text = f"{m['icon']} {m['name']}"
            else:
                item_text = f"{m['icon']} {m['name']}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, m)
            
            if m.get('has_update'):
                item.setForeground(QColor("#f59e0b"))
                font = QFont()
                font.setBold(True)
                item.setFont(font)
            
            self.module_list.addItem(item)
        
        self._update_stat_value(self.card_total, str(len(mods)))
        self._update_stat_value(self.card_active, str(active))
        self._update_stat_value(self.card_updates, str(updates_available))

    def check_modules_updates(self):
        """Vérifie les mises à jour des modules"""
        self.btn_check_updates.setEnabled(False)
        self.btn_check_updates.setText("Recherche en cours...")
        
        from config import Config
        self.checker = UpdateChecker(Config.UPDATE_SERVER, self.addons_dir)
        self.checker.update_found.connect(self.on_updates_found)
        self.checker.no_update.connect(self.on_no_updates)
        self.checker.error_occurred.connect(self.on_check_error)
        self.checker.start()
    
    def on_updates_found(self, updates):
        """Mise à jour trouvée"""
        self.btn_check_updates.setEnabled(True)
        self.btn_check_updates.setText("🔄 Vérifier les mises à jour")
        
        module_updates = {k: v for k, v in updates.items() if k != 'app'}
        
        if module_updates:
            for module_name, update_info in module_updates.items():
                for i in range(self.module_list.count()):
                    item = self.module_list.item(i)
                    mod = item.data(Qt.UserRole)
                    if mod['name'] == module_name:
                        mod['has_update'] = True
                        mod['new_version'] = update_info['new_version']
                        break
            
            self.refresh_data()
            
            reply = QMessageBox.question(
                self, 
                "✨ Mises à jour disponibles", 
                f"{len(module_updates)} module(s) peuvent être mis à jour.\n\n"
                "Souhaitez-vous installer les mises à jour maintenant ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.install_module_updates(module_updates)
        else:
            QMessageBox.information(self, "Mise à jour", "Aucune mise à jour disponible")
    
    def on_no_updates(self):
        """Aucune mise à jour"""
        self.btn_check_updates.setEnabled(True)
        self.btn_check_updates.setText("🔄 Vérifier les mises à jour")
        QMessageBox.information(self, "Mise à jour", "Tous vos modules sont à jour")
    
    def on_check_error(self, error):
        """Erreur lors de la vérification"""
        self.btn_check_updates.setEnabled(True)
        self.btn_check_updates.setText("🔄 Vérifier les mises à jour")
        QMessageBox.warning(self, "Erreur", f"Impossible de vérifier les mises à jour:\n{error}")
    
    def install_module_updates(self, updates):
        """Installe les mises à jour des modules"""
        self.progress_dialog = QProgressDialog("Installation des mises à jour...", "Annuler", 0, len(updates), self)
        self.progress_dialog.setWindowTitle("Mise à jour")
        self.progress_dialog.setMinimumWidth(400)
        self.progress_dialog.setStyleSheet("""
            QProgressDialog {
                background: white;
                border-radius: 16px;
            }
            QProgressBar {
                border: none;
                background: #e2e8f0;
                border-radius: 10px;
                height: 8px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                border-radius: 10px;
            }
        """)
        
        self.installer = UpdateInstaller(self.addons_dir)
        self.installer.progress.connect(self.on_install_progress)
        self.installer.status.connect(self.on_install_status)
        self.installer.finished.connect(self.on_install_finished)
        
        for module_name, update_info in updates.items():
            self.installer.add_update(update_info)
        
        self.installer.start()
    
    def on_install_progress(self, current, total):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(current)
            self.progress_dialog.setMaximum(total)
    
    def on_install_status(self, status):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setLabelText(status)
    
    def on_install_finished(self, success, message):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        if success:
            self.refresh_data()
            QMessageBox.information(self, "Succès", message + "\n\nRedémarrez l'application pour appliquer les changements.")
        else:
            QMessageBox.warning(self, "Erreur", message)

    def display_module_details(self, index):
        """Affiche les détails d'un module"""
        if index < 0:
            self.placeholder.show()
            return
        
        self.placeholder.hide()
        
        while self.dynamic_layout.count():
            w = self.dynamic_layout.takeAt(0).widget()
            if w and w != self.placeholder:
                w.deleteLater()

        mod = self.module_list.currentItem().data(Qt.UserRole)

        # ========== EN-TÊTE ==========
        header_section = QFrame()
        header_section.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                border-radius: 20px;
            }
        """)
        header_layout = QHBoxLayout(header_section)
        header_layout.setContentsMargins(25, 20, 25, 20)
        
        # Icône
        icon_container = QFrame()
        icon_container.setFixedSize(70, 70)
        icon_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_lbl = QLabel(mod.get('icon', '📦'))
        icon_lbl.setStyleSheet("font-size: 32px;")
        icon_layout.addWidget(icon_lbl)
        
        # Titre et version
        title_container = QVBoxLayout()
        title_container.setSpacing(8)
        
        title_row = QHBoxLayout()
        title_lbl = QLabel(mod['name'])
        title_lbl.setStyleSheet("font-size: 24px; font-weight: 800; color: #1e293b;")
        title_row.addWidget(title_lbl)
        
        version_badge = QLabel(f"v{mod['version']}")
        version_badge.setStyleSheet("""
            background: #e2e8f0;
            color: #475569;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        """)
        title_row.addWidget(version_badge)
        
        if mod.get('has_update'):
            update_badge = QLabel(f"🔄 Mise à jour v{mod['new_version']} disponible")
            update_badge.setStyleSheet("""
                background: #fef3c7;
                color: #f59e0b;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            """)
            title_row.addWidget(update_badge)
        
        title_row.addStretch()
        
        author_lbl = QLabel(f"Par {mod['author']}")
        author_lbl.setStyleSheet("color: #64748b; font-size: 13px;")
        
        title_container.addLayout(title_row)
        title_container.addWidget(author_lbl)
        
        header_layout.addWidget(icon_container)
        header_layout.addSpacing(20)
        header_layout.addLayout(title_container, 1)
        
        self.dynamic_layout.addWidget(header_section)
        
        # ========== DESCRIPTION ==========
        desc_card = QFrame()
        desc_card.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        desc_layout = QVBoxLayout(desc_card)
        desc_layout.setContentsMargins(20, 18, 20, 18)
        
        desc_title = QLabel("📖 Description")
        desc_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 8px;")
        desc_layout.addWidget(desc_title)
        
        desc_text = QLabel(mod['description'] or "Aucune description disponible.")
        desc_text.setWordWrap(True)
        desc_text.setStyleSheet("color: #475569; font-size: 14px; line-height: 150%;")
        desc_layout.addWidget(desc_text)
        
        self.dynamic_layout.addWidget(desc_card)
        
        # ========== INFORMATIONS TECHNIQUES ==========
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(20, 18, 20, 18)
        
        info_title = QLabel("🔧 Informations techniques")
        info_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 12px;")
        info_layout.addWidget(info_title)
        
        info_grid = QGridLayout()
        info_grid.setSpacing(12)
        
        # Dépendances
        deps = mod.get('dependencies', [])
        deps_text = ', '.join(deps) if deps else 'Aucune'
        info_grid.addWidget(QLabel("📦 Dépendances:"), 0, 0)
        info_grid.addWidget(QLabel(deps_text), 0, 1)
        
        # Catégorie
        category = mod.get('category', 'Général')
        info_grid.addWidget(QLabel("📁 Catégorie:"), 1, 0)
        info_grid.addWidget(QLabel(category), 1, 1)
        
        # Licence
        license = mod.get('license', 'Propriétaire')
        info_grid.addWidget(QLabel("📜 Licence:"), 2, 0)
        info_grid.addWidget(QLabel(license), 2, 1)
        
        # Date d'installation
        module_info = self.version_manager.get_module_info(mod['folder_name'])
        if module_info and module_info.get('last_update'):
            date_text = module_info['last_update'][:10]
            info_grid.addWidget(QLabel("📅 Dernière MAJ:"), 3, 0)
            info_grid.addWidget(QLabel(date_text), 3, 1)
        
        info_layout.addLayout(info_grid)
        self.dynamic_layout.addWidget(info_card)
        
        # ========== ACTIONS ==========
        actions_card = QFrame()
        actions_card.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(20, 18, 20, 18)
        
        actions_title = QLabel("⚡ Actions")
        actions_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 12px;")
        actions_layout.addWidget(actions_title)
        
        actions_buttons = QHBoxLayout()
        actions_buttons.setSpacing(15)
        
        # Bouton site web
        if mod.get('website'):
            btn_website = QPushButton("🌐 Site du développeur")
            btn_website.setCursor(Qt.PointingHandCursor)
            btn_website.setStyleSheet("""
                QPushButton {
                    background: white;
                    color: #475569;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: #f1f5f9;
                    border-color: #cbd5e1;
                }
            """)
            btn_website.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(mod['website'])))
            actions_buttons.addWidget(btn_website)
        
        # Bouton de mise à jour
        if mod.get('has_update'):
            btn_update = QPushButton(f"⬆️ Mettre à jour vers v{mod['new_version']}")
            btn_update.setCursor(Qt.PointingHandCursor)
            btn_update.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #f59e0b, stop:1 #ea580c);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 10px 22px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #ea580c, stop:1 #c2410c);
                }
            """)
            btn_update.clicked.connect(lambda: self.update_single_module(mod))
            actions_buttons.addWidget(btn_update)
        
        actions_buttons.addStretch()
        
        # Bouton activer/désactiver
        is_installed = mod.get('installable', True)
        btn_toggle = QPushButton("🔌 Désactiver" if is_installed else "▶️ Activer")
        btn_toggle.setCursor(Qt.PointingHandCursor)
        color = "#ef4444" if is_installed else "#10b981"
        btn_toggle.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 22px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {color}dd;
            }}
        """)
        btn_toggle.clicked.connect(lambda: self.toggle_status(mod['folder_name'], is_installed))
        actions_buttons.addWidget(btn_toggle)
        
        actions_layout.addLayout(actions_buttons)
        self.dynamic_layout.addWidget(actions_card)
        
        self.dynamic_layout.addStretch()
    
    def update_single_module(self, mod):
        """Met à jour un module spécifique"""
        from config import Config
        self.checker = UpdateChecker(Config.UPDATE_SERVER, self.addons_dir)
        self.checker.update_found.connect(lambda updates: self.on_single_update_found(mod, updates))
        self.checker.start()
    
    def on_single_update_found(self, mod, updates):
        """Gère la mise à jour d'un seul module"""
        if mod['name'] in updates:
            self.install_module_updates({mod['name']: updates[mod['name']]})
        else:
            QMessageBox.information(self, "Info", f"Aucune mise à jour disponible pour {mod['name']}")

    def toggle_status(self, folder, current):
        """Active/Désactive un module"""
        manifest_path = os.path.join(self.addons_dir, folder, "manifest.json")
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f: 
                data = json.load(f)
            data["installable"] = not current
            with open(manifest_path, 'w', encoding='utf-8') as f: 
                json.dump(data, f, indent=4)
            
            self.version_manager.enable_module(folder, not current)
            self.refresh_data()
            QMessageBox.information(self, "Succès", f"Module {'activé' if not current else 'désactivé'}")
        except Exception as e: 
            QMessageBox.critical(self, "Erreur", str(e))

    def import_zip_module(self):
        """Importe un module depuis un fichier zip avec validation"""
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Importer un module", 
            "", 
            "Module ZIP (*.zip);;Tous les fichiers (*)"
        )
        if not path: 
            return
        
        # Valider le ZIP avant l'import
        if not self.validate_zip_module(path):
            return
        
        # Dialogue de progression
        self.progress_dialog = QProgressDialog("Installation du module...", "Annuler", 0, 100, self)
        self.progress_dialog.setWindowTitle("Installation")
        self.progress_dialog.setMinimumWidth(400)
        self.progress_dialog.setStyleSheet("""
            QProgressDialog {
                background: white;
                border-radius: 16px;
            }
            QProgressBar {
                border: none;
                background: #e2e8f0;
                border-radius: 10px;
                height: 8px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                border-radius: 10px;
            }
        """)
        
        self.installer_thread = ModuleInstaller(path, self.addons_dir)
        self.installer_thread.progress.connect(self.progress_dialog.setValue)
        self.installer_thread.status.connect(self.progress_dialog.setLabelText)
        self.installer_thread.finished.connect(self.on_import_finished)
        self.installer_thread.start()

    def validate_zip_module(self, zip_path):
        """Valide qu'un fichier ZIP contient un manifest.json valide"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Liste tous les fichiers dans le zip
                file_list = zip_ref.namelist()
                
                # Chercher manifest.json (à la racine ou dans un dossier)
                manifest_found = None
                for file_name in file_list:
                    if file_name.endswith('manifest.json'):
                        manifest_found = file_name
                        break
                
                if not manifest_found:
                    QMessageBox.warning(
                        self, 
                        "Module invalide", 
                        "Le fichier ZIP ne contient pas de manifest.json.\n\n"
                        "Un module valide doit avoir la structure suivante :\n"
                        "  • manifest.json (fichier de configuration)\n"
                        "  • Les fichiers du module dans un dossier ou à la racine\n\n"
                        "Exemple de manifest.json valide :\n"
                        "{\n"
                        '  "name": "MonModule",\n'
                        '  "version": "1.0.0",\n'
                        '  "author": "Nom Auteur",\n'
                        '  "description": "Description du module"\n'
                        "}"
                    )
                    return False
                
                # Vérifier que le manifest.json est valide (contient les champs requis)
                with zip_ref.open(manifest_found) as manifest_file:
                    try:
                        manifest_data = json.load(manifest_file)
                        
                        # Vérifier les champs requis
                        required_fields = ['name', 'version']
                        missing_fields = [f for f in required_fields if f not in manifest_data]
                        
                        if missing_fields:
                            QMessageBox.warning(
                                self,
                                "Manifest invalide",
                                f"Le manifest.json ne contient pas les champs requis : {', '.join(missing_fields)}"
                            )
                            return False
                        
                        # Afficher les infos du module pour confirmation
                        module_name = manifest_data.get('name', 'Inconnu')
                        module_version = manifest_data.get('version', '0.0.0')
                        module_author = manifest_data.get('author', 'Auteur inconnu')
                        
                        reply = QMessageBox.question(
                            self,
                            "Confirmation d'import",
                            f"Module à importer :\n\n"
                            f"📦 Nom : {module_name}\n"
                            f"🔖 Version : {module_version}\n"
                            f"👤 Auteur : {module_author}\n\n"
                            f"Souhaitez-vous installer ce module ?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        
                        return reply == QMessageBox.Yes
                        
                    except json.JSONDecodeError as e:
                        QMessageBox.warning(
                            self,
                            "Manifest invalide",
                            f"Le fichier manifest.json n'est pas un JSON valide :\n{str(e)}"
                        )
                        return False
                        
        except zipfile.BadZipFile:
            QMessageBox.warning(self, "Fichier invalide", "Le fichier sélectionné n'est pas un ZIP valide.")
            return False
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la validation : {str(e)}")
            return False
    
    def on_import_finished(self, success, message):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        if success:
            self.refresh_data()
            QMessageBox.information(self, "Succès", message)
        else:
            QMessageBox.critical(self, "Erreur", message)