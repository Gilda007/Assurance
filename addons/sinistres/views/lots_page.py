"""
Page de gestion des lots de paiement
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QComboBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from typing import List


class LotsPage(QWidget):
    """Page de gestion des lots de paiement"""
    
    def __init__(self, controller, user, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # En-tête
        header = QLabel("📦 Gestion des lots de paiement")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)
        
        # Filtres
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        filter_layout.addWidget(QLabel("Statut:"))
        self.filter_statut = QComboBox()
        self.filter_statut.addItem("Tous", "")
        self.filter_statut.addItem("Ouvert", "OUVERT")
        self.filter_statut.addItem("Validé", "VALIDE")
        self.filter_statut.addItem("Traité", "TRAITE")
        self.filter_statut.addItem("Comptabilisé", "COMPTABILISE")
        self.filter_statut.currentIndexChanged.connect(self.load_data)
        filter_layout.addWidget(self.filter_statut)
        
        filter_layout.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Rafraîchir")
        self.btn_refresh.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        self.btn_refresh.clicked.connect(self.load_data)
        filter_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(filter_layout)
        
        # Tableau des lots
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "N° Lot", "Date", "Nombre", "Montant", "Type", "Statut", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
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
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.on_row_double_clicked)
        layout.addWidget(self.table)
    
    def load_data(self):
        """Charge les lots"""
        try:
            statut = self.filter_statut.currentData()
            lots = self.controller.get_lots_by_statut(statut) if statut else self.controller.get_all_lots()
            self.update_table(lots)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement lots: {str(e)}")
    
    def update_table(self, lots: List[dict]):
        """Met à jour le tableau des lots"""
        self.table.setRowCount(len(lots))
        
        statut_colors = {
            'OUVERT': '#f59e0b',
            'VALIDE': '#3b82f6',
            'TRAITE': '#06b6d4',
            'COMPTABILISE': '#22c55e'
        }
        
        for i, lot in enumerate(lots):
            self.table.setItem(i, 0, QTableWidgetItem(lot.get('numero_lot', '')))
            self.table.setItem(i, 1, QTableWidgetItem(lot.get('date_creation', '')[:10] if lot.get('date_creation') else ''))
            self.table.setItem(i, 2, QTableWidgetItem(str(lot.get('nombre_paiements', 0))))
            self.table.setItem(i, 3, QTableWidgetItem(f"{lot.get('montant_total', 0):,.0f}"))
            self.table.setItem(i, 4, QTableWidgetItem(lot.get('type_lot', '')))
            
            statut = lot.get('statut', '')
            statut_item = QTableWidgetItem(statut)
            color = statut_colors.get(statut, '#64748b')
            statut_item.setBackground(QColor(color))
            statut_item.setForeground(QColor('white'))
            self.table.setItem(i, 5, statut_item)
            
            # Bouton d'action
            btn = QPushButton("👁️ Voir")
            btn.setStyleSheet("padding: 4px 10px; border-radius: 4px;")
            btn.clicked.connect(lambda checked, row=i: self.open_lot_detail(row))
            self.table.setCellWidget(i, 6, btn)
    
    def open_lot_detail(self, row: int):
        """Ouvre le détail d'un lot"""
        numero = self.table.item(row, 0).text()
        QMessageBox.information(self, "Détail", f"Détail du lot {numero}\n(Fonctionnalité à venir)")
    
    def on_row_double_clicked(self, index):
        """Ouvre le détail du lot sélectionné"""
        row = index.row()
        if row >= 0:
            self.open_lot_detail(row)