



"""
Vue principale du module LOMETA Sinistres
Interface utilisateur complète pour la gestion des règlements
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
from typing import Optional


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
    """Badge de statut arrondi (pill)"""
    
    STATUS_STYLES = {
        'PAYE':         ("#d1fae5", "#065f46", "Payé"),
        'VALIDE':       ("#dbeafe", "#1e40af", "Validé"),
        'EN_ATTENTE':   ("#fef3c7", "#92400e", "En attente"),
        'TRAITE':       ("#cffafe", "#155e75", "Traité"),
        'CREE':         ("#fed7aa", "#9a3412", "Créé"),
        'ANNULE':       ("#fee2e2", "#991b1b", "Annulé"),
        'REJETE':       ("#fee2e2", "#991b1b", "Rejeté"),
    }
    
    def __init__(self, statut: str, parent=None):
        super().__init__(parent)
        
        bg, fg, label = self.STATUS_STYLES.get(
            statut, ("#e2e8f0", "#475569", statut)
        )
        
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


class LotBadge(QLabel):
    """Badge pour le numéro de lot avec icône FontAwesome"""
    
    def __init__(self, lot_id, parent=None):
        super().__init__(parent)
        
        if lot_id and str(lot_id) not in ('-', '', 'None'):
            # ✅ Utiliser un container avec icône + texte
            self.setText(f"   {lot_id}  ")
            self.setStyleSheet("""
                QLabel {
                    background: #ede9fe;
                    color: #6d28d9;
                    border-radius: 10px;
                    padding: 2px 8px;
                    font-size: 10px;
                    font-weight: 700;
                    border: 1px solid #ddd6fe;
                }
            """)
        else:
            self.setText("  —  ")
            self.setStyleSheet("""
                QLabel {
                    background: transparent;
                    color: #cbd5e1;
                    font-size: 11px;
                }
            """)
        
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(20)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)


# ═══════════════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════

class ReglementsPage(QWidget):
    """Page de gestion des règlements — Design moderne v2.0"""
    
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
        self.selected_reglement_id = None
        
        # Pagination
        self._current_page = 1
        self._per_page = 15
        self._total_reglements = 0
        
        self.setup_ui()
        self._appliquer_permissions()
        self.load_data()
    
    def _appliquer_permissions(self):
        """Cache les boutons selon les permissions"""
        self.permissions_ui.masquer_si_non_autorise(
            self.btn_creer_reg, 'reglement', 'CREATE'
        )
        self.permissions_ui.masquer_si_non_autorise(
            self.btn_creer_lot, 'reglement', 'CREATE'
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
        """En-tête : titre + filtre sinistre + bouton Nouveau Règlement"""
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
        icon_lbl.setPixmap(qta.icon('fa5s.credit-card', color='#2563eb').pixmap(QSize(24, 24)))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_lbl)
        
        layout.addWidget(icon_container)
        
        # Titre + sous-titre
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title = QLabel("Gestion des Règlements")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
            background: transparent;
        """)
        title_block.addWidget(title)
        
        subtitle = QLabel("Suivi et traitement des règlements")
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
        
        # ✅ Bouton Nouveau Règlement avec icône plus
        self.btn_creer_reg = QPushButton("  Nouveau Règlement")
        self.btn_creer_reg.setCursor(Qt.PointingHandCursor)
        self.btn_creer_reg.setFixedHeight(38)
        self.btn_creer_reg.setIcon(qta.icon('fa5s.plus-circle', color='white'))
        self.btn_creer_reg.setIconSize(QSize(14, 14))
        self.btn_creer_reg.setStyleSheet("""
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
        self.btn_creer_reg.clicked.connect(self.creer_reglement)
        layout.addWidget(self.btn_creer_reg)
        
        return frame
    
    def _build_stats_row(self):
        """Rangée de 4 cartes statistiques avec icônes FontAwesome"""
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        
        self.card_total = StatCard(
            icon_name="fa5s.folder-open", 
            title="Total Règlements", value="0",
            color_bg="#dbeafe", color_fg="#1e40af"
        )
        self.card_payes = StatCard(
            icon_name="fa5s.check-double", 
            title="Payés", value="0",
            color_bg="#d1fae5", color_fg="#059669"
        )
        self.card_valides = StatCard(
            icon_name="fa5s.shield-alt", 
            title="Validés", value="0",
            color_bg="#cffafe", color_fg="#0891b2"
        )
        self.card_attente = StatCard(
            icon_name="fa5s.hourglass-half", 
            title="En attente", value="0",
            color_bg="#fed7aa", color_fg="#ea580c"
        )
        
        layout.addWidget(self.card_total)
        layout.addWidget(self.card_payes)
        layout.addWidget(self.card_valides)
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
        
        title = QLabel("Liste des Règlements")
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
            "Tous les statuts", "Créé", "Validé", "Payé", "En attente",
            "Traité", "Annulé", "Rejeté"
        ])
        self.statut_filter.setStyleSheet("""
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
        self.table_reglements = QTableWidget()
        self.table_reglements.setColumnCount(8)
        self.table_reglements.setHorizontalHeaderLabels([
            "N° Règlement", "Bénéficiaire", "Montant", "Type",
            "Date", "Statut", "Lot", "Actions"
        ])
        
        self.table_reglements.setStyleSheet("""
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
        
        self.table_reglements.setAlternatingRowColors(False)
        self.table_reglements.verticalHeader().setVisible(False)
        self.table_reglements.verticalHeader().setDefaultSectionSize(52)
        self.table_reglements.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_reglements.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_reglements.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_reglements.setShowGrid(False)
        
        # Largeurs
        header_view = self.table_reglements.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table_reglements.setColumnWidth(7, 60)
        
        # Signaux
        self.table_reglements.itemSelectionChanged.connect(
            self._on_reglement_selection_changed
        )
        self.table_reglements.cellClicked.connect(self._on_reglement_cell_clicked)
        
        # Menu contextuel
        self.table_reglements.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_reglements.customContextMenuRequested.connect(
            self._show_table_context_menu
        )
        
        layout.addWidget(self.table_reglements)
        
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
        pag_layout.addWidget(self.btn_prev)
        
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
        
        # ✅ Bouton Valider
        self.btn_valider_reg = QPushButton("  Valider")
        self.btn_valider_reg.setCursor(Qt.PointingHandCursor)
        self.btn_valider_reg.setIcon(qta.icon('fa5s.check-circle', color='#d97706'))
        self.btn_valider_reg.setIconSize(QSize(14, 14))
        self.btn_valider_reg.setStyleSheet(btn_style % ("#f59e0b", "#d97706"))
        self.btn_valider_reg.clicked.connect(self.valider_reglement)
        layout.addWidget(self.btn_valider_reg)
        
        # ✅ Bouton Payer
        self.btn_payer_reg = QPushButton("  Payer")
        self.btn_payer_reg.setCursor(Qt.PointingHandCursor)
        self.btn_payer_reg.setIcon(qta.icon('fa5s.credit-card', color='#16a34a'))
        self.btn_payer_reg.setIconSize(QSize(14, 14))
        self.btn_payer_reg.setStyleSheet(btn_style % ("#22c55e", "#16a34a"))
        self.btn_payer_reg.clicked.connect(self.payer_reglement)
        layout.addWidget(self.btn_payer_reg)
        
        # ✅ Bouton Créer lot
        self.btn_creer_lot = QPushButton("  Créer un lot")
        self.btn_creer_lot.setCursor(Qt.PointingHandCursor)
        self.btn_creer_lot.setIcon(qta.icon('fa5s.boxes', color='#7c3aed'))
        self.btn_creer_lot.setIconSize(QSize(14, 14))
        self.btn_creer_lot.setStyleSheet(btn_style % ("#8b5cf6", "#7c3aed"))
        self.btn_creer_lot.clicked.connect(self.creer_lot_paiement)
        layout.addWidget(self.btn_creer_lot)
        
        # ✅ Bouton Valider lot
        self.btn_valider_lot = QPushButton("  Valider lot")
        self.btn_valider_lot.setCursor(Qt.PointingHandCursor)
        self.btn_valider_lot.setIcon(qta.icon('fa5s.check-double', color='#0891b2'))
        self.btn_valider_lot.setIconSize(QSize(14, 14))
        self.btn_valider_lot.setStyleSheet(btn_style % ("#06b6d4", "#0891b2"))
        self.btn_valider_lot.clicked.connect(self.valider_lot_paiement)
        layout.addWidget(self.btn_valider_lot)
        
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
            self.sinistre_combo.addItem("Sélectionner un sinistre", None)
            
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
        """Charge les règlements du sinistre sélectionné"""
        if index > 0:
            sinistre_id = self.sinistre_combo.currentData()
            if sinistre_id:
                self.current_sinistre_id = sinistre_id
                self._current_page = 1
                self.load_reglements(sinistre_id)
    
    def load_reglements(self, sinistre_id: int):
        """Charge les règlements d'un sinistre"""
        try:
            reglements = self.controller.get_reglements_by_sinistre(sinistre_id)
            
            # Filtre recherche
            query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""
            if query:
                reglements = [
                    r for r in reglements
                    if query in str(r.get('numero_reglement', '')).lower()
                    or query in str(r.get('beneficiaire_nom', '')).lower()
                ]
            
            # Filtre statut
            statut_filter = self.statut_filter.currentText() if hasattr(self, 'statut_filter') else "Tous les statuts"
            if statut_filter != "Tous les statuts":
                statut_map = {
                    "Créé": "CREE", "Validé": "VALIDE", "Payé": "PAYE",
                    "En attente": "EN_ATTENTE", "Traité": "TRAITE",
                    "Annulé": "ANNULE", "Rejeté": "REJETE"
                }
                target = statut_map.get(statut_filter, "")
                if target:
                    reglements = [r for r in reglements if r.get('statut') == target]
            
            self._total_reglements = len(reglements)
            
            # Pagination
            start = (self._current_page - 1) * self._per_page
            end = start + self._per_page
            page_data = reglements[start:end]
            
            # Mise à jour des stats
            self._update_stats(reglements)
            
            # Remplir le tableau
            self.table_reglements.setRowCount(len(page_data))
            
            for i, reg in enumerate(page_data):
                self._fill_row(i, reg)
            
            self._update_pagination(start, min(end, self._total_reglements))
            
            # Reset boutons
            self.btn_valider_reg.setEnabled(False)
            self.btn_payer_reg.setEnabled(False)
            self.btn_valider_lot.setEnabled(False)
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement règlements: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _fill_row(self, row: int, reg: dict):
        """Remplit une ligne du tableau"""
        # 0. N° Règlement
        num_item = QTableWidgetItem(reg.get('numero_reglement', ''))
        num_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        num_item.setForeground(QColor("#2563eb"))
        self.table_reglements.setItem(row, 0, num_item)
        
        # 1. Bénéficiaire
        self.table_reglements.setItem(
            row, 1, QTableWidgetItem(reg.get('beneficiaire_nom', '') or '-')
        )
        
        # 2. Montant
        montant = reg.get('montant', 0) or 0
        montant_str = f"{float(montant):,.0f}".replace(",", " ")
        montant_item = QTableWidgetItem(f"{montant_str} FCFA")
        montant_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_reglements.setItem(row, 2, montant_item)
        
        # 3. Type
        self.table_reglements.setItem(
            row, 3, QTableWidgetItem(reg.get('type_paiement', '') or '-')
        )
        
        # 4. Date
        date_demande = reg.get('date_demande', '')
        if date_demande:
            try:
                dt = datetime.fromisoformat(str(date_demande)[:19])
                date_str = dt.strftime("%d %b %Y")
            except Exception:
                date_str = str(date_demande)[:10]
        else:
            date_str = '-'
        self.table_reglements.setItem(row, 4, QTableWidgetItem(date_str))
        
        # 5. Statut (badge)
        statut = reg.get('statut', '')
        badge = StatusBadge(statut)
        badge_container = QWidget()
        badge_layout = QHBoxLayout(badge_container)
        badge_layout.setContentsMargins(4, 6, 4, 6)
        badge_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        badge_layout.addWidget(badge)
        badge_layout.addStretch()
        self.table_reglements.setCellWidget(row, 5, badge_container)
        
        # 6. Lot (badge)
        lot_id = reg.get('lot_paiement_id')
        lot_badge = LotBadge(lot_id)
        lot_container = QWidget()
        lot_layout = QHBoxLayout(lot_container)
        lot_layout.setContentsMargins(4, 8, 4, 8)
        lot_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lot_layout.addWidget(lot_badge)
        lot_layout.addStretch()
        self.table_reglements.setCellWidget(row, 6, lot_container)
        
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
            lambda checked=False, r=reg, b=btn_actions: self._show_row_actions_menu(r, b)
        )
        
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(4, 6, 4, 6)
        actions_layout.setAlignment(Qt.AlignCenter)
        actions_layout.addWidget(btn_actions)
        self.table_reglements.setCellWidget(row, 7, actions_container)
    
    def _update_stats(self, reglements: list):
        """Met à jour les 4 cartes statistiques"""
        total = len(reglements)
        payes = sum(1 for r in reglements if r.get('statut') == 'PAYE')
        valides = sum(1 for r in reglements if r.get('statut') == 'VALIDE')
        attente = sum(1 for r in reglements if r.get('statut') in ['CREE', 'EN_ATTENTE'])
        
        for card, value in [
            (self.card_total, total),
            (self.card_payes, payes),
            (self.card_valides, valides),
            (self.card_attente, attente),
        ]:
            for lbl in card.findChildren(QLabel):
                if lbl.objectName() == "stat_value":
                    lbl.setText(f"{value:,}".replace(",", " "))
    
    def _update_pagination(self, start: int, end: int):
        """Met à jour la pagination"""
        self.lbl_pagination.setText(
            f"{start + 1}-{end} de {self._total_reglements:,}".replace(",", " ")
            if self._total_reglements > 0 else "0-0 de 0"
        )
        self.btn_prev.setEnabled(self._current_page > 1)
        self.btn_next.setEnabled(end < self._total_reglements)
    
    def _go_prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self.load_reglements(self.current_sinistre_id)
    
    def _go_next_page(self):
        if self._current_page * self._per_page < self._total_reglements:
            self._current_page += 1
            self.load_reglements(self.current_sinistre_id)
    
    def _on_search_changed(self, text: str):
        """Recherche en temps réel"""
        self._current_page = 1
        if self.current_sinistre_id:
            self.load_reglements(self.current_sinistre_id)
    
    def _on_filter_changed(self, text: str):
        """Filtre statut"""
        self._current_page = 1
        if self.current_sinistre_id:
            self.load_reglements(self.current_sinistre_id)
    
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
    
    def _show_table_context_menu(self, position):
        """Affiche le menu contextuel au clic droit sur une ligne"""
        row = self.table_reglements.currentRow()
        if row < 0:
            menu = QMenu(self)
            menu.setStyleSheet(self._menu_style())
            # ✅ Icône refresh
            action_refresh = menu.addAction(
                qta.icon('fa5s.sync-alt', color='#64748b'),
                "  Actualiser"
            )
            action_refresh.triggered.connect(lambda: self.load_reglements(self.current_sinistre_id))
            menu.exec(self.table_reglements.viewport().mapToGlobal(position))
            return
        
        # Récupérer les données du règlement
        reg_numero = self.table_reglements.item(row, 0).text()
        
        try:
            reg_data = self.controller.get_reglement_by_numero(reg_numero)
            if not reg_data:
                return
        except Exception as e:
            print(f"❌ Erreur récupération règlement: {e}")
            return
        
        statut = reg_data.get('statut', '')
        lot_id = reg_data.get('lot_paiement_id')
        
        # Créer le menu
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        # ─── Consultation ───
        action_details = QAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir les détails", self
        )
        action_details.triggered.connect(
            lambda: self._action_details_from_menu(reg_data)
        )
        menu.addAction(action_details)
        
        # Si lot associé
        if lot_id and str(lot_id) not in ('-', '', 'None'):
            action_lot = QAction(
                qta.icon('fa5s.box', color='#7c3aed'),
                f"  Voir le lot {lot_id}", self
            )
            action_lot.triggered.connect(
                lambda: self._action_voir_lot(lot_id)
            )
            menu.addAction(action_lot)
        
        menu.addSeparator()
        
        # ─── Actions métier ───
        
        # Valider (si CREE)
        if statut == "CREE":
            if self.permissions_ui.peut('reglement', 'VALIDATE'):
                action_valider = QAction(
                    qta.icon('fa5s.check-circle', color='#f59e0b'),
                    "  Valider", self
                )
                action_valider.triggered.connect(
                    lambda: self._action_valider_from_menu(reg_numero)
                )
                menu.addAction(action_valider)
        
        # Payer (si VALIDE)
        if statut == "VALIDE":
            if self.permissions_ui.peut('reglement', 'PAY'):
                action_payer = QAction(
                    qta.icon('fa5s.credit-card', color='#22c55e'),
                    "  Payer", self
                )
                action_payer.triggered.connect(
                    lambda: self._action_payer_from_menu(reg_numero)
                )
                menu.addAction(action_payer)
        
        # Valider le lot
        if lot_id and str(lot_id) not in ('-', '', 'None') and statut == "VALIDE":
            if self.permissions_ui.peut('reglement', 'VALIDATE'):
                action_valider_lot = QAction(
                    qta.icon('fa5s.check-double', color='#06b6d4'),
                    f"  Valider le lot {lot_id}", self
                )
                action_valider_lot.triggered.connect(
                    lambda: self._action_valider_lot_from_menu(lot_id)
                )
                menu.addAction(action_valider_lot)
        
        menu.addSeparator()
        
        # ─── Annulation / Rejet ───
        if statut not in ["PAYE", "ANNULE", "REJETE"]:
            if self.permissions_ui.peut('reglement', 'DELETE'):
                action_annuler = QAction(
                    qta.icon('fa5s.ban', color='#ef4444'),
                    "  Annuler", self
                )
                action_annuler.triggered.connect(
                    lambda: self._action_annuler_from_menu(reg_data)
                )
                menu.addAction(action_annuler)
        
        # ─── Utilitaires ───
        menu.addSeparator()
        
        action_copy = QAction(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier le N°", self
        )
        action_copy.triggered.connect(lambda: self._copy_to_clipboard(reg_numero))
        menu.addAction(action_copy)
        
        # Afficher
        menu.exec(self.table_reglements.viewport().mapToGlobal(position))
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS DU MENU CONTEXTUEL
    # ═══════════════════════════════════════════════════════════════
    
    def _action_details_from_menu(self, reg_data: dict):
        """Affiche les détails d'un règlement"""
        QMessageBox.information(
            self,
            f"Règlement {reg_data.get('numero_reglement', 'N/A')}",
            f"<b>Bénéficiaire :</b> {reg_data.get('beneficiaire_nom', 'N/A')}<br>"
            f"<b>Montant :</b> {float(reg_data.get('montant', 0)):,.0f} FCFA<br>"
            f"<b>Type :</b> {reg_data.get('type_paiement', 'N/A')}<br>"
            f"<b>Date demande :</b> {str(reg_data.get('date_demande', ''))[:10]}<br>"
            f"<b>Statut :</b> {reg_data.get('statut', 'N/A')}<br>"
            f"<b>Lot :</b> {reg_data.get('lot_paiement_id', '-') or '-'}"
        )
    
    def _action_voir_lot(self, lot_id):
        """Affiche les détails d'un lot"""
        try:
            from addons.sinistres.views.lot_paiement_dialog import LotPaiementDialog
            dialog = LotPaiementDialog(
                reglement_controller=self.controller,
                user=self.user,
                parent=self,
                lot_id=lot_id
            )
            dialog.exec()
        except Exception:
            QMessageBox.information(
                self, "Info",
                f"Lot {lot_id}\n\n"
                f"Pour voir les détails du lot, ouvrez le dialogue des lots."
            )
    
    def _action_valider_from_menu(self, reg_numero: str):
        """Valide un règlement depuis le menu"""
        self._select_row_by_numero(reg_numero)
        self.valider_reglement()
    
    def _action_payer_from_menu(self, reg_numero: str):
        """Paye un règlement depuis le menu"""
        self._select_row_by_numero(reg_numero)
        self.payer_reglement()
    
    def _action_valider_lot_from_menu(self, lot_id):
        """Valide un lot depuis le menu"""
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous valider le lot {lot_id} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.valider_lot_paiement(int(lot_id))
                if result:
                    QMessageBox.information(self, "Succès", f"Lot {lot_id} validé")
                    if self.current_sinistre_id:
                        self.load_reglements(self.current_sinistre_id)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def _action_annuler_from_menu(self, reg_data: dict):
        """Annule un règlement"""
        reg_numero = reg_data.get('numero_reglement', 'N/A')
        
        from PySide6.QtWidgets import QInputDialog
        motif, ok = QInputDialog.getMultiLineText(
            self, f"Annuler le règlement {reg_numero}",
            "Motif d'annulation (obligatoire) :", ""
        )
        
        if not ok or not motif.strip():
            return
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Annuler le règlement {reg_numero} ?\n\nMotif : {motif}",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        try:
            if hasattr(self.controller, 'annuler_reglement'):
                result = self.controller.annuler_reglement(reg_data.get('id'), motif=motif)
                if result:
                    QMessageBox.information(self, "Succès", "Règlement annulé")
                    if self.current_sinistre_id:
                        self.load_reglements(self.current_sinistre_id)
            else:
                QMessageBox.information(
                    self, "Info",
                    "Fonction d'annulation à implémenter dans le contrôleur."
                )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
    
    def _select_row_by_numero(self, reg_numero: str):
        """Sélectionne la ligne par numéro"""
        for i in range(self.table_reglements.rowCount()):
            item = self.table_reglements.item(i, 0)
            if item and item.text() == reg_numero:
                self.table_reglements.selectRow(i)
                return
    
    def _copy_to_clipboard(self, text: str):
        """Copie dans le presse-papiers"""
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copié", f"'{text}' copié")
    
    # ═══════════════════════════════════════════════════════════════
    # MENU D'ACTIONS PAR LIGNE (bouton ⋯)
    # ═══════════════════════════════════════════════════════════════
    
    def _show_row_actions_menu(self, reg: dict, button: QPushButton):
        """Affiche le menu d'actions depuis le bouton ⋯"""
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        statut = reg.get('statut', '')
        reg_numero = reg.get('numero_reglement', '')
        lot_id = reg.get('lot_paiement_id')
        
        # Consultation
        action_details = menu.addAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir les détails"
        )
        action_details.triggered.connect(
            lambda: self._action_details_from_menu(reg)
        )
        
        if lot_id and str(lot_id) not in ('-', '', 'None'):
            action_lot = menu.addAction(
                qta.icon('fa5s.box', color='#7c3aed'),
                f"  Voir le lot {lot_id}"
            )
            action_lot.triggered.connect(lambda: self._action_voir_lot(lot_id))
        
        menu.addSeparator()
        
        # Actions métier
        if statut == "CREE" and self.permissions_ui.peut('reglement', 'VALIDATE'):
            action_valider = menu.addAction(
                qta.icon('fa5s.check-circle', color='#f59e0b'),
                "  Valider"
            )
            action_valider.triggered.connect(
                lambda: self._action_valider_from_menu(reg_numero)
            )
        
        if statut == "VALIDE" and self.permissions_ui.peut('reglement', 'PAY'):
            action_payer = menu.addAction(
                qta.icon('fa5s.credit-card', color='#22c55e'),
                "  Payer"
            )
            action_payer.triggered.connect(
                lambda: self._action_payer_from_menu(reg_numero)
            )
        
        if lot_id and str(lot_id) not in ('-', '', 'None') and statut == "VALIDE":
            if self.permissions_ui.peut('reglement', 'VALIDATE'):
                action_vl = menu.addAction(
                    qta.icon('fa5s.check-double', color='#06b6d4'),
                    f"  Valider lot {lot_id}"
                )
                action_vl.triggered.connect(
                    lambda: self._action_valider_lot_from_menu(lot_id)
                )
        
        menu.addSeparator()
        
        if statut not in ["PAYE", "ANNULE", "REJETE"]:
            if self.permissions_ui.peut('reglement', 'DELETE'):
                action_ann = menu.addAction(
                    qta.icon('fa5s.ban', color='#ef4444'),
                    "  Annuler"
                )
                action_ann.triggered.connect(
                    lambda: self._action_annuler_from_menu(reg)
                )
        
        menu.addSeparator()
        
        action_copy = menu.addAction(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier le N°"
        )
        action_copy.triggered.connect(lambda: self._copy_to_clipboard(reg_numero))
        
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
    
    # ═══════════════════════════════════════════════════════════════
    # EXPORT — inchangé
    # ═══════════════════════════════════════════════════════════════
    
    def _export_data(self):
        """Exporte en CSV"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les règlements",
            f"reglements_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV (*.csv)"
        )
        if not path:
            return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "N° Règlement", "Bénéficiaire", "Montant",
                    "Type", "Date", "Statut", "Lot"
                ])
                for row in range(self.table_reglements.rowCount()):
                    values = []
                    for col in range(7):
                        item = self.table_reglements.item(row, col)
                        if item:
                            values.append(item.text())
                        else:
                            widget = self.table_reglements.cellWidget(row, col)
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
                f"{self.table_reglements.rowCount()} règlements exportés"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS MÉTIER — inchangées
    # ═══════════════════════════════════════════════════════════════
    
    def creer_reglement(self):
        """Crée un nouveau règlement"""
        if not self.current_sinistre_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un sinistre")
            return
        
        sinistre_info = {}
        try:
            from addons.sinistres.controllers.sinistre_controller import SinistreController
            sc = SinistreController()
            sc.set_current_user(self.user)
            sinistre_data = sc.get_sinistre(self.current_sinistre_id)
            if sinistre_data:
                sinistre_info = {
                    'numero_sinistre': sinistre_data.get('numero_sinistre', 'N/A'),
                    'client_nom': 'N/A',
                    'branche': sinistre_data.get('branche', 'N/A')
                }
        except Exception:
            pass
        
        from addons.sinistres.views.reglement_dialog import ReglementDialog
        dialog = ReglementDialog(
            sinistre_id=self.current_sinistre_id,
            reglement_controller=self.controller,
            user=self.user,
            sinistre_info=sinistre_info,
            parent=self
        )
        dialog.reglement_created.connect(self._on_reglement_created)
        dialog.exec()
    
    def _on_reglement_created(self, data: dict):
        self.load_reglements(self.current_sinistre_id)
        QMessageBox.information(self, "Succès", "Règlement créé avec succès !")
    
    def valider_reglement(self):
        """Valide le règlement sélectionné"""
        row = self.table_reglements.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un règlement")
            return
        
        reglement_numero = self.table_reglements.item(row, 0).text()
        
        try:
            reg_data = self.controller.get_reglement_by_numero(reglement_numero)
            if not reg_data:
                QMessageBox.warning(self, "Erreur", "Règlement non trouvé")
                return
            statut = reg_data.get('statut', '')
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {e}")
            return
        
        if statut != "CREE":
            QMessageBox.warning(
                self, "Attention",
                f"Seul un règlement au statut 'CRÉÉ' peut être validé (statut: {statut})"
            )
            return
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Valider le règlement {reglement_numero} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.valider_reglement(reg_data.get('id'))
                if result:
                    QMessageBox.information(self, "Succès", "Règlement validé")
                    self.load_reglements(self.current_sinistre_id)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def payer_reglement(self):
        """Paye le règlement sélectionné"""
        row = self.table_reglements.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un règlement")
            return
        
        reglement_numero = self.table_reglements.item(row, 0).text()
        
        try:
            reg_data = self.controller.get_reglement_by_numero(reglement_numero)
            if not reg_data:
                return
            statut = reg_data.get('statut', '')
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
            return
        
        if statut != "VALIDE":
            QMessageBox.warning(
                self, "Attention",
                f"Seul un règlement au statut 'VALIDÉ' peut être payé (statut: {statut})"
            )
            return
        
        from addons.sinistres.views.paiement_dialog import PaiementDialog
        dialog = PaiementDialog(
            reglement_numero=reglement_numero,
            reglement_controller=self.controller,
            user=self.user,
            parent=self
        )
        dialog.paiement_effectue.connect(self._on_paiement_effectue)
        dialog.exec()
    
    def _on_reglement_selection_changed(self):
        """Active/désactive les boutons selon la sélection"""
        row = self.table_reglements.currentRow()
        
        if row < 0:
            self.btn_valider_reg.setEnabled(False)
            self.btn_payer_reg.setEnabled(False)
            self.btn_valider_lot.setEnabled(False)
            return
        
        reg_numero = self.table_reglements.item(row, 0).text()
        
        try:
            reg_data = self.controller.get_reglement_by_numero(reg_numero)
            if not reg_data:
                return
            statut = reg_data.get('statut', '')
            lot_id = reg_data.get('lot_paiement_id')
        except Exception:
            return
        
        peut_valider = self.permissions_ui.peut('reglement', 'VALIDATE')
        peut_payer = self.permissions_ui.peut('reglement', 'PAY')
        
        self.btn_valider_reg.setEnabled(
            bool(peut_valider and statut == "CREE")
        )
        self.btn_payer_reg.setEnabled(
            bool(peut_payer and statut == "VALIDE")
        )
        self.btn_valider_lot.setEnabled(
            _safe_bool(peut_valider) 
            and _safe_bool(lot_id) 
            and str(lot_id) not in ('-', '', 'None')
        )
    
    def _on_paiement_effectue(self, data: dict):
        self.load_reglements(self.current_sinistre_id)
        QMessageBox.information(self, "Succès", "Paiement effectué !")
    
    def creer_lot_paiement(self):
        """Crée un lot de paiement"""
        from addons.sinistres.views.lot_paiement_dialog import LotPaiementDialog
        dialog = LotPaiementDialog(
            reglement_controller=self.controller,
            user=self.user,
            parent=self
        )
        dialog.lot_created.connect(self._on_lot_created)
        dialog.exec()
    
    def _on_lot_created(self, data: dict):
        QMessageBox.information(
            self, "Succès",
            f"Lot {data.get('numero_lot')} créé !\n"
            f"{data.get('nombre_paiements')} règlements\n"
            f"{data.get('montant_total', 0):,.0f} FCFA"
        )
        if self.current_sinistre_id:
            self.load_reglements(self.current_sinistre_id)
    
    def valider_lot_paiement(self):
        """Valide un lot de paiement"""
        row = self.table_reglements.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un règlement")
            return
        
        reg_numero = self.table_reglements.item(row, 0).text()
        
        try:
            reg_data = self.controller.get_reglement_by_numero(reg_numero)
            lot_id = reg_data.get('lot_paiement_id') if reg_data else None
        except Exception:
            lot_id = None
        
        if not lot_id or str(lot_id) in ('-', '', 'None'):
            QMessageBox.warning(self, "Attention", "Ce règlement n'appartient à aucun lot")
            return
        
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Valider le lot {lot_id} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = self.controller.valider_lot_paiement(int(lot_id))
                if result:
                    QMessageBox.information(self, "Succès", f"Lot {lot_id} validé")
                    if self.current_sinistre_id:
                        self.load_reglements(self.current_sinistre_id)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))
    
    def _on_reglement_cell_clicked(self, row: int, col: int):
        """Clic sur une ligne"""
        if col == 7:
            return
        reg_numero = self.table_reglements.item(row, 0).text()
        try:
            reg_data = self.controller.get_reglement_by_numero(reg_numero)
            if reg_data:
                self.selected_reglement_id = reg_data.get('id')
        except Exception:
            pass
    
    def get_selected_reglement_id(self) -> Optional[int]:
        """Retourne l'ID du règlement sélectionné"""
        row = self.table_reglements.currentRow()
        if row >= 0:
            reg_numero = self.table_reglements.item(row, 0).text()
            try:
                reg_data = self.controller.get_reglement_by_numero(reg_numero)
                if reg_data:
                    return reg_data.get('id')
            except Exception:
                pass
        return None
    
    def get_lots_by_sinistre(self, sinistre_id: int):
        """Récupère les lots d'un sinistre"""
        try:
            return self.controller.get_lots_by_sinistre(sinistre_id)
        except Exception as e:
            print(f"Erreur chargement lots: {e}")
            return []