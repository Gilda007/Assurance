
"""
Gestion des Contacts - Interface moderne et professionnelle
Utilisation de QtAwesome pour les icônes
"""

import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QLineEdit, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QFileDialog, QScrollArea,
    QSizePolicy, QDialog, QComboBox, QMenu, QTextEdit,
    QGridLayout, QSplitter, QToolButton, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QMargins
from PySide6.QtGui import QFont, QColor, QAction, QBrush, QPainter, QIcon
from PySide6.QtCharts import (
    QChart, QChartView, QPieSeries, QBarSeries, QBarSet,
    QBarCategoryAxis, QValueAxis
)
import qtawesome as qta

from addons.Automobiles.security.access_control import Permissions, SecurityManager
from addons.Automobiles.views.contact_form_view import ContactForm
from addons.Automobiles.reports.pdf_generator import generate_contact_pdf
from core.logger import logger
from core.workers.database_worker import async_query


class ContactListView(QWidget):
    """Interface moderne de gestion des contacts"""
    
    contact_selected = Signal(object)
    contact_updated = Signal()
    
    # Palette de couleurs moderne
    COLORS = {
        'primary': '#2563eb',
        'primary_light': '#dbeafe',
        'success': '#16a34a',
        'success_light': '#dcfce7',
        'warning': '#f59e0b',
        'warning_light': '#fef3c7',
        'danger': '#dc2626',
        'danger_light': '#fee2e2',
        'purple': '#7c3aed',
        'purple_light': '#ede9fe',
        'teal': '#0d9488',
        'teal_light': '#ccfbf1',
        'orange': '#ea580c',
        'orange_light': '#ffedd5',
        'gray': '#64748b',
        'gray_light': '#f1f5f9',
        'dark': '#0f172a',
        'border': '#e2e8f0',
        'bg': '#f8fafc',
        'white': '#ffffff',
    }

    ICONS = {
        'address_book': 'mdi.account',
        'users': 'mdi.account-multiple',
        'user_check': 'mdi.account-check',
        'user_tie': 'mdi.account-tie',
        'circle_check': 'mdi.check-circle',
        'circle_xmark': 'mdi.close-circle',
        'circle_info': 'mdi.information',
        'triangle_exclamation': 'mdi.alert',
        'plus': 'mdi.plus',
        'pen': 'mdi.pencil',
        'trash_can': 'mdi.delete',
        'copy': 'mdi.content-copy',
        'eye': 'mdi.eye',
        'note_sticky': 'mdi.note',
        'floppy_disk': 'mdi.content-save',
        'file_csv': 'mdi.file-delimited',
        'file_pdf': 'mdi.file-pdf-box',
        'file_import': 'mdi.file-import',
        'file_export': 'mdi.file-export',
        'magnifying_glass': 'mdi.magnify',
        'list': 'mdi.format-list-bulleted',
        'clipboard_list': 'mdi.clipboard-list',
        'rotate_right': 'mdi.sync',
        'bars': 'mdi.menu',
        'filter': 'mdi.filter',
        'download': 'mdi.download',
        'upload': 'mdi.upload',
        'print': 'mdi.printer',
        'share': 'mdi.share',
        'star': 'mdi.star',
        'heart': 'mdi.heart',
        'user_astronaut': 'mdi.rocket',
    }

    def __init__(self, controller, current_user):
        super().__init__()
        self.controller = controller
        self.current_user = current_user
        self._data_loaded = False
        self.all_contacts = []
        self.filtered_contacts = []
        self.selected_contacts = []
        
        self.setup_ui()
        self.apply_security_policy()
        self.load_contacts()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """Configure l'interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setStyleSheet(f"""
            QWidget {{
                background: {self.COLORS['bg']};
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }}
        """)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 24, 32, 24)
        container_layout.setSpacing(20)
        
        # En-tête
        # self._create_header(container_layout)
        
        # Barre d'outils
        self._create_toolbar(container_layout)
        
        # Statistiques
        self._create_stats(container_layout)
        
        # Tableau
        self._create_table(container_layout)
        
        # Barre de statut
        self._create_status_bar(container_layout)
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
    
    # def _create_header(self, parent_layout):
    #     """Crée l'en-tête avec style moderne"""
    #     header = QFrame()
    #     header.setStyleSheet(f"""
    #         QFrame {{
    #             background: {self.COLORS['white']};
    #             border-radius: 16px;
    #             border: 1px solid {self.COLORS['border']};
    #             padding: 20px 28px;
    #         }}
    #     """)
        
    #     layout = QHBoxLayout(header)
    #     layout.setSpacing(24)
        
    #     # Titre avec icône
    #     title_layout = QVBoxLayout()
    #     title_layout.setSpacing(4)
        
    #     title_widget = QWidget()
    #     title_widget_layout = QHBoxLayout(title_widget)
    #     title_widget_layout.setContentsMargins(0, 0, 0, 0)
    #     title_widget_layout.setSpacing(12)
        
    #     icon_label = QLabel()
    #     icon_label.setPixmap(qta.icon(self.ICONS['address_book'], color=self.COLORS['primary']).pixmap(32, 32))
    #     title_widget_layout.addWidget(icon_label)
        
    #     title = QLabel("Contacts")
    #     title.setStyleSheet(f"""
    #         font-size: 24px;
    #         font-weight: 700;
    #         color: {self.COLORS['dark']};
    #         background: transparent;
    #         border: none;
    #         letter-spacing: -0.5px;
    #     """)
    #     title_widget_layout.addWidget(title)
    #     title_widget_layout.addStretch()
        
    #     subtitle = QLabel("Gérez vos contacts, clients et prospects")
    #     subtitle.setStyleSheet(f"""
    #         font-size: 14px;
    #         color: {self.COLORS['gray']};
    #         background: transparent;
    #         border: none;
    #         padding-left: 44px;
    #     """)
        
    #     title_layout.addWidget(title_widget)
    #     title_layout.addWidget(subtitle)
        
    #     # Compteurs
    #     counter_layout = QHBoxLayout()
    #     counter_layout.setSpacing(24)
        
    #     self.total_label = self._create_counter('users', "0", "Total")
    #     self.active_label = self._create_counter('user_check', "0", "Actifs")
        
    #     counter_layout.addWidget(self.total_label)
    #     counter_layout.addWidget(self.active_label)
        
    #     layout.addLayout(title_layout)
    #     layout.addStretch()
    #     layout.addLayout(counter_layout)
        
    #     parent_layout.addWidget(header)
    
    def _create_counter(self, icon_name, count, label):
        """Crée un compteur moderne"""
        container = QFrame()
        container.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(self.ICONS[icon_name], color=self.COLORS['primary']).pixmap(20, 20))
        icon_label.setStyleSheet("background: transparent; border: none;")
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        
        count_label = QLabel(count)
        count_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 700;
            color: {self.COLORS['dark']};
            background: transparent;
            border: none;
        """)
        count_label.setObjectName(f"counter_{label.lower()}")
        
        name_label = QLabel(label)
        name_label.setStyleSheet(f"""
            font-size: 11px;
            color: {self.COLORS['gray']};
            text-transform: uppercase;
            letter-spacing: 0.8px;
            background: transparent;
            border: none;
        """)
        
        text_layout.addWidget(count_label)
        text_layout.addWidget(name_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        
        return container
    
    def _create_toolbar(self, parent_layout):
        """Crée la barre d'outils moderne et professionnelle"""
        toolbar = QFrame()
        toolbar.setStyleSheet(f"""
            QFrame {{
                background: {self.COLORS['white']};
                border-radius: 16px;
                border: 1px solid {self.COLORS['border']};
                padding: 8px 16px;
            }}
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # ============================================================
        # GROUPE 1 : Actions principales (CRUD)
        # ============================================================
        self.btn_add = self._create_action_btn(
            "Nouveau", self.COLORS['primary'], 'plus',
            shortcut="Ctrl+N", tooltip="Ajouter un contact (Ctrl+N)"
        )
        self.btn_add.clicked.connect(self.on_add_contact)
        
        self.btn_edit = self._create_action_btn(
            "Modifier", self.COLORS['primary'], 'pen',
            shortcut="Ctrl+E", tooltip="Modifier le contact sélectionné (Ctrl+E)"
        )
        self.btn_edit.clicked.connect(self.on_edit_contact)
        self.btn_edit.setEnabled(False)
        
        self.btn_delete = self._create_action_btn(
            "Supprimer", self.COLORS['danger'], 'trash_can',
            shortcut="Delete", tooltip="Supprimer le(s) contact(s) sélectionné(s) (Delete)"
        )
        self.btn_delete.clicked.connect(self.on_delete_contact)
        self.btn_delete.setEnabled(False)
        
        self.btn_duplicate = self._create_action_btn(
            "Dupliquer", self.COLORS['purple'], 'copy',
            shortcut="Ctrl+D", tooltip="Dupliquer le contact sélectionné (Ctrl+D)"
        )
        self.btn_duplicate.clicked.connect(self.duplicate_contact)
        self.btn_duplicate.setEnabled(False)
        
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_edit)
        layout.addWidget(self.btn_delete)
        layout.addWidget(self.btn_duplicate)
        
        # Séparateur
        layout.addWidget(self._create_separator())
        
        # ============================================================
        # GROUPE 2 : Import / Export
        # ============================================================
        self.btn_import = self._create_action_btn(
            "Importer", self.COLORS['teal'], 'file_import',
            is_small=True, tooltip="Importer des contacts depuis un fichier"
        )
        self.btn_import.clicked.connect(self.import_contacts)
        
        self.btn_export_csv = self._create_action_btn(
            "Exporter CSV", self.COLORS['teal'], 'file_csv',
            is_small=True, tooltip="Exporter les contacts au format CSV"
        )
        self.btn_export_csv.clicked.connect(self.export_to_csv)
        
        self.btn_export_pdf = self._create_action_btn(
            "Exporter PDF", self.COLORS['danger'], 'file_pdf',
            is_small=True, tooltip="Exporter les contacts au format PDF"
        )
        self.btn_export_pdf.clicked.connect(self.export_to_pdf)
        
        layout.addWidget(self.btn_import)
        # layout.addWidget(self.btn_export_csv)
        layout.addWidget(self.btn_export_pdf)
        
        # Séparateur
        layout.addWidget(self._create_separator())
        
        # ============================================================
        # GROUPE 3 : Outils
        # ============================================================
        self.btn_audit = self._create_action_btn(
            "Audit", self.COLORS['purple'], 'clipboard_list',
            is_small=True, tooltip="Consulter l'historique des actions"
        )
        self.btn_audit.clicked.connect(self.show_audit_logs)
        
        self.btn_refresh = self._create_action_btn(
            "", self.COLORS['gray'], 'rotate_right',
            is_small=True, icon_only=True, tooltip="Actualiser la liste (Ctrl+R)"
        )
        self.btn_refresh.clicked.connect(self.load_contacts)
        
        layout.addWidget(self.btn_audit)
        layout.addWidget(self.btn_refresh)
        
        # ============================================================
        # ESPACEUR + RECHERCHE
        # ============================================================
        layout.addStretch()
        
        # Indicateur de sélection
        self.selection_label = QLabel("")
        self.selection_label.setStyleSheet(f"""
            color: {self.COLORS['gray']};
            font-size: 12px;
            font-weight: 500;
            background: transparent;
            border: none;
            padding: 0 8px;
        """)
        layout.addWidget(self.selection_label)
        
        # Champ de recherche
        search_container = QFrame()
        search_container.setStyleSheet("background: transparent; border: none;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(0)
        
        # Icône de recherche
        search_icon = QLabel()
        search_icon.setPixmap(qta.icon(self.ICONS['magnifying_glass'], color=self.COLORS['gray']).pixmap(16, 16))
        search_icon.setStyleSheet("padding: 0 8px 0 14px; background: transparent; border: none;")
        
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un contact...")
        self.search_input.setMinimumWidth(220)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {self.COLORS['border']};
                border-radius: 10px;
                padding: 7px 14px 7px 4px;
                background: {self.COLORS['gray_light']};
                font-size: 13px;
                color: {self.COLORS['dark']};
            }}
            QLineEdit:focus {{
                border-color: {self.COLORS['primary']};
                background: {self.COLORS['white']};
            }}
            QLineEdit::placeholder {{
                color: {self.COLORS['gray']};
                font-weight: 400;
            }}
        """)
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        
        layout.addWidget(search_container)
        
        # ============================================================
        # FILTRE
        # ============================================================
        filter_container = QFrame()
        filter_container.setStyleSheet("background: transparent; border: none;")
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(4)
        
        filter_icon = QLabel()
        filter_icon.setPixmap(qta.icon(self.ICONS['filter'], color=self.COLORS['gray']).pixmap(14, 14))
        filter_icon.setStyleSheet("padding: 0 2px 0 8px; background: transparent; border: none;")
        # filter_layout.addWidget(filter_icon)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Souscripteur", "Tous", "Chauffeur", "Particulier", "Société"])
        self.filter_combo.setStyleSheet(f"""
            QComboBox {{
                border: 2px solid {self.COLORS['border']};
                border-radius: 10px;
                padding: 6px 10px 6px 6px;
                background: {self.COLORS['gray_light']};
                font-size: 12px;
                color: {self.COLORS['dark']};
                min-width: 120px;
                font-weight: 500;
            }}
            QComboBox:focus {{
                border-color: {self.COLORS['primary']};
                background: {self.COLORS['white']};
            }}
            QComboBox:hover {{
                border-color: {self.COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                background: transparent;
                padding-right: 4px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
        """)
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_combo)
        
        layout.addWidget(filter_container)
        
        parent_layout.addWidget(toolbar)


    def _create_action_btn(self, text, color, icon_name, is_small=False, icon_only=False, shortcut=None, tooltip=None):
        """
        Crée un bouton d'action stylisé avec icône QtAwesome
        
        Args:
            text: Texte du bouton
            color: Couleur de fond
            icon_name: Nom de l'icône dans ICONS
            is_small: Bouton compact
            icon_only: Uniquement l'icône
            shortcut: Raccourci clavier (ex: "Ctrl+N")
            tooltip: Infobulle
        """
        btn = QPushButton()
        
        # Configuration de l'icône
        if icon_name and icon_name in self.ICONS:
            icon_color = 'white' if color != self.COLORS['gray'] else self.COLORS['dark']
            icon = qta.icon(self.ICONS[icon_name], color=icon_color)
            
            if icon_only:
                btn.setIcon(icon)
                btn.setIconSize(QSize(18, 18))
            else:
                btn.setText(f"  {text}")
                btn.setIcon(icon)
                btn.setIconSize(QSize(16, 16))
        else:
            btn.setText(text if not icon_only else "")
        
        # Taille du bouton
        if icon_only:
            btn.setFixedSize(36, 36)
        elif is_small:
            btn.setFixedHeight(32)
            btn.setMinimumWidth(80)
        else:
            btn.setFixedHeight(38)
            btn.setMinimumWidth(100)
        
        # Style du bouton
        padding = "6px 14px" if is_small else "8px 18px"
        font_size = "12px" if is_small else "13px"
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: {'white' if color != self.COLORS['gray'] else self.COLORS['dark']};
                border: none;
                border-radius: 10px;
                padding: {padding};
                font-weight: 600;
                font-size: {font_size};
                font-family: 'Inter', -apple-system, sans-serif;
            }}
            QPushButton:hover {{
                background: {self._darken_color(color, 15)};
            }}
            QPushButton:pressed {{
                background: {self._darken_color(color, 25)};
            }}
            QPushButton:disabled {{
                background: {self.COLORS['gray_light']};
                color: {self.COLORS['gray']};
            }}
        """)
        
        # Raccourci clavier
        if shortcut:
            btn.setShortcut(shortcut)
        
        # Infobulle
        if tooltip:
            btn.setToolTip(tooltip)
        
        return btn


    def _darken_color(self, hex_color, amount):
        """Assombrit une couleur hexadécimale"""
        try:
            # Convertir hex en RGB
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Assombrir
            r = max(0, r - amount)
            g = max(0, g - amount)
            b = max(0, b - amount)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color

    def _create_btn(self, text, color, icon_name=None, is_small=False, icon_only=False):
        """Crée un bouton stylisé avec icône QtAwesome"""
        btn = QPushButton()
        
        if icon_name:
            icon = qta.icon(self.ICONS[icon_name], color='white' if color != self.COLORS['gray'] else self.COLORS['dark'])
            if icon_only:
                btn.setIcon(icon)
                btn.setIconSize(QSize(18, 18))
            else:
                btn.setText(f"  {text}")
                btn.setIcon(icon)
                btn.setIconSize(QSize(16, 16))
        else:
            btn.setText(text)
        
        if icon_only:
            btn.setFixedSize(38, 38)
        elif is_small:
            btn.setFixedHeight(34)
        
        padding = "4px 12px" if is_small else "8px 18px"
        font_size = "12px" if is_small else "13px"
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: {'white' if color != self.COLORS['gray'] else self.COLORS['dark']};
                border: none;
                border-radius: 10px;
                padding: {padding};
                font-weight: 600;
                font-size: {font_size};
                font-family: 'Inter', sans-serif;
            }}
            QPushButton:hover {{
                background: {self._darken_color(color, 0.1)};
            }}
            QPushButton:pressed {{
                background: {self._darken_color(color, 0.2)};
            }}
            QPushButton:disabled {{
                background: {self.COLORS['gray_light']};
                color: {self.COLORS['gray']};
            }}
            QPushButton:disabled {{
                background: {self.COLORS['gray_light']};
                color: {self.COLORS['gray']};
            }}
        """)
        
        return btn
    
    def _create_separator(self):
        """Crée un séparateur vertical"""
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"background: {self.COLORS['border']}; max-width: 1px;")
        sep.setFixedWidth(1)
        sep.setFixedHeight(32)
        return sep
    
    def _darken_color(self, hex_color, amount):
        """Assombrit une couleur hexadécimale"""
        # Simplification: retourne une version plus sombre
        # Pour une implémentation complète, on pourrait utiliser QColor
        return hex_color
    
    def _create_stats(self, parent_layout):
        """Crée les statistiques modernes"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.COLORS['white']};
                border-radius: 16px;
                border: 1px solid {self.COLORS['border']};
                padding: 16px 20px;
            }}
        """)
        
        layout = QHBoxLayout(stats_frame)
        layout.setSpacing(16)
        
        # Cartes de stats
        stats_data = [
            ("total", "users", "Total", self.COLORS['primary']),
            ("souscripteurs", "user_tie", "Souscripteurs", self.COLORS['success']),
            ("chauffeurs", "user_astronaut", "Chauffeurs", self.COLORS['orange']),
            ("actifs", "circle_check", "Actifs", self.COLORS['purple'])
        ]
        
        self.stats_cards = {}
        for key, icon, label, color in stats_data:
            card = self._create_stat_card(icon, label, "0", color)
            layout.addWidget(card)
            self.stats_cards[key] = card
        
        layout.addStretch()
        
        parent_layout.addWidget(stats_frame)
    
    def _create_stat_card(self, icon_name, label, value, color):
        """Crée une carte de statistique moderne"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {color}08;
                border: 1px solid {color}25;
                border-radius: 8px;
                padding: 12px 18px;
                min-width: 120px;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setSpacing(14)
        layout.setContentsMargins(14, 10, 14, 10)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(self.ICONS['circle_check'], color=color).pixmap(24, 24))
        icon_label.setStyleSheet("background: transparent; border: none;")
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {color};
            background: transparent;
            border: none;
            letter-spacing: -0.5px;
        """)
        value_label.setObjectName(f"stat_{label.lower()}")
        
        name_label = QLabel(label)
        name_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 500;
            color: {self.COLORS['gray']};
            background: transparent;
            border: none;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        
        text_layout.addWidget(value_label)
        text_layout.addWidget(name_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        
        return card
    
    def _create_table(self, parent_layout):
        """Crée le tableau moderne"""
        table_container = QFrame()
        table_container.setStyleSheet(f"""
            QFrame {{
                background: {self.COLORS['white']};
                border-radius: 16px;
                border: 1px solid {self.COLORS['border']};
            }}
        """)
        
        layout = QVBoxLayout(table_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # En-tête du tableau
        header = QFrame()
        header.setStyleSheet(f"""
            background: transparent;
            border-bottom: 1px solid {self.COLORS['border']};
            padding: 14px 24px;
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon(self.ICONS['list'], color=self.COLORS['primary']).pixmap(18, 18))
        header_layout.addWidget(title_icon)
        
        title = QLabel("Liste des contacts")
        title.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 600;
            color: {self.COLORS['dark']};
            background: transparent;
            border: none;
            padding-left: 10px;
        """)
        header_layout.addWidget(title)
        
        # header_layout.addStretch()
        
        info = QLabel("Double-cliquez pour voir les détails")
        info.setStyleSheet(f"""
            font-size: 12px;
            color: {self.COLORS['gray']};
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(info)
        
        # layout.addWidget(header)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "CONTACT", "TÉLÉPHONE", "EMAIL", "TYPE", "NATURE", "STATUT", "ACTIONS"
        ])
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(62)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: transparent;
                border: none;
                outline: none;
                gridline-color: transparent;
                alternate-background-color: {self.COLORS['gray_light']};
            }}
            QTableWidget::item {{
                padding: 12px 14px;
                border-bottom: 1px solid {self.COLORS['border']};
                font-size: 13px;
                color: {self.COLORS['dark']};
                background: transparent;
            }}
            QTableWidget::item:selected {{
                background: {self.COLORS['primary_light']};
                color: {self.COLORS['dark']};
            }}
            QTableWidget::item:hover {{
                background: {self.COLORS['gray_light']};
            }}
            QHeaderView::section {{
                background: {self.COLORS['gray_light']};
                padding: 12px 14px;
                border: none;
                border-bottom: 2px solid {self.COLORS['border']};
                font-weight: 600;
                font-size: 11px;
                color: {self.COLORS['gray']};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)
        
        # Ajustement des largeurs de colonnes
        self.table.setColumnWidth(0, 55)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 160)
        
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)
        
        # Pied
        footer = QFrame()
        footer.setStyleSheet(f"""
            background: transparent;
            border-top: 1px solid {self.COLORS['border']};
            padding: 10px 24px;
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        
        self.total_rows_label = QLabel("0 contact(s)")
        self.total_rows_label.setStyleSheet(f"""
            color: {self.COLORS['gray']};
            font-size: 13px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        
        footer_layout.addWidget(self.total_rows_label)
        footer_layout.addStretch()
        
        # Indicateur de sélection
        self.selection_count_label = QLabel("")
        self.selection_count_label.setStyleSheet(f"""
            color: {self.COLORS['gray']};
            font-size: 12px;
            background: transparent;
            border: none;
        """)
        footer_layout.addWidget(self.selection_count_label)
        
        layout.addWidget(footer)
        
        parent_layout.addWidget(table_container)
    
    def _create_status_bar(self, parent_layout):
        """Crée la barre de statut moderne"""
        status_bar = QFrame()
        status_bar.setStyleSheet(f"""
            QFrame {{
                background: {self.COLORS['white']};
                border-radius: 16px;
                border: 1px solid {self.COLORS['border']};
                padding: 10px 24px;
            }}
        """)
        
        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Statut avec indicateur
        status_indicator = QLabel()
        status_indicator.setPixmap(qta.icon(self.ICONS['circle_check'], color=self.COLORS['success']).pixmap(16, 16))
        layout.addWidget(status_indicator)
        
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet(f"""
            color: {self.COLORS['success']};
            font-size: 13px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Version et info
        info_label = QLabel("v2.0")
        info_label.setStyleSheet(f"""
            color: {self.COLORS['gray']};
            font-size: 11px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(info_label)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet(f"background: {self.COLORS['border']}; max-width: 1px;")
        separator.setFixedWidth(1)
        separator.setFixedHeight(16)
        layout.addWidget(separator)
        
        self.last_update_label = QLabel("")
        self.last_update_label.setStyleSheet(f"""
            color: {self.COLORS['gray']};
            font-size: 11px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.last_update_label)
        
        parent_layout.addWidget(status_bar)
    
    def _create_avatar(self, item):
        """Crée un avatar moderne avec initiales"""
        nom = getattr(item, 'nom', '')
        prenom = getattr(item, 'prenom', '')
        
        if not nom and hasattr(item, 'data'):
            data = getattr(item, 'data', None)
            if data:
                nom = getattr(data, 'nom', '')
                prenom = getattr(data, 'prenom', '')
        
        initials = ""
        if prenom:
            initials += prenom[0].upper()
        if nom:
            initials += nom[0].upper()
        initials = initials or "?"
        
        display_type = getattr(item, 'display_type', 'Souscripteur')
        if display_type == "Chauffeur":
            color = self.COLORS['orange']
        else:
            color = self.COLORS['primary']
        
        avatar = QLabel(initials)
        avatar.setFixedSize(38, 38)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            background: {color};
            color: white;
            border-radius: 19px;
            font-weight: 700;
            font-size: 14px;
            font-family: 'Inter', sans-serif;
        """)
        return avatar
    
    # def _create_action_buttons(self, item):
    #     """Crée les boutons d'action modernes avec QtAwesome"""
    #     container = QWidget()
    #     layout = QHBoxLayout(container)
    #     layout.setContentsMargins(0, 0, 0, 0)
    #     layout.setSpacing(2)
    #     layout.setAlignment(Qt.AlignCenter)
        
    #     btn_style = """
    #         QPushButton {
    #             background: transparent;
    #             border-radius: 8px;
    #             padding: 6px;
    #             min-width: 36px;
    #             min-height: 36px;
    #             border: none;
    #             font-size: 14px;
    #         }
    #         QPushButton:hover {
    #             background: %s;
    #         }
    #     """
        
    #     # ✅ Voir
    #     btn_view = QPushButton()
    #     btn_view.setIcon(qta.icon(self.ICONS['eye'], color=self.COLORS['gray']))
    #     btn_view.setIconSize(QSize(16, 16))
    #     btn_view.setToolTip("Voir les détails")
    #     btn_view.setStyleSheet(btn_style % self.COLORS['primary_light'])
    #     btn_view.clicked.connect(lambda: self.view_contact(item))
        
    #     # ✅ Modifier
    #     btn_edit = QPushButton()
    #     btn_edit.setIcon(qta.icon(self.ICONS['pen'], color=self.COLORS['gray']))
    #     btn_edit.setIconSize(QSize(14, 14))
    #     btn_edit.setToolTip("Modifier")
    #     btn_edit.setStyleSheet(btn_style % self.COLORS['warning_light'])
    #     btn_edit.clicked.connect(lambda: self.edit_contact(item))
        
    #     # ✅ Note
    #     btn_note = QPushButton()
    #     btn_note.setIcon(qta.icon(self.COLORS['note_sticky'], color=self.COLORS['gray']))
    #     btn_note.setIconSize(QSize(14, 14))
    #     btn_note.setToolTip("Ajouter une note")
    #     btn_note.setStyleSheet(btn_style % self.COLORS['success_light'])
    #     btn_note.clicked.connect(lambda: self.add_quick_note(item))
        
    #     # ✅ Supprimer
    #     btn_delete = QPushButton()
    #     btn_delete.setIcon(qta.icon('trash_can', color=self.COLORS['gray']))
    #     btn_delete.setIconSize(QSize(14, 14))
    #     btn_delete.setToolTip("Supprimer")
    #     btn_delete.setStyleSheet(btn_style % self.COLORS['danger_light'])
    #     btn_delete.clicked.connect(lambda: self.delete_contact(item))
        
    #     layout.addWidget(btn_view)
    #     layout.addWidget(btn_edit)
    #     layout.addWidget(btn_note)
    #     layout.addWidget(btn_delete)
        
    #     return container

    def _create_action_buttons(self, item):
        """Crée les boutons d'action modernes avec QtAwesome"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        
        btn_style = """
            QPushButton {
                background: transparent;
                border-radius: 8px;
                padding: 8px;
                min-width: 36px;
                min-height: 36px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background: %s;
            }
        """
        
        # ✅ Voir
        btn_view = QPushButton()
        btn_view.setIcon(qta.icon(self.ICONS['eye'], color=self.COLORS['gray']))
        btn_view.setIconSize(QSize(18, 18))
        btn_view.setToolTip("Voir les détails")
        btn_view.setStyleSheet(btn_style % self.COLORS['primary_light'])
        btn_view.clicked.connect(lambda: self.view_contact(item))
        
        # ✅ Modifier
        btn_edit = QPushButton()
        btn_edit.setIcon(qta.icon(self.ICONS['pen'], color=self.COLORS['gray']))
        btn_edit.setIconSize(QSize(16, 16))
        btn_edit.setToolTip("Modifier")
        btn_edit.setStyleSheet(btn_style % self.COLORS['warning_light'])
        btn_edit.clicked.connect(lambda: self.edit_contact(item))
        
        # ✅ Note
        btn_note = QPushButton()
        btn_note.setIcon(qta.icon(self.ICONS['note_sticky'], color=self.COLORS['gray']))  # ✅ CORRIGÉ
        btn_note.setIconSize(QSize(16, 16))
        btn_note.setToolTip("Ajouter une note")
        btn_note.setStyleSheet(btn_style % self.COLORS['success_light'])
        btn_note.clicked.connect(lambda: self.add_quick_note(item))
        
        # ✅ Supprimer
        btn_delete = QPushButton()
        btn_delete.setIcon(qta.icon(self.ICONS['trash_can'], color=self.COLORS['gray']))  # ✅ CORRIGÉ
        btn_delete.setIconSize(QSize(16, 16))
        btn_delete.setToolTip("Supprimer")
        btn_delete.setStyleSheet(btn_style % self.COLORS['danger_light'])
        btn_delete.clicked.connect(lambda: self.delete_contact(item))
        
        layout.addWidget(btn_view)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_note)
        layout.addWidget(btn_delete)
        
        return container


    def load_contacts(self):
        """Charge les contacts (souscripteurs + chauffeurs)"""
        try:
            self.set_status("Chargement...", "info")
            
            from core.workers.query_cache import query_cache
            query_cache.invalidate('all_contacts_drivers')
            query_cache.invalidate('contacts_all')
            
            self.all_contacts = self.controller.contacts.get_all_contacts_with_drivers(force_refresh=True)
            self.filtered_contacts = self.all_contacts.copy()
            
            self.display_contacts()
            self.update_statistics()
            self.update_last_update_time()

            # APPLIQUER LE FILTRE APRÈS LE CHARGEMENT
            self.apply_filters()  # ou self.on_filter_changed()
            
            count = len(self.all_contacts)
            self.set_status(f"{count} contact(s) chargé(s)", "success")
            
        except Exception as e:
            self.set_status(f"Erreur: {str(e)}", "error")
            logger.error(f"Erreur chargement contacts: {e}")
            import traceback
            traceback.print_exc()

    def display_contacts(self):
        """Affiche les contacts"""
        self.table.setRowCount(0)
        count = len(self.filtered_contacts)
        self.total_rows_label.setText(f"{count} contact(s)")
        
        for row, item in enumerate(self.filtered_contacts):
            try:
                self.table.insertRow(row)
                
                # ✅ ID
                id_value = getattr(item, 'id', None) or getattr(item, 'data', None)
                if hasattr(id_value, 'id'):
                    id_value = id_value.id
                id_item = QTableWidgetItem(str(id_value or '—'))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 0, id_item)
                
                # ✅ Contact (avatar + nom)
                contact_widget = QWidget()
                contact_layout = QHBoxLayout(contact_widget)
                contact_layout.setContentsMargins(0, 0, 0, 0)
                contact_layout.setSpacing(12)
                
                avatar = self._create_avatar(item)
                contact_layout.addWidget(avatar)
                
                nom = getattr(item, 'nom', '')
                prenom = getattr(item, 'prenom', '')
                if not nom and hasattr(item, 'data'):
                    data = getattr(item, 'data', None)
                    if data:
                        nom = getattr(data, 'nom', '')
                        prenom = getattr(data, 'prenom', '')
                
                name = f"{nom or ''} {prenom or ''}".strip()
                name_label = QLabel(name or "—")
                name_label.setStyleSheet(f"""
                    font-weight: 600;
                    font-size: 14px;
                    color: {self.COLORS['dark']};
                    background: transparent;
                    border: none;
                """)
                contact_layout.addWidget(name_label)
                contact_layout.addStretch()
                
                self.table.setCellWidget(row, 1, contact_widget)
                
                # ✅ Téléphone
                telephone = getattr(item, 'telephone', '')
                if not telephone and hasattr(item, 'data'):
                    telephone = getattr(item.data, 'telephone', '')
                self.table.setItem(row, 2, QTableWidgetItem(telephone or "—"))
                
                # ✅ Email
                email = getattr(item, 'email', '')
                if not email and hasattr(item, 'data'):
                    email = getattr(item.data, 'email', '')
                self.table.setItem(row, 3, QTableWidgetItem(email or "—"))
                
                # ✅ Type
                display_type = getattr(item, 'display_type', 'Souscripteur')
                if not display_type and hasattr(item, 'data'):
                    display_type = 'Souscripteur'
                type_item = QTableWidgetItem(display_type)
                type_item.setTextAlignment(Qt.AlignCenter)
                type_item.setForeground(self._get_type_color(display_type))
                self.table.setItem(row, 4, type_item)
                
                # ✅ Nature
                nature = getattr(item, 'nature', '')
                if not nature and hasattr(item, 'data'):
                    nature = getattr(item.data, 'nature', '')
                nature_item = QTableWidgetItem(nature or "—")
                nature_item.setTextAlignment(Qt.AlignCenter)
                nature_item.setForeground(self._get_nature_color(nature))
                self.table.setItem(row, 5, nature_item)
                
                # ✅ Statut avec badge
                statut = getattr(item, 'statut', 'Actif')
                if not statut and hasattr(item, 'data'):
                    statut = getattr(item.data, 'statut', 'Actif')
                status_item = QTableWidgetItem(statut)
                status_item.setTextAlignment(Qt.AlignCenter)
                status_item.setForeground(self._get_status_color(statut))
                self.table.setItem(row, 6, status_item)
                
                # ✅ Actions
                actions = self._create_action_buttons(item)
                self.table.setCellWidget(row, 7, actions)
                
                self.table.setRowHeight(row, 62)
                
            except Exception as e:
                print(f"❌ Erreur à la ligne {row}: {e}")
                import traceback
                traceback.print_exc()

    def update_statistics(self):
        """Met à jour les statistiques"""
        total = len(self.filtered_contacts)
        
        souscripteurs = len([e for e in self.filtered_contacts if getattr(e, 'display_type', '') == "Souscripteur" or getattr(e, 'source', '') == 'contact'])
        chauffeurs = len([e for e in self.filtered_contacts if getattr(e, 'display_type', '') == "Chauffeur" or getattr(e, 'source', '') == 'driver'])
        actifs = len([e for e in self.filtered_contacts if getattr(e, 'statut', 'Actif') == "Actif"])
        
        self._update_stat_card("total", str(total))
        self._update_stat_card("souscripteurs", str(souscripteurs))
        self._update_stat_card("chauffeurs", str(chauffeurs))
        self._update_stat_card("actifs", str(actifs))
        
        self._update_counter("total", str(total))
        self._update_counter("actifs", str(actifs))

    def _update_stat_card(self, key, value):
        """Met à jour une carte statistique"""
        card = self.stats_cards.get(key)
        if card:
            for label in card.findChildren(QLabel):
                if label.objectName().startswith("stat_"):
                    label.setText(value)
                    break
    
    def _update_counter(self, key, value):
        """Met à jour un compteur"""
        for label in self.findChildren(QLabel):
            if label.objectName() == f"counter_{key}":
                label.setText(value)
                break
    
    def on_selection_changed(self):
        """Gère la sélection"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        self.selected_contacts = []
        for row in selected_rows:
            if row < len(self.filtered_contacts):
                self.selected_contacts.append(self.filtered_contacts[row])
        
        count = len(self.selected_contacts)
        self.btn_edit.setEnabled(count == 1)
        self.btn_delete.setEnabled(count > 0)
        self.btn_duplicate.setEnabled(count == 1)
        
        self.selection_label.setText(f"{count} sélectionné(s)" if count > 0 else "")
        
        # Mise à jour du compteur de sélection dans le footer
        if count > 0:
            self.selection_count_label.setText(f"• {count} sélectionné{'s' if count > 1 else ''}")
        else:
            self.selection_count_label.setText("")
        
        if count == 1:
            self.contact_selected.emit(self.selected_contacts[0])
    
    def on_item_double_clicked(self, item):
        """Double-clic pour voir les détails"""
        row = item.row()
        if row < len(self.filtered_contacts):
            self.view_contact(self.filtered_contacts[row])
    
    def on_search(self):
        """Recherche"""
        self.apply_filters()
    
    def on_filter_changed(self):
        """Filtre"""
        self.apply_filters()
   
    def apply_filters(self):
        """Applique les filtres"""
        search_text = self.search_input.text().strip().lower()
        filter_text = self.filter_combo.currentText()
        
        filtered = self.all_contacts.copy()
        
        if search_text:
            filtered = [e for e in filtered if self._matches_search(e, search_text)]
        
        if filter_text != "Tous":
            if filter_text == "Souscripteur":
                filtered = [e for e in filtered if getattr(e, 'display_type', '') == "Souscripteur" or getattr(e, 'source', '') == 'contact']
            elif filter_text == "Chauffeur":
                filtered = [e for e in filtered if getattr(e, 'display_type', '') == "Chauffeur" or getattr(e, 'source', '') == 'driver']
            elif filter_text in ["Particulier", "Société"]:
                filtered = [e for e in filtered if getattr(e, 'nature', '') == filter_text]
        
        self.filtered_contacts = filtered
        self.display_contacts()
        self.update_statistics()
        self.set_status(f"{len(filtered)} contact(s) trouvé(s)", "info")

    def _matches_search(self, entry, search_text):
        """Vérifie si l'entrée correspond à la recherche"""
        nom = getattr(entry, 'nom', '') or ''
        prenom = getattr(entry, 'prenom', '') or ''
        telephone = getattr(entry, 'telephone', '') or ''
        email = getattr(entry, 'email', '') or ''
        type_client = getattr(entry, 'type_client', '') or ''
        nature = getattr(entry, 'nature', '') or ''
        code_client = getattr(entry, 'code_client', '') or ''
        code_chauffeur = getattr(entry, 'code_chauffeur', '') or ''
        display_type = getattr(entry, 'display_type', '') or ''
        specialite = getattr(entry, 'specialite', '') or ''
        
        search_lower = search_text.lower()
        
        return any([
            search_lower in nom.lower(),
            search_lower in prenom.lower(),
            search_lower in telephone.lower(),
            search_lower in email.lower(),
            search_lower in type_client.lower(),
            search_lower in nature.lower(),
            search_lower in code_client.lower(),
            search_lower in code_chauffeur.lower(),
            search_lower in display_type.lower(),
            search_lower in specialite.lower()
        ])

    # ============================================================
    # CRUD
    # ============================================================
    
    def on_add_contact(self):
        """Ajoute un contact"""
        dialog = ContactForm(self.controller, parent=self)
        if dialog.exec_():
            data = dialog._get_data()
            contact, success, message = self.controller.contacts.create_contact(data)
            if success:
                self.load_contacts()
                self.set_status("Contact ajouté avec succès", "success")
            else:
                self.set_status(f"Erreur: {message}", "error")
    
    def on_edit_contact(self):
        """Modifie un contact"""
        if len(self.selected_contacts) == 1:
            self.edit_contact(self.selected_contacts[0])
    
    def edit_contact(self, contact):
        """Modifie un contact"""
        fresh_contact = self.controller.contacts.get_contact_by_id(contact.id)
        if fresh_contact:
            dialog = ContactForm(self.controller, fresh_contact, parent=self, mode="edit")
            if dialog.exec_():
                self.load_contacts()
                self.contact_updated.emit()
                self.set_status("Contact modifié avec succès", "success")
    
    def view_contact(self, contact):
        """Voir les détails d'un contact"""
        from addons.Automobiles.views.contact_detail_view import ContactDetailView
        dialog = ContactDetailView(self.controller, contact, self)
        dialog.contact_updated.connect(self.load_contacts)
        dialog.exec_()
    
    def delete_contact(self, contact):
        """Supprime un contact"""
        name = f"{contact.nom} {contact.prenom or ''}".strip()
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirmation")
        msg.setText(f"Supprimer le contact '{name}' ?")
        msg.setInformativeText("Cette action est irréversible.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        if msg.exec() == QMessageBox.Yes:
            if self.controller.contacts.delete_contact(contact.id):
                self.load_contacts()
                self.set_status("Contact supprimé", "success")
    
    def on_delete_contact(self):
        """Supprime plusieurs contacts"""
        if not self.selected_contacts:
            return
        
        count = len(self.selected_contacts)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirmation")
        
        if count == 1:
            contact = self.selected_contacts[0]
            name = f"{contact.nom} {contact.prenom or ''}".strip()
            msg.setText(f"Supprimer le contact '{name}' ?")
        else:
            msg.setText(f"Supprimer {count} contacts ?")
        
        msg.setInformativeText("Cette action est irréversible.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        if msg.exec() == QMessageBox.Yes:
            success_count = 0
            for contact in self.selected_contacts:
                if self.controller.contacts.delete_contact(contact.id):
                    success_count += 1
            
            self.load_contacts()
            self.set_status(f"{success_count} contact(s) supprimé(s)", "success")
    
    def duplicate_contact(self):
        """Duplique un contact"""
        if len(self.selected_contacts) == 1:
            contact = self.selected_contacts[0]
            new_data = {
                'nom': contact.nom + " (Copie)" if contact.nom else "Copie",
                'prenom': contact.prenom,
                'telephone': contact.telephone,
                'email': contact.email,
                'type_client': contact.type_client,
                'nature': contact.nature,
                'statut': contact.statut,
                'code_client': contact.code_client + "_COPY" if contact.code_client else None,
                'code_chauffeur': contact.code_chauffeur + "_COPY" if contact.code_chauffeur else None
            }
            contact, success, message = self.controller.contacts.create_contact(new_data)
            if success:
                self.load_contacts()
                self.set_status("Contact dupliqué avec succès", "success")
    
    def import_contacts(self):
        """Importe des contacts"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Importer des contacts",
            "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
        )
        if path:
            try:
                count = self.controller.contacts.import_from_file(path)
                self.load_contacts()
                self.set_status(f"{count} contact(s) importé(s)", "success")
            except Exception as e:
                self.set_status(f"Erreur d'import: {str(e)}", "error")
    
    def add_quick_note(self, contact):
        """Ajoute une note rapide"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📝 Note - {contact.nom}")
        dialog.resize(450, 250)
        dialog.setStyleSheet(f"""
            QDialog {{
                background: {self.COLORS['white']};
                border-radius: 16px;
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)
        
        info = QLabel(f"Contact: {contact.nom} {contact.prenom or ''}")
        info.setStyleSheet(f"""
            font-weight: 600;
            font-size: 14px;
            color: {self.COLORS['dark']};
            background: transparent;
            border: none;
        """)
        layout.addWidget(info)
        
        note_input = QTextEdit()
        note_input.setPlaceholderText("Écrivez votre note ici...")
        note_input.setStyleSheet(f"""
            QTextEdit {{
                border: 2px solid {self.COLORS['border']};
                border-radius: 12px;
                padding: 12px;
                font-size: 13px;
                background: {self.COLORS['gray_light']};
            }}
            QTextEdit:focus {{
                border-color: {self.COLORS['primary']};
                background: {self.COLORS['white']};
            }}
        """)
        layout.addWidget(note_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: {self.COLORS['gray_light']};
                color: {self.COLORS['dark']};
                border: 1px solid {self.COLORS['border']};
                border-radius: 10px;
                padding: 10px 24px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {self.COLORS['border']};
            }}
        """)
        btn_cancel.clicked.connect(dialog.reject)
        
        btn_save = QPushButton()
        btn_save.setIcon(qta.icon(self.ICONS['floppy_disk'], color='white'))
        btn_save.setIconSize(QSize(16, 16))
        btn_save.setText("  Enregistrer")
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {self.COLORS['primary']};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 24px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {self._darken_color(self.COLORS['primary'], 0.1)};
            }}
        """)
        
        def on_save():
            note = note_input.toPlainText().strip()
            if note:
                self.controller.contacts.log_contact_action(
                    action="NOTE_ADDED",
                    contact_id=contact.id,
                    details=note
                )
                self.set_status("Note ajoutée avec succès", "success")
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Attention", "Veuillez écrire une note.")
        
        btn_save.clicked.connect(on_save)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    # ============================================================
    # EXPORTS
    # ============================================================
    
    def export_to_csv(self):
        """Exporte en CSV"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les contacts",
            f"contacts_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        if path:
            try:
                import csv
                with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Nom", "Prénom", "Téléphone", "Email", "Type", "Nature", "Statut"])
                    for c in self.filtered_contacts:
                        writer.writerow([
                            c.id, c.nom or "", c.prenom or "", c.telephone or "",
                            c.email or "", c.type_client or "", c.nature or "", c.statut or "Actif"
                        ])
                self.set_status("Export CSV réussi", "success")
            except Exception as e:
                self.set_status(f"Erreur export: {str(e)}", "error")
    
    def export_to_pdf(self):
        """Exporte en PDF"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter en PDF",
            f"contacts_{datetime.now().strftime('%Y%m%d')}.pdf",
            "PDF Files (*.pdf)"
        )
        if path:
            try:
                contacts_data = [{
                    'id': c.id, 'nom': c.nom, 'prenom': c.prenom,
                    'telephone': c.telephone, 'email': c.email,
                    'type': c.type_client, 'nature': c.nature, 'statut': c.statut
                } for c in self.filtered_contacts]
                
                stats = {
                    'total': len(contacts_data),
                    'souscripteurs': len([c for c in contacts_data if c['type'] == "Souscripteur"]),
                    'chauffeurs': len([c for c in contacts_data if c['type'] == "Chauffeur"]),
                    'actifs': len([c for c in contacts_data if c['statut'] == "Actif"])
                }
                
                generate_contact_pdf(path, contacts_data, stats)
                self.set_status("Export PDF réussi", "success")
            except Exception as e:
                self.set_status(f"Erreur export: {str(e)}", "error")
    
    def show_audit_logs(self):
        """Affiche les logs d'audit"""
        try:
            logs = self.controller.contacts.get_audit_logs()
            if not logs:
                QMessageBox.information(self, "Audit", "Aucun historique disponible")
                return
            
            dialog = QDialog(self)
            dialog.setWindowTitle("📜 Journal d'audit")
            dialog.resize(1000, 600)
            dialog.setStyleSheet(f"""
                QDialog {{
                    background: {self.COLORS['white']};
                }}
            """)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(16)
            layout.setContentsMargins(24, 24, 24, 24)
            
            title_widget = QWidget()
            title_layout = QHBoxLayout(title_widget)
            title_layout.setContentsMargins(0, 0, 0, 0)
            title_layout.setSpacing(12)
            
            icon_label = QLabel()
            icon_label.setPixmap(qta.icon(self.ICONS['clipboard_list'], color=self.COLORS['primary']).pixmap(28, 28))
            title_layout.addWidget(icon_label)
            
            title = QLabel("Journal d'audit")
            title.setStyleSheet(f"""
                font-size: 20px;
                font-weight: 700;
                color: {self.COLORS['dark']};
                background: transparent;
                border: none;
            """)
            title_layout.addWidget(title)
            title_layout.addStretch()
            layout.addWidget(title_widget)
            
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Date", "Action", "Utilisateur", "Détails"])
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setShowGrid(False)
            table.verticalHeader().setVisible(False)
            table.setStyleSheet(f"""
                QTableWidget {{
                    border: 1px solid {self.COLORS['border']};
                    border-radius: 12px;
                }}
                QHeaderView::section {{
                    background: {self.COLORS['gray_light']};
                    padding: 12px 16px;
                    font-weight: 600;
                    color: {self.COLORS['gray']};
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    font-size: 11px;
                }}
                QTableWidget::item {{
                    padding: 12px 16px;
                }}
            """)
            
            table.setRowCount(len(logs))
            for i, log in enumerate(logs):
                date_str = log.created_at.strftime("%d/%m/%Y %H:%M:%S") if log.created_at else "—"
                table.setItem(i, 0, QTableWidgetItem(date_str))
                table.setItem(i, 1, QTableWidgetItem(log.action or "—"))
                table.setItem(i, 2, QTableWidgetItem(f"ID: {log.user_id or '?'}"))
                table.setItem(i, 3, QTableWidgetItem(log.details or "—"))
            
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
            table.setColumnWidth(0, 170)
            table.setColumnWidth(1, 140)
            table.setColumnWidth(2, 100)
            
            layout.addWidget(table)
            
            btn_close = QPushButton("Fermer")
            btn_close.setStyleSheet(f"""
                QPushButton {{
                    background: {self.COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 12px;
                    font-weight: 600;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background: {self._darken_color(self.COLORS['primary'], 0.1)};
                }}
            """)
            btn_close.clicked.connect(dialog.accept)
            layout.addWidget(btn_close)
            
            dialog.exec_()
        except Exception as e:
            self.set_status(f"Erreur: {str(e)}", "error")
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        menu = QMenu()
        menu.setStyleSheet(f"""
            QMenu {{
                background: {self.COLORS['white']};
                border: 1px solid {self.COLORS['border']};
                border-radius: 12px;
                padding: 6px;
                min-width: 180px;
            }}
            QMenu::item {{
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
                color: {self.COLORS['dark']};
            }}
            QMenu::item:selected {{
                background: {self.COLORS['primary_light']};
                color: {self.COLORS['primary']};
            }}
            QMenu::separator {{
                height: 1px;
                background: {self.COLORS['border']};
                margin: 4px 12px;
            }}
        """)
        
        item = self.table.itemAt(position)
        if not item:
            return
        
        row = item.row()
        if row >= len(self.filtered_contacts):
            return
        
        contact = self.filtered_contacts[row]
        
        view_action = QAction(qta.icon(self.ICONS['eye'], color=self.COLORS['gray']), "Voir les détails", self)
        view_action.triggered.connect(lambda: self.view_contact(contact))
        
        edit_action = QAction(qta.icon('pen', color=self.COLORS['gray']), "Modifier", self)
        edit_action.triggered.connect(lambda: self.edit_contact(contact))
        
        note_action = QAction(qta.icon(self.COLORS['note_sticky'], color=self.COLORS['gray']), "Ajouter une note", self)
        note_action.triggered.connect(lambda: self.add_quick_note(contact))
        
        duplicate_action = QAction(qta.icon('copy', color=self.COLORS['gray']), "Dupliquer", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_single_contact(contact))
        
        delete_action = QAction(qta.icon('trash_can', color=self.COLORS['danger']), "Supprimer", self)
        delete_action.triggered.connect(lambda: self.delete_contact(contact))
        
        menu.addAction(view_action)
        menu.addAction(edit_action)
        menu.addSeparator()
        menu.addAction(note_action)
        menu.addAction(duplicate_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        
        menu.exec_(self.table.viewport().mapToGlobal(position))
    
    def duplicate_single_contact(self, contact):
        """Duplique un contact spécifique"""
        new_data = {
            'nom': contact.nom + " (Copie)" if contact.nom else "Copie",
            'prenom': contact.prenom,
            'telephone': contact.telephone,
            'email': contact.email,
            'type_client': contact.type_client,
            'nature': contact.nature,
            'statut': contact.statut
        }
        contact, success, message = self.controller.contacts.create_contact(new_data)
        if success:
            self.load_contacts()
            self.set_status("Contact dupliqué avec succès", "success")
    
    # ============================================================
    # UTILITAIRES
    # ============================================================
    
    def _get_type_color(self, contact_type):
        """Couleur selon le type de client"""
        colors = {
            "Souscripteur": QColor(self.COLORS['success']),
            "Chauffeur": QColor(self.COLORS['orange']),
            "Assuré": QColor(self.COLORS['success']),
            "Prospect": QColor(self.COLORS['orange']),
            "Partenaire": QColor(self.COLORS['purple']),
            "Fournisseur": QColor(self.COLORS['teal'])
        }
        return colors.get(contact_type, QColor(self.COLORS['gray']))
    
    def _get_nature_color(self, nature):
        """Couleur selon la nature"""
        colors = {
            "Particulier": QColor(self.COLORS['primary']),
            "Société": QColor(self.COLORS['purple']),
            "Personne Physique": QColor(self.COLORS['primary']),
            "Personne Morale": QColor(self.COLORS['purple'])
        }
        return colors.get(nature, QColor(self.COLORS['gray']))
    
    def _get_status_color(self, status):
        """Couleur selon le statut"""
        colors = {
            "Actif": QColor(self.COLORS['success']),
            "Inactif": QColor(self.COLORS['danger']),
            "En attente": QColor(self.COLORS['warning']),
            "Suspendu": QColor(self.COLORS['warning'])
        }
        return colors.get(status, QColor(self.COLORS['gray']))
    
    # def set_status(self, message, msg_type="info"):
    #     """Définit le message de statut"""
    #     icons = {
    #         "success": qta.icon(self.ICONS['circle_check'], color=self.COLORS['success']),
    #         "error": qta.icon('circle_xmark', color=self.COLORS['danger']),
    #         "info": qta.icon('circle_info', color=self.COLORS['primary']),
    #         "warning": qta.icon('triangle-exclamation', color=self.COLORS['warning'])
    #     }
    #     colors = {
    #         "success": self.COLORS['success'],
    #         "error": self.COLORS['danger'],
    #         "info": self.COLORS['primary'],
    #         "warning": self.COLORS['warning']
    #     }
        
    #     # Mettre à jour l'icône de statut
    #     status_indicator = self.status_label.parent().findChildren(QLabel)[0] if self.status_label.parent() else None
    #     if status_indicator and msg_type in icons:
    #         status_indicator.setPixmap(icons[msg_type].pixmap(16, 16))
        
    #     self.status_label.setText(message)
    #     self.status_label.setStyleSheet(f"""
    #         color: {colors.get(msg_type, self.COLORS['gray'])};
    #         font-size: 13px;
    #         font-weight: 500;
    #         background: transparent;
    #         border: none;
    #     """)
        
    #     if msg_type != "error":
    #         QTimer.singleShot(3000, self._reset_status)

    def set_status(self, message, msg_type="info"):
        """Définit le message de statut"""
        icons = {
            "success": qta.icon(self.ICONS['circle_check'], color=self.COLORS['success']),
            "error": qta.icon(self.ICONS['circle_xmark'], color=self.COLORS['danger']),
            "info": qta.icon(self.ICONS['circle_info'], color=self.COLORS['primary']),
            "warning": qta.icon(self.ICONS['triangle_exclamation'], color=self.COLORS['warning'])
        }
        colors = {
            "success": self.COLORS['success'],
            "error": self.COLORS['danger'],
            "info": self.COLORS['primary'],
            "warning": self.COLORS['warning']
        }
        
        # Mettre à jour l'icône de statut
        status_indicator = self.status_label.parent().findChildren(QLabel)[0] if self.status_label.parent() else None
        if status_indicator and msg_type in icons:
            status_indicator.setPixmap(icons[msg_type].pixmap(16, 16))
        
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            color: {colors.get(msg_type, self.COLORS['gray'])};
            font-size: 13px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        
        if msg_type != "error":
            QTimer.singleShot(3000, self._reset_status)

    def _reset_status(self):
        """Réinitialise le statut"""
        status_indicator = self.status_label.parent().findChildren(QLabel)[0] if self.status_label.parent() else None
        if status_indicator:
            status_indicator.setPixmap(qta.icon(self.ICONS['circle_check'], color=self.COLORS['success']).pixmap(16, 16))
        
        self.status_label.setText("Prêt")
        self.status_label.setStyleSheet(f"""
            color: {self.COLORS['success']};
            font-size: 13px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
    
    def update_last_update_time(self):
        """Met à jour l'heure de dernière mise à jour"""
        self.last_update_label.setText(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
    
    def apply_security_policy(self):
        """Applique la politique de sécurité"""
        if hasattr(self.current_user, 'role'):
            role = self.current_user.role
            if not SecurityManager.has_permission(role, Permissions.CONTACT_ADD):
                self.btn_add.setVisible(False)
            if not SecurityManager.has_permission(role, Permissions.CONTACT_EDIT):
                self.btn_edit.setVisible(False)
            if not SecurityManager.has_permission(role, Permissions.CONTACT_DELETE):
                self.btn_delete.setVisible(False)
            if not SecurityManager.has_permission(role, Permissions.AUDIT_VIEW):
                self.btn_audit.setVisible(False)
    
    def refresh(self):
        """Rafraîchit la vue"""
        self.load_contacts()

    def get_driver_by_id(self, driver_id):
        """Récupère un chauffeur par son ID"""
        try:
            from addons.Automobiles.models.driver_models import Driver
            return self.db.query(Driver).filter(Driver.id == driver_id).first()
        except Exception as e:
            print(f"Erreur get_driver_by_id: {e}")
            return None

    def delete_driver(self, driver_id):
        """Supprime un chauffeur"""
        try:
            from addons.Automobiles.models.driver_models import Driver
            driver = self.db.query(Driver).filter(Driver.id == driver_id).first()
            if driver:
                self.db.delete(driver)
                self.db.commit()
                return True
            return False
        except Exception as e:
            print(f"Erreur delete_driver: {e}")
            self.db.rollback()
            return False
    
    def setup_shortcuts(self):
        """Configure les raccourcis clavier"""
        shortcuts = [
            ("Ctrl+N", self.on_add_contact),
            ("Ctrl+E", self.on_edit_contact),
            ("Delete", self.on_delete_contact),
            ("Ctrl+R", self.load_contacts),
            ("Ctrl+F", lambda: self.search_input.setFocus()),
            ("Ctrl+D", self.duplicate_contact),
        ]
        for key, callback in shortcuts:
            action = QAction(self)
            action.setShortcut(key)
            action.triggered.connect(callback)
            self.addAction(action)


        