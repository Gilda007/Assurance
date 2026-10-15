from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QComboBox, QLineEdit,
    QGroupBox, QFormLayout, QDialog, QDialogButtonBox,
    QMessageBox, QFrame, QTabWidget, QCheckBox, QScrollArea,
    QMenu, QSizePolicy, QGridLayout, QAbstractItemView
)
from PySide6.QtCore import QSize, Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QAction, QPainterPath
from typing import List, Dict, Any
from addons.sinistres.views.dialogs_files.expert_dialog import ExpertDialog
import qtawesome as qta


ENTITE_COLORS = {
        'Sinistre': '#1a73e8',       # Bleu vif
        'Expertise': '#8b5cf6',       # Violet
        'Evaluation': '#06b6d4',      # Cyan
        'Reglement': '#f59e0b',       # Orange
        'Recours': '#ef4444',         # Rouge
        'Provision': '#84cc16',       # Vert lime
        'Referentiel': '#ec4899',     # Rose
        'User': '#64748b',            # Gris
        'Document': '#14b8a6',        # Teal
        'Autre': '#94a3b8',           # Gris clair
    }

ACTION_COLORS = {
        'CREATION': ('#dcfce7', '#166534'),           # Vert
        'MODIFICATION': ('#fef3c7', '#92400e'),       # Ambre
        'VALIDATION': ('#dbeafe', '#1e40af'),         # Bleu
        'SUPPRESSION': ('#fee2e2', '#991b1b'),        # Rouge
        'CHANGEMENT_STATUT': ('#ede9fe', '#5b21b6'),  # Violet
        'REVISION': ('#fce7f3', '#9d174d'),           # Rose
        'AFFECTATION': ('#cffafe', '#155e75'),        # Cyan
        'DEMARRAGE': ('#e0e7ff', '#3730a3'),          # Indigo
        'FICHIERS_JOINTS': ('#f3e8ff', '#6b21a8'),    # Fuchsia
        'PAIEMENT': ('#d1fae5', '#065f46'),           # Émeraude
        'ENCAISSEMENT': ('#dcfce7', '#14532d'),       # Vert foncé
    }


# ============================================================
# WIDGET : CARTE BANQUE
# ============================================================

class BanqueCard(QFrame):
    """Carte d'une banque style capture"""
    
    edit_requested = Signal(dict)
    delete_requested = Signal(dict)
    view_requested = Signal(dict)
    comptes_requested = Signal(dict)
    context_menu_requested = Signal(dict, QPointF)
    
    def __init__(self, banque: dict, nb_comptes: int = 0, nb_actifs: int = 0, parent=None):
        super().__init__(parent)
        self.banque = banque
        self.setFixedWidth(380)
        self.setMinimumHeight(260)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        
        self.setStyleSheet("""
            BanqueCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            BanqueCard:hover {
                border: 1px solid #cbd5e1;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)
        
        # ============================================================
        # LIGNE 1 : Logo + Nom + Statut
        # ============================================================
        header = QHBoxLayout()
        header.setSpacing(12)
        
        # Logo (initiales dans un carré coloré)
        code = banque.get('code_banque', '?')
        logo = QLabel(code[:2].upper())
        logo.setFixedSize(50, 50)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            background-color: #1a73e8;
            color: white;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
        """)
        header.addWidget(logo)
        
        # Nom + infos
        name_layout = QVBoxLayout()
        name_layout.setSpacing(2)
        
        libelle = QLabel(banque.get('libelle', 'Sans nom'))
        libelle.setStyleSheet("font-size: 15px; font-weight: bold; color: #1e293b;")
        libelle.setWordWrap(True)
        name_layout.addWidget(libelle)
        
        code_lbl = QLabel(f"Code: {code}")
        code_lbl.setStyleSheet("font-size: 10px; color: #64748b;")
        name_layout.addWidget(code_lbl)
        
        header.addLayout(name_layout, 1)
        
        # Statut badge
        actif = banque.get('est_actif', True)
        statut = QLabel("✅ ACTIF" if actif else "❌ INACTIF")
        statut.setStyleSheet(f"""
            background-color: {'#dcfce7' if actif else '#fee2e2'};
            color: {'#166534' if actif else '#991b1b'};
            padding: 4px 10px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        """)
        statut.setAlignment(Qt.AlignCenter)
        header.addWidget(statut)
        
        layout.addLayout(header)
        
        # ============================================================
        # LIGNE 2 : Boutons d'action (icônes)
        # ============================================================
        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addStretch()
        
        for icon_name, tooltip, callback in [
            ("fa5s.edit", "Modifier", lambda: self.edit_requested.emit(self.banque)),
            ("fa5s.trash-alt", "Supprimer", lambda: self.delete_requested.emit(self.banque)),
            ("fa5s.eye", "Voir détails", lambda: self.view_requested.emit(self.banque)),
        ]:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setToolTip(tooltip)
            btn.setIcon(qta.icon(icon_name, color='#64748b'))
            btn.setIconSize(QSize(12, 12))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f1f5f9;
                    border: none;
                    border-radius: 15px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e2e8f0;
                }
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            actions.addWidget(btn)
        
        layout.addLayout(actions)
        
        # ============================================================
        # LIGNE 3 : BIC/SWIFT
        # ============================================================
        bic_layout = QVBoxLayout()
        bic_layout.setSpacing(2)
        
        bic_lbl = QLabel("BIC/SWIFT")
        bic_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        bic_layout.addWidget(bic_lbl)
        
        bic_val = QLabel(banque.get('bic_swift', '—'))
        bic_val.setStyleSheet("font-size: 13px; color: #1e293b; font-weight: bold;")
        bic_layout.addWidget(bic_val)
        
        layout.addLayout(bic_layout)
        
        # ============================================================
        # LIGNE 4 : Pays + Utilisateur
        # ============================================================
        info_row = QHBoxLayout()
        
        # Pays
        pays_layout = QVBoxLayout()
        pays_layout.setSpacing(2)
        
        pays_lbl = QLabel("Pays")
        pays_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        pays_layout.addWidget(pays_lbl)
        
        pays_val = QLabel(banque.get('pays', '—'))
        pays_val.setStyleSheet("font-size: 12px; color: #1e293b;")
        pays_layout.addWidget(pays_val)
        
        info_row.addLayout(pays_layout, 1)
        
        # Utilisateur
        user_layout = QVBoxLayout()
        user_layout.setSpacing(2)
        
        user_lbl = QLabel("Personne")
        user_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        user_layout.addWidget(user_lbl)
        
        created = banque.get('created_at', '')
        if created:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created.replace('Z', ''))
                created_str = dt.strftime('%d-%m-%Y %H:%M')
            except:
                created_str = created[:16]
        else:
            created_str = '—'
        
        user_val = QLabel(f"🕐 {created_str}")
        user_val.setStyleSheet("font-size: 11px; color: #64748b;")
        user_layout.addWidget(user_val)
        
        info_row.addLayout(user_layout, 1)
        
        layout.addLayout(info_row)
        
        # ============================================================
        # LIGNE 5 : Comptes associés
        # ============================================================
        comptes_layout = QHBoxLayout()
        comptes_layout.setSpacing(8)
        
        comptes_info = QVBoxLayout()
        comptes_info.setSpacing(2)
        
        comptes_lbl = QLabel("Comptes associés")
        comptes_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        comptes_info.addWidget(comptes_lbl)
        
        comptes_val = QLabel(f"{nb_actifs} actifs, {nb_comptes - nb_actifs} en attente")
        comptes_val.setStyleSheet("font-size: 11px; color: #1e293b;")
        comptes_info.addWidget(comptes_val)
        
        comptes_layout.addLayout(comptes_info, 1)
        
        # Bouton Voir Comptes
        btn_comptes = QPushButton("📋 Voir Comptes")
        btn_comptes.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11px;
                color: #1e293b;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        btn_comptes.setCursor(Qt.PointingHandCursor)
        btn_comptes.clicked.connect(lambda: self.comptes_requested.emit(self.banque))
        comptes_layout.addWidget(btn_comptes)
        
        layout.addLayout(comptes_layout)
    
    def _on_context_menu(self, pos):
        self.context_menu_requested.emit(self.banque, self.mapToGlobal(pos))


# [Le code complet de BanqueCard est au-dessus]

class BanquesTab(QWidget):
    """Onglet de gestion des banques - Style carte + tableau"""
    
    def __init__(self, reglement_controller, user):
        super().__init__()
        self.reglement_controller = reglement_controller
        self.user = user
        self._banques = []
        self._filtered_banques = []
        self._view_mode = "carte"
        self._current_page = 1
        self._per_page = 6
        
        from addons.sinistres.services.permission_service import PermissionService
        from addons.sinistres.security.permissions_helper import PermissionsUI
        self._perm_ui = PermissionsUI(self.user, PermissionService())
        
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
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)
        
        # ─── KPI Cards ───
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        
        self.kpi_total = self._make_kpi_card(
            "fa5s.university", "8", "Total de Banques", "↑ 2 vs Dernier mois", "#1a73e8"
        )
        kpi_row.addWidget(self.kpi_total)
        
        self.kpi_actives = self._make_kpi_card(
            "fa5s.check-circle", "6", "Banques Actives", "Actives vs En cours", 
            "#22c55e", show_progress=True, pct=75
        )
        kpi_row.addWidget(self.kpi_actives)
        
        self.kpi_pays = self._make_kpi_card(
            "fa5s.globe", "4", "Pays d'Opération", 
            "Afrique: 4 · Caraïbes: 0 · Pérou: 0", "#3b82f6"
        )
        kpi_row.addWidget(self.kpi_pays)
        
        layout.addLayout(kpi_row)
        
        # ─── Toolbar ───
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
        
        # ✅ Bouton Nouvelle banque
        self.btn_nouvelle = QPushButton("  Nouvelle banque")
        self.btn_nouvelle.setIcon(qta.icon('fa5s.plus-circle', color='white'))
        self.btn_nouvelle.setIconSize(QSize(12, 12))
        self.btn_nouvelle.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
                border: none;
                text-align: left;
            }
            QPushButton:hover { background-color: #1557b0; }
        """)
        self.btn_nouvelle.setCursor(Qt.PointingHandCursor)
        self.btn_nouvelle.clicked.connect(self.ouvrir_dialogue_creation)
        if not self._perm_ui.peut('referentiel', 'CREATE'):
            self.btn_nouvelle.hide()
        tb_layout.addWidget(self.btn_nouvelle)
        
        # ✅ Bouton Rafraîchir
        self.btn_refresh = QPushButton("  Rafraîchir")
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#1e293b'))
        self.btn_refresh.setIconSize(QSize(12, 12))
        self.btn_refresh.setStyleSheet(self._toolbar_btn_style())
        self.btn_refresh.clicked.connect(self.load_data)
        tb_layout.addWidget(self.btn_refresh)
        
        # ✅ Bouton Exporter
        self.btn_export = QPushButton("  Exporter CSV")
        self.btn_export.setIcon(qta.icon('fa5s.download', color='#1e293b'))
        self.btn_export.setIconSize(QSize(12, 12))
        self.btn_export.setStyleSheet(self._toolbar_btn_style())
        self.btn_export.clicked.connect(self.exporter_csv)
        tb_layout.addWidget(self.btn_export)
        
        # ✅ Bouton Paramètres Import
        self.btn_import = QPushButton("  Paramètres")
        self.btn_import.setIcon(qta.icon('fa5s.cog', color='#1e293b'))
        self.btn_import.setIconSize(QSize(12, 12))
        self.btn_import.setStyleSheet(self._toolbar_btn_style())
        self.btn_import.clicked.connect(self.ouvrir_parametres_import)
        tb_layout.addWidget(self.btn_import)
        
        # Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche...")
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
        
        # Filtre Pays
        self.filter_pays = QComboBox()
        self.filter_pays.addItem("Pays", None)
        self.filter_pays.setStyleSheet(self._combo_style())
        self.filter_pays.currentIndexChanged.connect(self._apply_filters)
        tb_layout.addWidget(self.filter_pays)
        
        # Filtre Statut
        self.filter_statut = QComboBox()
        self.filter_statut.addItem("Statut", None)
        self.filter_statut.addItem("Actif", True)
        self.filter_statut.addItem("Inactif", False)
        self.filter_statut.setStyleSheet(self._combo_style())
        self.filter_statut.currentIndexChanged.connect(self._apply_filters)
        tb_layout.addWidget(self.filter_statut)
        
        # ✅ Vue Tableau
        self.btn_view_table = QPushButton("  VUE TABLEAU")
        self.btn_view_table.setCheckable(True)
        self.btn_view_table.setIcon(qta.icon('fa5s.th', color='#1e293b'))
        self.btn_view_table.setIconSize(QSize(12, 12))
        self.btn_view_table.setStyleSheet(self._view_btn_style())
        self.btn_view_table.clicked.connect(lambda: self._set_view_mode("tableau"))
        tb_layout.addWidget(self.btn_view_table)
        
        # ✅ Vue Carte
        self.btn_view_card = QPushButton("  VUE CARTE")
        self.btn_view_card.setCheckable(True)
        self.btn_view_card.setChecked(True)
        self.btn_view_card.setIcon(qta.icon('fa5s.th-large', color='#1e293b'))
        self.btn_view_card.setIconSize(QSize(12, 12))
        self.btn_view_card.setStyleSheet(self._view_btn_style())
        self.btn_view_card.clicked.connect(lambda: self._set_view_mode("carte"))
        tb_layout.addWidget(self.btn_view_card)
        
        layout.addWidget(toolbar)
        
        # ─── Vue container ───
        self.view_container = QWidget()
        self.view_layout = QVBoxLayout(self.view_container)
        self.view_layout.setContentsMargins(0, 0, 0, 0)
        self.view_layout.setSpacing(12)
        
        # Cartes
        self.cards_container = QWidget()
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        self.cards_grid.setSpacing(14)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Code", "Libellé", "BIC/SWIFT", "Pays", "Téléphone", "Email", "Statut"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(52)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_table_context_menu)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px 12px;
                font-size: 12px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background-color: #e8f0fe;
                color: #1e293b;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px;
                font-weight: 600;
                font-size: 11px;
                color: #64748b;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        self.table.hide()
        
        self.view_layout.addWidget(self.cards_container)
        self.view_layout.addWidget(self.table)
        
        layout.addWidget(self.view_container)
        
        # ─── Pagination ───
        pagination = QFrame()
        pagination.setStyleSheet("background: transparent; border: none;")
        pg_layout = QHBoxLayout(pagination)
        pg_layout.setContentsMargins(0, 8, 0, 8)
        
        self.lbl_pagination = QLabel("Affichage de 0-0 sur 0 banques")
        self.lbl_pagination.setStyleSheet("color: #64748b; font-size: 12px;")
        pg_layout.addWidget(self.lbl_pagination)
        
        pg_layout.addStretch()
        
        # ✅ Boutons pagination avec icônes
        self.btn_first = QPushButton()
        self.btn_first.setIcon(qta.icon('fa5s.step-backward', color='#64748b'))
        self.btn_first.setIconSize(QSize(10, 10))
        self.btn_first.setStyleSheet(self._pagination_btn_style())
        self.btn_first.clicked.connect(lambda: self._go_to_page(1))
        pg_layout.addWidget(self.btn_first)
        
        self.btn_prev = QPushButton()
        self.btn_prev.setIcon(qta.icon('fa5s.chevron-left', color='#64748b'))
        self.btn_prev.setIconSize(QSize(10, 10))
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
        
        self.btn_next = QPushButton()
        self.btn_next.setIcon(qta.icon('fa5s.chevron-right', color='#64748b'))
        self.btn_next.setIconSize(QSize(10, 10))
        self.btn_next.setStyleSheet(self._pagination_btn_style())
        self.btn_next.clicked.connect(lambda: self._go_to_page(self._current_page + 1))
        pg_layout.addWidget(self.btn_next)
        
        self.btn_last = QPushButton()
        self.btn_last.setIcon(qta.icon('fa5s.step-forward', color='#64748b'))
        self.btn_last.setIconSize(QSize(10, 10))
        self.btn_last.setStyleSheet(self._pagination_btn_style())
        self.btn_last.clicked.connect(lambda: self._go_to_page(99999))
        pg_layout.addWidget(self.btn_last)
        
        layout.addWidget(pagination)
        
        layout.addStretch()
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)
    
    # ─── Styles ───
    
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
                text-align: left;
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
                min-width: 90px;
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
                text-align: left;
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
    
    def _make_kpi_card(self, icon_name: str, value: str, title: str, subtitle: str,
                       color: str, show_progress: bool = False, pct: int = 0):
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
        
        # ✅ Icône FontAwesome
        icon_c = QFrame()
        icon_c.setFixedSize(52, 52)
        icon_c.setStyleSheet(f"background-color: {color}1A; border-radius: 10px;")
        ic_layout = QVBoxLayout(icon_c)
        ic_layout.setContentsMargins(0, 0, 0, 0)
        
        ic_lbl = QLabel()
        ic_lbl.setPixmap(qta.icon(icon_name, color=color).pixmap(QSize(24, 24)))
        ic_lbl.setAlignment(Qt.AlignCenter)
        ic_lbl.setStyleSheet("background: transparent;")
        ic_layout.addWidget(ic_lbl)
        layout.addWidget(icon_c)
        
        # Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 12px; color: #64748b; font-weight: 500;")
        text_layout.addWidget(title_lbl)
        
        line = QHBoxLayout()
        line.setSpacing(8)
        
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet("font-size: 26px; font-weight: bold; color: #1e293b;")
        line.addWidget(value_lbl)
        
        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet("font-size: 10px; color: #64748b;")
            line.addWidget(sub)
        
        line.addStretch()
        text_layout.addLayout(line)
        
        if show_progress:
            pb = QFrame()
            pb.setFixedHeight(6)
            pb.setStyleSheet("background-color: #e2e8f0; border-radius: 3px;")
            pb_layout = QHBoxLayout(pb)
            pb_layout.setContentsMargins(0, 0, 0, 0)
            
            fill = QFrame()
            fill.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
            fill.setFixedWidth(int(200 * pct / 100))
            pb_layout.addWidget(fill)
            pb_layout.addStretch()
            
            text_layout.addWidget(pb)
        
        layout.addLayout(text_layout, 1)
        
        card.value_label = value_lbl
        return card
    
    # ─── Chargement ───
    
    def load_data(self):
        try:
            banques = self.reglement_controller.get_banques()
            self._banques = banques
            
            try:
                comptes = self.reglement_controller.get_comptes_bancaires(actifs_only=False)
            except Exception:
                comptes = []
            
            for b in banques:
                b['_comptes'] = [c for c in comptes if c.get('banque') == b.get('id')]
                b['_nb_comptes'] = len(b['_comptes'])
                b['_nb_actifs'] = sum(1 for c in b['_comptes'] if c.get('est_actif'))
            
            self._update_kpis(banques)
            self._populate_filters(banques)
            self._apply_filters()
        except Exception as e:
            print(f"❌ Erreur chargement banques: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les banques: {e}")
    
    def _update_kpis(self, banques):
        total = len(banques)
        actives = sum(1 for b in banques if b.get('est_actif'))
        pays = set(b.get('pays') for b in banques if b.get('pays'))
        nb_pays = len(pays)
        
        self.kpi_total.value_label.setText(str(total))
        self.kpi_actives.value_label.setText(str(actives))
        self.kpi_pays.value_label.setText(str(nb_pays))
    
    def _populate_filters(self, banques):
        self.filter_pays.blockSignals(True)
        current_pays = self.filter_pays.currentData()
        self.filter_pays.clear()
        self.filter_pays.addItem("Pays", None)
        pays_set = sorted(set(b.get('pays') for b in banques if b.get('pays')))
        for p in pays_set:
            self.filter_pays.addItem(p, p)
        for i in range(self.filter_pays.count()):
            if self.filter_pays.itemData(i) == current_pays:
                self.filter_pays.setCurrentIndex(i)
                break
        self.filter_pays.blockSignals(False)
    
    # ─── Filtres ───
    
    def _apply_filters(self):
        filtered = list(self._banques)
        
        search = self.search_input.text().strip().lower()
        if search:
            filtered = [
                b for b in filtered
                if search in (b.get('code_banque', '') or '').lower()
                or search in (b.get('libelle', '') or '').lower()
                or search in (b.get('bic_swift', '') or '').lower()
                or search in (b.get('pays', '') or '').lower()
            ]
        
        pays_f = self.filter_pays.currentData()
        if pays_f:
            filtered = [b for b in filtered if b.get('pays') == pays_f]
        
        statut_f = self.filter_statut.currentData()
        if statut_f is not None:
            filtered = [b for b in filtered if b.get('est_actif') == statut_f]
        
        self._filtered_banques = filtered
        self._current_page = 1
        self._render_current_view()
    
    # ─── Rendu ───
    
    def _set_view_mode(self, mode: str):
        self._view_mode = mode
        self.btn_view_table.setChecked(mode == "tableau")
        self.btn_view_card.setChecked(mode == "carte")
        self._render_current_view()
    
    def _render_current_view(self):
        if self._view_mode == "carte":
            self.cards_container.show()
            self.table.hide()
            self._render_cards()
        else:
            self.cards_container.hide()
            self.table.show()
            self._render_table()
        
        self._update_pagination()
    
    def _render_cards(self):
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        start = (self._current_page - 1) * self._per_page
        end = start + self._per_page
        page_banques = self._filtered_banques[start:end]
        
        if not page_banques:
            empty = QLabel("Aucune banque à afficher")
            empty.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 40px;")
            empty.setAlignment(Qt.AlignCenter)
            self.cards_grid.addWidget(empty, 0, 0, 1, 2)
            return
        
        for i, b in enumerate(page_banques):
            card = BanqueCard(
                b,
                nb_comptes=b.get('_nb_comptes', 0),
                nb_actifs=b.get('_nb_actifs', 0),
            )
            card.edit_requested.connect(self._on_edit_banque)
            card.delete_requested.connect(self._on_delete_banque)
            card.view_requested.connect(self._on_view_banque)
            card.comptes_requested.connect(self._on_view_comptes)
            card.context_menu_requested.connect(self._show_card_context_menu)
            
            row = i // 2
            col = i % 2
            self.cards_grid.addWidget(card, row, col)
    
    def _render_table(self):
        start = (self._current_page - 1) * self._per_page
        end = start + self._per_page
        page_banques = self._filtered_banques[start:end]
        
        self.table.setRowCount(len(page_banques))
        
        for i, b in enumerate(page_banques):
            code_item = QTableWidgetItem(b.get('code_banque', ''))
            code_item.setData(Qt.UserRole, b)
            self.table.setItem(i, 0, code_item)
            
            self.table.setItem(i, 1, QTableWidgetItem(b.get('libelle', '')))
            self.table.setItem(i, 2, QTableWidgetItem(b.get('bic_swift', '') or '—'))
            self.table.setItem(i, 3, QTableWidgetItem(b.get('pays', '') or '—'))
            self.table.setItem(i, 4, QTableWidgetItem(b.get('telephone', '') or '—'))
            self.table.setItem(i, 5, QTableWidgetItem(b.get('email', '') or '—'))
            
            actif = b.get('est_actif', True)
            statut_item = QTableWidgetItem("Actif" if actif else "Inactif")
            statut_item.setBackground(QColor('#dcfce7' if actif else '#fee2e2'))
            statut_item.setForeground(QColor('#166534' if actif else '#991b1b'))
            statut_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 6, statut_item)
    
    def _update_pagination(self):
        total = len(self._filtered_banques)
        start = (self._current_page - 1) * self._per_page + 1 if total > 0 else 0
        end = min(self._current_page * self._per_page, total)
        total_pages = max(1, (total + self._per_page - 1) // self._per_page)
        
        self.lbl_pagination.setText(f"Affichage de {start}-{end} sur {total} banques")
        self.btn_page.setText(str(self._current_page))
        
        self.btn_first.setEnabled(self._current_page > 1)
        self.btn_prev.setEnabled(self._current_page > 1)
        self.btn_next.setEnabled(self._current_page < total_pages)
        self.btn_last.setEnabled(self._current_page < total_pages)
    
    def _go_to_page(self, page: int):
        total_pages = max(1, (len(self._filtered_banques) + self._per_page - 1) // self._per_page)
        page = max(1, min(page, total_pages))
        if page != self._current_page:
            self._current_page = page
            self._render_current_view()
    
    # ─── Menu contextuel ───
    
    def _show_card_context_menu(self, banque: dict, global_pos):
        self._show_banque_context_menu(banque, global_pos)
    
    def _show_table_context_menu(self, pos):
        row = self.table.currentRow()
        if row < 0:
            return
        
        code_item = self.table.item(row, 0)
        if not code_item:
            return
        banque = code_item.data(Qt.UserRole)
        if not banque:
            return
        
        self._show_banque_context_menu(banque, self.table.viewport().mapToGlobal(pos))
    
    def _show_banque_context_menu(self, banque: dict, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px;
                min-width: 220px;
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
        
        # ✅ Actions avec icônes FontAwesome
        action_view = QAction(qta.icon('fa5s.eye', color='#64748b'), "  Voir les détails", self)
        action_view.triggered.connect(lambda: self._on_view_banque(banque))
        menu.addAction(action_view)
        
        action_comptes = QAction(qta.icon('fa5s.list', color='#8b5cf6'), "  Voir les comptes", self)
        action_comptes.triggered.connect(lambda: self._on_view_comptes(banque))
        menu.addAction(action_comptes)
        
        menu.addSeparator()
        
        if self._perm_ui.peut('referentiel', 'UPDATE'):
            action_edit = QAction(qta.icon('fa5s.edit', color='#f59e0b'), "  Modifier", self)
            action_edit.triggered.connect(lambda: self._on_edit_banque(banque))
            menu.addAction(action_edit)
        
        action_copy = QAction(qta.icon('fa5s.copy', color='#64748b'), "  Copier le code", self)
        action_copy.triggered.connect(lambda: self._copy_to_clipboard(banque.get('code_banque', '')))
        menu.addAction(action_copy)
        
        menu.addSeparator()
        
        if self._perm_ui.peut('referentiel', 'DELETE'):
            action_delete = QAction(qta.icon('fa5s.trash-alt', color='#ef4444'), "  Supprimer", self)
            action_delete.triggered.connect(lambda: self._on_delete_banque(banque))
            menu.addAction(action_delete)
        
        menu.exec(global_pos)
    
    # ─── Actions ───
    
    def _on_view_banque(self, banque: dict):
        QMessageBox.information(
            self, "Détails de la banque",
            f"<b>Code :</b> {banque.get('code_banque', 'N/A')}<br>"
            f"<b>Libellé :</b> {banque.get('libelle', 'N/A')}<br>"
            f"<b>Pays :</b> {banque.get('pays', '—')}<br>"
            f"<b>BIC/SWIFT :</b> {banque.get('bic_swift', '—')}<br>"
            f"<b>Téléphone :</b> {banque.get('telephone', '—')}<br>"
            f"<b>Email :</b> {banque.get('email', '—')}<br>"
            f"<b>Adresse :</b> {banque.get('adresse', '—')}<br>"
            f"<b>Comptes :</b> {banque.get('_nb_comptes', 0)} ({banque.get('_nb_actifs', 0)} actifs)"
        )
    
    def _on_view_comptes(self, banque: dict):
        comptes = banque.get('_comptes', [])
        
        if not comptes:
            QMessageBox.information(
                self, "Comptes",
                f"Aucun compte associé à {banque.get('libelle', 'cette banque')}."
            )
            return
        
        lines = [f"{banque.get('libelle')}\n"]
        for c in comptes:
            statut = "Actif" if c.get('est_actif') else "Inactif"
            lines.append(f"  • {c.get('code_banque', '')} — {c.get('libelle', '')} ({c.get('devise', '')}) [{statut}]")
        
        QMessageBox.information(self, "Comptes associés", "\n".join(lines))
    
    def _on_edit_banque(self, banque: dict):
        from addons.sinistres.views.banque_dialog import BanqueDialog
        dialog = BanqueDialog(
            reglement_controller=self.reglement_controller,
            user=self.user,
            banque_data=banque,
            parent=self,
        )
        dialog.banque_created.connect(self._on_banque_creee)
        dialog.exec()
    
    def _on_delete_banque(self, banque: dict):
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous vraiment supprimer la banque\n"
            f"« {banque.get('libelle', 'N/A')} » ?\n\n"
            f"⚠️ Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                QMessageBox.information(self, "Info", "Suppression à implémenter")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copié", f"'{text}' copié")
    
    def exporter_csv(self):
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exporter les banques",
            "banques.csv",
            "CSV (*.csv)"
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Code", "Libellé", "BIC/SWIFT", "Pays",
                                 "Téléphone", "Email", "Statut", "Nb comptes"])
                for b in self._filtered_banques:
                    writer.writerow([
                        b.get('code_banque', ''), b.get('libelle', ''),
                        b.get('bic_swift', ''), b.get('pays', ''),
                        b.get('telephone', ''), b.get('email', ''),
                        "Actif" if b.get('est_actif') else "Inactif",
                        b.get('_nb_comptes', 0),
                    ])
            QMessageBox.information(self, "Export", f"{len(self._filtered_banques)} banques exportées")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    def ouvrir_parametres_import(self):
        QMessageBox.information(
            self, "Paramètres d'import",
            "Configuration des paramètres d'import de banques (à implémenter)."
        )
    
    def ouvrir_dialogue_creation(self):
        from addons.sinistres.views.banque_dialog import BanqueDialog
        dialog = BanqueDialog(
            reglement_controller=self.reglement_controller,
            user=self.user,
            banque_data=None,
            parent=self,
        )
        dialog.banque_created.connect(self._on_banque_creee)
        dialog.exec()
    
    def _on_banque_creee(self, data: dict):
        self.load_data()


# class BanquesTab(QWidget):
#     """Onglet de gestion des banques - Style carte + tableau"""
    
#     def __init__(self, reglement_controller, user):
#         super().__init__()
#         self.reglement_controller = reglement_controller
#         self.user = user
#         self._banques = []
#         self._filtered_banques = []
#         self._view_mode = "carte"  # "carte" ou "tableau"
#         self._current_page = 1
#         self._per_page = 6
        
#         from addons.sinistres.services.permission_service import PermissionService
#         from addons.sinistres.security.permissions_helper import PermissionsUI
#         self._perm_ui = PermissionsUI(self.user, PermissionService())
        
#         self.setup_ui()
#         self.load_data()
    
#     def setup_ui(self):
#         outer_layout = QVBoxLayout(self)
#         outer_layout.setContentsMargins(0, 0, 0, 0)
#         outer_layout.setSpacing(0)
        
#         scroll = QScrollArea()
#         scroll.setWidgetResizable(True)
#         scroll.setStyleSheet("""
#             QScrollArea { border: none; background: transparent; }
#             QScrollArea > QWidget > QWidget { background: transparent; }
#         """)
        
#         content = QWidget()
#         content.setStyleSheet("background-color: #f8fafc;")
#         layout = QVBoxLayout(content)
#         layout.setContentsMargins(20, 18, 20, 18)
#         layout.setSpacing(14)
        
#         # ============================================================
#         # LIGNE 1 : KPI CARDS (3 cards)
#         # ============================================================
#         kpi_row = QHBoxLayout()
#         kpi_row.setSpacing(12)
        
#         self.kpi_total = self._make_kpi_card("🏦", "8", "Total de Banques", "↑ 2 vs Dernier mois", "#1a73e8")
#         kpi_row.addWidget(self.kpi_total)
        
#         self.kpi_actives = self._make_kpi_card("✅", "6", "Banques Actives", "Actives vs En cours", "#22c55e", show_progress=True, pct=75)
#         kpi_row.addWidget(self.kpi_actives)
        
#         self.kpi_pays = self._make_kpi_card("🌍", "4", "Pays d'Opération", "Afrique: 4 · Caraïbes: 0 · Pérou: 0", "#3b82f6")
#         kpi_row.addWidget(self.kpi_pays)
        
#         layout.addLayout(kpi_row)
        
#         # ============================================================
#         # LIGNE 2 : BARRE D'OUTILS
#         # ============================================================
#         toolbar = QFrame()
#         toolbar.setStyleSheet("""
#             QFrame {
#                 background-color: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 10px;
#             }
#         """)
#         tb_layout = QHBoxLayout(toolbar)
#         tb_layout.setContentsMargins(12, 10, 12, 10)
#         tb_layout.setSpacing(8)
        
#         # Bouton Nouvelle banque
#         self.btn_nouvelle = QPushButton("➕  Nouvelle banque")
#         self.btn_nouvelle.setStyleSheet("""
#             QPushButton {
#                 background-color: #1a73e8;
#                 color: white;
#                 padding: 8px 16px;
#                 border-radius: 8px;
#                 font-weight: 600;
#                 font-size: 12px;
#                 border: none;
#             }
#             QPushButton:hover { background-color: #1557b0; }
#         """)
#         self.btn_nouvelle.setCursor(Qt.PointingHandCursor)
#         self.btn_nouvelle.clicked.connect(self.ouvrir_dialogue_creation)
#         if not self._perm_ui.peut('referentiel', 'CREATE'):
#             self.btn_nouvelle.hide()
#         tb_layout.addWidget(self.btn_nouvelle)
        
#         # Bouton Rafraîchir
#         self.btn_refresh = QPushButton("🔄  Rafraîchir")
#         self.btn_refresh.setStyleSheet(self._toolbar_btn_style())
#         self.btn_refresh.clicked.connect(self.load_data)
#         tb_layout.addWidget(self.btn_refresh)
        
#         # Bouton Exporter
#         self.btn_export = QPushButton("⬇️  Exporter Données (CSV)")
#         self.btn_export.setStyleSheet(self._toolbar_btn_style())
#         self.btn_export.clicked.connect(self.exporter_csv)
#         tb_layout.addWidget(self.btn_export)
        
#         # Bouton Paramètres Import
#         self.btn_import = QPushButton("⚙️  Paramètres Import")
#         self.btn_import.setStyleSheet(self._toolbar_btn_style())
#         self.btn_import.clicked.connect(self.ouvrir_parametres_import)
#         tb_layout.addWidget(self.btn_import)
        
#         # Recherche
#         self.search_input = QLineEdit()
#         self.search_input.setPlaceholderText("🔍  Recherche...")
#         self.search_input.setStyleSheet("""
#             QLineEdit {
#                 background-color: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 8px 12px;
#                 font-size: 12px;
#                 min-width: 180px;
#             }
#             QLineEdit:focus { border: 2px solid #1a73e8; }
#         """)
#         self.search_input.textChanged.connect(self._apply_filters)
#         tb_layout.addWidget(self.search_input, 1)
        
#         # Filtre Pays
#         self.filter_pays = QComboBox()
#         self.filter_pays.addItem("Pays", None)
#         self.filter_pays.setStyleSheet(self._combo_style())
#         self.filter_pays.currentIndexChanged.connect(self._apply_filters)
#         tb_layout.addWidget(self.filter_pays)
        
#         # Filtre Statut
#         self.filter_statut = QComboBox()
#         self.filter_statut.addItem("Statut", None)
#         self.filter_statut.addItem("Actif", True)
#         self.filter_statut.addItem("Inactif", False)
#         self.filter_statut.setStyleSheet(self._combo_style())
#         self.filter_statut.currentIndexChanged.connect(self._apply_filters)
#         tb_layout.addWidget(self.filter_statut)
        
#         # Vue Tableau
#         self.btn_view_table = QPushButton("⊞  VUE TABLEAU")
#         self.btn_view_table.setCheckable(True)
#         self.btn_view_table.setStyleSheet(self._view_btn_style())
#         self.btn_view_table.clicked.connect(lambda: self._set_view_mode("tableau"))
#         tb_layout.addWidget(self.btn_view_table)
        
#         # Vue Carte
#         self.btn_view_card = QPushButton("🗺  VUE CARTE")
#         self.btn_view_card.setCheckable(True)
#         self.btn_view_card.setChecked(True)
#         self.btn_view_card.setStyleSheet(self._view_btn_style())
#         self.btn_view_card.clicked.connect(lambda: self._set_view_mode("carte"))
#         tb_layout.addWidget(self.btn_view_card)
        
#         layout.addWidget(toolbar)
        
#         # ============================================================
#         # LIGNE 3 : CONTENEUR (cartes OU tableau)
#         # ============================================================
#         self.view_container = QWidget()
#         self.view_layout = QVBoxLayout(self.view_container)
#         self.view_layout.setContentsMargins(0, 0, 0, 0)
#         self.view_layout.setSpacing(12)
        
#         # --- Vue CARTES ---
#         self.cards_container = QWidget()
#         self.cards_grid = QGridLayout(self.cards_container)
#         self.cards_grid.setContentsMargins(0, 0, 0, 0)
#         self.cards_grid.setSpacing(14)
        
#         # --- Vue TABLEAU ---
#         self.table = QTableWidget()
#         self.table.setColumnCount(7)
#         self.table.setHorizontalHeaderLabels([
#             "Code", "Libellé", "BIC/SWIFT", "Pays", "Téléphone", "Email", "Statut"
#         ])
#         self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         self.table.setAlternatingRowColors(True)
#         self.table.setSelectionBehavior(QTableWidget.SelectRows)
#         self.table.setSelectionMode(QTableWidget.SingleSelection)
#         self.table.setEditTriggers(QTableWidget.NoEditTriggers)
#         self.table.verticalHeader().setDefaultSectionSize(48)
#         self.table.verticalHeader().setVisible(False)
#         self.table.setContextMenuPolicy(Qt.CustomContextMenu)
#         self.table.customContextMenuRequested.connect(self._show_table_context_menu)
#         self.table.setStyleSheet("""
#             QTableWidget {
#                 border: 1px solid #e2e8f0;
#                 border-radius: 10px;
#                 background-color: white;
#             }
#             QTableWidget::item {
#                 padding: 8px 12px;
#                 font-size: 12px;
#                 border-bottom: 1px solid #f1f5f9;
#             }
#             QTableWidget::item:selected {
#                 background-color: #e8f0fe;
#                 color: #1e293b;
#             }
#             QHeaderView::section {
#                 background-color: #f8fafc;
#                 padding: 12px;
#                 font-weight: 600;
#                 font-size: 11px;
#                 color: #64748b;
#                 border: none;
#                 border-bottom: 1px solid #e2e8f0;
#             }
#         """)
#         self.table.hide()
        
#         self.view_layout.addWidget(self.cards_container)
#         self.view_layout.addWidget(self.table)
        
#         layout.addWidget(self.view_container)
        
#         # ============================================================
#         # LIGNE 4 : PAGINATION
#         # ============================================================
#         pagination = QFrame()
#         pagination.setStyleSheet("""
#             QFrame {
#                 background-color: transparent;
#                 border: none;
#             }
#         """)
#         pg_layout = QHBoxLayout(pagination)
#         pg_layout.setContentsMargins(0, 8, 0, 8)
        
#         self.lbl_pagination = QLabel("Affichage de 0-0 sur 0 banques")
#         self.lbl_pagination.setStyleSheet("color: #64748b; font-size: 12px;")
#         pg_layout.addWidget(self.lbl_pagination)
        
#         pg_layout.addStretch()
        
#         self.btn_first = QPushButton("⏮")
#         self.btn_first.setStyleSheet(self._pagination_btn_style())
#         self.btn_first.clicked.connect(lambda: self._go_to_page(1))
#         pg_layout.addWidget(self.btn_first)
        
#         self.btn_prev = QPushButton("◀")
#         self.btn_prev.setStyleSheet(self._pagination_btn_style())
#         self.btn_prev.clicked.connect(lambda: self._go_to_page(self._current_page - 1))
#         pg_layout.addWidget(self.btn_prev)
        
#         self.btn_page = QPushButton("1")
#         self.btn_page.setStyleSheet("""
#             QPushButton {
#                 background-color: #e8f0fe;
#                 border: 1px solid #1a73e8;
#                 border-radius: 6px;
#                 padding: 6px 14px;
#                 color: #1a73e8;
#                 font-weight: bold;
#                 min-width: 32px;
#             }
#         """)
#         pg_layout.addWidget(self.btn_page)
        
#         self.btn_next = QPushButton("▶")
#         self.btn_next.setStyleSheet(self._pagination_btn_style())
#         self.btn_next.clicked.connect(lambda: self._go_to_page(self._current_page + 1))
#         pg_layout.addWidget(self.btn_next)
        
#         self.btn_last = QPushButton("⏭")
#         self.btn_last.setStyleSheet(self._pagination_btn_style())
#         self.btn_last.clicked.connect(lambda: self._go_to_page(99999))
#         pg_layout.addWidget(self.btn_last)
        
#         layout.addWidget(pagination)
        
#         layout.addStretch()
#         scroll.setWidget(content)
#         outer_layout.addWidget(scroll)
    
#     # ============================================================
#     # STYLES
#     # ============================================================
    
#     def _toolbar_btn_style(self):
#         return """
#             QPushButton {
#                 background-color: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 8px 14px;
#                 color: #1e293b;
#                 font-weight: 600;
#                 font-size: 12px;
#             }
#             QPushButton:hover { background-color: #f1f5f9; }
#         """
    
#     def _combo_style(self):
#         return """
#             QComboBox {
#                 background-color: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 8px 12px;
#                 font-size: 12px;
#                 min-width: 90px;
#             }
#             QComboBox:focus { border: 2px solid #1a73e8; }
#             QComboBox::drop-down { border: none; width: 22px; }
#         """
    
#     def _view_btn_style(self):
#         return """
#             QPushButton {
#                 background-color: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 8px 14px;
#                 color: #1e293b;
#                 font-weight: 600;
#                 font-size: 12px;
#             }
#             QPushButton:hover { background-color: #f1f5f9; }
#             QPushButton:checked {
#                 background-color: #1a73e8;
#                 color: white;
#                 border: 1px solid #1a73e8;
#             }
#         """
    
#     def _pagination_btn_style(self):
#         return """
#             QPushButton {
#                 background-color: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 6px;
#                 padding: 6px 12px;
#                 color: #64748b;
#                 font-weight: bold;
#                 min-width: 32px;
#             }
#             QPushButton:hover { background-color: #f1f5f9; }
#             QPushButton:disabled { color: #cbd5e1; }
#         """
    
#     def _make_kpi_card(self, icon: str, value: str, title: str, subtitle: str,
#                        color: str, show_progress: bool = False, pct: int = 0):
#         card = QFrame()
#         card.setStyleSheet("""
#             QFrame {
#                 background-color: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 12px;
#             }
#         """)
#         card.setMinimumHeight(100)
        
#         layout = QHBoxLayout(card)
#         layout.setContentsMargins(16, 14, 16, 14)
#         layout.setSpacing(14)
        
#         # Icône
#         icon_c = QFrame()
#         icon_c.setFixedSize(52, 52)
#         icon_c.setStyleSheet(f"background-color: {color}1A; border-radius: 10px;")
#         ic_layout = QVBoxLayout(icon_c)
#         ic_layout.setContentsMargins(0, 0, 0, 0)
#         ic_lbl = QLabel(icon)
#         ic_lbl.setStyleSheet(f"font-size: 24px; color: {color}; background: transparent;")
#         ic_lbl.setAlignment(Qt.AlignCenter)
#         ic_layout.addWidget(ic_lbl)
#         layout.addWidget(icon_c)
        
#         # Texte
#         text_layout = QVBoxLayout()
#         text_layout.setSpacing(2)
        
#         title_lbl = QLabel(title)
#         title_lbl.setStyleSheet("font-size: 12px; color: #64748b; font-weight: 500;")
#         text_layout.addWidget(title_lbl)
        
#         # Ligne valeur + subtitle
#         line = QHBoxLayout()
#         line.setSpacing(8)
        
#         value_lbl = QLabel(value)
#         value_lbl.setStyleSheet("font-size: 26px; font-weight: bold; color: #1e293b;")
#         line.addWidget(value_lbl)
        
#         if subtitle:
#             sub = QLabel(subtitle)
#             sub.setStyleSheet("font-size: 10px; color: #64748b;")
#             line.addWidget(sub)
        
#         line.addStretch()
#         text_layout.addLayout(line)
        
#         if show_progress:
#             pb = QFrame()
#             pb.setFixedHeight(6)
#             pb.setStyleSheet("background-color: #e2e8f0; border-radius: 3px;")
#             pb_layout = QHBoxLayout(pb)
#             pb_layout.setContentsMargins(0, 0, 0, 0)
            
#             fill = QFrame()
#             fill.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
#             fill.setFixedWidth(int(200 * pct / 100))
#             pb_layout.addWidget(fill)
#             pb_layout.addStretch()
            
#             text_layout.addWidget(pb)
        
#         layout.addLayout(text_layout, 1)
        
#         # Retourne (card, value_label) pour mise à jour
#         card.value_label = value_lbl
#         return card
    
#     # ============================================================
#     # CHARGEMENT DES DONNÉES
#     # ============================================================
    
#     def load_data(self):
#         try:
#             banques = self.reglement_controller.get_banques()
#             self._banques = banques
            
#             # Charger les comptes pour calculer les stats
#             try:
#                 comptes = self.reglement_controller.get_comptes_bancaires(actifs_only=False)
#             except Exception:
#                 comptes = []
            
#             # Associer comptes → banque
#             for b in banques:
#                 b['_comptes'] = [c for c in comptes if c.get('banque') == b.get('id')]
#                 b['_nb_comptes'] = len(b['_comptes'])
#                 b['_nb_actifs'] = sum(1 for c in b['_comptes'] if c.get('est_actif'))
            
#             self._update_kpis(banques)
#             self._populate_filters(banques)
#             self._apply_filters()
#         except Exception as e:
#             print(f"❌ Erreur chargement banques: {e}")
#             import traceback
#             traceback.print_exc()
#             QMessageBox.warning(self, "Erreur", f"Impossible de charger les banques: {e}")
    
#     def _update_kpis(self, banques):
#         total = len(banques)
#         actives = sum(1 for b in banques if b.get('est_actif'))
        
#         # Pays uniques
#         pays = set(b.get('pays') for b in banques if b.get('pays'))
#         nb_pays = len(pays)
        
#         # Mettre à jour les valeurs
#         self.kpi_total.value_label.setText(str(total))
#         self.kpi_actives.value_label.setText(str(actives))
#         self.kpi_pays.value_label.setText(str(nb_pays))
    
#     def _populate_filters(self, banques):
#         # Pays
#         self.filter_pays.blockSignals(True)
#         current_pays = self.filter_pays.currentData()
#         self.filter_pays.clear()
#         self.filter_pays.addItem("Pays", None)
#         pays_set = sorted(set(b.get('pays') for b in banques if b.get('pays')))
#         for p in pays_set:
#             self.filter_pays.addItem(p, p)
#         for i in range(self.filter_pays.count()):
#             if self.filter_pays.itemData(i) == current_pays:
#                 self.filter_pays.setCurrentIndex(i)
#                 break
#         self.filter_pays.blockSignals(False)
    
#     # ============================================================
#     # FILTRES
#     # ============================================================
    
#     def _apply_filters(self):
#         filtered = list(self._banques)
        
#         # Recherche
#         search = self.search_input.text().strip().lower()
#         if search:
#             filtered = [
#                 b for b in filtered
#                 if search in (b.get('code_banque', '') or '').lower()
#                 or search in (b.get('libelle', '') or '').lower()
#                 or search in (b.get('bic_swift', '') or '').lower()
#                 or search in (b.get('pays', '') or '').lower()
#             ]
        
#         # Filtre pays
#         pays_f = self.filter_pays.currentData()
#         if pays_f:
#             filtered = [b for b in filtered if b.get('pays') == pays_f]
        
#         # Filtre statut
#         statut_f = self.filter_statut.currentData()
#         if statut_f is not None:
#             filtered = [b for b in filtered if b.get('est_actif') == statut_f]
        
#         self._filtered_banques = filtered
#         self._current_page = 1
#         self._render_current_view()
    
#     # ============================================================
#     # RENDU
#     # ============================================================
    
#     def _set_view_mode(self, mode: str):
#         self._view_mode = mode
#         self.btn_view_table.setChecked(mode == "tableau")
#         self.btn_view_card.setChecked(mode == "carte")
#         self._render_current_view()
    
#     def _render_current_view(self):
#         if self._view_mode == "carte":
#             self.cards_container.show()
#             self.table.hide()
#             self._render_cards()
#         else:
#             self.cards_container.hide()
#             self.table.show()
#             self._render_table()
        
#         self._update_pagination()
    
#     def _render_cards(self):
#         # Vider la grille
#         while self.cards_grid.count():
#             item = self.cards_grid.takeAt(0)
#             if item.widget():
#                 item.widget().deleteLater()
        
#         # Pagination
#         start = (self._current_page - 1) * self._per_page
#         end = start + self._per_page
#         page_banques = self._filtered_banques[start:end]
        
#         if not page_banques:
#             empty = QLabel("Aucune banque à afficher")
#             empty.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 40px;")
#             empty.setAlignment(Qt.AlignCenter)
#             self.cards_grid.addWidget(empty, 0, 0, 1, 2)
#             return
        
#         # Grille 2 colonnes
#         for i, b in enumerate(page_banques):
#             card = BanqueCard(
#                 b,
#                 nb_comptes=b.get('_nb_comptes', 0),
#                 nb_actifs=b.get('_nb_actifs', 0),
#             )
#             card.edit_requested.connect(self._on_edit_banque)
#             card.delete_requested.connect(self._on_delete_banque)
#             card.view_requested.connect(self._on_view_banque)
#             card.comptes_requested.connect(self._on_view_comptes)
#             card.context_menu_requested.connect(self._show_card_context_menu)
            
#             row = i // 2
#             col = i % 2
#             self.cards_grid.addWidget(card, row, col)
    
#     def _render_table(self):
#         start = (self._current_page - 1) * self._per_page
#         end = start + self._per_page
#         page_banques = self._filtered_banques[start:end]
        
#         self.table.setRowCount(len(page_banques))
        
#         for i, b in enumerate(page_banques):
#             code_item = QTableWidgetItem(b.get('code_banque', ''))
#             code_item.setData(Qt.UserRole, b)
#             self.table.setItem(i, 0, code_item)
            
#             self.table.setItem(i, 1, QTableWidgetItem(b.get('libelle', '')))
#             self.table.setItem(i, 2, QTableWidgetItem(b.get('bic_swift', '') or '—'))
#             self.table.setItem(i, 3, QTableWidgetItem(b.get('pays', '') or '—'))
#             self.table.setItem(i, 4, QTableWidgetItem(b.get('telephone', '') or '—'))
#             self.table.setItem(i, 5, QTableWidgetItem(b.get('email', '') or '—'))
            
#             actif = b.get('est_actif', True)
#             statut_item = QTableWidgetItem("✅ Actif" if actif else "❌ Inactif")
#             statut_item.setForeground(QColor('#22c55e' if actif else '#ef4444'))
#             self.table.setItem(i, 6, statut_item)
    
#     def _update_pagination(self):
#         total = len(self._filtered_banques)
#         start = (self._current_page - 1) * self._per_page + 1 if total > 0 else 0
#         end = min(self._current_page * self._per_page, total)
#         total_pages = max(1, (total + self._per_page - 1) // self._per_page)
        
#         self.lbl_pagination.setText(f"Affichage de {start}-{end} sur {total} banques")
#         self.btn_page.setText(str(self._current_page))
        
#         self.btn_first.setEnabled(self._current_page > 1)
#         self.btn_prev.setEnabled(self._current_page > 1)
#         self.btn_next.setEnabled(self._current_page < total_pages)
#         self.btn_last.setEnabled(self._current_page < total_pages)
    
#     def _go_to_page(self, page: int):
#         total_pages = max(1, (len(self._filtered_banques) + self._per_page - 1) // self._per_page)
#         page = max(1, min(page, total_pages))
#         if page != self._current_page:
#             self._current_page = page
#             self._render_current_view()
    
#     # ============================================================
#     # MENU CONTEXTUEL
#     # ============================================================
    
#     def _show_card_context_menu(self, banque: dict, global_pos):
#         """Menu contextuel sur une carte"""
#         self._show_banque_context_menu(banque, global_pos)
    
#     def _show_table_context_menu(self, pos):
#         """Menu contextuel sur le tableau"""
#         row = self.table.currentRow()
#         if row < 0:
#             return
        
#         code_item = self.table.item(row, 0)
#         if not code_item:
#             return
#         banque = code_item.data(Qt.UserRole)
#         if not banque:
#             return
        
#         self._show_banque_context_menu(banque, self.table.viewport().mapToGlobal(pos))
    
#     def _show_banque_context_menu(self, banque: dict, global_pos):
#         """Affiche le menu contextuel d'une banque"""
#         menu = QMenu(self)
#         menu.setStyleSheet("""
#             QMenu {
#                 background-color: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 padding: 6px;
#             }
#             QMenu::item {
#                 padding: 8px 20px 8px 14px;
#                 border-radius: 5px;
#                 font-size: 12px;
#                 color: #1e293b;
#             }
#             QMenu::item:selected {
#                 background-color: #f1f5f9;
#                 color: #1a73e8;
#             }
#             QMenu::separator {
#                 height: 1px;
#                 background-color: #e2e8f0;
#                 margin: 4px 8px;
#             }
#         """)
        
#         # Voir détails
#         action_view = QAction("👁️  Voir les détails", self)
#         action_view.triggered.connect(lambda: self._on_view_banque(banque))
#         menu.addAction(action_view)
        
#         # Voir comptes
#         action_comptes = QAction("📋  Voir les comptes", self)
#         action_comptes.triggered.connect(lambda: self._on_view_comptes(banque))
#         menu.addAction(action_comptes)
        
#         menu.addSeparator()
        
#         # Modifier (permission)
#         if self._perm_ui.peut('referentiel', 'UPDATE'):
#             action_edit = QAction("✏️  Modifier", self)
#             action_edit.triggered.connect(lambda: self._on_edit_banque(banque))
#             menu.addAction(action_edit)
        
#         # Copier le code
#         action_copy = QAction("📋  Copier le code", self)
#         action_copy.triggered.connect(lambda: self._copy_to_clipboard(banque.get('code_banque', '')))
#         menu.addAction(action_copy)
        
#         menu.addSeparator()
        
#         # Supprimer (permission)
#         if self._perm_ui.peut('referentiel', 'DELETE'):
#             action_delete = QAction("🗑️  Supprimer", self)
#             action_delete.triggered.connect(lambda: self._on_delete_banque(banque))
#             menu.addAction(action_delete)
        
#         menu.exec(global_pos)
    
#     # ============================================================
#     # ACTIONS
#     # ============================================================
    
#     def _on_view_banque(self, banque: dict):
#         QMessageBox.information(
#             self, "Détails de la banque",
#             f"🏦 Code: {banque.get('code_banque', 'N/A')}\n"
#             f"📛 Libellé: {banque.get('libelle', 'N/A')}\n"
#             f"🌍 Pays: {banque.get('pays', '—')}\n"
#             f"🔢 BIC/SWIFT: {banque.get('bic_swift', '—')}\n"
#             f"📞 Téléphone: {banque.get('telephone', '—')}\n"
#             f"✉️ Email: {banque.get('email', '—')}\n"
#             f"📍 Adresse: {banque.get('adresse', '—')}\n"
#             f"💼 Comptes: {banque.get('_nb_comptes', 0)} "
#             f"({banque.get('_nb_actifs', 0)} actifs)"
#         )
    
#     def _on_view_comptes(self, banque: dict):
#         """Affiche les comptes de la banque dans une modale"""
#         comptes = banque.get('_comptes', [])
        
#         if not comptes:
#             QMessageBox.information(
#                 self, "Comptes",
#                 f"Aucun compte associé à {banque.get('libelle', 'cette banque')}."
#             )
#             return
        
#         # Construire le message
#         lines = [f"🏦 {banque.get('libelle')}\n"]
#         for c in comptes:
#             statut = "✅" if c.get('est_actif') else "❌"
#             lines.append(
#                 f"{statut} {c.get('code_banque', '')} — "
#                 f"{c.get('libelle', '')} ({c.get('devise', '')})"
#             )
        
#         QMessageBox.information(self, "Comptes associés", "\n".join(lines))
    
#     def _on_edit_banque(self, banque: dict):
#         from addons.sinistres.views.banque_dialog import BanqueDialog
#         dialog = BanqueDialog(
#             reglement_controller=self.reglement_controller,
#             user=self.user,
#             banque_data=banque,
#             parent=self,
#         )
#         dialog.banque_created.connect(self._on_banque_creee)
#         dialog.exec()
    
#     def _on_delete_banque(self, banque: dict):
#         reply = QMessageBox.question(
#             self, "Confirmation",
#             f"Voulez-vous vraiment supprimer la banque\n"
#             f"« {banque.get('libelle', 'N/A')} » ?\n\n"
#             f"⚠️ Cette action est irréversible.",
#             QMessageBox.Yes | QMessageBox.No
#         )
#         if reply == QMessageBox.Yes:
#             try:
#                 # TODO: appeler le service de suppression
#                 # self.reglement_controller.supprimer_banque(banque.get('id'))
#                 QMessageBox.information(self, "Info", "Suppression à implémenter")
#                 self.load_data()
#             except Exception as e:
#                 QMessageBox.critical(self, "Erreur", str(e))
    
#     def _copy_to_clipboard(self, text: str):
#         from PySide6.QtWidgets import QApplication
#         QApplication.clipboard().setText(text)
#         QMessageBox.information(self, "Copié", f"✅ '{text}' copié")
    
#     def exporter_csv(self):
#         """Exporte la liste des banques en CSV"""
#         from PySide6.QtWidgets import QFileDialog
#         import csv
        
#         filepath, _ = QFileDialog.getSaveFileName(
#             self, "Exporter les banques",
#             "banques.csv",
#             "CSV (*.csv)"
#         )
#         if not filepath:
#             return
        
#         try:
#             with open(filepath, 'w', newline='', encoding='utf-8') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(["Code", "Libellé", "BIC/SWIFT", "Pays",
#                                  "Téléphone", "Email", "Statut", "Nb comptes"])
#                 for b in self._filtered_banques:
#                     writer.writerow([
#                         b.get('code_banque', ''), b.get('libelle', ''),
#                         b.get('bic_swift', ''), b.get('pays', ''),
#                         b.get('telephone', ''), b.get('email', ''),
#                         "Actif" if b.get('est_actif') else "Inactif",
#                         b.get('_nb_comptes', 0),
#                     ])
#             QMessageBox.information(self, "Export", f"✅ {len(self._filtered_banques)} banques exportées")
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
#     def ouvrir_parametres_import(self):
#         QMessageBox.information(
#             self, "Paramètres d'import",
#             "Configuration des paramètres d'import de banques (à implémenter)."
#         )
    
#     def ouvrir_dialogue_creation(self):
#         from addons.sinistres.views.banque_dialog import BanqueDialog
#         dialog = BanqueDialog(
#             reglement_controller=self.reglement_controller,
#             user=self.user,
#             banque_data=None,
#             parent=self,
#         )
#         dialog.banque_created.connect(self._on_banque_creee)
#         dialog.exec()
    
#     def _on_banque_creee(self, data: dict):
#         self.load_data()

# ============================================================
# WIDGET : CARTE COMPTE BANCAIRE
# ============================================================

class CompteBancaireCard(QFrame):
    """Carte d'un compte bancaire"""
    
    edit_requested = Signal(dict)
    delete_requested = Signal(dict)
    view_requested = Signal(dict)
    context_menu_requested = Signal(dict, QPointF)
    
    def __init__(self, compte: dict, banque_nom: str = "", parent=None):
        super().__init__(parent)
        self.compte = compte
        self.banque_nom = banque_nom
        self.setFixedWidth(380)
        self.setMinimumHeight(280)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        
        self.setStyleSheet("""
            CompteBancaireCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            CompteBancaireCard:hover {
                border: 1px solid #cbd5e1;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)
        
        # ============================================================
        # HEADER : Logo + Libellé + Statut
        # ============================================================
        header = QHBoxLayout()
        header.setSpacing(12)
        
        logo = QLabel("💳")
        logo.setFixedSize(48, 48)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            background-color: #1a73e8;
            color: white;
            border-radius: 10px;
            font-size: 22px;
        """)
        header.addWidget(logo)
        
        name_layout = QVBoxLayout()
        name_layout.setSpacing(2)
        
        libelle = QLabel(compte.get('libelle', 'Sans nom'))
        libelle.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b;")
        libelle.setWordWrap(True)
        name_layout.addWidget(libelle)
        
        banque_lbl = QLabel(f"🏦 {banque_nom or '—'}")
        banque_lbl.setStyleSheet("font-size: 10px; color: #64748b;")
        name_layout.addWidget(banque_lbl)
        
        header.addLayout(name_layout, 1)
        
        # Statut
        actif = compte.get('est_actif', True)
        statut_lbl = QLabel("✅ ACTIF" if actif else "❌ INACTIF")
        statut_lbl.setStyleSheet(f"""
            background-color: {'#dcfce7' if actif else '#fee2e2'};
            color: {'#166534' if actif else '#991b1b'};
            padding: 4px 10px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        """)
        statut_lbl.setAlignment(Qt.AlignCenter)
        header.addWidget(statut_lbl)
        
        layout.addLayout(header)
        
        # ============================================================
        # ACTIONS ICÔNES
        # ============================================================
        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addStretch()
        
        for icon, tooltip, callback in [
            ("👁️", "Voir", lambda: self.view_requested.emit(self.compte)),
            ("✏️", "Modifier", lambda: self.edit_requested.emit(self.compte)),
            ("🗑️", "Supprimer", lambda: self.delete_requested.emit(self.compte)),
        ]:
            btn = QPushButton(icon)
            btn.setFixedSize(30, 30)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f1f5f9;
                    border: none;
                    border-radius: 15px;
                    font-size: 12px;
                }
                QPushButton:hover { background-color: #e2e8f0; }
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            actions.addWidget(btn)
        
        layout.addLayout(actions)
        
        # ============================================================
        # IBAN
        # ============================================================
        iban_layout = QVBoxLayout()
        iban_layout.setSpacing(2)
        iban_lbl = QLabel("N° Compte / IBAN")
        iban_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        iban_layout.addWidget(iban_lbl)
        
        iban_val = QLabel(compte.get('iban', '—'))
        iban_val.setStyleSheet("font-size: 12px; color: #1e293b; font-weight: 500;")
        iban_val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        iban_layout.addWidget(iban_val)
        layout.addLayout(iban_layout)
        
        # ============================================================
        # DEVISES + SOLDE
        # ============================================================
        solde_layout = QHBoxLayout()
        
        devise_layout = QVBoxLayout()
        devise_layout.setSpacing(2)
        devise_lbl = QLabel("Devise")
        devise_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        devise_layout.addWidget(devise_lbl)
        devise_val = QLabel(compte.get('devise', '—'))
        devise_val.setStyleSheet("font-size: 12px; color: #1e293b; font-weight: bold;")
        devise_layout.addWidget(devise_val)
        solde_layout.addLayout(devise_layout, 1)
        
        solde_v_layout = QVBoxLayout()
        solde_v_layout.setSpacing(2)
        solde_lbl = QLabel("Solde")
        solde_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        solde_v_layout.addWidget(solde_lbl)
        
        solde = compte.get('solde', 0) or 0
        solde_val = QLabel(f"{solde:,.0f} {compte.get('devise', '')}")
        solde_val.setStyleSheet("font-size: 13px; color: #1e293b; font-weight: bold;")
        solde_v_layout.addWidget(solde_val)
        solde_layout.addLayout(solde_v_layout, 1)
        
        layout.addLayout(solde_layout)
        
        # ============================================================
        # TITULAIRE
        # ============================================================
        titulaire_layout = QVBoxLayout()
        titulaire_layout.setSpacing(2)
        tit_lbl = QLabel("Titulaire")
        tit_lbl.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 600;")
        titulaire_layout.addWidget(tit_lbl)
        
        titulaire = compte.get('titulaire') or compte.get('personne') or '—'
        tit_val = QLabel(titulaire)
        tit_val.setStyleSheet("font-size: 12px; color: #1e293b;")
        titulaire_layout.addWidget(tit_val)
        
        layout.addLayout(titulaire_layout)
        
        # ============================================================
        # ALERTES (si présentes)
        # ============================================================
        alertes = compte.get('alertes', [])
        if alertes:
            alerte_frame = QFrame()
            alerte_frame.setStyleSheet("""
                QFrame {
                    background-color: #fef3c7;
                    border-radius: 6px;
                    border-left: 3px solid #f59e0b;
                }
            """)
            alerte_layout = QVBoxLayout(alerte_frame)
            alerte_layout.setContentsMargins(8, 6, 8, 6)
            for a in alertes[:2]:
                lbl = QLabel(f"⚠️ {a}")
                lbl.setStyleSheet("font-size: 10px; color: #92400e;")
                lbl.setWordWrap(True)
                alerte_layout.addWidget(lbl)
            layout.addWidget(alerte_frame)
    
    def _on_context_menu(self, pos):
        self.context_menu_requested.emit(self.compte, self.mapToGlobal(pos))

class ComptesBancairesTab(QWidget):
    """Onglet de gestion des comptes bancaires - Style capture"""
    
    def __init__(self, reglement_controller, user):
        super().__init__()
        self.reglement_controller = reglement_controller
        self.user = user
        self._comptes = []
        self._filtered_comptes = []
        self._banques_map = {}  # id → nom banque
        self._view_mode = "tableau"  # "tableau" ou "carte"
        self._current_page = 1
        self._per_page = 20
        
        from addons.sinistres.services.permission_service import PermissionService
        from addons.sinistres.security.permissions_helper import PermissionsUI
        self._perm_ui = PermissionsUI(self.user, PermissionService())
        
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
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)
        
        # ============================================================
        # LIGNE 1 : KPI CARDS (3 cards)
        # ============================================================
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        
        # --- Carte 1 : Total de Comptes ---
        self.kpi_total = self._make_kpi_card(
            "🏦", "24", "Total de Comptes",
            mini_chart=[
                ("Courant", "#3b82f6"),
                ("Épargne", "#22c55e"),
                ("Devise", "#f59e0b"),
            ]
        )
        kpi_row.addWidget(self.kpi_total, 1)
        
        # --- Carte 2 : Solde Total ---
        self.kpi_solde = self._make_kpi_card(
            "💵", "520,000,000 XAF", "Solde Total (XAF Équiv.)",
            show_progress_bar=True,
            progress_segments=[
                ("XAF", "#3b82f6"),
                ("EUR", "#22c55e"),
                ("USD", "#f59e0b"),
                ("GHS", "#a855f7"),
            ]
        )
        kpi_row.addWidget(self.kpi_solde, 1)
        
        # --- Carte 3 : Anomalies Récentes ---
        self.kpi_anomalies = self._make_anomalies_card()
        kpi_row.addWidget(self.kpi_anomalies, 1)
        
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
        
        # Bouton Nouveau compte
        self.btn_nouveau = QPushButton("➕  Nouveau compte")
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
        if not self._perm_ui.peut('referentiel', 'CREATE'):
            self.btn_nouveau.hide()
        tb_layout.addWidget(self.btn_nouveau)
        
        # Bouton Rafraîchir
        self.btn_refresh = QPushButton("🔄  Rafraîchir")
        self.btn_refresh.setStyleSheet(self._toolbar_btn_style())
        self.btn_refresh.clicked.connect(self.load_data)
        tb_layout.addWidget(self.btn_refresh)
        
        # Bouton Exporter
        self.btn_export = QPushButton("⬇️  Exporter Données (CSV)")
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
        
        # Filtre Devise
        self.filter_devise = QComboBox()
        self.filter_devise.addItem("Pays", None)  # placeholder
        self.filter_devise.setStyleSheet(self._combo_style())
        self.filter_devise.currentIndexChanged.connect(self._apply_filters)
        tb_layout.addWidget(self.filter_devise)
        
        # Filtre Statut
        self.filter_statut = QComboBox()
        self.filter_statut.addItem("Statut", None)
        self.filter_statut.addItem("Actif", True)
        self.filter_statut.addItem("Inactif", False)
        self.filter_statut.setStyleSheet(self._combo_style())
        self.filter_statut.currentIndexChanged.connect(self._apply_filters)
        tb_layout.addWidget(self.filter_statut)
        
        # Vue Tableau
        self.btn_view_table = QPushButton("⊞  VUE TABLEAU")
        self.btn_view_table.setCheckable(True)
        self.btn_view_table.setChecked(True)
        self.btn_view_table.setStyleSheet(self._view_btn_style())
        self.btn_view_table.clicked.connect(lambda: self._set_view_mode("tableau"))
        tb_layout.addWidget(self.btn_view_table)
        
        # Vue Carte
        self.btn_view_card = QPushButton("🗺  VUE CARTE")
        self.btn_view_card.setCheckable(True)
        self.btn_view_card.setStyleSheet(self._view_btn_style())
        self.btn_view_card.clicked.connect(lambda: self._set_view_mode("carte"))
        tb_layout.addWidget(self.btn_view_card)
        
        layout.addWidget(toolbar)
        
        # ============================================================
        # LIGNE 3 : CONTENEUR (tableau OU cartes)
        # ============================================================
        self.view_container = QWidget()
        self.view_layout = QVBoxLayout(self.view_container)
        self.view_layout.setContentsMargins(0, 0, 0, 0)
        self.view_layout.setSpacing(12)
        
        # --- Vue TABLEAU (avec panneau alertes) ---
        self.table_wrapper = QFrame()
        self.table_wrapper.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        tw_layout = QHBoxLayout(self.table_wrapper)
        tw_layout.setContentsMargins(0, 0, 0, 0)
        tw_layout.setSpacing(0)
        
        # -- Tableau principal --
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "☐", "Banque", "N° de Compte / IBAN", "Titulaire",
            "Devise", "Solde Actuel", "Dernier Mouvement", "Statut"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 40)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(80)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_table_context_menu)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                border-radius: 10px 0 0 10px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px 12px;
                font-size: 12px;
                border-bottom: 1px solid #f1f5f9;
                color: #1e293b;
            }
            QTableWidget::item:selected {
                background-color: #e8f0fe;
                color: #1e293b;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px;
                font-weight: 600;
                font-size: 11px;
                color: #64748b;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        tw_layout.addWidget(self.table, 3)
        
        # -- Panneau Alertes --
        self.alertes_panel = QFrame()
        self.alertes_panel.setFixedWidth(220)
        self.alertes_panel.setStyleSheet("""
            QFrame {
                background-color: #fef3c7;
                border: none;
                border-left: 1px solid #e2e8f0;
                border-radius: 0 10px 10px 0;
            }
        """)
        self.alertes_layout = QVBoxLayout(self.alertes_panel)
        self.alertes_layout.setContentsMargins(12, 12, 12, 12)
        self.alertes_layout.setSpacing(10)
        
        alertes_header = QLabel("Alertes de Compte & Tâches")
        alertes_header.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #92400e;
            padding-bottom: 6px;
            border-bottom: 1px solid #fde68a;
        """)
        alertes_header.setWordWrap(True)
        self.alertes_layout.addWidget(alertes_header)
        
        self.alertes_content = QVBoxLayout()
        self.alertes_content.setSpacing(8)
        self.alertes_layout.addLayout(self.alertes_content)
        self.alertes_layout.addStretch()
        
        tw_layout.addWidget(self.alertes_panel, 1)
        
        self.view_layout.addWidget(self.table_wrapper)
        
        # --- Vue CARTES ---
        self.cards_container = QWidget()
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        self.cards_grid.setSpacing(14)
        self.cards_container.hide()
        
        self.view_layout.addWidget(self.cards_container)
        
        layout.addWidget(self.view_container)
        
        # ============================================================
        # LIGNE 4 : PAGINATION
        # ============================================================
        pagination = QFrame()
        pagination.setStyleSheet("background: transparent; border: none;")
        pg_layout = QHBoxLayout(pagination)
        pg_layout.setContentsMargins(0, 8, 0, 8)
        
        pg_layout.addStretch()
        
        self.lbl_pagination = QLabel("Affichage de 0-0 sur 0 comptes")
        self.lbl_pagination.setStyleSheet("color: #64748b; font-size: 12px;")
        pg_layout.addWidget(self.lbl_pagination)
        
        pg_layout.addSpacing(20)
        
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
        
        layout.addStretch()
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
                min-width: 90px;
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
    
    def _make_kpi_card(self, icon: str, value: str, title: str,
                       mini_chart=None, show_progress_bar=False,
                       progress_segments=None):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        card.setMinimumHeight(110)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)
        
        # Icône
        icon_c = QFrame()
        icon_c.setFixedSize(56, 56)
        icon_c.setStyleSheet("background-color: #e8f0fe; border-radius: 12px;")
        ic_layout = QVBoxLayout(icon_c)
        ic_layout.setContentsMargins(0, 0, 0, 0)
        ic_lbl = QLabel(icon)
        ic_lbl.setStyleSheet("font-size: 26px; color: #1a73e8; background: transparent;")
        ic_lbl.setAlignment(Qt.AlignCenter)
        ic_layout.addWidget(ic_lbl)
        layout.addWidget(icon_c)
        
        # Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 12px; color: #64748b; font-weight: 500;")
        text_layout.addWidget(title_lbl)
        
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #1e293b;")
        text_layout.addWidget(value_lbl)
        
        # Mini chart (3 petites barres colorées)
        if mini_chart:
            chart_row = QHBoxLayout()
            chart_row.setSpacing(8)
            for label, color in mini_chart:
                seg_layout = QVBoxLayout()
                seg_layout.setSpacing(2)
                
                seg = QFrame()
                seg.setFixedHeight(20)
                seg.setFixedWidth(40)
                seg.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
                seg_layout.addWidget(seg)
                
                seg_lbl = QLabel(label)
                seg_lbl.setStyleSheet("font-size: 9px; color: #64748b;")
                seg_lbl.setAlignment(Qt.AlignCenter)
                seg_layout.addWidget(seg_lbl)
                
                chart_row.addLayout(seg_layout)
            chart_row.addStretch()
            text_layout.addLayout(chart_row)
        
        # Barre de progression multi-segments
        if show_progress_bar and progress_segments:
            pb_frame = QFrame()
            pb_frame.setFixedHeight(8)
            pb_frame.setStyleSheet("background-color: #f1f5f9; border-radius: 4px;")
            pb_layout = QHBoxLayout(pb_frame)
            pb_layout.setContentsMargins(0, 0, 0, 0)
            pb_layout.setSpacing(0)
            
            for label, color in progress_segments:
                seg = QFrame()
                seg.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
                pb_layout.addWidget(seg, 1)
            
            text_layout.addWidget(pb_frame)
            
            # Légende des segments
            legend_row = QHBoxLayout()
            legend_row.setSpacing(12)
            for label, color in progress_segments:
                item = QHBoxLayout()
                item.setSpacing(4)
                dot = QLabel()
                dot.setFixedSize(8, 8)
                dot.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
                item.addWidget(dot)
                lbl = QLabel(label)
                lbl.setStyleSheet("font-size: 9px; color: #64748b;")
                item.addWidget(lbl)
                legend_row.addLayout(item)
            legend_row.addStretch()
            text_layout.addLayout(legend_row)
        
        layout.addLayout(text_layout, 1)
        
        card.value_label = value_lbl
        return card
    
    def _make_anomalies_card(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #fee2e2;
                border: 1px solid #fecaca;
                border-radius: 12px;
            }
        """)
        card.setMinimumHeight(110)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)
        
        # Icône alerte
        icon_c = QFrame()
        icon_c.setFixedSize(56, 56)
        icon_c.setStyleSheet("background-color: #fecaca; border-radius: 12px;")
        ic_layout = QVBoxLayout(icon_c)
        ic_layout.setContentsMargins(0, 0, 0, 0)
        ic_lbl = QLabel("⚠️")
        ic_lbl.setStyleSheet("font-size: 28px; color: #ef4444; background: transparent;")
        ic_lbl.setAlignment(Qt.AlignCenter)
        ic_layout.addWidget(ic_lbl)
        layout.addWidget(icon_c)
        
        # Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        title_lbl = QLabel("Anomalies Récentes")
        title_lbl.setStyleSheet("font-size: 13px; color: #7f1d1d; font-weight: bold;")
        text_layout.addWidget(title_lbl)
        
        # Ligne 1 : PENDING VERIFICATION
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        
        count1 = QLabel("4")
        count1.setStyleSheet("font-size: 20px; font-weight: bold; color: #991b1b;")
        row1.addWidget(count1)
        
        badge1 = QLabel("PENDING VERIFICATION")
        badge1.setStyleSheet("""
            background-color: #fef3c7;
            color: #92400e;
            padding: 3px 8px;
            border-radius: 8px;
            font-size: 9px;
            font-weight: bold;
        """)
        row1.addWidget(badge1)
        row1.addStretch()
        
        text_layout.addLayout(row1)
        
        # Ligne 2 : Anomalies in compliance
        row2 = QHBoxLayout()
        row2.setSpacing(8)
        
        count2 = QLabel("1")
        count2.setStyleSheet("font-size: 16px; font-weight: bold; color: #991b1b;")
        row2.addWidget(count2)
        
        label2 = QLabel("Anomalies in compliance")
        label2.setStyleSheet("font-size: 10px; color: #991b1b;")
        row2.addWidget(label2)
        row2.addStretch()
        
        text_layout.addLayout(row2)
        
        layout.addLayout(text_layout, 1)
        
        # Icône à droite
        right_icon = QLabel("⚠️")
        right_icon.setStyleSheet("font-size: 20px;")
        layout.addWidget(right_icon)
        
        card.value_label = count1
        return card
    
    # ============================================================
    # CHARGEMENT DES DONNÉES
    # ============================================================
    
    def load_data(self):
        try:
            # Charger les banques pour la map id → nom
            try:
                banques = self.reglement_controller.get_banques()
                self._banques_map = {b.get('id'): b.get('libelle', '') for b in banques}
            except Exception:
                self._banques_map = {}
            
            # Charger les comptes
            comptes = self.reglement_controller.get_comptes_bancaires(actifs_only=False)
            self._comptes = comptes
            
            self._update_kpis(comptes)
            self._populate_filters(comptes)
            self._apply_filters()
        except Exception as e:
            print(f"❌ Erreur chargement comptes: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les comptes: {e}")
    
    def _update_kpis(self, comptes):
        total = len(comptes)
        
        # Somme des soldes
        total_solde = sum((c.get('solde') or 0) for c in comptes)
        
        # Anomalies : comptes inactifs ou non vérifiés
        anomalies = sum(1 for c in comptes if not c.get('est_actif'))
        
        self.kpi_total.value_label.setText(str(total))
        self.kpi_solde.value_label.setText(f"{total_solde:,.0f} XAF")
        self.kpi_anomalies.value_label.setText(str(anomalies))
    
    def _populate_filters(self, comptes):
        # Devises
        self.filter_devise.blockSignals(True)
        current = self.filter_devise.currentData()
        self.filter_devise.clear()
        self.filter_devise.addItem("Pays", None)
        devises = sorted(set(c.get('devise') for c in comptes if c.get('devise')))
        for d in devises:
            self.filter_devise.addItem(d, d)
        for i in range(self.filter_devise.count()):
            if self.filter_devise.itemData(i) == current:
                self.filter_devise.setCurrentIndex(i)
                break
        self.filter_devise.blockSignals(False)
    
    # ============================================================
    # FILTRES
    # ============================================================
    
    def _apply_filters(self):
        filtered = list(self._comptes)
        
        # Recherche
        search = self.search_input.text().strip().lower()
        if search:
            filtered = [
                c for c in filtered
                if search in (c.get('code_banque', '') or '').lower()
                or search in (c.get('libelle', '') or '').lower()
                or search in (c.get('iban', '') or '').lower()
                or search in (c.get('devise', '') or '').lower()
                or search in (c.get('titulaire', '') or '').lower()
            ]
        
        # Filtre devise
        devise_f = self.filter_devise.currentData()
        if devise_f:
            filtered = [c for c in filtered if c.get('devise') == devise_f]
        
        # Filtre statut
        statut_f = self.filter_statut.currentData()
        if statut_f is not None:
            filtered = [c for c in filtered if c.get('est_actif') == statut_f]
        
        self._filtered_comptes = filtered
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
            self.table_wrapper.show()
            self.cards_container.hide()
            self._render_table()
            self._render_alertes()
        else:
            self.table_wrapper.hide()
            self.cards_container.show()
            self._render_cards()
        
        self._update_pagination()
    
    def _render_table(self):
        start = (self._current_page - 1) * self._per_page
        end = start + self._per_page
        page_comptes = self._filtered_comptes[start:end]
        
        self.table.setRowCount(len(page_comptes))
        
        for i, c in enumerate(page_comptes):
            # Checkbox
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk.setCheckState(Qt.Unchecked)
            self.table.setItem(i, 0, chk)
            
            # Banque (nom + logo)
            banque_id = c.get('banque')
            banque_nom = self._banques_map.get(banque_id, '—')
            banque_item = QTableWidgetItem(f"🏦 {banque_nom}")
            banque_item.setData(Qt.UserRole, c)
            self.table.setItem(i, 1, banque_item)
            
            # IBAN
            self.table.setItem(i, 2, QTableWidgetItem(c.get('iban', '') or '—'))
            
            # Titulaire
            titulaire = c.get('titulaire') or c.get('personne') or '—'
            self.table.setItem(i, 3, QTableWidgetItem(titulaire))
            
            # Devise
            self.table.setItem(i, 4, QTableWidgetItem(c.get('devise', '') or '—'))
            
            # Solde
            solde = c.get('solde', 0) or 0
            solde_item = QTableWidgetItem(f"{solde:,.0f} {c.get('devise', '')}")
            solde_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 5, solde_item)
            
            # Dernier mouvement
            dm = c.get('date_dernier_mouvement', '') or ''
            self.table.setItem(i, 6, QTableWidgetItem(dm[:16] if dm else '—'))
            
            # Statut badge
            actif = c.get('est_actif', True)
            statut_item = QTableWidgetItem("ACTIF" if actif else "INACTIF")
            statut_item.setBackground(QColor('#dcfce7' if actif else '#fee2e2'))
            statut_item.setForeground(QColor('#166534' if actif else '#991b1b'))
            statut_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 7, statut_item)
    
    def _render_alertes(self):
        """Met à jour le panneau d'alertes"""
        # Vider
        while self.alertes_content.count():
            item = self.alertes_content.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Chercher les comptes avec alertes
        comptes_alertes = [
            c for c in self._filtered_comptes
            if c.get('alertes') or not c.get('est_actif')
        ]
        
        if not comptes_alertes:
            empty = QLabel("Aucune alerte")
            empty.setStyleSheet("color: #92400e; font-size: 11px; font-style: italic;")
            empty.setAlignment(Qt.AlignCenter)
            self.alertes_content.addWidget(empty)
            return
        
        for c in comptes_alertes[:6]:
            alerte = QFrame()
            alerte.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 6px;
                    border-left: 3px solid #ef4444;
                }
            """)
            al_layout = QVBoxLayout(alerte)
            al_layout.setContentsMargins(8, 6, 8, 6)
            
            title = QLabel(c.get('libelle', 'Compte'))
            title.setStyleSheet("font-size: 10px; font-weight: bold; color: #7f1d1d;")
            al_layout.addWidget(title)
            
            msg = QLabel(c.get('alerte_message', 'Vérification requise'))
            msg.setStyleSheet("font-size: 10px; color: #991b1b;")
            msg.setWordWrap(True)
            al_layout.addWidget(msg)
            
            self.alertes_content.addWidget(alerte)
    
    def _render_cards(self):
        # Vider la grille
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        start = (self._current_page - 1) * self._per_page
        end = start + self._per_page
        page_comptes = self._filtered_comptes[start:end]
        
        if not page_comptes:
            empty = QLabel("Aucun compte à afficher")
            empty.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 40px;")
            empty.setAlignment(Qt.AlignCenter)
            self.cards_grid.addWidget(empty, 0, 0, 1, 2)
            return
        
        for i, c in enumerate(page_comptes):
            banque_id = c.get('banque')
            banque_nom = self._banques_map.get(banque_id, '—')
            
            card = CompteBancaireCard(c, banque_nom=banque_nom)
            card.edit_requested.connect(self._on_edit_compte)
            card.delete_requested.connect(self._on_delete_compte)
            card.view_requested.connect(self._on_view_compte)
            card.context_menu_requested.connect(self._show_card_context_menu)
            
            row = i // 2
            col = i % 2
            self.cards_grid.addWidget(card, row, col)
    
    def _update_pagination(self):
        total = len(self._filtered_comptes)
        start = (self._current_page - 1) * self._per_page + 1 if total > 0 else 0
        end = min(self._current_page * self._per_page, total)
        total_pages = max(1, (total + self._per_page - 1) // self._per_page)
        
        self.lbl_pagination.setText(f"Affichage de {start}-{end} sur {total} comptes")
        self.btn_page.setText(str(self._current_page))
        
        self.btn_first.setEnabled(self._current_page > 1)
        self.btn_prev.setEnabled(self._current_page > 1)
        self.btn_next.setEnabled(self._current_page < total_pages)
        self.btn_last.setEnabled(self._current_page < total_pages)
    
    def _go_to_page(self, page: int):
        total_pages = max(1, (len(self._filtered_comptes) + self._per_page - 1) // self._per_page)
        page = max(1, min(page, total_pages))
        if page != self._current_page:
            self._current_page = page
            self._render_current_view()
    
    # ============================================================
    # MENU CONTEXTUEL
    # ============================================================
    
    def _show_card_context_menu(self, compte: dict, global_pos):
        self._show_compte_context_menu(compte, global_pos)
    
    def _show_table_context_menu(self, pos):
        row = self.table.currentRow()
        if row < 0:
            return
        
        banque_item = self.table.item(row, 1)
        if not banque_item:
            return
        compte = banque_item.data(Qt.UserRole)
        if not compte:
            return
        
        self._show_compte_context_menu(compte, self.table.viewport().mapToGlobal(pos))
    
    def _show_compte_context_menu(self, compte: dict, global_pos):
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
        
        action_view = QAction("👁️  Voir les détails", self)
        action_view.triggered.connect(lambda: self._on_view_compte(compte))
        menu.addAction(action_view)
        
        action_copy_iban = QAction("📋  Copier l'IBAN", self)
        action_copy_iban.triggered.connect(lambda: self._copy_to_clipboard(compte.get('iban', '')))
        menu.addAction(action_copy_iban)
        
        menu.addSeparator()
        
        if self._perm_ui.peut('referentiel', 'UPDATE'):
            action_edit = QAction("✏️  Modifier", self)
            action_edit.triggered.connect(lambda: self._on_edit_compte(compte))
            menu.addAction(action_edit)
        
        menu.addSeparator()
        
        if self._perm_ui.peut('referentiel', 'DELETE'):
            action_delete = QAction("🗑️  Supprimer", self)
            action_delete.triggered.connect(lambda: self._on_delete_compte(compte))
            menu.addAction(action_delete)
        
        menu.exec(global_pos)
    
    # ============================================================
    # ACTIONS
    # ============================================================
    
    def _on_view_compte(self, compte: dict):
        banque_id = compte.get('banque')
        banque_libelle = compte.get("libelle")
        banque_nom = str(f"{banque_id} - {banque_libelle}")
        solde = compte.get('solde', 0) or 0
        
        QMessageBox.information(
            self, "Détails du compte",
            f"💳 Libellé: {compte.get('libelle', 'N/A')}\n"
            f"🏦 Banque: {banque_nom}\n"
            f"🔢 IBAN: {compte.get('iban', '—')}\n"
            f"💱 Devise: {compte.get('devise', '—')}\n"
            f"💰 Solde: {solde:,.0f} {compte.get('devise', '')}\n"
            f"👤 Titulaire: {compte.get('titulaire') or '—'}\n"
            f"📅 Dernier mouvement: {compte.get('date_dernier_mouvement', '—')}\n"
            f"📌 Statut: {'✅ Actif' if compte.get('est_actif') else '❌ Inactif'}"
        )
    
    def _on_edit_compte(self, compte: dict):
        QMessageBox.information(
            self, "Modifier compte",
            f"Édition du compte {compte.get('libelle', '')} (à implémenter)"
        )
    
    def _on_delete_compte(self, compte: dict):
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous vraiment supprimer le compte\n"
            f"« {compte.get('libelle', 'N/A')} » ?\n\n"
            f"⚠️ Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Info", "Suppression à implémenter")
    
    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copié", f"✅ '{text}' copié")
    
    def exporter_csv(self):
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exporter les comptes",
            "comptes_bancaires.csv",
            "CSV (*.csv)"
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Banque", "IBAN", "Libellé", "Devise",
                                 "Solde", "Titulaire", "Statut"])
                for c in self._filtered_comptes:
                    banque_nom = self._banques_map.get(c.get('banque'), '')
                    writer.writerow([
                        banque_nom, c.get('iban', ''), c.get('libelle', ''),
                        c.get('devise', ''), c.get('solde', 0),
                        c.get('titulaire', ''),
                        "Actif" if c.get('est_actif') else "Inactif",
                    ])
            QMessageBox.information(self, "Export", f"✅ {len(self._filtered_comptes)} comptes exportés")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    def ouvrir_dialogue_creation(self):
        from addons.sinistres.views.compte_bancaire_dialog import CompteBancaireDialog
        dialog = CompteBancaireDialog(
            reglement_controller=self.reglement_controller,
            user=self.user,
            parent=self,
        )
        dialog.compte_created.connect(self._on_compte_cree)
        dialog.exec()
    
    def _on_compte_cree(self, data: dict):
        self.load_data()

# ============================================================
# WIDGETS CUSTOM POUR L'ONGLET AUDIT (v2)
# ============================================================

class DonutChart(QWidget):
    """Graphique en anneau avec légende intégrée"""
    
    def __init__(self, data: dict = None, colors: dict = None, parent=None):
        super().__init__(parent)
        self.data = data or {}
        self.colors = colors or {}
        self.setMinimumSize(160, 160)
        self.setMaximumSize(160, 160)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.data:
            painter.end()
            return
        
        rect = self.rect()
        size = min(rect.width(), rect.height()) - 20
        x = (rect.width() - size) / 2
        y = (rect.height() - size) / 2
        
        total = sum(self.data.values()) or 1
        start_angle = 90 * 16
        thickness = 18
        
        for label, value in self.data.items():
            span = int((value / total) * 360 * 16)
            color = QColor(self.colors.get(label, '#64748b'))
            
            pen = QPen(color, thickness)
            pen.setCapStyle(Qt.FlatCap)
            painter.setPen(pen)
            
            painter.drawArc(
                int(x), int(y), int(size), int(size),
                start_angle, -span
            )
            start_angle -= span
        
        # Texte central
        if total > 0:
            painter.setPen(QColor('#1e293b'))
            painter.setFont(QFont("Arial", 14, QFont.Bold))
            painter.drawText(
                QRectF(x, y, size, size),
                Qt.AlignCenter,
                str(total)
            )
            painter.setPen(QColor('#64748b'))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(
                QRectF(x, y + 25, size, size),
                Qt.AlignCenter,
                "total"
            )
        
        painter.end()


class BarChartWidget(QWidget):
    """Graphique à barres avec valeurs au-dessus et légende dessous"""
    
    def __init__(self, data: dict = None, color: str = '#22c55e', parent=None):
        super().__init__(parent)
        self.data = data or {}
        self.color = color
        self.setMinimumHeight(130)
        self.setMaximumHeight(160)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.data:
            painter.end()
            return
        
        rect = self.rect()
        padding_left = 20
        padding_right = 20
        padding_top = 25
        padding_bottom = 35
        
        usable_width = rect.width() - padding_left - padding_right
        usable_height = rect.height() - padding_top - padding_bottom
        
        max_val = max(self.data.values()) or 1
        n = len(self.data)
        if n == 0:
            painter.end()
            return
        
        bar_width = min(50, usable_width // (n * 2))
        spacing = (usable_width - (bar_width * n)) // (n + 1)
        
        # Grille horizontale (lignes)
        painter.setPen(QPen(QColor('#f1f5f9'), 1))
        for i in range(5):
            y = padding_top + (i * usable_height / 4)
            painter.drawLine(padding_left, int(y), rect.width() - padding_right, int(y))
        
        # Barres
        for i, (label, value) in enumerate(self.data.items()):
            x = padding_left + spacing + i * (bar_width + spacing)
            bar_height = int((value / max_val) * usable_height) if max_val > 0 else 0
            y = padding_top + usable_height - bar_height
            
            if value == 0:
                painter.setBrush(QBrush(QColor('#e2e8f0')))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(int(x), int(padding_top + usable_height - 3),
                                        bar_width, 3, 1, 1)
                # Valeur "0" au-dessus
                painter.setPen(QColor('#94a3b8'))
                painter.setFont(QFont("Arial", 10, QFont.Bold))
                painter.drawText(int(x), int(padding_top + usable_height - 25),
                                bar_width, 18, Qt.AlignCenter, "0")
            else:
                # Barre normale
                painter.setBrush(QBrush(QColor(self.color)))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(int(x), int(y), bar_width, bar_height, 4, 4)
                
                # Valeur au-dessus
                painter.setPen(QColor('#1e293b'))
                painter.setFont(QFont("Arial", 10, QFont.Bold))
                painter.drawText(int(x), int(y) - 18, bar_width, 18,
                                Qt.AlignCenter, str(value))
        
        painter.end()

# ============================================================
# WIDGETS CUSTOM v3 — Style capture
# ============================================================

class KPICard(QFrame):
    """Carte KPI style capture : icône colorée + valeur + libellé"""
    
    def __init__(self, icon: str, value: str, title: str, subtitle: str = "",
                 color: str = "#1a73e8", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        self.setMinimumHeight(110)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        
        # Icône colorée (carré arrondi)
        icon_container = QFrame()
        icon_container.setFixedSize(52, 52)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background-color: {color}1A;
                border-radius: 10px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 22px; color: {color}; background: transparent;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_lbl)
        
        layout.addWidget(icon_container)
        
        # Contenu texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        # Titre en haut
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 12px; color: #64748b; font-weight: 500;")
        text_layout.addWidget(title_lbl)
        
        # Valeur grande
        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet("font-size: 26px; font-weight: bold; color: #1e293b;")
        text_layout.addWidget(self.value_lbl)
        
        # Sous-titre / libellé
        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setStyleSheet("font-size: 11px; color: #94a3b8;")
            sub_lbl.setWordWrap(True)
            text_layout.addWidget(sub_lbl)
        
        layout.addLayout(text_layout, 1)
        
        # Icône à droite (optionnelle)
        self.right_icon = QLabel("")
        self.right_icon.setStyleSheet("font-size: 16px; color: #cbd5e1;")
        self.right_icon.setAlignment(Qt.AlignTop | Qt.AlignRight)
        layout.addWidget(self.right_icon)
    
    def set_value(self, value: str):
        self.value_lbl.setText(value)
    
    def set_right_icon(self, icon: str):
        self.right_icon.setText(icon)


class BarChartWidget(QWidget):
    """Bar chart avec badges numérotés au-dessus des barres"""
    
    def __init__(self, data: dict = None, parent=None):
        super().__init__(parent)
        self.data = data or {}
        self.setMinimumHeight(200)
        self.setMaximumHeight(240)
        
        # Palette de couleurs dégradées pour les barres
        self.bar_colors = ['#94a3b8', '#7d9d9a', '#7da89d', '#7fb39b']
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.data:
            painter.end()
            return
        
        rect = self.rect()
        padding_left = 30
        padding_right = 20
        padding_top = 45
        padding_bottom = 30
        
        usable_width = rect.width() - padding_left - padding_right
        usable_height = rect.height() - padding_top - padding_bottom
        
        max_val = max(self.data.values()) or 1
        n = len(self.data)
        if n == 0:
            painter.end()
            return
        
        bar_width = min(60, usable_width // (n * 2))
        spacing = (usable_width - (bar_width * n)) // (n + 1)
        
        # Grille horizontale (5 lignes)
        painter.setPen(QPen(QColor('#f1f5f9'), 1))
        for i in range(5):
            y = padding_top + (i * usable_height / 4)
            painter.drawLine(padding_left, int(y), rect.width() - padding_right, int(y))
        
        # Barres
        for i, (label, value) in enumerate(self.data.items()):
            x = padding_left + spacing + i * (bar_width + spacing)
            bar_height = int((value / max_val) * usable_height) if max_val > 0 else 0
            y = padding_top + usable_height - bar_height
            
            # Couleur par barre
            color = self.bar_colors[i % len(self.bar_colors)]
            
            # Barre (coins arrondis en haut)
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(x), int(y), bar_width, bar_height, 6, 6)
            
            # Badge numéroté au-dessus (fond sombre arrondi)
            badge_w = 34
            badge_h = 20
            badge_x = x + (bar_width - badge_w) / 2
            badge_y = y - badge_h - 8
            
            painter.setBrush(QBrush(QColor('#334155')))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(badge_x), int(badge_y), badge_w, badge_h, 5, 5)
            
            # Petite flèche en bas du badge
            painter.drawPolygon([
                QPointF(badge_x + badge_w / 2 - 4, badge_y + badge_h),
                QPointF(badge_x + badge_w / 2 + 4, badge_y + badge_h),
                QPointF(badge_x + badge_w / 2, badge_y + badge_h + 4),
            ])
            
            # Valeur dans le badge
            painter.setPen(QColor('white'))
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(
                int(badge_x), int(badge_y), badge_w, badge_h,
                Qt.AlignCenter, str(value)
            )
        
        painter.end()


class StackedBarWidget(QWidget):
    """Barre horizontale empilée avec séparateurs"""
    
    def __init__(self, data: dict = None, colors: dict = None, parent=None):
        super().__init__(parent)
        self.data = data or {}
        self.colors = colors or {}
        self.setMinimumHeight(40)
        self.setMaximumHeight(50)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.data:
            painter.end()
            return
        
        rect = self.rect()
        total = sum(self.data.values()) or 1
        
        x = 0
        radius = 6
        
        for label, value in self.data.items():
            width = int((value / total) * rect.width())
            color = self.colors.get(label, '#94a3b8')
            
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.NoPen)
            
            if x == 0:
                # Premier : coins gauche arrondis
                painter.drawRoundedRect(x, 0, width + radius, rect.height(), radius, radius)
                painter.drawRect(x + width - radius, 0, radius, rect.height())
            elif x + width >= rect.width():
                # Dernier : coins droit arrondis
                painter.drawRoundedRect(x - radius, 0, width + radius, rect.height(), radius, radius)
                painter.drawRect(x, 0, radius, rect.height())
            else:
                painter.drawRect(x, 0, width, rect.height())
            
            x += width
        
        painter.end()


class LegendWidget(QWidget):
    """Légende horizontale style capture"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(16)
        self.layout.setAlignment(Qt.AlignCenter)
    
    def set_data(self, data: dict, colors: dict, total: int = 0):
        # Vider
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if total == 0:
            total = sum(data.values()) or 1
        
        sorted_items = sorted(data.items(), key=lambda x: -x[1])
        
        for label, value in sorted_items[:8]:
            color = colors.get(label, '#94a3b8')
            
            item = QWidget()
            item.setStyleSheet("background: transparent;")
            h = QHBoxLayout(item)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(6)
            
            # Pastille
            dot = QLabel()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
            h.addWidget(dot)
            
            # Nom
            name = QLabel(label)
            name.setStyleSheet("font-size: 11px; color: #475569; font-weight: 500;")
            h.addWidget(name)
            
            self.layout.addWidget(item)
        
        self.layout.addStretch()


class PaginationWidget(QFrame):
    """Widget de pagination style capture"""
    
    page_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 1
        self.total_pages = 1
        
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 12px;
                color: #64748b;
                font-weight: bold;
                min-width: 32px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
            QPushButton:disabled {
                color: #cbd5e1;
                background-color: #f8fafc;
            }
            QLabel {
                color: #64748b;
                font-size: 11px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(6)
        
        self.lbl_total = QLabel("Total: 0 résultats")
        layout.addWidget(self.lbl_total)
        
        layout.addStretch()
        
        self.btn_first = QPushButton("⏮")
        self.btn_first.clicked.connect(lambda: self.go_to_page(1))
        layout.addWidget(self.btn_first)
        
        self.btn_prev = QPushButton("◀")
        self.btn_prev.clicked.connect(lambda: self.go_to_page(self.current_page - 1))
        layout.addWidget(self.btn_prev)
        
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
        layout.addWidget(self.btn_page)
        
        self.btn_next = QPushButton("▶")
        self.btn_next.clicked.connect(lambda: self.go_to_page(self.current_page + 1))
        layout.addWidget(self.btn_next)
        
        self.btn_last = QPushButton("⏭")
        self.btn_last.clicked.connect(lambda: self.go_to_page(self.total_pages))
        layout.addWidget(self.btn_last)
        
        layout.addStretch()
        
        self.lbl_24h = QLabel("🕐 24h: 0")
        layout.addWidget(self.lbl_24h)
        
        self._update_buttons()
    
    def set_data(self, total: int, current_page: int, total_pages: int, count_24h: int = 0):
        self.current_page = current_page
        self.total_pages = max(1, total_pages)
        
        self.lbl_total.setText(f"Total: {total} résultats")
        self.lbl_24h.setText(f"🕐 24h: {count_24h}")
        self.btn_page.setText(str(current_page))
        self._update_buttons()
    
    def go_to_page(self, page: int):
        if 1 <= page <= self.total_pages and page != self.current_page:
            self.current_page = page
            self._update_buttons()
            self.page_changed.emit(page)
    
    def _update_buttons(self):
        self.btn_first.setEnabled(self.current_page > 1)
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < self.total_pages)
        self.btn_last.setEnabled(self.current_page < self.total_pages)


# ============================================================
# ONGLET AUDIT - Nouvelle version
# ============================================================

class AuditTab(QWidget):
    """Onglet d'audit et logs - Version moderne"""
    
    PAGE_SIZE = 50
    
    def __init__(self, audit_controller=None, user=None):
        super().__init__()
        self.audit_controller = audit_controller
        self.user = user
        self._all_logs = []
        self._filtered_logs = []
        self._current_page = 1
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
        # LIGNE 1 : BARRE DE FILTRES
        # ============================================================
        filter_bar = QFrame()
        filter_bar.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        filter_layout = QHBoxLayout(filter_bar)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(12)
        
        # Filtre Action
        self.filter_action = QComboBox()
        self.filter_action.addItem("Filtrer par action", None)
        self.filter_action.addItem("Création", "CREATION")
        self.filter_action.addItem("Modification", "MODIFICATION")
        self.filter_action.addItem("Validation", "VALIDATION")
        self.filter_action.addItem("Suppression", "SUPPRESSION")
        self.filter_action.addItem("Changement statut", "CHANGEMENT_STATUT")
        self.filter_action.setMinimumWidth(180)
        self.filter_action.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                color: #1e293b;
            }
            QComboBox:focus { border: 2px solid #1a73e8; }
            QComboBox::drop-down { border: none; width: 24px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #64748b;
                margin-right: 8px;
            }
        """)
        self.filter_action.currentIndexChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.filter_action)
        
        # Filtre Entité
        self.filter_entite = QComboBox()
        self.filter_entite.addItem("Filtrer par entité", None)
        self.filter_entite.addItem("Sinistre", "Sinistre")
        self.filter_entite.addItem("Expertise", "Expertise")
        self.filter_entite.addItem("Evaluation", "Evaluation")
        self.filter_entite.addItem("Reglement", "Reglement")
        self.filter_entite.addItem("Recours", "Recours")
        self.filter_entite.setMinimumWidth(180)
        self.filter_entite.setStyleSheet(self.filter_action.styleSheet())
        self.filter_entite.currentIndexChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.filter_entite)
        
        # Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Rechercher...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QLineEdit:focus { border: 2px solid #1a73e8; }
        """)
        self.search_input.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_input, 1)
        
        # Compteur
        self.lbl_results = QLabel("0 résultats")
        self.lbl_results.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
        filter_layout.addWidget(self.lbl_results)
        
        # Bouton Rafraîchir
        self.btn_refresh = QPushButton("🔄 Rafraîchir")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                color: #1e293b;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #f1f5f9; }
        """)
        self.btn_refresh.clicked.connect(self.load_data)
        filter_layout.addWidget(self.btn_refresh)
        
        layout.addWidget(filter_bar)
        
        # ============================================================
        # LIGNE 2 : KPI CARDS (4 cards)
        # ============================================================
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)
        
        self.kpi_total = KPICard("📄", "0", "Total des Actions", "Actions totales cumulées", "#3b82f6")
        kpi_row.addWidget(self.kpi_total)
        
        self.kpi_24h = KPICard("🕐", "0", "Activité Récente", "Dernier jour\n(24 heures)", "#8b5cf6")
        kpi_row.addWidget(self.kpi_24h)
        
        self.kpi_users = KPICard("👤", "0", "Utilisateurs Uniques", "Utilisateurs uniques sur\nla période", "#06b6d4")
        kpi_row.addWidget(self.kpi_users)
        
        self.kpi_top = KPICard("🏆", "—", "Top Action", "Action la plus fréquente\n(Dernier jour: 0)", "#f59e0b")
        kpi_row.addWidget(self.kpi_top)
        
        layout.addLayout(kpi_row)
        
        # ============================================================
        # LIGNE 3 : GRAPHIQUES (2 colonnes)
        # ============================================================
        charts_row = QHBoxLayout()
        charts_row.setSpacing(14)
        
        # --- Aperçu des actions ---
        card_actions = QFrame()
        card_actions.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        ca_layout = QVBoxLayout(card_actions)
        ca_layout.setContentsMargins(16, 14, 16, 14)
        ca_layout.setSpacing(10)
        
        ca_title = QLabel("📊 Aperçu des actions")
        ca_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        ca_layout.addWidget(ca_title)
        
        self.chart_actions = BarChartWidget()
        ca_layout.addWidget(self.chart_actions, 1)
        
        charts_row.addWidget(card_actions, 1)
        
        # --- Répartition des entités ---
        card_entites = QFrame()
        card_entites.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        ce_layout = QVBoxLayout(card_entites)
        ce_layout.setContentsMargins(16, 14, 16, 14)
        ce_layout.setSpacing(12)
        
        ce_title = QLabel("📈 Répartition des entités")
        ce_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        ce_layout.addWidget(ce_title)
        
        # Barre empilée
        self.stacked_bar = StackedBarWidget({}, {})
        ce_layout.addWidget(self.stacked_bar)
        
        # Légende horizontale
        self.legend = LegendWidget()
        ce_layout.addWidget(self.legend)
        
        ce_layout.addStretch()
        
        charts_row.addWidget(card_entites, 1)
        
        layout.addLayout(charts_row)
        
        # ============================================================
        # LIGNE 4 : TABLEAU
        # ============================================================
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        tc_layout = QVBoxLayout(table_container)
        tc_layout.setContentsMargins(0, 0, 0, 0)
        tc_layout.setSpacing(0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Date", "Utilisateur", "Action", "Entité", "ID", "Champ", "Ancien → Nouveau"
        ])
        self.table.setMinimumHeight(320)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(52)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                border-radius: 10px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px 12px;
                font-size: 12px;
                border-bottom: 1px solid #f1f5f9;
                color: #1e293b;
            }
            QTableWidget::item:selected {
                background-color: #e8f0fe;
                color: #1e293b;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px;
                font-weight: 600;
                font-size: 11px;
                color: #64748b;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px;
            }
        """)
        tc_layout.addWidget(self.table)
        
        layout.addWidget(table_container)
        
        # ============================================================
        # LIGNE 5 : PAGINATION
        # ============================================================
        self.pagination = PaginationWidget()
        self.pagination.page_changed.connect(self._on_page_changed)
        layout.addWidget(self.pagination)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    def load_data(self):
        """Charge les logs d'audit"""
        try:
            logs = self._fetch_logs()
            self._all_logs = logs
            self._apply_filters()
        except Exception as e:
            print(f"❌ Erreur chargement audit: {e}")
            import traceback
            traceback.print_exc()
            self._all_logs = []
            self._apply_filters()
    
    def _fetch_logs(self) -> List[dict]:
        """Récupère les logs via AuditController"""
        if not self.audit_controller:
            print("⚠️ Aucun AuditController fourni")
            return []
        return self.audit_controller.get_all_logs(limit=500) or []
    
    def _serialize_audit_logs(self, logs) -> List[dict]:
        """Convertit les objets ORM en dicts"""
        result = []
        for log in logs:
            try:
                result.append({
                    'date': log.date_action.strftime('%Y-%m-%d %H:%M') if getattr(log, 'date_action', None) else '',
                    'user': getattr(log, 'utilisateur_nom', '') or getattr(log, 'utilisateur', 'N/A'),
                    'action': getattr(log, 'action', ''),
                    'entite': getattr(log, 'entite', ''),
                    'id': getattr(log, 'entite_nom', '') or str(getattr(log, 'entite_id', '')),
                    'champ': getattr(log, 'champ_modifie', '') or '',
                    'change': f"{getattr(log, 'ancienne_valeur', '') or ''} → {getattr(log, 'nouvelle_valeur', '') or ''}".strip(' →'),
                })
            except Exception as e:
                print(f"Erreur sérialisation log: {e}")
        return result
    
    def _apply_filters(self):
        """Applique les filtres actifs"""
        filtered = list(self._all_logs)
        
        # Filtre action
        action_f = self.filter_action.currentData()
        if action_f:
            filtered = [l for l in filtered if l.get('action') == action_f]
        
        # Filtre entité
        entite_f = self.filter_entite.currentData()
        if entite_f:
            filtered = [l for l in filtered if l.get('entite') == entite_f]
        
        # ✅ Recherche texte
        search = self.search_input.text().strip().lower()
        if search:
            filtered = [
                l for l in filtered
                if search in (l.get('user', '') or '').lower()
                or search in (l.get('id', '') or '').lower()
                or search in (l.get('entite', '') or '').lower()
                or search in (l.get('action', '') or '').lower()
                or search in (l.get('champ', '') or '').lower()
                or search in (l.get('change', '') or '').lower()
            ]
        
        self._filtered_logs = filtered
        self._current_page = 1
        
        self._update_kpis(filtered)
        self._update_charts(filtered)
        self._render_table()

    def _update_kpis(self, logs: List[dict]):
        from datetime import datetime, timedelta
        from collections import Counter
        
        total = len(logs)
        self.kpi_total.set_value(str(total))
        
        # 24h
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        count_24h = sum(1 for l in logs
                        if l.get('date_iso') and
                        datetime.fromisoformat(l['date_iso']) >= yesterday)
        self.kpi_24h.set_value(str(count_24h))
        
        # Users uniques
        users = set(l.get('user', '') for l in logs if l.get('user'))
        self.kpi_users.set_value(str(len(users)))
        
        # Top action
        actions = Counter(l.get('action', '') for l in logs if l.get('action'))
        if actions:
            top_action, top_count = actions.most_common(1)[0]
            self.kpi_top.set_value(top_action)
            
            # Nombre dans les 24h pour cette action
            top_24h = sum(1 for l in logs
                        if l.get('action') == top_action
                        and l.get('date_iso')
                        and datetime.fromisoformat(l['date_iso']) >= yesterday)
            # Note : on peut mettre à jour le sous-titre si besoin
        else:
            self.kpi_top.set_value("—")

    def _update_charts(self, logs: List[dict]):
        from collections import Counter
        
        # ============================================================
        # Bar chart : Top 4 actions
        # ============================================================
        actions = Counter(l.get('action') for l in logs if l.get('action'))
        
        action_labels = {
            'CREATION': 'Création',
            'MODIFICATION': 'Modification',
            'VALIDATION': 'Validation',
            'SUPPRESSION': 'Suppression',
            'CHANGEMENT_STATUT': 'Statut',
            'REVISION': 'Révision',
            'AFFECTATION': 'Affectation',
            'DEMARRAGE': 'Démarrage',
            'FICHIERS_JOINTS': 'Fichiers',
            'PAIEMENT': 'Paiement',
            'ANNULATION': 'Annulation',
        }
        
        top_actions = actions.most_common(4)
        data_bar = {action_labels.get(k, k): v for k, v in top_actions}
        
        self.chart_actions.data = data_bar
        self.chart_actions.update()
        
        # ============================================================
        # Stacked bar : Entités
        # ============================================================
        entites = Counter(l.get('entite') for l in logs if l.get('entite'))
        data_stacked = dict(entites) if entites else {"Aucune donnée": 0}
        
        colors = {}
        for key in data_stacked.keys():
            colors[key] = ENTITE_COLORS.get(key, '#94a3b8')
        
        # Trier par valeur décroissante
        sorted_data = dict(sorted(data_stacked.items(), key=lambda x: -x[1]))
        
        self.stacked_bar.data = sorted_data
        self.stacked_bar.colors = colors
        self.stacked_bar.update()
        
        self.legend.set_data(sorted_data, colors)
        
        # ============================================================
        # Compteur
        # ============================================================
        self.lbl_results.setText(f"{len(logs)} résultats")

    def _clear_layout(self, layout):
        """Vide un layout de ses widgets"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
   
    def _render_table(self):
        start = (self._current_page - 1) * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        page_logs = self._filtered_logs[start:end]
        
        self.table.setRowCount(len(page_logs))
        
        # Masquer les colonnes vides
        has_champ = any(l.get('champ') for l in page_logs)
        has_change = any(l.get('change') for l in page_logs)
        self.table.setColumnHidden(5, not has_champ)
        self.table.setColumnHidden(6, not has_change)
        
        for i, log in enumerate(page_logs):
            # Date
            date_item = QTableWidgetItem(log.get('date', ''))
            date_item.setData(Qt.UserRole, log)
            self.table.setItem(i, 0, date_item)
            
            # Utilisateur avec avatar initial
            user_name = log.get('user', '')
            initials = ''.join([w[0] for w in user_name.split()[:2]]).upper() if user_name else '?'
            
            user_widget = QWidget()
            user_layout = QHBoxLayout(user_widget)
            user_layout.setContentsMargins(8, 4, 8, 4)
            user_layout.setSpacing(8)
            
            # Avatar circulaire
            avatar = QLabel(initials)
            avatar.setFixedSize(28, 28)
            avatar.setStyleSheet("""
                background-color: #e2e8f0;
                color: #475569;
                border-radius: 14px;
                font-weight: bold;
                font-size: 10px;
            """)
            avatar.setAlignment(Qt.AlignCenter)
            user_layout.addWidget(avatar)
            
            # Nom
            name_lbl = QLabel(user_name)
            name_lbl.setStyleSheet("font-size: 12px; color: #1e293b;")
            user_layout.addWidget(name_lbl, 1)
            
            self.table.setCellWidget(i, 1, user_widget)
            
            # Action (badge)
            action = log.get('action', '')
            action_item = QTableWidgetItem(action)
            bg, fg = ACTION_COLORS.get(action, ('#f1f5f9', '#64748b'))
            action_item.setBackground(QColor(bg))
            action_item.setForeground(QColor(fg))
            action_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, action_item)
            
            # Entité avec pastille
            entite = log.get('entite', '')
            entite_item = QTableWidgetItem(f"●  {entite}")
            entite_color = ENTITE_COLORS.get(entite, '#94a3b8')
            entite_item.setForeground(QColor(entite_color))
            self.table.setItem(i, 3, entite_item)
            
            # ID
            self.table.setItem(i, 4, QTableWidgetItem(log.get('id', '')))
            
            # Champ
            if has_champ:
                self.table.setItem(i, 5, QTableWidgetItem(log.get('champ', '') or ''))
            
            # Ancien → Nouveau
            if has_change:
                self.table.setItem(i, 6, QTableWidgetItem(log.get('change', '')))
        
        # Pagination
        total = len(self._filtered_logs)
        total_pages = max(1, (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        
        from datetime import datetime, timedelta
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        count_24h = sum(1 for l in self._filtered_logs
                        if l.get('date_iso') and
                        datetime.fromisoformat(l['date_iso']) >= yesterday)
        
        self.pagination.set_data(total, self._current_page, total_pages, count_24h)

    def _on_page_changed(self, page: int):
        self._current_page = page
        self._render_table()
    
    def _show_context_menu(self, pos):
        """Affiche le menu contextuel"""
        row = self.table.currentRow()
        if row < 0:
            return
        
        log_item = self.table.item(row, 1)
        if not log_item:
            return
        log = log_item.data(Qt.UserRole)
        if not log:
            return
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 8px 16px;
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
        
        action_detail = QAction("👁️  Voir les détails", self)
        action_detail.triggered.connect(lambda: self._show_log_details(log))
        menu.addAction(action_detail)
        
        action_filter = QAction(f"🔽  Filtrer par {log.get('user', 'utilisateur')}", self)
        action_filter.triggered.connect(lambda: self._filter_by_user(log.get('user')))
        menu.addAction(action_filter)
        
        menu.addSeparator()
        
        action_export = QAction("⬇️  Exporter", self)
        action_export.triggered.connect(lambda: self._export_log(log))
        menu.addAction(action_export)
        
        menu.exec(self.table.viewport().mapToGlobal(pos))
    
    def _show_log_details(self, log: dict):
        QMessageBox.information(
            self, "Détails du log",
            f"📅 Date: {log.get('date', 'N/A')}\n"
            f"👤 Utilisateur: {log.get('user', 'N/A')}\n"
            f"🔧 Action: {log.get('action', 'N/A')}\n"
            f"📦 Entité: {log.get('entite', 'N/A')}\n"
            f"🆔 ID: {log.get('id', 'N/A')}\n"
            f"📝 Champ: {log.get('champ', '—')}\n"
            f"🔄 Changement: {log.get('change', '—')}"
        )
    
    def _filter_by_user(self, username: str):
        """Filtre par utilisateur"""
        self._filtered_logs = [l for l in self._all_logs if l.get('user') == username]
        self._current_page = 1
        self._render_table()
    
    def _export_log(self, log: dict):
        """Exporte un log unique en CSV (simple)"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exporter le log",
            f"log_{log.get('id', 'unknown')}.csv",
            "CSV (*.csv)"
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Utilisateur", "Action", "Entité", "ID", "Champ", "Changement"])
                writer.writerow([
                    log.get('date', ''), log.get('user', ''),
                    log.get('action', ''), log.get('entite', ''),
                    log.get('id', ''), log.get('champ', ''), log.get('change', ''),
                ])
            QMessageBox.information(self, "Export", f"✅ Exporté vers {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")

    def _show_context_menu(self, pos):
        """Affiche le menu contextuel au clic droit"""
        row = self.table.currentRow()
        if row < 0:
            return
        
        # Récupérer le log via UserRole
        date_item = self.table.item(row, 0)
        if not date_item:
            return
        log = date_item.data(Qt.UserRole)
        if not log:
            return
        
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
        
        # Actions
        action_detail = QAction("👁️  Voir les détails", self)
        action_detail.triggered.connect(lambda: self._show_log_details(log))
        menu.addAction(action_detail)
        
        action_filter_user = QAction(f"👤  Filtrer par {log.get('user', 'utilisateur')}", self)
        action_filter_user.triggered.connect(lambda: self._filter_by_user(log.get('user')))
        menu.addAction(action_filter_user)
        
        action_filter_entite = QAction(f"📦  Filtrer par {log.get('entite', 'entité')}", self)
        action_filter_entite.triggered.connect(lambda: self._filter_by_entite(log.get('entite')))
        menu.addAction(action_filter_entite)
        
        menu.addSeparator()
        
        action_export = QAction("⬇️  Exporter (CSV)", self)
        action_export.triggered.connect(lambda: self._export_log(log))
        menu.addAction(action_export)
        
        action_export_all = QAction("📤  Exporter tout (CSV)", self)
        action_export_all.triggered.connect(self._export_all_filtered)
        menu.addAction(action_export_all)
        
        menu.addSeparator()
        
        action_copy = QAction("📋  Copier l'ID", self)
        action_copy.triggered.connect(lambda: self._copy_to_clipboard(log.get('id', '')))
        menu.addAction(action_copy)
        
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _filter_by_entite(self, entite: str):
        """Filtre par entité"""
        if not entite:
            return
        # Mettre à jour le combo
        for i in range(self.filter_entite.count()):
            if self.filter_entite.itemData(i) == entite:
                self.filter_entite.setCurrentIndex(i)
                break

    def _export_all_filtered(self):
        """Exporte tous les logs filtrés en CSV"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exporter tous les logs",
            "audit_logs.csv",
            "CSV (*.csv)"
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Utilisateur", "Action", "Entité", "ID", "Champ", "Changement"])
                for log in self._filtered_logs:
                    writer.writerow([
                        log.get('date', ''), log.get('user', ''),
                        log.get('action', ''), log.get('entite', ''),
                        log.get('id', ''), log.get('champ', ''), log.get('change', ''),
                    ])
            QMessageBox.information(self, "Export", f"✅ {len(self._filtered_logs)} logs exportés vers {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")

    def _copy_to_clipboard(self, text: str):
        """Copie un texte dans le presse-papiers"""
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copié", f"✅ '{text}' copié dans le presse-papiers")



class ParametresPage(QWidget):
    """Page de gestion des paramètres et des rôles"""
    # Palette qualitative pour les entités (contraste maximal)
    
    def __init__(self, referentiel_controller, user, reglement_controller=None, audit_controller=None, parent=None):
        super().__init__(parent)
        self.reglement_controller = reglement_controller
        self.referentiel_controller = referentiel_controller 
        self.audit_controller = audit_controller 
        self.user = user
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # En-tête
        header = QLabel("⚙️ Paramètres et administration")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)
        
        # Onglets
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 0 0 8px 8px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 2px;
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #1a73e8;
            }
            QTabBar::tab:hover {
                background-color: #f1f5f9;
            }
        """)
        
        # Onglet 1: Utilisateurs et rôles
        self.tabs.addTab(self.create_users_tab(), "👤 Utilisateurs et rôles")
        
        # Onglet 2: Paramètres généraux
        self.tabs.addTab(self.create_settings_tab(), "📋 Paramètres généraux")
        
        # Onglet 3: Audit et logs
        self.tabs.addTab(self.create_audit_tab(), "📜 Audit et logs")
        
        if self.reglement_controller:
            self.tab_banques = BanquesTab(self.reglement_controller, self.user)
            self.tabs.addTab(self.tab_banques, "🏦 Banques")
            
            # ✅ NOUVEAU : Onglet Comptes bancaires
            self.tab_comptes = ComptesBancairesTab(self.reglement_controller, self.user)
            self.tabs.addTab(self.tab_comptes, "💳 Comptes bancaires")
        
        layout.addWidget(self.tabs)
    
    def create_users_tab(self):
        """Crée l'onglet de gestion des utilisateurs et rôles"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Section: Rôles
        roles_group = QGroupBox("Rôles utilisateurs")
        roles_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        roles_layout = QVBoxLayout(roles_group)
        
        # Tableau des rôles
        self.table_roles = QTableWidget()
        self.table_roles.setColumnCount(6)
        self.table_roles.setHorizontalHeaderLabels([
            "ID", "Nom du rôle", "Description", "Utilisateurs", "Statut", "Actions"
        ])
        self.table_roles.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_roles.setAlternatingRowColors(True)
        self.table_roles.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        self.table_roles.setSortingEnabled(True)
        roles_layout.addWidget(self.table_roles)
        
        # Boutons rôles
        roles_btn_layout = QHBoxLayout()
        
        self.btn_ajouter_role = QPushButton("➕ Ajouter un rôle")
        self.btn_ajouter_role.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_ajouter_role.clicked.connect(self.ajouter_role)
        roles_btn_layout.addWidget(self.btn_ajouter_role)
        
        roles_btn_layout.addStretch()
        roles_layout.addLayout(roles_btn_layout)
        
        layout.addWidget(roles_group)
        
        # Section: Utilisateurs
        users_group = QGroupBox("Utilisateurs")
        users_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        users_layout = QVBoxLayout(users_group)
        
        # Tableau des utilisateurs
        self.table_users = QTableWidget()
        self.table_users.setColumnCount(7)
        self.table_users.setHorizontalHeaderLabels([
            "ID", "Nom", "Email", "Rôle", "Statut", "Dernière connexion", "Actions"
        ])
        self.table_users.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_users.setAlternatingRowColors(True)
        self.table_users.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        self.table_users.setSortingEnabled(True)
        users_layout.addWidget(self.table_users)
        
        # Boutons utilisateurs
        users_btn_layout = QHBoxLayout()
        
        self.btn_ajouter_user = QPushButton("➕ Ajouter un utilisateur")
        self.btn_ajouter_user.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_ajouter_user.clicked.connect(self.ajouter_utilisateur)
        users_btn_layout.addWidget(self.btn_ajouter_user)
        
        users_btn_layout.addStretch()
        users_layout.addLayout(users_btn_layout)

        # Section: Experts
        experts_group = QGroupBox("Experts")
        experts_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        experts_layout = QVBoxLayout(experts_group)

        # Tableau des experts
        self.table_experts = QTableWidget()
        self.table_experts.setColumnCount(7)
        self.table_experts.setHorizontalHeaderLabels([
            "Code", "Nom", "Agrément", "Domaines", "Mobile", "Statut", "Actions"
        ])
        self.table_experts.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_experts.setAlternatingRowColors(True)
        self.table_experts.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        self.table_experts.setSortingEnabled(True)
        experts_layout.addWidget(self.table_experts)

        # Bouton "Ajouter un expert"
        experts_btn_layout = QHBoxLayout()

        self.btn_ajouter_expert = QPushButton("➕ Enregistrer un expert")
        self.btn_ajouter_expert.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_ajouter_expert.clicked.connect(self.ajouter_expert)
        experts_btn_layout.addWidget(self.btn_ajouter_expert)

        experts_btn_layout.addStretch()
        experts_layout.addLayout(experts_btn_layout)

        layout.addWidget(experts_group)
        
        layout.addWidget(users_group)
        
        return tab
    
    # ============================================================
    # ONGLET 2: PARAMÈTRES GÉNÉRAUX
    # ============================================================
    
    def create_settings_tab(self):
        """Crée l'onglet des paramètres généraux"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Section: Paramètres de l'application
        app_group = QGroupBox("Paramètres de l'application")
        app_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        app_layout = QFormLayout(app_group)
        app_layout.setSpacing(12)
        
        # Langue
        self.input_langue = QComboBox()
        self.input_langue.addItems(["Français", "English"])
        app_layout.addRow("Langue:", self.input_langue)
        
        # Date format
        self.input_date_format = QComboBox()
        self.input_date_format.addItems(["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        app_layout.addRow("Format de date:", self.input_date_format)
        
        # Devise
        self.input_devise = QComboBox()
        self.input_devise.addItems(["XAF", "EUR", "USD"])
        app_layout.addRow("Devise par défaut:", self.input_devise)
        
        content_layout.addWidget(app_group)
        
        # Section: Paramètres des sinistres
        sinistre_group = QGroupBox("Paramètres des sinistres")
        sinistre_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        sinistre_layout = QFormLayout(sinistre_group)
        sinistre_layout.setSpacing(12)
        
        # Délai d'instruction
        self.input_delai_instruction = QLineEdit()
        self.input_delai_instruction.setPlaceholderText("30")
        sinistre_layout.addRow("Délai d'instruction (jours):", self.input_delai_instruction)
        
        # Délai d'expertise
        self.input_delai_expertise = QLineEdit()
        self.input_delai_expertise.setPlaceholderText("15")
        sinistre_layout.addRow("Délai d'expertise (jours):", self.input_delai_expertise)
        
        # Délai de règlement
        self.input_delai_reglement = QLineEdit()
        self.input_delai_reglement.setPlaceholderText("10")
        sinistre_layout.addRow("Délai de règlement (jours):", self.input_delai_reglement)
        
        content_layout.addWidget(sinistre_group)
        
        # Section: Notifications
        notif_group = QGroupBox("Notifications")
        notif_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        notif_layout = QFormLayout(notif_group)
        notif_layout.setSpacing(12)
        
        self.check_email = QCheckBox("Activer les notifications par email")
        self.check_email.setChecked(True)
        notif_layout.addRow("", self.check_email)
        
        self.check_sms = QCheckBox("Activer les notifications par SMS")
        notif_layout.addRow("", self.check_sms)
        
        content_layout.addWidget(notif_group)
        
        # Bouton sauvegarder
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_save_settings = QPushButton("💾 Sauvegarder les paramètres")
        self.btn_save_settings.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                padding: 10px 30px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        self.btn_save_settings.clicked.connect(self.sauvegarder_parametres)
        btn_layout.addWidget(self.btn_save_settings)
        
        content_layout.addLayout(btn_layout)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    # ============================================================
    # ONGLET 3: AUDIT ET LOGS
    # ============================================================
    
    def create_audit_tab(self):
        """Crée l'onglet d'audit et logs (version moderne)"""
        self.audit_tab = AuditTab(
            audit_controller=self.audit_controller,
            user=self.user,
        )
        return self.audit_tab
    
    # ============================================================
    # MÉTHODES DE CHARGEMENT
    # ============================================================
    
    def load_data(self):
        """Charge toutes les données"""
        self.load_roles()
        self.load_users()
        self.load_experts() 
         
    
    def load_roles(self):
        """Charge la liste des rôles"""
        # TODO: Récupérer les rôles depuis la base
        roles = [
            {'id': 1, 'nom': 'Admin', 'description': 'Accès complet', 'users': 1, 'actif': True},
            {'id': 2, 'nom': 'Gestionnaire', 'description': 'Gestion des sinistres', 'users': 5, 'actif': True},
            {'id': 3, 'nom': 'Responsable', 'description': 'Validation des évaluations', 'users': 2, 'actif': True},
            {'id': 4, 'nom': 'Expert', 'description': 'Expertise et rapports', 'users': 3, 'actif': True},
            {'id': 5, 'nom': 'Comptable', 'description': 'Paiements et comptabilité', 'users': 2, 'actif': True},
        ]
        self.update_roles_table(roles)
    
    def update_roles_table(self, roles: List[dict]):
        """Met à jour le tableau des rôles"""
        self.table_roles.setRowCount(len(roles))
        
        for i, role in enumerate(roles):
            self.table_roles.setItem(i, 0, QTableWidgetItem(str(role.get('id', ''))))
            self.table_roles.setItem(i, 1, QTableWidgetItem(role.get('nom', '')))
            self.table_roles.setItem(i, 2, QTableWidgetItem(role.get('description', '')))
            self.table_roles.setItem(i, 3, QTableWidgetItem(str(role.get('users', 0))))
            
            statut_item = QTableWidgetItem("✅ Actif" if role.get('actif') else "❌ Inactif")
            statut_item.setForeground(QColor("#22c55e" if role.get('actif') else "#ef4444"))
            self.table_roles.setItem(i, 4, statut_item)
            
            # Boutons d'action
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(5)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(30, 30)
            btn_edit.setStyleSheet("border-radius: 15px;")
            btn_edit.clicked.connect(lambda checked, r=role: self.editer_role(r))
            btn_layout.addWidget(btn_edit)
            
            btn_toggle = QPushButton("🔒" if role.get('actif') else "🔓")
            btn_toggle.setFixedSize(30, 30)
            btn_toggle.setStyleSheet("border-radius: 15px;")
            btn_toggle.clicked.connect(lambda checked, r=role: self.toggle_role(r))
            btn_layout.addWidget(btn_toggle)
            
            btn_layout.addStretch()
            self.table_roles.setCellWidget(i, 5, btn_widget)
    
    def load_users(self):
        """Charge la liste des utilisateurs"""
        # TODO: Récupérer les utilisateurs depuis la base
        users = [
            {'id': 1, 'nom': 'Jean Dupont', 'email': 'jean@example.com', 'role': 'Admin', 'actif': True, 'last_login': '2026-09-07 10:30'},
            {'id': 2, 'nom': 'Marie Martin', 'email': 'marie@example.com', 'role': 'Gestionnaire', 'actif': True, 'last_login': '2026-09-07 09:15'},
            {'id': 3, 'nom': 'Pierre Durand', 'email': 'pierre@example.com', 'role': 'Expert', 'actif': True, 'last_login': '2026-09-06 16:45'},
        ]
        self.update_users_table(users)
    
    def update_users_table(self, users: List[dict]):
        """Met à jour le tableau des utilisateurs"""
        self.table_users.setRowCount(len(users))
        
        for i, user in enumerate(users):
            self.table_users.setItem(i, 0, QTableWidgetItem(str(user.get('id', ''))))
            self.table_users.setItem(i, 1, QTableWidgetItem(user.get('nom', '')))
            self.table_users.setItem(i, 2, QTableWidgetItem(user.get('email', '')))
            self.table_users.setItem(i, 3, QTableWidgetItem(user.get('role', '')))
            
            statut_item = QTableWidgetItem("✅ Actif" if user.get('actif') else "❌ Inactif")
            statut_item.setForeground(QColor("#22c55e" if user.get('actif') else "#ef4444"))
            self.table_users.setItem(i, 4, statut_item)
            
            self.table_users.setItem(i, 5, QTableWidgetItem(user.get('last_login', '')))
            
            # Boutons d'action
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(5)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(30, 30)
            btn_edit.setStyleSheet("border-radius: 15px;")
            btn_edit.clicked.connect(lambda checked, u=user: self.editer_utilisateur(u))
            btn_layout.addWidget(btn_edit)
            
            btn_toggle = QPushButton("🔒" if user.get('actif') else "🔓")
            btn_toggle.setFixedSize(30, 30)
            btn_toggle.setStyleSheet("border-radius: 15px;")
            btn_toggle.clicked.connect(lambda checked, u=user: self.toggle_utilisateur(u))
            btn_layout.addWidget(btn_toggle)
            
            btn_layout.addStretch()
            self.table_users.setCellWidget(i, 6, btn_widget)
    
    def load_audit(self):
        """Charge les logs d'audit"""
        # TODO: Récupérer les logs depuis la base
        logs = [
            {'date': '2026-09-07 10:30', 'user': 'Jean Dupont', 'action': 'CREATION', 'entite': 'Sinistre', 'id': 'SIN-2026-000001', 'champ': '', 'change': ''},
            {'date': '2026-09-07 10:35', 'user': 'Jean Dupont', 'action': 'MODIFICATION', 'entite': 'Sinistre', 'id': 'SIN-2026-000001', 'champ': 'statut', 'change': 'OUVERT → EN_INSTRUCTION'},
        ]
        self.update_audit_table(logs)
    
    def update_audit_table(self, logs: List[dict]):
        """Met à jour le tableau d'audit"""
        self.table_audit.setRowCount(len(logs))
        
        action_colors = {
            'CREATION': '#22c55e',
            'MODIFICATION': '#f59e0b',
            'VALIDATION': '#3b82f6',
            'SUPPRESSION': '#ef4444',
            'CHANGEMENT_STATUT': '#8b5cf6'
        }
        
        for i, log in enumerate(logs):
            self.table_audit.setItem(i, 0, QTableWidgetItem(log.get('date', '')))
            self.table_audit.setItem(i, 1, QTableWidgetItem(log.get('user', '')))
            
            action_item = QTableWidgetItem(log.get('action', ''))
            color = action_colors.get(log.get('action', ''), '#64748b')
            action_item.setBackground(QColor(color))
            action_item.setForeground(QColor('white'))
            self.table_audit.setItem(i, 2, action_item)
            
            self.table_audit.setItem(i, 3, QTableWidgetItem(log.get('entite', '')))
            self.table_audit.setItem(i, 4, QTableWidgetItem(log.get('id', '')))
            self.table_audit.setItem(i, 5, QTableWidgetItem(log.get('champ', '')))
            self.table_audit.setItem(i, 6, QTableWidgetItem(log.get('change', '')))
        
        self.lbl_total_logs.setText(f"Total: {len(logs)}")
        self.lbl_actions_24h.setText(f"24h: {len([l for l in logs if '2026-09-07' in l.get('date', '')])}")
    
    # ============================================================
    # ACTIONS RÔLES
    # ============================================================
    
    def ajouter_role(self):
        """Ouvre le dialogue d'ajout de rôle"""
        QMessageBox.information(self, "Ajout rôle", "Dialogue d'ajout de rôle (à implémenter)")
    
    def editer_role(self, role: dict):
        """Ouvre le dialogue d'édition de rôle"""
        QMessageBox.information(self, "Édition rôle", f"Édition du rôle {role.get('nom')} (à implémenter)")
    
    def toggle_role(self, role: dict):
        """Active/désactive un rôle"""
        QMessageBox.information(self, "Toggle rôle", f"Activation/désactivation du rôle {role.get('nom')} (à implémenter)")
    
    # ============================================================
    # ACTIONS UTILISATEURS
    # ============================================================
    
    def ajouter_utilisateur(self):
        """Ouvre le dialogue d'ajout d'utilisateur"""
        QMessageBox.information(self, "Ajout utilisateur", "Dialogue d'ajout d'utilisateur (à implémenter)")
    
    def editer_utilisateur(self, user: dict):
        """Ouvre le dialogue d'édition d'utilisateur"""
        QMessageBox.information(self, "Édition utilisateur", f"Édition de l'utilisateur {user.get('nom')} (à implémenter)")
    
    def toggle_utilisateur(self, user: dict):
        """Active/désactive un utilisateur"""
        QMessageBox.information(self, "Toggle utilisateur", f"Activation/désactivation de l'utilisateur {user.get('nom')} (à implémenter)")
    
    # ============================================================
    # PARAMÈTRES
    # ============================================================
    
    def sauvegarder_parametres(self):
        """Sauvegarde les paramètres"""
        QMessageBox.information(self, "Sauvegarde", "Paramètres sauvegardés avec succès !")


    # ============================================================
    # EXPERTS
    # ============================================================

    def load_experts(self):
        try:
            from addons.sinistres.controllers.expertise_controller import ExpertiseController
            ec = ExpertiseController()
            ec.set_current_user(self.user)
            experts = ec.get_experts_actifs() or []  # ✅
            self.update_experts_table(experts)
        except Exception as e:
            print(f"Erreur chargement experts: {e}")
            self.update_experts_table([])

    def update_experts_table(self, experts: List[dict]):
        """Met à jour le tableau des experts"""
        self.table_experts.setRowCount(len(experts))
        
        for i, exp in enumerate(experts):
            # Code
            self.table_experts.setItem(i, 0, QTableWidgetItem(exp.get('code', '') or ''))
            
            # Nom complet
            nom_complet = f"{exp.get('nom', '')} {exp.get('prenom', '') or ''}".strip()
            self.table_experts.setItem(i, 1, QTableWidgetItem(nom_complet))
            
            # Agrément
            self.table_experts.setItem(i, 2, QTableWidgetItem(exp.get('agrement', '') or ''))
            
            # Domaines
            domaines = exp.get('domaines') or []
            self.table_experts.setItem(i, 3, QTableWidgetItem(", ".join(domaines) if isinstance(domaines, list) else str(domaines)))
            
            # Mobile
            self.table_experts.setItem(i, 4, QTableWidgetItem(exp.get('portable', '') or ''))
            
            # Statut
            actif = exp.get('est_actif', True)
            statut_item = QTableWidgetItem("✅ Actif" if actif else "❌ Inactif")
            statut_item.setForeground(QColor("#22c55e" if actif else "#ef4444"))
            self.table_experts.setItem(i, 5, statut_item)
            
            # Boutons d'action
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(5)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(30, 30)
            btn_edit.setStyleSheet("border-radius: 15px;")
            btn_edit.clicked.connect(lambda checked, e=exp: self.editer_expert(e))
            btn_layout.addWidget(btn_edit)
            
            btn_toggle = QPushButton("🔒" if actif else "🔓")
            btn_toggle.setFixedSize(30, 30)
            btn_toggle.setStyleSheet("border-radius: 15px;")
            btn_toggle.clicked.connect(lambda checked, e=exp: self.toggle_expert(e))
            btn_layout.addWidget(btn_toggle)
            
            btn_layout.addStretch()
            self.table_experts.setCellWidget(i, 6, btn_widget)


    def ajouter_expert(self):
        """Ouvre le dialogue d'enregistrement d'expert"""
        try:
            from addons.sinistres.controllers.expertise_controller import ExpertiseController
            expertise_controller = ExpertiseController()
            expertise_controller.set_current_user(self.user)
            
            dialog = ExpertDialog(
                expert_controller=expertise_controller,
                user=self.user,
                referentiel_controller=self.reglement_controller,
                parent=self
            )
            dialog.expert_saved.connect(self._on_expert_saved)
            dialog.exec()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le dialogue: {str(e)}")


    def editer_expert(self, expert: dict):
        """Ouvre le dialogue d'édition d'expert"""
        try:
            from addons.sinistres.controllers.expertise_controller import ExpertiseController
            expertise_controller = ExpertiseController()
            expertise_controller.set_current_user(self.user)
            
            dialog = ExpertDialog(
                expert_controller=expertise_controller,
                user=self.user,
                expert_data=expert,
                referentiel_controller=self.reglement_controller,
                parent=self
            )
            dialog.expert_saved.connect(self._on_expert_saved)
            dialog.exec()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le dialogue: {str(e)}")


    def toggle_expert(self, expert: dict):
        """Active/désactive un expert"""
        expert_id = expert.get('id')
        nom = f"{expert.get('nom', '')} {expert.get('prenom', '') or ''}".strip()
        actif = expert.get('est_actif', True)
        
        action = "désactiver" if actif else "activer"
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous {action} l'expert {nom} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            from addons.sinistres.controllers.expertise_controller import ExpertiseController
            ec = ExpertiseController()
            ec.set_current_user(self.user)
            
            result = ec.toggle_expert(expert_id, not actif)
            if result:
                QMessageBox.information(self, "Succès", f"Expert {action} avec succès")
                self.load_experts()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


    def _on_expert_saved(self, data: dict):
        """Appelé après enregistrement d'un expert"""
        self.load_experts()

    def _style_table_uniform(self, table):
        """Style moderne uniforme pour tous les tableaux"""
        table.setStyleSheet("""
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
            QTableWidget::item:selected { background: #eff6ff; color: #1e293b; }
            QTableWidget::item:hover { background: #f8fafc; }
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
            QScrollBar:vertical { background: transparent; width: 8px; margin: 0; }
            QScrollBar::handle:vertical {
                background: #cbd5e1; border-radius: 4px; min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #94a3b8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(52)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setShowGrid(False)
        table.setAlternatingRowColors(False)


    def _show_any_table_context_menu(self, table, pos):
        """Menu contextuel universel pour les tableaux Rôles/Users/Experts"""
        row = table.currentRow()
        if row < 0:
            # Menu vide
            menu = QMenu(self)
            menu.setStyleSheet(self._menu_style_uniform())
            a = menu.addAction("🔄  Actualiser")
            a.triggered.connect(self.load_data)
            menu.exec(table.viewport().mapToGlobal(pos))
            return
        
        # Déterminer le type de tableau
        if table is self.table_roles:
            item = table.item(row, 0)
            if item:
                data = item.data(Qt.UserRole) or self._dict_from_role_row(table, row)
                self._build_role_context_menu(data, table.viewport().mapToGlobal(pos))
        elif table is self.table_users:
            item = table.item(row, 0)
            if item:
                data = item.data(Qt.UserRole) or self._dict_from_user_row(table, row)
                self._build_user_context_menu(data, table.viewport().mapToGlobal(pos))
        elif table is self.table_experts:
            item = table.item(row, 0)
            if item:
                data = item.data(Qt.UserRole) or self._dict_from_expert_row(table, row)
                self._build_expert_context_menu(data, table.viewport().mapToGlobal(pos))


    def _menu_style_uniform(self):
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
            QMenu::item:selected { background: #eff6ff; color: #2563eb; }
            QMenu::item:disabled { color: #94a3b8; }
            QMenu::separator {
                height: 1px;
                background: #f1f5f9;
                margin: 4px 8px;
            }
        """


    def _build_role_context_menu(self, role, pos):
        """Menu contextuel pour un rôle"""
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style_uniform())
        
        a_view = menu.addAction("👁️  Voir les détails")
        a_view.triggered.connect(lambda: self._show_role_detail(role))
        
        menu.addSeparator()
        
        a_edit = menu.addAction("✏️  Modifier")
        a_edit.triggered.connect(lambda: self.editer_role(role))
        
        a_toggle = menu.addAction("🚫  Désactiver" if role.get('est_actif', True) else "✓  Réactiver")
        a_toggle.triggered.connect(lambda: self.toggle_role(role))
        
        menu.addSeparator()
        
        a_perm = menu.addAction("🔑  Éditer les permissions")
        a_perm.triggered.connect(lambda: self._open_permissions_for_role(role))
        
        menu.addSeparator()
        
        a_copy = menu.addAction("📋  Copier le code")
        a_copy.triggered.connect(lambda: self._copy_role_code(role))
        
        menu.exec(pos)


    def _build_user_context_menu(self, user, pos):
        """Menu contextuel pour un utilisateur"""
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style_uniform())
        
        a_view = menu.addAction("👁️  Voir les détails")
        a_view.triggered.connect(lambda: self._show_user_detail(user))
        
        menu.addSeparator()
        
        a_edit = menu.addAction("✏️  Modifier")
        a_edit.triggered.connect(lambda: self.editer_utilisateur(user))
        
        a_toggle = menu.addAction("🚫  Désactiver" if user.get('est_actif', True) else "✓  Activer")
        a_toggle.triggered.connect(lambda: self.toggle_utilisateur(user))
        
        menu.addSeparator()
        
        a_reset = menu.addAction("🔑  Réinitialiser mot de passe")
        a_reset.triggered.connect(lambda: self._reset_password(user))
        
        menu.addSeparator()
        
        a_copy = menu.addAction("📋  Copier l'email")
        a_copy.triggered.connect(lambda: self._copy_text(user.get('email', '')))
        
        menu.exec(pos)


    def _build_expert_context_menu(self, expert, pos):
        """Menu contextuel pour un expert"""
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style_uniform())
        
        a_view = menu.addAction("👁️  Voir les détails")
        a_view.triggered.connect(lambda: self._show_expert_detail(expert))
        
        menu.addSeparator()
        
        a_edit = menu.addAction("✏️  Modifier")
        a_edit.triggered.connect(lambda: self.editer_expert(expert))
        
        a_toggle = menu.addAction("🚫  Désactiver" if expert.get('est_actif', True) else "✓  Activer")
        a_toggle.triggered.connect(lambda: self.toggle_expert(expert))
        
        menu.addSeparator()
        
        a_copy = menu.addAction("📋  Copier le code")
        a_copy.triggered.connect(lambda: self._copy_text(expert.get('code', '')))
        
        menu.exec(pos)


    # -- HELPERS --

    def _dict_from_role_row(self, table, row):
        return {
            'id': table.item(row, 0).text() if table.item(row, 0) else '',
            'code': table.item(row, 0).text() if table.item(row, 0) else '',
            'libelle': table.item(row, 1).text() if table.item(row, 1) else '',
            'description': table.item(row, 2).text() if table.item(row, 2) else '',
            'est_actif': True,
        }

    def _dict_from_user_row(self, table, row):
        return {
            'id': table.item(row, 0).text() if table.item(row, 0) else '',
            'username': table.item(row, 1).text() if table.item(row, 1) else '',
            'nom_complet': table.item(row, 1).text() if table.item(row, 1) else '',
            'email': table.item(row, 2).text() if table.item(row, 2) else '',
            'est_actif': True,
        }

    def _dict_from_expert_row(self, table, row):
        return {
            'code': table.item(row, 0).text() if table.item(row, 0) else '',
            'nom': table.item(row, 1).text() if table.item(row, 1) else '',
            'prenom': '',
            'agrement': table.item(row, 2).text() if table.item(row, 2) else '',
            'est_actif': True,
        }

    def _show_role_detail(self, role):
        QMessageBox.information(self, f"Rôle {role.get('code', role.get('nom', 'N/A'))}",
            f"📋 Code : {role.get('code', role.get('nom', 'N/A'))}\n"
            f"📝 Libellé : {role.get('libelle', role.get('nom', ''))}\n"
            f"📄 Description : {role.get('description', '—') or '—'}\n"
            f"📌 Statut : {'✅ Actif' if role.get('est_actif', True) else '❌ Inactif'}")

    def _show_user_detail(self, user):
        QMessageBox.information(self, f"Utilisateur {user.get('username', user.get('nom', 'N/A'))}",
            f"👤 Username : {user.get('username', user.get('nom', ''))}\n"
            f"📧 Email : {user.get('email', '—')}\n"
            f"📌 Statut : {'✅ Actif' if user.get('est_actif', True) else '❌ Inactif'}")

    def _show_expert_detail(self, expert):
        QMessageBox.information(self, f"Expert {expert.get('nom', 'N/A')}",
            f"🔖 Code : {expert.get('code', '—')}\n"
            f"👤 Nom : {expert.get('nom', '')} {expert.get('prenom', '')}\n"
            f"📋 Agrément : {expert.get('agrement', '—')}\n"
            f"📌 Statut : {'✅ Actif' if expert.get('est_actif', True) else '❌ Inactif'}")

    def _open_permissions_for_role(self, role):
        QMessageBox.information(self, "Permissions",
            f"Éditer les permissions de {role.get('code', role.get('nom'))} (à implémenter)")

    def _reset_password(self, user):
        reply = QMessageBox.question(self, "Confirmation",
            f"Réinitialiser le mot de passe de {user.get('username', user.get('nom'))} ?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Info", "Réinitialisation à implémenter")

    def _copy_role_code(self, role):
        self._copy_text(role.get('code', ''))

    def _copy_text(self, text):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(str(text))
        QMessageBox.information(self, "Copié", f"✅ '{text}' copié")








