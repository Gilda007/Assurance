"""
Widgets réutilisables pour l'onglet Tiers
TiersCard, KpiCardTiers, DonutWithLine
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont

from typing import Optional, List


# ============================================================
# KPI CARD
# ============================================================

class KpiCardTiers(QFrame):
    """Carte KPI pour l'onglet Tiers"""
    
    def __init__(self, title: str, value: str, subtitle: str = "", 
                 color: str = "#3b82f6", icon: str = "", parent=None):
        super().__init__(parent)
        self._color = color
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                border-left: 5px solid {color};
            }}
        """)
        self.setMinimumHeight(110)
        self.setMaximumHeight(130)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)
        
        # Titre
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(
            "color: #64748b; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;"
        )
        layout.addWidget(title_lbl)
        
        # Valeur + icône
        row = QHBoxLayout()
        
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet(
            f"font-size: 32px; font-weight: bold; color: #1e293b;"
        )
        row.addWidget(self.lbl_value)
        
        row.addStretch()
        
        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(f"font-size: 32px; color: {color}; opacity: 0.3;")
            row.addWidget(icon_lbl)
        
        layout.addLayout(row)
        
        # Sous-titre
        if subtitle:
            self.lbl_sub = QLabel(subtitle)
            self.lbl_sub.setStyleSheet("color: #94a3b8; font-size: 10px; font-style: italic;")
            self.lbl_sub.setWordWrap(True)
            layout.addWidget(self.lbl_sub)
    
    def set_value(self, value: str):
        self.lbl_value.setText(value)


# ============================================================
# DONUT + COURBE (KPI graphique)
# ============================================================

class DonutWithLine(QWidget):
    """Donut avec pourcentage + courbe simple"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._percent = 0
        self._color = "#22c55e"
        self._line_data: List[float] = []
        self._line_color = "#22c55e"
        self.setMinimumHeight(110)
    
    def set_data(self, percent: float, color: str = "#22c55e",
                 line_data: Optional[List[float]] = None,
                 line_color: Optional[str] = None):
        self._percent = max(0, min(100, percent))
        self._color = color
        if line_data is not None:
            self._line_data = line_data
        self._line_color = line_color or color
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # --- Donut (gauche, ~40%) ---
        donut_size = min(h - 20, int(w * 0.4))
        donut_rect = QRectF(10, (h - donut_size) / 2, donut_size, donut_size)
        
        # Fond gris
        pen = QPen(QColor("#e2e8f0"), 8, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(donut_rect, 0, 360 * 16)
        
        # Arc coloré
        pen = QPen(QColor(self._color), 8, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        span = -int(self._percent / 100 * 360 * 16)
        painter.drawArc(donut_rect, 90 * 16, span)
        
        # Pourcentage au centre
        painter.setPen(QColor("#1e293b"))
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        text = f"{int(self._percent)}%"
        painter.drawText(donut_rect, Qt.AlignCenter, text)
        
        # --- Courbe (droite) ---
        if len(self._line_data) >= 2:
            line_x0 = donut_size + 25
            line_w = w - line_x0 - 10
            line_h = h - 30
            line_y0 = 15
            
            min_v = min(self._line_data)
            max_v = max(self._line_data)
            rng = max_v - min_v if max_v != min_v else 1
            
            points = []
            for i, v in enumerate(self._line_data):
                px = line_x0 + (line_w * i / (len(self._line_data) - 1))
                py = line_y0 + line_h - ((v - min_v) / rng) * line_h
                points.append(QPointF(px, py))
            
            # Aire sous la courbe
            painter.setPen(Qt.NoPen)
            color_light = QColor(self._line_color)
            color_light.setAlpha(40)
            painter.setBrush(QBrush(color_light))
            
            from PySide6.QtGui import QPolygonF
            poly = QPolygonF(points + [QPointF(points[-1].x(), line_y0 + line_h),
                                        QPointF(points[0].x(), line_y0 + line_h)])
            painter.drawPolygon(poly)
            
            # Ligne
            pen = QPen(QColor(self._line_color), 2)
            painter.setPen(pen)
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i+1])


# ============================================================
# CARTE TIERS
# ============================================================

class TiersCard(QFrame):
    """Carte individuelle d'un tiers"""
    
    clicked = Signal(dict)      # Clic sur la carte
    contact_clicked = Signal(dict, str)  # (tiers, 'phone'/'email'/'info')
    
    def __init__(self, tiers: dict, parent=None):
        super().__init__(parent)
        self.tiers = tiers
        
        self.setStyleSheet("""
            QFrame#TiersCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
            QFrame#TiersCard:hover {
                border: 2px solid #1a73e8;
            }
        """)
        self.setObjectName("TiersCard")
        self.setMinimumHeight(180)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # --- En-tête : nom + type + badge statut ---
        header = QHBoxLayout()
        header.setSpacing(8)
        
        # Colonne gauche : nom + type
        left = QVBoxLayout()
        left.setSpacing(2)
        
        nom = tiers.get('nom', '') or ''
        prenom = tiers.get('prenom', '') or ''
        nom_complet = f"{nom} {prenom}".strip() or "Sans nom"
        
        lbl_nom = QLabel(nom_complet.upper())
        lbl_nom.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        left.addWidget(lbl_nom)
        
        type_tiers = self._format_type(tiers.get('type_tiers', ''))
        lbl_type = QLabel(f"👤 {type_tiers}")
        lbl_type.setStyleSheet("font-size: 11px; color: #64748b;")
        left.addWidget(lbl_type)
        
        header.addLayout(left, 1)
        
        # Badge statut
        statut = self._get_statut(tiers)
        badge = QLabel(statut['label'])
        badge.setStyleSheet(f"""
            background-color: {statut['bg']};
            color: {statut['fg']};
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        """)
        badge.setAlignment(Qt.AlignCenter)
        badge.setMaximumHeight(22)
        header.addWidget(badge)
        
        layout.addLayout(header)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #f1f5f9; max-height: 1px; border: none;")
        layout.addWidget(sep)
        
        # --- Coordonnées ---
        coord_layout = QHBoxLayout()
        coord_layout.setSpacing(15)
        
        # Téléphone
        col1 = QVBoxLayout()
        col1.setSpacing(2)
        lbl_tel_key = QLabel("Téléphone")
        lbl_tel_key.setStyleSheet("font-size: 10px; color: #94a3b8; font-weight: 600;")
        col1.addWidget(lbl_tel_key)
        tel = tiers.get('telephone') or "Non renseigné"
        lbl_tel_val = QLabel(tel)
        lbl_tel_val.setStyleSheet("font-size: 11px; color: #1e293b;")
        col1.addWidget(lbl_tel_val)
        coord_layout.addLayout(col1, 1)
        
        # Assurance
        col2 = QVBoxLayout()
        col2.setSpacing(2)
        lbl_ass_key = QLabel("Assurance")
        lbl_ass_key.setStyleSheet("font-size: 10px; color: #94a3b8; font-weight: 600;")
        col2.addWidget(lbl_ass_key)
        assurance = tiers.get('assurance') or tiers.get('compagnie_assurance') or "Non renseignée"
        lbl_ass_val = QLabel(assurance)
        lbl_ass_val.setStyleSheet("font-size: 11px; color: #1e293b;")
        col2.addWidget(lbl_ass_val)
        coord_layout.addLayout(col2, 1)
        
        # Police
        col3 = QVBoxLayout()
        col3.setSpacing(2)
        lbl_pol_key = QLabel("Police")
        lbl_pol_key.setStyleSheet("font-size: 10px; color: #94a3b8; font-weight: 600;")
        col3.addWidget(lbl_pol_key)
        police = tiers.get('police_assurance') or "Non fournie"
        lbl_pol_val = QLabel(police)
        lbl_pol_val.setStyleSheet("font-size: 11px; color: #1e293b;")
        col3.addWidget(lbl_pol_val)
        coord_layout.addLayout(col3, 1)
        
        layout.addLayout(coord_layout)
        
        # --- Boutons d'action ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        for icon, action in [("📞", "phone"), ("✉️", "email"), ("ℹ️", "info")]:
            btn = QPushButton(icon)
            btn.setFixedSize(28, 28)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e8f0fe;
                    border-color: #1a73e8;
                }
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, a=action: self.contact_clicked.emit(self.tiers, a))
            btn_layout.addWidget(btn)
        
        layout.addLayout(btn_layout)
        
        # Stockage pour accès
        self._nom_complet = nom_complet
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.tiers)
        super().mousePressEvent(event)
    
    # --- Helpers ---
    
    def _format_type(self, type_tiers: str) -> str:
        mapping = {
            'responsable': 'Conducteur',
            'victime': 'Victime',
            'temoin': 'Témoin',
            'assureur_adverse': 'Assureur adverse',
            'conducteur': 'Conducteur',
            'passager': 'Passager',
            'autre_conducteur': 'Autre conducteur',
        }
        return mapping.get((type_tiers or '').lower(), type_tiers or 'Tiers')
    
    def _get_statut(self, tiers: dict) -> dict:
        """Détermine le badge de statut"""
        tel = tiers.get('telephone')
        assurance = tiers.get('assurance')
        police = tiers.get('police_assurance')
        
        if tel and assurance and police:
            return {'label': 'CONTACTÉ', 'bg': '#dcfce7', 'fg': '#166534'}
        elif tel and (not assurance or not police):
            return {'label': 'INFO MANQUANTE', 'bg': '#fef3c7', 'fg': '#92400e'}
        elif not tel:
            return {'label': 'À RELANCER', 'bg': '#fed7aa', 'fg': '#9a3412'}
        else:
            return {'label': 'EN ATTENTE', 'bg': '#f1f5f9', 'fg': '#64748b'}


# ============================================================
# CARTE "+ AJOUTER"
# ============================================================

class AddTiersCard(QFrame):
    """Carte cliquable pour ajouter un tiers"""
    
    clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 2px dashed #cbd5e1;
                border-radius: 10px;
            }
            QFrame:hover {
                background-color: #e8f0fe;
                border-color: #1a73e8;
            }
        """)
        self.setMinimumHeight(180)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        
        icon = QLabel("➕")
        icon.setStyleSheet("font-size: 36px; color: #94a3b8;")
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)
        
        text = QLabel("Ajouter un nouveau tiers")
        text.setStyleSheet("font-size: 13px; color: #64748b; font-weight: 500;")
        text.setAlignment(Qt.AlignCenter)
        layout.addWidget(text)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)