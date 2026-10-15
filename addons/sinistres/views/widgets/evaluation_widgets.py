"""
Widgets pour l'onglet Évaluations
KpiEvaluationCard avec donut intégré
"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QFont


class DonutEvaluation(QWidget):
    """Petit donut circulaire avec pourcentage au centre"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._percent = 0
        self._color = "#2c5282"
        self._label = ""
        self.setFixedSize(70, 70)
    
    def set_data(self, percent: float, color: str = "#2c5282", label: str = ""):
        self._percent = max(0, min(100, percent))
        self._color = color
        self._label = label
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        size = min(w, h) - 8
        rect = QRectF((w - size) / 2, (h - size) / 2, size, size)
        
        # Fond gris
        pen = QPen(QColor("#e2e8f0"), 6, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Arc coloré
        if self._percent > 0:
            pen = QPen(QColor(self._color), 6, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)
            span = -int(self._percent / 100 * 360 * 16)
            painter.drawArc(rect, 90 * 16, span)
        
        # Texte au centre
        painter.setPen(QColor("#1e293b"))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        text = self._label if self._label else f"{int(self._percent)}%"
        painter.drawText(rect, Qt.AlignCenter, text)


class KpiEvaluationCard(QFrame):
    """Carte KPI avec titre, valeur principale et donut"""
    
    def __init__(self, title: str, value: str, percent: float = 0,
                 donut_label: str = "", footer: str = "", parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        self.setMinimumHeight(150)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # Titre
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        layout.addWidget(title_lbl)
        
        # Corps : valeur + donut
        body = QHBoxLayout()
        body.setSpacing(15)
        
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet("font-size: 32px; font-weight: bold; color: #1e293b;")
        body.addWidget(self.lbl_value)
        
        body.addStretch()
        
        self.donut = DonutEvaluation()
        self.donut.set_data(percent, "#2c5282", donut_label)
        body.addWidget(self.donut)
        
        layout.addLayout(body)
        
        # Footer
        if footer:
            self.lbl_footer = QLabel(footer)
            self.lbl_footer.setStyleSheet("font-size: 11px; color: #64748b;")
            layout.addWidget(self.lbl_footer)
        else:
            self.lbl_footer = None
        
        layout.addStretch()
    
    def set_value(self, value: str, percent: float = None, donut_label: str = None):
        self.lbl_value.setText(value)
        if percent is not None or donut_label is not None:
            self.donut.set_data(
                percent if percent is not None else self.donut._percent,
                "#2c5282",
                donut_label if donut_label is not None else self.donut._label
            )
    
    def set_footer(self, text: str):
        if self.lbl_footer:
            self.lbl_footer.setText(text)


class FloatingAddButton(QFrame):
    """Bouton flottant bleu pour ajouter une évaluation"""
    
    from PySide6.QtCore import Signal
    clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFixedSize(110, 110)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                background-color: #1a73e8;
                border-radius: 12px;
            }
            QFrame:hover {
                background-color: #1557b0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        
        icon = QLabel("➕")
        icon.setStyleSheet("font-size: 32px; color: white; background: transparent;")
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)
        
        text = QLabel("Nouvelle\névaluation")
        text.setStyleSheet("""
            font-size: 11px;
            font-weight: bold;
            color: white;
            background: transparent;
        """)
        text.setAlignment(Qt.AlignCenter)
        layout.addWidget(text)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class EvaluationRow(QWidget):
    """Ligne d'une évaluation"""
    
    from PySide6.QtCore import Signal
    edit_requested = Signal(dict)
    validate_requested = Signal(dict)
    delete_requested = Signal(dict)
    context_menu_requested = Signal(dict, object)
    
    def __init__(self, evaluation: dict, parent=None):
        super().__init__(parent)
        self.evaluation = evaluation
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        
        self.setStyleSheet("""
            EvaluationRow {
                background-color: white;
                border-bottom: 1px solid #f1f5f9;
            }
            EvaluationRow:hover {
                background-color: #f8fafc;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)
        
        # --- N° Évaluation ---
        num_lbl = QLabel(evaluation.get('numero_evaluation', 'N/A'))
        num_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #1e293b;")
        num_lbl.setFixedWidth(130)
        layout.addWidget(num_lbl)
        
        # --- Date ---
        date_str = self._format_date(evaluation.get('created_at'))
        date_lbl = QLabel(date_str)
        date_lbl.setStyleSheet("font-size: 12px; color: #64748b;")
        date_lbl.setFixedWidth(110)
        layout.addWidget(date_lbl)
        
        # --- Type ---
        type_lbl = QLabel(evaluation.get('type_evaluation', 'N/A'))
        type_lbl.setStyleSheet("font-size: 12px; color: #1e293b;")
        type_lbl.setFixedWidth(130)
        layout.addWidget(type_lbl)
        
        # --- Expert ---
        expert_lbl = QLabel(evaluation.get('expert_nom', '—'))
        expert_lbl.setStyleSheet("font-size: 12px; color: #1e293b;")
        expert_lbl.setFixedWidth(130)
        layout.addWidget(expert_lbl)
        
        # --- Montant Brut ---
        brut = evaluation.get('montant_brut', 0) or 0
        brut_lbl = QLabel(f"{brut:,.0f}".replace(",", " "))
        brut_lbl.setStyleSheet("font-size: 12px; color: #1e293b;")
        brut_lbl.setFixedWidth(110)
        brut_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(brut_lbl)
        
        # --- Franchise ---
        fr = evaluation.get('franchise', 0) or 0
        fr_lbl = QLabel(f"{fr:,.0f}".replace(",", " "))
        fr_lbl.setStyleSheet("font-size: 12px; color: #64748b;")
        fr_lbl.setFixedWidth(100)
        fr_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(fr_lbl)
        
        # --- Montant Net ---
        net = evaluation.get('montant_net', 0) or 0
        net_lbl = QLabel(f"{net:,.0f}".replace(",", " "))
        net_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #1e293b;")
        net_lbl.setFixedWidth(110)
        net_lbl.setAlignment(Qt.AlignRight)
        layout.addWidget(net_lbl)
        
        # --- Statut (badge) ---
        statut = self._get_statut(evaluation)
        statut_lbl = QLabel(statut['label'])
        statut_lbl.setStyleSheet(f"""
            background-color: {statut['bg']};
            color: {statut['fg']};
            padding: 3px 12px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        """)
        statut_lbl.setFixedWidth(110)
        statut_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(statut_lbl)
        
        # --- Validée (checkbox) ---
        from PySide6.QtWidgets import QCheckBox
        checkbox = QCheckBox()
        checkbox.setChecked(bool(evaluation.get('est_validee')))
        checkbox.setFixedWidth(80)
        checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #cbd5e1;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #1a73e8;
                border-color: #1a73e8;
            }
        """)
        layout.addWidget(checkbox)
    
    def _get_statut(self, ev: dict) -> dict:
        if ev.get('est_validee'):
            return {'label': 'Validée', 'bg': '#22c55e', 'fg': 'white'}
        elif ev.get('montant_accepte'):
            return {'label': 'À valider', 'bg': '#f59e0b', 'fg': 'white'}
        else:
            return {'label': 'Brouillon', 'bg': '#94a3b8', 'fg': 'white'}
    
    def _format_date(self, dt) -> str:
        if not dt:
            return "—"
        try:
            return str(dt)[:10]
        except Exception:
            return "—"
    
    def _on_context_menu(self, pos):
        global_pos = self.mapToGlobal(pos)
        self.context_menu_requested.emit(self.evaluation, global_pos)