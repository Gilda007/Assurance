# """
# Page Audit global - Consultation de tous les logs
# """
# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
#     QHeaderView, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox,
#     QDateEdit, QFrame
# )
# from PySide6.QtCore import Qt, QDate
# from PySide6.QtGui import QColor


# class AuditPage(QWidget):
#     """Page de consultation de tous les logs d'audit"""
    
#     def __init__(self, audit_controller, user, parent=None):
#         super().__init__(parent)
#         self.controller = audit_controller
#         self.user = user
#         self.setup_ui()
#         self.load_data()
    
#     def setup_ui(self):
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(25, 25, 25, 25)
#         layout.setSpacing(15)
        
#         header = QLabel("📜 Journal d'Audit Global")
#         header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
#         layout.addWidget(header)
        
#         # Filtres
#         filters = QFrame()
#         filters.setStyleSheet("background-color: #f8fafc; border-radius: 8px; padding: 10px;")
#         f_layout = QHBoxLayout(filters)
#         f_layout.setSpacing(10)
        
#         f_layout.addWidget(QLabel("Utilisateur:"))
#         self.filter_user = QLineEdit()
#         self.filter_user.setPlaceholderText("ID utilisateur")
#         self.filter_user.setFixedWidth(100)
#         f_layout.addWidget(self.filter_user)
        
#         f_layout.addWidget(QLabel("Action:"))
#         self.filter_action = QComboBox()
#         self.filter_action.addItem("Toutes", None)
#         for a in ['CREATION', 'MODIFICATION', 'VALIDATION', 'SUPPRESSION', 
#                   'CHANGEMENT_STATUT', 'PAIEMENT', 'ENCAISSEMENT']:
#             self.filter_action.addItem(a, a)
#         f_layout.addWidget(self.filter_action)
        
#         f_layout.addWidget(QLabel("Entité:"))
#         self.filter_entite = QComboBox()
#         self.filter_entite.addItem("Toutes", None)
#         for e in ['Sinistre', 'Expertise', 'Evaluation', 'Reglement', 'Recours']:
#             self.filter_entite.addItem(e, e)
#         f_layout.addWidget(self.filter_entite)
        
#         f_layout.addStretch()
        
#         self.btn_search = QPushButton("🔍 Rechercher")
#         self.btn_search.setStyleSheet("""
#             QPushButton {
#                 background-color: #1a73e8; color: white;
#                 padding: 8px 20px; border-radius: 8px; font-weight: bold;
#             }
#             QPushButton:hover { background-color: #1557b0; }
#         """)
#         self.btn_search.clicked.connect(self.load_data)
#         f_layout.addWidget(self.btn_search)
        
#         layout.addWidget(filters)
        
#         # Tableau
#         self.table = QTableWidget()
#         self.table.setColumnCount(7)
#         self.table.setHorizontalHeaderLabels([
#             "Date", "Utilisateur", "Action", "Entité", "ID", "Champ", "Ancien → Nouveau"
#         ])
#         self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#         self.table.setAlternatingRowColors(True)
#         self.table.setStyleSheet("""
#             QTableWidget {
#                 border: 1px solid #e2e8f0;
#                 border-radius: 8px;
#                 gridline-color: #f1f5f9;
#             }
#             QTableWidget::item { padding: 8px; }
#             QHeaderView::section {
#                 background-color: #f8fafc;
#                 padding: 8px;
#                 font-weight: bold;
#                 border: none;
#                 border-bottom: 1px solid #e2e8f0;
#             }
#         """)
#         layout.addWidget(self.table)
        
#         # Info total
#         self.lbl_total = QLabel("Total: 0 entrées")
#         self.lbl_total.setStyleSheet("color: #64748b; font-size: 12px;")
#         layout.addWidget(self.lbl_total)
    
#     def load_data(self):
#         """Charge les logs"""
#         try:
#             logs = []
#             if hasattr(self.controller, 'get_logs'):
#                 logs = self.controller.get_logs(
#                     utilisateur_id=int(self.filter_user.text()) if self.filter_user.text().isdigit() else None,
#                     action=self.filter_action.currentData(),
#                     entite=self.filter_entite.currentData(),
#                     limit=500,
#                 ) or []
            
#             self.table.setRowCount(len(logs))
            
#             action_colors = {
#                 'CREATION': '#22c55e',
#                 'MODIFICATION': '#3b82f6',
#                 'VALIDATION': '#06b6d4',
#                 'SUPPRESSION': '#ef4444',
#                 'CHANGEMENT_STATUT': '#8b5cf6',
#                 'PAIEMENT': '#f59e0b',
#                 'ENCAISSEMENT': '#10b981',
#             }
            
#             for i, log in enumerate(logs):
#                 date = str(log.get('date_action', ''))[:19].replace('T', ' ')
#                 self.table.setItem(i, 0, QTableWidgetItem(date))
#                 self.table.setItem(i, 1, QTableWidgetItem(log.get('utilisateur_nom', '')))
                
#                 action = log.get('action', '')
#                 action_item = QTableWidgetItem(action)
#                 color = action_colors.get(action, '#64748b')
#                 action_item.setForeground(QColor(color))
#                 self.table.setItem(i, 2, action_item)
                
#                 self.table.setItem(i, 3, QTableWidgetItem(log.get('entite', '')))
#                 self.table.setItem(i, 4, QTableWidgetItem(str(log.get('entite_id', ''))))
#                 self.table.setItem(i, 5, QTableWidgetItem(log.get('champ_modifie', '') or ''))
                
#                 ancien = log.get('ancienne_valeur', '') or ''
#                 nouveau = log.get('nouvelle_valeur', '') or ''
#                 self.table.setItem(i, 6, QTableWidgetItem(f"{ancien} → {nouveau}" if ancien or nouveau else '—'))
            
#             self.lbl_total.setText(f"Total: {len(logs)} entrées")
#         except Exception as e:
#             print(f"Erreur chargement logs: {e}")
    
#     def refresh(self):
#         self.load_data()




"""
Page Audit global - Consultation de tous les logs
Design moderne avec icônes FontAwesome
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox,
    QDateEdit, QFrame, QMenu, QSizePolicy, QAbstractItemView,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QColor, QFont, QAction

import qtawesome as qta

from datetime import datetime


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
        
        # Icône FontAwesome
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


# ═══════════════════════════════════════════════════════════════════
# PAGE AUDIT
# ═══════════════════════════════════════════════════════════════════

class AuditPage(QWidget):
    """Page de consultation de tous les logs d'audit — Design moderne"""
    
    def __init__(self, audit_controller, user, parent=None):
        super().__init__(parent)
        self.controller = audit_controller
        self.user = user
        
        # État
        self._current_page = 1
        self._per_page = 50
        self._total_logs = 0
        self._all_logs = []
        
        self.setup_ui()
        self.load_data()
    
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
        layout.addWidget(self._build_filters())
        layout.addWidget(self._build_table_card(), 1)
    
    def _build_header(self):
        """En-tête avec titre et icône"""
        frame = QFrame()
        frame.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Icône FontAwesome
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
        icon_lbl.setPixmap(qta.icon('fa5s.history', color='#2563eb').pixmap(QSize(24, 24)))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_lbl)
        
        layout.addWidget(icon_container)
        
        # Titre + sous-titre
        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        
        title = QLabel("Journal d'Audit Global")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
            background: transparent;
        """)
        title_block.addWidget(title)
        
        subtitle = QLabel("Historique complet des actions sur le système")
        subtitle.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        title_block.addWidget(subtitle)
        
        layout.addLayout(title_block)
        layout.addStretch()
        
        # Bouton refresh
        self.btn_refresh = QPushButton()
        self.btn_refresh.setFixedSize(38, 38)
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
        
        return frame
    
    def _build_stats_row(self):
        """Rangée de 4 cartes statistiques"""
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        
        self.card_total = StatCard(
            icon_name="fa5s.list", 
            title="Total entrées", value="0",
            color_bg="#dbeafe", color_fg="#1e40af"
        )
        self.card_creations = StatCard(
            icon_name="fa5s.plus-circle", 
            title="Créations", value="0",
            color_bg="#d1fae5", color_fg="#059669"
        )
        self.card_modifications = StatCard(
            icon_name="fa5s.edit", 
            title="Modifications", value="0",
            color_bg="#fef3c7", color_fg="#92400e"
        )
        self.card_suppressions = StatCard(
            icon_name="fa5s.trash-alt", 
            title="Suppressions", value="0",
            color_bg="#fee2e2", color_fg="#991b1b"
        )
        
        layout.addWidget(self.card_total)
        layout.addWidget(self.card_creations)
        layout.addWidget(self.card_modifications)
        layout.addWidget(self.card_suppressions)
        
        return wrapper
    
    def _build_filters(self):
        """Barre de filtres"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)
        
        def make_filter(label_text: str, icon_name: str, icon_color: str):
            box = QVBoxLayout()
            box.setSpacing(4)
            
            header = QHBoxLayout()
            header.setSpacing(6)
            
            icon_lbl = QLabel()
            icon_lbl.setPixmap(qta.icon(icon_name, color=icon_color).pixmap(QSize(11, 11)))
            icon_lbl.setFixedSize(13, 13)
            icon_lbl.setStyleSheet("background: transparent;")
            header.addWidget(icon_lbl)
            
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; background: transparent;")
            header.addWidget(lbl)
            header.addStretch()
            
            box.addLayout(header)
            return box
        
        # Filtre utilisateur
        user_box = make_filter("Utilisateur", "fa5s.user", "#8b5cf6")
        self.filter_user = QLineEdit()
        self.filter_user.setPlaceholderText("ID utilisateur")
        self.filter_user.setFixedWidth(100)
        self.filter_user.setStyleSheet("""
            QLineEdit {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #1e293b;
            }
            QLineEdit:focus { border-color: #3b82f6; background: white; }
        """)
        user_box.addWidget(self.filter_user)
        layout.addLayout(user_box)
        
        # Filtre action
        action_box = make_filter("Action", "fa5s.bolt", "#f59e0b")
        self.filter_action = QComboBox()
        self.filter_action.addItem("Toutes les actions", None)
        for a, label in [
            ('CREATION', 'Création'),
            ('MODIFICATION', 'Modification'),
            ('VALIDATION', 'Validation'),
            ('SUPPRESSION', 'Suppression'),
            ('CHANGEMENT_STATUT', 'Changement statut'),
            ('PAIEMENT', 'Paiement'),
            ('ENCAISSEMENT', 'Encaissement'),
        ]:
            self.filter_action.addItem(label, a)
        self.filter_action.setStyleSheet(self._combo_style())
        action_box.addWidget(self.filter_action)
        layout.addLayout(action_box)
        
        # Filtre entité
        entite_box = make_filter("Entité", "fa5s.cube", "#06b6d4")
        self.filter_entite = QComboBox()
        self.filter_entite.addItem("Toutes les entités", None)
        for e, label in [
            ('Sinistre', 'Sinistre'),
            ('Expertise', 'Expertise'),
            ('Evaluation', 'Évaluation'),
            ('Reglement', 'Règlement'),
            ('Recours', 'Recours'),
        ]:
            self.filter_entite.addItem(label, e)
        self.filter_entite.setStyleSheet(self._combo_style())
        entite_box.addWidget(self.filter_entite)
        layout.addLayout(entite_box)
        
        # Filtre période
        periode_box = make_filter("Période", "fa5s.calendar-alt", "#22c55e")
        self.filter_periode = QComboBox()
        self.filter_periode.addItems([
            "Toutes les périodes", "Aujourd'hui", "7 derniers jours",
            "30 derniers jours", "3 derniers mois", "Année en cours"
        ])
        self.filter_periode.setStyleSheet(self._combo_style())
        periode_box.addWidget(self.filter_periode)
        layout.addLayout(periode_box)
        
        layout.addStretch()
        
        # Bouton rechercher
        self.btn_search = QPushButton("  Rechercher")
        self.btn_search.setCursor(Qt.PointingHandCursor)
        self.btn_search.setFixedHeight(36)
        self.btn_search.setIcon(qta.icon('fa5s.search', color='white'))
        self.btn_search.setIconSize(QSize(14, 14))
        self.btn_search.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 700;
                text-align: left;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        self.btn_search.clicked.connect(self.load_data)
        layout.addWidget(self.btn_search)
        
        # Bouton reset
        btn_reset = QPushButton("  Réinitialiser")
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setFixedHeight(36)
        btn_reset.setIcon(qta.icon('fa5s.sync-alt', color='#64748b'))
        btn_reset.setIconSize(QSize(12, 12))
        btn_reset.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                color: #64748b;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background: #f8fafc;
                border-color: #cbd5e1;
                color: #1e293b;
            }
        """)
        btn_reset.clicked.connect(self._reset_filters)
        layout.addWidget(btn_reset)
        
        return frame
    
    def _combo_style(self) -> str:
        return """
            QComboBox {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #1e293b;
                min-width: 140px;
            }
            QComboBox:hover { border-color: #3b82f6; background: white; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #64748b;
                margin-right: 6px;
            }
        """
    
    def _build_table_card(self):
        """Carte contenant le tableau"""
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
        
        # Titre avec icône
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('fa5s.list', color='#2563eb').pixmap(QSize(14, 14)))
        title_row.addWidget(title_icon)
        
        title = QLabel("Journal des Actions")
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
        
        # ✅ Bouton Export avec icône download
        btn_export = QPushButton("  Export CSV")
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
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Date", "Utilisateur", "Action", "Entité",
            "ID", "Champ", "Ancien → Nouveau"
        ])
        
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
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(6, QHeaderView.Stretch)
        
        # ✅ MENU CONTEXTUEL (clic droit)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_table_context_menu)
        
        layout.addWidget(self.table)
        
        # ─── Footer avec total ───
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-top: 1px solid #f1f5f9;
            }
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 12, 20, 12)
        
        # ✅ Icône info
        info_icon = QLabel()
        info_icon.setPixmap(qta.icon('fa5s.info-circle', color='#64748b').pixmap(QSize(12, 12)))
        footer_layout.addWidget(info_icon)
        
        self.lbl_total = QLabel("Total: 0 entrées")
        self.lbl_total.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")
        footer_layout.addWidget(self.lbl_total)
        footer_layout.addStretch()
        
        layout.addWidget(footer)
        
        return card
    
    # ═══════════════════════════════════════════════════════════════
    # CHARGEMENT DES DONNÉES
    # ═══════════════════════════════════════════════════════════════
    
    def load_data(self):
        """Charge les logs"""
        try:
            logs = []
            if hasattr(self.controller, 'get_logs'):
                logs = self.controller.get_logs(
                    utilisateur_id=int(self.filter_user.text()) if self.filter_user.text().isdigit() else None,
                    action=self.filter_action.currentData(),
                    entite=self.filter_entite.currentData(),
                    limit=500,
                ) or []
            
            self._all_logs = logs
            
            # Pagination
            start = (self._current_page - 1) * self._per_page
            end = start + self._per_page
            page_logs = logs[start:end]
            
            # Mise à jour stats
            self._update_stats(logs)
            
            # Remplir le tableau
            self.table.setRowCount(len(page_logs))
            
            action_colors = {
                'CREATION': ('#d1fae5', '#065f46', 'fa5s.plus-circle'),
                'MODIFICATION': ('#dbeafe', '#1e40af', 'fa5s.edit'),
                'VALIDATION': ('#cffafe', '#155e75', 'fa5s.check-circle'),
                'SUPPRESSION': ('#fee2e2', '#991b1b', 'fa5s.trash-alt'),
                'CHANGEMENT_STATUT': ('#ede9fe', '#6d28d9', 'fa5s.exchange-alt'),
                'PAIEMENT': ('#fef3c7', '#92400e', 'fa5s.money-bill-wave'),
                'ENCAISSEMENT': ('#d1fae5', '#065f46', 'fa5s.money-bill-wave'),
                'AFFECTATION': ('#cffafe', '#155e75', 'fa5s.user-plus'),
                'DEMARRAGE': ('#e0e7ff', '#3730a3', 'fa5s.play'),
                'FICHIERS_JOINTS': ('#f3e8ff', '#6b21a8', 'fa5s.paperclip'),
                'REVISION': ('#fce7f3', '#9d174d', 'fa5s.redo'),
            }
            
            for i, log in enumerate(page_logs):
                date = str(log.get('date_action', ''))[:19].replace('T', ' ')
                self.table.setItem(i, 0, QTableWidgetItem(date))
                self.table.setItem(i, 1, QTableWidgetItem(log.get('utilisateur_nom', '')))
                
                action = log.get('action', '')
                # ✅ Badge coloré pour l'action
                bg, fg, _ = action_colors.get(action, ("#e2e8f0", "#475569", "fa5s.circle"))
                action_item = QTableWidgetItem(f"  {action}  ")
                action_item.setBackground(QColor(bg))
                action_item.setForeground(QColor(fg))
                action_item.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
                self.table.setItem(i, 2, action_item)
                
                self.table.setItem(i, 3, QTableWidgetItem(log.get('entite', '')))
                self.table.setItem(i, 4, QTableWidgetItem(str(log.get('entite_id', ''))))
                self.table.setItem(i, 5, QTableWidgetItem(log.get('champ_modifie', '') or ''))
                
                ancien = log.get('ancienne_valeur', '') or ''
                nouveau = log.get('nouvelle_valeur', '') or ''
                self.table.setItem(i, 6, QTableWidgetItem(
                    f"{ancien} → {nouveau}" if ancien or nouveau else '—'
                ))
            
            self.lbl_total.setText(f"Total: {len(logs)} entrées")
            
        except Exception as e:
            print(f"Erreur chargement logs: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_stats(self, logs: list):
        """Met à jour les 4 cartes statistiques"""
        total = len(logs)
        creations = sum(1 for l in logs if l.get('action') == 'CREATION')
        modifications = sum(1 for l in logs if l.get('action') == 'MODIFICATION')
        suppressions = sum(1 for l in logs if l.get('action') == 'SUPPRESSION')
        
        for card, value in [
            (self.card_total, total),
            (self.card_creations, creations),
            (self.card_modifications, modifications),
            (self.card_suppressions, suppressions),
        ]:
            for lbl in card.findChildren(QLabel):
                if lbl.objectName() == "stat_value":
                    lbl.setText(f"{value:,}".replace(",", " "))
    
    def _reset_filters(self):
        """Réinitialise tous les filtres"""
        self.filter_user.clear()
        self.filter_action.setCurrentIndex(0)
        self.filter_entite.setCurrentIndex(0)
        self.filter_periode.setCurrentIndex(0)
        self.load_data()
    
    # ═══════════════════════════════════════════════════════════════
    # MENU CONTEXTUEL
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
    
    def _show_table_context_menu(self, position):
        """Affiche le menu contextuel au clic droit"""
        row = self.table.currentRow()
        if row < 0:
            menu = QMenu(self)
            menu.setStyleSheet(self._menu_style())
            # ✅ Icône refresh
            action_refresh = menu.addAction(
                qta.icon('fa5s.sync-alt', color='#64748b'),
                "  Actualiser"
            )
            action_refresh.triggered.connect(self.load_data)
            menu.exec(self.table.viewport().mapToGlobal(position))
            return
        
        # ✅ Récupérer les données du log
        log_data = None
        if 0 <= row < len(self._all_logs):
            log_data = self._all_logs[row]
        
        if not log_data:
            return
        
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        # ─── Consultation ───
        action_detail = QAction(
            qta.icon('fa5s.eye', color='#64748b'),
            "  Voir les détails", self
        )
        action_detail.triggered.connect(lambda: self._show_log_detail(log_data))
        menu.addAction(action_detail)
        
        # ─── Filtrer par cet utilisateur ───
        user_name = log_data.get('utilisateur_nom', '')
        user_id = log_data.get('utilisateur_id')
        if user_id:
            action_filter_user = QAction(
                qta.icon('fa5s.user', color='#8b5cf6'),
                f"  Filtrer par {user_name}", self
            )
            action_filter_user.triggered.connect(
                lambda: self._filter_by_user(user_id)
            )
            menu.addAction(action_filter_user)
        
        # ─── Filtrer par cette entité ───
        entite = log_data.get('entite', '')
        if entite:
            action_filter_entite = QAction(
                qta.icon('fa5s.cube', color='#06b6d4'),
                f"  Filtrer par {entite}", self
            )
            action_filter_entite.triggered.connect(
                lambda: self._filter_by_entite(entite)
            )
            menu.addAction(action_filter_entite)
        
        menu.addSeparator()
        
        # ─── Copier ───
        submenu = menu.addMenu(
            qta.icon('fa5s.copy', color='#64748b'),
            "  Copier"
        )
        submenu.setStyleSheet(self._menu_style())
        
        act_copy_id = submenu.addAction("ID entité")
        act_copy_id.triggered.connect(
            lambda: self._copy_to_clipboard(str(log_data.get('entite_id', '')))
        )
        
        act_copy_champ = submenu.addAction("Nom du champ")
        act_copy_champ.triggered.connect(
            lambda: self._copy_to_clipboard(log_data.get('champ_modifie', '') or '')
        )
        
        # ─── Export ligne ───
        action_export = QAction(
            qta.icon('fa5s.download', color='#22c55e'),
            "  Exporter cette ligne", self
        )
        action_export.triggered.connect(lambda: self._export_single_log(log_data))
        menu.addAction(action_export)
        
        menu.exec(self.table.viewport().mapToGlobal(position))
    
    # ═══════════════════════════════════════════════════════════════
    # ACTIONS DU MENU CONTEXTUEL
    # ═══════════════════════════════════════════════════════════════
    
    def _show_log_detail(self, log_data: dict):
        """Affiche les détails d'un log"""
        QMessageBox.information(
            self,
            "Détails du log d'audit",
            f"<b>Date :</b> {str(log_data.get('date_action', ''))[:19]}<br>"
            f"<b>Utilisateur :</b> {log_data.get('utilisateur_nom', 'N/A')}<br>"
            f"<b>Action :</b> {log_data.get('action', 'N/A')}<br>"
            f"<b>Entité :</b> {log_data.get('entite', 'N/A')}<br>"
            f"<b>ID :</b> {log_data.get('entite_id', 'N/A')}<br>"
            f"<b>Champ modifié :</b> {log_data.get('champ_modifie', '—') or '—'}<br>"
            f"<b>Ancienne valeur :</b> {log_data.get('ancienne_valeur', '—') or '—'}<br>"
            f"<b>Nouvelle valeur :</b> {log_data.get('nouvelle_valeur', '—') or '—'}"
        )
    
    def _filter_by_user(self, user_id):
        """Filtre les logs par utilisateur"""
        self.filter_user.setText(str(user_id))
        self.load_data()
    
    def _filter_by_entite(self, entite: str):
        """Filtre les logs par entité"""
        for i in range(self.filter_entite.count()):
            if self.filter_entite.itemData(i) == entite:
                self.filter_entite.setCurrentIndex(i)
                break
        self.load_data()
    
    def _copy_to_clipboard(self, text: str):
        """Copie dans le presse-papiers"""
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copié", f"'{text}' copié")
    
    # ═══════════════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════════════
    
    def _export_data(self):
        """Exporte tous les logs filtrés en CSV"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        if not self._all_logs:
            QMessageBox.warning(self, "Export", "Aucune donnée à exporter")
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter le journal d'audit",
            f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv)"
        )
        if not path:
            return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Date", "Utilisateur", "Action", "Entité",
                    "ID", "Champ", "Ancien", "Nouveau"
                ])
                for log in self._all_logs:
                    writer.writerow([
                        str(log.get('date_action', ''))[:19],
                        log.get('utilisateur_nom', ''),
                        log.get('action', ''),
                        log.get('entite', ''),
                        log.get('entite_id', ''),
                        log.get('champ_modifie', '') or '',
                        log.get('ancienne_valeur', '') or '',
                        log.get('nouvelle_valeur', '') or '',
                    ])
            
            QMessageBox.information(
                self, "Export réussi",
                f"{len(self._all_logs)} entrées exportées"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    def _export_single_log(self, log_data: dict):
        """Exporte un seul log en CSV"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter cette entrée",
            f"audit_log_{log_data.get('id', 'unknown')}.csv",
            "CSV (*.csv)"
        )
        if not path:
            return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Champ", "Valeur"])
                for key, value in log_data.items():
                    writer.writerow([key, value])
            
            QMessageBox.information(self, "Export réussi", f"Export vers {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur export: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # REFRESH
    # ═══════════════════════════════════════════════════════════════
    
    def refresh(self):
        """Rafraîchit la page"""
        self.load_data()


