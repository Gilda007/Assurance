import sys
import random
import numpy as np
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget, 
                               QHBoxLayout, QFrame, QLabel, QPushButton, QSizePolicy, 
                               QGraphicsDropShadowEffect, QGridLayout, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QLineEdit, QProgressBar,
                               QStatusBar, QMenu, QMessageBox, QComboBox, QScrollArea,
                               QSplitter)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer, QEvent, QSettings
from PySide6.QtGui import QFont, QColor, QKeySequence, QShortcut, QPainter
from core.database import SessionLocal, engine, Base, init_db
from core.alerts import AlertManager
from core.logger import logger
from core.loader import AddonLoader
import os

# Imports pour les graphiques
try:
    import pyqtgraph as pg
    HAS_PYQTGRAPH = True
except ImportError:
    HAS_PYQTGRAPH = False
    print("Pour de meilleurs graphiques: pip install pyqtgraph")

# Imports des modules
from addons.Paramètres.views.setup_view import SetupView
from addons.Paramètres.controllers.setup_controller import SetupController
from addons.Paramètres.views.loggin_view import LoginView
from addons.Paramètres.controllers.login_controller import LoginController
from addons.Paramètres.models.models import User
from update_manager import UpdateManager


from core.database import engine, Base
# import addons.Automobiles.models as models

# Palette de couleurs moderne
class AppColors:
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    PRIMARY_LIGHT = "#60a5fa"
    SECONDARY = "#64748b"
    BACKGROUND = "#f8fafc"
    SIDEBAR_BG = "#0f172a"
    SIDEBAR_HOVER = "#1e293b"
    CARD_BG = "#ffffff"
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#475569"
    BORDER = "#e2e8f0"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    INFO = "#3b82f6"
    
    # Couleurs pour les graphiques
    CHART_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4"]
# Style Sheet
STYLE_SHEET = f"""
    QMainWindow {{
        background-color: {AppColors.BACKGROUND};
    }}
    
    QFrame#Sidebar {{
        background: {AppColors.SIDEBAR_BG};
        border: none;
        border-radius: 20px;
        margin: 10px 0 10px 10px;
    }}
    
    QPushButton#MenuBtn {{
        color: #94a3b8;
        background-color: transparent;
        border: none;
        border-radius: 10px;
        text-align: left;
        padding: 10px 16px;
        font-weight: 500;
        margin: 2px 10px;
    }}
    
    QPushButton#MenuBtn:hover {{
        background-color: {AppColors.SIDEBAR_HOVER};
        color: white;
    }}
    
    QPushButton#MenuBtn[active="true"] {{
        background: {AppColors.PRIMARY};
        color: white;
    }}
    
    QFrame#UserCard {{
        background: rgba(255,255,255,0.05);
        border-radius: 14px;
        margin: 10px;
        padding: 10px;
    }}
    
    QFrame#Header {{
        background: {AppColors.CARD_BG};
        border: 1px solid {AppColors.BORDER};
        border-radius: 16px;
        margin: 10px 10px 0 0;
    }}
    
    QLabel#PageTitle {{
        font-size: 20px;
        font-weight: 700;
        color: {AppColors.TEXT_PRIMARY};
    }}
    
    QStackedWidget#ContentArea {{
        background: transparent;
        margin: 10px 10px 10px 0;
    }}
    
    QScrollBar:vertical {{
        background: {AppColors.BACKGROUND};
        width: 6px;
        border-radius: 3px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {AppColors.SECONDARY};
        border-radius: 3px;
    }}
    
    QLineEdit#SearchBar {{
        background: #f1f5f9;
        border: none;
        border-radius: 20px;
        padding: 8px 16px;
        min-width: 250px;
    }}
    
    QLineEdit#SearchBar:focus {{
        border: 1px solid {AppColors.PRIMARY};
        background: white;
    }}
    
    QProgressBar {{
        border: none;
        border-radius: 3px;
        background: #e2e8f0;
        height: 4px;
    }}
    
    QProgressBar::chunk {{
        background: {AppColors.PRIMARY};
        border-radius: 3px;
    }}
    
    QTableWidget {{
        background: {AppColors.CARD_BG};
        border: 1px solid {AppColors.BORDER};
        border-radius: 12px;
        gridline-color: {AppColors.BORDER};
    }}
    
    QTableWidget::item {{
        padding: 8px;
    }}
    
    QHeaderView::section {{
        background: {AppColors.BACKGROUND};
        border: none;
        border-bottom: 1px solid {AppColors.BORDER};
        padding: 10px;
        font-weight: 600;
        color: {AppColors.TEXT_PRIMARY};
    }}
    
    QComboBox {{
        background: {AppColors.CARD_BG};
        border: 1px solid {AppColors.BORDER};
        border-radius: 8px;
        padding: 4px 8px;
        font-size: 12px;
    }}
    
    QPushButton#HomeBtn {{
        background: {AppColors.PRIMARY};
        color: white;
        border: none;
        border-radius: 10px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 600;
    }}
    QPushButton#HomeBtn:hover {{
        background: {AppColors.PRIMARY_DARK};
    }}
"""


class ModernChartWidget(QWidget):
    """Widget de graphique moderne avec pyqtgraph"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if HAS_PYQTGRAPH:
            # Graphique principal
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setBackground('w')
            self.plot_widget.setLabel('left', 'Montant (FCFA)')
            self.plot_widget.setLabel('bottom', 'Période')
            self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
            self.plot_widget.setMinimumHeight(300)
            
            # Légende
            self.plot_widget.addLegend()
            
            layout.addWidget(self.plot_widget)
        else:
            # Fallback si pyqtgraph n'est pas installé
            fallback = QLabel("📊 Graphique\nInstallez pyqtgraph pour des graphiques avancés")
            fallback.setAlignment(Qt.AlignCenter)
            fallback.setStyleSheet("background: white; border-radius: 12px; padding: 50px; color: #94a3b8;")
            layout.addWidget(fallback)
    
    def create_line_chart(self, data, labels, title="Évolution", x_label="Période", y_label="Valeur"):
        """Crée un graphique en ligne"""
        if not HAS_PYQTGRAPH:
            return
        
        self.plot_widget.clear()
        self.plot_widget.setTitle(title, size='14pt')
        self.plot_widget.setLabel('left', y_label)
        self.plot_widget.setLabel('bottom', x_label)
        
        x = list(range(len(data)))
        
        # Tracer la ligne
        pen = pg.mkPen(color=AppColors.CHART_COLORS[0], width=3)
        curve = self.plot_widget.plot(x, data, pen=pen, name=labels[0] if labels else "Série")
        
        # Ajouter des points
        scatter = pg.ScatterPlotItem(
            size=10,
            brush=pg.mkBrush(AppColors.CHART_COLORS[0]),
            pen=pg.mkPen('w', width=2)
        )
        spots = [{'pos': (i, val), 'data': i} for i, val in enumerate(data)]
        scatter.addPoints(spots)
        self.plot_widget.addItem(scatter)
        
        # Configurer l'axe X
        if len(labels) > 1:
            ticks = [(i, labels[i]) for i in range(len(labels))]
            ax = self.plot_widget.getAxis('bottom')
            ax.setTicks([ticks])
    
    def create_bar_chart(self, data, labels, title="Répartition", x_label="Catégories", y_label="Valeur"):
        """Crée un graphique à barres"""
        if not HAS_PYQTGRAPH:
            return
        
        self.plot_widget.clear()
        self.plot_widget.setTitle(title, size='14pt')
        self.plot_widget.setLabel('left', y_label)
        self.plot_widget.setLabel('bottom', x_label)
        
        # Créer les barres
        x = np.arange(len(data))
        bg = pg.BarGraphItem(x=x, height=data, width=0.6, brush=AppColors.CHART_COLORS[0])
        self.plot_widget.addItem(bg)
        
        # Configurer l'axe X
        if labels:
            ticks = [(i, labels[i]) for i in range(len(labels))]
            ax = self.plot_widget.getAxis('bottom')
            ax.setTicks([ticks])
    
    def create_pie_chart(self, data, labels, title="Répartition"):
        """Crée un graphique en secteurs (camembert)"""
        if not HAS_PYQTGRAPH:
            return
        
        self.plot_widget.clear()
        self.plot_widget.setTitle(title, size='14pt')
        
        # Calculer les angles
        total = sum(data)
        angles = [360 * d / total for d in data]
        
        # Créer un graphique en secteurs avec des couleurs différentes
        start_angle = 0
        for i, (value, label) in enumerate(zip(data, labels)):
            angle = 360 * value / total
            # Note: pyqtgraph n'a pas de camembert natif, on utilise un workaround
            # ou on peut utiliser matplotlib pour cela
            pass
    
    def clear(self):
        """Efface le graphique"""
        if HAS_PYQTGRAPH:
            self.plot_widget.clear()


class ModernDashboard(QWidget):
    """Dashboard moderne avec graphiques professionnels"""
    
    card_clicked = Signal(str)
    
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setup_ui()
        self.init_data()
        self.start_realtime_updates()
    
    def setup_ui(self):
        # Layout principal avec ScrollArea
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ScrollArea pour tout le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        # Widget conteneur
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(20)
        
        # ==================== EN-TÊTE ====================
        header_layout = QHBoxLayout()
        welcome_label = QLabel(f"Bonjour, {self.user.username if self.user else 'Utilisateur'}")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #1e293b;")
        
        date_label = QLabel(datetime.now().strftime("%A %d %B %Y"))
        date_label.setStyleSheet("color: #64748b; font-size: 14px;")
        
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(date_label)
        container_layout.addLayout(header_layout)
        
        # ==================== SECTION 1: CARTES STATISTIQUES ====================
        stats_title = QLabel("📊 Indicateurs clés")
        stats_title.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 12px;
        """)
        container_layout.addWidget(stats_title)

        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(16)

        stats_data = [
            {"icon": "🚗", "title": "Véhicules", "value": "156", "color": "#3b82f6"},
            {"icon": "📄", "title": "Contrats", "value": "234", "color": "#10b981"},
            {"icon": "💰", "title": "Primes", "value": "2.5M", "color": "#f59e0b"},
            {"icon": "⚠️", "title": "Sinistres", "value": "3", "color": "#ef4444"},
            {"icon": "👥", "title": "Clients", "value": "189", "color": "#8b5cf6"},
            {"icon": "📅", "title": "Échéances", "value": "12", "color": "#64748b"}
        ]

        self.stat_cards = []
        for i, stat in enumerate(stats_data):
            card = self.create_simple_stat_card(stat)
            self.stats_grid.addWidget(card, i // 3, i % 3)
            self.stat_cards.append(card)

        container_layout.addLayout(self.stats_grid)
        
        # ==================== SECTION 2: GRAPHIQUES PRINCIPAUX ====================
        charts_title = QLabel("📈 Analyses et tendances")
        charts_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1e293b; margin-top: 16px;")
        container_layout.addWidget(charts_title)
        
        # Splitter pour les deux graphiques principaux
        charts_splitter = QSplitter(Qt.Horizontal)
        charts_splitter.setStyleSheet("QSplitter::handle { background: #e2e8f0; width: 1px; margin: 0 10px; }")
        
        # Graphique 1: Évolution des primes (ligne)
        chart1_card = self.create_chart_card("📈 Évolution des primes", "line")
        charts_splitter.addWidget(chart1_card)
        
        # Graphique 2: Répartition des garanties (barres)
        chart2_card = self.create_chart_card("📊 Répartition des garanties", "bar")
        charts_splitter.addWidget(chart2_card)
        
        container_layout.addWidget(charts_splitter)
        
        # ==================== SECTION 3: GRAPHIQUES SUPPLÉMENTAIRES ====================
        extra_charts_layout = QHBoxLayout()
        extra_charts_layout.setSpacing(20)
        
        # Graphique 3: Comparaison annuelle (3D-like)
        chart3_card = self.create_chart_card("📊 Comparaison annuelle", "bar")
        extra_charts_layout.addWidget(chart3_card)
        
        # Graphique 4: Tendance des sinistres (ligne)
        chart4_card = self.create_chart_card("⚠️ Tendance des sinistres", "line")
        extra_charts_layout.addWidget(chart4_card)
        
        container_layout.addLayout(extra_charts_layout)
        
        # ==================== SECTION 4: TABLEAU DES ACTIVITÉS ====================
        activities_title = QLabel("📋 Dernières activités")
        activities_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1e293b; margin-top: 16px;")
        container_layout.addWidget(activities_title)
        
        activities_card = self.create_activities_card()
        container_layout.addWidget(activities_card)
        
        # ==================== SECTION 5: INDICATEURS RAPIDES ====================
        quick_stats_title = QLabel("⚡ Indicateurs rapides")
        quick_stats_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1e293b; margin-top: 16px;")
        container_layout.addWidget(quick_stats_title)
        
        quick_stats_layout = QHBoxLayout()
        quick_stats_layout.setSpacing(15)
        
        quick_stats = [
            ("📊 Taux d'occupation", "78%", AppColors.PRIMARY),
            ("⭐ Satisfaction client", "4.8/5", AppColors.SUCCESS),
            ("⚡ Temps de réponse", "< 2h", AppColors.WARNING),
            ("🔄 Taux renouvellement", "95%", AppColors.INFO),
        ]
        
        for label, value, color in quick_stats:
            stat = self.create_quick_stat(label, value, color)
            quick_stats_layout.addWidget(stat)
        
        quick_stats_layout.addStretch()
        container_layout.addLayout(quick_stats_layout)
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def create_enhanced_stat_card(self, stat):
        """Crée une carte statistique améliorée avec effet moderne"""
        card = QFrame()
        card.setFixedHeight(140)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: {AppColors.CARD_BG};
                border-radius: 20px;
                border: 1px solid {AppColors.BORDER};
            }}
            QFrame:hover {{
                border-color: {stat['color']};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 white, stop:1 {stat['color']}08);
            }}
        """)
        
        card.setToolTip(f"Cliquez pour voir les détails des {stat['title']}")
        
        def on_click(event):
            self.card_clicked.emit(stat['title'])
        card.mousePressEvent = on_click
        
        # Ombre plus élégante
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)
        
        # ========== EN-TÊTE ==========
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Icône avec cercle de fond
        icon_container = QFrame()
        icon_container.setFixedSize(44, 44)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {stat['color']}15;
                border-radius: 14px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(stat['icon'])
        icon_label.setStyleSheet(f"font-size: 24px; background: transparent;")
        icon_layout.addWidget(icon_label)
        
        header_layout.addWidget(icon_container)
        
        # Valeur et titre
        value_title_layout = QVBoxLayout()
        value_title_layout.setSpacing(4)
        
        value_label = QLabel(stat['value'])
        value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 800;
            color: {stat['color']};
            background: transparent;
            letter-spacing: -0.5px;
        """)
        value_label.setObjectName(f"value_{stat['title'].lower().replace(' ', '_')}")
        
        title_label = QLabel(stat['title'])
        title_label.setStyleSheet("""
            color: #1e293b;
            font-size: 14px;
            font-weight: 600;
            background: transparent;
        """)
        
        value_title_layout.addWidget(value_label)
        value_title_layout.addWidget(title_label)
        
        header_layout.addLayout(value_title_layout)
        header_layout.addStretch()
        
        # Badge de tendance
        trend_container = QFrame()
        if stat['trend_type'] == "up":
            trend_container.setStyleSheet(f"""
                QFrame {{
                    background: {AppColors.SUCCESS}15;
                    border-radius: 20px;
                    padding: 4px 10px;
                }}
            """)
            trend_layout = QHBoxLayout(trend_container)
            trend_layout.setSpacing(4)
            trend_layout.setContentsMargins(8, 4, 8, 4)
            
            trend_icon = QLabel("▲")
            trend_icon.setStyleSheet(f"color: {AppColors.SUCCESS}; font-size: 11px; font-weight: bold;")
            
            trend_label = QLabel(stat['trend'])
            trend_label.setStyleSheet(f"color: {AppColors.SUCCESS}; font-size: 12px; font-weight: 700;")
            
            trend_layout.addWidget(trend_icon)
            trend_layout.addWidget(trend_label)
            
        elif stat['trend_type'] == "down":
            trend_container.setStyleSheet(f"""
                QFrame {{
                    background: {AppColors.DANGER}15;
                    border-radius: 20px;
                    padding: 4px 10px;
                }}
            """)
            trend_layout = QHBoxLayout(trend_container)
            trend_layout.setSpacing(4)
            trend_layout.setContentsMargins(8, 4, 8, 4)
            
            trend_icon = QLabel("▼")
            trend_icon.setStyleSheet(f"color: {AppColors.DANGER}; font-size: 11px; font-weight: bold;")
            
            trend_label = QLabel(stat['trend'])
            trend_label.setStyleSheet(f"color: {AppColors.DANGER}; font-size: 12px; font-weight: 700;")
            
            trend_layout.addWidget(trend_icon)
            trend_layout.addWidget(trend_label)
            
        else:
            trend_container.setStyleSheet(f"""
                QFrame {{
                    background: {AppColors.SECONDARY}15;
                    border-radius: 20px;
                    padding: 4px 10px;
                }}
            """)
            trend_layout = QHBoxLayout(trend_container)
            trend_layout.setSpacing(4)
            trend_layout.setContentsMargins(8, 4, 8, 4)
            
            trend_label = QLabel(stat['trend'])
            trend_label.setStyleSheet(f"color: {AppColors.SECONDARY}; font-size: 12px; font-weight: 700;")
            
            trend_layout.addWidget(trend_label)
        
        header_layout.addWidget(trend_container)
        
        layout.addLayout(header_layout)
        
        # ========== PIED DE CARTE ==========
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 4, 0, 0)
        
        # Sous-titre
        subtitle_label = QLabel(stat['subtitle'])
        subtitle_label.setStyleSheet("""
            color: #64748b;
            font-size: 11px;
            font-weight: 500;
            background: transparent;
        """)
        
        # Lien "Voir détails"
        detail_link = QLabel("🔍 Détails")
        detail_link.setStyleSheet(f"""
            color: {stat['color']};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            text-decoration: underline;
        """)
        detail_link.setCursor(Qt.PointingHandCursor)
        detail_link.mousePressEvent = lambda e: self.card_clicked.emit(stat['title'])
        
        footer_layout.addWidget(subtitle_label)
        footer_layout.addStretch()
        footer_layout.addWidget(detail_link)
        
        layout.addLayout(footer_layout)
        
        # Barre de progression miniature (optionnelle)
        progress_bar = QFrame()
        progress_bar.setFixedHeight(3)
        progress_bar.setStyleSheet(f"""
            QFrame {{
                background: {AppColors.BORDER};
                border-radius: 2px;
            }}
        """)
        
        progress_fill = QFrame()
        progress_fill.setFixedHeight(3)
        progress_fill.setStyleSheet(f"""
            QFrame {{
                background: {stat['color']};
                border-radius: 2px;
            }}
        """)
        
        # Largeur aléatoire pour la démo (à remplacer par des données réelles)
        progress_width = random.randint(30, 90)
        progress_fill.setFixedWidth(progress_width)
        
        progress_layout = QHBoxLayout(progress_bar)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.addWidget(progress_fill)
        progress_layout.addStretch()
        
        layout.addWidget(progress_bar)
        
        return card
    
    def create_stat_card(self, icon, title, value, color, trend, subtitle):
        """Crée une carte statistique"""
        card = QFrame()
        card.setFixedHeight(130)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: {AppColors.CARD_BG};
                border-radius: 16px;
                border: 1px solid {AppColors.BORDER};
            }}
            QFrame:hover {{
                border-color: {color};
                background: #f8fafc;
            }}
        """)
        
        card.setToolTip(f"Cliquez pour voir les détails des {title}")
        
        def on_click(event):
            self.card_clicked.emit(title)
        card.mousePressEvent = on_click
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px;")
        header.addWidget(icon_label)
        header.addStretch()
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {color};")
        value_label.setObjectName(f"value_{title.lower().replace(' ', '_')}")
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")
        
        trend_label = QLabel(trend)
        if '+' in trend:
            trend_label.setStyleSheet("color: #10b981; font-size: 11px;")
            trend_label.setText(f"▲ {trend}")
        elif '-' in trend:
            trend_label.setStyleSheet("color: #ef4444; font-size: 11px;")
            trend_label.setText(f"▼ {trend}")
        else:
            trend_label.setStyleSheet("color: #64748b; font-size: 11px;")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #94a3b8; font-size: 10px;")
        
        layout.addLayout(header)
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        layout.addWidget(trend_label)
        layout.addWidget(subtitle_label)
        
        return card
    
    def create_chart_card(self, title, chart_type="line"):
        """Crée une carte avec graphique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {AppColors.CARD_BG};
                border-radius: 16px;
                border: 1px solid {AppColors.BORDER};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        
        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: 700; font-size: 15px;")
        layout.addWidget(title_label)
        
        # Sélecteur de période (pour certains graphiques)
        period_combo = QComboBox()
        period_combo.addItems(["6 derniers mois", "12 derniers mois", "24 derniers mois"])
        period_combo.setStyleSheet("font-size: 11px; padding: 2px 4px; max-width: 120px;")
        period_combo.currentTextChanged.connect(lambda: self.update_chart_data(chart_type))
        layout.addWidget(period_combo)
        
        # Widget de graphique
        chart_widget = ModernChartWidget()
        layout.addWidget(chart_widget)
        
        # Stocker le widget pour mise à jour
        if not hasattr(self, 'chart_widgets'):
            self.chart_widgets = []
        self.chart_widgets.append((chart_widget, chart_type, title))
        
        # Initialiser avec des données
        self.init_chart_data(chart_widget, chart_type, title)
        
        return card
    
    def init_chart_data(self, chart_widget, chart_type, title):
        """Initialise les données du graphique"""
        if chart_type == "line":
            # Données pour graphique en ligne
            months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            values = [125, 138, 152, 162, 175, 185, 192, 198, 205, 212, 218, 225]
            chart_widget.create_line_chart(values[:6], months[:6], title, "Mois", "Montant (k FCFA)")
        
        elif chart_type == "bar":
            # Données pour graphique à barres
            categories = ['RC', 'Vol', 'Incendie', 'Bris', 'DTA', 'IPT']
            values = [45, 25, 15, 10, 3, 2]
            chart_widget.create_bar_chart(values, categories, title, "Garanties", "Souscriptions (%)")
    
    def update_chart_data(self, chart_type):
        """Met à jour les données des graphiques"""
        # Simuler une mise à jour
        for chart_widget, c_type, title in getattr(self, 'chart_widgets', []):
            if c_type == chart_type:
                new_values = [random.randint(100, 250) for _ in range(6)]
                months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun']
                chart_widget.create_line_chart(new_values, months, title, "Mois", "Montant (k FCFA)")
    
    def create_activities_card(self):
        """Crée une carte avec le tableau des activités"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {AppColors.CARD_BG};
                border-radius: 16px;
                border: 1px solid {AppColors.BORDER};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        
        self.activities_table = QTableWidget(0, 3)
        self.activities_table.setHorizontalHeaderLabels(["Heure", "Action", "Utilisateur"])
        self.activities_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.activities_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.activities_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.activities_table.setShowGrid(False)
        self.activities_table.setAlternatingRowColors(True)
        self.activities_table.setFixedHeight(250)
        
        activities = [
            ("10:30", "🚗 Nouveau véhicule enregistré (LT 123 AB)", "Admin"),
            ("09:45", "📄 Contrat #12345 renouvelé", "Agent Dupont"),
            ("09:15", "💰 Paiement reçu de 250 000 FCFA", "Agent Martin"),
            ("08:30", "👥 Nouveau client enregistré", "Admin"),
            ("Hier 16:20", "⚠️ Sinistre #789 déclaré", "Agent Sophie"),
        ]
        
        for time, action, user in activities:
            row = self.activities_table.rowCount()
            self.activities_table.insertRow(row)
            self.activities_table.setItem(row, 0, QTableWidgetItem(time))
            self.activities_table.setItem(row, 1, QTableWidgetItem(action))
            self.activities_table.setItem(row, 2, QTableWidgetItem(user))
        
        layout.addWidget(self.activities_table)
        
        return card
    
    def create_simple_stat_card(self, stat):
        """Crée une carte statistique simple et propre"""
        card = QFrame()
        card.setFixedHeight(110)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }}
            QFrame:hover {{
                border-color: {stat['color']};
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)
        
        # Icône
        icon_label = QLabel(stat['icon'])
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            font-size: 28px;
            background: {stat['color']}10;
            border-radius: 12px;
        """)
        
        # Infos
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        value_label = QLabel(stat['value'])
        value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {stat['color']};
        """)
        
        title_label = QLabel(stat['title'])
        title_label.setStyleSheet("color: #64748b; font-size: 13px;")
        
        info_layout.addWidget(value_label)
        info_layout.addWidget(title_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return card
    
    def create_quick_stat(self, label, value, color):
        """Crée un indicateur rapide"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background: {AppColors.CARD_BG};
                border-radius: 12px;
                border: 1px solid {AppColors.BORDER};
                padding: 8px 16px;
            }}
        """)
        
        layout = QHBoxLayout(widget)
        layout.setSpacing(10)
        
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet("color: #64748b; font-size: 12px;")
        
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: 700;")
        
        layout.addWidget(label_lbl)
        layout.addWidget(value_lbl)
        
        return widget
    
    def init_data(self):
        """Initialise les données"""
        pass
    
    def update_stats(self):
        """Met à jour les statistiques"""
        values = ["178", "245", "2.8M", "2", "201", "8"]
        for i, (card, title) in enumerate(self.stat_cards):
            for child in card.findChildren(QLabel):
                if child.objectName().startswith("value_"):
                    child.setText(values[i])
    
    def start_realtime_updates(self):
        """Démarre les mises à jour en temps réel"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_activities)
        self.timer.start(30000)
    
    def refresh_stats(self):
        """Rafraîchit les statistiques avec animation"""
        self.status_bar.showMessage("Actualisation des statistiques...", 2000)
        
        # Simuler de nouvelles valeurs (à remplacer par des appels BD)
        new_values = [
            str(random.randint(150, 180)),
            str(random.randint(220, 260)),
            f"{random.randint(2, 4)}.{random.randint(0, 9)}M",
            str(random.randint(1, 6)),
            str(random.randint(180, 220)),
            str(random.randint(8, 18))
        ]
        
        for i, (card, title) in enumerate(self.stat_cards):
            # Animer la mise à jour
            for child in card.findChildren(QLabel):
                if child.objectName().startswith("value_"):
                    old_text = child.text()
                    child.setText(new_values[i])
                    
                    # Animation de changement de couleur
                    child.setStyleSheet(f"""
                        font-size: 28px;
                        font-weight: 800;
                        color: {AppColors.SUCCESS};
                        background: transparent;
                        transition: color 0.3s;
                    """)
                    
                    # Retour à la couleur normale après 500ms
                    QTimer.singleShot(500, lambda c=child, t=title: self.reset_card_color(c, t))
        
        # Mettre à jour la tendance
        self.status_bar.showMessage("Statistiques mises à jour", 2000)

    def reset_card_color(self, label, title):
        """Remet la couleur d'origine de la carte"""
        # Récupérer la couleur d'origine
        for stat in self.stats_data:
            if stat['title'] == title:
                label.setStyleSheet(f"""
                    font-size: 28px;
                    font-weight: 800;
                    color: {stat['color']};
                    background: transparent;
                    letter-spacing: -0.5px;
                """)
                break

    def update_activities(self):
        """Ajoute une nouvelle activité périodiquement"""
        current_time = datetime.now().strftime("%H:%M")
        self.activities_table.insertRow(0)
        self.activities_table.setItem(0, 0, QTableWidgetItem(current_time))
        self.activities_table.setItem(0, 1, QTableWidgetItem("🔄 Mise à jour automatique des données"))
        self.activities_table.setItem(0, 2, QTableWidgetItem("Système"))
        
        while self.activities_table.rowCount() > 10:
            self.activities_table.removeRow(10)

class AnimatedSidebar(QFrame):
    """Sidebar moderne avec animation et design premium"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("Sidebar")
        self.collapsed = False
        self.collapsed_width = 70
        self.expanded_width = 240
        self.setFixedWidth(self.expanded_width)
        
        # Initialiser la liste des boutons
        self.menu_buttons = []

        # Animation
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)

        # Style global
        self.setStyleSheet("""
        #Sidebar {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b,
                stop:1 #0f172a
            );
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        """)

        # Ombre
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(3)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Burger button
        burger_frame = QFrame()
        burger_frame.setFixedHeight(60)
        burger_layout = QHBoxLayout(burger_frame)
        burger_layout.setContentsMargins(15, 0, 15, 0)

        self.burger_btn = QPushButton("☰")
        self.burger_btn.setFixedSize(36, 36)
        self.burger_btn.setCursor(Qt.PointingHandCursor)

        self.burger_btn.setStyleSheet("""
        QPushButton {
            background: rgba(255,255,255,0.08);
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 18px;
        }
        QPushButton:hover {
            background: rgba(255,255,255,0.18);
        }
        QPushButton:pressed {
            background: rgba(255,255,255,0.25);
        }
        """)

        self.burger_btn.clicked.connect(self.toggle_sidebar)

        burger_layout.addWidget(self.burger_btn)
        burger_layout.addStretch()
        layout.addWidget(burger_frame)

        # Logo
        self.logo_label = QLabel("LOMETA")
        self.logo_label.setAlignment(Qt.AlignCenter)

        self.logo_label.setStyleSheet("""
        color: white;
        font-size: 20px;
        font-weight: 700;
        padding: 18px;
        margin: 10px;
        background: rgba(255,255,255,0.04);
        border-radius: 14px;
        letter-spacing: 1px;
        """)

        layout.addWidget(self.logo_label)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255,255,255,0.1); margin: 10px 15px;")
        layout.addWidget(sep)

        # Menu container
        self.menu_container = QVBoxLayout()
        self.menu_container.setSpacing(6)
        self.menu_container.setContentsMargins(10, 10, 10, 10)
        self.menu_container.setAlignment(Qt.AlignTop)

        self.menu_widget = QWidget()
        self.menu_widget.setLayout(self.menu_container)
        layout.addWidget(self.menu_widget)

        layout.addStretch()

        # ========== USER CARD AMÉLIORÉE ==========
        self.user_card = QFrame()
        self.user_card.setObjectName("UserCard")

        self.user_card.setStyleSheet("""
        #UserCard {
            background: rgba(255,255,255,0.08);
            border-radius: 20px;
            margin: 16px;
            padding: 16px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        """)

        user_layout = QVBoxLayout(self.user_card)
        user_layout.setSpacing(12)
        user_layout.setContentsMargins(0, 0, 0, 0)

        # ========== AVATAR AVEC STATUT ==========
        avatar_container = QWidget()
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_layout.setSpacing(0)

        self.user_avatar = QLabel("A")
        self.user_avatar.setAlignment(Qt.AlignCenter)
        self.user_avatar.setFixedSize(56, 56)
        self.user_avatar.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #3b82f6,
                stop:1 #6366f1
            );
            border-radius: 28px;
        """)

        # Badge de statut (cercle vert en bas à droite de l'avatar)
        status_badge = QLabel()
        status_badge.setFixedSize(14, 14)
        status_badge.move(40, 40)
        status_badge.setParent(self.user_avatar)
        status_badge.setStyleSheet("""
            background-color: #10b981;
            border-radius: 7px;
            border: 2px solid #0f172a;
        """)

        avatar_layout.addWidget(self.user_avatar)

        user_layout.addWidget(avatar_container, 0, Qt.AlignCenter)

        # ========== NOM UTILISATEUR ==========
        self.user_name = QLabel("Jean Dupont")
        self.user_name.setAlignment(Qt.AlignCenter)
        self.user_name.setStyleSheet("""
            color: white;
            font-weight: 700;
            font-size: 14px;
        """)
        user_layout.addWidget(self.user_name)

        # ========== RÔLE ==========
        self.user_role = QLabel("Administrateur")
        self.user_role.setAlignment(Qt.AlignCenter)
        self.user_role.setStyleSheet("""
            color: rgba(255,255,255,0.6);
            font-size: 11px;
        """)
        user_layout.addWidget(self.user_role)

        # ========== STATUT EN LIGNE (texte) ==========
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setAlignment(Qt.AlignCenter)
        status_layout.setSpacing(6)
        status_layout.setContentsMargins(0, 4, 0, 0)

        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(8, 8)
        self.status_indicator.setStyleSheet("background-color: #10b981; border-radius: 4px;")

        self.status_label = QLabel("En ligne")
        self.status_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 10px;")

        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)

        user_layout.addWidget(status_container)

        layout.addWidget(self.user_card)

        # Logout button
        # ========== LOGOUT BUTTON AVEC ANIMATION ==========
        self.logout_btn = QPushButton("🚪  Déconnexion")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                color: #fca5a5;
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.25);
                border-radius: 14px;
                padding: 12px;
                font-size: 13px;
                font-weight: 600;
                text-align: center;
                margin: 12px 16px 20px 16px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.2);
                border-color: rgba(239, 68, 68, 0.5);
                color: #fecaca;
                padding-left: 16px;
            }
            QPushButton:pressed {
                background: rgba(239, 68, 68, 0.3);
                padding-top: 13px;
                padding-bottom: 11px;
            }
        """)
        layout.addWidget(self.logout_btn)

        # Animation au survol (optionnel)
    
    def animate_logout_button(event):
        if event.type() == QEvent.Enter:
            # Animation d'entrée
            pass
        elif event.type() == QEvent.Leave:
            # Animation de sortie
            pass

    def toggle_sidebar(self):
        self.collapsed = not self.collapsed
        target_width = self.collapsed_width if self.collapsed else self.expanded_width

        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.start()

        # Logo switch
        if self.collapsed:
            self.logo_label.setText("🚗")
            self.logo_label.setStyleSheet("""
                color: white;
                font-size: 24px;
                font-weight: 700;
                padding: 18px;
                margin: 10px;
                background: rgba(255,255,255,0.04);
                border-radius: 14px;
            """)
        else:
            self.logo_label.setText("LOMETA")
            self.logo_label.setStyleSheet("""
                color: white;
                font-size: 20px;
                font-weight: 700;
                padding: 18px;
                margin: 10px;
                background: rgba(255,255,255,0.04);
                border-radius: 14px;
                letter-spacing: 1px;
            """)

        # Menu text - utiliser menu_buttons au lieu de menu_container
        for btn in self.menu_buttons:
            if hasattr(btn, 'original_text'):
                btn.setText(btn.icon_only if self.collapsed else btn.original_text)

        self.user_name.setVisible(not self.collapsed)

    def add_menu_button(self, label, icon_char, widget=None):
        btn = QPushButton(f"{icon_char}  {label}")
        btn.setObjectName("MenuBtn")
        btn.setCursor(Qt.PointingHandCursor)

        btn.original_text = f"{icon_char}  {label}"
        btn.icon_only = icon_char
        btn.setCheckable(True)
        btn.setProperty("linked_widget", widget)

        btn.setStyleSheet("""
        QPushButton {
            color: #cbd5f5;
            background: transparent;
            border: none;
            padding: 12px;
            text-align: left;
            border-radius: 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background: rgba(255,255,255,0.08);
            color: white;
        }
        QPushButton:checked {
            background: #3b82f6;
            color: white;
        }
        """)

        self.menu_container.addWidget(btn)
        self.menu_buttons.append(btn)
        return btn

    def set_active_module(self, active_widget):
        for btn in self.menu_buttons:
            is_active = btn.property("linked_widget") == active_widget
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def set_user_status(self, status="online"):
        """Définit le statut de l'utilisateur"""
        status_colors = {
            "online": "#10b981",
            "away": "#f59e0b",
            "busy": "#ef4444",
            "offline": "#64748b"
        }
        status_texts = {
            "online": "En ligne",
            "away": "Absent",
            "busy": "Occupé",
            "offline": "Hors ligne"
        }
        
        color = status_colors.get(status, "#10b981")
        text = status_texts.get(status, "En ligne")
        
        self.status_indicator.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
        self.status_label.setText(text)

    def set_user_info(self, username, role="Utilisateur", email=""):
        """Définit les informations utilisateur"""
        self.user_name.setText(username)
        self.user_role.setText(role)
        
        # Avatar avec initiales
        initials = username[0].upper() if username else "U"
        self.user_avatar.setText(initials)
        
        # Tooltip avec email
        if email:
            self.user_card.setToolTip(f"📧 {email}")

    def set_user_info(self, username):
        self.user_name.setText(username)
        initials = username[0].upper() if username else "U"
        self.user_avatar.setText(initials)

class MainWindow(QMainWindow):
    logout_requested = Signal()
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("LOMETA - Tableau de Bord")
        self.resize(1280, 800)
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(STYLE_SHEET)
        
        self.setup_ui()
        self.init_modules()
        self.update_manager = UpdateManager(self)
        self.setup_shortcuts()
        self.check_environment()
    
    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = AnimatedSidebar()
        self.main_layout.addWidget(self.sidebar)
        
        # Zone de contenu
        self.right_container = QWidget()
        right_layout = QVBoxLayout(self.right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Header
        self.setup_header()
        right_layout.addWidget(self.header)
        
        # Content area
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("ContentArea")
        right_layout.addWidget(self.content_area)
        
        self.main_layout.addWidget(self.right_container, 1)
        
        # Status bar
        self.setup_statusbar()
        
        # Dashboard par défaut
        self.dashboard = ModernDashboard(self.user)
        self.content_area.addWidget(self.dashboard)
        self.content_area.setCurrentWidget(self.dashboard)
        
        # Compatibilité avec les addons existants
        self.sidebar_layout = self.sidebar.menu_container
        
        # Déconnexion
        self.sidebar.logout_btn.clicked.connect(self.handle_logout)
        self.sidebar.set_user_info(self.user.username)
    
    # Dans main.py ou au début de l'application
    def check_environment(self):
        """Vérifie l'environnement et affiche les chemins"""
        from config import Config
        
        print("=" * 60)
        print("🔍 DIAGNOSTIC DE L'ENVIRONNEMENT")
        print("=" * 60)
        print(f"Mode compilé : {getattr(sys, 'frozen', False)}")
        print(f"Executable : {sys.executable}")
        print(f"Dossier exe : {Config.get_app_dir()}")
        print(f"Dossier addons : {Config.get_addons_dir()}")
        
        # Vérifier si _internal existe
        internal_dir = Config.get_internal_dir()
        print(f"Dossier _internal : {internal_dir}")
        print(f"_internal existe : {os.path.exists(internal_dir)}")
        
        # Vérifier le contenu de addons
        addons_dir = Config.get_addons_dir()
        if os.path.exists(addons_dir):
            print(f"\n📁 Contenu de addons :")
            for item in os.listdir(addons_dir):
                item_path = os.path.join(addons_dir, item)
                if os.path.isdir(item_path):
                    print(f"  📁 {item}/")
                    # Vérifier si manifest.json existe
                    manifest = os.path.join(item_path, 'manifest.json')
                    if os.path.exists(manifest):
                        print(f"     ✅ manifest.json présent")
                    else:
                        print(f"     ❌ manifest.json manquant")
                else:
                    print(f"  📄 {item}")
        else:
            print(f"\n❌ Dossier addons non trouvé !")
        
        print("=" * 60)

    def setup_header(self):
        self.header = QFrame()
        self.header.setObjectName("Header")
        self.header.setFixedHeight(70)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        header_layout.setSpacing(15)
        
        # ========== PARTIE GAUCHE ==========
        # Bouton Home
        self.home_btn = QPushButton("🏠")
        self.home_btn.setFixedSize(36, 36)
        self.home_btn.setCursor(Qt.PointingHandCursor)
        self.home_btn.setToolTip("Accueil (Ctrl+D)")
        self.home_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #f1f5f9;
            }
        """)
        self.home_btn.clicked.connect(self.go_to_dashboard)
        header_layout.addWidget(self.home_btn)
        
        # Titre de la page
        self.page_title = QLabel("Tableau de Bord")
        self.page_title.setObjectName("PageTitle")
        header_layout.addWidget(self.page_title)
        
        header_layout.addStretch()
        
        # ========== PARTIE CENTRALE ==========
        # Barre de recherche
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.setPlaceholderText("🔍 Rechercher un véhicule, client, contrat...")
        self.search_bar.setMinimumWidth(350)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background: #f1f5f9;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QLineEdit:focus {
                background: white;
                border: 1px solid #3b82f6;
            }
        """)
        self.search_bar.returnPressed.connect(self.handle_search)
        header_layout.addWidget(self.search_bar)
        
        header_layout.addStretch()
        
        # ========== PARTIE DROITE ==========
        # Bouton notifications
        self.notif_btn = QPushButton("🔔")
        self.notif_btn.setFixedSize(36, 36)
        self.notif_btn.setCursor(Qt.PointingHandCursor)
        self.notif_btn.setToolTip("Notifications")
        self.notif_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #f1f5f9;
            }
        """)
        self.notif_btn.clicked.connect(self.show_notifications)
        header_layout.addWidget(self.notif_btn)
        
        # Bouton aide
        self.help_btn = QPushButton("❓")
        self.help_btn.setFixedSize(36, 36)
        self.help_btn.setCursor(Qt.PointingHandCursor)
        self.help_btn.setToolTip("Aide (F1)")
        self.help_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #f1f5f9;
            }
        """)
        self.help_btn.clicked.connect(self.show_help)
        header_layout.addWidget(self.help_btn)
        
        # Bouton plein écran
        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.setFixedSize(36, 36)
        self.fullscreen_btn.setCursor(Qt.PointingHandCursor)
        self.fullscreen_btn.setToolTip("Plein écran (F11)")
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #f1f5f9;
            }
        """)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        header_layout.addWidget(self.fullscreen_btn)
        
        # Avatar utilisateur
        self.user_avatar = QLabel()
        self.user_avatar.setFixedSize(36, 36)
        self.user_avatar.setAlignment(Qt.AlignCenter)
        self.user_avatar.setCursor(Qt.PointingHandCursor)
        self.user_avatar.setToolTip("Profil utilisateur")
        self.user_avatar.setStyleSheet("""
            QLabel {
                background: #3b82f6;
                color: white;
                font-weight: bold;
                border-radius: 18px;
                font-size: 14px;
            }
        """)
        self.user_avatar.mousePressEvent = self.show_user_menu
        header_layout.addWidget(self.user_avatar)
    
    def setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Horloge
        self.clock_label = QLabel()
        self.update_clock()
        self.status_bar.addPermanentWidget(self.clock_label)
        
        # Timer pour l'horloge
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
    
    def update_clock(self):
        self.clock_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+F"), self, self.focus_search)
        QShortcut(QKeySequence("F5"), self, self.refresh)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+D"), self, self.go_to_dashboard)
    
    def focus_search(self):
        self.search_bar.setFocus()
        self.search_bar.selectAll()
    
    def refresh(self):
        self.status_bar.showMessage("Actualisation des données...", 2000)
        if hasattr(self, 'dashboard'):
            self.dashboard.update_stats()
    
    def create_menu(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        
        # Action Vérifier les mises à jour
        check_update_action = help_menu.addAction("&Vérifier les mises à jour")
        check_update_action.triggered.connect(self.manual_update_check)
        
        help_menu.addSeparator()
        
        about_action = help_menu.addAction("&À propos")
        about_action.triggered.connect(self.show_about)

    def check_updates_startup(self):
        """Vérifie les mises à jour au démarrage"""
        # Optionnel: vérifier silencieusement
        self.update_manager.check_updates_auto()
        
        # Afficher un message dans la barre d'état
        self.statusBar().showMessage("Vérification des mises à jour...", 2000)
    
    def manual_update_check(self):
        """Vérification manuelle des mises à jour"""
        self.update_manager.check_updates_manual()
    
    def show_status_message(self, message):
        """Affiche un message dans la barre d'état"""
        self.statusBar().showMessage(message, 5000)
    
    def show_about(self):
        """Affiche la boîte À propos"""
        QMessageBox.about(self, "À propos", 
                         "Mon Application v1.0.0\n\n"
                         "Application de gestion modulaire\n"
                         "© 2024 Votre Société")

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def go_to_dashboard(self):
        """Retourne au tableau de bord"""
        if self.content_area.currentWidget() != self.dashboard:
            self.content_area.setCurrentWidget(self.dashboard)
            self.page_title.setText("Tableau de Bord")
            self.sidebar.set_active_module(self.dashboard)
            self.status_bar.showMessage("Retour au tableau de bord", 2000)
    
    def handle_search(self):
        query = self.search_bar.text().strip()
        if query:
            self.status_bar.showMessage(f"Recherche de : {query}", 3000)
    
    def init_modules(self):
        """Charge tous les modules/addons - IDENTIQUE À old.py"""
        self.db_session = SessionLocal()
        self.loader = AddonLoader()
        self.addons = self.loader.load_all(self)
    
    def add_menu_button(self, label, icon_char, widget):
        """Ajoute un bouton de menu (pour la compatibilité avec les addons) - IDENTIQUE À old.py"""
        btn = self.sidebar.add_menu_button(label, icon_char, widget)
        btn.clicked.connect(lambda: self.set_content_widget(widget, label))
        
        if self.content_area.indexOf(widget) == -1:
            self.content_area.addWidget(widget)
    
    def set_content_widget(self, widget, title="Module"):
        """Change le widget affiché - IDENTIQUE À old.py"""
        if self.content_area.currentWidget() == widget:
            return
        
        self.page_title.setText(title)
        
        if self.content_area.indexOf(widget) == -1:
            self.content_area.addWidget(widget)
        
        self.content_area.setCurrentWidget(widget)
        self.update_sidebar_style(widget)
    
    def update_sidebar_style(self, active_widget):
        """Met à jour le style du bouton actif - IDENTIQUE À old.py"""
        for i in range(self.sidebar.menu_container.count()):
            item = self.sidebar.menu_container.itemAt(i)
            if item and item.widget():
                btn = item.widget()
                if isinstance(btn, QPushButton):
                    is_active = btn.property("linked_widget") == active_widget
                    btn.setProperty("active", str(is_active).lower())
                    btn.style().unpolish(btn)
                    btn.style().polish(btn)
    
    def handle_logout(self):
        """Déconnexion"""
        reply = QMessageBox.question(
            self, "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            logger.info("Déconnexion")
            self.logout_requested.emit()
            self.close()
    
    def closeEvent(self, event):
        """Fermeture"""
        if hasattr(self, 'db_session'):
            self.db_session.close()
        event.accept()

    def show_notifications(self):
        """Affiche le menu des notifications"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 8px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 8px;
            }
            QMenu::item:selected {
                background: #f1f5f9;
            }
        """)
        
        # Notifications
        menu.addAction("📄 Nouveau contrat signé")
        menu.addAction("💰 Paiement reçu de 250 000 FCFA")
        menu.addAction("⚠️ Contrat expirant dans 30 jours")
        menu.addSeparator()
        menu.addAction("🔔 Marquer tout comme lu")
        menu.addAction("⚙️ Paramètres")
        
        menu.exec(self.notif_btn.mapToGlobal(self.notif_btn.rect().bottomLeft()))

    def show_help(self):
        """Affiche l'aide"""
        QMessageBox.information(self, "Aide", """
        <h3>Raccourcis clavier</h3>
        <ul>
            <li><b>Ctrl+D</b> - Retour au tableau de bord</li>
            <li><b>Ctrl+F</b> - Recherche</li>
            <li><b>F5</b> - Rafraîchir</li>
            <li><b>F11</b> - Plein écran</li>
            <li><b>Ctrl+Q</b> - Quitter</li>
        </ul>
        """)

    def show_user_menu(self, event):
        """Affiche le menu utilisateur"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 8px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 8px;
            }
            QMenu::item:selected {
                background: #f1f5f9;
            }
        """)
        
        menu.addAction(f"👤 {self.user.username}")
        menu.addSeparator()
        menu.addAction("⚙️ Mon profil")
        menu.addAction("🔑 Changer mot de passe")
        menu.addSeparator()
        menu.addAction("🚪 Déconnexion", self.handle_logout)
        
        menu.exec(self.user_avatar.mapToGlobal(self.user_avatar.rect().bottomLeft()))

    def setup_shortcuts(self):
        """Configure les raccourcis clavier"""
        QShortcut(QKeySequence("Ctrl+F"), self, self.focus_search)
        QShortcut(QKeySequence("F5"), self, self.refresh)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+D"), self, self.go_to_dashboard)
        QShortcut(QKeySequence("F1"), self, self.show_help)

    def update_user_avatar(self):
        """Met à jour l'avatar utilisateur"""
        initials = self.user.username[0].upper() if self.user.username else "U"
        self.user_avatar.setText(initials)

class AppController:
    """Contrôleur principal"""
    
    def __init__(self):
        init_db()
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        self.app.setStyle('Fusion')
        
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Base de données prête")
        except Exception as e:
            AlertManager.show_error(None, "Erreur DB", "L'accès à PostgreSQL a échoué.", e)
            sys.exit(1)
        
        if self.is_database_empty():
            self.show_setup()
        else:
            self.show_login()
    
    def is_database_empty(self):
        db = SessionLocal()
        try:
            return db.query(User).count() == 0
        finally:
            db.close()
    
    def show_setup(self):
        self.setup_view = SetupView()
        self.setup_ctrl = SetupController(self.setup_view)
        self.setup_ctrl.setup_finished.connect(self.show_login)
        self.setup_view.show()
    
    def show_login(self):
        if hasattr(self, 'setup_view'):
            self.setup_view.close()
        
        self.login_view = LoginView()
        self.login_ctrl = LoginController(self.login_view)
        self.login_ctrl.login_success.connect(self.launch_main_app)
        self.login_view.show()
    
    def launch_main_app(self, user):
        if hasattr(self, 'login_view'):
            self.login_view.close()
        
        self.main_window = MainWindow(user)
        self.main_window.current_user = user
        self.main_window.show()


if __name__ == "__main__":
    try:
        init_db()
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Erreur DB: {e}")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    controller = AppController()
    sys.exit(app.exec())