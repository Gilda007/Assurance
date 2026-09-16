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

from addons.sinistres.views.widgets.tabs.client_tab import ClientTab
from addons.sinistres.views.widgets.tabs.tiers_tab import TiersTab as NewTiersTab
from addons.sinistres.views.widgets.damage_widgets import KpiDamageCard, DamageRow



# ============================================================
# CLASSE UTILITAIRE : CARTE AVEC BANDEAU
# ============================================================

class Card(QFrame):
    """Carte avec bandeau de titre bleu et zone de contenu"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame#Card {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        self.setObjectName("Card")
        
        # Layout principal
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # Bandeau titre
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #2c5282;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom: none;
            }
        """)
        header.setFixedHeight(38)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 0, 18, 0)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        self._main_layout.addWidget(header)
        
        # Zone de contenu
        self._content_widget = QWidget()
        self._content_widget.setStyleSheet("background-color: transparent;")
        
        self.content_layout = QVBoxLayout(self._content_widget)
        self.content_layout.setContentsMargins(18, 15, 18, 15)
        self.content_layout.setSpacing(12)
        
        self._main_layout.addWidget(self._content_widget, 1)
    
    def add_widget(self, widget: QWidget):
        """Ajoute un widget dans la zone de contenu"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Ajoute un layout dans la zone de contenu"""
        self.content_layout.addLayout(layout)
    
    def content(self) -> QVBoxLayout:
        """Retourne le layout de contenu (pour usage avancé)"""
        return self.content_layout



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
        self.tab_tiers = NewTiersTab(self)
        self.tab_expertises = ExpertisesTab(self)
        self.tab_dommages = DommagesTab(self)
        self.tab_evaluations = EvaluationsTab(self)
        self.tab_reglements = ReglementsTab(self)
        self.tab_recours = RecoursTab(self)
        self.tab_documents = DocumentsTab(self)
        self.tab_historique = HistoriqueTab(self)
        
        self.tabs.addTab(self.tab_general, "📋 Général")
        self.tabs.addTab(self.tab_client, "👤 Client")
        self.tabs.addTab(self.tab_tiers, "👥 Tiers")
        self.tabs.addTab(self.tab_expertises, "🔬 Expertises")
        self.tabs.addTab(self.tab_dommages, "💥 Dommages")
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

        # self.toolbar.addStretch()
        
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
    """Onglet Général - Style fiche dossier"""
    
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 15, 20, 15)
        root.setSpacing(15)
        
        # ============================================================
        # Ligne principale : 2 colonnes
        # ============================================================
        main_row = QHBoxLayout()
        main_row.setSpacing(15)
        
        # --- Colonne gauche (60%) ---
        left_col = QVBoxLayout()
        left_col.setSpacing(15)
        left_col.addWidget(self._build_card_infos())
        left_col.addWidget(self._build_card_dates())
        left_col.addStretch()
        
        left_widget = QWidget()
        left_widget.setLayout(left_col)
        main_row.addWidget(left_widget, 3)
        
        # --- Colonne droite (40%) ---
        right_col = QVBoxLayout()
        right_col.setSpacing(15)
        right_col.addWidget(self._build_card_description())
        right_col.addWidget(self._build_card_historique_docs())
        
        # Bouton "Modifier les informations"
        btn_modifier = QPushButton("✏️  Modifier les informations")
        btn_modifier.setStyleSheet("""
            QPushButton {
                background-color: #2c5282;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1e3a5f;
            }
        """)
        btn_modifier.setCursor(Qt.PointingHandCursor)
        btn_modifier.clicked.connect(self.on_modifier)
        right_col.addWidget(btn_modifier)
        right_col.addStretch()
        
        right_widget = QWidget()
        right_widget.setLayout(right_col)
        main_row.addWidget(right_widget, 2)
        
        root.addLayout(main_row)
    
    # ============================================================
    # CARTE : INFORMATIONS GÉNÉRALES
    # ============================================================
    
    def _build_card_infos(self) -> Card:
        card = Card("Informations Générales")
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Ligne 1
        self.tile_claim = self._make_tile("📄", "Claim#", "-")
        self.tile_statut = self._make_tile("ℹ️", "Statut", "-", badge=True)
        self.tile_branche1 = self._make_tile("🚗", "Branch", "-")
        grid.addWidget(self.tile_claim, 0, 0)
        grid.addWidget(self.tile_statut, 0, 1)
        grid.addWidget(self.tile_branche1, 0, 2)
        
        # Ligne 2
        self.tile_branche2 = self._make_tile("👥", "Branch", "-")
        self.tile_categorie = self._make_tile("📋", "Catégorie", "-")
        self.tile_survenance = self._make_tile("📅", "Date survenance", "-")
        grid.addWidget(self.tile_branche2, 1, 0)
        grid.addWidget(self.tile_categorie, 1, 1)
        grid.addWidget(self.tile_survenance, 1, 2)
        
        # Ligne 3
        self.tile_liability = self._make_tile("⚖️", "Liability", "-")
        self.tile_circonstance = self._make_tile("🔆", "Circonstance", "-")
        grid.addWidget(self.tile_liability, 2, 0)
        grid.addWidget(self.tile_circonstance, 2, 1)
        
        card.add_layout(grid)
        return card
    
    def _make_tile(self, icon: str, label: str, value: str, badge: bool = False) -> QFrame:
        """Crée une tuile d'information"""
        tile = QFrame()
        tile.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        tile.setMinimumHeight(72)
        
        h = QHBoxLayout(tile)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(10)
        
        # Icône
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 20px;")
        lbl_icon.setFixedWidth(28)
        lbl_icon.setAlignment(Qt.AlignCenter)
        h.addWidget(lbl_icon)
        
        # Contenu (label + valeur)
        v = QVBoxLayout()
        v.setSpacing(2)
        
        lbl_label = QLabel(label)
        lbl_label.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 600;")
        v.addWidget(lbl_label)
        
        lbl_value = QLabel(str(value))
        if badge:
            lbl_value.setStyleSheet("""
                background-color: #dcfce7;
                color: #166534;
                padding: 2px 10px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            """)
            lbl_value.setMaximumWidth(100)
            lbl_value.setAlignment(Qt.AlignCenter)
        else:
            lbl_value.setStyleSheet("color: #1e293b; font-size: 13px; font-weight: bold;")
        v.addWidget(lbl_value)
        
        h.addLayout(v, 1)
        
        # Références pour mise à jour
        tile.value_label = lbl_value
        
        return tile
    
    # ============================================================
    # CARTE : DATES (timeline verticale)
    # ============================================================
    
    # def _build_card_dates(self) -> Card:
    #     card = Card("Dates")
        
    #     # Conteneur de la timeline
    #     self.timeline_widget = QWidget()
    #     self.timeline_layout = QVBoxLayout(self.timeline_widget)
    #     self.timeline_layout.setContentsMargins(30, 10, 30, 10)
    #     self.timeline_layout.setSpacing(0)
        
    #     card.add_widget(self.timeline_widget)
    #     return card

    def _build_card_dates(self) -> Card:
        card = Card("Historique du dossier")
        
        # En-tête avec sélecteur de mode
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        
        self.btn_mode_dates = QPushButton("📅 Dates clés")
        self.btn_mode_statuts = QPushButton("🔄 Statuts")
        
        for btn, mode in [(self.btn_mode_dates, "dates"), (self.btn_mode_statuts, "statuts")]:
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 4px 12px;
                    font-size: 11px;
                    color: #64748b;
                }
                QPushButton:checked {
                    background-color: #e8f0fe;
                    border-color: #1a73e8;
                    color: #1a73e8;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f1f5f9;
                }
            """)
            btn.clicked.connect(lambda checked=False, m=mode: self._switch_timeline_mode(m))
            header_row.addWidget(btn)
        
        self.btn_mode_dates.setChecked(True)
        header_row.addStretch()
        
        card.add_layout(header_row)
        
        # Conteneur timeline
        self.timeline_widget = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_widget)
        self.timeline_layout.setContentsMargins(30, 10, 30, 10)
        self.timeline_layout.setSpacing(0)
        
        card.add_widget(self.timeline_widget)
        
        # Mode actuel
        self._timeline_mode = "dates"
        
        return card

    def _switch_timeline_mode(self, mode: str):
        """Change entre mode dates et mode statuts"""
        self._timeline_mode = mode
        self.btn_mode_dates.setChecked(mode == "dates")
        self.btn_mode_statuts.setChecked(mode == "statuts")
        # Redessiner
        if hasattr(self, '_last_data') and self._last_data:
            self._render_dates_or_statuts(self._last_data)

    def _render_dates_or_statuts(self, data):
        """Affiche soit les dates clés, soit l'historique des statuts"""
        
        # Récupérer l'historique
        historique = self._charger_historique_statuts()
        
        # Filtrer les changements de statut
        changements = [h for h in historique if h.get('action') in (
            'CHANGEMENT_STATUT', 'CREATION', 'REOUVERTURE'
        )]
        
        if self._timeline_mode == "statuts" and changements:
            self._render_timeline_statuts(changements)
        else:
            self._render_timeline_dates(data)

    def _charger_historique_statuts(self) -> list:
        """Charge l'historique depuis le contrôleur"""
        try:
            sinistre_id = self.dossier_360.sinistre_id
            controller = self.dossier_360.sinistre_controller
            historique = controller.get_historique_sinistre(sinistre_id) or []
            return historique
        except Exception as e:
            print(f"Erreur chargement historique: {e}")
            return []


    def _render_timeline_dates(self, data):
        """Timeline des dates clés (mode actuel)"""
        dates = [
            ("Date de survenance", self._format_date(data.get('date_survenance')), True),
            ("Date de déclaration", self._format_date(data.get('date_declaration')), True),
            ("Date d'ouverture", self._format_date(data.get('date_ouverture')), True),
            ("Date de clôture",
            self._format_date(data.get('date_cloture')) if data.get('date_cloture') else "(en cours)",
            bool(data.get('date_cloture'))),
        ]
        self._render_timeline(dates)


    def _render_timeline_statuts(self, changements: list):
        """Timeline des changements de statut"""
        self._clear_timeline()
        
        # Couleurs par statut
        statut_colors = {
            'OUVERT': '#f59e0b',
            'EN_INSTRUCTION': '#3b82f6',
            'EN_EXPERTISE': '#8b5cf6',
            'EN_EVALUATION': '#ec4899',
            'VALIDE': '#06b6d4',
            'EN_REGLEMENT': '#f97316',
            'EN_RECOURS': '#ef4444',
            'CLOTURE': '#22c55e',
            'REOUVERT': '#f59e0b',
        }
        
        # Trier du plus récent au plus ancien (ou l'inverse)
        changements_tries = sorted(
            changements,
            key=lambda h: h.get('date_action', ''),
            reverse=False  # du plus ancien au plus récent
        )
        
        for i, h in enumerate(changements_tries):
            action = h.get('action', '')
            date_str = h.get('date_action', '')
            utilisateur = h.get('utilisateur_nom', '')
            ancien = h.get('ancienne_valeur', '') or ''
            nouveau = h.get('nouvelle_valeur', '') or ''
            commentaire = h.get('commentaire', '') or ''
            
            # Formater la date
            date_display = self._format_datetime(date_str)
            
            # Ligne
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(15)
            
            # Pastille
            dot = QLabel("●")
            dot.setStyleSheet(f"""
                color: {statut_colors.get(nouveau, '#1a73e8')};
                font-size: 16px;
            """)
            dot.setFixedWidth(20)
            dot.setAlignment(Qt.AlignCenter)
            row.addWidget(dot)
            
            # Contenu (date + transition + utilisateur)
            content = QVBoxLayout()
            content.setSpacing(2)
            
            # Ligne 1 : date + ancien → nouveau
            line1 = QHBoxLayout()
            line1.setSpacing(8)
            
            lbl_date = QLabel(date_display)
            lbl_date.setStyleSheet("color: #64748b; font-size: 10px;")
            line1.addWidget(lbl_date)
            
            if ancien and nouveau:
                transition = QLabel(f"{ancien} → {nouveau}")
                transition.setStyleSheet(f"""
                    color: {statut_colors.get(nouveau, '#1e293b')};
                    font-size: 12px;
                    font-weight: bold;
                """)
                line1.addWidget(transition)
            elif nouveau:
                transition = QLabel(nouveau)
                transition.setStyleSheet(f"""
                    color: {statut_colors.get(nouveau, '#1e293b')};
                    font-size: 12px;
                    font-weight: bold;
                """)
                line1.addWidget(transition)
            
            line1.addStretch()
            content.addLayout(line1)
            
            # Ligne 2 : utilisateur + commentaire
            if utilisateur or commentaire:
                details = []
                if utilisateur:
                    details.append(f"👤 {utilisateur}")
                if commentaire:
                    details.append(f"💬 {commentaire}")
                
                lbl_details = QLabel("  •  ".join(details))
                lbl_details.setStyleSheet("color: #94a3b8; font-size: 10px; font-style: italic;")
                lbl_details.setWordWrap(True)
                content.addWidget(lbl_details)
            
            row.addLayout(content, 1)
            self.timeline_layout.addWidget(row_widget)
            
            # Ligne de connexion
            if i < len(changements_tries) - 1:
                line_widget = QWidget()
                line_row = QHBoxLayout(line_widget)
                line_row.setContentsMargins(10, 0, 0, 0)
                line_row.setSpacing(0)
                
                line = QFrame()
                line.setFixedWidth(2)
                line.setFixedHeight(25)
                line.setStyleSheet("background-color: #cbd5e1;")
                line_row.addWidget(line)
                line_row.addStretch()
                
                self.timeline_layout.addWidget(line_widget)


    def _clear_timeline(self):
        """Vide la timeline"""
        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())


    def _format_datetime(self, dt_str) -> str:
        """Formate une datetime ISO en '14 sept. 2026 14:30'"""
        if not dt_str:
            return "-"
        try:
            s = str(dt_str).replace('T', ' ')[:16]
            from datetime import datetime
            dt = datetime.strptime(s, "%Y-%m-%d %H:%M")
            mois = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin',
                    'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
            return f"{dt.day} {mois[dt.month - 1]} {dt.year} {dt.hour:02d}:{dt.minute:02d}"
        except Exception:
            return str(dt_str)[:16]

    def _render_timeline(self, dates: list):
        """dates = [(label, valeur, is_active), ...]"""
        # Vider
        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        
        for i, (label, value, active) in enumerate(dates):
            # ----- Ligne : pastille + label/valeur -----
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(15)
            
            # Pastille
            dot = QLabel("●" if active else "○")
            dot.setStyleSheet(f"""
                color: {'#1a73e8' if active else '#94a3b8'};
                font-size: 16px;
            """)
            dot.setFixedWidth(20)
            dot.setAlignment(Qt.AlignCenter)
            row.addWidget(dot)
            
            # Label + valeur (alignés à droite)
            info = QVBoxLayout()
            info.setSpacing(0)
            
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet("color: #64748b; font-size: 11px;")
            lbl.setAlignment(Qt.AlignRight)
            info.addWidget(lbl)
            
            val = QLabel(value)
            val.setStyleSheet(f"""
                color: {'#1e293b' if active else '#94a3b8'};
                font-size: 13px;
                font-weight: bold;
            """)
            val.setAlignment(Qt.AlignRight)
            info.addWidget(val)
            
            row.addLayout(info, 1)
            
            self.timeline_layout.addWidget(row_widget)
            
            # ----- Ligne de connexion verticale (sauf dernier) -----
            if i < len(dates) - 1:
                line_widget = QWidget()
                line_row = QHBoxLayout(line_widget)
                line_row.setContentsMargins(10, 0, 0, 0)
                line_row.setSpacing(0)
                
                line = QFrame()
                line.setFixedWidth(2)
                line.setFixedHeight(25)
                line.setStyleSheet("background-color: #cbd5e1;")
                line_row.addWidget(line)
                line_row.addStretch()
                
                self.timeline_layout.addWidget(line_widget)
    
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
    
    # ============================================================
    # CARTE : DESCRIPTION
    # ============================================================
    
    def _build_card_description(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        card.setMinimumHeight(280)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # En-tête
        header = QHBoxLayout()
        title = QLabel("▾  Description")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        # Barre d'outils
        toolbar = QHBoxLayout()
        toolbar.setSpacing(4)
        for label in ["B", "I", "U", "≡", "≣", "🔗", "⋯"]:
            btn = QPushButton(label)
            btn.setFixedSize(24, 24)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    color: #64748b;
                }
                QPushButton:hover {
                    background-color: #f1f5f9;
                }
            """)
            toolbar.addWidget(btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Zone de texte
        self.txt_description = QTextEdit()
        self.txt_description.setPlaceholderText("Description du sinistre...")
        self.txt_description.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                color: #1e293b;
            }
            QTextEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        layout.addWidget(self.txt_description, 1)
        
        # Bouton Sauvegarder
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        self.btn_save_desc = QPushButton("Sauvegarder")
        self.btn_save_desc.setStyleSheet("""
            QPushButton {
                background-color: #2c5282;
                color: white;
                padding: 6px 18px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #1e3a5f;
            }
        """)
        self.btn_save_desc.setCursor(Qt.PointingHandCursor)
        self.btn_save_desc.clicked.connect(self._sauvegarder_description)
        btn_row.addWidget(self.btn_save_desc)
        layout.addLayout(btn_row)
        
        return card
    
    def _sauvegarder_description(self):
        try:
            nouvelle_desc = self.txt_description.toPlainText().strip()
            result = self.dossier_360.sinistre_controller.update_sinistre(
                self.dossier_360.sinistre_id,
                {'description': nouvelle_desc}
            )
            if result:
                QMessageBox.information(self, "Succès", "Description mise à jour")
                self.dossier_360.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    # ============================================================
    # CARTE : HISTORIQUE + DOCUMENTS
    # ============================================================
    
    def _build_card_historique_docs(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        card.setMinimumHeight(200)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)
        
        # Onglets
        tabs = QHBoxLayout()
        tabs.setSpacing(0)
        
        btn_hist = QPushButton("🕐  Historique")
        btn_hist.setCheckable(True)
        btn_hist.setChecked(True)
        
        btn_doc = QPushButton("📄  Documents  ▾")
        btn_doc.setCheckable(True)
        
        for btn in [btn_hist, btn_doc]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-bottom: 2px solid transparent;
                    padding: 8px 14px;
                    font-size: 11px;
                    color: #64748b;
                    font-weight: 600;
                }
                QPushButton:checked {
                    color: #1a73e8;
                    border-bottom: 2px solid #1a73e8;
                }
                QPushButton:hover {
                    background-color: #f8fafc;
                }
            """)
            tabs.addWidget(btn)
        tabs.addStretch()
        layout.addLayout(tabs)
        
        # Aperçu
        preview = QFrame()
        preview.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        preview.setMinimumHeight(120)
        
        p_layout = QHBoxLayout(preview)
        p_layout.setContentsMargins(10, 10, 10, 10)
        p_layout.setSpacing(10)
        
        # Page
        page = QLabel("📄")
        page.setFixedSize(70, 90)
        page.setStyleSheet("""
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            font-size: 36px;
        """)
        page.setAlignment(Qt.AlignCenter)
        p_layout.addWidget(page)
        
        # Liste
        docs = QVBoxLayout()
        docs.setSpacing(4)
        
        for icon, name in [("📕", "Rapport expert.pdf"), ("🖼️", "Photo_1.png")]:
            row = QHBoxLayout()
            row.setSpacing(6)
            i = QLabel(icon)
            i.setStyleSheet("font-size: 14px;")
            row.addWidget(i)
            n = QLabel(name)
            n.setStyleSheet("font-size: 11px; color: #1e293b;")
            row.addWidget(n, 1)
            docs.addLayout(row)
        
        total = QLabel("14 documents total")
        total.setStyleSheet("color: #64748b; font-size: 10px; font-style: italic;")
        docs.addWidget(total)
        docs.addStretch()
        
        p_layout.addLayout(docs, 1)
        layout.addWidget(preview)
        
        return card
    
    # ============================================================
    # MISE À JOUR DES DONNÉES
    # ============================================================
    
    def update_data(self, data):
        try:
            # --- Tuiles ---
            self._last_data = data
            self.tile_claim.value_label.setText(data.get('numero_sinistre', '-'))
            
            statut = data.get('statut', 'INCONNU')
            self.tile_statut.value_label.setText(statut)
            statut_colors = {
                'OUVERT': ('#dcfce7', '#166534'),
                'EN_INSTRUCTION': ('#dbeafe', '#1e40af'),
                'EN_EXPERTISE': ('#ede9fe', '#5b21b6'),
                'EN_EVALUATION': ('#fce7f3', '#9d174d'),
                'VALIDE': ('#cffafe', '#155e75'),
                'EN_REGLEMENT': ('#ffedd5', '#9a3412'),
                'EN_RECOURS': ('#fee2e2', '#991b1b'),
                'CLOTURE': ('#dcfce7', '#166534'),
                'REOUVERT': ('#fef3c7', '#92400e'),
            }
            bg, fg = statut_colors.get(statut, ('#f1f5f9', '#64748b'))
            self.tile_statut.value_label.setStyleSheet(f"""
                background-color: {bg};
                color: {fg};
                padding: 2px 10px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            """)
            
            self.tile_branche1.value_label.setText(data.get('branche', '-'))
            self.tile_branche2.value_label.setText(data.get('branche', '-'))
            self.tile_categorie.value_label.setText(data.get('categorie', '-'))
            
            date_surv = data.get('date_survenance', '')
            self.tile_survenance.value_label.setText(
                self._format_date(date_surv) if date_surv else '-'
            )
            
            taux = data.get('taux_responsabilite', 0) or 0
            self.tile_liability.value_label.setText(f"{taux * 100:.0f}%")
            
            self.tile_circonstance.value_label.setText(
                data.get('circonstance_principale', '-')
            )
            
            # --- Timeline ---
            dates = [
                ("Date de survenance", self._format_date(data.get('date_survenance')), True),
                ("Date de déclaration", self._format_date(data.get('date_declaration')), True),
                ("Date d'ouverture", self._format_date(data.get('date_ouverture')), True),
                ("Date de clôture",
                 self._format_date(data.get('date_cloture')) if data.get('date_cloture') else "(en cours)",
                 bool(data.get('date_cloture'))),
            ]
            self._render_dates_or_statuts(data)
            self._render_timeline(dates)
            
            # --- Description ---
            self.txt_description.setPlainText(data.get('description', '') or '')
        
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def _format_date(self, date_str) -> str:
        """Formate une date ISO en '11 sept. 2026'"""
        if not date_str:
            return "-"
        try:
            s = str(date_str)[:10]
            from datetime import datetime
            dt = datetime.strptime(s, "%Y-%m-%d")
            mois = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin',
                    'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
            return f"{dt.day} {mois[dt.month - 1]} {dt.year}"
        except Exception:
            return str(date_str)[:10]
    
    def on_modifier(self):
        self.dossier_360.edit_sinistre()


class DommagesTab(BaseTab):
    """Onglet Dommages - Style fiche avec KPI et lignes pliables"""
    
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 15, 20, 15)
        root.setSpacing(15)
        
        # ============================================================
        # LIGNE 1 : 4 cartes KPI
        # ============================================================
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        
        from addons.sinistres.views.widgets.damage_widgets import KpiDamageCard
        
        self.kpi_total_estime = KpiDamageCard(
            "Total Damages Estimated", "FCFA 0", 65, "#1a73e8"
        )
        self.kpi_accepte = KpiDamageCard(
            "Damages Accepted", "FCFA 0", 40, "#1a73e8"
        )
        self.kpi_evaluations = KpiDamageCard(
            "Evaluations Complete", "0/0", 75, "#1a73e8", suffix="evaluated"
        )
        self.kpi_tiers = KpiDamageCard(
            "Pending Third Party", "0", 0, "#1a73e8", icon="👤"
        )
        
        kpi_row.addWidget(self.kpi_total_estime)
        kpi_row.addWidget(self.kpi_accepte)
        kpi_row.addWidget(self.kpi_evaluations)
        kpi_row.addWidget(self.kpi_tiers)
        root.addLayout(kpi_row)
        
        # ============================================================
        # LIGNE 2 : Barre d'actions (Add + Filtre)
        # ============================================================
        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        
        # Bouton "Add Damage"
        self.btn_add = QPushButton("➕  Add Damage")
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #2c5282;
                color: white;
                padding: 8px 18px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1e3a5f;
            }
        """)
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self.ajouter_dommage)
        action_row.addWidget(self.btn_add)
        
        # Champ de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Filtre")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)
        self.search_input.textChanged.connect(self._filtrer_dommages)
        action_row.addWidget(self.search_input, 1)
        
        root.addLayout(action_row)
        
        # ============================================================
        # LIGNE 3 : En-tête du tableau
        # ============================================================
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        header.setFixedHeight(42)

        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(15, 0, 15, 0)
        h_layout.setSpacing(10)

        # Colonnes : (label, largeur, alignement)
        colonnes = [
            ("", 30, Qt.AlignLeft),              # chevron
            ("Type", 140, Qt.AlignLeft),
            ("Description", 0, Qt.AlignLeft),    # stretch
            ("Montant estimé", 110, Qt.AlignRight),
            ("Montant accepté", 110, Qt.AlignRight),
            ("Évaluation", 100, Qt.AlignCenter),
            ("Actions", 110, Qt.AlignCenter),
        ]

        for label, width, align in colonnes:
            lbl = QLabel(label)
            lbl.setStyleSheet("""
                font-size: 11px;
                font-weight: 600;
                color: #64748b;
                letter-spacing: 0.3px;
            """)
            lbl.setAlignment(align)
            if width > 0:
                lbl.setFixedWidth(width)
                h_layout.addWidget(lbl)
            else:
                h_layout.addWidget(lbl, 1)

        root.addWidget(header)
        
        # ============================================================
        # LIGNE 4 : Conteneur des dommages (scrollable)
        # ============================================================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-top: none;
                border-radius: 0 0 8px 8px;
            }
        """)
        
        self.dommages_container = QWidget()
        self.dommages_container.setStyleSheet("background-color: white;")
        self.dommages_layout = QVBoxLayout(self.dommages_container)
        self.dommages_layout.setContentsMargins(0, 0, 0, 0)
        self.dommages_layout.setSpacing(0)
        
        scroll.setWidget(self.dommages_container)
        root.addWidget(scroll, 1)
    
    # ============================================================
    # MISE À JOUR DES DONNÉES
    # ============================================================
    
    def update_data(self, data):
        """Met à jour les KPI et la liste des dommages"""
        try:
            dommages = data.get('dommages', []) or []
            
            # --- KPIs ---
            total_estime = sum(d.get('montant_estime', 0) or 0 for d in dommages)
            total_accepte = sum(d.get('montant_accepte', 0) or 0 for d in dommages)
            nb_valides = sum(1 for d in dommages if d.get('montant_accepte'))
            nb_total = len(dommages)
            
            # Pourcentage estimé vs accepté
            pct_estime = 65  # placeholder
            pct_accepte = int((total_accepte / total_estime * 100) if total_estime > 0 else 0)
            pct_eval = int((nb_valides / nb_total * 100) if nb_total > 0 else 0)
            
            self.kpi_total_estime.set_value(
                f"FCFA {total_estime:,.0f}".replace(",", " "),
                percent=100,  # le total est toujours à 100%
                donut_label=f"{pct_accepte}%"
            )
            self.kpi_accepte.set_value(
                f"FCFA {total_accepte:,.0f}".replace(",", " "),
                percent=pct_accepte,
                donut_label=f"{pct_accepte}%"
            )
            self.kpi_evaluations.set_value(
                f"{nb_valides}/{nb_total}",
                percent=pct_eval,
                donut_label=f"{pct_eval}%"
            )
            
            # Tiers en attente
            tiers_en_attente = sum(
                1 for t in (data.get('tiers', []) or [])
                if not t.get('telephone')
            )
            self.kpi_tiers.set_value(str(tiers_en_attente))
            
            # --- Liste ---
            self._render_dommages(dommages)
        
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def _render_dommages(self, dommages: list):
        """Reconstruit la liste des dommages"""
        from addons.sinistres.views.widgets.damage_widgets import DamageRow
        
        # Vider
        while self.dommages_layout.count():
            item = self.dommages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        
        if not dommages:
            empty = QLabel("Aucun dommage enregistré")
            empty.setStyleSheet("color: #94a3b8; font-size: 12px; padding: 30px;")
            empty.setAlignment(Qt.AlignCenter)
            self.dommages_layout.addWidget(empty)
            return
        
        for d in dommages:
            if not d:  # ✅ Sécurité
                continue
            row = DamageRow(d)
            row.edit_clicked.connect(self._on_edit_dommage)
            row.validate_clicked.connect(self._on_validate_dommage)
            row.reject_clicked.connect(self._on_reject_dommage)
            row.delete_clicked.connect(self._on_delete_dommage)
            row.context_menu_requested.connect(self._show_damage_context_menu)
            self.dommages_layout.addWidget(row)
        
        self.dommages_layout.addStretch()

    def _clear_layout(self, layout):
        """Nettoie récursivement un layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
    
    def _filtrer_dommages(self, text: str):
        """Filtre la liste selon le texte"""
        if not hasattr(self, '_all_dommages'):
            return
        
        text = text.strip().lower()
        if not text:
            self._render_dommages(self._all_dommages)
            return
        
        filtered = [
            d for d in self._all_dommages
            if text in (d.get('type_dommage') or '').lower()
            or text in (d.get('description') or '').lower()
            or text in (d.get('code_dommage') or '').lower()
        ]
        self._render_dommages(filtered)
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
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
    
    def _on_edit_dommage(self, dommage: dict):
        QMessageBox.information(self, "Modifier", f"Modification du dommage {dommage.get('id')}")
        # TODO: ouvrir un dialogue d'édition
    
    def _on_validate_dommage(self, dommage: dict):
        QMessageBox.information(self, "Valider", f"Validation du dommage {dommage.get('id')}")
    
    def _on_reject_dommage(self, dommage: dict):
        QMessageBox.information(self, "Rejeter", f"Rejet du dommage {dommage.get('id')}")
    
    def _on_delete_dommage(self, dommage: dict):
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Supprimer le dommage {dommage.get('type_dommage')} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Supprimer", "Suppression à implémenter")

    def _show_damage_context_menu(self, dommage: dict, global_pos):
        """Affiche le menu contextuel au clic droit sur une ligne"""
        
        # Marquer la ligne courante
        self._selected_dommage = dommage
        
        # Rafraîchir la surbrillance
        for i in range(self.dommages_layout.count()):
            item = self.dommages_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), DamageRow):
                row = item.widget()
                row.set_selected(row.dommage.get('id') == dommage.get('id'))
        
        # --- Construire le menu ---
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 13px;
                color: #1e293b;
            }
            QMenu::item:selected {
                background-color: #f1f5f9;
                color: #1a73e8;
            }
            QMenu::item:disabled {
                color: #94a3b8;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e2e8f0;
                margin: 4px 8px;
            }
        """)
        
        # --- Section 1 : Consultation ---
        action_voir = QAction("👁️  Voir les détails", self)
        action_voir.triggered.connect(lambda: self._on_voir_dommage(dommage))
        menu.addAction(action_voir)
        
        action_etendre = QAction("🔽  Étendre / Réduire", self)
        action_etendre.triggered.connect(lambda: self._toggle_row(dommage))
        menu.addAction(action_etendre)
        
        menu.addSeparator()
        
        # --- Section 2 : Modification ---
        action_modifier = QAction("✏️  Modifier", self)
        action_modifier.triggered.connect(lambda: self._on_edit_dommage(dommage))
        menu.addAction(action_modifier)
        
        action_dupliquer = QAction("📋  Dupliquer", self)
        action_dupliquer.triggered.connect(lambda: self._on_dupliquer_dommage(dommage))
        menu.addAction(action_dupliquer)
        
        menu.addSeparator()
        
        # --- Section 3 : Validation ---
        est_valide = bool(dommage.get('montant_accepte'))
        
        action_valider = QAction("✔️  Valider le montant", self)
        action_valider.setEnabled(not est_valide)
        if est_valide:
            action_valider.setToolTip("Dommage déjà validé")
        action_valider.triggered.connect(lambda: self._on_validate_dommage(dommage))
        menu.addAction(action_valider)
        
        action_rejeter = QAction("❌  Rejeter", self)
        action_rejeter.triggered.connect(lambda: self._on_reject_dommage(dommage))
        menu.addAction(action_rejeter)
        
        menu.addSeparator()
        
        # --- Section 4 : Évaluation ---
        action_evaluer = QAction("💰  Créer une évaluation", self)
        action_evaluer.triggered.connect(lambda: self._on_evaluer_dommage(dommage))
        menu.addAction(action_evaluer)
        
        menu.addSeparator()
        
        # --- Section 5 : Suppression ---
        action_supprimer = QAction("🗑️  Supprimer", self)
        action_supprimer.triggered.connect(lambda: self._on_delete_dommage(dommage))
        menu.addAction(action_supprimer)
        
        # --- Afficher ---
        menu.exec(global_pos)

    def _on_voir_dommage(self, dommage: dict):
        """Ouvre une fiche détaillée du dommage"""
        QMessageBox.information(
            self,
            f"Dommage {dommage.get('type_dommage', 'N/A')}",
            f"Description : {dommage.get('description') or '—'}\n"
            f"Montant estimé : FCFA {dommage.get('montant_estime', 0):,.0f}\n"
            f"Montant accepté : FCFA {dommage.get('montant_accepte', 0):,.0f}\n"
            f"Évaluation ID : {dommage.get('evaluation_id') or '—'}"
        )


    def _toggle_row(self, dommage: dict):
        """Étend/Réduit la ligne correspondante"""
        for i in range(self.dommages_layout.count()):
            item = self.dommages_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), DamageRow):
                row = item.widget()
                if row.dommage.get('id') == dommage.get('id'):
                    row._toggle_expand()
                    break


    def _on_dupliquer_dommage(self, dommage: dict):
        """Duplique un dommage"""
        reply = QMessageBox.question(
            self, "Dupliquer",
            f"Dupliquer le dommage '{dommage.get('type_dommage')}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # TODO: appeler le contrôleur
            QMessageBox.information(self, "Dupliquer", "Fonctionnalité à implémenter")


    def _on_evaluer_dommage(self, dommage: dict):
        """Crée une évaluation pour ce dommage"""
        from .dialogs import AddEvaluationDialog
        dialog = AddEvaluationDialog(
            self.dossier_360.sinistre_id,
            self.dossier_360.evaluation_controller,
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
        from addons.sinistres.views.mission_dialog import MissionDialog
        dialog = MissionDialog(
            self.dossier_360.expertise_controller,
            self.dossier_360.sinistre_id,
            self.dossier_360.user,
        )
        if dialog.exec():
            self.dossier_360.refresh()


class EvaluationsTab(BaseTab):
    """Onglet Évaluations - Style fiche avec KPI et filtres par colonne"""
    
    def setup_ui(self):
        from PySide6.QtWidgets import QCheckBox
        from addons.sinistres.views.widgets.evaluation_widgets import (
            KpiEvaluationCard, FloatingAddButton
        )
        
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 15, 20, 15)
        root.setSpacing(15)
        
        # ============================================================
        # LIGNE 1 : 4 KPI + bouton flottant
        # ============================================================
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        
        self.kpi_total = KpiEvaluationCard(
            "Total Évalué Net", "0 €", 0, "0%", "Brut : 0 €"
        )
        self.kpi_expertises = KpiEvaluationCard(
            "Expertises Actives", "0", 0, "0/0"
        )
        self.kpi_taux = KpiEvaluationCard(
            "Taux de Validation", "0%", 0, "0%",
            "0 en attente, 0 validée"
        )
        self.kpi_temps = KpiEvaluationCard(
            "Temps Moyen", "0 jours", 0, "0/10 jours"
        )
        
        kpi_row.addWidget(self.kpi_total)
        kpi_row.addWidget(self.kpi_expertises)
        kpi_row.addWidget(self.kpi_taux)
        kpi_row.addWidget(self.kpi_temps)
        
        # Bouton flottant
        self.btn_floating_add = FloatingAddButton()
        self.btn_floating_add.clicked.connect(self.ajouter_evaluation)
        kpi_row.addWidget(self.btn_floating_add)
        
        root.addLayout(kpi_row)
        
        # ============================================================
        # LIGNE 2 : Tableau avec filtres par colonne
        # ============================================================
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        
        # --- En-tête du tableau ---
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        header.setFixedHeight(42)
        
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(15, 0, 15, 0)
        h_layout.setSpacing(8)
        
        colonnes = [
            ("N° Évaluation", 130),
            ("Date", 110),
            ("Type", 130),
            ("Expert Assigné", 130),
            ("Montant Brut", 110),
            ("Franchise", 100),
            ("Montant Net", 110),
            ("Statut", 110),
            ("Validée", 80),
        ]
        
        for label, width in colonnes:
            lbl = QLabel(label)
            lbl.setStyleSheet("""
                font-size: 11px;
                font-weight: 600;
                color: #1e293b;
            """)
            if width > 0:
                lbl.setFixedWidth(width)
                h_layout.addWidget(lbl)
        
        table_layout.addWidget(header)
        
        # --- Ligne de filtres ---
        filters = QFrame()
        filters.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        filters.setFixedHeight(50)
        
        f_layout = QHBoxLayout(filters)
        f_layout.setContentsMargins(15, 8, 15, 8)
        f_layout.setSpacing(8)
        
        # Filtre N° (combo)
        self.filter_numero = QComboBox()
        self.filter_numero.addItem("Tous", None)
        self.filter_numero.setFixedWidth(130)
        self.filter_numero.setStyleSheet(self._filter_style())
        self.filter_numero.currentIndexChanged.connect(self._apply_filters)
        f_layout.addWidget(self.filter_numero)
        
        # Filtre Date (QDateEdit avec icône)
        self.filter_date = QDateEdit()
        self.filter_date.setCalendarPopup(True)
        self.filter_date.setDisplayFormat("")
        self.filter_date.setSpecialValueText("📅")
        self.filter_date.setDate(QDate(2000, 1, 1))
        self.filter_date.setFixedWidth(110)
        self.filter_date.setStyleSheet(self._filter_style())
        self.filter_date.dateChanged.connect(self._apply_filters)
        f_layout.addWidget(self.filter_date)
        
        # Filtre Type (combo)
        self.filter_type = QComboBox()
        self.filter_type.addItem("Tous", None)
        for t in ["Carrosserie", "Électricité", "Mécanique", "Peinture", "Vitrage"]:
            self.filter_type.addItem(t, t)
        self.filter_type.setFixedWidth(130)
        self.filter_type.setStyleSheet(self._filter_style())
        self.filter_type.currentIndexChanged.connect(self._apply_filters)
        f_layout.addWidget(self.filter_type)
        
        # Filtre Expert (combo)
        self.filter_expert = QComboBox()
        self.filter_expert.addItem("Tous", None)
        self.filter_expert.setFixedWidth(130)
        self.filter_expert.setStyleSheet(self._filter_style())
        self.filter_expert.currentIndexChanged.connect(self._apply_filters)
        f_layout.addWidget(self.filter_expert)
        
        # Filtre Montant min
        from PySide6.QtWidgets import QLineEdit
        self.filter_brut = QLineEdit()
        self.filter_brut.setPlaceholderText("Min")
        self.filter_brut.setFixedWidth(110)
        self.filter_brut.setStyleSheet(self._filter_style())
        self.filter_brut.textChanged.connect(self._apply_filters)
        f_layout.addWidget(self.filter_brut)
        
        # Filtre Franchise
        self.filter_franchise = QLineEdit()
        self.filter_franchise.setPlaceholderText("Min")
        self.filter_franchise.setFixedWidth(100)
        self.filter_franchise.setStyleSheet(self._filter_style())
        self.filter_franchise.textChanged.connect(self._apply_filters)
        f_layout.addWidget(self.filter_franchise)
        
        # Filtre Net
        self.filter_net = QLineEdit()
        self.filter_net.setPlaceholderText("Min")
        self.filter_net.setFixedWidth(110)
        self.filter_net.setStyleSheet(self._filter_style())
        self.filter_net.textChanged.connect(self._apply_filters)
        f_layout.addWidget(self.filter_net)
        
        # Filtre Statut
        self.filter_statut = QComboBox()
        self.filter_statut.addItem("Tous", None)
        self.filter_statut.addItem("Brouillon", "BROUILLON")
        self.filter_statut.addItem("À valider", "A_VALIDER")
        self.filter_statut.addItem("Validée", "VALIDEE")
        self.filter_statut.setFixedWidth(110)
        self.filter_statut.setStyleSheet(self._filter_style())
        self.filter_statut.currentIndexChanged.connect(self._apply_filters)
        f_layout.addWidget(self.filter_statut)
        
        # Filtre Validée (checkbox)
        self.filter_validee = QCheckBox()
        self.filter_validee.setFixedWidth(80)
        self.filter_validee.stateChanged.connect(self._apply_filters)
        f_layout.addWidget(self.filter_validee)
        
        table_layout.addWidget(filters)
        
        # --- Corps du tableau (scrollable) ---
        from PySide6.QtWidgets import QScrollArea
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: none;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        self.table_container = QWidget()
        self.table_container.setStyleSheet("background-color: white;")
        self.table_layout = QVBoxLayout(self.table_container)
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        self.table_layout.setSpacing(0)
        
        scroll.setWidget(self.table_container)
        table_layout.addWidget(scroll, 1)
        
        root.addWidget(table_container, 1)
        
        # Stockage
        self._all_evaluations = []
    
    def _filter_style(self) -> str:
        return """
            QComboBox, QLineEdit, QDateEdit {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 11px;
                color: #1e293b;
            }
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus {
                border: 1px solid #1a73e8;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """
    
    # ============================================================
    # MISE À JOUR DES DONNÉES
    # ============================================================
    
    def update_data(self, data):
        try:
            evaluations = data.get('evaluations', []) or []
            self._all_evaluations = evaluations
            
            # --- KPI ---
            self._update_kpis(evaluations, data)
            
            # --- Remplir les filtres ---
            self._populate_filters(evaluations)
            
            # --- Tableau ---
            self._render_table(evaluations)
        
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def _update_kpis(self, evaluations: list, data: dict):
        """Met à jour les 4 cartes KPI"""
        # Total évalué net
        total_net = sum(ev.get('montant_net', 0) or 0 for ev in evaluations)
        total_brut = sum(ev.get('montant_brut', 0) or 0 for ev in evaluations)
        self.kpi_total.set_value(
            f"{total_net:,.0f} €".replace(",", " "),
            0, "0%"
        )
        self.kpi_total.set_footer(f"Brut : {total_brut:,.0f} €".replace(",", " "))
        
        # Expertises actives
        nb_total = len(evaluations)
        nb_validees = sum(1 for ev in evaluations if ev.get('est_validee'))
        self.kpi_expertises.set_value(
            str(nb_total),
            0, f"{nb_validees}/{nb_total}"
        )
        
        # Taux de validation
        taux = int(nb_validees / nb_total * 100) if nb_total > 0 else 0
        nb_attente = nb_total - nb_validees
        self.kpi_taux.set_value(
            f"{taux}%",
            taux, f"{taux}%"
        )
        self.kpi_taux.set_footer(f"{nb_attente} en attente, {nb_validees} validée(s)")
        
        # Temps moyen (placeholder)
        self.kpi_temps.set_value(
            "0 jours",
            0, "0/10 jours"
        )
    
    def _populate_filters(self, evaluations: list):
        """Remplit les combos de filtre avec les valeurs disponibles"""
        # Experts
        self.filter_expert.blockSignals(True)
        current = self.filter_expert.currentData()
        self.filter_expert.clear()
        self.filter_expert.addItem("Tous", None)
        experts = set(ev.get('expert_nom') for ev in evaluations if ev.get('expert_nom'))
        for e in sorted(experts):
            self.filter_expert.addItem(e, e)
        # Restaurer
        for i in range(self.filter_expert.count()):
            if self.filter_expert.itemData(i) == current:
                self.filter_expert.setCurrentIndex(i)
                break
        self.filter_expert.blockSignals(False)
    
    # ============================================================
    # RENDU DU TABLEAU
    # ============================================================
    
    def _render_table(self, evaluations: list):
        """Construit les lignes du tableau"""
        from addons.sinistres.views.widgets.evaluation_widgets import EvaluationRow
        
        # Vider
        while self.table_layout.count():
            item = self.table_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not evaluations:
            empty = QLabel("Aucune évaluation")
            empty.setStyleSheet("color: #94a3b8; font-size: 12px; padding: 30px;")
            empty.setAlignment(Qt.AlignCenter)
            self.table_layout.addWidget(empty)
            return
        
        for ev in evaluations:
            row = EvaluationRow(ev)
            row.edit_requested.connect(self._on_edit)
            row.validate_requested.connect(self._on_validate)
            row.delete_requested.connect(self._on_delete)
            row.context_menu_requested.connect(self._show_context_menu)
            self.table_layout.addWidget(row)
        
        self.table_layout.addStretch()
    
    # ============================================================
    # FILTRES
    # ============================================================
    
    def _apply_filters(self):
        """Applique tous les filtres"""
        filtered = list(self._all_evaluations)
        
        # N° évaluation
        num = self.filter_numero.currentData()
        if num:
            filtered = [e for e in filtered if e.get('numero_evaluation') == num]
        
        # Type
        type_f = self.filter_type.currentData()
        if type_f:
            filtered = [e for e in filtered if e.get('type_evaluation') == type_f]
        
        # Expert
        expert_f = self.filter_expert.currentData()
        if expert_f:
            filtered = [e for e in filtered if e.get('expert_nom') == expert_f]
        
        # Statut
        statut_f = self.filter_statut.currentData()
        if statut_f:
            filtered = [e for e in filtered if self._get_statut(e) == statut_f]
        
        # Validée
        if self.filter_validee.isChecked():
            filtered = [e for e in filtered if e.get('est_validee')]
        
        # Montants minimum
        for attr, widget in [
            ('montant_brut', self.filter_brut),
            ('franchise', self.filter_franchise),
            ('montant_net', self.filter_net),
        ]:
            text = widget.text().strip()
            if text:
                try:
                    mini = float(text)
                    filtered = [e for e in filtered if (e.get(attr) or 0) >= mini]
                except ValueError:
                    pass
        
        self._render_table(filtered)
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
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
    
    def _on_edit(self, ev: dict):
        QMessageBox.information(self, "Modifier", f"Modification de {ev.get('numero_evaluation')}")
    
    def _on_validate(self, ev: dict):
        QMessageBox.information(self, "Valider", f"Validation de {ev.get('numero_evaluation')}")
    
    def _on_delete(self, ev: dict):
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Supprimer l'évaluation {ev.get('numero_evaluation')} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Supprimer", "À implémenter")
    
    def _get_statut(self, ev: dict) -> str:
        if ev.get('est_validee'):
            return "VALIDEE"
        elif ev.get('montant_accepte'):
            return "A_VALIDER"
        else:
            return "BROUILLON"
    
    # ============================================================
    # MENU CONTEXTUEL
    # ============================================================
    
    def _show_context_menu(self, ev: dict, global_pos):
        """Affiche le menu contextuel"""
        from PySide6.QtGui import QAction
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 13px;
                color: #1e293b;
            }
            QMenu::item:selected {
                background-color: #f1f5f9;
                color: #1a73e8;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e2e8f0;
                margin: 4px 8px;
            }
        """)
        
        action_voir = QAction("👁️  Voir les détails", self)
        action_voir.triggered.connect(lambda: self._on_edit(ev))
        menu.addAction(action_voir)
        
        action_modifier = QAction("✏️  Modifier", self)
        action_modifier.triggered.connect(lambda: self._on_edit(ev))
        menu.addAction(action_modifier)
        
        action_dupliquer = QAction("📋  Dupliquer", self)
        menu.addAction(action_dupliquer)
        
        menu.addSeparator()
        
        action_valider = QAction("✔️  Valider", self)
        action_valider.setEnabled(not ev.get('est_validee'))
        action_valider.triggered.connect(lambda: self._on_validate(ev))
        menu.addAction(action_valider)
        
        action_rejeter = QAction("❌  Rejeter", self)
        menu.addAction(action_rejeter)
        
        menu.addSeparator()
        
        action_supprimer = QAction("🗑️  Supprimer", self)
        action_supprimer.triggered.connect(lambda: self._on_delete(ev))
        menu.addAction(action_supprimer)
        
        menu.exec(global_pos)


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
        
        # Barre d'info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        info_layout = QHBoxLayout(info_frame)
        
        self.lbl_count = QLabel("0 entrée(s)")
        self.lbl_count.setStyleSheet("color: #64748b; font-size: 12px;")
        info_layout.addWidget(self.lbl_count)
        
        info_layout.addStretch()
        
        self.btn_rafraichir = QPushButton("🔄 Rafraîchir")
        self.btn_rafraichir.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 14px;
                color: #64748b;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e8f0fe;
                color: #1a73e8;
                border-color: #1a73e8;
            }
        """)
        self.btn_rafraichir.clicked.connect(self._charger_historique)
        info_layout.addWidget(self.btn_rafraichir)
        
        layout.addWidget(info_frame)
        
        # Tableau
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
    
    def update_data(self, data):
        """Appelé par Dossier360View.update_ui() → délègue au chargement dédié"""
        self._charger_historique()
    
    def _charger_historique(self):
        """Charge l'historique via le contrôleur dédié"""
        try:
            sinistre_id = self.dossier_360.sinistre_id
            controller = self.dossier_360.sinistre_controller
            
            # ✅ Appel au contrôleur dédié
            historique = controller.get_historique_sinistre(sinistre_id)
            
            if historique is None:
                historique = []
            
            self._afficher(historique)
            
        except Exception as e:
            print(f"Erreur chargement historique: {e}")
            import traceback
            traceback.print_exc()
            self.table.setRowCount(0)
            self.lbl_count.setText("Erreur de chargement")
    
    def _afficher(self, historique: List[dict]):
        """Affiche les entrées d'historique"""
        self.table.setRowCount(len(historique))
        
        # Couleurs par type d'action
        action_colors = {
            'CREATION': '#22c55e',
            'MODIFICATION': '#3b82f6',
            'VALIDATION': '#06b6d4',
            'SUPPRESSION': '#ef4444',
            'PAIEMENT': '#8b5cf6',
            'ENCAISSEMENT': '#10b981',
            'CLOTURE': '#64748b',
            'REOUVERTURE': '#f59e0b',
        }
        
        for i, h in enumerate(historique):
            # Date formatée
            date_str = h.get('date_action', '')
            if date_str:
                try:
                    date_str = date_str.replace('T', ' ')[:19]
                except Exception:
                    pass
            self.table.setItem(i, 0, QTableWidgetItem(date_str))
            
            self.table.setItem(i, 1, QTableWidgetItem(h.get('utilisateur_nom', '')))
            
            # Action avec couleur
            action = h.get('action', '')
            action_item = QTableWidgetItem(action)
            color = action_colors.get(action.upper() if action else '', '#64748b')
            action_item.setForeground(QColor(color))
            self.table.setItem(i, 2, action_item)
            
            self.table.setItem(i, 3, QTableWidgetItem(h.get('entite', '')))
            self.table.setItem(i, 4, QTableWidgetItem(h.get('champ_modifie', '') or ''))
            
            ancien = h.get('ancienne_valeur', '') or ''
            nouveau = h.get('nouvelle_valeur', '') or ''
            if ancien or nouveau:
                self.table.setItem(i, 5, QTableWidgetItem(f"{ancien} → {nouveau}"))
            else:
                self.table.setItem(i, 5, QTableWidgetItem('—'))
        
        self.lbl_count.setText(f"{len(historique)} entrée(s)")
