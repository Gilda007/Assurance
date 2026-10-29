
# addons/Automobiles/views/main_view.py
"""
Vue principale modernisée avec design professionnel
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QFileDialog, QMessageBox, QGroupBox,
    QGridLayout, QCheckBox, QComboBox, QLineEdit, QApplication,
    QTextEdit, QTabWidget, QScrollArea, QSplitter, QListWidgetItem,
    QDialog, QDateEdit, QFormLayout, QSizePolicy, QStackedWidget,
    QTreeWidget, QTreeWidgetItem, QMenu, QListWidget,
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor
import qtawesome as qta

from addons.Automobiles.views.style import Colors, Fonts, Spacing, apply_global_style
from addons.Automobiles.views.widgets.modern_card import ModernCard
from addons.Automobiles.security.access_control import Permissions, SecurityManager, Role
from addons.Automobiles.views.widgets.loading_widget import LoadingPage
from core.logger import logger



import qtawesome as qta


# ═══════════════════════════════════════════════════════════════════
# HELPERS — Couleurs dérivées (à ajouter en haut du fichier)
# ═══════════════════════════════════════════════════════════════════

def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple) -> str:
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def rgba(hex_color: str, alpha: float) -> str:
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r}, {g}, {b}, {int(alpha * 255)})"


def darken(hex_color: str, amount: float = 0.2) -> str:
    r, g, b = hex_to_rgb(hex_color)
    r = int(r * (1 - amount))
    g = int(g * (1 - amount))
    b = int(b * (1 - amount))
    return rgb_to_hex((r, g, b))

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
        self._page_factories = {}
        self.page_widgets = {}
        self.pages = []
        self._page_rows = {}
        self._page_history = []
        self.refresh_timer = None
        self.vehicles_controller = controller.vehicles
        self.setup_ui()
        self.load_initial_data()
  
    def setup_ui(self):
        

        # ✅ Utiliser self.main_layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.setup_sidebar()
        self.main_layout.addWidget(self.sidebar_container)

        # Contenu principal
        self.setup_content_area()
        self.main_layout.addWidget(self.content_container, 1)

    def _start_refresh_timer(self):
        """Démarre l'auto-refresh APRES affichage."""
        if self.refresh_timer is None:
            self.refresh_timer = QTimer(self)
            self.refresh_timer.timeout.connect(self.load_data)
            self.refresh_timer.start(300000)  # 5 min

    def load_data(self):
        """Charge les données du dashboard."""
        if self._loading:
            return
        self._loading = True
        try:
            # ✅ Différer les updates visuels lourds
            QTimer.singleShot(0, self._fetch_and_update)
        except Exception as e:
            logger.error(f"Erreur load_data: {e}")
            self._loading = False


    def _fetch_and_update(self):
        """Récupération + mise à jour en plusieurs cycles Qt."""
        try:
            self._fetch_data()
            QApplication.processEvents()

            self._update_main_chart()
            QApplication.processEvents()

            self._update_donut()
            QApplication.processEvents()

        except Exception as e:
            logger.error(f"Erreur fetch_and_update: {e}")
        finally:
            self._loading = False

    # def setup_sidebar(self):
    #     """Configure la sidebar moderne avec Font Awesome"""
    #     self.sidebar = QFrame()
    #     self.sidebar.setFixedWidth(260)
    #     self.sidebar.setStyleSheet(f"""
    #         QFrame {{
    #             background-color: {Colors.WHITE};
    #             border-right: 1px solid {Colors.BORDER};
    #         }}
    #     """)
        
    #     sidebar_layout = QVBoxLayout(self.sidebar)
    #     sidebar_layout.setContentsMargins(16, 24, 16, 24)
    #     sidebar_layout.setSpacing(16)
        
    #     # Logo avec icône Font Awesome
    #     logo_widget = QWidget()
    #     logo_layout = QHBoxLayout(logo_widget)
    #     logo_layout.setContentsMargins(0, 0, 0, 0)
    #     logo_layout.setSpacing(12)
        
    #     logo_icon_label = QLabel()
    #     logo_icon = qta.icon('fa5s.car', color='#00288e')
    #     logo_icon_label.setPixmap(logo_icon.pixmap(32, 32))
    #     logo_icon_label.setStyleSheet("background: transparent; border: none;")
        
    #     logo_text_layout = QVBoxLayout()
    #     logo_text_layout.setSpacing(0)
        
    #     logo_text = QLabel("AutoAssure")
    #     logo_text.setStyleSheet(f"""
    #         font-size: 20px;
    #         font-weight: 700;
    #         color: {Colors.TEXT_PRIMARY};
    #         background: transparent;
    #         border: none;
    #     """)
        
    #     logo_subtext = QLabel("Management Portal")
    #     logo_subtext.setStyleSheet(f"""
    #         font-size: 11px;
    #         color: {Colors.TEXT_MUTED};
    #         background: transparent;
    #         border: none;
    #     """)
        
    #     logo_text_layout.addWidget(logo_text)
    #     logo_text_layout.addWidget(logo_subtext)
        
    #     logo_layout.addWidget(logo_icon_label)
    #     logo_layout.addLayout(logo_text_layout)
    #     logo_layout.addStretch()
    #     sidebar_layout.addWidget(logo_widget)
        
    #     # Navigation
    #     nav_widget = QWidget()
    #     nav_layout = QVBoxLayout(nav_widget)
    #     nav_layout.setSpacing(4)
        
    #     nav_title = QLabel("MENU PRINCIPAL")
    #     nav_title.setStyleSheet(f"""
    #         font-size: 10px;
    #         font-weight: 700;
    #         color: {Colors.TEXT_MUTED};
    #         letter-spacing: 1px;
    #         background: transparent;
    #         border: none;
    #         padding-bottom: 8px;
    #     """)
    #     nav_layout.addWidget(nav_title)
        
    #     # ✅ Boutons de navigation avec Font Awesome
    #     self.nav_buttons = {}
    #     nav_items = [
    #         ("dashboard", "Tableau de bord"),
    #         ("vehicles", "Véhicules"),
    #         ("contacts", "Clients"),
    #         ("companies", "Compagnies"),
    #         ("contracts", "Contrats"),
    #         ("sinistres", "Sinistres"),
    #         ("expertises", "Expertises"),
    #         ("garages", "Garages"),
    #         ("import", "Import ASAC"),
    #         ("reports", "Rapports"),
    #         ("settings", "Paramètres"),
    #     ]
        
    #     for key, text in nav_items:
    #         if not self.can_access_page(key):
    #             continue
    #         btn = ModernSidebarButton(text, key, key == "dashboard")
    #         btn.clicked.connect(lambda checked, k=key: self._on_sidebar_clicked(k))
    #         nav_layout.addWidget(btn)
    #         self.nav_buttons[key] = btn
        
    #     nav_layout.addStretch()
    #     sidebar_layout.addWidget(nav_widget)
        
    #     # Footer
    #     footer = QFrame()
    #     footer.setStyleSheet(f"""
    #         QFrame {{
    #             border-top: 1px solid {Colors.BORDER};
    #             padding-top: 8px;
    #         }}
    #     """)
    #     footer_layout = QVBoxLayout(footer)
    #     footer_layout.setSpacing(4)
    #     footer_layout.setContentsMargins(0, 8, 0, 0)
        
    #     footer_btn = QPushButton()
    #     footer_layout_h = QHBoxLayout()
    #     footer_layout_h.setContentsMargins(12, 8, 12, 8)
    #     footer_layout_h.setSpacing(10)
        
    #     user_icon = qta.icon('fa5s.user', color='#444653')
    #     user_icon_label = QLabel()
    #     user_icon_label.setPixmap(user_icon.pixmap(16, 16))
        
    #     user_text = QLabel("Admin")
    #     user_text.setStyleSheet(f"""
    #         font-size: 13px;
    #         color: {Colors.ON_SURFACE_VARIANT};
    #         background: transparent;
    #         border: none;
    #     """)
        
    #     footer_layout_h.addWidget(user_icon_label)
    #     footer_layout_h.addWidget(user_text)
    #     footer_layout_h.addStretch()
        
    #     footer_btn.setLayout(footer_layout_h)
    #     footer_btn.setStyleSheet(f"""
    #         QPushButton {{
    #             background: transparent;
    #             border: none;
    #             border-radius: 8px;
    #         }}
    #         QPushButton:hover {{
    #             background-color: {Colors.SURFACE_VARIANT};
    #         }}
    #     """)
    #     footer_btn.setCursor(Qt.PointingHandCursor)
        
    #     footer_layout.addWidget(footer_btn)
    #     sidebar_layout.addWidget(footer)
    
    def setup_sidebar(self):
        """Sidebar moderne identique à SinistreMainView."""

        # ═══════════════════════════════════════════════════════════════
        # CONTENEUR
        # ═══════════════════════════════════════════════════════════════
        self.sidebar_container = QFrame()
        self.sidebar_container.setFixedWidth(280)
        self.sidebar_container.setObjectName("SidebarContainer")
        self.sidebar_container.setStyleSheet("""
            QFrame#SidebarContainer {
                background-color: #ffffff;
                border: none;
                border-right: 1px solid #e2e8f0;
            }
        """)

        sidebar_layout = QVBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # ═══════════════════════════════════════════════════════════════
        # HEADER gradient + logo
        # ═══════════════════════════════════════════════════════════════
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a73e8, stop:1 #1557b0);
                border: none;
            }
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(12)

        logo_container = QFrame()
        logo_container.setFixedSize(44, 44)
        logo_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignCenter)

        logo_icon = QLabel()
        logo_icon.setPixmap(qta.icon('fa5s.car', color='white').pixmap(QSize(24, 24)))
        logo_icon.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_icon)
        header_layout.addWidget(logo_container)

        logo_text_layout = QVBoxLayout()
        logo_text_layout.setSpacing(0)
        logo_text_layout.setContentsMargins(0, 0, 0, 0)

        app_name = QLabel("AutoAssure")
        app_name.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: 800;
            letter-spacing: 1px;
            background: transparent;
        """)
        logo_text_layout.addWidget(app_name)

        app_subtitle = QLabel("Management Portal")
        app_subtitle.setStyleSheet("""
            color: rgba(255, 255, 255, 0.85);
            font-size: 10px;
            font-weight: 500;
            background: transparent;
        """)
        logo_text_layout.addWidget(app_subtitle)

        header_layout.addLayout(logo_text_layout)
        header_layout.addStretch()
        sidebar_layout.addWidget(header)

        # ═══════════════════════════════════════════════════════════════
        # BARRE DE RECHERCHE
        # ═══════════════════════════════════════════════════════════════
        search_container = QFrame()
        search_container.setStyleSheet("""
            QFrame {
                background: transparent;
                padding: 16px 16px 8px 16px;
            }
        """)
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(16, 16, 16, 8)

        self.sidebar_search = QLineEdit()
        self.sidebar_search.setPlaceholderText("🔍  Rechercher une page...")
        self.sidebar_search.setStyleSheet("""
            QLineEdit {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 13px;
                color: #1e293b;
            }
            QLineEdit:focus {
                border-color: #1a73e8;
                background-color: white;
            }
        """)
        self.sidebar_search.textChanged.connect(self._filter_sidebar_items)
        search_layout.addWidget(self.sidebar_search)
        sidebar_layout.addWidget(search_container)

        # ═══════════════════════════════════════════════════════════════
        # ZONE SCROLLABLE
        # ═══════════════════════════════════════════════════════════════
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { background: transparent; width: 6px; margin: 0; }
            QScrollBar::handle:vertical {
                background: #cbd5e1; border-radius: 3px; min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #94a3b8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)

        # ═══════════════════════════════════════════════════════════════
        # SECTION "PRINCIPAL"
        # ═══════════════════════════════════════════════════════════════
        section_title_container = QFrame()
        section_title_container.setStyleSheet("""
            QFrame { background: transparent; padding: 12px 20px 6px 20px; }
        """)
        st_layout = QVBoxLayout(section_title_container)
        st_layout.setContentsMargins(20, 12, 20, 6)

        section_title = QLabel("MENU PRINCIPAL")
        section_title.setStyleSheet("""
            color: #94a3b8;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1.5px;
            background: transparent;
        """)
        st_layout.addWidget(section_title)
        scroll_layout.addWidget(section_title_container)

        # ═══════════════════════════════════════════════════════════════
        # QListWidget des items
        # ═══════════════════════════════════════════════════════════════
        self.sidebar = QListWidget()
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                padding: 0px 8px;
            }
            QListWidget::item {
                background: transparent;
                border: none;
                padding: 0;
                margin: 2px 8px;
            }
            QListWidget::item:selected { background: transparent; }
            QListWidget::item:hover { background: transparent; }
        """)
        self.sidebar.setFrameShape(QFrame.NoFrame)
        self.sidebar.setFixedWidth(260)
        self.sidebar.currentRowChanged.connect(self.switch_page)

        # Pages de la sidebar (clé, label, icône, couleur)
        nav_items = [
            ("dashboard",  "Tableau de bord", "fa5s.chart-pie",      "#3b82f6"),
            ("vehicles",   "Véhicules",       "fa5s.car",            "#06b6d4"),
            ("contacts",   "Clients",         "fa5s.users",          "#8b5cf6"),
            ("companies",  "Compagnies",      "fa5s.building",       "#f59e0b"),
            ("contracts",  "Contrats",        "fa5s.file-contract",  "#22c55e"),
            ("sinistres",  "Sinistres",       "fa5s.exclamation-triangle", "#ef4444"),
            ("expertises", "Expertises",      "fa5s.search-plus",    "#a855f7"),
            ("garages",    "Garages",         "fa5s.tools",          "#0ea5e9"),
            ("import",     "Import ASAC",     "fa5s.upload",         "#64748b"),
            ("reports",    "Rapports",        "fa5s.chart-line",     "#84cc16"),
            ("settings",   "Paramètres",      "fa5s.cog",            "#475569"),
        ]

        self.pages = []
        self._page_rows = {}
        self._section_title_widgets = [section_title]

        for page_id, label, icon_name, icon_color in nav_items:
            if not self.can_access_page(page_id):
                continue

            # Item widget custom
            item_widget = self._build_sidebar_item(label, icon_name, icon_color)
            item_widget._page_id = page_id

            item = QListWidgetItem()
            item.setData(Qt.UserRole, page_id)
            item.setData(Qt.UserRole + 1, label.lower())
            item.setSizeHint(QSize(0, 56))

            self._page_rows[page_id] = len(self.pages)
            self.pages.append(page_id)
            self.sidebar.addItem(item)
            self.sidebar.setItemWidget(item, item_widget)
        
        print("📋 Pages dans self.pages :")
        for i, pid in enumerate(self.pages):
            print(f"   [{i}] {pid}")
        print("📋 Items dans self.sidebar :")
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            print(f"   [{i}] {item.data(Qt.UserRole)}")

        scroll_layout.addWidget(self.sidebar)

        # Message si aucune page accessible
        if not self.pages:
            no_access = QLabel("⛔ Aucune page accessible\n\nContactez un administrateur.")
            no_access.setStyleSheet("""
                color: #94a3b8;
                font-size: 12px;
                font-style: italic;
                padding: 30px;
                background: transparent;
            """)
            no_access.setAlignment(Qt.AlignCenter)
            no_access.setWordWrap(True)
            scroll_layout.addWidget(no_access)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        sidebar_layout.addWidget(scroll, 1)

        # ═══════════════════════════════════════════════════════════════
        # FOOTER utilisateur
        # ═══════════════════════════════════════════════════════════════
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background: transparent;
                border-top: 1px solid #e2e8f0;
                padding: 12px;
            }
        """)
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(12, 12, 12, 12)
        footer_layout.setSpacing(8)

        user_card = QFrame()
        user_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        user_card_layout = QHBoxLayout(user_card)
        user_card_layout.setContentsMargins(12, 10, 12, 10)
        user_card_layout.setSpacing(10)

        initials = "U"
        if self.user:
            full_name = getattr(self.user, 'full_name', None) or \
                        getattr(self.user, 'username', 'User')
            initials = "".join([w[0].upper() for w in str(full_name).split()[:2]])

        avatar = QLabel(initials)
        avatar.setFixedSize(38, 38)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a73e8, stop:1 #6366f1);
                color: white;
                border-radius: 19px;
                font-size: 14px;
                font-weight: 700;
            }
        """)
        user_card_layout.addWidget(avatar)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        user_name = QLabel(
            getattr(self.user, 'full_name', 'Utilisateur') if self.user else 'Utilisateur'
        )
        user_name.setStyleSheet("""
            color: #1e293b;
            font-size: 13px;
            font-weight: 600;
            background: transparent;
        """)
        info_layout.addWidget(user_name)

        user_role = QLabel(
            f"● {getattr(self.user, 'role', 'Membre') if self.user else 'Membre'}"
        )
        user_role.setStyleSheet("""
            color: #10b981;
            font-size: 10px;
            font-weight: 600;
            background: transparent;
        """)
        info_layout.addWidget(user_role)

        user_card_layout.addLayout(info_layout)
        user_card_layout.addStretch()

        user_menu_btn = QPushButton("⋯")
        user_menu_btn.setFixedSize(28, 28)
        user_menu_btn.setCursor(Qt.PointingHandCursor)
        user_menu_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #94a3b8;
                font-size: 16px;
                font-weight: bold;
                border-radius: 14px;
            }
            QPushButton:hover {
                background: rgba(26, 115, 232, 0.1);
                color: #1a73e8;
            }
        """)
        user_menu_btn.clicked.connect(self._show_user_menu)
        user_card_layout.addWidget(user_menu_btn)

        footer_layout.addWidget(user_card)
        sidebar_layout.addWidget(footer)

        # Ajouter le conteneur au layout principal
        # self.layout.addWidget(self.sidebar_container)

    # def setup_content_area(self):
    #     """Configure la zone de contenu principale"""
    #     self.content_container = QWidget()
    #     self.content_container.setStyleSheet("background: transparent;")
        
    #     content_layout = QVBoxLayout(self.content_container)
    #     content_layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
    #     content_layout.setSpacing(Spacing.XL)
    #     self.loading_page = LoadingPage(message="Chargement du module...")

    # # ✅ Stack contenant loading_page + pages chargées
    #     self.container = QStackedWidget()
    #     self.container.setStyleSheet("background: transparent;")
    #     self.container.addWidget(self.loading_page)  # index 0

    #     content_layout.addWidget(self.container)
        
    #     # En-tête
    #     # header = self.setup_header()
    #     # content_layout.addWidget(header)
        
    #     # Zone de contenu empilé
    #     self.stacked_widget = QStackedWidget()
    #     self.stacked_widget.setStyleSheet("background: transparent;")
        
    #     # Pages
    #     self.pages = {}
    #     # self.init_pages()
        
    #     content_layout.addWidget(self.stacked_widget)

    def setup_content_area(self):
        """Zone de contenu principale."""
        self.content_container = QWidget()
        self.content_container.setStyleSheet("background: transparent;")

        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)

        from addons.Automobiles.views.widgets.loading_widget import LoadingPage
        self.loading_page = LoadingPage(message="Chargement du module...")

        self.container = QStackedWidget()
        self.container.setStyleSheet("""
            QStackedWidget {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        self.container.addWidget(self.loading_page)
        content_layout.addWidget(self.container)

        self.main_layout.addWidget(self.content_container, 1)

    def refresh_data(self):
        """Rafraîchit la page courante si déjà chargée."""
        if not self._page_history:
            return
        current = self._page_history[-1]
        widget = self.page_widgets.get(current)
        if widget is None:
            return
        try:
            if hasattr(widget, 'refresh'):
                widget.refresh()
            elif hasattr(widget, 'load_data'):
                widget.load_data()
        except Exception as e:
            print(f"⚠️ Erreur refresh {current}: {e}")

    # def init_pages(self):
    #     """Initialise les différentes pages"""
    #     # À implémenter avec les vues spécifiques
    #     from addons.Automobiles.views.dashboard_view import DashboardView
    #     from addons.Automobiles.views.automobile_view import VehiculeModuleView
    #     from addons.Automobiles.views.contacts_view import ContactListView
    #     from addons.Automobiles.views.compagnies_view import CompanyTariffView
    #     from addons.Automobiles.views.contract_view import ContractView
    #     from addons.Automobiles.views.reports_view import ReportView
    #     from addons.Automobiles.views.settings_view import SettingsView
    #     from addons.Automobiles.views.asac_import_view import ASACImportView 
    #     from addons.Automobiles.views.sinistre.sinistre_list_view import SinistreListView
    #     from addons.Automobiles.views.expertise.expertise_list_view import ExpertiseListView
    #     from addons.Automobiles.views.garages.garage_list_view import GarageListView
        
    #     page_factories = {
    #         "dashboard": lambda: DashboardView(self.controller, self.user),
    #         "vehicles": lambda: VehiculeModuleView(self.controller, self.user),
    #         "contacts": lambda: ContactListView(self.controller, self.user),
    #         "companies": lambda: CompanyTariffView(self.controller, self.user),
    #         "contracts": lambda: ContractView(self.controller, self.user),
    #         "import": lambda: ASACImportView(self.controller, self.user),
    #         "reports": lambda: ReportView(self.controller, self.user),
    #         "settings": lambda: SettingsView(self.controller, self.user),
    #         "sinistres": lambda: SinistreListView(self.controller, self.user),
    #         "expertises": lambda: ExpertiseListView(self.controller, self.user),
    #         "garages": lambda: GarageListView(self.controller, self.user),
    #     }
        
    #     for key, factory in page_factories.items():
    #         if not self.can_access_page(key):
    #             continue
    #         self.pages[key] = factory()
    #         self.stacked_widget.addWidget(self.pages[key])
        
    #     if not self.pages:
    #         self.pages["dashboard"] = DashboardView(self.controller, self.user)
    #         self.stacked_widget.addWidget(self.pages["dashboard"])
    
    # def _register_page_factories(self):
    #     """Enregistre les factories (création différée)."""
    #     self._page_factories = {
    #         "dashboard":  lambda: self._make_dashboard(),
    #         "vehicles":   lambda: self._make_vehicles(),
    #         "contacts":   lambda: self._make_contacts(),
    #         "companies":  lambda: self._make_companies(),
    #         "contracts":  lambda: self._make_contracts(),
    #         "import":     lambda: self._make_asac_import(),
    #         "reports":    lambda: self._make_reports(),
    #         "settings":   lambda: self._make_settings(),
    #         "sinistres":  lambda: self._make_sinistres(),
    #         "expertises": lambda: self._make_expertises(),
    #         "garages":    lambda: self._make_garages(),
    #     }

    #     self.pages = []
    #     self._page_rows = {}
    #     for page_id in self._page_factories:
    #         if self.can_access_page(page_id):
    #             self._page_rows[page_id] = len(self.pages)
    #             self.pages.append(page_id)

    def _register_page_factories(self):
        """Enregistre les identifiants de pages accessibles pour le rôle courant."""
        self.pages = []
        self._page_rows = {}

        all_pages = [
            "dashboard", "vehicles", "contacts", "companies",
            "contracts", "sinistres", "expertises", "garages",
            "import", "reports", "settings",
        ]
        for page_id in all_pages:
            if self.can_access_page(page_id):
                self._page_rows[page_id] = len(self.pages)
                self.pages.append(page_id)

    def _on_sidebar_clicked(self, page_id: str):
        """Convertit la clé en index et délègue à switch_page."""
        if page_id not in self._page_rows:
            return
        self.switch_page(self._page_rows[page_id])

    # ─── Factories (imports locaux = création différée) ───

    def _make_dashboard(self):
        from addons.Automobiles.views.dashboard_view import DashboardView
        return DashboardView(self.controller, self.user)

    def _make_vehicles(self):
        from addons.Automobiles.views.automobile_view import VehiculeModuleView
        return VehiculeModuleView(self.controller, self.user)

    def _make_contacts(self):
        from addons.Automobiles.views.contacts_view import ContactListView
        return ContactListView(self.controller, self.user)

    def _make_companies(self):
        from addons.Automobiles.views.compagnies_view import CompanyTariffView
        return CompanyTariffView(self.controller, self.user)

    def _make_contracts(self):
        from addons.Automobiles.views.contract_view import ContractView
        return ContractView(self.controller, self.user)

    def _make_asac_import(self):
        from addons.Automobiles.views.asac_import_view import ASACImportView
        return ASACImportView(self.controller, self.user)

    def _make_reports(self):
        from addons.Automobiles.views.reports_view import ReportView
        return ReportView(self.controller, self.user)

    def _make_settings(self):
        from addons.Automobiles.views.settings_view import SettingsView
        return SettingsView(self.controller, self.user)

    def _make_sinistres(self):
        from addons.Automobiles.views.sinistre.sinistre_list_view import SinistreListView
        return SinistreListView(self.controller, self.user)

    def _make_expertises(self):
        from addons.Automobiles.views.expertise.expertise_list_view import ExpertiseListView
        return ExpertiseListView(self.controller, self.user)

    def _make_garages(self):
        from addons.Automobiles.views.garages.garage_list_view import GarageListView
        return GarageListView(self.controller, self.user)

    def _create_page_async(self, page_id: str):
        """Crée la page en différé — l'UI reste fluide."""

        try:
            # Étape 1 : Créer le widget (peut être lent, mais l'UI est déjà peinte)
            self.loading_page.set_message("Création de l'interface...")
            QApplication.processEvents()

            widget = self._page_factories[page_id]()
            if widget is None:
                raise RuntimeError("Widget non créé (import manquant ?)")

            # Étape 2 : Charger les données
            self.loading_page.set_message("Chargement des données...")
            QApplication.processEvents()

            if hasattr(widget, 'refresh'):
                widget.refresh()
            elif hasattr(widget, 'load_data'):
                widget.load_data()

            widget._has_loaded = True

            # Étape 3 : Afficher
            self.page_widgets[page_id] = widget
            self.container.addWidget(widget)

            # ✅ Laisser la barre atteindre 100% avant de basculer
            QTimer.singleShot(300, lambda w=widget: self.container.setCurrentWidget(w))

        except Exception as e:
            import traceback
            traceback.print_exc()
            error_widget = self._build_error_widget(page_id, str(e))
            self.container.addWidget(error_widget)
            self.container.setCurrentWidget(error_widget)

    # def switch_page(self, index: int):
    #     """Change la page affichée — basé sur l'item sélectionné, pas l'index."""
    #     if not (0 <= index < self.sidebar.count()):
    #         return

    #     # ✅ Utiliser l'item réellement sélectionné
    #     item = self.sidebar.item(index)
    #     if not item:
    #         return
    #     page_id = item.data(Qt.UserRole)
    #     if not page_id:
    #         return

    #     self._highlight_sidebar_item(index)

    #     widget = self.page_widgets.get(page_id)

    #     if widget is None:
    #         # Première visite : créer
    #         self.loading_page.set_message(f"Chargement de '{page_id}'...")
    #         self.container.setCurrentWidget(self.loading_page)
    #         QApplication.processEvents()

    #         try:
    #             widget = self._create_page_async(page_id)
    #         except Exception as e:
    #             import traceback
    #             traceback.print_exc()
    #             widget = None

    #         if widget is None:
    #             error_widget = self._build_error_widget(page_id, "Page non disponible")
    #             self.container.addWidget(error_widget)
    #             self.container.setCurrentWidget(error_widget)
    #             return

    #         # Charger les données
    #         self.loading_page.set_message("Chargement des données...")
    #         QApplication.processEvents()

    #         try:
    #             if hasattr(widget, 'refresh'):
    #                 widget.refresh()
    #             elif hasattr(widget, 'load_data'):
    #                 widget.load_data()
    #             widget._has_loaded = True
    #         except Exception as e:
    #             print(f"❌ Erreur refresh {page_id}: {e}")
    #             import traceback
    #             traceback.print_exc()

    #         # Afficher la page
    #         QTimer.singleShot(300, lambda w=widget: self.container.setCurrentWidget(w))
    #     else:
    #         # Page en cache : afficher + refresh doux
    #         self.container.setCurrentWidget(widget)
    #         if hasattr(widget, 'refresh'):
    #             try:
    #                 QTimer.singleShot(10, widget.refresh)
    #             except Exception:
    #                 pass

    def switch_page(self, index: int):
        """Change la page affichée — basé sur l'item réellement sélectionné."""
        if not (0 <= index < self.sidebar.count()):
            return

        item = self.sidebar.item(index)
        if not item:
            return

        page_id = item.data(Qt.UserRole)
        if not page_id:
            return

        self._highlight_sidebar_item(index)

        # Historique
        if not self._page_history or self._page_history[-1] != page_id:
            self._page_history.append(page_id)
            if len(self._page_history) > 20:
                self._page_history.pop(0)

        widget = self.page_widgets.get(page_id)

        # ─── Page déjà en cache : afficher ───
        if widget is not None:
            self.container.setCurrentWidget(widget)
            if hasattr(widget, 'refresh'):
                try:
                    QTimer.singleShot(10, widget.refresh)
                except Exception:
                    pass
            return

        # ─── Première visite : créer ───
        self.loading_page.set_message(f"Chargement de '{page_id}'...")
        self.container.setCurrentWidget(self.loading_page)
        QApplication.processEvents()

        widget = self._create_page_async(page_id)

        if widget is None:
            error_widget = self._build_error_widget(page_id, "Page non disponible")
            self.container.addWidget(error_widget)
            self.container.setCurrentWidget(error_widget)
            return

        # Charger les données
        try:
            if hasattr(widget, 'refresh'):
                widget.refresh()
            elif hasattr(widget, 'load_data'):
                widget.load_data()
            widget._has_loaded = True
        except Exception as e:
            print(f"❌ Erreur refresh {page_id}: {e}")
            import traceback
            traceback.print_exc()

        QTimer.singleShot(300, lambda w=widget: self.container.setCurrentWidget(w))

    def _create_page_async(self, page_id: str):
        """
        Crée une page à la demande (Lazy Loading).
        Utilise self.controller.<sous_controleur> conformément à l'API
        exposée par AutomobileMainController.
        """
        if page_id in self.page_widgets:
            return self.page_widgets[page_id]

        try:
            if page_id == 'dashboard':
                from addons.Automobiles.views.dashboard_view import DashboardView
                page = DashboardView(self.controller, self.user)

            elif page_id == 'vehicles':
                from addons.Automobiles.views.automobile_view import VehiculeModuleView
                page = VehiculeModuleView(self.controller, self.user)

            elif page_id == 'contacts':
                from addons.Automobiles.views.contacts_view import ContactListView
                page = ContactListView(self.controller, self.user)

            elif page_id == 'companies':
                from addons.Automobiles.views.compagnies_view import CompanyTariffView
                page = CompanyTariffView(self.controller, self.user)

            elif page_id == 'contracts':
                from addons.Automobiles.views.contract_view import ContractView
                page = ContractView(self.controller, self.user)

            elif page_id == 'sinistres':
                from addons.Automobiles.views.sinistre.sinistre_list_view import SinistreListView
                page = SinistreListView(self.controller, self.user)

            elif page_id == 'expertises':
                from addons.Automobiles.views.expertise.expertise_list_view import ExpertiseListView
                page = ExpertiseListView(self.controller, self.user)

            elif page_id == 'garages':
                from addons.Automobiles.views.garages.garage_list_view import GarageListView
                page = GarageListView(self.controller, self.user)

            elif page_id == 'import':
                from addons.Automobiles.views.asac_import_view import ASACImportView
                page = ASACImportView(self.controller, self.user)

            elif page_id == 'reports':
                from addons.Automobiles.views.reports_view import ReportView
                page = ReportView(self.controller, self.user)

            elif page_id == 'settings':
                from addons.Automobiles.views.settings_view import SettingsView
                page = SettingsView(self.controller, self.user)

            else:
                print(f"⚠️ Page inconnue : {page_id}")
                return None

            # ✅ Mise en cache + ajout au container
            if page is not None:
                self.page_widgets[page_id] = page
                self.container.addWidget(page)
                print(f"✅ Page '{page_id}' créée ({type(page).__name__})")

            return page

        except Exception as e:
            print(f"❌ Erreur création page '{page_id}': {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_error_widget(self, page_id: str, error: str) -> QWidget:
        """Widget d'erreur stylisé."""
        w = QWidget()
        w.setStyleSheet("background: white;")

        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        icon = QLabel("⚠️")
        icon.setStyleSheet("font-size: 64px;")
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        title = QLabel(f"Impossible de charger '{page_id}'")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1e293b;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        msg = QLabel(error)
        msg.setStyleSheet("color: #64748b; font-size: 13px;")
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        layout.addWidget(msg)

        return w

    def animate_page_transition(self, index: int):
        """Anime la transition entre pages"""
        self.stacked_widget.setCurrentIndex(index)
        # Ici on pourrait ajouter une animation de fondu
    
    def load_initial_data(self):
        """Enregistre les factories et affiche la 1ère page accessible."""
        self._register_page_factories()

        if self.pages:
            # ✅ Différer l'appel pour laisser le widget se peindre
            QTimer.singleShot(0, lambda: self.switch_page(0))

    def can_access_page(self, page_key: str) -> bool:
        """Retourne True si le rôle courant peut accéder à la page."""
        permission = self.PAGE_PERMISSIONS.get(page_key)
        if permission is None:
            return True
        if permission == "admin_only":
            return self.user_role == Role.ADMIN.value or self.user_role == Role.ADMIN
        return SecurityManager.has_permission(self.user_role, permission)

    def _build_sidebar_item(self, label: str, icon_name: str, icon_color: str) -> QWidget:
        """Construit un widget custom pour un item de la sidebar."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        # Icône FontAwesome
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon(icon_name, color=icon_color).pixmap(QSize(20, 20)))
        icon_lbl.setFixedSize(24, 24)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(icon_lbl)

        # Texte
        text_lbl = QLabel(label)
        text_lbl.setStyleSheet("""
            color: #475569;
            font-size: 16px;
            font-weight: 500;
            background: transparent;
        """)
        layout.addWidget(text_lbl)
        layout.addStretch()

        # Références pour le highlight
        widget._icon_label = icon_lbl
        widget._text_label = text_lbl
        widget._icon_name = icon_name
        widget._icon_color = icon_color
        widget._label_text = label

        return widget

    def _highlight_sidebar_item(self, active_index: int):
        """Met en surbrillance l'item actif avec les couleurs de son icône."""
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            widget = self.sidebar.itemWidget(item)
            if not widget:
                continue

            is_active = (i == active_index)
            icon_color = getattr(widget, '_icon_color', '#1a73e8')

            if is_active:
                bg_color = rgba(icon_color, 0.10)
                text_color = darken(icon_color, 0.1)

                widget.setStyleSheet(f"""
                    QWidget {{
                        background: {bg_color};
                        border-radius: 10px;
                    }}
                """)

                if hasattr(widget, '_text_label'):
                    widget._text_label.setStyleSheet(f"""
                        color: {text_color};
                        font-size: 16px;
                        font-weight: 700;
                        background: transparent;
                    """)
            else:
                widget.setStyleSheet("""
                    QWidget {
                        background: transparent;
                        border-radius: 10px;
                    }
                """)

                if hasattr(widget, '_text_label'):
                    widget._text_label.setStyleSheet("""
                        color: #475569;
                        font-size: 16px;
                        font-weight: 500;
                        background: transparent;
                    """)

    def _filter_sidebar_items(self, text: str):
        """Filtre les items selon la recherche."""
        text = text.strip().lower()
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            label = item.data(Qt.UserRole + 1) or ""
            item.setHidden(bool(text) and text not in label)

        for title_widget in getattr(self, '_section_title_widgets', []):
            title_widget.setVisible(True)

    def _show_user_menu(self):
        """Menu contextuel utilisateur."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 6px;
                min-width: 200px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                color: #1e293b;
            }
            QMenu::item:selected {
                background: #eff6ff;
                color: #2563eb;
            }
            QMenu::separator {
                height: 1px;
                background: #f1f5f9;
                margin: 4px 8px;
            }
        """)

        header_action = menu.addAction(
            f"👤 {getattr(self.user, 'full_name', 'Utilisateur') if self.user else 'Utilisateur'}"
        )
        header_action.setEnabled(False)
        menu.addSeparator()

        menu.addAction("⚙️  Mon profil").triggered.connect(lambda: None)
        menu.addAction("🔑  Changer mot de passe").triggered.connect(lambda: None)
        menu.addSeparator()
        menu.addAction("🚪  Déconnexion").triggered.connect(self._on_logout_clicked)

        sender = self.sender()
        if sender:
            menu.exec(sender.mapToGlobal(sender.rect().bottomRight()))
        else:
            from PySide6.QtGui import QCursor
            menu.exec(QCursor.pos())

    def _on_logout_clicked(self):
        """Déconnexion avec confirmation."""
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            print("🔒 Déconnexion demandée")
            parent = self.parent()
            while parent and not hasattr(parent, 'close'):
                parent = parent.parent()
            if parent:
                parent.close()

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