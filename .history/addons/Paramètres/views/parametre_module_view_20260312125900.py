from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QFrame)
from PySide6.QtCore import Qt

class ParametreModuleWidget(QWidget):
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setup_ui()
        self.refresh_list()

    def _create_stat_card(self, title, color):
        card = QFrame()
        card.setObjectName("StatCard")
        card.setFixedHeight(90)
        card.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: white; border-radius: 12px;
                border: 1px solid #e2e8f0; border-left: 5px solid {color};
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        layout = QVBoxLayout(card)
        t_lbl = QLabel(title.upper())
        t_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800;")
        v_lbl = QLabel("--")
        v_lbl.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800;")
        layout.addWidget(t_lbl)
        layout.addWidget(v_lbl)
        card.val_lbl = v_lbl
        return card

    def setup_ui(self):
        self.setStyleSheet("background-color: #f8fafc;")
        main_layout = QVBoxLayout(self)
        
        # Dashboard
        stats_layout = QHBoxLayout()
        self.card_total = self._create_stat_card("Modules installés", "#3b82f6")
        self.card_size = self._create_stat_card("Espace utilisé", "#f59e0b")
        stats_layout.addWidget(self.card_total)
        stats_layout.addWidget(self.card_size)
        main_layout.addLayout(stats_layout)

        # Contenu
        content_layout = QHBoxLayout()
        
        # Liste (Gauche)
        self.module_list = QListWidget()
        self.module_list.setStyleSheet("""
            QListWidget { background: white; border-radius: 12px; border: 1px solid #e2e8f0; outline: none; }
            QListWidget::item { padding: 15px; border-bottom: 1px solid #f1f5f9; }
            QListWidget::item:selected { background: #eff6ff; color: #2563eb; font-weight: bold; border-radius: 8px; }
        """)
        self.module_list.currentRowChanged.connect(self.display_details)
        content_layout.addWidget(self.module_list, 1)

        # Détails (Droite)
        self.detail_card = QFrame()
        self.detail_card.setObjectName("DetailCard")
        self.detail_card.setStyleSheet("""
            QFrame#DetailCard { background: white; border-radius: 12px; border: 1px solid #e2e8f0; }
            QLabel { border: none; background: transparent; }
        """)
        
        detail_inner = QVBoxLayout(self.detail_card)
        detail_inner.setContentsMargins(30, 30, 30, 30)

        self.lbl_name = QLabel("Sélectionnez un module")
        self.lbl_name.setStyleSheet("font-size: 22px; font-weight: 800; color: #0f172a;")
        
        self.lbl_desc = QLabel("")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #475569; font-size: 14px; line-height: 150%;")

        # Zone Dépendances
        self.dep_layout = QHBoxLayout()
        self.dep_layout.addStretch()

        self.btn_uninstall = QPushButton("🗑️ Désinstaller")
        self.btn_uninstall.setFixedSize(130, 35)
        self.btn_uninstall.setStyleSheet("background: #fff1f2; color: #e11d48; border-radius: 6px; font-weight: bold;")
        self.btn_uninstall.clicked.connect(self.on_uninstall_clicked)
        self.btn_uninstall.hide()

        detail_inner.addWidget(self.lbl_name)
        detail_inner.addSpacing(10)
        detail_inner.addWidget(self.lbl_desc)
        detail_inner.addLayout(self.dep_layout)
        detail_inner.addStretch()
        detail_inner.addWidget(self.btn_uninstall, 0, Qt.AlignRight)

        content_layout.addWidget(self.detail_card, 2)
        main_layout.addLayout(content_layout)

    def display_details(self, row):
        if row < 0: return
        mod = self.module_list.item(row).data(Qt.UserRole)
        
        self.lbl_name.setText(mod.get('name', 'Module'))
        self.lbl_desc.setText(mod.get('description', 'Pas de description.'))
        
        # --- SÉCURITÉ ANTI-SUPPRESSION ---
        folder = mod.get('folder_name', '').lower()
        # On cache le bouton si c'est le module Paramètres ou Core
        is_system = folder in ["paramètres", "parametre", "settings", "core"]
        self.btn_uninstall.setVisible(not is_system)
        
    def refresh_list(self):
        self.module_list.clear()
        modules = self.controller.get_all_modules()
        for mod in modules:
            item = QListWidgetItem(f"📦 {mod['name']}")
            item.setData(Qt.UserRole, mod)
            self.module_list.addItem(item)

    def on_uninstall_clicked(self):
        # Ici on ajoutera la logique de confirmation
        pass