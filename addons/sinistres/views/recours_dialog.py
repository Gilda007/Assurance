"""
Dialogue de création de recours conforme au CDC Tome 6 §5
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QMessageBox, QFrame, QCheckBox, QRadioButton
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor


class RecoursDialog(QDialog):
    """Dialogue de création de recours (conforme CDC Tome 6)"""
    
    recours_created = Signal(dict)
    
    def __init__(self, sinistre_id, recours_controller, user, sinistre_info=None, parent=None):
        super().__init__(parent)
        self.sinistre_id = sinistre_id
        self.recours_controller = recours_controller
        self.user = user
        self.sinistre_info = sinistre_info or {}
        
        # ✅ Listes de débiteurs
        self.tiers_disponibles = []
        self.compagnies_disponibles = []
        
        self.setWindowTitle("Créer un recours")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setup_ui()
        self.charger_debiteurs()
        self.verifier_conditions()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ============================================================
        # EN-TÊTE
        # ============================================================
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 10px;
                padding: 14px;
                border: 1px solid #e2e8f0;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("⚖️ Création de recours")
        title.setStyleSheet("font-weight: bold; font-size: 15px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"Sinistre: {self.sinistre_info.get('numero_sinistre', 'N/A')}"))
        info_layout.addWidget(QLabel(f"Client: {self.sinistre_info.get('client_nom', 'N/A')}"))
        
        montant_regle = self.sinistre_info.get('montant_regle', 0)
        self.lbl_montant = QLabel(f"💰 Montant réglé: {montant_regle:,.0f} FCFA")
        self.lbl_montant.setStyleSheet("font-weight: bold; color: #1a73e8;")
        info_layout.addWidget(self.lbl_montant)
        info_layout.addStretch()
        
        header_layout.addLayout(info_layout)
        layout.addWidget(header_frame)
        
        # ============================================================
        # SECTION 1 : TYPE DE RECOURS (CDC §4)
        # ============================================================
        type_group = QGroupBox("1️⃣ Type de recours (CDC §4)")
        type_group.setStyleSheet(self._group_style())
        tg_layout = QVBoxLayout(type_group)
        tg_layout.setContentsMargins(16, 20, 16, 16)
        tg_layout.setSpacing(8)
        
        self.input_type = QComboBox()
        self.input_type.addItems([
            "-- Sélectionner un type --",
            "COMPAGNIE (assureur adverse, tiers payant)",
            "TIERS (conducteur, transporteur, particulier, entreprise)",
            "CONTRACTUEL (coassurance, réassurance, convention)",
            "JURIDIQUE (contentieux, décision judiciaire, arbitrage)",
        ])
        self.input_type.currentIndexChanged.connect(self._on_type_changed)
        self.input_type.setStyleSheet(self._input_style())
        tg_layout.addWidget(self.input_type)
        
        layout.addWidget(type_group)
        
        # ============================================================
        # SECTION 2 : DÉBITEUR (CDC §5.2)
        # ============================================================
        debiteur_group = QGroupBox("2️⃣ Débiteur (CDC §5.2)")
        debiteur_group.setStyleSheet(self._group_style())
        dg_layout = QVBoxLayout(debiteur_group)
        dg_layout.setContentsMargins(16, 20, 16, 16)
        dg_layout.setSpacing(10)
        
        # Choix du type de débiteur
        type_deb_layout = QHBoxLayout()
        type_deb_layout.addWidget(QLabel("Type de débiteur:"))
        
        self.radio_tiers = QRadioButton("Tiers (personne)")
        self.radio_compagnie = QRadioButton("Compagnie (assureur)")
        self.radio_tiers.setChecked(True)
        self.radio_tiers.toggled.connect(self._on_debiteur_type_changed)
        
        type_deb_layout.addWidget(self.radio_tiers)
        type_deb_layout.addWidget(self.radio_compagnie)
        type_deb_layout.addStretch()
        dg_layout.addLayout(type_deb_layout)
        
        # Combo tiers
        self.input_tiers = QComboBox()
        self.input_tiers.setStyleSheet(self._input_style())
        self.input_tiers.addItem("-- Sélectionner un tiers --", None)
        self.input_tiers.setVisible(True)
        dg_layout.addWidget(QLabel("Tiers responsable:"))
        dg_layout.addWidget(self.input_tiers)
        
        # Combo compagnie
        self.input_compagnie = QComboBox()
        self.input_compagnie.setStyleSheet(self._input_style())
        self.input_compagnie.addItem("-- Sélectionner une compagnie --", None)
        self.input_compagnie.setVisible(False)
        self.lbl_compagnie = QLabel("Compagnie adverse:")
        self.lbl_compagnie.setVisible(False)
        dg_layout.addWidget(self.lbl_compagnie)
        dg_layout.addWidget(self.input_compagnie)
        
        layout.addWidget(debiteur_group)
        
        # ============================================================
        # SECTION 3 : MONTANTS (CDC §5.2 / REC-003)
        # ============================================================
        montant_group = QGroupBox("3️⃣ Montants")
        montant_group.setStyleSheet(self._group_style())
        mg_layout = QFormLayout(montant_group)
        mg_layout.setContentsMargins(16, 20, 16, 16)
        mg_layout.setSpacing(12)
        
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999_999_999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        self.input_montant.setStyleSheet(self._input_style())
        self.input_montant.valueChanged.connect(self._update_summary)
        mg_layout.addRow("Montant réclamé *:", self.input_montant)
        
        # Avertissement REC-003
        self.lbl_warning_montant = QLabel("")
        self.lbl_warning_montant.setStyleSheet("color: #92400e; font-size: 11px;")
        self.lbl_warning_montant.setWordWrap(True)
        mg_layout.addRow("", self.lbl_warning_montant)
        
        layout.addWidget(montant_group)
        
        # ============================================================
        # SECTION 4 : RÉFÉRENCES (optionnel)
        # ============================================================
        ref_group = QGroupBox("4️⃣ Références (optionnel)")
        ref_group.setStyleSheet(self._group_style())
        rg_layout = QFormLayout(ref_group)
        rg_layout.setContentsMargins(16, 20, 16, 16)
        rg_layout.setSpacing(12)
        
        self.input_reference = QLineEdit()
        self.input_reference.setPlaceholderText("Référence interne, dossier, courrier...")
        self.input_reference.setStyleSheet(self._input_style())
        rg_layout.addRow("Référence accord:", self.input_reference)
        
        layout.addWidget(ref_group)
        
        # ============================================================
        # SECTION 5 : OBSERVATIONS
        # ============================================================
        self.input_observations = QTextEdit()
        self.input_observations.setPlaceholderText(
            "Circonstances du recours, pièces justificatives, contacts..."
        )
        self.input_observations.setMaximumHeight(80)
        self.input_observations.setStyleSheet(self._input_style())
        layout.addWidget(QLabel("Observations:"))
        layout.addWidget(self.input_observations)
        
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
        """)
        summary_layout = QVBoxLayout(self.summary_frame)
        
        summary_title = QLabel("📋 Récapitulatif")
        summary_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #0369a1;")
        summary_layout.addWidget(summary_title)
        
        self.summary_text = QLabel("Remplissez les champs pour voir le récapitulatif")
        self.summary_text.setStyleSheet("color: #0369a1; font-size: 12px;")
        self.summary_text.setWordWrap(True)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(self.summary_frame)
        
        # ============================================================
        # BOUTONS
        # ============================================================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_annuler = QPushButton("Annuler")
        btn_annuler.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                border-radius: 8px;
                font-weight: bold;
                background-color: #f1f5f9;
                color: #64748b;
                border: none;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        btn_annuler.clicked.connect(self.reject)
        btn_layout.addWidget(btn_annuler)
        
        self.btn_creer = QPushButton("✅ Créer le recours")
        self.btn_creer.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 10px 40px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #1557b0; }
            QPushButton:disabled {
                background-color: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self.btn_creer.clicked.connect(self.creer_recours)
        self.btn_creer.setEnabled(False)
        btn_layout.addWidget(self.btn_creer)
        
        layout.addLayout(btn_layout)
        
        # Connexions
        self.input_tiers.currentIndexChanged.connect(self._update_summary)
        self.input_compagnie.currentIndexChanged.connect(self._update_summary)
        self.input_observations.textChanged.connect(self._update_summary)
    
    # ============================================================
    # STYLES
    # ============================================================
    
    def _group_style(self):
        return """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 12px;
                background-color: white;
                color: #1e293b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #1a73e8;
                font-size: 12px;
            }
        """
    
    def _input_style(self):
        return """
            QComboBox, QLineEdit, QDateEdit, QTextEdit, QDoubleSpinBox {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                background-color: white;
            }
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus {
                border: 2px solid #1a73e8;
            }
        """
    
    # ============================================================
    # CHARGEMENT DES DÉBITEURS
    # ============================================================
    
    def charger_debiteurs(self):
        """Charge les tiers et les compagnies via le contrôleur"""
        # ============================================================
        # TIERS — via RecoursController (pas de TiersController)
        # ============================================================
        try:
            self.tiers_disponibles = self.recours_controller.get_all_tiers()
            
            self.input_tiers.clear()
            self.input_tiers.addItem("-- Sélectionner un tiers --", None)
            
            for t in self.tiers_disponibles:
                nom = (
                    t.get('nom_complet')
                    or f"{t.get('nom', '')} {t.get('prenom', '')}".strip()
                    or f"Tiers #{t.get('id')}"
                )
                self.input_tiers.addItem(nom, t.get('id'))
            
            print(f"✅ {len(self.tiers_disponibles)} tiers chargés")
        except Exception as e:
            print(f"⚠️ Erreur chargement tiers: {e}")
            import traceback
            traceback.print_exc()
        
        # ============================================================
        # COMPAGNIES — via RecoursController
        # ============================================================
        try:
            self.compagnies_disponibles = self.recours_controller.get_compagnies_disponibles()
            
            self.input_compagnie.clear()
            self.input_compagnie.addItem("-- Sélectionner une compagnie --", None)
            
            for c in self.compagnies_disponibles:
                libelle = c.get('libelle') or c.get('nom') or f"Compagnie #{c.get('id')}"
                self.input_compagnie.addItem(libelle, c.get('id'))
            
            print(f"✅ {len(self.compagnies_disponibles)} compagnies chargées")
        except Exception as e:
            print(f"⚠️ Erreur chargement compagnies: {e}")
    
    # ============================================================
    # VÉRIFICATIONS CDC
    # ============================================================
    
    def verifier_conditions(self):
        """Vérifie les conditions préalables (REC-001, REC-002, REC-003)"""
        conditions_ok = True
        messages = []
        
        # REC-001 : Le sinistre doit exister
        if not self.sinistre_id:
            messages.append("❌ REC-001 : Sinistre non défini")
            conditions_ok = False
        
        # REC-002 : Responsabilité adverse identifiée
        taux_resp = self.sinistre_info.get('taux_responsabilite', 1) or 1
        if taux_resp >= 1.0:  # 100% responsable
            messages.append(
                "❌ REC-002 : Aucune responsabilité adverse "
                f"(taux de responsabilité = {taux_resp*100:.0f}%)"
            )
            conditions_ok = False
        
        # REC-003 : Montant récupérable déterminé
        montant_regle = self.sinistre_info.get('montant_regle', 0)
        if montant_regle <= 0:
            messages.append(
                "❌ REC-003 : Aucun montant réglé sur ce sinistre "
                "(impossible de déterminer le montant récupérable)"
            )
            conditions_ok = False
        
        if not conditions_ok:
            self.btn_creer.setEnabled(False)
            # Afficher les messages dans un bandeau d'erreur
            warn = QFrame()
            warn.setStyleSheet("""
                QFrame {
                    background-color: #fee2e2;
                    border: 1px solid #fecaca;
                    border-radius: 8px;
                    padding: 10px;
                }
                QLabel { color: #991b1b; font-size: 11px; }
            """)
            warn_layout = QVBoxLayout(warn)
            warn_layout.setContentsMargins(10, 8, 10, 8)
            for m in messages:
                l = QLabel(m)
                l.setWordWrap(True)
                warn_layout.addWidget(l)
            self.layout().insertWidget(0, warn)
    
    # ============================================================
    # ÉVÉNEMENTS
    # ============================================================
    
    def _on_type_changed(self):
        """Met à jour selon le type de recours sélectionné"""
        type_idx = self.input_type.currentIndex()
        
        # Auto-sélection du type de débiteur selon le type de recours
        if type_idx == 1:  # COMPAGNIE
            self.radio_compagnie.setChecked(True)
        elif type_idx == 2:  # TIERS
            self.radio_tiers.setChecked(True)
        # CONTRACTUEL (3) et JURIDIQUE (4) : laisser l'utilisateur choisir
        
        self._update_summary()
    
    def _on_debiteur_type_changed(self):
        """Change l'affichage du combo de débiteur"""
        is_tiers = self.radio_tiers.isChecked()
        
        self.input_tiers.setVisible(is_tiers)
        self.input_compagnie.setVisible(not is_tiers)
        self.lbl_compagnie.setVisible(not is_tiers)
        
        self._update_summary()
    
    def _update_summary(self):
        """Met à jour le récapitulatif"""
        lines = []
        all_ok = True
        
        # Type
        type_text = self.input_type.currentText()
        if type_text and not type_text.startswith("--"):
            lines.append(f"📌 Type: {type_text.split(' ')[0]}")
        else:
            lines.append("⚠️ Type de recours non sélectionné")
            all_ok = False
        
        # Débiteur
        if self.radio_tiers.isChecked():
            deb_id = self.input_tiers.currentData()
            if deb_id:
                deb_nom = self.input_tiers.currentText()
                lines.append(f"👤 Tiers: {deb_nom}")
            else:
                lines.append("⚠️ Tiers non sélectionné")
                all_ok = False
        else:
            deb_id = self.input_compagnie.currentData()
            if deb_id:
                deb_nom = self.input_compagnie.currentText()
                lines.append(f"🏢 Compagnie: {deb_nom}")
            else:
                lines.append("⚠️ Compagnie non sélectionnée")
                all_ok = False
        
        # Montant
        montant = self.input_montant.value()
        if montant > 0:
            lines.append(f"💰 Montant réclamé: {montant:,.0f} FCFA")
            
            # REC-003 : vérifier cohérence
            montant_regle = self.sinistre_info.get('montant_regle', 0)
            if montant > montant_regle:
                self.lbl_warning_montant.setText(
                    f"⚠️ REC-003 : Le montant réclamé ({montant:,.0f}) dépasse "
                    f"le montant réglé ({montant_regle:,.0f} FCFA)"
                )
            else:
                self.lbl_warning_montant.setText("")
        else:
            lines.append("⚠️ Montant non défini")
            all_ok = False
        
        self.summary_text.setText("\n".join(lines))
        
        # Activer le bouton si tout est OK
        self.btn_creer.setEnabled(all_ok)
    
    # ============================================================
    # CRÉATION
    # ============================================================
    
    def creer_recours(self):
        """Crée le recours (conforme CDC)"""
        try:
            # ============================================================
            # VALIDATION
            # ============================================================
            
            # Type
            type_idx = self.input_type.currentIndex()
            if type_idx <= 0:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un type de recours")
                return
            
            type_mapping = {
                1: "COMPAGNIE",
                2: "TIERS",
                3: "CONTRACTUEL",
                4: "JURIDIQUE",
            }
            type_recours = type_mapping[type_idx]
            
            # Débiteur
            debiteur_type = "TIERS" if self.radio_tiers.isChecked() else "COMPAGNIE"
            
            if debiteur_type == "TIERS":
                debiteur_id = self.input_tiers.currentData()
                debiteur_nom = self.input_tiers.currentText()
                debiteur_tiers_id = debiteur_id
                debiteur_compagnie_id = None
            else:
                debiteur_id = self.input_compagnie.currentData()
                debiteur_nom = self.input_compagnie.currentText()
                debiteur_tiers_id = None
                debiteur_compagnie_id = debiteur_id
            
            if not debiteur_id:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un débiteur")
                return
            
            # Montant
            montant = self.input_montant.value()
            if montant <= 0:
                QMessageBox.warning(self, "Validation", "Le montant doit être positif")
                return
            
            # REC-003 : Vérifier cohérence avec le montant réglé
            montant_regle = self.sinistre_info.get('montant_regle', 0)
            if montant > montant_regle:
                reply = QMessageBox.question(
                    self, "Confirmation REC-003",
                    f"Le montant réclamé ({montant:,.0f} FCFA) dépasse le montant "
                    f"réglé ({montant_regle:,.0f} FCFA).\n\n"
                    f"Voulez-vous continuer malgré tout ?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            # ============================================================
            # CONSTRUCTION DES DONNÉES
            # ============================================================
            data = {
                'sinistre_id': self.sinistre_id,
                'type_recours': type_recours,
                'debiteur_type': debiteur_type,
                'debiteur_tiers_id': debiteur_tiers_id,
                'debiteur_compagnie_id': debiteur_compagnie_id,
                'debiteur_nom': debiteur_nom,
                'montant_reclame': montant,
                'reference_accord': self.input_reference.text().strip() or None,
                'observations': self.input_observations.toPlainText().strip() or None,
                # ✅ Gestionnaire / responsable (obligatoire CDC)
                'responsable_id': self.user.id if self.user else None,
                'created_by': self.user.id if self.user else None,
            }
            
            # ============================================================
            # ENVOI
            # ============================================================
            print(f"📝 Création recours conforme CDC : {data}")
            
            result = self.recours_controller.creer_recours(data)
            
            if result:
                self.recours_created.emit(result)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"✅ Recours créé avec succès !\n\n"
                    f"📌 N° Recours: {result.get('numero_recours', 'N/A')}\n"
                    f"📌 Type: {type_recours}\n"
                    f"👤 Débiteur: {debiteur_nom}\n"
                    f"💰 Montant réclamé: {montant:,.0f} FCFA\n"
                    f"📌 Statut: OUVERT"
                )
                self.accept()
        
        except Exception as e:
            print(f"❌ Erreur création recours: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")