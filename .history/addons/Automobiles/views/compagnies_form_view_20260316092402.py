from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect, 
                             QComboBox, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class FormulaireCreationCompagnie(QDialog):
    def __init__(self, controller=None, current_user=None):
        super().__init__()
        self.controller = controller
        self.user = current_user
        self.setup_ui()

    def setup_ui(self):
        # Fond très clair pour faire ressortir le blanc pur
        self.setStyleSheet("background-color: #f8fafc;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        scroll.setWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(80, 40, 80, 40)
        layout.setSpacing(40)

        # --- SECTION 1 : INFOS GÉNÉRALES ---
        section_info = QFrame()
        section_info.setStyleSheet("background: white; border-radius: 16px;")
        self._add_soft_shadow(section_info)
        
        lay_info = QVBoxLayout(section_info)
        lay_info.setContentsMargins(40, 40, 40, 40)
        lay_info.setSpacing(20)

        lay_info.addWidget(self._title("Enregistrement Compagnie"))
        
        # Champs sans bordures (uniquement un trait en bas au focus)
        self.nom = self._modern_input("Nom de la compagnie")
        self.code = self._modern_input("Code identifiant")
        self.email = self._modern_input("Email officiel")
        self.tel = self._modern_input("Contact téléphonique")
        
        lay_info.addWidget(self.nom)
        lay_info.addWidget(self.code)
        lay_info.addWidget(self.email)
        lay_info.addWidget(self.tel)
        layout.addWidget(section_info)

        # --- SECTION 2 : TARIFICATION (SANS BORDURES) ---
        section_tarif = QFrame()
        section_tarif.setStyleSheet("background: white; border-radius: 16px;")
        self._add_soft_shadow(section_tarif)
        
        lay_tarif = QVBoxLayout(section_tarif)
        lay_tarif.setContentsMargins(40, 40, 40, 40)
        
        head_t = QHBoxLayout()
        head_t.addWidget(self._title("Paramétrage des Tarifs"))
        head_t.addStretch()
        
        btn_add = QPushButton("+ Ajouter une garantie")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("color: #3b82f6; font-weight: 800; border: none; background: transparent; font-size: 13px;")
        btn_add.clicked.connect(self.add_row)
        head_t.addWidget(btn_add)
        lay_tarif.addLayout(head_t)

        # Configuration du tableau "Invisible"
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Désignation", "Type", "Valeur"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False) # SUPPRESSION DES LIGNES DE GRILLE
        
        # Style du tableau sans bordures
        self.table.setStyleSheet("""
            QTableWidget { 
                border: none; 
                background-color: white;
                selection-background-color: #eff6ff;
            }
            QHeaderView::section {
                background-color: white;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #f1f5f9;
                color: #94a3b8;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 10px;
            }
        """)
        lay_tarif.addWidget(self.table)
        layout.addWidget(section_tarif)

        # --- BOUTON DE VALIDATION ---
        self.btn_save = QPushButton("CRÉER LE PARTENAIRE")
        self.btn_save.setFixedHeight(55)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0f172a; color: white; font-weight: 800;
                border-radius: 12px; font-size: 14px; border: none;
            }
            QPushButton:hover { background-color: #1e293b; }
        """)
        layout.addWidget(self.btn_save)
        
        main_layout.addWidget(scroll)

    def _title(self, text):
        l = QLabel(text)
        l.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e293b;")
        return l

    def _modern_input(self, placeholder):
        e = QLineEdit()
        e.setPlaceholderText(placeholder)
        e.setFixedHeight(45)
        # Bordure uniquement en bas pour un look minimaliste
        e.setStyleSheet("""
            QLineEdit {
                background: #f8fafc; border: none;
                border-bottom: 2px solid #e2e8f0; 
                padding-left: 5px; color: #1e293b; font-size: 14px;
            }
            QLineEdit:focus { 
                border-bottom: 2px solid #3b82f6; 
                background: white; 
            }
        """)
        return e

    def _add_soft_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 10)) # Ombre très subtile
        shadow.setOffset(0, 10)
        widget.setGraphicsEffect(shadow)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        c = QComboBox()
        c.addItems(["Taux (%)", "Forfait Fixe"])
        c.setStyleSheet("border: 1px solid #f1f5f9; border-radius: 4px; padding: 5px;")
        
        # On enlève aussi les bordures des items du tableau
        item_name = QTableWidgetItem("Nom de la garantie...")
        self.table.setItem(row, 0, item_name)
        self.table.setCellWidget(row, 1, c)
        self.table.setItem(row, 2, QTableWidgetItem("0.0"))