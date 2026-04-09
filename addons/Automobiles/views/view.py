import random
import subprocess
import re
import platform
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect, QProgressBar,
                             QTableWidgetItem, QScrollArea, QLabel, QPushButton, 
                             QLineEdit, QFrame, QStackedWidget, QGridLayout)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QMargins, QPointF, QThread, Signal
from PySide6.QtGui import QFont, QColor, QLinearGradient, QBrush, QPainter, QPen
from PySide6.QtCharts import (QChart, QChartView, QPieSeries, QBarSeries, 
                             QBarSet, QBarCategoryAxis, QValueAxis, QLineSeries,
                             QSplineSeries, QAreaSeries, QScatterSeries,
                             QCategoryAxis, QDateTimeAxis, QLegend, QPieSlice)
from PySide6.QtCore import QDateTime, QPointF
import math

from addons.Automobiles.views.automobile_view import VehiculeModuleView
from addons.Automobiles.views.contacts_view import ContactListView
from addons.Automobiles.views.compagnies_view import CompanyTariffView


class NetworkSpeedWorker(QThread):
    """Thread pour mesurer la vitesse réseau sans bloquer l'UI"""
    speed_updated = Signal(float, float, float, float)  # download, upload, latency, packet_loss
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        while self.running:
            try:
                download = self.measure_download_speed()
                upload = self.measure_upload_speed()
                latency = self.measure_latency()
                packet_loss = self.measure_packet_loss()
                self.speed_updated.emit(download, upload, latency, packet_loss)
            except Exception as e:
                print(f"Network measurement error: {e}")
                self.speed_updated.emit(0, 0, 999, 100)
            self.msleep(3000)  # Mesure toutes les 3 secondes
            
    def measure_latency(self):
        """Mesure la latence (ping) vers google.com"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            response = subprocess.run(
                ['ping', param, '4', '8.8.8.8'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if response.returncode == 0:
                # Extraction du temps de ping moyen
                if platform.system().lower() == 'windows':
                    matches = re.findall(r'temps[=<](\d+)ms', response.stdout)
                else:
                    matches = re.findall(r'time=(\d+\.?\d*) ms', response.stdout)
                
                if matches:
                    times = [float(t) for t in matches]
                    return sum(times) / len(times)
        except Exception:
            pass
        return 0
        
    def measure_packet_loss(self):
        """Mesure le taux de perte de paquets"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            response = subprocess.run(
                ['ping', param, '10', '8.8.8.8'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if response.returncode == 0:
                if platform.system().lower() == 'windows':
                    match = re.search(r'Perte = (\d+)%', response.stdout)
                else:
                    match = re.search(r'(\d+)% packet loss', response.stdout)
                if match:
                    return float(match.group(1))
        except Exception:
            pass
        return 0
        
    def measure_download_speed(self):
        """Mesure la vitesse de téléchargement réelle"""
        try:
            import urllib.request
            import time
            
            # Télécharge un fichier de test de 5MB
            test_url = 'https://speed.cloudflare.com/__down?bytes=5000000'
            start_time = time.time()
            
            req = urllib.request.urlopen(test_url, timeout=5)
            data = req.read()
            end_time = time.time()
            
            duration = end_time - start_time
            if duration > 0:
                # 5MB en Méga bits par seconde
                speed_mbps = (5 * 8) / duration
                return min(speed_mbps, 1000)  # Limite à 1000 Mbps
        except Exception:
            pass
        return 0
        
    def measure_upload_speed(self):
        """Mesure la vitesse d'envoi réelle"""
        try:
            import urllib.request
            import time
            
            # Données de test
            test_data = b'X' * 1000000  # 1MB de données
            start_time = time.time()
            
            req = urllib.request.Request(
                'https://httpbin.org/post',
                data=test_data,
                method='POST'
            )
            urllib.request.urlopen(req, timeout=5)
            end_time = time.time()
            
            duration = end_time - start_time
            if duration > 0:
                # 1MB en Méga bits par seconde
                speed_mbps = (1 * 8) / duration
                return min(speed_mbps, 500)  # Limite à 500 Mbps
        except Exception:
            pass
        return 0
        
    def stop(self):
        self.running = False

class NetworkSpeedMonitor(QFrame):
    """Widget de monitoring de la qualité de connexion internet avec données réelles"""
    def __init__(self):
        super().__init__()
        self.download_speed = 0
        self.upload_speed = 0
        self.latency = 0
        self.packet_loss = 0
        self.quality = 100
        self.worker = None
        self.animation_value = 0
        self.setup_ui()
        self.setup_network_monitoring()
        self.setup_animation_timer()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        header = QHBoxLayout()
        self.icon_label = QLabel("🌐")
        self.icon_label.setStyleSheet("font-size: 28px;")
        
        title = QLabel("Qualité Connexion")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a;")
        
        self.status_badge = QLabel("● EN LIGNE")
        self.status_badge.setStyleSheet("""
            font-size: 10px;
            font-weight: 600;
            color: #10b981;
            background-color: #d1fae5;
            padding: 4px 10px;
            border-radius: 20px;
        """)
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedSize(32, 32)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                border-radius: 16px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.refresh_btn.clicked.connect(self.force_refresh)
        
        header.addWidget(self.icon_label)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status_badge)
        header.addWidget(self.refresh_btn)
        layout.addLayout(header)
        
        # Jauge de qualité
        self.quality_label = QLabel("Qualité du réseau")
        self.quality_label.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 500;")
        layout.addWidget(self.quality_label)
        
        self.quality_bar = QProgressBar()
        self.quality_bar.setFixedHeight(10)
        self.quality_bar.setStyleSheet("""
            QProgressBar {
                background-color: #e2e8f0;
                border-radius: 5px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ef4444, stop:0.3 #f59e0b, stop:0.7 #eab308, stop:1 #10b981);
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.quality_bar)
        
        # Métriques principales
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(12)
        
        self.download_widget = self._create_metric_card("📥", "Téléchargement", "0 Mbps", "#3B82F6")
        self.upload_widget = self._create_metric_card("📤", "Envoi", "0 Mbps", "#10B981")
        self.latency_widget = self._create_metric_card("⏱", "Latence", "0 ms", "#F59E0B")
        self.packet_widget = self._create_metric_card("📦", "Perte", "0%", "#EF4444")
        
        metrics_layout.addWidget(self.download_widget)
        metrics_layout.addWidget(self.upload_widget)
        metrics_layout.addWidget(self.latency_widget)
        metrics_layout.addWidget(self.packet_widget)
        layout.addLayout(metrics_layout)
        
        # Détails supplémentaires
        details_layout = QHBoxLayout()
        details_layout.setSpacing(15)
        
        # Lignes corrigées
        self.ip_label = self._create_detail_label("📍", "IP", "Détection...")
        self.network_label = self._create_detail_label("📶", "Réseau", "Détection...")
        self.time_label = self._create_detail_label("🕐", "Dernière mesure", "---")
        
        details_layout.addWidget(self.ip_label)
        details_layout.addWidget(self.network_label)
        details_layout.addWidget(self.time_label)
        layout.addLayout(details_layout)
        
        # Graphique d'historique miniature
        self.history_title = QLabel("Historique des performances")
        self.history_title.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 500; margin-top: 8px;")
        layout.addWidget(self.history_title)
        
        self.history_chart = QChartView()
        self.history_chart.setFixedHeight(60)
        self.history_chart.setStyleSheet("background-color: transparent; border: none;")
        self.setup_history_chart()
        layout.addWidget(self.history_chart)
        
        # Label de statut détaillé
        self.status_label = QLabel("🟢 Mesure en cours...")
        self.status_label.setStyleSheet("""
            font-size: 11px;
            color: #64748b;
            font-weight: 500;
            padding: 8px;
            background-color: #f8fafc;
            border-radius: 12px;
        """)
        layout.addWidget(self.status_label)
        
    def _create_metric_card(self, icon, title, value, color):
        """Crée une carte métrique moderne"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #f8fafc;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }}
        """)
        card.setFixedHeight(90)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        
        # Icône et titre
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18px;")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 500;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Valeur
        value_label = QLabel(value)
        value_label.setObjectName(f"{title}_value")
        value_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 800;
            color: {color};
        """)
        layout.addWidget(value_label, alignment=Qt.AlignCenter)
        
        # Stocker la référence
        if title == "Téléchargement":
            self.download_value = value_label
        elif title == "Envoi":
            self.upload_value = value_label
        elif title == "Latence":
            self.latency_value = value_label
        elif title == "Perte":
            self.packet_value = value_label
            
        return card
    
    def _create_detail_label(self, icon, title, value):
        """Crée un label de détail"""
        widget = QFrame()
        widget.setStyleSheet("background-color: transparent;")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 12px;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 10px; color: #94a3b8;")
        
        detail_value = QLabel(value)
        detail_value.setStyleSheet("""
            font-size: 10px; 
            color: #475569; 
            font-weight: 500;
        """)
        detail_value.setWordWrap(True)  # Permettre le retour à la ligne
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(detail_value)
        layout.addStretch()
        
        # Stocker la référence
        if title == "IP":
            self.ip_value = detail_value
        elif title == "Réseau":
            self.network_value = detail_value
        elif title == "Dernière mesure":
            self.time_value = detail_value
            
        return widget
    
    def setup_history_chart(self):
        """Configure le graphique d'historique"""
        self.history_series = QLineSeries()
        self.history_chart_obj = QChart()
        self.history_chart_obj.addSeries(self.history_series)
        self.history_chart_obj.setBackgroundVisible(False)
        self.history_chart_obj.setMargins(QMargins(0, 0, 0, 0))
        
        axis_x = QValueAxis()
        axis_x.setVisible(False)
        axis_x.setRange(0, 20)
        
        axis_y = QValueAxis()
        axis_y.setVisible(False)
        axis_y.setRange(0, 100)
        
        self.history_chart_obj.addAxis(axis_x, Qt.AlignBottom)
        self.history_chart_obj.addAxis(axis_y, Qt.AlignLeft)
        self.history_series.attachAxis(axis_x)
        self.history_series.attachAxis(axis_y)
        
        self.history_chart.setChart(self.history_chart_obj)
        self.history_chart.setRenderHint(QPainter.Antialiasing)
        
        self.history_data = []
        
    def setup_animation_timer(self):
        """Configure le timer d'animation"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_ui)
        self.animation_timer.start(1000)  # Animation plus lente
        
    def animate_ui(self):
        """Anime les éléments UI"""
        self.animation_value += 0.1
        
        # Animation simple de l'icône (changement de taille via font-size)
        font_size = 24 + int(abs(math.sin(self.animation_value)) * 4)
        self.icon_label.setStyleSheet(f"font-size: {font_size}px;")
        
    def setup_network_monitoring(self):
        """Démarre le monitoring réseau dans un thread séparé"""
        self.get_local_ip()
        self.worker = NetworkSpeedWorker()
        self.worker.speed_updated.connect(self.update_network_stats)
        self.worker.start()
            
    def get_public_ip(self):
        """Récupère l'adresse IP publique"""
        try:
            import urllib.request
            
            # Utiliser ipify.org (service fiable et gratuit)
            req = urllib.request.urlopen('https://api.ipify.org', timeout=5)
            public_ip = req.read().decode('utf-8').strip()
            
            if public_ip and '.' in public_ip:
                return public_ip
        except Exception:
            pass
        
        # Fallback vers un autre service
        try:
            req = urllib.request.urlopen('https://checkip.amazonaws.com', timeout=5)
            public_ip = req.read().decode('utf-8').strip()
            if public_ip and '.' in public_ip:
                return public_ip
        except Exception:
            pass
        
        return None
      
    def get_local_ip(self):
        """Récupère l'IP locale"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            if hasattr(self, 'ip_value'):
                self.ip_value.setText(ip)
        except Exception:
            if hasattr(self, 'ip_value'):
                self.ip_value.setText("Non détectée")
                
    def get_network_type(self):
        """Détecte le type de réseau"""
        try:
            # Version simplifiée sans psutil
            import subprocess
            result = subprocess.run(['iwgetid'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                return "Wi-Fi"
            return "Ethernet"
        except Exception:
            return "Connecté"
        
    def force_refresh(self):
        """Force une mise à jour immédiate"""
        self.status_label.setText("🟡 Mesure en cours...")
        self.status_label.setStyleSheet("""
            font-size: 11px;
            color: #f59e0b;
            font-weight: 500;
            padding: 8px;
            background-color: #fef3c7;
            border-radius: 12px;
        """)
        
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        
        self.worker = NetworkSpeedWorker()
        self.worker.speed_updated.connect(self.update_network_stats)
        self.worker.start()
        
    def update_network_stats(self, download, upload, latency, packet_loss):
        """Met à jour l'affichage avec les données réelles"""
        self.download_speed = download
        self.upload_speed = upload
        self.latency = latency
        self.packet_loss = packet_loss
        
        # Calcul de la qualité basé sur plusieurs facteurs
        latency_score = max(0, min(40, (150 - latency) / 150 * 40)) if latency > 0 else 20
        packet_score = max(0, min(30, (100 - packet_loss) / 100 * 30))
        speed_score = max(0, min(30, (download / 100) * 30))
        self.quality = min(100, latency_score + packet_score + speed_score)
        
        # Mise à jour des affichages
        if hasattr(self, 'download_value'):
            self.download_value.setText(f"{download:.1f} Mbps")
        if hasattr(self, 'upload_value'):
            self.upload_value.setText(f"{upload:.1f} Mbps")
        if hasattr(self, 'latency_value'):
            self.latency_value.setText(f"{latency:.0f} ms")
        if hasattr(self, 'packet_value'):
            self.packet_value.setText(f"{packet_loss:.0f}%")
        
        self.quality_bar.setValue(int(self.quality))
        
        # Mise à jour du réseau
        if hasattr(self, 'network_value'):
            self.network_value.setText(self.get_network_type())
        
        # Mise à jour de l'heure
        from datetime import datetime
        if hasattr(self, 'time_value'):
            self.time_value.setText(datetime.now().strftime("%H:%M:%S"))
        
        # Mise à jour de l'historique
        self.history_data.append(self.quality)
        if len(self.history_data) > 20:
            self.history_data.pop(0)
        
        self.update_history_chart()
        
        # Mise à jour du statut et du style
        self.update_status_style()
        
    def update_history_chart(self):
        """Met à jour le graphique d'historique"""
        self.history_series.clear()
        for i, value in enumerate(self.history_data):
            self.history_series.append(i, value)
        
        # Style de la ligne
        pen = QPen()
        pen.setColor(QColor(59, 130, 246))
        pen.setWidth(2)
        self.history_series.setPen(pen)
        
        # Remplir la zone sous la courbe
        if hasattr(self, 'area_series'):
            self.history_chart_obj.removeSeries(self.area_series)
        
        from PySide6.QtCharts import QAreaSeries
        self.area_series = QAreaSeries(self.history_series)
        self.area_series.setBrush(QBrush(QColor(59, 130, 246, 50)))
        self.history_chart_obj.addSeries(self.area_series)
        
        # Attacher l'axe
        axes = self.history_chart_obj.axes(Qt.Horizontal)
        if axes:
            self.area_series.attachAxis(axes[0])
        axes_y = self.history_chart_obj.axes(Qt.Vertical)
        if axes_y:
            self.area_series.attachAxis(axes_y[0])
        
    def update_status_style(self):
        """Met à jour le style selon la qualité"""
        if self.quality < 40:
            # Connexion mauvaise
            self.status_label.setText("🔴 Connexion instable - Vérifiez votre réseau")
            self.status_label.setStyleSheet("""
                font-size: 11px;
                color: #ef4444;
                font-weight: 500;
                padding: 8px;
                background-color: #fee2e2;
                border-radius: 12px;
            """)
            self.status_badge.setText("⚠️ CONNEXION FAIBLE")
            self.status_badge.setStyleSheet("""
                font-size: 10px;
                font-weight: 600;
                color: #ef4444;
                background-color: #fee2e2;
                padding: 4px 10px;
                border-radius: 20px;
            """)
            self.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 20px;
                }
            """)
            
        elif self.quality < 70:
            # Connexion moyenne
            self.status_label.setText("🟡 Connexion moyenne - Peut affecter les performances")
            self.status_label.setStyleSheet("""
                font-size: 11px;
                color: #f59e0b;
                font-weight: 500;
                padding: 8px;
                background-color: #fef3c7;
                border-radius: 12px;
            """)
            self.status_badge.setText("🟡 CONNEXION MOYENNE")
            self.status_badge.setStyleSheet("""
                font-size: 10px;
                font-weight: 600;
                color: #f59e0b;
                background-color: #fef3c7;
                padding: 4px 10px;
                border-radius: 20px;
            """)
            self.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 20px;
                }
            """)
            
        else:
            # Excellente connexion
            self.status_label.setText("🟢 Excellente connexion - Tout fonctionne parfaitement")
            self.status_label.setStyleSheet("""
                font-size: 11px;
                color: #10b981;
                font-weight: 500;
                padding: 8px;
                background-color: #d1fae5;
                border-radius: 12px;
            """)
            self.status_badge.setText("🟢 CONNEXION EXCELLENTE")
            self.status_badge.setStyleSheet("""
                font-size: 10px;
                font-weight: 600;
                color: #10b981;
                background-color: #d1fae5;
                padding: 4px 10px;
                border-radius: 20px;
            """)
            self.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 20px;
                }
            """)
            
    def closeEvent(self, event):
        """Arrête le thread à la fermeture"""
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
        super().closeEvent(event)

class AnimatedPieChart(QChartView):
    """Camembert 3D animé avec effets visuels avancés"""
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setup_chart()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_slices)
        self.animation_step = 0
        self.animation_timer.start(100)  # Démarrer l'animation immédiatement
        
    def setup_chart(self):
        self.chart = QChart()
        self.series = QPieSeries()
        
        # Couleurs modernes avec dégradés
        self.colors = [
            QColor(59, 130, 246),   # Bleu primaire
            QColor(16, 185, 129),   # Vert émeraude
            QColor(245, 158, 11),   # Orange
            QColor(239, 68, 68),    # Rouge
            QColor(139, 92, 246),   # Violet
            QColor(236, 72, 153),   # Rose
            QColor(6, 182, 212),    # Cyan
            QColor(168, 85, 247),   # Pourpre
            QColor(34, 197, 94),    # Vert clair
            QColor(249, 115, 22)    # Orange foncé
        ]
        
        # Couleurs de bordure
        self.border_colors = [
            QColor(37, 99, 235),    # Bleu foncé
            QColor(4, 120, 87),     # Vert foncé
            QColor(194, 65, 12),    # Orange foncé
            QColor(185, 28, 28),    # Rouge foncé
            QColor(109, 40, 217),   # Violet foncé
            QColor(190, 24, 93),    # Rose foncé
            QColor(8, 145, 178),    # Cyan foncé
            QColor(126, 34, 206),   # Pourpre foncé
            QColor(21, 128, 61),    # Vert foncé
            QColor(194, 65, 12)     # Orange foncé
        ]
        
        # Ajout des données avec styles améliorés
        total = sum(self.data.values())
        self.slice_objects = []  # Stocker les slices pour animation
        
        for i, (name, value) in enumerate(self.data.items()):
            percentage = (value / total) * 100 if total > 0 else 0
            slice_ = self.series.append(name, value)
            
            # Style de la slice
            slice_.setLabelVisible(True)
            slice_.setLabelColor(QColor(30, 41, 59))
            slice_.setLabelFont(QFont("Segoe UI", 10, QFont.Bold))
            slice_.setLabelPosition(QPieSlice.LabelOutside)
            slice_.setLabelArmLengthFactor(0.3)
            
            # Format du label: Nom (valeur - pourcentage)
            slice_.setLabel(f"{name}\n{value} ({percentage:.1f}%)")
            
            # Couleurs
            color = self.colors[i % len(self.colors)]
            border_color = self.border_colors[i % len(self.border_colors)]
            slice_.setBrush(QBrush(color))
            slice_.setBorderColor(border_color)
            slice_.setBorderWidth(2)
            
            # Effet hover
            slice_.setHovered(False)
            slice_.setPen(QPen(border_color, 2))
            
            self.slice_objects.append(slice_)
        
        self.chart.addSeries(self.series)
        
        # Configuration du titre
        self.chart.setTitle("Répartition des Clients")
        self.chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))
        self.chart.setTitleBrush(QBrush(QColor(15, 23, 42)))
        
        # Animations
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setAnimationDuration(1000)
        self.chart.setBackgroundVisible(False)
        self.chart.setTheme(QChart.ChartThemeLight)
        
        # Configuration de la légende
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self.chart.legend().setFont(QFont("Segoe UI", 9))
        self.chart.legend().setLabelColor(QColor(51, 65, 85))
        self.chart.legend().setBackgroundVisible(False)
        
        # Effet d'ombre 3D sur le graphique
        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(400)
        
        # Ombre portée pour l'effet 3D
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            QChartView {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        # Connecter les signaux hover
        for slice_ in self.slice_objects:
            slice_.hovered.connect(lambda hovered, s=slice_: self.on_slice_hovered(hovered, s))
    
    def on_slice_hovered(self, hovered, slice_):
        """Effet au survol de la souris"""
        if hovered:
            # Agrandir légèrement la slice au survol
            slice_.setExploded(True)
            slice_.setExplodeDistanceFactor(0.15)
            # Changer l'opacité de la bordure
            slice_.setBorderColor(QColor(255, 255, 255))
            slice_.setBorderWidth(3)
            # Mettre en évidence le label
            slice_.setLabelFont(QFont("Segoe UI", 11, QFont.Bold))
            slice_.setLabelColor(QColor(59, 130, 246))
        else:
            # Revenir à l'état normal
            if not self.animation_timer.isActive() or slice_.isExploded() == False:
                slice_.setExploded(False)
            slice_.setBorderColor(self.border_colors[self.slice_objects.index(slice_) % len(self.border_colors)])
            slice_.setBorderWidth(2)
            slice_.setLabelFont(QFont("Segoe UI", 10, QFont.Bold))
            slice_.setLabelColor(QColor(30, 41, 59))
    
    def animate_slices(self):
        """Animation 3D des slices avec effet de rotation"""
        self.animation_step += 0.03
        
        for i, slice_ in enumerate(self.slice_objects):
            # Animation d'explosion en vague
            wave_offset = math.sin(self.animation_step + i * 0.8)
            explosion_factor = max(0, wave_offset * 0.12)
            
            # Explosion sélective en fonction de la position dans la vague
            if wave_offset > 0.3:
                slice_.setExploded(True)
                slice_.setExplodeDistanceFactor(0.08 + explosion_factor)
            else:
                slice_.setExploded(False)
            
            # Animation de pulsation des couleurs
            brightness = 0.85 + abs(math.sin(self.animation_step * 1.5 + i)) * 0.15
            color = self.colors[i % len(self.colors)]
            animated_color = QColor(
                min(255, int(color.red() * brightness)),
                min(255, int(color.green() * brightness)),
                min(255, int(color.blue() * brightness))
            )
            slice_.setBrush(QBrush(animated_color))
            
            # Animation de la bordure
            border_width = 2 + abs(math.sin(self.animation_step * 2 + i)) * 1
            slice_.setBorderWidth(border_width)
            
            # Animation du label (légère rotation)
            if hasattr(slice_, 'setLabelArmLengthFactor'):
                arm_factor = 0.3 + abs(math.sin(self.animation_step + i)) * 0.05
                slice_.setLabelArmLengthFactor(arm_factor)


class AnimatedPieChart3D(QChartView):
    """Version améliorée avec effet 3D plus prononcé et donut optionnel"""
    def __init__(self, data, donut_mode=False):
        super().__init__()
        self.data = data
        self.donut_mode = donut_mode
        self.setup_chart()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_3d_rotation)
        self.animation_step = 0
        self.animation_timer.start(100)
        
    def setup_chart(self):
        self.chart = QChart()
        self.series = QPieSeries()
        
        # Palette de couleurs premium
        self.colors = [
            "#3B82F6", "#10B981", "#F59E0B", "#EF4444", 
            "#8B5CF6", "#EC4899", "#06B6D4", "#F97316",
            "#6366F1", "#14B8A6", "#F43F5E", "#8B5CF6"
        ]
        
        total = sum(self.data.values())
        
        for i, (name, value) in enumerate(self.data.items()):
            percentage = (value / total) * 100 if total > 0 else 0
            slice_ = self.series.append(name, value)
            
            # Configuration avancée des labels
            slice_.setLabelVisible(True)
            slice_.setLabelColor(QColor(15, 23, 42))
            slice_.setLabelFont(QFont("Inter", 9, QFont.Bold))
            slice_.setLabelPosition(QPieSlice.LabelOutside)
            slice_.setLabelArmLengthFactor(0.35)
            slice_.setLabelFont(QFont("Inter", 9, QFont.Bold))
            slice_.setLabelFont(f"{name}\n{percentage:.1f}%")
            
            # Style de la slice
            color = QColor(self.colors[i % len(self.colors)])
            slice_.setBrush(QBrush(color))
            slice_.setBorderColor(QColor(255, 255, 255))
            slice_.setBorderWidth(3)
            
            self.series.append(slice_)
        
        self.chart.addSeries(self.series)
        
        # Configuration du donut (trou central pour effet 3D)
        if self.donut_mode:
            self.series.setHoleSize(0.35)
        
        # Titre stylisé
        self.chart.setTitle("📊 Répartition des Clients")
        self.chart.setTitleFont(QFont("Inter", 16, QFont.Bold))
        self.chart.setTitleBrush(QBrush(QColor(15, 23, 42)))
        
        # Animations
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setAnimationDuration(1200)
        self.chart.setBackgroundVisible(False)
        self.chart.setTheme(QChart.ChartThemeLight)
        
        # Légende moderne
        legend = self.chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignRight)
        legend.setFont(QFont("Inter", 9))
        legend.setLabelColor(QColor(71, 85, 105))
        legend.setBackgroundVisible(False)
        legend.setMarkerShape(QLegend.MarkerShapeCircle)
        
        # Effet de profondeur 3D
        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(420)
        
        # Ombre multicouche pour effet 3D
        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(30)
        shadow1.setColor(QColor(0, 0, 0, 40))
        shadow1.setOffset(0, 6)
        
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(15)
        shadow2.setColor(QColor(0, 0, 0, 20))
        shadow2.setOffset(0, 2)
        
        self.setGraphicsEffect(shadow1)
        
        self.setStyleSheet("""
            QChartView {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border-radius: 24px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        # Ajout d'un effet de survol pour chaque slice
        for slice_ in self.series.slices():
            slice_.hovered.connect(lambda hovered, s=slice_: self.on_hover_3d(hovered, s))
    
    def on_hover_3d(self, hovered, slice_):
        """Effet 3D au survol"""
        if hovered:
            # Animation de l'explosion
            slice_.setExploded(True)
            slice_.setExplodeDistanceFactor(0.12)
            # Grossissement du label
            slice_.setLabelFont(QFont("Inter", 10, QFont.Bold))
            slice_.setLabelColor(QColor(59, 130, 246))
            # Surbrillance
            color = slice_.brush().color()
            lighter_color = QColor(color)
            lighter_color.setAlpha(200)
            slice_.setBrush(QBrush(lighter_color))
        else:
            slice_.setExploded(False)
            slice_.setLabelFont(QFont("Inter", 9, QFont.Bold))
            slice_.setLabelColor(QColor(15, 23, 42))
            # Restaurer la couleur d'origine
            original_color = QColor(self.colors[self.series.slices().index(slice_) % len(self.colors)])
            slice_.setBrush(QBrush(original_color))
    
    def animate_3d_rotation(self):
        """Animation de rotation 3D"""
        self.animation_step += 0.02
        
        # Rotation des slices
        for i, slice_ in enumerate(self.series.slices()):
            # Effet de rotation 3D (changement de l'angle d'explosion)
            rotation_angle = math.sin(self.animation_step * 0.5 + i) * 0.1
            current_explode = slice_.isExploded()
            
            if not current_explode:
                # Animation subtile de l'angle
                if hasattr(slice_, 'setStartAngle'):
                    start_angle = (self.animation_step * 50) % 360
                    slice_.setStartAngle(start_angle)
            
            # Pulsation des couleurs
            pulse = abs(math.sin(self.animation_step * 1.2 + i)) * 0.12
            color = QColor(self.colors[i % len(self.colors)])
            animated_color = QColor(
                min(255, color.red() + int(pulse * 30)),
                min(255, color.green() + int(pulse * 30)),
                min(255, color.blue() + int(pulse * 30))
            )
            slice_.setBrush(QBrush(animated_color))


class AnimatedBarChart3D(QChartView):
    """Graphique en barres 3D avec effets visuels avancés"""
    def __init__(self):
        super().__init__()
        self.setup_chart()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_bars)
        self.animation_value = 0
        self.animation_timer.start(50)
        
    def setup_chart(self):
        self.chart = QChart()
        self.chart.setTitle("Évolution du Parc Automobile")
        self.chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setAnimationDuration(800)
        self.chart.setBackgroundVisible(False)
        self.chart.setTheme(QChart.ChartThemeLight)
        
        # Dégradé de fond pour le chart
        self.chart.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
        
        # Création de plusieurs séries pour un effet 3D
        self.series_main = QBarSeries()
        self.series_main.setBarWidth(0.6)
        
        # Couleurs dégradées pour chaque barre
        self.gradient_colors = [
            QColor(59, 130, 246),   # Bleu
            QColor(16, 185, 129),   # Vert
            QColor(245, 158, 11),   # Orange
            QColor(239, 68, 68),    # Rouge
            QColor(139, 92, 246),   # Violet
            QColor(236, 72, 153),   # Rose
            QColor(6, 182, 212)     # Cyan
        ]
        
        # Données avec valeurs réelles et cibles
        self.months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil"]
        self.current_data = [5, 12, 8, 15, 20, 14, 18]
        self.target_data = [8, 15, 12, 20, 25, 20, 25]
        self.animation_data = self.current_data.copy()
        
        # BarSet principal
        self.bar_set = QBarSet("Véhicules")
        self.bar_set.append(self.animation_data)
        
        # Appliquer des couleurs individuelles - CORRECTION: utiliser setColor()
        for i, color in enumerate(self.gradient_colors):
            if i < len(self.animation_data):
                self.bar_set.setColor(color)  # Définit la couleur pour tout le set
                # Note: PySide6 ne permet pas de définir des couleurs individuelles par barre
                # On utilisera une série différente pour chaque barre si nécessaire
        
        self.series_main.append(self.bar_set)
        self.chart.addSeries(self.series_main)
        
        # Axe X avec style amélioré
        axis_x = QBarCategoryAxis()
        axis_x.append(self.months)
        axis_x.setTitleText("Mois")
        axis_x.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        axis_x.setLabelsFont(QFont("Segoe UI", 9))
        axis_x.setLabelsAngle(0)
        axis_x.setGridLineVisible(False)
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.series_main.attachAxis(axis_x)
        
        # Axe Y avec style amélioré
        axis_y = QValueAxis()
        axis_y.setTitleText("Nombre de véhicules")
        axis_y.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        axis_y.setLabelsFont(QFont("Segoe UI", 9))
        axis_y.setRange(0, 35)
        axis_y.setTickCount(8)
        axis_y.setLabelFormat("%.0f")
        axis_y.setGridLineVisible(True)
        axis_y.setGridLineColor(QColor(226, 232, 240))
        axis_y.setLineVisible(True)
        axis_y.setLinePenColor(QColor(203, 213, 225))
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        self.series_main.attachAxis(axis_y)
        
        # Personnalisation de la légende
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignTop)
        self.chart.legend().setFont(QFont("Segoe UI", 9))
        self.chart.legend().setLabelColor(QColor(51, 65, 85))
        
        # Effet d'ombre 3D
        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(400)
        
        # Ombre portée
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            QChartView {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
        """)
        
    def animate_bars(self):
        """Animation 3D avec effet de vague et de pulsation"""
        self.animation_value += 0.04
        
        # Animation de vague sinusoïdale avec décalage par barre
        for i in range(len(self.current_data)):
            # Effet de vague progressive
            wave_offset = math.sin(self.animation_value + i * 0.5)
            # Effet de pulsation générale
            pulse = abs(math.sin(self.animation_value * 1.5)) * 0.15
            
            # Calcul de la hauteur animée
            base_value = self.current_data[i]
            target_amplitude = (self.target_data[i] - base_value) * 0.3
            animated_value = base_value + (wave_offset * 3) + (target_amplitude * abs(wave_offset))
            
            # Limiter la valeur
            animated_value = max(0.5, min(35, animated_value))
            self.animation_data[i] = animated_value
            
            # Mettre à jour la série
            self.bar_set.replace(i, animated_value)
            
            # Animation des couleurs (effet de brillance)
            if i < len(self.gradient_colors):
                color = self.gradient_colors[i]
                brightness = 0.7 + abs(math.sin(self.animation_value + i)) * 0.3
                animated_color = QColor(
                    min(255, int(color.red() * brightness)),
                    min(255, int(color.green() * brightness)),
                    min(255, int(color.blue() * brightness))
                )
                self.bar_set.setColor(animated_color)

class AnimatedBarChart3DImproved(QChartView):
    """Version alternative avec barres individuelles pour un effet 3D plus prononcé"""
    def __init__(self):
        super().__init__()
        self.setup_chart()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_bars)
        self.animation_value = 0
        self.animation_timer.start(50)
        
    def setup_chart(self):
        self.chart = QChart()
        self.chart.setTitle("Évolution du Parc Automobile")
        self.chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundVisible(False)
        self.chart.setTheme(QChart.ChartThemeLight)
        
        self.data = [5, 12, 8, 15, 20, 14, 18]
        self.months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil"]
        self.animation_data = self.data.copy()
        
        self.colors = [
            QColor(59, 130, 246),   # Bleu
            QColor(16, 185, 129),   # Vert
            QColor(245, 158, 11),   # Orange
            QColor(239, 68, 68),    # Rouge
            QColor(139, 92, 246),   # Violet
            QColor(236, 72, 153),   # Rose
            QColor(6, 182, 212)     # Cyan
        ]
        
        # Créer une série distincte pour chaque barre (permet des couleurs individuelles)
        self.series_list = []
        for i in range(len(self.data)):
            series = QBarSeries()
            bar_set = QBarSet(self.months[i])
            bar_set.append([self.animation_data[i]])
            bar_set.setColor(self.colors[i])
            series.append(bar_set)
            series.setBarWidth(0.5)
            self.series_list.append(series)
            self.chart.addSeries(series)
        
        # Axe X
        axis_x = QBarCategoryAxis()
        axis_x.append(self.months)
        axis_x.setTitleText("Mois")
        axis_x.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        axis_x.setLabelsFont(QFont("Segoe UI", 9))
        axis_x.setGridLineVisible(False)
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        
        # Axe Y
        axis_y = QValueAxis()
        axis_y.setTitleText("Nombre de véhicules")
        axis_y.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        axis_y.setLabelsFont(QFont("Segoe UI", 9))
        axis_y.setRange(0, 35)
        axis_y.setTickCount(8)
        axis_y.setGridLineColor(QColor(226, 232, 240))
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        
        # Attacher les axes à toutes les séries
        for series in self.series_list:
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)
        
        # Personnalisation de la légende
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignTop)
        self.chart.legend().setFont(QFont("Segoe UI", 9))
        
        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(400)
        
        # Ombre portée
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            QChartView {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
        """)
        
    def animate_bars(self):
        """Animation 3D avec effet de vague"""
        self.animation_value += 0.04
        
        for i in range(len(self.data)):
            # Effet de vague sinusoïdale
            wave_offset = math.sin(self.animation_value + i * 0.5)
            pulse = abs(math.sin(self.animation_value * 1.5)) * 0.15
            
            # Calcul de la hauteur animée
            animated_value = self.data[i] + (wave_offset * 2) + (pulse * 3)
            animated_value = max(0.5, min(35, animated_value))
            self.animation_data[i] = animated_value
            
            # Mettre à jour la barre
            if i < len(self.series_list):
                bar_set = self.series_list[i].barSets()[0]
                bar_set.replace(0, animated_value)
                
                # Animation des couleurs
                color = self.colors[i]
                brightness = 0.7 + abs(math.sin(self.animation_value + i)) * 0.3
                animated_color = QColor(
                    min(255, int(color.red() * brightness)),
                    min(255, int(color.green() * brightness)),
                    min(255, int(color.blue() * brightness))
                )
                bar_set.setColor(animated_color)


class TrendLineChart(QChartView):
    """Graphique de tendance avec courbe spline animée"""
    def __init__(self):
        super().__init__()
        self.setup_chart()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_line)
        self.progress = 0
        self.animation_timer.start(100)  # Démarrer l'animation immédiatement
        
    def setup_chart(self):
        self.chart = QChart()
        self.spline = QSplineSeries()
        self.area = QAreaSeries(self.spline)
        
        # Données simulées
        self.data_points = [
            QPointF(0, 45), QPointF(1, 52), QPointF(2, 48), QPointF(3, 55),
            QPointF(4, 62), QPointF(5, 58), QPointF(6, 65), QPointF(7, 72),
            QPointF(8, 78), QPointF(9, 85), QPointF(10, 82), QPointF(11, 90)
        ]
        
        # Zone sous la courbe
        self.area.setBrush(QBrush(QColor(59, 130, 246, 30)))
        self.spline.setColor(QColor(59, 130, 246))
        self.spline.setPointsVisible(True)
        self.spline.setPointLabelsVisible(True)
        self.spline.setPointLabelsColor(QColor(30, 41, 59))
        self.spline.setPen(QPen(QColor(59, 130, 246), 3))
        
        self.chart.addSeries(self.spline)
        self.chart.addSeries(self.area)
        
        self.chart.setTitle("Tendance des Immatriculations")
        self.chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundVisible(False)
        self.chart.setTheme(QChart.ChartThemeLight)
        
        # Axe X
        axis_x = QCategoryAxis()
        axis_x.append("Jan", 0)
        axis_x.append("Fév", 1)
        axis_x.append("Mar", 2)
        axis_x.append("Avr", 3)
        axis_x.append("Mai", 4)
        axis_x.append("Juin", 5)
        axis_x.append("Juil", 6)
        axis_x.append("Aoû", 7)
        axis_x.append("Sep", 8)
        axis_x.append("Oct", 9)
        axis_x.append("Nov", 10)
        axis_x.append("Déc", 11)
        axis_x.setTitleText("Mois")
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.spline.attachAxis(axis_x)
        
        # Axe Y
        axis_y = QValueAxis()
        axis_y.setTitleText("Nombre d'immatriculations")
        axis_y.setRange(0, 120)
        axis_y.setTickCount(7)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        self.spline.attachAxis(axis_y)
        
        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(400)
        
        # Ombre portée
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            QChartView {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
        """)
        
    def update_line(self):
        """Animation progressive de la courbe"""
        if self.progress < len(self.data_points):
            self.spline.clear()
            for i in range(self.progress + 1):
                self.spline.append(self.data_points[i])
            self.progress += 1
        else:
            self.animation_timer.stop()


class ScatterPerformanceChart(QChartView):
    """Nuage de points pour la performance des flottes"""
    def __init__(self):
        super().__init__()
        self.setup_chart()
        
    def setup_chart(self):
        self.chart = QChart()
        self.scatter = QScatterSeries()
        
        # Génération de données aléatoires
        for i in range(20):
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            self.scatter.append(x, y)
        
        self.scatter.setColor(QColor(139, 92, 246))
        self.scatter.setMarkerSize(14)
        self.scatter.setBorderColor(QColor(255, 255, 255))
        self.scatter.setBorderColor(2)
        
        self.chart.addSeries(self.scatter)
        self.chart.setTitle("Performance des Flottes")
        self.chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))
        self.chart.setBackgroundVisible(False)
        self.chart.setTheme(QChart.ChartThemeLight)
        
        # Axes
        axis_x = QValueAxis()
        axis_x.setTitleText("Utilisation (%)")
        axis_x.setRange(0, 100)
        axis_x.setTickCount(6)
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.scatter.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Performance (%)")
        axis_y.setRange(0, 100)
        axis_y.setTickCount(6)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        self.scatter.attachAxis(axis_y)
        
        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(400)
        
        # Ombre portée
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            QChartView {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
        """)


class Colors:
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    PRIMARY_LIGHT = "#60a5fa"
    SECONDARY = "#64748b"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    INFO = "#06b6d4"
    BACKGROUND = "#f8fafc"
    CARD_BG = "#ffffff"
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#475569"
    BORDER = "#e2e8f0"
    SIDEBAR_BG = "#ffffff"
    SIDEBAR_ACTIVE = "#eff6ff"


class VehicleMainView(QWidget):
    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BACKGROUND};
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
        """)
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_sidebar()
        self.setup_content_area()

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_container, 1)

        self.btn_dash.clicked.connect(lambda: self._switch_page(0, self.btn_dash))
        self.btn_vehicles.clicked.connect(lambda: self._switch_page(1, self.btn_vehicles))
        self.btn_clients.clicked.connect(lambda: self._switch_page(2, self.btn_clients))
        self.btn_comp.clicked.connect(lambda: self._switch_page(3, self.btn_comp))

    def setup_sidebar(self):
        """Configure la sidebar avec un design moderne"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-right: 1px solid {Colors.BORDER};
            }}
        """)
        
        # Ombre pour la sidebar
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(2, 0)
        self.sidebar.setGraphicsEffect(shadow)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # En-tête de la sidebar
        header = QFrame()
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        logo = QLabel("🚗 Automobile")
        logo.setStyleSheet("font-size: 28px; background: transparent;")
        
        header_layout.addWidget(logo)
        header_layout.addStretch()
        
        sidebar_layout.addWidget(header)

        # Zone de navigation
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(16, 30, 16, 30)
        nav_layout.setSpacing(8)

        nav_title = QLabel("NAVIGATION")
        nav_title.setStyleSheet(f"""
            color: {Colors.SECONDARY};
            font-weight: 600;
            font-size: 11px;
            letter-spacing: 1px;
            margin-bottom: 12px;
        """)
        nav_layout.addWidget(nav_title)

        self.btn_dash = self._create_nav_btn("📊 Tableau de Bord", active=True)
        self.btn_vehicles = self._create_nav_btn("🚗 Véhicules")
        self.btn_comp = self._create_nav_btn("🏢 Compagnies et Tarifs")
        self.btn_clients = self._create_nav_btn("👥 Clients")

        nav_layout.addWidget(self.btn_dash)
        nav_layout.addWidget(self.btn_vehicles)
        nav_layout.addWidget(self.btn_comp)
        nav_layout.addWidget(self.btn_clients)
        nav_layout.addStretch()

        sidebar_layout.addWidget(nav_container)

    def setup_content_area(self):
        """Configure la zone de contenu principale"""
        self.content_container = QWidget()
        self.content_container.setStyleSheet("background: transparent;")
        
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(24)

        # Header de la page
        page_header = QFrame()
        page_header.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 20px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        page_header.setFixedHeight(70)
        
        header_layout = QHBoxLayout(page_header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        
        self.page_title = QLabel("Tableau de Bord")
        self.page_title.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {Colors.TEXT_PRIMARY};
        """)
        
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()
        
        content_layout.addWidget(page_header)

        # Cartes KPI
        self.setup_kpi_cards()
        content_layout.addLayout(self.kpi_layout)

        # Stacked Widget
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("""
            QStackedWidget {
                background: transparent;
            }
        """)
        
        self.page_dashboard = self._init_dashboard_page()
        self.page_vehicles = self._init_vehicles_page()
        self.page_clients = self._init_contacts_page()
        self.page_compagnies = self._init_compagnies_page()
        
        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_vehicles)
        self.stack.addWidget(self.page_clients)
        self.stack.addWidget(self.page_compagnies)
        
        content_layout.addWidget(self.stack)

    def setup_kpi_cards(self):
        """Configure les cartes KPI modernes"""
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(20)
        
        kpi_data = [
            {"title": "Véhicules", "value": "142", "trend": "+12", "color": Colors.PRIMARY, "icon": "🚗", "trend_up": True},
            {"title": "Flottes", "value": "12", "trend": "+3", "color": Colors.SUCCESS, "icon": "🏢", "trend_up": True},
            {"title": "Entreprises", "value": "08", "trend": "+2", "color": Colors.WARNING, "icon": "🏭", "trend_up": True},
            {"title": "Particuliers", "value": "89", "trend": "+8", "color": Colors.INFO, "icon": "👤", "trend_up": True}
        ]
        
        for data in kpi_data:
            card = self._create_modern_kpi_card(data)
            self.kpi_layout.addWidget(card)

    def _create_modern_kpi_card(self, data):
        """Crée une carte KPI simple et élégante"""
        main_color = data.get('color', '#3B82F6')
        trend_up = data.get('trend_up', True)
        trend_color = '#10B981' if trend_up else '#EF4444'
        trend_icon = '↑' if trend_up else '↓'
        
        card = QFrame()
        card.setFixedHeight(110)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {Colors.BORDER};
                border-radius: 16px;
            }}
            QFrame:hover {{
                border-color: {main_color};
                background: {main_color}04;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(12)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(6)
        
        value = QLabel(data['value'])
        value.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {main_color};")
        
        title = QLabel(data['title'])
        title.setStyleSheet(f"font-size: 12px; font-weight: 500; color: {Colors.TEXT_SECONDARY};")
        
        trend = QLabel(f"{trend_icon} {data['trend']}")
        trend.setStyleSheet(f"font-size: 11px; font-weight: 500; color: {trend_color};")
        
        text_layout.addWidget(value)
        text_layout.addWidget(title)
        text_layout.addWidget(trend)
        text_layout.addStretch()
        
        icon_container = QFrame()
        icon_container.setFixedSize(44, 44)
        icon_container.setStyleSheet(f"""
            background: {main_color}10;
            border-radius: 12px;
        """)
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon = QLabel(data['icon'])
        icon.setStyleSheet("font-size: 22px;")
        icon_layout.addWidget(icon)
        
        layout.addLayout(text_layout, 1)
        layout.addWidget(icon_container)
        
        return card

    def _create_nav_btn(self, text, active=False):
        """Crée un bouton de navigation moderne"""
        btn = QPushButton(text)
        btn.setFixedHeight(48)
        btn.setCursor(Qt.PointingHandCursor)
        self._style_nav_btn(btn, active)
        return btn

    def _style_nav_btn(self, btn, active):
        """Applique le style aux boutons de navigation"""
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {Colors.SIDEBAR_ACTIVE};
                    color: {Colors.PRIMARY};
                    font-weight: 600;
                    border-radius: 12px;
                    text-align: left;
                    padding-left: 16px;
                    border: none;
                }}
                QPushButton:hover {{
                    background: {Colors.PRIMARY}10;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {Colors.TEXT_SECONDARY};
                    border-radius: 12px;
                    text-align: left;
                    padding-left: 16px;
                    border: none;
                }}
                QPushButton:hover {{
                    background: {Colors.PRIMARY}08;
                    color: {Colors.PRIMARY};
                }}
            """)

    def _switch_page(self, index, btn):
        """Change la page active avec animation"""
        self.stack.setCurrentIndex(index)
        
        titles = ["Tableau de Bord", "Gestion des Véhicules", "Gestion des Clients", "Compagnies et Tarifs"]
        self.page_title.setText(titles[index])
        
        for b in [self.btn_dash, self.btn_vehicles, self.btn_comp, self.btn_clients]:
            self._style_nav_btn(b, False)
        self._style_nav_btn(btn, True)

    # ========== PAGES ==========

    def _init_dashboard_page(self):
        """Page Dashboard avec graphiques modernes et animés"""
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)
        
        # Ligne 1: Camembert + Barres 3D
        row1 = QHBoxLayout()
        row1.setSpacing(20)
        
        stats = self.controller.contacts.get_contact_stats() if self.controller and hasattr(self.controller, 'contacts') else {'Physique': 65, 'Morale': 35}
        pie_data = {
            "Particuliers": stats.get('Physique', 65),
            "Entreprises": stats.get('Morale', 35)
        }
        
        self.pie_chart = AnimatedPieChart3D(pie_data, donut_mode=True) 
        self.bar_chart = AnimatedBarChart3D()
        
        row1.addWidget(self.pie_chart, 1)
        row1.addWidget(self.bar_chart, 1)
        layout.addLayout(row1)
        
        # Ligne 2: Courbe de tendance + Monitor réseau
        row2 = QHBoxLayout()
        row2.setSpacing(20)
        
        self.trend_chart = TrendLineChart()
        self.network_monitor = NetworkSpeedMonitor()
        
        row2.addWidget(self.trend_chart, 2)
        row2.addWidget(self.network_monitor, 1)
        layout.addLayout(row2)
        
        # Ligne 3: Nuage de points
        row3 = QHBoxLayout()
        row3.setSpacing(20)
        
        self.scatter_chart = ScatterPerformanceChart()
        row3.addWidget(self.scatter_chart, 1)
        layout.addLayout(row3)
        
        scroll.setWidget(container)
        
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        
        return page

    def _init_vehicles_page(self):
        if not self.controller:
            return QWidget()
        
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        full_management_page = VehiculeModuleView(
            controller=self.controller, 
            current_user=self.user
        )
        layout.addWidget(full_management_page)
        
        return page

    def _init_contacts_page(self):
        if not self.controller:
            return QWidget()
        
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        client_page = ContactListView(
            controller=self.controller, 
            current_user=self.user
        )
        layout.addWidget(client_page)
        
        return page

    def _init_compagnies_page(self):
        if not self.controller:
            return QWidget()
        
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        compagnies_page = CompanyTariffView(
            controller=self.controller, 
            current_user=self.user
        )
        layout.addWidget(compagnies_page)
        
        return page