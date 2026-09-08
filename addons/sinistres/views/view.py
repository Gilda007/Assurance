

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
    QProgressBar, QToolBar, QMenu, QCheckBox, QRadioButton
)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QDate
from PySide6.QtGui import QColor, QIcon, QFont

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Import des contrôleurs
from addons.sinistres.controllers.sinistre_controller import SinistreController
from addons.sinistres.controllers.referentiel_controller import ReferentielController
from addons.sinistres.controllers.expertise_controller import ExpertiseController
from addons.sinistres.controllers.evaluation_controller import EvaluationController
from addons.sinistres.controllers.reglement_controller import ReglementController
from addons.sinistres.controllers.recours_controller import RecoursController

# Import des vues détaillées
from addons.sinistres.views.dossier_360 import Dossier360View
from addons.sinistres.views.parametres_page import ParametresPage
from addons.sinistres.views.tableau_base import TableauActions

# Importation des pages spécifiques
from addons.sinistres.views.dashboard_view import DashboardPage
from addons.sinistres.views.sinistre_form_view import NouveauSinistrePage
from addons.sinistres.views.search_view import RecherchePage
from addons.sinistres.views.expertise_page import ExpertisesPage 
from addons.sinistres.views.evaluation_page import EvaluationsPage
from addons.sinistres.views.reglement_page import ReglementsPage
from addons.sinistres.views.recours_page import RecoursPage
from addons.sinistres.views.referentiel_page import ReferentielsPage


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
        self.user = user
        self.pages_cache = {}
        
        # Style Global
        self.setObjectName("LometaMainView")
        self.setStyleSheet("background-color: #f8fafc;")

        # Layout principal
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Configurer la sidebar et le contenu
        self.setup_sidebar()
        self.setup_content_area()
        
        # Sélectionner la première page
        if hasattr(self, 'sidebar') and self.sidebar.count() > 0:
            self.sidebar.setCurrentRow(0)
        
        # Connecter les signaux des contrôleurs
        self._connect_signals()
    
    def _connect_signals(self):
        """Connecte les signaux des contrôleurs aux slots"""
        # SinistreController
        self.sinistre_controller.error_occurred.connect(self._on_error)
        self.sinistre_controller.success_occurred.connect(self._on_success)
        self.sinistre_controller.sinistre_created.connect(self._on_sinistre_created)
        self.sinistre_controller.sinistre_updated.connect(self._on_sinistre_updated)
        self.sinistre_controller.sinistre_status_changed.connect(self._on_status_changed)
        self.sinistre_controller.sinistre_list_updated.connect(self._on_sinistre_list_updated)
        
        # ReferentielController
        self.referentiel_controller.error_occurred.connect(self._on_error)
        self.referentiel_controller.success_occurred.connect(self._on_success)
        
        # ExpertiseController
        self.expertise_controller.error_occurred.connect(self._on_error)
        self.expertise_controller.success_occurred.connect(self._on_success)
        
        # EvaluationController
        self.evaluation_controller.error_occurred.connect(self._on_error)
        self.evaluation_controller.success_occurred.connect(self._on_success)
        
        # ReglementController
        self.reglement_controller.error_occurred.connect(self._on_error)
        self.reglement_controller.success_occurred.connect(self._on_success)
        
        # RecoursController
        self.recours_controller.error_occurred.connect(self._on_error)
        self.recours_controller.success_occurred.connect(self._on_success)
    
    @Slot(str)
    def _on_error(self, message: str):
        """Gère les erreurs des contrôleurs"""
        QMessageBox.critical(self, "Erreur", message)
    
    @Slot(str)
    def _on_success(self, message: str):
        """Gère les succès des contrôleurs"""
        QMessageBox.information(self, "Succès", message)
    
    @Slot(dict)
    def _on_sinistre_created(self, data: dict):
        """Rafraîchit après création d'un sinistre"""
        self._refresh_current_page()
    
    @Slot(dict)
    def _on_sinistre_updated(self, data: dict):
        """Rafraîchit après mise à jour d'un sinistre"""
        self._refresh_current_page()
    
    @Slot(int, str)
    def _on_status_changed(self, sinistre_id: int, nouveau_statut: str):
        """Rafraîchit après changement de statut"""
        self._refresh_current_page()
    
    @Slot(list)
    def _on_sinistre_list_updated(self, data: list):
        """Met à jour la liste des sinistres"""
        if hasattr(self, 'current_list_widget'):
            self.current_list_widget = data
    
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
        """Création de la barre latérale avec les pages"""
        self.sidebar_container = QFrame()
        self.sidebar_container.setFixedWidth(260)
        self.sidebar_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 0px;
                border-right: 1px solid #e2e8f0;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)
        
        # Titre
        title_label = QLabel("🏛️ LOMETA")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1a73e8;
                padding-bottom: 15px;
                border-bottom: 2px solid #e2e8f0;
            }
        """)
        sidebar_layout.addWidget(title_label)
        
        # Sous-titre
        subtitle = QLabel("Gestion des Sinistres")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #64748b;
                margin-bottom: 10px;
            }
        """)
        sidebar_layout.addWidget(subtitle)
        
        # Liste des pages
        self.sidebar = QListWidget()
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-radius: 8px;
                color: #64748b;
                font-size: 14px;
                font-weight: 500;
            }
            QListWidget::item:hover {
                background-color: #f1f5f9;
                color: #1e293b;
            }
            QListWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
                border-right: 3px solid #1a73e8;
            }
        """)
        self.sidebar.setFixedWidth(230)
        
        # Pages du module LOMETA
        self.pages = [
            "dashboard",
            "nouveau",
            "recherche",
            "expertises",
            "evaluations",
            "reglements",
            "recours",
            "referentiels",
            "parametres" 
        ]
        
        page_labels = [
            ("📊 Tableau de bord", "dashboard"),
            ("📝 Nouveau sinistre", "nouveau"),
            ("🔍 Recherche", "recherche"),
            ("🔬 Expertises", "expertises"),
            ("💰 Évaluations", "evaluations"),
            ("💳 Règlements", "reglements"),
            ("⚖️ Recours", "recours"),
            ("⚙️ Référentiels", "referentiels"),
            ("⚙️ Paramètres", "parametres") 
        ]
        
        for label, page_id in page_labels:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, page_id)
            self.sidebar.addItem(item)
        
        self.sidebar.currentRowChanged.connect(self.switch_page)
        sidebar_layout.addWidget(self.sidebar)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #e2e8f0; max-height: 1px;")
        sidebar_layout.addWidget(separator)
        
        # Statistiques rapides
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                color: #1e293b;
                font-size: 11px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("📈 Statistiques rapides")
        stats_title.setStyleSheet("font-weight: bold; font-size: 12px;")
        stats_layout.addWidget(stats_title)
        
        self.stats_ouverts = QLabel("🔴 Ouverts: 0")
        self.stats_encours = QLabel("🟡 En cours: 0")
        self.stats_clotures = QLabel("✅ Clôturés: 0")
        stats_layout.addWidget(self.stats_ouverts)
        stats_layout.addWidget(self.stats_encours)
        stats_layout.addWidget(self.stats_clotures)
        
        sidebar_layout.addWidget(stats_frame)
        sidebar_layout.addStretch()
        
        # Informations utilisateur
        user_info = QFrame()
        user_info.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border-radius: 10px;
                padding: 12px;
                margin-top: 10px;
            }
            QLabel {
                color: #1e293b;
                font-size: 12px;
            }
        """)
        user_layout = QVBoxLayout(user_info)
        
        user_name = QLabel(f"👤 {self.user.full_name if self.user and hasattr(self.user, 'full_name') else 'Utilisateur'}")
        user_name.setStyleSheet("font-weight: bold; font-size: 13px;")
        user_layout.addWidget(user_name)
        
        user_role = QLabel(f"Rôle: {self.user.role if self.user else 'Non défini'}")
        user_role.setStyleSheet("color: #64748b; font-size: 11px;")
        user_layout.addWidget(user_role)
        
        sidebar_layout.addWidget(user_info)
        
        self.layout.addWidget(self.sidebar_container)
    
    # ============================================================
    # CONTENT AREA
    # ============================================================
    
    def setup_content_area(self):
        """Zone de contenu avec les pages"""
        self.content_container = QFrame()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        self.container = QStackedWidget()
        self.container.setStyleSheet("""
            QStackedWidget {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        # Effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.container.setGraphicsEffect(shadow)
        
        # ✅ Création des pages avec TOUS les contrôleurs
        self.dashboard_page = DashboardPage(self.sinistre_controller, self.user)
        self.nouveau_page = NouveauSinistrePage(self.sinistre_controller, self.referentiel_controller, self.user)
        self.recherche_page = RecherchePage(
            self.sinistre_controller,
            self.referentiel_controller,
            self.expertise_controller,
            self.evaluation_controller,
            self.reglement_controller,
            self.recours_controller,
            self.user
        )
        self.expertises_page = ExpertisesPage(self.expertise_controller, self.user)
        self.evaluations_page = EvaluationsPage(self.evaluation_controller, self.user)
        self.reglements_page = ReglementsPage(self.reglement_controller, self.user)
        self.recours_page = RecoursPage(self.recours_controller, self.user)
        self.referentiels_page = ReferentielsPage(self.referentiel_controller, self.user)
        self.parametres_page = ParametresPage(self.referentiel_controller, self.user)
        
        self.container.addWidget(self.dashboard_page)      # index 0
        self.container.addWidget(self.nouveau_page)        # index 1
        self.container.addWidget(self.recherche_page)      # index 2
        self.container.addWidget(self.expertises_page)     # index 3
        self.container.addWidget(self.evaluations_page)    # index 4
        self.container.addWidget(self.reglements_page)     # index 5
        self.container.addWidget(self.recours_page)        # index 6
        self.container.addWidget(self.referentiels_page)   # index 7
        self.container.addWidget(self.parametres_page)     # index 8
        
        self.content_layout.addWidget(self.container)
        self.layout.addWidget(self.content_container)
    
    def switch_page(self, index):
        """Change la page affichée"""
        if 0 <= index < self.container.count():
            self.container.setCurrentIndex(index)
            # Rafraîchir la page si nécessaire
            if index == 0:  # Dashboard
                self.dashboard_page.refresh()
            elif index == 2:  # Recherche
                self.recherche_page.refresh()
            elif index == 3:  # Expertises
                self.expertises_page.load_data()
            elif index == 4:  # Évaluations
                self.evaluations_page.load_data()
            elif index == 5:  # Règlements
                self.reglements_page.load_data()
            elif index == 6:  # Recours
                self.recours_page.load_data()
            elif index == 8:  # Paramètres
                self.parametres_page.load_data()


    