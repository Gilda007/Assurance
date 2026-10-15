

# # """
# # Vue principale du module LOMETA Sinistres
# # Interface utilisateur complète pour la gestion des sinistres
# # """
# # from PySide6.QtWidgets import (
# #     QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
# #     QHeaderView, QLabel, QPushButton,
# #     QListWidget, QFrame, QMessageBox,
# #     QLineEdit, QComboBox
# # )
# # from PySide6.QtCore import Qt, QSize, Signal, Slot, QDate
# # from PySide6.QtGui import QColor, QIcon, QFont

# # from datetime import datetime, timedelta
# # from typing import Optional, List, Dict, Any

# # # ============================================================
# # # PAGE 8: RÉFÉRENTIELS
# # # ============================================================

# # class ReferentielsPage(QWidget):
# #     """Page de gestion des référentiels"""
    
# #     def __init__(self, controller, user):
# #         super().__init__()
# #         self.controller = controller
# #         self.user = user
# #         self.selected_referentiel_id = None
# #         self.setup_ui()
# #         self.load_data()
    
# #     def setup_ui(self):
# #         layout = QVBoxLayout(self)
# #         layout.setContentsMargins(25, 25, 25, 25)
# #         layout.setSpacing(15)
        
# #         # En-tête
# #         header = QLabel("⚙️ Gestion des Référentiels")
# #         header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
# #         layout.addWidget(header)
        
# #         # Sélecteur de famille
# #         select_layout = QHBoxLayout()
# #         select_layout.addWidget(QLabel("Famille:"))
# #         self.famille_combo = QComboBox()
# #         self.famille_combo.currentIndexChanged.connect(self.on_famille_changed)
# #         select_layout.addWidget(self.famille_combo)
        
# #         select_layout.addStretch()
        
# #         self.btn_refresh = QPushButton("🔄")
# #         self.btn_refresh.setFixedSize(35, 35)
# #         self.btn_refresh.setStyleSheet("border-radius: 17px;")
# #         self.btn_refresh.clicked.connect(self.load_data)
# #         select_layout.addWidget(self.btn_refresh)
        
# #         layout.addLayout(select_layout)
        
# #         # Tableau des référentiels
# #         self.table_referentiels = QTableWidget()
# #         self.table_referentiels.setColumnCount(5)
# #         self.table_referentiels.setHorizontalHeaderLabels([
# #             "Code", "Libellé", "Description", "Valeur", "Actif"
# #         ])
# #         self.table_referentiels.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
# #         self.table_referentiels.setAlternatingRowColors(True)
# #         self.table_referentiels.setStyleSheet("""
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
# #         layout.addWidget(self.table_referentiels)
        
# #         # Boutons d'action
# #         btn_layout = QHBoxLayout()
        
# #         self.btn_creer = QPushButton("➕ Ajouter")
# #         self.btn_creer.setStyleSheet("""
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
# #         self.btn_creer.clicked.connect(self.ajouter_referentiel)
# #         btn_layout.addWidget(self.btn_creer)

# #         # Modifier
# #         self.btn_modifier = QPushButton("✏️ Modifier")
# #         self.btn_modifier.setStyleSheet("""
# #             QPushButton {
# #                 background-color: #f59e0b;
# #                 color: white;
# #                 padding: 8px 20px;
# #                 border-radius: 8px;
# #                 font-weight: bold;
# #             }
# #             QPushButton:hover { background-color: #d97706; }
# #         """)
# #         self.btn_modifier.clicked.connect(self.modifier_referentiel)
# #         btn_layout.addWidget(self.btn_modifier)

# #         # Désactiver (REF-003)
# #         self.btn_desactiver = QPushButton("🚫 Désactiver")
# #         self.btn_desactiver.setStyleSheet("""
# #             QPushButton {
# #                 background-color: #ef4444;
# #                 color: white;
# #                 padding: 8px 20px;
# #                 border-radius: 8px;
# #                 font-weight: bold;
# #             }
# #             QPushButton:hover { background-color: #dc2626; }
# #         """)
# #         self.btn_desactiver.clicked.connect(self.desactiver_referentiel)
# #         btn_layout.addWidget(self.btn_desactiver)
        
# #         self.btn_importer = QPushButton("📥 Importer")
# #         self.btn_importer.setStyleSheet("padding: 8px 20px; border-radius: 8px;")
# #         self.btn_importer.clicked.connect(self._importer_donnees)
# #         btn_layout.addWidget(self.btn_importer)
        
# #         btn_layout.addStretch()
# #         layout.addLayout(btn_layout)
    
# #     def load_data(self):
# #         """Charge les familles de référentiels"""
# #         try:
# #             self.famille_combo.clear()
# #             familles = [
# #                 "sinistres_types", "circonstances", "responsabilites", "dommages",
# #                 "branches", "garanties", "types_experts", "types_avocats",
# #                 "modes_paiement", "statuts_sinistre", "suites_a_donner"
# #             ]
# #             for f in familles:
# #                 self.famille_combo.addItem(f.replace("_", " ").title(), f)
            
# #             if self.famille_combo.count() > 0:
# #                 self.famille_combo.setCurrentIndex(0)
# #         except Exception as e:
# #             print(f"Erreur chargement familles: {e}")
    
# #     def on_famille_changed(self, index):
# #         """Charge les référentiels de la famille sélectionnée"""
# #         if index >= 0:
# #             famille = self.famille_combo.currentData()
# #             if famille:
# #                 self.load_referentiels(famille)
    
# #     def load_referentiels(self, famille: str):
# #         """Charge les référentiels d'une famille"""
# #         try:
# #             referentiels = self.controller.get_referentiels_by_famille(famille)
# #             self.table_referentiels.setRowCount(len(referentiels))
            
# #             for i, ref in enumerate(referentiels):
# #                 self.table_referentiels.setItem(i, 0, QTableWidgetItem(ref.get('code', '')))
# #                 self.table_referentiels.setItem(i, 1, QTableWidgetItem(ref.get('libelle', '')))
# #                 self.table_referentiels.setItem(i, 2, QTableWidgetItem(ref.get('description', '')[:50] + ('...' if len(ref.get('description', '')) > 50 else '')))
# #                 self.table_referentiels.setItem(i, 3, QTableWidgetItem(str(ref.get('valeur', '')) if ref.get('valeur') is not None else '-'))
                
# #                 actif_item = QTableWidgetItem("✅" if ref.get('est_actif') else "❌")
# #                 actif_item.setForeground(QColor("#22c55e" if ref.get('est_actif') else "#ef4444"))
# #                 self.table_referentiels.setItem(i, 4, actif_item)
                
# #         except Exception as e:
# #             QMessageBox.critical(self, "Erreur", f"Erreur chargement référentiels: {str(e)}")
    
# #     def ajouter_referentiel(self):
# #         """Ouvre le dialogue d'ajout de référentiel"""
# #         from addons.sinistres.views.referentiel_dialog import ReferentielDialog
        
# #         famille = self.famille_combo.currentData()
        
# #         dialog = ReferentielDialog(
# #             controller=self.controller,
# #             user=self.user,
# #             referentiel_data=None,
# #             famille=famille,
# #             parent=self
# #         )
        
# #         dialog.referentiel_saved.connect(self._on_referentiel_saved)
# #         dialog.exec()
    
# #     def _importer_donnees(self):
# #         """Importe les données initiales des référentiels"""
# #         reply = QMessageBox.question(
# #             self,
# #             "Confirmation",
# #             "Voulez-vous importer les données initiales des référentiels ?\n"
# #             "Cela créera les données par défaut (types de sinistres, circonstances, etc.)",
# #             QMessageBox.Yes | QMessageBox.No
# #         )
        
# #         if reply == QMessageBox.Yes:
# #             try:
# #                 result = self.controller.init_donnees_initiales()
# #                 QMessageBox.information(
# #                     self,
# #                     "Import terminé",
# #                     f"✅ {result.get('crees', 0)} référentiels créés\n"
# #                     f"📝 {result.get('mis_a_jour', 0)} mis à jour\n"
# #                     f"{'⚠️ ' + str(result.get('erreurs', [])) if result.get('erreurs') else ''}"
# #                 )
# #                 self.load_referentiels(self.famille_combo.currentData())
# #             except Exception as e:
# #                 QMessageBox.critical(self, "Erreur", str(e))

# #     def _on_referentiel_cell_clicked(self, row: int, col: int):
# #         """Gère le clic sur une ligne de référentiel"""
# #         referentiel_id = self.table_referentiels.item(row, 0).data(Qt.UserRole)
# #         if referentiel_id:
# #             self.selected_referentiel_id = referentiel_id
# #         self.table_referentiels.selectRow(row)

# #     def modifier_referentiel(self):
# #         """Ouvre le dialogue de modification"""
# #         row = self.table_referentiels.currentRow()
# #         if row < 0:
# #             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un référentiel")
# #             return
        
# #         code = self.table_referentiels.item(row, 0).text()
# #         famille = self.famille_combo.currentData()
        
# #         # Récupérer le référentiel complet
# #         referentiel = self.controller.service.get_referentiel_by_code(famille, code)
# #         if not referentiel:
# #             QMessageBox.warning(self, "Erreur", "Référentiel introuvable")
# #             return
        
# #         # Convertir en dict
# #         data = {
# #             'id': referentiel.id,
# #             'famille': referentiel.famille,
# #             'code': referentiel.code,
# #             'libelle': referentiel.libelle,
# #             'description': referentiel.description,
# #             'valeur': referentiel.valeur,
# #             'date_effet': referentiel.date_effet.isoformat() if referentiel.date_effet else None,
# #             'date_fin': referentiel.date_fin.isoformat() if referentiel.date_fin else None,
# #             'societe': referentiel.societe,
# #             'branche': referentiel.branche,
# #             'est_actif': referentiel.est_actif,
# #             'donnees_supplementaires': referentiel.donnees_supplementaires,
# #         }
        
# #         from addons.sinistres.views.referentiel_dialog import ReferentielDialog
# #         dialog = ReferentielDialog(
# #             controller=self.controller,
# #             user=self.user,
# #             referentiel_data=data,
# #             parent=self
# #         )
# #         dialog.referentiel_saved.connect(self._on_referentiel_saved)
# #         dialog.exec()


# #     def desactiver_referentiel(self):
# #         """Désactive un référentiel (REF-003)"""
# #         row = self.table_referentiels.currentRow()
# #         if row < 0:
# #             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un référentiel")
# #             return
        
# #         code = self.table_referentiels.item(row, 0).text()
# #         famille = self.famille_combo.currentData()
        
# #         reply = QMessageBox.question(
# #             self,
# #             "Confirmation",
# #             f"Voulez-vous désactiver le référentiel {code} ?\n\n"
# #             f"ℹ️ Règle REF-003 : la suppression physique est interdite.\n"
# #             f"Le référentiel ne sera plus proposé dans les listes déroulantes.",
# #             QMessageBox.Yes | QMessageBox.No
# #         )
        
# #         if reply != QMessageBox.Yes:
# #             return
        
# #         referentiel = self.controller.service.get_referentiel_by_code(famille, code)
# #         if not referentiel:
# #             QMessageBox.warning(self, "Erreur", "Référentiel introuvable")
# #             return
        
# #         if self.controller.desactiver_referentiel(referentiel.id):
# #             QMessageBox.information(self, "Succès", f"Référentiel {code} désactivé")
# #             self.load_referentiels(famille)


# #     def _on_referentiel_saved(self, data: dict):
# #         """Rafraîchit après enregistrement"""
# #         self.load_referentiels(self.famille_combo.currentData())

# #     def get_selected_referentiel_id(self) -> Optional[int]:
# #         """Retourne l'ID du référentiel sélectionné"""
# #         row = self.table_referentiels.currentRow()
# #         if row >= 0:
# #             return self.table_referentiels.item(row, 0).data(Qt.UserRole)
# #         return None


# """
# Vue principale du module LOMETA Sinistres
# Interface utilisateur complète pour la gestion des référentiels
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
        
#         shadow = QGraphicsDropShadowEffect()
#         shadow.setBlurRadius(8)
#         shadow.setColor(QColor(0, 0, 0, 12))
#         shadow.setOffset(0, 2)
#         self.setGraphicsEffect(shadow)
        
#         layout = QHBoxLayout(self)
#         layout.setContentsMargins(16, 14, 16, 14)
#         layout.setSpacing(14)
        
#         # Icône
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
#             font-size: 22px;
#             font-weight: 800;
#             background: transparent;
#             border: none;
#         """)
#         value_lbl.setObjectName("stat_value")
        
#         text_layout.addWidget(title_lbl)
#         text_layout.addWidget(value_lbl)
        
#         layout.addLayout(text_layout, 1)


# class ActiveBadge(QLabel):
#     """Badge arrondi pour l'état actif/inactif"""
    
#     def __init__(self, is_active: bool, parent=None):
#         super().__init__(parent)
        
#         if is_active:
#             bg, fg, label = "#d1fae5", "#065f46", "Actif"
#         else:
#             bg, fg, label = "#fee2e2", "#991b1b", "Inactif"
        
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

# class ReferentielsPage(QWidget):
#     """Page de gestion des référentiels — Design moderne v2.0"""
    
#     def __init__(self, controller, user):
#         super().__init__()
#         self.controller = controller
#         self.user = user
#         self.selected_referentiel_id = None
        
#         # Pagination
#         self._current_page = 1
#         self._per_page = 20
#         self._total_refs = 0
#         self._all_refs = []
        
#         self.setup_ui()
#         self.load_data()
    
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
        
#         # ─── 2. CARTES STATISTIQUES ───
#         layout.addWidget(self._build_stats_row())
        
#         # ─── 3. TABLE CARD ───
#         layout.addWidget(self._build_table_card(), 1)
        
#         # ─── 4. ACTIONS SECONDAIRES ───
#         layout.addWidget(self._build_secondary_actions())
    
#     def _build_header(self):
#         """En-tête : titre + filtre famille + bouton Ajouter"""
#         frame = QFrame()
#         frame.setStyleSheet("background: transparent; border: none;")
#         layout = QHBoxLayout(frame)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(12)
        
#         # Titre
#         title = QLabel("Gestion des Référentiels")
#         title.setStyleSheet("""
#             font-size: 26px;
#             font-weight: 800;
#             color: #0f172a;
#             background: transparent;
#         """)
#         layout.addWidget(title)
        
#         # Sous-titre
#         sub = QLabel("Paramétrage et données de référence")
#         sub.setStyleSheet("color: #64748b; font-size: 12px; background: transparent; padding-top: 8px;")
#         layout.addWidget(sub, 0, Qt.AlignBottom)
        
#         layout.addStretch()
        
#         # Filtre famille
#         famille_label = QLabel("Famille :")
#         famille_label.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
#         layout.addWidget(famille_label)
        
#         self.famille_combo = QComboBox()
#         self.famille_combo.setMinimumWidth(220)
#         self.famille_combo.setStyleSheet("""
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
#         self.famille_combo.currentIndexChanged.connect(self.on_famille_changed)
#         layout.addWidget(self.famille_combo)
        
#         # Refresh
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
#         self.btn_refresh.clicked.connect(self._reload_current)
#         layout.addWidget(self.btn_refresh)
        
#         # Bouton Ajouter
#         self.btn_creer = QPushButton("  +  Ajouter")
#         self.btn_creer.setCursor(Qt.PointingHandCursor)
#         self.btn_creer.setFixedHeight(38)
#         self.btn_creer.setStyleSheet("""
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
#         self.btn_creer.clicked.connect(self.ajouter_referentiel)
#         layout.addWidget(self.btn_creer)
        
#         return frame
    
#     def _build_stats_row(self):
#         """Rangée de 4 cartes statistiques"""
#         wrapper = QWidget()
#         wrapper.setStyleSheet("background: transparent;")
#         layout = QHBoxLayout(wrapper)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(14)
        
#         self.card_total = StatCard(
#             icon="📋", title="Total dans la famille", value="0",
#             color_bg="#dbeafe", color_fg="#1e40af"
#         )
#         self.card_actifs = StatCard(
#             icon="✓", title="Actifs", value="0",
#             color_bg="#d1fae5", color_fg="#059669"
#         )
#         self.card_inactifs = StatCard(
#             icon="✕", title="Inactifs", value="0",
#             color_bg="#fee2e2", color_fg="#991b1b"
#         )
#         self.card_familles = StatCard(
#             icon="🗂", title="Familles", value="0",
#             color_bg="#ede9fe", color_fg="#6d28d9"
#         )
        
#         layout.addWidget(self.card_total)
#         layout.addWidget(self.card_actifs)
#         layout.addWidget(self.card_inactifs)
#         layout.addWidget(self.card_familles)
        
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
        
#         self.lbl_table_title = QLabel("Liste des Référentiels")
#         self.lbl_table_title.setStyleSheet("""
#             font-size: 16px;
#             font-weight: 700;
#             color: #0f172a;
#             background: transparent;
#         """)
#         header_layout.addWidget(self.lbl_table_title)
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
        
#         # Filtre actif/inactif
#         self.statut_filter = QComboBox()
#         self.statut_filter.addItems(["Tous", "Actifs", "Inactifs"])
#         self.statut_filter.setStyleSheet("""
#             QComboBox {
#                 background: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 6px 10px;
#                 font-size: 12px;
#                 color: #1e293b;
#                 min-width: 110px;
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
#         self.statut_filter.currentTextChanged.connect(self._on_filter_changed)
#         header_layout.addWidget(self.statut_filter)
        
#         # Export
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
#         self.table_referentiels = QTableWidget()
#         self.table_referentiels.setColumnCount(6)
#         self.table_referentiels.setHorizontalHeaderLabels([
#             "Code", "Libellé", "Description", "Valeur", "Statut", "Actions"
#         ])
        
#         self.table_referentiels.setStyleSheet("""
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
        
#         self.table_referentiels.setAlternatingRowColors(False)
#         self.table_referentiels.verticalHeader().setVisible(False)
#         self.table_referentiels.verticalHeader().setDefaultSectionSize(52)
#         self.table_referentiels.setSelectionBehavior(QAbstractItemView.SelectRows)
#         self.table_referentiels.setSelectionMode(QAbstractItemView.SingleSelection)
#         self.table_referentiels.setEditTriggers(QAbstractItemView.NoEditTriggers)
#         self.table_referentiels.setShowGrid(False)
        
#         # Largeurs
#         header_view = self.table_referentiels.horizontalHeader()
#         header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
#         header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
#         header_view.setSectionResizeMode(2, QHeaderView.Stretch)
#         header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
#         header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
#         header_view.setSectionResizeMode(5, QHeaderView.Fixed)
#         self.table_referentiels.setColumnWidth(5, 60)
        
#         # Signaux
#         self.table_referentiels.itemSelectionChanged.connect(self._on_selection_changed)
#         self.table_referentiels.cellDoubleClicked.connect(self._on_row_double_clicked)
        
#         # ✅ MENU CONTEXTUEL (clic droit)
#         self.table_referentiels.setContextMenuPolicy(Qt.CustomContextMenu)
#         self.table_referentiels.customContextMenuRequested.connect(
#             self._show_table_context_menu
#         )
        
#         layout.addWidget(self.table_referentiels)
        
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
    
#     def _build_secondary_actions(self):
#         """Barre d'actions secondaires"""
#         wrapper = QWidget()
#         wrapper.setStyleSheet("background: transparent;")
#         layout = QHBoxLayout(wrapper)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(10)
        
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
#             QPushButton:disabled {
#                 background: #f8fafc;
#                 color: #cbd5e1;
#                 border-color: #e2e8f0;
#             }
#         """
        
#         self.btn_modifier = QPushButton("  ✏️  Modifier")
#         self.btn_modifier.setCursor(Qt.PointingHandCursor)
#         self.btn_modifier.setStyleSheet(btn_style % ("#f59e0b", "#d97706"))
#         self.btn_modifier.clicked.connect(self.modifier_referentiel)
#         self.btn_modifier.setEnabled(False)
#         layout.addWidget(self.btn_modifier)
        
#         self.btn_desactiver = QPushButton("  🚫  Désactiver")
#         self.btn_desactiver.setCursor(Qt.PointingHandCursor)
#         self.btn_desactiver.setStyleSheet(btn_style % ("#ef4444", "#dc2626"))
#         self.btn_desactiver.clicked.connect(self.desactiver_referentiel)
#         self.btn_desactiver.setEnabled(False)
#         layout.addWidget(self.btn_desactiver)
        
#         self.btn_importer = QPushButton("  📥  Importer données initiales")
#         self.btn_importer.setCursor(Qt.PointingHandCursor)
#         self.btn_importer.setStyleSheet(btn_style % ("#8b5cf6", "#7c3aed"))
#         self.btn_importer.clicked.connect(self._importer_donnees)
#         layout.addWidget(self.btn_importer)
        
#         layout.addStretch()
        
#         return wrapper
    
#     # ═══════════════════════════════════════════════════════════════
#     # CHARGEMENT DES DONNÉES
#     # ═══════════════════════════════════════════════════════════════
    
#     def load_data(self):
#         """Charge les familles de référentiels"""
#         try:
#             self.famille_combo.blockSignals(True)
#             self.famille_combo.clear()
            
#             familles = [
#                 ("sinistres_types", "Types de sinistres"),
#                 ("circonstances", "Circonstances"),
#                 ("responsabilites", "Responsabilités"),
#                 ("dommages", "Dommages"),
#                 ("branches", "Branches"),
#                 ("garanties", "Garanties"),
#                 ("types_experts", "Types d'experts"),
#                 ("types_avocats", "Types d'avocats"),
#                 ("modes_paiement", "Modes de paiement"),
#                 ("statuts_sinistre", "Statuts sinistre"),
#                 ("suites_a_donner", "Suites à donner"),
#             ]
            
#             for code, label in familles:
#                 self.famille_combo.addItem(label, code)
            
#             self.famille_combo.blockSignals(False)
            
#             # Mettre à jour le compteur de familles
#             for lbl in self.card_familles.findChildren(QLabel):
#                 if lbl.objectName() == "stat_value":
#                     lbl.setText(str(len(familles)))
            
#             # Charger la première famille
#             if self.famille_combo.count() > 0:
#                 self.famille_combo.setCurrentIndex(0)
#                 self.on_famille_changed(0)
                
#         except Exception as e:
#             print(f"Erreur chargement familles: {e}")
    
#     def on_famille_changed(self, index):
#         """Charge les référentiels de la famille sélectionnée"""
#         if index >= 0:
#             famille = self.famille_combo.currentData()
#             if famille:
#                 self._current_page = 1
#                 self.load_referentiels(famille)
    
#     def load_referentiels(self, famille: str):
#         """Charge les référentiels d'une famille"""
#         try:
#             referentiels = self.controller.get_referentiels_by_famille(famille)
#             self._all_refs = referentiels or []
#             self._process_refs()
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur chargement référentiels: {str(e)}")
#             import traceback
#             traceback.print_exc()
    
#     def _process_refs(self):
#         """Traite et affiche les référentiels"""
#         refs = list(self._all_refs)
        
#         # Filtre recherche
#         query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""
#         if query:
#             refs = [
#                 r for r in refs
#                 if query in str(r.get('code', '')).lower()
#                 or query in str(r.get('libelle', '')).lower()
#                 or query in str(r.get('description', '') or '').lower()
#             ]
        
#         # Filtre actif/inactif
#         filter_val = self.statut_filter.currentText() if hasattr(self, 'statut_filter') else "Tous"
#         if filter_val == "Actifs":
#             refs = [r for r in refs if _safe_bool(r.get('est_actif'))]
#         elif filter_val == "Inactifs":
#             refs = [r for r in refs if not _safe_bool(r.get('est_actif'))]
        
#         self._total_refs = len(refs)
        
#         # Pagination
#         start = (self._current_page - 1) * self._per_page
#         end = start + self._per_page
#         page_data = refs[start:end]
        
#         # Mise à jour stats
#         self._update_stats(self._all_refs)
        
#         # Titre avec famille
#         famille_label = self.famille_combo.currentText()
#         self.lbl_table_title.setText(f"Liste — {famille_label}")
        
#         # Remplir le tableau
#         self.table_referentiels.setRowCount(len(page_data))
#         for i, ref in enumerate(page_data):
#             self._fill_row(i, ref)
        
#         self._update_pagination(start, min(end, self._total_refs))
        
#         # Reset boutons
#         self.btn_modifier.setEnabled(False)
#         self.btn_desactiver.setEnabled(False)
    
#     def _fill_row(self, row: int, ref: dict):
#         """Remplit une ligne du tableau"""
#         # 0. Code
#         code_item = QTableWidgetItem(ref.get('code', ''))
#         code_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
#         code_item.setForeground(QColor("#2563eb"))
#         code_item.setData(Qt.UserRole, ref)
#         self.table_referentiels.setItem(row, 0, code_item)
        
#         # 1. Libellé
#         libelle_item = QTableWidgetItem(ref.get('libelle', ''))
#         libelle_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
#         self.table_referentiels.setItem(row, 1, libelle_item)
        
#         # 2. Description (tronquée)
#         desc = ref.get('description', '') or ''
#         if len(desc) > 80:
#             desc = desc[:77] + '...'
#         self.table_referentiels.setItem(row, 2, QTableWidgetItem(desc or '—'))
        
#         # 3. Valeur
#         valeur = ref.get('valeur')
#         valeur_str = str(valeur) if valeur is not None else '—'
#         self.table_referentiels.setItem(row, 3, QTableWidgetItem(valeur_str))
        
#         # 4. Statut (badge)
#         is_active = _safe_bool(ref.get('est_actif'))
#         badge = ActiveBadge(is_active)
#         badge_container = QWidget()
#         badge_layout = QHBoxLayout(badge_container)
#         badge_layout.setContentsMargins(4, 6, 4, 6)
#         badge_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
#         badge_layout.addWidget(badge)
#         badge_layout.addStretch()
#         self.table_referentiels.setCellWidget(row, 4, badge_container)
        
#         # 5. Actions
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
#             lambda checked=False, r=ref, b=btn_actions: self._show_row_actions_menu(r, b)
#         )
        
#         actions_container = QWidget()
#         actions_layout = QHBoxLayout(actions_container)
#         actions_layout.setContentsMargins(4, 6, 4, 6)
#         actions_layout.setAlignment(Qt.AlignCenter)
#         actions_layout.addWidget(btn_actions)
#         self.table_referentiels.setCellWidget(row, 5, actions_container)
    
#     def _update_stats(self, refs: list):
#         """Met à jour les 4 cartes stats"""
#         total = len(refs)
#         actifs = sum(1 for r in refs if _safe_bool(r.get('est_actif')))
#         inactifs = total - actifs
        
#         for card, value in [
#             (self.card_total, total),
#             (self.card_actifs, actifs),
#             (self.card_inactifs, inactifs),
#         ]:
#             for lbl in card.findChildren(QLabel):
#                 if lbl.objectName() == "stat_value":
#                     lbl.setText(f"{value}")
    
#     def _update_pagination(self, start: int, end: int):
#         if self._total_refs > 0:
#             self.lbl_pagination.setText(
#                 f"{start + 1}-{end} de {self._total_refs:,}".replace(",", " ")
#             )
#         else:
#             self.lbl_pagination.setText("0-0 de 0")
        
#         self.btn_prev.setEnabled(self._current_page > 1)
#         self.btn_next.setEnabled(end < self._total_refs)
    
#     def _go_prev_page(self):
#         if self._current_page > 1:
#             self._current_page -= 1
#             self._reload_current()
    
#     def _go_next_page(self):
#         if self._current_page * self._per_page < self._total_refs:
#             self._current_page += 1
#             self._reload_current()
    
#     def _reload_current(self):
#         """Recharge la famille courante"""
#         famille = self.famille_combo.currentData()
#         if famille:
#             self.load_referentiels(famille)
    
#     def _on_search_changed(self, text):
#         self._current_page = 1
#         self._process_refs()
    
#     def _on_filter_changed(self, text):
#         self._current_page = 1
#         self._process_refs()
    
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
#                 min-width: 240px;
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
#         """Menu contextuel (clic droit)"""
#         row = self.table_referentiels.currentRow()
#         if row < 0:
#             menu = QMenu(self)
#             menu.setStyleSheet(self._menu_style())
#             action_refresh = menu.addAction("🔄  Actualiser")
#             action_refresh.triggered.connect(self._reload_current)
#             menu.exec(self.table_referentiels.viewport().mapToGlobal(position))
#             return
        
#         item = self.table_referentiels.item(row, 0)
#         if not item:
#             return
#         ref_data = item.data(Qt.UserRole)
#         if not ref_data:
#             return
        
#         self._build_ref_menu(ref_data, self.table_referentiels.viewport().mapToGlobal(position))
    
#     def _show_row_actions_menu(self, ref_data: dict, button: QPushButton):
#         """Menu du bouton ⋯"""
#         self._build_ref_menu(ref_data, button.mapToGlobal(button.rect().bottomLeft()))
    
#     def _build_ref_menu(self, ref_data: dict, global_pos):
#         """Construit le menu pour un référentiel"""
#         menu = QMenu(self)
#         menu.setStyleSheet(self._menu_style())
        
#         code = ref_data.get('code', 'N/A')
#         is_active = _safe_bool(ref_data.get('est_actif'))
        
#         # Consultation
#         action_detail = QAction("👁️  Voir les détails", self)
#         action_detail.triggered.connect(lambda: self._show_ref_detail(ref_data))
#         menu.addAction(action_detail)
        
#         menu.addSeparator()
        
#         # Actions
#         action_edit = QAction("✏️  Modifier", self)
#         action_edit.triggered.connect(lambda: self._edit_from_menu(ref_data))
#         menu.addAction(action_edit)
        
#         if is_active:
#             action_deactivate = QAction("🚫  Désactiver", self)
#             action_deactivate.triggered.connect(
#                 lambda: self._deactivate_from_menu(ref_data)
#             )
#             menu.addAction(action_deactivate)
#         else:
#             action_activate = QAction("✓  Réactiver", self)
#             action_activate.triggered.connect(
#                 lambda: self._activate_from_menu(ref_data)
#             )
#             menu.addAction(action_activate)
        
#         menu.addSeparator()
        
#         # Copier
#         submenu = menu.addMenu("📋  Copier")
#         submenu.setStyleSheet(self._menu_style())
#         act_code = submenu.addAction("Code")
#         act_code.triggered.connect(lambda: self._copy_to_clipboard(code))
#         act_label = submenu.addAction("Libellé")
#         act_label.triggered.connect(lambda: self._copy_to_clipboard(ref_data.get('libelle', '')))
        
#         menu.exec(global_pos)
    
#     # ═══════════════════════════════════════════════════════════════
#     # ACTIONS MÉTIER
#     # ═══════════════════════════════════════════════════════════════
    
#     def _show_ref_detail(self, ref_data: dict):
#         """Affiche les détails d'un référentiel"""
#         QMessageBox.information(
#             self,
#             f"Référentiel {ref_data.get('code', 'N/A')}",
#             f"📋 <b>Code :</b> {ref_data.get('code', 'N/A')}\n"
#             f"📝 <b>Libellé :</b> {ref_data.get('libelle', 'N/A')}\n"
#             f"📄 <b>Description :</b> {ref_data.get('description', '—') or '—'}\n"
#             f"🔢 <b>Valeur :</b> {ref_data.get('valeur', '—') if ref_data.get('valeur') is not None else '—'}\n"
#             f"🗂 <b>Famille :</b> {ref_data.get('famille', 'N/A')}\n"
#             f"📌 <b>Statut :</b> {'✅ Actif' if _safe_bool(ref_data.get('est_actif')) else '❌ Inactif'}"
#         )
    
#     def _edit_from_menu(self, ref_data: dict):
#         """Modifie depuis le menu"""
#         row = self._find_row_by_code(ref_data.get('code'))
#         if row >= 0:
#             self.table_referentiels.selectRow(row)
#         self.modifier_referentiel()
    
#     def _deactivate_from_menu(self, ref_data: dict):
#         """Désactive depuis le menu"""
#         row = self._find_row_by_code(ref_data.get('code'))
#         if row >= 0:
#             self.table_referentiels.selectRow(row)
#         self.desactiver_referentiel()
    
#     def _activate_from_menu(self, ref_data: dict):
#         """Réactive depuis le menu"""
#         code = ref_data.get('code')
#         famille = self.famille_combo.currentData()
        
#         reply = QMessageBox.question(
#             self, "Confirmation",
#             f"Réactiver le référentiel {code} ?",
#             QMessageBox.Yes | QMessageBox.No
#         )
#         if reply != QMessageBox.Yes:
#             return
        
#         try:
#             # Récupérer le référentiel
#             ref = self.controller.service.get_referentiel_by_code(famille, code)
#             if not ref:
#                 QMessageBox.warning(self, "Erreur", "Référentiel introuvable")
#                 return
            
#             # Utiliser la méthode du contrôleur si elle existe
#             if hasattr(self.controller, 'activer_referentiel'):
#                 self.controller.activer_referentiel(ref.id)
#             else:
#                 # Fallback : modifier directement
#                 ref.est_actif = True
#                 self.controller.service.db.commit()
            
#             QMessageBox.information(self, "Succès", f"Référentiel {code} réactivé")
#             self._reload_current()
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", str(e))
    
#     def _find_row_by_code(self, code: str) -> int:
#         """Trouve la ligne par code"""
#         for i in range(self.table_referentiels.rowCount()):
#             item = self.table_referentiels.item(i, 0)
#             if item and item.text() == code:
#                 return i
#         return -1
    
#     def _copy_to_clipboard(self, text: str):
#         from PySide6.QtWidgets import QApplication
#         QApplication.clipboard().setText(str(text))
#         QMessageBox.information(self, "Copié", f"✅ '{text}' copié")
    
#     # ═══════════════════════════════════════════════════════════════
#     # ACTIONS PRINCIPALES (existantes, adaptées)
#     # ═══════════════════════════════════════════════════════════════
    
#     def ajouter_referentiel(self):
#         """Ouvre le dialogue d'ajout"""
#         famille = self.famille_combo.currentData()
        
#         from addons.sinistres.views.referentiel_dialog import ReferentielDialog
#         dialog = ReferentielDialog(
#             controller=self.controller,
#             user=self.user,
#             referentiel_data=None,
#             famille=famille,
#             parent=self
#         )
#         dialog.referentiel_saved.connect(self._on_referentiel_saved)
#         dialog.exec()
    
#     def modifier_referentiel(self):
#         """Ouvre le dialogue de modification"""
#         row = self.table_referentiels.currentRow()
#         if row < 0:
#             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un référentiel")
#             return
        
#         item = self.table_referentiels.item(row, 0)
#         if not item:
#             return
#         ref_data = item.data(Qt.UserRole)
#         if not ref_data:
#             return
        
#         code = ref_data.get('code')
#         famille = self.famille_combo.currentData()
        
#         # Récupérer le référentiel complet
#         ref = self.controller.service.get_referentiel_by_code(famille, code)
#         if not ref:
#             QMessageBox.warning(self, "Erreur", "Référentiel introuvable")
#             return
        
#         data = {
#             'id': ref.id,
#             'famille': ref.famille,
#             'code': ref.code,
#             'libelle': ref.libelle,
#             'description': ref.description,
#             'valeur': ref.valeur,
#             'date_effet': ref.date_effet.isoformat() if ref.date_effet else None,
#             'date_fin': ref.date_fin.isoformat() if ref.date_fin else None,
#             'societe': ref.societe,
#             'branche': ref.branche,
#             'est_actif': ref.est_actif,
#             'donnees_supplementaires': ref.donnees_supplementaires,
#         }
        
#         from addons.sinistres.views.referentiel_dialog import ReferentielDialog
#         dialog = ReferentielDialog(
#             controller=self.controller,
#             user=self.user,
#             referentiel_data=data,
#             parent=self
#         )
#         dialog.referentiel_saved.connect(self._on_referentiel_saved)
#         dialog.exec()
    
#     def desactiver_referentiel(self):
#         """Désactive un référentiel (REF-003)"""
#         row = self.table_referentiels.currentRow()
#         if row < 0:
#             QMessageBox.warning(self, "Attention", "Veuillez sélectionner un référentiel")
#             return
        
#         item = self.table_referentiels.item(row, 0)
#         if not item:
#             return
#         ref_data = item.data(Qt.UserRole)
#         if not ref_data:
#             return
        
#         code = ref_data.get('code')
#         famille = self.famille_combo.currentData()
        
#         reply = QMessageBox.question(
#             self, "Confirmation",
#             f"Désactiver le référentiel {code} ?\n\n"
#             f"ℹ️ Règle REF-003 : la suppression physique est interdite.\n"
#             f"Le référentiel ne sera plus proposé dans les listes déroulantes.",
#             QMessageBox.Yes | QMessageBox.No
#         )
        
#         if reply != QMessageBox.Yes:
#             return
        
#         ref = self.controller.service.get_referentiel_by_code(famille, code)
#         if not ref:
#             QMessageBox.warning(self, "Erreur", "Référentiel introuvable")
#             return
        
#         if self.controller.desactiver_referentiel(ref.id):
#             QMessageBox.information(self, "Succès", f"Référentiel {code} désactivé")
#             self._reload_current()
    
#     def _on_referentiel_saved(self, data: dict):
#         """Rafraîchit après enregistrement"""
#         self._reload_current()
    
#     def _importer_donnees(self):
#         """Importe les données initiales"""
#         reply = QMessageBox.question(
#             self, "Confirmation",
#             "Importer les données initiales des référentiels ?\n"
#             "Cela créera les données par défaut (types de sinistres, circonstances, etc.)",
#             QMessageBox.Yes | QMessageBox.No
#         )
        
#         if reply == QMessageBox.Yes:
#             try:
#                 result = self.controller.init_donnees_initiales()
#                 QMessageBox.information(
#                     self, "Import terminé",
#                     f"✅ {result.get('crees', 0)} référentiels créés\n"
#                     f"📝 {result.get('mis_a_jour', 0)} mis à jour\n"
#                     f"{'⚠️ ' + str(result.get('erreurs', [])) if result.get('erreurs') else ''}"
#                 )
#                 self._reload_current()
#             except Exception as e:
#                 QMessageBox.critical(self, "Erreur", str(e))
    
#     # ═══════════════════════════════════════════════════════════════
#     # ÉVÉNEMENTS
#     # ═══════════════════════════════════════════════════════════════
    
#     def _on_selection_changed(self):
#         """Active/désactive les boutons selon la sélection"""
#         row = self.table_referentiels.currentRow()
        
#         if row < 0:
#             self.btn_modifier.setEnabled(False)
#             self.btn_desactiver.setEnabled(False)
#             return
        
#         item = self.table_referentiels.item(row, 0)
#         if not item:
#             return
        
#         ref_data = item.data(Qt.UserRole)
#         if not ref_data:
#             return
        
#         self.selected_referentiel_id = ref_data.get('id')
#         is_active = _safe_bool(ref_data.get('est_actif'))
        
#         self.btn_modifier.setEnabled(True)
#         self.btn_desactiver.setEnabled(is_active)
    
#     def _on_row_double_clicked(self, row: int, col: int):
#         """Double-clic : modifier"""
#         if col == 5:
#             return
#         self.modifier_referentiel()
    
#     def get_selected_referentiel_id(self) -> Optional[int]:
#         """Retourne l'ID du référentiel sélectionné"""
#         row = self.table_referentiels.currentRow()
#         if row < 0:
#             return None
#         item = self.table_referentiels.item(row, 0)
#         if not item:
#             return None
#         ref_data = item.data(Qt.UserRole)
#         return ref_data.get('id') if ref_data else None
    
#     # ═══════════════════════════════════════════════════════════════
#     # EXPORT
#     # ═══════════════════════════════════════════════════════════════
    
#     def _export_data(self):
#         """Exporte en CSV"""
#         from PySide6.QtWidgets import QFileDialog
#         import csv
        
#         if not self._all_refs:
#             QMessageBox.warning(self, "Export", "Aucune donnée à exporter")
#             return
        
#         famille = self.famille_combo.currentData() or "referentiels"
#         path, _ = QFileDialog.getSaveFileName(
#             self, "Exporter les référentiels",
#             f"{famille}_{datetime.now().strftime('%Y%m%d')}.csv",
#             "CSV (*.csv)"
#         )
#         if not path:
#             return
        
#         try:
#             with open(path, 'w', newline='', encoding='utf-8') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(["Code", "Libellé", "Description", "Valeur", "Actif"])
#                 for r in self._all_refs:
#                     writer.writerow([
#                         r.get('code', ''),
#                         r.get('libelle', ''),
#                         r.get('description', '') or '',
#                         r.get('valeur', '') if r.get('valeur') is not None else '',
#                         'Oui' if _safe_bool(r.get('est_actif')) else 'Non',
#                     ])
            
#             QMessageBox.information(
#                 self, "Export réussi",
#                 f"✅ {len(self._all_refs)} référentiels exportés"
#             )
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")



"""
Vue principale du module LOMETA Sinistres
Interface utilisateur complète pour la gestion des référentiels
Design moderne avec icônes FontAwesome
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QListWidgetItem, QStackedWidget,
    QListWidget, QFrame, QMessageBox, QDialog, QGraphicsDropShadowEffect,
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QTabWidget, QSplitter, QScrollArea,
    QProgressBar, QToolBar, QMenu, QCheckBox, QRadioButton, QSizePolicy,
    QAbstractItemView, QApplication
)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QDate
from PySide6.QtGui import QColor, QIcon, QFont, QAction

import qtawesome as qta

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


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
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 12))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)
        
        # ✅ Icône FontAwesome
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
            font-size: 22px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)
        value_lbl.setObjectName("stat_value")
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(value_lbl)
        
        layout.addLayout(text_layout, 1)


class ActiveBadge(QLabel):
    """Badge arrondi pour l'état actif/inactif"""
    
    def __init__(self, is_active: bool, parent=None):
        super().__init__(parent)
        
        if is_active:
            bg, fg, label = "#d1fae5", "#065f46", "Actif"
        else:
            bg, fg, label = "#fee2e2", "#991b1b", "Inactif"
        
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

class ReferentielsPage(QWidget):
    """Page de gestion des référentiels — Design moderne v2.0"""
    
    def __init__(self, controller, user):
        super().__init__()
        self.controller = controller
        self.user = user
        self.selected_referentiel_id = None
        
        # Pagination
        self._current_page = 1
        self._per_page = 20
        self._total_refs = 0
        self._all_refs = []
        
        self.setup_ui()
        self.load_data()
    
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
        layout.addWidget(self._build_table_card(), 1)
        layout.addWidget(self._build_secondary_actions())
    
    def _build_header(self):
        """En-tête : titre + filtre famille + bouton Ajouter"""
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
        icon_lbl.setPixmap(qta.icon('fa5s.book', color='#2563eb').pixmap(QSize(24, 24)))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_lbl)
        
        layout.addWidget(icon_container)
        
        # Titre + sous-titre
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title = QLabel("Gestion des Référentiels")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
            background: transparent;
        """)
        title_block.addWidget(title)
        
        sub = QLabel("Paramétrage et données de référence")
        sub.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        title_block.addWidget(sub)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        # Filtre famille
        famille_label = QLabel("Famille :")
        famille_label.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        layout.addWidget(famille_label)
        
        self.famille_combo = QComboBox()
        self.famille_combo.setMinimumWidth(220)
        self.famille_combo.setStyleSheet("""
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
        self.famille_combo.currentIndexChanged.connect(self.on_famille_changed)
        layout.addWidget(self.famille_combo)
        
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
        self.btn_refresh.clicked.connect(self._reload_current)
        layout.addWidget(self.btn_refresh)
        
        # ✅ Bouton Ajouter avec icône plus
        self.btn_creer = QPushButton("  Ajouter")
        self.btn_creer.setCursor(Qt.PointingHandCursor)
        self.btn_creer.setFixedHeight(38)
        self.btn_creer.setIcon(qta.icon('fa5s.plus-circle', color='white'))
        self.btn_creer.setIconSize(QSize(14, 14))
        self.btn_creer.setStyleSheet("""
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
        self.btn_creer.clicked.connect(self.ajouter_referentiel)
        layout.addWidget(self.btn_creer)
        
        return frame
    
    def _build_stats_row(self):
        """Rangée de 4 cartes statistiques avec icônes FontAwesome"""
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        
        # ✅ Icônes FontAwesome pour les stats
        self.card_total = StatCard(
            icon_name="fa5s.clipboard-list", 
            title="Total dans la famille", value="0",
            color_bg="#dbeafe", color_fg="#1e40af"
        )
        self.card_actifs = StatCard(
            icon_name="fa5s.check-circle", 
            title="Actifs", value="0",
            color_bg="#d1fae5", color_fg="#059669"
        )
        self.card_inactifs = StatCard(
            icon_name="fa5s.times-circle", 
            title="Inactifs", value="0",
            color_bg="#fee2e2", color_fg="#991b1b"
        )
        self.card_familles = StatCard(
            icon_name="fa5s.folder", 
            title="Familles", value="0",
            color_bg="#ede9fe", color_fg="#6d28d9"
        )
        
        layout.addWidget(self.card_total)
        layout.addWidget(self.card_actifs)
        layout.addWidget(self.card_inactifs)
        layout.addWidget(self.card_familles)
        
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
        
        self.lbl_table_title = QLabel("Liste des Référentiels")
        self.lbl_table_title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #0f172a;
            background: transparent;
        """)
        title_row.addWidget(self.lbl_table_title)
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
        
        # Filtre actif/inactif
        self.statut_filter = QComboBox()
        self.statut_filter.addItems(["Tous", "Actifs", "Inactifs"])
        self.statut_filter.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #1e293b;
                min-width: 110px;
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
        self.statut_filter.currentTextChanged.connect(self._on_filter_changed)
        header_layout.addWidget(self.statut_filter)
        
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
        self.table_referentiels = QTableWidget()
        self.table_referentiels.setColumnCount(6)
        self.table_referentiels.setHorizontalHeaderLabels([
            "Code", "Libellé", "Description", "Valeur", "Statut", "Actions"
        ])
        
        self.table_referentiels.setStyleSheet("""
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
        
        self.table_referentiels.setAlternatingRowColors(False)
        self.table_referentiels.verticalHeader().setVisible(False)
        self.table_referentiels.verticalHeader().setDefaultSectionSize(52)
        self.table_referentiels.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_referentiels.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_referentiels.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_referentiels.setShowGrid(False)
        
        # Largeurs
        header_view = self.table_referentiels.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table_referentiels.setColumnWidth(5, 60)
        
        # Signaux
        self.table_referentiels.itemSelectionChanged.connect(self._on_selection_changed)
        self.table_referentiels.cellDoubleClicked.connect(self._on_row_double_clicked)
        
        # Menu contextuel
        self.table_referentiels.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_referentiels.customContextMenuRequested.connect(
            self._show_table_context_menu
        )
        
        layout.addWidget(self.table_referentiels)
        
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
        
        # ✅ Bouton prev avec icône chevron-left
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
        
        # ✅ Bouton next avec icône chevron-right
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
            QPushButton:disabled {
                background: #f8fafc;
                color: #cbd5e1;
                border-color: #e2e8f0;
            }
        """
        
        # ✅ Bouton Modifier avec icône edit
        self.btn_modifier = QPushButton("  Modifier")
        self.btn_modifier.setCursor(Qt.PointingHandCursor)
        self.btn_modifier.setIcon(qta.icon('fa5s.edit', color='#d97706'))
        self.btn_modifier.setIconSize(QSize(14, 14))
        self.btn_modifier.setStyleSheet(btn_style % ("#f59e0b", "#d97706"))
        self.btn_modifier.clicked.connect(self.modifier_referentiel)
        self.btn_modifier.setEnabled(False)
        layout.addWidget(self.btn_modifier)
        
        # ✅ Bouton Désactiver avec icône ban
        self.btn_desactiver = QPushButton("  Désactiver")
        self.btn_desactiver.setCursor(Qt.PointingHandCursor)
        self.btn_desactiver.setIcon(qta.icon('fa5s.ban', color='#dc2626'))
        self.btn_desactiver.setIconSize(QSize(14, 14))
        self.btn_desactiver.setStyleSheet(btn_style % ("#ef4444", "#dc2626"))
        self.btn_desactiver.clicked.connect(self.desactiver_referentiel)
        self.btn_desactiver.setEnabled(False)
        layout.addWidget(self.btn_desactiver)
        
        # ✅ Bouton Importer avec icône download
        self.btn_importer = QPushButton("  Importer données initiales")
        self.btn_importer.setCursor(Qt.PointingHandCursor)
        self.btn_importer.setIcon(qta.icon('fa5s.file-import', color='#7c3aed'))
        self.btn_importer.setIconSize(QSize(14, 14))
        self.btn_importer.setStyleSheet(btn_style % ("#8b5cf6", "#7c3aed"))
        self.btn_importer.clicked.connect(self._importer_donnees)
        layout.addWidget(self.btn_importer)
        
        layout.addStretch()
        
        return wrapper
    
    # ═══════════════════════════════════════════════════════════════
    # CHARGEMENT DES DONNÉES
    # ═══════════════════════════════════════════════════════════════
    
    def load_data(self):
        """Charge les familles de référentiels"""
        try:
            self.famille_combo.blockSignals(True)
            self.famille_combo.clear()
            
            familles = [
                ("sinistres_types", "Types de sinistres"),
                ("circonstances", "Circonstances"),
                ("responsabilites", "Responsabilités"),
                ("dommages", "Dommages"),
                ("branches", "Branches"),
                ("garanties", "Garanties"),
                ("types_experts", "Types d'experts"),
                ("types_avocats", "Types d'avocats"),
                ("modes_paiement", "Modes de paiement"),
                ("statuts_sinistre", "Statuts sinistre"),
                ("suites_a_donner", "Suites à donner"),
            ]
            
            for code, label in familles:
                self.famille_combo.addItem(label, code)
            
            self.famille_combo.blockSignals(False)
            
            # Mettre à jour le compteur de familles
            for lbl in self.card_familles.findChildren(QLabel):
                if lbl.objectName() == "stat_value":
                    lbl.setText(str(len(familles)))
            
            # Charger la première famille
            if self.famille_combo.count() > 0:
                self.famille_combo.setCurrentIndex(0)
                self.on_famille_changed(0)
                
        except Exception as e:
            print(f"Erreur chargement familles: {e}")
    
    def on_famille_changed(self, index):
        """Charge les référentiels de la famille sélectionnée"""
        if index >= 0:
            famille = self.famille_combo.currentData()
            if famille:
                self._current_page = 1
                self.load_referentiels(famille)
    
    def load_referentiels(self, famille: str):
        """Charge les référentiels d'une famille"""
        try:
            referentiels = self.controller.get_referentiels_by_famille(famille)
            self._all_refs = referentiels or []
            self._process_refs()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement référentiels: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _process_refs(self):
        """Traite et affiche les référentiels"""
        refs = list(self._all_refs)
        
        query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""
        if query:
            refs = [
                r for r in refs
                if query in str(r.get('code', '')).lower()
                or query in str(r.get('libelle', '')).lower()
                or query in str(r.get('description', '') or '').lower()
            ]
        
        filter_val = self.statut_filter.currentText() if hasattr(self, 'statut_filter') else "Tous"
        if filter_val == "Actifs":
            refs = [r for r in refs if _safe_bool(r.get('est_actif'))]
        elif filter_val == "Inactifs":
            refs = [r for r in refs if not _safe_bool(r.get('est_actif'))]
        
        self._total_refs = len(refs)
        
        start = (self._current_page - 1) * self._per_page
        end = start + self._per_page
        page_data = refs[start:end]
        
        self._update_stats(self._all_refs)
        
        famille_label = self.famille_combo.currentText()
        self.lbl_table_title.setText(f"Liste — {famille_label}")
        
        self.table_referentiels.setRowCount(len(page_data))
        for i, ref in enumerate(page_data):
            self._fill_row(i, ref)
        
        self._update_pagination(start, min(end, self._total_refs))
        
        self.btn_modifier.setEnabled(False)
        self.btn_desactiver.setEnabled(False)
    
    def _fill_row(self, row: int, ref: dict):
        """Remplit une ligne du tableau"""
        # 0. Code
        code_item = QTableWidgetItem(ref.get('code', ''))
        code_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        code_item.setForeground(QColor("#2563eb"))
        code_item.setData(Qt.UserRole, ref)
        self.table_referentiels.setItem(row, 0, code_item)
        
        # 1. Libellé
        libelle_item = QTableWidgetItem(ref.get('libelle', ''))
        libelle_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        self.table_referentiels.setItem(row, 1, libelle_item)
        
        # 2. Description (tronquée)
        desc = ref.get('description', '') or ''
        if len(desc) > 80:
            desc = desc[:77] + '...'
        self.table_referentiels.setItem(row, 2, QTableWidgetItem(desc or '—'))
        
        # 3. Valeur
        valeur = ref.get('valeur')
        valeur_str = str(valeur) if valeur is not None else '—'
        self.table_referentiels.setItem(row, 3, QTableWidgetItem(valeur_str))
        
        # 4. Statut (badge)
        is_active = _safe_bool(ref.get('est_actif'))
        badge = ActiveBadge(is_active)
        badge_container = QWidget()
        badge_layout = QHBoxLayout(badge_container)
        badge_layout.setContentsMargins(4, 6, 4, 6)
        badge_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        badge_layout.addWidget(badge)
        badge_layout.addStretch()
        self.table_referentiels.setCellWidget(row, 4, badge_container)
        
        # 5. Actions avec icône ellipsis
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
            lambda checked=False, r=ref, b=btn_actions: self._show_row_actions_menu(r, b)
        )
        
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(4, 6, 4, 6)
        actions_layout.setAlignment(Qt.AlignCenter)
        actions_layout.addWidget(btn_actions)
        self.table_referentiels.setCellWidget(row, 5, actions_container)
    
    def _update_stats(self, refs: list):
        """Met à jour les 4 cartes stats"""
        total = len(refs)
        actifs = sum(1 for r in refs if _safe_bool(r.get('est_actif')))
        inactifs = total - actifs
        
        for card, value in [
            (self.card_total, total),
            (self.card_actifs, actifs),
            (self.card_inactifs, inactifs),
        ]:
            for lbl in card.findChildren(QLabel):
                if lbl.objectName() == "stat_value":
                    lbl.setText(f"{value}")
    
    def _update_pagination(self, start: int, end: int):
        if self._total_refs > 0:
            self.lbl_pagination.setText(
                f"{start + 1}-{end} de {self._total_refs:,}".replace(",", " ")
            )
        else:
            self.lbl_pagination.setText("0-0 de 0")
        
        self.btn_prev.setEnabled(self._current_page > 1)
        self.btn_next.setEnabled(end < self._total_refs)
    
    def _go_prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self._reload_current()
    
    def _go_next_page(self):
        if self._current_page * self._per_page < self._total_refs:
            self._current_page += 1
            self._reload_current()
    
    def _reload_current(self):
        """Recharge la famille courante"""
        famille = self.famille_combo.currentData()
        if famille:
            self.load_referentiels(famille)
    
    def _on_search_changed(self, text):
        self._current_page = 1
        self._process_refs()
    
    def _on_filter_changed(self, text):
        self._current_page = 1
        self._process_refs()
    
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
                min-width: 240px;
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
        """Menu contextuel (clic droit)"""
        row = self.table_referentiels.currentRow()
        if row < 0:
            menu = QMenu(self)
            menu.setStyleSheet(self._menu_style())
            # ✅ Icône refresh
            action_refresh = menu.addAction(
                qta.icon('fa5s.sync-alt', color='#64748b'),
                "  Actualiser"
            )
            action_refresh.triggered.connect(self._reload_current)
            menu.exec(self.table_referentiels.viewport().mapToGlobal(position))
            return
        
        item = self.table_referentiels.item(row, 0)
        if not item:
            return
        ref_data = item.data(Qt.UserRole)
        if not ref_data:
            return
        
        self._build_ref_menu(ref_data, self.table_referentiels.viewport().mapToGlobal(position))
    
    def _show_row_actions_menu(self, ref_data: dict, button: QPushButton):
        """Menu du bouton ⋯"""
        self._build_ref_menu(ref_data, button.mapToGlobal(button.rect().bottomLeft()))
    
    def _build_ref_menu(self, ref_data: dict, global_pos):
        """Construit le menu pour un référentiel"""
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        code = ref_data.get('code', 'N/A')
        is_active = _safe_bool(ref_data.get('est_actif'))
        
        # ✅ Voir détail
        action_detail = QAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir les détails", self
        )
        action_detail.triggered.connect(lambda: self._show_ref_detail(ref_data))
        menu.addAction(action_detail)
        
        menu.addSeparator()
        
        # ✅ Modifier
        action_edit = QAction(
            qta.icon('fa5s.edit', color='#f59e0b'),
            "  Modifier", self
        )
        action_edit.triggered.connect(lambda: self._edit_from_menu(ref_data))
        menu.addAction(action_edit)
        
        # ✅ Activer/Désactiver
        if is_active:
            action_deactivate = QAction(
                qta.icon('fa5s.ban', color='#ef4444'),
                "  Désactiver", self
            )
            action_deactivate.triggered.connect(
                lambda: self._deactivate_from_menu(ref_data)
            )
            menu.addAction(action_deactivate)
        else:
            action_activate = QAction(
                qta.icon('fa5s.check', color='#22c55e'),
                "  Réactiver", self
            )
            action_activate.triggered.connect(
                lambda: self._activate_from_menu(ref_data)
            )
            menu.addAction(action_activate)
        
        menu.addSeparator()
        
        # ✅ Sous-menu Copier
        submenu = menu.addMenu(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier"
        )
        submenu.setStyleSheet(self._menu_style())
        act_code = submenu.addAction("Code")
        act_code.triggered.connect(lambda: self._copy_to_clipboard(code))
        act_label = submenu.addAction("Libellé")
        act_label.triggered.connect(lambda: self._copy_to_clipboard(ref_data.get('libelle', '')))
        
        menu.exec(global_pos)
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS MÉTIER
    # ═══════════════════════════════════════════════════════════════
    
    def _show_ref_detail(self, ref_data: dict):
        """Affiche les détails d'un référentiel"""
        QMessageBox.information(
            self,
            f"Référentiel {ref_data.get('code', 'N/A')}",
            f"<b>Code :</b> {ref_data.get('code', 'N/A')}<br>"
            f"<b>Libellé :</b> {ref_data.get('libelle', 'N/A')}<br>"
            f"<b>Description :</b> {ref_data.get('description', '—') or '—'}<br>"
            f"<b>Valeur :</b> {ref_data.get('valeur', '—') if ref_data.get('valeur') is not None else '—'}<br>"
            f"<b>Famille :</b> {ref_data.get('famille', 'N/A')}<br>"
            f"<b>Statut :</b> {'✅ Actif' if _safe_bool(ref_data.get('est_actif')) else '❌ Inactif'}"
        )
    
    def _edit_from_menu(self, ref_data: dict):
        """Modifie depuis le menu"""
        row = self._find_row_by_code(ref_data.get('code'))
        if row >= 0:
            self.table_referentiels.selectRow(row)
        self.modifier_referentiel()
    
    def _deactivate_from_menu(self, ref_data: dict):
        """Désactive depuis le menu"""
        row = self._find_row_by_code(ref_data.get('code'))
        if row >= 0:
            self.table_referentiels.selectRow(row)
        self.desactiver_referentiel()
    
    def _activate_from_menu(self, ref_data: dict):
        """Réactive depuis le menu"""
        code = ref_data.get('code')
        famille = self.famille_combo.currentData()
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Réactiver le référentiel {code} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        try:
            ref = self.controller.service.get_referentiel_by_code(famille, code)
            if not ref:
                QMessageBox.warning(self, "Erreur", "Référentiel introuvable")
                return
            
            if hasattr(self.controller, 'activer_referentiel'):
                self.controller.activer_referentiel(ref.id)
            else:
                ref.est_actif = True
                self.controller.service.db.commit()
            
            QMessageBox.information(self, "Succès", f"Référentiel {code} réactivé")
            self._reload_current()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _find_row_by_code(self, code: str) -> int:
        """Trouve la ligne par code"""
        for i in range(self.table_referentiels.rowCount()):
            item = self.table_referentiels.item(i, 0)
            if item and item.text() == code:
                return i
        return -1
    
    def _copy_to_clipboard(self, text: str):
        QApplication.clipboard().setText(str(text))
        QMessageBox.information(self, "Copié", f"'{text}' copié")
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS PRINCIPALES
    # ═══════════════════════════════════════════════════════════════
    
    def ajouter_referentiel(self):
        """Ouvre le dialogue d'ajout"""
        famille = self.famille_combo.currentData()
        
        from addons.sinistres.views.referentiel_dialog import ReferentielDialog
        dialog = ReferentielDialog(
            controller=self.controller,
            user=self.user,
            referentiel_data=None,
            famille=famille,
            parent=self
        )
        dialog.referentiel_saved.connect(self._on_referentiel_saved)
        dialog.exec()
    
    def modifier_referentiel(self):
        """Ouvre le dialogue de modification"""
        row = self.table_referentiels.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un référentiel")
            return
        
        item = self.table_referentiels.item(row, 0)
        if not item:
            return
        ref_data = item.data(Qt.UserRole)
        if not ref_data:
            return
        
        code = ref_data.get('code')
        famille = self.famille_combo.currentData()
        
        ref = self.controller.service.get_referentiel_by_code(famille, code)
        if not ref:
            QMessageBox.warning(self, "Erreur", "Référentiel introuvable")
            return
        
        data = {
            'id': ref.id,
            'famille': ref.famille,
            'code': ref.code,
            'libelle': ref.libelle,
            'description': ref.description,
            'valeur': ref.valeur,
            'date_effet': ref.date_effet.isoformat() if ref.date_effet else None,
            'date_fin': ref.date_fin.isoformat() if ref.date_fin else None,
            'societe': ref.societe,
            'branche': ref.branche,
            'est_actif': ref.est_actif,
            'donnees_supplementaires': ref.donnees_supplementaires,
        }
        
        from addons.sinistres.views.referentiel_dialog import ReferentielDialog
        dialog = ReferentielDialog(
            controller=self.controller,
            user=self.user,
            referentiel_data=data,
            parent=self
        )
        dialog.referentiel_saved.connect(self._on_referentiel_saved)
        dialog.exec()
    
    def desactiver_referentiel(self):
        """Désactive un référentiel (REF-003)"""
        row = self.table_referentiels.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un référentiel")
            return
        
        item = self.table_referentiels.item(row, 0)
        if not item:
            return
        ref_data = item.data(Qt.UserRole)
        if not ref_data:
            return
        
        code = ref_data.get('code')
        famille = self.famille_combo.currentData()
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Désactiver le référentiel {code} ?\n\n"
            f"Règle REF-003 : la suppression physique est interdite.\n"
            f"Le référentiel ne sera plus proposé dans les listes déroulantes.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        ref = self.controller.service.get_referentiel_by_code(famille, code)
        if not ref:
            QMessageBox.warning(self, "Erreur", "Référentiel introuvable")
            return
        
        if self.controller.desactiver_referentiel(ref.id):
            QMessageBox.information(self, "Succès", f"Référentiel {code} désactivé")
            self._reload_current()
    
    def _on_referentiel_saved(self, data: dict):
        """Rafraîchit après enregistrement"""
        self._reload_current()
    
    def _importer_donnees(self):
        """Importe les données initiales"""
        reply = QMessageBox.question(
            self, "Confirmation",
            "Importer les données initiales des référentiels ?\n"
            "Cela créera les données par défaut (types de sinistres, circonstances, etc.)",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.init_donnees_initiales()
                QMessageBox.information(
                    self, "Import terminé",
                    f"{result.get('crees', 0)} référentiels créés\n"
                    f"{result.get('mis_a_jour', 0)} mis à jour\n"
                    f"{'⚠️ ' + str(result.get('erreurs', [])) if result.get('erreurs') else ''}"
                )
                self._reload_current()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    # ═══════════════════════════════════════════════════════════════
    # ÉVÉNEMENTS
    # ═══════════════════════════════════════════════════════════════
    
    def _on_selection_changed(self):
        """Active/désactive les boutons selon la sélection"""
        row = self.table_referentiels.currentRow()
        
        if row < 0:
            self.btn_modifier.setEnabled(False)
            self.btn_desactiver.setEnabled(False)
            return
        
        item = self.table_referentiels.item(row, 0)
        if not item:
            return
        
        ref_data = item.data(Qt.UserRole)
        if not ref_data:
            return
        
        self.selected_referentiel_id = ref_data.get('id')
        is_active = _safe_bool(ref_data.get('est_actif'))
        
        self.btn_modifier.setEnabled(True)
        self.btn_desactiver.setEnabled(is_active)
    
    def _on_row_double_clicked(self, row: int, col: int):
        """Double-clic : modifier"""
        if col == 5:
            return
        self.modifier_referentiel()
    
    def get_selected_referentiel_id(self) -> Optional[int]:
        """Retourne l'ID du référentiel sélectionné"""
        row = self.table_referentiels.currentRow()
        if row < 0:
            return None
        item = self.table_referentiels.item(row, 0)
        if not item:
            return None
        ref_data = item.data(Qt.UserRole)
        return ref_data.get('id') if ref_data else None
    
    # ═══════════════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════════════
    
    def _export_data(self):
        """Exporte en CSV"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        if not self._all_refs:
            QMessageBox.warning(self, "Export", "Aucune donnée à exporter")
            return
        
        famille = self.famille_combo.currentData() or "referentiels"
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les référentiels",
            f"{famille}_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV (*.csv)"
        )
        if not path:
            return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Code", "Libellé", "Description", "Valeur", "Actif"])
                for r in self._all_refs:
                    writer.writerow([
                        r.get('code', ''),
                        r.get('libelle', ''),
                        r.get('description', '') or '',
                        r.get('valeur', '') if r.get('valeur') is not None else '',
                        'Oui' if _safe_bool(r.get('est_actif')) else 'Non',
                    ])
            
            QMessageBox.information(
                self, "Export réussi",
                f"{len(self._all_refs)} référentiels exportés"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")