"""
Helper pour appliquer un effet d'ombrage uniforme aux cartes
"""
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget
from PySide6.QtGui import QColor


# Paramètres d'ombrage uniformes
SHADOW_BLUR_RADIUS = 20
SHADOW_X_OFFSET = 0
SHADOW_Y_OFFSET = 3
SHADOW_COLOR = QColor(15, 23, 42, 30)   # Noir bleuté, alpha ~12%


def apply_card_shadow(widget: QWidget, intensity: str = "normal"):
    """
    Applique un effet d'ombrage subtil à un widget.
    
    Args:
        widget: widget auquel appliquer l'ombre
        intensity: 'subtle', 'normal', 'strong'
    """
    configs = {
        'subtle': (15, 2, 20),
        'normal': (20, 3, 30),
        'strong': (25, 4, 50),
    }
    
    blur, y_offset, alpha = configs.get(intensity, configs['normal'])
    
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setXOffset(SHADOW_X_OFFSET)
    shadow.setYOffset(y_offset)
    shadow.setColor(QColor(15, 23, 42, alpha))
    widget.setGraphicsEffect(shadow)