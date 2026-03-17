from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton, QListWidgetItem, QStackedWidget, QListWidget, QFrame, QMessageBox, QDialog)
from PySide6.QtCore import Qt

class AboutUsView(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("AboutUsPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        # --- LOGO OU TITRE ---
        self.logo_label = QLabel("AMS AUTO")
        self.logo_label.setStyleSheet("""
            font-size: 48px; 
            font-weight: 900; 
            color: #1e3a8a; 
            letter-spacing: 2px;
        """)
        
        self.version_badge = QLabel("Version 1.1.0 Professional")
        self.version_badge.setStyleSheet("""
            background-color: #dbeafe; 
            color: #1e40af; 
            padding: 5px 15px; 
            border-radius: 12px;
            font-weight: bold;
            font-size: 13px;
        """)

        # --- DESCRIPTION ---
        self.description = QLabel(
            "Système intelligent de gestion d'assurance automobile.\n"
            "Conçu pour optimiser le workflow des agents et la gestion des polices."
        )
        self.description.setAlignment(Qt.AlignCenter)
        self.description.setWordWrap(True)
        self.description.setStyleSheet("color: #64748b; font-size: 16px; line-height: 140%;")

        # --- GRILLE D'INFORMATIONS ---
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: white; 
                border-radius: 20px; 
                border: 1px solid #e2e8f0;
                padding: 20px;
            }
            QLabel { border: none; color: #334155; }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        # Détails techniques
        tech_info = [
            ("👤 Développeur", "Fearless Software Solutions"),
            ("📅 Dernière mise à jour", "Mars 2026"),
            ("🛡️ Licence", "Propriétaire - AMS Project Group"),
            ("⚙️ Technologies", "Python 3.12, PySide6, SQLAlchemy")
        ]

        for label, value in tech_info:
            row = QHBoxLayout()
            lbl = QLabel(label); lbl.setStyleSheet("font-weight: bold;")
            val = QLabel(value); val.setStyleSheet("color: #3b82f6;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            info_layout.addLayout(row)

        # --- BOUTONS DE LIENS ---
        btn_layout = QHBoxLayout()
        self.btn_support = QPushButton("🌐 Support Technique")
        self.btn_update = QPushButton("🔄 Vérifier les mises à jour")
        
        for btn in [self.btn_support, self.btn_update]:
            btn.setFixedSize(200, 40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f1f5f9; color: #475569; 
                    border-radius: 8px; font-weight: bold;
                }
                QPushButton:hover { background-color: #e2e8f0; }
            """)

        btn_layout.addWidget(self.btn_support)
        btn_layout.addWidget(self.btn_update)

        # --- FOOTER ---
        footer = QLabel("© 2026 AMS Project Group. Tous droits réservés.")
        footer.setStyleSheet("color: #94a3b8; font-size: 11px; margin-top: 30px;")

        # Ajout au layout principal
        layout.addStretch()
        layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.version_badge, alignment=Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(self.description, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(info_frame)
        layout.addSpacing(20)
        layout.addLayout(btn_layout)
        layout.addStretch()
        layout.addWidget(footer, alignment=Qt.AlignCenter)