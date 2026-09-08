"""
Dialogue d'affectation d'un expert à une mission
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton,
    QDialogButtonBox, QMessageBox, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from datetime import datetime


class AffecterExpertDialog(QDialog):
    """Dialogue d'affectation d'un expert à une mission"""
    
    expert_affected = Signal(dict)  # Émis quand l'expert est affecté
    
    def __init__(self, mission_id, mission_info, expertise_controller, user, parent=None):
        super().__init__(parent)
        self.mission_id = mission_id
        self.mission_info = mission_info or {}
        self.expertise_controller = expertise_controller
        self.user = user
        self.selected_expert_id = None
        
        self.setWindowTitle("Affecter un expert à la mission")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self.setup_ui()
        self.load_experts()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # ============================================================
        # EN-TÊTE AVEC INFOS MISSION
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
        
        title = QLabel("👤 Affectation d'expert")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a73e8;")
        header_layout.addWidget(title)
        
        info_layout = QHBoxLayout()
        
        self.lbl_mission = QLabel(f"Mission: {self.mission_info.get('numero_mission', 'N/A')}")
        info_layout.addWidget(self.lbl_mission)
        
        self.lbl_type = QLabel(f"Type: {self.mission_info.get('type_expertise', 'N/A')}")
        info_layout.addWidget(self.lbl_type)
        
        self.lbl_statut = QLabel(f"Statut: {self.mission_info.get('statut', 'N/A')}")
        statut = self.mission_info.get('statut', '')
        statut_colors = {
            'CREEE': '#f59e0b',
            'AFFECTEE': '#3b82f6',
            'EN_COURS': '#8b5cf6',
            'RAPPORT_REÇU': '#06b6d4',
            'VALIDE': '#22c55e'
        }
        color = statut_colors.get(statut, '#64748b')
        self.lbl_statut.setStyleSheet(f"color: {color}; font-weight: bold;")
        info_layout.addWidget(self.lbl_statut)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        layout.addWidget(header_frame)
        
        # ============================================================
        # SECTION: LISTE DES EXPERTS DISPONIBLES
        # ============================================================
        form_group = QGroupBox("Experts disponibles")
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
        group_layout = QVBoxLayout(form_group)
        
        # Barre de recherche
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un expert...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border-color: #1a73e8;
            }
        """)
        self.search_input.textChanged.connect(self.filter_experts)
        search_layout.addWidget(self.search_input)
        
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedSize(35, 35)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                border-radius: 17px;
                border: 1px solid #e2e8f0;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """)
        self.btn_refresh.clicked.connect(self.load_experts)
        search_layout.addWidget(self.btn_refresh)
        
        group_layout.addLayout(search_layout)
        
        # Tableau des experts
        self.table_experts = QTableWidget()
        self.table_experts.setColumnCount(5)
        self.table_experts.setHorizontalHeaderLabels([
            "ID", "Nom", "Spécialité", "Disponibilité", "Actions"
        ])
        self.table_experts.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_experts.setAlternatingRowColors(True)
        self.table_experts.setStyleSheet("""
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
        self.table_experts.setSortingEnabled(True)
        self.table_experts.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        group_layout.addWidget(self.table_experts)
        
        layout.addWidget(form_group)
        
        # ============================================================
        # SECTION: RÉCAPITULATIF DE LA SÉLECTION
        # ============================================================
        self.selection_frame = QFrame()
        self.selection_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 8px;
                padding: 12px;
            }
            QLabel {
                color: #0369a1;
                font-size: 12px;
            }
            QLabel.title {
                font-weight: bold;
                font-size: 13px;
            }
        """)
        self.selection_frame.hide()
        selection_layout = QVBoxLayout(self.selection_frame)
        
        selection_title = QLabel("📋 Expert sélectionné")
        selection_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #0369a1;")
        selection_layout.addWidget(selection_title)
        
        self.selected_expert_label = QLabel("Aucun expert sélectionné")
        self.selected_expert_label.setStyleSheet("color: #0369a1;")
        selection_layout.addWidget(self.selected_expert_label)
        
        layout.addWidget(self.selection_frame)
        
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
        
        self.btn_affecter = QPushButton("✅ Affecter l'expert")
        self.btn_affecter.setStyleSheet("""
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
        self.btn_affecter.clicked.connect(self.affecter_expert)
        self.btn_affecter.setEnabled(False)
        btn_layout.addWidget(self.btn_affecter)
        
        layout.addLayout(btn_layout)
    
    def load_experts(self):
        """Charge la liste des experts disponibles"""
        try:
            # TODO: Récupérer les experts depuis la base
            # Pour l'instant, données mockées
            experts = [
                {'id': 1, 'nom': 'Dr. Jean Dupont', 'specialite': 'Auto', 'disponible': True},
                {'id': 2, 'nom': 'Mme. Marie Martin', 'specialite': 'Bâtiment', 'disponible': True},
                {'id': 3, 'nom': 'M. Pierre Durand', 'specialite': 'Transport', 'disponible': False},
                {'id': 4, 'nom': 'Dr. Sophie Lefevre', 'specialite': 'Médical', 'disponible': True},
                {'id': 5, 'nom': 'M. Michel Bernard', 'specialite': 'Judiciaire', 'disponible': True},
            ]
            self._display_experts(experts)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement experts: {str(e)}")
    
    def _display_experts(self, experts: list):
        """Affiche la liste des experts dans le tableau"""
        self.table_experts.setRowCount(len(experts))
        self.experts_data = experts
        
        for i, expert in enumerate(experts):
            # ID
            self.table_experts.setItem(i, 0, QTableWidgetItem(str(expert.get('id', ''))))
            
            # Nom
            nom_item = QTableWidgetItem(expert.get('nom', ''))
            nom_item.setData(Qt.UserRole, expert)
            self.table_experts.setItem(i, 1, nom_item)
            
            # Spécialité
            self.table_experts.setItem(i, 2, QTableWidgetItem(expert.get('specialite', '')))
            
            # Disponibilité
            disponible = expert.get('disponible', False)
            dispo_item = QTableWidgetItem("✅ Disponible" if disponible else "❌ Non disponible")
            dispo_item.setForeground(QColor("#22c55e" if disponible else "#ef4444"))
            self.table_experts.setItem(i, 3, dispo_item)
            
            # Bouton d'action
            btn = QPushButton("👤 Sélectionner")
            btn.setStyleSheet("""
                QPushButton {
                    padding: 4px 12px;
                    border-radius: 4px;
                    background-color: #1a73e8;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #1557b0;
                }
            """)
            btn.clicked.connect(lambda checked, row=i: self.select_expert(row))
            
            # Désactiver le bouton si expert non disponible
            if not disponible:
                btn.setEnabled(False)
                btn.setStyleSheet("""
                    QPushButton {
                        padding: 4px 12px;
                        border-radius: 4px;
                        background-color: #e2e8f0;
                        color: #94a3b8;
                    }
                """)
            
            self.table_experts.setCellWidget(i, 4, btn)
    
    def filter_experts(self):
        """Filtre la liste des experts selon la recherche"""
        search_text = self.search_input.text().lower()
        
        for i in range(self.table_experts.rowCount()):
            nom = self.table_experts.item(i, 1).text().lower()
            specialite = self.table_experts.item(i, 2).text().lower()
            
            if search_text in nom or search_text in specialite:
                self.table_experts.setRowHidden(i, False)
            else:
                self.table_experts.setRowHidden(i, True)
    
    def select_expert(self, row: int):
        """Sélectionne un expert"""
        expert_data = self.table_experts.item(row, 1).data(Qt.UserRole)
        if expert_data:
            self.selected_expert_id = expert_data.get('id')
            self.selected_expert_label.setText(
                f"👤 {expert_data.get('nom')} - {expert_data.get('specialite')}"
            )
            self.selection_frame.show()
            self.btn_affecter.setEnabled(True)
            
            # Mettre en surbrillance la ligne sélectionnée
            for i in range(self.table_experts.rowCount()):
                for j in range(self.table_experts.columnCount()):
                    item = self.table_experts.item(i, j)
                    if item:
                        if i == row:
                            item.setBackground(QColor("#e8f0fe"))
                        else:
                            item.setBackground(QColor("white"))
    
    def affecter_expert(self):
        """Affecte l'expert sélectionné à la mission"""
        if not self.selected_expert_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un expert")
            return
        
        # Récupérer le nom de l'expert
        expert_nom = self.selected_expert_label.text().replace("👤 ", "")
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous affecter l'expert '{expert_nom}' à cette mission ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.expertise_controller.affecter_expert(
                    self.mission_id,
                    self.selected_expert_id
                )
                
                if result:
                    self.expert_affected.emit({
                        'mission_id': self.mission_id,
                        'expert_id': self.selected_expert_id,
                        'expert_nom': expert_nom
                    })
                    QMessageBox.information(
                        self,
                        "Succès",
                        f"✅ Expert '{expert_nom}' affecté avec succès !\n\n"
                        f"📌 La mission est maintenant en attente de démarrage."
                    )
                    self.accept()
                    
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'affectation: {str(e)}")