


# addons/Automobiles/views/dashboard_view.py
"""
Vue Dashboard avec graphiques - Version avec Font Awesome
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar
)
from PySide6.QtCore import Qt, QTimer, QMargins, QPointF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtCharts import (
    QChart, QChartView, QLineSeries, QBarSeries, QBarSet,
    QBarCategoryAxis, QValueAxis, QPieSeries, QPieSlice,
    QAreaSeries
)
import qtawesome as qta

from datetime import datetime, timedelta

from addons.Automobiles.views.style import Colors, Spacing, Fonts
from addons.Automobiles.views.widgets.modern_card import ModernCard, StatsCard
from core.logger import logger


class DashboardView(QWidget):
    """Dashboard moderne avec KPI et graphiques (style reports_view)"""

    # Mapping des icônes Font Awesome 5
    ICON_MAP = {
        "vehicles": "fa5s.car",
        "contracts": "fa5s.file-contract",
        "clients": "fa5s.users",
        "revenue": "fa5s.coins",
        "chart_line": "fa5s.chart-line",
        "chart_bar": "fa5s.chart-bar",
        "pie_chart": "fa5s.chart-pie",
        "sync": "fa5s.sync-alt",
        "clock": "fa5s.clock",
        "user": "fa5s.user",
        "building": "fa5s.building",
        "exclamation": "fa5s.exclamation-triangle",
        "search": "fa5s.search-plus",
        "tools": "fa5s.tools",
        "upload": "fa5s.upload",
        "cog": "fa5s.cog",
    }
    
    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.kpi_cards = {}
        self._loading = False
        self.current_data = {}
        
        self.setup_ui()
        
        # Charger après l'affichage
        QTimer.singleShot(100, self.load_data)
        
        # Auto-refresh toutes les 5 minutes
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(300000)
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.XL)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(Spacing.XL)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête
        # header = self._create_header()
        # content_layout.addWidget(header)
        
        # Ligne 1: Cartes KPI
        self.setup_kpi_cards()
        content_layout.addLayout(self.kpi_layout)
        
        # Ligne 2: Graphiques principaux (2 colonnes)
        row2 = QHBoxLayout()
        row2.setSpacing(Spacing.XL)
        
        self.contracts_chart = self._create_contracts_chart()
        self.revenue_chart = self._create_revenue_chart()
        
        row2.addWidget(self.contracts_chart, 1)
        row2.addWidget(self.revenue_chart, 1)
        content_layout.addLayout(row2)
        
        # Ligne 3: Graphiques secondaires (3 colonnes)
        row3 = QHBoxLayout()
        row3.setSpacing(Spacing.XL)
        
        self.vehicle_type_chart = self._create_vehicle_type_chart()
        self.contract_status_chart = self._create_contract_status_chart()
        self.client_type_chart = self._create_client_type_chart()
        
        row3.addWidget(self.vehicle_type_chart, 1)
        row3.addWidget(self.contract_status_chart, 1)
        row3.addWidget(self.client_type_chart, 1)
        content_layout.addLayout(row3)
        
        # Ligne 4: Activité récente
        self.setup_recent_activity()
        content_layout.addWidget(self.recent_activity_card)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _create_header(self):
        """Crée l'en-tête avec Font Awesome"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e293b, stop:1 #0f172a);
                border-radius: 16px;
                padding: 20px 28px;
            }
        """)
        header.setMinimumHeight(80)
        
        layout = QHBoxLayout(header)
        
        # ✅ Icône Dashboard avec Font Awesome
        icon_label = QLabel()
        icon = qta.icon('fa5s.chart-pie', color='#ffffff')
        icon_label.setPixmap(icon.pixmap(28, 28))
        icon_label.setStyleSheet("background: transparent; border: none;")
        
        title = QLabel("Tableau de bord")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: 700; background: transparent; border: none; margin-left: 10px;")
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(0)
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title)
        
        self.last_update_label = QLabel("Dernière mise à jour: ...")
        self.last_update_label.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent; border: none;")
        
        # ✅ Bouton Actualiser avec Font Awesome
        refresh_btn = QPushButton()
        refresh_icon = qta.icon('fa5s.sync-alt', color='#ffffff')
        refresh_btn.setIcon(refresh_icon)
        refresh_btn.setText(" Actualiser")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 10px;
                padding: 8px 20px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addWidget(self.last_update_label)
        layout.addWidget(refresh_btn)
        
        return header
    
    def setup_kpi_cards(self):
        """Configure les cartes KPI avec Font Awesome"""
        self.kpi_layout = QGridLayout()
        self.kpi_layout.setSpacing(Spacing.LG)
        
        self.kpi_cards = {}
        
        # ✅ KPI avec icônes Font Awesome
        kpi_data = [
            {"key": "vehicles", "title": "VÉHICULES", "icon": "fa5s.car", "color": Colors.PRIMARY},
            {"key": "contracts", "title": "CONTRATS ACTIFS", "icon": "fa5s.file", "color": Colors.SUCCESS},  # fa5s.file au lieu de file-contract
            {"key": "clients", "title": "CLIENTS", "icon": "fa5s.user-friends", "color": Colors.INFO},  # user-friends au lieu de users
            {"key": "revenue", "title": "CHIFFRE D'AFFAIRES", "icon": "fa5s.money-bill-wave", "color": Colors.WARNING},  # money-bill-wave au lieu de coins
        ]
        
        for i, data in enumerate(kpi_data):
            card = StatsCard(data["title"], 0, data["icon"], data["color"])
            self.kpi_layout.addWidget(card, 0, i)
            self.kpi_cards[data["key"]] = card

    def get_icon(self, name, color="#ffffff", size=20):
        """Récupère une icône avec vérification"""
        try:
            # Essayer avec le nom exact
            icon = qta.icon(name, color=color)
            return icon.pixmap(size, size)
        except:
            # Fallback: utiliser une icône par défaut
            # print(f"⚠️ Icône non trouvée: {name}, utilisation de 'fa5s.circle'")
            icon = qta.icon('fa5s.circle', color=color)
            return icon.pixmap(size, size)
    
    def _create_contracts_chart(self):
        """Crée le graphique d'évolution des contrats avec Font Awesome"""
        card = ModernCard(title="Évolution des contrats", icon="fa5s.chart-line")
        card.setMinimumHeight(300)
        
        self.chart_contracts = QChart()
        self.chart_contracts.setBackgroundVisible(False)
        self.chart_contracts.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart_contracts.setMargins(QMargins(5, 5, 5, 5))
        
        view = QChartView(self.chart_contracts)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet("background: transparent; border: none;")
        
        card.add_widget(view)
        return card
    
    def _create_revenue_chart(self):
        """Crée le graphique des revenus avec Font Awesome"""
        card = ModernCard(title="Revenus mensuels", icon="fa5s.chart-bar")
        card.setMinimumHeight(300)
        
        self.chart_revenue = QChart()
        self.chart_revenue.setBackgroundVisible(False)
        self.chart_revenue.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart_revenue.setMargins(QMargins(5, 5, 5, 5))
        
        view = QChartView(self.chart_revenue)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet("background: transparent; border: none;")
        
        card.add_widget(view)
        return card
    
    def _create_vehicle_type_chart(self):
        """Crée le graphique des types de véhicules avec Font Awesome"""
        card = ModernCard(title="Types de véhicules", icon="fa5s.car")
        card.setMinimumHeight(250)
        
        self.chart_vehicle_types = QChart()
        self.chart_vehicle_types.setBackgroundVisible(False)
        self.chart_vehicle_types.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart_vehicle_types.legend().setAlignment(Qt.AlignBottom)
        self.chart_vehicle_types.setMargins(QMargins(5, 5, 5, 5))
        
        view = QChartView(self.chart_vehicle_types)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet("background: transparent; border: none;")
        
        card.add_widget(view)
        return card
    
    def _create_contract_status_chart(self):
        """Crée le graphique des statuts de contrats avec Font Awesome"""
        card = ModernCard(title="Statuts des contrats", icon="fa5s.file-contract")
        card.setMinimumHeight(250)
        
        self.chart_contract_status = QChart()
        self.chart_contract_status.setBackgroundVisible(False)
        self.chart_contract_status.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart_contract_status.legend().setAlignment(Qt.AlignBottom)
        self.chart_contract_status.setMargins(QMargins(5, 5, 5, 5))
        
        view = QChartView(self.chart_contract_status)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet("background: transparent; border: none;")
        
        card.add_widget(view)
        return card
    
    def _create_client_type_chart(self):
        """Crée le graphique des types de clients avec Font Awesome"""
        card = ModernCard(title="Types de clients", icon="fa5s.users")
        card.setMinimumHeight(250)
        
        self.chart_client_types = QChart()
        self.chart_client_types.setBackgroundVisible(False)
        self.chart_client_types.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart_client_types.legend().setAlignment(Qt.AlignBottom)
        self.chart_client_types.setMargins(QMargins(5, 5, 5, 5))
        
        view = QChartView(self.chart_client_types)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet("background: transparent; border: none;")
        
        card.add_widget(view)
        return card
    
    def setup_recent_activity(self):
        """Configure la section d'activité récente avec Font Awesome"""
        self.recent_activity_card = ModernCard(title="Activité récente", icon="fa5s.clock")
        self.recent_activity_card.setMinimumHeight(250)
        
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Date", "Type", "Description", "Statut"])
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.setShowGrid(False)
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background: transparent;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 10px 8px;
                border: none;
                font-weight: 600;
                font-size: 11px;
                color: #64748b;
                text-transform: uppercase;
            }
        """)
        self.activity_table.horizontalHeader().setStretchLastSection(True)
        self.activity_table.setColumnWidth(0, 150)
        self.activity_table.setColumnWidth(1, 120)
        self.activity_table.setColumnWidth(2, 250)
        self.activity_table.setColumnWidth(3, 100)
        
        self.recent_activity_card.add_widget(self.activity_table)
    
    def load_data(self):
        """Charge les données du dashboard"""
        if self._loading:
            return
        
        self._loading = True
        
        try:
            self._fetch_data()
            self._update_kpis()
            self._update_contracts_chart()
            self._update_revenue_chart()
            self._update_vehicle_type_chart()
            self._update_contract_status_chart()
            self._update_client_type_chart()
            self._update_activity()
            
            
            
        except Exception as e:
            logger.error(f"Erreur chargement dashboard: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._loading = False
    
    def _fetch_data(self):
        """Récupère les données depuis le contrôleur"""
        try:
            if hasattr(self.controller, 'get_vehicle_stats'):
                self.current_data['vehicle_stats'] = self.controller.get_vehicle_stats()
            if hasattr(self.controller, 'get_contract_stats'):
                self.current_data['contract_stats'] = self.controller.get_contract_stats()
            if hasattr(self.controller, 'get_contact_stats'):
                self.current_data['contact_stats'] = self.controller.get_contact_stats()
            
            if hasattr(self.controller, 'vehicles'):
                if hasattr(self.controller.vehicles, 'get_all_vehicles'):
                    self.current_data['vehicles'] = self.controller.vehicles.get_all_vehicles()
                elif hasattr(self.controller.vehicles, 'get_all'):
                    self.current_data['vehicles'] = self.controller.vehicles.get_all()
            
            if hasattr(self.controller, 'contracts'):
                if hasattr(self.controller.contracts, 'get_all_contracts'):
                    self.current_data['contracts'] = self.controller.contracts.get_all_contracts(limit=200)
                elif hasattr(self.controller.contracts, 'get_all'):
                    self.current_data['contracts'] = self.controller.contracts.get_all()
            
            if hasattr(self.controller, 'contacts'):
                if hasattr(self.controller.contacts, 'get_all_contacts'):
                    self.current_data['contacts'] = self.controller.contacts.get_all_contacts()
                elif hasattr(self.controller.contacts, 'get_all'):
                    self.current_data['contacts'] = self.controller.contacts.get_all()
            
            if hasattr(self.controller, 'get_recent_activity'):
                self.current_data['activities'] = self.controller.get_recent_activity(limit=20)
                
        except Exception as e:
            logger.error(f"Erreur fetch_data: {e}")
    
    def _update_kpis(self):
        """Met à jour les KPI"""
        try:
            vehicle_stats = self.current_data.get('vehicle_stats', {})
            contract_stats = self.current_data.get('contract_stats', {})
            contact_stats = self.current_data.get('contact_stats', {})
            
            if "vehicles" in self.kpi_cards:
                self.kpi_cards["vehicles"].animate_value(vehicle_stats.get('total', 0))
            if "contracts" in self.kpi_cards:
                self.kpi_cards["contracts"].animate_value(contract_stats.get('active', 0))
            if "clients" in self.kpi_cards:
                self.kpi_cards["clients"].animate_value(contact_stats.get('total', 0))
            if "revenue" in self.kpi_cards:
                self.kpi_cards["revenue"].animate_value(int(contract_stats.get('total_premium', 0)))
                
        except Exception as e:
            logger.error(f"Erreur update KPI: {e}")
    
    def _update_contracts_chart(self):
        """Met à jour le graphique des contrats"""
        try:
            self.chart_contracts.removeAllSeries()
            
            contracts = self.current_data.get('contracts', [])
            
            monthly_data = {}
            for contract in contracts:
                if hasattr(contract, 'date_debut') and contract.date_debut:
                    month_key = contract.date_debut.strftime("%b %Y")
                    monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
            
            months = sorted(monthly_data.keys())
            values = [monthly_data[m] for m in months]
            
            if not months:
                months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"]
                values = [0, 0, 0, 0, 0, 0]
            
            bar_set = QBarSet("Contrats")
            for value in values:
                bar_set.append(value)
            bar_set.setColor(QColor(Colors.PRIMARY))
            
            bar_series = QBarSeries()
            bar_series.append(bar_set)
            bar_series.setBarWidth(0.6)
            
            self.chart_contracts.addSeries(bar_series)
            
            axis_x = QBarCategoryAxis()
            axis_x.append(months)
            self.chart_contracts.addAxis(axis_x, Qt.AlignBottom)
            bar_series.attachAxis(axis_x)
            
            max_value = max(values) + 5 if values else 10
            axis_y = QValueAxis()
            axis_y.setRange(0, max_value)
            axis_y.setTitleText("Nombre de contrats")
            self.chart_contracts.addAxis(axis_y, Qt.AlignLeft)
            bar_series.attachAxis(axis_y)
            
            self.chart_contracts.setTitle("Évolution des contrats")
            
        except Exception as e:
            logger.error(f"Erreur update contracts chart: {e}")
    
    def _update_revenue_chart(self):
        """Met à jour le graphique des revenus"""
        try:
            self.chart_revenue.removeAllSeries()
            
            contracts = self.current_data.get('contracts', [])
            
            monthly_revenue = {}
            for contract in contracts:
                if hasattr(contract, 'date_debut') and contract.date_debut:
                    month_key = contract.date_debut.strftime("%b %Y")
                    premium = getattr(contract, 'prime_totale_ttc', 0) or getattr(contract, 'total_premium', 0)
                    monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + premium
            
            months = sorted(monthly_revenue.keys())
            values = [monthly_revenue[m] for m in months]
            
            if not months:
                months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"]
                values = [0, 0, 0, 0, 0, 0]
            
            bar_set = QBarSet("Revenus (XAF)")
            for value in values:
                bar_set.append(value)
            bar_set.setColor(QColor(Colors.SUCCESS))
            
            series = QBarSeries()
            series.append(bar_set)
            series.setBarWidth(0.6)
            
            self.chart_revenue.addSeries(series)
            
            axis_x = QBarCategoryAxis()
            axis_x.append(months)
            self.chart_revenue.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)
            
            max_value = max(values) * 1.1 if values else 1000
            axis_y = QValueAxis()
            axis_y.setRange(0, max_value)
            axis_y.setTitleText("Revenus (XAF)")
            self.chart_revenue.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)
            
            self.chart_revenue.setTitle("Revenus mensuels")
            
        except Exception as e:
            logger.error(f"Erreur update revenue chart: {e}")
    
    def _update_vehicle_type_chart(self):
        """Met à jour le graphique des types de véhicules"""
        try:
            self.chart_vehicle_types.removeAllSeries()
            
            vehicles = self.current_data.get('vehicles', [])
            
            categories = {}
            for vehicle in vehicles:
                cat = getattr(vehicle, 'categorie', None) or getattr(vehicle, 'type', 'Inconnu')
                categories[cat] = categories.get(cat, 0) + 1
            
            if not categories:
                categories = {"VP": 12, "VU": 8, "PL": 5, "VL": 3}
            
            series = QPieSeries()
            colors = [Colors.PRIMARY, Colors.SUCCESS, Colors.WARNING, "#8b5cf6", Colors.INFO]
            
            total = sum(categories.values())
            for i, (name, value) in enumerate(categories.items()):
                if value > 0:
                    percentage = (value / total * 100)
                    slice = series.append(f"{name} ({value})", value)
                    slice.setColor(QColor(colors[i % len(colors)]))
                    slice.setLabelVisible(True)
                    slice.setLabel(f"{name}\n{percentage:.1f}%")
            
            self.chart_vehicle_types.addSeries(series)
            self.chart_vehicle_types.setTitle("Types de véhicules")
            
        except Exception as e:
            logger.error(f"Erreur update vehicle type chart: {e}")
    
    def _update_contract_status_chart(self):
        """Met à jour le graphique des statuts de contrats"""
        try:
            self.chart_contract_status.removeAllSeries()
            
            contracts = self.current_data.get('contracts', [])
            
            status_counts = {}
            for contract in contracts:
                status = getattr(contract, 'statut', 'Inconnu')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if not status_counts:
                status_counts = {"Actif": 15, "En attente": 5, "Expiré": 8, "Résilié": 3}
            
            series = QPieSeries()
            colors = {"Actif": "#10b981", "En attente": "#f59e0b", "Expiré": "#ef4444", "Résilié": "#64748b"}
            default_colors = [Colors.SUCCESS, Colors.WARNING, Colors.DANGER, Colors.TEXT_SECONDARY]
            
            total = sum(status_counts.values())
            for i, (status, count) in enumerate(status_counts.items()):
                if count > 0:
                    percentage = (count / total * 100)
                    slice = series.append(f"{status} ({count})", count)
                    color = colors.get(status, default_colors[i % len(default_colors)])
                    slice.setColor(QColor(color))
                    slice.setLabelVisible(True)
                    slice.setLabel(f"{status}\n{percentage:.1f}%")
            
            self.chart_contract_status.addSeries(series)
            self.chart_contract_status.setTitle("Statuts des contrats")
            
        except Exception as e:
            logger.error(f"Erreur update contract status chart: {e}")
    
    def _update_client_type_chart(self):
        """Met à jour le graphique des types de clients"""
        try:
            self.chart_client_types.removeAllSeries()
            
            contacts = self.current_data.get('contacts', [])
            
            type_counts = {}
            for contact in contacts:
                client_type = getattr(contact, 'type_client', None) or getattr(contact, 'type', 'Inconnu')
                if client_type:
                    type_counts[client_type] = type_counts.get(client_type, 0) + 1
            
            if not type_counts:
                type_counts = {"Assuré": 20, "Prospect": 10, "Partenaire": 5}
            
            series = QPieSeries()
            colors = ["#8b5cf6", Colors.PRIMARY, Colors.SUCCESS, Colors.WARNING]
            
            total = sum(type_counts.values())
            for i, (name, value) in enumerate(type_counts.items()):
                if value > 0:
                    percentage = (value / total * 100)
                    slice = series.append(f"{name} ({value})", value)
                    slice.setColor(QColor(colors[i % len(colors)]))
                    slice.setLabelVisible(True)
                    slice.setLabel(f"{name}\n{percentage:.1f}%")
            
            self.chart_client_types.addSeries(series)
            self.chart_client_types.setTitle("Types de clients")
            
        except Exception as e:
            logger.error(f"Erreur update client type chart: {e}")
    
    def _update_activity(self):
        """Met à jour l'activité récente"""
        try:
            activities = self.current_data.get('activities', [])
            
            if not activities:
                activities = [
                    {"date": datetime.now() - timedelta(minutes=5), 
                     "type": "Contrat", 
                     "description": "Nouveau contrat #C-2024-0012", 
                     "status": "Actif"},
                    {"date": datetime.now() - timedelta(minutes=25), 
                     "type": "Véhicule", 
                     "description": "Véhicule Toyota Rav4 ajouté", 
                     "status": "Terminé"},
                    {"date": datetime.now() - timedelta(hours=2), 
                     "type": "Contact", 
                     "description": "Prospect Jean Dupont contacté", 
                     "status": "En attente"},
                ]
            
            self.activity_table.setRowCount(len(activities))
            
            status_colors = {
                "Actif": "#10b981",
                "Terminé": "#3b82f6",
                "En attente": "#f59e0b",
                "Annulé": "#ef4444"
            }
            
            for i, activity in enumerate(activities):
                date = activity.get('date', datetime.now())
                if isinstance(date, datetime):
                    date_str = date.strftime("%d/%m/%Y %H:%M")
                else:
                    date_str = str(date)
                
                self.activity_table.setItem(i, 0, QTableWidgetItem(date_str))
                self.activity_table.setItem(i, 1, QTableWidgetItem(activity.get('type', '—')))
                self.activity_table.setItem(i, 2, QTableWidgetItem(activity.get('description', '—')))
                
                status = activity.get('status', '—')
                status_item = QTableWidgetItem(status)
                color = status_colors.get(status, "#64748b")
                status_item.setForeground(QColor(color))
                self.activity_table.setItem(i, 3, status_item)
                
        except Exception as e:
            logger.error(f"Erreur update activity: {e}")
    
    def refresh(self):
        """Rafraîchit le dashboard"""
        self.load_data()
    
    def closeEvent(self, event):
        """Arrête le timer lors de la fermeture"""
        self.refresh_timer.stop()
        super().closeEvent(event)