# contact_detail_view.py - Version corrigée avec tableaux responsives
"""
Vue détaillée d'un contact avec onglets modernes
"""

from PySide6.QtWidgets import (
    QComboBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QScrollArea, QGridLayout,
    QDialog, QGraphicsDropShadowEffect, QApplication, QLineEdit, QCheckBox
)
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont, QColor
import qtawesome as qta
from addons.Automobiles.views.automobile_form_view import VehicleForm
from addons.Automobiles.views.flotte_form_view import FleetForm

from datetime import datetime
import traceback


class ContactDetailView(QDialog):
    """Fenêtre de détails d'un contact"""

    contact_updated = Signal()

    def __init__(self, controller, contact, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.contact = contact
        self.parent_window = parent

        self.is_driver = hasattr(contact, 'driver_name') or hasattr(contact, 'source_type')
        
        # ✅ Si c'est un ContactListItem, extraire l'objet réel
        if hasattr(contact, 'data') and hasattr(contact, 'source_type'):
            self.real_contact = contact.data
            self.source_type = contact.source_type
        else:
            self.real_contact = contact
            self.source_type = 'driver' if hasattr(contact, 'driver_name') else 'contact'
        
        self.setWindowTitle(f"Détails du contact - {contact.nom} {contact.prenom or ''}")
        self.setMinimumSize(1200, 800)
        self.resize(1200, 800)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configure l'interface principale"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setStyleSheet("""
            QToolTip {
                color: #333333;              /* Couleur du texte */
                background-color: #333333; /* Couleur de fond */
                border: 1px solid #3498db; /* Bordure (optionnel) */
                padding: 4px;
            }
        """)

        # En-tête
        header = self._create_header()
        main_layout.addWidget(header)

        # Contenu principal
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f8fafc;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(24)

        # Cartes de résumé
        summary_cards = self._create_summary_cards()
        content_layout.addLayout(summary_cards)

        # Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background: white;
                border-radius: 16px;
            }
            QTabBar::tab {
                background: transparent;
                padding: 12px 28px;
                margin-right: 4px;
                font-weight: 600;
                font-size: 13px;
                color: #64748b;
            }
            QTabBar::tab:hover {
                background: #f1f5f9;
                border-radius: 10px;
            }
            QTabBar::tab:selected {
                color: #2563eb;
            }
        """)

        self.tab_widget.addTab(
            self._create_info_tab(),
            qta.icon('mdi.account', color='#2563eb'), "Informations"
        )
        self.tab_widget.addTab(
            self._create_contrats_tab(),
            qta.icon('mdi.file-document', color='#64748b'), "Contrats"
        )
        self.tab_widget.addTab(
            self._create_vehicules_tab(),
            qta.icon('mdi.car', color='#64748b'), "Véhicules"
        )
        self.tab_widget.addTab(
            self._create_flottes_tab(),
            qta.icon('mdi.truck', color='#64748b'), "Flottes"
        )
        self.tab_widget.addTab(
            self._create_documents_tab(),
            qta.icon('mdi.paperclip', color='#64748b'), "Documents"
        )

        content_layout.addWidget(self.tab_widget)

        # Action bar
        action_bar = self._create_action_bar()
        content_layout.addWidget(action_bar)

        main_layout.addWidget(content_widget)

    def _create_header(self):
        """Crée l'en-tête fidèle à la maquette avec icônes qtawesome"""
        header = QFrame()
        header.setFixedHeight(160)
        header.setStyleSheet("""
            QFrame {
                background: white;
                border-bottom: 1px solid #e2e8f0;
            }
        """)

        layout = QVBoxLayout(header)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(15)

        # 1. Fil d'Ariane
        breadcrumb = QLabel("Gestion des Clients / Fiches contacts")
        breadcrumb.setStyleSheet("color: #64748b; font-size: 13px; background: transparent;")
        layout.addWidget(breadcrumb)

        # 2. Ligne principale (Avatar + Nom + Infos + Code)
        main_row = QHBoxLayout()
        main_row.setSpacing(24)

        # ============================
        # AVATAR
        # ============================
        avatar = QLabel()
        avatar.setFixedSize(90, 90)
        avatar.setAlignment(Qt.AlignCenter)

        nom = getattr(self.real_contact, 'nom', 'Contact')
        prenom = getattr(self.real_contact, 'prenom', '')
        initials = (nom[0].upper() if nom else "C")
        if prenom:
            initials += prenom[0].upper()

        avatar.setText(initials)
        avatar.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #4f46e5, stop:1 #7c3aed);
            border-radius: 45px;
        """)
        main_row.addWidget(avatar)

        # ============================
        # INFOS CONTACT
        # ============================
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        # Ligne Nom + Badge
        name_row = QHBoxLayout()
        name_row.setSpacing(10)

        name_lbl = QLabel(f"{nom} {prenom}".strip())
        name_lbl.setStyleSheet("""
            font-size: 26px;
            font-weight: 800;
            color: #0f172a;
            background: transparent;
        """)
        name_row.addWidget(name_lbl)

        # Badge Statut avec icône check
        status_text = getattr(self.real_contact, 'statut', 'Actif') or 'Actif'
        status_badge = QLabel(f"  {status_text}")
        status_badge.setPixmap(qta.icon('mdi.check-circle', color='white').pixmap(12, 12))
        status_badge.setStyleSheet("""
            background: #10b981;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        """)
        name_row.addWidget(status_badge)
        name_row.addStretch()
        info_layout.addLayout(name_row)

        # Ligne Téléphone + Email
        contact_row = QHBoxLayout()
        contact_row.setSpacing(8)

        phone = getattr(self.real_contact, 'telephone', None) or "Non renseigné"
        phone_icon = QLabel()
        phone_icon.setPixmap(qta.icon('mdi.phone', color='#475569').pixmap(16, 16))
        phone_icon.setStyleSheet("background: transparent;")
        phone_lbl = QLabel(phone)
        phone_lbl.setStyleSheet("color: #475569; font-size: 14px; background: transparent;")

        email = getattr(self.real_contact, 'email', None) or "Non renseigné"
        email_icon = QLabel()
        email_icon.setPixmap(qta.icon('mdi.email-outline', color='#475569').pixmap(16, 16))
        email_icon.setStyleSheet("background: transparent;")
        email_lbl = QLabel(email)
        email_lbl.setStyleSheet("color: #475569; font-size: 14px; background: transparent;")

        contact_row.addWidget(phone_icon)
        contact_row.addWidget(phone_lbl)
        contact_row.addSpacing(20)
        contact_row.addWidget(email_icon)
        contact_row.addWidget(email_lbl)
        contact_row.addStretch()
        info_layout.addLayout(contact_row)

        main_row.addLayout(info_layout)
        main_row.addStretch()

        # ============================
        # CODE CLIENT + BOUTON COPIER
        # ============================
        code_container = QFrame()
        code_container.setStyleSheet("""
            QFrame {
                background: #f1f5f9;
                border-radius: 12px;
                padding: 12px 20px;
            }
        """)
        code_layout = QVBoxLayout(code_container)
        code_layout.setSpacing(4)

        code_title = QLabel("CODE CLIENT")
        code_title.setStyleSheet("""
            color: #64748b;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.5px;
            background: transparent;
        """)

        code_row = QHBoxLayout()
        code_row.setSpacing(8)

        code_val = QLabel(f"LMT-CLT-{self.real_contact.id:05d}")
        code_val.setStyleSheet("""
            color: #0f172a;
            font-size: 18px;
            font-weight: 800;
            background: transparent;
        """)

        btn_copy = QPushButton()
        btn_copy.setIcon(qta.icon('mdi.content-copy', color='#64748b'))
        btn_copy.setIconSize(QSize(16, 16))
        btn_copy.setFixedSize(24, 24)
        btn_copy.setCursor(Qt.PointingHandCursor)
        btn_copy.setToolTip("Copier le code client")
        btn_copy.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(code_val.text()))

        code_row.addWidget(code_val)
        code_row.addWidget(btn_copy)
        code_row.addStretch()

        code_layout.addWidget(code_title)
        code_layout.addLayout(code_row)

        main_row.addWidget(code_container)

        layout.addLayout(main_row)
        return header

    def _create_summary_cards(self):
        """Crée les cartes de résumé"""
        layout = QHBoxLayout()
        layout.setSpacing(16)

        cards = [
            ("mdi.file-document-outline", "Contrats",       "0", "#3b82f6"),
            ("mdi.car",                   "Véhicules",      "0", "#10b981"),
            ("mdi.truck",                 "Flottes",        "0", "#8b5cf6"),
            ("mdi.cash-multiple",         "Primes totales", "0 FCFA", "#f59e0b"),
        ]

        self.summary_labels = {}

        for icon, label, value, color in cards:
            card = self._create_card(icon, label, value, color)
            layout.addWidget(card)
            self.summary_labels[label.lower()] = card

        layout.addStretch()
        return layout

    def _create_card(self, icon_name, label, value, color):
        card = QFrame()
        card.setFixedHeight(100)
        bg_colors = {
            "#3b82f6": "#eff6ff",
            "#10b981": "#ecfdf5",
            "#8b5cf6": "#f5f3ff",
            "#f59e0b": "#fffbeb",
        }
        bg_color = bg_colors.get(color, "#f8fafc")

        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #f1f5f9;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        icon_bg = QFrame()
        icon_bg.setFixedSize(50, 50)
        icon_bg.setStyleSheet(f"background: {bg_color}; border-radius: 12px;")
        icon_layout = QVBoxLayout(icon_bg)
        icon_layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon(icon_name, color=color).pixmap(24, 24))
        icon_lbl.setStyleSheet("background: transparent;")
        icon_layout.addWidget(icon_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        value_lbl = QLabel(value)
        value_lbl.setObjectName(f"summary_{label.lower().replace(' ', '_')}")
        value_lbl.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {color}; background: transparent;")

        title_lbl = QLabel(label.upper())
        title_lbl.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 600; letter-spacing: 0.5px; background: transparent;")

        text_layout.addWidget(value_lbl)
        text_layout.addWidget(title_lbl)

        layout.addWidget(icon_bg)
        layout.addLayout(text_layout)
        layout.addStretch()
        return card

    def _create_info_tab(self):
        """Onglet informations"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(24)

        # ✅ Utiliser real_contact au lieu de contact
        if self.source_type == 'driver':
            nom = getattr(self.real_contact, 'driver_name', '')
            prenom = ''
            date_naissance = getattr(self.real_contact, 'date_naissance', None)
            nationalite = getattr(self.real_contact, 'nationalite', '')
            telephone = getattr(self.real_contact, 'telephone', '')
            email = getattr(self.real_contact, 'email', '')
            adresse = getattr(self.real_contact, 'adresse', '')
            ville = getattr(self.real_contact, 'ville', '')
            num_permis = getattr(self.real_contact, 'num_permis', '')
            cat_permis = getattr(self.real_contact, 'cat_permis', '')
            # Pour un chauffeur, on n'a pas ces champs
            num_contribuable = ''
            cat_socio_prof = ''
            tel_portable = ''
            adresse_2 = ''
            type_client = 'Chauffeur'
            statut = 'Actif'
            charge_clientele = ''
        else:
            nom = getattr(self.real_contact, 'nom', '')
            prenom = getattr(self.real_contact, 'prenom', '')
            date_naissance = getattr(self.real_contact, 'date_naissance', None)
            nationalite = getattr(self.real_contact, 'nationalite', '')
            telephone = getattr(self.real_contact, 'telephone', '')
            email = getattr(self.real_contact, 'email', '')
            adresse = getattr(self.real_contact, 'adresse', '')
            ville = getattr(self.real_contact, 'ville', '')
            num_permis = getattr(self.real_contact, 'num_permis', '')
            cat_permis = getattr(self.real_contact, 'cat_permis', '')
            num_contribuable = getattr(self.real_contact, 'num_contribuable', '')
            cat_socio_prof = getattr(self.real_contact, 'cat_socio_prof', '')
            tel_portable = getattr(self.real_contact, 'tel_portable', '')
            adresse_2 = getattr(self.real_contact, 'adresse_2', '')
            type_client = getattr(self.real_contact, 'type_client', '')
            statut = getattr(self.real_contact, 'statut', 'Actif')
            charge_clientele = getattr(self.real_contact, 'charge_clientele', '')

        # Grille d'informations
        info_grid = QGridLayout()
        info_grid.setSpacing(24)
        info_grid.setColumnStretch(0, 1)
        info_grid.setColumnStretch(1, 1)

        sections = [
            ("Identité", [
                ("Nom complet", f"{nom} {prenom}".strip()),
                ("Date de naissance", date_naissance.strftime("%d/%m/%Y") if date_naissance else "Non renseigné"),
                ("Nationalité", nationalite or "Non renseigné"),
                ("Numéro contribuable", num_contribuable or "Non renseigné"),
                ("Catégorie socio-pro", cat_socio_prof or "Non renseigné"),
            ]),
            ("Coordonnées", [
                ("Téléphone", telephone or "Non renseigné"),
                ("Téléphone portable", tel_portable or "Non renseigné"),
                ("Email", email or "Non renseigné"),
                ("Email secondaire", adresse_2 or "Non renseigné"),
                ("Adresse", adresse or "Non renseigné"),
                ("Ville", ville or "Non renseigné"),
                ("Permis de conduire", num_permis or "Non renseigné"),
            ]),
        ]

        for col, (title, fields) in enumerate(sections):
            section = self._create_info_section(title, fields)
            info_grid.addWidget(section, 0, col)

        container_layout.addLayout(info_grid)

        # Section complémentaire
        extra_section = self._create_info_section("Informations complémentaires", [
            ("Type de client", type_client or "Non renseigné"),
            ("Statut", statut or "Standard"),
            ("Chargé de clientèle", charge_clientele or "Non attribué"),
        ])
        container_layout.addWidget(extra_section)

        # Section Audit
        created_at = getattr(self.real_contact, 'created_at', None)
        updated_at = getattr(self.real_contact, 'updated_at', None)
        created_by = getattr(self.real_contact, 'created_by', 'Système')
        updated_by = getattr(self.real_contact, 'updated_by', '—')
        
        audit_section = self._create_info_section("Audit", [
            ("Créé le", created_at.strftime("%d/%m/%Y à %H:%M") if created_at else "Non renseigné"),
            ("Créé par", created_by or "Système"),
            ("Dernière modification", updated_at.strftime("%d/%m/%Y à %H:%M") if updated_at else "Jamais"),
            ("Modifié par", updated_by or "—"),
        ])
        container_layout.addWidget(audit_section)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        return tab

    def _create_info_section(self, title, fields):
        """Crée une section d'informations"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #1e293b;
        """)
        layout.addWidget(title_lbl)

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setColumnStretch(1, 1)

        for i, (label, value) in enumerate(fields):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #64748b; font-size: 12px;")
            val = QLabel(str(value) if value else "—")
            val.setStyleSheet("color: #1e293b; font-size: 13px; font-weight: 500;")
            val.setWordWrap(True)
            grid.addWidget(lbl, i, 0)
            grid.addWidget(val, i, 1)

        layout.addLayout(grid)

        return section

    def _create_contrats_tab(self):
        """Onglet contrats"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)

        # Barre d'outils
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(15, 10, 15, 10)

        title = QLabel("📋 Historique des contrats")
        title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1e293b;")

        toolbar_layout.addWidget(title)
        toolbar_layout.addStretch()

        layout.addWidget(toolbar)

        # Tableau avec redimensionnement automatique
        self.contrats_table = QTableWidget()
        self.contrats_table.setColumnCount(6)
        self.contrats_table.setHorizontalHeaderLabels([
            "N° Police", "Véhicule", "Début", "Fin", "Prime (FCFA)", "Statut"
        ])
        self.contrats_table.setAlternatingRowColors(True)
        self.contrats_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.contrats_table.setShowGrid(False)
        self.contrats_table.verticalHeader().setVisible(False)
        self.contrats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.contrats_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background: white;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 12px;
                font-weight: 600;
                color: #64748b;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f5f9;
            }
        """)

        layout.addWidget(self.contrats_table)

        # Résumé
        summary_frame = self._create_summary_frame("contrats")
        layout.addWidget(summary_frame)

        return tab

    def _create_vehicules_tab(self):
        """Onglet véhicules fidèle à la maquette"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ─── BARRE D'OUTILS ───
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 10, 16, 10)
        toolbar_layout.setSpacing(12)


        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('mdi.car', color='#0f172a').pixmap(18, 18))
        title_icon.setStyleSheet("background: transparent;")
        title = QLabel("Véhicules du client")
        title.setStyleSheet("font-size: 15px; font-weight: 700; color: #0f172a; background: transparent;")
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.addWidget(title_icon)
        title_row.addWidget(title)
        toolbar_layout.addLayout(title_row)
        toolbar_layout.addStretch()

        # Barre de recherche
        self.search_vehicle_input = QLineEdit()
        self.search_vehicle_input.setPlaceholderText("Rechercher un véhicule...")
        self.search_vehicle_input.setFixedWidth(250)
        self.search_vehicle_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                background: #f8fafc;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #3b82f6; background: white; }
        """)
        self.search_vehicle_input.textChanged.connect(self._apply_vehicle_filters)
        toolbar_layout.addWidget(self.search_vehicle_input)

        #filtrage par flotte
        self.search_flotte_input = QComboBox()
        self.search_flotte_input.setPlaceholderText("Filtrage par flotte")
        self.search_flotte_input.setFixedWidth(250)
        self.search_flotte_input.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                background: #f8fafc;
                font-size: 13px;
            }
            QComboBox:focus { border-color: #3b82f6; background: white; }
        """)
        self.search_flotte_input.currentIndexChanged.connect(self._apply_vehicle_filters)
        toolbar_layout.addWidget(self.search_flotte_input)

        # Bouton Nouveau (Bleu)
        btn_new = QPushButton("  Nouveau véhicule")
        btn_new.setIcon(qta.icon('mdi.plus', color='white'))
        btn_new.setIconSize(QSize(16, 16))
        btn_new.setCursor(Qt.PointingHandCursor)
        btn_new.setStyleSheet("""
            QPushButton {
                background: #3b82f6; color: white; border: none;
                border-radius: 8px; padding: 8px 16px; font-weight: 600; font-size: 13px;
            }
            QPushButton:hover { background: #2563eb; }
        """)
        btn_new.clicked.connect(self._on_new_vehicle)
        toolbar_layout.addWidget(btn_new)

        # Bouton Impression groupée (Gris)
        self.btn_batch_print = QPushButton("  Impression groupée")
        self.btn_batch_print.setIcon(qta.icon('mdi.printer', color='#475569'))
        self.btn_batch_print.setIconSize(QSize(16, 16))
        self.btn_batch_print.setCursor(Qt.PointingHandCursor)
        self.btn_batch_print.setEnabled(False)
        self.btn_batch_print.setStyleSheet("""
            QPushButton {
                background: white; color: #475569; border: 1px solid #e2e8f0;
                border-radius: 8px; padding: 8px 16px; font-weight: 600; font-size: 13px;
            }
            QPushButton:hover { background: #f8fafc; }
            QPushButton:disabled { background: #f1f5f9; color: #94a3b8; }
        """)
        self.btn_batch_print.clicked.connect(self._on_batch_print)
        toolbar_layout.addWidget(self.btn_batch_print)

        # Bouton Importer (Vert)
        btn_import = QPushButton("  Importer")
        btn_import.setIcon(qta.icon('mdi.download', color='white'))
        btn_import.setIconSize(QSize(16, 16))
        btn_import.setCursor(Qt.PointingHandCursor)
        btn_import.setStyleSheet("""
            QPushButton {
                background: #10b981; color: white; border: none;
                border-radius: 8px; padding: 8px 16px; font-weight: 600; font-size: 13px;
            }
            QPushButton:hover { background: #059669; }
        """)
        btn_import.clicked.connect(self._on_import_vehicle)
        toolbar_layout.addWidget(btn_import)

        layout.addWidget(toolbar)

        # ─── TABLEAU ───
        self.vehicules_table = QTableWidget()
        self.vehicules_table.setColumnCount(9)
        self.vehicules_table.setHorizontalHeaderLabels([
            "✓", "Immatriculation", "Marque", "Modèle", "Année", "Énergie", "Contrat", "Code", "Actions"
        ])
        self.vehicules_table.setAlternatingRowColors(True)
        self.vehicules_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vehicules_table.setShowGrid(False)
        self.vehicules_table.verticalHeader().setVisible(False)
        self.vehicules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vehicules_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                gridline-color: transparent;
                alternate-background-color: #f8fafc;
                font-size: 13px;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 14px 12px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: 600;
                color: #64748b;
                text-transform: uppercase;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background: #eff6ff;
                color: #0f172a;
            }
        """)
        
        # Connecter la sélection pour le bouton d'impression
        self.vehicules_table.itemChanged.connect(self._on_vehicle_selection_changed)
        
        layout.addWidget(self.vehicules_table)

        # ─── PIED DE PAGE (Total + Pagination) ───
        footer = QFrame()
        footer.setStyleSheet("background: transparent;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)

        self.total_label = QLabel("Total : 0 véhicule(s)")
        self.total_label.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")
        footer_layout.addWidget(self.total_label)
        self.select_all_vehicles_checkbox = QCheckBox("Tout sélectionner")
        self.select_all_vehicles_checkbox.setTristate(True)
        self.select_all_vehicles_checkbox.setEnabled(False)
        self.select_all_vehicles_checkbox.clicked.connect(self._set_all_vehicles_selected)
        footer_layout.addWidget(self.select_all_vehicles_checkbox)
        footer_layout.addStretch()

        pagination_label = QLabel("Pagination  <  >")
        pagination_label.setStyleSheet("color: #94a3b8; font-size: 13px;")
        footer_layout.addWidget(pagination_label)

        layout.addWidget(footer)

        return tab

    def _apply_vehicle_filters(self):
        text = self.search_vehicle_input.text().strip().lower()
        selected_fleet_id = self.search_flotte_input.currentData()

        for row in range(self.vehicules_table.rowCount()):
            matches_text = not text
            if text:
                for col in range(1, 8):
                    item = self.vehicules_table.item(row, col)
                    if item and text in item.text().lower():
                        matches_text = True
                        break
                if not matches_text:
                    widget = self.vehicules_table.cellWidget(row, 2)
                    if widget:
                        for lbl in widget.findChildren(QLabel):
                            if text in lbl.text().lower():
                                matches_text = True
                                break

            check_item = self.vehicules_table.item(row, 0)
            fleet_id = check_item.data(Qt.UserRole + 1) if check_item else None
            if selected_fleet_id == "__unassigned__":
                matches_fleet = fleet_id is None
            else:
                matches_fleet = selected_fleet_id is None or fleet_id == selected_fleet_id

            self.vehicules_table.setRowHidden(row, not (matches_text and matches_fleet))

        self._update_vehicle_selection_controls()

    def _create_flottes_tab(self):
        """Onglet flottes avec boutons d'import, création et impression groupée"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)

        # ─── BARRE D'OUTILS ───
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(15, 10, 15, 10)
        toolbar_layout.setSpacing(10)

        # Titre avec icône
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('mdi.truck', color='#0f172a').pixmap(18, 18))
        title_icon.setStyleSheet("background: transparent;")
        title = QLabel("Flottes du client")
        title.setStyleSheet("font-size: 15px; font-weight: 700; color: #0f172a; background: transparent;")
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.addWidget(title_icon)
        title_row.addWidget(title)
        toolbar_layout.addLayout(title_row)
        toolbar_layout.addStretch()

        # ── Bouton Nouvelle flotte (violet) ──
        self.btn_new_fleet = QPushButton("  Nouvelle flotte")
        self.btn_new_fleet.setIcon(qta.icon('mdi.plus', color='white'))
        self.btn_new_fleet.setIconSize(QSize(16, 16))
        self.btn_new_fleet.setCursor(Qt.PointingHandCursor)
        self.btn_new_fleet.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #7c3aed; }
        """)
        self.btn_new_fleet.clicked.connect(self._on_new_fleet)
        toolbar_layout.addWidget(self.btn_new_fleet)

        # ── Bouton Impression groupée (gris, désactivé par défaut) ──
        self.btn_batch_print_fleets = QPushButton("  Impression groupée")
        self.btn_batch_print_fleets.setIcon(qta.icon('mdi.printer', color='#475569'))
        self.btn_batch_print_fleets.setIconSize(QSize(16, 16))
        self.btn_batch_print_fleets.setCursor(Qt.PointingHandCursor)
        self.btn_batch_print_fleets.setEnabled(False)
        self.btn_batch_print_fleets.setStyleSheet("""
            QPushButton {
                background: white;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { background: #f8fafc; }
            QPushButton:disabled { background: #f1f5f9; color: #94a3b8; }
        """)
        self.btn_batch_print_fleets.clicked.connect(self._on_batch_print_fleets)
        toolbar_layout.addWidget(self.btn_batch_print_fleets)

        # ── Bouton Importer (vert) ──
        self.btn_import_flotte = QPushButton("  Importer")
        self.btn_import_flotte.setIcon(qta.icon('mdi.download', color='white'))
        self.btn_import_flotte.setIconSize(QSize(16, 16))
        self.btn_import_flotte.setCursor(Qt.PointingHandCursor)
        self.btn_import_flotte.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        self.btn_import_flotte.clicked.connect(self._on_import_fleet)
        toolbar_layout.addWidget(self.btn_import_flotte)
        toolbar_layout.addWidget(self.btn_new_fleet)
        toolbar_layout.addWidget(self.btn_batch_print_fleets)

        layout.addWidget(toolbar)

        # Tableau avec 7 colonnes (incluant sélection et Actions)
        self.flottes_table = QTableWidget()
        self.flottes_table.setColumnCount(7)  # +1 pour la checkbox
        self.flottes_table.setHorizontalHeaderLabels([
            "✓", "Nom", "Code", "Assureur", "Véhicules", "Statut", "Actions"
        ])
        self.flottes_table.setColumnWidth(0, 40)  # Largeur fixe pour la checkbox
        self.flottes_table.setAlternatingRowColors(True)
        self.flottes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.flottes_table.setShowGrid(False)
        self.flottes_table.verticalHeader().setVisible(False)
        self.flottes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.flottes_table.setStyleSheet(self.contrats_table.styleSheet())
        
        # Connecter le signal de changement de sélection
        self.flottes_table.itemChanged.connect(self._on_fleet_selection_changed)

        layout.addWidget(self.flottes_table)

        # Résumé
        summary_frame = self._create_summary_frame("flottes")
        layout.addWidget(summary_frame)

        return tab

    def _on_fleet_selection_changed(self, item):
        """Active/désactive le bouton d'impression selon la sélection des flottes"""
        if item and item.column() == 0:
            has_selection = False
            for row in range(self.flottes_table.rowCount()):
                check_item = self.flottes_table.item(row, 0)
                if check_item and check_item.checkState() == Qt.Checked:
                    has_selection = True
                    break
            
            self.btn_batch_print_fleets.setEnabled(has_selection)

    def _on_batch_print_fleets(self):
        """Gère l'impression groupée des flottes sélectionnées - Génère directement les PDF"""
        selected_fleets = []
        
        for row in range(self.flottes_table.rowCount()):
            check_item = self.flottes_table.item(row, 0)
            if check_item and check_item.checkState() == Qt.Checked:
                fleet_id = check_item.data(Qt.UserRole)
                selected_fleets.append({
                    'id': fleet_id,
                    'nom': self.flottes_table.item(row, 1).text(),
                    'code': self.flottes_table.item(row, 2).text(),
                })
        
        if not selected_fleets:
            QMessageBox.warning(self, "Aucune sélection", 
                            "Veuillez sélectionner au moins une flotte à imprimer.")
            return
        
        # Lancer directement l'impression sans dialogue de sélection
        self._start_fleet_batch_print(selected_fleets)

    def _start_fleet_batch_print(self, fleets_data):
        """Lance l'impression groupée des flottes (rapport PDF uniquement)"""
        from addons.Automobiles.views.fleet_batch_print_manager import FleetBatchPrintManager
        
        if not hasattr(self, 'fleet_batch_print_manager'):
            self.fleet_batch_print_manager = FleetBatchPrintManager(self.controller, self)
        
        # Passer directement les documents par défaut (rapport de flotte)
        # Pas de dialogue, on imprime directement le rapport
        self.fleet_batch_print_manager.start_batch_print(fleets_data)

    def _on_import_fleet(self):
        """Importe des flottes depuis un fichier Excel/CSV avec calcul des garanties"""
        try:
            # Vérifier que le contrôleur a les méthodes nécessaires
            if not hasattr(self.controller, 'fleets'):
                QMessageBox.warning(self, "Erreur", "Module flottes non disponible")
                return
            
            if not hasattr(self.controller, 'vehicles'):
                QMessageBox.warning(self, "Erreur", "Module véhicules non disponible")
                return
            
            # Stocker l'ID du contact dans le contrôleur pour l'import
            self.controller.current_contact_id = self.contact.id
            
            # Ouvrir le dialogue d'importation avancée
            from addons.Automobiles.views.fleet_import_avanced_dialog import FleetImportAdvancedDialog
            dialog = FleetImportAdvancedDialog(self.controller, self)
            
            if dialog.exec():
                # Recharger les données après l'import
                self.load_flottes()
                self.load_vehicules()
                self._update_summary_cards()
                QMessageBox.information(self, "Succès", "Importation terminée avec succès!")
                
        except ImportError as e:
            print(f"Erreur import du module: {e}")
            traceback.print_exc()
            QMessageBox.warning(self, "Information", 
                            "La fonctionnalité d'importation avancée sera bientôt disponible.\n"
                            "Pour l'instant, vous pouvez créer les flottes manuellement.")
        except Exception as e:
            print(f"Erreur import flotte: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'importation: {str(e)}")

    def _create_documents_tab(self):
        """Onglet documents"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)

        docs_frame = QFrame()
        docs_frame.setStyleSheet("background: white; border-radius: 16px;")
        docs_layout = QVBoxLayout(docs_frame)
        docs_layout.setContentsMargins(20, 20, 20, 20)
        docs_layout.setSpacing(15)

        title = QLabel("Documents associés")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1e293b;")
        docs_layout.addWidget(title)

        doc_types = ["Contrat", "Attestation", "Devis", "Facture", "Avenant", "Sinistre"]
        
        for doc in doc_types:
            doc_item = self._create_document_item(doc)
            docs_layout.addWidget(doc_item)

        layout.addWidget(docs_frame)

        return tab

    def _create_document_item(self, doc_name):
        item = QFrame()
        item.setStyleSheet("""
            QFrame { background: #f8fafc; border-radius: 10px; }
            QFrame:hover { background: #f1f5f9; }
        """)
        layout = QHBoxLayout(item)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)

        # Mapping doc -> icône
        icons = {
            "Contrat":     "mdi.file-document",
            "Attestation": "mdi.certificate",
            "Devis":       "mdi.file-edit",
            "Facture":     "mdi.receipt",
            "Avenant":     "mdi.file-plus",
            "Sinistre":    "mdi.alert-circle",
        }
        icon_key = icons.get(doc_name, "mdi.file")

        icon = QLabel()
        icon.setPixmap(qta.icon(icon_key, color='#3b82f6').pixmap(20, 20))
        icon.setStyleSheet("background: transparent;")

        name = QLabel(doc_name)
        name.setStyleSheet("font-weight: 500; color: #1e293b; background: transparent;")

        date = QLabel("Aucun document")
        date.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent;")

        btn = QPushButton("  Ajouter")
        btn.setIcon(qta.icon('mdi.plus', color='#3b82f6'))
        btn.setIconSize(QSize(12, 12))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(90, 30)
        btn.setStyleSheet("""
            QPushButton {
                background: white; border: 1px solid #e2e8f0;
                border-radius: 8px; color: #3b82f6;
                font-weight: 600; font-size: 11px;
            }
            QPushButton:hover { background: #eff6ff; }
        """)

        layout.addWidget(icon)
        layout.addWidget(name)
        layout.addStretch()
        layout.addWidget(date)
        layout.addWidget(btn)
        return item

    def _create_summary_frame(self, prefix):
        """Crée un cadre de résumé"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #f1f5f9;
                border-radius: 12px;
            }
        """)
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(20, 12, 20, 12)

        total_label = QLabel(f"Total: 0 élément(s)")
        total_label.setObjectName(f"total_{prefix}")
        total_label.setStyleSheet("font-weight: 600; color: #1e293b;")

        frame_layout.addWidget(total_label)
        frame_layout.addStretch()

        return frame

    def _create_action_bar(self):
        """Crée la barre d'action"""
        bar = QFrame()
        bar.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 14px;
            }
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 12, 20, 12)

        layout.addStretch()

        self.btn_edit = QPushButton("Modifier le contact")
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)

        # ✅ Bouton Actualiser
        self.btn_refresh = QPushButton("  Actualiser")
        self.btn_refresh.setIcon(qta.icon('mdi.refresh', color='white'))
        self.btn_refresh.setIconSize(QSize(16, 16))
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        self.btn_refresh.clicked.connect(self.refresh_all_data)

        self.btn_edit = QPushButton("  Modifier le contact")
        self.btn_edit.setIcon(qta.icon('mdi.pencil', color='white'))
        self.btn_edit.setIconSize(QSize(16, 16))
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        self.btn_edit.clicked.connect(self._on_edit_click)
        self.btn_edit.clicked.connect(self._on_edit_click)

        self.btn_close = QPushButton("  Fermer")
        self.btn_close.setIcon(qta.icon('mdi.close', color='#475569'))
        self.btn_close.setIconSize(QSize(16, 16))
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: none;
                border-radius: 10px;
                padding: 10px 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        self.btn_close.clicked.connect(self.close)

        layout.addWidget(self.btn_edit)
        layout.addSpacing(10)
        layout.addWidget(self.btn_close)
        layout.addWidget(self.btn_refresh)

        return bar

    def load_data(self):
        """Charge toutes les données"""
        self.load_contrats()
        self.load_vehicules()
        self.load_flottes()
        self._update_summary_cards()

    def load_contrats(self, force_refresh: bool = False):
        """Charge les contrats du contact (plusieurs contrats possibles)"""
        try:
            if force_refresh and hasattr(self.controller.contracts, '_invalidate_cache'):
                self.controller.contracts._invalidate_cache()
            # Récupérer TOUS les contrats du contact
            contrats = self.controller.contracts.get_active_contract_by_owner_id(self.contact.id)
            print(self.contact.id)
            
            # S'assurer que contrats est une liste
            if contrats is None:
                contrats_list = []
            elif hasattr(contrats, 'id') and not hasattr(contrats, '__iter__'):
                # Si c'est un seul objet, le mettre dans une liste
                contrats_list = [contrats]
            else:
                contrats_list = contrats
            
            self.contrats_table.setRowCount(0)
            
            total_primes = 0
            actifs = 0

            # Parcourir TOUS les contrats
            for contrat in contrats_list:
                row = self.contrats_table.rowCount()
                self.contrats_table.insertRow(row)
                
                # Récupérer le véhicule associé au contrat
                vehicule = None
                if hasattr(contrat, 'vehicle_id') and contrat.vehicle_id:
                    vehicule = self.controller.vehicles.get_vehicles_by_id(contrat.vehicle_id)
                
                self.contrats_table.setItem(row, 0, QTableWidgetItem(contrat.numero_police or "—"))
                self.contrats_table.setItem(row, 1, QTableWidgetItem(vehicule.immatriculation if vehicule else "—"))
                self.contrats_table.setItem(row, 2, QTableWidgetItem(contrat.date_debut.strftime("%d/%m/%Y") if contrat.date_debut else "—"))
                self.contrats_table.setItem(row, 3, QTableWidgetItem(contrat.date_fin.strftime("%d/%m/%Y") if contrat.date_fin else "—"))
                
                prime = float(contrat.prime_totale_ttc or 0)
                total_primes += prime
                self.contrats_table.setItem(row, 4, QTableWidgetItem(f"{prime:,.0f}".replace(",", " ")))
                
                statut = contrat.statut_paiement or "NON_PAYE"
                if statut.upper() == "PAYE":
                    statut_item = QTableWidgetItem("✅ Payé")
                    statut_item.setForeground(QColor("#10b981"))
                    actifs += 1
                elif statut.upper() == "PARTIEL":
                    statut_item = QTableWidgetItem("⚠️ Partiel")
                    statut_item.setForeground(QColor("#f59e0b"))
                else:
                    statut_item = QTableWidgetItem("⏳ En attente")
                    statut_item.setForeground(QColor("#ef4444"))
                self.contrats_table.setItem(row, 5, statut_item)

            # Mettre à jour le résumé
            total_label = self.findChild(QLabel, "total_contrats")
            if total_label:
                total_label.setText(f"Total: {self.contrats_table.rowCount()} contrat(s)")
            
            # Mettre à jour les cartes
            self._update_card_value("contrats", str(self.contrats_table.rowCount()))
            self._update_card_value("primes totales", f"{total_primes:,.0f}".replace(",", " ") + " FCFA")

        except Exception as e:
            print(f"Erreur chargement contrats: {e}")
            import traceback
            traceback.print_exc()

    def load_vehicules(self, force_refresh: bool = False):
        """Charge les véhicules du contact"""
        try:
            if force_refresh and hasattr(self.controller.vehicles, '_invalidate_cache'):
                self.controller.vehicles._invalidate_cache()
                
            result = self.controller.vehicles.get_vehicles_by_owner_id(self.contact.id)
            vehicules = []
            if result:
                if isinstance(result, list):
                    vehicules = result
                elif hasattr(result, 'id'):
                    vehicules = [result]
            
            self.vehicules_table.setRowCount(0)
            self.vehicules_table.blockSignals(True)

            for v in vehicules:
                row = self.vehicules_table.rowCount()
                self.vehicules_table.insertRow(row)
                self.vehicules_table.setRowHeight(row, 60)

                # 1. Checkbox
                check_item = QTableWidgetItem()
                check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                check_item.setCheckState(Qt.Unchecked)
                check_item.setData(Qt.UserRole, v.id)
                check_item.setData(Qt.UserRole + 1, getattr(v, 'fleet_id', None))
                self.vehicules_table.setItem(row, 0, check_item)

                # 2. Immatriculation (en gras)
                immat = QTableWidgetItem(v.immatriculation or "—")
                font = immat.font()
                font.setBold(True)
                immat.setFont(font)
                self.vehicules_table.setItem(row, 1, immat)

                # 3. Marque (Logo + Texte)
                # marque_widget = QWidget()
                # marque_layout = QHBoxLayout(marque_widget)
                # marque_layout.setContentsMargins(0, 0, 0, 0)
                # marque_layout.setSpacing(8)
                
                # # On simule un logo avec un label (si pas d'image, on met juste le texte)
                # # Si vous avez les logos, utilisez QPixmap
                # logo_lbl = QLabel("🚗") 
                # logo_lbl.setStyleSheet("font-size: 16px;")
                # nom_marque = QLabel(v.marque or "—")
                # nom_marque.setStyleSheet("font-weight: 500;")
                
                # marque_layout.addWidget(logo_lbl)
                # marque_layout.addWidget(nom_marque)
                # marque_layout.addStretch()
                # self.vehicules_table.setCellWidget(row, 2, marque_widget)

                marque_widget = QWidget()
                marque_layout = QHBoxLayout(marque_widget)
                marque_layout.setContentsMargins(0, 0, 0, 0)
                marque_layout.setSpacing(8)

                logo_lbl = QLabel()
                logo_lbl.setPixmap(qta.icon('mdi.car-side', color='#64748b').pixmap(18, 18))
                logo_lbl.setStyleSheet("background: transparent;")

                nom_marque = QLabel(v.marque or "—")
                nom_marque.setStyleSheet("font-weight: 500; background: transparent;")

                marque_layout.addWidget(logo_lbl)
                marque_layout.addWidget(nom_marque)
                marque_layout.addStretch()
                self.vehicules_table.setCellWidget(row, 2, marque_widget)

                # 4. Modèle
                self.vehicules_table.setItem(row, 3, QTableWidgetItem(v.modele or "—"))

                # 5. Année
                self.vehicules_table.setItem(row, 4, QTableWidgetItem(str(v.annee or "—")))

                # 6. Énergie
                self.vehicules_table.setItem(row, 5, QTableWidgetItem(v.energie or "—"))

                # 7. Contrat
                contrat = self.controller.contracts.get_active_contract_by_vehicle(v.id)
                contrat_text = "—"
                if contrat:
                    contrat_text = "SED" # Ou contrat.type_contrat si existe
                self.vehicules_table.setItem(row, 6, QTableWidgetItem(contrat_text))

                # 8. Code (PF-202607-0001)
                # Si vous avez un champ code_police dans le contrat
                code_police = getattr(contrat, 'numero_police', f"PF-2026{row:02d}-0001")
                self.vehicules_table.setItem(row, 7, QTableWidgetItem(code_police))

                # 9. Actions
                actions_widget = self._create_actions_widget_for_vehicle(v)
                self.vehicules_table.setCellWidget(row, 8, actions_widget)

            self.vehicules_table.blockSignals(False)
            self._update_vehicle_selection_controls()
            self._apply_vehicle_filters()
            
            # Mettre à jour le total
            if hasattr(self, 'total_label'):
                self.total_label.setText(f"Total : {self.vehicules_table.rowCount()} véhicule(s)")
            
            self._update_card_value("véhicules", str(self.vehicules_table.rowCount()))

        except Exception as e:
            print(f"Erreur chargement véhicules: {e}")
            import traceback
            traceback.print_exc()

    def refresh_all_data(self):
        """
        Rafraîchit toutes les données de la page (contrats, véhicules, flottes, cartes)
        """
        # Désactiver le bouton pendant l'actualisation
        self.btn_refresh.setEnabled(False)
        self.btn_refresh.setText("⏳ Actualisation...")
        
        try:
            # ✅ 1. Invalider le cache des véhicules
            if hasattr(self.controller, 'vehicles'):
                if hasattr(self.controller.vehicles, '_invalidate_cache'):
                    self.controller.vehicles._invalidate_cache()
                if hasattr(self.controller.vehicles, 'invalidate_vehicle_cache'):
                    self.controller.vehicles.invalidate_vehicle_cache()
            
            # ✅ 2. Invalider le cache des contrats
            if hasattr(self.controller, 'contracts'):
                if hasattr(self.controller.contracts, '_invalidate_cache'):
                    self.controller.contracts._invalidate_cache()
            
            # ✅ 3. Invalider le cache des flottes (CORRECTION)
            if hasattr(self.controller, 'fleets'):
                # Appeler _invalidate_cache si elle existe
                if hasattr(self.controller.fleets, '_invalidate_cache'):
                    self.controller.fleets._invalidate_cache()
                # Appeler invalidate_fleet_cache si elle existe
                if hasattr(self.controller.fleets, 'invalidate_fleet_cache'):
                    self.controller.fleets.invalidate_fleet_cache()
            
            # ✅ 4. Invalider le cache des contacts
            if hasattr(self.controller, 'contacts'):
                if hasattr(self.controller.contacts, 'invalidate_cache'):
                    self.controller.contacts.invalidate_cache()
            
            # ✅ 5. Recharger toutes les données
            self.load_contrats()
            self.load_vehicules()
            self.load_flottes()
            
            # ✅ 6. Mettre à jour les cartes de résumé
            self._update_summary_cards()
            
            # ✅ 7. Mettre à jour l'en-tête
            self._update_header_info()
            
            # ✅ 8. Notification de succès
            QMessageBox.information(self, "Actualisation", "✅ Toutes les données ont été actualisées avec succès.")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'actualisation: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'actualisation: {str(e)}")
        
        finally:
            # Réactiver le bouton
            self.btn_refresh.setEnabled(True)
            self.btn_refresh.setText("🔄 Actualiser")

    def _update_header_info(self):
        """
        Met à jour les informations de l'en-tête (nom, code client, etc.)
        """
        # Récupérer les dernières données du contact depuis la base
        if self.source_type == 'driver':
            refreshed_contact = self.controller.drivers.get_driver_by_id(self.real_contact.id)
        else:
            refreshed_contact = self.controller.contacts.get_contact_by_id(self.real_contact.id)
        
        if refreshed_contact:
            # Mettre à jour l'objet interne
            self.real_contact = refreshed_contact
            
            # Mettre à jour l'en-tête (optionnel)
            # Si tu veux mettre à jour le titre de la fenêtre
            nom = getattr(self.real_contact, 'nom', 'Contact')
            prenom = getattr(self.real_contact, 'prenom', '')
            self.setWindowTitle(f"Détails du contact - {nom} {prenom}".strip())

    def _on_vehicle_selection_changed(self, item):
        """Active/désactive le bouton d'impression selon la sélection"""
        if item and item.column() == 0:
            self._update_vehicle_selection_controls()

    def _set_all_vehicles_selected(self, selected: bool):
        """Sélectionne ou désélectionne uniquement les lignes visibles."""
        self.vehicules_table.blockSignals(True)
        try:
            for row in range(self.vehicules_table.rowCount()):
                if self.vehicules_table.isRowHidden(row):
                    continue
                check_item = self.vehicules_table.item(row, 0)
                if check_item:
                    check_item.setCheckState(Qt.Checked if selected else Qt.Unchecked)
        finally:
            self.vehicules_table.blockSignals(False)
        self._update_vehicle_selection_controls()

    def _update_vehicle_selection_controls(self):
        """Synchronise les commandes avec la sélection visible et globale."""
        visible_rows = [
            row for row in range(self.vehicules_table.rowCount())
            if not self.vehicules_table.isRowHidden(row)
        ]
        selected_visible = sum(
            1
            for row in visible_rows
            if (check_item := self.vehicules_table.item(row, 0))
            and check_item.checkState() == Qt.Checked
        )
        selected_total = sum(
            1
            for row in range(self.vehicules_table.rowCount())
            if (check_item := self.vehicules_table.item(row, 0))
            and check_item.checkState() == Qt.Checked
        )

        self.btn_batch_print.setEnabled(selected_total > 0)
        self.select_all_vehicles_checkbox.setEnabled(bool(visible_rows))

        if selected_visible == 0:
            state = Qt.Unchecked
        elif selected_visible == len(visible_rows):
            state = Qt.Checked
        else:
            state = Qt.PartiallyChecked

        signals_were_blocked = self.select_all_vehicles_checkbox.blockSignals(True)
        self.select_all_vehicles_checkbox.setCheckState(state)
        self.select_all_vehicles_checkbox.blockSignals(signals_were_blocked)

    def _create_actions_widget_for_vehicle(self, vehicle):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)

        btn_style = """
            QPushButton {
                background: transparent;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover { background: %s; border-color: %s; }
        """

        btn_view = QPushButton()
        btn_view.setIcon(qta.icon('mdi.eye', color='#64748b'))
        btn_view.setIconSize(QSize(16, 16))
        btn_view.setFixedSize(32, 32)
        btn_view.setStyleSheet(btn_style % ("#eff6ff", "#3b82f6"))
        btn_view.clicked.connect(lambda: self._view_vehicle_detail(vehicle))

        btn_edit = QPushButton()
        btn_edit.setIcon(qta.icon('mdi.pencil', color='#64748b'))
        btn_edit.setIconSize(QSize(16, 16))
        btn_edit.setFixedSize(32, 32)
        btn_edit.setStyleSheet(btn_style % ("#fffbeb", "#f59e0b"))
        btn_edit.clicked.connect(lambda: self._edit_vehicle(vehicle))

        btn_delete = QPushButton()
        btn_delete.setIcon(qta.icon('mdi.trash-can', color='#64748b'))
        btn_delete.setIconSize(QSize(16, 16))
        btn_delete.setFixedSize(32, 32)
        btn_delete.setStyleSheet(btn_style % ("#fef2f2", "#ef4444"))
        btn_delete.clicked.connect(lambda: self._delete_vehicle(vehicle))

        layout.addWidget(btn_view)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        return container

    def load_flottes(self, force_refresh: bool = False):
        """Charge les flottes du contact avec colonne de sélection"""
        try:
            if force_refresh and hasattr(self.controller.fleets, '_invalidate_cache'):
                self.controller.fleets._invalidate_cache()
            # Vider le tableau AVANT de parcourir les données
            self.flottes_table.setRowCount(0)
            
            # Vérifier que le controller existe
            if not hasattr(self.controller, 'fleets'):
                print("❌ Controller.fleets non disponible")
                return
            
            # Mettre à jour le nombre de colonnes (7 au lieu de 6)
            self.flottes_table.setColumnCount(7)
            self.flottes_table.setHorizontalHeaderLabels([
                "✓", "Nom", "Code", "Assureur", "Véhicules", "Statut", "Actions"
            ])
            self.flottes_table.setColumnWidth(0, 40)
            
            # Récupérer les flottes
            all_fleets = self.controller.fleets.get_fleets_by_owner(self.contact.id)
            
            # Normaliser en liste
            if not all_fleets:
                all_fleets = []
            elif not isinstance(all_fleets, (list, tuple)):
                all_fleets = [all_fleets]

            selected_fleet_id = self.search_flotte_input.currentData()
            self.search_flotte_input.blockSignals(True)
            try:
                self.search_flotte_input.clear()
                self.search_flotte_input.addItem("Toutes les flottes", None)
                self.search_flotte_input.addItem("Véhicules sans flotte", "__unassigned__")
                for fleet in all_fleets:
                    if getattr(fleet, 'owner_id', None) != self.contact.id:
                        continue
                    fleet_name = getattr(fleet, 'nom_flotte', None) or getattr(fleet, 'nom', None) or f"Flotte {fleet.id}"
                    fleet_code = getattr(fleet, 'code_flotte', None) or getattr(fleet, 'code', None)
                    label = f"{fleet_name} ({fleet_code})" if fleet_code else fleet_name
                    self.search_flotte_input.addItem(label, fleet.id)
            finally:
                self.search_flotte_input.blockSignals(False)
            selected_index = self.search_flotte_input.findData(selected_fleet_id)
            self.search_flotte_input.setCurrentIndex(selected_index if selected_index >= 0 else 0)
            self._apply_vehicle_filters()
            
            # Pré-charger toutes les compagnies pour optimisation
            compagnie_ids = set()
            for fleet in all_fleets:
                if hasattr(fleet, 'owner_id') and fleet.owner_id == self.contact.id:
                    if hasattr(fleet, 'assureur') and fleet.assureur and isinstance(fleet.assureur, int):
                        compagnie_ids.add(fleet.assureur)
            
            # Charger les noms des compagnies en une seule requête
            compagnies_cache = {}
            if compagnie_ids and hasattr(self.controller, 'session'):
                try:
                    from addons.Automobiles.models import Compagnie
                    compagnies = self.controller.session.query(Compagnie).filter(
                        Compagnie.id.in_(compagnie_ids)
                    ).all()
                    compagnies_cache = {c.id: c.nom for c in compagnies if hasattr(c, 'nom')}
                except Exception as e:
                    print(f"Erreur chargement compagnies: {e}")
            
            # Remplir le tableau
            self.flottes_table.blockSignals(True)
            
            for fleet in all_fleets:
                # Vérifier l'appartenance
                owner_id = getattr(fleet, 'owner_id', None)
                if owner_id != self.contact.id:
                    continue
                
                row = self.flottes_table.rowCount()
                self.flottes_table.insertRow(row)
                self.flottes_table.setRowHeight(row, 70)
                
                # ⭐ Checkbox de sélection
                check_item = QTableWidgetItem()
                check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                check_item.setCheckState(Qt.Unchecked)
                check_item.setData(Qt.UserRole, fleet.id)  # Stocker l'ID de la flotte
                self.flottes_table.setItem(row, 0, check_item)
                
                # Nom de la flotte
                nom_flotte = getattr(fleet, 'nom_flotte', None) or getattr(fleet, 'nom', '—')
                self.flottes_table.setItem(row, 1, QTableWidgetItem(nom_flotte))
                
                # Code flotte
                code_flotte = getattr(fleet, 'code_flotte', None) or getattr(fleet, 'code', '—')
                self.flottes_table.setItem(row, 2, QTableWidgetItem(code_flotte))
                
                # Compagnie
                compagnie_nom = '—'
                if hasattr(fleet, 'compagnie') and fleet.compagnie:
                    compagnie_nom = getattr(fleet.compagnie, 'nom', '—')
                elif hasattr(fleet, 'assureur') and fleet.assureur:
                    compagnie_nom = compagnies_cache.get(fleet.assureur, str(fleet.assureur))
                self.flottes_table.setItem(row, 3, QTableWidgetItem(compagnie_nom))
                
                # Nombre de véhicules
                nb_vehicules = 0
                if hasattr(fleet, 'vehicles'):
                    nb_vehicules = len(fleet.vehicles)
                elif hasattr(fleet, 'vehicules'):
                    nb_vehicules = len(fleet.vehicules)
                self.flottes_table.setItem(row, 4, QTableWidgetItem(str(nb_vehicules)))
                
                # Statut
                statut = getattr(fleet, 'statut', 'Actif')
                statut_item = QTableWidgetItem("✅ Actif" if str(statut).upper() == "ACTIF" else "❌ Inactif")
                statut_item.setForeground(QColor("#10b981" if str(statut).upper() == "ACTIF" else "#ef4444"))
                self.flottes_table.setItem(row, 5, statut_item)
                
                # Actions
                actions_widget = self._create_actions_widget_for_fleet(fleet)
                self.flottes_table.setCellWidget(row, 6, actions_widget)
            
            self.flottes_table.blockSignals(False)
            
            # Connecter le signal de sélection
            self.flottes_table.itemChanged.connect(self._on_fleet_selection_changed)
            
            # Mettre à jour les résumés
            total_label = self.findChild(QLabel, "total_flottes")
            if total_label:
                total_label.setText(f"Total: {self.flottes_table.rowCount()} flotte(s)")
            
            self._update_card_value("flottes", str(self.flottes_table.rowCount()))
            
            # Désactiver le bouton d'impression par défaut
            self.btn_batch_print_fleets.setEnabled(False)
            
            print(f"✅ {self.flottes_table.rowCount()} flottes chargées pour le contact {self.contact.id}")

        except Exception as e:
            print(f"❌ Erreur chargement flottes: {e}")
            import traceback
            traceback.print_exc()

    def _create_actions_widget_for_fleet(self, fleet):
        """Crée les boutons d'action pour une flotte"""
        container = QWidget()
        container.setFixedHeight(45)  # Hauteur fixe pour le conteneur
        container.setMinimumWidth(120)  # Largeur minimale
        container.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        # Bouton Voir les détails
        btn_style = """
            QPushButton {
                background: transparent;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover { background: %s; border-color: %s; }
        """

        btn_view = QPushButton()
        btn_view.setIcon(qta.icon('mdi.eye', color='#64748b'))
        btn_view.setIconSize(QSize(16, 16))
        btn_view.setFixedSize(32, 32)
        btn_view.setStyleSheet(btn_style % ("#eff6ff", "#3b82f6"))
        btn_view.clicked.connect(lambda: self._view_fleet_detail(fleet))

        btn_edit = QPushButton()
        btn_edit.setIcon(qta.icon('mdi.pencil', color='#64748b'))
        btn_edit.setIconSize(QSize(16, 16))
        btn_edit.setFixedSize(32, 32)
        btn_edit.setStyleSheet(btn_style % ("#fffbeb", "#f59e0b"))
        btn_edit.clicked.connect(lambda: self._edit_fleet(fleet))

        btn_delete = QPushButton()
        btn_delete.setIcon(qta.icon('mdi.trash-can', color='#64748b'))
        btn_delete.setIconSize(QSize(16, 16))
        btn_delete.setFixedSize(32, 32)
        btn_delete.setStyleSheet(btn_style % ("#fef2f2", "#ef4444"))
        btn_delete.clicked.connect(lambda: self._delete_fleet(fleet))

        btn_vehicles = QPushButton()
        btn_vehicles.setIcon(qta.icon('mdi.car-multiple', color='#64748b'))
        btn_vehicles.setIconSize(QSize(16, 16))
        btn_vehicles.setFixedSize(32, 32)
        btn_vehicles.setToolTip("Gérer les véhicules")
        btn_vehicles.setStyleSheet(btn_style % ("#f0fdf4", "#10b981"))
        btn_vehicles.clicked.connect(lambda: self._manage_fleet_vehicles(fleet))

        layout.addWidget(btn_view)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        layout.addWidget(btn_vehicles)
        
        return container
    
    def _view_fleet_detail(self, fleet):
        """Affiche les détails d'une flotte"""
        try:
            # Ouvrir une vue détaillée de la flotte
            from addons.Automobiles.views.flotte_detail_view import FleetDetailView
            dialog = FleetDetailView(self.controller, fleet, self)
            dialog.show()
        except Exception as e:
            print(f"Erreur affichage détails flotte: {e}")
            QMessageBox.warning(self, "Erreur", f"Impossible d'afficher les détails: {str(e)}")

    def _edit_fleet(self, fleet):
        """Modifie une flotte"""
        try:
            from addons.Automobiles.views.flotte_form_view import FleetForm
            
            contacts = self.controller.fleets.get_all_contacts_for_combo()
            compagnies = self.controller.fleets.get_all_compagnies_for_combo()
            
            dialog = FleetForm(
                controller=self.controller,
                current_fleet=fleet,
                mode="update",
                contacts_list=contacts,
                compagnies_list=compagnies,
                preselected_client_id=self.contact.id
            )
            
            if dialog.exec():
                self.load_flottes()  # Recharger les données
                self._update_summary_cards()
                QMessageBox.information(self, "Succès", "Flotte modifiée avec succès!")
                
        except Exception as e:
            print(f"Erreur modification flotte: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de modifier la flotte: {str(e)}")

    def _delete_fleet(self, fleet):
        """Supprime une flotte après confirmation"""
        try:
            # Vérifier si la flotte contient des véhicules
            nb_vehicules = 0
            if hasattr(fleet, 'vehicles'):
                nb_vehicules = len(fleet.vehicles)
            elif hasattr(fleet, 'vehicules'):
                nb_vehicules = len(fleet.vehicules)
            
            message = f"Êtes-vous sûr de vouloir supprimer la flotte '{fleet.nom_flotte}' ?"
            if nb_vehicules > 0:
                message += f"\n\n⚠️ Attention: Cette flotte contient {nb_vehicules} véhicule(s).\nLa suppression ne supprimera pas les véhicules, mais ils ne seront plus associés à cette flotte."
            
            reply = QMessageBox.question(
                self, 
                "Confirmation de suppression",
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Détacher les véhicules puis supprimer
                if nb_vehicules > 0:
                    # Optionnel: détacher les véhicules
                    for vehicle in fleet.vehicles:
                        vehicle.fleet_id = None
                        self.controller.session.commit()
                
                # Supprimer la flotte
                success, msg = self.controller.fleets.delete_fleet(fleet.id)
                
                if success:
                    self.load_flottes()
                    self._update_summary_cards()
                    QMessageBox.information(self, "Succès", "Flotte supprimée avec succès!")
                else:
                    QMessageBox.warning(self, "Erreur", f"Erreur lors de la suppression: {msg}")
                    
        except Exception as e:
            print(f"Erreur suppression flotte: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de supprimer la flotte: {str(e)}")

    def _manage_fleet_vehicles(self, fleet):
        """Gère les véhicules d'une flotte"""
        try:
            from addons.Automobiles.views.fleet_vehicles_manager import FleetVehiclesManager
            dialog = FleetVehiclesManager(self.controller, fleet, self)
            if dialog.exec():
                self.load_flottes()  # Recharger pour mettre à jour le nombre de véhicules
                self._update_summary_cards()
        except ImportError:
            # Fallback: ouvrir le formulaire de la flotte en mode édition
            QMessageBox.information(self, "Gestion des véhicules", 
                                "Cette fonctionnalité sera bientôt disponible.\n"
                                "Pour l'instant, utilisez 'Modifier' pour gérer les véhicules.")
            self._edit_fleet(fleet)

    def _update_summary_cards(self):
        """Met à jour les cartes de résumé - Version directe"""
        try:
            # Récupérer les données
            result = self.controller.vehicles.get_vehicles_by_owner_id(self.contact.id)
            if result is None:
                vehicules = []
            elif hasattr(result, 'id') and not hasattr(result, '__iter__'):
                vehicules = [result]
            else:
                vehicules = result
            
            # Récupérer les contrats
            contrats = self.controller.contracts.get_active_contract_by_owner_id(self.contact.id)
            if contrats is None:
                contrats_list = []
            elif hasattr(contrats, 'id') and not hasattr(contrats, '__iter__'):
                contrats_list = [contrats]
            else:
                contrats_list = contrats
            
            # Calcul des totaux
            total_primes = sum(int(getattr(c, 'prime_totale_ttc', 0) or 0) for c in contrats_list)
            
            # Mettre à jour directement les cartes
            updates = [
                ("contrats", str(len(contrats_list))),
                ("vehicules", str(len(vehicules))),  # ← sans accent
                ("flottes", str(self.flottes_table.rowCount())),
                ("primes_totales", f"{total_primes:,.0f}".replace(",", " ") + " FCFA")  # ← underscore
            ]
            
            for key, value in updates:
                target = self.findChild(QLabel, f"summary_{key}")
                if target:
                    target.setText(value)
                    print(f"✅ Mis à jour: summary_{key} = {value}")
                else:
                    print(f"❌ Label non trouvé: summary_{key}")
                    
        except Exception as e:
            print(f"Erreur mise à jour résumé: {e}")
            import traceback
            traceback.print_exc()

    def _update_card_value(self, card_key, value):
        """Met à jour la valeur d'une carte"""
        if card_key in self.summary_labels:
            for child in self.summary_labels[card_key].findChildren(QLabel):
                if child.objectName() == f"summary_{card_key}":
                    child.setText(value)
                    # Forcer le rafraîchissement
                    child.update()
                    child.repaint()
                    break

    def _on_new_vehicle(self):
        """Crée un nouveau véhicule pour ce contact"""
        
        # Créer un dictionnaire avec l'ID du propriétaire
        prefill_data = {
            'owner_id': self.contact.id
        }
        
        # Ouvrir le formulaire avec les données pré-remplies
        dialog = VehicleForm(
            controller=self.controller,
            contacts_list=[],
            current_user=getattr(self, 'current_user', None),
            mode="add",
            data=prefill_data
        )
        
        if dialog.exec():
            self.load_vehicules()
            self.load_contrats()
            self._update_summary_cards()
            QMessageBox.information(self, "Succès", "Véhicule ajouté avec succès!")

    def _on_import_vehicle(self):
        """Importe des véhicules"""
        QMessageBox.information(self, "Importer véhicules", "Fonctionnalité à implémenter")

    def _on_new_fleet(self):
        """Crée une nouvelle flotte pour ce contact"""
        
        contacts = self.controller.fleets.get_all_contacts_for_combo()
        compagnies = self.controller.fleets.get_all_compagnies_for_combo()
        
        dialog = FleetForm(
            controller=self.controller,
            current_fleet=None,
            mode="add",
            contacts_list=contacts,
            compagnies_list=compagnies,
            preselected_client_id=self.contact.id  # ← Passer l'ID du contact
        )
        if dialog.exec():
            self.load_flottes()
            self._update_summary_cards()
            QMessageBox.information(self, "Succès", "Flotte créée avec succès!")

    def format_phone(self, phone):
        """Formate un numéro de téléphone avec +237"""
        if not phone or phone == 'N/A':
            return 'N/A'
        
        # Nettoyer : enlever espaces, tirets, parenthèses
        cleaned = ''.join(filter(str.isdigit, str(phone)))
        
        if not cleaned:
            return 'N/A'
        
        # 9 chiffres -> +237XXXXXXXXX
        if len(cleaned) == 9:
            return f"+237{cleaned}"
        
        # 12 chiffres commençant par 237 -> +237XXXXXXXXX
        if len(cleaned) == 12 and cleaned.startswith('237'):
            return f"+{cleaned}"
        
        # Déjà formaté avec +237
        if str(phone).startswith('+237'):
            return str(phone)
        
        # Déjà formaté avec 237 sans +
        if str(phone).startswith('237'):
            return f"+{phone}"
        
        return str(phone)

    def _view_vehicle_detail(self, vehicle):
        """
        Prépare et affiche l'interface de détails pour un objet Vehicle.
        """
        
        try:
            print(f"🔍 Chargement détails pour le véhicule ID: {vehicle.id if hasattr(vehicle, 'id') else 'unknown'}")
            
            # ============================================================
            # ÉTAPE 1 : VÉRIFIER L'OBJET ET RÉCUPÉRER LES DONNÉES VIA LE CONTRÔLEUR
            # ============================================================
            
            # Récupérer l'ID du véhicule
            vehicle_id = getattr(vehicle, 'id', None)
            if not vehicle_id:
                QMessageBox.warning(self, "Erreur", "ID du véhicule non trouvé")
                return
            
            # ✅ Utiliser le contrôleur pour récupérer les données du véhicule
            if not hasattr(self.controller, 'vehicles'):
                QMessageBox.warning(self, "Erreur", "Contrôleur de véhicules non disponible")
                return
            
            # ✅ Récupérer les données du véhicule via le contrôleur
            vehicle_data = self.controller.vehicles.get_vehicle_details_data(vehicle_id)
            
            if not vehicle_data:
                QMessageBox.warning(self, "Erreur", "Impossible de récupérer les données du véhicule")
                return
            
            # ============================================================
            # ÉTAPE 2 : ENRICHIR LES DONNÉES AVEC LE PROPRIÉTAIRE ET LA COMPAGNIE
            # ============================================================
            
            # ✅ Récupérer le propriétaire via le contrôleur
            if hasattr(self.controller, 'contacts'):
                owner_id = vehicle_data.get('owner_id')
                if owner_id:
                    owner = self.controller.contacts.get_contact_by_id(owner_id)
                    if owner:
                        vehicle_data['owner'] = f"{getattr(owner, 'nom', '')} {getattr(owner, 'prenom', '')}".strip()
                        vehicle_data['phone'] = self.format_phone(getattr(owner, 'telephone', 'N/A'))
                        vehicle_data['email'] = getattr(owner, 'email', 'N/A')
                        vehicle_data['city'] = getattr(owner, 'ville', 'Yaoundé')
            
            # ✅ Récupérer la compagnie via le contrôleur
            if hasattr(self.controller, 'compagnies'):
                compagny_id = vehicle_data.get('compagny_id')
                if compagny_id:
                    compagny = self.controller.vehicles.get_compagnie_by_id(compagny_id)
                    if compagny:
                        vehicle_data['compagny'] = getattr(compagny, 'nom', 'Non définie')
            
            # ============================================================
            # ÉTAPE 3 : CHARGER LES GARANTIES SI NÉCESSAIRE
            # ============================================================
            
            
            
            # ============================================================
            # ÉTAPE 4 : AFFICHER LA VUE
            # ============================================================
            
            from .vehicle_detail_view import VehicleDetailView
            
            detail_dialog = QDialog(self)
            detail_dialog.setWindowTitle(f"Fiche Véhicule : {vehicle_data.get('immatriculation', 'N/A')}")
            detail_dialog.setMinimumSize(950, 750)
            
            layout = QVBoxLayout(detail_dialog)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # ✅ Passer les données au lieu de l'objet SQLAlchemy
            self.view_details = VehicleDetailView(
                vehicle_data=vehicle_data,
                controller=self.controller,
                db_session=None  # Plus besoin de session car toutes les données sont dans le dict
            )
            layout.addWidget(self.view_details)
            
            if hasattr(self.view_details, 'btn_back'):
                self.view_details.btn_back.clicked.connect(detail_dialog.close)
            
            detail_dialog.exec()
            
        except Exception as e:
            print(f"❌ Erreur show_detail_vehicle : {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Impossible d'afficher les détails du véhicule : {e}")

    def _on_edit_click(self):
        """Ouvre le formulaire d'édition"""
        from addons.Automobiles.views.contact_form_view import ContactForm
        dialog = ContactForm(self, self.contact)
        if dialog.exec_():
            self.contact_updated.emit()
            self.close()

    def _edit_vehicle(self, vehicle):
        """Ouvre le formulaire d'édition d'un véhicule"""
        try:
            from addons.Automobiles.views.automobile_form_view import VehicleForm
            
            # Récupérer l'utilisateur courant
            current_user = getattr(self.controller, 'current_user', None)
            
            # Ouvrir le formulaire en mode édition
            dialog = VehicleForm(
                controller=self.controller,
                contacts_list=[],
                current_user=current_user,
                vehicle_to_edit=vehicle,
                mode="edit"
            )
            
            if dialog.exec():
                # Recharger les données après modification
                self.load_vehicules()
                self.load_contrats()
                self._update_summary_cards()
                QMessageBox.information(self, "Succès", "Véhicule modifié avec succès!")
                
        except Exception as e:
            print(f"Erreur édition véhicule: {e}")
            QMessageBox.warning(self, "Erreur", f"Impossible de modifier le véhicule: {str(e)}")

    def _on_batch_print(self):
        """Gère l'impression groupée des véhicules sélectionnés"""
        selected_vehicles = []
        
        for row in range(self.vehicules_table.rowCount()):
            check_item = self.vehicules_table.item(row, 0)
            if check_item and check_item.checkState() == Qt.Checked:
                vehicle_id = check_item.data(Qt.UserRole)
                # ⭐ Passer l'ID complet du véhicule, pas seulement les données d'affichage
                selected_vehicles.append({
                    'id': vehicle_id,
                    'immatriculation': self.vehicules_table.item(row, 1).text(),
                })
        
        if not selected_vehicles:
            QMessageBox.warning(self, "Aucune sélection", 
                            "Veuillez sélectionner au moins un véhicule à imprimer.")
            return
        
        from addons.Automobiles.views.batch_print_dialog import BatchPrintDialog
        dialog = BatchPrintDialog(self)
        
        if dialog.exec():
            selected_documents = dialog.get_selected_documents()
            if selected_documents:
                mode_dialog = QMessageBox(self)
                mode_dialog.setWindowTitle("Mode de sortie")
                mode_dialog.setText("Comment souhaitez-vous traiter les documents sélectionnés ?")
                pdf_button = mode_dialog.addButton(
                    "Exporter en PDF (choisir un dossier)",
                    QMessageBox.AcceptRole
                )
                paper_button = mode_dialog.addButton(
                    "Imprimer sur papier",
                    QMessageBox.ActionRole
                )
                mode_dialog.addButton(QMessageBox.Cancel)
                mode_dialog.exec()

                if mode_dialog.clickedButton() is pdf_button:
                    self._start_batch_print(selected_vehicles, selected_documents, "pdf")
                elif mode_dialog.clickedButton() is paper_button:
                    self._start_batch_print(selected_vehicles, selected_documents, "paper")

    def _start_batch_print(self, vehicles_data, selected_documents, output_mode="paper"):
        """Lance l'impression groupée via le gestionnaire"""
        from addons.Automobiles.views.batch_print_manager import BatchPrintManager
        
        # Créer le gestionnaire s'il n'existe pas
        if not hasattr(self, 'batch_print_manager'):
            self.batch_print_manager = BatchPrintManager(self.controller, self)
        
        # Démarrer l'impression
        self.batch_print_manager.start_batch_print(
            vehicles_data,
            selected_documents,
            output_mode=output_mode
        )

    def _cancel_batch_print(self):
        """Annule l'impression groupée de manière thread-safe"""
        if hasattr(self, 'print_thread') and self.print_thread and self.print_thread.isRunning():
            self.print_thread.cancel()
            # Attendre que le thread se termine (avec timeout)
            self.print_thread.wait(2000)

    def _on_print_progress(self, current, total, message):
        """Met à jour la progression - appelé depuis le thread principal"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            # Éviter les appels trop fréquents
            if current % 1 == 0 or current == total:
                self.progress_dialog.setValue(current)
                self.progress_dialog.setLabelText(message)
                QApplication.processEvents()

    def _on_print_finished(self, success, message):
        """Termine l'impression groupée - appelé depuis le thread principal"""
        # Nettoyer le thread
        if hasattr(self, 'print_thread') and self.print_thread:
            self.print_thread.quit()
            self.print_thread.wait(1000)
            self.print_thread = None
        
        # Fermer la boîte de progression
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog.deleteLater()
        
        if success:
            QMessageBox.information(self, "Impression terminée", message)
        else:
            QMessageBox.warning(self, "Erreur", message)
        
        # Réactiver le bouton d'impression
        self.btn_batch_print.setEnabled(True)

    def _on_document_printed(self, document_name, success):
        """Notification pour chaque document imprimé - appelé depuis le thread principal"""
        # Optionnel: afficher une notification discrète
        if not success:
            print(f"❌ Erreur lors de l'impression de {document_name}")

    def _delete_vehicle(self, vehicle):
        """Supprime un véhicule après confirmation"""
        try:
            # Demander confirmation
            reply = QMessageBox.question(
                self,
                "Confirmation de suppression",
                f"Êtes-vous sûr de vouloir supprimer le véhicule {vehicle.immatriculation} ?\n\n"
                f"⚠️ Cette action est irréversible.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Appeler la méthode de suppression du contrôleur
                success, message = self.controller.vehicles.deactivate_vehicle(vehicle.id, getattr(self.controller, 'current_user_id', 1))
                
                if success:
                    self.load_vehicules()
                    self.load_contrats()
                    self._update_summary_cards()
                    QMessageBox.information(self, "Succès", f"Véhicule {vehicle.immatriculation} supprimé avec succès!")
                else:
                    QMessageBox.warning(self, "Erreur", f"Erreur lors de la suppression: {message}")
                    
        except Exception as e:
            print(f"Erreur suppression véhicule: {e}")
            QMessageBox.warning(self, "Erreur", f"Impossible de supprimer le véhicule: {str(e)}")

def show_contact_details(controller, contact, parent=None):
    """Ouvre la fenêtre de détails d'un contact"""
    dialog = ContactDetailView(controller, contact, parent)
    dialog.exec_()