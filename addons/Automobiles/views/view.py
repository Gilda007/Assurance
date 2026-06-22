
# addons/Automobiles/views/main_view.py
"""
Vue principale modernisée avec design professionnel
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QStackedWidget, QPushButton, QLineEdit,
    QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor

from addons.Automobiles.views.style import Colors, Fonts, Spacing, apply_global_style
from addons.Automobiles.views.widgets.modern_card import ModernCard


class ModernSidebarButton(QPushButton):
    """Bouton de navigation moderne"""
    
    def __init__(self, text: str, icon: str, is_active: bool = False):
        super().__init__(text)
        self.icon_text = icon
        self.is_active = is_active
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(self.get_style())
    
    def get_style(self):
        if self.is_active:
            return f"""
                QPushButton {{
                    background-color: {Colors.SIDEBAR_ACTIVE};
                    color: {Colors.PRIMARY};
                    font-weight: {Fonts.SEMIBOLD};
                    border-radius: 12px;
                    text-align: left;
                    padding-left: 16px;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {Colors.PRIMARY}15;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {Colors.TEXT_SECONDARY};
                    border-radius: 12px;
                    text-align: left;
                    padding-left: 16px;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {Colors.PRIMARY}10;
                    color: {Colors.PRIMARY};
                }}
            """
    
    def set_active(self, active: bool):
        self.is_active = active
        self.setStyleSheet(self.get_style())


class StatsCard(ModernCard):
    """Carte de statistiques avec valeur animée"""
    
    def __init__(self, title: str, value: int, icon: str, color: str, trend: str = None):
        super().__init__(title=None, icon=icon)
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self.trend = trend
        self.setup_content()
    
    def setup_content(self):
        # Valeur
        self.value_label = QLabel(str(self.value))
        self.value_label.setStyleSheet(f"""
            font-size: {Fonts.H1}px;
            font-weight: {Fonts.BOLD};
            color: {self.color};
        """)
        
        # Titre
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-size: {Fonts.SMALL}px;
            color: {Colors.TEXT_SECONDARY};
            letter-spacing: 0.5px;
        """)
        
        # Tendance
        if self.trend:
            trend_layout = QHBoxLayout()
            trend_layout.setSpacing(Spacing.XS)
            
            trend_icon = QLabel("▲" if "+" in self.trend else "▼")
            trend_icon.setStyleSheet(f"""
                color: {Colors.SUCCESS if "+" in self.trend else Colors.DANGER};
                font-size: {Fonts.SMALL}px;
            """)
            
            trend_label = QLabel(self.trend)
            trend_label.setStyleSheet(f"""
                color: {Colors.SUCCESS if "+" in self.trend else Colors.DANGER};
                font-size: {Fonts.SMALL}px;
                font-weight: {Fonts.MEDIUM};
            """)
            
            trend_layout.addWidget(trend_icon)
            trend_layout.addWidget(trend_label)
            trend_layout.addStretch()
            
            self.main_layout.addLayout(trend_layout)
        
        self.main_layout.addWidget(self.value_label, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(title_label, alignment=Qt.AlignCenter)
    
    def animate_value(self, new_value: int):
        """Anime la valeur de la carte"""
        self.value = new_value
        self.value_label.setText(str(new_value))


class VehicleMainView(QWidget):
    """Vue principale modernisée"""
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BACKGROUND};
            }}
        """)
        
        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Contenu principal
        self.setup_content_area()
        main_layout.addWidget(self.content_container, 1)
    
    def setup_sidebar(self):
        """Configure la sidebar moderne"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.WHITE};
                border-right: 1px solid {Colors.BORDER};
            }}
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(Spacing.LG, Spacing.XL, Spacing.LG, Spacing.XL)
        sidebar_layout.setSpacing(Spacing.XL)
        
        # Logo
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_icon = QLabel("🚗")
        logo_icon.setStyleSheet("font-size: 32px;")
        
        logo_text = QLabel("AutoAssure")
        logo_text.setStyleSheet(f"""
            font-size: {Fonts.H4}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
        """)
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        sidebar_layout.addWidget(logo_widget)
        
        # Navigation
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setSpacing(Spacing.SM)
        
        nav_title = QLabel("MENU PRINCIPAL")
        nav_title.setStyleSheet(f"""
            font-size: {Fonts.CAPTION}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_MUTED};
            letter-spacing: 1px;
            margin-bottom: {Spacing.MD}px;
        """)
        nav_layout.addWidget(nav_title)
        
        # Boutons de navigation
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊", "Tableau de bord"),
            ("vehicles", "🚗", "Véhicules"),
            ("contacts", "👥", "Clients"),
            ("companies", "🏢", "Compagnies"),
            ("contracts", "📄", "Contrats"),
            ("import", "📥", "Import ASAC"),
            ("reports", "📈", "Rapports"),
            ("settings", "⚙️", "Paramètres"),
        ]
        
        for key, icon, text in nav_items:
            btn = ModernSidebarButton(f"  {icon}  {text}", icon, key == "dashboard")
            btn.clicked.connect(lambda checked, k=key: self.switch_page(k))
            nav_layout.addWidget(btn)
            self.nav_buttons[key] = btn
        
        nav_layout.addStretch()
        sidebar_layout.addWidget(nav_widget)
        
        # Footer
        footer = QWidget()
        footer_layout = QVBoxLayout(footer)
        footer_layout.setSpacing(Spacing.SM)
        
        user_label = QLabel(f"👤 {self.user.username if self.user else 'Utilisateur'}")
        user_label.setStyleSheet(f"""
            font-size: {Fonts.SMALL}px;
            color: {Colors.TEXT_SECONDARY};
        """)
        
        version_label = QLabel("Version 2.0.0")
        version_label.setStyleSheet(f"""
            font-size: {Fonts.CAPTION}px;
            color: {Colors.TEXT_MUTED};
        """)
        
        footer_layout.addWidget(user_label)
        footer_layout.addWidget(version_label)
        sidebar_layout.addWidget(footer)
    
    def setup_content_area(self):
        """Configure la zone de contenu principale"""
        self.content_container = QWidget()
        self.content_container.setStyleSheet("background: transparent;")
        
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        content_layout.setSpacing(Spacing.XL)
        
        # En-tête
        header = self.setup_header()
        content_layout.addWidget(header)
        
        # Zone de contenu empilé
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")
        
        # Pages
        self.pages = {}
        self.init_pages()
        
        content_layout.addWidget(self.stacked_widget)
    
    def setup_header(self):
        """Configure l'en-tête moderne"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: transparent;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Titre de page
        self.page_title = QLabel("Tableau de Bord")
        self.page_title.setStyleSheet(f"""
            font-size: {Fonts.H2}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
        """)
        
        # Barre de recherche
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(Spacing.SM)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher...")
        self.search_input.setFixedWidth(250)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {Colors.BORDER};
                border-radius: 20px;
                padding: 8px 16px;
                background-color: {Colors.WHITE};
            }}
            QLineEdit:focus {{
                border-color: {Colors.PRIMARY};
            }}
        """)
        
        search_layout.addWidget(self.search_input)
        
        # Bouton notifications
        notif_btn = QPushButton("🔔")
        notif_btn.setFixedSize(40, 40)
        notif_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 20px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {Colors.GRAY_100};
            }}
        """)
        
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()
        header_layout.addWidget(search_widget)
        header_layout.addWidget(notif_btn)
        
        return header
    
    def init_pages(self):
        """Initialise les différentes pages"""
        # À implémenter avec les vues spécifiques
        from addons.Automobiles.views.dashboard_view import DashboardView
        from addons.Automobiles.views.automobile_view import VehiculeModuleView
        from addons.Automobiles.views.contacts_view import ContactListView
        from addons.Automobiles.views.compagnies_view import CompanyTariffView
        from addons.Automobiles.views.contract_view import ContractView
        from addons.Automobiles.views.reports_view import ReportView
        from addons.Automobiles.views.settings_view import SettingsView
        from addons.Automobiles.views.asac_import_view import ASACImportView 
        
        self.pages["dashboard"] = DashboardView(self.controller, self.user)
        self.pages["vehicles"] = VehiculeModuleView(self.controller, self.user)
        self.pages["contacts"] = ContactListView(self.controller, self.user)
        self.pages["companies"] = CompanyTariffView(self.controller, self.user)
        self.pages["contracts"] = ContractView(self.controller, self.user)
        self.pages["import"] = ASACImportView(self.controller, self.user)
        self.pages["reports"] = ReportView(self.controller, self.user)
        self.pages["settings"] = SettingsView(self.controller, self.user)
        
        for key, page in self.pages.items():
            self.stacked_widget.addWidget(page)
    
    def switch_page(self, page_key: str):
        """Change de page avec animation"""
        # Mettre à jour les boutons
        for key, btn in self.nav_buttons.items():
            btn.set_active(key == page_key)
        
        # Mettre à jour le titre
        titles = {
            "dashboard": "Tableau de Bord",
            "vehicles": "Gestion des Véhicules",
            "contacts": "Gestion des Clients",
            "companies": "Compagnies d'Assurance",
            "contracts": "Gestion des Contrats",
            "import": "Import ASAC",
            "reports": "Rapports et Statistiques",
            "settings": "Paramètres"
        }
        self.page_title.setText(titles.get(page_key, page_key))
        
        # Changer de page avec animation
        index = list(self.pages.keys()).index(page_key)
        self.animate_page_transition(index)
    
    def animate_page_transition(self, index: int):
        """Anime la transition entre pages"""
        self.stacked_widget.setCurrentIndex(index)
        # Ici on pourrait ajouter une animation de fondu
    
    def load_initial_data(self):
        """Charge les données initiales"""
        # Déclencher le chargement des données
        pass

    # addons/Automobiles/views/view.py - Dans VehicleMainView

    def _lazy_load_data(self):
        """Charge les données en arrière-plan après l'affichage"""
        if self._initialized:
            return
        
        self._initialized = True
        
        # ✅ Rollback pour éviter les transactions bloquées
        try:
            if hasattr(self.controller, 'db_session'):
                self.controller.db_session.rollback()
        except:
            pass
        
        # Chargement léger d'abord
        self._load_light_data()
        
        # Puis chargement complet en arrière-plan
        QTimer.singleShot(500, self._load_full_data)