import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QScrollArea, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QGraphicsDropShadowEffect, QComboBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QCursor
from core.alerts import AlertManager
from addons.Automobiles.views.compagnies_form_view import FormulaireCreationCompagnie

class CompanyTariffView(QWidget):
    def __init__(self, controller, current_user):
        super().__init__()
        self.controller = controller
        self.user = current_user
        self.setup_ui()

    def _add_shadow(self, widget, blur=15, strength=20):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setColor(QColor(0, 0, 0, strength))
        shadow.setOffset(0, 4)
        widget.setGraphicsEffect(shadow)

    def setup_ui(self):
        # Palette Slate 50 pour le fond
        self.setStyleSheet("background-color: #f8fafc; border: none;")
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        # --- 1. SIDEBAR : LISTE DES COMPAGNIES ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(300)
        self.sidebar.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        self._add_shadow(self.sidebar, 20, 15)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 25, 20, 25)
        
        side_title = QLabel("Compagnies")
        side_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #0f172a; margin-bottom: 10px;")
        sidebar_layout.addWidget(side_title)
        
        # Barre de recherche rapide compagnies
        self.comp_search = QLineEdit()
        self.comp_search.setPlaceholderText("Rechercher...")
        self.comp_search.setStyleSheet("""
            QLineEdit {
                background-color: #f1f5f9; border-radius: 8px; padding: 8px 12px; font-size: 13px;
            }
        """)
        sidebar_layout.addWidget(self.comp_search)
        
        # Liste (Simulée ici)
        self.comp_list_scroll = QScrollArea()
        self.comp_list_scroll.setWidgetResizable(True)
        self.comp_list_scroll.setStyleSheet("border: none;")
        
        self.comp_container = QWidget()
        self.comp_vbox = QVBoxLayout(self.comp_container)
        self.comp_vbox.setContentsMargins(0, 10, 0, 0)
        self.comp_vbox.setAlignment(Qt.AlignTop)
        
        # Exemple de items
        for name in ["AXA Assurance", "Allianz", "NSIA Benin", "Saham", "Gras Savoye"]:
            btn = self._create_company_item(name)
            self.comp_vbox.addWidget(btn)
            
        self.comp_list_scroll.setWidget(self.comp_container)
        sidebar_layout.addWidget(self.comp_list_scroll)
        
        self.btn_add_comp = QPushButton("+ Ajouter Compagnie")
        btn_add_comp.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9; color: #475569; font-weight: 700; 
                border-radius: 8px; padding: 10px; font-size: 12px;
            }
            QPushButton:hover { background-color: #e2e8f0; color: #1e293b; }
        """)
        sidebar_layout.addWidget(btn_add_comp)
        self.btn_add_comp.clicked.connect(self.on_add_click)

        # --- 2. CONTENU PRINCIPAL : TARIFS & CONVENTIONS ---
        self.main_content = QVBoxLayout()
        self.main_content.setSpacing(20)

        # Header de la section droite
        top_header = QHBoxLayout()
        self.selected_label = QLabel("AXA Assurance - Gestion des Tarifs")
        self.selected_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a;")
        
        btn_save_tariffs = QPushButton("Enregistrer les tarifs")
        btn_save_tariffs.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; font-weight: bold; 
                border-radius: 8px; padding: 10px 20px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        
        top_header.addWidget(self.selected_label)
        top_header.addStretch()
        top_header.addWidget(btn_save_tariffs)
        self.main_content.addLayout(top_header)

        # Grille de Tarification (Tableau Moderne)
        self.tariff_card = QFrame()
        self.tariff_card.setStyleSheet("background-color: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        self._add_shadow(self.tariff_card, 25, 10)
        
        tariff_layout = QVBoxLayout(self.tariff_card)
        tariff_layout.setContentsMargins(20, 20, 20, 20)
        
        # Filtres de catégorie
        filter_box = QHBoxLayout()
        cat_combo = QComboBox()
        cat_combo.addItems(["Automobile", "Santé", "Responsabilité Civile", "Multirisque Habitation"])
        cat_combo.setFixedWidth(200)
        cat_combo.setStyleSheet("""
            QComboBox { 
                background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 5px; 
            }
        """)
        filter_box.addWidget(QLabel("Catégorie :"))
        filter_box.addWidget(cat_combo)
        filter_box.addStretch()
        tariff_layout.addLayout(filter_box)

        # Tableau
        self.table = QTableWidget(10, 4)
        self.table.setHorizontalHeaderLabels(["Garantie", "Taux Conventionnel", "Prime Minimum", "Observation"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #f1f5f9;
                background-color: white;
                alternate-background-color: #f8fafc;
                font-size: 13px;
                color: #475569;
            }
            QHeaderView::section {
                background-color: white;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #64748b;
                text-transform: uppercase;
                font-size: 11px;
            }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tariff_layout.addWidget(self.table)

        self.main_content.addWidget(self.tariff_card)

        # Ajout des layouts au main
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addLayout(self.main_content, 1)

    def _create_company_item(self, name):
        btn = QPushButton(name)
        btn.setCheckable(True)
        btn.setFixedHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left; padding-left: 15px; border: none; 
                border-radius: 10px; color: #64748b; font-weight: 600; font-size: 14px;
            }
            QPushButton:checked {
                background-color: #eff6ff; color: #2563eb; font-weight: 800;
            }
            QPushButton:hover:!checked {
                background-color: #f8fafc; color: #1e293b;
            }
        """)
        return btn
    
    def on_add_click(self):
        """Déclenche l'ouverture du formulaire d'ajout de contact."""
        dialog = FormulaireCreationCompagnie(self)
        
        if dialog.exec_():
            new_data = dialog.get_data()
            
            # Appel au contrôleur
            result = self.controller.contacts.create_contact(new_data)
            
            # --- GESTION DU RETOUR DU CONTRÔLEUR ---
            new_contact = None
            success = False
            
            # Cas 1 : Le contrôleur renvoie un tuple (objet, succes) ou (objet, succes, message)
            if isinstance(result, tuple):
                new_contact = result[0]
                success = result[1]
            # Cas 2 : Le contrôleur renvoie directement l'objet ou None
            else:
                new_contact = result
                success = True if result else False

            if success and hasattr(new_contact, 'nom'):
                # --- AUDIT ---
                # On sécurise l'accès aux attributs
                nom = getattr(new_contact, 'nom', 'Inconnu')
                prenom = getattr(new_contact, 'prenom', '')
                details = f"Création du contact : {nom} {prenom}"
                
                # Log de l'action
                self.controller.contacts.log_contact_action("CRÉATION", new_contact.id, details)
                
                # Rafraîchir l'interface
                self.display_contacts(self.controller.contacts.get_all_contacts())
            else:
                AlertManager.show_error(self, "Erreur", "Le contact n'a pas pu être créé ou les données sont corrompues.")
