"""
Dialogue de création de lot de paiement - Version 2
Avec sélection de sinistre et affichage des détails
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QMessageBox, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QCheckBox, QSplitter,
    QScrollArea, QGridLayout, QWidget
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor

from datetime import datetime
from typing import List, Dict, Optional


class LotPaiementDialog(QDialog):
    """Dialogue de création de lot de paiement - V2"""
    
    lot_created = Signal(dict)
    
    def __init__(self, reglement_controller, user, parent=None):
        super().__init__(parent)
        self.reglement_controller = reglement_controller
        self.user = user
        
        self.selected_reglements = []
        self.reglements_disponibles = []
        self.reglements_filtres = []
        self.comptes_bancaires = []
        self.sinistres = []
        self.sinistre_selectionne = None
        
        self.setWindowTitle("Créer un lot de paiement")
        self.setModal(True)
        self.setMinimumSize(1100, 750)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ============================================================
        # EN-TÊTE
        # ============================================================
        header = self._make_header()
        layout.addWidget(header)
        
        # ============================================================
        # SPLITTER : GAUCHE (sélection) / DROITE (infos lot)
        # ============================================================
        splitter = QSplitter(Qt.Horizontal)
        
        # --- PARTIE GAUCHE : Sinistre + Règlements ---
        left_panel = self._make_left_panel()
        splitter.addWidget(left_panel)
        
        # --- PARTIE DROITE : Infos du lot + Sélection ---
        right_panel = self._make_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([700, 400])
        
        layout.addWidget(splitter, 1)
        
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
                border: none;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        self.btn_creer = QPushButton("✅ Créer le lot")
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
        self.btn_creer.clicked.connect(self.creer_lot)
        self.btn_creer.setEnabled(False)
        btn_layout.addWidget(self.btn_creer)
        
        layout.addLayout(btn_layout)
    
    # ============================================================
    # CONSTRUCTION DES PANNEAUX
    # ============================================================
    
    def _make_header(self) -> QFrame:
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        
        icon = QLabel("📦")
        icon.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon)
        
        title = QLabel("Création d'un lot de paiement")
        title.setStyleSheet("font-weight: bold; font-size: 15px; color: #1e293b;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Compteurs
        self.lbl_total = QLabel("💰 Total: 0 FCFA")
        self.lbl_total.setStyleSheet("font-weight: bold; color: #1a73e8; font-size: 13px;")
        header_layout.addWidget(self.lbl_total)
        
        header_layout.addSpacing(20)
        
        self.lbl_nb = QLabel("📊 Sélectionnés: 0")
        self.lbl_nb.setStyleSheet("font-weight: bold; color: #64748b; font-size: 13px;")
        header_layout.addWidget(self.lbl_nb)
        
        return header
    
    def _make_left_panel(self) -> QWidget:
        """Panneau gauche : sélection sinistre + règlements"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # ============================================================
        # SECTION 1 : Sélection du sinistre
        # ============================================================
        sinistre_group = QGroupBox("1️⃣ Sélection du sinistre")
        sinistre_group.setStyleSheet(self._group_style())
        sg_layout = QVBoxLayout(sinistre_group)
        sg_layout.setContentsMargins(16, 20, 16, 16)
        sg_layout.setSpacing(10)
        
        # Ligne de sélection
        select_row = QHBoxLayout()
        select_row.setSpacing(10)
        
        select_row.addWidget(QLabel("Sinistre:"))
        
        self.combo_sinistre = QComboBox()
        self.combo_sinistre.setMinimumWidth(400)
        self.combo_sinistre.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QComboBox:focus { border: 2px solid #1a73e8; }
            QComboBox::drop-down { border: none; width: 24px; }
        """)
        self.combo_sinistre.currentIndexChanged.connect(self._on_sinistre_changed)
        select_row.addWidget(self.combo_sinistre, 1)
        
        select_row.addStretch()
        sg_layout.addLayout(select_row)
        
        # Détails du sinistre (cachés au départ)
        self.sinistre_details = QFrame()
        self.sinistre_details.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        self.sinistre_details.setVisible(False)
        
        sd_layout = QGridLayout(self.sinistre_details)
        sd_layout.setContentsMargins(14, 12, 14, 12)
        sd_layout.setSpacing(10)
        
        # On va créer les labels une seule fois
        self._sd_labels = {}
        fields = [
            ("numero", "📄 N° Sinistre"),
            ("client", "👤 Client"),
            ("branche", "🏢 Branche"),
            ("date_survenance", "📅 Date survenance"),
            ("statut", "📌 Statut"),
            ("montant_evalue", "💰 Montant évalué"),
            ("nb_evaluations", "📊 Évaluations"),
            ("nb_reglements", "💳 Règlements en attente"),
        ]
        
        for i, (key, label) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 600;")
            sd_layout.addWidget(lbl, row, col)
            
            val = QLabel("—")
            val.setStyleSheet("font-size: 12px; color: #1e293b; font-weight: 500;")
            sd_layout.addWidget(val, row, col + 1)
            
            self._sd_labels[key] = val
        
        sg_layout.addWidget(self.sinistre_details)
        
        layout.addWidget(sinistre_group)
        
        # ============================================================
        # SECTION 2 : Règlements du sinistre
        # ============================================================
        regs_group = QGroupBox("2️⃣ Règlements du sinistre sélectionné")
        regs_group.setStyleSheet(self._group_style())
        rg_layout = QVBoxLayout(regs_group)
        rg_layout.setContentsMargins(16, 20, 16, 16)
        rg_layout.setSpacing(10)
        
        # Barre d'actions
        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)
        
        self.btn_select_all = QPushButton("☑️ Tout sélectionner")
        self.btn_select_all.setStyleSheet(self._small_btn_style())
        self.btn_select_all.clicked.connect(self._selectionner_tout)
        actions_row.addWidget(self.btn_select_all)
        
        self.btn_deselect_all = QPushButton("☐ Tout désélectionner")
        self.btn_deselect_all.setStyleSheet(self._small_btn_style())
        self.btn_deselect_all.clicked.connect(self._deselectionner_tout)
        actions_row.addWidget(self.btn_deselect_all)
        
        actions_row.addStretch()
        
        self.lbl_regs_count = QLabel("0 règlement(s)")
        self.lbl_regs_count.setStyleSheet("color: #64748b; font-size: 11px;")
        actions_row.addWidget(self.lbl_regs_count)
        
        rg_layout.addLayout(actions_row)
        
        # Tableau des règlements
        self.table_reglements = QTableWidget()
        self.table_reglements.setColumnCount(6)
        self.table_reglements.setHorizontalHeaderLabels([
            "☐", "N° Règlement", "Bénéficiaire", "Montant", "Type", "Statut"
        ])
        header = self.table_reglements.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table_reglements.setColumnWidth(0, 40)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.table_reglements.setAlternatingRowColors(True)
        self.table_reglements.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_reglements.setSelectionMode(QTableWidget.SingleSelection)
        self.table_reglements.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_reglements.verticalHeader().setDefaultSectionSize(48)
        self.table_reglements.verticalHeader().setVisible(False)
        self.table_reglements.setShowGrid(False)
        self.table_reglements.itemSelectionChanged.connect(self._on_reglement_selected)
        self.table_reglements.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px 12px;
                font-size: 12px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background-color: #e8f0fe;
                color: #1e293b;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px;
                font-weight: 600;
                font-size: 11px;
                color: #64748b;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        rg_layout.addWidget(self.table_reglements, 1)
        
        layout.addWidget(regs_group, 1)
        
        return panel
    
    def _make_right_panel(self) -> QWidget:
        """Panneau droit : infos du lot + détails du règlement sélectionné"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # ============================================================
        # SECTION 1 : Informations du lot
        # ============================================================
        lot_group = QGroupBox("Informations du lot")
        lot_group.setStyleSheet(self._group_style())
        lg_layout = QFormLayout(lot_group)
        lg_layout.setContentsMargins(16, 20, 16, 16)
        lg_layout.setSpacing(10)
        
        # Type de lot
        self.input_type = QComboBox()
        self.input_type.addItems(["STANDARD", "URGENT", "RECOURS"])
        self.input_type.setStyleSheet(self._input_style())
        lg_layout.addRow("Type de lot:", self.input_type)
        
        # Banque
        self.input_banque = QComboBox()
        self.input_banque.setStyleSheet(self._input_style())
        self.input_banque.addItem("-- Sélectionner --", None)
        self.input_banque.currentIndexChanged.connect(self._charger_comptes_pour_banque)
        lg_layout.addRow("Banque *:", self.input_banque)
        
        # Compte bancaire
        self.input_compte = QComboBox()
        self.input_compte.setStyleSheet(self._input_style())
        self.input_compte.addItem("-- Sélectionner --", None)
        lg_layout.addRow("Compte *:", self.input_compte)
        
        # Date de traitement
        self.input_date_traitement = QDateEdit()
        self.input_date_traitement.setDate(QDate.currentDate().addDays(3))
        self.input_date_traitement.setCalendarPopup(True)
        self.input_date_traitement.setStyleSheet(self._input_style())
        lg_layout.addRow("Date traitement:", self.input_date_traitement)
        
        # Observations
        self.input_observations = QTextEdit()
        self.input_observations.setPlaceholderText("Observations...")
        self.input_observations.setMaximumHeight(60)
        self.input_observations.setStyleSheet(self._input_style())
        lg_layout.addRow("Observations:", self.input_observations)
        
        layout.addWidget(lot_group)
        
        # ============================================================
        # SECTION 2 : Détails du règlement sélectionné
        # ============================================================
        self.detail_group = QGroupBox("Détails du règlement")
        self.detail_group.setStyleSheet(self._group_style())
        dg_layout = QVBoxLayout(self.detail_group)
        dg_layout.setContentsMargins(16, 20, 16, 16)
        dg_layout.setSpacing(8)
        
        self.detail_content = QLabel("Sélectionnez un règlement pour voir ses détails")
        self.detail_content.setStyleSheet("""
            color: #94a3b8;
            font-size: 11px;
            font-style: italic;
            padding: 20px;
        """)
        self.detail_content.setWordWrap(True)
        self.detail_content.setAlignment(Qt.AlignTop)
        dg_layout.addWidget(self.detail_content)
        
        layout.addWidget(self.detail_group)
        
        # ============================================================
        # SECTION 3 : Résumé du lot
        # ============================================================
        resume_group = QGroupBox("Résumé")
        resume_group.setStyleSheet(self._group_style())
        rg_layout = QVBoxLayout(resume_group)
        rg_layout.setContentsMargins(16, 20, 16, 16)
        rg_layout.setSpacing(6)
        
        self.lbl_resume_nb = QLabel("📊 Règlements: 0")
        self.lbl_resume_nb.setStyleSheet("font-size: 12px; color: #1e293b; font-weight: 600;")
        rg_layout.addWidget(self.lbl_resume_nb)
        
        self.lbl_resume_total = QLabel("💰 Total: 0 FCFA")
        self.lbl_resume_total.setStyleSheet("font-size: 14px; color: #1a73e8; font-weight: bold;")
        rg_layout.addWidget(self.lbl_resume_total)
        
        layout.addWidget(resume_group)
        layout.addStretch()
        
        return panel
    
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
            QComboBox, QDateEdit, QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                background-color: white;
            }
            QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border: 2px solid #1a73e8;
            }
        """
    
    def _small_btn_style(self):
        return """
            QPushButton {
                background-color: #f1f5f9;
                color: #64748b;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 11px;
                border: none;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """
    
    # ============================================================
    # CHARGEMENT DES DONNÉES
    # ============================================================
    
    def load_data(self):
        """Charge les sinistres, banques et comptes"""
        try:
            # 1. Banques
            banques = self.reglement_controller.get_banques()
            self.input_banque.blockSignals(True)
            self.input_banque.clear()
            self.input_banque.addItem("-- Sélectionner --", None)
            for b in banques:
                self.input_banque.addItem(
                    f"{b.get('code_banque', '')} - {b.get('libelle', '')}",
                    b.get('id')
                )
            self.input_banque.blockSignals(False)
            
            # 2. Comptes bancaires
            self.comptes_bancaires = self.reglement_controller.get_comptes_bancaires()
            
            # 3. Sinistres ayant des règlements en attente
            self._load_sinistres_avec_reglements()
            
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_sinistres_avec_reglements(self):
        """Charge la liste des sinistres qui ont des règlements en attente"""
        try:
            # Récupérer TOUS les règlements en attente
            all_reglements = self.reglement_controller.get_reglements_en_attente()
            self.reglements_disponibles = all_reglements
            
            # Regrouper par sinistre_id
            sinistres_ids = set()
            for r in all_reglements:
                sid = r.get('sinistre_id')
                if sid:
                    sinistres_ids.add(sid)
            
            # Charger les infos des sinistres
            self.sinistres = []
            for sid in sorted(sinistres_ids):
                # Récupérer les infos du sinistre
                sinistre_info = self._get_sinistre_info(sid)
                if sinistre_info:
                    # Compter les règlements en attente pour ce sinistre
                    nb_regs = sum(1 for r in all_reglements if r.get('sinistre_id') == sid)
                    sinistre_info['_nb_reglements'] = nb_regs
                    self.sinistres.append(sinistre_info)
            
            # Remplir le combo
            self.combo_sinistre.blockSignals(True)
            self.combo_sinistre.clear()
            self.combo_sinistre.addItem("-- Sélectionner un sinistre --", None)
            
            for s in self.sinistres:
                label = (
                    f"{s.get('numero_sinistre', 'N/A')} • "
                    f"{s.get('client_nom', 'Client inconnu')} • "
                    f"{s.get('branche', 'N/A')} • "
                    f"({s.get('_nb_reglements', 0)} règlement(s))"
                )
                self.combo_sinistre.addItem(label, s.get('id'))
            
            self.combo_sinistre.blockSignals(False)
            
        except Exception as e:
            print(f"❌ Erreur chargement sinistres: {e}")
    
    def _get_sinistre_info(self, sinistre_id: int) -> Optional[dict]:
        """Récupère les infos d'un sinistre"""
        try:
            # Essayer via le contrôleur sinistre
            from addons.sinistres.controllers.sinistre_controller import SinistreController
            sc = SinistreController()
            sc.set_current_user(self.user)
            info = sc.get_sinistre(sinistre_id)
            if info:
                return info
        except Exception:
            pass
        
        # Fallback : reconstruire depuis les règlements
        for r in self.reglements_disponibles:
            if r.get('sinistre_id') == sinistre_id:
                return {
                    'id': sinistre_id,
                    'numero_sinistre': r.get('sinistre_numero', f'SIN-{sinistre_id}'),
                    'client_nom': r.get('beneficiaire_nom', 'N/A'),
                    'branche': 'N/A',
                }
        return None
    
    # ============================================================
    # CHARGEMENT DES COMPTES POUR BANQUE
    # ============================================================
    
    def _charger_comptes_pour_banque(self):
        """Charge les comptes de la banque sélectionnée (appel direct au contrôleur)"""
        banque_id = self.input_banque.currentData()
        
        # Réinitialiser
        self.input_compte.clear()
        self.input_compte.addItem("-- Sélectionner --", None)
        
        if banque_id is None:
            self.input_compte.setEnabled(False)
            return
        
        try:
            # ✅ Appel DIRECT au contrôleur (filtre côté base)
            comptes = self.reglement_controller.get_comptes_bancaires_by_banque(banque_id)
            
            if not comptes:
                self.input_compte.addItem("⚠️ Aucun compte pour cette banque", None)
                self.input_compte.setEnabled(False)
                return
            
            self.input_compte.setEnabled(True)
            
            for compte in comptes:
                libelle = compte.get('libelle', 'N/A')
                devise = compte.get('devise', '')
                iban = compte.get('iban', '')
                iban_court = f"...{iban[-4:]}" if iban and len(iban) > 4 else iban
                label = f"{libelle} • {devise} • {iban_court}"
                self.input_compte.addItem(label, compte.get('id'))
            
            print(f"✅ {len(comptes)} compte(s) chargé(s) pour banque_id={banque_id}")
        
        except Exception as e:
            print(f"❌ Erreur chargement comptes: {e}")
            import traceback
            traceback.print_exc()
            self.input_compte.addItem("⚠️ Erreur de chargement", None)
            self.input_compte.setEnabled(False)

    # ============================================================
    # SÉLECTION DU SINISTRE
    # ============================================================
    
    def _on_sinistre_changed(self):
        """Appelé quand on change de sinistre"""
        sinistre_id = self.combo_sinistre.currentData()
        self.sinistre_selectionne = None
        
        if not sinistre_id:
            self.sinistre_details.setVisible(False)
            self.table_reglements.setRowCount(0)
            self.lbl_regs_count.setText("0 règlement(s)")
            self._update_total()
            return
        
        # Trouver le sinistre
        sinistre = next((s for s in self.sinistres if s.get('id') == sinistre_id), None)
        if not sinistre:
            return
        
        self.sinistre_selectionne = sinistre
        self._afficher_sinistre_details(sinistre)
        self._charger_reglements_sinistre(sinistre_id)
    
    def _afficher_sinistre_details(self, sinistre: dict):
        """Affiche les détails du sinistre sélectionné"""
        self.sinistre_details.setVisible(True)
        
        # Formater les valeurs
        date_surv = sinistre.get('date_survenance', '')
        if date_surv and len(str(date_surv)) >= 10:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(str(date_surv).replace('Z', ''))
                date_surv = dt.strftime('%d/%m/%Y')
            except Exception:
                date_surv = str(date_surv)[:10]
        
        montant = sinistre.get('montant_evalue', 0) or sinistre.get('montant_total_evalue', 0) or 0
        
        # Calculer les évaluations et règlements
        nb_evals = sinistre.get('_nb_evaluations', 0)
        nb_regs = sinistre.get('_nb_reglements', 0)
        
        # Mettre à jour les labels
        self._sd_labels['numero'].setText(sinistre.get('numero_sinistre', '—'))
        self._sd_labels['client'].setText(sinistre.get('client_nom', '—'))
        self._sd_labels['branche'].setText(sinistre.get('branche', '—'))
        self._sd_labels['date_survenance'].setText(date_surv or '—')
        self._sd_labels['statut'].setText(sinistre.get('statut', '—'))
        self._sd_labels['montant_evalue'].setText(f"{montant:,.0f} FCFA" if montant else '—')
        self._sd_labels['nb_evaluations'].setText(str(nb_evals))
        self._sd_labels['nb_reglements'].setText(str(nb_regs))
    
    def _charger_reglements_sinistre(self, sinistre_id: int):
        """Charge les règlements du sinistre sélectionné"""
        # Filtrer les règlements par sinistre
        self.reglements_filtres = [
            r for r in self.reglements_disponibles
            if r.get('sinistre_id') == sinistre_id
        ]
        
        # Réinitialiser la sélection
        self.selected_reglements = []
        
        self._afficher_reglements()
    
    # ============================================================
    # AFFICHAGE DES RÈGLEMENTS
    # ============================================================
    
    def _afficher_reglements(self):
        """Affiche les règlements filtrés dans le tableau"""
        reglements = self.reglements_filtres
        self.table_reglements.setRowCount(len(reglements))
        self.table_reglements.blockSignals(True)
        
        for i, reg in enumerate(reglements):
            # Checkbox
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk.setCheckState(Qt.Unchecked)
            chk.setData(Qt.UserRole, reg)
            self.table_reglements.setItem(i, 0, chk)
            
            # N° Règlement
            self.table_reglements.setItem(i, 1, QTableWidgetItem(reg.get('numero_reglement', '')))
            
            # Bénéficiaire
            self.table_reglements.setItem(i, 2, QTableWidgetItem(reg.get('beneficiaire_nom', '')))
            
            # Montant
            montant = reg.get('montant', 0)
            montant_item = QTableWidgetItem(f"{montant:,.0f} FCFA")
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_reglements.setItem(i, 3, montant_item)
            
            # Type
            self.table_reglements.setItem(i, 4, QTableWidgetItem(reg.get('type_paiement', '')))
            
            # Statut
            statut = reg.get('statut', '')
            statut_colors = {
                'CREE': ('#fef3c7', '#92400e'),
                'VALIDE': ('#dbeafe', '#1e40af'),
                'EN_ATTENTE': ('#ede9fe', '#5b21b6'),
            }
            bg, fg = statut_colors.get(statut, ('#f1f5f9', '#64748b'))
            statut_item = QTableWidgetItem(statut)
            statut_item.setBackground(QColor(bg))
            statut_item.setForeground(QColor(fg))
            statut_item.setTextAlignment(Qt.AlignCenter)
            self.table_reglements.setItem(i, 5, statut_item)
        
        self.table_reglements.blockSignals(False)
        
        # Connecter les checkboxes
        self.table_reglements.itemChanged.connect(self._on_checkbox_changed)
        
        self.lbl_regs_count.setText(f"{len(reglements)} règlement(s)")
        self._update_total()
    
    def _on_checkbox_changed(self, item):
        """Gère le changement d'état d'une checkbox"""
        if item.column() != 0:
            return
        self._update_total()
    
    # ============================================================
    # SÉLECTION DES RÈGLEMENTS
    # ============================================================
    
    def _on_reglement_selected(self):
        """Affiche les détails du règlement sélectionné"""
        row = self.table_reglements.currentRow()
        if row < 0:
            return
        
        chk = self.table_reglements.item(row, 0)
        if not chk:
            return
        
        reg = chk.data(Qt.UserRole)
        if not reg:
            return
        
        self._afficher_reglement_details(reg)
    
    def _afficher_reglement_details(self, reg: dict):
        """Affiche les détails d'un règlement dans le panneau droit"""
        montant = reg.get('montant', 0)
        statut = reg.get('statut', '—')
        
        html = f"""
        <div style="font-family: Arial; font-size: 11px; line-height: 1.6;">
            <p style="margin: 4px 0;"><b>📄 N° Règlement:</b> {reg.get('numero_reglement', '—')}</p>
            <p style="margin: 4px 0;"><b>👤 Bénéficiaire:</b> {reg.get('beneficiaire_nom', '—')}</p>
            <p style="margin: 4px 0;"><b>💰 Montant:</b> 
                <span style="color: #1a73e8; font-weight: bold;">{montant:,.0f} FCFA</span>
            </p>
            <p style="margin: 4px 0;"><b>💳 Type paiement:</b> {reg.get('type_paiement', '—')}</p>
            <p style="margin: 4px 0;"><b>📌 Statut:</b> {statut}</p>
            <p style="margin: 4px 0;"><b>🆔 Évaluation liée:</b> {reg.get('evaluation_id', '—')}</p>
            <p style="margin: 4px 0;"><b>📅 Date demande:</b> 
                {reg.get('date_demande', '')[:16] if reg.get('date_demande') else '—'}
            </p>
        </div>
        """
        
        self.detail_content.setText(html)
        self.detail_content.setStyleSheet("""
            color: #1e293b;
            font-size: 11px;
            padding: 10px;
        """)
    
    # ============================================================
    # SÉLECTION TOUT / RIEN
    # ============================================================
    
    def _selectionner_tout(self):
        """Sélectionne tous les règlements"""
        self.table_reglements.blockSignals(True)
        for i in range(self.table_reglements.rowCount()):
            item = self.table_reglements.item(i, 0)
            if item:
                item.setCheckState(Qt.Checked)
        self.table_reglements.blockSignals(False)
        self._update_total()
    
    def _deselectionner_tout(self):
        """Désélectionne tous les règlements"""
        self.table_reglements.blockSignals(True)
        for i in range(self.table_reglements.rowCount()):
            item = self.table_reglements.item(i, 0)
            if item:
                item.setCheckState(Qt.Unchecked)
        self.table_reglements.blockSignals(False)
        self._update_total()
    
    # ============================================================
    # MISE À JOUR DU TOTAL
    # ============================================================
    
    def _update_total(self):
        """Met à jour le total et la liste des règlements sélectionnés"""
        total = 0
        count = 0
        self.selected_reglements = []
        
        for i in range(self.table_reglements.rowCount()):
            chk = self.table_reglements.item(i, 0)
            if not chk or chk.checkState() != Qt.Checked:
                continue
            
            reg = chk.data(Qt.UserRole)
            if not reg:
                continue
            
            montant = reg.get('montant', 0) or 0
            total += montant
            count += 1
            
            self.selected_reglements.append({
                'id': reg.get('id'),
                'numero_reglement': reg.get('numero_reglement'),
                'sinistre_id': reg.get('sinistre_id'),
                'beneficiaire_nom': reg.get('beneficiaire_nom'),
                'montant': montant,
            })
        
        self.lbl_total.setText(f"💰 Total: {total:,.0f} FCFA")
        self.lbl_nb.setText(f"📊 Sélectionnés: {count}")
        self.lbl_resume_nb.setText(f"📊 Règlements: {count}")
        self.lbl_resume_total.setText(f"💰 Total: {total:,.0f} FCFA")
        
        self.btn_creer.setEnabled(count > 0)
    
    # ============================================================
    # CRÉATION DU LOT
    # ============================================================
    
    def creer_lot(self):
        """Crée le lot de paiement"""
        try:
            # Validation
            if not self.sinistre_selectionne:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un sinistre")
                return
            
            if not self.selected_reglements:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner au moins un règlement")
                return
            
            banque_id = self.input_banque.currentData()
            if not banque_id:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner une banque")
                return
            
            compte_id = self.input_compte.currentData()
            if not compte_id:
                QMessageBox.warning(self, "Validation", "Veuillez sélectionner un compte bancaire")
                return
            
            reglement_ids = [r['id'] for r in self.selected_reglements if r.get('id')]
            if len(reglement_ids) != len(self.selected_reglements):
                QMessageBox.warning(self, "Erreur", "Certains règlements n'ont pas d'ID valide")
                return
            
            data = {
                'banque_id': banque_id,
                'compte_bancaire_id': compte_id,
                'type_lot': self.input_type.currentText(),
                'date_traitement': self.input_date_traitement.date().toPython(),
                'observations': self.input_observations.toPlainText().strip() or None,
                'reglement_ids': reglement_ids,
                'created_by': self.user.id if self.user else None,
            }
            
            print(f"📝 Création lot avec {len(reglement_ids)} règlement(s)")
            result = self.reglement_controller.creer_lot_paiement(data)
            
            if result:
                self.lot_created.emit({
                    'lot_id': result.get('id'),
                    'numero_lot': result.get('numero_lot'),
                    'nombre_paiements': len(reglement_ids),
                    'montant_total': sum(r.get('montant', 0) for r in self.selected_reglements),
                })
                
                QMessageBox.information(
                    self, "Succès",
                    f"✅ Lot créé avec succès !\n\n"
                    f"📌 N° Lot: {result.get('numero_lot', 'N/A')}\n"
                    f"📊 {len(reglement_ids)} règlements\n"
                    f"💰 {sum(r.get('montant', 0) for r in self.selected_reglements):,.0f} FCFA"
                )
                self.accept()
        
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", str(e))