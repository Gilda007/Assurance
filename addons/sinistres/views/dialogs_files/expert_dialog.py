"""
Dialogue d'enregistrement / modification d'un expert
Aligné sur le modèle Expert (Tome 4 du CDC)
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QMessageBox, QFrame, QScrollArea, QWidget,
    QGridLayout, QCheckBox, QTabWidget, QFileDialog, QListWidget,
    QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QPixmap, QColor

from datetime import datetime
from typing import Optional, Dict, Any, List


# ============================================================
# STYLES
# ============================================================

STYLE_DIALOG = "QDialog { background-color: #f8fafc; }"

STYLE_HEADER = """
    QFrame#Header {
        background-color: white;
        border-bottom: 1px solid #e2e8f0;
    }
"""

STYLE_GROUP = """
    QGroupBox {
        font-weight: bold;
        font-size: 12px;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        margin-top: 10px;
        padding-top: 15px;
        background-color: white;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px;
        color: #1e293b;
    }
"""

STYLE_INPUT = """
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 7px 10px;
        font-size: 12px;
        color: #1e293b;
        min-height: 18px;
    }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
    QTextEdit:focus, QDoubleSpinBox:focus {
        border: 2px solid #1a73e8;
        background-color: white;
    }
"""

STYLE_REQUIRED = """
    QLineEdit, QComboBox, QDateEdit {
        background-color: #fefce8;
        border: 1px solid #fde047;
        border-radius: 8px;
        padding: 7px 10px;
        font-size: 12px;
        min-height: 18px;
    }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
        border: 2px solid #1a73e8;
        background-color: white;
    }
"""

STYLE_BTN_PRIMARY = """
    QPushButton {
        background-color: #1a73e8;
        color: white;
        padding: 9px 24px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 12px;
        border: none;
    }
    QPushButton:hover { background-color: #1557b0; }
    QPushButton:disabled {
        background-color: #cbd5e1;
        color: #94a3b8;
    }
"""

STYLE_BTN_SECONDARY = """
    QPushButton {
        background-color: white;
        color: #64748b;
        padding: 9px 20px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 12px;
        border: 1px solid #e2e8f0;
    }
    QPushButton:hover { background-color: #f8fafc; }
"""

STYLE_TAB = """
    QTabWidget::pane {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background-color: white;
    }
    QTabBar::tab {
        padding: 8px 18px;
        margin-right: 2px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
        font-size: 12px;
    }
    QTabBar::tab:selected {
        background-color: white;
        border-bottom: 2px solid #1a73e8;
        color: #1a73e8;
    }
    QTabBar::tab:hover { background-color: #f1f5f9; }
"""


# ============================================================
# LISTES PAR DÉFAUT (à remplacer par référentiels)
# ============================================================

DOMAINES_EXPERTISE = [
    "Automobile",
    "Bâtiment",
    "Transport",
    "Marchandises",
    "Médical",
    "Judiciaire",
    "Incendie",
    "RC",
    "Multirisque",
]

ZONES_GEOGRAPHIQUES = [
    "Douala",
    "Yaoundé",
    "Bafoussam",
    "Garoua",
    "Bamenda",
    "Maroua",
    "Ngaoundéré",
    "Bertoua",
    "Ebolowa",
    "Buea",
    "Limbé",
    "Kribi",
]


# ============================================================
# DIALOGUE
# ============================================================

class ExpertDialog(QDialog):
    """
    Dialogue d'enregistrement / modification d'un expert.
    
    Modes :
    - Création : expert_data=None
    - Modification : expert_data=dict existant
    """
    
    expert_saved = Signal(dict)
    
    def __init__(
        self,
        expert_controller,
        user,
        expert_data: Optional[Dict] = None,
        referentiel_controller=None,
        parent=None
    ):
        super().__init__(parent)
        self.expert_controller = expert_controller
        self.user = user
        self.expert_data = expert_data
        self.referentiel_controller = referentiel_controller
        self.is_edit_mode = expert_data is not None
        
        title = "Modifier un expert" if self.is_edit_mode else "Enregistrer un expert"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(720, 640)
        self.setStyleSheet(STYLE_DIALOG)
        
        self._photo_path = None
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self._populate()
    
    # ============================================================
    # UI
    # ============================================================
    
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # En-tête
        root.addWidget(self._build_header())
        
        # Onglets
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(STYLE_TAB)
        self.tabs.addTab(self._build_tab_identite(), "👤 Identité")
        self.tabs.addTab(self._build_tab_coordonnees(), "📞 Coordonnées")
        self.tabs.addTab(self._build_tab_metier(), "🛠️ Métier")
        self.tabs.addTab(self._build_tab_complement(), "📝 Complément")
        
        root.addWidget(self.tabs, 1)
        
        # Pied
        root.addWidget(self._build_footer())
    
    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("Header")
        header.setStyleSheet(STYLE_HEADER)
        header.setFixedHeight(70)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 12, 20, 12)
        
        # Icône
        icon = QLabel("✏️" if self.is_edit_mode else "➕")
        icon.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon)
        
        # Titre
        title_block = QVBoxLayout()
        title_block.setSpacing(0)
        
        title = QLabel(
            "Modifier un expert" if self.is_edit_mode else "Enregistrer un expert"
        )
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        title_block.addWidget(title)
        
        subtitle = QLabel("Les champs marqués * sont obligatoires")
        subtitle.setStyleSheet("font-size: 10px; color: #64748b;")
        title_block.addWidget(subtitle)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        # Badge mode
        if self.is_edit_mode:
            badge = QLabel(f"✏️ Mode édition")
            badge.setStyleSheet("""
                background-color: #fef3c7;
                color: #92400e;
                padding: 4px 10px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            """)
            layout.addWidget(badge)
        
        return header
    
    # ============================================================
    # ONGLET 1 : IDENTITÉ
    # ============================================================
    
    def _build_tab_identite(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # --- Photo + identité ---
        top_row = QHBoxLayout()
        top_row.setSpacing(20)
        
        # Photo (gauche)
        photo_container = QVBoxLayout()
        photo_container.setSpacing(6)
        
        self.lbl_photo = QLabel("👤")
        self.lbl_photo.setFixedSize(100, 100)
        self.lbl_photo.setAlignment(Qt.AlignCenter)
        self.lbl_photo.setStyleSheet("""
            background-color: #f1f5f9;
            border: 2px dashed #cbd5e1;
            border-radius: 50px;
            font-size: 40px;
            color: #94a3b8;
        """)
        photo_container.addWidget(self.lbl_photo, alignment=Qt.AlignCenter)
        
        btn_photo = QPushButton("📷 Choisir")
        btn_photo.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #64748b;
                padding: 5px 12px;
                border-radius: 6px;
                border: 1px solid #e2e8f0;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #1a73e8;
                color: #1a73e8;
            }
        """)
        btn_photo.setCursor(Qt.PointingHandCursor)
        btn_photo.clicked.connect(self._choisir_photo)
        photo_container.addWidget(btn_photo, alignment=Qt.AlignCenter)
        
        top_row.addLayout(photo_container)
        
        # Champs identité (droite)
        form_group = QGroupBox("Identité")
        form_group.setStyleSheet(STYLE_GROUP)
        form = QFormLayout(form_group)
        form.setSpacing(10)
        form.setContentsMargins(15, 20, 15, 15)
        
        # Civilité + Nom + Prénom
        row_nom = QHBoxLayout()
        row_nom.setSpacing(8)
        
        self.input_civilite = QComboBox()
        self.input_civilite.addItem("—", None)
        for c in ["M.", "Mme", "Mlle"]:
            self.input_civilite.addItem(c, c)
        self.input_civilite.setStyleSheet(STYLE_INPUT)
        self.input_civilite.setFixedWidth(70)
        row_nom.addWidget(self.input_civilite)
        
        self.input_nom = QLineEdit()
        self.input_nom.setPlaceholderText("Nom *")
        self.input_nom.setStyleSheet(STYLE_REQUIRED)
        self.input_nom.textChanged.connect(self._update_completion)
        row_nom.addWidget(self.input_nom, 1)
        
        self.input_prenom = QLineEdit()
        self.input_prenom.setPlaceholderText("Prénom")
        self.input_prenom.setStyleSheet(STYLE_INPUT)
        row_nom.addWidget(self.input_prenom, 1)
        
        form.addRow("Nom complet *:", row_nom)
        
        # Code expert
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Code interne (auto-généré si vide)")
        self.input_code.setStyleSheet(STYLE_INPUT)
        form.addRow("Code expert:", self.input_code)
        
        # Numéro d'agrément
        self.input_agrement = QLineEdit()
        self.input_agrement.setPlaceholderText("N° d'agrément officiel *")
        self.input_agrement.setStyleSheet(STYLE_REQUIRED)
        self.input_agrement.textChanged.connect(self._update_completion)
        form.addRow("N° Agrément *:", self.input_agrement)
        
        # Date d'agrément
        self.input_date_agrement = QDateEdit()
        self.input_date_agrement.setDate(QDate.currentDate())
        self.input_date_agrement.setCalendarPopup(True)
        self.input_date_agrement.setStyleSheet(STYLE_INPUT)
        form.addRow("Date agrément:", self.input_date_agrement)
        
        top_row.addWidget(form_group, 1)
        
        layout.addLayout(top_row)
        
        # --- Statut ---
        statut_group = QGroupBox("Statut")
        statut_group.setStyleSheet(STYLE_GROUP)
        statut_layout = QHBoxLayout(statut_group)
        statut_layout.setContentsMargins(15, 20, 15, 15)
        
        self.check_actif = QCheckBox("Expert actif (peut recevoir des missions)")
        self.check_actif.setChecked(True)
        self.check_actif.setStyleSheet("font-size: 12px;")
        statut_layout.addWidget(self.check_actif)
        
        statut_layout.addStretch()
        
        layout.addWidget(statut_group)
        layout.addStretch()
        
        return tab
    
    # ============================================================
    # ONGLET 2 : COORDONNÉES
    # ============================================================
    
    def _build_tab_coordonnees(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        group = QGroupBox("Coordonnées")
        group.setStyleSheet(STYLE_GROUP)
        form = QFormLayout(group)
        form.setSpacing(10)
        form.setContentsMargins(15, 20, 15, 15)
        
        # Téléphone + Portable
        row_tel = QHBoxLayout()
        row_tel.setSpacing(8)
        
        self.input_telephone = QLineEdit()
        self.input_telephone.setPlaceholderText("Téléphone fixe")
        self.input_telephone.setStyleSheet(STYLE_INPUT)
        row_tel.addWidget(self.input_telephone, 1)
        
        self.input_portable = QLineEdit()
        self.input_portable.setPlaceholderText("Mobile *")
        self.input_portable.setStyleSheet(STYLE_REQUIRED)
        self.input_portable.textChanged.connect(self._update_completion)
        row_tel.addWidget(self.input_portable, 1)
        
        form.addRow("Téléphone:", row_tel)
        
        # Email
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("email@exemple.com")
        self.input_email.setStyleSheet(STYLE_INPUT)
        form.addRow("Email:", self.input_email)
        
        # Adresse
        self.input_adresse = QLineEdit()
        self.input_adresse.setPlaceholderText("Adresse complète")
        self.input_adresse.setStyleSheet(STYLE_INPUT)
        form.addRow("Adresse:", self.input_adresse)
        
        # Code postal + Ville
        row_ville = QHBoxLayout()
        row_ville.setSpacing(8)
        
        self.input_code_postal = QLineEdit()
        self.input_code_postal.setPlaceholderText("Code postal")
        self.input_code_postal.setStyleSheet(STYLE_INPUT)
        self.input_code_postal.setFixedWidth(100)
        row_ville.addWidget(self.input_code_postal)
        
        self.input_ville = QLineEdit()
        self.input_ville.setPlaceholderText("Ville")
        self.input_ville.setStyleSheet(STYLE_INPUT)
        row_ville.addWidget(self.input_ville, 1)
        
        form.addRow("Localisation:", row_ville)
        
        # Pays
        self.input_pays = QComboBox()
        self.input_pays.setStyleSheet(STYLE_INPUT)
        for p in ["Cameroun", "France", "Sénégal", "Côte d'Ivoire", "Autre"]:
            self.input_pays.addItem(p, p)
        form.addRow("Pays:", self.input_pays)
        
        layout.addWidget(group)
        layout.addStretch()
        
        return tab
    
    # ============================================================
    # ONGLET 3 : MÉTIER
    # ============================================================
    
    def _build_tab_metier(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # --- Domaines d'expertise (liste multi-sélection) ---
        domaines_group = QGroupBox("Domaines d'expertise *")
        domaines_group.setStyleSheet(STYLE_GROUP)
        domaines_layout = QVBoxLayout(domaines_group)
        domaines_layout.setContentsMargins(15, 20, 15, 15)
        
        info = QLabel("Sélectionnez un ou plusieurs domaines :")
        info.setStyleSheet("font-size: 11px; color: #64748b; font-style: italic;")
        domaines_layout.addWidget(info)
        
        self.list_domaines = QListWidget()
        self.list_domaines.setSelectionMode(QListWidget.MultiSelection)
        self.list_domaines.setMaximumHeight(150)
        self.list_domaines.setStyleSheet("""
            QListWidget {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 4px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 6px 10px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            QListWidget::item:hover {
                background-color: #f1f5f9;
            }
        """)
        for domaine in self._load_domaines():
            item = QListWidgetItem(domaine['libelle'])
            item.setData(Qt.UserRole, domaine['code'])      # ✅ stocke le code
            item.setData(Qt.UserRole + 1, domaine['libelle'])  # libellé
            self.list_domaines.addItem(item)
        self.list_domaines.itemSelectionChanged.connect(self._update_completion)
        domaines_layout.addWidget(self.list_domaines)
        
        layout.addWidget(domaines_group)
        
        # --- Zones géographiques ---
        zones_group = QGroupBox("Zones géographiques d'intervention")
        zones_group.setStyleSheet(STYLE_GROUP)
        zones_layout = QVBoxLayout(zones_group)
        zones_layout.setContentsMargins(15, 20, 15, 15)
        
        info_zones = QLabel("Sélectionnez les zones couvertes :")
        info_zones.setStyleSheet("font-size: 11px; color: #64748b; font-style: italic;")
        zones_layout.addWidget(info_zones)
        
        # Grille de checkboxes
        zones_grid = QGridLayout()
        zones_grid.setSpacing(6)
        
        self.check_zones = {}
        for i, zone in enumerate(self._load_zones()):
            check = QCheckBox(zone['libelle'])
            check.setProperty("zone_code", zone['code'])    # ✅ stocke le code
            check.setStyleSheet("font-size: 11px;")
            self.check_zones[zone['code']] = check          # clé = code
            zones_grid.addWidget(check, i // 4, i % 4)
        
        zones_layout.addLayout(zones_grid)
        layout.addWidget(zones_group)
        
        # --- Tarifs ---
        tarifs_group = QGroupBox("Tarification")
        tarifs_group.setStyleSheet(STYLE_GROUP)
        tarifs_form = QFormLayout(tarifs_group)
        tarifs_form.setSpacing(10)
        tarifs_form.setContentsMargins(15, 20, 15, 15)
        
        # Tarif horaire
        self.input_tarif_horaire = QDoubleSpinBox()
        self.input_tarif_horaire.setRange(0, 10_000_000)
        self.input_tarif_horaire.setPrefix("FCFA ")
        self.input_tarif_horaire.setDecimals(0)
        self.input_tarif_horaire.setSingleStep(1000)
        self.input_tarif_horaire.setStyleSheet(STYLE_INPUT)
        tarifs_form.addRow("Tarif honoraire:", self.input_tarif_horaire)
        
        # Frais de déplacement
        self.input_frais_deplacement = QDoubleSpinBox()
        self.input_frais_deplacement.setRange(0, 10_000_000)
        self.input_frais_deplacement.setPrefix("FCFA ")
        self.input_frais_deplacement.setDecimals(0)
        self.input_frais_deplacement.setSingleStep(1000)
        self.input_frais_deplacement.setStyleSheet(STYLE_INPUT)
        tarifs_form.addRow("Frais de déplacement:", self.input_frais_deplacement)
        
        layout.addWidget(tarifs_group)
        layout.addStretch()
        
        return tab
    
    # ============================================================
    # ONGLET 4 : COMPLÉMENT
    # ============================================================
    
    def _build_tab_complement(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        group = QGroupBox("Informations complémentaires")
        group.setStyleSheet(STYLE_GROUP)
        form = QFormLayout(group)
        form.setSpacing(10)
        form.setContentsMargins(15, 20, 15, 15)
        
        # Observations
        self.input_observations = QTextEdit()
        self.input_observations.setPlaceholderText(
            "Notes internes, spécialités, historique, remarques..."
        )
        self.input_observations.setMaximumHeight(150)
        self.input_observations.setStyleSheet(STYLE_INPUT)
        form.addRow("Observations:", self.input_observations)
        
        # Info
        info = QLabel(
            "💡 Ces informations sont visibles uniquement par les administrateurs "
            "et les gestionnaires de sinistres."
        )
        info.setStyleSheet("font-size: 11px; color: #64748b; font-style: italic;")
        info.setWordWrap(True)
        form.addRow("", info)
        
        layout.addWidget(group)
        layout.addStretch()
        
        return tab
    
    # ============================================================
    # PIED
    # ============================================================
    
    def _build_footer(self) -> QFrame:
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #e2e8f0;
            }
        """)
        footer.setFixedHeight(70)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 12, 20, 12)
        
        # Statut de complétion
        self.lbl_status = QLabel("📌 Champs obligatoires : Nom, Agrément, Téléphone, Domaines")
        self.lbl_status.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(self.lbl_status)
        
        layout.addStretch()
        
        # Annuler
        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.setStyleSheet(STYLE_BTN_SECONDARY)
        self.btn_annuler.clicked.connect(self.reject)
        layout.addWidget(self.btn_annuler)
        
        # Enregistrer
        self.btn_save = QPushButton("💾 Enregistrer")
        self.btn_save.setStyleSheet(STYLE_BTN_PRIMARY)
        self.btn_save.setMinimumWidth(160)
        self.btn_save.clicked.connect(self.save)
        layout.addWidget(self.btn_save)
        
        return footer
    
    # ============================================================
    # PRÉ-REMPLISSAGE (édition)
    # ============================================================
    
    def _populate(self):
        """Pré-remplit le formulaire en mode édition"""
        d = self.expert_data
        
        # Identité
        self.input_civilite.setCurrentText(d.get('civilite') or "—")
        self.input_nom.setText(d.get('nom', '') or '')
        self.input_prenom.setText(d.get('prenom', '') or '')
        self.input_code.setText(d.get('code', '') or '')
        self.input_agrement.setText(d.get('agrement', '') or '')
        
        # Date agrément
        date_ag = d.get('date_agrement')
        if date_ag:
            try:
                s = str(date_ag)[:10]
                y, m, day = s.split('-')
                self.input_date_agrement.setDate(QDate(int(y), int(m), int(day)))
            except Exception:
                pass
        
        self.check_actif.setChecked(bool(d.get('est_actif', True)))
        
        # Coordonnées
        self.input_telephone.setText(d.get('telephone', '') or '')
        self.input_portable.setText(d.get('portable', '') or '')
        self.input_email.setText(d.get('email', '') or '')
        self.input_adresse.setText(d.get('adresse', '') or '')
        self.input_code_postal.setText(d.get('code_postal', '') or '')
        self.input_ville.setText(d.get('ville', '') or '')
        
        pays = d.get('pays')
        if pays:
            idx = self.input_pays.findText(pays)
            if idx >= 0:
                self.input_pays.setCurrentIndex(idx)
        
        # Métier - Domaines
        domaines = d.get('domaines', []) or []
        for i in range(self.list_domaines.count()):
            item = self.list_domaines.item(i)
            if item.data(Qt.UserRole) in domaines:
                item.setSelected(True)
        
        # Métier - Zones
        zones = d.get('zones', []) or []
        for zone_name, check in self.check_zones.items():
            if zone_name in zones:
                check.setChecked(True)
        
        # Tarifs
        self.input_tarif_horaire.setValue(d.get('tarif_horaire', 0) or 0)
        self.input_frais_deplacement.setValue(d.get('frais_deplacement', 0) or 0)
        
        # Complément
        self.input_observations.setPlainText(d.get('observations', '') or '')
    
    # ============================================================
    # VALIDATION EN DIRECT
    # ============================================================
    
    def _update_completion(self):
        """Met à jour l'état de complétion"""
        nom_ok = bool(self.input_nom.text().strip())
        agrement_ok = bool(self.input_agrement.text().strip())
        portable_ok = bool(self.input_portable.text().strip())
        domaines_ok = len(self.list_domaines.selectedItems()) > 0
        
        if nom_ok and agrement_ok and portable_ok and domaines_ok:
            self.lbl_status.setText("✅ Formulaire prêt à être enregistré")
            self.lbl_status.setStyleSheet("color: #16a34a; font-size: 11px; font-weight: bold;")
            self.btn_save.setEnabled(True)
        else:
            missing = []
            if not nom_ok:
                missing.append("Nom")
            if not agrement_ok:
                missing.append("Agrément")
            if not portable_ok:
                missing.append("Mobile")
            if not domaines_ok:
                missing.append("Domaines")
            self.lbl_status.setText(f"⚠️ Champs manquants : {', '.join(missing)}")
            self.lbl_status.setStyleSheet("color: #dc2626; font-size: 11px; font-weight: bold;")
            self.btn_save.setEnabled(False)
    
    # ============================================================
    # PHOTO
    # ============================================================
    
    def _choisir_photo(self):
        """Ouvre un sélecteur de photo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir une photo",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;Tous les fichiers (*)"
        )
        
        if not file_path:
            return
        
        self._photo_path = file_path
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.lbl_photo.setPixmap(scaled)
            self.lbl_photo.setStyleSheet("""
                background-color: #f1f5f9;
                border: 2px solid #1a73e8;
                border-radius: 50px;
            """)
    
    # ============================================================
    # SAUVEGARDE
    # ============================================================
    
    def _load_domaines(self) -> list:
        """Charge les domaines d'expertise depuis le référentiel"""
        try:
            if self.referentiel_controller:
                refs = self.referentiel_controller.get_referentiels_by_famille("domaines_expertise")
                if refs:
                    return [
                        {
                            'code': r.get('code'),
                            'libelle': r.get('libelle') or r.get('code'),
                        }
                        for r in refs
                    ]
        except Exception as e:
            print(f"Erreur chargement domaines: {e}")
        
        # Fallback
        return [{'code': d.upper(), 'libelle': d} for d in DOMAINES_EXPERTISE]


    def _load_zones(self) -> list:
        """Charge les zones géographiques depuis le référentiel"""
        try:
            if self.referentiel_controller:
                refs = self.referentiel_controller.get_referentiels_by_famille("zones_geographiques")
                if refs:
                    return [
                        {
                            'code': r.get('code'),
                            'libelle': r.get('libelle') or r.get('code'),
                        }
                        for r in refs
                    ]
        except Exception as e:
            print(f"Erreur chargement zones: {e}")
        
        # Fallback
        return [{'code': z[:3].upper(), 'libelle': z} for z in ZONES_GEOGRAPHIQUES]


    def save(self):
        """Valide et enregistre l'expert"""
        try:
            # --- Validation finale ---
            nom = self.input_nom.text().strip()
            if not nom:
                self._show_error("Le nom est obligatoire")
                return
            
            agrement = self.input_agrement.text().strip()
            if not agrement:
                self._show_error("Le numéro d'agrément est obligatoire")
                return
            
            portable = self.input_portable.text().strip()
            if not portable:
                self._show_error("Le numéro de mobile est obligatoire")
                return
            
            domaines = [
                item.data(Qt.UserRole)
                for item in self.list_domaines.selectedItems()
            ]
            if not domaines:
                self._show_error("Sélectionnez au moins un domaine d'expertise")
                return
            
            zones = [
                code for code, check in self.check_zones.items()
                if check.isChecked()
            ]
            
            # --- Construction des données ---
            date_agrement = self.input_date_agrement.date().toPython()
            
            data = {
                'civilite': self.input_civilite.currentData(),
                'nom': nom,
                'prenom': self.input_prenom.text().strip() or None,
                'code': self.input_code.text().strip() or None,
                'agrement': agrement,
                'date_agrement': date_agrement,
                'est_actif': self.check_actif.isChecked(),
                'telephone': self.input_telephone.text().strip() or None,
                'portable': portable,
                'email': self.input_email.text().strip() or None,
                'adresse': self.input_adresse.text().strip() or None,
                'code_postal': self.input_code_postal.text().strip() or None,
                'ville': self.input_ville.text().strip() or None,
                'pays': self.input_pays.currentData(),
                'domaines': domaines,
                'zones': zones,
                'tarif_horaire': self.input_tarif_horaire.value(),
                'frais_deplacement': self.input_frais_deplacement.value(),
                'observations': self.input_observations.toPlainText().strip() or None,
            }
            # ✅ Photo
            if self._photo_path:
                # Copier la photo via FileService
                try:
                    from addons.sinistres.services.file_service import get_file_service
                    fs = get_file_service()
                    rel_path = fs.save_expert_photo(
                        expert_code=self.input_code.text().strip() or nom,
                        source_path=self._photo_path,
                        compress=True,
                    )
                    if rel_path:
                        data['photo_path'] = rel_path
                except Exception as e:
                    print(f"Erreur copie photo expert: {e}")
            
            # --- Envoi au contrôleur ---
            if self.is_edit_mode:
                data['updated_by'] = self.user.id if self.user else None
                result = self.expert_controller.update_expert(
                    self.expert_data['id'], data
                )
                action = "modifié"
            else:
                data['created_by'] = self.user.id if self.user else None
                result = self.expert_controller.creer_expert(data)
                action = "enregistré"
            
            if not result:
                self._show_error("Erreur lors de l'enregistrement")
                return
            
            # --- Succès ---
            self.expert_saved.emit(result)
            QMessageBox.information(
                self,
                "✅ Succès",
                f"Expert {action} avec succès !\n\n"
                f"👤 {nom} {self.input_prenom.text()}\n"
                f"📋 Agrément : {agrement}"
            )
            self.accept()
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._show_error(f"Erreur inattendue : {str(e)}")

    
    def _show_error(self, message: str):
        """Affiche une erreur"""
        self.lbl_status.setText(f"⚠️ {message}")
        self.lbl_status.setStyleSheet("color: #dc2626; font-size: 11px; font-weight: bold;")
        QMessageBox.warning(self, "Validation", message)