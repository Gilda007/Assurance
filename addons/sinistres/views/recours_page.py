

# """
# Vue principale du module LOMETA Sinistres
# Interface utilisateur complète pour la gestion des sinistres
# """
# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
#     QHeaderView, QLabel, QPushButton, QListWidgetItem, QStackedWidget,
#     QListWidget, QFrame, QMessageBox, QDialog, QGraphicsDropShadowEffect,
#     QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
#     QFormLayout, QGroupBox, QTabWidget, QSplitter, QScrollArea,
#     QProgressBar, QToolBar, QMenu, QCheckBox, QRadioButton
# )
# from PySide6.QtCore import Qt, QSize, Signal, Slot, QDate
# from PySide6.QtGui import QColor, QIcon, QFont, QAction, QCursor

# from datetime import datetime, timedelta
# from typing import Optional, List

# from addons.sinistres.views.repartition_recours_dialog import RepartitionRecoursDialog
# from addons.sinistres.views.comptabilite_recours_dialog import ComptabiliteRecoursDialog
# from addons.sinistres.views.widgets.alertes_widget import AlertesWidget
# from addons.sinistres.controllers.comptabilite_controller import ComptabiliteController


# # ============================================================
# # PAGE 7: RECOURS
# # ============================================================

# # class RecoursPage(QWidget):
# #     """Page de gestion des recours"""
    
# #     def __init__(self, controller, user):
# #         super().__init__()
# #         self.controller = controller
# #         self.user = user
# #         self.current_sinistre_id = None
# #         self.selected_recours_id = None
        
# #         # ✅ Contrôleur comptabilité
# #         self.comptabilite_controller = ComptabiliteController()
# #         self.comptabilite_controller.set_current_user(user)
        
# #         # ✅ Service de permissions (déjà utilisé dans _appliquer_permissions)
# #         from addons.sinistres.services.permission_service import PermissionService
# #         from addons.sinistres.security.permissions_helper import PermissionsUI
# #         self.permission_service = PermissionService()
# #         self.permissions_ui = PermissionsUI(user, self.permission_service)
        
# #         self.setup_ui()
# #         self._appliquer_permissions()
# #         self.load_data()

# #     def _appliquer_permissions(self):
# #         self.permissions_ui.masquer_si_non_autorise(
# #             self.btn_creer_rec, 'recours', 'CREATE'
# #         )
# #         self.permissions_ui.masquer_si_non_autorise(
# #             self.btn_encaisser, 'recours', 'UPDATE'
# #         )
# #         self.permissions_ui.masquer_si_non_autorise(
# #             self.btn_relance, 'recours', 'UPDATE'
# #         )
# #         self.permissions_ui.masquer_si_non_autorise(
# #             self.btn_planifier, 'recours', 'UPDATE'
# #         )
# #         # ✅ Nouveaux boutons
# #         self.permissions_ui.masquer_si_non_autorise(
# #             self.btn_repartition, 'recours', 'UPDATE'
# #         )
# #         self.permissions_ui.masquer_si_non_autorise(
# #             self.btn_comptabilite, 'recours', 'READ'
# #         )
# #         self.permissions_ui.masquer_si_non_autorise(
# #             self.btn_suivi, 'recours', 'READ'
# #         )
    
# #     def setup_ui(self):
# #         layout = QVBoxLayout(self)
# #         layout.setContentsMargins(25, 25, 25, 25)
# #         layout.setSpacing(15)
        
# #         header_layout = QHBoxLayout()
        
# #         title = QLabel("⚖️ Gestion des Recours")
# #         title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
# #         header_layout.addWidget(title)
        
# #         header_layout.addStretch()
        
# #         header_layout.addWidget(QLabel("Sinistre:"))
# #         self.sinistre_combo = QComboBox()
# #         self.sinistre_combo.setMinimumWidth(200)
# #         self.sinistre_combo.currentIndexChanged.connect(self.on_sinistre_changed)
# #         header_layout.addWidget(self.sinistre_combo)
        
# #         self.btn_refresh = QPushButton("🔄")
# #         self.btn_refresh.setFixedSize(35, 35)
# #         self.btn_refresh.setStyleSheet("border-radius: 17px;")
# #         self.btn_refresh.clicked.connect(self.load_data)
# #         header_layout.addWidget(self.btn_refresh)
        
# #         layout.addLayout(header_layout)
        
# #         # Statistiques
# #         stats_frame = QFrame()
# #         stats_frame.setStyleSheet("""
# #             QFrame {
# #                 background-color: #f8fafc;
# #                 border-radius: 8px;
# #                 padding: 10px;
# #             }
# #         """)
# #         stats_layout = QHBoxLayout(stats_frame)
        
# #         self.lbl_total = QLabel("Total recours: 0")
# #         self.lbl_total.setStyleSheet("font-weight: bold; color: #1e293b;")
# #         stats_layout.addWidget(self.lbl_total)
        
# #         stats_layout.addStretch()
        
# #         self.lbl_aboutis = QLabel("✅ Aboutis: 0")
# #         self.lbl_aboutis.setStyleSheet("color: #22c55e;")
# #         stats_layout.addWidget(self.lbl_aboutis)
        
# #         self.lbl_encours = QLabel("🟡 En cours: 0")
# #         self.lbl_encours.setStyleSheet("color: #f59e0b;")
# #         stats_layout.addWidget(self.lbl_encours)
        
# #         self.lbl_taux_recup = QLabel("📊 Taux récupération: 0%")
# #         self.lbl_taux_recup.setStyleSheet("color: #3b82f6;")
# #         stats_layout.addWidget(self.lbl_taux_recup)
        
# #         layout.addWidget(stats_frame)

# #         self.alertes_widget = AlertesWidget()
# #         self.alertes_widget.alerte_clicked.connect(self._on_alerte_clicked)
# #         layout.addWidget(self.alertes_widget)
        
# #         self.table_recours = QTableWidget()
# #         self.table_recours.setColumnCount(8)  # Augmenter de 7 à 8
# #         self.table_recours.setHorizontalHeaderLabels([
# #             "N°", "Débiteur", "Réclamé", "Accepté", "Encaissé", "Solde", "Prochaine relance", "Statut"
# #         ])
   
# #         self.table_recours.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
# #         self.table_recours.setAlternatingRowColors(True)
# #         self.table_recours.setStyleSheet("""
# #             QTableWidget {
# #                 border: 1px solid #e2e8f0;
# #                 border-radius: 8px;
# #                 gridline-color: #f1f5f9;
# #             }
# #             QTableWidget::item {
# #                 padding: 8px;
# #             }
# #             QHeaderView::section {
# #                 background-color: #f8fafc;
# #                 padding: 8px;
# #                 font-weight: bold;
# #                 border: none;
# #                 border-bottom: 1px solid #e2e8f0;
# #             }
# #         """)
# #         self.table_recours.setContextMenuPolicy(Qt.CustomContextMenu)
# #         self.table_recours.customContextMenuRequested.connect(self._show_table_context_menu)
# #         layout.addWidget(self.table_recours)
        
# #         btn_layout = QHBoxLayout()

# #         self.btn_creer_rec = QPushButton("➕ Nouveau recours")
# #         self.btn_creer_rec.setStyleSheet("""
# #             QPushButton {
# #                 background-color: #1a73e8;
# #                 color: white;
# #                 padding: 8px 20px;
# #                 border-radius: 8px;
# #                 font-weight: bold;
# #             }
# #             QPushButton:hover {
# #                 background-color: #1557b0;
# #             }
# #         """)
# #         self.btn_creer_rec.clicked.connect(self.creer_recours)
# #         btn_layout.addWidget(self.btn_creer_rec)

# #         # ✅ AJOUTER LE BOUTON ENCAISSER
# #         self.btn_encaisser = QPushButton("💰 Encaisser")
# #         self.btn_encaisser.setStyleSheet("""
# #             QPushButton {
# #                 background-color: #22c55e;
# #                 color: white;
# #                 padding: 8px 20px;
# #                 border-radius: 8px;
# #                 font-weight: bold;
# #             }
# #             QPushButton:hover {
# #                 background-color: #16a34a;
# #             }
# #         """)
# #         self.btn_encaisser.clicked.connect(self.encaisser_recours)
# #         btn_layout.addWidget(self.btn_encaisser)

# #         # ✅ AJOUTER LE BOUTON RELANCE
# #         self.btn_relance = QPushButton("🔔 Relancer")
# #         self.btn_relance.setStyleSheet("""
# #             QPushButton {
# #                 background-color: #f59e0b;
# #                 color: white;
# #                 padding: 8px 20px;
# #                 border-radius: 8px;
# #                 font-weight: bold;
# #             }
# #             QPushButton:hover {
# #                 background-color: #d97706;
# #             }
# #         """)
# #         self.btn_relance.clicked.connect(self.ajouter_relance)
# #         btn_layout.addWidget(self.btn_relance)

# #         # ✅ AJOUTER LE BOUTON PLANIFICATION AUTO
# #         self.btn_planifier = QPushButton("📅 Planifier relances")
# #         self.btn_planifier.setStyleSheet("""
# #             QPushButton {
# #                 background-color: #8b5cf6;
# #                 color: white;
# #                 padding: 8px 20px;
# #                 border-radius: 8px;
# #                 font-weight: bold;
# #             }
# #             QPushButton:hover {
# #                 background-color: #7c3aed;
# #             }
# #         """)
# #         self.btn_planifier.clicked.connect(self.planifier_relances_auto)
# #         btn_layout.addWidget(self.btn_planifier)

# #                 # ✅ Bouton Répartition
# #         self.btn_repartition = QPushButton("📊 Répartition")
# #         self.btn_repartition.setStyleSheet("""
# #             QPushButton {
# #                 background-color: #06b6d4;
# #                 color: white;
# #                 padding: 8px 20px;
# #                 border-radius: 8px;
# #                 font-weight: bold;
# #             }
# #             QPushButton:hover { background-color: #0891b2; }
# #             QPushButton:disabled { background-color: #cbd5e1; }
# #         """)
# #         self.btn_repartition.clicked.connect(self.ouvrir_repartition)
# #         btn_layout.addWidget(self.btn_repartition)
        
# #         # ✅ Bouton Comptabilité
# #         self.btn_comptabilite = QPushButton("📒 Écritures")
# #         self.btn_comptabilite.setStyleSheet("""
# #             QPushButton {
# #                 background-color: #8b5cf6;
# #                 color: white;
# #                 padding: 8px 20px;
# #                 border-radius: 8px;
# #                 font-weight: bold;
# #             }
# #             QPushButton:hover { background-color: #7c3aed; }
# #         """)
# #         self.btn_comptabilite.clicked.connect(self.ouvrir_comptabilite)
# #         btn_layout.addWidget(self.btn_comptabilite)

# #         # ✅ Bouton Suivi
# #         self.btn_suivi = QPushButton("📈 Suivi")
# #         self.btn_suivi.setStyleSheet("""
# #             QPushButton {
# #                 background-color: #3b82f6;
# #                 color: white;
# #                 padding: 8px 20px;
# #                 border-radius: 8px;
# #                 font-weight: bold;
# #             }
# #             QPushButton:hover { background-color: #2563eb; }
# #         """)
# #         self.btn_suivi.clicked.connect(self.ouvrir_suivi)
# #         btn_layout.addWidget(self.btn_suivi)

# #         btn_layout.addStretch()
# #         layout.addLayout(btn_layout)
    
# #     def load_data(self):
# #         """Charge les sinistres"""
# #         try:
# #             self.sinistre_combo.clear()
# #             self.sinistre_combo.addItem("📋 Tous les sinistres", None)   # ✅ Ajout
# #             sinistres = self.controller.get_sinistres_recents()
# #             for s in sinistres:
# #                 self.sinistre_combo.addItem(
# #                     f"{s.get('numero_sinistre')} - {s.get('branche', '')}",
# #                     s.get('id')
# #                 )
            
# #             # ✅ Charger les alertes
# #             self._charger_alertes()
# #         except Exception as e:
# #             print(f"Erreur chargement sinistres: {e}")
    
# #     def on_sinistre_changed(self, index):
# #         """Charge les données du sinistre sélectionné"""
# #         if index > 0:
# #             sinistre_id = self.sinistre_combo.currentData()
# #             if sinistre_id:
# #                 self.current_sinistre_id = sinistre_id
# #                 self.load_recours(sinistre_id)
 
# #     def load_recours(self, sinistre_id: int):
# #         """Charge les recours d'un sinistre"""
# #         try:
# #             recours = self.controller.get_recours_by_sinistre(sinistre_id)
# #             self.table_recours.setRowCount(len(recours))
            
# #             total = len(recours)
# #             aboutis = sum(1 for r in recours if r.get('statut') in ['ABOUTI', 'ENCAISSE', 'PAYE', 'COMPTABILISE', 'CLOTURE'])
# #             encours = total - aboutis
            
# #             total_reclame = sum(r.get('montant_reclame', 0) for r in recours)
# #             total_encaisse = sum(r.get('montant_encaisse', 0) for r in recours)
# #             taux = (total_encaisse / total_reclame * 100) if total_reclame > 0 else 0
            
# #             self.lbl_total.setText(f"Total recours: {total}")
# #             self.lbl_aboutis.setText(f"✅ Aboutis: {aboutis}")
# #             self.lbl_encours.setText(f"🟡 En cours: {encours}")
# #             self.lbl_taux_recup.setText(f"📊 Taux récupération: {taux:.1f}%")
            
# #             statut_colors = {
# #                 'OUVERT': '#f59e0b',
# #                 'EN_INSTRUCTION': '#3b82f6',
# #                 'RELANCE': '#8b5cf6',
# #                 'CONTESTE': '#ef4444',
# #                 'REFUSE': '#ef4444',
# #                 'ABOUTI': '#06b6d4',
# #                 'EN_ATTENTE_ENCAISSEMENT': '#f97316',
# #                 'PARTIELLEMENT_ENCAISSE': '#f97316',
# #                 'ENCAISSE': '#22c55e',
# #                 'REVERSEMENT_EN_COURS': '#8b5cf6',
# #                 'PAYE': '#22c55e',
# #                 'COMPTABILISE': '#22c55e',
# #                 'CLOTURE': '#64748b'
# #             }
            
# #             for i, rec in enumerate(recours):
# #                 self.table_recours.setItem(i, 0, QTableWidgetItem(rec.get('numero_recours', '')))
# #                 self.table_recours.setItem(i, 1, QTableWidgetItem(rec.get('debiteur_nom', '')))
# #                 self.table_recours.setItem(i, 2, QTableWidgetItem(f"{rec.get('montant_reclame', 0):,.0f}"))
# #                 self.table_recours.setItem(i, 3, QTableWidgetItem(f"{rec.get('montant_accepte', 0):,.0f}" if rec.get('montant_accepte') else '-'))
# #                 self.table_recours.setItem(i, 4, QTableWidgetItem(f"{rec.get('montant_encaisse', 0):,.0f}"))
# #                 self.table_recours.setItem(i, 5, QTableWidgetItem(f"{rec.get('solde', 0):,.0f}"))
                
# #                 # ✅ Ajouter la date de prochaine relance
# #                 prochaine = rec.get('date_prochaine_relance', '')
# #                 if prochaine:
# #                     date_obj = datetime.fromisoformat(prochaine[:10])
# #                     if date_obj.date() <= datetime.now().date():
# #                         prochaine_display = f"⚠️ {prochaine[:10]}"
# #                     else:
# #                         prochaine_display = prochaine[:10]
# #                 else:
# #                     prochaine_display = "-"
# #                 self.table_recours.setItem(i, 6, QTableWidgetItem(prochaine_display))
                
# #                 statut = rec.get('statut', '')
# #                 statut_item = QTableWidgetItem(statut)
# #                 color = statut_colors.get(statut, '#64748b')
# #                 statut_item.setBackground(QColor(color))
# #                 statut_item.setForeground(QColor('white'))
# #                 self.table_recours.setItem(i, 7, statut_item)
                
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", f"Erreur chargement recours: {str(e)}")

# #     def creer_recours(self):
# #         """Crée un nouveau recours (conforme CDC Tome 6 §5)"""
# #         if not self.current_sinistre_id:
# #             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
# #             return
        
# #         # ============================================================
# #         # ✅ Vérifier les conditions préalables (CDC REC-001 à REC-003)
# #         # ============================================================
# #         conditions = self.controller.verifier_conditions_recours(self.current_sinistre_id)
        
# #         if not conditions.get('peut_creer'):
# #             QMessageBox.warning(
# #                 self,
# #                 "Condition CDC non remplie",
# #                 f"Impossible de créer un recours :\n\n"
# #                 f"{conditions.get('raison', 'Condition non remplie')}"
# #             )
# #             return
        
# #         # ============================================================
# #         # Construire les infos à passer au dialogue
# #         # ============================================================
# #         sinistre_info = {}
# #         try:
# #             from addons.sinistres.controllers.sinistre_controller import SinistreController
# #             sc = SinistreController()
# #             sc.set_current_user(self.user)
# #             sinistre_data = sc.get_sinistre(self.current_sinistre_id)
            
# #             if sinistre_data:
# #                 sinistre_info = {
# #                     'numero_sinistre': sinistre_data.get('numero_sinistre', 'N/A'),
# #                     'client_nom': sinistre_data.get('client_nom', 'N/A'),
# #                     'branche': sinistre_data.get('branche', 'N/A'),
# #                     'montant_regle': conditions.get('montant_regle', 0),
# #                     'taux_responsabilite': conditions.get('taux_responsabilite', 1),
# #                 }
# #         except Exception as e:
# #             print(f"⚠️ Erreur récupération infos sinistre: {e}")
        
# #         # ============================================================
# #         # Ouvrir le dialogue
# #         # ============================================================
# #         from addons.sinistres.views.recours_dialog import RecoursDialog
# #         dialog = RecoursDialog(
# #             sinistre_id=self.current_sinistre_id,
# #             recours_controller=self.controller,
# #             user=self.user,
# #             sinistre_info=sinistre_info,
# #             parent=self
# #         )
        
# #         dialog.recours_created.connect(self._on_recours_created)
# #         dialog.exec()


# #     def _on_recours_created(self, data: dict):
# #         """Appelé après la création d'un recours"""
# #         self.load_recours(self.current_sinistre_id)
# #         QMessageBox.information(
# #             self,
# #             "Succès",
# #             f"✅ Recours créé avec succès !"
# #         )

# #     def get_reglements_by_sinistre(self, sinistre_id: int) -> List[dict]:
# #         """Récupère les règlements d'un sinistre"""
# #         try:
# #             from addons.sinistres.controllers.reglement_controller import ReglementController
# #             rc = ReglementController()
# #             rc.set_current_user(self.user)
# #             return rc.get_reglements_by_sinistre(sinistre_id)
# #         except Exception as e:
# #             print(f"Erreur chargement règlements: {e}")
# #             return []

# #     def encaisser_recours(self):
# #         """Enregistre un encaissement pour le recours sélectionné"""
# #         row = self.table_recours.currentRow()
# #         if row < 0:
# #             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
# #             return
        
# #         recours_numero = self.table_recours.item(row, 0).text()
# #         statut = self.table_recours.item(row, 7).text()
        
# #         # Vérifier que le recours peut être encaissé
# #         if statut not in ["EN_ATTENTE_ENCAISSEMENT", "PARTIELLEMENT_ENCAISSE"]:
# #             QMessageBox.warning(
# #                 self,
# #                 "Attention",
# #                 f"Seul un recours en attente d'encaissement peut être encaissé (statut: {statut})"
# #             )
# #             return
        
# #         try:
# #             recours_data = self.controller.get_recours_by_numero(recours_numero)
# #             if not recours_data:
# #                 QMessageBox.warning(self, "Erreur", "Recours non trouvé")
# #                 return
            
# #             recours_id = recours_data.get('id')
# #             recours_info = self.controller.get_recours(recours_id)
            
# #             from addons.sinistres.views.encaissement_dialog import EncaissementDialog
# #             dialog = EncaissementDialog(
# #                 recours_id=recours_id,
# #                 recours_info=recours_info,
# #                 recours_controller=self.controller,
# #                 user=self.user,
# #                 parent=self
# #             )
            
# #             dialog.encaissement_added.connect(self._on_encaissement_added)
# #             dialog.exec()
            
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

# #     def _on_encaissement_added(self, data: dict):
# #         """Appelé après un encaissement"""
# #         self.load_recours(self.current_sinistre_id)
# #         QMessageBox.information(
# #             self,
# #             "Succès",
# #             f"✅ Encaissement de {data.get('montant', 0):,.0f} FCFA enregistré !\n"
# #             f"📊 Solde restant: {data.get('solde_restant', 0):,.0f} FCFA"
# #         )

# #     def ajouter_relance(self):
# #         """Ajoute une relance au recours sélectionné"""
# #         row = self.table_recours.currentRow()
# #         if row < 0:
# #             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
# #             return
        
# #         recours_numero = self.table_recours.item(row, 0).text()
        
# #         try:
# #             recours_data = self.controller.get_recours_by_numero(recours_numero)
# #             if not recours_data:
# #                 QMessageBox.warning(self, "Erreur", "Recours non trouvé")
# #                 return
            
# #             recours_id = recours_data.get('id')
# #             recours_info = self.controller.get_recours(recours_id)
            
# #             from addons.sinistres.views.relance_dialog import RelanceDialog
# #             dialog = RelanceDialog(
# #                 recours_id=recours_id,
# #                 recours_info=recours_info,
# #                 recours_controller=self.controller,
# #                 user=self.user,
# #                 parent=self
# #             )
            
# #             dialog.relance_added.connect(self._on_relance_added)
# #             dialog.exec()
            
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

# #     def _on_relance_added(self, data: dict):
# #         """Appelé après l'ajout d'une relance"""
# #         self.load_recours(self.current_sinistre_id)
# #         QMessageBox.information(
# #             self,
# #             "Succès",
# #             f"✅ Relance ajoutée avec succès !\n"
# #             f"📅 Prochaine relance: {data.get('prochaine_relance', 'Non planifiée')}"
# #         )

# #     def planifier_relances_auto(self):
# #         """Planifie automatiquement les relances"""
# #         reply = QMessageBox.question(
# #             self,
# #             "Confirmation",
# #             "Voulez-vous planifier automatiquement les relances pour tous les recours ?",
# #             QMessageBox.Yes | QMessageBox.No
# #         )
        
# #         if reply == QMessageBox.Yes:
# #             try:
# #                 result = self.controller.planifier_relances_auto()
# #                 QMessageBox.information(
# #                     self,
# #                     "Planification terminée",
# #                     f"✅ {result.get('planifiees', 0)} relances planifiées\n"
# #                     f"❌ {result.get('erreurs', 0)} erreurs"
# #                 )
# #                 self.load_recours(self.current_sinistre_id)
# #             except Exception as e:
# #                 QMessageBox.critical(self, "Erreur", str(e))

# #     def _on_recours_cell_clicked(self, row: int, col: int):
# #         """Gère le clic sur une ligne de recours"""
# #         rec_numero = self.table_recours.item(row, 0).text()
# #         try:
# #             rec_data = self.controller.get_recours_by_numero(rec_numero)
# #             if rec_data:
# #                 self.selected_recours_id = rec_data.get('id')
# #         except:
# #             pass
# #         self.table_recours.selectRow(row)

# #     def get_selected_recours_id(self) -> Optional[int]:
# #         """Retourne l'ID du recours sélectionné"""
# #         row = self.table_recours.currentRow()
# #         if row >= 0:
# #             rec_numero = self.table_recours.item(row, 0).text()
# #             try:
# #                 rec_data = self.controller.get_recours_by_numero(rec_numero)
# #                 if rec_data:
# #                     return rec_data.get('id')
# #             except:
# #                 pass
# #         return None

# #     # ============================================================
# #     # ✅ ALERTES
# #     # ============================================================
    
# #     def _charger_alertes(self):
# #         """Charge les alertes recours"""
# #         try:
# #             alertes = self.controller.get_alertes_recours()
# #             self.alertes_widget.set_alertes(alertes)
# #         except Exception as e:
# #             print(f"❌ Erreur chargement alertes : {e}")
    
# #     def _on_alerte_clicked(self, alerte: dict):
# #         """Gère le clic sur une alerte"""
# #         recours_id = alerte.get('recours_id')
# #         if not recours_id:
# #             return
        
# #         # Sélectionner la ligne correspondante dans le tableau
# #         for i in range(self.table_recours.rowCount()):
# #             num_item = self.table_recours.item(i, 0)
# #             if not num_item:
# #                 continue
# #             try:
# #                 rec = self.controller.get_recours_by_numero(num_item.text())
# #                 if rec and rec.get('id') == recours_id:
# #                     self.table_recours.selectRow(i)
# #                     break
# #             except Exception:
# #                 continue

# #     # ============================================================
# #     # MENU CONTEXTUEL DU TABLEAU
# #     # ============================================================

# #     def _show_table_context_menu(self, position):
# #         """Affiche le menu contextuel au clic droit sur une ligne"""
# #         row = self.table_recours.currentRow()
# #         if row < 0:
# #             return
        
# #         # Récupérer les données du recours
# #         recours_numero = self.table_recours.item(row, 0).text()
        
# #         try:
# #             recours_data = self.controller.get_recours_by_numero(recours_numero)
# #             if not recours_data:
# #                 return
# #         except Exception as e:
# #             print(f"❌ Erreur récupération recours: {e}")
# #             return
        
# #         statut = recours_data.get('statut', '')
        
# #         # Créer le menu
# #         menu = QMenu(self)
# #         menu.setStyleSheet("""
# #             QMenu {
# #                 background-color: #ffffff;
# #                 border: 1px solid #e2e8f0;
# #                 border-radius: 8px;
# #                 padding: 6px;
# #             }
# #             QMenu::item {
# #                 background-color: transparent;
# #                 padding: 8px 24px 8px 16px;
# #                 border-radius: 5px;
# #                 font-size: 12px;
# #                 color: #1e293b;
# #             }
# #             QMenu::item:selected {
# #                 background-color: #f1f5f9;
# #                 color: #1a73e8;
# #             }
# #             QMenu::item:disabled {
# #                 color: #94a3b8;
# #             }
# #             QMenu::separator {
# #                 height: 1px;
# #                 background-color: #e2e8f0;
# #                 margin: 4px 8px;
# #             }
# #         """)
        
# #         # ============================================================
# #         # SECTION 1 : CONSULTATION (toujours)
# #         # ============================================================
        
# #         action_suivi = QAction("📈  Voir le suivi complet", self)
# #         action_suivi.triggered.connect(lambda: self._action_suivi_from_menu(recours_numero))
# #         menu.addAction(action_suivi)
        
# #         action_details = QAction("👁️  Voir les détails", self)
# #         action_details.triggered.connect(lambda: self._action_details_from_menu(recours_data))
# #         menu.addAction(action_details)
        
# #         menu.addSeparator()
        
# #         # ============================================================
# #         # SECTION 2 : ACTIONS MÉTIER (selon statut)
# #         # ============================================================
        
# #         # -- Encaisser (si statut le permet)
# #         if statut in ["EN_ATTENTE_ENCAISSEMENT", "PARTIELLEMENT_ENCAISSE"]:
# #             if self.permissions_ui.peut('recours', 'UPDATE'):
# #                 action_encaisser = QAction("💰  Encaisser", self)
# #                 action_encaisser.triggered.connect(lambda: self._action_encaisser_from_menu(recours_numero))
# #                 menu.addAction(action_encaisser)
        
# #         # -- Relancer (si statut le permet)
# #         if statut in ["OUVERT", "EN_INSTRUCTION", "RELANCE", "CONTESTE"]:
# #             if self.permissions_ui.peut('recours', 'UPDATE'):
# #                 action_relancer = QAction("🔔  Relancer", self)
# #                 action_relancer.triggered.connect(lambda: self._action_relancer_from_menu(recours_numero))
# #                 menu.addAction(action_relancer)
        
# #         # -- Répartition (si encaissé)
# #         if statut in ["ENCAISSE", "PARTIELLEMENT_ENCAISSE", "REVERSEMENT_EN_COURS"]:
# #             if self.permissions_ui.peut('recours', 'UPDATE'):
# #                 action_repartition = QAction("📊  Répartition", self)
# #                 action_repartition.triggered.connect(lambda: self._action_repartition_from_menu(recours_numero))
# #                 menu.addAction(action_repartition)
        
# #         # -- Reversements (si encaissé)
# #         if statut in ["ENCAISSE", "REVERSEMENT_EN_COURS", "PAYE"]:
# #             if self.permissions_ui.peut('recours', 'UPDATE'):
# #                 action_reversement = QAction("💸  Reversements", self)
# #                 action_reversement.triggered.connect(lambda: self._action_reversements_from_menu(recours_numero))
# #                 menu.addAction(action_reversement)
        
# #         # -- Écritures comptables (toujours)
# #         if self.permissions_ui.peut('recours', 'READ'):
# #             action_ecritures = QAction("📒  Écritures comptables", self)
# #             action_ecritures.triggered.connect(lambda: self._action_ecritures_from_menu(recours_numero))
# #             menu.addAction(action_ecritures)
        
# #         menu.addSeparator()
        
# #         # ============================================================
# #         # SECTION 3 : CLÔTURE / ANNULATION
# #         # ============================================================
        
# #         # -- Clôturer (si pas déjà clôturé)
# #         if statut not in ["CLOTURE", "REFUSE"]:
# #             if self.permissions_ui.peut('recours', 'VALIDATE'):
# #                 action_cloturer = QAction("🔒  Clôturer", self)
# #                 action_cloturer.triggered.connect(lambda: self._action_cloturer_from_menu(recours_data))
# #                 menu.addAction(action_cloturer)
        
# #         # -- Annuler (si pas déjà annulé/clôturé)
# #         if statut not in ["CLOTURE", "REFUSE", "ANNULE"]:
# #             if self.permissions_ui.peut('recours', 'DELETE'):
# #                 action_annuler = QAction("🚫  Annuler", self)
# #                 action_annuler.triggered.connect(lambda: self._action_annuler_from_menu(recours_data))
# #                 menu.addAction(action_annuler)
        
# #         # ============================================================
# #         # SECTION 4 : UTILITAIRES
# #         # ============================================================
        
# #         menu.addSeparator()
        
# #         action_copy = QAction("📋  Copier le N° de recours", self)
# #         action_copy.triggered.connect(lambda: self._copy_to_clipboard(recours_numero))
# #         menu.addAction(action_copy)
        
# #         # ============================================================
# #         # AFFICHER LE MENU
# #         # ============================================================
        
# #         menu.exec(self.table_recours.viewport().mapToGlobal(position))
    
# #     # ============================================================
# #     # ✅ RÉPARTITION
# #     # ============================================================
    
# #     def ouvrir_suivi(self):
# #         """Ouvre le dialogue de suivi complet du recours"""
# #         row = self.table_recours.currentRow()
# #         if row < 0:
# #             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
# #             return
        
# #         recours_numero = self.table_recours.item(row, 0).text()
        
# #         try:
# #             recours_data = self.controller.get_recours_by_numero(recours_numero)
# #             if not recours_data:
# #                 QMessageBox.warning(self, "Erreur", "Recours non trouvé")
# #                 return
            
# #             from addons.sinistres.views.recours_suivi_dialog import RecoursSuiviDialog
            
# #             dialog = RecoursSuiviDialog(
# #                 recours_id=recours_data.get('id'),
# #                 recours_info=recours_data,
# #                 recours_controller=self.controller,
# #                 comptabilite_controller=self.comptabilite_controller,
# #                 user=self.user,
# #                 parent=self,
# #             )
# #             dialog.exec()
        
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

# #     def ouvrir_repartition(self):
# #         """Ouvre le dialogue de répartition"""
# #         row = self.table_recours.currentRow()
# #         if row < 0:
# #             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
# #             return
        
# #         recours_numero = self.table_recours.item(row, 0).text()
# #         statut = self.table_recours.item(row, 7).text()
        
# #         # Vérifier que le recours peut être réparti
# #         if statut not in ["ENCAISSE", "PARTIELLEMENT_ENCAISSE"]:
# #             QMessageBox.warning(
# #                 self,
# #                 "Attention",
# #                 f"Seul un recours encaissé peut être réparti (statut: {statut})"
# #             )
# #             return
        
# #         try:
# #             recours_data = self.controller.get_recours_by_numero(recours_numero)
# #             if not recours_data:
# #                 QMessageBox.warning(self, "Erreur", "Recours non trouvé")
# #                 return
            
# #             dialog = RepartitionRecoursDialog(
# #                 recours_id=recours_data.get('id'),
# #                 recours_info=recours_data,
# #                 recours_controller=self.controller,
# #                 user=self.user,
# #                 parent=self,
# #             )
# #             dialog.repartition_validee.connect(self._on_repartition_validee)
# #             dialog.exec()
        
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
# #     def _on_repartition_validee(self, repartitions: list):
# #         """Appelé après validation de la répartition"""
# #         self.load_recours(self.current_sinistre_id)
# #         QMessageBox.information(
# #             self,
# #             "Succès",
# #             f"✅ Répartition enregistrée : {len(repartitions)} part(s)"
# #         )
    
# #     # ============================================================
# #     # ✅ COMPTABILITÉ
# #     # ============================================================
    
# #     def ouvrir_comptabilite(self):
# #         """Ouvre le dialogue des écritures comptables"""
# #         row = self.table_recours.currentRow()
# #         if row < 0:
# #             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
# #             return
        
# #         recours_numero = self.table_recours.item(row, 0).text()
        
# #         try:
# #             recours_data = self.controller.get_recours_by_numero(recours_numero)
# #             if not recours_data:
# #                 QMessageBox.warning(self, "Erreur", "Recours non trouvé")
# #                 return
            
# #             dialog = ComptabiliteRecoursDialog(
# #                 recours_id=recours_data.get('id'),
# #                 recours_info=recours_data,
# #                 comptabilite_controller=self.comptabilite_controller,
# #                 user=self.user,
# #                 parent=self,
# #             )
# #             dialog.exec()
        
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

# #     # ============================================================
# #     # ACTIONS DU MENU CONTEXTUEL
# #     # ============================================================

# #     def _action_suivi_from_menu(self, recours_numero: str):
# #         """Ouvre le suivi complet depuis le menu contextuel"""
# #         try:
# #             recours_data = self.controller.get_recours_by_numero(recours_numero)
# #             if not recours_data:
# #                 QMessageBox.warning(self, "Erreur", "Recours non trouvé")
# #                 return
            
# #             from addons.sinistres.views.recours_suivi_dialog import RecoursSuiviDialog
# #             dialog = RecoursSuiviDialog(
# #                 recours_id=recours_data.get('id'),
# #                 recours_info=recours_data,
# #                 recours_controller=self.controller,
# #                 comptabilite_controller=self.comptabilite_controller,
# #                 user=self.user,
# #                 parent=self,
# #             )
# #             dialog.exec()
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

# #     def _action_details_from_menu(self, recours_data: dict):
# #         """Affiche les détails d'un recours"""
# #         QMessageBox.information(
# #             self,
# #             f"Recours {recours_data.get('numero_recours', 'N/A')}",
# #             f"📌 Type: {recours_data.get('type_recours', 'N/A')}\n"
# #             f"👤 Débiteur: {recours_data.get('debiteur_nom', 'N/A')}\n"
# #             f"💰 Montant réclamé: {float(recours_data.get('montant_reclame', 0)):,.0f} FCFA\n"
# #             f"✅ Montant accepté: {float(recours_data.get('montant_accepte', 0) or 0):,.0f} FCFA\n"
# #             f"💵 Montant encaissé: {float(recours_data.get('montant_encaisse', 0) or 0):,.0f} FCFA\n"
# #             f"📊 Solde: {float(recours_data.get('solde', 0) or 0):,.0f} FCFA\n"
# #             f"📅 Date ouverture: {recours_data.get('date_ouverture', '')[:10]}\n"
# #             f"📌 Statut: {recours_data.get('statut', 'N/A')}\n"
# #             f"👤 Responsable: {recours_data.get('responsable_id', 'N/A')}"
# #         )

# #     def _action_encaisser_from_menu(self, recours_numero: str):
# #         """Ouvre le dialogue d'encaissement"""
# #         # Sélectionner la ligne
# #         for i in range(self.table_recours.rowCount()):
# #             if self.table_recours.item(i, 0).text() == recours_numero:
# #                 self.table_recours.selectRow(i)
# #                 break
# #         self.encaisser_recours()

# #     def _action_relancer_from_menu(self, recours_numero: str):
# #         """Ouvre le dialogue de relance"""
# #         for i in range(self.table_recours.rowCount()):
# #             if self.table_recours.item(i, 0).text() == recours_numero:
# #                 self.table_recours.selectRow(i)
# #                 break
# #         self.ajouter_relance()

# #     def _action_repartition_from_menu(self, recours_numero: str):
# #         """Ouvre le dialogue de répartition"""
# #         for i in range(self.table_recours.rowCount()):
# #             if self.table_recours.item(i, 0).text() == recours_numero:
# #                 self.table_recours.selectRow(i)
# #                 break
# #         self.ouvrir_repartition()

# #     def _action_reversements_from_menu(self, recours_numero: str):
# #         """Ouvre le dialogue des reversements"""
# #         try:
# #             recours_data = self.controller.get_recours_by_numero(recours_numero)
# #             if not recours_data:
# #                 return
            
# #             recours_info = self.controller.get_recours(recours_data.get('id'))
            
# #             from addons.sinistres.views.reviser_evaluation_dialog import ReviserEvaluationDialog
# #             dialog = ReviserEvaluationDialog(
# #                 recours_id=recours_data.get('id'),
# #                 recours_info=recours_info,
# #                 recours_controller=self.controller,
# #                 user=self.user,
# #                 parent=self,
# #             )
# #             dialog.exec()
# #             self.load_recours(self.current_sinistre_id)
# #         except ImportError:
# #             QMessageBox.information(
# #                 self, "Info",
# #                 "Le dialogue de reversement n'est pas encore disponible.\n"
# #                 "Fonctionnalité à venir."
# #             )
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

# #     def _action_ecritures_from_menu(self, recours_numero: str):
# #         """Ouvre le dialogue des écritures comptables"""
# #         for i in range(self.table_recours.rowCount()):
# #             if self.table_recours.item(i, 0).text() == recours_numero:
# #                 self.table_recours.selectRow(i)
# #                 break
# #         self.ouvrir_comptabilite()

# #     def _action_cloturer_from_menu(self, recours_data: dict):
# #         """Clôture un recours"""
# #         recours_numero = recours_data.get('numero_recours', 'N/A')
        
# #         # Demander le motif
# #         from PySide6.QtWidgets import QInputDialog
# #         motif, ok = QInputDialog.getMultiLineText(
# #             self,
# #             f"Clôturer le recours {recours_numero}",
# #             "Motif de clôture (obligatoire) :",
# #             ""
# #         )
        
# #         if not ok or not motif.strip():
# #             return
        
# #         reply = QMessageBox.question(
# #             self,
# #             "Confirmation",
# #             f"Voulez-vous vraiment clôturer le recours {recours_numero} ?\n\n"
# #             f"Motif : {motif}",
# #             QMessageBox.Yes | QMessageBox.No
# #         )
        
# #         if reply != QMessageBox.Yes:
# #             return
        
# #         try:
# #             result = self.controller.changer_statut_recours(
# #                 recours_data.get('id'),
# #                 "CLOTURE",
# #                 motif=motif,
# #             )
# #             if result:
# #                 QMessageBox.information(self, "Succès", "Recours clôturé avec succès")
# #                 self.load_recours(self.current_sinistre_id)
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", str(e))

# #     def _action_annuler_from_menu(self, recours_data: dict):
# #         """Annule un recours"""
# #         recours_numero = recours_data.get('numero_recours', 'N/A')
        
# #         from PySide6.QtWidgets import QInputDialog
# #         motif, ok = QInputDialog.getMultiLineText(
# #             self,
# #             f"Annuler le recours {recours_numero}",
# #             "Motif d'annulation (obligatoire) :",
# #             ""
# #         )
        
# #         if not ok or not motif.strip():
# #             return
        
# #         reply = QMessageBox.question(
# #             self,
# #             "Confirmation",
# #             f"Voulez-vous vraiment annuler le recours {recours_numero} ?\n\n"
# #             f"Motif : {motif}",
# #             QMessageBox.Yes | QMessageBox.No
# #         )
        
# #         if reply != QMessageBox.Yes:
# #             return
        
# #         try:
# #             result = self.controller.changer_statut_recours(
# #                 recours_data.get('id'),
# #                 "REFUSE",
# #                 motif=motif,
# #             )
# #             if result:
# #                 QMessageBox.information(self, "Succès", "Recours annulé avec succès")
# #                 self.load_recours(self.current_sinistre_id)
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", str(e))

# #     def _copy_to_clipboard(self, text: str):
# #         """Copie un texte dans le presse-papiers"""
# #         from PySide6.QtWidgets import QApplication
# #         QApplication.clipboard().setText(text)
# #         QMessageBox.information(self, "Copié", f"✅ '{text}' copié dans le presse-papiers")


# """
# Vue principale du module LOMETA Sinistres
# Interface utilisateur complète pour la gestion des recours
# """
# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
#     QHeaderView, QLabel, QPushButton, QListWidgetItem, QStackedWidget,
#     QListWidget, QFrame, QMessageBox, QDialog, QGraphicsDropShadowEffect,
#     QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
#     QFormLayout, QGroupBox, QTabWidget, QSplitter, QScrollArea,
#     QProgressBar, QToolBar, QMenu, QCheckBox, QRadioButton, QSizePolicy,
#     QAbstractItemView
# )
# from PySide6.QtCore import Qt, QSize, Signal, Slot, QDate
# from PySide6.QtGui import QColor, QIcon, QFont, QAction, QCursor, QPainter, QBrush

# from datetime import datetime, timedelta
# from typing import Optional, List

# from addons.sinistres.views.repartition_recours_dialog import RepartitionRecoursDialog
# from addons.sinistres.views.comptabilite_recours_dialog import ComptabiliteRecoursDialog
# from addons.sinistres.views.widgets.alertes_widget import AlertesWidget
# from addons.sinistres.controllers.comptabilite_controller import ComptabiliteController


# # ═══════════════════════════════════════════════════════════════════
# # WIDGETS PERSONNALISÉS
# # ═══════════════════════════════════════════════════════════════════

# class StatCard(QFrame):
#     """Carte statistique moderne avec icône colorée"""
    
#     def __init__(self, icon, title, value, color_bg, color_fg, parent=None):
#         super().__init__(parent)
#         self.setMinimumHeight(90)
#         self.setStyleSheet(f"""
#             QFrame {{
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 12px;
#             }}
#         """)
        
#         # Ombre légère
#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(8)
#         shadow.setColor(QColor(0, 0, 0, 12))
#         shadow.setOffset(0, 2)
#         self.setGraphicsEffect(shadow)
        
#         layout = QHBoxLayout(self)
#         layout.setContentsMargins(16, 14, 16, 14)
#         layout.setSpacing(14)
        
#         # Conteneur d'icône (carré coloré)
#         icon_container = QFrame()
#         icon_container.setFixedSize(48, 48)
#         icon_container.setStyleSheet(f"""
#             QFrame {{
#                 background: {color_bg};
#                 border-radius: 10px;
#                 border: none;
#             }}
#         """)
#         icon_layout = QVBoxLayout(icon_container)
#         icon_layout.setContentsMargins(0, 0, 0, 0)
#         icon_layout.setAlignment(Qt.AlignCenter)
        
#         icon_label = QLabel(icon)
#         icon_label.setAlignment(Qt.AlignCenter)
#         icon_label.setStyleSheet(f"""
#             font-size: 22px;
#             color: {color_fg};
#             background: transparent;
#             border: none;
#         """)
#         icon_layout.addWidget(icon_label)
        
#         layout.addWidget(icon_container)
        
#         # Textes
#         text_layout = QVBoxLayout()
#         text_layout.setSpacing(2)
        
#         title_lbl = QLabel(title)
#         title_lbl.setStyleSheet("""
#             color: #64748b;
#             font-size: 12px;
#             font-weight: 500;
#             background: transparent;
#             border: none;
#         """)
        
#         value_lbl = QLabel(str(value))
#         value_lbl.setStyleSheet(f"""
#             color: {color_fg};
#             font-size: 26px;
#             font-weight: 800;
#             background: transparent;
#             border: none;
#         """)
#         value_lbl.setObjectName("stat_value")
        
#         text_layout.addWidget(title_lbl)
#         text_layout.addWidget(value_lbl)
        
#         layout.addLayout(text_layout, 1)


# class StatusBadge(QLabel):
#     """Badge de statut arrondi (pill)"""
    
#     STATUS_STYLES = {
#         'ABOUTI':       ("#d1fae5", "#065f46", "Aboutis"),
#         'ENCAISSE':     ("#d1fae5", "#065f46", "Encaissé"),
#         'PAYE':         ("#d1fae5", "#065f46", "Payé"),
#         'COMPTABILISE': ("#d1fae5", "#065f46", "Comptabilisé"),
#         'CLOTURE':      ("#e2e8f0", "#334155", "Clôturé"),
#         'EN_COURS':     ("#fed7aa", "#9a3412", "En cours"),
#         'OUVERT':       ("#fed7aa", "#9a3412", "Ouvert"),
#         'EN_INSTRUCTION': ("#fed7aa", "#9a3412", "En instruction"),
#         'RELANCE':      ("#fed7aa", "#9a3412", "Relancé"),
#         'EN_ATTENTE_ENCAISSEMENT': ("#fed7aa", "#9a3412", "En attente"),
#         'PARTIELLEMENT_ENCAISSE': ("#fed7aa", "#9a3412", "Partiel"),
#         'REVERSEMENT_EN_COURS': ("#fed7aa", "#9a3412", "Reversement"),
#         'CONTESTE':     ("#fee2e2", "#991b1b", "Contesté"),
#         'REFUSE':       ("#fee2e2", "#991b1b", "Refusé"),
#         'ANNULE':       ("#fee2e2", "#991b1b", "Annulé"),
#     }
    
#     def __init__(self, statut: str, parent=None):
#         super().__init__(parent)
        
#         bg, fg, label = self.STATUS_STYLES.get(
#             statut, ("#e2e8f0", "#475569", statut)
#         )
        
#         self.setText(f"  {label}  ")
#         self.setAlignment(Qt.AlignCenter)
#         self.setStyleSheet(f"""
#             QLabel {{
#                 background: {bg};
#                 color: {fg};
#                 border-radius: 11px;
#                 padding: 3px 8px;
#                 font-size: 11px;
#                 font-weight: 600;
#                 border: none;
#             }}
#         """)
#         self.setFixedHeight(22)
#         self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)


# # ═══════════════════════════════════════════════════════════════════
# # PAGE PRINCIPALE
# # ═══════════════════════════════════════════════════════════════════

# class RecoursPage(QWidget):
#     """Page de gestion des recours — Design moderne v2.0"""
    
#     def __init__(self, controller, user):
#         super().__init__()
#         self.controller = controller
#         self.user = user
#         self.current_sinistre_id = None
#         self.selected_recours_id = None
        
#         # Pagination
#         self._current_page = 1
#         self._per_page = 10
#         self._total_recours = 0
        
#         # Contrôleur comptabilité
#         self.comptabilite_controller = ComptabiliteController()
#         self.comptabilite_controller.set_current_user(user)
        
#         # Service de permissions
#         from addons.sinistres.services.permission_service import PermissionService
#         from addons.sinistres.security.permissions_helper import PermissionsUI
#         self.permission_service = PermissionService()
#         self.permissions_ui = PermissionsUI(user, self.permission_service)
        
#         self.setup_ui()
#         self._appliquer_permissions()
#         self.load_data()
    
#     def _appliquer_permissions(self):
#         """Applique les permissions sur les boutons"""
#         self.permissions_ui.masquer_si_non_autorise(
#             self.btn_creer_rec, 'recours', 'CREATE'
#         )
#         self.permissions_ui.masquer_si_non_autorise(
#             self.btn_planifier, 'recours', 'UPDATE'
#         )
#         self.permissions_ui.masquer_si_non_autorise(
#             self.btn_repartition, 'recours', 'UPDATE'
#         )
#         self.permissions_ui.masquer_si_non_autorise(
#             self.btn_comptabilite, 'recours', 'READ'
#         )
    
#     # ═══════════════════════════════════════════════════════════════
#     # CONSTRUCTION DE L'INTERFACE
#     # ═══════════════════════════════════════════════════════════════
    
#     def setup_ui(self):
#         # Fond gris clair
#         self.setStyleSheet("background: #f1f5f9;")
        
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(24, 20, 24, 20)
#         layout.setSpacing(16)
        
#         # ─── 1. HEADER (titre + bouton nouveau) ───
#         layout.addWidget(self._build_header())
        
#         # ─── 2. CARTES STATISTIQUES ───
#         layout.addWidget(self._build_stats_row())
        
#         # ─── 3. ALERTES (conservées, mais discrètes) ───
#         self.alertes_widget = AlertesWidget()
#         self.alertes_widget.alerte_clicked.connect(self._on_alerte_clicked)
#         layout.addWidget(self.alertes_widget)
        
#         # ─── 4. TABLE CARD ───
#         layout.addWidget(self._build_table_card(), 1)
        
#         # ─── 5. BARRE D'ACTIONS SECONDAIRES ───
#         layout.addWidget(self._build_secondary_actions())
    
#     def _build_header(self):
#         """En-tête : titre + bouton Nouveau Recours"""
#         frame = QFrame()
#         frame.setStyleSheet("background: transparent; border: none;")
#         layout = QHBoxLayout(frame)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(12)
        
#         # Titre
#         title = QLabel("Gestion des Recours")
#         title.setStyleSheet("""
#             font-size: 26px;
#             font-weight: 800;
#             color: #0f172a;
#             background: transparent;
#         """)
#         layout.addWidget(title)
        
#         layout.addStretch()
        
#         # Filtre sinistre (discret)
#         sinistre_label = QLabel("Sinistre :")
#         sinistre_label.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
#         layout.addWidget(sinistre_label)
        
#         self.sinistre_combo = QComboBox()
#         self.sinistre_combo.setMinimumWidth(200)
#         self.sinistre_combo.setStyleSheet("""
#             QComboBox {
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 6px 10px;
#                 font-size: 12px;
#                 color: #1e293b;
#             }
#             QComboBox:hover { border-color: #3b82f6; }
#             QComboBox::drop-down { border: none; width: 20px; }
#             QComboBox::down-arrow {
#                 image: none;
#                 border-left: 4px solid transparent;
#                 border-right: 4px solid transparent;
#                 border-top: 5px solid #64748b;
#                 margin-right: 6px;
#             }
#         """)
#         self.sinistre_combo.currentIndexChanged.connect(self.on_sinistre_changed)
#         layout.addWidget(self.sinistre_combo)
        
#         # Bouton refresh
#         self.btn_refresh = QPushButton("🔄")
#         self.btn_refresh.setFixedSize(34, 34)
#         self.btn_refresh.setCursor(Qt.PointingHandCursor)
#         self.btn_refresh.setToolTip("Actualiser")
#         self.btn_refresh.setStyleSheet("""
#             QPushButton {
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 font-size: 14px;
#             }
#             QPushButton:hover { background: #f8fafc; border-color: #cbd5e1; }
#         """)
#         self.btn_refresh.clicked.connect(self.load_data)
#         layout.addWidget(self.btn_refresh)
        
#         # Bouton Nouveau Recours (principal)
#         self.btn_creer_rec = QPushButton("  +  Nouveau Recours")
#         self.btn_creer_rec.setCursor(Qt.PointingHandCursor)
#         self.btn_creer_rec.setFixedHeight(38)
#         self.btn_creer_rec.setStyleSheet("""
#             QPushButton {
#                 background: #2563eb;
#                 color: white;
#                 border: none;
#                 border-radius: 8px;
#                 padding: 8px 18px;
#                 font-size: 13px;
#                 font-weight: 700;
#             }
#             QPushButton:hover { background: #1d4ed8; }
#             QPushButton:pressed { background: #1e40af; }
#         """)
#         self.btn_creer_rec.clicked.connect(self.creer_recours)
#         layout.addWidget(self.btn_creer_rec)
        
#         return frame
    
#     def _build_stats_row(self):
#         """Rangée de 4 cartes statistiques"""
#         wrapper = QWidget()
#         wrapper.setStyleSheet("background: transparent;")
#         layout = QHBoxLayout(wrapper)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(14)
        
#         # 4 cartes
#         self.card_total = StatCard(
#             icon="📁", title="Total Recours", value="0",
#             color_bg="#dbeafe", color_fg="#1e40af"
#         )
#         self.card_aboutis = StatCard(
#             icon="✓", title="Aboutis", value="0",
#             color_bg="#d1fae5", color_fg="#059669"
#         )
#         self.card_encours = StatCard(
#             icon="⏱", title="En cours", value="0",
#             color_bg="#fed7aa", color_fg="#ea580c"
#         )
#         self.card_attente = StatCard(
#             icon="⚠", title="En attente", value="0",
#             color_bg="#f1f5f9", color_fg="#475569"
#         )
        
#         layout.addWidget(self.card_total)
#         layout.addWidget(self.card_aboutis)
#         layout.addWidget(self.card_encours)
#         layout.addWidget(self.card_attente)
        
#         return wrapper
    
#     def _build_table_card(self):
#         """Carte contenant le tableau avec header intégré"""
#         card = QFrame()
#         card.setStyleSheet("""
#             QFrame {
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 14px;
#             }
#         """)
        
#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(12)
#         shadow.setColor(QColor(0, 0, 0, 15))
#         shadow.setOffset(0, 2)
#         card.setGraphicsEffect(shadow)
        
#         layout = QVBoxLayout(card)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(0)
        
#         # ─── Header de la carte ───
#         header = QFrame()
#         header.setStyleSheet("""
#             QFrame {
#                 background: transparent;
#                 border: none;
#                 border-bottom: 1px solid #f1f5f9;
#             }
#         """)
#         header_layout = QHBoxLayout(header)
#         header_layout.setContentsMargins(20, 16, 20, 16)
#         header_layout.setSpacing(10)
        
#         title = QLabel("Liste des Recours")
#         title.setStyleSheet("""
#             font-size: 16px;
#             font-weight: 700;
#             color: #0f172a;
#             background: transparent;
#         """)
#         header_layout.addWidget(title)
#         header_layout.addStretch()
        
#         # Recherche
#         self.search_input = QLineEdit()
#         self.search_input.setPlaceholderText("Recherche")
#         self.search_input.setFixedWidth(220)
#         self.search_input.setStyleSheet("""
#             QLineEdit {
#                 background: #f8fafc;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 6px 12px;
#                 font-size: 12px;
#                 color: #1e293b;
#             }
#             QLineEdit:focus {
#                 border-color: #3b82f6;
#                 background: white;
#             }
#         """)
#         self.search_input.textChanged.connect(self._on_search_changed)
#         header_layout.addWidget(self.search_input)
        
#         # Bouton Filtre
#         btn_filter = QPushButton("  ⚙  Filtrer")
#         btn_filter.setCursor(Qt.PointingHandCursor)
#         btn_filter.setStyleSheet("""
#             QPushButton {
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 6px 14px;
#                 font-size: 12px;
#                 color: #1e293b;
#                 font-weight: 500;
#             }
#             QPushButton:hover { background: #f8fafc; border-color: #cbd5e1; }
#         """)
#         header_layout.addWidget(btn_filter)
        
#         # Bouton Date picker
#         self.date_picker = QDateEdit()
#         self.date_picker.setCalendarPopup(True)
#         self.date_picker.setDisplayFormat("dd MMM yyyy")
#         self.date_picker.setDate(QDate.currentDate())
#         self.date_picker.setStyleSheet("""
#             QDateEdit {
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 6px 10px;
#                 font-size: 12px;
#                 color: #1e293b;
#                 min-width: 130px;
#             }
#             QDateEdit:hover { border-color: #3b82f6; }
#             QDateEdit::drop-down { border: none; width: 18px; }
#         """)
#         header_layout.addWidget(self.date_picker)
        
#         # Bouton Export
#         btn_export = QPushButton("  ⬇  Export")
#         btn_export.setCursor(Qt.PointingHandCursor)
#         btn_export.setStyleSheet("""
#             QPushButton {
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 6px 14px;
#                 font-size: 12px;
#                 color: #1e293b;
#                 font-weight: 500;
#             }
#             QPushButton:hover { background: #f8fafc; border-color: #cbd5e1; }
#         """)
#         btn_export.clicked.connect(self._export_data)
#         header_layout.addWidget(btn_export)
        
#         layout.addWidget(header)
        
#         # ─── Tableau ───
#         self.table_recours = QTableWidget()
#         self.table_recours.setColumnCount(8)
#         self.table_recours.setHorizontalHeaderLabels([
#             "N° Recours", "Client", "Assuré", "Date Création",
#             "Statut", "Montant", "Gestionnaire", "Actions"
#         ])
        
#         # Style du tableau
#         self.table_recours.setStyleSheet("""
#             QTableWidget {
#                 background: white;
#                 border: none;
#                 gridline-color: transparent;
#                 outline: none;
#             }
#             QTableWidget::item {
#                 padding: 12px 8px;
#                 border-bottom: 1px solid #f1f5f9;
#                 color: #1e293b;
#                 font-size: 12px;
#             }
#             QTableWidget::item:selected {
#                 background: #eff6ff;
#                 color: #1e293b;
#             }
#             QTableWidget::item:hover {
#                 background: #f8fafc;
#             }
#             QHeaderView::section {
#                 background: #f8fafc;
#                 padding: 12px 8px;
#                 font-weight: 600;
#                 font-size: 12px;
#                 color: #475569;
#                 border: none;
#                 border-bottom: 1px solid #e2e8f0;
#                 border-top: 1px solid #f1f5f9;
#             }
#             QScrollBar:vertical {
#                 background: transparent;
#                 width: 8px;
#                 margin: 0;
#             }
#             QScrollBar::handle:vertical {
#                 background: #cbd5e1;
#                 border-radius: 4px;
#                 min-height: 30px;
#             }
#             QScrollBar::handle:vertical:hover { background: #94a3b8; }
#             QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
#         """)
        
#         self.table_recours.setAlternatingRowColors(False)
#         self.table_recours.verticalHeader().setVisible(False)
#         self.table_recours.verticalHeader().setDefaultSectionSize(52)
#         self.table_recours.setSelectionBehavior(QAbstractItemView.SelectRows)
#         self.table_recours.setSelectionMode(QAbstractItemView.SingleSelection)
#         self.table_recours.setEditTriggers(QAbstractItemView.NoEditTriggers)
#         self.table_recours.setShowGrid(False)
        
#         # Largeurs des colonnes
#         header_view = self.table_recours.horizontalHeader()
#         header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # N°
#         header_view.setSectionResizeMode(1, QHeaderView.Stretch)           # Client
#         header_view.setSectionResizeMode(2, QHeaderView.Stretch)           # Assuré
#         header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Date
#         header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Statut
#         header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Montant
#         header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Gestionnaire
#         header_view.setSectionResizeMode(7, QHeaderView.Fixed)             # Actions
#         self.table_recours.setColumnWidth(7, 60)
        
#         # Clic sur ligne
#         self.table_recours.cellClicked.connect(self._on_recours_cell_clicked)
        
#         layout.addWidget(self.table_recours)
        
#         # ─── Pagination en bas ───
#         pagination = QFrame()
#         pagination.setStyleSheet("""
#             QFrame {
#                 background: transparent;
#                 border: none;
#                 border-top: 1px solid #f1f5f9;
#             }
#         """)
#         pag_layout = QHBoxLayout(pagination)
#         pag_layout.setContentsMargins(20, 12, 20, 12)
#         pag_layout.setSpacing(10)
        
#         pag_layout.addStretch()
        
#         self.lbl_pagination = QLabel("0-0 de 0")
#         self.lbl_pagination.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
#         pag_layout.addWidget(self.lbl_pagination)
        
#         self.btn_prev = QPushButton("◀ Précédent")
#         self.btn_prev.setCursor(Qt.PointingHandCursor)
#         self.btn_prev.setStyleSheet("""
#             QPushButton {
#                 background: transparent;
#                 border: none;
#                 color: #3b82f6;
#                 font-size: 12px;
#                 font-weight: 600;
#                 padding: 4px 8px;
#             }
#             QPushButton:hover { color: #1d4ed8; text-decoration: underline; }
#             QPushButton:disabled { color: #cbd5e1; text-decoration: none; }
#         """)
#         self.btn_prev.clicked.connect(self._go_prev_page)
#         pag_layout.addWidget(self.btn_prev)
        
#         self.btn_next = QPushButton("Suivant ▶")
#         self.btn_next.setCursor(Qt.PointingHandCursor)
#         self.btn_next.setStyleSheet("""
#             QPushButton {
#                 background: transparent;
#                 border: none;
#                 color: #3b82f6;
#                 font-size: 12px;
#                 font-weight: 600;
#                 padding: 4px 8px;
#             }
#             QPushButton:hover { color: #1d4ed8; text-decoration: underline; }
#             QPushButton:disabled { color: #cbd5e1; text-decoration: none; }
#         """)
#         self.btn_next.clicked.connect(self._go_next_page)
#         pag_layout.addWidget(self.btn_next)
        
#         layout.addWidget(pagination)
        
#         return card
    
#     def _build_secondary_actions(self):
#         """Barre d'actions secondaires (planifier, répartition, comptabilité)"""
#         wrapper = QWidget()
#         wrapper.setStyleSheet("background: transparent;")
#         layout = QHBoxLayout(wrapper)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(10)
        
#         # Style commun pour les boutons secondaires
#         btn_style = """
#             QPushButton {
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 8px 16px;
#                 font-size: 12px;
#                 font-weight: 600;
#                 color: #1e293b;
#             }
#             QPushButton:hover {
#                 background: #f8fafc;
#                 border-color: %s;
#                 color: %s;
#             }
#         """
        
#         self.btn_planifier = QPushButton("  📅  Planifier relances")
#         self.btn_planifier.setCursor(Qt.PointingHandCursor)
#         self.btn_planifier.setStyleSheet(btn_style % ("#8b5cf6", "#7c3aed"))
#         self.btn_planifier.clicked.connect(self.planifier_relances_auto)
#         layout.addWidget(self.btn_planifier)
        
#         self.btn_repartition = QPushButton("  📊  Répartition")
#         self.btn_repartition.setCursor(Qt.PointingHandCursor)
#         self.btn_repartition.setStyleSheet(btn_style % ("#06b6d4", "#0891b2"))
#         self.btn_repartition.clicked.connect(self.ouvrir_repartition)
#         layout.addWidget(self.btn_repartition)
        
#         self.btn_comptabilite = QPushButton("  📒  Écritures comptables")
#         self.btn_comptabilite.setCursor(Qt.PointingHandCursor)
#         self.btn_comptabilite.setStyleSheet(btn_style % ("#8b5cf6", "#7c3aed"))
#         self.btn_comptabilite.clicked.connect(self.ouvrir_comptabilite)
#         layout.addWidget(self.btn_comptabilite)
        
#         layout.addStretch()
        
#         return wrapper
    
#     # ═══════════════════════════════════════════════════════════════
#     # CHARGEMENT DES DONNÉES
#     # ═══════════════════════════════════════════════════════════════
    
#     def load_data(self):
#         """Charge les sinistres dans le combo"""
#         try:
#             self.sinistre_combo.blockSignals(True)
#             self.sinistre_combo.clear()
#             self.sinistre_combo.addItem("📋 Tous les sinistres", None)
            
#             sinistres = self.controller.get_sinistres_recents()
#             for s in sinistres:
#                 self.sinistre_combo.addItem(
#                     f"{s.get('numero_sinistre')} - {s.get('branche', '')}",
#                     s.get('id')
#                 )
#             self.sinistre_combo.blockSignals(False)
            
#             self._charger_alertes()
#         except Exception as e:
#             print(f"Erreur chargement sinistres: {e}")
    
#     def on_sinistre_changed(self, index):
#         """Charge les recours du sinistre sélectionné"""
#         if index > 0:
#             sinistre_id = self.sinistre_combo.currentData()
#             if sinistre_id:
#                 self.current_sinistre_id = sinistre_id
#                 self.load_recours(sinistre_id)
#         elif index == 0:
#             # Tous les sinistres
#             self.current_sinistre_id = None
#             self.load_recours(None)
    
#     def load_recours(self, sinistre_id: Optional[int] = None):
#         """Charge les recours dans le tableau"""
#         try:
#             if sinistre_id:
#                 recours = self.controller.get_recours_by_sinistre(sinistre_id)
#             else:
#                 # Récupérer tous les recours récents
#                 try:
#                     recours = self.controller.get_all_recours(limit=200)
#                 except AttributeError:
#                     recours = []
            
#             # Filtrer selon la recherche
#             query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""
#             if query:
#                 recours = [
#                     r for r in recours
#                     if query in str(r.get('numero_recours', '')).lower()
#                     or query in str(r.get('debiteur_nom', '')).lower()
#                     or query in str(r.get('client_nom', '')).lower()
#                 ]
            
#             self._total_recours = len(recours)
            
#             # Pagination
#             start = (self._current_page - 1) * self._per_page
#             end = start + self._per_page
#             page_recours = recours[start:end]
            
#             # Mise à jour des stats
#             self._update_stats(recours)
            
#             # Remplir le tableau
#             self.table_recours.setRowCount(len(page_recours))
            
#             for i, rec in enumerate(page_recours):
#                 self._fill_row(i, rec)
            
#             # Mise à jour pagination
#             self._update_pagination(start, min(end, self._total_recours))
        
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur chargement recours: {str(e)}")
#             import traceback
#             traceback.print_exc()
    
#     def _fill_row(self, row: int, rec: dict):
#         """Remplit une ligne du tableau"""
#         # 0. N° Recours
#         num_item = QTableWidgetItem(rec.get('numero_recours', ''))
#         num_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
#         num_item.setForeground(QColor("#2563eb"))
#         self.table_recours.setItem(row, 0, num_item)
        
#         # 1. Client
#         client = rec.get('client_nom') or rec.get('debiteur_nom') or '-'
#         self.table_recours.setItem(row, 1, QTableWidgetItem(client))
        
#         # 2. Assuré (pour l'instant = client, à adapter selon votre modèle)
#         assure = rec.get('assure_nom') or rec.get('debiteur_nom') or '-'
#         self.table_recours.setItem(row, 2, QTableWidgetItem(assure))
        
#         # 3. Date Création
#         date_creation = rec.get('date_ouverture') or rec.get('created_at', '')
#         if date_creation:
#             try:
#                 dt = datetime.fromisoformat(str(date_creation)[:19])
#                 date_str = dt.strftime("%d %b %Y")
#             except Exception:
#                 date_str = str(date_creation)[:10]
#         else:
#             date_str = '-'
#         self.table_recours.setItem(row, 3, QTableWidgetItem(date_str))
        
#         # 4. Statut (badge)
#         statut = rec.get('statut', '')
#         badge = StatusBadge(statut)
#         badge_container = QWidget()
#         badge_layout = QHBoxLayout(badge_container)
#         badge_layout.setContentsMargins(4, 6, 4, 6)
#         badge_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
#         badge_layout.addWidget(badge)
#         badge_layout.addStretch()
#         self.table_recours.setCellWidget(row, 4, badge_container)
        
#         # 5. Montant
#         montant = rec.get('montant_reclame', 0) or 0
#         montant_str = f"€{float(montant):,.2f}".replace(",", " ").replace(".", ",")
#         montant_item = QTableWidgetItem(montant_str)
#         montant_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
#         montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
#         self.table_recours.setItem(row, 5, montant_item)
        
#         # 6. Gestionnaire
#         gestionnaire = rec.get('gestionnaire_nom') or rec.get('responsable_nom') or 'M. Moreau'
#         self.table_recours.setItem(row, 6, QTableWidgetItem(gestionnaire))
        
#         # 7. Actions (bouton [...])
#         btn_actions = QPushButton("⋯")
#         btn_actions.setCursor(Qt.PointingHandCursor)
#         btn_actions.setFixedSize(32, 28)
#         btn_actions.setStyleSheet("""
#             QPushButton {
#                 background: transparent;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 6px;
#                 font-size: 16px;
#                 font-weight: bold;
#                 color: #64748b;
#             }
#             QPushButton:hover {
#                 background: #f1f5f9;
#                 border-color: #cbd5e1;
#                 color: #1e293b;
#             }
#             QPushButton:pressed {
#                 background: #e2e8f0;
#             }
#         """)
#         btn_actions.setToolTip("Actions")
        
#         # Capturer le recours pour le menu
#         btn_actions.clicked.connect(
#             lambda checked=False, r=rec, b=btn_actions: self._show_row_actions_menu(r, b)
#         )
        
#         actions_container = QWidget()
#         actions_layout = QHBoxLayout(actions_container)
#         actions_layout.setContentsMargins(4, 6, 4, 6)
#         actions_layout.setAlignment(Qt.AlignCenter)
#         actions_layout.addWidget(btn_actions)
#         self.table_recours.setCellWidget(row, 7, actions_container)
    
#     def _update_stats(self, recours: list):
#         """Met à jour les 4 cartes statistiques"""
#         total = len(recours)
#         aboutis_statuts = ['ABOUTI', 'ENCAISSE', 'PAYE', 'COMPTABILISE', 'CLOTURE']
#         aboutis = sum(1 for r in recours if r.get('statut') in aboutis_statuts)
#         attente_statuts = ['EN_ATTENTE_ENCAISSEMENT', 'OUVERT', 'CONTESTE']
#         attente = sum(1 for r in recours if r.get('statut') in attente_statuts)
#         encours = total - aboutis - attente
#         if encours < 0:
#             encours = 0
        
#         # Mettre à jour les labels
#         for card, value in [
#             (self.card_total, total),
#             (self.card_aboutis, aboutis),
#             (self.card_encours, encours),
#             (self.card_attente, attente),
#         ]:
#             for lbl in card.findChildren(QLabel):
#                 if lbl.objectName() == "stat_value":
#                     lbl.setText(f"{value:,}".replace(",", " "))
    
#     def _update_pagination(self, start: int, end: int):
#         """Met à jour la pagination"""
#         self.lbl_pagination.setText(f"{start + 1}-{end} de {self._total_recours:,}".replace(",", " "))
#         self.btn_prev.setEnabled(self._current_page > 1)
#         self.btn_next.setEnabled(end < self._total_recours)
    
#     def _go_prev_page(self):
#         if self._current_page > 1:
#             self._current_page -= 1
#             self.load_recours(self.current_sinistre_id)
    
#     def _go_next_page(self):
#         if self._current_page * self._per_page < self._total_recours:
#             self._current_page += 1
#             self.load_recours(self.current_sinistre_id)
    
#     def _on_search_changed(self, text: str):
#         """Recherche en temps réel"""
#         self._current_page = 1
#         self.load_recours(self.current_sinistre_id)
    
#     # ═══════════════════════════════════════════════════════════════
#     # MENU D'ACTIONS PAR LIGNE
#     # ═══════════════════════════════════════════════════════════════
    
#     def _show_row_actions_menu(self, recours: dict, button: QPushButton):
#         """Affiche le menu d'actions pour un recours"""
#         menu = QMenu(self)
#         menu.setStyleSheet("""
#             QMenu {
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 10px;
#                 padding: 6px;
#                 min-width: 220px;
#             }
#             QMenu::item {
#                 padding: 8px 16px;
#                 border-radius: 6px;
#                 font-size: 12px;
#                 color: #1e293b;
#             }
#             QMenu::item:selected {
#                 background: #eff6ff;
#                 color: #2563eb;
#             }
#             QMenu::separator {
#                 height: 1px;
#                 background: #f1f5f9;
#                 margin: 4px 8px;
#             }
#         """)
        
#         statut = recours.get('statut', '')
#         recours_numero = recours.get('numero_recours', '')
        
#         # Consultation
#         action_suivi = menu.addAction("📈  Voir le suivi complet")
#         action_suivi.triggered.connect(
#             lambda: self._action_suivi_from_menu(recours_numero)
#         )
        
#         action_details = menu.addAction("👁️  Voir les détails")
#         action_details.triggered.connect(
#             lambda: self._action_details_from_menu(recours)
#         )
        
#         menu.addSeparator()
        
#         # Actions métier
#         if statut in ["EN_ATTENTE_ENCAISSEMENT", "PARTIELLEMENT_ENCAISSE"]:
#             if self.permissions_ui.peut('recours', 'UPDATE'):
#                 action_encaisser = menu.addAction("💰  Encaisser")
#                 action_encaisser.triggered.connect(
#                     lambda: self._action_encaisser_from_menu(recours_numero)
#                 )
        
#         if statut in ["OUVERT", "EN_INSTRUCTION", "RELANCE", "CONTESTE"]:
#             if self.permissions_ui.peut('recours', 'UPDATE'):
#                 action_relancer = menu.addAction("🔔  Relancer")
#                 action_relancer.triggered.connect(
#                     lambda: self._action_relancer_from_menu(recours_numero)
#                 )
        
#         if statut in ["ENCAISSE", "PARTIELLEMENT_ENCAISSE", "REVERSEMENT_EN_COURS"]:
#             if self.permissions_ui.peut('recours', 'UPDATE'):
#                 action_rep = menu.addAction("📊  Répartition")
#                 action_rep.triggered.connect(
#                     lambda: self._action_repartition_from_menu(recours_numero)
#                 )
        
#         if self.permissions_ui.peut('recours', 'READ'):
#             action_ecr = menu.addAction("📒  Écritures comptables")
#             action_ecr.triggered.connect(
#                 lambda: self._action_ecritures_from_menu(recours_numero)
#             )
        
#         menu.addSeparator()
        
#         # Clôture / Annulation
#         if statut not in ["CLOTURE", "REFUSE", "ANNULE"]:
#             if self.permissions_ui.peut('recours', 'VALIDATE'):
#                 action_clot = menu.addAction("🔒  Clôturer")
#                 action_clot.triggered.connect(
#                     lambda: self._action_cloturer_from_menu(recours)
#                 )
        
#         if statut not in ["CLOTURE", "REFUSE", "ANNULE"]:
#             if self.permissions_ui.peut('recours', 'DELETE'):
#                 action_ann = menu.addAction("🚫  Annuler")
#                 action_ann.triggered.connect(
#                     lambda: self._action_annuler_from_menu(recours)
#                 )
        
#         menu.addSeparator()
        
#         action_copy = menu.addAction("📋  Copier le N°")
#         action_copy.triggered.connect(lambda: self._copy_to_clipboard(recours_numero))
        
#         # Afficher le menu
#         menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
    
#     # ═══════════════════════════════════════════════════════════════
#     # EXPORT
#     # ═══════════════════════════════════════════════════════════════
    
#     def _export_data(self):
#         """Exporte les données (CSV simple)"""
#         from PySide6.QtWidgets import QFileDialog
#         import csv
        
#         path, _ = QFileDialog.getSaveFileName(
#             self, "Exporter les recours",
#             f"recours_{datetime.now().strftime('%Y%m%d')}.csv",
#             "CSV (*.csv)"
#         )
#         if not path:
#             return
        
#         try:
#             with open(path, 'w', newline='', encoding='utf-8') as f:
#                 writer = csv.writer(f)
#                 writer.writerow([
#                     "N° Recours", "Client", "Assuré", "Date Création",
#                     "Statut", "Montant", "Gestionnaire"
#                 ])
#                 for row in range(self.table_recours.rowCount()):
#                     values = []
#                     for col in range(7):
#                         item = self.table_recours.item(row, col)
#                         values.append(item.text() if item else '')
#                     writer.writerow(values)
            
#             QMessageBox.information(
#                 self, "Export réussi",
#                 f"✅ {self.table_recours.rowCount()} recours exportés vers:\n{path}"
#             )
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
#     # ═══════════════════════════════════════════════════════════════
#     # CRÉATION DE RECOURS
#     # ═══════════════════════════════════════════════════════════════
    
#     def creer_recours(self):
#         """Crée un nouveau recours"""
#         if not self.current_sinistre_id:
#             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
#             return
        
#         conditions = self.controller.verifier_conditions_recours(self.current_sinistre_id)
        
#         if not conditions.get('peut_creer'):
#             QMessageBox.warning(
#                 self, "Condition CDC non remplie",
#                 f"Impossible de créer un recours :\n\n"
#                 f"{conditions.get('raison', 'Condition non remplie')}"
#             )
#             return
        
#         sinistre_info = {}
#         try:
#             from addons.sinistres.controllers.sinistre_controller import SinistreController
#             sc = SinistreController()
#             sc.set_current_user(self.user)
#             sinistre_data = sc.get_sinistre(self.current_sinistre_id)
            
#             if sinistre_data:
#                 sinistre_info = {
#                     'numero_sinistre': sinistre_data.get('numero_sinistre', 'N/A'),
#                     'client_nom': sinistre_data.get('client_nom', 'N/A'),
#                     'branche': sinistre_data.get('branche', 'N/A'),
#                     'montant_regle': conditions.get('montant_regle', 0),
#                     'taux_responsabilite': conditions.get('taux_responsabilite', 1),
#                 }
#         except Exception as e:
#             print(f"⚠️ Erreur récupération infos sinistre: {e}")
        
#         from addons.sinistres.views.recours_dialog import RecoursDialog
#         dialog = RecoursDialog(
#             sinistre_id=self.current_sinistre_id,
#             recours_controller=self.controller,
#             user=self.user,
#             sinistre_info=sinistre_info,
#             parent=self
#         )
#         dialog.recours_created.connect(self._on_recours_created)
#         dialog.exec()
    
#     def _on_recours_created(self, data: dict):
#         self.load_recours(self.current_sinistre_id)
#         QMessageBox.information(self, "Succès", "✅ Recours créé avec succès !")
    
#     # ═══════════════════════════════════════════════════════════════
#     # ACTIONS MÉTIER (reprises de l'ancien code)
#     # ═══════════════════════════════════════════════════════════════
    
#     def _on_recours_cell_clicked(self, row: int, col: int):
#         """Clic sur une ligne"""
#         if col == 7:  # Colonne actions
#             return
#         num_item = self.table_recours.item(row, 0)
#         if not num_item:
#             return
#         try:
#             rec_data = self.controller.get_recours_by_numero(num_item.text())
#             if rec_data:
#                 self.selected_recours_id = rec_data.get('id')
#         except Exception:
#             pass
    
#     def _charger_alertes(self):
#         try:
#             alertes = self.controller.get_alertes_recours()
#             self.alertes_widget.set_alertes(alertes)
#         except Exception as e:
#             print(f"❌ Erreur chargement alertes : {e}")
    
#     def _on_alerte_clicked(self, alerte: dict):
#         recours_id = alerte.get('recours_id')
#         if not recours_id:
#             return
#         for i in range(self.table_recours.rowCount()):
#             num_item = self.table_recours.item(i, 0)
#             if not num_item:
#                 continue
#             try:
#                 rec = self.controller.get_recours_by_numero(num_item.text())
#                 if rec and rec.get('id') == recours_id:
#                     self.table_recours.selectRow(i)
#                     break
#             except Exception:
#                 continue
    
#     def ouvrir_repartition(self):
#         """Ouvre le dialogue de répartition"""
#         recours_data = self._get_selected_recours()
#         if not recours_data:
#             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
#             return
        
#         statut = recours_data.get('statut', '')
#         if statut not in ["ENCAISSE", "PARTIELLEMENT_ENCAISSE"]:
#             QMessageBox.warning(
#                 self, "Attention",
#                 f"Seul un recours encaissé peut être réparti (statut: {statut})"
#             )
#             return
        
#         try:
#             dialog = RepartitionRecoursDialog(
#                 recours_id=recours_data.get('id'),
#                 recours_info=recours_data,
#                 recours_controller=self.controller,
#                 user=self.user,
#                 parent=self,
#             )
#             dialog.repartition_validee.connect(self._on_repartition_validee)
#             dialog.exec()
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
#     def _on_repartition_validee(self, repartitions: list):
#         self.load_recours(self.current_sinistre_id)
#         QMessageBox.information(
#             self, "Succès",
#             f"✅ Répartition enregistrée : {len(repartitions)} part(s)"
#         )
    
#     def ouvrir_comptabilite(self):
#         """Ouvre le dialogue des écritures comptables"""
#         recours_data = self._get_selected_recours()
#         if not recours_data:
#             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
#             return
        
#         try:
#             dialog = ComptabiliteRecoursDialog(
#                 recours_id=recours_data.get('id'),
#                 recours_info=recours_data,
#                 comptabilite_controller=self.comptabilite_controller,
#                 user=self.user,
#                 parent=self,
#             )
#             dialog.exec()
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
#     def planifier_relances_auto(self):
#         reply = QMessageBox.question(
#             self, "Confirmation",
#             "Voulez-vous planifier automatiquement les relances pour tous les recours ?",
#             QMessageBox.Yes | QMessageBox.No
#         )
#         if reply == QMessageBox.Yes:
#             try:
#                 result = self.controller.planifier_relances_auto()
#                 QMessageBox.information(
#                     self, "Planification terminée",
#                     f"✅ {result.get('planifiees', 0)} relances planifiées\n"
#                     f"❌ {result.get('erreurs', 0)} erreurs"
#                 )
#                 self.load_recours(self.current_sinistre_id)
#             except Exception as e:
#                 QMessageBox.critical(self, "Erreur", str(e))
    
#     # ═══════════════════════════════════════════════════════════════
#     # HELPERS
#     # ═══════════════════════════════════════════════════════════════
    
#     def _get_selected_recours(self) -> Optional[dict]:
#         """Retourne le recours actuellement sélectionné"""
#         row = self.table_recours.currentRow()
#         if row < 0:
#             return None
#         num_item = self.table_recours.item(row, 0)
#         if not num_item:
#             return None
#         try:
#             return self.controller.get_recours_by_numero(num_item.text())
#         except Exception:
#             return None
    
#     def get_selected_recours_id(self) -> Optional[int]:
#         rec = self._get_selected_recours()
#         return rec.get('id') if rec else None
    
#     # ═══════════════════════════════════════════════════════════════
#     # ACTIONS DU MENU CONTEXTUEL
#     # ═══════════════════════════════════════════════════════════════
    
#     def _action_suivi_from_menu(self, recours_numero: str):
#         try:
#             recours_data = self.controller.get_recours_by_numero(recours_numero)
#             if not recours_data:
#                 return
#             from addons.sinistres.views.recours_suivi_dialog import RecoursSuiviDialog
#             dialog = RecoursSuiviDialog(
#                 recours_id=recours_data.get('id'),
#                 recours_info=recours_data,
#                 recours_controller=self.controller,
#                 comptabilite_controller=self.comptabilite_controller,
#                 user=self.user,
#                 parent=self,
#             )
#             dialog.exec()
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
#     def _action_details_from_menu(self, recours_data: dict):
#         QMessageBox.information(
#             self,
#             f"Recours {recours_data.get('numero_recours', 'N/A')}",
#             f"📌 Type: {recours_data.get('type_recours', 'N/A')}\n"
#             f"👤 Débiteur: {recours_data.get('debiteur_nom', 'N/A')}\n"
#             f"💰 Montant réclamé: {float(recours_data.get('montant_reclame', 0)):,.0f} FCFA\n"
#             f"✅ Montant accepté: {float(recours_data.get('montant_accepte', 0) or 0):,.0f} FCFA\n"
#             f"💵 Montant encaissé: {float(recours_data.get('montant_encaisse', 0) or 0):,.0f} FCFA\n"
#             f"📊 Solde: {float(recours_data.get('solde', 0) or 0):,.0f} FCFA\n"
#             f"📅 Date ouverture: {str(recours_data.get('date_ouverture', ''))[:10]}\n"
#             f"📌 Statut: {recours_data.get('statut', 'N/A')}"
#         )
    
#     def _action_encaisser_from_menu(self, recours_numero: str):
#         self._select_row_by_numero(recours_numero)
#         self._do_encaisser()
    
#     def _action_relancer_from_menu(self, recours_numero: str):
#         self._select_row_by_numero(recours_numero)
#         self._do_relancer()
    
#     def _action_repartition_from_menu(self, recours_numero: str):
#         self._select_row_by_numero(recours_numero)
#         self.ouvrir_repartition()
    
#     def _action_ecritures_from_menu(self, recours_numero: str):
#         self._select_row_by_numero(recours_numero)
#         self.ouvrir_comptabilite()
    
#     def _action_reversements_from_menu(self, recours_numero: str):
#         QMessageBox.information(
#             self, "Info",
#             "Le dialogue de reversement sera disponible prochainement."
#         )
    
#     def _action_cloturer_from_menu(self, recours_data: dict):
#         recours_numero = recours_data.get('numero_recours', 'N/A')
#         from PySide6.QtWidgets import QInputDialog
#         motif, ok = QInputDialog.getMultiLineText(
#             self, f"Clôturer {recours_numero}",
#             "Motif de clôture :", ""
#         )
#         if not ok or not motif.strip():
#             return
#         reply = QMessageBox.question(
#             self, "Confirmation",
#             f"Clôturer le recours {recours_numero} ?",
#             QMessageBox.Yes | QMessageBox.No
#         )
#         if reply != QMessageBox.Yes:
#             return
#         try:
#             result = self.controller.changer_statut_recours(
#                 recours_data.get('id'), "CLOTURE", motif=motif
#             )
#             if result:
#                 QMessageBox.information(self, "Succès", "Recours clôturé")
#                 self.load_recours(self.current_sinistre_id)
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", str(e))
    
#     def _action_annuler_from_menu(self, recours_data: dict):
#         recours_numero = recours_data.get('numero_recours', 'N/A')
#         from PySide6.QtWidgets import QInputDialog
#         motif, ok = QInputDialog.getMultiLineText(
#             self, f"Annuler {recours_numero}",
#             "Motif d'annulation :", ""
#         )
#         if not ok or not motif.strip():
#             return
#         reply = QMessageBox.question(
#             self, "Confirmation",
#             f"Annuler le recours {recours_numero} ?",
#             QMessageBox.Yes | QMessageBox.No
#         )
#         if reply != QMessageBox.Yes:
#             return
#         try:
#             result = self.controller.changer_statut_recours(
#                 recours_data.get('id'), "REFUSE", motif=motif
#             )
#             if result:
#                 QMessageBox.information(self, "Succès", "Recours annulé")
#                 self.load_recours(self.current_sinistre_id)
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", str(e))
    
#     def _do_encaisser(self):
#         """Encaissement du recours sélectionné"""
#         recours_data = self._get_selected_recours()
#         if not recours_data:
#             return
#         statut = recours_data.get('statut', '')
#         if statut not in ["EN_ATTENTE_ENCAISSEMENT", "PARTIELLEMENT_ENCAISSE"]:
#             QMessageBox.warning(
#                 self, "Attention",
#                 f"Statut incompatible pour encaissement : {statut}"
#             )
#             return
#         try:
#             from addons.sinistres.views.encaissement_dialog import EncaissementDialog
#             dialog = EncaissementDialog(
#                 recours_id=recours_data.get('id'),
#                 recours_info=recours_data,
#                 recours_controller=self.controller,
#                 user=self.user,
#                 parent=self,
#             )
#             dialog.encaissement_added.connect(self._on_encaissement_added)
#             dialog.exec()
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
#     def _on_encaissement_added(self, data: dict):
#         self.load_recours(self.current_sinistre_id)
#         QMessageBox.information(
#             self, "Succès",
#             f"✅ Encaissement de {data.get('montant', 0):,.0f} FCFA enregistré\n"
#             f"📊 Solde: {data.get('solde_restant', 0):,.0f} FCFA"
#         )
    
#     def _do_relancer(self):
#         """Relance du recours sélectionné"""
#         recours_data = self._get_selected_recours()
#         if not recours_data:
#             return
#         try:
#             from addons.sinistres.views.relance_dialog import RelanceDialog
#             dialog = RelanceDialog(
#                 recours_id=recours_data.get('id'),
#                 recours_info=recours_data,
#                 recours_controller=self.controller,
#                 user=self.user,
#                 parent=self,
#             )
#             dialog.relance_added.connect(self._on_relance_added)
#             dialog.exec()
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
#     def _on_relance_added(self, data: dict):
#         self.load_recours(self.current_sinistre_id)
#         QMessageBox.information(self, "Succès", "✅ Relance ajoutée")
    
#     def _select_row_by_numero(self, recours_numero: str):
#         """Sélectionne la ligne correspondant au numéro"""
#         for i in range(self.table_recours.rowCount()):
#             item = self.table_recours.item(i, 0)
#             if item and item.text() == recours_numero:
#                 self.table_recours.selectRow(i)
#                 return
    
#     def _copy_to_clipboard(self, text: str):
#         from PySide6.QtWidgets import QApplication
#         QApplication.clipboard().setText(text)
#         QMessageBox.information(self, "Copié", f"✅ '{text}' copié")


"""
Vue principale du module LOMETA Sinistres
Interface utilisateur complète pour la gestion des recours
Design moderne avec icônes FontAwesome
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QListWidgetItem, QStackedWidget,
    QListWidget, QFrame, QMessageBox, QDialog, QGraphicsDropShadowEffect,
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QTabWidget, QSplitter, QScrollArea,
    QProgressBar, QToolBar, QMenu, QCheckBox, QRadioButton, QSizePolicy,
    QAbstractItemView
)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QDate
from PySide6.QtGui import QColor, QIcon, QFont, QAction, QCursor

import qtawesome as qta

from datetime import datetime, timedelta
from typing import Optional, List

from addons.sinistres.views.repartition_recours_dialog import RepartitionRecoursDialog
from addons.sinistres.views.comptabilite_recours_dialog import ComptabiliteRecoursDialog
from addons.sinistres.views.widgets.alertes_widget import AlertesWidget
from addons.sinistres.controllers.comptabilite_controller import ComptabiliteController


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def _safe_bool(value) -> bool:
    """Convertit n'importe quelle valeur en booléen sûr"""
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() not in ('', 'none', 'null', '0', 'false')
    return bool(value)


def make_icon_label(icon_name: str, color: str = "#1a73e8", size: int = 20) -> QLabel:
    """Crée un QLabel contenant une icône FontAwesome"""
    lbl = QLabel()
    try:
        icon = qta.icon(icon_name, color=color)
        lbl.setPixmap(icon.pixmap(QSize(size, size)))
    except Exception as e:
        print(f"⚠️ Icône '{icon_name}' introuvable : {e}")
        lbl.setText("●")
        lbl.setStyleSheet(f"color: {color}; font-size: {size}px;")
    
    lbl.setFixedSize(size + 4, size + 4)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(lbl.styleSheet() + "background: transparent;")
    return lbl


# ═══════════════════════════════════════════════════════════════════
# WIDGETS PERSONNALISÉS
# ═══════════════════════════════════════════════════════════════════

class StatCard(QFrame):
    """Carte statistique moderne avec icône FontAwesome"""
    
    def __init__(self, icon_name: str, title: str, value: str, 
                 color_bg: str, color_fg: str, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(90)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        
        # Ombre légère
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 12))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)
        
        # ✅ Conteneur d'icône avec FontAwesome
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {color_bg};
                border-radius: 10px;
                border: none;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel()
        try:
            icon = qta.icon(icon_name, color=color_fg)
            icon_label.setPixmap(icon.pixmap(QSize(22, 22)))
        except Exception as e:
            print(f"⚠️ Icône '{icon_name}' introuvable : {e}")
            icon_label.setText("●")
            icon_label.setStyleSheet(f"color: {color_fg}; font-size: 18px;")
        
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(icon_label.styleSheet() + "background: transparent; border: none;")
        icon_layout.addWidget(icon_label)
        
        layout.addWidget(icon_container)
        
        # Textes
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            color: #64748b;
            font-size: 12px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        
        value_lbl = QLabel(str(value))
        value_lbl.setStyleSheet(f"""
            color: {color_fg};
            font-size: 26px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)
        value_lbl.setObjectName("stat_value")
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(value_lbl)
        
        layout.addLayout(text_layout, 1)


class StatusBadge(QLabel):
    """Badge de statut arrondi (pill)"""
    
    STATUS_STYLES = {
        'ABOUTI':       ("#d1fae5", "#065f46", "Aboutis"),
        'ENCAISSE':     ("#d1fae5", "#065f46", "Encaissé"),
        'PAYE':         ("#d1fae5", "#065f46", "Payé"),
        'COMPTABILISE': ("#d1fae5", "#065f46", "Comptabilisé"),
        'CLOTURE':      ("#e2e8f0", "#334155", "Clôturé"),
        'EN_COURS':     ("#fed7aa", "#9a3412", "En cours"),
        'OUVERT':       ("#fed7aa", "#9a3412", "Ouvert"),
        'EN_INSTRUCTION': ("#fed7aa", "#9a3412", "En instruction"),
        'RELANCE':      ("#fed7aa", "#9a3412", "Relancé"),
        'EN_ATTENTE_ENCAISSEMENT': ("#fed7aa", "#9a3412", "En attente"),
        'PARTIELLEMENT_ENCAISSE': ("#fed7aa", "#9a3412", "Partiel"),
        'REVERSEMENT_EN_COURS': ("#fed7aa", "#9a3412", "Reversement"),
        'CONTESTE':     ("#fee2e2", "#991b1b", "Contesté"),
        'REFUSE':       ("#fee2e2", "#991b1b", "Refusé"),
        'ANNULE':       ("#fee2e2", "#991b1b", "Annulé"),
    }
    
    def __init__(self, statut: str, parent=None):
        super().__init__(parent)
        
        bg, fg, label = self.STATUS_STYLES.get(
            statut, ("#e2e8f0", "#475569", statut)
        )
        
        self.setText(f"  {label}  ")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 11px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
                border: none;
            }}
        """)
        self.setFixedHeight(22)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)


# ═══════════════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════

class RecoursPage(QWidget):
    """Page de gestion des recours — Design moderne v2.0"""
    
    def __init__(self, controller, user):
        super().__init__()
        self.controller = controller
        self.user = user
        self.current_sinistre_id = None
        self.selected_recours_id = None
        
        # Pagination
        self._current_page = 1
        self._per_page = 10
        self._total_recours = 0
        
        # Contrôleur comptabilité
        self.comptabilite_controller = ComptabiliteController()
        self.comptabilite_controller.set_current_user(user)
        
        # Service de permissions
        from addons.sinistres.services.permission_service import PermissionService
        from addons.sinistres.security.permissions_helper import PermissionsUI
        self.permission_service = PermissionService()
        self.permissions_ui = PermissionsUI(user, self.permission_service)
        
        self.setup_ui()
        self._appliquer_permissions()
        self.load_data()
    
    def _appliquer_permissions(self):
        """Applique les permissions sur les boutons"""
        self.permissions_ui.masquer_si_non_autorise(
            self.btn_creer_rec, 'recours', 'CREATE'
        )
        self.permissions_ui.masquer_si_non_autorise(
            self.btn_planifier, 'recours', 'UPDATE'
        )
        self.permissions_ui.masquer_si_non_autorise(
            self.btn_repartition, 'recours', 'UPDATE'
        )
        self.permissions_ui.masquer_si_non_autorise(
            self.btn_comptabilite, 'recours', 'READ'
        )
    
    # ═══════════════════════════════════════════════════════════════
    # CONSTRUCTION DE L'INTERFACE
    # ═══════════════════════════════════════════════════════════════
    
    def setup_ui(self):
        self.setStyleSheet("background: #f1f5f9;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        layout.addWidget(self._build_header())
        layout.addWidget(self._build_stats_row())
        
        # Alertes
        self.alertes_widget = AlertesWidget()
        self.alertes_widget.alerte_clicked.connect(self._on_alerte_clicked)
        layout.addWidget(self.alertes_widget)
        
        layout.addWidget(self._build_table_card(), 1)
        layout.addWidget(self._build_secondary_actions())
    
    def _build_header(self):
        """En-tête : titre + filtre sinistre + bouton Nouveau Recours"""
        frame = QFrame()
        frame.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # ✅ Icône FontAwesome pour le titre
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet("""
            QFrame {
                background: #eff6ff;
                border-radius: 12px;
                border: 1px solid #dbeafe;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon('fa5s.balance-scale', color='#2563eb').pixmap(QSize(24, 24)))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_lbl)
        
        layout.addWidget(icon_container)
        
        # Titre + sous-titre
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title = QLabel("Gestion des Recours")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
            background: transparent;
        """)
        title_block.addWidget(title)
        
        subtitle = QLabel("Suivi et gestion des recours contentieux")
        subtitle.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        title_block.addWidget(subtitle)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        # Filtre sinistre
        sinistre_label = QLabel("Sinistre :")
        sinistre_label.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        layout.addWidget(sinistre_label)
        
        self.sinistre_combo = QComboBox()
        self.sinistre_combo.setMinimumWidth(200)
        self.sinistre_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #1e293b;
            }
            QComboBox:hover { border-color: #3b82f6; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #64748b;
                margin-right: 6px;
            }
        """)
        self.sinistre_combo.currentIndexChanged.connect(self.on_sinistre_changed)
        layout.addWidget(self.sinistre_combo)
        
        # ✅ Bouton refresh avec icône sync
        self.btn_refresh = QPushButton()
        self.btn_refresh.setFixedSize(34, 34)
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setToolTip("Actualiser")
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#64748b'))
        self.btn_refresh.setIconSize(QSize(14, 14))
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QPushButton:hover { background: #f8fafc; border-color: #cbd5e1; }
        """)
        self.btn_refresh.clicked.connect(self.load_data)
        layout.addWidget(self.btn_refresh)
        
        # ✅ Bouton Nouveau Recours
        self.btn_creer_rec = QPushButton("  Nouveau Recours")
        self.btn_creer_rec.setCursor(Qt.PointingHandCursor)
        self.btn_creer_rec.setFixedHeight(38)
        self.btn_creer_rec.setIcon(qta.icon('fa5s.plus-circle', color='white'))
        self.btn_creer_rec.setIconSize(QSize(14, 14))
        self.btn_creer_rec.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: 700;
                text-align: left;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:pressed { background: #1e40af; }
        """)
        self.btn_creer_rec.clicked.connect(self.creer_recours)
        layout.addWidget(self.btn_creer_rec)
        
        return frame
    
    def _build_stats_row(self):
        """Rangée de 4 cartes statistiques avec icônes FontAwesome"""
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        
        self.card_total = StatCard(
            icon_name="fa5s.folder-open", 
            title="Total Recours", value="0",
            color_bg="#dbeafe", color_fg="#1e40af"
        )
        self.card_aboutis = StatCard(
            icon_name="fa5s.check-circle", 
            title="Aboutis", value="0",
            color_bg="#d1fae5", color_fg="#059669"
        )
        self.card_encours = StatCard(
            icon_name="fa5s.hourglass-half", 
            title="En cours", value="0",
            color_bg="#fed7aa", color_fg="#ea580c"
        )
        self.card_attente = StatCard(
            icon_name="fa5s.exclamation-circle", 
            title="En attente", value="0",
            color_bg="#f1f5f9", color_fg="#475569"
        )
        
        layout.addWidget(self.card_total)
        layout.addWidget(self.card_aboutis)
        layout.addWidget(self.card_encours)
        layout.addWidget(self.card_attente)
        
        return wrapper
    
    def _build_table_card(self):
        """Carte contenant le tableau avec header intégré"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ─── Header de la carte ───
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-bottom: 1px solid #f1f5f9;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(10)
        
        # ✅ Titre avec icône liste
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('fa5s.list', color='#2563eb').pixmap(QSize(14, 14)))
        title_row.addWidget(title_icon)
        
        title = QLabel("Liste des Recours")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #0f172a;
            background: transparent;
        """)
        title_row.addWidget(title)
        title_row.addStretch()
        
        header_layout.addLayout(title_row)
        header_layout.addStretch()
        
        # Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche")
        self.search_input.setFixedWidth(220)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
                color: #1e293b;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: white;
            }
        """)
        self.search_input.textChanged.connect(self._on_search_changed)
        header_layout.addWidget(self.search_input)
        
        # ✅ Bouton Filtre avec icône filter
        btn_filter = QPushButton("  Filtrer")
        btn_filter.setCursor(Qt.PointingHandCursor)
        btn_filter.setIcon(qta.icon('fa5s.filter', color='#1e293b'))
        btn_filter.setIconSize(QSize(12, 12))
        btn_filter.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
                color: #1e293b;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover { background: #f8fafc; border-color: #cbd5e1; }
        """)
        header_layout.addWidget(btn_filter)
        
        # Date picker
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat("dd MMM yyyy")
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setStyleSheet("""
            QDateEdit {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #1e293b;
                min-width: 130px;
            }
            QDateEdit:hover { border-color: #3b82f6; }
            QDateEdit::drop-down { border: none; width: 18px; }
        """)
        header_layout.addWidget(self.date_picker)
        
        # ✅ Bouton Export avec icône download
        btn_export = QPushButton("  Export")
        btn_export.setCursor(Qt.PointingHandCursor)
        btn_export.setIcon(qta.icon('fa5s.download', color='#1e293b'))
        btn_export.setIconSize(QSize(12, 12))
        btn_export.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
                color: #1e293b;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover { background: #f8fafc; border-color: #cbd5e1; }
        """)
        btn_export.clicked.connect(self._export_data)
        header_layout.addWidget(btn_export)
        
        layout.addWidget(header)
        
        # ─── Tableau ───
        self.table_recours = QTableWidget()
        self.table_recours.setColumnCount(8)
        self.table_recours.setHorizontalHeaderLabels([
            "N° Recours", "Client", "Assuré", "Date Création",
            "Statut", "Montant", "Gestionnaire", "Actions"
        ])
        
        self.table_recours.setStyleSheet("""
            QTableWidget {
                background: white;
                border: none;
                gridline-color: transparent;
                outline: none;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f5f9;
                color: #1e293b;
                font-size: 12px;
            }
            QTableWidget::item:selected {
                background: #eff6ff;
                color: #1e293b;
            }
            QTableWidget::item:hover {
                background: #f8fafc;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 12px 8px;
                font-weight: 600;
                font-size: 12px;
                color: #475569;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                border-top: 1px solid #f1f5f9;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #94a3b8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        
        self.table_recours.setAlternatingRowColors(False)
        self.table_recours.verticalHeader().setVisible(False)
        self.table_recours.verticalHeader().setDefaultSectionSize(52)
        self.table_recours.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_recours.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_recours.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_recours.setShowGrid(False)
        
        # Largeurs des colonnes
        header_view = self.table_recours.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)
        header_view.setSectionResizeMode(2, QHeaderView.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table_recours.setColumnWidth(7, 60)
        
        self.table_recours.cellClicked.connect(self._on_recours_cell_clicked)
        
        layout.addWidget(self.table_recours)
        
        # ─── Pagination ───
        pagination = QFrame()
        pagination.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-top: 1px solid #f1f5f9;
            }
        """)
        pag_layout = QHBoxLayout(pagination)
        pag_layout.setContentsMargins(20, 12, 20, 12)
        pag_layout.setSpacing(10)
        
        pag_layout.addStretch()
        
        self.lbl_pagination = QLabel("0-0 de 0")
        self.lbl_pagination.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        pag_layout.addWidget(self.lbl_pagination)
        
        # ✅ Bouton prev
        self.btn_prev = QPushButton("  Précédent")
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.setIcon(qta.icon('fa5s.chevron-left', color='#3b82f6'))
        self.btn_prev.setIconSize(QSize(10, 10))
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #3b82f6;
                font-size: 12px;
                font-weight: 600;
                padding: 4px 8px;
                text-align: left;
            }
            QPushButton:hover { color: #1d4ed8; text-decoration: underline; }
            QPushButton:disabled { color: #cbd5e1; text-decoration: none; }
        """)
        self.btn_prev.clicked.connect(self._go_prev_page)
        pag_layout.addWidget(self.btn_prev)
        
        # ✅ Bouton next
        self.btn_next = QPushButton("Suivant  ")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setIcon(qta.icon('fa5s.chevron-right', color='#3b82f6'))
        self.btn_next.setIconSize(QSize(10, 10))
        self.btn_next.setLayoutDirection(Qt.RightToLeft)
        self.btn_next.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #3b82f6;
                font-size: 12px;
                font-weight: 600;
                padding: 4px 8px;
                text-align: left;
            }
            QPushButton:hover { color: #1d4ed8; text-decoration: underline; }
            QPushButton:disabled { color: #cbd5e1; text-decoration: none; }
        """)
        self.btn_next.clicked.connect(self._go_next_page)
        pag_layout.addWidget(self.btn_next)
        
        layout.addWidget(pagination)
        
        return card
    
    def _build_secondary_actions(self):
        """Barre d'actions secondaires avec icônes FontAwesome"""
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        btn_style = """
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
                color: #1e293b;
                text-align: left;
            }
            QPushButton:hover {
                background: #f8fafc;
                border-color: %s;
                color: %s;
            }
        """
        
        # ✅ Bouton Planifier
        self.btn_planifier = QPushButton("  Planifier relances")
        self.btn_planifier.setCursor(Qt.PointingHandCursor)
        self.btn_planifier.setIcon(qta.icon('fa5s.calendar-plus', color='#7c3aed'))
        self.btn_planifier.setIconSize(QSize(14, 14))
        self.btn_planifier.setStyleSheet(btn_style % ("#8b5cf6", "#7c3aed"))
        self.btn_planifier.clicked.connect(self.planifier_relances_auto)
        layout.addWidget(self.btn_planifier)
        
        # ✅ Bouton Répartition
        self.btn_repartition = QPushButton("  Répartition")
        self.btn_repartition.setCursor(Qt.PointingHandCursor)
        self.btn_repartition.setIcon(qta.icon('fa5s.chart-pie', color='#0891b2'))
        self.btn_repartition.setIconSize(QSize(14, 14))
        self.btn_repartition.setStyleSheet(btn_style % ("#06b6d4", "#0891b2"))
        self.btn_repartition.clicked.connect(self.ouvrir_repartition)
        layout.addWidget(self.btn_repartition)
        
        # ✅ Bouton Écritures
        self.btn_comptabilite = QPushButton("  Écritures comptables")
        self.btn_comptabilite.setCursor(Qt.PointingHandCursor)
        self.btn_comptabilite.setIcon(qta.icon('fa5s.book', color='#7c3aed'))
        self.btn_comptabilite.setIconSize(QSize(14, 14))
        self.btn_comptabilite.setStyleSheet(btn_style % ("#8b5cf6", "#7c3aed"))
        self.btn_comptabilite.clicked.connect(self.ouvrir_comptabilite)
        layout.addWidget(self.btn_comptabilite)
        
        layout.addStretch()
        
        return wrapper
    
    # ═══════════════════════════════════════════════════════════════
    # CHARGEMENT DES DONNÉES — inchangé
    # ═══════════════════════════════════════════════════════════════
    
    def load_data(self):
        """Charge les sinistres dans le combo"""
        try:
            self.sinistre_combo.blockSignals(True)
            self.sinistre_combo.clear()
            self.sinistre_combo.addItem("Tous les sinistres", None)
            
            sinistres = self.controller.get_sinistres_recents()
            for s in sinistres:
                self.sinistre_combo.addItem(
                    f"{s.get('numero_sinistre')} - {s.get('branche', '')}",
                    s.get('id')
                )
            self.sinistre_combo.blockSignals(False)
            
            self._charger_alertes()
        except Exception as e:
            print(f"Erreur chargement sinistres: {e}")
    
    def on_sinistre_changed(self, index):
        """Charge les recours du sinistre sélectionné"""
        if index > 0:
            sinistre_id = self.sinistre_combo.currentData()
            if sinistre_id:
                self.current_sinistre_id = sinistre_id
                self.load_recours(sinistre_id)
        elif index == 0:
            self.current_sinistre_id = None
            self.load_recours(None)
    
    def load_recours(self, sinistre_id: Optional[int] = None):
        """Charge les recours dans le tableau"""
        try:
            if sinistre_id:
                recours = self.controller.get_recours_by_sinistre(sinistre_id)
            else:
                try:
                    recours = self.controller.get_all_recours(limit=200)
                except AttributeError:
                    recours = []
            
            query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""
            if query:
                recours = [
                    r for r in recours
                    if query in str(r.get('numero_recours', '')).lower()
                    or query in str(r.get('debiteur_nom', '')).lower()
                    or query in str(r.get('client_nom', '')).lower()
                ]
            
            self._total_recours = len(recours)
            
            start = (self._current_page - 1) * self._per_page
            end = start + self._per_page
            page_recours = recours[start:end]
            
            self._update_stats(recours)
            
            self.table_recours.setRowCount(len(page_recours))
            
            for i, rec in enumerate(page_recours):
                self._fill_row(i, rec)
            
            self._update_pagination(start, min(end, self._total_recours))
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement recours: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _fill_row(self, row: int, rec: dict):
        """Remplit une ligne du tableau"""
        # 0. N° Recours
        num_item = QTableWidgetItem(rec.get('numero_recours', ''))
        num_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        num_item.setForeground(QColor("#2563eb"))
        self.table_recours.setItem(row, 0, num_item)
        
        # 1. Client
        client = rec.get('client_nom') or rec.get('debiteur_nom') or '-'
        self.table_recours.setItem(row, 1, QTableWidgetItem(client))
        
        # 2. Assuré
        assure = rec.get('assure_nom') or rec.get('debiteur_nom') or '-'
        self.table_recours.setItem(row, 2, QTableWidgetItem(assure))
        
        # 3. Date Création
        date_creation = rec.get('date_ouverture') or rec.get('created_at', '')
        if date_creation:
            try:
                dt = datetime.fromisoformat(str(date_creation)[:19])
                date_str = dt.strftime("%d %b %Y")
            except Exception:
                date_str = str(date_creation)[:10]
        else:
            date_str = '-'
        self.table_recours.setItem(row, 3, QTableWidgetItem(date_str))
        
        # 4. Statut (badge)
        statut = rec.get('statut', '')
        badge = StatusBadge(statut)
        badge_container = QWidget()
        badge_layout = QHBoxLayout(badge_container)
        badge_layout.setContentsMargins(4, 6, 4, 6)
        badge_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        badge_layout.addWidget(badge)
        badge_layout.addStretch()
        self.table_recours.setCellWidget(row, 4, badge_container)
        
        # 5. Montant
        montant = rec.get('montant_reclame', 0) or 0
        montant_str = f"€{float(montant):,.2f}".replace(",", " ").replace(".", ",")
        montant_item = QTableWidgetItem(montant_str)
        montant_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_recours.setItem(row, 5, montant_item)
        
        # 6. Gestionnaire
        gestionnaire = rec.get('gestionnaire_nom') or rec.get('responsable_nom') or 'M. Moreau'
        self.table_recours.setItem(row, 6, QTableWidgetItem(gestionnaire))
        
        # 7. Actions avec icône ellipsis
        btn_actions = QPushButton()
        btn_actions.setCursor(Qt.PointingHandCursor)
        btn_actions.setFixedSize(32, 28)
        btn_actions.setIcon(qta.icon('fa5s.ellipsis-h', color='#64748b'))
        btn_actions.setIconSize(QSize(14, 14))
        btn_actions.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #f1f5f9;
                border-color: #cbd5e1;
            }
            QPushButton:pressed { background: #e2e8f0; }
        """)
        btn_actions.setToolTip("Actions")
        
        btn_actions.clicked.connect(
            lambda checked=False, r=rec, b=btn_actions: self._show_row_actions_menu(r, b)
        )
        
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(4, 6, 4, 6)
        actions_layout.setAlignment(Qt.AlignCenter)
        actions_layout.addWidget(btn_actions)
        self.table_recours.setCellWidget(row, 7, actions_container)
    
    def _update_stats(self, recours: list):
        """Met à jour les 4 cartes statistiques"""
        total = len(recours)
        aboutis_statuts = ['ABOUTI', 'ENCAISSE', 'PAYE', 'COMPTABILISE', 'CLOTURE']
        aboutis = sum(1 for r in recours if r.get('statut') in aboutis_statuts)
        attente_statuts = ['EN_ATTENTE_ENCAISSEMENT', 'OUVERT', 'CONTESTE']
        attente = sum(1 for r in recours if r.get('statut') in attente_statuts)
        encours = total - aboutis - attente
        if encours < 0:
            encours = 0
        
        for card, value in [
            (self.card_total, total),
            (self.card_aboutis, aboutis),
            (self.card_encours, encours),
            (self.card_attente, attente),
        ]:
            for lbl in card.findChildren(QLabel):
                if lbl.objectName() == "stat_value":
                    lbl.setText(f"{value:,}".replace(",", " "))
    
    def _update_pagination(self, start: int, end: int):
        """Met à jour la pagination"""
        self.lbl_pagination.setText(f"{start + 1}-{end} de {self._total_recours:,}".replace(",", " "))
        self.btn_prev.setEnabled(self._current_page > 1)
        self.btn_next.setEnabled(end < self._total_recours)
    
    def _go_prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self.load_recours(self.current_sinistre_id)
    
    def _go_next_page(self):
        if self._current_page * self._per_page < self._total_recours:
            self._current_page += 1
            self.load_recours(self.current_sinistre_id)
    
    def _on_search_changed(self, text: str):
        """Recherche en temps réel"""
        self._current_page = 1
        self.load_recours(self.current_sinistre_id)
    
    # ═══════════════════════════════════════════════════════════════
    # MENU D'ACTIONS PAR LIGNE (avec icônes FontAwesome)
    # ═══════════════════════════════════════════════════════════════
    
    def _menu_style(self) -> str:
        return """
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 6px;
                min-width: 230px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                color: #1e293b;
            }
            QMenu::item:selected {
                background: #eff6ff;
                color: #2563eb;
            }
            QMenu::item:disabled {
                color: #94a3b8;
            }
            QMenu::separator {
                height: 1px;
                background: #f1f5f9;
                margin: 4px 8px;
            }
        """
    
    def _show_row_actions_menu(self, recours: dict, button: QPushButton):
        """Affiche le menu d'actions pour un recours"""
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        statut = recours.get('statut', '')
        recours_numero = recours.get('numero_recours', '')
        
        # ✅ Consultation
        action_suivi = menu.addAction(
            qta.icon('fa5s.chart-line', color='#3b82f6'),
            "  Voir le suivi complet"
        )
        action_suivi.triggered.connect(
            lambda: self._action_suivi_from_menu(recours_numero)
        )
        
        action_details = menu.addAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir les détails"
        )
        action_details.triggered.connect(
            lambda: self._action_details_from_menu(recours)
        )
        
        menu.addSeparator()
        
        # ✅ Actions métier
        if statut in ["EN_ATTENTE_ENCAISSEMENT", "PARTIELLEMENT_ENCAISSE"]:
            if self.permissions_ui.peut('recours', 'UPDATE'):
                action_encaisser = menu.addAction(
                    qta.icon('fa5s.money-bill-wave', color='#22c55e'),
                    "  Encaisser"
                )
                action_encaisser.triggered.connect(
                    lambda: self._action_encaisser_from_menu(recours_numero)
                )
        
        if statut in ["OUVERT", "EN_INSTRUCTION", "RELANCE", "CONTESTE"]:
            if self.permissions_ui.peut('recours', 'UPDATE'):
                action_relancer = menu.addAction(
                    qta.icon('fa5s.bell', color='#f59e0b'),
                    "  Relancer"
                )
                action_relancer.triggered.connect(
                    lambda: self._action_relancer_from_menu(recours_numero)
                )
        
        if statut in ["ENCAISSE", "PARTIELLEMENT_ENCAISSE", "REVERSEMENT_EN_COURS"]:
            if self.permissions_ui.peut('recours', 'UPDATE'):
                action_rep = menu.addAction(
                    qta.icon('fa5s.chart-pie', color='#06b6d4'),
                    "  Répartition"
                )
                action_rep.triggered.connect(
                    lambda: self._action_repartition_from_menu(recours_numero)
                )
        
        if self.permissions_ui.peut('recours', 'READ'):
            action_ecr = menu.addAction(
                qta.icon('fa5s.book', color='#8b5cf6'),
                "  Écritures comptables"
            )
            action_ecr.triggered.connect(
                lambda: self._action_ecritures_from_menu(recours_numero)
            )
        
        menu.addSeparator()
        
        # ✅ Clôture / Annulation
        if statut not in ["CLOTURE", "REFUSE", "ANNULE"]:
            if self.permissions_ui.peut('recours', 'VALIDATE'):
                action_clot = menu.addAction(
                    qta.icon('fa5s.lock', color='#64748b'),
                    "  Clôturer"
                )
                action_clot.triggered.connect(
                    lambda: self._action_cloturer_from_menu(recours)
                )
        
        if statut not in ["CLOTURE", "REFUSE", "ANNULE"]:
            if self.permissions_ui.peut('recours', 'DELETE'):
                action_ann = menu.addAction(
                    qta.icon('fa5s.ban', color='#ef4444'),
                    "  Annuler"
                )
                action_ann.triggered.connect(
                    lambda: self._action_annuler_from_menu(recours)
                )
        
        menu.addSeparator()
        
        action_copy = menu.addAction(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier le N°"
        )
        action_copy.triggered.connect(lambda: self._copy_to_clipboard(recours_numero))
        
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
    
    # ═══════════════════════════════════════════════════════════════
    # EXPORT — inchangé
    # ═══════════════════════════════════════════════════════════════
    
    def _export_data(self):
        """Exporte les données (CSV simple)"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les recours",
            f"recours_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV (*.csv)"
        )
        if not path:
            return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "N° Recours", "Client", "Assuré", "Date Création",
                    "Statut", "Montant", "Gestionnaire"
                ])
                for row in range(self.table_recours.rowCount()):
                    values = []
                    for col in range(7):
                        item = self.table_recours.item(row, col)
                        values.append(item.text() if item else '')
                    writer.writerow(values)
            
            QMessageBox.information(
                self, "Export réussi",
                f"{self.table_recours.rowCount()} recours exportés vers:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # CRÉATION DE RECOURS — inchangé
    # ═══════════════════════════════════════════════════════════════
    
    def creer_recours(self):
        """Crée un nouveau recours"""
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        conditions = self.controller.verifier_conditions_recours(self.current_sinistre_id)
        
        if not conditions.get('peut_creer'):
            QMessageBox.warning(
                self, "Condition CDC non remplie",
                f"Impossible de créer un recours :\n\n"
                f"{conditions.get('raison', 'Condition non remplie')}"
            )
            return
        
        sinistre_info = {}
        try:
            from addons.sinistres.controllers.sinistre_controller import SinistreController
            sc = SinistreController()
            sc.set_current_user(self.user)
            sinistre_data = sc.get_sinistre(self.current_sinistre_id)
            
            if sinistre_data:
                sinistre_info = {
                    'numero_sinistre': sinistre_data.get('numero_sinistre', 'N/A'),
                    'client_nom': sinistre_data.get('client_nom', 'N/A'),
                    'branche': sinistre_data.get('branche', 'N/A'),
                    'montant_regle': conditions.get('montant_regle', 0),
                    'taux_responsabilite': conditions.get('taux_responsabilite', 1),
                }
        except Exception as e:
            print(f"⚠️ Erreur récupération infos sinistre: {e}")
        
        from addons.sinistres.views.recours_dialog import RecoursDialog
        dialog = RecoursDialog(
            sinistre_id=self.current_sinistre_id,
            recours_controller=self.controller,
            user=self.user,
            sinistre_info=sinistre_info,
            parent=self
        )
        dialog.recours_created.connect(self._on_recours_created)
        dialog.exec()
    
    def _on_recours_created(self, data: dict):
        self.load_recours(self.current_sinistre_id)
        QMessageBox.information(self, "Succès", "Recours créé avec succès !")
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS MÉTIER — inchangées
    # ═══════════════════════════════════════════════════════════════
    
    def _on_recours_cell_clicked(self, row: int, col: int):
        if col == 7:
            return
        num_item = self.table_recours.item(row, 0)
        if not num_item:
            return
        try:
            rec_data = self.controller.get_recours_by_numero(num_item.text())
            if rec_data:
                self.selected_recours_id = rec_data.get('id')
        except Exception:
            pass
    
    def _charger_alertes(self):
        try:
            alertes = self.controller.get_alertes_recours()
            self.alertes_widget.set_alertes(alertes)
        except Exception as e:
            print(f"❌ Erreur chargement alertes : {e}")
    
    def _on_alerte_clicked(self, alerte: dict):
        recours_id = alerte.get('recours_id')
        if not recours_id:
            return
        for i in range(self.table_recours.rowCount()):
            num_item = self.table_recours.item(i, 0)
            if not num_item:
                continue
            try:
                rec = self.controller.get_recours_by_numero(num_item.text())
                if rec and rec.get('id') == recours_id:
                    self.table_recours.selectRow(i)
                    break
            except Exception:
                continue
    
    def ouvrir_repartition(self):
        recours_data = self._get_selected_recours()
        if not recours_data:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
            return
        
        statut = recours_data.get('statut', '')
        if statut not in ["ENCAISSE", "PARTIELLEMENT_ENCAISSE"]:
            QMessageBox.warning(
                self, "Attention",
                f"Seul un recours encaissé peut être réparti (statut: {statut})"
            )
            return
        
        try:
            dialog = RepartitionRecoursDialog(
                recours_id=recours_data.get('id'),
                recours_info=recours_data,
                recours_controller=self.controller,
                user=self.user,
                parent=self,
            )
            dialog.repartition_validee.connect(self._on_repartition_validee)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def _on_repartition_validee(self, repartitions: list):
        self.load_recours(self.current_sinistre_id)
        QMessageBox.information(
            self, "Succès",
            f"Répartition enregistrée : {len(repartitions)} part(s)"
        )
    
    def ouvrir_comptabilite(self):
        recours_data = self._get_selected_recours()
        if not recours_data:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un recours")
            return
        
        try:
            dialog = ComptabiliteRecoursDialog(
                recours_id=recours_data.get('id'),
                recours_info=recours_data,
                comptabilite_controller=self.comptabilite_controller,
                user=self.user,
                parent=self,
            )
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def planifier_relances_auto(self):
        reply = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous planifier automatiquement les relances pour tous les recours ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.planifier_relances_auto()
                QMessageBox.information(
                    self, "Planification terminée",
                    f"{result.get('planifiees', 0)} relances planifiées\n"
                    f"{result.get('erreurs', 0)} erreurs"
                )
                self.load_recours(self.current_sinistre_id)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    # ═══════════════════════════════════════════════════════════════
    # HELPERS — inchangés
    # ═══════════════════════════════════════════════════════════════
    
    def _get_selected_recours(self) -> Optional[dict]:
        row = self.table_recours.currentRow()
        if row < 0:
            return None
        num_item = self.table_recours.item(row, 0)
        if not num_item:
            return None
        try:
            return self.controller.get_recours_by_numero(num_item.text())
        except Exception:
            return None
    
    def get_selected_recours_id(self) -> Optional[int]:
        rec = self._get_selected_recours()
        return rec.get('id') if rec else None
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS DU MENU CONTEXTUEL — inchangées
    # ═══════════════════════════════════════════════════════════════
    
    def _action_suivi_from_menu(self, recours_numero: str):
        try:
            recours_data = self.controller.get_recours_by_numero(recours_numero)
            if not recours_data:
                return
            from addons.sinistres.views.recours_suivi_dialog import RecoursSuiviDialog
            dialog = RecoursSuiviDialog(
                recours_id=recours_data.get('id'),
                recours_info=recours_data,
                recours_controller=self.controller,
                comptabilite_controller=self.comptabilite_controller,
                user=self.user,
                parent=self,
            )
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def _action_details_from_menu(self, recours_data: dict):
        QMessageBox.information(
            self,
            f"Recours {recours_data.get('numero_recours', 'N/A')}",
            f"<b>Type :</b> {recours_data.get('type_recours', 'N/A')}<br>"
            f"<b>Débiteur :</b> {recours_data.get('debiteur_nom', 'N/A')}<br>"
            f"<b>Montant réclamé :</b> {float(recours_data.get('montant_reclame', 0)):,.0f} FCFA<br>"
            f"<b>Montant accepté :</b> {float(recours_data.get('montant_accepte', 0) or 0):,.0f} FCFA<br>"
            f"<b>Montant encaissé :</b> {float(recours_data.get('montant_encaisse', 0) or 0):,.0f} FCFA<br>"
            f"<b>Solde :</b> {float(recours_data.get('solde', 0) or 0):,.0f} FCFA<br>"
            f"<b>Date ouverture :</b> {str(recours_data.get('date_ouverture', ''))[:10]}<br>"
            f"<b>Statut :</b> {recours_data.get('statut', 'N/A')}"
        )
    
    def _action_encaisser_from_menu(self, recours_numero: str):
        self._select_row_by_numero(recours_numero)
        self._do_encaisser()
    
    def _action_relancer_from_menu(self, recours_numero: str):
        self._select_row_by_numero(recours_numero)
        self._do_relancer()
    
    def _action_repartition_from_menu(self, recours_numero: str):
        self._select_row_by_numero(recours_numero)
        self.ouvrir_repartition()
    
    def _action_ecritures_from_menu(self, recours_numero: str):
        self._select_row_by_numero(recours_numero)
        self.ouvrir_comptabilite()
    
    def _action_reversements_from_menu(self, recours_numero: str):
        QMessageBox.information(
            self, "Info",
            "Le dialogue de reversement sera disponible prochainement."
        )
    
    def _action_cloturer_from_menu(self, recours_data: dict):
        recours_numero = recours_data.get('numero_recours', 'N/A')
        from PySide6.QtWidgets import QInputDialog
        motif, ok = QInputDialog.getMultiLineText(
            self, f"Clôturer {recours_numero}",
            "Motif de clôture :", ""
        )
        if not ok or not motif.strip():
            return
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Clôturer le recours {recours_numero} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            result = self.controller.changer_statut_recours(
                recours_data.get('id'), "CLOTURE", motif=motif
            )
            if result:
                QMessageBox.information(self, "Succès", "Recours clôturé")
                self.load_recours(self.current_sinistre_id)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _action_annuler_from_menu(self, recours_data: dict):
        recours_numero = recours_data.get('numero_recours', 'N/A')
        from PySide6.QtWidgets import QInputDialog
        motif, ok = QInputDialog.getMultiLineText(
            self, f"Annuler {recours_numero}",
            "Motif d'annulation :", ""
        )
        if not ok or not motif.strip():
            return
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Annuler le recours {recours_numero} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            result = self.controller.changer_statut_recours(
                recours_data.get('id'), "REFUSE", motif=motif
            )
            if result:
                QMessageBox.information(self, "Succès", "Recours annulé")
                self.load_recours(self.current_sinistre_id)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _do_encaisser(self):
        recours_data = self._get_selected_recours()
        if not recours_data:
            return
        statut = recours_data.get('statut', '')
        if statut not in ["EN_ATTENTE_ENCAISSEMENT", "PARTIELLEMENT_ENCAISSE"]:
            QMessageBox.warning(
                self, "Attention",
                f"Statut incompatible pour encaissement : {statut}"
            )
            return
        try:
            from addons.sinistres.views.encaissement_dialog import EncaissementDialog
            dialog = EncaissementDialog(
                recours_id=recours_data.get('id'),
                recours_info=recours_data,
                recours_controller=self.controller,
                user=self.user,
                parent=self,
            )
            dialog.encaissement_added.connect(self._on_encaissement_added)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def _on_encaissement_added(self, data: dict):
        self.load_recours(self.current_sinistre_id)
        QMessageBox.information(
            self, "Succès",
            f"Encaissement de {data.get('montant', 0):,.0f} FCFA enregistré\n"
            f"Solde : {data.get('solde_restant', 0):,.0f} FCFA"
        )
    
    def _do_relancer(self):
        recours_data = self._get_selected_recours()
        if not recours_data:
            return
        try:
            from addons.sinistres.views.relance_dialog import RelanceDialog
            dialog = RelanceDialog(
                recours_id=recours_data.get('id'),
                recours_info=recours_data,
                recours_controller=self.controller,
                user=self.user,
                parent=self,
            )
            dialog.relance_added.connect(self._on_relance_added)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def _on_relance_added(self, data: dict):
        self.load_recours(self.current_sinistre_id)
        QMessageBox.information(self, "Succès", "Relance ajoutée")
    
    def _select_row_by_numero(self, recours_numero: str):
        for i in range(self.table_recours.rowCount()):
            item = self.table_recours.item(i, 0)
            if item and item.text() == recours_numero:
                self.table_recours.selectRow(i)
                return
    
    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copié", f"'{text}' copié")