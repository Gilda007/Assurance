"""
Widget de chargement avec progression en temps réel.
Pattern LOMETA standard.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsDropShadowEffect, QProgressBar, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath


class SpinnerWidget(QWidget):
    def __init__(self, size=80, color="#2563eb", parent=None):
        super().__init__(parent)
        self._size = size
        self._color = QColor(color)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.start(16)
        self.setFixedSize(size, size)

    def _rotate(self):
        self._angle = (self._angle + 6) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pen_bg = QPen(QColor("#e2e8f0"), 6)
        pen_bg.setCapStyle(Qt.RoundCap)
        p.setPen(pen_bg)
        rect = QRectF(4, 4, self._size - 8, self._size - 8)
        p.drawArc(rect, 0, 360 * 16)
        pen = QPen(self._color, 6)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawArc(rect, -self._angle * 16, 90 * 16)

    def start(self):
        if not self._timer.isActive():
            self._timer.start(16)

    def stop(self):
        self._timer.stop()


class StepIcon(QWidget):
    def __init__(self, size=22, parent=None):
        super().__init__(parent)
        self._size = size
        self._state = "pending"
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self.setFixedSize(size, size)

    def set_state(self, state):
        self._state = state
        if state == "loading":
            self._timer.start(50)
        else:
            self._timer.stop()
        self.update()

    def _rotate(self):
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = self._size
        c = s / 2
        r = s / 2 - 2
        if self._state == "pending":
            p.setPen(QPen(QColor("#cbd5e1"), 2))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(c, c), r, r)
        elif self._state == "loading":
            p.setPen(QPen(QColor("#e2e8f0"), 2))
            p.drawEllipse(QPointF(c, c), r, r)
            pen = QPen(QColor("#2563eb"), 2)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawArc(QRectF(2, 2, s - 4, s - 4), -self._angle * 16, 90 * 16)
        elif self._state == "done":
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor("#10b981")))
            p.drawEllipse(QPointF(c, c), r, r)
            pen = QPen(QColor("white"), 2)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            p.setPen(pen)
            path = QPainterPath()
            path.moveTo(s * 0.3, s * 0.5)
            path.lineTo(s * 0.45, s * 0.65)
            path.lineTo(s * 0.72, s * 0.35)
            p.drawPath(path)
        elif self._state == "error":
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor("#ef4444")))
            p.drawEllipse(QPointF(c, c), r, r)
            pen = QPen(QColor("white"), 2)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawLine(QPointF(s * 0.32, s * 0.32), QPointF(s * 0.68, s * 0.68))
            p.drawLine(QPointF(s * 0.68, s * 0.32), QPointF(s * 0.32, s * 0.68))


class StepRow(QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.icon = StepIcon(size=20)
        layout.addWidget(self.icon)
        self.label = QLabel(label)
        self.label.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent;")
        layout.addWidget(self.label)
        layout.addStretch()
        self.status = QLabel("")
        self.status.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600; background: transparent;")
        layout.addWidget(self.status)

    def set_state(self, state, status_text=""):
        self.icon.set_state(state)
        if state == "pending":
            self.label.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent;")
            self.status.setText("")
        elif state == "loading":
            self.label.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: 600; background: transparent;")
            self.status.setStyleSheet("color: #2563eb; font-size: 11px; font-weight: 600; background: transparent;")
            self.status.setText(status_text or "…")
        elif state == "done":
            self.label.setStyleSheet("color: #1e293b; font-size: 12px; background: transparent;")
            self.status.setStyleSheet("color: #10b981; font-size: 11px; font-weight: 700; background: transparent;")
            self.status.setText(status_text or "✓")
        elif state == "error":
            self.label.setStyleSheet("color: #ef4444; font-size: 12px; background: transparent;")
            self.status.setStyleSheet("color: #ef4444; font-size: 11px; font-weight: 700; background: transparent;")
            self.status.setText(status_text or "✕")


class ModernProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setTextVisible(False)
        self.setFixedHeight(8)
        self.setStyleSheet("""
            QProgressBar { background: #f1f5f9; border: none; border-radius: 4px; }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:0.5 #3b82f6, stop:1 #60a5fa);
                border-radius: 4px;
            }
        """)


class LoadingPage(QWidget):
    def __init__(self, title="Chargement...", message=None, parent=None):
        super().__init__(parent)
        self._title = message or title
        self.setStyleSheet("background: white;")
        self._steps = {}
        self._step_weights = {}
        self._weights_done = 0
        self._total_weight = 0
        self._current_progress = 0
        self._target_progress = 0
        self._smooth_timer = QTimer(self)
        self._smooth_timer.timeout.connect(self._smooth_progress)
        self._smooth_timer.start(16)
        self._setup_ui()
        self._animate_in()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setAlignment(Qt.AlignCenter)

        self.card = QFrame()
        self.card.setObjectName("LoadingCard")
        self.card.setFixedSize(500, 480)
        self.card.setStyleSheet("""
            QFrame#LoadingCard {
                background: white; border-radius: 24px; border: 1px solid #e2e8f0;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(37, 99, 235, 25))
        shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 32, 40, 32)
        card_layout.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(16)
        self.spinner = SpinnerWidget(size=56, color="#2563eb")
        header.addWidget(self.spinner)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #0f172a; background: transparent;")
        title_box.addWidget(self.title_label)
        self.subtitle_label = QLabel("Préparation en cours...")
        self.subtitle_label.setStyleSheet("font-size: 12px; color: #64748b; background: transparent;")
        title_box.addWidget(self.subtitle_label)
        header.addLayout(title_box, 1)
        card_layout.addLayout(header)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #f1f5f9;")
        card_layout.addWidget(sep)

        self.steps_container = QVBoxLayout()
        self.steps_container.setSpacing(4)
        card_layout.addLayout(self.steps_container)
        card_layout.addStretch()

        progress_header = QHBoxLayout()
        lbl = QLabel("Progression")
        lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; background: transparent;")
        progress_header.addWidget(lbl)
        progress_header.addStretch()
        self.percent_label = QLabel("0%")
        self.percent_label.setStyleSheet("color: #2563eb; font-size: 16px; font-weight: 800; background: transparent;")
        progress_header.addWidget(self.percent_label)
        card_layout.addLayout(progress_header)

        self.progress_bar = ModernProgressBar()
        card_layout.addWidget(self.progress_bar)

        self.current_step_label = QLabel("Initialisation...")
        self.current_step_label.setStyleSheet("color: #94a3b8; font-size: 11px; font-style: italic; background: transparent;")
        self.current_step_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.current_step_label)

        main_layout.addWidget(self.card, 0, Qt.AlignCenter)

    def _animate_in(self):
        self._opacity = QGraphicsOpacityEffect()
        self.card.setGraphicsEffect(self._opacity)
        self._fade = QPropertyAnimation(self._opacity, b"opacity")
        self._fade.setDuration(300)
        self._fade.setStartValue(0)
        self._fade.setEndValue(1)
        self._fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade.finished.connect(self._restore_shadow)
        self._fade.start()

    def _restore_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(37, 99, 235, 25))
        shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)

    def reset(self, title=None):
        if title:
            self._title = title
            self.title_label.setText(title)
        while self.steps_container.count():
            item = self.steps_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._steps.clear()
        self._step_weights.clear()
        self._weights_done = 0
        self._total_weight = 0
        self._current_progress = 0
        self._target_progress = 0
        self.progress_bar.setValue(0)
        self.percent_label.setText("0%")
        self.current_step_label.setText("Initialisation...")
        self.subtitle_label.setText("Préparation en cours...")

    def add_step(self, step_id, label, weight=1):
        row = StepRow(label)
        self.steps_container.addWidget(row)
        self._steps[step_id] = row
        self._step_weights[step_id] = weight
        self._total_weight += weight

    def step_started(self, step_id, subtitle=None):
        if step_id in self._steps:
            self._steps[step_id].set_state("loading")
            self.current_step_label.setText(f"→ {step_id}")
        if subtitle:
            self.subtitle_label.setText(subtitle)

    def step_done(self, step_id, status_text="✓"):
        if step_id in self._steps:
            self._steps[step_id].set_state("done", status_text)
        if step_id in self._step_weights:
            self._weights_done += self._step_weights[step_id]
            self._target_progress = int((self._weights_done / self._total_weight) * 100)

    def step_error(self, step_id, error_message=None):
        if step_id in self._steps:
            self._steps[step_id].set_state("error", "✕")
        if error_message:
            self.current_step_label.setText(f"❌ {error_message}")

    def set_subtitle(self, text):
        self.subtitle_label.setText(text)

    def set_message(self, text):
        self._title = text
        self.title_label.setText(text)

    def set_title(self, text):
        self._title = text
        self.title_label.setText(text)

    def set_percent(self, percent):
        self._target_progress = max(0, min(100, percent))

    def _smooth_progress(self):
        if self._current_progress < self._target_progress:
            diff = self._target_progress - self._current_progress
            step = max(1, diff // 6)
            self._current_progress = min(self._target_progress, self._current_progress + step)
            self.progress_bar.setValue(self._current_progress)
            self.percent_label.setText(f"{self._current_progress}%")
            if self._current_progress >= 100:
                self.current_step_label.setText("✅ Chargement terminé")
                self.subtitle_label.setText("Prêt")

    def stop(self):
        self.spinner.stop()
        self._smooth_timer.stop()
