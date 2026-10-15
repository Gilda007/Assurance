"""
Vue Recours - Gestion des recours et encaissements
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


class RecoursView(QWidget):
    """Vue de gestion des recours"""
    
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
        
        title = QLabel("⚖️ Gestion des Recours")
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
        
        # Statistiques
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.lbl_total = QLabel("Total recours: 0")
        self.lbl_total.setStyleSheet("font-weight: bold; color: #1e293b;")
        stats_layout.addWidget(self.lbl_total)
        
        stats_layout.addStretch()
        
        self.lbl_aboutis = QLabel("✅ Aboutis: 0")
        self.lbl_aboutis.setStyleSheet("color: #22c55e;")
        stats_layout.addWidget(self.lbl_aboutis)
        
        self.lbl_encours = QLabel("🟡 En cours: 0")
        self.lbl_encours.setStyleSheet("color: #f59e0b;")
        stats_layout.addWidget(self.lbl_encours)
        
        self.lbl_taux_recup = QLabel("📊 Taux récupération: 0%")
        self.lbl_taux_recup.setStyleSheet("color: #3b82f6;")
        stats_layout.addWidget(self.lbl_taux_recup)
        
        layout.addWidget(stats_frame)
        
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
        
        # Onglet Recours
        self.rec_tab = QWidget()
        rec_layout = QVBoxLayout(self.rec_tab)
        
        self.table_recours = QTableWidget()
        self.table_recours.setColumnCount(8)
        self.table_recours.setHorizontalHeaderLabels([
            "N°", "Débiteur", "Réclamé", "Accepté", "Encaissé", "Solde", "Statut", "Actions"
        ])
        self.table_recours.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_recours.setAlternatingRowColors(True)
        self.table_recours.setStyleSheet("""
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
        rec_layout.addWidget(self.table_recours)
        
        # Boutons recours
        rec_btn_layout = QHBoxLayout()
        
        self.btn_creer_rec = QPushButton("➕ Nouveau recours")
        self.btn_creer_rec.setStyleSheet("""
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
        self.btn_creer_rec.clicked.connect(self.creer_recours)
        rec_btn_layout.addWidget(self.btn_creer_rec)
        
        self.btn_encaissement = QPushButton("💰 Encaisser")
        self.btn_encaissement.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        self.btn_encaissement.clicked.connect(self.enregistrer_encaissement)
        rec_btn_layout.addWidget(self.btn_encaissement)
        
        self.btn_relance = QPushButton("🔔 Relancer")
        self.btn_relance.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        self.btn_relance.clicked.connect(self.ajouter_relance)
        rec_btn_layout.addWidget(self.btn_relance)
        
        rec_btn_layout.addStretch()
        rec_layout.addLayout(rec_btn_layout)
        
        self.sub_tabs.addTab(self.rec_tab, "⚖️ Recours")
        
        # Onglet Encaissements
        self.enc_tab = QWidget()
        enc_layout = QVBoxLayout(self.enc_tab)
        
        self.table_encaissements = QTableWidget()
        self.table_encaissements.setColumnCount(6)
        self.table_encaissements.setHorizontalHeaderLabels([
            "Date", "Montant", "Mode", "Référence", "Partiel", "Statut"
        ])
        self.table_encaissements.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_encaissements.setAlternatingRowColors(True)
        self.table_encaissements.setStyleSheet("""
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
        enc_layout.addWidget(self.table_encaissements)
        
        self.sub_tabs.addTab(self.enc_tab, "💰 Encaissements")
        
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
                self.load_recours(sinistre_id)
                self.load_encaissements(sinistre_id)
        else:
            self.table_recours.setRowCount(0)
            self.table_encaissements.setRowCount(0)
    
    def load_recours(self, sinistre_id: int):
        """Charge les recours d'un sinistre"""
        try:
            recours = self.controller.get_recours_by_sinistre(sinistre_id)
            self.update_rec_table(recours)
            
            total = len(recours)
            aboutis = sum(1 for r in recours if r.get('statut') in ['ABOUTI', 'ENCAISSE', 'PAYE', 'COMPTABILISE', 'CLOTURE'])
            encours = total - aboutis
            
            total_reclame = sum(r.get('montant_reclame', 0) for r in recours)
            total_encaisse = sum(r.get('montant_encaisse', 0) for r in recours)
            taux = (total_encaisse / total_reclame * 100) if total_reclame > 0 else 0
            
            self.lbl_total.setText(f"Total recours: {total}")
            self.lbl_aboutis.setText(f"✅ Aboutis: {aboutis}")
            self.lbl_encours.setText(f"🟡 En cours: {encours}")
            self.lbl_taux_recup.setText(f"📊 Taux récupération: {taux:.1f}%")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement recours: {str(e)}")
    
    def update_rec_table(self, recours: List[dict]):
        """Met à jour le tableau des recours"""
        self.table_recours.setRowCount(len(recours))
        
        statut_colors = {
            'OUVERT': '#f59e0b',
            'EN_INSTRUCTION': '#3b82f6',
            'RELANCE': '#8b5cf6',
            'CONTESTE': '#ef4444',
            'REFUSE': '#ef4444',
            'ABOUTI': '#06b6d4',
            'EN_ATTENTE_ENCAISSEMENT': '#f97316',
            'PARTIELLEMENT_ENCAISSE': '#f97316',
            'ENCAISSE': '#22c55e',
            'REVERSEMENT_EN_COURS': '#8b5cf6',
            'PAYE': '#22c55e',
            'COMPTABILISE': '#22c55e',
            'CLOTURE': '#64748b'
        }
        
        for i, rec in enumerate(recours):
            self.table_recours.setItem(i, 0, QTableWidgetItem(rec.get('numero_recours', '')))
            self.table_recours.setItem(i, 1, QTableWidgetItem(rec.get('debiteur_nom', '')))
            self.table_recours.setItem(i, 2, QTableWidgetItem(f"{rec.get('montant_reclame', 0):,.0f}"))
            self.table_recours.setItem(i, 3, QTableWidgetItem(f"{rec.get('montant_accepte', 0):,.0f}" if rec.get('montant_accepte') else '-'))
            self.table_recours.setItem(i, 4, QTableWidgetItem(f"{rec.get('montant_encaisse', 0):,.0f}"))
            self.table_recours.setItem(i, 5, QTableWidgetItem(f"{rec.get('solde', 0):,.0f}"))
            
            statut = rec.get('statut', '')
            statut_item = QTableWidgetItem(statut)
            color = statut_colors.get(statut, '#64748b')
            statut_item.setBackground(QColor(color))
            statut_item.setForeground(QColor('white'))
            self.table_recours.setItem(i, 6, statut_item)
    
    def load_encaissements(self, sinistre_id: int):
        """Charge les encaissements"""
        try:
            # TODO: Récupérer les encaissements
            self.table_encaissements.setRowCount(0)
        except Exception as e:
            print(f"Erreur chargement encaissements: {e}")
    
    def creer_recours(self):
        """Crée un nouveau recours"""
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        dialog = RecoursDialog(self.controller, self.current_sinistre_id, self.user)
        if dialog.exec():
            self.load_recours(self.current_sinistre_id)
    
    def enregistrer_encaissement(self):
        """Enregistre un encaissement"""
        row = self.table_recours.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
            return
        
        dialog = EncaissementDialog(self.controller, self.user)
        if dialog.exec():
            self.load_recours(self.current_sinistre_id)
            self.load_encaissements(self.current_sinistre_id)
    
    def ajouter_relance(self):
        """Ajoute une relance"""
        row = self.table_recours.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
            return
        
        QMessageBox.information(self, "Relance", "Dialogue de relance (à implémenter)")


class RecoursDialog(QDialog):
    """Dialogue de création de recours"""
    
    def __init__(self, controller, sinistre_id, user, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.sinistre_id = sinistre_id
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
            
            result = self.controller.creer_recours(data)
            if result:
                QMessageBox.information(self, "Succès", "Recours créé avec succès")
                super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


class EncaissementDialog(QDialog):
    """Dialogue d'enregistrement d'encaissement"""
    
    def __init__(self, controller, user, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.setWindowTitle("Enregistrer un encaissement")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Encaissement")
        form_layout = QFormLayout(form_group)
        
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999999999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        form_layout.addRow("Montant:", self.input_montant)
        
        self.input_mode = QComboBox()
        self.input_mode.addItems(["VIREMENT", "CHEQUE", "MOBILE_MONEY", "COMPENSATION"])
        form_layout.addRow("Mode:", self.input_mode)
        
        self.input_reference = QLineEdit()
        self.input_reference.setPlaceholderText("Référence bancaire")
        form_layout.addRow("Référence:", self.input_reference)
        
        self.input_date = QDateEdit()
        self.input_date.setDate(QDate.currentDate())
        self.input_date.setCalendarPopup(True)
        form_layout.addRow("Date:", self.input_date)
        
        layout.addWidget(form_group)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def accept(self):
        # TODO: Envoyer les données au contrôleur
        super().accept()