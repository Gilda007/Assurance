"""
Dialogue de création de mission d'expertise
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QWidget, QFrame,
    QListWidget, QListWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate, QDateTime, QSize
from PySide6.QtGui import QColor, QPixmap, QIcon

from datetime import datetime, timedelta
from pathlib import Path


class MissionDialog(QDialog):
    """Dialogue de création de mission d'expertise"""
    
    mission_created = Signal(dict)
    
    def __init__(self, sinistre_id, expertise_controller, user, 
                 sinistre_info=None, expert_controller=None, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.expertise_controller = expertise_controller
        self.expert_controller = expert_controller  # ✅ NOUVEAU
        self.user = user
        self.sinistre_info = sinistre_info or {}
        
        # ✅ FileService pour les photos
        try:
            from addons.sinistres.services.file_service import get_file_service
            self.file_service = get_file_service()
        except ImportError:
            self.file_service = None
            print("[MissionDialog] FileService non disponible")
        
        self.setWindowTitle("Créer une mission d'expertise")
        self.setModal(True)
        self.setMinimumWidth(750)
        self.setup_ui()
        self.load_experts()   # ✅ NOUVEAU : chargement dynamique
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
            "auto_materiel", "auto_corporel", "batiment", "transport",
            "medical", "judiciaire", "contenant", "marchandise"
        ])
        form_layout.addRow("Type d'expertise *:", self.input_type)
        
        # Domaine spécifique
        self.input_domaine = QLineEdit()
        self.input_domaine.setPlaceholderText("Ex: Carrosserie, Électricité... (optionnel)")
        self.input_domaine.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Domaine:", self.input_domaine)
        
        # ============================================================
        # ✅ SECTION EXPERT AVEC PHOTO
        # ============================================================
        expert_widget = QWidget()
        expert_layout = QHBoxLayout(expert_widget)
        expert_layout.setContentsMargins(0, 0, 0, 0)
        expert_layout.setSpacing(10)
        
        # --- Colonne gauche : sélection expert ---
        left_col = QVBoxLayout()
        left_col.setSpacing(6)
        
        self.input_expert = QComboBox()
        self.input_expert.setEditable(True)
        self.input_expert.setPlaceholderText("Rechercher un expert...")
        self.input_expert.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_expert.addItem("-- Sélectionner un expert --", None)
        left_col.addWidget(self.input_expert)
        
        # Bouton "Nouvel expert"
        self.btn_new_expert = QPushButton("➕ Nouvel expert")
        self.btn_new_expert.setStyleSheet("""
            QPushButton {
                background-color: #f0f9ff;
                color: #0369a1;
                border: 1px solid #bae6fd;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0f2fe;
            }
        """)
        self.btn_new_expert.clicked.connect(self._open_new_expert_dialog)
        left_col.addWidget(self.btn_new_expert)
        
        # Infos expert
        self.lbl_expert_info = QLabel("")
        self.lbl_expert_info.setStyleSheet("color: #64748b; font-size: 11px;")
        self.lbl_expert_info.setWordWrap(True)
        left_col.addWidget(self.lbl_expert_info)
        left_col.addStretch()
        
        expert_layout.addLayout(left_col, 1)
        
        # --- Colonne droite : photo expert ---
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(100, 100)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cbd5e1;
                border-radius: 8px;
                background-color: #f8fafc;
                color: #94a3b8;
                font-size: 11px;
            }
        """)
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setText("📷\nAucune\nphoto")
        expert_layout.addWidget(self.photo_label, 0, Qt.AlignTop)
        
        form_layout.addRow("Expert *:", expert_widget)
        
        # ============================================================
        # DATES
        # ============================================================
        self.input_date_mission = QDateEdit()
        self.input_date_mission.setDate(QDate.currentDate())
        self.input_date_mission.setCalendarPopup(True)
        self.input_date_mission.setStyleSheet("border: 2px solid #1a73e8; border-radius: 6px; padding: 4px;")
        form_layout.addRow("Date de mission *:", self.input_date_mission)
        
        self.input_echeance = QDateEdit()
        self.input_echeance.setDate(QDate.currentDate().addDays(14))
        self.input_echeance.setCalendarPopup(True)
        self.input_echeance.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Date d'échéance *:", self.input_echeance)
        
        # Montant estimé
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
                padding: 10px 30px; border-radius: 8px; font-weight: bold;
                background-color: #f1f5f9; color: #64748b;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        self.btn_annuler.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_annuler)
        
        self.btn_creer = QPushButton("✅ Créer la mission")
        self.btn_creer.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8; color: white;
                padding: 10px 40px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1557b0; }
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
        self.input_expert.currentIndexChanged.connect(self._on_expert_changed)  # ✅
    
    # ============================================================
    # ✅ CHARGEMENT DES EXPERTS
    # ============================================================
    
    def load_experts(self):
        """Charge la liste des experts depuis la BDD"""
        try:
            self.input_expert.clear()
            self.input_expert.addItem("-- Sélectionner un expert --", None)
            
            if not self.expert_controller:
                print("❌ [MissionDialog] expert_controller non fourni")
                self.input_expert.addItem("⚠️ Contrôleur indisponible", None)
                return
            
            # ✅ Utiliser la BONNE méthode du contrôleur
            experts = self.expert_controller.get_experts_actifs()
            
            print(f"🔍 [MissionDialog] {len(experts)} expert(s) récupéré(s)")
            
            if not experts:
                self.input_expert.addItem("⚠️ Aucun expert disponible", None)
                return
            
            for expert in experts:
                # expert est déjà un dict sérialisé par _serialize_expert()
                nom = expert.get('nom', '') or ''
                prenom = expert.get('prenom', '') or ''
                
                # ✅ Utiliser 'domaines' (liste) au lieu de 'specialite'
                domaines = expert.get('domaines', []) or []
                domaine_str = ", ".join(domaines) if domaines else ''
                
                # ✅ Fallback sur 'agrement' si pas de domaine
                if not domaine_str and expert.get('agrement'):
                    domaine_str = expert['agrement']
                
                label = f"{nom} {prenom}".strip() or f"Expert #{expert.get('id')}"
                if domaine_str:
                    label += f" - {domaine_str}"
                
                print(f"🔍 [MissionDialog] Ajout: {label}")
                self.input_expert.addItem(label, expert)
            
            print(f"✅ [MissionDialog] {len(experts)} expert(s) chargé(s)")
        
        except Exception as e:
            print(f"❌ [MissionDialog] Erreur load_experts: {e}")
            import traceback
            traceback.print_exc()
            self.input_expert.addItem(f"⚠️ Erreur: {e}", None)

    def _on_expert_changed(self, index):
        """Met à jour la photo et les infos quand l'expert change"""
        expert = self.input_expert.currentData()
        
        if not expert:
            self.photo_label.setText("📷\nAucune\nphoto")
            self.photo_label.setPixmap(QPixmap())
            self.lbl_expert_info.setText("")
            self._update_summary()
            return
        
        # ✅ Infos textuelles — utiliser les bons champs du _serialize_expert()
        info_lines = []
        if expert.get('email'):
            info_lines.append(f"📧 {expert['email']}")
        
        # ✅ 'portable' ou 'telephone'
        tel = expert.get('portable') or expert.get('telephone')
        if tel:
            info_lines.append(f"📞 {tel}")
        
        if expert.get('code'):
            info_lines.append(f"🆔 {expert['code']}")
        
        if expert.get('agrement'):
            info_lines.append(f"📜 Agrément: {expert['agrement']}")
        
        if expert.get('ville'):
            info_lines.append(f"📍 {expert['ville']}")
        
        self.lbl_expert_info.setText("\n".join(info_lines))
        
        # ✅ Photo de l'expert
        self._load_expert_photo(expert)
        
        self._update_summary()

    def _load_expert_photo(self, expert):
        """Charge et affiche la photo de l'expert"""
        photo_path = expert.get('photo_path')
        
        if not photo_path or not self.file_service:
            self.photo_label.setText("📷\nAucune\nphoto")
            return
        
        # Récupérer le chemin absolu
        abs_path = self.file_service.get_absolute_path(photo_path)
        
        if not abs_path or not Path(abs_path).exists():
            self.photo_label.setText("📷\nPhoto\nintrouvable")
            return
        
        # Charger et redimensionner
        pixmap = QPixmap(abs_path)
        if pixmap.isNull():
            self.photo_label.setText("📷\nErreur\nchargement")
            return
        
        scaled = pixmap.scaled(
            100, 100,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.photo_label.setPixmap(scaled)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 2px solid #1a73e8;
                border-radius: 8px;
                background-color: #f8fafc;
            }
        """)
    
    # ============================================================
    # ✅ CRÉATION D'UN NOUVEL EXPERT
    # ============================================================
    
    def _open_new_expert_dialog(self):
        """Ouvre le dialogue de création d'un nouvel expert"""
        try:
            from addons.sinistres.views.dialogs_files.expert_dialog import ExpertDialog
        except ImportError:
            try:
                from addons.sinistres.views.dialogs_files.expert_dialog import ExpertDialog
            except ImportError:
                QMessageBox.warning(
                    self, "Indisponible",
                    "Le dialogue de création d'expert n'est pas disponible.\n"
                    "Vérifiez que expert_dialog.py existe."
                )
                return
        
        if not self.expert_controller:
            QMessageBox.warning(
                self, "Indisponible",
                "Le contrôleur des experts n'est pas disponible."
            )
            return
        
        dialog = ExpertDialog(
            expert_controller=self.expert_controller,
            user=self.user,
            parent=self
        )
        
        if dialog.exec() == QDialog.Accepted:
            # Recharger la liste
            self.load_experts()
            
            # Sélectionner le nouvel expert
            new_expert = getattr(dialog, 'created_expert', None)
            if new_expert:
                for i in range(self.input_expert.count()):
                    data = self.input_expert.itemData(i)
                    if data and data.get('id') == new_expert.get('id'):
                        self.input_expert.setCurrentIndex(i)
                        break
    
    # ============================================================
    # SUITE (inchangé)
    # ============================================================
    
    def load_data(self):
        self._update_summary()
    
    def _update_summary(self):
        lines = []
        type_text = self.input_type.currentText()
        if type_text:
            lines.append(f"📌 Type: {type_text.replace('_', ' ').title()}")
        
        domaine = self.input_domaine.text().strip()
        if domaine:
            lines.append(f"🔧 Domaine: {domaine}")
        
        expert = self.input_expert.currentData()
        if expert:
            nom = f"{expert.get('nom', '')} {expert.get('prenom', '')}".strip()
            lines.append(f"👤 Expert: {nom}")
            
            # ✅ Vérifier les domaines
            domaines = expert.get('domaines', []) or []
            if domaines:
                lines.append(f"   🔧 Domaines: {', '.join(domaines)}")
            
            # ✅ Photo
            if expert.get('photo_path'):
                lines.append("   📷 Photo: ✅")
            else:
                lines.append("   📷 Photo: ❌")
        else:
            lines.append("⚠️ Expert non sélectionné")
        
        date_mission = self.input_date_mission.date()
        lines.append(f"📅 Date de mission: {date_mission.toString('dd/MM/yyyy')}")
        
        echeance = self.input_echeance.date()
        lines.append(f"📅 Échéance: {echeance.toString('dd/MM/yyyy')}")
        
        montant = self.input_montant.value()
        if montant > 0:
            lines.append(f"💰 Montant estimé: {montant:,.0f} FCFA")
        else:
            lines.append("💰 Montant estimé: Non défini")
        
        self.summary_text.setText("\n".join(lines))
    
    def creer_mission(self):
        try:
            if not self.input_type.currentText():
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un type d'expertise")
                return
            
            expert = self.input_expert.currentData()
            if not expert:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un expert")
                return
            
            expert_id = expert.get('id')
            
            date_mission = self.input_date_mission.date().toPython()
            if not date_mission:
                QMessageBox.warning(self, "Validation", "Veuillez saisir une date de mission")
                return
            
            echeance = self.input_echeance.date().toPython()
            if not echeance:
                QMessageBox.warning(self, "Validation", "Veuillez saisir une date d'échéance")
                return
            
            if date_mission > echeance:
                QMessageBox.warning(
                    self, "Validation",
                    "La date de mission ne peut pas être postérieure à la date d'échéance"
                )
                return
            
            data = {
                'sinistre_id': self.sinistre_id,
                'type_expertise': self.input_type.currentText(),
                'domaine': self.input_domaine.text().strip() or None,
                'expert_id': expert_id,
                'date_mission': date_mission,
                'date_echeance': echeance,
                'montant_estime': self.input_montant.value() or None,
                'observations': self.input_observations.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            print(f"📝 Création mission avec les données: {data}")
            result = self.expertise_controller.creer_mission(data)
            
            if result:
                self.mission_created.emit(result)
                QMessageBox.information(
                    self, "Succès",
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