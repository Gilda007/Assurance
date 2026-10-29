# addons/Automobiles/main_ui.py - Version avec animation non bloquante

from PySide6.QtWidgets import QPushButton, QFrame, QVBoxLayout, QLabel, QProgressBar, QGraphicsDropShadowEffect, QApplication, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QThread, Signal, QEasingCurve, QMetaObject, Q_ARG, Slot, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QBrush
import math
import os
import json
from pathlib import Path
import qtawesome as qta

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
    
    # def __init__(self, parent=None, size=48):
    #     super().__init__(parent)
    #     self.setFixedSize(size, size)
    #     self._angle = 0
    #     self._timer = QTimer()
    #     self._timer.timeout.connect(self._rotate)
    #     self._timer.setInterval(16)  # 60 FPS
    #     self._animation_running = False
        
    #     self._colors = [
    #         QColor("#3b82f6"), QColor("#6366f1"), QColor("#8b5cf6"),
    #         QColor("#06b6d4"), QColor("#10b981"),
    #     ]
    #     self._current_color = 0
    def __init__(self, parent=None, size=48):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._angle = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._rotate)
        self._timer.setInterval(16)
        self._animation_running = False
        
        # ✅ Utiliser qtawesome pour l'icône
        self.icon = qta.icon('fa5s.spinner', color='#3b82f6')
        self.icon_pixmap = self.icon.pixmap(size-8, size-8)
        
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


from Custom_Widgets.QCustomLoadingIndicators import QCustom3CirclesLoader

class LoadingOverlay(QFrame):
    """Overlay de chargement ultra-simple"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.hide()
        
        # ✅ Layout simple comme dans test.py
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # ✅ Loader comme dans test.py
        self.loader = QCustom3CirclesLoader(color=QColor("#3b82f6"))
        layout.addWidget(self.loader, alignment=Qt.AlignCenter)
        
        # Label de message
        self.message_label = QLabel("Chargement...")
        self.message_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: 500;
            background: transparent;
            margin-top: 20px;
        """)
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: rgba(255,255,255,0.2);
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background: #3b82f6;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)
        
        # Pourcentage
        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet("""
            color: rgba(255,255,255,0.7);
            font-size: 12px;
            font-weight: 500;
            background: transparent;
        """)
        self.percentage_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.percentage_label)
        
        # Fond semi-transparent
        self.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.6);
            }
        """)
        
        # Animation de fondu
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(200)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
    def show_loading(self, message="Chargement...", title=None):
        """Affiche l'overlay"""
        self.message_label.setText(message)
        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")
        
        if self.parent():
            self.resize(self.parent().size())
        
        self.setWindowOpacity(0)
        self.show()
        self.raise_()
        
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.start()
        
    def update_progress(self, value, step=None):
        """Met à jour la progression"""
        self.progress_bar.setValue(value)
        self.percentage_label.setText(f"{value}%")
        if step:
            self.message_label.setText(step)
        QApplication.processEvents()
        
    def hide_loading(self):
        """Cache l'overlay"""
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
        super().resizeEvent(event)


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
        # ✅ Ajouter un flag pour éviter les chargements multiples
        self._is_loading = False
        self._is_loaded = False
        
    def setup(self):
        self._create_navigation_button()
        self._add_to_sidebar()
        
    def _create_navigation_button(self):
        """Crée le bouton de navigation en utilisant la méthode de la sidebar"""
        from icons import get_icon
        
        # Récupérer la sidebar
        sidebar = getattr(self.main_window, 'sidebar', None)
        if not sidebar:
            # Fallback: créer un bouton simple
            self._button = QPushButton()
            self._button.setIcon(get_icon('car', color='#f8fafc', size=18))
            self._button.setIconSize(QSize(18, 18))
            self._button.setText("  Automobile")
            self._button.setFixedHeight(self.BUTTON_HEIGHT)
            self._button.setCursor(Qt.PointingHandCursor)
            self._button.setStyleSheet(self.BUTTON_STYLE)
            self._button.clicked.connect(self.activate_module)
            return
        
        # Utiliser la méthode add_menu_button de la sidebar avec l'icône 'car'
        self._button = sidebar.add_menu_button("Automobile", "car", self)
        
        # Définir l'icône via get_icon
        self._button.setIcon(get_icon('car', color='#cbd5f5', size=18))
        self._button.setIconSize(QSize(18, 18))
        
        # Connecter le clic
        self._button.clicked.disconnect()
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
        """Active le module — la vue gère elle-même son LoadingPage."""
        if self._is_loaded and self._view:
            content_stack = self._get_content_area()
            if content_stack:
                content_stack.setCurrentWidget(self._view)
            return

        if self._is_loading:
            return

        self._is_loading = True

        current_user = self._get_current_user()
        if not current_user:
            AlertManager.show_error(self.main_window, "Accès Refusé", "Veuillez vous connecter.")
            self._is_loading = False
            return

        try:
            from addons.Automobiles.controllers import AutomobileMainController

            controller = AutomobileMainController(
                session=self.db_session,
                current_user_id=current_user.id
            )

            self._controller = controller
            self._view = VehicleMainView(controller=controller, user=current_user)

            content_stack = self._get_content_area()
            if content_stack.indexOf(self._view) == -1:
                content_stack.addWidget(self._view)
            content_stack.setCurrentWidget(self._view)

            self._is_loaded = True
            self._is_loading = False

        except Exception as e:
            self._is_loading = False
            import traceback
            traceback.print_exc()
            AlertManager.show_error(self.main_window, "Erreur", f"Erreur: {e}")

        
    def _on_progress(self, loader, value, step):
        """Mise à jour progression (thread-safe)"""
        if loader:
            loader.update_progress(value, step)
            
    def _on_module_initialized(self, controller, current_user, content_stack, loader):
        """Finalisation dans le thread principal"""
        self._controller = controller
        self._view = VehicleMainView(controller=self._controller, user=current_user)
        
        # ✅ Marquer comme chargé
        self._is_loaded = True
        self._is_loading = False
        
        if content_stack.indexOf(self._view) == -1:
            content_stack.addWidget(self._view)
        
        content_stack.setCurrentWidget(self._view)
        
        if loader:
            loader.hide_loading()
        
        # ✅ Attendre la fin du thread avant de le supprimer
        if self._init_thread:
            if self._init_thread.isRunning():
                self._init_thread.wait(500)
            self._init_thread.deleteLater()
            self._init_thread = None
            
    def _show_existing_view(self):
        """Affiche la vue déjà chargée"""
        content_stack = self._get_content_area()
        if content_stack and self._view:
            if content_stack.indexOf(self._view) == -1:
                content_stack.addWidget(self._view)
            content_stack.setCurrentWidget(self._view)
            
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
        """Gestion d'erreur d'initialisation"""
        # ✅ Réinitialiser l'état de chargement
        self._is_loading = False
        
        if loader:
            loader.hide_loading()
        AlertManager.show_error(self.main_window, "Erreur d'initialisation", f"Erreur: {error}")
        
        # ✅ Attendre la fin du thread avant de le supprimer
        if self._init_thread:
            if self._init_thread.isRunning():
                self._init_thread.wait(500)
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
        """Nettoie les ressources du module"""
        # ✅ Attendre la fin du thread avant de le supprimer
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
        self._is_loading = False
        self._is_loaded = False


class IconHelper:
    """Helper pour les icônes Font Awesome via qtawesome"""
    
    @staticmethod
    def get_icon(name, color="#2563eb", size=20, animation=None):
        """Récupère une icône Font Awesome"""
        icon = qta.icon(name, color=color)
        if animation:
            icon = qta.icon(name, color=color, animation=animation)
        return icon
    
    @staticmethod
    def get_pixmap(name, color="#2563eb", size=20, animation=None):
        """Récupère un pixmap d'icône Font Awesome"""
        icon = IconHelper.get_icon(name, color, animation)
        return icon.pixmap(size, size)