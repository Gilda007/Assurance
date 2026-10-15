"""
Dialogue de création d'évaluation avec calcul automatique du montant net
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor

from datetime import datetime
import qtawesome as qta


class EvaluationDialog(QDialog):
    """Dialogue de création d'évaluation avec calcul automatique"""
    
    evaluation_created = Signal(dict)
    
    def __init__(self, sinistre_id, evaluation_controller, user, sinistre_info=None, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.evaluation_controller = evaluation_controller
        self.user = user
        self.sinistre_info = sinistre_info or {}
        
        self.setWindowTitle("Créer une évaluation")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # ============================================================
        # EN-TÊTE AVEC INFOS SINISTRE
        # ============================================================
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #e2e8f0;
            }
            QLabel {
                color: #1e293b;
                font-size: 12px;
            }
            QLabel.title {
                font-weight: bold;
                font-size: 14px;
                color: #1a73e8;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("💰 Création d'évaluation")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        
        self.lbl_sinistre = QLabel(f"Sinistre: {self.sinistre_info.get('numero_sinistre', 'N/A')}")
        info_layout.addWidget(self.lbl_sinistre)
        
        self.lbl_client = QLabel(f"Client: {self.sinistre_info.get('client_nom', 'N/A')}")
        info_layout.addWidget(self.lbl_client)
        
        self.lbl_branche = QLabel(f"Branche: {self.sinistre_info.get('branche', 'N/A')}")
        info_layout.addWidget(self.lbl_branche)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        layout.addWidget(header_frame)
        
        # ============================================================
        # SECTION 1: INFORMATIONS DE L'ÉVALUATION
        # ============================================================
        form_group = QGroupBox("Informations de l'évaluation")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(12)
        
        # Type d'évaluation
        self.input_type = QComboBox()
        self.input_type.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_type.addItems([
            "auto_materiel",
            "auto_corporel",
            "incendie",
            "vol",
            "degats_eau",
            "rc_generale",
            "defense_recours",
            "transport_marchandises",
            "transport_conteneurs"
        ])
        form_layout.addRow("Type d'évaluation *:", self.input_type)
        
        # Catégorie (optionnel)
        self.input_categorie = QLineEdit()
        self.input_categorie.setPlaceholderText("Ex: Véhicule, Bâtiment... (optionnel)")
        self.input_categorie.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Catégorie:", self.input_categorie)
        
        layout.addWidget(form_group)
        
        # ============================================================
        # SECTION 2: CALCUL DU MONTANT
        # ============================================================
        calc_group = QGroupBox("Calcul du montant")
        calc_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        calc_layout = QFormLayout(calc_group)
        calc_layout.setSpacing(12)
        
        # Montant brut
        self.input_montant_brut = QDoubleSpinBox()
        self.input_montant_brut.setRange(0, 999999999)
        self.input_montant_brut.setPrefix("FCFA ")
        self.input_montant_brut.setDecimals(0)
        self.input_montant_brut.setSingleStep(10000)
        self.input_montant_brut.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        self.input_montant_brut.valueChanged.connect(self.calculer_net)
        calc_layout.addRow("Montant brut *:", self.input_montant_brut)
        
        # Franchise
        self.input_franchise = QDoubleSpinBox()
        self.input_franchise.setRange(0, 999999999)
        self.input_franchise.setPrefix("FCFA ")
        self.input_franchise.setDecimals(0)
        self.input_franchise.setSingleStep(5000)
        self.input_franchise.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_franchise.valueChanged.connect(self.calculer_net)
        calc_layout.addRow("Franchise:", self.input_franchise)
        
        # Taux de responsabilité
        self.input_taux = QDoubleSpinBox()
        self.input_taux.setRange(0, 100)
        self.input_taux.setSuffix("%")
        self.input_taux.setValue(100)
        self.input_taux.setSingleStep(5)
        self.input_taux.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_taux.valueChanged.connect(self.calculer_net)
        calc_layout.addRow("Taux responsabilité:", self.input_taux)
        
        # Résultat
        result_frame = QFrame()
        result_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 6px;
                padding: 10px;
            }
            QLabel {
                color: #0369a1;
                font-size: 14px;
            }
            QLabel.value {
                font-weight: bold;
                font-size: 18px;
                color: #1a73e8;
            }
        """)
        result_layout = QVBoxLayout(result_frame)
        
        self.lbl_net = QLabel("Montant net: 0 FCFA")
        self.lbl_net.setStyleSheet("font-weight: bold; font-size: 18px; color: #1a73e8;")
        self.lbl_net.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(self.lbl_net)
        
        # Formule affichée
        self.lbl_formule = QLabel("Formule: (Brut - Franchise) × Taux")
        self.lbl_formule.setStyleSheet("color: #64748b; font-size: 11px;")
        self.lbl_formule.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(self.lbl_formule)
        
        calc_layout.addRow("", result_frame)
        
        layout.addWidget(calc_group)
        
        # ============================================================
        # SECTION 3: DÉTAILS
        # ============================================================
        self.input_details = QTextEdit()
        self.input_details.setPlaceholderText("Détails de l'évaluation, justifications...")
        self.input_details.setMaximumHeight(80)
        self.input_details.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px;")
        layout.addWidget(QLabel("Détails:"))
        layout.addWidget(self.input_details)
        
        # ============================================================
        # SECTION 4: RÉCAPITULATIF
        # ============================================================
        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 8px;
                padding: 12px;
            }
            QLabel {
                color: #0369a1;
                font-size: 12px;
            }
            QLabel.title {
                font-weight: bold;
                font-size: 13px;
            }
        """)
        summary_layout = QVBoxLayout(self.summary_frame)
        
        summary_title = QLabel("📋 Récapitulatif de l'évaluation")
        summary_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #0369a1;")
        summary_layout.addWidget(summary_title)
        
        self.summary_text = QLabel("Remplissez les champs pour voir le récapitulatif")
        self.summary_text.setStyleSheet("color: #0369a1;")
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(self.summary_frame)
        
        # ============================================================
        # BOUTONS
        # ============================================================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                border-radius: 8px;
                font-weight: bold;
                background-color: #f1f5f9;
                color: #64748b;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.btn_annuler.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_annuler)
        
        self.btn_creer = QPushButton("✅ Créer l'évaluation")
        self.btn_creer.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 10px 40px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_creer.clicked.connect(self.creer_evaluation)
        btn_layout.addWidget(self.btn_creer)
        
        layout.addLayout(btn_layout)
        
        # ============================================================
        # CONNEXIONS
        # ============================================================
        self.input_type.currentIndexChanged.connect(self._update_summary)
        self.input_categorie.textChanged.connect(self._update_summary)
        self.input_montant_brut.valueChanged.connect(self._update_summary)
        self.input_franchise.valueChanged.connect(self._update_summary)
        self.input_taux.valueChanged.connect(self._update_summary)
        self.input_details.textChanged.connect(self._update_summary)

    def load_data(self):
        """Charge les données initiales"""
        self.calculer_net()
        self._update_summary()
    
    def calculer_net(self):
        """Calcule le montant net automatiquement"""
        brut = self.input_montant_brut.value()
        franchise = self.input_franchise.value()
        taux = self.input_taux.value() / 100
        net = brut - franchise
        self.lbl_net.setText(f"Montant net: {net:,.0f} FCFA")
        self._net_calcule = net
        return net
    
    def _update_summary(self):
        """Met à jour le récapitulatif"""
        lines = []
        
        # Type
        type_text = self.input_type.currentText()
        if type_text:
            lines.append(f"📌 Type: {type_text.replace('_', ' ').title()}")
        
        # Catégorie
        categorie = self.input_categorie.text().strip()
        if categorie:
            lines.append(f"📂 Catégorie: {categorie}")
        
        # Montants
        brut = self.input_montant_brut.value()
        franchise = self.input_franchise.value()
        taux = self.input_taux.value()
        net = self.calculer_net()
        
        if brut > 0:
            lines.append(f"💰 Brut: {brut:,.0f} FCFA")
            lines.append(f"📉 Franchise: {franchise:,.0f} FCFA")
            lines.append(f"📊 Taux: {taux:.0f}%")
            lines.append(f"✅ Net: {net:,.0f} FCFA")
        else:
            lines.append("⚠️ Montant brut non défini")
        
        # Détails
        details = self.input_details.toPlainText().strip()
        if details:
            lines.append(f"📝 Détails: {details[:50]}...")
        
        self.summary_text.setText("\n".join(lines))

    def _filtrer_beneficiaires(self):
        """Filtre les bénéficiaires selon le type."""
        type_filtre = self.input_type.currentData()
        current = self.input_type.currentData()
        
        self.input_type.blockSignals(True)
        self.input_type.clear()
        self.input_type.addItem("-- Sélectionner un bénéficiaire --", None)
        
        for b in getattr(self, '_tous_beneficiaires', []):
            source = b.get('source', '')
            type_b = b.get('type_beneficiaire', 'AUTRE')
            
            # ✅ Filtre par source
            if type_filtre == 'BENEFICIAIRE':
                if source != 'BENEFICIAIRE':
                    continue
            elif type_filtre == 'TIERS':
                if source != 'TIERS':
                    continue
            elif type_filtre == 'EXPERT':
                if source != 'EXPERT':
                    continue
            elif type_filtre:
                # Filtre par type_beneficiaire exact
                if type_b != type_filtre:
                    continue
            
            display = self._format_beneficiaire_display(b)
            icon = self._get_beneficiaire_icon(b)
            self.input_type.addItem(icon, display, b)
        
        self.input_type.blockSignals(False)
        
        # Restaurer la sélection
        if current:
            for i in range(self.input_type.count()):
                if self.input_type.itemData(i) == current:
                    self.input_type.setCurrentIndex(i)
                    break
        
        self._update_summary()

    def _charger_beneficiaires(self):
        """Charge TOUS les bénéficiaires possibles (bénéficiaires + tiers + experts)."""
        try:
            # ✅ Appel unifié (3 sources)
            self._tous_beneficiaires = self.reglement_controller.get_beneficiaires()
            
            # Statistiques
            nb_benefs = sum(1 for b in self._tous_beneficiaires if b.get('source') == 'BENEFICIAIRE')
            nb_tiers = sum(1 for b in self._tous_beneficiaires if b.get('source') == 'TIERS')
            nb_experts = sum(1 for b in self._tous_beneficiaires if b.get('source') == 'EXPERT')
            
            print(f"📋 {len(self._tous_beneficiaires)} bénéficiaire(s) : "
                f"{nb_benefs} bénéficiaires, {nb_tiers} tiers, {nb_experts} experts")
            
            # Remplir le combo
            self.input_type.blockSignals(True)
            self.input_type.clear()
            self.input_type.addItem(
                "-- Sélectionner un bénéficiaire --", None
            )
            
            for b in self._tous_beneficiaires:
                display = self._format_beneficiaire_display(b)
                icon = self._get_beneficiaire_icon(b)
                self.input_type.addItem(icon, display, b)
            
            self.input_type.blockSignals(False)
        
        except Exception as e:
            print(f"❌ Erreur chargement bénéficiaires : {e}")
            import traceback
            traceback.print_exc()

    def _format_beneficiaire_display(self, b: dict) -> str:
        """Formate l'affichage d'un bénéficiaire."""
        nom_complet = b.get('nom_complet') or 'Sans nom'
        type_ben = b.get('type_beneficiaire') or 'AUTRE'
        source = b.get('source', '')
        is_benef = b.get('is_beneficiaire', False)
        
        # ✅ Suffixe pour distinguer la source
        if source == 'BENEFICIAIRE':
            suffix = "  ✓"   # déjà enregistré
        elif source == 'TIERS':
            suffix = "  (tiers)"   # à créer si utilisé
        elif source == 'EXPERT':
            suffix = "  (expert)"
        else:
            suffix = ""
        
        infos = []
        if b.get('telephone'):
            infos.append(b['telephone'])
        elif b.get('portable'):
            infos.append(b['portable'])
        
        if b.get('agrement'):
            infos.append(f"Agrément: {b['agrement']}")
        
        info_str = f"  ·  {'  ·  '.join(infos)}" if infos else ""
        
        return f"{nom_complet}  ({type_ben}){suffix}{info_str}"

    def _get_beneficiaire_icon(self, b: dict):
        """Icône FontAwesome selon la source."""
        source = b.get('source', '')
        type_ben = b.get('type_beneficiaire', '')
        
        # Priorité : source d'abord
        if source == 'BENEFICIAIRE':
            return qta.icon('fa5s.check-circle', color='#16a34a')
        elif source == 'TIERS':
            return qta.icon('fa5s.user-friends', color='#2563eb')
        elif source == 'EXPERT':
            return qta.icon('fa5s.user-tie', color='#7c3aed')
        
        # Fallback : type
        icon_map = {
            'ASSURE': 'fa5s.user',
            'GARAGE': 'fa5s.wrench',
            'AVOCAT': 'fa5s.gavel',
            'HOPITAL': 'fa5s.hospital',
        }
        icon_name = icon_map.get(type_ben, 'fa5s.user-circle')
        return qta.icon(icon_name, color='#64748b')
    
    def creer_evaluation(self):
        """Crée l'évaluation"""
        try:
            # ============================================================
            # VALIDATION
            # ============================================================
            
            # Vérifier le type
            if not self.input_type.currentText():
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un type d'évaluation")
                return
            
            # Vérifier le montant brut
            brut = self.input_montant_brut.value()
            if brut <= 0:
                QMessageBox.warning(self, "Validation", "Veuillez saisir un montant brut valide")
                return
            
            # Vérifier que le taux est valide
            taux = self.input_taux.value()
            if taux < 0 or taux > 100:
                QMessageBox.warning(self, "Validation", "Le taux de responsabilité doit être entre 0 et 100%")
                return
            
            # ============================================================
            # CONSTRUCTION DES DONNÉES
            # ============================================================
            data = {
                'sinistre_id': self.sinistre_id,
                'type_evaluation': self.input_type.currentText(),
                'categorie': self.input_categorie.text().strip() or None,
                'montant_brut': brut,
                'franchise': self.input_franchise.value(),
                'taux_responsabilite': taux / 100,
                'details': self.input_details.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            # ============================================================
            # ENVOI
            # ============================================================
            print(f"📝 Création évaluation avec les données: {data}")
            
            result = self.evaluation_controller.creer_evaluation(data)
            
            if result:
                self.evaluation_created.emit(result)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"✅ Évaluation créée avec succès !\n\n"
                    f"📌 N° Évaluation: {result.get('numero_evaluation', 'N/A')}\n"
                    f"💰 Montant brut: {brut:,.0f} FCFA\n"
                    f"✅ Montant net: {self._net_calcule:,.0f} FCFA\n"
                    f"📌 Type: {data['type_evaluation'].replace('_', ' ').title()}\n\n"
                    f"💡 Une provision a été créée automatiquement."
                )
                self.accept()
            
        except Exception as e:
            print(f"❌ Erreur création évaluation: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")