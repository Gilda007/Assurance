"""
Dialogue professionnel d'ajout / modification de tiers
Respecte la structure de LometaTiers
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QPushButton,
    QMessageBox, QFrame, QScrollArea, QWidget, QGridLayout, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor
from datetime import datetime
from typing import Optional, Dict, Any


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
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        margin-top: 10px;
        padding-top: 15px;
        background-color: white;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 10px;
        color: #1e293b;
        font-size: 13px;
    }
"""

STYLE_INPUT = """
    QLineEdit, QComboBox, QDateEdit, QTextEdit {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: #1e293b;
        min-height: 20px;
    }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
        border: 2px solid #1a73e8;
        background-color: white;
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
"""

STYLE_REQUIRED = """
    QLineEdit, QComboBox {
        background-color: #fefce8;
        border: 1px solid #fde047;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        min-height: 20px;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 2px solid #1a73e8;
        background-color: white;
    }
"""

STYLE_ERROR = """
    QLineEdit, QComboBox {
        background-color: #fef2f2;
        border: 2px solid #dc2626;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        min-height: 20px;
    }
"""

STYLE_BTN_PRIMARY = """
    QPushButton {
        background-color: #1a73e8;
        color: white;
        padding: 10px 28px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 13px;
        border: none;
    }
    QPushButton:hover {
        background-color: #1557b0;
    }
"""

STYLE_BTN_SECONDARY = """
    QPushButton {
        background-color: white;
        color: #64748b;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 13px;
        border: 1px solid #e2e8f0;
    }
    QPushButton:hover {
        background-color: #f8fafc;
    }
"""

STYLE_TYPES_BTN = """
    QPushButton {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 8px;
        font-size: 11px;
        color: #64748b;
        text-align: center;
    }
    QPushButton:hover {
        background-color: #f1f5f9;
        border-color: #94a3b8;
    }
    QPushButton:checked {
        background-color: #e8f0fe;
        border: 2px solid #1a73e8;
        color: #1a73e8;
        font-weight: bold;
    }
"""


# ============================================================
# TYPES DE TIERS
# ============================================================

TYPES_TIERS = [
    {"code": "conducteur", "label": "🚗 Conducteur", "desc": "Conducteur impliqué"},
    {"code": "passager", "label": "🧍 Passager", "desc": "Passager du véhicule"},
    {"code": "victime", "label": "🩹 Victime", "desc": "Victime du sinistre"},
    {"code": "temoin", "label": "👁️ Témoin", "desc": "Témoin de l'accident"},
    {"code": "autre_conducteur", "label": "🚙 Autre conducteur", "desc": "Conducteur tiers"},
    {"code": "assureur_adverse", "label": "🏢 Assureur adverse", "desc": "Compagnie adverse"},
]

CIVILITES = ["M.", "Mme", "Mlle"]


# ============================================================
# DIALOGUE
# ============================================================

class TiersDialog(QDialog):
    """
    Dialogue d'ajout / modification de tiers
    
    Modes :
    - Création : tiers_data=None
    - Modification : tiers_data=dict existant
    """
    
    tiers_saved = Signal(dict)
    
    def __init__(
        self,
        sinistre_id: int,
        controller,
        user,
        tiers_data: Optional[Dict] = None,
        referentiel_controller=None,
        parent=None
    ):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.controller = controller
        self.user = user
        self.tiers_data = tiers_data
        self.referentiel_controller = referentiel_controller
        self.is_edit_mode = tiers_data is not None
        
        title = "Modifier un tiers" if self.is_edit_mode else "Ajouter un tiers"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(720, 780)
        self.setStyleSheet(STYLE_DIALOG)
        
        self._type_selected = None
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
        
        # Corps scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: #f8fafc;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(15)
        
        content_layout.addWidget(self._build_card_type())
        content_layout.addWidget(self._build_card_identite())
        content_layout.addWidget(self._build_card_coordonnees())
        content_layout.addWidget(self._build_card_assurance())
        content_layout.addWidget(self._build_card_complement())
        content_layout.addStretch()
        
        scroll.setWidget(content)
        root.addWidget(scroll, 1)
        
        # Pied
        root.addWidget(self._build_footer())
    
    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("Header")
        header.setStyleSheet(STYLE_HEADER)
        header.setFixedHeight(80)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(25, 15, 25, 15)
        
        # Icône
        icon = QLabel("✏️" if self.is_edit_mode else "➕")
        icon.setStyleSheet("font-size: 28px;")
        layout.addWidget(icon)
        
        # Titre
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title = QLabel("Modifier le tiers" if self.is_edit_mode else "Nouveau tiers")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        title_block.addWidget(title)
        
        subtitle = QLabel("Les champs marqués * sont obligatoires")
        subtitle.setStyleSheet("font-size: 11px; color: #64748b;")
        title_block.addWidget(subtitle)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        # Badge "Sinistre N°..."
        badge = QLabel(f"📄 Sinistre #{self.sinistre_id}")
        badge.setStyleSheet("""
            background-color: #e8f0fe;
            color: #1a73e8;
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        """)
        layout.addWidget(badge)
        
        return header
    
    # ---------- CARTE 1 : TYPE ----------
    
    def _build_card_type(self) -> QGroupBox:
        group = QGroupBox("🏷️ Type de tiers *")
        group.setStyleSheet(STYLE_GROUP)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Grille de boutons radio
        grid = QGridLayout()
        grid.setSpacing(10)
        
        self._type_buttons = []
        for i, t in enumerate(TYPES_TIERS):
            btn = QPushButton(t['label'])
            btn.setCheckable(True)
            btn.setStyleSheet(STYLE_TYPES_BTN)
            btn.setMinimumHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(t['desc'])
            btn.clicked.connect(lambda checked=False, code=t['code']: self._on_type_selected(code))
            grid.addWidget(btn, i // 3, i % 3)
            self._type_buttons.append((code := t['code'], btn))
        
        layout.addLayout(grid)
        
        # Champ de précision (optionnel)
        self.input_precision_type = QLineEdit()
        self.input_precision_type.setPlaceholderText("Précision (optionnel) : ex: conducteur du véhicule A")
        self.input_precision_type.setStyleSheet(STYLE_INPUT)
        layout.addWidget(self.input_precision_type)
        
        return group
    
    def _on_type_selected(self, code: str):
        """Gère la sélection du type"""
        self._type_selected = code
        for c, btn in self._type_buttons:
            btn.setChecked(c == code)
        self._update_completion()
    
    # ---------- CARTE 2 : IDENTITÉ ----------
    
    def _build_card_identite(self) -> QGroupBox:
        group = QGroupBox("👤 Identité")
        group.setStyleSheet(STYLE_GROUP)
        
        form = QFormLayout(group)
        form.setSpacing(12)
        form.setContentsMargins(15, 20, 15, 15)
        
        # Civilité + Nom + Prénom sur une ligne
        row_identite = QHBoxLayout()
        row_identite.setSpacing(10)
        
        self.input_civilite = QComboBox()
        self.input_civilite.addItem("—", None)
        for c in CIVILITES:
            self.input_civilite.addItem(c, c)
        self.input_civilite.setStyleSheet(STYLE_INPUT)
        self.input_civilite.setFixedWidth(80)
        row_identite.addWidget(self.input_civilite)
        
        self.input_nom = QLineEdit()
        self.input_nom.setPlaceholderText("Nom *")
        self.input_nom.setStyleSheet(STYLE_REQUIRED)
        self.input_nom.textChanged.connect(self._update_completion)
        row_identite.addWidget(self.input_nom, 1)
        
        self.input_prenom = QLineEdit()
        self.input_prenom.setPlaceholderText("Prénom")
        self.input_prenom.setStyleSheet(STYLE_INPUT)
        row_identite.addWidget(self.input_prenom, 1)
        
        form.addRow("Nom complet *:", row_identite)
        
        # Code tiers (optionnel)
        self.input_code_tiers = QLineEdit()
        self.input_code_tiers.setPlaceholderText("Référence interne (optionnel)")
        self.input_code_tiers.setStyleSheet(STYLE_INPUT)
        form.addRow("Code tiers:", self.input_code_tiers)
        
        # Date de naissance + Profession
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        self.input_date_naissance = QDateEdit()
        self.input_date_naissance.setDate(QDate(1990, 1, 1))
        self.input_date_naissance.setCalendarPopup(True)
        self.input_date_naissance.setStyleSheet(STYLE_INPUT)
        row2.addWidget(self.input_date_naissance, 1)
        
        self.input_profession = QLineEdit()
        self.input_profession.setPlaceholderText("Profession")
        self.input_profession.setStyleSheet(STYLE_INPUT)
        row2.addWidget(self.input_profession, 1)
        
        form.addRow("Naissance / Profession:", row2)
        
        return group
    
    # ---------- CARTE 3 : COORDONNÉES ----------
    
    def _build_card_coordonnees(self) -> QGroupBox:
        group = QGroupBox("📞 Coordonnées")
        group.setStyleSheet(STYLE_GROUP)
        
        form = QFormLayout(group)
        form.setSpacing(12)
        form.setContentsMargins(15, 20, 15, 15)
        
        # Téléphone + Email sur une ligne
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        self.input_telephone = QLineEdit()
        self.input_telephone.setPlaceholderText("Téléphone")
        self.input_telephone.setStyleSheet(STYLE_INPUT)
        self.input_telephone.textChanged.connect(self._update_completion)
        row1.addWidget(self.input_telephone, 1)
        
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Email")
        self.input_email.setStyleSheet(STYLE_INPUT)
        row1.addWidget(self.input_email, 1)
        
        form.addRow("Contact:", row1)
        
        # Adresse
        self.input_adresse = QLineEdit()
        self.input_adresse.setPlaceholderText("Adresse complète")
        self.input_adresse.setStyleSheet(STYLE_INPUT)
        form.addRow("Adresse:", self.input_adresse)
        
        # Code postal + Ville + Pays
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        self.input_code_postal = QLineEdit()
        self.input_code_postal.setPlaceholderText("Code postal")
        self.input_code_postal.setStyleSheet(STYLE_INPUT)
        self.input_code_postal.setFixedWidth(120)
        row2.addWidget(self.input_code_postal)
        
        self.input_ville = QLineEdit()
        self.input_ville.setPlaceholderText("Ville")
        self.input_ville.setStyleSheet(STYLE_INPUT)
        row2.addWidget(self.input_ville, 1)
        
        self.input_pays = QComboBox()
        self.input_pays.setStyleSheet(STYLE_INPUT)
        self.input_pays.addItem("Cameroun", "CM")
        self.input_pays.addItem("France", "FR")
        self.input_pays.addItem("Sénégal", "SN")
        self.input_pays.addItem("Côte d'Ivoire", "CI")
        self.input_pays.addItem("Autre", "AUTRE")
        row2.addWidget(self.input_pays, 1)
        
        form.addRow("Localisation:", row2)
        
        return group
    
    # ---------- CARTE 4 : ASSURANCE ----------
    
    def _build_card_assurance(self) -> QGroupBox:
        group = QGroupBox("🏢 Assurance du tiers")
        group.setStyleSheet(STYLE_GROUP)
        
        form = QFormLayout(group)
        form.setSpacing(12)
        form.setContentsMargins(15, 20, 15, 15)
        
        # Compagnie + N° police sur une ligne
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        self.input_assurance = QLineEdit()
        self.input_assurance.setPlaceholderText("Compagnie d'assurance")
        self.input_assurance.setStyleSheet(STYLE_INPUT)
        row1.addWidget(self.input_assurance, 1)
        
        self.input_police = QLineEdit()
        self.input_police.setPlaceholderText("N° police")
        self.input_police.setStyleSheet(STYLE_INPUT)
        row1.addWidget(self.input_police, 1)
        
        form.addRow("Assurance:", row1)
        
        # Info
        info = QLabel("ℹ️ Renseignez ces informations uniquement si le tiers est assuré (responsable ou victime).")
        info.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        info.setWordWrap(True)
        form.addRow("", info)
        
        return group
    
    # ---------- CARTE 5 : COMPLÉMENT ----------
    
    def _build_card_complement(self) -> QGroupBox:
        group = QGroupBox("📝 Informations complémentaires")
        group.setStyleSheet(STYLE_GROUP)
        
        form = QFormLayout(group)
        form.setSpacing(12)
        form.setContentsMargins(15, 20, 15, 15)
        
        self.input_observations = QTextEdit()
        self.input_observations.setPlaceholderText(
            "Observations, précisions sur l'implication du tiers, éléments à retenir..."
        )
        self.input_observations.setMaximumHeight(100)
        self.input_observations.setStyleSheet(STYLE_INPUT)
        form.addRow("Observations:", self.input_observations)
        
        return group
    
    # ---------- PIED ----------
    
    def _build_footer(self) -> QFrame:
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
        
        # Statut de complétion
        self.lbl_status = QLabel("📌 Champs obligatoires : Type et Nom")
        self.lbl_status.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(self.lbl_status)
        
        layout.addStretch()
        
        # Annuler
        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.setStyleSheet(STYLE_BTN_SECONDARY)
        self.btn_annuler.clicked.connect(self.reject)
        layout.addWidget(self.btn_annuler)
        
        # Enregistrer
        self.btn_save = QPushButton("💾  Enregistrer")
        self.btn_save.setStyleSheet(STYLE_BTN_PRIMARY)
        self.btn_save.setMinimumWidth(180)
        self.btn_save.clicked.connect(self.save)
        layout.addWidget(self.btn_save)
        
        return footer
    
    # ============================================================
    # PRÉ-REMPLISSAGE (édition)
    # ============================================================
    
    def _populate(self):
        """Pré-remplit le formulaire en mode édition"""
        d = self.tiers_data
        
        # Type
        type_code = (d.get('type_tiers') or '').lower()
        # Mapper les anciens libellés vers les nouveaux codes
        mapping = {
            'responsable': 'conducteur',
            'victime': 'victime',
            'temoin': 'temoin',
            'témoin': 'temoin',
            'assureur_adverse': 'assureur_adverse',
        }
        type_code = mapping.get(type_code, type_code)
        if type_code:
            self._on_type_selected(type_code)
        
        # Identité
        self.input_civilite.setCurrentText(d.get('civilite') or "—")
        self.input_nom.setText(d.get('nom', '') or '')
        self.input_prenom.setText(d.get('prenom', '') or '')
        self.input_code_tiers.setText(d.get('code_tiers', '') or '')
        
        if d.get('date_naissance'):
            try:
                date_str = str(d['date_naissance'])[:10]
                y, m, day = date_str.split('-')
                self.input_date_naissance.setDate(QDate(int(y), int(m), int(day)))
            except Exception:
                pass
        
        self.input_profession.setText(d.get('profession', '') or '')
        
        # Coordonnées
        self.input_telephone.setText(d.get('telephone', '') or '')
        self.input_email.setText(d.get('email', '') or '')
        self.input_adresse.setText(d.get('adresse', '') or '')
        self.input_code_postal.setText(d.get('code_postal', '') or '')
        self.input_ville.setText(d.get('ville', '') or '')
        
        pays = (d.get('pays') or '').lower()
        if pays:
            for i in range(self.input_pays.count()):
                if self.input_pays.itemText(i).lower() == pays:
                    self.input_pays.setCurrentIndex(i)
                    break
        
        # Assurance
        self.input_assurance.setText(d.get('assurance', '') or '')
        self.input_police.setText(d.get('police_assurance', '') or '')
        
        # Complément
        self.input_observations.setPlainText(d.get('observations', '') or '')
    
    # ============================================================
    # VALIDATION EN DIRECT
    # ============================================================
    
    def _update_completion(self):
        """Met à jour l'état de complétion du formulaire"""
        type_ok = bool(self._type_selected)
        nom_ok = bool(self.input_nom.text().strip())
        
        if type_ok and nom_ok:
            self.lbl_status.setText("✅ Formulaire prêt à être enregistré")
            self.lbl_status.setStyleSheet("color: #16a34a; font-size: 11px; font-weight: bold;")
            self.btn_save.setEnabled(True)
        else:
            missing = []
            if not type_ok:
                missing.append("Type")
            if not nom_ok:
                missing.append("Nom")
            self.lbl_status.setText(f"⚠️ Champs manquants : {', '.join(missing)}")
            self.lbl_status.setStyleSheet("color: #dc2626; font-size: 11px; font-weight: bold;")
            self.btn_save.setEnabled(False)
    
    # ============================================================
    # ENREGISTREMENT
    # ============================================================
    
    def save(self):
        """Valide et enregistre"""
        try:
            # ---- Validation finale ----
            if not self._type_selected:
                self._show_error("Veuillez sélectionner un type de tiers")
                return
            
            nom = self.input_nom.text().strip()
            if not nom:
                self._show_error("Le nom est obligatoire")
                return
            
            # ---- Construction des données ----
            date_naissance = self.input_date_naissance.date().toPython()
            
            data = {
                'type_tiers': self._type_selected,
                'code_tiers': self.input_code_tiers.text().strip() or None,
                'civilite': self.input_civilite.currentData(),
                'nom': nom,
                'prenom': self.input_prenom.text().strip() or None,
                'adresse': self.input_adresse.text().strip() or None,
                'code_postal': self.input_code_postal.text().strip() or None,
                'ville': self.input_ville.text().strip() or None,
                'pays': self.input_pays.currentText(),
                'telephone': self.input_telephone.text().strip() or None,
                'email': self.input_email.text().strip() or None,
                'assurance': self.input_assurance.text().strip() or None,
                'police_assurance': self.input_police.text().strip() or None,
                'date_naissance': date_naissance if date_naissance.year > 1900 else None,
                'profession': self.input_profession.text().strip() or None,
                'observations': self.input_observations.toPlainText().strip() or None,
            }
            
            # ---- Envoi au contrôleur ----
            if self.is_edit_mode:
                data['updated_by'] = self.user.id if self.user else None
                result = self.controller.update_tiers(self.tiers_data['id'], data)
                action = "modifié"
            else:
                data['created_by'] = self.user.id if self.user else None
                result = self.controller.ajouter_tiers(self.sinistre_id, data)
                action = "créé"
            
            if not result:
                self._show_error("Erreur lors de l'enregistrement")
                return
            
            # ---- Succès ----
            self.tiers_saved.emit(result)
            QMessageBox.information(
                self,
                "✅ Succès",
                f"Tiers {action} avec succès !\n\n"
                f"👤 {nom} {self.input_prenom.text()}".strip()
            )
            self.accept()
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._show_error(f"Erreur inattendue : {str(e)}")
    
    def _show_error(self, message: str):
        """Affiche une erreur dans le pied + popup"""
        self.lbl_status.setText(f"⚠️ {message}")
        self.lbl_status.setStyleSheet("color: #dc2626; font-size: 11px; font-weight: bold;")
        QMessageBox.warning(self, "Validation", message)