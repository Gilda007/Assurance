"""
Dialogue de paiement d'un règlement
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor

from datetime import datetime


class PaiementDialog(QDialog):
    """Dialogue de paiement d'un règlement"""
    
    paiement_effectue = Signal(dict)
    
    def __init__(self, reglement_numero, reglement_controller, user, parent=None):
        super().__init__(parent)
        self.reglement_numero = reglement_numero
        self.reglement_controller = reglement_controller
        self.user = user
        self.reglement_data = None
        
        self.setWindowTitle("Effectuer le paiement")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # ============================================================
        # EN-TÊTE
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
        
        title = QLabel("💳 Paiement du règlement")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        
        self.lbl_reglement = QLabel(f"Règlement: {self.reglement_numero}")
        info_layout.addWidget(self.lbl_reglement)
        
        self.lbl_montant = QLabel("Montant: -")
        self.lbl_montant.setStyleSheet("font-weight: bold; color: #1a73e8;")
        info_layout.addWidget(self.lbl_montant)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        layout.addWidget(header_frame)
        
        # ============================================================
        # INFORMATIONS DE PAIEMENT
        # ============================================================
        form_group = QGroupBox("Informations de paiement")
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
        
        # Référence de paiement
        self.input_reference = QLineEdit()
        self.input_reference.setPlaceholderText("Référence du paiement")
        self.input_reference.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        form_layout.addRow("Référence *:", self.input_reference)
        
        # Date de paiement
        self.input_date = QDateEdit()
        self.input_date.setDate(QDate.currentDate())
        self.input_date.setCalendarPopup(True)
        self.input_date.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Date paiement:", self.input_date)
        
        # Informations complémentaires
        self.input_infos = QTextEdit()
        self.input_infos.setPlaceholderText("Informations complémentaires (optionnel)")
        self.input_infos.setMaximumHeight(60)
        self.input_infos.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px;")
        form_layout.addRow("Infos complémentaires:", self.input_infos)
        
        layout.addWidget(form_group)
        
        # ============================================================
        # RÉCAPITULATIF
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
        
        summary_title = QLabel("📋 Récapitulatif du paiement")
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
        
        self.btn_payer = QPushButton("✅ Effectuer le paiement")
        self.btn_payer.setStyleSheet("""
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
        self.btn_payer.clicked.connect(self.payer)
        btn_layout.addWidget(self.btn_payer)
        
        layout.addLayout(btn_layout)
        
        # ============================================================
        # CONNEXIONS
        # ============================================================
        self.input_reference.textChanged.connect(self._update_summary)
        self.input_date.dateChanged.connect(self._update_summary)
    
    def load_data(self):
        """Charge les données du règlement"""
        try:
            self.reglement_data = self.reglement_controller.get_reglement_by_numero(
                self.reglement_numero
            )
            if self.reglement_data:
                self.lbl_montant.setText(f"Montant: {self.reglement_data.get('montant', 0):,.0f} FCFA")
                self.input_reference.setText(f"REF-{self.reglement_numero}")
                self._update_summary()
        except Exception as e:
            print(f"Erreur chargement règlement: {e}")
    
    def _update_summary(self):
        """Met à jour le récapitulatif"""
        lines = []
        
        # Règlement
        lines.append(f"📌 Règlement: {self.reglement_numero}")
        if self.reglement_data:
            lines.append(f"💰 Montant: {self.reglement_data.get('montant', 0):,.0f} FCFA")
        
        # Référence
        reference = self.input_reference.text().strip()
        if reference:
            lines.append(f"🔖 Référence: {reference}")
        else:
            lines.append("⚠️ Référence non saisie")
        
        # Date
        date = self.input_date.date()
        lines.append(f"📅 Date: {date.toString('dd/MM/yyyy')}")
        
        self.summary_text.setText("\n".join(lines))
    
    def payer(self):
        """Effectue le paiement"""
        try:
            # ============================================================
            # VALIDATION
            # ============================================================
            
            # Vérifier la référence
            reference = self.input_reference.text().strip()
            if not reference:
                QMessageBox.warning(self, "Validation", "Veuillez saisir une référence de paiement")
                return
            
            # ============================================================
            # CONSTRUCTION DES DONNÉES
            # ============================================================
            data = {
                'reference_paiement': reference,
                'date_paiement': self.input_date.date().toPython(),
                'informations': self.input_infos.toPlainText().strip() or None,
                'updated_by': self.user.id if self.user else None
            }
            
            # ============================================================
            # ENVOI
            # ============================================================
            print(f"📝 Paiement avec les données: {data}")
            
            # Récupérer l'ID du règlement
            reglement_id = self.reglement_data.get('id') if self.reglement_data else None
            if not reglement_id:
                raise ValueError("Règlement non trouvé")
            
            result = self.reglement_controller.payer_reglement(reglement_id, data)
            
            if result:
                self.paiement_effectue.emit({
                    'reglement_id': reglement_id,
                    'reference': reference,
                    'montant': self.reglement_data.get('montant', 0)
                })
                QMessageBox.information(
                    self,
                    "Succès",
                    f"✅ Paiement effectué avec succès !\n\n"
                    f"📌 Règlement: {self.reglement_numero}\n"
                    f"💰 Montant: {self.reglement_data.get('montant', 0):,.0f} FCFA\n"
                    f"🔖 Référence: {reference}\n"
                    f"📌 Statut: PAYÉ"
                )
                self.accept()
            
        except Exception as e:
            print(f"❌ Erreur paiement: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors du paiement: {str(e)}")