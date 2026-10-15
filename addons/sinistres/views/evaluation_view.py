"""
Vue Évaluations - Gestion des évaluations et provisions
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QComboBox, QLineEdit, QDateEdit,
    QFormLayout, QGroupBox, QDialog, QDialogButtonBox, QMessageBox,
    QTextEdit, QDoubleSpinBox, QFrame, QTabWidget, QSplitter
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor

from datetime import datetime
from typing import Optional, List, Dict, Any


class EvaluationsView(QWidget):
    """Vue de gestion des évaluations"""
    
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
        
        title = QLabel("💰 Gestion des Évaluations")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Sélecteur de sinistre
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
        
        self.lbl_total = QLabel("Total évalué: 0 FCFA")
        self.lbl_total.setStyleSheet("font-weight: bold; color: #1e293b; font-size: 14px;")
        stats_layout.addWidget(self.lbl_total)
        
        stats_layout.addStretch()
        
        self.lbl_validees = QLabel("✅ Validées: 0")
        self.lbl_validees.setStyleSheet("color: #22c55e;")
        stats_layout.addWidget(self.lbl_validees)
        
        self.lbl_non_validees = QLabel("❌ Non validées: 0")
        self.lbl_non_validees.setStyleSheet("color: #ef4444;")
        stats_layout.addWidget(self.lbl_non_validees)
        
        self.lbl_provisions = QLabel("📊 Provisions: 0 FCFA")
        self.lbl_provisions.setStyleSheet("color: #3b82f6;")
        stats_layout.addWidget(self.lbl_provisions)
        
        layout.addWidget(stats_frame)
        
        # Onglets: Évaluations et Provisions
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
        
        # Onglet Évaluations
        self.eval_tab = QWidget()
        eval_layout = QVBoxLayout(self.eval_tab)
        
        self.table_evaluations = QTableWidget()
        self.table_evaluations.setColumnCount(8)
        self.table_evaluations.setHorizontalHeaderLabels([
            "N°", "Type", "Brut", "Franchise", "Taux", "Net", "Validée", "Actions"
        ])
        self.table_evaluations.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_evaluations.setAlternatingRowColors(True)
        self.table_evaluations.setStyleSheet("""
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
        eval_layout.addWidget(self.table_evaluations)
        
        # Boutons évaluations
        eval_btn_layout = QHBoxLayout()
        
        self.btn_creer_eval = QPushButton("➕ Nouvelle évaluation")
        self.btn_creer_eval.setStyleSheet("""
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
        self.btn_creer_eval.clicked.connect(self.creer_evaluation)
        eval_btn_layout.addWidget(self.btn_creer_eval)
        
        self.btn_reviser = QPushButton("✏️ Réviser")
        self.btn_reviser.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        self.btn_reviser.clicked.connect(self.reviser_evaluation)
        eval_btn_layout.addWidget(self.btn_reviser)
        
        self.btn_valider_eval = QPushButton("✅ Valider")
        self.btn_valider_eval.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        self.btn_valider_eval.clicked.connect(self.valider_evaluation)
        eval_btn_layout.addWidget(self.btn_valider_eval)
        
        eval_btn_layout.addStretch()
        eval_layout.addLayout(eval_btn_layout)
        
        self.sub_tabs.addTab(self.eval_tab, "📊 Évaluations")
        
        # Onglet Provisions
        self.prov_tab = QWidget()
        prov_layout = QVBoxLayout(self.prov_tab)
        
        self.table_provisions = QTableWidget()
        self.table_provisions.setColumnCount(6)
        self.table_provisions.setHorizontalHeaderLabels([
            "N° Provision", "Type", "Montant", "Active", "Comptabilisée", "Actions"
        ])
        self.table_provisions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_provisions.setAlternatingRowColors(True)
        self.table_provisions.setStyleSheet("""
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
        prov_layout.addWidget(self.table_provisions)
        
        prov_btn_layout = QHBoxLayout()
        
        self.btn_creer_prov = QPushButton("➕ Créer une provision")
        self.btn_creer_prov.setStyleSheet("""
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
        self.btn_creer_prov.clicked.connect(self.creer_provision)
        prov_btn_layout.addWidget(self.btn_creer_prov)
        
        prov_btn_layout.addStretch()
        prov_layout.addLayout(prov_btn_layout)
        
        self.sub_tabs.addTab(self.prov_tab, "📦 Provisions")
        
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
                self.load_evaluations(sinistre_id)
                self.load_provisions(sinistre_id)
        else:
            self.table_evaluations.setRowCount(0)
            self.table_provisions.setRowCount(0)
    
    def load_evaluations(self, sinistre_id: int):
        """Charge les évaluations d'un sinistre"""
        try:
            evaluations = self.controller.get_evaluations_by_sinistre(sinistre_id)
            self.update_eval_table(evaluations)
            
            total = sum(e.get('montant_net', 0) for e in evaluations)
            validees = sum(1 for e in evaluations if e.get('est_validee'))
            non_validees = len(evaluations) - validees
            
            self.lbl_total.setText(f"Total évalué: {total:,.0f} FCFA")
            self.lbl_validees.setText(f"✅ Validées: {validees}")
            self.lbl_non_validees.setText(f"❌ Non validées: {non_validees}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement évaluations: {str(e)}")
    
    def update_eval_table(self, evaluations: List[dict]):
        """Met à jour le tableau des évaluations"""
        self.table_evaluations.setRowCount(len(evaluations))
        
        for i, eval_ in enumerate(evaluations):
            self.table_evaluations.setItem(i, 0, QTableWidgetItem(eval_.get('numero_evaluation', '')))
            self.table_evaluations.setItem(i, 1, QTableWidgetItem(eval_.get('type_evaluation', '')))
            self.table_evaluations.setItem(i, 2, QTableWidgetItem(f"{eval_.get('montant_brut', 0):,.0f}"))
            self.table_evaluations.setItem(i, 3, QTableWidgetItem(f"{eval_.get('franchise', 0):,.0f}"))
            self.table_evaluations.setItem(i, 4, QTableWidgetItem(f"{eval_.get('taux_responsabilite', 1) * 100:.0f}%"))
            self.table_evaluations.setItem(i, 5, QTableWidgetItem(f"{eval_.get('montant_net', 0):,.0f}"))
            
            validee_item = QTableWidgetItem("✅" if eval_.get('est_validee') else "❌")
            validee_item.setForeground(QColor("#22c55e" if eval_.get('est_validee') else "#ef4444"))
            self.table_evaluations.setItem(i, 6, validee_item)
            
            btn = QPushButton("👁️ Voir")
            btn.setStyleSheet("padding: 4px 10px; border-radius: 4px;")
            btn.clicked.connect(lambda checked, row=i: self.open_evaluation_detail(row))
            self.table_evaluations.setCellWidget(i, 7, btn)
    
    def load_provisions(self, sinistre_id: int):
        """Charge les provisions d'un sinistre"""
        try:
            provisions = self.controller.get_provisions_by_sinistre(sinistre_id)
            self.update_prov_table(provisions)
            
            total = sum(p.get('montant', 0) for p in provisions if p.get('est_active'))
            self.lbl_provisions.setText(f"📊 Provisions: {total:,.0f} FCFA")
            
        except Exception as e:
            print(f"Erreur chargement provisions: {e}")
    
    def update_prov_table(self, provisions: List[dict]):
        """Met à jour le tableau des provisions"""
        self.table_provisions.setRowCount(len(provisions))
        
        for i, prov in enumerate(provisions):
            self.table_provisions.setItem(i, 0, QTableWidgetItem(prov.get('numero_provision', '')))
            self.table_provisions.setItem(i, 1, QTableWidgetItem(prov.get('type_provision', '')))
            self.table_provisions.setItem(i, 2, QTableWidgetItem(f"{prov.get('montant', 0):,.0f}"))
            
            active_item = QTableWidgetItem("✅" if prov.get('est_active') else "❌")
            active_item.setForeground(QColor("#22c55e" if prov.get('est_active') else "#ef4444"))
            self.table_provisions.setItem(i, 3, active_item)
            
            comptabilisee_item = QTableWidgetItem("✅" if prov.get('est_comptabilisee') else "❌")
            comptabilisee_item.setForeground(QColor("#22c55e" if prov.get('est_comptabilisee') else "#ef4444"))
            self.table_provisions.setItem(i, 4, comptabilisee_item)
    
    def open_evaluation_detail(self, row: int):
        """Ouvre le détail d'une évaluation"""
        numero = self.table_evaluations.item(row, 0).text()
        QMessageBox.information(self, "Détail", f"Détail de l'évaluation {numero}\n(Fonctionnalité à venir)")
    
    def creer_evaluation(self):
        """Crée une nouvelle évaluation"""
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        dialog = EvaluationDialog(self.controller, self.current_sinistre_id, self.user)
        if dialog.exec():
            self.load_evaluations(self.current_sinistre_id)
    
    def reviser_evaluation(self):
        """Révisé une évaluation"""
        row = self.table_evaluations.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une évaluation")
            return
        
        QMessageBox.information(self, "Révision", "Dialogue de révision (à implémenter)")
    
    def valider_evaluation(self):
        """Valide une évaluation"""
        row = self.table_evaluations.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une évaluation")
            return
        
        reply = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous valider cette évaluation ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                # TODO: Récupérer l'ID de l'évaluation
                QMessageBox.information(self, "Succès", "Évaluation validée")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def creer_provision(self):
        """Crée une nouvelle provision"""
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        QMessageBox.information(self, "Création", "Dialogue de création de provision (à implémenter)")


class EvaluationDialog(QDialog):
    """Dialogue de création d'évaluation"""
    
    def __init__(self, controller, sinistre_id, user, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.sinistre_id = sinistre_id
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
        self.input_type.addItems([
            "auto_materiel", "auto_corporel", "incendie", 
            "vol", "degats_eau", "rc_generale", "defense_recours"
        ])
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
        
        # Connecter les signaux pour le calcul automatique
        self.input_montant_brut.valueChanged.connect(self.calculer_net)
        self.input_franchise.valueChanged.connect(self.calculer_net)
        self.input_taux.valueChanged.connect(self.calculer_net)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def calculer_net(self):
        """Calcule le montant net automatiquement"""
        brut = self.input_montant_brut.value()
        franchise = self.input_franchise.value()
        taux = self.input_taux.value() / 100
        net = (brut - franchise) * taux
        self.lbl_net.setText(f"Montant net: {net:,.0f} FCFA")
    
    def accept(self):
        """Valide la création"""
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
                QMessageBox.information(self, "Succès", "Évaluation créée avec succès")
                super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))