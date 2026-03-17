from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QScrollArea, 
                             QGridLayout, QWidget, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from core.alerts import AlertManager
from datetime import date, datetime

class CompanyTarifForm(QDialog):
    def __init__(self, parent=None, controller=None, current_user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = current_user
        
        # --- CONFIGURATION LOOK "AIR" (MODERNE SANS BORDURES) ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(1150)
        self.setFixedHeight(900)
        
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
        title = QLabel("Édition Complète du Barème Tarifaire")
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

        # 1. IDENTIFICATION (Toutes les colonnes du CSV)
        s_lay.addWidget(self._lbl_sec("IDENTIFICATION DU BARÈME"))
        grid_id = QGridLayout()
        grid_id.addWidget(self._reg_input("Cie", "Code Cie", "1111"), 0, 0)
        grid_id.addWidget(self._reg_input("Nom_Cie", "Nom Compagnie", "SANLAM"), 0, 1)
        grid_id.addWidget(self._reg_input("Tarif", "Code Tarif", "01"), 0, 2)
        grid_id.addWidget(self._reg_input("Lib_Tarif", "Libellé Barème", "AMBULANCES..."), 1, 0, 1, 2) # Large
        grid_id.addWidget(self._reg_input("Categorie", "Catégorie", "0800"), 1, 2)
        grid_id.addWidget(self._reg_input("Zone", "Zone", "A"), 2, 0)
        grid_id.addWidget(self._reg_input("Nbre Place", "Nbre de Places", "5"), 2, 1)
        grid_id.addWidget(self._reg_input("LIBELLE OPTION", "Libellé Option", "Standard"), 2, 2)
        s_lay.addLayout(grid_id)

        # 2. LA GRANDE MATRICE (Primes, Remorquage, Inflammable, Essence, Diesel)
        s_lay.addWidget(self._lbl_sec("MATRICE DES TAUX (LIGNES 1 À 10)"))
        grid_main = QGridLayout()
        grid_main.setSpacing(8)

        # En-têtes
        headers = ["N°", "PRIME RC", "REMORQUAGE", "INFLAMMABLE", "ESSENCE", "DIESEL"]
        for col, text in enumerate(headers):
            h_lbl = QLabel(text)
            h_lbl.setStyleSheet("color: #64748b; font-size: 9px; font-weight: 900; padding-bottom: 5px;")
            h_lbl.setAlignment(Qt.AlignCenter if col > 0 else Qt.AlignLeft)
            grid_main.addWidget(h_lbl, 0, col)

        # Remplissage des 10 lignes
        for i in range(1, 11):
            row_lbl = QLabel(f"{i}")
            row_lbl.setStyleSheet("color: #94a3b8; font-weight: 800;")
            grid_main.addWidget(row_lbl, i, 0)

            grid_main.addWidget(self._create_grid_cell(f"Prime{i}"), i, 1)
            grid_main.addWidget(self._create_grid_cell(f"Remorq{i}"), i, 2)
            grid_main.addWidget(self._create_grid_cell(f"Inflamble{i}"), i, 3)
            # Attention : dans votre CSV les colonnes s'appellent "Essence 1" (avec espace)
            grid_main.addWidget(self._create_grid_cell(f"Essence {i}"), i, 4)
            grid_main.addWidget(self._create_grid_cell(f"Diesel {i}"), i, 5)
        s_lay.addLayout(grid_main)

        # 3. LIMITES ET SURPRIMES
        s_lay.addWidget(self._lbl_sec("LIMITES & SURPRIMES SPÉCIFIQUES"))
        grid_extra = QGridLayout()
        grid_extra.addWidget(self._reg_input("Max Corpo", "Plafond Corporel", "Illimité"), 0, 0)
        grid_extra.addWidget(self._reg_input("Max_Materiel", "Plafond Matériel", "0.0"), 0, 1)
        grid_extra.addWidget(self._reg_input("Surprime 1", "Surprime 1", "0.0"), 1, 0)
        grid_extra.addWidget(self._reg_input("Surprime 2", "Surprime 2", "0.0"), 1, 1)
        s_lay.addLayout(grid_extra)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # --- FOOTER ---
        footer = QFrame()
        footer.setFixedHeight(90)
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(35, 0, 35, 0)
        btn_save = QPushButton("SAUVEGARDER LE BARÈME DANS LA BASE")
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
        edit.setFixedHeight(32)
        edit.setAlignment(Qt.AlignCenter)
        edit.setStyleSheet("""
            QLineEdit {
                background: #f8fafc; border: 1px solid #f1f5f9;
                border-radius: 4px; color: #1e293b; font-size: 11px;
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
        edit = QLineEdit(); edit.setPlaceholderText(placeholder); edit.setFixedHeight(38)
        edit.setStyleSheet("QLineEdit { background: #f8fafc; border: none; border-bottom: 2px solid #f1f5f9; border-radius: 6px; padding-left: 12px; } QLineEdit:focus { border-bottom: 2px solid #3b82f6; background: white; }")
        l.addWidget(lbl); l.addWidget(edit)
        self.inputs[key] = edit
        return w

    # def get_data(self):
    #     """
    #     Récupère dynamiquement les 62 champs du formulaire.
    #     Convertit les vides en '0.0' pour les champs numériques et nettoie le texte.
    #     """
    #     data = {}
        
    #     # Définition des champs qui doivent rester du texte
    #     champs_strict_texte = [
    #         "Cie", "Nom_Cie", "Tarif", "Lib_Tarif", 
    #         "Categorie", "Zone", "LIBELLE OPTION", "Nbre Place"
    #     ]

    #     for key, widget in self.inputs.items():
    #         # Récupération de la valeur saisie dans le QLineEdit
    #         valeur = widget.text().strip()
            
    #         if key in champs_strict_texte:
    #             # Pour le texte, on garde la valeur telle quelle
    #             data[key] = valeur
    #         else:
    #             # Pour les 50+ champs de la grille (RC, Remorque, Essence, etc.)
    #             if valeur == "":
    #                 # Sécurité : un champ numérique vide devient 0.0
    #                 data[key] = "0.0"
    #             else:
    #                 # On remplace la virgule par un point pour être compatible SQL/Excel
    #                 data[key] = valeur.replace(',', '.')
                    
    #     return data

    def get_data(self):
        """
        Récupère proprement les 62+ champs en utilisant le dictionnaire self.inputs.
        """
        data = {
            'created_by': self.user.id if self.user else None,
            'created_at': datetime.now(),
            'is_active': True
        }

        # Mapping des noms de colonnes SQL vs clés dans self.inputs
        # On nettoie les clés pour correspondre exactement aux attentes du modèle
        for key, widget in self.inputs.items():
            valeur = widget.text().strip()
            
            # Conversion des noms avec espaces (ex: "Essence 1" -> "essence_1")
            clean_key = key.lower().replace(" ", "_")

            # Liste des champs qui doivent rester du texte
            if clean_key in ["cie", "nom_cie", "tarif", "lib_tarif", "categorie", "zone", "libelle_option", "max_corpo"]:
                # Pour cie_id, on s'assure que c'est un entier
                if clean_key == "cie":
                    data['cie_id'] = int(valeur) if valeur.isdigit() else 0
                else:
                    data[clean_key] = valeur
            else:
                # Pour tous les champs numériques (Primes, Essences, Diesel, Remorquage...)
                try:
                    # Remplace la virgule par un point et convertit en float
                    data[clean_key] = float(valeur.replace(',', '.')) if valeur else 0.0
                except ValueError:
                    data[clean_key] = 0.0
                    
        return data
    
    def accept(self):
        """Surchargé pour valider et enregistrer avant de fermer."""
        tarif_data = self.get_data()
        
        
        # Validation minimale
        if tarif_data.get('cie_id') == 0 or not tarif_data.get('tarif_code'):
            AlertManager.show_error(self, "Champs manquants", "Le Code Cie et le Code Tarif sont obligatoires.")
            return

        # Appel au contrôleur
        success, message = self.controller.create_tarif(tarif_data)
        
        if success:
            AlertManager.show_success(self, "Succès", message)
            super().accept() # Ferme la fenêtre uniquement si succès
        else:
            AlertManager.show_error(self, "Erreur SQL", message)