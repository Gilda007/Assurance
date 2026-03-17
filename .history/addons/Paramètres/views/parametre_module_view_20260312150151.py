from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QFileDialog, 
                             QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont
import os

class ParametreModuleWidget(QWidget):
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        self.setStyleSheet("background-color: #f8fafc;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        # --- 1. ZONE DES CARTES (STATISTIQUES) ---
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)

        self.card_total = self._create_stat_card("Modules Totaux", "0", "#3b82f6")
        self.card_installed = self._create_stat_card("Modules Installés", "0", "#10b981")
        self.card_storage = self._create_stat_card("Espace Utilisé", "0 MB", "#f59e0b")

        self.stats_layout.addWidget(self.card_total)
        self.stats_layout.addWidget(self.card_installed)
        self.stats_layout.addWidget(self.card_storage)
        self.main_layout.addLayout(self.stats_layout)

        # --- 2. ZONE DE CONTENU (LISTE + DÉTAILS) ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(25)

        # Panneau Gauche
        left_panel = QVBoxLayout()
        self.btn_install = QPushButton("📥  Déployer une extension")
        self.btn_install.setFixedHeight(45)
        self.btn_install.setCursor(Qt.PointingHandCursor)
        self.btn_install.setStyleSheet("""
            QPushButton {
                background-color: #0f172a; color: white; border-radius: 10px;
                font-weight: 600; font-size: 13px; border: none;
            }
            QPushButton:hover { background-color: #1e293b; }
        """)
        self.btn_install.clicked.connect(self.on_install_clicked)

        self.module_list = QListWidget()
        self.module_list.setObjectName("ModernList")
        self.module_list.setSpacing(5)
        self.module_list.setStyleSheet("""
            QListWidget#ModernList { background-color: transparent; border: none; outline: none; }
            QListWidget#ModernList::item {
                background-color: white; border-radius: 10px; padding: 15px;
                color: #334155; border: 1px solid #e2e8f0; margin-bottom: 5px;
            }
            QListWidget#ModernList::item:selected {
                background-color: #ffffff; color: #2563eb; 
                border: 2px solid #3b82f6; font-weight: bold;
            }
        """)
        self.module_list.currentRowChanged.connect(self.display_details)

        left_panel.addWidget(self.btn_install)
        left_panel.addWidget(self.module_list)
        content_layout.addLayout(left_panel, 1)

        # Panneau Droit (Carte Détails)
        self.detail_card = QFrame()
        self.detail_card.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        
        detail_inner = QVBoxLayout(self.detail_card)
        detail_inner.setContentsMargins(40, 40, 40, 40)
        
        self.lbl_name = QLabel("Sélectionnez un module")
        self.lbl_name.setStyleSheet("font-size: 26px; font-weight: 800; color: #0f172a;")
        
        self.lbl_size_tag = QLabel("") # Affichera la taille
        self.lbl_size_tag.setStyleSheet("color: #64748b; font-weight: bold; font-size: 12px;")
        
        self.lbl_desc = QLabel("")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #475569; font-size: 14px; line-height: 160%; margin-top: 15px;")

        self.btn_uninstall = QPushButton("🗑️ Désinstaller")
        self.btn_uninstall.setFixedSize(140, 40)
        self.btn_uninstall.setStyleSheet("""
            QPushButton {
                background-color: #fff1f2; color: #e11d48; 
                border-radius: 8px; font-weight: 700; border: 1px solid #fecdd3;
            }
            QPushButton:hover { background-color: #ffe4e6; }
        """)
        self.btn_uninstall.clicked.connect(self.on_uninstall_clicked)
        self.btn_uninstall.hide()

        detail_inner.addWidget(self.lbl_name)
        detail_inner.addWidget(self.lbl_size_tag)
        detail_inner.addWidget(self.lbl_desc)
        detail_inner.addStretch()
        detail_inner.addWidget(self.btn_uninstall, 0, Qt.AlignRight)

        content_layout.addWidget(self.detail_card, 2)
        self.main_layout.addLayout(content_layout)

    def _create_stat_card(self, title, value, color):
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white; border-radius: 15px;
                border-left: 5px solid {color}; border: 1px solid #e2e8f0;
            }}
        """)
        
        # Ombre douce
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 10))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800; letter-spacing: 1px;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 900;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        
        # On attache le label de valeur à la carte pour pouvoir le modifier plus tard
        card.value_label = lbl_value 
        return card

    def refresh_data(self):
        self.module_list.clear()
        modules = self.get_all_modules()
        
        total_size = 0
        for mod in modules:
            size = mod.get('size', 0)
            total_size += size
            item = QListWidgetItem(f" 🧩 {mod['name']}")
            item.setData(Qt.UserRole, mod)
            self.module_list.addItem(item)

        # Mise à jour des cartes KPI
        self.card_total.val_lbl.setText(str(len(modules)))
        self.card_installed.val_lbl.setText(str(len(modules))) # À adapter selon votre logique
        self.card_storage.val_lbl.setText(f"{total_size / 1024:.1f} MB")

    def display_details(self, row):
        if row < 0: return
        mod = self.module_list.item(row).data(Qt.UserRole)
        self.lbl_name.setText(mod['name'])
        self.lbl_size_tag.setText(f"TAILLE SUR DISQUE : {mod.get('size', 0)} KB")
        self.lbl_desc.setText(mod.get('description', 'Aucune description.'))
        
        is_sys = mod['folder_name'].lower() in ["paramètre", "settings"]
        self.btn_uninstall.setVisible(not is_sys)

    def refresh_list(self):
        self.module_list.clear()
        modules = self.service.get_all_modules()
        for mod in modules:
            icon = mod.get('icon', '🧩')
            item = QListWidgetItem(f"  {icon}   {mod['name']}")
            item.setData(Qt.UserRole, mod)
            self.module_list.addItem(item)

    def display_details(self, row):
        if row < 0: return
        mod = self.module_list.item(row).data(Qt.UserRole)
        
        # Mise à jour sécurisée des widgets
        self.lbl_name.setText(mod['name'])
        # self.badge_version.setText(f"V {mod['version']}")
        self.lbl_desc.setText(mod.get('description', 'Aucune description.'))
        
        # Gestion bouton désinstaller
        is_system = mod['folder_name'].lower() in ["paramètre", "settings"]
        self.btn_uninstall.setVisible(not is_system)
        self.btn_uninstall.setProperty("folder", mod['folder_name'])
    
    def on_install_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importer Extension", "", "Archives (*.zip)")
        if path:
            success, msg = self.service.install_zip(path)
            if success:
                QMessageBox.information(self, "Système", "L'extension a été déployée avec succès.")
                self.refresh_list()
            else:
                QMessageBox.critical(self, "Erreur", f"Échec du déploiement : {msg}")


    def on_uninstall_clicked(self):
        folder = self.btn_uninstall.property("folder")
        confirm = QMessageBox.question(self, "Sécurité", 
                                     f"Voulez-vous vraiment supprimer le composant <b>{folder}</b> ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            # Appel service suppression
            pass