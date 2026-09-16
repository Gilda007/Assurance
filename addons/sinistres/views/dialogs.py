"""
Dialogue pour les actions LOMETA
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QFileDialog, QWidget, QFrame
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
    """Dialogue d'ajout de dommage avec support photos"""
    
    def __init__(self, sinistre_id, controller, user, referentiel_controller=None, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.controller = controller
        self.user = user
        self.referentiel_controller = referentiel_controller
        self._photos = []  # Liste des chemins de photos
        
        self.setWindowTitle("Ajouter un dommage")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(550)
        self.setup_ui()
    
    def setup_ui(self):
        from PySide6.QtWidgets import (
            QScrollArea, QGridLayout, QFrame
        )
        
        root = QVBoxLayout(self)
        root.setSpacing(15)
        root.setContentsMargins(20, 20, 20, 20)
        
        # ============================================================
        # SECTION 1 : Informations principales
        # ============================================================
        form_group = QGroupBox("Informations du dommage")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 10px;
                color: #1e293b;
            }
        """)
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(12)
        
        # Type de dommage
        from addons.sinistres.views.helpers.referentiel_helper import ReferentielHelper

        self.input_type = QComboBox()
        ReferentielHelper.populate_combo(
            combo=self.input_type,
            famille="dommages",
            controller=self.controller.referentiel_controller,  # à passer au dialogue
            selected_code=dommage_data.get('type_dommage') if dommage_data else None
        )
        self.input_type.setStyleSheet(self._input_style())
        form_layout.addRow("Type *:", self.input_type)
        
        # Code dommage (optionnel)
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Référence interne (optionnel)")
        self.input_code.setStyleSheet(self._input_style())
        form_layout.addRow("Code:", self.input_code)
        
        # Description
        self.input_description = QTextEdit()
        self.input_description.setMaximumHeight(90)
        self.input_description.setPlaceholderText(
            "Décrivez le dommage : localisation, étendue, observations..."
        )
        self.input_description.setStyleSheet(self._input_style())
        form_layout.addRow("Description:", self.input_description)
        
        # Montant estimé
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999_999_999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        self.input_montant.setStyleSheet(self._input_style())
        form_layout.addRow("Montant estimé:", self.input_montant)
        
        root.addWidget(form_group)
        
        # ============================================================
        # SECTION 2 : Photos
        # ============================================================
        photos_group = QGroupBox("Photos du dommage")
        photos_group.setStyleSheet(form_group.styleSheet())
        photos_layout = QVBoxLayout(photos_group)
        photos_layout.setSpacing(10)
        
        # Barre d'action
        action_row = QHBoxLayout()
        
        self.btn_add_photo = QPushButton("📷  Ajouter des photos")
        self.btn_add_photo.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_add_photo.setCursor(Qt.PointingHandCursor)
        self.btn_add_photo.clicked.connect(self._ajouter_photos)
        action_row.addWidget(self.btn_add_photo)
        
        action_row.addStretch()
        
        self.lbl_count = QLabel("0 photo(s)")
        self.lbl_count.setStyleSheet("color: #64748b; font-size: 11px;")
        action_row.addWidget(self.lbl_count)
        
        photos_layout.addLayout(action_row)
        
        # Zone de prévisualisation (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #f8fafc;
                border: 1px dashed #cbd5e1;
                border-radius: 8px;
            }
        """)
        scroll.setMinimumHeight(140)
        scroll.setMaximumHeight(180)
        
        self.photos_container = QWidget()
        self.photos_container.setStyleSheet("background-color: transparent;")
        self.photos_grid = QGridLayout(self.photos_container)
        self.photos_grid.setContentsMargins(10, 10, 10, 10)
        self.photos_grid.setSpacing(10)
        
        scroll.setWidget(self.photos_container)
        photos_layout.addWidget(scroll)
        
        # Message vide
        self.lbl_empty = QLabel("Aucune photo ajoutée\nCliquez sur « Ajouter des photos » pour commencer")
        self.lbl_empty.setStyleSheet("""
            color: #94a3b8;
            font-size: 11px;
            font-style: italic;
        """)
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        photos_layout.addWidget(self.lbl_empty)
        
        root.addWidget(photos_group)
        
        # ============================================================
        # BOUTONS
        # ============================================================
        btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        btn_box.button(QDialogButtonBox.Ok).setText("💾  Enregistrer")
        btn_box.button(QDialogButtonBox.Ok).setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        btn_box.button(QDialogButtonBox.Cancel).setText("Annuler")
        btn_box.button(QDialogButtonBox.Cancel).setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #64748b;
                padding: 8px 20px;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f8fafc;
            }
        """)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        root.addWidget(btn_box)
    
    def _input_style(self) -> str:
        return """
            QLineEdit, QComboBox, QTextEdit, QDoubleSpinBox {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #1e293b;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDoubleSpinBox:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """
    
    # ============================================================
    # GESTION DES PHOTOS
    # ============================================================
    
    def _ajouter_photos(self):
        """Ouvre le sélecteur de fichiers pour ajouter des photos"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner des photos",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;Tous les fichiers (*)"
        )
        
        if not files:
            return
        
        for path in files:
            if path not in self._photos:
                self._photos.append(path)
        
        self._refresh_photos()
    
    def _refresh_photos(self):
        """Reconstruit la grille des vignettes"""
        from addons.sinistres.views.widgets.damage_widgets import PhotoThumbnail
        
        # Vider la grille
        while self.photos_grid.count():
            item = self.photos_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Vider aussi les widgets vides restants
        for i in reversed(range(self.photos_grid.count())):
            item = self.photos_grid.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        
        # Message vide
        if not self._photos:
            self.lbl_empty.show()
            self.lbl_count.setText("0 photo(s)")
            return
        
        self.lbl_empty.hide()
        self.lbl_count.setText(f"{len(self._photos)} photo(s)")
        
        # Ajouter les vignettes (4 par ligne)
        for i, path in enumerate(self._photos):
            container = self._make_photo_thumbnail(path, i)
            row = i // 4
            col = i % 4
            self.photos_grid.addWidget(container, row, col)
        
        # Ajouter un stretch à la fin
        self.photos_grid.setRowStretch(self.photos_grid.rowCount(), 1)
    
    def _make_photo_thumbnail(self, path: str, index: int) -> QWidget:
        """Crée une vignette avec bouton supprimer"""
        from PySide6.QtGui import QPixmap
        
        container = QFrame()
        container.setFixedSize(90, 90)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            QFrame:hover {
                border: 2px solid #1a73e8;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        # Vignette image
        thumb = QLabel()
        thumb.setFixedSize(84, 70)
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setStyleSheet("border: none; background-color: transparent;")
        thumb.setCursor(Qt.PointingHandCursor)
        
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(84, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumb.setPixmap(scaled)
            thumb.setToolTip("Cliquer pour agrandir")
            thumb.mousePressEvent = lambda e, p=path, i=index: self._preview_photo(p, i)
        else:
            thumb.setText("❓")
            thumb.setStyleSheet("font-size: 24px;")
        
        layout.addWidget(thumb)
        
        # Bouton supprimer
        btn_del = QPushButton("✖")
        btn_del.setFixedSize(84, 14)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setStyleSheet("""
            QPushButton {
                background-color: #fee2e2;
                color: #dc2626;
                border: none;
                border-radius: 4px;
                font-size: 9px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
                color: white;
            }
        """)
        btn_del.clicked.connect(lambda checked=False, p=path: self._supprimer_photo(p))
        layout.addWidget(btn_del)
        
        return container
    
    def _supprimer_photo(self, path: str):
        """Supprime une photo de la liste"""
        if path in self._photos:
            self._photos.remove(path)
            self._refresh_photos()
    
    def _preview_photo(self, path: str, index: int):
        """Ouvre l'aperçu en grand"""
        from addons.sinistres.views.widgets.damage_widgets import PhotoViewerDialog
        dialog = PhotoViewerDialog(self._photos, current_index=index, parent=self)
        dialog.exec()
    
    # ============================================================
    # VALIDATION ET ENREGISTREMENT
    # ============================================================
    
    def accept(self):
        try:
            # --- Validation ---
            type_dommage = self.input_type.currentText()
            if not type_dommage:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un type")
                return
            
            # --- Copie physique des photos ---
            from addons.sinistres.services.file_service import get_file_service
            file_service = get_file_service()
            
            photos_copiees = []
            erreurs = []
            
            for local_path in self._photos:
                rel_path = file_service.save_dommage_photo(
                    sinistre_id=self.sinistre_id,
                    source_path=local_path,
                    compress=True
                )
                if rel_path:
                    photos_copiees.append(rel_path)
                else:
                    erreurs.append(Path(local_path).name)
            
            # Si des photos ont échoué, prévenir l'utilisateur
            if erreurs and not photos_copiees:
                QMessageBox.warning(
                    self, "Attention",
                    f"Aucune photo n'a pu être copiée :\n" + "\n".join(erreurs)
                )
                return
            
            if erreurs:
                reply = QMessageBox.question(
                    self, "Avertissement",
                    f"{len(erreurs)} photo(s) n'ont pas pu être copiées :\n"
                    + "\n".join(erreurs) +
                    "\n\nContinuer quand même ?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            # --- Construction des données ---
            data = {
                'type_dommage': type_dommage,
                'code_dommage': self.input_code.text().strip() or None,
                'description': self.input_description.toPlainText().strip() or None,
                'montant_estime': self.input_montant.value(),
                'photos': photos_copiees or None,   # ✅ Chemins relatifs
                'created_by': self.user.id if self.user else None,
            }
            
            # --- Envoi au contrôleur ---
            result = self.controller.ajouter_dommage(self.sinistre_id, data)
            
            if result:
                super().accept()
            else:
                # Échec BDD : nettoyer les photos copiées
                for rel in photos_copiees:
                    file_service.delete_dommage_photo(rel)
                QMessageBox.warning(self, "Erreur", "Impossible d'enregistrer le dommage")
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", str(e))


def AddTiersDialog(sinistre_id, controller, user, parent=None):
    """Wrapper de compatibilité — utilise le nouveau TiersDialog"""
    from addons.sinistres.views.dialogs_files.tiers_dialog import TiersDialog
    return TiersDialog(
        sinistre_id=sinistre_id,
        controller=controller,
        user=user,
        parent=parent
    )


# class AddExpertiseDialog(QDialog):
#     def __init__(self, sinistre_id, controller, user, parent=None):
#         super().__init__(parent)
#         self.sinistre_id = sinistre_id
#         self.controller = controller
#         self.user = user
        
#         self.setWindowTitle("Créer une mission d'expertise")
#         self.setModal(True)
#         self.setMinimumWidth(500)
#         self.setup_ui()
    
#     def setup_ui(self):
#         layout = QVBoxLayout(self)
        
#         form_group = QGroupBox("Mission d'expertise")
#         form_layout = QFormLayout(form_group)
        
#         self.input_type = QComboBox()
#         self.input_type.addItems(["auto_materiel", "auto_corporel", "batiment", "transport", "medical", "judiciaire"])
#         form_layout.addRow("Type:", self.input_type)
        
#         self.input_domaine = QLineEdit()
#         self.input_domaine.setPlaceholderText("Domaine spécifique (optionnel)")
#         form_layout.addRow("Domaine:", self.input_domaine)
        
#         self.input_echeance = QDateEdit()
#         self.input_echeance.setDate(QDate.currentDate().addDays(14))
#         self.input_echeance.setCalendarPopup(True)
#         form_layout.addRow("Échéance:", self.input_echeance)
        
#         self.input_observations = QTextEdit()
#         self.input_observations.setMaximumHeight(80)
#         self.input_observations.setPlaceholderText("Observations (optionnel)")
#         form_layout.addRow("Observations:", self.input_observations)
        
#         layout.addWidget(form_group)
        
#         btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
#         btn_box.accepted.connect(self.accept)
#         btn_box.rejected.connect(self.reject)
#         layout.addWidget(btn_box)
    
#     def accept(self):
#         try:
#             data = {
#                 'sinistre_id': self.sinistre_id,
#                 'type_expertise': self.input_type.currentText(),
#                 'domaine': self.input_domaine.text().strip() or None,
#                 'date_echeance': self.input_echeance.date().toPython(),
#                 'observations': self.input_observations.toPlainText().strip() or None,
#                 'created_by': self.user.id if self.user else None
#             }
            
#             result = self.controller.creer_mission(data)
#             if result:
#                 super().accept()
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", str(e))


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