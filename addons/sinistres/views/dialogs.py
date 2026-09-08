"""
Dialogue pour les actions LOMETA
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from datetime import datetime


class EditSinistreDialog(QDialog):
    """Dialogue d'édition d'un sinistre"""
    
    def __init__(self, sinistre_id, controller, referentiel_controller, user, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.controller = controller
        self.referentiel_controller = referentiel_controller
        self.user = user
        self.sinistre_data = None
        
        self.setWindowTitle("Modifier le sinistre")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.load_data()
        self.setup_ui()
    
    def load_data(self):
        self.sinistre_data = self.controller.get_sinistre(self.sinistre_id)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Informations générales")
        form_layout = QFormLayout(form_group)
        
        # Référence
        self.input_reference = QLineEdit()
        self.input_reference.setText(self.sinistre_data.get('numero_reference', ''))
        form_layout.addRow("Référence:", self.input_reference)
        
        # Branche
        self.input_branche = QComboBox()
        branches = self.referentiel_controller.get_referentiels_by_famille("branches")
        for b in branches:
            self.input_branche.addItem(b.get('libelle', ''), b.get('code', ''))
        current_branche = self.sinistre_data.get('branche', '')
        for i in range(self.input_branche.count()):
            if self.input_branche.itemData(i) == current_branche:
                self.input_branche.setCurrentIndex(i)
                break
        form_layout.addRow("Branche:", self.input_branche)
        
        # Circonstance
        self.input_circonstance = QComboBox()
        circonstances = self.referentiel_controller.get_referentiels_by_famille("circonstances")
        for c in circonstances:
            self.input_circonstance.addItem(c.get('libelle', ''), c.get('code', ''))
        current_circ = self.sinistre_data.get('circonstance_principale', '')
        for i in range(self.input_circonstance.count()):
            if self.input_circonstance.itemData(i) == current_circ:
                self.input_circonstance.setCurrentIndex(i)
                break
        form_layout.addRow("Circonstance:", self.input_circonstance)
        
        # Responsabilité
        self.input_responsabilite = QComboBox()
        responsabilites = self.referentiel_controller.get_referentiels_by_famille("responsabilites")
        for r in responsabilites:
            self.input_responsabilite.addItem(
                f"{r.get('libelle', '')} ({int(r.get('valeur', 0) * 100)}%)",
                r.get('code', '')
            )
        current_taux = self.sinistre_data.get('taux_responsabilite', 0)
        for i in range(self.input_responsabilite.count()):
            code = self.input_responsabilite.itemData(i)
            for r in responsabilites:
                if r.get('code') == code and r.get('valeur', 0) == current_taux:
                    self.input_responsabilite.setCurrentIndex(i)
                    break
        form_layout.addRow("Responsabilité:", self.input_responsabilite)
        
        # Description
        self.input_description = QTextEdit()
        self.input_description.setText(self.sinistre_data.get('description', ''))
        self.input_description.setMaximumHeight(100)
        form_layout.addRow("Description:", self.input_description)
        
        layout.addWidget(form_group)
        
        # Boutons
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def accept(self):
        try:
            data = {
                'numero_reference': self.input_reference.text().strip() or None,
                'branche': self.input_branche.currentData(),
                'circonstance_principale': self.input_circonstance.currentData(),
                'taux_responsabilite': self._get_responsabilite_taux(),
                'description': self.input_description.toPlainText().strip() or None,
                'updated_by': self.user.id if self.user else None
            }
            
            result = self.controller.update_sinistre(self.sinistre_id, data)
            if result:
                super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _get_responsabilite_taux(self) -> float:
        code = self.input_responsabilite.currentData()
        referentiels = self.referentiel_controller.get_referentiels_by_famille("responsabilites")
        for r in referentiels:
            if r.get('code') == code:
                return r.get('valeur', 0)
        return 0.0


class AddDommageDialog(QDialog):
    def __init__(self, sinistre_id, controller, user, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.controller = controller
        self.user = user
        
        self.setWindowTitle("Ajouter un dommage")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Dommage")
        form_layout = QFormLayout(form_group)
        
        self.input_type = QComboBox()
        self.input_type.addItems(["matériel", "corporel", "immatériel", "mixte"])
        form_layout.addRow("Type:", self.input_type)
        
        self.input_description = QTextEdit()
        self.input_description.setMaximumHeight(80)
        self.input_description.setPlaceholderText("Description du dommage...")
        form_layout.addRow("Description:", self.input_description)
        
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999999999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        form_layout.addRow("Montant estimé:", self.input_montant)
        
        layout.addWidget(form_group)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def accept(self):
        try:
            data = {
                'type_dommage': self.input_type.currentText(),
                'description': self.input_description.toPlainText().strip() or None,
                'montant_estime': self.input_montant.value(),
                'created_by': self.user.id if self.user else None
            }
            
            result = self.controller.ajouter_dommage(self.sinistre_id, data)
            if result:
                super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


class AddTiersDialog(QDialog):
    def __init__(self, sinistre_id, controller, user, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.controller = controller
        self.user = user
        
        self.setWindowTitle("Ajouter un tiers")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Tiers")
        form_layout = QFormLayout(form_group)
        
        self.input_type = QComboBox()
        self.input_type.addItems(["responsable", "victime", "témoin", "assureur_adverse"])
        form_layout.addRow("Type:", self.input_type)
        
        self.input_nom = QLineEdit()
        self.input_nom.setPlaceholderText("Nom du tiers")
        form_layout.addRow("Nom:", self.input_nom)
        
        self.input_prenom = QLineEdit()
        self.input_prenom.setPlaceholderText("Prénom")
        form_layout.addRow("Prénom:", self.input_prenom)
        
        self.input_telephone = QLineEdit()
        self.input_telephone.setPlaceholderText("Téléphone")
        form_layout.addRow("Téléphone:", self.input_telephone)
        
        self.input_assurance = QLineEdit()
        self.input_assurance.setPlaceholderText("Compagnie d'assurance")
        form_layout.addRow("Assurance:", self.input_assurance)
        
        self.input_police = QLineEdit()
        self.input_police.setPlaceholderText("Police d'assurance")
        form_layout.addRow("Police:", self.input_police)
        
        layout.addWidget(form_group)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def accept(self):
        try:
            data = {
                'type_tiers': self.input_type.currentText(),
                'nom': self.input_nom.text().strip(),
                'prenom': self.input_prenom.text().strip() or None,
                'telephone': self.input_telephone.text().strip() or None,
                'assurance': self.input_assurance.text().strip() or None,
                'police_assurance': self.input_police.text().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            if not data['nom']:
                QMessageBox.warning(self, "Validation", "Veuillez saisir un nom")
                return
            
            result = self.controller.ajouter_tiers(self.sinistre_id, data)
            if result:
                super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


class AddExpertiseDialog(QDialog):
    def __init__(self, sinistre_id, controller, user, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.controller = controller
        self.user = user
        
        self.setWindowTitle("Créer une mission d'expertise")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Mission d'expertise")
        form_layout = QFormLayout(form_group)
        
        self.input_type = QComboBox()
        self.input_type.addItems(["auto_materiel", "auto_corporel", "batiment", "transport", "medical", "judiciaire"])
        form_layout.addRow("Type:", self.input_type)
        
        self.input_domaine = QLineEdit()
        self.input_domaine.setPlaceholderText("Domaine spécifique (optionnel)")
        form_layout.addRow("Domaine:", self.input_domaine)
        
        self.input_echeance = QDateEdit()
        self.input_echeance.setDate(QDate.currentDate().addDays(14))
        self.input_echeance.setCalendarPopup(True)
        form_layout.addRow("Échéance:", self.input_echeance)
        
        self.input_observations = QTextEdit()
        self.input_observations.setMaximumHeight(80)
        self.input_observations.setPlaceholderText("Observations (optionnel)")
        form_layout.addRow("Observations:", self.input_observations)
        
        layout.addWidget(form_group)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def accept(self):
        try:
            data = {
                'sinistre_id': self.sinistre_id,
                'type_expertise': self.input_type.currentText(),
                'domaine': self.input_domaine.text().strip() or None,
                'date_echeance': self.input_echeance.date().toPython(),
                'observations': self.input_observations.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            result = self.controller.creer_mission(data)
            if result:
                super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


class AddEvaluationDialog(QDialog):
    def __init__(self, sinistre_id, controller, user, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.controller = controller
        self.user = user
        
        self.setWindowTitle("Créer une évaluation")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Évaluation")
        form_layout = QFormLayout(form_group)
        
        self.input_type = QComboBox()
        self.input_type.addItems(["auto_materiel", "auto_corporel", "incendie", "vol", "degats_eau", "rc_generale"])
        form_layout.addRow("Type:", self.input_type)
        
        self.input_montant_brut = QDoubleSpinBox()
        self.input_montant_brut.setRange(0, 999999999)
        self.input_montant_brut.setPrefix("FCFA ")
        self.input_montant_brut.setDecimals(0)
        self.input_montant_brut.setSingleStep(10000)
        form_layout.addRow("Montant brut:", self.input_montant_brut)
        
        self.input_franchise = QDoubleSpinBox()
        self.input_franchise.setRange(0, 999999999)
        self.input_franchise.setPrefix("FCFA ")
        self.input_franchise.setDecimals(0)
        self.input_franchise.setSingleStep(5000)
        form_layout.addRow("Franchise:", self.input_franchise)
        
        self.input_taux = QDoubleSpinBox()
        self.input_taux.setRange(0, 100)
        self.input_taux.setSuffix("%")
        self.input_taux.setValue(100)
        self.input_taux.setSingleStep(5)
        form_layout.addRow("Taux responsabilité:", self.input_taux)
        
        self.input_details = QTextEdit()
        self.input_details.setMaximumHeight(80)
        self.input_details.setPlaceholderText("Détails de l'évaluation...")
        form_layout.addRow("Détails:", self.input_details)
        
        layout.addWidget(form_group)
        
        # Montant net calculé
        self.lbl_net = QLabel("Montant net: 0 FCFA")
        self.lbl_net.setStyleSheet("font-weight: bold; color: #1a73e8; font-size: 14px;")
        layout.addWidget(self.lbl_net)
        
        self.input_montant_brut.valueChanged.connect(self.calculer_net)
        self.input_franchise.valueChanged.connect(self.calculer_net)
        self.input_taux.valueChanged.connect(self.calculer_net)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def calculer_net(self):
        brut = self.input_montant_brut.value()
        franchise = self.input_franchise.value()
        taux = self.input_taux.value() / 100
        net = (brut - franchise) * taux
        self.lbl_net.setText(f"Montant net: {net:,.0f} FCFA")
    
    def accept(self):
        try:
            data = {
                'sinistre_id': self.sinistre_id,
                'type_evaluation': self.input_type.currentText(),
                'montant_brut': self.input_montant_brut.value(),
                'franchise': self.input_franchise.value(),
                'taux_responsabilite': self.input_taux.value() / 100,
                'details': self.input_details.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            result = self.controller.creer_evaluation(data)
            if result:
                super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


class AddReglementDialog(QDialog):
    def __init__(self, sinistre_id, controller, user, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.controller = controller
        self.user = user
        
        self.setWindowTitle("Créer un règlement")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Règlement")
        form_layout = QFormLayout(form_group)
        
        self.input_beneficiaire = QLineEdit()
        self.input_beneficiaire.setPlaceholderText("Nom du bénéficiaire")
        form_layout.addRow("Bénéficiaire:", self.input_beneficiaire)
        
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999999999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        form_layout.addRow("Montant:", self.input_montant)
        
        self.input_type = QComboBox()
        self.input_type.addItems(["CHEQUE", "VIREMENT", "MOBILE_MONEY"])
        form_layout.addRow("Type paiement:", self.input_type)
        
        self.input_observations = QTextEdit()
        self.input_observations.setMaximumHeight(80)
        self.input_observations.setPlaceholderText("Observations...")
        form_layout.addRow("Observations:", self.input_observations)
        
        layout.addWidget(form_group)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def accept(self):
        try:
            data = {
                'sinistre_id': self.sinistre_id,
                'beneficiaire_nom': self.input_beneficiaire.text().strip(),
                'montant': self.input_montant.value(),
                'type_paiement': self.input_type.currentText(),
                'observations': self.input_observations.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            if not data['beneficiaire_nom']:
                QMessageBox.warning(self, "Validation", "Veuillez saisir un bénéficiaire")
                return
            
            result = self.controller.creer_reglement(data)
            if result:
                super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


class AddRecoursDialog(QDialog):
    def __init__(self, sinistre_id, controller, user, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.controller = controller
        self.user = user
        
        self.setWindowTitle("Créer un recours")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Recours")
        form_layout = QFormLayout(form_group)
        
        self.input_debiteur = QLineEdit()
        self.input_debiteur.setPlaceholderText("Nom du débiteur")
        form_layout.addRow("Débiteur:", self.input_debiteur)
        
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999999999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        form_layout.addRow("Montant réclamé:", self.input_montant)
        
        self.input_type = QComboBox()
        self.input_type.addItems(["responsable", "assureur_adverse", "coassureur", "reaseureur"])
        form_layout.addRow("Type recours:", self.input_type)
        
        self.input_observations = QTextEdit()
        self.input_observations.setMaximumHeight(80)
        self.input_observations.setPlaceholderText("Observations...")
        form_layout.addRow("Observations:", self.input_observations)
        
        layout.addWidget(form_group)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def accept(self):
        try:
            data = {
                'sinistre_id': self.sinistre_id,
                'debiteur_nom': self.input_debiteur.text().strip(),
                'montant_reclame': self.input_montant.value(),
                'type_recours': self.input_type.currentText(),
                'observations': self.input_observations.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            if not data['debiteur_nom']:
                QMessageBox.warning(self, "Validation", "Veuillez saisir un débiteur")
                return
            
            result = self.controller.creer_recours(data)
            if result:
                super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))