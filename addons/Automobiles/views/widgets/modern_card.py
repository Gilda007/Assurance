

# addons/Automobiles/views/widgets/modern_card.py
"""
Widget carte moderne avec ombres et effets
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect, QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PySide6.QtGui import QColor
import qtawesome as qta

from addons.Automobiles.views.style import Colors, Fonts, Spacing


class ModernCard(QFrame):
    """Carte moderne avec animation au survol"""
    
    def __init__(self, title: str = None, icon: str = None, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon_name = icon
        self._animating = False
        self.original_pos = None
        self.animation = None
        
        self.setup_ui()
    
    def setup_ui(self):
        self.setObjectName("modern_card")
        self.setStyleSheet(f"""
            QFrame#modern_card {{
                background-color: {Colors.CARD_BG};
                border: 1px solid {Colors.BORDER};
                border-radius: 16px;
                padding: 20px;
            }}
            QFrame#modern_card:hover {{
                border-color: {Colors.PRIMARY_LIGHT};
                background: {Colors.GRAY_50};
            }}
        """)
        
        # Ombre portée
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)
        
        # ✅ Layout principal unique
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        self.main_layout.setSpacing(Spacing.MD)
        
        # ✅ En-tête avec icône Font Awesome
        if self.title or self.icon_name:
            header_layout = QHBoxLayout()
            header_layout.setSpacing(Spacing.SM)
            
            # ✅ Icône Font Awesome
            if self.icon_name:
                icon_label = QLabel()
                try:
                    fa_icon = qta.icon(self.icon_name, color=Colors.PRIMARY)
                    icon_label.setPixmap(fa_icon.pixmap(20, 20))
                except Exception as e:
                    # print(f"⚠️ Erreur chargement icône {self.icon_name}: {e}")
                    icon_label.setText(self.icon_name)
                    icon_label.setStyleSheet(f"""
                        font-size: 16px;
                        color: {Colors.PRIMARY};
                        background: transparent;
                        border: none;
                    """)
                icon_label.setStyleSheet("background: transparent; border: none;")
                header_layout.addWidget(icon_label)
            
            # Titre
            if self.title:
                title_label = QLabel(self.title)
                title_label.setStyleSheet(f"""
                    font-size: {Fonts.H6}px;
                    font-weight: {Fonts.SEMIBOLD};
                    color: {Colors.TEXT_PRIMARY};
                    background: transparent;
                    border: none;
                """)
                header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            self.main_layout.addLayout(header_layout)
        
        # ✅ Zone de contenu unique
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent; border: none;")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(Spacing.SM)
        
        self.main_layout.addWidget(self.content)
        
        # Configurer l'animation
        self.setup_animation()
    
    def setup_animation(self):
        """Configure l'animation au survol"""
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        QTimer.singleShot(50, self._capture_initial_position)
    
    def _capture_initial_position(self):
        """Capture la position initiale réelle de la carte"""
        if self.isVisible() and self.pos().y() > 0:
            self.original_pos = self.pos()
        else:
            QTimer.singleShot(100, self._capture_initial_position)
    
    def _get_original_pos(self):
        """Récupère la position originale de manière sécurisée"""
        if self.original_pos is None or self.original_pos.y() <= 0:
            return self.pos()
        return self.original_pos
    
    def enterEvent(self, event):
        """Animation à l'entrée de la souris"""
        if self._animating or not self.animation:
            return
        
        current_pos = self.pos()
        original = self._get_original_pos()
        
        if current_pos.y() <= 0 or original.y() <= 0:
            return
        
        self.animation.stop()
        self.animation.setStartValue(current_pos)
        self.animation.setEndValue(QPoint(current_pos.x(), current_pos.y() - 4))
        self.animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Animation à la sortie de la souris"""
        if self._animating or not self.animation:
            return
        
        original = self._get_original_pos()
        
        if original.y() <= 0:
            return
        
        self.animation.stop()
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(original)
        self.animation.start()
        
        super().leaveEvent(event)
    
    def add_widget(self, widget):
        """✅ Ajoute un widget à la zone de contenu"""
        if hasattr(self, 'content_layout'):
            self.content_layout.addWidget(widget)
        else:
            self.main_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """✅ Ajoute un layout à la zone de contenu"""
        if hasattr(self, 'content_layout'):
            self.content_layout.addLayout(layout)
        else:
            self.main_layout.addLayout(layout)
    
    def set_content(self, widget):
        """✅ Définit le widget de contenu (vide puis ajoute)"""
        if hasattr(self, 'content_layout'):
            # Vider le layout existant
            while self.content_layout.count():
                item = self.content_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.add_widget(widget)


class StatsCard(QFrame):
    """Carte de statistiques avec valeur animée"""
    
    def __init__(self, title: str, value: int, icon: str, color: str, trend: str = None):
        super().__init__()
        self.title = title
        self.value = value
        self.icon_name = icon
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
        
        # ✅ Icône Font Awesome
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
        
        icon_label = QLabel()
        try:
            fa_icon = qta.icon(self.icon_name, color=self.color)
            icon_label.setPixmap(fa_icon.pixmap(24, 24))
        except Exception as e:
            print(f"⚠️ Erreur icône {self.icon_name}: {e}")
            icon_label.setText(self.icon_name)
            icon_label.setStyleSheet(f"""
                font-size: 20px;
                color: {self.color};
                background: transparent;
            """)
        icon_label.setStyleSheet("background: transparent; border: none;")
        icon_layout.addWidget(icon_label)
        
        # Informations
        info_layout = QVBoxLayout()
        info_layout.setSpacing(Spacing.XS)
        
        self.value_label = QLabel(str(self.value))
        self.value_label.setStyleSheet(f"""
            font-size: {Fonts.H1}px;
            font-weight: {Fonts.BOLD};
            color: {self.color};
            background: transparent;
            border: none;
        """)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-size: 12px;
            color: {Colors.TEXT_MUTED};
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: transparent;
            border: none;
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
                background: transparent;
            """)
            
            trend_label = QLabel(self.trend)
            trend_label.setStyleSheet(f"""
                color: {Colors.SUCCESS if "+" in self.trend else Colors.DANGER};
                font-size: 11px;
                font-weight: 600;
                background: transparent;
            """)
            
            trend_layout.addWidget(trend_icon, alignment=Qt.AlignCenter)
            trend_layout.addWidget(trend_label, alignment=Qt.AlignCenter)
            layout.addLayout(trend_layout)
    
    def animate_value(self, new_value: int):
        """Anime la valeur de la carte"""
        self.value = new_value
        self.value_label.setText(str(new_value))