from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect, 
                             QComboBox, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class FormulaireCreationTarif(QDialog):
    def __init__(self, parent=None, controller=None, current_user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = current_user
        
        # --- CONFIGURATION DU DIALOGUE (LOOK MODERNE SANS CADRE) ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()

    def _add_glow_effect(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 10)
        widget.setGraphicsEffect(shadow)

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)

        # --- CONTENEUR PRINCIPAL ---
        self.container = QFrame()
        self.container.setFixedWidth(750) # Plus large pour le tableau
        self.container.setStyleSheet("background-color: white; border-radius: 10px; border: none;")
        self._add_glow_effect(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(25)

        # --- HEADER ---
        top_bar = QHBoxLayout()
        title = QLabel("Configuration du Barème")
        title.setStyleSheet("font-size: 24px; font-weight: 900; color: #0f172a; border: none;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.clicked.connect(self.reject)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc; color: #64748b; 
                border-radius: 17px; font-size: 14px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #fee2e2; color: #ef4444; }
        """)
        
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_close)
        layout.addLayout(top_bar)

        # --- INFOS GÉNÉRALES ---
        info_layout = QHBoxLayout()
        self.nom_tarif = self._create_modern_field("Nom du Barème", "ex: Tarif Flotte 2026")
        self.type_vehicule = self._create_modern_field("Catégorie", "ex: Véhicules Légers")
        info_layout.addWidget(self.nom_tarif)
        info_layout.addWidget(self.type_vehicule)
        layout.addLayout(info_layout)

        # --- SECTION GRILLE TARIFAIRE ---
        grid_section = QVBoxLayout()
        grid_section.setSpacing(15)
        
        grid_header = QHBoxLayout()
        grid_label = QLabel("DÉTAILS DES GARANTIES")
        grid_label.setStyleSheet("color: #3b82f6; font-size: 10px; font-weight: 900; letter-spacing: 2px;")
        
        self.btn_add_row = QPushButton("+ Ajouter une ligne")
        self.btn_add_row.setCursor(Qt.PointingHandCursor)
        self.btn_add_row.setStyleSheet("""
            QPushButton { color: #3b82f6; font-weight: 800; background: transparent; border: none; font-size: 12px; }
            QPushButton:hover { color: #1d4ed8; }
        """)
        self.btn_add_row.clicked.connect(self.add_row)
        
        grid_header.addWidget(grid_label)
        grid_header.addStretch()
        grid_header.addWidget(self.btn_add_row)
        grid_section.addLayout(grid_header)

        # Tableau "Zero Border"
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Garantie", "Calcul", "Valeur"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False) # Pas de lignes de grille
        self.table.setFixedHeight(200)
        self.table.setStyleSheet("""
            QTableWidget { background-color: transparent; border: none; font-size: 13px; }
            QHeaderView::section {
                background-color: transparent; border: none;
                border-bottom: 2px solid #f1f5f9;
                color: #cbd5e1; font-weight: 800; font-size: 10px;
                padding-bottom: 8px; text-transform: uppercase;
            }
        """)
        grid_section.addWidget(self.table)
        layout.addLayout(grid_section)

        # --- BOUTON SAUVEGARDE ---
        self.btn_save = QPushButton("ENREGISTRER LE BARÈME")
        self.btn_save.setFixedHeight(55)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0f172a; color: white; font-weight: 800;
                border-radius: 15px; font-size: 14px; border: none;
            }
            QPushButton:hover { background-color: #1e293b; }
        """)
        layout.addWidget(self.btn_save)

        self.main_layout.addWidget(self.container)

    def _create_modern_field(self, label, placeholder):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(5)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 800; text-transform: uppercase; border: none;")
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(45)
        edit.setStyleSheet("""
            QLineEdit {
                background-color: #f8fafc; border: none; border-bottom: 2px solid #f1f5f9; 
                border-radius: 8px; padding-left: 15px; color: #1e293b;
            }
            QLineEdit:focus { border-bottom: 2px solid #3b82f6; background-color: white; }
        """)
        l.addWidget(lbl)
        l.addWidget(edit)
        return w

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Combo Method
        c = QComboBox()
        c.addItems(["Taux (%)", "Forfait Fixe"])
        c.setStyleSheet("background: #f8fafc; border: none; border-radius: 6px; padding: 4px;")
        
        item_name = QTableWidgetItem("Nom garantie...")
        item_val = QTableWidgetItem("0.00")
        
        self.table.setItem(row, 0, item_name)
        self.table.setCellWidget(row, 1, c)
        self.table.setItem(row, 2, item_val)

    def get_data(self):
        """Récupère les tarifs pour le dictionnaire final"""
        tarifs = []
        for i in range(self.table.rowCount()):
            tarifs.append({
                "garantie": self.table.item(i, 0).text(),
                "methode": self.table.cellWidget(i, 1).currentText(),
                "valeur": self.table.item(i, 2).text()
            })
        return {
            "nom_bareme": self.nom_tarif.findChild(QLineEdit).text(),
            "categorie": self.type_vehicule.findChild(QLineEdit).text(),
            "details": tarifs
        }