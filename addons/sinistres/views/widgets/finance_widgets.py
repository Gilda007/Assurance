"""
Widgets financiers pour le dashboard LOMETA
Résumé Financier + Pipeline Financier
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QWidget, QPushButton, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPolygonF
from PySide6.QtCore import QPointF, QRectF


# ============================================================
# CONSTANTES DE COULEUR
# ============================================================

FINANCE_COLORS = {
    'estime': {
        'bg': '#ecfdf5',       # Vert très pâle
        'border': '#d1fae5',
        'icon_bg': '#10b981',  # Vert
        'text': '#059669',
        'line': '#10b981',
    },
    'provision': {
        'bg': '#fef2f2',       # Rouge très pâle
        'border': '#fee2e2',
        'icon_bg': '#991b1b',  # Brique
        'text': '#991b1b',
        'line': '#991b1b',
    },
    'regle': {
        'bg': '#fffbeb',       # Doré très pâle
        'border': '#fef3c7',
        'icon_bg': '#d4a574',  # Doré
        'text': '#b45309',
        'line': '#d4a574',
    },
    'recours': {
        'bg': '#f1f5f9',       # Gris très pâle
        'border': '#e2e8f0',
        'icon_bg': '#334155',  # Ardoise
        'text': '#1e293b',
        'line': '#334155',
    },
}


# ============================================================
# MINI SPARKLINE (courbe) POUR TUILE ESTIMÉ
# ============================================================

# class SparklineWidget(QWidget):
#     """Mini-courbe verte avec aire remplie"""
    
#     def __init__(self, color: str = "#10b981", parent=None):
#         super().__init__(parent)
#         self._color = color
#         self._data = []
#         self.setFixedHeight(35)
    
#     def set_data(self, data: list, color: str = None):
#         self._data = data or []
#         if color:
#             self._color = color
#         self.update()
    
#     def paintEvent(self, event):
#         if len(self._data) < 2:
#             return
        
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.Antialiasing)
        
#         w, h = self.width(), self.height()
#         min_v = min(self._data)
#         max_v = max(self._data)
#         rng = max_v - min_v if max_v != min_v else 1
        
#         points = []
#         for i, v in enumerate(self._data):
#             px = (w * i) / (len(self._data) - 1)
#             py = h - ((v - min_v) / rng) * (h - 6) - 3
#             points.append(QPointF(px, py))
        
#         # Aire
#         painter.setPen(Qt.NoPen)
#         color_light = QColor(self._color)
#         color_light.setAlpha(60)
#         painter.setBrush(color_light)
        
#         poly = QPolygonF(points + [
#             QPointF(points[-1].x(), h),
#             QPointF(points[0].x(), h)
#         ])
#         painter.drawPolygon(poly)
        
#         # Ligne
#         painter.setPen(QPen(QColor(self._color), 1.5))
#         for i in range(len(points) - 1):
#             painter.drawLine(points[i], points[i + 1])

class SparklineWidget(QWidget):
    """Mini-courbe compacte (22px de haut)"""
    
    def __init__(self, color: str = "#10b981", parent=None):
        super().__init__(parent)
        self._color = color
        self._data = []
        self.setFixedHeight(22)
        self.setFixedWidth(70)
    
    def set_data(self, data: list, color: str = None):
        self._data = data or []
        if color:
            self._color = color
        self.update()
    
    def paintEvent(self, event):
        if len(self._data) < 2:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        min_v = min(self._data)
        max_v = max(self._data)
        rng = max_v - min_v if max_v != min_v else 1
        
        points = []
        for i, v in enumerate(self._data):
            px = (w * i) / (len(self._data) - 1)
            py = h - ((v - min_v) / rng) * (h - 4) - 2
            points.append(QPointF(px, py))
        
        # Aire
        painter.setPen(Qt.NoPen)
        color_light = QColor(self._color)
        color_light.setAlpha(60)
        painter.setBrush(color_light)
        
        poly = QPolygonF(points + [
            QPointF(points[-1].x(), h),
            QPointF(points[0].x(), h)
        ])
        painter.drawPolygon(poly)
        
        # Ligne
        painter.setPen(QPen(QColor(self._color), 1.2))
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])

# ============================================================
# MINI BARS POUR TUILE RECOURS
# ============================================================

# class MiniBarsWidget(QWidget):
#     """Mini-barres verticales grises"""
    
#     def __init__(self, color: str = "#334155", parent=None):
#         super().__init__(parent)
#         self._color = color
#         self._data = []
#         self.setFixedHeight(35)
    
#     def set_data(self, data: list, color: str = None):
#         self._data = data or []
#         if color:
#             self._color = color
#         self.update()
    
#     def paintEvent(self, event):
#         if not self._data:
#             return
        
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.Antialiasing)
        
#         w, h = self.width(), self.height()
#         max_v = max(self._data) if max(self._data) > 0 else 1
        
#         n = len(self._data)
#         gap = 3
#         bar_w = (w - (n - 1) * gap) / n
        
#         painter.setPen(Qt.NoPen)
#         painter.setBrush(QColor(self._color))
        
#         for i, v in enumerate(self._data):
#             bar_h = (v / max_v) * (h - 4)
#             x = i * (bar_w + gap)
#             y = h - bar_h
#             painter.drawRect(QRectF(x, y, bar_w, bar_h))


class MiniBarsWidget(QWidget):
    """Mini-barres compactes (22px de haut)"""
    
    def __init__(self, color: str = "#334155", parent=None):
        super().__init__(parent)
        self._color = color
        self._data = []
        self.setFixedHeight(22)
        self.setFixedWidth(70)
    
    def set_data(self, data: list, color: str = None):
        self._data = data or []
        if color:
            self._color = color
        self.update()
    
    def paintEvent(self, event):
        if not self._data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        max_v = max(self._data) if max(self._data) > 0 else 1
        
        n = len(self._data)
        gap = 2
        bar_w = (w - (n - 1) * gap) / n
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(self._color))
        
        for i, v in enumerate(self._data):
            bar_h = (v / max_v) * (h - 2)
            x = i * (bar_w + gap)
            y = h - bar_h
            painter.drawRect(QRectF(x, y, bar_w, bar_h))

# ============================================================
# TUILE FINANCIÈRE (icône + label + valeur + graphique)
# ============================================================

# class FinanceTile(QFrame):
#     """
#     Tuile financière individuelle
#     ┌──────────────────────────────────┐
#     │ ● [icône]  (Label)               │
#     │                                   │
#     │  0 FCFA           [sparkline]    │
#     └──────────────────────────────────┘
#     """
    
#     def __init__(self, label: str, icon_text: str, color_key: str, parent=None):
#         super().__init__(parent)
        
#         self.color_key = color_key
#         colors = FINANCE_COLORS[color_key]
        
#         # Style du cadre
#         self.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {colors['bg']};
#                 border: 1px solid {colors['border']};
#                 border-radius: 12px;
#             }}
#         """)
        
#         self.setMinimumHeight(50)
        
#         # --- Layout principal ---
#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(16, 12, 16, 12)
#         main_layout.setSpacing(8)
        
#         # ============================================================
#         # Ligne 1 : pastille + icône + label
#         # ============================================================
#         header = QHBoxLayout()
#         header.setSpacing(8)
        
#         # Pastille colorée
#         dot = QLabel("●")
#         dot.setStyleSheet(f"color: {colors['icon_bg']}; font-size: 12px;")
#         dot.setFixedWidth(10)
#         header.addWidget(dot)
        
#         # Icône dans cercle coloré
#         icon_container = QFrame()
#         icon_container.setFixedSize(34, 34)
#         icon_container.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {colors['icon_bg']};
#                 border-radius: 17px;
#             }}
#         """)
#         icon_layout = QVBoxLayout(icon_container)
#         icon_layout.setContentsMargins(0, 0, 0, 0)
#         icon_lbl = QLabel(icon_text)
#         icon_lbl.setStyleSheet("font-size: 16px; color: white; background: transparent;")
#         icon_lbl.setAlignment(Qt.AlignCenter)
#         icon_layout.addWidget(icon_lbl)
#         header.addWidget(icon_container)
        
#         # Label
#         label_lbl = QLabel(f"({label})")
#         label_lbl.setStyleSheet(f"""
#             color: {colors['text']};
#             font-size: 13px;
#             font-weight: 600;
#         """)
#         header.addWidget(label_lbl)
#         header.addStretch()
        
#         main_layout.addLayout(header)
        
#         # ============================================================
#         # Ligne 2 : valeur + graphique
#         # ============================================================
#         body = QHBoxLayout()
#         body.setSpacing(10)
        
#         # Valeur
#         self.value_label = QLabel("0 FCFA")
#         self.value_label.setStyleSheet("""
#             color: #1e293b;
#             font-size: 22px;
#             font-weight: bold;
#         """)
#         body.addWidget(self.value_label)
        
#         body.addStretch()
        
#         # Zone graphique (sera remplacée par Sparkline ou MiniBars)
#         self.chart_widget = None
#         self.chart_placeholder = QLabel()
#         self.chart_placeholder.setFixedSize(90, 35)
#         self.chart_placeholder.setStyleSheet("background-color: transparent;")
#         body.addWidget(self.chart_placeholder)
        
#         main_layout.addLayout(body)
    
#     def set_chart(self, widget: QWidget):
#         """Remplace le placeholder par le graphique réel"""
#         if self.chart_widget:
#             self.chart_widget.deleteLater()
        
#         # Retirer le placeholder du layout
#         parent_layout = self.chart_placeholder.parentWidget().layout()
#         if parent_layout:
#             # Trouver le body layout et remplacer
#             pass
        
#         widget.setFixedSize(90, 35)
#         self.chart_widget = widget
#         # Insérer le widget au même endroit que le placeholder
#         # (plus simple : cacher le placeholder et ajouter le widget à côté)
#         self.chart_placeholder.hide()
        
#         # Trouver le body layout
#         for i in range(self.layout().count()):
#             item = self.layout().itemAt(i)
#             if item and item.layout():
#                 # Chercher le HBoxLayout
#                 sub_layout = item.layout()
#                 sub_layout.addWidget(widget)
#                 break
    
#     def set_value(self, value: str):
#         """Met à jour la valeur"""
#         self.value_label.setText(value)

class FinanceTile(QFrame):
    """Tuile financière compacte"""
    
    def __init__(self, label: str, icon_text: str, color_key: str, parent=None):
        super().__init__(parent)
        
        self.color_key = color_key
        colors = FINANCE_COLORS[color_key]
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['bg']};
                border: 1px solid {colors['border']};
                border-radius: 10px;
            }}
        """)
        
        self.setMinimumHeight(65)
        self.setMaximumHeight(75)
        
        # --- Layout principal ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(4)
        
        # ============================================================
        # Ligne 1 : pastille + icône + label
        # ============================================================
        header = QHBoxLayout()
        header.setSpacing(5)
        
        # Pastille
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {colors['icon_bg']}; font-size: 8px;")
        dot.setFixedWidth(8)
        header.addWidget(dot)
        
        # Icône (24×24 au lieu de 34×34)
        icon_container = QFrame()
        icon_container.setFixedSize(22, 22)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['icon_bg']};
                border-radius: 11px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel(icon_text)
        icon_lbl.setStyleSheet("font-size: 11px; color: white; background: transparent;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_lbl)
        header.addWidget(icon_container)
        
        # Label (plus petit)
        label_lbl = QLabel(label)
        label_lbl.setStyleSheet(f"""
            color: {colors['text']};
            font-size: 11px;
            font-weight: 600;
        """)
        header.addWidget(label_lbl)
        header.addStretch()
        
        main_layout.addLayout(header)
        
        # ============================================================
        # Ligne 2 : valeur + graphique
        # ============================================================
        body = QHBoxLayout()
        body.setSpacing(6)
        body.setContentsMargins(0, 0, 0, 0)
        
        # Valeur (plus petite)
        self.value_label = QLabel("0 FCFA")
        self.value_label.setStyleSheet("""
            color: #1e293b;
            font-size: 15px;
            font-weight: bold;
        """)
        body.addWidget(self.value_label)
        
        body.addStretch()
        
        # Zone graphique (placeholer)
        self.chart_widget = None
        self.chart_placeholder = QLabel()
        self.chart_placeholder.setFixedSize(70, 22)
        self.chart_placeholder.setStyleSheet("background-color: transparent;")
        body.addWidget(self.chart_placeholder)
        
        main_layout.addLayout(body)
    
    def set_chart(self, widget: QWidget):
        """Remplace le placeholder par le graphique réel"""
        if self.chart_widget:
            self.chart_widget.deleteLater()
        
        widget.setFixedSize(70, 22)
        self.chart_widget = widget
        self.chart_placeholder.hide()
        
        # Ajouter au body layout
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.layout():
                item.layout().addWidget(widget)
                break
    
    def set_value(self, value: str):
        self.value_label.setText(value)

# ============================================================
# LIGNE DE PIPELINE
# ============================================================

# class PipelineRow(QWidget):
#     """Ligne du pipeline financier"""
    
#     def __init__(self, label: str, color: str, parent=None):
#         super().__init__(parent)
        
#         self._color = color
#         self._percent = 0
        
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(0, 8, 0, 8)
#         layout.setSpacing(6)
        
#         # --- Ligne : label + valeur ---
#         header = QHBoxLayout()
        
#         self.label_lbl = QLabel(label)
#         self.label_lbl.setStyleSheet("""
#             color: #1e293b;
#             font-size: 13px;
#             font-weight: 500;
#         """)
#         header.addWidget(self.label_lbl)
#         header.addStretch()
        
#         self.value_lbl = QLabel("0 FCFA")
#         self.value_lbl.setStyleSheet(f"""
#             color: {color};
#             font-size: 13px;
#             font-weight: bold;
#         """)
#         header.addWidget(self.value_lbl)
        
#         layout.addLayout(header)
        
#         # --- Ligne : barre de progression + % ---
#         progress_row = QHBoxLayout()
#         progress_row.setSpacing(8)
        
#         self.progress = ProgressBarHorizontal(color=color)
#         progress_row.addWidget(self.progress, 1)
        
#         self.percent_lbl = QLabel("0%")
#         self.percent_lbl.setStyleSheet(f"""
#             color: {color};
#             font-size: 11px;
#             font-weight: bold;
#         """)
#         self.percent_lbl.setFixedWidth(40)
#         self.percent_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
#         progress_row.addWidget(self.percent_lbl)
        
#         layout.addLayout(progress_row)
    
#     def set_data(self, value: float, percent: float):
#         """Met à jour la ligne"""
#         self.value_lbl.setText(f"{value:,.0f} FCFA".replace(",", " "))
#         self.percent_lbl.setText(f"{int(percent)}%")
#         self.progress.set_percent(percent)


# ============================================================
# BARRE DE PROGRESSION HORIZONTALE
# ============================================================

# class ProgressBarHorizontal(QWidget):
#     """Barre de progression horizontale fine"""
    
#     def __init__(self, color: str = "#3b82f6", height: int = 8, parent=None):
#         super().__init__(parent)
#         self._color = color
#         self._percent = 0
#         self._bar_height = height
#         self.setFixedHeight(height + 2)
    
#     def set_percent(self, percent: float):
#         self._percent = max(0.0, min(100.0, percent))
#         self.update()
    
#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.Antialiasing)
        
#         w = self.width()
#         h = self._bar_height
#         y = (self.height() - h) / 2
#         radius = h / 2
        
#         # Fond gris
#         painter.setPen(Qt.NoPen)
#         painter.setBrush(QColor("#e2e8f0"))
#         painter.drawRoundedRect(QRectF(0, y, w, h), radius, radius)
        
#         # Remplissage
#         if self._percent > 0:
#             fill_w = (w * self._percent) / 100.0
#             if fill_w < h:
#                 fill_w = h  # minimum visuel
            
#             painter.setBrush(QColor(self._color))
#             painter.drawRoundedRect(QRectF(0, y, fill_w, h), radius, radius)


class ProgressBarHorizontal(QWidget):
    """Barre de progression compacte"""
    
    def __init__(self, color: str = "#3b82f6", height: int = 6, parent=None):
        super().__init__(parent)
        self._color = color
        self._percent = 0
        self._bar_height = height
        self.setFixedHeight(height + 2)
    
    def set_percent(self, percent: float):
        self._percent = max(0.0, min(100.0, percent))
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self._bar_height
        y = (self.height() - h) / 2
        radius = h / 2
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#e2e8f0"))
        painter.drawRoundedRect(QRectF(0, y, w, h), radius, radius)
        
        if self._percent > 0:
            fill_w = (w * self._percent) / 100.0
            if fill_w < h:
                fill_w = h
            
            painter.setBrush(QColor(self._color))
            painter.drawRoundedRect(QRectF(0, y, fill_w, h), radius, radius)

# ============================================================
# CARTE RÉSUMÉ FINANCIER
# ============================================================

# class FinanceSummaryCard(QFrame):
#     """Carte Résumé Financier avec 4 tuiles"""
    
#     def __init__(self, parent=None):
#         super().__init__(parent)
        
#         self.setStyleSheet("""
#             QFrame#FinanceSummaryCard {
#                 background-color: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 16px;
#             }
#         """)
#         self.setObjectName("FinanceSummaryCard")
        
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(20, 18, 20, 18)
#         layout.setSpacing(15)
        
#         # ============================================================
#         # En-tête : icône 💰 + titre + menu ⋮
#         # ============================================================
#         header = QHBoxLayout()
#         header.setSpacing(8)
        
#         icon = QLabel("💰")
#         icon.setStyleSheet("font-size: 20px;")
#         header.addWidget(icon)
        
#         title = QLabel("Résumé Financier")
#         title.setStyleSheet("""
#             font-size: 16px;
#             font-weight: bold;
#             color: #1e293b;
#         """)
#         header.addWidget(title)
#         header.addStretch()
        
#         # Bouton menu ⋮
#         btn_menu = QPushButton("⋮")
#         btn_menu.setFixedSize(32, 32)
#         btn_menu.setCursor(Qt.PointingHandCursor)
#         btn_menu.setStyleSheet("""
#             QPushButton {
#                 background-color: #f1f5f9;
#                 border: none;
#                 border-radius: 8px;
#                 font-size: 16px;
#                 color: #64748b;
#             }
#             QPushButton:hover {
#                 background-color: #e2e8f0;
#             }
#         """)
#         header.addWidget(btn_menu)
        
#         layout.addLayout(header)
        
#         # ============================================================
#         # Grille 2×2 des tuiles
#         # ============================================================
#         grid = QGridLayout()
#         grid.setSpacing(12)
        
#         # Tuile 1 : Total Estimé (graphique courbe)
#         self.tile_estime = FinanceTile(
#             label="Total Estimé",
#             icon_text="📊",
#             color_key="estime"
#         )
#         self.spark_estime = SparklineWidget(color="#10b981")
#         self.tile_estime.set_chart(self.spark_estime)
#         self.spark_estime.set_data([0, 1, 0.5, 2, 1.5, 2.5, 2])
        
#         # Tuile 2 : Provisions (ligne simple)
#         self.tile_provision = FinanceTile(
#             label="Provisions",
#             icon_text="🛡️",
#             color_key="provision"
#         )
        
#         # Tuile 3 : Total Réglé (ligne dorée)
#         self.tile_regle = FinanceTile(
#             label="Total Réglé",
#             icon_text="💳",
#             color_key="regle"
#         )
        
#         # Tuile 4 : Recours (mini-barres)
#         self.tile_recours = FinanceTile(
#             label="Recours",
#             icon_text="⚖️",
#             color_key="recours"
#         )
#         self.bars_recours = MiniBarsWidget(color="#334155")
#         self.tile_recours.set_chart(self.bars_recours)
#         self.bars_recours.set_data([2, 4, 3, 5, 4, 6, 5])
        
#         grid.addWidget(self.tile_estime, 0, 0)
#         grid.addWidget(self.tile_provision, 0, 1)
#         grid.addWidget(self.tile_regle, 1, 0)
#         grid.addWidget(self.tile_recours, 1, 1)
        
#         layout.addLayout(grid)
    
#     # ============================================================
#     # MISE À JOUR
#     # ============================================================
    
#     def set_data(self, data: dict):
#         """
#         Met à jour les 4 tuiles.
#         data = {
#             'estime': float,
#             'provision': float,
#             'regle': float,
#             'recours': float,
#         }
#         """
#         estime = data.get('estime', 0) or 0
#         provision = data.get('provision', 0) or 0
#         regle = data.get('regle', 0) or 0
#         recours = data.get('recours', 0) or 0
        
#         self.tile_estime.set_value(f"{estime:,.0f} FCFA".replace(",", " "))
#         self.tile_provision.set_value(f"{provision:,.0f} FCFA".replace(",", " "))
#         self.tile_regle.set_value(f"{regle:,.0f} FCFA".replace(",", " "))
#         self.tile_recours.set_value(f"{recours:,.0f} FCFA".replace(",", " "))

class FinanceSummaryCard(QFrame):
    """Carte Résumé Financier compacte"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QFrame#FinanceSummaryCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        self.setObjectName("FinanceSummaryCard")

        # ============================================================
        # ✅ Effet d'ombrage subtil
        # ============================================================
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(15, 23, 42, 30))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        
        # ============================================================
        # En-tête
        # ============================================================
        header = QHBoxLayout()
        header.setSpacing(6)
        
        icon = QLabel("💰")
        icon.setStyleSheet("font-size: 15px;")
        header.addWidget(icon)
        
        title = QLabel("Résumé Financier")
        title.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #1e293b;
        """)
        header.addWidget(title)
        header.addStretch()
        
        btn_menu = QPushButton("⋮")
        btn_menu.setFixedSize(24, 24)
        btn_menu.setCursor(Qt.PointingHandCursor)
        btn_menu.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                color: #64748b;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        header.addWidget(btn_menu)
        
        layout.addLayout(header)
        
        # ============================================================
        # Grille 2×2 compacte
        # ============================================================
        grid = QGridLayout()
        grid.setSpacing(8)
        
        self.tile_estime = FinanceTile("Total Estimé", "📊", "estime")
        self.spark_estime = SparklineWidget(color="#10b981")
        self.tile_estime.set_chart(self.spark_estime)
        self.spark_estime.set_data([0, 1, 0.5, 2, 1.5, 2.5, 2])
        
        self.tile_provision = FinanceTile("Provisions", "🛡️", "provision")
        self.tile_regle = FinanceTile("Total Réglé", "💳", "regle")
        
        self.tile_recours = FinanceTile("Recours", "⚖️", "recours")
        self.bars_recours = MiniBarsWidget(color="#334155")
        self.tile_recours.set_chart(self.bars_recours)
        self.bars_recours.set_data([2, 4, 3, 5, 4, 6, 5])
        
        grid.addWidget(self.tile_estime, 0, 0)
        grid.addWidget(self.tile_provision, 0, 1)
        grid.addWidget(self.tile_regle, 1, 0)
        grid.addWidget(self.tile_recours, 1, 1)
        
        layout.addLayout(grid)
    
    def set_data(self, data: dict):
        estime = data.get('estime', 0) or 0
        provision = data.get('provision', 0) or 0
        regle = data.get('regle', 0) or 0
        recours = data.get('recours', 0) or 0
        
        self.tile_estime.set_value(f"{estime:,.0f} FCFA".replace(",", " "))
        self.tile_provision.set_value(f"{provision:,.0f} FCFA".replace(",", " "))
        self.tile_regle.set_value(f"{regle:,.0f} FCFA".replace(",", " "))
        self.tile_recours.set_value(f"{recours:,.0f} FCFA".replace(",", " "))

# ============================================================
# CARTE PIPELINE FINANCIER
# ============================================================

# class FinancePipelineCard(QFrame):
#     """Carte Pipeline Financier avec 4 barres horizontales"""
    
#     def __init__(self, parent=None):
#         super().__init__(parent)
        
#         self.setStyleSheet("""
#             QFrame#FinancePipelineCard {
#                 background-color: white;
#                 border: 1px solid #e2e8f0;
#                 border-radius: 16px;
#             }
#         """)
#         self.setObjectName("FinancePipelineCard")
        
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(20, 18, 20, 18)
#         layout.setSpacing(15)
        
#         # ============================================================
#         # En-tête : icône 📈 + titre + menu ⋮
#         # ============================================================
#         header = QHBoxLayout()
#         header.setSpacing(8)
        
#         icon = QLabel("📈")
#         icon.setStyleSheet("font-size: 20px;")
#         header.addWidget(icon)
        
#         title = QLabel("Pipeline Financier")
#         title.setStyleSheet("""
#             font-size: 16px;
#             font-weight: bold;
#             color: #1e293b;
#         """)
#         header.addWidget(title)
#         header.addStretch()
        
#         btn_menu = QPushButton("⋮")
#         btn_menu.setFixedSize(32, 32)
#         btn_menu.setCursor(Qt.PointingHandCursor)
#         btn_menu.setStyleSheet("""
#             QPushButton {
#                 background-color: #f1f5f9;
#                 border: none;
#                 border-radius: 8px;
#                 font-size: 16px;
#                 color: #64748b;
#             }
#             QPushButton:hover {
#                 background-color: #e2e8f0;
#             }
#         """)
#         header.addWidget(btn_menu)
        
#         layout.addLayout(header)
        
#         # ============================================================
#         # Lignes du pipeline
#         # ============================================================
#         self.rows_container = QVBoxLayout()
#         self.rows_container.setSpacing(4)
        
#         # Créer les 4 lignes
#         self.row_estime = PipelineRow("Estimé", "#3b82f6")
#         self.row_provision = PipelineRow("Provisionné", "#991b1b")
#         self.row_regle = PipelineRow("Réglé", "#d4a574")
#         self.row_recours = PipelineRow("Récupéré (recours)", "#334155")
        
#         self.rows_container.addWidget(self.row_estime)
#         self.rows_container.addWidget(self._make_separator())
#         self.rows_container.addWidget(self.row_provision)
#         self.rows_container.addWidget(self._make_separator())
#         self.rows_container.addWidget(self.row_regle)
#         self.rows_container.addWidget(self._make_separator())
#         self.rows_container.addWidget(self.row_recours)
        
#         layout.addLayout(self.rows_container)
        
#         # ============================================================
#         # Pied : période + dernière MAJ
#         # ============================================================
#         footer = QHBoxLayout()
        
#         self.lbl_period = QLabel("Période : —")
#         self.lbl_period.setStyleSheet("font-size: 11px; color: #64748b;")
#         footer.addWidget(self.lbl_period)
        
#         footer.addStretch()
        
#         self.lbl_updated = QLabel("Mise à jour le —")
#         self.lbl_updated.setStyleSheet("font-size: 11px; color: #64748b;")
#         footer.addWidget(self.lbl_updated)
        
#         layout.addLayout(footer)
    
#     def _make_separator(self) -> QFrame:
#         sep = QFrame()
#         sep.setFrameShape(QFrame.HLine)
#         sep.setStyleSheet("background-color: #f1f5f9; max-height: 1px; border: none;")
#         return sep
    
#     # ============================================================
#     # MISE À JOUR
#     # ============================================================
    
#     def set_data(self, data: dict, period: str = None):
#         """
#         Met à jour les 4 lignes.
#         data = {
#             'estime': float,
#             'provision': float,
#             'regle': float,
#             'recours': float,
#         }
#         """
#         estime = data.get('estime', 0) or 0
#         provision = data.get('provision', 0) or 0
#         regle = data.get('regle', 0) or 0
#         recours = data.get('recours', 0) or 0
        
#         # Calcul des pourcentages (base = estimé)
#         base = estime if estime > 0 else 1
#         pct_provision = (provision / base) * 100
#         pct_regle = (regle / base) * 100
#         pct_recours = (recours / base) * 100
        
#         self.row_estime.set_data(estime, 100 if estime > 0 else 0)
#         self.row_provision.set_data(provision, pct_provision)
#         self.row_regle.set_data(regle, pct_regle)
#         self.row_recours.set_data(recours, pct_recours)
        
#         # Pied
#         if period:
#             self.lbl_period.setText(f"Période : {period}")
#         else:
#             from datetime import datetime
#             now = datetime.now()
#             trimestre = (now.month - 1) // 3 + 1
#             self.lbl_period.setText(f"Période : T{trimestre} {now.year}")
        
#         from datetime import datetime
#         mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
#                 'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc']
#         now = datetime.now()
#         self.lbl_updated.setText(
#             f"Mise à jour le {now.day} {mois[now.month - 1]}. {now.year}"
#         )


class PipelineRow(QWidget):
    """Ligne du pipeline financier compacte"""
    
    def __init__(self, label: str, color: str, parent=None):
        super().__init__(parent)
        
        self._color = color
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(3)
        
        # Ligne : label + valeur
        header = QHBoxLayout()
        
        self.label_lbl = QLabel(label)
        self.label_lbl.setStyleSheet("""
            color: #475569;
            font-size: 11px;
            font-weight: 500;
        """)
        header.addWidget(self.label_lbl)
        header.addStretch()
        
        self.value_lbl = QLabel("0 FCFA")
        self.value_lbl.setStyleSheet(f"""
            color: {color};
            font-size: 11px;
            font-weight: bold;
        """)
        header.addWidget(self.value_lbl)
        
        layout.addLayout(header)
        
        # Barre + %
        progress_row = QHBoxLayout()
        progress_row.setSpacing(6)
        
        self.progress = ProgressBarHorizontal(color=color, height=6)
        progress_row.addWidget(self.progress, 1)
        
        self.percent_lbl = QLabel("0%")
        self.percent_lbl.setStyleSheet(f"""
            color: {color};
            font-size: 10px;
            font-weight: bold;
        """)
        self.percent_lbl.setFixedWidth(30)
        self.percent_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        progress_row.addWidget(self.percent_lbl)
        
        layout.addLayout(progress_row)
    
    def set_data(self, value: float, percent: float):
        self.value_lbl.setText(f"{value:,.0f} FCFA".replace(",", " "))
        self.percent_lbl.setText(f"{int(percent)}%")
        self.progress.set_percent(percent)


class FinancePipelineCard(QFrame):
    """Carte Pipeline Financier compacte"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QFrame#FinancePipelineCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        self.setObjectName("FinancePipelineCard")

        # ============================================================
        # ✅ Effet d'ombrage subtil
        # ============================================================
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(15, 23, 42, 30))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        
        # ============================================================
        # En-tête
        # ============================================================
        header = QHBoxLayout()
        header.setSpacing(6)
        
        icon = QLabel("📈")
        icon.setStyleSheet("font-size: 15px;")
        header.addWidget(icon)
        
        title = QLabel("Pipeline Financier")
        title.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #1e293b;
        """)
        header.addWidget(title)
        header.addStretch()
        
        btn_menu = QPushButton("⋮")
        btn_menu.setFixedSize(24, 24)
        btn_menu.setCursor(Qt.PointingHandCursor)
        btn_menu.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                color: #64748b;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        header.addWidget(btn_menu)
        
        layout.addLayout(header)
        
        # ============================================================
        # Lignes du pipeline (compactes)
        # ============================================================
        self.rows_container = QVBoxLayout()
        self.rows_container.setSpacing(2)
        
        self.row_estime = PipelineRow("Estimé", "#3b82f6")
        self.row_provision = PipelineRow("Provisionné", "#991b1b")
        self.row_regle = PipelineRow("Réglé", "#d4a574")
        self.row_recours = PipelineRow("Récupéré (recours)", "#334155")
        
        self.rows_container.addWidget(self.row_estime)
        self.rows_container.addWidget(self._make_separator())
        self.rows_container.addWidget(self.row_provision)
        self.rows_container.addWidget(self._make_separator())
        self.rows_container.addWidget(self.row_regle)
        self.rows_container.addWidget(self._make_separator())
        self.rows_container.addWidget(self.row_recours)
        
        layout.addLayout(self.rows_container)
        
        # ============================================================
        # Pied : période + dernière MAJ
        # ============================================================
        footer = QHBoxLayout()
        
        self.lbl_period = QLabel("Période : —")
        self.lbl_period.setStyleSheet("font-size: 10px; color: #94a3b8;")
        footer.addWidget(self.lbl_period)
        
        footer.addStretch()
        
        self.lbl_updated = QLabel("Mise à jour le —")
        self.lbl_updated.setStyleSheet("font-size: 10px; color: #94a3b8;")
        footer.addWidget(self.lbl_updated)
        
        layout.addLayout(footer)
    
    def _make_separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #f1f5f9; max-height: 1px; border: none;")
        return sep
    
    def set_data(self, data: dict, period: str = None):
        estime = data.get('estime', 0) or 0
        provision = data.get('provision', 0) or 0
        regle = data.get('regle', 0) or 0
        recours = data.get('recours', 0) or 0
        
        base = estime if estime > 0 else 1
        pct_provision = (provision / base) * 100
        pct_regle = (regle / base) * 100
        pct_recours = (recours / base) * 100
        
        self.row_estime.set_data(estime, 100 if estime > 0 else 0)
        self.row_provision.set_data(provision, pct_provision)
        self.row_regle.set_data(regle, pct_regle)
        self.row_recours.set_data(recours, pct_recours)
        
        if period:
            self.lbl_period.setText(f"Période : {period}")
        else:
            from datetime import datetime
            now = datetime.now()
            trimestre = (now.month - 1) // 3 + 1
            self.lbl_period.setText(f"Période : T{trimestre} {now.year}")
        
        from datetime import datetime
        mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc']
        now = datetime.now()
        self.lbl_updated.setText(
            f"Mise à jour le {now.day} {mois[now.month - 1]}. {now.year}"
        )