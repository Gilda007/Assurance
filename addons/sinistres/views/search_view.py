

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
from typing import Optional, List, Dict, Any

# Import des contrôleurs
from addons.sinistres.controllers.sinistre_controller import SinistreController
from addons.sinistres.controllers.referentiel_controller import ReferentielController
from addons.sinistres.controllers.expertise_controller import ExpertiseController
from addons.sinistres.controllers.evaluation_controller import EvaluationController
from addons.sinistres.controllers.reglement_controller import ReglementController
from addons.sinistres.controllers.recours_controller import RecoursController

# Import des vues détaillées
from addons.sinistres.views.dossier_360 import Dossier360View
from addons.sinistres.views.parametres_page import ParametresPage
from addons.sinistres.views.tableau_base import TableauActions

# ============================================================
# PAGE 3: RECHERCHE (avec intégration Dossier 360°)
# ============================================================

class RecherchePage(QWidget):
    """Page de recherche des sinistres"""
    
    def __init__(
        self,
        sinistre_controller,
        referentiel_controller,
        expertise_controller,
        evaluation_controller,
        reglement_controller,
        recours_controller,
        user
    ):
        super().__init__()
        self.sinistre_controller = sinistre_controller
        self.referentiel_controller = referentiel_controller
        self.expertise_controller = expertise_controller
        self.evaluation_controller = evaluation_controller
        self.reglement_controller = reglement_controller
        self.recours_controller = recours_controller
        self.user = user
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # En-tête
        header = QLabel("🔍 Recherche de sinistres")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)
        
        # Barre de recherche
        search_layout = QHBoxLayout()
        
        self.input_recherche = QLineEdit()
        self.input_recherche.setPlaceholderText("🔎 Numéro sinistre, client, contrat...")
        self.input_recherche.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)
        self.input_recherche.returnPressed.connect(self.rechercher)
        search_layout.addWidget(self.input_recherche)
        
        self.btn_rechercher = QPushButton("Rechercher")
        self.btn_rechercher.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 10px 25px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_rechercher.clicked.connect(self.rechercher)
        search_layout.addWidget(self.btn_rechercher)
        
        layout.addLayout(search_layout)
        
        # Filtres rapides
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(10)
        
        self.filter_statut = QComboBox()
        self.filter_statut.addItem("Tous les statuts", "")
        for statut in ["OUVERT", "EN_INSTRUCTION", "EN_EXPERTISE", "EN_EVALUATION", "VALIDE", "EN_REGLEMENT", "EN_RECOURS", "CLOTURE"]:
            self.filter_statut.addItem(statut, statut)
        filters_layout.addWidget(QLabel("Statut:"))
        filters_layout.addWidget(self.filter_statut)
        
        self.filter_branche = QComboBox()
        self.filter_branche.addItem("Toutes les branches", "")
        filters_layout.addWidget(QLabel("Branche:"))
        filters_layout.addWidget(self.filter_branche)
        
        filters_layout.addStretch()
        layout.addLayout(filters_layout)
        
        # Résultats
        layout.addWidget(QLabel("📋 Résultats"))
        
        self.table_resultats = QTableWidget()
        self.table_resultats.setColumnCount(7)
        self.table_resultats.setHorizontalHeaderLabels([
            "N° Sinistre", "Référence", "Client", "Branche", "Date", "Statut", "Montant"
        ])
        self.table_resultats.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_resultats.setAlternatingRowColors(True)
        self.table_resultats.setStyleSheet("""
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
        self.table_resultats.setSortingEnabled(True)
        self.table_resultats.doubleClicked.connect(self._on_row_double_clicked)
        layout.addWidget(self.table_resultats)
        
        # Charger les branches pour le filtre
        self._load_branches()
    
    def _load_branches(self):
        """Charge les branches pour le filtre"""
        try:
            branches = self.referentiel_controller.get_referentiels_by_famille("branches")
            for b in branches:
                self.filter_branche.addItem(b.get('libelle', ''), b.get('code', ''))
        except Exception as e:
            print(f"Erreur chargement branches: {e}")
    
    def rechercher(self):
        """Exécute la recherche"""
        try:
            criteres = {}
            
            text = self.input_recherche.text().strip()
            if text:
                criteres['numero_sinistre'] = text
            
            statut = self.filter_statut.currentData()
            if statut:
                criteres['statut'] = statut
            
            branche = self.filter_branche.currentData()
            if branche:
                criteres['branche'] = branche
            
            sinistres = self.sinistre_controller.rechercher_sinistres(criteres)
            self._afficher_resultats(sinistres)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche: {str(e)}")
    
    def _afficher_resultats(self, sinistres: List[dict]):
        """Affiche les résultats de la recherche"""
        self.table_resultats.setRowCount(len(sinistres))
        
        for i, s in enumerate(sinistres):
            self.table_resultats.setItem(i, 0, QTableWidgetItem(s.get('numero_sinistre', '')))
            self.table_resultats.setItem(i, 1, QTableWidgetItem(s.get('numero_reference', '') or '-'))
            self.table_resultats.setItem(i, 2, QTableWidgetItem(str(s.get('client_id', ''))))
            self.table_resultats.setItem(i, 3, QTableWidgetItem(s.get('branche', '')))
            self.table_resultats.setItem(i, 4, QTableWidgetItem(s.get('date_survenance', '')[:10] if s.get('date_survenance') else ''))
            
            statut_item = QTableWidgetItem(s.get('statut', ''))
            statut_colors = {
                'OUVERT': '#f59e0b',
                'CLOTURE': '#22c55e',
                'EN_INSTRUCTION': '#3b82f6',
                'EN_EXPERTISE': '#8b5cf6',
                'EN_EVALUATION': '#ec4899',
                'VALIDE': '#06b6d4',
                'EN_REGLEMENT': '#f97316',
                'EN_RECOURS': '#ef4444'
            }
            color = statut_colors.get(s.get('statut', ''), '#64748b')
            statut_item.setBackground(QColor(color))
            statut_item.setForeground(QColor('white'))
            self.table_resultats.setItem(i, 5, statut_item)
            
            self.table_resultats.setItem(i, 6, QTableWidgetItem(f"{s.get('montant_net', 0):,.0f}"))
            
            # Stocker l'ID pour l'ouverture du dossier 360°
            self.table_resultats.item(i, 0).setData(Qt.UserRole, s.get('id'))
    
    def _on_row_double_clicked(self, index):
        """Ouvre le détail de la mission sélectionnée"""
        row = index.row()
        if row >= 0:
            self.open_mission_detail(row)

    def open_dossier_360(self, sinistre_id: int):
        """Ouvre la vue Dossier 360°"""
        try:
            dossier = Dossier360View(
                sinistre_id=sinistre_id,
                sinistre_controller=self.sinistre_controller,
                referentiel_controller=self.referentiel_controller,
                expertise_controller=self.expertise_controller,
                evaluation_controller=self.evaluation_controller,
                reglement_controller=self.reglement_controller,
                recours_controller=self.recours_controller,
                user=self.user
            )
            # Remplacer la page courante par le dossier
            parent = self.parent()
            if hasattr(parent, 'container'):
                # Ajouter comme page temporaire
                parent.container.addWidget(dossier)
                parent.container.setCurrentWidget(dossier)
            else:
                QMessageBox.warning(self, "Erreur", "Impossible d'ouvrir le dossier 360°")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur d'ouverture du dossier: {str(e)}")
    
    def refresh(self):
        """Rafraîchit la page"""
        if self.filter_branche.count() <= 1:
            self._load_branches()

    def get_selected_mission_id(self) -> Optional[int]:
        """Retourne l'ID de la mission sélectionnée"""
        row = self.table.currentRow()
        if row >= 0:
            mission_numero = self.table.item(row, 0).text()
            try:
                mission_data = self.controller.get_mission_by_numero(mission_numero)
                if mission_data:
                    return mission_data.get('id')
            except:
                pass
        return None

    def _on_row_double_clicked(self, index):
        """Ouvre le Dossier 360° du sinistre sélectionné"""
        row = index.row()
        if row >= 0:
            sinistre_id = self.table_resultats.item(row, 0).data(Qt.UserRole)
            if sinistre_id:
                self.open_dossier_360(sinistre_id)

    def open_dossier_360(self, sinistre_id: int):
        """Ouvre la vue Dossier 360°"""
        try:
            dossier = Dossier360View(
                sinistre_id=sinistre_id,
                sinistre_controller=self.sinistre_controller,
                referentiel_controller=self.referentiel_controller,
                expertise_controller=self.expertise_controller,
                evaluation_controller=self.evaluation_controller,
                reglement_controller=self.reglement_controller,
                recours_controller=self.recours_controller,
                user=self.user
            )
            parent = self.parent()
            if hasattr(parent, 'container'):
                parent.container.addWidget(dossier)
                parent.container.setCurrentWidget(dossier)
            else:
                QMessageBox.warning(self, "Erreur", "Impossible d'ouvrir le dossier 360°")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur d'ouverture du dossier: {str(e)}")

    def open_mission_detail(self, mission_numero: str):
        """Ouvre le détail d'une mission"""
        QMessageBox.information(self, "Détail", f"Détail de la mission {mission_numero}")
