"""
Vue Expertises - Gestion complète des missions d'expertise
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QComboBox, QLineEdit, QDateEdit,
    QFormLayout, QGroupBox, QDialog, QDialogButtonBox, QMessageBox,
    QTextEdit, QFileDialog, QFrame, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor

from datetime import datetime
from typing import Optional, List, Dict, Any


class ExpertisesView(QWidget):
    """Vue de gestion des expertises"""
    
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
        
        title = QLabel("🔬 Gestion des Expertises")
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
        
        # Statistiques rapides
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.lbl_total = QLabel("Total: 0")
        self.lbl_total.setStyleSheet("font-weight: bold; color: #1e293b;")
        stats_layout.addWidget(self.lbl_total)
        
        stats_layout.addStretch()
        
        self.lbl_en_cours = QLabel("🟣 En cours: 0")
        self.lbl_en_cours.setStyleSheet("color: #8b5cf6;")
        stats_layout.addWidget(self.lbl_en_cours)
        
        self.lbl_termine = QLabel("✅ Terminées: 0")
        self.lbl_termine.setStyleSheet("color: #22c55e;")
        stats_layout.addWidget(self.lbl_termine)
        
        layout.addWidget(stats_frame)
        
        # Liste des expertises
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "N° Mission", "Expert", "Type", "Date", "Échéance", "Montant", "Statut", "Actions"
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
            QTableWidget::item:hover {
                background-color: #f1f5f9;
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
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        
        self.btn_creer = QPushButton("➕ Nouvelle mission")
        self.btn_creer.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 10px 25px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_creer.clicked.connect(self.creer_mission)
        btn_layout.addWidget(self.btn_creer)
        
        self.btn_affecter = QPushButton("👤 Affecter expert")
        self.btn_affecter.setStyleSheet("padding: 10px 25px; border-radius: 8px;")
        self.btn_affecter.clicked.connect(self.affecter_expert)
        btn_layout.addWidget(self.btn_affecter)
        
        self.btn_rapport = QPushButton("📄 Déposer rapport")
        self.btn_rapport.setStyleSheet("padding: 10px 25px; border-radius: 8px;")
        self.btn_rapport.clicked.connect(self.deposer_rapport)
        btn_layout.addWidget(self.btn_rapport)
        
        self.btn_valider = QPushButton("✅ Valider")
        self.btn_valider.setStyleSheet("padding: 10px 25px; border-radius: 8px;")
        self.btn_valider.clicked.connect(self.valider_mission)
        btn_layout.addWidget(self.btn_valider)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def load_data(self):
        """Charge les sinistres pour le combo"""
        try:
            # TODO: Récupérer les sinistres récents
            # Pour l'instant, on utilise une méthode qui sera implémentée
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
        """Charge les expertises du sinistre sélectionné"""
        if index > 0:
            sinistre_id = self.sinistre_combo.currentData()
            if sinistre_id:
                self.current_sinistre_id = sinistre_id
                self.load_expertises(sinistre_id)
        else:
            self.table.setRowCount(0)
    
    def load_expertises(self, sinistre_id: int):
        """Charge les expertises d'un sinistre"""
        try:
            expertises = self.controller.get_missions_by_sinistre(sinistre_id)
            self.update_table(expertises)
            
            # Mettre à jour les stats
            total = len(expertises)
            en_cours = sum(1 for e in expertises if e.get('statut') in ['CREEE', 'AFFECTEE', 'EN_COURS', 'RAPPORT_REÇU'])
            termine = sum(1 for e in expertises if e.get('statut') in ['VALIDE'])
            
            self.lbl_total.setText(f"Total: {total}")
            self.lbl_en_cours.setText(f"🟣 En cours: {en_cours}")
            self.lbl_termine.setText(f"✅ Terminées: {termine}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement expertises: {str(e)}")
    
    def update_table(self, expertises: List[dict]):
        """Met à jour le tableau des expertises"""
        self.table.setRowCount(len(expertises))
        
        statut_colors = {
            'CREEE': '#f59e0b',
            'AFFECTEE': '#3b82f6',
            'EN_COURS': '#8b5cf6',
            'RAPPORT_REÇU': '#06b6d4',
            'VALIDE': '#22c55e',
            'ANNULE': '#ef4444'
        }
        
        statut_labels = {
            'CREEE': 'Créée',
            'AFFECTEE': 'Affectée',
            'EN_COURS': 'En cours',
            'RAPPORT_REÇU': 'Rapport reçu',
            'VALIDE': 'Validée',
            'ANNULE': 'Annulée'
        }
        
        for i, exp in enumerate(expertises):
            self.table.setItem(i, 0, QTableWidgetItem(exp.get('numero_mission', '')))
            self.table.setItem(i, 1, QTableWidgetItem(exp.get('expert_nom', 'Non affecté')))
            self.table.setItem(i, 2, QTableWidgetItem(exp.get('type_expertise', '')))
            self.table.setItem(i, 3, QTableWidgetItem(exp.get('date_mission', '')[:10] if exp.get('date_mission') else ''))
            self.table.setItem(i, 4, QTableWidgetItem(exp.get('date_echeance', '')[:10] if exp.get('date_echeance') else ''))
            self.table.setItem(i, 5, QTableWidgetItem(f"{exp.get('montant_estime', 0):,.0f}" if exp.get('montant_estime') else '-'))
            
            statut = exp.get('statut', '')
            statut_item = QTableWidgetItem(statut_labels.get(statut, statut))
            color = statut_colors.get(statut, '#64748b')
            statut_item.setBackground(QColor(color))
            statut_item.setForeground(QColor('white'))
            self.table.setItem(i, 6, statut_item)
            
            # Bouton d'action
            btn = QPushButton("👁️ Voir")
            btn.setStyleSheet("padding: 4px 10px; border-radius: 4px;")
            btn.clicked.connect(lambda checked, row=i: self.open_mission_detail(row))
            self.table.setCellWidget(i, 7, btn)
        
        # Ajuster les colonnes
        self.table.resizeColumnsToContents()
    
    def open_mission_detail(self, row: int):
        """Ouvre le détail d'une mission"""
        numero = self.table.item(row, 0).text()
        QMessageBox.information(self, "Détail", f"Détail de la mission {numero}\n(Fonctionnalité à venir)")
    
    def on_row_double_clicked(self, index):
        """Ouvre le détail de la mission sélectionnée"""
        row = index.row()
        if row >= 0:
            self.open_mission_detail(row)
    
    def creer_mission(self):
        """Ouvre le dialogue de création de mission"""
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        dialog = MissionDialog(self.controller, self.current_sinistre_id, self.user)
        if dialog.exec():
            self.load_expertises(self.current_sinistre_id)
    
    def affecter_expert(self):
        """Affecte un expert à la mission sélectionnée"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une mission")
            return
        
        mission_id = self.table.item(row, 0).data(Qt.UserRole)
        if not mission_id:
            mission_id = self.controller.get_mission_by_numero(self.table.item(row, 0).text()).get('id')
        
        # TODO: Ouvrir dialogue d'affectation
        QMessageBox.information(self, "Affectation", "Dialogue d'affectation (à implémenter)")
    
    def deposer_rapport(self):
        """Dépose un rapport pour la mission sélectionnée"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une mission")
            return
        
        # Ouvrir dialogue de dépôt de rapport
        dialog = RapportDialog(self.controller, self.user)
        if dialog.exec():
            self.load_expertises(self.current_sinistre_id)
    
    def valider_mission(self):
        """Valide la mission sélectionnée"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une mission")
            return
        
        mission_numero = self.table.item(row, 0).text()
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous valider la mission {mission_numero} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                mission = self.controller.get_mission_by_numero(mission_numero)
                if mission:
                    result = self.controller.valider_mission(mission.get('id'))
                    if result:
                        QMessageBox.information(self, "Succès", "Mission validée avec succès")
                        self.load_expertises(self.current_sinistre_id)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))


class MissionDialog(QDialog):
    """Dialogue de création de mission d'expertise"""
    
    def __init__(self, controller, sinistre_id, user, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.sinistre_id = sinistre_id
        self.user = user
        self.setWindowTitle("Créer une mission d'expertise")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Formulaire
        form_group = QGroupBox("Informations de la mission")
        form_layout = QFormLayout(form_group)
        
        self.input_type = QComboBox()
        self.input_type.addItems([
            "auto_materiel", "auto_corporel", "batiment", 
            "transport", "medical", "judiciaire"
        ])
        form_layout.addRow("Type d'expertise:", self.input_type)
        
        self.input_domaine = QLineEdit()
        self.input_domaine.setPlaceholderText("Domaine spécifique (optionnel)")
        form_layout.addRow("Domaine:", self.input_domaine)
        
        self.input_echeance = QDateEdit()
        self.input_echeance.setDate(QDate.currentDate().addDays(14))
        self.input_echeance.setCalendarPopup(True)
        form_layout.addRow("Date d'échéance:", self.input_echeance)
        
        self.input_observations = QTextEdit()
        self.input_observations.setMaximumHeight(80)
        self.input_observations.setPlaceholderText("Observations (optionnel)")
        form_layout.addRow("Observations:", self.input_observations)
        
        layout.addWidget(form_group)
        
        # Boutons
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def accept(self):
        """Valide la création"""
        try:
            data = {
                'sinistre_id': self.sinistre_id,
                'type_expertise': self.input_type.currentText(),
                'domaine': self.input_domaine.text().strip() or None,
                'date_echeance': self.input_echeance.date().toPython(),
                'observations': self.input_observations.toPlainText().strip() or None,
                'created_by': self.user.id if self.user else None
            }
            
            result = self.controller.creer_mission(data)
            if result:
                QMessageBox.information(self, "Succès", "Mission créée avec succès")
                super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


class RapportDialog(QDialog):
    """Dialogue de dépôt de rapport d'expertise"""
    
    def __init__(self, controller, user, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.setWindowTitle("Déposer un rapport d'expertise")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Formulaire
        form_group = QGroupBox("Rapport d'expertise")
        form_layout = QFormLayout(form_group)
        
        self.input_contenu = QTextEdit()
        self.input_contenu.setPlaceholderText("Contenu du rapport...")
        self.input_contenu.setMinimumHeight(150)
        form_layout.addRow("Contenu:", self.input_contenu)
        
        self.input_montant = QDoubleSpinBox()
        self.input_montant.setRange(0, 999999999)
        self.input_montant.setPrefix("FCFA ")
        self.input_montant.setDecimals(0)
        self.input_montant.setSingleStep(10000)
        form_layout.addRow("Montant estimé:", self.input_montant)
        
        self.btn_file = QPushButton("📎 Joindre un fichier")
        self.btn_file.clicked.connect(self.select_file)
        self.lbl_file = QLabel("Aucun fichier sélectionné")
        self.lbl_file.setStyleSheet("color: #64748b; font-size: 11px;")
        file_layout = QVBoxLayout()
        file_layout.addWidget(self.btn_file)
        file_layout.addWidget(self.lbl_file)
        form_layout.addRow("Document:", file_layout)
        
        layout.addWidget(form_group)
        
        # Boutons
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def select_file(self):
        """Sélectionne un fichier à joindre"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier",
            "",
            "PDF Files (*.pdf);;Word Files (*.docx);;All Files (*.*)"
        )
        if file_path:
            self.lbl_file.setText(f"📄 {file_path.split('/')[-1]}")
            self.lbl_file.setStyleSheet("color: #1a73e8; font-size: 11px;")
            self.selected_file = file_path