"""
Dialogue d'enregistrement d'encaissement de recours
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QDate

from datetime import datetime


class EncaissementDialog(QDialog):
    """Dialogue d'enregistrement d'encaissement"""
    
    encaissement_added = Signal(dict)
    
    def __init__(self, recours_id, recours_info, recours_controller, user, parent=None):
        super().__init__(parent)
        self.recours_id = recours_id
        self.recours_info = recours_info or {}
        self.recours_controller = recours_controller
        self.user = user
        
        self.setWindowTitle("Enregistrer un encaissement")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setup_ui()
        self._update_summary()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # ============================================================
        # EN-TÊTE AVEC INFOS RECOURS
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
        
        title = QLabel("💰 Encaissement de recours")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        
        self.lbl_recours = QLabel(f"Recours: {self.recours_info.get('numero_recours', 'N/A')}")
        info_layout.addWidget(self.lbl_recours)
        
        self.lbl_debiteur = QLabel(f"Débiteur: {self.recours_info.get('debiteur_nom', 'N/A')}")
        info_layout.addWidget(self.lbl_debiteur)
        
        self.lbl_solde = QLabel(f"💰 Solde restant: {self.recours_info.get('solde', 0):,.0f} FCFA")
        self.lbl_solde.setStyleSheet("font-weight: bold; color: #1a73e8;")
        info_layout.addWidget(self.lbl_solde)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        layout.addWidget(header_frame)
        
        # ============================================================
        # SECTION 1: INFORMATIONS DE L'ENCAISSEMENT
        # ============================================================
        form_group = QGroupBox("Informations de l'encaissement")
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
        
        # Montant encaissé
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999999999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        self.input_montant.setMaximum(self.recours_info.get('solde', 0))
        self.input_montant.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        self.input_montant.valueChanged.connect(self._update_summary)
        form_layout.addRow("Montant encaissé *:", self.input_montant)
        
        # Mode d'encaissement
        self.input_mode = QComboBox()
        self.input_mode.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_mode.addItems(["VIREMENT", "CHEQUE", "MOBILE_MONEY", "COMPENSATION"])
        self.input_mode.currentIndexChanged.connect(self._update_summary)
        form_layout.addRow("Mode d'encaissement *:", self.input_mode)
        
        # Référence bancaire
        self.input_reference = QLineEdit()
        self.input_reference.setPlaceholderText("Référence bancaire")
        self.input_reference.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_reference.textChanged.connect(self._update_summary)
        form_layout.addRow("Référence bancaire:", self.input_reference)
        
        # Date d'encaissement
        self.input_date = QDateEdit()
        self.input_date.setDate(QDate.currentDate())
        self.input_date.setCalendarPopup(True)
        self.input_date.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Date d'encaissement:", self.input_date)
        
        # Banque
        self.input_banque = QLineEdit()
        self.input_banque.setPlaceholderText("Banque (optionnel)")
        self.input_banque.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Banque:", self.input_banque)
        
        layout.addWidget(form_group)
        
        # ============================================================
        # SECTION 2: OBSERVATIONS
        # ============================================================
        self.input_observations = QTextEdit()
        self.input_observations.setPlaceholderText("Observations sur l'encaissement...")
        self.input_observations.setMaximumHeight(60)
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
        
        summary_title = QLabel("📋 Récapitulatif de l'encaissement")
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
        
        self.btn_encaisser = QPushButton("✅ Enregistrer l'encaissement")
        self.btn_encaisser.setStyleSheet("""
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
        self.btn_encaisser.clicked.connect(self.enregistrer_encaissement)
        btn_layout.addWidget(self.btn_encaisser)
        
        layout.addLayout(btn_layout)
    
    def _update_summary(self):
        """Met à jour le récapitulatif"""
        lines = []
        
        # Montant
        montant = self.input_montant.value()
        if montant > 0:
            lines.append(f"💰 Montant: {montant:,.0f} FCFA")
            solde_restant = self.recours_info.get('solde', 0) - montant
            if solde_restant > 0:
                lines.append(f"📊 Solde restant: {solde_restant:,.0f} FCFA")
            else:
                lines.append("✅ Recours soldé")
        else:
            lines.append("⚠️ Montant non défini")
        
        # Mode
        mode = self.input_mode.currentText()
        if mode:
            lines.append(f"💳 Mode: {mode}")
        
        # Référence
        reference = self.input_reference.text().strip()
        if reference:
            lines.append(f"🔖 Référence: {reference}")
        
        self.summary_text.setText("\n".join(lines))
    
    def enregistrer_encaissement(self):
        """Enregistre l'encaissement"""
        try:
            # ============================================================
            # VALIDATION
            # ============================================================
            
            montant = self.input_montant.value()
            if montant <= 0:
                QMessageBox.warning(self, "Validation", "Veuillez saisir un montant valide")
                return
            
            if montant > self.recours_info.get('solde', 0):
                QMessageBox.warning(
                    self,
                    "Validation",
                    f"Le montant ({montant:,.0f} FCFA) dépasse le solde restant ({self.recours_info.get('solde', 0):,.0f} FCFA)"
                )
                return
            
            mode = self.input_mode.currentText()
            if not mode:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un mode d'encaissement")
                return
            
            # ============================================================
            # CONSTRUCTION DES DONNÉES
            # ============================================================
            data = {
                'montant': montant,
                'mode_encaissement': mode,
                'reference_bancaire': self.input_reference.text().strip() or None,
                'date_encaissement': self.input_date.date().toPython(),
                'banque': self.input_banque.text().strip() or None,
                'observations': self.input_observations.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            # ============================================================
            # ENVOI
            # ============================================================
            print(f"📝 Encaissement avec les données: {data}")
            
            result = self.recours_controller.enregistrer_encaissement(
                self.recours_id,
                data
            )
            
            if result:
                solde_restant = self.recours_info.get('solde', 0) - montant
                self.encaissement_added.emit({
                    'recours_id': self.recours_id,
                    'montant': montant,
                    'mode': mode,
                    'solde_restant': solde_restant
                })
                
                QMessageBox.information(
                    self,
                    "Succès",
                    f"✅ Encaissement enregistré avec succès !\n\n"
                    f"📌 Recours: {self.recours_info.get('numero_recours', 'N/A')}\n"
                    f"💰 Montant encaissé: {montant:,.0f} FCFA\n"
                    f"💳 Mode: {mode}\n"
                    f"📊 Solde restant: {solde_restant:,.0f} FCFA\n"
                    f"📌 Statut: {'SOLDE' if solde_restant == 0 else 'PARTIELLEMENT ENCAISSÉ'}"
                )
                self.accept()
            
        except Exception as e:
            print(f"❌ Erreur encaissement: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'encaissement: {str(e)}")