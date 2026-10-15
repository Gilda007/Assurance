"""
Dialogue de création/modification d'une banque (référentiel)
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox, QFrame,
    QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression


class BanqueDialog(QDialog):
    """Dialogue de création/modification d'une banque"""
    
    banque_created = Signal(dict)
    banque_updated = Signal(dict)
    
    def __init__(self, reglement_controller, user, banque_data=None, parent=None):
        super().__init__(parent)
        self.reglement_controller = reglement_controller
        self.user = user
        self.banque_data = banque_data  # None = création, dict = édition
        self.is_edit_mode = banque_data is not None
        
        title = "Modifier une banque" if self.is_edit_mode else "Nouvelle banque"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(550)
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_banque_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ============================================================
        # EN-TÊTE
        # ============================================================
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        header_layout = QHBoxLayout(header)
        
        icon = QLabel("🏦")
        icon.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon)
        
        title = QLabel(
            "Modifier la banque" if self.is_edit_mode else "Créer une nouvelle banque"
        )
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # ============================================================
        # FORMULAIRE
        # ============================================================
        form_group = QGroupBox("Informations de la banque")
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
        
        # Code banque (obligatoire, unique)
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Ex: ATL, ECO, BIC")
        self.input_code.setMaxLength(20)
        # Validation : alphanumérique uniquement
        regex = QRegularExpression("^[A-Z0-9]{2,20}$")
        self.input_code.setValidator(QRegularExpressionValidator(regex))
        self._style_input(self.input_code)
        form_layout.addRow("Code banque *:", self.input_code)
        
        # Libellé (obligatoire)
        self.input_libelle = QLineEdit()
        self.input_libelle.setPlaceholderText("Ex: Banque Atlantique du Cameroun")
        self.input_libelle.setMaxLength(200)
        self._style_input(self.input_libelle)
        form_layout.addRow("Libellé *:", self.input_libelle)
        
        # BIC / SWIFT
        self.input_bic = QLineEdit()
        self.input_bic.setPlaceholderText("Ex: ATLCCMCX")
        self.input_bic.setMaxLength(20)
        self._style_input(self.input_bic)
        form_layout.addRow("BIC / SWIFT:", self.input_bic)
        
        # Pays
        self.input_pays = QLineEdit()
        self.input_pays.setPlaceholderText("Ex: Cameroun")
        self.input_pays.setMaxLength(100)
        self.input_pays.setText("Cameroun")  # valeur par défaut
        self._style_input(self.input_pays)
        form_layout.addRow("Pays:", self.input_pays)
        
        # Adresse
        self.input_adresse = QLineEdit()
        self.input_adresse.setPlaceholderText("Adresse complète")
        self.input_adresse.setMaxLength(300)
        self._style_input(self.input_adresse)
        form_layout.addRow("Adresse:", self.input_adresse)
        
        # Téléphone
        self.input_telephone = QLineEdit()
        self.input_telephone.setPlaceholderText("Ex: +237 6 XX XX XX XX")
        self.input_telephone.setMaxLength(50)
        self._style_input(self.input_telephone)
        form_layout.addRow("Téléphone:", self.input_telephone)
        
        # Email
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Ex: contact@banque.cm")
        self.input_email.setMaxLength(200)
        self._style_input(self.input_email)
        form_layout.addRow("Email:", self.input_email)
        
        # Actif
        self.check_actif = QCheckBox("Banque active (disponible pour les paiements)")
        self.check_actif.setChecked(True)
        self.check_actif.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #1e293b;
                padding: 4px;
            }
        """)
        form_layout.addRow("Statut:", self.check_actif)
        
        layout.addWidget(form_group)
        
        # ============================================================
        # INFO
        # ============================================================
        info = QLabel(
            "ℹ️ Le code banque doit être unique. "
            "Il sera utilisé pour identifier la banque dans les paiements."
        )
        info.setStyleSheet("""
            color: #64748b;
            font-size: 11px;
            font-style: italic;
            padding: 8px;
            background-color: #f8fafc;
            border-radius: 6px;
        """)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # ============================================================
        # BOUTONS
        # ============================================================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setStyleSheet("""
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
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton(
            "💾 Enregistrer" if self.is_edit_mode else "✅ Créer la banque"
        )
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 10px 30px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        btn_save.clicked.connect(self.save)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def _style_input(self, widget):
        widget.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)
    
    def load_banque_data(self):
        """Charge les données d'une banque existante"""
        if not self.banque_data:
            return
        self.input_code.setText(self.banque_data.get('code_banque', ''))
        self.input_libelle.setText(self.banque_data.get('libelle', ''))
        self.input_bic.setText(self.banque_data.get('bic_swift', '') or '')
        self.input_pays.setText(self.banque_data.get('pays', '') or '')
        self.input_adresse.setText(self.banque_data.get('adresse', '') or '')
        self.input_telephone.setText(self.banque_data.get('telephone', '') or '')
        self.input_email.setText(self.banque_data.get('email', '') or '')
        self.check_actif.setChecked(self.banque_data.get('est_actif', True))
        
        # En mode édition, le code banque ne doit plus être modifiable
        if self.is_edit_mode:
            self.input_code.setReadOnly(True)
            self.input_code.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 8px 10px;
                    font-size: 12px;
                    background-color: #f8fafc;
                    color: #64748b;
                }
            """)
    
    def save(self):
        """Enregistre la banque (création ou mise à jour)"""
        # ============================================================
        # VALIDATION
        # ============================================================
        code = self.input_code.text().strip().upper()
        libelle = self.input_libelle.text().strip()
        
        if not code:
            QMessageBox.warning(self, "Validation", "Le code banque est obligatoire")
            self.input_code.setFocus()
            return
        
        if len(code) < 2:
            QMessageBox.warning(self, "Validation", "Le code banque doit contenir au moins 2 caractères")
            self.input_code.setFocus()
            return
        
        if not libelle:
            QMessageBox.warning(self, "Validation", "Le libellé est obligatoire")
            self.input_libelle.setFocus()
            return
        
        # Email (validation basique)
        email = self.input_email.text().strip()
        if email and '@' not in email:
            QMessageBox.warning(self, "Validation", "L'email n'est pas valide")
            self.input_email.setFocus()
            return
        
        # ============================================================
        # CONSTRUCTION DES DONNÉES
        # ============================================================
        data = {
            'code_banque': code,
            'libelle': libelle,
            'bic_swift': self.input_bic.text().strip() or None,
            'pays': self.input_pays.text().strip() or None,
            'adresse': self.input_adresse.text().strip() or None,
            'telephone': self.input_telephone.text().strip() or None,
            'email': email or None,
            'est_actif': self.check_actif.isChecked(),
        }
        
        # ============================================================
        # ENVOI
        # ============================================================
        try:
            if self.is_edit_mode:
                # TODO: implémenter la modification (contrôleur non existant)
                QMessageBox.information(
                    self, "Info",
                    "La modification de banque n'est pas encore implémentée.\n"
                    "Utilisez la création pour ajouter de nouvelles banques."
                )
                return
            
            result = self.reglement_controller.creer_banque(data)
            
            if result:
                self.banque_created.emit(result)
                QMessageBox.information(
                    self, "Succès",
                    f"✅ Banque créée avec succès !\n\n"
                    f"🏦 Code : {result.get('code_banque', 'N/A')}\n"
                    f"📛 Libellé : {result.get('libelle', 'N/A')}"
                )
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de créer la banque")
        
        except Exception as e:
            print(f"❌ Erreur création banque: {e}")
            import traceback
            traceback.print_exc()
            
            # Message d'erreur plus lisible si doublon
            err_msg = str(e)
            if 'unique' in err_msg.lower() or 'duplicate' in err_msg.lower():
                QMessageBox.warning(
                    self, "Doublon",
                    f"Une banque avec le code '{code}' existe déjà.\n"
                    f"Veuillez utiliser un code différent."
                )
            else:
                QMessageBox.critical(
                    self, "Erreur",
                    f"Erreur lors de la création : {err_msg}"
                )