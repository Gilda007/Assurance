# icons/theme.py
"""
Gestionnaire de thèmes pour LOMETA
Support des thèmes clair et sombre
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor
from enum import Enum


class ThemeType(Enum):
    """Types de thèmes disponibles"""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


# ============================================================================
# PALETTE DE COULEURS
# ============================================================================

class Colors:
    """Palette de couleurs pour les thèmes"""
    
    # Couleurs de base (identiques pour tous les thèmes)
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    PRIMARY_LIGHT = "#60a5fa"
    SUCCESS = "#16a34a"
    SUCCESS_LIGHT = "#dcfce7"
    WARNING = "#f59e0b"
    WARNING_LIGHT = "#fef3c7"
    DANGER = "#dc2626"
    DANGER_LIGHT = "#fee2e2"
    INFO = "#7c3aed"
    INFO_LIGHT = "#ede9fe"
    
    # Couleurs des textes
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#475569"
    TEXT_MUTED = "#94a3b8"
    TEXT_WHITE = "#ffffff"
    
    # Couleurs de fond
    BG_PRIMARY = "#f8fafc"
    BG_SECONDARY = "#f1f5f9"
    BG_CARD = "#ffffff"
    BG_SIDEBAR = "#0f172a"
    
    # Bordures
    BORDER = "#e2e8f0"
    BORDER_LIGHT = "#f1f5f9"
    BORDER_DARK = "#cbd5e1"
    
    # Statuts
    STATUS_ONLINE = "#10b981"
    STATUS_OFFLINE = "#94a3b8"
    STATUS_BUSY = "#ef4444"
    STATUS_AWAY = "#f59e0b"


class DarkColors:
    """Palette de couleurs pour le thème sombre"""
    
    # Couleurs de base
    PRIMARY = "#3b82f6"
    PRIMARY_DARK = "#2563eb"
    PRIMARY_LIGHT = "#93c5fd"
    SUCCESS = "#34d399"
    SUCCESS_LIGHT = "#065f46"
    WARNING = "#fbbf24"
    WARNING_LIGHT = "#78350f"
    DANGER = "#f87171"
    DANGER_LIGHT = "#7f1d1d"
    INFO = "#a78bfa"
    INFO_LIGHT = "#4c1d95"
    
    # Couleurs des textes
    TEXT_PRIMARY = "#f1f5f9"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    TEXT_WHITE = "#ffffff"
    
    # Couleurs de fond
    BG_PRIMARY = "#0f172a"
    BG_SECONDARY = "#1e293b"
    BG_CARD = "#1e293b"
    BG_SIDEBAR = "#0f172a"
    
    # Bordures
    BORDER = "#334155"
    BORDER_LIGHT = "#1e293b"
    BORDER_DARK = "#475569"
    
    # Statuts
    STATUS_ONLINE = "#34d399"
    STATUS_OFFLINE = "#64748b"
    STATUS_BUSY = "#f87171"
    STATUS_AWAY = "#fbbf24"


# ============================================================================
# STYLESHEETS
# ============================================================================

def get_light_stylesheet() -> str:
    """Retourne le stylesheet pour le thème clair"""
    return f"""
        /* ============================================================
           STYLES GÉNÉRAUX
           ============================================================ */
        QMainWindow {{
            background-color: {Colors.BG_PRIMARY};
        }}
        
        QWidget {{
            background-color: transparent;
            color: {Colors.TEXT_PRIMARY};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        /* ============================================================
           SCROLLBARS
           ============================================================ */
        QScrollBar:vertical {{
            background: {Colors.BG_SECONDARY};
            width: 6px;
            border-radius: 3px;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background: {Colors.BORDER_DARK};
            border-radius: 3px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {Colors.PRIMARY};
        }}
        QScrollBar:horizontal {{
            background: {Colors.BG_SECONDARY};
            height: 6px;
            border-radius: 3px;
            border: none;
        }}
        QScrollBar::handle:horizontal {{
            background: {Colors.BORDER_DARK};
            border-radius: 3px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {Colors.PRIMARY};
        }}
        
        /* ============================================================
           BOUTONS
           ============================================================ */
        QPushButton {{
            background: {Colors.PRIMARY};
            color: {Colors.TEXT_WHITE};
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background: {Colors.PRIMARY_DARK};
        }}
        QPushButton:pressed {{
            background: {Colors.PRIMARY_DARK};
            padding-top: 9px;
            padding-bottom: 7px;
        }}
        QPushButton:disabled {{
            background: {Colors.BORDER};
            color: {Colors.TEXT_MUTED};
        }}
        
        /* Bouton secondaire */
        QPushButton[secondary="true"] {{
            background: {Colors.BG_SECONDARY};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER};
        }}
        QPushButton[secondary="true"]:hover {{
            background: {Colors.BORDER};
        }}
        
        /* Bouton danger */
        QPushButton[danger="true"] {{
            background: {Colors.DANGER};
            color: white;
        }}
        QPushButton[danger="true"]:hover {{
            background: #b91c1c;
        }}
        
        /* Bouton succès */
        QPushButton[success="true"] {{
            background: {Colors.SUCCESS};
            color: white;
        }}
        QPushButton[success="true"]:hover {{
            background: #15803d;
        }}
        
        /* ============================================================
           CHAMPS DE TEXTE
           ============================================================ */
        QLineEdit, QTextEdit, QComboBox {{
            background: {Colors.BG_CARD};
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
            color: {Colors.TEXT_PRIMARY};
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border-color: {Colors.PRIMARY};
            background: {Colors.BG_CARD};
        }}
        QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled {{
            background: {Colors.BG_SECONDARY};
            color: {Colors.TEXT_MUTED};
        }}
        
        /* ============================================================
           TABLEAUX
           ============================================================ */
        QTableWidget {{
            background: {Colors.BG_CARD};
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
            gridline-color: {Colors.BORDER};
        }}
        QTableWidget::item {{
            padding: 10px 12px;
            color: {Colors.TEXT_PRIMARY};
        }}
        QTableWidget::item:selected {{
            background: {Colors.PRIMARY_LIGHT}40;
            color: {Colors.TEXT_PRIMARY};
        }}
        QHeaderView::section {{
            background: {Colors.BG_SECONDARY};
            border: none;
            border-bottom: 2px solid {Colors.BORDER};
            padding: 10px 12px;
            font-weight: 600;
            font-size: 11px;
            color: {Colors.TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        QTableWidget::item:hover {{
            background: {Colors.BG_SECONDARY};
        }}
        
        /* ============================================================
           GROUPBOX
           ============================================================ */
        QGroupBox {{
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: 600;
            font-size: 14px;
            color: {Colors.TEXT_PRIMARY};
            background: {Colors.BG_CARD};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px 0 8px;
            color: {Colors.TEXT_PRIMARY};
        }}
        
        /* ============================================================
           LABELS
           ============================================================ */
        QLabel {{
            color: {Colors.TEXT_PRIMARY};
        }}
        QLabel[secondary="true"] {{
            color: {Colors.TEXT_SECONDARY};
        }}
        QLabel[muted="true"] {{
            color: {Colors.TEXT_MUTED};
        }}
        
        /* ============================================================
           COMBOBOX
           ============================================================ */
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background: {Colors.BG_CARD};
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
            padding: 4px;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            border-radius: 4px;
        }}
        QComboBox QAbstractItemView::item:selected {{
            background: {Colors.PRIMARY_LIGHT}40;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background: {Colors.BG_SECONDARY};
        }}
        
        /* ============================================================
           PROGRESS BAR
           ============================================================ */
        QProgressBar {{
            border: none;
            background: {Colors.BG_SECONDARY};
            border-radius: 4px;
            height: 6px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background: {Colors.PRIMARY};
            border-radius: 4px;
        }}
        
        /* ============================================================
           MENUS
           ============================================================ */
        QMenu {{
            background: {Colors.BG_CARD};
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
            padding: 4px;
        }}
        QMenu::item {{
            padding: 8px 20px;
            border-radius: 4px;
            color: {Colors.TEXT_PRIMARY};
        }}
        QMenu::item:selected {{
            background: {Colors.PRIMARY_LIGHT}40;
            color: {Colors.TEXT_PRIMARY};
        }}
        QMenu::separator {{
            height: 1px;
            background: {Colors.BORDER};
            margin: 4px 8px;
        }}
        
        /* ============================================================
           CARDS
           ============================================================ */
        QFrame[card="true"] {{
            background: {Colors.BG_CARD};
            border: 1px solid {Colors.BORDER};
            border-radius: 12px;
        }}
        QFrame[card="true"]:hover {{
            border-color: {Colors.PRIMARY_LIGHT};
        }}
        
        /* ============================================================
           BADGES
           ============================================================ */
        QFrame[badge="success"] {{
            background: {Colors.SUCCESS_LIGHT};
            color: {Colors.SUCCESS};
            border-radius: 20px;
            padding: 2px 10px;
            font-weight: 600;
            font-size: 11px;
        }}
        QFrame[badge="warning"] {{
            background: {Colors.WARNING_LIGHT};
            color: {Colors.WARNING};
            border-radius: 20px;
            padding: 2px 10px;
            font-weight: 600;
            font-size: 11px;
        }}
        QFrame[badge="danger"] {{
            background: {Colors.DANGER_LIGHT};
            color: {Colors.DANGER};
            border-radius: 20px;
            padding: 2px 10px;
            font-weight: 600;
            font-size: 11px;
        }}
        QFrame[badge="info"] {{
            background: {Colors.INFO_LIGHT};
            color: {Colors.INFO};
            border-radius: 20px;
            padding: 2px 10px;
            font-weight: 600;
            font-size: 11px;
        }}
    """


def get_dark_stylesheet() -> str:
    """Retourne le stylesheet pour le thème sombre"""
    # Copier le stylesheet clair en remplaçant les couleurs
    light_style = get_light_stylesheet()
    
    # Remplacer les couleurs du thème clair par les couleurs sombres
    replacements = {
        Colors.BG_PRIMARY: DarkColors.BG_PRIMARY,
        Colors.BG_SECONDARY: DarkColors.BG_SECONDARY,
        Colors.BG_CARD: DarkColors.BG_CARD,
        Colors.TEXT_PRIMARY: DarkColors.TEXT_PRIMARY,
        Colors.TEXT_SECONDARY: DarkColors.TEXT_SECONDARY,
        Colors.TEXT_MUTED: DarkColors.TEXT_MUTED,
        Colors.BORDER: DarkColors.BORDER,
        Colors.BORDER_LIGHT: DarkColors.BORDER_LIGHT,
        Colors.BORDER_DARK: DarkColors.BORDER_DARK,
        Colors.PRIMARY_LIGHT: DarkColors.PRIMARY_LIGHT,
        Colors.DANGER_LIGHT: DarkColors.DANGER_LIGHT,
        Colors.SUCCESS_LIGHT: DarkColors.SUCCESS_LIGHT,
        Colors.WARNING_LIGHT: DarkColors.WARNING_LIGHT,
        Colors.INFO_LIGHT: DarkColors.INFO_LIGHT,
    }
    
    for old, new in replacements.items():
        light_style = light_style.replace(old, new)
    
    return light_style


# ============================================================================
# GESTIONNAIRE DE THÈMES
# ============================================================================

class ThemeManager(QObject):
    """Gestionnaire de thèmes pour l'application"""
    
    theme_changed = Signal(str)
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self._current_theme = ThemeType.LIGHT
        self._available_themes = {
            ThemeType.LIGHT: get_light_stylesheet,
            ThemeType.DARK: get_dark_stylesheet,
        }
    
    def set_theme(self, theme: ThemeType):
        """Change le thème actif"""
        if theme not in self._available_themes:
            return
        
        self._current_theme = theme
        stylesheet = self._available_themes[theme]()
        self.theme_changed.emit(stylesheet)
    
    def get_current_theme(self) -> ThemeType:
        """Retourne le thème actif"""
        return self._current_theme
    
    def get_stylesheet(self, theme: ThemeType = None) -> str:
        """Retourne le stylesheet pour un thème donné"""
        if theme is None:
            theme = self._current_theme
        return self._available_themes[theme]()
    
    def toggle_theme(self):
        """Bascule entre les thèmes clair et sombre"""
        if self._current_theme == ThemeType.LIGHT:
            self.set_theme(ThemeType.DARK)
        else:
            self.set_theme(ThemeType.LIGHT)


# ============================================================================
# INSTANCE GLOBALE
# ============================================================================

theme_manager = ThemeManager()