# # addons/Automobiles/views/view.py
# from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
#                              QTableWidgetItem, QHeaderView, QLabel, QPushButton, 
#                              QLineEdit, QFrame, QStackedWidget, QGridLayout)
# from PySide6.QtCore import Qt
# from PySide6.QtGui import QColor, QIcon
# from addons.Automobiles.views.automobile_view import VehiculeModuleView
# from addons.Automobiles.views.contacts_view import ContactListView
# from addons.Automobiles.views.compagnies_view import CompanyTariffView
# from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis
# from PySide6.QtGui import QPainter
# # from addons.Automobiles.views.contract_view import ContactListView


# class VehicleMainView(QWidget):
#     def __init__(self, controller=None, user=None):
#         super().__init__()
#         self.controller = controller
#         self.user = user
#         self.setup_ui()

#     def setup_ui(self):
#         self.setStyleSheet("background-color: #f1f5f9;")
#         # Layout Principal Horizontal (Menu latéral gauche | Contenu droite)
#         self.main_layout = QHBoxLayout(self)
#         self.main_layout.setContentsMargins(0, 0, 0, 0)
#         self.main_layout.setSpacing(0)

#         # --- 1. NAVIGATION INTERNE DU MODULE (Sidebar Gauche) ---
#         self.sidebar = QFrame()
#         self.sidebar.setFixedWidth(220)
#         self.sidebar.setStyleSheet("background-color: #ffffff; border-right: 1px solid #e2e8f0;")
#         sidebar_layout = QVBoxLayout(self.sidebar)
#         sidebar_layout.setContentsMargins(15, 30, 15, 30)
#         sidebar_layout.setSpacing(10)

#         nav_title = QLabel("MENU AUTOMOBILE")
#         nav_title.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 11px; margin-bottom: 10px;")
#         sidebar_layout.addWidget(nav_title)

#         self.btn_dash = self._create_nav_btn("📊 Tableau de Bord", active=True)
#         self.btn_vehicles = self._create_nav_btn("🚗 Véhicules")
#         self.btn_comp = self._create_nav_btn("📦 Compagnies et Tarifs")
#         self.btn_clients = self._create_nav_btn("👥 Clients")

#         sidebar_layout.addWidget(self.btn_dash)
#         sidebar_layout.addWidget(self.btn_vehicles)
#         sidebar_layout.addWidget(self.btn_comp)
#         sidebar_layout.addWidget(self.btn_clients)
#         sidebar_layout.addStretch()

#         # --- 2. ZONE DE CONTENU PRINCIPALE (A droite) ---
#         self.content_area = QVBoxLayout()
#         self.content_area.setContentsMargins(25, 25, 25, 25)
#         self.content_area.setSpacing(20)

#         # A. SECTION DES CARTES KPI (Toujours visibles en haut)
#         self.kpi_layout = QHBoxLayout()
#         self.kpi_layout.addWidget(self._create_kpi_card("Véhicules", "142", "#3b82f6", "#779ede"))
#         self.kpi_layout.addWidget(self._create_kpi_card("Flottes", "12", "#10b981", "#67d7b1"))
#         self.kpi_layout.addWidget(self._create_kpi_card("Entreprises", "08", "#ef4444", "#ec7e7e"))
#         self.kpi_layout.addWidget(self._create_kpi_card("Particuliers", "89", "#f59e0b", "#ecc788"))
#         self.content_area.addLayout(self.kpi_layout)

#         # B. STACKED WIDGET (Le coeur du module)
#         self.stack = QStackedWidget()
        
#         # Initialisation des pages
#         self.page_dashboard = self._init_dashboard_page()
#         self.page_vehicles = self._init_vehicles_page()
#         self.page_clients = self._init_contacts_page()
#         self.page_compagnies = self._init_compagnies_page()
        
#         self.stack.addWidget(self.page_dashboard)
#         self.stack.addWidget(self.page_vehicles)
#         self.stack.addWidget(self.page_clients)
#         self.stack.addWidget(self.page_compagnies)
#         # On peut ajouter ici les pages Flottes et Clients plus tard
        
#         self.content_area.addWidget(self.stack)

#         # Assemblage final
#         self.main_layout.addWidget(self.sidebar)
#         self.main_layout.addLayout(self.content_area)

#         # Connexions des boutons
#         self.btn_dash.clicked.connect(lambda: self._switch_page(0, self.btn_dash))
#         self.btn_vehicles.clicked.connect(lambda: self._switch_page(1, self.btn_vehicles))
#         self.btn_clients.clicked.connect(lambda: self._switch_page(2, self.btn_clients))
#         self.btn_comp.clicked.connect(lambda: self._switch_page(3, self.btn_comp))    

#     # --- MÉTHODES DE CONSTRUCTION DES PAGES ---

#     def _init_dashboard_page(self):
#         """Page avec de vrais diagrammes de visualisation"""
#         page = QWidget()
#         layout = QGridLayout(page)
#         layout.setSpacing(20)

#         # --- 1. GRAPHIQUE : RÉPARTITION DES CONTACTS (CAMEMBERT) ---
#         chart_view_pie = self._create_contacts_pie_chart()
#         layout.addWidget(chart_view_pie, 0, 0)

#         # --- 2. GRAPHIQUE : STATISTIQUES VÉHICULES (BARRES) ---
#         chart_view_bar = self._create_vehicles_bar_chart()
#         layout.addWidget(chart_view_bar, 0, 1)

#         return page

#     def _create_contacts_pie_chart(self):
#         """Crée un graphique en camembert pour les contacts"""
#         series = QPieSeries()
        
#         # Récupération des vraies données via le contrôleur
#         stats = self.controller.contacts.get_contact_stats()
#         series.append("Physique", stats.get('Physique', 10))
#         series.append("Morale", stats.get('Morale', 5))

#         # Style : mettre en avant une tranche
#         slice = series.slices()[0]
#         slice.setExploded(True)
#         slice.setLabelVisible(True)

#         chart = QChart()
#         chart.addSeries(series)
#         chart.setTitle("Répartition des Clients")
#         chart.setAnimationOptions(QChart.SeriesAnimations) # Animation moderne

#         chart_view = QChartView(chart)
#         chart_view.setRenderHint(QPainter.Antialiasing)
#         chart_view.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #e2e8f0;")
#         return chart_view

#     def _create_vehicles_bar_chart(self):
#         """Crée un graphique en barres pour la flotte"""
#         set0 = QBarSet("Véhicules")
#         set0.append([5, 12, 8, 15, 20]) # Données d'exemple (à lier au contrôleur)

#         series = QBarSeries()
#         series.append(set0)

#         chart = QChart()
#         chart.addSeries(series)
#         chart.setTitle("Activité par Flotte")
#         chart.setAnimationOptions(QChart.SeriesAnimations)

#         axis_x = QBarCategoryAxis()
#         axis_x.append(["Flotte A", "Flotte B", "Flotte C", "Flotte D", "Flotte E"])
#         chart.addAxis(axis_x, Qt.AlignBottom)
#         series.attachAxis(axis_x)

#         chart_view = QChartView(chart)
#         chart_view.setRenderHint(QPainter.Antialiasing)
#         chart_view.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #e2e8f0;")
#         return chart_view

#     def _init_vehicles_page(self):
#         """Page contenant le tableau des véhicules"""
#         page = QWidget()
#         layout = QVBoxLayout(page) 

#         if not self.controller:
#             # Sécurité au cas où le contrôleur n'est pas encore chargé
#             return QWidget()
#         full_management_page = VehiculeModuleView(
#             controller=self.controller, 
#             current_user=self.user
#         )
        
#         return full_management_page
#         # return page

#     def _init_contacts_page(self):
#         if not self.controller:
#             return QWidget()
            
#         # On instancie la vue que vous avez fournie
#         # Elle prend en paramètres (controller, current_user)
#         client_page = ContactListView(
#             controller=self.controller, 
#             current_user=self.user
#         )
        
#         return client_page
#         # return page

#     def _init_compagnies_page(self):
#         if not self.controller:
#             return QWidget()
            
#         # On instancie la vue que vous avez fournie
#         # Elle prend en paramètres (controller, current_user)
#         client_page = CompanyTariffView(
#             controller=self.controller, 
#             current_user=self.user
#         )
        
#         return client_page
#         # return page
#     # --- HELPERS (Boutons, Cartes, Navigation) ---

#     def _create_kpi_card(self, title, value, color, bgcolor):
#         card = QFrame()
#         card.setFixedHeight(110)
#         card.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {bgcolor}; border-radius: 10px;
#                 border-left: 2px solid {color};
#             }}
#         """)
#         layout = QVBoxLayout(card)
#         t = QLabel(title)
#         t.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
#         v = QLabel(value)
#         v.setStyleSheet(f"color: white; font-size: 28px; font-weight: 900;")
#         layout.addWidget(t)
#         layout.addWidget(v)
#         return card

#     def _create_nav_btn(self, text, active=False):
#         btn = QPushButton(text)
#         btn.setFixedHeight(45)
#         btn.setCursor(Qt.PointingHandCursor)
#         self._style_nav_btn(btn, active)
#         return btn

#     def _style_nav_btn(self, btn, active):
#         if active:
#             btn.setStyleSheet("background-color: #eff6ff; color: #2563eb; font-weight: bold; border-radius: 8px; text-align: left; padding-left: 15px; border: none;")
#         else:
#             btn.setStyleSheet("background-color: transparent; color: #475569; border-radius: 8px; text-align: left; padding-left: 15px; border: none;")

#     def _switch_page(self, index, btn):
#         self.stack.setCurrentIndex(index)
#         print(index)
#         # Reset styles
#         for b in [self.btn_dash, self.btn_vehicles, self.btn_comp, self.btn_clients]:
#             self._style_nav_btn(b, False)
#         self._style_nav_btn(btn, True)

# addons/Automobiles/views/view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton, 
                             QLineEdit, QFrame, QStackedWidget, QGridLayout,
                             QScrollArea, QGraphicsDropShadowEffect, QSizePolicy)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor, QIcon, QFont, QPainter, QLinearGradient, QBrush
from addons.Automobiles.views.automobile_view import VehiculeModuleView
from addons.Automobiles.views.contacts_view import ContactListView
from addons.Automobiles.views.compagnies_view import CompanyTariffView
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PySide6.QtGui import QPainter

# Palette de couleurs moderne
class Colors:
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    PRIMARY_LIGHT = "#60a5fa"
    SECONDARY = "#64748b"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    INFO = "#06b6d4"
    BACKGROUND = "#f8fafc"
    CARD_BG = "#ffffff"
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#475569"
    BORDER = "#e2e8f0"
    SIDEBAR_BG = "#ffffff"
    SIDEBAR_ACTIVE = "#eff6ff"


class VehicleMainView(QWidget):
    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BACKGROUND};
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
        """)
        
        # Layout Principal Horizontal
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- 1. SIDEBAR NAVIGATION MODERNE ---
        self.setup_sidebar()
        
        # --- 2. ZONE DE CONTENU PRINCIPALE ---
        self.setup_content_area()

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_container, 1)

        # Connexions des boutons
        self.btn_dash.clicked.connect(lambda: self._switch_page(0, self.btn_dash))
        self.btn_vehicles.clicked.connect(lambda: self._switch_page(1, self.btn_vehicles))
        self.btn_clients.clicked.connect(lambda: self._switch_page(2, self.btn_clients))
        self.btn_comp.clicked.connect(lambda: self._switch_page(3, self.btn_comp))

    def setup_sidebar(self):
        """Configure la sidebar avec un design moderne"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-right: 1px solid {Colors.BORDER};
            }}
        """)
        
        # Ombre pour la sidebar
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(2, 0)
        self.sidebar.setGraphicsEffect(shadow)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # En-tête de la sidebar
        header = QFrame()
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        logo = QLabel("🚗 Automobile")
        logo.setStyleSheet("font-size: 28px; background: transparent;")
        
        header_layout.addWidget(logo)
        header_layout.addStretch()
        
        sidebar_layout.addWidget(header)

        # Zone de navigation
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(16, 30, 16, 30)
        nav_layout.setSpacing(8)

        nav_title = QLabel("NAVIGATION")
        nav_title.setStyleSheet(f"""
            color: {Colors.SECONDARY};
            font-weight: 600;
            font-size: 11px;
            letter-spacing: 1px;
            margin-bottom: 12px;
        """)
        nav_layout.addWidget(nav_title)

        self.btn_dash = self._create_nav_btn("📊 Tableau de Bord", active=True)
        self.btn_vehicles = self._create_nav_btn("🚗 Véhicules")
        self.btn_comp = self._create_nav_btn("🏢 Compagnies et Tarifs")
        self.btn_clients = self._create_nav_btn("👥 Clients")

        nav_layout.addWidget(self.btn_dash)
        nav_layout.addWidget(self.btn_vehicles)
        nav_layout.addWidget(self.btn_comp)
        nav_layout.addWidget(self.btn_clients)
        nav_layout.addStretch()

        sidebar_layout.addWidget(nav_container)

    def setup_content_area(self):
        """Configure la zone de contenu principale"""
        self.content_container = QWidget()
        self.content_container.setStyleSheet("background: transparent;")
        
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(24)

        # Header de la page
        page_header = QFrame()
        page_header.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 20px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        page_header.setFixedHeight(70)
        
        header_layout = QHBoxLayout(page_header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        
        self.page_title = QLabel("Tableau de Bord")
        self.page_title.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {Colors.TEXT_PRIMARY};
        """)
        
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()
        
        content_layout.addWidget(page_header)

        # Cartes KPI
        self.setup_kpi_cards()
        content_layout.addLayout(self.kpi_layout)

        # Stacked Widget
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("""
            QStackedWidget {
                background: transparent;
            }
        """)
        
        self.page_dashboard = self._init_dashboard_page()
        self.page_vehicles = self._init_vehicles_page()
        self.page_clients = self._init_contacts_page()
        self.page_compagnies = self._init_compagnies_page()
        
        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_vehicles)
        self.stack.addWidget(self.page_clients)
        self.stack.addWidget(self.page_compagnies)
        
        content_layout.addWidget(self.stack)

    def setup_kpi_cards(self):
        """Configure les cartes KPI modernes"""
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(20)
        
        kpi_data = [
            {"title": "Véhicules", "value": "142", "trend": "+12", "color": Colors.PRIMARY, "icon": "🚗"},
            {"title": "Flottes", "value": "12", "trend": "+3", "color": Colors.SUCCESS, "icon": "🏢"},
            {"title": "Entreprises", "value": "08", "trend": "+2", "color": Colors.WARNING, "icon": "🏭"},
            {"title": "Particuliers", "value": "89", "trend": "+8", "color": Colors.INFO, "icon": "👤"}
        ]
        
        for data in kpi_data:
            card = self._create_modern_kpi_card(data)
            self.kpi_layout.addWidget(card)

    def _create_modern_kpi_card(self, data):
        """Crée une carte KPI moderne et élégante"""
        card = QFrame()
        card.setFixedHeight(120)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 20px;
                border: 1px solid {Colors.BORDER};
            }}
            QFrame:hover {{
                border-color: {data['color']};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 white, stop:1 {data['color']}08);
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        
        # Icône
        icon_container = QFrame()
        icon_container.setFixedSize(52, 52)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {data['color']}15;
                border-radius: 16px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon = QLabel(data['icon'])
        icon.setStyleSheet(f"font-size: 28px; background: transparent;")
        icon_layout.addWidget(icon)
        
        # Infos
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        value_label = QLabel(data['value'])
        value_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 800;
            color: {data['color']};
        """)
        
        title_label = QLabel(data['title'])
        title_label.setStyleSheet(f"""
            color: {Colors.TEXT_SECONDARY};
            font-size: 13px;
            font-weight: 500;
        """)
        
        trend_label = QLabel(f"▲ {data['trend']} ce mois")
        trend_label.setStyleSheet(f"""
            color: {Colors.SUCCESS};
            font-size: 11px;
        """)
        
        info_layout.addWidget(value_label)
        info_layout.addWidget(title_label)
        info_layout.addWidget(trend_label)
        
        layout.addWidget(icon_container)
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return card

    def _create_nav_btn(self, text, active=False):
        """Crée un bouton de navigation moderne"""
        btn = QPushButton(text)
        btn.setFixedHeight(48)
        btn.setCursor(Qt.PointingHandCursor)
        self._style_nav_btn(btn, active)
        return btn

    def _style_nav_btn(self, btn, active):
        """Applique le style aux boutons de navigation"""
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {Colors.SIDEBAR_ACTIVE};
                    color: {Colors.PRIMARY};
                    font-weight: 600;
                    border-radius: 12px;
                    text-align: left;
                    padding-left: 16px;
                    border: none;
                }}
                QPushButton:hover {{
                    background: {Colors.PRIMARY}10;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {Colors.TEXT_SECONDARY};
                    border-radius: 12px;
                    text-align: left;
                    padding-left: 16px;
                    border: none;
                }}
                QPushButton:hover {{
                    background: {Colors.PRIMARY}08;
                    color: {Colors.PRIMARY};
                }}
            """)

    def _switch_page(self, index, btn):
        """Change la page active avec animation"""
        self.stack.setCurrentIndex(index)
        
        # Titres des pages
        titles = ["Tableau de Bord", "Gestion des Véhicules", "Gestion des Clients", "Compagnies et Tarifs"]
        self.page_title.setText(titles[index])
        
        # Reset styles
        for b in [self.btn_dash, self.btn_vehicles, self.btn_comp, self.btn_clients]:
            self._style_nav_btn(b, False)
        self._style_nav_btn(btn, True)

    # --- PAGES ---

    def _init_dashboard_page(self):
        """Page Dashboard avec graphiques modernes"""
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        
        # ScrollArea pour le dashboard
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)
        
        # Section Graphiques
        charts_title = QLabel("📊 Analyses et Statistiques")
        charts_title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 700;
            color: {Colors.TEXT_PRIMARY};
            margin-bottom: 8px;
        """)
        layout.addWidget(charts_title)
        
        charts_grid = QGridLayout()
        charts_grid.setSpacing(20)
        
        # Graphique Camembert
        pie_chart = self._create_contacts_pie_chart()
        charts_grid.addWidget(pie_chart, 0, 0)
        
        # Graphique Barres
        bar_chart = self._create_vehicles_bar_chart()
        charts_grid.addWidget(bar_chart, 0, 1)
        
        layout.addLayout(charts_grid)
        
        scroll.setWidget(container)
        
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        
        return page

    def _create_contacts_pie_chart(self):
        """Crée un graphique en camembert stylisé"""
        series = QPieSeries()
        
        stats = self.controller.contacts.get_contact_stats() if self.controller else {'Physique': 10, 'Morale': 5}
        series.append("Particuliers", stats.get('Physique', 10))
        series.append("Entreprises", stats.get('Morale', 5))
        
        # Style du camembert
        slices = series.slices()
        if len(slices) > 0:
            slice1 = slices[0]
            slice1.setExploded(True)
            slice1.setLabelVisible(True)
            slice1.setLabelColor(QColor(Colors.TEXT_PRIMARY))
            slice1.setBrush(QColor(Colors.PRIMARY))
        
        if len(slices) > 1:
            slice2 = slices[1]
            slice2.setLabelVisible(True)
            slice2.setLabelColor(QColor(Colors.TEXT_PRIMARY))
            slice2.setBrush(QColor(Colors.SUCCESS))
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Répartition des Clients")
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundVisible(False)
        chart.setTheme(QChart.ChartThemeLight)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(350)
        chart_view.setStyleSheet(f"""
            QChartView {{
                background: white;
                border-radius: 20px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        chart_view.setGraphicsEffect(shadow)
        
        return chart_view
    
    def _create_vehicles_bar_chart(self):
        """Crée un graphique en barres stylisé"""
        set0 = QBarSet("Véhicules")
        data = [5, 12, 8, 15, 20]
        set0.append(data)
        set0.setColor(QColor(Colors.PRIMARY))
        
        series = QBarSeries()
        series.append(set0)
        series.setBarWidth(0.6)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Activité par Flotte")
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundVisible(False)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(["Flotte A", "Flotte B", "Flotte C", "Flotte D", "Flotte E"])
        axis_x.setTitleText("Flottes")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = chart.axisY()
        # axis_y.setTitleText("Nombre de véhicules")
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(350)
        chart_view.setStyleSheet(f"""
            QChartView {{
                background: white;
                border-radius: 20px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        chart_view.setGraphicsEffect(shadow)
        
        return chart_view

    def _init_vehicles_page(self):
        """Page de gestion des véhicules"""
        if not self.controller:
            return QWidget()
        
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        full_management_page = VehiculeModuleView(
            controller=self.controller, 
            current_user=self.user
        )
        layout.addWidget(full_management_page)
        
        return page

    def _init_contacts_page(self):
        """Page de gestion des contacts"""
        if not self.controller:
            return QWidget()
        
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        client_page = ContactListView(
            controller=self.controller, 
            current_user=self.user
        )
        layout.addWidget(client_page)
        
        return page

    def _init_compagnies_page(self):
        """Page de gestion des compagnies"""
        if not self.controller:
            return QWidget()
        
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        compagnies_page = CompanyTariffView(
            controller=self.controller, 
            current_user=self.user
        )
        layout.addWidget(compagnies_page)
        
        return page