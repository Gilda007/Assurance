from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton, 
                             QLineEdit, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon

class VehicleMainView(QWidget):
    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setStyleSheet("background-color: #f8fafc;")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        # --- EN-TÊTE ---
        header_layout = QHBoxLayout()
        
        title_container = QVBoxLayout()
        self.title_label = QLabel("Parc Automobile")
        self.title_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #1e293b;")
        self.subtitle_label = QLabel("Gérez vos véhicules, contrats et expertises")
        self.subtitle_label.setStyleSheet("color: #64748b; font-size: 14px;")
        title_container.addWidget(self.title_label)
        title_container.addWidget(self.subtitle_label)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        # Bouton Ajouter (Visible selon rôle)
        self.btn_add = QPushButton(" + Nouveau Véhicule")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6; color: white; padding: 10px 20px;
                border-radius: 8px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        header_layout.addWidget(self.btn_add)
        self.layout.addLayout(header_layout)

        # --- BARRE DE RECHERCHE & FILTRES ---
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background: white; border-radius: 10px; border: 1px solid #e2e8f0;")
        filter_layout = QHBoxLayout(filter_frame)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par immatriculation, marque ou propriétaire...")
        self.search_input.setStyleSheet("border: none; padding: 8px; font-size: 14px;")
        
        filter_layout.addWidget(self.search_input)
        self.layout.addWidget(filter_frame)

        # --- TABLEAU DES VÉHICULES ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Immatriculation", "Marque/Modèle", "Propriétaire", "Statut", "Actions"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; border: 1px solid #e2e8f0;
                border-radius: 12px; gridline-color: #f1f5f9; outline: none;
            }
            QHeaderView::section {
                background-color: #f8fafc; padding: 15px; border: none;
                border-bottom: 2px solid #e2e8f0; color: #475569; font-weight: bold;
            }
            QTableWidget::item { padding: 12px; border-bottom: 1px solid #f1f5f9; }
        """)
        
        self.layout.addWidget(self.table)

    def load_data(self):
        """Remplit le tableau avec les données du contrôleur"""
        if not self.controller:
            return
            
        vehicles = self.controller.get_all_vehicles()
        self.table.setRowCount(len(vehicles))
        
        for i, v in enumerate(vehicles):
            # --- CORRECTION ICI ---
            # getattr(objet, "nom_attribut", "valeur_par_défaut")
            immat = getattr(v, 'immatriculation', '---')
            marque = getattr(v, 'marque', '')
            modele = getattr(v, 'modele', '')
            proprietaire = getattr(v, 'client_name', 'Inconnu')
            statut = getattr(v, 'status', 'Actif')

            # On crée les items du tableau en s'assurant que ce sont des STR
            self.table.setItem(i, 0, QTableWidgetItem(str(immat)))
            
            # On peut combiner marque et modèle
            self.table.setItem(i, 1, QTableWidgetItem(f"{marque} {modele}"))
            
            self.table.setItem(i, 2, QTableWidgetItem(str(proprietaire)))
            
            # Pour le statut, on peut garder le centrage
            status_item = QTableWidgetItem(str(statut))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, status_item)
            
            # Bouton détails (inchangé)
            btn_view = QPushButton("Détails")
            btn_view.setStyleSheet("color: #3b82f6; font-weight: bold; border: none; background: transparent;")
            self.table.setCellWidget(i, 4, btn_view)

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QStackedWidget, QFrame, QLabel)
from PySide6.QtCore import Qt

# Importez ici vos 10 sous-fichiers (onglets)
# from .tabs.vehicle_tab import VehicleTabView
# from .tabs.fleet_tab import FleetTabView
# from .tabs.client_tab import ClientTabView

class VehicleMainView(QWidget):
    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        # Configuration du layout principal (Horizontal : Menu à gauche | Contenu à droite)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- 1. MENU DE NAVIGATION INTERNE (Sub-Sidebar) ---
        self.nav_frame = QFrame()
        self.nav_frame.setFixedWidth(220)
        self.nav_frame.setStyleSheet("background-color: #ffffff; border-right: 1px solid #e2e8f0;")
        self.nav_layout = QVBoxLayout(self.nav_frame)
        self.nav_layout.setContentsMargins(15, 30, 15, 30)
        self.nav_layout.setSpacing(10)

        # Titre du menu
        menu_label = QLabel("GESTION AUTO")
        menu_label.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 11px; margin-bottom: 10px;")
        self.nav_layout.addWidget(menu_label)

        # Création des boutons de navigation
        self.btn_vehicles = self._create_nav_btn("🚗 Véhicules", active=True)
        self.btn_fleets = self._create_nav_btn("📦 Flottes")
        self.btn_clients = self._create_nav_btn("👥 Clients")
        
        self.nav_layout.addWidget(self.btn_vehicles)
        self.nav_layout.addWidget(self.btn_fleets)
        self.nav_layout.addWidget(self.btn_clients)
        self.nav_layout.addStretch() # Pousse tout vers le haut

        # --- 2. CONTENEUR EMPILLÉ (QStackedWidget) ---
        self.sub_container = QStackedWidget()
        self.sub_container.setStyleSheet("background-color: #f8fafc;")

        # Initialisation des pages (On leur passe le controller et l'user)
        # Remplacez les QWidget() par vos classes réelles une fois créées
        self.page_vehicles = QWidget() # Remplacer par VehicleTabView(self.controller, self.user)
        self.page_fleets = QWidget()   # Remplacer par FleetTabView(self.controller, self.user)
        self.page_clients = QWidget()  # Remplacer par ClientTabView(self.controller, self.user)

        self.sub_container.addWidget(self.page_vehicles)
        self.sub_container.addWidget(self.page_fleets)
        self.sub_container.addWidget(self.page_clients)

        # --- AJOUT AU LAYOUT PRINCIPAL ---
        self.main_layout.addWidget(self.nav_frame)
        self.main_layout.addWidget(self.sub_container)

        # Connexions
        self.btn_vehicles.clicked.connect(lambda: self.switch_page(0, self.btn_vehicles))
        self.btn_fleets.clicked.connect(lambda: self.switch_page(1, self.btn_fleets))
        self.btn_clients.clicked.connect(lambda: self.switch_page(2, self.btn_clients))

    def _create_nav_btn(self, text, active=False):
        """Utilitaire pour créer des boutons de menu uniformes"""
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        self._apply_btn_style(btn, active)
        return btn

    def _apply_btn_style(self, btn, active=False):
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #eff6ff; color: #1d4ed8; text-align: left;
                    padding-left: 15px; border-radius: 8px; font-weight: bold; border: none;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: #475569; text-align: left;
                    padding-left: 15px; border-radius: 8px; border: none;
                }
                QPushButton:hover { background-color: #f1f5f9; }
            """)

    def switch_page(self, index, active_btn):
        """Change la page et met à jour le style des boutons"""
        self.sub_container.setCurrentIndex(index)
        
        # Réinitialise tous les boutons
        for btn in [self.btn_vehicles, self.btn_fleets, self.btn_clients]:
            self._apply_btn_style(btn, active=False)
        
        # Active le bouton cliqué
        self._apply_btn_style(active_btn, active=True)
