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
        self.kpi_layout.addWidget(self._create_kpi_card("Véhicules", "142", "#3b82f6", "#779ede"))
        self.kpi_layout.addWidget(self._create_kpi_card("Flottes", "12", "#10b981", "#67d7b1"))
        self.kpi_layout.addWidget(self._create_kpi_card("Entreprises", "08", "#ef4444", "#ec7e7e"))
        self.kpi_layout.addWidget(self._create_kpi_card("Particuliers", "89", "#f59e0b", "#ecc788"))
        self.content_area.addLayout(self.kpi_layout)

        # B. STACKED WIDGET (Le coeur du module)
        self.stack = QStackedWidget()
        
        # Initialisation des pages
        self.page_dashboard = self._init_dashboard_page()
        self.page_vehicles = self._init_vehicles_page()
        self.page_clients = self._init_contacts_page()
        
        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_vehicles)
        self.stack.addWidget(self.page_clients)
        # On peut ajouter ici les pages Flottes et Clients plus tard
        
        self.content_area.addWidget(self.stack)

        # Assemblage final
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addLayout(self.content_area)

        # Connexions des boutons
        self.btn_dash.clicked.connect(lambda: self._switch_page(0, self.btn_dash))
        self.btn_vehicles.clicked.connect(lambda: self._switch_page(1, self.btn_vehicles))
        # self.btn_fleets.clicked.connect(lambda: self._switch_page(2, self.btn_fleets))
        self.btn_clients.clicked.connect(lambda: self._switch_page(2, self.btn_clients))        

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
        if not self.controller:
            return QWidget()
            
        # On instancie la vue que vous avez fournie
        # Elle prend en paramètres (controller, current_user)
        client_page = ContactListView(
            controller=self.controller, 
            current_user=self.user
        )
        
        return client_page
        # return page

    # --- HELPERS (Boutons, Cartes, Navigation) ---

    def _create_kpi_card(self, title, value, color, bgcolor):
        card = QFrame()
        card.setFixedHeight(110)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bgcolor}; border-radius: 10px;
                border-left: 2px solid {color};
            }}
        """)
        layout = QVBoxLayout(card)
        t = QLabel(title)
        t.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        v = QLabel(value)
        v.setStyleSheet(f"color: white; font-size: 28px; font-weight: 900;")
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
        print(index)
        # Reset styles
        for b in [self.btn_dash, self.btn_vehicles, self.btn_fleets, self.btn_clients]:
            self._style_nav_btn(b, False)
        self._style_nav_btn(btn, True)
