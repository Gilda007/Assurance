

"""
Vue principale du module LOMETA Sinistres
Interface utilisateur complète pour la gestion des expertises
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
from PySide6.QtGui import QFont, QColor, QPalette, QAction

import qtawesome as qta

from datetime import datetime, timedelta
from typing import Optional, List


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


class StatusBadge(QLabel):
    """Badge arrondi pour les statuts d'expertise avec icône FontAwesome"""
    
    STATUS_STYLES = {
        'CREEE':        ("#fed7aa", "#9a3412", "Créée",        "fa5s.plus-circle"),
        'AFFECTEE':     ("#dbeafe", "#1e40af", "Affectée",     "fa5s.user-check"),
        'EN_COURS':     ("#ede9fe", "#6d28d9", "En cours",     "fa5s.spinner"),
        'RAPPORT_RECU': ("#cffafe", "#155e75", "Rapport reçu", "fa5s.file-alt"),
        'RAPPORT_REÇU': ("#cffafe", "#155e75", "Rapport reçu", "fa5s.file-alt"),
        'VALIDE':       ("#d1fae5", "#065f46", "Validée",      "fa5s.check-circle"),
        'ANNULE':       ("#fee2e2", "#991b1b", "Annulée",      "fa5s.times-circle"),
    }
    
    def __init__(self, statut: str, parent=None):
        super().__init__(parent)
        
        bg, fg, label, icon_name = self.STATUS_STYLES.get(
            statut, ("#e2e8f0", "#475569", statut, "fa5s.circle")
        )
        
        # Container avec icône + texte
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

class ExpertisesPage(QWidget):
    """Page de gestion des expertises — Design moderne v2.0"""
    
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
        self.selected_mission_id = None
        
        # Pagination
        self._current_page = 1
        self._per_page = 15
        self._total_missions = 0
        self._all_missions = []
        
        self.setup_ui()
        self._appliquer_permissions()
        self.load_data()
    
    def _appliquer_permissions(self):
        """Cache les boutons selon les permissions"""
        self.permissions_ui.masquer_si_non_autorise(
            self.btn_creer, 'expertise', 'CREATE'
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
        layout.addWidget(self._build_table_card(), 1)
        layout.addWidget(self._build_secondary_actions())
    
    def _build_header(self):
        """En-tête : titre + filtre sinistre + bouton Nouvelle Mission"""
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
        icon_lbl.setPixmap(qta.icon('fa5s.microscope', color='#2563eb').pixmap(QSize(24, 24)))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_lbl)
        
        layout.addWidget(icon_container)
        
        # Titre + sous-titre
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title = QLabel("Gestion des Expertises")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
            background: transparent;
        """)
        title_block.addWidget(title)
        
        subtitle = QLabel("Suivi et gestion des missions d'expertise")
        subtitle.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        title_block.addWidget(subtitle)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        # Filtre sinistre
        sinistre_label = QLabel("Sinistre :")
        sinistre_label.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        layout.addWidget(sinistre_label)
        
        self.sinistre_combo = QComboBox()
        self.sinistre_combo.setMinimumWidth(240)
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
        
        # ✅ Bouton Nouvelle Mission avec icône plus
        self.btn_creer = QPushButton("  Nouvelle Mission")
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
        self.btn_creer.clicked.connect(self.creer_mission)
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
            title="Total Missions", value="0",
            color_bg="#dbeafe", color_fg="#1e40af"
        )
        self.card_encours = StatCard(
            icon_name="fa5s.hourglass-half", 
            title="En cours", value="0",
            color_bg="#ede9fe", color_fg="#6d28d9"
        )
        self.card_termine = StatCard(
            icon_name="fa5s.check-circle", 
            title="Terminées", value="0",
            color_bg="#d1fae5", color_fg="#059669"
        )
        self.card_attente = StatCard(
            icon_name="fa5s.exclamation-circle", 
            title="En attente", value="0",
            color_bg="#fed7aa", color_fg="#ea580c"
        )
        
        layout.addWidget(self.card_total)
        layout.addWidget(self.card_encours)
        layout.addWidget(self.card_termine)
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
        
        title = QLabel("Liste des Missions")
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
        
        # Filtre statut
        self.statut_filter = QComboBox()
        self.statut_filter.addItems([
            "Tous les statuts", "Créée", "Affectée", "En cours",
            "Rapport reçu", "Validée", "Annulée"
        ])
        self.statut_filter.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #1e293b;
                min-width: 150px;
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
        btn_export.clicked.connect(self._export_data)
        header_layout.addWidget(btn_export)

        # self.type_filter = QComboBox()
        # self.type_filter.addItems([
        #     "Tous les types", "Expertise", "Garagiste", "Contre-expertise",
        # ])
        # self.type_filter.currentTextChanged.connect(self._on_filter_changed)
        # header_layout.addWidget(self.type_filter)

        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous les types", None)
        for t in self.controller.get_types_mission(actifs_only=True):
            self.type_filter.addItem(t['libelle'], t['code'])
        self.type_filter.setStyleSheet("""
            QComboBox {
                background: white; border: 1px solid #e2e8f0;
                border-radius: 8px; padding: 6px 10px;
                font-size: 12px; min-width: 140px;
            }
        """)
        self.type_filter.currentIndexChanged.connect(self._on_filter_changed)
        header_layout.addWidget(self.type_filter)
        
        layout.addWidget(header)
        
        # ─── Tableau ───
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "N° Mission", "Type", "N° Sinistre", "Expert", "Domaine",
            "Date", "Échéance", "Statut", "Actions"
        ])
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # N° Mission
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # N° Sinistre
        header_view.setSectionResizeMode(3, QHeaderView.Stretch)           # Expert
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Domaine
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Date
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Échéance
        header_view.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Statut
        header_view.setSectionResizeMode(8, QHeaderView.Fixed)             # Actions
        self.table.setColumnWidth(8, 60)
        self.table.setStyleSheet("""
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
        
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(52)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        
        # Largeurs
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 60)
        
        # Signaux
        self.table.itemSelectionChanged.connect(self._on_mission_selection_changed)
        self.table.cellDoubleClicked.connect(self._on_mission_double_clicked)
        
        # Menu contextuel
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_table_context_menu)
        
        layout.addWidget(self.table)
        
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
        
        # ✅ Affecter expert
        self.btn_affecter = QPushButton("  Affecter expert")
        self.btn_affecter.setCursor(Qt.PointingHandCursor)
        self.btn_affecter.setIcon(qta.icon('fa5s.user-plus', color='#2563eb'))
        self.btn_affecter.setIconSize(QSize(14, 14))
        self.btn_affecter.setStyleSheet(btn_style % ("#3b82f6", "#2563eb"))
        self.btn_affecter.clicked.connect(self.affecter_expert)
        self.btn_affecter.setEnabled(False)
        layout.addWidget(self.btn_affecter)
        
        # ✅ Démarrer
        self.btn_demarrer = QPushButton("  Démarrer")
        self.btn_demarrer.setCursor(Qt.PointingHandCursor)
        self.btn_demarrer.setIcon(qta.icon('fa5s.play', color='#7c3aed'))
        self.btn_demarrer.setIconSize(QSize(14, 14))
        self.btn_demarrer.setStyleSheet(btn_style % ("#8b5cf6", "#7c3aed"))
        self.btn_demarrer.clicked.connect(self.demarrer_mission)
        self.btn_demarrer.setEnabled(False)
        layout.addWidget(self.btn_demarrer)
        
        # ✅ Déposer rapport
        self.btn_rapport = QPushButton("  Déposer rapport")
        self.btn_rapport.setCursor(Qt.PointingHandCursor)
        self.btn_rapport.setIcon(qta.icon('fa5s.file-upload', color='#0891b2'))
        self.btn_rapport.setIconSize(QSize(14, 14))
        self.btn_rapport.setStyleSheet(btn_style % ("#06b6d4", "#0891b2"))
        self.btn_rapport.clicked.connect(self.deposer_rapport)
        self.btn_rapport.setEnabled(False)
        layout.addWidget(self.btn_rapport)
        
        # ✅ Valider
        self.btn_valider = QPushButton("  Valider")
        self.btn_valider.setCursor(Qt.PointingHandCursor)
        self.btn_valider.setIcon(qta.icon('fa5s.check', color='#16a34a'))
        self.btn_valider.setIconSize(QSize(14, 14))
        self.btn_valider.setStyleSheet(btn_style % ("#22c55e", "#16a34a"))
        self.btn_valider.clicked.connect(self.valider_mission)
        self.btn_valider.setEnabled(False)
        layout.addWidget(self.btn_valider)
        
        layout.addStretch()
        
        return wrapper
    
    # ═══════════════════════════════════════════════════════════════
    # CHARGEMENT DES DONNÉES
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
        """Charge les missions du sinistre sélectionné"""
        sinistre_id = self.sinistre_combo.currentData()
        self.current_sinistre_id = sinistre_id
        self._current_page = 1
        
        if sinistre_id is None:
            self.load_all_expertises()
        else:
            self.load_expertises(sinistre_id)
    
    def load_all_expertises(self):
        """Charge toutes les missions"""
        try:
            missions = self.controller.get_all_missions()
            self._process_missions(missions)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement missions: {str(e)}")
    
    def load_expertises(self, sinistre_id: int):
        """Charge les missions d'un sinistre"""
        try:
            missions = self.controller.get_missions_by_sinistre(sinistre_id)
            self._process_missions(missions)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement missions: {str(e)}")
    
    def _process_missions(self, missions: list):
        """Traite et affiche les missions"""
        query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""
        if query:
            missions = [
                m for m in missions
                if query in str(m.get('numero_mission', '')).lower()
                or query in str(m.get('expert_nom', '') or '').lower()
                or query in str(m.get('sinistre_numero', '')).lower()
            ]
        
        filter_val = self.statut_filter.currentText() if hasattr(self, 'statut_filter') else "Tous les statuts"
        statut_map = {
            "Créée": "CREEE",
            "Affectée": "AFFECTEE",
            "En cours": "EN_COURS",
            "Rapport reçu": "RAPPORT_RECU",
            "Validée": "VALIDE",
            "Annulée": "ANNULE",
        }
        if filter_val != "Tous les statuts":
            target = statut_map.get(filter_val, "")
            if target:
                missions = [m for m in missions if m.get('statut') == target]

        target_type = self.type_filter.currentData() if hasattr(self, 'type_filter') else None
        if target_type:
            missions = [m for m in missions if m.get('type_mission_code') == target_type]
        
        self._all_missions = missions
        self._total_missions = len(missions)
        
        start = (self._current_page - 1) * self._per_page
        end = start + self._per_page
        page_data = missions[start:end]
        
        self._update_stats(missions)
        
        self.table.setRowCount(len(page_data))
        for i, mission in enumerate(page_data):
            self._fill_row(i, mission)
        
        self._update_pagination(start, min(end, self._total_missions))
        
        self.btn_affecter.setEnabled(False)
        self.btn_demarrer.setEnabled(False)
        self.btn_rapport.setEnabled(False)
        self.btn_valider.setEnabled(False)
    
    # def _fill_row(self, row: int, mission: dict):
    #     """Remplit une ligne"""
    #     # 0. N° Mission
    #     num_item = QTableWidgetItem(mission.get('numero_mission', ''))
    #     num_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
    #     num_item.setForeground(QColor("#2563eb"))
    #     num_item.setData(Qt.UserRole, mission)
    #     self.table.setItem(row, 0, num_item)
    #     num_text = mission.get('numero_mission', '')
    #     if mission.get('est_contre_expertise') and mission.get('mission_parente_numero'):
    #         num_text += f"\n↳ de {mission['mission_parente_numero']}"
    #     num_item = QTableWidgetItem(num_text)

    #     # 1. N° Sinistre
    #     self.table.setItem(
    #         row, 1, QTableWidgetItem(mission.get('sinistre_numero', '') or 'N/A')
    #     )
        
    #     # 2. Expert
    #     expert = mission.get('expert_nom') or 'Non affecté'
    #     expert_item = QTableWidgetItem(expert)
    #     if not mission.get('expert_nom'):
    #         expert_item.setForeground(QColor("#94a3b8"))
    #         expert_item.setFont(QFont("Segoe UI", 11, QFont.StyleItalic))
    #     self.table.setItem(row, 2, expert_item)
        
    #     # 3. Type
    #     self.table.setItem(
    #         row, 3, QTableWidgetItem(mission.get('type_expertise', '') or '-')
    #     )

    #     # Colonne 1 : Type de mission
    #     type_mission = mission.get('type_mission', 'EXPERTISE')
    #     type_labels = {
    #         'EXPERTISE': ('Expertise', '#2563eb'),
    #         'GARAGISTE': ('Garagiste', '#ea580c'),
    #         'CONTRE_EXPERTISE': ('Contre-exp.', '#7c3aed'),
    #     }
    #     label, color = type_labels.get(type_mission, (type_mission, '#64748b'))
    #     type_item = QTableWidgetItem(label)
    #     type_item.setForeground(QColor(color))
    #     type_item.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
    #     self.table.setItem(row, 1, type_item)
        
    #     # 4. Date
    #     date_mission = mission.get('date_mission', '')
    #     if date_mission:
    #         try:
    #             dt = datetime.fromisoformat(str(date_mission)[:19])
    #             date_str = dt.strftime("%d %b %Y")
    #         except Exception:
    #             date_str = str(date_mission)[:10]
    #     else:
    #         date_str = '-'
    #     self.table.setItem(row, 4, QTableWidgetItem(date_str))
        
    #     # 5. Échéance
    #     date_echeance = mission.get('date_echeance', '')
    #     if date_echeance:
    #         try:
    #             dt = datetime.fromisoformat(str(date_echeance)[:19])
    #             if dt.date() < datetime.now().date() and mission.get('statut') not in ['VALIDE', 'ANNULE']:
    #                 echeance_str = f"⚠ {dt.strftime('%d %b %Y')}"
    #             else:
    #                 echeance_str = dt.strftime("%d %b %Y")
    #         except Exception:
    #             echeance_str = str(date_echeance)[:10]
    #     else:
    #         echeance_str = '-'
    #     self.table.setItem(row, 5, QTableWidgetItem(echeance_str))
        
    #     # 6. Statut (badge)
    #     statut = mission.get('statut', '')
    #     badge = StatusBadge(statut)
    #     badge_container = QWidget()
    #     badge_layout = QHBoxLayout(badge_container)
    #     badge_layout.setContentsMargins(4, 6, 4, 6)
    #     badge_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    #     badge_layout.addWidget(badge)
    #     badge_layout.addStretch()
    #     self.table.setCellWidget(row, 6, badge_container)
        
    #     # 7. Actions avec icône ellipsis
    #     btn_actions = QPushButton()
    #     btn_actions.setCursor(Qt.PointingHandCursor)
    #     btn_actions.setFixedSize(32, 28)
    #     btn_actions.setIcon(qta.icon('fa5s.ellipsis-h', color='#64748b'))
    #     btn_actions.setIconSize(QSize(14, 14))
    #     btn_actions.setStyleSheet("""
    #         QPushButton {
    #             background: transparent;
    #             border: 1px solid #e2e8f0;
    #             border-radius: 6px;
    #         }
    #         QPushButton:hover {
    #             background: #f1f5f9;
    #             border-color: #cbd5e1;
    #         }
    #         QPushButton:pressed { background: #e2e8f0; }
    #     """)
    #     btn_actions.setToolTip("Actions")
    #     btn_actions.clicked.connect(
    #         lambda checked=False, m=mission, b=btn_actions: self._show_row_actions_menu(m, b)
    #     )
        
    #     actions_container = QWidget()
    #     actions_layout = QHBoxLayout(actions_container)
    #     actions_layout.setContentsMargins(4, 6, 4, 6)
    #     actions_layout.setAlignment(Qt.AlignCenter)
    #     actions_layout.addWidget(btn_actions)
    #     self.table.setCellWidget(row, 7, actions_container)
    
    def _fill_row(self, row: int, mission: dict):
        # Colonne 0 : N° + badge parenté
        num_text = mission.get('numero_mission', '')
        if mission.get('est_contre_expertise') and mission.get('mission_parente_numero'):
            num_text += f"\n↳ de {mission['mission_parente_numero']}"
        num_item = QTableWidgetItem(num_text)
        num_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        num_item.setForeground(QColor("#2563eb"))
        num_item.setData(Qt.UserRole, mission)
        self.table.setItem(row, 0, num_item)

        # Colonne 1 : Type (couleur du référentiel)
        type_lib = mission.get('type_mission_libelle') or mission.get('type_mission_code', '')
        type_col = mission.get('type_mission_couleur') or '#64748b'
        type_item = QTableWidgetItem(type_lib)
        type_item.setForeground(QColor(type_col))
        type_item.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.table.setItem(row, 1, type_item)

        # Colonne 2 : N° sinistre
        self.table.setItem(row, 2, QTableWidgetItem(mission.get('sinistre_numero') or 'N/A'))

        # Colonne 3 : Expert
        expert = mission.get('expert_nom') or 'Non affecté'
        e_item = QTableWidgetItem(expert)
        if not mission.get('expert_nom'):
            e_item.setForeground(QColor("#94a3b8"))
            e_item.setFont(QFont("Segoe UI", 11, QFont.StyleItalic))
        self.table.setItem(row, 3, e_item)

        # Colonne 4 : Domaine
        self.table.setItem(row, 4, QTableWidgetItem(mission.get('domaine') or '-'))

        # Colonne 5 : Date
        dm = mission.get('date_mission')
        ds = '-'
        if dm:
            try:
                ds = datetime.fromisoformat(str(dm)[:19]).strftime("%d %b %Y")
            except Exception:
                ds = str(dm)[:10]
        self.table.setItem(row, 5, QTableWidgetItem(ds))

        # Colonne 6 : Échéance
        de = mission.get('date_echeance')
        es = '-'
        if de:
            try:
                dt = datetime.fromisoformat(str(de)[:19])
                if dt.date() < datetime.now().date() and mission.get('statut') not in ['VALIDE', 'ANNULE']:
                    es = f"⚠ {dt.strftime('%d %b %Y')}"
                else:
                    es = dt.strftime("%d %b %Y")
            except Exception:
                es = str(de)[:10]
        self.table.setItem(row, 6, QTableWidgetItem(es))

        # Colonne 7 : Statut (badge)
        badge = StatusBadge(mission.get('statut', ''))
        c = QWidget()
        l = QHBoxLayout(c); l.setContentsMargins(4, 6, 4, 6)
        l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        l.addWidget(badge); l.addStretch()
        self.table.setCellWidget(row, 7, c)

        # Colonne 8 : Actions
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(32, 28)
        btn.setIcon(qta.icon('fa5s.ellipsis-h', color='#64748b'))
        btn.setIconSize(QSize(14, 14))
        btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: 1px solid #e2e8f0; border-radius: 6px;
            }
            QPushButton:hover { background: #f1f5f9; border-color: #cbd5e1; }
        """)
        btn.clicked.connect(lambda _, m=mission, b=btn: self._show_row_actions_menu(m, b))
        c2 = QWidget(); l2 = QHBoxLayout(c2)
        l2.setContentsMargins(4, 6, 4, 6); l2.setAlignment(Qt.AlignCenter)
        l2.addWidget(btn)
        self.table.setCellWidget(row, 8, c2)

    def _update_stats(self, missions: list):
        """Met à jour les 4 cartes"""
        total = len(missions)
        en_cours = sum(
            1 for m in missions
            if m.get('statut') in ['CREEE', 'AFFECTEE', 'EN_COURS']
        )
        termine = sum(1 for m in missions if m.get('statut') == 'VALIDE')
        attente = sum(1 for m in missions if m.get('statut') == 'RAPPORT_RECU')
        
        for card, value in [
            (self.card_total, total),
            (self.card_encours, en_cours),
            (self.card_termine, termine),
            (self.card_attente, attente),
        ]:
            for lbl in card.findChildren(QLabel):
                if lbl.objectName() == "stat_value":
                    lbl.setText(f"{value}")
    
    def _update_pagination(self, start: int, end: int):
        if self._total_missions > 0:
            self.lbl_pagination.setText(
                f"{start + 1}-{end} de {self._total_missions:,}".replace(",", " ")
            )
        else:
            self.lbl_pagination.setText("0-0 de 0")
        
        self.btn_prev.setEnabled(self._current_page > 1)
        self.btn_next.setEnabled(end < self._total_missions)
    
    def _go_prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self._reload_missions()
    
    def _go_next_page(self):
        if self._current_page * self._per_page < self._total_missions:
            self._current_page += 1
            self._reload_missions()
    
    def _reload_missions(self):
        if self.current_sinistre_id:
            self.load_expertises(self.current_sinistre_id)
        else:
            self.load_all_expertises()
    
    def _on_search_changed(self, text):
        self._current_page = 1
        self._reload_missions()
    
    def _on_filter_changed(self, text):
        self._current_page = 1
        self._reload_missions()
    
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
    
    # def _show_table_context_menu(self, position):
    #     """Menu contextuel (clic droit)"""
    #     row = self.table.currentRow()
    #     if row < 0:
    #         menu = QMenu(self)
    #         menu.setStyleSheet(self._menu_style())
    #         # ✅ Icône refresh
    #         action_refresh = menu.addAction(
    #             qta.icon('fa5s.sync-alt', color='#64748b'),
    #             "  Actualiser"
    #         )
    #         action_refresh.triggered.connect(self._reload_missions)
    #         menu.exec(self.table.viewport().mapToGlobal(position))
    #         return
        
    #     item = self.table.item(row, 0)
    #     if not item:
    #         return
    #     mission_data = item.data(Qt.UserRole)
    #     if not mission_data:
    #         return

    #     if mission_data.get('type_mission_code') == 'GARAGISTE':
    #         already = mission_data.get('nb_contre_expertises', 0) > 0
    #         act = QAction(
    #             qta.icon('fa5s.exchange-alt', color='#7c3aed'),
    #             "  Déjà contre-expertisée" if already else "  Contre-expertiser cette mission",
    #             self
    #         )
    #         act.setEnabled(
    #             not already and mission_data.get('statut') in ('RAPPORT_RECU', 'RAPPORT_REÇU', 'VALIDE')
    #         )
    #         act.triggered.connect(lambda: self._creer_contre_expertise(mission_data))
    #         menu.addAction(act)

    #     if mission_data.get('est_contre_expertise') and mission_data.get('mission_parente_id'):
    #         act2 = QAction(
    #             qta.icon('fa5s.level-up-alt', color='#64748b'),
    #             f"  Voir la mission parente ({mission_data['mission_parente_numero']})", self
    #         )
    #         act2.triggered.connect(
    #             lambda: self.open_mission_detail_by_numero(mission_data['mission_parente_numero'])
    #         )
    #         menu.addAction(act2)
        
    #     self._build_mission_menu(mission_data, self.table.viewport().mapToGlobal(position))
    
    def _show_table_context_menu(self, position):
        """Menu contextuel (clic droit)"""
        row = self.table.currentRow()
        if row < 0:
            menu = QMenu(self)
            menu.setStyleSheet(self._menu_style())
            action_refresh = menu.addAction(
                qta.icon('fa5s.sync-alt', color='#64748b'),
                "  Actualiser"
            )
            action_refresh.triggered.connect(self._reload_missions)
            menu.exec(self.table.viewport().mapToGlobal(position))
            return

        item = self.table.item(row, 0)
        if not item:
            return
        mission_data = item.data(Qt.UserRole)
        if not mission_data:
            return

        # ✅ Déléguer entièrement au menu contextuel
        self._build_mission_menu(mission_data, self.table.viewport().mapToGlobal(position))

    def _show_row_actions_menu(self, mission: dict, button: QPushButton):
        """Menu du bouton ⋯"""
        self._build_mission_menu(mission, button.mapToGlobal(button.rect().bottomLeft()))
    
    def _build_mission_menu(self, mission_data: dict, global_pos):
        """Construit le menu pour une mission"""
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        statut = mission_data.get('statut', '')
        mission_numero = mission_data.get('numero_mission', 'N/A')
        
        # ✅ Consultation - Voir détail
        action_detail = QAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir le détail", self
        )
        action_detail.triggered.connect(
            lambda: self.open_mission_detail_by_numero(mission_numero)
        )
        menu.addAction(action_detail)
        
        # ✅ Modifier
        action_edit = QAction(
            qta.icon('fa5s.edit', color='#f59e0b'),
            "  Modifier", self
        )
        action_edit.triggered.connect(
            lambda: self._on_modifier_mission(mission_data)
        )
        menu.addAction(action_edit)
        
        menu.addSeparator()

        # Dans _build_mission_menu
        # ✅ Actions spécifiques aux types de mission
        if mission_data.get('type_mission_code') == 'GARAGISTE':
            already = mission_data.get('nb_contre_expertises', 0) > 0
            act = QAction(
                qta.icon('fa5s.exchange-alt', color='#7c3aed'),
                "  Déjà contre-expertisée" if already else "  Contre-expertiser cette mission",
                self
            )
            act.setEnabled(
                not already and mission_data.get('statut') in ('RAPPORT_RECU', 'RAPPORT_REÇU', 'VALIDE')
            )
            act.triggered.connect(lambda: self._creer_contre_expertise(mission_data))
            menu.addAction(act)
            menu.addSeparator()

        if mission_data.get('est_contre_expertise') and mission_data.get('mission_parente_id'):
            act2 = QAction(
                qta.icon('fa5s.level-up-alt', color='#64748b'),
                f"  Voir la mission parente ({mission_data['mission_parente_numero']})",
                self
            )
            act2.triggered.connect(
                lambda: self.open_mission_detail_by_numero(mission_data['mission_parente_numero'])
            )
            menu.addAction(act2)
            menu.addSeparator()
        
        # Actions métier
        if self.permissions_ui.peut('expertise', 'UPDATE'):
            # ✅ Affecter
            action_affecter = QAction(
                qta.icon('fa5s.user-plus', color='#2563eb'),
                "  Affecter expert", self
            )
            action_affecter.setEnabled(statut in ["CREEE", "AFFECTEE"])
            action_affecter.triggered.connect(
                lambda: self._affecter_expert_from_menu(mission_data)
            )
            menu.addAction(action_affecter)
            
            # ✅ Démarrer
            action_demarrer = QAction(
                qta.icon('fa5s.play', color='#7c3aed'),
                "  Démarrer", self
            )
            action_demarrer.setEnabled(statut == "AFFECTEE")
            action_demarrer.triggered.connect(
                lambda: self._demarrer_mission_from_menu(mission_data)
            )
            menu.addAction(action_demarrer)
            
            # ✅ Rapport
            action_rapport = QAction(
                qta.icon('fa5s.file-upload', color='#0891b2'),
                "  Déposer rapport", self
            )
            action_rapport.setEnabled(statut in ["EN_COURS", "RAPPORT_RECU"])
            action_rapport.triggered.connect(
                lambda: self._deposer_rapport_from_menu(mission_data)
            )
            menu.addAction(action_rapport)
        
        # ✅ Valider
        if self.permissions_ui.peut('expertise', 'VALIDATE'):
            action_valider = QAction(
                qta.icon('fa5s.check-circle', color='#16a34a'),
                "  Valider", self
            )
            action_valider.setEnabled(statut in ("RAPPORT_RECU", "RAPPORT_REÇU"))
            action_valider.triggered.connect(
                lambda: self._valider_mission_from_menu(mission_data)
            )
            menu.addAction(action_valider)
        
        menu.addSeparator()
        
        # ✅ Supprimer
        if self.permissions_ui.peut('expertise', 'DELETE'):
            action_supp = QAction(
                qta.icon('fa5s.trash-alt', color='#ef4444'),
                "  Supprimer", self
            )
            action_supp.setEnabled(statut in ["CREEE", "ANNULE"])
            action_supp.triggered.connect(
                lambda: self._on_supprimer_mission(mission_data)
            )
            menu.addAction(action_supp)
        
        menu.addSeparator()
        
        # ✅ Copier
        action_copy = QAction(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier le N°", self
        )
        action_copy.triggered.connect(lambda: self._copy_to_clipboard(mission_numero))
        menu.addAction(action_copy)
        
        menu.exec(global_pos)

    # def _creer_contre_expertise(self, mission_garagiste: dict):
    #     """Ouvre MissionDialog en mode contre-expertise pré-rempli"""
    #     from addons.sinistres.views.mission_dialog import MissionDialog
        
    #     dialog = MissionDialog(
    #         sinistre_id=mission_garagiste['sinistre_id'],
    #         expertise_controller=self.controller,
    #         user=self.user,
    #         sinistre_info={...},
    #         expert_controller=self.controller,
    #         parent=self,
    #     )
    #     # ✅ Forcer le mode contre-expertise
    #     dialog.radio_contre.setChecked(True)
    #     dialog._load_missions_parentes()
    #     # Sélectionner la mission parente
    #     for i in range(dialog.parent_combo.count()):
    #         d = dialog.parent_combo.itemData(i)
    #         if d and d['id'] == mission_garagiste['id']:
    #             dialog.parent_combo.setCurrentIndex(i)
    #             break
    #     dialog.mission_created.connect(self._on_mission_created)
    #     dialog.exec()

    def _creer_contre_expertise(self, mission_garagiste: dict):
        """Ouvre MissionDialog en mode contre-expertise pré-rempli"""
        from addons.sinistres.views.mission_dialog import MissionDialog

        dialog = MissionDialog(
            sinistre_id=mission_garagiste['sinistre_id'],
            expertise_controller=self.controller,
            user=self.user,
            sinistre_info={
                'numero_sinistre': mission_garagiste.get('sinistre_numero', 'N/A'),
                'branche': '',
                'client_nom': '',
            },
            expert_controller=self.controller,
            parent=self,
            force_type_code='CONTRE_EXPERTISE',
            force_mission_parente_id=mission_garagiste['id'],
        )
        dialog.mission_created.connect(self._on_mission_created)
        dialog.exec()

    # ═══════════════════════════════════════════════════════════════
    # ACTIONS MÉTIER (depuis le menu) — inchangées
    # ═══════════════════════════════════════════════════════════════
    
    def _affecter_expert_from_menu(self, data: dict):
        mission_id = data.get('id')
        if not mission_id:
            QMessageBox.warning(self, "Erreur", "Mission non trouvée")
            return
        
        mission_info = self.controller.get_mission(mission_id)
        
        from addons.sinistres.views.affecter_expert_dialog import AffecterExpertDialog
        dialog = AffecterExpertDialog(
            mission_id=mission_id,
            mission_info=mission_info,
            expertise_controller=self.controller,
            user=self.user,
            parent=self
        )
        dialog.expert_affected.connect(self._on_expert_affected)
        dialog.exec()
    
    def _demarrer_mission_from_menu(self, data: dict):
        mission_id = data.get('id')
        mission_numero = data.get('numero_mission')
        
        if not mission_id:
            return
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Démarrer la mission {mission_numero} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.demarrer_mission(mission_id)
                if result:
                    QMessageBox.information(self, "Succès", "Mission démarrée")
                    self._reload_missions()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def _deposer_rapport_from_menu(self, data: dict):
        mission_id = data.get('id')
        if not mission_id:
            return
        
        mission_info = self.controller.get_mission(mission_id)
        
        from addons.sinistres.views.deposer_rapport_dialog import DeposerRapportDialog
        dialog = DeposerRapportDialog(
            mission_id=mission_id,
            mission_info=mission_info,
            expertise_controller=self.controller,
            user=self.user,
            parent=self
        )
        dialog.rapport_depose.connect(self._on_rapport_depose)
        dialog.exec()
    
    def _valider_mission_from_menu(self, data: dict):
        mission_id = data.get('id')
        mission_numero = data.get('numero_mission')
        
        if not mission_id:
            return
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Valider la mission {mission_numero} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.valider_mission(mission_id)
                if result:
                    QMessageBox.information(self, "Succès", "Mission validée")
                    self._reload_missions()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def _on_modifier_mission(self, data: dict):
        QMessageBox.information(
            self, "Modification",
            f"Modification de la mission {data.get('numero_mission')} (à implémenter)"
        )
    
    def _on_supprimer_mission(self, data: dict):
        mission_numero = data.get('numero_mission')
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Supprimer la mission {mission_numero} ?\n\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self, "Info",
                f"Suppression de {mission_numero} à implémenter."
            )
    
    def _copy_to_clipboard(self, text: str):
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copié", f"'{text}' copié")
    
    # ═══════════════════════════════════════════════════════════════
    # SÉLECTION ET BOUTONS — inchangées
    # ═══════════════════════════════════════════════════════════════
    
    def _on_mission_selection_changed(self):
        row = self.table.currentRow()
        
        if row < 0:
            self.btn_affecter.setEnabled(False)
            self.btn_demarrer.setEnabled(False)
            self.btn_rapport.setEnabled(False)
            self.btn_valider.setEnabled(False)
            return
        
        item = self.table.item(row, 0)
        if not item:
            return
        mission_data = item.data(Qt.UserRole)
        if not mission_data:
            return
        
        statut = mission_data.get('statut', '')
        self.selected_mission_id = mission_data.get('id')
        
        peut_update = self.permissions_ui.peut('expertise', 'UPDATE')
        peut_validate = self.permissions_ui.peut('expertise', 'VALIDATE')
        
        self.btn_affecter.setEnabled(
            bool(peut_update and statut in ["CREEE", "AFFECTEE"])
        )
        self.btn_demarrer.setEnabled(
            bool(peut_update and statut == "AFFECTEE")
        )
        self.btn_rapport.setEnabled(
            bool(peut_update and statut in ["EN_COURS", "RAPPORT_RECU"])
        )
        self.btn_valider.setEnabled(
            bool(peut_validate and statut == "RAPPORT_RECU")
        )
    
    def _on_mission_double_clicked(self, row: int, col: int):
        if col == 8:
            return
        item = self.table.item(row, 0)
        if item:
            mission_data = item.data(Qt.UserRole)
            if mission_data:
                self.open_mission_detail_by_numero(mission_data.get('numero_mission'))
    
    # ═══════════════════════════════════════════════════════════════
    # EXPORT — inchangé
    # ═══════════════════════════════════════════════════════════════
    
    def _export_data(self):
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les missions",
            f"missions_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV (*.csv)"
        )
        if not path:
            return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "N° Mission", "N° Sinistre", "Expert", "Type",
                    "Date", "Échéance", "Statut"
                ])
                for row in range(self.table.rowCount()):
                    values = []
                    for col in range(9):
                        item = self.table.item(row, col)
                        if item:
                            values.append(item.text())
                        else:
                            widget = self.table.cellWidget(row, col)
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
                f"{self.table.rowCount()} missions exportées"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS MÉTIER (boutons secondaires) — inchangées
    # ═══════════════════════════════════════════════════════════════
    
    def creer_mission(self):
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        sinistre_info = {}
        try:
            sinistre_info = {
                'numero_sinistre': self.sinistre_combo.currentText().split(' - ')[0]
                    if self.sinistre_combo.currentIndex() > 0 else 'N/A',
                'branche': self.sinistre_combo.currentText().split(' - ')[1]
                    if len(self.sinistre_combo.currentText().split(' - ')) > 1 else 'N/A',
                'client_nom': 'N/A'
            }
        except Exception:
            pass
        
        from addons.sinistres.views.mission_dialog import MissionDialog
        dialog = MissionDialog(
            sinistre_id=self.current_sinistre_id,
            expertise_controller=self.controller,
            user=self.user,
            sinistre_info=sinistre_info,
            expert_controller=self.controller,
            parent=self
        )
        dialog.mission_created.connect(self._on_mission_created)
        dialog.exec()
    
    def _on_mission_created(self, mission_data: dict):
        QMessageBox.information(
            self, "Succès",
            f"Mission {mission_data.get('numero_mission', '')} créée"
        )
        self._reload_missions()
    
    def affecter_expert(self):
        mission_data = self._get_selected_mission_data()
        if not mission_data:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une mission")
            return
        
        statut = mission_data.get('statut', '')
        if statut not in ["CREEE", "AFFECTEE"]:
            QMessageBox.warning(
                self, "Attention",
                f"Cette mission ne peut pas être affectée (statut: {statut})\n"
                "Seules les missions 'CRÉÉE' ou 'AFFECTÉE' peuvent l'être."
            )
            return
        
        self._affecter_expert_from_menu(mission_data)
    
    def _on_expert_affected(self, data: dict):
        self._reload_missions()
        QMessageBox.information(
            self, "Succès",
            f"Expert affecté à la mission {data.get('mission_id')}"
        )
    
    def demarrer_mission(self):
        mission_data = self._get_selected_mission_data()
        if not mission_data:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une mission")
            return
        
        statut = mission_data.get('statut', '')
        if statut != "AFFECTEE":
            QMessageBox.warning(
                self, "Attention",
                f"Seule une mission 'AFFECTÉE' peut être démarrée (statut: {statut})"
            )
            return
        
        self._demarrer_mission_from_menu(mission_data)
    
    def deposer_rapport(self):
        mission_data = self._get_selected_mission_data()
        if not mission_data:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une mission")
            return
        
        statut = mission_data.get('statut', '')
        if statut not in ["EN_COURS", "RAPPORT_RECU"]:
            QMessageBox.warning(
                self, "Attention",
                f"Seule une mission 'EN COURS' peut recevoir un rapport (statut: {statut})"
            )
            return
        
        self._deposer_rapport_from_menu(mission_data)
    
    def _on_rapport_depose(self, data: dict):
        self._reload_missions()
        QMessageBox.information(
            self, "Succès",
            f"Rapport déposé pour la mission {data.get('mission_id')}"
        )
    
    def valider_mission(self):
        mission_data = self._get_selected_mission_data()
        if not mission_data:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une mission")
            return
        
        statut = mission_data.get('statut', '')
        if statut != "RAPPORT_RECU":
            QMessageBox.warning(
                self, "Attention",
                f"Seule une mission avec rapport peut être validée (statut: {statut})"
            )
            return
        
        self._valider_mission_from_menu(mission_data)
    
    # ═══════════════════════════════════════════════════════════════
    # HELPERS — inchangés
    # ═══════════════════════════════════════════════════════════════
    
    def _get_selected_mission_data(self) -> Optional[dict]:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if not item:
            return None
        return item.data(Qt.UserRole)
    
    def get_selected_mission_id(self) -> Optional[int]:
        data = self._get_selected_mission_data()
        return data.get('id') if data else None
    
    def open_mission_detail_by_numero(self, mission_numero: str):
        """Ouvre le détail d'une mission"""
        try:
            mission_data = self.controller.get_mission_by_numero(mission_numero)
            if not mission_data:
                QMessageBox.warning(self, "Erreur", f"Mission {mission_numero} non trouvée")
                return
            
            mission_info = self.controller.get_mission(mission_data.get('id'))
            
            expert = mission_info.get('expert_nom') or 'Non affecté'
            montant = mission_info.get('montant_estime', 0) or 0
            
            QMessageBox.information(
                self,
                f"Détail de la mission {mission_numero}",
                f"<b>Mission :</b> {mission_numero}<br>"
                f"<b>Sinistre :</b> {mission_info.get('sinistre_numero', 'N/A')}<br>"
                f"<b>Expert :</b> {expert}<br>"
                f"<b>Type :</b> {mission_info.get('type_expertise', 'N/A')}<br>"
                f"<b>Date :</b> {str(mission_info.get('date_mission', ''))[:10] or 'N/A'}<br>"
                f"<b>Échéance :</b> {str(mission_info.get('date_echeance', ''))[:10] or 'N/A'}<br>"
                f"<b>Statut :</b> {mission_info.get('statut', 'N/A')}<br>"
                f"<b>Montant estimé :</b> {float(montant):,.0f} FCFA"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def open_mission_detail_from_data(self, data: dict):
        mission_numero = data.get('numero_mission')
        if mission_numero:
            self.open_mission_detail_by_numero(mission_numero)