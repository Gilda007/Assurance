


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
Dashboard style "AutoAssure / LOMETA"
- Reproduit la maquette fournie
- Ajoute les KPIs système (CPU, RAM, APM, SecOps, FinOps)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QSizePolicy, QGraphicsDropShadowEffect,
    QComboBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QTimer, QMargins, QPointF, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QBrush, QPixmap
from PySide6.QtCharts import (
    QChart, QChartView, QLineSeries, QBarSeries, QBarSet,
    QBarCategoryAxis, QValueAxis, QPieSeries, QPieSlice,
    QAreaSeries, QSplineSeries, QCategoryAxis
)
import qtawesome as qta

from datetime import datetime, timedelta
import random

from core.logger import logger


# ═══════════════════════════════════════════════════════════════════
# PALETTE & STYLES (inspirée de la capture)
# ═══════════════════════════════════════════════════════════════════

class Pal:
    """Palette extraite de la capture"""
    # Fonds
    BG_APP = "#f1f5f9"
    BG_CARD = "#ffffff"
    BG_SIDEBAR = "#0f172a"
    BG_SIDEBAR_HOVER = "#1e293b"
    BG_SIDEBAR_ACTIVE = "#1e40af"

    # Texte
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#475569"
    TEXT_MUTED = "#94a3b8"
    TEXT_LIGHT = "#ffffff"

    # Accents (repris de la capture)
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    SUCCESS = "#10b981"
    SUCCESS_DARK = "#059669"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    INFO = "#3b82f6"
    PURPLE = "#8b5cf6"
    ORANGE = "#f97316"

    # Badges
    BADGE_STABLE = "#10b981"
    BADGE_RESOLVED = "#10b981"
    BADGE_RATING = "#94a3b8"


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def create_shadow(blur=20, color=QColor(0, 0, 0, 15), offset=(0, 4)):
    """Crée une ombre portée douce (style capture)."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setColor(color)
    shadow.setOffset(*offset)
    return shadow


def make_card(bg=Pal.BG_CARD, radius=14, border="#e2e8f0"):
    """Retourne un QFrame en style carte."""
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background: {bg};
            border-radius: {radius}px;
            border: 1px solid {border};
        }}
    """)
    card.setGraphicsEffect(create_shadow())
    return card


# ═══════════════════════════════════════════════════════════════════
# WIDGETS CUSTOM
# ═══════════════════════════════════════════════════════════════════

class KpiCardBig(QFrame):
    """
    Grande carte KPI style capture :
    ┌─────────────────────────────┐
    │ POLICES ACTIVES             │
    │ 12,450 POLICES              │
    │ Rétention 88.5% Rétention 88.5% │
    │ [STABLE]       ~~~~            │
    └─────────────────────────────┘
    """

    def __init__(self, title, value, subtitle="", badges=None, sparkline_data=None,
                 sparkline_color="#10b981", parent=None):
        super().__init__(parent)
        self.setFixedHeight(140)
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 14px;
                border: 1px solid #e2e8f0;
            }}
        """)
        self.setGraphicsEffect(create_shadow())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Titre (uppercase, gris, gras)
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"""
            color: {Pal.TEXT_PRIMARY};
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(title_lbl)

        # Valeur principale (grande, bold)
        value_row = QHBoxLayout()
        value_row.setSpacing(8)

        value_lbl = QLabel(value)
        value_lbl.setStyleSheet(f"""
            color: {Pal.TEXT_PRIMARY};
            font-size: 26px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: transparent;
            border: none;
        """)
        value_row.addWidget(value_lbl)
        value_row.addStretch()

        # Badge optionnel à droite
        if badges:
            badge_text, badge_color = badges[0]
            badge = QLabel(badge_text)
            badge.setStyleSheet(f"""
                background: {badge_color};
                color: white;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 700;
                border: none;
            """)
            value_row.addWidget(badge, 0, Qt.AlignVCenter)

        layout.addLayout(value_row)

        # Sous-titre + sparkline
        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setStyleSheet(f"""
                color: {Pal.TEXT_SECONDARY};
                font-size: 10px;
                background: transparent;
                border: none;
            """)
            sub_lbl.setWordWrap(True)
            bottom.addWidget(sub_lbl, 1)

        bottom.addStretch()

        if sparkline_data:
            spark = SparklineMini(sparkline_data, sparkline_color)
            spark.setFixedSize(70, 28)
            bottom.addWidget(spark)

        layout.addLayout(bottom)

        # Badges supplémentaires (ex: STABLE, Résolues)
        if badges and len(badges) > 1:
            badge_row = QHBoxLayout()
            badge_row.setSpacing(6)
            for text, color in badges[1:]:
                b = QLabel(text)
                b.setStyleSheet(f"""
                    background: {color};
                    color: white;
                    border-radius: 5px;
                    padding: 3px 8px;
                    font-size: 9px;
                    font-weight: 700;
                    border: none;
                """)
                badge_row.addWidget(b)
            badge_row.addStretch()
            layout.addLayout(badge_row)


class SparklineMini(QWidget):
    """Mini sparkline dessinée avec QPainter."""

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
        min_v = min(self.data)
        max_v = max(self.data)
        rng = max_v - min_v if max_v != min_v else 1
        step = (w - 2 * pad) / (len(self.data) - 1)

        pts = []
        for i, v in enumerate(self.data):
            x = pad + i * step
            y = h - pad - ((v - min_v) / rng) * (h - 2 * pad)
            pts.append(QPointF(x, y))

        # Zone remplie
        from PySide6.QtGui import QPainterPath, QLinearGradient
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
        grad.setColorAt(0, QColor(c.red(), c.green(), c.blue(), 70))
        grad.setColorAt(1, QColor(c.red(), c.green(), c.blue(), 0))
        p.setBrush(grad)
        p.setPen(Qt.NoPen)
        p.drawPath(fill)

        # Ligne
        pen = QPen(QColor(self.color), 1.8)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)


class ProgressWithTarget(QWidget):
    """
    Barre de progression avec marqueur de target (comme dans la capture).
    ┌──────────────────────────────────────────┐
    │ Reçus    ████████████░░░░░░  ▼            │
    └──────────────────────────────────────────┘
    """

    def __init__(self, label, percent, target_percent=None, color="#2563eb", parent=None):
        super().__init__(parent)
        self.label = label
        self.percent = percent
        self.target_percent = target_percent
        self.color = color
        self.setFixedHeight(28)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Label à gauche
        p.setPen(QColor(Pal.TEXT_PRIMARY))
        font = QFont("Segoe UI", 10, QFont.Medium)
        p.setFont(font)
        label_w = 100
        p.drawText(0, 0, label_w, h, Qt.AlignVCenter | Qt.AlignLeft, self.label)

        # Barre
        bar_x = label_w + 10
        bar_w = w - bar_x - 10
        bar_y = h / 2 - 3
        bar_h = 6

        # Fond gris
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#e2e8f0"))
        p.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 3, 3)

        # Remplissage
        fill_w = int(bar_w * self.percent / 100)
        p.setBrush(QColor(self.color))
        p.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 3, 3)

        # Marqueur target (triangle)
        if self.target_percent is not None:
            tx = bar_x + int(bar_w * self.target_percent / 100)
            p.setBrush(QColor("#1e293b"))
            from PySide6.QtCore import QPointF
            from PySide6.QtGui import QPolygonF
            tri = QPolygonF([
                QPointF(tx, bar_y - 6),
                QPointF(tx - 4, bar_y - 1),
                QPointF(tx + 4, bar_y - 1),
            ])
            p.drawPolygon(tri)


class SecurityStatCard(QFrame):
    """Carte style 'Sinistre suspect non traité' de la capture."""

    def __init__(self, value, label, color="#ef4444", bg="#fee2e2", parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.setStyleSheet(f"""
            QFrame {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        # Badge valeur
        badge = QLabel(str(value))
        badge.setFixedSize(48, 48)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"""
            background: {bg};
            color: {color};
            border-radius: 10px;
            font-size: 20px;
            font-weight: 800;
            border: none;
        """)
        layout.addWidget(badge)

        # Label
        lbl = QLabel(label)
        lbl.setStyleSheet(f"""
            color: {Pal.TEXT_PRIMARY};
            font-size: 13px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        lbl.setWordWrap(True)
        layout.addWidget(lbl, 1)


# ═══════════════════════════════════════════════════════════════════
# DASHBOARD PRINCIPAL
# ═══════════════════════════════════════════════════════════════════

class DashboardView(QWidget):
    """Dashboard principal style AutoAssure + KPIs système."""

    def __init__(self, controller, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.kpi_cards = {}
        self._loading = False
        self.current_data = {}

        self.setup_ui()

        QTimer.singleShot(100, self.load_data)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(300000)  # 5 min

    # ═══════════════════════════════════════════════════════════════
    # LAYOUT
    # ═══════════════════════════════════════════════════════════════

    def setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ─── Sidebar (comme la capture) ───
        # (Commentée — la sidebar existe déjà au niveau de VehicleMainView)
        # Si tu veux l'inclure ICI, décommente les lignes ci-dessous.
        #
        # self.sidebar = self._build_sidebar()
        # root.addWidget(self.sidebar)

        # ─── Contenu principal ───
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {Pal.BG_APP}; border: none; }}")

        content = QWidget()
        content.setStyleSheet(f"background: {Pal.BG_APP};")
        self.main_layout = QVBoxLayout(content)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(16)

        # ─── Ligne 1 : 5 KPI horizontaux ───
        self.main_layout.addLayout(self._build_kpi_row())

        # ─── Ligne 2 : Graphique + Statut + Donut ───
        self.main_layout.addLayout(self._build_main_charts_row())

        # ─── Ligne 3 : Sécurité + Sinistres récents ───
        self.main_layout.addLayout(self._build_alerts_row())

        # ═══════════════════════════════════════════════════════════
        # 🆕 SECTION : KPIs SYSTÈME (depuis le document Rôles)
        # ═══════════════════════════════════════════════════════════
        self.main_layout.addWidget(self._build_section_title(
            "⚙️ Performance Système & Infrastructure",
            "Monitoring temps réel — CPU, RAM, Disques, Réseau"
        ))
        self.main_layout.addLayout(self._build_system_kpi_row())

        # ═══════════════════════════════════════════════════════════
        # 🆕 SECTION : SRE / SLA
        # ═══════════════════════════════════════════════════════════
        self.main_layout.addWidget(self._build_section_title(
            "📊 Santé & Disponibilité (SRE)",
            "Uptime, MTBF, MTTR, incidents actifs"
        ))
        self.main_layout.addLayout(self._build_sre_row())

        # ═══════════════════════════════════════════════════════════
        # 🆕 SECTION : APM / Golden Signals
        # ═══════════════════════════════════════════════════════════
        self.main_layout.addWidget(self._build_section_title(
            "📡 Performance Applicative (APM)",
            "Latence, RPS, Erreurs, Base de données, Queues"
        ))
        self.main_layout.addLayout(self._build_apm_row())

        # ═══════════════════════════════════════════════════════════
        # 🆕 SECTION : SecOps (Certificats, Brute force)
        # ═══════════════════════════════════════════════════════════
        self.main_layout.addWidget(self._build_section_title(
            "🔐 Sécurité & Conformité (SecOps)",
            "Certificats, brute-force, anomalies réseau"
        ))
        self.main_layout.addLayout(self._build_secops_row())

        # ═══════════════════════════════════════════════════════════
        # 🆕 SECTION : FinOps
        # ═══════════════════════════════════════════════════════════
        self.main_layout.addWidget(self._build_section_title(
            "💰 FinOps & Coûts Cloud",
            "Coût temps réel, répartition, optimisation"
        ))
        self.main_layout.addLayout(self._build_finops_row())

        self.main_layout.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

    # ═══════════════════════════════════════════════════════════════
    # SIDEBAR (optionnelle — comme la capture)
    # ═══════════════════════════════════════════════════════════════

    def _build_sidebar(self):
        """Sidebar sombre verticale, style capture."""
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: {Pal.BG_SIDEBAR};
                border: none;
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ─── Logo ───
        logo_box = QFrame()
        logo_box.setFixedHeight(70)
        logo_box.setStyleSheet(f"background: {Pal.BG_SIDEBAR};")
        logo_l = QHBoxLayout(logo_box)
        logo_l.setContentsMargins(16, 0, 16, 0)
        logo_l.setSpacing(10)

        car = QLabel()
        car.setPixmap(qta.icon('fa5s.shield-alt', color='#3b82f6').pixmap(28, 28))
        logo_l.addWidget(car)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        t1 = QLabel("AutoAssure")
        t1.setStyleSheet("color: white; font-size: 15px; font-weight: 800;")
        t2 = QLabel("PORTAL DE GESTION DE CONTRATS")
        t2.setStyleSheet("color: #64748b; font-size: 7px; letter-spacing: 1px;")
        title_box.addWidget(t1)
        title_box.addWidget(t2)
        logo_l.addLayout(title_box)
        logo_l.addStretch()
        layout.addWidget(logo_box)

        # ─── Menu principal ───
        section_lbl = QLabel("MENU PRINCIPAL")
        section_lbl.setStyleSheet("color: #475569; font-size: 9px; font-weight: 700; "
                                   "letter-spacing: 1px; padding: 16px 20px 8px 20px;")
        layout.addWidget(section_lbl)

        menu_items = [
            ("Tableau de bord", "fa5s.tachometer-alt", True),
            ("Contrats & Polices", "fa5s.file-contract", False),
            ("Sinistres & Réclamations", "fa5s.exclamation-triangle", False),
            ("Clients & Conducteurs", "fa5s.users", False),
            ("Souscriptions & Devis", "fa5s.tags", False),
            ("Facturation & Paiements", "fa5s.credit-card", False),
            ("Performances Ventes", "fa5s.chart-line", False),
            ("Rapports", "fa5s.chart-bar", False),
            ("Paramètres", "fa5s.cog", False),
        ]

        for label, icon_name, active in menu_items:
            item = QFrame()
            item.setFixedHeight(38)
            if active:
                item.setStyleSheet(f"""
                    QFrame {{
                        background: {Pal.BG_SIDEBAR_ACTIVE};
                        border-radius: 0px;
                    }}
                """)
            else:
                item.setStyleSheet("background: transparent;")
            item.setCursor(Qt.PointingHandCursor)

            il = QHBoxLayout(item)
            il.setContentsMargins(20, 0, 20, 0)
            il.setSpacing(12)

            ic = QLabel()
            color = "#ffffff" if active else "#94a3b8"
            ic.setPixmap(qta.icon(icon_name, color=color).pixmap(14, 14))
            il.addWidget(ic)

            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {'white' if active else '#cbd5e1'}; "
                              f"font-size: 12px; font-weight: {'600' if active else '400'};")
            il.addWidget(lbl)
            il.addStretch()

            layout.addWidget(item)

        layout.addStretch()
        return sidebar

    # ═══════════════════════════════════════════════════════════════
    # TITRE DE SECTION
    # ═══════════════════════════════════════════════════════════════

    def _build_section_title(self, title, subtitle=""):
        frame = QFrame()
        frame.setStyleSheet("background: transparent;")
        l = QHBoxLayout(frame)
        l.setContentsMargins(0, 12, 0, 0)
        l.setSpacing(10)

        t = QLabel(title)
        t.setStyleSheet(f"""
            color: {Pal.TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 800;
            background: transparent;
        """)
        l.addWidget(t)

        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet(f"color: {Pal.TEXT_MUTED}; font-size: 11px; background: transparent;")
            l.addWidget(s, 0, Qt.AlignBottom)

        l.addStretch()
        return frame

    # ═══════════════════════════════════════════════════════════════
    # LIGNE 1 : 5 KPI horizontaux (comme la capture)
    # ═══════════════════════════════════════════════════════════════

    def _build_kpi_row(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        # ─── KPI 1 : Polices actives ───
        kpi1 = KpiCardBig(
            title="Polices actives",
            value="12,450",
            subtitle="Rétention 88.5%",
            badges=[("STABLE", Pal.SUCCESS)],
            sparkline_data=[3, 4, 5, 4, 6, 7, 6, 8, 9, 8, 10],
            sparkline_color=Pal.SUCCESS
        )
        row.addWidget(kpi1, 2)

        # ─── KPI 2 : Sinistres & Disponibilité ───
        kpi2 = KpiCardBig(
            title="Sinistres & Disponibilité",
            value="94.20%",
            subtitle="Status code · Délai moyen 14j · Clôtures 420h",
            badges=[("RÉSOLUES", Pal.SUCCESS)]
        )
        row.addWidget(kpi2, 2)

        # ─── KPI 3 : Temps de devis / APM ───
        kpi3 = KpiCardBig(
            title="Temps de devis / APM",
            value="4.2 min",
            subtitle="p95 · Throughput · Taux conversion 12.04%",
            badges=[("1,450", Pal.PRIMARY)]
        )
        row.addWidget(kpi3, 2)

        # ─── KPI 4 : Fraudes & Sécurité ───
        kpi4 = KpiCardBig(
            title="Fraudes & Sécurité",
            value="0",
            subtitle="Alerte fraude",
            badges=[("RPGD Valide", Pal.SUCCESS)]
        )
        row.addWidget(kpi4, 2)

        # ─── KPI 5 : Primes / Finances ───
        kpi5 = KpiCardBig(
            title="Primes / Finances est.",
            value="14,850,000",
            subtitle="▲ 4% vs m-1 · 92% de recouvrement",
            badges=[("EUR", Pal.PRIMARY)]
        )
        row.addWidget(kpi5, 2)

        return row

    # ═══════════════════════════════════════════════════════════════
    # LIGNE 2 : Graphique + Statut + Donut
    # ═══════════════════════════════════════════════════════════════

    def _build_main_charts_row(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        # ─── Colonne 1 : Graphique en aires (Évolution Polices/Sinistres) ───
        chart_card = make_card()
        cl = QVBoxLayout(chart_card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(10)

        # Header : titre + combo
        header = QHBoxLayout()
        title = QLabel("📈 Évolution des Nouvelles Polices & Sinistres (APM)")
        title.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 13px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()

        combo = QComboBox()
        combo.addItems(["Période 12 mois", "Période 6 mois", "Période 3 mois"])
        combo.setStyleSheet(f"""
            QComboBox {{
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 11px;
                color: {Pal.TEXT_PRIMARY};
                min-width: 120px;
            }}
        """)
        header.addWidget(combo)
        cl.addLayout(header)

        # Chart
        self.chart_main = QChart()
        self.chart_main.setBackgroundVisible(False)
        self.chart_main.setAnimationOptions(QChart.SeriesAnimations)
        self.chart_main.setMargins(QMargins(0, 0, 0, 0))
        self.chart_main.legend().setAlignment(Qt.AlignTop)
        self.chart_main.legend().setLabelColor(QColor(Pal.TEXT_PRIMARY))
        self.chart_main.legend().setFont(QFont("Segoe UI", 9))

        chart_view = QChartView(self.chart_main)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setStyleSheet("background: transparent; border: none;")
        chart_view.setMinimumHeight(280)
        cl.addWidget(chart_view)

        row.addWidget(chart_card, 4)

        # ─── Colonne 2 : Statut des dossiers ───
        status_card = make_card()
        sl = QVBoxLayout(status_card)
        sl.setContentsMargins(20, 16, 20, 16)
        sl.setSpacing(12)

        st = QLabel("⚙️ Statut des dossiers (Sinistres)")
        st.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 13px; font-weight: 700;")
        sl.addWidget(st)

        statuses = [
            ("Reçus", 95, 100, Pal.INFO),
            ("Expertise", 78, 100, Pal.SUCCESS),
            ("En traitement", 65, 100, Pal.SUCCESS),
            ("Négociation", 40, 100, Pal.DANGER),
            ("Règlement", 50, 100, Pal.SUCCESS),
        ]
        for label, pct, target, color in statuses:
            sl.addWidget(ProgressWithTarget(label, pct, target, color))

        sl.addStretch()
        row.addWidget(status_card, 3)

        # ─── Colonne 3 : Donut "Primes par type" ───
        donut_card = make_card()
        dl = QVBoxLayout(donut_card)
        dl.setContentsMargins(20, 16, 20, 16)
        dl.setSpacing(10)

        dt = QLabel("🎯 Primes par type de contrat")
        dt.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 13px; font-weight: 700;")
        dl.addWidget(dt)

        self.chart_donut = QChart()
        self.chart_donut.setBackgroundVisible(False)
        self.chart_donut.setAnimationOptions(QChart.SeriesAnimations)
        self.chart_donut.legend().setAlignment(Qt.AlignBottom)
        self.chart_donut.legend().setFont(QFont("Segoe UI", 8))
        self.chart_donut.legend().setLabelColor(QColor(Pal.TEXT_PRIMARY))
        self.chart_donut.setMargins(QMargins(0, 0, 0, 0))

        dv = QChartView(self.chart_donut)
        dv.setRenderHint(QPainter.Antialiasing)
        dv.setStyleSheet("background: transparent; border: none;")
        dv.setMinimumHeight(240)
        dl.addWidget(dv)

        row.addWidget(donut_card, 2)

        return row

    # ═══════════════════════════════════════════════════════════════
    # LIGNE 3 : Sécurité + Sinistres récents
    # ═══════════════════════════════════════════════════════════════

    def _build_alerts_row(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        # ─── Colonne 1 : Sécurité & Accès ───
        sec_card = make_card()
        sec_l = QVBoxLayout(sec_card)
        sec_l.setContentsMargins(20, 16, 20, 16)
        sec_l.setSpacing(14)

        st = QLabel("🔒 Sécurité & Accès (Fraudes)")
        st.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 13px; font-weight: 700;")
        sec_l.addWidget(st)

        sec_l.addWidget(SecurityStatCard("0", "Sinistre suspect non traité",
                                          color="#ef4444", bg="#fee2e2"))
        sec_l.addWidget(SecurityStatCard("12", "Tentatives de fraude bloquées",
                                          color="#8b5cf6", bg="#ede9fe"))
        sec_l.addStretch()

        row.addWidget(sec_card, 2)

        # ─── Colonne 2 : Table des sinistres récents ───
        tbl_card = make_card()
        tl = QVBoxLayout(tbl_card)
        tl.setContentsMargins(20, 16, 20, 16)
        tl.setSpacing(10)

        th = QHBoxLayout()
        tt = QLabel("ℹ️ Sinistres & Activités Récents")
        tt.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 13px; font-weight: 700;")
        th.addWidget(tt)
        th.addStretch()

        filter_combo = QComboBox()
        filter_combo.addItems(["Tech sobre", "Tous", "Critiques"])
        filter_combo.setStyleSheet(f"""
            QComboBox {{
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                min-width: 100px;
            }}
        """)
        th.addWidget(filter_combo)
        tl.addLayout(th)

        self.sinistres_table = QTableWidget()
        self.sinistres_table.setColumnCount(4)
        self.sinistres_table.setHorizontalHeaderLabels(
            ["DATE/HEURE", "NIVEAU", "DOSSIER / INCIDENT", "STATUT"]
        )
        self.sinistres_table.setShowGrid(False)
        self.sinistres_table.verticalHeader().setVisible(False)
        self.sinistres_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sinistres_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sinistres_table.horizontalHeader().setStretchLastSection(True)
        self.sinistres_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.sinistres_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.sinistres_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.sinistres_table.setStyleSheet(f"""
            QTableWidget {{
                background: transparent;
                border: none;
                gridline-color: transparent;
            }}
            QTableWidget::item {{
                padding: 10px 6px;
                border-bottom: 1px solid #f1f5f9;
                color: {Pal.TEXT_PRIMARY};
                font-size: 12px;
            }}
            QHeaderView::section {{
                background: transparent;
                color: {Pal.TEXT_MUTED};
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.5px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                padding: 8px 6px;
            }}
        """)
        self.sinistres_table.setMinimumHeight(220)

        # Données de démo (reproduites depuis la capture)
        demo = [
            ("15/10/2026 10:26", "Critique", "Accident grave - Pol #8491", "A traiter"),
            ("15/10/2026 09:45", "Avertissement", "Vol véhicule - Pol #8489", "En cours"),
            ("14/10/2026 16:15", "Info", "Bris de glace - Pol #8482", "Validé"),
            ("14/10/2026 14:30", "Sécurité", "Non-conformité déclarations IP…", "Rejeté"),
        ]
        self.sinistres_table.setRowCount(len(demo))
        for i, row_data in enumerate(demo):
            for j, val in enumerate(row_data):
                item = QTableWidgetItem(val)
                if j == 1:  # Colonne niveau
                    item.setForeground(QColor(self._level_color(val)))
                if j == 3:  # Colonne statut
                    item.setForeground(QColor(self._status_color(val)))
                self.sinistres_table.setItem(i, j, item)

        tl.addWidget(self.sinistres_table)
        row.addWidget(tbl_card, 4)

        return row

    def _level_color(self, level):
        return {
            "Critique": Pal.DANGER,
            "Avertissement": Pal.WARNING,
            "Info": Pal.INFO,
            "Sécurité": Pal.PURPLE,
        }.get(level, Pal.TEXT_SECONDARY)

    def _status_color(self, status):
        return {
            "A traiter": Pal.DANGER,
            "En cours": Pal.WARNING,
            "Validé": Pal.SUCCESS,
            "Rejeté": Pal.TEXT_SECONDARY,
        }.get(status, Pal.TEXT_SECONDARY)

    # ═══════════════════════════════════════════════════════════════
    # 🆕 SYSTÈME — CPU, RAM, Disques, Réseau
    # ═══════════════════════════════════════════════════════════════

    def _build_system_kpi_row(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        # Cartes KPI système
        self.sys_cards = {}
        sys_items = [
            ("CPU",         "42%",   "Load: 0.8/1.1/0.9", Pal.INFO,    "fa5s.microchip"),
            ("Mémoire RAM", "68%",   "10.9 / 16 Go",      Pal.SUCCESS, "fa5s.memory"),
            ("Disque",      "54%",   "215 / 400 Go",      Pal.WARNING, "fa5s.hdd"),
            ("Réseau",      "12.4",  "Mo/s ↓ · 3.2 Mo/s ↑", Pal.PURPLE, "fa5s.network-wired"),
        ]

        for key, value, subtitle, color, icon in sys_items:
            card = self._build_system_card(key, value, subtitle, color, icon)
            row.addWidget(card)

        return row

    def _build_system_card(self, key, value, subtitle, color, icon_name):
        card = make_card()
        card.setFixedHeight(120)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        # Top : icône + value
        top = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(qta.icon(icon_name, color=color).pixmap(18, 18))
        top.addWidget(ic)
        top.addStretch()

        # Indicateur LED
        led = QLabel("●")
        led.setStyleSheet(f"color: {color}; font-size: 12px;")
        top.addWidget(led)

        layout.addLayout(top)

        # Nom
        name = QLabel(key.upper())
        name.setStyleSheet(f"""
            color: {Pal.TEXT_MUTED};
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(name)

        # Valeur
        val = QLabel(value)
        val.setStyleSheet(f"""
            color: {color};
            font-size: 22px;
            font-weight: 800;
        """)
        layout.addWidget(val)

        # Sous-titre
        sub = QLabel(subtitle)
        sub.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 10px;")
        layout.addWidget(sub)

        # Mini barre de progression
        pct = int(''.join(filter(str.isdigit, value)) or 50)
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(min(100, pct))
        bar.setTextVisible(False)
        bar.setFixedHeight(4)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background: #f1f5f9;
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 2px;
            }}
        """)
        layout.addWidget(bar)

        return card

    # ═══════════════════════════════════════════════════════════════
    # 🆕 SRE — Uptime, MTBF, MTTR
    # ═══════════════════════════════════════════════════════════════

    def _build_sre_row(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        sre_items = [
            ("Uptime 30j",   "99.98%",   "3 min 12s downtime", Pal.SUCCESS, "fa5s.check-circle"),
            ("MTBF",         "14.2 j",   "Mean Time Between Failures", Pal.INFO, "fa5s.clock"),
            ("MTTR",         "23 min",   "Mean Time To Repair", Pal.WARNING, "fa5s.wrench"),
            ("Incidents",    "2",        "1 critique · 1 warning", Pal.DANGER, "fa5s.exclamation-circle"),
        ]

        for label, value, sub, color, icon in sre_items:
            row.addWidget(self._build_system_card(label, value, sub, color, icon))

        return row

    # ═══════════════════════════════════════════════════════════════
    # 🆕 APM — Latence, RPS, Erreurs, DB, Queues
    # ═══════════════════════════════════════════════════════════════

    def _build_apm_row(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        apm_items = [
            ("Latence avg",  "128 ms",  "p95: 320 ms · p99: 890 ms", Pal.INFO,    "fa5s.tachometer-alt"),
            ("Throughput",   "1,450",   "RPS · pic 2,300",           Pal.SUCCESS, "fa5s.bolt"),
            ("Taux d'erreur","0.42%",   "4xx: 0.31% · 5xx: 0.11%",   Pal.WARNING, "fa5s.bug"),
            ("DB Pool",      "45 / 100","3 slow queries",             Pal.PURPLE,  "fa5s.database"),
            ("Queues",       "0",       "Backlog 0 · retention 2s",   Pal.SUCCESS, "fa5s.stream"),
        ]

        for label, value, sub, color, icon in apm_items:
            row.addWidget(self._build_system_card(label, value, sub, color, icon))

        return row

    # ═══════════════════════════════════════════════════════════════
    # 🆕 SecOps — Certificats, brute-force, anomalies
    # ═══════════════════════════════════════════════════════════════

    def _build_secops_row(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        # Certificat SSL principal
        ssl_card = make_card()
        sl = QVBoxLayout(ssl_card)
        sl.setContentsMargins(20, 16, 20, 16)
        sl.setSpacing(8)

        h = QHBoxLayout()
        h.addWidget(QLabel("🔒 Certificat SSL principal"))
        h.addStretch()
        h.itemAt(0).widget().setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 12px; font-weight: 700;")
        sl.addLayout(h)

        info = QLabel("lometa.app — Let's Encrypt R3\nExpire le 12/08/2027")
        info.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 11px;")
        sl.addWidget(info)

        # Badge jours restants
        badge = QLabel("302 jours restants")
        badge.setStyleSheet(f"""
            background: {Pal.SUCCESS};
            color: white;
            border-radius: 6px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 700;
        """)
        sl.addWidget(badge, 0, Qt.AlignLeft)

        sl.addStretch()
        row.addWidget(ssl_card, 2)

        # Brute force + anomalies
        bf_card = make_card()
        bl = QVBoxLayout(bf_card)
        bl.setContentsMargins(20, 16, 20, 16)
        bl.setSpacing(10)

        t = QLabel("🛡️ Détections temps réel (24h)")
        t.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 12px; font-weight: 700;")
        bl.addWidget(t)

        for label, count, color in [
            ("Tentatives d'authentification échouées", 47, Pal.WARNING),
            ("Brute-force bloqués",                    12, Pal.DANGER),
            ("Scans de ports détectés",                 3, Pal.INFO),
            ("Anomalies DDoS",                          0, Pal.SUCCESS),
        ]:
            row_l = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 11px;")
            row_l.addWidget(lbl, 1)
            cnt = QLabel(str(count))
            cnt.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 800;")
            row_l.addWidget(cnt)
            bl.addLayout(row_l)

        bl.addStretch()
        row.addWidget(bf_card, 3)

        # Modules certifiés (RSA/HMAC)
        mod_card = make_card()
        ml = QVBoxLayout(mod_card)
        ml.setContentsMargins(20, 16, 20, 16)
        ml.setSpacing(10)

        mt = QLabel("📦 Certificats modules LOMETA")
        mt.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 12px; font-weight: 700;")
        ml.addWidget(mt)

        for name, version, days, color in [
            ("Automobile", "3.0.0 RSA", 280, Pal.SUCCESS),
            ("Sinistres",  "3.0.0 RSA", 15,  Pal.WARNING),
            ("Paramètres", "2.0.0 HMAC", 90, Pal.INFO),
        ]:
            row_l = QHBoxLayout()
            n = QLabel(f"{name} — {version}")
            n.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 11px; font-weight: 600;")
            row_l.addWidget(n, 1)

            d = QLabel(f"{days}j")
            d.setStyleSheet(f"""
                background: {color};
                color: white;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 700;
            """)
            row_l.addWidget(d)
            ml.addLayout(row_l)

        ml.addStretch()
        row.addWidget(mod_card, 2)

        return row

    # ═══════════════════════════════════════════════════════════════
    # 🆕 FinOps
    # ═══════════════════════════════════════════════════════════════

    def _build_finops_row(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        # Coût temps réel
        cost_card = make_card()
        cl = QVBoxLayout(cost_card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(8)

        t = QLabel("💸 Coût estimé — mois en cours")
        t.setStyleSheet(f"color: {Pal.TEXT_MUTED}; font-size: 11px; font-weight: 700;")
        cl.addWidget(t)

        cost = QLabel("€ 1,247.80")
        cost.setStyleSheet(f"""
            color: {Pal.TEXT_PRIMARY};
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
        """)
        cl.addWidget(cost)

        proj = QLabel("Projection fin de mois : € 1,890")
        proj.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 11px;")
        cl.addWidget(proj)

        cl.addStretch()
        row.addWidget(cost_card, 1)

        # Répartition par service
        breakdown = make_card()
        bl = QVBoxLayout(breakdown)
        bl.setContentsMargins(20, 16, 20, 16)
        bl.setSpacing(8)

        bt = QLabel("📊 Répartition par service")
        bt.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 12px; font-weight: 700;")
        bl.addWidget(bt)

        for service, amount, pct, color in [
            ("Compute",   "€ 620", 50, Pal.PRIMARY),
            ("Database",  "€ 380", 30, Pal.SUCCESS),
            ("Storage",   "€ 148", 12, Pal.WARNING),
            ("Network",   "€ 100",  8, Pal.PURPLE),
        ]:
            row_l = QHBoxLayout()
            s = QLabel(service)
            s.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 11px;")
            row_l.addWidget(s, 1)

            a = QLabel(amount)
            a.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 12px; font-weight: 700;")
            row_l.addWidget(a)

            p = QLabel(f"{pct}%")
            p.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 700;")
            row_l.addWidget(p)
            bl.addLayout(row_l)

        bl.addStretch()
        row.addWidget(breakdown, 2)

        # Optimisations détectées
        opt = make_card()
        ol = QVBoxLayout(opt)
        ol.setContentsMargins(20, 16, 20, 16)
        ol.setSpacing(10)

        ot = QLabel("⚡ Optimisations détectées")
        ot.setStyleSheet(f"color: {Pal.TEXT_PRIMARY}; font-size: 12px; font-weight: 700;")
        ol.addWidget(ot)

        for icon, label, saving, color in [
            ("fa5s.server", "3 instances sous-utilisées (<15% CPU)", "€ 120/mois", Pal.WARNING),
            ("fa5s.database", "Volume DB non compressé", "€ 45/mois",  Pal.WARNING),
            ("fa5s.hdd",      "Logs > 90 jours (archive S3 possible)", "€ 28/mois",  Pal.INFO),
        ]:
            row_l = QHBoxLayout()
            ic = QLabel()
            ic.setPixmap(qta.icon(icon, color=color).pixmap(14, 14))
            row_l.addWidget(ic)

            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {Pal.TEXT_SECONDARY}; font-size: 11px;")
            lbl.setWordWrap(True)
            row_l.addWidget(lbl, 1)

            s = QLabel(saving)
            s.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 700;")
            row_l.addWidget(s)
            ol.addLayout(row_l)

        ol.addStretch()
        row.addWidget(opt, 2)

        return row

    # ═══════════════════════════════════════════════════════════════
    # CHARGEMENT DES DONNÉES
    # ═══════════════════════════════════════════════════════════════

    def load_data(self):
        if self._loading:
            return
        self._loading = True
        try:
            self._fetch_data()
            self._update_main_chart()
            self._update_donut()
        except Exception as e:
            logger.error(f"Erreur dashboard: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._loading = False

    def _fetch_data(self):
        """Récupère les données métier (à connecter au controller)."""
        try:
            if hasattr(self.controller, 'get_contract_stats'):
                self.current_data['contract_stats'] = self.controller.get_contract_stats()
        except Exception as e:
            logger.error(f"fetch_data: {e}")

    def _update_main_chart(self):
        """Graphique en aires : Nouvelles Polices + Sinistres."""
        self.chart_main.removeAllSeries()

        months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"]
        polices   = [150, 190, 140, 200, 160, 180]
        sinistres = [ 80,  50,  60,  55,  90, 110]

        # Zone Polices (aire bleue)
        area_series_1 = QSplineSeries()
        line_series_1 = QSplineSeries()
        for i, v in enumerate(polices):
            area_series_1.append(i, v)
            line_series_1.append(i, v)

        area1 = QAreaSeries(area_series_1, QSplineSeries())
        area1.setName("Nouvelles Polices")
        area1.setColor(QColor(37, 99, 235, 90))
        area1.setBorderColor(QColor(Pal.PRIMARY))
        self.chart_main.addSeries(area1)

        # Zone Sinistres (aire verte)
        area_series_2 = QSplineSeries()
        for i, v in enumerate(sinistres):
            area_series_2.append(i, v)

        area2 = QAreaSeries(area_series_2, QSplineSeries())
        area2.setName("Sinistres déclarés")
        area2.setColor(QColor(16, 185, 129, 90))
        area2.setBorderColor(QColor(Pal.SUCCESS))
        self.chart_main.addSeries(area2)

        # Axes
        axis_x = QCategoryAxis()
        for i, m in enumerate(months):
            axis_x.append(m, i)
        axis_x.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        axis_x.setRange(0, len(months) - 1)
        self.chart_main.addAxis(axis_x, Qt.AlignBottom)
        area1.attachAxis(axis_x)
        area2.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, 220)
        axis_y.setTitleText("Polices")
        self.chart_main.addAxis(axis_y, Qt.AlignLeft)
        area1.attachAxis(axis_y)
        area2.attachAxis(axis_y)

        axis_y2 = QValueAxis()
        axis_y2.setRange(0, 600)
        axis_y2.setTitleText("Sinistres")
        self.chart_main.addAxis(axis_y2, Qt.AlignRight)
        area2.attachAxis(axis_y2)

    def _update_donut(self):
        """Donut 'Primes par type de contrat'."""
        self.chart_donut.removeAllSeries()

        series = QPieSeries()
        series.setHoleSize(0.5)
        series.setPieSize(0.75)

        data = [
            ("Tous Risques", 45, Pal.PRIMARY),
            ("Tiers Simple", 25, Pal.WARNING),
            ("Vol & Incendie", 18, Pal.SUCCESS),
            ("Jeunes Conducteurs", 12, Pal.PURPLE),
        ]

        for name, value, color in data:
            sl = series.append(name, value)
            sl.setColor(QColor(color))
            sl.setLabelVisible(False)

        self.chart_donut.addSeries(series)

    def refresh(self):
        self.load_data()

    def closeEvent(self, event):
        self.refresh_timer.stop()
        super().closeEvent(event)