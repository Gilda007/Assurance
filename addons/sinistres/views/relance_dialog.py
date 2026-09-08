"""
Dialogue d'ajout de relance pour un recours
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor

from datetime import datetime, timedelta


class RelanceDialog(QDialog):
    """Dialogue d'ajout de relance pour un recours"""
    
    relance_added = Signal(dict)
    
    def __init__(self, recours_id, recours_info, recours_controller, user, parent=None):
        super().__init__(parent)
        self.recours_id = recours_id
        self.recours_info = recours_info or {}
        self.recours_controller = recours_controller
        self.user = user
        
        self.setWindowTitle("Ajouter une relance")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setup_ui()
    
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
        
        title = QLabel("🔔 Relance de recours")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        
        self.lbl_recours = QLabel(f"Recours: {self.recours_info.get('numero_recours', 'N/A')}")
        info_layout.addWidget(self.lbl_recours)
        
        self.lbl_debiteur = QLabel(f"Débiteur: {self.recours_info.get('debiteur_nom', 'N/A')}")
        info_layout.addWidget(self.lbl_debiteur)
        
        self.lbl_nb_relances = QLabel(f"📊 Relances: {self.recours_info.get('nombre_relances', 0)}")
        info_layout.addWidget(self.lbl_nb_relances)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        layout.addWidget(header_frame)
        
        # ============================================================
        # SECTION 1: INFORMATIONS DE LA RELANCE
        # ============================================================
        form_group = QGroupBox("Informations de la relance")
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
        
        # Type de relance
        self.input_type = QComboBox()
        self.input_type.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        self.input_type.addItems([
            "COURRIER",
            "EMAIL",
            "TELEPHONE",
            "SMS",
            "WHATSAPP"
        ])
        form_layout.addRow("Type de relance *:", self.input_type)
        
        # Date de relance
        self.input_date = QDateEdit()
        self.input_date.setDate(QDate.currentDate())
        self.input_date.setCalendarPopup(True)
        self.input_date.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Date de relance:", self.input_date)
        
        # Délai pour la prochaine relance
        self.input_delai = QSpinBox()
        self.input_delai.setRange(1, 90)
        self.input_delai.setValue(15)
        self.input_delai.setSuffix(" jours")
        self.input_delai.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Délai prochaine relance:", self.input_delai)
        
        # Contenu de la relance
        self.input_contenu = QTextEdit()
        self.input_contenu.setPlaceholderText("""
Contenu de la relance:

Objet: Relance - Recours N°XXX

Madame/Monsieur,

Nous vous rappelons que le recours N°XXX est toujours en attente de traitement.

Merci de nous faire parvenir votre réponse dans les meilleurs délais.

Cordialement.
        """.strip())
        self.input_contenu.setMinimumHeight(120)
        self.input_contenu.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px;
                font-family: monospace;
                font-size: 12px;
            }
            QTextEdit:focus {
                border-color: #1a73e8;
            }
        """)
        form_layout.addRow("Contenu de la relance:", self.input_contenu)
        
        layout.addWidget(form_group)
        
        # ============================================================
        # SECTION 2: OPTIONS
        # ============================================================
        options_group = QGroupBox("Options")
        options_group.setStyleSheet("""
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
        options_layout = QVBoxLayout(options_group)
        
        self.check_auto_prochaine = QCheckBox("Planifier automatiquement la prochaine relance")
        self.check_auto_prochaine.setChecked(True)
        self.check_auto_prochaine.setStyleSheet("font-weight: normal;")
        options_layout.addWidget(self.check_auto_prochaine)
        
        self.check_envoyer_email = QCheckBox("Envoyer par email (si disponible)")
        self.check_envoyer_email.setChecked(True)
        self.check_envoyer_email.setStyleSheet("font-weight: normal;")
        options_layout.addWidget(self.check_envoyer_email)
        
        layout.addWidget(options_group)
        
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
        
        summary_title = QLabel("📋 Récapitulatif de la relance")
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
        
        self.btn_ajouter = QPushButton("✅ Ajouter la relance")
        self.btn_ajouter.setStyleSheet("""
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
        self.btn_ajouter.clicked.connect(self.ajouter_relance)
        btn_layout.addWidget(self.btn_ajouter)
        
        layout.addLayout(btn_layout)
        
        # ============================================================
        # CONNEXIONS
        # ============================================================
        self.input_type.currentIndexChanged.connect(self._update_summary)
        self.input_date.dateChanged.connect(self._update_summary)
        self.input_delai.valueChanged.connect(self._update_summary)
        self.input_contenu.textChanged.connect(self._update_summary)
    
    def _update_summary(self):
        """Met à jour le récapitulatif"""
        lines = []
        
        # Type
        type_text = self.input_type.currentText()
        if type_text:
            lines.append(f"📌 Type: {type_text}")
        
        # Date
        date = self.input_date.date()
        lines.append(f"📅 Date: {date.toString('dd/MM/yyyy')}")
        
        # Délai prochaine
        delai = self.input_delai.value()
        prochaine_date = date.addDays(delai)
        lines.append(f"⏳ Prochaine relance: {prochaine_date.toString('dd/MM/yyyy')} (+{delai} jours)")
        
        # Contenu
        contenu = self.input_contenu.toPlainText().strip()
        if contenu:
            lines.append(f"📝 Contenu: {len(contenu)} caractères")
        else:
            lines.append("⚠️ Contenu non saisi")
        
        # Options
        if self.check_auto_prochaine.isChecked():
            lines.append("🔄 Planification automatique activée")
        if self.check_envoyer_email.isChecked():
            lines.append("📧 Envoi par email activé")
        
        self.summary_text.setText("\n".join(lines))
    
    def ajouter_relance(self):
        """Ajoute la relance"""
        try:
            # ============================================================
            # VALIDATION
            # ============================================================
            
            type_relance = self.input_type.currentText()
            if not type_relance:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un type de relance")
                return
            
            contenu = self.input_contenu.toPlainText().strip()
            if not contenu:
                QMessageBox.warning(self, "Validation", "Veuillez saisir le contenu de la relance")
                return
            
            # ============================================================
            # CONSTRUCTION DES DONNÉES
            # ============================================================
            date_relance = self.input_date.date().toPython()
            delai = self.input_delai.value()
            prochaine_relance = date_relance + timedelta(days=delai)
            
            data = {
                'recours_id': self.recours_id,
                'type_relance': type_relance,
                'date_relance': date_relance,
                'contenu': contenu,
                'delai_prochain': delai,
                'prochaine_relance': prochaine_relance if self.check_auto_prochaine.isChecked() else None,
                'envoyer_email': self.check_envoyer_email.isChecked(),
                'created_by': self.user.id if self.user else None
            }
            
            # ============================================================
            # ENVOI
            # ============================================================
            print(f"📝 Ajout relance avec les données: {data}")
            
            result = self.recours_controller.ajouter_relance(self.recours_id, data)
            
            if result:
                self.relance_added.emit({
                    'recours_id': self.recours_id,
                    'type_relance': type_relance,
                    'date_relance': date_relance.strftime('%d/%m/%Y'),
                    'prochaine_relance': prochaine_relance.strftime('%d/%m/%Y') if self.check_auto_prochaine.isChecked() else None
                })
                
                QMessageBox.information(
                    self,
                    "Succès",
                    f"✅ Relance ajoutée avec succès !\n\n"
                    f"📌 Recours: {self.recours_info.get('numero_recours', 'N/A')}\n"
                    f"📌 Type: {type_relance}\n"
                    f"📅 Date: {date_relance.strftime('%d/%m/%Y')}\n"
                    f"⏳ Prochaine relance: {prochaine_relance.strftime('%d/%m/%Y') if self.check_auto_prochaine.isChecked() else 'Non planifiée'}\n"
                    f"📧 Email: {'Oui' if self.check_envoyer_email.isChecked() else 'Non'}"
                )
                self.accept()
            
        except Exception as e:
            print(f"❌ Erreur ajout relance: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout: {str(e)}")