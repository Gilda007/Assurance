

"""
Vue principale du module LOMETA Sinistres
Interface utilisateur complète pour la gestion des sinistres
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QListWidgetItem, QStackedWidget,
    QListWidget, QFrame, QMessageBox, QDialog, QGraphicsDropShadowEffect,
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QTabWidget, QSplitter, QScrollArea,
    QProgressBar, QToolBar, QMenu, QCheckBox, QRadioButton
)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QDate
from PySide6.QtGui import QColor, QIcon, QFont

from datetime import datetime, timedelta
from typing import Optional

# ============================================================
# PAGE 6: RÈGLEMENTS
# ============================================================

class ReglementsPage(QWidget):
    """Page de gestion des règlements"""
    
    def __init__(self, controller, user):
        super().__init__()
        self.controller = controller
        self.user = user
        self.current_sinistre_id = None
        self.selected_reglement_id = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        
        title = QLabel("💳 Gestion des Règlements")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        header_layout.addWidget(QLabel("Sinistre:"))
        self.sinistre_combo = QComboBox()
        self.sinistre_combo.setMinimumWidth(200)
        self.sinistre_combo.currentIndexChanged.connect(self.on_sinistre_changed)
        header_layout.addWidget(self.sinistre_combo)
        
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedSize(35, 35)
        self.btn_refresh.setStyleSheet("border-radius: 17px;")
        self.btn_refresh.clicked.connect(self.load_data)
        header_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(header_layout)
        
        self.table_reglements = QTableWidget()
        self.table_reglements.setColumnCount(7)
        self.table_reglements.setHorizontalHeaderLabels([
            "N°", "Bénéficiaire", "Montant", "Type", "Date", "Statut", "Lot"
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
        layout.addWidget(self.table_reglements)
        
        btn_layout = QHBoxLayout()
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
        btn_layout.addWidget(self.btn_creer_reg)

        # ✅ AJOUTER LE BOUTON VALIDER
        self.btn_valider_reg = QPushButton("✅ Valider")
        self.btn_valider_reg.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        self.btn_valider_reg.clicked.connect(self.valider_reglement)
        btn_layout.addWidget(self.btn_valider_reg)

        # ✅ AJOUTER LE BOUTON PAYER
        self.btn_payer_reg = QPushButton("💳 Payer")
        self.btn_payer_reg.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        self.btn_payer_reg.clicked.connect(self.payer_reglement)
        btn_layout.addWidget(self.btn_payer_reg)

        # ✅ AJOUTER LE BOUTON CRÉER LOT
        self.btn_creer_lot = QPushButton("📦 Créer un lot")
        self.btn_creer_lot.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        self.btn_creer_lot.clicked.connect(self.creer_lot_paiement)
        btn_layout.addWidget(self.btn_creer_lot)

        # ✅ AJOUTER LE BOUTON VALIDER LOT
        self.btn_valider_lot = QPushButton("📦 Valider lot")
        self.btn_valider_lot.setStyleSheet("""
            QPushButton {
                background-color: #06b6d4;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0891b2;
            }
        """)
        self.btn_valider_lot.clicked.connect(self.valider_lot_paiement)
        btn_layout.addWidget(self.btn_valider_lot)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def load_data(self):
        """Charge les sinistres"""
        try:
            self.sinistre_combo.clear()
            sinistres = self.controller.get_sinistres_recents()
            for s in sinistres:
                self.sinistre_combo.addItem(
                    f"{s.get('numero_sinistre')} - {s.get('branche', '')}",
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
    
    def load_reglements(self, sinistre_id: int):
        """Charge les règlements d'un sinistre"""
        try:
            reglements = self.controller.get_reglements_by_sinistre(sinistre_id)
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
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement règlements: {str(e)}")
    
    def creer_reglement(self):
        """Crée un nouveau règlement"""
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        # Récupérer les informations du sinistre
        sinistre_info = {}
        try:
            from addons.sinistres.controllers.sinistre_controller import SinistreController
            sc = SinistreController()
            sc.set_current_user(self.user)
            sinistre_data = sc.get_sinistre(self.current_sinistre_id)
            if sinistre_data:
                sinistre_info = {
                    'numero_sinistre': sinistre_data.get('numero_sinistre', 'N/A'),
                    'client_nom': 'N/A',
                    'branche': sinistre_data.get('branche', 'N/A')
                }
        except:
            pass
        
        from addons.sinistres.views.reglement_dialog import ReglementDialog
        dialog = ReglementDialog(
            sinistre_id=self.current_sinistre_id,
            reglement_controller=self.controller,
            user=self.user,
            sinistre_info=sinistre_info,
            parent=self
        )
        
        dialog.reglement_created.connect(self._on_reglement_created)
        dialog.exec()

    def _on_reglement_created(self, data: dict):
        """Appelé après la création d'un règlement"""
        self.load_reglements(self.current_sinistre_id)
        QMessageBox.information(
            self,
            "Succès",
            f"✅ Règlement créé avec succès !"
        )

    def valider_reglement(self):
        """Valide le règlement sélectionné"""
        row = self.table_reglements.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un règlement")
            return
        
        reglement_numero = self.table_reglements.item(row, 0).text()
        statut = self.table_reglements.item(row, 5).text()
        
        if statut != "CREE":
            QMessageBox.warning(
                self,
                "Attention",
                f"Seul un règlement au statut 'CRÉÉ' peut être validé (statut: {statut})"
            )
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous valider le règlement {reglement_numero} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                reglement_data = self.controller.get_reglement_by_numero(reglement_numero)
                if not reglement_data:
                    QMessageBox.warning(self, "Erreur", "Règlement non trouvé")
                    return
                
                result = self.controller.valider_reglement(reglement_data.get('id'))
                if result:
                    QMessageBox.information(self, "Succès", "Règlement validé avec succès")
                    self.load_reglements(self.current_sinistre_id)
                    
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def payer_reglement(self):
        """Paye le règlement sélectionné"""
        row = self.table_reglements.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un règlement")
            return
        
        reglement_numero = self.table_reglements.item(row, 0).text()
        statut = self.table_reglements.item(row, 5).text()
        
        if statut != "VALIDE":
            QMessageBox.warning(
                self,
                "Attention",
                f"Seul un règlement au statut 'VALIDÉ' peut être payé (statut: {statut})"
            )
            return
        
        # Ouvrir le dialogue de paiement
        from addons.sinistres.views.paiement_dialog import PaiementDialog
        dialog = PaiementDialog(
            reglement_numero=reglement_numero,
            reglement_controller=self.controller,
            user=self.user,
            parent=self
        )
        
        dialog.paiement_effectue.connect(self._on_paiement_effectue)
        dialog.exec()

    def _on_paiement_effectue(self, data: dict):
        """Appelé après un paiement"""
        self.load_reglements(self.current_sinistre_id)
        QMessageBox.information(
            self,
            "Succès",
            f"✅ Paiement effectué avec succès !"
        )

    def creer_lot_paiement(self):
        """Crée un lot de paiement"""
        from addons.sinistres.views.lot_paiement_dialog import LotPaiementDialog
        dialog = LotPaiementDialog(
            reglement_controller=self.controller,
            user=self.user,
            parent=self
        )
        
        dialog.lot_created.connect(self._on_lot_created)
        dialog.exec()

    def _on_lot_created(self, data: dict):
        """Appelé après la création d'un lot"""
        QMessageBox.information(
            self,
            "Succès",
            f"✅ Lot {data.get('numero_lot')} créé avec succès !\n"
            f"📊 {data.get('nombre_paiements')} règlements inclus\n"
            f"💰 {data.get('montant_total', 0):,.0f} FCFA"
        )
        # Rafraîchir la liste des règlements
        if self.current_sinistre_id:
            self.load_reglements(self.current_sinistre_id)

    def valider_lot_paiement(self):
        """Valide un lot de paiement"""
        row = self.table_reglements.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un règlement dans le lot")
            return
        
        lot_id = self.table_reglements.item(row, 6).text()
        if lot_id == '-' or not lot_id:
            QMessageBox.warning(self, "Attention", "Ce règlement n'appartient à aucun lot")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous valider le lot {lot_id} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.valider_lot_paiement(int(lot_id))
                if result:
                    QMessageBox.information(self, "Succès", f"Lot {lot_id} validé avec succès")
                    if self.current_sinistre_id:
                        self.load_reglements(self.current_sinistre_id)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def get_lots_by_sinistre(self, sinistre_id: int):
        """Récupère les lots d'un sinistre"""
        try:
            return self.controller.get_lots_by_sinistre(sinistre_id)
        except Exception as e:
            print(f"Erreur chargement lots: {e}")
            return []

    def _on_reglement_cell_clicked(self, row: int, col: int):
        """Gère le clic sur une ligne de règlement"""
        reg_numero = self.table_reglements.item(row, 0).text()
        try:
            reg_data = self.controller.get_reglement_by_numero(reg_numero)
            if reg_data:
                self.selected_reglement_id = reg_data.get('id')
        except:
            pass
        self.table_reglements.selectRow(row)

    def get_selected_reglement_id(self) -> Optional[int]:
        """Retourne l'ID du règlement sélectionné"""
        row = self.table_reglements.currentRow()
        if row >= 0:
            reg_numero = self.table_reglements.item(row, 0).text()
            try:
                reg_data = self.controller.get_reglement_by_numero(reg_numero)
                if reg_data:
                    return reg_data.get('id')
            except:
                pass
        return None
