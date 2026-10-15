"""
Barre de progression pour les cartes KPI
"""
from PySide6.QtWidgets import QWidget, QFrame
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath, QFont


class ProgressBarKpi(QWidget):
    """
    Barre de progression horizontale fine avec pourcentage
    Utilisable dans les cartes KPI
    """
    
    def __init__(
        self,
        height: int = 8,
        color: str = "#1a73e8",
        bg_color: str = "#e2e8f0",
        show_percent: bool = False,
        parent=None
    ):
        super().__init__(parent)
        self._percent = 0
        self._color = color
        self._bg_color = bg_color
        self._show_percent = show_percent
        self._bar_height = height
        
        self.setMinimumHeight(height + 4)
        self.setMaximumHeight(height + 4)
    
    def set_percent(self, percent: float):
        """Définit le pourcentage (0-100)"""
        self._percent = max(0.0, min(100.0, percent))
        self.update()
    
    def set_color(self, color: str):
        self._color = color
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self._bar_height
        y = (self.height() - h) / 2
        radius = h / 2
        
        # --- Fond gris ---
        bg_path = QPainterPath()
        bg_path.addRoundedRect(0, y, w, h, radius, radius)
        painter.fillPath(bg_path, QColor(self._bg_color))
        
        # --- Segment coloré ---
        if self._percent > 0:
            paid_w = (w * self._percent) / 100.0
            # Éviter les tout petits segments
            if paid_w < h:
                paid_w = h
            
            fg_path = QPainterPath()
            fg_path.addRoundedRect(0, y, paid_w, h, radius, radius)
            painter.fillPath(fg_path, QColor(self._color))