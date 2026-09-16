

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
from PySide6.QtGui import QFont, QColor, QPalette, QAction

from datetime import datetime, timedelta
from typing import Optional, List
from addons.sinistres.models.sinistre import LometaSinistre
from addons.sinistres.views.tableau_base import TableauActions


# ============================================================
# PAGE 4: EXPERTISES
# ============================================================


class ExpertisesPage(QWidget):
    """Page de gestion des expertises"""
    
    def __init__(self, controller, user):
        super().__init__()
        self.controller = controller
        self.user = user
        self.current_sinistre_id = None
        self.selected_mission_id = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title = QLabel("🔬 Gestion des Expertises")
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
        
        self.lbl_total = QLabel("Total: 0")
        self.lbl_total.setStyleSheet("font-weight: bold; color: #1e293b;")
        stats_layout.addWidget(self.lbl_total)
        
        stats_layout.addStretch()
        
        self.lbl_encours = QLabel("🟣 En cours: 0")
        self.lbl_encours.setStyleSheet("color: #8b5cf6;")
        stats_layout.addWidget(self.lbl_encours)
        
        self.lbl_termine = QLabel("✅ Terminées: 0")
        self.lbl_termine.setStyleSheet("color: #22c55e;")
        stats_layout.addWidget(self.lbl_termine)
        
        layout.addWidget(stats_frame)
        
        # Liste des expertises
        self.table = TableauActions()
        columns = [
            {'key': 'numero_mission', 'label': 'N° Mission', 'width': 120},
            {'key': 'sinistre_numero', 'label': 'N° Sinistre', 'width': 120},
            {'key': 'expert_nom', 'label': 'Expert', 'width': 150},
            {'key': 'type_expertise', 'label': 'Type', 'width': 120},
            {'key': 'date_mission', 'label': 'Date', 'width': 100, 'format': lambda x: x[:10] if x else ''},
            {'key': 'date_echeance', 'label': 'Échéance', 'width': 100, 'format': lambda x: x[:10] if x else ''},
            {'key': 'statut', 'label': 'Statut', 'width': 120, 'color_map': self._get_statut_color},
        ]
        # Définir les actions
        actions = [
            {'label': 'Voir', 'icon': '👁️', 'callback': self._on_voir_mission, 'context_menu': True},
            {'label': 'Modifier', 'icon': '✏️', 'callback': self._on_modifier_mission, 'context_menu': True},
            {'label': 'Supprimer', 'icon': '🗑️', 'callback': self._on_supprimer_mission, 'context_menu': False},
        ]
        self.table.row_selected.connect(self._on_mission_selected)
        self.table.row_double_clicked.connect(self._on_mission_double_clicked)
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
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
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

        self.btn_demarrer = QPushButton("▶️ Démarrer")
        self.btn_demarrer.setStyleSheet("padding: 10px 25px; border-radius: 8px;")
        self.btn_demarrer.clicked.connect(self.demarrer_mission)
        btn_layout.addWidget(self.btn_demarrer)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def load_data(self):
        """Charge les sinistres et les expertises"""
        try:
            self.sinistre_combo.clear()
            self.sinistre_combo.addItem("📋 Tous les sinistres", None)
            sinistres = self.controller.get_sinistres_recents()
            for s in sinistres:
                self.sinistre_combo.addItem(
                    f"{s.get('numero_sinistre')} - {s.get('branche', '')}",
                    s.get('id')
                )
        except Exception as e:
            print(f"Erreur chargement données: {e}")

    def _get_statut_color(self, statut: str) -> Optional[str]:
        """Retourne la couleur selon le statut"""
        colors = {
            'CREEE': '#f59e0b',
            'AFFECTEE': '#3b82f6',
            'EN_COURS': '#8b5cf6',
            'RAPPORT_REÇU': '#06b6d4',
            'VALIDE': '#22c55e',
            'ANNULE': '#ef4444'
        }
        return colors.get(statut)

    def _on_cell_clicked(self, row: int, col: int):
        """Gère le clic sur une ligne"""
        self.table.selectRow(row)

    def _show_context_menu(self, position):
        """Affiche le menu contextuel sur clic droit avec un design moderne"""
        # Récupérer la ligne sélectionnée
        row = self.table.currentRow()
        if row < 0:
            return
        
        # Récupérer les données de la mission
        mission_data = self.table.get_selected_data()
        if not mission_data:
            return
        
        mission_numero = mission_data.get('numero_mission', 'N/A')
        mission_statut = mission_data.get('statut', '')
        
        # Créer le menu
        menu = QMenu(self)
        
        # 🎨 Style moderne QSS pour le menu contextuel
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
                font-weight: 500;
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
        
        # ✅ Action: Détail
        action_detail = QAction("👁️  Détail", self)
        action_detail.triggered.connect(lambda: self.open_mission_detail_by_numero(mission_numero))
        menu.addAction(action_detail)
        
        menu.addSeparator()
        
        # ✅ Action: Modifier
        action_modifier = QAction("✏️  Modifier", self)
        action_modifier.triggered.connect(lambda: self._on_modifier_mission(mission_data))
        menu.addAction(action_modifier)
        
        # ✅ Action: Supprimer
        action_supprimer = QAction("🗑️  Supprimer", self)
        action_supprimer.triggered.connect(lambda: self._on_supprimer_mission(mission_data))
        menu.addAction(action_supprimer)
        
        menu.addSeparator()
        
        # ✅ Action: Affecter expert (uniquement si statut CREEE ou AFFECTEE)
        action_affecter = QAction("👤  Affecter expert", self)
        action_affecter.setEnabled(mission_statut in ["CREEE", "AFFECTEE"])
        action_affecter.triggered.connect(lambda: self._affecter_expert_from_menu(mission_data))
        menu.addAction(action_affecter)
        
        # ✅ Action: Démarrer (uniquement si statut AFFECTEE)
        action_demarrer = QAction("▶️  Démarrer", self)
        action_demarrer.setEnabled(mission_statut == "AFFECTEE")
        action_demarrer.triggered.connect(lambda: self._demarrer_mission_from_menu(mission_data))
        menu.addAction(action_demarrer)
        
        # ✅ Action: Déposer rapport (uniquement si statut EN_COURS ou RAPPORT_REÇU)
        action_rapport = QAction("📄  Déposer rapport", self)
        action_rapport.setEnabled(mission_statut in ["EN_COURS", "RAPPORT_REÇU"])
        action_rapport.triggered.connect(lambda: self._deposer_rapport_from_menu(mission_data))
        menu.addAction(action_rapport)
        
        # ✅ Action: Valider (uniquement si statut RAPPORT_REÇU)
        action_valider = QAction("✅  Valider", self)
        action_valider.setEnabled(mission_statut == "RAPPORT_REÇU")
        action_valider.triggered.connect(lambda: self._valider_mission_from_menu(mission_data))
        menu.addAction(action_valider)
        
        # Afficher le menu avec ombre portée sous Qt
        menu.exec(self.table.viewport().mapToGlobal(position))

    # ============================================================
    # ✅ ACTIONS DU MENU CONTEXTUEL
    # ============================================================
    
    def _affecter_expert_from_menu(self, data: dict):
        """Affecte un expert à la mission (depuis le menu contextuel)"""
        mission_id = data.get('id')
        mission_numero = data.get('numero_mission')
        
        if not mission_id:
            QMessageBox.warning(self, "Erreur", "Mission non trouvée")
            return
        
        # Récupérer les infos de la mission
        mission_info = self.controller.get_mission(mission_id)
        
        from addons.sinistres.views.affecter_expert_dialog import AffecterExpertDialog
        dialog = AffecterExpertDialog(
            mission_id=mission_id,
            mission_info=mission_info,
            expertise_controller=self.controller,
            user=self.user,
            parent=self
        )
        dialog.expert_affected.connect(self._on_expert_affected)
        dialog.exec()
    
    def _demarrer_mission_from_menu(self, data: dict):
        """Démarre une mission (depuis le menu contextuel)"""
        mission_id = data.get('id')
        mission_numero = data.get('numero_mission')
        
        if not mission_id:
            QMessageBox.warning(self, "Erreur", "Mission non trouvée")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous démarrer la mission {mission_numero} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.demarrer_mission(mission_id)
                if result:
                    QMessageBox.information(self, "Succès", "Mission démarrée avec succès")
                    self.load_expertises(self.current_sinistre_id)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def _deposer_rapport_from_menu(self, data: dict):
        """Dépose un rapport (depuis le menu contextuel)"""
        mission_id = data.get('id')
        mission_numero = data.get('numero_mission')
        
        if not mission_id:
            QMessageBox.warning(self, "Erreur", "Mission non trouvée")
            return
        
        mission_info = self.controller.get_mission(mission_id)
        
        from addons.sinistres.views.deposer_rapport_dialog import DeposerRapportDialog
        dialog = DeposerRapportDialog(
            mission_id=mission_id,
            mission_info=mission_info,
            expertise_controller=self.controller,
            user=self.user,
            parent=self
        )
        dialog.rapport_depose.connect(self._on_rapport_depose)
        dialog.exec()
    
    def _valider_mission_from_menu(self, data: dict):
        """Valide une mission (depuis le menu contextuel)"""
        mission_id = data.get('id')
        mission_numero = data.get('numero_mission')
        
        if not mission_id:
            QMessageBox.warning(self, "Erreur", "Mission non trouvée")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous valider la mission {mission_numero} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.valider_mission(mission_id)
                if result:
                    QMessageBox.information(self, "Succès", "Mission validée avec succès")
                    self.load_expertises(self.current_sinistre_id)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def demarrer_mission(self):
        """Démarre une mission (passage en EN_COURS)"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une mission")
            return
        
        mission_numero = self.table.item(row, 0).text()
        mission_statut_affichage = self.table.item(row, 5).text()
        
        # ✅ Récupérer le statut réel depuis la base
        try:
            mission_data = self.controller.get_mission_by_numero(mission_numero)
            if not mission_data:
                QMessageBox.warning(self, "Erreur", "Mission non trouvée")
                return
            
            mission_statut = mission_data.get('statut')
            
            if mission_statut != "AFFECTEE":
                QMessageBox.warning(
                    self,
                    "Attention",
                    f"Seule une mission affectée peut être démarrée (statut: {mission_statut_affichage})"
                )
                return
            
            reply = QMessageBox.question(
                self,
                "Confirmation",
                f"Voulez-vous démarrer la mission {mission_numero} ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                result = self.controller.demarrer_mission(mission_data.get('id'))
                if result:
                    QMessageBox.information(self, "Succès", "Mission démarrée avec succès")
                    self.load_expertises(self.current_sinistre_id)
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def on_sinistre_changed(self, index):
        """Charge les expertises du sinistre sélectionné"""
        sinistre_id = self.sinistre_combo.currentData()
        self.current_sinistre_id = sinistre_id
        
        if sinistre_id is None:
            # ✅ Tous les sinistres
            self.load_all_expertises()
        else:
            self.load_expertises(sinistre_id)
    
    def load_all_expertises(self):
        """Charge toutes les expertises (tous sinistres)"""
        try:
            # Récupérer toutes les expertises
            all_expertises = self.controller.get_all_missions()
            self._update_table_with_actions(all_expertises)
            
            # Mettre à jour les stats
            total = len(all_expertises)
            en_cours = sum(1 for e in all_expertises if e.get('statut') in ['CREEE', 'AFFECTEE', 'EN_COURS', 'RAPPORT_REÇU'])
            termine = sum(1 for e in all_expertises if e.get('statut') in ['VALIDE'])
            
            self.lbl_total.setText(f"Total: {total}")
            self.lbl_encours.setText(f"🟣 En cours: {en_cours}")
            self.lbl_termine.setText(f"✅ Terminées: {termine}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement expertises: {str(e)}")

    def load_expertises(self, sinistre_id: int):
        """Charge les expertises et remplit le tableau"""
        try:
            expertises = self.controller.get_missions_by_sinistre(sinistre_id)
            self._update_table_with_actions(expertises)
            
            # Mettre à jour les stats
            total = len(expertises)
            en_cours = sum(1 for e in expertises if e.get('statut') in ['CREEE', 'AFFECTEE', 'EN_COURS', 'RAPPORT_REÇU'])
            termine = sum(1 for e in expertises if e.get('statut') in ['VALIDE'])
            
            self.lbl_total.setText(f"Total: {total}")
            self.lbl_encours.setText(f"🟣 En cours: {en_cours}")
            self.lbl_termine.setText(f"✅ Terminées: {termine}")
            
            # Remplir le tableau avec TableauActions
            self.table.set_data(expertises, self._get_columns(), self._get_actions())
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement expertises: {str(e)}")
    
    def _get_columns(self):
        """Retourne la configuration des colonnes"""
        return [
            {'key': 'numero_mission', 'label': 'N° Mission', 'width': 120},
            {'key': 'sinistre_numero', 'label': 'N° Sinistre', 'width': 120, 'format': lambda x: x or 'N/A'},
            {'key': 'expert_nom', 'label': 'Expert', 'width': 150, 'format': lambda x: x or 'Non affecté'},
            {'key': 'type_expertise', 'label': 'Type', 'width': 120},
            {'key': 'date_mission', 'label': 'Date', 'width': 100, 'format': lambda x: x[:10] if x else ''},
            {'key': 'date_echeance', 'label': 'Échéance', 'width': 100, 'format': lambda x: x[:10] if x else ''},
            {'key': 'statut', 'label': 'Statut', 'width': 120, 'color_map': self._get_statut_color},
        ]
    
    def _get_actions(self):
        """Retourne la configuration des actions"""
        return [
            {'label': 'Voir', 'icon': '👁️', 'callback': self._on_voir_mission, 'context_menu': True},
            {'label': 'Modifier', 'icon': '✏️', 'callback': self._on_modifier_mission, 'context_menu': True},
            {'label': 'Supprimer', 'icon': '🗑️', 'callback': self._on_supprimer_mission, 'context_menu': False},
        ]
    
    def _on_mission_selected(self, row: int, data: dict):
        """Gère la sélection d'une mission"""
        self.selected_mission_id = data.get('id')
    
    def _on_mission_double_clicked(self, row: int, data: dict):
        """Gère le double-clic sur une mission"""
        self.open_mission_detail_by_numero(data.get('numero_mission'))
    
    def _on_voir_mission(self, data: dict):
        """Ouvre le détail d'une mission"""
        self.open_mission_detail_by_numero(data.get('numero_mission'))
    
    def _on_modifier_mission(self, data: dict):
        """Modifie une mission"""
        QMessageBox.information(self, "Modification", f"Modification de la mission {data.get('numero_mission')}")
    
    def _on_supprimer_mission(self, data: dict):
        """Supprime une mission"""
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous supprimer la mission {data.get('numero_mission')} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Suppression", "Mission supprimée (à implémenter)")

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

    def _update_table_with_actions(self, expertises: List[dict]):
        """Met à jour le tableau avec TableauActions"""
        self.table.set_data(expertises, self._get_columns(), self._get_actions())

    # ============================================================
    # ✅ CRÉATION DE MISSION (version finale)
    # ============================================================
    
    def creer_mission(self):
        """Ouvre le dialogue de création de mission"""
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        # Récupérer les informations du sinistre
        sinistre_info = {}
        try:
            # TODO: Récupérer les infos du sinistre depuis le contrôleur
            sinistre_info = {
                'numero_sinistre': self.sinistre_combo.currentText().split(' - ')[0] if self.sinistre_combo.currentIndex() > 0 else 'N/A',
                'branche': self.sinistre_combo.currentText().split(' - ')[1] if len(self.sinistre_combo.currentText().split(' - ')) > 1 else 'N/A',
                'client_nom': 'N/A'  # À récupérer depuis la base
            }
        except:
            pass
        
        # ✅ Ouvrir le dialogue de création
        from addons.sinistres.views.mission_dialog import MissionDialog
        dialog = MissionDialog(
            sinistre_id=self.current_sinistre_id,
            expertise_controller=self.controller,
            user=self.user,
            sinistre_info=sinistre_info,
            parent=self
        )
        
        # Connecter le signal pour rafraîchir après création
        dialog.mission_created.connect(self._on_mission_created)
        
        dialog.exec()
    
    def _on_mission_created(self, mission_data: dict):
        """Appelé après la création d'une mission"""
        QMessageBox.information(
            self,
            "Succès",
            f"✅ Mission {mission_data.get('numero_mission', '')} créée avec succès !"
        )
        self.load_expertises(self.current_sinistre_id)
 
    def affecter_expert(self):
        """Affecte un expert à la mission sélectionnée"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une mission")
            return
        
        # ✅ Récupérer le statut réel depuis les données de la table
        mission_numero = self.table.item(row, 0).text()
        mission_statut_affichage = self.table.item(row, 5).text()
        mission_statut_reel = self.table.item(row, 5).data(Qt.UserRole)  # Stocké dans update_table
        
        # ✅ Si le statut n'est pas stocké, le récupérer via le contrôleur
        if not mission_statut_reel:
            try:
                mission_data = self.controller.get_mission_by_numero(mission_numero)
                if mission_data:
                    mission_statut_reel = mission_data.get('statut')
            except:
                pass
        
        # ✅ Vérifier avec la valeur réelle
        if mission_statut_reel not in ["CREEE", "AFFECTEE"]:
            QMessageBox.warning(
                self,
                "Attention",
                f"Cette mission ne peut pas être affectée (statut: {mission_statut_affichage})\n"
                "Seules les missions au statut 'CRÉÉE' ou 'AFFECTÉE' peuvent être affectées."
            )
            return
        
        try:
            mission_data = self.controller.get_mission_by_numero(mission_numero)
            if not mission_data:
                QMessageBox.warning(self, "Erreur", "Mission non trouvée")
                return
            
            mission_id = mission_data.get('id')
            mission_info = self.controller.get_mission(mission_id)
            
            from addons.sinistres.views.affecter_expert_dialog import AffecterExpertDialog
            dialog = AffecterExpertDialog(
                mission_id=mission_id,
                mission_info=mission_info,
                expertise_controller=self.controller,
                user=self.user,
                parent=self
            )
            
            dialog.expert_affected.connect(self._on_expert_affected)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

    def _on_expert_affected(self, data: dict):
        """Appelé après l'affectation d'un expert"""
        self.load_expertises(self.current_sinistre_id)
        QMessageBox.information(
            self,
            "Succès",
            f"✅ Expert affecté avec succès à la mission {data.get('mission_id')}"
        )    
  
    def deposer_rapport(self):
        """Dépose un rapport pour la mission sélectionnée"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une mission")
            return
        
        mission_numero = self.table.item(row, 0).text()
        mission_statut_affichage = self.table.item(row, 5).text()
        mission_statut_reel = self.table.item(row, 5).data(Qt.UserRole)
        
        # ✅ Récupérer le statut réel
        if not mission_statut_reel:
            try:
                mission_data = self.controller.get_mission_by_numero(mission_numero)
                if mission_data:
                    mission_statut_reel = mission_data.get('statut')
            except:
                pass
        
        # ✅ Vérifier que la mission peut recevoir un rapport
        if mission_statut_reel not in ["EN_COURS", "RAPPORT_REÇU"]:
            QMessageBox.warning(
                self,
                "Attention",
                f"Seule une mission en cours peut recevoir un rapport (statut: {mission_statut_affichage})\n"
                "La mission doit être démarrée avant de pouvoir déposer un rapport."
            )
            return
        
        try:
            mission_data = self.controller.get_mission_by_numero(mission_numero)
            if not mission_data:
                QMessageBox.warning(self, "Erreur", "Mission non trouvée")
                return
            
            mission_id = mission_data.get('id')
            mission_info = self.controller.get_mission(mission_id)
            
            # ✅ Ouvrir le dialogue de dépôt de rapport
            from addons.sinistres.views.deposer_rapport_dialog import DeposerRapportDialog
            dialog = DeposerRapportDialog(
                mission_id=mission_id,
                mission_info=mission_info,
                expertise_controller=self.controller,
                user=self.user,
                parent=self
            )
            
            dialog.rapport_depose.connect(self._on_rapport_depose)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

    def _on_rapport_depose(self, data: dict):
        """Appelé après le dépôt d'un rapport"""
        self.load_expertises(self.current_sinistre_id)
        QMessageBox.information(
            self,
            "Succès",
            f"✅ Rapport déposé avec succès pour la mission {data.get('mission_id')}"
        )
 
    def valider_mission(self):
        """Valide la mission sélectionnée"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une mission")
            return
        
        mission_numero = self.table.item(row, 0).text()
        mission_statut_affichage = self.table.item(row, 5).text()
        
        # ✅ Récupérer le statut réel depuis la base
        try:
            mission_data = self.controller.get_mission_by_numero(mission_numero)
            if not mission_data:
                QMessageBox.warning(self, "Erreur", "Mission non trouvée")
                return
            
            mission_statut = mission_data.get('statut')
            
            if mission_statut != "RAPPORT_REÇU":
                QMessageBox.warning(
                    self,
                    "Attention",
                    f"Seule une mission avec un rapport peut être validée (statut: {mission_statut_affichage})"
                )
                return
            
            reply = QMessageBox.question(
                self,
                "Confirmation",
                f"Voulez-vous valider la mission {mission_numero} ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                result = self.controller.valider_mission(mission_data.get('id'))
                if result:
                    QMessageBox.information(self, "Succès", "Mission validée avec succès")
                    self.load_expertises(self.current_sinistre_id)
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def open_mission_detail_from_data(self, data: dict):
        """Ouvre le détail d'une mission à partir des données"""
        mission_numero = data.get('numero_mission')
        if mission_numero:
            self.open_mission_detail_by_numero(mission_numero)

    def open_mission_detail_by_numero(self, mission_numero: str):
        """Ouvre le détail d'une mission par son numéro"""
        try:
            mission_data = self.controller.get_mission_by_numero(mission_numero)
            if mission_data:
                mission_id = mission_data.get('id')
                mission_info = self.controller.get_mission(mission_id)
                
                # Créer un dialogue ou une page de détail
                QMessageBox.information(
                    self,
                    "Détail de la mission",
                    f"📋 Mission: {mission_numero}\n"
                    f"👤 Expert: {mission_info.get('expert_nom', 'Non affecté')}\n"
                    f"📌 Type: {mission_info.get('type_expertise', 'N/A')}\n"
                    f"📅 Date: {mission_info.get('date_mission', 'N/A')}\n"
                    f"📅 Échéance: {mission_info.get('date_echeance', 'N/A')}\n"
                    f"📌 Statut: {mission_info.get('statut', 'N/A')}\n"
                    f"💰 Montant estimé: {mission_info.get('montant_estime', 0):,.0f} FCFA"
                )
            else:
                QMessageBox.warning(self, "Erreur", f"Mission {mission_numero} non trouvée")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

    

        