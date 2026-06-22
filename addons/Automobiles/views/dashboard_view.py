# addons/Automobiles/views/dashboard_view.py
"""
Vue Dashboard avec graphiques modernes
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QLabel, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtCharts import QChartView

from addons.Automobiles.views.style import Colors, Spacing, Fonts
from addons.Automobiles.views.widgets.modern_card import ModernCard, StatsCard


class DashboardView(QWidget):
    """Dashboard moderne avec KPI et graphiques"""
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.kpi_cards = {} 
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.XL)
        
        # Zone scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(Spacing.XL)
        
        # Ligne 1: Cartes KPI
        self.setup_kpi_cards()
        content_layout.addLayout(self.kpi_layout)
        
        # Ligne 2: Graphiques principaux
        row2 = QHBoxLayout()
        row2.setSpacing(Spacing.XL)
        
        self.contracts_chart = self.create_contracts_chart()
        self.revenue_chart = self.create_revenue_chart()
        
        row2.addWidget(self.contracts_chart, 1)
        row2.addWidget(self.revenue_chart, 1)
        content_layout.addLayout(row2)
        
        # Ligne 3: Activité récente
        self.setup_recent_activity()
        content_layout.addWidget(self.recent_activity_card)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def setup_kpi_cards(self):
        """Configure les cartes KPI"""
        self.kpi_layout = QGridLayout()
        self.kpi_layout.setSpacing(Spacing.LG)
        
        self.kpi_cards = {}
        
        kpi_data = [
            {"key": "vehicles", "title": "VÉHICULES", "icon": "🚗", "color": Colors.PRIMARY},
            {"key": "contracts", "title": "CONTRATS ACTIFS", "icon": "📄", "color": Colors.SUCCESS},
            {"key": "clients", "title": "CLIENTS", "icon": "👥", "color": Colors.INFO},
            {"key": "revenue", "title": "CHIFFRE D'AFFAIRES", "icon": "💰", "color": Colors.WARNING},
        ]
        
        for i, data in enumerate(kpi_data):
            card = StatsCard(data["title"], 0, data["icon"], data["color"])
            self.kpi_layout.addWidget(card, 0, i)
            self.kpi_cards[data["key"]] = card
    
    def create_contracts_chart(self):
        """Crée le graphique des contrats"""
        card = ModernCard(title="Évolution des contrats", icon="📊")
        # TODO: Ajouter le graphique
        return card
    
    def create_revenue_chart(self):
        """Crée le graphique des revenus"""
        card = ModernCard(title="Revenus mensuels", icon="💰")
        # TODO: Ajouter le graphique
        return card
    
    def setup_recent_activity(self):
        """Configure la section d'activité récente"""
        self.recent_activity_card = ModernCard(title="Activité récente", icon="🕐")
        # TODO: Ajouter la liste des activités
        activity_label = QLabel("• 3 nouveaux contrats aujourd'hui\n• 5 véhicules ajoutés cette semaine")
        activity_label.setStyleSheet(f"font-size: {Fonts.BODY}px; padding: {Spacing.MD}px;")
        self.recent_activity_card.add_widget(activity_label)
    
    def load_data(self):
        """Charge les données du dashboard"""
        if not self.controller:
            return
        
        try:
            # Charger les stats
            vehicle_stats = self.controller.get_vehicle_stats() if hasattr(self.controller, 'get_vehicle_stats') else {'total': 0}
            contract_stats = self.controller.get_contract_stats() if hasattr(self.controller, 'get_contract_stats') else {'active': 0, 'total_premium': 0}
            contact_stats = self.controller.get_contact_stats() if hasattr(self.controller, 'get_contact_stats') else {'total': 0}
            
            # Mettre à jour les KPI
            self.kpi_cards["vehicles"].animate_value(vehicle_stats.get('total', 0))
            self.kpi_cards["contracts"].animate_value(contract_stats.get('active', 0))
            self.kpi_cards["clients"].animate_value(contact_stats.get('total', 0))
            self.kpi_cards["revenue"].animate_value(int(contract_stats.get('total_premium', 0)))
            
        except Exception as e:
            print(f"Erreur chargement dashboard: {e}")