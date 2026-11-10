import sys
import random
import numpy as np
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget, 
                               QHBoxLayout, QFrame, QLabel, QPushButton, QSizePolicy, 
                               QGraphicsDropShadowEffect, QStackedLayout, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QLineEdit, QProgressBar,
                               QStatusBar, QMenu, QMessageBox, QComboBox, QScrollArea,
                               QSplitter, QGraphicsOpacityEffect)
from PySide6.QtCore import QRectF, QObject, Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer, QSize, QPointF, QThread, QRect
from PySide6.QtGui import QFont, QColor, QKeySequence, QShortcut, QPainter, QPen, QPixmap, QPainterPath, QLinearGradient
from core.database import SessionLocal, engine, Base, init_db
from core.alerts import AlertManager
from core.logger import logger
from core.loader import AddonLoader
import platform
import os
import threading
import traceback
import signal
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import time
from pathlib import Path
from dotenv import load_dotenv


if "__compiled__" in globals():
    base_dir = Path(sys.argv[0]).resolve().parent
else:
    base_dir = Path(__file__).resolve().parent

load_dotenv(dotenv_path=base_dir / ".env")
# Imports pour les graphiques
try:
    import pyqtgraph as pg
    HAS_PYQTGRAPH = True
except ImportError:
    HAS_PYQTGRAPH = False
    print("Pour de meilleurs graphiques: pip install pyqtgraph")

# Imports des modules
from addons.Parametres.views.setup_view import SetupView
from addons.Parametres.controllers.setup_controller import SetupController
from addons.Parametres.views.loggin_view import LoginView
from addons.Parametres.controllers.login_controller import LoginController
from icons import ICONS, get_icon, get_icon_pixmap, COLORS, ThemeManager, ThemeType
from addons.Parametres.models.models import User
from update_manager import UpdateManager
from update_client import UpdateClient
from update_widget import UpdateWidget
from core.widgets.global_loader import get_global_loader
from core.local_db import cache
from module_detector import ModuleDetector

from core.certificate_mode import get_certificate_mode_detector, CertificateMode, is_dev_mode


# import addons.Automobiles.models as models


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Gestionnaire global d'exceptions"""
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.error(f"Exception non capturée: {error_msg}")
    
    # Afficher une boîte de dialogue d'erreur (optionnel)
    QMessageBox.critical(None, "Erreur", 
                         f"Une erreur inattendue s'est produite:\n{str(exc_value)}\n\n"
                         f"Consultez les logs pour plus de détails.")
    
    # Ne pas quitter immédiatement, laisser l'application gérer
    # sys.exit(1)


# Installer le gestionnaire


sys.excepthook = global_exception_handler


# Gestionnaire pour les signaux Unix (segmentation fault)


def signal_handler(signum, frame):
    logger.error(f"Signal reçu: {signum}")
    QMessageBox.critical(None, "Erreur système", 
                         "L'application a rencontré une erreur critique.\n"
                         "Veuillez redémarrer l'application.")


signal.signal(signal.SIGSEGV, signal_handler)


def db_operation_with_retry(max_retries=3, delay=1):
    """Décorateur pour les opérations DB avec réessai"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    last_error = e
                    if "server closed the connection" in str(e) or "connection was closed" in str(e):
                        logger.warning(f"Connexion DB perdue, tentative {attempt + 1}/{max_retries}")
                        time.sleep(delay)
                        # Forcer la recréation de la session
                        from core.database import SessionLocal
                        if args and hasattr(args[0], 'db_session'):
                            try:
                                args[0].db_session.close()
                            except:
                                pass
                            args[0].db_session = SessionLocal()
                    else:
                        raise
                except Exception as e:
                    raise
            raise last_error
        return wrapper
    return decorator


# main.py - Ajoutez cette fonction utilitaire


def safe_emit(signal, *args, **kwargs):
    """
    Émet un signal de manière sécurisée (évite les crashes si l'objet est supprimé)
    
    Utilisation:
        safe_emit(self.my_signal, value1, value2)
    """
    try:
        signal.emit(*args, **kwargs)
    except RuntimeError as e:
        if "wrapped C/C++ object has been deleted" in str(e):
            logger.warning(f"Signal émis vers un objet supprimé: {e}")
        else:
            logger.error(f"Erreur lors de l'émission du signal: {e}")
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'émission du signal: {e}")


def safe_call(func, *args, default=None, **kwargs):
    """
    Appelle une fonction de manière sécurisée (avec try/except)
    
    Utilisation:
        result = safe_call(self.update_ui, arg1, default=[])
    """
    try:
        return func(*args, **kwargs)
    except RuntimeError as e:
        if "wrapped C/C++ object has been deleted" in str(e):
            logger.warning(f"Appel à {func.__name__} sur un objet supprimé")
        else:
            logger.error(f"Erreur dans {func.__name__}: {e}")
        return default
    except Exception as e:
        logger.error(f"Erreur inattendue dans {func.__name__}: {e}")
        return default


# Décorateur pour sécuriser les méthodes Qt


def safe_slot(func):
    """Décorateur pour sécuriser les slots Qt"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            if "wrapped C/C++ object has been deleted" in str(e):
                logger.warning(f"Slot {func.__name__} appelé sur objet supprimé")
            else:
                logger.error(f"Erreur dans le slot {func.__name__}: {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue dans le slot {func.__name__}: {e}")
    return wrapper


class CertificateToast(QFrame):
    """Notification toast moderne pour les certificats - Support RSA 3.0.0"""
    
    def __init__(self, statuses, parent=None):
        super().__init__(parent)
        self.statuses = statuses
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Compter les statuts avec support des versions
        self.valid_count = 0
        self.expiring_count = 0
        self.expired_count = 0
        self.no_cert_count = 0
        self.rsa_count = 0
        self.hmac_count = 0
        
        for s in self.statuses:
            status = s.get('status')
            version = s.get('version', '2.0.0')
            
            if version.startswith('3.'):
                self.rsa_count += 1
            else:
                self.hmac_count += 1
            
            if status == 'valid':
                self.valid_count += 1
            elif status == 'expiring':
                self.expiring_count += 1
            elif status == 'expired':
                self.expired_count += 1
            else:
                self.no_cert_count += 1
        
        # Couleur principale
        if self.expired_count > 0:
            self.main_color = "#ef4444"  # Rouge
            self.icon = "❌"
        elif self.expiring_count > 0:
            self.main_color = "#f59e0b"  # Orange
            self.icon = "⚠️"
        elif self.no_cert_count > 0:
            self.main_color = "#f59e0b"  # Orange
            self.icon = "⚠️"
        else:
            self.main_color = "#10b981"  # Vert
            self.icon = "✅"
        
        # Widget principal
        self.container = QFrame()
        self.container.setObjectName("ToastContainer")
        self.container.setStyleSheet(f"""
            QFrame#ToastContainer {{
                background: #1e293b;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.1);
            }}
        """)
        
        # Ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # ========== EN-TÊTE ==========
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Icône
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"font-size: 24px; background: transparent;")
        header_layout.addWidget(icon_label)
        
        # Titre
        if self.expired_count > 0:
            title = f"⚠️ {self.expired_count} certificat(s) expiré(s)"
        elif self.expiring_count > 0:
            title = f"🔔 {self.expiring_count} certificat(s) vont expirer"
        elif self.no_cert_count > 0:
            title = f"⚠️ {self.no_cert_count} module(s) sans certificat"
        else:
            title = "✅ Tous les certificats sont valides"
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: white;
            font-size: 15px;
            font-weight: 700;
            background: transparent;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Bouton fermer
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                border: none;
                border-radius: 14px;
                color: #94a3b8;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
                color: white;
            }
        """)
        close_btn.clicked.connect(self.close_animation)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # ========== DÉTAILS ==========
        details_layout = QVBoxLayout()
        details_layout.setSpacing(6)
        
        # Résumé
        summary_parts = []
        if self.valid_count > 0:
            summary_parts.append(f"✅ {self.valid_count} valide(s)")
        if self.expiring_count > 0:
            summary_parts.append(f"⚠️ {self.expiring_count} bientôt expiré(s)")
        if self.expired_count > 0:
            summary_parts.append(f"❌ {self.expired_count} expiré(s)")
        if self.no_cert_count > 0:
            summary_parts.append(f"📭 {self.no_cert_count} sans certificat")
        
        summary_label = QLabel(" · ".join(summary_parts))
        summary_label.setStyleSheet("""
            color: #94a3b8;
            font-size: 12px;
            background: transparent;
        """)
        details_layout.addWidget(summary_label)

        dev_count = sum(1 for s in self.statuses if s.get('mode') == 'dev')
        prod_count = sum(1 for s in self.statuses if s.get('mode') == 'production')

        if dev_count > 0:
            dev_label = QLabel(f"🔧 {dev_count} certificat(s) de DÉVELOPPEMENT")
            dev_label.setStyleSheet("""
                color: #92400e;
                background: #fef3c7;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            """)
            details_layout.addWidget(dev_label)

        if prod_count > 0:
            prod_label = QLabel(f"🏭 {prod_count} certificat(s) de PRODUCTION")
            prod_label.setStyleSheet("""
                color: #166534;
                background: #dcfce7;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            """)
            details_layout.addWidget(prod_label)
                
        # ✅ Ajouter la version dans les détails
        if self.rsa_count > 0:
            version_text = f"🔐 RSA {self.rsa_count} module(s) certifié(s)"
            if self.hmac_count > 0:
                version_text += f" | HMAC {self.hmac_count} module(s)"
            version_label = QLabel(version_text)
            version_label.setStyleSheet("""
                color: #64748b;
                font-size: 11px;
                background: transparent;
            """)
            details_layout.addWidget(version_label)
        
        # ✅ Détails des modules avec les jours restants
        if self.expiring_count > 0 or self.expired_count > 0:
            detail_text = ""
            for status in self.statuses:
                status_type = status.get('status')
                if status_type in ['expiring', 'expired']:
                    name = status.get('module_name', 'Inconnu')
                    days = status.get('remaining_days', 0)
                    expiry = status.get('expiry_date', 'Date inconnue')
                    version = status.get('version', '2.0.0')
                    version_prefix = "🔐" if version.startswith('3.') else "🔑"
                    
                    if status_type == 'expired':
                        detail_text += f"   {version_prefix} ❌ {name} (expiré depuis {abs(days)} jours)\n"
                    else:
                        detail_text += f"   {version_prefix} ⚠️ {name} (expire dans {days} jours)\n"
            
            if detail_text:
                detail_label = QLabel(detail_text)
                detail_label.setStyleSheet("""
                    color: #cbd5e1;
                    font-size: 12px;
                    background: transparent;
                    padding: 6px 10px;
                    border-radius: 8px;
                    background: rgba(255,255,255,0.05);
                """)
                details_layout.addWidget(detail_label)
        
        layout.addLayout(details_layout)
        
        # ========== BOUTON ACTION ==========
        if self.expired_count > 0 or self.expiring_count > 0:
            action_btn = QPushButton("🔄 Contacter l'administrateur")
            action_btn.setCursor(Qt.PointingHandCursor)
            action_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.main_color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: {self.main_color}dd;
                }}
            """)
            action_btn.clicked.connect(self.on_action_clicked)
            layout.addWidget(action_btn)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)
        
        # Ajuster la taille
        self.setFixedSize(self.container.sizeHint())

    def setup_animation(self):
        """Configure l'animation d'entrée/sortie"""
        # Animation d'opacité
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # Animation d'entrée
        self.enter_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.enter_animation.setDuration(400)
        self.enter_animation.setStartValue(0)
        self.enter_animation.setEndValue(1)
        self.enter_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Animation de sortie
        self.exit_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.exit_animation.setDuration(300)
        self.exit_animation.setStartValue(1)
        self.exit_animation.setEndValue(0)
        self.exit_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.exit_animation.finished.connect(self.deleteLater)

    def show_toast(self):
        """Affiche la notification avec animation"""
        # Positionner en bas à droite
        parent = self.parent()
        if parent:
            self.move(
                parent.width() - self.width() - 30,
                parent.height() - self.height() - 30
            )
        
        self.show()
        self.raise_()
        self.enter_animation.start()
        
        # Auto-disparition après 10 secondes (sauf si expiré)
        if self.expired_count == 0:
            QTimer.singleShot(10000, self.close_animation)
    
    def close_animation(self):
        """Ferme la notification avec animation"""
        self.exit_animation.start()
    
    def on_action_clicked(self):
        """Gère le clic sur le bouton d'action"""
        
        # Ouvrir une boîte de dialogue avec les détails
        details = "\n".join([
            f"• {s.get('module_name')}: {s.get('status')} - {s.get('message', '')} ({s.get('version', '2.0.0')})"
            for s in self.statuses
            if s.get('status') in ['expiring', 'expired', 'error']
        ])
        
        QMessageBox.information(
            self,
            "📋 Détails des certificats",
            f"Statut des certificats :\n\n{details}\n\n"
            f"📅 Total : {len(self.statuses)} module(s)\n"
            f"✅ Valides : {self.valid_count}\n"
            f"⚠️ Bientôt expirés : {self.expiring_count}\n"
            f"❌ Expirés : {self.expired_count}\n"
            f"🔐 RSA : {self.rsa_count} module(s)\n"
            f"🔑 HMAC : {self.hmac_count} module(s)\n\n"
            f"Veuillez contacter l'administrateur pour renouveler les certificats."
        )
        self.close_animation()


class Watchdog(QThread):
    """Thread de surveillance pour redémarrer l'application en cas de plantage"""
    
    application_frozen = Signal()
    
    def __init__(self, main_window, check_interval=10, timeout_seconds=60):
        super().__init__()
        self.main_window = main_window
        self.check_interval = check_interval
        self.timeout_seconds = timeout_seconds
        self.last_heartbeat = time.time()
        self._is_running = True
    
    def heartbeat(self):
        """Appelé régulièrement par l'application pour signaler qu'elle fonctionne"""
        self.last_heartbeat = time.time()
    
    def run(self):
        while self._is_running:
            time.sleep(self.check_interval)
            if time.time() - self.last_heartbeat > self.timeout_seconds:
                logger.error(f"Watchdog: Application non responsive depuis {self.timeout_seconds}s")
                self.application_frozen.emit()
                self.restart_application()
                break
    
    def restart_application(self):
        """Redémarre l'application"""
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def stop(self):
        self._is_running = False


class CrashHandler:
    """Gestionnaire des crashes pour redémarrage automatique"""
    
    @staticmethod
    def setup_crash_reporting(app_name="LOMETA"):
        """Configure le rapport de crash"""
        import signal
        
        def crash_handler(signum, frame):
            logger.critical(f"💥 Crash détecté - Signal: {signum}")
            # Sauvegarder l'état avant de quitter
            CrashHandler.save_crash_report(signum)
            sys.exit(1)
        
        # Capturer les signaux de crash
        signal.signal(signal.SIGSEGV, crash_handler)
        signal.signal(signal.SIGABRT, crash_handler)
        signal.signal(signal.SIGFPE, crash_handler)
        signal.signal(signal.SIGILL, crash_handler)
    
    @staticmethod
    def save_crash_report(signum):
        """Sauvegarde un rapport de crash"""
        crash_dir = os.path.join(os.path.expanduser("~"), "Documents", "LOMETA", "crashes")
        os.makedirs(crash_dir, exist_ok=True)
        
        crash_file = os.path.join(crash_dir, f"crash_LOMETA{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        with open(crash_file, 'w') as f:
            f.write(f"Crash report - {datetime.now()}\n")
            f.write(f"Signal: {signum}\n")
            f.write(f"Python version: {sys.version}\n")
            f.write(f"Platform: {platform.platform()}\n")
        logger.info(f"📄 Rapport de crash sauvegardé: {crash_file}")


class SafeThread(QThread):
    """Thread sécurisé avec gestion des exceptions"""
    
    def __init__(self, target=None, args=(), kwargs=None):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.error_occurred = Signal(str)
    
    def run(self):
        try:
            if self.target:
                self.target(*self.args, **self.kwargs)
        except Exception as e:
            error_msg = f"Erreur dans le thread {self.__class__.__name__}: {str(e)}"
            logger.error(error_msg)
            traceback.print_exc()
            self.error_occurred.emit(error_msg)


# Palette de couleurs moderne


class AppColors:
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    PRIMARY_LIGHT = "#60a5fa"
    SECONDARY = "#64748b"
    BACKGROUND = "#f8fafc"
    SIDEBAR_BG = "#0f172a"
    SIDEBAR_HOVER = "#1e293b"
    CARD_BG = "#ffffff"
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#475569"
    BORDER = "#e2e8f0"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    INFO = "#3b82f6"
    
    # Couleurs pour les graphiques
    CHART_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4"]


# Style Sheet


STYLE_SHEET = f"""
    QMainWindow {{
        background-color: {AppColors.BACKGROUND};
    }}
    
    QFrame#Sidebar {{
        background: {AppColors.SIDEBAR_BG};
        border: none;
        border-radius: 20px;
        margin: 10px 0 10px 10px;
    }}

    QHBoxLayout#header_layout {{
        background: {AppColors.SIDEBAR_BG};
    
    }}
    
    QPushButton#MenuBtn {{
        color: #94a3b8;
        background-color: transparent;
        border: none;
        border-radius: 10px;
        text-align: left;
        padding: 10px 16px;
        font-weight: 500;
        margin: 2px 10px;
    }}
    
    QPushButton#MenuBtn:hover {{
        background-color: {AppColors.SIDEBAR_HOVER};
        color: white;
    }}
    
    QPushButton#MenuBtn[active="true"] {{
        background: {AppColors.PRIMARY};
        color: white;
    }}
    
    QFrame#UserCard {{
        background: rgba(255,255,255,0.05);
        border-radius: 14px;
        margin: 10px;
        padding: 10px;
    }}
    
    QFrame#Header {{
        background: {AppColors.CARD_BG};
        border: 1px solid {AppColors.BORDER};
        border-radius: 16px;
        margin: 10px 10px 0 0;
    }}
    
    QLabel#PageTitle {{
        font-size: 20px;
        font-weight: 700;
        color: {AppColors.TEXT_PRIMARY};
    }}
    
    QStackedWidget#ContentArea {{
        background: transparent;
        margin: 10px 10px 10px 0;
    }}
    
    QScrollBar:vertical {{
        background: {AppColors.BACKGROUND};
        width: 6px;
        border-radius: 3px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {AppColors.SECONDARY};
        border-radius: 3px;
    }}
    
    QLineEdit#SearchBar {{
        background: #f1f5f9;
        border: none;
        border-radius: 20px;
        padding: 8px 16px;
        min-width: 250px;
    }}
    
    QLineEdit#SearchBar:focus {{
        border: 1px solid {AppColors.PRIMARY};
        background: white;
    }}
    
    QProgressBar {{
        border: none;
        border-radius: 3px;
        background: #e2e8f0;
        height: 4px;
    }}
    
    QProgressBar::chunk {{
        background: {AppColors.PRIMARY};
        border-radius: 3px;
    }}
    
    QTableWidget {{
        background: {AppColors.CARD_BG};
        border: 1px solid {AppColors.BORDER};
        border-radius: 12px;
        gridline-color: {AppColors.BORDER};
    }}
    
    QTableWidget::item {{
        padding: 8px;
    }}
    
    QHeaderView::section {{
        background: {AppColors.BACKGROUND};
        border: none;
        border-bottom: 1px solid {AppColors.BORDER};
        padding: 10px;
        font-weight: 600;
        color: {AppColors.TEXT_PRIMARY};
    }}
    
    QComboBox {{
        background: {AppColors.CARD_BG};
        border: 1px solid {AppColors.BORDER};
        border-radius: 8px;
        padding: 4px 8px;
        font-size: 12px;
    }}
    
    QPushButton#HomeBtn {{
        background: {AppColors.PRIMARY};
        color: white;
        border: none;
        border-radius: 10px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 600;
    }}
    QPushButton#HomeBtn:hover {{
        background: {AppColors.PRIMARY_DARK};
    }}
"""


class UpdateChecker(QObject):
    modules_available = Signal(object)
    no_modules = Signal()
    server_error = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._threads = []

    def _track_thread(self, thread):
        thread.finished.connect(lambda: self._cleanup_thread(thread))
        self._threads.append(thread)

    def _cleanup_thread(self, thread):
        if thread in self._threads:
            self._threads.remove(thread)
            thread.deleteLater()

    def stop_all_threads(self):
        for thread in list(self._threads):
            if thread.isRunning():
                thread.wait(2000)
            self._threads.remove(thread)
            thread.deleteLater()

    def check(self, server_url="http://http://localhost/:8000"):
        def safe_check():
            try:
                client = UpdateClient(server_url=server_url)
                status_code, modules = client.get_available_modules()
                
                if status_code == 200 and modules:
                    self.modules_available.emit(modules)
                elif status_code == 200:
                    self.no_modules.emit()
                elif status_code == 404:
                    self.server_error.emit()
            except Exception as e:
                logger.error(f"Erreur dans UpdateChecker: {e}")
                traceback.print_exc()
        
        thread = SafeThread(target=safe_check)
        self._track_thread(thread)
        thread.start()


class ModuleChecker(QObject):
    modules_found = Signal(object)
    
    def __init__(self, session_token: str = None, parent=None):
        super().__init__(parent)
        self.session_token = session_token
        self._threads = []

    def _track_thread(self, thread):
        thread.finished.connect(lambda: self._cleanup_thread(thread))
        self._threads.append(thread)

    def _cleanup_thread(self, thread):
        if thread in self._threads:
            self._threads.remove(thread)
            thread.deleteLater()

    def stop_all_threads(self):
        for thread in list(self._threads):
            if thread.isRunning():
                thread.wait(2000)
            self._threads.remove(thread)
            thread.deleteLater()

    def check(self):
        def safe_check():
            try:
                print(f"🔍 Vérification des modules...")
                client = UpdateClient(server_url="http://http://localhost:5000.100.89/:8000", 
                                     session_token=self.session_token)
                code, modules = client.get_available_modules()
                
                if code == 200 and modules:
                    print(f"   ✅ {len(modules)} module(s) trouvé(s)")
                    self.modules_found.emit(modules)
            except Exception as e:
                logger.error(f"Erreur dans ModuleChecker: {e}")
                traceback.print_exc()
        
        thread = SafeThread(target=safe_check)
        self._track_thread(thread)
        thread.start()


class ModernChartWidget(QWidget):
    """Widget de graphique moderne avec pyqtgraph"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if HAS_PYQTGRAPH:
            # Graphique principal
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setBackground('w')
            self.plot_widget.setLabel('left', 'Montant (FCFA)')
            self.plot_widget.setLabel('bottom', 'Période')
            self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
            self.plot_widget.setMinimumHeight(300)
            
            # Légende
            self.plot_widget.addLegend()
            
            layout.addWidget(self.plot_widget)
        else:
            # Fallback si pyqtgraph n'est pas installé
            fallback = QLabel("📊 Graphique\nInstallez pyqtgraph pour des graphiques avancés")
            fallback.setAlignment(Qt.AlignCenter)
            fallback.setStyleSheet("background: white; border-radius: 12px; padding: 50px; color: #94a3b8;")
            layout.addWidget(fallback)
    
    def create_line_chart(self, data, labels, title="Évolution", x_label="Période", y_label="Valeur"):
        """Crée un graphique en ligne"""
        if not HAS_PYQTGRAPH:
            return
        
        self.plot_widget.clear()
        self.plot_widget.setTitle(title, size='14pt')
        self.plot_widget.setLabel('left', y_label)
        self.plot_widget.setLabel('bottom', x_label)
        
        x = list(range(len(data)))
        
        # Tracer la ligne
        pen = pg.mkPen(color=AppColors.CHART_COLORS[0], width=3)
        curve = self.plot_widget.plot(x, data, pen=pen, name=labels[0] if labels else "Série")
        
        # Ajouter des points
        scatter = pg.ScatterPlotItem(
            size=10,
            brush=pg.mkBrush(AppColors.CHART_COLORS[0]),
            pen=pg.mkPen('w', width=2)
        )
        spots = [{'pos': (i, val), 'data': i} for i, val in enumerate(data)]
        scatter.addPoints(spots)
        self.plot_widget.addItem(scatter)
        
        # Configurer l'axe X
        if len(labels) > 1:
            ticks = [(i, labels[i]) for i in range(len(labels))]
            ax = self.plot_widget.getAxis('bottom')
            ax.setTicks([ticks])
    
    def create_bar_chart(self, data, labels, title="Répartition", x_label="Catégories", y_label="Valeur"):
        """Crée un graphique à barres"""
        if not HAS_PYQTGRAPH:
            return
        
        self.plot_widget.clear()
        self.plot_widget.setTitle(title, size='14pt')
        self.plot_widget.setLabel('left', y_label)
        self.plot_widget.setLabel('bottom', x_label)
        
        # Créer les barres
        x = np.arange(len(data))
        bg = pg.BarGraphItem(x=x, height=data, width=0.6, brush=AppColors.CHART_COLORS[0])
        self.plot_widget.addItem(bg)
        
        # Configurer l'axe X
        if labels:
            ticks = [(i, labels[i]) for i in range(len(labels))]
            ax = self.plot_widget.getAxis('bottom')
            ax.setTicks([ticks])
    
    def create_pie_chart(self, data, labels, title="Répartition"):
        """Crée un graphique en secteurs (camembert)"""
        if not HAS_PYQTGRAPH:
            return
        
        self.plot_widget.clear()
        self.plot_widget.setTitle(title, size='14pt')
        
        # Calculer les angles
        total = sum(data)
        angles = [360 * d / total for d in data]
        
        # Créer un graphique en secteurs avec des couleurs différentes
        start_angle = 0
        for i, (value, label) in enumerate(zip(data, labels)):
            angle = 360 * value / total
            # Note: pyqtgraph n'a pas de camembert natif, on utilise un workaround
            # ou on peut utiliser matplotlib pour cela
            pass
    
    def clear(self):
        """Efface le graphique"""
        if HAS_PYQTGRAPH:
            self.plot_widget.clear()

# ═══════════════════════════════════════════════════════════════════
# DASHBOARD V2.0 - COCKPIT INTELLIGENT
# ═══════════════════════════════════════════════════════════════════

class SparklineWidget(QWidget):
    """Mini-graphique sparkline pour les cartes KPI"""
    
    def __init__(self, data=None, color="#3b82f6", parent=None):
        super().__init__(parent)
        self.data = data or [5, 8, 6, 9, 7, 10, 12, 11, 14, 13, 15, 18]
        self.color = color
        self.setFixedHeight(36)
        self.setMinimumWidth(80)
    
    def paintEvent(self, event):
        if not self.data or len(self.data) < 2:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        padding = 2
        
        min_val = min(self.data)
        max_val = max(self.data)
        val_range = max_val - min_val if max_val != min_val else 1
        
        step_x = (w - 2 * padding) / (len(self.data) - 1)
        
        # Construire le chemin
        
        path = QPainterPath()
        points = []
        for i, val in enumerate(self.data):
            x = padding + i * step_x
            y = h - padding - ((val - min_val) / val_range) * (h - 2 * padding)
            points.append(QPointF(x, y))
        
        path.moveTo(points[0])
        for p in points[1:]:
            path.lineTo(p)
        
        # Remplissage dégradé sous la courbe
        fill_path = QPainterPath(path)
        fill_path.lineTo(points[-1].x(), h)
        fill_path.lineTo(points[0].x(), h)
        fill_path.closeSubpath()
        
        gradient = QLinearGradient(0, 0, 0, h)
        c = QColor(self.color)
        gradient.setColorAt(0, QColor(c.red(), c.green(), c.blue(), 80))
        gradient.setColorAt(1, QColor(c.red(), c.green(), c.blue(), 0))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawPath(fill_path)
        
        # Ligne
        pen = QPen(QColor(self.color), 2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)


class DonutChartWidget(QWidget):
    """Vrai graphique donut dessiné avec QPainter"""
    
    def __init__(self, data=None, colors=None, center_text="", parent=None):
        super().__init__(parent)
        self.data = data or [70.1, 29.9]
        self.colors = colors or ["#1e40af", "#f59e0b"]
        self.center_text = center_text or "210"
        self.center_subtitle = "Total Clients"
        self.setMinimumSize(180, 180)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        size = min(w, h) - 20
        rect = self.rect()
        
        # Rectangle pour le donut
        donut_rect = QRectF(
            (w - size) / 2,
            (h - size) / 2 - 10,
            size,
            size
        )
        
        total = sum(self.data)
        start_angle = 90 * 16  # Commencer en haut
        
        for value, color in zip(self.data, self.colors):
            span = int(-(value / total) * 360 * 16)
            
            pen = QPen(QColor(color), size * 0.18)
            pen.setCapStyle(Qt.FlatCap)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            
            # Réduire le rectangle pour que le trait soit centré
            inner_rect = donut_rect.adjusted(
                size * 0.09, size * 0.09,
                -size * 0.09, -size * 0.09
            )
            painter.drawArc(inner_rect, start_angle, span)
            start_angle += span
        
        # Texte central
        painter.setPen(QColor("#1e293b"))
        font = QFont("Segoe UI", 16, QFont.Bold)
        painter.setFont(font)
        text_rect = QRect(0, int(h / 2) - 25, w, 30)
        painter.drawText(text_rect, Qt.AlignCenter, self.center_text)
        
        painter.setPen(QColor("#64748b"))
        font.setPointSize(8)
        font.setBold(False)
        painter.setFont(font)
        sub_rect = QRect(0, int(h / 2) + 5, w, 20)
        painter.drawText(sub_rect, Qt.AlignCenter, self.center_subtitle)


class AlertBanner(QFrame):
    """Bandeau d'alertes prioritaires"""
    
    dismissed = Signal()
    
    def __init__(self, alerts=None, parent=None):
        super().__init__(parent)
        self.alerts = alerts or []
        self.setup_ui()
    
    def setup_ui(self):
        if not self.alerts:
            self.hide()
            return
        
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #fef2f2, stop:1 #fee2e2);
                border: 1px solid #fecaca;
                border-left: 4px solid #ef4444;
                border-radius: 10px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icône d'alerte
        icon = QLabel("🚨")
        icon.setStyleSheet("font-size: 20px; background: transparent;")
        layout.addWidget(icon)
        
        # Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title = QLabel(f"{len(self.alerts)} action(s) requise(s) aujourd'hui")
        title.setStyleSheet("font-weight: 700; color: #991b1b; font-size: 13px; background: transparent;")
        
        message = QLabel(" • ".join(self.alerts[:3]))
        message.setStyleSheet("color: #7f1d1d; font-size: 12px; background: transparent;")
        message.setWordWrap(True)
        
        text_layout.addWidget(title)
        text_layout.addWidget(message)
        layout.addLayout(text_layout, 1)
        
        # Bouton "Voir tout"
        see_all = QPushButton("Voir tout →")
        see_all.setCursor(Qt.PointingHandCursor)
        see_all.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { background: #dc2626; }
        """)
        layout.addWidget(see_all)
        
        # Bouton fermer
        close = QPushButton("✕")
        close.setFixedSize(24, 24)
        close.setCursor(Qt.PointingHandCursor)
        close.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #991b1b;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover { color: #450a0a; }
        """)
        close.clicked.connect(lambda: self.dismissed.emit())
        layout.addWidget(close)


# ============================================================
# NOUVELLES CLASSES POUR LE CARROUSEL (DESIGN LANDING PAGE)
# ==========================================================
# ============================================================
# PAGE 1 : AutoAssure (Clair, Bleu)
# ============================================================

class PageAutoAssure(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.bg_pixmap = QPixmap("assets/hero_1.jpg")
        
        overlay = QWidget(self)
        overlay.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout(overlay)
        content_layout.setContentsMargins(60, 40, 40, 40)
        
        left = QVBoxLayout()
        left.setSpacing(20)
        
        badge = QLabel("✨ NOUVEAUTÉ: LA GESTION INTELLIGENTE DE PARC")
        badge.setStyleSheet(
            "background: rgba(255,255,255,0.1); color: #cbd5e1; "
            "border: 1px solid #475569; font-size: 11px; font-weight: 600; "
            "padding: 6px 12px; border-radius: 15px;"
        )
        badge.setFixedWidth(380)
        left.addWidget(badge)

        title = QLabel("L'intelligence au service\nde votre parc automobile\net de vos assurances.")
        title.setStyleSheet("font-size: 38px; font-weight: 800; color: #ffffff;")
        left.addWidget(title)

        subtitle = QLabel(
            "Gérez vos polices, suivez vos sinistres en temps réel, "
            "collaborez avec des experts et optimisez la performance "
            "de vos véhicules au quotidien."
        )
        subtitle.setStyleSheet(
            "font-size: 15px; color: #cbd5e1; "
            "background: rgba(0,0,0,0.5); padding: 10px; border-radius: 8px;"
        )
        subtitle.setWordWrap(True)
        left.addWidget(subtitle)

        # Features
        features_layout = QVBoxLayout()
        features_layout.setSpacing(5)
        features = [
            "✓ Synchronisation en temps réel avec les experts",
            "✓ Tableaux de bord personnalisables",
            "✓ Sécurité et conformité garanties",
        ]
        for feature in features:
            lbl = QLabel(feature)
            lbl.setStyleSheet(
                "font-size: 13px; color: #cbd5e1; "
                "background: rgba(0,0,0,0.4); padding: 4px 8px; border-radius: 4px;"
            )
            features_layout.addWidget(lbl)
        left.addLayout(features_layout)
        left.addSpacing(10)

        btn_layout = QHBoxLayout()
        btn1 = QPushButton("Demander une démo")
        btn1.setStyleSheet(
            "background: #2563eb; color: white; padding: 12px 24px; "
            "border-radius: 8px; font-weight: 600; border: none;"
        )
        btn2 = QPushButton("Découvrir nos solutions ▶")
        btn2.setStyleSheet(
            "background: transparent; color: #ffffff; padding: 12px 24px; "
            "border-radius: 8px; font-weight: 600; border: 2px solid #ffffff;"
        )
        btn_layout.addWidget(btn1)
        btn_layout.addWidget(btn2)
        btn_layout.addStretch()
        left.addLayout(btn_layout)

        stats = QLabel("⭐ Plus de 12 450 polices actives")
        stats.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #cbd5e1; "
            "background: rgba(0,0,0,0.5); padding: 5px 10px; "
            "border-radius: 5px; margin-top: 20px;"
        )
        left.addWidget(stats)
        left.addStretch()

        content_layout.addLayout(left, 1)
        content_layout.addStretch(1)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(overlay)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.bg_pixmap.isNull():
            scaled = self.bg_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

            # ✅ Dégradé sombre comme les autres pages (#0f172a)
            gradient = QLinearGradient(0, 0, self.width(), 0)
            gradient.setColorAt(0.0, QColor(15, 23, 42, 240))   # opaque à gauche
            gradient.setColorAt(0.6, QColor(15, 23, 42, 150))   # semi-transparent
            gradient.setColorAt(1.0, QColor(15, 23, 42, 0))     # transparent à droite
            painter.fillRect(self.rect(), gradient)
        painter.end()


# ============================================================
# PAGE 2 : DriveGuard (Sombre, Doré)
# ============================================================
class PageDriveGuard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.bg_pixmap = QPixmap("assets/hero_2.jpg")
        
        overlay = QWidget(self)
        overlay.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout(overlay)
        content_layout.setContentsMargins(60, 40, 40, 40)
        
        left = QVBoxLayout()
        left.setSpacing(20)
        
        badge = QLabel("✨ DIGITAL-FIRST COVERAGE")
        badge.setStyleSheet("background: rgba(255,255,255,0.1); color: #cbd5e1; border: 1px solid #475569; font-size: 11px; font-weight: 600; padding: 6px 12px; border-radius: 15px;")
        badge.setFixedWidth(220)
        left.addWidget(badge)

        title = QLabel("The Smarter Way to\nProtect Your Drive.")
        title.setStyleSheet("font-size: 42px; font-weight: 800; color: #fcd34d;")
        left.addWidget(title)

        subtitle = QLabel("Get back on the road faster with stress-free car insurance and seamless, digital claims management. File, track, and resolve in minutes—all from your phone.")
        subtitle.setStyleSheet("font-size: 15px; color: #cbd5e1; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 8px;")
        subtitle.setWordWrap(True)
        left.addWidget(subtitle)

        # ✅ NOUVEAU : Bloc de features
        features_layout = QVBoxLayout()
        features_layout.setSpacing(5)
        features = [
            "✓ Digital claims in under 5 minutes",
            "✓ 24/7 roadside assistance included",
            "✓ Real-time policy tracking",
        ]
        for feature in features:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #cbd5e1; background: rgba(0,0,0,0.4); padding: 4px 8px; border-radius: 4px;")
            features_layout.addWidget(lbl)
        left.addLayout(features_layout)
        left.addSpacing(10)

        btn_layout = QHBoxLayout()
        btn1 = QPushButton("Get a Free Quote →")
        btn1.setStyleSheet("background: #fcd34d; color: #0f172a; padding: 12px 24px; border-radius: 20px; font-weight: 700; border: none;")
        btn2 = QPushButton("File or Track a Claim")
        btn2.setStyleSheet("background: transparent; color: white; padding: 12px 24px; border-radius: 20px; font-weight: 600; border: 1px solid white;")
        btn_layout.addWidget(btn1); btn_layout.addWidget(btn2); btn_layout.addStretch()
        left.addLayout(btn_layout)

        stats = QLabel("⭐ 4.8/5 Rated by Drivers | 24/7 Rapid Claims Support")
        stats.setStyleSheet("font-size: 13px; font-weight: 600; color: #cbd5e1; background: rgba(0,0,0,0.5); padding: 5px 10px; border-radius: 5px; margin-top: 20px;")
        left.addWidget(stats)
        left.addStretch()

        content_layout.addLayout(left, 1)
        content_layout.addStretch(1)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(overlay)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.bg_pixmap.isNull():
            scaled = self.bg_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

            # Dégradé sombre
            gradient = QLinearGradient(0, 0, self.width(), 0)
            gradient.setColorAt(0.0, QColor(15, 23, 42, 240)) # Opaque à gauche (#0f172a)
            gradient.setColorAt(0.6, QColor(15, 23, 42, 150))
            gradient.setColorAt(1.0, QColor(15, 23, 42, 0))
            painter.fillRect(self.rect(), gradient)
        painter.end()


# ============================================================
# PAGE 3 : Nexus (Bleu Néon, Tech)
# ============================================================
class PageNexus(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.bg_pixmap = QPixmap("assets/hero_3.jpg")
        
        overlay = QWidget(self)
        overlay.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout(overlay)
        content_layout.setContentsMargins(60, 40, 40, 40)
        
        left = QVBoxLayout()
        left.setSpacing(20)
        
        badge = QLabel("● NEXT-GEN AUTO INSURANCE")
        badge.setStyleSheet("background: rgba(0,0,0,0.5); color: #2dd4bf; border: 1px solid #2dd4bf; font-size: 11px; font-weight: 600; padding: 6px 12px; border-radius: 15px;")
        badge.setFixedWidth(240)
        left.addWidget(badge)

        title = QLabel("The Future of Coverage.\nIntelligent & Instant.")
        title.setStyleSheet("font-size: 40px; font-weight: 800; color: #a78bfa;")
        left.addWidget(title)

        subtitle = QLabel("Protect your drive with 24/7 connected coverage and AI-driven claims management. Experience automated crash detection, real-time safety insights, and instant claims resolution.")
        subtitle.setStyleSheet("font-size: 15px; color: #94a3b8; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 8px;")
        subtitle.setWordWrap(True)
        left.addWidget(subtitle)

        # ✅ NOUVEAU : Bloc de features
        features_layout = QVBoxLayout()
        features_layout.setSpacing(5)
        features = [
            "✓ AI-powered instant claims",
            "✓ Automated crash detection",
            "✓ Telematics & safety insights",
        ]
        for feature in features:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #94a3b8; background: rgba(0,0,0,0.4); padding: 4px 8px; border-radius: 4px;")
            features_layout.addWidget(lbl)
        left.addLayout(features_layout)
        left.addSpacing(10)

        btn_layout = QHBoxLayout()
        btn1 = QPushButton("GET A QUOTE")
        btn1.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2dd4bf, stop:1 #a78bfa); color: #050b14; padding: 12px 24px; border-radius: 20px; font-weight: 800; border: none;")
        btn2 = QPushButton("FILE OR TRACK CLAIM")
        btn2.setStyleSheet("background: transparent; color: #2dd4bf; padding: 12px 24px; border-radius: 20px; font-weight: 700; border: 1px solid #2dd4bf;")
        btn_layout.addWidget(btn1); btn_layout.addWidget(btn2); btn_layout.addStretch()
        left.addLayout(btn_layout)

        stats = QLabel("⏱ INSTANT CLAIMS (Avg. 3-Minute Approval) | 📡 TELEMATICS ACTIVE")
        stats.setStyleSheet("font-size: 12px; font-weight: 600; color: #94a3b8; background: rgba(0,0,0,0.5); padding: 5px 10px; border-radius: 5px; margin-top: 20px;")
        left.addWidget(stats)
        left.addStretch()

        content_layout.addLayout(left, 1)
        content_layout.addStretch(1)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(overlay)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.bg_pixmap.isNull():
            scaled = self.bg_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

            # Dégradé sombre (bleu nuit)
            gradient = QLinearGradient(0, 0, self.width(), 0)
            gradient.setColorAt(0.0, QColor(5, 11, 20, 240)) # #050b14
            gradient.setColorAt(0.6, QColor(5, 11, 20, 150))
            gradient.setColorAt(1.0, QColor(5, 11, 20, 0))
            painter.fillRect(self.rect(), gradient)
        painter.end()


# ============================================================
# PAGE 4 : AutoAssure (Français, Orange)
# ============================================================
class PageAutoAssureOrange(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.bg_pixmap = QPixmap("assets/hero_4.jpg")
        
        overlay = QWidget(self)
        overlay.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout(overlay)
        content_layout.setContentsMargins(60, 40, 40, 40)
        
        left = QVBoxLayout()
        left.setSpacing(20)
        
        badge = QLabel("ASSURANCE AUTO")
        badge.setStyleSheet("background: rgba(51, 65, 85, 0.9); color: #cbd5e1; font-size: 11px; font-weight: 600; padding: 6px 12px; border-radius: 15px;")
        badge.setFixedWidth(150)
        left.addWidget(badge)

        title = QLabel("Un accrochage ?\nOn s'occupe de\ntout, sans stress.")
        title.setStyleSheet("font-size: 40px; font-weight: 800; color: #fb923c;")
        left.addWidget(title)

        subtitle = QLabel("Déclarez votre sinistre en 3 clics et laissez nos experts gérer. Reprenez la route l'esprit tranquille.")
        subtitle.setStyleSheet("font-size: 15px; color: #cbd5e1; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 8px;")
        subtitle.setWordWrap(True)
        left.addWidget(subtitle)

        # ✅ NOUVEAU : Bloc de features
        features_layout = QVBoxLayout()
        features_layout.setSpacing(5)
        features = [
            "✓ Déclaration de sinistre en 3 clics",
            "✓ Prise en charge par nos experts",
            "✓ Suivi en temps réel de votre dossier",
        ]
        for feature in features:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #cbd5e1; background: rgba(0,0,0,0.4); padding: 4px 8px; border-radius: 4px;")
            features_layout.addWidget(lbl)
        left.addLayout(features_layout)
        left.addSpacing(10)

        btn_layout = QHBoxLayout()
        btn1 = QPushButton("Déclarer un sinistre ↗")
        btn1.setStyleSheet("background: #fb923c; color: white; padding: 12px 24px; border-radius: 20px; font-weight: 700; border: none;")
        btn2 = QPushButton("Estimer mon assurance")
        btn2.setStyleSheet("background: transparent; color: white; padding: 12px 24px; border-radius: 20px; font-weight: 600; border: 1px solid white;")
        btn_layout.addWidget(btn1); btn_layout.addWidget(btn2); btn_layout.addStretch()
        left.addLayout(btn_layout)
        left.addStretch()

        content_layout.addLayout(left, 1)
        content_layout.addStretch(1)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(overlay)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.bg_pixmap.isNull():
            scaled = self.bg_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

            # Dégradé sombre
            gradient = QLinearGradient(0, 0, self.width(), 0)
            gradient.setColorAt(0.0, QColor(15, 23, 42, 240)) # #0f172a
            gradient.setColorAt(0.6, QColor(15, 23, 42, 150))
            gradient.setColorAt(1.0, QColor(15, 23, 42, 0))
            painter.fillRect(self.rect(), gradient)
        painter.end()


class HeroSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        
        self.stack.addWidget(PageAutoAssure())
        self.stack.addWidget(PageDriveGuard())
        self.stack.addWidget(PageNexus())
        self.stack.addWidget(PageAutoAssureOrange())
        
        self.main_layout.addWidget(self.stack)
        
        self.dots_layout = QHBoxLayout()
        self.dots_layout.setAlignment(Qt.AlignCenter)
        self.dots_layout.setSpacing(10)
        self.dots_layout.setContentsMargins(0, 10, 0, 10)
        
        self.dots = []
        for i in range(4):
            dot = QLabel()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet("background: #cbd5e1; border-radius: 5px;")
            self.dots.append(dot)
            self.dots_layout.addWidget(dot)
            
        self.main_layout.addLayout(self.dots_layout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_page)
        self.timer.start(5000)
        
        self.current_index = 0
        self.update_dots()

    def next_page(self):
        self.current_index = (self.current_index + 1) % self.stack.count()
        self.stack.setCurrentIndex(self.current_index)
        self.update_dots()

    def update_dots(self):
        for i, dot in enumerate(self.dots):
            if i == self.current_index:
                dot.setStyleSheet("background: #2563eb; border-radius: 5px;")
            else:
                dot.setStyleSheet("background: #cbd5e1; border-radius: 5px;")


class ModernDashboard(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.hero = HeroSection()
        main_layout.addWidget(self.hero)


class AnimatedSidebar(QFrame):
    """Sidebar moderne sans contours arrondis et sans espaces"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("Sidebar")
        self.collapsed = False
        self.collapsed_width = 70
        self.expanded_width = 240
        self.setFixedWidth(self.expanded_width)
        self.setMinimumHeight(0)
        
        # Initialiser la liste des boutons
        self.menu_buttons = []

        # Animation
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)

        # ✅ Style sans contours arrondis et sans marges
        self.setStyleSheet("""
            QFrame#Sidebar {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b,
                    stop:1 #0f172a
                );
                border: none;
                border-radius: 0px;
                margin: 0px;
                padding: 0px;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Burger button
        burger_frame = QFrame()
        burger_frame.setFixedHeight(60)
        burger_frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        burger_layout = QHBoxLayout(burger_frame)
        burger_layout.setContentsMargins(12, 0, 12, 0)

        # ✅ Utiliser get_icon pour le bouton burger
        self.burger_btn = QPushButton()
        self.burger_btn.setFixedSize(50, 50)
        self.burger_btn.setCursor(Qt.PointingHandCursor)
        self.burger_btn.setIcon(get_icon('menu', color='#94a3b8', size=20))
        self.burger_btn.setIconSize(QSize(20, 20))
        self.burger_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.08);
                border: none;
                border-radius: 8px;
                color: white;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.18);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.25);
            }
        """)

        self.burger_btn.clicked.connect(self.toggle_sidebar)

        burger_layout.addWidget(self.burger_btn)
        burger_layout.addStretch()
        layout.addWidget(burger_frame)

        # Logo
        self.logo_widget = QWidget()
        self.logo_widget.setStyleSheet("""
            background: rgba(255,255,255,0.04);
            border: none;
            border-radius: 0px;
        """)
        self.logo_layout = QHBoxLayout(self.logo_widget)
        self.logo_layout.setContentsMargins(12, 12, 12, 12)
        self.logo_layout.setSpacing(8)
        self.logo_layout.setAlignment(Qt.AlignCenter)
        
        # Icône voiture
        self.logo_icon = QLabel()
        self.logo_icon.setPixmap(get_icon_pixmap('car', color='white', size=24))
        
        # Texte LOMETA
        self.logo_text = QLabel("LOMETA")
        self.logo_text.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: 700;
            background: transparent;
            border: none;
            letter-spacing: 1px;
        """)
        
        self.logo_layout.addWidget(self.logo_icon)
        self.logo_layout.addWidget(self.logo_text)
        layout.addWidget(self.logo_widget)
        
        layout.addWidget(self.logo_widget)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("""
            background: rgba(255,255,255,0.1);
            margin: 0px 12px;
            border: none;
        """)
        layout.addWidget(sep)

        # Menu container
        self.menu_container = QVBoxLayout()
        self.menu_container.setSpacing(2)
        self.menu_container.setContentsMargins(8, 8, 8, 8)
        self.menu_container.setAlignment(Qt.AlignTop)

        self.menu_widget = QWidget()
        self.menu_widget.setStyleSheet("""
            background: transparent;
            border: none;
            margin: 0px;
            padding: 0px;
        """)
        self.menu_widget.setLayout(self.menu_container)
        layout.addWidget(self.menu_widget)

        layout.addStretch()

        # ========== USER CARD ==========
        self.user_card = QFrame()
        self.user_card.setObjectName("UserCard")
        self.user_card.setStyleSheet("""
            QFrame#UserCard {
                background: rgba(255,255,255,0.08);
                border-radius: 0px;
                margin: 0px;
                padding: 12px 16px;
                border: none;
                border-top: 1px solid rgba(255,255,255,0.08);
            }
        """)

        user_layout = QVBoxLayout(self.user_card)
        user_layout.setSpacing(8)
        user_layout.setContentsMargins(0, 0, 0, 0)

        # Avatar
        avatar_container = QWidget()
        avatar_container.setStyleSheet("background: transparent; border: none;")
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_layout.setSpacing(0)
        avatar_layout.setContentsMargins(0, 0, 0, 0)

        self.user_avatar = QLabel("A")
        self.user_avatar.setAlignment(Qt.AlignCenter)
        self.user_avatar.setFixedSize(48, 48)
        self.user_avatar.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #3b82f6,
                stop:1 #6366f1
            );
            border-radius: 24px;
            border: none;
        """)

        avatar_layout.addWidget(self.user_avatar)
        user_layout.addWidget(avatar_container, 0, Qt.AlignCenter)

        # Nom utilisateur
        self.user_name = QLabel("Jean Dupont")
        self.user_name.setAlignment(Qt.AlignCenter)
        self.user_name.setStyleSheet("""
            color: white;
            font-weight: 700;
            font-size: 14px;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        """)
        user_layout.addWidget(self.user_name)

        # Rôle
        self.user_role = QLabel("Administrateur")
        self.user_role.setAlignment(Qt.AlignCenter)
        self.user_role.setStyleSheet("""
            color: rgba(255,255,255,0.6);
            font-size: 11px;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        """)
        user_layout.addWidget(self.user_role)

        # Statut en ligne
        status_container = QWidget()
        status_container.setStyleSheet("background: transparent; border: none;")
        status_layout = QHBoxLayout(status_container)
        status_layout.setAlignment(Qt.AlignCenter)
        status_layout.setSpacing(6)
        status_layout.setContentsMargins(0, 0, 0, 0)

        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(8, 8)
        self.status_indicator.setStyleSheet("background-color: #10b981; border-radius: 4px; border: none;")

        self.status_label = QLabel("En ligne")
        self.status_label.setStyleSheet("""
            color: rgba(255,255,255,0.7);
            font-size: 10px;
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        """)

        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)

        user_layout.addWidget(status_container)

        layout.addWidget(self.user_card)

        # Logout button
        self.logout_btn = QPushButton()
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setIcon(get_icon('logout', color='#fca5a5', size=50))
        self.logout_btn.setStyleSheet("""
            QPushButton {
                color: #fca5a5;
                background: rgba(239, 68, 68, 0.1);
                border: none;
                border-radius: 0px;
                padding: 12px 16px;
                font-size: 50px;
                font-weight: 600;
                text-align: center;
                margin: 0px;
                border-top: 1px solid rgba(255,255,255,0.05);
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.2);
                color: #fecaca;
                padding-left: 20px;
            }
            QPushButton:pressed {
                background: rgba(239, 68, 68, 0.3);
                padding-top: 13px;
                padding-bottom: 11px;
            }
        """)
        layout.addWidget(self.logout_btn)

    def toggle_sidebar(self):
        self.collapsed = not self.collapsed
        target_width = self.collapsed_width if self.collapsed else self.expanded_width

        # ✅ ANIMATION SUR LA LARGEUR FIXE
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.start()
        
        # ✅ Mettre à jour la largeur fixe APRÈS l'animation
        self.animation.finished.connect(lambda: self.setFixedWidth(target_width))

        # ✅ Logo switch - Version simplifiée sans suppression de widgets
        if self.collapsed:
            # Mode réduit : seulement l'icône voiture (plus grande)
            self.logo_icon.setPixmap(get_icon_pixmap('car', color='white', size=36))
            self.logo_icon.setVisible(True)
            self.logo_text.setVisible(False)
        else:
            # Mode étendu : LOMETA + icône voiture
            self.logo_icon.setPixmap(get_icon_pixmap('car', color='white', size=24))
            self.logo_icon.setVisible(True)
            self.logo_text.setVisible(True)

        # Menu text - ne garder que l'icône quand réduit
        for btn in self.menu_buttons:
            if hasattr(btn, 'original_text'):
                btn.setText(btn.icon_only if self.collapsed else btn.original_text)
                # ✅ Centrer l'icône quand réduit
                if self.collapsed:
                    btn.setStyleSheet("""
                        QPushButton#MenuBtn {
                            color: #cbd5f5;
                            background: transparent;
                            border: none;
                            border-radius: 0px;
                            padding: 10px 0px;
                            text-align: center;
                            font-size: 18px;
                            margin: 0px;
                        }
                        QPushButton#MenuBtn:hover {
                            background: rgba(255,255,255,0.08);
                            color: white;
                            border-left: 3px solid #3b82f6;
                            padding-left: 0px;
                        }
                        QPushButton#MenuBtn:checked {
                            background: #3b82f6;
                            color: white;
                            border-left: 3px solid #2563eb;
                            padding-left: 0px;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton#MenuBtn {
                            color: #cbd5f5;
                            background: transparent;
                            border: none;
                            border-radius: 0px;
                            padding: 10px 12px;
                            text-align: left;
                            font-size: 14px;
                            margin: 0px;
                        }
                        QPushButton#MenuBtn:hover {
                            background: rgba(255,255,255,0.08);
                            color: white;
                            border-left: 3px solid #3b82f6;
                            padding-left: 9px;
                        }
                        QPushButton#MenuBtn:checked {
                            background: #3b82f6;
                            color: white;
                            border-left: 3px solid #2563eb;
                            padding-left: 9px;
                        }
                    """)

        # Cacher/montrer les éléments quand réduit
        self.user_name.setVisible(not self.collapsed)
        self.user_role.setVisible(not self.collapsed)
        self.status_label.setVisible(not self.collapsed)
        
        # ✅ Réduire l'avatar quand la sidebar est réduite
        if self.collapsed:
            self.user_avatar.setFixedSize(36, 36)
            self.user_avatar.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: white;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3b82f6,
                    stop:1 #6366f1
                );
                border-radius: 18px;
                border: none;
            """)
        else:
            self.user_avatar.setFixedSize(48, 48)
            self.user_avatar.setStyleSheet("""
                font-size: 20px;
                font-weight: bold;
                color: white;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3b82f6,
                    stop:1 #6366f1
                );
                border-radius: 24px;
                border: none;
            """)

    def add_menu_button(self, label, icon_name, widget=None):
        """Ajoute un bouton de menu avec icône depuis le dossier icons"""
        
        btn = QPushButton()
        btn.setObjectName("MenuBtn")
        btn.setCursor(Qt.PointingHandCursor)
        
        # Stocker les informations pour le toggle
        btn._label = label
        btn._icon_name = icon_name
        
        # Définir l'icône
        btn.setIcon(get_icon(icon_name, color='#cbd5f5', size=20))
        btn.setIconSize(QSize(20, 20))
        
        # Texte selon l'état initial (étendu)
        btn.setText(f"  {label}")
        btn.setToolTip(label)
        
        # Stocker les versions textes pour le toggle
        btn.original_text = f"  {label}"
        btn.icon_only = ""  # Pas de texte quand réduit
        
        btn.setCheckable(True)
        btn.setProperty("linked_widget", widget)

        btn.setStyleSheet("""
            QPushButton#MenuBtn {
                color: #cbd5f5;
                background: transparent;
                border: none;
                border-radius: 0px;
                padding: 10px 12px;
                text-align: left;
                font-size: 14px;
                margin: 0px;
            }
            QPushButton#MenuBtn:hover {
                background: rgba(255,255,255,0.08);
                color: white;
                border-left: 3px solid #3b82f6;
                padding-left: 9px;
            }
            QPushButton#MenuBtn:checked {
                background: #3b82f6;
                color: white;
                border-left: 3px solid #2563eb;
                padding-left: 9px;
            }
        """)

        self.menu_container.addWidget(btn)
        self.menu_buttons.append(btn)
        return btn

    def set_active_module(self, active_widget):
        for btn in self.menu_buttons:
            is_active = btn.property("linked_widget") == active_widget
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def set_user_status(self, status="online"):
        """Définit le statut de l'utilisateur"""
        status_colors = {
            "online": "#10b981",
            "away": "#f59e0b",
            "busy": "#ef4444",
            "offline": "#64748b"
        }
        status_texts = {
            "online": "En ligne",
            "away": "Absent",
            "busy": "Occupé",
            "offline": "Hors ligne"
        }
        
        color = status_colors.get(status, "#10b981")
        text = status_texts.get(status, "En ligne")
        
        self.status_indicator.setStyleSheet(f"background-color: {color}; border-radius: 4px; border: none;")
        self.status_label.setText(text)

    def set_user_info(self, username, role="Utilisateur", email=""):
        """Définit les informations utilisateur"""
        self.user_name.setText(username)
        self.user_role.setText(role)
        
        # Avatar avec initiales
        initials = username[0].upper() if username else "U"
        self.user_avatar.setText(initials)
        
        if email:
            self.user_card.setToolTip(f"📧 {email}")

    def set_user_info(self, username):
        self.user_name.setText(username)
        initials = username[0].upper() if username else "U"
        self.user_avatar.setText(initials)


class MainWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self, user):
        super().__init__()
        self.user = user

        self.cert_mode = get_certificate_mode_detector().detect()
        self.is_dev = (self.cert_mode == CertificateMode.DEV)
        
        # ✅ Construire le titre AVANT de l'appliquer
        title = "LOMETA - Tableau de Bord"
        if is_dev_mode():
            title += "  [DEV]"
        self.setWindowTitle(title)
        
        self.resize(1280, 800)
        self.setMinimumSize(1400, 800)
        
        # ✅ Appliquer le thème actif AVANT de configurer l'UI
        # from icons.theme import theme_manager, ThemeType
        # self.theme_manager = theme_manager
        # self.current_theme = self.theme_manager.get_current_theme()
        # self.setStyleSheet(self.theme_manager.get_stylesheet())

        self.setup_ui()
        self.loader = get_global_loader()
        self.loader.setParent(self)
        
        # ✅ Initialisation du ModuleDetector AVANT tout
        self.module_detector = ModuleDetector()
        
        self.init_modules()
        QTimer.singleShot(1000, self.show_certificate_status_in_statusbar)
        cache_stats = cache.get_stats()
        print(f"📊 Cache local: {cache_stats.get('total_entries', 0)} entrées, {cache_stats.get('db_size_mb', 0)} MB")
        self.setup_shortcuts()
        self.check_environment()
        self.session_token = self._get_user_session_token()
        print(f"🔑 Token de session récupéré: {self.session_token is not None}")

        # ✅ Afficher les modules installés
        installed = self.module_detector.get_installed_modules()
        print(f"📦 {len(installed)} module(s) installé(s) détecté(s)")
        for mod_id, info in installed.items():
            print(f"   - {mod_id} v{info['version']}")

        # ✅ Connexion au changement de thème
        # self.theme_manager.theme_changed.connect(self.apply_theme)

        QTimer.singleShot(500, lambda: self._display_certificate_notification(self.loader.last_certificate_status))
        QTimer.singleShot(1000, self.update_notification_badge)
        
        # ✅ Initialisation du ModuleChecker avec le token
        self.module_checker = ModuleChecker(session_token=self.session_token)
        
        # ✅ Initialisation de l'UpdateManager avec le token
        self.update_manager = UpdateManager(self, session_token=self.session_token)
        
        # ✅ Connexion du signal
        self.module_checker.modules_found.connect(self.show_update_dialog, Qt.QueuedConnection)
        
        # ✅ Vérification différée
        QTimer.singleShot(2000, self.module_checker.check)

        # ============================================================
        # WATCHDOG
        # ============================================================
        self.watchdog = Watchdog(self, check_interval=10, timeout_seconds=60)
        self.watchdog.application_frozen.connect(self.on_application_frozen)
        self.watchdog.start()
        
        # Démarrer le heartbeat
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.update_heartbeat)
        self.heartbeat_timer.start(10000)
        
        # Premier heartbeat
        self.update_heartbeat()

    def update_heartbeat(self):
        """Met à jour le heartbeat du watchdog"""
        if hasattr(self, 'watchdog'):
            self.watchdog.heartbeat()

    def apply_theme(self, stylesheet: str):
        """
        Applique le stylesheet du thème à la fenêtre principale
        """
        self.setStyleSheet(stylesheet)
        
        # ✅ Mettre à jour le style de la sidebar si elle a des styles spécifiques
        if hasattr(self, 'sidebar'):
            # La sidebar utilise déjà le stylesheet global
            # Mais on peut ajouter des ajustements si nécessaire
            pass
        
        # ✅ Mettre à jour les autres composants si besoin
        # Les widgets enfants héritent automatiquement du stylesheet parent

    def toggle_theme(self):
        """
        Bascule entre les thèmes clair et sombre
        (à connecter à un bouton ou un raccourci)
        """
        self.theme_manager.toggle_theme()
        new_theme = self.theme_manager.get_current_theme()
        self.statusBar().showMessage(f"🎨 Thème {new_theme.value} activé", 2000)
    
    def manual_update_check(self):
        """Vérification manuelle des mises à jour"""
        # Afficher d'abord les modules installés
        installed = self.module_detector.get_installed_modules()
        installed_list = "\n".join([f"  • {info['name']} v{info['version']}" for info in installed.values()])
        
        if installed:
            self.statusBar().showMessage(f"📦 {len(installed)} module(s) installé(s) - Vérification des mises à jour...", 3000)
        
        self.update_manager.check_updates_manual()

    def on_application_frozen(self):
        """Appelé quand l'application est gelée"""
        logger.error("Application gelée - Sauvegarde des données...")
        # Sauvegarder l'état avant le redémarrage
        if hasattr(self, 'db_session'):
            try:
                self.db_session.commit()
            except:
                pass

    def _get_user_session_token(self):
        """Récupère le token de session de l'utilisateur connecté"""
        from core.database import SessionLocal
        from addons.Parametres.models.models import Session
        from datetime import datetime
        
        db = SessionLocal()
        try:
            # Chercher la session active de l'utilisateur
            session = db.query(Session).filter(
                Session.user_id == self.user.id,
                Session.expires_at > datetime.now()
            ).first()
            
            if session:
                print(f"✅ Session trouvée: {session.token_encrypted[:20]}... (expire le {session.expires_at})")
                return session.token_encrypted
            else:
                print("❌ Aucune session active trouvée")
                return None
        except Exception as e:
            print(f"Erreur récupération session: {e}")
            return None
        finally:
            db.close()
    
    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = AnimatedSidebar()
        self.main_layout.addWidget(self.sidebar)
        
        # Zone de contenu
        self.right_container = QWidget()
        right_layout = QVBoxLayout(self.right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Header
        self.setup_header()
        right_layout.addWidget(self.header)
        
        # Content area
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("ContentArea")
        right_layout.addWidget(self.content_area)
        
        self.main_layout.addWidget(self.right_container, 1)
        
        # Status bar
        self.setup_statusbar()
        
        # Dashboard par défaut
        self.dashboard = ModernDashboard(self.user)
        self.content_area.addWidget(self.dashboard)
        self.content_area.setCurrentWidget(self.dashboard)
        
        # Compatibilité avec les addons existants
        self.sidebar_layout = self.sidebar.menu_container
        
        # Déconnexion
        self.sidebar.logout_btn.clicked.connect(self.handle_logout)
        self.sidebar.set_user_info(self.user.username)
    
    # Dans main.py ou au début de l'application
    def check_environment(self):
        """Vérifie l'environnement et affiche les chemins"""
        from server.config import Config
        
        print("=" * 60)
        print("🔍 DIAGNOSTIC DE L'ENVIRONNEMENT")
        print("=" * 60)
        print(f"Mode compilé : {getattr(sys, 'frozen', True)}")
        print(f"Executable : {sys.executable}")
        print(f"Dossier exe : {Config.get_app_dir()}")
        print(f"Dossier addons : {Config.get_addons_dir()}")
        
        # Vérifier si _internal existe
        internal_dir = Config.get_internal_dir()
        print(f"Dossier _internal : {internal_dir}")
        print(f"_internal existe : {os.path.exists(internal_dir)}")
        
        # Vérifier le contenu de addons
        addons_dir = Config.get_addons_dir()
        if os.path.exists(addons_dir):
            print(f"\n📁 Contenu de addons :")
            for item in os.listdir(addons_dir):
                item_path = os.path.join(addons_dir, item)
                if os.path.isdir(item_path):
                    print(f"  📁 {item}/")
                    # Vérifier si manifest.json existe
                    manifest = os.path.join(item_path, 'manifest.json')
                    if os.path.exists(manifest):
                        print(f"     ✅ manifest.json présent")
                    else:
                        print(f"     ❌ manifest.json manquant")
                else:
                    print(f"  📄 {item}")
        else:
            print(f"\n❌ Dossier addons non trouvé !")
        
        print("=" * 60)

    def setup_header(self):
        
        self.header = QFrame()
        self.header.setObjectName("Header")
        self.header.setFixedHeight(60)
        self.header.setStyleSheet("""
            QFrame#Header {
                background: #1e293b;
                border: none;
                border-radius: 0px;
                margin: 0px;
                padding: 0px;
                border-bottom: 1px solid #1e293b;
            }
        """)
        
        header_layout = QHBoxLayout(self.header)
        header_layout
        header_layout.setContentsMargins(16, 0, 16, 0)
        header_layout.setSpacing(12)
        
        # ========== PARTIE GAUCHE ==========
        # Bouton Home
        self.home_btn = QPushButton()
        self.home_btn.setFixedSize(36, 36)
        self.home_btn.setCursor(Qt.PointingHandCursor)
        self.home_btn.setToolTip("Accueil (Ctrl+D)")
        self.home_btn.setIcon(get_icon('home', color='#cbd5e1', size=20))
        self.home_btn.setIconSize(QSize(20, 20))
        self.home_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background: #1e293b;
            }
        """)
        self.home_btn.clicked.connect(self.go_to_dashboard)
        header_layout.addWidget(self.home_btn)

        header_layout.addWidget(self.create_contextual_header())
        
        header_layout.addStretch()
        
        # ========== PARTIE CENTRALE ==========
        # Barre de recherche
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.setPlaceholderText("🔍 Rechercher un véhicule, client, contrat...")
        self.search_bar.setMinimumWidth(350)
        self.search_bar.setStyleSheet("""
            QLineEdit#SearchBar {
                background: #f1f5f9;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                margin: 0px;
            }
            QLineEdit#SearchBar:focus {
                background: white;
                border: 1px solid #3b82f6;
            }
        """)
        self.search_bar.returnPressed.connect(self.handle_search)
        header_layout.addWidget(self.search_bar)
        
        header_layout.addStretch()
        
        # ========== PARTIE DROITE ==========
        
        # Bouton de changement de thème
        self.theme_btn = QPushButton()
        self.theme_btn.setFixedSize(36, 36)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setToolTip("Changer de thème (Ctrl+T)")
        self.theme_btn.setIconSize(QSize(20, 20))
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background: #1e293b;
            }
        """)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        # Mettre à jour l'icône du thème
        # self.update_theme_button_icon()
        header_layout.addWidget(self.theme_btn)
        
        # Bouton notifications
        self.notif_btn = QPushButton()
        self.notif_btn.setFixedSize(36, 36)
        self.notif_btn.setCursor(Qt.PointingHandCursor)
        self.notif_btn.setToolTip("Notifications")
        self.notif_btn.setIcon(get_icon('bell', color='#cbd5e1', size=20))
        self.notif_btn.setIconSize(QSize(20, 20))
        self.notif_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background: #f1f5f9;
            }
        """)
        self.notif_btn.clicked.connect(self.show_notifications)
        header_layout.addWidget(self.notif_btn)

        # Bouton certificats
        self.certificate_btn = QPushButton()
        self.certificate_btn.setFixedSize(36, 36)
        self.certificate_btn.setCursor(Qt.PointingHandCursor)
        self.certificate_btn.setToolTip("Notifications des certificats")
        self.certificate_btn.setIcon(get_icon('certificate', color='#cbd5e1', size=20))
        self.certificate_btn.setIconSize(QSize(20, 20))
        self.certificate_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                margin: 0px;
                padding: 0px;
                position: relative;
            }
            QPushButton:hover {
                background: #1e293b;
            }
        """)
        self.certificate_btn.clicked.connect(self.show_certificate_notifications)
        header_layout.addWidget(self.certificate_btn)

        # Badge de notification
        self.notif_badge = QLabel()
        self.notif_badge.setFixedSize(20, 20)
        self.notif_badge.setAlignment(Qt.AlignCenter)
        self.notif_badge.setStyleSheet("""
            QLabel {
                background: #ef4444;
                color: white;
                border-radius: 10px;
                font-size: 10px;
                font-weight: 700;
                border: 2px solid white;
                margin: 0px;
                padding: 0px;
            }
        """)
        self.notif_badge.hide()
        
        # Positionner le badge sur le bouton
        self.notif_badge.setParent(self.notif_btn)
        self.notif_badge.move(22, -2)
        
        # Bouton aide
        self.help_btn = QPushButton()
        self.help_btn.setFixedSize(36, 36)
        self.help_btn.setCursor(Qt.PointingHandCursor)
        self.help_btn.setToolTip("Aide (F1)")
        self.help_btn.setIcon(get_icon('help', color='#cbd5e1', size=20))
        self.help_btn.setIconSize(QSize(20, 20))
        self.help_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background: #1e293b;
            }
        """)
        self.help_btn.clicked.connect(self.show_help)
        header_layout.addWidget(self.help_btn)
        
        # Bouton plein écran
        self.fullscreen_btn = QPushButton()
        self.fullscreen_btn.setFixedSize(36, 36)
        self.fullscreen_btn.setCursor(Qt.PointingHandCursor)
        self.fullscreen_btn.setToolTip("Plein écran (F11)")
        self.fullscreen_btn.setIcon(get_icon('fullscreen', color='#cbd5e1', size=20))
        self.fullscreen_btn.setIconSize(QSize(20, 20))
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background: #1e293b;
            }
        """)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        header_layout.addWidget(self.fullscreen_btn)
        
        # Avatar utilisateur
        self.user_avatar = QLabel()
        self.user_avatar.setFixedSize(36, 36)
        self.user_avatar.setAlignment(Qt.AlignCenter)
        self.user_avatar.setCursor(Qt.PointingHandCursor)
        self.user_avatar.setToolTip("Profil utilisateur")
        self.user_avatar.setStyleSheet("""
            QLabel {
                background: #3b82f6;
                color: white;
                font-weight: bold;
                border-radius: 18px;
                font-size: 14px;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        self.user_avatar.mousePressEvent = self.show_user_menu
        header_layout.addWidget(self.user_avatar)

    def setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {AppColors.SIDEBAR_HOVER};
                color: #f8fafc;
                border: none;
            }}
            QStatusBar::item {{
                border: none;
            }}
        """)
        self.setStatusBar(self.status_bar)
        
        # Horloge
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("color: #f8fafc; background: transparent;")
        self.update_clock()
        self.status_bar.addPermanentWidget(self.clock_label)
        
        # Timer pour l'horloge
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

        from core.certificate_mode import is_dev_mode
        if is_dev_mode():
            mode_badge = QLabel("  🔧 MODE DEV  ")
            mode_badge.setStyleSheet("""
                background: #fef3c7;
                color: #92400e;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 700;
            """)
            mode_badge.setToolTip(
                "Certificat de développement détecté.\n"
                "Les certificats expirent rapidement.\n"
                "NE PAS distribuer en production."
            )
            self.status_bar.addPermanentWidget(mode_badge)
    
    def update_clock(self):
        self.clock_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    def create_contextual_header(self):
        frame = QFrame()
        frame.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Salutation contextuelle
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Bonjour"
            emoji = "☀️"
        elif hour < 18:
            greeting = "Bon après-midi"
            emoji = "🌤️"
        else:
            greeting = "Bonsoir"
            emoji = "🌙"
        
        username = self.user.username if self.user else "Utilisateur"
        
        greeting_lbl = QLabel(f"{greeting}, {username} {emoji}")
        greeting_lbl.setStyleSheet("""
            font-size: 22px;
            font-weight: 800;
            color: #cbd5e1;
            background: transparent;
        """)
        layout.addWidget(greeting_lbl)
        
        layout.addStretch()
        
        # Badge "Système OK"
        # status_badge = QLabel("●  Système opérationnel")
        # status_badge.setStyleSheet("""
        #     background: #dcfce7;
        #     color: #166534;
        #     padding: 6px 14px;
        #     border-radius: 20px;
        #     font-size: 11px;
        #     font-weight: 600;
        # """)
        # layout.addWidget(status_badge)
        
        return frame

    def create_activity_timeline(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
                border: 1px solid #e2e8f0;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 12))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Header avec indicateur live
        header = QHBoxLayout()
        
        live = QLabel("● LIVE")
        live.setStyleSheet("""
            color: #ef4444;
            font-size: 10px;
            font-weight: 700;
        """)
        header.addWidget(live)
        
        layout.addLayout(self.timeline_layout)
        layout.addStretch()
        
        return card
    
    def refresh_stats(self):
        self._refresh_count += 1
        # Simuler une mise à jour de la timeline
        if hasattr(self, 'timeline_layout') and self.timeline_layout.count() > 0:
            # Ajouter une nouvelle activité en haut
            new_item = QHBoxLayout()
            new_item.setSpacing(8)
            
            d = QLabel("🟢")
            d.setStyleSheet("color: #10b981; font-size: 10px;")
            d.setFixedWidth(14)
            new_item.addWidget(d)
            
            t = QLabel("Mise à jour automatique")
            t.setStyleSheet("color: #1e293b; font-size: 11px; font-weight: 500;")
            new_item.addWidget(t, 1)
            
            tm = QLabel("à l'instant")
            tm.setStyleSheet("color: #94a3b8; font-size: 10px;")
            new_item.addWidget(tm)
            
            self.timeline_layout.insertLayout(0, new_item)
            
            # Limiter à 6 entrées
            while self.timeline_layout.count() > 6:
                item = self.timeline_layout.takeAt(self.timeline_layout.count() - 1)
                if item:
                    # Nettoyer le layout
                    while item.count():
                        child = item.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()

    def refresh_all(self):
        """Rafraîchit tout le dashboard"""
        self.refresh_stats()
        if hasattr(self, 'parent') and self.parent():
            # Notifier via statusbar si disponible
            pass

    def show_certificate_notifications(self):
        """Affiche le menu déroulant des notifications"""
        if not hasattr(self, '_last_certificate_statuses') or not self._last_certificate_statuses:
            QMessageBox.information(
                self,
                "🔔 Notifications",
                "✅ Tous les certificats sont valides.\n\nAucune notification à afficher."
            )
            return
        
        # Créer un menu personnalisé
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #1e293b;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 8px;
                min-width: 380px;
                max-width: 450px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 8px;
                color: #e2e8f0;
            }
            QMenu::item:selected {
                background: rgba(255,255,255,0.08);
            }
            QMenu::separator {
                height: 1px;
                background: rgba(255,255,255,0.1);
                margin: 4px 8px;
            }
        """)
        
        statuses = self._last_certificate_statuses
        
        # En-tête
        header_action = menu.addAction("📋 STATUT DES CERTIFICATS")
        header_action.setEnabled(False)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        header_action.setFont(font)
        
        menu.addSeparator()
        
        # Liste des statuts
        for status in statuses:
            name = status.get('module_name', 'Inconnu')
            status_type = status.get('status', 'unknown')
            
            if status_type == 'valid':
                icon = "✅"
                detail = "Valide"
                days = status.get('remaining_days', 0)
                if days > 0:
                    detail = f"Valide ({days} jours)"
            elif status_type == 'expiring':
                icon = "⚠️"
                days = status.get('remaining_days', 0)
                detail = f"Expire dans {days} jours"
            elif status_type == 'expired':
                icon = "❌"
                expiry = status.get('expiry_date', 'Date inconnue')
                detail = f"Expiré le {expiry}"
            else:
                icon = "📭"
                detail = status.get('message', 'Sans certificat')
            
            # ✅ Utiliser du HTML dans le texte pour la couleur
            action = menu.addAction(f'{icon} <b>{name}</b> — <span style="color:{self._get_color_for_status(status_type)};">{detail}</span>')
            action.setEnabled(False)
        
        menu.addSeparator()
        
        # Bouton "Tout voir"
        view_all = menu.addAction("🔍 Voir tous les détails")
        view_all.triggered.connect(self.show_certificate_details_dialog)
        
        # Afficher le menu
        menu.exec(self.certificate_btn.mapToGlobal(self.certificate_btn.rect().bottomLeft()))

    def show_certificate_details_dialog(self):
        """Affiche une boîte de dialogue détaillée des certificats"""
        if not hasattr(self, '_last_certificate_statuses'):
            QMessageBox.information(
                self,
                "Certificats",
                "Aucune information sur les certificats disponible."
            )
            return
        
        statuses = self._last_certificate_statuses
        
        if not statuses:
            QMessageBox.information(
                self,
                "Certificats",
                "Aucun certificat trouvé."
            )
            return
        
        # Compter les statuts
        valid = sum(1 for s in statuses if s.get('status') == 'valid')
        expiring = sum(1 for s in statuses if s.get('status') == 'expiring')
        expired = sum(1 for s in statuses if s.get('status') == 'expired')
        no_cert = sum(1 for s in statuses if s.get('status') == 'no_certificate')
        rsa_count = sum(1 for s in statuses if s.get('version', '').startswith('3.'))
        hmac_count = sum(1 for s in statuses if not s.get('version', '').startswith('3.'))
        
        # Construire le message détaillé
        details = []
        for status in statuses:
            name = status.get('module_name', 'Inconnu')
            status_type = status.get('status', 'unknown')
            version = status.get('version', '2.0.0')
            version_icon = "🔐" if version.startswith('3.') else "🔑"
            
            if status_type == 'valid':
                days = status.get('remaining_days', 0)
                detail = f"Valide (reste {days} jours)"
            elif status_type == 'expiring':
                days = status.get('remaining_days', 0)
                detail = f"Expire dans {days} jours"
            elif status_type == 'expired':
                expiry = status.get('expiry_date', 'Date inconnue')
                detail = f"Expiré le {expiry}"
            else:
                detail = status.get('message', 'Statut inconnu')
            
            details.append(f"{version_icon} {name} v{version} : {detail}")
        
        # Créer le message
        msg = (
            f"📋 RÉSUMÉ DES CERTIFICATS\n"
            f"{'─' * 40}\n\n"
            f"✅ Valides : {valid}\n"
            f"⚠️ Bientôt expirés : {expiring}\n"
            f"❌ Expirés : {expired}\n"
            f"📭 Sans certificat : {no_cert}\n"
            f"🔐 RSA : {rsa_count} module(s)\n"
            f"🔑 HMAC : {hmac_count} module(s)\n"
            f"\n{'─' * 40}\n\n"
            + "\n".join(details)
        )
        
        QMessageBox.information(
            self,
            "🔐 Certificats LOMETA",
            msg
        )

    def _get_color_for_status(self, status_type):
        """Retourne la couleur correspondant au statut"""
        colors = {
            'valid': '#10b981',      # Vert
            'expiring': '#f59e0b',   # Orange
            'expired': '#ef4444',    # Rouge
            'no_certificate': '#64748b',  # Gris
            'error': '#ef4444',      # Rouge
        }
        return colors.get(status_type, '#94a3b8')

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+F"), self, self.focus_search)
        QShortcut(QKeySequence("F5"), self, self.refresh)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+D"), self, self.go_to_dashboard)
    
    def focus_search(self):
        self.search_bar.setFocus()
        self.search_bar.selectAll()
    
    def refresh(self):
        self.status_bar.showMessage("Actualisation des données...", 2000)
        if hasattr(self, 'dashboard'):
            self.dashboard.update_stats()
    
    def create_menu(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        
        # Action Vérifier les mises à jour
        check_update_action = help_menu.addAction("&Vérifier les mises à jour")
        check_update_action.triggered.connect(self.manual_update_check)
        
        help_menu.addSeparator()
        
        about_action = help_menu.addAction("&À propos")
        about_action.triggered.connect(self.show_about)

    def _display_certificate_notification(self, statuses):
        """
        Affiche une notification moderne et animée des certificats.
        """
        if not statuses:
            return
        
        # ✅ Vérifier si la notification existe déjà
        if hasattr(self, '_certificate_toast') and self._certificate_toast is not None:
            try:
                self._certificate_toast.close_animation()
            except:
                pass
        
        # ✅ Compter les statuts pour un affichage rapide
        expired_count = sum(1 for s in statuses if s.get('status') == 'expired')
        expiring_count = sum(1 for s in statuses if s.get('status') == 'expiring')
        valid_count = sum(1 for s in statuses if s.get('status') == 'valid')
        no_cert_count = sum(1 for s in statuses if s.get('status') == 'no_certificate')
        
        # ✅ Si tout va bien, afficher un message discret dans la status bar
        if expired_count == 0 and expiring_count == 0 and no_cert_count == 0:
            self.status_bar.showMessage(f"✅ {valid_count} module(s) chargé(s) - Certificats valides", 5000)
            # Ne pas afficher de toast
            return
        
        # ✅ Créer et afficher la notification
        self._certificate_toast = CertificateToast(statuses, self)
        self._certificate_toast.show_toast()
        
        # ✅ Sauvegarder les statuts pour le bouton de notification
        self._last_certificate_statuses = statuses

    def check_updates_startup(self):
        """Vérifie les mises à jour au démarrage"""
        # Optionnel: vérifier silencieusement
        self.update_manager.check_updates_auto()
        
        # Afficher un message dans la barre d'état
        self.statusBar().showMessage("Vérification des mises à jour...", 2000)
    
    def manual_update_check(self):
        """Vérification manuelle des mises à jour"""
        self.update_manager.check_updates_manual()
    
    def show_status_message(self, message):
        """Affiche un message dans la barre d'état"""
        self.statusBar().showMessage(message, 5000)
    
    def show_about(self):
        """Affiche la boîte À propos"""
        QMessageBox.about(self, "À propos", 
                         "Mon Application v1.0.0\n\n"
                         "Application de gestion modulaire\n"
                         "© 2024 Votre Société")

    def update_notification_badge(self):
        """Met à jour le badge du bouton de notification"""
        if not hasattr(self, '_last_certificate_statuses'):
            self.notif_badge.hide()
            return
        
        statuses = self._last_certificate_statuses
        
        # Compter les notifications critiques
        expired = sum(1 for s in statuses if s.get('status') == 'expired')
        expiring = sum(1 for s in statuses if s.get('status') == 'expiring')
        
        total_alerts = expired + expiring
        
        if total_alerts > 0:
            self.notif_badge.setText(str(total_alerts) if total_alerts < 10 else "9+")
            self.notif_badge.show()
            # Changer la couleur si expiré
            if expired > 0:
                self.notif_badge.setStyleSheet("""
                    QLabel {
                        background: #ef4444;
                        color: white;
                        border-radius: 10px;
                        font-size: 10px;
                        font-weight: 700;
                    }
                """)
            else:
                self.notif_badge.setStyleSheet("""
                    QLabel {
                        background: #f59e0b;
                        color: white;
                        border-radius: 10px;
                        font-size: 10px;
                        font-weight: 700;
                    }
                """)
        else:
            self.notif_badge.hide()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def go_to_dashboard(self):
        """Retourne au tableau de bord"""
        if self.content_area.currentWidget() != self.dashboard:
            self.content_area.setCurrentWidget(self.dashboard)
            # self.page_title.setText("Tableau de Bord")
            self.sidebar.set_active_module(self.dashboard)
            self.status_bar.showMessage("Retour au tableau de bord", 2000)
    
    def handle_search(self):
        query = self.search_bar.text().strip()
        if query:
            self.status_bar.showMessage(f"Recherche de : {query}", 3000)
    
    def init_modules(self):
        """Charge tous les modules/addons - IDENTIQUE À old.py"""
        self.db_session = SessionLocal()
        self.loader = AddonLoader()
        self.addons = self.loader.load_all(self)
        if hasattr(self.loader, 'last_certificate_status'):
            statuses = self.loader.last_certificate_status
            if statuses:
                # ✅ Utiliser QTimer pour afficher après le démarrage complet
                QTimer.singleShot(500, lambda: self._display_certificate_notification(statuses))

    def show_certificate_status_in_statusbar(self):
        """
        Affiche un résumé des certificats dans la barre d'état.
        """
        if not hasattr(self.loader, 'last_certificate_status'):
            return
        
        statuses = self.loader.last_certificate_status
        
        valid = sum(1 for s in statuses if s.get('status') == 'valid')
        expiring = sum(1 for s in statuses if s.get('status') == 'expiring')
        expired = sum(1 for s in statuses if s.get('status') == 'expired')
        no_cert = sum(1 for s in statuses if s.get('status') == 'no_certificate')
        
        if expired > 0:
            self.statusBar().showMessage(
                f"❌ {expired} certificat(s) expiré(s) - Contactez l'administrateur",
                15000
            )
        elif expiring > 0:
            self.statusBar().showMessage(
                f"⚠️ {expiring} certificat(s) vont expirer - Renouvelez avant expiration",
                15000
            )
        elif no_cert > 0:
            self.statusBar().showMessage(
                f"⚠️ {no_cert} module(s) sans certificat",
                10000
            )
        else:
            self.statusBar().showMessage(
                f"✅ {valid} module(s) chargé(s) - Certificats valides",
                5000
            )
    
    def add_menu_button(self, label, icon_char, widget):
        """Ajoute un bouton de menu (pour la compatibilité avec les addons) - IDENTIQUE À old.py"""
        btn = self.sidebar.add_menu_button(label, icon_char, widget)
        btn.clicked.connect(lambda: self.set_content_widget(widget, label))
        
        if self.content_area.indexOf(widget) == -1:
            self.content_area.addWidget(widget)
    
    def set_content_widget(self, widget, title="Module"):
        """Change le widget affiché - IDENTIQUE À old.py"""
        if self.content_area.currentWidget() == widget:
            return
        
        # self.page_title.setText(title)
        
        if self.content_area.indexOf(widget) == -1:
            self.content_area.addWidget(widget)
        
        self.content_area.setCurrentWidget(widget)
        self.update_sidebar_style(widget)
    
    def update_sidebar_style(self, active_widget):
        """Met à jour le style du bouton actif - IDENTIQUE À old.py"""
        for i in range(self.sidebar.menu_container.count()):
            item = self.sidebar.menu_container.itemAt(i)
            if item and item.widget():
                btn = item.widget()
                if isinstance(btn, QPushButton):
                    is_active = btn.property("linked_widget") == active_widget
                    btn.setProperty("active", str(is_active).lower())
                    btn.style().unpolish(btn)
                    btn.style().polish(btn)
    
    def handle_logout(self):
        """Déconnexion"""
        reply = QMessageBox.question(
            self, "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            logger.info("Déconnexion")
            self.logout_requested.emit()
            self.close()
              
    def closeEvent(self, event):
        """Fermeture"""
        if hasattr(self, 'watchdog'):
            self.watchdog.stop()
            self.watchdog.quit()
            self.watchdog.wait(2000)
        if hasattr(self, 'heartbeat_timer'):
            self.heartbeat_timer.stop()
        if hasattr(self, 'module_checker'):
            self.module_checker.stop_all_threads()
        if hasattr(self, 'update_manager') and hasattr(self.update_manager, 'checker'):
            if self.update_manager.checker is not None:
                try:
                    self.update_manager.checker.wait(2000)
                except Exception:
                    pass
        if hasattr(self, 'db_session'):
            self.db_session.close()
        event.accept()

    def show_notifications(self):
        """Affiche le menu des notifications"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 8px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 8px;
            }
            QMenu::item:selected {
                background: #f1f5f9;
            }
        """)
        
        # Notifications
        menu.addAction("📄 Nouveau contrat signé")
        menu.addAction("💰 Paiement reçu de 250 000 FCFA")
        menu.addAction("⚠️ Contrat expirant dans 30 jours")
        menu.addSeparator()
        menu.addAction("🔔 Marquer tout comme lu")
        menu.addAction("⚙️ Paramètres")
        
        menu.exec(self.notif_btn.mapToGlobal(self.notif_btn.rect().bottomLeft()))

    def show_help(self):
        """Affiche l'aide"""
        QMessageBox.information(self, "Aide", """
        <h3>Raccourcis clavier</h3>
        <ul>
            <li><b>Ctrl+D</b> - Retour au tableau de bord</li>
            <li><b>Ctrl+F</b> - Recherche</li>
            <li><b>F5</b> - Rafraîchir</li>
            <li><b>F11</b> - Plein écran</li>
            <li><b>Ctrl+Q</b> - Quitter</li>
        </ul>
        """)

    def show_user_menu(self, event):
        """Affiche le menu utilisateur"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 8px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 8px;
            }
            QMenu::item:selected {
                background: #f1f5f9;
            }
        """)
        
        menu.addAction(f"👤 {self.user.username}")
        menu.addSeparator()
        menu.addAction("⚙️ Mon profil")
        menu.addAction("🔑 Changer mot de passe")
        menu.addSeparator()
        menu.addAction("🚪 Déconnexion", self.handle_logout)
        
        menu.exec(self.user_avatar.mapToGlobal(self.user_avatar.rect().bottomLeft()))

    def setup_shortcuts(self):
        """Configure les raccourcis clavier"""
        QShortcut(QKeySequence("Ctrl+F"), self, self.focus_search)
        QShortcut(QKeySequence("F5"), self, self.refresh)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+D"), self, self.go_to_dashboard)
        QShortcut(QKeySequence("F1"), self, self.show_help)

    def update_user_avatar(self):
        """Met à jour l'avatar utilisateur"""
        initials = self.user.username[0].upper() if self.user.username else "U"
        self.user_avatar.setText(initials)
 
    def check_for_modules(self):
        """Lance la vérification"""
        self.module_checker.check()
    
    def _filter_installed_modules(self, modules):
        """
        Filtre la liste des modules pour ne garder que ceux qui sont installés
        et qui ont une version plus récente.
        """
        if not modules:
            return []
        
        # Si modules est un dictionnaire, le convertir en liste
        if isinstance(modules, dict):
            modules = list(modules.values())
        
        if not isinstance(modules, list):
            return []
        
        filtered = []
        for module in modules:
            module_id = module.get('id')
            if not module_id:
                continue
            
            # Vérifier si le module est installé
            installed_version = self.module_detector.get_module_version(module_id)
            
            if installed_version is None:
                # Module non installé - ignorer
                print(f"⏭️ Module ignoré (non installé) : {module_id}")
                continue
            
            # Récupérer la version du serveur
            server_version = module.get('version', '0.0.0')
            
            # Comparer les versions
            if self._is_newer_version(server_version, installed_version):
                # Ajouter la version actuelle pour l'affichage
                module['current_version'] = installed_version
                filtered.append(module)
                print(f"📌 Mise à jour : {module_id} ({installed_version} → {server_version})")
            else:
                print(f"✅ Module déjà à jour : {module_id} ({installed_version})")
        
        return filtered

    def _show_certificate_status(self, modules):
        """
        Affiche le statut des certificats pour chaque module chargé.
        """
        if not modules:
            return
        
        # Récupérer les informations de validité depuis le loader
        if hasattr(self.loader, 'last_certificate_status'):
            statuses = self.loader.last_certificate_status
            if statuses:
                self._display_certificate_notification(statuses)
                return
        
        # Alternative : analyser les modules directement
        statuses = []
        for module in modules:
            if hasattr(module, 'certificate_info'):
                statuses.append(module.certificate_info)
        
        if statuses:
            self._display_certificate_notification(statuses)

    def _display_certificate_notification(self, statuses):
        """
        Affiche une notification moderne et animée des certificats.
        """
        if not statuses:
            return
        
        # ✅ Vérifier si la notification existe déjà
        if hasattr(self, '_certificate_toast') and self._certificate_toast is not None:
            try:
                self._certificate_toast.close_animation()
            except:
                pass
        
        # ✅ Créer et afficher la notification
        self._certificate_toast = CertificateToast(statuses, self)
        self._certificate_toast.show_toast()
        
        # ✅ Sauvegarder les statuts pour le bouton de notification
        self._last_certificate_statuses = statuses

    def show_update_dialog(self, modules):
        """
        Affiche le dialogue des modules disponibles.
        """
        print(f"📦 {len(modules)} module(s) disponible(s) sur le serveur")
        
        # Si modules est un dictionnaire, le convertir en liste
        if isinstance(modules, dict):
            modules = list(modules.values())
        
        if not modules:
            QMessageBox.information(self, "Mise à jour", "Aucun module disponible sur le serveur.")
            return
        
        # Récupérer la liste des modules installés
        installed_modules = self.module_detector.get_installed_modules()
        installed_ids = set(installed_modules.keys())
        print(f"📦 Modules installés détectés : {', '.join(installed_ids)}")
        
        # Filtrer : ne garder que les modules présents sur le serveur ET installés localement
        filtered_modules = []
        
        for module in modules:
            # ✅ Vérifier que module est bien un dictionnaire
            if not isinstance(module, dict):
                print(f"⚠️ Module ignoré (pas un dict) : {module}")
                continue
            
            module_id = module.get('id')
            if not module_id:
                print(f"⚠️ Module sans identifiant : {module}")
                continue
            
            print(f"🔍 Vérification du module serveur : {module_id}")
            
            # Vérifier si le module est installé
            if module_id in installed_ids:
                installed_version = installed_modules[module_id]['version']
                server_version = module.get('version', '0.0.0')
                
                # Ajouter la version actuelle
                module['current_version'] = installed_version
                module['is_installed'] = True
                
                # Vérifier si une mise à jour est disponible
                if self._is_newer_version(server_version, installed_version):
                    filtered_modules.append(module)
                    print(f"   📌 Mise à jour disponible : {module_id} ({installed_version} → {server_version})")
                else:
                    print(f"   ✅ Module déjà à jour : {module_id} ({installed_version})")
            else:
                print(f"   ⏭️ Module non installé : {module_id}")
        
        if not filtered_modules:
            QMessageBox.information(
                self, 
                "Mise à jour", 
                "✅ Tous vos modules sont à jour.\n\n"
                f"📦 {len(modules)} module(s) disponible(s) sur le serveur.\n"
                f"📦 {len(installed_ids)} module(s) installé(s) sur votre poste.\n\n"
                f"Aucun module installé ne nécessite de mise à jour."
            )
            return
        
        print(f"   ✅ {len(filtered_modules)} module(s) à mettre à jour")
        
        # ✅ CONSTRUIRE LE DICTIONNAIRE CORRECTEMENT
        # Chaque valeur doit être un dictionnaire avec les informations du module
        modules_dict = {}
        for module in filtered_modules:
            module_id = module.get('id')
            if module_id:
                modules_dict[module_id] = module
        
        # ✅ Vérifier que le dictionnaire est bien formé avant de l'envoyer
        print(f"📦 Modules à mettre à jour : {list(modules_dict.keys())}")
        
        dialog = UpdateWidget(modules_dict, self)
        dialog.exec()

    def _is_newer_version(self, server_version, local_version):
        """Compare deux versions sémantiques"""
        try:
            server_parts = [int(x) for x in str(server_version).split('.')]
            local_parts = [int(x) for x in str(local_version).split('.')]
            
            while len(server_parts) < 3:
                server_parts.append(0)
            while len(local_parts) < 3:
                local_parts.append(0)
            
            return server_parts > local_parts
        except (ValueError, AttributeError):
            return server_version != local_version


class AppController:
    """Contrôleur principal"""
    
    def __init__(self):
        init_db()
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        self.app.setStyle('Fusion')
        self.main_window = None
        self.login_view = None
        self.setup_view = None

        # ✅ Détecter le mode
        self.cert_mode_detector = get_certificate_mode_detector()
        self.cert_mode = self.cert_mode_detector.detect()
        
        # ✅ Log au démarrage
        logger.info(f"🔐 Mode de certification : {self.cert_mode.value}")
        logger.info(f"   Source : {self.cert_mode_detector.details.get('source')}")
        
        if self.cert_mode == CertificateMode.DEV:
            logger.warning("⚠️ MODE DÉVELOPPEMENT ACTIF — Ne pas utiliser en production")
        
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Base de données prête")
        except Exception as e:
            AlertManager.show_error(None, "Erreur DB", "L'accès à PostgreSQL a échoué.", e)
            sys.exit(1)
        
        if self.is_database_empty():
            self.show_setup()
        else:
            self.show_login()
    
    def is_database_empty(self):
        db = SessionLocal()
        try:
            return db.query(User).count() == 0
        finally:
            db.close()
    
    def show_setup(self):
        self.setup_view = SetupView()
        self.setup_ctrl = SetupController(self.setup_view)
        self.setup_ctrl.setup_finished.connect(self.show_login)
        self.setup_view.show()
    
    def show_login(self):
        if self.main_window is not None:
            self.main_window.close()
            self.main_window = None

        if self.setup_view is not None:
            self.setup_view.close()
            self.setup_view = None

        if self.login_view is not None:
            self.login_view.show()
            self.login_view.raise_()
            self.login_view.activateWindow()
            return
        
        self.login_view = LoginView()
        self.login_ctrl = LoginController(self.login_view)
        self.login_ctrl.login_success.connect(self.launch_main_app)
        self.login_view.show()
    
    def launch_main_app(self, user):
        if self.login_view is not None:
            self.login_view.close()
            self.login_view = None
        
        self.main_window = MainWindow(user)
        self.main_window.current_user = user
        self.main_window.logout_requested.connect(self.show_login, Qt.QueuedConnection)
        self.main_window.show()


if __name__ == "__main__":
    try:
        init_db()
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Erreur DB: {e}")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QToolTip {
            color: #000000;
            background-color: #eaf4fc;
            border: 1px solid #b8d8f0;
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 12px;
            font-weight: 500;
        }
    """)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    controller = AppController()
    sys.exit(app.exec())


