"""
Page de gestion des lots de paiement - Version moderne
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QComboBox, QMessageBox, QFrame,
    QScrollArea, QGridLayout, QLineEdit, QMenu, QDateEdit
)
from PySide6.QtCore import Qt, Signal, QPointF, QDate
from PySide6.QtGui import QColor, QAction

from typing import List
from datetime import datetime

from addons.sinistres.views.lot_detail_dialog import LotDetailDialog


# ============================================================
# COULEURS DES STATUTS
# ============================================================

LOT_STATUT_COLORS = {
    'OUVERT': ('#fef3c7', '#92400e'),        # Ambre
    'VALIDE': ('#dbeafe', '#1e40af'),        # Bleu
    'TRAITE': ('#cffafe', '#155e75'),        # Cyan
    'COMPTABILISE': ('#dcfce7', '#166534'),  # Vert
    'ANNULE': ('#fee2e2', '#991b1b'),        # Rouge
}


# ============================================================
# WIDGET : CARTE LOT
# ============================================================

class LotCard(QFrame):
    """Carte d'un lot de paiement"""
    
    view_requested = Signal(dict)
    validate_requested = Signal(dict)
    process_requested = Signal(dict)
    accounting_requested = Signal(dict)
    context_menu_requested = Signal(dict, QPointF)
    
    def __init__(self, lot: dict, parent=None):
        super().__init__(parent)
        self.lot = lot
        self.setFixedWidth(380)
        self.setMinimumHeight(260)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        
        self.setStyleSheet("""
            LotCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            LotCard:hover {
                border: 1px solid #cbd5e1;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)
        
        # ============================================================
        # HEADER
        # ============================================================
        header = QHBoxLayout()
        header.setSpacing(12)
        
        # Icône
        icon = QLabel("📦")
        icon.setFixedSize(48, 48)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("""
            background-color: #e8f0fe;
            border-radius: 10px;
            font-size: 22px;
        """)
        header.addWidget(icon)
        
        # Infos principales
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        numero = QLabel(lot.get('numero_lot', 'N/A'))
        numero.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b;")
        info_layout.addWidget(numero)
        
        date_creation = lot.get('date_creation', '')[:10] if lot.get('date_creation') else '—'
        date_lbl = QLabel(f"📅 {date_creation}")
        date_lbl.setStyleSheet("font-size: 10px; color: #64748b;")
        info_layout.addWidget(date_lbl)
        
        header.addLayout(info_layout, 1)
        
        # Statut badge
        statut = lot.get('statut', 'OUVERT')
        bg, fg = LOT_STATUT_COLORS.get(statut, ('#f1f5f9', '#64748b'))
        
        statut_lbl = QLabel(statut)
        statut_lbl.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            padding: 4px 10px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        """)
        statut_lbl.setAlignment(Qt.AlignCenter)
        header.addWidget(statut_lbl)
        
        layout.addLayout(header)
        
        # ============================================================
        # MONTANT
        # ============================================================
        montant_layout = QVBoxLayout()
        montant_layout.setSpacing(2)
        
        montant_lbl = QLabel("Montant total")
        montant_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        montant_layout.addWidget(montant_lbl)
        
        montant = lot.get('montant_total', 0)
        montant_val = QLabel(f"{montant:,.0f} FCFA")
        montant_val.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a73e8;")
        montant_layout.addWidget(montant_val)
        
        layout.addLayout(montant_layout)
        
        # ============================================================
        # NB PAIEMENTS + TYPE
        # ============================================================
        details_row = QHBoxLayout()
        
        nb_layout = QVBoxLayout()
        nb_layout.setSpacing(2)
        nb_lbl = QLabel("Paiements")
        nb_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        nb_layout.addWidget(nb_lbl)
        nb_val = QLabel(f"{lot.get('nombre_paiements', 0)} règlements")
        nb_val.setStyleSheet("font-size: 12px; color: #1e293b;")
        nb_layout.addWidget(nb_val)
        details_row.addLayout(nb_layout, 1)
        
        type_layout = QVBoxLayout()
        type_layout.setSpacing(2)
        type_lbl = QLabel("Type")
        type_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        type_layout.addWidget(type_lbl)
        type_val = QLabel(lot.get('type_lot', '—'))
        type_val.setStyleSheet("font-size: 12px; color: #1e293b;")
        type_layout.addWidget(type_val)
        details_row.addLayout(type_layout, 1)
        
        layout.addLayout(details_row)
        
        # ============================================================
        # BOUTONS D'ACTION
        # ============================================================
        actions = QHBoxLayout()
        actions.setSpacing(6)
        
        # Bouton Voir
        btn_view = QPushButton("👁️ Voir")
        btn_view.setStyleSheet(self._small_btn_style())
        btn_view.setCursor(Qt.PointingHandCursor)
        btn_view.clicked.connect(lambda: self.view_requested.emit(self.lot))
        actions.addWidget(btn_view)
        
        # Bouton d'action selon statut
        if statut == "OUVERT":
            btn_action = QPushButton("✅ Valider")
            btn_action.setStyleSheet(self._action_btn_style("#1a73e8"))
            btn_action.clicked.connect(lambda: self.validate_requested.emit(self.lot))
            actions.addWidget(btn_action)
        
        elif statut == "VALIDE":
            btn_action = QPushButton("▶️ Traiter")
            btn_action.setStyleSheet(self._action_btn_style("#8b5cf6"))
            btn_action.clicked.connect(lambda: self.process_requested.emit(self.lot))
            actions.addWidget(btn_action)
        
        elif statut == "TRAITE":
            btn_action = QPushButton("📊 Comptabiliser")
            btn_action.setStyleSheet(self._action_btn_style("#22c55e"))
            btn_action.clicked.connect(lambda: self.accounting_requested.emit(self.lot))
            actions.addWidget(btn_action)
        
        actions.addStretch()
        layout.addLayout(actions)
    
    def _small_btn_style(self):
        return """
            QPushButton {
                background-color: #f1f5f9;
                color: #64748b;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 11px;
                border: none;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """
    
    def _action_btn_style(self, color: str):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 6px 14px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 11px;
                border: none;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """
    
    def _on_context_menu(self, pos):
        self.context_menu_requested.emit(self.lot, self.mapToGlobal(pos))


# ============================================================
# PAGE : LOTS DE PAIEMENT
# ============================================================

class LotsPage(QWidget):
    """Page de gestion des lots de paiement - Style moderne"""
    
    def __init__(self, controller, user, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self._lots = []
        self._filtered_lots = []
        self._view_mode = "tableau"
        self._current_page = 1
        self._per_page = 20
        
        # Permissions
        from addons.sinistres.services.permission_service import PermissionService
        from addons.sinistres.security.permissions_helper import PermissionsUI
        self._perm_ui = PermissionsUI(user, PermissionService())
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
        """)
        
        content = QWidget()
        content.setStyleSheet("background-color: #f8fafc;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # ============================================================
        # LIGNE 1 : KPI CARDS (3 cards)
        # ============================================================
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)
        
        self.kpi_total = self._make_kpi_card(
            "📦", "0", "Total de Lots", "Lots cumulés", "#3b82f6"
        )
        kpi_row.addWidget(self.kpi_total)
        
        self.kpi_montant = self._make_kpi_card(
            "💰", "0 FCFA", "Montant Total Traité", "Cumul tous lots", "#22c55e"
        )
        kpi_row.addWidget(self.kpi_montant)
        
        self.kpi_attente = self._make_kpi_card(
            "⏳", "0", "Lots en Attente", "OUVERT + VALIDÉ", "#f59e0b"
        )
        kpi_row.addWidget(self.kpi_attente)
        
        layout.addLayout(kpi_row)
        
        # ============================================================
        # LIGNE 2 : BARRE D'OUTILS
        # ============================================================
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(12, 10, 12, 10)
        tb_layout.setSpacing(8)
        
        # Bouton Nouveau lot
        self.btn_nouveau = QPushButton("➕  Nouveau lot")
        self.btn_nouveau.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover { background-color: #1557b0; }
        """)
        self.btn_nouveau.setCursor(Qt.PointingHandCursor)
        self.btn_nouveau.clicked.connect(self.ouvrir_dialogue_creation)
        if not self._perm_ui.peut('reglement', 'CREATE'):
            self.btn_nouveau.hide()
        tb_layout.addWidget(self.btn_nouveau)
        
        # Rafraîchir
        self.btn_refresh = QPushButton("🔄  Rafraîchir")
        self.btn_refresh.setStyleSheet(self._toolbar_btn_style())
        self.btn_refresh.clicked.connect(self.load_data)
        tb_layout.addWidget(self.btn_refresh)
        
        # Exporter
        self.btn_export = QPushButton("⬇️  Exporter (CSV)")
        self.btn_export.setStyleSheet(self._toolbar_btn_style())
        self.btn_export.clicked.connect(self.exporter_csv)
        tb_layout.addWidget(self.btn_export)
        
        # Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Recherche...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                min-width: 180px;
            }
            QLineEdit:focus { border: 2px solid #1a73e8; }
        """)
        self.search_input.textChanged.connect(self._apply_filters)
        tb_layout.addWidget(self.search_input, 1)
        
        # Filtre Statut
        self.filter_statut = QComboBox()
        self.filter_statut.addItem("Statut", None)
        self.filter_statut.addItem("Ouvert", "OUVERT")
        self.filter_statut.addItem("Validé", "VALIDE")
        self.filter_statut.addItem("Traité", "TRAITE")
        self.filter_statut.addItem("Comptabilisé", "COMPTABILISE")
        self.filter_statut.setStyleSheet(self._combo_style())
        self.filter_statut.currentIndexChanged.connect(self._apply_filters)
        tb_layout.addWidget(self.filter_statut)
        
        # Vue Tableau
        self.btn_view_table = QPushButton("⊞  TABLEAU")
        self.btn_view_table.setCheckable(True)
        self.btn_view_table.setChecked(True)
        self.btn_view_table.setStyleSheet(self._view_btn_style())
        self.btn_view_table.clicked.connect(lambda: self._set_view_mode("tableau"))
        tb_layout.addWidget(self.btn_view_table)
        
        # Vue Carte
        self.btn_view_card = QPushButton("🗺  CARTE")
        self.btn_view_card.setCheckable(True)
        self.btn_view_card.setStyleSheet(self._view_btn_style())
        self.btn_view_card.clicked.connect(lambda: self._set_view_mode("carte"))
        tb_layout.addWidget(self.btn_view_card)
        
        layout.addWidget(toolbar)
        
        # ============================================================
        # LIGNE 3 : CONTENU (tableau OU cartes)
        # ============================================================
        self.view_container = QWidget()
        self.view_layout = QVBoxLayout(self.view_container)
        self.view_layout.setContentsMargins(0, 0, 0, 0)
        self.view_layout.setSpacing(12)
        
        # --- Vue TABLEAU ---
        # --- Vue TABLEAU ---
        self.table_container = QFrame()
        self.table_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        tc_layout = QVBoxLayout(self.table_container)
        tc_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "N° Lot", "Date création", "Nombre paiements", "Montant total",
            "Type", "Statut", "Actions"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        
        # ✅ HAUTEUR MINIMALE AUGMENTÉE
        self.table.setMinimumHeight(500)
        
        # ✅ Politique de taille : le tableau doit prendre tout l'espace disponible
        from PySide6.QtWidgets import QSizePolicy
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # ✅ LIGNES PLUS HAUTES (60px au lieu de 52px)
        self.table.verticalHeader().setDefaultSectionSize(60)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_table_context_menu)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
            }
            QTableWidget::item {
                padding: 12px 14px;
                font-size: 13px;
                border-bottom: 1px solid #f1f5f9;
                color: #1e293b;
            }
            QTableWidget::item:selected {
                background-color: #e8f0fe;
                color: #1e293b;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 14px 12px;
                font-weight: 600;
                font-size: 12px;
                color: #64748b;
                border: none;
                border-bottom: 2px solid #e2e8f0;
            }
        """)
        tc_layout.addWidget(self.table)
        
        # ✅ IMPORTANT : le tableau s'étend dans son conteneur
        self.view_layout.addWidget(self.table_container, 1)
        
        # --- Vue CARTES ---
        self.cards_container = QWidget()
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        self.cards_grid.setSpacing(14)
        self.cards_container.hide()
        
        self.view_layout.addWidget(self.cards_container)
        
        layout.addWidget(self.view_container, 1)
        
        # ============================================================
        # LIGNE 4 : PAGINATION
        # ============================================================
        pagination = QFrame()
        pagination.setStyleSheet("background: transparent; border: none;")
        pg_layout = QHBoxLayout(pagination)
        pg_layout.setContentsMargins(0, 8, 0, 8)
        
        self.lbl_pagination = QLabel("Affichage de 0-0 sur 0 lots")
        self.lbl_pagination.setStyleSheet("color: #64748b; font-size: 12px;")
        pg_layout.addWidget(self.lbl_pagination)
        
        pg_layout.addStretch()
        
        self.btn_first = QPushButton("⏮")
        self.btn_first.setStyleSheet(self._pagination_btn_style())
        self.btn_first.clicked.connect(lambda: self._go_to_page(1))
        pg_layout.addWidget(self.btn_first)
        
        self.btn_prev = QPushButton("◀")
        self.btn_prev.setStyleSheet(self._pagination_btn_style())
        self.btn_prev.clicked.connect(lambda: self._go_to_page(self._current_page - 1))
        pg_layout.addWidget(self.btn_prev)
        
        self.btn_page = QPushButton("1")
        self.btn_page.setStyleSheet("""
            QPushButton {
                background-color: #e8f0fe;
                border: 1px solid #1a73e8;
                border-radius: 6px;
                padding: 6px 14px;
                color: #1a73e8;
                font-weight: bold;
                min-width: 32px;
            }
        """)
        pg_layout.addWidget(self.btn_page)
        
        self.btn_next = QPushButton("▶")
        self.btn_next.setStyleSheet(self._pagination_btn_style())
        self.btn_next.clicked.connect(lambda: self._go_to_page(self._current_page + 1))
        pg_layout.addWidget(self.btn_next)
        
        self.btn_last = QPushButton("⏭")
        self.btn_last.setStyleSheet(self._pagination_btn_style())
        self.btn_last.clicked.connect(lambda: self._go_to_page(99999))
        pg_layout.addWidget(self.btn_last)
        
        layout.addWidget(pagination)
        
        scroll.setWidget(content)
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)
    
    # ============================================================
    # STYLES
    # ============================================================
    
    def _toolbar_btn_style(self):
        return """
            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 14px;
                color: #1e293b;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #f1f5f9; }
        """
    
    def _combo_style(self):
        return """
            QComboBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                min-width: 120px;
            }
            QComboBox:focus { border: 2px solid #1a73e8; }
            QComboBox::drop-down { border: none; width: 22px; }
        """
    
    def _view_btn_style(self):
        return """
            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 14px;
                color: #1e293b;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #f1f5f9; }
            QPushButton:checked {
                background-color: #1a73e8;
                color: white;
                border: 1px solid #1a73e8;
            }
        """
    
    def _pagination_btn_style(self):
        return """
            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 12px;
                color: #64748b;
                font-weight: bold;
                min-width: 32px;
            }
            QPushButton:hover { background-color: #f1f5f9; }
            QPushButton:disabled { color: #cbd5e1; }
        """
    
    def _make_kpi_card(self, icon: str, value: str, title: str, subtitle: str, color: str):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        card.setMinimumHeight(100)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)
        
        # Icône
        icon_c = QFrame()
        icon_c.setFixedSize(52, 52)
        icon_c.setStyleSheet(f"background-color: {color}1A; border-radius: 10px;")
        ic_layout = QVBoxLayout(icon_c)
        ic_layout.setContentsMargins(0, 0, 0, 0)
        ic_lbl = QLabel(icon)
        ic_lbl.setStyleSheet(f"font-size: 24px; color: {color}; background: transparent;")
        ic_lbl.setAlignment(Qt.AlignCenter)
        ic_layout.addWidget(ic_lbl)
        layout.addWidget(icon_c)
        
        # Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 12px; color: #64748b; font-weight: 500;")
        text_layout.addWidget(title_lbl)
        
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #1e293b;")
        text_layout.addWidget(value_lbl)
        
        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setStyleSheet("font-size: 10px; color: #94a3b8;")
            text_layout.addWidget(sub_lbl)
        
        layout.addLayout(text_layout, 1)
        
        card.value_label = value_lbl
        return card
    
    # ============================================================
    # CHARGEMENT
    # ============================================================
    
    def load_data(self):
        try:
            statut = self.filter_statut.currentData()
            if statut:
                lots = self.controller.get_lots_by_statut(statut)
            else:
                lots = self.controller.get_all_lots()
            
            self._lots = lots
            self._update_kpis(lots)
            self._apply_filters()
        except Exception as e:
            print(f"❌ Erreur chargement lots: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les lots: {e}")
    
    def _update_kpis(self, lots):
        total = len(lots)
        
        montant_total = sum(l.get('montant_total', 0) or 0 for l in lots)
        
        en_attente = sum(1 for l in lots if l.get('statut') in ('OUVERT', 'VALIDE'))
        
        self.kpi_total.value_label.setText(str(total))
        self.kpi_montant.value_label.setText(f"{montant_total:,.0f} FCFA")
        self.kpi_attente.value_label.setText(str(en_attente))
    
    # ============================================================
    # FILTRES
    # ============================================================
    
    def _apply_filters(self):
        filtered = list(self._lots)
        
        # Recherche
        search = self.search_input.text().strip().lower()
        if search:
            filtered = [
                l for l in filtered
                if search in (l.get('numero_lot', '') or '').lower()
                or search in (l.get('type_lot', '') or '').lower()
            ]
        
        # Filtre statut
        statut_f = self.filter_statut.currentData()
        if statut_f:
            filtered = [l for l in filtered if l.get('statut') == statut_f]
        
        self._filtered_lots = filtered
        self._current_page = 1
        self._render_current_view()
    
    # ============================================================
    # RENDU
    # ============================================================
    
    def _set_view_mode(self, mode: str):
        self._view_mode = mode
        self.btn_view_table.setChecked(mode == "tableau")
        self.btn_view_card.setChecked(mode == "carte")
        self._render_current_view()
    
    def _render_current_view(self):
        if self._view_mode == "tableau":
            self.table_container.show()
            self.cards_container.hide()
            self._render_table()
        else:
            self.table_container.hide()
            self.cards_container.show()
            self._render_cards()
        
        self._update_pagination()
    
    def _render_table(self):
        start = (self._current_page - 1) * self._per_page
        end = start + self._per_page
        page_lots = self._filtered_lots[start:end]
        
        self.table.setRowCount(len(page_lots))
        
        for i, lot in enumerate(page_lots):
            # N° Lot
            numero_item = QTableWidgetItem(lot.get('numero_lot', ''))
            numero_item.setData(Qt.UserRole, lot)
            self.table.setItem(i, 0, numero_item)
            
            # Date
            date_str = lot.get('date_creation', '')[:10] if lot.get('date_creation') else '—'
            self.table.setItem(i, 1, QTableWidgetItem(date_str))
            
            # Nombre
            nb_item = QTableWidgetItem(str(lot.get('nombre_paiements', 0)))
            nb_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, nb_item)
            
            # Montant
            montant = lot.get('montant_total', 0)
            montant_item = QTableWidgetItem(f"{montant:,.0f} FCFA")
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 3, montant_item)
            
            # Type
            self.table.setItem(i, 4, QTableWidgetItem(lot.get('type_lot', '')))
            
            # Statut
            statut = lot.get('statut', '')
            bg, fg = LOT_STATUT_COLORS.get(statut, ('#f1f5f9', '#64748b'))
            statut_item = QTableWidgetItem(statut)
            statut_item.setBackground(QColor(bg))
            statut_item.setForeground(QColor(fg))
            statut_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 5, statut_item)
            
            # Actions
            actions_widget = self._create_actions_widget(lot)
            self.table.setCellWidget(i, 6, actions_widget)
    
    def _create_actions_widget(self, lot: dict) -> QWidget:
        """Crée le widget d'actions pour une ligne"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Bouton Voir (toujours)
        btn_view = QPushButton("👁️")
        btn_view.setFixedSize(28, 28)
        btn_view.setToolTip("Voir les détails")
        btn_view.setStyleSheet(self._row_btn_style())
        btn_view.clicked.connect(lambda: self._on_view_lot(lot))
        layout.addWidget(btn_view)
        
        # Bouton d'action selon statut
        statut = lot.get('statut', '')
        if statut == "OUVERT" and self._perm_ui.peut('reglement', 'VALIDATE'):
            btn = QPushButton("✅")
            btn.setFixedSize(28, 28)
            btn.setToolTip("Valider")
            btn.setStyleSheet(self._row_btn_style())
            btn.clicked.connect(lambda: self._on_validate_lot(lot))
            layout.addWidget(btn)
        
        elif statut == "VALIDE" and self._perm_ui.peut('reglement', 'PAY'):
            btn = QPushButton("▶️")
            btn.setFixedSize(28, 28)
            btn.setToolTip("Traiter")
            btn.setStyleSheet(self._row_btn_style())
            btn.clicked.connect(lambda: self._on_process_lot(lot))
            layout.addWidget(btn)
        
        elif statut == "TRAITE" and self._perm_ui.peut('reglement', 'PAY'):
            btn = QPushButton("📊")
            btn.setFixedSize(28, 28)
            btn.setToolTip("Comptabiliser")
            btn.setStyleSheet(self._row_btn_style())
            btn.clicked.connect(lambda: self._on_accounting_lot(lot))
            layout.addWidget(btn)
        
        layout.addStretch()
        return widget
    
    def _row_btn_style(self):
        return """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 14px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #f1f5f9; }
        """
    
    def _render_cards(self):
        # Vider
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        start = (self._current_page - 1) * self._per_page
        end = start + self._per_page
        page_lots = self._filtered_lots[start:end]
        
        if not page_lots:
            empty = QLabel("Aucun lot à afficher")
            empty.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 40px;")
            empty.setAlignment(Qt.AlignCenter)
            self.cards_grid.addWidget(empty, 0, 0, 1, 2)
            return
        
        for i, lot in enumerate(page_lots):
            card = LotCard(lot)
            card.view_requested.connect(self._on_view_lot)
            card.validate_requested.connect(self._on_validate_lot)
            card.process_requested.connect(self._on_process_lot)
            card.accounting_requested.connect(self._on_accounting_lot)
            card.context_menu_requested.connect(self._show_card_context_menu)
            
            row = i // 2
            col = i % 2
            self.cards_grid.addWidget(card, row, col)
        
        # ✅ Stretch en bas pour pousser les cartes vers le haut
        self.cards_grid.setRowStretch(self.cards_grid.rowCount(), 1)

    def _update_pagination(self):
        total = len(self._filtered_lots)
        start = (self._current_page - 1) * self._per_page + 1 if total > 0 else 0
        end = min(self._current_page * self._per_page, total)
        total_pages = max(1, (total + self._per_page - 1) // self._per_page)
        
        self.lbl_pagination.setText(f"Affichage de {start}-{end} sur {total} lots")
        self.btn_page.setText(str(self._current_page))
        
        self.btn_first.setEnabled(self._current_page > 1)
        self.btn_prev.setEnabled(self._current_page > 1)
        self.btn_next.setEnabled(self._current_page < total_pages)
        self.btn_last.setEnabled(self._current_page < total_pages)
    
    def _go_to_page(self, page: int):
        total_pages = max(1, (len(self._filtered_lots) + self._per_page - 1) // self._per_page)
        page = max(1, min(page, total_pages))
        if page != self._current_page:
            self._current_page = page
            self._render_current_view()
    
    # ============================================================
    # MENU CONTEXTUEL
    # ============================================================
    
    def _show_card_context_menu(self, lot: dict, global_pos):
        self._show_lot_context_menu(lot, global_pos)
    
    def _show_table_context_menu(self, pos):
        row = self.table.currentRow()
        if row < 0:
            return
        numero_item = self.table.item(row, 0)
        if not numero_item:
            return
        lot = numero_item.data(Qt.UserRole)
        if not lot:
            return
        self._show_lot_context_menu(lot, self.table.viewport().mapToGlobal(pos))
    
    def _show_lot_context_menu(self, lot: dict, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 8px 20px 8px 14px;
                border-radius: 5px;
                font-size: 12px;
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
        
        # Voir détails
        action_view = QAction("👁️  Voir les détails", self)
        action_view.triggered.connect(lambda: self._on_view_lot(lot))
        menu.addAction(action_view)
        
        statut = lot.get('statut', '')
        
        # Actions selon statut
        if statut == "OUVERT" and self._perm_ui.peut('reglement', 'VALIDATE'):
            action = QAction("✅  Valider le lot", self)
            action.triggered.connect(lambda: self._on_validate_lot(lot))
            menu.addAction(action)
        
        if statut == "VALIDE" and self._perm_ui.peut('reglement', 'PAY'):
            action = QAction("▶️  Traiter le lot", self)
            action.triggered.connect(lambda: self._on_process_lot(lot))
            menu.addAction(action)
        
        if statut == "TRAITE" and self._perm_ui.peut('reglement', 'PAY'):
            action = QAction("📊  Comptabiliser le lot", self)
            action.triggered.connect(lambda: self._on_accounting_lot(lot))
            menu.addAction(action)
        
        menu.addSeparator()
        
        # Imprimer
        action_print = QAction("🖨️  Imprimer le bordereau", self)
        action_print.triggered.connect(lambda: self._on_print_lot(lot))
        menu.addAction(action_print)
        
        # Copier le numéro
        action_copy = QAction("📋  Copier le N° de lot", self)
        action_copy.triggered.connect(lambda: self._copy_to_clipboard(lot.get('numero_lot', '')))
        menu.addAction(action_copy)
        
        menu.exec(global_pos)
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def _on_view_lot(self, lot: dict):
        """Ouvre le dialog de détail"""
        try:
            # Recharger le lot complet (avec les règlements)
            lot_id = lot.get('id')
            lot_complet = self.controller.get_lot(lot_id)
            if not lot_complet:
                QMessageBox.warning(self, "Erreur", "Impossible de charger le lot")
                return
            
            dialog = LotDetailDialog(
                lot=lot_complet,
                reglement_controller=self.controller,
                user=self.user,
                parent=self,
            )
            dialog.lot_updated.connect(self._on_lot_updated)
            dialog.exec()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _on_validate_lot(self, lot: dict):
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous valider le lot {lot.get('numero_lot')} ?\n\n"
            f"📊 {lot.get('nombre_paiements', 0)} règlements\n"
            f"💰 {lot.get('montant_total', 0):,.0f} FCFA",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        try:
            success = self.controller.valider_lot_paiement(lot.get('id'))
            if success:
                QMessageBox.information(self, "Succès", "✅ Lot validé avec succès")
                self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _on_process_lot(self, lot: dict):
        QMessageBox.information(self, "Info", "Traitement à implémenter (Phase 2)")
    
    def _on_accounting_lot(self, lot: dict):
        QMessageBox.information(self, "Info", "Comptabilisation à implémenter (Phase 2)")
    
    def _on_print_lot(self, lot: dict):
        QMessageBox.information(self, "Info", "Impression PDF à implémenter (Phase 4)")
    
    def _on_lot_updated(self, lot: dict):
        self.load_data()
    
    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copié", f"✅ '{text}' copié dans le presse-papiers")
    
    # ============================================================
    # CRÉATION
    # ============================================================
    
    def ouvrir_dialogue_creation(self):
        """Ouvre le dialogue de création de lot"""
        from addons.sinistres.views.lot_paiement_dialog import LotPaiementDialog
        
        dialog = LotPaiementDialog(
            reglement_controller=self.controller,
            user=self.user,
            parent=self,
        )
        dialog.lot_created.connect(self._on_lot_created)
        dialog.exec()
    
    def _on_lot_created(self, data: dict):
        self.load_data()
    
    # ============================================================
    # EXPORT
    # ============================================================
    
    def exporter_csv(self):
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exporter les lots",
            "lots_paiement.csv",
            "CSV (*.csv)"
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "N° Lot", "Date création", "Nombre paiements",
                    "Montant total", "Type", "Statut"
                ])
                for l in self._filtered_lots:
                    writer.writerow([
                        l.get('numero_lot', ''),
                        l.get('date_creation', '')[:10] if l.get('date_creation') else '',
                        l.get('nombre_paiements', 0),
                        l.get('montant_total', 0),
                        l.get('type_lot', ''),
                        l.get('statut', ''),
                    ])
            QMessageBox.information(self, "Export", f"✅ {len(self._filtered_lots)} lots exportés")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")