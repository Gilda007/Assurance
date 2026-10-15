"""
Widget de timeline verticale pour le suivi d'un recours.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
)
from PySide6.QtCore import Qt


class RecoursTimelineWidget(QWidget):
    """
    Timeline verticale affichant l'historique d'un recours.
    Chaque événement est affiché sous forme de carte avec :
    - Icône colorée
    - Date
    - Titre
    - Description
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.evenements = []
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(20, 20, 20, 20)
        self.container_layout.setSpacing(0)
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)
    
    def set_evenements(self, evenements: list):
        """Met à jour la timeline avec une liste d'événements"""
        self.evenements = evenements
        
        # Vider
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not evenements:
            empty = QLabel("Aucun événement dans l'historique")
            empty.setStyleSheet("""
                color: #94a3b8;
                font-size: 13px;
                font-style: italic;
                padding: 40px;
            """)
            empty.setAlignment(Qt.AlignCenter)
            self.container_layout.addWidget(empty)
            return
        
        # Afficher chaque événement
        for i, ev in enumerate(evenements):
            self.container_layout.addWidget(self._make_event_widget(ev, i, len(evenements)))
        
        self.container_layout.addStretch()
    
    def _make_event_widget(self, ev: dict, index: int, total: int) -> QWidget:
        """Crée le widget d'un événement"""
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent;")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # ============================================================
        # Colonne gauche : timeline (pastille + ligne verticale)
        # ============================================================
        timeline_col = QVBoxLayout()
        timeline_col.setContentsMargins(0, 0, 0, 0)
        timeline_col.setSpacing(0)
        
        # Pastille colorée
        dot = QFrame()
        dot.setFixedSize(36, 36)
        dot.setStyleSheet(f"""
            QFrame {{
                background-color: {ev.get('couleur', '#1a73e8')};
                border-radius: 18px;
                border: 3px solid white;
            }}
        """)
        dot_layout = QVBoxLayout(dot)
        dot_layout.setContentsMargins(0, 0, 0, 0)
        dot_icon = QLabel(ev.get('icone', '📌'))
        dot_icon.setStyleSheet("font-size: 16px; background: transparent;")
        dot_icon.setAlignment(Qt.AlignCenter)
        dot_layout.addWidget(dot_icon)
        
        timeline_col.addWidget(dot, 0, Qt.AlignTop | Qt.AlignHCenter)
        
        # Ligne verticale (sauf dernier)
        if index < total - 1:
            line = QFrame()
            line.setFixedWidth(2)
            line.setStyleSheet("background-color: #cbd5e1;")
            line.setMinimumHeight(80)
            timeline_col.addWidget(line, 1, Qt.AlignHCenter)
        
        layout.addLayout(timeline_col)
        
        # ============================================================
        # Colonne droite : carte d'événement
        # ============================================================
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-left: 4px solid {ev.get('couleur', '#1a73e8')};
                border-radius: 8px;
            }}
        """)
        card.setMinimumHeight(70)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(4)
        
        # Ligne 1 : Date + Titre
        line1 = QHBoxLayout()
        line1.setSpacing(10)
        
        date_str = self._format_date(ev.get('date'))
        lbl_date = QLabel(date_str)
        lbl_date.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        line1.addWidget(lbl_date)
        
        lbl_titre = QLabel(ev.get('titre', ''))
        lbl_titre.setStyleSheet(f"""
            color: {ev.get('couleur', '#1e293b')};
            font-size: 13px;
            font-weight: bold;
        """)
        line1.addWidget(lbl_titre)
        
        # Montant à droite
        montant = ev.get('montant')
        if montant:
            lbl_montant = QLabel(f"{montant:,.0f} FCFA")
            lbl_montant.setStyleSheet(f"""
                color: {ev.get('couleur', '#1a73e8')};
                font-size: 13px;
                font-weight: bold;
            """)
            lbl_montant.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            line1.addStretch()
            line1.addWidget(lbl_montant)
        else:
            line1.addStretch()
        
        card_layout.addLayout(line1)
        
        # Ligne 2 : Description
        description = ev.get('description', '')
        if description:
            lbl_desc = QLabel(description)
            lbl_desc.setStyleSheet("color: #475569; font-size: 11px;")
            lbl_desc.setWordWrap(True)
            card_layout.addWidget(lbl_desc)
        
        layout.addWidget(card, 1)
        
        return widget
    
    def _format_date(self, date_str) -> str:
        """Formate une date ISO en français"""
        if not date_str:
            return "—"
        try:
            s = str(date_str).replace('T', ' ')[:16]
            from datetime import datetime
            dt = datetime.strptime(s, "%Y-%m-%d %H:%M")
            mois = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin',
                    'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
            return f"{dt.day:02d} {mois[dt.month - 1]} {dt.year} {dt.hour:02d}:{dt.minute:02d}"
        except Exception:
            return str(date_str)[:16]