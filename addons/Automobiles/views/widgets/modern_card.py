

# addons/Automobiles/views/widgets/modern_card.py
"""
Widget carte moderne avec ombres et effets
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PySide6.QtGui import QColor

from addons.Automobiles.views.style import Colors, Fonts, Spacing


class ModernCard(QFrame):
    """Carte moderne avec animation au survol"""
    
    def __init__(self, title: str = None, icon: str = None, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self._animating = False
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        self.setObjectName("modern_card")
        self.setStyleSheet(f"""
            QFrame#modern_card {{
                background-color: {Colors.CARD_BG};
                border: 1px solid {Colors.BORDER};
                border-radius: 20px;
            }}
            QFrame#modern_card:hover {{
                border-color: {Colors.PRIMARY_LIGHT};
            }}
        """)
        
        # Ombre portée
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        self.main_layout.setSpacing(Spacing.MD)
        
        # En-tête
        if self.title or self.icon:
            self.setup_header()
    
    def setup_header(self):
        header_layout = QHBoxLayout()
        header_layout.setSpacing(Spacing.SM)
        
        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setStyleSheet(f"font-size: 24px; background: transparent;")
            header_layout.addWidget(icon_label)
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet(f"""
                font-size: {Fonts.H6}px;
                font-weight: {Fonts.SEMIBOLD};
                color: {Colors.TEXT_PRIMARY};
                background: transparent;
            """)
            header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)
    
    def setup_animation(self):
        """Configure l'animation au survol"""
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Utiliser QTimer pour capturer la position réelle après l'affichage
        self.original_pos = None
        
        # Correction : s'assurer que la position est correcte après l'affichage
        QTimer.singleShot(50, self._capture_initial_position)
    
    def _capture_initial_position(self):
        """Capture la position initiale réelle de la carte"""
        # Ne capturer que si la carte est visible et a une position valide
        if self.isVisible() and self.pos().y() > 0:
            self.original_pos = self.pos()
        else:
            # Réessayer plus tard
            QTimer.singleShot(100, self._capture_initial_position)
    
    def _get_original_pos(self):
        """Récupère la position originale de manière sécurisée"""
        if self.original_pos is None or self.original_pos.y() <= 0:
            # Si la position n'est pas encore capturée, utiliser la position actuelle
            return self.pos()
        return self.original_pos
    
    def enterEvent(self, event):
        """Animation à l'entrée de la souris"""
        if self._animating:
            return
        
        current_pos = self.pos()
        original = self._get_original_pos()
        
        # Ne pas animer si la position n'est pas valide
        if current_pos.y() <= 0 or original.y() <= 0:
            return
        
        self.animation.stop()
        self.animation.setStartValue(current_pos)
        self.animation.setEndValue(QPoint(current_pos.x(), current_pos.y() - 4))
        self.animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Animation à la sortie de la souris"""
        if self._animating:
            return
        
        original = self._get_original_pos()
        
        # Ne pas animer si la position n'est pas valide
        if original.y() <= 0:
            return
        
        self.animation.stop()
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(original)
        self.animation.start()
        
        super().leaveEvent(event)
    
    def add_widget(self, widget):
        """Ajoute un widget à la carte"""
        self.main_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Ajoute un layout à la carte"""
        self.main_layout.addLayout(layout)


class StatsCard(QFrame):
    """Carte de statistiques avec valeur animée"""
    
    def __init__(self, title: str, value: int, icon: str, color: str, trend: str = None):
        super().__init__()
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self.trend = trend
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedHeight(110)
        self.setStyleSheet(f"""
            QFrame {{
                background: {Colors.CARD_BG};
                border-radius: 16px;
                border: 1px solid {Colors.BORDER};
            }}
            QFrame:hover {{
                border-color: {self.color};
                background: {self.color}10;
            }}
        """)
        
        # Ombre portée
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)
        layout.setSpacing(Spacing.MD)
        
        # Icône
        icon_container = QFrame()
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: {self.color}15;
                border-radius: 14px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"font-size: 24px; background: transparent;")
        icon_layout.addWidget(icon_label)
        
        # Informations
        info_layout = QVBoxLayout()
        info_layout.setSpacing(Spacing.XS)
        
        self.value_label = QLabel(str(self.value))
        self.value_label.setStyleSheet(f"""
            font-size: {Fonts.H1}px;
            font-weight: {Fonts.BOLD};
            color: {self.color};
        """)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 12px;
            color: #64748b;
            font-weight: 500;
        """)
        
        info_layout.addWidget(self.value_label)
        info_layout.addWidget(title_label)
        
        layout.addWidget(icon_container)
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Tendance
        if self.trend:
            trend_layout = QVBoxLayout()
            trend_layout.setSpacing(2)
            
            trend_icon = QLabel("▲" if "+" in self.trend else "▼")
            trend_icon.setStyleSheet(f"""
                color: {Colors.SUCCESS if "+" in self.trend else Colors.DANGER};
                font-size: 12px;
                font-weight: 600;
            """)
            
            trend_label = QLabel(self.trend)
            trend_label.setStyleSheet(f"""
                color: {Colors.SUCCESS if "+" in self.trend else Colors.DANGER};
                font-size: 11px;
                font-weight: 600;
            """)
            
            trend_layout.addWidget(trend_icon, alignment=Qt.AlignCenter)
            trend_layout.addWidget(trend_label, alignment=Qt.AlignCenter)
            layout.addLayout(trend_layout)
    
    def animate_value(self, new_value: int):
        """Anime la valeur de la carte"""
        self.value = new_value
        self.value_label.setText(str(new_value))