"""
Anneau de progression circulaire pour la section KPI Claims
Design : anneau bleu foncé avec valeur centrale
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QFont, QConicalGradient,
    QPainterPath, QBrush
)
import math


class CircularProgressRing(QWidget):
    """
    Anneau de progression circulaire
    - Piste en dégradé clair
    - Arc coloré (bleu foncé)
    - Valeur au centre
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._max_value = 100
        self._thickness = 12
        self._color = "#1e3a8a"      # Bleu foncé
        self._track_color = "#e0e7f0"  # Gris très clair
        self._text_color = "#1e3a8a"
        
        self.setFixedSize(180, 180)
    
    def set_value(self, value: float, max_value: float = 100):
        """Définit la valeur et le maximum"""
        self._value = max(0, value)
        self._max_value = max_value if max_value > 0 else 1
        self.update()
    
    def set_color(self, color: str):
        """Change la couleur de l'arc"""
        self._color = color
        self._text_color = color
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        thickness = self._thickness
        margin = thickness / 2 + 4
        
        # Rect de l'anneau
        rect = QRectF(
            margin, margin,
            w - 2 * margin, h - 2 * margin
        )
        
        # ============================================================
        # 1. PISTE DE FOND (track) avec dégradé
        # ============================================================
        pen = QPen(QColor(self._track_color), thickness, Qt.SolidLine, Qt.FlatCap)
        painter.setPen(pen)
        
        # On dessine un arc de 300° en partant de -120° (bas gauche)
        # pour laisser un vide en bas
        start_angle = 210 * 16       # 210° (bas gauche)
        span_angle = -300 * 16       # -300° dans le sens horaire
        painter.drawArc(rect, start_angle, span_angle)
        
        # ============================================================
        # 2. ARC DE PROGRESSION
        # ============================================================
        if self._value > 0:
            ratio = min(self._value / self._max_value, 1.0)
            progress_span = int(span_angle * ratio)
            
            # Dégradé conique bleu foncé → bleu plus clair
            gradient = QConicalGradient(rect.center(), 90)
            gradient.setColorAt(0.0, QColor("#1e3a8a"))
            gradient.setColorAt(0.5, QColor("#3b82f6"))
            gradient.setColorAt(1.0, QColor("#1e3a8a"))
            
            pen = QPen(QBrush(gradient), thickness, Qt.SolidLine, Qt.FlatCap)
            painter.setPen(pen)
            painter.drawArc(rect, start_angle, progress_span)
        
        # ============================================================
        # 3. VALEUR AU CENTRE
        # ============================================================
        painter.setPen(QColor(self._text_color))
        font = QFont()
        font.setPointSize(48)
        font.setBold(True)
        painter.setFont(font)
        
        # Décaler légèrement vers le haut pour compenser le vide en bas
        text_rect = rect.adjusted(0, -10, 0, -10)
        painter.drawText(text_rect, Qt.AlignCenter, str(int(self._value)))