from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect, 
                             QComboBox, QScrollArea)
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
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 5)
        widget.setGraphicsEffect(shadow)

    def setup_ui(self):
        # Fond Slate 50
        self.setStyleSheet("background-color: #f8fafc;")
        
        # On utilise un ScrollArea pour que le formulaire soit responsive
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        main_container = QWidget()
        main_container.setStyleSheet("background: transparent;")
        scroll.setWidget(main_container)
        
        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(100, 40, 100, 40) # Larges marges pour centrer le formulaire
        layout.setSpacing(30)

        # --- TITRE ---
        header = QVBoxLayout()
        t = QLabel("Fiche de Partenariat")
        t.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a;")
        st = QLabel("Remplissez les informations pour enregistrer une nouvelle compagnie.")
        st.setStyleSheet("color: #64748b; font-size: 14px;")
        header.addWidget(t)
        header.addWidget(st)
        layout.addLayout(header)

        # --- BLOC 1 : IDENTITÉ ---
        card_id = QFrame()
        card_id.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e2e8f0;")
        self._add_shadow(card_id)
        
        lay_id = QVBoxLayout(card_id)
        lay_id.setContentsMargins(30, 30, 30, 30)
        lay_id.setSpacing(15)
        
        lay_id.addWidget(self._title("🏢 Information de la Compagnie"))
        
        row1 = QHBoxLayout()
        self.nom = self._input("Nom complet de la compagnie")
        self.code = self._input("Code unique (ex: AXA-01)")
        row1.addWidget(self.nom)
        row1.addWidget(self.code)
        
        row2 = QHBoxLayout()
        self.email = self._input("Email contact")
        self.tel = self._input("Téléphone")
        row2.addWidget(self.email)
        row2.addWidget(self.tel)
        
        lay_id.addLayout(row1)
        lay_id.addLayout(row2)
        lay_id.addWidget(self._input("Adresse du siège social"))
        
        layout.addWidget(card_id)

        # --- BLOC 2 : TARIFICATION ---
        card_tarif = QFrame()
        card_tarif.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e2e8f0;")
        self._add_shadow(card_tarif)
        
        lay_tarif = QVBoxLayout(card_tarif)
        lay_tarif.setContentsMargins(30, 30, 30, 30)
        
        head_t = QHBoxLayout()
        head_t.addWidget(self._title("📊 Grille des Tarifs"))
        head_t.addStretch()
        btn_row = QPushButton("+ Ajouter une garantie")
        btn_row.setCursor(Qt.PointingHandCursor)
        btn_row.setStyleSheet("color: #2563eb; font-weight: bold; border: none; background: transparent;")
        btn_row.clicked.connect(self.add_row)
        head_t.addWidget(btn_row)
        lay_tarif.addLayout(head_t)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Garantie", "Type de Tarif", "Valeur par défaut"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setFixedHeight(250) # Hauteur fixe pour le tableau
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("QTableWidget { border: 1px solid #f1f5f9; border-radius: 4px; }")
        lay_tarif.addWidget(self.table)

        layout.addWidget(card_tarif)

        # --- BOUTON FINAL ---
        self.btn_save = QPushButton("CRÉER LE PARTENAIRE")
        self.btn_save.setFixedHeight(50)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; font-weight: 800;
                border-radius: 8px; font-size: 14px; margin-top: 10px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        layout.addWidget(self.btn_save)
        
        # Layout principal de la vue
        v_main = QVBoxLayout(self)
        v_main.setContentsMargins(0,0,0,0)
        v_main.addWidget(scroll)

    def _title(self, text):
        l = QLabel(text)
        l.setStyleSheet("font-size: 15px; font-weight: 700; color: #1e293b; margin-bottom: 5px;")
        return l

    def _input(self, placeholder):
        e = QLineEdit()
        e.setPlaceholderText(placeholder)
        e.setFixedHeight(42)
        e.setStyleSheet("""
            QLineEdit {
                background: #f8fafc; border: 1px solid #e2e8f0; 
                border-radius: 6px; padding-left: 12px; color: #1e293b;
            }
            QLineEdit:focus { border: 2px solid #3b82f6; background: white; }
        """)
        return e

    def add_row(self):
        r = self.table.rowCount()
        self.table.insertRow(r)
        c = QComboBox()
        c.addItems(["Taux (%)", "Montant Fixe"])
        self.table.setItem(r, 0, QTableWidgetItem("Garantie..."))
        self.table.setCellWidget(r, 1, c)
        self.table.setItem(r, 2, QTableWidgetItem("0.0"))