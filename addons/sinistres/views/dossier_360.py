"""
Vue Dossier 360° - Visualisation complète d'un sinistre
Tous les onglets : Général, Client, Dommages, Tiers, Expertises, Évaluations, Règlements, Recours, Documents, Historique
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFrame, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFormLayout, QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QDoubleSpinBox, QSpinBox, QSplitter, QScrollArea, QGridLayout,
    QProgressBar, QToolBar, QMenu, QDialog, QDialogButtonBox,
    QFileDialog, QCheckBox, QRadioButton
)
from PySide6.QtCore import Qt, Signal, Slot, QDate, QDateTime
from PySide6.QtGui import QColor, QFont, QIcon, QAction

from datetime import datetime
from typing import Optional, List, Dict, Any


class Dossier360View(QWidget):
    """
    Vue Dossier 360° - Visualisation complète d'un sinistre
    """
    
    dossier_modified = Signal(int)
    
    def __init__(
        self,
        sinistre_id: int,
        sinistre_controller,
        referentiel_controller,
        expertise_controller,
        evaluation_controller,
        reglement_controller,
        recours_controller,
        user=None,
        parent=None
    ):
        super().__init__(parent)
        
        self.sinistre_id = sinistre_id
        self.sinistre_controller = sinistre_controller
        self.referentiel_controller = referentiel_controller
        self.expertise_controller = expertise_controller
        self.evaluation_controller = evaluation_controller
        self.reglement_controller = reglement_controller
        self.recours_controller = recours_controller
        self.user = user
        self.parent_widget = parent
        
        self.sinistre_data = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        self.setup_toolbar()
        layout.addWidget(self.toolbar)
        
        # Onglets
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 0 0 8px 8px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 2px;
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #1a73e8;
            }
            QTabBar::tab:hover {
                background-color: #f1f5f9;
            }
        """)
        
        # Création des onglets
        self.tab_general = GeneralTab(self)
        self.tab_client = ClientTab(self)
        self.tab_dommages = DommagesTab(self)
        self.tab_tiers = TiersTab(self)
        self.tab_expertises = ExpertisesTab(self)
        self.tab_evaluations = EvaluationsTab(self)
        self.tab_reglements = ReglementsTab(self)
        self.tab_recours = RecoursTab(self)
        self.tab_documents = DocumentsTab(self)
        self.tab_historique = HistoriqueTab(self)
        
        self.tabs.addTab(self.tab_general, "📋 Général")
        self.tabs.addTab(self.tab_client, "👤 Client")
        self.tabs.addTab(self.tab_dommages, "💥 Dommages")
        self.tabs.addTab(self.tab_tiers, "👥 Tiers")
        self.tabs.addTab(self.tab_expertises, "🔬 Expertises")
        self.tabs.addTab(self.tab_evaluations, "💰 Évaluations")
        self.tabs.addTab(self.tab_reglements, "💳 Règlements")
        self.tabs.addTab(self.tab_recours, "⚖️ Recours")
        self.tabs.addTab(self.tab_documents, "📄 Documents")
        self.tabs.addTab(self.tab_historique, "📜 Historique")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self.setup_statusbar()
        layout.addWidget(self.statusbar)
    
    def setup_toolbar(self):
        """Barre d'outils"""
        self.toolbar = QToolBar()
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px 8px 0 0;
                padding: 5px;
                spacing: 10px;
            }
            QToolButton {
                padding: 5px 10px;
                border-radius: 6px;
            }
            QToolButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.toolbar.setMovable(False)
        
        # Titre
        self.title_label = QLabel("Dossier 360°")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        self.toolbar.addWidget(self.title_label)
        
        self.toolbar.addSeparator()
        
        # Numéro sinistre
        self.numero_label = QLabel("SIN-2026-000000")
        self.numero_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1a73e8;")
        self.toolbar.addWidget(self.numero_label)
        
        self.toolbar.addSeparator()
        
        # Statut
        self.statut_label = QLabel("OUVERT")
        self.statut_label.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            padding: 4px 12px;
            border-radius: 12px;
            background-color: #f59e0b;
            color: white;
        """)
        self.toolbar.addWidget(self.statut_label)
        
        self.toolbar.addSeparator()
        
        # Boutons d'action
        self.btn_editer = QAction("✏️ Éditer", self)
        self.btn_editer.triggered.connect(self.edit_sinistre)
        self.toolbar.addAction(self.btn_editer)
        
        self.btn_cloturer = QAction("🔒 Clôturer", self)
        self.btn_cloturer.triggered.connect(self.cloturer_sinistre)
        self.toolbar.addAction(self.btn_cloturer)
        
        self.btn_reouvrir = QAction("🔓 Réouvrir", self)
        self.btn_reouvrir.triggered.connect(self.reouvrir_sinistre)
        self.toolbar.addAction(self.btn_reouvrir)
        
        self.toolbar.addSeparator()
        
        self.btn_imprimer = QAction("🖨️ Imprimer", self)
        self.toolbar.addAction(self.btn_imprimer)
        
        self.toolbar.addStretch()
        
        # Bouton fermer
        self.btn_fermer = QAction("✖ Fermer", self)
        self.btn_fermer.triggered.connect(self.close_view)
        self.toolbar.addAction(self.btn_fermer)
    
    def setup_statusbar(self):
        """Barre de statut"""
        self.statusbar = QFrame()
        self.statusbar.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-top: none;
                border-radius: 0 0 8px 8px;
                padding: 5px 10px;
            }
            QLabel {
                color: #64748b;
                font-size: 11px;
            }
        """)
        layout = QHBoxLayout(self.statusbar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_info = QLabel("Prêt")
        layout.addWidget(self.status_info)
        
        layout.addStretch()
        
        self.status_created = QLabel("Créé le: --")
        layout.addWidget(self.status_created)
        
        self.status_modified = QLabel("Modifié le: --")
        layout.addWidget(self.status_modified)
    
    def load_data(self):
        """Charge les données du sinistre"""
        try:
            self.sinistre_data = self.sinistre_controller.get_sinistre(self.sinistre_id)
            if not self.sinistre_data:
                QMessageBox.critical(self, "Erreur", "Sinistre non trouvé")
                return
            
            self.update_ui()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de chargement: {str(e)}")
    
    def update_ui(self):
        """Met à jour l'interface avec les données chargées"""
        data = self.sinistre_data
        
        # Mettre à jour les labels
        self.numero_label.setText(data.get('numero_sinistre', 'N/A'))
        self.title_label.setText(f"Dossier 360° - {data.get('numero_sinistre', 'N/A')}")
        
        # Statut
        statut = data.get('statut', 'INCONNU')
        statut_colors = {
            'OUVERT': '#f59e0b',
            'EN_INSTRUCTION': '#3b82f6',
            'EN_EXPERTISE': '#8b5cf6',
            'EN_EVALUATION': '#ec4899',
            'VALIDE': '#06b6d4',
            'EN_REGLEMENT': '#f97316',
            'EN_RECOURS': '#ef4444',
            'CLOTURE': '#22c55e',
            'REOUVERT': '#f59e0b'
        }
        self.statut_label.setText(statut)
        self.statut_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: bold;
            padding: 4px 12px;
            border-radius: 12px;
            background-color: {statut_colors.get(statut, '#64748b')};
            color: white;
        """)
        
        # Status bar
        self.status_info.setText(f"Client: {data.get('client_id', 'N/A')} | Branche: {data.get('branche', 'N/A')}")
        self.status_created.setText(f"Créé le: {data.get('created_at', '--')[:10] if data.get('created_at') else '--'}")
        self.status_modified.setText(f"Modifié le: {data.get('updated_at', '--')[:10] if data.get('updated_at') else '--'}")
        
        # Mettre à jour tous les onglets
        self.tab_general.update_data(data)
        self.tab_client.update_data(data)
        self.tab_dommages.update_data(data)
        self.tab_tiers.update_data(data)
        self.tab_expertises.update_data(data)
        self.tab_evaluations.update_data(data)
        self.tab_reglements.update_data(data)
        self.tab_recours.update_data(data)
        self.tab_documents.update_data(data)
        self.tab_historique.update_data(data)
    
    def refresh(self):
        """Rafraîchit toutes les données"""
        self.load_data()
    
    def edit_sinistre(self):
        """Édite le sinistre"""
        from .dialogs import EditSinistreDialog
        dialog = EditSinistreDialog(
            self.sinistre_id,
            self.sinistre_controller,
            self.referentiel_controller,
            self.user,
            self
        )
        if dialog.exec():
            self.dossier_modified.emit(self.sinistre_id)
            self.refresh()
    
    def cloturer_sinistre(self):
        """Clôture le sinistre"""
        reply = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous vraiment clôturer ce sinistre ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                result = self.sinistre_controller.cloturer_sinistre(
                    self.sinistre_id, 
                    "Clôture par l'utilisateur"
                )
                if result:
                    self.dossier_modified.emit(self.sinistre_id)
                    self.refresh()
                    QMessageBox.information(self, "Succès", "Sinistre clôturé avec succès")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def reouvrir_sinistre(self):
        """Réouvre le sinistre"""
        reply = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous vraiment réouvrir ce sinistre ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                result = self.sinistre_controller.reouvrir_sinistre(
                    self.sinistre_id,
                    "Réouverture par l'utilisateur"
                )
                if result:
                    self.dossier_modified.emit(self.sinistre_id)
                    self.refresh()
                    QMessageBox.information(self, "Succès", "Sinistre réouvert avec succès")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def close_view(self):
        """Ferme la vue"""
        try:
            # Si la vue est dans un onglet parent
            if self.parent_widget and hasattr(self.parent_widget, 'removeTab'):
                index = self.parent_widget.indexOf(self)
                if index >= 0:
                    self.parent_widget.removeTab(index)
            # Sinon, suppression directe
            self.deleteLater()
        except Exception as e:
            print(f"Erreur fermeture vue: {e}")
            self.deleteLater()


# ============================================================
# ONGLETS
# ============================================================

class BaseTab(QWidget):
    """Onglet de base"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.dossier_360 = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Configuration de l'interface (à surcharger)"""
        pass
    
    def update_data(self, data):
        """Met à jour les données (à surcharger)"""
        pass


class GeneralTab(BaseTab):
    """Onglet Général"""
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Formulaire d'informations générales
        form_group = QGroupBox("Informations générales")
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
        
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(12)
        
        # Champs d'information (non modifiables en lecture seule)
        self.lbl_numero = QLabel("-")
        self.lbl_numero.setStyleSheet("font-weight: bold; color: #1a73e8;")
        form_layout.addRow("Numéro sinistre:", self.lbl_numero)
        
        self.lbl_reference = QLabel("-")
        form_layout.addRow("Référence:", self.lbl_reference)
        
        self.lbl_statut = QLabel("-")
        form_layout.addRow("Statut:", self.lbl_statut)
        
        self.lbl_branche = QLabel("-")
        form_layout.addRow("Branche:", self.lbl_branche)
        
        self.lbl_categorie = QLabel("-")
        form_layout.addRow("Catégorie:", self.lbl_categorie)
        
        self.lbl_survenance = QLabel("-")
        form_layout.addRow("Date survenance:", self.lbl_survenance)
        
        self.lbl_declaration = QLabel("-")
        form_layout.addRow("Date déclaration:", self.lbl_declaration)
        
        self.lbl_ouverture = QLabel("-")
        form_layout.addRow("Date ouverture:", self.lbl_ouverture)
        
        self.lbl_cloture = QLabel("-")
        form_layout.addRow("Date clôture:", self.lbl_cloture)
        
        self.lbl_responsabilite = QLabel("-")
        form_layout.addRow("Taux responsabilité:", self.lbl_responsabilite)
        
        self.lbl_circonstance = QLabel("-")
        form_layout.addRow("Circonstance:", self.lbl_circonstance)
        
        self.txt_description = QTextEdit()
        self.txt_description.setReadOnly(True)
        self.txt_description.setMaximumHeight(80)
        self.txt_description.setStyleSheet("background-color: #f8fafc;")
        form_layout.addRow("Description:", self.txt_description)
        
        layout.addWidget(form_group)
        
        # Bouton modifier
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_modifier = QPushButton("✏️ Modifier les informations")
        self.btn_modifier.setStyleSheet("""
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
        self.btn_modifier.clicked.connect(self.on_modifier)
        btn_layout.addWidget(self.btn_modifier)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
    
    def update_data(self, data):
        self.lbl_numero.setText(data.get('numero_sinistre', '-'))
        self.lbl_reference.setText(data.get('numero_reference', '-') or '-')
        self.lbl_statut.setText(data.get('statut', '-'))
        self.lbl_branche.setText(data.get('branche', '-'))
        self.lbl_categorie.setText(data.get('categorie', '-'))
        self.lbl_survenance.setText(data.get('date_survenance', '')[:10] if data.get('date_survenance') else '-')
        self.lbl_declaration.setText(data.get('date_declaration', '')[:10] if data.get('date_declaration') else '-')
        self.lbl_ouverture.setText(data.get('date_ouverture', '')[:10] if data.get('date_ouverture') else '-')
        self.lbl_cloture.setText(data.get('date_cloture', '')[:10] if data.get('date_cloture') else '-')
        self.lbl_responsabilite.setText(f"{data.get('taux_responsabilite', 0) * 100:.0f}%")
        self.lbl_circonstance.setText(data.get('circonstance_principale', '-'))
        self.txt_description.setText(data.get('description', '-'))
    
    def on_modifier(self):
        self.dossier_360.edit_sinistre()


class ClientTab(BaseTab):
    """Onglet Client"""
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Informations client
        form_group = QGroupBox("Informations client")
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
        
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(12)
        
        self.lbl_client_id = QLabel("-")
        form_layout.addRow("ID Client:", self.lbl_client_id)
        
        self.lbl_contrat_id = QLabel("-")
        form_layout.addRow("ID Contrat:", self.lbl_contrat_id)
        
        self.lbl_compagnie = QLabel("-")
        form_layout.addRow("Compagnie:", self.lbl_compagnie)
        
        self.lbl_agence = QLabel("-")
        form_layout.addRow("Agence:", self.lbl_agence)
        
        layout.addWidget(form_group)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_voir_client = QPushButton("👤 Voir le client")
        self.btn_voir_client.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        btn_layout.addWidget(self.btn_voir_client)
        
        self.btn_voir_contrat = QPushButton("📄 Voir le contrat")
        self.btn_voir_contrat.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        btn_layout.addWidget(self.btn_voir_contrat)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
    
    def update_data(self, data):
        self.lbl_client_id.setText(str(data.get('client_id', '-')))
        self.lbl_contrat_id.setText(str(data.get('contrat_id', '-')))
        self.lbl_compagnie.setText(str(data.get('compagnie_id', '-')) or '-')
        self.lbl_agence.setText(str(data.get('agence_id', '-')) or '-')


class DommagesTab(BaseTab):
    """Onglet Dommages"""
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Liste des dommages
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Type", "Description", "Montant estimé", "Montant accepté", "Évaluation"
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
        layout.addWidget(self.table)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        self.btn_ajouter = QPushButton("➕ Ajouter un dommage")
        self.btn_ajouter.setStyleSheet("""
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
        self.btn_ajouter.clicked.connect(self.ajouter_dommage)
        btn_layout.addWidget(self.btn_ajouter)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def update_data(self, data):
        dommages = data.get('dommages', [])
        self.table.setRowCount(len(dommages))
        
        for i, d in enumerate(dommages):
            self.table.setItem(i, 0, QTableWidgetItem(d.get('type_dommage', '')))
            self.table.setItem(i, 1, QTableWidgetItem(d.get('description', '')[:50]))
            self.table.setItem(i, 2, QTableWidgetItem(f"{d.get('montant_estime', 0):,.0f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{d.get('montant_accepte', 0):,.0f}" if d.get('montant_accepte') else '-'))
            self.table.setItem(i, 4, QTableWidgetItem(d.get('evaluation_id', '-')))
    
    def ajouter_dommage(self):
        from .dialogs import AddDommageDialog
        dialog = AddDommageDialog(
            self.dossier_360.sinistre_id,
            self.dossier_360.sinistre_controller,
            self.dossier_360.user,
            self
        )
        if dialog.exec():
            self.dossier_360.refresh()


class TiersTab(BaseTab):
    """Onglet Tiers"""
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Type", "Nom", "Téléphone", "Assurance", "Police"
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
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        
        self.btn_ajouter = QPushButton("➕ Ajouter un tiers")
        self.btn_ajouter.setStyleSheet("""
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
        self.btn_ajouter.clicked.connect(self.ajouter_tiers)
        btn_layout.addWidget(self.btn_ajouter)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def update_data(self, data):
        tiers = data.get('tiers', [])
        self.table.setRowCount(len(tiers))
        
        for i, t in enumerate(tiers):
            self.table.setItem(i, 0, QTableWidgetItem(t.get('type_tiers', '')))
            self.table.setItem(i, 1, QTableWidgetItem(f"{t.get('nom', '')} {t.get('prenom', '')}".strip()))
            self.table.setItem(i, 2, QTableWidgetItem(t.get('telephone', '')))
            self.table.setItem(i, 3, QTableWidgetItem(t.get('assurance', '')))
            self.table.setItem(i, 4, QTableWidgetItem(t.get('police_assurance', '')))
    
    def ajouter_tiers(self):
        from .dialogs import AddTiersDialog
        dialog = AddTiersDialog(
            self.dossier_360.sinistre_id,
            self.dossier_360.sinistre_controller,
            self.dossier_360.user,
            self
        )
        if dialog.exec():
            self.dossier_360.refresh()


class ExpertisesTab(BaseTab):
    """Onglet Expertises"""
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "N° Mission", "Expert", "Type", "Date", "Échéance", "Statut"
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
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        
        self.btn_ajouter = QPushButton("➕ Nouvelle expertise")
        self.btn_ajouter.setStyleSheet("""
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
        self.btn_ajouter.clicked.connect(self.ajouter_expertise)
        btn_layout.addWidget(self.btn_ajouter)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def update_data(self, data):
        expertises = data.get('expertises', [])
        self.table.setRowCount(len(expertises))
        
        statut_colors = {
            'CREEE': '#f59e0b',
            'AFFECTEE': '#3b82f6',
            'EN_COURS': '#8b5cf6',
            'RAPPORT_REÇU': '#06b6d4',
            'VALIDE': '#22c55e',
            'ANNULE': '#ef4444'
        }
        
        for i, exp in enumerate(expertises):
            self.table.setItem(i, 0, QTableWidgetItem(exp.get('numero_mission', '')))
            self.table.setItem(i, 1, QTableWidgetItem(exp.get('expert_nom', '')))
            self.table.setItem(i, 2, QTableWidgetItem(exp.get('type_expertise', '')))
            self.table.setItem(i, 3, QTableWidgetItem(exp.get('date_mission', '')[:10] if exp.get('date_mission') else ''))
            self.table.setItem(i, 4, QTableWidgetItem(exp.get('date_echeance', '')[:10] if exp.get('date_echeance') else ''))
            
            statut = exp.get('statut', '')
            statut_item = QTableWidgetItem(statut)
            color = statut_colors.get(statut, '#64748b')
            statut_item.setBackground(QColor(color))
            statut_item.setForeground(QColor('white'))
            self.table.setItem(i, 5, statut_item)
    
    def ajouter_expertise(self):
        from .dialogs import AddExpertiseDialog
        dialog = AddExpertiseDialog(
            self.dossier_360.sinistre_id,
            self.dossier_360.expertise_controller,
            self.dossier_360.user,
            self
        )
        if dialog.exec():
            self.dossier_360.refresh()


class EvaluationsTab(BaseTab):
    """Onglet Évaluations"""
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Résumé
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        summary_layout = QHBoxLayout(summary_frame)
        
        self.lbl_total = QLabel("Total évalué: 0")
        self.lbl_total.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b;")
        summary_layout.addWidget(self.lbl_total)
        
        summary_layout.addStretch()
        
        self.lbl_validees = QLabel("Validées: 0")
        self.lbl_validees.setStyleSheet("font-size: 14px; color: #22c55e;")
        summary_layout.addWidget(self.lbl_validees)
        
        self.lbl_non_validees = QLabel("Non validées: 0")
        self.lbl_non_validees.setStyleSheet("font-size: 14px; color: #ef4444;")
        summary_layout.addWidget(self.lbl_non_validees)
        
        layout.addWidget(summary_frame)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "N° Évaluation", "Type", "Montant brut", "Franchise", "Montant net", "Validée"
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
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        
        self.btn_ajouter = QPushButton("➕ Nouvelle évaluation")
        self.btn_ajouter.setStyleSheet("""
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
        self.btn_ajouter.clicked.connect(self.ajouter_evaluation)
        btn_layout.addWidget(self.btn_ajouter)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def update_data(self, data):
        evaluations = data.get('evaluations', [])
        self.table.setRowCount(len(evaluations))
        
        total = 0
        validees = 0
        
        for i, eval_ in enumerate(evaluations):
            montant_net = eval_.get('montant_net', 0)
            total += montant_net
            if eval_.get('est_validee'):
                validees += 1
            
            self.table.setItem(i, 0, QTableWidgetItem(eval_.get('numero_evaluation', '')))
            self.table.setItem(i, 1, QTableWidgetItem(eval_.get('type_evaluation', '')))
            self.table.setItem(i, 2, QTableWidgetItem(f"{eval_.get('montant_brut', 0):,.0f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{eval_.get('franchise', 0):,.0f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{montant_net:,.0f}"))
            
            validee_item = QTableWidgetItem("✅" if eval_.get('est_validee') else "❌")
            validee_item.setForeground(QColor("#22c55e" if eval_.get('est_validee') else "#ef4444"))
            self.table.setItem(i, 5, validee_item)
        
        self.lbl_total.setText(f"Total évalué: {total:,.0f}")
        self.lbl_validees.setText(f"Validées: {validees}")
        self.lbl_non_validees.setText(f"Non validées: {len(evaluations) - validees}")
    
    def ajouter_evaluation(self):
        from .dialogs import AddEvaluationDialog
        dialog = AddEvaluationDialog(
            self.dossier_360.sinistre_id,
            self.dossier_360.evaluation_controller,
            self.dossier_360.user,
            self
        )
        if dialog.exec():
            self.dossier_360.refresh()


class ReglementsTab(BaseTab):
    """Onglet Règlements"""
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Résumé
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        summary_layout = QHBoxLayout(summary_frame)
        
        self.lbl_total_paye = QLabel("Total payé: 0")
        self.lbl_total_paye.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b;")
        summary_layout.addWidget(self.lbl_total_paye)
        
        summary_layout.addStretch()
        
        self.lbl_nb_reglements = QLabel("Règlements: 0")
        self.lbl_nb_reglements.setStyleSheet("font-size: 14px; color: #64748b;")
        summary_layout.addWidget(self.lbl_nb_reglements)
        
        layout.addWidget(summary_frame)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "N° Règlement", "Bénéficiaire", "Montant", "Type", "Date", "Statut"
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
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        
        self.btn_ajouter = QPushButton("➕ Nouveau règlement")
        self.btn_ajouter.setStyleSheet("""
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
        self.btn_ajouter.clicked.connect(self.ajouter_reglement)
        btn_layout.addWidget(self.btn_ajouter)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def update_data(self, data):
        reglements = data.get('reglements', [])
        self.table.setRowCount(len(reglements))
        
        total_paye = 0
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
            if reg.get('statut') == 'PAYE':
                total_paye += reg.get('montant', 0)
            
            self.table.setItem(i, 0, QTableWidgetItem(reg.get('numero_reglement', '')))
            self.table.setItem(i, 1, QTableWidgetItem(reg.get('beneficiaire_nom', '')))
            self.table.setItem(i, 2, QTableWidgetItem(f"{reg.get('montant', 0):,.0f}"))
            self.table.setItem(i, 3, QTableWidgetItem(reg.get('type_paiement', '')))
            self.table.setItem(i, 4, QTableWidgetItem(reg.get('date_demande', '')[:10] if reg.get('date_demande') else ''))
            
            statut = reg.get('statut', '')
            statut_item = QTableWidgetItem(statut)
            color = statut_colors.get(statut, '#64748b')
            statut_item.setBackground(QColor(color))
            statut_item.setForeground(QColor('white'))
            self.table.setItem(i, 5, statut_item)
        
        self.lbl_total_paye.setText(f"Total payé: {total_paye:,.0f}")
        self.lbl_nb_reglements.setText(f"Règlements: {len(reglements)}")
    
    def ajouter_reglement(self):
        from .dialogs import AddReglementDialog
        dialog = AddReglementDialog(
            self.dossier_360.sinistre_id,
            self.dossier_360.reglement_controller,
            self.dossier_360.user,
            self
        )
        if dialog.exec():
            self.dossier_360.refresh()


class RecoursTab(BaseTab):
    """Onglet Recours"""
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "N° Recours", "Débiteur", "Réclamé", "Accepté", "Encaissé", "Solde", "Statut"
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
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        
        self.btn_ajouter = QPushButton("➕ Nouveau recours")
        self.btn_ajouter.setStyleSheet("""
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
        self.btn_ajouter.clicked.connect(self.ajouter_recours)
        btn_layout.addWidget(self.btn_ajouter)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def update_data(self, data):
        recours = data.get('recours', [])
        self.table.setRowCount(len(recours))
        
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
            self.table.setItem(i, 0, QTableWidgetItem(rec.get('numero_recours', '')))
            self.table.setItem(i, 1, QTableWidgetItem(rec.get('debiteur_nom', '')))
            self.table.setItem(i, 2, QTableWidgetItem(f"{rec.get('montant_reclame', 0):,.0f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{rec.get('montant_accepte', 0):,.0f}" if rec.get('montant_accepte') else '-'))
            self.table.setItem(i, 4, QTableWidgetItem(f"{rec.get('montant_encaisse', 0):,.0f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{rec.get('solde', 0):,.0f}"))
            
            statut = rec.get('statut', '')
            statut_item = QTableWidgetItem(statut)
            color = statut_colors.get(statut, '#64748b')
            statut_item.setBackground(QColor(color))
            statut_item.setForeground(QColor('white'))
            self.table.setItem(i, 6, statut_item)
    
    def ajouter_recours(self):
        from .dialogs import AddRecoursDialog
        dialog = AddRecoursDialog(
            self.dossier_360.sinistre_id,
            self.dossier_360.recours_controller,
            self.dossier_360.user,
            self
        )
        if dialog.exec():
            self.dossier_360.refresh()


class DocumentsTab(BaseTab):
    """Onglet Documents"""
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Nom", "Type", "Date", "Taille"
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
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        
        self.btn_ajouter = QPushButton("📤 Ajouter un document")
        self.btn_ajouter.setStyleSheet("""
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
        self.btn_ajouter.clicked.connect(self.ajouter_document)
        btn_layout.addWidget(self.btn_ajouter)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def update_data(self, data):
        # TODO: Charger les documents depuis la GED
        self.table.setRowCount(0)
    
    def ajouter_document(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un document",
            "",
            "Tous les fichiers (*.*)"
        )
        if file_path:
            QMessageBox.information(self, "Succès", f"Document ajouté: {file_path.split('/')[-1]}")
            # TODO: Enregistrer le document dans la GED


class HistoriqueTab(BaseTab):
    """Onglet Historique"""
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Date", "Utilisateur", "Action", "Entité", "Champ", "Ancienne → Nouvelle"
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
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_rafraichir = QPushButton("🔄 Rafraîchir")
        self.btn_rafraichir.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
        self.btn_rafraichir.clicked.connect(self.on_rafraichir)
        btn_layout.addWidget(self.btn_rafraichir)
        
        layout.addLayout(btn_layout)
    
    def update_data(self, data):
        historique = data.get('historique', [])
        self.table.setRowCount(len(historique))
        
        for i, h in enumerate(historique):
            self.table.setItem(i, 0, QTableWidgetItem(h.get('date_action', '')[:19] if h.get('date_action') else ''))
            self.table.setItem(i, 1, QTableWidgetItem(h.get('utilisateur_nom', '')))
            self.table.setItem(i, 2, QTableWidgetItem(h.get('action', '')))
            self.table.setItem(i, 3, QTableWidgetItem(h.get('entite', '')))
            self.table.setItem(i, 4, QTableWidgetItem(h.get('champ_modifie', '')))
            
            ancien = h.get('ancienne_valeur', '') or ''
            nouveau = h.get('nouvelle_valeur', '') or ''
            self.table.setItem(i, 5, QTableWidgetItem(f"{ancien} → {nouveau}"))
    
    def on_rafraichir(self):
        self.dossier_360.refresh()