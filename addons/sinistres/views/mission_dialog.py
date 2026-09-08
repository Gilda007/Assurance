"""
Dialogue de création de mission d'expertise
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QWidget, QFrame
)
from PySide6.QtCore import Qt, Signal, QDate, QDateTime
from PySide6.QtGui import QColor

from datetime import datetime, timedelta


class MissionDialog(QDialog):
    """Dialogue de création de mission d'expertise"""
    
    mission_created = Signal(dict)
    
    def __init__(self, sinistre_id, expertise_controller, user, sinistre_info=None, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.expertise_controller = expertise_controller
        self.user = user
        self.sinistre_info = sinistre_info or {}
        
        self.setWindowTitle("Créer une mission d'expertise")
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
        
        title = QLabel("📋 Mission d'expertise")
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
        # SECTION 1: INFORMATIONS DE LA MISSION
        # ============================================================
        form_group = QGroupBox("Informations de la mission")
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
        
        # Type d'expertise
        self.input_type = QComboBox()
        self.input_type.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_type.addItems([
            "auto_materiel",
            "auto_corporel",
            "batiment",
            "transport",
            "medical",
            "judiciaire",
            "contenant",
            "marchandise"
        ])
        form_layout.addRow("Type d'expertise *:", self.input_type)
        
        # Domaine spécifique
        self.input_domaine = QLineEdit()
        self.input_domaine.setPlaceholderText("Ex: Carrosserie, Électricité... (optionnel)")
        self.input_domaine.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Domaine:", self.input_domaine)
        
        # Expert
        self.input_expert = QComboBox()
        self.input_expert.setEditable(True)
        self.input_expert.setPlaceholderText("Rechercher un expert...")
        self.input_expert.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_expert.addItem("-- Sélectionner un expert --", None)
        # TODO: Charger les experts depuis la base
        self.input_expert.addItem("Expert 1 - Auto", 1)
        self.input_expert.addItem("Expert 2 - Bâtiment", 2)
        form_layout.addRow("Expert *:", self.input_expert)
        
        # ✅ NOUVEAU : Date de mission (obligatoire)
        self.input_date_mission = QDateEdit()
        self.input_date_mission.setDate(QDate.currentDate())
        self.input_date_mission.setCalendarPopup(True)
        self.input_date_mission.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        form_layout.addRow("Date de mission *:", self.input_date_mission)
        
        # Date d'échéance
        self.input_echeance = QDateEdit()
        self.input_echeance.setDate(QDate.currentDate().addDays(14))
        self.input_echeance.setCalendarPopup(True)
        self.input_echeance.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Date d'échéance *:", self.input_echeance)
        
        # Montant estimé (optionnel)
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999999999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        self.input_montant.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Montant estimé:", self.input_montant)
        
        layout.addWidget(form_group)
        
        # ============================================================
        # SECTION 2: OBSERVATIONS
        # ============================================================
        self.input_observations = QTextEdit()
        self.input_observations.setPlaceholderText("Observations, instructions particulières pour l'expert...")
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
        
        summary_title = QLabel("📋 Récapitulatif de la mission")
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
        
        self.btn_creer = QPushButton("✅ Créer la mission")
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
        self.btn_creer.clicked.connect(self.creer_mission)
        btn_layout.addWidget(self.btn_creer)
        
        layout.addLayout(btn_layout)
        
        # ============================================================
        # CONNEXIONS
        # ============================================================
        self.input_type.currentIndexChanged.connect(self._update_summary)
        self.input_domaine.textChanged.connect(self._update_summary)
        self.input_date_mission.dateChanged.connect(self._update_summary)
        self.input_echeance.dateChanged.connect(self._update_summary)
        self.input_montant.valueChanged.connect(self._update_summary)
        self.input_expert.currentIndexChanged.connect(self._update_summary)
    
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
        
        # Domaine
        domaine = self.input_domaine.text().strip()
        if domaine:
            lines.append(f"🔧 Domaine: {domaine}")
        
        # Expert
        expert_index = self.input_expert.currentIndex()
        if expert_index > 0:
            expert_text = self.input_expert.currentText()
            lines.append(f"👤 Expert: {expert_text}")
        else:
            lines.append("⚠️ Expert non sélectionné")
        
        # Date de mission
        date_mission = self.input_date_mission.date()
        lines.append(f"📅 Date de mission: {date_mission.toString('dd/MM/yyyy')}")
        
        # Échéance
        echeance = self.input_echeance.date()
        lines.append(f"📅 Échéance: {echeance.toString('dd/MM/yyyy')}")
        
        # Montant
        montant = self.input_montant.value()
        if montant > 0:
            lines.append(f"💰 Montant estimé: {montant:,.0f} FCFA")
        else:
            lines.append("💰 Montant estimé: Non défini")
        
        self.summary_text.setText("\n".join(lines))
    
    def creer_mission(self):
        """Crée la mission d'expertise"""
        try:
            # ============================================================
            # VALIDATION
            # ============================================================
            
            # Vérifier le type
            if not self.input_type.currentText():
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un type d'expertise")
                return
            
            # Vérifier l'expert
            expert_id = self.input_expert.currentData()
            if not expert_id:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un expert")
                return
            
            # ✅ Vérifier la date de mission
            date_mission = self.input_date_mission.date().toPython()
            if not date_mission:
                QMessageBox.warning(self, "Validation", "Veuillez saisir une date de mission")
                return
            
            # Vérifier la date d'échéance
            echeance = self.input_echeance.date().toPython()
            if not echeance:
                QMessageBox.warning(self, "Validation", "Veuillez saisir une date d'échéance")
                return
            
            # ✅ Vérifier que la date de mission n'est pas après la date d'échéance
            if date_mission > echeance:
                QMessageBox.warning(
                    self, 
                    "Validation", 
                    "La date de mission ne peut pas être postérieure à la date d'échéance"
                )
                return
            
            # ============================================================
            # CONSTRUCTION DES DONNÉES
            # ============================================================
            data = {
                'sinistre_id': self.sinistre_id,
                'type_expertise': self.input_type.currentText(),
                'domaine': self.input_domaine.text().strip() or None,
                'expert_id': expert_id,
                'date_mission': date_mission,  # ✅ Ajout de la date de mission
                'date_echeance': echeance,
                'montant_estime': self.input_montant.value() or None,
                'observations': self.input_observations.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            # ============================================================
            # ENVOI
            # ============================================================
            print(f"📝 Création mission avec les données: {data}")
            
            result = self.expertise_controller.creer_mission(data)
            
            if result:
                self.mission_created.emit(result)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"✅ Mission d'expertise créée avec succès !\n\n"
                    f"📌 N° Mission: {result.get('numero_mission', 'N/A')}\n"
                    f"👤 Expert: {result.get('expert_nom', 'N/A')}\n"
                    f"📅 Date de mission: {result.get('date_mission', '')[:10]}\n"
                    f"📅 Échéance: {result.get('date_echeance', '')[:10]}\n"
                    f"📌 Statut: CRÉÉE"
                )
                self.accept()
            
        except Exception as e:
            print(f"❌ Erreur création mission: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")