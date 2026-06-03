# fleet_import_dialog.py - Version améliorée avec design moderne et scrollable

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QProgressBar,
    QMessageBox, QFrame, QComboBox, QRadioButton, QButtonGroup,
    QScrollArea, QSplitter, QTextEdit, QCheckBox, QHeaderView,
    QWidget, QApplication, QLineEdit, QDateEdit, QGridLayout,
    QGroupBox, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QThread, QDate
from PySide6.QtGui import QFont, QColor, QPalette
import pandas as pd
import traceback
from datetime import datetime


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
    QTableWidget {{
        border: 1px solid {AppColors.BORDER};
        border-radius: 10px;
        background: {AppColors.WHITE};
        alternate-background-color: {AppColors.GRAY_LIGHT};
    }}
    QHeaderView::section {{
        background: {AppColors.GRAY_LIGHT};
        padding: 10px;
        font-weight: 600;
        font-size: 11px;
        color: {AppColors.GRAY};
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
"""


# ============================================================================
# COMPOSANTS
# ============================================================================

class GarantieCard(QFrame):
    """Carte pour une garantie avec checkbox et montants"""
    garantie_changed = Signal(str, bool, float)
    
    def __init__(self, key, label, icon, parent=None):
        super().__init__(parent)
        self.key = key
        self.label = label
        self.setStyleSheet(f"""
            QFrame {{
                background: {AppColors.WHITE};
                border: 1px solid {AppColors.BORDER};
                border-radius: 10px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # Checkbox
        self.checkbox = QCheckBox(f"{icon} {label}")
        self.checkbox.setStyleSheet("font-weight: 600;")
        self.checkbox.toggled.connect(self.on_toggle)
        layout.addWidget(self.checkbox, 2)
        
        # Montant
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Montant (FCFA)")
        self.amount_input.setEnabled(False)
        self.amount_input.textChanged.connect(self.on_amount_changed)
        layout.addWidget(self.amount_input, 1)
        
        # Taux de réduction
        self.reduction_input = QLineEdit()
        self.reduction_input.setPlaceholderText("Réduction %")
        self.reduction_input.setEnabled(False)
        self.reduction_input.setFixedWidth(100)
        self.reduction_input.textChanged.connect(self.on_reduction_changed)
        layout.addWidget(self.reduction_input)
        
        # Montant net
        self.net_label = QLabel("0 FCFA")
        self.net_label.setStyleSheet(f"""
            color: {AppColors.SUCCESS};
            font-weight: bold;
            background: {AppColors.SUCCESS_LIGHT};
            padding: 6px 12px;
            border-radius: 6px;
        """)
        self.net_label.setFixedWidth(120)
        layout.addWidget(self.net_label)
        
        self.current_amount = 0.0
        self.current_reduction = 0.0
    
    def on_toggle(self, checked):
        self.amount_input.setEnabled(checked)
        self.reduction_input.setEnabled(checked)
        if not checked:
            self.amount_input.clear()
            self.reduction_input.clear()
            self.net_label.setText("0 FCFA")
            self.current_amount = 0
            self.current_reduction = 0
        self.garantie_changed.emit(self.key, checked, self.get_net_amount())
    
    def on_amount_changed(self):
        if self.checkbox.isChecked():
            text = self.amount_input.text().replace(" ", "").replace(",", "")
            try:
                self.current_amount = float(text) if text else 0
                self.update_net()
            except:
                pass
    
    def on_reduction_changed(self):
        if self.checkbox.isChecked():
            text = self.reduction_input.text().replace("%", "").strip()
            try:
                self.current_reduction = float(text) if text else 0
                self.update_net()
            except:
                pass
    
    def update_net(self):
        reduction_amount = self.current_amount * (self.current_reduction / 100)
        net_amount = self.current_amount - reduction_amount
        self.net_label.setText(f"{net_amount:,.0f} FCFA".replace(",", " "))
        self.garantie_changed.emit(self.key, self.checkbox.isChecked(), net_amount)
    
    def get_net_amount(self):
        if not self.checkbox.isChecked():
            return 0
        reduction_amount = self.current_amount * (self.current_reduction / 100)
        return self.current_amount - reduction_amount
    
    def set_values(self, amount, reduction=0):
        self.current_amount = amount
        self.current_reduction = reduction
        if amount > 0:
            self.checkbox.setChecked(True)
            self.amount_input.setText(f"{amount:,.0f}".replace(",", " "))
            if reduction > 0:
                self.reduction_input.setText(str(reduction))
            self.update_net()
        else:
            self.checkbox.setChecked(False)


class VehicleGarantieDialog(QDialog):
    """Dialogue de personnalisation des garanties pour un véhicule"""
    
    def __init__(self, vehicle, garanties, parent=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.garanties = garanties
        self.setWindowTitle(f"Garanties - {vehicle.get('immatriculation', 'Véhicule')}")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        self.setup_ui()
        self.load_garanties()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # En-tête
        header = QFrame()
        header.setStyleSheet(f"""
            background: {AppColors.PRIMARY_LIGHT};
            border-radius: 10px;
        """)
        header_layout = QHBoxLayout(header)
        
        info = QLabel(f"🚗 {self.vehicle.get('immatriculation')} - {self.vehicle.get('marque')} {self.vehicle.get('modele')}")
        info.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {AppColors.PRIMARY_DARK};")
        
        header_layout.addWidget(info)
        header_layout.addStretch()
        layout.addWidget(header)
        
        # Zone scrollable pour les garanties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(12)
        
        # Créer les cartes de garanties
        self.garantie_cards = {}
        garanties_list = [
            ('rc', 'Responsabilité Civile', '🛡️'),
            ('dr', 'Défense Recours', '⚖️'),
            ('vol', 'Vol', '🚗'),
            ('vb', 'Vol à main armée', '🔫'),
            ('incendie', 'Incendie', '🔥'),
            ('bris_glace', 'Bris de glace', '🪟'),
            ('ar', 'Assistance Réparation', '🔧'),
            ('dta', 'Dommages Tous Accidents', '💥'),
            ('ipt', 'Individuelle Personnes Transportées', '👥'),
        ]
        
        for key, label, icon in garanties_list:
            card = GarantieCard(key, label, icon)
            scroll_layout.addWidget(card)
            self.garantie_cards[key] = card
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Total
        total_frame = QFrame()
        total_frame.setStyleSheet(f"""
            background: {AppColors.SUCCESS_LIGHT};
            border-radius: 10px;
        """)
        total_layout = QHBoxLayout(total_frame)
        total_layout.addWidget(QLabel("<b>💰 TOTAL GÉNÉRAL :</b>"))
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
    
    def load_garanties(self):
        for key, card in self.garantie_cards.items():
            amount = self.garanties.get(key, 0)
            reduction = self.garanties.get(f'reduction_{key}', 0)
            card.set_values(amount, reduction)
            card.garantie_changed.connect(self.on_garantie_changed)
    
    def on_garantie_changed(self, key, checked, net_amount):
        self.update_total()
    
    def update_total(self):
        total = sum(card.get_net_amount() for card in self.garantie_cards.values())
        self.total_label.setText(f"{total:,.0f} FCFA".replace(",", " "))
    
    def get_garanties(self):
        result = {}
        for key, card in self.garantie_cards.items():
            result[key] = card.get_net_amount()
            # Stocker aussi le montant brut et la réduction si besoin
            result[f'brut_{key}'] = card.current_amount
            result[f'reduction_{key}'] = card.current_reduction
        result['total'] = sum(v for k, v in result.items() if not k.startswith(('brut_', 'reduction_', 'total')))
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

    # Supprimer cette méthode qui cause l'erreur
    # def calculate_rc_brut(self):
    #     ...
    
    def calculate_garanties(self, vehicle):
        """Calcule les garanties pour un véhicule"""
        garanties = {}
        
        cie_id = self.params.get('compagny_id')
        zone = self.params.get('zone', 'A')
        code_tarif = self.params.get('code_tarif', '')
        avec_remorque = self.params.get('avec_remorque', False)
        
        v_neuf = vehicle.get('valeur_neuf', 0)
        v_venale = vehicle.get('valeur_venale', 0)
        places = vehicle.get('places', 5)
        puissance = vehicle.get('puissance', 0)
        energie = vehicle.get('energie', 'Essence')
        categorie = vehicle.get('categorie', 'VP')
        
        jours = self.params.get('duree_jours', 365)
        prorata = jours / 365.0
        
        # RC - Appel direct à la méthode du contrôleur
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
            rc = res.get('rc', 0) if isinstance(res, dict) else (res or 0)
        except Exception as e:
            print(f"Erreur calcul RC: {e}")
            rc = 0
        
        garanties['rc'] = rc * prorata
        garanties['dr'] = garanties['rc'] * 0.03
        garanties['vol'] = v_venale * 0.02 * prorata
        garanties['vb'] = v_venale * 0.02 * prorata
        garanties['incendie'] = v_venale * 0.025 * prorata
        garanties['bris_glace'] = v_neuf * 0.005 * prorata
        garanties['ar'] = v_venale * 0.75 * 0.03 * prorata
        garanties['dta'] = v_neuf * 0.05 * prorata
        
        if places <= 5:
            garanties['ipt'] = 7500 * prorata
        else:
            garanties['ipt'] = (7500 * places / 5) * prorata
        
        garanties['total'] = sum(garanties.values())
        
        return garanties

# ============================================================================
# DIALOGUE PRINCIPAL
# ============================================================================

class FleetImportAdvancedDialog(QDialog):
    """Dialogue d'importation de flotte"""
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Importation de flotte")
        self.setMinimumSize(1400, 900)
        self.resize(1500, 950)
        
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
        
        main_splitter.setSizes([450, 950])
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
        layout.setSpacing(20)
        
        # 1. Fichier
        layout.addWidget(self.create_file_section())
        
        # 2. Flotte
        layout.addWidget(self.create_fleet_section())
        
        # 3. Assurance
        layout.addWidget(self.create_insurance_section())
        
        # 4. Garanties globales
        layout.addWidget(self.create_global_garanties_section())
        
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
        drop_zone.setFixedHeight(100)
        drop_zone.mousePressEvent = lambda e: self.select_file()
        
        drop_layout = QVBoxLayout(drop_zone)
        drop_layout.setAlignment(Qt.AlignCenter)
        
        self.file_icon = QLabel("📂")
        self.file_icon.setStyleSheet("font-size: 24px;")
        self.file_label = QLabel("Cliquez pour sélectionner un fichier Excel ou CSV")
        self.file_label.setStyleSheet(f"color: {AppColors.GRAY}; font-size: 12px;")
        self.file_info = QLabel("")
        self.file_info.setStyleSheet(f"color: {AppColors.PRIMARY}; font-size: 11px;")
        
        drop_layout.addWidget(self.file_icon)
        drop_layout.addWidget(self.file_label)
        drop_layout.addWidget(self.file_info)
        
        layout.addWidget(drop_zone)
        
        # Lien template
        template_btn = QPushButton("📥 Télécharger le modèle Excel")
        template_btn.setFlat(True)
        template_btn.setCursor(Qt.PointingHandCursor)
        template_btn.setStyleSheet(f"color: {AppColors.PRIMARY}; text-align: left;")
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
        new_layout.setSpacing(10)
        
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
   
    def load_tarif_categories_by_code_async(self, code):
        """Charge les catégories associées à un code tarif de manière asynchrone"""
        compagny_id = self.compagny_combo.currentData()
        if not compagny_id or not code:
            return
        
        from core.widgets.global_loader import get_global_loader
        from core.workers.database_worker import async_query
        
        loader = get_global_loader()
        loader.show_loading("Chargement des catégories...")
        
        def fetch():
            return self.controller.vehicles.get_tarif_categories_by_compagnie_and_code(
                compagny_id, code
            )
        
        async_query.execute(
            fetch,
            on_finished=self._on_tarif_categories_loaded,
            on_error=self._on_tarif_categories_error
        )

    def on_code_tarif_changed(self, code):
        """Lorsque le code tarif change, charge les catégories associées"""
        compagny_id = self.compagny_combo.currentData()
        if code and compagny_id:
            # Charger les catégories liées à ce code tarif
            self.load_tarif_categories_by_code_async(code)

    def _on_tarif_categories_loaded(self, categories):
        """Callback quand les catégories sont chargées"""
        from core.widgets.global_loader import get_global_loader
        get_global_loader().hide_loading()
        
        self.categorie_combo.clear()
        self.categorie_combo.addItem("", "")
        
        if categories:
            unique_categories = sorted({str(c).strip() for c in categories if c})
            for categorie in unique_categories:
                self.categorie_combo.addItem(categorie)

    def _on_tarif_categories_error(self, error):
        """Callback en cas d'erreur de chargement"""
        from core.widgets.global_loader import get_global_loader
        get_global_loader().hide_loading()
        print(f"Erreur chargement catégories: {error}")

    def create_insurance_section(self):
        """Section des paramètres d'assurance"""
        group = QGroupBox("🛡️ 3. Paramètres d'assurance")
        layout = QGridLayout(group)
        layout.setSpacing(12)
        
        # Compagnie
        layout.addWidget(QLabel("Compagnie :"), 0, 0)
        self.compagny_combo = QComboBox()
        self.compagny_combo.currentIndexChanged.connect(self.on_compagny_changed)
        layout.addWidget(self.compagny_combo, 0, 1)
        
        # Zone
        layout.addWidget(QLabel("Zone :"), 1, 0)
        self.zone_combo = QComboBox()
        self.zone_combo.addItems(["A", "B", "C"])
        layout.addWidget(self.zone_combo, 1, 1)
        
        # Catégorie (comme dans automobile_form_view)
        layout.addWidget(QLabel("Catégorie :"), 2, 0)
        self.categorie_combo = QComboBox()  # ← Garder categorie_combo
        self.categorie_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                background: white;
                font-size: 13px;
            }
        """)
        self.categorie_combo.setEditable(True)
        self.categorie_combo.setPlaceholderText("Sélectionnez une catégorie...")
        layout.addWidget(self.categorie_combo, 2, 1)
        
        # Code tarif
        layout.addWidget(QLabel("Code tarif :"), 3, 0)
        self.code_tarif_combo = QComboBox()
        self.code_tarif_combo.setEditable(True)
        self.code_tarif_combo.currentTextChanged.connect(self.on_code_tarif_changed)  # ← Ajouter connexion
        layout.addWidget(self.code_tarif_combo, 3, 1)
        
        # Dates
        layout.addWidget(QLabel("Date début :"), 4, 0)
        self.date_debut = QDateEdit()
        self.date_debut.setDate(QDate.currentDate())
        self.date_debut.setCalendarPopup(True)
        layout.addWidget(self.date_debut, 4, 1)
        
        layout.addWidget(QLabel("Date fin :"), 5, 0)
        self.date_fin = QDateEdit()
        self.date_fin.setDate(QDate.currentDate().addYears(1))
        self.date_fin.setCalendarPopup(True)
        layout.addWidget(self.date_fin, 5, 1)
        
        # Options
        self.remorque_check = QCheckBox("🚛 Véhicule avec remorque")
        layout.addWidget(self.remorque_check, 6, 0, 1, 2)
        
        return group

    def create_global_garanties_section(self):
        """Section des garanties globales de la flotte"""
        group = QGroupBox("🎯 4. Garanties globales")
        layout = QVBoxLayout(group)
        
        info = QLabel("Sélectionnez les garanties et appliquez des coefficients à tous les véhicules")
        info.setStyleSheet(f"color: {AppColors.GRAY}; font-size: 11px;")
        layout.addWidget(info)
        
        # Grille des garanties
        grid = QGridLayout()
        grid.setSpacing(10)
        
        self.global_garanties = {}
        garanties_list = [
            ('rc', 'RC', '🛡️', True),
            ('dr', 'DR', '⚖️', True),
            ('vol', 'Vol', '🚗', False),
            ('vb', 'VB', '🔫', False),
            ('incendie', 'Incendie', '🔥', False),
            ('bris_glace', 'Bris', '🪟', False),
            ('ar', 'AR', '🔧', False),
            ('dta', 'DTA', '💥', False),
            ('ipt', 'IPT', '👥', False),
        ]
        
        for i, (key, label, icon, default) in enumerate(garanties_list):
            row = i // 3
            col = (i % 3) * 2
            
            # Checkbox
            cb = QCheckBox(f"{icon} {label}")
            cb.setChecked(default)
            grid.addWidget(cb, row, col)
            
            # Coefficient
            coeff = QLineEdit()
            coeff.setPlaceholderText("Coeff.")
            coeff.setFixedWidth(70)
            coeff.setEnabled(default)
            cb.toggled.connect(lambda checked, w=coeff: w.setEnabled(checked))
            grid.addWidget(coeff, row, col + 1)
            
            self.global_garanties[key] = {'checkbox': cb, 'coefficient': coeff}
        
        layout.addLayout(grid)
        
        # Bouton appliquer
        apply_btn = QPushButton("📌 Appliquer ces garanties à tous les véhicules")
        apply_btn.setProperty("class", "BtnPrimary")
        apply_btn.clicked.connect(self.apply_global_garanties)
        layout.addWidget(apply_btn)
        
        return group
    
    
    def create_right_panel(self):
        """Crée le panneau des résultats (scrollable)"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        
        # Statut
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet(f"""
            QFrame {{
                background: {AppColors.PRIMARY_LIGHT};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        status_layout = QHBoxLayout(self.status_frame)
        self.status_icon = QLabel("⏳")
        self.status_icon.setStyleSheet("font-size: 20px;")
        self.status_text = QLabel("Sélectionnez un fichier pour commencer")
        self.status_text.setStyleSheet(f"color: {AppColors.PRIMARY_DARK}; font-weight: 500;")
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        
        self.calc_btn = QPushButton("🔢 Calculer les garanties")
        self.calc_btn.setProperty("class", "BtnPrimary")
        self.calc_btn.setEnabled(False)
        self.calc_btn.clicked.connect(self.start_calculation)
        status_layout.addWidget(self.calc_btn)
        
        layout.addWidget(self.status_frame)
        
        # Progression
        self.progress_widget = QWidget()
        self.progress_widget.setVisible(False)
        progress_layout = QVBoxLayout(self.progress_widget)
        progress_layout.setSpacing(8)
        
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet(f"color: {AppColors.GRAY}; font-size: 11px;")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_widget)
        
        # Tableau des véhicules
        self.vehicles_table = QTableWidget()
        self.vehicles_table.setColumnCount(8)
        self.vehicles_table.setHorizontalHeaderLabels([
            "✓", "Immatriculation", "Marque", "Modèle", "RC (FCFA)", "Total (FCFA)", "Garanties", ""
        ])
        self.vehicles_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vehicles_table.setAlternatingRowColors(True)
        self.vehicles_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vehicles_table.setMinimumHeight(300)
        layout.addWidget(self.vehicles_table)
        
        # Récapitulatif des garanties (Tableau détaillé)
        recap_garanties_group = QGroupBox("📊 Récapitulatif détaillé des garanties")
        recap_garanties_layout = QVBoxLayout(recap_garanties_group)
        
        # Tableau des totaux par garantie
        self.garanties_summary_table = QTableWidget()
        self.garanties_summary_table.setColumnCount(4)
        self.garanties_summary_table.setHorizontalHeaderLabels([
            "Garantie", "Total (FCFA)", "Sélectionné (FCFA)", "%"
        ])
        self.garanties_summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.garanties_summary_table.setAlternatingRowColors(True)
        self.garanties_summary_table.setMaximumHeight(250)
        recap_garanties_layout.addWidget(self.garanties_summary_table)
        
        # layout.addWidget(recap_garanties_group)
        
        # Récapitulatif général avec toutes les garanties en cartes
        recap_group = QGroupBox("📊 Récapitulatif des garanties")
        recap_layout = QGridLayout(recap_group)  # Changer en QGridLayout
        recap_layout.setSpacing(15)
        recap_layout.setContentsMargins(15, 15, 15, 15)
        
        # Dictionnaire pour stocker les cartes de toutes les garanties
        self.recap_cards = {}
        
        # Liste de toutes les garanties avec leurs icônes
        all_garanties = [
            ('total', "Total véhicules", "0", "🚗"),
            ('selected', "Sélectionnés", "0", "✅"),
            ('rc', "RC", "0 FCFA", "🛡️"),
            ('dr', "DR", "0 FCFA", "⚖️"),
            ('vol', "Vol", "0 FCFA", "🚗"),
            ('vb', "VB", "0 FCFA", "🔫"),
            ('incendie', "Incendie", "0 FCFA", "🔥"),
            ('bris_glace', "Bris de glace", "0 FCFA", "🪟"),
            ('ar', "AR", "0 FCFA", "🔧"),
            ('dta', "Dommage Tout Accident", "0 FCFA", "💥"),
            ('ipt', "IPT", "0 FCFA", "👥"),
            ('prime_total', "Prime totale", "0 FCFA", "💰"),
        ]
        
        row = 0
        col = 0
        max_cols = 4  # 4 cartes par ligne
        
        for key, label, default_value, icon in all_garanties:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: {AppColors.GRAY_LIGHT};
                    border-radius: 10px;
                    padding: 8px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(4)
            
            # Ligne avec icône et label
            header_layout = QHBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 14px;")
            label_widget = QLabel(label)
            label_widget.setStyleSheet(f"color: {AppColors.GRAY}; font-size: 10px; font-weight: 500;")
            header_layout.addWidget(icon_label)
            header_layout.addWidget(label_widget)
            header_layout.addStretch()
            
            value_widget = QLabel(default_value)
            value_widget.setStyleSheet(f"color: {AppColors.DARK}; font-size: 16px; font-weight: 700;")
            value_widget.setAlignment(Qt.AlignCenter)
            
            card_layout.addLayout(header_layout)
            card_layout.addWidget(value_widget)
            
            self.recap_cards[key] = value_widget
            recap_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        layout.addWidget(recap_group)
        
        scroll.setWidget(content)
        return scroll

    def update_garanties_summary(self):
        """Met à jour le tableau récapitulatif des garanties"""
        # Définir les garanties à afficher
        garanties_list = [
            ('rc', 'Responsabilité Civile'),
            ('dr', 'Défense Recours'),
            ('vol', 'Vol'),
            ('vb', 'Vol à main armée'),
            ('incendie', 'Incendie'),
            ('bris_glace', 'Bris de glace'),
            ('ar', 'Assistance Réparation'),
            ('dta', 'Dommages Tous Accidents'),
            ('ipt', 'Individuelle Personnes Transportées'),
        ]
        
        # Calculer les totaux
        totals = {key: 0.0 for key, _ in garanties_list}
        selected_totals = {key: 0.0 for key, _ in garanties_list}
        total_vehicles = len(self.vehicles_data)
        selected_count = 0
        
        for row in range(self.vehicles_table.rowCount()):
            item = self.vehicles_table.item(row, 0)
            is_selected = item and item.checkState() == Qt.Checked
            if is_selected:
                selected_count += 1
            
            vehicle = self.vehicles_data[row] if row < len(self.vehicles_data) else None
            if vehicle and 'garanties' in vehicle:
                garanties = vehicle['garanties']
                for key, _ in garanties_list:
                    amount = garanties.get(key, 0)
                    totals[key] += amount
                    if is_selected:
                        selected_totals[key] += amount
        
        # Remplir le tableau
        self.garanties_summary_table.setRowCount(len(garanties_list))
        
        for i, (key, label) in enumerate(garanties_list):
            # Garantie
            self.garanties_summary_table.setItem(i, 0, QTableWidgetItem(label))
            
            # Total général
            total_item = QTableWidgetItem(f"{totals[key]:,.0f}".replace(",", " "))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.garanties_summary_table.setItem(i, 1, total_item)
            
            # Total sélectionné
            selected_item = QTableWidgetItem(f"{selected_totals[key]:,.0f}".replace(",", " "))
            selected_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            # Colorer en vert si montant > 0
            if selected_totals[key] > 0:
                selected_item.setForeground(QColor(AppColors.SUCCESS))
            self.garanties_summary_table.setItem(i, 2, selected_item)
            
            # Pourcentage
            percent = 0
            if totals[key] > 0:
                percent = (selected_totals[key] / totals[key]) * 100
            percent_item = QTableWidgetItem(f"{percent:.1f}%")
            percent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.garanties_summary_table.setItem(i, 3, percent_item)
        
        # Ajuster les colonnes
        self.garanties_summary_table.resizeColumnsToContents()

    def create_footer(self):
        """Crée le pied de page"""
        footer = QFrame()
        footer.setStyleSheet(f"border-top: 1px solid {AppColors.BORDER}; padding-top: 15px;")
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 0, 0, 0)
        
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
    #     """Charge le fichier"""
    #     try:
    #         if self.file_path.endswith(('.xlsx', '.xls')):
    #             df = pd.read_excel(self.file_path)
    #         else:
    #             df = pd.read_csv(self.file_path, encoding='utf-8')
            
    #         # Vérifier les colonnes
    #         required = ['immatriculation', 'marque', 'modele']
    #         missing = [c for c in required if c not in df.columns]
            
    #         if missing:
    #             self.file_info.setText(f"❌ Colonnes manquantes: {', '.join(missing)}")
    #             self.status_text.setText(f"Erreur: colonnes manquantes")
    #             return
            
    #         # Préparer les véhicules
    #         self.vehicles_data = []
    #         for _, row in df.iterrows():
    #             vehicle = {
    #                 'immatriculation': str(row.get('immatriculation', '')).strip().upper(),
    #                 'marque': str(row.get('marque', '')).strip(),
    #                 'modele': str(row.get('modele', '')).strip(),
    #                 'annee': int(row.get('annee', 0)) if pd.notna(row.get('annee')) else None,
    #                 'energie': str(row.get('energie', 'Essence')).strip() if pd.notna(row.get('energie')) else 'Essence',
    #                 'puissance': int(row.get('puissance', 0)) if pd.notna(row.get('puissance')) else 0,
    #                 'places': int(row.get('places', 5)) if pd.notna(row.get('places')) else 5,
    #                 'valeur_neuf': float(row.get('valeur_neuf', 0)) if pd.notna(row.get('valeur_neuf')) else 0,
    #                 'valeur_venale': float(row.get('valeur_venale', 0)) if pd.notna(row.get('valeur_venale')) else 0,
    #                 'categorie': str(row.get('categorie', 'VP')).strip() if pd.notna(row.get('categorie')) else 'VP'
    #             }
                
    #             if vehicle['immatriculation']:
    #                 self.vehicles_data.append(vehicle)
            
    #         self.file_info.setText(f"✅ {len(self.vehicles_data)} véhicules trouvés")
    #         self.status_text.setText(f"{len(self.vehicles_data)} véhicules chargés")
    #         self.status_icon.setText("✅")
    #         self.calc_btn.setEnabled(True)
            
    #         # Afficher un aperçu
    #         self.show_preview()
            
    #     except Exception as e:
    #         self.file_info.setText(f"❌ Erreur: {str(e)}")
    
    def load_file(self):
        """Charge le fichier"""
        try:
            if self.file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.file_path)
            else:
                df = pd.read_csv(self.file_path, encoding='utf-8')
            
            # Vérifier les colonnes
            required = ['immatriculation', 'marque', 'modele']
            missing = [c for c in required if c not in df.columns]
            
            if missing:
                self.file_info.setText(f"❌ Colonnes manquantes: {', '.join(missing)}")
                self.status_text.setText(f"Erreur: colonnes manquantes")
                return
            
            # Préparer les véhicules
            self.vehicles_data = []
            for _, row in df.iterrows():
                # Si la catégorie n'est pas dans le fichier, utiliser celle du combo
                categorie_value = ""
                if 'categorie' in df.columns and pd.notna(row.get('categorie')):
                    categorie_value = str(row.get('categorie', '')).strip().upper()
                else:
                    categorie_value = self.categorie_combo.currentText().strip().upper()
                
                vehicle = {
                    'immatriculation': str(row.get('immatriculation', '')).strip().upper(),
                    'chassis': str(row.get('chassis', '')).strip() if pd.notna(row.get('chassis')) else '',
                    'marque': str(row.get('marque', '')).strip(),
                    'modele': str(row.get('modele', '')).strip(),
                    'annee': int(row.get('annee', 0)) if pd.notna(row.get('annee')) else None,
                    'energie': str(row.get('energie', 'Essence')).strip() if pd.notna(row.get('energie')) else 'Essence',
                    'puissance': int(row.get('puissance', 0)) if pd.notna(row.get('puissance')) else 0,
                    'places': int(row.get('places', 5)) if pd.notna(row.get('places')) else 5,
                    'valeur_neuf': float(row.get('valeur_neuf', 0)) if pd.notna(row.get('valeur_neuf')) else 0,
                    'valeur_venale': float(row.get('valeur_venale', 0)) if pd.notna(row.get('valeur_venale')) else 0,
                    'categorie': categorie_value
                }
                
                if vehicle['immatriculation']:
                    self.vehicles_data.append(vehicle)
            
            self.file_info.setText(f"✅ {len(self.vehicles_data)} véhicules trouvés")
            self.status_text.setText(f"{len(self.vehicles_data)} véhicules chargés")
            self.status_icon.setText("✅")
            self.calc_btn.setEnabled(True)
            
            # Afficher un aperçu
            self.show_preview()
            
        except Exception as e:
            self.file_info.setText(f"❌ Erreur: {str(e)}")

    def show_preview(self):
        """Affiche un aperçu des véhicules"""
        self.vehicles_table.setRowCount(min(10, len(self.vehicles_data)))
        for i, v in enumerate(self.vehicles_data[:10]):
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Checked)
            self.vehicles_table.setItem(i, 0, check_item)
            
            self.vehicles_table.setItem(i, 1, QTableWidgetItem(v['immatriculation']))
            self.vehicles_table.setItem(i, 2, QTableWidgetItem(v['marque']))
            self.vehicles_table.setItem(i, 3, QTableWidgetItem(v['modele']))
            self.vehicles_table.setItem(i, 4, QTableWidgetItem("-"))
            self.vehicles_table.setItem(i, 5, QTableWidgetItem("-"))
            
            # Bouton garanties
            garanties_btn = QPushButton("🎯 Garanties")
            garanties_btn.setFixedSize(90, 28)
            garanties_btn.clicked.connect(lambda checked, r=i: self.edit_vehicle_garanties(r))
            self.vehicles_table.setCellWidget(i, 6, garanties_btn)
    
    def apply_global_garanties(self):
        """Applique les garanties globales à tous les véhicules"""
        if not self.vehicles_data:
            QMessageBox.warning(self, "Erreur", "Aucun véhicule chargé")
            return
        
        # Récupérer les coefficients
        coefficients = {}
        for key, widgets in self.global_garanties.items():
            if widgets['checkbox'].isChecked():
                coeff_text = widgets['coefficient'].text()
                try:
                    coeff = float(coeff_text) if coeff_text else 1.0
                except:
                    coeff = 1.0
                coefficients[key] = coeff
        
        if not coefficients:
            QMessageBox.warning(self, "Erreur", "Aucune garantie sélectionnée")
            return
        
        # Appliquer à tous les véhicules qui ont des garanties calculées
        applied = 0
        for vehicle in self.vehicles_data:
            if 'garanties' in vehicle:
                for key, coeff in coefficients.items():
                    if key in vehicle['garanties']:
                        vehicle['garanties'][key] = vehicle['garanties'][key] * coeff
                
                # Recalculer le total
                total_keys = ['rc', 'dr', 'vol', 'vb', 'incendie', 'bris_glace', 'ar', 'dta', 'ipt']
                vehicle['garanties']['total'] = sum(vehicle['garanties'].get(k, 0) for k in total_keys)
                applied += 1
        
        # Rafraîchir l'affichage
        self.refresh_vehicles_table()
        self.update_summary()
        
        QMessageBox.information(self, "Succès", f"Garanties appliquées à {applied} véhicules")
    
    def edit_vehicle_garanties(self, row):
        """Modifie les garanties d'un véhicule"""
        vehicle = self.vehicles_data[row]
        garanties = vehicle.get('garanties', {})
        
        dialog = VehicleGarantieDialog(vehicle, garanties, self)
        if dialog.exec():
            new_garanties = dialog.get_garanties()
            vehicle['garanties'] = new_garanties
            
            # Mettre à jour le tableau
            rc_item = self.vehicles_table.item(row, 4)
            rc_item.setText(f"{new_garanties.get('rc', 0):,.0f}".replace(",", " "))
            
            total_item = self.vehicles_table.item(row, 5)
            total_item.setText(f"{new_garanties.get('total', 0):,.0f}".replace(",", " "))
            
            self.update_summary()
    
    def refresh_vehicles_table(self):
        """Rafraîchit l'affichage du tableau"""
        for row, vehicle in enumerate(self.vehicles_data):
            if 'garanties' in vehicle:
                garanties = vehicle['garanties']
                
                rc_item = self.vehicles_table.item(row, 4)
                if rc_item:
                    rc_item.setText(f"{garanties.get('rc', 0):,.0f}".replace(",", " "))
                
                total_item = self.vehicles_table.item(row, 5)
                if total_item:
                    total_item.setText(f"{garanties.get('total', 0):,.0f}".replace(",", " "))
    
        # Mettre à jour les récapitulatifs
        self.update_summary()
        self.update_garanties_summary()  # ← Ajouter cette ligne
    
    def start_calculation(self):
        """Démarre le calcul des garanties"""
        if not self.vehicles_data:
            return
        
        compagny_id = self.compagny_combo.currentData()
        if not compagny_id:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une compagnie")
            return
        
        # Calculer la durée
        debut = self.date_debut.date().toPython()
        fin = self.date_fin.date().toPython()
        jours = max(1, (fin - debut).days)
        
        params = {
            'compagny_id': compagny_id,
            'zone': self.zone_combo.currentText(),
            'code_tarif': self.code_tarif_combo.currentText(),
            'avec_remorque': self.remorque_check.isChecked(),
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
    
    def on_calculation_progress(self, current, total, immat, garanties):
        """Met à jour la progression"""
        progress = int(current / total * 100)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Traitement de {immat}... ({current}/{total})")
        
        # Ajouter au tableau
        row = current - 1
        if row >= self.vehicles_table.rowCount():
            self.vehicles_table.setRowCount(row + 1)
        
        # Case à cocher
        check_item = QTableWidgetItem()
        check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        check_item.setCheckState(Qt.Checked)
        self.vehicles_table.setItem(row, 0, check_item)
        
        self.vehicles_table.setItem(row, 1, QTableWidgetItem(immat))
        self.vehicles_table.setItem(row, 2, QTableWidgetItem(self.vehicles_data[row].get('marque', '')))
        self.vehicles_table.setItem(row, 3, QTableWidgetItem(self.vehicles_data[row].get('modele', '')))
        
        rc_item = QTableWidgetItem(f"{garanties.get('rc', 0):,.0f}".replace(",", " "))
        rc_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 4, rc_item)
        
        total_item = QTableWidgetItem(f"{garanties.get('total', 0):,.0f}".replace(",", " "))
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 5, total_item)
        
        # Bouton modifier garanties
        garanties_btn = QPushButton("🎯 Garanties")
        garanties_btn.setFixedSize(90, 28)
        garanties_btn.clicked.connect(lambda checked, r=row: self.edit_vehicle_garanties(r))
        self.vehicles_table.setCellWidget(row, 6, garanties_btn)
        
        self.vehicles_table.resizeColumnsToContents()
        
        # Mettre à jour les récapitulatifs à la fin de tous les calculs
        if current == total:
            self.update_summary()
            self.update_garanties_summary()

    def on_calculation_finished(self, results):
        """Termine le calcul"""
        self.vehicles_data = results
        self.progress_widget.setVisible(False)
        self.calc_btn.setEnabled(False)
        self.calc_btn.setText("Calcul terminé")
        self.import_btn.setEnabled(True)
        
        self.status_icon.setText("✅")
        self.status_text.setText("Calcul terminé, vous pouvez importer les véhicules sélectionnés")
        
        self.update_summary()
        
    def update_summary(self):
        """Met à jour le récapitulatif avec toutes les garanties"""
        total = len(self.vehicles_data)
        selected = 0
        
        # Initialiser les totaux pour chaque garantie
        garanties_keys = ['rc', 'dr', 'vol', 'vb', 'incendie', 'bris_glace', 'ar', 'dta', 'ipt']
        totals = {key: 0.0 for key in garanties_keys}
        selected_totals = {key: 0.0 for key in garanties_keys}
        
        total_prime = 0
        
        for row in range(self.vehicles_table.rowCount()):
            item = self.vehicles_table.item(row, 0)
            is_selected = item and item.checkState() == Qt.Checked
            
            if is_selected:
                selected += 1
            
            vehicle = self.vehicles_data[row] if row < len(self.vehicles_data) else None
            if vehicle and 'garanties' in vehicle:
                garanties = vehicle['garanties']
                for key in garanties_keys:
                    amount = garanties.get(key, 0)
                    totals[key] += amount
                    if is_selected:
                        selected_totals[key] += amount
                
                # Total prime (PTTC) pour les sélectionnés
                if is_selected:
                    total_prime += garanties.get('total', 0)
        
        # Mettre à jour les cartes
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
        self.recap_cards['prime_total'].setText(f"{total_prime:,.0f}".replace(",", " ") + " FCFA")
        
        # Mettre à jour le tableau détaillé des garanties
        self.update_garanties_summary()

    def import_fleet(self):
        """Importe la flotte"""
        selected = []
        for row in range(self.vehicles_table.rowCount()):
            item = self.vehicles_table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                selected.append(self.vehicles_data[row])
        
        if not selected:
            QMessageBox.warning(self, "Erreur", "Aucun véhicule sélectionné")
            return
        
        try:
            owner_id = None
            current_user_id = 1
            
            if hasattr(self.parent(), 'contact'):
                owner_id = self.parent().contact.id
            
            if hasattr(self.controller, 'current_user_id'):
                current_user_id = self.controller.current_user_id
            
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
                    'assureur': self.compagny_combo.currentData(),
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
            
            # Importer les véhicules
            imported = 0
            errors = []
            
            for vehicle in selected:
                garanties = vehicle.get('garanties', {})
                
                chassis_value = vehicle.get('chassis', '')
                if not chassis_value or chassis_value == '':
                    chassis_value = f"CH-{vehicle['immatriculation']}"
                
                debut = self.date_debut.date().toPython()
                fin = self.date_fin.date().toPython()
                jours = max(1, (fin - debut).days)
                
                # Utiliser la catégorie du véhicule ou celle du combo
                categorie_value = vehicle.get('categorie', '')
                if not categorie_value:
                    categorie_value = self.categorie_combo.currentText().strip().upper()
                    if not categorie_value:
                        categorie_value = "VP"
                
                tva_rate = 0.1925
                total_garanties = garanties.get('total', 0)
                tva_amount = total_garanties * tva_rate
                
                vehicle_data = {
                    'immatriculation': vehicle['immatriculation'],
                    'chassis': chassis_value,
                    'zone': self.zone_combo.currentText(),
                    'marque': vehicle['marque'],
                    'categorie': categorie_value,
                    'modele': vehicle['modele'],
                    'annee': vehicle.get('annee'),
                    'energie': vehicle.get('energie', 'Essence'),
                    'usage': vehicle.get('puissance', 0),
                    'places': vehicle.get('places', 5),
                    'has_remorque': self.remorque_check.isChecked(),
                    'libele_tarif': "",
                    'code_tarif': self.code_tarif_combo.currentText(),
                    'owner_id': owner_id,
                    'compagny_id': self.compagny_combo.currentData(),
                    'fleet_id': fleet_id,
                    'tarif_id': None,
                    'date_debut': debut,
                    'date_fin': fin,
                    'statut': 'En Circulation',
                    'nbr_jour': jours,
                    'valeur_neuf': vehicle.get('valeur_neuf', 0),
                    'valeur_venale': vehicle.get('valeur_venale', 0),
                    'prime_brute': total_garanties,
                    'reduction': 0,
                    'prime_nette': total_garanties,
                    'prime_emise': total_garanties,
                    'carte_rose': 0,
                    'accessoires': 0,
                    'tva': tva_amount,
                    'fichier_asac': 0,
                    'vignette': 0,
                    'pttc': total_garanties + tva_amount,
                    # Garanties
                    'check_rc': True,
                    'amt_rc': garanties.get('rc', 0),
                    'red_rc': 0,
                    'amt_red_rc': garanties.get('rc', 0),
                    'amt_val_red_rc': 0,
                    'amt_fleet_rc_val': garanties.get('rc', 0),
                    'check_dr': True,
                    'amt_dr': garanties.get('dr', 0),
                    'red_dr': 0,
                    'amt_red_dr': garanties.get('dr', 0),
                    'amt_val_red_dr': 0,
                    'amt_fleet_dr_val': garanties.get('dr', 0),
                    'check_vol': garanties.get('vol', 0) > 0,
                    'amt_vol': garanties.get('vol', 0),
                    'red_vol': 0,
                    'amt_red_vol': garanties.get('vol', 0),
                    'amt_val_red_vol': 0,
                    'amt_fleet_vol_val': garanties.get('vol', 0),
                    'check_vb': garanties.get('vb', 0) > 0,
                    'amt_vb': garanties.get('vb', 0),
                    'red_vb': 0,
                    'amt_red_vb': garanties.get('vb', 0),
                    'amt_val_red_vb': 0,
                    'amt_fleet_vb_val': garanties.get('vb', 0),
                    'check_in': garanties.get('incendie', 0) > 0,
                    'amt_in': garanties.get('incendie', 0),
                    'red_in': 0,
                    'amt_red_in': garanties.get('incendie', 0),
                    'amt_val_red_in': 0,
                    'amt_fleet_in_val': garanties.get('incendie', 0),
                    'check_bris': garanties.get('bris_glace', 0) > 0,
                    'amt_bris': garanties.get('bris_glace', 0),
                    'red_bris': 0,
                    'amt_red_bris': garanties.get('bris_glace', 0),
                    'amt_val_red_bris': 0,
                    'amt_fleet_bris_val': garanties.get('bris_glace', 0),
                    'check_ar': garanties.get('ar', 0) > 0,
                    'amt_ar': garanties.get('ar', 0),
                    'red_ar': 0,
                    'amt_red_ar': garanties.get('ar', 0),
                    'amt_val_red_ar': 0,
                    'amt_fleet_ar_val': garanties.get('ar', 0),
                    'check_dta': garanties.get('dta', 0) > 0,
                    'amt_dta': garanties.get('dta', 0),
                    'red_dta': 0,
                    'amt_red_dta': garanties.get('dta', 0),
                    'amt_val_red_dta': 0,
                    'amt_fleet_dta_val': garanties.get('dta', 0),
                    'check_ipt': garanties.get('ipt', 0) > 0,
                    'amt_ipt': garanties.get('ipt', 0),
                    'red_ipt': 0,
                    'amt_red_ipt': garanties.get('ipt', 0),
                    'amt_val_red_ipt': 0,
                    'amt_fleet_ipt_val': garanties.get('ipt', 0),
                    'created_by': current_user_id,
                    'updated_by': None,
                    'created_ip': 'Offline',
                    'last_ip': None,
                    'is_active': True
                }
                
                try:
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
            
            if imported > 0:
                msg = f"✅ {imported} véhicule(s) importés avec succès"
                if errors:
                    msg += f"\n\n⚠️ {len(errors)} erreur(s):\n" + "\n".join(errors[:5])
                QMessageBox.information(self, "Importation terminée", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Erreur", "\n".join(errors[:5]))
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def download_template(self):
        """Télécharge le modèle Excel"""
        template_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le modèle", "modele_flotte_import.xlsx", "Excel (*.xlsx)"
        )
        
        if template_path:
            data = {
                "immatriculation": ["LT-001-AB", "LT-002-BC", "LT-003-CD"],
                "chassis": ["VF1ABCDEF12345678", "VF2GHIJKL98765432", "VF3MNOPQR45678901"],  # ← AJOUTER CETTE LIGNE
                "marque": ["Toyota", "Renault", "Mitsubishi"],
                "modele": ["Hilux", "Kangoo", "Outlander"],
                "annee": [2023, 2022, 2024],
                "energie": ["Diesel", "Diesel", "Essence"],
                "puissance": [7, 5, 6],
                "places": [5, 3, 7],
                "valeur_neuf": [35000000, 18000000, 28000000],
                "valeur_venale": [32000000, 15000000, 26000000],
                "categorie": ["VP", "VU", "VP"]
            }
            df = pd.DataFrame(data)
            df.to_excel(template_path, index=False)
            QMessageBox.information(self, "Succès", f"Modèle créé : {template_path}")
    
    def on_mode_changed(self):
        """Change le mode d'importation"""
        is_new = self.mode_new.isChecked()
        self.new_fleet_widget.setVisible(is_new)
        self.existing_fleet_widget.setVisible(not is_new)
        
        if not is_new:
            self.load_existing_fleets()
    
    def load_existing_fleets(self):
        """Charge les flottes existantes"""
        try:
            contact_id = None
            if hasattr(self.parent(), 'contact'):
                contact_id = self.parent().contact.id
            
            if contact_id:
                fleets = self.controller.fleets.get_fleets_by_owner(contact_id)
                self.existing_fleet_combo.clear()
                for fleet in fleets:
                    name = getattr(fleet, 'nom_flotte', getattr(fleet, 'nom', 'Sans nom'))
                    self.existing_fleet_combo.addItem(name, fleet.id)
        except Exception as e:
            print(f"Erreur: {e}")

    def _load_compagnies(self):
        """Charge les compagnies"""
        try:
            if hasattr(self.controller, 'compagnies'):
                if hasattr(self.controller.compagnies, 'get_contacts_for_combo'):
                    compagnies = self.controller.compagnies.get_contacts_for_combo()
                elif hasattr(self.controller.compagnies, 'get_contacts_for_combo'):
                    compagnies = self.controller.compagnies.get_contacts_for_combo()
                else:
                    compagnies = []
                
                self.compagny_combo.clear()
                self.compagny_combo.addItem("Sélectionner une compagnie", None)
                for cie in compagnies:
                    if hasattr(cie, 'nom'):
                        self.compagny_combo.addItem(cie.nom, cie.id)
                    elif isinstance(cie, tuple) and len(cie) >= 2:
                        self.compagny_combo.addItem(cie[1], cie[0])
        except Exception as e:
            print(f"Erreur chargement compagnies: {e}")
            self.compagny_combo.addItem("Erreur de chargement", None)
    
    def on_compagny_changed(self):
        """Charge les codes tarif pour la compagnie sélectionnée"""
        compagny_id = self.compagny_combo.currentData()
        if compagny_id:
            self.load_tarif_codes_async()

    def load_tarif_codes_async(self):
        """Charge les codes tarif de manière asynchrone"""
        compagny_id = self.compagny_combo.currentData()
        if not compagny_id:
            return
        
        from core.widgets.global_loader import get_global_loader
        from core.workers.database_worker import async_query
        
        loader = get_global_loader()
        loader.show_loading("Chargement des codes tarif...")
        
        def fetch():
            return self.controller.vehicles.get_tarif_codes_by_compagnie(compagny_id)
        
        async_query.execute(
            fetch,
            on_finished=self._on_tarif_codes_loaded,
            on_error=self._on_tarif_codes_error
        )

    def _on_tarif_codes_loaded(self, codes):
        """Callback quand les codes tarif sont chargés"""
        from core.widgets.global_loader import get_global_loader
        get_global_loader().hide_loading()
        
        self.code_tarif_combo.clear()
        self.code_tarif_combo.addItem("", "")
        
        for code, libelle in codes:
            self.code_tarif_combo.addItem(code, {"code": code, "libelle": libelle})

    def _on_tarif_codes_error(self, error):
        """Callback en cas d'erreur de chargement"""
        from core.widgets.global_loader import get_global_loader
        get_global_loader().hide_loading()
        print(f"Erreur chargement codes tarif: {error}")