"""
Dialogue de création de recours
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor

from datetime import datetime


class RecoursDialog(QDialog):
    """Dialogue de création de recours"""
    
    recours_created = Signal(dict)
    
    def __init__(self, sinistre_id, recours_controller, user, sinistre_info=None, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.recours_controller = recours_controller
        self.user = user
        self.sinistre_info = sinistre_info or {}
        
        self.setWindowTitle("Créer un recours")
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
        
        title = QLabel("⚖️ Création de recours")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        
        self.lbl_sinistre = QLabel(f"Sinistre: {self.sinistre_info.get('numero_sinistre', 'N/A')}")
        info_layout.addWidget(self.lbl_sinistre)
        
        self.lbl_client = QLabel(f"Client: {self.sinistre_info.get('client_nom', 'N/A')}")
        info_layout.addWidget(self.lbl_client)
        
        self.lbl_montant = QLabel(f"💰 Montant réglé: {self.sinistre_info.get('montant_regle', 0):,.0f} FCFA")
        self.lbl_montant.setStyleSheet("font-weight: bold; color: #1a73e8;")
        info_layout.addWidget(self.lbl_montant)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        layout.addWidget(header_frame)
        
        # ============================================================
        # SECTION 1: INFORMATIONS DU RECOURS
        # ============================================================
        form_group = QGroupBox("Informations du recours")
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
        
        # Type de recours
        self.input_type = QComboBox()
        self.input_type.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        self.input_type.addItems([
            "responsable",
            "assureur_adverse",
            "coassureur",
            "reaseureur"
        ])
        form_layout.addRow("Type de recours *:", self.input_type)
        
        # Débiteur
        self.input_debiteur = QLineEdit()
        self.input_debiteur.setPlaceholderText("Nom du débiteur")
        self.input_debiteur.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Débiteur *:", self.input_debiteur)
        
        # Montant réclamé
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999999999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        self.input_montant.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        form_layout.addRow("Montant réclamé *:", self.input_montant)
        
        # Date d'accord (optionnel)
        self.input_date_accord = QDateEdit()
        self.input_date_accord.setDate(QDate.currentDate().addDays(30))
        self.input_date_accord.setCalendarPopup(True)
        self.input_date_accord.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Date d'accord prévue:", self.input_date_accord)
        
        # Référence accord (optionnel)
        self.input_reference = QLineEdit()
        self.input_reference.setPlaceholderText("Référence de l'accord (optionnel)")
        self.input_reference.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Référence accord:", self.input_reference)
        
        layout.addWidget(form_group)
        
        # ============================================================
        # SECTION 2: OBSERVATIONS
        # ============================================================
        self.input_observations = QTextEdit()
        self.input_observations.setPlaceholderText("""
Observations sur le recours:
- Circonstances du recours
- Pièces justificatives
- Contacts
- Autres informations...
        """.strip())
        self.input_observations.setMaximumHeight(80)
        self.input_observations.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px;")
        layout.addWidget(QLabel("Observations:"))
        layout.addWidget(self.input_observations)
        
        # ============================================================
        # SECTION 3: RÉCAPITULATIF
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
        
        summary_title = QLabel("📋 Récapitulatif du recours")
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
        
        self.btn_creer = QPushButton("✅ Créer le recours")
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
        self.btn_creer.clicked.connect(self.creer_recours)
        btn_layout.addWidget(self.btn_creer)
        
        layout.addLayout(btn_layout)
        
        # ============================================================
        # CONNEXIONS
        # ============================================================
        self.input_type.currentIndexChanged.connect(self._update_summary)
        self.input_debiteur.textChanged.connect(self._update_summary)
        self.input_montant.valueChanged.connect(self._update_summary)
        self.input_observations.textChanged.connect(self._update_summary)
    
    def load_data(self):
        """Charge les données initiales"""
        self._update_summary()
    
    def _update_summary(self):
        """Met à jour le récapitulatif"""
        lines = []
        
        # Type
        type_text = self.input_type.currentText()
        if type_text:
            lines.append(f"📌 Type: {type_text.replace('_', ' ').title()}")
        
        # Débiteur
        debiteur = self.input_debiteur.text().strip()
        if debiteur:
            lines.append(f"👤 Débiteur: {debiteur}")
        else:
            lines.append("⚠️ Débiteur non saisi")
        
        # Montant
        montant = self.input_montant.value()
        if montant > 0:
            lines.append(f"💰 Montant réclamé: {montant:,.0f} FCFA")
        else:
            lines.append("⚠️ Montant non défini")
        
        self.summary_text.setText("\n".join(lines))
    
    def creer_recours(self):
        """Crée le recours"""
        try:
            # ============================================================
            # VALIDATION
            # ============================================================
            
            # Vérifier le débiteur
            debiteur = self.input_debiteur.text().strip()
            if not debiteur:
                QMessageBox.warning(self, "Validation", "Veuillez saisir le nom du débiteur")
                return
            
            # Vérifier le montant
            montant = self.input_montant.value()
            if montant <= 0:
                QMessageBox.warning(self, "Validation", "Veuillez saisir un montant valide")
                return
            
            # ============================================================
            # CONSTRUCTION DES DONNÉES
            # ============================================================
            data = {
                'sinistre_id': self.sinistre_id,
                'type_recours': self.input_type.currentText(),
                'debiteur_nom': debiteur,
                'montant_reclame': montant,
                'date_accord': self.input_date_accord.date().toPython(),
                'reference_accord': self.input_reference.text().strip() or None,
                'observations': self.input_observations.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            # ============================================================
            # ENVOI
            # ============================================================
            print(f"📝 Création recours avec les données: {data}")
            
            result = self.recours_controller.creer_recours(data)
            
            if result:
                self.recours_created.emit(result)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"✅ Recours créé avec succès !\n\n"
                    f"📌 N° Recours: {result.get('numero_recours', 'N/A')}\n"
                    f"👤 Débiteur: {debiteur}\n"
                    f"💰 Montant réclamé: {montant:,.0f} FCFA\n"
                    f"📌 Type: {data['type_recours'].replace('_', ' ').title()}\n"
                    f"📌 Statut: OUVERT"
                )
                self.accept()
            
        except Exception as e:
            print(f"❌ Erreur création recours: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")