from core.base_module import BaseModule
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize
from core.alerts import AlertManager
import qtawesome as qta

from addons.testModule.views.view import TestmoduleMainView


class TestmoduleMainViewModule(BaseModule):
    """Module testModule — Pattern LOMETA standard."""

    def __init__(self, main_window=None, controller=None):
        super().__init__(main_window)
        self.controller = controller
        self.db_session = None
        self.current_user = None
        self.view = None
        self.btn = None
        self._is_loaded = False

    def setup(self):
        """Ajout du bouton dans la sidebar principale."""
        self.db_session = getattr(self.main_window, 'db_session', None)
        self.current_user = getattr(self.main_window, 'current_user', None)

        sidebar = getattr(self.main_window, 'sidebar', None)

        if sidebar and hasattr(sidebar, 'add_menu_button'):
            # ✅ Utiliser la méthode de la sidebar principale
            self.btn = sidebar.add_menu_button(
                "testModule",
                "fa5s.cube",
                self,
            )
            # Icône qtawesome cohérente avec la sidebar
            self.btn.setIcon(qta.icon('fa5s.cube', color='#cbd5f5'))
            self.btn.setIconSize(QSize(20, 20))

            # Connecter à activate_module
            try:
                self.btn.clicked.disconnect()
            except Exception:
                pass
            self.btn.clicked.connect(self.activate_module)
        else:
            # Fallback : bouton simple
            self.btn = QPushButton("  testModule")
            self.btn.setIcon(qta.icon('fa5s.cube', color='#546e7a'))
            self.btn.setIconSize(QSize(20, 20))
            self.btn.setCheckable(True)
            self.btn.setFixedHeight(50)
            self.btn.setCursor(Qt.PointingHandCursor)
            self.btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #546e7a;
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 15px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #f1f3f4;
                    color: #1a73e8;
                }
                QPushButton:checked {
                    background: #e8f0fe;
                    color: #1a73e8;
                    border-right: 3px solid #1a73e8;
                }
            """)
            self.btn.clicked.connect(self.activate_module)

            if hasattr(self.main_window, 'sidebar_layout'):
                self.main_window.sidebar_layout.addWidget(self.btn)

    def activate_module(self):
        """Active le module — la vue gère son propre LoadingPage."""
        # ✅ Si déjà chargé, afficher directement
        if self._is_loaded and self.view:
            self.main_window.set_content_widget(self.view, "testModule")
            if self.btn:
                self.btn.setChecked(True)
            return

        try:
            user = getattr(self.main_window, 'current_user', None)
            db_session = getattr(self.main_window, 'db_session', None)

            if not user:
                AlertManager.show_error(
                    self.main_window,
                    "Sécurité",
                    "Aucun utilisateur connecté détecté."
                )
                return

            self.current_user = user
            self.db_session = db_session

            # ✅ Créer la vue (rapide — les pages sont créées à la demande)
            self.view = TestmoduleMainView(controller=self.controller, user=self.current_user)
            self._is_loaded = True

            self.main_window.set_content_widget(self.view, "testModule")
            if self.btn:
                self.btn.setChecked(True)

        except Exception as e:
            import traceback
            traceback.print_exc()
            AlertManager.show_error(self.main_window, "Erreur", str(e))
