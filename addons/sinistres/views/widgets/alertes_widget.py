"""
Widget d'affichage des alertes recours.
Peut être intégré dans n'importe quelle page.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal


class AlertesWidget(QWidget):
    """Panneau d'alertes compact"""
    
    alerte_clicked = Signal(dict)  # Émet l'alerte cliquée
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.alertes = []
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # En-tête
        header = QHBoxLayout()
        
        self.lbl_titre = QLabel("🔔 Alertes")
        self.lbl_titre.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #1e293b;"
        )
        header.addWidget(self.lbl_titre)
        
        header.addStretch()
        
        self.lbl_count = QLabel("0")
        self.lbl_count.setStyleSheet("""
            background-color: #ef4444;
            color: white;
            padding: 2px 10px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
        """)
        self.lbl_count.setAlignment(Qt.AlignCenter)
        header.addWidget(self.lbl_count)
        
        layout.addLayout(header)
        
        # Zone scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        scroll.setMaximumHeight(200)
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(6)
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)
    
    def set_alertes(self, alertes: list):
        """Met à jour la liste des alertes"""
        self.alertes = alertes
        self.lbl_count.setText(str(len(alertes)))
        
        # Vider
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not alertes:
            empty = QLabel("✅ Aucune alerte")
            empty.setStyleSheet("""
                color: #22c55e;
                font-size: 12px;
                font-style: italic;
                padding: 20px;
            """)
            empty.setAlignment(Qt.AlignCenter)
            self.container_layout.addWidget(empty)
            return
        
        # Afficher chaque alerte
        for a in alertes:
            self.container_layout.addWidget(self._make_alerte_widget(a))
        
        self.container_layout.addStretch()
    
    def _make_alerte_widget(self, alerte: dict) -> QFrame:
        """Crée un widget pour une alerte"""
        niveau = alerte.get('niveau', 'WARNING')
        
        colors = {
            'INFO': ('#dbeafe', '#1e40af', '#3b82f6'),
            'WARNING': ('#fef3c7', '#92400e', '#f59e0b'),
            'CRITICAL': ('#fee2e2', '#991b1b', '#ef4444'),
        }
        bg, fg, border = colors.get(niveau, colors['WARNING'])
        
        widget = QFrame()
        widget.setCursor(Qt.PointingHandCursor)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-left: 4px solid {border};
                border-radius: 6px;
                padding: 10px;
            }}
            QFrame:hover {{
                background-color: {bg};
                border-left: 5px solid {border};
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Ligne 1 : code + message
        line1 = QHBoxLayout()
        
        code_lbl = QLabel(alerte.get('code', ''))
        code_lbl.setStyleSheet(f"""
            background-color: {border};
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
        """)
        line1.addWidget(code_lbl)
        
        numero = alerte.get('numero_recours')
        if numero:
            num_lbl = QLabel(f"📋 {numero}")
            num_lbl.setStyleSheet(f"font-size: 11px; color: {fg}; font-weight: bold;")
            line1.addWidget(num_lbl)
        
        line1.addStretch()
        layout.addLayout(line1)
        
        # Ligne 2 : message
        msg_lbl = QLabel(alerte.get('message', ''))
        msg_lbl.setStyleSheet(f"font-size: 11px; color: {fg};")
        msg_lbl.setWordWrap(True)
        layout.addWidget(msg_lbl)
        
        # Clic
        widget.mousePressEvent = lambda e, a=alerte: self.alerte_clicked.emit(a)
        
        return widget