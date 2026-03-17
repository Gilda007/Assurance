# import os
# from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
#                              QPushButton, QFrame, QLineEdit, QScrollArea, 
#                              QTableWidget, QTableWidgetItem, QHeaderView, 
#                              QGraphicsDropShadowEffect, QComboBox)
# from PySide6.QtCore import Qt, QSize
# from PySide6.QtGui import QColor, QIcon, QCursor

# class CompanyTariffView(QWidget):
#     def __init__(self, controller, current_user):
#         super().__init__()
#         self.controller = controller
#         self.user = current_user
#         self.setup_ui()

#     def _add_shadow(self, widget, blur=15, strength=20):
#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(blur)
#         shadow.setColor(QColor(0, 0, 0, strength))
#         shadow.setOffset(0, 4)
#         widget.setGraphicsEffect(shadow)

#     def setup_ui(self):
#         # Palette Slate 50 pour le fond
#         self.setStyleSheet("background-color: #f8fafc; border: none;")
#         self.main_layout = QHBoxLayout(self)
#         self.main_layout.setContentsMargins(30, 30, 30, 30)
#         self.main_layout.setSpacing(25)

#         # --- 1. SIDEBAR : LISTE DES COMPAGNIES ---
#         self.sidebar = QFrame()
#         self.sidebar.setFixedWidth(300)
#         self.sidebar.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;")
#         self._add_shadow(self.sidebar, 20, 15)
        
#         sidebar_layout = QVBoxLayout(self.sidebar)
#         sidebar_layout.setContentsMargins(20, 25, 20, 25)
        
#         side_title = QLabel("Compagnies")
#         side_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #0f172a; margin-bottom: 10px;")
#         sidebar_layout.addWidget(side_title)
        
#         # Barre de recherche rapide compagnies
#         self.comp_search = QLineEdit()
#         self.comp_search.setPlaceholderText("Rechercher...")
#         self.comp_search.setStyleSheet("""
#             QLineEdit {
#                 background-color: #f1f5f9; border-radius: 8px; padding: 8px 12px; font-size: 13px;
#             }
#         """)
#         sidebar_layout.addWidget(self.comp_search)
        
#         # Liste (Simulée ici)
#         self.comp_list_scroll = QScrollArea()
#         self.comp_list_scroll.setWidgetResizable(True)
#         self.comp_list_scroll.setStyleSheet("border: none;")
        
#         self.comp_container = QWidget()
#         self.comp_vbox = QVBoxLayout(self.comp_container)
#         self.comp_vbox.setContentsMargins(0, 10, 0, 0)
#         self.comp_vbox.setAlignment(Qt.AlignTop)
        
#         # Exemple de items
#         for name in ["AXA Assurance", "Allianz", "NSIA Benin", "Saham", "Gras Savoye"]:
#             btn = self._create_company_item(name)
#             self.comp_vbox.addWidget(btn)
            
#         self.comp_list_scroll.setWidget(self.comp_container)
#         sidebar_layout.addWidget(self.comp_list_scroll)
        
#         btn_add_comp = QPushButton("+ Ajouter Compagnie")
#         btn_add_comp.setStyleSheet("""
#             QPushButton {
#                 background-color: #f1f5f9; color: #475569; font-weight: 700; 
#                 border-radius: 8px; padding: 10px; font-size: 12px;
#             }
#             QPushButton:hover { background-color: #e2e8f0; color: #1e293b; }
#         """)
#         sidebar_layout.addWidget(btn_add_comp)

#         # --- 2. CONTENU PRINCIPAL : TARIFS & CONVENTIONS ---
#         self.main_content = QVBoxLayout()
#         self.main_content.setSpacing(20)

#         # Header de la section droite
#         top_header = QHBoxLayout()
#         self.selected_label = QLabel("AXA Assurance - Gestion des Tarifs")
#         self.selected_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a;")
        
#         btn_save_tariffs = QPushButton("Enregistrer les tarifs")
#         btn_save_tariffs.setStyleSheet("""
#             QPushButton {
#                 background-color: #2563eb; color: white; font-weight: bold; 
#                 border-radius: 8px; padding: 10px 20px;
#             }
#             QPushButton:hover { background-color: #1d4ed8; }
#         """)
        
#         top_header.addWidget(self.selected_label)
#         top_header.addStretch()
#         top_header.addWidget(btn_save_tariffs)
#         self.main_content.addLayout(top_header)

#         # Grille de Tarification (Tableau Moderne)
#         self.tariff_card = QFrame()
#         self.tariff_card.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;")
#         self._add_shadow(self.tariff_card, 25, 10)
        
#         tariff_layout = QVBoxLayout(self.tariff_card)
#         tariff_layout.setContentsMargins(20, 20, 20, 20)
        
#         # Filtres de catégorie
#         filter_box = QHBoxLayout()
#         cat_combo = QComboBox()
#         cat_combo.addItems(["Automobile", "Santé", "Responsabilité Civile", "Multirisque Habitation"])
#         cat_combo.setFixedWidth(200)
#         cat_combo.setStyleSheet("""
#             QComboBox { 
#                 background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 5px; 
#             }
#         """)
#         filter_box.addWidget(QLabel("Catégorie :"))
#         filter_box.addWidget(cat_combo)
#         filter_box.addStretch()
#         tariff_layout.addLayout(filter_box)

#         # Tableau
#         self.table = QTableWidget(10, 4)
#         self.table.setHorizontalHeaderLabels(["Garantie", "Taux Conventionnel", "Prime Minimum", "Observation"])
#         self.table.verticalHeader().setVisible(False)
#         self.table.setAlternatingRowColors(True)
#         self.table.setStyleSheet("""
#             QTableWidget {
#                 border: none;
#                 gridline-color: #f1f5f9;
#                 background-color: white;
#                 alternate-background-color: #f8fafc;
#                 font-size: 13px;
#                 color: #475569;
#             }
#             QHeaderView::section {
#                 background-color: white;
#                 padding: 12px;
#                 border: none;
#                 border-bottom: 2px solid #e2e8f0;
#                 font-weight: bold;
#                 color: #64748b;
#                 text-transform: uppercase;
#                 font-size: 11px;
#             }
#         """)
#         self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         tariff_layout.addWidget(self.table)

#         self.main_content.addWidget(self.tariff_card)

#         # Ajout des layouts au main
#         self.main_layout.addWidget(self.sidebar)
#         self.main_layout.addLayout(self.main_content, 1)

#     def _create_company_item(self, name):
#         btn = QPushButton(name)
#         btn.setCheckable(True)
#         btn.setFixedHeight(45)
#         btn.setCursor(Qt.PointingHandCursor)
#         btn.setStyleSheet("""
#             QPushButton {
#                 text-align: left; padding-left: 15px; border: none; 
#                 border-radius: 10px; color: #64748b; font-weight: 600; font-size: 14px;
#             }
#             QPushButton:checked {
#                 background-color: #eff6ff; color: #2563eb; font-weight: 800;
#             }
#             QPushButton:hover:!checked {
#                 background-color: #f8fafc; color: #1e293b;
#             }
#         """)
#         return btn


from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect, 
                             QComboBox, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon

class CompanyTariffCreationView(QWidget):
    def __init__(self, controller=None, current_user=None):
        super().__init__()
        self.controller = controller
        self.user = current_user
        self.setup_ui()

    def _add_shadow(self, widget, blur=20, strength=15):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setColor(QColor(0, 0, 0, strength))
        shadow.setOffset(0, 6)
        widget.setGraphicsEffect(shadow)

    def setup_ui(self):
        self.setStyleSheet("background-color: #f1f5f9; border: none;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        # --- EN-TÊTE ---
        header = QHBoxLayout()
        title_v = QVBoxLayout()
        t = QLabel("Configuration des Partenaires")
        t.setStyleSheet("font-size: 26px; font-weight: 800; color: #0f172a;")
        st = QLabel("Enregistrez une nouvelle compagnie et définissez ses barèmes tarifaires.")
        st.setStyleSheet("color: #64748b; font-size: 14px;")
        title_v.addWidget(t)
        title_v.addWidget(st)
        header.addLayout(title_v)
        
        # Bouton global de sauvegarde
        self.btn_global_save = QPushButton("🚀 Publier la Compagnie")
        self.btn_global_save.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; font-weight: 800;
                border-radius: 10px; padding: 12px 25px; font-size: 14px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        header.addStretch()
        header.addWidget(self.btn_global_save)
        self.main_layout.addLayout(header)

        # --- ZONE DE TRAVAIL ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(25)

        # 1. FORMULAIRE COMPAGNIE (GAUCHE)
        comp_card = QFrame()
        comp_card.setFixedWidth(400)
        comp_card.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        self._add_shadow(comp_card)
        
        comp_layout = QVBoxLayout(comp_card)
        comp_layout.setContentsMargins(25, 25, 25, 25)
        comp_layout.setSpacing(15)

        comp_layout.addWidget(self._section_label("🏢 IDENTITÉ DE LA COMPAGNIE"))
        
        self.name_input = self._create_styled_input("Nom de la compagnie (ex: AXA)")
        self.code_input = self._create_styled_input("Code court (ex: AXA-BJ)")
        self.email_input = self._create_styled_input("Email contact")
        self.tel_input = self._create_styled_input("Téléphone")
        
        comp_layout.addWidget(self.name_input)
        comp_layout.addWidget(self.code_input)
        comp_layout.addWidget(self.email_input)
        comp_layout.addWidget(self.tel_input)
        
        comp_layout.addSpacing(10)
        comp_layout.addWidget(self._section_label("📍 ADRESSE ET SIÈGE"))
        self.addr_input = self._create_styled_input("Adresse complète")
        comp_layout.addWidget(self.addr_input)
        
        comp_layout.addStretch()
        
        # 2. CONFIGURATION DES TARIFS (DROITE)
        tariff_card = QFrame()
        tariff_card.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        self._add_shadow(tariff_card)
        
        tariff_layout = QVBoxLayout(tariff_card)
        tariff_layout.setContentsMargins(25, 25, 25, 25)
        
        t_header = QHBoxLayout()
        t_header.addWidget(self._section_label("📊 GRILLE TARIFAIRE PAR DÉFAUT"))
        
        btn_add_row = QPushButton("+ Ajouter une garantie")
        btn_add_row.setStyleSheet("color: #2563eb; font-weight: bold; background: transparent; font-size: 12px;")
        btn_add_row.clicked.connect(self.add_tariff_row)
        
        t_header.addStretch()
        t_header.addWidget(btn_add_row)
        tariff_layout.addLayout(t_header)

        # Table des tarifs
        self.tariff_table = QTableWidget(0, 4)
        self.tariff_table.setHorizontalHeaderLabels(["Garantie", "Type", "Taux (%)", "Prime Min"])
        self.tariff_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tariff_table.verticalHeader().setVisible(False)
        self.tariff_table.setStyleSheet("""
            QTableWidget { border: none; gridline-color: #f1f5f9; font-size: 13px; }
            QHeaderView::section { 
                background: white; padding: 10px; font-weight: 800; 
                color: #64748b; border: none; border-bottom: 2px solid #f1f5f9;
                text-transform: uppercase; font-size: 10px;
            }
        """)
        
        tariff_layout.addWidget(self.tariff_table)

        # Boutons d'import/export rapide
        footer_tools = QHBoxLayout()
        btn_import_csv = QPushButton("🔗 Importer Barème CSV")
        btn_import_csv.setStyleSheet("font-size: 11px; color: #64748b; background: #f8fafc; border-radius: 6px; padding: 5px 10px;")
        footer_tools.addStretch()
        footer_tools.addWidget(btn_import_csv)
        tariff_layout.addLayout(footer_tools)

        content_layout.addWidget(comp_card)
        content_layout.addWidget(tariff_card, 1)
        self.main_layout.addLayout(content_layout)

    def _section_label(self, text):
        l = QLabel(text)
        l.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px;")
        return l

    def _create_styled_input(self, placeholder):
        i = QLineEdit()
        i.setPlaceholderText(placeholder)
        i.setFixedHeight(45)
        i.setStyleSheet("""
            QLineEdit {
                background-color: #f8fafc; border: 1px solid #e2e8f0; 
                border-radius: 8px; padding-left: 15px; color: #1e293b;
            }
            QLineEdit:focus { border: 2px solid #3b82f6; background-color: white; }
        """)
        return i

    def add_tariff_row(self):
        row = self.tariff_table.rowCount()
        self.tariff_table.insertRow(row)
        
        # Combo pour le type de garantie
        combo = QComboBox()
        combo.addItems(["Fixe", "Proportionnel", "Variable"])
        combo.setStyleSheet("background: transparent; border: none;")
        
        self.tariff_table.setItem(row, 0, QTableWidgetItem("Nouvelle Garantie"))
        self.tariff_table.setCellWidget(row, 1, combo)
        self.tariff_table.setItem(row, 2, QTableWidgetItem("0.0"))
        self.tariff_table.setItem(row, 3, QTableWidgetItem("0"))