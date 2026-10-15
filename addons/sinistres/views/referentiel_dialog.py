"""
Dialogue d'ajout / modification d'un référentiel
Respecte les règles REF-001 à REF-007 du Tome 2 du CDC
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QMessageBox, QFrame, QCheckBox, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, Signal, QDate
from datetime import datetime


# ============================================================
# STYLES
# ============================================================

STYLE_DIALOG = """
    QDialog {
        background-color: #f8fafc;
    }
"""

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
        left: 10px;
        padding: 0 10px;
        color: #1e293b;
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
"""

STYLE_REQUIRED = """
    QLineEdit, QComboBox, QDateEdit {
        background-color: #fefce8;
        border: 1px solid #fde047;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        min-height: 20px;
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
        padding: 10px 28px;
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

STYLE_INFO_BOX = """
    QFrame {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
    }
    QLabel {
        color: #1e40af;
        font-size: 11px;
    }
"""


# ============================================================
# DIALOGUE
# ============================================================

class ReferentielDialog(QDialog):
    """
    Dialogue d'ajout/modification d'un référentiel.
    
    Modes :
    - Création : referentiel_data=None
    - Modification : referentiel_data=dict existant
    """
    
    referentiel_saved = Signal(dict)
    
    # Familles disponibles (issues du CDC Tome 2)
    FAMILLES = [
        # FAM-01
        ("sinistres_types", "Types de sinistres"),
        ("circonstances", "Circonstances"),
        ("responsabilites", "Responsabilités"),
        ("dommages", "Dommages"),
        ("types_evaluation", "Types d'évaluation"),
        ("qualite_chauffeur", "Qualité chauffeur"),
        ("types_sinistre_auto", "Types sinistre auto"),
        # FAM-02
        ("branches", "Branches"),
        ("garanties", "Garanties"),
        ("produits", "Produits"),
        ("types_resiliation", "Types de résiliation"),
        # FAM-03
        ("types_experts", "Types d'experts"),
        ("types_avocats", "Types d'avocats"),
        ("types_prestataires", "Types de prestataires"),
        # FAM-04
        ("pays", "Pays"),
        ("devises", "Devises"),
        ("types_documents", "Types de documents"),
        # FAM-05
        ("modes_paiement", "Modes de paiement"),
        ("modes_encaissement", "Modes d'encaissement"),
        ("operateurs_mobile", "Opérateurs mobile"),
        ("types_beneficiaires", "Types de bénéficiaires"),
        ("journaux_comptables", "Journaux comptables"),
        # FAM-06
        ("statuts_sinistre", "Statuts sinistre"),
        ("transitions_workflow", "Transitions workflow"),
        ("statuts_expertise", "Statuts expertise"),
        ("statuts_reglement", "Statuts règlement"),
        ("statuts_recours", "Statuts recours"),
        ("suites_a_donner", "Suites à donner"),
        ("actions_commerciales", "Actions commerciales"),
        # FAM-07
        ("origines_rappels", "Origines de rappels"),
        ("types_relances", "Types de relances"),
        ("priorites", "Priorités"),
    ]
    
    def __init__(self, controller, user, referentiel_data: dict = None, famille: str = None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.referentiel_data = referentiel_data  # None = création
        self.is_edit_mode = referentiel_data is not None
        self.default_famille = famille
        
        title = "Modifier un référentiel" if self.is_edit_mode else "Ajouter un référentiel"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(620)
        self.setMinimumHeight(650)
        self.setStyleSheet(STYLE_DIALOG)
        
        self.setup_ui()
        self._populate()
    
    # ============================================================
    # UI
    # ============================================================
    
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # ---------- En-tête ----------
        root.addWidget(self._build_header())
        
        # ---------- Corps scrollable ----------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: #f8fafc;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(15)
        
        # Carte 1 : Identification
        content_layout.addWidget(self._build_card_identification())
        
        # Carte 2 : Classification
        content_layout.addWidget(self._build_card_classification())
        
        # Carte 3 : Validité / Société
        content_layout.addWidget(self._build_card_validite())
        
        # Carte 4 : Données supplémentaires (JSON)
        content_layout.addWidget(self._build_card_extra())
        
        content_layout.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)
        
        # ---------- Pied ----------
        root.addWidget(self._build_footer())
    
    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("Header")
        header.setStyleSheet(STYLE_HEADER)
        header.setFixedHeight(75)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 12, 20, 12)
        
        # Icône + titre
        icon = QLabel("✏️" if self.is_edit_mode else "➕")
        icon.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon)
        
        title_block = QVBoxLayout()
        title_block.setSpacing(0)
        
        title = QLabel("Modifier le référentiel" if self.is_edit_mode else "Nouveau référentiel")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        title_block.addWidget(title)
        
        subtitle = QLabel("Tous les champs marqués * sont obligatoires")
        subtitle.setStyleSheet("font-size: 11px; color: #64748b;")
        title_block.addWidget(subtitle)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        return header
    
    def _build_card_identification(self) -> QGroupBox:
        group = QGroupBox("🔑 Identification")
        group.setStyleSheet(STYLE_GROUP)
        form = QFormLayout(group)
        form.setSpacing(12)
        form.setContentsMargins(15, 20, 15, 15)
        
        # Famille
        self.input_famille = QComboBox()
        self.input_famille.setStyleSheet(STYLE_REQUIRED)
        for code, libelle in self.FAMILLES:
            self.input_famille.addItem(libelle, code)
        form.addRow("Famille *:", self.input_famille)
        
        # Code
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Ex: RESP_100 (unique dans la famille)")
        self.input_code.setStyleSheet(STYLE_REQUIRED)
        form.addRow("Code *:", self.input_code)
        
        # Libellé
        self.input_libelle = QLineEdit()
        self.input_libelle.setPlaceholderText("Ex: Responsable 100%")
        self.input_libelle.setStyleSheet(STYLE_REQUIRED)
        form.addRow("Libellé *:", self.input_libelle)
        
        # Description
        self.input_description = QTextEdit()
        self.input_description.setPlaceholderText("Description détaillée (optionnel)")
        self.input_description.setMaximumHeight(70)
        self.input_description.setStyleSheet(STYLE_INPUT)
        form.addRow("Description:", self.input_description)
        
        return group
    
    def _build_card_classification(self) -> QGroupBox:
        group = QGroupBox("🏷️ Classification et valeurs")
        group.setStyleSheet(STYLE_GROUP)
        form = QFormLayout(group)
        form.setSpacing(12)
        form.setContentsMargins(15, 20, 15, 15)
        
        # Valeur numérique
        self.input_valeur = QDoubleSpinBox()
        self.input_valeur.setRange(-999999.99, 999999.99)
        self.input_valeur.setDecimals(4)
        self.input_valeur.setSingleStep(0.1)
        self.input_valeur.setStyleSheet(STYLE_INPUT)
        self.input_valeur.setSpecialValueText("—")
        form.addRow("Valeur numérique:", self.input_valeur)
        
        # Aide contextuelle
        info_valeur = QLabel("💡 Exemples : 1.0 pour 100%, 0.5 pour 50%, 7 pour 7 jours")
        info_valeur.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        form.addRow("", info_valeur)
        
        return group
    
    def _build_card_validite(self) -> QGroupBox:
        group = QGroupBox("📅 Validité et périmètre")
        group.setStyleSheet(STYLE_GROUP)
        form = QFormLayout(group)
        form.setSpacing(12)
        form.setContentsMargins(15, 20, 15, 15)
        
        # Date d'effet
        self.input_date_effet = QDateEdit()
        self.input_date_effet.setDate(QDate.currentDate())
        self.input_date_effet.setCalendarPopup(True)
        self.input_date_effet.setStyleSheet(STYLE_REQUIRED)
        form.addRow("Date d'effet *:", self.input_date_effet)
        
        # Date de fin
        self.input_date_fin = QDateEdit()
        self.input_date_fin.setDate(QDate.currentDate().addYears(10))
        self.input_date_fin.setCalendarPopup(True)
        self.input_date_fin.setStyleSheet(STYLE_INPUT)
        form.addRow("Date de fin:", self.input_date_fin)
        
        # Société
        self.input_societe = QLineEdit()
        self.input_societe.setPlaceholderText("Ex: LOMETA SA (multi-sociétés - REF-007)")
        self.input_societe.setStyleSheet(STYLE_INPUT)
        form.addRow("Société:", self.input_societe)
        
        # Branche
        self.input_branche = QLineEdit()
        self.input_branche.setPlaceholderText("Ex: AUTO, RC, INCENDIE (optionnel)")
        self.input_branche.setStyleSheet(STYLE_INPUT)
        form.addRow("Branche:", self.input_branche)
        
        # Actif
        self.check_actif = QCheckBox("Référentiel actif")
        self.check_actif.setChecked(True)
        self.check_actif.setStyleSheet("font-size: 13px;")
        form.addRow("Statut:", self.check_actif)
        
        # Info REF-003
        info = QLabel("ℹ️ Règle REF-003 : la suppression physique est interdite. Utilisez la désactivation.")
        info.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        form.addRow("", info)
        
        return group
    
    def _build_card_extra(self) -> QGroupBox:
        group = QGroupBox("📦 Données supplémentaires (JSON, optionnel)")
        group.setStyleSheet(STYLE_GROUP)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        
        self.input_extra = QTextEdit()
        self.input_extra.setPlaceholderText('{"clé": "valeur"} — laisser vide si non utilisé')
        self.input_extra.setMaximumHeight(80)
        self.input_extra.setStyleSheet(STYLE_INPUT)
        layout.addWidget(self.input_extra)
        
        info = QLabel("💡 Utile pour stocker des métadonnées propres à une famille.")
        info.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        layout.addWidget(info)
        
        return group
    
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
        
        # Info
        self.lbl_info = QLabel("📌 Tous les champs marqués * sont obligatoires")
        self.lbl_info.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(self.lbl_info)
        
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
    # PRÉ-REMPLISSAGE
    # ============================================================
    
    def _populate(self):
        """Pré-remplit le formulaire"""
        if self.is_edit_mode and self.referentiel_data:
            data = self.referentiel_data
            
            # Famille
            if data.get('famille'):
                idx = self.input_famille.findData(data['famille'])
                if idx >= 0:
                    self.input_famille.setCurrentIndex(idx)
            
            # Code (non modifiable en édition pour respecter REF-002)
            self.input_code.setText(data.get('code', ''))
            self.input_code.setReadOnly(True)
            self.input_code.setStyleSheet("""
                background-color: #f1f5f9;
                color: #64748b;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            """)
            self.input_code.setToolTip("Le code n'est pas modifiable (REF-002)")
            
            # Libellé
            self.input_libelle.setText(data.get('libelle', ''))
            
            # Description
            self.input_description.setPlainText(data.get('description', '') or '')
            
            # Valeur
            if data.get('valeur') is not None:
                self.input_valeur.setValue(float(data['valeur']))
            else:
                self.input_valeur.setValue(0)
            
            # Dates
            if data.get('date_effet'):
                self._set_date(self.input_date_effet, data['date_effet'])
            if data.get('date_fin'):
                self._set_date(self.input_date_fin, data['date_fin'])
            
            # Société / Branche
            self.input_societe.setText(data.get('societe', '') or '')
            self.input_branche.setText(data.get('branche', '') or '')
            
            # Actif
            self.check_actif.setChecked(bool(data.get('est_actif', True)))
            
            # Extra
            extra = data.get('donnees_supplementaires')
            if extra:
                import json
                try:
                    self.input_extra.setPlainText(
                        json.dumps(extra, ensure_ascii=False, indent=2)
                        if isinstance(extra, (dict, list))
                        else str(extra)
                    )
                except Exception:
                    self.input_extra.setPlainText(str(extra))
        
        else:
            # Création : pré-sélectionner la famille si fournie
            if self.default_famille:
                idx = self.input_famille.findData(self.default_famille)
                if idx >= 0:
                    self.input_famille.setCurrentIndex(idx)
            
            # Valeur par défaut
            self.input_valeur.setValue(0)
    
    def _set_date(self, widget: QDateEdit, iso_str: str):
        """Positionne une date à partir d'une chaîne ISO"""
        try:
            if isinstance(iso_str, datetime):
                dt = iso_str
            else:
                s = str(iso_str)
                if 'T' in s:
                    s = s.split('T')[0]
                y, m, d = s.split('-')
                widget.setDate(QDate(int(y), int(m), int(d)))
                return
            widget.setDate(QDate(dt.year, dt.month, dt.day))
        except Exception:
            pass
    
    # ============================================================
    # SAUVEGARDE
    # ============================================================
    
    def save(self):
        """Valide et enregistre le référentiel"""
        try:
            # ---------- Validation ----------
            code = self.input_code.text().strip().upper()
            libelle = self.input_libelle.text().strip()
            famille = self.input_famille.currentData()
            
            if not famille:
                self._error("Veuillez sélectionner une famille")
                return
            
            if not code:
                self._error("Le code est obligatoire")
                return
            
            # Validation du code : majuscules, chiffres, tirets, underscores
            import re
            if not re.match(r'^[A-Z0-9_\-]+$', code):
                self._error("Le code doit contenir uniquement des majuscules, chiffres, tirets ou underscores")
                return
            
            if not libelle:
                self._error("Le libellé est obligatoire")
                return
            
            if len(libelle) < 3:
                self._error("Le libellé doit contenir au moins 3 caractères")
                return
            
            # Validation des dates
            date_effet = self.input_date_effet.date().toPython()
            date_fin = self.input_date_fin.date().toPython()
            
            if date_fin and date_fin < date_effet:
                self._error("La date de fin ne peut pas être antérieure à la date d'effet")
                return
            
            # Validation JSON
            extra = None
            extra_text = self.input_extra.toPlainText().strip()
            if extra_text:
                import json
                try:
                    extra = json.loads(extra_text)
                except json.JSONDecodeError as e:
                    self._error(f"JSON invalide : {str(e)}")
                    return
            
            # ---------- Construction des données ----------
            data = {
                'famille': famille,
                'code': code,
                'libelle': libelle,
                'description': self.input_description.toPlainText().strip() or None,
                'valeur': self.input_valeur.value() if self.input_valeur.value() != 0 else None,
                'date_effet': date_effet,
                'date_fin': date_fin if date_fin else None,
                'societe': self.input_societe.text().strip() or None,
                'branche': self.input_branche.text().strip() or None,
                'est_actif': self.check_actif.isChecked(),
                'donnees_supplementaires': extra,
                'updated_by': self.user.id if self.user else None,
            }
            
            # ---------- Envoi au contrôleur ----------
            if self.is_edit_mode:
                # Modification
                data['updated_by'] = self.user.id if self.user else None
                result = self.controller.update_referentiel(
                    self.referentiel_data['id'], data
                )
                action = "modifié"
            else:
                # Création
                data['created_by'] = self.user.id if self.user else None
                result = self.controller.creer_referentiel(data)
                action = "créé"
            
            if not result:
                self._error("Erreur lors de l'enregistrement")
                return
            
            # ---------- Succès ----------
            self.referentiel_saved.emit(result)
            QMessageBox.information(
                self,
                "✅ Succès",
                f"Référentiel {action} avec succès !\n\n"
                f"📁 Famille : {famille}\n"
                f"🔑 Code : {code}\n"
                f"🏷️ Libellé : {libelle}"
            )
            self.accept()
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._error(f"Erreur inattendue : {str(e)}")
    
    def _error(self, message: str):
        """Affiche une erreur"""
        self.lbl_info.setText(f"⚠️ {message}")
        self.lbl_info.setStyleSheet("color: #dc2626; font-size: 11px; font-weight: bold;")
        QMessageBox.warning(self, "Validation", message)