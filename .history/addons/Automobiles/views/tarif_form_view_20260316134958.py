from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QScrollArea, 
                             QGridLayout, QWidget, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class CompanyTarifForm(QDialog):
    def __init__(self, parent=None, controller=None, current_user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = current_user
        
        # --- CONFIGURATION SANS BORDURES (LOOK AIR) ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(950)
        self.setFixedHeight(850)
        
        self.inputs = {} # Dictionnaire pour stocker les références des champs
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

        # CONTENEUR CARTE BLANCHE
        self.container = QFrame()
        self.container.setStyleSheet("background-color: white; border-radius: 25px; border: none;")
        self._add_soft_shadow(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- HEADER (Comme sur la photo) ---
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

        # --- ZONE SCROLLABLE (Pour tous les champs de l'image) ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content = QWidget()
        s_lay = QVBoxLayout(content)
        s_lay.setContentsMargins(35, 10, 35, 30)
        s_lay.setSpacing(30)

        # 1. IDENTIFICATION (Cie, Libellé, Zone, Catégorie)
        s_lay.addWidget(self._lbl_sec("IDENTIFICATION & LOCALISATION"))
        grid_id = QGridLayout()
        grid_id.addWidget(self._reg_input("Cie", "Code Compagnie", "1111"), 0, 0)
        grid_id.addWidget(self._reg_input("Nom_Cie", "Nom Compagnie", "SANLAM"), 0, 1)
        grid_id.addWidget(self._reg_input("Lib_Tarif", "Libellé du Tarif", "AMBULANCES..."), 1, 0)
        grid_id.addWidget(self._reg_input("Categorie", "Catégorie", "0800"), 1, 1)
        grid_id.addWidget(self._reg_input("Zone", "Zone Géographique", "A"), 2, 0)
        grid_id.addWidget(self._reg_input("Nbre_Place", "Nombre de Places", "5"), 2, 1)
        s_lay.addLayout(grid_id)

        # 2. GRILLE DES PRIMES RC (1 à 10 comme sur l'image)
        s_lay.addWidget(self._lbl_sec("PRIMES DE RÉFÉRENCE (PRIME 1 À 10)"))
        grid_primes = QGridLayout()
        for i in range(1, 11):
            grid_primes.addWidget(self._reg_input(f"Prime{i}", f"Prime {i}", "0.0"), (i-1)//5, (i-1)%5)
        s_lay.addLayout(grid_primes)

        # 3. OPTIONS : REMORQUAGE
        s_lay.addWidget(self._lbl_sec("OPTIONS REMORQUAGE"))
        grid_rem = QGridLayout()
        for i in range(1, 11):
            grid_rem.addWidget(self._reg_input(f"Remorq{i}", f"Remorquage {i}", "0.0"), (i-1)//5, (i-1)%5)
        s_lay.addLayout(grid_rem)

        # 4. ÉNERGIE : ESSENCE & DIESEL (Sections de l'image)
        s_lay.addWidget(self._lbl_sec("TARIFICATION PAR ÉNERGIE (ESSENCE / DIESEL)"))
        grid_energy = QGridLayout()
        for i in range(1, 6): # Exemple pour les 5 premières tranches
            grid_energy.addWidget(self._reg_input(f"Essence{i}", f"Essence {i}", "0.0"), i-1, 0)
            grid_energy.addWidget(self._reg_input(f"Diesel{i}", f"Diesel {i}", "0.0"), i-1, 1)
        s_lay.addLayout(grid_energy)

        # 5. LIMITES (Max Corpo, Max Matériel)
        s_lay.addWidget(self._lbl_sec("LIMITES DE RESPONSABILITÉ"))
        grid_limit = QGridLayout()
        grid_limit.addWidget(self._reg_input("Max_Corpo", "Max Corporel", "Illimité"), 0, 0)
        grid_limit.addWidget(self._reg_input("Max_Materiel", "Max Matériel", "0.0"), 0, 1)
        s_lay.addLayout(grid_limit)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # --- FOOTER ---
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

    def _reg_input(self, key, label, placeholder):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(5)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 700; border: none;")
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(40)
        edit.setStyleSheet("""
            QLineEdit {
                background: #f8fafc; border: none; border-bottom: 2px solid #f1f5f9;
                border-radius: 8px; padding-left: 12px; color: #1e293b;
            }
            QLineEdit:focus { border-bottom: 2px solid #3b82f6; background: white; }
        """)
        l.addWidget(lbl)
        l.addWidget(edit)
        self.inputs[key] = edit
        return w

    def get_data(self):
        """Récupère dynamiquement toutes les valeurs pour le contrôleur"""
        return {key: edit.text() for key, edit in self.inputs.items()}