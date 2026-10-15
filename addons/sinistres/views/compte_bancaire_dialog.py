"""
Dialogue de création d'un compte bancaire
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QCheckBox,
    QComboBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator


class CompteBancaireDialog(QDialog):
    """Dialogue de création d'un compte bancaire"""
    
    compte_created = Signal(dict)
    
    def __init__(self, reglement_controller, user, parent=None):
        super().__init__(parent)
        self.reglement_controller = reglement_controller
        self.user = user
        self._banques = []
        
        self.setWindowTitle("Nouveau compte bancaire")
        self.setModal(True)
        self.setMinimumWidth(600)
        
        self.setup_ui()
        self.load_banques()
    
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
        
        icon = QLabel("💳")
        icon.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon)
        
        title = QLabel("Créer un compte bancaire")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # ============================================================
        # FORMULAIRE
        # ============================================================
        form_group = QGroupBox("Informations du compte")
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
        
        # Banque (obligatoire)
        self.input_banque = QComboBox()
        self.input_banque.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 12px;
            }
            QComboBox:focus {
                border: 2px solid #1a73e8;
            }
        """)
        self.input_banque.addItem("-- Sélectionner une banque --", None)
        form_layout.addRow("Banque *:", self.input_banque)
        
        # Code banque (obligatoire)
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Ex: ATL-001, ECO-002")
        self.input_code.setMaxLength(20)
        regex = QRegularExpression("^[A-Z0-9\\-]{2,20}$")
        self.input_code.setValidator(QRegularExpressionValidator(regex))
        self._style_input(self.input_code)
        form_layout.addRow("Code compte *:", self.input_code)
        
        # Libellé (obligatoire)
        self.input_libelle = QLineEdit()
        self.input_libelle.setPlaceholderText("Ex: Compte Principal XAF")
        self.input_libelle.setMaxLength(100)
        self._style_input(self.input_libelle)
        form_layout.addRow("Libellé *:", self.input_libelle)
        
        # IBAN (obligatoire, unique)
        self.input_iban = QLineEdit()
        self.input_iban.setPlaceholderText("Ex: CM21 1000 2000 3000 4000 5000 600")
        self.input_iban.setMaxLength(34)
        self._style_input(self.input_iban)
        form_layout.addRow("IBAN *:", self.input_iban)
        
        # BIC / SWIFT
        self.input_bic = QLineEdit()
        self.input_bic.setPlaceholderText("Ex: ATLCCMCX")
        self.input_bic.setMaxLength(11)
        self._style_input(self.input_bic)
        form_layout.addRow("BIC / SWIFT:", self.input_bic)
        
        # Devise (obligatoire)
        self.input_devise = QComboBox()
        self.input_devise.addItems(["XAF", "EUR", "USD", "GBP"])
        self.input_devise.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 12px;
            }
            QComboBox:focus {
                border: 2px solid #1a73e8;
            }
        """)
        form_layout.addRow("Devise *:", self.input_devise)
        
        # Agence
        self.input_agence = QLineEdit()
        self.input_agence.setPlaceholderText("Ex: Agence Centrale Douala")
        self.input_agence.setMaxLength(100)
        self._style_input(self.input_agence)
        form_layout.addRow("Agence:", self.input_agence)
        
        # Solde initial
        self.input_solde = QDoubleSpinBox()
        self.input_solde.setRange(0, 999_999_999_999)
        self.input_solde.setDecimals(2)
        self.input_solde.setValue(0)
        self.input_solde.setSuffix(" FCFA")
        self.input_solde.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 12px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #1a73e8;
            }
        """)
        form_layout.addRow("Solde initial:", self.input_solde)
        
        # Statut
        self.check_actif = QCheckBox("Compte actif (disponible pour les paiements)")
        self.check_actif.setChecked(True)
        self.check_actif.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #1e293b;
                padding: 4px;
            }
        """)
        form_layout.addRow("Statut:", self.check_actif)
        
        # Par défaut
        self.check_defaut = QCheckBox("Compte par défaut (utilisé automatiquement)")
        self.check_defaut.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #1e293b;
                padding: 4px;
            }
        """)
        form_layout.addRow("", self.check_defaut)
        
        layout.addWidget(form_group)
        
        # ============================================================
        # INFO
        # ============================================================
        info = QLabel(
            "ℹ️ Le code compte et l'IBAN doivent être uniques. "
            "Le compte doit être associé à une banque du référentiel."
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
        
        btn_save = QPushButton("✅ Créer le compte")
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
    
    def load_banques(self):
        """Charge la liste des banques disponibles"""
        try:
            banques = self.reglement_controller.get_banques()
            self._banques = banques
            
            for b in banques:
                self.input_banque.addItem(
                    f"{b.get('code_banque', '')} - {b.get('libelle', '')} - {b.get('id', '')}",
                    b.get('id')
                )
        except Exception as e:
            print(f"❌ Erreur chargement banques: {e}")
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les banques: {e}")
    
    def save(self):
        """Enregistre le compte bancaire"""
        # ============================================================
        # VALIDATION
        # ============================================================
        banque_id = self.input_banque.currentData()
        if not banque_id:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner une banque")
            self.input_banque.setFocus()
            return
        
        code = self.input_code.text().strip().upper()
        if not code:
            QMessageBox.warning(self, "Validation", "Le code compte est obligatoire")
            self.input_code.setFocus()
            return
        
        libelle = self.input_libelle.text().strip()
        if not libelle:
            QMessageBox.warning(self, "Validation", "Le libellé est obligatoire")
            self.input_libelle.setFocus()
            return
        
        iban = self.input_iban.text().strip().replace(" ", "").upper()
        if not iban:
            QMessageBox.warning(self, "Validation", "L'IBAN est obligatoire")
            self.input_iban.setFocus()
            return
        
        if len(iban) < 10:
            QMessageBox.warning(self, "Validation", "L'IBAN est trop court")
            self.input_iban.setFocus()
            return
        
        devise = self.input_devise.currentText()
        
        # ============================================================
        # DONNÉES
        # ============================================================
        data = {
            'code_banque': code,
            'libelle': libelle,
            'iban': iban,
            'bic_swift': self.input_bic.text().strip().upper() or None,
            'devise': devise,
            'banque': banque_id,   # ⚠️ FK s'appelle 'banque' dans le modèle
            'agence': self.input_agence.text().strip() or None,
            'solde': float(self.input_solde.value()),
            'statut': "ACTIF" if self.check_actif.isChecked() else "INACTIF",
            'est_actif': self.check_actif.isChecked(),
            'est_par_defaut': self.check_defaut.isChecked(),
        }
        
        # ============================================================
        # ENVOI
        # ============================================================
        try:
            result = self.reglement_controller.creer_compte_bancaire(data)
            
            if result:
                self.compte_created.emit(result)
                QMessageBox.information(
                    self, "Succès",
                    f"✅ Compte bancaire créé avec succès !\n\n"
                    f"💳 Code : {result.get('iban', 'N/A')}\n"
                    f"📛 Libellé : {result.get('libelle', 'N/A')}"
                )
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de créer le compte")
        
        except Exception as e:
            print(f"❌ Erreur création compte: {e}")
            import traceback
            traceback.print_exc()
            
            err_msg = str(e)
            if 'unique' in err_msg.lower() or 'duplicate' in err_msg.lower() or 'UNIQUE' in err_msg:
                QMessageBox.warning(
                    self, "Doublon",
                    f"Un compte avec ce code ou cet IBAN existe déjà.\n"
                    f"Veuillez utiliser des valeurs différentes."
                )
            else:
                QMessageBox.critical(
                    self, "Erreur",
                    f"Erreur lors de la création : {err_msg}"
                )