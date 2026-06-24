# addons/Automobiles/views/animations.py
"""
Gestionnaire d'animations pour les transitions entre pages
"""

from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint
from PySide6.QtWidgets import QStackedWidget


class PageTransitionManager:
    """Gestionnaire de transitions entre pages"""
    
    def __init__(self, stacked_widget, duration=400):
        self.stacked_widget = stacked_widget
        self.duration = duration
        self._is_animating = False
    
    def fade_transition(self, new_index):
        """Transition par fondu élégant"""
        if self._is_animating:
            return
        
        current_index = self.stacked_widget.currentIndex()
        if current_index == new_index:
            return
        
        old_widget = self.stacked_widget.widget(current_index)
        new_widget = self.stacked_widget.widget(new_index)
        
        if not old_widget or not new_widget:
            self.stacked_widget.setCurrentIndex(new_index)
            return
        
        self._is_animating = True
        
        # ✅ Sauvegarder l'opacité initiale
        old_opacity = old_widget.windowOpacity()
        
        # Nouvelle page prête
        new_widget.setVisible(True)
        new_widget.setWindowOpacity(0.0)
        
        # Animation de sortie
        fade_out = QPropertyAnimation(old_widget, b"windowOpacity")
        fade_out.setDuration(self.duration // 2)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Animation d'entrée
        fade_in = QPropertyAnimation(new_widget, b"windowOpacity")
        fade_in.setDuration(self.duration // 2)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InOutQuad)
        
        def on_fade_out_finished():
            self.stacked_widget.setCurrentIndex(new_index)
            fade_in.start()
        
        def on_fade_in_finished():
            old_widget.setWindowOpacity(old_opacity)
            new_widget.setWindowOpacity(1.0)
            self._is_animating = False
        
        fade_out.finished.connect(on_fade_out_finished)
        fade_in.finished.connect(on_fade_in_finished)
        
        fade_out.start()
    
    def slide_transition(self, new_index, direction="left"):
        """Transition par glissement élégant"""
        if self._is_animating:
            return
        
        current_index = self.stacked_widget.currentIndex()
        if current_index == new_index:
            return
        
        old_widget = self.stacked_widget.widget(current_index)
        new_widget = self.stacked_widget.widget(new_index)
        
        if not old_widget or not new_widget:
            self.stacked_widget.setCurrentIndex(new_index)
            return
        
        self._is_animating = True
        
        # ✅ Sauvegarder la position initiale
        old_pos = old_widget.pos()
        
        # ✅ Déterminer la direction
        if direction == "left":
            offset = old_widget.width()
        elif direction == "right":
            offset = -old_widget.width()
        elif direction == "up":
            offset = old_widget.height()
        else:  # down
            offset = -old_widget.height()
        
        # ✅ La nouvelle page doit être visible
        new_widget.setVisible(True)
        new_widget.setWindowOpacity(0.0)
        new_widget.raise_()
        
        # ✅ Positionner la nouvelle page
        if direction in ["left", "right"]:
            new_widget.move(offset, 0)
            old_end = QPoint(-offset, 0)
            new_start = QPoint(offset, 0)
        else:
            new_widget.move(0, offset)
            old_end = QPoint(0, -offset)
            new_start = QPoint(0, offset)
        
        # ✅ Animation de sortie
        slide_out = QPropertyAnimation(old_widget, b"pos")
        slide_out.setDuration(self.duration)
        slide_out.setStartValue(old_pos)
        slide_out.setEndValue(old_end)
        slide_out.setEasingCurve(QEasingCurve.InOutQuad)
        
        # ✅ Animation d'entrée
        slide_in = QPropertyAnimation(new_widget, b"pos")
        slide_in.setDuration(self.duration)
        slide_in.setStartValue(new_start)
        slide_in.setEndValue(QPoint(0, 0))
        slide_in.setEasingCurve(QEasingCurve.InOutQuad)
        
        # ✅ Animation d'opacité
        fade_in = QPropertyAnimation(new_widget, b"windowOpacity")
        fade_in.setDuration(self.duration)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InOutQuad)
        
        # ✅ Grouper les animations
        group = QParallelAnimationGroup()
        group.addAnimation(slide_out)
        group.addAnimation(slide_in)
        group.addAnimation(fade_in)
        
        def on_finished():
            self.stacked_widget.setCurrentIndex(new_index)
            old_widget.move(0, 0)
            old_widget.setWindowOpacity(1.0)
            new_widget.move(0, 0)
            new_widget.setWindowOpacity(1.0)
            self._is_animating = False
        
        group.finished.connect(on_finished)
        group.start()
    
    def zoom_transition(self, new_index):
        """Transition par zoom élégant"""
        if self._is_animating:
            return
        
        current_index = self.stacked_widget.currentIndex()
        if current_index == new_index:
            return
        
        old_widget = self.stacked_widget.widget(current_index)
        new_widget = self.stacked_widget.widget(new_index)
        
        if not old_widget or not new_widget:
            self.stacked_widget.setCurrentIndex(new_index)
            return
        
        self._is_animating = True
        
        old_opacity = old_widget.windowOpacity()
        
        new_widget.setVisible(True)
        new_widget.setWindowOpacity(0.0)
        
        # Animation de sortie
        fade_out = QPropertyAnimation(old_widget, b"windowOpacity")
        fade_out.setDuration(self.duration // 2)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Animation d'entrée
        fade_in = QPropertyAnimation(new_widget, b"windowOpacity")
        fade_in.setDuration(self.duration // 2)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.OutBack)
        
        def on_fade_out_finished():
            self.stacked_widget.setCurrentIndex(new_index)
            fade_in.start()
        
        def on_fade_in_finished():
            old_widget.setWindowOpacity(old_opacity)
            new_widget.setWindowOpacity(1.0)
            self._is_animating = False
        
        fade_out.finished.connect(on_fade_out_finished)
        fade_in.finished.connect(on_fade_in_finished)
        
        fade_out.start()