"""
Widget Recent Claims avec :
- 2 modes d'affichage (Cartes / Tableau)
- Scroll vertical
- Hauteur extensible
- Compteur + bouton Voir tout
- Menu contextuel sur chaque ligne
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QGridLayout, QMenu, QButtonGroup, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtGui import QAction, QColor

from typing import List, Dict, Optional


# Modes d'affichage
MODE_CARDS = "cards"
MODE_TABLE = "table"


class RecentClaimsWidget(QWidget):
    """Widget Recent Claims avec 2 modes d'affichage"""
    
    # Signaux émis vers le parent
    view_detail_requested = Signal(dict)
    modify_requested = Signal(dict)
    print_requested = Signal(dict)
    view_all_requested = Signal()
    
    def __init__(self, statut_colors: dict, parent=None):
        super().__init__(parent)
        
        self.statut_colors = statut_colors
        self._sinistres = []
        
        # Préférence utilisateur pour le mode
        self._settings = QSettings("LOMETA", "Dashboard")
        self._current_mode = self._settings.value("recent_claims_mode", MODE_TABLE)
        
        self.setup_ui()
    
    # ============================================================
    # UI
    # ============================================================
    
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)
        
        # ============================================================
        # Barre supérieure : compteur + toggle + voir tout
        # ============================================================
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        # ✅ Barre de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔎 Rechercher un sinistre...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 11px;
                color: #1e293b;
                min-width: 180px;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                background-color: white;
            }
        """)
        self.search_input.textChanged.connect(self._filtrer)
        top_bar.addWidget(self.search_input, 1)

        # Compteur
        self.lbl_count = QLabel("0 sinistre(s)")
        self.lbl_count.setStyleSheet("""
            font-size: 10px;
            color: #64748b;
            font-weight: 500;
        """)
        top_bar.addWidget(self.lbl_count)
        
        # Compteur
        self.lbl_count = QLabel("0 sinistre(s) récent(s)")
        self.lbl_count.setStyleSheet("""
            font-size: 11px;
            color: #64748b;
            font-weight: 500;
        """)
        top_bar.addWidget(self.lbl_count)
        
        top_bar.addStretch()
        
        # Toggle mode
        toggle_frame = QFrame()
        toggle_frame.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border-radius: 8px;
                padding: 2px;
            }
        """)
        toggle_layout = QHBoxLayout(toggle_frame)
        toggle_layout.setContentsMargins(3, 3, 3, 3)
        toggle_layout.setSpacing(2)
        
        self.btn_mode_cards = QPushButton("🔲")
        self.btn_mode_table = QPushButton("📋")
        
        for btn, mode, tooltip in [
            (self.btn_mode_cards, MODE_CARDS, "Affichage en cartes"),
            (self.btn_mode_table, MODE_TABLE, "Affichage en tableau"),
        ]:
            btn.setCheckable(True)
            btn.setFixedSize(28, 28)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    color: #64748b;
                }
                QPushButton:hover {
                    background-color: #e2e8f0;
                }
                QPushButton:checked {
                    background-color: white;
                    color: #1a73e8;
                }
            """)
            btn.clicked.connect(lambda checked=False, m=mode: self._switch_mode(m))
            toggle_layout.addWidget(btn)
        
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        self.mode_group.addButton(self.btn_mode_cards)
        self.mode_group.addButton(self.btn_mode_table)
        
        top_bar.addWidget(toggle_frame)
        
        # Bouton "Voir tout"
        self.btn_view_all = QPushButton("Voir tout →")
        self.btn_view_all.setCursor(Qt.PointingHandCursor)
        self.btn_view_all.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1a73e8;
                border: none;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.btn_view_all.clicked.connect(self.view_all_requested.emit)
        top_bar.addWidget(self.btn_view_all)
        
        root.addLayout(top_bar)
        
        # ============================================================
        # Zone d'affichage (2 conteneurs superposés)
        # ============================================================
        self.content_stack = QWidget()
        stack_layout = QVBoxLayout(self.content_stack)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.setSpacing(0)
        
        # Mode Tableau
        self.table_container = self._build_table_container()
        stack_layout.addWidget(self.table_container)
        
        # Mode Cartes
        self.cards_container = self._build_cards_container()
        stack_layout.addWidget(self.cards_container)
        
        root.addWidget(self.content_stack, 1)
        
        # Appliquer le mode courant
        self._apply_mode()
    
    # ============================================================
    # MODE TABLEAU
    # ============================================================
    
    def _build_table_container(self) -> QWidget:
        """Construit le conteneur du tableau"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "N° Sinistre", "Client", "Branche", "Date", "Statut", "Montant"
        ])
        
        # Configuration des colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.setShowGrid(False)
        
        # ✅ Scroll vertical
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # ✅ Hauteur extensible
        self.table.setMinimumHeight(300)
        self.table.setSizePolicy(
            self.table.sizePolicy().horizontalPolicy(),
            self.table.sizePolicy().verticalPolicy()
        )
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                gridline-color: #f1f5f9;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 4px 6px;
                border-bottom: 1px solid #f8fafc;
            }
            QTableWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 6px;
                font-weight: bold;
                font-size: 10px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Menu contextuel
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.doubleClicked.connect(self._on_row_double_clicked)
        
        layout.addWidget(self.table)
        return container
    
    # ============================================================
    # MODE CARTES
    # ============================================================
    
    def _build_cards_container(self) -> QWidget:
        """Construit le conteneur des cartes"""
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        scroll.setMinimumHeight(300)
        
        # Conteneur des cartes
        self.cards_content = QWidget()
        self.cards_content.setStyleSheet("background-color: transparent;")
        
        self.cards_grid = QGridLayout(self.cards_content)
        self.cards_grid.setContentsMargins(2, 2, 2, 2)
        self.cards_grid.setSpacing(10)
        
        scroll.setWidget(self.cards_content)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
        return container
    
    # ============================================================
    # CHANGEMENT DE MODE
    # ============================================================
    
    def _switch_mode(self, mode: str):
        """Change le mode d'affichage"""
        if mode == self._current_mode:
            return
        
        self._current_mode = mode
        self._settings.setValue("recent_claims_mode", mode)
        self._apply_mode()
    
    def _apply_mode(self):
        """Applique le mode courant"""
        if self._current_mode == MODE_CARDS:
            self.btn_mode_cards.setChecked(True)
            self.table_container.hide()
            self.cards_container.show()
        else:
            self.btn_mode_table.setChecked(True)
            self.table_container.show()
            self.cards_container.hide()
    
    # ============================================================
    # MISE À JOUR DES DONNÉES
    # ============================================================
    
    def set_sinistres(self, sinistres: List[Dict]):
        """Met à jour la liste des sinistres"""
        self._sinistres = sinistres or []

        # ✅ Réinitialiser la recherche
        if hasattr(self, 'search_input'):
            self.search_input.blockSignals(True)
            self.search_input.clear()
            self.search_input.blockSignals(False)

        # Compteur
        self.lbl_count.setText(f"{len(self._sinistres)} sinistre(s)")

        # Mettre à jour les deux vues
        self._update_table(self._sinistres)
        self._update_cards(self._sinistres)
    
    def _update_table(self, sinistres: List[Dict]):
        """Met à jour le tableau"""
        # Limiter à 20 pour ne pas surcharger
        recents = sinistres[:20]
        self.table.setRowCount(len(recents))
        
        for i, s in enumerate(recents):
            # N°
            self.table.setItem(i, 0, QTableWidgetItem(s.get('numero_sinistre', '')))
            
            # Client
            self.table.setItem(i, 1, QTableWidgetItem(s.get('client_nom', '—')))
            
            # Branche
            self.table.setItem(i, 2, QTableWidgetItem(s.get('branche', '')))
            
            # Date
            date_str = (s.get('date_survenance') or s.get('date_declaration') or '')[:10]
            self.table.setItem(i, 3, QTableWidgetItem(date_str))
            
            # Statut
            statut = s.get('statut', '')
            statut_item = QTableWidgetItem(statut)

            # ✅ Récupérer la couleur (fallback si statut inconnu)
            color_hex = self.statut_colors.get(statut, '#64748b')

            # ✅ Appliquer la couleur de fond
            statut_item.setBackground(QColor(color_hex))
            statut_item.setForeground(QColor('white'))

            # ✅ Centrer le texte
            statut_item.setTextAlignment(Qt.AlignCenter)

            # ✅ Optionnel : rendre le texte en gras
            font = statut_item.font()
            font.setBold(True)
            statut_item.setFont(font)

            self.table.setItem(i, 4, statut_item)
            
            # Montant
            montant = s.get('montant_net', 0) or 0
            montant_item = QTableWidgetItem(f"{montant:,.0f}".replace(",", " "))
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 5, montant_item)
    
    def _update_cards(self, sinistres: List[Dict]):
        """Met à jour les cartes"""
        from addons.sinistres.views.widgets.recent_claim_card import RecentClaimCard
        
        # Vider la grille
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not sinistres:
            empty = QLabel("Aucun sinistre récent")
            empty.setStyleSheet("""
                color: #94a3b8;
                font-size: 12px;
                font-style: italic;
                padding: 30px;
            """)
            empty.setAlignment(Qt.AlignCenter)
            self.cards_grid.addWidget(empty, 0, 0, 1, 2)
            return
        
        # Limiter à 20
        recents = sinistres[:20]
        
        for i, s in enumerate(recents):
            card = RecentClaimCard(s, self.statut_colors)
            card.clicked.connect(self._on_card_clicked)
            card.setContextMenuPolicy(Qt.CustomContextMenu)
            card.customContextMenuRequested.connect(
                lambda pos, sin=s, w=card: self._show_card_context_menu(pos, sin, w)
            )
            
            row = i // 2
            col = i % 2
            self.cards_grid.addWidget(card, row, col)
        
        # Stretch à la fin
        self.cards_grid.setRowStretch(self.cards_grid.rowCount(), 1)
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def _on_row_double_clicked(self, index):
        """Double-clic sur une ligne du tableau"""
        row = index.row()
        if 0 <= row < len(self._sinistres):
            self.view_detail_requested.emit(self._sinistres[row])
    
    def _on_card_clicked(self, sinistre: dict):
        """Clic sur une carte"""
        self.view_detail_requested.emit(sinistre)
    
    def _show_context_menu(self, position):
        """Menu contextuel sur le tableau"""
        row = self.table.currentRow()
        if row < 0 or row >= len(self._sinistres):
            return
        
        sinistre = self._sinistres[row]
        self._build_context_menu(sinistre, self.table.viewport().mapToGlobal(position))
    
    def _show_card_context_menu(self, position, sinistre: dict, widget):
        """Menu contextuel sur une carte"""
        self._build_context_menu(sinistre, widget.mapToGlobal(position))
    
    def _build_context_menu(self, sinistre: dict, global_pos):
        """Construit le menu contextuel commun"""
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
        
        statut = sinistre.get('statut', '')
        
        # Voir détail
        action_detail = QAction("👁️  Voir le détail", self)
        action_detail.triggered.connect(lambda: self.view_detail_requested.emit(sinistre))
        menu.addAction(action_detail)
        
        # Modifier
        action_modifier = QAction("✏️  Modifier", self)
        action_modifier.setEnabled(statut != 'CLOTURE')
        action_modifier.triggered.connect(lambda: self.modify_requested.emit(sinistre))
        menu.addAction(action_modifier)
        
        menu.addSeparator()
        
        # Imprimer
        action_imprimer = QAction("🖨️  Imprimer", self)
        action_imprimer.triggered.connect(lambda: self.print_requested.emit(sinistre))
        menu.addAction(action_imprimer)
        
        menu.exec(global_pos)

    def _filtrer(self):
        """Filtre la liste selon le texte de recherche"""
        text = self.search_input.text().strip().lower()
        
        if not text:
            # Réinitialiser
            self._update_table(self._sinistres)
            self._update_cards(self._sinistres)
            self.lbl_count.setText(f"{len(self._sinistres)} sinistre(s)")
            return
        
        # Filtrer
        filtered = []
        for s in self._sinistres:
            # Recherche dans plusieurs champs
            champs = [
                s.get('numero_sinistre', ''),
                s.get('client_nom', ''),
                s.get('branche', ''),
                s.get('statut', ''),
                s.get('categorie', ''),
                s.get('numero_reference', ''),
            ]
            
            if any(text in str(champ).lower() for champ in champs):
                filtered.append(s)
        
        # Mettre à jour les vues
        self._update_table(filtered)
        self._update_cards(filtered)
        
        # Mettre à jour le compteur
        self.lbl_count.setText(f"{len(filtered)} / {len(self._sinistres)}")