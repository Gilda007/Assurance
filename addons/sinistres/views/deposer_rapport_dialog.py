"""
Dialogue de dépôt de rapport d'expertise
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QFrame, QFileDialog,
    QProgressBar, QCheckBox, QSpinBox, QListWidgetItem, QListWidget
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor

from datetime import datetime
import os


class DeposerRapportDialog(QDialog):
    """Dialogue de dépôt de rapport d'expertise"""
    
    rapport_depose = Signal(dict)  # Émis quand le rapport est déposé
    MAX_FILE_SIZE = 50 * 1024 * 1024  # ✅ 50 MB
    
    def __init__(self, mission_id, mission_info, expertise_controller, user, parent=None):
        super().__init__(parent)
        self.mission_id = mission_id
        self.mission_info = mission_info or {}
        self.expertise_controller = expertise_controller
        self.user = user
        self.files = []  # ✅ Liste des fichiers sélectionnés
        self.file_details = []  # ✅ Détails des fichiers
        
        self.setWindowTitle("Déposer un rapport d'expertise")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # ============================================================
        # EN-TÊTE AVEC INFOS MISSION
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
        
        title = QLabel("📄 Dépôt de rapport d'expertise")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        
        self.lbl_mission = QLabel(f"Mission: {self.mission_info.get('numero_mission', 'N/A')}")
        info_layout.addWidget(self.lbl_mission)
        
        self.lbl_expert = QLabel(f"Expert: {self.mission_info.get('expert_nom', 'N/A')}")
        info_layout.addWidget(self.lbl_expert)
        
        self.lbl_type = QLabel(f"Type: {self.mission_info.get('type_expertise', 'N/A')}")
        info_layout.addWidget(self.lbl_type)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        layout.addWidget(header_frame)
        
        # ============================================================
        # SECTION 1: CONTENU DU RAPPORT
        # ============================================================
        form_group1 = QGroupBox("Contenu du rapport")
        form_group1.setStyleSheet("""
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
        form_layout1 = QFormLayout(form_group1)
        form_layout1.setSpacing(12)
        
        # Contenu du rapport
        self.input_contenu = QTextEdit()
        self.input_contenu.setPlaceholderText("""
Rapport d'expertise

1. Observations:
   - ...

2. Constatations:
   - ...

3. Préconisations:
   - ...

4. Conclusion:
   - ...
        """.strip())
        self.input_contenu.setMinimumHeight(150)
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
        form_layout1.addRow("Contenu du rapport *:", self.input_contenu)
        
        layout.addWidget(form_group1)
        
        # ============================================================
        # SECTION 2: INFORMATIONS COMPLÉMENTAIRES
        # ============================================================
        form_group2 = QGroupBox("Informations complémentaires")
        form_group2.setStyleSheet("""
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
        form_layout2 = QFormLayout(form_group2)
        form_layout2.setSpacing(12)
        
        # Montant estimé
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999999999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        self.input_montant.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout2.addRow("Montant estimé:", self.input_montant)
        
        # Date du rapport
        self.input_date_rapport = QDateEdit()
        self.input_date_rapport.setDate(QDate.currentDate())
        self.input_date_rapport.setCalendarPopup(True)
        self.input_date_rapport.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout2.addRow("Date du rapport:", self.input_date_rapport)
        
        layout.addWidget(form_group2)
        
        # ============================================================
        # SECTION 3: PIÈCES JOINTES (MULTIPLES FICHIERS)
        # ============================================================
        form_group3 = QGroupBox("Pièces jointes")
        form_group3.setStyleSheet("""
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
        form_layout3 = QVBoxLayout(form_group3)

        # Boutons d'ajout/suppression
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_ajouter_fichier = QPushButton("📁 Ajouter des fichiers")
        self.btn_ajouter_fichier.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border-radius: 6px;
                background-color: #1a73e8;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_ajouter_fichier.clicked.connect(self.ajouter_fichiers)
        btn_layout.addWidget(self.btn_ajouter_fichier)

        self.btn_supprimer_fichier = QPushButton("🗑️ Supprimer")
        self.btn_supprimer_fichier.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border-radius: 6px;
                background-color: #ef4444;
                color: white;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.btn_supprimer_fichier.clicked.connect(self.supprimer_fichier)
        btn_layout.addWidget(self.btn_supprimer_fichier)

        btn_layout.addStretch()
        form_layout3.addLayout(btn_layout)

        # Liste des fichiers
        self.liste_fichiers = QListWidget()
        self.liste_fichiers.setStyleSheet("""
            QListWidget {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 5px;
                min-height: 100px;
                max-height: 150px;
            }
            QListWidget::item {
                padding: 5px 10px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #f1f5f9;
            }
            QListWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
        """)
        form_layout3.addWidget(self.liste_fichiers)

        # Information sur les formats acceptés
        info_label = QLabel("📌 Formats acceptés: PDF, DOCX, JPG, PNG, ZIP, RAR | Taille max: 50 MB par fichier")
        info_label.setStyleSheet("color: #64748b; font-size: 11px;")
        form_layout3.addWidget(info_label)

        layout.addWidget(form_group3)
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
        
        summary_title = QLabel("📋 Récapitulatif du rapport")
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
        
        self.btn_deposer = QPushButton("📤 Déposer le rapport")
        self.btn_deposer.setStyleSheet("""
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
        self.btn_deposer.clicked.connect(self.deposer_rapport)
        btn_layout.addWidget(self.btn_deposer)
        
        layout.addLayout(btn_layout)
        
        # ============================================================
        # CONNEXIONS
        # ============================================================
        self.input_contenu.textChanged.connect(self._update_summary)
        self.input_montant.valueChanged.connect(self._update_summary)
        # self.file_path_display.textChanged.connect(self._update_summary)
    
    def ajouter_fichiers(self):
        """Ajoute des fichiers à la liste"""
        file_filter = "Tous les fichiers (*.*);;PDF Files (*.pdf);;Word Files (*.docx);;Images (*.jpg *.png);;ZIP Archive (*.zip)"
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner les fichiers à joindre",
            "",
            file_filter
        )
        
        if not file_paths:
            return
        
        for file_path in file_paths:
            # Vérifier la taille
            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                QMessageBox.warning(
                    self,
                    "Taille excessive",
                    f"Le fichier {os.path.basename(file_path)} dépasse la taille maximale (50 MB)."
                )
                continue
            
            # Vérifier si le fichier est déjà dans la liste
            if file_path in self.files:
                continue
            
            self.files.append(file_path)
            self.file_details.append({
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': file_size,
                'size_str': self._format_size(file_size)
            })
            
            # Ajouter à la liste
            item = QListWidgetItem(f"📄 {os.path.basename(file_path)} ({self._format_size(file_size)})")
            item.setData(Qt.UserRole, file_path)
            self.liste_fichiers.addItem(item)
        
        self._update_summary()

    def supprimer_fichier(self):
        """Supprime le fichier sélectionné de la liste"""
        current_row = self.liste_fichiers.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un fichier à supprimer")
            return
        
        # Supprimer de la liste
        self.liste_fichiers.takeItem(current_row)
        
        # Supprimer des listes internes
        if current_row < len(self.files):
            del self.files[current_row]
            del self.file_details[current_row]
        
        self._update_summary()

    def _format_size(self, size: int) -> str:
        """Formate la taille du fichier"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _update_summary(self):
        """Met à jour le récapitulatif"""
        lines = []
        
        # Contenu
        contenu = self.input_contenu.toPlainText().strip()
        if contenu:
            lines.append(f"📝 Contenu: {len(contenu)} caractères")
        else:
            lines.append("⚠️ Contenu non saisi")
        
        # Montant
        montant = self.input_montant.value()
        if montant > 0:
            lines.append(f"💰 Montant estimé: {montant:,.0f} FCFA")
        else:
            lines.append("💰 Montant estimé: Non défini")
        
        # Fichiers
        if self.files:
            total_size = sum(f['size'] for f in self.file_details)
            lines.append(f"📎 {len(self.files)} fichier(s) joint(s) ({self._format_size(total_size)})")
            for f in self.file_details:
                lines.append(f"   - {f['name']} ({f['size_str']})")
        else:
            lines.append("⚠️ Aucun fichier joint")
        
        self.summary_text.setText("\n".join(lines))
    
    # def deposer_rapport(self):
    #     """Dépose le rapport d'expertise"""
    #     try:
    #         # ============================================================
    #         # VALIDATION
    #         # ============================================================
            
    #         # Vérifier le contenu
    #         contenu = self.input_contenu.toPlainText().strip()
    #         if not contenu:
    #             QMessageBox.warning(self, "Validation", "Veuillez saisir le contenu du rapport")
    #             return
            
    #         if len(contenu) < 20:
    #             reply = QMessageBox.question(
    #                 self,
    #                 "Confirmation",
    #                 "Le rapport est très court (moins de 20 caractères).\n"
    #                 "Voulez-vous continuer ?",
    #                 QMessageBox.Yes | QMessageBox.No
    #             )
    #             if reply == QMessageBox.No:
    #                 return
            
    #         # Vérifier le fichier (optionnel)
    #         if not self.selected_file_path:
    #             reply = QMessageBox.question(
    #                 self,
    #                 "Confirmation",
    #                 "Aucun fichier n'est joint.\n"
    #                 "Voulez-vous continuer ?",
    #                 QMessageBox.Yes | QMessageBox.No
    #             )
    #             if reply == QMessageBox.No:
    #                 return
            
    #         # ============================================================
    #         # CONSTRUCTION DES DONNÉES
    #         # ============================================================
    #         data = {
    #             'rapport_contenu': contenu,
    #             'montant_estime': self.input_montant.value() or None,
    #             'date_rapport': self.input_date_rapport.date().toPython().isoformat(),
    #             'rapport_path': self.selected_file_path if self.selected_file_path else None,
    #             'updated_by': self.user.id if self.user else None
    #         }
            
    #         # ============================================================
    #         # ENVOI
    #         # ============================================================
    #         print(f"📝 Dépôt rapport avec les données: {data}")
            
    #         result = self.expertise_controller.deposer_rapport(
    #             self.mission_id,
    #             data
    #         )
            
    #         if result:
    #             self.rapport_depose.emit({
    #                 'mission_id': self.mission_id,
    #                 'contenu': contenu[:100] + '...' if len(contenu) > 100 else contenu,
    #                 'montant_estime': data['montant_estime'],
    #                 'fichier': self.selected_file_path
    #             })
    #             QMessageBox.information(
    #                 self,
    #                 "Succès",
    #                 f"✅ Rapport déposé avec succès !\n\n"
    #                 f"📌 Mission: {self.mission_info.get('numero_mission', 'N/A')}\n"
    #                 f"💰 Montant estimé: {data['montant_estime']:,.0f} FCFA\n"
    #                 f"📎 Fichier: {os.path.basename(self.selected_file_path) if self.selected_file_path else 'Aucun'}\n"
    #                 f"📌 Statut: RAPPORT REÇU"
    #             )
    #             self.accept()
            
    #     except Exception as e:
    #         print(f"❌ Erreur dépôt rapport: {e}")
    #         import traceback
    #         traceback.print_exc()
    #         QMessageBox.critical(self, "Erreur", f"Erreur lors du dépôt: {str(e)}")

    def deposer_rapport(self):
        """Dépose le rapport d'expertise"""
        try:
            # ============================================================
            # VALIDATION
            # ============================================================
            
            # Vérifier le contenu
            contenu = self.input_contenu.toPlainText().strip()
            if not contenu:
                QMessageBox.warning(self, "Validation", "Veuillez saisir le contenu du rapport")
                return
            
            if len(contenu) < 20:
                reply = QMessageBox.question(
                    self,
                    "Confirmation",
                    "Le rapport est très court (moins de 20 caractères).\n"
                    "Voulez-vous continuer ?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            # Vérifier les fichiers (optionnel)
            if not self.files:
                reply = QMessageBox.question(
                    self,
                    "Confirmation",
                    "Aucun fichier n'est joint.\n"
                    "Voulez-vous continuer ?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            # ============================================================
            # CONSTRUCTION DES DONNÉES
            # ============================================================
            data = {
                'rapport_contenu': contenu,
                'montant_estime': self.input_montant.value() or None,
                'date_rapport': self.input_date_rapport.date().toPython().isoformat(),
                'files': self.files,  # ✅ Liste des fichiers
                'updated_by': self.user.id if self.user else None
            }
            
            # ============================================================
            # ENVOI
            # ============================================================
            print(f"📝 Dépôt rapport avec {len(self.files)} fichier(s)")
            
            result = self.expertise_controller.deposer_rapport(
                self.mission_id,
                data
            )
            
            if result:
                self.rapport_depose.emit({
                    'mission_id': self.mission_id,
                    'contenu': contenu[:100] + '...' if len(contenu) > 100 else contenu,
                    'montant_estime': data['montant_estime'],
                    'files': self.files,
                    'nb_files': len(self.files)
                })
                
                file_list = "\n".join([f"   - {os.path.basename(f)}" for f in self.files])
                QMessageBox.information(
                    self,
                    "Succès",
                    f"✅ Rapport déposé avec succès !\n\n"
                    f"📌 Mission: {self.mission_info.get('numero_mission', 'N/A')}\n"
                    f"💰 Montant estimé: {data['montant_estime']:,.0f} FCFA\n"
                    f"📎 {len(self.files)} fichier(s) joint(s):\n{file_list}\n"
                    f"📌 Statut: RAPPORT REÇU"
                )
                self.accept()
                
        except Exception as e:
            print(f"❌ Erreur dépôt rapport: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors du dépôt: {str(e)}")

    