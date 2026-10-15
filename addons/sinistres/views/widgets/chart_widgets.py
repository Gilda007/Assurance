"""
Widgets de graphiques faits main avec QPainter
Donut, LineChart, StackedBars, Sparkline
"""
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPolygonF, QBrush
import math


# ============================================================
# DONUT CHART
# ============================================================

class DonutChart(QWidget):
    """Camembert en donut avec valeurs au centre"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []          # [(label, value, color), ...]
        self._center_text = ""
        self.setMinimumSize(200, 200)
    
    def set_data(self, data: list, center_text: str = ""):
        self._data = data
        self._center_text = center_text
        self.update()
    
    def paintEvent(self, event):
        if not self._data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        size = min(w, h) - 40
        rect = QRectF((w - size) / 2, (h - size) / 2, size, size)
        
        total = sum(v for _, v, _ in self._data)
        if total <= 0:
            return
        
        # --- Segments ---
        start = 90 * 16
        for label, value, color in self._data:
            span = -int((value / total) * 360 * 16)
            painter.setBrush(QColor(color))
            painter.setPen(QPen(QColor("white"), 3))
            painter.drawPie(rect, start, span)
            start += span
        
        # --- Trou central ---
        inner_size = size * 0.55
        inner_rect = QRectF(
            (w - inner_size) / 2, (h - inner_size) / 2,
            inner_size, inner_size
        )
        painter.setBrush(QColor("white"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(inner_rect)
        
        # --- Texte centre ---
        if self._center_text:
            painter.setPen(QColor("#1e293b"))
            font = QFont()
            font.setPointSize(12)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(inner_rect, Qt.AlignCenter, self._center_text)


# ============================================================
# LINE CHART
# ============================================================

class LineChart(QWidget):
    """Graphique en ligne simple avec aire remplie"""
    
    def __init__(self, color: str = "#3b82f6", parent=None):
        super().__init__(parent)
        self._data = []          # [v1, v2, v3, ...]
        self._labels = []        # ["2026-09-01", ...]
        self._color = color
        self.setMinimumHeight(120)
    
    def set_data(self, data: list, labels: list = None, color: str = None):
        self._data = data or []
        self._labels = labels or []
        if color:
            self._color = color
        self.update()
    
    def paintEvent(self, event):
        if len(self._data) < 2:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        margin_top, margin_bottom = 15, 25
        margin_left, margin_right = 10, 10
        
        chart_w = w - margin_left - margin_right
        chart_h = h - margin_top - margin_bottom
        
        min_v = min(self._data)
        max_v = max(self._data)
        rng = max_v - min_v if max_v != min_v else 1
        
        # --- Grille horizontale ---
        painter.setPen(QPen(QColor("#f1f5f9"), 1))
        for i in range(4):
            y = margin_top + (chart_h * i / 3)
            painter.drawLine(margin_left, int(y), w - margin_right, int(y))
        
        # --- Points ---
        points = []
        for i, v in enumerate(self._data):
            px = margin_left + (chart_w * i / (len(self._data) - 1))
            py = margin_top + chart_h - ((v - min_v) / rng) * chart_h
            points.append(QPointF(px, py))
        
        # --- Aire ---
        painter.setPen(Qt.NoPen)
        color_light = QColor(self._color)
        color_light.setAlpha(50)
        painter.setBrush(color_light)
        
        poly = QPolygonF(points + [
            QPointF(points[-1].x(), margin_top + chart_h),
            QPointF(points[0].x(), margin_top + chart_h)
        ])
        painter.drawPolygon(poly)
        
        # --- Ligne ---
        painter.setPen(QPen(QColor(self._color), 2))
        painter.setBrush(Qt.NoBrush)
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i+1])
        
        # --- Points ---
        painter.setBrush(QColor(self._color))
        painter.setPen(QPen(QColor("white"), 2))
        for p in points:
            painter.drawEllipse(p, 3, 3)
        
        # --- Labels X ---
        if self._labels:
            painter.setPen(QColor("#94a3b8"))
            font = QFont()
            font.setPointSize(7)
            painter.setFont(font)
            for i, p in enumerate(points):
                if i % max(1, len(points) // 5) == 0:
                    lbl = str(self._labels[i])[:10] if i < len(self._labels) else ""
                    painter.drawText(
                        QRectF(p.x() - 30, h - 20, 60, 15),
                        Qt.AlignCenter, lbl
                    )


# ============================================================
# STACKED BARS
# ============================================================

class StackedBarChart(QWidget):
    """Barres empilées (Reported / Reserved / Paid)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._labels = []        # ["Sept", "Oct", ...]
        self._series = []        # [{"label": "...", "color": "#...", "values": [...]}]
        self.setMinimumHeight(150)
    
    def set_data(self, labels: list, series: list):
        self._labels = labels
        self._series = series
        self.update()
    
    def paintEvent(self, event):
        if not self._series or not self._labels:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        margin_top, margin_bottom = 10, 30
        margin_left, margin_right = 10, 10
        
        chart_w = w - margin_left - margin_right
        chart_h = h - margin_top - margin_bottom
        
        n_groups = len(self._labels)
        group_w = chart_w / n_groups
        bar_w = group_w * 0.5
        bar_x_offset = (group_w - bar_w) / 2
        
        # Max total par groupe
        max_total = 0
        for i in range(n_groups):
            total = sum(s['values'][i] for s in self._series if i < len(s['values']))
            max_total = max(max_total, total)
        
        if max_total == 0:
            return
        
        # --- Barres ---
        for i in range(n_groups):
            x = margin_left + i * group_w + bar_x_offset
            y_base = margin_top + chart_h
            
            for serie in self._series:
                if i >= len(serie['values']):
                    continue
                val = serie['values'][i]
                bar_h = (val / max_total) * chart_h
                
                painter.setBrush(QColor(serie['color']))
                painter.setPen(Qt.NoPen)
                painter.drawRect(QRectF(x, y_base - bar_h, bar_w, bar_h))
                
                y_base -= bar_h
            
            # Label X
            painter.setPen(QColor("#64748b"))
            font = QFont()
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(
                QRectF(x - bar_x_offset, h - 20, group_w, 15),
                Qt.AlignCenter, self._labels[i]
            )
    
    def get_legend(self):
        """Retourne les infos pour la légende"""
        return [(s['label'], s['color']) for s in self._series]


# ============================================================
# KPI CIRCLE CARD
# ============================================================

class KpiCircleCard(QFrame):
    """Grand cercle KPI (Total Claims)"""
    
    def __init__(self, title: str, value: str, color: str = "#1a73e8", parent=None):
        super().__init__(parent)
        self._color = color
        self._value = value
        
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)
        
        # Cercle
        self.circle = CircleValue(value, color)
        self.circle.setFixedSize(120, 120)
        layout.addWidget(self.circle, alignment=Qt.AlignCenter)
        
        # Titre
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 13px; color: #64748b; font-weight: 600;")
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)


class CircleValue(QWidget):
    """Cercle avec une valeur au centre"""
    
    def __init__(self, value: str, color: str, parent=None):
        super().__init__(parent)
        self._value = value
        self._color = color
    
    def set_value(self, value: str):
        self._value = value
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        size = min(w, h) - 10
        rect = QRectF((w - size) / 2, (h - size) / 2, size, size)
        
        # Cercle externe (glow)
        color_glow = QColor(self._color)
        color_glow.setAlpha(40)
        painter.setBrush(color_glow)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect)
        
        # Cercle principal
        inner = rect.adjusted(10, 10, -10, -10)
        painter.setBrush(QColor(self._color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(inner)
        
        # Valeur
        painter.setPen(QColor("white"))
        font = QFont()
        font.setPointSize(22)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(inner, Qt.AlignCenter, self._value)