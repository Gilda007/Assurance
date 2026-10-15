
"""
Vue principale du module LOMETA Sinistres
Interface utilisateur complète pour la gestion des évaluations
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
from typing import Optional, List


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def _safe_bool(value) -> bool:
    """Convertit n'importe quelle valeur en booléen sûr (évite les None)"""
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
            font-size: 22px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)
        value_lbl.setObjectName("stat_value")
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(value_lbl)
        
        layout.addLayout(text_layout, 1)


class StatusBadge(QLabel):
    """Badge arrondi pour le statut de validation avec icône FontAwesome"""
    
    def __init__(self, is_valid: bool, parent=None):
        super().__init__(parent)
        
        if is_valid:
            bg, fg, label, icon_name = "#d1fae5", "#065f46", "Validée", "fa5s.check-circle"
        else:
            bg, fg, label, icon_name = "#fed7aa", "#9a3412", "En attente", "fa5s.hourglass-half"
        
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


class BoolBadge(QLabel):
    """Badge booléen pour Provisions avec icône FontAwesome"""
    
    def __init__(self, value: bool, true_label: str = "Oui", false_label: str = "Non", parent=None):
        super().__init__(parent)
        
        if value:
            bg, fg = "#d1fae5", "#065f46"
            label = true_label
            icon_name = "fa5s.check"
        else:
            bg, fg = "#fee2e2", "#991b1b"
            label = false_label
            icon_name = "fa5s.times"
        
        self.setText(f"  {label}  ")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 700;
                border: none;
            }}
        """)
        self.setFixedHeight(20)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)


# ═══════════════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════

class EvaluationsPage(QWidget):
    """Page de gestion des évaluations — Design moderne v2.0"""
    
    def __init__(self, controller, user):
        super().__init__()
        self.controller = controller
        self.user = user
        
        # Permissions
        from addons.sinistres.services.permission_service import PermissionService
        from addons.sinistres.security.permissions_helper import PermissionsUI
        self.permission_service = PermissionService()
        self.permissions_ui = PermissionsUI(user, self.permission_service)
        
        self.current_sinistre_id = None
        self.selected_evaluation_id = None
        
        # Pagination évaluations
        self._current_page = 1
        self._per_page = 15
        self._total_evaluations = 0
        
        # Pagination provisions
        self._prov_current_page = 1
        self._prov_per_page = 15
        self._total_provisions = 0
        
        self.setup_ui()
        self._appliquer_permissions()
        self.load_data()
    
    def _appliquer_permissions(self):
        """Cache les boutons selon les permissions"""
        self.permissions_ui.masquer_si_non_autorise(
            self.btn_creer_eval, 'evaluation', 'CREATE'
        )
        self.permissions_ui.masquer_si_non_autorise(
            self.btn_reviser_eval, 'evaluation', 'UPDATE'
        )
        self.permissions_ui.masquer_si_non_autorise(
            self.btn_valider_eval, 'evaluation', 'VALIDATE'
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
        layout.addWidget(self._build_tabs_card(), 1)
        layout.addWidget(self._build_secondary_actions())
    
    def _build_header(self):
        """En-tête : titre + filtre sinistre + bouton Nouvelle Évaluation"""
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
        icon_lbl.setPixmap(qta.icon('fa5s.calculator', color='#2563eb').pixmap(QSize(24, 24)))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_lbl)
        
        layout.addWidget(icon_container)
        
        # Titre + sous-titre
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title = QLabel("Gestion des Évaluations")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
            background: transparent;
        """)
        title_block.addWidget(title)
        
        subtitle = QLabel("Suivi des évaluations et provisions")
        subtitle.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        title_block.addWidget(subtitle)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        # Filtre sinistre
        sinistre_label = QLabel("Sinistre :")
        sinistre_label.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        layout.addWidget(sinistre_label)
        
        self.sinistre_combo = QComboBox()
        self.sinistre_combo.setMinimumWidth(220)
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
        
        # ✅ Bouton Nouvelle Évaluation
        self.btn_creer_eval = QPushButton("  Nouvelle Évaluation")
        self.btn_creer_eval.setCursor(Qt.PointingHandCursor)
        self.btn_creer_eval.setFixedHeight(38)
        self.btn_creer_eval.setIcon(qta.icon('fa5s.plus-circle', color='white'))
        self.btn_creer_eval.setIconSize(QSize(14, 14))
        self.btn_creer_eval.setStyleSheet("""
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
        self.btn_creer_eval.clicked.connect(self.creer_evaluation)
        layout.addWidget(self.btn_creer_eval)
        
        return frame
    
    def _build_stats_row(self):
        """Rangée de 4 cartes statistiques avec icônes FontAwesome"""
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        
        self.card_total = StatCard(
            icon_name="fa5s.coins", 
            title="Total évalué", value="0 FCFA",
            color_bg="#dbeafe", color_fg="#1e40af"
        )
        self.card_validees = StatCard(
            icon_name="fa5s.check-double", 
            title="Validées", value="0",
            color_bg="#d1fae5", color_fg="#059669"
        )
        self.card_non_validees = StatCard(
            icon_name="fa5s.hourglass-half", 
            title="En attente", value="0",
            color_bg="#fed7aa", color_fg="#ea580c"
        )
        self.card_provisions = StatCard(
            icon_name="fa5s.box", 
            title="Provisions actives", value="0",
            color_bg="#ede9fe", color_fg="#6d28d9"
        )
        
        layout.addWidget(self.card_total)
        layout.addWidget(self.card_validees)
        layout.addWidget(self.card_non_validees)
        layout.addWidget(self.card_provisions)
        
        return wrapper
    
    def _build_tabs_card(self):
        """Carte contenant les onglets Évaluations et Provisions"""
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
        
        # ─── Tabs ───
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar {
                background: transparent;
            }
            QTabBar::tab {
                padding: 12px 24px;
                background-color: transparent;
                border: none;
                border-bottom: 2px solid transparent;
                color: #64748b;
                font-size: 13px;
                font-weight: 600;
                margin-right: 4px;
            }
            QTabBar::tab:hover {
                color: #1e293b;
            }
            QTabBar::tab:selected {
                color: #2563eb;
                border-bottom: 2px solid #2563eb;
            }
        """)
        
        # ═══ Onglet 1 : Évaluations ═══
        eval_tab = self._build_evaluations_tab()
        self.sub_tabs.addTab(eval_tab, "  Évaluations  ")
        
        # ═══ Onglet 2 : Provisions ═══
        prov_tab = self._build_provisions_tab()
        self.sub_tabs.addTab(prov_tab, "  Provisions  ")
        
        layout.addWidget(self.sub_tabs)
        return card
    
    # ═══════════════════════════════════════════════════════════════
    # ONGLET ÉVALUATIONS
    # ═══════════════════════════════════════════════════════════════
    
    def _build_evaluations_tab(self):
        """Construit l'onglet des évaluations"""
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(tab)
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
        
        title = QLabel("Liste des Évaluations")
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
        self.eval_search = QLineEdit()
        self.eval_search.setPlaceholderText("Recherche")
        self.eval_search.setFixedWidth(200)
        self.eval_search.setStyleSheet("""
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
        self.eval_search.textChanged.connect(self._on_eval_search_changed)
        header_layout.addWidget(self.eval_search)
        
        # Filtre validation
        self.eval_filter = QComboBox()
        self.eval_filter.addItems([
            "Toutes", "Validées", "Non validées"
        ])
        self.eval_filter.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #1e293b;
                min-width: 130px;
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
        self.eval_filter.currentTextChanged.connect(self._on_eval_filter_changed)
        header_layout.addWidget(self.eval_filter)
        
        # ✅ Bouton export avec icône download
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
        btn_export.clicked.connect(self._export_evaluations)
        header_layout.addWidget(btn_export)
        
        layout.addWidget(header)
        
        # ─── Tableau ───
        self.table_evaluations = QTableWidget()
        self.table_evaluations.setColumnCount(8)
        self.table_evaluations.setHorizontalHeaderLabels([
            "N° Évaluation", "Type", "Brut", "Franchise",
            "Taux", "Net", "Statut", "Actions"
        ])
        
        self.table_evaluations.setStyleSheet("""
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
        
        self.table_evaluations.setAlternatingRowColors(False)
        self.table_evaluations.verticalHeader().setVisible(False)
        self.table_evaluations.verticalHeader().setDefaultSectionSize(52)
        self.table_evaluations.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_evaluations.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_evaluations.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_evaluations.setShowGrid(False)
        
        # Largeurs
        header_view = self.table_evaluations.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table_evaluations.setColumnWidth(7, 60)
        
        # Signaux
        self.table_evaluations.itemSelectionChanged.connect(self._on_evaluation_selection_changed)
        self.table_evaluations.doubleClicked.connect(self._on_evaluation_double_clicked)
        
        # Menu contextuel
        self.table_evaluations.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_evaluations.customContextMenuRequested.connect(
            self._show_evaluation_context_menu
        )
        
        layout.addWidget(self.table_evaluations)
        
        # ─── Pagination ───
        pagination = self._build_pagination("eval")
        layout.addWidget(pagination)
        
        return tab
    
    # ═══════════════════════════════════════════════════════════════
    # ONGLET PROVISIONS
    # ═══════════════════════════════════════════════════════════════
    
    def _build_provisions_tab(self):
        """Construit l'onglet des provisions"""
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(tab)
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
        
        # ✅ Titre avec icône box
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('fa5s.boxes', color='#7c3aed').pixmap(QSize(14, 14)))
        title_row.addWidget(title_icon)
        
        title = QLabel("Liste des Provisions")
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
        self.prov_search = QLineEdit()
        self.prov_search.setPlaceholderText("Recherche")
        self.prov_search.setFixedWidth(200)
        self.prov_search.setStyleSheet("""
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
        self.prov_search.textChanged.connect(self._on_prov_search_changed)
        header_layout.addWidget(self.prov_search)
        
        # Filtre actif
        self.prov_filter = QComboBox()
        self.prov_filter.addItems([
            "Toutes", "Actives", "Inactives", "Comptabilisées"
        ])
        self.prov_filter.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #1e293b;
                min-width: 140px;
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
        self.prov_filter.currentTextChanged.connect(self._on_prov_filter_changed)
        header_layout.addWidget(self.prov_filter)
        
        # Export
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
        btn_export.clicked.connect(self._export_provisions)
        header_layout.addWidget(btn_export)
        
        layout.addWidget(header)
        
        # ─── Tableau ───
        self.table_provisions = QTableWidget()
        self.table_provisions.setColumnCount(6)
        self.table_provisions.setHorizontalHeaderLabels([
            "N° Provision", "Type", "Montant", "Active",
            "Comptabilisée", "Actions"
        ])
        
        self.table_provisions.setStyleSheet("""
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
        """)
        
        self.table_provisions.setAlternatingRowColors(False)
        self.table_provisions.verticalHeader().setVisible(False)
        self.table_provisions.verticalHeader().setDefaultSectionSize(52)
        self.table_provisions.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_provisions.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_provisions.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_provisions.setShowGrid(False)
        
        # Largeurs
        prov_header = self.table_provisions.horizontalHeader()
        prov_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        prov_header.setSectionResizeMode(1, QHeaderView.Stretch)
        prov_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        prov_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        prov_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        prov_header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table_provisions.setColumnWidth(5, 60)
        
        # Menu contextuel
        self.table_provisions.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_provisions.customContextMenuRequested.connect(
            self._show_provisions_context_menu
        )
        
        layout.addWidget(self.table_provisions)
        
        # ─── Pagination ───
        pagination = self._build_pagination("prov")
        layout.addWidget(pagination)
        
        return tab
    
    def _build_pagination(self, kind: str):
        """Construit une barre de pagination (eval ou prov)"""
        pagination = QFrame()
        pagination.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-top: 1px solid #f1f5f9;
            }
        """)
        layout = QHBoxLayout(pagination)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(10)
        
        layout.addStretch()
        
        if kind == "eval":
            self.lbl_pagination = QLabel("0-0 de 0")
            self.lbl_pagination.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
            layout.addWidget(self.lbl_pagination)
            
            # ✅ Bouton prev avec icône
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
            layout.addWidget(self.btn_prev)
            
            # ✅ Bouton next avec icône
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
            layout.addWidget(self.btn_next)
        
        else:  # prov
            self.lbl_pagination_prov = QLabel("0-0 de 0")
            self.lbl_pagination_prov.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
            layout.addWidget(self.lbl_pagination_prov)
            
            self.btn_prev_prov = QPushButton("  Précédent")
            self.btn_prev_prov.setCursor(Qt.PointingHandCursor)
            self.btn_prev_prov.setIcon(qta.icon('fa5s.chevron-left', color='#3b82f6'))
            self.btn_prev_prov.setIconSize(QSize(10, 10))
            self.btn_prev_prov.setStyleSheet("""
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
            self.btn_prev_prov.clicked.connect(self._go_prev_page_prov)
            layout.addWidget(self.btn_prev_prov)
            
            self.btn_next_prov = QPushButton("Suivant  ")
            self.btn_next_prov.setCursor(Qt.PointingHandCursor)
            self.btn_next_prov.setIcon(qta.icon('fa5s.chevron-right', color='#3b82f6'))
            self.btn_next_prov.setIconSize(QSize(10, 10))
            self.btn_next_prov.setLayoutDirection(Qt.RightToLeft)
            self.btn_next_prov.setStyleSheet("""
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
            self.btn_next_prov.clicked.connect(self._go_next_page_prov)
            layout.addWidget(self.btn_next_prov)
        
        return pagination
    
    def _build_secondary_actions(self):
        """Barre d'actions secondaires (Réviser, Valider)"""
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
        
        # ✅ Bouton Réviser
        self.btn_reviser_eval = QPushButton("  Réviser")
        self.btn_reviser_eval.setCursor(Qt.PointingHandCursor)
        self.btn_reviser_eval.setIcon(qta.icon('fa5s.edit', color='#d97706'))
        self.btn_reviser_eval.setIconSize(QSize(14, 14))
        self.btn_reviser_eval.setStyleSheet(btn_style % ("#f59e0b", "#d97706"))
        self.btn_reviser_eval.clicked.connect(self.reviser_evaluation)
        self.btn_reviser_eval.setEnabled(False)
        layout.addWidget(self.btn_reviser_eval)
        
        # ✅ Bouton Valider
        self.btn_valider_eval = QPushButton("  Valider")
        self.btn_valider_eval.setCursor(Qt.PointingHandCursor)
        self.btn_valider_eval.setIcon(qta.icon('fa5s.check', color='#16a34a'))
        self.btn_valider_eval.setIconSize(QSize(14, 14))
        self.btn_valider_eval.setStyleSheet(btn_style % ("#22c55e", "#16a34a"))
        self.btn_valider_eval.clicked.connect(self.valider_evaluation)
        self.btn_valider_eval.setEnabled(False)
        layout.addWidget(self.btn_valider_eval)
        
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
        except Exception as e:
            print(f"Erreur chargement sinistres: {e}")
    
    def on_sinistre_changed(self, index):
        """Charge les données du sinistre sélectionné"""
        sinistre_id = self.sinistre_combo.currentData()
        self.current_sinistre_id = sinistre_id
        
        self._current_page = 1
        self._prov_current_page = 1
        
        if sinistre_id is None:
            self.load_all_evaluations()
            self.load_all_provisions()
        else:
            self.load_evaluations(sinistre_id)
            self.load_provisions(sinistre_id)
    
    def load_evaluations(self, sinistre_id: int):
        try:
            evaluations = self.controller.get_evaluations_by_sinistre(sinistre_id)
            self._process_evaluations(evaluations)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement évaluations: {str(e)}")
    
    def load_all_evaluations(self):
        try:
            evaluations = self.controller.get_all_evaluations()
            self._process_evaluations(evaluations)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement évaluations: {str(e)}")
    
    def _process_evaluations(self, evaluations: list):
        query = self.eval_search.text().strip().lower() if hasattr(self, 'eval_search') else ""
        if query:
            evaluations = [
                e for e in evaluations
                if query in str(e.get('numero_evaluation', '')).lower()
                or query in str(e.get('type_evaluation', '')).lower()
            ]
        
        filter_val = self.eval_filter.currentText() if hasattr(self, 'eval_filter') else "Toutes"
        if filter_val == "Validées":
            evaluations = [e for e in evaluations if e.get('est_validee')]
        elif filter_val == "Non validées":
            evaluations = [e for e in evaluations if not e.get('est_validee')]
        
        self._total_evaluations = len(evaluations)
        
        start = (self._current_page - 1) * self._per_page
        end = start + self._per_page
        page_data = evaluations[start:end]
        
        self._update_stats(evaluations)
        
        self.table_evaluations.setRowCount(len(page_data))
        for i, ev in enumerate(page_data):
            self._fill_evaluation_row(i, ev)
        
        self._update_pagination(start, min(end, self._total_evaluations))
        
        self.btn_reviser_eval.setEnabled(False)
        self.btn_valider_eval.setEnabled(False)
    
    def _fill_evaluation_row(self, row: int, ev: dict):
        """Remplit une ligne d'évaluation"""
        # 0. N° Évaluation
        num_item = QTableWidgetItem(ev.get('numero_evaluation', ''))
        num_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        num_item.setForeground(QColor("#2563eb"))
        num_item.setData(Qt.UserRole, ev)
        self.table_evaluations.setItem(row, 0, num_item)
        
        # 1. Type
        self.table_evaluations.setItem(
            row, 1, QTableWidgetItem(ev.get('type_evaluation', '') or '-')
        )
        
        # 2. Brut
        brut = ev.get('montant_brut', 0) or 0
        brut_str = f"{float(brut):,.0f}".replace(",", " ")
        brut_item = QTableWidgetItem(f"{brut_str} FCFA")
        brut_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_evaluations.setItem(row, 2, brut_item)
        
        # 3. Franchise
        franchise = ev.get('franchise', 0) or 0
        fr_str = f"{float(franchise):,.0f}".replace(",", " ")
        fr_item = QTableWidgetItem(f"-{fr_str} FCFA" if franchise else "—")
        fr_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_evaluations.setItem(row, 3, fr_item)
        
        # 4. Taux
        taux = ev.get('taux_responsabilite', 1) or 1
        taux_item = QTableWidgetItem(f"{float(taux) * 100:.0f}%")
        taux_item.setTextAlignment(Qt.AlignCenter)
        self.table_evaluations.setItem(row, 4, taux_item)
        
        # 5. Net
        net = ev.get('montant_net', 0) or 0
        net_str = f"{float(net):,.0f}".replace(",", " ")
        net_item = QTableWidgetItem(f"{net_str} FCFA")
        net_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
        net_item.setForeground(QColor("#0f172a"))
        net_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_evaluations.setItem(row, 5, net_item)
        
        # 6. Statut (badge)
        badge = StatusBadge(_safe_bool(ev.get('est_validee')))
        badge_container = QWidget()
        badge_layout = QHBoxLayout(badge_container)
        badge_layout.setContentsMargins(4, 6, 4, 6)
        badge_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        badge_layout.addWidget(badge)
        badge_layout.addStretch()
        self.table_evaluations.setCellWidget(row, 6, badge_container)
        
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
            lambda checked=False, e=ev, b=btn_actions: self._show_row_actions_menu(e, b)
        )
        
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(4, 6, 4, 6)
        actions_layout.setAlignment(Qt.AlignCenter)
        actions_layout.addWidget(btn_actions)
        self.table_evaluations.setCellWidget(row, 7, actions_container)
    
    def load_provisions(self, sinistre_id: int):
        try:
            provisions = self.controller.get_provisions_by_sinistre(sinistre_id)
            self._process_provisions(provisions)
        except Exception as e:
            print(f"Erreur chargement provisions: {e}")
    
    def load_all_provisions(self):
        try:
            provisions = self.controller.get_all_provisions()
            self._process_provisions(provisions)
        except Exception as e:
            print(f"Erreur chargement provisions: {e}")
    
    def _process_provisions(self, provisions: list):
        query = self.prov_search.text().strip().lower() if hasattr(self, 'prov_search') else ""
        if query:
            provisions = [
                p for p in provisions
                if query in str(p.get('numero_provision', '')).lower()
                or query in str(p.get('type_provision', '')).lower()
            ]
        
        filter_val = self.prov_filter.currentText() if hasattr(self, 'prov_filter') else "Toutes"
        if filter_val == "Actives":
            provisions = [p for p in provisions if p.get('est_active')]
        elif filter_val == "Inactives":
            provisions = [p for p in provisions if not p.get('est_active')]
        elif filter_val == "Comptabilisées":
            provisions = [p for p in provisions if p.get('est_comptabilisee')]
        
        self._total_provisions = len(provisions)
        
        start = (self._prov_current_page - 1) * self._prov_per_page
        end = start + self._prov_per_page
        page_data = provisions[start:end]
        
        actives = sum(1 for p in provisions if p.get('est_active'))
        for lbl in self.card_provisions.findChildren(QLabel):
            if lbl.objectName() == "stat_value":
                lbl.setText(f"{actives}")
        
        self.table_provisions.setRowCount(len(page_data))
        for i, prov in enumerate(page_data):
            self._fill_provision_row(i, prov)
        
        self._update_pagination_prov(start, min(end, self._total_provisions))
    
    def _fill_provision_row(self, row: int, prov: dict):
        """Remplit une ligne de provision"""
        # 0. N° Provision
        num_item = QTableWidgetItem(prov.get('numero_provision', ''))
        num_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        num_item.setForeground(QColor("#7c3aed"))
        num_item.setData(Qt.UserRole, prov)
        self.table_provisions.setItem(row, 0, num_item)
        
        # 1. Type
        self.table_provisions.setItem(
            row, 1, QTableWidgetItem(prov.get('type_provision', '') or '-')
        )
        
        # 2. Montant
        montant = prov.get('montant', 0) or 0
        montant_str = f"{float(montant):,.0f}".replace(",", " ")
        montant_item = QTableWidgetItem(f"{montant_str} FCFA")
        montant_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_provisions.setItem(row, 2, montant_item)
        
        # 3. Active (badge)
        active_badge = BoolBadge(_safe_bool(prov.get('est_active')), "Active", "Inactive")
        active_container = QWidget()
        active_layout = QHBoxLayout(active_container)
        active_layout.setContentsMargins(4, 8, 4, 8)
        active_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        active_layout.addWidget(active_badge)
        active_layout.addStretch()
        self.table_provisions.setCellWidget(row, 3, active_container)
        
        # 4. Comptabilisée (badge)
        compt_badge = BoolBadge(
            _safe_bool(prov.get('est_comptabilisee')),
            "Oui", "Non"
        )
        compt_container = QWidget()
        compt_layout = QHBoxLayout(compt_container)
        compt_layout.setContentsMargins(4, 8, 4, 8)
        compt_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        compt_layout.addWidget(compt_badge)
        compt_layout.addStretch()
        self.table_provisions.setCellWidget(row, 4, compt_container)
        
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
        """)
        btn_actions.setToolTip("Actions")
        btn_actions.clicked.connect(
            lambda checked=False, p=prov, b=btn_actions: self._show_prov_row_actions_menu(p, b)
        )
        
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(4, 6, 4, 6)
        actions_layout.setAlignment(Qt.AlignCenter)
        actions_layout.addWidget(btn_actions)
        self.table_provisions.setCellWidget(row, 5, actions_container)
    
    def _update_stats(self, evaluations: list):
        """Met à jour les cartes stats"""
        total = 0
        validees = 0
        
        for ev in evaluations:
            total += ev.get('montant_net', 0) or 0
            if ev.get('est_validee'):
                validees += 1
        
        for lbl in self.card_total.findChildren(QLabel):
            if lbl.objectName() == "stat_value":
                if total >= 1_000_000:
                    lbl.setText(f"{total / 1_000_000:.1f}M FCFA")
                elif total >= 1_000:
                    lbl.setText(f"{total / 1_000:.0f}k FCFA")
                else:
                    lbl.setText(f"{total:,.0f} FCFA")
        
        for lbl in self.card_validees.findChildren(QLabel):
            if lbl.objectName() == "stat_value":
                lbl.setText(f"{validees}")
        
        for lbl in self.card_non_validees.findChildren(QLabel):
            if lbl.objectName() == "stat_value":
                lbl.setText(f"{len(evaluations) - validees}")
    
    def _update_pagination(self, start: int, end: int):
        if self._total_evaluations > 0:
            self.lbl_pagination.setText(
                f"{start + 1}-{end} de {self._total_evaluations:,}".replace(",", " ")
            )
        else:
            self.lbl_pagination.setText("0-0 de 0")
        
        self.btn_prev.setEnabled(self._current_page > 1)
        self.btn_next.setEnabled(end < self._total_evaluations)
    
    def _update_pagination_prov(self, start: int, end: int):
        if self._total_provisions > 0:
            self.lbl_pagination_prov.setText(
                f"{start + 1}-{end} de {self._total_provisions:,}".replace(",", " ")
            )
        else:
            self.lbl_pagination_prov.setText("0-0 de 0")
        
        self.btn_prev_prov.setEnabled(self._prov_current_page > 1)
        self.btn_next_prov.setEnabled(end < self._total_provisions)
    
    def _go_prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self._reload_evaluations()
    
    def _go_next_page(self):
        if self._current_page * self._per_page < self._total_evaluations:
            self._current_page += 1
            self._reload_evaluations()
    
    def _go_prev_page_prov(self):
        if self._prov_current_page > 1:
            self._prov_current_page -= 1
            self._reload_provisions()
    
    def _go_next_page_prov(self):
        if self._prov_current_page * self._prov_per_page < self._total_provisions:
            self._prov_current_page += 1
            self._reload_provisions()
    
    def _reload_evaluations(self):
        if self.current_sinistre_id:
            self.load_evaluations(self.current_sinistre_id)
        else:
            self.load_all_evaluations()
    
    def _reload_provisions(self):
        if self.current_sinistre_id:
            self.load_provisions(self.current_sinistre_id)
        else:
            self.load_all_provisions()
    
    def _on_eval_search_changed(self, text):
        self._current_page = 1
        self._reload_evaluations()
    
    def _on_eval_filter_changed(self, text):
        self._current_page = 1
        self._reload_evaluations()
    
    def _on_prov_search_changed(self, text):
        self._prov_current_page = 1
        self._reload_provisions()
    
    def _on_prov_filter_changed(self, text):
        self._prov_current_page = 1
        self._reload_provisions()
    
    # ═══════════════════════════════════════════════════════════════
    # MENU CONTEXTUEL : ÉVALUATIONS (avec icônes FontAwesome)
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
    
    def _show_evaluation_context_menu(self, position):
        """Affiche le menu contextuel au clic droit sur le tableau évaluations"""
        row = self.table_evaluations.currentRow()
        if row < 0:
            menu = QMenu(self)
            menu.setStyleSheet(self._menu_style())
            # ✅ Icône refresh
            action_refresh = menu.addAction(
                qta.icon('fa5s.sync-alt', color='#64748b'),
                "  Actualiser"
            )
            action_refresh.triggered.connect(self._reload_evaluations)
            menu.exec(self.table_evaluations.viewport().mapToGlobal(position))
            return
        
        item = self.table_evaluations.item(row, 0)
        if not item:
            return
        eval_data = item.data(Qt.UserRole)
        if not eval_data:
            return
        
        est_validee = _safe_bool(eval_data.get('est_validee'))
        eval_numero = eval_data.get('numero_evaluation', 'N/A')
        
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        # ✅ Voir détail
        action_detail = QAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir les détails", self
        )
        action_detail.triggered.connect(lambda: self._show_evaluation_detail(eval_data))
        menu.addAction(action_detail)
        
        # ✅ Historique
        action_history = QAction(
            qta.icon('fa5s.history', color='#8b5cf6'),
            "  Historique des révisions", self
        )
        action_history.triggered.connect(
            lambda: self._show_revisions_history(eval_numero, [])
        )
        menu.addAction(action_history)
        
        menu.addSeparator()
        
        # ✅ Réviser
        if not est_validee and self.permissions_ui.peut('evaluation', 'UPDATE'):
            action_reviser = QAction(
                qta.icon('fa5s.edit', color='#f59e0b'),
                "  Réviser", self
            )
            action_reviser.triggered.connect(lambda: self._reviser_from_menu(eval_data))
            menu.addAction(action_reviser)
        
        # ✅ Valider
        if not est_validee and self.permissions_ui.peut('evaluation', 'VALIDATE'):
            action_valider = QAction(
                qta.icon('fa5s.check-circle', color='#22c55e'),
                "  Valider", self
            )
            action_valider.triggered.connect(lambda: self._valider_from_menu(eval_data))
            menu.addAction(action_valider)
        
        menu.addSeparator()
        
        # ✅ Supprimer
        if not est_validee and self.permissions_ui.peut('evaluation', 'DELETE'):
            action_supprimer = QAction(
                qta.icon('fa5s.trash-alt', color='#ef4444'),
                "  Supprimer", self
            )
            action_supprimer.triggered.connect(lambda: self._supprimer_from_menu(eval_data))
            menu.addAction(action_supprimer)
        
        menu.addSeparator()
        
        # ✅ Copier
        action_copy = QAction(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier le N°", self
        )
        action_copy.triggered.connect(lambda: self._copy_to_clipboard(eval_numero))
        menu.addAction(action_copy)
        
        menu.exec(self.table_evaluations.viewport().mapToGlobal(position))
    
    def _show_provisions_context_menu(self, position):
        """Affiche le menu contextuel au clic droit sur le tableau provisions"""
        row = self.table_provisions.currentRow()
        if row < 0:
            menu = QMenu(self)
            menu.setStyleSheet(self._menu_style())
            action_refresh = menu.addAction(
                qta.icon('fa5s.sync-alt', color='#64748b'),
                "  Actualiser"
            )
            action_refresh.triggered.connect(self._reload_provisions)
            menu.exec(self.table_provisions.viewport().mapToGlobal(position))
            return
        
        item = self.table_provisions.item(row, 0)
        if not item:
            return
        prov_data = item.data(Qt.UserRole)
        if not prov_data:
            return
        
        prov_numero = prov_data.get('numero_provision', 'N/A')
        est_active = _safe_bool(prov_data.get('est_active'))
        est_comptabilisee = _safe_bool(prov_data.get('est_comptabilisee'))
        
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        # ✅ Voir détail
        action_detail = QAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir les détails", self
        )
        action_detail.triggered.connect(
            lambda: self._show_provision_detail(prov_data)
        )
        menu.addAction(action_detail)
        
        menu.addSeparator()
        
        # ✅ Activer/Désactiver
        if est_active and self.permissions_ui.peut('evaluation', 'UPDATE'):
            action_desactiver = QAction(
                qta.icon('fa5s.pause-circle', color='#f59e0b'),
                "  Désactiver la provision", self
            )
            action_desactiver.triggered.connect(
                lambda: self._toggle_provision_active(prov_data, False)
            )
            menu.addAction(action_desactiver)
        elif not est_active and self.permissions_ui.peut('evaluation', 'UPDATE'):
            action_activer = QAction(
                qta.icon('fa5s.play-circle', color='#22c55e'),
                "  Activer la provision", self
            )
            action_activer.triggered.connect(
                lambda: self._toggle_provision_active(prov_data, True)
            )
            menu.addAction(action_activer)
        
        # ✅ Comptabiliser
        if not est_comptabilisee and self.permissions_ui.peut('evaluation', 'VALIDATE'):
            action_comptabiliser = QAction(
                qta.icon('fa5s.book', color='#3b82f6'),
                "  Comptabiliser", self
            )
            action_comptabiliser.triggered.connect(
                lambda: self._comptabiliser_provision(prov_data)
            )
            menu.addAction(action_comptabiliser)
        
        menu.addSeparator()
        
        # ✅ Copier
        action_copy = QAction(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier le N°", self
        )
        action_copy.triggered.connect(lambda: self._copy_to_clipboard(prov_numero))
        menu.addAction(action_copy)
        
        menu.exec(self.table_provisions.viewport().mapToGlobal(position))
    
    # ═══════════════════════════════════════════════════════════════
    # MENU D'ACTIONS PAR LIGNE (bouton ⋯)
    # ═══════════════════════════════════════════════════════════════
    
    def _show_row_actions_menu(self, ev: dict, button: QPushButton):
        """Menu du bouton ⋯ pour une évaluation"""
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        est_validee = _safe_bool(ev.get('est_validee'))
        eval_numero = ev.get('numero_evaluation', 'N/A')
        
        action_detail = menu.addAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir les détails"
        )
        action_detail.triggered.connect(lambda: self._show_evaluation_detail(ev))
        
        action_history = menu.addAction(
            qta.icon('fa5s.history', color='#8b5cf6'),
            "  Historique des révisions"
        )
        action_history.triggered.connect(
            lambda: self._show_revisions_history(eval_numero, [])
        )
        
        menu.addSeparator()
        
        if not est_validee and self.permissions_ui.peut('evaluation', 'UPDATE'):
            action_reviser = menu.addAction(
                qta.icon('fa5s.edit', color='#f59e0b'),
                "  Réviser"
            )
            action_reviser.triggered.connect(lambda: self._reviser_from_menu(ev))
        
        if not est_validee and self.permissions_ui.peut('evaluation', 'VALIDATE'):
            action_valider = menu.addAction(
                qta.icon('fa5s.check-circle', color='#22c55e'),
                "  Valider"
            )
            action_valider.triggered.connect(lambda: self._valider_from_menu(ev))
        
        menu.addSeparator()
        
        if not est_validee and self.permissions_ui.peut('evaluation', 'DELETE'):
            action_supp = menu.addAction(
                qta.icon('fa5s.trash-alt', color='#ef4444'),
                "  Supprimer"
            )
            action_supp.triggered.connect(lambda: self._supprimer_from_menu(ev))
        
        menu.addSeparator()
        
        action_copy = menu.addAction(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier le N°"
        )
        action_copy.triggered.connect(lambda: self._copy_to_clipboard(eval_numero))
        
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
    
    def _show_prov_row_actions_menu(self, prov: dict, button: QPushButton):
        """Menu du bouton ⋯ pour une provision"""
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        est_active = _safe_bool(prov.get('est_active'))
        est_comptabilisee = _safe_bool(prov.get('est_comptabilisee'))
        prov_numero = prov.get('numero_provision', 'N/A')
        
        action_detail = menu.addAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir les détails"
        )
        action_detail.triggered.connect(lambda: self._show_provision_detail(prov))
        
        menu.addSeparator()
        
        if est_active and self.permissions_ui.peut('evaluation', 'UPDATE'):
            action_off = menu.addAction(
                qta.icon('fa5s.pause-circle', color='#f59e0b'),
                "  Désactiver"
            )
            action_off.triggered.connect(
                lambda: self._toggle_provision_active(prov, False)
            )
        elif not est_active and self.permissions_ui.peut('evaluation', 'UPDATE'):
            action_on = menu.addAction(
                qta.icon('fa5s.play-circle', color='#22c55e'),
                "  Activer"
            )
            action_on.triggered.connect(
                lambda: self._toggle_provision_active(prov, True)
            )
        
        if not est_comptabilisee and self.permissions_ui.peut('evaluation', 'VALIDATE'):
            action_compt = menu.addAction(
                qta.icon('fa5s.book', color='#3b82f6'),
                "  Comptabiliser"
            )
            action_compt.triggered.connect(
                lambda: self._comptabiliser_provision(prov)
            )
        
        menu.addSeparator()
        
        action_copy = menu.addAction(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier le N°"
        )
        action_copy.triggered.connect(lambda: self._copy_to_clipboard(prov_numero))
        
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS DU MENU CONTEXTUEL — inchangées sauf les QMessageBox avec HTML
    # ═══════════════════════════════════════════════════════════════
    
    def _show_evaluation_detail(self, data: dict):
        QMessageBox.information(
            self,
            f"Évaluation {data.get('numero_evaluation', 'N/A')}",
            f"<b>Type :</b> {data.get('type_evaluation', 'N/A')}<br>"
            f"<b>Brut :</b> {float(data.get('montant_brut', 0)):,.0f} FCFA<br>"
            f"<b>Franchise :</b> {float(data.get('franchise', 0) or 0):,.0f} FCFA<br>"
            f"<b>Taux :</b> {float(data.get('taux_responsabilite', 1) or 1) * 100:.0f}%<br>"
            f"<b>Net :</b> {float(data.get('montant_net', 0)):,.0f} FCFA<br>"
            f"<b>Statut :</b> {'✅ Validée' if data.get('est_validee') else '⏳ En attente'}"
        )
    
    def _show_provision_detail(self, data: dict):
        QMessageBox.information(
            self,
            f"Provision {data.get('numero_provision', 'N/A')}",
            f"<b>Type :</b> {data.get('type_provision', 'N/A')}<br>"
            f"<b>Montant :</b> {float(data.get('montant', 0)):,.0f} FCFA<br>"
            f"<b>Active :</b> {'Oui' if data.get('est_active') else 'Non'}<br>"
            f"<b>Comptabilisée :</b> {'Oui' if data.get('est_comptabilisee') else 'Non'}"
        )
    
    def _toggle_provision_active(self, prov_data: dict, active: bool):
        action = "activer" if active else "désactiver"
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous {action} la provision {prov_data.get('numero_provision')} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        try:
            if hasattr(self.controller, 'toggle_provision_active'):
                self.controller.toggle_provision_active(prov_data.get('id'), active)
                QMessageBox.information(self, "Succès", f"Provision {action}é avec succès")
                self._reload_provisions()
            else:
                QMessageBox.information(
                    self, "Info",
                    f"Fonction 'toggle_provision_active' à implémenter dans le contrôleur."
                )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _comptabiliser_provision(self, prov_data: dict):
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Comptabiliser la provision {prov_data.get('numero_provision')} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        try:
            if hasattr(self.controller, 'comptabiliser_provision'):
                self.controller.comptabiliser_provision(prov_data.get('id'))
                QMessageBox.information(self, "Succès", "Provision comptabilisée")
                self._reload_provisions()
            else:
                QMessageBox.information(
                    self, "Info",
                    "Fonction 'comptabiliser_provision' à implémenter dans le contrôleur."
                )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _reviser_from_menu(self, data: dict):
        eval_id = data.get('id')
        if not eval_id:
            return
        for row in range(self.table_evaluations.rowCount()):
            item = self.table_evaluations.item(row, 0)
            if item and item.data(Qt.UserRole).get('id') == eval_id:
                self.table_evaluations.selectRow(row)
                break
        self.reviser_evaluation()
    
    def _valider_from_menu(self, data: dict):
        eval_id = data.get('id')
        eval_numero = data.get('numero_evaluation')
        
        if not eval_id:
            return
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Valider l'évaluation {eval_numero} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.valider_evaluation(eval_id)
                if result:
                    QMessageBox.information(self, "Succès", "Évaluation validée")
                    self._reload_evaluations()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def _supprimer_from_menu(self, data: dict):
        eval_numero = data.get('numero_evaluation')
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Supprimer l'évaluation {eval_numero} ?\n\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self, "Info",
                f"Suppression de {eval_numero} à implémenter dans le contrôleur."
            )
    
    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copié", f"'{text}' copié")
    
    # ═══════════════════════════════════════════════════════════════
    # EXPORT — inchangé
    # ═══════════════════════════════════════════════════════════════
    
    def _export_evaluations(self):
        self._export_table(self.table_evaluations, "evaluations", 7)
    
    def _export_provisions(self):
        self._export_table(self.table_provisions, "provisions", 5)
    
    def _export_table(self, table, name: str, ncols: int):
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        path, _ = QFileDialog.getSaveFileName(
            self, f"Exporter {name}",
            f"{name}_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV (*.csv)"
        )
        if not path:
            return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                headers = [
                    table.horizontalHeaderItem(i).text()
                    for i in range(table.columnCount())
                ]
                writer.writerow(headers[:-1])
                
                for row in range(table.rowCount()):
                    values = []
                    for col in range(ncols):
                        item = table.item(row, col)
                        if item:
                            values.append(item.text())
                        else:
                            widget = table.cellWidget(row, col)
                            if widget:
                                for lbl in widget.findChildren(QLabel):
                                    values.append(lbl.text().strip())
                                    break
                                else:
                                    values.append('')
                            else:
                                values.append('')
                    writer.writerow(values)
            
            QMessageBox.information(
                self, "Export réussi",
                f"{table.rowCount()} lignes exportées"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS MÉTIER — inchangées
    # ═══════════════════════════════════════════════════════════════
    
    def creer_evaluation(self):
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        sinistre_info = {}
        try:
            sinistre_data = self.controller.get_sinistre_info(self.current_sinistre_id)
            if sinistre_data:
                sinistre_info = {
                    'numero_sinistre': sinistre_data.get('numero_sinistre', 'N/A'),
                    'client_nom': 'N/A',
                    'branche': sinistre_data.get('branche', 'N/A')
                }
        except Exception:
            pass
        
        from addons.sinistres.views.evaluation_dialog import EvaluationDialog
        dialog = EvaluationDialog(
            sinistre_id=self.current_sinistre_id,
            evaluation_controller=self.controller,
            user=self.user,
            sinistre_info=sinistre_info,
            parent=self
        )
        dialog.evaluation_created.connect(self._on_evaluation_created)
        dialog.exec()
    
    def _on_evaluation_created(self, data: dict):
        self._reload_evaluations()
        QMessageBox.information(self, "Succès", "Évaluation créée avec succès !")
    
    def _on_evaluation_selection_changed(self):
        row = self.table_evaluations.currentRow()
        
        if row < 0:
            self.btn_reviser_eval.setEnabled(False)
            self.btn_valider_eval.setEnabled(False)
            return
        
        item = self.table_evaluations.item(row, 0)
        if not item:
            return
        eval_data = item.data(Qt.UserRole)
        if not eval_data:
            return
        
        est_validee = _safe_bool(eval_data.get('est_validee'))
        peut_reviser = self.permissions_ui.peut('evaluation', 'UPDATE')
        peut_valider = self.permissions_ui.peut('evaluation', 'VALIDATE')
        
        self.btn_reviser_eval.setEnabled(
            bool(peut_reviser and not est_validee)
        )
        self.btn_valider_eval.setEnabled(
            bool(peut_valider and not est_validee)
        )
    
    def reviser_evaluation(self):
        row = self.table_evaluations.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une évaluation")
            return
        
        item = self.table_evaluations.item(row, 0)
        if not item:
            return
        eval_data = item.data(Qt.UserRole)
        if not eval_data:
            return
        
        if _safe_bool(eval_data.get('est_validee')):
            QMessageBox.warning(
                self, "Attention",
                "Cette évaluation est déjà validée et ne peut plus être révisée."
            )
            return
        
        try:
            eval_id = eval_data.get('id')
            eval_info = self.controller.get_evaluation(eval_id)
            
            from addons.sinistres.views.reviser_evaluation_dialog import ReviserEvaluationDialog
            dialog = ReviserEvaluationDialog(
                evaluation_id=eval_id,
                evaluation_info=eval_info,
                evaluation_controller=self.controller,
                user=self.user,
                parent=self
            )
            dialog.evaluation_revised.connect(self._on_evaluation_revised)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def _on_evaluation_revised(self, data: dict):
        self._reload_evaluations()
        QMessageBox.information(
            self, "Succès",
            f"Évaluation révisée !\n"
            f"Nouveau montant: {data.get('nouveau_net', 0):,.0f} FCFA"
        )
    
    def valider_evaluation(self):
        row = self.table_evaluations.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une évaluation")
            return
        
        item = self.table_evaluations.item(row, 0)
        if not item:
            return
        eval_data = item.data(Qt.UserRole)
        if not eval_data:
            return
        
        if _safe_bool(eval_data.get('est_validee')):
            QMessageBox.warning(self, "Attention", "Cette évaluation est déjà validée.")
            return
        
        eval_numero = eval_data.get('numero_evaluation')
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Valider l'évaluation {eval_numero} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.valider_evaluation(eval_data.get('id'))
                if result:
                    QMessageBox.information(self, "Succès", "Évaluation validée")
                    self._reload_evaluations()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def _on_evaluation_double_clicked(self, index):
        row = index.row()
        if row < 0:
            return
        item = self.table_evaluations.item(row, 0)
        if not item:
            return
        eval_data = item.data(Qt.UserRole)
        if eval_data:
            self._show_evaluation_detail(eval_data)
    
    def _show_revisions_history(self, eval_numero: str, revisions: List[dict]):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Historique des révisions - {eval_numero}")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(400)
        dialog.setStyleSheet("background: white;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # ✅ Titre avec icône
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('fa5s.history', color='#8b5cf6').pixmap(QSize(16, 16)))
        title_row.addWidget(title_icon)
        
        title = QLabel(f"Historique - {eval_numero}")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a;")
        title_row.addWidget(title)
        title_row.addStretch()
        
        layout.addLayout(title_row)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Date", "Ancien brut", "Nouveau brut", "Ancien net", "Nouveau net"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item { padding: 8px; }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        table.setRowCount(len(revisions))
        
        for i, rev in enumerate(revisions):
            table.setItem(i, 0, QTableWidgetItem(
                str(rev.get('date_revision', ''))[:16]
            ))
            table.setItem(i, 1, QTableWidgetItem(
                f"{rev.get('ancien_montant_brut', 0):,.0f}"
            ))
            table.setItem(i, 2, QTableWidgetItem(
                f"{rev.get('nouveau_montant_brut', 0):,.0f}"
            ))
            table.setItem(i, 3, QTableWidgetItem(
                f"{rev.get('ancien_montant_net', 0):,.0f}"
            ))
            table.setItem(i, 4, QTableWidgetItem(
                f"{rev.get('nouveau_montant_net', 0):,.0f}"
            ))
        
        layout.addWidget(table)
        
        if not revisions:
            empty = QLabel("Aucune révision enregistrée pour cette évaluation.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #94a3b8; padding: 40px;")
            layout.addWidget(empty)
        
        # ✅ Bouton fermer avec icône
        btn_close = QPushButton("  Fermer")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setIcon(qta.icon('fa5s.times', color='white'))
        btn_close.setIconSize(QSize(12, 12))
        btn_close.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)
        
        dialog.exec()
    
    def get_selected_evaluation_id(self) -> Optional[int]:
        row = self.table_evaluations.currentRow()
        if row < 0:
            return None
        item = self.table_evaluations.item(row, 0)
        if not item:
            return None
        eval_data = item.data(Qt.UserRole)
        return eval_data.get('id') if eval_data else None
    
    def get_sinistre_info(self, sinistre_id: int) -> dict:
        try:
            return self.controller.get_sinistre_info(sinistre_id)
        except Exception:
            return {}