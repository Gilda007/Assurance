# import sys
# from turtle import title
# from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget,QHBoxLayout, QFrame, QLabel, QPushButton
# from PySide6.QtCore import QTranslator, Qt, Signal
# from core.database import SessionLocal, engine, Base, init_db
# from core.alerts import AlertManager
# from core.logger import logger
# from core.loader import AddonLoader

# # Imports des modules
# from addons.Paramètres.views.setup_view import SetupView
# from addons.Paramètres.controllers.setup_controller import SetupController
# from addons.Paramètres.views.loggin_view import LoginView
# from addons.Paramètres.controllers.login_controller import LoginController
# from addons.Paramètres.models.models import User

# from core.database import engine, Base
# import addons.Automobiles.models as models


# # Palette de couleurs moderne
# COLOR_SIDEBAR = "#1e293b"      # Slate 900
# COLOR_SIDEBAR_HOVER = "#334155" # Slate 700
# COLOR_ACCENT = "#3b82f6"        # Blue 500
# COLOR_BACKGROUND = "#f8fafc"    # Slate 50

# # Palette de couleurs "Modern Slate"
# STYLE_SHEET = """
#     QMainWindow {
#         background-color: #F1F5F9;
#     }
    
#     #Sidebar {
#         background-color: #0F172A; /* Bleu très foncé presque noir */
#         border: none;
#         border-top-right-radius: 20px;
#         border-bottom-right-radius: 20px;
#     }

#     #ContentArea {
#         background-color: transparent;
#     }

#     #Header {
#         background-color: rgba(255, 255, 255, 0.8);
#         border-bottom: 1px solid #E2E8F0;
#         margin: 10px;
#         border-radius: 12px;
#     }

#     QPushButton#MenuBtn {
#         color: #94A3B8;
#         background-color: transparent;
#         border: none;
#         border-radius: 8px;
#         text-align: left;
#         padding: 12px 15px;
#         font-weight: 500;
#         margin: 2px 15px;
#     }

#     QPushButton#MenuBtn:hover {
#         background-color: #1E293B;
#         color: #F8FAFC;
#     }

#     QPushButton#MenuBtn[active="true"] {
#         background-color: #3B82F6; /* Bleu électrique */
#         color: white;
#     }

#     #UserCard {
#         background-color: #1E293B;
#         border-radius: 12px;
#         margin: 15px;
#         padding: 10px;
#     }
# """

# class MainWindow(QMainWindow):
#     logout_requested = Signal()
#     def __init__(self, user):
#         super().__init__()
#         self.user = user
#         self.setWindowTitle("AMS-AUTO PRO")
#         self.resize(1280, 800)
#         self.setStyleSheet(STYLE_SHEET)
        
#         self.setup_ui()
#         self.init_modules() # <--- Appel crucial ici

#     def setup_ui(self):
#         self.central_widget = QWidget()
#         self.setCentralWidget(self.central_widget)
#         self.layout_principal = QHBoxLayout(self.central_widget)
#         self.layout_principal.setContentsMargins(0, 0, 15, 15) # Marge à droite et en bas
#         self.layout_principal.setSpacing(10)

#         # --- SIDEBAR ---
#         # main.py

#         # 1. Création du cadre (Frame)
#         self.sidebar = QFrame()
#         self.sidebar.setObjectName("Sidebar")
#         self.sidebar.setFixedWidth(240)

#         # 2. Création du Layout INTERNE (C'est lui que le module cherche)
#         self.sidebar_layout = QVBoxLayout(self.sidebar) 
#         self.sidebar_layout.setAlignment(Qt.AlignTop)
#         self.sidebar_layout.setContentsMargins(10, 20, 10, 20)
#         self.sidebar_layout.setSpacing(10)

#         # 3. Logo ou Titre (Optionnel, au-dessus des boutons)
#         self.logo_label = QLabel("AMS AUTO 1.1")
#         self.logo_label.setStyleSheet("color: white; font-weight: bold; font-size: 18px; margin-bottom: 20px;")
#         self.sidebar_layout.addWidget(self.logo_label)

#         # Titre / Logo
#         label_app = QLabel("AMS AUTO 1.1")
#         label_app.setStyleSheet("color: white; font-size: 20px; font-weight: 800; margin-left: 25px; margin-bottom: 20px;")
#         self.sidebar_layout.addWidget(label_app)

#         # Conteneur des boutons
#         self.menu_container = QVBoxLayout()
#         self.menu_container.setSpacing(5)
#         self.sidebar_layout.addLayout(self.menu_container)
        
#         self.sidebar_layout.addStretch()

#         # Carte Utilisateur
#         self.user_card = QFrame()
#         self.user_card.setObjectName("UserCard")
#         user_layout = QHBoxLayout(self.user_card)
#         user_layout.addWidget(QLabel(f"👤"))
#         user_name = QLabel(self.user.username)
#         user_name.setStyleSheet("color: white; font-weight: bold;")
#         user_layout.addWidget(user_name)
#         self.sidebar_layout.addWidget(self.user_card)

#         # Bouton Déconnexion
#         self.btn_logout = QPushButton("🚪 Déconnexion")
#         self.btn_logout.setObjectName("MenuBtn") # On garde le même style
#         self.btn_logout.setStyleSheet("QPushButton { color: #f87171; } QPushButton:hover { background-color: #450a0a; }")
#         self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        
#         # On ne passe pas par set_content_widget ici, on veut quitter !
#         self.btn_logout.clicked.connect(self.handle_logout)
        
#         self.sidebar_layout.addWidget(self.btn_logout)

#         # --- ZONE DE CONTENU (À DROITE) ---
#         self.right_container = QVBoxLayout()
#         self.right_container.setSpacing(10)

#         # Header stylé
#         self.header = QFrame()
#         self.header.setObjectName("Header")
#         self.header.setFixedHeight(70)
#         header_layout = QHBoxLayout(self.header)
#         header_layout.setContentsMargins(20, 0, 20, 0)

#         self.page_title = QLabel("Tableau de Bord")
#         self.page_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
#         header_layout.addWidget(self.page_title)
        
#         # Champ de recherche ou Status
#         search_hint = QLabel("Rechercher un véhicule... (Ctrl+F)")
#         search_hint.setStyleSheet("color: #94A3B8; background: #F1F5F9; padding: 8px 15px; border-radius: 8px;")
#         header_layout.addStretch()
#         header_layout.addWidget(search_hint)

#         # Zone d'affichage des modules
#         self.content_area = QStackedWidget()
#         self.content_area.setObjectName("ContentArea")
        
#         self.right_container.addWidget(self.header)
#         self.right_container.addWidget(self.content_area)

#         # Assemblage
#         self.layout_principal.addWidget(self.sidebar)
#         self.layout_principal.addLayout(self.right_container)

#         # Dans main.py -> classe MainWindow
    
#     def init_modules(self):
#         self.db_session = SessionLocal()
#         self.loader = AddonLoader()
#         # Le retour est maintenant une liste, donc plus d'erreur TypeError
#         self.addons = self.loader.load_all(self)
        
#     def add_menu_button(self, label, icon_char, widget):
#         """Crée un bouton dans la sidebar et connecte le widget."""
#         btn = QPushButton(f"{icon_char}  {label}")
#         btn.setObjectName("MenuBtn")
#         btn.setProperty("linked_widget", widget)
#         btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
#         # Action au clic
#         btn.clicked.connect(lambda: self.set_content_widget(widget, label))
        
#         # On ajoute le widget au StackedWidget s'il n'y est pas
#         if self.content_area.indexOf(widget) == -1:
#             self.content_area.addWidget(widget)
            
#         self.menu_container.addWidget(btn)

#     # Dans main.py, à l'intérieur de la classe MainWindow
#     def set_content_widget(self, widget, title="Module"):
#         """Change le widget affiché dans la zone de contenu et met à jour le titre."""
#         # On met à jour le texte du header
#         if hasattr(self, 'page_title'):
#             self.page_title.setText(title)
        
#         # On vérifie si le widget est déjà dans le Stack, sinon on l'ajoute
#         if self.content_area.indexOf(widget) == -1:
#             self.content_area.addWidget(widget)
        
#         # On affiche le widget demandé
#         self.content_area.setCurrentWidget(widget)
        
#         # On met à jour le style visuel des boutons pour montrer lequel est actif
#         self.update_sidebar_style(widget)

#     def update_sidebar_style(self, active_widget):
#         """Met en surbrillance le bouton correspondant au module actif."""
#         for i in range(self.menu_container.count()):
#             item = self.menu_container.itemAt(i)
#             btn = item.widget()
#             if isinstance(btn, QPushButton):
#                 # On compare le widget lié au bouton avec le widget actuellement affiché
#                 is_active = btn.property("linked_widget") == active_widget
#                 btn.setProperty("active", str(is_active).lower())
                
#                 # Force le rafraîchissement du style QSS
#                 btn.style().unpolish(btn)
#                 btn.style().polish(btn)

#     def handle_logout(self):
#         """Action déclenchée par le bouton Déconnexion."""
#         logger.info("Bouton déconnexion cliqué")
#         self.logout_requested.emit()
#         self.close()

#     def closeEvent(self, event):
#         """S'exécute à la fermeture de la fenêtre (clic sur X ou bouton Logout)."""
#         if hasattr(self, 'db_session'):
#             self.db_session.close()
#             logger.info("Session DB fermée proprement.")
        
#         # Optionnel : Si tu veux relancer le login automatiquement au logout
#         # il faudra appeler une méthode du AppController ici.
#         event.accept()


# class AppController:
#     """Gère l'aiguillage entre Setup, Login et MainWindow."""
#     def __init__(self):
#         init_db()
#         self.app = QApplication.instance()
#         if not self.app:
#             self.app = QApplication(sys.argv)
        
#         # 1. Initialisation DB (Création des tables si inexistantes)
#         try:
#             print("Vérification des tables...")
#             Base.metadata.create_all(bind=engine)
#             print("Tables prêtes.")
#             logger.info("Vérification de la structure de la base de données...")
#         except Exception as e:
#             AlertManager.show_error(None, "Erreur DB", "L'accès à PostgreSQL a échoué.", e)
#             sys.exit(1)

#         # 2. Aiguillage automatique
#         if self.is_database_empty():
#             logger.info("Aucun utilisateur trouvé. Lancement de l'assistant de configuration.")
#             self.show_setup()
#         else:
#             logger.info("Utilisateurs détectés. Lancement de l'écran de connexion.")
#             self.show_login()

#     def is_database_empty(self):
#         """Vérifie si la table utilisateurs contient des données."""
#         db = SessionLocal()
#         # On compte le nombre d'entrées dans la table User
#         try:
#             # Maintenant 'User' est connu et ses relations (Vehicle, etc.) sont résolues
#             count = db.query(User).count()
#             return count == 0
#         finally:
#             db.close()

#     def show_setup(self):
#         self.setup_view = SetupView()
#         self.setup_ctrl = SetupController(self.setup_view)
        
#         # On connecte le signal du CONTROLLER au changement de vue
#         self.setup_ctrl.setup_finished.connect(self.show_login)
        
#         self.setup_view.show()

#     def show_login(self):
#         """Affiche l'écran de connexion."""
#         # Si on vient du Setup, on ferme la vue précédente
#         logger.info("[DEBUG] show_login a été appelé !")
#         if hasattr(self, 'setup_view'):
#             self.setup_view.close()

#         self.login_view = LoginView()
#         self.login_ctrl = LoginController(self.login_view)
#         # En cas de succès, on lance l'application principale
#         self.login_ctrl.login_success.connect(self.launch_main_app)
#         self.login_view.show()

#     # Dans main.py
#     def launch_main_app(self, user):
#         logger.info(f"Lancement de l'interface principale pour {user.username}")
        
#         if hasattr(self, 'login_view'):
#             self.login_view.close()
            
#         self.main_window = MainWindow(user) 
#         # AJOUTEZ CETTE LIGNE si elle n'y est pas :
#         self.main_window.current_user = user 
        
#         self.main_window.show()
    
# if __name__ == "__main__":
#     # 1. Initialisation de la base de données
#     try:
#         init_db()
#         Base.metadata.create_all(bind=engine)
#         logger.info("Base de données initialisée avec succès.")
#     except Exception as e:
#         logger.error(f"Erreur fatale DB : {e}")
#         sys.exit(1)

#     # 2. Lancement du contrôleur d'application
#     app = QApplication(sys.argv)
#     controller = AppController()
#     sys.exit(app.exec())

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget, QHBoxLayout, QFrame, QLabel, QPushButton, QSizePolicy, QSpacerItem
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
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
    """Sidebar avec animation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.collapsed = False
        self.collapsed_width = 70
        self.expanded_width = 240
        self.setFixedWidth(self.expanded_width)
        
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Burger button
        burger_frame = QFrame()
        burger_frame.setFixedHeight(60)
        burger_layout = QHBoxLayout(burger_frame)
        burger_layout.setContentsMargins(15, 0, 15, 0)
        
        self.burger_btn = QPushButton("☰")
        self.burger_btn.setFixedSize(36, 36)
        self.burger_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.burger_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
            }
        """)
        self.burger_btn.clicked.connect(self.toggle_sidebar)
        
        burger_layout.addWidget(self.burger_btn)
        burger_layout.addStretch()
        layout.addWidget(burger_frame)
        
        # Logo
        self.logo_label = QLabel("AMS AUTO")
        self.logo_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 15px;
            margin: 5px 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
        """)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: rgba(255,255,255,0.1); max-height: 1px; margin: 10px 15px;")
        layout.addWidget(sep)
        
        # Menu container (pour la compatibilité avec les addons)
        self.menu_container = QVBoxLayout()
        self.menu_container.setSpacing(5)
        self.menu_container.setContentsMargins(10, 10, 10, 10)
        self.menu_container.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Ajouter un widget conteneur pour les boutons
        self.menu_widget = QWidget()
        self.menu_widget.setLayout(self.menu_container)
        layout.addWidget(self.menu_widget)
        
        layout.addStretch()
        
        # User card
        self.user_card = QFrame()
        self.user_card.setObjectName("UserCard")
        user_layout = QVBoxLayout(self.user_card)
        user_layout.setSpacing(5)
        
        self.user_avatar = QLabel("👤")
        self.user_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_avatar.setStyleSheet("font-size: 28px;")
        
        self.user_name = QLabel()
        self.user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.user_name.setStyleSheet("color: white; font-weight: 600;")
        
        user_layout.addWidget(self.user_avatar)
        user_layout.addWidget(self.user_name)
        layout.addWidget(self.user_card)
        
        # Déconnexion
        self.logout_btn = QPushButton("Déconnexion")
        self.logout_btn.setObjectName("MenuBtn")
        self.logout_btn.setStyleSheet("color: #f87171;")
        layout.addWidget(self.logout_btn)
    
    def toggle_sidebar(self):
        """Anime la sidebar"""
        self.collapsed = not self.collapsed
        target_width = self.collapsed_width if self.collapsed else self.expanded_width
        
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.start()
        
        # Cacher/afficher le texte du logo
        if self.collapsed:
            self.logo_label.setText("🚗")
            self.logo_label.setStyleSheet("""
                font-size: 24px;
                padding: 15px;
                margin: 5px 10px;
            """)
        else:
            self.logo_label.setText("AMS AUTO")
            self.logo_label.setStyleSheet("""
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                margin: 5px 10px;
                background: rgba(255,255,255,0.05);
                border-radius: 12px;
            """)
        
        # Cacher/afficher les textes des boutons
        for i in range(self.menu_container.count()):
            item = self.menu_container.itemAt(i)
            if item and item.widget():
                btn = item.widget()
                if isinstance(btn, QPushButton) and hasattr(btn, 'original_text'):
                    if self.collapsed:
                        btn.setText(btn.icon_only)
                    else:
                        btn.setText(btn.original_text)
        
        # Cacher/afficher le nom utilisateur
        self.user_name.setVisible(not self.collapsed)
    
    def add_menu_button(self, label, icon_char, widget):
        """Ajoute un bouton de menu"""
        btn = QPushButton(f"{icon_char}  {label}")
        btn.setObjectName("MenuBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.original_text = f"{icon_char}  {label}"
        btn.icon_only = icon_char
        btn.setProperty("linked_widget", widget)
        
        self.menu_container.addWidget(btn)
        return btn
    
    def set_user_info(self, username):
        """Définit le nom utilisateur"""
        self.user_name.setText(username)
        
        # Avatar basé sur les initiales
        initials = username[0].upper() if username else "U"
        self.user_avatar.setText(initials)
        self.user_avatar.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            background: {AppColors.PRIMARY};
            border-radius: 25px;
            padding: 10px;
            min-width: 40px;
            min-height: 40px;
        """)


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