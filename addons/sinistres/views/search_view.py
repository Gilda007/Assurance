

# # """
# # Vue principale du module LOMETA Sinistres
# # Interface utilisateur complète pour la gestion des sinistres
# # """
# # from PySide6.QtWidgets import (
# #     QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
# #     QHeaderView, QLabel, QPushButton, QListWidgetItem, QStackedWidget,
# #     QListWidget, QFrame, QMessageBox, QDialog, QGraphicsDropShadowEffect,
# #     QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
# #     QFormLayout, QGroupBox, QTabWidget, QSplitter, QScrollArea,
# #     QProgressBar, QToolBar, QMenu, QCheckBox, QRadioButton
# # )
# # from PySide6.QtCore import Qt, QSize, Signal, Slot, QDate
# # from PySide6.QtGui import QColor, QIcon, QFont

# # from datetime import datetime, timedelta
# # from typing import Optional, List, Dict, Any

# # # Import des contrôleurs
# # from addons.sinistres.controllers.sinistre_controller import SinistreController
# # from addons.sinistres.controllers.referentiel_controller import ReferentielController
# # from addons.sinistres.controllers.expertise_controller import ExpertiseController
# # from addons.sinistres.controllers.evaluation_controller import EvaluationController
# # from addons.sinistres.controllers.reglement_controller import ReglementController
# # from addons.sinistres.controllers.recours_controller import RecoursController

# # # Import des vues détaillées
# # from addons.sinistres.views.dossier_360 import Dossier360View
# # from addons.sinistres.views.parametres_page import ParametresPage
# # from addons.sinistres.views.tableau_base import TableauActions

# # # ============================================================
# # # PAGE 3: RECHERCHE (avec intégration Dossier 360°)
# # # ============================================================

# # class RecherchePage(QWidget):
# #     """Page de recherche des sinistres"""
    
# #     def __init__(
# #         self,
# #         sinistre_controller,
# #         referentiel_controller,
# #         expertise_controller,
# #         evaluation_controller,
# #         reglement_controller,
# #         recours_controller,
# #         user
# #     ):
# #         super().__init__()
# #         self.sinistre_controller = sinistre_controller
# #         self.referentiel_controller = referentiel_controller
# #         self.expertise_controller = expertise_controller
# #         self.evaluation_controller = evaluation_controller
# #         self.reglement_controller = reglement_controller
# #         self.recours_controller = recours_controller
# #         self.user = user
# #         self.setup_ui()
    
# #     def setup_ui(self):
# #         layout = QVBoxLayout(self)
# #         layout.setContentsMargins(25, 25, 25, 25)
# #         layout.setSpacing(15)
        
# #         # En-tête
# #         header = QLabel("🔍 Recherche de sinistres")
# #         header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
# #         layout.addWidget(header)
        
# #         # Barre de recherche
# #         search_layout = QHBoxLayout()
        
# #         self.input_recherche = QLineEdit()
# #         self.input_recherche.setPlaceholderText("🔎 Numéro sinistre, client, contrat...")
# #         self.input_recherche.setStyleSheet("""
# #             QLineEdit {
# #                 padding: 10px 15px;
# #                 border: 1px solid #e2e8f0;
# #                 border-radius: 10px;
# #                 font-size: 14px;
# #             }
# #             QLineEdit:focus {
# #                 border: 2px solid #1a73e8;
# #             }
# #         """)
# #         self.input_recherche.returnPressed.connect(self.rechercher)
# #         search_layout.addWidget(self.input_recherche)
        
# #         self.btn_rechercher = QPushButton("Rechercher")
# #         self.btn_rechercher.setStyleSheet("""
# #             QPushButton {
# #                 background-color: #1a73e8;
# #                 color: white;
# #                 padding: 10px 25px;
# #                 border-radius: 10px;
# #                 font-weight: bold;
# #             }
# #             QPushButton:hover {
# #                 background-color: #1557b0;
# #             }
# #         """)
# #         self.btn_rechercher.clicked.connect(self.rechercher)
# #         search_layout.addWidget(self.btn_rechercher)
        
# #         layout.addLayout(search_layout)
        
# #         # Filtres rapides
# #         filters_layout = QHBoxLayout()
# #         filters_layout.setSpacing(10)
        
# #         self.filter_statut = QComboBox()
# #         self.filter_statut.addItem("Tous les statuts", "")
# #         for statut in ["OUVERT", "EN_INSTRUCTION", "EN_EXPERTISE", "EN_EVALUATION", "VALIDE", "EN_REGLEMENT", "EN_RECOURS", "CLOTURE"]:
# #             self.filter_statut.addItem(statut, statut)
# #         filters_layout.addWidget(QLabel("Statut:"))
# #         filters_layout.addWidget(self.filter_statut)
        
# #         self.filter_branche = QComboBox()
# #         self.filter_branche.addItem("Toutes les branches", "")
# #         filters_layout.addWidget(QLabel("Branche:"))
# #         filters_layout.addWidget(self.filter_branche)
        
# #         filters_layout.addStretch()
# #         layout.addLayout(filters_layout)
        
# #         # Résultats
# #         layout.addWidget(QLabel("📋 Résultats"))
        
# #         self.table_resultats = QTableWidget()
# #         self.table_resultats.setColumnCount(7)
# #         self.table_resultats.setHorizontalHeaderLabels([
# #             "N° Sinistre", "Référence", "Client", "Branche", "Date", "Statut", "Montant"
# #         ])
# #         self.table_resultats.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
# #         self.table_resultats.setAlternatingRowColors(True)
# #         self.table_resultats.setStyleSheet("""
# #             QTableWidget {
# #                 border: 1px solid #e2e8f0;
# #                 border-radius: 8px;
# #                 gridline-color: #f1f5f9;
# #             }
# #             QTableWidget::item {
# #                 padding: 8px;
# #             }
# #             QTableWidget::item:hover {
# #                 background-color: #f1f5f9;
# #             }
# #             QHeaderView::section {
# #                 background-color: #f8fafc;
# #                 padding: 8px;
# #                 font-weight: bold;
# #                 border: none;
# #                 border-bottom: 1px solid #e2e8f0;
# #             }
# #         """)
# #         self.table_resultats.setSortingEnabled(True)
# #         self.table_resultats.doubleClicked.connect(self._on_row_double_clicked)
# #         layout.addWidget(self.table_resultats)
        
# #         # Charger les branches pour le filtre
# #         self._load_branches()
    
# #     def _load_branches(self):
# #         """Charge les branches pour le filtre"""
# #         try:
# #             branches = self.referentiel_controller.get_referentiels_by_famille("branches")
# #             for b in branches:
# #                 self.filter_branche.addItem(b.get('libelle', ''), b.get('code', ''))
# #         except Exception as e:
# #             print(f"Erreur chargement branches: {e}")
    
# #     def rechercher(self):
# #         """Exécute la recherche"""
# #         try:
# #             criteres = {}
            
# #             text = self.input_recherche.text().strip()
# #             if text:
# #                 criteres['numero_sinistre'] = text
            
# #             statut = self.filter_statut.currentData()
# #             if statut:
# #                 criteres['statut'] = statut
            
# #             branche = self.filter_branche.currentData()
# #             if branche:
# #                 criteres['branche'] = branche
            
# #             sinistres = self.sinistre_controller.rechercher_sinistres(criteres)
# #             self._afficher_resultats(sinistres)
            
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche: {str(e)}")
    
# #     def _afficher_resultats(self, sinistres: List[dict]):
# #         """Affiche les résultats de la recherche"""
# #         self.table_resultats.setRowCount(len(sinistres))
        
# #         for i, s in enumerate(sinistres):
# #             self.table_resultats.setItem(i, 0, QTableWidgetItem(s.get('numero_sinistre', '')))
# #             self.table_resultats.setItem(i, 1, QTableWidgetItem(s.get('numero_reference', '') or '-'))
# #             self.table_resultats.setItem(i, 2, QTableWidgetItem(str(s.get('client_id', ''))))
# #             self.table_resultats.setItem(i, 3, QTableWidgetItem(s.get('branche', '')))
# #             self.table_resultats.setItem(i, 4, QTableWidgetItem(s.get('date_survenance', '')[:10] if s.get('date_survenance') else ''))
            
# #             statut_item = QTableWidgetItem(s.get('statut', ''))
# #             statut_colors = {
# #                 'OUVERT': '#f59e0b',
# #                 'CLOTURE': '#22c55e',
# #                 'EN_INSTRUCTION': '#3b82f6',
# #                 'EN_EXPERTISE': '#8b5cf6',
# #                 'EN_EVALUATION': '#ec4899',
# #                 'VALIDE': '#06b6d4',
# #                 'EN_REGLEMENT': '#f97316',
# #                 'EN_RECOURS': '#ef4444'
# #             }
# #             color = statut_colors.get(s.get('statut', ''), '#64748b')
# #             statut_item.setBackground(QColor(color))
# #             statut_item.setForeground(QColor('white'))
# #             self.table_resultats.setItem(i, 5, statut_item)
            
# #             self.table_resultats.setItem(i, 6, QTableWidgetItem(f"{s.get('montant_net', 0):,.0f}"))
            
# #             # Stocker l'ID pour l'ouverture du dossier 360°
# #             self.table_resultats.item(i, 0).setData(Qt.UserRole, s.get('id'))

# #     def open_dossier_360(self, sinistre_id: int):
# #         """Ouvre la vue Dossier 360°"""
# #         try:
# #             dossier = Dossier360View(
# #                 sinistre_id=sinistre_id,
# #                 sinistre_controller=self.sinistre_controller,
# #                 referentiel_controller=self.referentiel_controller,
# #                 expertise_controller=self.expertise_controller,
# #                 evaluation_controller=self.evaluation_controller,
# #                 reglement_controller=self.reglement_controller,
# #                 recours_controller=self.recours_controller,
# #                 user=self.user
# #             )
# #             # Remplacer la page courante par le dossier
# #             parent = self.parent()
# #             if hasattr(parent, 'container'):
# #                 # Ajouter comme page temporaire
# #                 parent.container.addWidget(dossier)
# #                 parent.container.setCurrentWidget(dossier)
# #             else:
# #                 QMessageBox.warning(self, "Erreur", "Impossible d'ouvrir le dossier 360°")
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", f"Erreur d'ouverture du dossier: {str(e)}")
    
# #     def refresh(self):
# #         """Rafraîchit la page"""
# #         if self.filter_branche.count() <= 1:
# #             self._load_branches()

# #     def _on_row_double_clicked(self, index):
# #         """Ouvre le Dossier 360° du sinistre sélectionné"""
# #         row = index.row()
# #         if row >= 0:
# #             sinistre_id = self.table_resultats.item(row, 0).data(Qt.UserRole)
# #             self.open_mission_detail(row)
# #             if sinistre_id:
# #                 self.open_dossier_360(sinistre_id)

# #     def open_dossier_360(self, sinistre_id: int):
# #         """Ouvre la vue Dossier 360°"""
# #         try:
# #             dossier = Dossier360View(
# #                 sinistre_id=sinistre_id,
# #                 sinistre_controller=self.sinistre_controller,
# #                 referentiel_controller=self.referentiel_controller,
# #                 expertise_controller=self.expertise_controller,
# #                 evaluation_controller=self.evaluation_controller,
# #                 reglement_controller=self.reglement_controller,
# #                 recours_controller=self.recours_controller,
# #                 user=self.user
# #             )
# #             parent = self.parent()
# #             if hasattr(parent, 'container'):
# #                 parent.container.addWidget(dossier)
# #                 parent.container.setCurrentWidget(dossier)
# #             else:
# #                 QMessageBox.warning(self, "Erreur", "Impossible d'ouvrir le dossier 360°")
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", f"Erreur d'ouverture du dossier: {str(e)}")

# #     def open_mission_detail(self, mission_numero: str):
# #         """Ouvre le détail d'une mission"""
# #         QMessageBox.information(self, "Détail", f"Détail de la mission {mission_numero}")


# """
# Vue principale du module LOMETA Sinistres
# Interface utilisateur complète pour la recherche des sinistres
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
# from PySide6.QtGui import QColor, QIcon, QFont, QAction

# from datetime import datetime, timedelta
# from typing import Optional, List, Dict, Any

# # Import des contrôleurs
# from addons.sinistres.controllers.sinistre_controller import SinistreController
# from addons.sinistres.controllers.referentiel_controller import ReferentielController
# from addons.sinistres.controllers.expertise_controller import ExpertiseController
# from addons.sinistres.controllers.evaluation_controller import EvaluationController
# from addons.sinistres.controllers.reglement_controller import ReglementController
# from addons.sinistres.controllers.recours_controller import RecoursController

# # Import des vues détaillées
# from addons.sinistres.views.dossier_360 import Dossier360View
# from addons.sinistres.views.parametres_page import ParametresPage


# # ═══════════════════════════════════════════════════════════════════
# # HELPERS
# # ═══════════════════════════════════════════════════════════════════

# def _safe_bool(value) -> bool:
#     """Convertit n'importe quelle valeur en booléen sûr"""
#     if value is None:
#         return False
#     if isinstance(value, str):
#         return value.strip().lower() not in ('', 'none', 'null', '0', 'false')
#     return bool(value)


# # ═══════════════════════════════════════════════════════════════════
# # WIDGETS PERSONNALISÉS
# # ═══════════════════════════════════════════════════════════════════

# class StatusBadge(QLabel):
#     """Badge arrondi pour le statut d'un sinistre"""
    
#     STATUS_STYLES = {
#         'OUVERT':         ("#fef3c7", "#92400e", "Ouvert"),
#         'EN_INSTRUCTION': ("#dbeafe", "#1e40af", "En instruction"),
#         'EN_EXPERTISE':   ("#ede9fe", "#6d28d9", "En expertise"),
#         'EN_EVALUATION':  ("#fce7f3", "#9f1239", "En évaluation"),
#         'VALIDE':         ("#cffafe", "#155e75", "Validé"),
#         'EN_REGLEMENT':   ("#ffedd5", "#9a3412", "En règlement"),
#         'EN_RECOURS':     ("#fee2e2", "#991b1b", "En recours"),
#         'CLOTURE':        ("#d1fae5", "#065f46", "Clôturé"),
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

# class RecherchePage(QWidget):
#     """Page de recherche des sinistres — Design moderne v2.0"""
    
#     def __init__(
#         self,
#         sinistre_controller,
#         referentiel_controller,
#         expertise_controller,
#         evaluation_controller,
#         reglement_controller,
#         recours_controller,
#         user
#     ):
#         super().__init__()
#         self.sinistre_controller = sinistre_controller
#         self.referentiel_controller = referentiel_controller
#         self.expertise_controller = expertise_controller
#         self.evaluation_controller = evaluation_controller
#         self.reglement_controller = reglement_controller
#         self.recours_controller = recours_controller
#         self.user = user
        
#         # Pagination
#         self._current_page = 1
#         self._per_page = 20
#         self._total_resultats = 0
#         self._all_resultats = []
        
#         self.setup_ui()
#         self._load_branches()
#         # Charger tous les sinistres au démarrage
#         self.rechercher()
    
#     # ═══════════════════════════════════════════════════════════════
#     # CONSTRUCTION DE L'INTERFACE
#     # ═══════════════════════════════════════════════════════════════
    
#     def setup_ui(self):
#         self.setStyleSheet("background: #f1f5f9;")
        
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(24, 20, 24, 20)
#         layout.setSpacing(16)
        
#         # ─── 1. HEADER ───
#         layout.addWidget(self._build_header())
        
#         # ─── 2. BARRE DE RECHERCHE ───
#         layout.addWidget(self._build_search_bar())
        
#         # ─── 3. FILTRES RAPIDES ───
#         layout.addWidget(self._build_filters_bar())
        
#         # ─── 4. TABLE CARD ───
#         layout.addWidget(self._build_table_card(), 1)
    
#     def _build_header(self):
#         """En-tête de la page"""
#         frame = QFrame()
#         frame.setStyleSheet("background: transparent; border: none;")
#         layout = QHBoxLayout(frame)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(12)
        
#         title = QLabel("Recherche de Sinistres")
#         title.setStyleSheet("""
#             font-size: 26px;
#             font-weight: 800;
#             color: #0f172a;
#             background: transparent;
#         """)
#         layout.addWidget(title)
        
#         # Sous-titre avec compteur
#         self.lbl_count = QLabel("")
#         self.lbl_count.setStyleSheet("""
#             color: #64748b;
#             font-size: 13px;
#             background: transparent;
#             padding-top: 8px;
#         """)
#         layout.addWidget(self.lbl_count, 0, Qt.AlignBottom)
        
#         layout.addStretch()
        
#         # Bouton Dossier 360°
#         self.btn_dossier = QPushButton("  📁  Ouvrir Dossier 360°")
#         self.btn_dossier.setCursor(Qt.PointingHandCursor)
#         self.btn_dossier.setFixedHeight(38)
#         self.btn_dossier.setStyleSheet("""
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
#             QPushButton:disabled {
#                 background: #cbd5e1;
#                 color: #94a3b8;
#             }
#         """)
#         self.btn_dossier.clicked.connect(self._open_selected_dossier)
#         self.btn_dossier.setEnabled(False)
#         layout.addWidget(self.btn_dossier)
        
#         return frame
    
#     def _build_search_bar(self):
#         """Barre de recherche principale"""
#         frame = QFrame()
#         frame.setStyleSheet("""
#             QFrame {
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 12px;
#             }
#         """)
#         layout = QHBoxLayout(frame)
#         layout.setContentsMargins(16, 12, 16, 12)
#         layout.setSpacing(12)
        
#         # Icône
#         icon = QLabel("🔎")
#         icon.setStyleSheet("font-size: 18px; background: transparent;")
#         layout.addWidget(icon)
        
#         # Input
#         self.input_recherche = QLineEdit()
#         self.input_recherche.setPlaceholderText(
#             "Rechercher par numéro de sinistre, référence, client, contrat, immatriculation..."
#         )
#         self.input_recherche.setStyleSheet("""
#             QLineEdit {
#                 border: none;
#                 background: transparent;
#                 font-size: 14px;
#                 color: #1e293b;
#                 padding: 4px 8px;
#             }
#             QLineEdit:focus {
#                 background: #f8fafc;
#                 border-radius: 6px;
#             }
#         """)
#         self.input_recherche.returnPressed.connect(self.rechercher)
#         self.input_recherche.textChanged.connect(self._on_search_text_changed)
#         layout.addWidget(self.input_recherche, 1)
        
#         # Bouton effacer (visible si texte)
#         self.btn_clear = QPushButton("✕")
#         self.btn_clear.setFixedSize(28, 28)
#         self.btn_clear.setCursor(Qt.PointingHandCursor)
#         self.btn_clear.setStyleSheet("""
#             QPushButton {
#                 background: #f1f5f9;
#                 border: none;
#                 border-radius: 14px;
#                 color: #64748b;
#                 font-size: 12px;
#             }
#             QPushButton:hover { background: #e2e8f0; color: #1e293b; }
#         """)
#         self.btn_clear.clicked.connect(self._clear_search)
#         self.btn_clear.setVisible(False)
#         layout.addWidget(self.btn_clear)
        
#         # Bouton rechercher
#         self.btn_rechercher = QPushButton("  Rechercher")
#         self.btn_rechercher.setCursor(Qt.PointingHandCursor)
#         self.btn_rechercher.setFixedHeight(36)
#         self.btn_rechercher.setStyleSheet("""
#             QPushButton {
#                 background: #2563eb;
#                 color: white;
#                 border: none;
#                 border-radius: 8px;
#                 padding: 8px 20px;
#                 font-size: 13px;
#                 font-weight: 700;
#             }
#             QPushButton:hover { background: #1d4ed8; }
#         """)
#         self.btn_rechercher.clicked.connect(self.rechercher)
#         layout.addWidget(self.btn_rechercher)
        
#         return frame
    
#     def _build_filters_bar(self):
#         """Barre de filtres"""
#         frame = QFrame()
#         frame.setStyleSheet("""
#             QFrame {
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 12px;
#             }
#         """)
#         layout = QHBoxLayout(frame)
#         layout.setContentsMargins(16, 12, 16, 12)
#         layout.setSpacing(14)
        
#         def make_filter(label_text, icon):
#             box = QVBoxLayout()
#             box.setSpacing(4)
#             lbl = QLabel(f"{icon} {label_text}")
#             lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; background: transparent;")
#             box.addWidget(lbl)
#             return box
        
#         # Filtre statut
#         statut_box = make_filter("Statut", "📌")
#         self.filter_statut = QComboBox()
#         self.filter_statut.addItem("Tous les statuts", "")
#         for statut_code, statut_label in [
#             ("OUVERT", "Ouvert"),
#             ("EN_INSTRUCTION", "En instruction"),
#             ("EN_EXPERTISE", "En expertise"),
#             ("EN_EVALUATION", "En évaluation"),
#             ("VALIDE", "Validé"),
#             ("EN_REGLEMENT", "En règlement"),
#             ("EN_RECOURS", "En recours"),
#             ("CLOTURE", "Clôturé"),
#         ]:
#             self.filter_statut.addItem(statut_label, statut_code)
#         self.filter_statut.setStyleSheet(self._combo_style())
#         self.filter_statut.currentIndexChanged.connect(self._on_filter_changed)
#         statut_box.addWidget(self.filter_statut)
#         layout.addLayout(statut_box)
        
#         # Filtre branche
#         branche_box = make_filter("Branche", "🏢")
#         self.filter_branche = QComboBox()
#         self.filter_branche.addItem("Toutes les branches", "")
#         self.filter_branche.setStyleSheet(self._combo_style())
#         self.filter_branche.currentIndexChanged.connect(self._on_filter_changed)
#         branche_box.addWidget(self.filter_branche)
#         layout.addLayout(branche_box)
        
#         # Filtre période
#         periode_box = make_filter("Période", "📅")
#         self.filter_periode = QComboBox()
#         self.filter_periode.addItems([
#             "Toutes les périodes", "30 derniers jours", "3 derniers mois",
#             "6 derniers mois", "12 derniers mois", "Année en cours"
#         ])
#         self.filter_periode.setStyleSheet(self._combo_style())
#         self.filter_periode.currentIndexChanged.connect(self._on_filter_changed)
#         periode_box.addWidget(self.filter_periode)
#         layout.addLayout(periode_box)
        
#         layout.addStretch()
        
#         # Bouton reset filtres
#         btn_reset = QPushButton("  ↻  Réinitialiser")
#         btn_reset.setCursor(Qt.PointingHandCursor)
#         btn_reset.setFixedHeight(34)
#         btn_reset.setStyleSheet("""
#             QPushButton {
#                 background: transparent;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 6px 14px;
#                 font-size: 12px;
#                 color: #64748b;
#                 font-weight: 500;
#             }
#             QPushButton:hover {
#                 background: #f8fafc;
#                 border-color: #cbd5e1;
#                 color: #1e293b;
#             }
#         """)
#         btn_reset.clicked.connect(self._reset_filters)
#         layout.addWidget(btn_reset)
        
#         return frame
    
#     def _combo_style(self) -> str:
#         return """
#             QComboBox {
#                 background: #f8fafc;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 6px 10px;
#                 font-size: 12px;
#                 color: #1e293b;
#                 min-width: 160px;
#             }
#             QComboBox:hover { border-color: #3b82f6; background: white; }
#             QComboBox::drop-down { border: none; width: 20px; }
#             QComboBox::down-arrow {
#                 image: none;
#                 border-left: 4px solid transparent;
#                 border-right: 4px solid transparent;
#                 border-top: 5px solid #64748b;
#                 margin-right: 6px;
#             }
#         """
    
#     def _build_table_card(self):
#         """Carte avec le tableau des résultats"""
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
        
#         # ─── Header ───
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
        
#         title = QLabel("Résultats de la recherche")
#         title.setStyleSheet("""
#             font-size: 16px;
#             font-weight: 700;
#             color: #0f172a;
#             background: transparent;
#         """)
#         header_layout.addWidget(title)
#         header_layout.addStretch()
        
#         # Export
#         btn_export = QPushButton("  ⬇  Export CSV")
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
#         self.table_resultats = QTableWidget()
#         self.table_resultats.setColumnCount(8)
#         self.table_resultats.setHorizontalHeaderLabels([
#             "N° Sinistre", "Référence", "Client", "Branche",
#             "Date", "Statut", "Montant", "Actions"
#         ])
        
#         self.table_resultats.setStyleSheet("""
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
        
#         self.table_resultats.setAlternatingRowColors(False)
#         self.table_resultats.verticalHeader().setVisible(False)
#         self.table_resultats.verticalHeader().setDefaultSectionSize(52)
#         self.table_resultats.setSelectionBehavior(QAbstractItemView.SelectRows)
#         self.table_resultats.setSelectionMode(QAbstractItemView.SingleSelection)
#         self.table_resultats.setEditTriggers(QAbstractItemView.NoEditTriggers)
#         self.table_resultats.setShowGrid(False)
#         self.table_resultats.setSortingEnabled(False)  # On gère le tri nous-mêmes
        
#         # Largeurs
#         header_view = self.table_resultats.horizontalHeader()
#         header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
#         header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
#         header_view.setSectionResizeMode(2, QHeaderView.Stretch)
#         header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
#         header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
#         header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)
#         header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)
#         header_view.setSectionResizeMode(7, QHeaderView.Fixed)
#         self.table_resultats.setColumnWidth(7, 60)
        
#         # Signaux
#         self.table_resultats.itemSelectionChanged.connect(self._on_selection_changed)
#         self.table_resultats.cellDoubleClicked.connect(self._on_row_double_clicked)
        
#         # ✅ MENU CONTEXTUEL (clic droit)
#         self.table_resultats.setContextMenuPolicy(Qt.CustomContextMenu)
#         self.table_resultats.customContextMenuRequested.connect(
#             self._show_table_context_menu
#         )
        
#         layout.addWidget(self.table_resultats)
        
#         # ─── Pagination ───
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
    
#     # ═══════════════════════════════════════════════════════════════
#     # CHARGEMENT DES DONNÉES
#     # ═══════════════════════════════════════════════════════════════
    
#     def _load_branches(self):
#         """Charge les branches pour le filtre"""
#         try:
#             branches = self.referentiel_controller.get_referentiels_by_famille("branches")
#             for b in branches:
#                 self.filter_branche.addItem(
#                     b.get('libelle', ''), b.get('code', '')
#                 )
#         except Exception as e:
#             print(f"Erreur chargement branches: {e}")
    
#     def rechercher(self):
#         """Exécute la recherche"""
#         try:
#             criteres = {}
            
#             text = self.input_recherche.text().strip()
#             if text:
#                 criteres['texte_libre'] = text
            
#             statut = self.filter_statut.currentData()
#             if statut:
#                 criteres['statut'] = statut
            
#             branche = self.filter_branche.currentData()
#             if branche:
#                 criteres['branche'] = branche
            
#             # Période
#             periode = self.filter_periode.currentText()
#             if periode != "Toutes les périodes":
#                 date_min = self._compute_date_from_periode(periode)
#                 if date_min:
#                     criteres['date_min'] = date_min
            
#             # Appel contrôleur
#             try:
#                 sinistres = self.sinistre_controller.rechercher_sinistres(criteres)
#             except TypeError:
#                 # Fallback si le contrôleur n'accepte pas tous les critères
#                 sinistres = self.sinistre_controller.rechercher_sinistres(
#                     {'numero_sinistre': text} if text else {}
#                 )
            
#             self._all_resultats = sinistres or []
#             self._current_page = 1
#             self._process_results()
            
#         except Exception as e:
#             QMessageBox.critical(
#                 self, "Erreur",
#                 f"Erreur lors de la recherche: {str(e)}"
#             )
#             import traceback
#             traceback.print_exc()
    
#     def _compute_date_from_periode(self, periode: str) -> Optional[str]:
#         """Calcule la date minimale selon la période"""
#         now = datetime.now()
#         if periode == "30 derniers jours":
#             return (now - timedelta(days=30)).strftime("%Y-%m-%d")
#         elif periode == "3 derniers mois":
#             return (now - timedelta(days=90)).strftime("%Y-%m-%d")
#         elif periode == "6 derniers mois":
#             return (now - timedelta(days=180)).strftime("%Y-%m-%d")
#         elif periode == "12 derniers mois":
#             return (now - timedelta(days=365)).strftime("%Y-%m-%d")
#         elif periode == "Année en cours":
#             return f"{now.year}-01-01"
#         return None
    
#     def _process_results(self):
#         """Traite et affiche les résultats"""
#         self._total_resultats = len(self._all_resultats)
        
#         # Mise à jour compteur
#         if self._total_resultats > 0:
#             self.lbl_count.setText(f"· {self._total_resultats} résultat(s)")
#         else:
#             self.lbl_count.setText("")
        
#         # Pagination
#         start = (self._current_page - 1) * self._per_page
#         end = start + self._per_page
#         page_data = self._all_resultats[start:end]
        
#         # Remplir le tableau
#         self.table_resultats.setRowCount(len(page_data))
#         for i, s in enumerate(page_data):
#             self._fill_row(i, s)
        
#         self._update_pagination(start, min(end, self._total_resultats))
        
#         # Reset bouton dossier
#         self.btn_dossier.setEnabled(False)
        
#         # Afficher "aucun résultat"
#         if self._total_resultats == 0:
#             self.table_resultats.setRowCount(1)
#             empty_item = QTableWidgetItem("Aucun résultat trouvé")
#             empty_item.setTextAlignment(Qt.AlignCenter)
#             empty_item.setForeground(QColor("#94a3b8"))
#             self.table_resultats.setItem(0, 0, empty_item)
#             self.table_resultats.setSpan(0, 0, 1, 8)
    
#     def _fill_row(self, row: int, s: dict):
#         """Remplit une ligne du tableau"""
#         # 0. N° Sinistre
#         num_item = QTableWidgetItem(s.get('numero_sinistre', ''))
#         num_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
#         num_item.setForeground(QColor("#2563eb"))
#         num_item.setData(Qt.UserRole, s)
#         self.table_resultats.setItem(row, 0, num_item)
        
#         # 1. Référence
#         self.table_resultats.setItem(
#             row, 1, QTableWidgetItem(s.get('numero_reference', '') or '—')
#         )
        
#         # 2. Client
#         client = (
#             s.get('client_nom')
#             or s.get('client_nom_complet')
#             or s.get('assure_nom')
#             or '—'
#         )
#         self.table_resultats.setItem(row, 2, QTableWidgetItem(client))
        
#         # 3. Branche
#         self.table_resultats.setItem(
#             row, 3, QTableWidgetItem(s.get('branche', '') or '—')
#         )
        
#         # 4. Date
#         date_surv = s.get('date_survenance', '')
#         if date_surv:
#             try:
#                 dt = datetime.fromisoformat(str(date_surv)[:19])
#                 date_str = dt.strftime("%d %b %Y")
#             except Exception:
#                 date_str = str(date_surv)[:10]
#         else:
#             date_str = '—'
#         self.table_resultats.setItem(row, 4, QTableWidgetItem(date_str))
        
#         # 5. Statut (badge)
#         statut = s.get('statut', '')
#         badge = StatusBadge(statut)
#         badge_container = QWidget()
#         badge_layout = QHBoxLayout(badge_container)
#         badge_layout.setContentsMargins(4, 6, 4, 6)
#         badge_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
#         badge_layout.addWidget(badge)
#         badge_layout.addStretch()
#         self.table_resultats.setCellWidget(row, 5, badge_container)
        
#         # 6. Montant
#         montant = s.get('montant_net', 0) or 0
#         montant_str = f"{float(montant):,.0f}".replace(",", " ")
#         montant_item = QTableWidgetItem(f"{montant_str} FCFA")
#         montant_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
#         montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
#         self.table_resultats.setItem(row, 6, montant_item)
        
#         # 7. Actions
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
#             QPushButton:pressed { background: #e2e8f0; }
#         """)
#         btn_actions.setToolTip("Actions")
#         btn_actions.clicked.connect(
#             lambda checked=False, sx=s, b=btn_actions: self._show_row_actions_menu(sx, b)
#         )
        
#         actions_container = QWidget()
#         actions_layout = QHBoxLayout(actions_container)
#         actions_layout.setContentsMargins(4, 6, 4, 6)
#         actions_layout.setAlignment(Qt.AlignCenter)
#         actions_layout.addWidget(btn_actions)
#         self.table_resultats.setCellWidget(row, 7, actions_container)
    
#     def _update_pagination(self, start: int, end: int):
#         if self._total_resultats > 0:
#             self.lbl_pagination.setText(
#                 f"{start + 1}-{end} de {self._total_resultats:,}".replace(",", " ")
#             )
#         else:
#             self.lbl_pagination.setText("0-0 de 0")
        
#         self.btn_prev.setEnabled(self._current_page > 1)
#         self.btn_next.setEnabled(end < self._total_resultats)
    
#     def _go_prev_page(self):
#         if self._current_page > 1:
#             self._current_page -= 1
#             self._process_results()
    
#     def _go_next_page(self):
#         if self._current_page * self._per_page < self._total_resultats:
#             self._current_page += 1
#             self._process_results()
    
#     # ═══════════════════════════════════════════════════════════════
#     # ✅ MENU CONTEXTUEL
#     # ═══════════════════════════════════════════════════════════════
    
#     def _menu_style(self) -> str:
#         return """
#             QMenu {
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 10px;
#                 padding: 6px;
#                 min-width: 250px;
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
#             QMenu::item:disabled {
#                 color: #94a3b8;
#             }
#             QMenu::separator {
#                 height: 1px;
#                 background: #f1f5f9;
#                 margin: 4px 8px;
#             }
#         """
    
#     def _show_table_context_menu(self, position):
#         """Menu contextuel (clic droit sur le tableau)"""
#         row = self.table_resultats.currentRow()
        
#         if row < 0 or self._total_resultats == 0:
#             # Menu vide : juste actualiser
#             menu = QMenu(self)
#             menu.setStyleSheet(self._menu_style())
#             action_refresh = menu.addAction("🔄  Actualiser")
#             action_refresh.triggered.connect(self.rechercher)
#             menu.exec(self.table_resultats.viewport().mapToGlobal(position))
#             return
        
#         item = self.table_resultats.item(row, 0)
#         if not item:
#             return
#         sinistre_data = item.data(Qt.UserRole)
#         if not sinistre_data:
#             return
        
#         self._build_sinistre_menu(
#             sinistre_data,
#             self.table_resultats.viewport().mapToGlobal(position)
#         )
    
#     def _show_row_actions_menu(self, sinistre_data: dict, button: QPushButton):
#         """Menu du bouton ⋯"""
#         self._build_sinistre_menu(
#             sinistre_data,
#             button.mapToGlobal(button.rect().bottomLeft())
#         )
    
#     def _build_sinistre_menu(self, sinistre_data: dict, global_pos):
#         """Construit le menu pour un sinistre"""
#         menu = QMenu(self)
#         menu.setStyleSheet(self._menu_style())
        
#         sinistre_id = sinistre_data.get('id')
#         numero = sinistre_data.get('numero_sinistre', 'N/A')
        
#         # Consultation
#         action_dossier = QAction("📁  Ouvrir Dossier 360°", self)
#         action_dossier.triggered.connect(
#             lambda: self.open_dossier_360(sinistre_id)
#         )
#         menu.addAction(action_dossier)
        
#         action_detail = QAction("👁️  Voir le détail", self)
#         action_detail.triggered.connect(
#             lambda: self._show_sinistre_detail(sinistre_data)
#         )
#         menu.addAction(action_detail)
        
#         menu.addSeparator()
        
#         # Actions rapides
#         action_edit = QAction("✏️  Modifier le sinistre", self)
#         action_edit.triggered.connect(
#             lambda: self._edit_sinistre(sinistre_data)
#         )
#         menu.addAction(action_edit)
        
#         action_new_mission = QAction("🔬  Nouvelle expertise", self)
#         action_new_mission.triggered.connect(
#             lambda: self._new_expertise(sinistre_data)
#         )
#         menu.addAction(action_new_mission)
        
#         action_new_eval = QAction("💰  Nouvelle évaluation", self)
#         action_new_eval.triggered.connect(
#             lambda: self._new_evaluation(sinistre_data)
#         )
#         menu.addAction(action_new_eval)
        
#         menu.addSeparator()
        
#         # Copier
#         submenu_copy = menu.addMenu("📋  Copier")
#         submenu_copy.setStyleSheet(self._menu_style())
        
#         action_copy_num = submenu_copy.addAction("Numéro de sinistre")
#         action_copy_num.triggered.connect(
#             lambda: self._copy_to_clipboard(numero)
#         )
        
#         ref = sinistre_data.get('numero_reference')
#         if ref:
#             action_copy_ref = submenu_copy.addAction("Numéro de référence")
#             action_copy_ref.triggered.connect(
#                 lambda: self._copy_to_clipboard(ref)
#             )
        
#         # Export ligne
#         action_export = QAction("⬇️  Exporter cette ligne", self)
#         action_export.triggered.connect(
#             lambda: self._export_single_sinistre(sinistre_data)
#         )
#         menu.addAction(action_export)
        
#         menu.exec(global_pos)
    
#     # ═══════════════════════════════════════════════════════════════
#     # ACTIONS MÉTIER
#     # ═══════════════════════════════════════════════════════════════
    
#     def _open_selected_dossier(self):
#         """Ouvre le dossier 360° du sinistre sélectionné"""
#         row = self.table_resultats.currentRow()
#         if row < 0:
#             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
#             return
        
#         item = self.table_resultats.item(row, 0)
#         if not item:
#             return
        
#         sinistre_data = item.data(Qt.UserRole)
#         if sinistre_data:
#             self.open_dossier_360(sinistre_data.get('id'))
    
#     def open_dossier_360(self, sinistre_id: int):
#         """Ouvre la vue Dossier 360°"""
#         if not sinistre_id:
#             return
        
#         try:
#             dossier = Dossier360View(
#                 sinistre_id=sinistre_id,
#                 sinistre_controller=self.sinistre_controller,
#                 referentiel_controller=self.referentiel_controller,
#                 expertise_controller=self.expertise_controller,
#                 evaluation_controller=self.evaluation_controller,
#                 reglement_controller=self.reglement_controller,
#                 recours_controller=self.recours_controller,
#                 user=self.user
#             )
            
#             # Essayer différents parents pour trouver le container
#             parent = self.parent()
#             container = None
#             while parent:
#                 if hasattr(parent, 'container') and parent.container is not None:
#                     container = parent.container
#                     break
#                 parent = parent.parent() if hasattr(parent, 'parent') else None
            
#             if container:
#                 container.addWidget(dossier)
#                 container.setCurrentWidget(dossier)
#             else:
#                 # Fallback : ouvrir dans une fenêtre séparée
#                 dossier.setWindowTitle(f"Dossier 360° — Sinistre {sinistre_id}")
#                 dossier.resize(1200, 800)
#                 dossier.show()
#                 self._dossier_window = dossier  # Garder une référence
        
#         except Exception as e:
#             QMessageBox.critical(
#                 self, "Erreur",
#                 f"Erreur d'ouverture du dossier: {str(e)}"
#             )
    
#     def _show_sinistre_detail(self, sinistre_data: dict):
#         """Affiche les détails d'un sinistre"""
#         QMessageBox.information(
#             self,
#             f"Sinistre {sinistre_data.get('numero_sinistre', 'N/A')}",
#             f"📋 <b>Numéro :</b> {sinistre_data.get('numero_sinistre', 'N/A')}\n"
#             f"📄 <b>Référence :</b> {sinistre_data.get('numero_reference', 'N/A')}\n"
#             f"👤 <b>Client :</b> {sinistre_data.get('client_nom', 'N/A')}\n"
#             f"🏢 <b>Branche :</b> {sinistre_data.get('branche', 'N/A')}\n"
#             f"📅 <b>Date surv. :</b> {str(sinistre_data.get('date_survenance', ''))[:10]}\n"
#             f"📌 <b>Statut :</b> {sinistre_data.get('statut', 'N/A')}\n"
#             f"💰 <b>Montant net :</b> {float(sinistre_data.get('montant_net', 0)):,.0f} FCFA"
#         )
    
#     def _edit_sinistre(self, sinistre_data: dict):
#         """Modifie un sinistre"""
#         QMessageBox.information(
#             self, "Modification",
#             f"Modification du sinistre {sinistre_data.get('numero_sinistre')} "
#             f"(à implémenter)"
#         )
    
#     def _new_expertise(self, sinistre_data: dict):
#         """Ouvre la création d'expertise pour ce sinistre"""
#         QMessageBox.information(
#             self, "Nouvelle expertise",
#             f"Créer une expertise pour le sinistre "
#             f"{sinistre_data.get('numero_sinistre')} (à implémenter)"
#         )
    
#     def _new_evaluation(self, sinistre_data: dict):
#         """Ouvre la création d'évaluation pour ce sinistre"""
#         QMessageBox.information(
#             self, "Nouvelle évaluation",
#             f"Créer une évaluation pour le sinistre "
#             f"{sinistre_data.get('numero_sinistre')} (à implémenter)"
#         )
    
#     def _copy_to_clipboard(self, text: str):
#         """Copie dans le presse-papiers"""
#         from PySide6.QtWidgets import QApplication
#         QApplication.clipboard().setText(str(text))
#         QMessageBox.information(self, "Copié", f"✅ '{text}' copié")
    
#     # ═══════════════════════════════════════════════════════════════
#     # ÉVÉNEMENTS
#     # ═══════════════════════════════════════════════════════════════
    
#     def _on_selection_changed(self):
#         """Active/désactive le bouton Dossier 360° selon la sélection"""
#         row = self.table_resultats.currentRow()
        
#         if row < 0 or self._total_resultats == 0:
#             self.btn_dossier.setEnabled(False)
#             return
        
#         item = self.table_resultats.item(row, 0)
#         if item and item.data(Qt.UserRole):
#             self.btn_dossier.setEnabled(True)
#         else:
#             self.btn_dossier.setEnabled(False)
    
#     def _on_row_double_clicked(self, row: int, col: int):
#         """Double-clic : ouvre le Dossier 360°"""
#         if col == 7:  # Colonne actions
#             return
        
#         item = self.table_resultats.item(row, 0)
#         if not item:
#             return
        
#         sinistre_data = item.data(Qt.UserRole)
#         if sinistre_data and sinistre_data.get('id'):
#             self.open_dossier_360(sinistre_data.get('id'))
    
#     def _on_search_text_changed(self, text: str):
#         """Affiche/cache le bouton clear"""
#         self.btn_clear.setVisible(bool(text.strip()))
    
#     def _on_filter_changed(self):
#         """Relance la recherche quand un filtre change"""
#         self.rechercher()
    
#     def _clear_search(self):
#         """Efface la recherche"""
#         self.input_recherche.clear()
#         self.btn_clear.setVisible(False)
#         self.rechercher()
    
#     def _reset_filters(self):
#         """Réinitialise tous les filtres"""
#         self.filter_statut.setCurrentIndex(0)
#         self.filter_branche.setCurrentIndex(0)
#         self.filter_periode.setCurrentIndex(0)
#         self.input_recherche.clear()
#         self.btn_clear.setVisible(False)
#         self.rechercher()
    
#     # ═══════════════════════════════════════════════════════════════
#     # EXPORT
#     # ═══════════════════════════════════════════════════════════════
    
#     def _export_data(self):
#         """Exporte tous les résultats en CSV"""
#         from PySide6.QtWidgets import QFileDialog
#         import csv
        
#         if not self._all_resultats:
#             QMessageBox.warning(self, "Export", "Aucun résultat à exporter")
#             return
        
#         path, _ = QFileDialog.getSaveFileName(
#             self, "Exporter les résultats",
#             f"recherche_sinistres_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
#             "CSV (*.csv)"
#         )
#         if not path:
#             return
        
#         try:
#             with open(path, 'w', newline='', encoding='utf-8') as f:
#                 writer = csv.writer(f)
#                 writer.writerow([
#                     "N° Sinistre", "Référence", "Client", "Branche",
#                     "Date survenance", "Statut", "Montant net"
#                 ])
#                 for s in self._all_resultats:
#                     writer.writerow([
#                         s.get('numero_sinistre', ''),
#                         s.get('numero_reference', '') or '',
#                         s.get('client_nom', '') or '',
#                         s.get('branche', '') or '',
#                         str(s.get('date_survenance', ''))[:10],
#                         s.get('statut', ''),
#                         s.get('montant_net', 0) or 0,
#                     ])
            
#             QMessageBox.information(
#                 self, "Export réussi",
#                 f"✅ {len(self._all_resultats)} résultats exportés"
#             )
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
#     def _export_single_sinistre(self, sinistre_data: dict):
#         """Exporte un seul sinistre"""
#         from PySide6.QtWidgets import QFileDialog
#         import csv
        
#         numero = sinistre_data.get('numero_sinistre', 'sinistre')
#         path, _ = QFileDialog.getSaveFileName(
#             self, f"Exporter {numero}",
#             f"{numero}.csv",
#             "CSV (*.csv)"
#         )
#         if not path:
#             return
        
#         try:
#             with open(path, 'w', newline='', encoding='utf-8') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(["Champ", "Valeur"])
#                 for key, value in sinistre_data.items():
#                     writer.writerow([key, value])
            
#             QMessageBox.information(self, "Export réussi", f"✅ Export vers {path}")
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
#     # ═══════════════════════════════════════════════════════════════
#     # REFRESH
#     # ═══════════════════════════════════════════════════════════════
    
#     def refresh(self):
#         """Rafraîchit la page"""
#         if self.filter_branche.count() <= 1:
#             self._load_branches()
#         self.rechercher()
    
#     # Compat : anciennes méthodes appelées ailleurs
#     def open_mission_detail(self, mission_numero: str):
#         """Compatibilité : ouvre le détail d'une mission"""
#         QMessageBox.information(
#             self, "Détail",
#             f"Détail de la mission {mission_numero}"
#         )





"""
Vue principale du module LOMETA Sinistres
Interface utilisateur complète pour la recherche des sinistres
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
from PySide6.QtGui import QColor, QIcon, QFont, QAction

import qtawesome as qta

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

class StatusBadge(QLabel):
    """Badge arrondi pour le statut d'un sinistre avec icône FontAwesome"""
    
    STATUS_STYLES = {
        'OUVERT':         ("#fef3c7", "#92400e", "Ouvert",          "fa5s.folder-open"),
        'EN_INSTRUCTION': ("#dbeafe", "#1e40af", "En instruction",  "fa5s.clipboard-list"),
        'EN_EXPERTISE':   ("#ede9fe", "#6d28d9", "En expertise",    "fa5s.microscope"),
        'EN_EVALUATION':  ("#fce7f3", "#9f1239", "En évaluation",   "fa5s.calculator"),
        'VALIDE':         ("#cffafe", "#155e75", "Validé",          "fa5s.check-circle"),
        'EN_REGLEMENT':   ("#ffedd5", "#9a3412", "En règlement",    "fa5s.credit-card"),
        'EN_RECOURS':     ("#fee2e2", "#991b1b", "En recours",      "fa5s.balance-scale"),
        'CLOTURE':        ("#d1fae5", "#065f46", "Clôturé",         "fa5s.archive"),
    }
    
    def __init__(self, statut: str, parent=None):
        super().__init__(parent)
        
        bg, fg, label, icon_name = self.STATUS_STYLES.get(
            statut, ("#e2e8f0", "#475569", statut, "fa5s.circle")
        )
        
        # ✅ Container avec icône + texte
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 11px;
                padding: 3px 10px 3px 8px;
                font-size: 11px;
                font-weight: 600;
                border: none;
            }}
        """)
        
        # Utiliser un layout interne pour icône + texte
        # (ici on triche avec HTML img en base64 pour rester simple,
        # mais on utilise directement le pixmap)
        self.setText(f"  {label}  ")
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(24)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)


# ═══════════════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════

class RecherchePage(QWidget):
    """Page de recherche des sinistres — Design moderne v2.0"""
    
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
        
        # Pagination
        self._current_page = 1
        self._per_page = 20
        self._total_resultats = 0
        self._all_resultats = []
        
        self.setup_ui()
        self._load_branches()
        self.rechercher()
    
    # ═══════════════════════════════════════════════════════════════
    # CONSTRUCTION DE L'INTERFACE
    # ═══════════════════════════════════════════════════════════════
    
    def setup_ui(self):
        self.setStyleSheet("background: #f1f5f9;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        layout.addWidget(self._build_header())
        layout.addWidget(self._build_search_bar())
        layout.addWidget(self._build_filters_bar())
        layout.addWidget(self._build_table_card(), 1)
    
    def _build_header(self):
        """En-tête de la page avec icône FontAwesome"""
        frame = QFrame()
        frame.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # ✅ Icône FontAwesome pour la recherche
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
        icon_lbl.setPixmap(qta.icon('fa5s.search', color='#2563eb').pixmap(QSize(24, 24)))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_lbl)
        
        layout.addWidget(icon_container)
        
        # Titre + sous-titre
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title = QLabel("Recherche de Sinistres")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
            background: transparent;
        """)
        title_block.addWidget(title)
        
        # Sous-titre + compteur
        subtitle_row = QHBoxLayout()
        subtitle_row.setSpacing(8)
        
        sub = QLabel("Trouvez rapidement un sinistre par numéro, client ou référence")
        sub.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        subtitle_row.addWidget(sub)
        
        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("""
            color: #2563eb;
            font-size: 12px;
            font-weight: 700;
            background: transparent;
        """)
        subtitle_row.addWidget(self.lbl_count)
        subtitle_row.addStretch()
        
        title_block.addLayout(subtitle_row)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        # ✅ Bouton Dossier 360° avec icône folder
        self.btn_dossier = QPushButton("  Ouvrir Dossier 360°")
        self.btn_dossier.setCursor(Qt.PointingHandCursor)
        self.btn_dossier.setFixedHeight(38)
        self.btn_dossier.setIcon(qta.icon('fa5s.folder-open', color='white'))
        self.btn_dossier.setIconSize(QSize(14, 14))
        self.btn_dossier.setStyleSheet("""
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
            QPushButton:disabled {
                background: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self.btn_dossier.clicked.connect(self._open_selected_dossier)
        self.btn_dossier.setEnabled(False)
        layout.addWidget(self.btn_dossier)
        
        return frame
    
    def _build_search_bar(self):
        """Barre de recherche principale avec icône FontAwesome"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # ✅ Icône loupe FontAwesome
        icon = QLabel()
        icon.setPixmap(qta.icon('fa5s.search', color='#94a3b8').pixmap(QSize(18, 18)))
        icon.setFixedSize(20, 20)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background: transparent;")
        layout.addWidget(icon)
        
        # Input
        self.input_recherche = QLineEdit()
        self.input_recherche.setPlaceholderText(
            "Rechercher par numéro de sinistre, référence, client, contrat, immatriculation..."
        )
        self.input_recherche.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                font-size: 14px;
                color: #1e293b;
                padding: 4px 8px;
            }
            QLineEdit:focus {
                background: #f8fafc;
                border-radius: 6px;
            }
        """)
        self.input_recherche.returnPressed.connect(self.rechercher)
        self.input_recherche.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self.input_recherche, 1)
        
        # ✅ Bouton clear avec icône times
        self.btn_clear = QPushButton()
        self.btn_clear.setFixedSize(28, 28)
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.setIcon(qta.icon('fa5s.times', color='#64748b'))
        self.btn_clear.setIconSize(QSize(12, 12))
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                border: none;
                border-radius: 14px;
            }
            QPushButton:hover { background: #e2e8f0; }
        """)
        self.btn_clear.clicked.connect(self._clear_search)
        self.btn_clear.setVisible(False)
        layout.addWidget(self.btn_clear)
        
        # ✅ Bouton rechercher avec icône
        self.btn_rechercher = QPushButton("  Rechercher")
        self.btn_rechercher.setCursor(Qt.PointingHandCursor)
        self.btn_rechercher.setFixedHeight(36)
        self.btn_rechercher.setIcon(qta.icon('fa5s.search', color='white'))
        self.btn_rechercher.setIconSize(QSize(14, 14))
        self.btn_rechercher.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 700;
                text-align: left;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        self.btn_rechercher.clicked.connect(self.rechercher)
        layout.addWidget(self.btn_rechercher)
        
        return frame
    
    def _build_filters_bar(self):
        """Barre de filtres avec icônes FontAwesome"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)
        
        def make_filter(label_text: str, icon_name: str, icon_color: str):
            box = QVBoxLayout()
            box.setSpacing(4)
            
            # ✅ En-tête avec icône FontAwesome
            header = QHBoxLayout()
            header.setSpacing(6)
            
            icon_lbl = QLabel()
            icon_lbl.setPixmap(qta.icon(icon_name, color=icon_color).pixmap(QSize(11, 11)))
            icon_lbl.setFixedSize(13, 13)
            icon_lbl.setStyleSheet("background: transparent;")
            header.addWidget(icon_lbl)
            
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; background: transparent;")
            header.addWidget(lbl)
            header.addStretch()
            
            box.addLayout(header)
            return box
        
        # Filtre statut
        statut_box = make_filter("Statut", "fa5s.tags", "#f59e0b")
        self.filter_statut = QComboBox()
        self.filter_statut.addItem("Tous les statuts", "")
        for statut_code, statut_label in [
            ("OUVERT", "Ouvert"),
            ("EN_INSTRUCTION", "En instruction"),
            ("EN_EXPERTISE", "En expertise"),
            ("EN_EVALUATION", "En évaluation"),
            ("VALIDE", "Validé"),
            ("EN_REGLEMENT", "En règlement"),
            ("EN_RECOURS", "En recours"),
            ("CLOTURE", "Clôturé"),
        ]:
            self.filter_statut.addItem(statut_label, statut_code)
        self.filter_statut.setStyleSheet(self._combo_style())
        self.filter_statut.currentIndexChanged.connect(self._on_filter_changed)
        statut_box.addWidget(self.filter_statut)
        layout.addLayout(statut_box)
        
        # Filtre branche
        branche_box = make_filter("Branche", "fa5s.building", "#8b5cf6")
        self.filter_branche = QComboBox()
        self.filter_branche.addItem("Toutes les branches", "")
        self.filter_branche.setStyleSheet(self._combo_style())
        self.filter_branche.currentIndexChanged.connect(self._on_filter_changed)
        branche_box.addWidget(self.filter_branche)
        layout.addLayout(branche_box)
        
        # Filtre période
        periode_box = make_filter("Période", "fa5s.calendar-alt", "#22c55e")
        self.filter_periode = QComboBox()
        self.filter_periode.addItems([
            "Toutes les périodes", "30 derniers jours", "3 derniers mois",
            "6 derniers mois", "12 derniers mois", "Année en cours"
        ])
        self.filter_periode.setStyleSheet(self._combo_style())
        self.filter_periode.currentIndexChanged.connect(self._on_filter_changed)
        periode_box.addWidget(self.filter_periode)
        layout.addLayout(periode_box)
        
        layout.addStretch()
        
        # ✅ Bouton reset avec icône sync
        btn_reset = QPushButton("  Réinitialiser")
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setFixedHeight(34)
        btn_reset.setIcon(qta.icon('fa5s.sync-alt', color='#64748b'))
        btn_reset.setIconSize(QSize(12, 12))
        btn_reset.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
                color: #64748b;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background: #f8fafc;
                border-color: #cbd5e1;
                color: #1e293b;
            }
        """)
        btn_reset.clicked.connect(self._reset_filters)
        layout.addWidget(btn_reset)
        
        return frame
    
    def _combo_style(self) -> str:
        return """
            QComboBox {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #1e293b;
                min-width: 160px;
            }
            QComboBox:hover { border-color: #3b82f6; background: white; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #64748b;
                margin-right: 6px;
            }
        """
    
    def _build_table_card(self):
        """Carte avec le tableau des résultats"""
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
        
        # ─── Header ───
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
        
        title = QLabel("Résultats de la recherche")
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
        
        # ✅ Bouton export avec icône download
        btn_export = QPushButton("  Export CSV")
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
        self.table_resultats = QTableWidget()
        self.table_resultats.setColumnCount(8)
        self.table_resultats.setHorizontalHeaderLabels([
            "N° Sinistre", "Référence", "Client", "Branche",
            "Date", "Statut", "Montant", "Actions"
        ])
        
        self.table_resultats.setStyleSheet("""
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
        
        self.table_resultats.setAlternatingRowColors(False)
        self.table_resultats.verticalHeader().setVisible(False)
        self.table_resultats.verticalHeader().setDefaultSectionSize(52)
        self.table_resultats.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_resultats.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_resultats.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_resultats.setShowGrid(False)
        self.table_resultats.setSortingEnabled(False)
        
        # Largeurs
        header_view = self.table_resultats.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table_resultats.setColumnWidth(7, 60)
        
        # Signaux
        self.table_resultats.itemSelectionChanged.connect(self._on_selection_changed)
        self.table_resultats.cellDoubleClicked.connect(self._on_row_double_clicked)
        
        # Menu contextuel
        self.table_resultats.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_resultats.customContextMenuRequested.connect(
            self._show_table_context_menu
        )
        
        layout.addWidget(self.table_resultats)
        
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
        
        self.btn_prev = QPushButton("◀ Précédent")
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
        
        self.btn_next = QPushButton("Suivant  ▶")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setLayoutDirection(Qt.RightToLeft)
        self.btn_next.setIcon(qta.icon('fa5s.chevron-right', color='#3b82f6'))
        self.btn_next.setIconSize(QSize(10, 10))
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
    
    # ═══════════════════════════════════════════════════════════════
    # CHARGEMENT DES DONNÉES (inchangé)
    # ═══════════════════════════════════════════════════════════════
    
    def _load_branches(self):
        try:
            branches = self.referentiel_controller.get_referentiels_by_famille("branches")
            for b in branches:
                self.filter_branche.addItem(
                    b.get('libelle', ''), b.get('code', '')
                )
        except Exception as e:
            print(f"Erreur chargement branches: {e}")
    
    def rechercher(self):
        try:
            criteres = {}
            
            text = self.input_recherche.text().strip()
            if text:
                criteres['texte_libre'] = text
            
            statut = self.filter_statut.currentData()
            if statut:
                criteres['statut'] = statut
            
            branche = self.filter_branche.currentData()
            if branche:
                criteres['branche'] = branche
            
            periode = self.filter_periode.currentText()
            if periode != "Toutes les périodes":
                date_min = self._compute_date_from_periode(periode)
                if date_min:
                    criteres['date_min'] = date_min
            
            try:
                sinistres = self.sinistre_controller.rechercher_sinistres(criteres)
            except TypeError:
                sinistres = self.sinistre_controller.rechercher_sinistres(
                    {'numero_sinistre': text} if text else {}
                )
            
            self._all_resultats = sinistres or []
            self._current_page = 1
            self._process_results()
            
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur",
                f"Erreur lors de la recherche: {str(e)}"
            )
            import traceback
            traceback.print_exc()
    
    def _compute_date_from_periode(self, periode: str) -> Optional[str]:
        now = datetime.now()
        if periode == "30 derniers jours":
            return (now - timedelta(days=30)).strftime("%Y-%m-%d")
        elif periode == "3 derniers mois":
            return (now - timedelta(days=90)).strftime("%Y-%m-%d")
        elif periode == "6 derniers mois":
            return (now - timedelta(days=180)).strftime("%Y-%m-%d")
        elif periode == "12 derniers mois":
            return (now - timedelta(days=365)).strftime("%Y-%m-%d")
        elif periode == "Année en cours":
            return f"{now.year}-01-01"
        return None
    
    def _process_results(self):
        self._total_resultats = len(self._all_resultats)
        
        if self._total_resultats > 0:
            self.lbl_count.setText(f"· {self._total_resultats} résultat(s)")
        else:
            self.lbl_count.setText("")
        
        start = (self._current_page - 1) * self._per_page
        end = start + self._per_page
        page_data = self._all_resultats[start:end]
        
        self.table_resultats.setRowCount(len(page_data))
        for i, s in enumerate(page_data):
            self._fill_row(i, s)
        
        self._update_pagination(start, min(end, self._total_resultats))
        self.btn_dossier.setEnabled(False)
        
        if self._total_resultats == 0:
            self.table_resultats.setRowCount(1)
            empty_item = QTableWidgetItem("Aucun résultat trouvé")
            empty_item.setTextAlignment(Qt.AlignCenter)
            empty_item.setForeground(QColor("#94a3b8"))
            self.table_resultats.setItem(0, 0, empty_item)
            self.table_resultats.setSpan(0, 0, 1, 8)
    
    def _fill_row(self, row: int, s: dict):
        """Remplit une ligne du tableau"""
        # 0. N° Sinistre
        num_item = QTableWidgetItem(s.get('numero_sinistre', ''))
        num_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        num_item.setForeground(QColor("#2563eb"))
        num_item.setData(Qt.UserRole, s)
        self.table_resultats.setItem(row, 0, num_item)
        
        # 1. Référence
        self.table_resultats.setItem(
            row, 1, QTableWidgetItem(s.get('numero_reference', '') or '—')
        )
        
        # 2. Client
        client = (
            s.get('client_nom')
            or s.get('client_nom_complet')
            or s.get('assure_nom')
            or '—'
        )
        self.table_resultats.setItem(row, 2, QTableWidgetItem(client))
        
        # 3. Branche
        self.table_resultats.setItem(
            row, 3, QTableWidgetItem(s.get('branche', '') or '—')
        )
        
        # 4. Date
        date_surv = s.get('date_survenance', '')
        if date_surv:
            try:
                dt = datetime.fromisoformat(str(date_surv)[:19])
                date_str = dt.strftime("%d %b %Y")
            except Exception:
                date_str = str(date_surv)[:10]
        else:
            date_str = '—'
        self.table_resultats.setItem(row, 4, QTableWidgetItem(date_str))
        
        # 5. Statut (badge)
        statut = s.get('statut', '')
        badge = StatusBadge(statut)
        badge_container = QWidget()
        badge_layout = QHBoxLayout(badge_container)
        badge_layout.setContentsMargins(4, 6, 4, 6)
        badge_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        badge_layout.addWidget(badge)
        badge_layout.addStretch()
        self.table_resultats.setCellWidget(row, 5, badge_container)
        
        # 6. Montant
        montant = s.get('montant_net', 0) or 0
        montant_str = f"{float(montant):,.0f}".replace(",", " ")
        montant_item = QTableWidgetItem(f"{montant_str} FCFA")
        montant_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_resultats.setItem(row, 6, montant_item)
        
        # 7. Actions
        btn_actions = QPushButton()
        btn_actions.setCursor(Qt.PointingHandCursor)
        btn_actions.setFixedSize(32, 28)
        # ✅ Icône ellipsis (3 points)
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
            lambda checked=False, sx=s, b=btn_actions: self._show_row_actions_menu(sx, b)
        )
        
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(4, 6, 4, 6)
        actions_layout.setAlignment(Qt.AlignCenter)
        actions_layout.addWidget(btn_actions)
        self.table_resultats.setCellWidget(row, 7, actions_container)
    
    def _update_pagination(self, start: int, end: int):
        if self._total_resultats > 0:
            self.lbl_pagination.setText(
                f"{start + 1}-{end} de {self._total_resultats:,}".replace(",", " ")
            )
        else:
            self.lbl_pagination.setText("0-0 de 0")
        
        self.btn_prev.setEnabled(self._current_page > 1)
        self.btn_next.setEnabled(end < self._total_resultats)
    
    def _go_prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self._process_results()
    
    def _go_next_page(self):
        if self._current_page * self._per_page < self._total_resultats:
            self._current_page += 1
            self._process_results()
    
    # ═══════════════════════════════════════════════════════════════
    # MENU CONTEXTUEL (avec icônes FontAwesome)
    # ═══════════════════════════════════════════════════════════════
    
    def _menu_style(self) -> str:
        return """
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 6px;
                min-width: 250px;
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
    
    def _show_table_context_menu(self, position):
        row = self.table_resultats.currentRow()
        
        if row < 0 or self._total_resultats == 0:
            menu = QMenu(self)
            menu.setStyleSheet(self._menu_style())
            # ✅ Icône refresh
            action_refresh = menu.addAction(
                qta.icon('fa5s.sync-alt', color='#64748b'), "  Actualiser"
            )
            action_refresh.triggered.connect(self.rechercher)
            menu.exec(self.table_resultats.viewport().mapToGlobal(position))
            return
        
        item = self.table_resultats.item(row, 0)
        if not item:
            return
        sinistre_data = item.data(Qt.UserRole)
        if not sinistre_data:
            return
        
        self._build_sinistre_menu(
            sinistre_data,
            self.table_resultats.viewport().mapToGlobal(position)
        )
    
    def _show_row_actions_menu(self, sinistre_data: dict, button: QPushButton):
        self._build_sinistre_menu(
            sinistre_data,
            button.mapToGlobal(button.rect().bottomLeft())
        )
    
    def _build_sinistre_menu(self, sinistre_data: dict, global_pos):
        """Construit le menu avec icônes FontAwesome"""
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        sinistre_id = sinistre_data.get('id')
        numero = sinistre_data.get('numero_sinistre', 'N/A')
        
        # ✅ Dossier 360°
        action_dossier = QAction(
            qta.icon('fa5s.folder-open', color='#2563eb'),
            "  Ouvrir Dossier 360°", self
        )
        action_dossier.triggered.connect(
            lambda: self.open_dossier_360(sinistre_id)
        )
        menu.addAction(action_dossier)
        
        # ✅ Voir détail
        action_detail = QAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir le détail", self
        )
        action_detail.triggered.connect(
            lambda: self._show_sinistre_detail(sinistre_data)
        )
        menu.addAction(action_detail)
        
        menu.addSeparator()
        
        # ✅ Modifier
        action_edit = QAction(
            qta.icon('fa5s.edit', color='#f59e0b'),
            "  Modifier le sinistre", self
        )
        action_edit.triggered.connect(
            lambda: self._edit_sinistre(sinistre_data)
        )
        menu.addAction(action_edit)
        
        # ✅ Nouvelle expertise
        action_new_mission = QAction(
            qta.icon('fa5s.microscope', color='#06b6d4'),
            "  Nouvelle expertise", self
        )
        action_new_mission.triggered.connect(
            lambda: self._new_expertise(sinistre_data)
        )
        menu.addAction(action_new_mission)
        
        # ✅ Nouvelle évaluation
        action_new_eval = QAction(
            qta.icon('fa5s.calculator', color='#8b5cf6'),
            "  Nouvelle évaluation", self
        )
        action_new_eval.triggered.connect(
            lambda: self._new_evaluation(sinistre_data)
        )
        menu.addAction(action_new_eval)
        
        menu.addSeparator()
        
        # ✅ Sous-menu Copier
        submenu_copy = menu.addMenu(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier"
        )
        submenu_copy.setStyleSheet(self._menu_style())
        
        action_copy_num = submenu_copy.addAction("Numéro de sinistre")
        action_copy_num.triggered.connect(
            lambda: self._copy_to_clipboard(numero)
        )
        
        ref = sinistre_data.get('numero_reference')
        if ref:
            action_copy_ref = submenu_copy.addAction("Numéro de référence")
            action_copy_ref.triggered.connect(
                lambda: self._copy_to_clipboard(ref)
            )
        
        # ✅ Export
        action_export = QAction(
            qta.icon('fa5s.download', color='#22c55e'),
            "  Exporter cette ligne", self
        )
        action_export.triggered.connect(
            lambda: self._export_single_sinistre(sinistre_data)
        )
        menu.addAction(action_export)
        
        menu.exec(global_pos)
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS MÉTIER (inchangées)
    # ═══════════════════════════════════════════════════════════════
    
    def _open_selected_dossier(self):
        row = self.table_resultats.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        item = self.table_resultats.item(row, 0)
        if not item:
            return
        
        sinistre_data = item.data(Qt.UserRole)
        if sinistre_data:
            self.open_dossier_360(sinistre_data.get('id'))
    
    def open_dossier_360(self, sinistre_id: int):
        if not sinistre_id:
            return
        
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
            container = None
            while parent:
                if hasattr(parent, 'container') and parent.container is not None:
                    container = parent.container
                    break
                parent = parent.parent() if hasattr(parent, 'parent') else None
            
            if container:
                container.addWidget(dossier)
                container.setCurrentWidget(dossier)
            else:
                dossier.setWindowTitle(f"Dossier 360° — Sinistre {sinistre_id}")
                dossier.resize(1200, 800)
                dossier.show()
                self._dossier_window = dossier
        
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur",
                f"Erreur d'ouverture du dossier: {str(e)}"
            )
    
    def _show_sinistre_detail(self, sinistre_data: dict):
        QMessageBox.information(
            self,
            f"Sinistre {sinistre_data.get('numero_sinistre', 'N/A')}",
            f"<b>Numéro :</b> {sinistre_data.get('numero_sinistre', 'N/A')}<br>"
            f"<b>Référence :</b> {sinistre_data.get('numero_reference', 'N/A')}<br>"
            f"<b>Client :</b> {sinistre_data.get('client_nom', 'N/A')}<br>"
            f"<b>Branche :</b> {sinistre_data.get('branche', 'N/A')}<br>"
            f"<b>Date surv. :</b> {str(sinistre_data.get('date_survenance', ''))[:10]}<br>"
            f"<b>Statut :</b> {sinistre_data.get('statut', 'N/A')}<br>"
            f"<b>Montant net :</b> {float(sinistre_data.get('montant_net', 0)):,.0f} FCFA"
        )
    
    def _edit_sinistre(self, sinistre_data: dict):
        QMessageBox.information(
            self, "Modification",
            f"Modification du sinistre {sinistre_data.get('numero_sinistre')} "
            f"(à implémenter)"
        )
    
    def _new_expertise(self, sinistre_data: dict):
        QMessageBox.information(
            self, "Nouvelle expertise",
            f"Créer une expertise pour le sinistre "
            f"{sinistre_data.get('numero_sinistre')} (à implémenter)"
        )
    
    def _new_evaluation(self, sinistre_data: dict):
        QMessageBox.information(
            self, "Nouvelle évaluation",
            f"Créer une évaluation pour le sinistre "
            f"{sinistre_data.get('numero_sinistre')} (à implémenter)"
        )
    
    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(str(text))
        QMessageBox.information(self, "Copié", f"'{text}' copié")
    
    # ═══════════════════════════════════════════════════════════════
    # ÉVÉNEMENTS
    # ═══════════════════════════════════════════════════════════════
    
    def _on_selection_changed(self):
        row = self.table_resultats.currentRow()
        
        if row < 0 or self._total_resultats == 0:
            self.btn_dossier.setEnabled(False)
            return
        
        item = self.table_resultats.item(row, 0)
        if item and item.data(Qt.UserRole):
            self.btn_dossier.setEnabled(True)
        else:
            self.btn_dossier.setEnabled(False)
    
    def _on_row_double_clicked(self, row: int, col: int):
        if col == 7:
            return
        
        item = self.table_resultats.item(row, 0)
        if not item:
            return
        
        sinistre_data = item.data(Qt.UserRole)
        if sinistre_data and sinistre_data.get('id'):
            self.open_dossier_360(sinistre_data.get('id'))
    
    def _on_search_text_changed(self, text: str):
        self.btn_clear.setVisible(bool(text.strip()))
    
    def _on_filter_changed(self):
        self.rechercher()
    
    def _clear_search(self):
        self.input_recherche.clear()
        self.btn_clear.setVisible(False)
        self.rechercher()
    
    def _reset_filters(self):
        self.filter_statut.setCurrentIndex(0)
        self.filter_branche.setCurrentIndex(0)
        self.filter_periode.setCurrentIndex(0)
        self.input_recherche.clear()
        self.btn_clear.setVisible(False)
        self.rechercher()
    
    # ═══════════════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════════════
    
    def _export_data(self):
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        if not self._all_resultats:
            QMessageBox.warning(self, "Export", "Aucun résultat à exporter")
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les résultats",
            f"recherche_sinistres_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv)"
        )
        if not path:
            return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "N° Sinistre", "Référence", "Client", "Branche",
                    "Date survenance", "Statut", "Montant net"
                ])
                for s in self._all_resultats:
                    writer.writerow([
                        s.get('numero_sinistre', ''),
                        s.get('numero_reference', '') or '',
                        s.get('client_nom', '') or '',
                        s.get('branche', '') or '',
                        str(s.get('date_survenance', ''))[:10],
                        s.get('statut', ''),
                        s.get('montant_net', 0) or 0,
                    ])
            
            QMessageBox.information(
                self, "Export réussi",
                f"{len(self._all_resultats)} résultats exportés"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    def _export_single_sinistre(self, sinistre_data: dict):
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        numero = sinistre_data.get('numero_sinistre', 'sinistre')
        path, _ = QFileDialog.getSaveFileName(
            self, f"Exporter {numero}",
            f"{numero}.csv",
            "CSV (*.csv)"
        )
        if not path:
            return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Champ", "Valeur"])
                for key, value in sinistre_data.items():
                    writer.writerow([key, value])
            
            QMessageBox.information(self, "Export réussi", f"Export vers {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # REFRESH
    # ═══════════════════════════════════════════════════════════════
    
    def refresh(self):
        if self.filter_branche.count() <= 1:
            self._load_branches()
        self.rechercher()
    
    def open_mission_detail(self, mission_numero: str):
        QMessageBox.information(
            self, "Détail",
            f"Détail de la mission {mission_numero}"
        )