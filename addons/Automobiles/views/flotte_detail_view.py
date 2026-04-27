# fleet_detail_view.py
"""
Vue détaillée d'une flotte avec design moderne et barre de titre personnalisée
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout,
    QMessageBox, QDialog, QTabWidget, QComboBox, QLineEdit, QDateEdit,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate, QSize, QPoint
from PySide6.QtGui import QFont, QColor, QPixmap, QPalette, QLinearGradient, QBrush
from datetime import datetime
import qrcode
from io import BytesIO


class FleetDetailView(QWidget):
    """Vue détaillée d'une flotte avec design moderne"""
    
    def __init__(self, controller, fleet, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.fleet = fleet
        self.parent_window = parent
        
        # Variables pour le redimensionnement
        self.drag_pos = QPoint()
        self.is_maximized = False
        self.normal_geometry = None
        
        # Initialiser les contrôleurs
        self._init_controllers()
        
        # Charger les données
        self.load_fleet_data()
        
        # Configuration de la fenêtre
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setMinimumSize(1200, 850)
        self.resize(1300, 900)
        self.setup_ui()
    
    def _get_style(self):
        """Retourne le style CSS moderne amélioré"""
        return """
            /* Global */
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                color: #1e293b;
            }
            
            /* Card principale */
            #MainCard {
                background: white;
                border-radius: 20px;
                border: 1px solid rgba(0,0,0,0.05);
            }
            
            /* Scroll Area */
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            
            QScrollBar:vertical {
                background: #e2e8f0;
                width: 8px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            
            /* Header Section */
            .HeaderCard {
                background: white;
                border-radius: 24px;
                border: 1px solid rgba(0,0,0,0.05);
            }
            
            /* Info Cards */
            .InfoCard {
                background: white;
                border-radius: 20px;
                border: 1px solid rgba(0,0,0,0.05);
            }
            
            /* Section Titles */
            .SectionTitle {
                font-size: 16px;
                font-weight: 700;
                color: #0f172a;
                padding-bottom: 12px;
                border-bottom: 2px solid #e2e8f0;
                margin-bottom: 20px;
            }
            
            /* Labels */
            .LabelPrimary {
                color: #64748b;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .LabelSecondary {
                color: #1e293b;
                font-size: 14px;
                font-weight: 600;
                margin-top: 4px;
            }
            
            .ValueLarge {
                font-size: 32px;
                font-weight: 800;
                color: #0f172a;
            }
            
            .ValueMedium {
                font-size: 18px;
                font-weight: 700;
                color: #1e293b;
            }
            
            /* Table */
            QTableWidget {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                gridline-color: #f1f5f9;
            }
            
            QTableWidget::item {
                padding: 14px 12px;
                border: none;
            }
            
            QTableWidget::item:selected {
                background: #f3e8ff;
                color: #7c3aed;
            }
            
            QHeaderView::section {
                background-color: #f8fafc;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                padding: 14px 12px;
                font-weight: 600;
                color: #475569;
                font-size: 12px;
            }
            
            /* Badge */
            .Badge {
                background: #f3e8ff;
                color: #7c3aed;
                border-radius: 20px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
            }
            
            .BadgeActive {
                background: #dcfce7;
                color: #15803d;
            }
            
            .BadgeInactive {
                background: #fee2e2;
                color: #dc2626;
            }
            
            /* Stats Card */
            .StatsCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 20px;
            }
            
            .StatsCard QLabel {
                color: white;
            }
            
            /* Tab Widget */
            QTabWidget::pane {
                border: none;
                background: transparent;
                border-radius: 16px;
            }
            
            QTabBar::tab {
                background: #f1f5f9;
                border: none;
                border-radius: 12px;
                padding: 10px 24px;
                margin: 0 6px;
                font-weight: 600;
                font-size: 13px;
                color: #64748b;
            }
            
            QTabBar::tab:selected {
                background: #8b5cf6;
                color: white;
            }
            
            QTabBar::tab:hover:!selected {
                background: #e2e8f0;
                color: #1e293b;
            }
            
            /* KPI Card */
            .KPICard {
                background: white;
                border-radius: 20px;
                border: 1px solid rgba(0,0,0,0.05);
            }
            
            .KPICard:hover {
                border-color: #8b5cf6;
            }
        """
    
    def _init_controllers(self):
        """Initialise les contrôleurs"""
        try:
            if hasattr(self.controller, 'session'):
                from addons.Automobiles.controllers.automobile_controller import VehicleController
                from addons.Automobiles.controllers.contract_controller import ContractController
                
                self.vehicle_ctrl = VehicleController(self.controller.session)
                self.contract_ctrl = ContractController(self.controller.session)
            else:
                self.vehicle_ctrl = None
                self.contract_ctrl = None
        except Exception as e:
            print(f"Erreur initialisation contrôleurs: {e}")
            self.vehicle_ctrl = None
            self.contract_ctrl = None
    
    def load_fleet_data(self):
        """Charge les données de la flotte"""
        try:
            # Récupérer les véhicules de la flotte
            if hasattr(self.fleet, 'vehicles'):
                self.vehicles = list(self.fleet.vehicles) if self.fleet.vehicles else []
            else:
                self.vehicles = []
            
            # Récupérer les contrats de la flotte
            if hasattr(self.fleet, 'contract'):
                self.contracts = [self.fleet.contract] if self.fleet.contract else []
            else:
                self.contracts = []
            
            # Calculer les statistiques
            self.total_vehicles = len(self.vehicles)
            self.total_contracts = len(self.contracts)
            
            # Calculer le total des primes
            self.total_premium = 0
            for vehicle in self.vehicles:
                if hasattr(vehicle, 'prime_nette'):
                    self.total_premium += float(vehicle.prime_nette or 0)
            
            # Récupérer le nom de la compagnie
            self.compagnie_nom = '—'
            if hasattr(self.fleet, 'compagnie') and self.fleet.compagnie:
                self.compagnie_nom = self.fleet.compagnie.nom
            elif hasattr(self.fleet, 'assureur') and self.fleet.assureur and hasattr(self.controller, 'session'):
                try:
                    from addons.Automobiles.models import Compagnie
                    compagnie = self.controller.session.query(Compagnie).get(self.fleet.assureur)
                    if compagnie:
                        self.compagnie_nom = compagnie.nom
                except:
                    pass
            
            # Récupérer le nom du propriétaire
            self.owner_name = '—'
            if hasattr(self.fleet, 'owner') and self.fleet.owner:
                owner = self.fleet.owner
                self.owner_name = f"{getattr(owner, 'nom', '')} {getattr(owner, 'prenom', '')}".strip()
                self.owner_phone = getattr(owner, 'telephone', '—')
                self.owner_email = getattr(owner, 'email', '—')
            
        except Exception as e:
            print(f"Erreur chargement données flotte: {e}")
            self.vehicles = []
            self.contracts = []
            self.total_vehicles = 0
            self.total_premium = 0
    
    def setup_ui(self):
        """Configure l'interface principale"""
        self.setStyleSheet(self._get_style())
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        
        # Carte principale avec ombre
        main_card = QFrame()
        main_card.setObjectName("MainCard")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 8)
        main_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(main_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        # Barre de titre personnalisée
        card_layout.addWidget(self.create_title_bar())
        
        # Conteneur du contenu
        content_widget = QWidget()
        content_widget.setStyleSheet("background: #f0f2f5;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(24, 24, 24, 32)
        content_layout.setSpacing(24)
        
        # En-tête
        content_layout.addWidget(self.create_header())
        
        # Création du TabWidget
        self.tab_widget = QTabWidget()
        
        self.tab_widget.addTab(self.create_info_tab(), "📋 Informations")
        self.tab_widget.addTab(self.create_vehicles_tab(), "🚗 Véhicules")
        self.tab_widget.addTab(self.create_stats_tab(), "📊 Statistiques")
        self.tab_widget.addTab(self.create_documents_tab(), "📁 Documents")
        
        content_layout.addWidget(self.tab_widget)
        
        card_layout.addWidget(content_widget)
        main_layout.addWidget(main_card)
    
    def create_title_bar(self):
        """Crée une barre de titre personnalisée avec boutons"""
        title_bar = QFrame()
        title_bar.setFixedHeight(65)
        title_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
            }
        """)
        
        # Layout de la barre de titre
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(24, 0, 20, 0)
        
        # Titre et icône
        title_icon = QLabel("🚛")
        title_icon.setStyleSheet("font-size: 22px; background: transparent;")
        
        fleet_name = getattr(self.fleet, 'nom_flotte', 'Flotte')
        title_text = QLabel(f"Détails de la flotte - {fleet_name}")
        title_text.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: white;
            background: transparent;
            letter-spacing: 0.5px;
        """)
        
        # Espaceur
        title_layout.addWidget(title_icon)
        title_layout.addSpacing(12)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        # Bouton minimiser
        self.btn_minimize = QPushButton("─")
        self.btn_minimize.setFixedSize(34, 34)
        self.btn_minimize.setCursor(Qt.PointingHandCursor)
        self.btn_minimize.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.15);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.3);
            }
        """)
        self.btn_minimize.clicked.connect(self.showMinimized)
        
        # Bouton maximiser/restaurer
        self.btn_maximize = QPushButton("□")
        self.btn_maximize.setFixedSize(34, 34)
        self.btn_maximize.setCursor(Qt.PointingHandCursor)
        self.btn_maximize.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.15);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.3);
            }
        """)
        self.btn_maximize.clicked.connect(self.toggle_maximize)
        
        # Bouton fermer
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(34, 34)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.15);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #ef4444;
            }
        """)
        self.btn_close.clicked.connect(self.close_window)
        
        title_layout.addWidget(self.btn_minimize)
        title_layout.addSpacing(6)
        title_layout.addWidget(self.btn_maximize)
        title_layout.addSpacing(6)
        title_layout.addWidget(self.btn_close)
        
        # Permettre de déplacer la fenêtre en cliquant sur la barre de titre
        title_bar.mousePressEvent = self.title_bar_mouse_press
        title_bar.mouseMoveEvent = self.title_bar_mouse_move
        
        return title_bar
    
    def title_bar_mouse_press(self, event):
        """Gère le clic sur la barre de titre pour déplacer"""
        if event.button() == Qt.LeftButton and not self.is_maximized:
            self.drag_pos = event.globalPosition().toPoint()
    
    def title_bar_mouse_move(self, event):
        """Gère le déplacement de la fenêtre"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_pos') and not self.is_maximized:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()
    
    def toggle_maximize(self):
        """Bascule entre mode normal et plein écran"""
        if self.is_maximized:
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.btn_maximize.setText("□")
            self.is_maximized = False
        else:
            self.normal_geometry = self.geometry()
            # Obtenir la géométrie de l'écran
            screen_geometry = self.screen().availableGeometry()
            self.setGeometry(screen_geometry)
            self.btn_maximize.setText("❐")
            self.is_maximized = True
    
    def close_window(self):
        """Ferme la fenêtre"""
        # Si la vue est dans un dialogue parent, fermer le dialogue
        parent = self.parent()
        while parent:
            if isinstance(parent, QDialog):
                parent.close()
                return
            parent = parent.parent()
        # Sinon, fermer la fenêtre
        self.close()
    
    def create_header(self):
        """Crée l'en-tête avec les informations principales"""
        header_card = QFrame()
        header_card.setProperty("class", "HeaderCard")
        
        # Ajouter une ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        header_card.setGraphicsEffect(shadow)
        
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(28, 24, 28, 24)
        header_layout.setSpacing(30)
        
        # Left side - Fleet info
        left_info = QVBoxLayout()
        left_info.setSpacing(10)
        
        nom_lbl = QLabel(getattr(self.fleet, 'nom_flotte', 'N/A'))
        nom_lbl.setStyleSheet("font-size: 28px; font-weight: 800; color: #0f172a;")
        
        code_lbl = QLabel(f"Code: {getattr(self.fleet, 'code_flotte', 'N/A')}")
        code_lbl.setStyleSheet("font-size: 14px; color: #64748b;")
        
        # Badge for status
        statut = getattr(self.fleet, 'statut', 'Actif')
        status_badge = QLabel(statut)
        if statut.upper() == "ACTIF":
            status_badge.setProperty("class", "Badge BadgeActive")
        elif statut.upper() == "INACTIF":
            status_badge.setProperty("class", "Badge BadgeInactive")
        else:
            status_badge.setProperty("class", "Badge")
        
        left_info.addWidget(nom_lbl)
        left_info.addWidget(code_lbl)
        left_info.addWidget(status_badge)
        
        # Middle - Period info (carte dédiée)
        middle_card = QFrame()
        middle_card.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 16px;
                padding: 12px 20px;
            }
        """)
        middle_info = QVBoxLayout(middle_card)
        middle_info.setSpacing(6)
        
        date_debut = self._format_date(getattr(self.fleet, 'date_debut', ''))
        date_fin = self._format_date(getattr(self.fleet, 'date_fin', ''))
        
        period_lbl = QLabel("PÉRIODE DU CONTRAT")
        period_lbl.setProperty("class", "LabelPrimary")
        
        dates_lbl = QLabel(f"{date_debut} → {date_fin}")
        dates_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #1e293b;")
        
        validity = self._calculate_validity()
        validity_color = "#10b981" if "Valide" in validity else "#ef4444"
        validity_lbl = QLabel(validity)
        validity_lbl.setStyleSheet(f"font-size: 12px; color: {validity_color}; font-weight: 600;")
        
        middle_info.addWidget(period_lbl)
        middle_info.addWidget(dates_lbl)
        middle_info.addWidget(validity_lbl)
        
        # Right side - Company info
        right_card = QFrame()
        right_card.setStyleSheet("""
            QFrame {
                background: #f3e8ff;
                border-radius: 16px;
                padding: 12px 20px;
            }
        """)
        right_info = QVBoxLayout(right_card)
        right_info.setSpacing(6)
        
        company_lbl = QLabel("COMPAGNIE D'ASSURANCE")
        company_lbl.setProperty("class", "LabelPrimary")
        
        company_name = QLabel(self.compagnie_nom)
        company_name.setStyleSheet("font-size: 16px; font-weight: 800; color: #7c3aed;")
        
        right_info.addWidget(company_lbl)
        right_info.addWidget(company_name)
        
        # Action buttons
        action_buttons = QHBoxLayout()
        action_buttons.setSpacing(12)
        
        actions = [
            ("✏️ Modifier", "edit", "#8b5cf6"),
            ("🔄 Renouveler", "renew", "#10b981"),
            ("📧 Email", "email", "#3b82f6"),
            ("📥 PDF", "export", "#f59e0b")
        ]
        
        self.action_buttons = {}
        for label, action, color in actions:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(42)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 10px 18px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: {color}dd;
                }}
                QPushButton:pressed {{
                    background: {color}bb;
                }}
            """)
            self.action_buttons[action] = btn
            action_buttons.addWidget(btn)
        
        header_layout.addLayout(left_info, 2)
        header_layout.addWidget(middle_card, 1)
        header_layout.addWidget(right_card, 1)
        header_layout.addLayout(action_buttons, 2)
        
        return header_card
    
    # ==================== MÉTHODES DES ONGLETS ====================
    
    def create_info_tab(self):
        """Onglet des informations générales"""
        tab = QWidget()
        
        # Scroll area pour le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 16, 0, 16)
        container_layout.setSpacing(24)
        
        # Carte d'informations détaillées
        container_layout.addWidget(self.create_info_card())
        
        # QR Code
        container_layout.addWidget(self.create_qrcode_section())
        
        container_layout.addStretch()
        
        scroll.setWidget(container)
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
        return tab
    
    def create_info_card(self):
        """Crée la carte d'informations détaillées"""
        info_card = QFrame()
        info_card.setProperty("class", "InfoCard")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        info_card.setGraphicsEffect(shadow)
        
        info_layout = QGridLayout(info_card)
        info_layout.setContentsMargins(28, 24, 28, 24)
        info_layout.setHorizontalSpacing(60)
        info_layout.setVerticalSpacing(28)
        
        # Section 1: Informations générales
        general_title = QLabel("📋 INFORMATIONS GÉNÉRALES")
        general_title.setStyleSheet("font-weight: 800; font-size: 13px; color: #7c3aed; letter-spacing: 0.5px;")
        info_layout.addWidget(general_title, 0, 0, 1, 2)
        
        general_info = [
            ("Nom de la flotte", getattr(self.fleet, 'nom_flotte', '—'), 1, 0),
            ("Code flotte", getattr(self.fleet, 'code_flotte', '—'), 1, 1),
            ("Type de gestion", getattr(self.fleet, 'type_gestion', '—'), 2, 0),
            ("Remise", f"{getattr(self.fleet, 'remise_flotte', 0)}%", 2, 1),
            ("Statut", getattr(self.fleet, 'statut', '—'), 3, 0),
            ("Date création", self._format_date(getattr(self.fleet, 'created_at', '')), 3, 1),
        ]
        
        for label, value, row, col in general_info:
            vbox = QVBoxLayout()
            vbox.setSpacing(6)
            lbl = QLabel(label)
            lbl.setProperty("class", "LabelPrimary")
            val = QLabel(str(value) if value else '—')
            val.setProperty("class", "LabelSecondary")
            vbox.addWidget(lbl)
            vbox.addWidget(val)
            info_layout.addLayout(vbox, row, col)
        
        # Section 2: Propriétaire
        owner_title = QLabel("👤 PROPRIÉTAIRE")
        owner_title.setStyleSheet("font-weight: 800; font-size: 13px; color: #7c3aed; letter-spacing: 0.5px; margin-top: 8px;")
        info_layout.addWidget(owner_title, 4, 0, 1, 2)
        
        owner_info = [
            ("Nom du client", self.owner_name, 5, 0),
            ("Téléphone", getattr(self, 'owner_phone', '—'), 5, 1),
            ("Email", getattr(self, 'owner_email', '—'), 6, 0),
        ]
        
        for label, value, row, col in owner_info:
            vbox = QVBoxLayout()
            vbox.setSpacing(6)
            lbl = QLabel(label)
            lbl.setProperty("class", "LabelPrimary")
            val = QLabel(str(value) if value else '—')
            val.setProperty("class", "LabelSecondary")
            val.setWordWrap(True)
            vbox.addWidget(lbl)
            vbox.addWidget(val)
            info_layout.addLayout(vbox, row, col)
        
        # Section 3: Assureur
        insurance_title = QLabel("🏦 ASSURANCE")
        insurance_title.setStyleSheet("font-weight: 800; font-size: 13px; color: #7c3aed; letter-spacing: 0.5px; margin-top: 8px;")
        info_layout.addWidget(insurance_title, 7, 0, 1, 2)
        
        insurance_info = [
            ("Compagnie", self.compagnie_nom, 8, 0),
            ("Date début", self._format_date(getattr(self.fleet, 'date_debut', '')), 8, 1),
            ("Date fin", self._format_date(getattr(self.fleet, 'date_fin', '')), 9, 0),
        ]
        
        for label, value, row, col in insurance_info:
            vbox = QVBoxLayout()
            vbox.setSpacing(6)
            lbl = QLabel(label)
            lbl.setProperty("class", "LabelPrimary")
            val = QLabel(str(value) if value else '—')
            val.setProperty("class", "LabelSecondary")
            val.setWordWrap(True)
            vbox.addWidget(lbl)
            vbox.addWidget(val)
            info_layout.addLayout(vbox, row, col)
        
        # Observations
        obs_title = QLabel("📝 OBSERVATIONS")
        obs_title.setStyleSheet("font-weight: 800; font-size: 13px; color: #7c3aed; letter-spacing: 0.5px; margin-top: 8px;")
        info_layout.addWidget(obs_title, 10, 0, 1, 2)
        
        obs_frame = QFrame()
        obs_frame.setStyleSheet("background: #f8fafc; border-radius: 12px; padding: 12px;")
        obs_layout = QVBoxLayout(obs_frame)
        
        obs_text = getattr(self.fleet, 'observations', '—')
        obs_lbl = QLabel(str(obs_text) if obs_text else 'Aucune observation')
        obs_lbl.setWordWrap(True)
        obs_lbl.setStyleSheet("color: #475569; font-size: 13px;")
        obs_layout.addWidget(obs_lbl)
        
        info_layout.addWidget(obs_frame, 11, 0, 1, 2)
        
        return info_card
    
    def create_qrcode_section(self):
        """Crée un QR code pour accès rapide"""
        qr_card = QFrame()
        qr_card.setProperty("class", "InfoCard")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        qr_card.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(qr_card)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(20)
        
        # Générer QR code
        fleet_id = getattr(self.fleet, 'id', '')
        data_str = f"https://amsassurance.com/fleet/{fleet_id}"
        
        try:
            qr = qrcode.QRCode(box_size=4, border=1)
            qr.add_data(data_str)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#8b5cf6", back_color="white")
            
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            qr_label = QLabel()
            qr_label.setPixmap(pixmap)
            qr_label.setStyleSheet("background: white; border-radius: 12px; padding: 8px;")
        except:
            qr_label = QLabel("🔲 QR Code")
            qr_label.setStyleSheet("font-size: 48px; background: white; border-radius: 12px; padding: 8px;")
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        
        title_lbl = QLabel("🔗 ACCÈS RAPIDE")
        title_lbl.setStyleSheet("font-weight: 800; font-size: 16px; color: #0f172a;")
        
        desc_lbl = QLabel("Scannez ce QR code pour accéder à la fiche flotte en ligne")
        desc_lbl.setStyleSheet("font-size: 13px; color: #64748b;")
        
        info_layout.addWidget(title_lbl)
        info_layout.addWidget(desc_lbl)
        
        layout.addWidget(qr_label)
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return qr_card
    
    def create_vehicles_tab(self):
        """Onglet des véhicules de la flotte"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(24)
        
        # En-tête avec statistiques
        layout.addWidget(self.create_vehicles_stats_bar())
        
        # Tableau des véhicules
        layout.addWidget(self.create_vehicles_table())
        
        # Section des garanties cumulées
        layout.addWidget(self.create_guarantees_summary())
        
        layout.addStretch()
        return tab
    
    def create_vehicles_stats_bar(self):
        """Crée la barre de statistiques des véhicules"""
        stats_card = QFrame()
        stats_card.setProperty("class", "StatsCard")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        stats_card.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(stats_card)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(40)
        
        stats = [
            ("🚗", "VÉHICULES", str(self.total_vehicles), "dans la flotte"),
            ("💰", "PRIME TOTALE", f"{self.total_premium:,.0f}".replace(",", " "), "FCFA"),
            ("📊", "PRIME MOYENNE", f"{self.total_premium/self.total_vehicles:,.0f}".replace(",", " ") if self.total_vehicles > 0 else "0", "FCFA/véhicule"),
        ]
        
        for icon, title, value, unit in stats:
            stat_widget = QVBoxLayout()
            stat_widget.setSpacing(6)
            
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 28px;")
            
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet("font-size: 11px; font-weight: 700; letter-spacing: 1px; opacity: 0.8; color: black;")
            
            value_lbl = QLabel(value)
            value_lbl.setStyleSheet("font-size: 32px; font-weight: 800; color: black;")
            
            unit_lbl = QLabel(unit)
            unit_lbl.setStyleSheet("font-size: 12px; opacity: 0.7; color: black;")
            
            stat_widget.addWidget(icon_lbl)
            stat_widget.addWidget(title_lbl)
            stat_widget.addWidget(value_lbl)
            stat_widget.addWidget(unit_lbl)
            
            layout.addLayout(stat_widget)
            layout.addStretch()
        
        return stats_card
    
    def create_vehicles_table(self):
        """Crée le tableau des véhicules"""
        card = QFrame()
        card.setProperty("class", "InfoCard")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        title = QLabel("📋 LISTE DES VÉHICULES")
        title.setProperty("class", "SectionTitle")
        layout.addWidget(title)
        
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Immatriculation", "Marque", "Modèle", "Année", "Énergie", 
            "Prime (FCFA)", "Statut"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setShowGrid(False)
        table.verticalHeader().setVisible(False)
        table.setFocusPolicy(Qt.NoFocus)
        
        total_prime = 0
        
        for row, vehicle in enumerate(self.vehicles):
            table.insertRow(row)
            table.setRowHeight(row, 50)
            
            immatriculation = getattr(vehicle, 'immatriculation', '—')
            marque = getattr(vehicle, 'marque', '—')
            modele = getattr(vehicle, 'modele', '—')
            annee = str(getattr(vehicle, 'annee', '—'))
            energie = getattr(vehicle, 'energie', '—')
            prime = float(getattr(vehicle, 'prime_nette', 0) or 0)
            total_prime += prime
            
            statut = getattr(vehicle, 'statut', 'En circulation')
            
            table.setItem(row, 0, QTableWidgetItem(immatriculation))
            table.setItem(row, 1, QTableWidgetItem(marque))
            table.setItem(row, 2, QTableWidgetItem(modele))
            table.setItem(row, 3, QTableWidgetItem(annee))
            table.setItem(row, 4, QTableWidgetItem(energie))
            
            prime_item = QTableWidgetItem(f"{prime:,.0f}".replace(",", " "))
            prime_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 5, prime_item)
            
            status_item = QTableWidgetItem(statut)
            if statut.lower() in ["actif", "en circulation"]:
                status_item.setForeground(QColor("#10b981"))
            else:
                status_item.setForeground(QColor("#ef4444"))
            table.setItem(row, 6, status_item)
        
        # Ajuster la hauteur
        row_height = 50
        header_height = 45
        table_height = min(400, header_height + len(self.vehicles) * row_height + 20) if self.vehicles else 100
        table.setFixedHeight(table_height)
        
        layout.addWidget(table)
        
        # Ligne de total
        total_frame = QFrame()
        total_frame.setStyleSheet("background: #f8fafc; border-radius: 12px;")
        total_layout = QHBoxLayout(total_frame)
        total_layout.setContentsMargins(20, 12, 20, 12)
        
        total_lbl = QLabel(f"Total: {self.total_vehicles} véhicule(s)")
        total_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        
        prime_lbl = QLabel(f"Prime totale: {total_prime:,.0f} FCFA".replace(",", " "))
        prime_lbl.setStyleSheet("font-weight: 800; color: #8b5cf6; font-size: 16px;")
        
        total_layout.addWidget(total_lbl)
        total_layout.addStretch()
        total_layout.addWidget(prime_lbl)
        
        layout.addWidget(total_frame)
        
        return card
    
    def create_guarantees_summary(self):
        """Crée le résumé des garanties cumulées"""
        card = QFrame()
        card.setProperty("class", "InfoCard")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        title = QLabel("🛡️ GARANTIES CUMULÉES")
        title.setProperty("class", "SectionTitle")
        layout.addWidget(title)
        
        # Récupérer les totaux des garanties
        garanties_data = [
            ("Responsabilité Civile", getattr(self.fleet, 'total_rc', 0) or 0, "#3b82f6"),
            ("Défense et Recours", getattr(self.fleet, 'total_dr', 0) or 0, "#10b981"),
            ("Vol du véhicule", getattr(self.fleet, 'total_vol', 0) or 0, "#f59e0b"),
            ("Vol à Main Armée", getattr(self.fleet, 'total_vb', 0) or 0, "#ef4444"),
            ("Incendie", getattr(self.fleet, 'total_in', 0) or 0, "#8b5cf6"),
            ("Bris de Glaces", getattr(self.fleet, 'total_bris', 0) or 0, "#06b6d4"),
            ("Assistance Panne", getattr(self.fleet, 'total_ar', 0) or 0, "#84cc16"),
            ("Dommages Tous Accidents", getattr(self.fleet, 'total_dta', 0) or 0, "#ec4899"),
        ]
        
        total_garanties = sum(amount for _, amount, _ in garanties_data)
        
        # Grille des garanties
        grid = QGridLayout()
        grid.setSpacing(12)
        
        for i, (name, amount, color) in enumerate(garanties_data):
            # Conteneur
            item_frame = QFrame()
            item_frame.setStyleSheet(f"""
                QFrame {{
                    background: {color}10;
                    border-radius: 12px;
                    border-left: 3px solid {color};
                }}
            """)
            item_layout = QVBoxLayout(item_frame)
            item_layout.setContentsMargins(16, 12, 16, 12)
            item_layout.setSpacing(6)
            
            # Nom
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {color};")
            
            # Montant
            amount_lbl = QLabel(f"{amount:,.0f}".replace(",", " "))
            amount_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #1e293b;")
            
            # Pourcentage
            percentage = (amount / total_garanties * 100) if total_garanties > 0 else 0
            percent_lbl = QLabel(f"{percentage:.1f}% du total")
            percent_lbl.setStyleSheet("font-size: 10px; color: #64748b;")
            
            item_layout.addWidget(name_lbl)
            item_layout.addWidget(amount_lbl)
            item_layout.addWidget(percent_lbl)
            
            grid.addWidget(item_frame, i // 2, i % 2)
        
        layout.addLayout(grid)
        
        # Total
        total_frame = QFrame()
        total_frame.setStyleSheet("background: #f3e8ff; border-radius: 12px;")
        total_layout = QHBoxLayout(total_frame)
        total_layout.setContentsMargins(20, 16, 20, 16)
        
        total_label = QLabel("TOTAL DES COUVERTURES")
        total_label.setStyleSheet("font-weight: 700; color: #7c3aed;")
        
        total_value = QLabel(f"{total_garanties:,.0f} FCFA".replace(",", " "))
        total_value.setStyleSheet("font-weight: 800; color: #7c3aed; font-size: 20px;")
        
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(total_value)
        
        layout.addWidget(total_frame)
        
        return card
    
    def create_stats_tab(self):
        """Onglet des statistiques"""
        tab = QWidget()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 16, 0, 16)
        container_layout.setSpacing(24)
        
        container_layout.addWidget(self.create_stats_header())
        container_layout.addWidget(self.create_kpi_container())
        container_layout.addWidget(self.create_stats_chart())
        container_layout.addWidget(self.create_performance_table())
        
        container_layout.addStretch()
        
        scroll.setWidget(container)
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
        return tab
    
    def create_stats_header(self):
        """Crée l'en-tête des statistiques"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e293b, stop:1 #0f172a);
                border-radius: 20px;
            }
        """)
        header.setMinimumHeight(100)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        header.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(28, 20, 28, 20)
        
        title_section = QVBoxLayout()
        title = QLabel("📊 TABLEAU DE BORD FLOTTE")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: 800; letter-spacing: 1px;")
        
        subtitle = QLabel(f"Analyse des performances - {self.total_vehicles} véhicule(s)")
        subtitle.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 13px;")
        
        title_section.addWidget(title)
        title_section.addWidget(subtitle)
        
        date_section = QVBoxLayout()
        date_section.setAlignment(Qt.AlignRight)
        
        date_lbl = QLabel(datetime.now().strftime("%d/%m/%Y"))
        date_lbl.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 13px; font-weight: 500;")
        
        rapport_lbl = QLabel("Rapport périodique")
        rapport_lbl.setStyleSheet("color: #fbbf24; font-size: 12px; font-weight: 700;")
        
        date_section.addWidget(rapport_lbl)
        date_section.addWidget(date_lbl)
        
        layout.addLayout(title_section)
        layout.addStretch()
        layout.addLayout(date_section)
        
        return header
    
    def create_kpi_container(self):
        """Crée le conteneur des cartes KPI"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # KPI 1: Nombre de véhicules
        kpi1 = self._create_kpi_card(
            title="🚗 VÉHICULES",
            value=str(self.total_vehicles),
            subtitle="dans la flotte",
            color="#8b5cf6"
        )
        layout.addWidget(kpi1, 1)
        
        # KPI 2: Prime totale
        kpi2 = self._create_kpi_card(
            title="💰 PRIME TOTALE",
            value=f"{self.total_premium/1000:.1f}k" if self.total_premium >= 1000 else f"{self.total_premium:,.0f}".replace(",", " "),
            subtitle="FCFA / an",
            color="#10b981"
        )
        layout.addWidget(kpi2, 1)
        
        # KPI 3: Prime moyenne
        avg_premium = self.total_premium / self.total_vehicles if self.total_vehicles > 0 else 0
        kpi3 = self._create_kpi_card(
            title="📊 PRIME MOYENNE",
            value=f"{avg_premium/1000:.1f}k" if avg_premium >= 1000 else f"{avg_premium:,.0f}".replace(",", " "),
            subtitle="FCFA / véhicule",
            color="#f59e0b"
        )
        layout.addWidget(kpi3, 1)
        
        # KPI 4: Taux de couverture
        coverage_rate = self._calculate_coverage_rate()
        kpi4 = self._create_kpi_card(
            title="🛡️ COUVERTURE",
            value=f"{coverage_rate}%",
            subtitle="taux moyen",
            color="#3b82f6"
        )
        layout.addWidget(kpi4, 1)
        
        return container
    
    def _create_kpi_card(self, title, value, subtitle, color):
        """Crée une carte KPI"""
        card = QFrame()
        card.setProperty("class", "KPICard")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 11px; font-weight: 800; color: {color}; letter-spacing: 0.5px;")
        
        value_lbl = QLabel(str(value))
        value_lbl.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {color};")
        
        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setStyleSheet("font-size: 11px; color: #94a3b8;")
        
        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        layout.addWidget(subtitle_lbl)
        
        return card
    
    def create_stats_chart(self):
        """Crée le graphique des statistiques"""
        card = QFrame()
        card.setProperty("class", "InfoCard")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)
        
        title = QLabel("📈 DISTRIBUTION PAR MARQUE")
        title.setProperty("class", "SectionTitle")
        layout.addWidget(title)
        
        # Compter les véhicules par marque
        marque_counts = {}
        for vehicle in self.vehicles:
            marque = getattr(vehicle, 'marque', 'Autre')
            if not marque or marque == '—':
                marque = 'Autre'
            marque_counts[marque] = marque_counts.get(marque, 0) + 1
        
        if marque_counts:
            max_count = max(marque_counts.values())
            
            for marque, count in sorted(marque_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / self.total_vehicles * 100) if self.total_vehicles > 0 else 0
                bar_width = int((count / max_count) * 200) if max_count > 0 else 50
                
                bar_widget = QWidget()
                bar_layout = QHBoxLayout(bar_widget)
                bar_layout.setContentsMargins(0, 10, 0, 10)
                bar_layout.setSpacing(15)
                
                name_lbl = QLabel(marque)
                name_lbl.setFixedWidth(150)
                name_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #1e293b;")
                
                bar_container = QFrame()
                bar_container.setStyleSheet("background: #f1f5f9; border-radius: 12px;")
                bar_container.setFixedHeight(30)
                
                bar = QFrame()
                bar.setStyleSheet(f"""
                    QFrame {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #8b5cf6, stop:1 #a78bfa);
                        border-radius: 12px;
                    }}
                """)
                bar.setFixedSize(bar_width, 30)
                
                # Layout pour la barre
                bar_layout_inner = QHBoxLayout(bar_container)
                bar_layout_inner.setContentsMargins(0, 0, 0, 0)
                bar_layout_inner.addWidget(bar)
                bar_layout_inner.addStretch()
                
                count_lbl = QLabel(f"{count} véhicule(s) ({percentage:.1f}%)")
                count_lbl.setFixedWidth(150)
                count_lbl.setStyleSheet("font-size: 12px; color: #64748b; font-weight: 500;")
                
                bar_layout.addWidget(name_lbl)
                bar_layout.addWidget(bar_container, 1)
                bar_layout.addWidget(count_lbl)
                
                layout.addWidget(bar_widget)
        else:
            empty_lbl = QLabel("Aucune donnée disponible")
            empty_lbl.setStyleSheet("color: #94a3b8; padding: 40px; text-align: center;")
            empty_lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty_lbl)
        
        return card
    
    def create_performance_table(self):
        """Crée le tableau des performances"""
        card = QFrame()
        card.setProperty("class", "InfoCard")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        title = QLabel("📋 INDICATEURS DE PERFORMANCE")
        title.setProperty("class", "SectionTitle")
        layout.addWidget(title)
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Indicateur", "Valeur", "Statut"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setFocusPolicy(Qt.NoFocus)
        
        performances = [
            ("Taille de la flotte", f"{self.total_vehicles} véhicules", self._get_status("size", self.total_vehicles)),
            ("Prime totale annuelle", f"{self.total_premium:,.0f} FCFA".replace(",", " "), self._get_status("premium", self.total_premium)),
            ("Prime moyenne par véhicule", f"{self.total_premium/self.total_vehicles:,.0f} FCFA".replace(",", " ") if self.total_vehicles > 0 else "0", self._get_status("avg_premium", self.total_premium/self.total_vehicles if self.total_vehicles > 0 else 0)),
            ("Taux de couverture moyen", f"{self._calculate_coverage_rate()}%", self._get_status("coverage", self._calculate_coverage_rate())),
        ]
        
        for row, (indicator, value, status) in enumerate(performances):
            table.insertRow(row)
            table.setRowHeight(row, 55)
            
            item_indicator = QTableWidgetItem(indicator)
            item_indicator.setFont(QFont("Segoe UI", 12))
            table.setItem(row, 0, item_indicator)
            
            item_value = QTableWidgetItem(str(value))
            item_value.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
            table.setItem(row, 1, item_value)
            
            if status == "Excellent":
                status_color = "#10b981"
                status_bg = "#dcfce7"
            elif status == "Bon":
                status_color = "#f59e0b"
                status_bg = "#fef3c7"
            else:
                status_color = "#64748b"
                status_bg = "#f1f5f9"
            
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(status_color))
            status_item.setBackground(QColor(status_bg))
            status_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            status_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 2, status_item)
        
        table.setFixedHeight(250)
        layout.addWidget(table)
        
        return card
            
            # Statut avec badge

        # ==================== MÉTHODES UTILITAIRES ====================
    
    def _format_date(self, date):
        """Formate une date"""
        if date and date != 'N/A' and date != '':
            try:
                if hasattr(date, 'strftime'):
                    return date.strftime("%d/%m/%Y")
                return str(date)
            except:
                return str(date)
        return "Non définie"
    
    def _calculate_validity(self):
        """Calcule la validité du contrat"""
        try:
            date_fin = getattr(self.fleet, 'date_fin', None)
            if date_fin:
                from datetime import date
                if isinstance(date_fin, date):
                    if date_fin < date.today():
                        return "Contrat expiré"
                    else:
                        days_left = (date_fin - date.today()).days
                        return f"Valide (encore {days_left} jours)"
        except:
            pass
        return "Statut inconnu"
    
    def _calculate_coverage_rate(self):
        """Calcule le taux de couverture moyen de la flotte"""
        if not self.vehicles:
            return 0
        
        garanties = ['rc', 'dr', 'vol', 'vb', 'in', 'bris', 'ar', 'dta']
        total_coverage = 0
        
        for vehicle in self.vehicles:
            coverage = 0
            for g in garanties:
                value = getattr(vehicle, f'amt_{g}', 0)
                if value and value > 0:
                    coverage += 1
            total_coverage += (coverage / len(garanties)) * 100
        
        return int(total_coverage / len(self.vehicles)) if self.vehicles else 0
    
    def _get_status(self, metric, value):
        """Retourne le statut selon la métrique"""
        if metric == "size":
            if value >= 10:
                return "Excellent"
            elif value >= 5:
                return "Bon"
            else:
                return "Standard"
        elif metric == "premium":
            if value >= 10000000:
                return "Excellent"
            elif value >= 5000000:
                return "Bon"
            else:
                return "Standard"
        elif metric == "avg_premium":
            if value >= 1000000:
                return "Excellent"
            elif value >= 500000:
                return "Bon"
            else:
                return "Standard"
        elif metric == "coverage":
            if value >= 80:
                return "Excellent"
            elif value >= 60:
                return "Bon"
            else:
                return "À améliorer"
        else:
            return "Standard"
    
    def _create_legend_dot(self, text, color):
        """Crée une légende avec point coloré"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {color}; border-radius: 4px;")
        
        label = QLabel(text)
        label.setStyleSheet("font-size: 10px; color: #64748b;")
        
        layout.addWidget(dot)
        layout.addWidget(label)
        
        return widget
    
    def create_documents_tab(self):
        """Onglet des documents"""
        tab = QWidget()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 16, 0, 16)
        container_layout.setSpacing(24)
        
        # Documents de la flotte
        container_layout.addWidget(self.create_fleet_documents())
        
        # Contacts utiles
        container_layout.addWidget(self.create_contacts_section())
        
        container_layout.addStretch()
        
        scroll.setWidget(container)
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
        return tab
    
    def create_fleet_documents(self):
        """Crée la section des documents de la flotte"""
        card = QFrame()
        card.setProperty("class", "InfoCard")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        title = QLabel("📁 DOCUMENTS")
        title.setProperty("class", "SectionTitle")
        layout.addWidget(title)
        
        docs_grid = QGridLayout()
        docs_grid.setSpacing(12)
        
        documents = [
            ("📄 Contrat de flotte", "contrat_flotte.pdf", "1.5 MB"),
            ("📋 Conditions générales", "conditions_flotte.pdf", "2.8 MB"),
            ("📝 Avenant flotte", "avenant_flotte.pdf", "0.6 MB"),
            ("💳 Relevé global", "releve_global.pdf", "0.9 MB"),
            ("🛡️ Attestation flotte", "attestation_flotte.pdf", "0.5 MB"),
            ("📊 Rapport annuel", "rapport_annuel.pdf", "2.1 MB")
        ]
        
        self.doc_buttons = {}
        
        for i, (name, file, size) in enumerate(documents):
            btn = QPushButton()
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(70)
            btn.setStyleSheet("""
                QPushButton {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    text-align: left;
                }
                QPushButton:hover {
                    background: #f1f5f9;
                    border-color: #8b5cf6;
                }
            """)
            
            btn_layout = QHBoxLayout(btn)
            btn_layout.setContentsMargins(16, 12, 16, 12)
            btn_layout.setSpacing(12)
            
            icon_lbl = QLabel(name.split()[0])
            icon_lbl.setStyleSheet("font-size: 24px;")
            
            info_layout = QVBoxLayout()
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #1e293b;")
            
            size_lbl = QLabel(f"📎 {size} • PDF")
            size_lbl.setStyleSheet("font-size: 10px; color: #64748b;")
            
            info_layout.addWidget(name_lbl)
            info_layout.addWidget(size_lbl)
            
            download_icon = QLabel("📥")
            download_icon.setStyleSheet("font-size: 18px; color: #8b5cf6;")
            
            btn_layout.addWidget(icon_lbl)
            btn_layout.addLayout(info_layout, 1)
            btn_layout.addWidget(download_icon)
            
            self.doc_buttons[file] = btn
            docs_grid.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(docs_grid)
        
        return card
    
    def create_contacts_section(self):
        """Crée la section des contacts utiles"""
        card = QFrame()
        card.setProperty("class", "InfoCard")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        title = QLabel("📞 CONTACTS UTILES")
        title.setProperty("class", "SectionTitle")
        layout.addWidget(title)
        
        contacts_grid = QGridLayout()
        contacts_grid.setSpacing(15)
        
        contacts = [
            ("👤 Agent commercial", self.owner_name, getattr(self, 'owner_phone', '+237 6XX XX XX XX'), getattr(self, 'owner_email', '')),
            ("🛡️ Service client", "Support flotte", "+237 800 00 00 00", "fleet@amsassurance.com"),
            ("⚖️ Gestion sinistres", "Déclaration sinistre", "+237 6XX XX XX XX", "sinistres@amsassurance.com"),
            ("📊 Conseiller", "Analyse performance", "+237 6XX XX XX XX", "conseil@amsassurance.com")
        ]
        
        for i, (role, name, phone, email) in enumerate(contacts):
            contact_widget = QFrame()
            contact_widget.setStyleSheet("""
                QFrame {
                    background: #f8fafc;
                    border-radius: 12px;
                }
            """)
            
            contact_layout = QVBoxLayout(contact_widget)
            contact_layout.setContentsMargins(16, 14, 16, 14)
            contact_layout.setSpacing(8)
            
            role_lbl = QLabel(role)
            role_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #8b5cf6; letter-spacing: 0.5px;")
            
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #1e293b;")
            
            phone_lbl = QLabel(phone)
            phone_lbl.setStyleSheet("font-size: 12px; color: #3b82f6;")
            
            contact_layout.addWidget(role_lbl)
            contact_layout.addWidget(name_lbl)
            contact_layout.addWidget(phone_lbl)
            
            if email:
                email_lbl = QLabel(email)
                email_lbl.setStyleSheet("font-size: 11px; color: #64748b;")
                contact_layout.addWidget(email_lbl)
            
            contacts_grid.addWidget(contact_widget, i // 2, i % 2)
        
        layout.addLayout(contacts_grid)
        
        return card