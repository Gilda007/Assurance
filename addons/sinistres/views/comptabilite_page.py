"""
Page de comptabilité - Design moderne avec onglets
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QFrame, QMessageBox, QDialog,
    QGraphicsDropShadowEffect, QLineEdit, QComboBox, QDateEdit, QMenu,
    QTabWidget, QScrollArea, QSizePolicy, QAbstractItemView, QApplication,
    QFileDialog
)
from PySide6.QtCore import Qt, QSize, Signal, QDate, QTimer
from PySide6.QtGui import QColor, QFont, QAction

import qtawesome as qta
from datetime import datetime, timedelta
from typing import Optional, List, Dict


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def make_icon_label(icon_name: str, color: str = "#64748b", size: int = 16) -> QLabel:
    """Crée un QLabel avec une icône FontAwesome."""
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
    lbl.setStyleSheet("background: transparent; border: none;")
    return lbl


# ═══════════════════════════════════════════════════════════════════
# WIDGETS PERSONNALISÉS
# ═══════════════════════════════════════════════════════════════════

class StatCard(QFrame):
    """Carte statistique"""
    
    def __init__(self, icon_name, title, value, color_bg, color_fg, parent=None):
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
        
        # Icône
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
        
        icon_lbl = make_icon_label(icon_name, color=color_fg, size=22)
        icon_layout.addWidget(icon_lbl)
        
        layout.addWidget(icon_container)
        
        # Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
        
        value_lbl = QLabel(str(value))
        value_lbl.setStyleSheet(f"color: {color_fg}; font-size: 22px; font-weight: 800;")
        value_lbl.setObjectName("stat_value")
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(value_lbl)
        
        layout.addLayout(text_layout, 1)


# ═══════════════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════

class ComptabilitePage(QWidget):
    """Page de comptabilité - 5 onglets"""
    
    def __init__(self, controller, user):
        super().__init__()
        self.controller = controller
        self.user = user
        
        # Pagination
        self._journal_page = 1
        self._per_page = 20
        self._total_ecritures = 0
        
        self.setup_ui()
        self.load_data()
    
    # ================================================================
    # UI
    # ================================================================
    
    def setup_ui(self):
        self.setStyleSheet("background: #f1f5f9;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        layout.addWidget(self._build_header())
        layout.addWidget(self._build_stats_row())
        layout.addWidget(self._build_tabs(), 1)
    
    def _build_header(self):
        """En-tête"""
        frame = QFrame()
        frame.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
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
        
        icon_lbl = make_icon_label('fa5s.book', color='#2563eb', size=24)
        icon_layout.addWidget(icon_lbl)
        
        layout.addWidget(icon_container)
        
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title = QLabel("Comptabilité")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a;")
        title_block.addWidget(title)
        
        subtitle = QLabel("Journal, grand livre, balance et rapprochement")
        subtitle.setStyleSheet("color: #64748b; font-size: 12px;")
        title_block.addWidget(subtitle)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        # Bouton refresh
        btn_refresh = QPushButton()
        btn_refresh.setFixedSize(36, 36)
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#64748b'))
        btn_refresh.setIconSize(QSize(14, 14))
        btn_refresh.setToolTip("Actualiser")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QPushButton:hover { background: #f8fafc; }
        """)
        btn_refresh.clicked.connect(self.load_data)
        layout.addWidget(btn_refresh)
        
        return frame
    
    def _build_stats_row(self):
        """Rangée de 4 cartes statistiques"""
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        
        self.card_total = StatCard(
            'fa5s.book', "Total écritures", "0",
            "#dbeafe", "#1e40af"
        )
        self.card_banque = StatCard(
            'fa5s.university', "Journal Banque", "0",
            "#d1fae5", "#059669"
        )
        self.card_sinistres = StatCard(
            'fa5s.file-invoice', "Journal Sinistres", "0",
            "#fed7aa", "#ea580c"
        )
        self.card_non_rapprochees = StatCard(
            'fa5s.exclamation-triangle', "Non rapprochées", "0",
            "#fee2e2", "#dc2626"
        )
        
        layout.addWidget(self.card_total)
        layout.addWidget(self.card_banque)
        layout.addWidget(self.card_sinistres)
        layout.addWidget(self.card_non_rapprochees)
        
        return wrapper
    
    def _build_tabs(self):
        """Onglets principaux"""
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
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
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
            QTabBar::tab:hover { color: #1e293b; }
            QTabBar::tab:selected {
                color: #2563eb;
                border-bottom: 2px solid #2563eb;
            }
        """)
        
        # Onglet 1 : Journal
        self.tabs.addTab(self._build_journal_tab(), "  Journal  ")
        
        # Onglet 2 : Grand Livre
        self.tabs.addTab(self._build_grand_livre_tab(), "  Grand Livre  ")
        
        # Onglet 3 : Balance
        self.tabs.addTab(self._build_balance_tab(), "  Balance  ")
        
        # Onglet 4 : Rapprochement
        self.tabs.addTab(self._build_rapprochement_tab(), "  Rapprochement  ")
        
        layout.addWidget(self.tabs)
        return card
    
    # ================================================================
    # ONGLET JOURNAL
    # ================================================================
    
    def _build_journal_tab(self):
        """Onglet Journal"""
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: transparent;
                border-bottom: 1px solid #f1f5f9;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(10)
        
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.addWidget(make_icon_label('fa5s.list', color='#2563eb', size=14))
        
        title = QLabel("Journal des écritures")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a;")
        title_row.addWidget(title)
        header_layout.addLayout(title_row)
        header_layout.addStretch()
        
        # Filtre journal
        self.journal_filter = QComboBox()
        self.journal_filter.addItem("Tous les journaux", None)
        self.journal_filter.addItem("Banque", "BANQUE")
        self.journal_filter.addItem("Sinistres", "SINISTRES")
        self.journal_filter.addItem("Recours", "RECOURS")
        self.journal_filter.addItem("Régularisations", "REGULARISATIONS")
        self.journal_filter.setMinimumWidth(180)
        self.journal_filter.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
            }
        """)
        self.journal_filter.currentIndexChanged.connect(self._reload_journal)
        header_layout.addWidget(self.journal_filter)
        
        # Bouton export
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
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover { background: #f8fafc; }
        """)
        btn_export.clicked.connect(self._export_journal)
        header_layout.addWidget(btn_export)
        
        layout.addWidget(header)
        
        # Tableau
        self.table_journal = QTableWidget()
        self.table_journal.setColumnCount(8)
        self.table_journal.setHorizontalHeaderLabels([
            "N° Écriture", "Date", "Journal", "Libellé",
            "Débit", "Crédit", "Montant", "Statut"
        ])
        self._setup_table(self.table_journal)
        
        header_view = self.table_journal.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.Stretch)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        
        self.table_journal.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_journal.customContextMenuRequested.connect(
            self._show_journal_context_menu
        )
        
        layout.addWidget(self.table_journal)
        
        return tab
    
    # ================================================================
    # ONGLET GRAND LIVRE
    # ================================================================
    
    def _build_grand_livre_tab(self):
        """Onglet Grand Livre"""
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: transparent;
                border-bottom: 1px solid #f1f5f9;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(10)
        
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.addWidget(make_icon_label('fa5s.book-open', color='#2563eb', size=14))
        
        title = QLabel("Grand Livre")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a;")
        title_row.addWidget(title)
        header_layout.addLayout(title_row)
        header_layout.addStretch()
        
        # Compte
        header_layout.addWidget(QLabel("Compte :"))
        self.gl_compte_input = QLineEdit()
        self.gl_compte_input.setPlaceholderText("ex: 616000")
        self.gl_compte_input.setFixedWidth(150)
        self.gl_compte_input.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }
        """)
        self.gl_compte_input.returnPressed.connect(self._load_grand_livre)
        header_layout.addWidget(self.gl_compte_input)
        
        btn_load = QPushButton("  Charger")
        btn_load.setCursor(Qt.PointingHandCursor)
        btn_load.setIcon(qta.icon('fa5s.search', color='white'))
        btn_load.setIconSize(QSize(12, 12))
        btn_load.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        btn_load.clicked.connect(self._load_grand_livre)
        header_layout.addWidget(btn_load)
        
        layout.addWidget(header)
        
        # Résumé
        self.gl_summary = QFrame()
        self.gl_summary.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        summary_layout = QHBoxLayout(self.gl_summary)
        summary_layout.setContentsMargins(20, 12, 20, 12)
        summary_layout.setSpacing(20)
        
        self.gl_lbl_total_debit = QLabel("Total Débit : 0 FCFA")
        self.gl_lbl_total_debit.setStyleSheet("color: #1e40af; font-weight: 600;")
        summary_layout.addWidget(self.gl_lbl_total_debit)
        
        self.gl_lbl_total_credit = QLabel("Total Crédit : 0 FCFA")
        self.gl_lbl_total_credit.setStyleSheet("color: #059669; font-weight: 600;")
        summary_layout.addWidget(self.gl_lbl_total_credit)
        
        self.gl_lbl_solde = QLabel("Solde : 0 FCFA")
        self.gl_lbl_solde.setStyleSheet("color: #0f172a; font-weight: 700;")
        summary_layout.addWidget(self.gl_lbl_solde)
        
        summary_layout.addStretch()
        layout.addWidget(self.gl_summary)
        
        # Tableau
        self.table_grand_livre = QTableWidget()
        self.table_grand_livre.setColumnCount(6)
        self.table_grand_livre.setHorizontalHeaderLabels([
            "Date", "N° Écriture", "Libellé", "Journal",
            "Débit", "Crédit"
        ])
        self._setup_table(self.table_grand_livre)
        
        header_view = self.table_grand_livre.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table_grand_livre)
        
        return tab
    
    # ================================================================
    # ONGLET BALANCE
    # ================================================================
    
    def _build_balance_tab(self):
        """Onglet Balance"""
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: transparent;
                border-bottom: 1px solid #f1f5f9;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(10)
        
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.addWidget(make_icon_label('fa5s.balance-scale', color='#2563eb', size=14))
        
        title = QLabel("Balance comptable")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a;")
        title_row.addWidget(title)
        header_layout.addLayout(title_row)
        header_layout.addStretch()
        
        btn_refresh_balance = QPushButton("  Actualiser")
        btn_refresh_balance.setCursor(Qt.PointingHandCursor)
        btn_refresh_balance.setIcon(qta.icon('fa5s.sync-alt', color='#1e293b'))
        btn_refresh_balance.setIconSize(QSize(12, 12))
        btn_refresh_balance.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover { background: #f8fafc; }
        """)
        btn_refresh_balance.clicked.connect(self._load_balance)
        header_layout.addWidget(btn_refresh_balance)
        
        layout.addWidget(header)
        
        # Tableau
        self.table_balance = QTableWidget()
        self.table_balance.setColumnCount(4)
        self.table_balance.setHorizontalHeaderLabels([
            "Compte", "Total Débit", "Total Crédit", "Solde"
        ])
        self._setup_table(self.table_balance)
        
        header_view = self.table_balance.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.Stretch)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table_balance)
        
        return tab
    
    # ================================================================
    # ONGLET RAPPROCHEMENT
    # ================================================================
    
    def _build_rapprochement_tab(self):
        """Onglet Rapprochement bancaire"""
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: transparent;
                border-bottom: 1px solid #f1f5f9;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(10)
        
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.addWidget(make_icon_label('fa5s.check-double', color='#2563eb', size=14))
        
        title = QLabel("Écritures non rapprochées")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a;")
        title_row.addWidget(title)
        header_layout.addLayout(title_row)
        header_layout.addStretch()
        
        btn_load_rap = QPushButton("  Charger")
        btn_load_rap.setCursor(Qt.PointingHandCursor)
        btn_load_rap.setIcon(qta.icon('fa5s.sync-alt', color='white'))
        btn_load_rap.setIconSize(QSize(12, 12))
        btn_load_rap.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        btn_load_rap.clicked.connect(self._load_non_rapprochees)
        header_layout.addWidget(btn_load_rap)
        
        layout.addWidget(header)
        
        # Tableau
        self.table_rapprochement = QTableWidget()
        self.table_rapprochement.setColumnCount(7)
        self.table_rapprochement.setHorizontalHeaderLabels([
            "N° Écriture", "Date", "Journal", "Libellé",
            "Compte Débit", "Compte Crédit", "Montant"
        ])
        self._setup_table(self.table_rapprochement)
        
        header_view = self.table_rapprochement.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.Stretch)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.table_rapprochement.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_rapprochement.customContextMenuRequested.connect(
            self._show_rapprochement_context_menu
        )
        
        layout.addWidget(self.table_rapprochement)
        
        return tab
    
    # ================================================================
    # HELPERS TABLEAU
    # ================================================================
    
    def _setup_table(self, table: QTableWidget):
        """Configure un tableau"""
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
            QTableWidget::item:selected {
                background: #eff6ff;
                color: #1e293b;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 12px 8px;
                font-weight: 600;
                font-size: 12px;
                color: #475569;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(48)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setShowGrid(False)
        table.setAlternatingRowColors(False)
    
    # ================================================================
    # CHARGEMENT DES DONNÉES
    # ================================================================
    
    def load_data(self):
        """Charge toutes les données"""
        self._load_stats()
        self._reload_journal()
    
    def refresh(self):
        """Rafraîchit la page"""
        self.load_data()
    
    def _load_stats(self):
        """Charge les statistiques"""
        try:
            stats = self.controller.get_statistiques()
            
            total = stats.get('total_ecritures', 0)
            par_journal = stats.get('par_journal', {})
            non_rapprochees = stats.get('non_rapprochees', 0)
            
            # Mettre à jour les cartes
            for lbl in self.card_total.findChildren(QLabel):
                if lbl.objectName() == "stat_value":
                    lbl.setText(str(total))
            
            for lbl in self.card_banque.findChildren(QLabel):
                if lbl.objectName() == "stat_value":
                    lbl.setText(str(par_journal.get('BANQUE', 0)))
            
            for lbl in self.card_sinistres.findChildren(QLabel):
                if lbl.objectName() == "stat_value":
                    lbl.setText(str(par_journal.get('SINISTRES', 0)))
            
            for lbl in self.card_non_rapprochees.findChildren(QLabel):
                if lbl.objectName() == "stat_value":
                    lbl.setText(str(non_rapprochees))
        except Exception as e:
            print(f"⚠️ Erreur stats : {e}")
    
    def _reload_journal(self):
        """Recharge le journal"""
        try:
            journal = self.journal_filter.currentData()
            ecritures = self.controller.get_ecritures_by_journal(journal or "")
            
            # Si pas de filtre, charger tous les journaux
            if not journal:
                all_ecritures = []
                for j in ['BANQUE', 'SINISTRES', 'RECOURS', 'REGULARISATIONS']:
                    all_ecritures.extend(
                        self.controller.get_ecritures_by_journal(j)
                    )
                ecritures = sorted(
                    all_ecritures,
                    key=lambda e: e.get('date_ecriture', ''),
                    reverse=True
                )
            
            self._fill_journal_table(ecritures)
        except Exception as e:
            print(f"⚠️ Erreur journal : {e}")
    
    def _fill_journal_table(self, ecritures: list):
        """Remplit le tableau du journal"""
        self.table_journal.setRowCount(len(ecritures))
        
        for i, e in enumerate(ecritures):
            # N° Écriture
            num_item = QTableWidgetItem(e.get('numero_ecriture', ''))
            num_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
            num_item.setForeground(QColor("#2563eb"))
            self.table_journal.setItem(i, 0, num_item)
            
            # Date
            date_str = e.get('date_ecriture', '')
            if date_str:
                try:
                    dt = datetime.fromisoformat(str(date_str)[:19])
                    date_str = dt.strftime("%d/%m/%Y")
                except:
                    date_str = str(date_str)[:10]
            self.table_journal.setItem(i, 1, QTableWidgetItem(date_str))
            
            # Journal
            self.table_journal.setItem(i, 2, QTableWidgetItem(e.get('journal', '')))
            
            # Libellé
            self.table_journal.setItem(i, 3, QTableWidgetItem(e.get('libelle', '')))
            
            # Débit
            self.table_journal.setItem(i, 4, QTableWidgetItem(e.get('compte_debit', '')))
            
            # Crédit
            self.table_journal.setItem(i, 5, QTableWidgetItem(e.get('compte_credit', '')))
            
            # Montant
            montant = e.get('montant', 0)
            montant_str = f"{float(montant):,.0f}".replace(",", " ")
            montant_item = QTableWidgetItem(f"{montant_str} FCFA")
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            montant_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
            self.table_journal.setItem(i, 6, montant_item)
            
            # Statut
            statut = "Annulée" if e.get('est_annulee') else (
                "Rapprochée" if e.get('est_rapprochee') else (
                    "Validée" if e.get('est_valide') else "En attente"
                )
            )
            statut_item = QTableWidgetItem(statut)
            if e.get('est_annulee'):
                statut_item.setForeground(QColor("#dc2626"))
            elif e.get('est_rapprochee'):
                statut_item.setForeground(QColor("#059669"))
            elif e.get('est_valide'):
                statut_item.setForeground(QColor("#2563eb"))
            else:
                statut_item.setForeground(QColor("#f59e0b"))
            
            self.table_journal.setItem(i, 7, statut_item)
            
            # Stocker les données
            self.table_journal.item(i, 0).setData(Qt.UserRole, e)
    
    def _load_grand_livre(self):
        """Charge le grand livre"""
        compte = self.gl_compte_input.text().strip()
        if not compte:
            QMessageBox.warning(self, "Attention", "Veuillez saisir un compte")
            return
        
        try:
            result = self.controller.get_grand_livre(compte)
            if not result:
                QMessageBox.information(self, "Info", "Aucune écriture pour ce compte")
                return
            
            # Résumé
            self.gl_lbl_total_debit.setText(
                f"Total Débit : {result.get('total_debit', 0):,.0f} FCFA".replace(",", " ")
            )
            self.gl_lbl_total_credit.setText(
                f"Total Crédit : {result.get('total_credit', 0):,.0f} FCFA".replace(",", " ")
            )
            self.gl_lbl_solde.setText(
                f"Solde : {result.get('solde_final', 0):,.0f} FCFA".replace(",", " ")
            )
            
            # Tableau
            mouvements = result.get('mouvements', [])
            self.table_grand_livre.setRowCount(len(mouvements))
            
            for i, m in enumerate(mouvements):
                # Date
                date_str = m.get('date', '')
                if date_str:
                    try:
                        dt = datetime.fromisoformat(str(date_str)[:19])
                        date_str = dt.strftime("%d/%m/%Y")
                    except:
                        date_str = str(date_str)[:10]
                self.table_grand_livre.setItem(i, 0, QTableWidgetItem(date_str))
                
                # N° Écriture
                num_item = QTableWidgetItem(m.get('numero', ''))
                num_item.setForeground(QColor("#2563eb"))
                self.table_grand_livre.setItem(i, 1, num_item)
                
                # Libellé
                self.table_grand_livre.setItem(i, 2, QTableWidgetItem(m.get('libelle', '')))
                
                # Journal
                self.table_grand_livre.setItem(i, 3, QTableWidgetItem(m.get('journal', '')))
                
                # Débit
                debit = m.get('debit', 0)
                if debit:
                    debit_item = QTableWidgetItem(f"{debit:,.0f}".replace(",", " "))
                    debit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    debit_item.setForeground(QColor("#1e40af"))
                else:
                    debit_item = QTableWidgetItem("—")
                self.table_grand_livre.setItem(i, 4, debit_item)
                
                # Crédit
                credit = m.get('credit', 0)
                if credit:
                    credit_item = QTableWidgetItem(f"{credit:,.0f}".replace(",", " "))
                    credit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    credit_item.setForeground(QColor("#059669"))
                else:
                    credit_item = QTableWidgetItem("—")
                self.table_grand_livre.setItem(i, 5, credit_item)
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur : {str(e)}")
    
    def _load_balance(self):
        """Charge la balance"""
        try:
            balance = self.controller.get_balance()
            
            self.table_balance.setRowCount(len(balance))
            
            for i, ligne in enumerate(balance):
                # Compte
                compte_item = QTableWidgetItem(ligne.get('compte', ''))
                compte_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
                self.table_balance.setItem(i, 0, compte_item)
                
                # Total Débit
                debit = ligne.get('total_debit', 0)
                debit_item = QTableWidgetItem(f"{debit:,.0f}".replace(",", " "))
                debit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                debit_item.setForeground(QColor("#1e40af"))
                self.table_balance.setItem(i, 1, debit_item)
                
                # Total Crédit
                credit = ligne.get('total_credit', 0)
                credit_item = QTableWidgetItem(f"{credit:,.0f}".replace(",", " "))
                credit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                credit_item.setForeground(QColor("#059669"))
                self.table_balance.setItem(i, 2, credit_item)
                
                # Solde
                solde = ligne.get('solde', 0)
                solde_item = QTableWidgetItem(f"{solde:,.0f}".replace(",", " "))
                solde_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                solde_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
                solde_item.setForeground(
                    QColor("#0f172a") if solde >= 0 else QColor("#dc2626")
                )
                self.table_balance.setItem(i, 3, solde_item)
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur : {str(e)}")
    
    def _load_non_rapprochees(self):
        """Charge les écritures non rapprochées"""
        try:
            ecritures = self.controller.get_ecritures_non_rapprochees()
            
            self.table_rapprochement.setRowCount(len(ecritures))
            
            for i, e in enumerate(ecritures):
                # N° Écriture
                num_item = QTableWidgetItem(e.get('numero_ecriture', ''))
                num_item.setForeground(QColor("#2563eb"))
                num_item.setData(Qt.UserRole, e)
                self.table_rapprochement.setItem(i, 0, num_item)
                
                # Date
                date_str = e.get('date_ecriture', '')
                if date_str:
                    try:
                        dt = datetime.fromisoformat(str(date_str)[:19])
                        date_str = dt.strftime("%d/%m/%Y")
                    except:
                        date_str = str(date_str)[:10]
                self.table_rapprochement.setItem(i, 1, QTableWidgetItem(date_str))
                
                # Journal
                self.table_rapprochement.setItem(i, 2, QTableWidgetItem(e.get('journal', '')))
                
                # Libellé
                self.table_rapprochement.setItem(i, 3, QTableWidgetItem(e.get('libelle', '')))
                
                # Compte Débit
                self.table_rapprochement.setItem(i, 4, QTableWidgetItem(e.get('compte_debit', '')))
                
                # Compte Crédit
                self.table_rapprochement.setItem(i, 5, QTableWidgetItem(e.get('compte_credit', '')))
                
                # Montant
                montant = e.get('montant', 0)
                montant_item = QTableWidgetItem(f"{float(montant):,.0f}".replace(",", " "))
                montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                montant_item.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
                self.table_rapprochement.setItem(i, 6, montant_item)
        
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur : {str(e)}")
    
    # ================================================================
    # MENUS CONTEXTUELS
    # ================================================================
    
    def _show_journal_context_menu(self, position):
        """Menu contextuel sur le journal"""
        row = self.table_journal.currentRow()
        if row < 0:
            return
        
        item = self.table_journal.item(row, 0)
        if not item:
            return
        ecriture_data = item.data(Qt.UserRole)
        if not ecriture_data:
            return
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 6px;
                min-width: 220px;
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
            QMenu::separator {
                height: 1px;
                background: #f1f5f9;
                margin: 4px 8px;
            }
        """)
        
        est_annulee = ecriture_data.get('est_annulee', False)
        est_valide = ecriture_data.get('est_valide', False)
        
        # Voir détails
        action_detail = menu.addAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir les détails"
        )
        action_detail.triggered.connect(
            lambda: self._show_ecriture_detail(ecriture_data)
        )
        
        menu.addSeparator()
        
        # Valider
        if not est_annulee and not est_valide:
            action_valider = menu.addAction(
                qta.icon('fa5s.check-circle', color='#22c55e'),
                "  Valider"
            )
            action_valider.triggered.connect(
                lambda: self._valider_ecriture(ecriture_data)
            )
        
        # Annuler
        if not est_annulee:
            action_annuler = menu.addAction(
                qta.icon('fa5s.ban', color='#ef4444'),
                "  Annuler"
            )
            action_annuler.triggered.connect(
                lambda: self._annuler_ecriture(ecriture_data)
            )
        
        menu.exec(self.table_journal.viewport().mapToGlobal(position))
    
    def _show_rapprochement_context_menu(self, position):
        """Menu contextuel sur le rapprochement"""
        row = self.table_rapprochement.currentRow()
        if row < 0:
            return
        
        item = self.table_rapprochement.item(row, 0)
        if not item:
            return
        ecriture_data = item.data(Qt.UserRole)
        if not ecriture_data:
            return
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 6px;
                min-width: 220px;
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
        """)
        
        action_rapprocher = menu.addAction(
            qta.icon('fa5s.check-double', color='#22c55e'),
            "  Rapprocher cette écriture"
        )
        action_rapprocher.triggered.connect(
            lambda: self._rapprocher_ecriture(ecriture_data)
        )
        
        menu.exec(self.table_rapprochement.viewport().mapToGlobal(position))
    
    # ================================================================
    # ACTIONS
    # ================================================================
    
    def _show_ecriture_detail(self, data: dict):
        """Affiche les détails d'une écriture"""
        QMessageBox.information(
            self,
            f"Écriture {data.get('numero_ecriture', 'N/A')}",
            f"<b>Journal :</b> {data.get('journal', 'N/A')}<br>"
            f"<b>Libellé :</b> {data.get('libelle', 'N/A')}<br>"
            f"<b>Débit :</b> {data.get('compte_debit', 'N/A')}<br>"
            f"<b>Crédit :</b> {data.get('compte_credit', 'N/A')}<br>"
            f"<b>Montant :</b> {data.get('montant', 0):,.0f} FCFA<br>"
            f"<b>Référence :</b> {data.get('reference_type', 'N/A')} "
            f"#{data.get('reference_id', 'N/A')}<br>"
            f"<b>Date :</b> {str(data.get('date_ecriture', ''))[:19]}<br>"
            f"<b>Statut :</b> "
            f"{'❌ Annulée' if data.get('est_annulee') else ('✅ Validée' if data.get('est_valide') else '⏳ En attente')}"
        )
    
    def _valider_ecriture(self, data: dict):
        """Valide une écriture"""
        reply = QMessageBox.question(
            self, "Confirmation",
            f"Valider l'écriture {data.get('numero_ecriture')} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        if self.controller.valider_ecriture(data.get('id')):
            self._reload_journal()
            self._load_stats()
    
    def _annuler_ecriture(self, data: dict):
        """Annule une écriture"""
        from PySide6.QtWidgets import QInputDialog
        
        motif, ok = QInputDialog.getMultiLineText(
            self, f"Annuler l'écriture {data.get('numero_ecriture')}",
            "Motif d'annulation (obligatoire) :", ""
        )
        
        if not ok or not motif.strip():
            return
        
        if self.controller.annuler_ecriture(data.get('id'), motif):
            self._reload_journal()
            self._load_stats()
    
    def _rapprocher_ecriture(self, data: dict):
        """Rapproche une écriture"""
        from PySide6.QtWidgets import QInputDialog
        
        reference, ok = QInputDialog.getText(
            self, "Rapprochement bancaire",
            f"Référence bancaire pour {data.get('numero_ecriture')} :"
        )
        
        if not ok or not reference.strip():
            return
        
        if self.controller.rapprocher_ecriture(data.get('id'), reference):
            self._load_non_rapprochees()
            self._load_stats()
    
    def _export_journal(self):
        """Exporte le journal en CSV"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter le journal",
            f"journal_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV (*.csv)"
        )
        if not path:
            return
        
        try:
            import csv
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                headers = [
                    self.table_journal.horizontalHeaderItem(i).text()
                    for i in range(self.table_journal.columnCount())
                ]
                writer.writerow(headers)
                
                for row in range(self.table_journal.rowCount()):
                    values = []
                    for col in range(self.table_journal.columnCount()):
                        item = self.table_journal.item(row, col)
                        values.append(item.text() if item else '')
                    writer.writerow(values)
            
            QMessageBox.information(
                self, "Export réussi",
                f"{self.table_journal.rowCount()} écritures exportées"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export : {e}")