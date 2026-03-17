from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QScrollArea, 
                             QComboBox, QGridLayout, QWidget, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class CompanyTariffView(QDialog):
    def __init__(self, parent=None, current_usercontroller=None):
        super().__init__(parent)
        self.controller = controller
        self.user = current_user
        
        # Configuration de la fenêtre (Look "Air" sans bordures)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(900)
        self.setMinimumHeight(700)
        
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        
        # --- CONTENEUR PRINCIPAL ---
        self.container = QFrame()
        self.container.setStyleSheet("background-color: white; border-radius: 25px; border: none;")
        shadow = QGraphicsDropShadowEffect(blurRadius=50, xOffset=0, yOffset=10)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)

        # 1. HEADER FIXE
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("background: white; border-top-left-radius: 25px; border-top-right-radius: 25px;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(40, 0, 40, 0)
        
        title_label = QLabel("Configuration Avancée du Tarif")
        title_label.setStyleSheet("font-size: 22px; font-weight: 900; color: #0f172a;")
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(35, 35)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.reject)
        btn_close.setStyleSheet("""
            QPushButton { background: #f8fafc; border-radius: 17px; color: #64748b; font-weight: bold; }
            QPushButton:hover { background: #fee2e2; color: #ef4444; }
        """)
        
        h_layout.addWidget(title_label)
        h_layout.addStretch()
        h_layout.addWidget(btn_close)
        layout.addWidget(header)

        # 2. ZONE SCROLLABLE (CONTENU)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 0, 40, 20)
        content_layout.setSpacing(30)

        # --- SECTION : IDENTIFICATION (Basé sur colonnes Cie, Nom_Cie, Lib_Tarif) ---
        content_layout.addWidget(self._create_section_title("IDENTIFICATION DU BARÈME"))
        grid_id = QGridLayout()
        grid_id.addWidget(self._create_input("Code Cie", "Cie"), 0, 0)
        grid_id.addWidget(self._create_input("Nom de la Compagnie", "Nom_Cie"), 0, 1)
        grid_id.addWidget(self._create_input("Libellé Tarif", "Lib_Tarif"), 1, 0)
        grid_id.addWidget(self._create_input("Catégorie", "Categorie"), 1, 1)
        content_layout.addLayout(grid_id)

        # --- SECTION : PARAMÈTRES TECHNIQUES (Zone, Essence/Diesel) ---
        content_layout.addWidget(self._create_section_title("PARAMÈTRES TECHNIQUES"))
        grid_tech = QGridLayout()
        
        zone_box = QComboBox()
        zone_box.addItems(["Zone A", "Zone B", "Zone C"])
        zone_box.setStyleSheet(self._combo_style())
        
        grid_tech.addWidget(QLabel("Zone Géographique"), 0, 0)
        grid_tech.addWidget(zone_box, 1, 0)
        grid_tech.addWidget(self._create_input("Nombre de Places", "Nbre Place"), 1, 1)
        content_layout.addLayout(grid_tech)

        # --- SECTION : GRILLE DES PRIMES (Prime 1 à Prime 6) ---
        content_layout.addWidget(self._create_section_title("GRILLE DES PRIMES (RC)"))
        grid_primes = QGridLayout()
        for i in range(1, 7):
            grid_primes.addWidget(self._create_input(f"Prime {i}", "0.00"), (i-1)//3, (i-1)%3)
        content_layout.addLayout(grid_primes)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # 3. FOOTER (ACTION)
        footer = QFrame()
        footer.setFixedHeight(100)
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(40, 0, 40, 0)
        
        self.btn_save = QPushButton("ENREGISTRER CE TARIF")
        self.btn_save.setFixedHeight(55)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0f172a; color: white; font-weight: 800;
                border-radius: 15px; font-size: 14px;
            }
            QPushButton:hover { background-color: #1e293b; }
        """)
        f_lay.addWidget(self.btn_save)
        layout.addWidget(footer)

        self.main_layout.addWidget(self.container)

    def _create_section_title(self, text):
        l = QLabel(text)
        l.setStyleSheet("color: #3b82f6; font-size: 11px; font-weight: 900; letter-spacing: 1.5px; margin-top: 10px;")
        return l

    def _create_input(self, label, placeholder):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(5)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 800; text-transform: uppercase;")
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(42)
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

    def _combo_style(self):
        return "background: #f8fafc; border: none; border-radius: 8px; padding: 10px; color: #1e293b;"