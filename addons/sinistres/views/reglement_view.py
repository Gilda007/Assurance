"""
Vue Règlements - Gestion des paiements et lots
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QComboBox, QLineEdit, QDateEdit,
    QFormLayout, QGroupBox, QDialog, QDialogButtonBox, QMessageBox,
    QTextEdit, QDoubleSpinBox, QFrame, QTabWidget
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor

from datetime import datetime
from typing import Optional, List, Dict, Any


class ReglementsView(QWidget):
    """Vue de gestion des règlements"""
    
    def __init__(self, controller, user=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.current_sinistre_id = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title = QLabel("💳 Gestion des Règlements")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        header_layout.addWidget(QLabel("Sinistre:"))
        self.sinistre_combo = QComboBox()
        self.sinistre_combo.setMinimumWidth(250)
        self.sinistre_combo.currentIndexChanged.connect(self.on_sinistre_changed)
        header_layout.addWidget(self.sinistre_combo)
        
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedSize(35, 35)
        self.btn_refresh.setStyleSheet("border-radius: 17px;")
        self.btn_refresh.clicked.connect(self.load_data)
        header_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(header_layout)
        
        # Onglets
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 0 0 8px 8px;
            }
            QTabBar::tab {
                padding: 8px 15px;
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #1a73e8;
            }
        """)
        
        # Onglet Règlements
        self.reg_tab = QWidget()
        reg_layout = QVBoxLayout(self.reg_tab)
        
        self.table_reglements = QTableWidget()
        self.table_reglements.setColumnCount(8)
        self.table_reglements.setHorizontalHeaderLabels([
            "N°", "Bénéficiaire", "Montant", "Type", "Date", "Statut", "Lot", "Actions"
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
        reg_layout.addWidget(self.table_reglements)
        
        # Boutons règlements
        reg_btn_layout = QHBoxLayout()
        
        self.btn_creer_reg = QPushButton("➕ Nouveau règlement")
        self.btn_creer_reg.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_creer_reg.clicked.connect(self.creer_reglement)
        reg_btn_layout.addWidget(self.btn_creer_reg)
        
        self.btn_valider_reg = QPushButton("✅ Valider")
        self.btn_valider_reg.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        self.btn_valider_reg.clicked.connect(self.valider_reglement)
        reg_btn_layout.addWidget(self.btn_valider_reg)
        
        self.btn_payer = QPushButton("💳 Payer")
        self.btn_payer.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        self.btn_payer.clicked.connect(self.payer_reglement)
        reg_btn_layout.addWidget(self.btn_payer)
        
        reg_btn_layout.addStretch()
        reg_layout.addLayout(reg_btn_layout)
        
        self.sub_tabs.addTab(self.reg_tab, "💳 Règlements")
        
        # Onglet Lots
        self.lot_tab = QWidget()
        lot_layout = QVBoxLayout(self.lot_tab)
        
        self.table_lots = QTableWidget()
        self.table_lots.setColumnCount(6)
        self.table_lots.setHorizontalHeaderLabels([
            "N° Lot", "Date", "Nb paiements", "Montant total", "Statut", "Actions"
        ])
        self.table_lots.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_lots.setAlternatingRowColors(True)
        self.table_lots.setStyleSheet("""
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
        lot_layout.addWidget(self.table_lots)
        
        lot_btn_layout = QHBoxLayout()
        
        self.btn_creer_lot = QPushButton("➕ Créer un lot")
        self.btn_creer_lot.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_creer_lot.clicked.connect(self.creer_lot)
        lot_btn_layout.addWidget(self.btn_creer_lot)
        
        self.btn_valider_lot = QPushButton("✅ Valider lot")
        self.btn_valider_lot.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        self.btn_valider_lot.clicked.connect(self.valider_lot)
        lot_btn_layout.addWidget(self.btn_valider_lot)
        
        lot_btn_layout.addStretch()
        lot_layout.addLayout(lot_btn_layout)
        
        self.sub_tabs.addTab(self.lot_tab, "📦 Lots")
        
        layout.addWidget(self.sub_tabs)
    
    def load_data(self):
        """Charge les sinistres"""
        try:
            sinistres = []  # self.controller.get_sinistres_recent()
            self.sinistre_combo.clear()
            self.sinistre_combo.addItem("-- Sélectionner un sinistre --", None)
            for s in sinistres:
                self.sinistre_combo.addItem(
                    f"{s.get('numero_sinistre', '')} - {s.get('branche', '')}",
                    s.get('id')
                )
        except Exception as e:
            print(f"Erreur chargement sinistres: {e}")
    
    def on_sinistre_changed(self, index):
        """Charge les données du sinistre sélectionné"""
        if index > 0:
            sinistre_id = self.sinistre_combo.currentData()
            if sinistre_id:
                self.current_sinistre_id = sinistre_id
                self.load_reglements(sinistre_id)
                self.load_lots(sinistre_id)
        else:
            self.table_reglements.setRowCount(0)
            self.table_lots.setRowCount(0)
    
    def load_reglements(self, sinistre_id: int):
        """Charge les règlements d'un sinistre"""
        try:
            reglements = self.controller.get_reglements_by_sinistre(sinistre_id)
            self.update_reg_table(reglements)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement règlements: {str(e)}")
    
    def update_reg_table(self, reglements: List[dict]):
        """Met à jour le tableau des règlements"""
        self.table_reglements.setRowCount(len(reglements))
        
        statut_colors = {
            'CREE': '#f59e0b',
            'VALIDE': '#3b82f6',
            'EN_ATTENTE': '#8b5cf6',
            'TRAITE': '#06b6d4',
            'PAYE': '#22c55e',
            'ANNULE': '#ef4444',
            'REJETE': '#ef4444'
        }
        
        for i, reg in enumerate(reglements):
            self.table_reglements.setItem(i, 0, QTableWidgetItem(reg.get('numero_reglement', '')))
            self.table_reglements.setItem(i, 1, QTableWidgetItem(reg.get('beneficiaire_nom', '')))
            self.table_reglements.setItem(i, 2, QTableWidgetItem(f"{reg.get('montant', 0):,.0f}"))
            self.table_reglements.setItem(i, 3, QTableWidgetItem(reg.get('type_paiement', '')))
            self.table_reglements.setItem(i, 4, QTableWidgetItem(reg.get('date_demande', '')[:10] if reg.get('date_demande') else ''))
            
            statut = reg.get('statut', '')
            statut_item = QTableWidgetItem(statut)
            color = statut_colors.get(statut, '#64748b')
            statut_item.setBackground(QColor(color))
            statut_item.setForeground(QColor('white'))
            self.table_reglements.setItem(i, 5, statut_item)
            
            self.table_reglements.setItem(i, 6, QTableWidgetItem(reg.get('lot_paiement_id', '-') or '-'))
    
    def load_lots(self, sinistre_id: int):
        """Charge les lots de paiement"""
        try:
            lots = []  # self.controller.get_lots_by_sinistre(sinistre_id)
            self.update_lot_table(lots)
        except Exception as e:
            print(f"Erreur chargement lots: {e}")
    
    def update_lot_table(self, lots: List[dict]):
        """Met à jour le tableau des lots"""
        self.table_lots.setRowCount(len(lots))
        
        for i, lot in enumerate(lots):
            self.table_lots.setItem(i, 0, QTableWidgetItem(lot.get('numero_lot', '')))
            self.table_lots.setItem(i, 1, QTableWidgetItem(lot.get('date_creation', '')[:10] if lot.get('date_creation') else ''))
            self.table_lots.setItem(i, 2, QTableWidgetItem(str(lot.get('nombre_paiements', 0))))
            self.table_lots.setItem(i, 3, QTableWidgetItem(f"{lot.get('montant_total', 0):,.0f}"))
            self.table_lots.setItem(i, 4, QTableWidgetItem(lot.get('statut', '')))
    
    def creer_reglement(self):
        """Crée un nouveau règlement"""
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        dialog = ReglementDialog(self.controller, self.current_sinistre_id, self.user)
        if dialog.exec():
            self.load_reglements(self.current_sinistre_id)
    
    def valider_reglement(self):
        """Valide le règlement sélectionné"""
        row = self.table_reglements.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un règlement")
            return
        
        reply = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous valider ce règlement ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                QMessageBox.information(self, "Succès", "Règlement validé")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def payer_reglement(self):
        """Paye le règlement sélectionné"""
        row = self.table_reglements.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un règlement")
            return
        
        dialog = PaiementDialog(self.controller, self.user)
        if dialog.exec():
            self.load_reglements(self.current_sinistre_id)
    
    def creer_lot(self):
        """Crée un lot de paiement"""
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        QMessageBox.information(self, "Création", "Dialogue de création de lot (à implémenter)")
    
    def valider_lot(self):
        """Valide le lot sélectionné"""
        QMessageBox.information(self, "Validation", "Validation de lot (à implémenter)")


class ReglementDialog(QDialog):
    """Dialogue de création de règlement"""
    
    def __init__(self, controller, sinistre_id, user, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.sinistre_id = sinistre_id
        self.user = user
        self.setWindowTitle("Créer un règlement")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Règlement")
        form_layout = QFormLayout(form_group)
        
        self.input_beneficiaire = QComboBox()
        self.input_beneficiaire.setEditable(True)
        self.input_beneficiaire.addItems(["-- Sélectionner un bénéficiaire --"])
        # TODO: Charger les bénéficiaires
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
        """Valide la création"""
        try:
            data = {
                'sinistre_id': self.sinistre_id,
                'beneficiaire_id': 1,  # TODO: Récupérer l'ID sélectionné
                'montant': self.input_montant.value(),
                'type_paiement': self.input_type.currentText(),
                'observations': self.input_observations.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            result = self.controller.creer_reglement(data)
            if result:
                QMessageBox.information(self, "Succès", "Règlement créé avec succès")
                super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


class PaiementDialog(QDialog):
    """Dialogue de paiement"""
    
    def __init__(self, controller, user, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.setWindowTitle("Effectuer le paiement")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Paiement")
        form_layout = QFormLayout(form_group)
        
        self.input_reference = QLineEdit()
        self.input_reference.setPlaceholderText("Référence du paiement")
        form_layout.addRow("Référence:", self.input_reference)
        
        self.input_date = QDateEdit()
        self.input_date.setDate(QDate.currentDate())
        self.input_date.setCalendarPopup(True)
        form_layout.addRow("Date paiement:", self.input_date)
        
        layout.addWidget(form_group)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def accept(self):
        # TODO: Envoyer les données au contrôleur
        super().accept()