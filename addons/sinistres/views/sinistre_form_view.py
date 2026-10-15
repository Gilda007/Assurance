
# """
# Formulaire de création de sinistre - Version professionnelle v2.0
# Design moderne avec cartes, progression et récapitulatif
# """
# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
#     QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox,
#     QFormLayout, QGroupBox, QFrame, QMessageBox, QScrollArea,
#     QGraphicsDropShadowEffect, QGridLayout, QSizePolicy, QSpacerItem,
#     QProgressBar, QMenu
# )
# from PySide6.QtCore import Qt, Signal, QDate, QSize, QTimer, QPropertyAnimation, QEasingCurve
# from PySide6.QtGui import QColor, QFont, QIcon, QPixmap, QPainter, QBrush, QPen, QAction

# from datetime import datetime, timedelta


# # ═══════════════════════════════════════════════════════════════════
# # HELPERS
# # ═══════════════════════════════════════════════════════════════════

# def _safe_bool(value) -> bool:
#     if value is None:
#         return False
#     if isinstance(value, str):
#         return value.strip().lower() not in ('', 'none', 'null', '0', 'false')
#     return bool(value)


# # ═══════════════════════════════════════════════════════════════════
# # STYLES CONSTANTS
# # ═══════════════════════════════════════════════════════════════════

# STYLE_CARD = """
#     QFrame#Card {
#         background-color: white;
#         border: 1px solid #e2e8f0;
#         border-radius: 12px;
#     }
# """

# STYLE_CARD_HEADER = """
#     QLabel#CardTitle {
#         font-size: 14px;
#         font-weight: 700;
#         color: #0f172a;
#     }
#     QLabel#CardIcon {
#         font-size: 18px;
#     }
# """

# STYLE_INPUT = """
#     QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox {
#         background-color: #f8fafc;
#         border: 1px solid #e2e8f0;
#         border-radius: 8px;
#         padding: 8px 12px;
#         font-size: 13px;
#         color: #1e293b;
#         min-height: 20px;
#     }
#     QLineEdit:hover, QComboBox:hover, QDateEdit:hover,
#     QTextEdit:hover, QDoubleSpinBox:hover {
#         border-color: #cbd5e1;
#     }
#     QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
#     QTextEdit:focus, QDoubleSpinBox:focus {
#         border: 2px solid #3b82f6;
#         background-color: white;
#     }
#     QLineEdit:disabled, QComboBox:disabled {
#         background-color: #f1f5f9;
#         color: #94a3b8;
#     }
#     QComboBox::drop-down { border: none; width: 24px; }
#     QComboBox::down-arrow {
#         image: none;
#         border-left: 4px solid transparent;
#         border-right: 4px solid transparent;
#         border-top: 5px solid #64748b;
#         margin-right: 8px;
#     }
# """

# STYLE_REQUIRED = """
#     QLineEdit, QComboBox, QDateEdit, QTextEdit {
#         background-color: #fffbeb;
#         border: 1px solid #fde047;
#         border-radius: 8px;
#         padding: 8px 12px;
#         font-size: 13px;
#         color: #1e293b;
#         min-height: 20px;
#     }
#     QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
#         border: 2px solid #3b82f6;
#         background-color: white;
#     }
# """

# STYLE_BADGE_SUCCESS = """
#     QLabel {
#         background-color: #d1fae5;
#         color: #065f46;
#         padding: 4px 10px;
#         border-radius: 11px;
#         font-size: 11px;
#         font-weight: 700;
#     }
# """

# STYLE_BADGE_ERROR = """
#     QLabel {
#         background-color: #fed7aa;
#         color: #9a3412;
#         padding: 4px 10px;
#         border-radius: 11px;
#         font-size: 11px;
#         font-weight: 700;
#     }
# """

# STYLE_FLOTTE_BANNER = """
#     QFrame {
#         background-color: #eff6ff;
#         border-left: 4px solid #3b82f6;
#         border-radius: 8px;
#         padding: 10px;
#     }
#     QLabel {
#         color: #1e40af;
#         font-size: 12px;
#         font-weight: 600;
#         background: transparent;
#     }
# """

# STYLE_BTN_PRIMARY = """
#     QPushButton {
#         background-color: #2563eb;
#         color: white;
#         padding: 10px 28px;
#         border-radius: 8px;
#         font-weight: 700;
#         font-size: 13px;
#         border: none;
#     }
#     QPushButton:hover { background-color: #1d4ed8; }
#     QPushButton:pressed { background-color: #1e40af; }
#     QPushButton:disabled {
#         background-color: #cbd5e1;
#         color: #94a3b8;
#     }
# """

# STYLE_BTN_SECONDARY = """
#     QPushButton {
#         background-color: white;
#         color: #64748b;
#         padding: 10px 20px;
#         border-radius: 8px;
#         font-weight: 600;
#         font-size: 13px;
#         border: 1px solid #e2e8f0;
#     }
#     QPushButton:hover {
#         background-color: #f8fafc;
#         border-color: #cbd5e1;
#         color: #1e293b;
#     }
# """

# STYLE_SUMMARY_CARD = """
#     QFrame#SummaryCard {
#         background-color: #f8fafc;
#         border: 1px solid #e2e8f0;
#         border-radius: 12px;
#     }
# """

# STYLE_STEP_BADGE_ACTIVE = """
#     QLabel {
#         background-color: #2563eb;
#         color: white;
#         border-radius: 12px;
#         padding: 4px 14px;
#         font-size: 11px;
#         font-weight: 700;
#     }
# """

# STYLE_STEP_BADGE_INACTIVE = """
#     QLabel {
#         background-color: #f1f5f9;
#         color: #94a3b8;
#         border-radius: 12px;
#         padding: 4px 14px;
#         font-size: 11px;
#         font-weight: 600;
#     }
# """


# # ═══════════════════════════════════════════════════════════════════
# # WIDGETS PERSONNALISÉS
# # ═══════════════════════════════════════════════════════════════════

# class Card(QFrame):
#     """Carte avec titre et icône (style moderne)"""
    
#     def __init__(self, icon: str, title: str, parent=None):
#         super().__init__(parent)
#         self.setObjectName("Card")
#         self.setStyleSheet(STYLE_CARD)
        
#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(8)
#         shadow.setColor(QColor(0, 0, 0, 10))
#         shadow.setOffset(0, 2)
#         self.setGraphicsEffect(shadow)
        
#         self.layout = QVBoxLayout(self)
#         self.layout.setContentsMargins(20, 16, 20, 18)
#         self.layout.setSpacing(14)
        
#         # Header
#         header = QHBoxLayout()
#         header.setSpacing(8)
        
#         lbl_icon = QLabel(icon)
#         lbl_icon.setObjectName("CardIcon")
#         lbl_icon.setStyleSheet(STYLE_CARD_HEADER)
#         header.addWidget(lbl_icon)
        
#         lbl_title = QLabel(title)
#         lbl_title.setObjectName("CardTitle")
#         lbl_title.setStyleSheet(STYLE_CARD_HEADER)
#         header.addWidget(lbl_title)
#         header.addStretch()
        
#         self.layout.addLayout(header)
        
#         # Séparateur
#         sep = QFrame()
#         sep.setFrameShape(QFrame.HLine)
#         sep.setStyleSheet("background-color: #f1f5f9; max-height: 1px; border: none;")
#         self.layout.addWidget(sep)
        
#         # Zone de contenu
#         self.content = QVBoxLayout()
#         self.content.setSpacing(12)
#         self.layout.addLayout(self.content)
    
#     def add_row(self, label: str, widget: QWidget, required: bool = False):
#         """Ajoute une ligne label + widget"""
#         row = QHBoxLayout()
#         row.setSpacing(15)
        
#         lbl = QLabel(label + (" *" if required else ""))
#         lbl.setStyleSheet(f"""
#             font-size: 12px;
#             font-weight: 600;
#             color: {'#1e293b' if required else '#475569'};
#             background: transparent;
#             min-width: 140px;
#         """)
#         row.addWidget(lbl)
#         row.addWidget(widget, 1)
#         self.content.addLayout(row)
#         return lbl


# class Badge(QLabel):
#     """Badge coloré"""
    
#     def __init__(self, text: str, success: bool = True, parent=None):
#         super().__init__(text, parent)
#         self.setStyleSheet(STYLE_BADGE_SUCCESS if success else STYLE_BADGE_ERROR)
#         self.setAlignment(Qt.AlignCenter)


# # ═══════════════════════════════════════════════════════════════════
# # PAGE PRINCIPALE
# # ═══════════════════════════════════════════════════════════════════

# class NouveauSinistrePage(QWidget):
#     """Formulaire de création de sinistre — Design moderne v2.0"""
    
#     sinistre_created = Signal(dict)
    
#     def __init__(self, sinistre_controller, referentiel_controller, user):
#         super().__init__()
#         self.sinistre_controller = sinistre_controller
#         self.referentiel_controller = referentiel_controller
#         self.user = user
        
#         # Permissions
#         from addons.sinistres.services.permission_service import PermissionService
#         from addons.sinistres.security.permissions_helper import PermissionsUI
#         self.permission_service = PermissionService()
#         self.permissions_ui = PermissionsUI(user, self.permission_service)
        
#         from addons.sinistres.controllers.automobile_controller import AutomobileController
#         self.automobile_controller = AutomobileController()
#         self.automobile_controller.set_current_user(user)
        
#         self._vehicule_sinistre = None
#         self._branches_cache = {}
#         self._circonstances_cache = {}
#         self._responsabilites_cache = {}
        
#         self.setup_ui()
#         self.load_referentiels()
#         self._connect_validators()
        
#         # Vérifier la permission CREATE sinistre
#         if not self.permissions_ui.peut('sinistre', 'CREATE'):
#             self.btn_creer.setEnabled(False)
#             self.btn_creer.setText("⛔  Non autorisé")
#             self.btn_creer.setToolTip("Vous n'avez pas la permission de créer un sinistre")
    
#     # ═══════════════════════════════════════════════════════════════
#     # UI PRINCIPALE
#     # ═══════════════════════════════════════════════════════════════
    
#     def setup_ui(self):
#         # Fond gris clair
#         self.setStyleSheet("background: #f1f5f9;")
        
#         root = QVBoxLayout(self)
#         root.setContentsMargins(0, 0, 0, 0)
#         root.setSpacing(0)
        
#         # En-tête fixe
#         root.addWidget(self._build_header())
        
#         # Corps scrollable + panneau latéral
#         body = QHBoxLayout()
#         body.setContentsMargins(24, 20, 24, 20)
#         body.setSpacing(20)
        
#         body.addWidget(self._build_form_column(), 3)
#         body.addWidget(self._build_summary_column(), 1)
        
#         root.addLayout(body, 1)
        
#         # Pied fixe
#         root.addWidget(self._build_footer())
    
#     def _build_header(self) -> QWidget:
#         """En-tête avec titre et stepper"""
#         header = QFrame()
#         header.setStyleSheet("""
#             QFrame {
#                 background-color: white;
#                 border-bottom: 1px solid #e2e8f0;
#                 border-radius: 0;
#             }
#         """)
#         header.setFixedHeight(90)
        
#         layout = QHBoxLayout(header)
#         layout.setContentsMargins(24, 15, 24, 15)
        
#         # Titre
#         title_block = QVBoxLayout()
#         title_block.setSpacing(2)
        
#         title = QLabel("Nouveau Sinistre")
#         title.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a; background: transparent;")
#         title_block.addWidget(title)
        
#         subtitle = QLabel("Déclaration d'un événement dommageable")
#         subtitle.setStyleSheet("font-size: 12px; color: #64748b; background: transparent;")
#         title_block.addWidget(subtitle)
        
#         layout.addLayout(title_block)
#         layout.addStretch()
        
#         # Stepper
#         steps_layout = QHBoxLayout()
#         steps_layout.setSpacing(8)
        
#         self.step_badges = []
#         for step in ["1. Client", "2. Contrat", "3. Détails", "4. Validation"]:
#             badge = QLabel(step)
#             badge.setStyleSheet(STYLE_STEP_BADGE_INACTIVE)
#             steps_layout.addWidget(badge)
#             self.step_badges.append(badge)
        
#         layout.addLayout(steps_layout)
        
#         return header
    
#     def _build_form_column(self) -> QWidget:
#         """Colonne principale avec les cartes"""
#         scroll = QScrollArea()
#         scroll.setWidgetResizable(True)
#         scroll.setStyleSheet("""
#             QScrollArea { border: none; background: transparent; }
#             QScrollBar:vertical {
#                 background: transparent; width: 8px; margin: 0;
#             }
#             QScrollBar::handle:vertical {
#                 background: #cbd5e1; border-radius: 4px; min-height: 30px;
#             }
#             QScrollBar::handle:vertical:hover { background: #94a3b8; }
#             QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
#         """)
        
#         content = QWidget()
#         content.setStyleSheet("background: transparent;")
#         layout = QVBoxLayout(content)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(16)
        
#         layout.addWidget(self._card_client_contrat())
#         layout.addWidget(self._card_infos_generales())
#         layout.addWidget(self._card_classification())
#         layout.addWidget(self._card_circonstances())
#         layout.addWidget(self._card_dates())
#         layout.addWidget(self._card_description())
        
#         layout.addStretch()
#         scroll.setWidget(content)
#         return scroll
    
#     # ═══════════════════════════════════════════════════════════════
#     # CARTES
#     # ═══════════════════════════════════════════════════════════════
    
#     def _card_client_contrat(self) -> Card:
#         from addons.sinistres.views.client_search_widget import ClientSearchWidget
#         from addons.sinistres.views.contract_selector_widget import ContractSelectorWidget
        
#         card = Card("👥", "Client et contrat")
        
#         # Badge état
#         self.badge_client = Badge("⏳ En attente", success=False)
#         card.layout.insertWidget(0, self.badge_client, alignment=Qt.AlignRight)
        
#         # Widgets spécialisés
#         self.client_search = ClientSearchWidget(self.automobile_controller)
#         self.client_search.client_selected.connect(self._on_client_selected)
#         card.content.addWidget(self.client_search)
        
#         self.contract_selector = ContractSelectorWidget(self.automobile_controller)
#         self.contract_selector.contract_selected.connect(self._on_contract_selected)
#         self.contract_selector.vehicle_selected.connect(self._on_vehicle_selected)
#         card.content.addWidget(self.contract_selector)
        
#         # Bandeau flotte
#         self.flotte_banner = QFrame()
#         self.flotte_banner.setStyleSheet(STYLE_FLOTTE_BANNER)
#         self.flotte_banner.hide()
#         flotte_layout = QVBoxLayout(self.flotte_banner)
#         flotte_layout.setContentsMargins(12, 8, 12, 8)
        
#         self.lbl_flotte_info = QLabel("🚛 Contrat flotte détecté — Sélectionnez le véhicule sinistré")
#         flotte_layout.addWidget(self.lbl_flotte_info)
        
#         card.content.addWidget(self.flotte_banner)
        
#         return card
    
#     def _card_infos_generales(self) -> Card:
#         card = Card("📋", "Informations générales")
        
#         self.input_numero_ref = QLineEdit()
#         self.input_numero_ref.setPlaceholderText("Ex: REF-2026-001")
#         self.input_numero_ref.setStyleSheet(STYLE_INPUT)
#         card.add_row("Référence", self.input_numero_ref)
        
#         self.input_compagnie = QLineEdit()
#         self.input_compagnie.setPlaceholderText("ID compagnie (optionnel)")
#         self.input_compagnie.setStyleSheet(STYLE_INPUT)
#         card.add_row("Compagnie", self.input_compagnie)
        
#         self.input_agence = QLineEdit()
#         self.input_agence.setPlaceholderText("ID agence (optionnel)")
#         self.input_agence.setStyleSheet(STYLE_INPUT)
#         card.add_row("Agence", self.input_agence)
        
#         return card
    
#     def _card_classification(self) -> Card:
#         card = Card("🏷️", "Classification")
        
#         self.input_branche = QComboBox()
#         self.input_branche.setStyleSheet(STYLE_REQUIRED)
#         self.input_branche.currentIndexChanged.connect(self._on_branche_changed)
#         card.add_row("Branche", self.input_branche, required=True)
        
#         self.input_categorie = QLineEdit()
#         self.input_categorie.setPlaceholderText("Ex: Collision, Incendie, Vol...")
#         self.input_categorie.setStyleSheet(STYLE_REQUIRED)
#         self.input_categorie.textChanged.connect(self._update_summary)
#         card.add_row("Catégorie", self.input_categorie, required=True)
        
#         self.input_sous_categorie = QLineEdit()
#         self.input_sous_categorie.setPlaceholderText("Ex: Véhicule, Bâtiment...")
#         self.input_sous_categorie.setStyleSheet(STYLE_INPUT)
#         card.add_row("Sous-catégorie", self.input_sous_categorie)
        
#         return card
    
#     def _card_circonstances(self) -> Card:
#         card = Card("⚠️", "Circonstances et responsabilité")
        
#         self.input_circonstance = QComboBox()
#         self.input_circonstance.setStyleSheet(STYLE_REQUIRED)
#         self.input_circonstance.currentIndexChanged.connect(self._update_summary)
#         card.add_row("Circonstance principale", self.input_circonstance, required=True)
        
#         self.input_circonstance_secondaire = QComboBox()
#         self.input_circonstance_secondaire.addItem("-- Aucune --", None)
#         self.input_circonstance_secondaire.setStyleSheet(STYLE_INPUT)
#         card.add_row("Circonstance secondaire", self.input_circonstance_secondaire)
        
#         self.input_responsabilite = QComboBox()
#         self.input_responsabilite.setStyleSheet(STYLE_REQUIRED)
#         self.input_responsabilite.currentIndexChanged.connect(self._update_summary)
#         card.add_row("Responsabilité", self.input_responsabilite, required=True)
        
#         return card
    
#     def _card_dates(self) -> Card:
#         card = Card("📅", "Dates")
        
#         self.input_date_survenance = QDateEdit()
#         self.input_date_survenance.setDate(QDate.currentDate())
#         self.input_date_survenance.setCalendarPopup(True)
#         self.input_date_survenance.setStyleSheet(STYLE_REQUIRED)
#         self.input_date_survenance.dateChanged.connect(self._validate_dates)
#         card.add_row("Date de survenance", self.input_date_survenance, required=True)
        
#         self.input_date_declaration = QDateEdit()
#         self.input_date_declaration.setDate(QDate.currentDate())
#         self.input_date_declaration.setCalendarPopup(True)
#         self.input_date_declaration.setStyleSheet(STYLE_REQUIRED)
#         self.input_date_declaration.dateChanged.connect(self._validate_dates)
#         card.add_row("Date de déclaration", self.input_date_declaration, required=True)
        
#         # Message d'aide
#         self.lbl_date_warning = QLabel("")
#         self.lbl_date_warning.setStyleSheet("color: #dc2626; font-size: 11px; font-weight: bold; background: transparent;")
#         card.content.addWidget(self.lbl_date_warning)
        
#         # Info
#         info = QLabel("ℹ️ La date d'ouverture sera générée automatiquement")
#         info.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic; background: transparent;")
#         card.content.addWidget(info)
        
#         return card
    
#     def _card_description(self) -> Card:
#         card = Card("📝", "Description")
        
#         self.input_description = QTextEdit()
#         self.input_description.setPlaceholderText("Décrivez les circonstances détaillées du sinistre...")
#         self.input_description.setMaximumHeight(120)
#         self.input_description.setStyleSheet(STYLE_INPUT)
#         self.input_description.textChanged.connect(self._update_char_count)
#         card.content.addWidget(self.input_description)
        
#         # Compteur de caractères
#         self.lbl_char_count = QLabel("0 / 2000 caractères")
#         self.lbl_char_count.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent;")
#         self.lbl_char_count.setAlignment(Qt.AlignRight)
#         card.content.addWidget(self.lbl_char_count)
        
#         return card
    
#     # ═══════════════════════════════════════════════════════════════
#     # PANNEAU RÉSUMÉ
#     # ═══════════════════════════════════════════════════════════════
    
#     def _build_summary_column(self) -> QWidget:
#         container = QWidget()
#         container.setStyleSheet("background: transparent;")
#         layout = QVBoxLayout(container)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(15)
        
#         # Carte résumé
#         summary = QFrame()
#         summary.setObjectName("SummaryCard")
#         summary.setStyleSheet(STYLE_SUMMARY_CARD)
        
#         s_layout = QVBoxLayout(summary)
#         s_layout.setContentsMargins(18, 18, 18, 18)
#         s_layout.setSpacing(15)
        
#         # Titre
#         title = QLabel("📋 Récapitulatif")
#         title.setStyleSheet("font-size: 14px; font-weight: 700; color: #0f172a; background: transparent;")
#         s_layout.addWidget(title)
        
#         sep = QFrame()
#         sep.setFrameShape(QFrame.HLine)
#         sep.setStyleSheet("background-color: #e2e8f0; max-height: 1px; border: none;")
#         s_layout.addWidget(sep)
        
#         # Sections du résumé
#         self.summary_client = self._summary_block("👤 CLIENT", "Non sélectionné", s_layout)
#         self.summary_contrat = self._summary_block("📄 CONTRAT", "Non sélectionné", s_layout)
#         self.summary_vehicule = self._summary_block("🚗 VÉHICULE", "—", s_layout)
#         self.summary_branche = self._summary_block("🏷️ BRANCHE", "—", s_layout)
#         self.summary_dates = self._summary_block("📅 DATES", "—", s_layout)
        
#         s_layout.addStretch()
        
#         # Barre de progression
#         progress_frame = QFrame()
#         progress_frame.setStyleSheet("""
#             QFrame {
#                 background: white;
#                 border-radius: 8px;
#                 border: 1px solid #e2e8f0;
#             }
#         """)
#         p_layout = QVBoxLayout(progress_frame)
#         p_layout.setContentsMargins(12, 10, 12, 10)
#         p_layout.setSpacing(6)
        
#         p_top = QHBoxLayout()
#         p_title = QLabel("Complétion")
#         p_title.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 700; background: transparent;")
#         p_top.addWidget(p_title)
#         p_top.addStretch()
        
#         self.lbl_completion = QLabel("0%")
#         self.lbl_completion.setStyleSheet("font-size: 14px; font-weight: 800; color: #2563eb; background: transparent;")
#         p_top.addWidget(self.lbl_completion)
        
#         p_layout.addLayout(p_top)
        
#         # Progress bar
#         self.progress_bar = QProgressBar()
#         self.progress_bar.setRange(0, 100)
#         self.progress_bar.setValue(0)
#         self.progress_bar.setTextVisible(False)
#         self.progress_bar.setFixedHeight(6)
#         self.progress_bar.setStyleSheet("""
#             QProgressBar {
#                 background: #f1f5f9;
#                 border: none;
#                 border-radius: 3px;
#             }
#             QProgressBar::chunk {
#                 background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
#                     stop:0 #2563eb, stop:1 #3b82f6);
#                 border-radius: 3px;
#             }
#         """)
#         p_layout.addWidget(self.progress_bar)
        
#         s_layout.addWidget(progress_frame)
        
#         layout.addWidget(summary)
#         layout.addStretch()
        
#         return container
    
#     def _summary_block(self, label: str, value: str, parent_layout) -> QLabel:
#         """Crée un bloc de résumé (label + valeur)"""
#         block = QVBoxLayout()
#         block.setSpacing(2)
        
#         lbl = QLabel(label)
#         lbl.setStyleSheet("""
#             font-size: 10px;
#             color: #94a3b8;
#             font-weight: 700;
#             background: transparent;
#             letter-spacing: 0.5px;
#         """)
#         block.addWidget(lbl)
        
#         val = QLabel(value)
#         val.setStyleSheet("font-size: 12px; color: #0f172a; font-weight: 600; background: transparent;")
#         val.setWordWrap(True)
#         block.addWidget(val)
        
#         parent_layout.addLayout(block)
#         return val
    
#     # ═══════════════════════════════════════════════════════════════
#     # PIED (boutons fixes)
#     # ═══════════════════════════════════════════════════════════════
    
#     def _build_footer(self) -> QWidget:
#         footer = QFrame()
#         footer.setStyleSheet("""
#             QFrame {
#                 background-color: white;
#                 border-top: 1px solid #e2e8f0;
#             }
#         """)
#         footer.setFixedHeight(75)
        
#         layout = QHBoxLayout(footer)
#         layout.setContentsMargins(24, 15, 24, 15)
        
#         # Statut
#         self.lbl_footer_status = QLabel("📌 Les champs marqués * sont obligatoires")
#         self.lbl_footer_status.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
#         layout.addWidget(self.lbl_footer_status)
        
#         layout.addStretch()
        
#         # Bouton annuler
#         self.btn_annuler = QPushButton("Annuler")
#         self.btn_annuler.setCursor(Qt.PointingHandCursor)
#         self.btn_annuler.setStyleSheet(STYLE_BTN_SECONDARY)
#         self.btn_annuler.clicked.connect(self.clear_form)
#         layout.addWidget(self.btn_annuler)
        
#         # Bouton créer
#         self.btn_creer = QPushButton("✅  Créer le sinistre")
#         self.btn_creer.setCursor(Qt.PointingHandCursor)
#         self.btn_creer.setStyleSheet(STYLE_BTN_PRIMARY)
#         self.btn_creer.setMinimumWidth(200)
#         self.btn_creer.clicked.connect(self.creer_sinistre)
#         layout.addWidget(self.btn_creer)
        
#         return footer
    
#     # ═══════════════════════════════════════════════════════════════
#     # LOGIQUE MÉTIER
#     # ═══════════════════════════════════════════════════════════════
    
#     def _connect_validators(self):
#         """Connecte les validateurs"""
#         pass
    
#     def _on_client_selected(self, client: dict):
#         """Client sélectionné"""
#         client_id = client.get('id')
#         if client_id:
#             self.contract_selector.set_client(client_id)
#             self._vehicule_sinistre = None
            
#             nom = f"{client.get('nom', '')} {client.get('prenom', '')}".strip()
#             code = client.get('code_client', '')
#             self.summary_client.setText(f"{nom}\n{code}" if code else nom)
            
#             self.badge_client.setText("✅ Client OK")
#             self.badge_client.setStyleSheet(STYLE_BADGE_SUCCESS)
            
#             self._update_completion()
    
#     def _on_contract_selected(self, contract: dict):
#         """Contrat sélectionné"""
#         self._vehicule_sinistre = None
        
#         police = contract.get('numero_police', 'N/A')
#         statut = contract.get('statut', 'N/A')
#         self.summary_contrat.setText(f"{police}\n{str(statut).upper()}")
        
#         # Détection flotte
#         try:
#             is_flotte = self.contract_selector._is_flotte(contract)
#         except Exception:
#             is_flotte = False
        
#         if is_flotte:
#             self.flotte_banner.show()
#             self.summary_vehicule.setText("Sélection requise")
#         else:
#             self.flotte_banner.hide()
#             self.summary_vehicule.setText("—")
        
#         self._update_summary()
#         self._update_completion()
    
#     def _on_vehicle_selected(self, vehicule: dict):
#         """Véhicule sélectionné"""
#         self._vehicule_sinistre = vehicule
#         immat = vehicule.get('immatriculation', 'N/A')
#         marque = vehicule.get('marque', '') or ''
#         modele = vehicule.get('modele', '') or ''
#         detail = f"{marque} {modele}".strip()
#         self.summary_vehicule.setText(f"{immat}\n{detail}" if detail else immat)
#         self._update_completion()
    
#     def _on_branche_changed(self, index: int):
#         """Branche changée"""
#         self._update_summary()
    
#     def _validate_dates(self):
#         """Vérifie la cohérence des dates"""
#         date_surv = self.input_date_survenance.date().toPython()
#         date_decl = self.input_date_declaration.date().toPython()
        
#         if date_decl < date_surv:
#             self.lbl_date_warning.setText("⚠️ La date de déclaration ne peut être antérieure à la date de survenance")
#             self.input_date_declaration.setStyleSheet("""
#                 background-color: #fef2f2;
#                 border: 2px solid #dc2626;
#                 border-radius: 8px;
#                 padding: 8px 12px;
#                 font-size: 13px;
#             """)
#         else:
#             self.lbl_date_warning.setText("")
#             self.input_date_declaration.setStyleSheet(STYLE_REQUIRED)
        
#         self._update_summary()
    
#     def _update_char_count(self):
#         """Met à jour le compteur de caractères"""
#         count = len(self.input_description.toPlainText())
#         self.lbl_char_count.setText(f"{count} / 2000 caractères")
#         if count > 2000:
#             self.lbl_char_count.setStyleSheet("color: #dc2626; font-size: 11px; font-weight: bold; background: transparent;")
#         else:
#             self.lbl_char_count.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent;")
    
#     def _update_summary(self):
#         """Met à jour le résumé"""
#         branche = self.input_branche.currentText()
#         self.summary_branche.setText(branche or "—")
        
#         date_s = self.input_date_survenance.date().toString("dd/MM/yyyy")
#         date_d = self.input_date_declaration.date().toString("dd/MM/yyyy")
#         self.summary_dates.setText(f"Surv. : {date_s}\nDécl. : {date_d}")
        
#         self._update_completion()
    
#     def _update_completion(self):
#         """Calcule le pourcentage de complétion"""
#         checks = [
#             bool(self.client_search.get_selected_client()),
#             bool(self.contract_selector.get_selected_contract()),
#             bool(self.input_branche.currentData()),
#             bool(self.input_categorie.text().strip()),
#             bool(self.input_circonstance.currentData()),
#             bool(self.input_responsabilite.currentData()),
#         ]
        
#         # Véhicule requis si flotte
#         try:
#             contract = self.contract_selector.get_selected_contract()
#             if contract and self.contract_selector._is_flotte(contract):
#                 checks.append(self._vehicule_sinistre is not None)
#         except Exception:
#             pass
        
#         percent = int((sum(checks) / len(checks)) * 100) if checks else 0
#         self.lbl_completion.setText(f"{percent}%")
        
#         # Progress bar
#         self.progress_bar.setValue(percent)
        
#         # Couleur selon avancement
#         if percent >= 100:
#             self.lbl_completion.setStyleSheet("font-size: 14px; font-weight: 800; color: #10b981; background: transparent;")
#         elif percent >= 50:
#             self.lbl_completion.setStyleSheet("font-size: 14px; font-weight: 800; color: #2563eb; background: transparent;")
#         else:
#             self.lbl_completion.setStyleSheet("font-size: 14px; font-weight: 800; color: #f59e0b; background: transparent;")
        
#         # Badges étapes
#         self._update_step_badges(percent)
    
#     def _update_step_badges(self, percent: int):
#         """Met à jour les badges d'étapes"""
#         active_count = 0
#         if self.client_search.get_selected_client():
#             active_count = 1
#         if self.contract_selector.get_selected_contract():
#             active_count = 2
#         if self.input_categorie.text().strip():
#             active_count = 3
#         if percent >= 100:
#             active_count = 4
        
#         for i, badge in enumerate(self.step_badges):
#             if i < active_count:
#                 badge.setStyleSheet(STYLE_STEP_BADGE_ACTIVE)
#             else:
#                 badge.setStyleSheet(STYLE_STEP_BADGE_INACTIVE)
    
#     # ═══════════════════════════════════════════════════════════════
#     # CHARGEMENT RÉFÉRENTIELS
#     # ═══════════════════════════════════════════════════════════════
    
#     def load_referentiels(self):
#         """Charge les référentiels"""
#         try:
#             # Branches
#             branches = self.referentiel_controller.get_referentiels_by_famille("branches")
#             self._branches_cache = {}
#             self.input_branche.blockSignals(True)
#             self.input_branche.clear()
#             self.input_branche.addItem("-- Sélectionner --", None)
#             for b in branches:
#                 self.input_branche.addItem(b.get('libelle', ''), b.get('code', ''))
#                 self._branches_cache[b.get('code', '')] = b
#             self.input_branche.blockSignals(False)
            
#             # Circonstances
#             circonstances = self.referentiel_controller.get_referentiels_by_famille("circonstances")
#             self._circonstances_cache = {}
#             self.input_circonstance.blockSignals(True)
#             self.input_circonstance_secondaire.blockSignals(True)
#             self.input_circonstance.clear()
#             self.input_circonstance_secondaire.clear()
#             self.input_circonstance.addItem("-- Sélectionner --", None)
#             self.input_circonstance_secondaire.addItem("-- Aucune --", None)
#             for c in circonstances:
#                 label = c.get('libelle', '')
#                 code = c.get('code', '')
#                 self.input_circonstance.addItem(label, code)
#                 self.input_circonstance_secondaire.addItem(label, code)
#                 self._circonstances_cache[code] = c
#             self.input_circonstance.blockSignals(False)
#             self.input_circonstance_secondaire.blockSignals(False)
            
#             # Responsabilités
#             responsabilites = self.referentiel_controller.get_referentiels_by_famille("responsabilites")
#             self._responsabilites_cache = {}
#             self.input_responsabilite.blockSignals(True)
#             self.input_responsabilite.clear()
#             self.input_responsabilite.addItem("-- Sélectionner --", None)
#             for r in responsabilites:
#                 label = f"{r.get('libelle', '')} ({int(r.get('valeur', 0) * 100)}%)"
#                 code = r.get('code', '')
#                 self.input_responsabilite.addItem(label, code)
#                 self._responsabilites_cache[code] = r
#             self.input_responsabilite.blockSignals(False)
            
#         except Exception as e:
#             print(f"Erreur chargement référentiels: {e}")
#             import traceback
#             traceback.print_exc()
    
#     # ═══════════════════════════════════════════════════════════════
#     # CRÉATION
#     # ═══════════════════════════════════════════════════════════════
    
#     def creer_sinistre(self):
#         """Crée le sinistre"""
#         try:
#             client = self.client_search.get_selected_client()
#             contract = self.contract_selector.get_selected_contract()
            
#             # Validations
#             if not client:
#                 self._show_error("Veuillez sélectionner un client")
#                 return
#             if not contract:
#                 self._show_error("Veuillez sélectionner un contrat")
#                 return
            
#             categorie = self.input_categorie.text().strip()
#             if not categorie:
#                 self._show_error("Veuillez saisir une catégorie")
#                 return
            
#             if not self.input_branche.currentData():
#                 self._show_error("Veuillez sélectionner une branche")
#                 return
            
#             if not self.input_circonstance.currentData():
#                 self._show_error("Veuillez sélectionner une circonstance")
#                 return
            
#             if not self.input_responsabilite.currentData():
#                 self._show_error("Veuillez sélectionner une responsabilité")
#                 return
            
#             # Vérifier flotte
#             try:
#                 est_flotte = self.contract_selector._is_flotte(contract)
#             except Exception:
#                 est_flotte = False
            
#             if est_flotte and not self._vehicule_sinistre:
#                 self._show_error("Ce contrat est une flotte. Sélectionnez le véhicule sinistré.")
#                 return
            
#             # Vérifier dates
#             date_surv = self.input_date_survenance.date().toPython()
#             date_decl = self.input_date_declaration.date().toPython()
#             if date_decl < date_surv:
#                 self._show_error("La date de déclaration ne peut être antérieure à la date de survenance")
#                 return
            
#             # Construire les données
#             data = {
#                 'client_id': client.get('id'),
#                 'contrat_id': contract.get('id'),
#                 'numero_reference': self.input_numero_ref.text().strip() or None,
#                 'compagnie_id': int(self.input_compagnie.text()) if self.input_compagnie.text().strip().isdigit() else None,
#                 'agence_id': int(self.input_agence.text()) if self.input_agence.text().strip().isdigit() else None,
#                 'branche': self.input_branche.currentData(),
#                 'categorie': categorie,
#                 'sous_categorie': self.input_sous_categorie.text().strip() or None,
#                 'circonstance_principale': self.input_circonstance.currentData(),
#                 'circonstance_secondaire': self.input_circonstance_secondaire.currentData(),
#                 'taux_responsabilite': self._get_responsabilite_taux(),
#                 'date_survenance': date_surv,
#                 'date_declaration': date_decl,
#                 'description': self.input_description.toPlainText().strip() or None,
#                 'est_flotte': est_flotte,
#                 'vehicule_sinistre_id': self.contract_selector.get_selected_vehicle_id(),
#                 'created_by': self.user.id if self.user else None,
#             }
            
#             result = self.sinistre_controller.creer_sinistre(data)
            
#             if result:
#                 numero = result.get('numero_sinistre', 'N/A')
                
#                 # Notification succès
#                 QMessageBox.information(
#                     self,
#                     "✅ Sinistre créé",
#                     f"<b>Sinistre {numero}</b> créé avec succès !\n\n"
#                     f"👤 <b>Client :</b> {client.get('nom', '')} {client.get('prenom', '')}\n"
#                     f"📄 <b>Contrat :</b> {contract.get('numero_police', 'N/A')}\n"
#                     f"📅 <b>Survenance :</b> {date_surv.strftime('%d/%m/%Y')}\n"
#                     f"📌 <b>Statut :</b> OUVERT"
#                 )
                
#                 # Émettre le signal
#                 self.sinistre_created.emit(result)
                
#                 # Reset
#                 self.clear_form()
#                 self.lbl_footer_status.setText("✅ Sinistre créé — formulaire réinitialisé")
#                 self.lbl_footer_status.setStyleSheet("color: #10b981; font-size: 12px; font-weight: 600; background: transparent;")
#                 QTimer.singleShot(4000, lambda: self.lbl_footer_status.setStyleSheet(
#                     "color: #64748b; font-size: 12px; background: transparent;"
#                 ))
        
#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             QMessageBox.critical(self, "Erreur", f"Erreur lors de la création : {str(e)}")
    
#     def _get_responsabilite_taux(self) -> float:
#         """Récupère le taux de responsabilité"""
#         code = self.input_responsabilite.currentData()
#         ref = self._responsabilites_cache.get(code)
#         if ref:
#             return float(ref.get('valeur', 0))
#         return 0.0
    
#     def _show_error(self, message: str):
#         """Affiche une erreur dans la barre de statut + message box"""
#         self.lbl_footer_status.setText(f"⚠️ {message}")
#         self.lbl_footer_status.setStyleSheet("color: #dc2626; font-size: 12px; font-weight: 700; background: transparent;")
#         QMessageBox.warning(self, "Validation", message)
        
#         QTimer.singleShot(5000, lambda: self.lbl_footer_status.setStyleSheet(
#             "color: #64748b; font-size: 12px; background: transparent;"
#         ))
    
#     def clear_form(self):
#         """Réinitialise le formulaire"""
#         try:
#             self.client_search.clear_selection()
#         except Exception:
#             pass
        
#         try:
#             self.contract_selector.clear_selection()
#         except Exception:
#             pass
        
#         self.input_numero_ref.clear()
#         self.input_compagnie.clear()
#         self.input_agence.clear()
#         self.input_branche.setCurrentIndex(0)
#         self.input_categorie.clear()
#         self.input_sous_categorie.clear()
#         self.input_circonstance.setCurrentIndex(0)
#         self.input_circonstance_secondaire.setCurrentIndex(0)
#         self.input_responsabilite.setCurrentIndex(0)
#         self.input_date_survenance.setDate(QDate.currentDate())
#         self.input_date_declaration.setDate(QDate.currentDate())
#         self.input_description.clear()
        
#         self._vehicule_sinistre = None
#         self.flotte_banner.hide()
        
#         self.summary_client.setText("Non sélectionné")
#         self.summary_contrat.setText("Non sélectionné")
#         self.summary_vehicule.setText("—")
#         self.summary_branche.setText("—")
#         self.summary_dates.setText("—")
        
#         self.badge_client.setText("⏳ En attente")
#         self.badge_client.setStyleSheet(STYLE_BADGE_ERROR)
        
#         self._update_completion()



"""
Formulaire de création de sinistre - Version professionnelle v2.0
Design moderne avec icônes FontAwesome
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox,
    QFormLayout, QGroupBox, QFrame, QMessageBox, QScrollArea,
    QGraphicsDropShadowEffect, QGridLayout, QSizePolicy, QSpacerItem,
    QProgressBar, QMenu
)
from PySide6.QtCore import Qt, Signal, QDate, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont, QIcon, QPixmap, QPainter, QBrush, QPen, QAction

import qtawesome as qta

from datetime import datetime, timedelta


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def _safe_bool(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() not in ('', 'none', 'null', '0', 'false')
    return bool(value)


def make_icon_label(icon_name: str, color: str = "#1a73e8", size: int = 20) -> QLabel:
    """Crée un QLabel contenant une icône FontAwesome"""
    lbl = QLabel()
    try:
        icon = qta.icon(icon_name, color=color)
        lbl.setPixmap(icon.pixmap(QSize(size, size)))
    except Exception as e:
        print(f"⚠️ Icône '{icon_name}' introuvable : {e}")
        lbl.setText("●")
        lbl.setStyleSheet(f"color: {color}; font-size: {size}px;")
    
    lbl.setFixedSize(size + 4, size + 4)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(lbl.styleSheet() + "background: transparent;")
    return lbl


# ═══════════════════════════════════════════════════════════════════
# STYLES CONSTANTS
# ═══════════════════════════════════════════════════════════════════

STYLE_CARD = """
    QFrame#Card {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }
"""

STYLE_INPUT = """
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: #1e293b;
        min-height: 20px;
    }
    QLineEdit:hover, QComboBox:hover, QDateEdit:hover,
    QTextEdit:hover, QDoubleSpinBox:hover {
        border-color: #cbd5e1;
    }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
    QTextEdit:focus, QDoubleSpinBox:focus {
        border: 2px solid #3b82f6;
        background-color: white;
    }
    QLineEdit:disabled, QComboBox:disabled {
        background-color: #f1f5f9;
        color: #94a3b8;
    }
    QComboBox::drop-down { border: none; width: 24px; }
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #64748b;
        margin-right: 8px;
    }
"""

STYLE_REQUIRED = """
    QLineEdit, QComboBox, QDateEdit, QTextEdit {
        background-color: #fffbeb;
        border: 1px solid #fde047;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: #1e293b;
        min-height: 20px;
    }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
        border: 2px solid #3b82f6;
        background-color: white;
    }
"""

STYLE_BADGE_SUCCESS = """
    QLabel {
        background-color: #d1fae5;
        color: #065f46;
        padding: 4px 10px;
        border-radius: 11px;
        font-size: 11px;
        font-weight: 700;
    }
"""

STYLE_BADGE_ERROR = """
    QLabel {
        background-color: #fed7aa;
        color: #9a3412;
        padding: 4px 10px;
        border-radius: 11px;
        font-size: 11px;
        font-weight: 700;
    }
"""

STYLE_FLOTTE_BANNER = """
    QFrame {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 10px;
    }
    QLabel {
        color: #1e40af;
        font-size: 12px;
        font-weight: 600;
        background: transparent;
    }
"""

STYLE_BTN_PRIMARY = """
    QPushButton {
        background-color: #2563eb;
        color: white;
        padding: 10px 28px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
        border: none;
    }
    QPushButton:hover { background-color: #1d4ed8; }
    QPushButton:pressed { background-color: #1e40af; }
    QPushButton:disabled {
        background-color: #cbd5e1;
        color: #94a3b8;
    }
"""

STYLE_BTN_SECONDARY = """
    QPushButton {
        background-color: white;
        color: #64748b;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
        border: 1px solid #e2e8f0;
    }
    QPushButton:hover {
        background-color: #f8fafc;
        border-color: #cbd5e1;
        color: #1e293b;
    }
"""

STYLE_SUMMARY_CARD = """
    QFrame#SummaryCard {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }
"""

STYLE_STEP_BADGE_ACTIVE = """
    QLabel {
        background-color: #2563eb;
        color: white;
        border-radius: 12px;
        padding: 4px 14px;
        font-size: 11px;
        font-weight: 700;
    }
"""

STYLE_STEP_BADGE_INACTIVE = """
    QLabel {
        background-color: #f1f5f9;
        color: #94a3b8;
        border-radius: 12px;
        padding: 4px 14px;
        font-size: 11px;
        font-weight: 600;
    }
"""


# ═══════════════════════════════════════════════════════════════════
# WIDGETS PERSONNALISÉS
# ═══════════════════════════════════════════════════════════════════

class Card(QFrame):
    """Carte avec icône FontAwesome + titre"""
    
    def __init__(self, icon_name: str, title: str, icon_color: str = "#1a73e8", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setStyleSheet(STYLE_CARD)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 16, 20, 18)
        self.layout.setSpacing(14)
        
        # ─── Header : Icône + Titre ───
        header = QHBoxLayout()
        header.setSpacing(10)
        
        # ✅ Icône FontAwesome (au lieu d'emoji)
        icon_lbl = make_icon_label(icon_name, color=icon_color, size=18)
        header.addWidget(icon_lbl)
        
        # Titre
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #0f172a;
            background: transparent;
        """)
        header.addWidget(title_lbl)
        header.addStretch()
        
        self.layout.addLayout(header)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #f1f5f9; max-height: 1px; border: none;")
        self.layout.addWidget(sep)
        
        # Zone de contenu
        self.content = QVBoxLayout()
        self.content.setSpacing(12)
        self.layout.addLayout(self.content)
    
    def add_row(self, label: str, widget: QWidget, required: bool = False):
        """Ajoute une ligne label + widget"""
        row = QHBoxLayout()
        row.setSpacing(15)
        
        lbl = QLabel(label + (" *" if required else ""))
        lbl.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {'#1e293b' if required else '#475569'};
            background: transparent;
            min-width: 140px;
        """)
        row.addWidget(lbl)
        row.addWidget(widget, 1)
        self.content.addLayout(row)
        return lbl


class Badge(QLabel):
    """Badge coloré avec icône FontAwesome optionnelle"""
    
    def __init__(self, text: str, success: bool = True, icon_name: str = None, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet(STYLE_BADGE_SUCCESS if success else STYLE_BADGE_ERROR)
        self.setAlignment(Qt.AlignCenter)
        
        if icon_name:
            try:
                icon = qta.icon(icon_name, color='#065f46' if success else '#9a3412')
                self.setPixmap(icon.pixmap(QSize(12, 12)))
                # Utiliser un layout pour icône + texte
                # (ici, on simplifie en mettant juste le texte + icône via HTML)
                self.setText(f" {text}")
            except Exception:
                self.setText(text)
        else:
            self.setText(text)


# ═══════════════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════

class NouveauSinistrePage(QWidget):
    """Formulaire de création de sinistre — Design moderne v2.0"""
    
    sinistre_created = Signal(dict)
    
    def __init__(self, sinistre_controller, referentiel_controller, user):
        super().__init__()
        self.sinistre_controller = sinistre_controller
        self.referentiel_controller = referentiel_controller
        self.user = user
        
        # Permissions
        from addons.sinistres.services.permission_service import PermissionService
        from addons.sinistres.security.permissions_helper import PermissionsUI
        self.permission_service = PermissionService()
        self.permissions_ui = PermissionsUI(user, self.permission_service)
        
        from addons.sinistres.controllers.automobile_controller import AutomobileController
        self.automobile_controller = AutomobileController()
        self.automobile_controller.set_current_user(user)
        
        self._vehicule_sinistre = None
        self._branches_cache = {}
        self._circonstances_cache = {}
        self._responsabilites_cache = {}
        
        self.setup_ui()
        self.load_referentiels()
        self._connect_validators()
        
        # Vérifier la permission CREATE sinistre
        if not self.permissions_ui.peut('sinistre', 'CREATE'):
            self.btn_creer.setEnabled(False)
            self.btn_creer.setText("  Non autorisé")
            self.btn_creer.setIcon(qta.icon('fa5s.ban', color='#94a3b8'))
            self.btn_creer.setToolTip("Vous n'avez pas la permission de créer un sinistre")
    
    # ═══════════════════════════════════════════════════════════════
    # UI PRINCIPALE
    # ═══════════════════════════════════════════════════════════════
    
    def setup_ui(self):
        self.setStyleSheet("background: #f1f5f9;")
        
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        root.addWidget(self._build_header())
        
        body = QHBoxLayout()
        body.setContentsMargins(24, 20, 24, 20)
        body.setSpacing(20)
        
        body.addWidget(self._build_form_column(), 3)
        body.addWidget(self._build_summary_column(), 1)
        
        root.addLayout(body, 1)
        root.addWidget(self._build_footer())
    
    def _build_header(self) -> QWidget:
        """En-tête avec titre et stepper"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #e2e8f0;
                border-radius: 0;
            }
        """)
        header.setFixedHeight(90)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 15, 24, 15)
        
        # ─── Titre avec icône FontAwesome ───
        title_block = QHBoxLayout()
        title_block.setSpacing(14)
        
        # ✅ Icône FontAwesome à la place de 📝
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet("""
            QFrame {
                background: #eff6ff;
                border-radius: 12px;
                border: 1px solid #dbeafe;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon('fa5s.file-medical', color='#2563eb').pixmap(QSize(24, 24)))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_lbl)
        
        title_block.addWidget(icon_container)
        
        # Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Nouveau Sinistre")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a; background: transparent;")
        text_layout.addWidget(title)
        
        subtitle = QLabel("Déclaration d'un événement dommageable")
        subtitle.setStyleSheet("font-size: 12px; color: #64748b; background: transparent;")
        text_layout.addWidget(subtitle)
        
        title_block.addLayout(text_layout)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        # ─── Stepper ───
        steps_layout = QHBoxLayout()
        steps_layout.setSpacing(8)
        
        self.step_badges = []
        for step in ["1. Client", "2. Contrat", "3. Détails", "4. Validation"]:
            badge = QLabel(step)
            badge.setStyleSheet(STYLE_STEP_BADGE_INACTIVE)
            steps_layout.addWidget(badge)
            self.step_badges.append(badge)
        
        layout.addLayout(steps_layout)
        
        return header
    
    def _build_form_column(self) -> QWidget:
        """Colonne principale avec les cartes"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: transparent; width: 8px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1; border-radius: 4px; min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #94a3b8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        layout.addWidget(self._card_client_contrat())
        layout.addWidget(self._card_infos_generales())
        layout.addWidget(self._card_classification())
        layout.addWidget(self._card_circonstances())
        layout.addWidget(self._card_dates())
        layout.addWidget(self._card_description())
        
        layout.addStretch()
        scroll.setWidget(content)
        return scroll
    
    # ═══════════════════════════════════════════════════════════════
    # CARTES (avec icônes FontAwesome)
    # ═══════════════════════════════════════════════════════════════
    
    def _card_client_contrat(self) -> Card:
        from addons.sinistres.views.client_search_widget import ClientSearchWidget
        from addons.sinistres.views.contract_selector_widget import ContractSelectorWidget
        
        # ✅ Icône utilisateur + contrat
        card = Card("fa5s.users", "Client et contrat", "#3b82f6")
        
        # Badge état
        self.badge_client = Badge("  En attente", success=False)
        self.badge_client.setStyleSheet(STYLE_BADGE_ERROR)
        card.layout.insertWidget(0, self.badge_client, alignment=Qt.AlignRight)
        
        # Widgets spécialisés
        self.client_search = ClientSearchWidget(self.automobile_controller)
        self.client_search.client_selected.connect(self._on_client_selected)
        card.content.addWidget(self.client_search)
        
        self.contract_selector = ContractSelectorWidget(self.automobile_controller)
        self.contract_selector.contract_selected.connect(self._on_contract_selected)
        self.contract_selector.vehicle_selected.connect(self._on_vehicle_selected)
        card.content.addWidget(self.contract_selector)
        
        # Bandeau flotte
        self.flotte_banner = QFrame()
        self.flotte_banner.setStyleSheet(STYLE_FLOTTE_BANNER)
        self.flotte_banner.hide()
        flotte_layout = QHBoxLayout(self.flotte_banner)
        flotte_layout.setContentsMargins(12, 8, 12, 8)
        flotte_layout.setSpacing(10)
        
        # ✅ Icône camion
        flotte_icon = QLabel()
        flotte_icon.setPixmap(qta.icon('fa5s.truck', color='#1e40af').pixmap(QSize(16, 16)))
        flotte_layout.addWidget(flotte_icon)
        
        self.lbl_flotte_info = QLabel("Contrat flotte détecté — Sélectionnez le véhicule sinistré")
        flotte_layout.addWidget(self.lbl_flotte_info)
        flotte_layout.addStretch()
        
        card.content.addWidget(self.flotte_banner)
        
        return card
    
    def _card_infos_generales(self) -> Card:
        # ✅ Icône info
        card = Card("fa5s.info-circle", "Informations générales", "#8b5cf6")
        
        self.input_numero_ref = QLineEdit()
        self.input_numero_ref.setPlaceholderText("Ex: REF-2026-001")
        self.input_numero_ref.setStyleSheet(STYLE_INPUT)
        card.add_row("Référence", self.input_numero_ref)
        
        self.input_compagnie = QLineEdit()
        self.input_compagnie.setPlaceholderText("ID compagnie (optionnel)")
        self.input_compagnie.setStyleSheet(STYLE_INPUT)
        card.add_row("Compagnie", self.input_compagnie)
        
        self.input_agence = QLineEdit()
        self.input_agence.setPlaceholderText("ID agence (optionnel)")
        self.input_agence.setStyleSheet(STYLE_INPUT)
        card.add_row("Agence", self.input_agence)
        
        return card
    
    def _card_classification(self) -> Card:
        # ✅ Icône tags
        card = Card("fa5s.tags", "Classification", "#06b6d4")
        
        self.input_branche = QComboBox()
        self.input_branche.setStyleSheet(STYLE_REQUIRED)
        self.input_branche.currentIndexChanged.connect(self._on_branche_changed)
        card.add_row("Branche", self.input_branche, required=True)
        
        self.input_categorie = QLineEdit()
        self.input_categorie.setPlaceholderText("Ex: Collision, Incendie, Vol...")
        self.input_categorie.setStyleSheet(STYLE_REQUIRED)
        self.input_categorie.textChanged.connect(self._update_summary)
        card.add_row("Catégorie", self.input_categorie, required=True)
        
        self.input_sous_categorie = QLineEdit()
        self.input_sous_categorie.setPlaceholderText("Ex: Véhicule, Bâtiment...")
        self.input_sous_categorie.setStyleSheet(STYLE_INPUT)
        card.add_row("Sous-catégorie", self.input_sous_categorie)
        
        return card
    
    def _card_circonstances(self) -> Card:
        # ✅ Icône alerte
        card = Card("fa5s.exclamation-triangle", "Circonstances et responsabilité", "#f59e0b")
        
        self.input_circonstance = QComboBox()
        self.input_circonstance.setStyleSheet(STYLE_REQUIRED)
        self.input_circonstance.currentIndexChanged.connect(self._update_summary)
        card.add_row("Circonstance principale", self.input_circonstance, required=True)
        
        self.input_circonstance_secondaire = QComboBox()
        self.input_circonstance_secondaire.addItem("-- Aucune --", None)
        self.input_circonstance_secondaire.setStyleSheet(STYLE_INPUT)
        card.add_row("Circonstance secondaire", self.input_circonstance_secondaire)
        
        self.input_responsabilite = QComboBox()
        self.input_responsabilite.setStyleSheet(STYLE_REQUIRED)
        self.input_responsabilite.currentIndexChanged.connect(self._update_summary)
        card.add_row("Responsabilité", self.input_responsabilite, required=True)
        
        return card
    
    def _card_dates(self) -> Card:
        # ✅ Icône calendrier
        card = Card("fa5s.calendar-alt", "Dates", "#22c55e")
        
        self.input_date_survenance = QDateEdit()
        self.input_date_survenance.setDate(QDate.currentDate())
        self.input_date_survenance.setCalendarPopup(True)
        self.input_date_survenance.setStyleSheet(STYLE_REQUIRED)
        self.input_date_survenance.dateChanged.connect(self._validate_dates)
        card.add_row("Date de survenance", self.input_date_survenance, required=True)
        
        self.input_date_declaration = QDateEdit()
        self.input_date_declaration.setDate(QDate.currentDate())
        self.input_date_declaration.setCalendarPopup(True)
        self.input_date_declaration.setStyleSheet(STYLE_REQUIRED)
        self.input_date_declaration.dateChanged.connect(self._validate_dates)
        card.add_row("Date de déclaration", self.input_date_declaration, required=True)
        
        # Message d'aide
        self.lbl_date_warning = QLabel("")
        self.lbl_date_warning.setStyleSheet("color: #dc2626; font-size: 11px; font-weight: bold; background: transparent;")
        card.content.addWidget(self.lbl_date_warning)
        
        # Info avec icône
        info_row = QHBoxLayout()
        info_row.setSpacing(6)
        
        info_icon = QLabel()
        info_icon.setPixmap(qta.icon('fa5s.info-circle', color='#64748b').pixmap(QSize(12, 12)))
        info_row.addWidget(info_icon)
        
        info = QLabel("La date d'ouverture sera générée automatiquement")
        info.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic; background: transparent;")
        info_row.addWidget(info)
        info_row.addStretch()
        
        card.content.addLayout(info_row)
        
        return card
    
    def _card_description(self) -> Card:
        # ✅ Icône commentaire
        card = Card("fa5s.comment-alt", "Description", "#64748b")
        
        self.input_description = QTextEdit()
        self.input_description.setPlaceholderText("Décrivez les circonstances détaillées du sinistre...")
        self.input_description.setMaximumHeight(120)
        self.input_description.setStyleSheet(STYLE_INPUT)
        self.input_description.textChanged.connect(self._update_char_count)
        card.content.addWidget(self.input_description)
        
        # Compteur de caractères
        self.lbl_char_count = QLabel("0 / 2000 caractères")
        self.lbl_char_count.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent;")
        self.lbl_char_count.setAlignment(Qt.AlignRight)
        card.content.addWidget(self.lbl_char_count)
        
        return card
    
    # ═══════════════════════════════════════════════════════════════
    # PANNEAU RÉSUMÉ
    # ═══════════════════════════════════════════════════════════════
    
    def _build_summary_column(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Carte résumé
        summary = QFrame()
        summary.setObjectName("SummaryCard")
        summary.setStyleSheet(STYLE_SUMMARY_CARD)
        
        s_layout = QVBoxLayout(summary)
        s_layout.setContentsMargins(18, 18, 18, 18)
        s_layout.setSpacing(15)
        
        # ─── Titre avec icône ───
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('fa5s.clipboard-list', color='#2563eb').pixmap(QSize(16, 16)))
        title_row.addWidget(title_icon)
        
        title = QLabel("Récapitulatif")
        title.setStyleSheet("font-size: 14px; font-weight: 700; color: #0f172a; background: transparent;")
        title_row.addWidget(title)
        title_row.addStretch()
        
        s_layout.addLayout(title_row)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #e2e8f0; max-height: 1px; border: none;")
        s_layout.addWidget(sep)
        
        # Sections du résumé (avec icônes FontAwesome)
        self.summary_client = self._summary_block(
            "fa5s.user", "CLIENT", "Non sélectionné", s_layout, "#3b82f6"
        )
        self.summary_contrat = self._summary_block(
            "fa5s.file-contract", "CONTRAT", "Non sélectionné", s_layout, "#8b5cf6"
        )
        self.summary_vehicule = self._summary_block(
            "fa5s.car", "VÉHICULE", "—", s_layout, "#06b6d4"
        )
        self.summary_branche = self._summary_block(
            "fa5s.tag", "BRANCHE", "—", s_layout, "#f59e0b"
        )
        self.summary_dates = self._summary_block(
            "fa5s.calendar", "DATES", "—", s_layout, "#22c55e"
        )
        
        s_layout.addStretch()
        
        # Barre de progression
        progress_frame = QFrame()
        progress_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
        """)
        p_layout = QVBoxLayout(progress_frame)
        p_layout.setContentsMargins(12, 10, 12, 10)
        p_layout.setSpacing(6)
        
        p_top = QHBoxLayout()
        
        # Icône de progression
        prog_icon = QLabel()
        prog_icon.setPixmap(qta.icon('fa5s.tasks', color='#64748b').pixmap(QSize(12, 12)))
        p_top.addWidget(prog_icon)
        
        p_title = QLabel("Complétion")
        p_title.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 700; background: transparent;")
        p_top.addWidget(p_title)
        p_top.addStretch()
        
        self.lbl_completion = QLabel("0%")
        self.lbl_completion.setStyleSheet("font-size: 14px; font-weight: 800; color: #2563eb; background: transparent;")
        p_top.addWidget(self.lbl_completion)
        
        p_layout.addLayout(p_top)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: #f1f5f9;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #3b82f6);
                border-radius: 3px;
            }
        """)
        p_layout.addWidget(self.progress_bar)
        
        s_layout.addWidget(progress_frame)
        
        layout.addWidget(summary)
        layout.addStretch()
        
        return container
    
    def _summary_block(self, icon_name: str, label: str, value: str, 
                       parent_layout, color: str = "#1a73e8") -> QLabel:
        """Crée un bloc de résumé (icône + label + valeur)"""
        block = QVBoxLayout()
        block.setSpacing(4)
        
        # ─── En-tête : icône + label ───
        header = QHBoxLayout()
        header.setSpacing(6)
        
        icon_lbl = QLabel()
        try:
            icon_lbl.setPixmap(qta.icon(icon_name, color=color).pixmap(QSize(12, 12)))
        except Exception:
            icon_lbl.setText("●")
        header.addWidget(icon_lbl)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"""
            font-size: 10px;
            color: {color};
            font-weight: 700;
            background: transparent;
            letter-spacing: 0.5px;
        """)
        header.addWidget(lbl)
        header.addStretch()
        
        block.addLayout(header)
        
        # ─── Valeur ───
        val = QLabel(value)
        val.setStyleSheet("font-size: 12px; color: #0f172a; font-weight: 600; background: transparent;")
        val.setWordWrap(True)
        block.addWidget(val)
        
        parent_layout.addLayout(block)
        return val
    
    # ═══════════════════════════════════════════════════════════════
    # PIED (boutons avec icônes FontAwesome)
    # ═══════════════════════════════════════════════════════════════
    
    def _build_footer(self) -> QWidget:
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #e2e8f0;
            }
        """)
        footer.setFixedHeight(75)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(24, 15, 24, 15)
        
        # Statut avec icône
        status_row = QHBoxLayout()
        status_row.setSpacing(6)
        
        status_icon = QLabel()
        status_icon.setPixmap(qta.icon('fa5s.asterisk', color='#94a3b8').pixmap(QSize(10, 10)))
        status_row.addWidget(status_icon)
        
        self.lbl_footer_status = QLabel("Les champs marqués * sont obligatoires")
        self.lbl_footer_status.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        status_row.addWidget(self.lbl_footer_status)
        status_row.addStretch()
        
        layout.addLayout(status_row)
        layout.addStretch()
        
        # ✅ Bouton annuler avec icône
        self.btn_annuler = QPushButton("  Annuler")
        self.btn_annuler.setCursor(Qt.PointingHandCursor)
        self.btn_annuler.setIcon(qta.icon('fa5s.times', color='#64748b'))
        self.btn_annuler.setIconSize(QSize(14, 14))
        self.btn_annuler.setStyleSheet(STYLE_BTN_SECONDARY)
        self.btn_annuler.clicked.connect(self.clear_form)
        layout.addWidget(self.btn_annuler)
        
        # ✅ Bouton créer avec icône check
        self.btn_creer = QPushButton("  Créer le sinistre")
        self.btn_creer.setCursor(Qt.PointingHandCursor)
        self.btn_creer.setIcon(qta.icon('fa5s.check-circle', color='white'))
        self.btn_creer.setIconSize(QSize(16, 16))
        self.btn_creer.setStyleSheet(STYLE_BTN_PRIMARY)
        self.btn_creer.setMinimumWidth(200)
        self.btn_creer.clicked.connect(self.creer_sinistre)
        layout.addWidget(self.btn_creer)
        
        return footer
    
    # ═══════════════════════════════════════════════════════════════
    # LOGIQUE MÉTIER (inchangée)
    # ═══════════════════════════════════════════════════════════════
    
    def _connect_validators(self):
        pass
    
    def _on_client_selected(self, client: dict):
        client_id = client.get('id')
        if client_id:
            self.contract_selector.set_client(client_id)
            self._vehicule_sinistre = None
            
            nom = f"{client.get('nom', '')} {client.get('prenom', '')}".strip()
            code = client.get('code_client', '')
            self.summary_client.setText(f"{nom}\n{code}" if code else nom)
            
            self.badge_client.setText("  Client OK")
            self.badge_client.setStyleSheet(STYLE_BADGE_SUCCESS)
            
            self._update_completion()
    
    def _on_contract_selected(self, contract: dict):
        self._vehicule_sinistre = None
        
        police = contract.get('numero_police', 'N/A')
        statut = contract.get('statut', 'N/A')
        self.summary_contrat.setText(f"{police}\n{str(statut).upper()}")
        
        try:
            is_flotte = self.contract_selector._is_flotte(contract)
        except Exception:
            is_flotte = False
        
        if is_flotte:
            self.flotte_banner.show()
            self.summary_vehicule.setText("Sélection requise")
        else:
            self.flotte_banner.hide()
            self.summary_vehicule.setText("—")
        
        self._update_summary()
        self._update_completion()
    
    def _on_vehicle_selected(self, vehicule: dict):
        self._vehicule_sinistre = vehicule
        immat = vehicule.get('immatriculation', 'N/A')
        marque = vehicule.get('marque', '') or ''
        modele = vehicule.get('modele', '') or ''
        detail = f"{marque} {modele}".strip()
        self.summary_vehicule.setText(f"{immat}\n{detail}" if detail else immat)
        self._update_completion()
    
    def _on_branche_changed(self, index: int):
        self._update_summary()
    
    def _validate_dates(self):
        date_surv = self.input_date_survenance.date().toPython()
        date_decl = self.input_date_declaration.date().toPython()
        
        if date_decl < date_surv:
            self.lbl_date_warning.setText("La date de déclaration ne peut être antérieure à la date de survenance")
            self.input_date_declaration.setStyleSheet("""
                background-color: #fef2f2;
                border: 2px solid #dc2626;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            """)
        else:
            self.lbl_date_warning.setText("")
            self.input_date_declaration.setStyleSheet(STYLE_REQUIRED)
        
        self._update_summary()
    
    def _update_char_count(self):
        count = len(self.input_description.toPlainText())
        self.lbl_char_count.setText(f"{count} / 2000 caractères")
        if count > 2000:
            self.lbl_char_count.setStyleSheet("color: #dc2626; font-size: 11px; font-weight: bold; background: transparent;")
        else:
            self.lbl_char_count.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent;")
    
    def _update_summary(self):
        branche = self.input_branche.currentText()
        self.summary_branche.setText(branche or "—")
        
        date_s = self.input_date_survenance.date().toString("dd/MM/yyyy")
        date_d = self.input_date_declaration.date().toString("dd/MM/yyyy")
        self.summary_dates.setText(f"Surv. : {date_s}\nDécl. : {date_d}")
        
        self._update_completion()
    
    def _update_completion(self):
        checks = [
            bool(self.client_search.get_selected_client()),
            bool(self.contract_selector.get_selected_contract()),
            bool(self.input_branche.currentData()),
            bool(self.input_categorie.text().strip()),
            bool(self.input_circonstance.currentData()),
            bool(self.input_responsabilite.currentData()),
        ]
        
        try:
            contract = self.contract_selector.get_selected_contract()
            if contract and self.contract_selector._is_flotte(contract):
                checks.append(self._vehicule_sinistre is not None)
        except Exception:
            pass
        
        percent = int((sum(checks) / len(checks)) * 100) if checks else 0
        self.lbl_completion.setText(f"{percent}%")
        self.progress_bar.setValue(percent)
        
        if percent >= 100:
            self.lbl_completion.setStyleSheet("font-size: 14px; font-weight: 800; color: #10b981; background: transparent;")
        elif percent >= 50:
            self.lbl_completion.setStyleSheet("font-size: 14px; font-weight: 800; color: #2563eb; background: transparent;")
        else:
            self.lbl_completion.setStyleSheet("font-size: 14px; font-weight: 800; color: #f59e0b; background: transparent;")
        
        self._update_step_badges(percent)
    
    def _update_step_badges(self, percent: int):
        active_count = 0
        if self.client_search.get_selected_client():
            active_count = 1
        if self.contract_selector.get_selected_contract():
            active_count = 2
        if self.input_categorie.text().strip():
            active_count = 3
        if percent >= 100:
            active_count = 4
        
        for i, badge in enumerate(self.step_badges):
            if i < active_count:
                badge.setStyleSheet(STYLE_STEP_BADGE_ACTIVE)
            else:
                badge.setStyleSheet(STYLE_STEP_BADGE_INACTIVE)
    
    def load_referentiels(self):
        try:
            branches = self.referentiel_controller.get_referentiels_by_famille("branches")
            self._branches_cache = {}
            self.input_branche.blockSignals(True)
            self.input_branche.clear()
            self.input_branche.addItem("-- Sélectionner --", None)
            for b in branches:
                self.input_branche.addItem(b.get('libelle', ''), b.get('code', ''))
                self._branches_cache[b.get('code', '')] = b
            self.input_branche.blockSignals(False)
            
            circonstances = self.referentiel_controller.get_referentiels_by_famille("circonstances")
            self._circonstances_cache = {}
            self.input_circonstance.blockSignals(True)
            self.input_circonstance_secondaire.blockSignals(True)
            self.input_circonstance.clear()
            self.input_circonstance_secondaire.clear()
            self.input_circonstance.addItem("-- Sélectionner --", None)
            self.input_circonstance_secondaire.addItem("-- Aucune --", None)
            for c in circonstances:
                label = c.get('libelle', '')
                code = c.get('code', '')
                self.input_circonstance.addItem(label, code)
                self.input_circonstance_secondaire.addItem(label, code)
                self._circonstances_cache[code] = c
            self.input_circonstance.blockSignals(False)
            self.input_circonstance_secondaire.blockSignals(False)
            
            responsabilites = self.referentiel_controller.get_referentiels_by_famille("responsabilites")
            self._responsabilites_cache = {}
            self.input_responsabilite.blockSignals(True)
            self.input_responsabilite.clear()
            self.input_responsabilite.addItem("-- Sélectionner --", None)
            for r in responsabilites:
                label = f"{r.get('libelle', '')} ({int(r.get('valeur', 0) * 100)}%)"
                code = r.get('code', '')
                self.input_responsabilite.addItem(label, code)
                self._responsabilites_cache[code] = r
            self.input_responsabilite.blockSignals(False)
            
        except Exception as e:
            print(f"Erreur chargement référentiels: {e}")
            import traceback
            traceback.print_exc()
    
    def creer_sinistre(self):
        try:
            client = self.client_search.get_selected_client()
            contract = self.contract_selector.get_selected_contract()
            
            if not client:
                self._show_error("Veuillez sélectionner un client")
                return
            if not contract:
                self._show_error("Veuillez sélectionner un contrat")
                return
            
            categorie = self.input_categorie.text().strip()
            if not categorie:
                self._show_error("Veuillez saisir une catégorie")
                return
            
            if not self.input_branche.currentData():
                self._show_error("Veuillez sélectionner une branche")
                return
            
            if not self.input_circonstance.currentData():
                self._show_error("Veuillez sélectionner une circonstance")
                return
            
            if not self.input_responsabilite.currentData():
                self._show_error("Veuillez sélectionner une responsabilité")
                return
            
            try:
                est_flotte = self.contract_selector._is_flotte(contract)
            except Exception:
                est_flotte = False
            
            if est_flotte and not self._vehicule_sinistre:
                self._show_error("Ce contrat est une flotte. Sélectionnez le véhicule sinistré.")
                return
            
            date_surv = self.input_date_survenance.date().toPython()
            date_decl = self.input_date_declaration.date().toPython()
            if date_decl < date_surv:
                self._show_error("La date de déclaration ne peut être antérieure à la date de survenance")
                return
            
            data = {
                'client_id': client.get('id'),
                'contrat_id': contract.get('id'),
                'numero_reference': self.input_numero_ref.text().strip() or None,
                'compagnie_id': int(self.input_compagnie.text()) if self.input_compagnie.text().strip().isdigit() else None,
                'agence_id': int(self.input_agence.text()) if self.input_agence.text().strip().isdigit() else None,
                'branche': self.input_branche.currentData(),
                'categorie': categorie,
                'sous_categorie': self.input_sous_categorie.text().strip() or None,
                'circonstance_principale': self.input_circonstance.currentData(),
                'circonstance_secondaire': self.input_circonstance_secondaire.currentData(),
                'taux_responsabilite': self._get_responsabilite_taux(),
                'date_survenance': date_surv,
                'date_declaration': date_decl,
                'description': self.input_description.toPlainText().strip() or None,
                'est_flotte': est_flotte,
                'vehicule_sinistre_id': self.contract_selector.get_selected_vehicle_id(),
                'created_by': self.user.id if self.user else None,
            }
            
            result = self.sinistre_controller.creer_sinistre(data)
            
            if result:
                numero = result.get('numero_sinistre', 'N/A')
                
                QMessageBox.information(
                    self,
                    "Sinistre créé",
                    f"<b>Sinistre {numero}</b> créé avec succès !\n\n"
                    f"<b>Client :</b> {client.get('nom', '')} {client.get('prenom', '')}<br>"
                    f"<b>Contrat :</b> {contract.get('numero_police', 'N/A')}<br>"
                    f"<b>Survenance :</b> {date_surv.strftime('%d/%m/%Y')}<br>"
                    f"<b>Statut :</b> OUVERT"
                )
                
                self.sinistre_created.emit(result)
                self.clear_form()
                
                self.lbl_footer_status.setText("Sinistre créé — formulaire réinitialisé")
                self.lbl_footer_status.setStyleSheet("color: #10b981; font-size: 12px; font-weight: 600; background: transparent;")
                QTimer.singleShot(4000, lambda: self.lbl_footer_status.setStyleSheet(
                    "color: #64748b; font-size: 12px; background: transparent;"
                ))
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création : {str(e)}")
    
    def _get_responsabilite_taux(self) -> float:
        code = self.input_responsabilite.currentData()
        ref = self._responsabilites_cache.get(code)
        if ref:
            return float(ref.get('valeur', 0))
        return 0.0
    
    def _show_error(self, message: str):
        self.lbl_footer_status.setText(message)
        self.lbl_footer_status.setStyleSheet("color: #dc2626; font-size: 12px; font-weight: 700; background: transparent;")
        QMessageBox.warning(self, "Validation", message)
        
        QTimer.singleShot(5000, lambda: self.lbl_footer_status.setStyleSheet(
            "color: #64748b; font-size: 12px; background: transparent;"
        ))
    
    def clear_form(self):
        try:
            self.client_search.clear_selection()
        except Exception:
            pass
        
        try:
            self.contract_selector.clear_selection()
        except Exception:
            pass
        
        self.input_numero_ref.clear()
        self.input_compagnie.clear()
        self.input_agence.clear()
        self.input_branche.setCurrentIndex(0)
        self.input_categorie.clear()
        self.input_sous_categorie.clear()
        self.input_circonstance.setCurrentIndex(0)
        self.input_circonstance_secondaire.setCurrentIndex(0)
        self.input_responsabilite.setCurrentIndex(0)
        self.input_date_survenance.setDate(QDate.currentDate())
        self.input_date_declaration.setDate(QDate.currentDate())
        self.input_description.clear()
        
        self._vehicule_sinistre = None
        self.flotte_banner.hide()
        
        self.summary_client.setText("Non sélectionné")
        self.summary_contrat.setText("Non sélectionné")
        self.summary_vehicule.setText("—")
        self.summary_branche.setText("—")
        self.summary_dates.setText("—")
        
        self.badge_client.setText("  En attente")
        self.badge_client.setStyleSheet(STYLE_BADGE_ERROR)
        
        self._update_completion()