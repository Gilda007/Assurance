from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect, 
                             QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class FormulaireCreationCompagnie(QWidget):
    def __init__(self, controller=None, current_user=None):
        super().__init__()
        self.controller = controller
        self.user = current_user
        self.setup_ui()

    def _add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        widget.setGraphicsEffect(shadow)

    def setup_ui(self):
        # Configuration du conteneur principal
        self.setStyleSheet("background-color: #f8fafc;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- ZONE FORMULAIRE (HORIZONTAL) ---
        form_container = QHBoxLayout()
        form_container.setSpacing(20)

        # 1. BLOC IDENTITÉ (GAUCHE)
        card_info = QFrame()
        card_info.setFixedWidth(380)
        card_info.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e2e8f0;")
        self._add_shadow(card_info)
        
        layout_info = QVBoxLayout(card_info)
        layout_info.setContentsMargins(25, 25, 25, 25)
        layout_info.setSpacing(15)

        layout_info.addWidget(QLabel("<b>IDENTITÉ COMPAGNIE</b>"))
        
        self.nom = self._create_input("Nom de la compagnie")
        self.code = self._create_input("Code (ex: AXA-01)")
        self.email = self._create_input("Email contact")
        self.tel = self._create_input("Téléphone")
        self.adresse = self._create_input("Adresse")
        
        layout_info.addWidget(self.nom)
        layout_info.addWidget(self.code)
        layout_info.addWidget(self.email)
        layout_info.addWidget(self.tel)
        layout_info.addWidget(self.adresse)
        layout_info.addStretch()

        # 2. BLOC TARIFS (DROITE)
        card_tarif = QFrame()
        card_tarif.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e2e8f0;")
        self._add_shadow(card_tarif)
        
        layout_tarif = QVBoxLayout(card_tarif)
        layout_tarif.setContentsMargins(20, 20, 20, 20)

        header_tarif = QHBoxLayout()
        header_tarif.addWidget(QLabel("<b>GRILLE TARIFAIRE</b>"))
        header_tarif.addStretch()
        
        btn_add = QPushButton("+ Ajouter une ligne")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("color: #2563eb; font-weight: bold; border: none; background: transparent;")
        btn_add.clicked.connect(self.add_row)
        header_tarif.addWidget(btn_add)
        
        layout_tarif.addLayout(header_tarif)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Garantie", "Type", "Valeur"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("QTableWidget { border: none; gridline-color: #f1f5f9; }")
        
        layout_tarif.addWidget(self.table)

        # --- AJOUT AU LAYOUT ---
        form_container.addWidget(card_info)
        form_container.addWidget(card_tarif)
        layout.addLayout(form_container)

        # --- BOUTON DE VALIDATION ---
        self.btn_save = QPushButton("💾 ENREGISTRER LE PARTENAIRE")
        self.btn_save.setFixedHeight(50)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0f172a; color: white; font-weight: 800;
                border-radius: 8px; font-size: 14px;
            }
            QPushButton:hover { background-color: #1e293b; }
        """)
        layout.addWidget(self.btn_save)

    def _create_input(self, placeholder):
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(40)
        edit.setStyleSheet("""
            QLineEdit {
                background: #f8fafc; border: 1px solid #e2e8f0; 
                border-radius: 6px; padding-left: 10px;
            }
            QLineEdit:focus { border: 2px solid #3b82f6; background: white; }
        """)
        return edit

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        combo = QComboBox()
        combo.addItems(["Taux (%)", "Forfait Fixe"])
        
        self.table.setItem(row, 0, QTableWidgetItem("Nouvelle garantie"))
        self.table.setCellWidget(row, 1, combo)
        self.table.setItem(row, 2, QTableWidgetItem("0.0"))