from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QScrollArea, 
                             QGridLayout, QGraphicsDropShadowEffect, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QCursor
from addons.Automobiles.security.access_control import Permissions, SecurityManager

class CompagnyListView(QWidget):
    def __init__(self, controller, current_user):
        super().__init__()
        self.controller = controller
        self.current_user = current_user
        self.setup_ui()

    def _add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        widget.setGraphicsEffect(shadow)

    def setup_ui(self):
        self.setStyleSheet("background-color: #f8fafc;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        # --- 1. EN-TÊTE & ACTIONS ---
        header_layout = QHBoxLayout()
        
        title_v = QVBoxLayout()
        title = QLabel("Annuaire des Contacts")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #0f172a;")
        subtitle = QLabel("Gérez vos clients, prospects et partenaires commerciaux.")
        subtitle.setStyleSheet("color: #64748b; font-size: 14px;")
        title_v.addWidget(title)
        title_v.addWidget(subtitle)
        
        actions_h = QHBoxLayout()
        self.btn_add = self._create_action_btn("➕ Nouveau Contact", "#2563eb", "white")
        self.btn_pdf = self._create_action_btn("📥 Export PDF", "#ffffff", "#1e293b", True)
        
        actions_h.addWidget(self.btn_pdf)
        actions_h.addWidget(self.btn_add)
        
        header_layout.addLayout(title_v)
        header_layout.addStretch()
        header_layout.addLayout(actions_h)
        self.main_layout.addLayout(header_layout)

        # --- 2. BARRE DE RECHERCHE ---
        search_frame = QFrame()
        search_frame.setFixedHeight(60)
        search_frame.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e2e8f0;")
        self._add_shadow(search_frame)
        
        search_layout = QHBoxLayout(search_frame)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un nom, un téléphone ou un type de contact...")
        self.search_input.setStyleSheet("border: none; font-size: 14px; color: #1e293b; background: transparent;")
        self.search_input.textChanged.connect(self.filter_contacts)
        
        search_layout.addWidget(QLabel("🔍"))
        search_layout.addWidget(self.search_input)
        self.main_layout.addWidget(search_frame)

        # --- 3. ZONE DE GRILLE (SCROLLABLE) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.container)
        self.main_layout.addWidget(self.scroll_area)

        # Initialisation des données
        self.refresh_contact_list()
        self.apply_security_policy()

    def _create_action_btn(self, text, bg, fg, border=False):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(42)
        border_css = "border: 1px solid #e2e8f0;" if border else "border: none;"
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg}; color: {fg}; {border_css}
                border-radius: 8px; font-weight: bold; padding: 0 20px;
            }}
            QPushButton:hover {{ background-color: {'#f1f5f9' if border else '#1d4ed8'}; }}
        """)
        return btn

    def refresh_contact_list(self):
        """Récupère et affiche les contacts sous forme de cartes"""
        # Nettoyage
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        contacts = self.controller.contacget_all_contacts()
        self.display_contacts(contacts)

    def display_contacts(self, contacts):
        columns = 3 # Nombre de cartes par ligne
        for i, contact in enumerate(contacts):
            card = self._create_contact_card(contact)
            self.grid_layout.addWidget(card, i // columns, i % columns)

    def _create_contact_card(self, contact):
        """Crée une carte individuelle élégante pour chaque contact"""
        card = QFrame()
        card.setFixedSize(300, 180)
        card.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #e2e8f0;")
        self._add_shadow(card)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        # En-tête de carte (Initiales + Nom)
        top = QHBoxLayout()
        initials = QLabel((contact.name[0] if contact.name else "?").upper())
        initials.setFixedSize(40, 40)
        initials.setAlignment(Qt.AlignCenter)
        initials.setStyleSheet("""
            background-color: #eff6ff; color: #2563eb; 
            border-radius: 20px; font-weight: 800; font-size: 14px;
        """)
        
        name_v = QVBoxLayout()
        name = QLabel(contact.name)
        name.setStyleSheet("font-weight: 700; color: #1e293b; font-size: 15px;")
        ctype = QLabel(contact.type_contact or "Client")
        ctype.setStyleSheet("color: #64748b; font-size: 11px; text-transform: uppercase; font-weight: 600;")
        name_v.addWidget(name)
        name_v.addWidget(ctype)
        
        top.addWidget(initials)
        top.addLayout(name_v)
        top.addStretch()
        layout.addLayout(top)
        
        layout.addSpacing(15)

        # Infos de contact
        phone = QLabel(f"📞 {contact.phone or 'N/A'}")
        phone.setStyleSheet("color: #475569; font-size: 13px;")
        email = QLabel(f"✉️ {contact.email or 'N/A'}")
        email.setStyleSheet("color: #475569; font-size: 13px;")
        
        layout.addWidget(phone)
        layout.addWidget(email)
        layout.addStretch()

        # Bouton Voir Détails
        btn_details = QPushButton("Voir le profil")
        btn_details.setCursor(Qt.PointingHandCursor)
        btn_details.setStyleSheet("""
            QPushButton { 
                background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; 
                border-radius: 6px; font-size: 11px; font-weight: bold; padding: 5px;
            }
            QPushButton:hover { background: #eff6ff; color: #2563eb; border-color: #3b82f6; }
        """)
        btn_details.clicked.connect(lambda: self.open_contact_details(contact))
        layout.addWidget(btn_details)
        
        return card

    def filter_contacts(self):
        text = self.search_input.text().lower()
        # Logique de filtrage identique à ton code précédent mais avec display_contacts
        # ... (à compléter selon tes besoins de filtrage)

    def apply_security_policy(self):
        role = self.current_user.role
        self.btn_add.setVisible(SecurityManager.has_permission(role, Permissions.CONTACT_ADD))
        self.btn_pdf.setVisible(SecurityManager.has_permission(role, Permissions.AUDIT_VIEW))