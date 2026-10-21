from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from addons.Automobiles.views.automobile_style import COLORS, FONTS, SPACING, field_style


def make_section(icon_name: str, title: str, subtitle: str = "") -> QWidget:
    """En-tête de section : icône + titre en majuscules + sous-titre"""
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 0, 0, 8)
    h.setSpacing(10)

    # Icône discrète
    ic = QLabel()
    ic.setPixmap(qta.icon(icon_name, color=COLORS['text_muted']).pixmap(QSize(16, 16)))
    ic.setFixedSize(20, 20)
    h.addWidget(ic, 0, Qt.AlignTop)

    # Bloc titre
    block = QVBoxLayout()
    block.setSpacing(1)
    t = QLabel(title.upper())
    t.setStyleSheet(f"""
        font-size: 11px;
        font-weight: 700;
        color: {COLORS['text_muted']};
        letter-spacing: 1px;
    """)
    block.addWidget(t)
    if subtitle:
        s = QLabel(subtitle)
        s.setStyleSheet(f"font-size: 11px; color: {COLORS['text_hint']};")
        block.addWidget(s)
    h.addLayout(block, 1)
    return w


def make_field(label_text: str, widget: QWidget, required: bool = False) -> QWidget:
    """Champ avec label au-dessus"""
    w = QWidget()
    v = QVBoxLayout(w)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(4)

    lbl = QLabel(label_text + (" *" if required else ""))
    lbl.setStyleSheet(f"""
        font-size: 12px;
        font-weight: 500;
        color: {COLORS['text']};
    """)
    v.addWidget(lbl)
    v.addWidget(widget)
    return w


def make_row(*widgets, spacing: int = 12) -> QWidget:
    """Range des widgets horizontalement avec un espacement cohérent"""
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(spacing)
    for wdg in widgets:
        h.addWidget(wdg, 1)
    return w