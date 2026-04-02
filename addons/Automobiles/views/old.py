import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget, QHBoxLayout, QFrame, QLabel, QPushButton, QSizePolicy, QSpacerItem,  QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor
from core.database import SessionLocal, engine, Base, init_db
from core.alerts import AlertManager
from core.logger import logger
from core.loader import AddonLoader

# Imports des modules
from addons.Paramètres.views.setup_view import SetupView
from addons.Paramètres.controllers.setup_controller import SetupController
from addons.Paramètres.views.loggin_view import LoginView
from addons.Paramètres.controllers.login_controller import LoginController
from addons.Paramètres.models.models import User

from core.database import engine, Base
import addons.Automobiles.models as models

# Palette de couleurs moderne
class AppColors:
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    SECONDARY = "#64748b"
    BACKGROUND = "#f8fafc"
    SIDEBAR_BG = "#0f172a"
    SIDEBAR_HOVER = "#1e293b"
    CARD_BG = "#ffffff"
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#475569"
    BORDER = "#e2e8f0"

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
        border-radius: 12px;
        margin: 15px;
        padding: 12px;
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
"""


class AnimatedSidebar(QFrame):
    """Sidebar moderne avec animation et design premium"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("Sidebar")
        self.collapsed = False
        self.collapsed_width = 70
        self.expanded_width = 240
        self.setFixedWidth(self.expanded_width)

        # Animation
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)

        # Style global
        self.setStyleSheet("""
        #Sidebar {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b,
                stop:1 #0f172a
            );
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        """)

        # Ombre
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(3)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # =========================
        # 🍔 BURGER
        # =========================
        burger_frame = QFrame()
        burger_frame.setFixedHeight(60)

        burger_layout = QHBoxLayout(burger_frame)
        burger_layout.setContentsMargins(15, 0, 15, 0)

        self.burger_btn = QPushButton("☰")
        self.burger_btn.setFixedSize(36, 36)
        self.burger_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.burger_btn.setStyleSheet("""
        QPushButton {
            background: rgba(255,255,255,0.08);
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 18px;
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

        # =========================
        # 🚗 LOGO
        # =========================
        self.logo_label = QLabel("AMS AUTO")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logo_label.setStyleSheet("""
        color: white;
        font-size: 20px;
        font-weight: 700;
        padding: 18px;
        margin: 10px;
        background: rgba(255,255,255,0.04);
        border-radius: 14px;
        letter-spacing: 1px;
        """)

        layout.addWidget(self.logo_label)

        # =========================
        # SEPARATOR
        # =========================
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255,255,255,0.1); margin: 10px 15px;")
        layout.addWidget(sep)

        # =========================
        # MENU
        # =========================
        self.menu_container = QVBoxLayout()
        self.menu_container.setSpacing(6)
        self.menu_container.setContentsMargins(10, 10, 10, 10)
        self.menu_container.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.menu_widget = QWidget()
        self.menu_widget.setLayout(self.menu_container)
        layout.addWidget(self.menu_widget)

        layout.addStretch()

        # =========================
        # 👤 USER CARD
        # =========================
        self.user_card = QFrame()
        self.user_card.setObjectName("UserCard")

        self.user_card.setStyleSheet("""
        #UserCard {
            background: rgba(255,255,255,0.05);
            border-radius: 14px;
            margin: 10px;
            padding: 10px;
        }
        """)

        user_layout = QVBoxLayout(self.user_card)
        user_layout.setSpacing(5)

        self.user_avatar = QLabel("A")
        self.user_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.user_avatar.setStyleSheet("""
        font-size: 16px;
        font-weight: bold;
        color: white;
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #3b82f6,
            stop:1 #6366f1
        );
        border-radius: 20px;
        min-width: 40px;
        min-height: 40px;
        """)

        self.user_name = QLabel("Utilisateur")
        self.user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_name.setStyleSheet("color: white; font-weight: 600;")

        user_layout.addWidget(self.user_avatar)
        user_layout.addWidget(self.user_name)

        layout.addWidget(self.user_card)

        # =========================
        # 🚪 LOGOUT
        # =========================
        self.logout_btn = QPushButton("Déconnexion")

        self.logout_btn.setStyleSheet("""
        QPushButton {
            color: #f87171;
            background: transparent;
            border: none;
            padding: 12px;
            border-radius: 10px;
        }
        QPushButton:hover {
            background: rgba(248,113,113,0.1);
        }
        """)

        layout.addWidget(self.logout_btn)

    # =========================
    # 🎯 TOGGLE
    # =========================
    def toggle_sidebar(self):
        self.collapsed = not self.collapsed
        target_width = self.collapsed_width if self.collapsed else self.expanded_width

        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.start()

        # Logo switch
        if self.collapsed:
            self.logo_label.setText("🚗 AMS AUTO")
        else:
            self.logo_label.setText("🚗")
            self.logo_label.setStyleSheet("""font-size: 28px;""")

        # Menu text
        for i in range(self.menu_container.count()):
            item = self.menu_container.itemAt(i)
            if item and item.widget():
                btn = item.widget()
                if hasattr(btn, 'original_text'):
                    btn.setText(btn.icon_only if self.collapsed else btn.original_text)

        self.user_name.setVisible(not self.collapsed)

    # =========================
    # ➕ ADD BUTTON
    # =========================
    def add_menu_button(self, label, icon_char, widget=None):
        btn = QPushButton(f"{icon_char}  {label}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn.original_text = f"{icon_char}  {label}"
        btn.icon_only = icon_char
        btn.setCheckable(True)

        btn.setStyleSheet("""
        QPushButton {
            color: #cbd5f5;
            background: transparent;
            border: none;
            padding: 12px;
            text-align: left;
            border-radius: 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background: rgba(255,255,255,0.08);
            color: white;
        }
        QPushButton:checked {
            background: #3b82f6;
            color: white;
        }
        """)

        self.menu_container.addWidget(btn)
        return btn

    # =========================
    # 👤 USER INFO
    # =========================
    def set_user_info(self, username):
        self.user_name.setText(username)

        initials = username[0].upper() if username else "U"
        self.user_avatar.setText(initials)

class MainWindow(QMainWindow):
    logout_requested = Signal()
    
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("AMS AUTO PRO")
        self.resize(1280, 800)
        self.setMinimumSize(1000, 600)
        self.setStyleSheet(STYLE_SHEET)
        
        self.setup_ui()
        self.init_modules()
    
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
        self.header = QFrame()
        self.header.setObjectName("Header")
        self.header.setFixedHeight(70)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        
        self.page_title = QLabel("Tableau de Bord")
        self.page_title.setObjectName("PageTitle")
        
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()
        
        right_layout.addWidget(self.header)
        
        # Content area
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("ContentArea")
        right_layout.addWidget(self.content_area)
        
        self.main_layout.addWidget(self.right_container, 1)
        
        # Compatibilité avec les addons existants
        self.sidebar_layout = self.sidebar.menu_container
        
        # Déconnexion
        self.sidebar.logout_btn.clicked.connect(self.handle_logout)
        self.sidebar.set_user_info(self.user.username)
    
    def init_modules(self):
        """Charge tous les modules/addons"""
        self.db_session = SessionLocal()
        self.loader = AddonLoader()
        self.addons = self.loader.load_all(self)
    
    def add_menu_button(self, label, icon_char, widget):
        """Ajoute un bouton de menu (pour la compatibilité avec les addons)"""
        btn = self.sidebar.add_menu_button(label, icon_char, widget)
        btn.clicked.connect(lambda: self.set_content_widget(widget, label))
        
        if self.content_area.indexOf(widget) == -1:
            self.content_area.addWidget(widget)
    
    def set_content_widget(self, widget, title="Module"):
        """Change le widget affiché"""
        self.page_title.setText(title)
        
        if self.content_area.indexOf(widget) == -1:
            self.content_area.addWidget(widget)
        
        self.content_area.setCurrentWidget(widget)
        self.update_sidebar_style(widget)
    
    def update_sidebar_style(self, active_widget):
        """Met à jour le style du bouton actif"""
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
        logger.info("Déconnexion")
        self.logout_requested.emit()
        self.close()
    
    def closeEvent(self, event):
        """Fermeture"""
        if hasattr(self, 'db_session'):
            self.db_session.close()
        event.accept()


class AppController:
    """Contrôleur principal"""
    
    def __init__(self):
        init_db()
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        self.app.setStyle('Fusion')
        
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
        if hasattr(self, 'setup_view'):
            self.setup_view.close()
        
        self.login_view = LoginView()
        self.login_ctrl = LoginController(self.login_view)
        self.login_ctrl.login_success.connect(self.launch_main_app)
        self.login_view.show()
    
    def launch_main_app(self, user):
        if hasattr(self, 'login_view'):
            self.login_view.close()
        
        self.main_window = MainWindow(user)
        self.main_window.current_user = user
        self.main_window.show()


if __name__ == "__main__":
    try:
        init_db()
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Erreur DB: {e}")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    controller = AppController()
    sys.exit(app.exec())
