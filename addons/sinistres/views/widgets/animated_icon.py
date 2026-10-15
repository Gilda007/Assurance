"""
Widget d'icône animée pour la sidebar
Supporte : rotation, scale (pulse)
"""
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, Property
)
from PySide6.QtGui import QPixmap, QTransform
import qtawesome as qta


class AnimatedIconLabel(QLabel):
    """
    QLabel qui affiche une icône FontAwesome et supporte plusieurs animations :
    - rotate : rotation à 360°
    - pulse : grossissement/rétrécissement
    """
    
    def __init__(self, icon_name: str, color: str = "#64748b", size: int = 20, parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._color = color
        self._size = size
        self._angle = 0
        self._scale = 1.0
        self._float_timer = None
        self._float_offset = 0
        self._float_direction = -1
        self._float_amplitude = 0
        self._float_speed = 1
        self.setFixedSize(size + 4, size + 4)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: transparent;")
        
        # Timer pour la rotation
        self._rotate_timer = QTimer(self)
        self._rotate_timer.timeout.connect(self._on_rotate_tick)
        
        # Variables pour la rotation
        self._rotate_total = 0
        self._rotate_step = 0
        self._rotate_interval = 30
        
        # Animation de pulse
        self._pulse_anim = None

        self._pulse_timer = None
        self._pulse_max_scale = 1.25
        self._pulse_period = 1.2
        self._pulse_elapsed = 0.0
        self._pulse_frame_ms = 16
        
        # Rendu initial
        self._render()
    
    # ═══════════════════════════════════════════════════════════════
    # RENDU
    # ═══════════════════════════════════════════════════════════════
    
    def _render(self):
        """Génère et applique le pixmap avec la rotation/scale actuels"""
        try:
            icon = qta.icon(self._icon_name, color=self._color)
            pixmap = icon.pixmap(QSize(self._size, self._size))
            
            # Appliquer la rotation
            if self._angle != 0:
                transform = QTransform()
                transform.translate(
                    pixmap.width() / 2,
                    pixmap.height() / 2
                )
                transform.rotate(self._angle)
                transform.translate(
                    -pixmap.width() / 2,
                    -pixmap.height() / 2
                )
                pixmap = pixmap.transformed(
                    transform,
                    Qt.SmoothTransformation
                )
            
            # Appliquer le scale
            if self._scale != 1.0:
                new_size = int(self._size * self._scale)
                pixmap = pixmap.scaled(
                    new_size, new_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            
            self.setPixmap(pixmap)
        except Exception as e:
            print(f"⚠️ Erreur rendu icône '{self._icon_name}': {e}")
            self.setText("●")
    
    # ═══════════════════════════════════════════════════════════════
    # API PUBLIQUE
    # ═══════════════════════════════════════════════════════════════
    
    def set_color(self, color: str):
        """Change la couleur et re-rend"""
        self._color = color
        self._render()
    
    def rotate(self, duration_ms: int = 500, loops: int = 1):
        """Lance une rotation à 360°"""
        self._rotate_total = 360 * loops
        self._rotate_step = 0
        self._rotate_interval = max(16, duration_ms // max(1, self._rotate_total // 6))
        self._rotate_timer.start(self._rotate_interval)
    
    def _on_rotate_tick(self):
        """Tick de rotation"""
        self._angle = (self._angle + 6) % 360
        self._rotate_step += 6
        self._render()
        
        if self._rotate_step >= self._rotate_total:
            self._rotate_timer.stop()
            self._angle = 0
            self._render()
    
    def start_continuous_rotate(self, speed_ms: int = 40):
        """Rotation infinie (pour hover)"""
        self._rotate_total = 0  # 0 = infini
        self._rotate_step = 0
        self._rotate_interval = speed_ms
        self._rotate_timer.start(speed_ms)
    
    def stop_continuous_rotate(self):
        """Arrête la rotation continue"""
        self._rotate_timer.stop()
        self._angle = 0
        self._render()
    
    def pulse(self, duration_ms: int = 400, max_scale: float = 1.3):
        """Pulse : grossit puis revient"""
        self._pulse_anim = QPropertyAnimation(self, b"scale_factor")
        self._pulse_anim.setDuration(duration_ms)
        self._pulse_anim.setStartValue(1.0)
        self._pulse_anim.setEndValue(max_scale)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse_anim.setLoopCount(2)  # 2 = aller-retour
        self._pulse_anim.start()
    
    def _get_scale(self) -> float:
        return self._scale
    
    def _set_scale(self, value: float):
        self._scale = value
        self._render()
    
    scale_factor = Property(float, _get_scale, _set_scale)

    def start_floating(self, amplitude: int = 3, duration: int = 800):
        """
        Démarre une animation flottante (monte/descend en boucle).
        amplitude : décalage en pixels (positif = monte)
        duration : durée d'un cycle complet (montée + descente)
        """
        # Éviter de créer plusieurs animations en même temps
        self.stop_floating()
        
        self._float_offset = 0
        self._float_direction = -1   # -1 = monter, +1 = descendre
        self._float_amplitude = amplitude
        self._float_speed = max(1, int(amplitude * 2 / max(1, duration / 16)))
        
        self._float_timer = QTimer(self)
        self._float_timer.timeout.connect(self._on_float_tick)
        self._float_timer.start(16)
        
        # Centrer verticalement de base
        self.setAlignment(Qt.AlignCenter)

    def stop_floating(self):
        """Arrête l'animation flottante et remet l'icône au centre"""
        if hasattr(self, '_float_timer') and self._float_timer is not None:
            self._float_timer.stop()
            self._float_timer = None
        
        self._float_offset = 0
        self._apply_float_offset()
        self.setAlignment(Qt.AlignCenter)

    def _on_float_tick(self):
        """Tick de l'animation flottante"""
        # Avancer
        self._float_offset += self._float_direction * self._float_speed
        
        # Inverser la direction aux bornes
        if self._float_offset <= -self._float_amplitude:
            self._float_offset = -self._float_amplitude
            self._float_direction = 1
        elif self._float_offset >= 0:
            self._float_offset = 0
            self._float_direction = -1
        
        self._apply_float_offset()

    def _apply_float_offset(self):
        """Applique le décalage vertical via margin-top"""
        # On utilise un padding-top négatif simulé par la marge
        # pour décaler l'icône vers le haut
        offset = self._float_offset
        self.setStyleSheet(f"""
            background: transparent;
            margin-top: {offset}px;
            margin-bottom: {-offset}px;
        """)

    def start_pulse_continuous(self, max_scale: float = 1.25, duration_ms: int = 1200):
        """
        Pulse continu ultra-fluide via QTimer + sinusoïde.
        Aucune pause aux extrémités — l'oscillation est parfaitement lisse.
        """
        import math
        
        self.stop_pulse_continuous()
        
        self._pulse_max_scale = max_scale
        self._pulse_period = duration_ms / 1000.0   # en secondes
        self._pulse_elapsed = 0.0
        self._pulse_frame_ms = 16                    # ~60 FPS
        
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._on_pulse_tick)
        self._pulse_timer.start(self._pulse_frame_ms)

    def _on_pulse_tick(self):
        """Calcule l'échelle via sinusoïde et met à jour le rendu"""
        import math
        
        # Avancer le temps
        self._pulse_elapsed += self._pulse_frame_ms / 1000.0
        
        # Calcul de la phase (0 → 2π sur une période complète)
        phase = (self._pulse_elapsed / self._pulse_period) * 2 * math.pi
        
        # Sinusoïde : oscille entre -1 et +1
        # On la remappe pour osciller entre 1.0 et max_scale
        normalized = (math.sin(phase) + 1) / 2    # 0 → 1
        new_scale = 1.0 + (self._pulse_max_scale - 1.0) * normalized
        
        # Mise à jour (si changement significatif)
        if abs(new_scale - self._scale) > 0.001:
            self._scale = new_scale
            self._render()

    def stop_pulse_continuous(self):
        """Arrête l'animation pulse et remet l'icône à sa taille normale"""
        # Arrêter le timer
        if hasattr(self, '_pulse_timer') and self._pulse_timer is not None:
            self._pulse_timer.stop()
            self._pulse_timer = None
        
        # Arrêter aussi l'ancien QPropertyAnimation s'il existe
        if hasattr(self, '_pulse_anim') and self._pulse_anim is not None:
            self._pulse_anim.stop()
            self._pulse_anim = None
        
        # Reset
        self._scale = 1.0
        self._render()