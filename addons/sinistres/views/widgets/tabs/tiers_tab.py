
"""
Onglet Tiers du Dossier 360 - 3 modes d'affichage
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QScrollArea, QMenu, QButtonGroup, QLineEdit
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor, QAction

from typing import List, Dict, Optional

from addons.sinistres.views.widgets.tiers_widgets import (
    KpiCardTiers, DonutWithLine, TiersCard, AddTiersCard
)


# ============================================================
# MODES D'AFFICHAGE
# ============================================================

MODE_CARDS = "cards"
MODE_TABLE = "table"
MODE_MIXED = "mixed"


class TiersTab(QWidget):
    """Onglet Tiers avec 3 modes d'affichage (Cartes / Tableau / Mixte)"""
    
    def __init__(self, dossier_360):
        super().__init__()
        self.dossier_360 = dossier_360
        self._tiers: List[dict] = []
        self._tiers_filtres: List[dict] = []
        self._selected_tiers: dict = None
        
        # Charger la préférence utilisateur
        self._settings = QSettings("LOMETA", "Dossier360")
        user_key = f"tiers_mode_{self._get_user_id()}"
        self._current_mode = self._settings.value(user_key, MODE_CARDS)
        
        self.setup_ui()
    
    # ============================================================
    # UI
    # ============================================================
    
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 15, 20, 15)
        root.setSpacing(12)
        
        root.addLayout(self._build_top_bar())
        
        # Zone KPI
        self.kpi_container = QWidget()
        self.kpi_layout = QHBoxLayout(self.kpi_container)
        self.kpi_layout.setContentsMargins(0, 0, 0, 0)
        self.kpi_layout.setSpacing(12)
        root.addWidget(self.kpi_container)
        
        # Zone contenu principal
        self.content_stack = QWidget()
        self.content_layout = QVBoxLayout(self.content_stack)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        root.addWidget(self.content_stack, 1)
        
        self._apply_mode()
    
    def _build_top_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(10)
        
        # Sélecteur de mode
        mode_frame = QFrame()
        mode_frame.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border-radius: 8px;
                padding: 2px;
            }
        """)
        mode_layout = QHBoxLayout(mode_frame)
        mode_layout.setContentsMargins(3, 3, 3, 3)
        mode_layout.setSpacing(2)
        
        self.btn_mode_cards = QPushButton("🔲  Cartes")
        self.btn_mode_table = QPushButton("📋  Tableau")
        self.btn_mode_mixed = QPushButton("⚙️  Mixte")
        
        for btn, mode in [
            (self.btn_mode_cards, MODE_CARDS),
            (self.btn_mode_table, MODE_TABLE),
            (self.btn_mode_mixed, MODE_MIXED),
        ]:
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 14px;
                    font-size: 12px;
                    font-weight: 500;
                    color: #64748b;
                }
                QPushButton:hover {
                    background-color: #e2e8f0;
                }
                QPushButton:checked {
                    background-color: white;
                    color: #1a73e8;
                    font-weight: bold;
                }
            """)
            btn.clicked.connect(lambda checked=False, m=mode: self._switch_mode(m))
            mode_layout.addWidget(btn)
        
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        self.mode_group.addButton(self.btn_mode_cards)
        self.mode_group.addButton(self.btn_mode_table)
        self.mode_group.addButton(self.btn_mode_mixed)
        
        bar.addWidget(mode_frame)
        bar.addStretch()
        
        # Bouton rafraîchir
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedSize(34, 34)
        self.btn_refresh.setToolTip("Rafraîchir la liste")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e8f0fe;
                border-color: #1a73e8;
            }
        """)
        self.btn_refresh.clicked.connect(self._recharger)
        bar.addWidget(self.btn_refresh)
        
        # Bouton ajouter
        self.btn_add = QPushButton("➕  Ajouter un tiers")
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self._ajouter_tiers)
        bar.addWidget(self.btn_add)
        
        return bar
    
    # ============================================================
    # CHANGEMENT DE MODE
    # ============================================================
    
    def _switch_mode(self, mode: str):
        if mode == self._current_mode:
            return
        self._current_mode = mode
        user_key = f"tiers_mode_{self._get_user_id()}"
        self._settings.setValue(user_key, mode)
        self._apply_mode()
        self._render_kpis()
        self._render_content()
    
    def _apply_mode(self):
        self.btn_mode_cards.setChecked(self._current_mode == MODE_CARDS)
        self.btn_mode_table.setChecked(self._current_mode == MODE_TABLE)
        self.btn_mode_mixed.setChecked(self._current_mode == MODE_MIXED)
    
    def _get_user_id(self) -> int:
        try:
            return self.dossier_360.user.id if self.dossier_360.user else 0
        except Exception:
            return 0
    
    # ============================================================
    # KPIs
    # ============================================================
    
    def _render_kpis(self):
        while self.kpi_layout.count():
            item = self.kpi_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        total = len(self._tiers)
        en_attente = sum(1 for t in self._tiers if not t.get('telephone'))
        complets = sum(1 for t in self._tiers
                       if t.get('telephone') and t.get('assurance') and t.get('police_assurance'))
        taux = int(complets / total * 100) if total > 0 else 0
        repartition = self._calculer_repartition_types()
        
        if self._current_mode == MODE_CARDS:
            self.kpi_layout.addWidget(KpiCardTiers(
                "Nombre de Tiers", str(total),
                "Parties impliquées dans le sinistre",
                "#3b82f6", "👥"
            ))
            self.kpi_layout.addWidget(KpiCardTiers(
                "En attente contact", str(en_attente), "", "#8b5cf6", "📞"
            ))
            self.kpi_layout.addWidget(KpiCardTiers(
                "Détails complets", str(complets), "", "#6366f1", "📋"
            ))
            
            card_taux = QFrame()
            card_taux.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    border-left: 5px solid #1a73e8;
                }
            """)
            card_taux.setMinimumHeight(110)
            card_taux.setMaximumHeight(130)
            layout = QVBoxLayout(card_taux)
            layout.setContentsMargins(18, 14, 18, 14)
            layout.setSpacing(4)
            
            lbl = QLabel("TAUX RÉPONSE")
            lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 700;")
            layout.addWidget(lbl)
            
            val = QLabel(f"{taux}%")
            val.setStyleSheet("font-size: 32px; font-weight: bold; color: #1e293b;")
            layout.addWidget(val)
            
            spark = QLabel("📈")
            spark.setStyleSheet("font-size: 24px; color: #22c55e;")
            spark.setAlignment(Qt.AlignRight)
            layout.addWidget(spark)
            
            self.kpi_layout.addWidget(card_taux)
        else:
            self.kpi_layout.addWidget(self._build_kpi_nombre_tiers_card(total, repartition))
            self.kpi_layout.addWidget(self._build_kpi_graph_card(
                "Tiers Impliqués (% Claims)",
                f"{taux}%",
                f"(+{taux/10:.1f}% MoM)" if taux > 0 else "",
                taux, "#22c55e",
                [20, 35, 40, 55, 60, 70, taux]
            ))
            self.kpi_layout.addWidget(self._build_kpi_graph_card(
                "Délai Moyen de Traitement",
                "14 Jours", "(-1 Jour MoM)", 65, "#1e293b",
                [18, 15, 20, 14, 16, 13, 14]
            ))
            self.kpi_layout.addWidget(self._build_recours_card())
    
    def _build_kpi_graph_card(self, title, value, sub, percent, color, line_data) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        card.setMinimumHeight(150)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)
        
        header = QHBoxLayout()
        lbl = QLabel(title)
        lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600;")
        header.addWidget(lbl)
        header.addStretch()
        menu = QLabel("⋮")
        menu.setStyleSheet("color: #94a3b8; font-size: 16px;")
        header.addWidget(menu)
        layout.addLayout(header)
        
        row = QHBoxLayout()
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #1e293b;")
        row.addWidget(val_lbl)
        if sub:
            sub_lbl = QLabel(sub)
            sub_lbl.setStyleSheet("color: #94a3b8; font-size: 10px;")
            row.addWidget(sub_lbl)
        row.addStretch()
        layout.addLayout(row)
        
        graph = DonutWithLine()
        graph.set_data(percent, color, line_data, color)
        layout.addWidget(graph, 1)
        
        return card
    
    def _build_recours_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        card.setMinimumHeight(150)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)
        
        title = QLabel("Statut de Recours (Subrogation)")
        title.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600;")
        layout.addWidget(title)
        
        for label, val, color in [
            ("🟠 Open case", "26", "#fed7aa"),
            ("⚫ Closed case", "31", "#1e293b"),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 11px; color: #1e293b;")
            row.addWidget(lbl)
            row.addStretch()
            v = QLabel(val)
            v.setStyleSheet("font-size: 11px; color: #1e293b; font-weight: bold;")
            row.addWidget(v)
            layout.addLayout(row)
            
            bar = QFrame()
            bar.setFixedHeight(8)
            bar.setStyleSheet(f"QFrame {{ background-color: {color}; border-radius: 4px; }}")
            layout.addWidget(bar)
        
        pct = QLabel("88% Complété")
        pct.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        pct.setAlignment(Qt.AlignRight)
        layout.addWidget(pct)
        
        return card
    
    # ============================================================
    # CONTENU PRINCIPAL
    # ============================================================
    
    def _render_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        
        if self._current_mode == MODE_CARDS:
            self.content_layout.addWidget(self._build_cards_view())
        elif self._current_mode == MODE_TABLE:
            self.content_layout.addWidget(self._build_table_view())
        elif self._current_mode == MODE_MIXED:
            self.content_layout.addWidget(self._build_mixed_view())
    
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
    
    def _build_cards_view(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: #f8fafc;")
        
        content = QWidget()
        content.setStyleSheet("background-color: #f8fafc;")
        grid = QGridLayout(content)
        grid.setContentsMargins(0, 10, 0, 10)
        grid.setSpacing(15)
        
        add_card = AddTiersCard()
        add_card.clicked.connect(self._ajouter_tiers)
        grid.addWidget(add_card, 0, 0)
        
        for i, tiers in enumerate(self._tiers, start=1):
            card = TiersCard(tiers)
            card.clicked.connect(self._on_tiers_clicked)
            card.contact_clicked.connect(self._on_contact_action)
            grid.addWidget(card, i // 4, i % 4)
        
        grid.setRowStretch(grid.rowCount(), 1)
        scroll.setWidget(content)
        return scroll
    
    def _build_table_view(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(8)
        
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔎 Rechercher...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
            }
        """)
        self.search_input.textChanged.connect(self._filtrer_tableau)
        search_row.addWidget(self.search_input, 1)
        layout.addLayout(search_row)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Type", "Nom", "Téléphone", "Assurance", "Police"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
                font-size: 12px;
            }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)

        self.table.itemSelectionChanged.connect(self._on_table_selection_changed)
        self.table.doubleClicked.connect(self._on_row_double_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_tiers_context_menu)
        self.table.doubleClicked.connect(self._on_row_double_clicked)
        
        self._populate_table(self._tiers)
        layout.addWidget(self.table)
        return container
    
    def _populate_table(self, tiers: List[dict]):
        self._tiers_filtres = list(tiers)
        self.table.setRowCount(len(tiers))
        
        for i, t in enumerate(tiers):
            type_tiers = self._format_type(t.get('type_tiers', ''))
            nom_complet = f"{t.get('nom', '')} {t.get('prenom', '')}".strip()
            
            item_type = QTableWidgetItem(type_tiers)
            item_type.setData(Qt.UserRole, i)
            self.table.setItem(i, 0, item_type)
            self.table.setItem(i, 1, QTableWidgetItem(nom_complet))
            self.table.setItem(i, 2, QTableWidgetItem(t.get('telephone') or "—"))
            self.table.setItem(i, 3, QTableWidgetItem(t.get('assurance') or "—"))
            self.table.setItem(i, 4, QTableWidgetItem(t.get('police_assurance') or "—"))
    
    def _filtrer_tableau(self, text: str):
        text = text.lower().strip()
        if not text:
            self._populate_table(self._tiers)
            return
        filtered = [
            t for t in self._tiers
            if text in (t.get('nom') or '').lower()
            or text in (t.get('prenom') or '').lower()
            or text in (t.get('telephone') or '').lower()
            or text in (t.get('assurance') or '').lower()
            or text in (t.get('police_assurance') or '').lower()
        ]
        self._populate_table(filtered)
    
    def _build_mixed_view(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        # Tableau (gauche, ~70%)
        table_widget = self._build_table_view()
        layout.addWidget(table_widget, 3)
        
        # ✅ Conteneur pour le panneau latéral (permet le refresh ciblé)
        self._side_panel_container = QWidget()
        side_layout = QVBoxLayout(self._side_panel_container)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_panel = self._build_side_panel()
        side_layout.addWidget(side_panel)
        
        layout.addWidget(self._side_panel_container, 1)
        
        return container
    
    def _build_side_panel(self) -> QWidget:
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        panel.setMinimumWidth(280)
        panel.setMaximumWidth(400)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(15)
        
        if not self._selected_tiers:
            empty = QLabel("👈 Sélectionnez un tiers\npour voir ses détails")
            empty.setStyleSheet("color: #94a3b8; font-size: 12px; font-style: italic;")
            empty.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty)
            layout.addStretch()
            return panel
        
        t = self._selected_tiers
        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 48px;")
        avatar.setAlignment(Qt.AlignCenter)
        layout.addWidget(avatar)
        
        nom_complet = f"{t.get('nom', '')} {t.get('prenom', '')}".strip()
        lbl_nom = QLabel(nom_complet)
        lbl_nom.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        lbl_nom.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_nom)
        
        lbl_type = QLabel(f"👤 {self._format_type(t.get('type_tiers', ''))}")
        lbl_type.setStyleSheet("font-size: 11px; color: #64748b;")
        lbl_type.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_type)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #f1f5f9; max-height: 1px; border: none;")
        layout.addWidget(sep)
        
        contact_title = QLabel("Contact")
        contact_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #1e293b;")
        layout.addWidget(contact_title)
        
        for label, value in [
            ("📞", t.get('telephone') or "Non renseigné"),
            ("✉️", t.get('email') or "Non renseigné"),
            ("📍", t.get('adresse') or "Non renseignée"),
        ]:
            row = QHBoxLayout()
            icon = QLabel(label)
            icon.setStyleSheet("font-size: 12px;")
            row.addWidget(icon)
            val = QLabel(value)
            val.setStyleSheet("font-size: 11px; color: #1e293b;")
            val.setWordWrap(True)
            row.addWidget(val, 1)
            layout.addLayout(row)
        
        layout.addStretch()
        return panel
    
    def _calculer_repartition_types(self) -> Dict[str, int]:
        repartition = {}
        for t in self._tiers:
            type_tiers = (t.get('type_tiers') or 'autre').lower()
            libelle = self._format_type(type_tiers)
            repartition[libelle] = repartition.get(libelle, 0) + 1
        return repartition
    
    def _build_kpi_nombre_tiers_card(self, total, repartition) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        card.setMinimumHeight(150)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)
        
        header = QHBoxLayout()
        lbl = QLabel("Nombre de Tiers")
        lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600;")
        header.addWidget(lbl)
        header.addStretch()
        layout.addLayout(header)
        
        row = QHBoxLayout()
        val_lbl = QLabel(str(total))
        val_lbl.setStyleSheet("font-size: 32px; font-weight: bold; color: #1e293b;")
        row.addWidget(val_lbl)
        row.addStretch()
        
        icon = QLabel("👥")
        icon.setStyleSheet("font-size: 32px; color: #3b82f6;")
        row.addWidget(icon)
        layout.addLayout(row)
        
        if repartition:
            repart_layout = QHBoxLayout()
            repart_layout.setSpacing(6)
            colors = {
                'Conducteur': '#3b82f6', 'Passager': '#8b5cf6',
                'Témoin': '#f59e0b', 'Victime': '#ef4444',
                'Assureur adverse': '#06b6d4', 'Autre conducteur': '#10b981',
                'Tiers': '#64748b',
            }
            for type_label, count in list(repartition.items())[:4]:
                color = colors.get(type_label, '#64748b')
                badge = QLabel(f"{count} {type_label}")
                badge.setStyleSheet(f"""
                    background-color: {color}20;
                    color: {color};
                    padding: 2px 8px;
                    border-radius: 8px;
                    font-size: 10px;
                    font-weight: bold;
                """)
                repart_layout.addWidget(badge)
            repart_layout.addStretch()
            layout.addLayout(repart_layout)
        
        layout.addStretch()
        return card
    
    # ============================================================
    # DONNÉES
    # ============================================================
    
    def update_data(self, data):
        """Charge la liste des tiers depuis le sinistre"""
        try:
            tiers_data = data.get('tiers') if data else None
            
            if tiers_data is None:
                sinistre = self.dossier_360.sinistre_controller.get_sinistre(
                    self.dossier_360.sinistre_id
                )
                tiers_data = (sinistre or {}).get('tiers', [])
            
            self._tiers = tiers_data or []
            self._tiers_filtres = list(self._tiers)
            self._selected_tiers = None
            
            self._render_kpis()
            self._render_content()
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur de chargement des tiers : {e}")
    
    def _recharger(self):
        if self.dossier_360.sinistre_data:
            self.update_data(self.dossier_360.sinistre_data)
    
    # ============================================================
    # HELPERS
    # ============================================================
    
    def _format_type(self, type_tiers: str) -> str:
        mapping = {
            'responsable': 'Conducteur',
            'victime': 'Victime',
            'temoin': 'Témoin',
            'assureur_adverse': 'Assureur adverse',
            'conducteur': 'Conducteur',
            'passager': 'Passager',
            'autre_conducteur': 'Autre conducteur',
        }
        return mapping.get((type_tiers or '').lower(), type_tiers or 'Tiers')
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def _on_tiers_clicked(self, tiers: dict):
        self._selected_tiers = tiers
        self._ouvrir_fiche_tiers(tiers)
    
    def _on_contact_action(self, tiers: dict, action: str):
        nom = f"{tiers.get('nom', '')} {tiers.get('prenom', '')}".strip()
        if action == 'phone':
            tel = tiers.get('telephone')
            if tel:
                QMessageBox.information(self, "Appel", f"Appel de {nom}\n📞 {tel}")
            else:
                QMessageBox.warning(self, "Info", "Téléphone non renseigné")
        elif action == 'email':
            email = tiers.get('email')
            if email:
                QMessageBox.information(self, "Email", f"Email à {nom}\n✉️ {email}")
            else:
                QMessageBox.warning(self, "Info", "Email non renseigné")
        elif action == 'info':
            self._ouvrir_fiche_tiers(tiers)
    
    def _ouvrir_fiche_tiers(self, tiers: dict):
        nom = f"{tiers.get('nom', '')} {tiers.get('prenom', '')}".strip()
        QMessageBox.information(
            self, f"Fiche tiers : {nom}",
            f"Type : {self._format_type(tiers.get('type_tiers', ''))}\n"
            f"Téléphone : {tiers.get('telephone') or '—'}\n"
            f"Email : {tiers.get('email') or '—'}\n"
            f"Adresse : {tiers.get('adresse') or '—'}\n"
            f"Assurance : {tiers.get('assurance') or '—'}\n"
            f"Police : {tiers.get('police_assurance') or '—'}"
        )
    
    # ============================================================
    # AJOUT / MODIFICATION / SUPPRESSION
    # ============================================================
    
    def _ajouter_tiers(self):
        """Ouvre le dialogue d'ajout de tiers"""
        try:
            from addons.sinistres.views.dialogs_files.tiers_dialog import TiersDialog
            dialog = TiersDialog(
                sinistre_id=self.dossier_360.sinistre_id,
                controller=self.dossier_360.sinistre_controller,
                user=self.dossier_360.user,
                parent=self
            )
            dialog.tiers_saved.connect(lambda data: self.dossier_360.refresh())
            dialog.exec()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le dialogue: {str(e)}")
    
    def _modifier_tiers(self, tiers: dict):
        """Ouvre le dialogue de modification du tiers"""
        try:
            from addons.sinistres.views.dialogs_files.tiers_dialog import TiersDialog
            dialog = TiersDialog(
                sinistre_id=self.dossier_360.sinistre_id,
                controller=self.dossier_360.sinistre_controller,
                user=self.dossier_360.user,
                tiers_data=tiers,
                parent=self
            )
            dialog.tiers_saved.connect(lambda data: self.dossier_360.refresh())
            dialog.exec()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le dialogue: {str(e)}")
    
    def _supprimer_tiers(self, tiers: dict):
        nom_complet = f"{tiers.get('nom', '')} {tiers.get('prenom', '')}".strip()
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous vraiment supprimer le tiers :\n\n"
            f"👤 {nom_complet}\n"
            f"📞 {tiers.get('telephone') or '—'}\n\n"
            f"Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            success = self.dossier_360.sinistre_controller.supprimer_tiers(tiers.get('id'))
            if success:
                QMessageBox.information(self, "Succès", f"Tiers {nom_complet} supprimé")
                self.dossier_360.refresh()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de supprimer le tiers")
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    # ============================================================
    # MENU CONTEXTUEL
    # ============================================================
    
    def _show_tiers_context_menu(self, position):
        row = self.table.currentRow()
        if row < 0:
            return
        
        tiers = self._get_tiers_from_row(row)
        if not tiers:
            return
        
        tel = tiers.get('telephone')
        email = tiers.get('email')
        
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
            QMenu::item:disabled { color: #94a3b8; }
            QMenu::separator {
                height: 1px;
                background-color: #e2e8f0;
                margin: 4px 8px;
            }
        """)
        
        action_voir = QAction("👁️  Voir la fiche", self)
        action_voir.triggered.connect(lambda: self._ouvrir_fiche_tiers(tiers))
        menu.addAction(action_voir)
        
        action_modifier = QAction("✏️  Modifier", self)
        action_modifier.triggered.connect(lambda: self._modifier_tiers(tiers))
        menu.addAction(action_modifier)
        
        menu.addSeparator()
        
        action_appeler = QAction("📞  Appeler", self)
        action_appeler.setEnabled(bool(tel))
        action_appeler.triggered.connect(lambda: self._on_contact_action(tiers, 'phone'))
        menu.addAction(action_appeler)
        
        action_email = QAction("✉️  Envoyer email", self)
        action_email.setEnabled(bool(email))
        action_email.triggered.connect(lambda: self._on_contact_action(tiers, 'email'))
        menu.addAction(action_email)
        
        action_sms = QAction("💬  Envoyer SMS", self)
        action_sms.setEnabled(bool(tel))
        action_sms.triggered.connect(lambda: self._envoyer_sms(tiers))
        menu.addAction(action_sms)
        
        action_whatsapp = QAction("📱  Envoyer WhatsApp", self)
        action_whatsapp.setEnabled(bool(tel))
        action_whatsapp.triggered.connect(lambda: self._envoyer_whatsapp(tiers))
        menu.addAction(action_whatsapp)
        
        menu.addSeparator()
        
        action_copier = QAction("📋  Copier les coordonnées", self)
        action_copier.triggered.connect(lambda: self._copier_coordonnees(tiers))
        menu.addAction(action_copier)
        
        action_exporter = QAction("📥  Exporter en CSV", self)
        action_exporter.triggered.connect(lambda: self._exporter_tiers_csv(tiers))
        menu.addAction(action_exporter)
        
        menu.addSeparator()
        
        action_supprimer = QAction("🗑️  Supprimer", self)
        action_supprimer.triggered.connect(lambda: self._supprimer_tiers(tiers))
        menu.addAction(action_supprimer)
        
        menu.exec(self.table.viewport().mapToGlobal(position))
    
    def _get_tiers_from_row(self, row: int) -> Optional[dict]:
        if self._tiers_filtres and 0 <= row < len(self._tiers_filtres):
            return self._tiers_filtres[row]
        if self._tiers and 0 <= row < len(self._tiers):
            return self._tiers[row]
        return None
    
    def _envoyer_sms(self, tiers: dict):
        tel = tiers.get('telephone')
        if not tel:
            QMessageBox.warning(self, "Info", "Téléphone non renseigné")
            return
        QMessageBox.information(self, "SMS",
            f"SMS à {tiers.get('nom')} {tiers.get('prenom')}\n📞 {tel}")
    
    def _envoyer_whatsapp(self, tiers: dict):
        tel = tiers.get('telephone')
        if not tel:
            QMessageBox.warning(self, "Info", "Téléphone non renseigné")
            return
        QMessageBox.information(self, "WhatsApp",
            f"WhatsApp à {tiers.get('nom')} {tiers.get('prenom')}\n📞 {tel}")
    
    def _copier_coordonnees(self, tiers: dict):
        from PySide6.QtWidgets import QApplication
        nom_complet = f"{tiers.get('nom', '')} {tiers.get('prenom', '')}".strip()
        lignes = [
            f"Nom : {nom_complet}",
            f"Type : {self._format_type(tiers.get('type_tiers', ''))}",
            f"Téléphone : {tiers.get('telephone') or '—'}",
            f"Email : {tiers.get('email') or '—'}",
            f"Adresse : {tiers.get('adresse') or '—'}",
            f"Assurance : {tiers.get('assurance') or '—'}",
            f"Police : {tiers.get('police_assurance') or '—'}",
        ]
        texte = "\n".join(lignes)
        QApplication.clipboard().setText(texte)
        QMessageBox.information(self, "Copié", f"Coordonnées copiées :\n\n{texte}")
    
    def _exporter_tiers_csv(self, tiers: dict):
        from PySide6.QtWidgets import QFileDialog
        import csv
        nom_complet = f"{tiers.get('nom', '')} {tiers.get('prenom', '')}".strip()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporter le tiers",
            f"tiers_{nom_complet.replace(' ', '_')}.csv",
            "CSV (*.csv)"
        )
        if not filename:
            return
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Champ", "Valeur"])
                writer.writerow(["Nom", nom_complet])
                writer.writerow(["Type", self._format_type(tiers.get('type_tiers', ''))])
                writer.writerow(["Téléphone", tiers.get('telephone') or ''])
                writer.writerow(["Email", tiers.get('email') or ''])
                writer.writerow(["Adresse", tiers.get('adresse') or ''])
                writer.writerow(["Assurance", tiers.get('assurance') or ''])
                writer.writerow(["Police", tiers.get('police_assurance') or ''])
            QMessageBox.information(self, "Export", f"Fichier exporté :\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur d'export: {str(e)}")
    
    def _on_row_double_clicked(self, index):
        row = index.row()
        tiers = self._get_tiers_from_row(row)
        if tiers:
            self._ouvrir_fiche_tiers(tiers)

    def _on_table_selection_changed(self):
        """Appelé quand la sélection dans le tableau change"""
        row = self.table.currentRow()
        if row < 0:
            return
        
        tiers = self._get_tiers_from_row(row)
        if not tiers:
            return
        
        self._selected_tiers = tiers
        
        # En mode Mixte → recharger uniquement le panneau latéral
        if self._current_mode == MODE_MIXED:
            self._refresh_side_panel()

    def _refresh_side_panel(self):
        """Met à jour uniquement le panneau latéral (sans reconstruire le tableau)"""
        # Trouver le QFrame contenant le panneau latéral
        if not hasattr(self, '_side_panel_container'):
            return
        
        # Vider le conteneur
        while self._side_panel_container.layout().count():
            item = self._side_panel_container.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Reconstruire le contenu
        new_panel = self._build_side_panel()
        self._side_panel_container.layout().addWidget(new_panel)