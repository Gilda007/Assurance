
# # addons/Automobiles/views/sinistre/sinistre_list_view.py
# """
# Vue de la liste des sinistres - Version avec vue tableau et vue cartes
# """

# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog,
#     QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
#     QLineEdit, QFrame, QMessageBox, QScrollArea, QGridLayout,
#     QSizePolicy, QButtonGroup
# )
# from PySide6.QtCore import Qt, QTimer, QSize
# from PySide6.QtGui import QColor, QFont

# from addons.Automobiles.views.style import Colors, Fonts, Spacing
# from addons.Automobiles.views.widgets.modern_card import ModernCard
# from addons.Automobiles.views.sinistre.sinistre_card import SinistreCard
# from addons.Automobiles.models.sinistre_models import StatutSinistre, TypeSinistre

# class SinistreListView(QWidget):
#     """Vue de la liste des sinistres avec mode tableau et mode cartes"""
    
#     # Constantes pour les modes d'affichage
#     MODE_TABLEAU = "tableau"
#     MODE_CARTES = "cartes"
    
#     def __init__(self, controller, user=None):
#         super().__init__()
#         self.controller = controller
#         self.user = user
#         self.current_mode = self.MODE_TABLEAU
#         self.sinistres = []
#         self.filtered_sinistres = []
        
#         self.setup_ui()
#         self.load_data()
    
#     # def setup_ui(self):
#     #     layout = QVBoxLayout(self)
#     #     layout.setSpacing(Spacing.LG)
#     #     layout.setContentsMargins(0, 0, 0, 0)
        
#     #     # En-tête
#     #     header = self.setup_header()
#     #     layout.addWidget(header)
        
#     #     # Filtres
#     #     filters = self.setup_filters()
#     #     layout.addWidget(filters)
        
#     #     # Statistiques
#     #     self.stats_widget = self.setup_stats()
#     #     layout.addWidget(self.stats_widget)
        
#     #     # Zone de contenu (tableau ou cartes)
#     #     self.content_frame = QFrame()
#     #     self.content_layout = QVBoxLayout(self.content_frame)
#     #     self.content_layout.setContentsMargins(0, 0, 0, 0)
#     #     self.content_layout.setSpacing(Spacing.MD)
        
#     #     # Tableau
#     #     self.table = self.setup_table()
#     #     self.content_layout.addWidget(self.table)
        
#     #     # Zone cartes (cachée par défaut)
#     #     self.cards_scroll = QScrollArea()
#     #     self.cards_scroll.setWidgetResizable(True)
#     #     self.cards_scroll.setStyleSheet("border: none; background: transparent;")
#     #     self.cards_container = QWidget()
#     #     self.cards_layout = QGridLayout(self.cards_container)
#     #     self.cards_layout.setSpacing(Spacing.MD)
#     #     self.cards_scroll.setWidget(self.cards_container)
#     #     self.cards_scroll.setVisible(False)
#     #     self.content_layout.addWidget(self.cards_scroll)
        
#     #     layout.addWidget(self.content_frame, 1)
    
#     def setup_ui(self):
#         layout = QVBoxLayout(self)
#         layout.setSpacing(Spacing.LG)
#         layout.setContentsMargins(0, 0, 0, 0)
        
#         # En-tête
#         header = self.setup_header()
#         layout.addWidget(header)
        
#         # Filtres
#         filters = self.setup_filters()
#         layout.addWidget(filters)
        
#         # Statistiques
#         self.stats_widget = self.setup_stats()
#         layout.addWidget(self.stats_widget)
        
#         # Zone de contenu (tableau ou cartes)
#         self.content_frame = QFrame()
#         self.content_layout = QVBoxLayout(self.content_frame)
#         self.content_layout.setContentsMargins(0, 0, 0, 0)
#         self.content_layout.setSpacing(Spacing.MD)
        
#         # Tableau
#         self.table = self.setup_table()
#         self.content_layout.addWidget(self.table)
        
#         # ✅ Zone cartes avec GridLayout 5 colonnes
#         self.cards_scroll = QScrollArea()
#         self.cards_scroll.setWidgetResizable(True)
#         self.cards_scroll.setStyleSheet("""
#             QScrollArea {
#                 border: none;
#                 background: transparent;
#             }
#             QScrollBar:vertical {
#                 background: #f1f5f9;
#                 width: 8px;
#                 border-radius: 4px;
#             }
#             QScrollBar::handle:vertical {
#                 background: #cbd5e1;
#                 border-radius: 4px;
#                 min-height: 30px;
#             }
#             QScrollBar::handle:vertical:hover {
#                 background: #94a3b8;
#             }
#             QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
#                 height: 0px;
#             }
#         """)
        
#         self.cards_container = QWidget()
#         self.cards_container.setStyleSheet("background: transparent;")
        
#         # ✅ GridLayout avec 5 colonnes
#         self.cards_layout = QGridLayout(self.cards_container)
#         self.cards_layout.setSpacing(Spacing.MD)
#         self.cards_layout.setContentsMargins(0, 0, 0, 0)
        
#         # ✅ Configurer 5 colonnes
#         for col in range(5):
#             self.cards_layout.setColumnStretch(col, 1)
        
#         self.cards_scroll.setWidget(self.cards_container)
#         self.cards_scroll.setVisible(False)
#         self.content_layout.addWidget(self.cards_scroll)
        
#         layout.addWidget(self.content_frame, 1)

#     def setup_header(self):
#         """En-tête de la page"""
#         header = QFrame()
#         header_layout = QHBoxLayout(header)
#         header_layout.setContentsMargins(0, 0, 0, 0)
        
#         title = QLabel("Gestion des Sinistres")
#         title.setStyleSheet(f"""
#             font-size: {Fonts.H2}px;
#             font-weight: {Fonts.BOLD};
#             color: {Colors.TEXT_PRIMARY};
#         """)
        
#         # Groupe de boutons
#         btn_group = QWidget()
#         btn_layout = QHBoxLayout(btn_group)
#         btn_layout.setContentsMargins(0, 0, 0, 0)
#         btn_layout.setSpacing(Spacing.SM)
        
#         # Bouton Vue Tableau
#         self.btn_tableau = QPushButton("📊 Tableau")
#         self.btn_tableau.setCheckable(True)
#         self.btn_tableau.setChecked(True)
#         self.btn_tableau.setStyleSheet(self._get_view_button_style(True))
#         self.btn_tableau.clicked.connect(lambda: self.switch_view(self.MODE_TABLEAU))
#         btn_layout.addWidget(self.btn_tableau)
        
#         # Bouton Vue Cartes
#         self.btn_cartes = QPushButton("📋 Cartes")
#         self.btn_cartes.setCheckable(True)
#         self.btn_cartes.setStyleSheet(self._get_view_button_style(False))
#         self.btn_cartes.clicked.connect(lambda: self.switch_view(self.MODE_CARTES))
#         btn_layout.addWidget(self.btn_cartes)
        
#         # Bouton Nouveau
#         btn_new = QPushButton("+ Nouveau Sinistre")
#         btn_new.setStyleSheet(f"""
#             QPushButton {{
#                 background-color: {Colors.PRIMARY};
#                 color: white;
#                 border: none;
#                 border-radius: 8px;
#                 padding: 10px 20px;
#                 font-weight: {Fonts.MEDIUM};
#             }}
#             QPushButton:hover {{
#                 background-color: {Colors.PRIMARY_DARK};
#             }}
#         """)
#         btn_new.clicked.connect(self.open_new_sinistre)
        
#         header_layout.addWidget(title)
#         header_layout.addStretch()
#         header_layout.addWidget(btn_group)
#         header_layout.addWidget(btn_new)
        
#         return header
    
#     def _get_view_button_style(self, is_active):
#         """Style des boutons de vue"""
#         if is_active:
#             return f"""
#                 QPushButton {{
#                     background-color: {Colors.PRIMARY};
#                     color: white;
#                     border: none;
#                     border-radius: 8px;
#                     padding: 8px 16px;
#                     font-weight: {Fonts.MEDIUM};
#                 }}
#                 QPushButton:hover {{
#                     background-color: {Colors.PRIMARY_DARK};
#                 }}
#             """
#         else:
#             return f"""
#                 QPushButton {{
#                     background-color: {Colors.GRAY_100};
#                     color: {Colors.TEXT_SECONDARY};
#                     border: none;
#                     border-radius: 8px;
#                     padding: 8px 16px;
#                     font-weight: {Fonts.MEDIUM};
#                 }}
#                 QPushButton:hover {{
#                     background-color: {Colors.GRAY_200};
#                 }}
#             """
    
#     def setup_filters(self):
#         """Barre de filtres"""
#         filters = QFrame()
#         filters.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {Colors.WHITE};
#                 border: 1px solid {Colors.BORDER};
#                 border-radius: 12px;
#                 padding: 12px;
#             }}
#         """)
        
#         layout = QHBoxLayout(filters)
#         layout.setSpacing(Spacing.MD)
        
#         # Recherche
#         self.search_input = QLineEdit()
#         self.search_input.setPlaceholderText("🔍 Rechercher un sinistre...")
#         self.search_input.textChanged.connect(self.filter_data)
#         self.search_input.setStyleSheet(self._get_input_style())
#         layout.addWidget(self.search_input, 2)
        
#         # Filtre statut
#         self.statut_filter = QComboBox()
#         self.statut_filter.addItem("Tous les statuts")
#         for statut in StatutSinistre:
#             self.statut_filter.addItem(statut.value)
#         self.statut_filter.currentTextChanged.connect(self.filter_data)
#         self.statut_filter.setStyleSheet(self._get_combo_style())
#         layout.addWidget(self.statut_filter, 1)
        
#         # Filtre type
#         self.type_filter = QComboBox()
#         self.type_filter.addItem("Tous les types")
#         for type_ in TypeSinistre:
#             self.type_filter.addItem(type_.value)
#         self.type_filter.currentTextChanged.connect(self.filter_data)
#         self.type_filter.setStyleSheet(self._get_combo_style())
#         layout.addWidget(self.type_filter, 1)
        
#         # Bouton Rafraîchir
#         btn_refresh = QPushButton("🔄")
#         btn_refresh.setFixedSize(36, 36)
#         btn_refresh.setStyleSheet(f"""
#             QPushButton {{
#                 background-color: {Colors.GRAY_100};
#                 border: 1px solid {Colors.BORDER};
#                 border-radius: 8px;
#                 font-size: 16px;
#             }}
#             QPushButton:hover {{
#                 background-color: {Colors.GRAY_200};
#             }}
#         """)
#         btn_refresh.clicked.connect(self.load_data)
#         layout.addWidget(btn_refresh)
        
#         return filters
    
#     def _get_input_style(self):
#         """Style des champs de saisie"""
#         return f"""
#             QLineEdit {{
#                 border: 1px solid {Colors.BORDER};
#                 border-radius: 8px;
#                 padding: 8px 12px;
#                 background-color: {Colors.WHITE};
#                 color: {Colors.TEXT_PRIMARY};
#                 font-size: 13px;
#             }}
#             QLineEdit:focus {{
#                 border-color: {Colors.PRIMARY};
#                 outline: none;
#             }}
#         """
    
#     def _get_combo_style(self):
#         """Style des QComboBox"""
#         return f"""
#             QComboBox {{
#                 border: 1px solid {Colors.BORDER};
#                 border-radius: 8px;
#                 padding: 8px 12px;
#                 background-color: {Colors.WHITE};
#                 color: {Colors.TEXT_PRIMARY};
#                 font-size: 13px;
#                 min-width: 120px;
#             }}
#             QComboBox:focus {{
#                 border-color: {Colors.PRIMARY};
#                 outline: none;
#             }}
#             QComboBox::drop-down {{
#                 border: none;
#                 width: 30px;
#             }}
#             QComboBox QAbstractItemView {{
#                 border: 1px solid {Colors.BORDER};
#                 border-radius: 8px;
#                 background-color: {Colors.WHITE};
#                 selection-background-color: {Colors.PRIMARY}20;
#                 selection-color: {Colors.TEXT_PRIMARY};
#                 padding: 4px;
#             }}
#         """
    
#     def setup_stats(self):
#         """Cartes de statistiques"""
#         stats = QFrame()
#         stats_layout = QHBoxLayout(stats)
#         stats_layout.setSpacing(Spacing.MD)
        
#         self.stats_cards = {}
#         stat_items = [
#             ("total", "Total", "0", "#2563eb"),
#             ("en_cours", "En cours", "0", "#f59e0b"),
#             ("clos", "Clos", "0", "#16a34a"),
#             ("urgent", "Urgents", "0", "#dc2626"),
#         ]
        
#         for key, title, value, color in stat_items:
#             card = QFrame()
#             card.setStyleSheet(f"""
#                 QFrame {{
#                     background-color: {Colors.WHITE};
#                     border: 1px solid {Colors.BORDER};
#                     border-radius: 12px;
#                     padding: 16px;
#                     min-width: 120px;
#                 }}
#             """)
#             card_layout = QVBoxLayout(card)
            
#             label_value = QLabel(value)
#             label_value.setStyleSheet(f"""
#                 font-size: {Fonts.H1}px;
#                 font-weight: {Fonts.BOLD};
#                 color: {color};
#             """)
#             label_value.setAlignment(Qt.AlignCenter)
            
#             label_title = QLabel(title)
#             label_title.setStyleSheet(f"""
#                 font-size: {Fonts.SMALL}px;
#                 color: {Colors.TEXT_SECONDARY};
#             """)
#             label_title.setAlignment(Qt.AlignCenter)
            
#             card_layout.addWidget(label_value)
#             card_layout.addWidget(label_title)
            
#             stats_layout.addWidget(card)
#             self.stats_cards[key] = label_value
        
#         return stats
    
#     def setup_table(self):
#         """Tableau des sinistres avec hauteur de ligne ajustée"""
#         table = QTableWidget()
#         table.setColumnCount(8)
#         table.setHorizontalHeaderLabels([
#             "N° Dossier", "Type", "Véhicule", "Date", "Statut", "Montant", "Jours", "Actions"
#         ])
        
#         # ✅ Ajustement des colonnes
#         table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
#         table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
#         table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
#         table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
#         table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
#         table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
#         table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
#         table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        
#         table.verticalHeader().setVisible(False)
#         table.setAlternatingRowColors(True)
        
#         # ✅ Hauteur des lignes
#         table.verticalHeader().setDefaultSectionSize(45)
        
#         # ✅ Style
#         table.setStyleSheet(f"""
#             QTableWidget {{
#                 background-color: {Colors.WHITE};
#                 border: 1px solid {Colors.BORDER};
#                 border-radius: 12px;
#                 gridline-color: {Colors.BORDER};
#             }}
#             QTableWidget::item {{
#                 padding: 8px 12px;
#             }}
#             QTableWidget::item:selected {{
#                 background-color: {Colors.PRIMARY}20;
#                 color: {Colors.TEXT_PRIMARY};
#             }}
#             QHeaderView::section {{
#                 background-color: {Colors.GRAY_50};
#                 padding: 8px 12px;
#                 border: none;
#                 border-bottom: 1px solid {Colors.BORDER};
#                 font-weight: {Fonts.MEDIUM};
#                 color: {Colors.TEXT_SECONDARY};
#             }}
#         """)
        
#         return table
    
#     def switch_view(self, mode):
#         """Change le mode d'affichage"""
#         self.current_mode = mode
        
#         # Mettre à jour les boutons
#         self.btn_tableau.setChecked(mode == self.MODE_TABLEAU)
#         self.btn_tableau.setStyleSheet(self._get_view_button_style(mode == self.MODE_TABLEAU))
#         self.btn_cartes.setChecked(mode == self.MODE_CARTES)
#         self.btn_cartes.setStyleSheet(self._get_view_button_style(mode == self.MODE_CARTES))
        
#         # Afficher/cacher les vues
#         self.table.setVisible(mode == self.MODE_TABLEAU)
#         self.cards_scroll.setVisible(mode == self.MODE_CARTES)
        
#         # Si on passe en mode cartes, les générer
#         if mode == self.MODE_CARTES:
#             self.display_cards()
    
#     def load_data(self):
#         """Charge les données"""
#         try:
#             self.sinistres = self.controller.sinistre.get_all() or []
#             self.filtered_sinistres = self.sinistres.copy()
#             self.display_data()
#             self.update_stats()
#         except Exception as e:
#             print(f"Erreur chargement sinistres: {e}")
#             self.sinistres = []
#             self.filtered_sinistres = []
#             self.display_data()
    
#     def display_data(self):
#         """Affiche les données dans le tableau"""
#         self.display_table()
#         if self.current_mode == self.MODE_CARTES:
#             self.display_cards()
    
#     def display_table(self):
#         """Affiche les données dans le tableau"""
#         self.table.setRowCount(len(self.filtered_sinistres))
        
#         for i, sinistre in enumerate(self.filtered_sinistres):
#             # N° dossier
#             self.table.setItem(i, 0, QTableWidgetItem(sinistre.numero_dossier))
            
#             # Type
#             type_item = QTableWidgetItem(sinistre.get_type_label())
#             type_item.setTextAlignment(Qt.AlignCenter)
#             self.table.setItem(i, 1, type_item)
            
#             # Véhicule
#             immat = sinistre.vehicule.immatriculation if sinistre.vehicule else "N/A"
#             self.table.setItem(i, 2, QTableWidgetItem(immat))
            
#             # Date
#             date_str = sinistre.date_survenue.strftime("%d/%m/%Y") if sinistre.date_survenue else ""
#             date_item = QTableWidgetItem(date_str)
#             date_item.setTextAlignment(Qt.AlignCenter)
#             self.table.setItem(i, 3, date_item)
            
#             # Statut avec couleur
#             statut_item = QTableWidgetItem(sinistre.statut.value)
#             statut_item.setForeground(self.get_statut_color(sinistre.statut))
#             statut_item.setTextAlignment(Qt.AlignCenter)
#             self.table.setItem(i, 4, statut_item)
            
#             # Montant
#             montant = f"{sinistre.estimation_preliminaire:,.0f} FCFA"
#             montant_item = QTableWidgetItem(montant)
#             montant_item.setTextAlignment(Qt.AlignRight)
#             self.table.setItem(i, 5, montant_item)
            
#             # Jours
#             jours_item = QTableWidgetItem(str(sinistre.jours_ecoules))
#             jours_item.setTextAlignment(Qt.AlignCenter)
#             self.table.setItem(i, 6, jours_item)
            
#             # Actions
#             actions_widget = QWidget()
#             actions_layout = QHBoxLayout(actions_widget)
#             actions_layout.setContentsMargins(4, 4, 4, 4)
#             actions_layout.setSpacing(4)
            
#             btn_view = QPushButton("👁️")
#             btn_view.setFixedSize(30, 30)
#             btn_view.setStyleSheet("border: none; background: transparent; font-size: 16px;")
#             btn_view.clicked.connect(lambda checked, s=sinistre: self.view_sinistre(s))
            
#             btn_edit = QPushButton("✏️")
#             btn_edit.setFixedSize(30, 30)
#             btn_edit.setStyleSheet("border: none; background: transparent; font-size: 16px;")
#             btn_edit.clicked.connect(lambda checked, s=sinistre: self.edit_sinistre(s))
            
#             actions_layout.addWidget(btn_view)
#             actions_layout.addWidget(btn_edit)
            
#             self.table.setCellWidget(i, 7, actions_widget)
    
#     # def display_cards(self):
#     #     """Affiche les données en mode cartes"""
#     #     # Vider le layout
#     #     self.clear_layout(self.cards_layout)
        
#     #     if not self.filtered_sinistres:
#     #         # Message si aucun sinistre
#     #         empty_label = QLabel("Aucun sinistre trouvé")
#     #         empty_label.setStyleSheet(f"""
#     #             font-size: {Fonts.H4}px;
#     #             color: {Colors.TEXT_MUTED};
#     #             padding: 40px;
#     #             text-align: center;
#     #         """)
#     #         empty_label.setAlignment(Qt.AlignCenter)
#     #         self.cards_layout.addWidget(empty_label, 0, 0)
#     #         return
        
#     #     # Calculer le nombre de colonnes
#     #     cols = 2
#     #     if self.width() > 1200:
#     #         cols = 3
        
#     #     for i, sinistre in enumerate(self.filtered_sinistres):
#     #         row = i // cols
#     #         col = i % cols
            
#     #         card = SinistreCard(
#     #             sinistre,
#     #             on_view=self.view_sinistre,
#     #             on_edit=self.edit_sinistre
#     #         )
#     #         self.cards_layout.addWidget(card, row, col)
       
#     def display_cards(self):
#         """Affiche les données en mode cartes"""
#         # Vider le layout
#         self.clear_layout(self.cards_layout)
        
#         if not self.filtered_sinistres:
#             # Message si aucun sinistre
#             empty_label = QLabel("Aucun sinistre trouvé")
#             empty_label.setStyleSheet(f"""
#                 font-size: {Fonts.H4}px;
#                 color: {Colors.TEXT_MUTED};
#                 padding: 40px;
#                 text-align: center;
#             """)
#             empty_label.setAlignment(Qt.AlignCenter)
#             self.cards_layout.addWidget(empty_label, 0, 0, 1, 5)  # ✅ 5 colonnes
#             return
        
#         # ✅ 5 COLONNES FIXES
#         cols = 5
        
#         # Calculer le nombre de lignes nécessaires
#         rows = (len(self.filtered_sinistres) + cols - 1) // cols
        
#         # Configurer les colonnes pour qu'elles s'étendent uniformément
#         for col in range(cols):
#             self.cards_layout.setColumnStretch(col, 1)
        
#         # Ajouter les cartes
#         for i, sinistre in enumerate(self.filtered_sinistres):
#             row = i // cols
#             col = i % cols
            
#             card = SinistreCard(
#                 sinistre,
#                 on_view=self.view_sinistre,
#                 on_edit=self.edit_sinistre
#             )
#             self.cards_layout.addWidget(card, row, col)
        
#         # ✅ Ajouter des espaces vides pour remplir la dernière ligne si nécessaire
#         remaining = len(self.filtered_sinistres) % cols
#         if remaining > 0:
#             last_row = rows - 1
#             for col in range(remaining, cols):
#                 spacer = QWidget()
#                 spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
#                 self.cards_layout.addWidget(spacer, last_row, col)

#     def clear_layout(self, layout):
#         """Vide un layout"""
#         while layout.count():
#             item = layout.takeAt(0)
#             if item.widget():
#                 item.widget().deleteLater()
    
#     def get_statut_color(self, statut):
#         """Retourne la couleur selon le statut"""
#         colors = {
#             StatutSinistre.DECLARE: QColor("#2563eb"),
#             StatutSinistre.EN_INSTRUCTION: QColor("#f59e0b"),
#             StatutSinistre.EN_ATTENTE: QColor("#f59e0b"),
#             StatutSinistre.EXPERTISE: QColor("#8b5cf6"),
#             StatutSinistre.VALIDE: QColor("#16a34a"),
#             StatutSinistre.REJETE: QColor("#dc2626"),
#             StatutSinistre.INDEMNISE: QColor("#16a34a"),
#             StatutSinistre.CLOS: QColor("#64748b"),
#         }
#         return colors.get(statut, QColor("#64748b"))
    
#     def update_stats(self):
#         """Met à jour les statistiques"""
#         try:
#             stats = self.controller.sinistre.get_stats() or {}
            
#             self.stats_cards["total"].setText(str(stats.get('total', 0)))
#             self.stats_cards["en_cours"].setText(str(stats.get('en_cours', 0)))
#             self.stats_cards["clos"].setText(str(stats.get('clos', 0)))
            
#             # Urgents : sinistres en cours depuis > 15 jours
#             urgents = sum(1 for s in self.filtered_sinistres if s.est_urgent)
#             self.stats_cards["urgent"].setText(str(urgents))
#         except Exception as e:
#             print(f"Erreur mise à jour stats: {e}")
    
#     def filter_data(self):
#         """Filtre les données affichées"""
#         search = self.search_input.text().lower()
#         statut = self.statut_filter.currentText()
#         type_ = self.type_filter.currentText()
        
#         self.filtered_sinistres = []
#         for s in self.sinistres:
#             if search and search not in s.numero_dossier.lower():
#                 continue
#             if statut != "Tous les statuts" and s.statut.value != statut:
#                 continue
#             if type_ != "Tous les types" and s.type.value != type_:
#                 continue
#             self.filtered_sinistres.append(s)
        
#         self.display_data()
#         self.update_stats()
    
#     def open_new_sinistre(self):
#         """Ouvre le formulaire de création"""
#         from addons.Automobiles.views.sinistre.sinistre_form_view import SinistreFormView
    
#         form = SinistreFormView(
#             controller=self.controller,
#             user=self.user,
#             parent=self
#         )
#         form.sinistre_saved.connect(self.on_sinistre_saved)
        
#         if form.exec() == QDialog.Accepted:
#             self.load_data()
#             self.update_stats()
    
#     def view_sinistre(self, sinistre):
#         """Affiche les détails d'un sinistre"""
#         from addons.Automobiles.views.sinistre.sinistre_detail_view import SinistreDetailView
#         detail = SinistreDetailView(self.controller, sinistre, self.user, parent=self)
#         detail.exec()
    
#     def on_sinistre_saved(self, sinistre):
#         """
#         Appelé quand un sinistre est sauvegardé
#         """
#         try:
#             self.load_data()
#             self.update_stats()
            
#             # Sélectionner le sinistre dans la liste
#             for row in range(self.table.rowCount()):
#                 item = self.table.item(row, 0)
#                 if item and item.text() == sinistre.numero_dossier:
#                     self.table.selectRow(row)
#                     break
                    
#         except Exception as e:
#             print(f"Erreur dans on_sinistre_saved: {e}")

#     def edit_sinistre(self, sinistre):
#         """Édite un sinistre"""
#         from addons.Automobiles.views.sinistre.sinistre_form_view import SinistreFormView
    
#         form = SinistreFormView(
#             controller=self.controller,
#             user=self.user,
#             sinistre=sinistre,
#             parent=self
#         )
#         form.sinistre_saved.connect(self.on_sinistre_saved)
        
#         if form.exec() == QDialog.Accepted:
#             self.load_data()
#             self.update_stats()
    
#     def resizeEvent(self, event):
#         """Gère le redimensionnement pour les cartes"""
#         super().resizeEvent(event)
#         if self.current_mode == self.MODE_CARTES:
#             self.display_cards()

# addons/Automobiles/views/sinistre/sinistre_list_view.py
"""
Vue de la liste des sinistres - Version optimisée
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QLineEdit, QFrame, QMessageBox, QScrollArea, QGridLayout,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QColor, QFont

from addons.Automobiles.views.style import Colors, Fonts, Spacing
from addons.Automobiles.views.sinistre.sinistre_card import SinistreCard
from addons.Automobiles.models.sinistre_models import StatutSinistre, TypeSinistre


class SinistreListView(QWidget):
    """Vue de la liste des sinistres avec mode tableau et mode cartes"""
    
    MODE_TABLEAU = "tableau"
    MODE_CARTES = "cartes"
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.current_mode = self.MODE_TABLEAU
        self.sinistres = []
        self.filtered_sinistres = []
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(Spacing.MD)  # ✅ Réduit
        layout.setContentsMargins(0, 0, 0, 0)
        
        # En-tête + Boutons (compact)
        header = self.setup_header()
        layout.addWidget(header)
        
        # Filtres (compact)
        filters = self.setup_filters()
        layout.addWidget(filters)
        
        # Statistiques (compact)
        self.stats_widget = self.setup_stats()
        layout.addWidget(self.stats_widget)
        
        # Zone de contenu
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(Spacing.SM)
        
        # Tableau
        self.table = self.setup_table()
        self.content_layout.addWidget(self.table)
        
        # Zone cartes
        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(Spacing.MD)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        
        # 5 colonnes
        for col in range(5):
            self.cards_layout.setColumnStretch(col, 1)
        
        self.cards_scroll.setWidget(self.cards_container)
        self.cards_scroll.setVisible(False)
        self.content_layout.addWidget(self.cards_scroll)
        
        layout.addWidget(self.content_frame, 1)
    
    def setup_header(self):
        """En-tête compact"""
        header = QFrame()
        header.setStyleSheet("background: transparent;")
        header.setFixedHeight(50)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(Spacing.MD)
        
        title = QLabel("📋 Gestion des Sinistres")
        title.setStyleSheet(f"""
            font-size: {Fonts.H3}px;
            font-weight: {Fonts.BOLD};
            color: {Colors.TEXT_PRIMARY};
        """)
        
        # Groupe de boutons
        btn_group = QWidget()
        btn_layout = QHBoxLayout(btn_group)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(Spacing.SM)
        
        self.btn_tableau = QPushButton("📊")
        self.btn_tableau.setCheckable(True)
        self.btn_tableau.setChecked(True)
        self.btn_tableau.setToolTip("Vue Tableau")
        self.btn_tableau.setFixedSize(36, 36)
        self.btn_tableau.setStyleSheet(self._get_icon_button_style(True))
        self.btn_tableau.clicked.connect(lambda: self.switch_view(self.MODE_TABLEAU))
        btn_layout.addWidget(self.btn_tableau)
        
        self.btn_cartes = QPushButton("📋")
        self.btn_cartes.setCheckable(True)
        self.btn_cartes.setToolTip("Vue Cartes")
        self.btn_cartes.setFixedSize(36, 36)
        self.btn_cartes.setStyleSheet(self._get_icon_button_style(False))
        self.btn_cartes.clicked.connect(lambda: self.switch_view(self.MODE_CARTES))
        btn_layout.addWidget(self.btn_cartes)
        
        btn_group.setFixedWidth(80)
        
        # Bouton Nouveau
        btn_new = QPushButton("+ Nouveau")
        btn_new.setFixedHeight(36)
        btn_new.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 18px;
                font-weight: {Fonts.MEDIUM};
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_DARK};
            }}
        """)
        btn_new.clicked.connect(self.open_new_sinistre)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(btn_group)
        header_layout.addWidget(btn_new)
        
        return header
    
    def _get_icon_button_style(self, is_active):
        """Style des boutons d'icônes"""
        if is_active:
            return f"""
                QPushButton {{
                    background-color: {Colors.PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: {Colors.PRIMARY_DARK};
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {Colors.GRAY_100};
                    color: {Colors.TEXT_SECONDARY};
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: {Colors.GRAY_200};
                }}
            """
    
    def setup_filters(self):
        """Barre de filtres compacte"""
        filters = QFrame()
        filters.setFixedHeight(44)
        filters.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
                padding: 0 12px;
            }}
        """)
        
        layout = QHBoxLayout(filters)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(Spacing.SM)
        
        # Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher...")
        self.search_input.textChanged.connect(self.filter_data)
        self.search_input.setFixedHeight(32)
        self.search_input.setStyleSheet(self._get_input_style())
        layout.addWidget(self.search_input, 2)
        
        # Filtre statut
        self.statut_filter = QComboBox()
        self.statut_filter.addItem("Tous les statuts")
        for statut in StatutSinistre:
            self.statut_filter.addItem(statut.value)
        self.statut_filter.currentTextChanged.connect(self.filter_data)
        self.statut_filter.setFixedHeight(32)
        self.statut_filter.setStyleSheet(self._get_combo_style())
        layout.addWidget(self.statut_filter, 1)
        
        # Filtre type
        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous les types")
        for type_ in TypeSinistre:
            self.type_filter.addItem(type_.value)
        self.type_filter.currentTextChanged.connect(self.filter_data)
        self.type_filter.setFixedHeight(32)
        self.type_filter.setStyleSheet(self._get_combo_style())
        layout.addWidget(self.type_filter, 1)
        
        # Bouton Rafraîchir
        btn_refresh = QPushButton("🔄")
        btn_refresh.setFixedSize(32, 32)
        btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GRAY_100};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {Colors.GRAY_200};
            }}
        """)
        btn_refresh.clicked.connect(self.load_data)
        layout.addWidget(btn_refresh)
        
        return filters
    
    def _get_input_style(self):
        """Style des champs de saisie"""
        return f"""
            QLineEdit {{
                border: 1px solid {Colors.BORDER};
                border-radius: 6px;
                padding: 4px 10px;
                background-color: {Colors.WHITE};
                color: {Colors.TEXT_PRIMARY};
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {Colors.PRIMARY};
            }}
        """
    
    def _get_combo_style(self):
        """Style des QComboBox"""
        return f"""
            QComboBox {{
                border: 1px solid {Colors.BORDER};
                border-radius: 6px;
                padding: 4px 10px;
                background-color: {Colors.WHITE};
                color: {Colors.TEXT_PRIMARY};
                font-size: 12px;
                min-width: 100px;
            }}
            QComboBox:focus {{
                border-color: {Colors.PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {Colors.BORDER};
                border-radius: 6px;
                background-color: {Colors.WHITE};
                selection-background-color: {Colors.PRIMARY}20;
                padding: 4px;
            }}
        """
    
    def setup_stats(self):
        """Cartes de statistiques compactes"""
        stats = QFrame()
        stats.setFixedHeight(60)
        stats.setStyleSheet("background: transparent;")
        
        stats_layout = QHBoxLayout(stats)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(Spacing.SM)
        
        self.stats_cards = {}
        stat_items = [
            ("total", "Total", "0", "#2563eb"),
            ("en_cours", "En cours", "0", "#f59e0b"),
            ("clos", "Clos", "0", "#16a34a"),
            ("urgent", "Urgents", "0", "#dc2626"),
        ]
        
        for key, title, value, color in stat_items:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {Colors.WHITE};
                    border: 1px solid {Colors.BORDER};
                    border-radius: 8px;
                    padding: 4px 16px;
                }}
            """)
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(8, 4, 8, 4)
            card_layout.setSpacing(8)
            
            label_value = QLabel(value)
            label_value.setStyleSheet(f"""
                font-size: {Fonts.H2}px;
                font-weight: {Fonts.BOLD};
                color: {color};
            """)
            card_layout.addWidget(label_value)
            
            label_title = QLabel(title)
            label_title.setStyleSheet(f"""
                font-size: 11px;
                color: {Colors.TEXT_SECONDARY};
            """)
            card_layout.addWidget(label_title)
            
            card_layout.addStretch()
            
            stats_layout.addWidget(card)
            self.stats_cards[key] = label_value
        
        stats_layout.addStretch()
        
        return stats
    
    def setup_table(self):
        """Tableau optimisé"""
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "N° Dossier", "Type", "Véhicule", "Date", "Statut", "Montant", "Jours", "Actions"
        ])
        
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setDefaultSectionSize(38)
        
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Colors.WHITE};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
                gridline-color: {Colors.BORDER};
            }}
            QTableWidget::item {{
                padding: 4px 8px;
                font-size: 12px;
            }}
            QTableWidget::item:selected {{
                background-color: {Colors.PRIMARY}15;
            }}
            QHeaderView::section {{
                background-color: {Colors.GRAY_50};
                padding: 4px 8px;
                border: none;
                border-bottom: 1px solid {Colors.BORDER};
                font-weight: {Fonts.MEDIUM};
                font-size: 11px;
                color: {Colors.TEXT_SECONDARY};
            }}
        """)
        
        return table
    
    def switch_view(self, mode):
        """Change le mode d'affichage"""
        self.current_mode = mode
        
        self.btn_tableau.setChecked(mode == self.MODE_TABLEAU)
        self.btn_tableau.setStyleSheet(self._get_icon_button_style(mode == self.MODE_TABLEAU))
        self.btn_cartes.setChecked(mode == self.MODE_CARTES)
        self.btn_cartes.setStyleSheet(self._get_icon_button_style(mode == self.MODE_CARTES))
        
        self.table.setVisible(mode == self.MODE_TABLEAU)
        self.cards_scroll.setVisible(mode == self.MODE_CARTES)
        
        if mode == self.MODE_CARTES:
            self.display_cards()
    
    def load_data(self):
        """Charge les données"""
        try:
            self.sinistres = self.controller.sinistre.get_all() or []
            self.filtered_sinistres = self.sinistres.copy()
            self.display_data()
            self.update_stats()
        except Exception as e:
            print(f"Erreur chargement sinistres: {e}")
            self.sinistres = []
            self.filtered_sinistres = []
            self.display_data()
    
    def display_data(self):
        """Affiche les données"""
        self.display_table()
        if self.current_mode == self.MODE_CARTES:
            self.display_cards()
    
    def display_table(self):
        """Affiche les données dans le tableau"""
        self.table.setRowCount(len(self.filtered_sinistres))
        
        for i, sinistre in enumerate(self.filtered_sinistres):
            self.table.setItem(i, 0, QTableWidgetItem(sinistre.numero_dossier))
            
            type_item = QTableWidgetItem(sinistre.get_type_label())
            type_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, type_item)
            
            immat = sinistre.vehicule.immatriculation if sinistre.vehicule else "N/A"
            self.table.setItem(i, 2, QTableWidgetItem(immat))
            
            date_str = sinistre.date_survenue.strftime("%d/%m/%Y") if sinistre.date_survenue else ""
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, date_item)
            
            statut_item = QTableWidgetItem(sinistre.statut.value)
            statut_item.setForeground(self.get_statut_color(sinistre.statut))
            statut_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, statut_item)
            
            montant = f"{sinistre.estimation_preliminaire:,.0f} FCFA"
            montant_item = QTableWidgetItem(montant)
            montant_item.setTextAlignment(Qt.AlignRight)
            self.table.setItem(i, 5, montant_item)
            
            jours_item = QTableWidgetItem(str(sinistre.jours_ecoules))
            jours_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 6, jours_item)
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            btn_view = QPushButton("👁️")
            btn_view.setFixedSize(26, 26)
            btn_view.setStyleSheet("border: none; background: transparent; font-size: 14px;")
            btn_view.clicked.connect(lambda checked, s=sinistre: self.view_sinistre(s))
            
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(26, 26)
            btn_edit.setStyleSheet("border: none; background: transparent; font-size: 14px;")
            btn_edit.clicked.connect(lambda checked, s=sinistre: self.edit_sinistre(s))
            
            actions_layout.addWidget(btn_view)
            actions_layout.addWidget(btn_edit)
            
            self.table.setCellWidget(i, 7, actions_widget)
    
    def display_cards(self):
        """Affiche les données en mode cartes"""
        self.clear_layout(self.cards_layout)
        
        if not self.filtered_sinistres:
            empty_label = QLabel("Aucun sinistre trouvé")
            empty_label.setStyleSheet(f"""
                font-size: {Fonts.H4}px;
                color: {Colors.TEXT_MUTED};
                padding: 40px;
            """)
            empty_label.setAlignment(Qt.AlignCenter)
            self.cards_layout.addWidget(empty_label, 0, 0, 1, 5)
            return
        
        cols = 5
        rows = (len(self.filtered_sinistres) + cols - 1) // cols
        
        for col in range(cols):
            self.cards_layout.setColumnStretch(col, 1)
        
        for i, sinistre in enumerate(self.filtered_sinistres):
            row = i // cols
            col = i % cols
            
            card = SinistreCard(
                sinistre,
                on_view=self.view_sinistre,
                on_edit=self.edit_sinistre
            )
            self.cards_layout.addWidget(card, row, col)
        
        remaining = len(self.filtered_sinistres) % cols
        if remaining > 0 and rows > 0:
            last_row = rows - 1
            for col in range(remaining, cols):
                spacer = QWidget()
                spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                self.cards_layout.addWidget(spacer, last_row, col)
    
    def clear_layout(self, layout):
        """Vide un layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def get_statut_color(self, statut):
        """Retourne la couleur selon le statut"""
        colors = {
            StatutSinistre.DECLARE: QColor("#2563eb"),
            StatutSinistre.EN_INSTRUCTION: QColor("#f59e0b"),
            StatutSinistre.EN_ATTENTE: QColor("#f59e0b"),
            StatutSinistre.EXPERTISE: QColor("#8b5cf6"),
            StatutSinistre.VALIDE: QColor("#16a34a"),
            StatutSinistre.REJETE: QColor("#dc2626"),
            StatutSinistre.INDEMNISE: QColor("#16a34a"),
            StatutSinistre.CLOS: QColor("#64748b"),
        }
        return colors.get(statut, QColor("#64748b"))
    
    def update_stats(self):
        """Met à jour les statistiques"""
        try:
            stats = self.controller.sinistre.get_stats() or {}
            
            self.stats_cards["total"].setText(str(stats.get('total', 0)))
            self.stats_cards["en_cours"].setText(str(stats.get('en_cours', 0)))
            self.stats_cards["clos"].setText(str(stats.get('clos', 0)))
            
            urgents = sum(1 for s in self.filtered_sinistres if s.est_urgent)
            self.stats_cards["urgent"].setText(str(urgents))
        except Exception as e:
            print(f"Erreur mise à jour stats: {e}")
    
    def filter_data(self):
        """Filtre les données affichées"""
        search = self.search_input.text().lower()
        statut = self.statut_filter.currentText()
        type_ = self.type_filter.currentText()
        
        self.filtered_sinistres = []
        for s in self.sinistres:
            if search and search not in s.numero_dossier.lower():
                continue
            if statut != "Tous les statuts" and s.statut.value != statut:
                continue
            if type_ != "Tous les types" and s.type.value != type_:
                continue
            self.filtered_sinistres.append(s)
        
        self.display_data()
        self.update_stats()
    
    def open_new_sinistre(self):
        """Ouvre le formulaire de création"""
        from addons.Automobiles.views.sinistre.sinistre_form_view import SinistreFormView
    
        form = SinistreFormView(
            controller=self.controller,
            user=self.user,
            parent=self
        )
        form.sinistre_saved.connect(self.on_sinistre_saved)
        
        if form.exec() == QDialog.Accepted:
            self.load_data()
            self.update_stats()
    
    def view_sinistre(self, sinistre):
        """Affiche les détails d'un sinistre"""
        from addons.Automobiles.views.sinistre.sinistre_detail_view import SinistreDetailView
        detail = SinistreDetailView(self.controller, sinistre, self.user, parent=self)
        detail.exec()
    
    def on_sinistre_saved(self, sinistre):
        """Appelé quand un sinistre est sauvegardé"""
        try:
            self.load_data()
            self.update_stats()
            
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.text() == sinistre.numero_dossier:
                    self.table.selectRow(row)
                    break
        except Exception as e:
            print(f"Erreur dans on_sinistre_saved: {e}")

    def edit_sinistre(self, sinistre):
        """Édite un sinistre"""
        from addons.Automobiles.views.sinistre.sinistre_form_view import SinistreFormView
    
        form = SinistreFormView(
            controller=self.controller,
            user=self.user,
            sinistre=sinistre,
            parent=self
        )
        form.sinistre_saved.connect(self.on_sinistre_saved)
        
        if form.exec() == QDialog.Accepted:
            self.load_data()
            self.update_stats()
    
    def resizeEvent(self, event):
        """Gère le redimensionnement"""
        super().resizeEvent(event)
        if self.current_mode == self.MODE_CARTES:
            self.display_cards()