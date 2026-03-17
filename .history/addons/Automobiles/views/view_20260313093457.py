# from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
#                              QTableWidgetItem, QHeaderView, QLabel, QPushButton, 
#                              QLineEdit, QFrame, QGraphicsDropShadowEffect)
# from PySide6.QtCore import Qt, QSize
# from PySide6.QtGui import QColor, QIcon

# class VehicleMainView(QWidget):
#     def __init__(self, controller=None, user=None):
#         super().__init__()
#         self.controller = controller
#         self.user = user
#         self.setup_ui()
#         self.load_data()

#     def setup_ui(self):
#         self.setStyleSheet("background-color: #f8fafc;")
#         self.layout = QVBoxLayout(self)
#         self.layout.setContentsMargins(30, 30, 30, 30)
#         self.layout.setSpacing(20)

#         # --- EN-TÊTE ---
#         header_layout = QHBoxLayout()
        
#         title_container = QVBoxLayout()
#         self.title_label = QLabel("Parc Automobile")
#         self.title_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #1e293b;")
#         self.subtitle_label = QLabel("Gérez vos véhicules, contrats et expertises")
#         self.subtitle_label.setStyleSheet("color: #64748b; font-size: 14px;")
#         title_container.addWidget(self.title_label)
#         title_container.addWidget(self.subtitle_label)
        
#         header_layout.addLayout(title_container)
#         header_layout.addStretch()
        
#         # Bouton Ajouter (Visible selon rôle)
#         self.btn_add = QPushButton(" + Nouveau Véhicule")
#         self.btn_add.setCursor(Qt.PointingHandCursor)
#         self.btn_add.setStyleSheet("""
#             QPushButton {
#                 background-color: #3b82f6; color: white; padding: 10px 20px;
#                 border-radius: 8px; font-weight: bold; border: none;
#             }
#             QPushButton:hover { background-color: #2563eb; }
#         """)
#         header_layout.addWidget(self.btn_add)
#         self.layout.addLayout(header_layout)

#         # --- BARRE DE RECHERCHE & FILTRES ---
#         filter_frame = QFrame()
#         filter_frame.setStyleSheet("background: white; border-radius: 10px; border: 1px solid #e2e8f0;")
#         filter_layout = QHBoxLayout(filter_frame)
        
#         self.search_input = QLineEdit()
#         self.search_input.setPlaceholderText("Rechercher par immatriculation, marque ou propriétaire...")
#         self.search_input.setStyleSheet("border: none; padding: 8px; font-size: 14px;")
        
#         filter_layout.addWidget(self.search_input)
#         self.layout.addWidget(filter_frame)

#         # --- TABLEAU DES VÉHICULES ---
#         self.table = QTableWidget()
#         self.table.setColumnCount(5)
#         self.table.setHorizontalHeaderLabels(["Immatriculation", "Marque/Modèle", "Propriétaire", "Statut", "Actions"])
#         self.table.setAlternatingRowColors(True)
#         self.table.setSelectionBehavior(QTableWidget.SelectRows)
#         self.table.verticalHeader().setVisible(False)
#         self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
#         self.table.setStyleSheet("""
#             QTableWidget {
#                 background-color: white; border: 1px solid #e2e8f0;
#                 border-radius: 12px; gridline-color: #f1f5f9; outline: none;
#             }
#             QHeaderView::section {
#                 background-color: #f8fafc; padding: 15px; border: none;
#                 border-bottom: 2px solid #e2e8f0; color: #475569; font-weight: bold;
#             }
#             QTableWidget::item { padding: 12px; border-bottom: 1px solid #f1f5f9; }
#         """)
        
#         self.layout.addWidget(self.table)

#     def load_data(self):
#         """Remplit le tableau avec les données du contrôleur"""
#         if not self.controller:
#             return
            
#         vehicles = self.controller.get_all_vehicles()
#         self.table.setRowCount(len(vehicles))
        
#         for i, v in enumerate(vehicles):
#             # --- CORRECTION ICI ---
#             # getattr(objet, "nom_attribut", "valeur_par_défaut")
#             immat = getattr(v, 'immatriculation', '---')
#             marque = getattr(v, 'marque', '')
#             modele = getattr(v, 'modele', '')
#             proprietaire = getattr(v, 'client_name', 'Inconnu')
#             statut = getattr(v, 'status', 'Actif')

#             # On crée les items du tableau en s'assurant que ce sont des STR
#             self.table.setItem(i, 0, QTableWidgetItem(str(immat)))
            
#             # On peut combiner marque et modèle
#             self.table.setItem(i, 1, QTableWidgetItem(f"{marque} {modele}"))
            
#             self.table.setItem(i, 2, QTableWidgetItem(str(proprietaire)))
            
#             # Pour le statut, on peut garder le centrage
#             status_item = QTableWidgetItem(str(statut))
#             status_item.setTextAlignment(Qt.AlignCenter)
#             self.table.setItem(i, 3, status_item)
            
#             # Bouton détails (inchangé)
#             btn_view = QPushButton("Détails")
#             btn_view.setStyleSheet("color: #3b82f6; font-weight: bold; border: none; background: transparent;")
#             self.table.setCellWidget(i, 4, btn_view)


# addons/Automobiles/views/view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton, 
                             QLineEdit, QFrame, QStackedWidget, QGridLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon
from addons.Automobiles.views.automobile_view import VehiculeModuleView
from addons.Automobiles.views.contacts_view import ContactListView
# from addons.Automobiles.views.contract_view import ContactListView


class VehicleMainView(QWidget):
    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background-color: #f1f5f9;")
        # Layout Principal Horizontal (Menu latéral gauche | Contenu droite)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- 1. NAVIGATION INTERNE DU MODULE (Sidebar Gauche) ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #ffffff; border-right: 1px solid #e2e8f0;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(10)

        nav_title = QLabel("MENU AUTOMOBILE")
        nav_title.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 11px; margin-bottom: 10px;")
        sidebar_layout.addWidget(nav_title)

        self.btn_dash = self._create_nav_btn("📊 Tableau de Bord", active=True)
        self.btn_vehicles = self._create_nav_btn("🚗 Véhicules")
        self.btn_fleets = self._create_nav_btn("📦 Flottes")
        self.btn_clients = self._create_nav_btn("👥 Clients")

        sidebar_layout.addWidget(self.btn_dash)
        sidebar_layout.addWidget(self.btn_vehicles)
        sidebar_layout.addWidget(self.btn_fleets)
        sidebar_layout.addWidget(self.btn_clients)
        sidebar_layout.addStretch()

        # --- 2. ZONE DE CONTENU PRINCIPALE (A droite) ---
        self.content_area = QVBoxLayout()
        self.content_area.setContentsMargins(25, 25, 25, 25)
        self.content_area.setSpacing(20)

        # A. SECTION DES CARTES KPI (Toujours visibles en haut)
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.addWidget(self._create_kpi_card("Véhicules", "142", "#3b82f6"))
        self.kpi_layout.addWidget(self._create_kpi_card("Flottes", "12", "#10b981"))
        self.kpi_layout.addWidget(self._create_kpi_card("Sinistres", "08", "#ef4444"))
        self.kpi_layout.addWidget(self._create_kpi_card("Clients", "89", "#f59e0b"))
        self.content_area.addLayout(self.kpi_layout)

        # B. STACKED WIDGET (Le coeur du module)
        self.stack = QStackedWidget()
        
        # Initialisation des pages
        self.page_dashboard = self._init_dashboard_page()
        self.page_vehicles = self._init_vehicles_page()
        self.page_clients
        
        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_vehicles)
        # On peut ajouter ici les pages Flottes et Clients plus tard
        
        self.content_area.addWidget(self.stack)

        # Assemblage final
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addLayout(self.content_area)

        # Connexions des boutons
        self.btn_dash.clicked.connect(lambda: self._switch_page(0, self.btn_dash))
        self.btn_vehicles.clicked.connect(lambda: self._switch_page(1, self.btn_vehicles))
        self.btn_fleets.clicked.connect(lambda: self._switch_page(2, self.btn_fleets))
        self.btn_clients.clicked.connect(lambda: self._switch_page(3, self.btn_clients))        

    # --- MÉTHODES DE CONSTRUCTION DES PAGES ---

    def _init_dashboard_page(self):
        """Page avec des diagrammes modernes de visualisation"""
        page = QWidget()
        layout = QGridLayout(page)
        layout.setSpacing(20)

        # Graphique 1 : Évolution (Placeholder)
        g1 = QFrame()
        g1.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #e2e8f0;")
        l1 = QVBoxLayout(g1)
        l1.addWidget(QLabel("📈 Évolution Mensuelle des Contrats"), alignment=Qt.AlignCenter)
        
        # Graphique 2 : Répartition (Placeholder)
        g2 = QFrame()
        g2.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #e2e8f0;")
        l2 = QVBoxLayout(g2)
        l2.addWidget(QLabel("📊 Répartition par Type de Flotte"), alignment=Qt.AlignCenter)

        layout.addWidget(g1, 0, 0)
        layout.addWidget(g2, 0, 1)
        return page

    def _init_vehicles_page(self):
        """Page contenant le tableau des véhicules"""
        page = QWidget()
        layout = QVBoxLayout(page) 

        if not self.controller:
            # Sécurité au cas où le contrôleur n'est pas encore chargé
            return QWidget()
        full_management_page = VehiculeModuleView(
            controller=self.controller, 
            current_user=self.user
        )
        
        return full_management_page
        # return page

    def _init_contacts_page(self):
        """Page contenant le tableau des véhicules"""
        page = QWidget()
        layout = QVBoxLayout(page) 

        if not self.controller:
            # Sécurité au cas où le contrôleur n'est pas encore chargé
            return QWidget()
        full_management_page = ContactListView(
            controller=self.controller, 
            current_user=self.user
        )
        
        return full_management_page
        # return page

    # --- HELPERS (Boutons, Cartes, Navigation) ---

    def _create_kpi_card(self, title, value, color):
        card = QFrame()
        card.setFixedHeight(110)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white; border-radius: 15px;
                border-bottom: 4px solid {color};
            }}
        """)
        layout = QVBoxLayout(card)
        t = QLabel(title)
        t.setStyleSheet("color: #64748b; font-size: 12px; font-weight: bold;")
        v = QLabel(value)
        v.setStyleSheet(f"color: #1e293b; font-size: 28px; font-weight: 900;")
        layout.addWidget(t)
        layout.addWidget(v)
        return card

    def _create_nav_btn(self, text, active=False):
        btn = QPushButton(text)
        btn.setFixedHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        self._style_nav_btn(btn, active)
        return btn

    def _style_nav_btn(self, btn, active):
        if active:
            btn.setStyleSheet("background-color: #eff6ff; color: #2563eb; font-weight: bold; border-radius: 8px; text-align: left; padding-left: 15px; border: none;")
        else:
            btn.setStyleSheet("background-color: transparent; color: #475569; border-radius: 8px; text-align: left; padding-left: 15px; border: none;")

    def _switch_page(self, index, btn):
        self.stack.setCurrentIndex(index)
        # Reset styles
        for b in [self.btn_dash, self.btn_vehicles, self.btn_fleets, self.btn_clients]:
            self._style_nav_btn(b, False)
        self._style_nav_btn(btn, True)
