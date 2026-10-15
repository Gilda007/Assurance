"""
Barre KPI Claims - Design complet :
- Anneau circulaire (Total Claims)
- 5 blocs de statistiques avec pastilles
- Séparateurs verticaux
"""
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import QGraphicsDropShadowEffect

from addons.sinistres.views.widgets.kpi_ring import CircularProgressRing


# ============================================================
# CONSTANTES
# ============================================================

LABEL_COLOR = "#334155"
VALUE_COLOR = "#475569"
SEPARATOR_COLOR = "#e2e8f0"

PASTILLE_COLORS = {
    'claims':   "#fecaca",   # Pêche clair
    'open':     "#fed7aa",   # Orange clair
    'closed':   "#bbf7d0",   # Vert clair
    'recourse': "#fecaca",   # Rouge clair
    'today':    "#bfdbfe",   # Bleu clair
}


# ============================================================
# WIDGET PRINCIPAL
# ============================================================

class KpiClaimsBar(QFrame):
    """
    Carte KPI unique style moderne :
    ┌──────────────────────────────────────────────────────────────┐
    │  Total Claims  │ Claims │ Open │ Closed │ Recourse │ Today  │
    │   ╭──────╮     │   8    │  2   │   0    │    0     │   0    │
    │   │  8   │     │        │      │        │          │        │
    │   ╰──────╯     │        │      │        │          │        │
    └──────────────────────────────────────────────────────────────┘
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- Style de la carte ---
        self.setObjectName("KpiClaimsBar")
        self.setStyleSheet(f"""
            QFrame#KpiClaimsBar {{
                background-color: white;
                border: none;
                border-radius: 18px;
            }}
        """)
        # ============================================================
        # ✅ Effet d'ombrage subtil
        # ============================================================
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(15, 23, 42, 30))
        self.setGraphicsEffect(shadow)
        
        self.setMinimumHeight(220)
        
        # --- Layout horizontal ---
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(0)
        
        # ============================================================
        # BLOC 1 : Anneau Total Claims
        # ============================================================
        total_block = QVBoxLayout()
        total_block.setSpacing(8)
        total_block.setAlignment(Qt.AlignCenter)
        
        title_total = QLabel("Total Claims")
        title_total.setStyleSheet(f"""
            color: {LABEL_COLOR};
            font-size: 14px;
            font-weight: 500;
        """)
        title_total.setAlignment(Qt.AlignCenter)
        total_block.addWidget(title_total)
        
        self.ring = CircularProgressRing()
        total_block.addWidget(self.ring, alignment=Qt.AlignCenter)
        
        layout.addLayout(total_block)
        
        # ============================================================
        # SÉPARATEUR 1
        # ============================================================
        layout.addWidget(self._make_separator())
        
        # ============================================================
        # BLOCS 2-6 : Statistiques
        # ============================================================
        self.stat_claims = self._make_stat_block("Claims", "0", PASTILLE_COLORS['claims'])
        self.stat_open = self._make_stat_block("Open", "0", PASTILLE_COLORS['open'])
        self.stat_closed = self._make_stat_block("Closed", "0", PASTILLE_COLORS['closed'])
        self.stat_recourse = self._make_stat_block("In Recourse", "0", PASTILLE_COLORS['recourse'])
        self.stat_today = self._make_stat_block("New Today", "0", PASTILLE_COLORS['today'])
        
        for stat_block in [
            self.stat_claims,
            self.stat_open,
            self.stat_closed,
            self.stat_recourse,
            self.stat_today,
        ]:
            layout.addLayout(stat_block['layout'], 1)
            layout.addWidget(self._make_separator())
        
        # Retirer le dernier séparateur
        last_item = layout.itemAt(layout.count() - 1)
        if last_item and last_item.widget():
            last_item.widget().deleteLater()
            layout.removeItem(last_item)
    
    # ============================================================
    # HELPERS
    # ============================================================
    
    def _make_separator(self) -> QFrame:
        """Crée un séparateur vertical fin"""
        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background-color: {SEPARATOR_COLOR};")
        sep.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        return sep
    
    def _make_stat_block(self, label: str, value: str, pastille_color: str) -> dict:
        """Crée un bloc statistique (pastille + label + valeur)"""
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(15, 0, 15, 0)
        
        # --- Ligne 1 : pastille + label ---
        header = QHBoxLayout()
        header.setSpacing(6)
        header.setAlignment(Qt.AlignCenter)
        
        pastille = QLabel()
        pastille.setFixedSize(10, 10)
        pastille.setStyleSheet(f"""
            background-color: {pastille_color};
            border-radius: 5px;
        """)
        header.addWidget(pastille)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"""
            color: {LABEL_COLOR};
            font-size: 14px;
            font-weight: 400;
        """)
        header.addWidget(lbl)
        
        layout.addLayout(header)
        
        # --- Ligne 2 : valeur ---
        val = QLabel(value)
        val.setStyleSheet(f"""
            color: {VALUE_COLOR};
            font-size: 48px;
            font-weight: 600;
        """)
        val.setAlignment(Qt.AlignCenter)
        layout.addWidget(val)
        
        return {'layout': layout, 'value_label': val}
    
    # ============================================================
    # MISE À JOUR
    # ============================================================
    
    def set_data(self, total: int, claims: int, open_: int,
                 closed: int, recourse: int, today: int):
        """Met à jour toutes les valeurs"""
        # Anneau
        self.ring.set_value(total, max(total, 1))
        
        # Blocs
        self.stat_claims['value_label'].setText(str(claims))
        self.stat_open['value_label'].setText(str(open_))
        self.stat_closed['value_label'].setText(str(closed))
        self.stat_recourse['value_label'].setText(str(recourse))
        self.stat_today['value_label'].setText(str(today))