# contact_detail_view.py - Version corrigée avec tableaux responsives
"""
Vue détaillée d'un contact avec onglets modernes
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QScrollArea, QGridLayout,
    QDialog, QGraphicsDropShadowEffect, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
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
        
        self.setWindowTitle(f"Détails du contact - {contact.nom} {contact.prenom or ''}")
        self.setMinimumSize(1100, 700)
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

        # ⭐ NOUVEAU: Bouton Impression groupée
        self.btn_batch_print = QPushButton("🖨️ Impression groupée")
        self.btn_batch_print.setCursor(Qt.PointingHandCursor)
        self.btn_batch_print.setEnabled(False)  # Désactivé par défaut
        self.btn_batch_print.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #cbd5e1;
            }
        """)
        self.btn_batch_print.clicked.connect(self._on_batch_print)

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
        toolbar_layout.addWidget(self.btn_batch_print)
        toolbar_layout.addWidget(self.btn_import_vehicle)

        layout.addWidget(toolbar)

        # Tableau avec redimensionnement automatique
        self.vehicules_table = QTableWidget()
        self.vehicules_table.setColumnCount(8)
        self.vehicules_table.setHorizontalHeaderLabels([
            "Immatriculation", "Marque", "Modèle", "Année", "Énergie", "Contrat", "Code", "Actions"
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
        """Onglet flottes avec boutons d'import, création et impression groupée"""
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

        # ⭐ NOUVEAU: Bouton Impression groupée pour les flottes
        self.btn_batch_print_fleets = QPushButton("🖨️ Impression groupée")
        self.btn_batch_print_fleets.setCursor(Qt.PointingHandCursor)
        self.btn_batch_print_fleets.setEnabled(False)  # Désactivé par défaut
        self.btn_batch_print_fleets.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #cbd5e1;
            }
        """)
        self.btn_batch_print_fleets.clicked.connect(self._on_batch_print_fleets)

        self.btn_import_flotte = QPushButton("📥 Importer")
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
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.btn_import_flotte.clicked.connect(self._on_import_fleet)

        toolbar_layout.addWidget(self.btn_new_fleet)
        toolbar_layout.addWidget(self.btn_batch_print_fleets)
        toolbar_layout.addWidget(self.btn_import_flotte)

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
        """Importe des flottes"""
        QMessageBox.information(self, "Importer flottes", "Fonctionnalité à implémenter")

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

    def load_vehicules(self):
        """Charge les véhicules du contact avec colonne de sélection"""
        try:
            result = self.controller.vehicles.get_vehicles_by_owner_id(self.contact.id)
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
                self.vehicules_table.setRowHeight(row, 60)

                # ⭐ Checkbox de sélection
                check_item = QTableWidgetItem()
                check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                check_item.setCheckState(Qt.Unchecked)
                check_item.setData(Qt.UserRole, v.id)  # Stocker l'ID
                self.vehicules_table.setItem(row, 0, check_item)

                self.vehicules_table.setItem(row, 1, QTableWidgetItem(v.immatriculation or "—"))
                self.vehicules_table.setItem(row, 2, QTableWidgetItem(v.marque or "—"))
                self.vehicules_table.setItem(row, 3, QTableWidgetItem(v.modele or "—"))
                self.vehicules_table.setItem(row, 4, QTableWidgetItem(str(v.annee or "—")))
                self.vehicules_table.setItem(row, 5, QTableWidgetItem(v.energie or "—"))
                
                contrat = self.controller.contracts.get_active_contract_by_vehicle(v.id)
                self.vehicules_table.setItem(row, 6, QTableWidgetItem(contrat.numero_police if contrat else "—"))
                
                # Actions
                actions_widget = self._create_actions_widget_for_vehicle(v)
                self.vehicules_table.setCellWidget(row, 7, actions_widget)

            # Activer/désactiver le bouton d'impression selon la sélection
            self.vehicules_table.itemChanged.connect(self._on_vehicle_selection_changed)
            
            # Mettre à jour le résumé
            total_label = self.findChild(QLabel, "total_vehicules")
            if total_label:
                total_label.setText(f"Total: {self.vehicules_table.rowCount()} véhicule(s)")
            
            self._update_card_value("véhicules", str(self.vehicules_table.rowCount()))

        except Exception as e:
            print(f"Erreur chargement véhicules: {e}")
            import traceback
            traceback.print_exc()


    def _on_vehicle_selection_changed(self, item):
        """Active/désactive le bouton d'impression selon la sélection"""
        if item and item.column() == 0:
            # Vérifier s'il y a au moins un véhicule sélectionné
            has_selection = False
            for row in range(self.vehicules_table.rowCount()):
                check_item = self.vehicules_table.item(row, 0)
                if check_item and check_item.checkState() == Qt.Checked:
                    has_selection = True
                    break
            
            self.btn_batch_print.setEnabled(has_selection)

    def _create_actions_widget_for_vehicle(self, vehicle):
        """Crée les boutons d'action pour un véhicule"""
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        # Bouton Voir
        btn_view = QPushButton("👁️")
        btn_view.setFixedSize(50, 32)
        btn_view.setCursor(Qt.PointingHandCursor)
        btn_view.setToolTip("Voir les détails")
        btn_view.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                border: 1px solid #3498db;
                border-radius: 6px;
                background-color: transparent;
                color: #3498db;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
        """)
        btn_view.clicked.connect(lambda: self._view_vehicle_detail(vehicle))
        
        # Bouton Modifier
        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(50, 32)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setToolTip("Modifier le véhicule")
        btn_edit.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                border: 1px solid #f39c12;
                border-radius: 6px;
                background-color: transparent;
                color: #f39c12;
            }
            QPushButton:hover {
                background-color: #f39c12;
                color: white;
            }
        """)
        btn_edit.clicked.connect(lambda: self._edit_vehicle(vehicle))
        
        # Bouton Supprimer
        btn_delete = QPushButton("🗑️")
        btn_delete.setFixedSize(50, 32)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setToolTip("Supprimer le véhicule")
        btn_delete.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                border: 1px solid #e74c3c;
                border-radius: 6px;
                background-color: transparent;
                color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: white;
            }
        """)
        btn_delete.clicked.connect(lambda: self._delete_vehicle(vehicle))
        
        layout.addWidget(btn_view)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        
        return container
    
    def load_flottes(self):
        """Charge les flottes du contact avec colonne de sélection"""
        try:
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
        btn_view = QPushButton("👁️")
        btn_view.setFixedSize(50, 32)
        btn_view.setCursor(Qt.PointingHandCursor)
        btn_view.setToolTip("Voir les détails de la flotte")
        btn_view.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                border: 1px solid #3498db;
                border-radius: 6px;
                background-color: transparent;
                color: #3498db;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
        """)
        btn_view.clicked.connect(lambda: self._view_fleet_detail(fleet))
        
        # Bouton Modifier
        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(50, 32)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setToolTip("Modifier la flotte")
        btn_edit.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                border: 1px solid #f39c12;
                border-radius: 6px;
                background-color: transparent;
                color: #f39c12;
            }
            QPushButton:hover {
                background-color: #f39c12;
                color: white;
            }
        """)
        btn_edit.clicked.connect(lambda: self._edit_fleet(fleet))
        
        # Bouton Supprimer
        btn_delete = QPushButton("🗑️")
        btn_delete.setFixedSize(50, 32)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setToolTip("Supprimer la flotte")
        btn_delete.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                border: 1px solid #e74c3c;
                border-radius: 6px;
                background-color: transparent;
                color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: white;
            }
        """)
        btn_delete.clicked.connect(lambda: self._delete_fleet(fleet))
        
        # Bouton Gérer les véhicules
        btn_vehicles = QPushButton("🚗")
        btn_vehicles.setFixedSize(50, 32)
        btn_vehicles.setCursor(Qt.PointingHandCursor)
        btn_vehicles.setToolTip("Gérer les véhicules de la flotte")
        btn_vehicles.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                border: 1px solid #2ecc71;
                border-radius: 6px;
                background-color: transparent;
                color: #2ecc71;
            }
            QPushButton:hover {
                background-color: #27ae60;
                color: white;
            }
        """)
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

    def _view_vehicle_detail(self, vehicle):
        """
        Prépare et affiche l'interface de détails pour un objet Vehicle.
        """
        try:
            # ⚠️ CRUCIAL : Récupérer la session AVANT tout
            session = getattr(self.controller, 'session', None)
            if not session:
                raise Exception("Session non disponible")
            
            # ============================================================
            # CHARGER TOUTES LES DONNÉES NÉCESSAIRES TANT QUE LA SESSION EST ACTIVE
            # ============================================================
            
            # 1. Charger explicitement la relation contract
            contract = None
            if hasattr(vehicle, 'id') and vehicle.id:
                # Méthode 1 : via la relation (si elle existe)
                try:
                    # Forcer le chargement de la relation contract
                    contract = vehicle.contract
                except Exception as e:
                    print(f"Erreur chargement contract via relation: {e}")
                    # Méthode 2 : via une requête directe
                    try:
                        from addons.Automobiles.models import Contrat  # Adaptez le chemin
                        contract = session.query(Contrat).filter(Contrat.vehicle_id == vehicle.id).first()
                        print(f"✓ Contrat trouvé via requête directe: {contract.id if contract else 'None'}")
                    except Exception as e2:
                        print(f"Erreur chargement contract via requête: {e2}")
            
            # 2. Charger les informations du propriétaire (Contact)
            owner_name = "N/A"
            owner_phone = "N/A"
            owner_email = "N/A"
            owner_city = "Yaoundé"
            owner_obj = None
            
            if hasattr(vehicle, 'owner_id') and vehicle.owner_id:
                try:
                    from addons.Automobiles.models import Contact  # Adaptez le chemin
                    owner_obj = session.query(Contact).get(vehicle.owner_id)
                    if owner_obj:
                        owner_name = f"{getattr(owner_obj, 'nom', '')} {getattr(owner_obj, 'prenom', '')}".strip()
                        owner_phone = getattr(owner_obj, 'telephone', 'N/A')
                        owner_email = getattr(owner_obj, 'email', 'N/A')
                        owner_city = getattr(owner_obj, 'ville', 'Yaoundé')
                        print(f"✓ Propriétaire trouvé: {owner_name}")
                except Exception as e:
                    print(f"Erreur chargement contact: {e}")
            
            # 3. Charger les informations de la compagnie
            compagny_name = "Non définie"
            if hasattr(vehicle, 'compagny_id') and vehicle.compagny_id:
                try:
                    from addons.Automobiles.models import Compagnie  # Adaptez le chemin
                    compagny_obj = session.query(Compagnie).get(vehicle.compagny_id)
                    if compagny_obj:
                        compagny_name = getattr(compagny_obj, 'nom', 'N/A')
                        print(f"✓ Compagnie trouvée: {compagny_name}")
                except Exception as e:
                    print(f"Erreur chargement compagnie: {e}")
            
            # 4. Récupérer les dates (attention: vehicle.date_debut peut être une date ou None)
            date_debut_str = ""
            date_fin_str = ""
            if hasattr(vehicle, 'date_debut') and vehicle.date_debut:
                if hasattr(vehicle.date_debut, 'strftime'):
                    date_debut_str = vehicle.date_debut.strftime('%d/%m/%Y')
                else:
                    date_debut_str = str(vehicle.date_debut)
            if hasattr(vehicle, 'date_fin') and vehicle.date_fin:
                if hasattr(vehicle.date_fin, 'strftime'):
                    date_fin_str = vehicle.date_fin.strftime('%d/%m/%Y')
                else:
                    date_fin_str = str(vehicle.date_fin)
            
            # ============================================================
            # CONSTRUCTION DU DICTIONNAIRE vehicle_data (plus aucun accès DB)
            # ============================================================
            
            vehicle_data = {
                # Identification
                'id': getattr(vehicle, 'id', None),
                'immatriculation': getattr(vehicle, 'immatriculation', 'N/A'),
                'chassis': getattr(vehicle, 'chassis', 'N/A'),
                'marque': getattr(vehicle, 'marque', 'N/A'),
                'modele': getattr(vehicle, 'modele', 'N/A'),
                'annee': str(getattr(vehicle, 'annee', 'N/A')),
                
                # Contrat
                'numero_police': getattr(contract, 'numero_police', 'Aucun contrat actif') if contract else 'Aucun contrat actif',
                'date_debut': date_debut_str,
                'date_fin': date_fin_str,
                'prime_totale': getattr(contract, 'prime_totale_ttc', 0.0) if contract else 0.0,
                'montant_paye': getattr(contract, 'montant_paye', 0.0) if contract else 0.0,
                'statut_paiement': getattr(contract, 'statut_paiement', 'NON_PAYE') if contract else 'NON_PAYE',
                
                # Technique
                'energy': getattr(vehicle, 'energie', 'N/A'),
                'usage': getattr(vehicle, 'usage', '0'),
                'places': str(getattr(vehicle, 'places', '5')),
                'zone': getattr(vehicle, 'zone', 'N/A'),
                'categorie': getattr(vehicle, 'categorie', 'N/A'),
                'code_tarif': getattr(vehicle, 'code_tarif', 'N/A'),
                'prime_emise': getattr(vehicle, 'prime_emise', 0),
                'valeur_neuf': getattr(vehicle, 'valeur_neuf', 0),
                'valeur_venale': getattr(vehicle, 'valeur_venale', 0),
                'prime_nette': getattr(vehicle, 'prime_nette', 0),
                'prime_brute': getattr(vehicle, 'prime_brute', 0),
                'réduction': getattr(vehicle, 'reduction', 0),
                'carte_rose': getattr(vehicle, 'carte_rose', 'N/A'),
                'accessoires': getattr(vehicle, 'accessoires', 'N/A'),
                'tva': getattr(vehicle, 'tva', 0),
                'fichier_asac': getattr(vehicle, 'fichier_asac', 'N/A'),
                'vignette': getattr(vehicle, 'vignette', 'N/A'),
                'PTTC': getattr(vehicle, 'pttc', 0),
                'libele_tarif': getattr(vehicle, 'libele_tarif', 'N/A'),
                
                # Propriétaire & Assurance
                'owner': owner_name,
                'compagny': compagny_name,
                'phone': owner_phone,
                'email': owner_email,
                'city': owner_city,
                
                # Garanties (Checkboxes)
                'check_rc': getattr(vehicle, 'check_rc', False),
                'check_dr': getattr(vehicle, 'check_dr', False),
                'check_vb': getattr(vehicle, 'check_vb', False),
                'check_vol': getattr(vehicle, 'check_vol', False),
                'check_in': getattr(vehicle, 'check_in', False),
                'check_bris': getattr(vehicle, 'check_bris', False),
                'check_ar': getattr(vehicle, 'check_ar', False),
                'check_dta': getattr(vehicle, 'check_dta', False),
                'check_ipt': getattr(vehicle, 'check_ipt', False),
                
                # Montants des garanties
                'amt_rc': getattr(vehicle, 'amt_rc', 0),
                'amt_dr': getattr(vehicle, 'amt_dr', 0),
                'amt_vb': getattr(vehicle, 'amt_vb', 0),
                'amt_vol': getattr(vehicle, 'amt_vol', 0),
                'amt_in': getattr(vehicle, 'amt_in', 0),
                'amt_bris': getattr(vehicle, 'amt_bris', 0),
                'amt_ar': getattr(vehicle, 'amt_ar', 0),
                'amt_dta': getattr(vehicle, 'amt_dta', 0),
                'amt_ipt': getattr(vehicle, 'amt_ipt', 0),
                
                # Montants réduits des garanties
                'amt_red_rc': getattr(vehicle, 'amt_red_rc', 0),
                'amt_red_dr': getattr(vehicle, 'amt_red_dr', 0),
                'amt_red_vol': getattr(vehicle, 'amt_red_vol', 0),
                'amt_red_vb': getattr(vehicle, 'amt_red_vb', 0),
                'amt_red_in': getattr(vehicle, 'amt_red_in', 0),
                'amt_red_bris': getattr(vehicle, 'amt_red_bris', 0),
                'amt_red_ar': getattr(vehicle, 'amt_red_ar', 0),
                'amt_red_dta': getattr(vehicle, 'amt_red_dta', 0),
                'amt_red_ipt': getattr(vehicle, 'amt_red_ipt', 0)
            }
            
            # ============================================================
            # AFFICHAGE DE LA VUE (la session peut maintenant être fermée)
            # ============================================================
            
            from .vehicle_detail_view import VehicleDetailView
            from PySide6.QtWidgets import QDialog, QVBoxLayout
            
            detail_dialog = QDialog(self)
            detail_dialog.setWindowTitle(f"Fiche Véhicule : {vehicle_data['immatriculation']}")
            detail_dialog.setMinimumSize(950, 750)
            
            layout = QVBoxLayout(detail_dialog)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Plus besoin de passer la session, toutes les données sont dans vehicle_data
            self.view_details = VehicleDetailView(vehicle_data=vehicle_data, controller=self.controller)
            layout.addWidget(self.view_details)
            
            if hasattr(self.view_details, 'btn_back'):
                self.view_details.btn_back.clicked.connect(detail_dialog.close)
            
            detail_dialog.exec()
            
        except Exception as e:
            print(f"❌ Erreur show_detail_vehicle : {str(e)}")
            import traceback
            traceback.print_exc()
            from PySide6.QtWidgets import QMessageBox
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
                self._start_batch_print(selected_vehicles, selected_documents)

    # Dans contact_detail_view.py

    def _start_batch_print(self, vehicles_data, selected_documents):
        """Lance l'impression groupée via le gestionnaire"""
        from addons.Automobiles.views.batch_print_manager import BatchPrintManager
        
        # Créer le gestionnaire s'il n'existe pas
        if not hasattr(self, 'batch_print_manager'):
            self.batch_print_manager = BatchPrintManager(self.controller, self)
        
        # Démarrer l'impression
        self.batch_print_manager.start_batch_print(vehicles_data, selected_documents)


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