# addons/Automobiles/main_ui.py - Version avec animation non bloquante

from PySide6.QtWidgets import QPushButton, QFrame, QVBoxLayout, QLabel, QProgressBar, QGraphicsDropShadowEffect, QApplication, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QThread, Signal, QEasingCurve, QMetaObject, Q_ARG, Slot
from PySide6.QtGui import QColor, QPainter, QPen, QBrush
import math
import os
import json
from pathlib import Path

from core.base_module import BaseModule
from core.alerts import AlertManager

from addons.Automobiles.views.view import VehicleMainView
from addons.Automobiles.controllers import AutomobileMainController

#============================================================================
# IMPORT DU MODULE API ASAC
# ============================================================================
try:
    from addons.Automobiles.api import AsacService, AsacCredentials, AsacAPIError
    ASAC_AVAILABLE = True
except ImportError:
    ASAC_AVAILABLE = False
    print("⚠️ Module ASAC non disponible - fonction d'export désactivée")


class ModernSpinner(QWidget):
    """Spinner moderne qui tourne SANS bloquer l'UI"""
    
    def __init__(self, parent=None, size=48):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._angle = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._rotate)
        self._timer.setInterval(16)  # 60 FPS
        self._animation_running = False
        
        self._colors = [
            QColor("#3b82f6"), QColor("#6366f1"), QColor("#8b5cf6"),
            QColor("#06b6d4"), QColor("#10b981"),
        ]
        self._current_color = 0
        
    def start(self):
        """Démarre l'animation (non bloquante)"""
        if not self._animation_running:
            self._animation_running = True
            self._timer.start()
        
    def stop(self):
        """Arrête l'animation"""
        if self._animation_running:
            self._animation_running = False
            self._timer.stop()
            self._angle = 0
            self.update()
        
    def _rotate(self):
        """Rotation (appelée par le timer, thread principal mais non bloquante)"""
        self._angle = (self._angle + 8) % 360
        self._current_color = (self._current_color + 1) % len(self._colors)
        self.update()  # Schedule repaint, ne bloque pas
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(self.width(), self.height()) // 2 - 4
        
        # Anneau de fond
        pen = QPen()
        pen.setColor(QColor("#e2e8f0"))
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(center_x - radius, center_y - radius, 2 * radius, 2 * radius, 0, 360 * 16)
        
        # Anneau animé
        pen.setColor(self._colors[self._current_color])
        painter.setPen(pen)
        start_angle = self._angle * 16
        painter.drawArc(center_x - radius, center_y - radius, 2 * radius, 2 * radius, start_angle, 270 * 16)
        
        painter.end()


class GlassCard(QFrame):
    """Carte glassmorphism"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.98);
                border-radius: 28px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)


class AsacInitializer(QThread):
    """Thread pour initialiser l'API ASAC en arrière-plan"""
    
    initialized = Signal(bool, str, object)  # success, message, service
    progress = Signal(int, str)
    
    def __init__(self, config_path=None):
        super().__init__()
        self.config_path = config_path or self._get_default_config_path()
        
    def _get_default_config_path(self):
        """Chemin par défaut du fichier de configuration"""
        # Chercher dans plusieurs endroits
        paths = [
            Path(__file__).parent / "config" / "asac_config.json",
            Path(__file__).parent / "asac_config.json",
            Path.home() / ".lometa" / "asac_config.json",
        ]
        for path in paths:
            if path.exists():
                return str(path)
        return None
    
    def run(self):
        try:
            # Étape 1: Charger la configuration
            self.progress.emit(10, "📋 Chargement de la configuration ASAC...")
            
            config = self._load_config()
            if not config:
                self.progress.emit(100, "⚠️ Configuration ASAC manquante")
                self.initialized.emit(False, "Fichier de configuration ASAC non trouvé", None)
                return
            
            # Étape 2: Vérifier les credentials
            self.progress.emit(30, "🔑 Vérification des identifiants ASAC...")
            
            app_key = config.get("app_key")
            username = config.get("username")
            api_url = config.get("api_url", "https://ppeatt-api.asac.cm")
            
            if not app_key or not username:
                self.progress.emit(100, "⚠️ Credentials ASAC incomplets")
                self.initialized.emit(False, "Clé applicative ou nom d'utilisateur manquant", None)
                return
            
            # Étape 3: Créer le service
            self.progress.emit(50, "🔧 Initialisation du service ASAC...")
            
            credentials = AsacCredentials(
                app_key=app_key,
                username=username,
                api_url=api_url
            )
            service = AsacService(credentials)
            
            # Étape 4: Tester la connexion (authentification)
            self.progress.emit(70, "🌐 Test de connexion à l'API ASAC...")
            
            try:
                token = service.authenticate()
                self.progress.emit(100, f"✅ ASAC connecté (expire: {token.expires_at.strftime('%d/%m/%Y %H:%M')})")
                self.initialized.emit(True, "API ASAC initialisée avec succès", service)
            except AsacAPIError as e:
                self.progress.emit(100, f"❌ Erreur ASAC: {str(e)[:50]}...")
                self.initialized.emit(False, f"Erreur d'authentification ASAC: {str(e)}", None)
                
        except Exception as e:
            self.progress.emit(100, f"❌ Erreur: {str(e)[:50]}...")
            self.initialized.emit(False, f"Erreur d'initialisation ASAC: {str(e)}", None)
    
    def _load_config(self):
        """Charge la configuration ASAC"""
        # Essayer de charger depuis le fichier JSON
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Essayer depuis les variables d'environnement
        config = {
            "app_key": os.environ.get("ASAC_APP_KEY"),
            "username": os.environ.get("ASAC_USERNAME"),
            "api_url": os.environ.get("ASAC_API_URL", "https://ppeatt-api.asac.cm"),
            "office_code": os.environ.get("ASAC_OFFICE_CODE", "AG-DLA-001"),
            "organization_code": os.environ.get("ASAC_ORGANIZATION_CODE", "ACTIVA")
        }
        
        if config["app_key"] and config["username"]:
            return config
        
        # Essayer depuis un fichier .env
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if key == "ASAC_APP_KEY":
                            config["app_key"] = value
                        elif key == "ASAC_USERNAME":
                            config["username"] = value
                        elif key == "ASAC_API_URL":
                            config["api_url"] = value
                        elif key == "ASAC_OFFICE_CODE":
                            config["office_code"] = value
                        elif key == "ASAC_ORGANIZATION_CODE":
                            config["organization_code"] = value
            
            if config["app_key"] and config["username"]:
                return config
        
        return None


class LoadingOverlay(QFrame):
    """Overlay de chargement avec animations fluides NON BLOQUANTES"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.hide()
        
        self._setup_ui()
        self._setup_animations()
        
        # ✅ Timer pour animation continue (indépendante des requêtes)
        self._continuous_animation_timer = QTimer()
        self._continuous_animation_timer.timeout.connect(self._animate_continuous)
        self._continuous_animation_timer.setInterval(50)  # 20 FPS
        self._animation_value = 0

        # ✅ AJOUTER CES LIGNES
        self._base_message = ""
        self._continuous_step = 0
        self._continuous_timer = QTimer()
        self._continuous_timer.timeout.connect(self._continuous_animation)
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.card = GlassCard()
        card_layout = QVBoxLayout(self.card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(24)
        card_layout.setContentsMargins(48, 40, 48, 40)
        
        self.spinner = ModernSpinner(size=64)
        card_layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        
        self.title_label = QLabel("Chargement")
        self.title_label.setStyleSheet("color: #1e293b; font-size: 22px; font-weight: 700; background: transparent;")
        card_layout.addWidget(self.title_label, alignment=Qt.AlignCenter)
        
        self.message_label = QLabel("Veuillez patienter...")
        self.message_label.setStyleSheet("color: #64748b; font-size: 14px; background: transparent;")
        card_layout.addWidget(self.message_label, alignment=Qt.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #f1f5f9;
                border-radius: 8px;
                height: 6px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:0.5 #6366f1, stop:1 #8b5cf6);
                border-radius: 8px;
            }
        """)
        card_layout.addWidget(self.progress_bar)
        
        info_layout = QHBoxLayout()
        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet("color: #3b82f6; font-size: 12px; font-weight: 600;")
        self.step_label = QLabel("Initialisation...")
        self.step_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        self.step_label.setAlignment(Qt.AlignRight)
        info_layout.addWidget(self.percentage_label)
        info_layout.addStretch()
        info_layout.addWidget(self.step_label)
        card_layout.addLayout(info_layout)
        
        layout.addWidget(self.card)
        
    def _setup_animations(self):
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        self.zoom_anim = QPropertyAnimation(self.card, b"geometry")
        self.zoom_anim.setDuration(400)
        self.zoom_anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        
        self.progress_anim = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_anim.setDuration(400)

    def _animate_continuous(self):
        """Animation continue indépendante des requêtes"""
        self._animation_value += 0.05
        
        # 1. Animation du spinner (rotation des couleurs)
        if hasattr(self, 'spinner') and self.spinner:
            # Changer la couleur du spinner cycliquement
            colors = ["#3b82f6", "#6366f1", "#8b5cf6", "#06b6d4", "#10b981"]
            color_index = int(self._animation_value * 2) % len(colors)
            self.spinner._current_color = color_index
            self.spinner.update()
        
        # 2. Animation de la barre de progression (va et vient)
        if hasattr(self, 'progress_bar'):
            # Effet de vague sur la barre de progression
            progress = int((abs(math.sin(self._animation_value)) * 100))
            self.progress_bar.setValue(progress)
            self.percentage_label.setText(f"{progress}%")
        
        # 3. Animation du texte des étapes (cycle de messages)
        messages = [
            "🔄 Initialisation...",
            "📊 Chargement des données...",
            "⚙️ Traitement en cours...",
            "🎨 Préparation de l'interface...",
            "✨ Presque terminé..."
        ]
        msg_index = int(self._animation_value * 0.5) % len(messages)
        self.step_label.setText(messages[msg_index])
        
        # 4. Animation de pulsation du titre
        pulse = 0.8 + abs(math.sin(self._animation_value * 3)) * 0.2
        self.title_label.setStyleSheet(f"""
            color: #1e293b; 
            font-size: {int(20 + pulse * 2)}px; 
            font-weight: 700; 
            background: transparent;
        """)

    def _start_progress_animation(self):
        """Animation continue de la barre de progression"""
        self._progress_anim_value = 0
        
        def animate():
            self._progress_anim_value = (self._progress_anim_value + 2) % 100
            self.progress_bar.setValue(self._progress_anim_value)
            self.percentage_label.setText(f"{self._progress_anim_value}%")
        
        # Timer pour animation fluide de la barre
        self._progress_timer = QTimer()
        self._progress_timer.timeout.connect(animate)
        self._progress_timer.start(30)
        
    def show_loading(self, message="Chargement...", title=None, simulate=False):
        """Affiche l'overlay avec animation continue indépendante"""
        self._base_message = message
        self.message_label.setText(message)
        if title:
            self.title_label.setText(title)
        
        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")
        self.step_label.setText("Initialisation...")
        self.spinner.start()
        
        if self.parent():
            self.resize(self.parent().size())
        
        # Animation d'entrée
        self.setWindowOpacity(0)
        self.show()
        self.raise_()
        
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.start()
        
        QTimer.singleShot(50, self._start_zoom_animation)
        
        # ✅ DÉMARRER L'ANIMATION CONTINUE (indépendante des requêtes)
        self._continuous_step = 0
        if not hasattr(self, '_continuous_timer'):
            self._continuous_timer = QTimer()
            self._continuous_timer.timeout.connect(self._continuous_animation)
        self._continuous_timer.start(80)  # Animation fluide
        
        # Simulation de progression (optionnelle)
        if simulate:
            self._simulated_value = 0
            self._continuous_animation_timer.start(50)
        
    def _start_zoom_animation(self):
        if not self.isVisible():
            return
        card_geo = self.card.geometry()
        start_rect = card_geo.adjusted(30, 20, -30, -20)
        self.card.setGeometry(start_rect)
        self.zoom_anim.setStartValue(start_rect)
        self.zoom_anim.setEndValue(card_geo)
        self.zoom_anim.start()
        
    def _simulate_progress(self):
        """Simule une progression pour donner l'illusion de travail"""
        if self._simulated_value < 90:
            self._simulated_value += 1
            self.progress_bar.setValue(self._simulated_value)
            self.percentage_label.setText(f"{self._simulated_value}%")
        
    def update_progress(self, value, step=None):
        """Met à jour la progression (appel depuis n'importe quel thread)"""
        # Utiliser invokeMethod pour thread-safety
        QMetaObject.invokeMethod(self, "_do_update_progress", 
                                 Qt.ConnectionType.QueuedConnection,
                                 Q_ARG(int, value),
                                 Q_ARG(str, step or ""))
        
    @Slot(int, str)
    def _do_update_progress(self, value, step):
        """Exécuté dans le thread principal"""
        self.progress_anim.setStartValue(self.progress_bar.value())
        self.progress_anim.setEndValue(value)
        self.progress_anim.start()
        
        self.percentage_label.setText(f"{value}%")
        
        if step:
            self.step_label.setText(step)
            self._animate_step_label()
        
        if value >= 100:
            self._continuous_animation_timer.stop()
        
    def _animate_step_label(self):
        anim = QPropertyAnimation(self.step_label, b"styleSheet")
        anim.setDuration(250)
        anim.setKeyValueAt(0, "color: #94a3b8; font-size: 12px;")
        anim.setKeyValueAt(0.5, "color: #3b82f6; font-size: 12px; font-weight: 500;")
        anim.setKeyValueAt(1, "color: #94a3b8; font-size: 12px;")
        anim.start()
        
    def hide_loading(self):
        """Cache l'overlay - Arrête toutes les animations"""
        # ✅ Arrêter tous les timers d'animation
        if hasattr(self, '_continuous_animation_timer'):
            self._continuous_animation_timer.stop()
        if hasattr(self, '_progress_timer'):
            self._progress_timer.stop()
        
        # Arrêter le spinner
        if hasattr(self, 'spinner'):
            self.spinner.stop()
        
        # Animation de disparition
        self.fade_anim.setStartValue(1)
        self.fade_anim.setEndValue(0)
        self.fade_anim.finished.connect(self._on_fade_out_complete)
        self.fade_anim.start()
        
    def _on_fade_out_complete(self):
        self.fade_anim.finished.disconnect(self._on_fade_out_complete)
        self.hide()
        
    def resizeEvent(self, event):
        if self.parent():
            self.resize(self.parent().size())
            parent_rect = self.rect()
            self.card.setGeometry(
                (parent_rect.width() - 400) // 2,
                (parent_rect.height() - 320) // 2,
                400, 320
            )
        super().resizeEvent(event)

    def _continuous_animation(self):
        """Animation continue qui tourne jusqu'à la fermeture"""
        self._continuous_step += 1
        
        # 1. Animation de la barre de progression (aller-retour)
        step = self._continuous_step % 200
        if step <= 100:
            progress = step
        else:
            progress = 200 - step
        self.progress_bar.setValue(progress)
        self.percentage_label.setText(f"{progress}%")
        
        # 2. Animation du texte d'étape (cycle)
        steps = [
            "🔄 Analyse des données...",
            "📊 Chargement en cours...",
            "⚙️ Traitement des informations...",
            "🎨 Préparation de l'affichage...",
            "✨ Finalisation..."
        ]
        idx = (self._continuous_step // 15) % len(steps)
        self.step_label.setText(steps[idx])
        
        # 3. Animation du message (points qui dansent)
        if hasattr(self, '_base_message'):
            dots = "." * ((self._continuous_step // 10) % 4)
            self.message_label.setText(f"{self._base_message}{dots}")
        
        # 4. Animation du titre (pulsation)
        pulse = 0.9 + (self._continuous_step % 20) / 100
        self.title_label.setStyleSheet(f"""
            color: #1e293b; 
            font-size: {int(20 + pulse * 2)}px; 
            font-weight: 700; 
            background: transparent;
        """)


class ModuleInitThread(QThread):
    """Thread avec progression dynamique et chargement optimisé"""
    
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(int, str)
    
    def __init__(self, db_session, user):
        super().__init__()
        self.db_session = db_session
        self.user = user
        
    def run(self):
        try:
            user_id = self.user.id if hasattr(self.user, 'id') else self.user
            
            # Progression linéaire
            self.progress.emit(0, "🚀 Démarrage...")
            
            # Étape 1: Vérification session
            self.progress.emit(5, "🔐 Vérification de la session...")
            
            # Étape 2: Connexion DB
            self.progress.emit(10, "💾 Connexion à la base de données...")
            
            # Étape 3: Chargement des véhicules (avec timeout)
            self.progress.emit(20, "🚗 Chargement des véhicules...")
            try:
                from addons.Automobiles.models import Vehicle
                # Utiliser une requête plus légère
                vehicles_query = self.db_session.query(Vehicle.id, Vehicle.immatriculation).filter_by(owner_id=user_id)
                vehicle_count = vehicles_query.count()
                self.progress.emit(25, f"🚗 {vehicle_count} véhicules chargés")
            except Exception as e:
                self.progress.emit(25, f"🚗 Erreur chargement véhicules: {str(e)[:50]}")
            
            # Étape 4: Chargement des contrats (optimisé)
            self.progress.emit(35, "📄 Chargement des contrats...")
            try:
                from addons.Automobiles.models import Contrat
                # Ne charger que les IDs et champs essentiels
                contrats_query = self.db_session.query(Contrat.id, Contrat.numero_police).filter_by(owner_id=user_id)
                contrat_count = contrats_query.count()
                self.progress.emit(40, f"📄 {contrat_count} contrats chargés")
            except Exception as e:
                self.progress.emit(40, f"📄 Erreur chargement contrats: {str(e)[:50]}")
            
            # Étape 5: Chargement des clients - CORRECTION ICI
            self.progress.emit(45, "👥 Chargement des clients...")
            try:
                from addons.Paramètres.models.models import User
                # OPTIMISATION 1: Utiliser une requête avec timeout
                # OPTIMISATION 2: Ne compter que si nécessaire
                # OPTIMISATION 3: Mettre en cache
                
                # Version avec timeout personnalisé (si possible)
                import threading
                import time
                
                client_count = 0
                def count_clients():
                    nonlocal client_count
                    try:
                        # Utiliser une requête plus légère
                        client_count = self.db_session.query(User.id).filter_by(role='client').count()
                    except:
                        client_count = -1
                
                # Exécuter avec timeout (5 secondes max)
                thread = threading.Thread(target=count_clients)
                thread.daemon = True
                thread.start()
                thread.join(timeout=5)
                
                if thread.is_alive():
                    self.progress.emit(50, "👥 Chargement clients: timeout (trop long)...")
                    client_count = 0  # Valeur par défaut
                else:
                    if client_count >= 0:
                        self.progress.emit(50, f"👥 {client_count} clients chargés")
                    else:
                        self.progress.emit(50, "👥 Clients: non disponible")
                        
            except Exception as e:
                self.progress.emit(50, f"👥 Clients ignorés: {str(e)[:40]}")
            
            # Étape 6: Calcul des statistiques (optionnel)
            self.progress.emit(60, "📊 Préparation des données...")
            
            # Étape 7: Initialisation du contrôleur
            self.progress.emit(70, "⚙️ Initialisation du contrôleur...")
            controller = AutomobileMainController(
                session=self.db_session,
                current_user_id=user_id
            )
            self.progress.emit(85, "⚙️ Contrôleur initialisé")
            
            # Étape 8: Préparation de l'interface
            self.progress.emit(90, "🎨 Préparation de l'interface...")
            
            # Finalisation
            self.progress.emit(100, "✅ Module prêt !")
            self.finished.emit(controller)
            
        except Exception as e:
            self.error.emit(str(e))
           

class AutomobileModule(BaseModule):
    """Module automobile avec chargement asynchrone NON BLOQUANT"""
    
    BUTTON_HEIGHT = 45
    BUTTON_STYLE = """
        QPushButton {
            background-color: transparent;
            color: #f8fafc;
            text-align: left;
            padding-left: 20px;
            border: none;
            border-radius: 8px;
            margin: 2px 10px;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #334155;
        }
        QPushButton:pressed {
            background-color: #1e293b;
        }
    """
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self._view = None
        self._controller = None
        self._button = None
        self._loading_overlay = None
        self._init_thread = None
        
    def setup(self):
        self._create_navigation_button()
        self._add_to_sidebar()
        
    def _create_navigation_button(self):
        self._button = QPushButton("🚗  Automobile")
        self._button.setFixedHeight(self.BUTTON_HEIGHT)
        self._button.setCursor(Qt.PointingHandCursor)
        self._button.setStyleSheet(self.BUTTON_STYLE)
        self._button.clicked.connect(self.activate_module)
        
    def _add_to_sidebar(self):
        sidebar_layout = getattr(self.main_window, 'sidebar_layout', None)
        if sidebar_layout:
            sidebar_layout.addWidget(self._button)
            return
        sidebar = getattr(self.main_window, 'sidebar', None)
        if sidebar and hasattr(sidebar, 'layout'):
            sidebar.layout().addWidget(self._button)
            
    def _ensure_loading_overlay(self):
        if self._loading_overlay:
            return self._loading_overlay
        parent = self.main_window.centralWidget() if self.main_window else None
        if parent:
            self._loading_overlay = LoadingOverlay(parent)
        return self._loading_overlay
        
    def activate_module(self):
        """Active le module - UI reste complètement réactive"""
        loader = self._ensure_loading_overlay()
        if loader:
            loader.show_loading("Chargement du module Automobile...", "Initialisation", simulate=True)
        
        # Forcer l'update UI (non bloquant)
        QApplication.processEvents()
        
        current_user = self._get_current_user()
        if not current_user:
            self._hide_loader_and_show_error(loader, "Accès Refusé", "Veuillez vous connecter.")
            return
        
        content_stack = self._get_content_area()
        if not content_stack:
            self._hide_loader_and_show_error(loader, "Erreur", "Zone de contenu introuvable.")
            return
        
        if not self._view or not self._controller:
            self._init_module_async(current_user, content_stack, loader)
        else:
            self._show_module(content_stack, loader)
            
    def _init_module_async(self, current_user, content_stack, loader):
        """Initialisation dans un thread - UI reste réactive"""
        self._init_thread = ModuleInitThread(self.db_session, current_user)
        self._init_thread.finished.connect(
            lambda controller: self._on_module_initialized(controller, current_user, content_stack, loader)
        )
        self._init_thread.error.connect(lambda error: self._on_init_error(error, loader))
        self._init_thread.progress.connect(lambda value, step: self._on_progress(loader, value, step))
        self._init_thread.start()
        
    def _on_progress(self, loader, value, step):
        """Mise à jour progression (thread-safe)"""
        if loader:
            loader.update_progress(value, step)
            
    def _on_module_initialized(self, controller, current_user, content_stack, loader):
        """Finalisation dans le thread principal"""
        self._controller = controller
        self._view = VehicleMainView(controller=self._controller, user=current_user)
        
        if content_stack.indexOf(self._view) == -1:
            content_stack.addWidget(self._view)
        
        content_stack.setCurrentWidget(self._view)
        
        if loader:
            loader.hide_loading()
        
        if self._init_thread:
            self._init_thread.deleteLater()
            self._init_thread = None
            
    def _show_module(self, content_stack, loader):
        if content_stack.indexOf(self._view) == -1:
            content_stack.addWidget(self._view)
        content_stack.setCurrentWidget(self._view)
        if loader:
            loader.hide_loading()
            
    def _hide_loader_and_show_error(self, loader, title, message):
        if loader:
            loader.hide_loading()
        AlertManager.show_error(self.main_window, title, message)
        
    def _on_init_error(self, error, loader):
        if loader:
            loader.hide_loading()
        AlertManager.show_error(self.main_window, "Erreur d'initialisation", f"Erreur: {error}")
        if self._init_thread:
            self._init_thread.deleteLater()
            self._init_thread = None
            
    def _get_current_user(self):
        return getattr(self.main_window, 'current_user', None)
        
    def _get_content_area(self):
        content_attrs = ['content_area', 'stacked_widget', 'main_stack', 'content_stack']
        for attr in content_attrs:
            content_area = getattr(self.main_window, attr, None)
            if content_area:
                return content_area
        return None
        
    def _log_error(self, message):
        print(f"[AutomobileModule] ERROR: {message}")
        
    @property
    def view(self):
        return self._view
        
    @property
    def controller(self):
        return self._controller
        
    @property
    def db_session(self):
        return getattr(self.main_window, 'db_session', None)
        
    def cleanup(self):
        if self._init_thread and self._init_thread.isRunning():
            self._init_thread.quit()
            self._init_thread.wait(1000)
            self._init_thread = None
        if self._controller and hasattr(self._controller, 'cleanup'):
            self._controller.cleanup()
        if self._view:
            self._view.deleteLater()
            self._view = None
        if self._loading_overlay:
            self._loading_overlay.deleteLater()
            self._loading_overlay = None
        self._controller = None


# class AutomobileModule(BaseModule):
#     """Module automobile - L'API ASAC est optionnelle et non bloquante"""
    
#     BUTTON_HEIGHT = 45
#     BUTTON_STYLE = """
#         QPushButton {
#             background-color: transparent;
#             color: #f8fafc;
#             text-align: left;
#             padding-left: 20px;
#             border: none;
#             border-radius: 8px;
#             margin: 2px 10px;
#             font-size: 13px;
#             font-weight: 500;
#         }
#         QPushButton:hover {
#             background-color: #334155;
#         }
#         QPushButton:pressed {
#             background-color: #1e293b;
#         }
#     """
    
#     def __init__(self, main_window):
#         super().__init__(main_window)
#         self._view = None
#         self._controller = None
#         self._button = None
#         self._loading_overlay = None
#         self._init_thread = None
#         self._asac_service = None
#         self._asac_initializer = None
#         self._asac_available = False
        
#     def setup(self):
#         self._create_navigation_button()
#         self._add_to_sidebar()
#         # Démarrer l'initialisation ASAC en arrière-plan (non bloquante)
#         self._start_asac_initialization()
        
#     def _create_navigation_button(self):
#         self._button = QPushButton("🚗  Automobile")
#         self._button.setFixedHeight(self.BUTTON_HEIGHT)
#         self._button.setCursor(Qt.PointingHandCursor)
#         self._button.setStyleSheet(self.BUTTON_STYLE)
#         self._button.clicked.connect(self.activate_module)
        
#     def _add_to_sidebar(self):
#         sidebar_layout = getattr(self.main_window, 'sidebar_layout', None)
#         if sidebar_layout:
#             sidebar_layout.addWidget(self._button)
#             return
#         sidebar = getattr(self.main_window, 'sidebar', None)
#         if sidebar and hasattr(sidebar, 'layout'):
#             sidebar.layout().addWidget(self._button)
            
#     def _ensure_loading_overlay(self):
#         if self._loading_overlay:
#             return self._loading_overlay
#         parent = self.main_window.centralWidget() if self.main_window else None
#         if parent:
#             self._loading_overlay = LoadingOverlay(parent)
#         return self._loading_overlay
    
#     def _start_asac_initialization(self):
#         """Démarre l'initialisation de l'API ASAC en arrière-plan (NON BLOQUANT)"""
#         if not ASAC_AVAILABLE:
#             print("⚠️ Module ASAC non disponible")
#             return
            
#         if self._asac_initializer and self._asac_initializer.isRunning():
#             return
        
#         self._asac_initializer = AsacInitializer()
#         self._asac_initializer.initialized.connect(self._on_asac_initialized)
#         self._asac_initializer.start()
#         print("🔄 Initialisation ASAC en arrière-plan...")
    
#     def _on_asac_initialized(self, success, message, service):
#         """Callback quand ASAC est initialisé (ne bloque pas l'UI)"""
#         if success:
#             self._asac_service = service
#             self._asac_available = True
#             print(f"✅ {message}")
#             # Mettre à jour la vue si elle existe déjà
#             if self._view and hasattr(self._view, 'set_asac_service'):
#                 self._view.set_asac_service(service)
#         else:
#             self._asac_service = None
#             self._asac_available = False
#             print(f"⚠️ {message}")
        
#         # Nettoyer le thread
#         if self._asac_initializer:
#             self._asac_initializer.deleteLater()
#             self._asac_initializer = None
        
#     def activate_module(self):
#         """Active le module - OUVERTURE IMMÉDIATE, ASAC en arrière-plan"""
        
#         loader = self._ensure_loading_overlay()
#         if loader:
#             loader.show_loading("Chargement du module Automobile...", "Initialisation", simulate=True)
        
#         QApplication.processEvents()
        
#         current_user = self._get_current_user()
#         if not current_user:
#             self._hide_loader_and_show_error(loader, "Accès Refusé", "Veuillez vous connecter.")
#             return
        
#         content_stack = self._get_content_area()
#         if not content_stack:
#             self._hide_loader_and_show_error(loader, "Erreur", "Zone de contenu introuvable.")
#             return
        
#         if not self._view or not self._controller:
#             self._init_module_async(current_user, content_stack, loader)
#         else:
#             self._show_module(content_stack, loader)
            
#     def _init_module_async(self, current_user, content_stack, loader):
#         """Initialisation dans un thread - UI reste réactive"""
#         self._init_thread = ModuleInitThread(self.db_session, current_user)
#         self._init_thread.finished.connect(
#             lambda controller: self._on_module_initialized(controller, current_user, content_stack, loader)
#         )
#         self._init_thread.error.connect(lambda error: self._on_init_error(error, loader))
#         self._init_thread.progress.connect(lambda value, step: self._on_progress(loader, value, step))
#         self._init_thread.start()
        
#     def _on_progress(self, loader, value, step):
#         """Mise à jour progression"""
#         if loader:
#             loader.update_progress(value, step)
            
#     def _on_module_initialized(self, controller, current_user, content_stack, loader):
#         """Finalisation dans le thread principal"""
#         self._controller = controller
        
#         # Ajouter le service ASAC au contrôleur s'il est disponible
#         if hasattr(self._controller, 'asac_service'):
#             self._controller.asac_service = self._asac_service
        
#         self._view = VehicleMainView(controller=self._controller, user=current_user)
        
#         # Passer le service ASAC à la vue si disponible
#         if self._asac_service:
#             if hasattr(self._view, 'set_asac_service'):
#                 self._view.set_asac_service(self._asac_service)
#             elif hasattr(self._view, 'asac_service'):
#                 self._view.asac_service = self._asac_service
        
#         if content_stack.indexOf(self._view) == -1:
#             content_stack.addWidget(self._view)
        
#         content_stack.setCurrentWidget(self._view)
        
#         if loader:
#             loader.hide_loading()
        
#         if self._init_thread:
#             self._init_thread.deleteLater()
#             self._init_thread = None
            
#     def _show_module(self, content_stack, loader):
#         if content_stack.indexOf(self._view) == -1:
#             content_stack.addWidget(self._view)
#         content_stack.setCurrentWidget(self._view)
#         if loader:
#             loader.hide_loading()
            
#     def _hide_loader_and_show_error(self, loader, title, message):
#         if loader:
#             loader.hide_loading()
#         AlertManager.show_error(self.main_window, title, message)
        
#     def _on_init_error(self, error, loader):
#         if loader:
#             loader.hide_loading()
#         AlertManager.show_error(self.main_window, "Erreur d'initialisation", f"Erreur: {error}")
#         if self._init_thread:
#             self._init_thread.deleteLater()
#             self._init_thread = None
            
#     def _get_current_user(self):
#         return getattr(self.main_window, 'current_user', None)
        
#     def _get_content_area(self):
#         content_attrs = ['content_area', 'stacked_widget', 'main_stack', 'content_stack']
#         for attr in content_attrs:
#             content_area = getattr(self.main_window, attr, None)
#             if content_area:
#                 return content_area
#         return None
        
#     def _log_error(self, message):
#         print(f"[AutomobileModule] ERROR: {message}")
        
#     @property
#     def view(self):
#         return self._view
        
#     @property
#     def controller(self):
#         return self._controller
        
#     @property
#     def db_session(self):
#         return getattr(self.main_window, 'db_session', None)
        
#     def cleanup(self):
#         if self._init_thread and self._init_thread.isRunning():
#             self._init_thread.quit()
#             self._init_thread.wait(1000)
#             self._init_thread = None
#         if self._asac_initializer and self._asac_initializer.isRunning():
#             self._asac_initializer.quit()
#             self._asac_initializer.wait(1000)
#             self._asac_initializer = None
#         if self._controller and hasattr(self._controller, 'cleanup'):
#             self._controller.cleanup()
#         if self._view:
#             self._view.deleteLater()
#             self._view = None
#         if self._loading_overlay:
#             self._loading_overlay.deleteLater()
#             self._loading_overlay = None
#         self._controller = None
#         self._asac_service = None