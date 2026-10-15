"""
Dialogue d'affichage des écritures comptables d'un recours
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class ComptabiliteRecoursDialog(QDialog):
    """Dialogue d'affichage des écritures comptables"""
    
    def __init__(self, recours_id, recours_info, comptabilite_controller, user, parent=None):
        super().__init__(parent)
        self.recours_id = recours_id
        self.recours_info = recours_info or {}
        self.comptabilite_controller = comptabilite_controller
        self.user = user
        
        self.setWindowTitle(f"Écritures comptables - {self.recours_info.get('numero_recours', 'N/A')}")
        self.setModal(True)
        self.setMinimumSize(1000, 600)
        
        self.setup_ui()
        self.charger_ecritures()
    
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
                border-radius: 10px;
                padding: 14px;
                border: 1px solid #e2e8f0;
            }
        """)
        header_layout = QVBoxLayout(header)
        
        title = QLabel("📒 Écritures comptables du recours")
        title.setStyleSheet("font-weight: bold; font-size: 15px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info = QHBoxLayout()
        info.addWidget(QLabel(f"Recours: {self.recours_info.get('numero_recours', 'N/A')}"))
        info.addWidget(QLabel(f"Débiteur: {self.recours_info.get('debiteur_nom', 'N/A')}"))
        info.addStretch()
        header_layout.addLayout(info)
        
        layout.addWidget(header)
        
        # ============================================================
        # TABLEAU
        # ============================================================
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "N° Écriture", "Date", "Journal", "Libellé",
            "Débit", "Crédit", "Montant"
        ])
        header_t = self.table.horizontalHeader()
        header_t.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_t.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_t.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_t.setSectionResizeMode(3, QHeaderView.Stretch)
        header_t.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_t.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header_t.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        
        layout.addWidget(self.table, 1)
        
        # ============================================================
        # PIED
        # ============================================================
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        footer_layout = QHBoxLayout(footer)
        
        self.lbl_total = QLabel("Total : 0 écriture(s)")
        self.lbl_total.setStyleSheet("font-size: 13px; font-weight: bold; color: #0369a1;")
        footer_layout.addWidget(self.lbl_total)
        
        footer_layout.addStretch()
        
        self.lbl_montant_total = QLabel("Montant total : 0 FCFA")
        self.lbl_montant_total.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #1a73e8;"
        )
        footer_layout.addWidget(self.lbl_montant_total)
        
        layout.addWidget(footer)
        
        # ============================================================
        # BOUTONS
        # ============================================================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_close = QPushButton("Fermer")
        self.btn_close.setStyleSheet("""
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
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
    
    def charger_ecritures(self):
        """Charge et affiche les écritures comptables"""
        try:
            ecritures = self.comptabilite_controller.get_ecritures_by_recours(self.recours_id)
            
            self.table.setRowCount(len(ecritures))
            
            journal_colors = {
                'BANQUE': '#3b82f6',
                'SINISTRES': '#8b5cf6',
                'RECOURS': '#22c55e',
                'REGULARISATIONS': '#f59e0b',
            }
            
            total_montant = 0
            
            for i, e in enumerate(ecritures):
                # N° écriture
                self.table.setItem(i, 0, QTableWidgetItem(e.get('numero_ecriture', '')))
                
                # Date
                date_str = e.get('date_ecriture', '')
                if date_str:
                    date_str = date_str[:16].replace('T', ' ')
                self.table.setItem(i, 1, QTableWidgetItem(date_str))
                
                # Journal (avec badge)
                journal = e.get('journal', '')
                journal_item = QTableWidgetItem(journal)
                color = journal_colors.get(journal, '#64748b')
                journal_item.setBackground(QColor(color))
                journal_item.setForeground(QColor('white'))
                journal_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 2, journal_item)
                
                # Libellé
                self.table.setItem(i, 3, QTableWidgetItem(e.get('libelle', '')))
                
                # Débit
                self.table.setItem(i, 4, QTableWidgetItem(e.get('compte_debit', '')))
                
                # Crédit
                self.table.setItem(i, 5, QTableWidgetItem(e.get('compte_credit', '')))
                
                # Montant
                montant = float(e.get('montant', 0))
                total_montant += montant
                montant_item = QTableWidgetItem(f"{montant:,.0f} FCFA")
                montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                montant_item.setForeground(QColor('#1a73e8'))
                self.table.setItem(i, 6, montant_item)
            
            self.lbl_total.setText(f"Total : {len(ecritures)} écriture(s)")
            self.lbl_montant_total.setText(f"Montant total : {total_montant:,.0f} FCFA")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement écritures : {str(e)}")