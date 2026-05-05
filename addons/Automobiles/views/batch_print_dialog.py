# batch_print_dialog.py
"""
Dialogue de sélection pour l'impression groupée de documents
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QCheckBox, QGroupBox, QScrollArea, QWidget,
    QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor


class BatchPrintDialog(QDialog):
    """Dialogue de sélection des documents pour impression groupée"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📄 Impression groupée - Sélection des documents")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        header = QLabel("🔖 Sélectionnez les documents à imprimer")
        header.setStyleSheet("font-size: 16px; font-weight: 800; color: #1e293b;")
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Cochez les documents que vous souhaitez générer pour chaque véhicule sélectionné.")
        desc.setStyleSheet("color: #64748b; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Groupe des documents
        group = QGroupBox("Documents disponibles")
        group.setStyleSheet("""
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
        """)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)
        group_layout.setContentsMargins(20, 20, 20, 20)
        
        # Documents avec icônes
        self.documents = {
            'vignette': QCheckBox("🎫 Vignette"),
            'carte_rose': QCheckBox("📄 Carte Rose"),
            'attestation': QCheckBox("🛡️ Attestation"),
            'devis': QCheckBox("📊 Devis"),
            'quittance': QCheckBox("🧾 Quittance")
        }
        
        for doc in self.documents.values():
            doc.setStyleSheet("""
                QCheckBox {
                    spacing: 12px;
                    font-size: 14px;
                    padding: 8px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 6px;
                    border: 2px solid #cbd5e1;
                }
                QCheckBox::indicator:checked {
                    background-color: #3b82f6;
                    border-color: #3b82f6;
                }
            """)
            group_layout.addWidget(doc)
        
        layout.addWidget(group)
        
        # Information
        info = QLabel("ℹ️ Les documents seront générés un par un et ouverts automatiquement.")
        info.setStyleSheet("color: #64748b; font-size: 11px; margin-top: 5px;")
        layout.addWidget(info)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        self.btn_print = QPushButton("🖨️ Imprimer la sélection")
        self.btn_print.setCursor(Qt.PointingHandCursor)
        self.btn_print.setEnabled(False)
        self.btn_print.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #1d4ed8);
            }
            QPushButton:disabled {
                background: #cbd5e1;
            }
        """)
        self.btn_print.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_print)
        
        layout.addLayout(btn_layout)
        
        # Connecter les signaux
        for doc in self.documents.values():
            doc.stateChanged.connect(self._update_button_state)
        
        self._update_button_state()
    
    def _update_button_state(self):
        """Active/désactive le bouton d'impression selon la sélection"""
        has_selection = any(doc.isChecked() for doc in self.documents.values())
        self.btn_print.setEnabled(has_selection)
    
    def get_selected_documents(self):
        """Retourne la liste des documents sélectionnés"""
        return [key for key, checkbox in self.documents.items() if checkbox.isChecked()]