# addons/Automobiles/views/police_number_selector.py
"""
Widget de sélection de numéro de police pour un contrat
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QComboBox, QMessageBox,
                               QProgressBar, QWidget, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class PoliceNumberSelector(QDialog):
    """Dialogue pour sélectionner/attribuer un numéro de police"""
    
    number_selected = Signal(int, str)  # numero_attribue, numero_police_complet
    
    def __init__(self, controller, compagnie_id, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.compagnie_id = compagnie_id
        self.available_numbers = []
        self.total_numbers = 0
        self.used_count = 0
        
        self.setWindowTitle("Attribution du numéro de police")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()
        self.load_numbers()
    
    def setup_ui(self):
        """Configure l'interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        
        # Conteneur principal
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 24px;
            }
        """)
        
        # Ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # ========== EN-TÊTE ==========
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-top-left-radius: 24px;
                border-top-right-radius: 24px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        
        title = QLabel("Attribution du numéro de police")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: white;
        """)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.3);
            }
        """)
        close_btn.clicked.connect(self.reject)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        container_layout.addWidget(header)
        
        # ========== CORPS ==========
        body = QFrame()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 24, 28, 28)
        body_layout.setSpacing(20)
        
        # ========== SECTION STATISTIQUES ==========
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 16px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(20, 16, 20, 16)
        stats_layout.setSpacing(30)
        
        self.total_label = QLabel("Total: --")
        self.total_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #1e293b;")
        
        self.used_label = QLabel("Utilisés: --")
        self.used_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #f59e0b;")
        
        self.available_label = QLabel("Disponibles: --")
        self.available_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #10b981;")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.used_label)
        stats_layout.addWidget(self.available_label)
        stats_layout.addStretch()
        
        body_layout.addWidget(stats_frame)
        
        # ========== BARRE DE PROGRESSION ==========
        progress_label = QLabel("Taux d'occupation des numéros")
        progress_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #64748b;")
        body_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #e2e8f0;
                border-radius: 6px;
                height: 8px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #f59e0b, stop:1 #ef4444);
                border-radius: 6px;
            }
        """)
        body_layout.addWidget(self.progress_bar)
        
        # ========== ZONE DE SÉLECTION ==========
        selection_label = QLabel("Choisissez un numéro de police")
        selection_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #1e293b; margin-top: 8px;")
        body_layout.addWidget(selection_label)
        
        # Grille des numéros disponibles
        self.numbers_grid = QFrame()
        self.numbers_grid.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 16px;
            }
        """)
        self.numbers_layout = QHBoxLayout(self.numbers_grid)
        self.numbers_layout.setSpacing(12)
        
        # Combo box ou liste déroulante
        self.number_combo = QComboBox()
        self.number_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: 600;
                min-width: 200px;
            }
            QComboBox:hover {
                border-color: #8b5cf6;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.number_combo.currentIndexChanged.connect(self.on_number_selected)
        
        self.numbers_layout.addWidget(self.number_combo)
        self.numbers_layout.addStretch()
        
        body_layout.addWidget(self.numbers_grid)
        
        # ========== PRÉVISUALISATION ==========
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background: #eef2ff;
                border-radius: 16px;
            }
        """)
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(20, 16, 20, 16)
        preview_layout.setSpacing(8)
        
        preview_title = QLabel("Numéro de police généré")
        preview_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #64748b;")
        preview_layout.addWidget(preview_title)
        
        self.preview_number = QLabel("---")
        self.preview_number.setStyleSheet("""
            font-size: 24px;
            font-weight: 800;
            color: #3b82f6;
            font-family: monospace;
        """)
        preview_layout.addWidget(self.preview_number)
        
        body_layout.addWidget(preview_frame)
        
        # ========== BOUTONS ==========
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.confirm_btn = QPushButton("✓ Attribuer ce numéro")
        self.confirm_btn.setCursor(Qt.PointingHandCursor)
        self.confirm_btn.setFixedHeight(44)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #059669;
            }
            QPushButton:disabled {
                background: #cbd5e1;
            }
        """)
        self.confirm_btn.clicked.connect(self.confirm_selection)
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setFixedHeight(44)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        body_layout.addLayout(btn_layout)
        
        # Message d'avertissement
        self.warning_label = QLabel()
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("""
            font-size: 11px;
            color: #ef4444;
            padding: 8px;
            background: #fef2f2;
            border-radius: 8px;
        """)
        self.warning_label.setVisible(False)
        body_layout.addWidget(self.warning_label)
        
        container_layout.addWidget(body)
        main_layout.addWidget(container)
    
    def load_numbers(self):
        """Charge les numéros disponibles"""
        try:
            available, total, used = self.controller.get_available_numbers(self.compagnie_id)
            
            self.available_numbers = available
            self.total_numbers = total
            self.used_count = used
            
            # Mettre à jour les labels
            self.total_label.setText(f"Total: {total}")
            self.used_label.setText(f"Utilisés: {used}")
            self.available_label.setText(f"Disponibles: {len(available)}")
            
            # Mettre à jour la barre de progression
            if total > 0:
                percentage = int((used / total) * 100)
                self.progress_bar.setValue(percentage)
                
                if percentage >= 90:
                    self.progress_bar.setStyleSheet("""
                        QProgressBar::chunk {
                            background: #ef4444;
                            border-radius: 6px;
                        }
                    """)
                elif percentage >= 70:
                    self.progress_bar.setStyleSheet("""
                        QProgressBar::chunk {
                            background: #f59e0b;
                            border-radius: 6px;
                        }
                    """)
            
            # Remplir la combo
            self.number_combo.clear()
            for num in available:
                self.number_combo.addItem(str(num), num)
            
            if len(available) == 0:
                self.number_combo.addItem("AUCUN NUMÉRO DISPONIBLE", None)
                self.number_combo.setEnabled(False)
                self.confirm_btn.setEnabled(False)
                
                self.warning_label.setText(
                    "⚠️ ATTENTION : La plage de numéros de cette compagnie est épuisée !\n\n"
                    "Veuillez contacter l'administrateur pour étendre la plage de numéros "
                    "(num_debut / num_fin) dans les paramètres de la compagnie."
                )
                self.warning_label.setVisible(True)
            else:
                self.confirm_btn.setEnabled(True)
                self.on_number_selected(0)
                
        except Exception as e:
            print(f"Erreur load_numbers: {e}")
    
    def on_number_selected(self, index):
        """Met à jour la prévisualisation du numéro sélectionné"""
        if index >= 0 and self.number_combo.itemData(index):
            num = self.number_combo.itemData(index)
            police_number = self.controller.generate_police_number(self.compagnie_id, num)
            self.preview_number.setText(police_number)
    
    def confirm_selection(self):
        """Confirme la sélection du numéro"""
        current_index = self.number_combo.currentIndex()
        if current_index < 0:
            return
        
        num = self.number_combo.itemData(current_index)
        if not num:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un numéro valide")
            return
        
        police_number = self.controller.generate_police_number(self.compagnie_id, num)
        
        # Confirmation
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Attribuer le numéro de police {police_number} ?\n\n"
            "Ce numéro sera définitif et ne pourra pas être modifié.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.number_selected.emit(num, police_number)
            self.accept()