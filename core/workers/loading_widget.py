# core/workers/loading_widget.py
"""
Widget de chargement moderne avec animation
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFrame
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont


class SpinnerWidget(QWidget):
    """Widget de spinner animé"""
    
    def __init__(self, parent=None, size=40, color="#3b82f6"):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._angle = 0
        self._color = QColor(color)
        self._timer = QTimer()
        self._timer.timeout.connect(self._rotate)
        self._timer.start(30)
    
    def _rotate(self):
        self._angle = (self._angle + 10) % 360
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dessiner le cercle
        pen = QPen(self._color)
        pen.setWidth(3)
        painter.setPen(pen)
        
        rect = self.rect().adjusted(4, 4, -4, -4)
        painter.drawArc(rect, self._angle * 16, 270 * 16)
        
        painter.end()
    
    def stop(self):
        self._timer.stop()


class LoadingOverlay(QWidget):
    """Overlay de chargement moderne"""
    
    def __init__(self, parent=None, message="Chargement en cours..."):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.65); border-radius: 12px;")
        self.hide()
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # Conteneur blanc
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                padding: 25px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSpacing(15)
        
        # Spinner
        self.spinner = SpinnerWidget(size=50, color="#3b82f6")
        container_layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        
        # Message
        self.message_label = QLabel(message)
        self.message_label.setStyleSheet("""
            color: #1e293b;
            font-size: 14px;
            font-weight: 500;
            background: transparent;
        """)
        self.message_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.message_label)
        
        # Barre de progression (optionnelle)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #e2e8f0;
                border-radius: 6px;
                height: 6px;
            }
            QProgressBar::chunk {
                background: #3b82f6;
                border-radius: 6px;
            }
        """)
        container_layout.addWidget(self.progress_bar)
        
        layout.addWidget(container)
        
        # Animation d'apparition
        self._opacity = 0
        self._animating = False
    
    def show_loading(self, message=None):
        """Affiche l'overlay"""
        if message:
            self.message_label.setText(message)
        self.resize(self.parent().size())
        self.raise_()
        self.show()
        self._animate_in()
    
    def hide_loading(self):
        """Cache l'overlay"""
        self._animate_out()
    
    def set_progress(self, value, message=None):
        """Met à jour la progression"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(value)
        if message:
            self.message_label.setText(message)
        if value >= 100:
            QTimer.singleShot(500, self.hide_loading)
    
    def _animate_in(self):
        """Animation d'entrée"""
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self._opacity = 0
        self._animating = True
        
        def update():
            if self._opacity < 65 and self._animating:
                self._opacity += 5
                self.setStyleSheet(f"background-color: rgba(0, 0, 0, {self._opacity});")
                QTimer.singleShot(20, update)
            else:
                self._animating = False
        
        QTimer.singleShot(20, update)
    
    def _animate_out(self):
        """Animation de sortie"""
        self._animating = True
        
        def update():
            if self._opacity > 0 and self._animating:
                self._opacity -= 10
                self.setStyleSheet(f"background-color: rgba(0, 0, 0, {max(0, self._opacity)});")
                QTimer.singleShot(20, update)
            else:
                self._animating = False
                self.hide()
                self.spinner.stop()
        
        QTimer.singleShot(20, update)
    
    def resizeEvent(self, event):
        """Redimensionne l'overlay avec le parent"""
        if self.parent():
            self.resize(self.parent().size())
        super().resizeEvent(event)