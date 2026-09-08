"""
Dialogue de création de règlement avec sélection de bénéficiaire
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QFrame, QCheckBox,
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor

from datetime import datetime


class ReglementDialog(QDialog):
    """Dialogue de création de règlement"""
    
    reglement_created = Signal(dict)
    
    def __init__(self, sinistre_id, reglement_controller, user, sinistre_info=None, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.reglement_controller = reglement_controller
        self.user = user
        self.sinistre_info = sinistre_info or {}
        self.evaluations = []
        
        self.setWindowTitle("Créer un règlement")
        self.setModal(True)
        self.setMinimumWidth(650)
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
        
        title = QLabel("💳 Création de règlement")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        
        self.lbl_sinistre = QLabel(f"Sinistre: {self.sinistre_info.get('numero_sinistre', 'N/A')}")
        info_layout.addWidget(self.lbl_sinistre)
        
        self.lbl_client = QLabel(f"Client: {self.sinistre_info.get('client_nom', 'N/A')}")
        info_layout.addWidget(self.lbl_client)
        
        self.lbl_montant_dispo = QLabel(f"💰 Montant disponible: 0 FCFA")
        self.lbl_montant_dispo.setStyleSheet("font-weight: bold; color: #1a73e8;")
        info_layout.addWidget(self.lbl_montant_dispo)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        layout.addWidget(header_frame)
        
        # ============================================================
        # SECTION 1: INFORMATIONS DU RÈGLEMENT
        # ============================================================
        form_group = QGroupBox("Informations du règlement")
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
        
        # Bénéficiaire (avec recherche)
        self.input_beneficiaire = QComboBox()
        self.input_beneficiaire.setEditable(True)
        self.input_beneficiaire.setPlaceholderText("Rechercher un bénéficiaire...")
        self.input_beneficiaire.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        self.input_beneficiaire.addItem("-- Sélectionner un bénéficiaire --", None)
        form_layout.addRow("Bénéficiaire *:", self.input_beneficiaire)
        
        # Type de bénéficiaire (filtre)
        self.input_type_beneficiaire = QComboBox()
        self.input_type_beneficiaire.addItem("Tous", None)
        self.input_type_beneficiaire.addItem("Assuré", "ASSURE")
        self.input_type_beneficiaire.addItem("Tiers", "TIERS")
        self.input_type_beneficiaire.addItem("Expert", "EXPERT")
        self.input_type_beneficiaire.addItem("Garage", "GARAGE")
        self.input_type_beneficiaire.addItem("Avocat", "AVOCAT")
        self.input_type_beneficiaire.currentIndexChanged.connect(self._filtrer_beneficiaires)
        form_layout.addRow("Type bénéficiaire:", self.input_type_beneficiaire)
        
        # Évaluation associée
        self.input_evaluation = QComboBox()
        self.input_evaluation.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_evaluation.addItem("-- Sélectionner une évaluation --", None)
        self.input_evaluation.currentIndexChanged.connect(self._on_evaluation_changed)
        form_layout.addRow("Évaluation associée:", self.input_evaluation)
        
        # Montant
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999999999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        self.input_montant.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        form_layout.addRow("Montant *:", self.input_montant)
        
        # Type de paiement
        self.input_type_paiement = QComboBox()
        self.input_type_paiement.addItems(["CHEQUE", "VIREMENT", "MOBILE_MONEY"])
        self.input_type_paiement.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_type_paiement.currentIndexChanged.connect(self._on_type_paiement_changed)
        form_layout.addRow("Type paiement:", self.input_type_paiement)
        
        layout.addWidget(form_group)
        
        # ============================================================
        # SECTION 2: DÉTAILS DU PAIEMENT (selon le type)
        # ============================================================
        self.paiement_details_group = QGroupBox("Détails du paiement")
        self.paiement_details_group.setStyleSheet("""
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
        self.paiement_details_group.hide()
        
        details_layout = QFormLayout(self.paiement_details_group)
        details_layout.setSpacing(12)
        
        # Pour CHÈQUE
        self.input_cheque_numero = QLineEdit()
        self.input_cheque_numero.setPlaceholderText("Numéro du chèque")
        self.input_cheque_numero.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        details_layout.addRow("Numéro chèque:", self.input_cheque_numero)
        
        self.input_cheque_banque = QLineEdit()
        self.input_cheque_banque.setPlaceholderText("Banque émettrice")
        self.input_cheque_banque.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        details_layout.addRow("Banque émettrice:", self.input_cheque_banque)
        
        # Pour VIREMENT
        self.input_virement_ref = QLineEdit()
        self.input_virement_ref.setPlaceholderText("Référence du virement")
        self.input_virement_ref.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        details_layout.addRow("Référence virement:", self.input_virement_ref)
        
        # Pour MOBILE_MONEY
        self.input_mobile_numero = QLineEdit()
        self.input_mobile_numero.setPlaceholderText("Numéro Mobile Money")
        self.input_mobile_numero.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        details_layout.addRow("Numéro mobile:", self.input_mobile_numero)
        
        self.input_mobile_operateur = QComboBox()
        self.input_mobile_operateur.addItems(["ORANGE", "MTN", "NEXTTEL", "CAMTEL"])
        self.input_mobile_operateur.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        details_layout.addRow("Opérateur:", self.input_mobile_operateur)
        
        layout.addWidget(self.paiement_details_group)
        
        # ============================================================
        # SECTION 3: OBSERVATIONS
        # ============================================================
        self.input_observations = QTextEdit()
        self.input_observations.setPlaceholderText("Observations...")
        self.input_observations.setMaximumHeight(80)
        self.input_observations.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px;")
        layout.addWidget(QLabel("Observations:"))
        layout.addWidget(self.input_observations)
        
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
        
        summary_title = QLabel("📋 Récapitulatif du règlement")
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
        
        self.btn_creer = QPushButton("✅ Créer le règlement")
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
        self.btn_creer.clicked.connect(self.creer_reglement)
        btn_layout.addWidget(self.btn_creer)
        
        layout.addLayout(btn_layout)
        
        # ============================================================
        # CONNEXIONS
        # ============================================================
        self.input_beneficiaire.currentIndexChanged.connect(self._update_summary)
        self.input_evaluation.currentIndexChanged.connect(self._update_summary)
        self.input_montant.valueChanged.connect(self._update_summary)
        self.input_type_paiement.currentIndexChanged.connect(self._update_summary)
        self.input_observations.textChanged.connect(self._update_summary)
    
    def load_data(self):
        """Charge les données initiales"""
        try:
            # Charger les bénéficiaires
            self._charger_beneficiaires()
            
            # Charger les évaluations validées du sinistre
            self._charger_evaluations()
            
        except Exception as e:
            print(f"Erreur chargement données: {e}")
    
    def _charger_beneficiaires(self):
        """Charge la liste des bénéficiaires"""
        try:
            beneficiaires = self.reglement_controller.get_beneficiaires()
            for b in beneficiaires:
                display = f"{b.get('nom', '')} {b.get('prenom', '')}".strip()
                if b.get('type_beneficiaire'):
                    display += f" ({b.get('type_beneficiaire')})"
                self.input_beneficiaire.addItem(display, b)
        except Exception as e:
            print(f"Erreur chargement bénéficiaires: {e}")
    
    def _filtrer_beneficiaires(self):
        """Filtre les bénéficiaires par type"""
        type_filtre = self.input_type_beneficiaire.currentData()
        
        for i in range(self.input_beneficiaire.count()):
            data = self.input_beneficiaire.itemData(i)
            if data and type_filtre:
                if data.get('type_beneficiaire') == type_filtre:
                    self.input_beneficiaire.setItemData(i, True, Qt.UserRole + 1)
                else:
                    self.input_beneficiaire.setItemData(i, False, Qt.UserRole + 1)
            else:
                self.input_beneficiaire.setItemData(i, True, Qt.UserRole + 1)
    
    def _charger_evaluations(self):
        """Charge les évaluations validées du sinistre"""
        try:
            self.evaluations = self.reglement_controller.get_evaluations_by_sinistre(self.sinistre_id)
            self.input_evaluation.clear()
            self.input_evaluation.addItem("-- Sélectionner une évaluation --", None)
            
            total_disponible = 0
            for ev in self.evaluations:
                if ev.get('est_validee'):
                    display = f"{ev.get('numero_evaluation')} - {ev.get('montant_net', 0):,.0f} FCFA"
                    self.input_evaluation.addItem(display, ev)
                    total_disponible += ev.get('montant_net', 0)
            
            self.lbl_montant_dispo.setText(f"💰 Montant disponible: {total_disponible:,.0f} FCFA")
            
        except Exception as e:
            print(f"Erreur chargement évaluations: {e}")
    
    def _on_evaluation_changed(self):
        """Met à jour le montant maximum selon l'évaluation sélectionnée"""
        evaluation = self.input_evaluation.currentData()
        if evaluation:
            self.input_montant.setMaximum(evaluation.get('montant_net', 0))
            self.input_montant.setValue(evaluation.get('montant_net', 0))
        else:
            self.input_montant.setMaximum(999999999)
    
    def _on_type_paiement_changed(self):
        """Affiche les détails selon le type de paiement"""
        type_paiement = self.input_type_paiement.currentText()
        
        # Cacher tous les champs
        self.input_cheque_numero.hide()
        self.input_cheque_banque.hide()
        self.input_virement_ref.hide()
        self.input_mobile_numero.hide()
        self.input_mobile_operateur.hide()
        
        # Afficher les champs appropriés
        if type_paiement == "CHEQUE":
            self.input_cheque_numero.show()
            self.input_cheque_banque.show()
            self.paiement_details_group.show()
        elif type_paiement == "VIREMENT":
            self.input_virement_ref.show()
            self.paiement_details_group.show()
        elif type_paiement == "MOBILE_MONEY":
            self.input_mobile_numero.show()
            self.input_mobile_operateur.show()
            self.paiement_details_group.show()
        else:
            self.paiement_details_group.hide()
        
        self._update_summary()
    
    def _update_summary(self):
        """Met à jour le récapitulatif"""
        lines = []
        
        # Bénéficiaire
        beneficiaire = self.input_beneficiaire.currentData()
        if beneficiaire:
            nom = f"{beneficiaire.get('nom', '')} {beneficiaire.get('prenom', '')}".strip()
            lines.append(f"👤 Bénéficiaire: {nom} ({beneficiaire.get('type_beneficiaire', 'N/A')})")
        else:
            lines.append("⚠️ Bénéficiaire non sélectionné")
        
        # Évaluation
        evaluation = self.input_evaluation.currentData()
        if evaluation:
            lines.append(f"📊 Évaluation: {evaluation.get('numero_evaluation')} - {evaluation.get('montant_net', 0):,.0f} FCFA")
        
        # Montant
        montant = self.input_montant.value()
        lines.append(f"💰 Montant: {montant:,.0f} FCFA")
        
        # Type paiement
        type_paiement = self.input_type_paiement.currentText()
        lines.append(f"💳 Type: {type_paiement}")
        
        self.summary_text.setText("\n".join(lines))
    
    def creer_reglement(self):
        """Crée le règlement"""
        try:
            # ============================================================
            # VALIDATION
            # ============================================================
            
            # Vérifier le bénéficiaire
            beneficiaire = self.input_beneficiaire.currentData()
            if not beneficiaire:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un bénéficiaire")
                return
            
            # Vérifier le montant
            montant = self.input_montant.value()
            if montant <= 0:
                QMessageBox.warning(self, "Validation", "Veuillez saisir un montant valide")
                return
            
            # Vérifier le type de paiement
            type_paiement = self.input_type_paiement.currentText()
            if not type_paiement:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un type de paiement")
                return
            
            # ============================================================
            # CONSTRUCTION DES DONNÉES
            # ============================================================
            data = {
                'sinistre_id': self.sinistre_id,
                'beneficiaire_id': beneficiaire.get('id'),
                'beneficiaire_nom': f"{beneficiaire.get('nom', '')} {beneficiaire.get('prenom', '')}".strip(),
                'montant': montant,
                'type_paiement': type_paiement,
                'observations': self.input_observations.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            # Ajouter les détails selon le type
            if type_paiement == "CHEQUE":
                data['numero_cheque'] = self.input_cheque_numero.text().strip() or None
                data['banque_emetteur'] = self.input_cheque_banque.text().strip() or None
            elif type_paiement == "VIREMENT":
                data['reference_virement'] = self.input_virement_ref.text().strip() or None
            elif type_paiement == "MOBILE_MONEY":
                data['numero_mobile'] = self.input_mobile_numero.text().strip() or None
                data['operateur_mobile'] = self.input_mobile_operateur.currentText()
            
            # Ajouter l'évaluation si sélectionnée
            evaluation = self.input_evaluation.currentData()
            if evaluation:
                data['evaluation_id'] = evaluation.get('id')
            
            # ============================================================
            # ENVOI
            # ============================================================
            print(f"📝 Création règlement avec les données: {data}")
            
            result = self.reglement_controller.creer_reglement(data)
            
            if result:
                self.reglement_created.emit(result)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"✅ Règlement créé avec succès !\n\n"
                    f"📌 N° Règlement: {result.get('numero_reglement', 'N/A')}\n"
                    f"👤 Bénéficiaire: {data['beneficiaire_nom']}\n"
                    f"💰 Montant: {montant:,.0f} FCFA\n"
                    f"💳 Type: {type_paiement}\n"
                    f"📌 Statut: CRÉÉ"
                )
                self.accept()
            
        except Exception as e:
            print(f"❌ Erreur création règlement: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")