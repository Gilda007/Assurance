"""
Dialogue de création de lot de paiement
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QMessageBox, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor
from typing import List, Dict

from datetime import datetime


class LotPaiementDialog(QDialog):
    """Dialogue de création de lot de paiement"""
    
    lot_created = Signal(dict)
    
    def __init__(self, reglement_controller, user, parent=None):
        super().__init__(parent)
        self.reglement_controller = reglement_controller
        self.user = user
        self.selected_reglements = []
        self.reglements_disponibles = []
        
        self.setWindowTitle("Créer un lot de paiement")
        self.setModal(True)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
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
        
        title = QLabel("📦 Création d'un lot de paiement")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        
        self.lbl_date = QLabel(f"Date: {datetime.now().strftime('%d/%m/%Y')}")
        info_layout.addWidget(self.lbl_date)
        
        info_layout.addStretch()
        
        self.lbl_total = QLabel("💰 Total: 0 FCFA")
        self.lbl_total.setStyleSheet("font-weight: bold; color: #1a73e8;")
        info_layout.addWidget(self.lbl_total)
        
        self.lbl_nb = QLabel("📊 Nombre: 0")
        self.lbl_nb.setStyleSheet("font-weight: bold; color: #64748b;")
        info_layout.addWidget(self.lbl_nb)
        
        header_layout.addLayout(info_layout)
        
        layout.addWidget(header_frame)
        
        # ============================================================
        # SECTION 1: INFORMATIONS DU LOT
        # ============================================================
        form_group = QGroupBox("Informations du lot")
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
        
        # Type de lot
        self.input_type = QComboBox()
        self.input_type.addItems(["STANDARD", "URGENT", "RECOURS"])
        self.input_type.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Type de lot:", self.input_type)
        
        # Banque
        self.input_banque = QComboBox()
        self.input_banque.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_banque.addItem("-- Sélectionner une banque --", None)
        # TODO: Charger les banques depuis la base
        self.input_banque.addItem("Banque Atlantique", 1)
        self.input_banque.addItem("Ecobank", 2)
        self.input_banque.addItem("BICEC", 3)
        form_layout.addRow("Banque *:", self.input_banque)
        
        # Compte bancaire
        self.input_compte = QComboBox()
        self.input_compte.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        self.input_compte.addItem("-- Sélectionner un compte --", None)
        # TODO: Charger les comptes depuis la base
        self.input_compte.addItem("Compte Principal - XAF", 1)
        self.input_compte.addItem("Compte Secondaire - XAF", 2)
        form_layout.addRow("Compte bancaire *:", self.input_compte)
        
        # Date de traitement souhaitée
        self.input_date_traitement = QDateEdit()
        self.input_date_traitement.setDate(QDate.currentDate().addDays(3))
        self.input_date_traitement.setCalendarPopup(True)
        self.input_date_traitement.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;")
        form_layout.addRow("Date traitement souhaitée:", self.input_date_traitement)
        
        # Observations
        self.input_observations = QTextEdit()
        self.input_observations.setPlaceholderText("Observations sur le lot...")
        self.input_observations.setMaximumHeight(60)
        self.input_observations.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px;")
        form_layout.addRow("Observations:", self.input_observations)
        
        layout.addWidget(form_group)
        
        # ============================================================
        # SECTION 2: RÈGLEMENTS DISPONIBLES
        # ============================================================
        reg_group = QGroupBox("Règlements disponibles")
        reg_group.setStyleSheet("""
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
        reg_layout = QVBoxLayout(reg_group)
        
        # Filtres
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        self.filter_sinistre = QLineEdit()
        self.filter_sinistre.setPlaceholderText("🔍 Filtrer par sinistre...")
        self.filter_sinistre.setStyleSheet("""
            QLineEdit {
                padding: 6px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border-color: #1a73e8;
            }
        """)
        self.filter_sinistre.textChanged.connect(self._filtrer_reglements)
        filter_layout.addWidget(self.filter_sinistre)
        
        self.btn_select_all = QPushButton("Tout sélectionner")
        self.btn_select_all.setStyleSheet("padding: 6px 15px; border-radius: 6px;")
        self.btn_select_all.clicked.connect(self._selectionner_tout)
        filter_layout.addWidget(self.btn_select_all)
        
        self.btn_deselect_all = QPushButton("Tout désélectionner")
        self.btn_deselect_all.setStyleSheet("padding: 6px 15px; border-radius: 6px;")
        self.btn_deselect_all.clicked.connect(self._deselectionner_tout)
        filter_layout.addWidget(self.btn_deselect_all)
        
        filter_layout.addStretch()
        reg_layout.addLayout(filter_layout)
        
        # Tableau des règlements
        self.table_reglements = QTableWidget()
        self.table_reglements.setColumnCount(6)
        self.table_reglements.setHorizontalHeaderLabels([
            "Sélection", "N° Règlement", "Sinistre", "Bénéficiaire", "Montant", "Statut"
        ])
        self.table_reglements.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_reglements.setAlternatingRowColors(True)
        self.table_reglements.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        self.table_reglements.setSortingEnabled(True)
        self.table_reglements.itemChanged.connect(self._on_selection_changed)
        reg_layout.addWidget(self.table_reglements)
        
        layout.addWidget(reg_group)
        
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
        
        self.btn_creer = QPushButton("✅ Créer le lot")
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
        self.btn_creer.clicked.connect(self.creer_lot)
        self.btn_creer.setEnabled(False)
        btn_layout.addWidget(self.btn_creer)
        
        layout.addLayout(btn_layout)
    
    def load_data(self):
        """Charge les règlements disponibles"""
        try:
            # Récupérer les règlements en attente
            reglements = self.reglement_controller.get_reglements_en_attente()
            self.reglements_disponibles = reglements
            self._afficher_reglements(reglements)
            
        except Exception as e:
            print(f"Erreur chargement règlements: {e}")
    
    def _afficher_reglements(self, reglements: List[dict]):
        """Affiche les règlements dans le tableau"""
        self.table_reglements.setRowCount(len(reglements))
        self.table_reglements.setSortingEnabled(False)
        
        for i, reg in enumerate(reglements):
            # Case à cocher
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, row=i: self._on_checkbox_changed(row, state))
            self.table_reglements.setCellWidget(i, 0, checkbox)
            
            # Numéro règlement
            self.table_reglements.setItem(i, 1, QTableWidgetItem(reg.get('numero_reglement', '')))
            
            # Sinistre
            self.table_reglements.setItem(i, 2, QTableWidgetItem(str(reg.get('sinistre_id', ''))))
            
            # Bénéficiaire
            self.table_reglements.setItem(i, 3, QTableWidgetItem(reg.get('beneficiaire_nom', '')))
            
            # Montant
            montant_item = QTableWidgetItem(f"{reg.get('montant', 0):,.0f}")
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_reglements.setItem(i, 4, montant_item)
            
            # Statut
            statut_item = QTableWidgetItem(reg.get('statut', ''))
            statut_colors = {
                'CREE': '#f59e0b',
                'VALIDE': '#3b82f6',
                'EN_ATTENTE': '#8b5cf6'
            }
            color = statut_colors.get(reg.get('statut', ''), '#64748b')
            statut_item.setBackground(QColor(color))
            statut_item.setForeground(QColor('white'))
            self.table_reglements.setItem(i, 5, statut_item)
        
        self.table_reglements.setSortingEnabled(True)
        self._update_total()
    
    def _on_checkbox_changed(self, row: int, state: int):
        """Gère le changement d'état d'une checkbox"""
        self._update_total()
    
    def _on_selection_changed(self, item):
        """Gère les changements dans la table"""
        self._update_total()
    
    def _selectionner_tout(self):
        """Sélectionne tous les règlements"""
        for i in range(self.table_reglements.rowCount()):
            checkbox = self.table_reglements.cellWidget(i, 0)
            if checkbox:
                checkbox.setChecked(True)
        self._update_total()
    
    def _deselectionner_tout(self):
        """Désélectionne tous les règlements"""
        for i in range(self.table_reglements.rowCount()):
            checkbox = self.table_reglements.cellWidget(i, 0)
            if checkbox:
                checkbox.setChecked(False)
        self._update_total()
    
    def _filtrer_reglements(self):
        """Filtre les règlements selon la recherche"""
        search_text = self.filter_sinistre.text().lower()
        
        for i in range(self.table_reglements.rowCount()):
            show = True
            if search_text:
                sinistre = self.table_reglements.item(i, 2).text().lower()
                beneficiaire = self.table_reglements.item(i, 3).text().lower()
                if search_text not in sinistre and search_text not in beneficiaire:
                    show = False
            self.table_reglements.setRowHidden(i, not show)
    
    def _update_total(self):
        """Met à jour le total et le nombre de règlements sélectionnés"""
        total = 0
        count = 0
        self.selected_reglements = []
        
        for i in range(self.table_reglements.rowCount()):
            checkbox = self.table_reglements.cellWidget(i, 0)
            if checkbox and checkbox.isChecked():
                montant_item = self.table_reglements.item(i, 4)
                if montant_item:
                    montant = float(montant_item.text().replace(',', ''))
                    total += montant
                    count += 1
                    
                    # Récupérer les données du règlement
                    reg_data = {
                        'numero_reglement': self.table_reglements.item(i, 1).text(),
                        'sinistre_id': self.table_reglements.item(i, 2).text(),
                        'beneficiaire_nom': self.table_reglements.item(i, 3).text(),
                        'montant': montant
                    }
                    self.selected_reglements.append(reg_data)
        
        self.lbl_total.setText(f"💰 Total: {total:,.0f} FCFA")
        self.lbl_nb.setText(f"📊 Nombre: {count}")
        
        # Activer/désactiver le bouton de création
        self.btn_creer.setEnabled(count > 0)
    
    def creer_lot(self):
        """Crée le lot de paiement"""
        try:
            # ============================================================
            # VALIDATION
            # ============================================================
            
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
            
            # ============================================================
            # CONSTRUCTION DES DONNÉES
            # ============================================================
            data = {
                'banque_id': banque_id,
                'compte_bancaire_id': compte_id,
                'type_lot': self.input_type.currentText(),
                'date_traitement': self.input_date_traitement.date().toPython(),
                'observations': self.input_observations.toPlainText().strip() or None,
                'reglements': self.selected_reglements,
                'created_by': self.user.id if self.user else None
            }
            
            # ============================================================
            # ENVOI
            # ============================================================
            print(f"📝 Création lot avec {len(self.selected_reglements)} règlement(s)")
            
            result = self.reglement_controller.creer_lot_paiement(data)
            
            if result:
                self.lot_created.emit({
                    'lot_id': result.get('id'),
                    'numero_lot': result.get('numero_lot'),
                    'nombre_paiements': len(self.selected_reglements),
                    'montant_total': sum(r.get('montant', 0) for r in self.selected_reglements)
                })
                
                QMessageBox.information(
                    self,
                    "Succès",
                    f"✅ Lot de paiement créé avec succès !\n\n"
                    f"📌 N° Lot: {result.get('numero_lot', 'N/A')}\n"
                    f"📊 Nombre de paiements: {len(self.selected_reglements)}\n"
                    f"💰 Montant total: {sum(r.get('montant', 0) for r in self.selected_reglements):,.0f} FCFA\n"
                    f"📌 Statut: OUVERT\n\n"
                    f"💡 Les règlements ont été ajoutés au lot."
                )
                self.accept()
            
        except Exception as e:
            print(f"❌ Erreur création lot: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")