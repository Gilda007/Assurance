# core/widgets/global_loader.py
"""
Widget de chargement global pour toute l'application
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFrame
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont


class SpinnerWidget(QWidget):
    """Spinner animé"""
    
    def __init__(self, parent=None, size=40, color="#3b82f6"):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._angle = 0
        self._color = QColor(color)
        self._timer = QTimer()
        self._timer.timeout.connect(self._rotate)
        self._timer.start(30)
        self._visible = True
    
    def _rotate(self):
        if self._visible:
            self._angle = (self._angle + 10) % 360
            self.update()
    
    def paintEvent(self, event):
        if not self._visible:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(self._color)
        pen.setWidth(3)
        painter.setPen(pen)
        
        rect = self.rect().adjusted(4, 4, -4, -4)
        painter.drawArc(rect, self._angle * 16, 270 * 16)
        
        painter.end()
    
    def stop(self):
        self._visible = False
        self._timer.stop()
        self.hide()


class GlobalLoader(QWidget):
    """Loader global qui se superpose à toute l'application"""
    
    _instance = None
    loading_changed = Signal(bool)
    
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
        self.setup_ui()
        self.hide()
        self._loading_count = 0
    
    def setup_ui(self):
        """Configure l'interface du loader"""
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.65);
            }
            QFrame {
                background: white;
                border-radius: 16px;
            }
            QLabel {
                color: #1e293b;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
            }
            QProgressBar {
                border: none;
                background: #e2e8f0;
                border-radius: 6px;
                height: 4px;
            }
            QProgressBar::chunk {
                background: #3b82f6;
                border-radius: 6px;
            }
        """)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Conteneur blanc
        container = QFrame()
        container.setFixedSize(280, 180)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSpacing(15)
        
        # Spinner
        self.spinner = SpinnerWidget(size=50, color="#3b82f6")
        container_layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        
        # Message
        self.message_label = QLabel("Chargement en cours...")
        self.message_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.message_label)
        
        # Barre de progression (optionnelle)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setVisible(False)
        container_layout.addWidget(self.progress_bar)
        
        layout.addWidget(container)
        
        # Animation
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(200)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def show_loading(self, message="Chargement en cours..."):
        """Affiche le loader"""
        self._loading_count += 1
        
        if self._loading_count == 1:
            self.message_label.setText(message)
            self.progress_bar.setVisible(False)
            self.spinner.show()
            self.spinner._visible = True
            
            # Centrer sur l'écran
            screen = self.screen().availableGeometry()
            self.move(
                screen.center().x() - self.width() // 2,
                screen.center().y() - self.height() // 2
            )
            
            self.opacity_anim.setStartValue(0)
            self.opacity_anim.setEndValue(1)
            self.show()
            self.opacity_anim.start()
            
            self.loading_changed.emit(True)
    
    def hide_loading(self):
        """Cache le loader"""
        self._loading_count = max(0, self._loading_count - 1)
        
        if self._loading_count == 0:
            self.opacity_anim.setStartValue(1)
            self.opacity_anim.setEndValue(0)
            self.opacity_anim.finished.connect(self._on_hide)
            self.opacity_anim.start()
            self.loading_changed.emit(False)
    
    def _on_hide(self):
        self.opacity_anim.finished.disconnect(self._on_hide)
        self.hide()
        self.spinner.stop()
    
    def set_progress(self, value, message=None):
        """Met à jour la progression"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(value)
        if message:
            self.message_label.setText(message)
        if value >= 100:
            QTimer.singleShot(500, self.hide_loading)


_global_loader = None

def get_global_loader():
    """Retourne l'instance singleton du loader global."""
    global _global_loader
    if _global_loader is None:
        _global_loader = GlobalLoader()
    return _global_loader