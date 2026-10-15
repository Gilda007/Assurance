"""
Dialog de détail d'un lot de paiement
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from typing import Dict, Any


class LotDetailDialog(QDialog):
    """Dialog de détail d'un lot de paiement"""
    
    # Signal émis après une action (valider, traiter, comptabiliser)
    lot_updated = Signal(dict)
    
    def __init__(self, lot: dict, reglement_controller, user, parent=None):
        super().__init__(parent)
        self.lot = lot
        self.reglement_controller = reglement_controller
        self.user = user
        
        self.setWindowTitle(f"Détail du lot {lot.get('numero_lot', 'N/A')}")
        self.setModal(True)
        self.setMinimumSize(900, 600)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # ============================================================
        # EN-TÊTE : N° lot + Statut + Montant
        # ============================================================
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 14, 16, 14)
        header_layout.setSpacing(14)
        
        # Icône
        icon = QLabel("📦")
        icon.setFixedSize(52, 52)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("""
            background-color: #e8f0fe;
            border-radius: 10px;
            font-size: 26px;
        """)
        header_layout.addWidget(icon)
        
        # Infos principales
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        numero = QLabel(self.lot.get('numero_lot', 'N/A'))
        numero.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        info_layout.addWidget(numero)
        
        date_creation = self.lot.get('date_creation', '')[:16] if self.lot.get('date_creation') else '—'
        date_lbl = QLabel(f"📅 Créé le {date_creation}")
        date_lbl.setStyleSheet("font-size: 11px; color: #64748b;")
        info_layout.addWidget(date_lbl)
        
        header_layout.addLayout(info_layout, 1)
        
        # Montant
        montant_layout = QVBoxLayout()
        montant_layout.setSpacing(4)
        
        montant_lbl = QLabel("Montant total")
        montant_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        montant_layout.addWidget(montant_lbl)
        
        montant_val = QLabel(f"{self.lot.get('montant_total', 0):,.0f} FCFA")
        montant_val.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a73e8;")
        montant_layout.addWidget(montant_val)
        
        header_layout.addLayout(montant_layout)
        
        # Statut badge
        statut = self.lot.get('statut', 'OUVERT')
        statut_colors = {
            'OUVERT': ('#fef3c7', '#92400e'),
            'VALIDE': ('#dbeafe', '#1e40af'),
            'TRAITE': ('#cffafe', '#155e75'),
            'COMPTABILISE': ('#dcfce7', '#166534'),
            'ANNULE': ('#fee2e2', '#991b1b'),
        }
        bg, fg = statut_colors.get(statut, ('#f1f5f9', '#64748b'))
        
        statut_lbl = QLabel(statut)
        statut_lbl.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            padding: 6px 14px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        """)
        statut_lbl.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(statut_lbl)
        
        layout.addWidget(header)
        
        # ============================================================
        # INFORMATIONS DU LOT
        # ============================================================
        infos_group = QGroupBox("Informations du lot")
        infos_group.setStyleSheet("""
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
                left: 10px;
                padding: 0 10px;
            }
        """)
        infos_layout = QHBoxLayout(infos_group)
        infos_layout.setContentsMargins(16, 14, 16, 14)
        infos_layout.setSpacing(20)
        
        # Colonne 1
        col1 = QVBoxLayout()
        col1.setSpacing(8)
        
        self._add_info_row(col1, "Type de lot", self.lot.get('type_lot', '—'))
        self._add_info_row(col1, "Nombre de paiements", str(self.lot.get('nombre_paiements', 0)))
        
        infos_layout.addLayout(col1, 1)
        
        # Colonne 2
        col2 = QVBoxLayout()
        col2.setSpacing(8)
        
        self._add_info_row(col2, "Date de traitement",
                           self.lot.get('date_traitement', '')[:16] if self.lot.get('date_traitement') else '—')
        self._add_info_row(col2, "Date de comptabilisation",
                           self.lot.get('date_comptabilisation', '')[:16] if self.lot.get('date_comptabilisation') else '—')
        
        infos_layout.addLayout(col2, 1)
        
        layout.addWidget(infos_group)
        
        # ============================================================
        # RÈGLEMENTS DU LOT
        # ============================================================
        regs_group = QGroupBox(f"Règlements inclus ({self.lot.get('nombre_paiements', 0)})")
        regs_group.setStyleSheet("""
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
                left: 10px;
                padding: 0 10px;
            }
        """)
        regs_layout = QVBoxLayout(regs_group)
        regs_layout.setContentsMargins(0, 14, 0, 0)
        
        self.table_regs = QTableWidget()
        self.table_regs.setColumnCount(5)
        self.table_regs.setHorizontalHeaderLabels([
            "N° Règlement", "Bénéficiaire", "Montant", "Type paiement", "Statut"
        ])
        header = self.table_regs.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.table_regs.setAlternatingRowColors(True)
        self.table_regs.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_regs.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_regs.verticalHeader().setVisible(False)
        self.table_regs.verticalHeader().setDefaultSectionSize(44)
        self.table_regs.setShowGrid(False)
        self.table_regs.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px 12px;
                font-size: 12px;
                border-bottom: 1px solid #f1f5f9;
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
        
        # Remplir le tableau
        reglements = self.lot.get('reglements', [])
        self.table_regs.setRowCount(len(reglements))
        
        action_colors = {
            'CREE': ('#fef3c7', '#92400e'),
            'VALIDE': ('#dbeafe', '#1e40af'),
            'EN_ATTENTE': ('#ede9fe', '#5b21b6'),
            'TRAITE': ('#cffafe', '#155e75'),
            'PAYE': ('#dcfce7', '#166534'),
            'ANNULE': ('#fee2e2', '#991b1b'),
        }
        
        for i, reg in enumerate(reglements):
            self.table_regs.setItem(i, 0, QTableWidgetItem(reg.get('numero_reglement', '')))
            self.table_regs.setItem(i, 1, QTableWidgetItem(reg.get('beneficiaire_nom', '')))
            
            montant = reg.get('montant', 0)
            montant_item = QTableWidgetItem(f"{montant:,.0f} FCFA")
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_regs.setItem(i, 2, montant_item)
            
            self.table_regs.setItem(i, 3, QTableWidgetItem(reg.get('type_paiement', '')))
            
            statut = reg.get('statut', '')
            statut_item = QTableWidgetItem(statut)
            bg, fg = action_colors.get(statut, ('#f1f5f9', '#64748b'))
            statut_item.setBackground(QColor(bg))
            statut_item.setForeground(QColor(fg))
            statut_item.setTextAlignment(Qt.AlignCenter)
            self.table_regs.setItem(i, 4, statut_item)
        
        regs_layout.addWidget(self.table_regs)
        layout.addWidget(regs_group, 1)
        
        # ============================================================
        # BOUTONS D'ACTION
        # ============================================================
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # Bouton Fermer
        self.btn_close = QPushButton("✖ Fermer")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #64748b;
                padding: 10px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        self.btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_close)
        
        btn_layout.addStretch()
        
        # Boutons d'action selon statut
        statut = self.lot.get('statut', '')
        
        if statut == "OUVERT":
            self.btn_valider = QPushButton("✅ Valider le lot")
            self.btn_valider.setStyleSheet(self._action_btn_style("#1a73e8", "#1557b0"))
            self.btn_valider.clicked.connect(self._on_valider)
            btn_layout.addWidget(self.btn_valider)
        
        elif statut == "VALIDE":
            self.btn_traiter = QPushButton("▶️ Traiter le lot")
            self.btn_traiter.setStyleSheet(self._action_btn_style("#8b5cf6", "#7c3aed"))
            self.btn_traiter.clicked.connect(self._on_traiter)
            btn_layout.addWidget(self.btn_traiter)
        
        elif statut == "TRAITE":
            self.btn_comptabiliser = QPushButton("📊 Comptabiliser le lot")
            self.btn_comptabiliser.setStyleSheet(self._action_btn_style("#22c55e", "#16a34a"))
            self.btn_comptabiliser.clicked.connect(self._on_comptabiliser)
            btn_layout.addWidget(self.btn_comptabiliser)
        
        # Bouton Imprimer (toujours visible)
        self.btn_imprimer = QPushButton("🖨️ Imprimer")
        self.btn_imprimer.setStyleSheet(self._action_btn_style("#64748b", "#475569"))
        self.btn_imprimer.clicked.connect(self._on_imprimer)
        btn_layout.addWidget(self.btn_imprimer)
        
        layout.addLayout(btn_layout)
    
    def _add_info_row(self, parent_layout, label: str, value: str):
        """Ajoute une ligne info (label + valeur)"""
        row = QHBoxLayout()
        row.setSpacing(8)
        
        lbl = QLabel(f"{label}:")
        lbl.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 600; min-width: 130px;")
        row.addWidget(lbl)
        
        val = QLabel(str(value))
        val.setStyleSheet("font-size: 12px; color: #1e293b;")
        row.addWidget(val, 1)
        
        parent_layout.addLayout(row)
    
    def _action_btn_style(self, bg: str, hover: str) -> str:
        return f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                padding: 10px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
                border: none;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
        """
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def _on_valider(self):
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous valider le lot {self.lot.get('numero_lot')} ?\n\n"
            f"📊 {self.lot.get('nombre_paiements', 0)} règlements\n"
            f"💰 {self.lot.get('montant_total', 0):,.0f} FCFA",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        try:
            lot_id = self.lot.get('id')
            success = self.reglement_controller.valider_lot_paiement(lot_id)
            
            if success:
                QMessageBox.information(self, "Succès", "✅ Lot validé avec succès")
                self.lot_updated.emit(self.lot)
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _on_traiter(self):
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous traiter le lot {self.lot.get('numero_lot')} ?\n\n"
            f"Cette action enverra le lot à la banque.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        try:
            # TODO: méthode à ajouter dans le contrôleur
            QMessageBox.information(self, "Info", "Traitement à implémenter (Phase 2)")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _on_comptabiliser(self):
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous comptabiliser le lot {self.lot.get('numero_lot')} ?\n\n"
            f"Cette action marquera tous les règlements comme comptabilisés.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        try:
            # TODO: méthode à ajouter dans le contrôleur
            QMessageBox.information(self, "Info", "Comptabilisation à implémenter (Phase 2)")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _on_imprimer(self):
        QMessageBox.information(self, "Impression", "Génération PDF à implémenter (Phase 4)")