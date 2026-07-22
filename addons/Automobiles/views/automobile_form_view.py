
import os
import re
from datetime import date, datetime, timedelta
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QListWidget, QListWidgetItem, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QProgressBar, QLabel, QLineEdit, 
    QComboBox, QPushButton, QFrame, QGraphicsDropShadowEffect, 
    QWidget, QScrollArea, QTextEdit, QDateEdit, QMessageBox, 
    QApplication, QGroupBox, QSplitter, QTabWidget, QFormLayout,
    QSpinBox, QDoubleSpinBox, QButtonGroup, QRadioButton, QSizePolicy
)
from PySide6.QtCore import Qt, QPoint, QDate, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QPixmap, QFont, QLinearGradient, QBrush

import socket
import platform
import requests

from core.widgets.global_loader import get_global_loader
from core.workers.database_worker import async_query
from addons.Automobiles.controllers.compagnies_controller import CompagnieController

# Importer le style unifié
from addons.Automobiles.views.style import Colors, Fonts, Spacing, create_shadow


class VehicleForm(QDialog):
    """
    Formulaire complet de gestion des véhicules
    Conforme aux spécifications API ASAC
    """
    FIELD_STYLE = """
        QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 10px 14px;
            background-color: white;
            font-size: 13px;
            color: #2d3748;
            font-family: 'Segoe UI';
        }
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
            border-color: #3498db;
            background-color: #f0f9ff;
        }
        QLabel {
            color: #4a5568;
            font-weight: 600;
            font-size: 12px;
            margin-bottom: 4px;
        }
    """
    
    GROUP_STYLE = """
        QGroupBox {
            font-size: 14px;
            font-weight: bold;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            margin-top: 12px;
            padding-top: 12px;
            background: white;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 12px 0 12px;
            color: #2c3e50;
        }
    """
    # Constantes pour les codes ASAC
    ASAC_CUSTOMER_TYPES = {
        "TSPP": "Personne Physique",
        "TSPM": "Personne Morale"
    }
    
    ASAC_VEHICLE_CATEGORIES = {
        "VP01": "Véhicule de tourisme (Personne physique)",
        "VP02": "Transport pour propre compte",
        "VP03": "Transport public de marchandises",
        "VP04": "Transport public de voyageurs",
        "VP05": "Véhicule motorisé à 2 ou 3 roues",
        "VP06": "Véhicule des garagistes",
        "VP07": "Véhicule d'auto-écoles",
        "VP08": "Véhicule de location",
        "VP09": "Engin de chantier",
        "VP10": "Véhicules spéciaux",
        "VP11": "Catégorie 11",
        "VP12": "Véhicule de tourisme (Personne morale)"
    }
    
    ASAC_VEHICLE_GENRES = {
        "GV01": "Camion",
        "GV02": "Camionnette",
        "GV03": "Cyclomoteur (2/3 Roues)",
        "GV04": "Voiture (4 Roues)",
        "GV05": "Engins de chantiers",
        "GV06": "Car",
        "GV07": "Fourgonnette",
        "GV08": "Remorque",
        "GV09": "Scooter",
        "GV10": "Semi-remorque",
        "GV11": "Tracteur agricole",
        "GV12": "Tracteur routier"
    }
    
    ASAC_VEHICLE_TYPES = {
        "TV01": "Ambulance",
        "TV02": "Auto Car (Plus de 41 places)",
        "TV03": "Corbiard",
        "TV04": "Mini Car (9 à 40 places)",
        "TV05": "Taxi Communaux",
        "TV06": "Taxi Urbain (MATCA, VTC)",
        "TV07": "Véhicule Auto-École",
        "TV08": "Véhicule de Service Public",
        "TV09": "Véhicule de Tourisme (max 9 places, avec chauffeur)",
        "TV10": "Véhicule Particulier (PTAC max 3,5 T)",
        "TV11": "Véhicule Utilitaire",
        "TV12": "Voiture de Location",
        "TV13": "Cyclomoteur (2/3 Roues)"
    }
    
    ASAC_VEHICLE_USAGES = {
        "UV01": "Promenade ou Affaire",
        "UV02": "Transport pour propre compte",
        "UV03": "Transport privé de voyageurs",
        "UV04": "Transport public de marchandises",
        "UV05": "Transport public de voyageurs",
        "UV06": "Véhicules Auto-école",
        "UV07": "Véhicules de Location",
        "UV08": "Véhicules Spéciaux",
        "UV09": "Engin de Chantier",
        "UV10": "Véhicule motorisé 2 à 3 roues"
    }
    
    ASAC_VEHICLE_ENERGIES = {
        "SEE": "Essence",
        "SED": "Diesel",
        "SEL": "Électrique",
        "SEHY": "Hybride"
    }
    
    ASAC_CIRCULATION_ZONES = {
        "ZA": "A",
        "ZB": "B",
        "ZC": "C"
    }
    
    ASAC_INSURED_PROFESSIONS = {
        "ST01": "Agent commercial",
        "ST02": "Agent de recouvrement",
        "ST03": "Agriculteur",
        "ST04": "Artisan",
        "ST05": "Conjoint",
        "ST06": "Employeur",
        "ST07": "Religieux",
        "ST08": "Retraité",
        "ST09": "Salarié",
        "ST10": "Sans emploi",
        "ST11": "VRP (Vendeur, Représentant et Placer)",
        "ST12": "Autre profession"
    }
    
    def __init__(self, controller, contacts_list=None, current_user=None, data=None, mode="add", vehicle_to_edit=None):
        super().__init__()
      
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.controller = controller
        self.contacts = contacts_list or []
        self.current_user = current_user
        self.mode = mode
        self.initial_data = data
        self.vehicle_to_edit = vehicle_to_edit
        self.vehicle_id = vehicle_to_edit.id if hasattr(vehicle_to_edit, 'id') else None
        self.selected_cie_id = None
        self.old_pos = None
        self.is_maximized = False
        self.normal_geometry = None
        self.preselected_owner_id = data.get('owner_id') if data else None
        
        # Dictionnaire pour stocker les champs de garanties
        self.garanties_widgets = {}
        
        self.setup_ui()

        if vehicle_to_edit:
            self.load_existing_data(vehicle_to_edit)

        if self.initial_data:
            self.fill_form(self.initial_data)
        
        if self.mode == "view":
            self.freeze_ui()
            
        # Connecter les signaux pour les calculs automatiques
        self._connect_signals()

    def _connect_signals(self):
        """Connecte les signaux pour les calculs automatiques"""
        if hasattr(self, 'combo_zone'):
            self.combo_zone.currentTextChanged.connect(self.on_zone_changed)
        if hasattr(self, 'combo_cat'):
            self.combo_cat.currentTextChanged.connect(self.on_category_changed)
        if hasattr(self, 'combo_usage'):
            self.combo_usage.currentTextChanged.connect(self.on_usage_changed)
        if hasattr(self, 'usage_input'):
            self.usage_input.textChanged.connect(self.on_power_changed)
        if hasattr(self, 'date_debut'):
            self.date_debut.dateChanged.connect(self.on_date_changed)
        if hasattr(self, 'date_fin'):
            self.date_fin.dateChanged.connect(self.on_date_changed)

    def on_zone_changed(self, zone):
        self.update_rc_calculation_async()
        
    def on_category_changed(self, category):
        self.update_rc_calculation_async()
        
    def on_usage_changed(self, usage):
        self.update_rc_calculation_async()
        
    def on_power_changed(self, power):
        self.update_rc_calculation_async()
        
    def on_date_changed(self):
        self.calculate_prorata()
        self.refresh_all_garanties()

    def _create_classification_tab(self):
        """Crée l'onglet de classification ASAC avec ScrollArea"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ScrollArea pour tout le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3498db;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        field_style = """
            QLineEdit, QComboBox, QDateEdit {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 10px 14px;
                background-color: white;
                font-size: 13px;
                color: #2d3748;
                font-family: 'Segoe UI';
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #3498db;
                background-color: #f0f9ff;
            }
            QLabel {
                color: #4a5568;
                font-weight: 600;
                font-size: 12px;
                margin-bottom: 4px;
            }
        """
        
        group_style = """
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                margin-top: 12px;
                padding-top: 12px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 12px 0 12px;
                color: #2c3e50;
            }
        """
        
        # Groupe: Classification ASAC
        group_class = QGroupBox("📊 Classification ASAC")
        group_class.setStyleSheet(group_style)
        
        class_layout = QGridLayout(group_class)
        class_layout.setSpacing(15)
        class_layout.setContentsMargins(25, 25, 25, 25)
        
        # Catégorie
        class_layout.addWidget(self._create_label("🏷️", "Catégorie *"), 0, 0)
        self.asac_combo_cat = QComboBox()
        self.asac_combo_cat.setStyleSheet(field_style)
        self.asac_combo_cat.setEditable(True)
        self.asac_combo_cat.addItem("", "")
        for code, label in self.ASAC_VEHICLE_CATEGORIES.items():
            self.asac_combo_cat.addItem(f"{code} - {label}", code)
        self.asac_combo_cat.currentTextChanged.connect(self.on_category_changed)
        class_layout.addWidget(self.asac_combo_cat, 1, 0)
        
        # Genre
        class_layout.addWidget(self._create_label("🚗", "Genre *"), 0, 1)
        self.combo_genre = QComboBox()
        self.combo_genre.setStyleSheet(field_style)
        self.combo_genre.addItem("", "")
        for code, label in self.ASAC_VEHICLE_GENRES.items():
            self.combo_genre.addItem(f"{code} - {label}", code)
        class_layout.addWidget(self.combo_genre, 1, 1)
        
        # Type
        class_layout.addWidget(self._create_label("📱", "Type *"), 2, 0)
        self.combo_type = QComboBox()
        self.combo_type.setStyleSheet(field_style)
        self.combo_type.addItem("", "")
        for code, label in self.ASAC_VEHICLE_TYPES.items():
            self.combo_type.addItem(f"{code} - {label}", code)
        class_layout.addWidget(self.combo_type, 3, 0)
        
        # Usage
        class_layout.addWidget(self._create_label("📊", "Usage *"), 2, 1)
        self.combo_usage = QComboBox()
        self.combo_usage.setStyleSheet(field_style)
        self.combo_usage.addItem("", "")
        for code, label in self.ASAC_VEHICLE_USAGES.items():
            self.combo_usage.addItem(f"{code} - {label}", code)
        self.combo_usage.currentTextChanged.connect(self.on_usage_changed)
        class_layout.addWidget(self.combo_usage, 3, 1)
        
        # Énergie
        class_layout.addWidget(self._create_label("⛽", "Énergie *"), 4, 0)
        self.combo_energie = QComboBox()
        self.combo_energie.setStyleSheet(field_style)
        self.combo_energie.addItem("", "")
        for code, label in self.ASAC_VEHICLE_ENERGIES.items():
            self.combo_energie.addItem(f"{code} - {label}", code)
        class_layout.addWidget(self.combo_energie, 5, 0)
        
        # Zone de circulation
        class_layout.addWidget(self._create_label("🗺️", "Zone de circulation *"), 4, 1)
        self.combo_zone = QComboBox()
        self.combo_zone.setStyleSheet(field_style)
        self.combo_zone.addItem("", "")
        for code, label in self.ASAC_CIRCULATION_ZONES.items():
            self.combo_zone.addItem(f"{code} - {label}", code)
        self.combo_zone.currentTextChanged.connect(self.on_zone_changed)
        class_layout.addWidget(self.combo_zone, 5, 1)
        
        content_layout.addWidget(group_class)
        
        # Groupe: Options et compléments
        group_options = QGroupBox("⚙️ Options et compléments")
        group_options.setStyleSheet(group_style)
        
        options_layout = QGridLayout(group_options)
        options_layout.setSpacing(15)
        options_layout.setContentsMargins(25, 25, 25, 25)
        
        # Remorque
        self.check_remorque = QCheckBox("🚛 Véhicule avec Remorque")
        self.check_remorque.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                font-weight: 600;
                color: #4a5568;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #cbd5e0;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)
        self.check_remorque.stateChanged.connect(self.on_remorque_changed)
        options_layout.addWidget(self.check_remorque, 0, 0)
        
        # Immatriculation remorque
        options_layout.addWidget(self._create_label("🔢", "Immatriculation Remorque"), 1, 0)
        self.remorque_immat = QLineEdit()
        self.remorque_immat.setPlaceholderText("Immatriculation de la remorque")
        self.remorque_immat.setStyleSheet(field_style)
        self.remorque_immat.setEnabled(False)
        options_layout.addWidget(self.remorque_immat, 2, 0)
        
        # Matières inflammables
        self.check_inflammable = QCheckBox("🔥 Remorque transportant des matières inflammables")
        self.check_inflammable.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                font-weight: 600;
                color: #4a5568;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #cbd5e0;
            }
            QCheckBox::indicator:checked {
                background-color: #e74c3c;
                border-color: #e74c3c;
            }
        """)
        self.check_inflammable.setEnabled(False)
        options_layout.addWidget(self.check_inflammable, 0, 1)
        
        # Double commande (auto-école)
        self.check_double_commande = QCheckBox("🎓 Double commande (Auto-école)")
        self.check_double_commande.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                font-weight: 600;
                color: #4a5568;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #cbd5e0;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)
        options_layout.addWidget(self.check_double_commande, 1, 1)
        
        # RC élèves (auto-école)
        self.check_rc_eleves = QCheckBox("👨‍🎓 Garantie RC élèves (Auto-école)")
        self.check_rc_eleves.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                font-weight: 600;
                color: #4a5568;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #cbd5e0;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)
        options_layout.addWidget(self.check_rc_eleves, 2, 1)
        
        # Engin portuaire
        self.check_engin_portuaire = QCheckBox("⚓ Engin portuaire")
        self.check_engin_portuaire.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                font-weight: 600;
                color: #4a5568;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #cbd5e0;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)
        options_layout.addWidget(self.check_engin_portuaire, 3, 1)
        
        content_layout.addWidget(group_options)
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        return tab

    def on_fleet_changed(self, libelle):
        """Met à jour le code tarif en fonction du libellé"""
        if libelle:
            # Chercher le code correspondant
            for i in range(self.combo_fleet.count()):
                data = self.combo_fleet.itemData(i)
                if data and data.get('libelle') == libelle:
                    code = data.get('code')
                    if code:
                        self.code_tarif.setCurrentText(code)
                    break

    def calculate_prorata(self):
        try:
            d_debut = self.date_debut.date().toPython()
            d_fin = self.date_fin.date().toPython()
            nbr_jr = (max(0, (d_fin - d_debut).days)) + 1
            
            self.nbr_jour.setText(str(nbr_jr))
            return nbr_jr / 365.0 if nbr_jr > 0 else 1
        except Exception:
            return 1

    def setup_ui(self):
        """Configure l'interface utilisateur avec style unifié"""
        self.resize(1100, 900)
        self.setMinimumSize(1000, 800)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # Carte principale
        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setStyleSheet(f"""
            QFrame#MainCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Colors.WHITE}, stop:1 {Colors.GRAY_50});
                border-radius: 24px;
                border: 1px solid rgba(0,0,0,0.08);
            }}
        """)
        
        shadow = create_shadow(blur=40, offset_y=10, color=QColor(0, 0, 0, 40))
        self.card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # --- HEADER GRADIENT ---
        self._setup_header(card_layout)
        
        # --- BANNIÈRE D'ALERTE ---
        self._setup_alert_banner(card_layout)
        
        # --- CONTENU AVEC ONGLETS ---
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
                border-radius: 10px 10px 0 0;
                margin-right: 4px;
                color: {Colors.TEXT_SECONDARY};
            }}
            QTabBar::tab:selected {{
                background: {Colors.PRIMARY};
                color: {Colors.WHITE};
            }}
            QTabBar::tab:hover:!selected {{
                background: {Colors.GRAY_200};
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        
        # Créer les onglets
        self.tab_widget.addTab(self._create_identification_tab(), "🔍 Identification")
        self.tab_widget.addTab(self._create_classification_tab(), "🏷️ Classification")
        self.tab_widget.addTab(self._create_technical_tab(), "⚙️ Caractéristiques")
        self.tab_widget.addTab(self._create_owner_tab(), "👤 Propriétaire")
        self.tab_widget.addTab(self._create_guarantees_tab(), "🛡️ Garanties")
        self.tab_widget.addTab(self._create_financial_tab(), "💰 Financier")
        
        card_layout.addWidget(self.tab_widget)
        
        # --- FOOTER ---
        self._setup_footer(card_layout)
        
        main_layout.addWidget(self.card)

    def _setup_header(self, parent_layout):
        """Configure l'en-tête du formulaire"""
        header_widget = QFrame()
        header_widget.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK});
                border-top-left-radius: 24px;
                border-top-right-radius: 24px;
            }}
        """)
        header_widget.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 0, 20, 0)
        
        # Titre avec icône
        mode_text = "MODIFICATION" if self.mode == "edit" else "NOUVEAU"
        title_text = QLabel(f"🚗 FICHE VÉHICULE - {mode_text}")
        title_text.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 800;
            color: {Colors.WHITE};
            font-family: 'Segoe UI', 'Arial';
            letter-spacing: 0.5px;
        """)
        
        # Boutons de contrôle
        btn_style = f"""
            QPushButton {{
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 8px;
                color: {Colors.WHITE};
                font-size: 16px;
                padding: 8px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.3);
            }}
            QPushButton#closeBtn:hover {{
                background: {Colors.DANGER};
            }}
        """
        
        self.btn_minimize = QPushButton("─")
        self.btn_minimize.setFixedSize(32, 32)
        self.btn_minimize.setStyleSheet(btn_style)
        self.btn_minimize.clicked.connect(self.showMinimized)
        
        self.btn_maximize = QPushButton("□")
        self.btn_maximize.setFixedSize(32, 32)
        self.btn_maximize.setStyleSheet(btn_style)
        self.btn_maximize.clicked.connect(self.toggle_maximize)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("closeBtn")
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setStyleSheet(btn_style)
        self.btn_close.clicked.connect(self.reject)
        
        header_layout.addWidget(title_text)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_minimize)
        header_layout.addWidget(self.btn_maximize)
        header_layout.addWidget(self.btn_close)
        
        parent_layout.addWidget(header_widget)

    def _setup_alert_banner(self, parent_layout):
        """Configure la bannière d'alerte pour les champs obligatoires"""
        alert_widget = QFrame()
        alert_widget.setStyleSheet(f"""
            QFrame {{
                background: {Colors.WARNING}20;
                border: 2px solid {Colors.WARNING};
                border-radius: 10px;
                margin: 8px 20px 0 20px;
            }}
        """)
        alert_widget.setFixedHeight(44)
        
        alert_layout = QHBoxLayout(alert_widget)
        alert_layout.setContentsMargins(16, 6, 16, 6)
        
        alert_icon = QLabel("⚠️")
        alert_icon.setStyleSheet("font-size: 18px; background: transparent;")
        
        alert_text = QLabel(
            "Les champs marqués d'une <b><span style='color: #dc2626;'>*</span></b> sont obligatoires"
        )
        alert_text.setStyleSheet(f"""
            font-size: 13px;
            color: {Colors.TEXT_SECONDARY};
            background: transparent;
        """)
        
        alert_layout.addWidget(alert_icon)
        alert_layout.addWidget(alert_text, 1)
        alert_layout.addStretch()
        
        parent_layout.addWidget(alert_widget)

    def _create_label(self, icon, text):
        """Crée un label avec icône"""
        label = QLabel(f"{icon} {text}")
        label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {Colors.TEXT_SECONDARY};
            margin-bottom: 4px;
        """)
        return label

    def _get_field_style(self):
        """Retourne le style unifié pour les champs"""
        return f"""
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
                border: 2px solid {Colors.BORDER};
                border-radius: 10px;
                padding: 9px 12px;
                background-color: {Colors.WHITE};
                font-size: 13px;
                color: {Colors.TEXT_PRIMARY};
                font-family: {Fonts.FAMILY};
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
                border-color: {Colors.PRIMARY};
                background-color: {Colors.PRIMARY}10;
            }}
            QLineEdit:disabled, QComboBox:disabled, QDateEdit:disabled {{
                background-color: {Colors.GRAY_100};
                color: {Colors.TEXT_MUTED};
            }}
        """

    def _get_group_style(self):
        """Retourne le style unifié pour les groupes"""
        return f"""
            QGroupBox {{
                font-size: 13px;
                font-weight: bold;
                border: 2px solid {Colors.BORDER};
                border-radius: 14px;
                margin-top: 10px;
                padding-top: 10px;
                background: {Colors.WHITE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 10px 0 10px;
                color: {Colors.TEXT_PRIMARY};
            }}
        """

    def on_remorque_changed(self, state):
        """Active/désactive les champs liés à la remorque"""
        enabled = state == Qt.CheckState.Checked
        self.remorque_immat.setEnabled(enabled)
        self.check_inflammable.setEnabled(enabled)

    def calculate_tva(self):
        """Calcule la TVA (19.25%)"""
        try:
            prime_nette = self.get_float_value(self.prime_nette)
            accessoires = self.get_float_value(self.accessoire)
            asac = self.get_float_value(self.asac)
            
            base_tva = prime_nette + accessoires + asac
            tva = base_tva * 0.1925
            
            self.tva.setText(f"{tva:,.0f}".replace(",", " "))
            return tva
        except Exception as e:
            print(f"Erreur TVA: {e}")
            return 0
    
    def calculate_pttc(self):
        """Calcule le PTTC"""
        try:
            prime_nette = self.get_float_value(self.prime_nette)
            accessoires = self.get_float_value(self.accessoire)
            asac = self.get_float_value(self.asac)
            tva = self.get_float_value(self.tva)
            vignette = self.get_float_value(self.vignette)
            carte_rose = self.get_float_value(self.carte_rose)
            
            pttc = prime_nette + accessoires + asac + tva + vignette + carte_rose
            
            self.pttc.setText(f"{pttc:,.0f}".replace(",", " "))
            return pttc
        except Exception as e:
            print(f"Erreur PTTC: {e}")
            return 0

    def load_tarif_categories_by_code_async(self, code):
        """Charge les catégories associées à un code tarif sélectionné."""
        if not self.selected_cie_id or not self.controller or not code:
            return

        loader = get_global_loader()
        loader.show_loading("Chargement des catégories...")

        def fetch():
            return self.controller.vehicles.get_tarif_categories_by_compagnie_and_code(
                self.selected_cie_id,
                code
            )

        async_query.execute(
            fetch,
            on_finished=self._on_tarif_categories_loaded,
            on_error=self._on_tarif_codes_error
        )

    def get_rc_base_amount(self):
        """
        Récupère le montant de base de la RC (utile pour les garanties dépendantes)
        
        Returns:
            float: Montant de la RC (0 si non calculée)
        """
        try:
            garantie_data = self.result_labels.get("rc")
            if garantie_data:
                montant_brut_label = garantie_data['montant_brut']
                if montant_brut_label and montant_brut_label.isVisible():
                    txt = montant_brut_label.text().replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    return float(txt) if txt else 0.0
            return 0.0
        except (ValueError, AttributeError):
            return 0.0
    
    # ============================================================
    # ONGLET PROPRIÉTAIRE AVEC SCROLLAREA
    # ============================================================
    
    def _create_owner_tab(self):
        """Crée l'onglet des propriétaires avec ScrollArea"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ScrollArea pour tout le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {Colors.GRAY_100};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {Colors.GRAY_400};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Colors.PRIMARY};
            }}
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        field_style = self._get_field_style()
        group_style = self._get_group_style()
        
        # ====== SOUSCRIPTEUR ======
        group_customer = QGroupBox("👤 Souscripteur <span style='color:#dc2626;'>*</span>")
        group_customer.setStyleSheet(group_style)
        customer_layout = QVBoxLayout(group_customer)
        customer_layout.setSpacing(12)
        customer_layout.setContentsMargins(20, 20, 20, 20)
        
        # Barre de recherche
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.search_customer = QLineEdit()
        self.search_customer.setPlaceholderText("🔍 Rechercher un souscripteur (nom, téléphone, code)...")
        self.search_customer.setStyleSheet(field_style)
        self.search_customer.textChanged.connect(self.filter_customers)
        search_layout.addWidget(self.search_customer, 1)
        
        new_customer_btn = QPushButton("➕ Nouveau")
        new_customer_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.SUCCESS};
                color: {Colors.WHITE};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {Colors.SUCCESS}cc;
            }}
        """)
        new_customer_btn.clicked.connect(self._open_new_contact_dialog)
        search_layout.addWidget(new_customer_btn)
        
        customer_layout.addLayout(search_layout)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {Colors.BORDER}; margin: 4px 0;")
        customer_layout.addWidget(sep)
        
        # Contenu principal : Liste + Détails
        customer_content = QHBoxLayout()
        customer_content.setSpacing(15)
        
        # Liste
        self.customer_list = QListWidget()
        self.customer_list.setFixedWidth(280)
        self.customer_list.setMinimumHeight(150)
        self.customer_list.setStyleSheet(f"""
            QListWidget {{
                border: 2px solid {Colors.BORDER};
                border-radius: 10px;
                background: {Colors.WHITE};
                outline: none;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                border-radius: 6px;
                margin: 1px;
                font-size: 12px;
            }}
            QListWidget::item:hover {{
                background: {Colors.GRAY_100};
            }}
            QListWidget::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK});
                color: {Colors.WHITE};
            }}
        """)
        self.customer_list.currentRowChanged.connect(self.display_customer_details)
        customer_content.addWidget(self.customer_list)
        
        # Carte de détails
        self.customer_card = QFrame()
        self.customer_card.setObjectName("CustomerCard")
        self.customer_card.setStyleSheet(f"""
            QFrame#CustomerCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Colors.GRAY_50}, stop:1 {Colors.GRAY_100});
                border-radius: 12px;
                border: 2px solid {Colors.BORDER};
                padding: 16px;
            }}
        """)
        customer_card_layout = QHBoxLayout(self.customer_card)
        customer_card_layout.setSpacing(15)
        
        # Avatar
        avatar_container = QFrame()
        avatar_container.setFixedSize(70, 70)
        avatar_container.setStyleSheet(f"""
            QFrame {{
                background: {Colors.PRIMARY};
                border-radius: 35px;
                border: 3px solid {Colors.WHITE};
            }}
        """)
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.customer_photo = QLabel("👤")
        self.customer_photo.setStyleSheet(f"""
            font-size: 28px;
            color: {Colors.WHITE};
            background: transparent;
        """)
        self.customer_photo.setAlignment(Qt.AlignCenter)
        avatar_layout.addWidget(self.customer_photo)
        customer_card_layout.addWidget(avatar_container)
        
        # Informations
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setSpacing(6)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_customer_name = QLabel("Aucun souscripteur sélectionné")
        self.lbl_customer_name.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 700;
            color: {Colors.TEXT_PRIMARY};
        """)
        
        self.lbl_customer_info = QLabel("Sélectionnez un souscripteur dans la liste")
        self.lbl_customer_info.setStyleSheet(f"""
            font-size: 12px;
            color: {Colors.TEXT_MUTED};
            line-height: 1.6;
        """)
        self.lbl_customer_info.setWordWrap(True)
        
        info_layout.addWidget(self.lbl_customer_name)
        info_layout.addWidget(self.lbl_customer_info)
        info_layout.addStretch()
        
        customer_card_layout.addWidget(info_widget, 1)
        customer_content.addWidget(self.customer_card, 1)
        
        customer_layout.addLayout(customer_content)
        content_layout.addWidget(group_customer)
        
        # ====== ASSURÉ ======
        group_insured = QGroupBox("🛡️ Assuré <span style='color:#dc2626;'>*</span>")
        group_insured.setStyleSheet(group_style)
        insured_layout = QVBoxLayout(group_insured)
        insured_layout.setSpacing(12)
        insured_layout.setContentsMargins(20, 20, 20, 20)
        
        # Barre de recherche
        search_layout2 = QHBoxLayout()
        search_layout2.setSpacing(10)
        
        self.search_insured = QLineEdit()
        self.search_insured.setPlaceholderText("🔍 Rechercher un assuré (nom, téléphone, code)...")
        self.search_insured.setStyleSheet(field_style)
        self.search_insured.textChanged.connect(self.filter_insured)
        search_layout2.addWidget(self.search_insured, 1)
        
        new_insured_btn = QPushButton("➕ Nouveau")
        new_insured_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.SUCCESS};
                color: {Colors.WHITE};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {Colors.SUCCESS}cc;
            }}
        """)
        new_insured_btn.clicked.connect(self._open_new_contact_dialog)
        search_layout2.addWidget(new_insured_btn)
        
        insured_layout.addLayout(search_layout2)
        
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet(f"background: {Colors.BORDER}; margin: 4px 0;")
        insured_layout.addWidget(sep2)
        
        # Contenu principal
        insured_content = QHBoxLayout()
        insured_content.setSpacing(15)
        
        self.insured_list = QListWidget()
        self.insured_list.setFixedWidth(280)
        self.insured_list.setMinimumHeight(150)
        self.insured_list.setStyleSheet(self.customer_list.styleSheet())
        self.insured_list.currentRowChanged.connect(self.display_insured_details)
        insured_content.addWidget(self.insured_list)
        
        self.insured_card = QFrame()
        self.insured_card.setObjectName("InsuredCard")
        self.insured_card.setStyleSheet(f"""
            QFrame#InsuredCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Colors.GRAY_50}, stop:1 {Colors.GRAY_100});
                border-radius: 12px;
                border: 2px solid {Colors.BORDER};
                padding: 16px;
            }}
        """)
        insured_card_layout = QHBoxLayout(self.insured_card)
        insured_card_layout.setSpacing(15)
        
        avatar_container2 = QFrame()
        avatar_container2.setFixedSize(70, 70)
        avatar_container2.setStyleSheet(f"""
            QFrame {{
                background: {Colors.SUCCESS};
                border-radius: 35px;
                border: 3px solid {Colors.WHITE};
            }}
        """)
        avatar_layout2 = QVBoxLayout(avatar_container2)
        avatar_layout2.setAlignment(Qt.AlignCenter)
        avatar_layout2.setContentsMargins(0, 0, 0, 0)
        
        self.insured_photo = QLabel("🛡️")
        self.insured_photo.setStyleSheet(f"""
            font-size: 28px;
            color: {Colors.WHITE};
            background: transparent;
        """)
        self.insured_photo.setAlignment(Qt.AlignCenter)
        avatar_layout2.addWidget(self.insured_photo)
        insured_card_layout.addWidget(avatar_container2)
        
        info_widget2 = QWidget()
        info_layout2 = QVBoxLayout(info_widget2)
        info_layout2.setSpacing(6)
        info_layout2.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_insured_name = QLabel("Aucun assuré sélectionné")
        self.lbl_insured_name.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 700;
            color: {Colors.TEXT_PRIMARY};
        """)
        
        self.lbl_insured_info = QLabel("Sélectionnez un assuré dans la liste")
        self.lbl_insured_info.setStyleSheet(f"""
            font-size: 12px;
            color: {Colors.TEXT_MUTED};
            line-height: 1.6;
        """)
        self.lbl_insured_info.setWordWrap(True)
        
        info_layout2.addWidget(self.lbl_insured_name)
        info_layout2.addWidget(self.lbl_insured_info)
        info_layout2.addStretch()
        
        insured_card_layout.addWidget(info_widget2, 1)
        insured_content.addWidget(self.insured_card, 1)
        
        insured_layout.addLayout(insured_content)
        content_layout.addWidget(group_insured)
        
        # ====== CONDUCTEUR ======
        group_driver = QGroupBox("🚗 Conducteur habituel <span style='color:#dc2626;'>*</span>")
        group_driver.setStyleSheet(group_style)
        driver_layout = QGridLayout(group_driver)
        driver_layout.setSpacing(12)
        driver_layout.setContentsMargins(20, 20, 20, 20)
        
        driver_layout.addWidget(self._create_label("👤", "Nom et prénom *"), 0, 0)
        driver_layout.addWidget(self._create_label("📅", "Date de naissance *"), 0, 1)
        
        self.driver_name = QLineEdit()
        self.driver_name.setPlaceholderText("NOM Prénom")
        self.driver_name.setStyleSheet(field_style)
        driver_layout.addWidget(self.driver_name, 1, 0)
        
        self.driver_birth = QDateEdit()
        self.driver_birth.setDisplayFormat("dd/MM/yyyy")
        self.driver_birth.setCalendarPopup(True)
        self.driver_birth.setDate(QDate.currentDate().addYears(-30))
        self.driver_birth.setStyleSheet(field_style)
        driver_layout.addWidget(self.driver_birth, 1, 1)
        
        driver_layout.addWidget(self._create_label("🪪", "N° de permis *"), 2, 0)
        driver_layout.addWidget(self._create_label("📋", "Catégorie *"), 2, 1)
        
        self.driver_licence = QLineEdit()
        self.driver_licence.setPlaceholderText("Numéro du permis de conduire")
        self.driver_licence.setStyleSheet(field_style)
        driver_layout.addWidget(self.driver_licence, 3, 0)
        
        self.driver_licence_cat = QComboBox()
        self.driver_licence_cat.setStyleSheet(field_style)
        self.driver_licence_cat.addItems(["", "A", "B", "C", "D", "E"])
        driver_layout.addWidget(self.driver_licence_cat, 3, 1)
        
        driver_layout.addWidget(self._create_label("📅", "Date de délivrance *"), 4, 0)
        driver_layout.addWidget(self._create_label("🏛️", "Autorité de délivrance"), 4, 1)
        
        self.driver_licence_date = QDateEdit()
        self.driver_licence_date.setDisplayFormat("dd/MM/yyyy")
        self.driver_licence_date.setCalendarPopup(True)
        self.driver_licence_date.setDate(QDate.currentDate().addYears(-5))
        self.driver_licence_date.setStyleSheet(field_style)
        driver_layout.addWidget(self.driver_licence_date, 5, 0)
        
        self.driver_licence_authority = QLineEdit()
        self.driver_licence_authority.setPlaceholderText("Ex: Préfecture de ...")
        self.driver_licence_authority.setStyleSheet(field_style)
        driver_layout.addWidget(self.driver_licence_authority, 5, 1)
        
        content_layout.addWidget(group_driver)
        
        # ====== COMPAGNIE ======
        group_company = QGroupBox("🏢 Compagnie d'assurance <span style='color:#dc2626;'>*</span>")
        group_company.setStyleSheet(group_style)
        company_layout = QVBoxLayout(group_company)
        company_layout.setSpacing(12)
        company_layout.setContentsMargins(20, 20, 20, 20)
        
        # Barre de recherche avec bouton
        search_layout3 = QHBoxLayout()
        search_layout3.setSpacing(10)
        
        self.search_company = QLineEdit()
        self.search_company.setPlaceholderText("🔍 Rechercher une compagnie...")
        self.search_company.setStyleSheet(field_style)
        self.search_company.textChanged.connect(self.filter_companies)
        search_layout3.addWidget(self.search_company, 1)
        
        new_company_btn = QPushButton("➕ Nouveau")
        new_company_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.INFO};
                color: {Colors.WHITE};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {Colors.INFO}cc;
            }}
        """)
        new_company_btn.clicked.connect(self._open_new_company_dialog)
        search_layout3.addWidget(new_company_btn)
        
        company_layout.addLayout(search_layout3)
        
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.HLine)
        sep3.setStyleSheet(f"background: {Colors.BORDER}; margin: 4px 0;")
        company_layout.addWidget(sep3)
        
        # Contenu principal
        company_content = QHBoxLayout()
        company_content.setSpacing(15)
        
        self.company_list = QListWidget()
        self.company_list.setFixedWidth(280)
        self.company_list.setMinimumHeight(120)
        self.company_list.setStyleSheet(self.customer_list.styleSheet())
        self.company_list.currentRowChanged.connect(self.display_company_details)
        company_content.addWidget(self.company_list)
        
        self.company_card = QFrame()
        self.company_card.setObjectName("CompanyCard")
        self.company_card.setStyleSheet(f"""
            QFrame#CompanyCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Colors.GRAY_50}, stop:1 {Colors.GRAY_100});
                border-radius: 12px;
                border: 2px solid {Colors.BORDER};
                padding: 16px;
            }}
        """)
        company_card_layout = QHBoxLayout(self.company_card)
        company_card_layout.setSpacing(15)
        
        avatar_container3 = QFrame()
        avatar_container3.setFixedSize(70, 70)
        avatar_container3.setStyleSheet(f"""
            QFrame {{
                background: {Colors.INFO};
                border-radius: 35px;
                border: 3px solid {Colors.WHITE};
            }}
        """)
        avatar_layout3 = QVBoxLayout(avatar_container3)
        avatar_layout3.setAlignment(Qt.AlignCenter)
        avatar_layout3.setContentsMargins(0, 0, 0, 0)
        
        self.company_photo = QLabel("🏢")
        self.company_photo.setStyleSheet(f"""
            font-size: 28px;
            color: {Colors.WHITE};
            background: transparent;
        """)
        self.company_photo.setAlignment(Qt.AlignCenter)
        avatar_layout3.addWidget(self.company_photo)
        company_card_layout.addWidget(avatar_container3)
        
        info_widget3 = QWidget()
        info_layout3 = QVBoxLayout(info_widget3)
        info_layout3.setSpacing(6)
        info_layout3.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_company_name = QLabel("Aucune compagnie sélectionnée")
        self.lbl_company_name.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 700;
            color: {Colors.TEXT_PRIMARY};
        """)
        
        self.lbl_company_info = QLabel("Sélectionnez une compagnie dans la liste")
        self.lbl_company_info.setStyleSheet(f"""
            font-size: 12px;
            color: {Colors.TEXT_MUTED};
            line-height: 1.6;
        """)
        self.lbl_company_info.setWordWrap(True)
        
        info_layout3.addWidget(self.lbl_company_name)
        info_layout3.addWidget(self.lbl_company_info)
        info_layout3.addStretch()
        
        company_card_layout.addWidget(info_widget3, 1)
        company_content.addWidget(self.company_card, 1)
        
        company_layout.addLayout(company_content)
        content_layout.addWidget(group_company)
        
        content_layout.addStretch()
        
        # Assigner le contenu à la ScrollArea
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        return tab

    # ============================================================
    # MÉTHODES DE FILTRAGE ET AFFICHAGE
    # ============================================================

    def _open_new_contact_dialog(self):
        """Ouvre le dialogue de création d'un nouveau contact"""
        try:
            from addons.Automobiles.views.contacts_view import ContactDialog
            
            dialog = ContactDialog(self.controller, current_user=self.current_user)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if hasattr(self, 'search_customer'):
                    self.filter_customers(self.search_customer.text())
                if hasattr(self, 'search_insured'):
                    self.filter_insured(self.search_insured.text())
                QMessageBox.information(self, "Succès", "Contact créé avec succès")
        except ImportError:
            QMessageBox.information(self, "Nouveau contact", 
                "Veuillez créer le contact depuis l'onglet 'Clients'")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la création: {str(e)}")

    def _open_new_company_dialog(self):
        """Ouvre le dialogue de création d'une nouvelle compagnie"""
        try:
            from addons.Automobiles.views.compagnies_view import CompanyDialog
            
            dialog = CompanyDialog(self.controller, current_user=self.current_user)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if hasattr(self, 'search_company'):
                    self.filter_companies(self.search_company.text())
                QMessageBox.information(self, "Succès", "Compagnie créée avec succès")
        except ImportError:
            QMessageBox.information(self, "Nouvelle compagnie",
                "Veuillez créer la compagnie depuis l'onglet 'Compagnies'")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la création: {str(e)}")

    def filter_customers(self, text):
        """Filtre les souscripteurs selon la recherche"""
        self.customer_list.clear()
        if len(text) < 2:
            item = QListWidgetItem("🔍 Saisissez au moins 2 caractères")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.customer_list.addItem(item)
            return
        
        try:
            contacts = self.controller.contacts.search_contacts(text)
            if not contacts:
                item = QListWidgetItem("Aucun souscripteur trouvé")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.customer_list.addItem(item)
                return
            
            for contact in contacts:
                display = f"{contact.nom} {contact.prenom or ''} - {contact.telephone or ''}"
                item = QListWidgetItem(display)
                item.setData(Qt.UserRole, contact)
                self.customer_list.addItem(item)
        except Exception as e:
            print(f"Erreur filtrage souscripteurs: {e}")
            item = QListWidgetItem(f"Erreur: {str(e)}")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.customer_list.addItem(item)

    def filter_insured(self, text):
        """Filtre les assurés selon la recherche"""
        self.insured_list.clear()
        if len(text) < 2:
            item = QListWidgetItem("🔍 Saisissez au moins 2 caractères")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.insured_list.addItem(item)
            return
        
        try:
            contacts = self.controller.contacts.search_contacts(text)
            if not contacts:
                item = QListWidgetItem("Aucun assuré trouvé")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.insured_list.addItem(item)
                return
            
            for contact in contacts:
                display = f"{contact.nom} {contact.prenom or ''} - {contact.telephone or ''}"
                item = QListWidgetItem(display)
                item.setData(Qt.UserRole, contact)
                self.insured_list.addItem(item)
        except Exception as e:
            print(f"Erreur filtrage assurés: {e}")
            item = QListWidgetItem(f"Erreur: {str(e)}")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.insured_list.addItem(item)

    def filter_companies(self, text):
        """Filtre les compagnies selon la recherche"""
        self.company_list.clear()
        if len(text) < 2:
            item = QListWidgetItem("🔍 Saisissez au moins 2 caractères")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.company_list.addItem(item)
            return
        
        try:
            if hasattr(self.controller, 'compagnies'):
                companies = self.controller.compagnies.search_companies(text)
            else:
                from core.database import SessionLocal
                
                session = SessionLocal()
                controller = CompagnieController(session)
                companies = controller.search_companies(text)
                session.close()
            
            if not companies:
                item = QListWidgetItem("Aucune compagnie trouvée")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.company_list.addItem(item)
                return
            
            for company in companies:
                display = f"{company.nom} - {company.code or ''}"
                item = QListWidgetItem(display)
                item.setData(Qt.UserRole, company)
                self.company_list.addItem(item)
                
        except Exception as e:
            print(f"Erreur filtrage compagnies: {e}")
            item = QListWidgetItem(f"Erreur: {str(e)}")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.company_list.addItem(item)

    def display_customer_details(self, row):
        """Affiche les détails du souscripteur sélectionné"""
        if row < 0:
            return
        
        item = self.customer_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            return
        
        contact = item.data(Qt.UserRole)
        self.selected_customer_id = contact.id
        
        name = f"{contact.nom} {contact.prenom or ''}".upper()
        self.lbl_customer_name.setText(name)
        
        info = f"""📌 Type: {contact.nature or 'Particulier'}
📞 Tél: {contact.telephone or 'N/A'}
📧 Email: {contact.email or 'N/A'}
🆔 code: {contact.code_client or 'N/A'}
📍 adresse: {contact.adresse or 'N/A'}"""
        self.lbl_customer_info.setText(info)
        
        initials = f"{contact.nom[0]}{contact.prenom[0] if contact.prenom else ''}".upper()
        self.customer_photo.setText(initials)
        self.customer_photo.setStyleSheet(f"""
            font-size: 24px;
            color: {Colors.WHITE};
            background: transparent;
        """)

    def display_insured_details(self, row):
        """Affiche les détails de l'assuré sélectionné"""
        if row < 0:
            return
        
        item = self.insured_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            return
        
        contact = item.data(Qt.UserRole)
        self.selected_insured_id = contact.id
        
        name = f"{contact.nom} {contact.prenom or ''}".upper()
        self.lbl_insured_name.setText(name)
        
        info = f"""📌 Type: {contact.nature or 'Particulier'}
📞 Tél: {contact.telephone or 'N/A'}
📧 Email: {contact.email or 'N/A'}
🆔 Code: {contact.code_client or 'N/A'}
📍 Adresse: {contact.adresse or 'N/A'}"""
        self.lbl_insured_info.setText(info)
        
        initials = f"{contact.nom[0]}{contact.prenom[0] if contact.prenom else ''}".upper()
        self.insured_photo.setText(initials)
        self.insured_photo.setStyleSheet(f"""
            font-size: 24px;
            color: {Colors.WHITE};
            background: transparent;
        """)

    def display_company_details(self, row):
        """Affiche les détails de la compagnie sélectionnée"""
        if row < 0:
            return
        
        item = self.company_list.currentItem()
        if not item or not item.data(Qt.UserRole):
            return
        
        company = item.data(Qt.UserRole)
        self.selected_cie_id = company.id
        
        self.lbl_company_name.setText(company.nom.upper())
        
        info = f"""📌 Code: {company.code or 'N/A'}
📞 Tél: {company.telephone or 'N/A'}
📧 Email: {company.email or 'N/A'}
📍 Adresse: {company.adresse or 'N/A'}"""
        self.lbl_company_info.setText(info)
        
        if hasattr(company, 'logo') and company.logo:
            pixmap = QPixmap()
            pixmap.loadFromData(company.logo)
            self.company_photo.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.company_photo.setText("🏢")
            self.company_photo.setStyleSheet(f"""
                font-size: 28px;
                color: {Colors.WHITE};
                background: transparent;
            """)
        
        self.load_tarif_codes_async()

    def _add_contact_to_list(self, contact, list_widget):
        """Ajoute un contact à une liste"""
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item and item.data(Qt.UserRole) and hasattr(item.data(Qt.UserRole), 'id'):
                if item.data(Qt.UserRole).id == contact.id:
                    list_widget.setCurrentItem(item)
                    return
        
        display = f"{contact.nom} {contact.prenom or ''} - {contact.telephone or ''}"
        item = QListWidgetItem(display)
        item.setData(Qt.UserRole, contact)
        list_widget.addItem(item)
        list_widget.setCurrentItem(item)

    def load_owner_details_by_id(self, owner_id):
        """Charge les détails du propriétaire par son ID"""
        try:
            contact = self.controller.contacts.get_contact_by_id(owner_id)
            if not contact:
                return
            
            self._add_contact_to_list(contact, self.customer_list)
            self._add_contact_to_list(contact, self.insured_list)
            
        except Exception as e:
            print(f"Erreur chargement propriétaire: {e}")

    def load_tarif_codes_async(self):
        """Charge les codes tarif de manière asynchrone"""
        if not self.selected_cie_id or not self.controller:
            return
        
        loader = get_global_loader()
        loader.show_loading("Chargement des tarifs...")
        
        def fetch():
            return self.controller.vehicles.get_tarif_codes_by_compagnie(self.selected_cie_id)
        
        async_query.execute(
            fetch,
            on_finished=self._on_tarif_codes_loaded,
            on_error=self._on_tarif_codes_error
        )

    def _on_tarif_codes_loaded(self, codes):
        get_global_loader().hide_loading()
        
        if hasattr(self, 'code_tarif'):
            self.code_tarif.clear()
            self.code_tarif.addItem("", "")
        
        if hasattr(self, 'combo_fleet'):
            self.combo_fleet.clear()
            self.combo_fleet.addItem("", "")
        
        for code, libelle in codes:
            if hasattr(self, 'code_tarif'):
                self.code_tarif.addItem(code, {"code": code, "libelle": libelle})
            if hasattr(self, 'combo_fleet'):
                self.combo_fleet.addItem(libelle, {"code": code, "libelle": libelle})

    def _on_tarif_codes_error(self, error):
        get_global_loader().hide_loading()
        print(f"Erreur chargement tarifs: {error}")

    def _on_immat_change(self, text):
        """Formate l'immatriculation en majuscules"""
        self.immat_input.setText(text.upper())

    # ============================================================
    # MÉTHODES DE GESTION DES GARANTIES (simplifiées)
    # ============================================================

    def refresh_all_garanties(self):
        """Rafraîchit toutes les garanties"""
        for key in self.garanties_widgets:
            checkbox = self.garanties_widgets[key].get('checkbox')
            if checkbox and checkbox.isChecked():
                self.update_garantie_price(key, 2)

    def update_garantie_price(self, key, state):
        """Met à jour le prix d'une garantie"""
        garantie = self.garanties_widgets.get(key)
        if not garantie:
            return
        # Implémentation simplifiée - à compléter selon vos besoins
        pass

    def update_rc_calculation_async(self):
        """Met à jour le calcul de la RC en tâche de fond"""
        pass

    # ============================================================
    # AUTRES MÉTHODES UTILITAIRES
    # ============================================================

    def toggle_maximize(self):
        """Bascule entre mode normal et plein écran"""
        if self.is_maximized:
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.btn_maximize.setText("□")
        else:
            self.normal_geometry = self.geometry()
            screen_geometry = self.screen().availableGeometry()
            self.setGeometry(screen_geometry)
            self.btn_maximize.setText("❐")
        self.is_maximized = not self.is_maximized

    def mousePressEvent(self, event):
        """Gère le déplacement de la fenêtre"""
        if event.button() == Qt.LeftButton and not self.is_maximized:
            child = self.childAt(event.pos())
            if not isinstance(child, (QPushButton, QLineEdit, QComboBox, QTextEdit, QListWidget, QCheckBox, QTabWidget)):
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        """Déplace la fenêtre"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position') and not self.is_maximized:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Libère le déplacement"""
        if hasattr(self, 'drag_position'):
            delattr(self, 'drag_position')

    def fill_form(self, data):
        """Pré-remplit le formulaire"""
        if not data:
            return
        
        owner_id = data.get('owner_id')
        if owner_id:
            self.preselected_owner_id = owner_id
            self.load_owner_details_by_id(owner_id)

    def _to_qdate(self, dt):
        """
        Convertit un datetime ou date en QDate.
        
        Args:
            dt: datetime, date ou None
        
        Returns:
            QDate: Date convertie ou date courante
        """
        if dt is None:
            return QDate.currentDate()
        if isinstance(dt, datetime):
            return QDate(dt.year, dt.month, dt.day)
        if isinstance(dt, date):
            return QDate(dt.year, dt.month, dt.day)
        return QDate.currentDate()

    def load_existing_data(self, vehicle):
        """
        Charge les données d'un véhicule existant dans le formulaire.
        Cette méthode est appelée lors de l'édition d'un véhicule.
        
        Args:
            vehicle: Objet Vehicle chargé depuis la base de données
        """
        try:
            # ============================================================
            # 1. IDENTIFICATION
            # ============================================================
            if hasattr(self, 'immat_input') and vehicle.immatriculation:
                self.immat_input.setText(vehicle.immatriculation)
            
            if hasattr(self, 'chassis_input') and vehicle.chassis:
                self.chassis_input.setText(vehicle.chassis)
            
            if hasattr(self, 'marque_input') and vehicle.marque:
                self.marque_input.setText(vehicle.marque)
            
            if hasattr(self, 'modele_input') and vehicle.modele:
                self.modele_input.setText(vehicle.modele)
            
            if hasattr(self, 'annee_input') and vehicle.annee:
                self.annee_input.setText(str(vehicle.annee))
            
            if hasattr(self, 'date_mise_circulation') and vehicle.date_mise_circulation:
                self.date_mise_circulation.setDate(self._to_qdate(vehicle.date_mise_circulation))
            
            # ============================================================
            # 2. CLASSIFICATION ASAC
            # ============================================================
            # Catégorie
            if hasattr(self, 'asac_combo_cat') and vehicle.categorie:
                # Chercher l'item correspondant
                for i in range(self.asac_combo_cat.count()):
                    item_text = self.asac_combo_cat.itemText(i)
                    if vehicle.categorie in item_text:
                        self.asac_combo_cat.setCurrentIndex(i)
                        break
            
            if hasattr(self, 'combo_cat') and vehicle.categorie:
                for i in range(self.combo_cat.count()):
                    item_text = self.combo_cat.itemText(i)
                    if vehicle.categorie in item_text:
                        self.combo_cat.setCurrentIndex(i)
                        break
            
            # Genre
            if hasattr(self, 'combo_genre') and vehicle.genre:
                for i in range(self.combo_genre.count()):
                    item_text = self.combo_genre.itemText(i)
                    if vehicle.genre in item_text:
                        self.combo_genre.setCurrentIndex(i)
                        break
            
            # Type
            if hasattr(self, 'combo_type') and vehicle.type_vehicule:
                for i in range(self.combo_type.count()):
                    item_text = self.combo_type.itemText(i)
                    if vehicle.type_vehicule in item_text:
                        self.combo_type.setCurrentIndex(i)
                        break
            
            # Usage
            if hasattr(self, 'combo_usage') and vehicle.usage:
                for i in range(self.combo_usage.count()):
                    item_text = self.combo_usage.itemText(i)
                    if vehicle.usage in item_text:
                        self.combo_usage.setCurrentIndex(i)
                        break
            
            # Énergie
            if hasattr(self, 'combo_energie') and vehicle.energie:
                for i in range(self.combo_energie.count()):
                    item_text = self.combo_energie.itemText(i)
                    if vehicle.energie in item_text:
                        self.combo_energie.setCurrentIndex(i)
                        break
            
            # Zone
            if hasattr(self, 'combo_zone') and vehicle.zone:
                for i in range(self.combo_zone.count()):
                    item_text = self.combo_zone.itemText(i)
                    if not item_text:  # Ignorer les items vides
                        continue
                    # Vérifier si la zone est dans le texte ou si c'est la dernière lettre
                    if vehicle.zone in item_text or vehicle.zone == item_text[-1]:
                        self.combo_zone.setCurrentIndex(i)
                        break
            
            # ============================================================
            # 3. CARACTÉRISTIQUES TECHNIQUES
            # ============================================================
            if hasattr(self, 'usage_input') and vehicle.puissance_fiscale:
                self.usage_input.setText(str(vehicle.puissance_fiscale))
            
            if hasattr(self, 'places_input') and vehicle.places:
                self.places_input.setText(str(vehicle.places))
            
            if hasattr(self, 'cylindree_input') and vehicle.cylindree:
                self.cylindree_input.setText(str(vehicle.cylindree))
            
            if hasattr(self, 'ptac_input') and vehicle.ptac:
                self.ptac_input.setText(str(vehicle.ptac))
            
            if hasattr(self, 'charge_utile_input') and vehicle.charge_utile:
                self.charge_utile_input.setText(str(vehicle.charge_utile))
            
            if hasattr(self, 'val_neuf') and vehicle.valeur_neuf:
                self.val_neuf.setText(f"{vehicle.valeur_neuf:,.0f}".replace(",", " "))
            
            if hasattr(self, 'val_venale') and vehicle.valeur_venale:
                self.val_venale.setText(f"{vehicle.valeur_venale:,.0f}".replace(",", " "))
            
            # ============================================================
            # 4. OPTIONS
            # ============================================================
            if hasattr(self, 'check_remorque'):
                self.check_remorque.setChecked(vehicle.has_remorque or False)
            
            if hasattr(self, 'check_inflammable'):
                self.check_inflammable.setChecked(vehicle.remorque_inflammable or False)
            
            if hasattr(self, 'check_double_commande'):
                self.check_double_commande.setChecked(vehicle.double_commande or False)
            
            if hasattr(self, 'check_rc_eleves'):
                self.check_rc_eleves.setChecked(vehicle.rc_eleves or False)
            
            if hasattr(self, 'check_engin_portuaire'):
                self.check_engin_portuaire.setChecked(vehicle.engin_portuaire or False)
            
            if hasattr(self, 'remorque_immat') and vehicle.remorque_immat:
                self.remorque_immat.setText(vehicle.remorque_immat)
                self.remorque_immat.setEnabled(vehicle.has_remorque or False)
            
            # ============================================================
            # 5. CODES TARIFAIRES
            # ============================================================
            if hasattr(self, 'code_tarif') and vehicle.code_tarif:
                for i in range(self.code_tarif.count()):
                    item_text = self.code_tarif.itemText(i)
                    if vehicle.code_tarif in item_text or vehicle.code_tarif == item_text:
                        self.code_tarif.setCurrentIndex(i)
                        break
            
            if hasattr(self, 'combo_fleet') and vehicle.libele_tarif:
                for i in range(self.combo_fleet.count()):
                    item_text = self.combo_fleet.itemText(i)
                    if vehicle.libele_tarif in item_text or vehicle.libele_tarif == item_text:
                        self.combo_fleet.setCurrentIndex(i)
                        break
            
            if hasattr(self, 'code_assure') and vehicle.code_assure:
                self.code_assure.setText(vehicle.code_assure)
            
            # ============================================================
            # 6. PROPRIÉTAIRES (Souscripteur et Assuré)
            # ============================================================
            if hasattr(self, 'owner_id') and vehicle.owner_id:
                self.selected_customer_id = vehicle.owner_id
                self.selected_insured_id = vehicle.owner_id
                
                # Charger les détails du propriétaire
                self.load_owner_details_by_id(vehicle.owner_id)
            
            # ============================================================
            # 7. COMPAGNIE
            # ============================================================
            if hasattr(self, 'selected_cie_id') and vehicle.compagny_id:
                self.selected_cie_id = vehicle.compagny_id
                # Charger les détails de la compagnie
                self._load_company_by_id(vehicle.compagny_id)
            
            # ============================================================
            # 8. CONDUCTEUR (Driver)
            # ============================================================
            if hasattr(vehicle, 'driver') and vehicle.driver is not None:
                driver = vehicle.driver
                
                if hasattr(self, 'driver_name'):
                    # Le modèle stocke le nom complet dans driver_name
                    # On essaie de séparer nom et prénom si possible
                    full_name = driver.driver_name or ''
                    # Si le nom contient un espace, on le divise en nom et prénom
                    if ' ' in full_name:
                        parts = full_name.split(' ', 1)
                        nom = parts[0]
                        prenom = parts[1] if len(parts) > 1 else ''
                    else:
                        nom = full_name
                        prenom = ''
                    self.driver_name.setText(full_name)
                
                if hasattr(self, 'driver_birth') and driver.driver_birth_date:
                    self.driver_birth.setDate(self._to_qdate(driver.driver_birth_date))
                
                if hasattr(self, 'driver_licence'):
                    self.driver_licence.setText(driver.driver_licence_number or '')
                
                if hasattr(self, 'driver_licence_cat'):
                    index = self.driver_licence_cat.findText(driver.driver_licence_category or '')
                    if index >= 0:
                        self.driver_licence_cat.setCurrentIndex(index)
                
                if hasattr(self, 'driver_licence_date') and driver.driver_licence_issued_at:
                    self.driver_licence_date.setDate(self._to_qdate(driver.driver_licence_issued_at))
                
                if hasattr(self, 'driver_licence_authority'):
                    self.driver_licence_authority.setText(driver.driver_licence_issued_by or '')
            
            # ============================================================
            # 9. GARANTIES
            # ============================================================
            if hasattr(vehicle, 'guarantees') and vehicle.guarantees:
                g = vehicle.guarantees
                self._load_guarantee_values(g)
            elif hasattr(vehicle, 'guarantee') and vehicle.guarantee:
                g = vehicle.guarantee
                self._load_guarantee_values(g)
            
            # ============================================================
            # 10. DATES
            # ============================================================
            if hasattr(self, 'date_debut') and vehicle.date_debut:
                self.date_debut.setDate(self._to_qdate(vehicle.date_debut))
            
            if hasattr(self, 'date_fin') and vehicle.date_fin:
                self.date_fin.setDate(self._to_qdate(vehicle.date_fin))
            
            if hasattr(self, 'nbr_jour') and vehicle.nbr_jour:
                self.nbr_jour.setText(str(vehicle.nbr_jour))
            
            # ============================================================
            # 11. FINANCES
            # ============================================================
            if hasattr(self, 'prime_brute') and vehicle.prime_brute:
                self.prime_brute.setText(f"{vehicle.prime_brute:,.0f}".replace(",", " "))
            
            if hasattr(self, 'reduction') and vehicle.reduction:
                self.reduction.setText(f"{vehicle.reduction:,.0f}".replace(",", " "))
            
            if hasattr(self, 'prime_nette') and vehicle.prime_nette:
                self.prime_nette.setText(f"{vehicle.prime_nette:,.0f}".replace(",", " "))
            
            if hasattr(self, 'accessoire') and vehicle.accessoires:
                self.accessoire.setText(f"{vehicle.accessoires:,.0f}".replace(",", " "))
            
            if hasattr(self, 'tva') and vehicle.tva:
                self.tva.setText(f"{vehicle.tva:,.0f}".replace(",", " "))
            
            if hasattr(self, 'asac') and vehicle.fichier_asac:
                self.asac.setText(f"{vehicle.fichier_asac:,.0f}".replace(",", " "))
            
            if hasattr(self, 'carte_rose') and vehicle.carte_rose:
                self.carte_rose.setText(f"{vehicle.carte_rose:,.0f}".replace(",", " "))
            
            if hasattr(self, 'vignette') and vehicle.vignette:
                self.vignette.setText(f"{vehicle.vignette:,.0f}".replace(",", " "))
            
            if hasattr(self, 'pttc') and vehicle.pttc:
                self.pttc.setText(f"{vehicle.pttc:,.0f}".replace(",", " "))
            
            print(f"✅ Données du véhicule {vehicle.immatriculation} chargées avec succès")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des données: {e}")
            import traceback
            traceback.print_exc()

    def _load_guarantee_values(self, guarantees):
        """
        Charge les valeurs des garanties dans le formulaire.
        
        Args:
            guarantees: Objet garantie (VehicleGuarantee)
        """
        try:
            # Mapping des clés garantie
            guarantee_map = {
                'rc': ('RC', 'Responsabilité Civile'),
                'dr': ('DR', 'Défense Recours'),
                'vol': ('VOL', 'Vol/Vol partie'),
                'vb': ('VB', 'Vol/Braquage'),
                'in': ('INC', 'Incendie'),
                'bris': ('BG', 'Bris de Glace'),
                'ar': ('AR', 'Assistance Réparation'),
                'dta': ('DTA', 'Dommages'),
                'ipt': ('IPT', 'Indiv. Personnes Transportées')
            }
            
            for key, (code, label) in guarantee_map.items():
                if key not in self.garanties_widgets:
                    continue
                
                garantie_widgets = self.garanties_widgets[key]
                checkbox = garantie_widgets['checkbox']
                montant_brut = garantie_widgets['montant_brut']
                taux_input = garantie_widgets['taux']
                montant_taux = garantie_widgets['montant_taux']
                montant_net = garantie_widgets['montant_net']
                
                # Récupérer les valeurs depuis l'objet garantie
                valeur_brute = getattr(guarantees, key, 0) or 0
                valeur_taux = getattr(guarantees, f'red_{key}', 0) or 0
                valeur_net = getattr(guarantees, f'net_{key}', 0) or 0
                valeur_reduction = getattr(guarantees, f'reduction_{key}', 0) or 0
                
                # Si la valeur brute est > 0, activer la garantie
                if valeur_brute > 0:
                    checkbox.setChecked(True)
                    montant_brut.setText(f"{valeur_brute:,.0f} FCFA".replace(",", " "))
                    montant_brut.setVisible(True)
                    
                    if valeur_taux > 0:
                        taux_input.setText(f"{valeur_taux}")
                    taux_input.setVisible(True)
                    
                    if valeur_reduction > 0:
                        montant_taux.setText(f"{valeur_reduction:,.0f} FCFA".replace(",", " "))
                    montant_taux.setVisible(True)
                    
                    if valeur_net > 0:
                        montant_net.setText(f"{valeur_net:,.0f} FCFA".replace(",", " "))
                    montant_net.setVisible(True)
                else:
                    checkbox.setChecked(False)
                    montant_brut.setVisible(False)
                    taux_input.setVisible(False)
                    montant_taux.setVisible(False)
                    montant_net.setVisible(False)
            
        except Exception as e:
            print(f"Erreur lors du chargement des garanties: {e}")

    def _load_company_by_id(self, compagny_id):
        """
        Charge les détails d'une compagnie par son ID.
        
        Args:
            compagny_id: ID de la compagnie
        """
        try:
            # Récupérer la compagnie depuis le contrôleur
            compagny = self.controller.vehicles.get_compagnie_by_id(compagny_id)
            if not compagny:
                return
            
            # Afficher dans la liste
            if hasattr(self, 'company_list'):
                for i in range(self.company_list.count()):
                    item = self.company_list.item(i)
                    if item and item.data(Qt.UserRole):
                        if item.data(Qt.UserRole).id == compagny_id:
                            self.company_list.setCurrentItem(item)
                            break
            
            # Mettre à jour les détails
            if hasattr(self, 'lbl_company_name'):
                self.lbl_company_name.setText(compagny.nom.upper())
            
            if hasattr(self, 'lbl_company_info'):
                info = f"""📌 Code: {compagny.code or 'N/A'}
    📞 Tél: {compagny.telephone or 'N/A'}
    📧 Email: {compagny.email or 'N/A'}
    📍 Adresse: {compagny.adresse or 'N/A'}"""
                self.lbl_company_info.setText(info)
            
            # Charger les tarifs de la compagnie
            self.load_tarif_codes_async()
            
        except Exception as e:
            print(f"Erreur chargement compagnie {compagny_id}: {e}")

    def freeze_ui(self):
        """Désactive tous les champs pour la consultation"""
        for widget in self.findChildren((QLineEdit, QComboBox, QTextEdit, QCheckBox, QDateEdit)):
            widget.setEnabled(False)
        for widget in self.findChildren(QListWidget):
            widget.setEnabled(False)
        if hasattr(self, 'btn_save'):
            self.btn_save.setEnabled(False)
        self.setWindowTitle("Consultation du véhicule")

    def _setup_footer(self, parent_layout):
        """Configure le pied de page"""
        footer = QHBoxLayout()
        footer.setContentsMargins(30, 20, 30, 30)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 6px;
                background-color: {Colors.GRAY_100};
                height: 8px;
                text-align: center;
                font-size: 10px;
                font-weight: 500;
                color: {Colors.TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK});
                border-radius: 6px;
            }}
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        
        self.btn_save = QPushButton("💾 ENREGISTRER LE VÉHICULE")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK});
                color: {Colors.WHITE};
                font-size: 15px;
                font-weight: bold;
                border-radius: 16px;
                padding: 14px 32px;
                font-family: 'Segoe UI';
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY_HOVER}, stop:1 {Colors.PRIMARY});
            }}
            QPushButton:pressed {{
                padding-top: 15px;
                padding-bottom: 13px;
            }}
        """)
        self.btn_save.clicked.connect(self.validate_and_save)
        
        footer.addStretch()
        footer.addWidget(self.progress_bar)
        footer.addStretch()
        footer.addWidget(self.btn_save)
        footer.addStretch()
        
        parent_layout.addLayout(footer)

    # ============================================================
    # MÉTHODES DE SAUVEGARDE (simplifiées)
    # ============================================================

    def get_form_data(self):
        """
        Récupère toutes les données du formulaire pour la sauvegarde
        
        Returns:
            dict: Dictionnaire des données du formulaire
        """
        data = {}
        
        # ============================================================
        # IDENTIFICATION
        # ============================================================
        if hasattr(self, 'immat_input'):
            data["immatriculation"] = self.immat_input.text().strip().upper()
        else:
            data["immatriculation"] = ""
        
        if hasattr(self, 'chassis_input'):
            data["chassis"] = self.chassis_input.text().strip().upper()
        else:
            data["chassis"] = ""
        
        if hasattr(self, 'marque_input'):
            data["marque"] = self.marque_input.text().strip()
        else:
            data["marque"] = ""
        
        if hasattr(self, 'modele_input'):
            data["modele"] = self.modele_input.text().strip()
        else:
            data["modele"] = ""
        
        if hasattr(self, 'annee_input'):
            data["annee"] = int(self.annee_input.text()) if self.annee_input.text().isdigit() else None
        else:
            data["annee"] = None
        
        if hasattr(self, 'date_mise_circulation'):
            data["date_mise_circulation"] = self.date_mise_circulation.date().toPython()
        else:
            data["date_mise_circulation"] = None
        
        # ============================================================
        # CLASSIFICATION ASAC
        # ============================================================
        if hasattr(self, 'asac_combo_cat'):
            cat_text = self.asac_combo_cat.currentText().strip()
            # Extraire le code avant le " - "
            data["categorie"] = cat_text.split(" - ")[0] if " - " in cat_text else cat_text
        elif hasattr(self, 'combo_cat'):
            cat_text = self.combo_cat.currentText().strip()
            data["categorie"] = cat_text.split(" - ")[0] if " - " in cat_text else cat_text
        else:
            data["categorie"] = ""
        
        if hasattr(self, 'combo_genre'):
            genre_text = self.combo_genre.currentText().strip()
            data["genre"] = genre_text.split(" - ")[0] if " - " in genre_text else genre_text
        else:
            data["genre"] = ""
        
        if hasattr(self, 'combo_type'):
            type_text = self.combo_type.currentText().strip()
            data["type_vehicule"] = type_text.split(" - ")[0] if " - " in type_text else type_text
        else:
            data["type_vehicule"] = ""
        
        if hasattr(self, 'combo_usage'):
            usage_text = self.combo_usage.currentText().strip()
            data["usage"] = usage_text.split(" - ")[0] if " - " in usage_text else usage_text
        else:
            data["usage"] = ""
        
        if hasattr(self, 'combo_energie'):
            energie_text = self.combo_energie.currentText().strip()
            data["energie"] = energie_text.split(" - ")[0] if " - " in energie_text else energie_text
        else:
            data["energie"] = ""
        
        if hasattr(self, 'combo_zone'):
            zone_text = self.combo_zone.currentText().strip()
            # Extraire la lettre après "ZA - Zone A" -> "A"
            if " - " in zone_text:
                # Prendre la dernière lettre (ex: "ZA" -> "A")
                code = zone_text.split(" - ")[0].strip()  # "ZA"
                data["zone"] = code[-1] if code else ""   # "A"
            else:
                # Si c'est déjà "A", "B" ou "C"
                data["zone"] = zone_text
        else:
            data["zone"] = ""
        
        # ============================================================
        # CARACTÉRISTIQUES TECHNIQUES
        # ============================================================
        if hasattr(self, 'usage_input'):
            data["puissance_fiscale"] = self.get_int_value(self.usage_input)
        else:
            data["puissance_fiscale"] = 0
        
        if hasattr(self, 'places_input'):
            data["places"] = self.get_int_value(self.places_input)
        else:
            data["places"] = 5
        
        if hasattr(self, 'cylindree_input'):
            data["cylindree"] = self.get_int_value(self.cylindree_input)
        else:
            data["cylindree"] = 0
        
        if hasattr(self, 'ptac_input'):
            data["ptac"] = self.get_int_value(self.ptac_input)
        else:
            data["ptac"] = 0
        
        if hasattr(self, 'charge_utile_input'):
            data["charge_utile"] = self.get_int_value(self.charge_utile_input)
        else:
            data["charge_utile"] = 0
        
        if hasattr(self, 'val_neuf'):
            data["valeur_neuf"] = self.get_float_value(self.val_neuf)
        else:
            data["valeur_neuf"] = 0
        
        if hasattr(self, 'val_venale'):
            data["valeur_venale"] = self.get_float_value(self.val_venale)
        else:
            data["valeur_venale"] = 0
        
        # ============================================================
        # OPTIONS
        # ============================================================
        if hasattr(self, 'check_remorque'):
            data["has_remorque"] = self.check_remorque.isChecked()
        else:
            data["has_remorque"] = False
        
        if hasattr(self, 'check_inflammable'):
            data["remorque_inflammable"] = self.check_inflammable.isChecked()
        else:
            data["remorque_inflammable"] = False
        
        if hasattr(self, 'check_double_commande'):
            data["double_commande"] = self.check_double_commande.isChecked()
        else:
            data["double_commande"] = False
        
        if hasattr(self, 'check_rc_eleves'):
            data["rc_eleves"] = self.check_rc_eleves.isChecked()
        else:
            data["rc_eleves"] = False
        
        if hasattr(self, 'check_engin_portuaire'):
            data["engin_portuaire"] = self.check_engin_portuaire.isChecked()
        else:
            data["engin_portuaire"] = False
        
        if hasattr(self, 'remorque_immat'):
            data["remorque_immat"] = self.remorque_immat.text().strip().upper()
        else:
            data["remorque_immat"] = ""
        
        # ============================================================
        # CODES TARIFAIRES
        # ============================================================
        if hasattr(self, 'code_tarif'):
            data["code_tarif"] = self.code_tarif.currentText().strip()
        else:
            data["code_tarif"] = ""
        
        if hasattr(self, 'combo_fleet'):
            data["libele_tarif"] = self.combo_fleet.currentText().strip()
        else:
            data["libele_tarif"] = ""
        
        if hasattr(self, 'code_assure'):
            data["code_assure"] = self.code_assure.text().strip()
        else:
            data["code_assure"] = ""
        
        # ============================================================
        # PROPRIÉTAIRES
        # ============================================================
        data["customer_id"] = getattr(self, 'selected_customer_id', None)
        data["insured_id"] = getattr(self, 'selected_insured_id', None)
        data["compagny_id"] = self.selected_cie_id if hasattr(self, 'selected_cie_id') else None
        data["owner_id"] = getattr(self, 'selected_customer_id', None)  # Alias pour compatibilité
        
        # ============================================================
        # CONDUCTEUR
        # ============================================================
        if hasattr(self, 'driver_name'):
            data["driver_name"] = self.driver_name.text().strip()
        else:
            data["driver_name"] = ""
        
        if hasattr(self, 'driver_birth'):
            data["driver_birth"] = self.driver_birth.date().toPython()
        else:
            data["driver_birth"] = None
        
        if hasattr(self, 'driver_licence'):
            data["driver_licence"] = self.driver_licence.text().strip()
        else:
            data["driver_licence"] = ""
        
        if hasattr(self, 'driver_licence_cat'):
            data["driver_licence_cat"] = self.driver_licence_cat.currentText()
        else:
            data["driver_licence_cat"] = ""
        
        if hasattr(self, 'driver_licence_date'):
            data["driver_licence_date"] = self.driver_licence_date.date().toPython()
        else:
            data["driver_licence_date"] = None
        
        if hasattr(self, 'driver_licence_authority'):
            data["driver_licence_authority"] = self.driver_licence_authority.text().strip()
        else:
            data["driver_licence_authority"] = ""
        
        # ============================================================
        # DATES
        # ============================================================
        if hasattr(self, 'date_debut'):
            data["date_debut"] = self.date_debut.date().toPython()
        else:
            data["date_debut"] = None
        
        if hasattr(self, 'date_fin'):
            data["date_fin"] = self.date_fin.date().toPython()
        else:
            data["date_fin"] = None
        
        if hasattr(self, 'nbr_jour'):
            data["nbr_jour"] = self.get_int_value(self.nbr_jour)
        else:
            data["nbr_jour"] = 0

        # ============================================================
        # CONDUCTEUR - Préparer les données pour la table Driver
        # ============================================================
        driver_data = {}
        
        if hasattr(self, 'driver_name'):
            driver_data["nom"] = self.driver_name.text().strip()
        else:
            driver_data["nom"] = ""
        
        if hasattr(self, 'driver_birth'):
            driver_data["date_naissance"] = self.driver_birth.date().toPython()
        else:
            driver_data["date_naissance"] = None
        
        if hasattr(self, 'driver_licence'):
            driver_data["num_permis"] = self.driver_licence.text().strip()
        else:
            driver_data["num_permis"] = ""
        
        if hasattr(self, 'driver_licence_cat'):
            driver_data["categorie_permis"] = self.driver_licence_cat.currentText()
        else:
            driver_data["categorie_permis"] = ""
        
        if hasattr(self, 'driver_licence_date'):
            driver_data["date_permis"] = self.driver_licence_date.date().toPython()
        else:
            driver_data["date_permis"] = None
        
        if hasattr(self, 'driver_licence_authority'):
            driver_data["autorite_delivrance"] = self.driver_licence_authority.text().strip()
        else:
            driver_data["autorite_delivrance"] = ""
        
        # Ajouter les données du conducteur au dictionnaire principal
        data["driver"] = driver_data
        
        # ============================================================
        # FINANCES (récupérées depuis les champs de l'onglet financier)
        # ============================================================
        if hasattr(self, 'prime_brute'):
            data["prime_brute"] = self.get_float_value(self.prime_brute)
        else:
            data["prime_brute"] = 0
        
        if hasattr(self, 'reduction'):
            data["reduction"] = self.get_float_value(self.reduction)
        else:
            data["reduction"] = 0
        
        if hasattr(self, 'prime_nette'):
            data["prime_nette"] = self.get_float_value(self.prime_nette)
        else:
            data["prime_nette"] = 0
        
        if hasattr(self, 'accessoire'):
            data["accessoires"] = self.get_float_value(self.accessoire)
        else:
            data["accessoires"] = 0
        
        if hasattr(self, 'tva'):
            data["tva"] = self.get_float_value(self.tva)
        else:
            data["tva"] = 0
        
        if hasattr(self, 'asac'):
            data["fichier_asac"] = self.get_float_value(self.asac)
        else:
            data["fichier_asac"] = 0
        
        if hasattr(self, 'carte_rose'):
            data["carte_rose"] = self.get_float_value(self.carte_rose)
        else:
            data["carte_rose"] = 0
        
        if hasattr(self, 'vignette'):
            data["vignette"] = self.get_float_value(self.vignette)
        else:
            data["vignette"] = 0
        
        if hasattr(self, 'pttc'):
            data["pttc"] = self.get_float_value(self.pttc)
        else:
            data["pttc"] = 0
        
        # ============================================================
        # GARANTIES
        # ============================================================
        for key, garantie in self.garanties_widgets.items():
            if garantie['checkbox'].isChecked():
                # Montant brut
                brut_text = garantie['montant_brut'].text()
                brut_text = brut_text.replace(" FCFA", "").replace(" ", "").replace(",", ".")
                data[f"amt_{key}_brut"] = float(brut_text) if brut_text else 0
                
                # Montant net
                net_text = garantie['montant_net'].text()
                net_text = net_text.replace(" FCFA", "").replace(" ", "").replace(",", ".")
                data[f"amt_{key}_net"] = float(net_text) if net_text else 0
                
                # Réduction
                red_text = garantie['montant_taux'].text()
                red_text = red_text.replace(" FCFA", "").replace(" ", "").replace(",", ".")
                data[f"amt_{key}_red"] = float(red_text) if red_text else 0
                
                # Taux
                taux_text = garantie['taux'].text().strip()
                if taux_text.endswith('%'):
                    taux_text = taux_text[:-1]
                data[f"red_{key}"] = float(taux_text) if taux_text else 0
            else:
                data[f"amt_{key}_brut"] = 0
                data[f"amt_{key}_net"] = 0
                data[f"amt_{key}_red"] = 0
                data[f"red_{key}"] = 0
        
        return data

    def _extract_zone(self, text: str) -> str:
        """
        Extrait la zone de circulation d'une chaîne du type "ZA - Zone A"
        
        Args:
            text: Chaîne contenant le code et le libellé
        
        Returns:
            str: Zone (ex: "A", "B" ou "C")
        """
        if not text:
            return ""
        if " - " in text:
            code = text.split(" - ")[0].strip()  # "ZA"
            return code[-1] if code else ""      # "A"
        return text.strip()

    def validate_and_save(self):
        """
        Valide et sauvegarde le véhicule avec toutes les données du formulaire
        Conforme aux spécifications API ASAC
        """
        print("🔍 validate_and_save() appelée")
        
        # ============================================================
        # 1. VALIDATION DES CHAMPS OBLIGATOIRES
        # ============================================================
        errors = []
        
        # Identification
        if not hasattr(self, 'immat_input') or not self.immat_input.text().strip():
            errors.append("❌ Immatriculation obligatoire")
        if not hasattr(self, 'chassis_input') or not self.chassis_input.text().strip():
            errors.append("❌ N° Châssis obligatoire")
        if not hasattr(self, 'marque_input') or not self.marque_input.text().strip():
            errors.append("❌ Marque obligatoire")
        if not hasattr(self, 'modele_input') or not self.modele_input.text().strip():
            errors.append("❌ Modèle obligatoire")
        
        # Classification ASAC
        if hasattr(self, 'combo_cat') and not self.combo_cat.currentText().strip():
            errors.append("❌ Catégorie obligatoire")
        if hasattr(self, 'combo_genre') and not self.combo_genre.currentText().strip():
            errors.append("❌ Genre obligatoire")
        if hasattr(self, 'combo_type') and not self.combo_type.currentText().strip():
            errors.append("❌ Type obligatoire")
        if hasattr(self, 'combo_usage') and not self.combo_usage.currentText().strip():
            errors.append("❌ Usage obligatoire")
        if hasattr(self, 'combo_energie') and not self.combo_energie.currentText().strip():
            errors.append("❌ Énergie obligatoire")
        if hasattr(self, 'combo_zone') and not self.combo_zone.currentText().strip():
            errors.append("❌ Zone de circulation obligatoire")
        
        # Caractéristiques
        if hasattr(self, 'usage_input') and not self.usage_input.text().strip():
            errors.append("❌ Puissance fiscale obligatoire")
        if hasattr(self, 'places_input') and not self.places_input.text().strip():
            errors.append("❌ Nombre de places obligatoire")
        if hasattr(self, 'val_neuf') and not self.val_neuf.text().strip():
            errors.append("❌ Valeur à neuf obligatoire")
        if hasattr(self, 'val_venale') and not self.val_venale.text().strip():
            errors.append("❌ Valeur vénale obligatoire")
        
        # Propriétaire (Souscripteur/Assuré)
        if hasattr(self, 'customer_list') and self.customer_list.currentItem() is None:
            errors.append("❌ Souscripteur obligatoire (sélectionnez un contact)")
        if hasattr(self, 'insured_list') and self.insured_list.currentItem() is None:
            errors.append("❌ Assuré obligatoire (sélectionnez un contact)")
        
        # Conducteur
        if hasattr(self, 'driver_name') and not self.driver_name.text().strip():
            errors.append("❌ Nom du conducteur obligatoire")
        if hasattr(self, 'driver_licence') and not self.driver_licence.text().strip():
            errors.append("❌ N° de permis obligatoire")
        if hasattr(self, 'driver_licence_cat') and not self.driver_licence_cat.currentText().strip():
            errors.append("❌ Catégorie du permis obligatoire")
        
        # Compagnie
        if hasattr(self, 'company_list') and self.company_list.currentItem() is None:
            errors.append("❌ Compagnie d'assurance obligatoire")
        
        # ============================================================
        # 2. AFFICHAGE DES ERREURS
        # ============================================================
        if errors:
            error_msg = "\n".join(errors)
            QMessageBox.warning(self, "Champs obligatoires", 
                f"Veuillez corriger les erreurs suivantes :\n\n{error_msg}")
            return
        
        # ============================================================
        # 3. CONFIRMATION DE L'UTILISATEUR
        # ============================================================
        mode_text = "modification" if self.mode == "edit" else "création"
        reply = QMessageBox.question(
            self, 
            "Confirmation",
            f"Voulez-vous confirmer la {mode_text} de ce véhicule ?\n\n"
            f"🚗 {self.immat_input.text().strip().upper()}\n"
            f"🏭 {self.marque_input.text().strip()} {self.modele_input.text().strip()}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # ============================================================
        # 4. PRÉPARATION DE L'UI
        # ============================================================
        self._prepare_save_ui()
        
        try:
            # ============================================================
            # 5. RÉCUPÉRATION DES DONNÉES DU FORMULAIRE
            # ============================================================
            data = self.get_form_data()
            
            # ============================================================
            # 6. INFORMATIONS RÉSEAU
            # ============================================================
            local_ip = socket.gethostbyname(socket.gethostname())
            public_ip = None
            try:
                public_ip = requests.get('https://api.ipify.org', timeout=1).text
            except Exception:
                public_ip = "Non disponible"
            
            current_user_id = getattr(self.current_user, 'id', 1)
            
            # ============================================================
            # 7. SAUVEGARDE
            # ============================================================
            self.progress_bar.setValue(30)
            
            def save_vehicle():
                from addons.Automobiles.controllers.automobile_controller import VehicleController
                from core.database import SessionLocal
                
                session = SessionLocal()
                try:
                    vehicle_ctrl = VehicleController(session)
                    
                    if self.vehicle_id:
                        # Mise à jour
                        return vehicle_ctrl.update_vehicle(
                            vehicle_id=self.vehicle_id,
                            new_data=data,
                            user_id=current_user_id,
                            local_ip=local_ip,
                            public_ip=public_ip
                        )
                    else:
                        # Création
                        return vehicle_ctrl.create_vehicle(
                            data=data,
                            user_id=current_user_id,
                            local_ip=local_ip,
                            public_ip=public_ip
                        )
                finally:
                    session.close()
            
            async_query.execute(
                save_vehicle,
                on_finished=self._on_save_finished,
                on_error=self._on_save_error,
                show_loader=True,
                loader_message="Enregistrement du véhicule..."
            )
            
        except Exception as e:
            self._reset_save_ui()
            QMessageBox.critical(self, "Erreur de sauvegarde", f"Détails : {str(e)}")
            import traceback
            traceback.print_exc()

    def _prepare_save_ui(self):
        """Prépare l'interface avant la sauvegarde"""
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.btn_save.setEnabled(False)
        self.btn_save.setText("⏳ Traitement en cours...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        QApplication.processEvents()

    def _reset_save_ui(self):
        """Réinitialise l'interface après la sauvegarde"""
        QApplication.restoreOverrideCursor()
        self.btn_save.setEnabled(True)
        self.btn_save.setText("💾 ENREGISTRER LE VÉHICULE")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def _on_save_finished(self, result):
        """Callback en cas de succès de la sauvegarde"""
        QApplication.restoreOverrideCursor()
        self.progress_bar.setValue(100)
        
        if not isinstance(result, (tuple, list)) or len(result) == 0:
            self._reset_save_ui()
            QMessageBox.critical(self, "Erreur de sauvegarde", "Résultat inattendu")
            return
        
        success = result[0]
        if success:
            message = result[1] if len(result) > 1 else "Véhicule enregistré avec succès"
            QMessageBox.information(self, "Succès", message)
            self.accept()
            return
        
        message = result[1] if len(result) > 1 else "Erreur inconnue"
        self._reset_save_ui()
        QMessageBox.critical(self, "Erreur de sauvegarde", f"Détails : {message}")

    def _on_save_error(self, error):
        """Callback en cas d'erreur de sauvegarde"""
        self._reset_save_ui()
        QMessageBox.critical(self, "Erreur de sauvegarde", f"Détails : {error}")

    # ============================================================
    # MÉTHODES À COMPLÉTER (onglets autres)
    # ============================================================
    
    def _create_identification_tab(self):
        """Crée l'onglet d'identification du véhicule avec ScrollArea"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ScrollArea pour tout le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3498db;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        # Style commun
        field_style = """
            QLineEdit, QComboBox, QDateEdit {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 10px 14px;
                background-color: white;
                font-size: 13px;
                color: #2d3748;
                font-family: 'Segoe UI';
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #3498db;
                background-color: #f0f9ff;
            }
            QLabel {
                color: #4a5568;
                font-weight: 600;
                font-size: 12px;
                margin-bottom: 4px;
            }
        """
        
        group_style = """
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                margin-top: 12px;
                padding-top: 12px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 12px 0 12px;
                color: #2c3e50;
            }
        """
        
        # Groupe: Immatriculation et identification
        group_id = QGroupBox("🔑 Identification du véhicule")
        group_id.setStyleSheet(group_style)
        
        id_layout = QGridLayout(group_id)
        id_layout.setSpacing(15)
        id_layout.setContentsMargins(25, 25, 25, 25)
        
        # Ligne 1: Immatriculation et Châssis
        id_layout.addWidget(self._create_label("🔢", "Immatriculation *"), 0, 0)
        id_layout.addWidget(self._create_label("🔧", "N° Châssis *"), 0, 1)
        
        self.immat_input = QLineEdit()
        self.immat_input.setPlaceholderText("EX: LS-123-AB")
        self.immat_input.setStyleSheet(field_style)
        self.immat_input.textChanged.connect(self._on_immat_change)
        id_layout.addWidget(self.immat_input, 1, 0)
        
        self.chassis_input = QLineEdit()
        self.chassis_input.setPlaceholderText("N° de châssis du véhicule")
        self.chassis_input.setStyleSheet(field_style)
        id_layout.addWidget(self.chassis_input, 1, 1)
        
        # Ligne 2: Marque, Modèle, Année
        id_layout.addWidget(self._create_label("🏭", "Marque *"), 2, 0)
        id_layout.addWidget(self._create_label("📱", "Modèle *"), 2, 1)
        id_layout.addWidget(self._create_label("📅", "Année"), 2, 2)
        
        self.marque_input = QLineEdit()
        self.marque_input.setPlaceholderText("EX: TOYOTA")
        self.marque_input.setStyleSheet(field_style)
        id_layout.addWidget(self.marque_input, 3, 0)
        
        self.modele_input = QLineEdit()
        self.modele_input.setPlaceholderText("EX: COROLLA")
        self.modele_input.setStyleSheet(field_style)
        id_layout.addWidget(self.modele_input, 3, 1)
        
        self.annee_input = QLineEdit()
        self.annee_input.setPlaceholderText("2024")
        self.annee_input.setStyleSheet(field_style)
        id_layout.addWidget(self.annee_input, 3, 2)
        
        # Ligne 3: Date première mise en circulation
        id_layout.addWidget(self._create_label("📅", "1ère mise en circulation"), 4, 0)
        
        self.date_mise_circulation = QDateEdit()
        self.date_mise_circulation.setDisplayFormat("dd/MM/yyyy")
        self.date_mise_circulation.setCalendarPopup(True)
        self.date_mise_circulation.setDate(QDate.currentDate().addYears(-5))
        self.date_mise_circulation.setStyleSheet(field_style)
        id_layout.addWidget(self.date_mise_circulation, 5, 0)
        
        content_layout.addWidget(group_id)
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        return tab

    def on_code_tarif_changed(self, code):
        """Charge les catégories liées au code tarif"""
        if code and self.selected_cie_id:
            self.load_tarif_categories_by_code_async(code)

    def _create_technical_tab(self):
        """Crée l'onglet des caractéristiques techniques avec ScrollArea"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ScrollArea pour tout le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3498db;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        field_style = """
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 10px 14px;
                background-color: white;
                font-size: 13px;
                color: #2d3748;
                font-family: 'Segoe UI';
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3498db;
                background-color: #f0f9ff;
            }
            QLabel {
                color: #4a5568;
                font-weight: 600;
                font-size: 12px;
                margin-bottom: 4px;
            }
        """
        
        group_style = """
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                margin-top: 12px;
                padding-top: 12px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 12px 0 12px;
                color: #2c3e50;
            }
        """
        
        # Groupe: Caractéristiques techniques
        group_tech = QGroupBox("⚙️ Caractéristiques techniques")
        group_tech.setStyleSheet(group_style)
        
        tech_layout = QGridLayout(group_tech)
        tech_layout.setSpacing(15)
        tech_layout.setContentsMargins(25, 25, 25, 25)
        
        # Puissance fiscale
        tech_layout.addWidget(self._create_label("⚡", "Puissance fiscale (CV) *"), 0, 0)
        self.usage_input = QLineEdit()
        self.usage_input.setPlaceholderText("Ex: 7")
        self.usage_input.setStyleSheet(field_style)
        self.usage_input.textChanged.connect(self.on_power_changed)
        tech_layout.addWidget(self.usage_input, 1, 0)
        
        # Nombre de places
        tech_layout.addWidget(self._create_label("👥", "Nombre de places *"), 0, 1)
        self.places_input = QLineEdit()
        self.places_input.setPlaceholderText("5")
        self.places_input.setStyleSheet(field_style)
        tech_layout.addWidget(self.places_input, 1, 1)
        
        # Cylindrée
        tech_layout.addWidget(self._create_label("🔧", "Cylindrée (cm³)"), 2, 0)
        self.cylindree_input = QLineEdit()
        self.cylindree_input.setPlaceholderText("Ex: 1600")
        self.cylindree_input.setStyleSheet(field_style)
        tech_layout.addWidget(self.cylindree_input, 3, 0)
        
        # PTAC
        tech_layout.addWidget(self._create_label("📊", "PTAC (kg)"), 2, 1)
        self.ptac_input = QLineEdit()
        self.ptac_input.setPlaceholderText("Poids total autorisé en charge")
        self.ptac_input.setStyleSheet(field_style)
        tech_layout.addWidget(self.ptac_input, 3, 1)
        
        # Charge utile
        tech_layout.addWidget(self._create_label("📦", "Charge utile (kg)"), 4, 0)
        self.charge_utile_input = QLineEdit()
        self.charge_utile_input.setPlaceholderText("Capacité de charge")
        self.charge_utile_input.setStyleSheet(field_style)
        tech_layout.addWidget(self.charge_utile_input, 5, 0)
        
        content_layout.addWidget(group_tech)
        
        # Groupe: Valeurs
        group_values = QGroupBox("💰 Valeurs")
        group_values.setStyleSheet(group_style)
        
        values_layout = QGridLayout(group_values)
        values_layout.setSpacing(15)
        values_layout.setContentsMargins(25, 25, 25, 25)
        
        # Valeur à neuf
        values_layout.addWidget(self._create_label("💎", "Valeur à neuf (FCFA) *"), 0, 0)
        self.val_neuf = QLineEdit()
        self.val_neuf.setPlaceholderText("0")
        self.val_neuf.setStyleSheet(field_style)
        self.val_neuf.textChanged.connect(self.refresh_all_garanties)
        values_layout.addWidget(self.val_neuf, 1, 0)
        
        # Valeur vénale
        values_layout.addWidget(self._create_label("📉", "Valeur vénale (FCFA) *"), 0, 1)
        self.val_venale = QLineEdit()
        self.val_venale.setPlaceholderText("0")
        self.val_venale.setStyleSheet(field_style)
        self.val_venale.textChanged.connect(self.refresh_all_garanties)
        values_layout.addWidget(self.val_venale, 1, 1)
        
        content_layout.addWidget(group_values)
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        return tab

    def handle_garantie_click(self, key, state):
        """
        Gère le clic sur une garantie
        
        Args:
            key: Identifiant de la garantie (rc, dr, vol, etc.)
            state: État de la checkbox (0=décoché, 2=coché)
        """
        is_checked = state == 2  # Qt.Checked
        
        garantie = self.garanties_widgets.get(key)
        if not garantie:
            return
        
        # Récupérer les widgets
        montant_brut = garantie['montant_brut']
        taux_input = garantie['taux']
        montant_taux = garantie['montant_taux']
        montant_net = garantie['montant_net']
        
        if is_checked:
            # ✅ Garantie activée - Afficher tous les champs
            montant_brut.setVisible(True)
            taux_input.setVisible(True)
            montant_taux.setVisible(True)
            montant_net.setVisible(True)
            
            # Calculer le montant brut (appel à la méthode de calcul)
            self.update_garantie_price(key, state)
            
        else:
            # ❌ Garantie désactivée - Cacher tous les champs
            montant_brut.setVisible(False)
            taux_input.setVisible(False)
            montant_taux.setVisible(False)
            montant_net.setVisible(False)
            
            # Réinitialiser les valeurs
            montant_brut.setText("0 FCFA")
            montant_taux.setText("0 FCFA")
            montant_net.setText("0 FCFA")
            taux_input.setText("")
            
            # Mettre à jour le total
            self.calculate_total_premium()

    def update_garantie_price(self, key, state):
        """
        Met à jour le prix d'une garantie
        
        Args:
            key: Identifiant de la garantie
            state: État de la checkbox
        """
        if not state:  # Si désactivé
            return
        
        garantie = self.garanties_widgets.get(key)
        if not garantie:
            return
        
        try:
            # Calculer le prorata
            prorata = self.calculate_prorata()
            
            # Calculer le montant brut
            montant_brut = self.calculate_garantie_amount(key, prorata)
            
            # Mettre à jour le label du montant brut
            garantie['montant_brut'].setText(f"{montant_brut:,.0f} FCFA".replace(",", " "))
            garantie['montant_brut'].setVisible(True)
            
            # Activer les autres champs
            garantie['taux'].setVisible(True)
            garantie['montant_taux'].setVisible(True)
            garantie['montant_net'].setVisible(True)
            
            # Calculer le montant net initial (sans réduction)
            self.update_net_amount(key)
            
            # Mettre à jour le total
            self.calculate_total_premium()
            
        except Exception as e:
            print(f"Erreur lors du calcul de la garantie {key}: {e}")

    def update_net_amount(self, key):
        """
        Met à jour le montant net après application du taux
        
        Args:
            key: Identifiant de la garantie
        """
        garantie = self.garanties_widgets.get(key)
        if not garantie:
            return
        
        try:
            # Récupérer le montant brut
            brut_text = garantie['montant_brut'].text()
            brut_text = brut_text.replace(" FCFA", "").replace(" ", "").replace(",", ".")
            montant_brut = float(brut_text) if brut_text else 0
            
            # Récupérer le taux
            taux_text = garantie['taux'].text().strip()
            if taux_text.endswith('%'):
                taux_text = taux_text[:-1]
            taux = float(taux_text) if taux_text else 0
            
            # Calculer la réduction et le montant net
            if taux > 0:
                reduction = montant_brut * (taux / 100)
                montant_net = montant_brut - reduction
            else:
                reduction = 0
                montant_net = montant_brut
            
            # Mettre à jour les labels
            garantie['montant_taux'].setText(f"{reduction:,.0f} FCFA".replace(",", " "))
            garantie['montant_net'].setText(f"{montant_net:,.0f} FCFA".replace(",", " "))
            
            # Mettre à jour le total
            self.calculate_total_premium()
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour du net pour {key}: {e}")

    def calculate_total_premium(self):
        """
        Calcule le total des primes (brut, net, réduction)
        """
        try:
            total_brut = 0
            total_net = 0
            total_reduction = 0
            
            for key, garantie in self.garanties_widgets.items():
                # Vérifier si la garantie est active
                if garantie['checkbox'].isChecked():
                    # Brut
                    brut_text = garantie['montant_brut'].text()
                    brut_text = brut_text.replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    montant_brut = float(brut_text) if brut_text else 0
                    total_brut += montant_brut
                    
                    # Net
                    net_text = garantie['montant_net'].text()
                    net_text = net_text.replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    montant_net = float(net_text) if net_text else 0
                    total_net += montant_net
                    
                    # Réduction
                    red_text = garantie['montant_taux'].text()
                    red_text = red_text.replace(" FCFA", "").replace(" ", "").replace(",", ".")
                    montant_red = float(red_text) if red_text else 0
                    total_reduction += montant_red
            
            # Mettre à jour les champs de récapitulatif
            self.prime_brute.setText(f"{total_brut:,.0f}".replace(",", " "))
            self.prime_nette.setText(f"{total_net:,.0f}".replace(",", " "))
            self.reduction.setText(f"{total_reduction:,.0f}".replace(",", " "))
            
            # Recalculer la TVA et le PTTC
            self.calculate_tva()
            self.calculate_pttc()
            
        except Exception as e:
            print(f"Erreur lors du calcul du total: {e}")

    def calculate_garantie_amount(self, key, prorata):
        """
        Calcule le montant brut d'une garantie
        
        Args:
            key: Identifiant de la garantie
            prorata: Facteur de prorata
        
        Returns:
            float: Montant brut calculé
        """
        v_venale = self.get_float_value(self.val_venale)
        v_neuf = self.get_float_value(self.val_neuf)
        
        if key == "rc":
            return self.calculate_rc_brut() * prorata
        elif key == "dr":
            return (self.calculate_rc_brut() * prorata ) * 0.03 * prorata
        elif key == "vol":
            return v_venale * 0.02 * prorata
        elif key == "vb":
            return v_venale * 0.02 * prorata
        elif key == "in":
            return v_venale * 0.025 * prorata
        elif key == "bris":
            return v_neuf * 0.005 * prorata
        elif key == "ar":
            return v_venale * 0.75 * 0.03 * prorata
        elif key == "dta":
            return v_neuf * 0.05 * prorata
        elif key == "ipt":
            places = int(self.places_input.text()) if self.places_input.text().isdigit() else 5
            if places <= 5:
                return 7500 * prorata
            else:
                return (7500 * places / 5) * prorata
        return 0

    def _create_guarantees_tab(self):
        """Crée l'onglet des garanties avec ScrollArea"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ScrollArea pour tout le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3498db;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        field_style = """
            QLineEdit, QComboBox, QDateEdit {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 10px 14px;
                background-color: white;
                font-size: 13px;
                color: #2d3748;
                font-family: 'Segoe UI';
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #3498db;
                background-color: #f0f9ff;
            }
            QLabel {
                color: #4a5568;
                font-weight: 600;
                font-size: 12px;
                margin-bottom: 4px;
            }
        """
        
        group_style = """
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                margin-top: 12px;
                padding-top: 12px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 12px 0 12px;
                color: #2c3e50;
            }
        """
        
        # ============================================================
        # GROUPE: INFORMATIONS TARIFAIRES
        # ============================================================
        group_tarif = QGroupBox("📋 Informations tarifaires")
        group_tarif.setStyleSheet(group_style)
        
        tarif_layout = QGridLayout(group_tarif)
        tarif_layout.setSpacing(15)
        tarif_layout.setContentsMargins(25, 25, 25, 25)
        
        # Code tarif
        tarif_layout.addWidget(self._create_label("📋", "Code Tarif"), 0, 0)
        self.code_tarif = QComboBox()
        self.code_tarif.setStyleSheet(field_style)
        self.code_tarif.setEditable(True)
        self.code_tarif.setPlaceholderText("Code ministériel du tarif...")
        self.code_tarif.currentTextChanged.connect(self.on_code_tarif_changed)
        tarif_layout.addWidget(self.code_tarif, 1, 0)
        
        # Libellé tarif
        tarif_layout.addWidget(self._create_label("📝", "Libellé Tarif"), 0, 1)
        self.combo_fleet = QComboBox()
        self.combo_fleet.setStyleSheet(field_style)
        self.combo_fleet.setEditable(True)
        self.combo_fleet.setPlaceholderText("Ex: Tarif Standard, Tarif Premium...")
        self.combo_fleet.currentTextChanged.connect(self.on_fleet_changed)
        tarif_layout.addWidget(self.combo_fleet, 1, 1)
        
        # Catégorie
        tarif_layout.addWidget(self._create_label("🏷️", "Catégorie *"), 2, 0)
        self.combo_cat = QComboBox()
        self.combo_cat.setStyleSheet(field_style)
        self.combo_cat.setEditable(True)
        self.combo_cat.addItem("", "")
        for code, label in self.ASAC_VEHICLE_CATEGORIES.items():
            self.combo_cat.addItem(f"{code} - {label}", code)
        self.combo_cat.currentTextChanged.connect(self.on_category_changed)
        tarif_layout.addWidget(self.combo_cat, 3, 0)
        
        # Code assuré
        tarif_layout.addWidget(self._create_label("🏷️", "Code Assuré"), 2, 1)
        self.code_assure = QLineEdit()
        self.code_assure.setPlaceholderText("Code interne de l'assuré")
        self.code_assure.setStyleSheet(field_style)
        tarif_layout.addWidget(self.code_assure, 3, 1)
        
        content_layout.addWidget(group_tarif)
        
        # ============================================================
        # GROUPE: GARANTIES
        # ============================================================
        group_garanties = QGroupBox("🛡️ Garanties & Cotisations")
        group_garanties.setStyleSheet(group_style)
        
        garanties_layout = QGridLayout(group_garanties)
        garanties_layout.setSpacing(12)
        garanties_layout.setContentsMargins(25, 25, 25, 25)
        
        # En-tête du tableau
        headers = ["Garantie", "Code", "Montant Brut", "Taux %", "Réduction", "Montant Net"]
        for col, header in enumerate(headers):
            label = QLabel(header)
            label.setStyleSheet("""
                font-weight: 700;
                color: #2c3e50;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            """)
            garanties_layout.addWidget(label, 0, col)
        
        # Liste des garanties
        garanties = [
            ("rc", "RC", "Responsabilité Civile"),
            ("dr", "DR", "Défense Recours"),
            ("vol", "VOL", "Vol/Vol partie"),
            ("vb", "VB", "Vol/Braquage"),
            ("in", "INC", "Incendie"),
            ("bris", "BG", "Bris de Glace"),
            ("ar", "AR", "Assistance Réparation"),
            ("dta", "DTA", "Dommages"),
            ("ipt", "IPT", "Indiv. Personnes Transportées")
        ]
        
        for i, (key, code, label_text) in enumerate(garanties):
            row = i + 1
            
            # Checkbox
            checkbox = QCheckBox(label_text)
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 12px;
                    font-weight: 600;
                    color: #4a5568;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 4px;
                    border: 2px solid #cbd5e0;
                }
                QCheckBox::indicator:checked {
                    background-color: #3498db;
                    border-color: #3498db;
                }
            """)
            checkbox.stateChanged.connect(lambda state, k=key: self.handle_garantie_click(k, state))
            setattr(self, f"check_{key}", checkbox)
            garanties_layout.addWidget(checkbox, row, 0)
            
            # Code
            code_label = QLabel(code)
            code_label.setStyleSheet("font-weight: 600; color: #64748b;")
            garanties_layout.addWidget(code_label, row, 1)
            
            # Montant brut
            montant_brut = QLabel("0 FCFA")
            montant_brut.setStyleSheet("""
                color: #27ae60;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 6px;
            """)
            montant_brut.setVisible(False)
            garanties_layout.addWidget(montant_brut, row, 2)
            
            # Taux
            taux_input = QLineEdit()
            taux_input.setPlaceholderText("0")
            taux_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 6px 10px;
                    font-size: 12px;
                    max-width: 80px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                }
            """)
            taux_input.setVisible(False)
            taux_input.textChanged.connect(lambda text, k=key: self.update_net_amount(k))
            garanties_layout.addWidget(taux_input, row, 3)
            
            # Réduction (montant)
            montant_taux = QLabel("0 FCFA")
            montant_taux.setStyleSheet("""
                color: #e67e22;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 6px;
            """)
            montant_taux.setVisible(False)
            garanties_layout.addWidget(montant_taux, row, 4)
            
            # Montant net
            montant_net = QLabel("0 FCFA")
            montant_net.setStyleSheet("""
                color: #2563eb;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 6px;
            """)
            montant_net.setVisible(False)
            garanties_layout.addWidget(montant_net, row, 5)
            
            # Stocker les références
            self.garanties_widgets[key] = {
                'checkbox': checkbox,
                'montant_brut': montant_brut,
                'taux': taux_input,
                'montant_taux': montant_taux,
                'montant_net': montant_net
            }
        
        content_layout.addWidget(group_garanties)
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        return tab

    def get_int_value(self, widget):
        """Récupère une valeur int d'un widget"""
        try:
            if not widget or not widget.text():
                return 0
            return int(widget.text())
        except:
            return 0
    
    def get_float_value(self, widget):
        """Récupère une valeur float d'un widget"""
        try:
            if not widget or not widget.text():
                return 0.0
            txt = widget.text().strip().replace(" ", "").replace(",", ".")
            return float(txt) if txt else 0.0
        except:
            return 0.0

    def calculate_rc_brut(self):
        """Calcule le montant brut de la RC"""
        try:
            if not self.selected_cie_id:
                return 0
                
            # Récupérer les paramètres
            code_tarif = self.code_tarif.currentText().strip() if hasattr(self.code_tarif, 'currentText') else ""
            categorie = self.combo_cat.currentText().strip()
            avec_remorque = self.check_remorque.isChecked()
            zone = self.combo_zone.currentText()
            energie = self.combo_energie.currentText()
            cv = self.get_int_value(self.usage_input)
            
            # Appeler la méthode du contrôleur
            res_rc = self.controller.vehicles.get_rc_premium_from_matrix(
                cie_id=self.selected_cie_id,
                zone_saisie=zone,
                categorie=categorie,
                energie=energie,
                cv_saisi=cv,
                avec_remorque=avec_remorque,
                code_tarif=code_tarif if code_tarif else None
            )
            
            # Récupérer le montant
            montant_rc = res_rc.get('rc', 0.0)
            
            # Mettre à jour le libellé et la catégorie si nécessaire
            libelle = res_rc.get('libelle', '')
            categorie_retournee = res_rc.get('categorie', '')
            
            if libelle and self.combo_fleet.currentText() != libelle:
                self.combo_fleet.setCurrentText(libelle)
            
            if categorie_retournee and self.combo_cat.currentText() != categorie_retournee:
                self.combo_cat.setCurrentText(categorie_retournee)
            
            return montant_rc
            
        except Exception as e:
            print(f"Erreur lors du calcul RC : {e}")
            return 0

    def _create_financial_tab(self):
        """Crée l'onglet financier avec ScrollArea"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ScrollArea pour tout le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f2f6;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3498db;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        group_style = """
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                margin-top: 12px;
                padding-top: 12px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 12px 0 12px;
                color: #2c3e50;
            }
        """
        
        field_style = """
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 10px 14px;
                background-color: white;
                font-size: 13px;
                color: #2d3748;
                font-family: 'Segoe UI';
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #f0f9ff;
            }
            QLabel {
                color: #4a5568;
                font-weight: 600;
                font-size: 12px;
                margin-bottom: 4px;
            }
        """
        
        # Styles spécifiques
        style_primary = """
            QLineEdit {
                background-color: #eff6ff;
                color: #1e40af;
                font-weight: bold;
                border: 2px solid #bfdbfe;
                border-radius: 12px;
                padding: 12px;
                font-size: 16px;
            }
        """
        
        style_success = """
            QLineEdit {
                background-color: #f0fdf4;
                color: #166534;
                font-weight: bold;
                border: 2px solid #bbf7d0;
                border-radius: 12px;
                padding: 12px;
                font-size: 18px;
            }
        """
        
        style_warning = """
            QLineEdit {
                background-color: #fffbeb;
                color: #b45309;
                font-weight: bold;
                border: 2px solid #fde68a;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
            }
        """
        
        # Groupe: Récapitulatif
        group_recap = QGroupBox("🧮 Récapitulatif financier")
        group_recap.setStyleSheet(group_style)
        
        recap_layout = QGridLayout(group_recap)
        recap_layout.setSpacing(15)
        recap_layout.setContentsMargins(25, 25, 25, 25)
        
        # Prime brute
        recap_layout.addWidget(self._create_label("📊", "Prime brute (FCFA)"), 0, 0)
        self.prime_brute = QLineEdit("0")
        self.prime_brute.setReadOnly(True)
        self.prime_brute.setStyleSheet(style_primary)
        self.prime_brute.setAlignment(Qt.AlignRight)
        recap_layout.addWidget(self.prime_brute, 1, 0)
        
        # Réduction
        recap_layout.addWidget(self._create_label("📉", "Réduction (FCFA)"), 0, 1)
        self.reduction = QLineEdit("0")
        self.reduction.setReadOnly(True)
        self.reduction.setStyleSheet(style_warning)
        self.reduction.setAlignment(Qt.AlignRight)
        recap_layout.addWidget(self.reduction, 1, 1)
        
        # Prime nette
        recap_layout.addWidget(self._create_label("✅", "Prime nette (FCFA)"), 0, 2)
        self.prime_nette = QLineEdit("0")
        self.prime_nette.setReadOnly(True)
        self.prime_nette.setStyleSheet(style_success)
        self.prime_nette.setAlignment(Qt.AlignRight)
        recap_layout.addWidget(self.prime_nette, 1, 2)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; margin: 10px 0;")
        recap_layout.addWidget(sep, 2, 0, 1, 3)
        
        # Taxe et accessoires
        recap_layout.addWidget(self._create_label("📋", "Accessoires (FCFA)"), 3, 0)
        self.accessoire = QLineEdit("0")
        self.accessoire.setStyleSheet(field_style)
        self.accessoire.setAlignment(Qt.AlignRight)
        self.accessoire.textChanged.connect(self.calculate_tva)
        self.accessoire.textChanged.connect(self.calculate_pttc)
        recap_layout.addWidget(self.accessoire, 4, 0)
        
        recap_layout.addWidget(self._create_label("📋", "Fichier ASAC (FCFA)"), 3, 1)
        self.asac = QLineEdit("0")
        self.asac.setStyleSheet(field_style)
        self.asac.setAlignment(Qt.AlignRight)
        self.asac.textChanged.connect(self.calculate_tva)
        self.asac.textChanged.connect(self.calculate_pttc)
        recap_layout.addWidget(self.asac, 4, 1)
        
        recap_layout.addWidget(self._create_label("📋", "TVA (19.25%)"), 3, 2)
        self.tva = QLineEdit("0")
        self.tva.setReadOnly(True)
        self.tva.setStyleSheet(field_style)
        self.tva.setAlignment(Qt.AlignRight)
        recap_layout.addWidget(self.tva, 4, 2)
        
        # Séparateur
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("background: #e2e8f0; margin: 10px 0;")
        recap_layout.addWidget(sep2, 5, 0, 1, 3)
        
        # Autres frais
        recap_layout.addWidget(self._create_label("📋", "Carte Rose (FCFA)"), 6, 0)
        self.carte_rose = QLineEdit("0")
        self.carte_rose.setStyleSheet(field_style)
        self.carte_rose.setAlignment(Qt.AlignRight)
        self.carte_rose.textChanged.connect(self.calculate_pttc)
        recap_layout.addWidget(self.carte_rose, 7, 0)
        
        recap_layout.addWidget(self._create_label("📋", "Vignette (FCFA)"), 6, 1)
        self.vignette = QLineEdit("0")
        self.vignette.setStyleSheet(field_style)
        self.vignette.setAlignment(Qt.AlignRight)
        self.vignette.textChanged.connect(self.calculate_pttc)
        recap_layout.addWidget(self.vignette, 7, 1)
        
        # PTTC
        recap_layout.addWidget(self._create_label("💰", "PTTC (FCFA)"), 6, 2)
        self.pttc = QLineEdit("0")
        self.pttc.setReadOnly(True)
        self.pttc.setStyleSheet("""
            QLineEdit {
                background-color: #fef3c7;
                color: #b45309;
                font-weight: bold;
                border: 2px solid #fde68a;
                border-radius: 12px;
                padding: 12px;
                font-size: 18px;
            }
        """)
        self.pttc.setAlignment(Qt.AlignRight)
        recap_layout.addWidget(self.pttc, 7, 2)
        
        # Séparateur
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.HLine)
        sep3.setStyleSheet("background: #e2e8f0; margin: 10px 0;")
        recap_layout.addWidget(sep3, 8, 0, 1, 3)
        
        # Dates
        recap_layout.addWidget(self._create_label("📅", "Date début"), 9, 0)
        self.date_debut = QDateEdit()
        self.date_debut.setDisplayFormat("dd/MM/yyyy")
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate())
        self.date_debut.setStyleSheet(field_style)
        self.date_debut.dateChanged.connect(self.on_date_changed)
        recap_layout.addWidget(self.date_debut, 10, 0)
        
        recap_layout.addWidget(self._create_label("📅", "Date fin"), 9, 1)
        self.date_fin = QDateEdit()
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate().addYears(1))
        self.date_fin.setStyleSheet(field_style)
        self.date_fin.dateChanged.connect(self.on_date_changed)
        recap_layout.addWidget(self.date_fin, 10, 1)
        
        recap_layout.addWidget(self._create_label("📊", "Jours"), 9, 2)
        self.nbr_jour = QLineEdit("0")
        self.nbr_jour.setReadOnly(True)
        self.nbr_jour.setStyleSheet(field_style)
        self.nbr_jour.setAlignment(Qt.AlignRight)
        recap_layout.addWidget(self.nbr_jour, 10, 2)
        
        content_layout.addWidget(group_recap)
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        return tab

    def _on_tarif_categories_loaded(self, categories):
        get_global_loader().hide_loading()
        self._populate_category_combobox(categories, keep_current=False)

        if categories:
            first_category = str(categories[0]).strip()
            if first_category:
                self.combo_cat.setCurrentText(first_category)

    def _populate_category_combobox(self, categories, keep_current=False):
        current_value = self.combo_cat.currentText() if keep_current else None
        self.combo_cat.clear()
        self.combo_cat.addItem("", "")

        unique_categories = sorted({str(c).strip() for c in categories if c})
        for categorie in unique_categories:
            self.combo_cat.addItem(categorie)

        if current_value:
            self.combo_cat.setCurrentText(current_value)

    