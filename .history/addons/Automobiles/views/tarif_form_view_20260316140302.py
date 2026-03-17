from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QScrollArea, 
                             QGridLayout, QWidget, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class CompanyTariffView(QDialog):
    def __init__(self, parent=None, controller=None, current_user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = current_user
        
        # --- CONFIGURATION SANS BORDURES (LOOK AIR) ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(1100) # Élargi pour accueillir les 5 colonnes
        self.setFixedHeight(850)
        
        self.inputs = {} 
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.container = QFrame()
        self.container.setStyleSheet("background-color: white; border-radius: 25px; border: none;")
        shadow = QGraphicsDropShadowEffect(blurRadius=40, xOffset=0, yOffset=10, color=QColor(0,0,0,25))
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- HEADER ---
        header = QWidget()
        header.setFixedHeight(75)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(35, 0, 35, 0)
        title = QLabel("Matrice Tarifaire Complète")
        title.setStyleSheet("font-size: 22px; font-weight: 900; color: #0f172a;")
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(35, 35)
        btn_close.clicked.connect(self.reject)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("QPushButton { background: #f8fafc; border-radius: 17px; color: #64748b; border: none; font-weight: bold; } QPushButton:hover { background: #fee2e2; color: #ef4444; }")
        
        h_lay.addWidget(title)
        h_lay.addStretch()
        h_lay.addWidget(btn_close)
        layout.addWidget(header)

        # --- ZONE SCROLLABLE ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content = QWidget()
        s_lay = QVBoxLayout(content)
        s_lay.setContentsMargins(35, 10, 35, 30)
        s_lay.setSpacing(30)

        # 1. IDENTIFICATION RAPIDE
        s_lay.addWidget(self._lbl_sec("INFORMATIONS GÉNÉRALES"))
        grid_id = QGridLayout()
        grid_id.addWidget(self._reg_input("Nom_Cie", "Compagnie", "SANLAM"), 0, 0)
        grid_id.addWidget(self._reg_input("Lib_Tarif", "Libellé Barème", "AMBULANCES..."), 0, 1)
        grid_id.addWidget(self._reg_input("Zone", "Zone", "A"), 0, 2)
        grid_id.addWidget(self._reg_input("Categorie", "Code Cat.", "0800"), 0, 3)
        s_lay.addLayout(grid_id)

        # --- GRILLE MAÎTRESSE (PRIME, REMORQUE, INFLAM., ESSENCE, DIESEL) ---
        s_lay.addWidget(self._lbl_sec("TABLEAU DE SAISIE DES PARAMÈTRES (1 À 10)"))
        
        grid_main = QGridLayout()
        grid_main.setSpacing(8)

        # En-têtes des 5 colonnes de données (+ 1 colonne index)
        headers = ["N°", "PRIME RC", "REMORQUAGE", "INFLAMMABLE", "ESSENCE", "DIESEL"]
        for col, text in enumerate(headers):
            h_lbl = QLabel(text)
            h_lbl.setStyleSheet("color: #64748b; font-size: 9px; font-weight: 900; padding-bottom: 5px; letter-spacing: 0.5px;")
            h_lbl.setAlignment(Qt.AlignCenter if col > 0 else Qt.AlignLeft)
            grid_main.addWidget(h_lbl, 0, col)

        # Génération des 10 lignes pour couvrir l'intégralité du CSV
        for i in range(1, 11):
            # Index de ligne
            row_lbl = QLabel(f"{i}")
            row_lbl.setStyleSheet("color: #94a3b8; font-weight: 800; font-size: 11px;")
            grid_main.addWidget(row_lbl, i, 0)

            # Les 5 colonnes de saisie par ligne
            grid_main.addWidget(self._create_grid_cell(f"Prime{i}"), i, 1)
            grid_main.addWidget(self._create_grid_cell(f"Remorq{i}"), i, 2)
            grid_main.addWidget(self._create_grid_cell(f"Inflamble{i}"), i, 3)
            grid_main.addWidget(self._create_grid_cell(f"Essence{i}"), i, 4)
            grid_main.addWidget(self._create_grid_cell(f"Diesel{i}"), i, 5)

        s_lay.addLayout(grid_main)

        # 3. LIMITES DE RESPONSABILITÉ
        s_lay.addWidget(self._lbl_sec("LIMITES DE RESPONSABILITÉ"))
        grid_lim = QHBoxLayout()
        grid_lim.addWidget(self._reg_input("Max_Corpo", "Max Corporel", "Illimité"))
        grid_lim.addWidget(self._reg_input("Max_Materiel", "Max Matériel", "0.0"))
        s_lay.addLayout(grid_lim)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # --- FOOTER ---
        footer = QFrame()
        footer.setFixedHeight(90)
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(35, 0, 35, 0)
        btn_save = QPushButton("ENREGISTRER LE BARÈME")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setFixedHeight(50)
        btn_save.setStyleSheet("QPushButton { background-color: #0f172a; color: white; font-weight: 800; border-radius: 12px; } QPushButton:hover { background-color: #1e293b; }")
        btn_save.clicked.connect(self.accept)
        f_lay.addWidget(btn_save)
        layout.addWidget(footer)

        self.main_layout.addWidget(self.container)

    def _lbl_sec(self, text):
        l = QLabel(text)
        l.setStyleSheet("color: #3b82f6; font-size: 10px; font-weight: 900; letter-spacing: 1px; border: none;")
        return l

    def _create_grid_cell(self, key):
        edit = QLineEdit()
        edit.setPlaceholderText("0.0")
        edit.setFixedHeight(35)
        edit.setAlignment(Qt.AlignCenter)
        edit.setStyleSheet("""
            QLineEdit {
                background: #f8fafc; border: 1px solid #f1f5f9;
                border-radius: 6px; color: #1e293b; font-size: 12px;
            }
            QLineEdit:focus { border: 1px solid #3b82f6; background: white; }
        """)
        self.inputs[key] = edit
        return edit

    def _reg_input(self, key, label, placeholder):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0,0,0,0); l.setSpacing(4)
        lbl = QLabel(label); lbl.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 700;")
        edit = QLineEdit(); edit.setPlaceholderText(placeholder); edit.setFixedHeight(40)
        edit.setStyleSheet("QLineEdit { background: #f8fafc; border: none; border-bottom: 2px solid #f1f5f9; border-radius: 8px; padding-left: 12px; } QLineEdit:focus { border-bottom: 2px solid #3b82f6; background: white; }")
        l.addWidget(lbl); l.addWidget(edit)
        self.inputs[key] = edit
        return w

    def get_data(self):
        return {k: v.text() for k, v in self.inputs.items()}