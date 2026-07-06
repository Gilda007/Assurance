
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QProgressBar,
    QMessageBox, QFrame, QComboBox, QRadioButton, QTabWidget,
    QScrollArea, QSplitter, QTextEdit, QCheckBox, QHeaderView,
    QWidget, QApplication, QLineEdit, QDateEdit, QGridLayout,
    QGroupBox, QSizePolicy, QSpacerItem, QMenu, QInputDialog
)
from PySide6.QtCore import Qt, Signal, QThread, QDate, QSettings
from PySide6.QtGui import QFont, QColor, QPalette, QAction
import pandas as pd
import traceback
from datetime import datetime
import os
import warnings

# Supprimer les avertissements Wayland
os.environ["QT_LOGGING_RULES"] = "qt.qpa.wayland.*=false"
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["XDG_SESSION_TYPE"] = "x11"
os.environ["GDK_BACKEND"] = "x11"
warnings.filterwarnings("ignore")


# ============================================================================
# STYLES MODERNES
# ============================================================================

class AppColors:
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1d4ed8"
    PRIMARY_LIGHT = "#eff6ff"
    SECONDARY = "#64748b"
    SUCCESS = "#10b981"
    SUCCESS_DARK = "#059669"
    SUCCESS_LIGHT = "#d1fae5"
    WARNING = "#f59e0b"
    WARNING_LIGHT = "#fef3c7"
    DANGER = "#ef4444"
    DANGER_LIGHT = "#fee2e2"
    DARK = "#0f172a"
    GRAY = "#64748b"
    GRAY_LIGHT = "#f1f5f9"
    WHITE = "#ffffff"
    BORDER = "#e2e8f0"


STYLESHEET = f"""
    QDialog {{
        background: {AppColors.GRAY_LIGHT};
    }}
    QGroupBox {{
        font-weight: 600;
        border: 1px solid {AppColors.BORDER};
        border-radius: 12px;
        margin-top: 12px;
        padding-top: 12px;
        background: {AppColors.WHITE};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 12px;
        color: {AppColors.DARK};
    }}
    QLineEdit, QComboBox, QDateEdit, QTextEdit {{
        border: 1px solid {AppColors.BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        background: {AppColors.WHITE};
        font-size: 13px;
    }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border-color: {AppColors.PRIMARY};
    }}
    QPushButton {{
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background: {AppColors.GRAY_LIGHT};
    }}
    .BtnPrimary {{
        background: {AppColors.PRIMARY};
        color: white;
    }}
    .BtnPrimary:hover {{
        background: {AppColors.PRIMARY_DARK};
    }}
    .BtnSuccess {{
        background: {AppColors.SUCCESS};
        color: white;
    }}
    .BtnSuccess:hover {{
        background: {AppColors.SUCCESS_DARK};
    }}
    .BtnSecondary {{
        background: {AppColors.WHITE};
        color: {AppColors.GRAY};
        border: 1px solid {AppColors.BORDER};
    }}
    .BtnWarning {{
        background: {AppColors.WARNING};
        color: white;
    }}
    .BtnWarning:hover {{
        background: #d97706;
    }}
    QTableWidget {{
        border: 1px solid {AppColors.BORDER};
        border-radius: 10px;
        background: {AppColors.WHITE};
        alternate-background-color: {AppColors.GRAY_LIGHT};
    }}
    QHeaderView::section {{
        background: {AppColors.GRAY_LIGHT};
        padding: 8px 4px;
        font-weight: 600;
        font-size: 10px;
        color: {AppColors.GRAY};
        border: none;
    }}
    QProgressBar {{
        border: none;
        border-radius: 6px;
        background: {AppColors.GRAY_LIGHT};
        height: 6px;
    }}
    QProgressBar::chunk {{
        background: {AppColors.PRIMARY};
        border-radius: 6px;
    }}
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollBar:vertical {{
        border: none;
        background: {AppColors.GRAY_LIGHT};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {AppColors.BORDER};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {AppColors.PRIMARY};
    }}
    QMenu {{
        background: white;
        border: 1px solid {AppColors.BORDER};
        border-radius: 8px;
        padding: 4px;
    }}
    QMenu::item {{
        padding: 6px 20px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background: {AppColors.PRIMARY_LIGHT};
        color: {AppColors.PRIMARY_DARK};
    }}
"""


# ============================================================================
# DIALOGUE DE RÉDUCTION EN MASSE
# ============================================================================

class MassReductionDialog(QDialog):
    """Dialogue pour appliquer une réduction en masse sur les garanties sélectionnées"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Application de réduction en masse")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        self.setStyleSheet(STYLESHEET)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête
        header = QLabel("📊 Application de réduction en masse")
        header.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a;")
        layout.addWidget(header)
        
        desc = QLabel("Appliquez une réduction sur les garanties sélectionnées pour tous les véhicules")
        desc.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(desc)
        
        # Groupe des garanties
        group = QGroupBox("Garanties concernées")
        group_layout = QVBoxLayout(group)
        
        # Liste des garanties avec checkboxes
        self.garantie_checkboxes = {}
        garanties_list = [
            ('rc', "RC/RTI"),
            ('dr', "Défense et Recours"),
            ('vol', "Vol/Vol partie"),
            ('vb', "Vol Braquage"),
            ('incendie', "Incendie"),
            ('bris_glace', "Bris de Glaces"),
            ('ar', "Assistance à la réparation"),
            ('dta', "Dommages Tous Accidents"),
            ('ipt', "IPT + Conducteur"),
        ]
        
        checkbox_layout = QGridLayout()
        for i, (key, label) in enumerate(garanties_list):
            row = i // 3
            col = (i % 3) * 2
            
            cb = QCheckBox(label)
            cb.setChecked(True)  # Par défaut toutes sélectionnées
            self.garantie_checkboxes[key] = cb
            checkbox_layout.addWidget(cb, row, col)
        
        # Bouton Sélectionner/Désélectionner tout
        select_all_btn = QPushButton("Tout sélectionner")
        select_all_btn.setFlat(True)
        select_all_btn.setStyleSheet("color: #2563eb; font-size: 11px;")
        select_all_btn.clicked.connect(lambda: self.toggle_all_checkboxes(True))
        
        deselect_all_btn = QPushButton("Tout désélectionner")
        deselect_all_btn.setFlat(True)
        deselect_all_btn.setStyleSheet("color: #64748b; font-size: 11px;")
        deselect_all_btn.clicked.connect(lambda: self.toggle_all_checkboxes(False))
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(deselect_all_btn)
        btn_layout.addStretch()
        checkbox_layout.addLayout(btn_layout, len(garanties_list) // 3 + 1, 0, 1, 6)
        
        group_layout.addLayout(checkbox_layout)
        layout.addWidget(group)
        
        # Type de réduction
        reduction_group = QGroupBox("Type de réduction")
        reduction_layout = QGridLayout(reduction_group)
        
        reduction_layout.addWidget(QLabel("Pourcentage de réduction (%) :"), 0, 0)
        self.reduction_input = QLineEdit("10")
        self.reduction_input.setPlaceholderText("Ex: 10")
        reduction_layout.addWidget(self.reduction_input, 0, 1)
        
        # Mode d'application
        reduction_layout.addWidget(QLabel("Mode :"), 1, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Réduire les montants (soustraire)",
            "Appliquer un coefficient multiplicateur",
            "Définir un montant fixe maximum"
        ])
        reduction_layout.addWidget(self.mode_combo, 1, 1)
        
        layout.addWidget(reduction_group)
        
        # Actions
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setProperty("class", "BtnSecondary")
        cancel_btn.setFixedSize(120, 35)
        cancel_btn.clicked.connect(self.reject)
        
        apply_btn = QPushButton("✅ Appliquer")
        apply_btn.setProperty("class", "BtnSuccess")
        apply_btn.setFixedSize(120, 35)
        apply_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)
    
    def toggle_all_checkboxes(self, checked):
        """Active ou désactive toutes les checkboxes"""
        for cb in self.garantie_checkboxes.values():
            cb.setChecked(checked)
    
    def get_selected_garanties(self):
        """Retourne la liste des garanties sélectionnées"""
        return [key for key, cb in self.garantie_checkboxes.items() if cb.isChecked()]
    
    def get_reduction_value(self):
        """Retourne la valeur de réduction"""
        try:
            return float(self.reduction_input.text().replace(",", "."))
        except:
            return 0.0
    
    def get_mode(self):
        """Retourne le mode d'application"""
        return self.mode_combo.currentIndex()




def build_vehicle_import_payload(vehicle, owner_id, compagny_id, fleet_id, current_user_id, debut, fin, jours, total_garanties, tva_amount, accessoires, asac, carte_rose, vignette):
    """Construit le payload attendu par le contrôleur pour créer un véhicule complet."""
    garanties = vehicle.get('garanties', {}) or {}

    categorie_value = (vehicle.get('categorie') or 'VP').strip() or 'VP'
    genre_value = (vehicle.get('genre') or 'GV04').strip() or 'GV04'
    type_value = (vehicle.get('type_vehicule') or 'TV10').strip() or 'TV10'
    usage_value = (vehicle.get('usage') or 'UV01').strip() or 'UV01'
    energie_value = (vehicle.get('energie') or 'SEE').strip() or 'SEE'

    guarantee_amounts = {
        'amt_rc': float(garanties.get('rc', 0) or 0),
        'amt_dr': float(garanties.get('dr', 0) or 0),
        'amt_vol': float(garanties.get('vol', 0) or 0),
        'amt_vb': float(garanties.get('vb', 0) or 0),
        'amt_in': float(garanties.get('incendie', garanties.get('in_garantie', 0)) or 0),
        'amt_bris': float(garanties.get('bris_glace', 0) or 0),
        'amt_ar': float(garanties.get('ar', 0) or 0),
        'amt_dta': float(garanties.get('dta', 0) or 0),
        'amt_ipt': float(garanties.get('ipt', 0) or 0),
    }

    guarantee_options = {
        'check_rc': guarantee_amounts['amt_rc'] > 0,
        'check_dr': guarantee_amounts['amt_dr'] > 0,
        'check_vol': guarantee_amounts['amt_vol'] > 0,
        'check_vb': guarantee_amounts['amt_vb'] > 0,
        'check_in': guarantee_amounts['amt_in'] > 0,
        'check_bris': guarantee_amounts['amt_bris'] > 0,
        'check_ar': guarantee_amounts['amt_ar'] > 0,
        'check_dta': guarantee_amounts['amt_dta'] > 0,
        'check_ipt': guarantee_amounts['amt_ipt'] > 0,
    }

    return {
        'immatriculation': vehicle['immatriculation'],
        'chassis': vehicle.get('chassis') or f"CH-{vehicle['immatriculation']}",
        'marque': vehicle.get('marque', ''),
        'modele': vehicle.get('modele', ''),
        'annee': vehicle.get('annee', None),
        'puissance_fiscale': vehicle.get('puissance', 0),
        'places': vehicle.get('places', 5),
        'cylindree': 0,
        'ptac': 0,
        'charge_utile': 0,
        'valeur_neuf': vehicle.get('valeur_neuf', 0),
        'valeur_venale': vehicle.get('valeur_venale', 0),
        'has_remorque': False,
        'remorque_inflammable': False,
        'remorque_immat': '',
        'double_commande': False,
        'engin_portuaire': False,
        'rc_eleves': False,
        'code_tarif': '',
        'libele_tarif': '',
        'code_assure': '',
        'date_debut': debut,
        'date_fin': fin,
        'date_mise_circulation': vehicle.get('date_mise_circulation', None),
        'nbr_jour': jours,
        'prime_brute': total_garanties,
        'reduction': 0,
        'prime_nette': total_garanties,
        'prime_emise': total_garanties,
        'accessoires': accessoires,
        'tva': tva_amount,
        'fichier_asac': asac,
        'carte_rose': carte_rose,
        'vignette': vignette,
        'pttc': total_garanties + accessoires + asac + tva_amount + vignette + carte_rose,
        'statut': 'ACTIF',
        'is_active': True,
        'owner_id': owner_id,
        'company_id': compagny_id,
        'compagny_id': compagny_id,
        'fleet_id': fleet_id,
        'tarif_id': None,
        'created_by': current_user_id,
        'created_ip': '127.0.0.1',
        'last_ip': '127.0.0.1',
        'categorie': categorie_value,
        'genre': genre_value,
        'type_vehicule': type_value,
        'usage': usage_value,
        'energie': energie_value,
        'zone': 'A',
        **guarantee_amounts,
        **guarantee_options,
        'red_rc': 0,
        'red_dr': 0,
        'red_vol': 0,
        'red_vb': 0,
        'red_in': 0,
        'red_bris': 0,
        'red_ar': 0,
        'red_dta': 0,
        'red_ipt': 0,
        'amt_val_red_rc': 0,
        'amt_val_red_dr': 0,
        'amt_val_red_vol': 0,
        'amt_val_red_vb': 0,
        'amt_val_red_in': 0,
        'amt_val_red_bris': 0,
        'amt_val_red_ar': 0,
        'amt_val_red_dta': 0,
        'amt_val_red_ipt': 0,
        'amt_fleet_rc_val': 0,
        'amt_fleet_dr_val': 0,
        'amt_fleet_vol_val': 0,
        'amt_fleet_vb_val': 0,
        'amt_fleet_in_val': 0,
        'amt_fleet_bris_val': 0,
        'amt_fleet_ar_val': 0,
        'amt_fleet_dta_val': 0,
        'amt_fleet_ipt_val': 0,
    }


class VehicleGarantieDialog(QDialog):
    """Dialogue de personnalisation complète d'un véhicule"""
    
    def __init__(self, vehicle, garanties, parent=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.garanties = garanties
        self.garantie_cards = {}
        self.setWindowTitle(f"Gestion du véhicule - {vehicle.get('immatriculation', 'Véhicule')}")
        self.setMinimumSize(900, 750)
        self.setModal(True)
        self.setStyleSheet(STYLESHEET)
        
        self.setup_ui()
        self.load_garanties()
        self.load_vehicle_infos()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête
        header = QFrame()
        header.setStyleSheet(f"""
            background: {AppColors.PRIMARY_LIGHT};
            border-radius: 10px;
            padding: 10px;
        """)
        header_layout = QHBoxLayout(header)
        
        info = QLabel(f"🚗 {self.vehicle.get('immatriculation')} - {self.vehicle.get('marque')} {self.vehicle.get('modele')}")
        info.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {AppColors.PRIMARY_DARK};")
        header_layout.addWidget(info)
        header_layout.addStretch()
        layout.addWidget(header)
        
        # Utiliser un QTabWidget pour organiser les informations
        tab_widget = QTabWidget()
        
        # ========== ONGLET 1 : GARANTIES ==========
        garanties_tab = self.create_garanties_tab()
        tab_widget.addTab(garanties_tab, "🛡️ Garanties")
        
        # ========== ONGLET 2 : INFORMATIONS VÉHICULE ==========
        vehicle_tab = self.create_vehicle_info_tab()
        tab_widget.addTab(vehicle_tab, "🚗 Véhicule")
        
        # ========== ONGLET 3 : FRAIS ET TAXES ==========
        frais_tab = self.create_frais_tab()
        tab_widget.addTab(frais_tab, "💰 Frais & Taxes")
        
        # ========== ONGLET 4 : DATES ET STATUT ==========
        dates_tab = self.create_dates_tab()
        tab_widget.addTab(dates_tab, "📅 Dates")
        
        layout.addWidget(tab_widget)
        
        # Total général
        total_frame = QFrame()
        total_frame.setStyleSheet(f"""
            background: {AppColors.SUCCESS_LIGHT};
            border-radius: 10px;
            padding: 10px;
        """)
        total_layout = QHBoxLayout(total_frame)
        total_layout.addWidget(QLabel("<b>💰 TOTAL GÉNÉRAL DES GARANTIES :</b>"))
        self.total_label = QLabel("0 FCFA")
        self.total_label.setStyleSheet(f"font-size: 16px; font-weight: 800; color: {AppColors.SUCCESS_DARK};")
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()
        layout.addWidget(total_frame)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("Valider")
        ok_btn.setProperty("class", "BtnSuccess")
        ok_btn.setFixedSize(120, 35)
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setProperty("class", "BtnSecondary")
        cancel_btn.setFixedSize(120, 35)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)
    
    def create_garanties_tab(self):
        """Crée l'onglet des garanties"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        scroll_layout = QVBoxLayout(content)
        
        self.garantie_inputs = {}
        garanties_list = [
            ('rc', "RC/RTI"),
            ('dr', "Défense et Recours"),
            ('vol', "Vol/Vol partie"),
            ('vb', "Vol Braquage"),
            ('incendie', "Incendie"),
            ('bris_glace', "Bris de Glaces"),
            ('ar', "Assistance à la réparation"),
            ('dta', "Dommages Tous Accidents"),
            ('ipt', "IPT + Conducteur"),
        ]
        
        for key, label in garanties_list:
            frame = QFrame()
            frame.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 8px;")
            frame_layout = QHBoxLayout(frame)
            
            checkbox = QCheckBox(label)
            checkbox.setStyleSheet("font-weight: 600;")
            checkbox.toggled.connect(lambda checked, k=key: self.on_garantie_toggle(k, checked))
            frame_layout.addWidget(checkbox, 2)
            
            amount_input = QLineEdit()
            amount_input.setPlaceholderText("Montant")
            amount_input.setEnabled(False)
            amount_input.textChanged.connect(lambda: self.update_total())
            frame_layout.addWidget(amount_input)
            
            reduction_input = QLineEdit()
            reduction_input.setPlaceholderText("Réduction %")
            reduction_input.setEnabled(False)
            reduction_input.setFixedWidth(100)
            reduction_input.textChanged.connect(lambda: self.update_total())
            frame_layout.addWidget(reduction_input)
            
            net_label = QLabel("0 FCFA")
            net_label.setStyleSheet(f"color: {AppColors.SUCCESS}; font-weight: bold;")
            net_label.setFixedWidth(120)
            frame_layout.addWidget(net_label)
            
            self.garantie_inputs[key] = {
                'checkbox': checkbox,
                'amount': amount_input,
                'reduction': reduction_input,
                'net': net_label
            }
            
            scroll_layout.addWidget(frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab

    def create_vehicle_info_tab(self):
        """Crée l'onglet des informations du véhicule"""
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Styles
        style_field = """
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                background: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """
        self.info_inputs = {}
        
        # Identifiants
        layout.addWidget(QLabel("Immatriculation :"), 0, 0)
        self.info_immatriculation = QLineEdit(self.vehicle.get('immatriculation', ''))
        self.info_immatriculation.setStyleSheet(style_field)
        layout.addWidget(self.info_immatriculation, 0, 1)
        
        layout.addWidget(QLabel("Châssis :"), 1, 0)
        self.info_chassis = QLineEdit(self.vehicle.get('chassis', ''))
        self.info_chassis.setStyleSheet(style_field)
        layout.addWidget(self.info_chassis, 1, 1)
        
        # Marque et modèle
        layout.addWidget(QLabel("Marque :"), 2, 0)
        self.info_marque = QLineEdit(self.vehicle.get('marque', ''))
        self.info_marque.setStyleSheet(style_field)
        layout.addWidget(self.info_marque, 2, 1)
        
        layout.addWidget(QLabel("Modèle :"), 3, 0)
        self.info_modele = QLineEdit(self.vehicle.get('modele', ''))
        self.info_modele.setStyleSheet(style_field)
        layout.addWidget(self.info_modele, 3, 1)
        
        # Caractéristiques
        layout.addWidget(QLabel("Catégorie :"), 4, 0)
        self.info_categorie = QLineEdit(self.vehicle.get('categorie', 'VP'))
        self.info_categorie.setStyleSheet(style_field)
        layout.addWidget(self.info_categorie, 4, 1)
        
        layout.addWidget(QLabel("Année :"), 5, 0)
        self.info_annee = QLineEdit(str(self.vehicle.get('annee', '')) if self.vehicle.get('annee') else '')
        self.info_annee.setStyleSheet(style_field)
        layout.addWidget(self.info_annee, 5, 1)
        
        layout.addWidget(QLabel("Énergie :"), 6, 0)
        self.info_energie = QLineEdit(self.vehicle.get('energie', 'Essence'))
        self.info_energie.setStyleSheet(style_field)
        layout.addWidget(self.info_energie, 6, 1)
        
        layout.addWidget(QLabel("Puissance (CV) :"), 7, 0)
        self.info_puissance = QLineEdit(str(self.vehicle.get('puissance', 0)))
        self.info_puissance.setStyleSheet(style_field)
        layout.addWidget(self.info_puissance, 7, 1)
        
        layout.addWidget(QLabel("Places :"), 8, 0)
        self.info_places = QLineEdit(str(self.vehicle.get('places', 5)))
        self.info_places.setStyleSheet(style_field)
        layout.addWidget(self.info_places, 8, 1)
        
        # Valeurs financières
        layout.addWidget(QLabel("Valeur à neuf (FCFA) :"), 9, 0)
        self.info_valeur_neuf = QLineEdit(f"{self.vehicle.get('valeur_neuf', 0):,.0f}".replace(",", " "))
        self.info_valeur_neuf.setStyleSheet(style_field)
        layout.addWidget(self.info_valeur_neuf, 9, 1)
        
        layout.addWidget(QLabel("Valeur vénale (FCFA) :"), 10, 0)
        self.info_valeur_venale = QLineEdit(f"{self.vehicle.get('valeur_venale', 0):,.0f}".replace(",", " "))
        self.info_valeur_venale.setStyleSheet(style_field)
        layout.addWidget(self.info_valeur_venale, 10, 1)
        
        layout.addWidget(QLabel("Zone :"), 11, 0)
        self.info_zone = QLineEdit(self.vehicle.get('zone', 'A'))
        self.info_zone.setStyleSheet(style_field)
        layout.addWidget(self.info_zone, 11, 1)
        
        # Remplacer layout.addStretch() par rowStretch
        layout.setRowStretch(12, 1)
        
        return tab

    def create_frais_tab(self):
        """Crée l'onglet des frais et taxes"""
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        style_field = """
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                background: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """
        
        # Frais supplémentaires
        layout.addWidget(QLabel("Accessoires (FCFA) :"), 0, 0)
        self.frais_accessoires = QLineEdit(str(self.vehicle.get('accessoires', 0)))
        self.frais_accessoires.setStyleSheet(style_field)
        self.frais_accessoires.textChanged.connect(self.calculate_tva_pttc)
        layout.addWidget(self.frais_accessoires, 0, 1)
        
        layout.addWidget(QLabel("Fichier ASAC (FCFA) :"), 1, 0)
        self.frais_asac = QLineEdit(str(self.vehicle.get('asac', 0)))
        self.frais_asac.setStyleSheet(style_field)
        self.frais_asac.textChanged.connect(self.calculate_tva_pttc)
        layout.addWidget(self.frais_asac, 1, 1)
        
        layout.addWidget(QLabel("Carte Rose (FCFA) :"), 2, 0)
        self.frais_carte_rose = QLineEdit(str(self.vehicle.get('carte_rose', 0)))
        self.frais_carte_rose.setStyleSheet(style_field)
        self.frais_carte_rose.textChanged.connect(self.calculate_pttc)
        layout.addWidget(self.frais_carte_rose, 2, 1)
        
        layout.addWidget(QLabel("Vignette (FCFA) :"), 3, 0)
        self.frais_vignette = QLineEdit(str(self.vehicle.get('vignette', 0)))
        self.frais_vignette.setStyleSheet(style_field)
        self.frais_vignette.textChanged.connect(self.calculate_pttc)
        layout.addWidget(self.frais_vignette, 3, 1)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; margin: 10px 0;")
        layout.addWidget(sep, 4, 0, 1, 2)
        
        # Résultats des calculs
        layout.addWidget(QLabel("TVA (19.25%) :"), 5, 0)
        self.frais_tva = QLineEdit("0")
        self.frais_tva.setReadOnly(True)
        self.frais_tva.setStyleSheet("background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 8px 12px;")
        layout.addWidget(self.frais_tva, 5, 1)
        
        layout.addWidget(QLabel("PTTC (Total) :"), 6, 0)
        self.frais_pttc = QLineEdit("0")
        self.frais_pttc.setReadOnly(True)
        self.frais_pttc.setStyleSheet("background-color: #d1fae5; border: 1px solid #bbf7d0; border-radius: 8px; padding: 8px 12px; font-weight: bold;")
        layout.addWidget(self.frais_pttc, 6, 1)
        
        # Remplacer layout.addStretch() par rowStretch
        layout.setRowStretch(7, 1)
        
        return tab

    def create_dates_tab(self):
        """Crée l'onglet des dates et statut"""
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        style_field = """
            QDateEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                background: white;
                font-size: 13px;
            }
        """
        
        # Date début
        layout.addWidget(QLabel("Date de début :"), 0, 0)
        self.dates_date_debut = QDateEdit()
        self.dates_date_debut.setCalendarPopup(True)
        self.dates_date_debut.setDisplayFormat("dd/MM/yyyy")
        self.dates_date_debut.dateChanged.connect(self.update_dates_calculations)
        layout.addWidget(self.dates_date_debut, 0, 1)
        
        # Date fin
        layout.addWidget(QLabel("Date de fin :"), 1, 0)
        self.dates_date_fin = QDateEdit()
        self.dates_date_fin.setCalendarPopup(True)
        self.dates_date_fin.setDisplayFormat("dd/MM/yyyy")
        self.dates_date_fin.dateChanged.connect(self.update_dates_calculations)
        layout.addWidget(self.dates_date_fin, 1, 1)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; margin: 10px 0;")
        layout.addWidget(sep, 2, 0, 1, 2)
        
        # Durée
        layout.addWidget(QLabel("Durée (jours) :"), 3, 0)
        self.dates_duree = QLabel("365")
        self.dates_duree.setStyleSheet("font-weight: bold; color: #2563eb; font-size: 14px;")
        layout.addWidget(self.dates_duree, 3, 1)
        
        # Prorata
        layout.addWidget(QLabel("Prorata :"), 4, 0)
        self.dates_prorata = QLabel("100%")
        self.dates_prorata.setStyleSheet("font-weight: bold; color: #10b981;")
        layout.addWidget(self.dates_prorata, 4, 1)
        
        # Statut
        layout.addWidget(QLabel("Statut :"), 5, 0)
        self.dates_statut = QLabel("En Circulation")
        self.dates_statut.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.dates_statut, 5, 1)
        
        # Remplacer layout.addStretch() par rowStretch
        layout.setRowStretch(6, 1)
        
        # Charger les dates
        self.load_dates()
        
        return tab

    def load_dates(self):
        """Charge les dates du véhicule"""
        date_debut = self.vehicle.get('date_debut')
        date_fin = self.vehicle.get('date_fin')
        
        if date_debut:
            if isinstance(date_debut, datetime):
                self.dates_date_debut.setDate(QDate(date_debut.year, date_debut.month, date_debut.day))
            elif isinstance(date_debut, QDate):
                self.dates_date_debut.setDate(date_debut)
        else:
            self.dates_date_debut.setDate(QDate.currentDate())
        
        if date_fin:
            if isinstance(date_fin, datetime):
                self.dates_date_fin.setDate(QDate(date_fin.year, date_fin.month, date_fin.day))
            elif isinstance(date_fin, QDate):
                self.dates_date_fin.setDate(date_fin)
        else:
            self.dates_date_fin.setDate(QDate.currentDate().addYears(1))
        
        self.update_dates_calculations()
    
    def update_dates_calculations(self):
        """Met à jour les calculs des dates"""
        debut = self.dates_date_debut.date()
        fin = self.dates_date_fin.date()
        
        if fin >= debut:
            jours = debut.daysTo(fin)
            prorata = (jours / 365.0) * 100
            
            self.dates_duree.setText(f"{jours} jours")
            self.dates_prorata.setText(f"{prorata:.1f}%")
            
            today = QDate.currentDate()
            if fin < today:
                self.dates_statut.setText("Expiré")
                self.dates_statut.setStyleSheet("color: #ef4444; font-weight: bold;")
            elif debut > today:
                self.dates_statut.setText("À venir")
                self.dates_statut.setStyleSheet("color: #f59e0b; font-weight: bold;")
            else:
                self.dates_statut.setText("En Circulation")
                self.dates_statut.setStyleSheet("color: #10b981; font-weight: bold;")
        else:
            self.dates_duree.setText("Invalide")
            self.dates_prorata.setText("0%")
            self.dates_statut.setText("Invalide")
            self.dates_statut.setStyleSheet("color: #ef4444; font-weight: bold;")
    
    def load_vehicle_infos(self):
        """Charge les informations du véhicule"""
        # Les valeurs sont déjà chargées dans les widgets via les text()
        pass

    def load_garanties(self):
        """Charge les garanties dans les cartes"""
        for key, card in self.garantie_cards.items():
            # Récupérer le montant de la garantie
            amount = self.garanties.get(key, 0)
            
            # ✅ Vérifier si le montant est valide (non None et > 0)
            if amount is None:
                amount = 0
            
            # ✅ Charger la réduction si elle existe
            reduction_key = f'reduction_{key}'
            reduction = self.garanties.get(reduction_key, 0)
            if reduction is None:
                reduction = 0
            
            # ✅ Définir les valeurs dans la carte
            card.set_values(float(amount), float(reduction))
            card.garantie_changed.connect(self.on_garantie_changed)

    def on_garantie_changed(self, key, checked, net_amount):
        self.update_total()
        self.calculate_tva_pttc()
    
    def update_total(self):
        total = sum(card.get_net_amount() for card in self.garantie_cards.values())
        self.total_label.setText(f"{total:,.0f} FCFA".replace(",", " "))
        self.calculate_tva_pttc()
    
    def calculate_tva_pttc(self):
        """Calcule la TVA et le PTTC"""
        try:
            total_garanties = sum(card.get_net_amount() for card in self.garantie_cards.values())
            accessoires = self.get_float_value(self.frais_accessoires)
            asac = self.get_float_value(self.frais_asac)
            
            base_tva = total_garanties + accessoires + asac
            tva = base_tva * 0.1925
            
            self.frais_tva.setText(f"{tva:,.0f}".replace(",", " "))
            self.calculate_pttc()
        except:
            pass
    
    def calculate_pttc(self):
        """Calcule le PTTC"""
        try:
            total_garanties = sum(card.get_net_amount() for card in self.garantie_cards.values())
            accessoires = self.get_float_value(self.frais_accessoires)
            asac = self.get_float_value(self.frais_asac)
            tva = self.get_float_value(self.frais_tva)
            vignette = self.get_float_value(self.frais_vignette)
            carte_rose = self.get_float_value(self.frais_carte_rose)
            
            pttc = total_garanties + accessoires + asac + tva + vignette + carte_rose
            self.frais_pttc.setText(f"{pttc:,.0f}".replace(",", " "))
        except:
            pass
    
    def get_float_value(self, widget):
        """Récupère une valeur float d'un widget"""
        try:
            if not widget or not widget.text():
                return 0.0
            txt = widget.text().strip().replace(" ", "").replace(",", ".")
            return float(txt) if txt else 0.0
        except:
            return 0.0
    
    def get_data(self):
        """Retourne les données modifiées"""
        data = {}
        
        # Garanties
        for key, inputs in self.garantie_inputs.items():
            if inputs['checkbox'].isChecked():
                try:
                    amount_text = inputs['amount'].text().replace(" ", "").replace(",", "")
                    amount = float(amount_text) if amount_text else 0
                    data[key] = amount
                    
                    reduction_text = inputs['reduction'].text().replace("%", "").strip()
                    reduction = float(reduction_text) if reduction_text else 0
                    data[f'reduction_{key}'] = reduction
                except:
                    data[key] = 0
                    data[f'reduction_{key}'] = 0
            else:
                data[key] = 0
                data[f'reduction_{key}'] = 0
        
        # ✅ Utiliser self.info_inputs pour récupérer les valeurs
        for key, input_widget in self.info_inputs.items():
            value = input_widget.text().strip()
            if key in ['annee', 'puissance', 'places']:
                try:
                    data[key] = int(value) if value else 0
                except:
                    data[key] = 0
            elif key in ['valeur_neuf', 'valeur_venale']:
                try:
                    data[key] = float(value.replace(" ", "").replace(",", "")) if value else 0
                except:
                    data[key] = 0
            else:
                data[key] = value
        
        # ✅ Ajouter les frais
        data['accessoires'] = self.get_float_value(self.frais_accessoires)
        data['asac'] = self.get_float_value(self.frais_asac)
        data['carte_rose'] = self.get_float_value(self.frais_carte_rose)
        data['vignette'] = self.get_float_value(self.frais_vignette)
        data['tva'] = self.get_float_value(self.frais_tva)
        data['pttc'] = self.get_float_value(self.frais_pttc)
        
        return data

    def get_garanties(self):
        result = {}
        for key, card in self.garantie_cards.items():
            result[key] = card.get_net_amount()
            result[f'brut_{key}'] = card.current_amount
            result[f'reduction_{key}'] = card.current_reduction
        result['total'] = sum(v for k, v in result.items() if not k.startswith(('brut_', 'reduction_', 'total')))
        
        # Ajouter les valeurs des frais
        result['accessoires'] = self.get_float_value(self.frais_accessoires)
        result['asac'] = self.get_float_value(self.frais_asac)
        result['carte_rose'] = self.get_float_value(self.frais_carte_rose)
        result['vignette'] = self.get_float_value(self.frais_vignette)
        result['tva'] = self.get_float_value(self.frais_tva)
        result['pttc'] = self.get_float_value(self.frais_pttc)
        
        # Ajouter les informations du véhicule
        result['immatriculation'] = self.info_immatriculation.text().strip().upper()
        result['chassis'] = self.info_chassis.text().strip()
        result['marque'] = self.info_marque.text().strip()
        result['modele'] = self.info_modele.text().strip()
        result['categorie'] = self.info_categorie.text().strip().upper()
        result['annee'] = self.get_float_value(self.info_annee)
        result['energie'] = self.info_energie.text().strip()
        result['puissance'] = self.get_float_value(self.info_puissance)
        result['places'] = int(self.get_float_value(self.info_places)) if self.get_float_value(self.info_places) else 5
        result['valeur_neuf'] = self.get_float_value(self.info_valeur_neuf)
        result['valeur_venale'] = self.get_float_value(self.info_valeur_venale)
        result['zone'] = self.info_zone.text().strip().upper()
        
        # Ajouter les dates
        result['date_debut'] = self.dates_date_debut.date().toPython()
        result['date_fin'] = self.dates_date_fin.date().toPython()
        result['nbr_jour'] = self.dates_date_debut.date().daysTo(self.dates_date_fin.date())
        result['statut'] = self.dates_statut.text()
        result['prorata'] = result['nbr_jour'] / 365.0 if result['nbr_jour'] > 0 else 0
        
        return result

# ============================================================================
# THREAD DE CALCUL
# ============================================================================

class CalculationThread(QThread):
    progress = Signal(int, int, str, dict)
    finished_signal = Signal(list)
    
    def __init__(self, controller, vehicles, params):
        super().__init__()
        self.controller = controller
        self.vehicles = vehicles
        self.params = params
        self._is_cancelled = False
    
    def cancel(self):
        self._is_cancelled = True
    
    def run(self):
        results = []
        total = len(self.vehicles)
        
        for i, vehicle in enumerate(self.vehicles):
            if self._is_cancelled:
                break
            
            try:
                garanties = self.calculate_garanties(vehicle)
                vehicle['garanties'] = garanties
                vehicle['status'] = 'success'
                results.append(vehicle)
                
                self.progress.emit(i + 1, total, vehicle['immatriculation'], garanties)
                
            except Exception as e:
                vehicle['status'] = 'error'
                vehicle['error'] = str(e)
                results.append(vehicle)
                self.progress.emit(i + 1, total, vehicle['immatriculation'], {})
        
        self.finished_signal.emit(results)

    def calculate_garanties(self, vehicle):
        """
        Calcule les garanties pour un véhicule
        Reprend la logique de calculate_garantie_amount de automobile_form_view.py
        """
        garanties = {}
        
        # Récupérer les paramètres
        cie_id = self.params.get('compagny_id')
        zone = self.params.get('zone', 'A')
        code_tarif = self.params.get('code_tarif', '')
        avec_remorque = self.params.get('avec_remorque', False)
        
        # Valeurs du véhicule
        v_neuf = vehicle.get('valeur_neuf', 0)
        v_venale = vehicle.get('valeur_venale', 0)
        places = vehicle.get('places', 5)
        puissance = vehicle.get('puissance', 0)
        energie = vehicle.get('energie', 'Essence')
        categorie = vehicle.get('categorie', 'VP')
        
        # Calcul du prorata
        jours = self.params.get('duree_jours', 365)
        prorata = jours / 365.0
        
        # ✅ 1. CALCUL DE LA RC (Responsabilité Civile)
        # Appel à la méthode du contrôleur pour obtenir la prime RC
        try:
            res = self.controller.vehicles.get_rc_premium_from_matrix(
                cie_id=cie_id,
                zone_saisie=zone,
                categorie=categorie,
                energie=energie,
                cv_saisi=puissance,
                avec_remorque=avec_remorque,
                code_tarif=code_tarif if code_tarif else None
            )
            rc_base = res.get('rc', 0) if isinstance(res, dict) else (res or 0)
        except Exception as e:
            print(f"Erreur calcul RC: {e}")
            rc_base = 0
        
        # ✅ 2. CALCUL DES GARANTIES (comme dans automobile_form_view.py)
        # RC
        garanties['rc'] = rc_base * prorata
        
        # DR (Défense et Recours) - 3% de la RC
        garanties['dr'] = (rc_base * prorata) * 0.03 * prorata
        
        # VOL - 2% de la valeur vénale
        garanties['vol'] = v_venale * 0.02 * prorata
        
        # VB (Vol à main armée) - 2% de la valeur vénale
        garanties['vb'] = v_venale * 0.02 * prorata
        
        # INCENDIE - 2.5% de la valeur vénale
        garanties['incendie'] = v_venale * 0.025 * prorata
        
        # BRIS DE GLACE - 0.5% de la valeur à neuf
        garanties['bris_glace'] = v_neuf * 0.005 * prorata
        
        # AR (Assistance Réparation) - 3% de 75% de la valeur vénale
        garanties['ar'] = v_venale * 0.75 * 0.03 * prorata
        
        # DTA (Dommages Tous Accidents) - 5% de la valeur à neuf
        garanties['dta'] = v_neuf * 0.05 * prorata
        
        # IPT (Individuelle Personnes Transportées)
        # Si places <= 5: 7500 FCFA, sinon: (7500 * places / 5)
        if places <= 5:
            garanties['ipt'] = 7500 * prorata
        else:
            garanties['ipt'] = (7500 * places / 5) * prorata
        
        # ✅ 3. TOTAL
        garanties['total'] = sum([
            garanties.get('rc', 0),
            garanties.get('dr', 0),
            garanties.get('vol', 0),
            garanties.get('vb', 0),
            garanties.get('incendie', 0),
            garanties.get('bris_glace', 0),
            garanties.get('ar', 0),
            garanties.get('dta', 0),
            garanties.get('ipt', 0)
        ])
        
        return garanties
# ============================================================================
# DIALOGUE PRINCIPAL
# ============================================================================

class VehicleActionsWidget(QWidget):
    """Widget contenant les deux boutons d'action pour un véhicule"""
    
    def __init__(self, vehicle_id, on_garanties_clicked, on_dates_clicked, on_modified_clicked, parent=None):
        super().__init__(parent)
        self.vehicle_id = vehicle_id
        self.on_garanties_clicked = on_garanties_clicked
        self.on_dates_clicked = on_dates_clicked
        self.on_modified_clicked = on_modified_clicked
        
        self.setFixedHeight(40)
        self.setMinimumWidth(110)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)
        
        # Bouton Garanties
        self.garanties_btn = QPushButton("🎯")
        self.garanties_btn.setToolTip("Modifier les garanties")
        self.garanties_btn.setFixedSize(38, 34)
        self.garanties_btn.setCursor(Qt.PointingHandCursor)
        self.garanties_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.garanties_btn.clicked.connect(lambda: self.on_garanties_clicked(self.vehicle_id))
        
        # Bouton Dates
        self.dates_btn = QPushButton("📅")
        self.dates_btn.setToolTip("Modifier les dates du contrat")
        self.dates_btn.setFixedSize(38, 34)
        self.dates_btn.setCursor(Qt.PointingHandCursor)
        self.dates_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.dates_btn.clicked.connect(lambda: self.on_dates_clicked(self.vehicle_id))

        # Bouton Dates
        self.update_btn = QPushButton("✏️")
        self.update_btn.setToolTip("Modifier les données du véhicule")
        self.update_btn.setFixedSize(38, 34)
        self.update_btn.setCursor(Qt.PointingHandCursor)
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.update_btn.clicked.connect(lambda: self.on_modified_clicked(self.vehicle_id))
        
        layout.addWidget(self.garanties_btn)
        layout.addWidget(self.dates_btn)
        layout.addWidget(self.update_btn)
        layout.setAlignment(Qt.AlignCenter)


# ============================================================================
# VEHICLE DATES DIALOG
# ============================================================================

class VehicleDatesDialog(QDialog):
    """Dialogue pour modifier les dates d'un véhicule"""
    
    def __init__(self, vehicle, parent=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.setWindowTitle(f"Dates du contrat - {vehicle.get('immatriculation', 'Véhicule')}")
        self.setMinimumSize(450, 350)
        self.setModal(True)
        self.setStyleSheet(STYLESHEET)
        
        self.setup_ui()
        self.load_dates()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # En-tête
        header = QFrame()
        header.setStyleSheet(f"""
            background: {AppColors.PRIMARY_LIGHT};
            border-radius: 10px;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 12, 15, 12)
        
        info = QLabel(f"📅 {self.vehicle.get('immatriculation')} - {self.vehicle.get('marque')} {self.vehicle.get('modele')}")
        info.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {AppColors.PRIMARY_DARK};")
        header_layout.addWidget(info)
        layout.addWidget(header)
        
        # Formulaire
        form_group = QGroupBox("Paramètres du contrat")
        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(15, 20, 15, 15)
        
        # Date début
        form_layout.addWidget(QLabel("📅 Date de début :"), 0, 0)
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDisplayFormat("dd/MM/yyyy")
        self.date_debut.dateChanged.connect(self.update_calculations)
        form_layout.addWidget(self.date_debut, 0, 1)
        
        # Date fin
        form_layout.addWidget(QLabel("📅 Date de fin :"), 1, 0)
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_fin.dateChanged.connect(self.update_calculations)
        form_layout.addWidget(self.date_fin, 1, 1)
        
        # Séparateur
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(f"background-color: {AppColors.BORDER};")
        form_layout.addWidget(line, 2, 0, 1, 2)
        
        # Durée calculée
        form_layout.addWidget(QLabel("⏱️ Durée :"), 3, 0)
        self.duree_label = QLabel("365 jours")
        self.duree_label.setStyleSheet(f"font-weight: bold; color: {AppColors.PRIMARY}; font-size: 14px;")
        form_layout.addWidget(self.duree_label, 3, 1)
        
        # Statut
        form_layout.addWidget(QLabel("📌 Statut :"), 4, 0)
        self.statut_label = QLabel("En Circulation")
        self.statut_label.setStyleSheet(f"font-weight: bold;")
        form_layout.addWidget(self.statut_label, 4, 1)
        
        # Prorata
        form_layout.addWidget(QLabel("💰 Prorata :"), 5, 0)
        self.prorata_label = QLabel("100%")
        self.prorata_label.setStyleSheet(f"color: {AppColors.SUCCESS}; font-weight: bold;")
        form_layout.addWidget(self.prorata_label, 5, 1)
        
        layout.addWidget(form_group)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setProperty("class", "BtnSecondary")
        cancel_btn.setFixedSize(120, 35)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("💾 Sauvegarder")
        save_btn.setProperty("class", "BtnSuccess")
        save_btn.setFixedSize(120, 35)
        save_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
    
    def load_dates(self):
        """Charge les dates existantes du véhicule"""
        date_debut = self.vehicle.get('date_debut')
        if date_debut:
            if isinstance(date_debut, QDate):
                self.date_debut.setDate(date_debut)
            elif isinstance(date_debut, datetime):
                self.date_debut.setDate(QDate(date_debut.year, date_debut.month, date_debut.day))
            elif isinstance(date_debut, str):
                try:
                    d = datetime.strptime(date_debut, "%Y-%m-%d")
                    self.date_debut.setDate(QDate(d.year, d.month, d.day))
                except:
                    self.date_debut.setDate(QDate.currentDate())
        else:
            self.date_debut.setDate(QDate.currentDate())
        
        date_fin = self.vehicle.get('date_fin')
        if date_fin:
            if isinstance(date_fin, QDate):
                self.date_fin.setDate(date_fin)
            elif isinstance(date_fin, datetime):
                self.date_fin.setDate(QDate(date_fin.year, date_fin.month, date_fin.day))
            elif isinstance(date_fin, str):
                try:
                    d = datetime.strptime(date_fin, "%Y-%m-%d")
                    self.date_fin.setDate(QDate(d.year, d.month, d.day))
                except:
                    self.date_fin.setDate(QDate.currentDate().addYears(1))
        else:
            self.date_fin.setDate(QDate.currentDate().addYears(1))
        
        self.update_calculations()
    
    def update_calculations(self):
        """Calcule et affiche la durée, le statut et le prorata"""
        debut = self.date_debut.date()
        fin = self.date_fin.date()
        
        if fin >= debut:
            jours = debut.daysTo(fin)
            self.duree_label.setText(f"{jours} jours ({jours/30:.1f} mois)")
            
            prorata = (jours / 365.0) * 100
            self.prorata_label.setText(f"{prorata:.1f}% de la prime annuelle")
            
            today = QDate.currentDate()
            if fin < today:
                self.statut_label.setText("⏰ Expiré")
                self.statut_label.setStyleSheet(f"color: {AppColors.DANGER}; font-weight: bold;")
            elif debut > today:
                self.statut_label.setText("⏳ À venir")
                self.statut_label.setStyleSheet(f"color: {AppColors.WARNING}; font-weight: bold;")
            else:
                self.statut_label.setText("✅ En Circulation")
                self.statut_label.setStyleSheet(f"color: {AppColors.SUCCESS}; font-weight: bold;")
        else:
            self.duree_label.setText("Date de fin invalide")
            self.prorata_label.setText("0%")
            self.statut_label.setText("❌ Invalide")
            self.statut_label.setStyleSheet(f"color: {AppColors.DANGER}; font-weight: bold;")
    
    def get_dates(self):
        """Retourne les dates sélectionnées"""
        debut = self.date_debut.date().toPython()
        fin = self.date_fin.date().toPython()
        jours = self.date_debut.date().daysTo(self.date_fin.date())
        prorata = jours / 365.0 if jours > 0 else 0
        
        today = datetime.now().date()
        if fin < today:
            statut = "Expiré"
        elif debut > today:
            statut = "À venir"
        else:
            statut = "En Circulation"
        
        return {
            'date_debut': debut,
            'date_fin': fin,
            'nbr_jour': jours,
            'prorata': prorata,
            'statut': statut
        }

# ============================================================================
# DIALOGUE PRINCIPAL
# ============================================================================

class FleetImportAdvancedDialog(QDialog):
    """Dialogue d'importation de flotte avec nouvelles fonctionnalités"""
    
    # Signal pour le rafraîchissement des données
    data_changed = Signal()
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Importation de flotte")
        self.setMinimumSize(1600, 1000)
        self.resize(1700, 1050)
        
        self.vehicles_data = []
        self.file_path = None
        self.calculation_thread = None
        
        self.setup_ui()
        self.setStyleSheet(STYLESHEET)
        
        self._load_compagnies()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # En-tête
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(1)
        
        # Panneau gauche - Configuration
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Panneau droit - Résultats
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        main_splitter.setSizes([350, 1250])
        main_layout.addWidget(main_splitter, 1)
        
        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)
    
    def create_header(self):
        """Crée l'en-tête"""
        header = QWidget()
        header.setStyleSheet(f"""
            background: {AppColors.WHITE};
            border-radius: 12px;
            padding: 15px;
        """)
        
        layout = QHBoxLayout(header)
        
        title = QLabel("🚚 Importation de flotte")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #0f172a;")
        
        subtitle = QLabel("Importez vos véhicules en masse avec calcul automatique des garanties")
        subtitle.setStyleSheet(f"color: {AppColors.GRAY}; font-size: 12px;")
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        
        return header
    
    def create_left_panel(self):
        """Crée le panneau de configuration (scrollable)"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(16)
        
        # 1. Fichier
        layout.addWidget(self.create_file_section())
        
        # 2. Flotte
        layout.addWidget(self.create_fleet_section())
        
        # 3. Paramètres d'assurance (simplifié)
        layout.addWidget(self.create_insurance_section())
        
        # Bouton Appliquer les frais
        apply_frais_btn = QPushButton("💰 Appliquer les frais aux véhicules sélectionnés")
        apply_frais_btn.setProperty("class", "BtnPrimary")
        apply_frais_btn.clicked.connect(self.apply_global_frais_to_selected)
        layout.addWidget(apply_frais_btn)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        return scroll
    
    def create_file_section(self):
        """Section de sélection du fichier"""
        group = QGroupBox("📄 1. Fichier d'importation")
        layout = QVBoxLayout(group)
        
        # Zone de dépôt
        drop_zone = QFrame()
        drop_zone.setStyleSheet(f"""
            QFrame {{
                background: {AppColors.GRAY_LIGHT};
                border: 2px dashed {AppColors.BORDER};
                border-radius: 10px;
            }}
        """)
        drop_zone.setFixedHeight(80)
        drop_zone.mousePressEvent = lambda e: self.select_file()
        
        drop_layout = QVBoxLayout(drop_zone)
        drop_layout.setAlignment(Qt.AlignCenter)
        
        self.file_icon = QLabel("📂")
        self.file_icon.setStyleSheet("font-size: 20px;")
        self.file_label = QLabel("Cliquez pour sélectionner un fichier Excel ou CSV")
        self.file_label.setStyleSheet(f"color: {AppColors.GRAY}; font-size: 11px;")
        self.file_info = QLabel("")
        self.file_info.setStyleSheet(f"color: {AppColors.PRIMARY}; font-size: 10px;")
        
        drop_layout.addWidget(self.file_icon)
        drop_layout.addWidget(self.file_label)
        drop_layout.addWidget(self.file_info)
        
        layout.addWidget(drop_zone)
        
        # Lien template
        template_btn = QPushButton("📥 Télécharger le modèle Excel")
        template_btn.setFlat(True)
        template_btn.setCursor(Qt.PointingHandCursor)
        template_btn.setStyleSheet(f"color: {AppColors.PRIMARY}; text-align: left; font-size: 11px;")
        template_btn.clicked.connect(self.download_template)
        layout.addWidget(template_btn)
        
        return group
    
    def create_fleet_section(self):
        """Section de configuration de la flotte"""
        group = QGroupBox("🏢 2. Configuration de la flotte")
        layout = QVBoxLayout(group)
        
        # Mode
        mode_layout = QHBoxLayout()
        self.mode_new = QRadioButton("✨ Créer une nouvelle flotte")
        self.mode_existing = QRadioButton("📦 Ajouter à une flotte existante")
        self.mode_new.setChecked(True)
        self.mode_new.toggled.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.mode_new)
        mode_layout.addWidget(self.mode_existing)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # Nouvelle flotte
        self.new_fleet_widget = QWidget()
        new_layout = QGridLayout(self.new_fleet_widget)
        new_layout.setSpacing(8)
        
        new_layout.addWidget(QLabel("Nom :"), 0, 0)
        self.fleet_name = QLineEdit()
        self.fleet_name.setPlaceholderText("Ex: Flotte Logistique 2024")
        new_layout.addWidget(self.fleet_name, 0, 1)
        
        new_layout.addWidget(QLabel("Code :"), 1, 0)
        self.fleet_code = QLineEdit()
        self.fleet_code.setPlaceholderText("Ex: FL-2024-001")
        new_layout.addWidget(self.fleet_code, 1, 1)
        
        layout.addWidget(self.new_fleet_widget)
        
        # Flotte existante
        self.existing_fleet_widget = QWidget()
        self.existing_fleet_widget.setVisible(False)
        existing_layout = QHBoxLayout(self.existing_fleet_widget)
        existing_layout.addWidget(QLabel("Sélectionner :"))
        self.existing_fleet_combo = QComboBox()
        existing_layout.addWidget(self.existing_fleet_combo, 1)
        layout.addWidget(self.existing_fleet_widget)
        
        return group
    
    def create_insurance_section(self):
        """Section des paramètres d'assurance (simplifiée)"""
        group = QGroupBox("📋 3. Paramètres du contrat")
        layout = QGridLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Date début
        layout.addWidget(QLabel("📅 Date début :"), 0, 0)
        self.date_debut = QDateEdit()
        self.date_debut.setDate(QDate.currentDate())
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDisplayFormat("dd/MM/yyyy")
        layout.addWidget(self.date_debut, 0, 1)
        
        # Date fin
        layout.addWidget(QLabel("📅 Date fin :"), 1, 0)
        self.date_fin = QDateEdit()
        self.date_fin.setDate(QDate.currentDate().addYears(1))
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        layout.addWidget(self.date_fin, 1, 1)
        
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; margin: 8px 0;")
        layout.addWidget(sep, 2, 0, 1, 2)
        
        # Titre des frais
        frais_title = QLabel("💰 FRAIS SUPPLÉMENTAIRES (par véhicule)")
        frais_title.setStyleSheet("font-weight: 700; color: #475569; font-size: 12px;")
        layout.addWidget(frais_title, 3, 0, 1, 2)
        
        # Accessoires
        layout.addWidget(QLabel("Accessoires (FCFA) :"), 4, 0)
        self.global_accessoires = QLineEdit("0")
        self.global_accessoires.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 10px;")
        layout.addWidget(self.global_accessoires, 4, 1)
        
        # Fichier ASAC
        layout.addWidget(QLabel("Fichier ASAC (FCFA) :"), 5, 0)
        self.global_asac = QLineEdit("0")
        self.global_asac.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 10px;")
        layout.addWidget(self.global_asac, 5, 1)
        
        # Carte Rose
        layout.addWidget(QLabel("Carte Rose (FCFA) :"), 6, 0)
        self.global_carte_rose = QLineEdit("0")
        self.global_carte_rose.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 10px;")
        layout.addWidget(self.global_carte_rose, 6, 1)
        
        # Vignette
        layout.addWidget(QLabel("Vignette (FCFA) :"), 7, 0)
        self.global_vignette = QLineEdit("0")
        self.global_vignette.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 10px;")
        layout.addWidget(self.global_vignette, 7, 1)
        
        return group
    
    def create_right_panel(self):
        """Crée le panneau des résultats"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(16)
        
        # Statut
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet(f"""
            QFrame {{
                background: {AppColors.PRIMARY_LIGHT};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        status_layout = QHBoxLayout(self.status_frame)
        self.status_icon = QLabel("⏳")
        self.status_icon.setStyleSheet("font-size: 18px;")
        self.status_text = QLabel("Sélectionnez un fichier pour commencer")
        self.status_text.setStyleSheet(f"color: {AppColors.PRIMARY_DARK}; font-weight: 500; font-size: 13px;")
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        
        self.calc_btn = QPushButton("🔢 Calculer les garanties")
        self.calc_btn.setProperty("class", "BtnPrimary")
        self.calc_btn.setEnabled(False)
        self.calc_btn.clicked.connect(self.start_calculation)
        status_layout.addWidget(self.calc_btn)

        self.refresh_btn = QPushButton("🔄 Rafraîchir")
        self.refresh_btn.setProperty("class", "BtnSecondary")
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.clicked.connect(self.refresh_fleet_guarantees)
        status_layout.addWidget(self.refresh_btn)
        
        # Bouton de réduction en masse
        self.mass_reduction_btn = QPushButton("📉 Réduction en masse")
        self.mass_reduction_btn.setProperty("class", "BtnWarning")
        self.mass_reduction_btn.setEnabled(False)
        self.mass_reduction_btn.clicked.connect(self.apply_mass_reduction)
        status_layout.addWidget(self.mass_reduction_btn)
        
        layout.addWidget(self.status_frame)
        
        # Progression
        self.progress_widget = QWidget()
        self.progress_widget.setVisible(False)
        progress_layout = QVBoxLayout(self.progress_widget)
        progress_layout.setSpacing(6)
        
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet(f"color: {AppColors.GRAY}; font-size: 11px;")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_widget)
        
        # Tableau des véhicules avec nouvelles colonnes
        self.setup_vehicle_table()
        layout.addWidget(self.vehicles_table, 1)
        
        # Récapitulatif
        recap_group = self.create_recap_section()
        layout.addWidget(recap_group)
        
        scroll.setWidget(content)
        return scroll
    
    def setup_vehicle_table(self):
        """Configure le tableau avec les nouvelles colonnes"""
        # Nouvelles entêtes
        headers = [
            "✓",  # 0
            "Rang",  # 1
            "Immatriculation",  # 2
            "Marque et Type",  # 3
            "Genre",  # 4
            "Puissance en CV",  # 5
            "Usage",  # 6
            "Nombre de Places",  # 7
            "Nombre de jours assurés",  # 8
            "PMEC",  # 9
            "Valeur Neuve",  # 10
            "Valeur Venale",  # 11
            "Capital Assistance à la réparation",  # 12
            "RC/RTI",  # 13
            "Défense et Recours",  # 14
            "Vol/Vol partie",  # 15
            "Vol Braquage",  # 16
            "Incendie",  # 17
            "Bris de Glaces",  # 18
            "Assistance à la réparation",  # 19
            "Dommages Tous Accidents",  # 20
            "IPT + Conducteur",  # 21
            "Prime brute",  # 22
            "Réductions",  # 23
            "Prime nette",  # 24
            "Droit de Timbre Automobile",  # 25
            "Actions"  # 26
        ]
        
        self.vehicles_table = QTableWidget()
        self.vehicles_table.setColumnCount(len(headers))
        self.vehicles_table.setHorizontalHeaderLabels(headers)
        
        # Configuration des colonnes
        column_widths = {
            0: 30,   # ✓
            1: 40,   # Rang
            2: 100,  # Immatriculation
            3: 120,  # Marque et Type
            4: 70,   # Genre
            5: 80,   # Puissance en CV
            6: 80,   # Usage
            7: 60,   # Nombre de Places
            8: 80,   # Nombre de jours assurés
            9: 70,   # PMEC
            10: 90,  # Valeur Neuve
            11: 90,  # Valeur Venale
            12: 90,  # Capital Assistance
            13: 80,  # RC/RTI
            14: 80,  # DR
            15: 80,  # Vol
            16: 80,  # VB
            17: 80,  # Incendie
            18: 80,  # Bris
            19: 80,  # AR
            20: 80,  # DTA
            21: 80,  # IPT
            22: 80,  # Prime brute
            23: 70,  # Réductions
            24: 80,  # Prime nette
            25: 80,  # Droit de Timbre
            26: 120  # Actions
        }
        
        for col, width in column_widths.items():
            self.vehicles_table.setColumnWidth(col, width)
        
        self.vehicles_table.setAlternatingRowColors(True)
        self.vehicles_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vehicles_table.setMinimumHeight(350)
        self.vehicles_table.verticalHeader().setDefaultSectionSize(40)
        self.vehicles_table.verticalHeader().setMinimumSectionSize(35)
        
        # Connecter le signal de changement de sélection
        self.vehicles_table.itemClicked.connect(self.on_table_item_clicked)
    
    def create_recap_section(self):
        """Crée la section récapitulative"""
        recap_group = QGroupBox("📊 Récapitulatif")
        recap_layout = QGridLayout(recap_group)
        recap_layout.setSpacing(10)
        recap_layout.setContentsMargins(15, 15, 15, 15)
        
        # Cartes de récapitulatif
        self.recap_cards = {}
        
        recap_items = [
            ('total', "Total véhicules", "0", "🚗"),
            ('selected', "Sélectionnés", "0", "✅"),
            ('rc', "RC/RTI", "0 FCFA", "🛡️"),
            ('dr', "DR", "0 FCFA", "⚖️"),
            ('vol', "Vol", "0 FCFA", "🚗"),
            ('vb', "Vol Braquage", "0 FCFA", "🔫"),
            ('incendie', "Incendie", "0 FCFA", "🔥"),
            ('bris_glace', "Bris de Glace", "0 FCFA", "🪟"),
            ('ar', "AR", "0 FCFA", "🔧"),
            ('dta', "DTA", "0 FCFA", "💥"),
            ('ipt', "IPT", "0 FCFA", "👥"),
            ('prime_brute', "Prime brute", "0 FCFA", "💰"),
            ('prime_nette', "Prime nette", "0 FCFA", "💳"),
            ('carte_rose', "Carte Rose", "0 FCFA", "📄"),
            ('accessoires', "Accessoires", "0 FCFA", "🔧"),
            ('asac', "Fichier ASAC", "0 FCFA", "📁"),
            ('vignette', "Vignette", "0 FCFA", "🏷️"),
            ('tva', "TVA", "0 FCFA", "📊"),
            ('pttc', "PTTC Total", "0 FCFA", "💰"),
        ]
        
        row = 0
        col = 0
        max_cols = 4
        
        for key, label, default_value, icon in recap_items:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: {AppColors.GRAY_LIGHT};
                    border-radius: 8px;
                    padding: 6px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(2)
            
            header_layout = QHBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 12px;")
            label_widget = QLabel(label)
            label_widget.setStyleSheet(f"color: {AppColors.GRAY}; font-size: 9px; font-weight: 500;")
            header_layout.addWidget(icon_label)
            header_layout.addWidget(label_widget)
            header_layout.addStretch()
            
            value_widget = QLabel(default_value)
            value_widget.setStyleSheet(f"color: {AppColors.DARK}; font-size: 14px; font-weight: 700;")
            value_widget.setAlignment(Qt.AlignCenter)
            
            card_layout.addLayout(header_layout)
            card_layout.addWidget(value_widget)
            
            self.recap_cards[key] = value_widget
            recap_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        return recap_group
    
    def create_footer(self):
        """Crée le pied de page"""
        footer = QFrame()
        footer.setStyleSheet(f"border-top: 1px solid {AppColors.BORDER}; padding-top: 12px;")
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Info sur les sélections
        self.selection_info = QLabel("0 véhicules sélectionnés")
        self.selection_info.setStyleSheet(f"color: {AppColors.GRAY}; font-size: 12px;")
        layout.addWidget(self.selection_info)
        
        layout.addStretch()
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setProperty("class", "BtnSecondary")
        self.cancel_btn.setFixedSize(120, 35)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.import_btn = QPushButton("✅ Importer la flotte")
        self.import_btn.setProperty("class", "BtnSuccess")
        self.import_btn.setEnabled(False)
        self.import_btn.setFixedSize(160, 40)
        self.import_btn.clicked.connect(self.import_fleet)
        
        layout.addWidget(self.cancel_btn)
        layout.addSpacing(10)
        layout.addWidget(self.import_btn)
        
        return footer
    
    def on_table_item_clicked(self, item):
        """Gère le clic sur un élément du tableau"""
        # Mettre à jour le compteur de sélection
        self.update_selection_count()
    
    def update_selection_count(self):
        """Met à jour le compteur de véhicules sélectionnés"""
        count = 0
        for row in range(self.vehicles_table.rowCount()):
            item = self.vehicles_table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                count += 1
        self.selection_info.setText(f"{count} véhicule(s) sélectionné(s)")
    
    def select_file(self):
        """Sélectionne le fichier"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier", "",
            "Excel (*.xlsx *.xls);;CSV (*.csv)"
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.load_file()

    # def load_file(self):
    #     """Charge le fichier avec détection intelligente du tableau"""
    #     try:
    #         if self.file_path.endswith(('.xlsx', '.xls')):
    #             df_raw = pd.read_excel(self.file_path, header=None)
    #         else:
    #             df_raw = pd.read_csv(self.file_path, encoding='utf-8', header=None)
            
    #         # Trouver la ligne où commence le tableau
    #         header_row = -1
            
    #         for idx, row in df_raw.iterrows():
    #             row_values = [str(v).strip() if pd.notna(v) else '' for v in row.values]
    #             if 'Rang' in row_values:
    #                 # Nouvelles colonnes attendues
    #                 expected_headers = ['Rang', 'Immatriculation', 'Numero Chassi', 'Marque et Type', 
    #                                 'Genre', 'Puissance en CV', 'Usage', 'Nombre de Places', 
    #                                 'Nombre de jours assurés', 'PMEC', 'Valeur Neuve', 
    #                                 'Valeur Venale', 'Capital Assistance à la réparation',
    #                                 'RC/RTI', 'Défense et Recours', 'Vol/Vol partiel - Braquage', 
    #                                 'Incendie', 'Bris de Glaces', 'Assistance à la réparation', 
    #                                 'Dommages Tous Accidents', 'IPT + Conducteur', 
    #                                 'Prime brute', 'Réductions', 'Prime nette', 'Droit de Timbre Automobile']
    #                 match_count = sum(1 for h in expected_headers if h in row_values)
    #                 if match_count >= 10:
    #                     header_row = idx
    #                     break
            
    #         if header_row == -1:
    #             for idx, row in df_raw.iterrows():
    #                 if 'Rang' in str(row.values):
    #                     header_row = idx
    #                     break
                
    #             if header_row == -1:
    #                 self.file_info.setText("❌ Impossible de trouver le tableau")
    #                 self.status_text.setText("Erreur: format de fichier non reconnu")
    #                 return
            
    #         # Récupérer les en-têtes et les données
    #         header_values = df_raw.iloc[header_row].values
    #         data_values = df_raw.values[header_row+1:]
            
    #         # Trouver la dernière colonne non vide dans les en-têtes
    #         max_cols = 0
    #         for i, val in enumerate(header_values):
    #             if pd.notna(val) and str(val).strip():
    #                 max_cols = i + 1
            
    #         if max_cols == 0:
    #             max_cols = len(header_values)
            
    #         # Tronquer les données pour correspondre au nombre d'en-têtes
    #         header_values = header_values[:max_cols]
    #         data_values = data_values[:, :max_cols]
            
    #         # Créer le DataFrame
    #         df = pd.DataFrame(data_values, columns=range(max_cols))
            
    #         # Renommer les colonnes avec les en-têtes
    #         column_names = []
    #         for i, val in enumerate(header_values):
    #             if pd.notna(val):
    #                 name = str(val).strip()
    #                 if name in column_names:
    #                     name = f"{name}.{column_names.count(name)}"
    #                 column_names.append(name)
    #             else:
    #                 column_names.append(f"Col_{i}")
            
    #         df.columns = column_names
            
    #         # ✅ MAPPING DES COLONNES AVEC LES NOUVEAUX NOMS
    #         column_mapping = {}
    #         for col in df.columns:
    #             col_lower = col.lower().strip()
                
    #             # Identifiants
    #             if 'immatriculation' in col_lower:
    #                 column_mapping[col] = 'Immatriculation'
    #             elif 'numéro chassi' in col_lower or 'numero chassi' in col_lower or 'chassi' in col_lower:
    #                 column_mapping[col] = 'Chassis'
    #             elif 'marque' in col_lower or 'type' in col_lower:
    #                 column_mapping[col] = 'Marque et Type'
    #             elif 'rang' in col_lower:
    #                 column_mapping[col] = 'Rang'
                
    #             # Caractéristiques
    #             elif 'genre' in col_lower:
    #                 column_mapping[col] = 'Genre'
    #             elif 'puissance' in col_lower:
    #                 column_mapping[col] = 'Puissance en CV'
    #             elif 'usage' in col_lower:
    #                 column_mapping[col] = 'Usage'
    #             elif 'place' in col_lower:
    #                 column_mapping[col] = 'Nombre de Places'
    #             elif 'jour' in col_lower:
    #                 column_mapping[col] = 'Nombre de jours assurés'
    #             elif 'pmec' in col_lower:
    #                 column_mapping[col] = 'PMEC'
                
    #             # Valeurs financières
    #             elif 'valeur neuf' in col_lower or 'valeur_neuf' in col_lower:
    #                 column_mapping[col] = 'Valeur Neuve'
    #             elif 'valeur venale' in col_lower or 'valeur_venale' in col_lower:
    #                 column_mapping[col] = 'Valeur Venale'
    #             elif 'capital' in col_lower and 'assistance' in col_lower:
    #                 column_mapping[col] = 'Capital Assistance à la réparation'
                
    #             # Garanties
    #             elif 'rc' in col_lower or 'rti' in col_lower:
    #                 column_mapping[col] = 'RC/RTI'
    #             elif 'défense' in col_lower or 'defense' in col_lower:
    #                 column_mapping[col] = 'Défense et Recours'
    #             elif 'vol/vol' in col_lower or 'vol partiel' in col_lower:
    #                 column_mapping[col] = 'Vol/Vol partie'
    #             elif 'vol braquage' in col_lower or 'braquage' in col_lower:
    #                 column_mapping[col] = 'Vol Braquage'
    #             elif 'incendie' in col_lower:
    #                 column_mapping[col] = 'Incendie'
    #             elif 'bris' in col_lower:
    #                 column_mapping[col] = 'Bris de Glaces'
    #             elif 'assistance' in col_lower and 'réparation' in col_lower:
    #                 column_mapping[col] = 'Assistance à la réparation'
    #             elif 'dommages' in col_lower or 'dta' in col_lower:
    #                 column_mapping[col] = 'Dommages Tous Accidents'
    #             elif 'ipt' in col_lower or 'individuelle' in col_lower:
    #                 column_mapping[col] = 'IPT + Conducteur'
                
    #             # Primes
    #             elif 'prime brute' in col_lower:
    #                 column_mapping[col] = 'Prime brute'
    #             elif 'réductions' in col_lower or 'reductions' in col_lower:
    #                 column_mapping[col] = 'Réductions'
    #             elif 'prime nette' in col_lower:
    #                 column_mapping[col] = 'Prime nette'
    #             elif 'timbre' in col_lower:
    #                 column_mapping[col] = 'Droit de Timbre Automobile'
            
    #         # Appliquer le renommage
    #         df.rename(columns=column_mapping, inplace=True)
            
    #         # ✅ VÉRIFIER QUE LES COLONNES OBLIGATOIRES EXISTENT
    #         if 'Immatriculation' not in df.columns:
    #             for col in df.columns:
    #                 if 'immat' in col.lower():
    #                     df.rename(columns={col: 'Immatriculation'}, inplace=True)
    #                     break
    #             else:
    #                 self.file_info.setText("❌ Colonne Immatriculation non trouvée")
    #                 self.status_text.setText("Erreur: colonne Immatriculation manquante")
    #                 return
            
    #         # Si 'Chassis' n'existe pas, créer une colonne vide
    #         if 'Chassis' not in df.columns:
    #             df['Chassis'] = ''
            
    #         # ✅ TRAITER LA COLONNE IMMATRICULATION
    #         df['Immatriculation'] = df['Immatriculation'].fillna('')
    #         df['Immatriculation'] = df['Immatriculation'].astype(str)
    #         df['Immatriculation'] = df['Immatriculation'].str.strip()
            
    #         # Filtrer les lignes vides
    #         df = df[df['Immatriculation'] != '']
    #         df = df[df['Immatriculation'] != 'nan']
    #         df = df[df['Immatriculation'] != 'None']
    #         df = df[df['Immatriculation'] != 'NaN']
    #         df = df[df['Immatriculation'].notna()]
            
    #         # Filtrer les lignes qui commencent par '=' ou contiennent des formules
    #         mask = ~df['Immatriculation'].str.startswith('=', na=False)
    #         df = df[mask]
            
    #         # Filtrer les lignes de total
    #         mask = ~df['Immatriculation'].str.contains('Prime|Total|Sous-total|Réductions|nette|CARBURANT', case=False, na=False)
    #         df = df[mask]
            
    #         df = df.reset_index(drop=True)
            
    #         if df.empty:
    #             self.file_info.setText("❌ Aucune donnée valide trouvée")
    #             self.status_text.setText("Erreur: fichier vide ou mal formaté")
    #             return
            
    #         # ✅ VÉRIFIER QUE 'Marque et Type' EXISTE
    #         if 'Marque et Type' not in df.columns:
    #             df['Marque et Type'] = ''
            
    #         # ✅ FONCTION POUR EXTRAIRE PUISSANCE ET ÉNERGIE
    #         def extract_power_and_energy(value):
    #             """
    #             Extrait la puissance et le type d'énergie d'une chaîne comme '9D', '6E', '4H'
    #             Retourne (puissance, energie)
    #             D = Diesel
    #             E = Essence
    #             H = Hybride
    #             """
    #             if pd.isna(value) or not value:
    #                 return (0, 'Essence')
                
    #             val_str = str(value).strip().upper()
                
    #             # Si c'est déjà un nombre pur
    #             if val_str.isdigit():
    #                 return (int(val_str), 'Essence')
                
    #             # Extraire le nombre et la lettre
    #             import re
    #             match = re.match(r'^(\d+)\s*([DEH]?)$', val_str)
    #             if match:
    #                 puissance = int(match.group(1))
    #                 energie_letter = match.group(2)
                    
    #                 # Convertir la lettre en nom complet
    #                 if energie_letter == 'D':
    #                     energie = 'SED'
    #                 elif energie_letter == 'E':
    #                     energie = 'SEE'
    #                 elif energie_letter == 'H':
    #                     energie = 'Hybride'
    #                 else:
    #                     energie = 'SEE'
                    
    #                 return (puissance, energie)
                
    #             # Fallback: essayer d'extraire juste le nombre
    #             numbers = re.findall(r'\d+', val_str)
    #             if numbers:
    #                 return (int(numbers[0]), 'SEE')
                
    #             return (0, 'SEE')
    #         # ✅ TRAITER LA COLONNE PUISSANCE EN CV
    #         if 'Puissance en CV' in df.columns:
    #             # Appliquer l'extraction sur chaque ligne
    #             power_data = df['Puissance en CV'].apply(extract_power_and_energy)
    #             df['Puissance'] = power_data.apply(lambda x: x[0])
    #             df['Energie'] = power_data.apply(lambda x: x[1])
    #         else:
    #             df['Puissance'] = 0
    #             df['Energie'] = 'SEE'

    #         # ✅ FONCTION POUR EXTRAIRE LA DATE DE PMEC
    #         def extract_pmec_date(value):
    #             """
    #             Extrait la date de mise en circulation de la colonne PMEC
    #             """
    #             if pd.isna(value) or not value:
    #                 return None
                
    #             # Si c'est déjà un datetime
    #             if isinstance(value, (pd.Timestamp, datetime)):
    #                 return value
                
    #             # Si c'est une chaîne
    #             val_str = str(value).strip()
                
    #             # Essayer différents formats
    #             formats = [
    #                 '%Y-%m-%d %H:%M:%S',
    #                 '%Y-%m-%d',
    #                 '%d/%m/%Y',
    #                 '%m/%d/%Y',
    #                 '%d-%m-%Y',
    #                 '%m-%d-%Y'
    #             ]
                
    #             for fmt in formats:
    #                 try:
    #                     return datetime.strptime(val_str, fmt)
    #                 except:
    #                     continue
                
    #             # Si c'est un nombre Excel
    #             try:
    #                 num_val = float(val_str)
    #                 # Les dates Excel commencent à partir de 1900-01-01
    #                 if num_val > 10000:  # Les dates Excel sont > 10000
    #                     from datetime import timedelta
    #                     base = datetime(1899, 12, 30)
    #                     return base + timedelta(days=num_val)
    #             except:
    #                 pass
                
    #             return None

    #         # ✅ TRAITER LA COLONNE PMEC
    #         if 'PMEC' in df.columns:
    #             df['Date_Mise_Circulation'] = df['PMEC'].apply(extract_pmec_date)
    #             # Garder la date au format string pour l'affichage
    #             df['PMEC_Display'] = df['Date_Mise_Circulation'].apply(
    #                 lambda x: x.strftime('%d/%m/%Y') if x else ''
    #             )
    #         else:
    #             df['Date_Mise_Circulation'] = None
    #             df['PMEC_Display'] = ''
                
    #         # Préparer les véhicules
    #         self.vehicles_data = []
            
    #         def safe_float(val):
    #             try:
    #                 if pd.isna(val):
    #                     return 0
    #                 if isinstance(val, (int, float)):
    #                     return float(val)
    #                 # Nettoyer les chaînes avec des formules Excel
    #                 val_str = str(val).strip()
    #                 if val_str.startswith('='):
    #                     return 0
    #                 return float(val_str.replace(' ', '').replace(',', '')) if val_str else 0
    #             except:
    #                 return 0
            
    #         def safe_int(val):
    #             try:
    #                 if pd.isna(val):
    #                     return 0
    #                 return int(float(val))
    #             except:
    #                 return 0
            
    #         for idx, row in df.iterrows():
    #             marque_type = str(row.get('Marque et Type', '')).strip()
    #             marque_parts = marque_type.split(' ', 1)
    #             marque = marque_parts[0] if marque_parts else ''
    #             modele = marque_parts[1] if len(marque_parts) > 1 else ''
                
    #             # Récupérer le châssis
    #             chassis = str(row.get('Chassis', '')).strip()
                
    #             # Récupérer la puissance et l'énergie
    #             puissance = safe_float(row.get('Puissance', 0))
    #             energie = row.get('Energie', 'SEE')
                
    #             vehicle = {
    #                 'id': idx + 1,
    #                 'rang': safe_int(row.get('Rang', idx + 1)),
    #                 'immatriculation': str(row.get('Immatriculation', '')).strip().upper(),
    #                 'chassis': chassis,
    #                 'marque': marque,
    #                 'modele': modele,
    #                 'marque_type': marque_type,
    #                 'genre': str(row.get('Genre', 'VP')).strip() if pd.notna(row.get('Genre')) else 'VP',
    #                 'puissance': puissance,
    #                 'energie': energie,
    #                 'usage': str(row.get('Usage', '')).strip() if pd.notna(row.get('Usage')) else '',
    #                 'places': safe_int(row.get('Nombre de Places', 5)),
    #                 'nbr_jour': safe_int(row.get('Nombre de jours assurés', 365)),
    #                 'pmec': row.get('PMEC_Display', ''),
    #                 'valeur_neuf': safe_float(row.get('Valeur Neuve', 0)),
    #                 'valeur_venale': safe_float(row.get('Valeur Venale', 0)),
    #                 'capital_ar': safe_float(row.get('Capital Assistance à la réparation', 0)),
    #                 'garanties': {
    #                     'rc': safe_float(row.get('RC/RTI', 0)),
    #                     'dr': safe_float(row.get('Défense et Recours', 0)),
    #                     'vol': safe_float(row.get('Vol/Vol partie', 0)),
    #                     'vb': safe_float(row.get('Vol Braquage', 0)),
    #                     'incendie': safe_float(row.get('Incendie', 0)),
    #                     'bris_glace': safe_float(row.get('Bris de Glaces', 0)),
    #                     'ar': safe_float(row.get('Assistance à la réparation', 0)),
    #                     'dta': safe_float(row.get('Dommages Tous Accidents', 0)),
    #                     'ipt': safe_float(row.get('IPT + Conducteur', 0)),
    #                 },
    #                 'prime_brute': safe_float(row.get('Prime brute', 0)),
    #                 'reductions': safe_float(row.get('Réductions', 0)),
    #                 'prime_nette': safe_float(row.get('Prime nette', 0)),
    #                 'droit_timbre': safe_float(row.get('Droit de Timbre Automobile', 0)),
    #                 'accessoires': 0,
    #                 'asac': 0,
    #                 'carte_rose': 0,
    #                 'vignette': 0,
    #                 'tva': 0,
    #                 'pttc': 0,
    #                 'status': 'loaded',
    #                 'from_fleet': False
    #             }
                
    #             total = sum(vehicle['garanties'].values())
    #             vehicle['garanties']['total'] = total
                
    #             if vehicle['immatriculation'] and vehicle['immatriculation'] not in ['NAN', 'NONE', '']:
    #                 self.vehicles_data.append(vehicle)
            
    #         if not self.vehicles_data:
    #             self.file_info.setText("❌ Aucun véhicule trouvé dans le fichier")
    #             self.status_text.setText("Erreur: aucun véhicule valide")
    #             return
            
    #         self.file_info.setText(f"✅ {len(self.vehicles_data)} véhicules trouvés")
    #         self.status_text.setText(f"{len(self.vehicles_data)} véhicules chargés")
    #         self.status_icon.setText("✅")
    #         self.calc_btn.setEnabled(True)
    #         self.display_vehicles()
            
    #     except Exception as e:
    #         self.file_info.setText(f"❌ Erreur: {str(e)}")
    #         self.status_text.setText(f"Erreur: {str(e)}")
    #         self.status_icon.setText("❌")
    #         traceback.print_exc()

    def load_file(self):
        """Charge le fichier avec détection intelligente du tableau"""
        try:
            if self.file_path.endswith(('.xlsx', '.xls')):
                # ✅ Lire le fichier avec openpyxl pour évaluer les formules
                import openpyxl
                from openpyxl.utils import get_column_letter
                
                wb = openpyxl.load_workbook(self.file_path, data_only=True)
                ws = wb.active
                
                # Convertir en DataFrame en utilisant les valeurs calculées
                data = []
                for row in ws.iter_rows(values_only=True):
                    data.append(row)
                
                df_raw = pd.DataFrame(data)
                wb.close()
            else:
                df_raw = pd.read_csv(self.file_path, encoding='utf-8', header=None)
            
            # Trouver la ligne où commence le tableau
            header_row = -1
            
            for idx, row in df_raw.iterrows():
                row_values = [str(v).strip() if pd.notna(v) else '' for v in row.values]
                if 'Rang' in row_values:
                    # Nouvelles colonnes attendues
                    expected_headers = ['Rang', 'Immatriculation', 'Numero Chassi', 'Marque et Type', 
                                    'Genre', 'Puissance en CV', 'Usage', 'Nombre de Places', 
                                    'Nombre de jours assurés', 'PMEC', 'Valeur Neuve', 
                                    'Valeur Venale', 'Capital Assistance à la réparation',
                                    'RC/RTI', 'Défense et Recours', 'Vol/Vol partiel - Braquage', 
                                    'Incendie', 'Bris de Glaces', 'Assistance à la réparation', 
                                    'Dommages Tous Accidents', 'IPT + Conducteur', 
                                    'Prime brute', 'Réductions', 'Prime nette', 'Droit de Timbre Automobile']
                    match_count = sum(1 for h in expected_headers if h in row_values)
                    if match_count >= 10:
                        header_row = idx
                        break
            
            if header_row == -1:
                for idx, row in df_raw.iterrows():
                    if 'Rang' in str(row.values):
                        header_row = idx
                        break
                
                if header_row == -1:
                    self.file_info.setText("❌ Impossible de trouver le tableau")
                    self.status_text.setText("Erreur: format de fichier non reconnu")
                    return
            
            # Récupérer les en-têtes et les données
            header_values = df_raw.iloc[header_row].values
            data_values = df_raw.values[header_row+1:]
            
            # Trouver la dernière colonne non vide dans les en-têtes
            max_cols = 0
            for i, val in enumerate(header_values):
                if pd.notna(val) and str(val).strip():
                    max_cols = i + 1
            
            if max_cols == 0:
                max_cols = len(header_values)
            
            # Tronquer les données pour correspondre au nombre d'en-têtes
            header_values = header_values[:max_cols]
            data_values = data_values[:, :max_cols]
            
            # Créer le DataFrame
            df = pd.DataFrame(data_values, columns=range(max_cols))
            
            # Renommer les colonnes avec les en-têtes
            column_names = []
            for i, val in enumerate(header_values):
                if pd.notna(val):
                    name = str(val).strip()
                    if name in column_names:
                        name = f"{name}.{column_names.count(name)}"
                    column_names.append(name)
                else:
                    column_names.append(f"Col_{i}")
            
            df.columns = column_names
            
            # Mapping des colonnes
            column_mapping = {}
            for col in df.columns:
                col_lower = col.lower().strip()
                
                if 'immatriculation' in col_lower:
                    column_mapping[col] = 'Immatriculation'
                elif 'numéro chassi' in col_lower or 'numero chassi' in col_lower or 'chassi' in col_lower:
                    column_mapping[col] = 'Chassis'
                elif 'marque' in col_lower or 'type' in col_lower:
                    column_mapping[col] = 'Marque et Type'
                elif 'rang' in col_lower:
                    column_mapping[col] = 'Rang'
                elif 'genre' in col_lower:
                    column_mapping[col] = 'Genre'
                elif 'puissance' in col_lower:
                    column_mapping[col] = 'Puissance en CV'
                elif 'usage' in col_lower:
                    column_mapping[col] = 'Usage'
                elif 'place' in col_lower:
                    column_mapping[col] = 'Nombre de Places'
                elif 'jour' in col_lower:
                    column_mapping[col] = 'Nombre de jours assurés'
                elif 'pmec' in col_lower:
                    column_mapping[col] = 'PMEC'
                elif 'valeur neuf' in col_lower or 'valeur_neuf' in col_lower:
                    column_mapping[col] = 'Valeur Neuve'
                elif 'valeur venale' in col_lower or 'valeur_venale' in col_lower:
                    column_mapping[col] = 'Valeur Venale'
                elif 'capital' in col_lower and 'assistance' in col_lower:
                    column_mapping[col] = 'Capital Assistance à la réparation'
                elif 'rc' in col_lower or 'rti' in col_lower:
                    column_mapping[col] = 'RC/RTI'
                elif 'défense' in col_lower or 'defense' in col_lower:
                    column_mapping[col] = 'Défense et Recours'
                elif 'vol/vol' in col_lower or 'vol partiel' in col_lower:
                    column_mapping[col] = 'Vol/Vol partie'
                elif 'vol braquage' in col_lower or 'braquage' in col_lower:
                    column_mapping[col] = 'Vol Braquage'
                elif 'incendie' in col_lower:
                    column_mapping[col] = 'Incendie'
                elif 'bris' in col_lower:
                    column_mapping[col] = 'Bris de Glaces'
                elif 'assistance' in col_lower and 'réparation' in col_lower:
                    column_mapping[col] = 'Assistance à la réparation'
                elif 'dommages' in col_lower or 'dta' in col_lower:
                    column_mapping[col] = 'Dommages Tous Accidents'
                elif 'ipt' in col_lower or 'individuelle' in col_lower:
                    column_mapping[col] = 'IPT + Conducteur'
                elif 'prime brute' in col_lower:
                    column_mapping[col] = 'Prime brute'
                elif 'réductions' in col_lower or 'reductions' in col_lower:
                    column_mapping[col] = 'Réductions'
                elif 'prime nette' in col_lower:
                    column_mapping[col] = 'Prime nette'
                elif 'timbre' in col_lower:
                    column_mapping[col] = 'Droit de Timbre Automobile'
            
            df.rename(columns=column_mapping, inplace=True)
            
            # Vérifier les colonnes obligatoires
            if 'Immatriculation' not in df.columns:
                for col in df.columns:
                    if 'immat' in col.lower():
                        df.rename(columns={col: 'Immatriculation'}, inplace=True)
                        break
                else:
                    self.file_info.setText("❌ Colonne Immatriculation non trouvée")
                    self.status_text.setText("Erreur: colonne Immatriculation manquante")
                    return
            
            if 'Chassis' not in df.columns:
                df['Chassis'] = ''
            
            # Traiter la colonne Immatriculation
            df['Immatriculation'] = df['Immatriculation'].fillna('')
            df['Immatriculation'] = df['Immatriculation'].astype(str)
            df['Immatriculation'] = df['Immatriculation'].str.strip()
            
            # Filtrer les lignes vides
            df = df[df['Immatriculation'] != '']
            df = df[df['Immatriculation'] != 'nan']
            df = df[df['Immatriculation'] != 'None']
            df = df[df['Immatriculation'] != 'NaN']
            df = df[df['Immatriculation'].notna()]
            
            # Filtrer les lignes qui commencent par '='
            mask = ~df['Immatriculation'].str.startswith('=', na=False)
            df = df[mask]
            
            # Filtrer les lignes de total
            mask = ~df['Immatriculation'].str.contains('Prime|Total|Sous-total|Réductions|nette|CARBURANT', case=False, na=False)
            df = df[mask]
            
            df = df.reset_index(drop=True)
            
            if df.empty:
                self.file_info.setText("❌ Aucune donnée valide trouvée")
                self.status_text.setText("Erreur: fichier vide ou mal formaté")
                return
            
            if 'Marque et Type' not in df.columns:
                df['Marque et Type'] = ''
            
            # ✅ FONCTION POUR EXTRAIRE PUISSANCE ET ÉNERGIE
            def extract_power_and_energy(value):
                if pd.isna(value) or not value:
                    return (0, 'SEE')
                
                val_str = str(value).strip().upper()
                
                if val_str.isdigit():
                    return (int(val_str), 'SEE')
                
                import re
                match = re.match(r'^(\d+)\s*([DEH]?)$', val_str)
                if match:
                    puissance = int(match.group(1))
                    energie_letter = match.group(2)
                    
                    if energie_letter == 'D':
                        energie = 'SED'
                    elif energie_letter == 'E':
                        energie = 'SEE'
                    elif energie_letter == 'H':
                        energie = 'Hybride'
                    else:
                        energie = 'SEE'
                    
                    return (puissance, energie)
                
                numbers = re.findall(r'\d+', val_str)
                if numbers:
                    return (int(numbers[0]), 'SEE')
                
                return (0, 'SEE')
            
            # Traiter la colonne Puissance en CV
            if 'Puissance en CV' in df.columns:
                power_data = df['Puissance en CV'].apply(extract_power_and_energy)
                df['Puissance'] = power_data.apply(lambda x: x[0])
                df['Energie'] = power_data.apply(lambda x: x[1])
            else:
                df['Puissance'] = 0
                df['Energie'] = 'SEE'
            
            # ✅ FONCTION POUR EXTRAIRE LA DATE DE PMEC
            def extract_pmec_date(value):
                if pd.isna(value) or not value:
                    return None
                
                if isinstance(value, (pd.Timestamp, datetime)):
                    return value
                
                val_str = str(value).strip()
                
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d',
                    '%d/%m/%Y',
                    '%m/%d/%Y',
                    '%d-%m-%Y',
                    '%m-%d-%Y'
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(val_str, fmt)
                    except:
                        continue
                
                try:
                    num_val = float(val_str)
                    if num_val > 10000:
                        from datetime import timedelta
                        base = datetime(1899, 12, 30)
                        return base + timedelta(days=num_val)
                except:
                    pass
                
                return None
            
            # ✅ TRAITER LA COLONNE PMEC
            if 'PMEC' in df.columns:
                df['Date_Mise_Circulation'] = df['PMEC'].apply(extract_pmec_date)
                df['PMEC_Display'] = df['Date_Mise_Circulation'].apply(
                    lambda x: x.strftime('%d/%m/%Y') if x else ''
                )
            else:
                df['Date_Mise_Circulation'] = None
                df['PMEC_Display'] = ''
            
            # ✅ FONCTION POUR EXTRAIRE LES VALEURS (gère les formules Excel)
            def safe_value(val):
                """Extrait une valeur numérique même si c'est une formule Excel"""
                try:
                    if pd.isna(val):
                        return 0
                    # Si c'est déjà un nombre
                    if isinstance(val, (int, float)):
                        return float(val)
                    # Si c'est une chaîne
                    val_str = str(val).strip()
                    if not val_str:
                        return 0
                    # Si c'est une formule Excel commençant par '='
                    if val_str.startswith('='):
                        # Essayer d'évaluer la formule
                        try:
                            # Remplacer les références de cellule par des valeurs si possible
                            import re
                            # Essayer de calculer la formule
                            # Pour simplifier, on retourne 0 si on ne peut pas évaluer
                            return 0
                        except:
                            return 0
                    # Nettoyer la chaîne
                    val_str = val_str.replace(' ', '').replace(',', '')
                    return float(val_str) if val_str else 0
                except:
                    return 0
            
            def safe_int(val):
                try:
                    if pd.isna(val):
                        return 0
                    return int(float(val))
                except:
                    return 0
            
            # ✅ PRÉPARER LES VÉHICULES
            self.vehicles_data = []
            
            for idx, row in df.iterrows():
                marque_type = str(row.get('Marque et Type', '')).strip()
                marque_parts = marque_type.split(' ', 1)
                marque = marque_parts[0] if marque_parts else ''
                modele = marque_parts[1] if len(marque_parts) > 1 else ''
                
                chassis = str(row.get('Chassis', '')).strip()
                puissance = safe_value(row.get('Puissance', 0))
                energie = row.get('Energie', 'SEE')
                
                # ✅ Récupérer les garanties avec safe_value
                rc_value = safe_value(row.get('RC/RTI', 0))
                dr_value = safe_value(row.get('Défense et Recours', 0))
                vol_value = safe_value(row.get('Vol/Vol partie', 0))
                vb_value = safe_value(row.get('Vol Braquage', 0))
                incendie_value = safe_value(row.get('Incendie', 0))
                bris_value = safe_value(row.get('Bris de Glaces', 0))
                ar_value = safe_value(row.get('Assistance à la réparation', 0))
                dta_value = safe_value(row.get('Dommages Tous Accidents', 0))
                ipt_value = safe_value(row.get('IPT + Conducteur', 0))
                
                vehicle = {
                    'id': idx + 1,
                    'rang': safe_int(row.get('Rang', idx + 1)),
                    'immatriculation': str(row.get('Immatriculation', '')).strip().upper(),
                    'chassis': chassis,
                    'marque': marque,
                    'modele': modele,
                    'marque_type': marque_type,
                    'genre': str(row.get('Genre', 'VP')).strip() if pd.notna(row.get('Genre')) else 'VP',
                    'puissance': puissance,
                    'energie': energie,
                    'usage': str(row.get('Usage', '')).strip() if pd.notna(row.get('Usage')) else '',
                    'places': safe_int(row.get('Nombre de Places', 5)),
                    'nbr_jour': safe_int(row.get('Nombre de jours assurés', 365)),
                    'pmec': row.get('PMEC_Display', ''),
                    'date_mise_circulation': row.get('Date_Mise_Circulation', None),
                    'valeur_neuf': safe_value(row.get('Valeur Neuve', 0)),
                    'valeur_venale': safe_value(row.get('Valeur Venale', 0)),
                    'capital_ar': safe_value(row.get('Capital Assistance à la réparation', 0)),
                    'garanties': {
                        'rc': rc_value,
                        'dr': dr_value,
                        'vol': vol_value,
                        'vb': vb_value,
                        'incendie': incendie_value,
                        'bris_glace': bris_value,
                        'ar': ar_value,
                        'dta': dta_value,
                        'ipt': ipt_value,
                    },
                    'prime_brute': safe_value(row.get('Prime brute', 0)),
                    'reductions': safe_value(row.get('Réductions', 0)),
                    'prime_nette': safe_value(row.get('Prime nette', 0)),
                    'droit_timbre': safe_value(row.get('Droit de Timbre Automobile', 0)),
                    'accessoires': 0,
                    'asac': 0,
                    'carte_rose': 0,
                    'vignette': 0,
                    'tva': 0,
                    'pttc': 0,
                    'status': 'loaded',
                    'from_fleet': False
                }
                
                total = sum(vehicle['garanties'].values())
                vehicle['garanties']['total'] = total
                
                if vehicle['immatriculation'] and vehicle['immatriculation'] not in ['NAN', 'NONE', '']:
                    self.vehicles_data.append(vehicle)
            
            if not self.vehicles_data:
                self.file_info.setText("❌ Aucun véhicule trouvé dans le fichier")
                self.status_text.setText("Erreur: aucun véhicule valide")
                return
            
            self.file_info.setText(f"✅ {len(self.vehicles_data)} véhicules trouvés")
            self.status_text.setText(f"{len(self.vehicles_data)} véhicules chargés")
            self.status_icon.setText("✅")
            self.calc_btn.setEnabled(True)
            self.display_vehicles()
            
        except Exception as e:
            self.file_info.setText(f"❌ Erreur: {str(e)}")
            self.status_text.setText(f"Erreur: {str(e)}")
            self.status_icon.setText("❌")
            traceback.print_exc()

    def setup_vehicle_table(self):
        """Configure le tableau avec les nouvelles colonnes"""
        # Nouvelles entêtes avec la colonne Énergie
        headers = [
            "✓",  # 0
            "Rang",  # 1
            "Immatriculation",  # 2
            "Marque et Type",  # 3
            "Genre",  # 4
            "Puissance en CV",  # 5
            "Énergie",  # 6  ← NOUVEAU
            "Usage",  # 7
            "Nombre de Places",  # 8
            "Nombre de jours assurés",  # 9
            "PMEC",  # 10
            "Valeur Neuve",  # 11
            "Valeur Venale",  # 12
            "Capital Assistance à la réparation",  # 13
            "RC/RTI",  # 14
            "Défense et Recours",  # 15
            "Vol/Vol partie",  # 16
            "Vol Braquage",  # 17
            "Incendie",  # 18
            "Bris de Glaces",  # 19
            "Assistance à la réparation",  # 20
            "Dommages Tous Accidents",  # 21
            "IPT + Conducteur",  # 22
            "Prime brute",  # 23
            "Réductions",  # 24
            "Prime nette",  # 25
            "Droit de Timbre Automobile",  # 26
            "Actions"  # 27
        ]
        
        self.vehicles_table = QTableWidget()
        self.vehicles_table.setColumnCount(len(headers))
        self.vehicles_table.setHorizontalHeaderLabels(headers)
        
        # Configuration des colonnes
        column_widths = {
            0: 30,   # ✓
            1: 40,   # Rang
            2: 100,  # Immatriculation
            3: 120,  # Marque et Type
            4: 70,   # Genre
            5: 80,   # Puissance en CV
            6: 80,   # Énergie  ← NOUVEAU
            7: 80,   # Usage
            8: 60,   # Nombre de Places
            9: 80,   # Nombre de jours assurés
            10: 70,  # PMEC
            11: 90,  # Valeur Neuve
            12: 90,  # Valeur Venale
            13: 90,  # Capital Assistance
            14: 80,  # RC/RTI
            15: 80,  # DR
            16: 80,  # Vol
            17: 80,  # VB
            18: 80,  # Incendie
            19: 80,  # Bris
            20: 80,  # AR
            21: 80,  # DTA
            22: 80,  # IPT
            23: 80,  # Prime brute
            24: 70,  # Réductions
            25: 80,  # Prime nette
            26: 80,  # Droit de Timbre
            27: 120  # Actions
        }
        
        for col, width in column_widths.items():
            self.vehicles_table.setColumnWidth(col, width)
        
        self.vehicles_table.setAlternatingRowColors(True)
        self.vehicles_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vehicles_table.setMinimumHeight(350)
        self.vehicles_table.verticalHeader().setDefaultSectionSize(40)
        self.vehicles_table.verticalHeader().setMinimumSectionSize(35)
        
        # Connecter le signal de changement de sélection
        self.vehicles_table.itemClicked.connect(self.on_table_item_clicked)

    def display_vehicles(self):
        """Affiche les véhicules dans le tableau avec les nouvelles colonnes"""
        self.vehicles_table.setRowCount(len(self.vehicles_data))
        
        for row, vehicle in enumerate(self.vehicles_data):
            # Case à cocher
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Checked)
            self.vehicles_table.setItem(row, 0, check_item)
            
            # Mettre à jour la ligne (utilise update_vehicle_row qui gère toutes les colonnes)
            self.update_vehicle_row(row, vehicle)
            
            # Actions (colonne 27)
            vehicle_id = vehicle.get('id', row)
            actions_widget = VehicleActionsWidget(
                vehicle_id,
                self.edit_vehicle_garanties,
                self.edit_vehicle_dates,
                self.on_modify_vehicle
            )
            self.vehicles_table.setCellWidget(row, 27, actions_widget)
        
        self.adjust_row_heights()
        self.update_selection_count()
        self.update_summary()

    def apply_mass_reduction(self):
        """Applique une réduction en masse sur les garanties sélectionnées"""
        if not self.vehicles_data:
            QMessageBox.warning(self, "Erreur", "Aucun véhicule chargé")
            return
        
        # Vérifier qu'il y a des véhicules sélectionnés
        selected_rows = []
        for row in range(self.vehicles_table.rowCount()):
            item = self.vehicles_table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                selected_rows.append(row)
        
        if not selected_rows:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner au moins un véhicule")
            return
        
        # Ouvrir le dialogue de réduction
        dialog = MassReductionDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
        
        selected_garanties = dialog.get_selected_garanties()
        if not selected_garanties:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner au moins une garantie")
            return
        
        reduction_value = dialog.get_reduction_value()
        mode = dialog.get_mode()
        
        if reduction_value <= 0 and mode != 2:
            QMessageBox.warning(self, "Erreur", "La réduction doit être supérieure à 0")
            return
        
        # Appliquer la réduction
        applied_count = 0
        for row in selected_rows:
            vehicle = self.vehicles_data[row]
            if 'garanties' not in vehicle:
                continue
            
            garanties = vehicle['garanties']
            modifications = {}
            
            for key in selected_garanties:
                if key not in garanties:
                    continue
                
                current_value = garanties.get(key, 0)
                
                if mode == 0:  # Réduire les montants (soustraire)
                    new_value = max(0, current_value - reduction_value)
                elif mode == 1:  # Coefficient multiplicateur
                    new_value = current_value * (1 - reduction_value / 100)
                else:  # Montant fixe maximum
                    new_value = min(current_value, reduction_value)
                
                modifications[key] = new_value
            
            # Appliquer les modifications
            total_keys = ['rc', 'dr', 'vol', 'vb', 'incendie', 'bris_glace', 'ar', 'dta', 'ipt']
            for key, new_value in modifications.items():
                garanties[key] = new_value
            
            # Recalculer le total
            garanties['total'] = sum(garanties.get(k, 0) for k in total_keys)
            
            # Mettre à jour les colonnes du tableau
            garanties_cols = {
                'rc': 13, 'dr': 14, 'vol': 15, 'vb': 16,
                'incendie': 17, 'bris_glace': 18, 'ar': 19,
                'dta': 20, 'ipt': 21
            }
            
            for key, col in garanties_cols.items():
                amount = garanties.get(key, 0)
                item = self.vehicles_table.item(row, col)
                if item:
                    item.setText(f"{amount:,.0f}".replace(",", " "))
            
            # Mettre à jour les primes
            prime_brute = garanties.get('total', 0)
            pb_item = self.vehicles_table.item(row, 22)
            if pb_item:
                pb_item.setText(f"{prime_brute:,.0f}".replace(",", " "))
            
            pn_item = self.vehicles_table.item(row, 24)
            if pn_item:
                pn_item.setText(f"{prime_brute:,.0f}".replace(",", " "))
            
            # Mettre à jour les réductions
            reductions_item = self.vehicles_table.item(row, 23)
            if reductions_item:
                reductions_item.setText(f"{reduction_value:.0f}")
            
            applied_count += 1
        
        # Mettre à jour les récapitulatifs
        self.update_summary()
        
        QMessageBox.information(
            self, 
            "Succès", 
            f"✅ Réduction appliquée à {applied_count} véhicule(s)\n"
            f"Garanties concernées: {len(selected_garanties)}\n"
            f"Valeur: {reduction_value}"
        )
    
    def start_calculation(self):
        """Démarre le calcul des garanties"""
        if not self.vehicles_data:
            return
        
        # Calculer la durée
        debut = self.date_debut.date().toPython()
        fin = self.date_fin.date().toPython()
        jours = max(1, (fin - debut).days)
        
        params = {
            'compagny_id': 1,  # ID par défaut
            'zone': 'A',
            'code_tarif': '',
            'avec_remorque': False,
            'duree_jours': jours
        }
        
        # Mettre à jour l'UI
        self.calc_btn.setEnabled(False)
        self.calc_btn.setText("Calcul en cours...")
        self.progress_widget.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_icon.setText("🔄")
        self.status_text.setText("Calcul des garanties en cours...")
        
        # Démarrer le thread
        self.calculation_thread = CalculationThread(self.controller, self.vehicles_data, params)
        self.calculation_thread.progress.connect(self.on_calculation_progress)
        self.calculation_thread.finished_signal.connect(self.on_calculation_finished)
        self.calculation_thread.start()
      
    def get_dataon_calculation_finished(self, results):
        """Termine le calcul"""
        self.vehicles_data = results
        self.progress_widget.setVisible(False)
        self.calc_btn.setEnabled(False)
        self.calc_btn.setText("Calcul terminé")
        self.import_btn.setEnabled(True)
        self.mass_reduction_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        
        self.status_icon.setText("✅")
        self.status_text.setText("Calcul terminé, vous pouvez importer les véhicules sélectionnés")
        
        self.update_summary()

    def on_calculation_finished(self, results):
        """Termine le calcul"""
        self.vehicles_data = results
        self.progress_widget.setVisible(False)
        self.calc_btn.setEnabled(False)
        self.calc_btn.setText("Calcul terminé")
        self.import_btn.setEnabled(True)
        self.mass_reduction_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        
        self.status_icon.setText("✅")
        self.status_text.setText("Calcul terminé, vous pouvez importer les véhicules sélectionnés")
        
        self.update_summary()

    def on_calculation_progress(self, current, total, immat, garanties):
        """Met à jour la progression"""
        progress = int(current / total * 100)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Traitement de {immat}... ({current}/{total})")
        
        row = current - 1
        if row >= len(self.vehicles_data):
            return
        
        vehicle = self.vehicles_data[row]
        vehicle['garanties'] = garanties
        
        # Mettre à jour la ligne
        self.update_vehicle_row(row, vehicle)
        
        # Actions
        if not self.vehicles_table.cellWidget(row, 27):
            vehicle_id = vehicle.get('id', row)
            actions_widget = VehicleActionsWidget(
                vehicle_id,
                self.edit_vehicle_garanties,
                self.edit_vehicle_dates,
                self.on_modify_vehicle
            )
            self.vehicles_table.setCellWidget(row, 27, actions_widget)
        
        if current == total:
            self.adjust_row_heights()
            self.update_summary()
            self.mass_reduction_btn.setEnabled(True)
    
    def update_summary(self):
        """Met à jour le récapitulatif"""
        total = len(self.vehicles_data)
        selected = 0
        
        # Initialiser les totaux
        garanties_keys = ['rc', 'dr', 'vol', 'vb', 'incendie', 'bris_glace', 'ar', 'dta', 'ipt']
        totals = {key: 0.0 for key in garanties_keys}
        selected_totals = {key: 0.0 for key in garanties_keys}
        
        total_prime_brute = 0
        total_prime_nette = 0
        total_timbre = 0
        
        # ✅ Totaux des frais
        total_accessoires = 0
        total_asac = 0
        total_carte_rose = 0
        total_vignette = 0
        total_tva = 0
        total_pttc = 0
        
        selected_accessoires = 0
        selected_asac = 0
        selected_carte_rose = 0
        selected_vignette = 0
        selected_tva = 0
        selected_pttc = 0
        
        for row in range(self.vehicles_table.rowCount()):
            item = self.vehicles_table.item(row, 0)
            is_selected = item and item.checkState() == Qt.Checked
            
            if is_selected:
                selected += 1
            
            vehicle = self.vehicles_data[row] if row < len(self.vehicles_data) else None
            if vehicle:
                # Garanties
                if 'garanties' in vehicle:
                    garanties = vehicle['garanties']
                    for key in garanties_keys:
                        amount = garanties.get(key, 0)
                        totals[key] += amount
                        if is_selected:
                            selected_totals[key] += amount
                    
                    if is_selected:
                        total_prime_brute += garanties.get('total', 0)
                        total_prime_nette += vehicle.get('prime_nette', garanties.get('total', 0))
                        total_timbre += vehicle.get('droit_timbre', 0)
                
                # ✅ Frais
                accessoires = vehicle.get('accessoires', 0)
                asac = vehicle.get('asac', 0)
                carte_rose = vehicle.get('carte_rose', 0)
                vignette = vehicle.get('vignette', 0)
                tva = vehicle.get('tva', 0)
                pttc = vehicle.get('pttc', 0)
                
                total_accessoires += accessoires
                total_asac += asac
                total_carte_rose += carte_rose
                total_vignette += vignette
                total_tva += tva
                total_pttc += pttc
                
                if is_selected:
                    selected_accessoires += accessoires
                    selected_asac += asac
                    selected_carte_rose += carte_rose
                    selected_vignette += vignette
                    selected_tva += tva
                    selected_pttc += pttc
        
        # Mettre à jour les cartes des garanties
        self.recap_cards['total'].setText(str(total))
        self.recap_cards['selected'].setText(str(selected))
        self.recap_cards['rc'].setText(f"{selected_totals['rc']:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['dr'].setText(f"{selected_totals['dr']:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['vol'].setText(f"{selected_totals['vol']:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['vb'].setText(f"{selected_totals['vb']:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['incendie'].setText(f"{selected_totals['incendie']:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['bris_glace'].setText(f"{selected_totals['bris_glace']:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['ar'].setText(f"{selected_totals['ar']:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['dta'].setText(f"{selected_totals['dta']:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['ipt'].setText(f"{selected_totals['ipt']:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['prime_brute'].setText(f"{total_prime_brute:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['prime_nette'].setText(f"{total_prime_nette:,.0f}".replace(",", " ") + " FCFA")
        
        # ✅ Mettre à jour les cartes des frais
        self.recap_cards['accessoires'].setText(f"{selected_accessoires:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['asac'].setText(f"{selected_asac:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['carte_rose'].setText(f"{selected_carte_rose:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['vignette'].setText(f"{selected_vignette:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['tva'].setText(f"{selected_tva:,.0f}".replace(",", " ") + " FCFA")
        self.recap_cards['pttc'].setText(f"{selected_pttc:,.0f}".replace(",", " ") + " FCFA")
        
        self.update_selection_count()

    def download_template(self):
        """Télécharge le modèle Excel avec les nouvelles colonnes"""
        template_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le modèle", "modele_flotte_import.xlsx", "Excel (*.xlsx)"
        )
        
        if template_path:
            # Créer un DataFrame avec les nouvelles colonnes
            data = {
                'Rang': [1, 2, 3, 4, 5],
                'Immatriculation': ['LT-001-AB', 'LT-002-BC', 'LT-003-CD', 'LT-004-DE', 'LT-005-EF'],
                'Marque et Type': ['Toyota Hilux', 'Renault Kangoo', 'Mitsubishi Outlander', 'Peugeot Partner', 'Mercedes Sprinter'],
                'Genre': ['VP', 'VU', 'VP', 'VU', 'PL'],
                'Puissance en CV': [7, 5, 6, 4, 8],
                'Usage': ['Transport de personnes', 'Transport de marchandises', 'Transport de personnes', 'Transport de marchandises', 'Transport de personnes'],
                'Nombre de Places': [5, 3, 7, 5, 9],
                'Nombre de jours assurés': [365, 365, 365, 365, 365],
                'PMEC': [2000, 1200, 1800, 1500, 3500],
                'Valeur Neuve': [35000000, 18000000, 28000000, 22000000, 45000000],
                'Valeur Venale': [32000000, 15000000, 26000000, 20000000, 42000000],
                'Capital Assistance à la réparation': [5000000, 3000000, 4000000, 3500000, 6000000],
                'RC/RTI': [0, 0, 0, 0, 0],
                'Défense et Recours': [0, 0, 0, 0, 0],
                'Vol/Vol partie': [0, 0, 0, 0, 0],
                'Vol Braquage': [0, 0, 0, 0, 0],
                'Incendie': [0, 0, 0, 0, 0],
                'Bris de Glaces': [0, 0, 0, 0, 0],
                'Assistance à la réparation': [0, 0, 0, 0, 0],
                'Dommages Tous Accidents': [0, 0, 0, 0, 0],
                'IPT + Conducteur': [0, 0, 0, 0, 0],
                'Prime brute': [0, 0, 0, 0, 0],
                'Réductions': [0, 0, 0, 0, 0],
                'Prime nette': [0, 0, 0, 0, 0],
                'Droit de Timbre Automobile': [5000, 5000, 5000, 5000, 5000]
            }
            
            df = pd.DataFrame(data)
            
            with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Véhicules', index=False)
                
                # Feuille d'instructions
                instructions_data = {
                    'Colonne': list(data.keys()),
                    'Description': [
                        'Numéro de rang (optionnel)',
                        '🔴 OBLIGATOIRE - Plaque d\'immatriculation',
                        '🔴 OBLIGATOIRE - Marque et modèle du véhicule',
                        'Genre du véhicule (VP, VU, PL, etc.)',
                        'Puissance fiscale en CV',
                        'Usage du véhicule',
                        'Nombre de places assises',
                        'Nombre de jours d\'assurance (365 par défaut)',
                        'PMEC (Poids Maximum Autorisé)',
                        'Valeur à neuf du véhicule (FCFA)',
                        'Valeur vénale actuelle (FCFA)',
                        'Capital pour l\'assistance à la réparation',
                        'RC/RTI - Laisser 0 pour calcul automatique',
                        'Défense et Recours - Laisser 0 pour calcul automatique',
                        'Vol/Vol partie - Laisser 0 pour calcul automatique',
                        'Vol Braquage - Laisser 0 pour calcul automatique',
                        'Incendie - Laisser 0 pour calcul automatique',
                        'Bris de Glaces - Laisser 0 pour calcul automatique',
                        'Assistance à la réparation - Laisser 0 pour calcul automatique',
                        'Dommages Tous Accidents - Laisser 0 pour calcul automatique',
                        'IPT + Conducteur - Laisser 0 pour calcul automatique',
                        'Prime brute - Laisser 0 pour calcul automatique',
                        'Réductions - Appliquer manuellement si besoin',
                        'Prime nette - Laisser 0 pour calcul automatique',
                        'Droit de Timbre Automobile (5000 FCFA par défaut)'
                    ],
                    'Statut': [
                        'Optionnel', '🔴 Requis', '🔴 Requis',
                        'Recommandé', 'Recommandé', 'Optionnel',
                        'Recommandé', 'Optionnel', 'Optionnel',
                        'Recommandé', 'Recommandé', 'Optionnel',
                        'Optionnel', 'Optionnel', 'Optionnel',
                        'Optionnel', 'Optionnel', 'Optionnel',
                        'Optionnel', 'Optionnel', 'Optionnel',
                        'Optionnel', 'Optionnel', 'Optionnel',
                        'Optionnel'
                    ]
                }
                
                instructions_df = pd.DataFrame(instructions_data)
                instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
                
                # Ajuster la largeur des colonnes
                from openpyxl.styles import PatternFill, Font, Alignment
                
                workbook = writer.book
                
                # Colorer les en-têtes
                header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                header_font = Font(color="FFFFFF", bold=True)
                
                for sheet_name in ['Véhicules', 'Instructions']:
                    ws = workbook[sheet_name]
                    for cell in ws[1]:
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = Alignment(horizontal='center')
                    
                    # Ajuster la largeur des colonnes
                    for column in ws.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 40)
                        ws.column_dimensions[column_letter].width = adjusted_width
            
            QMessageBox.information(
                self, 
                "Succès", 
                f"✅ Modèle créé avec succès !\n\n"
                f"📁 Emplacement: {template_path}\n\n"
                f"📋 Le fichier contient:\n"
                f"  • Une feuille 'Véhicules' avec les données à remplir\n"
                f"  • Une feuille 'Instructions' avec la description des colonnes\n\n"
                f"🔴 Les colonnes obligatoires sont:\n"
                f"  • Immatriculation\n"
                f"  • Marque et Type"
            )
    
    def adjust_row_heights(self):
        """Ajuste la hauteur des lignes"""
        for row in range(self.vehicles_table.rowCount()):
            self.vehicles_table.setRowHeight(row, 40)
    
    # Méthodes de gestion des flottes existantes (simplifiées)
    def on_mode_changed(self):
        """Change le mode d'importation"""
        is_new = self.mode_new.isChecked()
        self.new_fleet_widget.setVisible(is_new)
        self.existing_fleet_widget.setVisible(not is_new)
        
        if not is_new:
            self.load_existing_fleets()
            # Connecter le signal de changement de sélection
            try:
                self.existing_fleet_combo.currentIndexChanged.disconnect()
            except:
                pass
            self.existing_fleet_combo.currentIndexChanged.connect(self.on_existing_fleet_selected)
        else:
            # Déconnecter pour éviter les appels inutiles
            try:
                self.existing_fleet_combo.currentIndexChanged.disconnect()
            except:
                pass
      
    def load_existing_fleets(self):
        """Charge les flottes existantes depuis la base de données"""
        try:
            self.existing_fleet_combo.clear()
            self.existing_fleet_combo.addItem("Sélectionner une flotte", None)
            
            # Récupérer l'ID du contact propriétaire
            contact_id = None
            if hasattr(self.parent(), 'contact'):
                contact_id = self.parent().contact.id
            elif hasattr(self.controller, 'current_user_id'):
                # Récupérer le contact associé à l'utilisateur courant
                try:
                    current_user = self.controller.users.get_by_id(self.controller.current_user_id)
                    if current_user and hasattr(current_user, 'contact_id'):
                        contact_id = current_user.contact_id
                except Exception as e:
                    print(f"Erreur récupération utilisateur: {e}")
            
            # Charger les flottes
            fleets = []
            if contact_id:
                try:
                    fleets = self.controller.fleets.get_fleets_by_owner(contact_id)
                except AttributeError:
                    # Si la méthode n'existe pas, essayer d'autres méthodes
                    try:
                        fleets = self.controller.fleets.get_all_fleets()
                    except:
                        pass
            
            # Si pas de flottes trouvées, essayer de charger toutes les flottes
            if not fleets:
                try:
                    fleets = self.controller.fleets.get_all_fleets()
                except:
                    pass
            
            if fleets:
                for fleet in fleets:
                    # Récupérer le nom de la flotte
                    if hasattr(fleet, 'nom_flotte'):
                        name = fleet.nom_flotte
                    elif hasattr(fleet, 'nom'):
                        name = fleet.nom
                    elif hasattr(fleet, 'name'):
                        name = fleet.name
                    else:
                        name = f"Flotte {fleet.id if hasattr(fleet, 'id') else ''}"
                    
                    # Compter les véhicules
                    vehicle_count = 0
                    if hasattr(fleet, 'vehicles'):
                        vehicle_count = len(fleet.vehicles)
                    elif hasattr(fleet, 'vehicle_count'):
                        vehicle_count = fleet.vehicle_count
                    
                    # Récupérer l'ID
                    fleet_id = fleet.id if hasattr(fleet, 'id') else None
                    
                    if fleet_id:
                        display_name = f"{name} ({vehicle_count} véhicules)" if vehicle_count > 0 else name
                        self.existing_fleet_combo.addItem(display_name, fleet_id)
                
                # Sélectionner le premier élément si disponible
                if self.existing_fleet_combo.count() > 1:
                    self.existing_fleet_combo.setCurrentIndex(1)
                    self.on_existing_fleet_selected(1)
            else:
                self.existing_fleet_combo.addItem("Aucune flotte disponible", None)
                
        except Exception as e:
            print(f"Erreur chargement flottes: {e}")
            traceback.print_exc()
            self.existing_fleet_combo.clear()
            self.existing_fleet_combo.addItem("Erreur de chargement", None)

    def on_existing_fleet_selected(self, index):
        """Charge les véhicules de la flotte sélectionnée"""
        fleet_id = self.existing_fleet_combo.currentData()
        if not fleet_id:
            return
        
        try:
            self.status_icon.setText("🔄")
            self.status_text.setText("Chargement des véhicules de la flotte...")
            
            # Récupérer les véhicules de la flotte
            vehicles = []
            try:
                vehicles = self.controller.vehicles.get_vehicles_by_fleet(fleet_id)
            except AttributeError:
                # Essayer d'autres méthodes
                try:
                    vehicles = self.controller.fleets.get_fleet_vehicles(fleet_id)
                except:
                    pass
            
            if not vehicles:
                self.status_text.setText("Aucun véhicule dans cette flotte")
                self.status_icon.setText("📭")
                self.vehicles_data = []
                self.vehicles_table.setRowCount(0)
                self.calc_btn.setEnabled(False)
                self.import_btn.setEnabled(False)
                return
            
            # Transformer les données des véhicules
            self.vehicles_data = []
            for idx, vehicle in enumerate(vehicles):
                # Si c'est un objet SQLAlchemy, le convertir en dict
                if hasattr(vehicle, '__dict__') and not isinstance(vehicle, dict):
                    vehicle_dict = {
                        'id': getattr(vehicle, 'id', idx + 1),
                        'immatriculation': getattr(vehicle, 'immatriculation', ''),
                        'chassis': getattr(vehicle, 'chassis', ''),
                        'marque': getattr(vehicle, 'marque', ''),
                        'modele': getattr(vehicle, 'modele', ''),
                        'categorie': getattr(vehicle, 'categorie', 'VP'),
                        'genre': getattr(vehicle, 'genre', 'VP'),
                        'annee': getattr(vehicle, 'annee', None),
                        'energie': getattr(vehicle, 'energie', 'SEE'),
                        'puissance': getattr(vehicle, 'usage', 0) or getattr(vehicle, 'puissance', 0),
                        'places': getattr(vehicle, 'places', 5),
                        'valeur_neuf': getattr(vehicle, 'valeur_neuf', 0),
                        'valeur_venale': getattr(vehicle, 'valeur_venale', 0),
                        'zone': getattr(vehicle, 'zone', 'A'),
                        'date_debut': getattr(vehicle, 'date_debut', None),
                        'date_fin': getattr(vehicle, 'date_fin', None),
                        'nbr_jour': getattr(vehicle, 'nbr_jour', 365),
                        'statut': getattr(vehicle, 'statut', 'En Circulation'),
                        'prime_brute': getattr(vehicle, 'prime_brute', 0),
                        'prime_nette': getattr(vehicle, 'prime_nette', 0),
                        'reductions': getattr(vehicle, 'reductions', 0),
                        'droit_timbre': getattr(vehicle, 'droit_timbre', 0),
                        'accessoires': getattr(vehicle, 'accessoires', 0),
                        'asac': getattr(vehicle, 'asac', 0),
                        'carte_rose': getattr(vehicle, 'carte_rose', 0),
                        'vignette': getattr(vehicle, 'vignette', 0),
                        'tva': getattr(vehicle, 'tva', 0),
                        'pttc': getattr(vehicle, 'pttc', 0),
                        'marque_type': f"{getattr(vehicle, 'marque', '')} {getattr(vehicle, 'modele', '')}".strip(),
                        'usage': getattr(vehicle, 'usage', ''),
                        'pmec': getattr(vehicle, 'pmec', 0),
                        'capital_ar': getattr(vehicle, 'capital_ar', 0),
                        'status': 'loaded',
                        'from_fleet': True
                    }
                    
                    # Charger les garanties
                    garanties = {}
                    guarantee_keys = ['rc', 'dr', 'vol', 'vb', 'incendie', 'bris_glace', 'ar', 'dta', 'ipt']
                    for key in guarantee_keys:
                        # Essayer de récupérer depuis l'objet
                        if hasattr(vehicle, key):
                            garanties[key] = getattr(vehicle, key, 0)
                        elif hasattr(vehicle, 'guarantees') and vehicle.guarantees:
                            garanties[key] = getattr(vehicle.guarantees, key, 0)
                        else:
                            garanties[key] = 0
                    
                    garanties['total'] = sum(garanties.get(k, 0) for k in guarantee_keys)
                    vehicle_dict['garanties'] = garanties
                    
                else:
                    # Si c'est déjà un dict
                    vehicle_dict = vehicle.copy() if isinstance(vehicle, dict) else {'immatriculation': str(vehicle)}
                    if 'garanties' not in vehicle_dict:
                        vehicle_dict['garanties'] = {}
                    vehicle_dict['from_fleet'] = True
                    if 'id' not in vehicle_dict:
                        vehicle_dict['id'] = idx + 1
                
                self.vehicles_data.append(vehicle_dict)
            
            # Afficher les véhicules
            self.display_vehicles()
            
            self.file_info.setText(f"✅ {len(self.vehicles_data)} véhicules chargés depuis la flotte")
            self.status_text.setText(f"{len(self.vehicles_data)} véhicules chargés")
            self.status_icon.setText("✅")
            
            self.calc_btn.setEnabled(False)
            self.calc_btn.setText("Calcul déjà effectué")
            self.import_btn.setEnabled(True)
            self.refresh_btn.setEnabled(True)
            self.mass_reduction_btn.setEnabled(True)
            
        except Exception as e:
            self.status_text.setText(f"Erreur: {str(e)}")
            self.status_icon.setText("❌")
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les véhicules: {str(e)}")
            traceback.print_exc()

    def refresh_fleet_guarantees(self):
        """Rafraîchit les garanties de la flotte"""
        if not self.vehicles_data:
            QMessageBox.warning(self, "Erreur", "Aucun véhicule à rafraîchir")
            return
        
        # Vérifier que les données sont valides
        for vehicle in self.vehicles_data:
            if 'immatriculation' not in vehicle:
                QMessageBox.warning(self, "Erreur", "Données de véhicule invalides")
                return
        
        self.start_calculation()
    
    def apply_global_frais_to_selected(self):
        """Applique les frais aux véhicules sélectionnés"""
        selected_rows = []
        for row in range(self.vehicles_table.rowCount()):
            item = self.vehicles_table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                selected_rows.append(row)
        
        if not selected_rows:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner au moins un véhicule")
            return
        
        try:
            accessoires = float(self.global_accessoires.text().replace(" ", "").replace(",", "") or 0)
            asac = float(self.global_asac.text().replace(" ", "").replace(",", "") or 0)
            carte_rose = float(self.global_carte_rose.text().replace(" ", "").replace(",", "") or 0)
            vignette = float(self.global_vignette.text().replace(" ", "").replace(",", "") or 0)
            
            for row in selected_rows:
                vehicle = self.vehicles_data[row]
                vehicle['accessoires'] = accessoires
                vehicle['asac'] = asac
                vehicle['carte_rose'] = carte_rose
                vehicle['vignette'] = vignette
            
            self.update_summary()
            QMessageBox.information(self, "Succès", f"Frais appliqués à {len(selected_rows)} véhicule(s)")
            
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", f"Valeur invalide: {str(e)}")
    
    def edit_vehicle_garanties(self, vehicle_id):
        """Modifie les garanties d'un véhicule"""
        row = self.find_row_by_vehicle_id(vehicle_id)
        if row == -1:
            QMessageBox.warning(self, "Erreur", "Véhicule non trouvé")
            return
        
        vehicle = self.vehicles_data[row]
        garanties = vehicle.get('garanties', {})
        
        dialog = VehicleGarantieDialog(vehicle, garanties, self)
        if dialog.exec() == QDialog.Accepted:
            new_data = dialog.get_data()
            
            # Mettre à jour les garanties
            for key in ['rc', 'dr', 'vol', 'vb', 'incendie', 'bris_glace', 'ar', 'dta', 'ipt']:
                if key in new_data:
                    vehicle['garanties'][key] = new_data[key]
                    reduction_key = f'reduction_{key}'
                    if reduction_key in new_data:
                        vehicle['garanties'][reduction_key] = new_data[reduction_key]
            
            # Recalculer le total
            total_keys = ['rc', 'dr', 'vol', 'vb', 'incendie', 'bris_glace', 'ar', 'dta', 'ipt']
            vehicle['garanties']['total'] = sum(vehicle['garanties'].get(k, 0) for k in total_keys)
            
            # Mettre à jour les informations du véhicule
            for key in ['immatriculation', 'chassis', 'marque', 'modele', 'categorie', 'annee', 'energie', 'puissance', 'places', 'valeur_neuf', 'valeur_venale']:
                if key in new_data:
                    vehicle[key] = new_data[key]
            
            # Rafraîchir l'affichage
            self.update_vehicle_row(row, vehicle)
            self.update_summary()
            
            QMessageBox.information(self, "Succès", f"Véhicule {vehicle['immatriculation']} mis à jour")
    
    def edit_vehicle_dates(self, vehicle_id):
        """Modifie les dates d'un véhicule"""
        row = self.find_row_by_vehicle_id(vehicle_id)
        if row == -1:
            if isinstance(vehicle_id, int) and vehicle_id < len(self.vehicles_data):
                row = vehicle_id
            else:
                QMessageBox.warning(self, "Erreur", "Véhicule non trouvé")
                return
        
        vehicle = self.vehicles_data[row]
        
        dialog = VehicleDatesDialog(vehicle, self)
        if dialog.exec() == QDialog.Accepted:
            new_dates = dialog.get_dates()
            
            # Sauvegarder les montants annuels
            if 'garanties_annuelles' not in vehicle:
                vehicle['garanties_annuelles'] = vehicle.get('garanties', {}).copy()
            
            # Mettre à jour les dates
            vehicle['date_debut'] = new_dates['date_debut']
            vehicle['date_fin'] = new_dates['date_fin']
            vehicle['nbr_jour'] = new_dates['nbr_jour']
            vehicle['statut'] = new_dates['statut']
            
            # Recalculer les garanties au prorata
            prorata = new_dates['prorata']
            garanties_annuelles = vehicle['garanties_annuelles']
            new_garanties = {}
            for key, amount in garanties_annuelles.items():
                if key != 'total' and not key.startswith('reduction_'):
                    new_garanties[key] = amount * prorata
            
            new_garanties['total'] = sum(new_garanties.values())
            vehicle['garanties'] = new_garanties
            
            # Mettre à jour l'affichage
            self.update_vehicle_row(row, vehicle)
            self.update_summary()
            
            QMessageBox.information(self, "Succès", f"Dates mises à jour pour {vehicle['immatriculation']}")
    
    def on_modify_vehicle(self, vehicle_id):
        """Modifie complètement un véhicule"""
        row = self.find_row_by_vehicle_id(vehicle_id)
        if row == -1:
            if isinstance(vehicle_id, int) and vehicle_id < len(self.vehicles_data):
                row = vehicle_id
            else:
                QMessageBox.warning(self, "Erreur", "Véhicule non trouvé")
                return
        
        vehicle = self.vehicles_data[row]
        garanties = vehicle.get('garanties', {})
        
        dialog = VehicleGarantieDialog(vehicle, garanties, self)
        if dialog.exec() == QDialog.Accepted:
            new_data = dialog.get_data()
            
            # Mettre à jour toutes les données
            for key in ['rc', 'dr', 'vol', 'vb', 'incendie', 'bris_glace', 'ar', 'dta', 'ipt']:
                if key in new_data:
                    vehicle['garanties'][key] = new_data[key]
                    reduction_key = f'reduction_{key}'
                    if reduction_key in new_data:
                        vehicle['garanties'][reduction_key] = new_data[reduction_key]
            
            # Recalculer le total
            total_keys = ['rc', 'dr', 'vol', 'vb', 'incendie', 'bris_glace', 'ar', 'dta', 'ipt']
            vehicle['garanties']['total'] = sum(vehicle['garanties'].get(k, 0) for k in total_keys)
            
            # Mettre à jour les informations
            for key in ['immatriculation', 'chassis', 'marque', 'modele', 'categorie', 'annee', 'energie', 'puissance', 'places', 'valeur_neuf', 'valeur_venale']:
                if key in new_data:
                    vehicle[key] = new_data[key]
            
            # Rafraîchir l'affichage
            self.update_vehicle_row(row, vehicle)
            self.update_summary()
            
            QMessageBox.information(self, "Succès", f"Véhicule {vehicle['immatriculation']} mis à jour")
    
    def find_row_by_vehicle_id(self, vehicle_id):
        """Trouve l'index de la ligne à partir de l'ID du véhicule"""
        for i, vehicle in enumerate(self.vehicles_data):
            if vehicle.get('id') == vehicle_id:
                return i
            # Fallback par immatriculation
            if vehicle.get('immatriculation') == str(vehicle_id):
                return i
        return -1
    
    # def update_vehicle_row(self, row, vehicle):
    #     """Met à jour l'affichage d'une ligne du tableau"""
    #     if row >= self.vehicles_table.rowCount():
    #         return
        
    #     # Mettre à jour les colonnes de base
    #     self.vehicles_table.setItem(row, 1, QTableWidgetItem(str(vehicle.get('rang', row + 1))))
    #     self.vehicles_table.setItem(row, 2, QTableWidgetItem(vehicle.get('immatriculation', '')))
    #     self.vehicles_table.setItem(row, 3, QTableWidgetItem(vehicle.get('marque_type', vehicle.get('marque', ''))))
    #     self.vehicles_table.setItem(row, 4, QTableWidgetItem(vehicle.get('genre', 'VP')))
        
    #     puissance_item = QTableWidgetItem(str(vehicle.get('puissance', 0)))
    #     puissance_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #     self.vehicles_table.setItem(row, 5, puissance_item)
        
    #     self.vehicles_table.setItem(row, 6, QTableWidgetItem(vehicle.get('usage', '')))
        
    #     places_item = QTableWidgetItem(str(vehicle.get('places', 5)))
    #     places_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #     self.vehicles_table.setItem(row, 7, places_item)
        
    #     jours_item = QTableWidgetItem(str(vehicle.get('nbr_jour', 365)))
    #     jours_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #     self.vehicles_table.setItem(row, 8, jours_item)
        
    #     # Valeurs
    #     pmec_item = QTableWidgetItem(f"{vehicle.get('pmec', 0):,.0f}".replace(",", " "))
    #     pmec_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #     self.vehicles_table.setItem(row, 9, pmec_item)
        
    #     vn_item = QTableWidgetItem(f"{vehicle.get('valeur_neuf', 0):,.0f}".replace(",", " "))
    #     vn_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #     self.vehicles_table.setItem(row, 10, vn_item)
        
    #     vv_item = QTableWidgetItem(f"{vehicle.get('valeur_venale', 0):,.0f}".replace(",", " "))
    #     vv_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #     self.vehicles_table.setItem(row, 11, vv_item)
        
    #     capital_item = QTableWidgetItem(f"{vehicle.get('capital_ar', 0):,.0f}".replace(",", " "))
    #     capital_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #     self.vehicles_table.setItem(row, 12, capital_item)
        
    #     # Garanties
    #     garanties = vehicle.get('garanties', {})
    #     garanties_cols = {
    #         'rc': 13, 'dr': 14, 'vol': 15, 'vb': 16,
    #         'incendie': 17, 'bris_glace': 18, 'ar': 19,
    #         'dta': 20, 'ipt': 21
    #     }
        
    #     for key, col in garanties_cols.items():
    #         amount = garanties.get(key, 0)
    #         item = QTableWidgetItem(f"{amount:,.0f}".replace(",", " "))
    #         item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #         self.vehicles_table.setItem(row, col, item)
        
    #     # Primes
    #     prime_brute = garanties.get('total', 0)
    #     pb_item = QTableWidgetItem(f"{prime_brute:,.0f}".replace(",", " "))
    #     pb_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #     self.vehicles_table.setItem(row, 22, pb_item)
        
    #     reductions_item = QTableWidgetItem(str(vehicle.get('reductions', 0)))
    #     reductions_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #     self.vehicles_table.setItem(row, 23, reductions_item)
        
    #     prime_nette = vehicle.get('prime_nette', prime_brute)
    #     pn_item = QTableWidgetItem(f"{prime_nette:,.0f}".replace(",", " "))
    #     pn_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #     self.vehicles_table.setItem(row, 24, pn_item)
        
    #     timbre_item = QTableWidgetItem(f"{vehicle.get('droit_timbre', 0):,.0f}".replace(",", " "))
    #     timbre_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    #     self.vehicles_table.setItem(row, 25, timbre_item)

    def update_vehicle_row(self, row, vehicle):
        """Met à jour l'affichage d'une ligne du tableau"""
        if row >= self.vehicles_table.rowCount():
            return
        
        # Mettre à jour les colonnes de base
        self.vehicles_table.setItem(row, 1, QTableWidgetItem(str(vehicle.get('rang', row + 1))))
        self.vehicles_table.setItem(row, 2, QTableWidgetItem(vehicle.get('immatriculation', '')))
        self.vehicles_table.setItem(row, 3, QTableWidgetItem(vehicle.get('marque_type', vehicle.get('marque', ''))))
        self.vehicles_table.setItem(row, 4, QTableWidgetItem(vehicle.get('genre', 'VP')))
        
        puissance_item = QTableWidgetItem(str(vehicle.get('puissance', 0)))
        puissance_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 5, puissance_item)
        
        # ✅ AJOUT DE LA COLONNE ÉNERGIE
        energie = vehicle.get('energie', 'Essence')
        energie_item = QTableWidgetItem(energie)
        energie_item.setTextAlignment(Qt.AlignCenter)
        self.vehicles_table.setItem(row, 6, energie_item)
        
        self.vehicles_table.setItem(row, 7, QTableWidgetItem(vehicle.get('usage', '')))
        
        places_item = QTableWidgetItem(str(vehicle.get('places', 5)))
        places_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 8, places_item)
        
        jours_item = QTableWidgetItem(str(vehicle.get('nbr_jour', 365)))
        jours_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 9, jours_item)
        
        # Valeurs
        pmec_value = vehicle.get('pmec', '')
        pmec_item = QTableWidgetItem(str(pmec_value) if pmec_value else '')
        pmec_item.setTextAlignment(Qt.AlignCenter)
        self.vehicles_table.setItem(row, 10, pmec_item)
        
        vn_item = QTableWidgetItem(f"{vehicle.get('valeur_neuf', 0):,.0f}".replace(",", " "))
        vn_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 11, vn_item)
        
        vv_item = QTableWidgetItem(f"{vehicle.get('valeur_venale', 0):,.0f}".replace(",", " "))
        vv_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 12, vv_item)
        
        capital_item = QTableWidgetItem(f"{vehicle.get('capital_ar', 0):,.0f}".replace(",", " "))
        capital_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 13, capital_item)
        
        # Garanties
        garanties = vehicle.get('garanties', {})
        garanties_cols = {
            'rc': 14, 'dr': 15, 'vol': 16, 'vb': 17,
            'incendie': 18, 'bris_glace': 19, 'ar': 20,
            'dta': 21, 'ipt': 22
        }
        
        for key, col in garanties_cols.items():
            amount = garanties.get(key, 0)
            item = QTableWidgetItem(f"{amount:,.0f}".replace(",", " "))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.vehicles_table.setItem(row, col, item)
        
        # Primes
        prime_brute = garanties.get('total', 0)
        pb_item = QTableWidgetItem(f"{prime_brute:,.0f}".replace(",", " "))
        pb_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 23, pb_item)
        
        reductions_item = QTableWidgetItem(str(vehicle.get('reductions', 0)))
        reductions_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 24, reductions_item)
        
        prime_nette = vehicle.get('prime_nette', prime_brute)
        pn_item = QTableWidgetItem(f"{prime_nette:,.0f}".replace(",", " "))
        pn_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 25, pn_item)
        
        timbre_item = QTableWidgetItem(f"{vehicle.get('droit_timbre', 0):,.0f}".replace(",", " "))
        timbre_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 26, timbre_item)

    def import_fleet(self):
        """Importe la flotte dans la base de données"""
        # Récupérer les véhicules sélectionnés
        selected = []
        for row in range(self.vehicles_table.rowCount()):
            item = self.vehicles_table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                if row < len(self.vehicles_data):
                    selected.append(self.vehicles_data[row])
        
        if not selected:
            QMessageBox.warning(self, "Erreur", "Aucun véhicule sélectionné")
            return
        
        # ✅ VÉRIFIER QU'UNE COMPAGNIE EST SÉLECTIONNÉE
        # Récupérer l'ID de la compagnie depuis la combo box
        compagny_id = self.compagny_combo.currentData() if hasattr(self, 'compagny_combo') else None
        
        # Si la combo box n'existe pas ou n'est pas dans l'UI, on la crée
        if not hasattr(self, 'compagny_combo'):
            # Demander à l'utilisateur de sélectionner une compagnie
            compagny_id = self._ask_for_compagny()
            if not compagny_id:
                return
        elif not compagny_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une compagnie d'assurance")
            return
        
        try:
            # Récupérer l'ID du propriétaire
            owner_id = None
            if hasattr(self.parent(), 'contact'):
                owner_id = self.parent().contact.id
            
            if hasattr(self.controller, 'current_user_id'):
                current_user_id = self.controller.current_user_id
            else:
                current_user_id = 1
            
            # Créer ou récupérer la flotte
            fleet_id = None
            
            if self.mode_new.isChecked():
                fleet_name = self.fleet_name.text().strip()
                if not fleet_name:
                    QMessageBox.warning(self, "Erreur", "Veuillez entrer un nom de flotte")
                    return
                
                fleet_data = {
                    'nom_flotte': fleet_name,
                    'code_flotte': self.fleet_code.text().strip(),
                    'owner_id': owner_id,
                    'statut': 'Actif',
                    'assureur': compagny_id,  # ✅ Utiliser l'ID de la compagnie
                    'date_debut': self.date_debut.date().toPython(),
                    'date_fin': self.date_fin.date().toPython(),
                }
                
                success, result = self.controller.fleets.create_fleet(fleet_data, current_user_id)
                if not success:
                    QMessageBox.critical(self, "Erreur", f"Erreur création flotte: {result}")
                    return
                fleet_id = result.id if hasattr(result, 'id') else result
            else:
                fleet_id = self.existing_fleet_combo.currentData()
                if not fleet_id:
                    QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une flotte")
                    return
            
            # ✅ IMPORTER LES VÉHICULES
            imported = 0
            errors = []
            
            for vehicle in selected:
                try:
                    # Préparer les données du véhicule
                    garanties = vehicle.get('garanties', {})
                    
                    chassis_value = vehicle.get('chassis', '')
                    if not chassis_value or chassis_value == '':
                        chassis_value = f"CH-{vehicle['immatriculation']}"
                    
                    # Dates
                    if vehicle.get('date_debut'):
                        debut = vehicle['date_debut']
                        if isinstance(debut, datetime):
                            debut = debut.date()
                    else:
                        debut = self.date_debut.date().toPython()
                    
                    if vehicle.get('date_fin'):
                        fin = vehicle['date_fin']
                        if isinstance(fin, datetime):
                            fin = fin.date()
                    else:
                        fin = self.date_fin.date().toPython()
                    
                    jours = max(1, (fin - debut).days) if fin and debut else 365
                    
                    # Catégorie
                    categorie_value = vehicle.get('categorie', 'VP')
                    if not categorie_value:
                        categorie_value = 'VP'
                    
                    # Calcul TVA
                    tva_rate = 0.1925
                    total_garanties = garanties.get('total', 0)
                    tva_amount = total_garanties * tva_rate
                    
                    # Récupérer les frais
                    accessoires = vehicle.get('accessoires', 0)
                    asac = vehicle.get('asac', 0)
                    carte_rose = vehicle.get('carte_rose', 0)
                    vignette = vehicle.get('vignette', 0)
                    
                    # ✅ PRÉPARER LES DONNÉES DU VÉHICULE
                    vehicle_data = build_vehicle_import_payload(
                        vehicle=vehicle,
                        owner_id=owner_id,
                        compagny_id=compagny_id,
                        fleet_id=fleet_id,
                        current_user_id=current_user_id,
                        debut=debut,
                        fin=fin,
                        jours=jours,
                        total_garanties=total_garanties,
                        tva_amount=tva_amount,
                        accessoires=accessoires,
                        asac=asac,
                        carte_rose=carte_rose,
                        vignette=vignette,
                    )
                    
                    # ✅ APPEL AU CONTROLLER
                    result = self.controller.vehicles.create_vehicle(vehicle_data, current_user_id)
                    
                    if isinstance(result, tuple):
                        if len(result) == 2:
                            success, message = result
                        elif len(result) == 3:
                            success, _, message = result
                        else:
                            success = False
                            message = "Format de retour inattendu"
                    else:
                        success = bool(result)
                        message = "Succès" if success else "Erreur"
                    
                    if success:
                        imported += 1
                        print(f"✅ Véhicule {vehicle['immatriculation']} importé avec succès")
                    else:
                        errors.append(f"{vehicle['immatriculation']}: {message}")
                        
                except Exception as e:
                    errors.append(f"{vehicle['immatriculation']}: {str(e)}")
                    traceback.print_exc()
            
            # ✅ AFFICHER LE RÉSULTAT
            if imported > 0:
                msg = f"✅ {imported} véhicule(s) importés avec succès"
                if errors:
                    msg += f"\n\n⚠️ {len(errors)} erreur(s):\n" + "\n".join(errors[:5])
                QMessageBox.information(self, "Importation terminée", msg)
                
                # ✅ Émettre le signal pour rafraîchir la vue parente
                self.data_changed.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "Erreur", "\n".join(errors[:5]))
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
            traceback.print_exc()

    def _ask_for_compagny(self):
        """Demande à l'utilisateur de sélectionner une compagnie"""
        from PySide6.QtWidgets import QInputDialog, QComboBox, QDialogButtonBox, QVBoxLayout
        
        # Créer un dialogue simple
        dialog = QDialog(self)
        dialog.setWindowTitle("Sélectionner une compagnie")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Veuillez sélectionner une compagnie d'assurance :"))
        
        combo = QComboBox()
        # Charger les compagnies
        try:
            if hasattr(self.controller, 'compagnies'):
                compagnies = self.controller.compagnies.get_all_active_compagnies()
                for cie in compagnies:
                    if hasattr(cie, 'nom'):
                        combo.addItem(cie.nom, cie.id)
                    elif isinstance(cie, dict):
                        combo.addItem(cie.get('nom', ''), cie.get('id'))
        except Exception as e:
            print(f"Erreur chargement compagnies: {e}")
        
        layout.addWidget(combo)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            return combo.currentData()
        return None
    
    def _load_compagnies(self):
        """Charge les compagnies (simplifié)"""
        pass

    def create_compagny_section(self):
        """Section de sélection de la compagnie"""
        group = QGroupBox("🏢 2.5. Compagnie d'assurance")
        layout = QVBoxLayout(group)
        
        self.compagny_combo = QComboBox()
        self.compagny_combo.addItem("Sélectionner une compagnie", None)
        
        # Charger les compagnies
        try:
            if hasattr(self.controller, 'compagnies'):
                compagnies = self.controller.compagnies.get_all()
                for cie in compagnies:
                    if hasattr(cie, 'nom'):
                        self.compagny_combo.addItem(cie.nom, cie.id)
                    elif isinstance(cie, dict):
                        self.compagny_combo.addItem(cie.get('nom', ''), cie.get('id'))
        except Exception as e:
            print(f"Erreur chargement compagnies: {e}")
        
        layout.addWidget(self.compagny_combo)
        
        # Label d'information
        info = QLabel("⚠️ La compagnie est obligatoire pour l'importation")
        info.setStyleSheet("color: #ef4444; font-size: 11px;")
        layout.addWidget(info)
        
        return group
    
# ============================================================================
# FONCTION PRINCIPALE D'EXPORT
# ============================================================================

def create_fleet_import_dialog(controller, parent=None):
    """Crée et retourne le dialogue d'importation de flotte"""
    return FleetImportAdvancedDialog(controller, parent)