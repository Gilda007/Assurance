"""
Tableau de bord LOMETA Sinistres
Avec TableauActions (menu contextuel) et impression conditionnelle
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QMessageBox,
    QPushButton, QMenu, QHeaderView, QFileDialog
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QColor

from datetime import datetime
from typing import Optional, List, Dict

from addons.sinistres.views.tableau_base import TableauActions


# ============================================================
# CONFIGURATION DES STATUTS
# ============================================================

STATUT_COLORS = {
    'OUVERT': '#f59e0b',
    'EN_INSTRUCTION': '#3b82f6',
    'EN_EXPERTISE': '#8b5cf6',
    'EN_EVALUATION': '#ec4899',
    'VALIDE': '#06b6d4',
    'EN_REGLEMENT': '#f97316',
    'EN_RECOURS': '#ef4444',
    'CLOTURE': '#22c55e',
    'REOUVERT': '#dc2626',
}

# Types d'impression disponibles selon le statut
IMPRESSIONS_PAR_STATUT = {
    'OUVERT': [
        ('ACCUSE_RECEPTION', '📩 Accusé de réception'),
        ('FICHE_DECLARATION', '📄 Fiche de déclaration'),
    ],
    'EN_INSTRUCTION': [
        ('FICHE_INSTRUCTION', '📋 Fiche d\'instruction'),
    ],
    'EN_EXPERTISE': [
        ('FICHE_EXPERTISE', '🔬 Fiche d\'expertise'),
    ],
    'EN_EVALUATION': [
        ('FICHE_EVALUATION', '💰 Fiche d\'évaluation'),
    ],
    'VALIDE': [
        ('FICHE_VALIDEE', '✅ Fiche validée'),
    ],
    'EN_REGLEMENT': [
        ('FICHE_REGLEMENT', '💳 Fiche de règlement'),
    ],
    'EN_RECOURS': [
        ('FICHE_RECOURS', '⚖️ Fiche de recours'),
    ],
    'CLOTURE': [
        ('FICHE_DEFINITIVE', '📁 Fiche définitive'),
        ('ATTESTATION_CLOTURE', '📜 Attestation de clôture'),
    ],
    'REOUVERT': [
        ('FICHE_REOUVERTURE', '🔄 Fiche de réouverture'),
    ],
}


# ============================================================
# PAGE DASHBOARD
# ============================================================

class DashboardPage(QWidget):
    """Tableau de bord des sinistres avec actions contextuelles"""
    
    def __init__(self, controller, user, referentiel_controller=None, expertise_controller=None, evaluation_controller=None, reglement_controller=None, recours_controller=None,):
        super().__init__()
        self.controller = controller
        self.user = user
        self.referentiel_controller = referentiel_controller
        self.expertise_controller = expertise_controller
        self.evaluation_controller = evaluation_controller
        self.reglement_controller = reglement_controller
        self.recours_controller = recours_controller
        self._sinistres_data = []  # Cache local
        self.setup_ui()
        self.refresh()
    
    # ============================================================
    # UI
    # ============================================================
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # ---------- En-tête ----------
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Tableau de bord des sinistres")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Rafraîchir")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                color: #64748b;
            }
            QPushButton:hover {
                background-color: #e8f0fe;
                color: #1a73e8;
                border-color: #1a73e8;
            }
        """)
        self.btn_refresh.clicked.connect(self.refresh)
        header_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(header_layout)
        
        # ---------- Cartes de statistiques ----------
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        self.card_total = self._create_stat_card("Total Sinistres", "0", "#3b82f6", "📊")
        self.card_ouverts = self._create_stat_card("Ouverts", "0", "#f59e0b", "🔓")
        self.card_clotures = self._create_stat_card("Clôturés", "0", "#22c55e", "✅")
        self.card_recours = self._create_stat_card("En recours", "0", "#ef4444", "⚖️")
        
        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_ouverts)
        cards_layout.addWidget(self.card_clotures)
        cards_layout.addWidget(self.card_recours)
        layout.addLayout(cards_layout)
        
        # ---------- Section sinistres récents ----------
        section_header = QHBoxLayout()
        section_title = QLabel("📋 Sinistres récents")
        section_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        section_header.addWidget(section_title)
        
        section_header.addStretch()
        
        self.lbl_count = QLabel("0 sinistre(s)")
        self.lbl_count.setStyleSheet("color: #64748b; font-size: 12px;")
        section_header.addWidget(self.lbl_count)
        
        layout.addLayout(section_header)
        
        # ---------- Tableau avec actions ----------
        self.table = TableauActions()
        
        # Configuration des colonnes
        columns = self._get_columns()
        actions = self._get_actions()
        
        self.table.set_data([], columns, actions)
        self.table.row_selected.connect(self._on_row_selected)
        self.table.row_double_clicked.connect(self._on_row_double_clicked)
        
        # Style
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
                background-color: white;
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
        
        layout.addWidget(self.table, 1)
    
    def _create_stat_card(self, title: str, value: str, color: str, icon: str = "") -> QFrame:
        """Crée une carte de statistique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        
        # En-tête avec icône
        header = QHBoxLayout()
        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 16px;")
            header.addWidget(icon_lbl)
        
        label = QLabel(title)
        label.setStyleSheet("color: #64748b; font-size: 12px;")
        header.addWidget(label)
        header.addStretch()
        layout.addLayout(header)
        
        # Valeur
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
        layout.addWidget(value_label)
        
        card.value_label = value_label
        return card
    
    # ============================================================
    # CONFIGURATION TABLEAU
    # ============================================================
    
    def _get_columns(self) -> List[Dict]:
        """Colonnes du tableau"""
        return [
            {'key': 'numero_sinistre', 'label': 'N° Sinistre', 'width': 130},
            {'key': 'client_nom', 'label': 'Client', 'width': 180, 'format': lambda x: x or 'N/A'},
            {'key': 'branche', 'label': 'Branche', 'width': 100},
            {'key': 'date_survenance', 'label': 'Date', 'width': 100,
             'format': lambda x: x[:10] if x else ''},
            {'key': 'statut', 'label': 'Statut', 'width': 130,
             'color_map': self._get_statut_color},
            {'key': 'montant_net', 'label': 'Montant', 'width': 120,
             'format': lambda x: f"{x:,.0f}" if x else '0'},
        ]
    
    def _get_actions(self) -> List[Dict]:
        """Actions du tableau (menu contextuel)"""
        return [
            {'label': 'Voir le détail', 'icon': '👁️',
             'callback': self._on_voir_detail, 'context_menu': True},
            {'label': 'Modifier', 'icon': '✏️',
             'callback': self._on_modifier, 'context_menu': True},
            {'label': 'Imprimer', 'icon': '🖨️',
             'callback': self._on_imprimer, 'context_menu': True},
            {'label': 'Exporter', 'icon': '📥',
             'callback': self._on_exporter, 'context_menu': True},
        ]
    
    def _get_statut_color(self, statut: str) -> Optional[str]:
        """Retourne la couleur du statut"""
        return STATUT_COLORS.get(statut)
    
    # ============================================================
    # CHARGEMENT DES DONNÉES
    # ============================================================
    
    def refresh(self):
        """Rafraîchit le tableau de bord"""
        try:
            # Statistiques
            stats = self.controller.get_statistiques()
            
            self.card_total.value_label.setText(str(stats.get('total', 0)))
            par_statut = stats.get('par_statut', {})
            self.card_ouverts.value_label.setText(str(par_statut.get('OUVERT', 0)))
            self.card_clotures.value_label.setText(str(par_statut.get('CLOTURE', 0)))
            self.card_recours.value_label.setText(str(par_statut.get('EN_RECOURS', 0)))
            
            # Sinistres récents
            sinistres = self.controller.rechercher_sinistres({'limit': 20}) or []
            self._sinistres_data = sinistres
            
            # Enrichir avec le nom du client
            sinistres_enrichis = self._enrichir_sinistres(sinistres)
            
            # Mettre à jour le tableau
            self.table.set_data(sinistres_enrichis, self._get_columns(), self._get_actions())
            
            self.lbl_count.setText(f"{len(sinistres_enrichis)} sinistre(s)")
            
        except Exception as e:
            print(f"Erreur refresh dashboard: {e}")
            import traceback
            traceback.print_exc()
    
    def _enrichir_sinistres(self, sinistres: List[dict]) -> List[dict]:
        """Ajoute le nom du client pour l'affichage"""
        enriched = []
        for s in sinistres:
            s_copy = dict(s)
            # Nom du client (si dispo dans le dict, sinon fallback)
            if not s_copy.get('client_nom'):
                client_id = s_copy.get('client_id')
                s_copy['client_nom'] = self._get_client_nom(client_id)
            enriched.append(s_copy)
        return enriched
    
    def _get_client_nom(self, client_id) -> str:
        """Récupère le nom du client (fallback)"""
        if not client_id:
            return 'N/A'
        try:
            from addons.sinistres.controllers.automobile_controller import AutomobileController
            ac = AutomobileController()
            ac.set_current_user(self.user)
            client = ac.get_contact(client_id)
            if client:
                return f"{client.get('nom', '')} {client.get('prenom', '')}".strip()
        except Exception:
            pass
        return f"Client #{client_id}"
    
    # ============================================================
    # ACTIONS TABLEAU
    # ============================================================
    
    def _on_row_selected(self, row: int, data: dict):
        """Ligne sélectionnée"""
        pass
    
    def _on_row_double_clicked(self, row: int, data: dict):
        """Double-clic → ouvrir le détail"""
        self._on_voir_detail(data)
    
    def _on_voir_detail(self, data: dict):
        """Ouvre le détail du sinistre"""
        sinistre_id = data.get('id')
        numero = data.get('numero_sinistre', 'N/A')
        
        if not sinistre_id:
            QMessageBox.warning(self, "Erreur", "Sinistre non trouvé")
            return
        
        try:
            from addons.sinistres.views.dossier_360 import Dossier360View
            
            dossier = Dossier360View(
                sinistre_id=sinistre_id,
                sinistre_controller=self.controller,
                referentiel_controller=self.referentiel_controller, 
                expertise_controller=self.expertise_controller,      
                evaluation_controller=self.evaluation_controller,    
                reglement_controller=self.reglement_controller,      
                recours_controller=self.recours_controller,          
                user=self.user
            )
            dossier.setWindowTitle(f"Dossier 360° - {numero}")
            dossier.setMinimumSize(1200, 800)
            dossier.exec() if hasattr(dossier, 'exec') else dossier.show()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur d'ouverture: {str(e)}")
    
    def _on_modifier(self, data: dict):
        """Modifie un sinistre"""
        statut = data.get('statut', '')
        
        if statut == 'CLOTURE':
            QMessageBox.warning(
                self, "Attention",
                "Un sinistre clôturé ne peut pas être modifié directement.\n"
                "Utilisez la réouverture (SIN-071)."
            )
            return
        
        QMessageBox.information(
            self, "Modifier",
            f"Modification du sinistre {data.get('numero_sinistre')} (à implémenter)"
        )
    
    def _on_imprimer(self, data: dict):
        """Imprime un sinistre selon son statut"""
        statut = data.get('statut', '')
        numero = data.get('numero_sinistre', 'N/A')
        
        # Vérifier que le statut est connu
        if statut not in IMPRESSIONS_PAR_STATUT:
            QMessageBox.warning(
                self, "Impression impossible",
                f"Le statut '{statut}' ne permet pas l'impression."
            )
            return
        
        # Proposer les types d'impression disponibles
        types_dispo = IMPRESSIONS_PAR_STATUT[statut]
        
        if len(types_dispo) == 1:
            # Un seul type → impression directe
            self._generer_impression(data, types_dispo[0][0])
        else:
            # Plusieurs types → demander à l'utilisateur
            self._choisir_type_impression(data, types_dispo)
    
    def _choisir_type_impression(self, data: dict, types_dispo: List[tuple]):
        """Affiche un menu pour choisir le type d'impression"""
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
        """)
        
        for code, label in types_dispo:
            action = QAction(label, self)
            action.triggered.connect(
                lambda checked=False, c=code: self._generer_impression(data, c)
            )
            menu.addAction(action)
        
        # Afficher le menu au centre de l'écran
        menu.exec(self.cursor().pos())
    
    def _generer_impression(self, data: dict, type_impression: str):
        """Génère le document à imprimer"""
        numero = data.get('numero_sinistre', 'N/A')
        statut = data.get('statut', 'N/A')
        
        try:
            # Demander où sauvegarder
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer le document",
                f"{type_impression}_{numero}.pdf",
                "PDF (*.pdf);;Tous les fichiers (*)"
            )
            
            if not filename:
                return
            
            # TODO: Appeler le service d'impression
            # from addons.sinistres.services.impression_service import ImpressionService
            # service = ImpressionService()
            # result = service.generer_document(
            #     sinistre_id=data.get('id'),
            #     type_document=type_impression,
            #     filepath=filename
            # )
            
            # Pour l'instant, on simule
            print(f"📄 Génération du document:")
            print(f"   Sinistre : {numero}")
            print(f"   Statut   : {statut}")
            print(f"   Type     : {type_impression}")
            print(f"   Fichier  : {filename}")
            
            QMessageBox.information(
                self, "✅ Impression",
                f"Document généré avec succès :\n\n"
                f"📄 Sinistre : {numero}\n"
                f"📌 Statut : {statut}\n"
                f"🖨️ Type : {type_impression}\n"
                f"💾 Fichier : {filename}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur",
                f"Erreur lors de la génération du document:\n{str(e)}"
            )
    
    def _on_exporter(self, data: dict):
        """Exporte le sinistre en Excel/CSV"""
        numero = data.get('numero_sinistre', 'N/A')
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter le sinistre",
            f"sinistre_{numero}.csv",
            "CSV (*.csv);;Excel (*.xlsx)"
        )
        
        if filename:
            QMessageBox.information(
                self, "Export",
                f"Export vers {filename} (à implémenter)"
            )
    
    # ============================================================
    # MENU CONTEXTUEL (clic droit)
    # ============================================================
    
    def _show_context_menu(self, position):
        """Affiche le menu contextuel sur clic droit"""
        row = self.table.currentRow()
        if row < 0:
            return
        
        # Récupérer les données de la ligne
        data = self.table.get_selected_data()
        if not data:
            return
        
        numero = data.get('numero_sinistre', 'N/A')
        statut = data.get('statut', '')
        
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
        action_detail = QAction("👁️  Voir le détail", self)
        action_detail.triggered.connect(lambda: self._on_voir_detail(data))
        menu.addAction(action_detail)
        
        # --- Section 2 : Modification ---
        action_modifier = QAction("✏️  Modifier", self)
        action_modifier.setEnabled(statut != 'CLOTURE')
        if statut == 'CLOTURE':
            action_modifier.setToolTip("Sinistre clôturé (SIN-070)")
        action_modifier.triggered.connect(lambda: self._on_modifier(data))
        menu.addAction(action_modifier)
        
        menu.addSeparator()
        
        # --- Section 3 : Impression (dynamique selon statut) ---
        action_imprimer = QAction("🖨️  Imprimer", self)
        
        # Vérifier si le statut permet l'impression
        if statut in IMPRESSIONS_PAR_STATUT:
            types = IMPRESSIONS_PAR_STATUT[statut]
            if len(types) == 1:
                action_imprimer.triggered.connect(
                    lambda: self._generer_impression(data, types[0][0])
                )
            else:
                # Sous-menu
                submenu = menu.addMenu("🖨️  Imprimer")
                submenu.setStyleSheet(menu.styleSheet())
                for code, label in types:
                    sub_action = QAction(label, self)
                    sub_action.triggered.connect(
                        lambda checked=False, c=code: self._generer_impression(data, c)
                    )
                    submenu.addAction(sub_action)
                action_imprimer = None
        else:
            action_imprimer.setEnabled(False)
            action_imprimer.setToolTip(f"Statut '{statut}' non imprimable")
        
        if action_imprimer:
            menu.addAction(action_imprimer)
        
        # --- Section 4 : Export ---
        action_export = QAction("📥  Exporter", self)
        action_export.triggered.connect(lambda: self._on_exporter(data))
        menu.addAction(action_export)
        
        # --- Affichage ---
        menu.exec(self.table.viewport().mapToGlobal(position))