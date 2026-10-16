


# # addons/Automobiles/views/dashboard_view.py
# """
# Vue Dashboard avec graphiques - Version avec Font Awesome
# """

# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
#     QScrollArea, QLabel, QFrame, QPushButton,
#     QTableWidget, QTableWidgetItem, QHeaderView,
#     QProgressBar
# )
# from PySide6.QtCore import Qt, QTimer, QMargins, QPointF
# from PySide6.QtGui import QColor, QPainter, QPen
# from PySide6.QtCharts import (
#     QChart, QChartView, QLineSeries, QBarSeries, QBarSet,
#     QBarCategoryAxis, QValueAxis, QPieSeries, QPieSlice,
#     QAreaSeries
# )
# import qtawesome as qta

# from datetime import datetime, timedelta

# from addons.Automobiles.views.style import Colors, Spacing, Fonts
# from addons.Automobiles.views.widgets.modern_card import ModernCard, StatsCard
# from core.logger import logger


# class DashboardView(QWidget):
#     """Dashboard moderne avec KPI et graphiques (style reports_view)"""

#     # Mapping des icônes Font Awesome 5
#     ICON_MAP = {
#         "vehicles": "fa5s.car",
#         "contracts": "fa5s.file-contract",
#         "clients": "fa5s.users",
#         "revenue": "fa5s.coins",
#         "chart_line": "fa5s.chart-line",
#         "chart_bar": "fa5s.chart-bar",
#         "pie_chart": "fa5s.chart-pie",
#         "sync": "fa5s.sync-alt",
#         "clock": "fa5s.clock",
#         "user": "fa5s.user",
#         "building": "fa5s.building",
#         "exclamation": "fa5s.exclamation-triangle",
#         "search": "fa5s.search-plus",
#         "tools": "fa5s.tools",
#         "upload": "fa5s.upload",
#         "cog": "fa5s.cog",
#     }
    
#     def __init__(self, controller, user=None):
#         super().__init__()
#         self.controller = controller
#         self.user = user
#         self.kpi_cards = {}
#         self._loading = False
#         self.current_data = {}
        
#         self.setup_ui()
        
#         # Charger après l'affichage
#         QTimer.singleShot(100, self.load_data)
        
#         # Auto-refresh toutes les 5 minutes
#         self.refresh_timer = QTimer()
#         self.refresh_timer.timeout.connect(self.load_data)
#         self.refresh_timer.start(300000)
    
#     def setup_ui(self):
#         """Configure l'interface"""
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(Spacing.XL)
        
#         # Scroll area
#         scroll = QScrollArea()
#         scroll.setWidgetResizable(True)
#         scroll.setFrameShape(QScrollArea.NoFrame)
#         scroll.setStyleSheet("background: transparent; border: none;")
        
#         content = QWidget()
#         content_layout = QVBoxLayout(content)
#         content_layout.setSpacing(Spacing.XL)
#         content_layout.setContentsMargins(20, 20, 20, 20)
        
#         # En-tête
#         # header = self._create_header()
#         # content_layout.addWidget(header)
        
#         # Ligne 1: Cartes KPI
#         self.setup_kpi_cards()
#         content_layout.addLayout(self.kpi_layout)
        
#         # Ligne 2: Graphiques principaux (2 colonnes)
#         row2 = QHBoxLayout()
#         row2.setSpacing(Spacing.XL)
        
#         self.contracts_chart = self._create_contracts_chart()
#         self.revenue_chart = self._create_revenue_chart()
        
#         row2.addWidget(self.contracts_chart, 1)
#         row2.addWidget(self.revenue_chart, 1)
#         content_layout.addLayout(row2)
        
#         # Ligne 3: Graphiques secondaires (3 colonnes)
#         row3 = QHBoxLayout()
#         row3.setSpacing(Spacing.XL)
        
#         self.vehicle_type_chart = self._create_vehicle_type_chart()
#         self.contract_status_chart = self._create_contract_status_chart()
#         self.client_type_chart = self._create_client_type_chart()
        
#         row3.addWidget(self.vehicle_type_chart, 1)
#         row3.addWidget(self.contract_status_chart, 1)
#         row3.addWidget(self.client_type_chart, 1)
#         content_layout.addLayout(row3)
        
#         # Ligne 4: Activité récente
#         self.setup_recent_activity()
#         content_layout.addWidget(self.recent_activity_card)
        
#         scroll.setWidget(content)
#         layout.addWidget(scroll)
    
#     def _create_header(self):
#         """Crée l'en-tête avec Font Awesome"""
#         header = QFrame()
#         header.setStyleSheet("""
#             QFrame {
#                 background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
#                     stop:0 #1e293b, stop:1 #0f172a);
#                 border-radius: 16px;
#                 padding: 20px 28px;
#             }
#         """)
#         header.setMinimumHeight(80)
        
#         layout = QHBoxLayout(header)
        
#         # ✅ Icône Dashboard avec Font Awesome
#         icon_label = QLabel()
#         icon = qta.icon('fa5s.chart-pie', color='#ffffff')
#         icon_label.setPixmap(icon.pixmap(28, 28))
#         icon_label.setStyleSheet("background: transparent; border: none;")
        
#         title = QLabel("Tableau de bord")
#         title.setStyleSheet("color: white; font-size: 24px; font-weight: 700; background: transparent; border: none; margin-left: 10px;")
        
#         title_layout = QHBoxLayout()
#         title_layout.setSpacing(0)
#         title_layout.addWidget(icon_label)
#         title_layout.addWidget(title)
        
#         self.last_update_label = QLabel("Dernière mise à jour: ...")
#         self.last_update_label.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent; border: none;")
        
#         # ✅ Bouton Actualiser avec Font Awesome
#         refresh_btn = QPushButton()
#         refresh_icon = qta.icon('fa5s.sync-alt', color='#ffffff')
#         refresh_btn.setIcon(refresh_icon)
#         refresh_btn.setText(" Actualiser")
#         refresh_btn.setStyleSheet("""
#             QPushButton {
#                 background: rgba(255,255,255,0.1);
#                 color: white;
#                 border: 1px solid rgba(255,255,255,0.2);
#                 border-radius: 10px;
#                 padding: 8px 20px;
#                 font-weight: 500;
#             }
#             QPushButton:hover {
#                 background: rgba(255,255,255,0.2);
#             }
#         """)
#         refresh_btn.clicked.connect(self.load_data)
        
#         layout.addLayout(title_layout)
#         layout.addStretch()
#         layout.addWidget(self.last_update_label)
#         layout.addWidget(refresh_btn)
        
#         return header
    
#     def setup_kpi_cards(self):
#         """Configure les cartes KPI avec Font Awesome"""
#         self.kpi_layout = QGridLayout()
#         self.kpi_layout.setSpacing(Spacing.LG)
        
#         self.kpi_cards = {}
        
#         # ✅ KPI avec icônes Font Awesome
#         kpi_data = [
#             {"key": "vehicles", "title": "VÉHICULES", "icon": "fa5s.car", "color": Colors.PRIMARY},
#             {"key": "contracts", "title": "CONTRATS ACTIFS", "icon": "fa5s.file", "color": Colors.SUCCESS},  # fa5s.file au lieu de file-contract
#             {"key": "clients", "title": "CLIENTS", "icon": "fa5s.user-friends", "color": Colors.INFO},  # user-friends au lieu de users
#             {"key": "revenue", "title": "CHIFFRE D'AFFAIRES", "icon": "fa5s.money-bill-wave", "color": Colors.WARNING},  # money-bill-wave au lieu de coins
#         ]
        
#         for i, data in enumerate(kpi_data):
#             card = StatsCard(data["title"], 0, data["icon"], data["color"])
#             self.kpi_layout.addWidget(card, 0, i)
#             self.kpi_cards[data["key"]] = card

#     def get_icon(self, name, color="#ffffff", size=20):
#         """Récupère une icône avec vérification"""
#         try:
#             # Essayer avec le nom exact
#             icon = qta.icon(name, color=color)
#             return icon.pixmap(size, size)
#         except:
#             # Fallback: utiliser une icône par défaut
#             # print(f"⚠️ Icône non trouvée: {name}, utilisation de 'fa5s.circle'")
#             icon = qta.icon('fa5s.circle', color=color)
#             return icon.pixmap(size, size)
    
#     def _create_contracts_chart(self):
#         """Crée le graphique d'évolution des contrats avec Font Awesome"""
#         card = ModernCard(title="Évolution des contrats", icon="fa5s.chart-line")
#         card.setMinimumHeight(300)
        
#         self.chart_contracts = QChart()
#         self.chart_contracts.setBackgroundVisible(False)
#         self.chart_contracts.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
#         self.chart_contracts.setMargins(QMargins(5, 5, 5, 5))
        
#         view = QChartView(self.chart_contracts)
#         view.setRenderHint(QPainter.Antialiasing)
#         view.setStyleSheet("background: transparent; border: none;")
        
#         card.add_widget(view)
#         return card
    
#     def _create_revenue_chart(self):
#         """Crée le graphique des revenus avec Font Awesome"""
#         card = ModernCard(title="Revenus mensuels", icon="fa5s.chart-bar")
#         card.setMinimumHeight(300)
        
#         self.chart_revenue = QChart()
#         self.chart_revenue.setBackgroundVisible(False)
#         self.chart_revenue.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
#         self.chart_revenue.setMargins(QMargins(5, 5, 5, 5))
        
#         view = QChartView(self.chart_revenue)
#         view.setRenderHint(QPainter.Antialiasing)
#         view.setStyleSheet("background: transparent; border: none;")
        
#         card.add_widget(view)
#         return card
    
#     def _create_vehicle_type_chart(self):
#         """Crée le graphique des types de véhicules avec Font Awesome"""
#         card = ModernCard(title="Types de véhicules", icon="fa5s.car")
#         card.setMinimumHeight(250)
        
#         self.chart_vehicle_types = QChart()
#         self.chart_vehicle_types.setBackgroundVisible(False)
#         self.chart_vehicle_types.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
#         self.chart_vehicle_types.legend().setAlignment(Qt.AlignBottom)
#         self.chart_vehicle_types.setMargins(QMargins(5, 5, 5, 5))
        
#         view = QChartView(self.chart_vehicle_types)
#         view.setRenderHint(QPainter.Antialiasing)
#         view.setStyleSheet("background: transparent; border: none;")
        
#         card.add_widget(view)
#         return card
    
#     def _create_contract_status_chart(self):
#         """Crée le graphique des statuts de contrats avec Font Awesome"""
#         card = ModernCard(title="Statuts des contrats", icon="fa5s.file-contract")
#         card.setMinimumHeight(250)
        
#         self.chart_contract_status = QChart()
#         self.chart_contract_status.setBackgroundVisible(False)
#         self.chart_contract_status.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
#         self.chart_contract_status.legend().setAlignment(Qt.AlignBottom)
#         self.chart_contract_status.setMargins(QMargins(5, 5, 5, 5))
        
#         view = QChartView(self.chart_contract_status)
#         view.setRenderHint(QPainter.Antialiasing)
#         view.setStyleSheet("background: transparent; border: none;")
        
#         card.add_widget(view)
#         return card
    
#     def _create_client_type_chart(self):
#         """Crée le graphique des types de clients avec Font Awesome"""
#         card = ModernCard(title="Types de clients", icon="fa5s.users")
#         card.setMinimumHeight(250)
        
#         self.chart_client_types = QChart()
#         self.chart_client_types.setBackgroundVisible(False)
#         self.chart_client_types.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
#         self.chart_client_types.legend().setAlignment(Qt.AlignBottom)
#         self.chart_client_types.setMargins(QMargins(5, 5, 5, 5))
        
#         view = QChartView(self.chart_client_types)
#         view.setRenderHint(QPainter.Antialiasing)
#         view.setStyleSheet("background: transparent; border: none;")
        
#         card.add_widget(view)
#         return card
    
#     def setup_recent_activity(self):
#         """Configure la section d'activité récente avec Font Awesome"""
#         self.recent_activity_card = ModernCard(title="Activité récente", icon="fa5s.clock")
#         self.recent_activity_card.setMinimumHeight(250)
        
#         self.activity_table = QTableWidget()
#         self.activity_table.setColumnCount(4)
#         self.activity_table.setHorizontalHeaderLabels(["Date", "Type", "Description", "Statut"])
#         self.activity_table.setAlternatingRowColors(True)
#         self.activity_table.setShowGrid(False)
#         self.activity_table.verticalHeader().setVisible(False)
#         self.activity_table.setStyleSheet("""
#             QTableWidget {
#                 border: none;
#                 background: transparent;
#             }
#             QTableWidget::item {
#                 padding: 10px 8px;
#                 border-bottom: 1px solid #f1f5f9;
#             }
#             QHeaderView::section {
#                 background: #f8fafc;
#                 padding: 10px 8px;
#                 border: none;
#                 font-weight: 600;
#                 font-size: 11px;
#                 color: #64748b;
#                 text-transform: uppercase;
#             }
#         """)
#         self.activity_table.horizontalHeader().setStretchLastSection(True)
#         self.activity_table.setColumnWidth(0, 150)
#         self.activity_table.setColumnWidth(1, 120)
#         self.activity_table.setColumnWidth(2, 250)
#         self.activity_table.setColumnWidth(3, 100)
        
#         self.recent_activity_card.add_widget(self.activity_table)
    
#     def load_data(self):
#         """Charge les données du dashboard"""
#         if self._loading:
#             return
        
#         self._loading = True
        
#         try:
#             self._fetch_data()
#             self._update_kpis()
#             self._update_contracts_chart()
#             self._update_revenue_chart()
#             self._update_vehicle_type_chart()
#             self._update_contract_status_chart()
#             self._update_client_type_chart()
#             self._update_activity()
            
            
            
#         except Exception as e:
#             logger.error(f"Erreur chargement dashboard: {e}")
#             import traceback
#             traceback.print_exc()
#         finally:
#             self._loading = False
    
#     def _fetch_data(self):
#         """Récupère les données depuis le contrôleur"""
#         try:
#             if hasattr(self.controller, 'get_vehicle_stats'):
#                 self.current_data['vehicle_stats'] = self.controller.get_vehicle_stats()
#             if hasattr(self.controller, 'get_contract_stats'):
#                 self.current_data['contract_stats'] = self.controller.get_contract_stats()
#             if hasattr(self.controller, 'get_contact_stats'):
#                 self.current_data['contact_stats'] = self.controller.get_contact_stats()
            
#             if hasattr(self.controller, 'vehicles'):
#                 if hasattr(self.controller.vehicles, 'get_all_vehicles'):
#                     self.current_data['vehicles'] = self.controller.vehicles.get_all_vehicles()
#                 elif hasattr(self.controller.vehicles, 'get_all'):
#                     self.current_data['vehicles'] = self.controller.vehicles.get_all()
            
#             if hasattr(self.controller, 'contracts'):
#                 if hasattr(self.controller.contracts, 'get_all_contracts'):
#                     self.current_data['contracts'] = self.controller.contracts.get_all_contracts(limit=200)
#                 elif hasattr(self.controller.contracts, 'get_all'):
#                     self.current_data['contracts'] = self.controller.contracts.get_all()
            
#             if hasattr(self.controller, 'contacts'):
#                 if hasattr(self.controller.contacts, 'get_all_contacts'):
#                     self.current_data['contacts'] = self.controller.contacts.get_all_contacts()
#                 elif hasattr(self.controller.contacts, 'get_all'):
#                     self.current_data['contacts'] = self.controller.contacts.get_all()
            
#             if hasattr(self.controller, 'get_recent_activity'):
#                 self.current_data['activities'] = self.controller.get_recent_activity(limit=20)
                
#         except Exception as e:
#             logger.error(f"Erreur fetch_data: {e}")
    
#     def _update_kpis(self):
#         """Met à jour les KPI"""
#         try:
#             vehicle_stats = self.current_data.get('vehicle_stats', {})
#             contract_stats = self.current_data.get('contract_stats', {})
#             contact_stats = self.current_data.get('contact_stats', {})
            
#             if "vehicles" in self.kpi_cards:
#                 self.kpi_cards["vehicles"].animate_value(vehicle_stats.get('total', 0))
#             if "contracts" in self.kpi_cards:
#                 self.kpi_cards["contracts"].animate_value(contract_stats.get('active', 0))
#             if "clients" in self.kpi_cards:
#                 self.kpi_cards["clients"].animate_value(contact_stats.get('total', 0))
#             if "revenue" in self.kpi_cards:
#                 self.kpi_cards["revenue"].animate_value(int(contract_stats.get('total_premium', 0)))
                
#         except Exception as e:
#             logger.error(f"Erreur update KPI: {e}")
    
#     def _update_contracts_chart(self):
#         """Met à jour le graphique des contrats"""
#         try:
#             self.chart_contracts.removeAllSeries()
            
#             contracts = self.current_data.get('contracts', [])
            
#             monthly_data = {}
#             for contract in contracts:
#                 if hasattr(contract, 'date_debut') and contract.date_debut:
#                     month_key = contract.date_debut.strftime("%b %Y")
#                     monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
            
#             months = sorted(monthly_data.keys())
#             values = [monthly_data[m] for m in months]
            
#             if not months:
#                 months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"]
#                 values = [0, 0, 0, 0, 0, 0]
            
#             bar_set = QBarSet("Contrats")
#             for value in values:
#                 bar_set.append(value)
#             bar_set.setColor(QColor(Colors.PRIMARY))
            
#             bar_series = QBarSeries()
#             bar_series.append(bar_set)
#             bar_series.setBarWidth(0.6)
            
#             self.chart_contracts.addSeries(bar_series)
            
#             axis_x = QBarCategoryAxis()
#             axis_x.append(months)
#             self.chart_contracts.addAxis(axis_x, Qt.AlignBottom)
#             bar_series.attachAxis(axis_x)
            
#             max_value = max(values) + 5 if values else 10
#             axis_y = QValueAxis()
#             axis_y.setRange(0, max_value)
#             axis_y.setTitleText("Nombre de contrats")
#             self.chart_contracts.addAxis(axis_y, Qt.AlignLeft)
#             bar_series.attachAxis(axis_y)
            
#             self.chart_contracts.setTitle("Évolution des contrats")
            
#         except Exception as e:
#             logger.error(f"Erreur update contracts chart: {e}")
    
#     def _update_revenue_chart(self):
#         """Met à jour le graphique des revenus"""
#         try:
#             self.chart_revenue.removeAllSeries()
            
#             contracts = self.current_data.get('contracts', [])
            
#             monthly_revenue = {}
#             for contract in contracts:
#                 if hasattr(contract, 'date_debut') and contract.date_debut:
#                     month_key = contract.date_debut.strftime("%b %Y")
#                     premium = getattr(contract, 'prime_totale_ttc', 0) or getattr(contract, 'total_premium', 0)
#                     monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + premium
            
#             months = sorted(monthly_revenue.keys())
#             values = [monthly_revenue[m] for m in months]
            
#             if not months:
#                 months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"]
#                 values = [0, 0, 0, 0, 0, 0]
            
#             bar_set = QBarSet("Revenus (XAF)")
#             for value in values:
#                 bar_set.append(value)
#             bar_set.setColor(QColor(Colors.SUCCESS))
            
#             series = QBarSeries()
#             series.append(bar_set)
#             series.setBarWidth(0.6)
            
#             self.chart_revenue.addSeries(series)
            
#             axis_x = QBarCategoryAxis()
#             axis_x.append(months)
#             self.chart_revenue.addAxis(axis_x, Qt.AlignBottom)
#             series.attachAxis(axis_x)
            
#             max_value = max(values) * 1.1 if values else 1000
#             axis_y = QValueAxis()
#             axis_y.setRange(0, max_value)
#             axis_y.setTitleText("Revenus (XAF)")
#             self.chart_revenue.addAxis(axis_y, Qt.AlignLeft)
#             series.attachAxis(axis_y)
            
#             self.chart_revenue.setTitle("Revenus mensuels")
            
#         except Exception as e:
#             logger.error(f"Erreur update revenue chart: {e}")
    
#     def _update_vehicle_type_chart(self):
#         """Met à jour le graphique des types de véhicules"""
#         try:
#             self.chart_vehicle_types.removeAllSeries()
            
#             vehicles = self.current_data.get('vehicles', [])
            
#             categories = {}
#             for vehicle in vehicles:
#                 cat = getattr(vehicle, 'categorie', None) or getattr(vehicle, 'type', 'Inconnu')
#                 categories[cat] = categories.get(cat, 0) + 1
            
#             if not categories:
#                 categories = {"VP": 12, "VU": 8, "PL": 5, "VL": 3}
            
#             series = QPieSeries()
#             colors = [Colors.PRIMARY, Colors.SUCCESS, Colors.WARNING, "#8b5cf6", Colors.INFO]
            
#             total = sum(categories.values())
#             for i, (name, value) in enumerate(categories.items()):
#                 if value > 0:
#                     percentage = (value / total * 100)
#                     slice = series.append(f"{name} ({value})", value)
#                     slice.setColor(QColor(colors[i % len(colors)]))
#                     slice.setLabelVisible(True)
#                     slice.setLabel(f"{name}\n{percentage:.1f}%")
            
#             self.chart_vehicle_types.addSeries(series)
#             self.chart_vehicle_types.setTitle("Types de véhicules")
            
#         except Exception as e:
#             logger.error(f"Erreur update vehicle type chart: {e}")
    
#     def _update_contract_status_chart(self):
#         """Met à jour le graphique des statuts de contrats"""
#         try:
#             self.chart_contract_status.removeAllSeries()
            
#             contracts = self.current_data.get('contracts', [])
            
#             status_counts = {}
#             for contract in contracts:
#                 status = getattr(contract, 'statut', 'Inconnu')
#                 status_counts[status] = status_counts.get(status, 0) + 1
            
#             if not status_counts:
#                 status_counts = {"Actif": 15, "En attente": 5, "Expiré": 8, "Résilié": 3}
            
#             series = QPieSeries()
#             colors = {"Actif": "#10b981", "En attente": "#f59e0b", "Expiré": "#ef4444", "Résilié": "#64748b"}
#             default_colors = [Colors.SUCCESS, Colors.WARNING, Colors.DANGER, Colors.TEXT_SECONDARY]
            
#             total = sum(status_counts.values())
#             for i, (status, count) in enumerate(status_counts.items()):
#                 if count > 0:
#                     percentage = (count / total * 100)
#                     slice = series.append(f"{status} ({count})", count)
#                     color = colors.get(status, default_colors[i % len(default_colors)])
#                     slice.setColor(QColor(color))
#                     slice.setLabelVisible(True)
#                     slice.setLabel(f"{status}\n{percentage:.1f}%")
            
#             self.chart_contract_status.addSeries(series)
#             self.chart_contract_status.setTitle("Statuts des contrats")
            
#         except Exception as e:
#             logger.error(f"Erreur update contract status chart: {e}")
    
#     def _update_client_type_chart(self):
#         """Met à jour le graphique des types de clients"""
#         try:
#             self.chart_client_types.removeAllSeries()
            
#             contacts = self.current_data.get('contacts', [])
            
#             type_counts = {}
#             for contact in contacts:
#                 client_type = getattr(contact, 'type_client', None) or getattr(contact, 'type', 'Inconnu')
#                 if client_type:
#                     type_counts[client_type] = type_counts.get(client_type, 0) + 1
            
#             if not type_counts:
#                 type_counts = {"Assuré": 20, "Prospect": 10, "Partenaire": 5}
            
#             series = QPieSeries()
#             colors = ["#8b5cf6", Colors.PRIMARY, Colors.SUCCESS, Colors.WARNING]
            
#             total = sum(type_counts.values())
#             for i, (name, value) in enumerate(type_counts.items()):
#                 if value > 0:
#                     percentage = (value / total * 100)
#                     slice = series.append(f"{name} ({value})", value)
#                     slice.setColor(QColor(colors[i % len(colors)]))
#                     slice.setLabelVisible(True)
#                     slice.setLabel(f"{name}\n{percentage:.1f}%")
            
#             self.chart_client_types.addSeries(series)
#             self.chart_client_types.setTitle("Types de clients")
            
#         except Exception as e:
#             logger.error(f"Erreur update client type chart: {e}")
    
#     def _update_activity(self):
#         """Met à jour l'activité récente"""
#         try:
#             activities = self.current_data.get('activities', [])
            
#             if not activities:
#                 activities = [
#                     {"date": datetime.now() - timedelta(minutes=5), 
#                      "type": "Contrat", 
#                      "description": "Nouveau contrat #C-2024-0012", 
#                      "status": "Actif"},
#                     {"date": datetime.now() - timedelta(minutes=25), 
#                      "type": "Véhicule", 
#                      "description": "Véhicule Toyota Rav4 ajouté", 
#                      "status": "Terminé"},
#                     {"date": datetime.now() - timedelta(hours=2), 
#                      "type": "Contact", 
#                      "description": "Prospect Jean Dupont contacté", 
#                      "status": "En attente"},
#                 ]
            
#             self.activity_table.setRowCount(len(activities))
            
#             status_colors = {
#                 "Actif": "#10b981",
#                 "Terminé": "#3b82f6",
#                 "En attente": "#f59e0b",
#                 "Annulé": "#ef4444"
#             }
            
#             for i, activity in enumerate(activities):
#                 date = activity.get('date', datetime.now())
#                 if isinstance(date, datetime):
#                     date_str = date.strftime("%d/%m/%Y %H:%M")
#                 else:
#                     date_str = str(date)
                
#                 self.activity_table.setItem(i, 0, QTableWidgetItem(date_str))
#                 self.activity_table.setItem(i, 1, QTableWidgetItem(activity.get('type', '—')))
#                 self.activity_table.setItem(i, 2, QTableWidgetItem(activity.get('description', '—')))
                
#                 status = activity.get('status', '—')
#                 status_item = QTableWidgetItem(status)
#                 color = status_colors.get(status, "#64748b")
#                 status_item.setForeground(QColor(color))
#                 self.activity_table.setItem(i, 3, status_item)
                
#         except Exception as e:
#             logger.error(f"Erreur update activity: {e}")
    
#     def refresh(self):
#         """Rafraîchit le dashboard"""
#         self.load_data()
    
#     def closeEvent(self, event):
#         """Arrête le timer lors de la fermeture"""
#         self.refresh_timer.stop()
#         super().closeEvent(event)



# addons/Automobiles/views/dashboard_view.py
"""
Dashboard LOMETA — Version ENRICHIE
- ~50 indicateurs métier + système
- Construction <500 ms
- Sections différées en 2 vagues (rapide → détail)
- Graphiques custom QPainter
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QApplication, QPushButton
)
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
from PySide6.QtGui import (
    QColor, QPainter, QPen, QFont, QPainterPath,
    QLinearGradient, QPolygonF, QBrush
)
import qtawesome as qta
from datetime import datetime, timedelta

from core.logger import logger


# ═══════════════════════════════════════════════════════════════════
# PALETTE
# ═══════════════════════════════════════════════════════════════════

class Pal:
    BG_APP = "#f1f5f9"
    BG_CARD = "#ffffff"
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#475569"
    TEXT_MUTED = "#94a3b8"
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    SUCCESS = "#10b981"
    SUCCESS_DARK = "#059669"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    INFO = "#06b6d4"
    PURPLE = "#8b5cf6"
    PINK = "#ec4899"
    ORANGE = "#f97316"


# ═══════════════════════════════════════════════════════════════════
# WIDGETS CUSTOM
# ═══════════════════════════════════════════════════════════════════

class SparklineMini(QWidget):
    def __init__(self, data, color="#10b981", parent=None):
        super().__init__(parent)
        self.data = data
        self.color = color
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        if not self.data or len(self.data) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        pad = 2
        min_v, max_v = min(self.data), max(self.data)
        rng = max_v - min_v if max_v != min_v else 1
        step = (w - 2 * pad) / (len(self.data) - 1)

        pts = [QPointF(pad + i * step,
                       h - pad - ((v - min_v) / rng) * (h - 2 * pad))
               for i, v in enumerate(self.data)]

        path = QPainterPath()
        path.moveTo(pts[0])
        for pt in pts[1:]:
            path.lineTo(pt)

        fill = QPainterPath(path)
        fill.lineTo(pts[-1].x(), h)
        fill.lineTo(pts[0].x(), h)
        fill.closeSubpath()

        grad = QLinearGradient(0, 0, 0, h)
        c = QColor(self.color)
        grad.setColorAt(0, QColor(c.red(), c.green(), c.blue(), 60))
        grad.setColorAt(1, QColor(c.red(), c.green(), c.blue(), 0))
        p.setBrush(grad)
        p.setPen(Qt.NoPen)
        p.drawPath(fill)

        p.setPen(QPen(QColor(self.color), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)


class AreaChartMini(QWidget):
    """Graphique en aires custom."""

    def __init__(self, series_data, labels, colors, names, parent=None):
        super().__init__(parent)
        self.series_data = series_data
        self.labels = labels
        self.colors = colors
        self.names = names
        self.setMinimumHeight(260)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        ml, mb, mt, mr = 50, 30, 20, 20
        cw, ch = w - ml - mr, h - mt - mb

        all_vals = [v for s in self.series_data for v in s]
        max_v = max(all_vals) * 1.15 or 1

        # Grille
        p.setPen(QPen(QColor("#e2e8f0"), 1))
        for i in range(5):
            y = mt + int(ch * i / 4)
            p.drawLine(ml, y, w - mr, y)

        # Labels Y
        p.setPen(QColor(Pal.TEXT_MUTED))
        p.setFont(QFont("Segoe UI", 8))
        for i in range(5):
            y = mt + int(ch * i / 4)
            p.drawText(0, y - 8, ml - 8, 16,
                       Qt.AlignRight | Qt.AlignVCenter,
                       str(int(max_v * (1 - i / 4))))

        # Labels X
        n = len(self.labels)
        step_x = cw / max(n - 1, 1)
        for i, lbl in enumerate(self.labels):
            x = ml + int(i * step_x)
            p.drawText(x - 20, h - mb + 6, 40, 20, Qt.AlignCenter, lbl)

        # Séries
        for s_idx, series in enumerate(self.series_data):
            if not series:
                continue
            color = QColor(self.colors[s_idx])
            step = cw / max(len(series) - 1, 1)

            pts = [QPointF(ml + i * step,
                           mt + ch - (v / max_v) * ch)
                   for i, v in enumerate(series)]

            fill = QPainterPath()
            fill.moveTo(pts[0].x(), mt + ch)
            for pt in pts:
                fill.lineTo(pt)
            fill.lineTo(pts[-1].x(), mt + ch)
            fill.closeSubpath()

            grad = QLinearGradient(0, mt, 0, mt + ch)
            grad.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 70))
            grad.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 10))
            p.setBrush(grad)
            p.setPen(Qt.NoPen)
            p.drawPath(fill)

            line = QPainterPath()
            line.moveTo(pts[0])
            for pt in pts[1:]:
                line.lineTo(pt)
            p.setPen(QPen(color, 2))
            p.setBrush(Qt.NoBrush)
            p.drawPath(line)

        # Légende
        p.setFont(QFont("Segoe UI", 8))
        lx = ml
        for i, name in enumerate(self.names):
            c = QColor(self.colors[i])
            p.setBrush(c)
            p.setPen(Qt.NoPen)
            p.drawEllipse(lx, mt - 12, 8, 8)
            p.setPen(QColor(Pal.TEXT_SECONDARY))
            p.drawText(lx + 12, mt - 14, 120, 14,
                       Qt.AlignLeft | Qt.AlignVCenter, name)
            lx += 150


class BarChartMini(QWidget):
    """Graphique à barres custom."""

    def __init__(self, data, labels, colors=None, title="", parent=None):
        super().__init__(parent)
        self.data = data
        self.labels = labels
        self.colors = colors or [Pal.PRIMARY] * len(data)
        self.title = title
        self.setMinimumHeight(180)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        ml, mb, mt, mr = 40, 30, 15, 10
        cw, ch = w - ml - mr, h - mt - mb

        max_v = max(self.data) * 1.2 or 1
        n = len(self.data)
        bar_w = cw / n * 0.6
        gap = cw / n

        # Grille
        p.setPen(QPen(QColor("#f1f5f9"), 1))
        for i in range(5):
            y = mt + int(ch * i / 4)
            p.drawLine(ml, y, w - mr, y)

        # Barres
        for i, (val, lbl) in enumerate(zip(self.data, self.labels)):
            x = ml + i * gap + (gap - bar_w) / 2
            bar_h = (val / max_v) * ch
            y = mt + ch - bar_h

            color = QColor(self.colors[i])
            grad = QLinearGradient(0, y, 0, mt + ch)
            grad.setColorAt(0, color)
            grad.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 120))

            p.setBrush(grad)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(int(x), int(y), int(bar_w), int(bar_h), 4, 4)

            # Label
            p.setPen(QColor(Pal.TEXT_MUTED))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(int(x - 10), h - mb + 4, int(bar_w + 20), 20,
                       Qt.AlignCenter, lbl)


class DonutChartMini(QWidget):
    """Donut custom avec texte central."""

    def __init__(self, data, colors, center_text="", center_sub="", parent=None):
        super().__init__(parent)
        self.data = data
        self.colors = colors
        self.center_text = center_text
        self.center_sub = center_sub
        self.setMinimumHeight(200)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        size = min(w, h) - 40
        cx, cy = w // 2, h // 2

        total = sum(self.data) or 1
        start = 90 * 16

        for value, color in zip(self.data, self.colors):
            span = int(-(value / total) * 360 * 16)
            pen = QPen(QColor(color), size * 0.18)
            pen.setCapStyle(Qt.FlatCap)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            p.drawArc(cx - size // 2, cy - size // 2, size, size, start, span)
            start += span

        # Texte central
        if self.center_text:
            p.setPen(QColor(Pal.TEXT_PRIMARY))
            p.setFont(QFont("Segoe UI", 18, QFont.Bold))
            p.drawText(0, cy - 20, w, 30, Qt.AlignCenter, self.center_text)
            if self.center_sub:
                p.setPen(QColor(Pal.TEXT_MUTED))
                p.setFont(QFont("Segoe UI", 8))
                p.drawText(0, cy + 8, w, 20, Qt.AlignCenter, self.center_sub)


class GaugeWidget(QWidget):
    """Jauge semi-circulaire pour pourcentages."""

    def __init__(self, value, max_value=100, color="#10b981",
                 label="", suffix="%", parent=None):
        super().__init__(parent)
        self.value = value
        self.max_value = max_value
        self.color = color
        self.label = label
        self.suffix = suffix
        self.setMinimumSize(120, 80)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        margin = 15
        size = min(w - 2 * margin, (h - 30) * 2)
        cx = w // 2
        cy = h - 20

        # Arc de fond
        rect = QRectF(cx - size / 2, cy - size / 2, size, size)
        pen = QPen(QColor("#e2e8f0"), 8)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawArc(rect, 0, 180 * 16)

        # Arc de valeur
        pct = min(self.value / self.max_value, 1.0)
        pen.setColor(QColor(self.color))
        p.setPen(pen)
        p.drawArc(rect, 180 * 16, int(-pct * 180 * 16))

        # Valeur centrale
        p.setPen(QColor(Pal.TEXT_PRIMARY))
        p.setFont(QFont("Segoe UI", 14, QFont.Bold))
        p.drawText(0, cy - 15, w, 20, Qt.AlignCenter,
                   f"{self.value}{self.suffix}")

        # Label
        if self.label:
            p.setPen(QColor(Pal.TEXT_MUTED))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(0, cy + 5, w, 15, Qt.AlignCenter, self.label)


class HorizontalBarMini(QWidget):
    """Barre horizontale avec label et valeur."""

    def __init__(self, label, value, max_value=100, color="#2563eb",
                 suffix="%", parent=None):
        super().__init__(parent)
        self.label = label
        self.value = value
        self.max_value = max_value
        self.color = color
        self.suffix = suffix
        self.setFixedHeight(24)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Label
        p.setPen(QColor(Pal.TEXT_PRIMARY))
        p.setFont(QFont("Segoe UI", 9))
        label_w = 110
        p.drawText(0, 0, label_w, h, Qt.AlignVCenter | Qt.AlignLeft, self.label)

        # Valeur à droite
        p.setPen(QColor(self.color))
        p.setFont(QFont("Segoe UI", 9, QFont.Bold))
        val_w = 60
        p.drawText(w - val_w, 0, val_w, h,
                   Qt.AlignVCenter | Qt.AlignRight,
                   f"{self.value}{self.suffix}")

        # Barre
        bar_x = label_w + 8
        bar_w = w - bar_x - val_w - 12
        bar_y = h / 2 - 3
        bar_h = 6

        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#f1f5f9"))
        p.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 3, 3)

        fill_w = int(bar_w * min(self.value / self.max_value, 1.0))
        p.setBrush(QColor(self.color))
        p.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 3, 3)


class ProgressWithTarget(QWidget):
    def __init__(self, label, percent, color="#2563eb", parent=None):
        super().__init__(parent)
        self.label = label
        self.percent = percent
        self.color = color
        self.setFixedHeight(26)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        p.setPen(QColor(Pal.TEXT_PRIMARY))
        p.setFont(QFont("Segoe UI", 9))
        lw = 90
        p.drawText(0, 0, lw, h, Qt.AlignVCenter | Qt.AlignLeft, self.label)

        bx = lw + 8
        bw = w - bx - 8
        by = h / 2 - 3

        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#e2e8f0"))
        p.drawRoundedRect(bx, by, bw, 6, 3, 3)

        p.setBrush(QColor(self.color))
        p.drawRoundedRect(bx, by, int(bw * self.percent / 100), 6, 3, 3)


# ═══════════════════════════════════════════════════════════════════
# CARTES
# ═══════════════════════════════════════════════════════════════════

class KpiCardBig(QFrame):
    """Grande carte KPI avec sparkline."""

    def __init__(self, title, value, subtitle="", trend=None,
                 badge=None, badge_color="#10b981",
                 sparkline_data=None, sparkline_color="#10b981",
                 icon_name=None, icon_color=None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(130)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
            QLabel {
                border: none;
                background: transparent;
                outline: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # En-tête : icône + titre + badge
        header = QHBoxLayout()
        header.setSpacing(6)

        if icon_name:
            ic = QLabel()
            ic.setPixmap(qta.icon(icon_name,
                                   color=icon_color or Pal.PRIMARY).pixmap(14, 14))
            header.addWidget(ic)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"""
            color: {Pal.TEXT_SECONDARY};
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.6px;
            background: transparent;
            border: none;
        """)
        header.addWidget(title_lbl)
        header.addStretch()

        if badge:
            badge_lbl = QLabel(badge)
            badge_lbl.setStyleSheet(f"""
                background: {badge_color};
                color: white;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 9px;
                font-weight: 700;
                border: none;
            """)
            header.addWidget(badge_lbl)

        layout.addLayout(header)

        # Valeur + trend
        value_row = QHBoxLayout()
        value_row.setSpacing(6)

        value_lbl = QLabel(value)
        value_lbl.setStyleSheet(f"""
            color: {Pal.TEXT_PRIMARY};
            font-size: 24px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: transparent;
            border: none;
        """)
        value_row.addWidget(value_lbl)

        if trend:
            trend_color = Pal.SUCCESS if trend.startswith("+") else Pal.DANGER
            arrow = "↑" if trend.startswith("+") else "↓"
            trend_lbl = QLabel(f"{arrow} {trend}")
            trend_lbl.setStyleSheet(f"""
                color: {trend_color};
                font-size: 10px;
                font-weight: 700;
                background: transparent;
                border: none;
            """)
            value_row.addWidget(trend_lbl)

        value_row.addStretch()
        layout.addLayout(value_row)

        # Sous-titre + sparkline
        bottom = QHBoxLayout()
        bottom.setSpacing(6)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet(f"""
                color: {Pal.TEXT_MUTED};
                font-size: 9px;
                background: transparent;
                border: none;
            """)
            sub.setWordWrap(True)
            bottom.addWidget(sub, 1)

        bottom.addStretch()

        if sparkline_data:
            spark = SparklineMini(sparkline_data, sparkline_color)
            spark.setFixedSize(60, 22)
            bottom.addWidget(spark)

        layout.addLayout(bottom)


class MiniStatCard(QFrame):
    """Petite carte compacte pour mini-KPIs."""

    def __init__(self, label, value, unit="", color="#2563eb",
                 icon_name=None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        self.setStyleSheet("""
            QFrame {{
                background: white;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }}
            QLabel {
                border: none;
                background: transparent;
                outline: none;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        if icon_name:
            icon_box = QLabel()
            icon_box.setFixedSize(36, 36)
            icon_box.setAlignment(Qt.AlignCenter)
            icon_box.setPixmap(qta.icon(icon_name, color=color).pixmap(18, 18))
            icon_box.setStyleSheet(f"""
                background: {color}15;
                border-radius: 8px;
                border: none;
            """)
            layout.addWidget(icon_box)

        info = QVBoxLayout()
        info.setSpacing(0)

        val_row = QHBoxLayout()
        val_row.setSpacing(3)

        v = QLabel(str(value))
        v.setStyleSheet(f"""
            color: {color};
            font-size: 18px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)
        val_row.addWidget(v)

        if unit:
            u = QLabel(unit)
            u.setStyleSheet(f"""
                color: {Pal.TEXT_MUTED};
                font-size: 10px;
                background: transparent;
                border: none;
            """)
            val_row.addWidget(u, 0, Qt.AlignBottom)

        val_row.addStretch()
        info.addLayout(val_row)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"""
            color: {Pal.TEXT_SECONDARY};
            font-size: 10px;
            background: transparent;
            border: none;
        """)
        info.addWidget(lbl)

        layout.addLayout(info, 1)


class SystemKpiCard(QFrame):
    """Carte compacte pour les KPIs système."""

    def __init__(self, key, value, subtitle, color, icon_name, parent=None):
        super().__init__(parent)
        self.setFixedHeight(105)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }
            QLabel {
                border: none;
                background: transparent;
                outline: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(3)

        top = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(qta.icon(icon_name, color=color).pixmap(14, 14))
        top.addWidget(ic)
        top.addStretch()
        led = QLabel("●")
        led.setStyleSheet(f"color: {color}; font-size: 9px;")
        top.addWidget(led)
        layout.addLayout(top)

        name = QLabel(key.upper())
        name.setStyleSheet(f"""
            color: {Pal.TEXT_MUTED};
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.5px;
            background: transparent;
        """)
        layout.addWidget(name)

        val = QLabel(value)
        val.setStyleSheet(f"""
            color: {color};
            font-size: 18px;
            font-weight: 800;
            background: transparent;
        """)
        layout.addWidget(val)

        sub = QLabel(subtitle)
        sub.setStyleSheet(f"color: {Pal.TEXT_MUTED}; font-size: 9px; background: transparent;")
        layout.addWidget(sub)


class SectionTitle(QFrame):
    """Titre de section avec icône et sous-titre."""

    def __init__(self, icon_name, title, subtitle="", color="#2563eb", parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)
        self.setStyleSheet("""
            background: transparent;
            QLabel {
                border: none;
                background: transparent;
                outline: none;
            }
            """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(10)

        ic = QLabel()
        ic.setPixmap(qta.icon(icon_name, color=color).pixmap(18, 18))
        layout.addWidget(ic)

        t = QLabel(title)
        t.setStyleSheet(f"""
            color: {Pal.TEXT_PRIMARY};
            font-size: 15px;
            font-weight: 800;
            background: transparent;
        """)
        layout.addWidget(t)

        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet(f"""
                color: {Pal.TEXT_MUTED};
                font-size: 10px;
                background: transparent;
            """)
            layout.addWidget(s, 0, Qt.AlignBottom)

        layout.addStretch()


# ═══════════════════════════════════════════════════════════════════
# DASHBOARD PRINCIPAL
# ═══════════════════════════════════════════════════════════════════

class DashboardView(QWidget):
    """Dashboard enrichi — construit en 3 vagues pour la performance."""

    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self._loading = False
        self.refresh_timer = None

        self.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
                outline: none;
            }
        """)

        self.setup_ui_vague1()
        # ✅ Vagues différées
        QTimer.singleShot(200, self._build_vague2)
        QTimer.singleShot(600, self._build_vague3)

    # ═══════════════════════════════════════════════════════════════
    # VAGUE 1 : ESSENTIEL (rapide)
    # ═══════════════════════════════════════════════════════════════

    def setup_ui_vague1(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {Pal.BG_APP}; border: none; }}")

        content = QWidget()
        content.setStyleSheet(f"background: {Pal.BG_APP};")
        self.main_layout = QVBoxLayout(content)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(14)

        # ─── KPI PRINCIPAUX (6 au lieu de 3) ───
        self.main_layout.addLayout(self._build_kpi_row())

        # ─── MINI-STATS COMPACTES (6) ───
        self.main_layout.addLayout(self._build_mini_stats_row())

        # ─── GRAPHIQUE + DONUT ───
        self.main_layout.addLayout(self._build_charts_row())

        # ─── Conteneurs pour vagues suivantes ───
        self._vague2_container = QVBoxLayout()
        self._vague2_container.setSpacing(14)
        self.main_layout.addLayout(self._vague2_container)

        self._vague3_container = QVBoxLayout()
        self._vague3_container.setSpacing(14)
        self.main_layout.addLayout(self._vague3_container)

        self.main_layout.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

    def _build_kpi_row(self):
        """6 KPI principaux."""
        row = QHBoxLayout()
        row.setSpacing(10)

        kpis = [
            dict(title="Polices actives", value="12,450",
                 subtitle="Rétention 88.5%", trend="+3.2%",
                 badge="STABLE", badge_color=Pal.SUCCESS,
                 sparkline_data=[3, 4, 5, 4, 6, 7, 6, 8, 9, 8, 10],
                 sparkline_color=Pal.SUCCESS,
                 icon_name="fa5s.file-contract", icon_color=Pal.PRIMARY),

            dict(title="Sinistres en cours", value="47",
                 subtitle="14 experts · 3 en attente", trend="-12%",
                 badge="CRITIQUE", badge_color=Pal.DANGER,
                 icon_name="fa5s.exclamation-triangle", icon_color=Pal.DANGER),

            dict(title="Primes encaissées", value="14.85 M",
                 subtitle="€ · 92% recouvrement", trend="+4.1%",
                 badge="EUR", badge_color=Pal.PRIMARY,
                 icon_name="fa5s.euro-sign", icon_color=Pal.SUCCESS),

            dict(title="Taux résolution", value="94.2%",
                 subtitle="Délai moyen 14j", trend="+2.8%",
                 badge="EXCELLENT", badge_color=Pal.SUCCESS,
                 icon_name="fa5s.check-circle", icon_color=Pal.SUCCESS),

            dict(title="Clients actifs", value="3,821",
                 subtitle="Nouveaux 128 ce mois", trend="+5.6%",
                 icon_name="fa5s.users", icon_color=Pal.PURPLE),

            dict(title="Sinistres/1000 pol.", value="3.7",
                 subtitle="Sous la moyenne", trend="-0.8%",
                 icon_name="fa5s.chart-line", icon_color=Pal.WARNING),
        ]

        for kpi in kpis:
            row.addWidget(KpiCardBig(**kpi), 1)

        return row

    def _build_mini_stats_row(self):
        """6 mini-cartes compactes."""
        row = QHBoxLayout()
        row.setSpacing(10)

        stats = [
            ("Véhicules", "2,847", "", Pal.PRIMARY, "fa5s.car"),
            ("Nouveaux dossiers", "128", "/mois", Pal.SUCCESS, "fa5s.file-medical"),
            ("Délai traitement", "14", " jours", Pal.WARNING, "fa5s.clock"),
            ("Compagnies", "23", "", Pal.PURPLE, "fa5s.building"),
            ("Agents actifs", "18", "", Pal.INFO, "fa5s.user-tie"),
            ("Contrats échus", "12", "", Pal.DANGER, "fa5s.file-excel"),
        ]

        for label, value, unit, color, icon in stats:
            card = MiniStatCard(label, value, unit, color, icon)
            row.addWidget(card, 1)

        return row

    def _build_charts_row(self):
        row = QHBoxLayout()
        row.setSpacing(14)

        # ─── Graphique principal ───
        chart_card = QFrame()
        chart_card.setStyleSheet("""
            QFrame { background: white; border-radius: 12px; border: 1px solid #e2e8f0; }
        """)
        cl = QVBoxLayout(chart_card)
        cl.setContentsMargins(16, 12, 16, 12)
        cl.setSpacing(8)

        title = QLabel("📈 Évolution Polices vs Sinistres")
        title.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 12px; font-weight: 700;")
        cl.addWidget(title)

        chart = AreaChartMini(
            series_data=[
                [150, 190, 140, 200, 160, 180],
                [80, 50, 60, 55, 90, 110],
            ],
            labels=["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"],
            colors=[Pal.PRIMARY, Pal.SUCCESS],
            names=["Polices", "Sinistres"],
        )
        cl.addWidget(chart)

        row.addWidget(chart_card, 3)

        # ─── Donut ───
        donut_card = QFrame()
        donut_card.setStyleSheet("""
            QFrame { background: white; border-radius: 12px; border: 1px solid #e2e8f0; }
        """)
        dl = QVBoxLayout(donut_card)
        dl.setContentsMargins(16, 12, 16, 12)
        dl.setSpacing(6)

        dt = QLabel("🎯 Primes par type")
        dt.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 12px; font-weight: 700;")
        dl.addWidget(dt)

        donut = DonutChartMini(
            data=[45, 25, 18, 12],
            colors=[Pal.PRIMARY, Pal.WARNING, Pal.SUCCESS, Pal.PURPLE],
            center_text="100%",
            center_sub="Répartition",
        )
        donut.setFixedHeight(180)
        dl.addWidget(donut)

        # Légende compacte
        for name, pct, color in [
            ("Tous Risques", "45%", Pal.PRIMARY),
            ("Tiers Simple", "25%", Pal.WARNING),
            ("Vol & Incendie", "18%", Pal.SUCCESS),
            ("Jeunes Conducteurs", "12%", Pal.PURPLE),
        ]:
            r = QHBoxLayout()
            r.setSpacing(6)
            dot = QLabel()
            dot.setFixedSize(6, 6)
            dot.setStyleSheet(f"background: {color}; border-radius: 3px;")
            r.addWidget(dot)
            l = QLabel(name)
            l.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 9px;")
            r.addWidget(l, 1)
            v = QLabel(pct)
            v.setStyleSheet(f"color: {color}; font-size: 9px; font-weight: 700;")
            r.addWidget(v)
            dl.addLayout(r)

        row.addWidget(donut_card, 1)

        return row

    # ═══════════════════════════════════════════════════════════════
    # VAGUE 2 : MÉTIER + SRE (différée 200ms)
    # ═══════════════════════════════════════════════════════════════

    def _build_vague2(self):
        try:
            # ─── SRE / SLA ───
            self._vague2_container.addWidget(SectionTitle(
                "fa5s.heartbeat", "Santé & Disponibilité (SRE)",
                "Uptime, MTBF, MTTR, incidents", Pal.SUCCESS
            ))
            self._vague2_container.addLayout(self._row_sre())
            QApplication.processEvents()

            # ─── APM / Golden Signals ───
            self._vague2_container.addWidget(SectionTitle(
                "fa5s.tachometer-alt", "Performance Applicative (APM)",
                "Latence, RPS, erreurs, DB", Pal.INFO
            ))
            self._vague2_container.addLayout(self._row_apm())
            QApplication.processEvents()

            # ─── Sinistres + Activité ───
            self._vague2_container.addLayout(self._row_sinistres_activity())
            QApplication.processEvents()

        except Exception as e:
            logger.error(f"Erreur vague2: {e}")
            import traceback
            traceback.print_exc()

    def _row_sre(self):
        """Ligne SRE avec 4 KPI système."""
        row = QHBoxLayout()
        row.setSpacing(10)
        for k, v, s, c, i in [
            ("Uptime 30j", "99.98%", "3min 12s downtime", Pal.SUCCESS, "fa5s.check-circle"),
            ("MTBF",       "14.2 j", "Between Failures",  Pal.INFO,    "fa5s.clock"),
            ("MTTR",       "23 min", "To Repair",         Pal.WARNING, "fa5s.wrench"),
            ("Incidents",  "2",      "1 crit · 1 warn",   Pal.DANGER,  "fa5s.exclamation-circle"),
        ]:
            row.addWidget(SystemKpiCard(k, v, s, c, i), 1)
        return row

    def _row_apm(self):
        """Ligne APM avec 5 KPI système."""
        row = QHBoxLayout()
        row.setSpacing(10)
        for k, v, s, c, i in [
            ("Latence p95", "320 ms", "avg 128ms · p99 890ms", Pal.INFO,    "fa5s.tachometer-alt"),
            ("Throughput",  "1,450",  "RPS · pic 2,300",        Pal.SUCCESS, "fa5s.bolt"),
            ("Erreurs",     "0.42%",  "4xx 0.31% · 5xx 0.11%",  Pal.WARNING, "fa5s.bug"),
            ("DB Pool",     "45/100", "3 slow queries",          Pal.PURPLE,  "fa5s.database"),
            ("Queues",      "0",      "Backlog 0 · 2s retention",Pal.SUCCESS, "fa5s.stream"),
        ]:
            row.addWidget(SystemKpiCard(k, v, s, c, i), 1)
        return row

    def _row_sinistres_activity(self):
        """Sinistres (table) + Activité récente (liste)."""
        row = QHBoxLayout()
        row.setSpacing(14)

        # ─── Sinistres récents ───
        sin_card = QFrame()
        sin_card.setStyleSheet("""
            QFrame { background: white; border-radius: 12px; border: 1px solid #e2e8f0; }
        """)
        sl = QVBoxLayout(sin_card)
        sl.setContentsMargins(16, 12, 16, 12)
        sl.setSpacing(8)

        t = QLabel("⚠️ Sinistres récents")
        t.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 12px; font-weight: 700;")
        sl.addWidget(t)

        self.sinistres_table = QTableWidget()
        self.sinistres_table.setColumnCount(4)
        self.sinistres_table.setHorizontalHeaderLabels(
            ["Date", "Dossier", "Niveau", "Statut"]
        )
        self.sinistres_table.setShowGrid(False)
        self.sinistres_table.verticalHeader().setVisible(False)
        self.sinistres_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sinistres_table.horizontalHeader().setStretchLastSection(True)
        self.sinistres_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.sinistres_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.sinistres_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.sinistres_table.setStyleSheet(f"""
            QTableWidget {{ background: transparent; border: none; gridline-color: transparent; }}
            QTableWidget::item {{
                padding: 6px 4px;
                border-bottom: 1px solid #f1f5f9;
                color: {Pal.TEXT_PRIMARY};
                font-size: 10px;
            }}
            QHeaderView::section {{
                background: transparent;
                color: {Pal.TEXT_MUTED};
                font-size: 9px;
                font-weight: 700;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                padding: 6px 4px;
            }}
        """)
        self.sinistres_table.setMinimumHeight(180)

        demo = [
            ("15/10 10:26", "Accident grave - #8491", "Critique",      "À traiter"),
            ("15/10 09:45", "Vol véhicule - #8489",   "Avertissement", "En cours"),
            ("14/10 16:15", "Bris de glace - #8482",  "Info",          "Validé"),
            ("14/10 14:30", "Non-conformité IP",      "Sécurité",      "Rejeté"),
            ("13/10 11:20", "Dégât des eaux - #8476", "Info",          "Validé"),
        ]
        self.sinistres_table.setRowCount(len(demo))
        for i, row_data in enumerate(demo):
            for j, val in enumerate(row_data):
                item = QTableWidgetItem(val)
                if j == 2:
                    item.setForeground(QColor({
                        "Critique": Pal.DANGER,
                        "Avertissement": Pal.WARNING,
                        "Info": Pal.INFO,
                        "Sécurité": Pal.PURPLE,
                    }.get(val, Pal.TEXT_SECONDARY)))
                if j == 3:
                    item.setForeground(QColor({
                        "À traiter": Pal.DANGER,
                        "En cours": Pal.WARNING,
                        "Validé": Pal.SUCCESS,
                        "Rejeté": Pal.TEXT_MUTED,
                    }.get(val, Pal.TEXT_SECONDARY)))
                self.sinistres_table.setItem(i, j, item)

        sl.addWidget(self.sinistres_table)
        row.addWidget(sin_card, 3)

        # ─── Activité récente ───
        act_card = QFrame()
        act_card.setStyleSheet("""
            QFrame { background: white; border-radius: 12px; border: 1px solid #e2e8f0; }
        """)
        al = QVBoxLayout(act_card)
        al.setContentsMargins(16, 12, 16, 12)
        al.setSpacing(8)

        at = QLabel("📡 Activité en direct")
        at.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 12px; font-weight: 700;")
        al.addWidget(at)

        activities = [
            ("🟢", "Nouveau contrat signé",    "il y a 2 min",  Pal.SUCCESS),
            ("🔵", "Paiement reçu €1,250",     "il y a 8 min",  Pal.PRIMARY),
            ("🟡", "Sinistre déclaré",         "il y a 15 min", Pal.WARNING),
            ("🟢", "Client ajouté",            "il y a 22 min", Pal.SUCCESS),
            ("🟣", "Expertise terminée",       "il y a 45 min", Pal.PURPLE),
            ("🔵", "Contrat renouvelé",        "il y a 1h",     Pal.PRIMARY),
        ]

        for dot, text, time, color in activities:
            r = QHBoxLayout()
            r.setSpacing(6)
            d = QLabel(dot)
            d.setStyleSheet(f"color: {color}; font-size: 8px;")
            d.setFixedWidth(12)
            r.addWidget(d)

            t = QLabel(text)
            t.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 10px;")
            r.addWidget(t, 1)

            tm = QLabel(time)
            tm.setStyleSheet(f"color: {Pal.TEXT_MUTED}; font-size: 9px;")
            r.addWidget(tm)

            al.addLayout(r)

        al.addStretch()
        row.addWidget(act_card, 2)

        return row

    # ═══════════════════════════════════════════════════════════════
    # VAGUE 3 : SYSTÈME + SECOPS + FINOPS (différée 600ms)
    # ═══════════════════════════════════════════════════════════════

    def _build_vague3(self):
        try:
            # ─── Système ───
            self._vague3_container.addWidget(SectionTitle(
                "fa5s.server", "Performance Système",
                "CPU, RAM, disque, réseau", Pal.PURPLE
            ))
            self._vague3_container.addLayout(self._row_system())
            QApplication.processEvents()

            # ─── SecOps ───
            self._vague3_container.addWidget(SectionTitle(
                "fa5s.shield-alt", "Sécurité & Conformité",
                "Certificats, menaces, conformité", Pal.DANGER
            ))
            self._vague3_container.addLayout(self._row_secops())
            QApplication.processEvents()

            # ─── FinOps ───
            self._vague3_container.addWidget(SectionTitle(
                "fa5s.coins", "FinOps & Coûts Cloud",
                "Coût temps réel, optimisation", Pal.SUCCESS
            ))
            self._vague3_container.addLayout(self._row_finops())

        except Exception as e:
            logger.error(f"Erreur vague3: {e}")
            import traceback
            traceback.print_exc()

    def _row_system(self):
        row = QHBoxLayout()
        row.setSpacing(10)
        for k, v, s, c, i in [
            ("CPU",      "42%",  "Load 0.8 · 8 cores", Pal.INFO,    "fa5s.microchip"),
            ("RAM",      "68%",  "10.9/16 Go",          Pal.SUCCESS, "fa5s.memory"),
            ("Disque",   "54%",  "215/400 Go",          Pal.WARNING, "fa5s.hdd"),
            ("Réseau",   "12.4", "Mo/s ↓ · 3.2 ↑",      Pal.PURPLE,  "fa5s.network-wired"),
            ("SWAP",     "0%",   "Non utilisé",         Pal.SUCCESS, "fa5s.sd-card"),
            ("I/O Wait", "2.1%", "avg 5min",            Pal.SUCCESS, "fa5s.hourglass-half"),
        ]:
            row.addWidget(SystemKpiCard(k, v, s, c, i), 1)
        return row

    def _row_secops(self):
        row = QHBoxLayout()
        row.setSpacing(10)

        # Certificat SSL
        ssl = QFrame()
        ssl.setStyleSheet("""
            QFrame { background: white; border-radius: 10px; border: 1px solid #e2e8f0; }
        """)
        sl = QVBoxLayout(ssl)
        sl.setContentsMargins(16, 12, 16, 12)
        sl.setSpacing(6)

        t = QLabel("🔒 Certificat SSL")
        t.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 11px; font-weight: 700;")
        sl.addWidget(t)

        info = QLabel("lometa.app\nLet's Encrypt R3")
        info.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 10px;")
        sl.addWidget(info)

        b = QLabel("302 jours")
        b.setStyleSheet(f"""
            background: {Pal.SUCCESS}; color: white;
            border-radius: 5px; padding: 3px 10px;
            font-size: 10px; font-weight: 700;
        """)
        sl.addWidget(b, 0, Qt.AlignLeft)
        sl.addStretch()
        row.addWidget(ssl, 1)

        # Détections
        bf = QFrame()
        bf.setStyleSheet("""
            QFrame { background: white; border-radius: 10px; border: 1px solid #e2e8f0; }
        """)
        bl = QVBoxLayout(bf)
        bl.setContentsMargins(16, 12, 16, 12)
        bl.setSpacing(4)

        t = QLabel("🛡️ Détections (24h)")
        t.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 11px; font-weight: 700;")
        bl.addWidget(t)

        for label, count, color in [
            ("Auth échouées", 47, Pal.WARNING),
            ("Brute-force",   12, Pal.DANGER),
            ("Scans ports",    3, Pal.INFO),
            ("Anomalies",      0, Pal.SUCCESS),
        ]:
            r = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 10px;")
            r.addWidget(l, 1)
            c = QLabel(str(count))
            c.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 800;")
            r.addWidget(c)
            bl.addLayout(r)

        bl.addStretch()
        row.addWidget(bf, 1)

        # Modules certifiés
        mod = QFrame()
        mod.setStyleSheet("""
            QFrame { background: white; border-radius: 10px; border: 1px solid #e2e8f0; }
        """)
        ml = QVBoxLayout(mod)
        ml.setContentsMargins(16, 12, 16, 12)
        ml.setSpacing(4)

        t = QLabel("📦 Certificats modules")
        t.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 11px; font-weight: 700;")
        ml.addWidget(t)

        for name, ver, days, color in [
            ("Automobile", "3.0.0", 280, Pal.SUCCESS),
            ("Sinistres",  "3.0.0", 15,  Pal.WARNING),
            ("Paramètres", "2.0.0", 90,  Pal.INFO),
        ]:
            r = QHBoxLayout()
            n = QLabel(f"{name} v{ver}")
            n.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 10px;")
            r.addWidget(n, 1)
            d = QLabel(f"{days}j")
            d.setStyleSheet(f"""
                background: {color}; color: white;
                border-radius: 4px; padding: 2px 6px;
                font-size: 9px; font-weight: 700;
            """)
            r.addWidget(d)
            ml.addLayout(r)

        ml.addStretch()
        row.addWidget(mod, 1)

        # Conformité
        conf = QFrame()
        conf.setStyleSheet("""
            QFrame { background: white; border-radius: 10px; border: 1px solid #e2e8f0; }
        """)
        cl = QVBoxLayout(conf)
        cl.setContentsMargins(16, 12, 16, 12)
        cl.setSpacing(4)

        t = QLabel("✓ Conformité")
        t.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 11px; font-weight: 700;")
        cl.addWidget(t)

        for label, status, color in [
            ("RGPD",     "Valide",     Pal.SUCCESS),
            ("ISO 27001", "Valide",     Pal.SUCCESS),
            ("PCI-DSS",  "Renouv. 30j", Pal.WARNING),
        ]:
            r = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 10px;")
            r.addWidget(l, 1)
            c = QLabel(status)
            c.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: 700;")
            r.addWidget(c)
            cl.addLayout(r)

        cl.addStretch()
        row.addWidget(conf, 1)

        return row

    def _row_finops(self):
        row = QHBoxLayout()
        row.setSpacing(10)

        # Coût du mois
        cost = QFrame()
        cost.setStyleSheet("""
            QFrame { background: white; border-radius: 10px; border: 1px solid #e2e8f0; }
        """)
        cl = QVBoxLayout(cost)
        cl.setContentsMargins(16, 12, 16, 12)
        cl.setSpacing(4)

        t = QLabel("💸 Coût du mois")
        t.setStyleSheet(f"color: {Pal.TEXT_MUTED}; font-size: 10px; font-weight: 700;")
        cl.addWidget(t)

        c = QLabel("€ 1,247.80")
        c.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 22px; font-weight: 800;")
        cl.addWidget(c)

        p = QLabel("Projection : € 1,890")
        p.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 10px;")
        cl.addWidget(p)

        cl.addStretch()
        row.addWidget(cost, 1)

        # Répartition
        br = QFrame()
        br.setStyleSheet("""
            QFrame { background: white; border-radius: 10px; border: 1px solid #e2e8f0; }
        """)
        bl = QVBoxLayout(br)
        bl.setContentsMargins(16, 12, 16, 12)
        bl.setSpacing(4)

        t = QLabel("📊 Par service")
        t.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 11px; font-weight: 700;")
        bl.addWidget(t)

        for service, amount, pct, color in [
            ("Compute",  "€ 620", 50, Pal.PRIMARY),
            ("Database", "€ 380", 30, Pal.SUCCESS),
            ("Storage",  "€ 148", 12, Pal.WARNING),
            ("Network",  "€ 100", 8,  Pal.PURPLE),
        ]:
            r = QHBoxLayout()
            s = QLabel(service)
            s.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 10px;")
            r.addWidget(s, 1)
            a = QLabel(amount)
            a.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 11px; font-weight: 700;")
            r.addWidget(a)
            p = QLabel(f"{pct}%")
            p.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: 700;")
            r.addWidget(p)
            bl.addLayout(r)

        bl.addStretch()
        row.addWidget(br, 1)

        # Optimisations
        opt = QFrame()
        opt.setStyleSheet("""
            QFrame { background: white; border-radius: 10px; border: 1px solid #e2e8f0; }
        """)
        ol = QVBoxLayout(opt)
        ol.setContentsMargins(16, 12, 16, 12)
        ol.setSpacing(4)

        t = QLabel("⚡ Optimisations")
        t.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 11px; font-weight: 700;")
        ol.addWidget(t)

        for label, saving, color in [
            ("3 instances < 15% CPU", "€ 120", Pal.WARNING),
            ("DB non compressée",     "€ 45",  Pal.WARNING),
            ("Logs > 90j",            "€ 28",  Pal.INFO),
            ("Volume orphelin 50Go",  "€ 15",  Pal.WARNING),
        ]:
            r = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 10px;")
            r.addWidget(l, 1)
            s = QLabel(saving)
            s.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: 700;")
            r.addWidget(s)
            ol.addLayout(r)

        ol.addStretch()
        row.addWidget(opt, 1)

        # Usage quotas
        quota = QFrame()
        quota.setStyleSheet("""
            QFrame { background: white; border-radius: 10px; border: 1px solid #e2e8f0; }
        """)
        ql = QVBoxLayout(quota)
        ql.setContentsMargins(16, 12, 16, 12)
        ql.setSpacing(6)

        t = QLabel("📈 Quotas & limites")
        t.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 11px; font-weight: 700;")
        ql.addWidget(t)

        for label, pct, color in [
            ("API calls", 45, Pal.INFO),
            ("Stockage",  62, Pal.WARNING),
            ("Bandwidth", 78, Pal.DANGER),
        ]:
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 10px;")
            ql.addWidget(lbl)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(pct)
            bar.setTextVisible(False)
            bar.setFixedHeight(4)
            bar.setStyleSheet(f"""
                QProgressBar {{ background: #f1f5f9; border: none; border-radius: 2px; }}
                QProgressBar::chunk {{ background: {color}; border-radius: 2px; }}
            """)
            ql.addWidget(bar)

        ql.addStretch()
        row.addWidget(quota, 1)

        return row

    # ═══════════════════════════════════════════════════════════════
    # LIFECYCLE
    # ═══════════════════════════════════════════════════════════════

    def showEvent(self, event):
        super().showEvent(event)
        if self.refresh_timer is None:
            self.refresh_timer = QTimer(self)
            self.refresh_timer.timeout.connect(self.refresh)
            self.refresh_timer.start(300000)

    def refresh(self):
        pass

    def closeEvent(self, event):
        if self.refresh_timer is not None:
            self.refresh_timer.stop()
        super().closeEvent(event)


