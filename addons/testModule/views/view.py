from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidgetItem, QStackedWidget, QListWidget, QFrame,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QColor
import qtawesome as qta

from addons.testModule.views.widgets.loading_page import LoadingPage


# ═══════════════════════════════════════════════════════════════════
# BOUTON SIDEBAR MODERNE (avec qtawesome)
# ═══════════════════════════════════════════════════════════════════

class ModernSidebarButton(QPushButton):
    """Bouton de navigation avec icône qtawesome."""

    def __init__(self, text: str, icon_name: str, is_active: bool = False):
        super().__init__()
        self.icon_name = icon_name
        self.button_text = text
        self.is_active = is_active
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(self._get_style())

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(12, 0, 16, 0)
        self.layout().setSpacing(10)

        self.icon_label = QLabel()
        self.update_icon()

        self.text_label = QLabel(self.button_text)
        self.text_label.setStyleSheet(
            "font-size: 13px; background: transparent; border: none;"
        )
        self.layout().addWidget(self.icon_label)
        self.layout().addWidget(self.text_label)
        self.layout().addStretch()
        self.update_style()

    def update_icon(self):
        color = "#1a73e8" if self.is_active else "#64748b"
        pix = qta.icon(self.icon_name, color=color).pixmap(18, 18)
        self.icon_label.setPixmap(pix)
        self.icon_label.setStyleSheet("background: transparent; border: none;")

    def _get_style(self):
        if self.is_active:
            return """
                QPushButton {
                    background-color: #eff6ff;
                    color: #1a73e8;
                    border: none;
                    border-left: 4px solid #1a73e8;
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                    text-align: left;
                    padding: 0;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #dbeafe;
                }
            """
        return """
            QPushButton {
                background-color: transparent;
                color: #475569;
                border: none;
                border-radius: 8px;
                text-align: left;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                color: #1a73e8;
            }
        """

    def update_style(self):
        self.setStyleSheet(self._get_style())
        self.update_icon()
        color = "#1a73e8" if self.is_active else "#475569"
        weight = "600" if self.is_active else "500"
        self.text_label.setStyleSheet(
            "font-size: 13px; color: " + color + "; background: transparent; "
            "border: none; font-weight: " + weight + ";"
        )

    def set_active(self, active: bool):
        self.is_active = active
        self.update_style()


# ═══════════════════════════════════════════════════════════════════
# VUE PRINCIPALE — Lazy Loading + LoadingPage
# ═══════════════════════════════════════════════════════════════════

class TestmoduleMainView(QWidget):
    """Vue principale du module testModule."""

    SIDEBAR_ITEMS = [
            ("Accueil", "home", "fa5s.home"),
            ("Éléments", "items", "fa5s.cube"),
            ("Rapports", "reports", "fa5s.chart-bar"),
            ("Paramètres", "settings", "fa5s.cog"),
    ]

    def __init__(self, controller=None, user=None):
        super().__init__()
        self.controller = controller
        self.user = user

        # Lazy loading
        self._page_factories = {}
        self.page_widgets = {}
        self.pages = []
        self._page_rows = {}
        self._page_history = []
        self._loading_page_id = None

        self.setObjectName("MainModuleWindow")
        self.setStyleSheet("background-color: #f8fafc;")

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setup_sidebar()
        self.setup_content_area()

        # Enregistrer les factories puis afficher la 1re page
        self._register_page_factories()
        if self.pages:
            self.sidebar.setCurrentRow(0)

    # ═══════════════════════════════════════════════════════════════
    # SIDEBAR
    # ═══════════════════════════════════════════════════════════════

    def setup_sidebar(self):
        self.sidebar_container = QFrame()
        self.sidebar_container.setFixedWidth(260)
        self.sidebar_container.setStyleSheet(
            "QFrame { background: white; border-right: 1px solid #e2e8f0; }"
        )

        sidebar_layout = QVBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            "stop:0 #1a73e8, stop:1 #1557b0); }"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(12)

        logo_icon = QLabel()
        logo_icon.setPixmap(
            qta.icon('fa5s.cube', color='white').pixmap(QSize(24, 24))
        )
        header_layout.addWidget(logo_icon)

        title = QLabel("testModule")
        title.setStyleSheet(
            "color: white; font-size: 16px; font-weight: 700; "
            "letter-spacing: 1px; background: transparent;"
        )
        header_layout.addWidget(title)
        header_layout.addStretch()
        sidebar_layout.addWidget(header)

        # Liste des pages
        self.sidebar = QListWidget()
        self.sidebar.setFocusPolicy(Qt.NoFocus)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                padding-top: 12px;
                outline: none;
            }
            QListWidget::item {
                background: transparent;
                border: none;
                padding: 0;
                margin: 2px 8px;
                height: 44px;
            }
            QListWidget::item:selected {
                background: transparent;
            }
            QListWidget::item:hover {
                background: transparent;
            }
        """)

        for label, page_id, icon_name in self.SIDEBAR_ITEMS:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, page_id)
            item.setSizeHint(QSize(0, 44))

            btn = ModernSidebarButton(label, icon_name, is_active=False)
            self.sidebar.addItem(item)
            self.sidebar.setItemWidget(item, btn)

        self.sidebar.currentRowChanged.connect(self.display_page)
        sidebar_layout.addWidget(self.sidebar, 1)

        # User info en bas
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet(
            "QFrame { background: #f8fafc; border-top: 1px solid #e2e8f0; }"
        )
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 10, 16, 10)
        footer_layout.setSpacing(10)

        avatar = QLabel()
        avatar.setFixedSize(38, 38)
        initials = "U"
        if self.user and hasattr(self.user, 'username'):
            initials = self.user.username[0].upper()
        avatar.setText(initials)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a73e8, stop:1 #6366f1);
                color: white;
                border-top-left-radius: 19px;
                border-top-right-radius: 19px;
                border-bottom-left-radius: 19px;
                border-bottom-right-radius: 19px;
                font-weight: 700;
                font-size: 14px;
            }
        """)
        footer_layout.addWidget(avatar)

        info = QVBoxLayout()
        info.setSpacing(2)
        name_lbl = QLabel(
            getattr(self.user, 'username', 'Utilisateur') if self.user else 'Utilisateur'
        )
        name_lbl.setStyleSheet("color: #1e293b; font-size: 13px; font-weight: 600;")
        info.addWidget(name_lbl)

        role_text = str(getattr(self.user, 'role', 'Membre')) if self.user else 'Membre'
        role_lbl = QLabel("● " + role_text)
        role_lbl.setStyleSheet("color: #10b981; font-size: 10px; font-weight: 600;")
        info.addWidget(role_lbl)
        footer_layout.addLayout(info)
        footer_layout.addStretch()
        sidebar_layout.addWidget(footer)

        self.layout.addWidget(self.sidebar_container)

    # ═══════════════════════════════════════════════════════════════
    # CONTENT AREA
    # ═══════════════════════════════════════════════════════════════

    def setup_content_area(self):
        self.content_container = QFrame()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(12)

        # LoadingPage
        self.loading_page = LoadingPage(message="Chargement...")

        # Stack
        self.container = QStackedWidget()
        self.container.setStyleSheet(
            "QStackedWidget { background: white; border-radius: 16px; "
            "border: 1px solid #e2e8f0; }"
        )
        self.container.addWidget(self.loading_page)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        self.content_layout.addWidget(self.container)
        self.layout.addWidget(self.content_container, 1)

    # ═══════════════════════════════════════════════════════════════
    # LAZY LOADING — Factories
    # ═══════════════════════════════════════════════════════════════

    def _register_page_factories(self):
        self._page_factories = {
            "home": lambda: self._make_home(),
            "items": lambda: self._make_items(),
            "reports": lambda: self._make_reports(),
            "settings": lambda: self._make_settings(),
        }

        self.pages = []
        self._page_rows = {}
        for label, page_id, icon_name in self.SIDEBAR_ITEMS:
            if page_id in self._page_factories:
                self._page_rows[page_id] = len(self.pages)
                self.pages.append(page_id)


    def _make_home(self):
        """Page : Accueil"""
        # TODO: remplacer par la vraie vue
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon("fa5s.home", color="#1a73e8").pixmap(64, 64))
        icon_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_lbl)

        title = QLabel("Accueil")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #1e293b;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Page prête à être développée")
        sub.setStyleSheet("font-size: 14px; color: #64748b;")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)

        return page


    def _make_items(self):
        """Page : Éléments"""
        # TODO: remplacer par la vraie vue
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon("fa5s.cube", color="#1a73e8").pixmap(64, 64))
        icon_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_lbl)

        title = QLabel("Éléments")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #1e293b;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Page prête à être développée")
        sub.setStyleSheet("font-size: 14px; color: #64748b;")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)

        return page


    def _make_reports(self):
        """Page : Rapports"""
        # TODO: remplacer par la vraie vue
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon("fa5s.chart-bar", color="#1a73e8").pixmap(64, 64))
        icon_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_lbl)

        title = QLabel("Rapports")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #1e293b;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Page prête à être développée")
        sub.setStyleSheet("font-size: 14px; color: #64748b;")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)

        return page


    def _make_settings(self):
        """Page : Paramètres"""
        # TODO: remplacer par la vraie vue
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon("fa5s.cog", color="#1a73e8").pixmap(64, 64))
        icon_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_lbl)

        title = QLabel("Paramètres")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #1e293b;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Page prête à être développée")
        sub.setStyleSheet("font-size: 14px; color: #64748b;")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)

        return page


    # ═══════════════════════════════════════════════════════════════
    # SWITCH PAGE — Lazy Loading + LoadingPage
    # ═══════════════════════════════════════════════════════════════

    def display_page(self, row):
        """Change de page avec lazy loading."""
        if not (0 <= row < len(self.pages)):
            return

        # Verrou anti double-clic
        if self._loading_page_id is not None:
            return

        page_id = self.pages[row]

        # Mettre à jour les boutons
        for i in range(self.sidebar.count()):
            widget = self.sidebar.itemWidget(self.sidebar.item(i))
            if isinstance(widget, ModernSidebarButton):
                widget.set_active(i == row)

        # Historique
        if not self._page_history or self._page_history[-1] != page_id:
            self._page_history.append(page_id)
            if len(self._page_history) > 20:
                self._page_history.pop(0)

        widget = self.page_widgets.get(page_id)

        # ─── CAS 1 : Première visite → LoadingPage + création ───
        if widget is None:
            loading_msgs = {
            "home": "Chargement de accueil...",
            "items": "Chargement de éléments...",
            "reports": "Chargement de rapports...",
            "settings": "Chargement de paramètres...",
            }

            self.loading_page.set_message(loading_msgs.get(page_id, "Chargement..."))
            self.loading_page.set_subtitle("Veuillez patienter quelques instants...")
            self.container.setCurrentWidget(self.loading_page)

            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()

            self._loading_page_id = page_id

            # Créer la page
            try:
                widget = self._page_factories[page_id]()
            except Exception as e:
                import traceback
                traceback.print_exc()
                error_widget = self._build_error_widget(page_id, str(e))
                self.container.addWidget(error_widget)
                self.container.setCurrentWidget(error_widget)
                self._loading_page_id = None
                return

            if widget is None:
                error_widget = self._build_error_widget(
                    page_id, "Widget non créé (import manquant ?)"
                )
                self.container.addWidget(error_widget)
                self.container.setCurrentWidget(error_widget)
                self._loading_page_id = None
                return

            # Charger les données
            self.loading_page.set_message("Chargement des données...")
            QApplication.processEvents()

            try:
                if hasattr(widget, 'refresh'):
                    widget.refresh()
                elif hasattr(widget, 'load_data'):
                    widget.load_data()
            except Exception as refresh_err:
                print("Erreur refresh " + str(page_id) + ": " + str(refresh_err))

            # Mise en cache + affichage
            self.page_widgets[page_id] = widget
            self.container.addWidget(widget)

            def do_switch(w=widget):
                self.container.setCurrentWidget(w)
                self._loading_page_id = None

            QTimer.singleShot(300, do_switch)

        # ─── CAS 2 : Déjà visitée → affichage direct + refresh ───
        else:
            self.container.setCurrentWidget(widget)
            if hasattr(widget, 'refresh'):
                try:
                    QTimer.singleShot(10, widget.refresh)
                except Exception:
                    pass

    def _build_error_widget(self, page_id, error):
        """Widget d'erreur stylisé."""
        w = QWidget()
        w.setStyleSheet("background: white;")
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        icon = QLabel()
        icon.setPixmap(
            qta.icon('fa5s.exclamation-triangle', color='#f59e0b').pixmap(64, 64)
        )
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("Impossible de charger '" + str(page_id) + "'")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1e293b;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        msg = QLabel(str(error))
        msg.setStyleSheet("color: #64748b; font-size: 13px;")
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        layout.addWidget(msg)

        return w
