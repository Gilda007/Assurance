

"""
Vue principale du module LOMETA Sinistres
Interface utilisateur complète pour la gestion des sinistres
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QListWidgetItem, QStackedWidget,
    QListWidget, QFrame, QMessageBox, QDialog, QGraphicsDropShadowEffect,
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QTabWidget, QSplitter, QScrollArea,
    QProgressBar, QToolBar, QMenu, QCheckBox, QRadioButton
)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QDate
from PySide6.QtGui import QColor


# ============================================================
# PAGE 1: TABLEAU DE BORD
# ============================================================

class DashboardPage(QWidget):
    """Page du tableau de bord"""
    
    def __init__(self, controller, user):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # En-tête
        header = QLabel("📊 Tableau de bord des sinistres")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)
        
        # Cartes de statistiques
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        self.card_total = self._create_stat_card("Total Sinistres", "0", "#3b82f6")
        self.card_ouverts = self._create_stat_card("Ouverts", "0", "#f59e0b")
        self.card_clotures = self._create_stat_card("Clôturés", "0", "#22c55e")
        self.card_recours = self._create_stat_card("Recours", "0", "#ef4444")
        
        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_ouverts)
        cards_layout.addWidget(self.card_clotures)
        cards_layout.addWidget(self.card_recours)
        layout.addLayout(cards_layout)
        
        # Tableau des sinistres récents
        layout.addWidget(QLabel("📋 Sinistres récents"))
        
        self.table_recent = QTableWidget()
        self.table_recent.setColumnCount(6)
        self.table_recent.setHorizontalHeaderLabels([
            "N° Sinistre", "Client", "Branche", "Date", "Statut", "Montant"
        ])
        self.table_recent.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_recent.setAlternatingRowColors(True)
        self.table_recent.setStyleSheet("""
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
        layout.addWidget(self.table_recent)
        
        self.refresh()
    
    def _create_stat_card(self, title: str, value: str, color: str) -> QFrame:
        """Crée une carte de statistique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        label = QLabel(title)
        label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
        value_label.setObjectName("value")
        layout.addWidget(value_label)
        
        # Stocker la référence pour mise à jour
        card.value_label = value_label
        
        return card
    
    def refresh(self):
        """Rafraîchit le tableau de bord"""
        try:
            stats = self.controller.get_statistiques()
            
            # Mettre à jour les cartes
            self.card_total.value_label.setText(str(stats.get('total', 0)))
            
            par_statut = stats.get('par_statut', {})
            self.card_ouverts.value_label.setText(str(par_statut.get('OUVERT', 0)))
            self.card_clotures.value_label.setText(str(par_statut.get('CLOTURE', 0)))
            
            # Charger les sinistres récents
            sinistres = self.controller.rechercher_sinistres({'limit': 10})
            self.table_recent.setRowCount(len(sinistres))
            
            for i, s in enumerate(sinistres):
                self.table_recent.setItem(i, 0, QTableWidgetItem(s.get('numero_sinistre', '')))
                self.table_recent.setItem(i, 1, QTableWidgetItem(str(s.get('client_id', ''))))
                self.table_recent.setItem(i, 2, QTableWidgetItem(s.get('branche', '')))
                self.table_recent.setItem(i, 3, QTableWidgetItem(s.get('date_survenance', '')[:10] if s.get('date_survenance') else ''))
                
                # Statut avec couleur
                statut_item = QTableWidgetItem(s.get('statut', ''))
                statut_color = {
                    'OUVERT': '#f59e0b',
                    'CLOTURE': '#22c55e',
                    'EN_INSTRUCTION': '#3b82f6',
                    'EN_EXPERTISE': '#8b5cf6',
                    'EN_EVALUATION': '#ec4899',
                    'VALIDE': '#06b6d4',
                    'EN_REGLEMENT': '#f97316',
                    'EN_RECOURS': '#ef4444'
                }.get(s.get('statut', ''), '#64748b')
                statut_item.setBackground(QColor(statut_color))
                statut_item.setForeground(QColor('white'))
                self.table_recent.setItem(i, 4, statut_item)
                
                self.table_recent.setItem(i, 5, QTableWidgetItem(f"{s.get('montant_net', 0):,.0f}"))
            
        except Exception as e:
            print(f"Erreur refresh dashboard: {e}")
