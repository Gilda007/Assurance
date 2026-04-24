# contact_detail_view.py - Version corrigée avec tableaux responsives
"""
Vue détaillée d'un contact avec onglets modernes
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QScrollArea, QGridLayout,
    QDialog, QGraphicsDropShadowEffect, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from addons.Automobiles.views.automobile_form_view import VehicleForm
from addons.Automobiles.views.flotte_form_view import FleetForm

from datetime import datetime


class ContactDetailView(QDialog):
    """Fenêtre de détails d'un contact"""

    contact_updated = Signal()

    def __init__(self, controller, contact, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.contact = contact
        self.parent_window = parent
        
        # Initialiser le contrôleur de flottes
        self.fleet_controller = None
        if hasattr(controller, 'session') and hasattr(controller, 'current_user'):
            try:
                from addons.Automobiles.controllers.flotte_controller import FleetController
                self.fleet_controller = FleetController(controller.session, controller.current_user.id)
            except Exception as e:
                print(f"Erreur initialisation FleetController: {e}")
        
        self.setWindowTitle(f"Détails du contact - {contact.nom} {contact.prenom or ''}")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configure l'interface principale"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

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

        self.tab_widget.addTab(self._create_info_tab(), "👤  Informations")
        self.tab_widget.addTab(self._create_contrats_tab(), "📄  Contrats")
        self.tab_widget.addTab(self._create_vehicules_tab(), "🚗  Véhicules")
        self.tab_widget.addTab(self._create_flottes_tab(), "🚛  Flottes")
        self.tab_widget.addTab(self._create_documents_tab(), "📎  Documents")

        content_layout.addWidget(self.tab_widget)

        # Action bar
        action_bar = self._create_action_bar()
        content_layout.addWidget(action_bar)

        main_layout.addWidget(content_widget)

    def _create_header(self):
        """Crée l'en-tête"""
        header = QFrame()
        header.setFixedHeight(140)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffffff, stop:1 #f8fafc);
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(40, 20, 40, 20)

        # Avatar
        avatar = QLabel()
        avatar.setFixedSize(80, 80)
        avatar.setAlignment(Qt.AlignCenter)
        initials = (self.contact.nom[0].upper() if self.contact.nom else "C") + \
                   (self.contact.prenom[0].upper() if self.contact.prenom else "")
        avatar.setText(initials or "C")
        avatar.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #2563eb, stop:1 #7c3aed);
            border-radius: 40px;
        """)

        # Infos
        info_container = QVBoxLayout()
        info_container.setSpacing(6)

        name = QLabel(f"{self.contact.nom or ''} {self.contact.prenom or ''}".strip())
        name.setStyleSheet("font-size: 24px; font-weight: 700; color: #0f172a;")

        # Badges
        badges = QHBoxLayout()
        badges.setSpacing(8)
        
        type_badge = QLabel(self.contact.type_client or "Client")
        type_badge.setStyleSheet("""
            background: #dbeafe;
            color: #1d4ed8;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        """)
        
        status_badge = QLabel(self.contact.vip_status or "Standard")
        status_badge.setStyleSheet("""
            background: #dcfce7;
            color: #15803d;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        """)
        
        badges.addWidget(type_badge)
        badges.addWidget(status_badge)

        info_container.addWidget(name)
        info_container.addLayout(badges)

        # Contact rapide
        contact_info = QHBoxLayout()
        contact_info.setSpacing(20)
        
        phone = QLabel(f"📞 {self.contact.telephone or 'Tél. non renseigné'}")
        phone.setStyleSheet("color: #475569; font-size: 13px;")
        
        email = QLabel(f"✉️ {self.contact.email or 'Email non renseigné'}")
        email.setStyleSheet("color: #475569; font-size: 13px;")
        
        contact_info.addWidget(phone)
        contact_info.addWidget(email)

        info_container.addLayout(contact_info)

        layout.addWidget(avatar)
        layout.addSpacing(20)
        layout.addLayout(info_container)
        layout.addStretch()

        # Code client
        code_container = QFrame()
        code_container.setStyleSheet("""
            QFrame {
                background: #f1f5f9;
                border-radius: 12px;
                padding: 8px 20px;
            }
        """)
        code_layout = QVBoxLayout(code_container)
        code_layout.setSpacing(2)
        
        code_label = QLabel("CODE CLIENT")
        code_label.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 600;")
        
        code_value = QLabel(self.contact.code_client or "NON ATTRIBUÉ")
        code_value.setStyleSheet("color: #1e293b; font-size: 16px; font-weight: 700;")
        
        code_layout.addWidget(code_label)
        code_layout.addWidget(code_value)

        layout.addWidget(code_container)

        return header

    def _create_summary_cards(self):
        """Crée les cartes de résumé"""
        layout = QHBoxLayout()
        layout.setSpacing(16)

        cards = [
            ("📄", "Contrats", "0", "#3b82f6"),
            ("🚗", "Véhicules", "0", "#10b981"),
            ("🚛", "Flottes", "0", "#8b5cf6"),
            ("💰", "Primes totales", "0 FCFA", "#f59e0b")
        ]

        self.summary_labels = {}

        for icon, label, value, color in cards:
            card = self._create_card(icon, label, value, color)
            layout.addWidget(card)
            self.summary_labels[label.lower()] = card

        layout.addStretch()
        return layout

    def _create_card(self, icon, label, value, color):
        """Crée une carte individuelle"""
        card = QFrame()
        card.setFixedHeight(90)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 16px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        # Icône
        icon_bg = QFrame()
        icon_bg.setFixedSize(50, 50)
        icon_bg.setStyleSheet(f"""
            QFrame {{
                background: {color}10;
                border-radius: 14px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_bg)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 22px;")
        icon_layout.addWidget(icon_lbl)

        # Texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        # ⚠️ IMPORTANT: Définir l'objectName avec la bonne clé
        value_lbl = QLabel(value)
        # Nettoyer la clé : enlever les accents, remplacer les espaces par des underscores
        clean_label = label.lower().replace(" ", "_").replace("é", "e").replace("è", "e").replace("ê", "e")
        value_lbl.setObjectName(f"summary_{clean_label}")
        value_lbl.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 800;
            color: {color};
        """)

        title_lbl = QLabel(label.upper())
        title_lbl.setStyleSheet("""
            font-size: 10px;
            color: #64748b;
            font-weight: 600;
            letter-spacing: 0.5px;
        """)

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

        # Grille d'informations
        info_grid = QGridLayout()
        info_grid.setSpacing(24)
        info_grid.setColumnStretch(0, 1)
        info_grid.setColumnStretch(1, 1)

        sections = [
            ("Identité", [
                ("Nom complet", f"{self.contact.nom or ''} {self.contact.prenom or ''}".strip()),
                ("Date de naissance", self.contact.date_naissance.strftime("%d/%m/%Y") if self.contact.date_naissance else "Non renseigné"),
                ("Nationalité", self.contact.nationalite or "Non renseigné"),
                ("Numéro contribuable", self.contact.num_contribuable or "Non renseigné"),
                ("Catégorie socio-pro", self.contact.cat_socio_prof or "Non renseigné"),
            ]),
            ("Coordonnées", [
                ("Téléphone", self.contact.telephone or "Non renseigné"),
                ("Téléphone portable", self.contact.tel_portable or "Non renseigné"),
                ("Email", self.contact.email or "Non renseigné"),
                ("Email secondaire", self.contact.adresse_2 or "Non renseigné"),
                ("Adresse", self.contact.adresse or "Non renseigné"),
                ("Ville", self.contact.ville or "Non renseigné"),
                ("Permis de conduire", self.contact.num_permis or "Non renseigné"),
            ]),
        ]

        for col, (title, fields) in enumerate(sections):
            section = self._create_info_section(title, fields)
            info_grid.addWidget(section, 0, col)

        container_layout.addLayout(info_grid)

        # Section complémentaire
        extra_section = self._create_info_section("Informations complémentaires", [
            ("Type de client", self.contact.type_client or "Non renseigné"),
            ("Statut VIP", self.contact.vip_status or "Standard"),
            ("Chargé de clientèle", self.contact.charge_clientele or "Non attribué"),
        ])
        container_layout.addWidget(extra_section)

        # Section Audit
        audit_section = self._create_info_section("Audit", [
            ("Créé le", self.contact.created_at.strftime("%d/%m/%Y à %H:%M") if self.contact.created_at else "Non renseigné"),
            ("Créé par", self.contact.created_by or "Système"),
            ("Dernière modification", self.contact.updated_at.strftime("%d/%m/%Y à %H:%M") if self.contact.updated_at else "Jamais"),
            ("Modifié par", self.contact.updated_by or "—"),
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
        """Onglet véhicules avec boutons d'import et création"""
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

        title = QLabel("🚗 Véhicules du client")
        title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1e293b;")

        toolbar_layout.addWidget(title)
        toolbar_layout.addStretch()

        # Bouton Nouveau véhicule
        self.btn_new_vehicle = QPushButton("+ Nouveau véhicule")
        self.btn_new_vehicle.setCursor(Qt.PointingHandCursor)
        self.btn_new_vehicle.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.btn_new_vehicle.clicked.connect(self._on_new_vehicle)

        # Bouton Importer
        self.btn_import_vehicle = QPushButton("📥 Importer")
        self.btn_import_vehicle.setCursor(Qt.PointingHandCursor)
        self.btn_import_vehicle.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.btn_import_vehicle.clicked.connect(self._on_import_vehicle)

        toolbar_layout.addWidget(self.btn_new_vehicle)
        toolbar_layout.addWidget(self.btn_import_vehicle)

        layout.addWidget(toolbar)

        # Tableau avec redimensionnement automatique
        self.vehicules_table = QTableWidget()
        self.vehicules_table.setColumnCount(7)
        self.vehicules_table.setHorizontalHeaderLabels([
            "Immatriculation", "Marque", "Modèle", "Année", "Énergie", "Contrat", ""
        ])
        self.vehicules_table.setAlternatingRowColors(True)
        self.vehicules_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vehicules_table.setShowGrid(False)
        self.vehicules_table.verticalHeader().setVisible(False)
        self.vehicules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vehicules_table.setStyleSheet(self.contrats_table.styleSheet())

        layout.addWidget(self.vehicules_table)

        # Résumé
        summary_frame = self._create_summary_frame("vehicules")
        layout.addWidget(summary_frame)

        return tab

    def _create_flottes_tab(self):
        """Onglet flottes avec boutons d'import et création"""
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

        title = QLabel("🚛 Flottes du client")
        title.setStyleSheet("font-size: 14px; font-weight: 700; color: #1e293b;")

        toolbar_layout.addWidget(title)
        toolbar_layout.addStretch()

        # Bouton Nouvelle flotte
        self.btn_new_fleet = QPushButton("+ Nouvelle flotte")
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
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        self.btn_new_fleet.clicked.connect(self._on_new_fleet)

        toolbar_layout.addWidget(self.btn_new_fleet)

        layout.addWidget(toolbar)

        # Tableau avec redimensionnement automatique
        self.flottes_table = QTableWidget()
        self.flottes_table.setColumnCount(5)
        self.flottes_table.setHorizontalHeaderLabels([
            "Nom", "Code", "Assureur", "Véhicules", "Statut"
        ])
        self.flottes_table.setAlternatingRowColors(True)
        self.flottes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.flottes_table.setShowGrid(False)
        self.flottes_table.verticalHeader().setVisible(False)
        self.flottes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.flottes_table.setStyleSheet(self.contrats_table.styleSheet())

        layout.addWidget(self.flottes_table)

        # Résumé
        summary_frame = self._create_summary_frame("flottes")
        layout.addWidget(summary_frame)

        return tab

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
        """Crée un élément de document"""
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 10px;
            }
            QFrame:hover {
                background: #f1f5f9;
            }
        """)
        layout = QHBoxLayout(item)
        layout.setContentsMargins(15, 12, 15, 12)

        icon = QLabel("📄")
        icon.setStyleSheet("font-size: 18px;")

        name = QLabel(doc_name)
        name.setStyleSheet("font-weight: 500; color: #1e293b;")

        date = QLabel("Aucun document")
        date.setStyleSheet("color: #94a3b8; font-size: 11px;")

        btn = QPushButton("Ajouter")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(80, 30)
        btn.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                color: #3b82f6;
                font-weight: 600;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #eff6ff;
            }
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
        self.btn_edit.clicked.connect(self._on_edit_click)

        self.btn_close = QPushButton("Fermer")
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

        return bar

    def load_data(self):
        """Charge toutes les données"""
        self.load_contrats()
        self.load_vehicules()
        self.load_flottes()
        self._update_summary_cards()

    def load_contrats(self):
        """Charge les contrats du contact (plusieurs contrats possibles)"""
        try:
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
                self.contrats_table.setItem(row, 2, QTableWidgetItem(
                    vehicule.date_debut.strftime("%d/%m/%Y") if vehicule.date_debut else "—"
                ))
                self.contrats_table.setItem(row, 3, QTableWidgetItem(
                    vehicule.date_fin.strftime("%d/%m/%Y") if vehicule.date_fin else "—"
                ))
                
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

    def load_vehicules(self):
        """Charge les véhicules du contact"""
        try:
            # Récupérer les véhicules - s'assurer d'avoir une liste
            result = self.controller.vehicles.get_vehicles_by_owner_id(self.contact.id)
            # Si le résultat est un seul objet Vehicle, le mettre dans une liste
            if result is None:
                vehicules = []
            elif hasattr(result, 'id') and not hasattr(result, '__iter__'):
                vehicules = [result]
            else:
                vehicules = result
            
            self.vehicules_table.setRowCount(0)

            for v in vehicules:
                row = self.vehicules_table.rowCount()
                self.vehicules_table.insertRow(row)

                self.vehicules_table.setItem(row, 0, QTableWidgetItem(v.immatriculation or "—"))
                self.vehicules_table.setItem(row, 1, QTableWidgetItem(v.marque or "—"))
                self.vehicules_table.setItem(row, 2, QTableWidgetItem(v.modele or "—"))
                self.vehicules_table.setItem(row, 3, QTableWidgetItem(str(v.annee or "—")))
                self.vehicules_table.setItem(row, 4, QTableWidgetItem(v.energie or "—"))
                
                contrat = self.controller.contracts.get_active_contract_by_vehicle(v.id)
                self.vehicules_table.setItem(row, 5, QTableWidgetItem(contrat.numero_police if contrat else "—"))

                # Bouton détails
                btn_view = QPushButton("👁️")
                btn_view.setFixedSize(30, 28)
                btn_view.setCursor(Qt.PointingHandCursor)
                btn_view.setStyleSheet("""
                    QPushButton {
                        background: #f1f5f9;
                        border-radius: 6px;
                        border: none;
                    }
                    QPushButton:hover {
                        background: #3b82f6;
                        color: white;
                    }
                """)
                btn_view.clicked.connect(lambda checked, vid=v.id: self._view_vehicle_detail(vid))
                
                widget = QWidget()
                widget_layout = QHBoxLayout(widget)
                widget_layout.setContentsMargins(0, 0, 0, 0)
                widget_layout.addWidget(btn_view)
                self.vehicules_table.setCellWidget(row, 6, widget)

            # Mettre à jour le résumé
            total_label = self.findChild(QLabel, "total_vehicules")
            if total_label:
                total_label.setText(f"Total: {self.vehicules_table.rowCount()} véhicule(s)")
            
            self._update_card_value("véhicules", str(self.vehicules_table.rowCount()))

        except Exception as e:
            print(f"Erreur chargement véhicules: {e}")
            import traceback
            traceback.print_exc()

    def load_flottes(self):
        """Charge les flottes du contact"""
        try:
            self.flottes_table.setRowCount(0)
            
            if self.fleet_controller:
                all_fleets = self.fleet_controller.get_all_fleets()
                
                for fleet in all_fleets:
                    if hasattr(fleet, 'owner_id') and fleet.owner_id == self.contact.id:
                        row = self.flottes_table.rowCount()
                        self.flottes_table.insertRow(row)
                        
                        self.flottes_table.setItem(row, 0, QTableWidgetItem(
                            fleet.nom_flotte if hasattr(fleet, 'nom_flotte') else getattr(fleet, 'nom', '—')
                        ))
                        self.flottes_table.setItem(row, 1, QTableWidgetItem(
                            fleet.code_flotte if hasattr(fleet, 'code_flotte') else '—'
                        ))
                        self.flottes_table.setItem(row, 2, QTableWidgetItem(
                            fleet.assureur if hasattr(fleet, 'assureur') else '—'
                        ))
                        
                        # Compter les véhicules de la flotte
                        nb_vehicules = 0
                        if hasattr(fleet, 'vehicles'):
                            nb_vehicules = len(fleet.vehicles)
                        self.flottes_table.setItem(row, 3, QTableWidgetItem(str(nb_vehicules)))
                        
                        statut = fleet.statut if hasattr(fleet, 'statut') else "Actif"
                        if statut.upper() == "ACTIF":
                            statut_item = QTableWidgetItem("✅ Actif")
                            statut_item.setForeground(QColor("#10b981"))
                        else:
                            statut_item = QTableWidgetItem("❌ Inactif")
                            statut_item.setForeground(QColor("#ef4444"))
                        self.flottes_table.setItem(row, 4, statut_item)

            # Mettre à jour le résumé
            total_label = self.findChild(QLabel, "total_flottes")
            if total_label:
                total_label.setText(f"Total: {self.flottes_table.rowCount()} flotte(s)")
            
            self._update_card_value("flottes", str(self.flottes_table.rowCount()))

        except Exception as e:
            print(f"Erreur chargement flottes: {e}")
            import traceback
            traceback.print_exc()

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
            total_primes = sum(float(getattr(c, 'prime_totale_ttc', 0) or 0) for c in contrats_list)
            
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

    def _view_vehicle_detail(self, vehicle_id):
        """Affiche les détails d'un véhicule"""
        QMessageBox.information(self, "Détails véhicule", f"ID véhicule: {vehicle_id}")

    def _on_edit_click(self):
        """Ouvre le formulaire d'édition"""
        from addons.Automobiles.views.contact_form_view import ContactForm
        dialog = ContactForm(self, self.contact)
        if dialog.exec_():
            self.contact_updated.emit()
            self.close()


def show_contact_details(controller, contact, parent=None):
    """Ouvre la fenêtre de détails d'un contact"""
    dialog = ContactDetailView(controller, contact, parent)
    dialog.exec_()