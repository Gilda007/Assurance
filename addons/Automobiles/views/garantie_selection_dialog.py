from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QFrame, 
                             QGraphicsDropShadowEffect, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QScrollArea, QListWidget, QListWidgetItem, QWidget, QMessageBox, QDateEdit,
                             QSplitter, QGroupBox, QCheckBox)
from PySide6.QtCore import QDate, Qt, QPoint, QTimer
from PySide6.QtGui import QColor, QIcon, QPixmap, QFont
import os


class GarantieSelectionDialog(QDialog):
    """Dialogue personnalisé pour sélectionner les garanties d'un véhicule dans la flotte"""
    
    def __init__(self, vehicle_data, parent=None):
        super().__init__(parent)
        self.vehicle_data = vehicle_data
        self.selected_garanties = {}
        self.garantie_widgets = {}
        self.total_amount = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(f"Sélection des garanties - {self.vehicle_data.get('immatriculation', 'Véhicule')}")
        self.setMinimumSize(500, 600)
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 16px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
            QCheckBox {
                spacing: 8px;
                font-size: 13px;
                padding: 5px;
            }
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        header = QLabel(f"🚗 {self.vehicle_data.get('immatriculation', 'Véhicule')} - {self.vehicle_data.get('marque', '')} {self.vehicle_data.get('modele', '')}")
        header.setStyleSheet("font-size: 16px; font-weight: 800; color: #2c3e50; padding: 10px; background: #f0f9ff; border-radius: 10px;")
        layout.addWidget(header)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("border: none;")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(10)
        
        # Groupe Garanties de base
        base_group = QGroupBox("🛡️ Garanties de base")
        base_layout = QGridLayout(base_group)
        base_layout.setSpacing(10)
        
        garanties = [
            ("rc", "Responsabilité Civile", "amt_rc", "red_rc", "amt_red_rc", "amt_val_red_rc"),
            ("dr", "Défense et Recours", "amt_dr", "red_dr", "amt_red_dr", "amt_val_red_dr"),
            ("vol", "Vol du véhicule", "amt_vol", "red_vol", "amt_red_vol", "amt_val_red_vol"),
            ("vb", "Vol à main armée", "amt_vb", "red_vb", "amt_red_vb", "amt_val_red_vb"),
        ]
        
        for i, (key, label, amt_key) in enumerate(garanties):
            checkbox = QCheckBox(label)
            checkbox.setObjectName(key)
            checkbox.stateChanged.connect(lambda state, k=key: self.on_garantie_toggle(k, state))
            
            amount_input = QLineEdit()
            amount_input.setPlaceholderText("Montant (FCFA)")
            amount_input.setEnabled(False)
            amount_input.setObjectName(f"amount_{key}")
            amount_input.textChanged.connect(self.calculate_total)
            
            base_layout.addWidget(checkbox, i, 0)
            base_layout.addWidget(amount_input, i, 1)
            
            self.garantie_widgets[key] = {
                'checkbox': checkbox,
                'amount': amount_input,
                'amt_key': amt_key,
                'default_value': float(self.vehicle_data.get(amt_key, 0) or 0)
            }
            
            if self.garantie_widgets[key]['default_value'] > 0:
                amount_input.setText(f"{self.garantie_widgets[key]['default_value']:,.0f}".replace(",", " "))
                checkbox.setChecked(True)
                amount_input.setEnabled(True)
        
        container_layout.addWidget(base_group)
        
        # Groupe Garanties supplémentaires
        extra_group = QGroupBox("🔥 Garanties supplémentaires")
        extra_layout = QGridLayout(extra_group)
        extra_layout.setSpacing(10)
        
        extra_garanties = [
            ("in", "Incendie", "amt_in", "red_in", "amt_red_in", "amt_val_red_in"),
            ("bris", "Bris de glace", "amt_bris", "red_bris", "amt_red_bris", "amt_val_red_bris"),
            ("ar", "Assistance réparation", "amt_ar", "red_ar", "amt_red_ar", "amt_val_red_ar"),
            ("dta", "Dommages tous accidents", "amt_dta", "red_dta", "amt_red_dta", "amt_val_red_dta"),
            ("ipt", "Individuelle chauffeur", "amt_ipt", "red_ipt", "amt_red_ipt", "amt_val_red_ipt"),
        ]
        
        for i, (key, label, amt_key, red_key, amt_red_key, amt_val_red_key) in enumerate(extra_garanties):
            checkbox = QCheckBox(label)
            checkbox.setObjectName(key)
            checkbox.stateChanged.connect(lambda state, k=key: self.on_garantie_toggle(k, state))
            
            amount_input = QLineEdit()
            amount_input.setPlaceholderText("Montant (FCFA)")
            amount_input.setEnabled(False)
            amount_input.setObjectName(f"amount_{key}")
            amount_input.textChanged.connect(self.calculate_total)
            
            extra_layout.addWidget(checkbox, i, 0)
            extra_layout.addWidget(amount_input, i, 1)
            
            self.garantie_widgets[key] = {
                'checkbox': checkbox,
                'amount': amount_input,
                'amt_key': amt_key,
                'red_key': red_key,
                'amt_red_key': amt_red_key,
                'amt_val_red_key': amt_val_red_key,
                'default_value': float(self.vehicle_data.get(amt_key, 0) or 0)
            }
            
            if self.garantie_widgets[key]['default_value'] > 0:
                amount_input.setText(f"{self.garantie_widgets[key]['default_value']:,.0f}".replace(",", " "))
                checkbox.setChecked(True)
                amount_input.setEnabled(True)
        
        container_layout.addWidget(extra_group)

        for key, widget in self.garantie_widgets.items():
            print(f"Garantie {key}: default_value = {widget['default_value']}")
            if widget['default_value'] > 0:
                widget['amount'].setText(f"{widget['default_value']:,.0f}".replace(",", " "))
                widget['checkbox'].setChecked(True)
                widget['amount'].setEnabled(True)
            else:
                print(f"  -> Pas de valeur par défaut pour {key}")

        # Total
        total_frame = QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background: #f0fdf4;
                border-radius: 12px;
                margin-top: 10px;
            }
        """)
        total_layout = QHBoxLayout(total_frame)
        total_layout.setContentsMargins(15, 10, 15, 10)
        
        total_label = QLabel("💰 TOTAL DES GARANTIES:")
        total_label.setStyleSheet("font-weight: bold; color: #166534;")
        
        self.total_amount = QLabel("0 FCFA")
        self.total_amount.setStyleSheet("font-size: 18px; font-weight: 800; color: #166534;")
        
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.total_amount)
        
        container_layout.addWidget(total_frame)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_ok = QPushButton("✓ Valider")
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        btn_ok.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("✗ Annuler")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        
        self.calculate_total()
    
    def on_garantie_toggle(self, key, state):
        """Gère l'activation/désactivation d'une garantie"""
        widget = self.garantie_widgets.get(key)
        if widget:
            is_checked = state == Qt.Checked
            widget['amount'].setEnabled(is_checked)
            if not is_checked:
                widget['amount'].clear()
            self.calculate_total()
    
    def calculate_total(self):
        """Calcule le total des garanties sélectionnées"""
        total = 0
        for key, widget in self.garantie_widgets.items():
            if widget['checkbox'].isChecked():
                text = widget['amount'].text()
                clean_text = text.replace(" ", "").replace(",", "")
                try:
                    amount = float(clean_text) if clean_text else 0
                    total += amount
                except ValueError:
                    pass
        if self.total_amount:
            self.total_amount.setText(f"{total:,.0f}".replace(",", " ") + " FCFA")
    
    def get_selected_garanties(self):
        """Retourne les garanties sélectionnées avec leurs montants"""
        result = {}
        for key, widget in self.garantie_widgets.items():
            if widget['checkbox'].isChecked():
                text = widget['amount'].text()
                clean_text = text.replace(" ", "").replace(",", "")
                try:
                    amount = float(clean_text) if clean_text else 0
                    result[key] = amount
                except ValueError:
                    result[key] = 0
        return result
