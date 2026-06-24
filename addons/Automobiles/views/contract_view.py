

# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
#     QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QComboBox,
#     QFrame, QTabWidget, QGroupBox, QFormLayout, QDateEdit,
#     QDoubleSpinBox, QTextEdit, QMessageBox, QMenu, QDialog,
#     QDialogButtonBox, QGridLayout, QScrollArea, QSplitter,
#     QToolBar, QToolButton, QStyle, QSizePolicy, QProgressBar,
#     QCheckBox, QRadioButton, QButtonGroup
# )
# from PySide6.QtCore import Qt, Signal, QDate, QDateTime, QTimer
# from PySide6.QtGui import QColor, QFont

# from datetime import datetime, timedelta
# from typing import List, Dict, Any, Optional

# from addons.Automobiles.views.style import Colors, Fonts, Spacing
# from addons.Automobiles.views.widgets.modern_card import ModernCard


# class ContractView(QWidget):
#     """Vue principale de gestion des contrats"""
    
#     contract_selected = Signal(dict)
    
#     def __init__(self, controller, user=None):
#         super().__init__()
#         self.controller = controller
#         self.user = user
#         self.contracts = []
#         self.filtered_contracts = []
        
#         # ✅ Récupérer le contrôleur des contrats
#         if hasattr(controller, 'contracts'):
#             self.contract_ctrl = controller.contracts
#         elif hasattr(controller, 'contract_controller'):
#             self.contract_ctrl = controller.contract_controller
#         else:
#             self.contract_ctrl = None
        
#         self.setup_ui()
#         self.load_data()
        
#         # Timer pour rafraîchissement auto
#         self.refresh_timer = QTimer()
#         self.refresh_timer.timeout.connect(self.load_data)
#         self.refresh_timer.start(60000)  # 60 secondes
    
#     def setup_ui(self):
#         """Configure l'interface"""
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(Spacing.LG)
        
#         # En-tête avec stats
#         self.setup_stats_header()
#         layout.addWidget(self.stats_card)
        
#         # Barre d'outils
#         self.setup_toolbar()
#         layout.addWidget(self.toolbar)
        
#         # Tableau des contrats
#         self.setup_table()
#         layout.addWidget(self.table_card)
        
#         # Onglets supplémentaires
#         self.setup_tabs()
#         layout.addWidget(self.tabs_widget)
        
#         # Barre de statut
#         self.setup_status_bar()
#         layout.addWidget(self.status_bar)
    
#     def setup_stats_header(self):
#         """Configure l'en-tête avec statistiques"""
#         self.stats_card = ModernCard(title="Aperçu des contrats", icon="📊")
        
#         stats_layout = QHBoxLayout()
#         stats_layout.setSpacing(Spacing.XL)
        
#         stats_items = [
#             ("total", "📄", "Total contrats", "0"),
#             ("active", "✅", "Actifs", "0"),
#             ("expiring", "⏰", "Échéance < 30j", "0"),
#             ("revenue", "💰", "CA mensuel", "0 XAF")
#         ]
        
#         self.stats_labels = {}
#         for key, icon, title, default in stats_items:
#             stat_widget = QFrame()
#             stat_widget.setStyleSheet(f"""
#                 QFrame {{
#                     background: {Colors.WHITE};
#                     border-radius: 12px;
#                     padding: 12px;
#                 }}
#             """)
            
#             stat_layout = QHBoxLayout(stat_widget)
#             stat_layout.setSpacing(Spacing.MD)
            
#             icon_label = QLabel(icon)
#             icon_label.setStyleSheet("font-size: 24px;")
            
#             value_widget = QWidget()
#             value_layout = QVBoxLayout(value_widget)
#             value_layout.setSpacing(Spacing.XS)
            
#             value_label = QLabel(default)
#             value_label.setStyleSheet(f"""
#                 font-size: {Fonts.H3}px;
#                 font-weight: {Fonts.BOLD};
#                 color: {Colors.PRIMARY};
#             """)
            
#             title_label = QLabel(title)
#             title_label.setStyleSheet(f"""
#                 font-size: {Fonts.SMALL}px;
#                 color: {Colors.TEXT_SECONDARY};
#             """)
            
#             value_layout.addWidget(value_label)
#             value_layout.addWidget(title_label)
            
#             stat_layout.addWidget(icon_label)
#             stat_layout.addWidget(value_widget)
#             stat_layout.addStretch()
            
#             stats_layout.addWidget(stat_widget)
#             self.stats_labels[key] = value_label
        
#         self.stats_card.add_layout(stats_layout)
    
#     def setup_toolbar(self):
#         """Configure la barre d'outils"""
#         self.toolbar = QFrame()
#         self.toolbar.setStyleSheet(f"""
#             QFrame {{
#                 background: {Colors.WHITE};
#                 border-radius: 12px;
#                 padding: 8px;
#             }}
#         """)
        
#         toolbar_layout = QHBoxLayout(self.toolbar)
#         toolbar_layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
#         toolbar_layout.setSpacing(Spacing.MD)
        
#         # Bouton nouveau contrat
#         self.new_btn = QPushButton("➕ Nouveau contrat")
#         self.new_btn.setStyleSheet(f"""
#             QPushButton {{
#                 background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
#                     stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK});
#                 color: {Colors.WHITE};
#                 border-radius: 10px;
#                 padding: 10px 20px;
#                 font-weight: {Fonts.SEMIBOLD};
#             }}
#         """)
#         self.new_btn.clicked.connect(self.on_new_contract)
        
#         # Barre de recherche
#         self.search_input = QLineEdit()
#         self.search_input.setPlaceholderText("🔍 Rechercher par police...")
#         self.search_input.setFixedWidth(250)
#         self.search_input.textChanged.connect(self.on_search)
        
#         # Filtre statut
#         self.status_filter = QComboBox()
#         self.status_filter.addItems(["Tous", "ACTIF", "PROFORMAT", "EXPIRE", "RESILIE", "ANNULE"])
#         self.status_filter.setFixedWidth(140)
#         self.status_filter.currentTextChanged.connect(self.on_filter_change)
        
#         # Bouton export
#         self.export_btn = QPushButton("📎 Exporter")
#         self.export_btn.setStyleSheet(f"""
#             QPushButton {{
#                 background: {Colors.SUCCESS};
#                 color: {Colors.WHITE};
#                 border-radius: 8px;
#                 padding: 8px 16px;
#             }}
#         """)
#         self.export_btn.clicked.connect(self.on_export)
        
#         # Bouton rafraîchir
#         self.refresh_btn = QPushButton("🔄 Rafraîchir")
#         self.refresh_btn.setStyleSheet(f"""
#             QPushButton {{
#                 background: {Colors.GRAY_100};
#                 border-radius: 8px;
#                 padding: 8px 16px;
#             }}
#         """)
#         self.refresh_btn.clicked.connect(self.load_data)
        
#         toolbar_layout.addWidget(self.new_btn)
#         toolbar_layout.addStretch()
#         toolbar_layout.addWidget(self.search_input)
#         toolbar_layout.addWidget(self.status_filter)
#         toolbar_layout.addWidget(self.export_btn)
#         toolbar_layout.addWidget(self.refresh_btn)
    
#     def setup_table(self):
#         """Configure le tableau des contrats"""
#         self.table_card = ModernCard(title="Liste des contrats", icon="📄")
        
#         self.table = QTableWidget()
#         self.table.setColumnCount(9)
#         self.table.setHorizontalHeaderLabels([
#             "Police", "Souscripteur", "Véhicule", "Début", "Fin",
#             "Prime TTC", "Statut", "Paiement", "Actions"
#         ])
        
#         # Configuration des colonnes
#         header = self.table.horizontalHeader()
#         for i in range(8):
#             header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
#         header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
#         self.table.setColumnWidth(8, 120)
        
#         self.table.setAlternatingRowColors(True)
#         self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
#         self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
#         self.table.setSortingEnabled(True)
#         self.table.doubleClicked.connect(self.on_contract_double_clicked)
        
#         self.table_card.add_widget(self.table)
    
#     def setup_tabs(self):
#         """Configure les onglets supplémentaires"""
#         self.tabs_widget = QTabWidget()
#         self.tabs_widget.setStyleSheet(f"""
#             QTabWidget::pane {{
#                 background-color: {Colors.WHITE};
#                 border: 1px solid {Colors.BORDER};
#                 border-radius: 12px;
#             }}
#             QTabBar::tab {{
#                 padding: 10px 20px;
#                 margin-right: 4px;
#             }}
#         """)
        
#         # Onglet Échéances
#         expiring_tab = self.create_expiring_tab()
#         self.tabs_widget.addTab(expiring_tab, "📅 Échéances")
        
#         # Onglet Statistiques
#         stats_tab = self.create_stats_tab()
#         self.tabs_widget.addTab(stats_tab, "📊 Statistiques")
    
#     def create_expiring_tab(self):
#         """Crée l'onglet des échéances"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
        
#         self.expiring_table = QTableWidget()
#         self.expiring_table.setColumnCount(5)
#         self.expiring_table.setHorizontalHeaderLabels(["Police", "Souscripteur", "Date fin", "Jours restants", "Action"])
#         self.expiring_table.setAlternatingRowColors(True)
        
#         layout.addWidget(self.expiring_table)
        
#         return tab
    
#     def create_stats_tab(self):
#         """Crée l'onglet des statistiques"""
#         tab = QWidget()
#         layout = QVBoxLayout(tab)
        
#         stats_text = QLabel("Statistiques détaillées des contrats")
#         stats_text.setStyleSheet(f"font-size: {Fonts.H5}px; font-weight: {Fonts.MEDIUM};")
#         layout.addWidget(stats_text)
        
#         # TODO: Ajouter des graphiques
        
#         return tab
    
#     def setup_status_bar(self):
#         """Configure la barre de statut"""
#         self.status_bar = QFrame()
#         self.status_bar.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {Colors.GRAY_50};
#                 border-radius: 10px;
#             }}
#         """)
        
#         status_layout = QHBoxLayout(self.status_bar)
#         status_layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        
#         self.status_label = QLabel("Prêt")
#         self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
#         self.status_count = QLabel("0 contrats")
#         self.status_count.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px;")
        
#         status_layout.addWidget(self.status_label)
#         status_layout.addStretch()
#         status_layout.addWidget(self.status_count)
    
#     # ============================================================
#     # CHARGEMENT DES DONNÉES
#     # ============================================================
    
#     def load_data(self):
#         """Charge les données des contrats depuis la base"""
#         if not self.contract_ctrl:
#             self.status_label.setText("Contrôleur non disponible")
#             return
        
#         try:
#             # ✅ Récupérer tous les contrats
#             contracts = self.controller.contracts.get_all_contracts(limit=100, with_relations=True)
            
#             # ✅ Convertir en dictionnaires pour la vue
#             self.contracts_summary = []
#             for contract in contracts:
#                 summary = self.contract_ctrl.get_contract_summary(contract.id)
#                 if summary:
#                     self.contracts_summary.append(summary)
            
#             self.filtered_contracts = self.contracts_summary.copy()
#             self.refresh_table()
#             self.update_stats()
#             self.update_expiring_table()
            
#             self.status_count.setText(f"{len(self.contracts_summary)} contrats")
#             self.status_label.setText("✅ Données chargées")
            
#         except Exception as e:
#             self.status_label.setText(f"❌ Erreur: {str(e)}")
#             print(f"Erreur chargement contrats: {e}")
#             import traceback
#             traceback.print_exc()
    
#     # def refresh_table(self):
#     #     """Rafraîchit le tableau"""
#     #     self.table.setRowCount(len(self.filtered_contracts))
        
#     #     for row, contract in enumerate(self.filtered_contracts):
#     #         # Numéro police
#     #         police = getattr(contract, 'numero_police', '-')
#     #         self.table.setItem(row, 0, QTableWidgetItem(police))
            
#     #         # Souscripteur
#     #         owner = getattr(contract, 'owner', None)
#     #         if owner:
#     #             owner_name = getattr(owner, 'nom', getattr(owner, 'name', f"ID:{owner.id}"))
#     #         else:
#     #             owner_name = '-'
#     #         self.table.setItem(row, 1, QTableWidgetItem(owner_name))
            
#     #         # Véhicule
#     #         vehicle = getattr(contract, 'vehicle', None)
#     #         if vehicle:
#     #             vehicle_plate = getattr(vehicle, 'immatriculation', '-')
#     #         else:
#     #             vehicle_plate = '-'
#     #         self.table.setItem(row, 2, QTableWidgetItem(vehicle_plate))
            
#     #         # Dates
#     #         start = getattr(contract, 'date_debut', None)
#     #         start_str = start.strftime("%d/%m/%Y") if start else '-'
#     #         self.table.setItem(row, 3, QTableWidgetItem(start_str))
            
#     #         end = getattr(contract, 'date_fin', None)
#     #         end_str = end.strftime("%d/%m/%Y") if end else '-'
#     #         self.table.setItem(row, 4, QTableWidgetItem(end_str))
            
#     #         # Prime
#     #         prime = getattr(contract, 'prime_totale_ttc', 0)
#     #         prime_str = f"XAF {prime:,.0f}".replace(",", " ")
#     #         self.table.setItem(row, 5, QTableWidgetItem(prime_str))
            
#     #         # Statut avec couleur
#     #         status = getattr(contract, 'statut', 'INCONNU')
#     #         if hasattr(status, 'value'):
#     #             status = status.value
#     #         status_item = QTableWidgetItem(self.get_status_label(status))
#     #         status_colors = {
#     #             'ACTIF': Colors.SUCCESS,
#     #             'PROFORMAT': Colors.WARNING,
#     #             'EXPIRE': Colors.DANGER,
#     #             'RESILIE': Colors.DANGER,
#     #             'ANNULE': Colors.TEXT_MUTED
#     #         }
#     #         status_item.setForeground(QColor(status_colors.get(status.upper(), Colors.TEXT_SECONDARY)))
#     #         self.table.setItem(row, 6, status_item)
            
#     #         # Paiement
#     #         payment = getattr(contract, 'statut_paiement', 'NON_PAYE')
#     #         payment_item = QTableWidgetItem(self.get_payment_label(payment))
#     #         payment_color = Colors.SUCCESS if payment == "PAYE" else Colors.WARNING
#     #         payment_item.setForeground(QColor(payment_color))
#     #         self.table.setItem(row, 7, payment_item)
            
#     #         # Actions
#     #         actions_widget = self.create_actions_widget(contract)
#     #         self.table.setCellWidget(row, 8, actions_widget)
    
#     def refresh_table(self):
#         """Rafraîchit le tableau avec les données résumées"""
#         self.table.setRowCount(len(self.filtered_contracts))
        
#         for row, contract in enumerate(self.filtered_contracts):
#             # Numéro police
#             police = contract.get('numero_police', '-')
#             self.table.setItem(row, 0, QTableWidgetItem(police))
            
#             # Souscripteur
#             owner_name = contract.get('owner_name', '-')
#             self.table.setItem(row, 1, QTableWidgetItem(owner_name))
            
#             # Véhicule
#             vehicle_plate = contract.get('vehicle_plate', '-')
#             self.table.setItem(row, 2, QTableWidgetItem(vehicle_plate))
            
#             # Dates
#             start_str = contract.get('date_debut', '-')
#             self.table.setItem(row, 3, QTableWidgetItem(start_str))
            
#             end_str = contract.get('date_fin', '-')
#             self.table.setItem(row, 4, QTableWidgetItem(end_str))
            
#             # Prime
#             prime = contract.get('prime_totale_ttc', 0)
#             prime_str = f"XAF {prime:,.0f}".replace(",", " ")
#             self.table.setItem(row, 5, QTableWidgetItem(prime_str))
            
#             # Statut avec couleur - ✅ CORRECTION : Convertir en string
#             status = contract.get('statut', 'INCONNU')
#             # Si status est un Enum, convertir en string
#             if hasattr(status, 'value'):
#                 status_str = status.value
#             else:
#                 status_str = str(status)
            
#             status_label = contract.get('statut_label', status_str)
#             status_item = QTableWidgetItem(str(status_label))  # ✅ Forcer la conversion en string
#             status_colors = {
#                 'ACTIF': Colors.SUCCESS,
#                 'PROFORMAT': Colors.WARNING,
#                 'EXPIRE': Colors.DANGER,
#                 'RESILIE': Colors.DANGER,
#                 'ANNULE': Colors.TEXT_MUTED
#             }
#             status_item.setForeground(QColor(status_colors.get(status_str, Colors.TEXT_SECONDARY)))
#             self.table.setItem(row, 6, status_item)
            
#             # Paiement - ✅ CORRECTION : Forcer la conversion en string
#             payment = contract.get('statut_paiement', 'NON_PAYE')
#             payment_label = contract.get('statut_paiement_label', str(payment))
#             payment_item = QTableWidgetItem(str(payment_label))  # ✅ Forcer la conversion en string
#             payment_color = Colors.SUCCESS if payment == "PAYE" else Colors.WARNING
#             payment_item.setForeground(QColor(payment_color))
#             self.table.setItem(row, 7, payment_item)
            
#             # Actions
#             actions_widget = self.create_actions_widget(contract)
#             self.table.setCellWidget(row, 8, actions_widget)

#     def get_status_label(self, status):
#         """Retourne le libellé du statut"""
#         status = status.upper() if status else 'INCONNU'
#         labels = {
#             'ACTIF': '✅ Actif',
#             'PROFORMAT': '📝 Proformat',
#             'EXPIRE': '⏰ Expiré',
#             'RESILIE': '❌ Résilié',
#             'ANNULE': '🚫 Annulé'
#         }
#         return labels.get(status, status)
    
#     def get_payment_label(self, payment):
#         """Retourne le libellé du paiement"""
#         payment = payment.upper() if payment else 'NON_PAYE'
#         labels = {
#             'PAYE': '✅ Payé',
#             'PARTIEL': '⏳ Partiel',
#             'NON_PAYE': '⏳ En attente'
#         }
#         return labels.get(payment, payment)
    
#     def create_actions_widget(self, contract):
#         """Crée les boutons d'action"""
#         widget = QWidget()
#         layout = QHBoxLayout(widget)
#         layout.setContentsMargins(Spacing.XS, Spacing.XS, Spacing.XS, Spacing.XS)
#         layout.setSpacing(Spacing.XS)
        
#         view_btn = QPushButton("👁️")
#         view_btn.setFixedSize(28, 28)
#         view_btn.setToolTip("Voir détails")
#         view_btn.clicked.connect(lambda: self.on_view_contract(contract))
        
#         edit_btn = QPushButton("✏️")
#         edit_btn.setFixedSize(28, 28)
#         edit_btn.setToolTip("Modifier")
#         edit_btn.clicked.connect(lambda: self.on_edit_contract(contract))
        
#         delete_btn = QPushButton("🗑️")
#         delete_btn.setFixedSize(28, 28)
#         delete_btn.setToolTip("Supprimer")
#         delete_btn.clicked.connect(lambda: self.on_delete_contract(contract))
        
#         layout.addWidget(view_btn)
#         layout.addWidget(edit_btn)
#         layout.addWidget(delete_btn)
        
#         return widget
    
#     def update_stats(self):
#         """Met à jour les statistiques"""
#         total = len(self.contracts_summary)
#         active = sum(1 for c in self.contracts_summary if c.get('statut') == 'ACTIF')
        
#         # Contrats expirant dans 30 jours
#         today = datetime.now().date()
#         expiring = 0
#         for c in self.contracts_summary:
#             date_fin = c.get('date_fin')
#             if date_fin and date_fin != '-':
#                 try:
#                     end_date = datetime.strptime(date_fin, "%d/%m/%Y").date()
#                     days_left = (end_date - today).days
#                     if 0 <= days_left <= 30:
#                         expiring += 1
#                 except:
#                     pass
        
#         # CA mensuel
#         total_premium = sum(c.get('prime_totale_ttc', 0) for c in self.contracts_summary)
#         monthly_revenue = total_premium / 12 if total > 0 else 0
        
#         self.stats_labels["total"].setText(str(total))
#         self.stats_labels["active"].setText(str(active))
#         self.stats_labels["expiring"].setText(str(expiring))
#         self.stats_labels["revenue"].setText(f"XAF {monthly_revenue:,.0f}".replace(",", " "))
    
#     def update_expiring_table(self):
#         """Met à jour le tableau des échéances"""
#         from datetime import datetime
        
#         today = datetime.now().date()
#         expiring_contracts = []
        
#         for contract in self.contracts_summary:
#             date_fin = contract.get('date_fin')
#             if date_fin and date_fin != '-':
#                 try:
#                     end_date = datetime.strptime(date_fin, "%d/%m/%Y").date()
#                     days_left = (end_date - today).days
#                     if 0 <= days_left <= 30:
#                         expiring_contracts.append((contract, days_left))
#                 except:
#                     pass
        
#         expiring_contracts.sort(key=lambda x: x[1])
        
#         self.expiring_table.setRowCount(len(expiring_contracts))
        
#         for row, (contract, days_left) in enumerate(expiring_contracts):
#             police = contract.get('numero_police', '-')
#             self.expiring_table.setItem(row, 0, QTableWidgetItem(str(police)))  # ✅ Conversion en string
            
#             owner_name = contract.get('owner_name', '-')
#             self.expiring_table.setItem(row, 1, QTableWidgetItem(str(owner_name)))  # ✅ Conversion en string
            
#             date_fin = contract.get('date_fin', '-')
#             self.expiring_table.setItem(row, 2, QTableWidgetItem(str(date_fin)))  # ✅ Conversion en string
            
#             days_item = QTableWidgetItem(f"{days_left} jours")
#             if days_left <= 7:
#                 days_item.setForeground(QColor(Colors.DANGER))
#             elif days_left <= 15:
#                 days_item.setForeground(QColor(Colors.WARNING))
#             self.expiring_table.setItem(row, 3, days_item)
            
#             renew_btn = QPushButton("Renouveler")
#             renew_btn.setFixedWidth(100)
#             renew_btn.setStyleSheet(f"""
#                 QPushButton {{
#                     background-color: {Colors.PRIMARY};
#                     color: white;
#                     border-radius: 6px;
#                     padding: 4px 8px;
#                 }}
#             """)
#             renew_btn.clicked.connect(lambda checked, c=contract: self.on_renew_contract(c))
#             self.expiring_table.setCellWidget(row, 4, renew_btn)


#     # ============================================================
#     # ACTIONS
#     # ============================================================
    
#     def on_new_contract(self):
#         """Crée un nouveau contrat"""
#         # TODO: Implémenter le dialogue de création
#         QMessageBox.information(self, "Nouveau contrat", "Fonction à implémenter")
    
#     def on_edit_contract(self, contract):
#         """Modifie un contrat"""
#         # TODO: Implémenter le dialogue de modification
#         QMessageBox.information(self, "Modifier", f"Contrat: {getattr(contract, 'numero_police', '-')}")
    
#     def on_view_contract(self, contract):
#         """Affiche les détails d'un contrat"""
#         police = getattr(contract, 'numero_police', '-')
#         owner = getattr(contract, 'owner', None)
#         owner_name = getattr(owner, 'nom', 'N/A') if owner else 'N/A'
#         prime = getattr(contract, 'prime_totale_ttc', 0)
#         status = getattr(contract, 'statut', 'INCONNU')
        
#         QMessageBox.information(
#             self,
#             "Détails du contrat",
#             f"📄 Contrat: {police}\n"
#             f"👤 Souscripteur: {owner_name}\n"
#             f"💰 Prime: XAF {prime:,.0f}\n"
#             f"📌 Statut: {status}\n"
#             f"📅 Début: {getattr(contract, 'date_debut', '-')}\n"
#             f"📅 Fin: {getattr(contract, 'date_fin', '-')}"
#         )
    
#     def on_delete_contract(self, contract):
#         """Supprime un contrat"""
#         reply = QMessageBox.question(
#             self,
#             "Confirmation",
#             f"Êtes-vous sûr de vouloir supprimer le contrat {getattr(contract, 'numero_police', '-')} ?",
#             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
#         )
        
#         if reply == QMessageBox.StandardButton.Yes:
#             if self.contract_ctrl:
#                 success, message = self.contract_ctrl.delete_contract(contract.id, 1)
#                 if success:
#                     QMessageBox.information(self, "Succès", "Contrat supprimé")
#                     self.load_data()
#                 else:
#                     QMessageBox.critical(self, "Erreur", message)
    
#     def on_renew_contract(self, contract):
#         """Renouvelle un contrat"""
#         reply = QMessageBox.question(
#             self,
#             "Renouvellement",
#             f"Voulez-vous renouveler le contrat {getattr(contract, 'numero_police', '-')} pour un an ?",
#             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
#         )
        
#         if reply == QMessageBox.StandardButton.Yes:
#             # TODO: Implémenter le renouvellement
#             QMessageBox.information(self, "Renouvellement", "Fonction à implémenter")
    
#     def on_search(self, text):
#         """Recherche de contrats"""
#         if not text:
#             self.filtered_contracts = self.contracts.copy()
#         else:
#             text_lower = text.lower()
#             self.filtered_contracts = [
#                 c for c in self.contracts
#                 if text_lower in getattr(c, 'numero_police', '').lower()
#             ]
#         self.refresh_table()
    
#     def on_filter_change(self):
#         """Filtre par statut"""
#         status = self.status_filter.currentText()
#         if status == "Tous":
#             self.filtered_contracts = self.contracts.copy()
#         else:
#             self.filtered_contracts = [
#                 c for c in self.contracts
#                 if getattr(c, 'statut', '').upper() == status
#             ]
#         self.refresh_table()
    
#     def on_export(self):
#         """Exporte les données"""
#         QMessageBox.information(self, "Export", "Fonction d'export à implémenter")
    
#     def on_contract_double_clicked(self, index):
#         """Double-clic sur un contrat"""
#         row = index.row()
#         if row < len(self.filtered_contracts):
#             contract = self.filtered_contracts[row]
#             self.on_view_contract(contract)
    
#     def refresh_data(self):
#         """Rafraîchit les données"""
#         self.load_data()

# addons/Automobiles/views/contract_view.py
"""
Vue de gestion des contrats d'assurance - Version complète avec ScrollArea
Design moderne, fonctionnalités avancées et interface responsive
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QComboBox,
    QFrame, QTabWidget, QGroupBox, QFormLayout, QDateEdit,
    QDoubleSpinBox, QTextEdit, QMessageBox, QMenu, QDialog,
    QDialogButtonBox, QGridLayout, QScrollArea, QSplitter,
    QToolBar, QToolButton, QStyle, QSizePolicy, QProgressBar,
    QCheckBox, QRadioButton, QButtonGroup, QStackedWidget,
    QListWidget, QListWidgetItem, QSplitterHandle
)
from PySide6.QtCore import Qt, Signal, QDate, QDateTime, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont, QAction, QIcon, QPixmap

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import csv

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.views.widgets.modern_card import ModernCard
from addons.Automobiles.views.animations import PageTransitionManager


class ContractDialog(QDialog):
    """Dialogue de création/édition de contrat - Version améliorée avec ScrollArea"""
    
    def __init__(self, controller, contract_id: int = None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.contract_id = contract_id
        self.setup_ui()
        
        if contract_id:
            self.load_contract()
            self.setWindowTitle("✏️ Modifier le contrat")
        else:
            self.setWindowTitle("➕ Nouveau contrat")
    
    def setup_ui(self):
        self.setMinimumSize(850, 750)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BACKGROUND};
                border-radius: 16px;
            }}
            QGroupBox {{
                font-weight: {Fonts.SEMIBOLD};
                border: 2px solid {Colors.BORDER};
                border-radius: 12px;
                margin-top: 14px;
                padding-top: 14px;
                background: {Colors.WHITE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 10px;
                color: {Colors.PRIMARY};
            }}
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-weight: 500;
            }}
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox {{
                border: 2px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                background: {Colors.WHITE};
                font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
                border-color: {Colors.PRIMARY};
                background: {Colors.PRIMARY_LIGHT};
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {Colors.GRAY_100};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {Colors.GRAY_400};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Colors.PRIMARY};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.LG)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        
        # En-tête
        header = self.create_header()
        layout.addWidget(header)
        
        # ScrollArea pour le formulaire
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(Spacing.LG)
        form_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        
        # Sections du formulaire
        form_layout.addWidget(self.create_general_section())
        form_layout.addWidget(self.create_dates_section())
        form_layout.addWidget(self.create_finance_section())
        form_layout.addWidget(self.create_garanties_section())
        form_layout.addWidget(self.create_notes_section())
        
        form_layout.addStretch()
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Boutons
        layout.addWidget(self.create_buttons())
    
    def create_header(self):
        """Crée l'en-tête avec progression"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK});
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        
        title = QLabel("📋 " + ("Modification" if self.contract_id else "Création") + " du contrat")
        title.setStyleSheet(f"""
            color: {Colors.WHITE};
            font-size: 18px;
            font-weight: {Fonts.BOLD};
        """)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background: rgba(255,255,255,0.2);
                border-radius: 6px;
                height: 8px;
            }}
            QProgressBar::chunk {{
                background: {Colors.WHITE};
                border-radius: 6px;
            }}
        """)
        self.progress_bar.setFixedWidth(150)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.progress_bar)
        
        return header
    
    def create_general_section(self):
        """Section des informations générales"""
        group = QGroupBox("📌 Informations générales")
        layout = QGridLayout(group)
        layout.setSpacing(Spacing.MD)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        
        # Numéro police
        layout.addWidget(self.create_labeled_widget("Numéro police:", "police_input", "Auto-généré si vide"), 0, 0, 1, 2)
        
        # Souscripteur
        layout.addWidget(self.create_labeled_widget("Souscripteur *:", "owner_combo", ""), 1, 0, 1, 2)
        self.owner_combo.setEditable(True)
        self.load_contacts()
        
        # Compagnie
        layout.addWidget(self.create_labeled_widget("Compagnie *:", "company_combo", ""), 2, 0, 1, 2)
        self.load_companies()
        
        # Véhicule
        layout.addWidget(self.create_labeled_widget("Véhicule *:", "vehicle_combo", ""), 3, 0, 1, 2)
        self.vehicle_combo.setEditable(True)
        self.load_vehicles()
        
        # Type et Statut
        layout.addWidget(self.create_labeled_widget("Type contrat:", "type_combo", ""), 4, 0)
        self.type_combo.addItems(["VEHICULE", "FLOTTE"])
        
        layout.addWidget(self.create_labeled_widget("Statut:", "status_combo", ""), 4, 1)
        self.status_combo.addItems(["PROFORMAT", "ACTIF", "RESILIE", "EXPIRE", "ANNULE"])
        
        return group
    
    def create_dates_section(self):
        """Section des dates"""
        group = QGroupBox("📅 Période d'assurance")
        layout = QGridLayout(group)
        layout.setSpacing(Spacing.MD)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        
        layout.addWidget(self.create_labeled_widget("Date début *:", "start_date", ""), 0, 0)
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.dateChanged.connect(self.on_date_changed)
        
        layout.addWidget(self.create_labeled_widget("Date fin *:", "end_date", ""), 0, 1)
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addDays(365))
        self.end_date.dateChanged.connect(self.on_date_changed)
        
        layout.addWidget(self.create_labeled_widget("Date proformat:", "proformat_date", ""), 1, 0)
        self.proformat_date.setCalendarPopup(True)
        self.proformat_date.setDate(QDate.currentDate())
        
        self.duration_label = QLabel("Durée: 365 jours")
        self.duration_label.setStyleSheet(f"font-weight: {Fonts.BOLD}; color: {Colors.PRIMARY};")
        layout.addWidget(self.duration_label, 1, 1)
        
        return group
    
    def create_finance_section(self):
        """Section financière améliorée"""
        group = QGroupBox("💰 Informations financières")
        layout = QGridLayout(group)
        layout.setSpacing(Spacing.MD)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        
        # Colonne 1: Montants
        layout.addWidget(self.create_labeled_widget("Prime pure (XAF):", "prime_pure", ""), 0, 0)
        self.prime_pure.setRange(0, 100000000)
        self.prime_pure.setPrefix("XAF ")
        self.prime_pure.valueChanged.connect(self.update_total)
        
        layout.addWidget(self.create_labeled_widget("Accessoires (XAF):", "accessoires", ""), 1, 0)
        self.accessoires.setRange(0, 10000000)
        self.accessoires.setPrefix("XAF ")
        self.accessoires.valueChanged.connect(self.update_total)
        
        layout.addWidget(self.create_labeled_widget("Taxes (XAF):", "taxes", ""), 2, 0)
        self.taxes.setRange(0, 10000000)
        self.taxes.setPrefix("XAF ")
        self.taxes.valueChanged.connect(self.update_total)
        
        # Colonne 2: Réductions
        layout.addWidget(self.create_labeled_widget("Réduction flotte (%):", "discount", ""), 0, 1)
        self.discount.setRange(0, 50)
        self.discount.setSuffix(" %")
        self.discount.valueChanged.connect(self.update_total)
        
        layout.addWidget(self.create_labeled_widget("Commission (%):", "commission", ""), 1, 1)
        self.commission = QDoubleSpinBox()
        self.commission.setRange(0, 100)
        self.commission.setSuffix(" %")
        self.commission.valueChanged.connect(self.update_total)
        
        # Total
        self.total_frame = QFrame()
        self.total_frame.setStyleSheet(f"""
            QFrame {{
                background: {Colors.PRIMARY_LIGHT};
                border-radius: 10px;
                padding: 8px;
            }}
        """)
        total_layout = QHBoxLayout(self.total_frame)
        total_label = QLabel("Total TTC:")
        total_label.setStyleSheet(f"font-weight: {Fonts.BOLD};")
        self.total_label = QLabel("XAF 0")
        self.total_label.setStyleSheet(f"""
            font-weight: {Fonts.BOLD};
            color: {Colors.PRIMARY};
            font-size: 16px;
        """)
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.total_label)
        layout.addWidget(self.total_frame, 2, 0, 1, 2)
        
        return group
    
    def create_garanties_section(self):
        """Section des garanties incluses"""
        group = QGroupBox("🛡️ Garanties incluses")
        layout = QGridLayout(group)
        layout.setSpacing(Spacing.SM)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        
        garanties = [
            ("RC", "Responsabilité Civile", True),
            ("DR", "Défense Recours", True),
            ("VOL", "Vol", False),
            ("VB", "Vol à main armée", False),
            ("INC", "Incendie", False),
            ("BG", "Bris de glace", False),
            ("AR", "Assistance", False),
            ("DTA", "Dommages Tous Accidents", False),
            ("IPT", "Individuelle Personnes Transportées", False),
        ]
        
        self.garantie_checks = {}
        for i, (code, label, default) in enumerate(garanties):
            row = i // 3
            col = i % 3
            cb = QCheckBox(f"{code} - {label}")
            cb.setChecked(default)
            layout.addWidget(cb, row, col)
            self.garantie_checks[code] = cb
        
        return group
    
    def create_notes_section(self):
        """Section des notes"""
        group = QGroupBox("📝 Notes")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setPlaceholderText("Informations complémentaires...")
        layout.addWidget(self.notes_input)
        
        return group
    
    def create_labeled_widget(self, label_text, attr_name, placeholder):
        """Crée un widget avec label"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(Spacing.XS)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: 500; color: #475569;")
        layout.addWidget(label)
        
        # Créer le widget selon le type
        if attr_name in ["police_input"]:
            widget_obj = QLineEdit()
            widget_obj.setPlaceholderText(placeholder)
        elif attr_name in ["owner_combo", "company_combo", "vehicle_combo", "type_combo", "status_combo"]:
            widget_obj = QComboBox()
            if attr_name in ["owner_combo", "vehicle_combo"]:
                widget_obj.setEditable(True)
        elif attr_name in ["start_date", "end_date", "proformat_date"]:
            widget_obj = QDateEdit()
            widget_obj.setCalendarPopup(True)
        elif attr_name in ["prime_pure", "accessoires", "taxes", "discount", "commission"]:
            widget_obj = QDoubleSpinBox()
            widget_obj.setRange(0, 100000000)
        else:
            widget_obj = QLineEdit()
        
        setattr(self, attr_name, widget_obj)
        layout.addWidget(widget_obj)
        
        return widget
    
    def create_buttons(self):
        """Crée les boutons d'action"""
        buttons = QDialogButtonBox()
        buttons.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 24px;
                border-radius: 8px;
                font-weight: {Fonts.SEMIBOLD};
            }}
            QPushButton[standard="Save"] {{
                background: {Colors.PRIMARY};
                color: {Colors.WHITE};
            }}
            QPushButton[standard="Save"]:hover {{
                background: {Colors.PRIMARY_DARK};
            }}
        """)
        
        btn_save = buttons.addButton("💾 Enregistrer", QDialogButtonBox.AcceptRole)
        btn_cancel = buttons.addButton("Annuler", QDialogButtonBox.RejectRole)
        
        btn_save.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        
        return buttons
    
    def on_date_changed(self):
        """Met à jour la durée calculée"""
        debut = self.start_date.date()
        fin = self.end_date.date()
        if fin >= debut:
            jours = debut.daysTo(fin)
            self.duration_label.setText(f"Durée: {jours} jours ({jours//30} mois)")
    
    def update_total(self):
        """Met à jour le total calculé"""
        prime = self.prime_pure.value()
        access = self.accessoires.value()
        taxes = self.taxes.value()
        discount = self.discount.value()
        commission = self.commission.value()
        
        total = prime + access + taxes
        if discount > 0:
            total = total * (1 - discount / 100)
        if commission > 0:
            total = total * (1 + commission / 100)
        
        self.total_label.setText(f"XAF {total:,.0f}".replace(",", " "))
    
    def load_contacts(self):
        """Charge la liste des contacts"""
        try:
            from addons.Automobiles.models.contact_models import Contact
            if self.controller and hasattr(self.controller, 'session'):
                contacts = self.controller.session.query(Contact).limit(100).all()
                for contact in contacts:
                    name = getattr(contact, 'nom', getattr(contact, 'name', f"Contact {contact.id}"))
                    self.owner_combo.addItem(name, contact.id)
        except Exception as e:
            print(f"Erreur chargement contacts: {e}")
    
    def load_companies(self):
        """Charge la liste des compagnies"""
        try:
            from addons.Automobiles.models.compagnies_models import Compagnie
            if self.controller and hasattr(self.controller, 'session'):
                companies = self.controller.session.query(Compagnie).filter(Compagnie.is_active == True).limit(50).all()
                for company in companies:
                    name = getattr(company, 'nom', f"Compagnie {company.id}")
                    self.company_combo.addItem(name, company.id)
        except Exception as e:
            print(f"Erreur chargement compagnies: {e}")
    
    def load_vehicles(self):
        """Charge la liste des véhicules"""
        try:
            from addons.Automobiles.models.automobile_models import Vehicle
            if self.controller and hasattr(self.controller, 'session'):
                vehicles = self.controller.session.query(Vehicle).filter(Vehicle.is_active == True).limit(100).all()
                for vehicle in vehicles:
                    plate = getattr(vehicle, 'immatriculation', f"Véhicule {vehicle.id}")
                    self.vehicle_combo.addItem(plate, vehicle.id)
        except Exception as e:
            print(f"Erreur chargement véhicules: {e}")
    
    def load_contract(self):
        """Charge les données du contrat"""
        try:
            if self.controller and hasattr(self.controller, 'get_contract'):
                contract = self.controller.get_contract(self.contract_id)
                if contract:
                    self.police_input.setText(getattr(contract, 'numero_police', ''))
                    self.start_date.setDate(getattr(contract, 'date_debut', QDate.currentDate()))
                    self.end_date.setDate(getattr(contract, 'date_fin', QDate.currentDate().addDays(365)))
                    self.prime_pure.setValue(getattr(contract, 'prime_pure', 0))
                    self.accessoires.setValue(getattr(contract, 'accessoires', 0))
                    self.taxes.setValue(getattr(contract, 'taxes_totales', 0))
                    self.discount.setValue(getattr(contract, 'fleet_discount', 0))
                    self.update_total()
        except Exception as e:
            print(f"Erreur chargement contrat: {e}")
    
    def get_contract_data(self) -> Dict[str, Any]:
        """Récupère les données du formulaire"""
        return {
            'numero_police': self.police_input.text() or None,
            'owner_id': self.owner_combo.currentData(),
            'company_id': self.company_combo.currentData(),
            'vehicle_id': self.vehicle_combo.currentData(),
            'type_contrat': self.type_combo.currentText(),
            'statut': self.status_combo.currentText(),
            'date_debut': self.start_date.date().toPython(),
            'date_fin': self.end_date.date().toPython(),
            'date_proformat': self.proformat_date.date().toPython(),
            'prime_pure': self.prime_pure.value(),
            'accessoires': self.accessoires.value(),
            'taxes_totales': self.taxes.value(),
            'fleet_discount': self.discount.value(),
            'commission': self.commission.value(),
            'notes': self.notes_input.toPlainText()
        }


class ContractView(QWidget):
    """Vue principale de gestion des contrats - Version complète avec ScrollArea"""
    
    contract_selected = Signal(dict)
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.contracts_summary = []
        self.filtered_contracts = []
        self.selected_contract = None
        
        # Récupérer le contrôleur des contrats
        if hasattr(controller, 'contracts'):
            self.contract_ctrl = controller.contracts
        elif hasattr(controller, 'contract_controller'):
            self.contract_ctrl = controller.contract_controller
        else:
            self.contract_ctrl = None
        
        self.setup_ui()
        self.load_data()
        
        # Timer pour rafraîchissement auto
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(60000)
    
    # def setup_ui(self):
    #     """Configure l'interface avec ScrollArea"""
    #     layout = QVBoxLayout(self)
    #     layout.setContentsMargins(0, 0, 0, 0)
    #     layout.setSpacing(0)
        
    #     # ScrollArea principale
    #     scroll = QScrollArea()
    #     scroll.setWidgetResizable(True)
    #     scroll.setFrameShape(QScrollArea.NoFrame)
    #     scroll.setStyleSheet("""
    #         QScrollArea {
    #             background: transparent;
    #             border: none;
    #         }
    #         QScrollBar:vertical {
    #             background: #f1f5f9;
    #             width: 8px;
    #             border-radius: 4px;
    #         }
    #         QScrollBar::handle:vertical {
    #             background: #cbd5e1;
    #             border-radius: 4px;
    #             min-height: 20px;
    #         }
    #         QScrollBar::handle:vertical:hover {
    #             background: #3b82f6;
    #         }
    #     """)
        
    #     content = QWidget()
    #     content_layout = QVBoxLayout(content)
    #     content_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
    #     content_layout.setSpacing(Spacing.LG)
        
    #     # En-tête avec stats
    #     self.setup_stats_header()
    #     content_layout.addWidget(self.stats_card)
        
    #     # Barre d'outils
    #     self.setup_toolbar()
    #     content_layout.addWidget(self.toolbar)
        
    #     # Splitter pour tableau et détails
    #     splitter = QSplitter(Qt.Vertical)
    #     splitter.setHandleWidth(4)
    #     splitter.setStyleSheet("""
    #         QSplitterHandle {
    #             background: #e2e8f0;
    #             border-radius: 2px;
    #             height: 4px;
    #         }
    #     """)
        
    #     # Tableau des contrats
    #     self.setup_table()
    #     splitter.addWidget(self.table_card)
        
    #     # Détails du contrat sélectionné
    #     self.setup_details_panel()
    #     splitter.addWidget(self.details_panel)
    #     splitter.setSizes([450, 250])
        
    #     content_layout.addWidget(splitter, 1)
        
    #     # Onglets supplémentaires
    #     self.setup_tabs()
    #     content_layout.addWidget(self.tabs_widget)
        
    #     # Barre de statut
    #     self.setup_status_bar()
    #     content_layout.addWidget(self.status_bar)
        
    #     scroll.setWidget(content)
    #     layout.addWidget(scroll)

    # addons/Automobiles/views/contract_view.py

    def setup_ui(self):
        """Configure l'interface avec ScrollArea"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ScrollArea principale
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3b82f6;
            }
        """)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        content_layout.setSpacing(Spacing.LG)
        
        # En-tête avec stats
        self.setup_stats_header()
        content_layout.addWidget(self.stats_card)
        
        # Barre d'outils
        self.setup_toolbar()
        content_layout.addWidget(self.toolbar)
        
        # ✅ AJOUTER UN ESPACEMENT SUPPLÉMENTAIRE
        content_layout.addSpacing(Spacing.MD)
        
        # Splitter pour tableau et détails
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(4)
        splitter.setStyleSheet("""
            QSplitterHandle {
                background: #e2e8f0;
                border-radius: 2px;
                height: 4px;
            }
        """)
        
        # Tableau des contrats - AVEC PLUS D'ESPACE
        self.setup_table()
        splitter.addWidget(self.table_card)
        
        # Détails du contrat sélectionné
        self.setup_details_panel()
        splitter.addWidget(self.details_panel)
        splitter.setSizes([550, 200])  # ✅ Augmenté la taille du tableau
        
        content_layout.addWidget(splitter, 1)
        
        # Onglets supplémentaires
        self.setup_tabs()
        content_layout.addWidget(self.tabs_widget)
        
        # Barre de statut
        self.setup_status_bar()
        content_layout.addWidget(self.status_bar)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def setup_table(self):
        """Configure le tableau des contrats avec plus d'espace"""
        self.table_card = ModernCard(title="📋 Liste des contrats", icon="📄")
        self.table_card.setMinimumHeight(400)  # ✅ Hauteur minimale augmentée
        
        # Barre d'information sur la sélection
        selection_info = QHBoxLayout()
        selection_info.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)  # ✅ Marges
        self.selection_label = QLabel("0 contrat(s) sélectionné(s)")
        self.selection_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        self.select_all_cb = QCheckBox("Tout sélectionner")
        self.select_all_cb.stateChanged.connect(self.on_select_all)
        
        selection_info.addWidget(self.selection_label)
        selection_info.addStretch()
        selection_info.addWidget(self.select_all_cb)
        
        self.table_card.add_layout(selection_info)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Police", "Souscripteur", "Véhicule", "Début", "Fin",
            "Prime TTC", "Statut", "Paiement", "Échéance", "Actions"
        ])
        
        # ✅ Configuration des colonnes avec plus d'espace
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # ✅ Le souscripteur prend l'espace
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        
        # ✅ Largeurs des colonnes ajustées
        self.table.setColumnWidth(0, 130)   # Police
        self.table.setColumnWidth(2, 120)   # Véhicule
        self.table.setColumnWidth(3, 100)   # Début
        self.table.setColumnWidth(4, 100)   # Fin
        self.table.setColumnWidth(5, 120)   # Prime TTC
        self.table.setColumnWidth(6, 100)   # Statut
        self.table.setColumnWidth(7, 110)   # Paiement
        self.table.setColumnWidth(8, 100)   # Échéance
        self.table.setColumnWidth(9, 120)   # Actions
        
        # ✅ Hauteur des lignes augmentée
        self.table.verticalHeader().setDefaultSectionSize(45)
        self.table.verticalHeader().setMinimumSectionSize(40)
        
        # ✅ Padding pour les cellules
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: none;
                border-radius: 12px;
                gridline-color: #f1f5f9;
                padding: 4px;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #eef2ff;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 12px 8px;
                font-weight: 600;
                color: #475569;
                font-size: 12px;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3b82f6;
            }
        """)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.on_contract_double_clicked)
        self.table.clicked.connect(self.on_contract_selected)
        
        self.table_card.add_widget(self.table)

    def setup_stats_header(self):
        """Configure l'en-tête avec statistiques animées"""
        self.stats_card = ModernCard(title="📊 Aperçu des contrats", icon="📊")
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(Spacing.XL)
        
        stats_items = [
            ("total", "📄", "Total contrats", "0"),
            ("active", "✅", "Actifs", "0"),
            ("expiring", "⏰", "Échéance < 30j", "0"),
            ("expired", "❌", "Expirés", "0"),
            ("revenue", "💰", "CA mensuel", "0 XAF")
        ]
        
        self.stats_labels = {}
        for key, icon, title, default in stats_items:
            stat_widget = QFrame()
            stat_widget.setStyleSheet(f"""
                QFrame {{
                    background: {Colors.WHITE};
                    border-radius: 12px;
                    padding: 12px;
                }}
            """)
            
            stat_layout = QHBoxLayout(stat_widget)
            stat_layout.setSpacing(Spacing.MD)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24px;")
            
            value_widget = QWidget()
            value_layout = QVBoxLayout(value_widget)
            value_layout.setSpacing(Spacing.XS)
            
            value_label = QLabel(default)
            value_label.setStyleSheet(f"""
                font-size: {Fonts.H3}px;
                font-weight: {Fonts.BOLD};
                color: {Colors.PRIMARY};
            """)
            
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                font-size: {Fonts.SMALL}px;
                color: {Colors.TEXT_SECONDARY};
            """)
            
            value_layout.addWidget(value_label)
            value_layout.addWidget(title_label)
            
            stat_layout.addWidget(icon_label)
            stat_layout.addWidget(value_widget)
            stat_layout.addStretch()
            
            stats_layout.addWidget(stat_widget)
            self.stats_labels[key] = value_label
        
        self.stats_card.add_layout(stats_layout)
    
    def setup_toolbar(self):
        """Configure la barre d'outils"""
        self.toolbar = QFrame()
        self.toolbar.setStyleSheet(f"""
            QFrame {{
                background: {Colors.WHITE};
                border-radius: 12px;
                padding: 8px;
            }}
        """)
        
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        toolbar_layout.setSpacing(Spacing.MD)
        
        # Boutons d'action
        self.new_btn = QPushButton("➕ Nouveau contrat")
        self.new_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK});
                color: {Colors.WHITE};
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: {Fonts.SEMIBOLD};
            }}
        """)
        self.new_btn.clicked.connect(self.on_new_contract)
        
        self.quick_actions = QComboBox()
        self.quick_actions.addItems([
            "Actions rapides",
            "📋 Dupliquer le contrat",
            "📤 Exporter en CSV",
            "📊 Générer un rapport",
            "📧 Envoyer par email"
        ])
        self.quick_actions.setFixedWidth(180)
        self.quick_actions.currentIndexChanged.connect(self.on_quick_action)
        
        toolbar_layout.addWidget(self.new_btn)
        toolbar_layout.addWidget(self.quick_actions)
        toolbar_layout.addStretch()
        
        # Recherche
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(Spacing.XS)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par police, souscripteur...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.on_search)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous", "ACTIF", "PROFORMAT", "EXPIRE", "RESILIE", "ANNULE"])
        self.status_filter.setFixedWidth(140)
        self.status_filter.currentTextChanged.connect(self.on_filter_change)
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedSize(36, 36)
        self.refresh_btn.setToolTip("Rafraîchir")
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.GRAY_100};
                border-radius: 8px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background: {Colors.GRAY_200};
            }}
        """)
        self.refresh_btn.clicked.connect(self.load_data)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.status_filter)
        search_layout.addWidget(self.refresh_btn)
        
        toolbar_layout.addWidget(search_widget)
    
    # def setup_table(self):
    #     """Configure le tableau des contrats"""
    #     self.table_card = ModernCard(title="📋 Liste des contrats", icon="📄")
        
    #     # Barre d'information sur la sélection
    #     selection_info = QHBoxLayout()
    #     self.selection_label = QLabel("0 contrat(s) sélectionné(s)")
    #     self.selection_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
    #     self.select_all_cb = QCheckBox("Tout sélectionner")
    #     self.select_all_cb.stateChanged.connect(self.on_select_all)
        
    #     selection_info.addWidget(self.selection_label)
    #     selection_info.addStretch()
    #     selection_info.addWidget(self.select_all_cb)
        
    #     self.table_card.add_layout(selection_info)
        
    #     # Tableau
    #     self.table = QTableWidget()
    #     self.table.setColumnCount(10)
    #     self.table.setHorizontalHeaderLabels([
    #         "Police", "Souscripteur", "Véhicule", "Début", "Fin",
    #         "Prime TTC", "Statut", "Paiement", "Échéance", "Actions"
    #     ])
        
    #     # Configuration des colonnes
    #     header = self.table.horizontalHeader()
    #     header.setStretchLastSection(True)
    #     header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
    #     header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
    #     header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
    #     header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
    #     header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
    #     header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
    #     header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
    #     header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
    #     header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
    #     header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
    #     self.table.setColumnWidth(9, 120)
        
    #     self.table.setAlternatingRowColors(True)
    #     self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    #     self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    #     self.table.setSortingEnabled(True)
    #     self.table.doubleClicked.connect(self.on_contract_double_clicked)
    #     self.table.clicked.connect(self.on_contract_selected)
        
    #     self.table_card.add_widget(self.table)
    
    def setup_details_panel(self):
        """Configure le panneau de détails du contrat"""
        self.details_panel = QFrame()
        self.details_panel.setStyleSheet(f"""
            QFrame {{
                background: {Colors.WHITE};
                border-radius: 12px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        self.details_panel.setVisible(False)
        
        layout = QVBoxLayout(self.details_panel)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)
        
        # En-tête des détails
        header = QHBoxLayout()
        title = QLabel("📄 Détails du contrat")
        title.setStyleSheet(f"font-size: 16px; font-weight: {Fonts.BOLD};")
        header.addWidget(title)
        header.addStretch()
        
        # Boutons d'action rapide dans les détails
        self.detail_action_btn = QPushButton("✏️ Modifier")
        self.detail_action_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.PRIMARY};
                color: {Colors.WHITE};
                border-radius: 8px;
                padding: 6px 16px;
            }}
        """)
        self.detail_action_btn.clicked.connect(lambda: self.on_edit_contract(self.selected_contract))
        
        self.detail_close_btn = QPushButton("✕")
        self.detail_close_btn.setFixedSize(30, 30)
        self.detail_close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 15px;
                background: #e2e8f0;
            }
            QPushButton:hover {
                background: #ef4444;
                color: white;
            }
        """)
        self.detail_close_btn.clicked.connect(lambda: self.details_panel.setVisible(False))
        
        header.addWidget(self.detail_action_btn)
        header.addWidget(self.detail_close_btn)
        layout.addLayout(header)
        
        # Grille des détails
        self.details_grid = QGridLayout()
        self.details_grid.setSpacing(Spacing.MD)
        layout.addLayout(self.details_grid)
        
        # Liste des champs de détails
        detail_fields = [
            ("Police:", "police", ""),
            ("Souscripteur:", "souscripteur", ""),
            ("Véhicule:", "vehicule", ""),
            ("Compagnie:", "compagnie", ""),
            ("Type:", "type", ""),
            ("Date début:", "date_debut", ""),
            ("Date fin:", "date_fin", ""),
            ("Prime TTC:", "prime", ""),
            ("Statut paiement:", "statut_paiement", ""),
            ("Jours restants:", "jours_restants", ""),
            ("Notes:", "notes", "")
        ]
        
        self.detail_labels = {}
        for i, (label, key, default) in enumerate(detail_fields):
            row = i // 2
            col = (i % 2) * 2
            
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #64748b; font-weight: 500;")
            self.details_grid.addWidget(lbl, row, col)
            
            val = QLabel(default)
            val.setStyleSheet("font-weight: 500;")
            self.details_grid.addWidget(val, row, col + 1)
            self.detail_labels[key] = val
    
    def setup_tabs(self):
        """Configure les onglets supplémentaires"""
        self.tabs_widget = QTabWidget()
        self.tabs_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
            QTabBar::tab {{
                padding: 10px 20px;
                margin-right: 4px;
            }}
        """)
        
        # Onglet Échéances
        expiring_tab = self.create_expiring_tab()
        self.tabs_widget.addTab(expiring_tab, "📅 Échéances")
        
        # Onglet Statistiques
        stats_tab = self.create_stats_tab()
        self.tabs_widget.addTab(stats_tab, "📊 Statistiques")
        
        # Onglet Paiements
        payments_tab = self.create_payments_tab()
        self.tabs_widget.addTab(payments_tab, "💳 Paiements")
    
    def create_expiring_tab(self):
        """Crée l'onglet des échéances"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Info
        info = QLabel("Contrats arrivant à échéance dans les 30 prochains jours")
        info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(info)
        
        self.expiring_table = QTableWidget()
        self.expiring_table.setColumnCount(6)
        self.expiring_table.setHorizontalHeaderLabels(["Police", "Souscripteur", "Date fin", "Jours restants", "Montant", "Action"])
        self.expiring_table.setAlternatingRowColors(True)
        self.expiring_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        layout.addWidget(self.expiring_table)
        
        return tab
    
    def create_stats_tab(self):
        """Crée l'onglet des statistiques"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Stats en cartes
        stats_grid = QGridLayout()
        stats_grid.setSpacing(Spacing.MD)
        
        stats_data = [
            ("📊 Taux d'activation", "0%", "#3b82f6"),
            ("📈 Taux de recouvrement", "0%", "#10b981"),
            ("🔄 Taux de renouvellement", "0%", "#8b5cf6"),
            ("📉 Taux de résiliation", "0%", "#ef4444")
        ]
        
        self.stats_tab_labels = {}
        for i, (label, default, color) in enumerate(stats_data):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: {Colors.WHITE};
                    border-radius: 12px;
                    border: 1px solid {Colors.BORDER};
                    padding: 16px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            
            value_lbl = QLabel(default)
            value_lbl.setStyleSheet(f"""
                font-size: 24px;
                font-weight: {Fonts.BOLD};
                color: {color};
            """)
            
            label_lbl = QLabel(label)
            label_lbl.setStyleSheet(f"""
                font-size: 12px;
                color: {Colors.TEXT_SECONDARY};
            """)
            
            card_layout.addWidget(value_lbl)
            card_layout.addWidget(label_lbl)
            
            stats_grid.addWidget(card, i // 2, i % 2)
            self.stats_tab_labels[label] = value_lbl
        
        layout.addLayout(stats_grid)
        layout.addStretch()
        
        return tab
    
    def create_payments_tab(self):
        """Crée l'onglet des paiements"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info = QLabel("Historique des paiements du contrat sélectionné")
        info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(info)
        
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(5)
        self.payments_table.setHorizontalHeaderLabels(["Date", "Mode", "Montant", "Référence", "Statut"])
        self.payments_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.payments_table)
        
        return tab
    
    def setup_status_bar(self):
        """Configure la barre de statut"""
        self.status_bar = QFrame()
        self.status_bar.setStyleSheet(f"""
            QFrame {{
                background: {Colors.WHITE};
                border-radius: 10px;
                padding: 8px;
            }}
        """)
        
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        
        self.status_icon = QLabel("✅")
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.status_count = QLabel("0 contrats")
        self.status_count.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px;")
        self.status_last_update = QLabel("Dernière mise à jour: -")
        self.status_last_update.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px;")
        
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.status_count)
        status_layout.addWidget(self.status_last_update)
    
    # ============================================================
    # CHARGEMENT DES DONNÉES
    # ============================================================
    
    def load_data(self):
        """Charge les données des contrats depuis la base"""
        if not self.contract_ctrl:
            self.status_label.setText("Contrôleur non disponible")
            return
        
        try:
            # Récupérer tous les contrats
            contracts = self.contract_ctrl.get_all_contracts(limit=200, with_relations=True)
            
            # Convertir en dictionnaires pour la vue
            self.contracts_summary = []
            for contract in contracts:
                summary = self.contract_ctrl.get_contract_summary(contract.id)
                if summary:
                    self.contracts_summary.append(summary)
            
            self.filtered_contracts = self.contracts_summary.copy()
            self.refresh_table()
            self.update_stats()
            self.update_expiring_table()
            self.update_payments_table()
            
            self.status_count.setText(f"{len(self.contracts_summary)} contrats")
            self.status_label.setText("✅ Données chargées")
            self.status_last_update.setText(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.status_label.setText(f"❌ Erreur: {str(e)}")
            print(f"Erreur chargement contrats: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_table(self):
        """Rafraîchit le tableau avec les données résumées"""
        self.table.setRowCount(len(self.filtered_contracts))
        
        for row, contract in enumerate(self.filtered_contracts):
            # Checkbox de sélection
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Unchecked)
            self.table.setItem(row, 0, check_item)
            
            # Police
            self.table.setItem(row, 0, QTableWidgetItem(contract.get('numero_police', '-')))
            
            # Souscripteur
            self.table.setItem(row, 1, QTableWidgetItem(contract.get('owner_name', '-')))
            
            # Véhicule
            self.table.setItem(row, 2, QTableWidgetItem(contract.get('vehicle_plate', '-')))
            
            # Dates
            self.table.setItem(row, 3, QTableWidgetItem(contract.get('date_debut', '-')))
            self.table.setItem(row, 4, QTableWidgetItem(contract.get('date_fin', '-')))
            
            # Prime
            prime = contract.get('prime_totale_ttc', 0)
            self.table.setItem(row, 5, QTableWidgetItem(f"XAF {prime:,.0f}".replace(",", " ")))
            
            # Statut
            status = contract.get('statut', 'INCONNU')
            status_label = contract.get('statut_label', status)
            status_item = QTableWidgetItem(str(status_label))
            status_colors = {
                'ACTIF': Colors.SUCCESS,
                'PROFORMAT': Colors.WARNING,
                'EXPIRE': Colors.DANGER,
                'RESILIE': Colors.DANGER,
                'ANNULE': Colors.TEXT_MUTED
            }
            status_item.setForeground(QColor(status_colors.get(status, Colors.TEXT_SECONDARY)))
            self.table.setItem(row, 6, status_item)
            
            # Paiement
            payment = contract.get('statut_paiement', 'NON_PAYE')
            payment_label = contract.get('statut_paiement_label', str(payment))
            payment_item = QTableWidgetItem(str(payment_label))
            payment_color = Colors.SUCCESS if payment == "PAYE" else Colors.WARNING
            payment_item.setForeground(QColor(payment_color))
            self.table.setItem(row, 7, payment_item)
            
            # Échéance
            days_left = self.get_days_left_from_summary(contract)
            days_item = QTableWidgetItem(days_left)
            if "J-7" in days_left or "Expiré" in days_left:
                days_item.setForeground(QColor(Colors.DANGER))
            elif "J-15" in days_left:
                days_item.setForeground(QColor(Colors.WARNING))
            self.table.setItem(row, 8, days_item)
            
            # Actions
            actions_widget = self.create_actions_widget(contract)
            self.table.setCellWidget(row, 9, actions_widget)
    
    def get_days_left_from_summary(self, contract):
        """Calcule les jours restants à partir du résumé"""
        date_fin = contract.get('date_fin')
        if not date_fin or date_fin == '-':
            return "-"
        
        try:
            end_date = datetime.strptime(date_fin, "%d/%m/%Y").date()
            days_left = (end_date - datetime.now().date()).days
            
            if days_left < 0:
                return "⚠️ Expiré"
            elif days_left == 0:
                return "⚠️ Aujourd'hui"
            elif days_left <= 7:
                return f"🔴 J-{days_left}"
            elif days_left <= 15:
                return f"🟡 J-{days_left}"
            elif days_left <= 30:
                return f"🟢 J-{days_left}"
            else:
                return f"{days_left} jours"
        except:
            return "-"
    
    def create_actions_widget(self, contract):
        """Crée les boutons d'action"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(Spacing.XS, Spacing.XS, Spacing.XS, Spacing.XS)
        layout.setSpacing(Spacing.XS)
        
        actions = [
            ("👁️", "Voir détails", self.on_view_contract),
            ("✏️", "Modifier", self.on_edit_contract),
            ("📄", "PDF", self.on_generate_pdf),
            ("🗑️", "Supprimer", self.on_delete_contract)
        ]
        
        for icon, tooltip, callback in actions:
            btn = QPushButton(icon)
            btn.setFixedSize(30, 30)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 15px;
                    background: transparent;
                }
                QPushButton:hover {
                    background: #e2e8f0;
                }
            """)
            btn.clicked.connect(lambda checked, c=contract, cb=callback: cb(c))
            layout.addWidget(btn)
        
        return widget
    
    # ============================================================
    # MISE À JOUR DES STATISTIQUES
    # ============================================================
    
    def update_stats(self):
        """Met à jour les statistiques"""
        total = len(self.contracts_summary)
        active = sum(1 for c in self.contracts_summary if c.get('statut') == 'ACTIF')
        
        today = datetime.now().date()
        expiring = 0
        expired = 0
        
        for c in self.contracts_summary:
            date_fin = c.get('date_fin')
            if date_fin and date_fin != '-':
                try:
                    end_date = datetime.strptime(date_fin, "%d/%m/%Y").date()
                    days_left = (end_date - today).days
                    if 0 <= days_left <= 30:
                        expiring += 1
                    elif days_left < 0:
                        expired += 1
                except:
                    pass
        
        # CA mensuel
        total_premium = sum(c.get('prime_totale_ttc', 0) for c in self.contracts_summary)
        monthly_revenue = total_premium / 12 if total > 0 else 0
        
        # Taux d'activation
        activation_rate = (active / total * 100) if total > 0 else 0
        
        # Taux de recouvrement
        total_paid = sum(c.get('montant_paye', 0) for c in self.contracts_summary)
        recovery_rate = (total_paid / total_premium * 100) if total_premium > 0 else 0
        
        self.stats_labels["total"].setText(str(total))
        self.stats_labels["active"].setText(str(active))
        self.stats_labels["expiring"].setText(str(expiring))
        self.stats_labels["expired"].setText(str(expired))
        self.stats_labels["revenue"].setText(f"XAF {monthly_revenue:,.0f}".replace(",", " "))
        
        # Mettre à jour les stats de l'onglet Statistiques
        if hasattr(self, 'stats_tab_labels'):
            self.stats_tab_labels.get("📊 Taux d'activation", QLabel()).setText(f"{activation_rate:.1f}%")
            self.stats_tab_labels.get("📈 Taux de recouvrement", QLabel()).setText(f"{recovery_rate:.1f}%")
            self.stats_tab_labels.get("🔄 Taux de renouvellement", QLabel()).setText("0%")
            self.stats_tab_labels.get("📉 Taux de résiliation", QLabel()).setText("0%")
    
    def update_expiring_table(self):
        """Met à jour le tableau des échéances"""
        today = datetime.now().date()
        expiring_contracts = []
        
        for contract in self.contracts_summary:
            date_fin = contract.get('date_fin')
            if date_fin and date_fin != '-':
                try:
                    end_date = datetime.strptime(date_fin, "%d/%m/%Y").date()
                    days_left = (end_date - today).days
                    if 0 <= days_left <= 30:
                        expiring_contracts.append((contract, days_left))
                except:
                    pass
        
        expiring_contracts.sort(key=lambda x: x[1])
        
        self.expiring_table.setRowCount(len(expiring_contracts))
        
        for row, (contract, days_left) in enumerate(expiring_contracts):
            police = contract.get('numero_police', '-')
            self.expiring_table.setItem(row, 0, QTableWidgetItem(str(police)))
            
            owner_name = contract.get('owner_name', '-')
            self.expiring_table.setItem(row, 1, QTableWidgetItem(str(owner_name)))
            
            date_fin = contract.get('date_fin', '-')
            self.expiring_table.setItem(row, 2, QTableWidgetItem(str(date_fin)))
            
            days_item = QTableWidgetItem(f"{days_left} jours")
            if days_left <= 7:
                days_item.setForeground(QColor(Colors.DANGER))
            elif days_left <= 15:
                days_item.setForeground(QColor(Colors.WARNING))
            self.expiring_table.setItem(row, 3, days_item)
            
            prime = contract.get('prime_totale_ttc', 0)
            self.expiring_table.setItem(row, 4, QTableWidgetItem(f"XAF {prime:,.0f}".replace(",", " ")))
            
            renew_btn = QPushButton("Renouveler")
            renew_btn.setFixedWidth(100)
            renew_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.PRIMARY};
                    color: white;
                    border-radius: 6px;
                    padding: 4px 8px;
                }}
            """)
            renew_btn.clicked.connect(lambda checked, c=contract: self.on_renew_contract(c))
            self.expiring_table.setCellWidget(row, 5, renew_btn)
    
    def update_payments_table(self):
        """Met à jour le tableau des paiements"""
        # Données simulées pour l'instant
        payments = [
            ("15/06/2026", "Carte bancaire", "150 000 XAF", "PAY-001", "✅ Payé"),
            ("15/05/2026", "Virement", "150 000 XAF", "PAY-002", "✅ Payé"),
            ("15/04/2026", "Espèces", "150 000 XAF", "PAY-003", "⏳ En attente"),
        ]
        
        self.payments_table.setRowCount(len(payments))
        for row, payment in enumerate(payments):
            for col, value in enumerate(payment):
                item = QTableWidgetItem(value)
                if "✅" in value:
                    item.setForeground(QColor(Colors.SUCCESS))
                elif "⏳" in value:
                    item.setForeground(QColor(Colors.WARNING))
                self.payments_table.setItem(row, col, item)
    
    # ============================================================
    # GESTION DE LA SÉLECTION
    # ============================================================
    
    def on_contract_selected(self, index):
        """Affiche les détails du contrat sélectionné"""
        row = index.row()
        if row < len(self.filtered_contracts):
            self.selected_contract = self.filtered_contracts[row]
            self.show_contract_details(self.selected_contract)
            
            # Mettre à jour le compteur de sélection
            self.update_selection_count()
    
    def show_contract_details(self, contract):
        """Affiche les détails d'un contrat"""
        self.details_panel.setVisible(True)
        
        date_fin = contract.get('date_fin', '-')
        jours_restants = "-"
        if date_fin and date_fin != '-':
            try:
                end_date = datetime.strptime(date_fin, "%d/%m/%Y").date()
                days = (end_date - datetime.now().date()).days
                jours_restants = f"{days} jours" if days >= 0 else "Expiré"
            except:
                pass
        
        details = {
            'police': contract.get('numero_police', '-'),
            'souscripteur': contract.get('owner_name', '-'),
            'vehicule': contract.get('vehicle_plate', '-'),
            'compagnie': contract.get('company_name', '-'),
            'type': contract.get('type_contrat', '-'),
            'date_debut': contract.get('date_debut', '-'),
            'date_fin': contract.get('date_fin', '-'),
            'prime': f"XAF {contract.get('prime_totale_ttc', 0):,.0f}".replace(",", " "),
            'statut_paiement': contract.get('statut_paiement_label', '-'),
            'jours_restants': jours_restants,
            'notes': contract.get('notes', '-')
        }
        
        for key, value in details.items():
            if key in self.detail_labels:
                self.detail_labels[key].setText(str(value))
    
    def on_select_all(self, state):
        """Sélectionne/désélectionne tous les contrats"""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.Checked if state == Qt.Checked else Qt.Unchecked)
        self.update_selection_count()
    
    def update_selection_count(self):
        """Met à jour le compteur de sélection"""
        count = 0
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                count += 1
        self.selection_label.setText(f"{count} contrat(s) sélectionné(s)")
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def on_new_contract(self):
        """Crée un nouveau contrat"""
        dialog = ContractDialog(self.controller, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_contract_data()
            try:
                if self.contract_ctrl and hasattr(self.contract_ctrl, 'create_contract'):
                    success, contract, message = self.contract_ctrl.create_contract(data, 1)
                    if success:
                        self.load_data()
                        QMessageBox.information(self, "Succès", "✅ Contrat créé avec succès")
                    else:
                        QMessageBox.critical(self, "Erreur", f"❌ {message}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"❌ Erreur: {str(e)}")
    
    def on_edit_contract(self, contract):
        """Modifie un contrat"""
        if contract and contract.get('id'):
            dialog = ContractDialog(self.controller, contract['id'], self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()
                QMessageBox.information(self, "Succès", "✅ Contrat modifié")
    
    def on_view_contract(self, contract):
        """Affiche les détails d'un contrat"""
        self.show_contract_details(contract)
        QMessageBox.information(self, "Détails du contrat", 
            f"📄 Contrat: {contract.get('numero_police', '-')}\n"
            f"👤 Souscripteur: {contract.get('owner_name', '-')}\n"
            f"🚗 Véhicule: {contract.get('vehicle_plate', '-')}\n"
            f"💰 Prime: XAF {contract.get('prime_totale_ttc', 0):,.0f}\n"
            f"📅 Début: {contract.get('date_debut', '-')}\n"
            f"📅 Fin: {contract.get('date_fin', '-')}\n"
            f"📌 Statut: {contract.get('statut_label', '-')}"
        )
    
    def on_delete_contract(self, contract):
        """Supprime un contrat"""
        police = contract.get('numero_police', '-')
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer le contrat {police} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.contract_ctrl and hasattr(self.contract_ctrl, 'delete_contract'):
                success, message = self.contract_ctrl.delete_contract(contract['id'], 1)
                if success:
                    QMessageBox.information(self, "Succès", "✅ Contrat supprimé")
                    self.load_data()
                else:
                    QMessageBox.critical(self, "Erreur", f"❌ {message}")
    
    def on_renew_contract(self, contract):
        """Renouvelle un contrat"""
        police = contract.get('numero_police', '-')
        reply = QMessageBox.question(
            self,
            "Renouvellement",
            f"Voulez-vous renouveler le contrat {police} pour un an ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Calculer les nouvelles dates
                debut = datetime.now().date()
                fin = debut + timedelta(days=365)
                
                # Mettre à jour le contrat
                if self.contract_ctrl and hasattr(self.contract_ctrl, 'update_contract'):
                    success, message = self.contract_ctrl.update_contract(
                        contract['id'],
                        {
                            'date_debut': debut,
                            'date_fin': fin,
                            'statut': 'ACTIF'
                        },
                        1
                    )
                    if success:
                        self.load_data()
                        QMessageBox.information(self, "Succès", f"✅ Contrat {police} renouvelé jusqu'au {fin.strftime('%d/%m/%Y')}")
                    else:
                        QMessageBox.critical(self, "Erreur", f"❌ {message}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"❌ Erreur: {str(e)}")
    
    def on_generate_pdf(self, contract):
        """Génère un PDF du contrat"""
        police = contract.get('numero_police', '-')
        QMessageBox.information(self, "PDF", f"📄 Génération du PDF pour {police}")
    
    def on_quick_action(self, index):
        """Gère les actions rapides"""
        action = self.quick_actions.currentText()
        if action == "Actions rapides":
            return
        
        if action == "📋 Dupliquer le contrat":
            self.on_duplicate_contract()
        elif action == "📤 Exporter en CSV":
            self.on_export_csv()
        elif action == "📊 Générer un rapport":
            self.on_generate_report()
        elif action == "📧 Envoyer par email":
            self.on_send_email()
        
        self.quick_actions.setCurrentIndex(0)
    
    def on_duplicate_contract(self):
        """Duplique le contrat sélectionné"""
        if not self.selected_contract:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un contrat à dupliquer")
            return
        
        # Créer une copie du contrat
        try:
            data = self.selected_contract.copy()
            data.pop('id', None)
            data['numero_police'] = None  # Auto-généré
            
            if self.contract_ctrl and hasattr(self.contract_ctrl, 'create_contract'):
                success, contract, message = self.contract_ctrl.create_contract(data, 1)
                if success:
                    self.load_data()
                    QMessageBox.information(self, "Succès", "✅ Contrat dupliqué avec succès")
                else:
                    QMessageBox.critical(self, "Erreur", f"❌ {message}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"❌ Erreur: {str(e)}")
    
    def on_export_csv(self):
        """Exporte les données en CSV"""
        try:
            from PySide6.QtWidgets import QFileDialog
            
            path, _ = QFileDialog.getSaveFileName(
                self, "Exporter les contrats", f"contrats_{datetime.now().strftime('%Y%m%d')}.csv", "CSV (*.csv)"
            )
            
            if path:
                with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Police", "Souscripteur", "Véhicule", "Début", "Fin", "Prime TTC", "Statut", "Paiement"])
                    for contract in self.contracts_summary:
                        writer.writerow([
                            contract.get('numero_police', ''),
                            contract.get('owner_name', ''),
                            contract.get('vehicle_plate', ''),
                            contract.get('date_debut', ''),
                            contract.get('date_fin', ''),
                            contract.get('prime_totale_ttc', 0),
                            contract.get('statut_label', ''),
                            contract.get('statut_paiement_label', '')
                        ])
                QMessageBox.information(self, "Succès", f"✅ {len(self.contracts_summary)} contrats exportés")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"❌ Erreur: {str(e)}")
    
    def on_generate_report(self):
        """Génère un rapport"""
        total = len(self.contracts_summary)
        active = sum(1 for c in self.contracts_summary if c.get('statut') == 'ACTIF')
        total_premium = sum(c.get('prime_totale_ttc', 0) for c in self.contracts_summary)
        
        report = f"""
        📊 RAPPORT DES CONTRATS
        {'='*40}
        Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        📋 RÉSUMÉ
        {'-'*40}
        Total contrats: {total}
        Contrats actifs: {active}
        Taux d'activation: {(active/total*100):.1f}%
        
        💰 FINANCES
        {'-'*40}
        Prime totale: XAF {total_premium:,.0f}
        Prime mensuelle moyenne: XAF {total_premium/12:,.0f}
        """
        
        QMessageBox.information(self, "Rapport", report)
    
    def on_send_email(self):
        """Envoie par email"""
        if not self.selected_contract:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un contrat")
            return
        
        QMessageBox.information(self, "Email", f"📧 Envoi du contrat {self.selected_contract.get('numero_police', '-')} par email")
    
    def on_search(self, text):
        """Recherche de contrats"""
        if not text:
            self.filtered_contracts = self.contracts_summary.copy()
        else:
            text_lower = text.lower()
            self.filtered_contracts = [
                c for c in self.contracts_summary
                if text_lower in c.get('numero_police', '').lower() or
                   text_lower in c.get('owner_name', '').lower()
            ]
        self.refresh_table()
    
    def on_filter_change(self):
        """Filtre par statut"""
        status = self.status_filter.currentText()
        if status == "Tous":
            self.filtered_contracts = self.contracts_summary.copy()
        else:
            self.filtered_contracts = [
                c for c in self.contracts_summary
                if c.get('statut', '') == status
            ]
        self.refresh_table()
    
    def on_contract_double_clicked(self, index):
        """Double-clic sur un contrat"""
        row = index.row()
        if row < len(self.filtered_contracts):
            contract = self.filtered_contracts[row]
            self.on_view_contract(contract)
    
    def refresh_data(self):
        """Rafraîchit les données"""
        self.load_data()

