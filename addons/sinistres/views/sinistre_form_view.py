"""
Formulaire de création de sinistre - Version professionnelle
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox,
    QFormLayout, QGroupBox, QFrame, QMessageBox, QScrollArea,
    QGraphicsDropShadowEffect, QGridLayout, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QColor, QFont, QIcon, QPixmap

from datetime import datetime, timedelta


# ============================================================
# STYLES CONSTANTS
# ============================================================
STYLE_CARD = """
    QFrame#Card {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }
"""

STYLE_CARD_HEADER = """
    QLabel#CardTitle {
        font-size: 14px;
        font-weight: bold;
        color: #1e293b;
    }
    QLabel#CardIcon {
        font-size: 18px;
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
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, 
    QTextEdit:focus, QDoubleSpinBox:focus {
        border: 2px solid #1a73e8;
        background-color: white;
    }
    QLineEdit:disabled, QComboBox:disabled {
        background-color: #f1f5f9;
        color: #94a3b8;
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
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
        background-color: #fefce8;
        border: 1px solid #fde047;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
        border: 2px solid #1a73e8;
        background-color: white;
    }
"""

STYLE_BADGE_SUCCESS = """
    QLabel {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
    }
"""

STYLE_BADGE_ERROR = """
    QLabel {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
    }
"""

STYLE_FLOTTE_BANNER = """
    QFrame {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        padding: 10px;
    }
    QLabel {
        color: #1e40af;
        font-size: 12px;
        font-weight: bold;
    }
"""

STYLE_BTN_PRIMARY = """
    QPushButton {
        background-color: #1a73e8;
        color: white;
        padding: 12px 32px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 13px;
        border: none;
    }
    QPushButton:hover {
        background-color: #1557b0;
    }
    QPushButton:disabled {
        background-color: #cbd5e1;
        color: #94a3b8;
    }
"""

STYLE_BTN_SECONDARY = """
    QPushButton {
        background-color: white;
        color: #64748b;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 13px;
        border: 1px solid #e2e8f0;
    }
    QPushButton:hover {
        background-color: #f8fafc;
        border-color: #cbd5e1;
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
        background-color: #1a73e8;
        color: white;
        border-radius: 12px;
        padding: 4px 12px;
        font-size: 11px;
        font-weight: bold;
    }
"""

STYLE_STEP_BADGE_INACTIVE = """
    QLabel {
        background-color: #f1f5f9;
        color: #94a3b8;
        border-radius: 12px;
        padding: 4px 12px;
        font-size: 11px;
    }
"""


# ============================================================
# HELPER WIDGETS
# ============================================================

class Card(QFrame):
    """Carte avec titre et icône"""
    def __init__(self, icon: str, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setStyleSheet(STYLE_CARD)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 18, 20, 20)
        self.layout.setSpacing(15)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(8)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setObjectName("CardIcon")
        lbl_icon.setStyleSheet(STYLE_CARD_HEADER)
        header.addWidget(lbl_icon)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("CardTitle")
        lbl_title.setStyleSheet(STYLE_CARD_HEADER)
        header.addWidget(lbl_title)
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
            min-width: 140px;
        """)
        row.addWidget(lbl)
        
        row.addWidget(widget, 1)
        self.content.addLayout(row)
        
        return lbl


class Badge(QLabel):
    """Badge coloré"""
    def __init__(self, text: str, success: bool = True, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(STYLE_BADGE_SUCCESS if success else STYLE_BADGE_ERROR)
        self.setAlignment(Qt.AlignCenter)


# ============================================================
# PAGE PRINCIPALE
# ============================================================

class NouveauSinistrePage(QWidget):
    """Formulaire de création de sinistre - Version professionnelle"""
    
    def __init__(self, sinistre_controller, referentiel_controller, user):
        super().__init__()
        self.sinistre_controller = sinistre_controller
        self.referentiel_controller = referentiel_controller
        
        from addons.sinistres.controllers.automobile_controller import AutomobileController
        self.automobile_controller = AutomobileController()
        self.automobile_controller.set_current_user(user)
        
        self.user = user
        self._vehicule_sinistre = None
        
        self.setup_ui()
        self.load_referentiels()
        self._connect_validators()
    
    # ============================================================
    # UI PRINCIPALE
    # ============================================================
    
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # ============================================================
        # EN-TÊTE FIXE
        # ============================================================
        root.addWidget(self._build_header())
        
        # ============================================================
        # CORPS SCROLLABLE + PANNEAU LATÉRAL
        # ============================================================
        body = QHBoxLayout()
        body.setContentsMargins(25, 20, 25, 20)
        body.setSpacing(20)
        
        # Colonne principale (formulaire)
        body.addWidget(self._build_form_column(), 3)
        
        # Colonne latérale (résumé)
        body.addWidget(self._build_summary_column(), 1)
        
        root.addLayout(body, 1)
        
        # ============================================================
        # PIED FIXE (boutons)
        # ============================================================
        root.addWidget(self._build_footer())
    
    def _build_header(self) -> QWidget:
        """En-tête avec titre et stepper"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        header.setFixedHeight(90)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(25, 15, 25, 15)
        
        # Titre
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title = QLabel("📝 Nouveau sinistre")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1e293b;")
        title_block.addWidget(title)
        
        subtitle = QLabel("Déclaration d'un événement dommageable")
        subtitle.setStyleSheet("font-size: 12px; color: #64748b;")
        title_block.addWidget(subtitle)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        # Stepper
        steps_layout = QHBoxLayout()
        steps_layout.setSpacing(8)
        
        self.step_badges = []
        for i, step in enumerate(["1. Client", "2. Contrat", "3. Détails", "4. Validation"]):
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
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Carte 1 : Client et Contrat
        layout.addWidget(self._card_client_contrat())
        
        # Carte 2 : Informations générales
        layout.addWidget(self._card_infos_generales())
        
        # Carte 3 : Classification
        layout.addWidget(self._card_classification())
        
        # Carte 4 : Circonstances et responsabilité
        layout.addWidget(self._card_circonstances())
        
        # Carte 5 : Dates
        layout.addWidget(self._card_dates())
        
        # Carte 6 : Description
        layout.addWidget(self._card_description())
        
        layout.addStretch()
        scroll.setWidget(content)
        
        return scroll
    
    # ============================================================
    # CARTES
    # ============================================================
    
    def _card_client_contrat(self) -> Card:
        from addons.sinistres.views.client_search_widget import ClientSearchWidget
        from addons.sinistres.views.contract_selector_widget import ContractSelectorWidget
        
        card = Card("👥", "Client et contrat")
        
        # Badge état
        self.badge_client = Badge("⏳ En attente", success=False)
        card.layout.insertWidget(0, self.badge_client, alignment=Qt.AlignRight)
        
        # Widgets
        self.client_search = ClientSearchWidget(self.automobile_controller)
        self.client_search.client_selected.connect(self._on_client_selected)
        card.content.addWidget(self.client_search)
        
        self.contract_selector = ContractSelectorWidget(self.automobile_controller)
        self.contract_selector.contract_selected.connect(self._on_contract_selected)
        self.contract_selector.vehicle_selected.connect(self._on_vehicle_selected)
        card.content.addWidget(self.contract_selector)
        
        # Bandeau flotte (caché par défaut)
        self.flotte_banner = QFrame()
        self.flotte_banner.setStyleSheet(STYLE_FLOTTE_BANNER)
        self.flotte_banner.hide()
        flotte_layout = QVBoxLayout(self.flotte_banner)
        flotte_layout.setContentsMargins(12, 8, 12, 8)
        
        self.lbl_flotte_info = QLabel("🚛 Contrat flotte détecté - Sélectionnez le véhicule sinistré")
        flotte_layout.addWidget(self.lbl_flotte_info)
        
        card.content.addWidget(self.flotte_banner)
        
        return card
    
    def _card_infos_generales(self) -> Card:
        card = Card("📋", "Informations générales")
        
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
        card = Card("🏷️", "Classification")
        
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
        card = Card("⚠️", "Circonstances et responsabilité")
        
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
        card = Card("📅", "Dates")
        
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
        self.lbl_date_warning.setStyleSheet("color: #dc2626; font-size: 11px; font-weight: bold;")
        card.content.addWidget(self.lbl_date_warning)
        
        # Info date d'ouverture
        info = QLabel("ℹ️ La date d'ouverture sera générée automatiquement")
        info.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        card.content.addWidget(info)
        
        return card
    
    def _card_description(self) -> Card:
        card = Card("📝", "Description")
        
        self.input_description = QTextEdit()
        self.input_description.setPlaceholderText("Décrivez les circonstances détaillées du sinistre...")
        self.input_description.setMaximumHeight(120)
        self.input_description.setStyleSheet(STYLE_INPUT)
        self.input_description.textChanged.connect(self._update_char_count)
        card.content.addWidget(self.input_description)
        
        # Compteur de caractères
        self.lbl_char_count = QLabel("0 / 2000 caractères")
        self.lbl_char_count.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.lbl_char_count.setAlignment(Qt.AlignRight)
        card.content.addWidget(self.lbl_char_count)
        
        return card
    
    # ============================================================
    # PANNEAU RÉSUMÉ (sticky)
    # ============================================================
    
    def _build_summary_column(self) -> QWidget:
        container = QWidget()
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
        
        # Titre
        title = QLabel("📋 Récapitulatif")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b;")
        s_layout.addWidget(title)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #e2e8f0; max-height: 1px; border: none;")
        s_layout.addWidget(sep)
        
        # Sections du résumé
        self.summary_client = self._summary_block("👤 Client", "Non sélectionné", s_layout)
        self.summary_contrat = self._summary_block("📄 Contrat", "Non sélectionné", s_layout)
        self.summary_vehicule = self._summary_block("🚗 Véhicule", "—", s_layout)
        self.summary_branche = self._summary_block("🏷️ Branche", "—", s_layout)
        self.summary_dates = self._summary_block("📅 Dates", "—", s_layout)
        
        s_layout.addStretch()
        
        # Indicateur de complétion
        completion_frame = QFrame()
        completion_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        c_layout = QVBoxLayout(completion_frame)
        c_layout.setContentsMargins(10, 10, 10, 10)
        
        c_title = QLabel("Complétion")
        c_title.setStyleSheet("font-size: 11px; color: #64748b; font-weight: bold;")
        c_layout.addWidget(c_title)
        
        self.lbl_completion = QLabel("0%")
        self.lbl_completion.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a73e8;")
        c_layout.addWidget(self.lbl_completion)
        
        s_layout.addWidget(completion_frame)
        
        layout.addWidget(summary)
        layout.addStretch()
        
        return container
    
    def _summary_block(self, label: str, value: str, parent_layout) -> QLabel:
        """Crée un bloc de résumé (label + valeur)"""
        block = QVBoxLayout()
        block.setSpacing(2)
        
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 10px; color: #94a3b8; font-weight: 600; text-transform: uppercase;")
        block.addWidget(lbl)
        
        val = QLabel(value)
        val.setStyleSheet("font-size: 12px; color: #1e293b; font-weight: 500;")
        val.setWordWrap(True)
        block.addWidget(val)
        
        parent_layout.addLayout(block)
        return val
    
    # ============================================================
    # PIED (boutons fixes)
    # ============================================================
    
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
        layout.setContentsMargins(25, 15, 25, 15)
        
        # Statut
        self.lbl_footer_status = QLabel("📌 Les champs marqués * sont obligatoires")
        self.lbl_footer_status.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self.lbl_footer_status)
        
        layout.addStretch()
        
        # Bouton annuler
        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.setStyleSheet(STYLE_BTN_SECONDARY)
        self.btn_annuler.clicked.connect(self.clear_form)
        layout.addWidget(self.btn_annuler)
        
        # Bouton créer
        self.btn_creer = QPushButton("✅  Créer le sinistre")
        self.btn_creer.setStyleSheet(STYLE_BTN_PRIMARY)
        self.btn_creer.setMinimumWidth(200)
        self.btn_creer.clicked.connect(self.creer_sinistre)
        layout.addWidget(self.btn_creer)
        
        return footer
    
    # ============================================================
    # LOGIQUE MÉTIER
    # ============================================================
    
    def _connect_validators(self):
        """Connecte les validateurs"""
        pass  # À étendre
    
    def _on_client_selected(self, client: dict):
        """Client sélectionné"""
        client_id = client.get('id')
        if client_id:
            self.contract_selector.set_client(client_id)
            self._vehicule_sinistre = None
            
            nom = f"{client.get('nom', '')} {client.get('prenom', '')}".strip()
            self.summary_client.setText(f"{nom}\n{client.get('code_client', '')}")
            self.badge_client.setText("✅ Client OK")
            self.badge_client.setStyleSheet(STYLE_BADGE_SUCCESS)
            self._update_completion()
    
    def _on_contract_selected(self, contract: dict):
        """Contrat sélectionné"""
        self._vehicule_sinistre = None
        
        police = contract.get('numero_police', 'N/A')
        statut = contract.get('statut', 'N/A')
        self.summary_contrat.setText(f"{police}\n{str(statut).upper()}")
        
        # Détection flotte
        if self.contract_selector._is_flotte(contract):
            self.flotte_banner.show()
            self.summary_vehicule.setText("Sélection requise")
        else:
            self.flotte_banner.hide()
            self.summary_vehicule.setText("—")
        
        self._update_summary()
        self._update_completion()
    
    def _on_vehicle_selected(self, vehicule: dict):
        """Véhicule sélectionné"""
        self._vehicule_sinistre = vehicule
        immat = vehicule.get('immatriculation', 'N/A')
        marque = vehicule.get('marque', '') or ''
        modele = vehicule.get('modele', '') or ''
        self.summary_vehicule.setText(f"{immat}\n{marque} {modele}".strip())
        self._update_completion()
    
    def _on_branche_changed(self, index: int):
        """Branche changée"""
        self._update_summary()
    
    def _validate_dates(self):
        """Vérifie la cohérence des dates"""
        date_surv = self.input_date_survenance.date().toPython()
        date_decl = self.input_date_declaration.date().toPython()
        
        if date_decl < date_surv:
            self.lbl_date_warning.setText("⚠️ La date de déclaration ne peut être antérieure à la date de survenance")
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
        """Met à jour le compteur de caractères"""
        count = len(self.input_description.toPlainText())
        self.lbl_char_count.setText(f"{count} / 2000 caractères")
        if count > 2000:
            self.lbl_char_count.setStyleSheet("color: #dc2626; font-size: 11px; font-weight: bold;")
        else:
            self.lbl_char_count.setStyleSheet("color: #94a3b8; font-size: 11px;")
    
    def _update_summary(self):
        """Met à jour le résumé"""
        # Branche
        branche = self.input_branche.currentText()
        self.summary_branche.setText(branche or "—")
        
        # Dates
        date_s = self.input_date_survenance.date().toString("dd/MM/yyyy")
        date_d = self.input_date_declaration.date().toString("dd/MM/yyyy")
        self.summary_dates.setText(f"Surv.: {date_s}\nDécl.: {date_d}")
        
        self._update_completion()
    
    def _update_completion(self):
        """Calcule le pourcentage de complétion"""
        checks = [
            self.client_search.get_selected_client() is not None,
            self.contract_selector.get_selected_contract() is not None,
            self.input_branche.currentData() is not None,
            bool(self.input_categorie.text().strip()),
            self.input_circonstance.currentData() is not None,
            self.input_responsabilite.currentData() is not None,
        ]
        
        # Véhicule requis si flotte
        contract = self.contract_selector.get_selected_contract()
        if contract and self.contract_selector._is_flotte(contract):
            checks.append(self._vehicule_sinistre is not None)
        
        percent = int((sum(checks) / len(checks)) * 100)
        self.lbl_completion.setText(f"{percent}%")
        
        # Mise à jour badge étapes
        self._update_step_badges(percent)
    
    def _update_step_badges(self, percent: int):
        """Met à jour les badges d'étapes"""
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
    
    # ============================================================
    # CHARGEMENT RÉFÉRENTIELS
    # ============================================================
    
    def load_referentiels(self):
        """Charge les référentiels"""
        try:
            branches = self.referentiel_controller.get_referentiels_by_famille("branches")
            self.input_branche.clear()
            self.input_branche.addItem("-- Sélectionner --", None)
            for b in branches:
                self.input_branche.addItem(b.get('libelle', ''), b.get('code', ''))
            
            circonstances = self.referentiel_controller.get_referentiels_by_famille("circonstances")
            self.input_circonstance.clear()
            self.input_circonstance.addItem("-- Sélectionner --", None)
            self.input_circonstance_secondaire.clear()
            self.input_circonstance_secondaire.addItem("-- Aucune --", None)
            for c in circonstances:
                self.input_circonstance.addItem(c.get('libelle', ''), c.get('code', ''))
                self.input_circonstance_secondaire.addItem(c.get('libelle', ''), c.get('code', ''))
            
            responsabilites = self.referentiel_controller.get_referentiels_by_famille("responsabilites")
            self.input_responsabilite.clear()
            self.input_responsabilite.addItem("-- Sélectionner --", None)
            for r in responsabilites:
                self.input_responsabilite.addItem(
                    f"{r.get('libelle', '')} ({int(r.get('valeur', 0) * 100)}%)",
                    r.get('code', '')
                )
        except Exception as e:
            print(f"Erreur chargement référentiels: {e}")
    
    # ============================================================
    # CRÉATION
    # ============================================================
    
    def creer_sinistre(self):
        """Crée le sinistre"""
        try:
            client = self.client_search.get_selected_client()
            contract = self.contract_selector.get_selected_contract()
            
            # Validations
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
            
            # Vérifier flotte
            est_flotte = self.contract_selector._is_flotte(contract)
            if est_flotte and not self._vehicule_sinistre:
                self._show_error("Ce contrat est une flotte. Veuillez sélectionner le véhicule sinistré.")
                return
            
            # Vérifier dates
            date_surv = self.input_date_survenance.date().toPython()
            date_decl = self.input_date_declaration.date().toPython()
            if date_decl < date_surv:
                self._show_error("La date de déclaration ne peut être antérieure à la date de survenance")
                return
            
            # Construire les données
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
                'created_by': self.user.id if self.user else None
            }
            
            result = self.sinistre_controller.creer_sinistre(data)
            
            if result:
                self.clear_form()
                QMessageBox.information(
                    self,
                    "✅ Succès",
                    f"Sinistre {result.get('numero_sinistre')} créé avec succès !\n\n"
                    f"👤 Client : {client.get('nom')} {client.get('prenom', '')}\n"
                    f"📄 Contrat : {contract.get('numero_police')}\n"
                    f"📅 Survenance : {date_surv.strftime('%d/%m/%Y')}\n"
                    f"📌 Statut : OUVERT"
                )
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création : {str(e)}")
    
    def _get_responsabilite_taux(self) -> float:
        """Récupère le taux de responsabilité"""
        code = self.input_responsabilite.currentData()
        referentiels = self.referentiel_controller.get_referentiels_by_famille("responsabilites")
        for r in referentiels:
            if r.get('code') == code:
                return r.get('valeur', 0)
        return 0.0
    
    def _show_error(self, message: str):
        """Affiche une erreur dans la barre de statut + message box"""
        self.lbl_footer_status.setText(f"⚠️ {message}")
        self.lbl_footer_status.setStyleSheet("color: #dc2626; font-size: 12px; font-weight: bold;")
        QMessageBox.warning(self, "Validation", message)
        
        # Reset après 5 secondes
        from PySide6.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.lbl_footer_status.setStyleSheet("color: #64748b; font-size: 12px;"))
    
    def clear_form(self):
        """Réinitialise le formulaire"""
        self.client_search.clear_selection()
        self.contract_selector.clear_selection()
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
        
        self.badge_client.setText("⏳ En attente")
        self.badge_client.setStyleSheet(STYLE_BADGE_ERROR)
        
        self._update_completion()