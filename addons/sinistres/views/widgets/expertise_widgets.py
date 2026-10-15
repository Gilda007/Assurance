"""
Widgets pour l'onglet Expertises
KpiExpertiseCard, GaugeArc, ExpertTooltip, ExpertiseRow
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QPushButton, QToolTip
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPixmap, QPolygonF
import math


# ============================================================
# GAUGE EN ARC (demi-cercle avec zones colorées)
# ============================================================

class GaugeArc(QWidget):
    """Jauge demi-cercle avec zones vert/orange/rouge"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._percent = 0
        self._label = ""
        self.setFixedSize(90, 55)
    
    def set_data(self, percent: float, label: str = ""):
        self._percent = max(0, min(100, percent))
        self._label = label or f"{int(self._percent)}%"
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        rect = QRectF(8, 8, w - 16, (h - 8) * 2)
        
        # Zones colorées (vert, orange, rouge)
        zones = [
            (0, 50, "#22c55e"),    # 0-50% vert
            (50, 80, "#f59e0b"),   # 50-80% orange
            (80, 100, "#ef4444"),  # 80-100% rouge
        ]
        
        for start, end, color in zones:
            span = (end - start) / 100
            start_angle = 180 - (start / 100 * 180)
            span_angle = -int(span * 180)
            
            pen = QPen(QColor(color), 12, Qt.SolidLine, Qt.FlatCap)
            painter.setPen(pen)
            painter.drawArc(rect, int(start_angle * 16), int(span_angle * 16))
        
        # Aiguille
        ratio = self._percent / 100
        angle_deg = 180 - ratio * 180
        angle_rad = math.radians(angle_deg)
        
        cx = w / 2
        cy = 8 + (h - 8)
        length = (w - 16) / 2 - 6
        
        end_x = cx + length * math.cos(angle_rad)
        end_y = cy - length * math.sin(angle_rad)
        
        painter.setPen(QPen(QColor("#1e293b"), 2, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(cx, cy), QPointF(end_x, end_y))
        
        painter.setBrush(QColor("#1e293b"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), 3, 3)
        
        # Label au centre
        painter.setPen(QColor("#1e293b"))
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(0, h - 22, w, 20), Qt.AlignCenter, self._label)


# ============================================================
# SPARKLINE (mini-courbe)
# ============================================================

class Sparkline(QWidget):
    """Mini-courbe pour visualiser une tendance"""
    
    def __init__(self, data: list = None, color: str = "#1a73e8", parent=None):
        super().__init__(parent)
        self._data = data or []
        self._color = color
        self.setMinimumHeight(30)
    
    def set_data(self, data: list, color: str = None):
        self._data = data or []
        if color:
            self._color = color
        self.update()
    
    def paintEvent(self, event):
        if len(self._data) < 2:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        min_v = min(self._data)
        max_v = max(self._data)
        rng = max_v - min_v if max_v != min_v else 1
        
        points = []
        for i, v in enumerate(self._data):
            px = (w * i) / (len(self._data) - 1)
            py = h - ((v - min_v) / rng) * (h - 4) - 2
            points.append(QPointF(px, py))
        
        # Aire
        painter.setPen(Qt.NoPen)
        color_light = QColor(self._color)
        color_light.setAlpha(40)
        painter.setBrush(color_light)
        
        poly = QPolygonF(points + [QPointF(points[-1].x(), h), QPointF(points[0].x(), h)])
        painter.drawPolygon(poly)
        
        # Ligne
        painter.setPen(QPen(QColor(self._color), 2))
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i+1])


# ============================================================
# KPI EXPERTISE CARD
# ============================================================

class KpiExpertiseCard(QFrame):
    """Carte KPI pour l'onglet Expertises"""
    
    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        self.setMinimumHeight(150)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(10)
        
        # Titre
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #1e293b;
            letter-spacing: 0.3px;
        """)
        title_lbl.setWordWrap(True)
        layout.addWidget(title_lbl)
        
        # Corps
        self.body_layout = QHBoxLayout()
        self.body_layout.setSpacing(10)
        layout.addLayout(self.body_layout)
        
        # Valeur
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c5282;
        """)
        self.body_layout.addWidget(self.lbl_value)
        self.body_layout.addStretch()
        
        # Zone widget (gauge, sparkline, etc.)
        self.widget_zone = QVBoxLayout()
        self.widget_zone.setSpacing(4)
        self.body_layout.addLayout(self.widget_zone)
        
        # Footer
        self.lbl_footer = QLabel("")
        self.lbl_footer.setStyleSheet("font-size: 11px; color: #64748b;")
        self.lbl_footer.setWordWrap(True)
        layout.addWidget(self.lbl_footer)
        
        layout.addStretch()
    
    def add_widget(self, widget: QWidget):
        self.widget_zone.addWidget(widget)
    
    def set_footer(self, text: str):
        self.lbl_footer.setText(text)
    
    def set_value(self, value: str):
        self.lbl_value.setText(value)


# ============================================================
# EXPERT TOOLTIP (widget flottant)
# ============================================================

class ExpertTooltip(QFrame):
    """Tooltip personnalisé pour un expert"""
    
    def __init__(self, expert_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
            }
        """)
        self.setMinimumWidth(280)
        self.setMaximumWidth(350)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        
        # --- Photo ---
        photo = QLabel("👤")
        photo.setFixedSize(70, 70)
        photo.setStyleSheet("""
            background-color: #e2e8f0;
            border-radius: 8px;
            font-size: 32px;
        """)
        photo.setAlignment(Qt.AlignCenter)
        
        # Si une photo existe
        photo_path = expert_data.get('photo')
        if photo_path:
            from addons.sinistres.services.file_service import get_file_service
            fs = get_file_service()
            abs_path = fs.get_absolute_path(photo_path)
            if abs_path:
                pixmap = QPixmap(abs_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothCrop)
                    photo.setPixmap(scaled)
        
        layout.addWidget(photo)
        
        # --- Infos ---
        info = QVBoxLayout()
        info.setSpacing(4)
        
        # Nom
        nom = expert_data.get('nom') or expert_data.get('expert_nom') or 'Expert'
        lbl_nom = QLabel(nom)
        lbl_nom.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        info.addWidget(lbl_nom)
        
        # Rating
        rating = expert_data.get('rating', 4.8)
        lbl_rating = QLabel(f"⭐ Rating: {rating} / 5")
        lbl_rating.setStyleSheet("font-size: 11px; color: #1e293b;")
        info.addWidget(lbl_rating)
        
        # Spécialités
        specialites = expert_data.get('specialites') or "Auto, Corporel"
        lbl_spec = QLabel(f"🛠️ Expertise: {specialites}")
        lbl_spec.setStyleSheet("font-size: 11px; color: #1e293b;")
        lbl_spec.setWordWrap(True)
        info.addWidget(lbl_spec)
        
        # Années d'expérience
        annees = expert_data.get('annees_experience', 15)
        lbl_annees = QLabel(f"📅 Years: {annees}+")
        lbl_annees.setStyleSheet("font-size: 11px; color: #1e293b;")
        info.addWidget(lbl_annees)
        
        info.addStretch()
        layout.addLayout(info, 1)
    
    def show_at(self, global_pos):
        """Affiche le tooltip à une position"""
        self.move(global_pos)
        self.show()


# ============================================================
# EXPERTISE ROW (ligne du tableau)
# ============================================================

class ExpertiseRow(QWidget):
    """Ligne d'une expertise"""
    
    edit_requested = Signal(dict)
    context_menu_requested = Signal(dict, object)
    
    def __init__(self, expertise: dict, expert_data: dict = None, parent=None):
        super().__init__(parent)
        self.expertise = expertise
        self.expert_data = expert_data or {}
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        
        self.setStyleSheet("""
            ExpertiseRow {
                background-color: white;
                border-bottom: 1px solid #f1f5f9;
            }
            ExpertiseRow:hover {
                background-color: #f8fafc;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # --- N° Mission ---
        num_lbl = QLabel(expertise.get('numero_mission') or 'N/A')
        num_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #1e293b;")
        num_lbl.setFixedWidth(130)
        layout.addWidget(num_lbl)
        
        # --- Expert (avec icône + tooltip) ---
        expert_container = QWidget()
        expert_layout = QHBoxLayout(expert_container)
        expert_layout.setContentsMargins(0, 0, 0, 0)
        expert_layout.setSpacing(8)
        
        # Avatar
        avatar = QLabel("👤")
        avatar.setFixedSize(28, 28)
        avatar.setStyleSheet("""
            background-color: #e2e8f0;
            border-radius: 14px;
            font-size: 14px;
        """)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setCursor(Qt.PointingHandCursor)
        
        # Installer le tooltip au survol
        avatar.enterEvent = lambda e, ed=self.expert_data: self._show_expert_tooltip(e, ed)
        avatar.leaveEvent = lambda e: self._hide_expert_tooltip()
        
        expert_layout.addWidget(avatar)
        
        # Nom
        nom = expertise.get('expert_nom') or '—'
        nom_lbl = QLabel(nom)
        nom_lbl.setStyleSheet("font-size: 12px; color: #1a73e8; text-decoration: underline;")
        nom_lbl.setCursor(Qt.PointingHandCursor)
        expert_layout.addWidget(nom_lbl)
        expert_layout.addStretch()
        
        expert_container.setFixedWidth(130)
        layout.addWidget(expert_container)
        
        # --- Type ---
        type_lbl = QLabel(expertise.get('type_expertise') or '—')
        type_lbl.setStyleSheet("font-size: 12px; color: #1e293b;")
        layout.addWidget(type_lbl, 1)
        
        # --- Date ---
        date_str = self._format_date(expertise.get('date_mission'))
        date_lbl = QLabel(date_str)
        date_lbl.setStyleSheet("font-size: 12px; color: #64748b;")
        date_lbl.setFixedWidth(110)
        date_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(date_lbl)
        
        # --- Échéance ---
        ech_str = self._format_date(expertise.get('date_echeance'))
        ech_lbl = QLabel(ech_str)
        ech_lbl.setStyleSheet("font-size: 12px; color: #64748b;")
        ech_lbl.setFixedWidth(110)
        ech_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(ech_lbl)
        
        # --- Statut ---
        statut = expertise.get('statut') or 'INCONNU'
        statut_cfg = self._get_statut_config(statut)
        statut_lbl = QLabel(statut_cfg['label'])
        statut_lbl.setStyleSheet(f"""
            background-color: {statut_cfg['bg']};
            color: {statut_cfg['fg']};
            padding: 4px 14px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        """)
        statut_lbl.setFixedWidth(110)
        statut_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(statut_lbl)
        
        # Stockage
        self._tooltip = None
    
    def _show_expert_tooltip(self, event, expert_data):
        """Affiche le tooltip expert"""
        if not expert_data:
            return
        
        self._tooltip = ExpertTooltip(expert_data, parent=self)
        pos = self.mapToGlobal(event.position().toPoint() if hasattr(event, 'position') else event.pos())
        # Décaler pour ne pas masquer
        self._tooltip.show_at(pos + type(pos)(20, 20))
    
    def _hide_expert_tooltip(self):
        """Cache le tooltip expert"""
        if self._tooltip:
            self._tooltip.hide()
            self._tooltip.deleteLater()
            self._tooltip = None
    
    def _format_date(self, date_val) -> str:
        """Formate une date ISO en '14 Sept. 2026'"""
        if not date_val:
            return "—"
        try:
            s = str(date_val)[:10]
            from datetime import datetime
            dt = datetime.strptime(s, "%Y-%m-%d")
            mois = ['Jan', 'Fév', 'Mars', 'Avr', 'Mai', 'Juin',
                    'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc']
            return f"{dt.day} {mois[dt.month - 1]}. {dt.year}"
        except Exception:
            return str(date_val)[:10]
    
    def _get_statut_config(self, statut: str) -> dict:
        """Retourne la config visuelle d'un statut"""
        mapping = {
            'CREEE':        {'label': 'Créée',         'bg': '#f1f5f9', 'fg': '#64748b'},
            'AFFECTEE':     {'label': 'Affectée',      'bg': '#dbeafe', 'fg': '#1e40af'},
            'EN_COURS':     {'label': 'En cours',      'bg': '#fef3c7', 'fg': '#92400e'},
            'RAPPORT_RECU': {'label': 'Rapport remis', 'bg': '#dcfce7', 'fg': '#166534'},
            'RAPPORT_REÇU': {'label': 'Rapport remis', 'bg': '#dcfce7', 'fg': '#166534'},
            'VALIDE':       {'label': 'Validée',       'bg': '#22c55e', 'fg': 'white'},
            'ANNULE':       {'label': 'Annulée',       'bg': '#fee2e2', 'fg': '#991b1b'},
        }
        return mapping.get(statut, {'label': statut, 'bg': '#f1f5f9', 'fg': '#64748b'})
    
    def _on_context_menu(self, pos):
        """Émet un signal pour le menu contextuel"""
        global_pos = self.mapToGlobal(pos)
        self.context_menu_requested.emit(self.expertise, global_pos)