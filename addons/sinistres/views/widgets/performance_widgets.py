"""
Widgets de performance et alertes pour le dashboard
- PerformanceCard : KPI de délais moyens
- AlertsBanner : bandeau d'alertes en haut du dashboard
- TopClaimsCard : Top 5 des sinistres les plus coûteux
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QPushButton, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from typing import List, Dict, Optional


# ============================================================
# TUILES DE PERFORMANCE
# ============================================================

class PerformanceTile(QFrame):
    """Tuile individuelle pour un KPI de performance"""
    
    def __init__(
        self,
        label: str,
        value: str = "—",
        target: str = "",
        color: str = "#1a73e8",
        icon: str = "",
        parent=None
    ):
        super().__init__(parent)
        
        self._color = color
        self._target = target
        
        self.setStyleSheet(f"""
            PerformanceTile {{
                background-color: {color}10;
                border: 1px solid {color}30;
                border-left: 3px solid {color};
                border-radius: 8px;
            }}
        """)
        self.setObjectName("PerformanceTile")
        self.setMinimumHeight(70)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)
        
        # Ligne 1 : icône + label
        header = QHBoxLayout()
        header.setSpacing(4)
        
        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 12px;")
            header.addWidget(icon_lbl)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 10px; color: {color}; font-weight: 600;")
        header.addWidget(lbl)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Ligne 2 : valeur + cible
        value_row = QHBoxLayout()
        value_row.setSpacing(8)
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #1e293b;
        """)
        value_row.addWidget(self.value_label)
        
        if target:
            self.target_label = QLabel(target)
            self.target_label.setStyleSheet("""
                font-size: 9px;
                color: #94a3b8;
            """)
            value_row.addWidget(self.target_label)
        
        value_row.addStretch()
        layout.addLayout(value_row)
    
    def set_value(self, value: str):
        self.value_label.setText(value)


# ============================================================
# CARTE PERFORMANCE
# ============================================================

class PerformanceCard(QFrame):
    """
    Carte de performance :
    ┌─────────────────────────────────────────┐
    │  📊 Performance                         │
    │  ┌──────────┬──────────┐                │
    │  │ Délai    │ Délai    │                │
    │  │ instr.   │ expertise│                │
    │  │ 12 j     │ 28 j     │                │
    │  ├──────────┼──────────┤                │
    │  │ Délai    │ Taux de  │                │
    │  │ règlement│ clôture  │                │
    │  │ 8 j      │ 78%      │                │
    │  └──────────┴──────────┘                │
    └─────────────────────────────────────────┘
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            PerformanceCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        self.setObjectName("PerformanceCard")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        
        # En-tête
        header = QHBoxLayout()
        header.setSpacing(6)
        
        icon = QLabel("📊")
        icon.setStyleSheet("font-size: 15px;")
        header.addWidget(icon)
        
        title = QLabel("Performance")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        header.addWidget(title)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Grille 2x2
        grid = QGridLayout()
        grid.setSpacing(8)
        
        self.tile_instruction = PerformanceTile(
            "Délai d'instruction",
            "—",
            "cible < 15 j",
            "#3b82f6",
            "📋",
        )
        self.tile_expertise = PerformanceTile(
            "Délai d'expertise",
            "—",
            "cible < 30 j",
            "#8b5cf6",
            "🔬",
        )
        self.tile_reglement = PerformanceTile(
            "Délai de règlement",
            "—",
            "cible < 10 j",
            "#22c55e",
            "💳",
        )
        self.tile_cloture = PerformanceTile(
            "Taux de clôture",
            "—",
            "cible > 80%",
            "#06b6d4",
            "✅",
        )
        
        grid.addWidget(self.tile_instruction, 0, 0)
        grid.addWidget(self.tile_expertise, 0, 1)
        grid.addWidget(self.tile_reglement, 1, 0)
        grid.addWidget(self.tile_cloture, 1, 1)
        
        layout.addLayout(grid)
    
    def set_data(self, stats: dict):
        """
        Met à jour les 4 KPI.
        
        stats = {
            'delai_instruction': float (jours),
            'delai_expertise': float (jours),
            'delai_reglement': float (jours),
            'taux_cloture': float (%),
        }
        """
        # Délai instruction
        di = stats.get('delai_instruction', 0)
        self.tile_instruction.set_value(f"{di:.1f} j" if di else "—")
        
        # Délai expertise
        de = stats.get('delai_expertise', 0)
        self.tile_expertise.set_value(f"{de:.1f} j" if de else "—")
        
        # Délai règlement
        dr = stats.get('delai_reglement', 0)
        self.tile_reglement.set_value(f"{dr:.1f} j" if dr else "—")
        
        # Taux clôture
        tc = stats.get('taux_cloture', 0)
        self.tile_cloture.set_value(f"{tc:.1f}%" if tc else "—")


# ============================================================
# BANDEAU D'ALERTES
# ============================================================

class AlertsBanner(QFrame):
    """
    Bandeau horizontal d'alertes :
    ┌─────────────────────────────────────────────────────────────┐
    │  ⚠️  3 expertises en retard • 2 règlements en attente • ... │
    └─────────────────────────────────────────────────────────────┘
    """
    
    alert_clicked = Signal(str)   # émet le type d'alerte cliqué
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            AlertsBanner {
                background-color: #fef3c7;
                border: 1px solid #fde047;
                border-radius: 10px;
            }
        """)
        self.setObjectName("AlertsBanner")
        self.setMinimumHeight(44)
        self.setMaximumHeight(60)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(12)
        
        # Icône
        self.icon_lbl = QLabel("⚠️")
        self.icon_lbl.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.icon_lbl)
        
        # Conteneur des alertes
        self.alerts_layout = QHBoxLayout()
        self.alerts_layout.setSpacing(12)
        layout.addLayout(self.alerts_layout)
        
        layout.addStretch()
        
        # État vide
        self.empty_lbl = QLabel("Aucune alerte")
        self.empty_lbl.setStyleSheet("""
            color: #65a30d;
            font-size: 11px;
            font-weight: 600;
        """)
        self.empty_lbl.hide()
        layout.addWidget(self.empty_lbl)
    
    def set_alerts(self, alerts: List[Dict]):
        """
        Met à jour la liste des alertes.
        
        alerts = [
            {'type': 'expertise_retard', 'label': '3 expertises en retard', 'color': '#ef4444'},
            ...
        ]
        """
        # Vider
        while self.alerts_layout.count():
            item = self.alerts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Si aucune alerte
        if not alerts:
            self.setStyleSheet("""
                AlertsBanner {
                    background-color: #dcfce7;
                    border: 1px solid #86efac;
                    border-radius: 10px;
                }
            """)
            self.icon_lbl.setText("✅")
            self.empty_lbl.setText("Aucune alerte")
            self.empty_lbl.show()
            return
        
        # Style avec alertes
        self.setStyleSheet("""
            AlertsBanner {
                background-color: #fef3c7;
                border: 1px solid #fde047;
                border-radius: 10px;
            }
        """)
        self.icon_lbl.setText("⚠️")
        self.empty_lbl.hide()
        
        # Ajouter chaque alerte
        for i, alert in enumerate(alerts):
            btn = QPushButton(alert.get('label', ''))
            color = alert.get('color', '#ef4444')
            alert_type = alert.get('type', '')
            
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    color: {color};
                    border: 1px solid {color}40;
                    border-left: 3px solid {color};
                    border-radius: 6px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: 600;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {color}10;
                }}
            """)
            btn.clicked.connect(
                lambda checked=False, t=alert_type: self.alert_clicked.emit(t)
            )
            self.alerts_layout.addWidget(btn)
            
            # Séparateur entre alertes
            if i < len(alerts) - 1:
                sep = QLabel("•")
                sep.setStyleSheet("color: #94a3b8; font-size: 14px;")
                self.alerts_layout.addWidget(sep)


# ============================================================
# TOP 5 DES SINISTRES COÛTEUX
# ============================================================

class TopClaimRow(QFrame):
    """Ligne du Top 5"""
    
    def __init__(self, rang: int, sinistre: dict, statut_colors: dict, parent=None):
        super().__init__(parent)
        
        self.sinistre = sinistre
        
        self.setStyleSheet("""
            TopClaimRow {
                background-color: transparent;
                border-bottom: 1px solid #f1f5f9;
            }
            TopClaimRow:hover {
                background-color: #f8fafc;
            }
        """)
        self.setObjectName("TopClaimRow")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)
        
        # Rang
        rank_colors = {
            1: '#fbbf24',   # Or
            2: '#94a3b8',   # Argent
            3: '#d97706',   # Bronze
            4: '#64748b',   # Gris
            5: '#64748b',
        }
        rank_color = rank_colors.get(rang, '#64748b')
        
        rank_lbl = QLabel(f"#{rang}")
        rank_lbl.setFixedWidth(28)
        rank_lbl.setAlignment(Qt.AlignCenter)
        rank_lbl.setStyleSheet(f"""
            font-size: 11px;
            font-weight: bold;
            color: white;
            background-color: {rank_color};
            border-radius: 10px;
            padding: 2px;
        """)
        layout.addWidget(rank_lbl)
        
        # N° Sinistre
        numero = sinistre.get('numero_sinistre', '—')
        num_lbl = QLabel(numero)
        num_lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #1e293b;")
        num_lbl.setFixedWidth(110)
        layout.addWidget(num_lbl)
        
        # Client
        client = sinistre.get('client_nom', '—')
        client_lbl = QLabel(client)
        client_lbl.setStyleSheet("font-size: 10px; color: #475569;")
        client_lbl.setWordWrap(False)
        layout.addWidget(client_lbl, 1)
        
        # Montant
        montant = sinistre.get('montant_net', 0) or 0
        montant_lbl = QLabel(f"{montant:,.0f} F".replace(",", " "))
        montant_lbl.setStyleSheet("""
            font-size: 11px;
            font-weight: bold;
            color: #dc2626;
        """)
        montant_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(montant_lbl)


class TopClaimsCard(QFrame):
    """Carte Top 5 des sinistres les plus coûteux"""
    
    claim_clicked = Signal(dict)
    
    def __init__(self, statut_colors: dict, parent=None):
        super().__init__(parent)
        
        self.statut_colors = statut_colors
        
        self.setStyleSheet("""
            TopClaimsCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        self.setObjectName("TopClaimsCard")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        
        # En-tête
        header = QHBoxLayout()
        header.setSpacing(6)
        
        icon = QLabel("🏆")
        icon.setStyleSheet("font-size: 15px;")
        header.addWidget(icon)
        
        title = QLabel("Top 5 sinistres coûteux")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b;")
        header.addWidget(title)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Conteneur
        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(0)
        layout.addLayout(self.rows_layout)
    
    def set_sinistres(self, sinistres: List[Dict]):
        """Met à jour la liste"""
        # Vider
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not sinistres:
            empty = QLabel("Aucun sinistre")
            empty.setStyleSheet("""
                color: #94a3b8;
                font-size: 11px;
                font-style: italic;
                padding: 20px;
            """)
            empty.setAlignment(Qt.AlignCenter)
            self.rows_layout.addWidget(empty)
            return
        
        # Trier par montant décroissant
        tries = sorted(
            sinistres,
            key=lambda s: s.get('montant_net', 0) or 0,
            reverse=True
        )[:5]
        
        for i, s in enumerate(tries, start=1):
            row = TopClaimRow(i, s, self.statut_colors)
            row.setCursor(Qt.PointingHandCursor)
            row.mousePressEvent = lambda e, sin=s: self.claim_clicked.emit(sin)
            self.rows_layout.addWidget(row)