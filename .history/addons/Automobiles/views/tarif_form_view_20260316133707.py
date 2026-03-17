from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QScrollArea, 
                             QGridLayout, QWidget, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class CompanyTariffView(QDialog):
    def __init__(self, controller, contact_data=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.controller = controller
        self.contact_data = contact_data
        self.setMinimumWidth(850)
        self.setFixedHeight(750)
        
        self.setup_ui()

    def _add_soft_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 10)
        widget.setGraphicsEffect(shadow)

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # CONTENEUR CARTE (BLANC PUR)
        self.container = QFrame()
        self.container.setStyleSheet("background-color: white; border-radius: 25px; border: none;")
        self._add_soft_shadow(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- HEADER (TITRE + BOUTON X) ---
        header = QWidget()
        header.setFixedHeight(75)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(35, 0, 35, 0)
        
        title = QLabel("Configuration du Barème")
        title.setStyleSheet("font-size: 22px; font-weight: 900; color: #0f172a; border: none;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject) 
        self.btn_close.setStyleSheet("""
            QPushButton { background: #f8fafc; border-radius: 17px; color: #64748b; border: none; font-weight: bold; }
            QPushButton:hover { background: #fee2e2; color: #ef4444; }
        """)
        h_lay.addWidget(title)
        h_lay.addStretch()
        h_lay.addWidget(self.btn_close)
        layout.addWidget(header)

        # --- ZONE SCROLLABLE (Pour les nombreux champs du barème) ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content = QWidget()
        s_lay = QVBoxLayout(content)
        s_lay.setContentsMargins(35, 10, 35, 30)
        s_lay.setSpacing(25)

        # 1. Identification
        s_lay.addWidget(self._lbl_sec("IDENTIFICATION DU BARÈME"))
        grid_id = QGridLayout()
        self.cie_nom = self._create_input("Compagnie", "ex: SANLAM")
        self.lib_tarif = self._create_input("Libellé du Tarif", "ex: AMBULANCES ZONE A")
        grid_id.addWidget(self.cie_nom, 0, 0)
        grid_id.addWidget(self.lib_tarif, 0, 1)
        s_lay.addLayout(grid_id)

        # 2. Paramètres (Zone et Catégorie)
        s_lay.addWidget(self._lbl_sec("ZONE & CATÉGORIE"))
        grid_tech = QGridLayout()
        self.zone = self._create_input("Zone Géographique", "A, B ou C")
        self.cat = self._create_input("Code Catégorie", "0800")
        grid_tech.addWidget(self.zone, 0, 0)
        grid_tech.addWidget(self.cat, 0, 1)
        s_lay.addLayout(grid_tech)

        # 3. Grille des Primes (Prime 1 à Prime 6)
        s_lay.addWidget(self._lbl_sec("GRILLE DES PRIMES (RC)"))
        grid_primes = QGridLayout()
        self.inputs_primes = {}
        for i in range(1, 7):
            inp = self._create_input(f"Prime {i}", "0.0")
            self.inputs_primes[f"p{i}"] = inp
            grid_primes.addWidget(inp, (i-1)//3, (i-1)%3)
        s_lay.addLayout(grid_primes)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # --- FOOTER (BOUTON ENREGISTRER) ---
        footer = QFrame()
        footer.setFixedHeight(100)
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(35, 0, 35, 0)
        
        self.btn_save = QPushButton("ENREGISTRER LE BARÈME")
        self.btn_save.setFixedHeight(55)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0f172a; color: white; font-weight: 800;
                border-radius: 15px; border: none; font-size: 14px;
            }
            QPushButton:hover { background-color: #1e293b; }
        """)
        self.btn_save.clicked.connect(self.accept) 
        
        f_lay.addWidget(self.btn_save)
        layout.addWidget(footer)

        self.main_layout.addWidget(self.container)

    def _lbl_sec(self, text):
        l = QLabel(text)
        l.setStyleSheet("color: #3b82f6; font-size: 10px; font-weight: 900; letter-spacing: 1.5px; border: none;")
        return l

    def _create_input(self, label, placeholder):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(5)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 700; border: none;")
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(42)
        edit.setStyleSheet("""
            QLineEdit {
                background: #f8fafc; border: none; border-bottom: 2px solid #f1f5f9;
                border-radius: 8px; padding-left: 12px; color: #1e293b; font-size: 13px;
            }
            QLineEdit:focus { border-bottom: 2px solid #3b82f6; background: white; }
        """)
        l.addWidget(lbl)
        l.addWidget(edit)
        return w

    def get_data(self):
        """Récupération propre des valeurs"""
        return {
            "Nom_Cie": self.cie_nom.findChild(QLineEdit).text(),
            "Lib_Tarif": self.lib_tarif.findChild(QLineEdit).text(),
            "Zone": self.zone.findChild(QLineEdit).text(),
            "Categorie": self.cat.findChild(QLineEdit).text(),
            "Primes": [self.inputs_primes[f"p{i}"].findChild(QLineEdit).text() for i in range(1, 7)]
        }