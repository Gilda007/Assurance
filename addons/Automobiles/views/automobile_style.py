"""
Design System centralisé pour le module Automobile.
Un seul endroit pour changer les couleurs, la typographie, les espacements.
"""

# ============================================================
# PALETTE — 2 couleurs seulement (gris ardoise + bleu vif)
# ============================================================

COLORS = {
    "bg":          "#f4f4f5",     # Fond de page
    "card":        "#ffffff",     # Carte blanche
    "text":        "#18181b",     # Texte principal
    "text_muted":  "#71717a",     # Texte secondaire
    "text_hint":   "#a1a1aa",     # Texte hint
    "border":      "#e4e4e7",     # Bordures
    "border_focus": "#18181b",    # Bordure au focus
    "primary":     "#1d4ed8",     # Bleu d'action
    "primary_hover": "#1e40af",
    "danger":      "#dc2626",     # Erreur
    "success":     "#059669",     # Succès
    "warning":     "#d97706",     # Alerte
}

# ============================================================
# TYPOGRAPHIE
# ============================================================

FONTS = {
    "family": "'Segoe UI', system-ui, -apple-system, sans-serif",
    "title":  {"size": "18px", "weight": 700},
    "subtitle": {"size": "13px", "weight": 400},
    "label":  {"size": "12px", "weight": 500},
    "value":  {"size": "13px", "weight": 400},
    "mono":   {"family": "'Consolas', monospace", "size": "13px"},
}

# ============================================================
# ESPACEMENTS (multiples de 4)
# ============================================================

SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "12px",
    "lg": "16px",
    "xl": "24px",
    "2xl": "32px",
}

# ============================================================
# STYLES PRÊTS À L'EMPLOI
# ============================================================

def field_style():
    return f"""
        QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit {{
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 9px 12px;
            font-size: 13px;
            color: {COLORS['text']};
            font-family: {FONTS['family']};
            min-height: 20px;
        }}
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
        QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
            border: 1px solid {COLORS['border_focus']};
        }}
        QLineEdit:disabled, QComboBox:disabled, QDateEdit:disabled {{
            background: {COLORS['bg']};
            color: {COLORS['text_hint']};
        }}
        QComboBox::drop-down, QDateEdit::drop-down {{
            border: none; width: 28px;
        }}
        QComboBox::down-arrow, QDateEdit::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {COLORS['text_muted']};
            margin-right: 10px;
        }}
    """

def section_style():
    return f"""
        QGroupBox {{
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            margin-top: 10px;
            padding-top: 16px;
            font-size: 12px;
            font-weight: 600;
            color: {COLORS['text_muted']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: {COLORS['card']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px;
        }}
    """

def label_style():
    return f"""
        QLabel {{
            font-size: 12px;
            font-weight: 500;
            color: {COLORS['text']};
            background: transparent;
        }}
    """

def hint_style():
    return f"""
        QLabel {{
            font-size: 11px;
            color: {COLORS['text_hint']};
            background: transparent;
        }}
    """