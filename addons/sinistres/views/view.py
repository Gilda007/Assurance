

"""
Vue principale du module LOMETA Sinistres
Interface utilisateur complète pour la gestion des sinistres
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QListWidgetItem, QStackedWidget,
    QListWidget, QFrame, QMessageBox, QDialog, QGraphicsDropShadowEffect,
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QTabWidget, QSplitter, QScrollArea,
    QProgressBar, QToolBar, QMenu, QCheckBox, QRadioButton, QApplication
)
from PySide6.QtCore import QEasingCurve, Qt, QSize, Signal, Slot, QDate, QTimer, QThread
from PySide6.QtGui import QColor, QIcon, QFont, QAction, QCursor

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Import des contrôleurs
from addons.sinistres.controllers.sinistre_controller import SinistreController
from addons.sinistres.controllers.referentiel_controller import ReferentielController
from addons.sinistres.controllers.expertise_controller import ExpertiseController
from addons.sinistres.controllers.evaluation_controller import EvaluationController
from addons.sinistres.controllers.reglement_controller import ReglementController
from addons.sinistres.controllers.recours_controller import RecoursController
from addons.sinistres.controllers.audit_controller import AuditController
from addons.sinistres.controllers.comptabilite_controller import ComptabiliteController


# Import des vues détaillées
from addons.sinistres.views.dossier_360 import Dossier360View
from addons.sinistres.views.parametres_page import ParametresPage
from addons.sinistres.views.tableau_base import TableauActions
from addons.sinistres.views.widgets.animated_icon import AnimatedIconLabel


# Importation des pages spécifiques
from addons.sinistres.views.dashboard_view import DashboardPage
from addons.sinistres.views.sinistre_form_view import NouveauSinistrePage
from addons.sinistres.views.search_view import RecherchePage
from addons.sinistres.views.expertise_page import ExpertisesPage 
from addons.sinistres.views.evaluation_page import EvaluationsPage
from addons.sinistres.views.reglement_page import ReglementsPage
from addons.sinistres.views.recours_page import RecoursPage
from addons.sinistres.views.referentiel_page import ReferentielsPage
from addons.sinistres.views.widgets.loading_widget import LoadingPage
from addons.sinistres.views.comptabilite_page import ComptabilitePage


import qtawesome as qta


# ═══════════════════════════════════════════════════════════════════
# HELPERS — GÉNÉRATION DE COULEURS DÉRIVÉES
# ═══════════════════════════════════════════════════════════════════

def hex_to_rgb(hex_color: str) -> tuple:
    """Convertit '#3b82f6' en (59, 130, 246)"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple) -> str:
    """Convertit (59, 130, 246) en '#3b82f6'"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def lighten(hex_color: str, amount: float = 0.9) -> str:
    """
    Éclaircit une couleur en la mélangeant avec du blanc.
    amount = 0.9 → 90% blanc, 10% couleur d'origine
    """
    r, g, b = hex_to_rgb(hex_color)
    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)
    return rgb_to_hex((r, g, b))


def darken(hex_color: str, amount: float = 0.2) -> str:
    """
    Fonce une couleur en la mélangeant avec du noir.
    amount = 0.2 → 20% noir, 80% couleur d'origine
    """
    r, g, b = hex_to_rgb(hex_color)
    r = int(r * (1 - amount))
    g = int(g * (1 - amount))
    b = int(b * (1 - amount))
    return rgb_to_hex((r, g, b))


def rgba(hex_color: str, alpha: float) -> str:
    """
    Retourne la couleur au format rgba avec transparence.
    Utile pour Qt : rgba(59, 130, 246, 0.1) → 'rgba(59, 130, 246, 25)'
    """
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r}, {g}, {b}, {int(alpha * 255)})"


class LometaSinistresMainView(QWidget):
    """
    Vue principale du module LOMETA Sinistres
    Contient la sidebar et les différentes pages
    """
    

    def __init__(
        self,
        sinistre_controller=None,
        referentiel_controller=None,
        expertise_controller=None,
        evaluation_controller=None,
        reglement_controller=None,
        recours_controller=None,
        user=None
    ):
        super().__init__()
        self.sinistre_controller = sinistre_controller or SinistreController()
        self.referentiel_controller = referentiel_controller or ReferentielController()
        self.expertise_controller = expertise_controller or ExpertiseController()
        self.evaluation_controller = evaluation_controller or EvaluationController()
        self.reglement_controller = reglement_controller or ReglementController()
        self.recours_controller = recours_controller or RecoursController()
        self.comptabilite_controller = ComptabiliteController()
        # self.comptabilite_controller.set_current_user(user)
        self.audit_controller = AuditController()
        self.user = user
        self.pages_cache = {}
        
        # ============================================================
        # ✅ ÉTAPE 1 : Créer les services de permissions EN PREMIER
        # ============================================================
        from addons.sinistres.services.permission_service import PermissionService
        from addons.sinistres.security.permissions_helper import PermissionsUI
        
        self.permission_service = PermissionService()
        self.permissions_ui = PermissionsUI(user, self.permission_service)
        
        # ============================================================
        # ÉTAPE 2 : Style global
        # ============================================================
        self.setObjectName("LometaMainView")
        self.setStyleSheet("background-color: #f8fafc;")
        
        # ============================================================
        # ÉTAPE 3 : Heartbeat
        # ============================================================
        self._heartbeat_timer = QTimer(self)
        self._heartbeat_timer.timeout.connect(self._send_heartbeat)
        self._heartbeat_timer.start(5 * 60 * 1000)  # 5 min
        
        # ============================================================
        # ÉTAPE 4 : Layout principal
        # ============================================================
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # ============================================================
        # ÉTAPE 5 : Setup UI (peut maintenant utiliser self.permission_service)
        # ============================================================
        self.setup_sidebar()
        self.setup_content_area()
        
        # ============================================================
        # ÉTAPE 6 : Sélectionner la première page
        # ============================================================
        if hasattr(self, 'sidebar') and self.sidebar.count() > 0:
            self.sidebar.setCurrentRow(0)
        
        # ============================================================
        # ÉTAPE 7 : Connecter les signaux
        # ============================================================
        self._connect_signals()

    def _send_heartbeat(self):
        """Envoie un heartbeat au serveur"""
        try:
            if self.sinistre_controller:
                self.sinistre_controller.heartbeat()
        except Exception as e:
            print(f"Erreur heartbeat: {e}")
   
    def _connect_signals(self):
        """Connecte les signaux des contrôleurs aux slots."""
        
        # ============================================================
        # SinistreController
        # ============================================================
        self.sinistre_controller.error_occurred.connect(self._on_error)
        self.sinistre_controller.success_occurred.connect(self._on_success)
        self.sinistre_controller.sinistre_created.connect(self._on_sinistre_created)
        self.sinistre_controller.sinistre_updated.connect(self._on_sinistre_updated)
        self.sinistre_controller.sinistre_status_changed.connect(self._on_status_changed)
        self.sinistre_controller.sinistre_list_updated.connect(self._on_sinistre_list_updated)
        self.sinistre_controller.sinistre_deleted.connect(self._on_sinistre_deleted)
        
        # ============================================================
        # ReferentielController
        # ============================================================
        self.referentiel_controller.error_occurred.connect(self._on_error)
        self.referentiel_controller.success_occurred.connect(self._on_success)
        self.referentiel_controller.referentiel_created.connect(self._on_referentiel_created)
        self.referentiel_controller.referentiel_updated.connect(self._on_referentiel_updated)
        self.referentiel_controller.referentiel_deleted.connect(self._on_referentiel_deleted)
        self.referentiel_controller.referentiel_list_updated.connect(
            self._on_referentiel_list_updated
        )
        
        # ============================================================
        # ExpertiseController
        # ============================================================
        self.expertise_controller.error_occurred.connect(self._on_error)
        self.expertise_controller.success_occurred.connect(self._on_success)
        self.expertise_controller.mission_created.connect(self._on_mission_created)
        self.expertise_controller.mission_updated.connect(self._on_mission_updated)
        self.expertise_controller.mission_status_changed.connect(
            self._on_mission_status_changed
        )
        self.expertise_controller.mission_list_updated.connect(
            self._on_mission_list_updated
        )
        
        # ============================================================
        # EvaluationController
        # ============================================================
        self.evaluation_controller.error_occurred.connect(self._on_error)
        self.evaluation_controller.success_occurred.connect(self._on_success)
        self.evaluation_controller.evaluation_created.connect(
            self._on_evaluation_created
        )
        self.evaluation_controller.evaluation_updated.connect(
            self._on_evaluation_updated
        )
        self.evaluation_controller.evaluation_validated.connect(
            self._on_evaluation_validated
        )
        self.evaluation_controller.evaluation_revised.connect(
            self._on_evaluation_revised
        )
        self.evaluation_controller.evaluation_list_updated.connect(
            self._on_evaluation_list_updated
        )
        
        # ============================================================
        # ReglementController
        # ============================================================
        self.reglement_controller.error_occurred.connect(self._on_error)
        self.reglement_controller.success_occurred.connect(self._on_success)
        self.reglement_controller.reglement_created.connect(self._on_reglement_created)
        self.reglement_controller.reglement_updated.connect(self._on_reglement_updated)
        self.reglement_controller.reglement_validated.connect(
            self._on_reglement_validated
        )
        self.reglement_controller.reglement_paid.connect(self._on_reglement_paid)
        self.reglement_controller.reglement_list_updated.connect(
            self._on_reglement_list_updated
        )
        self.reglement_controller.lot_created.connect(self._on_lot_created)
        
        # ============================================================
        # RecoursController
        # ============================================================
        self.recours_controller.error_occurred.connect(self._on_error)
        self.recours_controller.success_occurred.connect(self._on_success)
        self.recours_controller.recours_created.connect(self._on_recours_created)
        self.recours_controller.recours_updated.connect(self._on_recours_updated)
        self.recours_controller.recours_status_changed.connect(
            self._on_recours_status_changed
        )
        self.recours_controller.recours_list_updated.connect(
            self._on_recours_list_updated
        )
        self.recours_controller.encaissement_added.connect(
            self._on_encaissement_added
        )
        self.recours_controller.reversement_added.connect(
            self._on_reversement_added
        )
        self.recours_controller.relance_added.connect(self._on_relance_added)
        
        # ============================================================
        # AuditController
        # ============================================================
        self.audit_controller.error_occurred.connect(self._on_error)
        self.audit_controller.success_occurred.connect(self._on_success)
        self.audit_controller.logs_loaded.connect(self._on_logs_loaded)
        self.audit_controller.stats_loaded.connect(self._on_audit_stats_loaded)
 
    # ============================================================
    # SLOTS GÉNÉRIQUES (déjà présents)
    # ============================================================

    @Slot(str)
    def _on_error(self, message: str):
        QMessageBox.critical(self, "Erreur", message)

    @Slot(str)
    def _on_success(self, message: str):
        QMessageBox.information(self, "Succès", message)


    # ============================================================
    # SLOTS SINISTRE
    # ============================================================

    @Slot(dict)
    def _on_sinistre_created(self, data: dict):
        self._refresh_current_page()

    @Slot(dict)
    def _on_sinistre_updated(self, data: dict):
        self._refresh_current_page()

    @Slot(int, str)
    def _on_status_changed(self, sinistre_id: int, nouveau_statut: str):
        self._refresh_current_page()

    @Slot(list)
    def _on_sinistre_list_updated(self, data: list):
        if hasattr(self, 'current_list_widget'):
            self.current_list_widget = data

    @Slot(int)
    def _on_sinistre_deleted(self, sinistre_id: int):
        self._refresh_current_page()


    # ============================================================
    # SLOTS RÉFÉRENTIEL
    # ============================================================

    @Slot(dict)
    def _on_referentiel_created(self, data: dict):
        self._refresh_current_page()

    @Slot(dict)
    def _on_referentiel_updated(self, data: dict):
        self._refresh_current_page()

    @Slot(int)
    def _on_referentiel_deleted(self, referentiel_id: int):
        self._refresh_current_page()

    @Slot(list)
    def _on_referentiel_list_updated(self, data: list):
        pass


    # ============================================================
    # SLOTS EXPERTISE
    # ============================================================

    @Slot(dict)
    def _on_mission_created(self, data: dict):
        self._refresh_page("expertises")
        self._refresh_page("dashboard")

    @Slot(dict)
    def _on_mission_updated(self, data: dict):
        self._refresh_page("expertises")

    @Slot(int, str)
    def _on_mission_status_changed(self, mission_id: int, statut: str):
        self._refresh_page("expertises")

    @Slot(list)
    def _on_mission_list_updated(self, data: list):
        pass


    # ============================================================
    # SLOTS ÉVALUATION
    # ============================================================

    @Slot(dict)
    def _on_evaluation_created(self, data: dict):
        self._refresh_page("evaluations")
        self._refresh_page("dashboard")

    @Slot(dict)
    def _on_evaluation_updated(self, data: dict):
        self._refresh_page("evaluations")

    @Slot(int)
    def _on_evaluation_validated(self, evaluation_id: int):
        self._refresh_page("evaluations")

    @Slot(dict)
    def _on_evaluation_revised(self, data: dict):
        self._refresh_page("evaluations")

    @Slot(list)
    def _on_evaluation_list_updated(self, data: list):
        pass


    # ============================================================
    # SLOTS RÈGLEMENT
    # ============================================================

    @Slot(dict)
    def _on_reglement_created(self, data: dict):
        self._refresh_page("reglements")
        self._refresh_page("dashboard")

    @Slot(dict)
    def _on_reglement_updated(self, data: dict):
        self._refresh_page("reglements")

    @Slot(int)
    def _on_reglement_validated(self, reglement_id: int):
        self._refresh_page("reglements")

    @Slot(int)
    def _on_reglement_paid(self, reglement_id: int):
        self._refresh_page("reglements")
        self._refresh_page("dashboard")

    @Slot(list)
    def _on_reglement_list_updated(self, data: list):
        pass

    @Slot(dict)
    def _on_lot_created(self, data: dict):
        self._refresh_page("lots")
        self._refresh_page("reglements")


    # ============================================================
    # SLOTS RECOURS
    # ============================================================

    @Slot(dict)
    def _on_recours_created(self, data: dict):
        self._refresh_page("recours")
        self._refresh_page("dashboard")

    @Slot(dict)
    def _on_recours_updated(self, data: dict):
        self._refresh_page("recours")

    @Slot(int, str)
    def _on_recours_status_changed(self, recours_id: int, statut: str):
        self._refresh_page("recours")

    @Slot(list)
    def _on_recours_list_updated(self, data: list):
        pass

    @Slot(dict)
    def _on_encaissement_added(self, data: dict):
        self._refresh_page("recours")

    @Slot(dict)
    def _on_reversement_added(self, data: dict):
        self._refresh_page("recours")

    @Slot(dict)
    def _on_relance_added(self, data: dict):
        self._refresh_page("recours")


    # ============================================================
    # SLOTS AUDIT
    # ============================================================

    @Slot(list)
    def _on_logs_loaded(self, data: list):
        pass

    @Slot(dict)
    def _on_audit_stats_loaded(self, data: dict):
        pass


    # ============================================================
    # HELPER : Rafraîchir une page par nom
    # ============================================================

    def _refresh_page(self, page_id: str):
        """Rafraîchit une page spécifique si elle est déjà créée."""
        widget = self.page_widgets.get(page_id)
        if widget is None:
            return  # Page pas encore créée, rien à faire
        
        try:
            if hasattr(widget, 'refresh'):
                widget.refresh()
            elif hasattr(widget, 'load_data'):
                widget.load_data()
        except Exception as e:
            print(f"⚠️ Erreur refresh page '{page_id}': {e}")

    def _refresh_current_page(self):
        """Rafraîchit la page courante"""
        current_index = self.container.currentIndex()
        if current_index >= 0 and current_index < len(self.pages):
            page_name = self.pages[current_index]
            if page_name == "dashboard":
                if hasattr(self, 'dashboard_page'):
                    self.dashboard_page.refresh()
            elif page_name == "recherche":
                if hasattr(self, 'recherche_page'):
                    self.recherche_page.refresh()
            elif page_name == "expertises":
                if hasattr(self, 'expertises_page'):
                    self.expertises_page.load_data()
            elif page_name == "evaluations":
                if hasattr(self, 'evaluations_page'):
                    self.evaluations_page.load_data()
            elif page_name == "reglements":
                if hasattr(self, 'reglements_page'):
                    self.reglements_page.load_data()
            elif page_name == "recours":
                if hasattr(self, 'recours_page'):
                    self.recours_page.load_data()
    
    # ============================================================
    # SIDEBAR
    # ============================================================


    def setup_sidebar(self):
        """Création de la barre latérale moderne avec sections, recherche et profil"""
        
        # ═══════════════════════════════════════════════════════════════
        # CONTENEUR PRINCIPAL
        # ═══════════════════════════════════════════════════════════════
        self.sidebar_container = QFrame()
        self.sidebar_container.setFixedWidth(280)
        self.sidebar_container.setStyleSheet("""
            QFrame#SidebarContainer {
                background-color: #ffffff;
                border: none;
                border-right: 1px solid #e2e8f0;
            }
        """)
        self.sidebar_container.setObjectName("SidebarContainer")
        
        sidebar_layout = QVBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # ═══════════════════════════════════════════════════════════════
        # EN-TÊTE : LOGO + NOM DE L'APPLICATION
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
        
        # Icône du logo (dans un carré blanc)
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
        logo_icon.setPixmap(
            qta.icon('fa5s.car-crash', color='white').pixmap(QSize(24, 24))
        )
        logo_icon.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_icon)
        
        header_layout.addWidget(logo_container)
        
        # Texte du logo
        logo_text_layout = QVBoxLayout()
        logo_text_layout.setSpacing(0)
        logo_text_layout.setContentsMargins(0, 0, 0, 0)
        
        app_name = QLabel("LOMETA")
        app_name.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: 800;
            letter-spacing: 1px;
            background: transparent;
        """)
        logo_text_layout.addWidget(app_name)
        
        app_subtitle = QLabel("Gestion Sinistres")
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
            QLineEdit::placeholder {
                color: #94a3b8;
            }
        """)
        self.sidebar_search.textChanged.connect(self._filter_sidebar_items)
        search_layout.addWidget(self.sidebar_search)
        
        sidebar_layout.addWidget(search_container)
        
        # ═══════════════════════════════════════════════════════════════
        # ZONE SCROLLABLE POUR LES SECTIONS
        # ═══════════════════════════════════════════════════════════════
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        
        # ═══════════════════════════════════════════════════════════════
        # CONFIGURATION DES SECTIONS
        # ═══════════════════════════════════════════════════════════════
        sections = [
            {
                "title": "PRINCIPAL",
                "pages": [
                    ("Tableau de bord",  "dashboard",  "fa5s.chart-pie",     "#3b82f6", None),
                    ("Nouveau sinistre", "nouveau",    "fa5s.plus-circle",   "#10b981", None),
                    ("Recherche",        "recherche",  "fa5s.search",        "#8b5cf6", None),
                    ("Expertises",       "expertises",  "fa5s.microscope",    "#06b6d4", None),
                    ("Évaluations",      "evaluations", "fa5s.calculator",    "#f59e0b", None),
                    ("Règlements",       "reglements",  "fa5s.credit-card",   "#22c55e", None),
                    ("Recours",          "recours",     "fa5s.balance-scale", "#ef4444", None),
                    ("Lots de paiement", "lots",        "fa5s.boxes",         "#a855f7", None),
                    ("Comptabilité",     "comptabilite", "fa5s.book",          "#0ea5e9", None),
                    ("Documents",        "documents",   "fa5s.folder-open",   "#0ea5e9", None),
                    ("Audit & Historique", "audit",        "fa5s.history",     "#64748b", None),
                    ("Rôles & Permissions","roles",        "fa5s.user-shield", "#dc2626", None),
                    ("Référentiels",       "referentiels", "fa5s.book",        "#84cc16", None),
                    ("Paramètres",         "parametres",   "fa5s.cog",         "#475569", None),
                ]
            }
        ]
        
        # ✅ Filtrer selon les permissions
        pages_autorisees = self.permission_service.get_accessible_pages(
            getattr(self.user, 'id', None)
        ) if self.user else set()
        
        print(f"🔒 Pages autorisées pour "
            f"{self.user.username if self.user else 'Anonyme'}: {pages_autorisees}")
        
        self.pages = []
        self._page_rows = {}  # {page_id: row_index}
        
        # ═══════════════════════════════════════════════════════════════
        # CONSTRUCTION DES SECTIONS
        # ═══════════════════════════════════════════════════════════════
        for section in sections:
            # Filtrer les pages accessibles dans cette section
            section_pages = [
                p for p in section["pages"]
                if p[1] in pages_autorisees
            ]
            
            if not section_pages:
                continue  # Ignorer les sections vides
            
            # ─── Titre de la section ───
            section_title_container = QFrame()
            section_title_container.setStyleSheet("""
                QFrame {
                    background: transparent;
                    padding: 12px 20px 6px 20px;
                }
            """)
            st_layout = QVBoxLayout(section_title_container)
            st_layout.setContentsMargins(20, 12, 20, 6)
            
            section_title = QLabel(section["title"])
            section_title.setStyleSheet("""
                color: #94a3b8;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1.5px;
                background: transparent;
            """)
            st_layout.addWidget(section_title)
            
            scroll_layout.addWidget(section_title_container)
            
            # ─── Pages de la section ───
            for label, page_id, icon_name, icon_color, badge in section_pages:
                print(f"   ✅ Page '{page_id}' affichée")
                
                # Créer le widget de l'item
                item_widget = self._build_sidebar_item(
                    label, icon_name, icon_color, badge
                )
                
                # Créer l'item
                item = QListWidgetItem()
                item.setData(Qt.UserRole, page_id)
                item.setData(Qt.UserRole + 1, label.lower())  # pour la recherche
                item.setSizeHint(QSize(0, 56))
                
                # Stocker l'index de ligne
                self._page_rows[page_id] = len(self.pages)
                self.pages.append(page_id)
                
                # Ajouter au QListWidget
                if not hasattr(self, 'sidebar'):
                    self.sidebar = QListWidget()
                    self.sidebar.setStyleSheet("""
                        QListWidget {
                            background-color: transparent;
                            border: none;
                            outline: none;
                            padding: 0px 8px;
                            min-height: 800px;
                        }
                        QListWidget::item {
                            background: transparent;
                            border: none;
                            padding: 0;
                            margin: 2px 8px;
                        }
                        QListWidget::item:selected {
                            background: transparent;
                        }
                        QListWidget::item:hover {
                            background: transparent;
                        }
                    """)
                    self.sidebar.setFrameShape(QFrame.NoFrame)
                    self.sidebar.setFixedWidth(260)
                    self.sidebar.currentRowChanged.connect(self.switch_page)
                
                self.sidebar.addItem(item)
                self.sidebar.setItemWidget(item, item_widget)
            
            # Ajouter le QListWidget au layout après la première section
            if self.sidebar.count() > 0 and scroll_layout.count() == 1:
                scroll_layout.addWidget(self.sidebar)
            
            # Espacement après la section
            spacer = QWidget()
            spacer.setFixedHeight(8)
            spacer.setStyleSheet("background: transparent;")
            scroll_layout.addWidget(spacer)
        
        # ═══════════════════════════════════════════════════════════════
        # SI AUCUNE PAGE : message d'erreur
        # ═══════════════════════════════════════════════════════════════
        if not self.pages:
            no_access = QLabel(
                "⛔ Aucune page accessible\n\n"
                "Contactez un administrateur."
            )
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
        # PIED : CARTE UTILISATEUR + DÉCONNEXION
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
        
        # ─── Carte utilisateur ───
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
        
        # Avatar avec initiales
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
        
        # Infos utilisateur
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
        user_name.setWordWrap(False)
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
        
        # Bouton menu utilisateur
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
        
        # ─── Bouton déconnexion ───
        
        sidebar_layout.addWidget(footer)
        
        # Ajouter le conteneur au layout principal
    
        self.layout.addWidget(self.sidebar_container)

    # ============================================================
    # CONTENT AREA
    # ============================================================


    def setup_content_area(self):
        """Zone de contenu — avec barre de navigation."""
        self.content_container = QFrame()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(12)
        
        # ─── Barre de navigation (breadcrumb + boutons) ───
        nav_bar = self._build_nav_bar()
        self.content_layout.addWidget(nav_bar)
        
        # ─── Container des pages ───
        self.page_widgets = {}
        
        from addons.sinistres.views.widgets.loading_widget import LoadingPage
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
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.container.setGraphicsEffect(shadow)
        
        self.content_layout.addWidget(self.container, 1)
        self.layout.addWidget(self.content_container)


    def _build_nav_bar(self):
        """Barre de navigation avec bouton Retour + breadcrumb."""
        bar = QFrame()
        bar.setFixedHeight(44)
        bar.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # ─── Bouton Retour ───
        self.btn_back = QPushButton("←  Retour")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setFixedHeight(36)
        self.btn_back.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                color: #475569;
                font-size: 12px;
                font-weight: 600;
                padding: 0 16px;
            }
            QPushButton:hover {
                background: #f8fafc;
                border-color: #cbd5e1;
                color: #1e293b;
            }
            QPushButton:disabled {
                background: #f8fafc;
                color: #cbd5e1;
                border-color: #e2e8f0;
            }
        """)
        self.btn_back.clicked.connect(self._on_back_clicked)
        self.btn_back.setEnabled(False)
        layout.addWidget(self.btn_back)
        
        # ─── Breadcrumb ───
        self.lbl_breadcrumb = QLabel("Accueil")
        self.lbl_breadcrumb.setStyleSheet("""
            color: #64748b;
            font-size: 13px;
            font-weight: 500;
            background: transparent;
        """)
        layout.addWidget(self.lbl_breadcrumb)
        
        layout.addStretch()
        
        return bar


    def _on_back_clicked(self):
        """Revient à la page précédente."""
        if not hasattr(self, '_page_history') or not self._page_history:
            return
        
        # Dépiler la page courante
        self._page_history.pop()
        
        if self._page_history:
            previous_page = self._page_history[-1]
            if previous_page in self.pages:
                self.sidebar.setCurrentRow(self.pages.index(previous_page))
        else:
            self.sidebar.setCurrentRow(0)


    def _build_sidebar_item(self, label: str, icon_name: str, icon_color: str, badge: int = None) -> QWidget:
        """Construit un widget personnalisé pour un item de la sidebar"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)
        
        # ─── Icône ───
        icon_lbl = AnimatedIconLabel(
            icon_name=icon_name,
            color=icon_color,
            size=20
        )
        layout.addWidget(icon_lbl)
        
        # ─── Texte ───
        text_lbl = QLabel(label)
        text_lbl.setStyleSheet("""
            color: #475569;
            font-size: 14px;
            font-weight: 500;
            background: transparent;
        """)
        layout.addWidget(text_lbl)
        layout.addStretch()
        
        # ─── Badge (optionnel) ───
        badge_lbl = None
        if badge is not None and badge > 0:
            badge_lbl = QLabel(str(badge))
            badge_lbl.setFixedSize(20, 20)
            badge_lbl.setAlignment(Qt.AlignCenter)
            badge_lbl.setStyleSheet("""
                QLabel {
                    background: #ef4444;
                    color: white;
                    border-radius: 10px;
                    font-size: 10px;
                    font-weight: 700;
                    border: none;
                }
            """)
            layout.addWidget(badge_lbl)
        
        # Références
        widget._icon_label = icon_lbl
        widget._text_label = text_lbl
        widget._badge_label = badge_lbl
        widget._icon_name = icon_name
        widget._icon_color = icon_color
        widget._label_text = label
        widget._page_id = None  # rempli plus tard
        
        return widget

    # ═══════════════════════════════════════════════════════════════════
    # LAZY LOADING — Création des pages à la demande
    # ═══════════════════════════════════════════════════════════════════

    def _create_page(self, page_id: str):
        """
        Crée une page à la demande (Lazy Loading).
        Retourne le widget ou None si échec.
        """
        # Si déjà créée, la retourner
        if page_id in self.page_widgets:
            return self.page_widgets[page_id]
        
        widget = None
        
        try:
            # ═══════════════════════════════════════════════════════════
            # DASHBOARD
            # ═══════════════════════════════════════════════════════════
            if page_id == 'dashboard':
                self.dashboard_page = DashboardPage(
                    controller=self.sinistre_controller,
                    user=self.user,
                    referentiel_controller=self.referentiel_controller,
                    expertise_controller=self.expertise_controller,
                    evaluation_controller=self.evaluation_controller,
                    reglement_controller=self.reglement_controller,
                    recours_controller=self.recours_controller,
                )
                widget = self.dashboard_page
            
            # ═══════════════════════════════════════════════════════════
            # NOUVEAU SINISTRE
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'nouveau':
                self.nouveau_page = NouveauSinistrePage(
                    self.sinistre_controller,
                    self.referentiel_controller,
                    self.user
                )
                widget = self.nouveau_page
            
            # ═══════════════════════════════════════════════════════════
            # RECHERCHE
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'recherche':
                self.recherche_page = RecherchePage(
                    self.sinistre_controller,
                    self.referentiel_controller,
                    self.expertise_controller,
                    self.evaluation_controller,
                    self.reglement_controller,
                    self.recours_controller,
                    self.user
                )
                widget = self.recherche_page
            
            # ═══════════════════════════════════════════════════════════
            # EXPERTISES
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'expertises':
                self.expertises_page = ExpertisesPage(
                    self.expertise_controller, self.user
                )
                widget = self.expertises_page
            
            # ═══════════════════════════════════════════════════════════
            # ÉVALUATIONS
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'evaluations':
                self.evaluations_page = EvaluationsPage(
                    self.evaluation_controller, self.user
                )
                widget = self.evaluations_page
            
            # ═══════════════════════════════════════════════════════════
            # RÈGLEMENTS
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'reglements':
                self.reglements_page = ReglementsPage(
                    self.reglement_controller, self.user
                )
                widget = self.reglements_page
            
            # ═══════════════════════════════════════════════════════════
            # RECOURS
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'recours':
                self.recours_page = RecoursPage(
                    self.recours_controller, self.user
                )
                widget = self.recours_page

            # ═══════════════════════════════════════════════════════════
            # COMPTABILITÉ
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'comptabilite':
                self.comptabilite_page = ComptabilitePage(
                    self.comptabilite_controller, self.user
                )
                widget = self.comptabilite_page

            # ═══════════════════════════════════════════════════════════
            # RÉFÉRENTIELS
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'referentiels':
                self.referentiels_page = ReferentielsPage(
                    self.referentiel_controller, self.user
                )
                widget = self.referentiels_page
            
            # ═══════════════════════════════════════════════════════════
            # PARAMÈTRES
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'parametres':
                self.parametres_page = ParametresPage(
                    referentiel_controller=self.referentiel_controller,
                    user=self.user,
                    reglement_controller=self.reglement_controller,
                    audit_controller=self.audit_controller,
                )
                widget = self.parametres_page
            
            # ═══════════════════════════════════════════════════════════
            # LOTS DE PAIEMENT
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'lots':
                try:
                    from addons.sinistres.views.lots_page import LotsPage
                    self.lots_page = LotsPage(self.reglement_controller, self.user)
                    widget = self.lots_page
                except ImportError:
                    print("⚠️ LotsPage non disponible")
            
            # ═══════════════════════════════════════════════════════════
            # DOCUMENTS / GED
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'documents':
                try:
                    from addons.sinistres.views.documents_page import DocumentsPage
                    self.documents_page = DocumentsPage(
                        self.sinistre_controller, self.user
                    )
                    widget = self.documents_page
                except ImportError:
                    print("⚠️ DocumentsPage non disponible")
            
            # ═══════════════════════════════════════════════════════════
            # AUDIT
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'audit':
                try:
                    from addons.sinistres.views.audit_page import AuditPage
                    from addons.sinistres.controllers.audit_controller import AuditController
                    ac = AuditController()
                    ac.set_current_user(self.user)
                    self.audit_page = AuditPage(ac, self.user)
                    widget = self.audit_page
                except ImportError:
                    print("⚠️ AuditPage non disponible")
            
            # ═══════════════════════════════════════════════════════════
            # RÔLES
            # ═══════════════════════════════════════════════════════════
            elif page_id == 'roles':
                try:
                    from addons.sinistres.views.roles_page import RolesPage
                    from addons.sinistres.controllers.permission_controller import (
                        PermissionController
                    )
                    pc = PermissionController()
                    pc.set_current_user(self.user)
                    self.roles_page = RolesPage(pc, self.user)
                    widget = self.roles_page
                except ImportError:
                    print("⚠️ RolesPage non disponible")
            
            # ✅ Mise en cache
            if widget:
                self.page_widgets[page_id] = widget
                self.container.addWidget(widget)
                print(f"✅ Page '{page_id}' créée")
            
            return widget
        
        except Exception as e:
            print(f"❌ Erreur création page '{page_id}': {e}")
            import traceback
            traceback.print_exc()
            return None


    # ═══════════════════════════════════════════════════════════════════
    # SWITCH PAGE — Lazy Loading avec LoadingPage
    # ═══════════════════════════════════════════════════════════════════


    def _highlight_sidebar_item(self, active_index: int):
        """Met en surbrillance l'item actif avec couleurs dérivées de son icône"""
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            widget = self.sidebar.itemWidget(item)
            if not widget:
                continue
            
            is_active = (i == active_index)
            
            # ✅ Récupérer la couleur de l'icône de CE widget
            icon_color = getattr(widget, '_icon_color', '#1a73e8')
            
            if is_active:
                # ─── État actif : couleurs dérivées de l'icône ───
                
                # Fond très clair (10% de la couleur)
                bg_color = rgba(icon_color, 0.10)
                
                # Bordure gauche en couleur pleine
                # Texte dans la couleur légèrement foncée
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
                
                # Animer l'icône
                if hasattr(widget, '_icon_label'):
                    icon_lbl = widget._icon_label
                    
                    # ✅ Utiliser la couleur de l'icône (déjà correcte)
                    if hasattr(icon_lbl, 'set_color'):
                        icon_lbl.set_color(icon_color)
                    
                    # Pulse continu
                    if hasattr(icon_lbl, 'start_pulse_continuous'):
                        icon_lbl.start_pulse_continuous(
                            max_scale=1.25,
                            duration_ms=600
                        )
            else:
                # ─── État inactif : style neutre ───
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
                
                if hasattr(widget, '_icon_label'):
                    icon_lbl = widget._icon_label
                    
                    if hasattr(icon_lbl, 'stop_pulse_continuous'):
                        icon_lbl.stop_pulse_continuous()
                    
                    if hasattr(icon_lbl, 'stop_floating'):
                        icon_lbl.stop_floating()
                    
                    if hasattr(icon_lbl, 'set_color'):
                        icon_lbl.set_color(widget._icon_color)


    def _filter_sidebar_items(self, text: str):
        """Filtre les items et masque les sections vides."""
        text = text.strip().lower()
        
        # Compter les items visibles par section
        visible_count = 0
        
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            label = item.data(Qt.UserRole + 1) or ""
            
            is_visible = (not text or text in label)
            item.setHidden(not is_visible)
            
            if is_visible:
                visible_count += 1
        
        # Masquer les titres de section si aucune page n'est visible
        # (il faut stocker les références aux titres dans une liste)
        for title_widget in getattr(self, '_section_title_widgets', []):
            title_widget.setVisible(visible_count > 0)


    def _on_logout_clicked(self):
        """Gère le clic sur Déconnexion"""
        reply = QMessageBox.question(
            self,
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Émettre un signal si vous en avez un
            # ou appeler directement la méthode de logout
            if hasattr(self, 'logout_requested'):
                self.logout_requested.emit()
            else:
                print("🔒 Déconnexion demandée")
                # Fermer la fenêtre principale
                parent = self.parent()
                while parent and not hasattr(parent, 'close'):
                    parent = parent.parent()
                if parent:
                    parent.close()


    def _show_user_menu(self):
        """Affiche le menu contextuel de l'utilisateur"""
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
        
        # Nom de l'utilisateur en en-tête
        header = menu.addAction(f"👤 {getattr(self.user, 'full_name', 'Utilisateur')}")
        header.setEnabled(False)
        
        menu.addSeparator()
        
        # Actions
        action_profile = menu.addAction("⚙️  Mon profil")
        action_profile.triggered.connect(lambda: print("Profil"))
        
        action_password = menu.addAction("🔑  Changer mot de passe")
        action_password.triggered.connect(lambda: print("Changer mdp"))
        
        action_settings = menu.addAction("🛠️  Paramètres")
        action_settings.triggered.connect(lambda: self.switch_page(
            self.pages.index("parametres") if "parametres" in self.pages else 0
        ))
        
        menu.addSeparator()
        
        # Déconnexion
        action_logout = menu.addAction("🚪  Déconnexion")
        action_logout.triggered.connect(self._on_logout_clicked)
        
        # Position : à droite du bouton
        sender = self.sender()
        if sender:
            menu.exec(sender.mapToGlobal(sender.rect().bottomRight()))
        else:
            menu.exec(QCursor.pos())


    def switch_page(self, index: int):
        """Change la page affichée — Lazy Loading avec cache"""
        if not (0 <= index < len(self.pages)):
            return

        self._highlight_sidebar_item(index)
        page_id = self.pages[index]
        widget = self.page_widgets.get(page_id)

        #✅ Historique de navigation
        if not hasattr(self, '_page_history'):
            self._page_history = []
        
        # Éviter les doublons consécutifs
        if not self._page_history or self._page_history[-1] != page_id:
            self._page_history.append(page_id)
            # Limiter la taille
            if len(self._page_history) > 20:
                self._page_history.pop(0)
        
        # Mettre à jour le breadcrumb
        if hasattr(self, 'lbl_breadcrumb'):
            self.lbl_breadcrumb.setText(f"Accueil  ›  {page_id.capitalize()}")
        
        # Activer/désactiver le bouton Retour
        if hasattr(self, 'btn_back'):
            self.btn_back.setEnabled(len(self._page_history) > 1)
        
        # ═══════════════════════════════════════════════════════════════
        # CAS 1 : Première visite — Créer + charger
        # ═══════════════════════════════════════════════════════════════
        if widget is None:
            messages = {
                'dashboard': "Préparation du tableau de bord...",
                'nouveau': "Chargement du formulaire...",
                'recherche': "Initialisation de la recherche...",
                'expertises': "Chargement des expertises...",
                'evaluations': "Chargement des évaluations...",
                'reglements': "Chargement des règlements...",
                'recours': "Chargement des recours...",
                'referentiels': "Chargement des référentiels...",
                'parametres': "Chargement des paramètres...",
                'comptabilite': "Chargement de la comptabilité...",
                'lots': "Chargement des lots de paiement...",
                'documents': "Chargement des documents...",
                'audit': "Chargement de l'historique...",
                'roles': "Chargement des rôles et permissions...",
            }
            self.loading_page.set_message(messages.get(page_id, "Chargement..."))
            self.loading_page.set_subtitle("Veuillez patienter quelques instants...")
            
            self.container.setCurrentWidget(self.loading_page)
            
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()
            
            # ✅ Créer la page (avec try/except sécurisé)
            try:
                widget = self._create_page(page_id)
            except Exception as create_error:
                # ✅ CORRECTION : capturer le message d'erreur HORS du lambda
                error_message = str(create_error)
                import traceback
                traceback.print_exc()
                
                error_widget = QLabel(
                    f"⚠️ Impossible de charger la page '{page_id}'.\n\n"
                    f"Erreur : {error_message}"
                )
                error_widget.setAlignment(Qt.AlignCenter)
                error_widget.setStyleSheet("""
                    color: #94a3b8;
                    font-size: 14px;
                    padding: 40px;
                """)
                self.container.addWidget(error_widget)
                self.container.setCurrentWidget(error_widget)
                return
            
            if widget is None:
                error_widget = QLabel(
                    f"⚠️ Impossible de charger la page '{page_id}'.\n\n"
                    f"Vérifiez que le module correspondant est bien installé."
                )
                error_widget.setAlignment(Qt.AlignCenter)
                error_widget.setStyleSheet("""
                    color: #94a3b8;
                    font-size: 14px;
                    padding: 40px;
                """)
                self.container.addWidget(error_widget)
                self.container.setCurrentWidget(error_widget)
                return
            
            # ✅ Charger les données
            self.loading_page.set_message("Chargement des données...")
            QApplication.processEvents()
            
            try:
                if hasattr(widget, 'refresh'):
                    widget.refresh()
                elif hasattr(widget, 'load_data'):
                    widget.load_data()
                widget._has_loaded = True
            except Exception as refresh_error:
                print(f"❌ Erreur refresh {page_id}: {refresh_error}")
                import traceback
                traceback.print_exc()
            
            # ✅ Afficher la page avec délai pour voir l'animation
            def do_switch():
                self.container.setCurrentWidget(widget)
            
            QTimer.singleShot(300, do_switch)
        
        # ═══════════════════════════════════════════════════════════════
        # CAS 2 : Page déjà visitée — Afficher directement
        # ═══════════════════════════════════════════════════════════════
        else:
            self.container.setCurrentWidget(widget)
            
            if hasattr(widget, 'refresh'):
                try:
                    QTimer.singleShot(10, widget.refresh)
                except Exception:
                    pass


    def _animate_widget_bg(self, widget, from_color: str, to_color: str, duration: int = 300):
        """Anime la transition de couleur de fond d'un widget"""
        from PySide6.QtCore import QVariantAnimation
        
        anim = QVariantAnimation(self)
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        def update_bg(t):
            # Interpolation linéaire RGB
            r1, g1, b1 = hex_to_rgb(from_color) if from_color.startswith('#') else (255, 255, 255)
            r2, g2, b2 = hex_to_rgb(to_color) if to_color.startswith('#') else (255, 255, 255)
            
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            
            widget.setStyleSheet(f"""
                QWidget {{
                    background: rgb({r}, {g}, {b});
                    border-radius: 10px;
                }}
            """)
        
        anim.valueChanged.connect(update_bg)
        anim.start()
        widget._bg_anim = anim  # garder une référence               


    def _run_async_refresh(self, widget, page_id: str):
        """Lance refresh_async et connecte les signaux de progression"""
        
        # Connecter les signaux
        def on_progress(percent: int, message: str):
            # Mapper 0-100 du widget vers 40-90% de la progression globale
            mapped = 40 + int((percent / 100) * 50)
            self.loading_page.set_percent(mapped)
            self.loading_page.set_subtitle(message)
            QApplication.processEvents()
        
        def on_error(msg: str):
            print(f"❌ Erreur refresh: {msg}")
            self.loading_page.step_error("data", msg)
        
        def on_finished():
            self.loading_page.step_done("data")
            self.loading_page.step_started("render", "Finalisation...")
            QApplication.processEvents()
            
            self.container.addWidget(widget)
            self.page_widgets[page_id] = widget
            widget._has_loaded = True
            
            QThread.msleep(100)
            self.loading_page.step_done("render")
            QApplication.processEvents()
            
            self._wait_and_switch(widget)
        
        widget.refresh_progress.connect(on_progress)
        widget.refresh_error.connect(on_error)
        widget.refresh_finished.connect(on_finished)
        
        # Lancer le refresh
        widget.refresh_async()


    def _wait_and_switch(self, widget):
        """Attend que la progression atteigne 100% avant de basculer"""
        def check():
            if self.loading_page._current_progress >= 100:
                self.container.setCurrentWidget(widget)
            else:
                QTimer.singleShot(50, check)
        
        QTimer.singleShot(100, check)


    def _build_error_widget(self, page_id: str, error: str) -> QWidget:
        """Widget d'erreur stylisé"""
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


    def closeEvent(self, event):
        """Nettoyage à la fermeture."""
        # 1. Arrêter le heartbeat
        if hasattr(self, '_heartbeat_timer'):
            self._heartbeat_timer.stop()
        
        # 2. Fermer les pages (si elles ont un closeEvent)
        for page_id, widget in self.page_widgets.items():
            try:
                if hasattr(widget, 'close'):
                    widget.close()
            except Exception as e:
                print(f"⚠️ Erreur fermeture page '{page_id}': {e}")
        
        # 3. Fermer les contrôleurs (si méthode close)
        for controller_name in [
            'sinistre_controller', 'referentiel_controller',
            'expertise_controller', 'evaluation_controller', 'comptabilite_controller',
            'reglement_controller', 'recours_controller', 'audit_controller',
        ]:
            controller = getattr(self, controller_name, None)
            if controller and hasattr(controller, 'close'):
                try:
                    controller.close()
                except Exception as e:
                    print(f"⚠️ Erreur fermeture {controller_name}: {e}")
        
        # 4. Appeler le parent
        super().closeEvent(event)