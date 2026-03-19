import os
import json
import zipfile
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QFileDialog, 
                             QMessageBox, QFrame, QScrollArea, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QDesktopServices, QColor, QFont

class ParametreModuleWidget(QWidget):
    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        # Fond général moderne (Slate 50)
        self.setStyleSheet("background-color: #f8fafc; border: none;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(30)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        header_v = QVBoxLayout()
        title = QLabel("Composants & Extensions")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: #1e293b;")
        subtitle = QLabel("Gérez les modules installés et étendez les fonctionnalités du système.")
        subtitle.setStyleSheet("color: #64748b; font-size: 14px;")
        header_v.addWidget(title)
        header_v.addWidget(subtitle)
        
        self.btn_import = QPushButton("📥 Importer un pack (.zip)")
        self.btn_import.setCursor(Qt.PointingHandCursor)
        self.btn_import.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6; color: white; font-weight: bold;
                border-radius: 8px; padding: 12px 24px; font-size: 13px;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        self.btn_import.clicked.connect(self.import_zip_module)

        header_layout.addLayout(header_v)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_import)
        self.main_layout.addLayout(header_layout)

        # --- STATS CARDS ---
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        
        self.card_total = self._create_stat_card("Modules Disponibles", "0", "#3b82f6")
        self.card_active = self._create_stat_card("Modules Installés", "0", "#10b981")
        
        self.stats_layout.addWidget(self.card_total)
        self.stats_layout.addWidget(self.card_active)
        # Spacer pour ne pas que les cartes prennent toute la largeur
        self.stats_layout.addStretch() 
        self.main_layout.addLayout(self.stats_layout)

        # --- MAIN CONTENT ---
        self.content_container = QHBoxLayout()
        self.content_container.setSpacing(25)

        # Sidebar Liste
        self.module_list = QListWidget()
        self.module_list.setFixedWidth(350)
        self.module_list.setStyleSheet("""
            QListWidget {
                background-color: white; border-radius: 15px;
                border: 1px solid #e2e8f0; outline: none; padding: 10px;
            }
            QListWidget::item {
                padding: 15px; border-radius: 10px; color: #475569; margin-bottom: 5px;
            }
            QListWidget::item:selected {
                background-color: #eff6ff; color: #3b82f6; font-weight: bold;
            }
            QListWidget::item:hover:!selected {
                background-color: #f1f5f9;
            }
        """)
        self._add_shadow(self.module_list)
        self.module_list.currentRowChanged.connect(self.display_module_details)

        # Détails (Card)
        self.detail_frame = QFrame()
        self.detail_frame.setStyleSheet("background-color: white; border-radius: 15px; border: 1px solid #e2e8f0;")
        self._add_shadow(self.detail_frame)
        self.detail_layout = QVBoxLayout(self.detail_frame)
        
        # Conteneur dynamique pour éviter le crash C++
        self.dynamic_widget = QWidget()
        self.dynamic_layout = QVBoxLayout(self.dynamic_widget)
        self.dynamic_layout.setContentsMargins(30, 30, 30, 30)

        self.placeholder = QLabel("Sélectionnez un module pour voir les détails")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color: #94a3b8; font-size: 16px;")

        self.detail_layout.addWidget(self.placeholder)
        self.detail_layout.addWidget(self.dynamic_widget)
        self.dynamic_widget.hide()

        self.content_container.addWidget(self.module_list)
        self.content_container.addWidget(self.detail_frame, 1)
        self.main_layout.addLayout(self.content_container)

    def _create_stat_card(self, title, value, color):
        card = QFrame()
        card.setFixedSize(280, 110)
        card.setStyleSheet(f"background-color: white; border-radius: 12px; border-left: 6px solid {color};")
        self._add_shadow(card)
        
        lay = QVBoxLayout(card)
        t = QLabel(title.upper())
        t.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        v = QLabel(value)
        v.setObjectName("val")
        v.setStyleSheet("color: #1e293b; font-size: 32px; font-weight: 800;")
        
        lay.addWidget(t)
        lay.addWidget(v)
        return card

    def _add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 8)
        widget.setGraphicsEffect(shadow)

    def get_all_modules(self):
        modules = []
        addons_path = os.path.join(os.getcwd(), "addons")
        if not os.path.exists(addons_path): return []
        for folder in os.listdir(addons_path):
            folder_path = os.path.join(addons_path, folder)
            manifest = os.path.join(folder_path, "manifest.json")
            if os.path.isdir(folder_path) and not folder.startswith("."):
                m_data = {"name": folder, "version": "1.0", "author": "Inconnu", "description": "", "installable": True, "folder_name": folder}
                if os.path.exists(manifest):
                    try:
                        with open(manifest, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data.get("description"), list): data["description"] = " ".join(data["description"])
                            m_data.update(data)
                    except: pass
                modules.append(m_data)
        return modules

    def refresh_data(self):
        self.module_list.clear()
        mods = self.get_all_modules()
        active = 0
        for m in mods:
            if m.get('installable'): active += 1
            item = QListWidgetItem(m['name'])
            item.setData(Qt.UserRole, m)
            self.module_list.addItem(item)
        
        self.card_total.findChild(QLabel, "val").setText(str(len(mods)))
        self.card_active.findChild(QLabel, "val").setText(str(active))

    def display_module_details(self, index):
        if index < 0: return
        self.placeholder.hide()
        self.dynamic_widget.show()
        
        while self.dynamic_layout.count():
            w = self.dynamic_layout.takeAt(0).widget()
            if w: w.deleteLater()

        mod = self.module_list.currentItem().data(Qt.UserRole)

        # --- UI DESIGN ---
        title = QLabel(mod['name'])
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #1e293b;")
        
        meta = QLabel(f"Version {mod['version']}  •  Par {mod['author']}")
        meta.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")
        
        self.dynamic_layout.addWidget(title)
        self.dynamic_layout.addWidget(meta)
        self.dynamic_layout.addSpacing(20)

        # Description Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: #fcfcfc; border-radius: 10px;")
        desc = QLabel(mod['description'] or "Aucune description disponible.")
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 20px; color: #475569; font-size: 15px; line-height: 160%;")
        scroll.setWidget(desc)
        self.dynamic_layout.addWidget(scroll, 1)

        # Dependencies
        self.dynamic_layout.addSpacing(15)
        deps = QLabel(f"<b>Dépendances :</b> {', '.join(mod.get('depends', [])) or 'Aucune'}")
        deps.setStyleSheet("color: #64748b; font-size: 12px;")
        self.dynamic_layout.addWidget(deps)

        # Actions
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 20, 0, 0)
        
        btn_about = QPushButton("🌐 Visiter le site du développeur")
        btn_about.setCursor(Qt.PointingHandCursor)
        btn_about.setStyleSheet("background: #f1f5f9; color: #1e293b; padding: 10px 18px; border-radius: 8px; font-weight: 600;")
        btn_about.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(mod.get('website', 'https://universalhouse.org'))))

        is_installed = mod.get('installable', True)
        btn_action = QPushButton("Désinstaller le module" if is_installed else "Réactiver le module")
        btn_action.setCursor(Qt.PointingHandCursor)
        color = "#ef4444" if is_installed else "#10b981"
        btn_action.setStyleSheet(f"background: {color}; color: white; padding: 10px 22px; border-radius: 8px; font-weight: 700;")
        btn_action.clicked.connect(lambda: self.toggle_status(mod['folder_name'], is_installed))

        footer.addWidget(btn_about)
        footer.addStretch()
        footer.addWidget(btn_action)
        self.dynamic_layout.addLayout(footer)

    def toggle_status(self, folder, current):
        path = os.path.join(os.getcwd(), "addons", folder, "manifest.json")
        try:
            with open(path, 'r') as f: data = json.load(f)
            data["installable"] = not current
            with open(path, 'w') as f: json.dump(data, f, indent=4)
            self.refresh_data()
        except Exception as e: QMessageBox.critical(self, "Erreur", str(e))

    def import_zip_module(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importer un pack de module", "", "Zip (*.zip)")
        if not path: return
        try:
            with zipfile.ZipFile(path, 'r') as z:
                z.extractall(os.path.join(os.getcwd(), "addons"))
            self.refresh_data()
            QMessageBox.information(self, "Succès", "Le module a été ajouté à la bibliothèque.")
        except Exception as e: QMessageBox.critical(self, "Erreur", f"Le pack est corrompu : {e}")