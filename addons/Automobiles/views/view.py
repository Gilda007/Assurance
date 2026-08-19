
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
import qtawesome as qta

from addons.Automobiles.views.style import Colors, Fonts, Spacing, apply_global_style
from addons.Automobiles.views.widgets.modern_card import ModernCard
from addons.Automobiles.security.access_control import Permissions, SecurityManager, Role



import qtawesome as qta

# class ModernSidebarButton(QPushButton):
#     """Bouton de navigation moderne avec Font Awesome - Style code.html"""
    
#     # Mapping des icônes Font Awesome
#     ICON_MAP = {
#         "dashboard": "fa5s.chart-pie",
#         "vehicles": "fa5s.car",
#         "contacts": "fa5s.users",
#         "companies": "fa5s.building",
#         "contracts": "fa5s.file-contract",
#         "sinistres": "fa5s.exclamation-triangle",
#         "expertises": "fa5s.search-plus",
#         "garages": "fa5s.tools",
#         "import": "fa5s.upload",
#         "reports": "fa5s.chart-line",
#         "settings": "fa5s.cog",
#     }
    
#     def __init__(self, text: str, icon_key: str, is_active: bool = False):
#         super().__init__()
#         self.icon_key = icon_key
#         self.button_text = text
#         self.is_active = is_active
#         self.setup_ui()
    
#     def setup_ui(self):
#         self.setFixedHeight(44)
#         self.setCursor(Qt.PointingHandCursor)
#         self.setStyleSheet(self.get_style())
        
#         self.setLayout(QHBoxLayout())
#         self.layout().setContentsMargins(12, 0, 16, 0)
#         self.layout().setSpacing(10)
        
#         # ✅ Icône Font Awesome
#         self.icon_label = QLabel()
#         self.update_icon()
        
#         # Texte
#         self.text_label = QLabel(self.button_text)
#         self.text_label.setStyleSheet("""
#             font-size: 13px;
#             background: transparent;
#             border: none;
#             font-weight: 500;
#         """)
        
#         self.layout().addWidget(self.icon_label)
#         self.layout().addWidget(self.text_label)
#         self.layout().addStretch()
        
#         self.update_style()
    
#     def update_icon(self):
#         """Met à jour l'icône Font Awesome"""
#         icon_name = self.ICON_MAP.get(self.icon_key, "fa5s.circle")
        
#         if self.is_active:
#             color = Colors.ON_SECONDARY_FIXED_VARIANT
#         else:
#             color = Colors.ON_SURFACE_VARIANT
        
#         icon = qta.icon(icon_name, color=color)
#         self.icon_label.setPixmap(icon.pixmap(18, 18))
#         self.icon_label.setStyleSheet("background: transparent; border: none;")
    
#     def get_style(self):
#         """Retourne le style selon l'état actif"""
#         if self.is_active:
#             return f"""
#                 QPushButton {{
#                     background-color: {Colors.SECONDARY_FIXED};
#                     color: {Colors.ON_SECONDARY_FIXED_VARIANT};
#                     border-left: 4px solid {Colors.PRIMARY};
#                     border-radius: 0 8px 8px 0;
#                     font-weight: 600;
#                     border-top-right-radius: 8px;
#                     border-bottom-right-radius: 8px;
#                     border-top-left-radius: 0px;
#                     border-bottom-left-radius: 0px;
#                     text-align: left;
#                     padding: 0px;
#                 }}
#                 QPushButton:hover {{
#                     background-color: {Colors.PRIMARY}15;
#                 }}
#             """
#         else:
#             return f"""
#                 QPushButton {{
#                     background-color: transparent;
#                     color: {Colors.ON_SURFACE_VARIANT};
#                     border: none;
#                     border-radius: 8px;
#                     text-align: left;
#                     padding: 0px;
#                 }}
#                 QPushButton:hover {{
#                     background-color: {Colors.SURFACE_VARIANT};
#                     color: {Colors.PRIMARY};
#                 }}
#             """
    
#     def update_style(self):
#         """Met à jour le style du bouton"""
#         self.setStyleSheet(self.get_style())
#         self.update_icon()
        
#         if self.is_active:
#             self.text_label.setStyleSheet(f"""
#                 font-size: 13px;
#                 color: {Colors.ON_SECONDARY_FIXED_VARIANT};
#                 background: transparent;
#                 border: none;
#                 font-weight: 600;
#             """)
#         else:
#             self.text_label.setStyleSheet(f"""
#                 font-size: 13px;
#                 color: {Colors.ON_SURFACE_VARIANT};
#                 background: transparent;
#                 border: none;
#                 font-weight: 500;
#             """)
    
#     def set_active(self, active: bool):
#         self.is_active = active
#         self.update_style()


class ModernSidebarButton(QPushButton):
    """Bouton de navigation moderne avec Font Awesome - Style code.html"""
    
    # Mapping des icônes Font Awesome
    ICON_MAP = {
        "dashboard": "fa5s.chart-pie",
        "vehicles": "fa5s.car",
        "contacts": "fa5s.users",
        "companies": "fa5s.building",
        "contracts": "fa5s.file-contract",
        "sinistres": "fa5s.exclamation-triangle",
        "expertises": "fa5s.search-plus",
        "garages": "fa5s.tools",
        "import": "fa5s.upload",
        "reports": "fa5s.chart-line",
        "settings": "fa5s.cog",
    }
    
    def __init__(self, text: str, icon_key: str, is_active: bool = False):
        super().__init__()
        self.icon_key = icon_key
        self.button_text = text
        self.is_active = is_active
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(self.get_style())
        
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(12, 0, 16, 0)
        self.layout().setSpacing(10)
        
        # Icône Font Awesome
        self.icon_label = QLabel()
        self.update_icon()
        
        # Texte
        self.text_label = QLabel(self.button_text)
        self.text_label.setStyleSheet("""
            font-size: 13px;
            background: transparent;
            border: none;
            font-weight: 500;
        """)
        
        self.layout().addWidget(self.icon_label)
        self.layout().addWidget(self.text_label)
        self.layout().addStretch()
        
        self.update_style()
    
    def update_icon(self):
        """Met à jour l'icône Font Awesome avec la couleur bleue"""
        icon_name = self.ICON_MAP.get(self.icon_key, "fa5s.circle")
        
        # ✅ Utiliser la couleur bleue pour les icônes
        if self.is_active:
            # Bleu foncé pour l'état actif
            color = Colors.PRIMARY  # ou "#1e40af"
        else:
            # Bleu clair/moyen pour l'état inactif
            color = Colors.ON_SECONDARY_FIXED_VARIANT  # "#2563eb"
        
        icon = qta.icon(icon_name, color=color)
        self.icon_label.setPixmap(icon.pixmap(18, 18))
        self.icon_label.setStyleSheet("background: transparent; border: none;")
    
    def get_style(self):
        """Retourne le style selon l'état actif"""
        if self.is_active:
            return f"""
                QPushButton {{
                    background-color: {Colors.SECONDARY_FIXED};
                    color: {Colors.PRIMARY};
                    border-left: 4px solid {Colors.PRIMARY};
                    border-radius: 0 8px 8px 0;
                    font-weight: 600;
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                    border-top-left-radius: 0px;
                    border-bottom-left-radius: 0px;
                    text-align: left;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: {Colors.PRIMARY}15;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {Colors.ON_SURFACE_VARIANT};
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: {Colors.SURFACE_VARIANT};
                    color: {Colors.PRIMARY};
                }}
            """
    
    def update_style(self):
        """Met à jour le style du bouton"""
        self.setStyleSheet(self.get_style())
        self.update_icon()
        
        if self.is_active:
            self.text_label.setStyleSheet(f"""
                font-size: 13px;
                color: {Colors.PRIMARY};
                background: transparent;
                border: none;
                font-weight: 600;
            """)
        else:
            self.text_label.setStyleSheet(f"""
                font-size: 13px;
                color: {Colors.ON_SURFACE_VARIANT};
                background: transparent;
                border: none;
                font-weight: 500;
            """)
    
    def set_active(self, active: bool):
        self.is_active = active
        self.update_style()

# addons/Automobiles/views/view.py - StatsCard modifié

class StatsCard(ModernCard):
    """Carte de statistiques avec icône Font Awesome"""
    
    def __init__(self, title: str, value: int, icon_name: str, color: str, trend: str = None):
        super().__init__(title=None)
        self.title = title
        self.value = value
        self.icon_name = icon_name
        self.color = color
        self.trend = trend
        self.setup_content()
    
    def setup_content(self):
        # Icône Font Awesome
        icon_layout = QHBoxLayout()
        icon_label = QLabel()
        icon = qta.icon(self.icon_name, color=self.color)
        icon_label.setPixmap(icon.pixmap(32, 32))
        icon_label.setStyleSheet("background: transparent; border: none;")
        icon_layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        self.main_layout.addLayout(icon_layout)
        
        # Valeur
        self.value_label = QLabel(str(self.value))
        self.value_label.setStyleSheet(f"""
            font-size: {Fonts.H1}px;
            font-weight: {Fonts.BOLD};
            color: {self.color};
            background: transparent;
            border: none;
        """)
        self.main_layout.addWidget(self.value_label, alignment=Qt.AlignCenter)
        
        # Titre
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-size: {Fonts.SMALL}px;
            color: {Colors.TEXT_SECONDARY};
            letter-spacing: 0.5px;
            background: transparent;
            border: none;
        """)
        self.main_layout.addWidget(title_label, alignment=Qt.AlignCenter)

class VehicleMainView(QWidget):
    """Vue principale modernisée"""

    PAGE_PERMISSIONS = {
        "dashboard": None,
        "vehicles": Permissions.VEHICLE_VIEW,
        "contacts": Permissions.CONTACT_VIEW,
        "companies": Permissions.CONTACT_VIEW,
        "contracts": Permissions.CONTRACT_VIEW,
        "import": Permissions.VEHICLE_EXPORT,
        "reports": Permissions.REPORT_VIEW,
        "settings": "admin_only",
        "sinistres": Permissions.SINISTRE_VIEW,
        "expertises": Permissions.EXPERTISE_VIEW,
        "garages": Permissions.GARAGE_VIEW,
    }
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.user_role = getattr(user, 'role', None) if user is not None else None
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
        """Configure la sidebar moderne avec Font Awesome"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.WHITE};
                border-right: 1px solid {Colors.BORDER};
            }}
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(16)
        
        # Logo avec icône Font Awesome
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(12)
        
        logo_icon_label = QLabel()
        logo_icon = qta.icon('fa5s.car', color='#00288e')
        logo_icon_label.setPixmap(logo_icon.pixmap(32, 32))
        logo_icon_label.setStyleSheet("background: transparent; border: none;")
        
        logo_text_layout = QVBoxLayout()
        logo_text_layout.setSpacing(0)
        
        logo_text = QLabel("AutoAssure")
        logo_text.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 700;
            color: {Colors.TEXT_PRIMARY};
            background: transparent;
            border: none;
        """)
        
        logo_subtext = QLabel("Management Portal")
        logo_subtext.setStyleSheet(f"""
            font-size: 11px;
            color: {Colors.TEXT_MUTED};
            background: transparent;
            border: none;
        """)
        
        logo_text_layout.addWidget(logo_text)
        logo_text_layout.addWidget(logo_subtext)
        
        logo_layout.addWidget(logo_icon_label)
        logo_layout.addLayout(logo_text_layout)
        logo_layout.addStretch()
        sidebar_layout.addWidget(logo_widget)
        
        # Navigation
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setSpacing(4)
        
        nav_title = QLabel("MENU PRINCIPAL")
        nav_title.setStyleSheet(f"""
            font-size: 10px;
            font-weight: 700;
            color: {Colors.TEXT_MUTED};
            letter-spacing: 1px;
            background: transparent;
            border: none;
            padding-bottom: 8px;
        """)
        nav_layout.addWidget(nav_title)
        
        # ✅ Boutons de navigation avec Font Awesome
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "Tableau de bord"),
            ("vehicles", "Véhicules"),
            ("contacts", "Clients"),
            ("companies", "Compagnies"),
            ("contracts", "Contrats"),
            ("sinistres", "Sinistres"),
            ("expertises", "Expertises"),
            ("garages", "Garages"),
            ("import", "Import ASAC"),
            ("reports", "Rapports"),
            ("settings", "Paramètres"),
        ]
        
        for key, text in nav_items:
            if not self.can_access_page(key):
                continue
            btn = ModernSidebarButton(text, key, key == "dashboard")
            btn.clicked.connect(lambda checked, k=key: self.switch_page(k))
            nav_layout.addWidget(btn)
            self.nav_buttons[key] = btn
        
        nav_layout.addStretch()
        sidebar_layout.addWidget(nav_widget)
        
        # Footer
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                border-top: 1px solid {Colors.BORDER};
                padding-top: 8px;
            }}
        """)
        footer_layout = QVBoxLayout(footer)
        footer_layout.setSpacing(4)
        footer_layout.setContentsMargins(0, 8, 0, 0)
        
        footer_btn = QPushButton()
        footer_layout_h = QHBoxLayout()
        footer_layout_h.setContentsMargins(12, 8, 12, 8)
        footer_layout_h.setSpacing(10)
        
        user_icon = qta.icon('fa5s.user', color='#444653')
        user_icon_label = QLabel()
        user_icon_label.setPixmap(user_icon.pixmap(16, 16))
        
        user_text = QLabel("Admin")
        user_text.setStyleSheet(f"""
            font-size: 13px;
            color: {Colors.ON_SURFACE_VARIANT};
            background: transparent;
            border: none;
        """)
        
        footer_layout_h.addWidget(user_icon_label)
        footer_layout_h.addWidget(user_text)
        footer_layout_h.addStretch()
        
        footer_btn.setLayout(footer_layout_h)
        footer_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {Colors.SURFACE_VARIANT};
            }}
        """)
        footer_btn.setCursor(Qt.PointingHandCursor)
        
        footer_layout.addWidget(footer_btn)
        sidebar_layout.addWidget(footer)
    
    def setup_content_area(self):
        """Configure la zone de contenu principale"""
        self.content_container = QWidget()
        self.content_container.setStyleSheet("background: transparent;")
        
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        content_layout.setSpacing(Spacing.XL)
        
        # En-tête
        # header = self.setup_header()
        # content_layout.addWidget(header)
        
        # Zone de contenu empilé
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")
        
        # Pages
        self.pages = {}
        self.init_pages()
        
        content_layout.addWidget(self.stacked_widget)

    def refresh_data(self):
        """Rafraîchit les données du tableau de bord"""
        # Chercher le dashboard dans la pile
        for i in range(self.stacked_widget.count()):
            widget = self.stacked_widget.widget(i)
            if widget.__class__.__name__ == "DashboardView":
                if hasattr(widget, 'refresh_data'):
                    widget.refresh_data()
                elif hasattr(widget, 'refresh'):
                    widget.refresh()
                elif hasattr(widget, 'load_data'):
                    widget.load_data()
                break
   
    # def setup_header(self):
    #     """Configure l'en-tête moderne - style photo"""
    #     header = QFrame()
    #     header.setStyleSheet(f"""
    #         QFrame {{
    #             background: {Colors.WHITE};
    #             border: 1px solid {Colors.BORDER};
    #             border-radius: 12px;
    #             padding: 12px 20px;
    #         }}
    #     """)
        
    #     header_layout = QHBoxLayout(header)
    #     header_layout.setContentsMargins(0, 0, 0, 0)
    #     header_layout.setSpacing(16)
        
    #     # ✅ Titre de page avec icône Font Awesome
    #     title_layout = QHBoxLayout()
    #     title_layout.setSpacing(10)
        
    #     page_icon = qta.icon('fa5s.chart-pie', color=Colors.PRIMARY)
    #     page_icon_label = QLabel()
    #     page_icon_label.setPixmap(page_icon.pixmap(20, 20))
    #     page_icon_label.setStyleSheet("background: transparent; border: none;")
        
    #     self.page_title = QLabel("Tableau de Bord")
    #     self.page_title.setStyleSheet(f"""
    #         font-size: {Fonts.H4}px;
    #         font-weight: {Fonts.BOLD};
    #         color: {Colors.TEXT_PRIMARY};
    #         background: transparent;
    #         border: none;
    #     """)
        
    #     title_layout.addWidget(page_icon_label)
    #     title_layout.addWidget(self.page_title)
        
    #     header_layout.addLayout(title_layout)
    #     header_layout.addStretch()
        
    #     # ✅ Barre de recherche
    #     search_widget = QWidget()
    #     search_layout = QHBoxLayout(search_widget)
    #     search_layout.setContentsMargins(0, 0, 0, 0)
    #     search_layout.setSpacing(8)
        
    #     self.search_input = QLineEdit()
    #     self.search_input.setPlaceholderText("🔍 Rechercher un véhicule, client, contrat...")
    #     self.search_input.setFixedWidth(280)
    #     self.search_input.setStyleSheet(f"""
    #         QLineEdit {{
    #             border: 1px solid {Colors.BORDER};
    #             border-radius: 20px;
    #             padding: 8px 16px;
    #             background-color: {Colors.GRAY_50};
    #             font-size: 13px;
    #             color: {Colors.TEXT_PRIMARY};
    #         }}
    #         QLineEdit:focus {{
    #             border-color: {Colors.PRIMARY};
    #             background-color: {Colors.WHITE};
    #         }}
    #     """)
    #     search_layout.addWidget(self.search_input)
        
    #     # ✅ Bouton Actualiser
    #     refresh_btn = QPushButton()
    #     refresh_icon = qta.icon('fa5s.sync-alt', color=Colors.PRIMARY)
    #     refresh_btn.setIcon(refresh_icon)
    #     refresh_btn.setFixedSize(36, 36)
    #     refresh_btn.setStyleSheet(f"""
    #         QPushButton {{
    #             background-color: {Colors.PRIMARY};
    #             border: none;
    #             border-radius: 18px;
    #         }}
    #         QPushButton:hover {{
    #             background-color: {Colors.PRIMARY_DARK};
    #         }}
    #     """)
    #     refresh_btn.setCursor(Qt.PointingHandCursor)
    #     refresh_btn.clicked.connect(self.refresh_data)
        
    #     # ✅ Bouton notifications
    #     notif_btn = QPushButton()
    #     notif_icon = qta.icon('fa5s.bell', color=Colors.TEXT_MUTED)
    #     notif_btn.setIcon(notif_icon)
    #     notif_btn.setFixedSize(36, 36)
    #     notif_btn.setStyleSheet(f"""
    #         QPushButton {{
    #             background-color: {Colors.GRAY_50};
    #             border: 1px solid {Colors.BORDER};
    #             border-radius: 18px;
    #         }}
    #         QPushButton:hover {{
    #             background-color: {Colors.GRAY_100};
    #         }}
    #     """)
    #     notif_btn.setCursor(Qt.PointingHandCursor)
        
    #     # ✅ Profil utilisateur
    #     user_btn = QPushButton()
    #     user_btn.setFixedSize(36, 36)
    #     user_btn.setStyleSheet(f"""
    #         QPushButton {{
    #             background-color: {Colors.PRIMARY};
    #             border: none;
    #             border-radius: 18px;
    #             font-weight: {Fonts.BOLD};
    #             color: {Colors.WHITE};
    #             font-size: 14px;
    #         }}
    #         QPushButton:hover {{
    #             background-color: {Colors.PRIMARY_DARK};
    #         }}
    #     """)
    #     user_btn.setText("AD")
    #     user_btn.setCursor(Qt.PointingHandCursor)
        
    #     search_layout.addWidget(refresh_btn)
    #     search_layout.addWidget(notif_btn)
    #     search_layout.addWidget(user_btn)
        
    #     header_layout.addWidget(search_widget)
        
    #     return header


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
        from addons.Automobiles.views.sinistre.sinistre_list_view import SinistreListView
        from addons.Automobiles.views.expertise.expertise_list_view import ExpertiseListView
        from addons.Automobiles.views.garages.garage_list_view import GarageListView
        
        page_factories = {
            "dashboard": lambda: DashboardView(self.controller, self.user),
            "vehicles": lambda: VehiculeModuleView(self.controller, self.user),
            "contacts": lambda: ContactListView(self.controller, self.user),
            "companies": lambda: CompanyTariffView(self.controller, self.user),
            "contracts": lambda: ContractView(self.controller, self.user),
            "import": lambda: ASACImportView(self.controller, self.user),
            "reports": lambda: ReportView(self.controller, self.user),
            "settings": lambda: SettingsView(self.controller, self.user),
            "sinistres": lambda: SinistreListView(self.controller, self.user),
            "expertises": lambda: ExpertiseListView(self.controller, self.user),
            "garages": lambda: GarageListView(self.controller, self.user),
        }
        
        for key, factory in page_factories.items():
            if not self.can_access_page(key):
                continue
            self.pages[key] = factory()
            self.stacked_widget.addWidget(self.pages[key])
        
        if not self.pages:
            self.pages["dashboard"] = DashboardView(self.controller, self.user)
            self.stacked_widget.addWidget(self.pages["dashboard"])
    
    def switch_page(self, page_key: str):
        """Change de page avec animation"""
        if page_key not in self.pages:
            page_key = next(iter(self.pages), "dashboard")
        
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
            "settings": "Paramètres",
            "sinistres": "Gestion des Sinistres",
            "expertises": "Expertises Automobiles",
            "garages": "Garages Agréés"
        }
        # self.page_title.setText(titles.get(page_key, page_key))
        
        # Changer de page avec animation
        index = list(self.pages.keys()).index(page_key)
        self.animate_page_transition(index)
    
    def animate_page_transition(self, index: int):
        """Anime la transition entre pages"""
        self.stacked_widget.setCurrentIndex(index)
        # Ici on pourrait ajouter une animation de fondu
    
    def load_initial_data(self):
        """Charge les données initiales"""
        if self.pages:
            self.switch_page(next(iter(self.pages)))

    def can_access_page(self, page_key: str) -> bool:
        """Retourne True si le rôle courant peut accéder à la page."""
        permission = self.PAGE_PERMISSIONS.get(page_key)
        if permission is None:
            return True
        if permission == "admin_only":
            return self.user_role == Role.ADMIN.value or self.user_role == Role.ADMIN
        return SecurityManager.has_permission(self.user_role, permission)

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