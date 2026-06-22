# addons/Automobiles/views/styles.py
"""
Styles modernes pour l'interface automobile
Design professionnel avec palette de couleurs cohérente
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

class Colors:
    """Palette de couleurs professionnelle"""
    
    # Couleurs principales
    PRIMARY = "#2563eb"      # Bleu professionnel
    PRIMARY_DARK = "#1e40af"  # Bleu foncé
    PRIMARY_LIGHT = "#60a5fa" # Bleu clair
    PRIMARY_HOVER = "#3b82f6" # Bleu hover
    
    # Couleurs secondaires
    SECONDARY = "#64748b"     # Gris ardoise
    SECONDARY_DARK = "#475569"
    SECONDARY_LIGHT = "#94a3b8"
    
    # États
    SUCCESS = "#10b981"       # Vert succès
    WARNING = "#f59e0b"       # Orange warning
    DANGER = "#ef4444"        # Rouge danger
    INFO = "#06b6d4"          # Cyan info
    
    # Neutres
    WHITE = "#ffffff"
    BLACK = "#0f172a"
    GRAY_50 = "#f8fafc"
    GRAY_100 = "#f1f5f9"
    GRAY_200 = "#e2e8f0"
    GRAY_300 = "#cbd5e1"
    GRAY_400 = "#94a3b8"
    GRAY_500 = "#64748b"
    GRAY_600 = "#475569"
    GRAY_700 = "#334155"
    GRAY_800 = "#1e293b"
    GRAY_900 = "#0f172a"
    
    # Fond et bordure
    BACKGROUND = "#f8fafc"
    CARD_BG = "#ffffff"
    BORDER = "#e2e8f0"
    SIDEBAR_BG = "#ffffff"
    SIDEBAR_ACTIVE = "#eff6ff"
    
    # Texte
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#475569"
    TEXT_MUTED = "#64748b"
    TEXT_DISABLED = "#94a3b8"
    
    # Graphiques
    CHART_COLORS = [
        "#3b82f6", "#10b981", "#f59e0b", "#ef4444",
        "#8b5cf6", "#ec4899", "#06b6d4", "#f97316",
        "#6366f1", "#14b8a6", "#f43f5e", "#8b5cf6"
    ]


class Fonts:
    """Configuration des polices"""
    
    FAMILY = "Inter, 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif"
    
    # Tailles
    H1 = 32
    H2 = 24
    H3 = 20
    H4 = 18
    H5 = 16
    H6 = 14
    BODY = 13
    SMALL = 11
    CAPTION = 10
    
    # Poids
    LIGHT = 300
    REGULAR = 400
    MEDIUM = 500
    SEMIBOLD = 600
    BOLD = 700


class Spacing:
    """Espacements standards"""
    
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32


class Shadows:
    """Ombres pour les cartes et éléments"""
    
    @staticmethod
    def card():
        return f"""
            background-color: {Colors.CARD_BG};
            border: 1px solid {Colors.BORDER};
            border-radius: 16px;
        """
    
    @staticmethod
    def card_hover():
        return f"""
            background-color: {Colors.CARD_BG};
            border: 1px solid {Colors.PRIMARY_LIGHT};
            border-radius: 16px;
        """
    
    @staticmethod
    def button():
        return f"""
            border: none;
            border-radius: 10px;
            font-weight: 500;
            padding: 8px 16px;
        """


# Style global de l'application
GLOBAL_STYLE = f"""
    * {{
        font-family: {Fonts.FAMILY};
    }}
    
    QWidget {{
        background-color: {Colors.BACKGROUND};
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.BODY}px;
    }}
    
    QLabel {{
        color: {Colors.TEXT_PRIMARY};
    }}
    
    QPushButton {{
        background-color: {Colors.PRIMARY};
        color: {Colors.WHITE};
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: {Fonts.MEDIUM};
        font-size: {Fonts.BODY}px;
    }}
    
    QPushButton:hover {{
        background-color: {Colors.PRIMARY_HOVER};
    }}
    
    QPushButton:pressed {{
        background-color: {Colors.PRIMARY_DARK};
    }}
    
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
        background-color: {Colors.WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: {Fonts.BODY}px;
    }}
    
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border-color: {Colors.PRIMARY};
        outline: none;
    }}
    
    QTableWidget {{
        background-color: {Colors.WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: 12px;
        gridline-color: {Colors.GRAY_100};
        selection-background-color: {Colors.PRIMARY_LIGHT};
        selection-color: {Colors.WHITE};
    }}
    
    QTableWidget::item {{
        padding: 12px;
    }}
    
    QTableWidget::item:selected {{
        background-color: {Colors.PRIMARY_LIGHT};
        color: {Colors.WHITE};
    }}
    
    QHeaderView::section {{
        background-color: {Colors.GRAY_50};
        padding: 12px;
        border: none;
        border-bottom: 1px solid {Colors.BORDER};
        font-weight: {Fonts.SEMIBOLD};
        color: {Colors.TEXT_SECONDARY};
    }}
    
    QScrollBar:vertical {{
        background-color: {Colors.GRAY_100};
        width: 10px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {Colors.GRAY_400};
        border-radius: 5px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {Colors.GRAY_500};
    }}
    
    QProgressBar {{
        border: none;
        border-radius: 6px;
        text-align: center;
        background-color: {Colors.GRAY_100};
    }}
    
    QProgressBar::chunk {{
        background-color: {Colors.PRIMARY};
        border-radius: 6px;
    }}
    
    QTabWidget::pane {{
        background-color: {Colors.WHITE};
        border: 1px solid {Colors.BORDER};
        border-radius: 12px;
    }}
    
    QTabBar::tab {{
        background-color: {Colors.GRAY_50};
        padding: 10px 20px;
        margin-right: 4px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {Colors.PRIMARY};
        color: {Colors.WHITE};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {Colors.GRAY_200};
    }}
    
    QMessageBox {{
        background-color: {Colors.WHITE};
    }}
    
    QDialog {{
        background-color: {Colors.WHITE};
    }}
"""


def apply_global_style(app):
    """Applique le style global à l'application"""
    app.setStyleSheet(GLOBAL_STYLE)

def create_shadow(blur=20, offset_x=0, offset_y=4, color=None):
    """
    Crée un effet d'ombre portée
    
    Args:
        blur: Rayon de flou (défaut: 20)
        offset_x: Décalage horizontal (défaut: 0)
        offset_y: Décalage vertical (défaut: 4)
        color: Couleur de l'ombre (défaut: noir avec opacité 30)
    
    Returns:
        QGraphicsDropShadowEffect: Effet d'ombre configuré
    """
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(offset_x, offset_y)
    
    if color is None:
        color = QColor(0, 0, 0, 30)
    shadow.setColor(color)
    
    return shadow