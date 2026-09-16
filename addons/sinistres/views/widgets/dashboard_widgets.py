"""
Widgets réutilisables pour les tableaux de bord
KpiCard, ProgressBicolor, Gauge, PieChart, MapPlaceholder
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath

from typing import Optional, List, Tuple


# ============================================================
# KPI CARD avec mini-graphe (sparkline)
# ============================================================

class KpiCard(QFrame):
    """Carte KPI avec titre, valeur et mini-graphe"""
    
    def __init__(self, title: str, value: str = "0", color: str = "#1a73e8", parent=None):
        super().__init__(parent)
        self._color = color
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
        """)
        self.setMinimumHeight(110)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # Titre
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600;")
        layout.addWidget(self.lbl_title)
        
        # Valeur
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {color};")
        layout.addWidget(self.lbl_value)
        
        # Zone sparkline (dessinée dans paintEvent)
        self._sparkline_data: List[float] = []
        layout.addStretch()
    
    def set_value(self, value: str):
        self.lbl_value.setText(value)
    
    def set_sparkline(self, data: List[float]):
        """Définit les données du mini-graphe"""
        self._sparkline_data = data
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._sparkline_data or len(self._sparkline_data) < 2:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Zone du graphe (bas de la carte)
        w = self.width() - 30
        h = 25
        x0 = 15
        y0 = self.height() - h - 8
        
        # Normaliser
        min_v = min(self._sparkline_data)
        max_v = max(self._sparkline_data)
        rng = max_v - min_v if max_v != min_v else 1
        
        points = []
        for i, v in enumerate(self._sparkline_data):
            px = x0 + (w * i / (len(self._sparkline_data) - 1))
            py = y0 + h - ((v - min_v) / rng) * h
            points.append(QPointF(px, py))
        
        # Ligne
        pen = QPen(QColor(self._color), 2)
        painter.setPen(pen)
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i+1])


# ============================================================
# BARRE DE PROGRESSION BICOLORE (payé / reste)
# ============================================================

class ProgressBicolor(QFrame):
    """Barre de progression avec 2 segments colorés"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._percent = 0
        self._color1 = "#22c55e"   # payé
        self._color2 = "#f59e0b"   # reste
        self.setMinimumHeight(10)
        self.setMaximumHeight(10)
    
    def set_values(self, percent: float, color1: str = "#22c55e", color2: str = "#f59e0b"):
        self._percent = max(0, min(100, percent))
        self._color1 = color1
        self._color2 = color2
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        radius = h / 2
        
        # Segment coloré (payé)
        paid_w = int(w * self._percent / 100)
        path1 = QPainterPath()
        path1.addRoundedRect(0, 0, paid_w, h, radius, radius)
        painter.fillPath(path1, QColor(self._color1))
        
        # Segment restant
        if paid_w < w:
            path2 = QPainterPath()
            path2.addRoundedRect(paid_w, 0, w - paid_w, h, radius, radius)
            painter.fillPath(path2, QColor(self._color2))


# ============================================================
# JAUGE DEMI-CERCLE
# ============================================================

class GaugeWidget(QWidget):
    """Jauge demi-cercle avec zones colorées (vert/orange/rouge)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._max = 100
        self.setMinimumSize(180, 110)
    
    def set_value(self, value: float, max_val: float = 100):
        self._value = max(0, min(max_val, value))
        self._max = max_val if max_val > 0 else 100
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        rect = QRectF(20, 20, w - 40, (h - 20) * 2)
        
        # Fond gris
        pen_bg = QPen(QColor("#e2e8f0"), 18, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 180 * 16, -180 * 16)
        
        # Zones colorées (vert, orange, rouge) — petit indicateur visuel
        zones = [
            (0, 40, "#22c55e"),      # 0-40% vert
            (40, 70, "#f59e0b"),     # 40-70% orange
            (70, 100, "#ef4444"),    # 70-100% rouge
        ]
        
        for start, end, color in zones:
            span = (end - start) / 100
            start_angle = 180 - (start / 100 * 180)
            span_angle = -int(span * 180)
            
            pen = QPen(QColor(color), 18, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rect, int(start_angle * 16), int(span_angle * 16))
        
        # Aiguille
        ratio = self._value / self._max
        angle_deg = 180 - ratio * 180
        import math
        angle_rad = math.radians(angle_deg)
        
        cx = w / 2
        cy = 20 + (h - 20)  # bas du cercle
        length = (w - 40) / 2 - 10
        
        end_x = cx + length * math.cos(angle_rad)
        end_y = cy - length * math.sin(angle_rad)
        
        painter.setPen(QPen(QColor("#1e293b"), 3, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(cx, cy), QPointF(end_x, end_y))
        
        # Point central
        painter.setBrush(QBrush(QColor("#1e293b")))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), 5, 5)


# ============================================================
# CAMEMBERT (simplifié)
# ============================================================

class PieChartWidget(QWidget):
    """Camembert simple"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: List[Tuple[str, float, str]] = []
        self.setMinimumSize(200, 200)
    
    def set_data(self, data: List[Tuple[str, float, str]]):
        """data = [(label, value, color), ...]"""
        self._data = data
        self.update()
    
    def paintEvent(self, event):
        if not self._data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        total = sum(v for _, v, _ in self._data)
        if total <= 0:
            return
        
        w = self.width()
        h = self.height()
        size = min(w, h) - 20
        rect = QRectF((w - size) / 2, (h - size) / 2, size, size)
        
        start_angle = 90 * 16  # démarre en haut
        for label, value, color in self._data:
            span = -int((value / total) * 360 * 16)
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor("white"), 2))
            painter.drawPie(rect, start_angle, span)
            start_angle += span


# ============================================================
# PLACEHOLDER CARTE
# ============================================================

class MapPlaceholder(QFrame):
    """Placeholder pour carte géographique"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        self.setMinimumHeight(250)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.lbl_icon = QLabel("🗺️")
        self.lbl_icon.setStyleSheet("font-size: 48px;")
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_icon)
        
        self.lbl_text = QLabel("Carte des sinistres")
        self.lbl_text.setStyleSheet("color: #64748b; font-size: 13px;")
        self.lbl_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_text)
        
        self.lbl_info = QLabel("Zone : Yaoundé")
        self.lbl_info.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_info)