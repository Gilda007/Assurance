# fleet_import_dialog.py - Version améliorée avec design moderne et scrollable

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QProgressBar,
    QMessageBox, QFrame, QComboBox, QRadioButton, QTabWidget,
    QScrollArea, QSplitter, QTextEdit, QCheckBox, QHeaderView,
    QWidget, QApplication, QLineEdit, QDateEdit, QGridLayout,
    QGroupBox, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QThread, QDate, QSettings
from PySide6.QtGui import QFont, QColor, QPalette
import pandas as pd
import traceback
from datetime import datetime
import os
import warnings

# Supprimer les avertissements Wayland
os.environ["QT_LOGGING_RULES"] = "qt.qpa.wayland.*=false"
os.environ["QT_QPA_PLATFORM"] = "xcb"  # Forcer l'utilisation de X11 au lieu de Wayland
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
        self.date_debut.dateChanged.connect(self.on_date_changed)
        form_layout.addWidget(self.date_debut, 0, 1)
        
        # Date fin
        form_layout.addWidget(QLabel("📅 Date de fin :"), 1, 0)
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_fin.dateChanged.connect(self.on_date_changed)
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
        
        # Prime calculée (optionnel)
        form_layout.addWidget(QLabel("💰 Prime prorata :"), 5, 0)
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
    
    def on_date_changed(self):
        """Met à jour les calculs quand les dates changent"""
        self.update_calculations()
    
    def update_calculations(self):
        """Calcule et affiche la durée, le statut et le prorata"""
        debut = self.date_debut.date()
        fin = self.date_fin.date()
        
        if fin >= debut:
            # Calculer la durée
            jours = debut.daysTo(fin)
            self.duree_label.setText(f"{jours} jours ({jours/30:.1f} mois)")
            
            # Calculer le prorata
            prorata = (jours / 365.0) * 100
            self.prorata_label.setText(f"{prorata:.1f}% de la prime annuelle")
            
            # Déterminer le statut
            today = QDate.currentDate()
            if fin < today:
                self.statut_label.setText("⏰ Expiré")
                self.statut_label.setStyleSheet(f"color: {AppColors.DANGER}; font-weight: bold;")
                self.prorata_label.setStyleSheet(f"color: {AppColors.DANGER}; font-weight: bold;")
            elif debut > today:
                self.statut_label.setText("⏳ À venir")
                self.statut_label.setStyleSheet(f"color: {AppColors.WARNING}; font-weight: bold;")
                self.prorata_label.setStyleSheet(f"color: {AppColors.WARNING}; font-weight: bold;")
            else:
                self.statut_label.setText("✅ En Circulation")
                self.statut_label.setStyleSheet(f"color: {AppColors.SUCCESS}; font-weight: bold;")
                self.prorata_label.setStyleSheet(f"color: {AppColors.SUCCESS}; font-weight: bold;")
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
        
        # Déterminer le statut
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


# class VehicleGarantieDialog(QDialog):
#     """Dialogue de personnalisation des garanties pour un véhicule"""
    
#     def __init__(self, vehicle, garanties, parent=None):
#         super().__init__(parent)
#         self.vehicle = vehicle
#         self.garanties = garanties
#         self.garantie_cards = {}
#         self.setWindowTitle(f"Garanties - {vehicle.get('immatriculation', 'Véhicule')}")
#         self.setMinimumSize(800, 700)
#         self.setModal(True)
#         self.setStyleSheet(STYLESHEET)
        
#         self.setup_ui()
#         self.load_garanties()
    
#     def setup_ui(self):
#         layout = QVBoxLayout(self)
#         layout.setSpacing(16)
#         layout.setContentsMargins(20, 20, 20, 20)
        
#         # En-tête
#         header = QFrame()
#         header.setStyleSheet(f"""
#             background: {AppColors.PRIMARY_LIGHT};
#             border-radius: 10px;
#             padding: 10px;
#         """)
#         header_layout = QHBoxLayout(header)
        
#         info = QLabel(f"🚗 {self.vehicle.get('immatriculation')} - {self.vehicle.get('marque')} {self.vehicle.get('modele')}")
#         info.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {AppColors.PRIMARY_DARK};")
#         header_layout.addWidget(info)
#         header_layout.addStretch()
#         layout.addWidget(header)
        
#         # Splitter horizontal pour diviser garanties et récapitulatif
#         splitter = QSplitter(Qt.Horizontal)
        
#         # ========== PARTIE GAUCHE : Garanties ==========
#         left_widget = QWidget()
#         left_layout = QVBoxLayout(left_widget)
#         left_layout.setContentsMargins(0, 0, 10, 0)
        
#         garanties_label = QLabel("🛡️ GARANTIES")
#         garanties_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 10px;")
#         left_layout.addWidget(garanties_label)
        
#         # Zone scrollable pour les garanties
#         scroll = QScrollArea()
#         scroll.setWidgetResizable(True)
#         scroll.setFrameShape(QFrame.NoFrame)
        
#         scroll_content = QWidget()
#         scroll_layout = QVBoxLayout(scroll_content)
#         scroll_layout.setSpacing(12)
        
#         # Créer les cartes de garanties
#         garanties_list = [
#             ('rc', 'Responsabilité Civile', '🛡️'),
#             ('dr', 'Défense Recours', '⚖️'),
#             ('vol', 'Vol', '🚗'),
#             ('vb', 'Vol à main armée', '🔫'),
#             ('incendie', 'Incendie', '🔥'),
#             ('bris_glace', 'Bris de glace', '🪟'),
#             ('ar', 'Assistance Réparation', '🔧'),
#             ('dta', 'Dommages Tous Accidents', '💥'),
#             ('ipt', 'Individuelle Personnes Transportées', '👥'),
#         ]
        
#         for key, label, icon in garanties_list:
#             card = GarantieCard(key, label, icon)
#             scroll_layout.addWidget(card)
#             self.garantie_cards[key] = card
        
#         scroll_layout.addStretch()
#         scroll.setWidget(scroll_content)
#         left_layout.addWidget(scroll)
        
#         # ========== PARTIE DROITE : Récapitulatif financier ==========
#         right_widget = QWidget()
#         right_layout = QVBoxLayout(right_widget)
#         right_layout.setContentsMargins(10, 0, 0, 0)
        
#         recap_label = QLabel("💰 RÉCAPITULATIF FINANCIER")
#         recap_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 10px;")
#         right_layout.addWidget(recap_label)
        
#         # Scroll pour le récapitulatif
#         recap_scroll = QScrollArea()
#         recap_scroll.setWidgetResizable(True)
#         recap_scroll.setFrameShape(QFrame.NoFrame)
        
#         recap_content = QWidget()
#         recap_form_layout = QVBoxLayout(recap_content)
#         recap_form_layout.setSpacing(12)
        
#         # Styles
#         style_primary = """
#             QLineEdit {
#                 background-color: #eff6ff;
#                 color: #1e40af;
#                 font-weight: bold;
#                 border: 2px solid #bfdbfe;
#                 border-radius: 12px;
#                 padding: 10px;
#                 font-size: 13px;
#             }
#         """
#         style_success = """
#             QLineEdit {
#                 background-color: #f0fdf4;
#                 color: #166534;
#                 font-weight: bold;
#                 border: 2px solid #bbf7d0;
#                 border-radius: 12px;
#                 padding: 10px;
#                 font-size: 14px;
#             }
#         """
#         style_warning = """
#             QLineEdit {
#                 background-color: #fffbeb;
#                 color: #b45309;
#                 font-weight: bold;
#                 border: 2px solid #fde68a;
#                 border-radius: 12px;
#                 padding: 10px;
#                 font-size: 13px;
#             }
#         """
#         style_info = """
#             QLineEdit {
#                 background-color: #f8fafc;
#                 color: #334155;
#                 font-weight: 500;
#                 border: 2px solid #e2e8f0;
#                 border-radius: 12px;
#                 padding: 10px;
#                 font-size: 12px;
#             }
#         """
        
#         # Montants principaux
#         prime_brute_group = self.create_labeled_field("Montant Brut", "0", style_info)
#         prime_nette_group = self.create_labeled_field("Prime Nette", "0", style_success)
#         reduction_group = self.create_labeled_field("Réduction", "0", style_warning)
        
#         recap_form_layout.addWidget(prime_brute_group)
#         recap_form_layout.addWidget(reduction_group)
#         recap_form_layout.addWidget(prime_nette_group)
        
#         # Séparateur
#         sep = QFrame()
#         sep.setFrameShape(QFrame.HLine)
#         sep.setStyleSheet("background: #e2e8f0; margin: 5px 0;")
#         recap_form_layout.addWidget(sep)
        
#         # Taxes et frais
#         accessoire_group = self.create_labeled_field("Accessoires", "0", style_info)
#         asac_group = self.create_labeled_field("Fichier ASAC", "0", style_info)
#         tva_group = self.create_labeled_field("TVA (19.25%)", "0", style_info)
        
#         recap_form_layout.addWidget(accessoire_group)
#         recap_form_layout.addWidget(asac_group)
#         recap_form_layout.addWidget(tva_group)
        
#         # Séparateur
#         sep2 = QFrame()
#         sep2.setFrameShape(QFrame.HLine)
#         sep2.setStyleSheet("background: #e2e8f0; margin: 5px 0;")
#         recap_form_layout.addWidget(sep2)
        
#         # Autres frais
#         carte_rose_group = self.create_labeled_field("Carte Rose", "0", style_info)
#         vignette_group = self.create_labeled_field("Vignette", "0", style_info)
#         pttc_group = self.create_labeled_field("PTTC", "0", style_primary)
        
#         recap_form_layout.addWidget(carte_rose_group)
#         recap_form_layout.addWidget(vignette_group)
#         recap_form_layout.addWidget(pttc_group)
        
#         recap_form_layout.addStretch()
#         recap_scroll.setWidget(recap_content)
#         right_layout.addWidget(recap_scroll)
        
#         # Ajouter les deux parties au splitter
#         splitter.addWidget(left_widget)
#         splitter.addWidget(right_widget)
#         splitter.setSizes([450, 300])
        
#         layout.addWidget(splitter)
        
#         # Total général
#         total_frame = QFrame()
#         total_frame.setStyleSheet(f"""
#             background: {AppColors.SUCCESS_LIGHT};
#             border-radius: 10px;
#             padding: 10px;
#         """)
#         total_layout = QHBoxLayout(total_frame)
#         total_layout.addWidget(QLabel("<b>💰 TOTAL GÉNÉRAL DES GARANTIES :</b>"))
#         self.total_label = QLabel("0 FCFA")
#         self.total_label.setStyleSheet(f"font-size: 16px; font-weight: 800; color: {AppColors.SUCCESS_DARK};")
#         total_layout.addWidget(self.total_label)
#         total_layout.addStretch()
#         layout.addWidget(total_frame)
        
#         # Boutons
#         btn_layout = QHBoxLayout()
#         btn_layout.addStretch()
        
#         ok_btn = QPushButton("Valider")
#         ok_btn.setProperty("class", "BtnSuccess")
#         ok_btn.setFixedSize(120, 35)
#         ok_btn.clicked.connect(self.accept)
        
#         cancel_btn = QPushButton("Annuler")
#         cancel_btn.setProperty("class", "BtnSecondary")
#         cancel_btn.setFixedSize(120, 35)
#         cancel_btn.clicked.connect(self.reject)
        
#         btn_layout.addWidget(cancel_btn)
#         btn_layout.addWidget(ok_btn)
#         layout.addLayout(btn_layout)
        
#         # Stocker les références des champs pour y accéder plus tard
#         self.prime_brute = prime_brute_group.findChild(QLineEdit)
#         self.prime_nette = prime_nette_group.findChild(QLineEdit)
#         self.reduction = reduction_group.findChild(QLineEdit)
#         self.accessoire = accessoire_group.findChild(QLineEdit)
#         self.asac = asac_group.findChild(QLineEdit)
#         self.tva = tva_group.findChild(QLineEdit)
#         self.carte_rose = carte_rose_group.findChild(QLineEdit)
#         self.vignette = vignette_group.findChild(QLineEdit)
#         self.pttc = pttc_group.findChild(QLineEdit)
        
#         # Connecter les signaux
#         self.accessoire.textChanged.connect(self.calculate_tva)
#         self.asac.textChanged.connect(self.calculate_tva)
#         self.accessoire.textChanged.connect(self.calculate_pttc)
#         self.asac.textChanged.connect(self.calculate_pttc)
#         self.carte_rose.textChanged.connect(self.calculate_pttc)
#         self.vignette.textChanged.connect(self.calculate_pttc)
    
#     def create_labeled_field(self, label_text, default_value, style):
#         """Crée un widget contenant un label et un champ"""
#         container = QWidget()
#         layout = QVBoxLayout(container)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.setSpacing(4)
        
#         label = QLabel(label_text)
#         label.setStyleSheet("""
#             font-size: 11px;
#             font-weight: 600;
#             color: #64748b;
#             letter-spacing: 0.3px;
#         """)
        
#         field = QLineEdit(default_value)
#         field.setStyleSheet(style)
#         field.setAlignment(Qt.AlignRight)
        
#         layout.addWidget(label)
#         layout.addWidget(field)
        
#         return container
    
#     def calculate_tva(self):
#         """Calcule la TVA"""
#         try:
#             prime_nette = self.get_float_value(self.prime_nette)
#             accessoires = self.get_float_value(self.accessoire)
#             asac = self.get_float_value(self.asac)
            
#             base_tva = prime_nette + accessoires + asac
#             tva = base_tva * 0.1925
            
#             self.tva.setText(f"{tva:,.0f}".replace(",", " "))
#             return tva
#         except:
#             return 0
    
#     def calculate_pttc(self):
#         """Calcule le PTTC"""
#         try:
#             prime_nette = self.get_float_value(self.prime_nette)
#             accessoires = self.get_float_value(self.accessoire)
#             asac = self.get_float_value(self.asac)
#             tva = self.get_float_value(self.tva)
#             vignette = self.get_float_value(self.vignette)
#             carte_rose = self.get_float_value(self.carte_rose)
            
#             pttc = prime_nette + accessoires + asac + tva + vignette + carte_rose
#             self.pttc.setText(f"{pttc:,.0f}".replace(",", " "))
#             return pttc
#         except:
#             return 0
    
#     def get_float_value(self, widget):
#         """Récupère une valeur float d'un widget"""
#         try:
#             if not widget or not widget.text():
#                 return 0.0
#             txt = widget.text().strip().replace(" ", "").replace(",", ".")
#             return float(txt) if txt else 0.0
#         except:
#             return 0.0
    
#     def load_garanties(self):
#         for key, card in self.garantie_cards.items():
#             amount = self.garanties.get(key, 0)
#             reduction = self.garanties.get(f'reduction_{key}', 0)
#             card.set_values(amount, reduction)
#             card.garantie_changed.connect(self.on_garantie_changed)
    
#     def on_garantie_changed(self, key, checked, net_amount):
#         self.update_total()
    
#     def update_total(self):
#         total = sum(card.get_net_amount() for card in self.garantie_cards.values())
#         self.total_label.setText(f"{total:,.0f} FCFA".replace(",", " "))
        
#         # Mettre à jour les champs du récapitulatif
#         self.prime_brute.setText(f"{total:,.0f}".replace(",", " "))
#         self.prime_nette.setText(f"{total:,.0f}".replace(",", " "))
#         self.calculate_tva()
#         self.calculate_pttc()
    
#     def get_garanties(self):
#         result = {}
#         for key, card in self.garantie_cards.items():
#             result[key] = card.get_net_amount()
#             result[f'brut_{key}'] = card.current_amount
#             result[f'reduction_{key}'] = card.current_reduction
#         result['total'] = sum(v for k, v in result.items() if not k.startswith(('brut_', 'reduction_', 'total')))
        
#         # Ajouter les valeurs du récapitulatif
#         result['carte_rose'] = self.get_float_value(self.carte_rose)
#         result['accessoires'] = self.get_float_value(self.accessoire)
#         result['asac'] = self.get_float_value(self.asac)
#         result['vignette'] = self.get_float_value(self.vignette)
#         result['tva'] = self.get_float_value(self.tva)
#         result['pttc'] = self.get_float_value(self.pttc)
        
#         return result

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
        layout.setSpacing(12)
        
        # Zone scrollable pour les garanties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(12)
        
        # Créer les cartes de garanties
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

    # def create_frais_tab(self):
    #     """Crée l'onglet des frais et taxes"""
    #     tab = QWidget()
    #     layout = QGridLayout(tab)
    #     layout.setSpacing(15)
    #     layout.setContentsMargins(20, 20, 20, 20)
        
    #     style_field = """
    #         QLineEdit {
    #             border: 1px solid #e2e8f0;
    #             border-radius: 8px;
    #             padding: 8px 12px;
    #             background: white;
    #             font-size: 13px;
    #         }
    #         QLineEdit:focus {
    #             border-color: #2563eb;
    #         }
    #     """
        
    #     # Frais supplémentaires
    #     layout.addWidget(QLabel("Accessoires (FCFA) :"), 0, 0)
    #     self.frais_accessoires = QLineEdit(str(self.vehicle.get('accessoires', 0)))
    #     self.frais_accessoires.setStyleSheet(style_field)
    #     self.frais_accessoires.textChanged.connect(self.calculate_tva_pttc)
    #     layout.addWidget(self.frais_accessoires, 0, 1)
        
    #     layout.addWidget(QLabel("Fichier ASAC (FCFA) :"), 1, 0)
    #     self.frais_asac = QLineEdit(str(self.vehicle.get('asac', 0)))
    #     self.frais_asac.setStyleSheet(style_field)
    #     self.frais_asac.textChanged.connect(self.calculate_tva_pttc)
    #     layout.addWidget(self.frais_asac, 1, 1)
        
    #     layout.addWidget(QLabel("Carte Rose (FCFA) :"), 2, 0)
    #     self.frais_carte_rose = QLineEdit(str(self.vehicle.get('carte_rose', 0)))
    #     self.frais_carte_rose.setStyleSheet(style_field)
    #     self.frais_carte_rose.textChanged.connect(self.calculate_pttc)
    #     layout.addWidget(self.frais_carte_rose, 2, 1)
        
    #     layout.addWidget(QLabel("Vignette (FCFA) :"), 3, 0)
    #     self.frais_vignette = QLineEdit(str(self.vehicle.get('vignette', 0)))
    #     self.frais_vignette.setStyleSheet(style_field)
    #     self.frais_vignette.textChanged.connect(self.calculate_pttc)
    #     layout.addWidget(self.frais_vignette, 3, 1)
        
    #     # Séparateur
    #     sep = QFrame()
    #     sep.setFrameShape(QFrame.HLine)
    #     sep.setStyleSheet("background: #e2e8f0; margin: 10px 0;")
    #     layout.addWidget(sep, 4, 0, 1, 2)
        
    #     # Résultats des calculs
    #     layout.addWidget(QLabel("TVA (19.25%) :"), 5, 0)
    #     self.frais_tva = QLineEdit("0")
    #     self.frais_tva.setReadOnly(True)
    #     self.frais_tva.setStyleSheet("background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 8px 12px;")
    #     layout.addWidget(self.frais_tva, 5, 1)
        
    #     layout.addWidget(QLabel("PTTC (Total) :"), 6, 0)
    #     self.frais_pttc = QLineEdit("0")
    #     self.frais_pttc.setReadOnly(True)
    #     self.frais_pttc.setStyleSheet("background-color: #d1fae5; border: 1px solid #bbf7d0; border-radius: 8px; padding: 8px 12px; font-weight: bold;")
    #     layout.addWidget(self.frais_pttc, 6, 1)
        
    #     layout.addStretch()
        
    #     return tab

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
        for key, card in self.garantie_cards.items():
            amount = self.garanties.get(key, 0)
            reduction = self.garanties.get(f'reduction_{key}', 0)
            card.set_values(amount, reduction)
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
        
        duree_contrat = vehicle.get('nbr_jour', 365)
        if duree_contrat <= 0:
            duree_contrat = 365

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

        # Bouton Appliquer les frais
        apply_frais_btn = QPushButton("💰 Appliquer les frais aux véhicules sélectionnés")
        apply_frais_btn.setProperty("class", "BtnPrimary")
        apply_frais_btn.clicked.connect(self.apply_global_frais_to_selected)
        layout.addWidget(apply_frais_btn)
        
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

    # def create_insurance_section(self):
    #     """Section des paramètres d'assurance"""
    #     group = QGroupBox("🛡️ 3. Paramètres d'assurance")
    #     layout = QGridLayout(group)
    #     layout.setSpacing(12)
        
    #     # Compagnie
    #     layout.addWidget(QLabel("Compagnie :"), 0, 0)
    #     self.compagny_combo = QComboBox()
    #     self.compagny_combo.currentIndexChanged.connect(self.on_compagny_changed)
    #     layout.addWidget(self.compagny_combo, 0, 1)
        
    #     # Zone
    #     layout.addWidget(QLabel("Zone :"), 1, 0)
    #     self.zone_combo = QComboBox()
    #     self.zone_combo.addItems(["A", "B", "C"])
    #     layout.addWidget(self.zone_combo, 1, 1)
        
    #     # Catégorie (comme dans automobile_form_view)
    #     layout.addWidget(QLabel("Catégorie :"), 2, 0)
    #     self.categorie_combo = QComboBox()  # ← Garder categorie_combo
    #     self.categorie_combo.setStyleSheet("""
    #         QComboBox {
    #             border: 1px solid #e2e8f0;
    #             border-radius: 8px;
    #             padding: 8px 12px;
    #             background: white;
    #             font-size: 13px;
    #         }
    #     """)
    #     self.categorie_combo.setEditable(True)
    #     self.categorie_combo.setPlaceholderText("Sélectionnez une catégorie...")
    #     layout.addWidget(self.categorie_combo, 2, 1)
        
    #     # Code tarif
    #     layout.addWidget(QLabel("Code tarif :"), 3, 0)
    #     self.code_tarif_combo = QComboBox()
    #     self.code_tarif_combo.setEditable(True)
    #     self.code_tarif_combo.currentTextChanged.connect(self.on_code_tarif_changed)  # ← Ajouter connexion
    #     layout.addWidget(self.code_tarif_combo, 3, 1)
        
    #     # Dates
    #     layout.addWidget(QLabel("Date début :"), 4, 0)
    #     self.date_debut = QDateEdit()
    #     self.date_debut.setDate(QDate.currentDate())
    #     self.date_debut.setCalendarPopup(True)
    #     layout.addWidget(self.date_debut, 4, 1)
        
    #     layout.addWidget(QLabel("Date fin :"), 5, 0)
    #     self.date_fin = QDateEdit()
    #     self.date_fin.setDate(QDate.currentDate().addYears(1))
    #     self.date_fin.setCalendarPopup(True)
    #     layout.addWidget(self.date_fin, 5, 1)
        
    #     # Options
    #     self.remorque_check = QCheckBox("🚛 Véhicule avec remorque")
    #     layout.addWidget(self.remorque_check, 6, 0, 1, 2)
        
    #     return group

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
        
        # Catégorie
        layout.addWidget(QLabel("Catégorie :"), 2, 0)
        self.categorie_combo = QComboBox()
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
        self.code_tarif_combo.currentTextChanged.connect(self.on_code_tarif_changed)
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
        
        # ========== NOUVEAUX CHAMPS DE FRAIS ==========
        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #e2e8f0; margin: 10px 0;")
        layout.addWidget(sep, 6, 0, 1, 2)
        
        # Titre des frais
        frais_title = QLabel("📋 FRAIS SUPPLÉMENTAIRES (par véhicule)")
        frais_title.setStyleSheet("font-weight: 700; color: #475569; margin-top: 5px;")
        layout.addWidget(frais_title, 7, 0, 1, 2)
        
        # Accessoires
        layout.addWidget(QLabel("Accessoires (FCFA) :"), 8, 0)
        self.global_accessoires = QLineEdit("0")
        self.global_accessoires.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px;")
        layout.addWidget(self.global_accessoires, 8, 1)
        
        # Fichier ASAC
        layout.addWidget(QLabel("Fichier ASAC (FCFA) :"), 9, 0)
        self.global_asac = QLineEdit("0")
        self.global_asac.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px;")
        layout.addWidget(self.global_asac, 9, 1)
        
        # Carte Rose
        layout.addWidget(QLabel("Carte Rose (FCFA) :"), 10, 0)
        self.global_carte_rose = QLineEdit("0")
        self.global_carte_rose.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px;")
        layout.addWidget(self.global_carte_rose, 10, 1)
        
        # Vignette
        layout.addWidget(QLabel("Vignette (FCFA) :"), 11, 0)
        self.global_vignette = QLineEdit("0")
        self.global_vignette.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px;")
        layout.addWidget(self.global_vignette, 11, 1)
        
        # Option remorque
        layout.addWidget(QLabel(""), 12, 0)
        self.remorque_check = QCheckBox("🚛 Véhicule avec remorque")
        layout.addWidget(self.remorque_check, 12, 1)
        
        return group

    def apply_global_frais_to_selected(self):
        """Applique les frais globaux (accessoires, asac, carte rose, vignette) aux véhicules sélectionnés"""
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
                
                # Recalculer TVA et PTTC
                garanties = vehicle.get('garanties', {})
                total_garanties = garanties.get('total', 0)
                vehicle['tva'] = (total_garanties + accessoires + asac) * 0.1925
                vehicle['pttc'] = total_garanties + accessoires + asac + vehicle['tva'] + vignette + carte_rose
            
            self.update_summary()
            self.update_garanties_summary()
            
            QMessageBox.information(self, "Succès", f"Frais appliqués à {len(selected_rows)} véhicule(s)")
            
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", f"Valeur invalide: {str(e)}")

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
   
    def edit_vehicle_dates(self, vehicle_id):
        """Modifie les dates d'un véhicule à partir de son ID"""
        row = self.find_row_by_vehicle_id(vehicle_id)
        if row == -1:
            QMessageBox.warning(self, "Erreur", "Véhicule non trouvé")
            return
        
        vehicle = self.vehicles_data[row]
        
        dialog = VehicleDatesDialog(vehicle, self)
        if dialog.exec():
            new_dates = dialog.get_dates()
            
            # Sauvegarder les montants annuels si pas encore fait
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
                if key != 'total':
                    new_garanties[key] = amount * prorata
            
            new_garanties['total'] = sum(new_garanties.values())
            vehicle['garanties'] = new_garanties
            
            # Mettre à jour l'affichage du tableau
            self.update_vehicle_row_display(row, vehicle, new_dates)
            
            self.update_summary()
            self.update_garanties_summary()
            
            QMessageBox.information(self, "Succès", f"Dates mises à jour pour {vehicle['immatriculation']}\nPrime recalculée au prorata de {prorata*100:.1f}%")

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

        self.refresh_btn = QPushButton("🔄 Rafraîchir garanties")
        self.refresh_btn.setProperty("class", "BtnSecondary")
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.clicked.connect(self.refresh_fleet_guarantees)
        status_layout.addWidget(self.refresh_btn)
        
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
        self.vehicles_table.setColumnCount(19)
        self.vehicles_table.setHorizontalHeaderLabels([
            "✓", "Immatriculation", "Marque", "Modèle", "Catégorie",
            "Date Début", "Date Fin", "Jours",
            "RC", "DR", "Vol", "VB", "Incendie", "Bris", "AR", "DTA", "IPT", "Total",
            "Actions"
        ])

        # Configuration du redimensionnement des colonnes
        for col in range(19):
            self.vehicles_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Interactive)

        # Permettre le déplacement des colonnes
        self.vehicles_table.horizontalHeader().setSectionsMovable(True)
        self.vehicles_table.horizontalHeader().setStretchLastSection(False)

        # Configuration générale
        self.vehicles_table.setAlternatingRowColors(True)
        self.vehicles_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vehicles_table.setMinimumHeight(400)

        # Hauteur des lignes
        self.vehicles_table.verticalHeader().setDefaultSectionSize(48)
        self.vehicles_table.verticalHeader().setMinimumSectionSize(40)

        # Largeur de la colonne Actions
        self.vehicles_table.setColumnWidth(18, 120)

        layout.addWidget(self.vehicles_table)
        
        # Récapitulatif général avec toutes les garanties en cartes
        recap_group = QGroupBox("📊 Récapitulatif des garanties")
        recap_layout = QGridLayout(recap_group)
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
            ('carte_rose', "Carte Rose", "0 FCFA", "📄"),
            ('accessoires', "Accessoires", "0 FCFA", "🔧"),
            ('asac', "Fichier ASAC", "0 FCFA", "📁"),
            ('vignette', "Vignette", "0 FCFA", "🏷️"),
            ('tva', "TVA", "0 FCFA", "📊"),
            ('pttc_total', "PTTC Total", "0 FCFA", "💰"),
        ]
        
        row = 0
        col = 0
        max_cols = 4
        
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

    def update_vehicle_row_display(self, row, vehicle, new_dates):
        """Met à jour l'affichage d'une ligne du tableau"""
        
        # Mettre à jour les dates
        date_debut_str = new_dates['date_debut'].strftime("%d/%m/%Y")
        date_fin_str = new_dates['date_fin'].strftime("%d/%m/%Y")
        
        self.vehicles_table.setItem(row, 5, QTableWidgetItem(date_debut_str))
        self.vehicles_table.setItem(row, 6, QTableWidgetItem(date_fin_str))
        
        jours_item = QTableWidgetItem(str(new_dates['nbr_jour']))
        jours_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 7, jours_item)
        
        # Mettre à jour les garanties
        garanties_mapping = [
            ('rc', 9), ('dr', 10), ('vol', 11), ('vb', 12),
            ('incendie', 13), ('bris_glace', 14), ('ar', 15), ('dta', 16), ('ipt', 17)
        ]
        
        garanties = vehicle.get('garanties', {})
        for key, col in garanties_mapping:
            amount = garanties.get(key, 0)
            item = QTableWidgetItem(f"{amount:,.0f}".replace(",", " "))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.vehicles_table.setItem(row, col, item)
        
        # Mettre à jour le total
        total_amount = garanties.get('total', 0)
        total_item = QTableWidgetItem(f"{total_amount:,.0f}".replace(",", " "))
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 17, total_item)

    def find_row_by_vehicle_id(self, vehicle_id):
        """Trouve l'index de la ligne à partir de l'ID du véhicule"""
        for i, vehicle in enumerate(self.vehicles_data):
            if vehicle.get('id') == vehicle_id:
                return i
        return -1

    def save_column_widths(self, logicalIndex, oldSize, newSize):
        """Sauvegarde les largeurs des colonnes quand l'utilisateur les modifie"""
        try:
            settings = QSettings("LOMETA", "FleetImport")
            widths = {}
            for col in range(self.vehicles_table.columnCount()):
                widths[str(col)] = self.vehicles_table.columnWidth(col)
            settings.setValue("fleet_table_column_widths", widths)
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")

    def restore_column_widths(self):
        """Restaure les largeurs des colonnes sauvegardées"""
        try:
            settings = QSettings("LOMETA", "FleetImport")
            widths = settings.value("fleet_table_column_widths")
            if widths and isinstance(widths, dict):
                for col_str, width in widths.items():
                    col = int(col_str)
                    if col < self.vehicles_table.columnCount():
                        self.vehicles_table.setColumnWidth(col, int(width))
        except Exception as e:
            print(f"Erreur restauration: {e}")

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
        
        # Calculer les totaux à partir du tableau
        totals = {key: 0.0 for key, _ in garanties_list}
        selected_totals = {key: 0.0 for key, _ in garanties_list}
        
        garanties_columns = {
            'rc': 5, 'dr': 6, 'vol': 7, 'vb': 8,
            'incendie': 9, 'bris_glace': 10, 'ar': 11, 'dta': 12, 'ipt': 13
        }
        
        for row in range(self.vehicles_table.rowCount()):
            # Vérifier si la ligne est sélectionnée
            check_item = self.vehicles_table.item(row, 0)
            is_selected = check_item and check_item.checkState() == Qt.Checked
            
            for key, col in garanties_columns.items():
                item = self.vehicles_table.item(row, col)
                if item and item.text() != "-":
                    try:
                        # Nettoyer le texte (enlever les espaces)
                        text = item.text().replace(" ", "")
                        amount = float(text) if text else 0
                        totals[key] += amount
                        if is_selected:
                            selected_totals[key] += amount
                    except ValueError:
                        pass

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
       
    def load_file(self):
        """Charge le fichier avec toutes les colonnes"""
        try:
            if self.file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.file_path)
            else:
                df = pd.read_csv(self.file_path, encoding='utf-8')
            
            # Vérifier les colonnes obligatoires
            required = ['immatriculation', 'marque', 'modele']
            missing = [c for c in required if c not in df.columns]
            
            if missing:
                self.file_info.setText(f"❌ Colonnes manquantes: {', '.join(missing)}")
                self.status_text.setText(f"Erreur: colonnes manquantes")
                return
            
            # Préparer les véhicules avec toutes les données
            self.vehicles_data = []
            for _, row in df.iterrows():
                # Catégorie: du fichier ou du combo
                categorie_value = ""
                if 'categorie' in df.columns and pd.notna(row.get('categorie')):
                    categorie_value = str(row.get('categorie', '')).strip().upper()
                else:
                    categorie_value = self.categorie_combo.currentText().strip().upper()
                    if not categorie_value:
                        categorie_value = "VP"
                
                # Zone: du fichier ou du combo
                zone_value = self.zone_combo.currentText()
                if 'zone_tarifaire' in df.columns and pd.notna(row.get('zone_tarifaire')):
                    zone_value = str(row.get('zone_tarifaire', '')).strip().upper()
                
                # Récupérer les dates depuis le fichier si disponibles
                date_debut_value = None
                date_fin_value = None
                nbr_jour_value = 365
                statut_value = "En Circulation"
                
                if 'date_debut' in df.columns and pd.notna(row.get('date_debut')):
                    try:
                        date_debut_value = pd.to_datetime(row.get('date_debut')).to_pydatetime()
                    except:
                        date_debut_value = None
                
                if 'date_fin' in df.columns and pd.notna(row.get('date_fin')):
                    try:
                        date_fin_value = pd.to_datetime(row.get('date_fin')).to_pydatetime()
                    except:
                        date_fin_value = None
                
                if date_debut_value and date_fin_value:
                    nbr_jour_value = (date_fin_value - date_debut_value).days
                    if nbr_jour_value <= 0:
                        nbr_jour_value = 365
                
                vehicle = {
                    # OBLIGATOIRES
                    'immatriculation': str(row.get('immatriculation', '')).strip().upper(),
                    'marque': str(row.get('marque', '')).strip(),
                    'modele': str(row.get('modele', '')).strip(),
                    
                    # RECOMMANDÉES
                    'chassis': str(row.get('chassis', '')).strip() if pd.notna(row.get('chassis')) else '',
                    'categorie': categorie_value,
                    'annee': int(row.get('annee', 0)) if pd.notna(row.get('annee')) else None,
                    'energie': str(row.get('energie', 'Essence')).strip() if pd.notna(row.get('energie')) else 'Essence',
                    'puissance': int(row.get('puissance', 0)) if pd.notna(row.get('puissance')) else 0,
                    'places': int(row.get('places', 5)) if pd.notna(row.get('places')) else 5,
                    'valeur_neuf': float(row.get('valeur_neuf', 0)) if pd.notna(row.get('valeur_neuf')) else 0,
                    'valeur_venale': float(row.get('valeur_venale', 0)) if pd.notna(row.get('valeur_venale')) else 0,
                    
                    # OPTIONNELLES
                    'type_vehicule': str(row.get('type_vehicule', '')).strip() if pd.notna(row.get('type_vehicule')) else '',
                    'zone': zone_value,
                    'proprietaire': str(row.get('proprietaire', '')).strip() if pd.notna(row.get('proprietaire')) else '',
                    'telephone': str(row.get('telephone', '')).strip() if pd.notna(row.get('telephone')) else '',
                    'email': str(row.get('email', '')).strip() if pd.notna(row.get('email')) else '',
                    'ville': str(row.get('ville', '')).strip() if pd.notna(row.get('ville')) else '',
                    'adresse': str(row.get('adresse', '')).strip() if pd.notna(row.get('adresse')) else '',
                    'code_postal': str(row.get('code_postal', '')).strip() if pd.notna(row.get('code_postal')) else '',
                    'conducteur_nom': str(row.get('conducteur_nom', '')).strip() if pd.notna(row.get('conducteur_nom')) else '',
                    'conducteur_naissance': str(row.get('conducteur_naissance', '')).strip() if pd.notna(row.get('conducteur_naissance')) else '',
                    'conducteur_permis': str(row.get('conducteur_permis', '')).strip() if pd.notna(row.get('conducteur_permis')) else '',
                    
                    # Dates (CORRECTION : utiliser les variables définies)
                    'date_debut': date_debut_value,
                    'date_fin': date_fin_value,
                    'nbr_jour': nbr_jour_value,
                    'statut': statut_value,
                    
                    # Initialiser les frais
                    'accessoires': 0,
                    'asac': 0,
                    'carte_rose': 0,
                    'vignette': 0,
                    'tva': 0,
                    'pttc': 0,
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
            traceback.print_exc()

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
            self.vehicles_table.setItem(i, 4, QTableWidgetItem(v.get('categorie', 'VP')))
            
            # Dates par défaut
            date_debut = self.date_debut.date().toPython()
            date_fin = self.date_fin.date().toPython()
            jours = (date_fin - date_debut).days
            
            self.vehicles_table.setItem(i, 5, QTableWidgetItem(date_debut.strftime("%d/%m/%Y")))
            self.vehicles_table.setItem(i, 6, QTableWidgetItem(date_fin.strftime("%d/%m/%Y")))
            
            jours_item = QTableWidgetItem(str(jours))
            jours_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.vehicles_table.setItem(i, 7, jours_item)
            
            # Initialiser les colonnes de garanties
            for col in range(8, 17):
                item = QTableWidgetItem("-")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.vehicles_table.setItem(i, col, item)
            
            # Total
            total_item = QTableWidgetItem("-")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.vehicles_table.setItem(i, 17, total_item)
            
            # Widget des actions (deux boutons)
            vehicle_id = v.get('id', i)  # Utilise l'ID du véhicule ou l'index comme fallback
            actions_widget = VehicleActionsWidget(
                vehicle_id,
                self.edit_vehicle_garanties,
                self.edit_vehicle_dates,
                self.on_modify_vehicle
            )
            self.vehicles_table.setCellWidget(i, 18, actions_widget)
            v['accessoires'] = 0
            v['asac'] = 0
            v['carte_rose'] = 0
            v['vignette'] = 0
        
        # Ajuster la hauteur des lignes
        self.adjust_row_heights()
        self.vehicles_table.resizeColumnsToContents()

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
    
    def edit_vehicle_garanties(self, vehicle_id):
        """Modifie les garanties et informations d'un véhicule à partir de son ID"""
        row = self.find_row_by_vehicle_id(vehicle_id)
        if row == -1:
            QMessageBox.warning(self, "Erreur", "Véhicule non trouvé")
            return
        
        vehicle = self.vehicles_data[row]
        garanties = vehicle.get('garanties', {})
        
        dialog = VehicleGarantieDialog(vehicle, garanties, self)
        if dialog.exec():
            new_data = dialog.get_garanties()
            
            # Mettre à jour les garanties
            vehicle['garanties'] = new_data
            
            # Mettre à jour les informations du véhicule
            vehicle['immatriculation'] = new_data.get('immatriculation', vehicle.get('immatriculation'))
            vehicle['chassis'] = new_data.get('chassis', vehicle.get('chassis'))
            vehicle['marque'] = new_data.get('marque', vehicle.get('marque'))
            vehicle['modele'] = new_data.get('modele', vehicle.get('modele'))
            vehicle['categorie'] = new_data.get('categorie', vehicle.get('categorie'))
            vehicle['annee'] = new_data.get('annee', vehicle.get('annee'))
            vehicle['energie'] = new_data.get('energie', vehicle.get('energie'))
            vehicle['puissance'] = new_data.get('puissance', vehicle.get('puissance'))
            vehicle['places'] = new_data.get('places', vehicle.get('places'))
            vehicle['valeur_neuf'] = new_data.get('valeur_neuf', vehicle.get('valeur_neuf'))
            vehicle['valeur_venale'] = new_data.get('valeur_venale', vehicle.get('valeur_venale'))
            vehicle['zone'] = new_data.get('zone', vehicle.get('zone'))
            
            # Mettre à jour les frais
            vehicle['accessoires'] = new_data.get('accessoires', 0)
            vehicle['asac'] = new_data.get('asac', 0)
            vehicle['carte_rose'] = new_data.get('carte_rose', 0)
            vehicle['vignette'] = new_data.get('vignette', 0)
            vehicle['tva'] = new_data.get('tva', 0)
            vehicle['pttc'] = new_data.get('pttc', 0)
            
            # Mettre à jour les dates
            vehicle['date_debut'] = new_data.get('date_debut', vehicle.get('date_debut'))
            vehicle['date_fin'] = new_data.get('date_fin', vehicle.get('date_fin'))
            vehicle['nbr_jour'] = new_data.get('nbr_jour', vehicle.get('nbr_jour', 365))
            vehicle['statut'] = new_data.get('statut', vehicle.get('statut', 'En Circulation'))
            
            # Mettre à jour l'affichage dans le tableau
            garanties_mapping = [
                ('rc', 8), ('dr', 9), ('vol', 10), ('vb', 11),
                ('incendie', 12), ('bris_glace', 13), ('ar', 14), ('dta', 15), ('ipt', 16)
            ]
            
            for key, col in garanties_mapping:
                amount = new_data.get(key, 0)
                item = QTableWidgetItem(f"{amount:,.0f}".replace(",", " "))
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.vehicles_table.setItem(row, col, item)
            
            total_amount = new_data.get('total', 0)
            total_item = QTableWidgetItem(f"{total_amount:,.0f}".replace(",", " "))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.vehicles_table.setItem(row, 17, total_item)
            
            # Mettre à jour les dates dans le tableau
            date_debut = vehicle.get('date_debut')
            date_fin = vehicle.get('date_fin')
            if date_debut:
                date_debut_str = date_debut.strftime("%d/%m/%Y") if isinstance(date_debut, datetime) else str(date_debut)
            else:
                date_debut_str = "-"
            if date_fin:
                date_fin_str = date_fin.strftime("%d/%m/%Y") if isinstance(date_fin, datetime) else str(date_fin)
            else:
                date_fin_str = "-"
            
            self.vehicles_table.setItem(row, 5, QTableWidgetItem(date_debut_str))
            self.vehicles_table.setItem(row, 6, QTableWidgetItem(date_fin_str))
            
            jours_item = QTableWidgetItem(str(vehicle.get('nbr_jour', 0)))
            jours_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.vehicles_table.setItem(row, 7, jours_item)
            
            # Mettre à jour la catégorie
            self.vehicles_table.setItem(row, 4, QTableWidgetItem(vehicle.get('categorie', 'VP')))
            
            self.update_summary()
            self.update_garanties_summary()
            
            QMessageBox.information(self, "Succès", f"Véhicule {vehicle['immatriculation']} mis à jour avec succès")
    
    def on_modify_vehicle(self, vehicle_id):
        """Modifie les garanties et informations d'un véhicule à partir de son ID"""
        row = self.find_row_by_vehicle_id(vehicle_id)
        if row == -1:
            QMessageBox.warning(self, "Erreur", "Véhicule non trouvé")
            return
        
        vehicle = self.vehicles_data[row]
        garanties = vehicle.get('garanties', {})
        
        dialog = VehicleGarantieDialog(vehicle, garanties, self)
        if dialog.exec():
            new_data = dialog.get_garanties()
            
            # Mettre à jour les garanties
            vehicle['garanties'] = new_data
            
            # Mettre à jour les informations du véhicule
            vehicle['immatriculation'] = new_data.get('immatriculation', vehicle.get('immatriculation'))
            vehicle['chassis'] = new_data.get('chassis', vehicle.get('chassis'))
            vehicle['marque'] = new_data.get('marque', vehicle.get('marque'))
            vehicle['modele'] = new_data.get('modele', vehicle.get('modele'))
            vehicle['categorie'] = new_data.get('categorie', vehicle.get('categorie'))
            vehicle['annee'] = new_data.get('annee', vehicle.get('annee'))
            vehicle['energie'] = new_data.get('energie', vehicle.get('energie'))
            vehicle['puissance'] = new_data.get('puissance', vehicle.get('puissance'))
            vehicle['places'] = new_data.get('places', vehicle.get('places'))
            vehicle['valeur_neuf'] = new_data.get('valeur_neuf', vehicle.get('valeur_neuf'))
            vehicle['valeur_venale'] = new_data.get('valeur_venale', vehicle.get('valeur_venale'))
            vehicle['zone'] = new_data.get('zone', vehicle.get('zone'))
            
            # Mettre à jour les frais
            vehicle['accessoires'] = new_data.get('accessoires', 0)
            vehicle['asac'] = new_data.get('asac', 0)
            vehicle['carte_rose'] = new_data.get('carte_rose', 0)
            vehicle['vignette'] = new_data.get('vignette', 0)
            vehicle['tva'] = new_data.get('tva', 0)
            vehicle['pttc'] = new_data.get('pttc', 0)
            
            # Mettre à jour les dates
            vehicle['date_debut'] = new_data.get('date_debut', vehicle.get('date_debut'))
            vehicle['date_fin'] = new_data.get('date_fin', vehicle.get('date_fin'))
            vehicle['nbr_jour'] = new_data.get('nbr_jour', vehicle.get('nbr_jour', 365))
            vehicle['statut'] = new_data.get('statut', vehicle.get('statut', 'En Circulation'))
            
            # Mettre à jour l'affichage dans le tableau
            garanties_mapping = [
                ('rc', 8), ('dr', 9), ('vol', 10), ('vb', 11),
                ('incendie', 12), ('bris_glace', 13), ('ar', 14), ('dta', 15), ('ipt', 16)
            ]
            
            for key, col in garanties_mapping:
                amount = new_data.get(key, 0)
                item = QTableWidgetItem(f"{amount:,.0f}".replace(",", " "))
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.vehicles_table.setItem(row, col, item)
            
            total_amount = new_data.get('total', 0)
            total_item = QTableWidgetItem(f"{total_amount:,.0f}".replace(",", " "))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.vehicles_table.setItem(row, 17, total_item)
            
            # Mettre à jour les dates dans le tableau
            date_debut = vehicle.get('date_debut')
            date_fin = vehicle.get('date_fin')
            if date_debut:
                date_debut_str = date_debut.strftime("%d/%m/%Y") if isinstance(date_debut, datetime) else str(date_debut)
            else:
                date_debut_str = "-"
            if date_fin:
                date_fin_str = date_fin.strftime("%d/%m/%Y") if isinstance(date_fin, datetime) else str(date_fin)
            else:
                date_fin_str = "-"
            
            self.vehicles_table.setItem(row, 5, QTableWidgetItem(date_debut_str))
            self.vehicles_table.setItem(row, 6, QTableWidgetItem(date_fin_str))
            
            jours_item = QTableWidgetItem(str(vehicle.get('nbr_jour', 0)))
            jours_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.vehicles_table.setItem(row, 7, jours_item)
            
            # Mettre à jour la catégorie
            self.vehicles_table.setItem(row, 4, QTableWidgetItem(vehicle.get('categorie', 'VP')))
            
            self.update_summary()
            self.update_garanties_summary()
            
            QMessageBox.information(self, "Succès", f"Véhicule {vehicle['immatriculation']} mis à jour avec succès")
 
    def refresh_vehicles_table(self):
        """Rafraîchit l'affichage du tableau avec toutes les garanties"""
        garanties_mapping = [
            ('rc', 5), ('dr', 6), ('vol', 7), ('vb', 8),
            ('incendie', 9), ('bris_glace', 10), ('ar', 11), ('dta', 12), ('ipt', 13)
        ]
        
        for row, vehicle in enumerate(self.vehicles_data):
            if 'garanties' in vehicle:
                garanties = vehicle['garanties']
                
                # Mettre à jour chaque garantie
                for key, col in garanties_mapping:
                    amount = garanties.get(key, 0)
                    item = self.vehicles_table.item(row, col)
                    if item:
                        item.setText(f"{amount:,.0f}".replace(",", " "))
                    else:
                        new_item = QTableWidgetItem(f"{amount:,.0f}".replace(",", " "))
                        new_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.vehicles_table.setItem(row, col, new_item)
                
                # Mettre à jour le total
                total_amount = garanties.get('total', 0)
                total_item = self.vehicles_table.item(row, 14)
                if total_item:
                    total_item.setText(f"{total_amount:,.0f}".replace(",", " "))
                else:
                    new_total_item = QTableWidgetItem(f"{total_amount:,.0f}".replace(",", " "))
                    new_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.vehicles_table.setItem(row, 14, new_total_item)
        
        # Mettre à jour les récapitulatifs
        self.update_summary()
        self.update_garanties_summary()
    
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
        
        # Informations de base
        self.vehicles_table.setItem(row, 1, QTableWidgetItem(immat))
        self.vehicles_table.setItem(row, 2, QTableWidgetItem(self.vehicles_data[row].get('marque', '')))
        self.vehicles_table.setItem(row, 3, QTableWidgetItem(self.vehicles_data[row].get('modele', '')))
        self.vehicles_table.setItem(row, 4, QTableWidgetItem(self.vehicles_data[row].get('categorie', 'VP')))

        # ========== AJOUT : Initialiser les frais pour ce véhicule ==========
        self.vehicles_data[row]['accessoires'] = 0
        self.vehicles_data[row]['asac'] = 0
        self.vehicles_data[row]['carte_rose'] = 0
        self.vehicles_data[row]['vignette'] = 0
        self.vehicles_data[row]['tva'] = 0
        self.vehicles_data[row]['pttc'] = 0
        
        # Dates
        date_debut = self.vehicles_data[row].get('date_debut')
        date_fin = self.vehicles_data[row].get('date_fin')
        
        if date_debut:
            if isinstance(date_debut, datetime):
                date_debut_str = date_debut.strftime("%d/%m/%Y")
            else:
                date_debut_str = str(date_debut)
        else:
            date_debut_str = self.date_debut.date().toPython().strftime("%d/%m/%Y")
        
        if date_fin:
            if isinstance(date_fin, datetime):
                date_fin_str = date_fin.strftime("%d/%m/%Y")
            else:
                date_fin_str = str(date_fin)
        else:
            date_fin_str = self.date_fin.date().toPython().strftime("%d/%m/%Y")
        
        self.vehicles_table.setItem(row, 5, QTableWidgetItem(date_debut_str))
        self.vehicles_table.setItem(row, 6, QTableWidgetItem(date_fin_str))
        
        # Jours
        nbr_jour = self.vehicles_data[row].get('nbr_jour', 0)
        jours_item = QTableWidgetItem(str(nbr_jour) if nbr_jour > 0 else "-")
        jours_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 7, jours_item)
        
        # Garanties
        garanties_mapping = [
            ('rc', 8), ('dr', 9), ('vol', 10), ('vb', 11),
            ('incendie', 12), ('bris_glace', 13), ('ar', 14), ('dta', 15), ('ipt', 16)
        ]
        
        for key, col in garanties_mapping:
            amount = garanties.get(key, 0)
            item = QTableWidgetItem(f"{amount:,.0f}".replace(",", " "))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.vehicles_table.setItem(row, col, item)
        
        # Total
        total_amount = garanties.get('total', 0)
        total_item = QTableWidgetItem(f"{total_amount:,.0f}".replace(",", " "))
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 17, total_item)
        
        # Widget des actions (deux boutons)
        vehicle_id = self.vehicles_data[row].get('id', row)  # Utilise l'ID du véhicule ou l'index comme fallback
        actions_widget = VehicleActionsWidget(
            vehicle_id,
            self.edit_vehicle_garanties,
            self.edit_vehicle_dates
        )
        self.vehicles_table.setCellWidget(row, 18, actions_widget)
        
        # Ajuster la hauteur de la ligne
        self.vehicles_table.resizeColumnsToContents()
        
        # Mettre à jour les récapitulatifs à la fin
        if current == total:
            self.adjust_row_heights()
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
        """Met à jour le récapitulatif avec toutes les garanties et frais"""
        total = len(self.vehicles_data)
        selected = 0
        
        # Initialiser les totaux pour chaque garantie
        garanties_keys = ['rc', 'dr', 'vol', 'vb', 'incendie', 'bris_glace', 'ar', 'dta', 'ipt']
        totals = {key: 0.0 for key in garanties_keys}
        selected_totals = {key: 0.0 for key in garanties_keys}
        
        # Initialiser les totaux pour les frais
        frais_keys = ['carte_rose', 'accessoires', 'asac', 'vignette', 'tva', 'pttc']
        frais_totals = {key: 0.0 for key in frais_keys}
        selected_frais_totals = {key: 0.0 for key in frais_keys}
        
        total_prime = 0
        total_pttc = 0
        
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
                
                # Total prime pour les sélectionnés
                if is_selected:
                    total_prime += garanties.get('total', 0)
                
                # Frais
                for key in frais_keys:
                    amount = vehicle.get(key, 0)
                    frais_totals[key] += amount
                    if is_selected:
                        selected_frais_totals[key] += amount
                        if key == 'pttc':
                            total_pttc += amount
        
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
        self.recap_cards['prime_total'].setText(f"{total_prime:,.0f}".replace(",", " ") + " FCFA")
        
        # Mettre à jour les cartes des frais (si vous les avez ajoutées dans recap_cards)
        # Sinon, ajoutez ces lignes après avoir ajouté les cartes correspondantes dans create_right_panel
        if 'carte_rose' in self.recap_cards:
            self.recap_cards['carte_rose'].setText(f"{selected_frais_totals['carte_rose']:,.0f}".replace(",", " ") + " FCFA")
        if 'accessoires' in self.recap_cards:
            self.recap_cards['accessoires'].setText(f"{selected_frais_totals['accessoires']:,.0f}".replace(",", " ") + " FCFA")
        if 'asac' in self.recap_cards:
            self.recap_cards['asac'].setText(f"{selected_frais_totals['asac']:,.0f}".replace(",", " ") + " FCFA")
        if 'vignette' in self.recap_cards:
            self.recap_cards['vignette'].setText(f"{selected_frais_totals['vignette']:,.0f}".replace(",", " ") + " FCFA")
        if 'tva' in self.recap_cards:
            self.recap_cards['tva'].setText(f"{selected_frais_totals['tva']:,.0f}".replace(",", " ") + " FCFA")
        if 'pttc_total' in self.recap_cards:
            self.recap_cards['pttc_total'].setText(f"{total_pttc:,.0f}".replace(",", " ") + " FCFA")
        
        self.update_garanties_summary()

    def import_fleet(self):
        """Importe la flotte"""
        selected = []
        for row in range(self.vehicles_table.rowCount()):
            item = self.vehicles_table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                # Vérifier que row existe dans self.vehicles_data
                if row < len(self.vehicles_data):
                    selected.append(self.vehicles_data[row])
                else:
                    print(f"Warning: row {row} out of range for vehicles_data (len={len(self.vehicles_data)})")
        
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
                
                # Utiliser les dates du véhicule si disponibles, sinon les dates globales
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
                
                # Utiliser la catégorie du véhicule ou celle du combo
                categorie_value = vehicle.get('categorie', '')
                if not categorie_value:
                    categorie_value = self.categorie_combo.currentText().strip().upper()
                    if not categorie_value:
                        categorie_value = "VP"
                
                tva_rate = 0.1925
                total_garanties = garanties.get('total', 0)
                tva_amount = total_garanties * tva_rate
                
                # Récupérer les frais du véhicule
                accessoires = vehicle.get('accessoires', 0)
                asac = vehicle.get('asac', 0)
                carte_rose = vehicle.get('carte_rose', 0)
                vignette = vehicle.get('vignette', 0)
                
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
                    'carte_rose': carte_rose,
                    'accessoires': accessoires,
                    'tva': tva_amount,
                    'fichier_asac': asac,
                    'vignette': vignette,
                    'pttc': total_garanties + accessoires + asac + tva_amount + vignette + carte_rose,
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
        """Télécharge le modèle Excel avec toutes les colonnes nécessaires"""
        template_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le modèle", "modele_flotte_import.xlsx", "Excel (*.xlsx)"
        )
        
        if template_path:
            # Créer un DataFrame avec toutes les colonnes
            data = {
                # Identifiants de base
                "immatriculation": ["LT-001-AB", "LT-002-BC", "LT-003-CD", "LT-004-DE", "LT-005-EF"],
                "chassis": ["VF1ABCDEF12345678", "VF2GHIJKL98765432", "VF3MNOPQR45678901", "VF4QRSTU12345678", "VF5VWXYZ98765432"],
                
                # Informations véhicule
                "marque": ["Toyota", "Renault", "Mitsubishi", "Peugeot", "Mercedes"],
                "modele": ["Hilux", "Kangoo", "Outlander", "Partner", "Sprinter"],
                "categorie": ["VP", "VU", "VP", "VU", "PL"],
                "annee": [2023, 2022, 2024, 2023, 2022],
                "energie": ["Diesel", "Diesel", "Essence", "Diesel", "Diesel"],
                "puissance": [7, 5, 6, 4, 8],
                "places": [5, 3, 7, 5, 9],
                
                # Valeurs financières
                "valeur_neuf": [35000000, 18000000, 28000000, 22000000, 45000000],
                "valeur_venale": [32000000, 15000000, 26000000, 20000000, 42000000],
                
                # Options
                "type_vehicule": ["Pick-up", "Utilitaire", "SUV", "Utilitaire", "Minibus"],
                "zone_tarifaire": ["A", "B", "A", "C", "B"],
                
                # Informations propriétaire (optionnel)
                "proprietaire": ["SARL Transport Log", "SARL Express", "ETS Voyages", "Logistique Plus", "Transport SARL"],
                "telephone": ["+237612345678", "+237623456789", "+237634567890", "+237645678901", "+237656789012"],
                "email": ["contact@transportlog.cm", "info@express.cm", "contact@voyages.cm", "info@logplus.cm", "contact@transport.cm"],
                
                # Adresse
                "ville": ["Douala", "Yaoundé", "Douala", "Garoua", "Douala"],
                "adresse": ["Rue 12, Bonanjo", "Bastos", "Akwa", "Quartier Administratif", "Bonabéri"],
                "code_postal": ["BP 1234", "BP 5678", "BP 9012", "BP 3456", "BP 7890"],
                
                # Conducteur principal (optionnel)
                "conducteur_nom": ["Jean Mbarga", "Paul Nganou", "Marie Ngo", "Jacques Tchoffo", "Emmanuel Njoya"],
                "conducteur_naissance": ["1985-06-15", "1990-03-22", "1988-11-10", "1982-08-05", "1979-12-18"],
                "conducteur_permis": ["2010-01-10", "2012-05-20", "2011-09-15", "2008-03-12", "2005-06-25"],
            }
            
            df = pd.DataFrame(data)
            
            # Ajouter des commentaires dans une feuille séparée
            with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Véhicules', index=False)
                
                # Créer une feuille d'instructions
                instructions_df = pd.DataFrame({
                    "Colonne": [
                        "immatriculation", "chassis", "marque", "modele", "categorie",
                        "annee", "energie", "puissance", "places", "valeur_neuf",
                        "valeur_venale", "type_vehicule", "zone_tarifaire", "proprietaire",
                        "telephone", "email", "ville", "adresse", "code_postal",
                        "conducteur_nom", "conducteur_naissance", "conducteur_permis"
                    ],
                    "Description": [
                        "🔴 OBLIGATOIRE - Plaque d'immatriculation du véhicule",
                        "Numéro de châssis (17 caractères recommandé)",
                        "🔴 OBLIGATOIRE - Marque du véhicule",
                        "🔴 OBLIGATOIRE - Modèle du véhicule",
                        "Catégorie: VP (Véhicule Particulier), VU (Véhicule Utilitaire), PL (Poids Lourd)",
                        "Année de mise en circulation",
                        "Type d'énergie: Essence, Diesel, Electrique, Hybride",
                        "Puissance fiscale en CV",
                        "Nombre de places assises",
                        "Valeur à neuf du véhicule (FCFA)",
                        "Valeur vénale actuelle (FCFA)",
                        "Type de véhicule: Pick-up, Utilitaire, SUV, Minibus, etc.",
                        "Zone tarifaire: A, B, C",
                        "Nom du propriétaire (optionnel)",
                        "Téléphone du propriétaire (optionnel)",
                        "Email du propriétaire (optionnel)",
                        "Ville de résidence",
                        "Adresse complète",
                        "Code postal / BP",
                        "Nom du conducteur principal",
                        "Date de naissance du conducteur (YYYY-MM-DD)",
                        "Date d'obtention du permis (YYYY-MM-DD)"
                    ],
                    "Exemple": [
                        "LT-001-AB", "VF1ABCDEF12345678", "Toyota", "Hilux", "VP",
                        "2023", "Diesel", "7", "5", "35000000",
                        "32000000", "Pick-up", "A", "SARL Transport Log",
                        "+237612345678", "contact@transportlog.cm", "Douala", "Rue 12, Bonanjo", "BP 1234",
                        "Jean Mbarga", "1985-06-15", "2010-01-10"
                    ],
                    "Statut": [
                        "🔴 Requis", "Optionnel", "🔴 Requis", "🔴 Requis", "Recommandé",
                        "Optionnel", "Recommandé", "Recommandé", "Optionnel", "Recommandé",
                        "Recommandé", "Optionnel", "Optionnel", "Optionnel",
                        "Optionnel", "Optionnel", "Optionnel", "Optionnel", "Optionnel",
                        "Optionnel", "Optionnel", "Optionnel"
                    ]
                })
                
                instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
                
                # Ajuster la largeur des colonnes pour la feuille Instructions
                worksheet_instructions = writer.sheets['Instructions']
                for column in worksheet_instructions.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet_instructions.column_dimensions[column_letter].width = adjusted_width
                
                # Ajouter des couleurs pour les en-têtes
                from openpyxl.styles import PatternFill, Font, Alignment
                
                workbook = writer.book
                
                # Colorer la feuille des instructions
                ws_instructions = workbook['Instructions']
                header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                header_font = Font(color="FFFFFF", bold=True)
                
                for cell in ws_instructions[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center')
                
                # Colorer la feuille des véhicules
                ws_vehicles = workbook['Véhicules']
                for cell in ws_vehicles[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center')
                
                # Ajuster la largeur des colonnes pour la feuille Véhicules
                for column in ws_vehicles.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 30)
                    ws_vehicles.column_dimensions[column_letter].width = adjusted_width
            
            QMessageBox.information(
                self, 
                "Succès", 
                f"✅ Modèle créé avec succès !\n\n"
                f"📁 Emplacement: {template_path}\n\n"
                f"📋 Le fichier contient:\n"
                f"  • Une feuille 'Véhicules' avec les données à remplir\n"
                f"  • Une feuille 'Instructions' avec la description des colonnes\n\n"
                f"🔴 Les colonnes obligatoires sont:\n"
                f"  • immatriculation\n"
                f"  • marque\n"
                f"  • modele"
            )
    
    def on_mode_changed(self):
        """Change le mode d'importation"""
        is_new = self.mode_new.isChecked()
        self.new_fleet_widget.setVisible(is_new)
        self.existing_fleet_widget.setVisible(not is_new)
        
        if not is_new:
            self.load_existing_fleets()
            # Connecter le signal de changement de sélection
            self.existing_fleet_combo.currentIndexChanged.connect(self.on_existing_fleet_selected)
        else:
            # Déconnecter pour éviter les appels inutiles
            try:
                self.existing_fleet_combo.currentIndexChanged.disconnect()
            except:
                pass
            # Réinitialiser les données
            self.vehicles_data = []
            self.vehicles_table.setRowCount(0)
            self.import_btn.setEnabled(False)
            self.calc_btn.setEnabled(False)
    
    def on_existing_fleet_selected(self, index):
        """Charge les véhicules de la flotte sélectionnée"""
        fleet_id = self.existing_fleet_combo.currentData()
        if not fleet_id:
            return
        
        try:
            # Afficher le chargement
            self.status_icon.setText("🔄")
            self.status_text.setText("Chargement des véhicules de la flotte...")
            
            # Récupérer les véhicules de la flotte
            vehicles = self.controller.vehicles.get_vehicles_by_fleet(fleet_id)
            
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
            for vehicle in vehicles:
                # Si c'est un objet SQLAlchemy
                if hasattr(vehicle, '__dict__'):
                    vehicle_dict = {
                        'id': vehicle.id,
                        'immatriculation': vehicle.immatriculation,
                        'chassis': vehicle.chassis,
                        'marque': vehicle.marque,
                        'modele': vehicle.modele,
                        'categorie': vehicle.categorie,
                        'annee': vehicle.annee,
                        'energie': vehicle.energie,
                        'puissance': vehicle.usage,  # usage stocke la puissance
                        'places': vehicle.places,
                        'valeur_neuf': vehicle.valeur_neuf,
                        'valeur_venale': vehicle.valeur_venale,
                        'zone': vehicle.zone,
                        'date_debut': vehicle.date_debut,
                        'date_fin': vehicle.date_fin,
                        'nbr_jour': vehicle.nbr_jour,
                        'statut': vehicle.statut,
                        # Garanties existantes
                        'garanties': {
                            'rc': vehicle.amt_rc or 0,
                            'dr': vehicle.amt_dr or 0,
                            'vol': vehicle.amt_vol or 0,
                            'vb': vehicle.amt_vb or 0,
                            'incendie': vehicle.amt_in or 0,
                            'bris_glace': vehicle.amt_bris or 0,
                            'ar': vehicle.amt_ar or 0,
                            'dta': vehicle.amt_dta or 0,
                            'ipt': vehicle.amt_ipt or 0,
                            'total': vehicle.prime_nette or 0
                        },
                        'status': 'success',
                        'from_fleet': True  # Marqueur pour indiquer que ça vient d'une flotte
                    }
                else:
                    # Si c'est déjà un dictionnaire
                    vehicle_dict = vehicle
                    vehicle_dict['from_fleet'] = True
                
                self.vehicles_data.append(vehicle_dict)
            
            # Afficher les véhicules dans le tableau
            self.display_fleet_vehicles()
            
            self.file_info.setText(f"✅ {len(self.vehicles_data)} véhicules chargés depuis la flotte")
            self.status_text.setText(f"{len(self.vehicles_data)} véhicules chargés")
            self.status_icon.setText("✅")
            
            # Activer les boutons appropriés
            self.calc_btn.setEnabled(False)  # Pas besoin de recalculer, les garanties existent déjà
            self.calc_btn.setText("Calcul déjà effectué")
            self.import_btn.setEnabled(True)
            
        except Exception as e:
            self.status_text.setText(f"Erreur: {str(e)}")
            self.status_icon.setText("❌")
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les véhicules: {str(e)}")

        self.refresh_btn.setEnabled(True)

    def display_fleet_vehicles(self):
        """Affiche les véhicules de la flotte dans le tableau"""
        self.vehicles_table.setRowCount(len(self.vehicles_data))
        
        # Mapping des garanties vers les colonnes
        garanties_mapping = [
            ('rc', 8), ('dr', 9), ('vol', 10), ('vb', 11),
            ('incendie', 12), ('bris_glace', 13), ('ar', 14), ('dta', 15), ('ipt', 16)
        ]
        
        for row, vehicle in enumerate(self.vehicles_data):
            # Case à cocher
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Checked)
            self.vehicles_table.setItem(row, 0, check_item)
            
            # Informations de base
            self.vehicles_table.setItem(row, 1, QTableWidgetItem(vehicle.get('immatriculation', '')))
            self.vehicles_table.setItem(row, 2, QTableWidgetItem(vehicle.get('marque', '')))
            self.vehicles_table.setItem(row, 3, QTableWidgetItem(vehicle.get('modele', '')))
            self.vehicles_table.setItem(row, 4, QTableWidgetItem(vehicle.get('categorie', 'VP')))
            
            # Dates
            date_debut = vehicle.get('date_debut')
            date_fin = vehicle.get('date_fin')
            
            if date_debut:
                if isinstance(date_debut, datetime):
                    date_debut_str = date_debut.strftime("%d/%m/%Y")
                else:
                    date_debut_str = str(date_debut)
            else:
                date_debut_str = "-"
            
            if date_fin:
                if isinstance(date_fin, datetime):
                    date_fin_str = date_fin.strftime("%d/%m/%Y")
                else:
                    date_fin_str = str(date_fin)
            else:
                date_fin_str = "-"
            
            self.vehicles_table.setItem(row, 5, QTableWidgetItem(date_debut_str))
            self.vehicles_table.setItem(row, 6, QTableWidgetItem(date_fin_str))
            
            # Jours
            nbr_jour = vehicle.get('nbr_jour', 0)
            jours_item = QTableWidgetItem(str(nbr_jour) if nbr_jour > 0 else "-")
            jours_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.vehicles_table.setItem(row, 7, jours_item)
            
            # Garanties
            garanties = vehicle.get('garanties', {})
            for key, col in garanties_mapping:
                amount = garanties.get(key, 0)
                item = QTableWidgetItem(f"{amount:,.0f}".replace(",", " "))
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.vehicles_table.setItem(row, col, item)
            
            # Total
            total_amount = garanties.get('total', 0)
            total_item = QTableWidgetItem(f"{total_amount:,.0f}".replace(",", " "))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.vehicles_table.setItem(row, 17, total_item)
            
            # Widget des actions (deux boutons)
            vehicle_id = vehicle.get('id', row)  # Utilise l'ID du véhicule ou l'index comme fallback
            actions_widget = VehicleActionsWidget(
                vehicle_id,
                self.edit_vehicle_garanties,
                self.edit_vehicle_dates
            )
            self.vehicles_table.setCellWidget(row, 18, actions_widget)
            if 'accessoires' not in vehicle:
                vehicle['accessoires'] = 0
            if 'asac' not in vehicle:
                vehicle['asac'] = 0
            if 'carte_rose' not in vehicle:
                vehicle['carte_rose'] = 0
            if 'vignette' not in vehicle:
                vehicle['vignette'] = 0
        
        self.adjust_row_heights()
        self.vehicles_table.resizeColumnsToContents()
        self.update_summary()
        self.update_garanties_summary()

    def recalculate_vehicle_garanties(self, row, new_days):
        """Recalcule les garanties au prorata des nouveaux jours"""
        vehicle = self.vehicles_data[row]
        
        # Récupérer les montants bruts annuels
        garanties_annuelles = vehicle.get('garanties_annuelles', {})
        if not garanties_annuelles:
            # Sauvegarder les montants annuels si pas encore fait
            garanties_annuelles = vehicle.get('garanties', {}).copy()
            vehicle['garanties_annuelles'] = garanties_annuelles
        
        # Recalculer au prorata
        prorata = new_days / 365.0
        new_garanties = {}
        for key, amount in garanties_annuelles.items():
            new_garanties[key] = amount * prorata
        
        new_garanties['total'] = sum(v for k, v in new_garanties.items() if k != 'total')
        vehicle['garanties'] = new_garanties
        
        # Rafraîchir l'affichage du tableau
        garanties_mapping = [
            ('rc', 9), ('dr', 10), ('vol', 11), ('vb', 12),
            ('incendie', 13), ('bris_glace', 14), ('ar', 15), ('dta', 16), ('ipt', 17)
        ]
        
        for key, col in garanties_mapping:
            amount = new_garanties.get(key, 0)
            item = QTableWidgetItem(f"{amount:,.0f}".replace(",", " "))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.vehicles_table.setItem(row, col, item)
        
        # Total
        total_item = QTableWidgetItem(f"{new_garanties.get('total', 0):,.0f}".replace(",", " "))
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vehicles_table.setItem(row, 17, total_item)

    def load_existing_fleets(self):
        """Charge les flottes existantes avec leurs informations"""
        try:
            contact_id = None
            if hasattr(self.parent(), 'contact'):
                contact_id = self.parent().contact.id
            elif hasattr(self.controller, 'current_user_id'):
                # Récupérer le contact associé à l'utilisateur courant
                current_user = self.controller.users.get_by_id(self.controller.current_user_id)
                if current_user and hasattr(current_user, 'contact_id'):
                    contact_id = current_user.contact_id
            
            if contact_id:
                fleets = self.controller.fleets.get_fleets_by_owner(contact_id)
                self.existing_fleet_combo.clear()
                self.existing_fleet_combo.addItem("Sélectionner une flotte", None)
                
                for fleet in fleets:
                    # Récupérer le nom de la flotte
                    if hasattr(fleet, 'nom_flotte'):
                        name = fleet.nom_flotte
                    elif hasattr(fleet, 'nom'):
                        name = fleet.nom
                    else:
                        name = 'Sans nom'
                    
                    # Ajouter le nombre de véhicules si disponible
                    if hasattr(fleet, 'vehicles') and fleet.vehicles:
                        vehicle_count = len(fleet.vehicles)
                        display_name = f"{name} ({vehicle_count} véhicules)"
                    else:
                        display_name = name
                    
                    self.existing_fleet_combo.addItem(display_name, fleet.id)
            else:
                self.existing_fleet_combo.clear()
                self.existing_fleet_combo.addItem("Aucune flotte disponible", None)
                
        except Exception as e:
            print(f"Erreur chargement flottes: {e}")
            self.existing_fleet_combo.clear()
            self.existing_fleet_combo.addItem("Erreur de chargement", None)

    def refresh_fleet_guarantees(self):
        """Rafraîchit les garanties des véhicules de la flotte"""
        if not self.vehicles_data:
            return
        
        # Récupérer les paramètres actuels
        compagny_id = self.compagny_combo.currentData()
        if not compagny_id:
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
        self.calc_btn.setText("Recalcul en cours...")
        self.progress_widget.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_icon.setText("🔄")
        self.status_text.setText("Recalcul des garanties en cours...")
        
        # Démarrer le thread de calcul
        self.calculation_thread = CalculationThread(self.controller, self.vehicles_data, params)
        self.calculation_thread.progress.connect(self.on_calculation_progress)
        self.calculation_thread.finished_signal.connect(self.on_fleet_recalculation_finished)
        self.calculation_thread.start()

    def on_fleet_recalculation_finished(self, results):
        """Termine le recalcul des garanties de la flotte"""
        self.vehicles_data = results
        self.progress_widget.setVisible(False)
        self.calc_btn.setEnabled(False)
        self.calc_btn.setText("Recalcul terminé")
        self.import_btn.setEnabled(True)
        
        self.status_icon.setText("✅")
        self.status_text.setText("Garanties recalculées avec succès")
        
        # Rafraîchir l'affichage
        self.display_fleet_vehicles()
        
        QMessageBox.information(self, "Succès", "Les garanties ont été recalculées avec succès!")

    def adjust_row_heights(self):
        """Ajuste la hauteur de toutes les lignes du tableau"""
        row_count = self.vehicles_table.rowCount()
        for row in range(row_count):
            self.vehicles_table.setRowHeight(row, 45)

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