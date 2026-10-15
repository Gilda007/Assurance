"""
Widget carte pour un sinistre récent (mode cartes)
"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont


class RecentClaimCard(QFrame):
    """Carte individuelle d'un sinistre récent"""
    
    clicked = Signal(dict)
    
    def __init__(self, sinistre: dict, statut_colors: dict, parent=None):
        super().__init__(parent)
        self.sinistre = sinistre
        self._statut_colors = statut_colors
        
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(110)
        
        self.setStyleSheet("""
            RecentClaimCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
            RecentClaimCard:hover {
                border: 2px solid #1a73e8;
                background-color: #f8fafc;
            }
        """)
        self.setObjectName("RecentClaimCard")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)
        
        # ============================================================
        # Ligne 1 : Numéro + badge statut
        # ============================================================
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        
        numero = sinistre.get('numero_sinistre') or 'N/A'
        lbl_numero = QLabel(numero)
        lbl_numero.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #1e293b;
        """)
        row1.addWidget(lbl_numero)
        row1.addStretch()
        
        statut = sinistre.get('statut', 'INCONNU')
        color = self._statut_colors.get(statut, '#64748b')
        badge = QLabel(statut)
        badge.setStyleSheet(f"""
            background-color: {color};
            color: white;
            padding: 2px 8px;
            border-radius: 8px;
            font-size: 9px;
            font-weight: bold;
        """)
        badge.setAlignment(Qt.AlignCenter)
        row1.addWidget(badge)
        
        layout.addLayout(row1)
        
        # ============================================================
        # Ligne 2 : Client
        # ============================================================
        client_nom = sinistre.get('client_nom') or '—'
        lbl_client = QLabel(f"👤 {client_nom}")
        lbl_client.setStyleSheet("""
            font-size: 11px;
            color: #475569;
        """)
        lbl_client.setWordWrap(True)
        layout.addWidget(lbl_client)
        
        # ============================================================
        # Ligne 3 : Branche + Date
        # ============================================================
        row3 = QHBoxLayout()
        row3.setSpacing(8)
        
        branche = sinistre.get('branche') or '—'
        lbl_branche = QLabel(f"🏢 {branche}")
        lbl_branche.setStyleSheet("font-size: 10px; color: #64748b;")
        row3.addWidget(lbl_branche)
        
        row3.addStretch()
        
        date_str = (sinistre.get('date_survenance') or 
                    sinistre.get('date_declaration') or '')[:10]
        lbl_date = QLabel(date_str)
        lbl_date.setStyleSheet("font-size: 10px; color: #94a3b8;")
        row3.addWidget(lbl_date)
        
        layout.addLayout(row3)
        
        # ============================================================
        # Ligne 4 : Montant
        # ============================================================
        montant = sinistre.get('montant_net', 0) or 0
        lbl_montant = QLabel(f"💰 {montant:,.0f} FCFA".replace(",", " "))
        lbl_montant.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #1e293b;
        """)
        layout.addWidget(lbl_montant)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.sinistre)
        super().mousePressEvent(event)